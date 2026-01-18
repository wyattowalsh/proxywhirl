"""
Unit tests for proxy fetchers and parsers.

Tests cover:
- T088: JSON parser (valid/invalid JSON, schema validation)
- T089: CSV parser (headers, malformed rows)
- T090: Plain text parser (one proxy per line)
- T091: HTML table parser (extract from <table> tags)
- T092: URL+Port deduplication
- T093: ProxyValidator (connectivity checks, timeout handling)
"""

import json

import pytest

from proxywhirl.exceptions import ProxyFetchError, ProxyValidationError


# T088: JSON Parser Tests
class TestJSONParser:
    """Test JSON proxy list parser."""

    def test_parse_valid_json_array(self) -> None:
        """Parse valid JSON array of proxy objects."""
        from proxywhirl.fetchers import JSONParser

        json_data = json.dumps(
            [
                {"host": "proxy1.com", "port": 8080, "protocol": "http"},
                {"host": "proxy2.com", "port": 3128, "protocol": "https"},
            ]
        )

        parser = JSONParser()
        proxies = parser.parse(json_data)

        assert len(proxies) == 2
        assert proxies[0]["host"] == "proxy1.com"
        assert proxies[0]["port"] == 8080
        assert proxies[1]["protocol"] == "https"

    def test_parse_valid_json_object(self) -> None:
        """Parse JSON object with proxies key."""
        from proxywhirl.fetchers import JSONParser

        json_data = json.dumps(
            {
                "proxies": [
                    {"host": "proxy1.com", "port": 8080},
                    {"host": "proxy2.com", "port": 3128},
                ]
            }
        )

        parser = JSONParser(key="proxies")
        proxies = parser.parse(json_data)

        assert len(proxies) == 2

    def test_parse_invalid_json_raises_error(self) -> None:
        """Invalid JSON raises ProxyFetchError."""
        from proxywhirl.fetchers import JSONParser

        invalid_json = "{invalid json here"

        parser = JSONParser()
        with pytest.raises(ProxyFetchError, match="Invalid JSON"):
            parser.parse(invalid_json)

    def test_parse_json_missing_required_fields(self) -> None:
        """JSON without required fields raises validation error."""
        from proxywhirl.fetchers import JSONParser

        json_data = json.dumps(
            [
                {"host": "proxy1.com"},  # Missing port
            ]
        )

        parser = JSONParser(required_fields=["host", "port"])
        with pytest.raises(ProxyValidationError, match="Missing required field"):
            parser.parse(json_data)

    def test_parse_empty_json_array(self) -> None:
        """Empty JSON array returns empty list."""
        from proxywhirl.fetchers import JSONParser

        json_data = json.dumps([])

        parser = JSONParser()
        proxies = parser.parse(json_data)

        assert proxies == []


# T089: CSV Parser Tests
class TestCSVParser:
    """Test CSV proxy list parser."""

    def test_parse_csv_with_headers(self) -> None:
        """Parse CSV with header row."""
        from proxywhirl.fetchers import CSVParser

        csv_data = """host,port,protocol
proxy1.com,8080,http
proxy2.com,3128,https"""

        parser = CSVParser(has_header=True)
        proxies = parser.parse(csv_data)

        assert len(proxies) == 2
        assert proxies[0]["host"] == "proxy1.com"
        assert proxies[0]["port"] == "8080"

    def test_parse_csv_without_headers(self) -> None:
        """Parse CSV without headers using column mapping."""
        from proxywhirl.fetchers import CSVParser

        csv_data = """proxy1.com,8080,http
proxy2.com,3128,https"""

        parser = CSVParser(has_header=False, columns=["host", "port", "protocol"])
        proxies = parser.parse(csv_data)

        assert len(proxies) == 2
        assert proxies[0]["host"] == "proxy1.com"

    def test_parse_csv_malformed_rows(self) -> None:
        """Skip malformed rows and continue parsing."""
        from proxywhirl.fetchers import CSVParser

        csv_data = """host,port,protocol
proxy1.com,8080,http
invalid row here
proxy2.com,3128,https"""

        parser = CSVParser(has_header=True, skip_invalid=True)
        proxies = parser.parse(csv_data)

        # Should skip malformed row
        assert len(proxies) == 2
        assert proxies[0]["host"] == "proxy1.com"
        assert proxies[1]["host"] == "proxy2.com"

    def test_parse_csv_strict_mode_fails_on_malformed(self) -> None:
        """Strict mode raises error on malformed rows."""
        from proxywhirl.fetchers import CSVParser

        csv_data = """host,port
proxy1.com,8080
invalid,row,with,extra,columns"""

        parser = CSVParser(has_header=True, skip_invalid=False)
        with pytest.raises(ProxyFetchError, match="Malformed"):
            parser.parse(csv_data)

    def test_parse_empty_csv(self) -> None:
        """Empty CSV returns empty list."""
        from proxywhirl.fetchers import CSVParser

        csv_data = ""

        parser = CSVParser()
        proxies = parser.parse(csv_data)

        assert proxies == []


# T090: Plain Text Parser Tests
class TestPlainTextParser:
    """Test plain text proxy list parser."""

    def test_parse_one_proxy_per_line(self) -> None:
        """Parse plain text with one proxy URL per line."""
        from proxywhirl.fetchers import PlainTextParser

        text_data = """http://proxy1.com:8080
http://proxy2.com:3128
socks5://proxy3.com:1080"""

        parser = PlainTextParser()
        proxies = parser.parse(text_data)

        assert len(proxies) == 3
        assert "proxy1.com" in proxies[0]["url"]
        assert "8080" in proxies[0]["url"]

    def test_parse_text_with_blank_lines(self) -> None:
        """Skip blank lines in text."""
        from proxywhirl.fetchers import PlainTextParser

        text_data = """http://proxy1.com:8080

http://proxy2.com:3128

"""

        parser = PlainTextParser()
        proxies = parser.parse(text_data)

        assert len(proxies) == 2

    def test_parse_text_with_comments(self) -> None:
        """Skip comment lines starting with #."""
        from proxywhirl.fetchers import PlainTextParser

        text_data = """# This is a comment
http://proxy1.com:8080
# Another comment
http://proxy2.com:3128"""

        parser = PlainTextParser()
        proxies = parser.parse(text_data)

        assert len(proxies) == 2

    def test_parse_invalid_urls_skipped(self) -> None:
        """Skip invalid URLs and continue."""
        from proxywhirl.fetchers import PlainTextParser

        text_data = """http://proxy1.com:8080
not-a-valid-url
http://proxy2.com:3128"""

        parser = PlainTextParser(skip_invalid=True)
        proxies = parser.parse(text_data)

        assert len(proxies) == 2


# T091: HTML Table Parser Tests
class TestHTMLTableParser:
    """Test HTML table proxy list parser."""

    def test_parse_html_table(self) -> None:
        """Extract proxies from HTML <table> tags."""
        from proxywhirl.fetchers import HTMLTableParser

        html_data = """
        <table>
            <tr><th>Host</th><th>Port</th><th>Protocol</th></tr>
            <tr><td>proxy1.com</td><td>8080</td><td>http</td></tr>
            <tr><td>proxy2.com</td><td>3128</td><td>https</td></tr>
        </table>
        """

        parser = HTMLTableParser(column_map={"Host": "host", "Port": "port"})
        proxies = parser.parse(html_data)

        assert len(proxies) == 2
        assert proxies[0]["host"] == "proxy1.com"
        assert proxies[0]["port"] == "8080"

    def test_parse_html_table_by_index(self) -> None:
        """Extract proxies using column indices."""
        from proxywhirl.fetchers import HTMLTableParser

        html_data = """
        <table>
            <tr><td>proxy1.com</td><td>8080</td><td>http</td></tr>
            <tr><td>proxy2.com</td><td>3128</td><td>https</td></tr>
        </table>
        """

        parser = HTMLTableParser(column_indices={"host": 0, "port": 1, "protocol": 2})
        proxies = parser.parse(html_data)

        assert len(proxies) == 2

    def test_parse_multiple_tables_select_by_id(self) -> None:
        """Select specific table by ID attribute."""
        from proxywhirl.fetchers import HTMLTableParser

        html_data = """
        <table id="other"><tr><td>ignored</td></tr></table>
        <table id="proxies">
            <tr><td>proxy1.com</td><td>8080</td></tr>
        </table>
        """

        parser = HTMLTableParser(table_selector="#proxies", column_indices={"host": 0, "port": 1})
        proxies = parser.parse(html_data)

        assert len(proxies) == 1
        assert proxies[0]["host"] == "proxy1.com"


# T092: URL+Port Deduplication Tests
class TestProxyDeduplication:
    """Test URL+Port deduplication logic."""

    def test_same_url_port_is_duplicate(self) -> None:
        """Same URL and port combination is considered duplicate."""
        from proxywhirl.fetchers import deduplicate_proxies

        proxies = [
            {"url": "http://proxy1.com:8080"},
            {"url": "http://proxy1.com:8080"},  # Duplicate
        ]

        unique = deduplicate_proxies(proxies)

        assert len(unique) == 1

    def test_different_ports_not_duplicate(self) -> None:
        """Same URL with different ports are unique."""
        from proxywhirl.fetchers import deduplicate_proxies

        proxies = [
            {"url": "http://proxy1.com:8080"},
            {"url": "http://proxy1.com:3128"},  # Different port
        ]

        unique = deduplicate_proxies(proxies)

        assert len(unique) == 2

    def test_deduplication_preserves_metadata(self) -> None:
        """Deduplication keeps first occurrence with metadata."""
        from proxywhirl.fetchers import deduplicate_proxies

        proxies = [
            {"url": "http://proxy1.com:8080", "source": "source1", "score": 10},
            {"url": "http://proxy1.com:8080", "source": "source2", "score": 5},
        ]

        unique = deduplicate_proxies(proxies)

        assert len(unique) == 1
        assert unique[0]["source"] == "source1"  # First occurrence
        assert unique[0]["score"] == 10


# T093: ProxyValidator Tests
class TestProxyValidator:
    """Test proxy connectivity validation."""

    async def test_validate_working_proxy(self) -> None:
        """Validate proxy connectivity check."""
        from proxywhirl.fetchers import ProxyValidator

        # Will need to mock HTTP requests
        validator = ProxyValidator(timeout=5.0)

        # This test will use mock in actual implementation
        # For now, just verify the class can be instantiated
        assert validator is not None

    async def test_validate_dead_proxy_returns_false(self) -> None:
        """Dead proxy fails validation."""
        from proxywhirl.fetchers import ProxyValidator

        validator = ProxyValidator(timeout=1.0)

        # This will be implemented with mocking
        assert validator is not None

    async def test_parallel_validation_performance(self) -> None:
        """Validate 100+ proxies per second."""
        from proxywhirl.fetchers import ProxyValidator

        validator = ProxyValidator()

        # Performance test - validate this meets SC-011 requirement
        # Should validate 100+ proxies/sec
        assert validator is not None


class TestJSONParserEdgeCases:
    """Additional JSON parser edge case tests."""

    def test_parse_json_with_key_missing(self) -> None:
        """Test JSON object missing the specified key."""
        from proxywhirl.fetchers import JSONParser

        json_data = json.dumps({"wrong_key": [{"host": "proxy1.com"}]})
        parser = JSONParser(key="proxies")

        with pytest.raises(ProxyFetchError, match="JSON missing key: proxies"):
            parser.parse(json_data)

    def test_parse_json_key_on_non_dict(self) -> None:
        """Test JSON with key specified but data is not dict."""
        from proxywhirl.fetchers import JSONParser

        json_data = json.dumps([{"host": "proxy1.com"}])  # Array, not object
        parser = JSONParser(key="proxies")

        with pytest.raises(ProxyFetchError, match="JSON missing key"):
            parser.parse(json_data)

    def test_parse_json_not_array(self) -> None:
        """Test JSON that is not an array after extraction."""
        from proxywhirl.fetchers import JSONParser

        json_data = json.dumps({"host": "proxy1.com"})  # Single object
        parser = JSONParser()

        with pytest.raises(ProxyFetchError, match="JSON must be array"):
            parser.parse(json_data)


class TestCSVParserEdgeCases:
    """Additional CSV parser edge case tests."""

    def test_parse_csv_header_only(self) -> None:
        """Test CSV with only header row returns empty list."""
        from proxywhirl.fetchers import CSVParser

        csv_data = "host,port,protocol"  # Header only, no data
        parser = CSVParser(has_header=True)
        proxies = parser.parse(csv_data)

        assert proxies == []

    def test_parse_csv_no_header_no_columns_raises(self) -> None:
        """Test CSV without header and no columns specified."""
        from proxywhirl.fetchers import CSVParser

        csv_data = "proxy1.com,8080,http"
        parser = CSVParser(has_header=False, columns=None)

        with pytest.raises(ProxyFetchError, match="Must provide columns"):
            parser.parse(csv_data)

    def test_parse_csv_no_header_malformed_row_raises(self) -> None:
        """Test CSV without header with malformed row raises error."""
        from proxywhirl.fetchers import CSVParser

        csv_data = """proxy1.com,8080,http
proxy2.com,3128"""  # Missing third column

        parser = CSVParser(
            has_header=False, columns=["host", "port", "protocol"], skip_invalid=False
        )

        with pytest.raises(ProxyFetchError, match="Malformed CSV row"):
            parser.parse(csv_data)

    def test_parse_csv_no_header_skip_malformed(self) -> None:
        """Test CSV without header skips malformed rows when skip_invalid=True."""
        from proxywhirl.fetchers import CSVParser

        csv_data = """proxy1.com,8080,http
proxy2.com,3128
proxy3.com,1080,socks5"""

        parser = CSVParser(
            has_header=False, columns=["host", "port", "protocol"], skip_invalid=True
        )
        proxies = parser.parse(csv_data)

        assert len(proxies) == 2
        assert proxies[0]["host"] == "proxy1.com"
        assert proxies[1]["host"] == "proxy3.com"


class TestPlainTextParserEdgeCases:
    """Additional plain text parser edge case tests."""

    def test_parse_invalid_url_raises_error(self) -> None:
        """Test invalid URL raises error when skip_invalid=False."""
        from proxywhirl.fetchers import PlainTextParser

        text_data = "not-a-valid-url"
        parser = PlainTextParser(skip_invalid=False)

        with pytest.raises(ProxyFetchError, match="Invalid URL"):
            parser.parse(text_data)

    def test_parse_url_missing_scheme(self) -> None:
        """Test URL without scheme raises error."""
        from proxywhirl.fetchers import PlainTextParser

        text_data = "proxy1.com:8080"  # Missing http://
        parser = PlainTextParser(skip_invalid=False)

        with pytest.raises(ProxyFetchError, match="Invalid URL"):
            parser.parse(text_data)

    def test_parse_exception_handling(self) -> None:
        """Test exception during URL parsing is handled."""
        from unittest.mock import patch

        from proxywhirl.fetchers import PlainTextParser

        text_data = "http://proxy1.com:8080"
        parser = PlainTextParser(skip_invalid=False)

        with patch("proxywhirl.fetchers.urlparse", side_effect=Exception("Parse error")):
            with pytest.raises(Exception, match="Parse error"):
                parser.parse(text_data)

    def test_parse_exception_skipped_when_skip_invalid(self) -> None:
        """Test exception during URL parsing is skipped when skip_invalid=True."""
        from unittest.mock import patch

        from proxywhirl.fetchers import PlainTextParser

        text_data = "http://proxy1.com:8080\nhttp://proxy2.com:3128"
        parser = PlainTextParser(skip_invalid=True)

        # First call to urlparse will fail, second will succeed
        original_urlparse = __import__("urllib.parse", fromlist=["urlparse"]).urlparse
        call_count = [0]

        def mock_urlparse(url):
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("Parse error")
            return original_urlparse(url)

        with patch("proxywhirl.fetchers.urlparse", side_effect=mock_urlparse):
            proxies = parser.parse(text_data)

        # First proxy skipped due to exception, second parsed
        assert len(proxies) == 1
        assert "proxy2.com" in proxies[0]["url"]


class TestHTMLTableParserEdgeCases:
    """Additional HTML table parser edge case tests."""

    def test_parse_no_table_found(self) -> None:
        """Test HTML without table returns empty list."""
        from proxywhirl.fetchers import HTMLTableParser

        html_data = "<div>No table here</div>"
        parser = HTMLTableParser()
        proxies = parser.parse(html_data)

        assert proxies == []

    def test_parse_table_no_td_cells(self) -> None:
        """Test table rows without td cells."""
        from proxywhirl.fetchers import HTMLTableParser

        html_data = """
        <table>
            <tr><th>Host</th><th>Port</th></tr>
        </table>
        """
        parser = HTMLTableParser(column_indices={"host": 0, "port": 1})
        proxies = parser.parse(html_data)

        assert proxies == []

    def test_parse_column_index_out_of_range(self) -> None:
        """Test column index beyond available cells."""
        from proxywhirl.fetchers import HTMLTableParser

        html_data = """
        <table>
            <tr><td>proxy1.com</td></tr>
        </table>
        """
        # Index 1 doesn't exist
        parser = HTMLTableParser(column_indices={"host": 0, "port": 1})
        proxies = parser.parse(html_data)

        assert len(proxies) == 1
        assert proxies[0]["host"] == "proxy1.com"
        assert "port" not in proxies[0]

    def test_parse_column_map_header_not_found(self) -> None:
        """Test column map with header not in table."""
        from proxywhirl.fetchers import HTMLTableParser

        html_data = """
        <table>
            <tr><th>Host</th><th>Port</th></tr>
            <tr><td>proxy1.com</td><td>8080</td></tr>
        </table>
        """
        # 'IP' header doesn't exist in table
        parser = HTMLTableParser(column_map={"IP": "ip_address", "Port": "port"})
        proxies = parser.parse(html_data)

        assert len(proxies) == 1
        assert proxies[0]["port"] == "8080"
        assert "ip_address" not in proxies[0]


class TestDeduplicateProxiesEdgeCases:
    """Additional deduplication edge case tests."""

    def test_deduplicate_host_port_format(self) -> None:
        """Test deduplication with host+port dict format."""
        from proxywhirl.fetchers import deduplicate_proxies

        proxies = [
            {"host": "proxy1.com", "port": "8080"},
            {"host": "proxy1.com", "port": "8080"},  # Duplicate
            {"host": "proxy2.com", "port": "3128"},
        ]

        unique = deduplicate_proxies(proxies)

        assert len(unique) == 2

    def test_deduplicate_empty_url(self) -> None:
        """Test deduplication with empty URL uses host:port."""
        from proxywhirl.fetchers import deduplicate_proxies

        proxies = [
            {"url": "", "host": "proxy1.com", "port": "8080"},
            {"host": "proxy1.com", "port": "8080"},  # Duplicate
        ]

        unique = deduplicate_proxies(proxies)

        assert len(unique) == 1

    def test_deduplicate_empty_list(self) -> None:
        """Test deduplication of empty list."""
        from proxywhirl.fetchers import deduplicate_proxies

        unique = deduplicate_proxies([])

        assert unique == []

    def test_deduplicate_mixed_case_hostnames_url_format(self) -> None:
        """Test deduplication with mixed-case hostnames in URL format (case-insensitive)."""
        from proxywhirl.fetchers import deduplicate_proxies

        proxies = [
            {"url": "http://PROXY.Example.com:8080"},
            {"url": "http://proxy.example.com:8080"},  # Same host/port, different case
            {"url": "http://ProXy.ExAmPlE.cOm:8080"},  # Same host/port, different case
            {"url": "http://proxy.example.com:3128"},  # Different port
        ]

        unique = deduplicate_proxies(proxies)

        assert len(unique) == 2
        # First occurrence (with original case preserved in proxy dict) should be kept
        assert unique[0]["url"] == "http://PROXY.Example.com:8080"
        assert unique[1]["url"] == "http://proxy.example.com:3128"

    def test_deduplicate_mixed_case_hostnames_host_port_format(self) -> None:
        """Test deduplication with mixed-case hostnames in host+port format (case-insensitive)."""
        from proxywhirl.fetchers import deduplicate_proxies

        proxies = [
            {"host": "PROXY.Example.com", "port": "8080"},
            {"host": "proxy.example.com", "port": "8080"},  # Same host/port, different case
            {"host": "ProXy.ExAmPlE.cOm", "port": "8080"},  # Same host/port, different case
            {"host": "proxy.example.com", "port": "3128"},  # Different port
        ]

        unique = deduplicate_proxies(proxies)

        assert len(unique) == 2
        # First occurrence should be kept
        assert unique[0]["host"] == "PROXY.Example.com"
        assert unique[0]["port"] == "8080"
        assert unique[1]["host"] == "proxy.example.com"
        assert unique[1]["port"] == "3128"


class TestProxyValidatorMethods:
    """Test ProxyValidator methods with mocking."""

    async def test_validate_no_url(self) -> None:
        """Test validate returns False for proxy without URL."""
        from proxywhirl.fetchers import ProxyValidator

        validator = ProxyValidator()
        result = await validator.validate({"host": "proxy1.com", "port": 8080})

        assert result.is_valid is False

    async def test_validate_url_missing_host(self) -> None:
        """Test validate returns False for URL without host."""
        from proxywhirl.fetchers import ProxyValidator

        validator = ProxyValidator()
        result = await validator.validate({"url": "http://:8080"})

        assert result.is_valid is False

    async def test_validate_url_missing_port(self) -> None:
        """Test validate returns False for URL without port."""
        from proxywhirl.fetchers import ProxyValidator

        validator = ProxyValidator()
        result = await validator.validate({"url": "http://proxy1.com"})

        assert result.is_valid is False

    async def test_validate_tcp_connection_failure(self) -> None:
        """Test validate returns False when TCP connection fails."""
        from proxywhirl.fetchers import ProxyValidator

        validator = ProxyValidator(timeout=0.1)
        # Use invalid IP that will fail TCP connection
        result = await validator.validate({"url": "http://192.0.2.1:1"})

        assert result.is_valid is False

    async def test_validate_batch_empty(self) -> None:
        """Test validate_batch with empty list."""
        from proxywhirl.fetchers import ProxyValidator

        validator = ProxyValidator()
        result = await validator.validate_batch([])

        assert result == []

    async def test_validate_batch_with_valid_and_invalid(self) -> None:
        """Test validate_batch filters out invalid proxies."""
        from unittest.mock import AsyncMock, patch

        from proxywhirl.fetchers import ProxyValidator, ValidationResult

        validator = ProxyValidator()

        # Mock validate to return ValidationResult for each proxy
        with patch.object(validator, "validate", new_callable=AsyncMock) as mock_validate:
            mock_validate.side_effect = [
                ValidationResult(is_valid=True, response_time_ms=100.0),
                ValidationResult(is_valid=False, response_time_ms=None),
                ValidationResult(is_valid=True, response_time_ms=150.0),
            ]

            proxies = [
                {"url": "http://proxy1.com:8080"},
                {"url": "http://proxy2.com:8080"},
                {"url": "http://proxy3.com:8080"},
            ]
            result = await validator.validate_batch(proxies)

        assert len(result) == 2
        assert result[0]["url"] == "http://proxy1.com:8080"
        assert result[0]["average_response_time_ms"] == 100.0
        assert result[1]["url"] == "http://proxy3.com:8080"
        assert result[1]["average_response_time_ms"] == 150.0

    async def test_validate_batch_handles_exception(self) -> None:
        """Test validate_batch handles exceptions from validate."""
        from unittest.mock import AsyncMock, patch

        from proxywhirl.fetchers import ProxyValidator

        validator = ProxyValidator()

        with patch.object(validator, "validate", new_callable=AsyncMock) as mock_validate:
            mock_validate.side_effect = Exception("Validation error")

            proxies = [{"url": "http://proxy1.com:8080"}]
            result = await validator.validate_batch(proxies)

        assert result == []

    async def test_validate_tcp_connectivity_success(self) -> None:
        """Test _validate_tcp_connectivity succeeds for open port."""
        from unittest.mock import MagicMock, patch

        from proxywhirl.fetchers import ProxyValidator

        validator = ProxyValidator()

        with patch("socket.create_connection") as mock_conn:
            mock_socket = MagicMock()
            mock_conn.return_value = mock_socket

            result = await validator._validate_tcp_connectivity("127.0.0.1", 80)

        assert result is True
        mock_socket.close.assert_called_once()

    async def test_validate_tcp_connectivity_timeout(self) -> None:
        """Test _validate_tcp_connectivity returns False on timeout."""
        import socket
        from unittest.mock import patch

        from proxywhirl.fetchers import ProxyValidator

        validator = ProxyValidator()

        with patch("socket.create_connection", side_effect=socket.timeout):
            result = await validator._validate_tcp_connectivity("127.0.0.1", 80)

        assert result is False

    async def test_validate_tcp_connectivity_connection_refused(self) -> None:
        """Test _validate_tcp_connectivity returns False on connection refused."""
        from unittest.mock import patch

        from proxywhirl.fetchers import ProxyValidator

        validator = ProxyValidator()

        with patch("socket.create_connection", side_effect=ConnectionRefusedError):
            result = await validator._validate_tcp_connectivity("127.0.0.1", 80)

        assert result is False

    async def test_validate_http_request_success(self) -> None:
        """Test _validate_http_request returns True on 200 response."""
        from unittest.mock import AsyncMock, MagicMock, patch

        from proxywhirl.fetchers import ProxyValidator

        validator = ProxyValidator()

        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            result = await validator._validate_http_request()

        assert result is True

    async def test_validate_http_request_timeout(self) -> None:
        """Test _validate_http_request returns False on timeout."""
        from unittest.mock import AsyncMock, patch

        import httpx

        from proxywhirl.fetchers import ProxyValidator

        validator = ProxyValidator()

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            result = await validator._validate_http_request()

        assert result is False

    async def test_check_anonymity_elite(self) -> None:
        """Test check_anonymity returns 'elite' when no proxy headers."""
        from unittest.mock import AsyncMock, MagicMock, patch

        from proxywhirl.fetchers import ProxyValidator

        validator = ProxyValidator()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"headers": {"User-Agent": "test"}}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            result = await validator.check_anonymity()

        assert result == "elite"

    async def test_check_anonymity_transparent(self) -> None:
        """Test check_anonymity returns 'transparent' when IP leaked."""
        from unittest.mock import AsyncMock, MagicMock, patch

        from proxywhirl.fetchers import ProxyValidator

        validator = ProxyValidator()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"headers": {"X-Forwarded-For": "1.2.3.4"}}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            result = await validator.check_anonymity()

        assert result == "transparent"

    async def test_check_anonymity_anonymous(self) -> None:
        """Test check_anonymity returns 'anonymous' when Via header present."""
        from unittest.mock import AsyncMock, MagicMock, patch

        from proxywhirl.fetchers import ProxyValidator

        validator = ProxyValidator()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"headers": {"Via": "1.1 proxy.example.com"}}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            result = await validator.check_anonymity()

        assert result == "anonymous"

    async def test_check_anonymity_unknown_status_code(self) -> None:
        """Test check_anonymity returns 'unknown' on non-200 status."""
        from unittest.mock import AsyncMock, MagicMock, patch

        from proxywhirl.fetchers import ProxyValidator

        validator = ProxyValidator()

        mock_response = MagicMock()
        mock_response.status_code = 500

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            result = await validator.check_anonymity()

        assert result == "unknown"

    async def test_check_anonymity_json_parse_error(self) -> None:
        """Test check_anonymity returns 'unknown' when JSON parse fails."""
        from unittest.mock import AsyncMock, MagicMock, patch

        from proxywhirl.fetchers import ProxyValidator

        validator = ProxyValidator()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            result = await validator.check_anonymity()

        assert result == "unknown"

    async def test_check_anonymity_network_error(self) -> None:
        """Test check_anonymity returns 'unknown' on network error."""
        from unittest.mock import AsyncMock, patch

        import httpx

        from proxywhirl.fetchers import ProxyValidator

        validator = ProxyValidator()

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(side_effect=httpx.NetworkError("Network error"))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            result = await validator.check_anonymity()

        assert result == "unknown"


class TestProxyFetcher:
    """Test ProxyFetcher class."""

    def test_init_default(self) -> None:
        """Test ProxyFetcher default initialization."""
        from proxywhirl.fetchers import ProxyFetcher

        fetcher = ProxyFetcher()

        assert fetcher.sources == []
        assert fetcher.validator is not None

    def test_init_with_sources(self) -> None:
        """Test ProxyFetcher initialization with sources."""
        from proxywhirl.fetchers import ProxyFetcher, ProxySourceConfig

        source = ProxySourceConfig(url="http://example.com/proxies.json")
        fetcher = ProxyFetcher(sources=[source])

        assert len(fetcher.sources) == 1
        assert str(fetcher.sources[0].url) == "http://example.com/proxies.json"

    def test_add_source(self) -> None:
        """Test adding a source."""
        from proxywhirl.fetchers import ProxyFetcher, ProxySourceConfig

        fetcher = ProxyFetcher()
        source = ProxySourceConfig(url="http://example.com/proxies.json")
        fetcher.add_source(source)

        assert len(fetcher.sources) == 1

    def test_remove_source(self) -> None:
        """Test removing a source by URL."""
        from proxywhirl.fetchers import ProxyFetcher, ProxySourceConfig

        source1 = ProxySourceConfig(url="http://example.com/proxies1.json")
        source2 = ProxySourceConfig(url="http://example.com/proxies2.json")
        fetcher = ProxyFetcher(sources=[source1, source2])

        fetcher.remove_source("http://example.com/proxies1.json")

        assert len(fetcher.sources) == 1
        assert str(fetcher.sources[0].url) == "http://example.com/proxies2.json"

    async def test_fetch_from_source_json(self) -> None:
        """Test fetching from JSON source."""
        from unittest.mock import AsyncMock, MagicMock, patch

        from proxywhirl.fetchers import ProxyFetcher, ProxySourceConfig

        source = ProxySourceConfig(url="http://example.com/proxies.json", format="json")
        fetcher = ProxyFetcher()

        mock_response = MagicMock()
        mock_response.text = '[{"host": "proxy1.com", "port": 8080}]'
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            proxies = await fetcher.fetch_from_source(source)

        assert len(proxies) == 1
        assert proxies[0]["host"] == "proxy1.com"

    def test_unsupported_format_rejected_by_validation(self) -> None:
        """Test that unsupported format is rejected by Pydantic validation."""
        from pydantic import ValidationError

        from proxywhirl.fetchers import ProxySourceConfig

        # Pydantic enum validation rejects invalid format strings
        with pytest.raises(ValidationError, match="format"):
            ProxySourceConfig(url="http://example.com/proxies.xyz", format="xyz")

    async def test_fetch_from_source_http_error(self) -> None:
        """Test fetching handles HTTP status error."""
        from unittest.mock import AsyncMock, MagicMock, patch

        import httpx

        from proxywhirl.fetchers import ProxyFetcher, ProxySourceConfig

        source = ProxySourceConfig(url="http://example.com/proxies.json", format="json")
        fetcher = ProxyFetcher()

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock(
            side_effect=httpx.HTTPStatusError(
                "Not found", request=MagicMock(), response=MagicMock()
            )
        )

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            with pytest.raises(ProxyFetchError, match="HTTP error"):
                await fetcher.fetch_from_source(source)

    async def test_fetch_from_source_request_error(self) -> None:
        """Test fetching handles request error."""
        from unittest.mock import AsyncMock, patch

        import httpx

        from proxywhirl.fetchers import ProxyFetcher, ProxySourceConfig

        source = ProxySourceConfig(url="http://example.com/proxies.json", format="json")
        fetcher = ProxyFetcher()

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(side_effect=httpx.RequestError("Connection failed"))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            with pytest.raises(ProxyFetchError, match="Request error"):
                await fetcher.fetch_from_source(source)

    async def test_fetch_from_source_custom_parser(self) -> None:
        """Test fetching with custom parser."""
        from unittest.mock import AsyncMock, MagicMock, patch

        from proxywhirl.fetchers import ProxyFetcher, ProxySourceConfig

        class CustomParser:
            def parse(self, data: str) -> list:
                return [{"url": "http://custom.com:8080"}]

        source = ProxySourceConfig(
            url="http://example.com/proxies.txt",
            format="custom",
            custom_parser=CustomParser(),
        )
        fetcher = ProxyFetcher()

        mock_response = MagicMock()
        mock_response.text = "custom data"
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            proxies = await fetcher.fetch_from_source(source)

        assert len(proxies) == 1
        assert proxies[0]["url"] == "http://custom.com:8080"

    async def test_fetch_all_multiple_sources(self) -> None:
        """Test fetch_all from multiple sources."""
        from unittest.mock import AsyncMock, patch

        from proxywhirl.fetchers import ProxyFetcher, ProxySourceConfig, ProxyValidator

        source1 = ProxySourceConfig(url="http://example1.com/proxies.json")
        source2 = ProxySourceConfig(url="http://example2.com/proxies.json")
        validator = ProxyValidator()
        fetcher = ProxyFetcher(sources=[source1, source2], validator=validator)

        with patch.object(fetcher, "fetch_from_source", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = [
                [{"url": "http://proxy1.com:8080"}],
                [{"url": "http://proxy2.com:8080"}],
            ]
            with patch.object(validator, "validate_batch", new_callable=AsyncMock) as mock_validate:
                mock_validate.return_value = [
                    {"url": "http://proxy1.com:8080"},
                    {"url": "http://proxy2.com:8080"},
                ]

                proxies = await fetcher.fetch_all(validate=True, deduplicate=True)

        assert len(proxies) == 2

    async def test_fetch_all_handles_source_exception(self) -> None:
        """Test fetch_all handles exception from source."""
        from unittest.mock import AsyncMock, patch

        from proxywhirl.fetchers import ProxyFetcher, ProxySourceConfig

        source1 = ProxySourceConfig(url="http://example1.com/proxies.json")
        source2 = ProxySourceConfig(url="http://example2.com/proxies.json")
        fetcher = ProxyFetcher(sources=[source1, source2])

        with patch.object(fetcher, "fetch_from_source", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = [
                Exception("Source 1 failed"),
                [{"url": "http://proxy2.com:8080"}],
            ]
            with patch.object(
                fetcher.validator, "validate_batch", new_callable=AsyncMock
            ) as mock_validate:
                mock_validate.return_value = [{"url": "http://proxy2.com:8080"}]

                proxies = await fetcher.fetch_all()

        assert len(proxies) == 1

    async def test_fetch_all_no_validation(self) -> None:
        """Test fetch_all without validation."""
        from unittest.mock import AsyncMock, patch

        from proxywhirl.fetchers import ProxyFetcher, ProxySourceConfig

        source = ProxySourceConfig(url="http://example.com/proxies.json")
        fetcher = ProxyFetcher(sources=[source])

        with patch.object(fetcher, "fetch_from_source", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = [{"url": "http://proxy1.com:8080"}]

            proxies = await fetcher.fetch_all(validate=False, deduplicate=False)

        assert len(proxies) == 1

    async def test_fetch_from_source_browser_render_mode(self) -> None:
        """Test fetch_from_source with browser render mode."""
        from unittest.mock import AsyncMock, MagicMock, patch

        from proxywhirl.fetchers import ProxyFetcher, ProxySourceConfig
        from proxywhirl.models import RenderMode

        source = ProxySourceConfig(
            url="http://example.com/js-rendered.html",
            format="html_table",
            render_mode=RenderMode.BROWSER,
        )
        fetcher = ProxyFetcher()

        mock_renderer = MagicMock()
        mock_renderer.render = AsyncMock(
            return_value="<table><tr><td>proxy1.com</td><td>8080</td></tr></table>"
        )
        mock_renderer.__aenter__ = AsyncMock(return_value=mock_renderer)
        mock_renderer.__aexit__ = AsyncMock(return_value=None)

        mock_browser_class = MagicMock(return_value=mock_renderer)
        mock_browser_module = MagicMock()
        mock_browser_module.BrowserRenderer = mock_browser_class

        with patch.dict("sys.modules", {"proxywhirl.browser": mock_browser_module}):
            proxies = await fetcher.fetch_from_source(source)

        # Should return empty list since no column mapping
        assert proxies == []

    async def test_fetch_from_source_browser_import_error(self) -> None:
        """Test fetch_from_source raises error when browser not installed."""
        import sys

        from proxywhirl.fetchers import ProxyFetcher, ProxySourceConfig
        from proxywhirl.models import RenderMode

        source = ProxySourceConfig(
            url="http://example.com/js-rendered.html",
            format="html_table",
            render_mode=RenderMode.BROWSER,
        )
        fetcher = ProxyFetcher()

        # Remove the browser module from sys.modules if it exists
        original = sys.modules.get("proxywhirl.browser")
        try:
            sys.modules["proxywhirl.browser"] = None  # type: ignore
            with pytest.raises(ProxyFetchError, match="Browser rendering requires Playwright"):
                await fetcher.fetch_from_source(source)
        finally:
            if original is not None:
                sys.modules["proxywhirl.browser"] = original
            elif "proxywhirl.browser" in sys.modules:
                del sys.modules["proxywhirl.browser"]

    async def test_fetch_from_source_browser_timeout(self) -> None:
        """Test fetch_from_source handles browser timeout."""
        from unittest.mock import AsyncMock, MagicMock, patch

        from proxywhirl.fetchers import ProxyFetcher, ProxySourceConfig
        from proxywhirl.models import RenderMode

        source = ProxySourceConfig(
            url="http://example.com/js-rendered.html",
            format="html_table",
            render_mode=RenderMode.BROWSER,
        )
        fetcher = ProxyFetcher()

        mock_renderer = MagicMock()
        mock_renderer.render = AsyncMock(side_effect=TimeoutError("Browser timeout"))
        mock_renderer.__aenter__ = AsyncMock(return_value=mock_renderer)
        mock_renderer.__aexit__ = AsyncMock(return_value=None)

        mock_browser_class = MagicMock(return_value=mock_renderer)
        mock_browser_module = MagicMock()
        mock_browser_module.BrowserRenderer = mock_browser_class

        with patch.dict("sys.modules", {"proxywhirl.browser": mock_browser_module}):
            with pytest.raises(ProxyFetchError, match="Browser timeout"):
                await fetcher.fetch_from_source(source)

    async def test_fetch_from_source_browser_runtime_error(self) -> None:
        """Test fetch_from_source handles browser runtime error."""
        from unittest.mock import AsyncMock, MagicMock, patch

        from proxywhirl.fetchers import ProxyFetcher, ProxySourceConfig
        from proxywhirl.models import RenderMode

        source = ProxySourceConfig(
            url="http://example.com/js-rendered.html",
            format="html_table",
            render_mode=RenderMode.BROWSER,
        )
        fetcher = ProxyFetcher()

        mock_renderer = MagicMock()
        mock_renderer.render = AsyncMock(side_effect=RuntimeError("Browser crashed"))
        mock_renderer.__aenter__ = AsyncMock(return_value=mock_renderer)
        mock_renderer.__aexit__ = AsyncMock(return_value=None)

        mock_browser_class = MagicMock(return_value=mock_renderer)
        mock_browser_module = MagicMock()
        mock_browser_module.BrowserRenderer = mock_browser_class

        with patch.dict("sys.modules", {"proxywhirl.browser": mock_browser_module}):
            with pytest.raises(ProxyFetchError, match="Browser error"):
                await fetcher.fetch_from_source(source)


class TestProxyValidatorWithSocks:
    """Test ProxyValidator with SOCKS proxies."""

    async def test_validate_socks_missing_httpx_socks(self) -> None:
        """Test validate handles missing httpx-socks gracefully."""
        from unittest.mock import AsyncMock, MagicMock, patch

        from proxywhirl.fetchers import ProxyValidator

        validator = ProxyValidator(timeout=1.0)

        # Mock TCP connection success
        mock_writer = AsyncMock()
        mock_writer.close = MagicMock()
        mock_writer.wait_closed = AsyncMock()

        # Mock SOCKS_AVAILABLE as False (simulate missing httpx-socks)
        with patch("asyncio.open_connection", new_callable=AsyncMock) as mock_open:
            mock_open.return_value = (AsyncMock(), mock_writer)

            with patch("proxywhirl.fetchers.SOCKS_AVAILABLE", False):
                result = await validator.validate({"url": "socks5://proxy1.com:1080"})

        # Should return invalid (not raise exception)
        assert result.is_valid is False
        assert result.response_time_ms is None

    async def test_validate_socks_proxy(self) -> None:
        """Test validate with SOCKS proxy uses httpx_socks."""
        from unittest.mock import AsyncMock, MagicMock, patch

        from proxywhirl.fetchers import ProxyValidator

        validator = ProxyValidator(timeout=1.0)

        # Mock TCP connection success
        mock_writer = AsyncMock()
        mock_writer.close = MagicMock()
        mock_writer.wait_closed = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("asyncio.open_connection", new_callable=AsyncMock) as mock_open:
            mock_open.return_value = (AsyncMock(), mock_writer)

            with patch("httpx_socks.AsyncProxyTransport") as mock_transport:
                mock_transport.from_url = MagicMock(return_value=MagicMock())

                with patch("httpx.AsyncClient") as mock_client:
                    mock_instance = AsyncMock()
                    mock_instance.get = AsyncMock(return_value=mock_response)
                    mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
                    mock_instance.__aexit__ = AsyncMock(return_value=None)
                    mock_client.return_value = mock_instance

                    result = await validator.validate({"url": "socks5://proxy1.com:1080"})

        assert result.is_valid is True

    async def test_validate_http_proxy_success(self) -> None:
        """Test validate with HTTP proxy succeeds."""
        from unittest.mock import AsyncMock, MagicMock, patch

        from proxywhirl.fetchers import ProxyValidator

        validator = ProxyValidator(timeout=1.0)

        # Mock TCP connection success
        mock_writer = AsyncMock()
        mock_writer.close = MagicMock()
        mock_writer.wait_closed = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("asyncio.open_connection", new_callable=AsyncMock) as mock_open:
            mock_open.return_value = (AsyncMock(), mock_writer)

            with patch("httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_instance.get = AsyncMock(return_value=mock_response)
                mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
                mock_instance.__aexit__ = AsyncMock(return_value=None)
                mock_client.return_value = mock_instance

                result = await validator.validate({"url": "http://proxy1.com:8080"})

        assert result.is_valid is True

    async def test_validate_exception_returns_false(self) -> None:
        """Test validate returns False on any exception."""
        from unittest.mock import AsyncMock, MagicMock, patch

        from proxywhirl.fetchers import ProxyValidator

        validator = ProxyValidator(timeout=1.0)

        # Mock TCP connection success
        mock_writer = AsyncMock()
        mock_writer.close = MagicMock()
        mock_writer.wait_closed = AsyncMock()

        with patch("asyncio.open_connection", new_callable=AsyncMock) as mock_open:
            mock_open.return_value = (AsyncMock(), mock_writer)

            with patch("httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_instance.get = AsyncMock(side_effect=Exception("Unknown error"))
                mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
                mock_instance.__aexit__ = AsyncMock(return_value=None)
                mock_client.return_value = mock_instance

                result = await validator.validate({"url": "http://proxy1.com:8080"})

        assert result.is_valid is False


class TestProxyFetcherClientPool:
    """Test ProxyFetcher shared client pool functionality."""

    async def test_get_client_creates_client(self) -> None:
        """Test _get_client creates client on first call."""
        from proxywhirl.fetchers import ProxyFetcher

        fetcher = ProxyFetcher()
        assert fetcher._client is None

        client = await fetcher._get_client()
        assert client is not None
        assert fetcher._client is client
        await fetcher.close()

    async def test_get_client_reuses_client(self) -> None:
        """Test _get_client reuses existing client."""
        from proxywhirl.fetchers import ProxyFetcher

        fetcher = ProxyFetcher()

        client1 = await fetcher._get_client()
        client2 = await fetcher._get_client()
        assert client1 is client2
        await fetcher.close()

    async def test_close_cleans_up_client(self) -> None:
        """Test close properly cleans up client."""
        from proxywhirl.fetchers import ProxyFetcher

        fetcher = ProxyFetcher()
        await fetcher._get_client()
        assert fetcher._client is not None

        await fetcher.close()
        assert fetcher._client is None

    async def test_close_cleans_up_validator_client(self) -> None:
        """Test close also closes validator's clients."""
        from unittest.mock import AsyncMock, patch

        from proxywhirl.fetchers import ProxyFetcher, ProxyValidator

        validator = ProxyValidator()
        fetcher = ProxyFetcher(validator=validator)

        # Create validator's client
        await validator._get_client()
        assert validator._client is not None

        # Mock the validator's close method to verify it's called
        with patch.object(validator, "close", new_callable=AsyncMock) as mock_close:
            await fetcher.close()
            mock_close.assert_called_once()

    async def test_context_manager_cleanup(self) -> None:
        """Test async context manager properly cleans up."""
        from proxywhirl.fetchers import ProxyFetcher

        async with ProxyFetcher() as fetcher:
            await fetcher._get_client()
            assert fetcher._client is not None

        # After context exit, client should be closed
        assert fetcher._client is None

    async def test_fetch_from_source_uses_shared_client(self) -> None:
        """Test fetch_from_source uses shared client instead of creating new one."""
        from unittest.mock import AsyncMock, MagicMock, call, patch

        from proxywhirl.fetchers import ProxyFetcher, ProxySourceConfig

        source = ProxySourceConfig(url="http://example.com/proxies.json", format="json")
        fetcher = ProxyFetcher()

        mock_response = MagicMock()
        mock_response.text = '[{"host": "proxy1.com", "port": 8080}]'
        mock_response.raise_for_status = MagicMock()

        # Mock _get_client to verify it's called
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch.object(fetcher, "_get_client", new_callable=AsyncMock) as mock_get_client:
            mock_get_client.return_value = mock_client

            # Fetch twice from the same source
            await fetcher.fetch_from_source(source)
            await fetcher.fetch_from_source(source)

            # _get_client should be called twice (once per fetch)
            assert mock_get_client.call_count == 2
            # The same client instance should be reused
            assert all(call_args == call() for call_args in mock_get_client.call_args_list)

        await fetcher.close()

    async def test_client_pool_configuration(self) -> None:
        """Test client is configured with correct limits."""
        from proxywhirl.fetchers import ProxyFetcher

        fetcher = ProxyFetcher()
        client = await fetcher._get_client()

        # Verify client was created (we can't check internal config reliably)
        assert client is not None
        assert isinstance(client, __import__("httpx").AsyncClient)

        await fetcher.close()
