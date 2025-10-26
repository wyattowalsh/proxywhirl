"""
Proxy fetching and parsing functionality.

This module provides tools for fetching proxies from various sources and
parsing different formats (JSON, CSV, plain text, HTML tables).
"""

import asyncio
import csv
import json
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from proxywhirl.models import ValidationLevel
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from proxywhirl.exceptions import ProxyFetchError, ProxyValidationError
from proxywhirl.models import RenderMode


class ProxySourceConfig(BaseModel):
    """Configuration for a proxy source."""

    url: str
    format: str = "json"  # json, csv, text, html
    refresh_interval: int = 3600  # seconds
    custom_parser: Optional[Any] = None
    render_mode: RenderMode = RenderMode.STATIC  # Page rendering mode


class JSONParser:
    """Parse JSON-formatted proxy lists."""

    def __init__(
        self,
        key: Optional[str] = None,
        required_fields: Optional[list[str]] = None,
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
        columns: Optional[list[str]] = None,
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

        Returns:
            List of proxy dictionaries with 'url' key
        """
        proxies = []

        for line in data.split("\n"):
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Skip comments
            if line.startswith("#"):
                continue

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
        column_map: Optional[dict[str, str]] = None,
        column_indices: Optional[dict[str, int]] = None,
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
        test_url: str = "http://httpbin.org/ip",
        level: Optional["ValidationLevel"] = None,
        concurrency: int = 50,
    ) -> None:
        """
        Initialize proxy validator.

        Args:
            timeout: Connection timeout in seconds
            test_url: URL to use for connectivity testing
            level: Validation level (BASIC, STANDARD, FULL). Defaults to STANDARD.
            concurrency: Maximum number of concurrent validations
        """
        from proxywhirl.models import ValidationLevel

        self.timeout = timeout
        self.test_url = test_url
        self.level = level or ValidationLevel.STANDARD
        self.concurrency = concurrency

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

    async def _validate_http_request(self, proxy_url: Optional[str] = None) -> bool:
        """
        Validate HTTP request through proxy.

        Args:
            proxy_url: Full proxy URL (e.g., "http://proxy.example.com:8080")
                      If None, makes request without proxy (for testing)

        Returns:
            True if HTTP request succeeds, False otherwise
        """
        try:
            client_kwargs: dict[str, Any] = {"timeout": self.timeout}
            if proxy_url:
                client_kwargs["proxies"] = proxy_url

            async with httpx.AsyncClient(**client_kwargs) as client:
                response = await client.get(self.test_url)
                return response.status_code == 200
        except (
            httpx.TimeoutException,
            httpx.ConnectError,
            httpx.NetworkError,
            Exception,
        ):
            # Request failed - timeout, connection error, network error, or other
            return False

    async def check_anonymity(self, proxy_url: Optional[str] = None) -> Optional[str]:
        """
        Check proxy anonymity level by detecting IP leakage.

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
            client_kwargs: dict[str, Any] = {"timeout": self.timeout}
            if proxy_url:
                client_kwargs["proxies"] = proxy_url

            async with httpx.AsyncClient(**client_kwargs) as client:
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
        Validate proxy connectivity.

        Args:
            proxy: Proxy dictionary to validate

        Returns:
            True if proxy is working, False otherwise
        """
        proxy_url = proxy.get("url")
        if not proxy_url:
            return False

        try:
            # HTTPX requires proxy as string in environment variable format
            # or using mounts. For now, use simple approach.
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Try to connect through proxy by setting it as default
                response = await client.get(
                    self.test_url,
                    extensions={"proxy": proxy_url},
                )
                return response.status_code == 200
        except Exception:
            # Any error means proxy is not working
            return False

    async def validate_batch(self, proxies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Validate multiple proxies in parallel with concurrency control.

        Uses asyncio.Semaphore to limit concurrent validations based on
        the configured concurrency limit.

        Args:
            proxies: List of proxy dictionaries

        Returns:
            List of working proxies (only proxies that passed validation)
        """
        if not proxies:
            return []

        # Create semaphore to limit concurrent validations
        semaphore = asyncio.Semaphore(self.concurrency)

        async def validate_with_semaphore(proxy: dict[str, Any]) -> tuple[dict[str, Any], bool]:
            """Validate a single proxy with semaphore control."""
            async with semaphore:
                try:
                    result = await self.validate(proxy)
                    return (proxy, result)
                except Exception:
                    # If validation raises an exception, treat as failed
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
        sources: Optional[list["ProxySourceConfig"]] = None,
        validator: Optional[ProxyValidator] = None,
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
            "text": PlainTextParser,
            "html": HTMLTableParser,
        }

    def add_source(self, source: "ProxySourceConfig") -> None:
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
        self.sources = [s for s in self.sources if s.url != url]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    )
    async def fetch_from_source(self, source: "ProxySourceConfig") -> list[dict[str, Any]]:
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
                        html_content = await renderer.render(source.url)
                except TimeoutError as e:
                    raise ProxyFetchError(f"Browser timeout fetching from {source.url}: {e}") from e
                except RuntimeError as e:
                    raise ProxyFetchError(f"Browser error fetching from {source.url}: {e}") from e
            else:
                # Use standard HTTP client for static pages
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(source.url)
                    response.raise_for_status()
                    html_content = response.text

            # Get parser
            if source.custom_parser:
                parser = source.custom_parser
            elif source.format in self._parsers:
                parser_class = self._parsers[source.format]
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
        self, validate: bool = True, deduplicate: bool = True
    ) -> list[dict[str, Any]]:
        """
        Fetch proxies from all configured sources.

        Args:
            validate: Whether to validate proxies before returning
            deduplicate: Whether to deduplicate proxies

        Returns:
            List of proxy dictionaries
        """
        all_proxies: list[dict[str, Any]] = []

        # Fetch from all sources in parallel
        tasks = [self.fetch_from_source(source) for source in self.sources]
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
            all_proxies = await self.validator.validate_batch(all_proxies)

        return all_proxies

    async def start_periodic_refresh(
        self,
        callback: Optional[Any] = None,
        interval: Optional[int] = None,
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
