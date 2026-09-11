"""Performance-based rotation strategy."""

from __future__ import annotations

import random

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import (
    Proxy,
    ProxyPool,
    SelectionContext,
    StrategyConfig,
)


class PerformanceBasedStrategy:
    """
    Performance-based proxy selection using EMA response times.

    Selects proxies using weighted random selection based on inverse EMA
    response times - faster proxies (lower EMA) get higher weights.
    This adaptively favors better-performing proxies while still giving
    all proxies a chance to be selected.

    Cold Start Handling:
    New proxies without performance data are given exploration trials
    (default: 3-5 trials) before being deprioritized. This ensures new
    proxies can build up performance data and prevents proxy starvation.

    Thread Safety: Uses Python's random.choices() which is thread-safe
    via GIL-protected random number generation. No additional locking required.
    """

    def __init__(self, exploration_count: int = 5) -> None:
        """Initialize performance-based strategy.

        Args:
            exploration_count: Minimum trials for new proxies before performance-based
                selection applies. Default is 5 trials. Set to 0 to disable exploration.
        """
        self.config: StrategyConfig | None = None
        self.exploration_count = exploration_count

    def select(self, pool: ProxyPool, context: SelectionContext | None = None) -> Proxy:
        """
        Select a proxy weighted by inverse EMA response time.

        Faster proxies (lower EMA) receive higher weights for selection.
        New proxies with insufficient trials (< exploration_count) are given
        priority to ensure they can build performance data.

        Args:
            pool: The proxy pool to select from
            context: Optional selection context for filtering

        Returns:
            Performance-weighted selected healthy proxy with EMA data

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

        # Separate proxies into exploration and exploitation groups
        exploration_proxies = []  # New proxies needing exploration trials
        exploitation_proxies = []  # Proxies with sufficient performance data

        for p in healthy_proxies:
            # Proxies with insufficient trials need exploration
            if p.total_requests < self.exploration_count:
                exploration_proxies.append(p)
            # Only include proxies with valid EMA data in exploitation
            elif p.ema_response_time_ms is not None and p.ema_response_time_ms > 0:
                exploitation_proxies.append(p)

        # Probabilistic exploration: cold proxies get extra chance without starving
        # established performers (RV-013 / L1-010).
        explore_probability = 0.5
        if self.config is not None:
            explore_probability = float(
                self.config.metadata.get("exploration_probability", explore_probability)
            )
        use_exploration = exploration_proxies and (
            not exploitation_proxies or random.random() < explore_probability  # nosec B311
        )
        if use_exploration:
            selected = random.choice(exploration_proxies)  # nosec B311
        elif exploitation_proxies:
            # Use performance-based selection for exploitation
            # Calculate inverse weights (lower EMA = higher weight)
            weights = [1.0 / p.ema_response_time_ms for p in exploitation_proxies]  # type: ignore[operator]
            selected = random.choices(  # nosec B311
                exploitation_proxies, weights=weights, k=1
            )[0]
        else:
            # No proxies with EMA data and no exploration candidates
            # This can happen if all proxies have been tried but none have EMA yet
            # (e.g., all requests failed). Fall back to random selection.
            selected = random.choice(  # nosec B311
                healthy_proxies
            )

        # Track request start
        selected.start_request()

        return selected

    def configure(self, config: StrategyConfig) -> None:
        """Configure the strategy with custom settings.

        Args:
            config: Strategy configuration with optional exploration_count
        """
        self.config = config
        # Allow configuration of exploration_count
        if config.exploration_count is not None:
            self.exploration_count = config.exploration_count

    def validate_metadata(self, pool: ProxyPool) -> bool:
        """
        Validate that pool is usable for performance-based selection.

        With exploration support, we only need at least one healthy proxy.
        Returns True if pool has healthy proxies (exploration will handle cold start).

        Returns:
            True if pool has at least one healthy proxy
        """
        healthy_proxies = pool.get_healthy_proxies()
        # With exploration, we can work with any healthy proxies
        # No longer require EMA data to be present
        return len(healthy_proxies) > 0

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        """
        Record the result of using a proxy.

        The EMA is updated using the strategy's configured alpha value,
        ensuring consistent metric calculations regardless of proxy state.

        Args:
            proxy: The proxy that was used
            success: Whether the request succeeded
            response_time_ms: Response time in milliseconds
        """
        # Pass strategy's alpha to avoid mutating proxy state
        alpha = self.config.ema_alpha if self.config is not None else None
        proxy.complete_request(success=success, response_time_ms=response_time_ms, alpha=alpha)
