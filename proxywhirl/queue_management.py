"""Queue management for request/response handling."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Generic, TypeVar

from loguru import logger

T = TypeVar("T")


class QueuePriority(str, Enum):
    """Queue item priority."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class QueueItem(Generic[T]):
    """Item in queue."""

    data: T
    priority: QueuePriority = QueuePriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    retry_count: int = 0
    max_retries: int = 3
    metadata: dict[str, Any] = field(default_factory=dict)

    def can_retry(self) -> bool:
        """Check if can retry.

        Returns:
            True if can retry
        """
        return self.retry_count < self.max_retries

    def increment_retry(self) -> None:
        """Increment retry count."""
        self.retry_count += 1


class PriorityQueue(Generic[T]):
    """Priority queue implementation."""

    def __init__(self, max_size: int = 1000):
        """Initialize queue.

        Args:
            max_size: Maximum queue size
        """
        self.max_size = max_size
        self._queues: dict[QueuePriority, list[QueueItem[T]]] = {
            priority: [] for priority in QueuePriority
        }
        self._stats = {
            "total_added": 0,
            "total_removed": 0,
            "total_retried": 0,
        }

    def put(self, data: T, priority: QueuePriority = QueuePriority.NORMAL) -> bool:
        """Add item to queue.

        Args:
            data: Item data
            priority: Item priority

        Returns:
            True if added
        """
        if self.size() >= self.max_size:
            logger.warning("Queue full, rejecting item")
            return False

        item = QueueItem(data=data, priority=priority)
        self._queues[priority].append(item)
        self._stats["total_added"] += 1

        return True

    def get(self) -> QueueItem[T] | None:
        """Get next item from queue.

        Returns:
            Item or None
        """
        # Check in priority order: CRITICAL, HIGH, NORMAL, LOW
        for priority in [
            QueuePriority.CRITICAL,
            QueuePriority.HIGH,
            QueuePriority.NORMAL,
            QueuePriority.LOW,
        ]:
            if self._queues[priority]:
                item = self._queues[priority].pop(0)
                self._stats["total_removed"] += 1
                return item

        return None

    def size(self) -> int:
        """Get queue size.

        Returns:
            Queue size
        """
        return sum(len(items) for items in self._queues.values())

    def peek(self) -> QueueItem[T] | None:
        """Peek at next item without removing.

        Returns:
            Item or None
        """
        for priority in [
            QueuePriority.CRITICAL,
            QueuePriority.HIGH,
            QueuePriority.NORMAL,
            QueuePriority.LOW,
        ]:
            if self._queues[priority]:
                return self._queues[priority][0]

        return None

    def clear(self) -> None:
        """Clear queue."""
        for priority in QueuePriority:
            self._queues[priority].clear()

        logger.info("Queue cleared")

    def get_stats(self) -> dict[str, Any]:
        """Get queue statistics.

        Returns:
            Stats dict
        """
        return {
            **self._stats,
            "current_size": self.size(),
            "by_priority": {priority.value: len(items) for priority, items in self._queues.items()},
        }


class RetryQueue(Generic[T]):
    """Queue for managing retries."""

    def __init__(self, max_retries: int = 3):
        """Initialize retry queue.

        Args:
            max_retries: Max retries per item
        """
        self.max_retries = max_retries
        self._failed_items: list[QueueItem[T]] = []
        self._success_count = 0
        self._permanent_failures = 0

    def add_failed_item(self, item: QueueItem[T]) -> None:
        """Add failed item.

        Args:
            item: Failed item
        """
        if item.can_retry():
            item.increment_retry()
            self._failed_items.append(item)
            logger.info(f"Item added to retry queue (attempt {item.retry_count})")
        else:
            self._permanent_failures += 1
            logger.error(f"Item exceeded max retries: {self.max_retries}")

    def get_failed_item(self) -> QueueItem[T] | None:
        """Get next failed item for retry.

        Returns:
            Item or None
        """
        if self._failed_items:
            return self._failed_items.pop(0)

        return None

    def mark_success(self, item: QueueItem[T]) -> None:
        """Mark item as successful.

        Args:
            item: Successful item
        """
        self._success_count += 1
        logger.info(f"Item succeeded after {item.retry_count} retries")

    def get_stats(self) -> dict[str, int]:
        """Get retry stats.

        Returns:
            Stats dict
        """
        return {
            "pending_retries": len(self._failed_items),
            "successful_retries": self._success_count,
            "permanent_failures": self._permanent_failures,
        }

    def clear(self) -> None:
        """Clear retry queue."""
        self._failed_items.clear()
        logger.info("Retry queue cleared")


class RoundRobinQueue(Generic[T]):
    """Round-robin queue implementation."""

    def __init__(self):
        """Initialize queue."""
        self._queues: dict[str, list[T]] = {}
        self._current_key: str | None = None
        self._key_order: list[str] = []

    def add_queue(self, name: str) -> None:
        """Add named queue.

        Args:
            name: Queue name
        """
        if name not in self._queues:
            self._queues[name] = []
            self._key_order.append(name)
            logger.info(f"Added queue: {name}")

    def put(self, queue_name: str, item: T) -> bool:
        """Add item to queue.

        Args:
            queue_name: Queue name
            item: Item to add

        Returns:
            True if added
        """
        if queue_name not in self._queues:
            return False

        self._queues[queue_name].append(item)
        return True

    def get(self) -> tuple[str, T] | None:
        """Get next item in round-robin.

        Returns:
            (queue_name, item) tuple or None
        """
        if not self._key_order:
            return None

        attempts = 0
        while attempts < len(self._key_order):
            if self._current_key is None:
                self._current_key = self._key_order[0]
            else:
                idx = self._key_order.index(self._current_key)
                self._current_key = self._key_order[(idx + 1) % len(self._key_order)]

            queue = self._queues.get(self._current_key, [])
            if queue:
                item = queue.pop(0)
                return self._current_key, item

            attempts += 1

        return None

    def size(self, queue_name: str | None = None) -> int:
        """Get queue size.

        Args:
            queue_name: Optional queue name

        Returns:
            Size
        """
        if queue_name:
            return len(self._queues.get(queue_name, []))

        return sum(len(q) for q in self._queues.values())

    def clear_queue(self, queue_name: str) -> None:
        """Clear specific queue.

        Args:
            queue_name: Queue name
        """
        if queue_name in self._queues:
            self._queues[queue_name].clear()
