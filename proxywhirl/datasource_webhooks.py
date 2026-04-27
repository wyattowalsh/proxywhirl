"""Webhook support for datasource updates.

Allows proxy sources to push updates via webhooks instead of polling.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable
from urllib.parse import urlparse

from loguru import logger


class WebhookEvent(str, Enum):
    """Types of webhook events."""

    PROXIES_UPDATED = "proxies.updated"
    SOURCE_ADDED = "source.added"
    SOURCE_REMOVED = "source.removed"
    HEALTH_CHANGED = "health.changed"


@dataclass
class WebhookPayload:
    """Webhook event payload."""

    event: WebhookEvent
    source_name: str
    timestamp: datetime = field(default_factory=datetime.now)
    data: dict[str, Any] = field(default_factory=dict)
    signature: str | None = None  # HMAC signature for verification

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return {
            "event": self.event.value,
            "source_name": self.source_name,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "signature": self.signature,
        }


@dataclass
class WebhookConfig:
    """Configuration for a webhook subscription."""

    url: str
    events: list[WebhookEvent] = field(default_factory=list)
    enabled: bool = True
    secret: str | None = None  # HMAC secret for verification
    retry_count: int = 3
    timeout_seconds: int = 30
    headers: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate webhook URL."""
        try:
            parsed = urlparse(self.url)
            if not parsed.scheme or parsed.scheme not in ('http', 'https'):
                raise ValueError(f"Invalid webhook URL: {self.url}")
            if not parsed.netloc:
                raise ValueError(f"Invalid webhook URL (no host): {self.url}")
        except Exception as e:
            raise ValueError(f"Failed to parse webhook URL: {e}")

        if not self.events:
            raise ValueError("Must specify at least one event type")


class WebhookManager:
    """Manages webhook subscriptions and delivery."""

    def __init__(self):
        """Initialize webhook manager."""
        self._webhooks: dict[str, WebhookConfig] = {}
        self._delivery_log: list[tuple[str, WebhookEvent, bool, str | None]] = []
        self._handlers: list[Callable[[WebhookPayload], None]] = []

    def register_webhook(self, webhook_id: str, config: WebhookConfig) -> None:
        """Register a webhook.

        Args:
            webhook_id: Unique webhook identifier
            config: Webhook configuration

        Raises:
            ValueError: If config is invalid
        """
        config.__post_init__()  # Validate on registration
        self._webhooks[webhook_id] = config
        logger.info(f"Registered webhook {webhook_id}: {config.url}")

    def unregister_webhook(self, webhook_id: str) -> bool:
        """Unregister a webhook.

        Args:
            webhook_id: Webhook to remove

        Returns:
            True if webhook existed
        """
        if webhook_id in self._webhooks:
            del self._webhooks[webhook_id]
            logger.info(f"Unregistered webhook {webhook_id}")
            return True
        return False

    def disable_webhook(self, webhook_id: str) -> bool:
        """Disable a webhook.

        Args:
            webhook_id: Webhook to disable

        Returns:
            True if webhook exists
        """
        if webhook_id in self._webhooks:
            self._webhooks[webhook_id].enabled = False
            logger.info(f"Disabled webhook {webhook_id}")
            return True
        return False

    def enable_webhook(self, webhook_id: str) -> bool:
        """Enable a webhook.

        Args:
            webhook_id: Webhook to enable

        Returns:
            True if webhook exists
        """
        if webhook_id in self._webhooks:
            self._webhooks[webhook_id].enabled = True
            logger.info(f"Enabled webhook {webhook_id}")
            return True
        return False

    def add_handler(self, handler: Callable[[WebhookPayload], None]) -> None:
        """Add a local webhook handler.

        Handlers are called immediately when webhooks are received.

        Args:
            handler: Callable that receives WebhookPayload
        """
        self._handlers.append(handler)

    async def dispatch_webhook(self, payload: WebhookPayload) -> None:
        """Dispatch a webhook to all registered endpoints.

        Args:
            payload: Webhook payload to send
        """
        # Call local handlers first
        for handler in self._handlers:
            try:
                handler(payload)
            except Exception as e:
                logger.error(f"Error in webhook handler: {e}", exc_info=True)

        # Send to remote webhooks
        applicable_webhooks = [
            (webhook_id, config)
            for webhook_id, config in self._webhooks.items()
            if config.enabled and payload.event in config.events
        ]

        if not applicable_webhooks:
            return

        logger.debug(
            f"Sending webhook {payload.event.value} to "
            f"{len(applicable_webhooks)} endpoints"
        )

        for webhook_id, config in applicable_webhooks:
            await self._send_webhook(webhook_id, config, payload)

    async def _send_webhook(
        self,
        webhook_id: str,
        config: WebhookConfig,
        payload: WebhookPayload,
    ) -> None:
        """Send webhook to a single endpoint.

        Args:
            webhook_id: Webhook identifier
            config: Webhook configuration
            payload: Payload to send
        """
        import asyncio
        import hashlib
        import hmac
        import json

        import httpx

        # Generate HMAC signature if secret configured
        if config.secret:
            payload_json = json.dumps(payload.to_dict(), default=str)
            signature = hmac.new(
                config.secret.encode(),
                payload_json.encode(),
                hashlib.sha256,
            ).hexdigest()
            payload.signature = f"sha256={signature}"

        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Event": payload.event.value,
            **config.headers,
        }

        if payload.signature:
            headers["X-Webhook-Signature"] = payload.signature

        payload_json = json.dumps(payload.to_dict(), default=str)

        # Retry logic
        last_error = None
        for attempt in range(config.retry_count):
            try:
                async with httpx.AsyncClient() as client:
                    response = await asyncio.wait_for(
                        client.post(
                            config.url,
                            content=payload_json,
                            headers=headers,
                            timeout=config.timeout_seconds,
                        ),
                        timeout=config.timeout_seconds + 5,
                    )

                    if response.status_code in (200, 201, 202, 204):
                        self._delivery_log.append(
                            (webhook_id, payload.event, True, None)
                        )
                        logger.debug(
                            f"Webhook {webhook_id} delivered "
                            f"({response.status_code})"
                        )
                        return
                    else:
                        last_error = f"HTTP {response.status_code}"

            except asyncio.TimeoutError:
                last_error = "Timeout"
            except Exception as e:
                last_error = str(e)

            if attempt < config.retry_count - 1:
                await asyncio.sleep(2 ** attempt)

        # All retries failed
        self._delivery_log.append(
            (webhook_id, payload.event, False, last_error)
        )
        logger.warning(
            f"Failed to deliver webhook {webhook_id} after "
            f"{config.retry_count} attempts: {last_error}"
        )

    def get_webhook(self, webhook_id: str) -> WebhookConfig | None:
        """Get webhook configuration.

        Args:
            webhook_id: Webhook identifier

        Returns:
            Configuration or None
        """
        return self._webhooks.get(webhook_id)

    def list_webhooks(self) -> dict[str, WebhookConfig]:
        """List all registered webhooks.

        Returns:
            Dict of {webhook_id: config}
        """
        return dict(self._webhooks)

    def get_delivery_log(
        self, webhook_id: str | None = None, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Get webhook delivery log.

        Args:
            webhook_id: Filter by webhook or None for all
            limit: Maximum entries to return

        Returns:
            List of delivery log entries
        """
        log = self._delivery_log[-limit:] if self._delivery_log else []

        if webhook_id:
            log = [entry for entry in log if entry[0] == webhook_id]

        return [
            {
                "webhook_id": wid,
                "event": event.value,
                "success": success,
                "error": error,
            }
            for wid, event, success, error in log
        ]
