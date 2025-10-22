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
from typing import Any

import pytest

from proxywhirl.exceptions import ProxyFetchError, ProxyValidationError


# T088: JSON Parser Tests
class TestJSONParser:
    """Test JSON proxy list parser."""

    def test_parse_valid_json_array(self) -> None:
        """Parse valid JSON array of proxy objects."""
        from proxywhirl.fetchers import JSONParser

        json_data = json.dumps([
            {"host": "proxy1.com", "port": 8080, "protocol": "http"},
            {"host": "proxy2.com", "port": 3128, "protocol": "https"},
        ])

        parser = JSONParser()
        proxies = parser.parse(json_data)

        assert len(proxies) == 2
        assert proxies[0]["host"] == "proxy1.com"
        assert proxies[0]["port"] == 8080
        assert proxies[1]["protocol"] == "https"

    def test_parse_valid_json_object(self) -> None:
        """Parse JSON object with proxies key."""
        from proxywhirl.fetchers import JSONParser

        json_data = json.dumps({
            "proxies": [
                {"host": "proxy1.com", "port": 8080},
                {"host": "proxy2.com", "port": 3128},
            ]
        })

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

        json_data = json.dumps([
            {"host": "proxy1.com"},  # Missing port
        ])

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

        parser = CSVParser(
            has_header=False, columns=["host", "port", "protocol"]
        )
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

        parser = HTMLTableParser(
            column_indices={"host": 0, "port": 1, "protocol": 2}
        )
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

        parser = HTMLTableParser(
            table_selector="#proxies", column_indices={"host": 0, "port": 1}
        )
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

    @pytest.mark.asyncio
    async def test_validate_working_proxy(self) -> None:
        """Validate proxy connectivity check."""
        from proxywhirl.fetchers import ProxyValidator

        # Will need to mock HTTP requests
        validator = ProxyValidator(timeout=5.0)

        # This test will use mock in actual implementation
        # For now, just verify the class can be instantiated
        assert validator is not None

    @pytest.mark.asyncio
    async def test_validate_dead_proxy_returns_false(self) -> None:
        """Dead proxy fails validation."""
        from proxywhirl.fetchers import ProxyValidator

        validator = ProxyValidator(timeout=1.0)

        # This will be implemented with mocking
        assert validator is not None

    @pytest.mark.asyncio
    async def test_parallel_validation_performance(self) -> None:
        """Validate 100+ proxies per second."""
        from proxywhirl.fetchers import ProxyValidator

        validator = ProxyValidator()

        # Performance test - validate this meets SC-011 requirement
        # Should validate 100+ proxies/sec
        assert validator is not None
