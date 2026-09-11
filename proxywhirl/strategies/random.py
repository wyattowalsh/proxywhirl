"""Random rotation strategy."""

from __future__ import annotations

import random

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import (
    Proxy,
    ProxyPool,
    SelectionContext,
    StrategyConfig,
)


class RandomStrategy:
    """
    Random proxy selection strategy with SelectionContext support.

    Randomly selects a proxy from the pool of healthy proxies.
    Provides unpredictable rotation for scenarios where sequential
    patterns should be avoided.

    Thread Safety: Uses Python's random module which is thread-safe
    via GIL-protected random number generation. No additional locking required.
    """

    def __init__(self) -> None:
        """Initialize random strategy."""
        self.config: StrategyConfig | None = None

    def select(self, pool: ProxyPool, context: SelectionContext | None = None) -> Proxy:
        """
        Select a random healthy proxy.

        Args:
            pool: The proxy pool to select from
            context: Optional selection context for filtering

        Returns:
            Randomly selected healthy proxy

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

        # Non-cryptographic randomness is sufficient for proxy load balancing.
        proxy = random.choice(healthy_proxies)  # nosec B311

        # Update proxy metadata to track request start
        proxy.start_request()

        return proxy

    def configure(self, config: StrategyConfig) -> None:
        """Configure the strategy with custom settings."""
        self.config = config

    def validate_metadata(self, pool: ProxyPool) -> bool:
        """Random selection doesn't require metadata validation."""
        return True

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        """Record the result of using a proxy."""
        # Pass strategy's alpha to avoid mutating proxy state
        alpha = self.config.ema_alpha if self.config is not None else None
        proxy.complete_request(success=success, response_time_ms=response_time_ms, alpha=alpha)
