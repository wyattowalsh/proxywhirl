"""Pytest fixtures for ProxyWhirl tests."""

# mypy: ignore-errors
# pyright: reportMissingImports=false
import asyncio
import json
from datetime import datetime, timedelta, timezone
from ipaddress import ip_address
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import httpx
import pytest

from proxywhirl.models import AnonymityLevel, Proxy, Scheme

# ============================================================================
# MOCKING FIXTURES
# ============================================================================


@pytest.fixture
def mock_httpx_client() -> Generator[MagicMock, None, None]:
    """Fixture to mock httpx.AsyncClient, handling async context manager."""
    with patch("proxywhirl.utils.httpx.AsyncClient", new_callable=MagicMock) as mock_client:
        instance = mock_client.return_value
        instance.__aenter__.return_value = instance
        instance.__aexit__.return_value = None

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.raise_for_status.return_value = None
        mock_response.text = "Mocked text"
        mock_response.json.return_value = {"mocked": "json"}

        instance.get = AsyncMock(return_value=mock_response)

        yield mock_client


# ============================================================================
# BASIC PROXY FIXTURES
# ============================================================================


@pytest.fixture
def sample_proxies() -> List[Proxy]:
    """Basic sample proxies for simple testing."""
    now = datetime.now(timezone.utc)
    return [
        Proxy(
            host="1.1.1.1",
            ip=ip_address("1.1.1.1"),
            port=8080,
            schemes=[Scheme.HTTP, Scheme.HTTPS],
            country_code="US",
            country=None,
            city=None,
            anonymity=AnonymityLevel.ELITE,
            last_checked=now,
            response_time=0.2,
            source="test",
        ),
        Proxy(
            host="2.2.2.2",
            ip=ip_address("2.2.2.2"),
            port=3128,
            schemes=[Scheme.HTTP],
            country_code="GB",
            country=None,
            city=None,
            anonymity=AnonymityLevel.ANONYMOUS,
            last_checked=now,
            response_time=0.5,
            source="test",
        ),
        Proxy(
            host="3.3.3.3",
            ip=ip_address("3.3.3.3"),
            port=1080,
            schemes=[Scheme.SOCKS5],
            country_code="DE",
            country=None,
            city=None,
            anonymity=AnonymityLevel.TRANSPARENT,
            last_checked=now,
            response_time=None,
            source="test",
        ),
    ]


@pytest.fixture
def comprehensive_proxy_list() -> List[Proxy]:
    """Comprehensive list of proxies covering all scenarios."""
    now = datetime.now(timezone.utc)
    proxies = []

    # Create diverse proxy scenarios
    protocols = [
        (Scheme.HTTP, 8080),
        (Scheme.HTTPS, 8443),
        (Scheme.SOCKS4, 1080),
        (Scheme.SOCKS5, 1080),
    ]

    countries = ["US", "GB", "DE", "FR", "JP", "AU", "CA", "RU", "CN", "BR"]
    anonymity_levels = [AnonymityLevel.ELITE, AnonymityLevel.ANONYMOUS, AnonymityLevel.TRANSPARENT]

    for i in range(50):  # Generate 50 diverse proxies
        scheme, default_port = protocols[i % len(protocols)]
        country = countries[i % len(countries)]
        anonymity = anonymity_levels[i % len(anonymity_levels)]

        # Vary response times for realistic testing
        response_time = None if i % 7 == 0 else (0.1 + (i % 20) * 0.05)

        proxy = Proxy(
            host=f"proxy-{i:03d}.example.com",
            ip=ip_address(f"192.0.{(i // 256) + 2}.{i % 256 + 1}"),
            port=default_port + (i % 100),
            schemes=[scheme],
            country_code=country,
            country=f"Country-{country}",
            city=f"City-{i % 10}",
            anonymity=anonymity,
            last_checked=now - timedelta(minutes=i % 60),
            response_time=response_time,
            source=f"source-{i % 5}",
        )
        proxies.append(proxy)

    return proxies


@pytest.fixture
def large_proxy_dataset() -> List[Proxy]:
    """Large proxy dataset for performance testing."""
    now = datetime.now(timezone.utc)
    proxies = []

    for i in range(1000):  # 1000 proxies for performance testing
        proxy = Proxy(
            host=f"perf-proxy-{i:04d}.example.com",
            ip=ip_address(f"10.{i // 65536}.{(i // 256) % 256}.{i % 256}"),
            port=8000 + (i % 10000),
            schemes=[Scheme.HTTP],
            country_code="US",
            anonymity=AnonymityLevel.ELITE,
            last_checked=now,
            response_time=0.1 + (i % 100) * 0.01,
            source="performance-test",
        )
        proxies.append(proxy)

    return proxies


# ============================================================================
# HTTP CLIENT MOCKS
# ============================================================================

# Removed duplicate mock_httpx_client fixture (uses httpx.Client) to avoid redefinition.


@pytest.fixture
def http_error_scenarios():
    """Factory for creating various HTTP error scenarios."""

    def _create_error_response(status_code: int, error_message: str = "HTTP Error"):
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = status_code
        mock_response.text = f"Error {status_code}: {error_message}"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            error_message, request=Mock(), response=mock_response
        )
        return mock_response

    return {
        "not_found": _create_error_response(404, "Not Found"),
        "server_error": _create_error_response(500, "Internal Server Error"),
        "timeout": _create_error_response(408, "Request Timeout"),
        "forbidden": _create_error_response(403, "Forbidden"),
        "rate_limited": _create_error_response(429, "Too Many Requests"),
    }


@pytest.fixture
def network_error_scenarios() -> Dict[str, Exception]:
    """Factory for creating network-level error scenarios."""
    return {
        "connection_timeout": httpx.ConnectTimeout("Connection timed out"),
        "read_timeout": httpx.ReadTimeout("Read timed out"),
        "connection_refused": httpx.ConnectError("Connection refused"),
        "dns_error": httpx.ConnectError("DNS resolution failed"),
        "ssl_error": httpx.ConnectError("SSL certificate verification failed"),
    }


# ============================================================================
# RESPONSE CONTENT FIXTURES
# ============================================================================


@pytest.fixture
def sample_proxy_html():
    """Sample HTML content for proxy list testing."""
    return """
    <html>
    <head><title>Proxy List</title></head>
    <body>
    <div class="proxy-list">
        <table>
            <tr><th>IP:Port</th><th>Country</th><th>Type</th></tr>
            <tr><td>192.168.1.1:8080</td><td>US</td><td>HTTP</td></tr>
            <tr><td>10.0.0.1:3128</td><td>GB</td><td>HTTP</td></tr>
            <tr><td>172.16.0.1:1080</td><td>DE</td><td>SOCKS5</td></tr>
        </table>
    </div>
    <script>/* some javascript */</script>
    </body>
    </html>
    """


@pytest.fixture
def sample_proxy_json():
    """Sample JSON content for API testing."""
    return {
        "proxies": [
            {
                "ip": "192.168.1.1",
                "port": 8080,
                "protocol": "http",
                "country": "US",
                "anonymity": "elite",
            },
            {
                "ip": "10.0.0.1",
                "port": 3128,
                "protocol": "http",
                "country": "GB",
                "anonymity": "anonymous",
            },
            {
                "ip": "172.16.0.1",
                "port": 1080,
                "protocol": "socks5",
                "country": "DE",
                "anonymity": "transparent",
            },
        ],
        "total": 3,
        "page": 1,
        "has_next": False,
    }


# sample_proxy_text defined later in legacy compatibility; avoid duplicate.


@pytest.fixture
def malformed_proxy_content():
    """Various malformed content scenarios for error testing."""
    return {
        "mixed_valid_invalid": """
192.168.1.1:8080
invalid-proxy-line
10.0.0.1:not-a-port
172.16.0.1:3128
just-text
:8080
192.168.1.1:
        """,
        "empty_lines": """

192.168.1.1:8080


10.0.0.1:3128

        """,
        "special_chars": """
192.168.1.1:8080;DROP TABLE proxies;--
10.0.0.1:3128<script>alert('xss')</script>
172.16.0.1:1080|rm -rf /
        """,
        "unicode_content": """
192.168.1.1:8080
10.0.0.1:3128 🚀
172.16.0.1:1080 测试
        """,
        "very_long_lines": f"192.168.1.1:8080{'a' * 10000}\n10.0.0.1:3128\n",
        "completely_invalid": "This is not proxy data at all!!! 🎉",
        "json_but_wrong_format": '{"not": "proxy", "data": "here"}',
        "html_but_no_proxies": ("<html><body><h1>No proxies here!</h1></body></html>"),
    }


# ============================================================================
# CACHE TESTING FIXTURES
# ============================================================================


@pytest.fixture
def temp_cache_paths(tmp_path: Path) -> Dict[str, Path]:
    """Temporary cache file paths for testing."""
    return {
        "json": tmp_path / "test_cache.json",
        "sqlite": tmp_path / "test_cache.sqlite",
        "backup": tmp_path / "backup_cache.json",
    }


@pytest.fixture
def mock_sqlite_connection():
    """Mock SQLite connection for testing database operations."""
    with patch("sqlite3.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_conn.cursor.return_value = mock_cursor
        mock_conn.execute.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        mock_cursor.fetchone.return_value = None

        mock_connect.return_value = mock_conn
        yield mock_conn


@pytest.fixture
def cache_performance_data():
    """Large dataset for cache performance testing."""
    proxies = []
    for i in range(10000):
        proxies.append(
            {
                "host": f"cache-test-{i:05d}.example.com",
                "ip": f"192.168.{i // 256}.{i % 256}",
                "port": 8000 + (i % 1000),
                "scheme": "http",
                "country_code": "US",
                "anonymity": "elite",
                "last_checked": datetime.now(timezone.utc).isoformat(),
                "response_time": 0.1 + (i % 100) * 0.01,
                "source": "performance-test",
            }
        )
    return proxies


# ============================================================================
# LOADER TESTING FIXTURES
# ============================================================================


@pytest.fixture
def loader_response_factory():
    """Factory for creating various loader response scenarios."""

    def _create_response(
        content: str = "",
        content_type: str = "text/plain",
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        should_raise: bool = False,
        exception_type: Optional[type] = None,
    ) -> Mock:
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = status_code
        mock_response.text = content
        mock_response.content = content.encode("utf-8")
        mock_response.headers = headers or {"content-type": content_type}

        # Handle JSON responses
        if content_type == "application/json":
            try:
                mock_response.json.return_value = json.loads(content)
            except json.JSONDecodeError:
                mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", content, 0)
        else:
            mock_response.json.side_effect = json.JSONDecodeError("Not JSON", content, 0)

        # Handle errors
        if should_raise:
            if exception_type:
                mock_response.raise_for_status.side_effect = exception_type("HTTP Error")
            else:
                mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                    "HTTP Error", request=Mock(), response=mock_response
                )
        else:
            mock_response.raise_for_status.return_value = None

        return mock_response

    return _create_response


@pytest.fixture
def multi_protocol_responses():
    """Responses for testing multi-protocol loaders."""
    return {
        "http": "192.168.1.1:8080\n10.0.0.1:3128\n172.16.0.1:8000\n",
        "socks4": "203.0.113.1:1080\n198.51.100.1:1080\n",
        "socks5": "192.0.2.1:1080\n192.0.2.2:1080\n192.0.2.3:1080\n",
    }


# ============================================================================
# PERFORMANCE TESTING FIXTURES
# ============================================================================


@pytest.fixture
def performance_test_config():
    """Configuration for performance testing scenarios."""
    return {
        "small_dataset": 100,
        "medium_dataset": 1000,
        "large_dataset": 10000,
        "timeout_short": 1.0,
        "timeout_medium": 5.0,
        "timeout_long": 30.0,
        "concurrent_requests": 10,
        "retry_attempts": 3,
    }


@pytest.fixture
def memory_usage_monitor():
    """Monitor for tracking memory usage during tests."""
    import os

    import psutil

    class MemoryMonitor:
        def __init__(self):
            self.process = psutil.Process(os.getpid())
            self.initial_memory = self.process.memory_info().rss

        def get_current_usage(self) -> int:
            return self.process.memory_info().rss

        def get_memory_increase(self) -> int:
            return self.get_current_usage() - self.initial_memory

    return MemoryMonitor()


# ============================================================================
# E2E TESTING FIXTURES
# ============================================================================


@pytest.fixture
def e2e_test_environment(tmp_path: Path):
    """Complete environment setup for E2E testing."""
    env = {
        "cache_dir": tmp_path / "cache",
        "config_dir": tmp_path / "config",
        "log_dir": tmp_path / "logs",
        "temp_dir": tmp_path / "temp",
    }

    # Create directories
    for directory in env.values():
        directory.mkdir(exist_ok=True)

    # Create sample config files
    config_data = {
        "cache": {
            "type": "json",
            "path": str(env["cache_dir"] / "proxies.json"),
        },
        "rotation": {"strategy": "round_robin"},
        "validation": {"timeout": 5.0, "max_retries": 3},
    }

    config_file = env["config_dir"] / "proxywhirl.json"
    config_file.write_text(json.dumps(config_data, indent=2))

    env["config_file"] = config_file
    return env


@pytest.fixture
def cli_test_scenarios():
    """Various CLI command scenarios for E2E testing."""
    return {
        "basic_fetch": ["fetch", "--loader", "proxyscrape", "--limit", "10"],
        "cache_operations": [
            ["cache", "clear"],
            ["fetch", "--loader", "proxyscrape", "--cache-type", "json"],
            ["list", "--cache-type", "json"],
        ],
        "validation_flow": [
            ["fetch", "--loader", "proxyscrape"],
            ["validate", "--timeout", "5"],
            ["list", "--valid-only"],
        ],
        "rotation_strategies": [
            ["get", "--strategy", "round_robin"],
            ["get", "--strategy", "random"],
            ["get", "--strategy", "weighted"],
        ],
        "error_scenarios": [
            ["fetch", "--loader", "nonexistent"],
            ["cache", "invalid-command"],
            ["get", "--strategy", "invalid"],
        ],
    }


# ============================================================================
# UTILITY FIXTURES
# ============================================================================


@pytest.fixture
def event_loop():
    """Ensure a loop exists for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_logger():
    """Mock logger for testing logging functionality."""
    with patch("proxywhirl.logger.logger") as mock_log:
        yield mock_log


@pytest.fixture
def time_freeze():
    """Freeze time for consistent testing."""
    frozen_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    with patch("proxywhirl.models.datetime") as mock_datetime:
        mock_datetime.now.return_value = frozen_time
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
        yield frozen_time


# ============================================================================
# LEGACY COMPATIBILITY (keep existing fixtures)
# ============================================================================


class FakeLoader:
    name = "fake-loader"

    def __init__(self, rows: List[Dict[str, Any]]):
        self._rows = rows

    def load(self):  # returns a pandas-like object with iterrows
        class DF:
            def __init__(self, rows):
                self._rows = rows

            def iterrows(self):
                for idx, row in enumerate(self._rows):
                    yield idx, type("R", (), {"to_dict": lambda self: row})()

        return DF(self._rows)


@pytest.fixture
def fake_loader_rows() -> List[Dict[str, Any]]:
    return [
        {
            "host": "10.0.0.1",
            "port": 8000,
            "protocol": "http",
            "country_code": "US",
            "anonymity": "elite",
        },
        {
            "host": "10.0.0.2",
            "port": 8080,
            "protocol": "https",
            "country_code": "FR",
            "anonymity": "anonymous",
        },
    ]


@pytest.fixture
def tmp_json_cache(tmp_path: Path) -> Path:
    return tmp_path / "proxies.json"


@pytest.fixture
def sample_proxy_text():
    """Sample plain text proxy list for testing."""
    return "192.168.1.1:8080\n10.0.0.1:3128\n172.16.0.1:1080\n"


@pytest.fixture
def malformed_proxy_text():
    """Malformed proxy data for testing error handling."""
    return """
192.168.1.1:8080
invalid-proxy-line
10.0.0.1:not-a-port
172.16.0.1:3128
just-text
:8080
192.168.1.1:
    """


@pytest.fixture
def loader_mock_factory():
    """Factory for creating consistent loader mocks."""

    def _create_loader_mock(
        response_text: str,
        status_code: int = 200,
        should_raise: bool = False,
        exception_class: type[Exception] | None = None,
    ):
        mock_response = Mock()
        mock_response.text = response_text
        mock_response.status_code = status_code

        if should_raise:
            if exception_class:
                mock_response.raise_for_status.side_effect = exception_class("HTTP Error")
            else:
                mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                    "HTTP Error", request=Mock(), response=mock_response
                )
        else:
            mock_response.raise_for_status.return_value = None

        return mock_response

    return _create_loader_mock


# comprehensive_proxy_list defined earlier; avoid duplicate redefinition.


@pytest.fixture
def cache_backend_configs() -> Dict[str, Dict[str, Any]]:
    """Configuration for testing different cache backends."""
    return {
        "memory": {"type": "MEMORY", "path": None},
        "json": {"type": "JSON", "path": "test_cache.json"},
        "sqlite": {"type": "SQLITE", "path": "test_cache.sqlite"},
    }


@pytest.fixture
def rotation_strategy_configs() -> List[str]:
    """Configuration for testing different rotation strategies."""
    return ["ROUND_ROBIN", "RANDOM", "WEIGHTED", "HEALTH_BASED", "LEAST_USED"]
