"""
Dead-letter queue for failed proxies in ProxyWhirl.

Provides a queue for proxies that have failed beyond recovery.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FailureReason(str, Enum):
    """Reasons for proxy failure."""

    MAX_RETRIES_EXCEEDED = "max_retries_exceeded"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"
    VALIDATION_FAILED = "validation_failed"
    AUTHENTICATION_FAILED = "authentication_failed"
    CONNECTION_TIMEOUT = "connection_timeout"
    BANDWIDTH_LIMIT = "bandwidth_limit"
    RATE_LIMIT = "rate_limit"
    BLACKLISTED = "blacklisted"
    MANUAL = "manual"
    UNKNOWN = "unknown"


class DeadLetterEntry(BaseModel):
    """Entry in the dead-letter queue."""

    proxy_url: str = Field(description="Proxy URL")
    pool_id: Optional[str] = Field(default=None, description="Pool identifier")
    reason: FailureReason = Field(description="Reason for failure")
    error_message: str = Field(description="Error message")
    failure_count: int = Field(ge=1, description="Number of failures")
    first_failure_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_failure_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, str] = Field(default_factory=dict, description="Additional metadata")

    model_config = ConfigDict(frozen=False)


class DeadLetterQueue:
    """Queue for permanently failed proxies."""

    def __init__(self, max_queue_size: int = 10000):
        """Initialize the dead-letter queue.

        Args:
            max_queue_size: Maximum entries to keep
        """
        self.max_queue_size = max_queue_size
        self._entries: list[DeadLetterEntry] = []
        self._index: dict[str, int] = {}

    def add(
        self,
        proxy_url: str,
        reason: FailureReason,
        error_message: str,
        pool_id: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> DeadLetterEntry:
        """Add a proxy to the dead-letter queue.

        Args:
            proxy_url: Proxy URL
            reason: Reason for failure
            error_message: Error message
            pool_id: Optional pool identifier
            metadata: Optional metadata

        Returns:
            DeadLetterEntry
        """
        existing_index = self._index.get(proxy_url)

        if existing_index is not None:
            entry = self._entries[existing_index]
            entry.failure_count += 1
            entry.last_failure_at = datetime.now(timezone.utc)
            entry.reason = reason
            entry.error_message = error_message
            if metadata:
                entry.metadata.update(metadata)
            return entry

        entry = DeadLetterEntry(
            proxy_url=proxy_url,
            pool_id=pool_id,
            reason=reason,
            error_message=error_message,
            failure_count=1,
            metadata=metadata or {},
        )

        if len(self._entries) >= self.max_queue_size:
            removed = self._entries.pop(0)
            del self._index[removed.proxy_url]
            self._reindex()

        self._entries.append(entry)
        self._index[proxy_url] = len(self._entries) - 1

        return entry

    def get(self, proxy_url: str) -> Optional[DeadLetterEntry]:
        """Get an entry from the queue.

        Args:
            proxy_url: Proxy URL

        Returns:
            DeadLetterEntry if found, None otherwise
        """
        index = self._index.get(proxy_url)
        if index is not None:
            return self._entries[index]
        return None

    def remove(self, proxy_url: str) -> bool:
        """Remove an entry from the queue.

        Args:
            proxy_url: Proxy URL

        Returns:
            True if removed, False if not found
        """
        index = self._index.get(proxy_url)
        if index is not None:
            del self._entries[index]
            del self._index[proxy_url]
            self._reindex()
            return True
        return False

    def list_entries(
        self,
        pool_id: Optional[str] = None,
        reason: Optional[FailureReason] = None,
        limit: Optional[int] = None,
    ) -> list[DeadLetterEntry]:
        """List entries in the queue.

        Args:
            pool_id: Filter by pool
            reason: Filter by reason
            limit: Maximum entries to return

        Returns:
            List of DeadLetterEntry objects
        """
        entries = self._entries

        if pool_id:
            entries = [e for e in entries if e.pool_id == pool_id]

        if reason:
            entries = [e for e in entries if e.reason == reason]

        if limit:
            entries = entries[-limit:]

        return entries

    def clear(self) -> int:
        """Clear all entries from the queue.

        Returns:
            Number of entries cleared
        """
        count = len(self._entries)
        self._entries.clear()
        self._index.clear()
        return count

    def _reindex(self) -> None:
        """Rebuild the index."""
        self._index.clear()
        for i, entry in enumerate(self._entries):
            self._index[entry.proxy_url] = i

    def __len__(self) -> int:
        """Get queue size."""
        return len(self._entries)

    def __iter__(self):
        """Iterate over entries."""
        return iter(self._entries)
