"""Proxy validation types and ProxyValidator."""

from __future__ import annotations

import asyncio
import hashlib
import json
import time
from collections import OrderedDict
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, NamedTuple
from urllib.parse import urlparse

import httpx
from loguru import logger

from proxywhirl.exceptions import ProxyFetchError, ProxyValidationError
from proxywhirl.fetchers.shared import (
    DEFAULT_ANONYMITY_TEST_URL,
    SOCKS_AVAILABLE,
    AsyncProxyTransport,
)
from proxywhirl.settings import TLSSettings
from proxywhirl.utils import mask_proxy_url

if TYPE_CHECKING:
    from proxywhirl.models import ValidationLevel


def _validate_proxy_url_safety_compat(url: str, *args, **kwargs):
    """Resolve validate_proxy_url_safety via package facade (patch-compatible)."""
    from proxywhirl.fetchers import validate_proxy_url_safety

    return validate_proxy_url_safety(url, *args, **kwargs)


class ValidationResult(NamedTuple):
    """Result of proxy validation with timing metrics."""

    is_valid: bool
    response_time_ms: float | None  # None if validation failed before timing

    def __bool__(self) -> bool:
        """Allow ValidationResult to be used in boolean context."""
        return self.is_valid


def _get_tls_verify() -> bool | str:
    """Return TLS verification setting for httpx clients.

    Reads ``TLSSettings.ca_bundle``. If set, uses the specified CA bundle path.
    Otherwise defaults to ``True``.
    """
    ca_bundle = TLSSettings().ca_bundle
    return str(ca_bundle) if ca_bundle else True


class ProxyValidator:
    """Validate proxy connectivity with detailed metrics and multiple test endpoints.

    Validates proxies by attempting actual HTTP/HTTPS requests through them.
    Includes result caching, concurrent validation limits, and multi-endpoint
    fallback for robust testing. Supports HTTP and SOCKS proxies.

    Attributes:
        timeout: HTTP request timeout in seconds
        level: Validation level (BASIC, STANDARD, FULL)
        concurrency: Maximum concurrent validations
        TEST_URLS: List of fast HTTP endpoints for testing
        HTTPS_TEST_URLS: List of HTTPS endpoints for protocol testing
    """

    # Multiple test URLs to avoid single-point bottleneck and rate limiting
    TEST_URLS = [
        "http://www.gstatic.com/generate_204",  # Google - fast, no rate limit
        "http://cp.cloudflare.com/generate_204",  # Cloudflare - very fast
        "http://connectivitycheck.android.com/generate_204",  # Android check
        "http://www.msftconnecttest.com/connecttest.txt",  # Microsoft
    ]

    # HTTPS-specific test URLs for validating HTTPS proxy connectivity.
    # Multiple endpoints for fallback — succeed on any.
    HTTPS_TEST_URLS = [
        "https://www.gstatic.com/generate_204",  # Google HTTPS (204)
        "https://cp.cloudflare.com/generate_204",  # Cloudflare HTTPS (204)
        "https://connectivity-check.ubuntu.com/",  # Ubuntu (204)
        "https://detectportal.firefox.com/canonical.html",  # Firefox (200)
    ]

    def __init__(
        self,
        timeout: float = 5.0,
        test_url: str | None = None,
        level: ValidationLevel | None = None,
        concurrency: int = 50,
        cache_ttl_seconds: int = 3600,
        *,
        anonymity_test_url: str | None = None,
    ) -> None:
        """
        Initialize proxy validator with configurable endpoints and validation level.

        Creates a new proxy validator with support for HTTP/HTTPS and SOCKS proxies.
        Multiple test endpoints are available to work around rate limiting.

        Args:
            timeout : float
                Connection timeout in seconds (default: 5.0).
            test_url : str | None
                Custom URL for proxy testing. If None, rotates between
                fast endpoints (Google, Cloudflare, etc.). Default: None.
            level : ValidationLevel | None
                Validation level: BASIC (TCP only), STANDARD (HTTP request),
                or FULL (detailed checks). Default: STANDARD.
            concurrency : int
                Maximum concurrent validations (default: 50). Uses asyncio.Semaphore.
            cache_ttl_seconds : int
                TTL for validation result caching in seconds (default: 3600 / 1 hour).
            anonymity_test_url : str | None
                Keyword-only endpoint used by FULL anonymity validation. If None,
                uses the configured public-IP echo endpoint.

        Returns:
            None

        Example:
            >>> validator = ProxyValidator(timeout=10.0, level=ValidationLevel.FULL)
            >>> async with validator:
            ...     result = await validator.validate({"url": "http://proxy.example.com:8080"})
            ...     print(result.is_valid)

        Note:
            - Result caching reduces redundant validations
            - Concurrent validations limited to prevent resource exhaustion
            - SOCKS support requires httpx-socks library
        """
        from proxywhirl.models import ValidationLevel

        if concurrency < 1:
            raise ValueError("concurrency must be >= 1")

        self.timeout = timeout
        self._custom_test_url = test_url  # None means rotate
        self._anonymity_test_url = anonymity_test_url or DEFAULT_ANONYMITY_TEST_URL
        self._test_url_index = 0
        self._https_test_url_index = 0
        self.level = level or ValidationLevel.STANDARD
        self.concurrency = concurrency
        self._client: httpx.AsyncClient | None = None
        self._socks_client: httpx.AsyncClient | None = None
        self._socks_clients: OrderedDict[str, httpx.AsyncClient] = OrderedDict()
        self._socks_client_lock = asyncio.Lock()
        # Match the rotator client-pool ceiling while allowing smaller validators
        # to retain no more clients than they can use concurrently.
        self._max_socks_clients = min(concurrency, 100)

        # Validation result cache with TTL
        self._validation_cache: dict[str, tuple[ValidationResult, float]] = {}
        self._cache_ttl_seconds = cache_ttl_seconds

    @property
    def test_url(self) -> str:
        """Get current test URL, rotating through multiple endpoints."""
        if self._custom_test_url:
            return self._custom_test_url
        # Rotate through test URLs to distribute load
        url = self.TEST_URLS[self._test_url_index % len(self.TEST_URLS)]
        self._test_url_index += 1
        return url

    def _get_test_url_for_protocol(self, protocol: str | None) -> str:
        """Get a test URL appropriate for the proxy's protocol.

        HTTPS proxies are validated against HTTPS endpoints to confirm
        they actually support TLS tunneling.
        """
        if self._custom_test_url:
            return self._custom_test_url
        if protocol == "https":
            url = self.HTTPS_TEST_URLS[self._https_test_url_index % len(self.HTTPS_TEST_URLS)]
            self._https_test_url_index += 1
            return url
        return self.test_url

    def _peek_test_url_for_protocol(self, protocol: str | None) -> str:
        """Get the next validation target without advancing URL rotation."""
        if self._custom_test_url:
            return self._custom_test_url
        if protocol == "https":
            return self.HTTPS_TEST_URLS[self._https_test_url_index % len(self.HTTPS_TEST_URLS)]
        return self.TEST_URLS[self._test_url_index % len(self.TEST_URLS)]

    @staticmethod
    def _get_effective_proxy_protocol(proxy: dict[str, Any], proxy_url: str | None) -> str | None:
        """Resolve the protocol that controls validation target and cache partitioning."""
        protocol = proxy.get("protocol")
        if isinstance(protocol, str) and protocol.strip():
            return protocol.strip().lower()

        if not proxy_url:
            return None

        parsed = urlparse(proxy_url)
        return parsed.scheme.lower() if parsed.scheme else None

    async def _get_client(self) -> httpx.AsyncClient:
        """
        Get or create the shared HTTP client.

        Returns:
            Shared httpx.AsyncClient instance
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                verify=_get_tls_verify(),
                limits=httpx.Limits(max_connections=1000, max_keepalive_connections=100),
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                },
            )
        return self._client

    async def _get_socks_client(self, proxy_url: str) -> httpx.AsyncClient:
        """
        Get or create a SOCKS client scoped to the exact proxy URL.

        Args:
            proxy_url: SOCKS proxy URL

        Returns:
            Reusable httpx.AsyncClient configured only for this URL and credentials

        Raises:
            ProxyValidationError: If httpx-socks is not installed
        """
        if not SOCKS_AVAILABLE:
            logger.warning(
                "SOCKS proxy support requires httpx-socks library. "
                "Install with: uv sync or add httpx-socks to your dependencies"
            )
            raise ProxyValidationError(
                "SOCKS proxy support requires httpx-socks library. "
                "Install with: uv sync or add httpx-socks to your dependencies"
            )

        if AsyncProxyTransport is None:
            logger.error("SOCKS_AVAILABLE is True but AsyncProxyTransport is None")
            raise ProxyValidationError(
                "SOCKS proxy transport is unavailable. Please reinstall httpx-socks."
            )

        # Hash the full URL so credentials participate in client isolation
        # without being retained as dictionary keys in process state.
        client_key = hashlib.sha256(proxy_url.encode()).hexdigest()
        async with self._socks_client_lock:
            client = self._socks_clients.get(client_key)
            if client is not None:
                self._socks_clients.move_to_end(client_key)
            else:
                if len(self._socks_clients) >= self._max_socks_clients:
                    _, evicted_client = self._socks_clients.popitem(last=False)
                    if self._socks_client is evicted_client:
                        self._socks_client = None
                    try:
                        await evicted_client.aclose()
                    except asyncio.CancelledError:
                        raise
                    except Exception as exc:
                        logger.bind(error_type=type(exc).__name__).warning(
                            "Error closing evicted SOCKS validation client"
                        )

                transport = AsyncProxyTransport.from_url(proxy_url)
                client = httpx.AsyncClient(
                    transport=transport,
                    timeout=self.timeout,
                    verify=_get_tls_verify(),
                    limits=httpx.Limits(max_connections=1000, max_keepalive_connections=100),
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    },
                )
                self._socks_clients[client_key] = client

            # Retain the legacy single-client attribute for compatibility with
            # callers that inspect it, without using it for cross-proxy reuse.
            self._socks_client = client
            return client

    async def close(self) -> None:
        """Close all client connections and cleanup resources."""
        async with self._socks_client_lock:
            clients: list[httpx.AsyncClient] = []
            if self._client is not None:
                clients.append(self._client)
            clients.extend(self._socks_clients.values())
            if self._socks_client is not None and not any(
                client is self._socks_client for client in clients
            ):
                clients.append(self._socks_client)

            self._client = None
            self._socks_client = None
            self._socks_clients.clear()
        if not clients:
            return

        async def close_clients() -> list[BaseException | None]:
            results = await asyncio.gather(
                *(client.aclose() for client in clients),
                return_exceptions=True,
            )
            return [result if isinstance(result, BaseException) else None for result in results]

        cleanup_task = asyncio.create_task(close_clients())
        externally_cancelled = False
        try:
            results = await asyncio.shield(cleanup_task)
        except asyncio.CancelledError:
            externally_cancelled = True
            results = await cleanup_task

        if externally_cancelled:
            raise asyncio.CancelledError
        for result in results:
            if result is not None:
                raise result

    async def __aenter__(self) -> ProxyValidator:
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()

    def _get_cache_key(self, proxy: dict[str, Any], target_url: str | None = None) -> str:
        """Generate cache key for a proxy.

        Args:
            proxy: Proxy dictionary with 'url' key
            target_url: Effective URL used to validate proxy connectivity

        Returns:
            Cache key string (hash of proxy URL, protocol, and validation target)
        """
        proxy_url = str(proxy.get("url") or "")
        protocol = self._get_effective_proxy_protocol(proxy, proxy_url)
        cache_payload = json.dumps(
            {
                "protocol": protocol or "",
                "target_url": target_url or "",
                "url": proxy_url,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.md5(cache_payload.encode(), usedforsecurity=False).hexdigest()

    def _get_cached_result(
        self,
        proxy: dict[str, Any],
        target_url: str | None = None,
    ) -> ValidationResult | None:
        """Get validation result from cache if not expired.

        Args:
            proxy: Proxy dictionary to check cache for
            target_url: Effective URL used to validate proxy connectivity

        Returns:
            ValidationResult if cached and not expired, None otherwise
        """
        cache_key = self._get_cache_key(proxy, target_url)
        if cache_key in self._validation_cache:
            result, timestamp = self._validation_cache[cache_key]
            if time.time() - timestamp < self._cache_ttl_seconds:
                logger.debug(f"Validation cache hit for {proxy.get('url')}")
                return result
            else:
                # Cache expired - remove it
                del self._validation_cache[cache_key]
        return None

    def _set_cached_result(
        self,
        proxy: dict[str, Any],
        result: ValidationResult,
        target_url: str | None = None,
    ) -> None:
        """Cache a validation result.

        Args:
            proxy: Proxy dictionary that was validated
            result: Validation result to cache
            target_url: Effective URL used to validate proxy connectivity
        """
        cache_key = self._get_cache_key(proxy, target_url)
        self._validation_cache[cache_key] = (result, time.time())

    async def _validate_tcp_connectivity(self, host: str, port: int) -> bool:
        """
        Validate TCP connectivity to proxy.

        Args:
            host: Proxy hostname or IP address
            port: Proxy port number

        Returns:
            True if TCP connection succeeds, False otherwise
        """
        import socket

        try:
            # Create TCP connection with timeout
            sock = socket.create_connection((host, port), timeout=self.timeout)
            sock.close()
            return True
        except (TimeoutError, ConnectionRefusedError, socket.gaierror, OSError):
            # Connection failed - timeout, refused, DNS error, or network unreachable
            return False

    async def _validate_http_request(self, proxy_url: str | None = None) -> bool:
        """
        Validate HTTP request through proxy.

        Args:
            proxy_url: Full proxy URL (e.g., "http://proxy.example.com:8080")
                      If None, makes request without proxy (for testing)

        Returns:
            True if HTTP request succeeds, False otherwise
        """
        try:
            # httpx requires proxy at client initialization, not per-request
            if proxy_url:
                async with httpx.AsyncClient(
                    proxy=proxy_url,
                    timeout=self.timeout,
                    verify=_get_tls_verify(),
                ) as client:
                    response = await client.get(self.test_url)
                    return response.status_code in (200, 204)
            else:
                # No proxy - use shared client for direct requests
                client = await self._get_client()
                response = await client.get(self.test_url)
                return response.status_code in (200, 204)
        except (
            httpx.TimeoutException,
            httpx.ConnectError,
            httpx.NetworkError,
            Exception,
        ):
            # Request failed - timeout, connection error, network error, or other
            return False

    @property
    def anonymity_test_url(self) -> str:
        """JSON echo endpoint used for FULL-level anonymity checks."""
        return self._anonymity_test_url

    async def check_anonymity(self, proxy_url: str | None = None) -> str | None:
        """
        Check proxy anonymity level by detecting IP leakage using shared client.

        Tests if the proxy reveals the real IP address or proxy usage through
        HTTP headers like X-Forwarded-For, Via, X-Real-IP, etc.

        Args:
            proxy_url: Full proxy URL (e.g., "http://proxy.example.com:8080")
                      If None, makes request without proxy (for testing)

        Returns:
            - "transparent": Proxy leaks real IP address
            - "anonymous": Proxy hides IP but reveals proxy usage via headers
            - "elite": Proxy completely hides both IP and proxy usage
            - "unknown" or None: Could not determine (error occurred)
        """
        # Headers that indicate proxy usage or IP leakage
        proxy_headers = {
            "via",
            "x-forwarded-for",
            "x-real-ip",
            "forwarded",
            "proxy-connection",
            "x-proxy-id",
            "proxy-agent",
        }

        try:
            # httpx requires proxy at client initialization, not per-request
            target_url = self._anonymity_test_url
            if proxy_url:
                async with httpx.AsyncClient(
                    proxy=proxy_url,
                    timeout=self.timeout,
                    verify=_get_tls_verify(),
                ) as client:
                    response = await client.get(target_url)
            else:
                client = await self._get_client()
                response = await client.get(target_url)

            if response.status_code != 200:
                return "unknown"

            # Try to parse JSON response for IP and headers
            try:
                data = response.json()
                headers = data.get("headers", {})

                # Convert header keys to lowercase for case-insensitive comparison
                headers_lower = {k.lower(): v for k, v in headers.items()}

                # Check for headers that leak real IP (transparent proxy)
                if "x-forwarded-for" in headers_lower or "x-real-ip" in headers_lower:
                    return "transparent"

                # Check for headers that reveal proxy usage (anonymous proxy)
                if any(header in headers_lower for header in proxy_headers):
                    return "anonymous"

                # No proxy-revealing headers found (elite proxy)
                return "elite"

            except (ValueError, KeyError):
                # Could not parse response or missing expected fields
                return "unknown"

        except (
            httpx.TimeoutException,
            httpx.ConnectError,
            httpx.NetworkError,
            Exception,
        ):
            # Request failed
            return "unknown"

    async def validate(self, proxy: dict[str, Any]) -> ValidationResult:
        """
        Validate proxy connectivity with fast TCP pre-check and timing metrics.

        Performs a two-stage validation:
        1. Fast TCP pre-check to ensure port is open (1 second timeout)
        2. Full HTTP request through proxy to test functionality

        Includes result caching to avoid re-validating identical proxies.
        Response times are measured for successful validations only.

        Args:
            proxy : dict[str, Any]
                Proxy dictionary with 'url' key (e.g., "http://1.2.3.4:8080").
                May also include 'protocol' key for HTTPS/SOCKS validation.

        Returns:
            ValidationResult
                NamedTuple with:
                - is_valid: bool - Whether proxy is working
                - response_time_ms: float | None - HTTP response time in ms (only if valid)

        Raises:
            None - All exceptions are caught and return invalid result.

        Example:
            >>> validator = ProxyValidator(timeout=10.0)
            >>> proxy = {"url": "http://proxy.example.com:8080", "protocol": "http"}
            >>> result = await validator.validate(proxy)
            >>> if result.is_valid:
            ...     print(f"Proxy works! Response time: {result.response_time_ms:.1f}ms")
            ... else:
            ...     print("Proxy is not working")

        Note:
            - Results are cached with TTL (default: 1 hour)
            - TCP pre-check uses 1 second timeout to fail fast
            - HTTPS proxies tested against HTTPS endpoints
            - SOCKS proxies require httpx-socks library
            - Transparent proxies are validated as working
        """
        from proxywhirl.models import ValidationLevel

        proxy_url = proxy.get("url")
        if not proxy_url:
            result = ValidationResult(is_valid=False, response_time_ms=None)
            self._set_cached_result(proxy, result)
            return result

        safe, safety_reason = _validate_proxy_url_safety_compat(str(proxy_url))
        if not safe:
            logger.debug(
                "Skipping validation for unsafe proxy URL {}: {}",
                proxy_url,
                safety_reason,
            )
            result = ValidationResult(is_valid=False, response_time_ms=None)
            self._set_cached_result(proxy, result)
            return result

        proxy_protocol = self._get_effective_proxy_protocol(proxy, proxy_url)
        cache_target_url = self._peek_test_url_for_protocol(proxy_protocol)
        cached_result = self._get_cached_result(proxy, cache_target_url)
        if cached_result is not None:
            return cached_result

        try:
            # Parse host:port from URL
            parsed = urlparse(proxy_url)
            host = parsed.hostname
            port = parsed.port

            if not host or not port:
                result = ValidationResult(is_valid=False, response_time_ms=None)
                self._set_cached_result(proxy, result, cache_target_url)
                return result

            # Fast TCP pre-check (async) - skip HTTP if port isn't even open
            # Use very short timeout for TCP (1s) - if port isn't open, fail fast
            try:
                _, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port),
                    timeout=min(1.0, self.timeout),
                )
                writer.close()
                await writer.wait_closed()
            except (asyncio.TimeoutError, OSError, ConnectionRefusedError):
                result = ValidationResult(is_valid=False, response_time_ms=None)
                self._set_cached_result(proxy, result, cache_target_url)
                return result

            if self.level == ValidationLevel.BASIC:
                result = ValidationResult(is_valid=True, response_time_ms=None)
                self._set_cached_result(proxy, result, cache_target_url)
                return result

            # TCP passed - now test actual proxy functionality with timing
            # httpx requires proxy at client initialization, not per-request
            is_socks = proxy_url.startswith(("socks4://", "socks5://"))
            target_url = self._get_test_url_for_protocol(proxy_protocol)
            start_time = time.perf_counter()

            if is_socks:
                # Create SOCKS client with transport
                if not SOCKS_AVAILABLE:
                    logger.warning(
                        f"Skipping SOCKS validation for {proxy_url}: httpx-socks library not installed. "
                        "Install with: uv sync or add httpx-socks to your dependencies"
                    )
                    # Return invalid rather than error - graceful degradation
                    # SOCKS proxies cannot be validated without the library
                    result = ValidationResult(is_valid=False, response_time_ms=None)
                    self._set_cached_result(proxy, result, target_url)
                    return result

                if AsyncProxyTransport is None:
                    # This should not happen if SOCKS_AVAILABLE is True, but guard against it
                    logger.error("SOCKS_AVAILABLE is True but AsyncProxyTransport is None")
                    result = ValidationResult(is_valid=False, response_time_ms=None)
                    self._set_cached_result(proxy, result, target_url)
                    return result

                transport = AsyncProxyTransport.from_url(proxy_url)
                async with httpx.AsyncClient(
                    transport=transport,
                    timeout=self.timeout,
                    verify=_get_tls_verify(),
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    },
                ) as client:
                    response = await client.get(target_url)
                    elapsed_ms = (time.perf_counter() - start_time) * 1000
                    is_valid = response.status_code in (200, 204)
                    result = ValidationResult(
                        is_valid=is_valid,
                        response_time_ms=elapsed_ms if is_valid else None,
                    )
                    self._set_cached_result(proxy, result, target_url)
                    return result
            else:
                # For HTTPS-tagged proxies: connect to the proxy via plaintext HTTP.
                # Free HTTP-CONNECT proxies don't speak TLS themselves — httpx with
                # proxy="https://..." would attempt a TLS handshake to the proxy and fail.
                # The HTTPS target_url verifies CONNECT tunneling capability.
                effective_proxy_url = (
                    proxy_url.replace("https://", "http://", 1)
                    if proxy_url.startswith("https://")
                    else proxy_url
                )
                async with httpx.AsyncClient(
                    proxy=effective_proxy_url,
                    timeout=self.timeout,
                    verify=_get_tls_verify(),
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    },
                ) as client:
                    response = await client.get(target_url)
                    elapsed_ms = (time.perf_counter() - start_time) * 1000
                    is_valid = response.status_code in (200, 204)
                    result = ValidationResult(
                        is_valid=is_valid,
                        response_time_ms=elapsed_ms if is_valid else None,
                    )
                    self._set_cached_result(proxy, result, target_url)
                    return result
        except (httpx.HTTPError, OSError, TimeoutError, ValueError, TypeError) as exc:
            logger.bind(
                proxy_url=mask_proxy_url(str(proxy.get("url", ""))),
                error_type=type(exc).__name__,
            ).debug("Proxy validation failed")
            result = ValidationResult(is_valid=False, response_time_ms=None)
            target_url = locals().get("target_url", cache_target_url)
            self._set_cached_result(proxy, result, target_url)
            return result

    async def validate_batch(
        self,
        proxies: list[dict[str, Any]],
        progress_callback: Any | None = None,
    ) -> list[dict[str, Any]]:
        """
        Validate multiple proxies in parallel with concurrency control and metrics.

        Uses asyncio.Semaphore to limit concurrent validations based on
        the configured concurrency limit. Records response time for valid proxies.
        Invalid proxies are excluded from the result.

        Args:
            proxies : list[dict[str, Any]]
                List of proxy dictionaries to validate. Each dict should have
                a "url" key with the proxy URL.
            progress_callback : callable | None
                Optional callback with signature progress_callback(completed, total, valid_count)
                called after each validation completes (default: None).

        Returns:
            list[dict[str, Any]]
                List of working proxies with response_time_ms added to each entry.

        Raises:
            None - Validation errors are handled gracefully with failed proxies excluded.

        Example:
            >>> validator = ProxyValidator()
            >>> proxies = [
            ...     {"url": "http://proxy1.example.com:8080"},
            ...     {"url": "http://proxy2.example.com:8080"},
            ... ]
            >>> def callback(completed, total, valid):
            ...     print(f"Progress: {completed}/{total}, Valid: {valid}")
            >>> valid_proxies = await validator.validate_batch(proxies, callback)
            >>> for proxy in valid_proxies:
            ...     print(f"{proxy['url']} - {proxy['response_time_ms']:.1f}ms")

        Note:
            - Uses concurrent validation with semaphore to prevent resource exhaustion
            - Includes caching to avoid re-validating proxies
            - Failed proxies are silently excluded from results
            - Response time is only recorded for valid proxies
        """
        if not proxies:
            return []

        # Create semaphore to limit concurrent validations
        semaphore = asyncio.Semaphore(self.concurrency)
        completed = 0
        valid_count = 0
        total = len(proxies)

        async def validate_with_semaphore(
            proxy: dict[str, Any],
        ) -> tuple[dict[str, Any], ValidationResult]:
            """Validate a single proxy with semaphore control and timing."""
            nonlocal completed, valid_count
            async with semaphore:
                try:
                    result = await self.validate(proxy)
                    completed += 1
                    if result.is_valid:
                        valid_count += 1
                    if progress_callback:
                        progress_callback(completed, total, valid_count)
                    return (proxy, result)
                except (
                    httpx.HTTPError,
                    OSError,
                    TimeoutError,
                    ProxyFetchError,
                    ValueError,
                    TypeError,
                ) as exc:
                    # If validation raises an exception, treat as failed
                    logger.bind(
                        proxy_url=mask_proxy_url(str(proxy.get("url", ""))),
                        error_type=type(exc).__name__,
                    ).debug("Proxy validation error")
                    completed += 1
                    if progress_callback:
                        progress_callback(completed, total, valid_count)
                    return (proxy, ValidationResult(is_valid=False, response_time_ms=None))

        # Run all validations in parallel (semaphore controls concurrency)
        tasks = [validate_with_semaphore(proxy) for proxy in proxies]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter valid proxies and add timing metrics
        validated: list[dict[str, Any]] = []
        for result in results:
            # Handle exceptions from gather
            if isinstance(result, Exception):
                continue
            # result is a tuple[dict[str, Any], ValidationResult]
            if not isinstance(result, tuple):
                continue
            proxy, validation_result = result
            if validation_result.is_valid:
                # Add response time to proxy dict for persistence
                # Use average_response_time_ms to match Proxy model field name
                proxy["average_response_time_ms"] = validation_result.response_time_ms
                proxy["status"] = "active"
                # Mark as checked with success
                proxy["total_requests"] = proxy.get("total_requests", 0) + 1
                proxy["total_successes"] = proxy.get("total_successes", 0) + 1
                # Record validation timestamp for freshness tracking
                proxy["last_success_at"] = datetime.now(timezone.utc)
                validated.append(proxy)

        return validated

    async def validate_https_capability_batch(
        self,
        http_proxies: list[dict[str, Any]],
        concurrency: int = 500,
        max_results: int | None = None,
        progress_callback: Any | None = None,
    ) -> list[dict[str, Any]]:
        """Test already-validated HTTP proxies for HTTPS/CONNECT support.

        Many free proxy lists label HTTP proxies as "HTTPS" after testing CONNECT
        tunneling. This method takes working HTTP proxies and tests each via the
        CONNECT method against an HTTPS endpoint. Proxies that pass are returned as
        ``https://`` entries ready for DB insertion.

        Args:
            http_proxies: Already-validated HTTP proxy dicts (protocol='http').
            concurrency: Max concurrent HTTPS tests (default 500).
            max_results: Stop early once this many HTTPS-capable proxies are found.
            progress_callback: Optional callback(completed, total, valid_count).

        Returns:
            Proxy dicts with ``protocol='https'`` and ``url='https://ip:port'``
            for each HTTP proxy that successfully tunnels HTTPS via CONNECT.
        """
        if not http_proxies:
            return []

        if concurrency < 1:
            raise ValueError("concurrency must be >= 1")

        # Deduplicate by URL to avoid testing the same proxy multiple times
        seen: set[str] = set()
        unique_proxies: list[dict[str, Any]] = []
        for p in http_proxies:
            url = p.get("url", "")
            protocol = p.get("protocol")
            normalized_protocol = protocol.lower() if isinstance(protocol, str) else None
            if (
                not isinstance(url, str)
                or not url.startswith("http://")
                or (normalized_protocol is not None and normalized_protocol != "http")
            ):
                logger.debug(f"Skipping HTTPS capability validation for non-HTTP proxy: {url}")
                continue
            if url not in seen:
                seen.add(url)
                unique_proxies.append(p)

        if not unique_proxies:
            return []

        semaphore = asyncio.Semaphore(concurrency)
        done_event = asyncio.Event()
        completed = 0
        valid_count = 0
        total = len(unique_proxies)

        # CONNECT tunneling needs: TCP connect + CONNECT handshake + TLS negotiation
        # + HTTP roundtrip. Cap at 8s per stage — 5s was too aggressive.
        per_stage = min(float(self.timeout), 8.0)
        https_timeout = httpx.Timeout(
            connect=per_stage,
            read=per_stage,
            write=2.0,
            pool=1.0,
        )

        https_test_urls = self.HTTPS_TEST_URLS

        # Diagnostic failure counters
        timeout_count = 0
        connection_count = 0
        http_error_count = 0
        other_error_count = 0

        async def test_one(
            proxy: dict[str, Any],
        ) -> tuple[dict[str, Any], ValidationResult]:
            nonlocal completed, valid_count
            nonlocal timeout_count, connection_count, http_error_count, other_error_count
            if done_event.is_set():
                completed += 1
                return (proxy, ValidationResult(is_valid=False, response_time_ms=None))
            async with semaphore:
                http_url = proxy["url"]  # always http://ip:port here
                is_valid = False
                elapsed_ms: float | None = None

                # Try all HTTPS test URLs — succeed on any
                for test_url in https_test_urls:
                    if done_event.is_set():
                        break
                    try:
                        start = time.perf_counter()
                        async with httpx.AsyncClient(
                            proxy=http_url,
                            timeout=https_timeout,
                            verify=_get_tls_verify(),
                            headers={
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                            },
                        ) as client:
                            response = await client.head(test_url)
                            elapsed_ms = (time.perf_counter() - start) * 1000
                            # Accept any 2xx/3xx as proof CONNECT tunneling works
                            if 200 <= response.status_code < 400:
                                is_valid = True
                                break
                    except (httpx.TimeoutException, TimeoutError):
                        timeout_count += 1
                        continue
                    except (httpx.ConnectError, httpx.ProxyError, OSError):
                        connection_count += 1
                        continue
                    except httpx.HTTPStatusError:
                        http_error_count += 1
                        continue
                    except (httpx.HTTPError, RuntimeError) as exc:
                        logger.bind(
                            proxy_url=mask_proxy_url(http_url),
                            error_type=type(exc).__name__,
                        ).debug("Unexpected HTTPS-validation error")
                        other_error_count += 1
                        continue

                completed += 1
                if is_valid:
                    valid_count += 1
                    if max_results is not None and valid_count >= max_results:
                        done_event.set()
                if progress_callback:
                    progress_callback(completed, total, valid_count)
                return (
                    proxy,
                    ValidationResult(
                        is_valid=is_valid,
                        response_time_ms=elapsed_ms if is_valid else None,
                    ),
                )

        tasks = [test_one(proxy) for proxy in unique_proxies]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log diagnostic failure summary
        logger.info(
            "HTTPS CONNECT validation: {} tested, {} passed, "
            "failures: {} timeout, {} connection, {} HTTP error, {} other",
            total,
            valid_count,
            timeout_count,
            connection_count,
            http_error_count,
            other_error_count,
        )

        https_capable: list[dict[str, Any]] = []
        for result in results:
            if isinstance(result, Exception) or not isinstance(result, tuple):
                continue
            proxy, vr = result
            if not vr.is_valid:
                continue
            # Build an https:// variant of this proxy
            http_url = proxy["url"]
            https_url = http_url.replace("http://", "https://", 1)
            entry = {
                **proxy,
                "url": https_url,
                "protocol": "https",
                "average_response_time_ms": vr.response_time_ms,
            }
            https_capable.append(entry)
            if max_results is not None and len(https_capable) >= max_results:
                break

        return https_capable
