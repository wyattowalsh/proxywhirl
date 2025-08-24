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
# ENHANCED ASYNC TESTING UTILITIES
# ============================================================================


@pytest.fixture
def mock_async_httpx_client():
    """Enhanced async httpx client mock with context manager support."""
    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    # Default successful response
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.text = "Success"
    mock_response.json.return_value = {"success": True}
    mock_response.raise_for_status.return_value = None

    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.post = AsyncMock(return_value=mock_response)

    return mock_client


@pytest.fixture
def mock_proxy_validator():
    """Mock ProxyValidator with configurable validation results."""
    from proxywhirl.validator import ValidationResult

    mock_validator = MagicMock()

    # Default successful validation
    mock_result = ValidationResult(
        proxy=None,  # Will be set by test
        is_valid=True,
        response_time=0.5,
        error=None,
        timestamp=datetime.now(timezone.utc),
    )

    mock_validator.validate_proxy = AsyncMock(return_value=mock_result)
    mock_validator.validate_proxy_async = AsyncMock(return_value=mock_result)  # For compatibility

    return mock_validator


@pytest.fixture
def mock_proxywhirl_settings():
    """Mock ProxyWhirl settings for configuration testing."""
    from proxywhirl.config import ProxyWhirlSettings

    return ProxyWhirlSettings(
        timeout=30.0,
        concurrent_limit=100,
        max_retries=3,
        cache_enabled=True,
        cache_ttl=3600,
        validation_timeout=10.0,
        validation_enabled=True,
    )


@pytest.fixture
def async_test_utilities():
    """Utilities for async testing patterns."""

    class AsyncTestUtils:
        @staticmethod
        async def run_with_timeout(coro, timeout=5.0):
            """Run coroutine with timeout."""
            return await asyncio.wait_for(coro, timeout=timeout)

        @staticmethod
        def create_mock_async_context_manager(return_value=None, side_effect=None):
            """Create a mock async context manager."""
            mock = MagicMock()
            mock.__aenter__ = AsyncMock(return_value=return_value or mock)
            mock.__aexit__ = AsyncMock(return_value=None)
            if side_effect:
                mock.__aenter__.side_effect = side_effect
            return mock

        @staticmethod
        def assert_async_called_with(mock_async, *args, **kwargs):
            """Assert async mock was called with specific arguments."""
            mock_async.assert_called_with(*args, **kwargs)

        @staticmethod
        async def collect_async_results(async_generator, limit=None):
            """Collect results from async generator."""
            results = []
            count = 0
            async for item in async_generator:
                results.append(item)
                count += 1
                if limit and count >= limit:
                    break
            return results

    return AsyncTestUtils()


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
# ENHANCED HTTP CLIENT MOCKS
# ============================================================================


@pytest.fixture
def comprehensive_httpx_mock():
    """Comprehensive httpx mock with multiple response scenarios."""
    mock_responses = {
        "success": {
            "status_code": 200,
            "text": "Success response",
            "json_data": {"status": "success", "data": []},
        },
        "not_found": {
            "status_code": 404,
            "text": "Not Found",
            "json_data": {"error": "Resource not found"},
            "raises": httpx.HTTPStatusError("404 Not Found", request=Mock(), response=Mock()),
        },
        "server_error": {
            "status_code": 500,
            "text": "Internal Server Error",
            "json_data": {"error": "Server error"},
            "raises": httpx.HTTPStatusError(
                "500 Internal Server Error", request=Mock(), response=Mock()
            ),
        },
        "timeout": {"raises": httpx.TimeoutException("Request timed out")},
        "connection_error": {"raises": httpx.ConnectError("Connection failed")},
    }

    def create_mock_response(scenario="success"):
        response_config = mock_responses.get(scenario, mock_responses["success"])

        if "raises" in response_config:
            mock_response = Mock()
            if "status_code" in response_config:
                mock_response.status_code = response_config["status_code"]
                mock_response.text = response_config["text"]
                mock_response.json.return_value = response_config["json_data"]
                mock_response.raise_for_status.side_effect = response_config["raises"]
            else:
                # Network-level errors
                mock_response = Mock()
                mock_response.get.side_effect = response_config["raises"]
                mock_response.post.side_effect = response_config["raises"]
        else:
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = response_config["status_code"]
            mock_response.text = response_config["text"]
            mock_response.json.return_value = response_config["json_data"]
            mock_response.raise_for_status.return_value = None

        return mock_response

    class HttpxMockFactory:
        def __init__(self):
            self.scenarios = mock_responses

        def create_client_mock(self, scenario="success"):
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)

            response = create_mock_response(scenario)
            mock_client.get = AsyncMock(return_value=response)
            mock_client.post = AsyncMock(return_value=response)

            return mock_client

        def create_response_sequence(self, scenarios):
            """Create mock that returns different responses in sequence."""
            responses = [create_mock_response(s) for s in scenarios]
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get = AsyncMock(side_effect=responses)
            return mock_client

    return HttpxMockFactory()


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
# COMPREHENSIVE LOADER MOCKING FIXTURES
# ============================================================================


@pytest.fixture
def loader_http_mock_factory():
    """Comprehensive factory for creating HTTP mocks for all loader types."""

    class LoaderMockFactory:

        # Sample data for different loader types
        LOADER_RESPONSES = {
            "thespeedx_http": "192.168.1.1:8080\n10.0.0.1:3128\n172.16.0.1:8000\n",
            "thespeedx_socks4": "203.0.113.1:1080\n198.51.100.1:1080\n",
            "thespeedx_socks5": "192.0.2.1:1080\n192.0.2.2:1080\n192.0.2.3:1080\n",
            "clarketm_raw": "192.168.1.100:8080\n10.0.0.100:3128\n172.16.0.100:1080\n",
            "monosans_http": "1.1.1.1:8080\n2.2.2.2:3128\n3.3.3.3:8000\n",
            "monosans_socks4": "4.4.4.4:1080\n5.5.5.5:1080\n",
            "monosans_socks5": "6.6.6.6:1080\n7.7.7.7:1080\n8.8.8.8:1080\n",
            "proxyscrape_api": """192.168.1.50:8080
10.0.0.50:3128
172.16.0.50:1080""",
            "vakhov_fresh": "203.0.113.50:8080\n198.51.100.50:3128\n",
            "proxifly_html": """<html>
<body>
<div class="proxy-content">
<table>
<tr><td>IP:PORT</td><td>Type</td><td>Country</td></tr>
<tr><td>192.168.2.1:8080</td><td>HTTP</td><td>US</td></tr>
<tr><td>10.0.1.1:3128</td><td>HTTP</td><td>GB</td></tr>
</table>
</div>
</body>
</html>""",
            "jetkai_http": "11.11.11.11:8080\n22.22.22.22:3128\n33.33.33.33:8000\n",
            "jetkai_socks": "44.44.44.44:1080\n55.55.55.55:1080\n",
        }

        ERROR_RESPONSES = {
            "empty": "",
            "invalid_format": "This is not proxy data!\nRandom text here",
            "malformed_json": '{"invalid": json data}',
            "html_no_proxies": "<html><body>No proxies found</body></html>",
            "partial_invalid": "192.168.1.1:8080\ninvalid-line\n10.0.0.1:3128\n",
            "unicode_chars": "192.168.1.1:8080 🚀\n10.0.0.1:3128 测试\n",
        }

        def create_success_mock(self, loader_type: str = "thespeedx_http", **kwargs):
            """Create a successful HTTP mock for specified loader type."""
            content = self.LOADER_RESPONSES.get(
                loader_type, self.LOADER_RESPONSES["thespeedx_http"]
            )
            return self._create_http_mock(
                content=content, status_code=200, content_type="text/plain", **kwargs
            )

        def create_error_mock(self, error_type: str = "empty", status_code: int = 404, **kwargs):
            """Create an error HTTP mock with specified error scenario."""
            content = self.ERROR_RESPONSES.get(error_type, "")
            exception = None

            if status_code >= 400:
                exception = httpx.HTTPStatusError(
                    f"{status_code} Error", request=Mock(), response=Mock(status_code=status_code)
                )

            return self._create_http_mock(
                content=content, status_code=status_code, raises=exception, **kwargs
            )

        def create_timeout_mock(self, timeout_type: str = "connect", **kwargs):
            """Create network timeout mock."""
            timeout_exceptions = {
                "connect": httpx.ConnectTimeout("Connection timed out"),
                "read": httpx.ReadTimeout("Read timed out"),
                "general": httpx.TimeoutException("Request timed out"),
            }
            exception = timeout_exceptions.get(timeout_type, timeout_exceptions["general"])

            return self._create_http_mock(raises=exception, **kwargs)

        def create_connection_error_mock(self, error_type: str = "connection_refused", **kwargs):
            """Create connection error mock."""
            connection_errors = {
                "connection_refused": httpx.ConnectError("Connection refused"),
                "dns_error": httpx.ConnectError("DNS resolution failed"),
                "ssl_error": httpx.ConnectError("SSL verification failed"),
                "network_unreachable": httpx.ConnectError("Network unreachable"),
            }
            exception = connection_errors.get(error_type, connection_errors["connection_refused"])

            return self._create_http_mock(raises=exception, **kwargs)

        def create_sequence_mock(self, response_sequence: list, **kwargs):
            """Create mock that returns different responses in sequence."""
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)

            responses = []
            for resp_config in response_sequence:
                if isinstance(resp_config, str):
                    # Simple content string
                    responses.append(self._create_response_mock(content=resp_config))
                elif isinstance(resp_config, dict):
                    # Full configuration
                    responses.append(self._create_response_mock(**resp_config))
                else:
                    # Exception
                    mock_resp = Mock()
                    mock_resp.get.side_effect = resp_config
                    responses.append(mock_resp)

            mock_client.get = AsyncMock(side_effect=responses)
            mock_client.post = AsyncMock(side_effect=responses)

            return mock_client

        def _create_http_mock(
            self,
            content: str = "",
            status_code: int = 200,
            content_type: str = "text/plain",
            raises: Exception = None,
            **kwargs,
        ):
            """Internal method to create HTTP mock."""
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)

            if raises:
                mock_client.get = AsyncMock(side_effect=raises)
                mock_client.post = AsyncMock(side_effect=raises)
            else:
                mock_response = self._create_response_mock(
                    content, status_code, content_type, **kwargs
                )
                mock_client.get = AsyncMock(return_value=mock_response)
                mock_client.post = AsyncMock(return_value=mock_response)

            return mock_client

        def _create_response_mock(
            self,
            content: str = "",
            status_code: int = 200,
            content_type: str = "text/plain",
            headers: dict = None,
            **kwargs,
        ):
            """Internal method to create response mock."""
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
                    mock_response.json.side_effect = json.JSONDecodeError(
                        "Invalid JSON", content, 0
                    )
            else:
                mock_response.json.side_effect = json.JSONDecodeError("Not JSON", content, 0)

            # Handle HTTP errors
            if status_code >= 400:
                mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                    f"{status_code} Error", request=Mock(), response=mock_response
                )
            else:
                mock_response.raise_for_status.return_value = None

            return mock_response

    return LoaderMockFactory()


@pytest.fixture
def all_loaders_mock_data():
    """Complete mock data for all loader types."""
    return {
        # TheSpeedX loader responses
        "thespeedx_responses": {
            "http": "1.1.1.1:8080\n2.2.2.2:3128\n3.3.3.3:8000\n4.4.4.4:9999\n",
            "https": "5.5.5.5:8443\n6.6.6.6:3128\n7.7.7.7:8080\n",
            "socks4": "8.8.8.8:1080\n9.9.9.9:1080\n10.10.10.10:1080\n",
            "socks5": "11.11.11.11:1080\n12.12.12.12:1080\n13.13.13.13:1080\n",
        },
        # Clarketm loader response
        "clarketm_response": """192.168.1.1:8080
10.0.0.1:3128
172.16.0.1:1080
203.0.113.1:8080
198.51.100.1:3128""",
        # Monosans loader responses
        "monosans_responses": {
            "http": "20.20.20.20:8080\n21.21.21.21:3128\n22.22.22.22:8000\n",
            "https": "23.23.23.23:8443\n24.24.24.24:3128\n",
            "socks4": "25.25.25.25:1080\n26.26.26.26:1080\n",
            "socks5": "27.27.27.27:1080\n28.28.28.28:1080\n29.29.29.29:1080\n",
        },
        # ProxyScrape API response
        "proxyscrape_response": """30.30.30.30:8080
31.31.31.31:3128
32.32.32.32:1080
33.33.33.33:8080""",
        # Vakhov Fresh response
        "vakhov_response": """34.34.34.34:8080
35.35.35.35:3128
36.36.36.36:1080""",
        # Proxifly HTML response
        "proxifly_html": """<html>
<head><title>Free Proxy List</title></head>
<body>
<div id="proxy-table">
<table class="table table-striped">
<thead>
<tr><th>IP Address</th><th>Port</th><th>Code</th><th>Country</th><th>Type</th></tr>
</thead>
<tbody>
<tr><td>40.40.40.40</td><td>8080</td><td>US</td><td>United States</td><td>HTTP</td></tr>
<tr><td>41.41.41.41</td><td>3128</td><td>GB</td><td>United Kingdom</td><td>HTTP</td></tr>
<tr><td>42.42.42.42</td><td>1080</td><td>DE</td><td>Germany</td><td>SOCKS5</td></tr>
</tbody>
</table>
</div>
</body>
</html>""",
        # JetKai proxy list responses
        "jetkai_responses": {
            "http": "50.50.50.50:8080\n51.51.51.51:3128\n52.52.52.52:8000\n",
            "socks": "53.53.53.53:1080\n54.54.54.54:1080\n",
        },
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
