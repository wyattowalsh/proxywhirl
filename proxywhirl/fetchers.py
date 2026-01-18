"""
Proxy fetching and parsing functionality.

This module provides tools for fetching proxies from various sources and
parsing different formats (JSON, CSV, plain text, HTML tables).
"""

from __future__ import annotations

import asyncio
import csv
import json
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

    # Pre-compiled regex pattern for IP:PORT format with anchors to prevent ReDoS
    # Pattern: ^(\d{1,3}\.){3}\d{1,3}:\d{1,5}$
    # Groups: (1) IP address, (2) port number
    _IP_PORT_PATTERN = re.compile(r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})$")

    def __init__(self, skip_invalid: bool = False) -> None:
        """
        Initialize plain text parser.

        Args:
            skip_invalid: Skip invalid URLs instead of raising error
        """
        self.skip_invalid = skip_invalid

    def _is_valid_ip_port(self, ip_str: str, port_str: str) -> bool:
        """Validate IP address octets (0-255) and port range (1-65535).

        Args:
            ip_str: IP address string (e.g., "192.168.1.1")
            port_str: Port number string (e.g., "8080")

        Returns:
            True if IP and port are valid, False otherwise
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

    def parse(self, data: str) -> list[dict[str, Any]]:
        """
        Parse plain text proxy data.

        Args:
            data: Plain text string with one proxy per line
                  Supports formats: IP:PORT, http://IP:PORT, socks5://IP:PORT

        Returns:
            List of proxy dictionaries with 'url' key

        Raises:
            ProxyFetchError: If invalid proxy format is encountered and skip_invalid=False
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


class ProxyValidator:
    """Validate proxy connectivity with metrics collection."""

    # Multiple test URLs to avoid single-point bottleneck and rate limiting
    TEST_URLS = [
        "http://www.gstatic.com/generate_204",  # Google - fast, no rate limit
        "http://cp.cloudflare.com/generate_204",  # Cloudflare - very fast
        "http://connectivitycheck.android.com/generate_204",  # Android check
        "http://www.msftconnecttest.com/connecttest.txt",  # Microsoft
    ]

    def __init__(
        self,
        timeout: float = 5.0,
        test_url: str | None = None,
        level: ValidationLevel | None = None,
        concurrency: int = 50,
    ) -> None:
        """
        Initialize proxy validator.

        Args:
            timeout: Connection timeout in seconds
            test_url: URL to use for connectivity testing. If None, rotates between
                     multiple fast endpoints (Google, Cloudflare, etc.)
            level: Validation level (BASIC, STANDARD, FULL). Defaults to STANDARD.
            concurrency: Maximum number of concurrent validations
        """
        from proxywhirl.models import ValidationLevel

        self.timeout = timeout
        self._custom_test_url = test_url  # None means rotate
        self._test_url_index = 0
        self.level = level or ValidationLevel.STANDARD
        self.concurrency = concurrency
        self._client: httpx.AsyncClient | None = None
        self._socks_client: httpx.AsyncClient | None = None

    @property
    def test_url(self) -> str:
        """Get current test URL, rotating through multiple endpoints."""
        if self._custom_test_url:
            return self._custom_test_url
        # Rotate through test URLs to distribute load
        url = self.TEST_URLS[self._test_url_index % len(self.TEST_URLS)]
        self._test_url_index += 1
        return url

    async def _get_client(self) -> httpx.AsyncClient:
        """
        Get or create the shared HTTP client.

        Returns:
            Shared httpx.AsyncClient instance
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
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

    async def validate(self, proxy: dict[str, Any]) -> ValidationResult:
        """
        Validate proxy connectivity with fast TCP pre-check and timing metrics.

        Args:
            proxy: Proxy dictionary with 'url' key (e.g., "http://1.2.3.4:8080")

        Returns:
            ValidationResult with is_valid flag and response_time_ms (if successful)
        """
        proxy_url = proxy.get("url")
        if not proxy_url:
            return ValidationResult(is_valid=False, response_time_ms=None)

        try:
            # Parse host:port from URL
            parsed = urlparse(proxy_url)
            host = parsed.hostname
            port = parsed.port

            if not host or not port:
                return ValidationResult(is_valid=False, response_time_ms=None)

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
                return ValidationResult(is_valid=False, response_time_ms=None)

            # TCP passed - now test actual proxy functionality with timing
            # httpx requires proxy at client initialization, not per-request
            is_socks = proxy_url.startswith(("socks4://", "socks5://"))
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
                    return ValidationResult(is_valid=False, response_time_ms=None)

                if AsyncProxyTransport is None:
                    # This should not happen if SOCKS_AVAILABLE is True, but guard against it
                    logger.error("SOCKS_AVAILABLE is True but AsyncProxyTransport is None")
                    return ValidationResult(is_valid=False, response_time_ms=None)

                transport = AsyncProxyTransport.from_url(proxy_url)
                async with httpx.AsyncClient(
                    transport=transport,
                    timeout=self.timeout,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    },
                ) as client:
                    response = await client.get(self.test_url)
                    elapsed_ms = (time.perf_counter() - start_time) * 1000
                    is_valid = response.status_code in (200, 204)
                    return ValidationResult(
                        is_valid=is_valid,
                        response_time_ms=elapsed_ms if is_valid else None,
                    )
            else:
                # Create HTTP client with proxy configured at initialization
                async with httpx.AsyncClient(
                    proxy=proxy_url,
                    timeout=self.timeout,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    },
                ) as client:
                    response = await client.get(self.test_url)
                    elapsed_ms = (time.perf_counter() - start_time) * 1000
                    is_valid = response.status_code in (200, 204)
                    return ValidationResult(
                        is_valid=is_valid,
                        response_time_ms=elapsed_ms if is_valid else None,
                    )
        except Exception:
            return ValidationResult(is_valid=False, response_time_ms=None)

    async def validate_batch(
        self,
        proxies: list[dict[str, Any]],
        progress_callback: Any | None = None,
    ) -> list[dict[str, Any]]:
        """
        Validate multiple proxies in parallel with concurrency control and metrics.

        Uses asyncio.Semaphore to limit concurrent validations based on
        the configured concurrency limit. Records response time for valid proxies.

        Args:
            proxies: List of proxy dictionaries
            progress_callback: Optional callback(completed, total, valid_count) for progress

        Returns:
            List of working proxies with response_time_ms added to each
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
        Fetch proxies from a single source.

        Includes automatic retry with exponential backoff for:
        - HTTP 429 (Too Many Requests) - respects Retry-After header
        - HTTP 503 (Service Unavailable)
        - HTTP 502 (Bad Gateway)
        - HTTP 504 (Gateway Timeout)
        - Network timeouts

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
