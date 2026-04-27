"""Notification and alerting system."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Callable, List, Optional


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Alert definition."""

    title: str
    message: str
    severity: AlertSeverity
    timestamp: datetime
    source: Optional[str] = None


class AlertManager:
    """Manages alerts and notifications."""

    def __init__(self):
        self.handlers: List[Callable] = []
        self.alerts: List[Alert] = []

    def register_handler(self, handler: Callable) -> None:
        """Register alert handler."""
        self.handlers.append(handler)

    def send_alert(
        self, title: str, message: str, severity: AlertSeverity, source: Optional[str] = None
    ) -> None:
        """Send an alert."""
        alert = Alert(
            title=title, message=message, severity=severity, timestamp=datetime.now(), source=source
        )

        self.alerts.append(alert)

        # Notify all handlers
        for handler in self.handlers:
            try:
                handler(alert)
            except Exception as e:
                print(f"Alert handler error: {e}")

    def send_email_alert(
        self, recipients: List[str], title: str, message: str, severity: AlertSeverity
    ) -> None:
        """Send email alert."""
        alert = Alert(
            title=title,
            message=message,
            severity=severity,
            timestamp=datetime.now(),
            source="email",
        )
        self.alerts.append(alert)

    def send_slack_alert(
        self, webhook_url: str, title: str, message: str, severity: AlertSeverity
    ) -> None:
        """Send Slack alert."""
        alert = Alert(
            title=title,
            message=message,
            severity=severity,
            timestamp=datetime.now(),
            source="slack",
        )
        self.alerts.append(alert)

    def get_recent_alerts(self, limit: int = 10) -> List[Alert]:
        """Get recent alerts."""
        return self.alerts[-limit:]
