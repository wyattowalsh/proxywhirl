"""Composite rotation strategy."""

from __future__ import annotations

from typing import Any

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import (
    Proxy,
    ProxyPool,
    SelectionContext,
    StrategyConfig,
)
from proxywhirl.strategies.base import RotationStrategy
from proxywhirl.strategies.registry import resolve_builtin_strategy
from proxywhirl.strategies.round_robin import RoundRobinStrategy


class CompositeStrategy:
    """
    Composite strategy that applies filtering and selection strategies in sequence.

    This strategy implements the filter + select pattern:
    1. Filter strategies narrow down the proxy pool based on criteria (e.g., geography)
    2. Selector strategy chooses the best proxy from the filtered set

    Geo honesty (L1-013): when ``GeoTargetedStrategy`` is used as a filter, the
    composite narrows the candidate set using ``SelectionContext`` country/region
    fields via ``_matches_filter`` — it does not re-run full geo scoring on every
    proxy. Filters that only implement ``select()`` (geo) are treated as
    geo-constraint probes; the selector owns performance/cost semantics.

    Example:
        >>> # Filter by geography, then select by performance
        >>> from proxywhirl.strategies import CompositeStrategy, GeoTargetedStrategy, PerformanceBasedStrategy
        >>> strategy = CompositeStrategy(
        ...     filters=[GeoTargetedStrategy()],
        ...     selector=PerformanceBasedStrategy()
        ... )
        >>> proxy = strategy.select(pool, SelectionContext(target_country="US"))

    Thread Safety:
        Thread-safe if all component strategies are thread-safe.

    Performance:
        Selection time is sum of filter and selector times.
        Target: <5ms total (SC-007).
    """

    def __init__(
        self,
        filters: list[RotationStrategy] | None = None,
        selector: RotationStrategy | None = None,
    ):
        """
        Initialize composite strategy.

        Args:
            filters: List of filtering strategies to apply sequentially
            selector: Final selection strategy to choose from filtered pool

        Raises:
            ValueError: If both filters and selector are None
        """

        self.filters = filters or []
        self.selector = selector or RoundRobinStrategy()

        if not self.filters and selector is None:
            raise ValueError("CompositeStrategy requires at least one filter or a selector")

    def select(self, pool: ProxyPool, context: SelectionContext | None = None) -> Proxy:
        """
        Select a proxy by applying filters then selector.

        Process:
        1. Start with full pool of healthy proxies
        2. Apply each filter strategy sequentially
        3. Apply selector strategy to filtered set
        4. Return selected proxy

        Args:
            pool: The proxy pool to select from
            context: Request context with filtering criteria

        Returns:
            Selected proxy from filtered pool

        Raises:
            ProxyPoolEmptyError: If filters eliminate all proxies

        Performance:
            Target: <5ms total including all filters and selector (SC-007)
        """

        if context is None:
            from proxywhirl.models import SelectionContext

            context = SelectionContext()

        # Start with the same selectable health states used by ProxyPool.
        filtered_proxies = pool.get_healthy_proxies()

        if not filtered_proxies:
            raise ProxyPoolEmptyError("No healthy proxies available")

        # Apply filters sequentially
        for filter_strategy in self.filters:
            # Probe filters against detached model copies. A filter strategy's
            # ``select`` contract starts a request, so using live objects here
            # would mutate counters for a request that is never sent. Snapshot /
            # restore is also unsafe because it can overwrite concurrent updates.
            temp_pool = pool.__class__(name=f"{pool.name}-filtered")
            for proxy in filtered_proxies:
                temp_pool.add_proxy(self._detached_candidate(proxy))

            try:
                selected = filter_strategy.select(temp_pool, context)
            except ProxyPoolEmptyError:
                # Filter eliminated all proxies
                raise ProxyPoolEmptyError(
                    f"Filter {filter_strategy.__class__.__name__} eliminated all proxies"
                )
            else:
                # If filter returned one proxy, use it to filter the set
                # For geo-filtering, this means only proxies matching criteria remain
                filtered_proxies = [
                    p for p in filtered_proxies if self._matches_filter(p, selected, context)
                ]

            if not filtered_proxies:
                raise ProxyPoolEmptyError("All proxies filtered out")

        # Apply selector to filtered pool
        final_pool = pool.__class__(name=f"{pool.name}-final")
        for proxy in filtered_proxies:
            final_pool.add_proxy(proxy)

        return self.selector.select(final_pool, context)

    def _matches_filter(
        self,
        proxy: Proxy,
        filter_result: Proxy,
        context: SelectionContext | None = None,
    ) -> bool:
        """
        Check if proxy matches filter criteria based on filter result.

        For now, we use a simple heuristic: if the filter strategy selected a proxy,
        we check if it shares key attributes (country, region) with other proxies.

        Args:
            proxy: Proxy to check
            filter_result: Proxy returned by filter strategy

        Returns:
            True if proxy matches filter criteria
        """
        # If same proxy, definitely matches
        if proxy.id == filter_result.id:
            return True

        target_country = context.target_country if context else None
        target_region = context.target_region if context else None

        if target_country:
            return (
                proxy.country_code is not None
                and proxy.country_code.upper() == target_country.upper()
            )

        if target_region:
            return proxy.region is not None and proxy.region.upper() == target_region.upper()

        # Check geo-location match from the selected filter result.
        if hasattr(filter_result, "country_code") and filter_result.country_code:
            proxy_country = getattr(proxy, "country_code", None)
            return proxy_country is not None and proxy_country.upper() == (
                filter_result.country_code.upper()
            )

        if hasattr(filter_result, "region") and filter_result.region:
            proxy_region = getattr(proxy, "region", None)
            return proxy_region is not None and proxy_region.upper() == filter_result.region.upper()

        # If no specific criteria, include all
        return True

    @staticmethod
    def _detached_candidate(proxy: Proxy) -> Proxy:
        """Clone a filter candidate with fresh private locks and isolated counters."""
        return Proxy.model_validate(proxy.model_dump(mode="python"))

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        """
        Record result by delegating to selector strategy.

        Args:
            proxy: The proxy that handled the request
            success: Whether the request succeeded
            response_time_ms: Response time in milliseconds
        """
        # Delegate to selector for result recording
        self.selector.record_result(proxy, success, response_time_ms)

    def configure(self, config: StrategyConfig) -> None:
        """
        Configure all component strategies.

        Args:
            config: Strategy configuration to apply
        """
        for filter_strategy in self.filters:
            if hasattr(filter_strategy, "configure"):
                filter_strategy.configure(config)

        if hasattr(self.selector, "configure"):
            self.selector.configure(config)

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> CompositeStrategy:
        """
        Create CompositeStrategy from configuration dictionary.

        Args:
            config: Configuration dict with keys:
                - filters: List of filter strategy names or instances
                - selector: Selector strategy name or instance

        Returns:
            Configured CompositeStrategy instance

        Example:
            >>> config = {
            ...     "filters": ["geo-targeted"],
            ...     "selector": "performance-based"
            ... }
            >>> strategy = CompositeStrategy.from_config(config)

        Raises:
            ValueError: If config is invalid
        """
        filters_config = config.get("filters", [])
        selector_config = config.get("selector", "round-robin")

        # Convert filter names to instances
        filters = []
        for f in filters_config:
            if isinstance(f, str):
                # Will be implemented with StrategyRegistry in T070
                filters.append(cls._strategy_from_name(f))
            else:
                filters.append(f)

        # Convert selector name to instance
        if isinstance(selector_config, str):
            selector = cls._strategy_from_name(selector_config)
        else:
            selector = selector_config

        return cls(filters=filters, selector=selector)

    @staticmethod
    def _strategy_from_name(name: str) -> RotationStrategy:
        """
        Convert strategy name to strategy instance.

        Args:
            name: Strategy name (e.g., "round-robin", "performance-based")

        Returns:
            Strategy instance

        Raises:
            ValueError: If strategy name not recognized
        """
        return resolve_builtin_strategy(name)
