"""Notification and alerting system for ProxyWhirl.

Supports multiple notification channels:
- Telegram bot alerts
- Email notifications
- Webhook callbacks
- Syslog events
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import httpx
from loguru import logger


class AlertLevel(str, Enum):
    """Alert severity levels."""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"


class AlertType(str, Enum):
    """Types of alerts that can be triggered."""

    POOL_EMPTY = "pool_empty"
    POOL_DEPLETED = "pool_depleted"
    PROXY_DEAD = "proxy_dead"
    ALL_PROXIES_FAILING = "all_proxies_failing"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"
    CIRCUIT_BREAKER_CLOSED = "circuit_breaker_closed"
    HIGH_FAILURE_RATE = "high_failure_rate"
    PERFORMANCE_DEGRADED = "performance_degraded"
    CACHE_CORRUPTION = "cache_corruption"
    STORAGE_ERROR = "storage_error"
    SOURCE_FETCH_FAILED = "source_fetch_failed"
    VALIDATION_ERROR = "validation_error"


@dataclass
class Alert:
    """Alert event with metadata."""

    alert_type: AlertType
    level: AlertLevel
    message: str
    timestamp: datetime
    context: dict[str, Any]
    pool_id: str | None = None


class NotificationHandler(ABC):
    """Base class for notification handlers."""

    @abstractmethod
    async def send(self, alert: Alert) -> bool:
        """Send notification for alert.

        Args:
            alert: Alert to send

        Returns:
            True if sent successfully, False otherwise
        """


class TelegramNotificationHandler(NotificationHandler):
    """Send alerts via Telegram bot.

    Requires:
    - PROXYWHIRL_TELEGRAM_BOT_TOKEN environment variable
    - PROXYWHIRL_TELEGRAM_CHAT_ID environment variable
    """

    def __init__(self, bot_token: str, chat_id: str):
        """Initialize Telegram handler.

        Args:
            bot_token: Telegram bot token
            chat_id: Target chat ID
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    async def send(self, alert: Alert) -> bool:
        """Send Telegram message."""
        try:
            emoji = self._emoji_for_level(alert.level)
            message = (
                f"{emoji} *{alert.alert_type.value}*\n\n"
                f"{alert.message}\n\n"
                f"_Level: {alert.level.value}_\n"
                f"_Time: {alert.timestamp.isoformat()}_"
            )

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": self.chat_id,
                        "text": message,
                        "parse_mode": "Markdown",
                    },
                    timeout=10,
                )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            return False

    @staticmethod
    def _emoji_for_level(level: AlertLevel) -> str:
        """Get emoji for alert level."""
        return {
            AlertLevel.CRITICAL: "🚨",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.INFO: "ℹ️",
            AlertLevel.DEBUG: "🔍",
        }.get(level, "📢")


class WebhookNotificationHandler(NotificationHandler):
    """Send alerts via HTTP webhook."""

    def __init__(self, webhook_url: str, secret: str | None = None):
        """Initialize webhook handler.

        Args:
            webhook_url: URL to send webhooks to
            secret: Optional secret for HMAC signature
        """
        self.webhook_url = webhook_url
        self.secret = secret

    async def send(self, alert: Alert) -> bool:
        """Send webhook notification."""
        try:
            payload = {
                "alert_type": alert.alert_type.value,
                "level": alert.level.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "context": alert.context,
                "pool_id": alert.pool_id,
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    timeout=10,
                )
            return response.status_code in (200, 201, 204)
        except Exception as e:
            logger.error(f"Failed to send webhook: {e}")
            return False


class EmailNotificationHandler(NotificationHandler):
    """Send alerts via email.

    Requires SMTP configuration via environment:
    - PROXYWHIRL_SMTP_HOST
    - PROXYWHIRL_SMTP_PORT
    - PROXYWHIRL_SMTP_USER
    - PROXYWHIRL_SMTP_PASSWORD
    """

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        sender: str,
        recipients: list[str],
        username: str | None = None,
        password: str | None = None,
    ):
        """Initialize email handler."""
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.sender = sender
        self.recipients = recipients
        self.username = username
        self.password = password

    async def send(self, alert: Alert) -> bool:
        """Send email notification."""
        try:
            import smtplib
            from email.mime.text import MIMEText

            body = (
                f"Alert: {alert.alert_type.value}\n"
                f"Level: {alert.level.value}\n"
                f"Time: {alert.timestamp.isoformat()}\n\n"
                f"Message:\n{alert.message}\n\n"
                f"Context: {alert.context}"
            )

            message = MIMEText(body)
            message["Subject"] = f"[{alert.level.value.upper()}] {alert.alert_type.value}"
            message["From"] = self.sender
            message["To"] = ", ".join(self.recipients)

            smtp = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            smtp.login(self.username, self.password)
            smtp.send_message(message)
            smtp.quit()
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False


class AlertManager:
    """Manages alert generation and dispatch."""

    def __init__(self):
        """Initialize alert manager."""
        self.handlers: list[NotificationHandler] = []
        self.alert_history: list[Alert] = []
        self.max_history = 1000
        self._dedup_cache: dict[str, datetime] = {}
        self._dedup_window_seconds = 60

    def add_handler(self, handler: NotificationHandler) -> None:
        """Add notification handler."""
        self.handlers.append(handler)
        logger.info(f"Added notification handler: {handler.__class__.__name__}")

    async def trigger_alert(
        self,
        alert_type: AlertType,
        level: AlertLevel,
        message: str,
        context: dict[str, Any],
        pool_id: str | None = None,
        deduplicate: bool = True,
    ) -> None:
        """Trigger an alert."""
        if deduplicate and self._should_deduplicate(alert_type):
            logger.debug(f"Alert deduplicated: {alert_type.value}")
            return

        alert = Alert(
            alert_type=alert_type,
            level=level,
            message=message,
            timestamp=datetime.now(timezone.utc),
            context=context,
            pool_id=pool_id,
        )

        self.alert_history.append(alert)
        if len(self.alert_history) > self.max_history:
            self.alert_history.pop(0)

        await self._dispatch_alert(alert)

    async def _dispatch_alert(self, alert: Alert) -> None:
        """Dispatch alert to all handlers."""
        tasks = [handler.send(alert) for handler in self.handlers]
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            successful = sum(1 for r in results if r is True)
            logger.info(f"Alert dispatched: {successful}/{len(self.handlers)} handlers")

    def _should_deduplicate(self, alert_type: AlertType) -> bool:
        """Check if alert should be deduplicated."""
        key = str(alert_type)
        now = datetime.now(timezone.utc)

        if key in self._dedup_cache:
            last_time = self._dedup_cache[key]
            if (now - last_time).total_seconds() < self._dedup_window_seconds:
                return True

        self._dedup_cache[key] = now
        return False

    def get_alert_history(
        self,
        alert_type: AlertType | None = None,
        level: AlertLevel | None = None,
        limit: int = 100,
    ) -> list[Alert]:
        """Get alert history with optional filtering."""
        history = self.alert_history

        if alert_type:
            history = [a for a in history if a.alert_type == alert_type]

        if level:
            history = [a for a in history if a.level == level]

        return history[-limit:]


# Global alert manager instance
_alert_manager: AlertManager | None = None


def get_alert_manager() -> AlertManager:
    """Get or create global alert manager."""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager


def set_alert_manager(manager: AlertManager) -> None:
    """Set global alert manager."""
    global _alert_manager
    _alert_manager = manager
