"""Webhook retry logic with exponential backoff.

Implements reliable webhook delivery with exponential
backoff, circuit breaking, and comprehensive logging.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from loguru import logger


class WebhookStatus(str, Enum):
    """Status of webhook delivery."""

    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class WebhookEvent:
    """Webhook event to deliver."""

    event_id: str
    event_type: str
    payload: dict[str, Any]
    target_url: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    attempt_count: int = 0
    last_attempt_at: datetime | None = None
    status: WebhookStatus = WebhookStatus.PENDING


@dataclass
class WebhookRetryConfig:
    """Configuration for webhook retries."""

    max_attempts: int = 5
    initial_delay_seconds: int = 5
    max_delay_seconds: int = 3600
    backoff_multiplier: float = 2.0
    timeout_seconds: int = 30


class WebhookRetryManager:
    """Manages webhook retry logic."""

    def __init__(self, config: WebhookRetryConfig | None = None) -> None:
        """Initialize webhook retry manager.

        Args:
            config: Retry configuration
        """
        self.config = config or WebhookRetryConfig()
        self._events: dict[str, WebhookEvent] = {}
        self._failed_count = 0
        logger.debug("WebhookRetryManager initialized")

    def queue_webhook(
        self,
        event_id: str,
        event_type: str,
        payload: dict[str, Any],
        target_url: str,
    ) -> bool:
        """Queue webhook for delivery.

        Args:
            event_id: Event ID
            event_type: Event type
            payload: Event payload
            target_url: Target URL

        Returns:
            True if queued
        """
        if event_id in self._events:
            logger.warning(f"Event already exists: {event_id}")
            return False

        event = WebhookEvent(
            event_id=event_id,
            event_type=event_type,
            payload=payload,
            target_url=target_url,
        )
        self._events[event_id] = event
        logger.info(f"Webhook queued: {event_id} ({event_type})")
        return True

    def get_next_retry_delay(self, attempt: int) -> int:
        """Calculate next retry delay.

        Args:
            attempt: Attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        delay = int(self.config.initial_delay_seconds * (self.config.backoff_multiplier**attempt))
        return min(delay, self.config.max_delay_seconds)

    def should_retry(self, event_id: str) -> bool:
        """Check if event should be retried.

        Args:
            event_id: Event ID

        Returns:
            True if should retry
        """
        if event_id not in self._events:
            return False

        event = self._events[event_id]
        return (
            event.status != WebhookStatus.DELIVERED
            and event.attempt_count < self.config.max_attempts
        )

    def mark_attempt(self, event_id: str, success: bool, error: str | None = None) -> bool:
        """Mark webhook delivery attempt.

        Args:
            event_id: Event ID
            success: Whether attempt succeeded
            error: Error message if failed

        Returns:
            True if marked
        """
        if event_id not in self._events:
            return False

        event = self._events[event_id]
        event.attempt_count += 1
        event.last_attempt_at = datetime.now(timezone.utc)

        if success:
            event.status = WebhookStatus.DELIVERED
            logger.info(f"Webhook delivered: {event_id}")
        else:
            if self.should_retry(event_id):
                event.status = WebhookStatus.RETRYING
                logger.warning(f"Webhook will retry: {event_id} ({error})")
            else:
                event.status = WebhookStatus.FAILED
                self._failed_count += 1
                logger.error(f"Webhook failed (max retries): {event_id}")

        return True

    def get_pending_webhooks(self) -> list[WebhookEvent]:
        """Get webhooks pending delivery.

        Returns:
            List of pending events
        """
        return [
            e
            for e in self._events.values()
            if e.status in (WebhookStatus.PENDING, WebhookStatus.RETRYING)
        ]

    def export_metrics(self) -> dict[str, Any]:
        """Export webhook metrics.

        Returns:
            Dictionary of metrics
        """
        delivered = sum(1 for e in self._events.values() if e.status == WebhookStatus.DELIVERED)
        failed = sum(1 for e in self._events.values() if e.status == WebhookStatus.FAILED)

        return {
            "total_webhooks": len(self._events),
            "delivered": delivered,
            "failed": failed,
            "pending": len(self.get_pending_webhooks()),
        }
