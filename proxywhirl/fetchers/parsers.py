"""Proxy list parsers and normalization helpers."""

from __future__ import annotations

import csv
import json
import re
from typing import Any
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from proxywhirl.exceptions import ProxyFetchError, ProxyValidationError
from proxywhirl.fetchers.shared import (
    FETCH_MAX_RESPONSE_BYTES,
    HTML_PARSE_MAX_BYTES,
    HTML_PARSE_MAX_ROWS,
)
from proxywhirl.models import ProxySourceConfig


def _ensure_bounded_text(data: str, max_bytes: int, *, label: str) -> None:
    """Reject text whose UTF-8 representation exceeds ``max_bytes``."""
    if max_bytes < 1:
        raise ValueError("max_bytes must be positive")

    # Every Unicode code point needs at least one UTF-8 byte. This fast path
    # rejects the common oversized case without allocating another full body.
    if len(data) > max_bytes:
        raise ProxyFetchError(f"{label} input exceeds configured limit of {max_bytes} bytes")

    bytes_seen = 0
    for offset in range(0, len(data), 4096):
        bytes_seen += len(data[offset : offset + 4096].encode("utf-8", errors="replace"))
        if bytes_seen > max_bytes:
            raise ProxyFetchError(f"{label} input exceeds configured limit of {max_bytes} bytes")


def _truncate_text_to_utf8_bytes(data: str, max_bytes: int) -> str:
    """Return the longest character-aligned prefix within ``max_bytes``."""
    if max_bytes < 1:
        raise ValueError("max_bytes must be positive")
    if len(data) <= max_bytes:
        try:
            _ensure_bounded_text(data, max_bytes, label="Parser")
        except ProxyFetchError:
            pass
        else:
            return data

    chunks: list[str] = []
    bytes_seen = 0
    for offset in range(0, len(data), 4096):
        chunk = data[offset : offset + 4096]
        encoded = chunk.encode("utf-8", errors="replace")
        remaining = max_bytes - bytes_seen
        if len(encoded) <= remaining:
            chunks.append(chunk)
            bytes_seen += len(encoded)
            continue

        low = 0
        high = len(chunk)
        while low < high:
            midpoint = (low + high + 1) // 2
            prefix_size = len(chunk[:midpoint].encode("utf-8", errors="replace"))
            if prefix_size <= remaining:
                low = midpoint
            else:
                high = midpoint - 1
        if low:
            chunks.append(chunk[:low])
        break

    return "".join(chunks)


def _parse_proxy_url_compat(url: str):
    """Resolve parse_proxy_url via package facade (patch-compatible with monolith)."""
    from proxywhirl.fetchers import parse_proxy_url

    return parse_proxy_url(url)


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
        max_bytes: int = HTML_PARSE_MAX_BYTES,
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
            max_bytes : int
                Maximum UTF-8 input size accepted before JSON decoding.

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
        if max_bytes < 1:
            raise ValueError("max_bytes must be positive")
        self.max_bytes = max_bytes

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
        _ensure_bounded_text(data, self.max_bytes, label="JSON parser")
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
        max_bytes: int = HTML_PARSE_MAX_BYTES,
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
            max_bytes : int
                Maximum UTF-8 input size accepted before CSV parsing.

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
        if max_bytes < 1:
            raise ValueError("max_bytes must be positive")
        self.max_bytes = max_bytes

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
        _ensure_bounded_text(data, self.max_bytes, label="CSV parser")
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
                proxies.append(dict(zip(headers, row, strict=True)))
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
                proxies.append(dict(zip(self.columns, row, strict=True)))

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

    def __init__(
        self,
        skip_invalid: bool = True,
        max_bytes: int = HTML_PARSE_MAX_BYTES,
    ) -> None:
        """
        Initialize plain text parser for line-based proxy lists.

        Args:
            skip_invalid : bool
                Skip invalid lines instead of raising error (default: True).
                When False, raises ProxyValidationError on first invalid line.
            max_bytes : int
                Maximum UTF-8 input size accepted before line parsing.

        Returns:
            None

        Example:
            >>> parser = PlainTextParser(skip_invalid=True)
            >>> text = "1.2.3.4:8080\\n5.6.7.8:9090\\ninvalid\\n"
            >>> proxies = parser.parse(text)  # Returns first 2 proxies
            >>> # Each proxy dict has {'url': 'http://1.2.3.4:8080'}
        """
        self.skip_invalid = skip_invalid
        if max_bytes < 1:
            raise ValueError("max_bytes must be positive")
        self.max_bytes = max_bytes

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
            _parse_proxy_url_compat(url)
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
        _ensure_bounded_text(data, self.max_bytes, label="Plain-text parser")
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
            except (ValueError, TypeError):
                if self.skip_invalid:
                    continue
                raise

            proxies.append({"url": line})

        return proxies


def _format_proxy_host(host: str) -> str:
    if ":" in host and not (host.startswith("[") and host.endswith("]")):
        return f"[{host}]"
    return host


def _candidate_proxy_protocol(source: ProxySourceConfig | None, proxy: dict[str, Any]) -> str:
    protocol = proxy.get("protocol")
    if isinstance(protocol, str) and protocol.strip():
        return protocol.strip().lower()
    if source is not None and isinstance(source.protocol, str) and source.protocol.strip():
        return source.protocol.strip().lower()
    return "http"


def _apply_protocol_override(url: str, protocol: str) -> str:
    parsed = urlparse(url)
    if not parsed.hostname:
        return url
    host = _format_proxy_host(parsed.hostname)
    port = parsed.port
    hostport = f"{host}:{port}" if port else host
    if parsed.username is None and parsed.password is None:
        return f"{protocol}://{hostport}"
    from urllib.parse import quote

    userinfo = quote(parsed.username or "", safe="")
    if parsed.password is not None:
        userinfo = f"{userinfo}:{quote(parsed.password, safe='')}"
    return f"{protocol}://{userinfo}@{hostport}"


def normalize_parsed_proxy_rows(
    proxies: list[dict[str, Any]],
    source: ProxySourceConfig | None = None,
) -> list[dict[str, Any]]:
    """Normalize host/port JSON/CSV/HTML rows into canonical ``url`` entries."""
    protocol_default = _candidate_proxy_protocol(source, {})
    normalized: list[dict[str, Any]] = []

    for proxy in proxies:
        if not isinstance(proxy, dict):
            continue

        row = dict(proxy)
        protocol = _candidate_proxy_protocol(source, row)
        url_value = row.get("url")
        port = row.get("port")
        host = row.get("host") or row.get("hostname") or row.get("ip")

        built_url: str | None = None
        if isinstance(url_value, str) and url_value.strip():
            stripped = url_value.strip()
            if "://" in stripped:
                parsed = urlparse(stripped)
                scheme = parsed.scheme.lower() if parsed.scheme else protocol_default
                if source and source.protocol:
                    scheme = source.protocol.strip().lower()
                elif isinstance(row.get("protocol"), str) and row["protocol"].strip():
                    scheme = row["protocol"].strip().lower()
                built_url = _apply_protocol_override(stripped, scheme)
            elif port not in (None, ""):
                built_url = f"{protocol}://{_format_proxy_host(stripped)}:{port}"
            else:
                built_url = f"{protocol}://{_format_proxy_host(stripped)}"

        if built_url is None and isinstance(host, str) and host.strip() and port not in (None, ""):
            built_url = f"{protocol}://{_format_proxy_host(host.strip())}:{port}"

        if not built_url:
            continue

        try:
            _parse_proxy_url_compat(built_url)
        except ValueError:
            continue

        row["url"] = built_url
        parsed_final = urlparse(built_url)
        if parsed_final.scheme:
            row["protocol"] = parsed_final.scheme.lower()
        normalized.append(row)

    return normalized


async def _read_bounded_response_text(
    response: httpx.Response,
    max_bytes: int = FETCH_MAX_RESPONSE_BYTES,
) -> str:
    """Read response body up to ``max_bytes``."""
    if max_bytes < 1:
        raise ValueError("max_bytes must be positive")

    body = bytearray()
    async for chunk in response.aiter_bytes(chunk_size=65536):
        if not chunk:
            continue
        remaining = max_bytes - len(body)
        if remaining <= 0:
            break
        body.extend(chunk[:remaining])
        if len(body) >= max_bytes:
            break
    return bytes(body).decode(response.encoding or "utf-8", errors="replace")


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
        max_bytes: int = HTML_PARSE_MAX_BYTES,
        max_rows: int = HTML_PARSE_MAX_ROWS,
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
            max_bytes : int
                Maximum UTF-8 input size retained for HTML parsing.
            max_rows : int
                Maximum number of table data rows returned.

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
        self.max_bytes = max_bytes
        self.max_rows = max_rows

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
        data = _truncate_text_to_utf8_bytes(data, self.max_bytes)

        soup = BeautifulSoup(data, "html.parser")
        table = soup.select_one(self.table_selector)

        if not table:
            return []

        proxies = []
        rows = table.find_all("tr")
        if len(rows) > self.max_rows + 1:
            rows = rows[: self.max_rows + 1]

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

    def __init__(self, max_bytes: int = HTML_PARSE_MAX_BYTES) -> None:
        """Initialize the parser with a bounded input size."""
        if max_bytes < 1:
            raise ValueError("max_bytes must be positive")
        self.max_bytes = max_bytes

    def parse(self, data: str) -> list[dict[str, Any]]:
        """Parse GeoNode API response.

        Args:
            data: JSON string from GeoNode API

        Returns:
            List of proxy dictionaries in standard format
        """
        _ensure_bounded_text(data, self.max_bytes, label="GeoNode parser")
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
                    _parse_proxy_url_compat(url)
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
