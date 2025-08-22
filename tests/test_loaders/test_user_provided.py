"""Tests for proxywhirl.loaders.user_provided module.

Unit tests for the UserProvidedLoader class with comprehensive coverage.
"""

from typing import Dict, List, Union

from pandas import DataFrame

from proxywhirl.loaders.user_provided import UserProvidedLoader


class TestUserProvidedLoader:
    """Test UserProvidedLoader with comprehensive coverage."""

    def test_loader_initialization_with_proxy_dicts(self):
        """Test loader initializes with proxy dictionaries."""
        proxy_dicts: List[Dict[str, Union[str, int]]] = [
            {"host": "192.168.1.1", "port": 8080, "protocol": "http"},
            {"host": "10.0.0.1", "port": 3128, "protocol": "http"},
        ]
        loader = UserProvidedLoader(proxies=proxy_dicts)
        assert loader.name == "user"
        assert "user-provided" in loader.description.lower()

    def test_loader_initialization_with_custom_name(self):
        """Test loader initializes with custom name."""
        proxy_dicts: List[Dict[str, Union[str, int]]] = [
            {"host": "192.168.1.1", "port": 8080, "protocol": "http"}
        ]
        custom_name = "my_custom_loader"
        loader = UserProvidedLoader(proxies=proxy_dicts, name=custom_name)
        assert loader.name == custom_name
        assert "user-provided" in loader.description.lower()

    def test_load_from_proxy_dicts(self):
        """Test loading from provided proxy dictionaries."""
        proxy_dicts: List[Dict[str, Union[str, int]]] = [
            {"host": "192.168.1.1", "port": 8080, "protocol": "http"},
            {"host": "10.0.0.1", "port": 3128, "protocol": "http"},
            {"host": "172.16.0.1", "port": 1080, "protocol": "socks5"},
        ]
        loader = UserProvidedLoader(proxies=proxy_dicts)
        df = loader.load()

        # Verify the result
        assert isinstance(df, DataFrame)
        assert len(df) == 3

        # Check that data is preserved
        assert "host" in df.columns
        assert "port" in df.columns
        assert "protocol" in df.columns

        # Check specific proxy data
        hosts = set(df["host"].tolist())
        ports = set(df["port"].tolist())
        protocols = set(df["protocol"].tolist())

        assert hosts == {"192.168.1.1", "10.0.0.1", "172.16.0.1"}
        assert ports == {8080, 3128, 1080}
        assert protocols == {"http", "socks5"}

    def test_load_with_minimal_proxy_dicts(self):
        """Test loading with minimal proxy dictionaries."""
        proxy_dicts: List[Dict[str, Union[str, int]]] = [
            {"host": "192.168.1.1", "port": 8080},
            {"host": "10.0.0.1", "port": 3128},
        ]
        loader = UserProvidedLoader(proxies=proxy_dicts)
        df = loader.load()

        # Verify the result
        assert isinstance(df, DataFrame)
        assert len(df) == 2
        assert "host" in df.columns
        assert "port" in df.columns

    def test_load_with_extra_fields(self):
        """Test loading with additional fields beyond host/port/protocol."""
        proxy_dicts: List[Dict[str, Union[str, int]]] = [
            {
                "host": "192.168.1.1",
                "port": 8080,
                "protocol": "http",
                "country": "US",
                "speed": "fast",
                "anonymity": "high",
            },
            {
                "host": "10.0.0.1",
                "port": 3128,
                "protocol": "http",
                "country": "UK",
                "speed": "medium",
            },
        ]
        loader = UserProvidedLoader(proxies=proxy_dicts)
        df = loader.load()

        # Verify the result includes extra fields
        assert isinstance(df, DataFrame)
        assert len(df) == 2
        assert "host" in df.columns
        assert "port" in df.columns
        assert "protocol" in df.columns
        assert "country" in df.columns
        assert "speed" in df.columns

    def test_load_with_empty_proxy_list(self):
        """Test loading with empty proxy list."""
        loader = UserProvidedLoader(proxies=[])
        df = loader.load()

        assert isinstance(df, DataFrame)
        assert len(df) == 0

    def test_load_with_inconsistent_fields(self):
        """Test loading with inconsistent field names across proxies."""
        proxy_dicts = [
            {"host": "192.168.1.1", "port": 8080, "protocol": "http"},
            {"ip": "10.0.0.1", "port_num": 3128, "type": "http"},
            {"host": "172.16.0.1", "port": 1080},
        ]
        loader = UserProvidedLoader(proxies=proxy_dicts)
        df = loader.load()

        # Should handle inconsistent fields gracefully
        assert isinstance(df, DataFrame)
        assert len(df) == 3

    def test_load_with_mixed_data_types(self):
        """Test loading with mixed data types."""
        proxy_dicts = [
            {"host": "192.168.1.1", "port": 8080, "protocol": "http"},
            {"host": "10.0.0.1", "port": "3128", "protocol": "http"},
            {"host": "172.16.0.1", "port": 1080, "protocol": "socks5"},
        ]
        loader = UserProvidedLoader(proxies=proxy_dicts)
        df = loader.load()

        # Should handle mixed types
        assert isinstance(df, DataFrame)
        assert len(df) == 3

    def test_load_with_none_values(self):
        """Test loading with None values."""
        proxy_dicts = [
            {"host": "192.168.1.1", "port": 8080, "protocol": "http"},
            {"host": "10.0.0.1", "port": None, "protocol": "http"},
            {"host": None, "port": 3128, "protocol": "http"},
        ]
        loader = UserProvidedLoader(proxies=proxy_dicts)
        df = loader.load()

        # Should handle None values
        assert isinstance(df, DataFrame)
        assert len(df) == 3

    def test_load_with_nested_data(self):
        """Test loading with nested data structures."""
        proxy_dicts = [
            {
                "host": "192.168.1.1",
                "port": 8080,
                "protocol": "http",
                "metadata": {"country": "US", "city": "New York"},
            },
            {
                "host": "10.0.0.1",
                "port": 3128,
                "protocol": "http",
                "metadata": {"country": "UK", "city": "London"},
            },
        ]
        loader = UserProvidedLoader(proxies=proxy_dicts)
        df = loader.load()

        # Should handle nested structures
        assert isinstance(df, DataFrame)
        assert len(df) == 2
        assert "metadata" in df.columns

    def test_load_with_large_proxy_list(self):
        """Test loading with large proxy list."""
        # Generate a large proxy list
        proxy_dicts = []
        for i in range(1000):
            proxy_dicts.append(
                {
                    "host": f"192.168.{i // 256}.{i % 256}",
                    "port": 8080 + (i % 100),
                    "protocol": "http",
                }
            )

        loader = UserProvidedLoader(proxies=proxy_dicts)
        df = loader.load()

        # Should handle large datasets efficiently
        assert isinstance(df, DataFrame)
        assert len(df) == 1000
        assert "host" in df.columns
        assert "port" in df.columns
        assert "protocol" in df.columns

    def test_load_with_duplicate_proxies(self):
        """Test loading handles duplicate proxies."""
        proxy_dicts = [
            {"host": "192.168.1.1", "port": 8080, "protocol": "http"},
            {"host": "10.0.0.1", "port": 3128, "protocol": "http"},
            {"host": "192.168.1.1", "port": 8080, "protocol": "http"},
            {"host": "172.16.0.1", "port": 1080, "protocol": "socks5"},
            {"host": "10.0.0.1", "port": 3128, "protocol": "http"},
        ]
        loader = UserProvidedLoader(proxies=proxy_dicts)
        df = loader.load()

        # Should preserve duplicates (deduplication happens downstream)
        assert isinstance(df, DataFrame)
        assert len(df) == 5

    def test_load_with_generator_input(self):
        """Test loading with generator as input."""

        def proxy_generator():
            for i in range(3):
                yield {
                    "host": f"192.168.1.{i + 1}",
                    "port": 8080 + i,
                    "protocol": "http",
                }

        loader = UserProvidedLoader(proxies=proxy_generator())
        df = loader.load()

        # Should handle generators
        assert isinstance(df, DataFrame)
        assert len(df) == 3

    def test_load_edge_cases(self):
        """Test edge cases and boundary conditions."""
        proxy_dicts = [{"host": "192.168.1.1", "port": 8080}]
        loader = UserProvidedLoader(proxies=proxy_dicts)

        # Test that loader has required attributes
        assert hasattr(loader, "name")
        assert hasattr(loader, "description")
        assert hasattr(loader, "load")

        # Test string representations
        assert str(loader) == loader.name
        assert loader.name in repr(loader)

    def test_initialization_with_various_iterables(self):
        """Test initialization with different iterable types."""
        proxy_dict = {"host": "192.168.1.1", "port": 8080, "protocol": "http"}

        # Test with list
        loader1 = UserProvidedLoader(proxies=[proxy_dict])
        assert len(loader1._proxies) == 1

        # Test with tuple
        loader2 = UserProvidedLoader(proxies=(proxy_dict,))
        assert len(loader2._proxies) == 1

        # Test with set (order may vary)
        loader3 = UserProvidedLoader(proxies={proxy_dict})
        assert len(loader3._proxies) == 1
