"""Cost-aware rotation strategy."""

from __future__ import annotations

import random

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import (
    Proxy,
    ProxyPool,
    SelectionContext,
    StrategyConfig,
)


class CostAwareStrategy:
    """
    Cost-aware proxy selection strategy.

    Prioritizes free proxies over paid ones, with configurable cost thresholds.
    Uses weighted random selection based on inverse cost - lower cost proxies
    are more likely to be selected.

    Features:
    - Free proxies (cost_per_request = 0.0) are heavily favored
    - Paid proxies are selected based on inverse cost weighting
    - Configurable cost threshold to filter out expensive proxies
    - Supports fallback to any proxy when no low-cost options available

    Thread Safety:
        Uses Python's random.choices() which is thread-safe via GIL.

    Example:
        >>> from proxywhirl.strategies import CostAwareStrategy
        >>> strategy = CostAwareStrategy()
        >>> config = StrategyConfig(metadata={"max_cost_per_request": 0.5})
        >>> strategy.configure(config)
        >>> proxy = strategy.select(pool)  # Selects cheapest available proxy
    """

    def __init__(self, max_cost_per_request: float | None = None) -> None:
        """Initialize cost-aware strategy.

        Args:
            max_cost_per_request: Maximum acceptable cost per request.
                Proxies exceeding this cost will be filtered out.
                None means no cost limit (default).
        """
        self.config: StrategyConfig | None = None
        self.max_cost_per_request = max_cost_per_request
        self._free_proxy_boost: float = 10.0  # Weight multiplier for free proxies

    def configure(self, config: StrategyConfig) -> None:
        """Configure cost-aware parameters.

        Args:
            config: Strategy configuration with optional metadata:
                - max_cost_per_request: Maximum cost threshold
                - free_proxy_boost: Weight multiplier for free proxies (default: 10.0)
        """
        self.config = config

        # Extract max cost from metadata if present
        if config.metadata and "max_cost_per_request" in config.metadata:
            self.max_cost_per_request = float(config.metadata["max_cost_per_request"])

        # Extract free proxy boost from metadata if present
        if config.metadata and "free_proxy_boost" in config.metadata:
            self._free_proxy_boost = float(config.metadata["free_proxy_boost"])

    def validate_metadata(self, pool: ProxyPool) -> bool:
        """Validate that pool has cost metadata.

        Cost field is optional, so always returns True.
        Proxies without cost data are treated as free (cost = 0.0).

        Args:
            pool: The proxy pool to validate

        Returns:
            Always True - cost data is optional
        """
        return True

    def select(self, pool: ProxyPool, context: SelectionContext | None = None) -> Proxy:
        """Select a proxy based on cost optimization.

        Selection logic:
        1. Get healthy proxies
        2. Filter by context.failed_proxy_ids if present
        3. Filter by max_cost_per_request threshold if configured
        4. Apply inverse cost weighting (lower cost = higher weight)
        5. Free proxies get boost multiplier (default 10x weight)
        6. Use weighted random selection

        Args:
            pool: The proxy pool to select from
            context: Optional selection context for filtering

        Returns:
            Cost-optimized proxy selection

        Raises:
            ProxyPoolEmptyError: If no proxies meet criteria
        """
        healthy_proxies = pool.get_healthy_proxies()

        if not healthy_proxies:
            raise ProxyPoolEmptyError("No healthy proxies available")

        # Filter by context failed proxies
        if context and context.failed_proxy_ids:
            failed_ids = set(context.failed_proxy_ids)
            healthy_proxies = [p for p in healthy_proxies if str(p.id) not in failed_ids]

            if not healthy_proxies:
                raise ProxyPoolEmptyError(
                    "No healthy proxies available after filtering failed proxies"
                )

        # Filter by cost threshold if configured
        if self.max_cost_per_request is not None:
            cost_filtered = [
                p
                for p in healthy_proxies
                if (p.cost_per_request or 0.0) <= self.max_cost_per_request
            ]

            # If filtering eliminates all proxies, raise error
            if not cost_filtered:
                raise ProxyPoolEmptyError(
                    f"No proxies available with cost <= {self.max_cost_per_request}"
                )

            healthy_proxies = cost_filtered

        # Calculate inverse cost weights
        weights = []
        for proxy in healthy_proxies:
            cost = proxy.cost_per_request or 0.0

            # Free proxy gets boost, paid proxy gets inverse cost weight
            weight = self._free_proxy_boost if cost == 0.0 else 1.0 / (cost + 0.001)

            weights.append(weight)

        # Normalize weights
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
        else:
            # Fallback to uniform weights (shouldn't happen with free proxy boost)
            weights = [1.0 / len(weights)] * len(weights)

        # Weighted non-cryptographic selection for proxy load balancing.
        selected = random.choices(  # nosec B311
            healthy_proxies, weights=weights, k=1
        )[0]

        # Mark proxy as in-use
        selected.start_request()

        return selected

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        """Record the result of using a proxy.

        Args:
            proxy: The proxy that was used
            success: Whether the request succeeded
            response_time_ms: Response time in milliseconds
        """
        # Pass strategy's alpha to avoid mutating proxy state
        alpha = self.config.ema_alpha if self.config is not None else None
        proxy.complete_request(success=success, response_time_ms=response_time_ms, alpha=alpha)
