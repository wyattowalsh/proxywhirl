"""Round-robin rotation strategy."""

from __future__ import annotations

import threading
from uuid import UUID

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import (
    Proxy,
    ProxyPool,
    SelectionContext,
    StrategyConfig,
)


class RoundRobinStrategy:
    """
    Round-robin proxy selection strategy with SelectionContext support.

    Selects proxies in sequential order, wrapping around to the first
    proxy after reaching the end of the list. Only selects healthy proxies.
    Supports filtering based on SelectionContext (e.g., failed_proxy_ids).

    Thread Safety:
        Uses threading.Lock to protect _current_index access, ensuring atomic
        index increment and preventing proxy skipping or duplicate selection
        in multi-threaded environments.
    """

    def __init__(self) -> None:
        """Initialize round-robin strategy."""
        self._last_proxy_id: UUID | None = None
        self._lock = threading.Lock()
        self.config: StrategyConfig | None = None

    def select(self, pool: ProxyPool, context: SelectionContext | None = None) -> Proxy:
        """
        Select next proxy in round-robin order.

        Args:
            pool: The proxy pool to select from
            context: Optional selection context for filtering

        Returns:
            Next healthy proxy in rotation

        Raises:
            ProxyPoolEmptyError: If no healthy proxies are available
        """
        healthy_proxies = pool.get_healthy_proxies()

        if not healthy_proxies:
            raise ProxyPoolEmptyError("No healthy proxies available in pool")

        # Filter out failed proxies if context provided
        if context and context.failed_proxy_ids:
            failed_ids = set(context.failed_proxy_ids)
            healthy_proxies = [p for p in healthy_proxies if str(p.id) not in failed_ids]

            if not healthy_proxies:
                raise ProxyPoolEmptyError(
                    "No healthy proxies available after filtering failed proxies"
                )

        # Stable order by proxy id so circuit-breaker subset churn does not skip peers
        ordered = sorted(healthy_proxies, key=lambda p: str(p.id))
        with self._lock:
            if self._last_proxy_id is None:
                index = 0
            else:
                id_order = [p.id for p in ordered]
                try:
                    last_index = id_order.index(self._last_proxy_id)
                    index = (last_index + 1) % len(ordered)
                except ValueError:
                    index = 0
            proxy = ordered[index]
            self._last_proxy_id = proxy.id

        # Update proxy metadata to track request start
        proxy.start_request()

        return proxy

    def configure(self, config: StrategyConfig) -> None:
        """
        Configure the strategy with custom settings.

        Args:
            config: Strategy configuration object
        """
        self.config = config

    def validate_metadata(self, pool: ProxyPool) -> bool:
        """
        Validate that pool has required metadata for this strategy.

        Round-robin doesn't require any special metadata, so always returns True.

        Args:
            pool: The proxy pool to validate

        Returns:
            Always True for round-robin
        """
        return True

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        """
        Record the result of using a proxy.

        Updates proxy statistics based on request outcome and completes the request tracking.

        Args:
            proxy: The proxy that was used
            success: Whether the request succeeded
            response_time_ms: Response time in milliseconds
        """
        # Pass strategy's alpha to avoid mutating proxy state
        alpha = self.config.ema_alpha if self.config is not None else None
        proxy.complete_request(success=success, response_time_ms=response_time_ms, alpha=alpha)
