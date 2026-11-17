"""
Async proxy rotation implementation using httpx.AsyncClient.
"""

from __future__ import annotations

import asyncio
import threading
from collections import OrderedDict
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any
from urllib.parse import quote, urljoin

import httpx
from loguru import logger

from proxywhirl.circuit_breaker import CircuitBreaker
from proxywhirl.exceptions import (
    ProxyAuthenticationError,
    ProxyConnectionError,
    ProxyPoolEmptyError,
    RateLimitExceededError,
    redact_url,
)
from proxywhirl.logging_config import configure_logging
from proxywhirl.models import BootstrapConfig, Proxy, ProxyPool
from proxywhirl.orchestration import FailoverPolicy, ProxyRotationCallback, RequestOrchestration
from proxywhirl.retry import NonRetryableError, RetryExecutor, RetryMetrics, RetryPolicy
from proxywhirl.rotator._bootstrap import bootstrap_pool_if_empty_async
from proxywhirl.rotator._wiring import resolve_strategy
from proxywhirl.rotator.base import CircuitBreakerSnapshot, ProxyRotatorBase
from proxywhirl.security import prepare_pinned_request
from proxywhirl.settings import ProxyConfiguration
from proxywhirl.strategies import RotationStrategy
from proxywhirl.utils import mask_proxy_url

if TYPE_CHECKING:
    from proxywhirl.rate_limiting import AsyncRateLimiter

_REDIRECT_STATUS_CODES = frozenset({301, 302, 303, 307, 308})
_MAX_PINNED_REDIRECTS = 5


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
                    except Exception as exc:
                        logger.bind(
                            proxy_id=lru_proxy_id,
                            error_type=type(exc).__name__,
                        ).warning("Error closing evicted async client")

                # Add new client
                self._clients[proxy_id] = client

    async def put_if_absent(
        self,
        proxy_id: str,
        client: httpx.AsyncClient,
    ) -> httpx.AsyncClient:
        """Atomically publish ``client`` or return the existing canonical client."""
        duplicate: httpx.AsyncClient | None = None
        evicted: tuple[str, httpx.AsyncClient] | None = None
        async with self._lock:
            existing = self._clients.get(proxy_id)
            if existing is not None:
                self._clients.move_to_end(proxy_id)
                duplicate = client
                canonical = existing
            else:
                if len(self._clients) >= self._maxsize:
                    evicted = self._clients.popitem(last=False)
                self._clients[proxy_id] = client
                canonical = client

        if duplicate is not None and duplicate is not canonical:
            await self._close_client(duplicate, proxy_id=proxy_id, reason="duplicate")
        if evicted is not None:
            evicted_proxy_id, evicted_client = evicted
            await self._close_client(
                evicted_client,
                proxy_id=evicted_proxy_id,
                reason="evicted",
            )
        return canonical

    @staticmethod
    async def _close_client(
        client: httpx.AsyncClient,
        *,
        proxy_id: str,
        reason: str,
    ) -> None:
        """Close a discarded client without disturbing the canonical pool entry."""
        try:
            await client.aclose()
            logger.debug(
                "Closed non-canonical pooled async client",
                proxy_id=proxy_id,
                reason=reason,
            )
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.bind(
                proxy_id=proxy_id,
                reason=reason,
                error_type=type(exc).__name__,
            ).warning("Error closing non-canonical async client")

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
                except Exception as exc:
                    logger.bind(
                        proxy_id=proxy_id,
                        error_type=type(exc).__name__,
                    ).warning("Error closing async client")

    async def clear(self) -> None:
        """Close all clients and clear the pool."""
        async with self._lock:
            clients = list(self._clients.items())
            self._clients.clear()

        cancellation: asyncio.CancelledError | None = None
        for proxy_id, client in clients:
            try:
                await client.aclose()
                logger.debug("Closed pooled async client", proxy_id=proxy_id)
            except asyncio.CancelledError as exc:
                cancellation = cancellation or exc
            except Exception as exc:
                logger.bind(
                    proxy_id=proxy_id,
                    error_type=type(exc).__name__,
                ).warning("Error closing async client")
        if cancellation is not None:
            raise cancellation

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

    Example::

        from proxywhirl import AsyncProxyWhirl, Proxy

        async with AsyncProxyWhirl() as rotator:
            await rotator.add_proxy("http://proxy1.example.com:8080")
            await rotator.add_proxy("http://proxy2.example.com:8080")

            response = await rotator.get("https://httpbin.org/ip")
            print(response.json())
    """

    def __init__(
        self,
        proxies: list[Proxy] | None = None,
        strategy: RotationStrategy | str | None = None,
        config: ProxyConfiguration | None = None,
        retry_policy: RetryPolicy | None = None,
        failover_policy: FailoverPolicy | None = None,
        proxy_rotation_callback: ProxyRotationCallback | None = None,
        bootstrap: BootstrapConfig | bool | None = None,
        rate_limiter: AsyncRateLimiter | None = None,
    ) -> None:
        """
        Initialize AsyncProxyWhirl.

        Args:
            proxies: Initial list of proxies (optional)
            strategy: Rotation strategy instance or name string. Supported
                names: ``round-robin``, ``random``, ``weighted``,
                ``least-used``, ``performance-based``, ``session``,
                ``geo-targeted``, ``cost-aware``. Defaults to RoundRobinStrategy.
            config: Configuration settings (default: ProxyConfiguration())
            retry_policy: Retry policy configuration (default: RetryPolicy())
            failover_policy: Cross-proxy failover policy (default: disabled for legacy behavior)
            proxy_rotation_callback: Optional callback invoked on proxy rotation.
            bootstrap: Bootstrap configuration for lazy proxy fetching.
                      False disables auto-bootstrap (for manual proxy management).
                      True or None uses default BootstrapConfig.
            rate_limiter: Async rate limiter for per-proxy request throttling (optional)
        """
        self.pool = ProxyPool(name="default", proxies=proxies or [])

        self.strategy = resolve_strategy(strategy)

        self.config = config or ProxyConfiguration()
        self._client: httpx.AsyncClient | None = None
        self._client_pool = LRUAsyncClientPool(maxsize=100)  # LRU cache with max 100 clients
        # Coerce bool/None to BootstrapConfig
        if bootstrap is False:
            self._bootstrap_config = BootstrapConfig(enabled=False)
        elif isinstance(bootstrap, BootstrapConfig):
            self._bootstrap_config = bootstrap
        else:
            self._bootstrap_config = BootstrapConfig()
        self._bootstrap_lock = asyncio.Lock()
        self._bootstrap_attempted = False
        self._bootstrap_error_message: str | None = None

        # Retry and circuit breaker components
        self.retry_policy = retry_policy or RetryPolicy()
        self.circuit_breakers: dict[str, CircuitBreaker] = {}
        self.retry_metrics = RetryMetrics()
        self.retry_executor = RetryExecutor(
            self.retry_policy, self.circuit_breakers, self.retry_metrics
        )
        self.failover_policy = failover_policy or FailoverPolicy.from_env()
        self.proxy_rotation_callback = proxy_rotation_callback
        self.rate_limiter = rate_limiter
        self._last_used_proxy: Proxy | None = None
        self.orchestrator = RequestOrchestration(
            failover_policy=self.failover_policy,
            retry_executor=self.retry_executor,
            strategy=self.strategy,
            pool=self.pool,
            circuit_breakers=self.circuit_breakers,
            select_proxy=self._select_proxy_with_circuit_breaker,
            get_all_proxies=self.pool.get_all_proxies,
            proxy_rotation_callback=self.proxy_rotation_callback,
        )

        # Initialize circuit breakers for existing proxies (all start CLOSED per FR-021)
        # Use thread-safe snapshot for initialization
        # The pool is not published yet, so its freshly validated list is safe to
        # inspect without acquiring a threading.RLock on the caller's event loop.
        for proxy in self.pool.proxies:
            self.circuit_breakers[str(proxy.id)] = CircuitBreaker(proxy_id=str(proxy.id))

        # Note: Strategy swapping is atomic via Python's reference assignment semantics.
        # No explicit lock needed as self.strategy = new_strategy is a single atomic operation.

        # Periodic metrics aggregation (daemon timer, same pattern as sync ProxyWhirl).
        # Deferred until ``__aenter__`` so bare ``AsyncProxyWhirl()`` construction in
        # unit tests does not schedule a Timer per instance (full-suite thread pressure).
        self._stop_event = threading.Event()
        self._aggregation_lock = threading.Lock()
        self._aggregation_timer: threading.Timer | None = None
        self._aggregation_thread: threading.Thread | None = None  # compat for tests

        # Configure logging
        if hasattr(logger, "_core") and not logger._core.handlers:
            configure_logging(
                level=self.config.log_level,
                format=self.config.log_format,
                redact_secrets=self.config.log_redact_credentials,
            )

    async def __aenter__(self) -> AsyncProxyWhirl:
        """Enter async context manager."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.config.timeout,
                verify=self.config.verify_ssl,
                follow_redirects=self.config.follow_redirects,
                limits=httpx.Limits(
                    max_connections=self.config.pool_connections,
                    max_keepalive_connections=self.config.pool_max_keepalive,
                ),
                http2=True,
            )
        self._stop_event.clear()
        # Start aggregation only for context-managed lifetime.
        if self._aggregation_timer is None:
            self._start_aggregation_timer()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context manager."""
        await self.aclose()

    async def aclose(self) -> None:
        """Close all owned resources; idempotent and cancellation-safe."""
        stop_event = getattr(self, "_stop_event", None)
        if stop_event is not None:
            stop_event.set()

        cancel_timer = getattr(self, "_cancel_aggregation_timer", None)
        if callable(cancel_timer):
            cancel_timer()

        first_error: BaseException | None = None
        client = getattr(self, "_client", None)
        if client is not None:
            self._client = None
            try:
                await client.aclose()
            except BaseException as exc:
                first_error = exc

        client_pool = getattr(self, "_client_pool", None)
        if client_pool is not None:
            try:
                await client_pool.clear()
            except BaseException as exc:
                if first_error is None:
                    first_error = exc
                else:
                    logger.bind(error_type=type(exc).__name__).warning(
                        "Additional error closing async client pool"
                    )

        if first_error is not None:
            raise first_error

    def __del__(self) -> None:
        """
        Destructor safety net when not used as a context manager.

        Only signals stop and cancels the daemon timer. Never joins or logs here:
        ``__del__`` can run during unrelated GC under a full pytest suite, and
        blocking work has been observed to hang the main thread.

        Note:
            Prefer ``async with AsyncProxyWhirl()`` for full httpx client cleanup.
        """
        stop_event = getattr(self, "_stop_event", None)
        if stop_event is not None:
            stop_event.set()
        cancel = getattr(self, "_cancel_aggregation_timer", None)
        if callable(cancel):
            cancel(join=False)

    async def _close_all_clients(self) -> None:
        """Close all pooled clients and clear the pool."""
        client_pool = getattr(self, "_client_pool", None)
        if client_pool is not None:
            await client_pool.clear()

    async def add_proxy(self, proxy: Proxy | str) -> None:
        """
        Add a proxy to the pool.

        Args:
            proxy: Proxy instance or URL string
        """
        if isinstance(proxy, str):
            from proxywhirl.utils import create_proxy_from_url

            proxy = create_proxy_from_url(proxy)

        if await self.pool.ahas_proxy_url(proxy.url):
            masked_url = mask_proxy_url(proxy.url)
            logger.debug(f"Skipped duplicate proxy: {masked_url}", proxy_id=str(proxy.id))
            return

        await self.pool.aadd_proxy(proxy)

        # Initialize circuit breaker for new proxy (starts CLOSED per FR-021)
        self.circuit_breakers[str(proxy.id)] = CircuitBreaker(proxy_id=str(proxy.id))

        masked_url = mask_proxy_url(proxy.url)
        logger.info(f"Added proxy to pool: {masked_url}", proxy_id=str(proxy.id))

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

        await self.pool.aremove_proxy(UUID(proxy_id))
        logger.info(f"Removed proxy from pool: {proxy_id}")

    async def _bootstrap_pool_if_empty(self) -> int:
        """Bootstrap pool from built-in sources when empty."""
        return await bootstrap_pool_if_empty_async(
            pool=self.pool,
            add_proxy=self.add_proxy,
            config=self._bootstrap_config,
        )

    async def _ensure_request_bootstrap(self) -> None:
        """Run one-time lazy bootstrap for async request path when pool starts empty."""
        if await self.pool.asize() > 0:
            return

        async with self._bootstrap_lock:
            if await self.pool.asize() > 0:
                return
            if self._bootstrap_error_message is not None:
                raise ProxyPoolEmptyError(self._bootstrap_error_message)
            if self._bootstrap_attempted:
                return

            self._bootstrap_attempted = True
            try:
                await self._bootstrap_pool_if_empty()
            except ProxyPoolEmptyError as exc:
                self._bootstrap_error_message = str(exc)
                raise

            # If pool is still empty after bootstrap (e.g., bootstrap disabled)
            if await self.pool.asize() == 0:
                if not self._bootstrap_config.enabled:
                    msg = (
                        "Proxy pool is empty and auto-bootstrap is disabled. "
                        "Call .add_proxy() to add proxies manually, or set "
                        "bootstrap=BootstrapConfig(enabled=True)."
                    )
                else:
                    msg = "Bootstrap completed but proxy pool is still empty."
                self._bootstrap_error_message = msg
                raise ProxyPoolEmptyError(msg)

    async def get_proxy(self) -> Proxy:
        """
        Get the next proxy from the pool using the rotation strategy.

        Triggers one-time lazy bootstrap when the pool is empty (parity with sync
        ProxyWhirl.get_proxy and request execution paths).

        Returns:
            Next proxy to use

        Raises:
            ProxyPoolEmptyError: If bootstrap fails or no healthy proxies available
        """
        if await self.pool.asize() == 0:
            await self._ensure_request_bootstrap()
        return await asyncio.to_thread(self._select_proxy_with_circuit_breaker)

    def set_strategy(self, strategy: RotationStrategy | str, *, atomic: bool = True) -> None:
        """
        Hot-swap the rotation strategy without restarting.

        This method implements atomic strategy swapping to ensure:
        - New requests immediately use the new strategy
        - In-flight requests complete with their original strategy
        - No requests are dropped during the swap
        - Swap completes in <100ms (SC-009)

        Args:
            strategy: New strategy instance or name string. Supported
                names: ``round-robin``, ``random``, ``weighted``,
                ``least-used``, ``performance-based``, ``session``,
                ``geo-targeted``, ``cost-aware``.
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
        new_strategy = resolve_strategy(strategy) if isinstance(strategy, str) else strategy

        # Store old strategy for logging
        old_strategy_name = self.strategy.__class__.__name__
        new_strategy_name = new_strategy.__class__.__name__

        # Python's reference assignment is atomic at the bytecode level,
        # so no explicit locking is needed for thread-safe strategy swap.
        # The 'atomic' parameter is kept for API compatibility but is now a no-op.
        self.strategy = new_strategy
        self.orchestrator.strategy = new_strategy

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

    @staticmethod
    def _pool_stats_from_snapshot(proxies_snapshot: list[Proxy]) -> dict[str, Any]:
        """Build pool statistics from one consistent proxy snapshot."""
        from proxywhirl.models import HealthStatus

        healthy_count = sum(
            1
            for proxy in proxies_snapshot
            if proxy.health_status
            in (HealthStatus.HEALTHY, HealthStatus.UNKNOWN, HealthStatus.DEGRADED)
        )
        unhealthy_count = sum(
            1 for proxy in proxies_snapshot if proxy.health_status == HealthStatus.UNHEALTHY
        )
        dead_count = sum(
            1 for proxy in proxies_snapshot if proxy.health_status == HealthStatus.DEAD
        )
        total_requests = sum(proxy.total_requests for proxy in proxies_snapshot)
        total_successes = sum(proxy.total_successes for proxy in proxies_snapshot)
        total_failures = sum(proxy.total_failures for proxy in proxies_snapshot)
        success_rates = [
            proxy.success_rate for proxy in proxies_snapshot if proxy.total_requests > 0
        ]

        return {
            "total_proxies": len(proxies_snapshot),
            "healthy_proxies": healthy_count,
            "unhealthy_proxies": unhealthy_count,
            "dead_proxies": dead_count,
            "total_requests": total_requests,
            "total_successes": total_successes,
            "total_failures": total_failures,
            "average_success_rate": (
                sum(success_rates) / len(success_rates) if success_rates else 0.0
            ),
        }

    def get_pool_stats(self) -> dict[str, Any]:
        """
        Get statistics about the proxy pool.

        Returns:
            dict[str, Any]: Pool statistics including total_proxies, healthy_proxies,
            unhealthy_proxies, dead_proxies, total_requests, total_successes,
            total_failures, and average_success_rate.
        """
        return self._pool_stats_from_snapshot(self.pool.get_all_proxies())

    async def aget_pool_stats(self) -> dict[str, Any]:
        """Get proxy-pool statistics without blocking the event loop."""
        return self._pool_stats_from_snapshot(await self.pool.aget_all_proxies())

    def get_statistics(self) -> dict[str, Any]:
        """
        Get comprehensive statistics including source breakdown (FR-050).

        Returns:
            dict[str, Any]: All stats from get_pool_stats() plus source_breakdown
            mapping source names to proxy counts.
        """
        stats = self.get_pool_stats()
        stats["source_breakdown"] = self.pool.get_source_breakdown()
        return stats

    async def aget_statistics(self) -> dict[str, Any]:
        """Get comprehensive statistics without blocking the event loop."""
        stats = await self.aget_pool_stats()
        stats["source_breakdown"] = await self.pool.aget_source_breakdown()
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
            for p in await self.pool.aget_all_proxies()
            if p.health_status in (HealthStatus.DEAD, HealthStatus.UNHEALTHY)
        ]

        removed_count = await self.pool.aclear_unhealthy()

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
            remaining_proxies=await self.pool.asize(),
        )

        return removed_count

    async def check_proxies_health(
        self, proxies: list[Proxy] | None = None, test_url: str = "https://httpbin.org/get"
    ) -> list[dict[str, Any]]:
        """Run concurrent health checks on proxies.

        Args:
            proxies: List of proxies to check. If None, checks all proxies in the pool.
            test_url: URL to use for health check requests

        Returns:
            List of health check result dictionaries
        """
        targets = proxies if proxies is not None else await self.pool.aget_all_proxies()
        if not targets:
            return []

        async def _check(proxy: Proxy) -> dict[str, Any]:
            proxy_dict = self._get_proxy_dict(proxy)
            loop = asyncio.get_running_loop()
            start_time = loop.time()
            try:
                async with httpx.AsyncClient(
                    proxy=proxy_dict.get("http://"),
                    timeout=self.config.timeout,
                    verify=self.config.verify_ssl,
                ) as client:
                    response = await client.get(test_url)
                    elapsed_ms = (loop.time() - start_time) * 1000
                    return {
                        "proxy_id": str(proxy.id),
                        "status": "healthy" if response.status_code == 200 else "unhealthy",
                        "latency_ms": elapsed_ms,
                        "error": None,
                    }
            except Exception as e:
                elapsed_ms = (loop.time() - start_time) * 1000
                return {
                    "proxy_id": str(proxy.id),
                    "status": "unhealthy",
                    "latency_ms": elapsed_ms,
                    "error": str(e),
                }

        return await asyncio.gather(*[_check(p) for p in targets])

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
            http2=True,
        )

        # Publish atomically so racing creators converge on one live client.
        canonical_client = await self._client_pool.put_if_absent(proxy_id, client)

        if canonical_client is client:
            logger.debug(
                "Created new pooled async client for proxy",
                proxy_id=proxy_id,
                pool_connections=self.config.pool_connections,
                pool_max_keepalive=self.config.pool_max_keepalive,
                client_pool_size=len(self._client_pool),
            )

        return canonical_client

    def _get_proxy_dict(self, proxy: Proxy) -> dict[str, str]:
        """
        Convert proxy to httpx proxy dict format.

        Args:
            proxy: Proxy to convert

        Returns:
            dict[str, str]: Proxy URL for httpx with "http://" and "https://" keys.
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

    @property
    def last_used_proxy(self) -> Proxy | None:
        """Return the proxy used for the most recent successful request."""
        return self._last_used_proxy

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
        if await self.pool.asize() == 0:
            await self._ensure_request_bootstrap()

        active_proxy: Proxy | None = None

        async def on_proxy_selected_async(proxy: Proxy) -> None:
            nonlocal active_proxy
            active_proxy = proxy
            if self.rate_limiter is None:
                return
            proxy_id = str(proxy.id)
            if await self.rate_limiter.check_limit(proxy_id):
                return
            masked_url = mask_proxy_url(str(proxy.url))
            logger.warning(
                f"Rate limit exceeded for proxy {proxy_id}",
                proxy_id=proxy_id,
                proxy_url=masked_url,
            )
            raise RateLimitExceededError(
                f"Rate limit exceeded for proxy {proxy_id}. "
                "Please wait before making more requests."
            )

        def request_fn_factory(
            proxy: Proxy,
        ) -> Callable[[], Awaitable[httpx.Response]]:
            proxy_dict = self._get_proxy_dict(proxy)
            masked_url = mask_proxy_url(str(proxy.url))
            safe_target_url = redact_url(url)
            logger.info(
                f"Making {method} request to {safe_target_url}",
                proxy_id=str(proxy.id),
                proxy_url=masked_url,
            )

            async def request_fn() -> httpx.Response:
                follow_redirects = bool(
                    kwargs.get("follow_redirects", self.config.follow_redirects)
                )
                current_url = url
                current_method = method
                request_kwargs = dict(kwargs)
                request_kwargs["follow_redirects"] = False
                response: httpx.Response | None = None
                client = await self._get_or_create_client(proxy, proxy_dict)
                for hop in range(_MAX_PINNED_REDIRECTS + 1):
                    try:
                        target, headers, extensions = prepare_pinned_request(
                            current_url,
                            headers=request_kwargs.get("headers"),
                            extensions=request_kwargs.get("extensions"),
                        )
                    except ValueError as exc:
                        raise ProxyConnectionError(f"Target URL blocked: {exc}") from exc
                    request_kwargs["headers"] = headers
                    request_kwargs["extensions"] = extensions
                    response = await client.request(current_method, target, **request_kwargs)
                    if response.status_code in (401, 407):
                        break
                    if (
                        not follow_redirects
                        or response.status_code not in _REDIRECT_STATUS_CODES
                        or hop >= _MAX_PINNED_REDIRECTS
                    ):
                        break
                    location = response.headers.get("location") or response.headers.get("Location")
                    if not location:
                        break
                    current_url = urljoin(current_url, location)
                    if response.status_code in {301, 302, 303} and current_method not in {
                        "GET",
                        "HEAD",
                    }:
                        current_method = "GET"
                        request_kwargs.pop("content", None)
                        request_kwargs.pop("data", None)
                        request_kwargs.pop("json", None)
                if response is None:
                    raise ProxyConnectionError("Pinned request produced no response")
                if response.status_code in (401, 407):
                    logger.error(
                        f"Proxy authentication failed: {masked_url}",
                        proxy_id=str(proxy.id),
                        status_code=response.status_code,
                    )
                    auth_message = (
                        "authentication required"
                        if response.status_code == 407
                        else "authentication failed"
                    )
                    raise ProxyAuthenticationError(
                        f"Proxy {auth_message} ({response.status_code}) for {masked_url}. "
                        "Please provide valid credentials (username and password)."
                    )
                return response

            return request_fn

        try:
            result = await self.orchestrator.execute_async(
                method=method,
                url=url,
                request_fn_factory=request_fn_factory,
                retry_policy=retry_policy,
                on_proxy_selected_async=on_proxy_selected_async,
            )
        except RateLimitExceededError:
            raise
        except ProxyAuthenticationError as exc:
            logger.error(
                f"Authentication error for proxy {active_proxy.id if active_proxy else 'unknown'}",
                proxy_id=str(active_proxy.id) if active_proxy else None,
                error_type=type(exc).__name__,
            )
            raise
        except NonRetryableError as e:
            if isinstance(e.__cause__, ProxyAuthenticationError):
                raise e.__cause__
            raise ProxyConnectionError(f"Request failed: {e}") from e
        except ProxyConnectionError as exc:
            logger.warning(
                f"Request failed after retries: {method} {redact_url(url)}",
                proxy_id=str(active_proxy.id) if active_proxy else None,
                error_type=type(exc).__name__,
            )
            raise
        except Exception as e:
            raise ProxyConnectionError(f"Request failed: {e}") from e

        logger.info(
            f"Request successful: {method} {redact_url(url)}",
            proxy_id=str(result.proxy.id),
            status_code=result.response.status_code,
            response_time_ms=result.response_time_ms,
        )
        self._last_used_proxy = result.proxy
        return result.response

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

    def _start_aggregation_timer(self) -> None:
        """Schedule the next metrics aggregation tick (every 5 minutes)."""

        def aggregate() -> None:
            try:
                if self._stop_event.is_set():
                    return
                try:
                    self.retry_metrics.aggregate_hourly()
                except Exception as exc:
                    logger.bind(error_type=type(exc).__name__).warning("Metrics aggregation failed")
            finally:
                current = threading.current_thread()
                with self._aggregation_lock:
                    if self._aggregation_timer is current:
                        self._aggregation_timer = None
                    if self._aggregation_thread is current:
                        self._aggregation_thread = None
                if not self._stop_event.is_set():
                    self._start_aggregation_timer()

        with self._aggregation_lock:
            if self._stop_event.is_set() or self._aggregation_timer is not None:
                return
            timer = threading.Timer(300.0, aggregate)
            timer.daemon = True
            timer.name = "proxywhirl-metrics-aggregation"
            self._aggregation_timer = timer
            # Expose timer as _aggregation_thread for existing teardown tests.
            self._aggregation_thread = timer
            try:
                timer.start()
            except BaseException:
                self._aggregation_timer = None
                self._aggregation_thread = None
                raise

    def _cancel_aggregation_timer(self, *, join: bool = True) -> None:
        """Cancel the scheduled timer and optionally join it outside destructors."""
        aggregation_lock = getattr(self, "_aggregation_lock", None)
        if aggregation_lock is None:
            timer = getattr(self, "_aggregation_timer", None)
            aggregation_thread = getattr(self, "_aggregation_thread", None)
            self._aggregation_timer = None
            self._aggregation_thread = None
        else:
            with aggregation_lock:
                timer = getattr(self, "_aggregation_timer", None)
                aggregation_thread = getattr(self, "_aggregation_thread", None)
                self._aggregation_timer = None
                self._aggregation_thread = None

        threads = {thread for thread in (timer, aggregation_thread) if thread is not None}
        for thread in threads:
            if isinstance(thread, threading.Timer):
                thread.cancel()
        if not join:
            return
        current = threading.current_thread()
        for thread in threads:
            if thread is not current and thread.is_alive():
                thread.join(timeout=5.0)

    def get_circuit_breaker_states(self) -> dict[str, CircuitBreakerSnapshot]:
        """
        Get circuit breaker states for all proxies.

        Returns:
            dict[str, CircuitBreakerSnapshot]: Mapping of proxy IDs to immutable snapshots.
        """
        return super().get_circuit_breaker_states()

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
