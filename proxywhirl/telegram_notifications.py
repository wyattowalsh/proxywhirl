"""Telegram alerting support for ProxyWhirl.

Sends alerts and notifications to Telegram when
proxy health status changes or errors occur.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from loguru import logger


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class TelegramConfig:
    """Configuration for Telegram bot."""

    bot_token: str
    chat_id: str
    enabled: bool = True

    def validate(self) -> bool:
        """Validate configuration.

        Returns:
            True if valid
        """
        if not self.bot_token:
            logger.error("Telegram bot_token is required")
            return False

        if not self.chat_id:
            logger.error("Telegram chat_id is required")
            return False

        return True


@dataclass
class TelegramAlert:
    """Represents an alert to be sent."""

    title: str
    message: str
    severity: AlertSeverity
    timestamp: datetime
    metadata: dict[str, Any] | None = None

    def format_message(self) -> str:
        """Format alert as message.

        Returns:
            Formatted message
        """
        severity_emoji = {
            AlertSeverity.INFO: "ℹ️",
            AlertSeverity.WARNING: "⚠️",
            AlertSeverity.CRITICAL: "🚨",
        }

        emoji = severity_emoji.get(self.severity, "")
        time_str = self.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")

        msg = f"{emoji} {self.title}\n"
        msg += f"Severity: {self.severity.value.upper()}\n"
        msg += f"Time: {time_str}\n"
        msg += f"Message: {self.message}\n"

        if self.metadata:
            msg += "\nMetadata:\n"
            for key, value in self.metadata.items():
                msg += f"  {key}: {value}\n"

        return msg


class TelegramNotificationManager:
    """Manages Telegram notifications."""

    def __init__(self, config: TelegramConfig) -> None:
        """Initialize Telegram notification manager.

        Args:
            config: Telegram configuration
        """
        if not config.validate():
            msg = "Invalid Telegram configuration"
            raise ValueError(msg)

        self.config = config
        self._alert_queue: list[TelegramAlert] = []
        logger.debug("TelegramNotificationManager initialized")

    def queue_alert(
        self,
        title: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.INFO,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Queue an alert for sending.

        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity
            metadata: Optional metadata

        Returns:
            True if queued
        """
        if not self.config.enabled:
            logger.debug("Telegram notifications are disabled")
            return False

        alert = TelegramAlert(
            title=title,
            message=message,
            severity=severity,
            timestamp=datetime.now(timezone.utc),
            metadata=metadata,
        )
        self._alert_queue.append(alert)
        logger.debug(f"Alert queued: {title}")
        return True

    def get_pending_alerts(self) -> list[TelegramAlert]:
        """Get pending alerts.

        Returns:
            List of pending alerts
        """
        return self._alert_queue.copy()

    def clear_alerts(self) -> None:
        """Clear pending alerts."""
        self._alert_queue.clear()
        logger.debug("Alerts cleared")

    def format_batch_message(self, alerts: list[TelegramAlert] | None = None) -> str:
        """Format multiple alerts into single message.

        Args:
            alerts: List of alerts (uses queue if None)

        Returns:
            Formatted message
        """
        if alerts is None:
            alerts = self._alert_queue

        if not alerts:
            return "No alerts"

        msg = f"📊 ProxyWhirl Alerts ({len(alerts)} total)\n\n"
        for i, alert in enumerate(alerts, 1):
            severity_emoji = {
                AlertSeverity.INFO: "ℹ️",
                AlertSeverity.WARNING: "⚠️",
                AlertSeverity.CRITICAL: "🚨",
            }
            emoji = severity_emoji.get(alert.severity, "")
            msg += f"{i}. {emoji} {alert.title}\n"
            msg += f"   {alert.message}\n\n"

        return msg

    def export_metrics(self) -> dict[str, Any]:
        """Export notification metrics.

        Returns:
            Dictionary of metrics
        """
        critical_count = sum(1 for a in self._alert_queue if a.severity == AlertSeverity.CRITICAL)
        warning_count = sum(1 for a in self._alert_queue if a.severity == AlertSeverity.WARNING)

        return {
            "total_pending_alerts": len(self._alert_queue),
            "critical_alerts": critical_count,
            "warning_alerts": warning_count,
            "enabled": self.config.enabled,
        }
