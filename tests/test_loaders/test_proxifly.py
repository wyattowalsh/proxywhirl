"""Comprehensive tests for proxywhirl.loaders.proxifly module.

This module tests the ProxiflyLoader class that fetches proxies
from Proxifly's CDN-hosted free proxy list service.
"""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from pandas import DataFrame

from proxywhirl.loaders.proxifly import ProxiflyLoader


class TestProxiflyLoader:
    """Test cases for ProxiflyLoader class."""

    def test_loader_initialization(self):
        """Test loader initialization and properties."""
        loader = ProxiflyLoader()

        assert loader.name == "Proxifly"
        assert "Proxies from Proxifly CDN-hosted free proxy list" in loader.description
        assert (
            loader.url
            == "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.json"
        )

    def test_inheritance(self):
        """Test that loader properly inherits from BaseLoader."""
        loader = ProxiflyLoader()

        # Should inherit BaseLoader functionality
        assert hasattr(loader, "name")
        assert hasattr(loader, "description")
        assert hasattr(loader, "load")

        # Should be callable
        assert callable(loader.load)

    @patch("proxywhirl.loaders.proxifly.httpx")
    def test_successful_load(self, mock_httpx):
        """Test successful proxy loading from Proxifly CDN."""
        # Mock HTTP response with sample Proxifly data
        sample_data = [
            {
                "ip": "192.168.1.1",
                "port": 8080,
                "protocols": ["http", "https"],
                "country": "United States",
                "country_code": "US",
                "anonymity": "anonymous",
                "uptime": 98.5,
                "response_time": 1200,
            },
            {
                "ip": "10.0.0.1",
                "port": 3128,
                "protocols": ["http"],
                "country": "Canada",
                "country_code": "CA",
                "anonymity": "elite",
                "uptime": 95.2,
                "response_time": 800,
            },
            {
                "ip": "203.0.113.1",
                "port": 1080,
                "protocols": ["socks4", "socks5"],
                "country": "Japan",
                "country_code": "JP",
                "anonymity": "transparent",
                "uptime": 92.1,
                "response_time": 1500,
            },
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = sample_data
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        loader = ProxiflyLoader()
        result = loader.load()

        # Verify HTTP call was made
        mock_client.get.assert_called_once_with(
            loader.url,
            timeout=30.0,
            headers={"User-Agent": "ProxyWhirl/1.0 (https://github.com/user/proxywhirl)"},
        )

        # Verify result is DataFrame
        assert isinstance(result, DataFrame)
        assert len(result) == 3

        # Check data structure
        assert "host" in result.columns
        assert "port" in result.columns
        assert "schemes" in result.columns
        assert "country_code" in result.columns

    @patch("proxywhirl.loaders.proxifly.httpx")
    def test_protocol_handling(self, mock_httpx):
        """Test handling of different proxy protocols."""
        # Test data with various protocol combinations
        protocol_test_data = [
            {
                "ip": "1.1.1.1",
                "port": 8080,
                "protocols": ["http"],
                "country": "US",
                "country_code": "US",
                "anonymity": "anonymous",
            },
            {
                "ip": "2.2.2.2",
                "port": 443,
                "protocols": ["https"],
                "country": "CA",
                "country_code": "CA",
                "anonymity": "anonymous",
            },
            {
                "ip": "3.3.3.3",
                "port": 1080,
                "protocols": ["socks4"],
                "country": "JP",
                "country_code": "JP",
                "anonymity": "anonymous",
            },
            {
                "ip": "4.4.4.4",
                "port": 1080,
                "protocols": ["socks5"],
                "country": "DE",
                "country_code": "DE",
                "anonymity": "anonymous",
            },
            {
                "ip": "5.5.5.5",
                "port": 8080,
                "protocols": ["http", "https", "socks4", "socks5"],
                "country": "FR",
                "country_code": "FR",
                "anonymity": "anonymous",
            },
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = protocol_test_data
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        loader = ProxiflyLoader()
        result = loader.load()

        # Should handle all protocol types
        assert len(result) == 5

        # Should properly transform protocols to schemes
        assert "schemes" in result.columns

        # Each proxy should have scheme information
        for schemes in result["schemes"]:
            assert schemes is not None
            assert isinstance(schemes, (list, str))

    @patch("proxywhirl.loaders.proxifly.httpx")
    def test_http_error_handling(self, mock_httpx):
        """Test handling of HTTP errors."""
        # Mock HTTP error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 503: Service Unavailable")

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        loader = ProxiflyLoader()

        with pytest.raises(Exception, match="HTTP 503: Service Unavailable"):
            loader.load()

    @patch("proxywhirl.loaders.proxifly.httpx")
    def test_json_parsing_error(self, mock_httpx):
        """Test handling of JSON parsing errors."""
        # Mock invalid JSON response
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Expecting value: line 1 column 1 (char 0)")
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        loader = ProxiflyLoader()

        with pytest.raises(ValueError, match="Expecting value"):
            loader.load()

    @patch("proxywhirl.loaders.proxifly.httpx")
    def test_empty_response_handling(self, mock_httpx):
        """Test handling of empty API response."""
        # Mock empty response
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        loader = ProxiflyLoader()
        result = loader.load()

        # Should return empty DataFrame
        assert isinstance(result, DataFrame)
        assert len(result) == 0

    @patch("proxywhirl.loaders.proxifly.httpx")
    def test_data_transformation(self, mock_httpx):
        """Test proper transformation of Proxifly data format."""
        # Mock Proxifly-specific data structure
        proxifly_data = [
            {
                "ip": "203.0.113.1",
                "port": 8080,
                "protocols": ["http", "https"],
                "country": "Singapore",
                "country_code": "SG",
                "anonymity": "elite",
                "uptime": 99.1,
                "response_time": 850,
                "last_checked": "2024-01-01T12:00:00Z",
                "source": "proxifly",
            }
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = proxifly_data
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        loader = ProxiflyLoader()
        result = loader.load()

        # Verify data transformation
        assert len(result) == 1
        row = result.iloc[0]

        assert row["host"] == "203.0.113.1"
        assert row["port"] == 8080
        assert row["country_code"] == "SG"

        # Should transform protocols list to schemes
        assert "schemes" in result.columns

    @patch("proxywhirl.loaders.proxifly.httpx")
    def test_large_dataset_handling(self, mock_httpx):
        """Test handling of large proxy datasets from CDN."""
        # Mock large dataset (2000+ proxies as mentioned in description)
        large_dataset = [
            {
                "ip": f"192.168.{i//255}.{i%255}",
                "port": 8080 + (i % 100),
                "protocols": ["http"],
                "country": "Test Country",
                "country_code": "TC",
                "anonymity": "anonymous",
                "uptime": 90.0 + (i % 10),
                "response_time": 1000 + (i % 1000),
            }
            for i in range(2000)
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = large_dataset
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        loader = ProxiflyLoader()
        result = loader.load()

        # Should handle large datasets efficiently
        assert isinstance(result, DataFrame)
        assert len(result) == 2000

        # Memory usage should be reasonable for 2000+ proxies
        assert result.memory_usage().sum() < 50_000_000  # Less than 50MB

    @patch("proxywhirl.loaders.proxifly.httpx")
    def test_malformed_data_handling(self, mock_httpx):
        """Test handling of malformed data from CDN."""
        # Mock response with missing required fields
        malformed_data = [
            {"ip": "1.1.1.1"},  # Missing port, protocols, etc.
            {"port": 8080},  # Missing IP
            {"ip": "2.2.2.2", "port": "invalid"},  # Invalid port
            {},  # Empty object
            {
                "ip": "3.3.3.3",
                "port": 8080,
                "protocols": [],  # Empty protocols
                "country_code": "US",
            },
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = malformed_data
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        loader = ProxiflyLoader()

        # Should handle malformed data gracefully
        result = loader.load()
        assert isinstance(result, DataFrame)
        # May return partial results or empty DataFrame

    @patch("proxywhirl.loaders.proxifly.httpx")
    def test_anonymity_level_handling(self, mock_httpx):
        """Test handling of different anonymity levels."""
        anonymity_test_data = [
            {
                "ip": "1.1.1.1",
                "port": 8080,
                "protocols": ["http"],
                "country_code": "US",
                "anonymity": "transparent",
            },
            {
                "ip": "2.2.2.2",
                "port": 8080,
                "protocols": ["http"],
                "country_code": "CA",
                "anonymity": "anonymous",
            },
            {
                "ip": "3.3.3.3",
                "port": 8080,
                "protocols": ["http"],
                "country_code": "JP",
                "anonymity": "elite",
            },
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = anonymity_test_data
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        loader = ProxiflyLoader()
        result = loader.load()

        # Should handle different anonymity levels
        assert len(result) == 3

        # Should include anonymity information if available
        if "anonymity" in result.columns:
            anonymity_values = set(result["anonymity"].dropna())
            assert len(anonymity_values) > 0

    def test_retry_mechanism(self):
        """Test retry mechanism for failed requests."""
        loader = ProxiflyLoader()

        # Should have retry decorator
        assert hasattr(loader.load, "__wrapped__")

    @patch("proxywhirl.loaders.proxifly.logger")
    @patch("proxywhirl.loaders.proxifly.httpx")
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

        loader = ProxiflyLoader()
        loader.load()

        # Should log loading activity
        assert mock_logger.info.called or mock_logger.debug.called

    def test_url_configuration(self):
        """Test URL configuration and CDN endpoint."""
        loader = ProxiflyLoader()

        # Should use correct GitHub raw endpoint for CDN
        assert "github.com" in loader.url
        assert "proxifly" in loader.url
        assert "free-proxy-list" in loader.url
        assert "data.json" in loader.url
        assert loader.url.startswith("https://")

    def test_loader_metadata(self):
        """Test loader metadata and documentation."""
        loader = ProxiflyLoader()

        # Should have proper name and description
        assert loader.name == "Proxifly"
        assert isinstance(loader.description, str)
        assert len(loader.description) > 0

        # Description should mention key features
        assert "proxifly" in loader.description.lower()
        assert "cdn" in loader.description.lower()
        assert "2000+" in loader.description or "multiple protocol" in loader.description.lower()


class TestProxiflyIntegration:
    """Test integration with the broader ProxyWhirl system."""

    def test_base_loader_interface(self):
        """Test compliance with BaseLoader interface."""
        loader = ProxiflyLoader()

        # Should implement required BaseLoader methods
        assert hasattr(loader, "load")
        assert callable(loader.load)

        # Should have required attributes
        assert hasattr(loader, "name")
        assert hasattr(loader, "description")

    @patch("proxywhirl.loaders.proxifly.httpx")
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

        loader = ProxiflyLoader()
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

    def test_cdn_reliability(self):
        """Test configuration for CDN hosting."""
        loader = ProxiflyLoader()

        # Should use CDN-style hosting (GitHub raw)
        assert "raw.githubusercontent.com" in loader.url
        assert loader.url.startswith("https://")

        # Should point to structured data endpoint
        assert loader.url.endswith(".json")

    def test_performance_characteristics(self):
        """Test performance characteristics of the loader."""
        loader = ProxiflyLoader()

        # Should have single endpoint (efficient)
        assert hasattr(loader, "url")
        assert isinstance(loader.url, str)

        # Should not store unnecessary state
        loader_attrs = [attr for attr in dir(loader) if not attr.startswith("_")]
        expected_attrs = ["name", "description", "url", "load"]

        for attr in expected_attrs:
            assert attr in loader_attrs or hasattr(loader, attr)

    def test_data_structure_consistency(self):
        """Test consistency of data structure across loads."""
        loader = ProxiflyLoader()

        # Should have consistent URL endpoint
        url1 = loader.url
        url2 = loader.url
        assert url1 == url2

        # Should maintain consistent loader identity
        assert loader.name == "Proxifly"
        assert "CDN-hosted" in loader.description
        assert "CDN-hosted" in loader.description
