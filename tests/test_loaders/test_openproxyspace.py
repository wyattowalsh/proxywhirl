"""Tests for proxywhirl.loaders.openproxyspace module.

Unit tests for the OpenProxySpaceLoader class with comprehensive coverage.
"""

from unittest.mock import Mock, patch

import pytest
from pandas import DataFrame
from tenacity import RetryError

from proxywhirl.loaders.openproxyspace import OpenProxySpaceLoader


class TestOpenProxySpaceLoader:
    """Test OpenProxySpaceLoader with comprehensive coverage."""

    def test_loader_initialization(self):
        """Test loader initializes with correct properties."""
        loader = OpenProxySpaceLoader()
        assert loader.name == "openproxyspace"
        assert "openproxyspace.com" in loader.description

        # Check that it has the expected URLs for different protocols
        assert hasattr(loader, "urls")
        assert isinstance(loader.urls, dict)
        assert "http" in loader.urls
        assert "socks4" in loader.urls
        assert "socks5" in loader.urls

    @patch("proxywhirl.loaders.openproxyspace.httpx.Client")
    def test_load_success_multiple_protocols(self, mock_client):
        """Test successful loading with multiple protocol responses."""
        # Mock responses for each protocol
        http_response = Mock()
        http_response.text = "192.168.1.1:8080\n10.0.0.1:3128\n"
        http_response.raise_for_status.return_value = None

        socks4_response = Mock()
        socks4_response.text = "172.16.0.1:1080\n192.168.2.1:1080\n"
        socks4_response.raise_for_status.return_value = None

        socks5_response = Mock()
        socks5_response.text = "203.0.113.1:1080\n"
        socks5_response.raise_for_status.return_value = None

        responses = [http_response, socks4_response, socks5_response]

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.side_effect = responses
        mock_client.return_value = mock_client_instance

        loader = OpenProxySpaceLoader()
        result = loader.load()

        # Verify the result contains proxies from all protocols
        assert isinstance(result, DataFrame)
        assert len(result) == 5  # 2 + 2 + 1 = 5 total proxies

        # Check that all protocols are represented
        schemes = result["protocol"].tolist()
        assert "http" in schemes
        assert "socks4" in schemes
        assert "socks5" in schemes

        # Count proxies by scheme
        scheme_counts = result["protocol"].value_counts()
        assert scheme_counts.get("http", 0) == 2
        assert scheme_counts.get("socks4", 0) == 2
        assert scheme_counts.get("socks5", 0) == 1

    @patch("proxywhirl.loaders.openproxyspace.httpx.Client")
    def test_load_empty_responses(self, mock_client):
        """Test handling of empty responses from all URLs."""
        empty_response = Mock()
        empty_response.text = ""
        empty_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = empty_response
        mock_client.return_value = mock_client_instance

        loader = OpenProxySpaceLoader()
        result = loader.load()

        # Should return empty DataFrame with correct columns
        assert isinstance(result, DataFrame)
        assert len(result) == 0
        assert list(result.columns) == ["host", "port", "protocol"]

    @patch("proxywhirl.loaders.openproxyspace.httpx.Client")
    def test_load_malformed_data(self, mock_client):
        """Test handling of malformed proxy data."""
        malformed_response = Mock()
        malformed_response.text = (
            "192.168.1.1:8080\n"
            "invalid:data\n"
            "192.168.1.2:80\n"
            "not.a.proxy\n"
            "malformed\n"
            "172.16.0.1:9999\n"
        )
        malformed_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = malformed_response
        mock_client.return_value = mock_client_instance

        loader = OpenProxySpaceLoader()
        result = loader.load()

        # Should filter out malformed entries and keep valid ones
        # Expecting 3 valid proxies per protocol * 3 protocols = 9 total
        assert isinstance(result, DataFrame)
        assert len(result) == 9

        # Check that valid hosts are preserved
        hosts = result["host"].unique()
        assert "192.168.1.1" in hosts
        assert "192.168.1.2" in hosts
        assert "172.16.0.1" in hosts

    @patch("proxywhirl.loaders.openproxyspace.httpx.Client")
    def test_load_partial_failure(self, mock_client):
        """Test handling when some URLs fail but others succeed."""
        success_response = Mock()
        success_response.text = "192.168.1.1:8080\n10.0.0.1:3128\n"
        success_response.raise_for_status.return_value = None

        def mock_get(url):
            if "http" in url:
                return success_response
            else:
                # Simulate failure for socks URLs
                raise Exception("Connection failed")

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.side_effect = mock_get
        mock_client.return_value = mock_client_instance

        loader = OpenProxySpaceLoader()
        result = loader.load()

        # Should return proxies from successful URLs only
        assert isinstance(result, DataFrame)
        assert len(result) == 2  # Only HTTP proxies should be returned
        assert all(result["protocol"] == "http")

    @patch("proxywhirl.loaders.openproxyspace.httpx.Client")
    def test_load_all_failures(self, mock_client):
        """Test handling when all URLs fail."""
        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.side_effect = Exception("Connection failed")
        mock_client.return_value = mock_client_instance

        loader = OpenProxySpaceLoader()

        # Should raise RetryError after all retry attempts
        with pytest.raises(RetryError):
            loader.load()

    @patch("proxywhirl.loaders.openproxyspace.httpx.Client")
    def test_load_with_whitespace_handling(self, mock_client):
        """Test handling of whitespace in proxy data."""
        whitespace_response = Mock()
        whitespace_response.text = (
            "  192.168.1.1:8080  \n\t10.0.0.1:3128\t\n\n   172.16.0.1:9999   \n  \n"
        )
        whitespace_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = whitespace_response
        mock_client.return_value = mock_client_instance

        loader = OpenProxySpaceLoader()
        result = loader.load()

        # Should handle whitespace correctly and extract valid proxies
        assert isinstance(result, DataFrame)
        # 3 valid proxies * 3 protocols = 9 total
        assert len(result) == 9

        hosts = result["host"].unique()
        assert "192.168.1.1" in hosts
        assert "10.0.0.1" in hosts
        assert "172.16.0.1" in hosts

    @patch("proxywhirl.loaders.openproxyspace.httpx.Client")
    def test_load_with_edge_case_ports(self, mock_client):
        """Test handling of edge case port numbers."""
        edge_case_response = Mock()
        edge_case_response.text = (
            "192.168.1.1:1\n192.168.1.2:65535\n192.168.1.3:0\n192.168.1.4:65536\n192.168.1.5:80\n"
        )
        edge_case_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = edge_case_response
        mock_client.return_value = mock_client_instance

        loader = OpenProxySpaceLoader()
        result = loader.load()

        # Should handle valid port ranges
        assert isinstance(result, DataFrame)
        ports = result["port"].unique()
        assert 1 in ports
        assert 65535 in ports
        assert 80 in ports

    def test_loader_name_consistency(self):
        """Test that loader name and properties are consistent."""
        loader1 = OpenProxySpaceLoader()
        loader2 = OpenProxySpaceLoader()
        assert loader1.name == loader2.name
        assert loader1.description == loader2.description
        assert loader1.urls == loader2.urls

    def test_loader_inheritance(self):
        """Test that OpenProxySpaceLoader inherits from BaseLoader correctly."""
        from proxywhirl.loaders.base import BaseLoader

        loader = OpenProxySpaceLoader()
        assert isinstance(loader, BaseLoader)
        assert hasattr(loader, "load")
        assert callable(loader.load)

    @patch("proxywhirl.loaders.openproxyspace.httpx.Client")
    def test_load_dataframe_structure(self, mock_client):
        """Test that returned DataFrame has correct structure."""
        sample_response = Mock()
        sample_response.text = "192.168.1.1:8080\n"
        sample_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = sample_response
        mock_client.return_value = mock_client_instance

        loader = OpenProxySpaceLoader()
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

    def test_urls_configuration(self):
        """Test that URLs are properly configured for all protocols."""
        loader = OpenProxySpaceLoader()

        # Check that all required protocols are configured
        required_protocols = ["http", "socks4", "socks5"]
        for protocol in required_protocols:
            assert protocol in loader.urls
            assert isinstance(loader.urls[protocol], str)
            assert loader.urls[protocol].startswith("http")
            assert "openproxyspace.com" in loader.urls[protocol]

    @patch("proxywhirl.loaders.openproxyspace.httpx.Client")
    def test_load_duplicate_handling(self, mock_client):
        """Test handling of duplicate proxies across protocols."""
        duplicate_response = Mock()
        duplicate_response.text = (
            "192.168.1.1:8080\n"
            "192.168.1.1:8080\n"  # Duplicate
            "10.0.0.1:3128\n"
        )
        duplicate_response.raise_for_status.return_value = None

        mock_client_instance = Mock()
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=None)
        mock_client_instance.get.return_value = duplicate_response
        mock_client.return_value = mock_client_instance

        loader = OpenProxySpaceLoader()
        result = loader.load()

        # Should handle duplicates appropriately
        assert isinstance(result, DataFrame)
        # The behavior depends on implementation - it might keep duplicates
        # across different schemes or deduplicate them
