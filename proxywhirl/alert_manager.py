"""Alert management and notification system for monitoring.

Provides:
- Alert rules and conditions
- Alert triggering and escalation
- Notification channels (email, webhook, Slack)
- Alert history and metrics
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from loguru import logger


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertState(str, Enum):
    """Alert states."""

    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"
    SILENCED = "silenced"


class NotificationChannel(str, Enum):
    """Notification channels."""

    EMAIL = "email"
    WEBHOOK = "webhook"
    SLACK = "slack"
    PAGERDUTY = "pagerduty"
    OPSGENIE = "opsgenie"


@dataclass
class AlertRule:
    """Alert rule definition."""

    rule_id: str
    name: str
    description: str
    severity: AlertSeverity
    condition: Callable[[dict[str, Any]], bool]
    threshold: float = 0.0
    duration_seconds: int = 60
    enabled: bool = True
    channels: list[NotificationChannel] = field(default_factory=list)


@dataclass
class Alert:
    """Single alert instance."""

    alert_id: str
    rule_id: str
    name: str
    severity: AlertSeverity
    message: str
    timestamp: float = field(default_factory=time.time)
    state: AlertState = AlertState.ACTIVE
    triggered_by: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    acknowledged_at: float | None = None
    resolved_at: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "rule_id": self.rule_id,
            "name": self.name,
            "severity": self.severity.value,
            "message": self.message,
            "timestamp": self.timestamp,
            "state": self.state.value,
            "triggered_by": self.triggered_by,
            "context": self.context,
            "acknowledged_at": self.acknowledged_at,
            "resolved_at": self.resolved_at,
            "duration_seconds": int(time.time() - self.timestamp),
        }


class AlertManager:
    """Manages alert rules and notifications."""

    def __init__(self):
        """Initialize alert manager."""
        self.rules: dict[str, AlertRule] = {}
        self.alerts: dict[str, Alert] = {}
        self.history: list[Alert] = []
        self.notification_handlers: dict[NotificationChannel, Callable] = {}
        self.rule_triggers: dict[str, float] = {}  # Track when rule last triggered
        self.silence_rules: dict[str, float] = {}  # Silence end times
        self.lock = asyncio.Lock()

        logger.info("Initialized AlertManager")

    def register_rule(self, rule: AlertRule) -> None:
        """Register alert rule.

        Args:
            rule: Alert rule
        """
        self.rules[rule.rule_id] = rule
        logger.info(f"Registered alert rule: {rule.rule_id} ({rule.name})")

    def register_notification_handler(
        self,
        channel: NotificationChannel,
        handler: Callable[[Alert], Any],
    ) -> None:
        """Register notification handler.

        Args:
            channel: Notification channel
            handler: Handler function
        """
        self.notification_handlers[channel] = handler
        logger.info(f"Registered notification handler for {channel.value}")

    async def evaluate_rule(
        self,
        rule: AlertRule,
        metrics: dict[str, Any],
    ) -> Alert | None:
        """Evaluate alert rule.

        Args:
            rule: Alert rule to evaluate
            metrics: Current metrics

        Returns:
            Alert if condition triggered, None otherwise
        """
        if not rule.enabled:
            return None

        # Check if rule is silenced
        if rule.rule_id in self.silence_rules:
            if time.time() < self.silence_rules[rule.rule_id]:
                return None

        try:
            if rule.condition(metrics):
                # Check cooldown
                last_trigger = self.rule_triggers.get(rule.rule_id, 0)
                if time.time() - last_trigger < rule.duration_seconds:
                    return None

                # Create alert
                alert = Alert(
                    alert_id=f"{rule.rule_id}-{int(time.time())}",
                    rule_id=rule.rule_id,
                    name=rule.name,
                    severity=rule.severity,
                    message=f"Alert triggered: {rule.description}",
                    triggered_by="rule_evaluation",
                    context=metrics,
                )

                self.rule_triggers[rule.rule_id] = time.time()
                return alert

        except Exception as e:
            logger.error(f"Error evaluating rule {rule.rule_id}: {e}")

        return None

    async def trigger_alert(
        self,
        alert: Alert,
    ) -> None:
        """Trigger alert and notify.

        Args:
            alert: Alert to trigger
        """
        async with self.lock:
            # Store alert
            self.alerts[alert.alert_id] = alert
            self.history.append(alert)

            # Limit history
            if len(self.history) > 10000:
                self.history.pop(0)

            logger.warning(f"Alert triggered: {alert.name} (severity={alert.severity.value})")

            # Get rule and notify
            rule = self.rules.get(alert.rule_id)
            if rule:
                for channel in rule.channels:
                    await self._notify(channel, alert)

    async def _notify(
        self,
        channel: NotificationChannel,
        alert: Alert,
    ) -> None:
        """Send notification.

        Args:
            channel: Notification channel
            alert: Alert to send
        """
        handler = self.notification_handlers.get(channel)
        if not handler:
            logger.warning(f"No handler for channel {channel.value}")
            return

        try:
            result = handler(alert)
            if isinstance(result, asyncio.coroutine):
                await result
            logger.info(f"Sent notification via {channel.value} for {alert.alert_id}")
        except Exception as e:
            logger.error(f"Failed to notify via {channel.value}: {e}")

    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge alert.

        Args:
            alert_id: Alert ID to acknowledge

        Returns:
            True if acknowledged
        """
        if alert_id in self.alerts:
            self.alerts[alert_id].state = AlertState.ACKNOWLEDGED
            self.alerts[alert_id].acknowledged_at = time.time()
            logger.info(f"Alert {alert_id} acknowledged")
            return True
        return False

    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve alert.

        Args:
            alert_id: Alert ID to resolve

        Returns:
            True if resolved
        """
        if alert_id in self.alerts:
            self.alerts[alert_id].state = AlertState.RESOLVED
            self.alerts[alert_id].resolved_at = time.time()
            logger.info(f"Alert {alert_id} resolved")
            return True
        return False

    async def silence_rule(
        self,
        rule_id: str,
        duration_seconds: int = 3600,
    ) -> None:
        """Silence alert rule.

        Args:
            rule_id: Rule ID to silence
            duration_seconds: Silence duration
        """
        silence_until = time.time() + duration_seconds
        self.silence_rules[rule_id] = silence_until
        logger.info(f"Silenced rule {rule_id} for {duration_seconds}s")

    def get_active_alerts(self) -> list[Alert]:
        """Get active alerts.

        Returns:
            List of active alerts
        """
        return [a for a in self.alerts.values() if a.state == AlertState.ACTIVE]

    def get_stats(self) -> dict[str, Any]:
        """Get alert statistics."""
        active = self.get_active_alerts()
        by_severity = {}

        for alert in self.alerts.values():
            severity = alert.severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1

        return {
            "total_alerts": len(self.alerts),
            "active_alerts": len(active),
            "rules_registered": len(self.rules),
            "by_severity": by_severity,
            "history_size": len(self.history),
        }


async def create_default_handlers() -> dict[NotificationChannel, Callable]:
    """Create default notification handlers.

    Returns:
        Dictionary of handlers
    """

    async def webhook_handler(alert: Alert) -> None:
        """Send webhook notification."""
        # This would be configured with actual webhook URLs
        logger.debug(f"Webhook notification would be sent for {alert.alert_id}")

    async def email_handler(alert: Alert) -> None:
        """Send email notification."""
        logger.debug(f"Email notification would be sent for {alert.alert_id}")

    return {
        NotificationChannel.WEBHOOK: webhook_handler,
        NotificationChannel.EMAIL: email_handler,
    }
