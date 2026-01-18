"""
Shared base class for ProxyRotator and AsyncProxyRotator.

This module provides common functionality between sync and async rotators,
reducing code duplication and ensuring consistent behavior.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from loguru import logger

from proxywhirl.circuit_breaker import CircuitBreaker
from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import Proxy, ProxyPool
from proxywhirl.retry import RetryMetrics, RetryPolicy
from proxywhirl.strategies import RotationStrategy
from proxywhirl.utils import mask_proxy_url


class ProxyRotatorBase:
    """
    Shared logic for sync and async proxy rotators.

    This base class provides common functionality for both ProxyRotator
    and AsyncProxyRotator, including:
    - Proxy dictionary conversion (credentials handling)
    - Circuit breaker state checking
    - Proxy selection with circuit breaker filtering
    - Common attribute initialization

    Attributes:
        pool: Proxy pool instance
        strategy: Rotation strategy instance
        config: Configuration settings
        circuit_breakers: Circuit breaker instances per proxy
        retry_policy: Retry policy configuration
        retry_metrics: Retry metrics tracking
    """

    def _init_common(
        self,
        pool: ProxyPool,
        strategy: RotationStrategy,
        config: Any,
        retry_policy: RetryPolicy,
    ) -> None:
        """
        Initialize common rotator attributes.

        This method should be called from __init__ of subclasses to set up
        shared state.

        Args:
            pool: Proxy pool instance
            strategy: Rotation strategy instance
            config: Configuration settings
            retry_policy: Retry policy configuration
        """
        self.pool = pool
        self.strategy = strategy
        self.config = config
        self.retry_policy = retry_policy
        self.circuit_breakers: dict[str, CircuitBreaker] = {}
        self.retry_metrics = RetryMetrics()

    def _get_proxy_dict(self, proxy: Proxy) -> dict[str, str]:
        """
        Convert proxy to httpx proxy dict format.

        This method handles credential injection into the proxy URL
        if username and password are present. The resulting dictionary
        is compatible with httpx's proxy parameter format.

        Args:
            proxy: Proxy to convert

        Returns:
            Dictionary with proxy URL for httpx (keys: "http://", "https://")

        Example:
            >>> proxy = Proxy(url="http://proxy.example.com:8080")
            >>> rotator._get_proxy_dict(proxy)
            {'http://': 'http://proxy.example.com:8080', 'https://': 'http://proxy.example.com:8080'}
        """
        url = str(proxy.url)

        # Add credentials to URL if present
        if proxy.username and proxy.password:
            username = proxy.username.get_secret_value()
            password = proxy.password.get_secret_value()

            # URL-encode credentials to handle special characters like @, :, /, etc.
            # Using safe='' ensures all special characters are encoded
            username_encoded = quote(username, safe="")
            password_encoded = quote(password, safe="")

            # Insert URL-encoded credentials into URL
            if "://" in url:
                protocol, rest = url.split("://", 1)
                url = f"{protocol}://{username_encoded}:{password_encoded}@{rest}"

        # Return proxy dict for all protocols
        return {
            "http://": url,
            "https://": url,
        }

    def _should_use_circuit_breaker(self, proxy: Proxy) -> bool:
        """
        Check if request should proceed based on circuit breaker state.

        This method checks whether a proxy's circuit breaker allows
        requests to proceed. Returns False if the circuit breaker is open.

        Args:
            proxy: Proxy to check

        Returns:
            True if circuit breaker allows request, False otherwise

        Note:
            This method assumes circuit breaker exists for the proxy.
            Callers should handle missing circuit breakers appropriately.
        """
        circuit_breaker = self.circuit_breakers.get(str(proxy.id))
        if circuit_breaker:
            return circuit_breaker.should_attempt_request()
        # If no circuit breaker exists, allow the request
        return True

    def _select_proxy_with_circuit_breaker(self) -> Proxy:
        """
        Select a proxy while respecting circuit breaker states.

        This method filters the proxy pool to only include proxies
        whose circuit breakers are not open, then uses the rotation
        strategy to select from the available proxies.

        Returns:
            Selected proxy

        Raises:
            ProxyPoolEmptyError: If no healthy proxies available or all circuit breakers open

        Note:
            The method takes a snapshot of proxies to avoid race conditions
            during iteration in multi-threaded/async environments.
        """
        # Take a snapshot to avoid race conditions during iteration
        # For sync rotator, use get_all_proxies(); for async, use proxies directly
        if hasattr(self.pool, "get_all_proxies"):
            proxies_snapshot = self.pool.get_all_proxies()
        else:
            proxies_snapshot = list(self.pool.proxies)

        # Filter proxies by circuit breaker state and expiration
        available_proxies = []
        expired_count = 0
        for proxy in proxies_snapshot:
            # Skip expired proxies
            if proxy.is_expired:
                expired_count += 1
                continue

            circuit_breaker = self.circuit_breakers.get(str(proxy.id))
            if circuit_breaker and circuit_breaker.should_attempt_request():
                available_proxies.append(proxy)

        if expired_count > 0:
            logger.debug(f"Skipped {expired_count} expired proxies during selection")

        if not available_proxies:
            logger.error("All circuit breakers are open or proxies expired - no proxies available")
            raise ProxyPoolEmptyError(
                "503 Service Temporarily Unavailable - All proxies are currently failing or expired. "
                "Please wait for circuit breakers to recover or add new proxies."
            )

        # Create temporary pool with available proxies
        temp_pool = ProxyPool(name="temp", proxies=available_proxies)

        # Select from available proxies using strategy
        return self.strategy.select(temp_pool)

    def _init_circuit_breakers_for_proxies(self, proxies: list[Proxy]) -> None:
        """
        Initialize circuit breakers for a list of proxies.

        All circuit breakers start in CLOSED state per FR-021.

        Args:
            proxies: List of proxies to initialize circuit breakers for
        """
        for proxy in proxies:
            self.circuit_breakers[str(proxy.id)] = CircuitBreaker(proxy_id=str(proxy.id))

    def _add_proxy_common(self, proxy: Proxy) -> None:
        """
        Common logic for adding a proxy to the pool.

        This method:
        1. Adds proxy to the pool
        2. Initializes circuit breaker (starts CLOSED per FR-021)
        3. Logs the addition (with masked credentials)

        Args:
            proxy: Proxy instance to add

        Note:
            Subclasses should call this method from their add_proxy implementation.
        """
        self.pool.add_proxy(proxy)

        # Initialize circuit breaker for new proxy (starts CLOSED per FR-021)
        self.circuit_breakers[str(proxy.id)] = CircuitBreaker(proxy_id=str(proxy.id))

        # Mask credentials in log output
        masked_url = mask_proxy_url(proxy.url)
        logger.info(f"Added proxy to pool: {masked_url}", proxy_id=str(proxy.id))

    def _remove_proxy_common(self, proxy_id: str) -> None:
        """
        Common logic for removing a proxy from the pool.

        This method:
        1. Removes circuit breaker to prevent memory leak
        2. Logs the removal

        Note:
            Subclasses must handle pool removal and client cleanup separately.

        Args:
            proxy_id: UUID of proxy to remove
        """
        # Clean up circuit breaker to prevent memory leak
        if proxy_id in self.circuit_breakers:
            del self.circuit_breakers[proxy_id]
            logger.debug(f"Removed circuit breaker for proxy: {proxy_id}")

    def get_circuit_breaker_states(self) -> dict[str, CircuitBreaker]:
        """
        Get circuit breaker states for all proxies.

        Returns:
            Dictionary mapping proxy IDs to their circuit breaker instances

        Note:
            Returns a copy to prevent external modification.
        """
        return self.circuit_breakers.copy()

    def reset_circuit_breaker(self, proxy_id: str) -> None:
        """
        Manually reset a circuit breaker to CLOSED state.

        Args:
            proxy_id: ID of the proxy whose circuit breaker to reset

        Raises:
            KeyError: If proxy_id not found
        """
        if proxy_id not in self.circuit_breakers:
            raise KeyError(f"No circuit breaker found for proxy {proxy_id}")

        self.circuit_breakers[proxy_id].reset()
        logger.info(f"Circuit breaker manually reset for proxy {proxy_id}")

    def get_retry_metrics(self) -> RetryMetrics:
        """
        Get retry metrics.

        Returns:
            RetryMetrics instance with current metrics
        """
        return self.retry_metrics

    def get_pool_stats(self) -> dict[str, Any]:
        """
        Get statistics about the proxy pool.

        Returns:
            Dictionary containing pool statistics:
            - total_proxies: Total number of proxies
            - healthy_proxies: Number of healthy/unknown proxies
            - unhealthy_proxies: Number of unhealthy proxies
            - dead_proxies: Number of dead proxies
            - total_requests: Total requests across all proxies
            - total_successes: Total successful requests
            - total_failures: Total failed requests
            - average_success_rate: Average success rate across all proxies
        """
        from proxywhirl.models import HealthStatus

        # Take a snapshot to avoid race conditions during iteration
        if hasattr(self.pool, "get_all_proxies"):
            proxies_snapshot = self.pool.get_all_proxies()
        else:
            proxies_snapshot = list(self.pool.proxies)

        healthy_count = sum(
            1
            for p in proxies_snapshot
            if p.health_status
            in (HealthStatus.HEALTHY, HealthStatus.UNKNOWN, HealthStatus.DEGRADED)
        )
        unhealthy_count = sum(
            1 for p in proxies_snapshot if p.health_status == HealthStatus.UNHEALTHY
        )
        dead_count = sum(1 for p in proxies_snapshot if p.health_status == HealthStatus.DEAD)

        total_requests = sum(p.total_requests for p in proxies_snapshot)
        total_successes = sum(p.total_successes for p in proxies_snapshot)
        total_failures = sum(p.total_failures for p in proxies_snapshot)

        # Calculate average success rate
        success_rates = [p.success_rate for p in proxies_snapshot if p.total_requests > 0]
        avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0.0

        return {
            "total_proxies": self.pool.size,
            "healthy_proxies": healthy_count,
            "unhealthy_proxies": unhealthy_count,
            "dead_proxies": dead_count,
            "total_requests": total_requests,
            "total_successes": total_successes,
            "total_failures": total_failures,
            "average_success_rate": avg_success_rate,
        }

    def get_statistics(self) -> dict[str, Any]:
        """
        Get comprehensive statistics including source breakdown (FR-050).

        Returns:
            Dictionary containing:
            - All stats from get_pool_stats()
            - source_breakdown: Count of proxies by source (USER, FETCHED, etc.)
        """
        stats = self.get_pool_stats()
        stats["source_breakdown"] = self.pool.get_source_breakdown()
        return stats
