"""Dead-letter queue for handling failed proxies.

Manages proxies that fail repeatedly and need special handling or investigation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from loguru import logger


class FailureReason(str, Enum):
    """Reasons for dead-lettering proxies."""

    MAX_RETRIES_EXCEEDED = "max_retries_exceeded"
    CONNECTION_TIMEOUT = "connection_timeout"
    SSL_CERTIFICATE_ERROR = "ssl_cert_error"
    AUTHENTICATION_FAILED = "auth_failed"
    MALFORMED_RESPONSE = "malformed_response"
    RATE_LIMITED = "rate_limited"
    BLACKLISTED = "blacklisted"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker"
    MANUAL = "manual"


@dataclass
class DeadLetterEntry:
    """Entry in the dead-letter queue."""

    proxy_url: str
    reason: FailureReason
    failure_count: int
    timestamp: datetime = field(default_factory=datetime.now)
    last_error_message: str | None = None
    context: dict[str, Any] = field(default_factory=dict)
    recovery_attempted: bool = False
    recovery_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict."""
        return {
            "proxy_url": self.proxy_url,
            "reason": self.reason.value,
            "failure_count": self.failure_count,
            "timestamp": self.timestamp.isoformat(),
            "last_error_message": self.last_error_message,
            "context": self.context,
            "recovery_attempted": self.recovery_attempted,
            "recovery_count": self.recovery_count,
        }


class DeadLetterQueue:
    """Manages dead-lettered proxies."""

    def __init__(self, max_entries: int = 10000):
        """Initialize DLQ.

        Args:
            max_entries: Maximum entries to keep (FIFO eviction)
        """
        self.max_entries = max_entries
        self._queue: dict[str, DeadLetterEntry] = {}
        self._access_log: list[tuple[str, datetime, str]] = []

    def add(
        self,
        proxy_url: str,
        reason: FailureReason,
        failure_count: int,
        error_message: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Add a proxy to the dead-letter queue.

        Args:
            proxy_url: URL of failed proxy
            reason: Failure reason
            failure_count: Number of failures
            error_message: Last error message
            context: Additional context about the failure
        """
        # Update existing entry or create new one
        if proxy_url in self._queue:
            entry = self._queue[proxy_url]
            entry.failure_count = failure_count
            entry.last_error_message = error_message
            entry.timestamp = datetime.now()
            if context:
                entry.context.update(context)
        else:
            entry = DeadLetterEntry(
                proxy_url=proxy_url,
                reason=reason,
                failure_count=failure_count,
                last_error_message=error_message,
                context=context or {},
            )
            self._queue[proxy_url] = entry

            # Enforce max entries
            if len(self._queue) > self.max_entries:
                # Remove oldest entry (FIFO)
                oldest_url = min(
                    self._queue.keys(),
                    key=lambda k: self._queue[k].timestamp,
                )
                del self._queue[oldest_url]

        # Log access
        self._access_log.append((proxy_url, datetime.now(), "add"))
        if len(self._access_log) > 10000:
            self._access_log = self._access_log[-5000:]

        logger.warning(
            f"Dead-lettered {proxy_url}: {reason.value} "
            f"(failures: {failure_count})"
        )

    def remove(self, proxy_url: str) -> DeadLetterEntry | None:
        """Remove a proxy from the queue (recovery/cleanup).

        Args:
            proxy_url: URL of proxy to remove

        Returns:
            The removed entry or None
        """
        entry = self._queue.pop(proxy_url, None)

        if entry:
            self._access_log.append((proxy_url, datetime.now(), "remove"))
            logger.info(f"Removed {proxy_url} from dead-letter queue")

        return entry

    def recover(self, proxy_url: str) -> bool:
        """Mark a proxy as recovered (attempt to restore to pool).

        Args:
            proxy_url: URL of proxy to recover

        Returns:
            True if recovery was marked
        """
        if proxy_url not in self._queue:
            return False

        entry = self._queue[proxy_url]
        entry.recovery_attempted = True
        entry.recovery_count += 1
        self._access_log.append((proxy_url, datetime.now(), "recover"))

        logger.info(
            f"Recovery attempt {entry.recovery_count} for {proxy_url}"
        )
        return True

    def get(self, proxy_url: str) -> DeadLetterEntry | None:
        """Get a dead-lettered entry.

        Args:
            proxy_url: URL to look up

        Returns:
            Entry or None
        """
        return self._queue.get(proxy_url)

    def list_by_reason(self, reason: FailureReason) -> list[DeadLetterEntry]:
        """List all entries with a specific failure reason.

        Args:
            reason: Failure reason to filter by

        Returns:
            List of matching entries
        """
        return [
            entry
            for entry in self._queue.values()
            if entry.reason == reason
        ]

    def list_recent(self, hours: int = 24) -> list[DeadLetterEntry]:
        """List recently dead-lettered proxies.

        Args:
            hours: Look back this many hours

        Returns:
            Sorted list of recent entries (newest first)
        """
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [
            entry
            for entry in self._queue.values()
            if entry.timestamp >= cutoff
        ]
        return sorted(recent, key=lambda e: e.timestamp, reverse=True)

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about the dead-letter queue.

        Returns:
            Stats dict
        """
        if not self._queue:
            return {
                "total_entries": 0,
                "by_reason": {},
                "recovered_count": 0,
            }

        by_reason = {}
        recovered_count = 0

        for entry in self._queue.values():
            reason = entry.reason.value
            by_reason[reason] = by_reason.get(reason, 0) + 1

            if entry.recovery_attempted:
                recovered_count += 1

        return {
            "total_entries": len(self._queue),
            "by_reason": by_reason,
            "recovered_count": recovered_count,
            "recovery_success_rate": (
                sum(
                    1
                    for e in self._queue.values()
                    if e.recovery_attempted and e.recovery_count > 0
                )
                / recovered_count
                if recovered_count > 0
                else 0
            ),
        }

    def export_all(self) -> list[dict[str, Any]]:
        """Export all dead-lettered entries for analysis.

        Returns:
            List of entry dicts
        """
        return [entry.to_dict() for entry in self._queue.values()]

    def clear(self) -> int:
        """Clear the dead-letter queue.

        Returns:
            Number of entries cleared
        """
        count = len(self._queue)
        self._queue.clear()
        logger.warning(f"Cleared {count} entries from dead-letter queue")
        return count
