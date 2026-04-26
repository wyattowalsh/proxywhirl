"""Tests for event-driven architecture."""

import asyncio
from uuid import uuid4

import pytest

from proxywhirl.events import Event, EventBus, EventHandler, EventType


class TestEventModel:
    """Test Event model."""

    def test_event_creation(self):
        """Test creating an event."""
        event = Event(
            event_type=EventType.PROXY_ADDED,
            source="test_component",
            payload={"proxy_id": "proxy-123"},
        )

        assert event.event_type == EventType.PROXY_ADDED
        assert event.source == "test_component"
        assert event.payload["proxy_id"] == "proxy-123"
        assert event.event_id is not None
        assert event.timestamp is not None

    def test_event_with_correlation(self):
        """Test event with correlation ID."""
        correlation_id = uuid4()
        event = Event(
            event_type=EventType.PROXY_ADDED,
            source="test",
            correlation_id=correlation_id,
        )

        assert event.correlation_id == correlation_id


class SimpleEventHandler(EventHandler):
    """Simple test event handler."""

    def __init__(self):
        self.handled_events = []

    async def handle(self, event: Event) -> None:
        """Handle an event."""
        self.handled_events.append(event)


@pytest.mark.asyncio
async def test_event_bus_subscribe():
    """Test subscribing to events."""
    bus = EventBus()
    handler = SimpleEventHandler()

    bus.subscribe(EventType.PROXY_ADDED, handler)

    await bus.start()
    try:
        event = Event(
            event_type=EventType.PROXY_ADDED,
            source="test",
        )
        await bus.emit(event)

        # Give handler time to process
        await asyncio.sleep(0.1)

        assert len(handler.handled_events) == 1
        assert handler.handled_events[0].event_type == EventType.PROXY_ADDED
    finally:
        await bus.stop()


@pytest.mark.asyncio
async def test_event_bus_multiple_subscribers():
    """Test multiple subscribers."""
    bus = EventBus()
    handler1 = SimpleEventHandler()
    handler2 = SimpleEventHandler()

    bus.subscribe(EventType.PROXY_ADDED, handler1)
    bus.subscribe(EventType.PROXY_ADDED, handler2)

    await bus.start()
    try:
        event = Event(
            event_type=EventType.PROXY_ADDED,
            source="test",
        )
        await bus.emit(event)

        await asyncio.sleep(0.1)

        assert len(handler1.handled_events) == 1
        assert len(handler2.handled_events) == 1
    finally:
        await bus.stop()


@pytest.mark.asyncio
async def test_event_bus_unsubscribe():
    """Test unsubscribing from events."""
    bus = EventBus()
    handler = SimpleEventHandler()

    unsubscribe = bus.subscribe(EventType.PROXY_ADDED, handler)

    await bus.start()
    try:
        event = Event(
            event_type=EventType.PROXY_ADDED,
            source="test",
        )
        await bus.emit(event)
        await asyncio.sleep(0.1)

        assert len(handler.handled_events) == 1

        # Unsubscribe
        unsubscribe()

        # Emit another event
        await bus.emit(event)
        await asyncio.sleep(0.1)

        # Should still have only 1
        assert len(handler.handled_events) == 1
    finally:
        await bus.stop()


@pytest.mark.asyncio
async def test_event_bus_filter():
    """Test event filtering."""
    bus = EventBus()
    handler = SimpleEventHandler()

    def filter_fn(event: Event) -> bool:
        return event.payload.get("important", False)

    bus.subscribe(
        EventType.PROXY_ADDED,
        handler,
        filter_fn=filter_fn,
    )

    await bus.start()
    try:
        # Important event
        important_event = Event(
            event_type=EventType.PROXY_ADDED,
            source="test",
            payload={"important": True},
        )
        await bus.emit(important_event)

        # Not important event
        not_important_event = Event(
            event_type=EventType.PROXY_ADDED,
            source="test",
            payload={"important": False},
        )
        await bus.emit(not_important_event)

        await asyncio.sleep(0.1)

        # Should only have important event
        assert len(handler.handled_events) == 1
        assert handler.handled_events[0].payload["important"] is True
    finally:
        await bus.stop()


@pytest.mark.asyncio
async def test_event_bus_function_handler():
    """Test using function as event handler."""
    bus = EventBus()
    events = []

    async def handle_event(event: Event) -> None:
        events.append(event)

    bus.subscribe(EventType.PROXY_ADDED, handle_event)

    await bus.start()
    try:
        event = Event(
            event_type=EventType.PROXY_ADDED,
            source="test",
        )
        await bus.emit(event)

        await asyncio.sleep(0.1)

        assert len(events) == 1
    finally:
        await bus.stop()


@pytest.mark.asyncio
async def test_event_bus_event_history():
    """Test event history tracking."""
    bus = EventBus()

    await bus.start()
    try:
        for i in range(5):
            event = Event(
                event_type=EventType.PROXY_ADDED,
                source="test",
                payload={"index": i},
            )
            await bus.emit(event)

        await asyncio.sleep(0.1)

        history = bus.get_event_history()
        assert len(history) == 5

        # Filter by event type
        history = bus.get_event_history(event_type=EventType.PROXY_ADDED)
        assert len(history) == 5

        # Limit
        history = bus.get_event_history(limit=2)
        assert len(history) == 2
    finally:
        await bus.stop()


@pytest.mark.asyncio
async def test_event_bus_stats():
    """Test event bus statistics."""
    bus = EventBus()
    handler = SimpleEventHandler()

    bus.subscribe(EventType.PROXY_ADDED, handler)

    stats = bus.get_stats()
    assert stats["running"] is False
    assert stats["queue_size"] == 0

    await bus.start()
    try:
        event = Event(
            event_type=EventType.PROXY_ADDED,
            source="test",
        )
        await bus.emit(event)

        await asyncio.sleep(0.1)

        stats = bus.get_stats()
        assert stats["running"] is True
        assert stats["subscribers"][EventType.PROXY_ADDED.value] == 1
    finally:
        await bus.stop()


@pytest.mark.asyncio
async def test_event_bus_multiple_event_types():
    """Test subscribing to multiple event types."""
    bus = EventBus()
    handler = SimpleEventHandler()

    bus.subscribe([EventType.PROXY_ADDED, EventType.PROXY_REMOVED], handler)

    await bus.start()
    try:
        event1 = Event(
            event_type=EventType.PROXY_ADDED,
            source="test",
        )
        event2 = Event(
            event_type=EventType.PROXY_REMOVED,
            source="test",
        )

        await bus.emit(event1)
        await bus.emit(event2)

        await asyncio.sleep(0.1)

        assert len(handler.handled_events) == 2
    finally:
        await bus.stop()
