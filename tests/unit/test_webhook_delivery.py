"""Tests for webhook delivery."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable

import pytest


class DeliveryStatus(Enum):
    """Webhook delivery status."""

    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class WebhookEvent:
    """Webhook event."""

    id: str
    event_type: str
    payload: dict[str, Any]
    timestamp: datetime
    attempts: int = 0
    status: DeliveryStatus = DeliveryStatus.PENDING


class WebhookDeliveryManager:
    """Manages webhook delivery."""

    def __init__(self, max_retries: int = 3) -> None:
        """Initialize delivery manager."""
        self.max_retries = max_retries
        self.events: dict[str, WebhookEvent] = {}
        self.handlers: list[Callable[[WebhookEvent], bool]] = []

    def register_handler(self, handler: Callable[[WebhookEvent], bool]) -> None:
        """Register event handler."""
        self.handlers.append(handler)

    def add_event(self, event: WebhookEvent) -> None:
        """Add event for delivery."""
        self.events[event.id] = event

    def deliver(self, event_id: str) -> bool:
        """Deliver event."""
        if event_id not in self.events:
            return False
        
        event = self.events[event_id]
        event.attempts += 1
        event.status = DeliveryStatus.RETRYING
        
        for handler in self.handlers:
            if handler(event):
                event.status = DeliveryStatus.DELIVERED
                return True
        
        if event.attempts >= self.max_retries:
            event.status = DeliveryStatus.FAILED
            return False
        
        event.status = DeliveryStatus.PENDING
        return False

    def get_status(self, event_id: str) -> DeliveryStatus | None:
        """Get event status."""
        if event_id in self.events:
            return self.events[event_id].status
        return None

    def get_pending_events(self) -> list[WebhookEvent]:
        """Get pending events."""
        return [
            e for e in self.events.values()
            if e.status == DeliveryStatus.PENDING
        ]


class TestWebhookDelivery:
    """Test webhook delivery."""

    @pytest.fixture
    def manager(self) -> WebhookDeliveryManager:
        """Provide delivery manager."""
        return WebhookDeliveryManager()

    def test_add_event(self, manager) -> None:
        """Test adding event."""
        event = WebhookEvent(
            id="evt_1",
            event_type="test.event",
            payload={"data": "test"},
            timestamp=datetime.now(),
        )
        manager.add_event(event)
        
        assert "evt_1" in manager.events

    def test_initial_status_pending(self, manager) -> None:
        """Test initial status is pending."""
        event = WebhookEvent(
            id="evt_1",
            event_type="test.event",
            payload={},
            timestamp=datetime.now(),
        )
        manager.add_event(event)
        
        assert manager.get_status("evt_1") == DeliveryStatus.PENDING

    def test_delivery_success(self, manager) -> None:
        """Test successful delivery."""
        event = WebhookEvent(
            id="evt_1",
            event_type="test.event",
            payload={},
            timestamp=datetime.now(),
        )
        manager.add_event(event)
        
        def handler(e: WebhookEvent) -> bool:
            return True
        
        manager.register_handler(handler)
        result = manager.deliver("evt_1")
        
        assert result is True
        assert manager.get_status("evt_1") == DeliveryStatus.DELIVERED

    def test_delivery_failure_retry(self, manager) -> None:
        """Test failed delivery triggers retry."""
        event = WebhookEvent(
            id="evt_1",
            event_type="test.event",
            payload={},
            timestamp=datetime.now(),
        )
        manager.add_event(event)
        
        def handler(e: WebhookEvent) -> bool:
            return False
        
        manager.register_handler(handler)
        result = manager.deliver("evt_1")
        
        assert result is False
        assert manager.get_status("evt_1") == DeliveryStatus.PENDING

    def test_max_retries_exceeded(self, manager) -> None:
        """Test max retries limit."""
        event = WebhookEvent(
            id="evt_1",
            event_type="test.event",
            payload={},
            timestamp=datetime.now(),
        )
        manager.add_event(event)
        
        def handler(e: WebhookEvent) -> bool:
            return False
        
        manager.register_handler(handler)
        
        # Exhaust retries
        for _ in range(manager.max_retries):
            manager.deliver("evt_1")
        
        assert manager.get_status("evt_1") == DeliveryStatus.FAILED

    def test_multiple_handlers(self, manager) -> None:
        """Test multiple handlers."""
        event = WebhookEvent(
            id="evt_1",
            event_type="test.event",
            payload={},
            timestamp=datetime.now(),
        )
        manager.add_event(event)
        
        call_count = [0]
        
        def handler1(e: WebhookEvent) -> bool:
            call_count[0] += 1
            return False
        
        def handler2(e: WebhookEvent) -> bool:
            call_count[0] += 1
            return True
        
        manager.register_handler(handler1)
        manager.register_handler(handler2)
        
        result = manager.deliver("evt_1")
        
        assert result is True
        assert call_count[0] == 2

    def test_get_pending_events(self, manager) -> None:
        """Test getting pending events."""
        event1 = WebhookEvent(
            id="evt_1",
            event_type="test.event",
            payload={},
            timestamp=datetime.now(),
        )
        event2 = WebhookEvent(
            id="evt_2",
            event_type="test.event",
            payload={},
            timestamp=datetime.now(),
        )
        manager.add_event(event1)
        manager.add_event(event2)
        
        def handler(e: WebhookEvent) -> bool:
            return e.id == "evt_1"
        
        manager.register_handler(handler)
        manager.deliver("evt_1")
        
        pending = manager.get_pending_events()
        assert len(pending) == 1
        assert pending[0].id == "evt_2"

    def test_attempt_counter(self, manager) -> None:
        """Test attempt counter increments."""
        event = WebhookEvent(
            id="evt_1",
            event_type="test.event",
            payload={},
            timestamp=datetime.now(),
        )
        manager.add_event(event)
        
        def handler(e: WebhookEvent) -> bool:
            return False
        
        manager.register_handler(handler)
        
        assert event.attempts == 0
        manager.deliver("evt_1")
        assert event.attempts == 1
        manager.deliver("evt_1")
        assert event.attempts == 2

    def test_nonexistent_event(self, manager) -> None:
        """Test delivering nonexistent event."""
        result = manager.deliver("nonexistent")
        assert result is False

    def test_event_payload_preserved(self, manager) -> None:
        """Test event payload is preserved."""
        payload = {"key": "value", "nested": {"data": 123}}
        event = WebhookEvent(
            id="evt_1",
            event_type="test.event",
            payload=payload,
            timestamp=datetime.now(),
        )
        manager.add_event(event)
        
        assert manager.events["evt_1"].payload == payload

    def test_conditional_handler(self, manager) -> None:
        """Test handler with conditions."""
        event = WebhookEvent(
            id="evt_1",
            event_type="important.event",
            payload={},
            timestamp=datetime.now(),
        )
        manager.add_event(event)
        
        def handler(e: WebhookEvent) -> bool:
            return e.event_type == "important.event"
        
        manager.register_handler(handler)
        result = manager.deliver("evt_1")
        
        assert result is True

    def test_custom_max_retries(self) -> None:
        """Test custom max retries."""
        manager = WebhookDeliveryManager(max_retries=5)
        
        event = WebhookEvent(
            id="evt_1",
            event_type="test.event",
            payload={},
            timestamp=datetime.now(),
        )
        manager.add_event(event)
        
        def handler(e: WebhookEvent) -> bool:
            return False
        
        manager.register_handler(handler)
        
        for _ in range(5):
            manager.deliver("evt_1")
        
        assert manager.get_status("evt_1") == DeliveryStatus.FAILED
