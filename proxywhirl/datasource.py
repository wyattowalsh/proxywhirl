"""Datasource polling and webhook management for dynamic proxy updates.

Supports:
- Polling sources on schedule
- Webhook-based source updates
- Automatic source refresh
- Update notifications
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class UpdateStrategy(str, Enum):
    """Strategy for updating sources."""

    POLL = "poll"  # Pull updates on schedule
    WEBHOOK = "webhook"  # Receive push updates
    HYBRID = "hybrid"  # Both poll and webhook


class PollingConfig(BaseModel):
    """Configuration for source polling."""

    model_config = ConfigDict(frozen=True)

    interval_seconds: int = Field(default=3600, ge=60)
    timeout_seconds: int = Field(default=30, ge=5)
    max_retries: int = Field(default=3, ge=1)
    backoff_multiplier: float = Field(default=2.0, ge=1.0)
    jitter_percent: int = Field(default=10, ge=0, le=100)


class WebhookConfig(BaseModel):
    """Configuration for webhook updates."""

    model_config = ConfigDict(frozen=True)

    webhook_url: str = Field(description="URL to receive webhook calls")
    secret_key: str = Field(description="Secret for verifying webhooks")
    max_payload_bytes: int = Field(default=10_000_000)
    timeout_seconds: int = Field(default=10)
    retry_count: int = Field(default=3)


class SourceUpdate(BaseModel):
    """Update from a proxy source."""

    model_config = ConfigDict(extra="forbid")

    source_id: str
    proxies_added: int = Field(description="Number of new proxies")
    proxies_removed: int = Field(description="Number of removed proxies")
    total_proxies: int = Field(description="Total proxies after update")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    update_id: UUID = Field(default_factory=uuid4)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PollingSchedule(BaseModel):
    """Schedule for source polling."""

    model_config = ConfigDict(frozen=True)

    source_id: str
    last_poll: datetime | None = None
    next_poll: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=1)
    )
    poll_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    avg_duration_ms: float = 0.0
    last_error: str | None = None


class SourcePollingManager:
    """Manages polling for proxy sources."""

    def __init__(self, config: PollingConfig):
        """Initialize polling manager.

        Args:
            config: Polling configuration
        """
        self.config = config
        self._schedules: dict[str, PollingSchedule] = {}
        self._handlers: dict[str, list[Callable]] = {}
        self._running = False
        self._tasks: dict[str, asyncio.Task] = {}

    def register_source(
        self,
        source_id: str,
        handler: Callable[[SourceUpdate], Any],
        initial_delay: timedelta | None = None,
    ) -> None:
        """Register a source for polling.

        Args:
            source_id: ID of the source
            handler: Async function called on updates
            initial_delay: Initial delay before first poll
        """
        next_poll = datetime.now(timezone.utc) + (
            initial_delay or timedelta(seconds=self.config.interval_seconds)
        )

        self._schedules[source_id] = PollingSchedule(
            source_id=source_id,
            next_poll=next_poll,
        )

        if source_id not in self._handlers:
            self._handlers[source_id] = []
        self._handlers[source_id].append(handler)

    def unregister_source(self, source_id: str) -> None:
        """Unregister a source from polling."""
        if source_id in self._schedules:
            del self._schedules[source_id]
        if source_id in self._handlers:
            del self._handlers[source_id]

    async def start(self) -> None:
        """Start the polling manager."""
        self._running = True
        for source_id in self._schedules:
            self._tasks[source_id] = asyncio.create_task(self._poll_source(source_id))

    async def stop(self) -> None:
        """Stop the polling manager."""
        self._running = False
        for task in self._tasks.values():
            task.cancel()
        self._tasks.clear()

    async def _poll_source(self, source_id: str) -> None:
        """Poll a single source."""
        while self._running:
            schedule = self._schedules.get(source_id)
            if not schedule:
                break

            now = datetime.now(timezone.utc)
            if now < schedule.next_poll:
                await asyncio.sleep(1)
                continue

            # Poll the source
            import time

            start_time = time.time()
            schedule.poll_count += 1

            try:
                # Call handlers (they would fetch from the source)
                for handler in self._handlers.get(source_id, []):
                    result = handler()
                    if asyncio.iscoroutine(result):
                        await result

                schedule.success_count += 1
                schedule.last_error = None

            except Exception as e:
                schedule.failure_count += 1
                schedule.last_error = str(e)

            finally:
                # Update schedule
                duration = (time.time() - start_time) * 1000
                schedule.avg_duration_ms = schedule.avg_duration_ms * 0.9 + duration * 0.1
                schedule.last_poll = now

                # Calculate next poll with jitter
                import random

                jitter = random.randint(-self.config.jitter_percent, 0) / 100.0
                next_interval = self.config.interval_seconds * (1 + jitter)
                schedule.next_poll = now + timedelta(seconds=next_interval)

    def get_schedule(self, source_id: str) -> PollingSchedule | None:
        """Get polling schedule for a source."""
        return self._schedules.get(source_id)

    def get_stats(self) -> dict[str, Any]:
        """Get polling statistics."""
        return {
            "total_sources": len(self._schedules),
            "schedules": {
                source_id: {
                    "last_poll": schedule.last_poll,
                    "next_poll": schedule.next_poll,
                    "poll_count": schedule.poll_count,
                    "success_count": schedule.success_count,
                    "failure_count": schedule.failure_count,
                    "avg_duration_ms": schedule.avg_duration_ms,
                    "last_error": schedule.last_error,
                }
                for source_id, schedule in self._schedules.items()
            },
        }


class WebhookUpdateHandler(ABC):
    """Handler for webhook-based source updates."""

    @abstractmethod
    async def handle_webhook(
        self,
        source_id: str,
        payload: dict[str, Any],
        timestamp: datetime,
    ) -> SourceUpdate:
        """Handle a webhook update.

        Args:
            source_id: ID of the source
            payload: Webhook payload
            timestamp: When webhook was received

        Returns:
            SourceUpdate with change details
        """


class SourceUpdateNotifier:
    """Notifies subscribers of source updates."""

    def __init__(self):
        """Initialize notifier."""
        self._subscribers: list[Callable[[SourceUpdate], Any]] = []

    def subscribe(self, handler: Callable[[SourceUpdate], Any]) -> Callable[[], None]:
        """Subscribe to source updates.

        Args:
            handler: Function called on updates

        Returns:
            Unsubscribe function
        """
        self._subscribers.append(handler)

        def unsubscribe() -> None:
            if handler in self._subscribers:
                self._subscribers.remove(handler)

        return unsubscribe

    async def notify(self, update: SourceUpdate) -> None:
        """Notify all subscribers of an update.

        Args:
            update: The source update
        """
        tasks = []
        for handler in self._subscribers:
            result = handler(update)
            if asyncio.iscoroutine(result):
                tasks.append(result)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
