"""
Proxy fetching and parsing functionality.

This module provides tools for fetching proxies from various sources and
parsing different formats (JSON, CSV, plain text, HTML tables).
"""

from __future__ import annotations

import asyncio
import csv
import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from proxywhirl.models import ValidationLevel
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from proxywhirl.exceptions import ProxyFetchError, ProxyValidationError
from proxywhirl.models import ProxySourceConfig, RenderMode


class JSONParser:
    """Parse JSON-formatted proxy lists."""

    def __init__(
        self,
        key: str | None = None,
        required_fields: list[str] | None = None,
    ) -> None:
        """
        Initialize JSON parser.

        Args:
            key: Optional key to extract from JSON object
            required_fields: Fields that must be present in each proxy
        """
        self.key = key
        self.required_fields = required_fields or []

    def parse(self, data: str) -> list[dict[str, Any]]:
        """
        Parse JSON proxy data.

        Args:
            data: JSON string to parse

        Returns:
            List of proxy dictionaries

        Raises:
            ProxyFetchError: If JSON is invalid
            ProxyValidationError: If required fields are missing
        """
        try:
            parsed = json.loads(data)
        except json.JSONDecodeError as e:
            raise ProxyFetchError(f"Invalid JSON: {e}") from e

        # Extract from key if specified
        if self.key:
            if not isinstance(parsed, dict) or self.key not in parsed:
                raise ProxyFetchError(f"JSON missing key: {self.key}")
            parsed = parsed[self.key]

        # Ensure we have a list
        if not isinstance(parsed, list):
            raise ProxyFetchError("JSON must be array or object with array key")

        # Validate required fields
        if self.required_fields:
            for proxy in parsed:
                for field in self.required_fields:
                    if field not in proxy:
                        raise ProxyValidationError(f"Missing required field: {field}")

        return parsed


class CSVParser:
    """Parse CSV-formatted proxy lists."""

    def __init__(
        self,
        has_header: bool = True,
        columns: list[str] | None = None,
        skip_invalid: bool = False,
    ) -> None:
        """
        Initialize CSV parser.

        Args:
            has_header: Whether CSV has header row
            columns: Column names if no header
            skip_invalid: Skip malformed rows instead of raising error
        """
        self.has_header = has_header
        self.columns = columns
        self.skip_invalid = skip_invalid

    def parse(self, data: str) -> list[dict[str, Any]]:
        """
        Parse CSV proxy data.

        Args:
            data: CSV string to parse

        Returns:
            List of proxy dictionaries

        Raises:
            ProxyFetchError: If CSV is malformed and skip_invalid is False
        """
        if not data.strip():
            return []

        lines = data.strip().split("\n")
        reader = csv.reader(lines)

        proxies = []

        if self.has_header:
            # First row is headers
            try:
                headers = next(reader)
            except StopIteration:
                return []

            for row in reader:
                if len(row) != len(headers):
                    if self.skip_invalid:
                        continue
                    raise ProxyFetchError(
                        f"Malformed CSV row: expected {len(headers)} columns, got {len(row)}"
                    )
                proxies.append(dict(zip(headers, row)))
        else:
            # Use provided column names
            if not self.columns:
                raise ProxyFetchError("Must provide columns if no header")

            for row in reader:
                if len(row) != len(self.columns):
                    if self.skip_invalid:
                        continue
                    raise ProxyFetchError(
                        f"Malformed CSV row: expected {len(self.columns)} columns, got {len(row)}"
                    )
                proxies.append(dict(zip(self.columns, row)))

        return proxies


class PlainTextParser:
    """Parse plain text proxy lists (one per line)."""

    def __init__(self, skip_invalid: bool = False) -> None:
        """
        Initialize plain text parser.

        Args:
            skip_invalid: Skip invalid URLs instead of raising error
        """
        self.skip_invalid = skip_invalid

    def parse(self, data: str) -> list[dict[str, Any]]:
        """
        Parse plain text proxy data.

        Args:
            data: Plain text string with one proxy per line
                  Supports formats: IP:PORT, http://IP:PORT, socks5://IP:PORT

        Returns:
            List of proxy dictionaries with 'url' key
        """
        import re

        # Pattern for IP:PORT (without scheme)
        ip_port_pattern = re.compile(r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)$")

        proxies = []

        for line in data.split("\n"):
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Skip comments
            if line.startswith("#"):
                continue

            # Handle IP:PORT format (prepend http://)
            if ip_port_pattern.match(line):
                line = f"http://{line}"

            # Validate URL format
            try:
                parsed = urlparse(line)
                if not parsed.scheme or not parsed.netloc:
                    if not self.skip_invalid:
                        raise ProxyFetchError(f"Invalid URL: {line}")
                    continue
            except Exception:
                if self.skip_invalid:
                    continue
                raise

            proxies.append({"url": line})

        return proxies


class HTMLTableParser:
    """Parse HTML table-formatted proxy lists."""

    def __init__(
        self,
        table_selector: str = "table",
        column_map: dict[str, str] | None = None,
        column_indices: dict[str, int] | None = None,
    ) -> None:
        """
        Initialize HTML table parser.

        Args:
            table_selector: CSS selector for table element
            column_map: Map header names to proxy fields
            column_indices: Map field names to column indices
        """
        self.table_selector = table_selector
        self.column_map = column_map or {}
        self.column_indices = column_indices or {}

    def parse(self, data: str) -> list[dict[str, Any]]:
        """
        Parse HTML table proxy data.

        Args:
            data: HTML string containing table

        Returns:
            List of proxy dictionaries
        """
        soup = BeautifulSoup(data, "html.parser")
        table = soup.select_one(self.table_selector)

        if not table:
            return []

        proxies = []
        rows = table.find_all("tr")

        # Determine if first row is header
        has_header = bool(rows and rows[0].find_all("th"))
        data_rows = rows[1:] if has_header else rows

        # Build header map if using column_map
        header_to_index: dict[str, int] = {}
        if has_header and self.column_map:
            headers = [th.get_text(strip=True) for th in rows[0].find_all("th")]
            for i, header in enumerate(headers):
                header_to_index[header] = i

        for row in data_rows:
            cells = row.find_all("td")
            proxy: dict[str, Any] = {}

            if self.column_indices:
                # Use column indices
                for field, index in self.column_indices.items():
                    if index < len(cells):
                        proxy[field] = cells[index].get_text(strip=True)
            elif self.column_map and header_to_index:
                # Use column map with headers
                for header, field in self.column_map.items():
                    if header in header_to_index:
                        index = header_to_index[header]
                        if index < len(cells):
                            proxy[field] = cells[index].get_text(strip=True)

            if proxy:  # Only add if we extracted any data
                proxies.append(proxy)

        return proxies


def deduplicate_proxies(proxies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Deduplicate proxies by URL+Port combination.

    Args:
        proxies: List of proxy dictionaries

    Returns:
        Deduplicated list (keeps first occurrence)
    """
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []

    for proxy in proxies:
        # Extract URL+port as key
        url = proxy.get("url", "")
        if url:
            parsed = urlparse(url)
            key = f"{parsed.netloc}"  # netloc includes host:port
        else:
            # Construct from host+port
            host = proxy.get("host", "")
            port = proxy.get("port", "")
            key = f"{host}:{port}"

        if key not in seen:
            seen.add(key)
            unique.append(proxy)

    return unique


class ProxyValidator:
    """Validate proxy connectivity."""

    def __init__(
        self,
        timeout: float = 5.0,
        test_url: str = "http://www.gstatic.com/generate_204",
        level: ValidationLevel | None = None,
        concurrency: int = 50,
    ) -> None:
        """
        Initialize proxy validator.

        Args:
            timeout: Connection timeout in seconds
            test_url: URL to use for connectivity testing. Defaults to Google's
                     204 endpoint which is fast and doesn't rate limit.
            level: Validation level (BASIC, STANDARD, FULL). Defaults to STANDARD.
            concurrency: Maximum number of concurrent validations
        """
        from proxywhirl.models import ValidationLevel

        self.timeout = timeout
        self.test_url = test_url
        self.level = level or ValidationLevel.STANDARD
        self.concurrency = concurrency
        self._client: httpx.AsyncClient | None = None
        self._socks_client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """
        Get or create the shared HTTP client.

        Returns:
            Shared httpx.AsyncClient instance
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                },
            )
        return self._client

    async def _get_socks_client(self, proxy_url: str) -> httpx.AsyncClient:
        """
        Get or create the shared SOCKS client.

        Args:
            proxy_url: SOCKS proxy URL

        Returns:
            Shared httpx.AsyncClient instance configured for SOCKS
        """
        if self._socks_client is None:
            from httpx_socks import AsyncProxyTransport

            transport = AsyncProxyTransport.from_url(proxy_url)
            self._socks_client = httpx.AsyncClient(
                transport=transport,
                timeout=self.timeout,
                limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                },
            )
        return self._socks_client

    async def close(self) -> None:
        """Close all client connections and cleanup resources."""
        if self._client:
            await self._client.aclose()
            self._client = None
        if self._socks_client:
            await self._socks_client.aclose()
            self._socks_client = None

    async def __aenter__(self) -> ProxyValidator:
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()

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
        except (socket.timeout, ConnectionRefusedError, socket.gaierror, OSError):
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
            if proxy_url:
                async with httpx.AsyncClient(
                    proxy=proxy_url,
                    timeout=self.timeout,
                ) as client:
                    response = await client.get(self.test_url)
            else:
                # No proxy - use shared client for direct requests
                client = await self._get_client()
                response = await client.get(self.test_url)

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

    async def validate(self, proxy: dict[str, Any]) -> bool:
        """
        Validate proxy connectivity with fast TCP pre-check.

        Args:
            proxy: Proxy dictionary with 'url' key (e.g., "http://1.2.3.4:8080")

        Returns:
            True if proxy is working, False otherwise
        """
        proxy_url = proxy.get("url")
        if not proxy_url:
            return False

        try:
            # Parse host:port from URL
            from urllib.parse import urlparse

            parsed = urlparse(proxy_url)
            host = parsed.hostname
            port = parsed.port

            if not host or not port:
                return False

            # Fast TCP pre-check (async) - skip HTTP if port isn't even open
            try:
                _, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port),
                    timeout=min(3.0, self.timeout),  # Quick TCP timeout (relaxed)
                )
                writer.close()
                await writer.wait_closed()
            except (asyncio.TimeoutError, OSError, ConnectionRefusedError):
                return False

            # TCP passed - now test actual proxy functionality
            # httpx requires proxy at client initialization, not per-request
            is_socks = proxy_url.startswith(("socks4://", "socks5://"))

            if is_socks:
                # Create SOCKS client with transport
                from httpx_socks import AsyncProxyTransport

                transport = AsyncProxyTransport.from_url(proxy_url)
                async with httpx.AsyncClient(
                    transport=transport,
                    timeout=self.timeout,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    },
                ) as client:
                    response = await client.get(self.test_url)
                    return response.status_code in (200, 204)
            else:
                # Create HTTP client with proxy configured at initialization
                async with httpx.AsyncClient(
                    proxy=proxy_url,
                    timeout=self.timeout,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    },
                ) as client:
                    response = await client.get(self.test_url)
                    return response.status_code in (200, 204)
        except Exception:
            return False

    async def validate_batch(
        self,
        proxies: list[dict[str, Any]],
        progress_callback: Any | None = None,
    ) -> list[dict[str, Any]]:
        """
        Validate multiple proxies in parallel with concurrency control.

        Uses asyncio.Semaphore to limit concurrent validations based on
        the configured concurrency limit.

        Args:
            proxies: List of proxy dictionaries
            progress_callback: Optional callback(completed, total, valid_count) for progress

        Returns:
            List of working proxies (only proxies that passed validation)
        """
        if not proxies:
            return []

        # Create semaphore to limit concurrent validations
        semaphore = asyncio.Semaphore(self.concurrency)
        completed = 0
        valid_count = 0
        total = len(proxies)

        async def validate_with_semaphore(proxy: dict[str, Any]) -> tuple[dict[str, Any], bool]:
            """Validate a single proxy with semaphore control."""
            nonlocal completed, valid_count
            async with semaphore:
                try:
                    result = await self.validate(proxy)
                    completed += 1
                    if result:
                        valid_count += 1
                    if progress_callback:
                        progress_callback(completed, total, valid_count)
                    return (proxy, result)
                except Exception as e:
                    # If validation raises an exception, treat as failed
                    import logging

                    logging.getLogger(__name__).debug(
                        f"Validation error for {proxy.get('url')}: {e}"
                    )
                    completed += 1
                    if progress_callback:
                        progress_callback(completed, total, valid_count)
                    return (proxy, False)

        # Run all validations in parallel (semaphore controls concurrency)
        tasks = [validate_with_semaphore(proxy) for proxy in proxies]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out failed validations and exceptions
        validated: list[dict[str, Any]] = []
        for result in results:
            # Handle exceptions from gather
            if isinstance(result, Exception):
                continue
            # result is a tuple[dict[str, Any], bool]
            if not isinstance(result, tuple):
                continue
            proxy, is_valid = result
            if is_valid:
                validated.append(proxy)

        return validated


class ProxyFetcher:
    """Fetch proxies from various sources."""

    def __init__(
        self,
        sources: list[ProxySourceConfig] | None = None,
        validator: ProxyValidator | None = None,
    ) -> None:
        """
        Initialize proxy fetcher.

        Args:
            sources: List of proxy source configurations
            validator: ProxyValidator instance for validating fetched proxies
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

    def add_source(self, source: ProxySourceConfig) -> None:
        """
        Add a proxy source.

        Args:
            source: Proxy source configuration to add
        """
        self.sources.append(source)

    def remove_source(self, url: str) -> None:
        """
        Remove a proxy source by URL.

        Args:
            url: URL of source to remove
        """
        self.sources = [s for s in self.sources if str(s.url) != url]

    async def _get_client(self) -> httpx.AsyncClient:
        """
        Get or create the shared HTTP client.

        Returns:
            Shared httpx.AsyncClient instance
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                limits=httpx.Limits(max_connections=50, max_keepalive_connections=10),
            )
        return self._client

    async def close(self) -> None:
        """Close client connection and cleanup resources."""
        if self._client:
            await self._client.aclose()
            self._client = None
        # Also close validator's clients
        if self.validator:
            await self.validator.close()

    async def __aenter__(self) -> ProxyFetcher:
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    )
    async def fetch_from_source(self, source: ProxySourceConfig) -> list[dict[str, Any]]:
        """
        Fetch proxies from a single source.

        Args:
            source: Proxy source configuration

        Returns:
            List of proxy dictionaries

        Raises:
            ProxyFetchError: If fetching fails after retries
        """
        try:
            # Determine if browser rendering is needed
            html_content: str

            if source.render_mode == RenderMode.BROWSER:
                # Use browser rendering for JavaScript-heavy pages
                try:
                    from proxywhirl.browser import BrowserRenderer
                except ImportError as e:
                    raise ProxyFetchError(
                        "Browser rendering requires Playwright. "
                        "Install with: pip install 'proxywhirl[js]' or pip install playwright"
                    ) from e

                try:
                    async with BrowserRenderer() as renderer:
                        html_content = await renderer.render(str(source.url))
                except TimeoutError as e:
                    raise ProxyFetchError(f"Browser timeout fetching from {source.url}: {e}") from e
                except RuntimeError as e:
                    raise ProxyFetchError(f"Browser error fetching from {source.url}: {e}") from e
            else:
                # Use standard HTTP client for static pages
                client = await self._get_client()
                response = await client.get(str(source.url))
                response.raise_for_status()
                html_content = response.text

            # Use custom parser if provided
            if source.custom_parser:
                proxies_list: list[dict[str, Any]] = source.custom_parser.parse(html_content)
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

            # Parse proxies
            proxies_list: list[dict[str, Any]] = parser.parse(html_content)
            return proxies_list

        except httpx.HTTPStatusError as e:
            raise ProxyFetchError(f"HTTP error fetching from {source.url}: {e}") from e
        except httpx.RequestError as e:
            raise ProxyFetchError(f"Request error fetching from {source.url}: {e}") from e
        except Exception as e:
            raise ProxyFetchError(f"Error fetching from {source.url}: {e}") from e

    async def fetch_all(
        self,
        validate: bool = True,
        deduplicate: bool = True,
        fetch_progress_callback: Any | None = None,
        validate_progress_callback: Any | None = None,
    ) -> list[dict[str, Any]]:
        """
        Fetch proxies from all configured sources.

        Args:
            validate: Whether to validate proxies before returning
            deduplicate: Whether to deduplicate proxies
            fetch_progress_callback: Optional callback(completed, total, proxies_found) for fetch progress
            validate_progress_callback: Optional callback(completed, total, valid_count) for validation progress

        Returns:
            List of proxy dictionaries
        """
        all_proxies: list[dict[str, Any]] = []
        completed_sources = 0
        total_sources = len(self.sources)

        # Fetch from all sources with progress tracking
        async def fetch_with_progress(source: ProxySourceConfig) -> list[dict[str, Any]]:
            nonlocal completed_sources
            try:
                result = await self.fetch_from_source(source)
                completed_sources += 1
                if fetch_progress_callback:
                    fetch_progress_callback(
                        completed_sources, total_sources, len(all_proxies) + len(result)
                    )
                return result
            except Exception:
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

        # Validate if requested
        if validate:
            all_proxies = await self.validator.validate_batch(
                all_proxies, progress_callback=validate_progress_callback
            )

        return all_proxies

    async def start_periodic_refresh(
        self,
        callback: Any | None = None,
        interval: int | None = None,
    ) -> None:
        """
        Start periodic proxy refresh.

        Args:
            callback: Optional callback to invoke with new proxies
            interval: Override default refresh interval (seconds)
        """
        while True:
            # Determine interval (use first source's interval if not specified)
            refresh_interval = interval or (
                self.sources[0].refresh_interval if self.sources else 3600
            )

            await asyncio.sleep(refresh_interval)

            # Fetch new proxies
            proxies = await self.fetch_all()

            # Invoke callback if provided
            if callback:
                await callback(proxies)
