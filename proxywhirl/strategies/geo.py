"""Geo-targeted rotation strategy."""

from __future__ import annotations

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import (
    Proxy,
    ProxyPool,
    SelectionContext,
    StrategyConfig,
)
from proxywhirl.strategies.base import RotationStrategy
from proxywhirl.strategies.least_used import LeastUsedStrategy
from proxywhirl.strategies.random import RandomStrategy
from proxywhirl.strategies.round_robin import RoundRobinStrategy


class GeoTargetedStrategy:
    """
    Geo-targeted proxy selection strategy.

    Filters proxies based on geographical location (country or region) specified
    in the SelectionContext. Supports fallback to any proxy when no matches found.

    Features:
    - Country-based filtering (ISO 3166-1 alpha-2 codes)
    - Region-based filtering (custom region names)
    - Country takes precedence over region when both specified
    - Configurable fallback behavior
    - Secondary strategy for selection from filtered proxies

    Thread Safety:
        Stateless per-request operations, thread-safe.

    Success Criteria:
        SC-006: 100% correct region selection when available

    Performance:
        O(n) filtering + O(1) or O(n) secondary selection
    """

    def __init__(self) -> None:
        """Initialize geo-targeted strategy."""
        self._fallback_enabled: bool = True
        self._secondary_strategy: RotationStrategy = RoundRobinStrategy()
        self.config: StrategyConfig | None = None

    def configure(self, config: StrategyConfig) -> None:
        """
        Configure geo-targeting parameters.

        Args:
            config: Strategy configuration with geo settings
        """
        # Store config for later use
        self.config = config

        if config.geo_fallback_enabled is not None:
            self._fallback_enabled = config.geo_fallback_enabled

        # Configure secondary strategy based on name
        if config.geo_secondary_strategy:
            strategy_name = config.geo_secondary_strategy.lower()
            if strategy_name == "round_robin":
                self._secondary_strategy = RoundRobinStrategy()
            elif strategy_name == "random":
                self._secondary_strategy = RandomStrategy()
            elif strategy_name == "least_used":
                self._secondary_strategy = LeastUsedStrategy()
            # Default to round_robin if unknown

    def validate_metadata(self, pool: ProxyPool) -> bool:
        """
        Validate that pool has geo metadata.

        Geo-targeting is optional, so always returns True.
        Proxies without geo data will simply not match geo filters.

        Args:
            pool: The proxy pool to validate

        Returns:
            Always True - geo data is optional
        """
        return True

    def select(self, pool: ProxyPool, context: SelectionContext | None = None) -> Proxy:
        """
        Select a proxy based on geographical targeting.

        Selection logic:
        1. If context has target_country: filter by country (exact match)
        2. Else if context has target_region: filter by region (exact match)
        3. If no target specified: use all healthy proxies
        4. Apply context.failed_proxy_ids filtering
        5. If filtered list empty and fallback enabled: use all healthy proxies
        6. If filtered list empty and fallback disabled: raise error
        7. Apply secondary strategy to filtered proxies

        Args:
            pool: The proxy pool to select from
            context: Selection context with target_country or target_region

        Returns:
            Proxy matching geo criteria (or any proxy if fallback enabled)

        Raises:
            ProxyPoolEmptyError: If no proxies match criteria and fallback disabled
        """
        # Start with all healthy proxies
        healthy_proxies = pool.get_healthy_proxies()

        if not healthy_proxies:
            raise ProxyPoolEmptyError("No healthy proxies available")

        # Determine target location from context
        target_country = context.target_country if context else None
        target_region = context.target_region if context else None

        # Filter by geography
        if target_country:
            # Country takes precedence - exact match
            filtered_proxies = [
                p
                for p in healthy_proxies
                if p.country_code and p.country_code.upper() == target_country.upper()
            ]
            target_location = target_country
        elif target_region:
            # Region filtering - exact match
            filtered_proxies = [
                p for p in healthy_proxies if p.region and p.region.upper() == target_region.upper()
            ]
            target_location = target_region
        else:
            # No geo targeting - use all healthy proxies
            filtered_proxies = healthy_proxies
            target_location = None

        # Filter out previously failed proxies from context
        if context and context.failed_proxy_ids:
            failed_ids = set(context.failed_proxy_ids)
            filtered_proxies = [p for p in filtered_proxies if str(p.id) not in failed_ids]

        # Handle empty filtered list
        if not filtered_proxies:
            if self._fallback_enabled:
                # Fallback to any healthy proxy (excluding failed)
                if context and context.failed_proxy_ids:
                    failed_ids = set(context.failed_proxy_ids)
                    filtered_proxies = [p for p in healthy_proxies if str(p.id) not in failed_ids]
                else:
                    filtered_proxies = healthy_proxies

                if not filtered_proxies:
                    raise ProxyPoolEmptyError("No healthy proxies available after filtering")
            else:
                # No fallback - raise error with clear message
                location_str = (
                    f"country={target_location}" if target_country else f"region={target_location}"
                )
                raise ProxyPoolEmptyError(
                    f"No proxies available for target location: {location_str}"
                )

        # Create temp pool and apply secondary strategy
        temp_pool = ProxyPool(name="geo_filtered", proxies=filtered_proxies)
        selected_proxy = self._secondary_strategy.select(temp_pool)

        return selected_proxy

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        """
        Record the result of a request through a proxy.

        Updates proxy completion statistics via Proxy.complete_request().

        Args:
            proxy: The proxy that handled the request
            success: Whether the request succeeded
            response_time_ms: Response time in milliseconds
        """
        # Pass strategy's alpha to avoid mutating proxy state
        alpha = self.config.ema_alpha if self.config is not None else None
        proxy.complete_request(success=success, response_time_ms=response_time_ms, alpha=alpha)
