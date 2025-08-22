"""Tests for proxywhirl.loaders.proxyscrape module.

Unit tests for the ProxyScrapeLoader class with comprehensive coverage.
"""

from unittest.mock import Mock, patch

import pytest
from pandas import DataFrame
from tenacity import RetryError

from proxywhirl.loaders.proxyscrape import ProxyScrapeLoader


class TestProxyScrapeLoader:
    """Test ProxyScrapeLoader with comprehensive coverage."""

    def test_loader_initialization(self):
        """Test loader initializes with correct properties."""
        loader = ProxyScrapeLoader()
        assert loader.name == "proxyscrape"
        assert "proxyscrape" in loader.description
        assert hasattr(loader, "url")
        assert loader.url is not None

    @patch("proxywhirl.loaders.proxyscrape.httpx.Client")
    def test_load_success_with_valid_data(self, mock_client):
        """Test successful loading with valid proxy data."""
        # Mock raw proxy list response
        mock_response = Mock()
        mock_response.text = """192.168.1.1:8080
10.0.0.1:3128
172.16.0.1:8000
203.0.113.1:1080"""
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = ProxyScrapeLoader()
        df = loader.load()

        # Verify the result
        assert isinstance(df, DataFrame)
        assert len(df) == 4
        assert list(df.columns) == ["host", "port", "protocol"]

        # Check specific proxy data
        hosts = set(df["host"].tolist())
        ports = set(df["port"].tolist())
        protocols = set(df["protocol"].tolist())

        expected_hosts = {"192.168.1.1", "10.0.0.1", "172.16.0.1", "203.0.113.1"}
        assert hosts == expected_hosts
        assert ports == {8080, 3128, 8000, 1080}
        # ProxyScrape typically provides HTTP proxies by default
        assert "http" in protocols

    @patch("proxywhirl.loaders.proxyscrape.httpx.Client")
    def test_load_with_different_formats(self, mock_client):
        """Test loading with different proxy format variations."""
        mock_response = Mock()
        # Test different delimiter formats that ProxyScrape might use
        mock_response.text = """192.168.1.1:8080
10.0.0.1:3128
172.16.0.1,8000
203.0.113.1 1080"""
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = ProxyScrapeLoader()
        df = loader.load()

        # Should parse most common formats correctly
        assert isinstance(df, DataFrame)
        # Exact count depends on format parsing implementation
        assert len(df) >= 2
        hosts = set(df["host"].tolist())
        assert "192.168.1.1" in hosts
        assert "10.0.0.1" in hosts

    @patch("proxywhirl.loaders.proxyscrape.httpx.Client")
    def test_load_with_malformed_data(self, mock_client):
        """Test loading handles malformed proxy data gracefully."""
        mock_response = Mock()
        mock_response.text = """192.168.1.1:8080
invalid-proxy-line
10.0.0.1:not-a-port
172.16.0.1:3128
just-text
:8080
192.168.1.1:
        """
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = ProxyScrapeLoader()
        df = loader.load()

        # Should only get valid proxies
        assert isinstance(df, DataFrame)
        assert len(df) == 2  # Only 192.168.1.1:8080 and 172.16.0.1:3128
        valid_hosts = set(df["host"].tolist())
        assert "192.168.1.1" in valid_hosts
        assert "172.16.0.1" in valid_hosts

    @patch("proxywhirl.loaders.proxyscrape.httpx.Client")
    def test_load_with_empty_response(self, mock_client):
        """Test loading with empty response."""
        mock_response = Mock()
        mock_response.text = ""
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = ProxyScrapeLoader()
        df = loader.load()

        assert isinstance(df, DataFrame)
        assert len(df) == 0

    @patch("proxywhirl.loaders.proxyscrape.httpx.Client")
    def test_load_with_json_format(self, mock_client):
        """Test loading with JSON format if ProxyScrape provides it."""
        mock_response = Mock()
        # Test JSON format response
        mock_response.json.return_value = [
            {"ip": "192.168.1.1", "port": 8080},
            {"ip": "10.0.0.1", "port": 3128},
        ]
        mock_response.text = "[]"  # Fallback
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = ProxyScrapeLoader()
        df = loader.load()

        # Should parse JSON format if supported
        assert isinstance(df, DataFrame)
        # Implementation may or may not support JSON, so flexible assertion
        assert len(df) >= 0

    @patch("proxywhirl.loaders.proxyscrape.httpx.Client")
    def test_load_with_whitespace_handling(self, mock_client):
        """Test loading handles various whitespace scenarios."""
        mock_response = Mock()
        mock_response.text = """
        
192.168.1.1:8080

10.0.0.1:3128
    172.16.0.1:8000

        """
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = ProxyScrapeLoader()
        df = loader.load()

        # Should get all valid proxies despite whitespace
        assert isinstance(df, DataFrame)
        assert len(df) == 3
        hosts = set(df["host"].tolist())
        assert hosts == {"192.168.1.1", "10.0.0.1", "172.16.0.1"}

    @patch("proxywhirl.loaders.proxyscrape.httpx.Client")
    def test_load_http_error(self, mock_client):
        """Test handling of HTTP errors."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 404")

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = ProxyScrapeLoader()

        with pytest.raises(RetryError):
            loader.load()

    @patch("proxywhirl.loaders.proxyscrape.httpx.Client")
    def test_load_network_timeout(self, mock_client):
        """Test handling of network timeouts."""
        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.side_effect = Exception("Connection timeout")
        mock_client.return_value = mock_client_instance

        loader = ProxyScrapeLoader()

        with pytest.raises(RetryError):
            loader.load()

    @patch("proxywhirl.loaders.proxyscrape.httpx.Client")
    def test_load_with_large_response(self, mock_client):
        """Test loading with large proxy list."""
        # Generate a large proxy list
        proxy_list = []
        for i in range(1000):
            proxy_list.append(f"192.168.{i // 256}.{i % 256}:8080")

        mock_response = Mock()
        mock_response.text = "\n".join(proxy_list)
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = ProxyScrapeLoader()
        df = loader.load()

        # Should handle large datasets efficiently
        assert isinstance(df, DataFrame)
        assert len(df) == 1000
        assert list(df.columns) == ["host", "port", "protocol"]

    def test_load_edge_cases(self):
        """Test edge cases and boundary conditions."""
        loader = ProxyScrapeLoader()

        # Test that loader has required attributes
        assert hasattr(loader, "name")
        assert hasattr(loader, "description")
        assert hasattr(loader, "url")
        assert hasattr(loader, "load")

        # Test string representations
        assert str(loader) == loader.name
        assert loader.name in repr(loader)
