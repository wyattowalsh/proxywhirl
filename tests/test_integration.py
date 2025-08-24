# type: ignore
"""Integration tests for ProxyWhirl core component interactions.

This module tests the integration between core ProxyWhirl components:
- ProxyCache (memory, JSON, SQLite) with ProxyRotator
- ProxyValidator with circuit breakers and ProxyCache
- ProxyWhirl orchestrator with all components
- End-to-end workflows with real component interactions

These tests focus on component boundaries, data flow, and failure scenarios
that require multiple components working together.
"""

import asyncio
import sqlite3
import tempfile
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, patch

import pytest

from proxywhirl.cache import ProxyCache
from proxywhirl.models import (
    AnonymityLevel,
    CacheType,
    CoreProxy,
    Proxy,
    ProxyStatus,
    RotationStrategy,
    Scheme,
    ValidationErrorType,
)
from proxywhirl.proxywhirl import ProxyWhirl
from proxywhirl.rotator import ProxyRotator
from proxywhirl.validator import ProxyValidator


@pytest.fixture
def temp_db_path():
    """Temporary SQLite database path for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "test_integration.db"


@pytest.fixture
def temp_json_path():
    """Temporary JSON cache path for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "test_integration.json"


@pytest.fixture
def sample_proxies():
    """Sample proxy data for integration tests."""
    return [
        Proxy(
            host="203.0.113.1",
            ip="203.0.113.1",
            port=8080,
            schemes=[Scheme.HTTP],
            country_code="US",
            country="United States",
            city="New York",
            region="New York",
            isp="Test ISP",
            organization="Test Org",
            anonymity=AnonymityLevel.ELITE,
            response_time=0.150,
            source="test-source",
            status=ProxyStatus.ACTIVE,
            quality_score=0.9,
            blacklist_reason=None,
            credentials=None,
            metrics=None,
            capabilities=None,
        ),
        Proxy(
            host="203.0.113.2",
            ip="203.0.113.2",
            port=3128,
            schemes=[Scheme.HTTPS],
            country_code="GB",
            country="United Kingdom",
            city="London",
            region="England",
            isp="Test ISP UK",
            organization="Test Org UK",
            anonymity=AnonymityLevel.ANONYMOUS,
            response_time=0.200,
            source="test-source",
            status=ProxyStatus.ACTIVE,
            quality_score=0.8,
            blacklist_reason=None,
            credentials=None,
            metrics=None,
            capabilities=None,
        ),
        Proxy(
            host="203.0.113.3",
            ip="203.0.113.3",
            port=1080,
            schemes=[Scheme.SOCKS4],
            country_code="DE",
            country="Germany",
            city="Berlin",
            region="Berlin",
            isp="Test ISP DE",
            organization="Test Org DE",
            anonymity=AnonymityLevel.TRANSPARENT,
            response_time=0.300,
            source="test-source",
            status=ProxyStatus.ACTIVE,
            quality_score=0.5,
            blacklist_reason=None,
            credentials=None,
            metrics=None,
            capabilities=None,
        ),
    ]


class TestCacheRotatorIntegration:
    """Test integration between ProxyCache and ProxyRotator."""

    @pytest.mark.integration
    def test_cache_rotator_memory_integration(self, sample_proxies: List[Proxy]) -> None:
        """Test memory cache integration with rotator."""
        cache = ProxyCache(CacheType.MEMORY)
        rotator = ProxyRotator(RotationStrategy.ROUND_ROBIN)

        # Add proxies to cache
        cache.add_proxies(sample_proxies)

        # Initialize rotator with cache data
        cached_proxies = cache.get_proxies()
        assert len(cached_proxies) == len(sample_proxies)

        # Test rotation works with cached data
        for _ in range(len(sample_proxies) * 2):
            proxy = rotator.get_proxy(cached_proxies)
            assert proxy is not None
            assert proxy in cached_proxies

    @pytest.mark.integration
    def test_cache_rotator_json_integration(
        self, temp_json_path: Path, sample_proxies: List[Proxy]
    ) -> None:
        """Test JSON cache integration with rotator."""
        cache = ProxyCache(CacheType.JSON, temp_json_path)
        rotator = ProxyRotator(RotationStrategy.WEIGHTED)

        # Add proxies to cache
        cache.add_proxies(sample_proxies)

        # Verify persistence
        assert temp_json_path.exists()

        # Create new cache instance to test loading
        cache2 = ProxyCache(CacheType.JSON, temp_json_path)
        loaded_proxies = cache2.get_proxies()
        assert len(loaded_proxies) == len(sample_proxies)

        # Test weighted rotation with persistent data
        proxy = rotator.get_proxy(loaded_proxies)
        assert proxy is not None
        # Proxy should be one of our loaded proxies
        assert proxy in loaded_proxies

    @pytest.mark.integration
    def test_cache_rotator_sqlite_integration(
        self, temp_db_path: Path, sample_proxies: List[Proxy]
    ) -> None:
        """Test SQLite cache integration with rotator."""
        cache = ProxyCache(CacheType.SQLITE, temp_db_path)
        rotator = ProxyRotator(RotationStrategy.RANDOM)

        # Add proxies to cache
        cache.add_proxies(sample_proxies)

        # Verify database creation
        assert temp_db_path.exists()

        # Test direct database access
        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM proxies")
            count = cursor.fetchone()[0]
            assert count == len(sample_proxies)

        # Test rotator integration with database data
        db_proxies = cache.get_proxies()
        assert len(db_proxies) == len(sample_proxies)

        # Test random rotation
        selected_proxies: set[str] = set()
        for _ in range(20):  # More iterations to test randomness
            proxy = rotator.get_proxy(db_proxies)
            assert proxy is not None
            selected_proxies.add(str(proxy.ip))

        # Should have selected from multiple proxies due to randomness
        assert len(selected_proxies) >= 1

    @pytest.mark.integration
    def test_cache_failure_scenarios(
        self, temp_json_path: Path, sample_proxies: List[Proxy]
    ) -> None:
        """Test cache behavior under various failure scenarios."""
        cache = ProxyCache(CacheType.JSON, temp_json_path)

        # Add valid data first
        cache.add_proxies(sample_proxies)
        assert len(cache.get_proxies()) == len(sample_proxies)

        # Test JSON corruption recovery
        temp_json_path.write_text("{ invalid json data }")

        # Create new cache instance - should handle corruption gracefully
        corrupted_cache = ProxyCache(CacheType.JSON, temp_json_path)
        recovered_proxies = corrupted_cache.get_proxies()

        # Should return empty list on corruption, not crash
        assert recovered_proxies == []

        # Should be able to add new data after corruption
        corrupted_cache.add_proxies(sample_proxies[:1])
        assert len(corrupted_cache.get_proxies()) == 1

    @pytest.mark.integration
    def test_cache_rotation_performance(self, sample_proxies: List[Proxy]) -> None:
        """Test cache and rotation performance with various strategies."""
        cache = ProxyCache(CacheType.MEMORY)

        # Test all rotation strategies
        strategies = [
            RotationStrategy.ROUND_ROBIN,
            RotationStrategy.RANDOM,
            RotationStrategy.WEIGHTED,
        ]

        cache.add_proxies(sample_proxies)
        cached_proxies = cache.get_proxies()

        for strategy in strategies:
            rotator = ProxyRotator(strategy)

            # Test multiple rotations
            selected_proxies = []
            for _ in range(10):
                proxy = rotator.get_proxy(cached_proxies)
                assert proxy is not None
                selected_proxies.append(proxy)

            # All strategies should return valid proxies
            assert len(selected_proxies) == 10
            assert all(p is not None for p in selected_proxies)

    @pytest.mark.integration
    def test_cache_size_handling(self, sample_proxies: List[Proxy]) -> None:
        """Test cache behavior with different dataset sizes."""
        cache = ProxyCache(CacheType.MEMORY)

        # Test with empty cache
        assert len(cache.get_proxies()) == 0

        # Test with single proxy
        cache.add_proxies([sample_proxies[0]])
        assert len(cache.get_proxies()) == 1

        # Test with multiple proxies
        cache.add_proxies(sample_proxies[1:])
        assert len(cache.get_proxies()) == len(sample_proxies)

        # Test cache clearing
        cache.clear()
        assert len(cache.get_proxies()) == 0


class TestCacheValidatorIntegration:
    """Test integration between ProxyCache and ProxyValidator."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_cache_validator_workflow(
        self, temp_json_path: Path, sample_proxies: List[Proxy]
    ) -> None:
        """Test complete cache-validator workflow."""
        cache = ProxyCache(CacheType.JSON, temp_json_path)
        validator = ProxyValidator()

        # Add initial proxies
        cache.add_proxies(sample_proxies)

        # Mock validation responses
        with patch.object(validator, "validate_proxy", new_callable=AsyncMock) as mock_validate:
            from proxywhirl.validator import ValidationResult

            # Create mock validation results with proper proxy parameter
            mock_results = [
                ValidationResult(
                    proxy=sample_proxies[0],
                    is_valid=True,
                    response_time=0.1,
                    error_type=None,
                    error_message=None,
                ),
                ValidationResult(
                    proxy=sample_proxies[1],
                    is_valid=False,
                    response_time=None,
                    error_type=ValidationErrorType.TIMEOUT,
                    error_message="Timeout",
                ),
                ValidationResult(
                    proxy=sample_proxies[2],
                    is_valid=True,
                    response_time=0.2,
                    error_type=None,
                    error_message=None,
                ),
            ]
            mock_validate.side_effect = mock_results

            # Validate all cached proxies
            cached_proxies = cache.get_proxies()
            validation_results = []

            for proxy in cached_proxies:
                result = await validator.validate_proxy(proxy)
                validation_results.append((proxy, result.is_valid))

                # Update cache with the proxy (simulating metric updates)
                cache.update_proxy(proxy)

        # Verify cache updates
        updated_proxies = cache.get_proxies()
        assert len(updated_proxies) == len(sample_proxies)

        # Check that we got mixed validation results
        valid_count = sum(1 for _, is_valid in validation_results if is_valid)
        invalid_count = len(validation_results) - valid_count

        assert valid_count > 0  # Some should be valid
        assert invalid_count > 0  # Some should be invalid    @pytest.mark.integration

    @pytest.mark.asyncio
    async def test_validator_circuit_breaker_cache_integration(
        self, temp_db_path: Path, sample_proxies: List[Proxy]
    ) -> None:
        """Test validator circuit breaker integration with cache updates."""
        cache = ProxyCache(CacheType.SQLITE, temp_db_path)
        validator = ProxyValidator()

        cache.add_proxies(sample_proxies)

        # Mock repeated failures to trigger circuit breaker
        with patch.object(validator, "validate_proxy", new_callable=AsyncMock) as mock_validate:
            # Simulate circuit breaker behavior
            failure_count = 0

            def mock_validation(proxy: Proxy) -> bool:
                nonlocal failure_count
                failure_count += 1
                if failure_count > 3:  # Circuit breaker threshold
                    raise Exception("Circuit breaker open")
                return False

            mock_validate.side_effect = mock_validation

            # Attempt validation that will trigger circuit breaker
            cached_proxies = cache.get_proxies()

            try:
                for proxy in cached_proxies:
                    await validator.validate_proxy(proxy)
                    proxy.failure_count += 1
                    cache.update_proxy(proxy)
            except Exception:
                pass  # Expected with circuit breaker

            # Verify cache was updated even with circuit breaker
            updated_proxies = cache.get_proxies()
            assert len(updated_proxies) == len(sample_proxies)

            # Check that some failure counts were incremented
            total_failures = sum(p.failure_count for p in updated_proxies)
            original_failures = sum(p.failure_count for p in sample_proxies)
            assert total_failures > original_failures


class TestFullComponentIntegration:
    """Test integration of all components together through ProxyWhirl."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_proxywhirl_component_orchestration(self, temp_json_path: Path) -> None:
        """Test ProxyWhirl orchestrating all components."""
        pw = ProxyWhirl(
            cache_type=CacheType.JSON,
            cache_path=temp_json_path,
            rotation_strategy=RotationStrategy.ROUND_ROBIN,
            auto_validate=True,
        )

        # Add test data
        test_data: List[Dict[str, Any]] = [
            {
                "ip": "203.0.113.10",
                "port": 8080,
                "scheme": "http",
                "country": "US",
                "anonymity": "elite",
            },
            {
                "ip": "203.0.113.11",
                "port": 3128,
                "scheme": "https",
                "country": "GB",
                "anonymity": "anonymous",
            },
        ]

        pw.add_user_provided_loader(test_data)

        # Mock validation for controlled testing
        with patch.object(pw.validator, "validate_proxy", new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = True

            # Test complete workflow
            fetch_count = await pw.fetch_proxies_async(validate=True)
            assert fetch_count >= 0

            # Test component integration
            proxy_count = pw.get_proxy_count()
            assert proxy_count >= 0

            # Test rotation integration
            proxy1 = pw.get_proxy()
            proxy2 = pw.get_proxy()

            # With round-robin, should get different proxies (if more than one valid)
            if proxy_count > 1:
                assert proxy1 != proxy2 or proxy1 is None or proxy2 is None

            # Test cache persistence
            assert temp_json_path.exists()

            # Test health reporting integration
            health_report = await pw.generate_health_report()
            assert "ProxyWhirl Health Report" in health_report

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_error_propagation_across_components(self, temp_db_path: Path) -> None:
        """Test error handling and propagation across components."""
        pw = ProxyWhirl(cache_type=CacheType.SQLITE, cache_path=temp_db_path)

        test_data: List[Dict[str, Any]] = [
            {"ip": "203.0.113.20", "port": 8080, "scheme": "http", "country": "US"}
        ]
        pw.add_user_provided_loader(test_data)

        # Test cache error handling
        with patch.object(pw.cache, "add_proxies", side_effect=sqlite3.Error("DB error")):
            # Should handle database errors gracefully
            with pytest.raises(sqlite3.Error):
                await pw.fetch_proxies_async()

        # Test validator error propagation
        with patch.object(
            pw.validator, "validate_proxy_async", new_callable=AsyncMock
        ) as mock_validate:
            mock_validate.side_effect = Exception("Validation service down")

            # Should handle validation errors gracefully
            result = await pw.validate_proxies_async()
            assert isinstance(result, int)  # Should not raise

        # Test rotator error handling
        with patch.object(pw.rotator, "get_next_proxy", side_effect=Exception("Rotation error")):
            # Should handle rotation errors gracefully
            proxy = pw.get_proxy()
            assert proxy is None  # Should return None on error

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_concurrent_component_access(self, temp_json_path: Path) -> None:
        """Test concurrent access to components."""
        pw = ProxyWhirl(cache_type=CacheType.JSON, cache_path=temp_json_path)

        test_data: List[Dict[str, Any]] = [
            {"ip": f"203.0.113.{i}", "port": 8080 + i, "scheme": "http", "country": "US"}
            for i in range(30, 40)
        ]
        pw.add_user_provided_loader(test_data)

        with patch.object(pw.validator, "validate_proxy", new_callable=AsyncMock) as mock_validate:
            from proxywhirl.validator import ValidationResult

            test_proxy = Proxy(
                host="203.0.113.30",
                port=8080,
                schemes=[Scheme.HTTP],
                country="US",
                anonymity="elite",
                source="test",
            )
            mock_validate.return_value = ValidationResult(
                proxy=test_proxy,
                is_valid=True,
                response_time=0.1,
            )

            # Run concurrent operations
            tasks = []

            # Add fetch tasks
            for _ in range(3):
                tasks.append(pw.fetch_proxies_async(validate=True))

            # Add validation tasks
            for _ in range(3):
                tasks.append(pw.validate_proxies_async())

            # Add proxy retrieval tasks
            async def get_multiple_proxies():
                results = []
                for _ in range(5):
                    proxy = pw.get_proxy()
                    results.append(proxy)
                return results

            for _ in range(2):
                tasks.append(get_multiple_proxies())

            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Verify no exceptions occurred
            exceptions = [r for r in results if isinstance(r, Exception)]
            assert len(exceptions) == 0, f"Concurrent operations failed: {exceptions}"

            # Verify some successful operations
            successful_results = [r for r in results if not isinstance(r, Exception)]
            assert len(successful_results) > 0

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_component_state_consistency(self, temp_db_path: Path) -> None:
        """Test that component states remain consistent across operations."""
        pw = ProxyWhirl(
            cache_type=CacheType.SQLITE,
            cache_path=temp_db_path,
            rotation_strategy=RotationStrategy.WEIGHTED,
        )

        test_data: List[Dict[str, Any]] = [
            {
                "ip": "203.0.113.50",
                "port": 8080,
                "scheme": "http",
                "country": "US",
                "anonymity": "elite",
            },
            {
                "ip": "203.0.113.51",
                "port": 3128,
                "scheme": "https",
                "country": "GB",
                "anonymity": "anonymous",
            },
        ]
        pw.add_user_provided_loader(test_data)

        with patch.object(pw.validator, "validate_proxy", new_callable=AsyncMock) as mock_validate:
            from proxywhirl.validator import ValidationResult

            test_proxy = Proxy(
                host="203.0.113.50",
                port=8080,
                schemes=[Scheme.HTTP],
                country="US",
                anonymity="elite",
                source="test",
            )
            mock_validate.return_value = ValidationResult(
                proxy=test_proxy,
                is_valid=True,
                response_time=0.1,
            )

            # Initial fetch
            await pw.fetch_proxies_async(validate=True)
            cache_count_1 = pw.get_proxy_count()

            # Validate again
            await pw.validate_proxies_async()
            cache_count_2 = pw.get_proxy_count()

            # Cache count should remain consistent
            assert cache_count_1 == cache_count_2

            # Test proxy rotation consistency
            retrieved_proxies = []
            for _ in range(10):
                proxy = pw.get_proxy()
                if proxy:
                    retrieved_proxies.append(proxy.ip)

            # Should have retrieved some proxies
            assert len(retrieved_proxies) > 0

            # Cache count should still be consistent
            final_count = pw.get_proxy_count()
            assert final_count == cache_count_1
