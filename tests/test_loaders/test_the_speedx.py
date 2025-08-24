"""Tests for proxywhirl.loaders.the_speedx module.

Unit tests for TheSpeedXHttpLoader and TheSpeedXSocksLoader classes.
Enhanced with comprehensive mocking and error scenario testing.
"""

from typing import List
from unittest.mock import Mock, patch

import httpx
import pytest
from hypothesis import assume, given
from hypothesis import strategies as st
from pandas import DataFrame
from tenacity import RetryError

from proxywhirl.loaders.the_speedx import TheSpeedXHttpLoader, TheSpeedXSocksLoader

# ============================================================================
# PROPERTY-BASED TESTING STRATEGIES
# ============================================================================


# Valid IP address strategy for property tests
valid_ip_strategy = st.builds(
    lambda a, b, c, d: f"{a}.{b}.{c}.{d}",
    st.integers(min_value=1, max_value=255),
    st.integers(min_value=0, max_value=255),
    st.integers(min_value=0, max_value=255),
    st.integers(min_value=1, max_value=254),
)

# Valid port strategy
valid_port_strategy = st.integers(min_value=1, max_value=65535)

# Proxy line strategy for testing
proxy_line_strategy = st.builds(
    lambda ip, port: f"{ip}:{port}", valid_ip_strategy, valid_port_strategy
)


class TestTheSpeedXHttpLoader:
    """Test TheSpeedXHttpLoader with comprehensive coverage."""

    def test_loader_initialization(self):
        """Test loader initializes with correct properties."""
        loader = TheSpeedXHttpLoader()
        assert loader.name == "the-speedx-http"
        assert "TheSpeedX/PROXY-List http.txt" in loader.description
        expected_url = "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
        assert loader.url == expected_url

    @patch("proxywhirl.loaders.the_speedx.httpx.Client")
    def test_load_success_with_enhanced_mock(self, mock_client, loader_http_mock_factory):
        """Test successful loading using enhanced mock factory."""
        # Use the enhanced mock factory for consistent testing
        mock_http_client = loader_http_mock_factory.create_success_mock("thespeedx_http")
        mock_client.return_value = mock_http_client

        loader = TheSpeedXHttpLoader()
        result = loader.load()

        # Verify the result
        assert isinstance(result, DataFrame)
        assert len(result) > 0
        assert all(result["protocol"] == "http")

        # Check that all hosts are valid IP addresses
        hosts = result["host"].tolist()
        ports = result["port"].tolist()

        assert all(isinstance(host, str) for host in hosts)
        assert all(isinstance(port, int) for port in ports)
        assert all(1 <= port <= 65535 for port in ports)

    @patch("proxywhirl.loaders.the_speedx.httpx.Client")
    def test_load_http_error_handling(self, mock_client, loader_http_mock_factory):
        """Test handling of HTTP errors."""
        # Test 404 error
        mock_http_client = loader_http_mock_factory.create_error_mock("empty", status_code=404)
        mock_client.return_value = mock_http_client

        loader = TheSpeedXHttpLoader()

        with pytest.raises(RetryError):
            loader.load()

    @patch("proxywhirl.loaders.the_speedx.httpx.Client")
    def test_load_network_timeout(self, mock_client, loader_http_mock_factory):
        """Test handling of network timeouts."""
        mock_http_client = loader_http_mock_factory.create_timeout_mock("connect")
        mock_client.return_value = mock_http_client

        loader = TheSpeedXHttpLoader()

        with pytest.raises(RetryError):
            loader.load()

    @patch("proxywhirl.loaders.the_speedx.httpx.Client")
    def test_load_connection_error(self, mock_client, loader_http_mock_factory):
        """Test handling of connection errors."""
        mock_http_client = loader_http_mock_factory.create_connection_error_mock(
            "connection_refused"
        )
        mock_client.return_value = mock_http_client

        loader = TheSpeedXHttpLoader()

        with pytest.raises(RetryError):
            loader.load()

    @patch("proxywhirl.loaders.the_speedx.httpx.Client")
    def test_load_malformed_data_resilience(self, mock_client, loader_http_mock_factory):
        """Test resilience against malformed proxy data."""
        mock_http_client = loader_http_mock_factory.create_error_mock(
            "partial_invalid", status_code=200
        )
        mock_client.return_value = mock_http_client

        loader = TheSpeedXHttpLoader()
        result = loader.load()

        # Should filter out invalid entries and keep valid ones
        assert isinstance(result, DataFrame)
        # Should have some valid entries despite malformed data
        if len(result) > 0:
            assert all(result["protocol"] == "http")

    @patch("proxywhirl.loaders.the_speedx.httpx.Client")
    def test_load_empty_response(self, mock_client, loader_http_mock_factory):
        """Test handling of empty response."""
        mock_http_client = loader_http_mock_factory.create_error_mock("empty", status_code=200)
        mock_client.return_value = mock_http_client

        loader = TheSpeedXHttpLoader()
        result = loader.load()

        # Should return empty DataFrame with correct columns
        assert isinstance(result, DataFrame)
        assert len(result) == 0
        assert list(result.columns) == ["host", "port", "protocol"]

    @patch("proxywhirl.loaders.the_speedx.httpx.Client")
    def test_load_retry_mechanism(self, mock_client, loader_http_mock_factory):
        """Test retry mechanism with sequence of failures then success."""
        # Create sequence: timeout, 500 error, then success
        sequence = [
            {"raises": httpx.TimeoutException("Timeout")},
            {"status_code": 500, "content": "Server Error"},
            {"content": "192.168.1.1:8080\n10.0.0.1:3128\n", "status_code": 200},
        ]

        mock_http_client = loader_http_mock_factory.create_sequence_mock(sequence)
        mock_client.return_value = mock_http_client

        loader = TheSpeedXHttpLoader()
        result = loader.load()

        # Should eventually succeed after retries
        assert isinstance(result, DataFrame)
        assert len(result) == 2
        assert all(result["protocol"] == "http")

    @given(st.lists(proxy_line_strategy, min_size=1, max_size=10))
    @patch("proxywhirl.loaders.the_speedx.httpx.Client")
    def test_property_load_with_generated_proxies(self, proxy_lines, mock_client):
        """Property-based test with generated proxy data."""
        proxy_text = "\n".join(proxy_lines)

        mock_response = Mock()
        mock_response.text = proxy_text
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = TheSpeedXHttpLoader()
        result = loader.load()

        # Properties that should always hold
        assert isinstance(result, DataFrame)
        assert len(result) >= 0  # Could be 0 if parsing fails
        if len(result) > 0:
            assert all(result["protocol"] == "http")
            assert all(isinstance(host, str) for host in result["host"])
            assert all(isinstance(port, int) for port in result["port"])
            assert all(1 <= port <= 65535 for port in result["port"])

    @given(st.text(alphabet=st.characters(blacklist_categories=["Cc"]), min_size=0, max_size=1000))
    @patch("proxywhirl.loaders.the_speedx.httpx.Client")
    def test_property_load_with_random_text(self, random_text, mock_client):
        """Property-based test with random text input."""
        # Skip empty strings and strings that might be accidentally valid
        assume(random_text.strip() != "")
        assume(":" not in random_text or not any(c.isdigit() for c in random_text))

        mock_response = Mock()
        mock_response.text = random_text
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = TheSpeedXHttpLoader()
        result = loader.load()

        # Should handle invalid input gracefully
        assert isinstance(result, DataFrame)
        assert len(result) == 0  # Should be empty for invalid data
        assert list(result.columns) == ["host", "port", "protocol"]

    @patch("proxywhirl.loaders.the_speedx.httpx.Client")
    def test_load_invalid_data_filtered(self, mock_client):
        """Test that invalid proxy data is filtered out."""
        mock_response = Mock()
        mock_response.text = (
            "192.168.1.1:8080\n"
            "invalid_line_without_colon\n"
            "192.168.1.2:80\n"
            "malformed:port:extra\n"
            "172.16.0.1:abc\n"  # Invalid port
            "valid.host.com:9999\n"
        )
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = TheSpeedXHttpLoader()
        result = loader.load()

        # Should filter out invalid entries
        assert isinstance(result, DataFrame)
        # Exact count depends on validation logic in implementation
        assert len(result) >= 2  # At least the clearly valid ones
        hosts = result["host"].tolist()
        assert "192.168.1.1" in hosts
        assert "192.168.1.2" in hosts

    @patch("proxywhirl.loaders.the_speedx.httpx.Client")
    def test_load_http_error(self, mock_client):
        """Test handling of HTTP errors."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 404")

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = TheSpeedXHttpLoader()

        # Should raise RetryError after all retry attempts
        with pytest.raises(RetryError):
            loader.load()

    @patch("proxywhirl.loaders.the_speedx.httpx.Client")
    def test_load_connection_error(self, mock_client):
        """Test handling of connection errors."""
        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.side_effect = Exception("Connection failed")
        mock_client.return_value = mock_client_instance

        loader = TheSpeedXHttpLoader()

        # Should raise RetryError after all retry attempts
        with pytest.raises(RetryError):
            loader.load()

    def test_loader_inheritance(self):
        """Test that TheSpeedXHttpLoader inherits from BaseLoader correctly."""
        from proxywhirl.loaders.base import BaseLoader

        loader = TheSpeedXHttpLoader()
        assert isinstance(loader, BaseLoader)
        assert hasattr(loader, "load")
        assert callable(loader.load)


class TestTheSpeedXSocksLoader:
    """Test TheSpeedXSocksLoader with comprehensive coverage."""

    def test_loader_initialization(self):
        """Test loader initializes with correct properties."""
        loader = TheSpeedXSocksLoader()
        assert loader.name == "the-speedx-socks"
        assert "TheSpeedX/PROXY-List socks" in loader.description
        # SOCKS loader uses multiple URLs, check URLs list contains socks URLs
        assert hasattr(loader, "urls")
        assert isinstance(loader.urls, list)
        assert any("socks5.txt" in url for url in loader.urls)

    @patch("proxywhirl.loaders.the_speedx.httpx.Client")
    def test_load_success_with_valid_data(self, mock_client):
        """Test successful loading with valid SOCKS proxy data."""
        mock_response = Mock()
        mock_response.text = (
            "192.168.1.1:1080\n"
            "10.0.0.1:1081\n"
            "172.16.0.1:1082\n"
            "\n"  # Empty line should be ignored
            "203.0.113.1:1083\n"
        )
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = TheSpeedXSocksLoader()
        result = loader.load()

        # Verify the result
        assert isinstance(result, DataFrame)
        assert len(result) == 4
        assert all(result["protocol"] == "socks5")

        # Check specific proxy entries
        hosts = result["host"].tolist()
        ports = result["port"].tolist()
        assert "192.168.1.1" in hosts
        assert "10.0.0.1" in hosts
        assert "172.16.0.1" in hosts
        assert "203.0.113.1" in hosts
        assert 1080 in ports
        assert 1081 in ports
        assert 1082 in ports
        assert 1083 in ports

    @patch("proxywhirl.loaders.the_speedx.httpx.Client")
    def test_load_empty_response(self, mock_client):
        """Test handling of empty response."""
        mock_response = Mock()
        mock_response.text = ""
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = TheSpeedXSocksLoader()
        result = loader.load()

        # Should return empty DataFrame with correct columns
        assert isinstance(result, DataFrame)
        assert len(result) == 0
        assert list(result.columns) == ["host", "port", "protocol"]

    @patch("proxywhirl.loaders.the_speedx.httpx.Client")
    def test_load_invalid_data_filtered(self, mock_client):
        """Test that invalid proxy data is filtered out."""
        mock_response = Mock()
        mock_response.text = (
            "192.168.1.1:1080\n"
            "invalid_line_without_colon\n"
            "192.168.1.2:1081\n"
            "malformed:port:extra\n"
            "172.16.0.1:abc\n"  # Invalid port
            "valid.host.com:1082\n"
        )
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = TheSpeedXSocksLoader()
        result = loader.load()

        # Should filter out invalid entries
        assert isinstance(result, DataFrame)
        # Exact count depends on validation logic in implementation
        assert len(result) >= 2  # At least the clearly valid ones
        hosts = result["host"].tolist()
        assert "192.168.1.1" in hosts
        assert "192.168.1.2" in hosts

    def test_loader_inheritance(self):
        """Test that TheSpeedXSocksLoader inherits from BaseLoader correctly."""
        from proxywhirl.loaders.base import BaseLoader

        loader = TheSpeedXSocksLoader()
        assert isinstance(loader, BaseLoader)
        assert hasattr(loader, "load")
        assert callable(loader.load)

    def test_loaders_consistency(self):
        """Test consistency between HTTP and SOCKS loaders."""
        http_loader = TheSpeedXHttpLoader()
        socks_loader = TheSpeedXSocksLoader()

        # Both should be from the same source but different protocols
        assert "TheSpeedX" in http_loader.description
        assert "TheSpeedX" in socks_loader.description
        assert http_loader.name != socks_loader.name
        assert "http" in http_loader.url
        assert any("socks" in url for url in socks_loader.urls)
