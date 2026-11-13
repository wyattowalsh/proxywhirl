"""ProxyFetcher for downloading and parsing proxy sources."""

from __future__ import annotations

import asyncio
import hashlib
import time
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx
from loguru import logger
from tenacity import (
    RetryCallState,
    retry,
    retry_if_exception,
    retry_if_exception_type,
    stop_after_attempt,
)

from proxywhirl.exceptions import ProxyFetchError, ProxyValidationError
from proxywhirl.fetchers.parsers import (
    CSVParser,
    HTMLTableParser,
    JSONParser,
    PlainTextParser,
    _read_bounded_response_text,
    deduplicate_proxies,
    normalize_parsed_proxy_rows,
)
from proxywhirl.fetchers.shared import (
    FETCH_MAX_RESPONSE_BYTES,
    PERIODIC_REFRESH_MAX_CONSECUTIVE_ERRORS,
)
from proxywhirl.fetchers.validator import ProxyValidator, _get_tls_verify
from proxywhirl.models import ProxySourceConfig, RenderMode
from proxywhirl.security import pin_outbound_url, redact_url, validate_source_url_safety

RETRYABLE_STATUS_CODES = {
    429,  # Too Many Requests
    503,  # Service Unavailable
    502,  # Bad Gateway
    504,  # Gateway Timeout
}

_REDIRECT_STATUS_CODES = {301, 302, 303, 307, 308}
_MAX_SOURCE_REDIRECTS = 10


def _is_retryable_http_error(exception: BaseException) -> bool:
    """Check if exception is a retryable HTTP error (429, 503, 502, 504).

    Args:
        exception: Exception to check

    Returns:
        True if exception is a retryable HTTP status error
    """
    if isinstance(exception, httpx.HTTPStatusError):
        return exception.response.status_code in RETRYABLE_STATUS_CODES
    return False


def _wait_with_retry_after(retry_state: RetryCallState) -> float:
    """Calculate wait time respecting Retry-After header.

    If the exception has a Retry-After header, use that value.
    Otherwise, use exponential backoff (2^attempt_number seconds, max 60s).

    Args:
        retry_state: Tenacity retry call state

    Returns:
        Wait time in seconds
    """
    import random

    # Try to get Retry-After header from exception
    exception = retry_state.outcome.exception() if retry_state.outcome else None
    if isinstance(exception, httpx.HTTPStatusError):
        retry_after = exception.response.headers.get("Retry-After")
        if retry_after:
            try:
                # Retry-After can be seconds or HTTP-date
                wait_seconds = int(retry_after)
                # Cap at 60 seconds to prevent DoS via long Retry-After
                return min(wait_seconds, 60)
            except ValueError:
                pass  # Not an integer, fall through to default

    # Default: exponential backoff with jitter
    attempt = retry_state.attempt_number
    base_wait = min(2**attempt, 60)  # Cap at 60 seconds
    # Add jitter (0-25% of base wait)
    jitter = random.uniform(0, base_wait * 0.25)  # noqa: S311
    return base_wait + jitter


class ProxyFetcher:
    """Fetch and parse proxies from multiple sources with validation and deduplication.

    Supports multiple proxy source formats (JSON, CSV, plain text, HTML tables)
    and automatic proxy validation. Includes request caching to avoid duplicate
    fetches and deduplication by URL+Port combination.

    Attributes:
        sources: List of proxy source configurations
        validator: Fetcher-owned ProxyValidator instance for validating fetched proxies
        _parsers: Mapping of format names to parser classes
        _request_cache: Cache for HTTP responses (URL -> content)
    """

    def __init__(
        self,
        sources: list[ProxySourceConfig] | None = None,
        validator: ProxyValidator | None = None,
        dedup_cache_ttl: int = 3600,
    ) -> None:
        """
        Initialize proxy fetcher with sources and validator.

        Creates a new proxy fetcher with support for multiple source formats
        and automatic validation. Request responses are cached to avoid
        duplicate HTTP fetches.

        Args:
            sources : list[ProxySourceConfig] | None
                List of proxy source configurations (default: []).
            validator : ProxyValidator | None
                ProxyValidator instance for validating fetched proxies.
                If None, creates a new ProxyValidator with default settings.
                Passing an instance transfers its cleanup ownership to the fetcher;
                :meth:`close` closes it, so callers must not reuse it afterward.
            dedup_cache_ttl : int
                TTL for request deduplication cache in seconds (default: 3600 / 1 hour).

        Returns:
            None

        Example:
            >>> sources = [
            ...     ProxySourceConfig(url="https://example.com/proxies.json", format="json"),
            ...     ProxySourceConfig(url="https://example.com/proxies.csv", format="csv"),
            ... ]
            >>> fetcher = ProxyFetcher(sources=sources)
            >>> proxies = await fetcher.fetch_proxies()

        Note:
            - Supports JSON, CSV, plain text, and HTML table formats
            - Automatic deduplication by URL+Port
            - Request caching reduces redundant HTTP fetches
            - Validator caching reduces redundant proxy tests
        """
        self.sources = sources or []
        self.validator = validator or ProxyValidator()
        self._parsers = {
            "json": JSONParser,
            "csv": CSVParser,
            "plain_text": PlainTextParser,
            "html_table": HTMLTableParser,
            # Legacy aliases for backwards compatibility
            "text": PlainTextParser,
            "html": HTMLTableParser,
        }
        self._client: httpx.AsyncClient | None = None

        # Request deduplication cache (URL -> (response_content, timestamp))
        self._request_cache: dict[str, tuple[str, float]] = {}
        self._dedup_cache_ttl = dedup_cache_ttl
        self._refresh_cancel = asyncio.Event()
        self._refresh_task: asyncio.Task[None] | None = None

    def add_source(self, source: ProxySourceConfig) -> None:
        """
        Add a proxy source to fetch from.

        Appends a new source configuration to the list of sources.
        Sources will be fetched in order when fetch_proxies() is called.

        Args:
            source : ProxySourceConfig
                Proxy source configuration with URL and format.

        Returns:
            None

        Example:
            >>> fetcher = ProxyFetcher()
            >>> source = ProxySourceConfig(
            ...     url="https://example.com/proxies.json",
            ...     format="json"
            ... )
            >>> fetcher.add_source(source)

        Note:
            - Duplicate sources are allowed
            - Sources are not validated at add time
        """
        self.sources.append(source)

    def remove_source(self, url: str) -> None:
        """
        Remove a proxy source by URL.

        Removes all sources matching the given URL. If multiple sources
        have the same URL, all are removed.

        Args:
            url : str
                URL of source to remove (e.g., "https://example.com/proxies.json").

        Returns:
            None

        Example:
            >>> fetcher = ProxyFetcher()
            >>> fetcher.remove_source("https://example.com/proxies.json")

        Note:
            - Does not raise error if source not found
            - Removes all matching URLs
        """
        self.sources = [s for s in self.sources if str(s.url) != url]

    async def _get_client(self) -> httpx.AsyncClient:
        """
        Get or create the shared HTTP client with HTTP/2 support.

        Returns:
            Shared httpx.AsyncClient instance with HTTP/1.1 and HTTP/2 support
        """
        if self._client is None:
            # follow_redirects=False: each hop must be re-validated by callers
            # that need redirects; default static fetch does not auto-follow.
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                verify=_get_tls_verify(),
                limits=httpx.Limits(max_connections=50, max_keepalive_connections=10),
                http2=True,
                follow_redirects=False,
            )
        return self._client

    async def close(self) -> None:
        """Close all fetcher-owned resources, including an injected validator.

        A validator passed to :meth:`__init__` follows transfer-of-ownership
        semantics and is closed here just like a validator created internally.
        """
        client = self._client
        self._client = None

        cleanup_calls = []
        if self._refresh_task is asyncio.current_task():
            self._refresh_cancel.set()
            self._refresh_task = None
        elif self._refresh_task is not None:
            cleanup_calls.append(self.stop_periodic_refresh())
        if client is not None:
            cleanup_calls.append(client.aclose())
        if self.validator is not None:
            cleanup_calls.append(self.validator.close())
        if not cleanup_calls:
            return

        async def cleanup() -> list[BaseException | None]:
            results = await asyncio.gather(*cleanup_calls, return_exceptions=True)
            return [result if isinstance(result, BaseException) else None for result in results]

        cleanup_task = asyncio.create_task(cleanup())
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

    async def _fetch_static_content(
        self,
        client: httpx.AsyncClient,
        source_url: str,
        *,
        headers: dict[str, str] | None,
        auth: Any,
    ) -> str:
        """Fetch a source with bounded, policy-checked manual redirects."""
        current_url = source_url
        current_auth = auth
        current_headers = headers

        for redirect_count in range(_MAX_SOURCE_REDIRECTS + 1):
            safe, safety_reason = validate_source_url_safety(current_url)
            if not safe:
                raise ProxyFetchError(f"Source URL blocked by SSRF protection: {safety_reason}")
            pin, pin_reason = pin_outbound_url(current_url, purpose="source")
            if pin is None:
                raise ProxyFetchError(f"Source URL blocked by SSRF protection: {pin_reason}")

            request_headers = dict(current_headers) if current_headers else {}
            request_headers["Host"] = pin.host_header
            async with client.stream(
                "GET",
                pin.pinned_url,
                headers=request_headers,
                auth=current_auth,
                extensions=pin.extensions,
            ) as response:
                if response.status_code not in _REDIRECT_STATUS_CODES:
                    response.raise_for_status()
                    return await _read_bounded_response_text(response)

                location = response.headers.get("Location")
                if not location:
                    raise ProxyFetchError("Source redirect response is missing Location header")
                if redirect_count >= _MAX_SOURCE_REDIRECTS:
                    raise ProxyFetchError(
                        f"Source exceeded maximum redirect count of {_MAX_SOURCE_REDIRECTS}"
                    )

                redirect_url = urljoin(current_url, location)
                safe, safety_reason = validate_source_url_safety(redirect_url)
                if not safe:
                    raise ProxyFetchError(
                        f"Source redirect blocked by SSRF protection: {safety_reason}"
                    )

                if urlparse(redirect_url).netloc != urlparse(current_url).netloc:
                    current_auth = None
                    if current_headers is not None:
                        current_headers = {
                            key: value
                            for key, value in current_headers.items()
                            if key.lower() not in {"authorization", "cookie", "proxy-authorization"}
                        }
                current_url = redirect_url

        raise ProxyFetchError("Source redirect handling terminated unexpectedly")

    def _get_request_cache_key(self, url: str) -> str:
        """Generate cache key for a URL.

        Args:
            url: URL to generate key for

        Returns:
            Cache key string (hash of URL)
        """
        return hashlib.md5(url.encode(), usedforsecurity=False).hexdigest()

    def _get_cached_response(self, url: str) -> str | None:
        """Get cached response if not expired.

        Args:
            url: URL to check cache for

        Returns:
            Cached response content if available and not expired, None otherwise
        """
        cache_key = self._get_request_cache_key(url)
        if cache_key in self._request_cache:
            content, timestamp = self._request_cache[cache_key]
            if time.time() - timestamp < self._dedup_cache_ttl:
                logger.debug(f"Request cache hit for {redact_url(url)}")
                return content
            else:
                # Cache expired - remove it
                del self._request_cache[cache_key]
        return None

    def _set_cached_response(self, url: str, content: str) -> None:
        """Cache a response content.

        Args:
            url: URL that was fetched
            content: Response content to cache
        """
        cache_key = self._get_request_cache_key(url)
        self._request_cache[cache_key] = (content, time.time())

    async def __aenter__(self) -> ProxyFetcher:
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()

    @retry(
        stop=stop_after_attempt(5),  # More retries for rate limiting scenarios
        wait=_wait_with_retry_after,  # Respects Retry-After header with fallback to exp backoff
        retry=(
            retry_if_exception_type(httpx.TimeoutException)
            | retry_if_exception(_is_retryable_http_error)
        ),
        reraise=True,  # Re-raise the original exception after retries exhausted
    )
    async def fetch_from_source(self, source: ProxySourceConfig) -> list[dict[str, Any]]:
        """
        Fetch and parse proxies from a single source with automatic retries and caching.

        Handles multiple source formats (JSON, CSV, plain text, HTML tables) and
        supports browser rendering for JavaScript-heavy pages. Includes automatic
        retry with exponential backoff for rate limiting and temporary server errors.
        Request responses are cached to avoid duplicate fetches.

        Includes automatic retry with exponential backoff for:
        - HTTP 429 (Too Many Requests) - respects Retry-After header
        - HTTP 503 (Service Unavailable)
        - HTTP 502 (Bad Gateway)
        - HTTP 504 (Gateway Timeout)
        - Network timeouts

        Args:
            source : ProxySourceConfig
                Proxy source configuration with:
                - url: Source URL (str or HttpUrl)
                - format: Format identifier (json, csv, plain_text, html_table)
                - protocol: Optional protocol override (socks4, socks5)
                - render_mode: RenderMode.BROWSER or RenderMode.STATIC (default)
                - custom_parser: Optional custom parser object

        Returns:
            list[dict[str, Any]]
                List of raw proxy dictionaries parsed from source. Each dict
                typically contains 'url' and optionally 'protocol', 'source', etc.

        Raises:
            ProxyFetchError
                If HTTP request fails after retries, format is unsupported,
                or parsing fails.

        Example:
            >>> fetcher = ProxyFetcher()
            >>> source = ProxySourceConfig(
            ...     url="https://example.com/proxies.json",
            ...     format="json"
            ... )
            >>> proxies = await fetcher.fetch_from_source(source)
            >>> print(f"Fetched {len(proxies)} proxies")

        Note:
            - Browser rendering requires Playwright (install with `pip install 'proxywhirl[js]'`)
            - Request responses cached for 1 hour (configurable)
            - Retries use exponential backoff with up to 5 attempts
            - Protocol override applied after parsing (for plain text sources)
            - Custom parsers take precedence over format-based parsers
        """
        try:
            # Check request cache first to avoid duplicate requests
            source_url = str(source.url)
            safe, safety_reason = validate_source_url_safety(source_url)
            if not safe:
                raise ProxyFetchError(f"Source URL blocked by SSRF protection: {safety_reason}")

            cached_content = self._get_cached_response(source_url)

            # Determine if browser rendering is needed
            html_content: str

            if cached_content is not None:
                html_content = cached_content
            elif source.render_mode == RenderMode.BROWSER:
                # Use browser rendering for JavaScript-heavy pages
                try:
                    from proxywhirl.browser import BrowserRenderer
                except ImportError as e:
                    raise ProxyFetchError(
                        "Browser rendering requires Playwright. "
                        "Install with: pip install 'proxywhirl[js]' or pip install playwright"
                    ) from e

                user_agent = source.headers.get("User-Agent") if source.headers else None
                try:
                    async with BrowserRenderer(user_agent=user_agent) as renderer:
                        html_content = await renderer.render(
                            source_url,
                            wait_for_selector=source.wait_selector,
                            wait_for_timeout=source.wait_timeout if source.wait_selector else None,
                            max_content_bytes=FETCH_MAX_RESPONSE_BYTES,
                        )
                except TimeoutError as e:
                    raise ProxyFetchError(f"Browser timeout fetching from {source_url}: {e}") from e
                except RuntimeError as e:
                    raise ProxyFetchError(f"Browser error fetching from {source_url}: {e}") from e

                # Cache the rendered content
                self._set_cached_response(source_url, html_content)
            else:
                client = await self._get_client()
                request_headers = dict(source.headers) if source.headers else None
                html_content = await self._fetch_static_content(
                    client,
                    source_url,
                    headers=request_headers,
                    auth=source.auth,
                )

                self._set_cached_response(source_url, html_content)

            # Use custom parser if provided
            if source.custom_parser:
                proxies_list = source.custom_parser.parse(html_content)
                proxies_list = normalize_parsed_proxy_rows(proxies_list, source)
                if source.trusted:
                    for proxy in proxies_list:
                        proxy["from_trusted_source"] = True
                return proxies_list

            # Otherwise use format-based parser
            # Note: parser field in ProxySourceConfig is now a string identifier, not an object
            # Custom parsers should be registered via _parsers dict
            format_key = source.format.value if hasattr(source.format, "value") else source.format
            if format_key in self._parsers:
                parser_class = self._parsers[format_key]
                parser = parser_class()
            else:
                raise ProxyFetchError(f"Unsupported format: {source.format}")

            proxies_list = parser.parse(html_content)
            proxies_list = normalize_parsed_proxy_rows(proxies_list, source)
            if source.trusted:
                for proxy in proxies_list:
                    proxy["from_trusted_source"] = True
            return proxies_list

        except httpx.HTTPStatusError as e:
            # Let retryable HTTP errors (429, 503, 502, 504) bubble up to retry decorator
            # Only convert to ProxyFetchError for non-retryable errors
            if e.response.status_code not in RETRYABLE_STATUS_CODES:
                raise ProxyFetchError(f"HTTP error fetching from {source.url}: {e}") from e
            raise  # Re-raise for retry decorator to handle
        except httpx.RequestError as e:
            raise ProxyFetchError(f"Request error fetching from {source.url}: {e}") from e
        except (ProxyFetchError, ProxyValidationError, ValueError, TypeError, KeyError) as e:
            raise ProxyFetchError(f"Error fetching from {source.url}: {e}") from e

    async def fetch_all(
        self,
        validate: bool = True,
        deduplicate: bool = True,
        fetch_progress_callback: Any | None = None,
        validate_progress_callback: Any | None = None,
    ) -> list[dict[str, Any]]:
        """
        Fetch and optionally validate proxies from all configured sources in parallel.

        Fetches from all sources concurrently, deduplicates by URL+Port if requested,
        and validates using the configured ProxyValidator. Progress can be tracked
        via callbacks during both fetch and validation phases.

        Args:
            validate : bool
                Whether to validate proxies before returning (default: True).
            deduplicate : bool
                Whether to deduplicate proxies by URL+Port (default: True).
            fetch_progress_callback : callable | None
                Optional callback with signature callback(completed, total, proxies_found)
                called after each source is fetched. Default: None.
            validate_progress_callback : callable | None
                Optional callback with signature callback(completed, total, valid_count)
                called during validation progress. Default: None.

        Returns:
            list[dict[str, Any]]
                List of working proxies with response_time_ms added if validated.
                Failed fetches from individual sources are logged but don't fail
                the entire operation.

        Raises:
            None - Individual source failures are logged and skipped gracefully.

        Example:
            >>> sources = [
            ...     ProxySourceConfig(url="https://api1.example.com/proxies.json", format="json"),
            ...     ProxySourceConfig(url="https://api2.example.com/proxies.csv", format="csv"),
            ... ]
            >>> fetcher = ProxyFetcher(sources=sources)
            >>> def fetch_callback(completed, total, proxies):
            ...     print(f"Fetched from {completed}/{total} sources, {proxies} proxies found")
            >>> def validate_callback(completed, total, valid):
            ...     print(f"Validated {completed}/{total}, {valid} are working")
            >>> proxies = await fetcher.fetch_all(
            ...     fetch_progress_callback=fetch_callback,
            ...     validate_progress_callback=validate_callback
            ... )
            >>> print(f"Final list: {len(proxies)} working proxies")

        Note:
            - Fetches from all sources in parallel for speed
            - Deduplication happens before validation
            - Failed individual source fetches are logged but don't fail the entire fetch
            - Validation uses configured concurrency limit
            - Returns empty list if all sources fail
        """
        all_proxies: list[dict[str, Any]] = []
        completed_sources = 0
        total_sources = len(self.sources)

        # Fetch from all sources with progress tracking
        async def fetch_with_progress(source: ProxySourceConfig) -> list[dict[str, Any]]:
            nonlocal completed_sources
            try:
                result = await self.fetch_from_source(source)
                for proxy in result:
                    if source.trusted:
                        proxy["from_trusted_source"] = True
                completed_sources += 1
                if fetch_progress_callback:
                    fetch_progress_callback(
                        completed_sources, total_sources, len(all_proxies) + len(result)
                    )
                return result
            except (ProxyFetchError, httpx.HTTPError):
                logger.opt(exception=True).warning("Failed to fetch from {}", source.url)
                completed_sources += 1
                if fetch_progress_callback:
                    fetch_progress_callback(completed_sources, total_sources, len(all_proxies))
                return []

        # Fetch from all sources in parallel
        tasks = [fetch_with_progress(source) for source in self.sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Collect successful results
        for result in results:
            if isinstance(result, list):
                all_proxies.extend(result)
            # Skip exceptions (already logged by retry decorator)

        # Deduplicate if requested
        if deduplicate:
            all_proxies = deduplicate_proxies(all_proxies)

        if validate:
            trusted_proxies = [p for p in all_proxies if p.get("from_trusted_source")]
            to_validate = [p for p in all_proxies if not p.get("from_trusted_source")]
            if not to_validate:
                return trusted_proxies
            validated = await self.validator.validate_batch(
                to_validate, progress_callback=validate_progress_callback
            )
            return validated + trusted_proxies

        return all_proxies

    async def stop_periodic_refresh(self) -> None:
        """Cancel a background periodic refresh loop started by ``start_periodic_refresh``."""
        self._refresh_cancel.set()
        if self._refresh_task is not None:
            self._refresh_task.cancel()
            try:
                await self._refresh_task
            except asyncio.CancelledError:
                pass
            self._refresh_task = None
        self._refresh_cancel.clear()

    async def start_periodic_refresh(
        self,
        callback: Any | None = None,
        interval: int | None = None,
        max_consecutive_errors: int = PERIODIC_REFRESH_MAX_CONSECUTIVE_ERRORS,
    ) -> None:
        """
        Start periodic proxy refresh.

        Args:
            callback: Optional callback to invoke with new proxies
            interval: Override default refresh interval (seconds)
            max_consecutive_errors: Stop refreshing after this many consecutive failures
        """
        if self._refresh_task is not None and not self._refresh_task.done():
            raise RuntimeError("Periodic refresh is already running")

        self._refresh_cancel.clear()

        async def _refresh_loop() -> None:
            consecutive_errors = 0
            while not self._refresh_cancel.is_set():
                refresh_interval = interval or (
                    self.sources[0].refresh_interval if self.sources else 3600
                )
                try:
                    await asyncio.wait_for(
                        self._refresh_cancel.wait(),
                        timeout=refresh_interval,
                    )
                    break
                except asyncio.TimeoutError:
                    pass

                if self._refresh_cancel.is_set():
                    break

                try:
                    proxies = await self.fetch_all()
                    consecutive_errors = 0
                    if callback:
                        result = callback(proxies)
                        if asyncio.iscoroutine(result):
                            await result
                except (ProxyFetchError, httpx.HTTPError, OSError, RuntimeError) as exc:
                    consecutive_errors += 1
                    logger.warning(
                        "Periodic refresh failed ({}/{}): {}",
                        consecutive_errors,
                        max_consecutive_errors,
                        exc,
                    )
                    if consecutive_errors >= max_consecutive_errors:
                        logger.error("Stopping periodic refresh after consecutive failures")
                        break

        self._refresh_task = asyncio.create_task(_refresh_loop())
        await self._refresh_task
