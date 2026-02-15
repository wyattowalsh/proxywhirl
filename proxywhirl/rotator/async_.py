"""
Async proxy rotation implementation using httpx.AsyncClient.
"""

from __future__ import annotations

import asyncio
import threading
from collections import OrderedDict
from typing import Any
from urllib.parse import quote

import httpx
from loguru import logger

from proxywhirl.circuit_breaker import CircuitBreaker
from proxywhirl.exceptions import (
    ProxyAuthenticationError,
    ProxyConnectionError,
    ProxyPoolEmptyError,
)
from proxywhirl.models import Proxy, ProxyConfiguration, ProxyPool
from proxywhirl.retry import RetryExecutor, RetryMetrics, RetryPolicy
from proxywhirl.rotator._bootstrap import bootstrap_pool_if_empty_async
from proxywhirl.rotator.base import ProxyRotatorBase
from proxywhirl.strategies import (
    LeastUsedStrategy,
    RandomStrategy,
    RotationStrategy,
    RoundRobinStrategy,
    WeightedStrategy,
)


class LRUAsyncClientPool:
    """
    LRU cache for httpx.AsyncClient instances with automatic eviction.

    When the pool reaches maxsize, the least recently used client is
    closed and removed to prevent unbounded memory growth.

    Supports dictionary-like access for backward compatibility with tests.
    """

    def __init__(self, maxsize: int = 100) -> None:
        """
        Initialize LRU async client pool.

        Args:
            maxsize: Maximum number of clients to cache (default: 100)
        """
        self._clients: OrderedDict[str, httpx.AsyncClient] = OrderedDict()
        self._maxsize = maxsize
        self._lock = asyncio.Lock()

    async def get(self, proxy_id: str) -> httpx.AsyncClient | None:
        """
        Get a client from the pool, marking it as recently used.

        Args:
            proxy_id: Proxy ID to look up

        Returns:
            Client if found, None otherwise
        """
        async with self._lock:
            if proxy_id in self._clients:
                # Move to end (most recently used)
                self._clients.move_to_end(proxy_id)
                return self._clients[proxy_id]
            return None

    async def put(self, proxy_id: str, client: httpx.AsyncClient) -> None:
        """
        Add a client to the pool, evicting LRU client if at capacity.

        Args:
            proxy_id: Proxy ID to store under
            client: Client instance to store
        """
        async with self._lock:
            if proxy_id in self._clients:
                # Already exists, move to end
                self._clients.move_to_end(proxy_id)
            else:
                # Check if we need to evict
                if len(self._clients) >= self._maxsize:
                    # Evict least recently used (first item)
                    lru_proxy_id, lru_client = self._clients.popitem(last=False)
                    try:
                        await lru_client.aclose()
                        logger.debug(
                            "Evicted LRU async client from pool",
                            evicted_proxy_id=lru_proxy_id,
                            pool_size=len(self._clients),
                        )
                    except Exception as e:
                        logger.warning(
                            f"Error closing evicted async client for proxy {lru_proxy_id}: {e}"
                        )

                # Add new client
                self._clients[proxy_id] = client

    async def remove(self, proxy_id: str) -> None:
        """
        Remove and close a client from the pool.

        Args:
            proxy_id: Proxy ID to remove
        """
        async with self._lock:
            if proxy_id in self._clients:
                client = self._clients.pop(proxy_id)
                try:
                    await client.aclose()
                    logger.debug("Removed async client from pool", proxy_id=proxy_id)
                except Exception as e:
                    logger.warning(f"Error closing async client for proxy {proxy_id}: {e}")

    async def clear(self) -> None:
        """Close all clients and clear the pool."""
        async with self._lock:
            for proxy_id, client in self._clients.items():
                try:
                    await client.aclose()
                    logger.debug("Closed pooled async client", proxy_id=proxy_id)
                except Exception as e:
                    logger.warning(f"Error closing async client for proxy {proxy_id}: {e}")
            self._clients.clear()

    def __len__(self) -> int:
        """Return number of clients in pool."""
        return len(self._clients)

    def __contains__(self, proxy_id: str) -> bool:
        """Check if proxy_id is in pool (supports 'in' operator)."""
        return proxy_id in self._clients

    async def __getitem__(self, proxy_id: str) -> httpx.AsyncClient:
        """Get client by proxy_id (supports dict-like access for tests)."""
        async with self._lock:
            return self._clients[proxy_id]

    async def __setitem__(self, proxy_id: str, client: httpx.AsyncClient) -> None:
        """Set client for proxy_id (supports dict-like access for tests)."""
        await self.put(proxy_id, client)

    async def __delitem__(self, proxy_id: str) -> None:
        """Delete client for proxy_id (supports dict-like deletion)."""
        await self.remove(proxy_id)


class AsyncProxyWhirl(ProxyRotatorBase):
    """
    Async proxy rotator with automatic failover and intelligent rotation.

    Provides async HTTP methods (GET, POST, PUT, DELETE, PATCH) that automatically
    rotate through a pool of proxies, with intelligent failover on connection errors.

    Example:
        ```python
        from proxywhirl import AsyncProxyWhirl, Proxy

        async with AsyncProxyWhirl() as rotator:
            await rotator.add_proxy("http://proxy1.example.com:8080")
            await rotator.add_proxy("http://proxy2.example.com:8080")

            response = await rotator.get("https://httpbin.org/ip")
            print(response.json())
        ```
    """

    _BOOTSTRAP_EMPTY_MESSAGE = (
        "Lazy auto-fetch bootstrap yielded zero proxies from built-in public sources"
    )

    def __init__(
        self,
        proxies: list[Proxy] | None = None,
        strategy: RotationStrategy | str | None = None,
        config: ProxyConfiguration | None = None,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        """
        Initialize AsyncProxyWhirl.

        Args:
            proxies: Initial list of proxies (optional)
            strategy: Rotation strategy instance or strategy name string
                     ("round-robin", "random", "weighted", "least-used")
                     Default: RoundRobinStrategy
            config: Configuration settings (default: ProxyConfiguration())
            retry_policy: Retry policy configuration (default: RetryPolicy())
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
        self._client: httpx.AsyncClient | None = None
        self._client_pool = LRUAsyncClientPool(maxsize=100)  # LRU cache with max 100 clients
        self._bootstrap_lock = asyncio.Lock()
        self._bootstrap_attempted = False

        # Retry and circuit breaker components
        self.retry_policy = retry_policy or RetryPolicy()
        self.circuit_breakers: dict[str, CircuitBreaker] = {}
        self.retry_metrics = RetryMetrics()
        self.retry_executor = RetryExecutor(
            self.retry_policy, self.circuit_breakers, self.retry_metrics
        )

        # Initialize circuit breakers for existing proxies (all start CLOSED per FR-021)
        # Use thread-safe snapshot for initialization
        for proxy in self.pool.get_all_proxies():
            self.circuit_breakers[str(proxy.id)] = CircuitBreaker(proxy_id=str(proxy.id))

        # Note: Strategy swapping is atomic via Python's reference assignment semantics.
        # No explicit lock needed as self.strategy = new_strategy is a single atomic operation.

        # Start periodic metrics aggregation thread (every 5 minutes)
        self._stop_event = threading.Event()
        self._aggregation_thread = threading.Thread(
            target=self._aggregation_loop, daemon=True, name="proxywhirl-metrics-aggregation"
        )
        self._aggregation_thread.start()

        # Configure logging
        if hasattr(logger, "_core") and not logger._core.handlers:
            from proxywhirl.utils import configure_logging

            configure_logging(
                level=self.config.log_level,
                format_type=self.config.log_format,
                redact_credentials=self.config.log_redact_credentials,
            )

    async def __aenter__(self) -> AsyncProxyWhirl:
        """Enter async context manager."""
        self._client = httpx.AsyncClient(
            timeout=self.config.timeout,
            verify=self.config.verify_ssl,
            follow_redirects=self.config.follow_redirects,
            limits=httpx.Limits(
                max_connections=self.config.pool_connections,
                max_keepalive_connections=self.config.pool_max_keepalive,
            ),
        )
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context manager."""
        if self._client:
            await self._client.aclose()
            self._client = None

        # Close all pooled clients
        await self._close_all_clients()

        # Stop aggregation thread
        self._stop_event.set()
        if self._aggregation_thread and self._aggregation_thread.is_alive():
            self._aggregation_thread.join(timeout=5.0)

    def __del__(self) -> None:
        """
        Destructor to ensure cleanup when not used as context manager.

        This method provides a safety net for resource cleanup when the object
        is garbage collected without proper context manager usage. It ensures
        that the background aggregation thread is stopped to prevent resource leaks.

        Note:
            Using AsyncProxyWhirl as a context manager (async with) is strongly
            recommended for proper async cleanup of httpx clients.
        """
        if hasattr(self, "_stop_event"):
            self._stop_event.set()
        if hasattr(self, "_aggregation_thread") and self._aggregation_thread.is_alive():
            self._aggregation_thread.join(timeout=1.0)
            logger.debug(
                "AsyncProxyWhirl cleanup via __del__ - context manager usage recommended",
                thread_name=self._aggregation_thread.name,
            )

    async def _close_all_clients(self) -> None:
        """Close all pooled clients and clear the pool."""
        await self._client_pool.clear()

    async def add_proxy(self, proxy: Proxy | str) -> None:
        """
        Add a proxy to the pool.

        Args:
            proxy: Proxy instance or URL string
        """
        if isinstance(proxy, str):
            from proxywhirl.utils import create_proxy_from_url

            proxy = create_proxy_from_url(proxy)

        self.pool.add_proxy(proxy)

        # Initialize circuit breaker for new proxy (starts CLOSED per FR-021)
        self.circuit_breakers[str(proxy.id)] = CircuitBreaker(proxy_id=str(proxy.id))

        logger.info(f"Added proxy to pool: {proxy.url}", proxy_id=str(proxy.id))

    async def remove_proxy(self, proxy_id: str) -> None:
        """
        Remove a proxy from the pool.

        Args:
            proxy_id: UUID of proxy to remove
        """
        from uuid import UUID

        # Close and remove the client for this proxy if it exists
        await self._client_pool.remove(proxy_id)

        # Clean up circuit breaker to prevent memory leak
        if proxy_id in self.circuit_breakers:
            del self.circuit_breakers[proxy_id]
            logger.debug(f"Removed circuit breaker for proxy: {proxy_id}")

        self.pool.remove_proxy(UUID(proxy_id))
        logger.info(f"Removed proxy from pool: {proxy_id}")

    async def _bootstrap_pool_if_empty(
        self,
        *,
        validate: bool = True,
        timeout: int = 10,
        max_concurrent: int = 100,
        max_proxies: int | None = None,
    ) -> int:
        """Bootstrap pool from built-in sources when empty."""
        return await bootstrap_pool_if_empty_async(
            pool=self.pool,
            add_proxy=self.add_proxy,
            validate=validate,
            timeout=timeout,
            max_concurrent=max_concurrent,
            max_proxies=max_proxies,
        )

    async def _ensure_request_bootstrap(self) -> None:
        """Run one-time lazy bootstrap for async request path when pool starts empty."""
        if self.pool.size > 0:
            return

        async with self._bootstrap_lock:
            if self.pool.size > 0:
                return
            if self._bootstrap_attempted:
                raise ProxyPoolEmptyError(self._BOOTSTRAP_EMPTY_MESSAGE)

            self._bootstrap_attempted = True
            await self._bootstrap_pool_if_empty()

        if self.pool.size == 0:
            raise ProxyPoolEmptyError(self._BOOTSTRAP_EMPTY_MESSAGE)

    async def get_proxy(self) -> Proxy:
        """
        Get the next proxy from the pool using the rotation strategy.

        Returns:
            Next proxy to use

        Raises:
            ProxyPoolEmptyError: If no healthy proxies available
        """
        return self._select_proxy_with_circuit_breaker()

    def set_strategy(self, strategy: RotationStrategy | str, *, atomic: bool = True) -> None:
        """
        Hot-swap the rotation strategy without restarting.

        This method implements atomic strategy swapping to ensure:
        - New requests immediately use the new strategy
        - In-flight requests complete with their original strategy
        - No requests are dropped during the swap
        - Swap completes in <100ms (SC-009)

        Args:
            strategy: New strategy instance or strategy name string
                     ("round-robin", "random", "weighted", "least-used",
                      "performance-based", "session", "geo-targeted")
            atomic: If True (default), ensures atomic swap. If False, allows
                   immediate replacement (faster but may affect in-flight requests)

        Example:
            >>> async with AsyncProxyWhirl(strategy="round-robin") as rotator:
            ...     # ... after some requests ...
            ...     rotator.set_strategy("performance-based")  # Hot-swap
            ...     # New requests now use performance-based strategy

        Thread Safety:
            Thread-safe via atomic reference swap. Multiple threads can
            call this method safely without race conditions.

        Performance:
            Target: <100ms for hot-swap completion (SC-009)
            Typical: <10ms for strategy instance creation and assignment
        """
        import time

        start_time = time.perf_counter()

        # Parse strategy string or use provided instance
        if isinstance(strategy, str):
            from proxywhirl.strategies import (
                GeoTargetedStrategy,
                PerformanceBasedStrategy,
                SessionPersistenceStrategy,
            )

            strategy_map: dict[str, type[RotationStrategy]] = {
                "round-robin": RoundRobinStrategy,
                "random": RandomStrategy,
                "weighted": WeightedStrategy,
                "least-used": LeastUsedStrategy,
                "performance-based": PerformanceBasedStrategy,
                "session": SessionPersistenceStrategy,
                "geo-targeted": GeoTargetedStrategy,
            }
            strategy_lower = strategy.lower()
            if strategy_lower not in strategy_map:
                raise ValueError(
                    f"Unknown strategy: {strategy}. Valid options: {', '.join(strategy_map.keys())}"
                )

            # Instantiate strategy
            strategy_class = strategy_map[strategy_lower]
            new_strategy = strategy_class()
        else:
            new_strategy = strategy

        # Store old strategy for logging
        old_strategy_name = self.strategy.__class__.__name__
        new_strategy_name = new_strategy.__class__.__name__

        # Python's reference assignment is atomic at the bytecode level,
        # so no explicit locking is needed for thread-safe strategy swap.
        # The 'atomic' parameter is kept for API compatibility but is now a no-op.
        self.strategy = new_strategy

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            f"Strategy hot-swapped: {old_strategy_name} ? {new_strategy_name} "
            f"(completed in {elapsed_ms:.2f}ms)",
            old_strategy=old_strategy_name,
            new_strategy=new_strategy_name,
            swap_time_ms=elapsed_ms,
        )

        # Validate SC-009: <100ms hot-swap time
        if elapsed_ms >= 100.0:
            logger.warning(
                f"Hot-swap exceeded target time: {elapsed_ms:.2f}ms (target: <100ms)",
                swap_time_ms=elapsed_ms,
            )

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

        # Use thread-safe snapshot for all calculations
        proxies_snapshot = self.pool.get_all_proxies()

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

    async def clear_unhealthy_proxies(self) -> int:
        """
        Remove all unhealthy and dead proxies from the pool.

        Returns:
            Number of proxies removed
        """
        from proxywhirl.models import HealthStatus

        # Capture IDs of proxies to be removed before clearing (thread-safe snapshot)
        removed_proxy_ids = [
            str(p.id)
            for p in self.pool.get_all_proxies()
            if p.health_status in (HealthStatus.DEAD, HealthStatus.UNHEALTHY)
        ]

        removed_count = self.pool.clear_unhealthy()

        # Clean up circuit breakers and pooled clients for removed proxies to prevent memory leak
        for proxy_id in removed_proxy_ids:
            # Remove pooled client
            await self._client_pool.remove(proxy_id)

            # Remove circuit breaker
            if proxy_id in self.circuit_breakers:
                del self.circuit_breakers[proxy_id]
                logger.debug(f"Removed circuit breaker for unhealthy proxy: {proxy_id}")

        logger.info(
            "Cleared unhealthy proxies from pool",
            removed_count=removed_count,
            remaining_proxies=self.pool.size,
        )

        return removed_count

    async def _get_or_create_client(
        self, proxy: Proxy, proxy_dict: dict[str, str]
    ) -> httpx.AsyncClient:
        """
        Get or create a pooled httpx.AsyncClient for the given proxy.

        This method implements connection pooling by maintaining a cache of clients
        per proxy. Clients are configured with connection pool settings from the
        configuration and are reused across multiple requests to the same proxy.

        The pool has a maximum size limit (default: 100). When the limit is reached,
        the least recently used client is evicted to prevent unbounded memory growth.

        Args:
            proxy: Proxy instance to get/create client for
            proxy_dict: Proxy dictionary for httpx configuration

        Returns:
            Configured httpx.AsyncClient instance with connection pooling
        """
        proxy_id = str(proxy.id)

        # Try to get existing client from LRU pool
        existing_client = await self._client_pool.get(proxy_id)
        if existing_client is not None:
            return existing_client

        # Create new client with connection pooling settings
        client = httpx.AsyncClient(
            proxy=proxy_dict.get("http://"),
            timeout=self.config.timeout,
            verify=self.config.verify_ssl,
            follow_redirects=self.config.follow_redirects,
            limits=httpx.Limits(
                max_connections=self.config.pool_connections,
                max_keepalive_connections=self.config.pool_max_keepalive,
            ),
        )

        # Store in LRU pool (automatically evicts LRU if at capacity)
        await self._client_pool.put(proxy_id, client)

        logger.debug(
            "Created new pooled async client for proxy",
            proxy_id=proxy_id,
            pool_connections=self.config.pool_connections,
            pool_max_keepalive=self.config.pool_max_keepalive,
            client_pool_size=len(self._client_pool),
        )

        return client

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

    async def _make_request(
        self,
        method: str,
        url: str,
        retry_policy: RetryPolicy | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Make async HTTP request with automatic proxy rotation, retry, and circuit breakers.

        Args:
            method: HTTP method
            url: URL to request
            retry_policy: Optional per-request retry policy override
            **kwargs: Additional request parameters

        Returns:
            HTTP response

        Raises:
            ProxyPoolEmptyError: If no healthy proxies available
            ProxyConnectionError: If all retry attempts fail
        """
        if self.pool.size == 0:
            await self._ensure_request_bootstrap()

        # Select proxy with circuit breaker filtering
        try:
            proxy = self._select_proxy_with_circuit_breaker()
        except ProxyPoolEmptyError:
            logger.error("No healthy proxies available or all circuit breakers open")
            raise

        proxy_dict = self._get_proxy_dict(proxy)

        logger.info(
            f"Making {method} request to {url}",
            proxy_id=str(proxy.id),
            proxy_url=str(proxy.url),
        )

        # Get or create pooled client for this proxy
        client = await self._get_or_create_client(proxy, proxy_dict)

        # Define async request function for retry executor
        async def request_fn() -> httpx.Response:
            # Use pooled client (no context manager - client is reused)
            response = await client.request(method, url, **kwargs)

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

            return response

        # Execute with retry - note that retry_executor.execute_with_retry is sync
        # We'll need to handle the async nature here
        try:
            # Since the retry executor is sync, we need to adapt it for async
            # For now, we'll call the async request_fn directly with basic retry logic
            response = await self._execute_async_with_retry(
                request_fn, proxy, method, url, retry_policy
            )

            # Record success in strategy
            self.strategy.record_result(proxy, success=True, response_time_ms=0.0)

            logger.info(
                f"Request successful: {method} {url}",
                proxy_id=str(proxy.id),
                status_code=response.status_code,
            )

            return response

        except ProxyAuthenticationError:
            # Re-raise auth errors without wrapping
            raise
        except Exception as e:
            # Record failure in strategy
            self.strategy.record_result(proxy, success=False, response_time_ms=0.0)

            logger.warning(
                f"Request failed after retries: {method} {url}",
                proxy_id=str(proxy.id),
                error=str(e),
            )

            raise ProxyConnectionError(f"Request failed: {e}") from e

    async def _execute_async_with_retry(
        self,
        request_fn: Any,
        proxy: Proxy,
        method: str,
        url: str,
        retry_policy: RetryPolicy | None = None,
    ) -> httpx.Response:
        """
        Execute async request with retry logic (ASYNCHRONOUS).

        This is the async counterpart to RetryExecutor.execute_with_retry.
        It uses asyncio.sleep for non-blocking delays instead of time.sleep.

        Args:
            request_fn: Async function to execute
            proxy: Proxy being used
            method: HTTP method
            url: Target URL
            retry_policy: Optional retry policy override

        Returns:
            HTTP response

        Raises:
            Exception: If all retry attempts fail
        """
        policy = retry_policy or self.retry_policy
        circuit_breaker = self.circuit_breakers.get(str(proxy.id))

        if circuit_breaker and not circuit_breaker.should_attempt_request():
            raise ProxyConnectionError("Circuit breaker is open for this proxy")

        last_exception = None
        previous_delay: float | None = None  # Track for decorrelated jitter
        for attempt in range(policy.max_attempts):
            try:
                response = await request_fn()

                # Record success in circuit breaker
                if circuit_breaker:
                    circuit_breaker.record_success()

                return response
            except Exception as e:
                last_exception = e

                # Record failure in circuit breaker
                if circuit_breaker:
                    circuit_breaker.record_failure()

                # Check if we should retry
                if attempt < policy.max_attempts - 1:
                    # Calculate backoff delay using decorrelated jitter
                    delay = policy.calculate_delay(attempt, previous_delay=previous_delay)
                    logger.debug(
                        f"Retry attempt {attempt + 1}/{policy.max_attempts} after {delay}s",
                        proxy_id=str(proxy.id),
                    )
                    # ASYNC sleep - non-blocking delay for event loop
                    await asyncio.sleep(delay)
                    previous_delay = delay  # Track for decorrelated jitter
                else:
                    break

        # All retries exhausted
        raise last_exception if last_exception else ProxyConnectionError("Request failed")

    async def get(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make async GET request."""
        return await self._make_request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make async POST request."""
        return await self._make_request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make async PUT request."""
        return await self._make_request("PUT", url, **kwargs)

    async def delete(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make async DELETE request."""
        return await self._make_request("DELETE", url, **kwargs)

    async def patch(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make async PATCH request."""
        return await self._make_request("PATCH", url, **kwargs)

    async def head(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make async HEAD request."""
        return await self._make_request("HEAD", url, **kwargs)

    async def options(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make async OPTIONS request."""
        return await self._make_request("OPTIONS", url, **kwargs)

    def _aggregation_loop(self) -> None:
        """
        Persistent thread loop for periodic metrics aggregation.

        Runs every 5 minutes until stop event is set.
        Uses threading.Event.wait() for interruptible sleep.
        """
        while not self._stop_event.wait(timeout=300.0):  # 5 minutes
            try:
                self.retry_metrics.aggregate_hourly()
            except Exception as e:
                logger.warning(f"Metrics aggregation failed: {e}")

    def get_circuit_breaker_states(self) -> dict[str, CircuitBreaker]:
        """
        Get circuit breaker states for all proxies.

        Returns:
            Dictionary mapping proxy IDs to their circuit breaker instances
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

    def _select_proxy_with_circuit_breaker(self) -> Proxy:
        """
        Select a proxy while respecting circuit breaker states.

        Returns:
            Selected proxy

        Raises:
            ProxyPoolEmptyError: If no healthy proxies available or all circuit breakers open
        """
        # Check if all circuit breakers are open (FR-019)
        # Use thread-safe snapshot to avoid race conditions during iteration
        available_proxies = []
        for proxy in self.pool.get_all_proxies():
            circuit_breaker = self.circuit_breakers.get(str(proxy.id))
            if circuit_breaker and circuit_breaker.should_attempt_request():
                available_proxies.append(proxy)

        if not available_proxies:
            logger.error("All circuit breakers are open - no proxies available")
            raise ProxyPoolEmptyError(
                "503 Service Temporarily Unavailable - All proxies are currently failing. "
                "Please wait for circuit breakers to recover."
            )

        # Create temporary pool with available proxies
        temp_pool = ProxyPool(name="temp", proxies=available_proxies)

        # Select from available proxies using strategy
        return self.strategy.select(temp_pool)
