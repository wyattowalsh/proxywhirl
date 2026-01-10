"""
Integration tests for ProxyRotator with mocked HTTP.
"""

from unittest.mock import MagicMock, Mock, patch

import httpx
import pytest

from proxywhirl import HealthStatus, Proxy, ProxyRotator
from proxywhirl.exceptions import ProxyPoolEmptyError


class TestProxyRotatorBasics:
    """Test basic ProxyRotator functionality."""

    def test_init_empty(self):
        """Test creating empty rotator."""
        rotator = ProxyRotator()
        assert rotator.pool.size == 0
        assert rotator.strategy is not None
        assert rotator.config is not None

    def test_init_with_proxies(self):
        """Test creating rotator with initial proxies."""
        proxies = [
            Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY),  # type: ignore
            Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY),  # type: ignore
        ]
        rotator = ProxyRotator(proxies=proxies)
        assert rotator.pool.size == 2

    def test_add_proxy_from_url_string(self):
        """Test adding proxy from URL string."""
        rotator = ProxyRotator()
        rotator.add_proxy("http://proxy.example.com:8080")
        assert rotator.pool.size == 1

    def test_add_proxy_from_proxy_object(self):
        """Test adding proxy from Proxy object."""
        rotator = ProxyRotator()
        proxy = Proxy(url="http://proxy.example.com:8080")  # type: ignore
        rotator.add_proxy(proxy)
        assert rotator.pool.size == 1

    def test_remove_proxy(self):
        """Test removing proxy."""
        rotator = ProxyRotator()
        proxy = Proxy(url="http://proxy.example.com:8080")  # type: ignore
        rotator.add_proxy(proxy)
        assert rotator.pool.size == 1

        rotator.remove_proxy(str(proxy.id))
        assert rotator.pool.size == 0


class TestProxyRotatorContextManager:
    """Test ProxyRotator context manager."""

    def test_context_manager_creates_client(self):
        """Test that context manager creates HTTP client."""
        rotator = ProxyRotator()
        assert rotator._client is None

        with rotator:
            assert rotator._client is not None

        assert rotator._client is None

    def test_context_manager_closes_client(self):
        """Test that context manager properly closes client."""
        rotator = ProxyRotator()

        with rotator as r:
            client = r._client
            assert client is not None

        # After exit, client should be None
        assert rotator._client is None


class TestProxyRotatorRequests:
    """Test ProxyRotator HTTP request methods with mocks."""

    @patch("httpx.Client")
    def test_get_request_with_mock(self, mock_client_class):
        """Test GET request with mocked httpx client."""
        # Setup mock
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"ip": "1.2.3.4"}

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        # Create rotator and add proxy
        rotator = ProxyRotator()
        rotator.add_proxy("http://proxy.example.com:8080")
        rotator.pool.proxies[0].health_status = HealthStatus.HEALTHY

        # Make request
        response = rotator.get("https://httpbin.org/ip")

        assert response.status_code == 200
        mock_client.request.assert_called_once()

    @patch("httpx.Client")
    def test_post_request_with_mock(self, mock_client_class):
        """Test POST request with mocked httpx client."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 201

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        rotator = ProxyRotator()
        rotator.add_proxy("http://proxy.example.com:8080")
        rotator.pool.proxies[0].health_status = HealthStatus.HEALTHY

        response = rotator.post("https://httpbin.org/post", json={"key": "value"})
        assert response.status_code == 201

    @patch("httpx.Client")
    def test_all_http_methods(self, mock_client_class):
        """Test all HTTP methods."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        rotator = ProxyRotator()
        rotator.add_proxy("http://proxy.example.com:8080")
        rotator.pool.proxies[0].health_status = HealthStatus.HEALTHY

        # Test all methods
        rotator.get("https://example.com")
        rotator.post("https://example.com")
        rotator.put("https://example.com")
        rotator.delete("https://example.com")
        rotator.patch("https://example.com")
        rotator.head("https://example.com")
        rotator.options("https://example.com")

        assert mock_client.request.call_count == 7

    def test_request_with_no_proxies_raises_error(self):
        """Test that request with no proxies raises ProxyPoolEmptyError."""
        rotator = ProxyRotator()

        with pytest.raises(ProxyPoolEmptyError):
            rotator.get("https://example.com")

    @patch("httpx.Client")
    def test_request_updates_stats(self, mock_client_class):
        """Test that requests update proxy statistics."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        rotator = ProxyRotator()
        rotator.add_proxy("http://proxy.example.com:8080")
        rotator.pool.proxies[0].health_status = HealthStatus.HEALTHY

        # Make successful request
        rotator.get("https://example.com")

        # Stats should be updated
        assert rotator.pool.proxies[0].total_successes == 1
        assert rotator.pool.proxies[0].total_requests == 1

    @patch("httpx.Client")
    def test_request_success_records_stats(self, mock_client_class):
        """Test that successful request records success stats."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        rotator = ProxyRotator()
        rotator.add_proxy("http://proxy.example.com:8080")
        rotator.pool.proxies[0].health_status = HealthStatus.HEALTHY

        rotator.get("https://example.com")

        assert rotator.pool.proxies[0].total_successes == 1
        assert rotator.pool.proxies[0].total_requests == 1


class TestProxyRotatorWithCredentials:
    """Test ProxyRotator with authenticated proxies."""

    def test_get_proxy_dict_without_credentials(self):
        """Test proxy dict generation without credentials."""
        rotator = ProxyRotator()
        proxy = Proxy(url="http://proxy.example.com:8080")  # type: ignore

        proxy_dict = rotator._get_proxy_dict(proxy)

        assert "http://" in proxy_dict
        assert "https://" in proxy_dict
        assert "proxy.example.com:8080" in proxy_dict["http://"]

    def test_get_proxy_dict_with_credentials(self):
        """Test proxy dict generation with credentials."""
        from pydantic import SecretStr

        rotator = ProxyRotator()
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            username=SecretStr("user"),
            password=SecretStr("pass"),
        )  # type: ignore

        proxy_dict = rotator._get_proxy_dict(proxy)

        assert "user:pass@proxy.example.com:8080" in proxy_dict["http://"]


class TestProxyRotatorWithContextManager:
    """Test ProxyRotator with context manager and persistent client."""

    @patch("httpx.Client")
    def test_request_with_persistent_client(self, mock_client_class):
        """Test request with persistent client in context manager."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        rotator = ProxyRotator()
        rotator.add_proxy("http://proxy.example.com:8080")
        rotator.pool.proxies[0].health_status = HealthStatus.HEALTHY

        with rotator:
            # Make multiple requests
            rotator.get("https://example.com")
            rotator.get("https://example.com")

        # Note: The client pool reuses clients for the same proxy
        # One client created in __enter__, one for the proxy
        assert mock_client_class.call_count == 2
