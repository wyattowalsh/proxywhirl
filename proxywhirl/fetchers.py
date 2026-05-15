"""
Proxy fetching and parsing functionality.

This module provides tools for fetching proxies from various sources and
parsing different formats (JSON, CSV, plain text, HTML tables).
"""

from __future__ import annotations

import asyncio
import csv
import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, NamedTuple

if TYPE_CHECKING:
    from proxywhirl.models import ValidationLevel
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from loguru import logger
from tenacity import (
    RetryCallState,
    retry,
    retry_if_exception,
    retry_if_exception_type,
    stop_after_attempt,
)

from proxywhirl.exceptions import ProxyFetchError, ProxyValidationError
from proxywhirl.models import ProxySourceConfig, RenderMode
from proxywhirl.utils import parse_proxy_url

# Check for httpx-socks availability (optional dependency for SOCKS proxy support)
try:
    from httpx_socks import AsyncProxyTransport

    SOCKS_AVAILABLE = True
except ImportError:
    AsyncProxyTransport = None  # type: ignore[misc, assignment]
    SOCKS_AVAILABLE = False
    logger.debug(
        "httpx-socks not installed. SOCKS4/SOCKS5 proxy validation will not work. "
        "Install with: uv sync or add httpx-socks to your dependencies"
    )


class JSONParser:
    """Parse JSON-formatted proxy lists with optional key extraction.

    Supports JSON arrays directly or arrays nested under a specified key.
    Validates required fields if specified.

    Attributes:
        key: Optional key to extract from JSON object before parsing array
        required_fields: List of field names that must be present in each proxy
    """

    def __init__(
        self,
        key: str | None = None,
        required_fields: list[str] | None = None,
    ) -> None:
        """
        Initialize JSON parser with optional key extraction and validation.

        Args:
            key : str | None
                Optional key to extract from JSON object. For example, if JSON is
                {"proxies": [{...}, {...}]}, set key="proxies" to extract the array.
                Default: None (expect array at top level).
            required_fields : list[str] | None
                Field names that must be present in each proxy dictionary.
                If any proxy is missing a required field, ProxyValidationError is raised.
                Default: None (no validation).

        Returns:
            None

        Example:
            >>> # Parse top-level array
            >>> parser = JSONParser()
            >>> proxies = parser.parse('[{"url": "http://1.2.3.4:8080"}]')
            >>> # Parse array nested under key
            >>> parser = JSONParser(key="proxies")
            >>> proxies = parser.parse('{"proxies": [{"url": "http://1.2.3.4:8080"}]}')
            >>> # Validate required fields
            >>> parser = JSONParser(required_fields=["url", "country"])
            >>> proxies = parser.parse('[{"url": "...", "country": "US"}]')
        """
        self.key = key
        self.required_fields = required_fields or []

    def parse(self, data: str) -> list[dict[str, Any]]:
        """
        Parse JSON string into list of proxy dictionaries.

        Extracts array from optional key, validates structure, and checks
        required fields if specified.

        Args:
            data : str
                JSON string containing proxy array or object with proxy array.

        Returns:
            list[dict[str, Any]]
                List of proxy dictionaries parsed from JSON.

        Raises:
            ProxyFetchError
                If JSON is invalid or missing expected key.
            ProxyValidationError
                If required fields are missing or entry is not a dict.

        Example:
            >>> parser = JSONParser()
            >>> data = '[{"url": "http://1.2.3.4:8080", "country": "US"}]'
            >>> proxies = parser.parse(data)
            >>> print(proxies[0])
            {'url': 'http://1.2.3.4:8080', 'country': 'US'}
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

        for index, proxy in enumerate(parsed):
            if not isinstance(proxy, dict):
                raise ProxyValidationError(f"Invalid proxy entry at index {index}: expected object")

        # Validate required fields
        if self.required_fields:
            for proxy in parsed:
                for field in self.required_fields:
                    if field not in proxy:
                        raise ProxyValidationError(f"Missing required field: {field}")

        return parsed


class CSVParser:
    """Parse CSV-formatted proxy lists with flexible header handling.

    Supports both header-based and column-indexed CSV formats.
    Can skip malformed rows or raise errors depending on configuration.

    Attributes:
        has_header: Whether first row contains column headers
        columns: Column names to use if no header row
        skip_invalid: Skip malformed rows instead of raising error
    """

    def __init__(
        self,
        has_header: bool = True,
        columns: list[str] | None = None,
        skip_invalid: bool = False,
    ) -> None:
        """
        Initialize CSV parser with header and column configuration.

        Args:
            has_header : bool
                Whether CSV has header row (default: True).
            columns : list[str] | None
                Column names to use when CSV has no header row.
                Required if has_header is False. Default: None.
            skip_invalid : bool
                Skip rows with incorrect column count instead of raising error
                (default: False). When True, malformed rows are silently skipped.

        Returns:
            None

        Example:
            >>> # Parse CSV with header
            >>> parser = CSVParser(has_header=True)
            >>> csv_data = "url,country,port\\n1.2.3.4,US,8080\\n"
            >>> proxies = parser.parse(csv_data)
            >>> # Parse CSV without header
            >>> parser = CSVParser(has_header=False, columns=["url", "country", "port"])
            >>> csv_data = "1.2.3.4,US,8080\\n"
            >>> proxies = parser.parse(csv_data)
        """
        self.has_header = has_header
        self.columns = columns
        self.skip_invalid = skip_invalid

    def parse(self, data: str) -> list[dict[str, Any]]:
        """
        Parse CSV string into list of proxy dictionaries.

        Converts each row to a dictionary with column names as keys.
        Handles both header-based and column-indexed formats.

        Args:
            data : str
                CSV string with proxy data.

        Returns:
            list[dict[str, Any]]
                List of proxy dictionaries, one per CSV row.

        Raises:
            ProxyFetchError
                If CSV is malformed (column count mismatch) and skip_invalid is False,
                or if columns are not specified for header-less CSV.

        Example:
            >>> parser = CSVParser(has_header=True)
            >>> csv = "url,country,port\\n1.2.3.4,US,8080\\n5.6.7.8,CN,9090\\n"
            >>> proxies = parser.parse(csv)
            >>> print(proxies[0])
            {'url': '1.2.3.4', 'country': 'US', 'port': '8080'}

        Note:
            - Empty input returns empty list
            - Column values are strings (no type conversion)
            - Set skip_invalid=True to handle partial/incomplete data
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
    """Parse plain text proxy lists (one proxy per line in IP:PORT format).

    Supports optional trailing metadata (e.g., country codes) which are ignored.
    Validates IP octets (0-255) and port ranges (1-65535) per RFC standards.

    Attributes:
        skip_invalid: Whether to skip invalid lines or raise error
        _IP_PORT_PATTERN: Pre-compiled regex for IP:PORT format (ReDoS-safe)
    """

    # Pre-compiled regex pattern for IP:PORT format with anchors to prevent ReDoS
    # Matches: 1.2.3.4:8080  or  1.2.3.4:8080:Country Name (trailing suffix ignored)
    # Groups: (1) IP address, (2) port number
    _IP_PORT_PATTERN = re.compile(r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})(?::.+)?$")

    def __init__(self, skip_invalid: bool = True) -> None:
        """
        Initialize plain text parser for line-based proxy lists.

        Args:
            skip_invalid : bool
                Skip invalid lines instead of raising error (default: True).
                When False, raises ProxyValidationError on first invalid line.

        Returns:
            None

        Example:
            >>> parser = PlainTextParser(skip_invalid=True)
            >>> text = "1.2.3.4:8080\\n5.6.7.8:9090\\ninvalid\\n"
            >>> proxies = parser.parse(text)  # Returns first 2 proxies
            >>> # Each proxy dict has {'url': 'http://1.2.3.4:8080'}
        """
        self.skip_invalid = skip_invalid

    def _is_valid_ip_port(self, ip_str: str, port_str: str) -> bool:
        """
        Validate IP address octets (0-255) and port range (1-65535).

        Performs RFC-compliant validation of IPv4 addresses and port numbers.
        Each octet must be 0-255. Port must be 1-65535 (0 is reserved).

        Args:
            ip_str : str
                IP address string (e.g., "192.168.1.1").
            port_str : str
                Port number string (e.g., "8080").

        Returns:
            bool
                True if IP and port are valid, False otherwise.

        Example:
            >>> parser = PlainTextParser()
            >>> parser._is_valid_ip_port("192.168.1.1", "8080")
            True
            >>> parser._is_valid_ip_port("256.1.1.1", "8080")  # Octet > 255
            False
            >>> parser._is_valid_ip_port("192.168.1.1", "70000")  # Port > 65535
            False
        """
        # Validate each IP octet is 0-255
        octets = ip_str.split(".")
        if len(octets) != 4:
            return False

        for octet in octets:
            try:
                value = int(octet)
                if value < 0 or value > 255:
                    return False
                # Reject leading zeros (e.g., "01", "001") except for "0" itself
                if octet != str(value):
                    return False
            except ValueError:
                return False

        # Validate port is 1-65535
        try:
            port = int(port_str)
            if port < 1 or port > 65535:
                return False
        except ValueError:
            return False

        return True

    def _validate_proxy_url(self, url: str) -> None:
        """Validate a full proxy URL from upstream source data."""
        try:
            parse_proxy_url(url)
        except ValueError as exception:
            raise ProxyFetchError(f"Invalid URL: {url}") from exception

    def parse(self, data: str) -> list[dict[str, Any]]:
        """
        Parse plain text proxy data (one proxy per line).

        Supports multiple input formats:
        - IP:PORT (converted to http://IP:PORT)
        - http://IP:PORT or https://IP:PORT
        - socks4://IP:PORT or socks5://IP:PORT
        - IP:PORT:CountryCode (trailing metadata ignored)

        Empty lines and comments (# prefix) are skipped. Validates IPv4 octets
        (0-255) and port ranges (1-65535) per RFC standards.

        Args:
            data : str
                Plain text string with one proxy per line.

        Returns:
            list[dict[str, Any]]
                List of proxy dictionaries with 'url' key set to full proxy URL.

        Raises:
            ProxyFetchError
                If invalid proxy format is encountered and skip_invalid is False.

        Example:
            >>> parser = PlainTextParser(skip_invalid=True)
            >>> text = '''
            ... 1.2.3.4:8080
            ... http://5.6.7.8:9090
            ... socks5://10.0.0.1:1080
            ... # This is a comment
            ... invalid data here
            ... '''
            >>> proxies = parser.parse(text)
            >>> for p in proxies:
            ...     print(p['url'])
            http://1.2.3.4:8080
            http://5.6.7.8:9090
            socks5://10.0.0.1:1080

        Note:
            - Empty lines and comments (# prefix) are skipped
            - IPv4 validation checks octets (0-255) and port (1-65535)
            - Leading zeros in octets are rejected (e.g., "192.01.1.1" invalid)
            - Regex is ReDoS-safe with anchors
            - Invalid proxies skipped if skip_invalid=True
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

            # Handle IP:PORT format (prepend http://)
            # Using pre-compiled pattern with anchors for ReDoS safety
            match = self._IP_PORT_PATTERN.match(line)
            if match:
                ip_str, port_str = match.groups()
                # Validate IP octet range (0-255) and port range (1-65535)
                if not self._is_valid_ip_port(ip_str, port_str):
                    if self.skip_invalid:
                        continue
                    raise ProxyFetchError(f"Invalid IP:PORT format: {line}")
                line = f"http://{ip_str}:{port_str}"

            # Validate URL format
            try:
                self._validate_proxy_url(line)
            except ProxyFetchError:
                if self.skip_invalid:
                    continue
                raise
            except Exception:
                if self.skip_invalid:
                    continue
                raise

            proxies.append({"url": line})

        return proxies


class HTMLTableParser:
    """Parse HTML table-formatted proxy lists with flexible column mapping.

    Extracts proxies from HTML <table> elements. Supports both:
    - Header-based mapping (matching header names to fields)
    - Column index mapping (selecting specific columns by position)

    Attributes:
        table_selector: CSS selector for table element (default: "table")
        column_map: Map from header names to proxy field names
        column_indices: Map from proxy field names to column indices
    """

    def __init__(
        self,
        table_selector: str = "table",
        column_map: dict[str, str] | None = None,
        column_indices: dict[str, int] | None = None,
    ) -> None:
        """
        Initialize HTML table parser with selector and column configuration.

        Args:
            table_selector : str
                CSS selector for table element (default: "table").
                Examples: "table", "table.proxies", "#proxy-table".
            column_map : dict[str, str] | None
                Map from HTML header names to proxy field names.
                Example: {"IP Address": "ip", "Port": "port"}.
                Default: None (use all columns in order).
            column_indices : dict[str, int] | None
                Map from proxy field names to column indices (0-based).
                Example: {"ip": 0, "port": 1}.
                Default: None (use column_map if provided).

        Returns:
            None

        Example:
            >>> # Extract from table with column_indices
            >>> parser = HTMLTableParser(
            ...     table_selector="table.proxies",
            ...     column_indices={"url": 0, "country": 2}
            ... )
            >>> # Extract from table with headers and column mapping
            >>> parser = HTMLTableParser(
            ...     column_map={"IP": "url", "Location": "country"}
            ... )
        """
        self.table_selector = table_selector
        self.column_map = column_map or {}
        self.column_indices = column_indices or {}

    def parse(self, data: str) -> list[dict[str, Any]]:
        """
        Parse HTML table into list of proxy dictionaries.

        Extracts all rows from the first matching table. Handles both
        header-based and index-based column extraction.

        Args:
            data : str
                HTML string containing table with proxy data.

        Returns:
            list[dict[str, Any]]
                List of proxy dictionaries, one per table row (excluding header).

        Raises:
            None - Returns empty list if no table found or on parse errors.

        Example:
            >>> html = '''
            ... <table class="proxies">
            ...     <tr><th>IP</th><th>Port</th><th>Country</th></tr>
            ...     <tr><td>1.2.3.4</td><td>8080</td><td>US</td></tr>
            ...     <tr><td>5.6.7.8</td><td>9090</td><td>CN</td></tr>
            ... </table>
            ... '''
            >>> parser = HTMLTableParser(
            ...     table_selector="table.proxies",
            ...     column_map={"IP": "url", "Port": "port"}
            ... )
            >>> proxies = parser.parse(html)
            >>> print(proxies[0])
            {'url': '1.2.3.4', 'port': '8080'}

        Note:
            - Returns empty list if no matching table found
            - Automatically detects header row by looking for <th> elements
            - Empty cells are extracted as empty strings
            - Both column_indices and column_map can be used (indices take priority)
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


class GeonodeParser:
    """Parse GeoNode API JSON response format.

    GeoNode API returns: {"data": [{"ip": "...", "port": "...", "protocols": ["http"]}, ...]}
    This parser extracts and transforms to standard format: {"url": "http://ip:port", "protocol": "http"}
    """

    def parse(self, data: str) -> list[dict[str, Any]]:
        """Parse GeoNode API response.

        Args:
            data: JSON string from GeoNode API

        Returns:
            List of proxy dictionaries in standard format
        """
        try:
            parsed = json.loads(data)
        except json.JSONDecodeError as e:
            raise ProxyFetchError(f"Invalid JSON from GeoNode: {e}") from e

        # Extract data array
        if not isinstance(parsed, dict) or "data" not in parsed:
            raise ProxyFetchError("GeoNode response missing 'data' key")

        items = parsed["data"]
        if not isinstance(items, list):
            raise ProxyFetchError("GeoNode 'data' is not an array")

        proxies = []
        for item in items:
            if not isinstance(item, dict):
                continue

            ip = item.get("ip")
            port = item.get("port")
            protocols = item.get("protocols", [])

            if not ip or not port or not isinstance(protocols, list):
                continue

            # GeoNode may return port as string or int
            port_str = str(port)
            host = str(ip)
            if ":" in host and not (host.startswith("[") and host.endswith("]")):
                host = f"[{host}]"

            # Create proxy entry for each protocol
            for protocol in protocols:
                if not isinstance(protocol, str):
                    continue
                protocol_lower = protocol.lower()
                url = f"{protocol_lower}://{host}:{port_str}"
                try:
                    parse_proxy_url(url)
                except ValueError:
                    continue
                proxies.append({"url": url, "protocol": protocol_lower})

        return proxies


def deduplicate_proxies(proxies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Deduplicate proxies by URL+Port combination.

    Hostnames are normalized to lowercase since DNS names are case-insensitive
    (RFC 4343). This ensures that "PROXY.EXAMPLE.COM:8080" and
    "proxy.example.com:8080" are correctly identified as duplicates.

    Handles edge cases including:
    - IPv6 addresses: [2001:db8::1]:8080 (preserved as-is, already case-insensitive)
    - IDN hostnames: Прокси.рф:8080 (lowercased correctly)
    - Mixed-case DNS names: Proxy.EXAMPLE.com:8080 (lowercased for comparison)

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
            # Normalize netloc to lowercase (RFC 4343: DNS names are case-insensitive)
            # netloc includes host:port (or [ipv6]:port)
            # IPv6 addresses: [2001:db8::1]:8080 -> lowercases to same (hex already lowercase)
            # IDN domains: Прокси.рф:8080 -> прокси.рф:8080
            key = parsed.netloc.lower()
        else:
            # Construct from host+port
            host = proxy.get("host", "")
            port = proxy.get("port", "")
            if not host or not port:
                # Skip proxies with incomplete host+port
                continue
            # Normalize hostname to lowercase (handles IDN, IPv6, and DNS names)
            key = f"{host.lower()}:{port}"

        if key not in seen:
            seen.add(key)
            unique.append(proxy)

    return unique


class ValidationResult(NamedTuple):
    """Result of proxy validation with timing metrics."""

    is_valid: bool
    response_time_ms: float | None  # None if validation failed before timing

    def __bool__(self) -> bool:
        """Allow ValidationResult to be used in boolean context."""
        return self.is_valid


def _get_tls_verify() -> bool | str:
    """Return TLS verification setting for httpx clients.

    Reads ``PROXYWHIRL_CA_BUNDLE`` environment variable. If set, uses
    the specified CA bundle path. Otherwise defaults to ``True``.
    """
    ca_bundle = os.environ.get("PROXYWHIRL_CA_BUNDLE")
    return ca_bundle if ca_bundle else True


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

        self.timeout = timeout
        self._custom_test_url = test_url  # None means rotate
        self._test_url_index = 0
        self._https_test_url_index = 0
        self.level = level or ValidationLevel.STANDARD
        self.concurrency = concurrency
        self._client: httpx.AsyncClient | None = None
        self._socks_client: httpx.AsyncClient | None = None

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
        Get or create the shared SOCKS client.

        Args:
            proxy_url: SOCKS proxy URL

        Returns:
            Shared httpx.AsyncClient instance configured for SOCKS

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

        if self._socks_client is None:
            transport = AsyncProxyTransport.from_url(proxy_url)
            self._socks_client = httpx.AsyncClient(
                transport=transport,
                timeout=self.timeout,
                verify=_get_tls_verify(),
                limits=httpx.Limits(max_connections=1000, max_keepalive_connections=100),
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

    def _get_cache_key(self, proxy: dict[str, Any]) -> str:
        """Generate cache key for a proxy.

        Args:
            proxy: Proxy dictionary with 'url' key

        Returns:
            Cache key string (hash of proxy URL)
        """
        proxy_url = proxy.get("url", "")
        return hashlib.md5(proxy_url.encode(), usedforsecurity=False).hexdigest()

    def _get_cached_result(self, proxy: dict[str, Any]) -> ValidationResult | None:
        """Get validation result from cache if not expired.

        Args:
            proxy: Proxy dictionary to check cache for

        Returns:
            ValidationResult if cached and not expired, None otherwise
        """
        cache_key = self._get_cache_key(proxy)
        if cache_key in self._validation_cache:
            result, timestamp = self._validation_cache[cache_key]
            if time.time() - timestamp < self._cache_ttl_seconds:
                logger.debug(f"Validation cache hit for {proxy.get('url')}")
                return result
            else:
                # Cache expired - remove it
                del self._validation_cache[cache_key]
        return None

    def _set_cached_result(self, proxy: dict[str, Any], result: ValidationResult) -> None:
        """Cache a validation result.

        Args:
            proxy: Proxy dictionary that was validated
            result: Validation result to cache
        """
        cache_key = self._get_cache_key(proxy)
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
                    verify=_get_tls_verify(),
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
        # Check cache first
        cached_result = self._get_cached_result(proxy)
        if cached_result is not None:
            return cached_result

        proxy_url = proxy.get("url")
        if not proxy_url:
            result = ValidationResult(is_valid=False, response_time_ms=None)
            self._set_cached_result(proxy, result)
            return result

        try:
            # Parse host:port from URL
            parsed = urlparse(proxy_url)
            host = parsed.hostname
            port = parsed.port

            if not host or not port:
                result = ValidationResult(is_valid=False, response_time_ms=None)
                self._set_cached_result(proxy, result)
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
                self._set_cached_result(proxy, result)
                return result

            # TCP passed - now test actual proxy functionality with timing
            # httpx requires proxy at client initialization, not per-request
            is_socks = proxy_url.startswith(("socks4://", "socks5://"))
            proxy_protocol = proxy.get("protocol")
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
                    self._set_cached_result(proxy, result)
                    return result

                if AsyncProxyTransport is None:
                    # This should not happen if SOCKS_AVAILABLE is True, but guard against it
                    logger.error("SOCKS_AVAILABLE is True but AsyncProxyTransport is None")
                    result = ValidationResult(is_valid=False, response_time_ms=None)
                    self._set_cached_result(proxy, result)
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
                    self._set_cached_result(proxy, result)
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
                    self._set_cached_result(proxy, result)
                    return result
        except Exception:
            result = ValidationResult(is_valid=False, response_time_ms=None)
            self._set_cached_result(proxy, result)
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
                except Exception as e:
                    # If validation raises an exception, treat as failed
                    import logging

                    logging.getLogger(__name__).debug(
                        f"Validation error for {proxy.get('url')}: {e}"
                    )
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

        # Deduplicate by URL to avoid testing the same proxy multiple times
        seen: set[str] = set()
        unique_proxies: list[dict[str, Any]] = []
        for p in http_proxies:
            url = p.get("url", "")
            if url and url not in seen:
                seen.add(url)
                unique_proxies.append(p)

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
                    except Exception:
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


# Retryable HTTP status codes for proxy fetching
RETRYABLE_STATUS_CODES = {
    429,  # Too Many Requests
    503,  # Service Unavailable
    502,  # Bad Gateway
    504,  # Gateway Timeout
}


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
        validator: ProxyValidator instance for validating fetched proxies
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
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                verify=_get_tls_verify(),
                limits=httpx.Limits(max_connections=50, max_keepalive_connections=10),
                http2=True,
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
                logger.debug(f"Request cache hit for {url}")
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

                try:
                    async with BrowserRenderer() as renderer:
                        html_content = await renderer.render(source_url)
                except TimeoutError as e:
                    raise ProxyFetchError(f"Browser timeout fetching from {source_url}: {e}") from e
                except RuntimeError as e:
                    raise ProxyFetchError(f"Browser error fetching from {source_url}: {e}") from e

                # Cache the rendered content
                self._set_cached_response(source_url, html_content)
            else:
                # Use standard HTTP client for static pages
                client = await self._get_client()
                response = await client.get(source_url)
                response.raise_for_status()
                html_content = response.text

                # Cache the response content
                self._set_cached_response(source_url, html_content)

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

            # Apply source protocol if specified (for plain text SOCKS sources)
            if source.protocol and source.protocol != "http":
                for proxy in proxies_list:
                    if "url" in proxy:
                        # Replace http:// with the specified protocol
                        url = proxy["url"]
                        if url.startswith("http://"):
                            proxy["url"] = f"{source.protocol}://{url[7:]}"
                        # Set protocol field explicitly
                        proxy["protocol"] = source.protocol

            return proxies_list

        except httpx.HTTPStatusError as e:
            # Let retryable HTTP errors (429, 503, 502, 504) bubble up to retry decorator
            # Only convert to ProxyFetchError for non-retryable errors
            if e.response.status_code not in RETRYABLE_STATUS_CODES:
                raise ProxyFetchError(f"HTTP error fetching from {source.url}: {e}") from e
            raise  # Re-raise for retry decorator to handle
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
                completed_sources += 1
                if fetch_progress_callback:
                    fetch_progress_callback(
                        completed_sources, total_sources, len(all_proxies) + len(result)
                    )
                return result
            except Exception:
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

        # Validate all proxies if requested
        if validate:
            return await self.validator.validate_batch(
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
