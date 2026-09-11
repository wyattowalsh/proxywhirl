"""Weighted rotation strategy."""

from __future__ import annotations

import random
import threading

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import (
    Proxy,
    ProxyPool,
    SelectionContext,
    StrategyConfig,
)


class WeightedStrategy:
    """
    Weighted proxy selection strategy with SelectionContext support.

    Selects proxies based on custom weights or success rates. When custom weights
    are provided via StrategyConfig, they take precedence. Otherwise, weights are
    derived from success_rate. Uses weighted random selection to favor
    higher-performing proxies while still giving all proxies a chance.

    Supports:
    - Custom weights via StrategyConfig.weights (proxy URL -> weight mapping)
    - Fallback to success_rate-based weights
    - Minimum weight (0.1) to ensure all proxies have selection chance
    - SelectionContext for filtering (e.g., failed_proxy_ids)
    - Weight caching to avoid O(n) recalculation on every selection

    Thread Safety:
        Uses threading.Lock to protect weight cache access, ensuring atomic
        cache validation and update operations. Prevents race conditions where
        multiple threads could trigger duplicate weight recalculations or
        inconsistent cache states.
    """

    def __init__(self) -> None:
        """Initialize weighted strategy."""
        self.config: StrategyConfig | None = None
        self._cached_weights: list[float] | None = None
        self._cached_proxy_ids: list[str] | None = None
        self._cache_valid: bool = False
        self._cache_lock = threading.Lock()

    def _invalidate_cache(self) -> None:
        """
        Invalidate the weight cache, forcing recalculation on next selection.

        Thread-safe: Acquires cache lock to ensure atomicity of invalidation.
        """
        with self._cache_lock:
            self._cache_valid = False
            self._cached_weights = None
            self._cached_proxy_ids = None

    def _calculate_weights(self, proxies: list[Proxy]) -> list[float]:
        """
        Calculate weights for the given proxies.

        Weights are always normalized to sum to 1.0 to maintain the invariant
        that total weight sum equals 1.0, even when proxies are removed.

        Args:
            proxies: List of proxies to calculate weights for

        Returns:
            List of normalized weights corresponding to each proxy (sum = 1.0)
        """
        weights = []
        for proxy in proxies:
            if self.config and self.config.weights:
                # Use custom weights from config (proxy id preferred, then URL)
                custom_weight = self.config.weights.get(str(proxy.id))
                if custom_weight is None:
                    custom_weight = self.config.weights.get(proxy.url, None)
                if custom_weight is not None and custom_weight > 0:
                    weights.append(custom_weight)
                else:
                    # Fallback to success rate or minimum weight
                    weights.append(max(proxy.success_rate, 0.1))
            else:
                # Use success rates as weights
                # Add small base weight (0.1) to give all proxies a chance
                weights.append(max(proxy.success_rate, 0.1))

        # Handle edge case: all weights are zero/negative (shouldn't happen with max(0.1))
        if all(w <= 0 for w in weights):
            # Fallback to uniform weights
            weights = [1.0] * len(weights)

        # Normalize weights to sum to 1.0
        # This ensures the invariant is maintained even when proxies are removed
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
        else:
            # Fallback to uniform normalized weights
            weights = [1.0 / len(weights)] * len(weights)

        return weights

    def _get_weights(self, proxies: list[Proxy]) -> list[float]:
        """
        Get weights for proxies, using cache if valid.

        Thread-safe: Acquires cache lock to ensure atomic cache check and update.
        Prevents race conditions where multiple threads could trigger duplicate
        weight recalculations.

        Args:
            proxies: List of proxies to get weights for

        Returns:
            List of weights corresponding to each proxy
        """
        # Include counters that feed success_rate so live health changes invalidate weights.
        current_proxy_ids = [
            (
                f"{proxy.id}:{proxy.total_successes}:{proxy.total_failures}:"
                f"{proxy.requests_completed}:{proxy.average_response_time_ms}:"
                f"{proxy.ema_response_time_ms}"
            )
            for proxy in proxies
        ]

        # Protect cache access with lock
        with self._cache_lock:
            # Check if cache is valid
            if (
                self._cache_valid
                and self._cached_proxy_ids == current_proxy_ids
                and self._cached_weights is not None
            ):
                # Cache hit - return cached weights
                return self._cached_weights

            # Cache miss - recalculate weights
            weights = self._calculate_weights(proxies)

            # Update cache atomically
            self._cached_weights = weights
            self._cached_proxy_ids = current_proxy_ids
            self._cache_valid = True

            return weights

    def select(self, pool: ProxyPool, context: SelectionContext | None = None) -> Proxy:
        """
        Select a proxy weighted by custom weights or success rate.

        Uses cached weights when possible to avoid O(n) recalculation on every call.
        Cache is invalidated when the proxy set changes (different IDs).

        Args:
            pool: The proxy pool to select from
            context: Optional selection context for filtering

        Returns:
            Weighted-random selected healthy proxy

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

        # Get weights (from cache if valid, otherwise recalculate)
        weights = self._get_weights(healthy_proxies)

        # Use non-cryptographic weighted selection for proxy load balancing.
        selected = random.choices(  # nosec B311
            healthy_proxies, weights=weights, k=1
        )[0]

        # Update proxy metadata to track request start
        selected.start_request()

        return selected

    def configure(self, config: StrategyConfig) -> None:
        """
        Configure the strategy with custom settings.

        Invalidates the weight cache since configuration changes may affect weights.

        Args:
            config: Strategy configuration object with optional custom weights
        """
        self.config = config
        # Invalidate cache when configuration changes
        self._invalidate_cache()

    def validate_metadata(self, pool: ProxyPool) -> bool:
        """
        Validate that pool has required metadata for weighted selection.

        Weighted strategy can work with success_rate (always available) or custom weights.

        Args:
            pool: The proxy pool to validate

        Returns:
            Always True as success_rate is always available
        """
        return True

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        """
        Record the result of using a proxy.

        Updates proxy statistics based on request outcome and invalidates the
        weight cache since success rates may have changed.

        Thread-safe: Uses double-checked locking pattern to ensure atomic
        invalidation and update. This prevents race conditions where another
        thread could select using stale weights while proxy stats are being updated.

        The lock ensures:
        1. No thread can read cached weights between invalidation and stat update
        2. Proxy stat updates are atomic with cache invalidation
        3. Multiple concurrent record_result() calls don't interfere

        Args:
            proxy: The proxy that was used
            success: Whether the request succeeded
            response_time_ms: Response time in milliseconds
        """
        # Double-checked locking: ensure atomic cache invalidation + proxy update
        # First check without lock (fast path for most calls)
        needs_invalidation = self._cache_valid

        if needs_invalidation:
            # Acquire lock for atomic invalidation + update
            with self._cache_lock:
                # Re-check under lock (double-checked locking)
                if self._cache_valid:
                    # Invalidate cache atomically
                    self._cache_valid = False
                    self._cached_weights = None
                    self._cached_proxy_ids = None

                # Update proxy stats while holding lock
                # This ensures no thread can see stale cache between invalidation and update
                alpha = self.config.ema_alpha if self.config is not None else None
                proxy.complete_request(
                    success=success, response_time_ms=response_time_ms, alpha=alpha
                )
        else:
            # Cache already invalid, just update proxy stats
            alpha = self.config.ema_alpha if self.config is not None else None
            proxy.complete_request(success=success, response_time_ms=response_time_ms, alpha=alpha)
