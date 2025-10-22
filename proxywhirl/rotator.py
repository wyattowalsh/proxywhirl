"""
Main proxy rotation implementation.
"""

from typing import Any, Optional, Union

import httpx
from loguru import logger
from tenacity import (
    retry,
    retry_if_not_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from proxywhirl.exceptions import (
    ProxyAuthenticationError,
    ProxyConnectionError,
    ProxyPoolEmptyError,
)
from proxywhirl.models import Proxy, ProxyConfiguration, ProxyPool
from proxywhirl.strategies import (
    LeastUsedStrategy,
    RandomStrategy,
    RotationStrategy,
    RoundRobinStrategy,
    WeightedStrategy,
)


class ProxyRotator:
    """
    Main class for proxy rotation with automatic failover.

    Provides HTTP methods (GET, POST, PUT, DELETE, PATCH) that automatically
    rotate through a pool of proxies, with intelligent failover on connection errors.

    Example:
        ```python
        from proxywhirl import ProxyRotator, Proxy

        rotator = ProxyRotator()
        rotator.add_proxy("http://proxy1.example.com:8080")
        rotator.add_proxy("http://proxy2.example.com:8080")

        response = rotator.get("https://httpbin.org/ip")
        print(response.json())
        ```
    """

    def __init__(
        self,
        proxies: Optional[list[Proxy]] = None,
        strategy: Union[RotationStrategy, str, None] = None,
        config: Optional[ProxyConfiguration] = None,
    ) -> None:
        """
        Initialize ProxyRotator.

        Args:
            proxies: Initial list of proxies (optional)
            strategy: Rotation strategy instance or strategy name string
                     ("round-robin", "random", "weighted", "least-used")
                     Default: RoundRobinStrategy
            config: Configuration settings (default: ProxyConfiguration())
        """
        self.pool = ProxyPool(name="default", proxies=proxies or [])

        # Parse strategy string or use provided instance
        if strategy is None:
            self.strategy: RotationStrategy = RoundRobinStrategy()
        elif isinstance(strategy, str):
            strategy_map = {
                "round-robin": RoundRobinStrategy,
                "random": RandomStrategy,
                "weighted": WeightedStrategy,
                "least-used": LeastUsedStrategy,
            }
            strategy_lower = strategy.lower()
            if strategy_lower not in strategy_map:
                raise ValueError(
                    f"Unknown strategy: {strategy}. Valid options: {', '.join(strategy_map.keys())}"
                )
            self.strategy = strategy_map[strategy_lower]()  # type: ignore[assignment]
        else:
            self.strategy = strategy

        self.config = config or ProxyConfiguration()
        self._client: Optional[httpx.Client] = None

        # Configure logging
        if hasattr(logger, "_core") and not logger._core.handlers:
            from proxywhirl.utils import configure_logging

            configure_logging(
                level=self.config.log_level,
                format_type=self.config.log_format,
                redact_credentials=self.config.log_redact_credentials,
            )

    def __enter__(self) -> "ProxyRotator":
        """Enter context manager."""
        self._client = httpx.Client(
            timeout=self.config.timeout,
            verify=self.config.verify_ssl,
            follow_redirects=self.config.follow_redirects,
            limits=httpx.Limits(
                max_connections=self.config.pool_connections,
                max_keepalive_connections=self.config.pool_max_keepalive,
            ),
        )
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager."""
        if self._client:
            self._client.close()
            self._client = None

    def add_proxy(self, proxy: Union[Proxy, str]) -> None:
        """
        Add a proxy to the pool.

        Args:
            proxy: Proxy instance or URL string
        """
        if isinstance(proxy, str):
            from proxywhirl.utils import create_proxy_from_url

            proxy = create_proxy_from_url(proxy)

        self.pool.add_proxy(proxy)
        logger.info(f"Added proxy to pool: {proxy.url}", proxy_id=str(proxy.id))

    def remove_proxy(self, proxy_id: str) -> None:
        """
        Remove a proxy from the pool.

        Args:
            proxy_id: UUID of proxy to remove
        """
        from uuid import UUID

        self.pool.remove_proxy(UUID(proxy_id))
        logger.info(f"Removed proxy from pool: {proxy_id}")

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

        healthy_count = sum(
            1
            for p in self.pool.proxies
            if p.health_status
            in (HealthStatus.HEALTHY, HealthStatus.UNKNOWN, HealthStatus.DEGRADED)
        )
        unhealthy_count = sum(
            1 for p in self.pool.proxies if p.health_status == HealthStatus.UNHEALTHY
        )
        dead_count = sum(1 for p in self.pool.proxies if p.health_status == HealthStatus.DEAD)

        total_requests = sum(p.total_requests for p in self.pool.proxies)
        total_successes = sum(p.total_successes for p in self.pool.proxies)
        total_failures = sum(p.total_failures for p in self.pool.proxies)

        # Calculate average success rate
        success_rates = [p.success_rate for p in self.pool.proxies if p.total_requests > 0]
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

    def clear_unhealthy_proxies(self) -> int:
        """
        Remove all unhealthy and dead proxies from the pool.

        Returns:
            Number of proxies removed
        """
        removed_count = self.pool.clear_unhealthy()

        logger.info(
            "Cleared unhealthy proxies from pool",
            removed_count=removed_count,
            remaining_proxies=self.pool.size,
        )

        return removed_count

    def _get_proxy_dict(self, proxy: Proxy) -> dict[str, str]:
        """
        Convert proxy to httpx proxy dict format.

        Args:
            proxy: Proxy to convert

        Returns:
            Dictionary with proxy URL for httpx
        """
        url = str(proxy.url)

        # Add credentials to URL if present
        if proxy.username and proxy.password:
            username = proxy.username.get_secret_value()
            password = proxy.password.get_secret_value()

            # Insert credentials into URL
            if "://" in url:
                protocol, rest = url.split("://", 1)
                url = f"{protocol}://{username}:{password}@{rest}"

        # Return proxy dict for all protocols
        return {
            "http://": url,
            "https://": url,
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_not_exception_type((ProxyAuthenticationError, ProxyPoolEmptyError)),
        reraise=True,
    )
    def _make_request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Make HTTP request with automatic proxy rotation and failover.

        Args:
            method: HTTP method
            url: URL to request
            **kwargs: Additional request parameters

        Returns:
            HTTP response

        Raises:
            ProxyPoolEmptyError: If no healthy proxies available
            ProxyConnectionError: If all retry attempts fail
        """
        import time

        # Select proxy
        try:
            proxy = self.strategy.select(self.pool)
        except ProxyPoolEmptyError as e:
            logger.error("No healthy proxies available")
            raise e

        proxy_dict = self._get_proxy_dict(proxy)

        logger.info(
            f"Making {method} request to {url}",
            proxy_id=str(proxy.id),
            proxy_url=str(proxy.url),
        )

        start_time = time.time()

        try:
            # Create temporary client with proxy if none exists
            if self._client is None:
                with httpx.Client(
                    proxy=proxy_dict.get("http://"),  # httpx uses proxy, not proxies
                    timeout=self.config.timeout,
                    verify=self.config.verify_ssl,
                    follow_redirects=self.config.follow_redirects,
                ) as client:
                    response = client.request(method, url, **kwargs)
            else:
                # Create a new request with proxy for existing client
                # httpx doesn't allow changing proxies on existing client
                with httpx.Client(
                    proxy=proxy_dict.get("http://"),
                    timeout=self.config.timeout,
                    verify=self.config.verify_ssl,
                    follow_redirects=self.config.follow_redirects,
                ) as client:
                    response = client.request(method, url, **kwargs)

            # Record success
            response_time_ms = (time.time() - start_time) * 1000
            self.strategy.record_result(proxy, success=True, response_time_ms=response_time_ms)

            # Check for 407 Proxy Authentication Required
            if response.status_code == 407:
                logger.error(
                    f"Proxy authentication failed: {proxy.url}",
                    proxy_id=str(proxy.id),
                    status_code=407,
                )
                raise ProxyAuthenticationError(
                    f"Proxy authentication required (407) for {proxy.url}. "
                    "Please provide valid credentials (username and password)."
                )

            logger.info(
                f"Request successful: {method} {url}",
                proxy_id=str(proxy.id),
                status_code=response.status_code,
                response_time_ms=response_time_ms,
            )

            return response

        except ProxyAuthenticationError:
            # Re-raise auth errors without wrapping
            raise
        except Exception as e:
            # Record failure
            response_time_ms = (time.time() - start_time) * 1000
            self.strategy.record_result(proxy, success=False, response_time_ms=response_time_ms)

            logger.warning(
                f"Request failed: {method} {url}",
                proxy_id=str(proxy.id),
                error=str(e),
            )

            raise ProxyConnectionError(f"Request failed: {e}") from e

    def get(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make GET request."""
        return self._make_request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make POST request."""
        return self._make_request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make PUT request."""
        return self._make_request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make DELETE request."""
        return self._make_request("DELETE", url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make PATCH request."""
        return self._make_request("PATCH", url, **kwargs)

    def head(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make HEAD request."""
        return self._make_request("HEAD", url, **kwargs)

    def options(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make OPTIONS request."""
        return self._make_request("OPTIONS", url, **kwargs)
