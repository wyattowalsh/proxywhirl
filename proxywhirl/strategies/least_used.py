"""Least-used rotation strategy."""

from __future__ import annotations

import threading

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import (
    Proxy,
    ProxyPool,
    SelectionContext,
    StrategyConfig,
)


class LeastUsedStrategy:
    """
    Least-used proxy selection strategy with SelectionContext support.

    Selects the proxy with the fewest started requests, helping to
    balance load across all available proxies. Uses min-heap for
    efficient O(log n) selection.

    Performance:
        - O(log n) selection using min-heap
        - O(n) heap rebuild when pool composition changes
        - Lazy heap invalidation for optimal performance

    Thread Safety:
        Uses threading.Lock to ensure atomic select-and-mark operations,
        preventing TOCTOU race conditions where multiple threads could
        select the same "least used" proxy simultaneously.

    Implementation:
        Uses a min-heap with lazy invalidation. The heap is rebuilt when:
        1. Pool composition changes (detected via proxy ID set)
        2. Heap becomes empty after filtering
        The heap stores tuples of (requests_started, proxy_id, proxy) for
        efficient comparison and retrieval.
    """

    def __init__(self) -> None:
        """Initialize least-used strategy."""
        self.config: StrategyConfig | None = None
        self._lock = threading.Lock()
        self._heap: list[tuple[int, str, Proxy]] = []
        self._proxy_id_set: set[str] = set()  # Track pool composition

    def _rebuild_heap(self, proxies: list[Proxy]) -> None:
        """
        Rebuild the min-heap with current proxy states.

        Args:
            proxies: List of proxies to build heap from
        """
        import heapq

        self._heap = [(proxy.requests_started, str(proxy.id), proxy) for proxy in proxies]
        heapq.heapify(self._heap)
        self._proxy_id_set = {str(proxy.id) for proxy in proxies}

    def _needs_rebuild(self, current_proxy_ids: set[str]) -> bool:
        """
        Check if heap needs rebuilding due to pool composition change.

        Args:
            current_proxy_ids: Set of current proxy IDs in filtered pool

        Returns:
            True if heap needs rebuilding
        """
        return self._proxy_id_set != current_proxy_ids or not self._heap

    def select(self, pool: ProxyPool, context: SelectionContext | None = None) -> Proxy:
        """
        Select the least-used healthy proxy using min-heap.

        Uses min-heap for O(log n) selection. The heap is lazily rebuilt when
        pool composition changes, providing optimal performance for stable pools.

        The selection and usage marking are performed atomically under a lock
        to prevent TOCTOU race conditions where multiple threads could select
        the same "least used" proxy simultaneously.

        Args:
            pool: The proxy pool to select from
            context: Optional selection context for filtering

        Returns:
            Healthy proxy with fewest started requests

        Raises:
            ProxyPoolEmptyError: If no healthy proxies are available
        """
        import heapq

        # Atomic select-and-mark to prevent TOCTOU race condition
        with self._lock:
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

            # Check if heap needs rebuilding
            current_proxy_ids = {str(p.id) for p in healthy_proxies}
            if self._needs_rebuild(current_proxy_ids):
                self._rebuild_heap(healthy_proxies)

            # Extract minimum from heap (O(log n))
            # The heap may contain stale entries (old requests_started values)
            # so we keep popping until we find a valid proxy from our filtered set
            while self._heap:
                requests_started, proxy_id, proxy = heapq.heappop(self._heap)

                # Verify proxy is still in our filtered set
                if proxy_id in current_proxy_ids:
                    # Re-push other proxies back onto heap
                    # Note: This proxy's requests_started will be incremented,
                    # so we rebuild heap on next call when composition changes

                    # Update proxy metadata to track request start (atomic with selection)
                    proxy.start_request()

                    # Invalidate heap since we modified a proxy's state
                    # This forces rebuild on next selection
                    self._proxy_id_set = set()

                    return proxy

            # If we get here, heap was empty after filtering - rebuild and retry
            self._rebuild_heap(healthy_proxies)
            if not self._heap:
                raise ProxyPoolEmptyError("No healthy proxies available")

            # Extract minimum from rebuilt heap
            requests_started, proxy_id, proxy = heapq.heappop(self._heap)

            # Update proxy metadata to track request start (atomic with selection)
            proxy.start_request()

            # Invalidate heap since we modified a proxy's state
            self._proxy_id_set = set()

            return proxy

    def configure(self, config: StrategyConfig) -> None:
        """Configure the strategy with custom settings."""
        self.config = config

    def validate_metadata(self, pool: ProxyPool) -> bool:
        """
        Validate that proxies have request tracking metadata.

        Args:
            pool: The proxy pool to validate

        Returns:
            True if all proxies have requests_started field
        """
        # All Proxy objects now have requests_started field by default
        return True

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        """Record the result of using a proxy."""
        # Pass strategy's alpha to avoid mutating proxy state
        alpha = self.config.ema_alpha if self.config is not None else None
        proxy.complete_request(success=success, response_time_ms=response_time_ms, alpha=alpha)
