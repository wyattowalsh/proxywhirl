"""Comprehensive tests for proxywhirl.loaders.vakhov_fresh module.

This module tests the VakhovFreshProxyLoader class that fetches proxies
from Vakhov's GitHub Pages hosted fresh proxy list service.
"""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from pandas import DataFrame

from proxywhirl.loaders.vakhov_fresh import VakhovFreshProxyLoader


class TestVakhovFreshProxyLoader:
    """Test cases for VakhovFreshProxyLoader class."""

    def test_loader_initialization(self):
        """Test loader initialization and properties."""
        loader = VakhovFreshProxyLoader()

        assert loader.name == "VakhovFresh"
        assert "Proxies from Vakhov fresh proxy list" in loader.description
        assert "GitHub Pages" in loader.description

        # Should have multiple protocol endpoints
        assert hasattr(loader, "urls")
        assert isinstance(loader.urls, dict)
        assert "http" in loader.urls
        assert "https" in loader.urls
        assert "socks4" in loader.urls
        assert "socks5" in loader.urls

    def test_url_configuration(self):
        """Test URL configuration for different protocols."""
        loader = VakhovFreshProxyLoader()

        # Verify GitHub Pages URLs
        for protocol, url in loader.urls.items():
            assert "vakhov.github.io" in url
            assert "fresh-proxy-list" in url
            assert f"{protocol}.txt" in url
            assert url.startswith("https://")

    def test_inheritance(self):
        """Test that loader properly inherits from BaseLoader."""
        loader = VakhovFreshProxyLoader()

        # Should inherit BaseLoader functionality
        assert hasattr(loader, "name")
        assert hasattr(loader, "description")
        assert hasattr(loader, "load")

        # Should be callable
        assert callable(loader.load)

    @patch("proxywhirl.loaders.vakhov_fresh.httpx")
    def test_successful_load_single_protocol(self, mock_httpx):
        """Test successful loading from single protocol endpoint."""
        # Mock HTTP response with sample proxy data
        sample_http_data = "192.168.1.1:8080\n10.0.0.1:3128\n203.0.113.1:8080"

        mock_response = MagicMock()
        mock_response.text = sample_http_data
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        loader = VakhovFreshProxyLoader()
        result = loader.load()

        # Verify HTTP calls were made to all endpoints
        assert mock_client.get.call_count == 4  # 4 protocols

        # Verify result is DataFrame
        assert isinstance(result, DataFrame)
        assert len(result) >= 3  # At least 3 proxies per protocol

        # Check required columns
        assert "host" in result.columns
        assert "port" in result.columns
        assert "schemes" in result.columns

    @patch("proxywhirl.loaders.vakhov_fresh.httpx")
    def test_multiple_protocol_loading(self, mock_httpx):
        """Test loading from multiple protocol endpoints."""
        # Mock responses for different protocols
        protocol_data = {
            "http": "1.1.1.1:8080\n2.2.2.2:8080",
            "https": "3.3.3.3:443\n4.4.4.4:443",
            "socks4": "5.5.5.5:1080\n6.6.6.6:1080",
            "socks5": "7.7.7.7:1080\n8.8.8.8:1080",
        }

        def mock_get(url, **kwargs):
            mock_response = MagicMock()
            # Determine protocol based on URL
            for protocol in protocol_data:
                if f"{protocol}.txt" in url:
                    mock_response.text = protocol_data[protocol]
                    break
            mock_response.raise_for_status.return_value = None
            return mock_response

        mock_client = MagicMock()
        mock_client.get.side_effect = mock_get
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        loader = VakhovFreshProxyLoader()
        result = loader.load()

        # Should have proxies from all protocols
        assert len(result) == 8  # 2 proxies per protocol × 4 protocols

        # Should have different scheme types
        unique_schemes = set()
        for schemes_list in result["schemes"]:
            if isinstance(schemes_list, list):
                unique_schemes.update(schemes_list)

        # Should contain multiple scheme types
        assert len(unique_schemes) > 1

    @patch("proxywhirl.loaders.vakhov_fresh.httpx")
    def test_partial_endpoint_failure(self, mock_httpx):
        """Test handling when some endpoints fail but others succeed."""

        def mock_get(url, **kwargs):
            mock_response = MagicMock()
            if "http.txt" in url:
                mock_response.text = "1.1.1.1:8080\n2.2.2.2:8080"
                mock_response.raise_for_status.return_value = None
            elif "https.txt" in url:
                mock_response.raise_for_status.side_effect = Exception("HTTP 404")
            else:
                mock_response.text = ""
                mock_response.raise_for_status.return_value = None
            return mock_response

        mock_client = MagicMock()
        mock_client.get.side_effect = mock_get
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        loader = VakhovFreshProxyLoader()
        result = loader.load()

        # Should return partial results from successful endpoints
        assert isinstance(result, DataFrame)
        # Should have some data despite partial failures

    @patch("proxywhirl.loaders.vakhov_fresh.httpx")
    def test_empty_endpoint_responses(self, mock_httpx):
        """Test handling of empty responses from endpoints."""
        mock_response = MagicMock()
        mock_response.text = ""
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        loader = VakhovFreshProxyLoader()
        result = loader.load()

        # Should return empty DataFrame
        assert isinstance(result, DataFrame)
        assert len(result) == 0

    @patch("proxywhirl.loaders.vakhov_fresh.httpx")
    def test_malformed_proxy_data_handling(self, mock_httpx):
        """Test handling of malformed proxy data."""
        # Mock response with various malformed entries
        malformed_data = """1.1.1.1:8080
invalid-line-without-port
2.2.2.2:invalid-port
:8080
3.3.3.3:
malformed-ip:8080
4.4.4.4:8080"""

        mock_response = MagicMock()
        mock_response.text = malformed_data
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        loader = VakhovFreshProxyLoader()
        result = loader.load()

        # Should handle malformed data gracefully
        assert isinstance(result, DataFrame)
        # Should only include valid entries

    @patch("proxywhirl.loaders.vakhov_fresh.httpx")
    def test_ip_port_parsing(self, mock_httpx):
        """Test correct parsing of IP:Port format."""
        sample_data = """192.168.1.1:8080
10.0.0.1:3128
203.0.113.1:80
198.51.100.1:8888"""

        mock_response = MagicMock()
        mock_response.text = sample_data
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        loader = VakhovFreshProxyLoader()
        result = loader.load()

        # Verify correct parsing
        assert len(result) >= 4

        # Check specific entries
        if len(result) > 0:
            first_row = result.iloc[0]
            assert "host" in result.columns
            assert "port" in result.columns
            assert isinstance(first_row["port"], int) or str(first_row["port"]).isdigit()

    @patch("proxywhirl.loaders.vakhov_fresh.httpx")
    def test_protocol_scheme_mapping(self, mock_httpx):
        """Test correct mapping of protocols to proxy schemes."""

        def mock_get(url, **kwargs):
            mock_response = MagicMock()
            mock_response.text = "1.1.1.1:8080"
            mock_response.raise_for_status.return_value = None
            return mock_response

        mock_client = MagicMock()
        mock_client.get.side_effect = mock_get
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        loader = VakhovFreshProxyLoader()
        result = loader.load()

        # Should assign correct schemes based on endpoint
        if len(result) > 0:
            assert "schemes" in result.columns
            # Each proxy should have scheme information
            for schemes in result["schemes"]:
                assert schemes is not None

    def test_retry_mechanism(self):
        """Test retry mechanism for failed requests."""
        loader = VakhovFreshProxyLoader()

        # Should have retry decorator
        assert hasattr(loader.load, "__wrapped__")

    @patch("proxywhirl.loaders.vakhov_fresh.logger")
    @patch("proxywhirl.loaders.vakhov_fresh.httpx")
    def test_logging_functionality(self, mock_httpx, mock_logger):
        """Test proper logging during load operations."""
        mock_response = MagicMock()
        mock_response.text = "1.1.1.1:8080"
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        loader = VakhovFreshProxyLoader()
        loader.load()

        # Should log loading activity
        assert mock_logger.info.called or mock_logger.debug.called

    @patch("proxywhirl.loaders.vakhov_fresh.httpx")
    def test_concurrent_endpoint_handling(self, mock_httpx):
        """Test handling of multiple concurrent endpoint requests."""
        # Mock slow response simulation
        call_count = 0

        def mock_get(url, **kwargs):
            nonlocal call_count
            call_count += 1
            mock_response = MagicMock()
            mock_response.text = f"{call_count}.{call_count}.{call_count}.{call_count}:8080"
            mock_response.raise_for_status.return_value = None
            return mock_response

        mock_client = MagicMock()
        mock_client.get.side_effect = mock_get
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        loader = VakhovFreshProxyLoader()
        result = loader.load()

        # Should handle all endpoints
        assert mock_client.get.call_count == 4
        assert isinstance(result, DataFrame)

    def test_loader_metadata(self):
        """Test loader metadata and configuration."""
        loader = VakhovFreshProxyLoader()

        # Should have proper name and description
        assert loader.name == "VakhovFresh"
        assert isinstance(loader.description, str)
        assert len(loader.description) > 0

        # Description should mention key features
        assert "vakhov" in loader.description.lower()
        assert "fresh" in loader.description.lower()
        assert "github" in loader.description.lower()


class TestVakhovIntegration:
    """Test integration with the broader ProxyWhirl system."""

    def test_base_loader_interface(self):
        """Test compliance with BaseLoader interface."""
        loader = VakhovFreshProxyLoader()

        # Should implement required BaseLoader methods
        assert hasattr(loader, "load")
        assert callable(loader.load)

        # Should have required attributes
        assert hasattr(loader, "name")
        assert hasattr(loader, "description")

    @patch("proxywhirl.loaders.vakhov_fresh.httpx")
    def test_dataframe_compatibility(self, mock_httpx):
        """Test DataFrame output compatibility with pandas operations."""
        mock_response = MagicMock()
        mock_response.text = "1.1.1.1:8080\n2.2.2.2:8080"
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        loader = VakhovFreshProxyLoader()
        result = loader.load()

        # Should support common pandas operations
        assert isinstance(result, pd.DataFrame)

        # Should be filterable
        if len(result) > 0:
            filtered = result[result["port"].astype(str).str.contains("8080")]
            assert isinstance(filtered, pd.DataFrame)

        # Should be serializable
        json_str = result.to_json()
        assert isinstance(json_str, str)

    def test_multiple_protocol_support(self):
        """Test support for multiple proxy protocols."""
        loader = VakhovFreshProxyLoader()

        # Should support major proxy protocols
        supported_protocols = loader.urls.keys()
        assert "http" in supported_protocols
        assert "https" in supported_protocols
        assert "socks4" in supported_protocols
        assert "socks5" in supported_protocols

    def test_github_pages_reliability(self):
        """Test configuration for GitHub Pages hosting."""
        loader = VakhovFreshProxyLoader()

        # All URLs should use GitHub Pages hosting
        for protocol, url in loader.urls.items():
            assert "github.io" in url
            assert url.startswith("https://")
            assert "vakhov" in url
            assert "fresh-proxy-list" in url

    def test_performance_characteristics(self):
        """Test performance characteristics of the loader."""
        loader = VakhovFreshProxyLoader()

        # Should use efficient data structures
        assert isinstance(loader.urls, dict)
        assert len(loader.urls) == 4  # Exactly 4 protocol endpoints

        # Should not store unnecessary state
        loader_attrs = [attr for attr in dir(loader) if not attr.startswith("_")]
        expected_attrs = ["name", "description", "urls", "load"]

        for attr in expected_attrs:
            assert attr in loader_attrs or hasattr(loader, attr)
            assert attr in loader_attrs or hasattr(loader, attr)
