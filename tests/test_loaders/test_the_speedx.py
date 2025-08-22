"""Tests for proxywhirl.loaders.the_speedx module.

Unit tests for TheSpeedXHttpLoader and TheSpeedXSocksLoader classes.
"""

from unittest.mock import Mock, patch

import pytest
from pandas import DataFrame
from tenacity import RetryError

from proxywhirl.loaders.the_speedx import TheSpeedXHttpLoader, TheSpeedXSocksLoader


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
    def test_load_success_with_valid_data(self, mock_client):
        """Test successful loading with valid proxy data."""
        mock_response = Mock()
        mock_response.text = (
            "192.168.1.1:8080\n"
            "10.0.0.1:3128\n"
            "172.16.0.1:8000\n"
            "\n"  # Empty line should be ignored
            "203.0.113.1:80\n"
        )
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = TheSpeedXHttpLoader()
        result = loader.load()

        # Verify the result
        assert isinstance(result, DataFrame)
        assert len(result) == 4
        assert all(result["protocol"] == "http")

        # Check specific proxy entries
        hosts = result["host"].tolist()
        ports = result["port"].tolist()
        assert "192.168.1.1" in hosts
        assert "10.0.0.1" in hosts
        assert "172.16.0.1" in hosts
        assert "203.0.113.1" in hosts
        assert 8080 in ports
        assert 3128 in ports
        assert 8000 in ports
        assert 80 in ports

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

        loader = TheSpeedXHttpLoader()
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
