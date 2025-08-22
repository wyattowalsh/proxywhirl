"""Tests for proxywhirl.loaders.monosans module.

Unit tests for the MonosansLoader class with comprehensive coverage.
"""

from unittest.mock import Mock, patch

import pytest
from pandas import DataFrame
from tenacity import RetryError

from proxywhirl.loaders.monosans import MonosansLoader


class TestMonosansLoader:
    """Test MonosansLoader with comprehensive coverage."""

    def test_loader_initialization(self):
        """Test loader initializes with correct properties."""
        loader = MonosansLoader()
        assert loader.name == "monosans"
        assert "monosans" in loader.description
        assert hasattr(loader, "url")
        assert loader.url is not None

    @patch("proxywhirl.loaders.monosans.httpx.Client")
    def test_load_success_with_valid_data(self, mock_client):
        """Test successful loading with valid proxy data."""
        # Mock JSON response with proxy data
        mock_response = Mock()
        mock_response.json.return_value = {
            "proxies": [
                {"ip": "192.168.1.1", "port": "8080", "protocol": "http"},
                {"ip": "10.0.0.1", "port": "3128", "protocol": "http"},
                {"ip": "172.16.0.1", "port": "1080", "protocol": "socks5"},
            ]
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = MonosansLoader()
        df = loader.load()

        # Verify the result
        assert isinstance(df, DataFrame)
        assert len(df) == 3
        assert list(df.columns) == ["host", "port", "protocol"]

        # Check specific proxy data
        hosts = set(df["host"].tolist())
        ports = set(df["port"].tolist())
        protocols = set(df["protocol"].tolist())

        assert hosts == {"192.168.1.1", "10.0.0.1", "172.16.0.1"}
        assert ports == {8080, 3128, 1080}
        assert protocols == {"http", "socks5"}

    @patch("proxywhirl.loaders.monosans.httpx.Client")
    def test_load_with_text_format(self, mock_client):
        """Test loading with text format response."""
        # Mock text response with proxy data
        mock_response = Mock()
        mock_response.text = """192.168.1.1:8080
10.0.0.1:3128
172.16.0.1:1080"""
        mock_response.json.side_effect = ValueError("Not JSON")
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = MonosansLoader()
        df = loader.load()

        # Verify the result
        assert isinstance(df, DataFrame)
        assert len(df) == 3
        assert list(df.columns) == ["host", "port", "protocol"]

    @patch("proxywhirl.loaders.monosans.httpx.Client")
    def test_load_with_malformed_json(self, mock_client):
        """Test loading handles malformed JSON gracefully."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "proxies": [
                {"ip": "192.168.1.1", "port": "8080", "protocol": "http"},
                {"ip": "invalid", "port": "not-a-port", "protocol": "http"},
                {"ip": "10.0.0.1", "port": "3128", "protocol": "http"},
                {"missing": "fields"},
            ]
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = MonosansLoader()
        df = loader.load()

        # Should only get valid proxies
        assert isinstance(df, DataFrame)
        # Exact count depends on implementation, but should have valid proxies
        assert len(df) >= 2
        valid_hosts = set(df["host"].tolist())
        assert "192.168.1.1" in valid_hosts
        assert "10.0.0.1" in valid_hosts

    @patch("proxywhirl.loaders.monosans.httpx.Client")
    def test_load_with_empty_response(self, mock_client):
        """Test loading with empty response."""
        mock_response = Mock()
        mock_response.json.return_value = {"proxies": []}
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = MonosansLoader()
        df = loader.load()

        assert isinstance(df, DataFrame)
        assert len(df) == 0

    @patch("proxywhirl.loaders.monosans.httpx.Client")
    def test_load_with_invalid_json_structure(self, mock_client):
        """Test loading with unexpected JSON structure."""
        mock_response = Mock()
        mock_response.json.return_value = {"unexpected": "structure"}
        mock_response.text = "192.168.1.1:8080\n10.0.0.1:3128"
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = MonosansLoader()
        df = loader.load()

        # Should fallback to text parsing
        assert isinstance(df, DataFrame)
        assert len(df) >= 2

    @patch("proxywhirl.loaders.monosans.httpx.Client")
    def test_load_http_error(self, mock_client):
        """Test handling of HTTP errors."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 404")

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = MonosansLoader()

        with pytest.raises(RetryError):
            loader.load()

    @patch("proxywhirl.loaders.monosans.httpx.Client")
    def test_load_network_timeout(self, mock_client):
        """Test handling of network timeouts."""
        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.side_effect = Exception("Connection timeout")
        mock_client.return_value = mock_client_instance

        loader = MonosansLoader()

        with pytest.raises(RetryError):
            loader.load()

    @patch("proxywhirl.loaders.monosans.httpx.Client")
    def test_load_with_mixed_protocols(self, mock_client):
        """Test loading with mixed protocol types."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "proxies": [
                {"ip": "192.168.1.1", "port": "8080", "protocol": "http"},
                {"ip": "10.0.0.1", "port": "1080", "protocol": "socks4"},
                {"ip": "172.16.0.1", "port": "1080", "protocol": "socks5"},
            ]
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        loader = MonosansLoader()
        df = loader.load()

        # Check protocol distribution
        assert isinstance(df, DataFrame)
        assert len(df) == 3
        protocols = df["protocol"].value_counts()
        assert "http" in protocols.index
        assert "socks4" in protocols.index or "socks5" in protocols.index

    def test_load_edge_cases(self):
        """Test edge cases and boundary conditions."""
        loader = MonosansLoader()

        # Test that loader has required attributes
        assert hasattr(loader, "name")
        assert hasattr(loader, "description")
        assert hasattr(loader, "url")
        assert hasattr(loader, "load")

        # Test string representations
        assert str(loader) == loader.name
        assert loader.name in repr(loader)
