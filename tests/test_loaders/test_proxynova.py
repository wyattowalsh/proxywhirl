"""Tests for proxywhirl.loaders.proxynova module.

Unit tests for the ProxyNovaLoader class with comprehensive coverage.
"""

from unittest.mock import Mock, patch

import pytest
from pandas import DataFrame
from tenacity import RetryError

from proxywhirl.loaders.proxynova import ProxyNovaLoader


class TestProxyNovaLoader:
    """Test ProxyNovaLoader with comprehensive coverage."""

    def test_loader_initialization(self):
        """Test loader initializes with correct properties."""
        loader = ProxyNovaLoader()
        assert loader.name == "proxynova"
        assert "proxynova.com" in loader.description
        expected_url = "https://www.proxynova.com/proxy-server-list/port-80/"
        assert loader.url == expected_url

    @patch("proxywhirl.loaders.proxynova.httpx.Client")
    def test_load_success_with_valid_data(self, mock_client: Mock):
        """Test successful loading with valid proxy data."""
        # Mock HTML response with proxy data
        mock_response = Mock()
        mock_response.text = """
        <html>
        <body>
        <div>Some content</div>
        <p>192.168.1.1:8080</p>
        <p>10.0.0.1:3128</p>
        <p>172.16.0.1:8000</p>
        <div>Some other content</div>
        </body>
        </html>
        """
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = ProxyNovaLoader()
        result = loader.load()

        # Verify the result
        assert isinstance(result, DataFrame)
        assert len(result) == 3
        assert all(result["protocol"] == "http")

        # Check specific proxy entries
        hosts = result["host"].tolist()
        ports = result["port"].tolist()
        assert "192.168.1.1" in hosts
        assert "10.0.0.1" in hosts
        assert "172.16.0.1" in hosts
        assert 8080 in ports
        assert 3128 in ports
        assert 8000 in ports

    @patch("proxywhirl.loaders.proxynova.httpx.Client")
    def test_load_empty_response(self, mock_client: Mock):
        """Test handling of empty response."""
        mock_response = Mock()
        mock_response.text = "<html><body></body></html>"
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = ProxyNovaLoader()
        result = loader.load()

        # Should return empty DataFrame with correct columns
        assert isinstance(result, DataFrame)
        assert len(result) == 0
        assert list(result.columns) == ["host", "port", "protocol"]

    @patch("proxywhirl.loaders.proxynova.httpx.Client")
    def test_load_invalid_data_filtered(self, mock_client: Mock):
        """Test that invalid proxy data is filtered out."""
        mock_response = Mock()
        mock_response.text = """
        <html>
        <body>
        <p>192.168.1.1:8080</p>
        <p>invalid:data</p>
        <p>192.168.1.2:80</p>
        <p>not.a.proxy</p>
        <p>172.16.0.1:9999</p>
        </body>
        </html>
        """
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = ProxyNovaLoader()
        result = loader.load()

        # Should only return valid proxies
        assert isinstance(result, DataFrame)
        assert len(result) == 3
        hosts = result["host"].tolist()
        assert "192.168.1.1" in hosts
        assert "192.168.1.2" in hosts
        assert "172.16.0.1" in hosts

    @patch("proxywhirl.loaders.proxynova.httpx.Client")
    def test_load_http_error(self, mock_client: Mock):
        """Test handling of HTTP errors."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 404")

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = ProxyNovaLoader()

        # Should raise RetryError after all retry attempts
        with pytest.raises(RetryError):
            loader.load()

    @patch("proxywhirl.loaders.proxynova.httpx.Client")
    def test_load_connection_error(self, mock_client: Mock):
        """Test handling of connection errors."""
        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.side_effect = Exception("Connection failed")
        mock_client.return_value = mock_client_instance

        loader = ProxyNovaLoader()

        # Should raise RetryError after all retry attempts
        with pytest.raises(RetryError):
            loader.load()

    @patch("proxywhirl.loaders.proxynova.httpx.Client")
    def test_load_with_malformed_html(self, mock_client: Mock):
        """Test handling of malformed HTML."""
        mock_response = Mock()
        mock_response.text = """
        <html>
        <body>
        <p>192.168.1.1:8080</p>
        <p>Broken HTML <unclosed tag
        <p>10.0.0.1:3128</p>
        """
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = ProxyNovaLoader()
        result = loader.load()

        # Should still extract valid proxies despite malformed HTML
        assert isinstance(result, DataFrame)
        assert len(result) == 2
        hosts = result["host"].tolist()
        assert "192.168.1.1" in hosts
        assert "10.0.0.1" in hosts

    @patch("proxywhirl.loaders.proxynova.httpx.Client")
    def test_load_with_edge_case_ports(self, mock_client: Mock):
        """Test handling of edge case port numbers."""
        mock_response = Mock()
        mock_response.text = """
        <html>
        <body>
        <p>192.168.1.1:1</p>
        <p>192.168.1.2:65535</p>
        <p>192.168.1.3:0</p>
        <p>192.168.1.4:65536</p>
        </body>
        </html>
        """
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = ProxyNovaLoader()
        result = loader.load()

        # Should handle valid port ranges (1-65535)
        assert isinstance(result, DataFrame)
        ports = result["port"].tolist()
        assert 1 in ports
        assert 65535 in ports
        # Port 0 and 65536 should be filtered out if validation exists

    def test_loader_name_consistency(self):
        """Test that loader name is consistent."""
        loader1 = ProxyNovaLoader()
        loader2 = ProxyNovaLoader()
        assert loader1.name == loader2.name
        assert loader1.description == loader2.description
        assert loader1.url == loader2.url

    def test_loader_inheritance(self):
        """Test that ProxyNovaLoader inherits from BaseLoader correctly."""
        from proxywhirl.loaders.base import BaseLoader

        loader = ProxyNovaLoader()
        assert isinstance(loader, BaseLoader)
        assert hasattr(loader, "load")
        assert callable(loader.load)

    @patch("proxywhirl.loaders.proxynova.httpx.Client")
    def test_load_dataframe_structure(self, mock_client: Mock):
        """Test that returned DataFrame has correct structure."""
        mock_response = Mock()
        mock_response.text = "<p>192.168.1.1:8080</p>"
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = ProxyNovaLoader()
        result = loader.load()

        # Check DataFrame structure
        assert isinstance(result, DataFrame)
        assert "host" in result.columns
        assert "port" in result.columns
        assert "protocol" in result.columns

        if len(result) > 0:
            # Check data types
            assert result["port"].dtype in ["int64", "int32"]
            assert result["host"].dtype == "object"
            assert result["protocol"].dtype == "object"
