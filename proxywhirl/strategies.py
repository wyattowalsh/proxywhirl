"""
Rotation strategies for proxy selection.
"""

import random
from typing import Protocol, runtime_checkable

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import Proxy, ProxyPool


@runtime_checkable
class RotationStrategy(Protocol):
    """Protocol defining interface for proxy rotation strategies."""

    def select(self, pool: ProxyPool) -> Proxy:
        """
        Select a proxy from the pool based on strategy logic.

        Args:
            pool: The proxy pool to select from

        Returns:
            Selected proxy

        Raises:
            ProxyPoolEmptyError: If no suitable proxy is available
        """
        ...

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        """
        Record the result of using a proxy.

        Args:
            proxy: The proxy that was used
            success: Whether the request succeeded
            response_time_ms: Response time in milliseconds
        """
        ...


class RoundRobinStrategy:
    """
    Round-robin proxy selection strategy.

    Selects proxies in sequential order, wrapping around to the first
    proxy after reaching the end of the list. Only selects healthy proxies.
    """

    def __init__(self) -> None:
        """Initialize round-robin strategy."""
        self._current_index: int = 0

    def select(self, pool: ProxyPool) -> Proxy:
        """
        Select next proxy in round-robin order.

        Args:
            pool: The proxy pool to select from

        Returns:
            Next healthy proxy in rotation

        Raises:
            ProxyPoolEmptyError: If no healthy proxies are available
        """
        healthy_proxies = pool.get_healthy_proxies()

        if not healthy_proxies:
            raise ProxyPoolEmptyError("No healthy proxies available in pool")

        # Select proxy at current index (with wraparound)
        proxy = healthy_proxies[self._current_index % len(healthy_proxies)]

        # Increment index for next selection
        self._current_index = (self._current_index + 1) % len(healthy_proxies)

        return proxy

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        """
        Record the result of using a proxy.

        Updates proxy statistics based on request outcome.

        Args:
            proxy: The proxy that was used
            success: Whether the request succeeded
            response_time_ms: Response time in milliseconds
        """
        if success:
            proxy.record_success(response_time_ms)
        else:
            proxy.record_failure()


class RandomStrategy:
    """
    Random proxy selection strategy.

    Randomly selects a proxy from the pool of healthy proxies.
    Provides unpredictable rotation for scenarios where sequential
    patterns should be avoided.
    """

    def select(self, pool: ProxyPool) -> Proxy:
        """
        Select a random healthy proxy.

        Args:
            pool: The proxy pool to select from

        Returns:
            Randomly selected healthy proxy

        Raises:
            ProxyPoolEmptyError: If no healthy proxies are available
        """
        healthy_proxies = pool.get_healthy_proxies()

        if not healthy_proxies:
            raise ProxyPoolEmptyError("No healthy proxies available in pool")

        return random.choice(healthy_proxies)

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        """Record the result of using a proxy."""
        if success:
            proxy.record_success(response_time_ms)
        else:
            proxy.record_failure()


class WeightedStrategy:
    """
    Weighted proxy selection strategy.

    Selects proxies based on their success rates, giving preference
    to proxies with higher success rates. Uses weighted random selection
    where weights are derived from success_rate.
    """

    def select(self, pool: ProxyPool) -> Proxy:
        """
        Select a proxy weighted by success rate.

        Args:
            pool: The proxy pool to select from

        Returns:
            Weighted-random selected healthy proxy

        Raises:
            ProxyPoolEmptyError: If no healthy proxies are available
        """
        healthy_proxies = pool.get_healthy_proxies()

        if not healthy_proxies:
            raise ProxyPoolEmptyError("No healthy proxies available in pool")

        # Calculate weights based on success rates
        # Add small base weight to give all proxies a chance
        weights = [max(proxy.success_rate, 0.1) for proxy in healthy_proxies]

        # Use random.choices for weighted selection
        selected = random.choices(healthy_proxies, weights=weights, k=1)[0]
        return selected

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        """Record the result of using a proxy."""
        if success:
            proxy.record_success(response_time_ms)
        else:
            proxy.record_failure()


class LeastUsedStrategy:
    """
    Least-used proxy selection strategy.

    Selects the proxy with the fewest total requests, helping to
    balance load across all available proxies. Useful for ensuring
    even distribution of traffic.
    """

    def select(self, pool: ProxyPool) -> Proxy:
        """
        Select the least-used healthy proxy.

        Args:
            pool: The proxy pool to select from

        Returns:
            Healthy proxy with fewest total requests

        Raises:
            ProxyPoolEmptyError: If no healthy proxies are available
        """
        healthy_proxies = pool.get_healthy_proxies()

        if not healthy_proxies:
            raise ProxyPoolEmptyError("No healthy proxies available in pool")

        # Select proxy with minimum total_requests
        return min(healthy_proxies, key=lambda p: p.total_requests)

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        """Record the result of using a proxy."""
        if success:
            proxy.record_success(response_time_ms)
        else:
            proxy.record_failure()
