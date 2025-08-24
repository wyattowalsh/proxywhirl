"""Comprehensive tests for proxywhirl.loaders.jetkai_proxy_list module.

This module tests the JetkaiProxyListLoader class that fetches proxies
from Jetkai's tested proxy list on GitHub.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
import pytest
from pandas import DataFrame

from proxywhirl.loaders.jetkai_proxy_list import JetkaiProxyListLoader


class TestJetkaiProxyListLoader:
    """Test cases for JetkaiProxyListLoader class."""

    def test_loader_initialization(self):
        """Test loader initialization and properties."""
        loader = JetkaiProxyListLoader()

        assert loader.name == "JetkaiProxyList"
        assert "Tested proxies from Jetkai proxy list" in loader.description
        assert "hourly updates" in loader.description
        assert (
            loader.url
            == "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/json/proxies.json"
        )

    def test_inheritance(self):
        """Test that loader properly inherits from BaseLoader."""
        loader = JetkaiProxyListLoader()

        # Should inherit BaseLoader functionality
        assert hasattr(loader, "name")
        assert hasattr(loader, "description")
        assert hasattr(loader, "load")

        # Should be callable
        assert callable(loader.load)

    @patch("proxywhirl.loaders.jetkai_proxy_list.httpx")
    def test_successful_load(self, mock_httpx):
        """Test successful proxy loading from Jetkai API."""
        # Mock HTTP response with sample Jetkai data
        sample_data = [
            {
                "ip": "192.168.1.1",
                "port": 8080,
                "protocols": ["http", "https"],
                "country": "United States",
                "country_code": "US",
                "anonymity": "anonymous",
                "timeout": 1500,
            },
            {
                "ip": "10.0.0.1",
                "port": 3128,
                "protocols": ["http"],
                "country": "Canada",
                "country_code": "CA",
                "anonymity": "elite",
                "timeout": 2000,
            },
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = sample_data
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        loader = JetkaiProxyListLoader()
        result = loader.load()

        # Verify HTTP call was made
        mock_client.get.assert_called_once_with(
            loader.url,
            timeout=30.0,
            headers={"User-Agent": "ProxyWhirl/1.0 (https://github.com/user/proxywhirl)"},
        )

        # Verify result is DataFrame
        assert isinstance(result, DataFrame)
        assert len(result) == 2

        # Check data structure
        assert "host" in result.columns
        assert "port" in result.columns
        assert "schemes" in result.columns
        assert "country_code" in result.columns

    @patch("proxywhirl.loaders.jetkai_proxy_list.httpx")
    def test_http_error_handling(self, mock_httpx):
        """Test handling of HTTP errors."""
        # Mock HTTP error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 404: Not Found")

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        loader = JetkaiProxyListLoader()

        with pytest.raises(Exception, match="HTTP 404: Not Found"):
            loader.load()

    @patch("proxywhirl.loaders.jetkai_proxy_list.httpx")
    def test_json_parsing_error(self, mock_httpx):
        """Test handling of JSON parsing errors."""
        # Mock invalid JSON response
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        loader = JetkaiProxyListLoader()

        with pytest.raises(ValueError, match="Invalid JSON"):
            loader.load()

    @patch("proxywhirl.loaders.jetkai_proxy_list.httpx")
    def test_empty_response_handling(self, mock_httpx):
        """Test handling of empty API response."""
        # Mock empty response
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        loader = JetkaiProxyListLoader()
        result = loader.load()

        # Should return empty DataFrame
        assert isinstance(result, DataFrame)
        assert len(result) == 0

    @patch("proxywhirl.loaders.jetkai_proxy_list.httpx")
    def test_data_transformation(self, mock_httpx):
        """Test proper transformation of Jetkai data format."""
        # Mock Jetkai-specific data structure
        jetkai_data = [
            {
                "ip": "203.0.113.1",
                "port": 8080,
                "protocols": ["http", "https"],
                "country": "Japan",
                "country_code": "JP",
                "anonymity": "anonymous",
                "timeout": 1200,
                "uptime": 98.5,
                "response_time": 0.8,
            }
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = jetkai_data
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        loader = JetkaiProxyListLoader()
        result = loader.load()

        # Verify data transformation
        assert len(result) == 1
        row = result.iloc[0]

        assert row["host"] == "203.0.113.1"
        assert row["port"] == 8080
        assert row["country_code"] == "JP"

        # Should transform protocols list to schemes
        assert "schemes" in result.columns

    @patch("proxywhirl.loaders.jetkai_proxy_list.httpx")
    def test_large_dataset_handling(self, mock_httpx):
        """Test handling of large proxy datasets."""
        # Mock large dataset (1000+ proxies)
        large_dataset = [
            {
                "ip": f"192.168.{i//255}.{i%255}",
                "port": 8080 + (i % 100),
                "protocols": ["http"],
                "country": "Test Country",
                "country_code": "TC",
                "anonymity": "anonymous",
                "timeout": 1500,
            }
            for i in range(1000)
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = large_dataset
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        loader = JetkaiProxyListLoader()
        result = loader.load()

        # Should handle large datasets efficiently
        assert isinstance(result, DataFrame)
        assert len(result) == 1000

        # Memory usage should be reasonable
        assert result.memory_usage().sum() < 10_000_000  # Less than 10MB

    @patch("proxywhirl.loaders.jetkai_proxy_list.logger")
    @patch("proxywhirl.loaders.jetkai_proxy_list.httpx")
    def test_logging_functionality(self, mock_httpx, mock_logger):
        """Test proper logging during load operations."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "ip": "1.1.1.1",
                "port": 8080,
                "protocols": ["http"],
                "country": "US",
                "country_code": "US",
                "anonymity": "anonymous",
            }
        ]
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        loader = JetkaiProxyListLoader()
        loader.load()

        # Should log loading activity
        assert mock_logger.info.called or mock_logger.debug.called

    def test_retry_mechanism(self):
        """Test retry mechanism for failed requests."""
        loader = JetkaiProxyListLoader()

        # Should have retry decorator
        assert hasattr(loader.load, "__wrapped__")

        # Test that load method has retry configuration
        # Note: Full retry testing would require more complex mocking
        # of the tenacity library behavior

    @patch("proxywhirl.loaders.jetkai_proxy_list.httpx")
    def test_malformed_data_handling(self, mock_httpx):
        """Test handling of malformed data from API."""
        # Mock response with missing required fields
        malformed_data = [
            {"ip": "1.1.1.1"},  # Missing port, protocols, etc.
            {"port": 8080},  # Missing IP
            {},  # Empty object
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = malformed_data
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        loader = JetkaiProxyListLoader()

        # Should handle malformed data gracefully
        # (may return partial data or raise specific errors)
        result = loader.load()
        assert isinstance(result, DataFrame)

    def test_url_configuration(self):
        """Test URL configuration and endpoint."""
        loader = JetkaiProxyListLoader()

        # Should use correct GitHub raw endpoint
        assert "github.com" in loader.url
        assert "jetkai" in loader.url
        assert "proxy-list" in loader.url
        assert "proxies.json" in loader.url
        assert loader.url.startswith("https://")

    def test_loader_metadata(self):
        """Test loader metadata and documentation."""
        loader = JetkaiProxyListLoader()

        # Should have proper name and description
        assert loader.name
        assert loader.description
        assert isinstance(loader.name, str)
        assert isinstance(loader.description, str)

        # Description should mention key features
        assert "tested" in loader.description.lower()
        assert "verified" in loader.description.lower() or "working" in loader.description.lower()
        assert "hourly" in loader.description.lower()


class TestJetkaiIntegration:
    """Test integration with the broader ProxyWhirl system."""

    def test_base_loader_interface(self):
        """Test compliance with BaseLoader interface."""
        loader = JetkaiProxyListLoader()

        # Should implement required BaseLoader methods
        assert hasattr(loader, "load")
        assert callable(loader.load)

        # Should have required attributes
        assert hasattr(loader, "name")
        assert hasattr(loader, "description")

    @patch("proxywhirl.loaders.jetkai_proxy_list.httpx")
    def test_dataframe_compatibility(self, mock_httpx):
        """Test DataFrame output compatibility with pandas operations."""
        # Mock valid response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "ip": "1.1.1.1",
                "port": 8080,
                "protocols": ["http"],
                "country": "US",
                "country_code": "US",
                "anonymity": "anonymous",
            }
        ]
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        loader = JetkaiProxyListLoader()
        result = loader.load()

        # Should support common pandas operations
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

        # Should be filterable
        if len(result) > 0:
            filtered = result[result["port"] == 8080]
            assert isinstance(filtered, pd.DataFrame)

        # Should be serializable
        json_str = result.to_json()
        assert isinstance(json_str, str)

    def test_performance_characteristics(self):
        """Test performance characteristics of the loader."""
        loader = JetkaiProxyListLoader()

        # Should have reasonable timeout configuration
        # (tested indirectly through HTTP client setup)

        # Should use efficient data structures
        assert hasattr(loader, "url")
        assert isinstance(loader.url, str)

        # Should not store unnecessary state
        loader_attrs = [attr for attr in dir(loader) if not attr.startswith("_")]
        expected_attrs = ["name", "description", "url", "load"]

        for attr in expected_attrs:
            assert attr in loader_attrs or hasattr(loader, attr)
            assert attr in loader_attrs or hasattr(loader, attr)
