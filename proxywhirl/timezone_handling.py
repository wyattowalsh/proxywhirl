"""Timezone handling and normalization utilities.

Ensures proper timezone handling across proxy logs,
metrics, and timestamps.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from loguru import logger


class TimezoneFormat(str, Enum):
    """Timezone representation formats."""

    UTC = "UTC"
    ISO8601 = "ISO8601"
    UNIX_TIMESTAMP = "UNIX_TIMESTAMP"
    LOCAL = "LOCAL"


class TimezoneManager:
    """Manages timezone conversions and normalization."""

    def __init__(self, default_tz: str = "UTC") -> None:
        """Initialize timezone manager.

        Args:
            default_tz: Default timezone
        """
        self.default_tz = default_tz
        logger.debug(f"TimezoneManager initialized (default={default_tz})")

    def now_utc(self) -> datetime:
        """Get current time in UTC.

        Returns:
            Current datetime in UTC
        """
        return datetime.now(timezone.utc)

    def now_utc_iso(self) -> str:
        """Get current time in UTC ISO format.

        Returns:
            Current time as ISO 8601 string
        """
        return self.now_utc().isoformat()

    def now_utc_timestamp(self) -> int:
        """Get current time as Unix timestamp.

        Returns:
            Current time as Unix timestamp
        """
        return int(self.now_utc().timestamp())

    def to_utc(self, dt: datetime) -> datetime:
        """Convert datetime to UTC.

        Args:
            dt: Datetime object

        Returns:
            Datetime in UTC
        """
        if dt.tzinfo is None:
            logger.warning("Naive datetime provided, assuming UTC")
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    def to_iso8601(self, dt: datetime | None = None) -> str:
        """Convert to ISO 8601 format.

        Args:
            dt: Datetime (uses current if None)

        Returns:
            ISO 8601 formatted string
        """
        if dt is None:
            dt = self.now_utc()
        else:
            dt = self.to_utc(dt)
        return dt.isoformat()

    def from_iso8601(self, iso_string: str) -> datetime | None:
        """Parse ISO 8601 string.

        Args:
            iso_string: ISO 8601 formatted string

        Returns:
            Datetime or None
        """
        try:
            return datetime.fromisoformat(iso_string)
        except Exception as e:
            logger.error(f"Failed to parse ISO 8601 string: {e}")
            return None

    def from_timestamp(self, timestamp: int | float) -> datetime:
        """Create datetime from Unix timestamp.

        Args:
            timestamp: Unix timestamp

        Returns:
            Datetime in UTC
        """
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)

    def format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format.

        Args:
            seconds: Duration in seconds

        Returns:
            Formatted duration string
        """
        if seconds < 60:
            return f"{seconds:.1f}s"

        if seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"

        if seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f}h"

        days = seconds / 86400
        return f"{days:.1f}d"

    def export_metrics(self) -> dict[str, Any]:
        """Export timezone metrics.

        Returns:
            Dictionary of metrics
        """
        return {
            "default_timezone": self.default_tz,
            "current_utc": self.now_utc_iso(),
            "current_timestamp": self.now_utc_timestamp(),
        }
