"""
Main proxy rotation implementation.
"""

from __future__ import annotations

import queue
import threading
import time
from collections.abc import Callable
from typing import TYPE_CHECKING, Any
from urllib.parse import quote

import httpx
from loguru import logger

from proxywhirl.circuit_breaker import CircuitBreaker
from proxywhirl.exceptions import (
    ProxyAuthenticationError,
    ProxyConnectionError,
    ProxyPoolEmptyError,
    RateLimitExceededError,
    RequestQueueFullError,
    redact_url,
)
from proxywhirl.logging_config import configure_logging
from proxywhirl.models import BootstrapConfig, Proxy, ProxyChain, ProxyPool
from proxywhirl.orchestration import (
    FailoverPolicy,
    ProxyRotationCallback,
    RequestOrchestration,
)
from proxywhirl.retry import NonRetryableError, RetryExecutor, RetryMetrics, RetryPolicy
from proxywhirl.rotator._bootstrap import bootstrap_pool_if_empty_sync
from proxywhirl.rotator._wiring import resolve_strategy
from proxywhirl.rotator.base import CircuitBreakerSnapshot, ProxyRotatorBase
from proxywhirl.rotator.client_pool import (
    LRUClientPool,  # noqa: F401 - re-export for backward compatibility
)
from proxywhirl.settings import ProxyConfiguration
from proxywhirl.strategies import RotationStrategy
from proxywhirl.utils import mask_proxy_url

if TYPE_CHECKING:
    from proxywhirl.rate_limiting import SyncRateLimiter


class _QueueRequestForProxyError(Exception):
    """Internal signal to queue a request after rate-limit selection."""

    def __init__(self, proxy: Proxy) -> None:
        self.proxy = proxy
        super().__init__(str(proxy.id))


_RESPONSE_TRUNCATED_EXTENSION = "proxywhirl_response_truncated"


def _request_with_bounded_response(
    client: httpx.Client,
    method: str,
    url: str,
    max_response_bytes: int,
    request_kwargs: dict[str, Any],
) -> httpx.Response:
    """Send a streaming request and retain at most ``max_response_bytes`` decoded bytes."""
    if max_response_bytes <= 0:
        raise ValueError("max_response_bytes must be positive")

    build_kwargs = dict(request_kwargs)
    send_kwargs: dict[str, Any] = {"stream": True}
    for option in ("auth", "follow_redirects"):
        if option in build_kwargs:
            send_kwargs[option] = build_kwargs.pop(option)

    request = client.build_request(method, url, **build_kwargs)
    streamed_response = client.send(request, **send_kwargs)
    content = bytearray()
    truncated = False
    chunk_size = min(65_536, max_response_bytes + 1)

    try:
        for chunk in streamed_response.iter_bytes(chunk_size=chunk_size):
            remaining = max_response_bytes + 1 - len(content)
            content.extend(chunk[:remaining])
            if len(content) > max_response_bytes:
                truncated = True
                break
    finally:
        streamed_response.close()

    extensions = dict(streamed_response.extensions)
    extensions[_RESPONSE_TRUNCATED_EXTENSION] = truncated
    return httpx.Response(
        streamed_response.status_code,
        headers=streamed_response.headers,
        content=bytes(content[:max_response_bytes]),
        request=streamed_response.request,
        extensions=extensions,
        history=list(streamed_response.history),
        default_encoding=streamed_response.default_encoding,
    )


class ProxyWhirl(ProxyRotatorBase):
    """
    Main class for proxy rotation with automatic failover.

    Provides HTTP methods (GET, POST, PUT, DELETE, PATCH) that automatically
    rotate through a pool of proxies, with intelligent failover on connection errors.

    Example::

        from proxywhirl import ProxyWhirl, Proxy

        rotator = ProxyWhirl()
        rotator.add_proxy("http://proxy1.example.com:8080")
        rotator.add_proxy("http://proxy2.example.com:8080")

        response = rotator.get("https://httpbin.org/ip")
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
        rate_limiter: SyncRateLimiter | None = None,
        bootstrap: BootstrapConfig | bool | None = None,
    ) -> None:
        """
        Initialize ProxyWhirl.

        Args:
            proxies: Initial list of proxies (optional)
            strategy: Rotation strategy instance or name string. Supported
                names: ``round-robin``, ``random``, ``weighted``,
                ``least-used``, ``performance-based``, ``session``,
                ``geo-targeted``, ``cost-aware``. Defaults to RoundRobinStrategy.
            config: Configuration settings (default: ProxyConfiguration())
            retry_policy: Retry policy configuration (default: RetryPolicy())
            failover_policy: Multi-proxy failover configuration (default from env, disabled).
            proxy_rotation_callback: Optional callback invoked on proxy rotation.
            rate_limiter: Synchronous rate limiter for controlling request rates (optional)
            bootstrap: Bootstrap configuration for lazy proxy fetching.
                      False disables auto-bootstrap (for manual proxy management).
                      True or None uses default BootstrapConfig.
        """
        self.pool = ProxyPool(name="default", proxies=proxies or [])
        self.chains: list[ProxyChain] = []  # Track registered proxy chains

        self.strategy = resolve_strategy(strategy)

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
        self.failover_policy = failover_policy or FailoverPolicy.from_env()
        self.proxy_rotation_callback = proxy_rotation_callback
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

        # Bootstrap configuration (coerce bool/None to BootstrapConfig)
        if bootstrap is False:
            self._bootstrap_config = BootstrapConfig(enabled=False)
        elif isinstance(bootstrap, BootstrapConfig):
            self._bootstrap_config = bootstrap
        else:
            self._bootstrap_config = BootstrapConfig()

        # Initialize strategy lock for atomic strategy swapping
        self._strategy_lock = threading.RLock()
        self._bootstrap_lock = threading.Lock()
        self._bootstrap_attempted = False
        self._bootstrap_error_message: str | None = None

        # Periodic metrics aggregation belongs to the explicit context lifetime.
        self._aggregation_stop_event = threading.Event()
        self._aggregation_lock = threading.Lock()
        self._aggregation_timer: threading.Timer | None = None

        # Configure logging
        if hasattr(logger, "_core") and not logger._core.handlers:
            configure_logging(
                level=self.config.log_level,
                format=self.config.log_format,
                redact_secrets=self.config.log_redact_credentials,
            )

    def __enter__(self) -> ProxyWhirl:
        """Enter context manager."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.Client(
                timeout=self.config.timeout,
                verify=self.config.verify_ssl,
                follow_redirects=self.config.follow_redirects,
                limits=httpx.Limits(
                    max_connections=self.config.pool_connections,
                    max_keepalive_connections=self.config.pool_max_keepalive,
                ),
                http2=True,
            )
        self._aggregation_stop_event.clear()
        if self._aggregation_timer is None:
            self._start_aggregation_timer()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager."""
        self.close()

    def close(self) -> None:
        """Close owned clients and background work; safe to call repeatedly."""
        stop_event = getattr(self, "_aggregation_stop_event", None)
        if stop_event is not None:
            stop_event.set()

        self._cancel_aggregation_timer()

        client = getattr(self, "_client", None)
        if client is not None:
            self._client = None
            try:
                client.close()
            except Exception as exc:
                logger.bind(error_type=type(exc).__name__).warning(
                    "Error closing shared HTTP client"
                )

        self._close_all_clients()

    def __del__(self) -> None:
        """Destructor to ensure clients are closed."""
        try:
            self.close()
        except Exception:
            # Destructors may run after interpreter/module teardown.
            pass

    def _close_all_clients(self) -> None:
        """Close all pooled clients and clear the pool."""
        client_pool = getattr(self, "_client_pool", None)
        if client_pool is not None:
            client_pool.clear()

    def add_proxy(self, proxy: Proxy | str) -> None:
        """
        Add a proxy to the rotation pool.

        Adds a new proxy to the pool for use in automatic rotation.
        Proxies can be specified as Proxy instances or URL strings.
        A circuit breaker is automatically initialized for the proxy.

        Args:
            proxy : Proxy | str
                Proxy instance or proxy URL string (e.g., "http://proxy.example.com:8080"
                or "http://user:pass@proxy.example.com:8080").

        Returns:
            None

        Raises:
            ValueError
                If proxy URL format is invalid.

        Example:
            >>> rotator = ProxyWhirl()
            >>> # Add proxy as URL string
            >>> rotator.add_proxy("http://proxy.example.com:8080")
            >>> # Add proxy with credentials
            >>> rotator.add_proxy("http://user:pass@proxy.example.com:8080")
            >>> # Add proxy as Proxy instance
            >>> from proxywhirl import Proxy
            >>> proxy = Proxy(url="socks5://proxy.example.com:1080")
            >>> rotator.add_proxy(proxy)

        Note:
            - URL strings are automatically parsed into Proxy instances
            - Circuit breaker initialized in CLOSED state (FR-021)
            - Credentials are masked in log output
            - Proxy ID is automatically assigned as UUID
        """
        if isinstance(proxy, str):
            from proxywhirl.utils import create_proxy_from_url

            proxy = create_proxy_from_url(proxy)

        if self.pool.has_proxy_url(proxy.url):
            masked_url = mask_proxy_url(proxy.url)
            logger.debug(f"Skipped duplicate proxy: {masked_url}", proxy_id=str(proxy.id))
            return

        self.pool.add_proxy(proxy)

        # Initialize circuit breaker for new proxy (starts CLOSED per FR-021)
        self.circuit_breakers[str(proxy.id)] = CircuitBreaker(proxy_id=str(proxy.id))

        # Mask credentials in log output
        masked_url = mask_proxy_url(proxy.url)
        logger.info(f"Added proxy to pool: {masked_url}", proxy_id=str(proxy.id))

    def remove_proxy(self, proxy_id: str) -> None:
        """
        Remove a proxy from the rotation pool.

        Removes a proxy by its UUID and cleans up associated resources
        (circuit breaker, pooled HTTP clients). This is safe to call
        while requests are in flight - they will complete with their
        current proxy before it's removed.

        Args:
            proxy_id : str
                UUID of the proxy to remove (e.g., "550e8400-e29b-41d4-a716-446655440000").

        Returns:
            None

        Raises:
            ValueError
                If proxy_id is not a valid UUID format.

        Example:
            >>> rotator = ProxyWhirl()
            >>> rotator.add_proxy("http://proxy1.example.com:8080")
            >>> # Get the proxy ID (usually from pool)
            >>> proxies = rotator.get_all_proxies()
            >>> proxy_id = str(proxies[0].id)
            >>> rotator.remove_proxy(proxy_id)

        Note:
            - Closes pooled HTTP clients for this proxy
            - Removes circuit breaker to prevent memory leaks
            - Thread-safe: safe to call during active requests
            - Does not raise error if proxy_id not found
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

    def _bootstrap_pool_if_empty(self) -> int:
        """Bootstrap pool from built-in sources when empty."""
        return bootstrap_pool_if_empty_sync(
            pool=self.pool,
            add_proxy=self.add_proxy,
            config=self._bootstrap_config,
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

            # If pool is still empty after bootstrap (e.g., bootstrap disabled)
            if self.pool.size == 0:
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

    def get_proxy(self) -> Proxy:
        """
        Get the next proxy from the pool using the rotation strategy.

        Triggers the same one-time lazy bootstrap as request execution when the
        pool is empty (parity with AsyncProxyWhirl.get_proxy).

        Returns:
            Next proxy to use

        Raises:
            ProxyPoolEmptyError: If bootstrap fails or no healthy proxies available
        """
        self._ensure_bootstrap_for_empty_pool()
        return self._select_proxy_with_circuit_breaker()

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

        # Add to pool (skip circuit breaker when duplicate URL is ignored)
        already_present = self.pool.has_proxy_url(entry_proxy.url)
        self.pool.add_proxy(entry_proxy)

        if not already_present:
            self.circuit_breakers[str(entry_proxy.id)] = CircuitBreaker(
                proxy_id=str(entry_proxy.id)
            )

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
                except Exception as exc:
                    logger.bind(error_type=type(exc).__name__).warning(
                        "Could not remove entry proxy"
                    )

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
            strategy: New strategy instance or name string. Supported
                names: ``round-robin``, ``random``, ``weighted``,
                ``least-used``, ``performance-based``, ``session``,
                ``geo-targeted``, ``cost-aware``.
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

        start_time = time.perf_counter()

        # Parse strategy string or use provided instance
        new_strategy = resolve_strategy(strategy) if isinstance(strategy, str) else strategy

        # Store old strategy for logging
        old_strategy_name = self.strategy.__class__.__name__
        new_strategy_name = new_strategy.__class__.__name__

        if atomic:
            # Use a lock to ensure atomic swap
            with self._strategy_lock:
                self.strategy = new_strategy
                self.orchestrator.strategy = new_strategy
        else:
            # Direct assignment (faster but less safe)
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

    def get_pool_stats(self) -> dict[str, Any]:
        """
        Get statistics about the proxy pool.

        Returns:
            dict[str, Any]: Pool statistics including total_proxies, healthy_proxies,
            unhealthy_proxies, dead_proxies, total_requests, total_successes,
            total_failures, and average_success_rate.
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
            dict[str, Any]: All stats from get_pool_stats() plus source_breakdown
            mapping source names to proxy counts.
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

        # Clean up circuit breakers and pooled clients for removed proxies
        for proxy_id in removed_proxy_ids:
            self._client_pool.remove(proxy_id)
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
            http2=True,
        )

        # Publish atomically so racing creators converge on one live client.
        canonical_client = self._client_pool.put_if_absent(proxy_id, client)

        if canonical_client is client:
            logger.debug(
                "Created new pooled client for proxy",
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

    def _make_request(
        self,
        method: str,
        url: str,
        retry_policy: RetryPolicy | None = None,
        _response_body_limit_bytes: int | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Make HTTP request with automatic proxy rotation, retry, and circuit breakers.

        Args:
            method: HTTP method
            url: URL to request
            retry_policy: Optional per-request retry policy override
            _response_body_limit_bytes: Internal decoded-response byte cap for API requests
            **kwargs: Additional request parameters

        Returns:
            HTTP response

        Raises:
            ProxyPoolEmptyError: If no healthy proxies available
            ProxyConnectionError: If all retry attempts fail
            RequestQueueFullError: If queue is full and cannot accept request
        """
        self._ensure_bootstrap_for_empty_pool()
        active_proxy: Proxy | None = None
        safe_target_url = redact_url(url)

        def on_proxy_selected(proxy: Proxy) -> None:
            nonlocal active_proxy
            active_proxy = proxy
            if self.rate_limiter is None:
                return
            proxy_id = str(proxy.id)
            if self.rate_limiter.check_limit(proxy_id):
                return
            masked_url = mask_proxy_url(str(proxy.url))
            logger.warning(
                f"Rate limit exceeded for proxy {proxy_id}",
                proxy_id=proxy_id,
                proxy_url=masked_url,
            )
            if self.config.queue_enabled and self._request_queue is not None:
                raise _QueueRequestForProxyError(proxy)
            raise RateLimitExceededError(
                f"Rate limit exceeded for proxy {proxy_id}. "
                "Please wait before making more requests."
            )

        def request_fn_factory(proxy: Proxy) -> Callable[[], httpx.Response]:
            proxy_dict = self._get_proxy_dict(proxy)
            masked_url = mask_proxy_url(str(proxy.url))
            logger.info(
                f"Making {method} request to {safe_target_url}",
                proxy_id=str(proxy.id),
                proxy_url=masked_url,
            )
            client = self._get_or_create_client(proxy, proxy_dict)

            def request_fn() -> httpx.Response:
                if _response_body_limit_bytes is None:
                    response = client.request(method, url, **kwargs)
                else:
                    response = _request_with_bounded_response(
                        client,
                        method,
                        url,
                        _response_body_limit_bytes,
                        kwargs,
                    )
                if response.status_code in (401, 407):
                    logger.error(
                        f"Proxy authentication failed: {masked_url}",
                        proxy_id=str(proxy.id),
                        status_code=response.status_code,
                    )
                    raise ProxyAuthenticationError(
                        f"Proxy authentication failed ({response.status_code}) for {masked_url}. "
                        "Please provide valid credentials (username and password)."
                    )
                return response

            return request_fn

        try:
            result = self.orchestrator.execute_sync(
                method=method,
                url=url,
                request_fn_factory=request_fn_factory,
                retry_policy=retry_policy,
                on_proxy_selected=on_proxy_selected,
            )
        except _QueueRequestForProxyError as queue_exc:
            return self._queue_request(
                method,
                url,
                queue_exc.proxy,
                retry_policy,
                _response_body_limit_bytes,
                **kwargs,
            )
        except ProxyPoolEmptyError:
            logger.error("No healthy proxies available or all circuit breakers open")
            raise
        except RateLimitExceededError:
            raise
        except ProxyAuthenticationError:
            logger.error(
                f"Authentication error for proxy {active_proxy.id if active_proxy else 'unknown'}",
                proxy_id=str(active_proxy.id) if active_proxy else None,
            )
            raise
        except NonRetryableError as e:
            if isinstance(e.__cause__, ProxyAuthenticationError):
                raise e.__cause__
            raise ProxyConnectionError(f"Request failed: {e}") from e
        except ProxyConnectionError:
            logger.warning(
                f"Request failed after retries: {method} {safe_target_url}",
                proxy_id=str(active_proxy.id) if active_proxy else None,
            )
            raise
        except Exception as e:
            raise ProxyConnectionError(f"Request failed: {e}") from e

        logger.info(
            f"Request successful: {method} {safe_target_url}",
            proxy_id=str(result.proxy.id),
            status_code=result.response.status_code,
            response_time_ms=result.response_time_ms,
        )
        self._last_used_proxy = result.proxy
        return result.response

    def _queue_request(
        self,
        method: str,
        url: str,
        proxy: Proxy,
        retry_policy: RetryPolicy | None = None,
        _response_body_limit_bytes: int | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Queue a request when rate limited.

        Args:
            method: HTTP method
            url: URL to request
            proxy: Proxy to use
            retry_policy: Optional retry policy
            _response_body_limit_bytes: Internal decoded-response byte cap for API requests
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
            "response_body_limit_bytes": _response_body_limit_bytes,
            "kwargs": kwargs,
        }

        # Queue the request (blocking put)
        try:
            # Use put_nowait to avoid blocking (raises QueueFull if full)
            self._request_queue.put_nowait(request_data)

            logger.info(
                "Request queued",
                method=method,
                url=redact_url(url),
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
        response_body_limit_bytes = request_data["response_body_limit_bytes"]
        kwargs = request_data["kwargs"]

        logger.info(
            "Processing queued request",
            method=method,
            url=redact_url(url),
            remaining_queue_size=self._request_queue.qsize(),
        )

        masked_url = mask_proxy_url(str(proxy.url))

        def request_fn_factory(selected_proxy: Proxy) -> Callable[[], httpx.Response]:
            proxy_dict = self._get_proxy_dict(selected_proxy)
            client = self._get_or_create_client(selected_proxy, proxy_dict)

            def request_fn() -> httpx.Response:
                if response_body_limit_bytes is None:
                    response = client.request(method, url, **kwargs)
                else:
                    response = _request_with_bounded_response(
                        client,
                        method,
                        url,
                        response_body_limit_bytes,
                        kwargs,
                    )
                if response.status_code in (401, 407):
                    logger.error(
                        f"Proxy authentication failed: {masked_url}",
                        proxy_id=str(selected_proxy.id),
                        status_code=response.status_code,
                    )
                    raise ProxyAuthenticationError(
                        f"Proxy authentication failed ({response.status_code}) for {masked_url}. "
                        "Please provide valid credentials (username and password)."
                    )
                return response

            return request_fn

        try:
            result = self.orchestrator.execute_sync(
                method=method,
                url=url,
                request_fn_factory=request_fn_factory,
                retry_policy=retry_policy,
                pinned_proxy=proxy,
            )
        except ProxyAuthenticationError:
            raise
        except NonRetryableError as e:
            raise ProxyConnectionError(f"Queued request failed: {e}") from e
        except Exception as e:
            logger.warning(
                f"Queued request failed: {method} {redact_url(url)}",
                proxy_id=str(proxy.id),
            )
            raise ProxyConnectionError(f"Queued request failed: {e}") from e

        logger.info(
            f"Queued request successful: {method} {redact_url(url)}",
            proxy_id=str(result.proxy.id),
            status_code=result.response.status_code,
            response_time_ms=result.response_time_ms,
        )
        self._last_used_proxy = result.proxy
        return result.response

    def get(self, url: str, **kwargs: Any) -> httpx.Response:
        """
        Make HTTP GET request through rotating proxy.

        Automatically selects a proxy from the pool, rotates on failure,
        and retries according to the retry policy.

        Args:
            url : str
                The target URL to request.
            **kwargs : dict
                Additional httpx client arguments (headers, params, timeout, etc.).

        Returns:
            httpx.Response
                HTTP response from the target server.

        Raises:
            ProxyPoolEmptyError
                If no healthy proxies are available.
            ProxyConnectionError
                If the request fails after all retry attempts.
            ProxyAuthenticationError
                If proxy authentication fails (401/407).
            RequestQueueFullError
                If request queue is full and queuing is enabled.

        Example:
            >>> rotator = ProxyWhirl()
            >>> rotator.add_proxy("http://proxy.example.com:8080")
            >>> response = rotator.get("https://httpbin.org/get")
            >>> print(response.status_code)  # 200
            >>> print(response.json())

        Note:
            - Supports all httpx parameters (headers, params, timeout, etc.)
            - Credentials are masked in log output for security
            - Response times are tracked for performance-based strategies
        """
        return self._make_request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> httpx.Response:
        """
        Make HTTP POST request through rotating proxy.

        Automatically selects a proxy from the pool, rotates on failure,
        and retries according to the retry policy.

        Args:
            url : str
                The target URL to request.
            **kwargs : dict
                Additional httpx arguments (data, json, headers, etc.).

        Returns:
            httpx.Response
                HTTP response from the target server.

        Raises:
            ProxyPoolEmptyError
                If no healthy proxies are available.
            ProxyConnectionError
                If the request fails after all retry attempts.
            ProxyAuthenticationError
                If proxy authentication fails.
            RequestQueueFullError
                If request queue is full and queuing is enabled.

        Example:
            >>> rotator = ProxyWhirl()
            >>> rotator.add_proxy("http://proxy.example.com:8080")
            >>> response = rotator.post(
            ...     "https://httpbin.org/post",
            ...     json={"key": "value"},
            ...     headers={"Content-Type": "application/json"}
            ... )
            >>> print(response.status_code)  # 200

        Note:
            - Supports data, json, files, and other POST parameters
            - Request body is included in retry attempts
            - Timeouts respect configuration settings
        """
        return self._make_request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> httpx.Response:
        """
        Make HTTP PUT request through rotating proxy.

        Automatically selects a proxy from the pool, rotates on failure,
        and retries according to the retry policy.

        Args:
            url : str
                The target URL to request.
            **kwargs : dict
                Additional httpx arguments (data, json, headers, etc.).

        Returns:
            httpx.Response
                HTTP response from the target server.

        Raises:
            ProxyPoolEmptyError
                If no healthy proxies are available.
            ProxyConnectionError
                If the request fails after all retry attempts.
            ProxyAuthenticationError
                If proxy authentication fails.
            RequestQueueFullError
                If request queue is full and queuing is enabled.

        Example:
            >>> rotator = ProxyWhirl()
            >>> response = rotator.put(
            ...     "https://api.example.com/resource/123",
            ...     json={"name": "updated"}
            ... )
            >>> print(response.status_code)  # 200
        """
        return self._make_request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> httpx.Response:
        """
        Make HTTP DELETE request through rotating proxy.

        Automatically selects a proxy from the pool, rotates on failure,
        and retries according to the retry policy.

        Args:
            url : str
                The target URL to request.
            **kwargs : dict
                Additional httpx arguments (headers, params, etc.).

        Returns:
            httpx.Response
                HTTP response from the target server.

        Raises:
            ProxyPoolEmptyError
                If no healthy proxies are available.
            ProxyConnectionError
                If the request fails after all retry attempts.
            ProxyAuthenticationError
                If proxy authentication fails.
            RequestQueueFullError
                If request queue is full and queuing is enabled.

        Example:
            >>> rotator = ProxyWhirl()
            >>> response = rotator.delete("https://api.example.com/resource/123")
            >>> print(response.status_code)  # 204
        """
        return self._make_request("DELETE", url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> httpx.Response:
        """
        Make HTTP PATCH request through rotating proxy.

        Automatically selects a proxy from the pool, rotates on failure,
        and retries according to the retry policy.

        Args:
            url : str
                The target URL to request.
            **kwargs : dict
                Additional httpx arguments (data, json, headers, etc.).

        Returns:
            httpx.Response
                HTTP response from the target server.

        Raises:
            ProxyPoolEmptyError
                If no healthy proxies are available.
            ProxyConnectionError
                If the request fails after all retry attempts.
            ProxyAuthenticationError
                If proxy authentication fails.
            RequestQueueFullError
                If request queue is full and queuing is enabled.

        Example:
            >>> rotator = ProxyWhirl()
            >>> response = rotator.patch(
            ...     "https://api.example.com/resource/123",
            ...     json={"status": "active"}
            ... )
            >>> print(response.status_code)  # 200
        """
        return self._make_request("PATCH", url, **kwargs)

    def head(self, url: str, **kwargs: Any) -> httpx.Response:
        """
        Make HTTP HEAD request through rotating proxy.

        HEAD request is identical to GET but without response body.
        Useful for checking resource existence and headers only.

        Args:
            url : str
                The target URL to request.
            **kwargs : dict
                Additional httpx arguments (headers, params, etc.).

        Returns:
            httpx.Response
                HTTP response headers (no body).

        Raises:
            ProxyPoolEmptyError
                If no healthy proxies are available.
            ProxyConnectionError
                If the request fails after all retry attempts.
            ProxyAuthenticationError
                If proxy authentication fails.
            RequestQueueFullError
                If request queue is full and queuing is enabled.

        Example:
            >>> rotator = ProxyWhirl()
            >>> response = rotator.head("https://example.com/resource")
            >>> print(response.headers.get("content-type"))
            >>> print(response.headers.get("content-length"))
        """
        return self._make_request("HEAD", url, **kwargs)

    def options(self, url: str, **kwargs: Any) -> httpx.Response:
        """
        Make HTTP OPTIONS request through rotating proxy.

        Retrieve communication options available for a resource.
        Typically used to discover allowed HTTP methods.

        Args:
            url : str
                The target URL to request.
            **kwargs : dict
                Additional httpx arguments (headers, params, etc.).

        Returns:
            httpx.Response
                HTTP response with Allow header listing supported methods.

        Raises:
            ProxyPoolEmptyError
                If no healthy proxies are available.
            ProxyConnectionError
                If the request fails after all retry attempts.
            ProxyAuthenticationError
                If proxy authentication fails.
            RequestQueueFullError
                If request queue is full and queuing is enabled.

        Example:
            >>> rotator = ProxyWhirl()
            >>> response = rotator.options("https://api.example.com/resource")
            >>> print(response.headers.get("allow"))  # GET, POST, PUT, DELETE, ...
        """
        return self._make_request("OPTIONS", url, **kwargs)

    def _start_aggregation_timer(self) -> None:
        """Start periodic metrics aggregation timer (every 5 minutes)."""

        stop_event = getattr(self, "_aggregation_stop_event", None)
        aggregation_lock = getattr(self, "_aggregation_lock", None)
        if stop_event is None or aggregation_lock is None:
            return

        def aggregate() -> None:
            try:
                if stop_event.is_set():
                    return
                try:
                    self.retry_metrics.aggregate_hourly()
                except Exception as exc:
                    logger.bind(error_type=type(exc).__name__).warning("Metrics aggregation failed")
            finally:
                current = threading.current_thread()
                with aggregation_lock:
                    if self._aggregation_timer is current:
                        self._aggregation_timer = None
                if not stop_event.is_set():
                    self._start_aggregation_timer()

        with aggregation_lock:
            if stop_event.is_set() or self._aggregation_timer is not None:
                return
            timer = threading.Timer(300.0, aggregate)  # 5 minutes
            timer.daemon = True
            self._aggregation_timer = timer
            try:
                timer.start()
            except BaseException:
                self._aggregation_timer = None
                raise

    def _cancel_aggregation_timer(self) -> None:
        """Cancel and join the current timer without ever joining this thread."""
        aggregation_lock = getattr(self, "_aggregation_lock", None)
        if aggregation_lock is None:
            timer = getattr(self, "_aggregation_timer", None)
            self._aggregation_timer = None
        else:
            with aggregation_lock:
                timer = getattr(self, "_aggregation_timer", None)
                self._aggregation_timer = None

        if timer is None:
            return
        timer.cancel()
        if timer is not threading.current_thread() and timer.is_alive():
            timer.join(timeout=5.0)

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

    def get_queue_stats(self) -> dict[str, Any]:
        """
        Get statistics about the request queue.

        Returns:
            dict[str, Any]: Queue statistics including enabled, size, max_size,
            is_full, and is_empty.
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
