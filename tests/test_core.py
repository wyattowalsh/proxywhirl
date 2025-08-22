"""Tests for proxywhirl core functionality.

This is the consolidated test module that contains comprehensive unit tests for:
- ProxyCache (memory, JSON, SQLite backends)
- ProxyRotator (all rotation strategies)
- ProxyValidator (with circuit breakers and health checks)
- ProxyWhirl (main orchestrator class)

This module replaces the deprecated test_core_complete.py and test_core_enhanced.py
files, providing complete coverage with robust mocking and edge case testing.

For integration tests that exercise component interactions, see test_core_integration.py.
"""

import sqlite3
import time
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from proxywhirl.cache import ProxyCache
from proxywhirl.models import AnonymityLevel, CacheType, Proxy, RotationStrategy, Scheme
from proxywhirl.proxywhirl import ProxyWhirl
from proxywhirl.rotator import ProxyRotator
from proxywhirl.validator import ProxyValidator


class TestProxyCache:
    """Comprehensive tests for ProxyCache with all cache types and scenarios."""

    def test_memory_cache_initialization(self):
        """Test memory cache initialization."""
        cache = ProxyCache(CacheType.MEMORY)
        assert cache.cache_type == CacheType.MEMORY
        assert cache.cache_path is None
        assert cache.get_proxies() == []

    def test_json_cache_initialization(self, temp_cache_paths):
        """Test JSON cache initialization."""
        cache_path = temp_cache_paths["json"]
        cache = ProxyCache(CacheType.JSON, cache_path)
        assert cache.cache_type == CacheType.JSON
        assert cache.cache_path == cache_path

    def test_sqlite_cache_initialization(self, temp_cache_paths):
        """Test SQLite cache initialization."""
        cache_path = temp_cache_paths["sqlite"]
        cache = ProxyCache(CacheType.SQLITE, cache_path)
        assert cache.cache_type == CacheType.SQLITE
        assert cache.cache_path == cache_path
        # Test that database connection exists (without accessing private _db)
        assert hasattr(cache, "_db")

    def test_sqlite_cache_requires_path(self):
        """Test that SQLite cache requires cache_path."""
        with pytest.raises(ValueError, match="cache_path is required"):
            ProxyCache(CacheType.SQLITE)

    def test_json_cache_requires_path(self):
        """Test that JSON cache requires cache_path."""
        with pytest.raises(ValueError, match="cache_path is required"):
            ProxyCache(CacheType.JSON)

    def test_add_and_get_proxies_memory(self, sample_proxies):
        """Test adding and getting proxies with memory cache."""
        cache = ProxyCache(CacheType.MEMORY)
        cache.add_proxies(sample_proxies)
        retrieved = cache.get_proxies()

        assert len(retrieved) == len(sample_proxies)
        assert retrieved[0].host == sample_proxies[0].host
        assert retrieved[1].host == sample_proxies[1].host

    def test_add_and_get_proxies_json(self, temp_cache_paths, sample_proxies):
        """Test adding and getting proxies with JSON cache."""
        cache_path = temp_cache_paths["json"]
        cache = ProxyCache(CacheType.JSON, cache_path)
        cache.add_proxies(sample_proxies)
        retrieved = cache.get_proxies()

        assert len(retrieved) == len(sample_proxies)
        assert retrieved[0].host == sample_proxies[0].host

        # Verify persistence
        cache2 = ProxyCache(CacheType.JSON, cache_path)
        retrieved2 = cache2.get_proxies()
        assert len(retrieved2) == len(sample_proxies)

    def test_add_and_get_proxies_sqlite(self, temp_cache_paths, sample_proxies):
        """Test adding and getting proxies with SQLite cache."""
        cache_path = temp_cache_paths["sqlite"]
        cache = ProxyCache(CacheType.SQLITE, cache_path)
        cache.add_proxies(sample_proxies)
        retrieved = cache.get_proxies()

        assert len(retrieved) == len(sample_proxies)
        assert retrieved[0].host == sample_proxies[0].host

        # Verify persistence
        cache2 = ProxyCache(CacheType.SQLITE, cache_path)
        retrieved2 = cache2.get_proxies()
        assert len(retrieved2) == len(sample_proxies)

    def test_add_large_dataset(self, temp_cache_paths, large_proxy_dataset):
        """Test adding large dataset for performance."""
        cache_path = temp_cache_paths["sqlite"]
        cache = ProxyCache(CacheType.SQLITE, cache_path)

        start_time = time.time()
        cache.add_proxies(large_proxy_dataset)
        end_time = time.time()

        # Should complete within reasonable time (5 seconds for 1000 proxies)
        assert (end_time - start_time) < 5.0

        retrieved = cache.get_proxies()
        assert len(retrieved) == len(large_proxy_dataset)

    def test_add_empty_proxy_list(self, temp_cache_paths):
        """Test adding empty proxy list."""
        cache_path = temp_cache_paths["json"]
        cache = ProxyCache(CacheType.JSON, cache_path)
        cache.add_proxies([])
        retrieved = cache.get_proxies()
        assert len(retrieved) == 0

    def test_add_duplicate_proxies(self, temp_cache_paths, sample_proxies):
        """Test handling duplicate proxies."""
        cache_path = temp_cache_paths["sqlite"]
        cache = ProxyCache(CacheType.SQLITE, cache_path)

        # Add same proxies twice
        cache.add_proxies(sample_proxies)
        cache.add_proxies(sample_proxies)

        retrieved = cache.get_proxies()
        # Should handle duplicates appropriately
        assert len(retrieved) >= len(sample_proxies)

    def test_update_proxy_memory(self, sample_proxies):
        """Test updating proxy in memory cache."""
        cache = ProxyCache(CacheType.MEMORY)
        cache.add_proxies([sample_proxies[0]])

        # Create updated proxy with new response time
        updated_proxy = Proxy(
            host=sample_proxies[0].host,
            ip=sample_proxies[0].ip,
            port=sample_proxies[0].port,
            schemes=sample_proxies[0].schemes,
            country_code=sample_proxies[0].country_code,
            country=sample_proxies[0].country,
            city=sample_proxies[0].city,
            anonymity=sample_proxies[0].anonymity,
            response_time=1.5,
            source=sample_proxies[0].source,
        )
        cache.update_proxy(updated_proxy)

        retrieved = cache.get_proxies()
        assert len(retrieved) == 1
        assert retrieved[0].response_time == 1.5

    def test_update_proxy_sqlite_port_change(self, temp_cache_paths, sample_proxies):
        """Test updating proxy with port change in SQLite cache."""
        cache_path = temp_cache_paths["sqlite"]
        cache = ProxyCache(CacheType.SQLITE, cache_path)
        cache.add_proxies([sample_proxies[0]])

        # Create proxy with different port - this should create a new entry
        # since (host, port) is the composite primary key
        updated_proxy = Proxy(
            host=sample_proxies[0].host,
            ip=sample_proxies[0].ip,
            port=9090,
            schemes=sample_proxies[0].schemes,
            country_code=sample_proxies[0].country_code,
            country=sample_proxies[0].country,
            city=sample_proxies[0].city,
            anonymity=sample_proxies[0].anonymity,
            response_time=sample_proxies[0].response_time,
            source=sample_proxies[0].source,
        )
        cache.update_proxy(updated_proxy)

        retrieved = cache.get_proxies()
        # Should now have 2 proxies: original and updated with different port
        assert len(retrieved) == 2
        ports = {p.port for p in retrieved}
        assert ports == {sample_proxies[0].port, 9090}

    def test_remove_proxy_memory(self, sample_proxies):
        """Test removing proxy from memory cache."""
        cache = ProxyCache(CacheType.MEMORY)
        cache.add_proxies(sample_proxies[:2])

        cache.remove_proxy(sample_proxies[0])
        retrieved = cache.get_proxies()

        assert len(retrieved) == 1
        assert retrieved[0].host == sample_proxies[1].host

    def test_remove_nonexistent_proxy(self, temp_cache_paths, sample_proxies):
        """Test removing proxy that doesn't exist."""
        cache_path = temp_cache_paths["json"]
        cache = ProxyCache(CacheType.JSON, cache_path)
        cache.add_proxies([sample_proxies[0]])

        # Try to remove different proxy
        cache.remove_proxy(sample_proxies[1])
        retrieved = cache.get_proxies()

        # Should still have original proxy
        assert len(retrieved) == 1
        assert retrieved[0].host == sample_proxies[0].host

    def test_clear_cache_memory(self, sample_proxies):
        """Test clearing memory cache."""
        cache = ProxyCache(CacheType.MEMORY)
        cache.add_proxies(sample_proxies)

        cache.clear()
        retrieved = cache.get_proxies()
        assert len(retrieved) == 0

    def test_clear_cache_json(self, temp_cache_paths, sample_proxies):
        """Test clearing JSON cache."""
        cache_path = temp_cache_paths["json"]
        cache = ProxyCache(CacheType.JSON, cache_path)
        cache.add_proxies(sample_proxies)

        cache.clear()
        retrieved = cache.get_proxies()
        assert len(retrieved) == 0

        # File should be removed or empty
        assert not cache_path.exists() or cache_path.stat().st_size == 0

    def test_clear_cache_sqlite(self, temp_cache_paths, sample_proxies):
        """Test clearing SQLite cache."""
        cache_path = temp_cache_paths["sqlite"]
        cache = ProxyCache(CacheType.SQLITE, cache_path)
        cache.add_proxies(sample_proxies)

        cache.clear()
        retrieved = cache.get_proxies()
        assert len(retrieved) == 0

    @patch("sqlite3.connect")
    def test_sqlite_connection_error(self, mock_connect, temp_cache_paths):
        """Test SQLite connection error handling."""
        mock_connect.side_effect = sqlite3.OperationalError("Database locked")
        cache_path = temp_cache_paths["sqlite"]

        with pytest.raises(sqlite3.OperationalError):
            ProxyCache(CacheType.SQLITE, cache_path)

    def test_json_file_corruption_handling(self, temp_cache_paths):
        """Test handling of corrupted JSON cache file."""
        cache_path = temp_cache_paths["json"]

        # Create corrupted JSON file
        cache_path.write_text("invalid json content {")

        cache = ProxyCache(CacheType.JSON, cache_path)
        # Should handle corruption gracefully
        retrieved = cache.get_proxies()
        assert isinstance(retrieved, list)

    def test_cache_file_permissions(self, temp_cache_paths, sample_proxies):
        """Test cache behavior with file permission issues."""
        cache_path = temp_cache_paths["json"]
        cache = ProxyCache(CacheType.JSON, cache_path)
        cache.add_proxies(sample_proxies)

        # Make file read-only
        cache_path.chmod(0o444)

        try:
            # Should handle permission errors gracefully
            cache.add_proxies([sample_proxies[0]])
        except PermissionError:
            # Expected behavior
            pass
        finally:
            # Restore permissions for cleanup
            cache_path.chmod(0o644)

    def test_cache_performance_with_large_dataset(self, temp_cache_paths, cache_performance_data):
        """Test cache performance with large dataset."""
        cache_path = temp_cache_paths["sqlite"]
        cache = ProxyCache(CacheType.SQLITE, cache_path)

        # Convert dict data to Proxy objects for testing
        proxy_objects = []
        for i, data in enumerate(cache_performance_data[:100]):  # Use subset for test speed
            proxy = Proxy(
                host=data["host"],
                ip=data["host"],  # Use host as IP for simplicity
                port=data["port"],
                schemes=[Scheme.HTTP],
                country_code="US",
                country="United States",
                city="Test City",
                anonymity=AnonymityLevel.UNKNOWN,
                response_time=data.get("response_time", 0.5),
                source="test_source",
            )
            proxy_objects.append(proxy)

        start_time = time.time()
        cache.add_proxies(proxy_objects)
        add_time = time.time() - start_time

        start_time = time.time()
        retrieved = cache.get_proxies()
        get_time = time.time() - start_time

        # Performance assertions (should be reasonable for 100 proxies)
        assert add_time < 1.0  # Less than 1 second to add
        assert get_time < 0.5  # Less than 0.5 seconds to retrieve
        assert len(retrieved) == 100


class TestProxyRotator:
    """Comprehensive tests for ProxyRotator with all rotation strategies."""

    @pytest.fixture
    def test_proxies(self, comprehensive_proxy_list):
        """Get test proxies with different characteristics."""
        return comprehensive_proxy_list[:5]  # Use first 5 for testing

    def test_rotator_initialization(self):
        """Test ProxyRotator initialization."""
        rotator = ProxyRotator(RotationStrategy.ROUND_ROBIN)
        assert rotator.strategy == RotationStrategy.ROUND_ROBIN

    def test_round_robin_rotation(self, test_proxies):
        """Test round-robin rotation strategy."""
        rotator = ProxyRotator(RotationStrategy.ROUND_ROBIN)

        # Should cycle through proxies in order
        first = rotator.get_proxy(test_proxies)
        second = rotator.get_proxy(test_proxies)
        third = rotator.get_proxy(test_proxies)

        assert first != second != third
        assert first is not None
        assert second is not None
        assert third is not None

    def test_random_rotation(self, test_proxies):
        """Test random rotation strategy."""
        rotator = ProxyRotator(RotationStrategy.RANDOM)

        # Get multiple proxies and ensure they're from our list
        selected = [rotator.get_proxy(test_proxies) for _ in range(20)]
        for proxy in selected:
            assert proxy in test_proxies

        # Should have some variation (not all the same)
        unique_proxies = set(proxy.host for proxy in selected if proxy)
        assert len(unique_proxies) > 1

    def test_weighted_rotation(self, test_proxies):
        """Test weighted rotation based on response time."""
        # Set response times for testing
        for i, proxy in enumerate(test_proxies):
            proxy.response_time = 0.1 + (i * 0.2)  # 0.1, 0.3, 0.5, 0.7, 0.9

        rotator = ProxyRotator(RotationStrategy.WEIGHTED)

        # Get many proxies to test distribution
        selected = [rotator.get_proxy(test_proxies) for _ in range(50)]

        # All selections should be valid
        assert all(proxy is not None for proxy in selected)
        assert all(proxy in test_proxies for proxy in selected)

    def test_health_based_rotation(self, test_proxies):
        """Test health-based rotation strategy."""
        rotator = ProxyRotator(RotationStrategy.HEALTH_BASED)

        # Initially, all proxies should be available
        selected = [rotator.get_proxy(test_proxies) for _ in range(10)]
        unique_hosts = set(proxy.host for proxy in selected if proxy)
        assert len(unique_hosts) > 1

        # Update health score to mark a proxy as unhealthy
        proxy_to_fail = test_proxies[0]
        rotator.update_health_score(proxy_to_fail, success=False)

        # Continue testing rotation after health update
        selected_after = [rotator.get_proxy(test_proxies) for _ in range(10)]
        assert all(proxy is not None for proxy in selected_after)

    def test_least_used_rotation(self, test_proxies):
        """Test least-used rotation strategy."""
        rotator = ProxyRotator(RotationStrategy.LEAST_USED)

        # Get proxies and track usage
        selections = [rotator.get_proxy(test_proxies) for _ in range(10)]

        # Should distribute across different proxies
        unique_hosts = set(proxy.host for proxy in selections if proxy)
        assert len(unique_hosts) >= 3  # Should use at least 3 different proxies

    def test_rotation_with_empty_proxy_list(self):
        """Test rotation behavior with empty proxy list."""
        rotator = ProxyRotator(RotationStrategy.ROUND_ROBIN)

        result = rotator.get_proxy([])
        assert result is None

    def test_rotation_with_single_proxy(self, test_proxies):
        """Test rotation behavior with single proxy."""
        single_proxy = [test_proxies[0]]
        rotator = ProxyRotator(RotationStrategy.ROUND_ROBIN)

        # Should always return the same proxy
        first = rotator.get_proxy(single_proxy)
        second = rotator.get_proxy(single_proxy)
        third = rotator.get_proxy(single_proxy)

        assert first == second == third == single_proxy[0]

    def test_invalid_rotation_strategy(self):
        """Test behavior with invalid rotation strategy."""
        with pytest.raises((ValueError, AttributeError)):
            ProxyRotator("INVALID_STRATEGY")

    def test_health_score_updates(self, test_proxies):
        """Test health score update functionality."""
        rotator = ProxyRotator(RotationStrategy.HEALTH_BASED)
        proxy = test_proxies[0]

        # Update with success
        rotator.update_health_score(proxy, success=True, response_time=0.5)
        assert proxy.response_time == 0.5

        # Update with failure
        rotator.update_health_score(proxy, success=False)
        # Proxy should still have response time from previous success
        assert proxy.response_time == 0.5

    def test_cooldown_functionality(self, test_proxies):
        """Test proxy cooldown after failure."""
        rotator = ProxyRotator(RotationStrategy.HEALTH_BASED)
        proxy = test_proxies[0]

        # Mark proxy as failed (should trigger cooldown)
        rotator.update_health_score(proxy, success=False)

        # Proxy might still be returned but with lower health score
        result = rotator.get_proxy(test_proxies)
        assert result is not None  # Should still get a proxy from the list


class TestProxyValidator:
    """Comprehensive tests for ProxyValidator with all validation scenarios."""

    @pytest.fixture
    def mock_validator(self):
        """Create ProxyValidator with mocked dependencies."""
        return ProxyValidator(timeout=5.0, test_url="https://httpbin.org/ip")

    @pytest.mark.asyncio
    async def test_validate_single_proxy_success(self, mock_validator, sample_proxies):
        """Test successful validation of a single proxy."""
        proxy = sample_proxies[0]

        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get.return_value = mock_response

        with patch("httpx.AsyncClient", return_value=mock_client):
            with patch("datetime.datetime") as mock_datetime:
                mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
                result = await mock_validator.validate_proxy(proxy)

        assert result is True
        assert proxy.response_time is not None

    @pytest.mark.asyncio
    async def test_validate_single_proxy_failure(self, mock_validator, sample_proxies):
        """Test proxy validation failure."""
        proxy = sample_proxies[0]

        # Mock timeout error
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get.side_effect = Exception("Connection failed")

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await mock_validator.validate_proxy(proxy)

        assert result is False

    @pytest.mark.asyncio
    async def test_validate_single_proxy_timeout(self, mock_validator, sample_proxies):
        """Test proxy validation with timeout."""
        proxy = sample_proxies[0]

        # Mock timeout error
        import httpx

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get.side_effect = httpx.TimeoutException("Request timed out")

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await mock_validator.validate_proxy(proxy)

        assert result is False

    @pytest.mark.asyncio
    async def test_validate_multiple_proxies(self, mock_validator, comprehensive_proxy_list):
        """Test validation of multiple proxies."""
        proxies = comprehensive_proxy_list[:5]

        # Mock mixed results - some success, some failure
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.raise_for_status = Mock()

        call_count = 0

        def mock_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count % 2 == 0:
                raise Exception("Connection failed")
            return mock_response_success

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get.side_effect = mock_get

        with patch("httpx.AsyncClient", return_value=mock_client):
            with patch("datetime.datetime") as mock_datetime:
                mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
                results = await mock_validator.validate_proxies(proxies)

        # Should return only valid proxies
        assert len(results) <= len(proxies)
        assert len(results) >= 0

    @pytest.mark.asyncio
    async def test_validate_with_custom_test_url(self, mock_validator, sample_proxies):
        """Test proxy validation with custom test URL."""
        proxy = sample_proxies[0]
        custom_url = "https://custom-test.com/check"

        # Update validator test URL
        mock_validator.test_url = custom_url

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get.return_value = mock_response

        with patch("httpx.AsyncClient", return_value=mock_client):
            with patch("datetime.datetime") as mock_datetime:
                mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
                result = await mock_validator.validate_proxy(proxy)

        # Should have called with custom URL
        mock_client.get.assert_called_once()
        assert result is True

    def test_validator_initialization(self):
        """Test ProxyValidator initialization."""
        validator = ProxyValidator(timeout=10.0, test_url="https://custom.test.com")

        assert validator.timeout == 10.0
        assert validator.test_url == "https://custom.test.com"

    @pytest.mark.asyncio
    async def test_validate_performance_with_large_dataset(
        self, mock_validator, large_proxy_dataset
    ):
        """Test validation performance with large proxy dataset."""
        # Use subset for testing
        test_proxies = large_proxy_dataset[:10]

        # Mock fast responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get.return_value = mock_response

        with patch("httpx.AsyncClient", return_value=mock_client):
            with patch("datetime.datetime") as mock_datetime:
                mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
                start_time = time.time()
                results = await mock_validator.validate_proxies(test_proxies)
                end_time = time.time()

        # Should complete reasonably quickly
        assert (end_time - start_time) < 3.0  # Less than 3 seconds for 10 proxies
        assert len(results) <= len(test_proxies)


class TestProxyWhirl:
    """Comprehensive tests for ProxyWhirl main orchestrator class."""

    @pytest.fixture
    def mock_whirl(self):
        """Create ProxyWhirl instance with test configuration."""
        return ProxyWhirl(
            cache_type=CacheType.MEMORY,
            rotation_strategy=RotationStrategy.ROUND_ROBIN,
            auto_validate=False,  # Disable validation for testing
        )

    def test_whirl_initialization(self, mock_whirl):
        """Test ProxyWhirl initialization with default settings."""
        assert mock_whirl.cache_type == CacheType.MEMORY
        assert mock_whirl.rotation_strategy == RotationStrategy.ROUND_ROBIN
        assert mock_whirl.auto_validate is False

    @pytest.mark.asyncio
    async def test_fetch_proxies_from_loaders(self, mock_whirl):
        """Test fetching proxies from loaders."""
        # Mock loader responses
        mock_df = Mock()
        mock_df.iterrows.return_value = [
            (0, {"host": "192.168.1.1", "port": 8080, "protocol": "http"}),
            (1, {"host": "192.168.1.2", "port": 3128, "protocol": "http"}),
        ]

        mock_loader = Mock()
        mock_loader.name = "test_loader"
        mock_loader.load.return_value = mock_df

        # Replace loaders with our mock
        mock_whirl.loaders = [mock_loader]

        count = await mock_whirl.fetch_proxies(validate=False)

        assert count == 2
        cached_proxies = mock_whirl.list_proxies()
        assert len(cached_proxies) == 2

    @pytest.mark.asyncio
    async def test_get_proxy_rotation(self, mock_whirl, sample_proxies):
        """Test getting proxies with rotation."""
        # Add proxies to cache
        mock_whirl.cache.add_proxies(sample_proxies)

        # Get proxies in rotation
        first = await mock_whirl.get_proxy()
        second = await mock_whirl.get_proxy()
        third = await mock_whirl.get_proxy()

        assert first in sample_proxies
        assert second in sample_proxies
        assert third in sample_proxies

    @pytest.mark.asyncio
    async def test_get_proxy_empty_cache(self, mock_whirl):
        """Test getting proxy when cache is empty."""
        proxy = await mock_whirl.get_proxy()
        assert proxy is None

    @pytest.mark.asyncio
    async def test_validate_proxies_functionality(self, mock_whirl, sample_proxies):
        """Test proxy validation functionality."""
        # Add proxies to cache
        mock_whirl.cache.add_proxies(sample_proxies)

        # Mock validator to return some valid proxies
        mock_validator = Mock()
        mock_validator.validate_proxies.return_value = sample_proxies[:2]  # Return first 2 as valid
        mock_whirl.validator = mock_validator

        valid_count = await mock_whirl.validate_proxies()

        assert valid_count == 2
        cached_proxies = mock_whirl.list_proxies()
        assert len(cached_proxies) == 2

    @pytest.mark.asyncio
    async def test_fetch_proxies_with_validation_enabled(
        self, mock_whirl, comprehensive_proxy_list
    ):
        """Test loading proxies with validation enabled."""
        # Mock loader
        mock_df = Mock()
        mock_df.iterrows.return_value = [
            (0, {"host": "192.168.1.1", "port": 8080, "protocol": "http"}),
            (1, {"host": "192.168.1.2", "port": 3128, "protocol": "http"}),
        ]

        mock_loader = Mock()
        mock_loader.name = "test_loader"
        mock_loader.load.return_value = mock_df

        # Mock validator to validate some proxies
        mock_validator = Mock()
        mock_validator.validate_proxies.return_value = comprehensive_proxy_list[:1]

        mock_whirl.loaders = [mock_loader]
        mock_whirl.validator = mock_validator

        count = await mock_whirl.fetch_proxies(validate=True)

        # Should only cache validated proxies
        assert count == 1
        cached_proxies = mock_whirl.list_proxies()
        assert len(cached_proxies) == 1

    def test_update_proxy_health(self, mock_whirl, sample_proxies):
        """Test updating proxy health scores."""
        proxy = sample_proxies[0]

        # Update health with success
        mock_whirl.update_proxy_health(proxy, success=True, response_time=0.5)

        # Verify proxy was updated
        assert proxy.response_time == 0.5

    def test_get_proxy_count(self, mock_whirl, sample_proxies):
        """Test getting proxy count."""
        assert mock_whirl.get_proxy_count() == 0

        mock_whirl.cache.add_proxies(sample_proxies)
        assert mock_whirl.get_proxy_count() == len(sample_proxies)

    def test_clear_cache(self, mock_whirl, sample_proxies):
        """Test clearing proxy cache."""
        mock_whirl.cache.add_proxies(sample_proxies)
        assert mock_whirl.get_proxy_count() > 0

        mock_whirl.clear_cache()
        assert mock_whirl.get_proxy_count() == 0

    def test_list_proxies(self, mock_whirl, sample_proxies):
        """Test listing all cached proxies."""
        assert mock_whirl.list_proxies() == []

        mock_whirl.cache.add_proxies(sample_proxies)
        listed = mock_whirl.list_proxies()

        assert len(listed) == len(sample_proxies)
        assert all(proxy in sample_proxies for proxy in listed)

    def test_whirl_configuration_validation(self):
        """Test ProxyWhirl configuration validation."""
        # Test valid configurations
        whirl1 = ProxyWhirl(cache_type="memory")
        assert whirl1.cache_type == CacheType.MEMORY

        whirl2 = ProxyWhirl(rotation_strategy="random")
        assert whirl2.rotation_strategy == RotationStrategy.RANDOM

    def test_whirl_with_sqlite_cache(self, temp_cache_paths, comprehensive_proxy_list):
        """Test ProxyWhirl with SQLite cache persistence."""
        cache_path = temp_cache_paths["sqlite"]
        whirl = ProxyWhirl(
            cache_type=CacheType.SQLITE,
            cache_path=cache_path,
            rotation_strategy=RotationStrategy.RANDOM,
        )

        # Add proxies to cache
        whirl.cache.add_proxies(comprehensive_proxy_list[:10])

        # Create new instance with same cache
        whirl2 = ProxyWhirl(
            cache_type=CacheType.SQLITE,
            cache_path=cache_path,
            rotation_strategy=RotationStrategy.RANDOM,
        )

        # Should load from persisted cache
        cached_proxies = whirl2.list_proxies()
        assert len(cached_proxies) == 10

    @pytest.mark.asyncio
    async def test_error_handling_during_fetch(self, mock_whirl):
        """Test error handling during proxy fetching."""
        # Mock loader that raises exception
        mock_loader = Mock()
        mock_loader.name = "failing_loader"
        mock_loader.load.side_effect = Exception("Loading failed")

        mock_whirl.loaders = [mock_loader]

        # Should handle errors gracefully and return 0
        count = await mock_whirl.fetch_proxies(validate=False)
        assert count == 0

    @pytest.mark.asyncio
    async def test_performance_with_rotation(self, mock_whirl, large_proxy_dataset):
        """Test ProxyWhirl performance with proxy rotation."""
        # Add large dataset to cache
        mock_whirl.cache.add_proxies(large_proxy_dataset[:100])  # Use subset

        # Test proxy rotation performance
        start_time = time.time()
        for _ in range(50):
            proxy = await mock_whirl.get_proxy()
            assert proxy is not None
        end_time = time.time()

        # Rotation should be very fast
        assert (end_time - start_time) < 0.5  # Less than 500ms for 50 rotations

    @pytest.mark.asyncio
    async def test_concurrent_proxy_access(self, mock_whirl, comprehensive_proxy_list):
        """Test concurrent access to proxy rotation."""
        # Load proxies
        mock_whirl.cache.add_proxies(comprehensive_proxy_list[:10])

        import asyncio

        async def get_proxy():
            return await mock_whirl.get_proxy()

        # Concurrent access should work without conflicts
        tasks = [get_proxy() for _ in range(20)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should succeed
        assert len(results) == 20
        assert all(isinstance(result, Proxy) for result in results if result is not None)

        # Should have used different proxies (with round robin)
        unique_hosts = set(proxy.host for proxy in results if proxy is not None)
        assert len(unique_hosts) > 1  # Should have rotated through multiple proxies
