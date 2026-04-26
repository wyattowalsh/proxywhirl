"""Webhook delivery system for event notifications.

Provides asynchronous webhook notifications for proxy events, health changes,
strategy updates, and custom events.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable
from uuid import uuid4

import httpx
from loguru import logger


class WebhookEventType(str, Enum):
    """Types of events that can trigger webhooks."""

    PROXY_ADDED = "proxy.added"
    PROXY_REMOVED = "proxy.removed"
    PROXY_HEALTH_CHANGED = "proxy.health_changed"
    PROXY_PERFORMANCE_UPDATE = "proxy.performance_update"
    POOL_SIZE_CHANGED = "pool.size_changed"
    STRATEGY_CHANGED = "strategy.changed"
    ROTATION_EVENT = "rotation.event"
    ERROR_OCCURRED = "error.occurred"
    COMPLIANCE_EVENT = "compliance.event"


@dataclass
class WebhookPayload:
    """Webhook event payload."""

    event_type: WebhookEventType
    timestamp: float = field(default_factory=time.time)
    event_id: str = field(default_factory=lambda: uuid4().hex)
    data: dict[str, Any] = field(default_factory=dict)
    source: str = "proxywhirl"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation of payload
        """
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "event_id": self.event_id,
            "data": self.data,
            "source": self.source,
        }


@dataclass
class WebhookConfig:
    """Webhook configuration."""

    url: str
    enabled: bool = True
    event_types: set[WebhookEventType] = field(default_factory=set)
    max_retries: int = 3
    timeout: float = 10.0
    headers: dict[str, str] = field(default_factory=dict)
    secret_key: str | None = None


class WebhookDelivery:
    """Webhook delivery system with retry logic and batching."""

    def __init__(self, max_concurrent: int = 10):
        """Initialize webhook delivery system.

        Args:
            max_concurrent: Maximum concurrent webhook deliveries
        """
        self.max_concurrent = max_concurrent
        self.webhooks: dict[str, WebhookConfig] = {}
        self.event_queue: asyncio.Queue[WebhookPayload] = asyncio.Queue()
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.delivery_stats = {
            "sent": 0,
            "failed": 0,
            "retried": 0,
        }

    def register_webhook(
        self,
        url: str,
        event_types: list[WebhookEventType] | None = None,
        secret_key: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Register a webhook endpoint.

        Args:
            url: Webhook URL to deliver events to
            event_types: List of event types to subscribe to
            secret_key: Optional secret key for HMAC signing
            **kwargs: Additional configuration options

        Returns:
            Webhook ID
        """
        webhook_id = uuid4().hex
        config = WebhookConfig(
            url=url,
            event_types=set(event_types or []),
            secret_key=secret_key,
            **kwargs,
        )
        self.webhooks[webhook_id] = config
        logger.info(f"Registered webhook {webhook_id} to {url}")
        return webhook_id

    def unregister_webhook(self, webhook_id: str) -> bool:
        """Unregister a webhook.

        Args:
            webhook_id: ID of webhook to remove

        Returns:
            True if webhook was removed, False if not found
        """
        if webhook_id in self.webhooks:
            del self.webhooks[webhook_id]
            logger.info(f"Unregistered webhook {webhook_id}")
            return True
        return False

    async def emit_event(self, payload: WebhookPayload) -> None:
        """Emit an event to subscribed webhooks.

        Args:
            payload: Event payload to deliver
        """
        await self.event_queue.put(payload)

    async def _deliver_webhook(
        self,
        webhook_id: str,
        payload: WebhookPayload,
    ) -> bool:
        """Deliver webhook with retry logic.

        Args:
            webhook_id: ID of webhook to deliver to
            payload: Payload to deliver

        Returns:
            True if delivered successfully, False otherwise
        """
        config = self.webhooks.get(webhook_id)
        if not config or not config.enabled:
            return False

        if config.event_types and payload.event_type not in config.event_types:
            return True  # Not subscribed to this event type

        async with self.semaphore:
            for attempt in range(config.max_retries):
                try:
                    async with httpx.AsyncClient() as client:
                        headers = dict(config.headers)
                        if config.secret_key:
                            headers["X-ProxyWhirl-Signature"] = self._sign_payload(
                                payload,
                                config.secret_key,
                            )

                        response = await client.post(
                            config.url,
                            json=payload.to_dict(),
                            headers=headers,
                            timeout=config.timeout,
                        )
                        response.raise_for_status()
                        self.delivery_stats["sent"] += 1
                        return True

                except Exception as e:
                    logger.warning(
                        f"Webhook delivery attempt {attempt + 1}/{config.max_retries} "
                        f"failed: {e}"
                    )
                    if attempt < config.max_retries - 1:
                        self.delivery_stats["retried"] += 1
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff

            self.delivery_stats["failed"] += 1
            return False

    async def start_delivery_loop(self) -> None:
        """Start the webhook delivery loop.

        This should be run as a background task.
        """
        while True:
            try:
                payload = await asyncio.wait_for(
                    self.event_queue.get(),
                    timeout=1.0,
                )

                # Deliver to all subscribed webhooks
                tasks = [
                    self._deliver_webhook(webhook_id, payload)
                    for webhook_id in self.webhooks
                ]
                await asyncio.gather(*tasks, return_exceptions=True)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Webhook delivery loop error: {e}")

    @staticmethod
    def _sign_payload(payload: WebhookPayload, secret_key: str) -> str:
        """Sign webhook payload with HMAC.

        Args:
            payload: Payload to sign
            secret_key: Secret key for signing

        Returns:
            HMAC signature
        """
        import hashlib
        import hmac
        import json

        payload_str = json.dumps(payload.to_dict(), sort_keys=True)
        signature = hmac.new(
            secret_key.encode(),
            payload_str.encode(),
            hashlib.sha256,
        ).hexdigest()
        return signature

    def get_stats(self) -> dict[str, int]:
        """Get delivery statistics.

        Returns:
            Dictionary of delivery stats
        """
        return self.delivery_stats.copy()

    def reset_stats(self) -> None:
        """Reset delivery statistics."""
        self.delivery_stats = {
            "sent": 0,
            "failed": 0,
            "retried": 0,
        }
