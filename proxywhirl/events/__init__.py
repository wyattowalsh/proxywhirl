"""Event-driven architecture with pub/sub for ProxyWhirl.

Provides:
- Event bus for internal event distribution
- Publisher and Subscriber interfaces
- Common event types for proxy pool, health, and webhook events
- Async-first design with backpressure support
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable
from uuid import UUID, uuid4

from loguru import logger
from pydantic import BaseModel, ConfigDict, Field


class EventType(str, Enum):
    """Standard event types in ProxyWhirl."""

    # Proxy pool events
    PROXY_ADDED = "proxy.added"
    PROXY_REMOVED = "proxy.removed"
    PROXY_ENABLED = "proxy.enabled"
    PROXY_DISABLED = "proxy.disabled"
    PROXY_HEALTH_CHANGED = "proxy.health_changed"

    # Pool events
    POOL_CREATED = "pool.created"
    POOL_CLEARED = "pool.cleared"
    POOL_RELOADED = "pool.reloaded"

    # Rotation events
    ROTATION_STRATEGY_CHANGED = "rotation.strategy_changed"
    ROTATION_EXECUTED = "rotation.executed"

    # Source events
    SOURCE_FETCHED = "source.fetched"
    SOURCE_UPDATED = "source.updated"
    SOURCE_FAILED = "source.failed"

    # Health events
    HEALTH_CHECK_EXECUTED = "health.check_executed"
    HEALTH_CHECK_FAILED = "health.check_failed"

    # Webhook events
    WEBHOOK_DELIVERED = "webhook.delivered"
    WEBHOOK_FAILED = "webhook.failed"
    WEBHOOK_SIGNED = "webhook.signed"


class Event(BaseModel):
    """Base event in the event bus."""

    model_config = ConfigDict(extra="forbid")

    event_type: EventType
    event_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = Field(description="Component that emitted event")
    payload: dict[str, Any] = Field(default_factory=dict)
    correlation_id: UUID | None = Field(None, description="For correlating related events")
    metadata: dict[str, Any] = Field(default_factory=dict)


class EventHandler(ABC):
    """Abstract base for event handlers."""

    @abstractmethod
    async def handle(self, event: Event) -> None:
        """Handle an event.

        Args:
            event: The event to handle
        """


class EventSubscriber:
    """Subscribes to specific event types."""

    def __init__(
        self,
        event_types: list[EventType] | EventType,
        handler: EventHandler | Callable[[Event], Any],
        filter_fn: Callable[[Event], bool] | None = None,
    ):
        """Initialize event subscriber.

        Args:
            event_types: Event type(s) to subscribe to
            handler: Handler function or EventHandler instance
            filter_fn: Optional filter function to pre-filter events
        """
        self.event_types = [event_types] if isinstance(event_types, EventType) else event_types
        self.handler = handler
        self.filter_fn = filter_fn or (lambda _: True)

    async def handle(self, event: Event) -> None:
        """Handle event if it matches criteria."""
        if not self.filter_fn(event):
            return

        if isinstance(self.handler, EventHandler):
            await self.handler.handle(event)
        else:
            result = self.handler(event)
            if asyncio.iscoroutine(result):
                await result


class EventBus:
    """Central event bus for pub/sub messaging.

    Provides async-first event distribution with backpressure support
    and error isolation (errors in one handler don't affect others).
    """

    def __init__(self, max_queue_size: int = 10000):
        """Initialize event bus.

        Args:
            max_queue_size: Maximum pending events before backpressure
        """
        self.max_queue_size = max_queue_size
        self._subscribers: dict[EventType, list[EventSubscriber]] = {}
        self._event_queue: asyncio.Queue[Event] = asyncio.Queue(maxsize=max_queue_size)
        self._running = False
        self._worker_task: asyncio.Task[None] | None = None
        self._event_history: list[Event] = []
        self._max_history = 1000

    def subscribe(
        self,
        event_type: EventType | list[EventType],
        handler: EventHandler | Callable[[Event], Any],
        filter_fn: Callable[[Event], bool] | None = None,
    ) -> Callable[[], None]:
        """Subscribe to event(s).

        Args:
            event_type: Event type(s) to subscribe to
            handler: Handler function or EventHandler instance
            filter_fn: Optional filter function

        Returns:
            Unsubscribe function
        """
        event_types = [event_type] if isinstance(event_type, EventType) else event_type
        subscriber = EventSubscriber(event_types, handler, filter_fn)

        for evt_type in event_types:
            if evt_type not in self._subscribers:
                self._subscribers[evt_type] = []
            self._subscribers[evt_type].append(subscriber)

        # Return unsubscribe function
        def unsubscribe() -> None:
            for evt_type in event_types:
                if evt_type in self._subscribers:
                    self._subscribers[evt_type].remove(subscriber)
                    if not self._subscribers[evt_type]:
                        del self._subscribers[evt_type]

        return unsubscribe

    async def emit(self, event: Event) -> None:
        """Emit an event to all subscribers.

        Args:
            event: Event to emit
        """
        try:
            await asyncio.wait_for(self._event_queue.put(event), timeout=5.0)
        except asyncio.TimeoutError:
            logger.warning(
                "Event queue full, dropping event",
                event_type=event.event_type,
            )

        # Keep event in history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history :]

    async def start(self) -> None:
        """Start the event bus worker."""
        if self._running:
            return

        self._running = True
        self._worker_task = asyncio.create_task(self._worker())
        logger.info("Event bus started")

    async def stop(self) -> None:
        """Stop the event bus worker."""
        self._running = False
        if self._worker_task:
            await self._worker_task
        logger.info("Event bus stopped")

    async def _worker(self) -> None:
        """Worker that processes events from queue."""
        while self._running:
            try:
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)

                subscribers = self._subscribers.get(event.event_type, [])
                if not subscribers:
                    continue

                # Run all handlers concurrently
                tasks = [sub.handle(event) for sub in subscribers]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Log any errors
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(
                            "Event handler failed",
                            event_type=event.event_type,
                            error=result,
                        )

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error("Event worker error", error=e)

    def get_event_history(
        self, event_type: EventType | None = None, limit: int = 100
    ) -> list[Event]:
        """Get event history.

        Args:
            event_type: Filter by event type (None = all)
            limit: Maximum events to return

        Returns:
            List of recent events
        """
        events = self._event_history
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return events[-limit:]

    def get_stats(self) -> dict[str, Any]:
        """Get event bus statistics."""
        return {
            "running": self._running,
            "queue_size": self._event_queue.qsize(),
            "subscribers": {evt.value: len(subs) for evt, subs in self._subscribers.items()},
            "total_events": len(self._event_history),
            "max_queue_size": self.max_queue_size,
        }


# Global event bus instance
_event_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """Get or create global event bus."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


def set_event_bus(bus: EventBus) -> None:
    """Set global event bus (for testing)."""
    global _event_bus
    _event_bus = bus
