"""Request queue management with backpressure handling.

Provides:
- FIFO request queueing
- Priority queuing support
- Backpressure and flow control
- Queue statistics
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4

from loguru import logger


class QueuePriority(str, Enum):
    """Request priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class QueuedRequest:
    """A queued request with metadata."""

    request_id: str = field(default_factory=lambda: uuid4().hex)
    url: str = ""
    method: str = "GET"
    priority: QueuePriority = QueuePriority.NORMAL
    payload: Any = None
    created_at: float = field(default_factory=time.time)
    timeout: float = 30.0
    max_retries: int = 3
    retry_count: int = 0

    @property
    def age_seconds(self) -> float:
        """Get request age in seconds."""
        return time.time() - self.created_at

    @property
    def is_expired(self) -> bool:
        """Check if request has timed out."""
        return self.age_seconds > self.timeout


class RequestQueue:
    """Priority-based request queue with backpressure control."""

    def __init__(
        self,
        max_size: int = 10000,
        max_queue_age: float = 3600,
    ):
        """Initialize request queue.

        Args:
            max_size: Maximum queue size before backpressure
            max_queue_age: Maximum age for queued requests in seconds
        """
        self.max_size = max_size
        self.max_queue_age = max_queue_age
        self.queues: dict[QueuePriority, list[QueuedRequest]] = {
            QueuePriority.CRITICAL: [],
            QueuePriority.HIGH: [],
            QueuePriority.NORMAL: [],
            QueuePriority.LOW: [],
        }
        self.lock = asyncio.Lock()
        self.enqueue_time: dict[str, float] = {}
        self.completed: int = 0
        self.failed: int = 0

    async def enqueue(
        self,
        url: str,
        method: str = "GET",
        priority: QueuePriority = QueuePriority.NORMAL,
        payload: Any = None,
        timeout: float = 30.0,
    ) -> str:
        """Enqueue a request.

        Args:
            url: Request URL
            method: HTTP method
            priority: Request priority
            payload: Request payload
            timeout: Request timeout in seconds

        Returns:
            Request ID

        Raises:
            RuntimeError: If queue is full (backpressure)
        """
        async with self.lock:
            # Check size
            total_size = sum(len(q) for q in self.queues.values())
            if total_size >= self.max_size:
                raise RuntimeError(f"Request queue full ({total_size}/{self.max_size})")

            # Create request
            request = QueuedRequest(
                url=url,
                method=method,
                priority=priority,
                payload=payload,
                timeout=timeout,
            )

            # Add to appropriate queue
            self.queues[priority].append(request)
            self.enqueue_time[request.request_id] = time.time()

            logger.debug(
                f"Enqueued request {request.request_id} with priority {priority}",
            )

            return request.request_id

    async def dequeue(self) -> QueuedRequest | None:
        """Dequeue highest priority request.

        Returns next request or None if queue is empty.
        """
        async with self.lock:
            # Try each priority level
            for priority in [
                QueuePriority.CRITICAL,
                QueuePriority.HIGH,
                QueuePriority.NORMAL,
                QueuePriority.LOW,
            ]:
                queue = self.queues[priority]
                while queue:
                    request = queue.pop(0)

                    # Check if expired
                    if request.is_expired:
                        logger.warning(f"Dequeued expired request {request.request_id}")
                        self.failed += 1
                        continue

                    self.enqueue_time.pop(request.request_id, None)
                    logger.debug(f"Dequeued request {request.request_id} from {priority}")
                    return request

            return None

    async def mark_completed(self, request_id: str) -> None:
        """Mark request as completed."""
        async with self.lock:
            self.enqueue_time.pop(request_id, None)
            self.completed += 1
            logger.debug(f"Marked request {request_id} as completed")

    async def mark_failed(self, request_id: str, request: QueuedRequest) -> bool:
        """Mark request as failed and requeue if retries available.

        Returns True if requeued, False if giving up.
        """
        async with self.lock:
            if request.retry_count < request.max_retries:
                request.retry_count += 1
                logger.warning(
                    f"Requeuing failed request {request_id} "
                    f"(attempt {request.retry_count}/{request.max_retries})"
                )
                self.queues[request.priority].append(request)
                return True
            else:
                logger.error(
                    f"Giving up on request {request_id} after {request.max_retries} retries"
                )
                self.enqueue_time.pop(request_id, None)
                self.failed += 1
                return False

    async def get_stats(self) -> dict[str, Any]:
        """Get queue statistics."""
        async with self.lock:
            total_queued = sum(len(q) for q in self.queues.values())
            return {
                "total_queued": total_queued,
                "critical": len(self.queues[QueuePriority.CRITICAL]),
                "high": len(self.queues[QueuePriority.HIGH]),
                "normal": len(self.queues[QueuePriority.NORMAL]),
                "low": len(self.queues[QueuePriority.LOW]),
                "completed": self.completed,
                "failed": self.failed,
                "max_size": self.max_size,
                "queue_fullness_percent": (total_queued / self.max_size) * 100
                if self.max_size > 0
                else 0,
            }

    async def flush(self) -> None:
        """Clear all queued requests."""
        async with self.lock:
            for queue in self.queues.values():
                queue.clear()
            self.enqueue_time.clear()
            logger.info("Flushed request queue")

    async def cleanup_expired(self) -> int:
        """Remove expired requests from queue.

        Returns number of requests removed.
        """
        async with self.lock:
            removed = 0
            for queue in self.queues.values():
                queue[:] = [r for r in queue if not r.is_expired]
                removed += len(queue)

            return len(self.enqueue_time)
