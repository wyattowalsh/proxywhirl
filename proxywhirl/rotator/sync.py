"""
Main proxy rotation implementation.
"""

from __future__ import annotations

import queue
import threading
import time
from typing import TYPE_CHECKING, Any
from urllib.parse import quote

import httpx
from loguru import logger

from proxywhirl.circuit_breaker import CircuitBreaker
from proxywhirl.exceptions import (
    ProxyAuthenticationError,
    ProxyConnectionError,
    ProxyPoolEmptyError,
    RequestQueueFullError,
)
from proxywhirl.models import Proxy, ProxyChain, ProxyConfiguration, ProxyPool
from proxywhirl.retry import NonRetryableError, RetryExecutor, RetryMetrics, RetryPolicy
from proxywhirl.rotator._bootstrap import bootstrap_pool_if_empty_sync
from proxywhirl.rotator.base import ProxyRotatorBase
from proxywhirl.rotator.client_pool import (
    LRUClientPool,  # noqa: F401 - re-export for backward compatibility
)
from proxywhirl.strategies import (
    LeastUsedStrategy,
    RandomStrategy,
    RotationStrategy,
    RoundRobinStrategy,
    WeightedStrategy,
)
from proxywhirl.utils import mask_proxy_url

if TYPE_CHECKING:
    from proxywhirl.rate_limiting import SyncRateLimiter


class ProxyWhirl(ProxyRotatorBase):
    """
    Main class for proxy rotation with automatic failover.

    Provides HTTP methods (GET, POST, PUT, DELETE, PATCH) that automatically
    rotate through a pool of proxies, with intelligent failover on connection errors.

    Example:
        ```python
        from proxywhirl import ProxyWhirl, Proxy

        rotator = ProxyWhirl()
        rotator.add_proxy("http://proxy1.example.com:8080")
        rotator.add_proxy("http://proxy2.example.com:8080")

        response = rotator.get("https://httpbin.org/ip")
        print(response.json())
        ```
    """

    def __init__(
        self,
        proxies: list[Proxy] | None = None,
        strategy: RotationStrategy | str | None = None,
        config: ProxyConfiguration | None = None,
        retry_policy: RetryPolicy | None = None,
        rate_limiter: SyncRateLimiter | None = None,
    ) -> None:
        """
        Initialize ProxyWhirl.

        Args:
            proxies: Initial list of proxies (optional)
            strategy: Rotation strategy instance or strategy name string
                     ("round-robin", "random", "weighted", "least-used")
                     Default: RoundRobinStrategy
            config: Configuration settings (default: ProxyConfiguration())
            retry_policy: Retry policy configuration (default: RetryPolicy())
            rate_limiter: Synchronous rate limiter for controlling request rates (optional)
        """
        self.pool = ProxyPool(name="default", proxies=proxies or [])
        self.chains: list[ProxyChain] = []  # Track registered proxy chains

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
        self._client: httpx.Client | None = None
        self._client_pool = LRUClientPool(maxsize=100)  # LRU cache with max 100 clients

        # Retry and circuit breaker components
        self.retry_policy = retry_policy or RetryPolicy()
        self.circuit_breakers: dict[str, CircuitBreaker] = {}
        self.retry_metrics = RetryMetrics()
        self.retry_executor = RetryExecutor(
            self.retry_policy, self.circuit_breakers, self.retry_metrics
        )

        # Rate limiting
        self.rate_limiter = rate_limiter

        # Request queuing (optional, disabled by default)
        self._request_queue: queue.Queue[Any] | None = None
        if self.config.queue_enabled:
            self._request_queue = queue.Queue(maxsize=self.config.queue_size)
            logger.info("Request queuing enabled", queue_size=self.config.queue_size)

        # Initialize circuit breakers for existing proxies (all start CLOSED per FR-021)
        # Use get_all_proxies() for consistency, even though this is during init
        for proxy in self.pool.get_all_proxies():
            self.circuit_breakers[str(proxy.id)] = CircuitBreaker(proxy_id=str(proxy.id))

        # Initialize strategy lock for atomic strategy swapping
        self._strategy_lock = threading.RLock()
        self._bootstrap_lock = threading.Lock()
        self._bootstrap_attempted = False
        self._bootstrap_error_message: str | None = None

        # Start periodic metrics aggregation timer (every 5 minutes)
        self._aggregation_timer: threading.Timer | None = None
        self._start_aggregation_timer()

        # Configure logging
        if hasattr(logger, "_core") and not logger._core.handlers:
            from proxywhirl.utils import configure_logging

            configure_logging(
                level=self.config.log_level,
                format_type=self.config.log_format,
                redact_credentials=self.config.log_redact_credentials,
            )

    def __enter__(self) -> ProxyWhirl:
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

        # Close all pooled clients
        self._close_all_clients()

        # Cancel aggregation timer
        if self._aggregation_timer:
            self._aggregation_timer.cancel()
            self._aggregation_timer = None

    def __del__(self) -> None:
        """Destructor to ensure clients are closed."""
        # Only cleanup if initialization completed
        if hasattr(self, "_client_pool"):
            self._close_all_clients()

        # Cancel aggregation timer
        if hasattr(self, "_aggregation_timer") and self._aggregation_timer:
            self._aggregation_timer.cancel()

    def _close_all_clients(self) -> None:
        """Close all pooled clients and clear the pool."""
        if hasattr(self, "_client_pool"):
            self._client_pool.clear()

    def add_proxy(self, proxy: Proxy | str) -> None:
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

        # Mask credentials in log output
        masked_url = mask_proxy_url(proxy.url)
        logger.info(f"Added proxy to pool: {masked_url}", proxy_id=str(proxy.id))

    def remove_proxy(self, proxy_id: str) -> None:
        """
        Remove a proxy from the pool.

        Args:
            proxy_id: UUID of proxy to remove
        """
        from uuid import UUID

        # Close and remove the client for this proxy if it exists
        self._client_pool.remove(proxy_id)

        # Clean up circuit breaker to prevent memory leak
        if proxy_id in self.circuit_breakers:
            del self.circuit_breakers[proxy_id]
            logger.debug(f"Removed circuit breaker for proxy: {proxy_id}")

        self.pool.remove_proxy(UUID(proxy_id))
        logger.info(f"Removed proxy from pool: {proxy_id}")

    def _bootstrap_pool_if_empty(
        self,
        *,
        validate: bool = True,
        timeout: int = 10,
        max_concurrent: int = 100,
        max_proxies: int | None = None,
    ) -> int:
        """Bootstrap pool from built-in sources when empty."""
        return bootstrap_pool_if_empty_sync(
            pool=self.pool,
            add_proxy=self.add_proxy,
            validate=validate,
            timeout=timeout,
            max_concurrent=max_concurrent,
            max_proxies=max_proxies,
        )

    def _ensure_bootstrap_for_empty_pool(self) -> None:
        """Trigger one-time lazy bootstrap before request-time proxy selection."""
        if self.pool.size > 0:
            return

        with self._bootstrap_lock:
            if self.pool.size > 0:
                return

            if self._bootstrap_error_message is not None:
                raise ProxyPoolEmptyError(self._bootstrap_error_message)

            if self._bootstrap_attempted:
                return

            self._bootstrap_attempted = True
            try:
                self._bootstrap_pool_if_empty()
            except ProxyPoolEmptyError as exc:
                self._bootstrap_error_message = str(exc)
                raise

    def add_chain(self, chain: ProxyChain) -> None:
        """
        Add a proxy chain to the rotator.

        This method registers a proxy chain for potential use in routing.
        The entry proxy (first proxy in the chain) is added to the pool
        for selection by rotation strategies.

        Note: Full CONNECT tunneling implementation is not yet supported.
        Currently, only the entry proxy is used for routing, with chain
        metadata stored for future multi-hop implementation.

        Args:
            chain: ProxyChain instance to register

        Example:
            >>> rotator = ProxyWhirl()
            >>> chain = ProxyChain(
            ...     proxies=[
            ...         Proxy(url="http://proxy1.com:8080"),
            ...         Proxy(url="http://proxy2.com:8080"),
            ...     ],
            ...     name="my_chain"
            ... )
            >>> rotator.add_chain(chain)
        """
        # Store the chain for future reference
        self.chains.append(chain)

        # Add entry proxy to the pool for selection
        entry_proxy = chain.entry_proxy

        # Tag the entry proxy to indicate it's part of a chain
        if not hasattr(entry_proxy, "tags"):
            entry_proxy.tags = set()
        entry_proxy.tags.add("chain_entry")

        # Store chain metadata in proxy metadata
        entry_proxy.metadata["chain_name"] = chain.name
        entry_proxy.metadata["chain_length"] = chain.chain_length
        entry_proxy.metadata["chain_urls"] = chain.get_chain_urls()

        # Add to pool
        self.pool.add_proxy(entry_proxy)

        # Initialize circuit breaker for the entry proxy
        self.circuit_breakers[str(entry_proxy.id)] = CircuitBreaker(proxy_id=str(entry_proxy.id))

        logger.info(
            "Added proxy chain to rotator",
            chain_name=chain.name or "unnamed",
            chain_length=chain.chain_length,
            entry_proxy=str(entry_proxy.url),
        )

    def get_chains(self) -> list[ProxyChain]:
        """
        Get all registered proxy chains.

        Returns:
            List of ProxyChain instances
        """
        return self.chains.copy()

    def remove_chain(self, chain_name: str) -> bool:
        """
        Remove a proxy chain by name.

        Args:
            chain_name: Name of the chain to remove

        Returns:
            True if chain was found and removed, False otherwise
        """
        for i, chain in enumerate(self.chains):
            if chain.name == chain_name:
                # Remove the entry proxy from the pool
                entry_proxy_id = str(chain.entry_proxy.id)
                try:
                    self.remove_proxy(entry_proxy_id)
                except Exception as e:
                    logger.warning(f"Could not remove entry proxy: {e}")

                # Remove the chain
                self.chains.pop(i)

                logger.info(f"Removed proxy chain: {chain_name}")
                return True

        logger.warning(f"Chain not found: {chain_name}")
        return False

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
            >>> rotator = ProxyWhirl(strategy="round-robin")
            >>> # ... after some requests ...
            >>> rotator.set_strategy("performance-based")  # Hot-swap
            >>> # New requests now use performance-based strategy

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

        if atomic:
            # Use a lock to ensure atomic swap
            with self._strategy_lock:
                self.strategy = new_strategy
        else:
            # Direct assignment (faster but less safe)
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

        # Take a snapshot to avoid race conditions during iteration
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

    def clear_unhealthy_proxies(self) -> int:
        """
        Remove all unhealthy and dead proxies from the pool.

        Returns:
            Number of proxies removed
        """
        from proxywhirl.models import HealthStatus

        # Take a snapshot to avoid race conditions during iteration
        proxies_snapshot = self.pool.get_all_proxies()

        # Capture IDs of proxies to be removed before clearing
        removed_proxy_ids = [
            str(p.id)
            for p in proxies_snapshot
            if p.health_status in (HealthStatus.DEAD, HealthStatus.UNHEALTHY)
        ]

        removed_count = self.pool.clear_unhealthy()

        # Clean up circuit breakers for removed proxies to prevent memory leak
        for proxy_id in removed_proxy_ids:
            if proxy_id in self.circuit_breakers:
                del self.circuit_breakers[proxy_id]
                logger.debug(f"Removed circuit breaker for unhealthy proxy: {proxy_id}")

        logger.info(
            "Cleared unhealthy proxies from pool",
            removed_count=removed_count,
            remaining_proxies=self.pool.size,
        )

        return removed_count

    def _get_or_create_client(self, proxy: Proxy, proxy_dict: dict[str, str]) -> httpx.Client:
        """
        Get or create a pooled httpx.Client for the given proxy.

        This method implements connection pooling by maintaining a cache of clients
        per proxy. Clients are configured with connection pool settings from the
        configuration and are reused across multiple requests to the same proxy.

        The pool has a maximum size limit (default: 100). When the limit is reached,
        the least recently used client is evicted to prevent unbounded memory growth.

        Args:
            proxy: Proxy instance to get/create client for
            proxy_dict: Proxy dictionary for httpx configuration

        Returns:
            Configured httpx.Client instance with connection pooling
        """
        proxy_id = str(proxy.id)

        # Try to get existing client from LRU pool
        existing_client = self._client_pool.get(proxy_id)
        if existing_client is not None:
            return existing_client

        # Create new client with connection pooling settings
        client = httpx.Client(
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
        self._client_pool.put(proxy_id, client)

        logger.debug(
            "Created new pooled client for proxy",
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

    def _make_request(
        self,
        method: str,
        url: str,
        retry_policy: RetryPolicy | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Make HTTP request with automatic proxy rotation, retry, and circuit breakers.

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
            RequestQueueFullError: If queue is full and cannot accept request
        """
        self._ensure_bootstrap_for_empty_pool()

        # Select proxy with circuit breaker filtering
        try:
            proxy = self._select_proxy_with_circuit_breaker()
        except ProxyPoolEmptyError:
            logger.error("No healthy proxies available or all circuit breakers open")
            raise

        # Check rate limit before making request
        if self.rate_limiter is not None:
            proxy_id = str(proxy.id)
            # Check rate limit (synchronous call)
            allowed = self.rate_limiter.check_limit(proxy_id)
            if not allowed:
                # Mask proxy URL in log output
                masked_url = mask_proxy_url(str(proxy.url))
                logger.warning(
                    f"Rate limit exceeded for proxy {proxy_id}",
                    proxy_id=proxy_id,
                    proxy_url=masked_url,
                )

                # If queuing is enabled, try to queue the request
                if self.config.queue_enabled and self._request_queue is not None:
                    return self._queue_request(method, url, proxy, retry_policy, **kwargs)

                # Otherwise, raise error
                raise ProxyConnectionError(
                    f"Rate limit exceeded for proxy {proxy_id}. "
                    "Please wait before making more requests."
                )

        proxy_dict = self._get_proxy_dict(proxy)

        # Mask proxy URL in log output
        masked_url = mask_proxy_url(str(proxy.url))
        logger.info(
            f"Making {method} request to {url}",
            proxy_id=str(proxy.id),
            proxy_url=masked_url,
        )

        # Get or create pooled client for this proxy
        client = self._get_or_create_client(proxy, proxy_dict)

        # Define request function for retry executor
        def request_fn() -> httpx.Response:
            # Use pooled client (no context manager - client is reused)
            response = client.request(method, url, **kwargs)

            # Check for authentication errors (401 Unauthorized, 407 Proxy Auth Required)
            if response.status_code in (401, 407):
                logger.error(
                    f"Proxy authentication failed: {proxy.url}",
                    proxy_id=str(proxy.id),
                    status_code=response.status_code,
                )
                raise ProxyAuthenticationError(
                    f"Proxy authentication failed ({response.status_code}) for {proxy.url}. "
                    "Please provide valid credentials (username and password)."
                )

            return response

        # Create a temporary retry executor with effective policy if different from global
        if retry_policy is not None:
            executor = RetryExecutor(retry_policy, self.circuit_breakers, self.retry_metrics)
        else:
            executor = self.retry_executor

        # Execute with retry
        try:
            request_start_time = time.time()
            response = executor.execute_with_retry(request_fn, proxy, method, url)
            response_time_ms = (time.time() - request_start_time) * 1000

            # Record success in strategy
            self.strategy.record_result(proxy, success=True, response_time_ms=response_time_ms)

            logger.info(
                f"Request successful: {method} {url}",
                proxy_id=str(proxy.id),
                status_code=response.status_code,
                response_time_ms=response_time_ms,
            )

            return response

        except ProxyAuthenticationError as e:
            # Record auth errors as failures
            self.strategy.record_result(proxy, success=False, response_time_ms=0.0)
            logger.error(
                f"Authentication error for proxy {proxy.id}",
                proxy_id=str(proxy.id),
                error=str(e),
            )
            # Re-raise auth errors without wrapping
            raise
        except NonRetryableError as e:
            # Check if this wraps a ProxyAuthenticationError
            if isinstance(e.__cause__, ProxyAuthenticationError):
                # Record auth errors as failures
                self.strategy.record_result(proxy, success=False, response_time_ms=0.0)
                logger.error(
                    f"Authentication error for proxy {proxy.id}",
                    proxy_id=str(proxy.id),
                    error=str(e.__cause__),
                )
                # Re-raise the original auth error
                raise e.__cause__
            # For other non-retryable errors, record failure and convert to ProxyConnectionError
            self.strategy.record_result(proxy, success=False, response_time_ms=0.0)
            logger.warning(
                f"Request failed after retries: {method} {url}",
                proxy_id=str(proxy.id),
                error=str(e),
            )
            raise ProxyConnectionError(f"Request failed: {e}") from e
        except Exception as e:
            # Record failure in strategy
            self.strategy.record_result(proxy, success=False, response_time_ms=0.0)

            logger.warning(
                f"Request failed after retries: {method} {url}",
                proxy_id=str(proxy.id),
                error=str(e),
            )

            raise ProxyConnectionError(f"Request failed: {e}") from e

    def _queue_request(
        self,
        method: str,
        url: str,
        proxy: Proxy,
        retry_policy: RetryPolicy | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Queue a request when rate limited.

        Args:
            method: HTTP method
            url: URL to request
            proxy: Proxy to use
            retry_policy: Optional retry policy
            **kwargs: Additional request parameters

        Returns:
            HTTP response after queuing

        Raises:
            RequestQueueFullError: If queue is full
        """
        if self._request_queue is None:
            raise RuntimeError("Request queue not initialized")

        # Check if queue has space (non-blocking check for backpressure)
        if self._request_queue.full():
            logger.error(
                "Request queue is full - backpressure triggered",
                queue_size=self.config.queue_size,
                current_size=self._request_queue.qsize(),
            )
            raise RequestQueueFullError(
                "Request queue is full. Cannot accept more requests.",
                queue_size=self.config.queue_size,
            )

        # Create request task
        request_data = {
            "method": method,
            "url": url,
            "proxy": proxy,
            "retry_policy": retry_policy,
            "kwargs": kwargs,
        }

        # Queue the request (blocking put)
        try:
            # Use put_nowait to avoid blocking (raises QueueFull if full)
            self._request_queue.put_nowait(request_data)

            logger.info(
                "Request queued",
                method=method,
                url=url,
                queue_size=self._request_queue.qsize(),
                proxy_id=str(proxy.id),
            )

            # Process the queue and execute the request
            return self._process_queue_sync()

        except queue.Full as e:
            logger.error("Queue is full - cannot add request")
            raise RequestQueueFullError(
                "Queue is full - cannot add request", queue_size=self.config.queue_size
            ) from e

    def _process_queue_sync(self) -> httpx.Response:
        """
        Process queued requests synchronously.

        Returns:
            HTTP response from processed request

        Raises:
            ProxyConnectionError: If request processing fails
        """
        if self._request_queue is None or self._request_queue.empty():
            raise RuntimeError("No requests in queue to process")

        # Get next request from queue (non-blocking)
        try:
            request_data = self._request_queue.get_nowait()
        except queue.Empty as e:
            raise ProxyConnectionError("No requests in queue") from e

        # Extract request parameters
        method = request_data["method"]
        url = request_data["url"]
        proxy = request_data["proxy"]
        retry_policy = request_data["retry_policy"]
        kwargs = request_data["kwargs"]

        logger.info(
            "Processing queued request",
            method=method,
            url=url,
            remaining_queue_size=self._request_queue.qsize(),
        )

        # Execute the request using the existing logic
        proxy_dict = self._get_proxy_dict(proxy)
        client = self._get_or_create_client(proxy, proxy_dict)

        # Define request function for retry executor
        def request_fn() -> httpx.Response:
            response = client.request(method, url, **kwargs)

            # Check for authentication errors
            if response.status_code in (401, 407):
                logger.error(
                    f"Proxy authentication failed: {proxy.url}",
                    proxy_id=str(proxy.id),
                    status_code=response.status_code,
                )
                raise ProxyAuthenticationError(
                    f"Proxy authentication failed ({response.status_code}) for {proxy.url}. "
                    "Please provide valid credentials (username and password)."
                )

            return response

        # Create executor with appropriate policy
        if retry_policy is not None:
            executor = RetryExecutor(retry_policy, self.circuit_breakers, self.retry_metrics)
        else:
            executor = self.retry_executor

        # Execute with retry
        try:
            request_start_time = time.time()
            response = executor.execute_with_retry(request_fn, proxy, method, url)
            response_time_ms = (time.time() - request_start_time) * 1000

            # Record success in strategy
            self.strategy.record_result(proxy, success=True, response_time_ms=response_time_ms)

            logger.info(
                f"Queued request successful: {method} {url}",
                proxy_id=str(proxy.id),
                status_code=response.status_code,
                response_time_ms=response_time_ms,
            )

            return response

        except Exception as e:
            # Record failure in strategy
            self.strategy.record_result(proxy, success=False, response_time_ms=0.0)

            logger.warning(
                f"Queued request failed: {method} {url}",
                proxy_id=str(proxy.id),
                error=str(e),
            )

            raise ProxyConnectionError(f"Queued request failed: {e}") from e

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

    def _start_aggregation_timer(self) -> None:
        """Start periodic metrics aggregation timer (every 5 minutes)."""

        def aggregate() -> None:
            self.retry_metrics.aggregate_hourly()
            self._start_aggregation_timer()  # Schedule next aggregation

        self._aggregation_timer = threading.Timer(300.0, aggregate)  # 5 minutes
        self._aggregation_timer.daemon = True
        self._aggregation_timer.start()

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

    def get_queue_stats(self) -> dict[str, Any]:
        """
        Get statistics about the request queue.

        Returns:
            Dictionary containing queue statistics:
            - enabled: Whether queuing is enabled
            - size: Current number of queued requests
            - max_size: Maximum queue capacity
            - is_full: Whether queue is at capacity
            - is_empty: Whether queue is empty
        """
        if not self.config.queue_enabled or self._request_queue is None:
            return {
                "enabled": False,
                "size": 0,
                "max_size": 0,
                "is_full": False,
                "is_empty": True,
            }

        return {
            "enabled": True,
            "size": self._request_queue.qsize(),
            "max_size": self.config.queue_size,
            "is_full": self._request_queue.full(),
            "is_empty": self._request_queue.empty(),
        }

    def clear_queue(self) -> int:
        """
        Clear all pending requests from the queue.

        Returns:
            Number of requests cleared

        Raises:
            RuntimeError: If queue is not enabled
        """
        if not self.config.queue_enabled or self._request_queue is None:
            raise RuntimeError("Request queue is not enabled")

        count = 0
        while not self._request_queue.empty():
            try:
                self._request_queue.get_nowait()
                count += 1
            except queue.Empty:
                break

        logger.info(f"Cleared {count} requests from queue")
        return count

    def _select_proxy_with_circuit_breaker(self) -> Proxy:
        """
        Select a proxy while respecting circuit breaker states.

        Returns:
            Selected proxy

        Raises:
            ProxyPoolEmptyError: If no healthy proxies available or all circuit breakers open
        """
        # Check if all circuit breakers are open (FR-019)
        # Take a snapshot to avoid race conditions during iteration
        proxies_snapshot = self.pool.get_all_proxies()

        available_proxies = []
        for proxy in proxies_snapshot:
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
