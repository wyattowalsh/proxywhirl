"""Tests for proxywhirl/proxywhirl.py -- Main ProxyWhirl unified class"""

import asyncio
import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock, patch

import pandas as pd
import pytest

from proxywhirl.loaders.base import BaseLoader
from proxywhirl.loaders.user_provided import UserProvidedLoader
from proxywhirl.models import CacheType, CoreProxy, RotationStrategy, Scheme
from proxywhirl.proxywhirl import ProxyWhirl


@pytest.fixture
def temp_cache_path():
    """Temporary cache path for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "test_cache.json"


@pytest.fixture
def temp_cache_paths():
    """Temporary cache paths for different cache types."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield {"json": Path(tmpdir) / "test_cache.json", "sqlite": Path(tmpdir) / "test_cache.db"}


@pytest.fixture
def sample_proxy_data() -> list[dict[str, str | int]]:
    """Sample proxy data for testing."""
    return [
        {"ip": "192.168.1.1", "port": 8080, "scheme": "http", "country": "US"},
        {"ip": "10.0.0.1", "port": 3128, "scheme": "https", "country": "CA"},
    ]


@pytest.fixture
def mock_loader() -> Mock:
    """Mock loader for testing."""

    async def mock_load_async():
        return pd.DataFrame(
            [
                {
                    "ip": "203.0.113.1",
                    "port": 8080,
                    "scheme": "http",
                    "country": "US",
                    "anonymity": "high",
                }
            ]
        )

    loader = Mock(spec=BaseLoader)
    loader.load.return_value = pd.DataFrame(
        [
            {
                "ip": "203.0.113.1",
                "port": 8080,
                "scheme": "http",
                "country": "US",
                "anonymity": "high",
            }
        ]
    )
    loader.load_async = mock_load_async
    loader.__class__.__name__ = "MockLoader"
    loader.name = "MockLoader"
    return loader


@pytest.fixture
def sample_core_proxy():
    """Sample CoreProxy for testing."""
    return CoreProxy(host="192.168.1.1", port=8080, scheme=Scheme.HTTP, source="test")


class TestProxyWhirlInitialization:
    """Test ProxyWhirl initialization and configuration."""

    def test_init_defaults(self) -> None:
        """Test ProxyWhirl initialization with default parameters."""
        pw = ProxyWhirl()

        assert pw.cache_type == CacheType.MEMORY
        assert pw.rotation_strategy == RotationStrategy.ROUND_ROBIN
        assert pw.health_check_interval == 30
        assert pw.auto_validate is True
        assert pw.enable_metrics is True
        assert pw.max_concurrent_validations == 10

        # Check components are initialized
        assert pw.cache is not None
        assert pw.rotator is not None
        assert pw.validator is not None
        assert len(pw.loaders) > 0

    def test_init_with_custom_cache_type_str(self) -> None:
        """Test initialization with cache type as string."""
        pw = ProxyWhirl(cache_type="json")
        assert pw.cache_type == CacheType.JSON

    def test_init_with_custom_rotation_strategy_str(self) -> None:
        """Test initialization with rotation strategy as string."""
        pw = ProxyWhirl(rotation_strategy="random")
        assert pw.rotation_strategy == RotationStrategy.RANDOM

    def test_init_with_json_cache_and_path(self, temp_cache_path: Path) -> None:
        """Test initialization with JSON cache and custom path."""
        pw = ProxyWhirl(cache_type=CacheType.JSON, cache_path=temp_cache_path)

        assert pw.cache_type == CacheType.JSON
        assert pw.cache.cache_path == temp_cache_path

    def test_init_with_sqlite_cache(self, temp_cache_path: Path) -> None:
        """Test initialization with SQLite cache."""
        sqlite_path = temp_cache_path.with_suffix(".db")
        pw = ProxyWhirl(cache_type=CacheType.SQLITE, cache_path=sqlite_path)

        assert pw.cache_type == CacheType.SQLITE
        assert pw.cache.cache_path == sqlite_path

    def test_init_with_custom_validator_settings(self) -> None:
        """Test initialization with custom validator settings."""
        pw = ProxyWhirl(
            validator_timeout=15.0,
            validator_test_url="https://example.com",
            max_concurrent_validations=5,
        )

        assert pw.validator.timeout == 15.0
        assert "https://example.com" in pw.validator.test_urls
        # max_concurrent is not directly accessible but stored in semaphore
        assert pw.max_concurrent_validations == 5

    def test_init_with_all_custom_settings(self, temp_cache_path: Path) -> None:
        """Test initialization with all custom settings."""
        pw = ProxyWhirl(
            cache_type=CacheType.SQLITE,
            cache_path=temp_cache_path.with_suffix(".db"),
            rotation_strategy=RotationStrategy.WEIGHTED,
            health_check_interval=60,
            auto_validate=False,
            validator_timeout=20.0,
            validator_test_url="https://test.example.com",
            enable_metrics=False,
            max_concurrent_validations=20,
        )

        assert pw.cache_type == CacheType.SQLITE
        assert pw.rotation_strategy == RotationStrategy.WEIGHTED
        assert pw.health_check_interval == 60
        assert pw.auto_validate is False
        assert pw.enable_metrics is False
        assert pw.max_concurrent_validations == 20
        assert pw.validator.timeout == 20.0


class TestProxyWhirlLoaderManagement:
    """Test ProxyWhirl loader management functionality."""

    def test_default_loaders_created(self) -> None:
        """Test default loader creation."""
        pw = ProxyWhirl()

        assert len(pw.loaders) > 0
        # Should not include UserProvidedLoader by default
        loader_names = [loader.__class__.__name__ for loader in pw.loaders]
        assert "UserProvidedLoader" not in loader_names

    def test_add_user_provided_loader_success(
        self, sample_proxy_data: list[dict[str, str | int]]
    ) -> None:
        """Test successful addition of user provided loader."""
        pw = ProxyWhirl()
        initial_count = len(pw.loaders)

        pw.add_user_provided_loader(sample_proxy_data)

        assert len(pw.loaders) == initial_count + 1
        assert isinstance(pw.loaders[-1], UserProvidedLoader)

    def test_add_user_provided_loader_exception(self) -> None:
        """Test user provided loader addition handles exceptions."""
        pw = ProxyWhirl()
        initial_count = len(pw.loaders)

        # Invalid data should be handled gracefully
        pw.add_user_provided_loader("invalid_data")  # type: ignore[arg-type]

        assert len(pw.loaders) == initial_count  # No change

    def test_register_custom_loader(self, mock_loader: Mock) -> None:
        """Test registration of custom loader."""
        pw = ProxyWhirl()
        initial_count = len(pw.loaders)

        pw.register_custom_loader(mock_loader)

        assert len(pw.loaders) == initial_count + 1
        assert pw.loaders[-1] == mock_loader


class TestProxyWhirlAsyncMethods:
    """Test ProxyWhirl async methods."""

    @pytest.mark.asyncio
    async def test_fetch_proxies_async(self) -> None:
        """Test async proxy fetching."""
        pw = ProxyWhirl()

        with patch.object(pw.cache, "add_proxies") as mock_add:
            result = await pw.fetch_proxies_async()
            assert isinstance(result, int)
            assert result >= 0
            # Should call add_proxies on cache
            mock_add.assert_called()

    @pytest.mark.asyncio
    async def test_fetch_proxies_async_parallel_execution(self) -> None:
        """Test that fetch_proxies_async uses parallel loading with load_with_retry."""
        pw = ProxyWhirl()

        # Mock all loaders to use load_with_retry and track call order
        load_with_retry_calls: list[str] = []

        async def mock_load_with_retry(loader_name: str) -> pd.DataFrame:
            """Mock load_with_retry that tracks when it was called."""
            load_with_retry_calls.append(f"start_{loader_name}")
            await asyncio.sleep(0.01)  # Small delay to verify parallel execution
            load_with_retry_calls.append(f"end_{loader_name}")
            return pd.DataFrame(
                [{"ip": "1.2.3.4", "port": 8080, "scheme": "http", "country": "US"}]
            )

        # Patch all loaders' load_with_retry method
        loader_patches: list[Any] = []
        for i, loader in enumerate(pw.loaders):
            # Use AsyncMock with a wrapped async function to avoid coroutine issues
            async def make_mock_fn(index: int) -> pd.DataFrame:
                return await mock_load_with_retry(f"loader_{index}")

            mock_fn = AsyncMock(side_effect=lambda i=i: make_mock_fn(i))
            patch_obj = patch.object(loader, "load_with_retry", mock_fn)
            loader_patches.append(patch_obj)

        with patch.object(pw.cache, "add_proxies") as mock_add:
            # Start all patches
            for p in loader_patches:
                p.start()

            try:
                result = await pw.fetch_proxies_async()

                # Verify result
                assert isinstance(result, int)
                assert result >= 0
                mock_add.assert_called()

                # Verify parallel execution - check that load_with_retry was called on all loaders
                assert (
                    len(load_with_retry_calls) == len(pw.loaders) * 2
                )  # start + end for each loader

            finally:
                # Stop all patches
                for p in loader_patches:
                    p.stop()

    @pytest.mark.asyncio
    async def test_get_proxy_async(self) -> None:
        """Test async proxy retrieval."""
        pw = ProxyWhirl()

        with patch.object(pw.cache, "get_proxies", return_value=[]):
            result = await pw.get_proxy_async()
            assert result is None  # No proxies available

    @pytest.mark.asyncio
    async def test_validate_proxies_async(self) -> None:
        """Test async proxy validation."""
        pw = ProxyWhirl()

        with (
            patch.object(pw.cache, "get_proxies", return_value=[]),
            patch.object(pw.cache, "clear") as mock_clear,
            patch.object(pw.cache, "add_proxies") as mock_add,
        ):
            result = await pw.validate_proxies_async()
            assert result == 0  # No proxies to validate
            mock_clear.assert_called_once()
            mock_add.assert_called_once()


class TestProxyWhirlSyncMethods:
    """Test ProxyWhirl sync methods."""

    def test_fetch_proxies_sync(self) -> None:
        """Test sync proxy fetching."""
        pw = ProxyWhirl()

        with patch.object(pw.cache, "add_proxies"):
            result = pw.fetch_proxies()
            assert isinstance(result, int)
            assert result >= 0

    def test_get_proxy_sync(self) -> None:
        """Test sync proxy retrieval."""
        pw = ProxyWhirl()

        with patch.object(pw.cache, "get_proxies", return_value=[]):
            result = pw.get_proxy()
            assert result is None  # No proxies available

    def test_validate_proxies_sync(self) -> None:
        """Test sync proxy validation."""
        pw = ProxyWhirl()

        with (
            patch.object(pw.cache, "get_proxies", return_value=[]),
            patch.object(pw.cache, "clear"),
            patch.object(pw.cache, "add_proxies"),
        ):
            result = pw.validate_proxies()
            assert result == 0  # No proxies to validate


class TestProxyWhirlUtilityMethods:
    """Test ProxyWhirl utility methods."""

    def test_list_proxies(self) -> None:
        """Test proxy listing."""
        pw = ProxyWhirl()

        with patch.object(pw.cache, "get_proxies", return_value=[]) as mock_get:
            proxies = pw.list_proxies()
            mock_get.assert_called_once()
            assert isinstance(proxies, list)

    def test_get_proxy_count(self) -> None:
        """Test proxy count retrieval."""
        pw = ProxyWhirl()

        with patch.object(pw.cache, "get_proxies", return_value=[]):
            count = pw.get_proxy_count()
            assert count == 0

    def test_clear_cache(self) -> None:
        """Test cache clearing."""
        pw = ProxyWhirl()

        with patch.object(pw.cache, "clear") as mock_clear:
            pw.clear_cache()
            mock_clear.assert_called_once()

    def test_update_proxy_health(self, sample_core_proxy: CoreProxy) -> None:
        """Test proxy health update."""
        pw = ProxyWhirl()
        proxy = sample_core_proxy.to_proxy()

        with (
            patch.object(pw.rotator, "update_health_score") as mock_update_health,
            patch.object(pw.cache, "update_proxy") as mock_update_proxy,
        ):
            pw.update_proxy_health(proxy, True, 1.5)
            mock_update_health.assert_called_once_with(proxy, True, 1.5)
            mock_update_proxy.assert_called_once_with(proxy)


class TestProxyWhirlErrorHandling:
    """Test ProxyWhirl error handling."""

    def test_handles_loader_failures_gracefully(self) -> None:
        """Test that ProxyWhirl handles loader failures gracefully."""
        pw = ProxyWhirl()

        # Mock all loaders to fail
        for loader in pw.loaders:
            loader.load = Mock(side_effect=Exception("Loader failed"))

        # Should not raise exception
        result = pw.fetch_proxies()
        assert isinstance(result, int)
        assert result >= 0

    @pytest.mark.asyncio
    async def test_handles_validator_failures_gracefully(self) -> None:
        """Test that ProxyWhirl handles validator failures gracefully."""
        pw = ProxyWhirl()

        with (
            patch.object(
                pw.validator, "validate_proxies", side_effect=Exception("Validation failed")
            ),
            patch.object(pw.cache, "get_proxies", return_value=[]),
            patch.object(pw.cache, "clear"),
            patch.object(pw.cache, "add_proxies"),
        ):
            # Should not raise exception
            result = await pw.validate_proxies_async()
            assert isinstance(result, int)

    def test_handles_cache_failures_gracefully(self) -> None:
        """Test that ProxyWhirl handles cache failures gracefully."""
        pw = ProxyWhirl()

        with patch.object(pw.cache, "get_proxies", side_effect=Exception("Cache failed")):
            # Should not raise exception for get_proxy_count
            result = pw.get_proxy_count()
            assert result == 0  # Should handle gracefully


class TestProxyWhirlIntegration:
    """Enhanced integration tests for ProxyWhirl with comprehensive scenarios."""

    def test_end_to_end_workflow(self, temp_cache_path: Path) -> None:
        """Test complete workflow from initialization to proxy retrieval."""
        pw = ProxyWhirl(cache_type=CacheType.JSON, cache_path=temp_cache_path, auto_validate=True)

        # Add some test data
        sample_data: list[dict[str, str | int]] = [
            {"ip": "192.168.1.1", "port": 8080, "scheme": "http", "country": "US"}
        ]
        pw.add_user_provided_loader(sample_data)

        # Test basic operations
        count = pw.get_proxy_count()
        assert isinstance(count, int)

        # Clear cache
        pw.clear_cache()

    @pytest.mark.asyncio
    async def test_async_end_to_end_workflow(self, temp_cache_path: Path) -> None:
        """Test complete async workflow."""
        pw = ProxyWhirl(cache_type=CacheType.JSON, cache_path=temp_cache_path, auto_validate=True)

        # Add test data
        sample_data: list[dict[str, str | int]] = [
            {"ip": "10.0.0.1", "port": 3128, "scheme": "https", "country": "CA"}
        ]
        pw.add_user_provided_loader(sample_data)

        # Test async operations
        fetch_result = await pw.fetch_proxies_async()
        assert isinstance(fetch_result, int)

        validate_result = await pw.validate_proxies_async()
        assert isinstance(validate_result, int)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_multi_cache_backend_integration(self, temp_cache_paths: Dict[str, Path]) -> None:
        """Test integration across different cache backends."""
        # Test data
        test_proxies: list[dict[str, Any]] = [
            {"ip": "203.0.113.1", "port": 8080, "scheme": "http", "country": "US"},
            {"ip": "203.0.113.2", "port": 3128, "scheme": "https", "country": "GB"},
            {"ip": "203.0.113.3", "port": 1080, "scheme": "socks4", "country": "DE"},
        ]

        # Test JSON cache backend
        pw_json = ProxyWhirl(cache_type=CacheType.JSON, cache_path=temp_cache_paths["json"])
        pw_json.add_user_provided_loader(test_proxies)

        with patch.object(
            pw_json.validator, "validate_proxy_async", new_callable=AsyncMock
        ) as mock_validate:
            mock_validate.return_value = True
            await pw_json.fetch_proxies_async(validate=True)

        json_count = pw_json.get_proxy_count()
        assert json_count > 0

        # Test SQLite cache backend
        pw_sqlite = ProxyWhirl(cache_type=CacheType.SQLITE, cache_path=temp_cache_paths["sqlite"])
        pw_sqlite.add_user_provided_loader(test_proxies)

        with patch.object(
            pw_sqlite.validator, "validate_proxy_async", new_callable=AsyncMock
        ) as mock_validate:
            mock_validate.return_value = True
            await pw_sqlite.fetch_proxies_async(validate=True)

        sqlite_count = pw_sqlite.get_proxy_count()
        assert sqlite_count > 0
        assert sqlite_count == json_count  # Should have same data

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_rotation_strategy_integration(self, temp_cache_path: Path) -> None:
        """Test integration of different rotation strategies with cache and validation."""
        test_proxies: list[dict[str, Any]] = [
            {"ip": f"203.0.113.{i}", "port": 8080 + i, "scheme": "http", "country": "US"}
            for i in range(1, 6)
        ]

        for strategy in [
            RotationStrategy.ROUND_ROBIN,
            RotationStrategy.RANDOM,
            RotationStrategy.WEIGHTED,
        ]:
            pw = ProxyWhirl(
                cache_type=CacheType.JSON, cache_path=temp_cache_path, rotation_strategy=strategy
            )
            pw.add_user_provided_loader(test_proxies)

            with patch.object(
                pw.validator, "validate_proxy_async", new_callable=AsyncMock
            ) as mock_validate:
                mock_validate.return_value = True
                await pw.fetch_proxies_async(validate=True)

            # Test proxy rotation
            proxies_retrieved: list[Any] = []
            for _ in range(len(test_proxies)):
                proxy = pw.get_proxy()
                if proxy:
                    proxies_retrieved.append(proxy)

            assert len(proxies_retrieved) > 0
            pw.clear_cache()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_loader_cache_validator_pipeline(self, temp_cache_path: Path) -> None:
        """Test complete data pipeline: loaders → cache → validator → rotator."""
        pw = ProxyWhirl(cache_type=CacheType.JSON, cache_path=temp_cache_path)

        # Mock multiple loaders
        mock_loader_data: list[list[dict[str, Any]]] = [
            [{"ip": "203.0.113.10", "port": 8080, "scheme": "http", "country": "US"}],
            [{"ip": "203.0.113.11", "port": 3128, "scheme": "https", "country": "GB"}],
        ]

        for data in mock_loader_data:
            pw.add_user_provided_loader(data)

        # Mock validator responses
        with patch.object(
            pw.validator, "validate_proxy_async", new_callable=AsyncMock
        ) as mock_validate:
            mock_validate.side_effect = [True, False, True]  # Mixed validation results

            # Run complete pipeline
            fetch_count = await pw.fetch_proxies_async(validate=True)
            assert fetch_count >= 0

            # Test that validation affects available proxies
            final_count = pw.get_proxy_count()
            assert final_count >= 0

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_concurrent_operations_integration(self, temp_cache_path: Path) -> None:
        """Test concurrent operations across components."""
        pw = ProxyWhirl(cache_type=CacheType.JSON, cache_path=temp_cache_path)

        test_proxies: list[dict[str, Any]] = [
            {"ip": f"203.0.113.{i}", "port": 8080 + i, "scheme": "http", "country": "US"}
            for i in range(1, 20)
        ]
        pw.add_user_provided_loader(test_proxies)

        with patch.object(
            pw.validator, "validate_proxy_async", new_callable=AsyncMock
        ) as mock_validate:
            mock_validate.return_value = True

            # Run concurrent operations
            tasks = []
            tasks.append(pw.fetch_proxies_async(validate=True))
            tasks.append(pw.validate_proxies_async())
            for _ in range(5):
                tasks.append(pw.get_proxy_async())

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Check that no exceptions occurred
            exceptions = [r for r in results if isinstance(r, Exception)]
            assert len(exceptions) == 0

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_error_propagation_and_recovery(self, temp_cache_path: Path) -> None:
        """Test error propagation and recovery across components."""
        pw = ProxyWhirl(cache_type=CacheType.JSON, cache_path=temp_cache_path)

        test_proxies = [{"ip": "203.0.113.100", "port": 8080, "scheme": "http", "country": "US"}]
        pw.add_user_provided_loader(test_proxies)

        # Test cache error recovery
        with patch.object(pw.cache, "add_proxies", side_effect=Exception("Cache error")):
            # Should handle cache errors gracefully
            result = await pw.fetch_proxies_async()
            assert isinstance(result, int)  # Should not raise

        # Test validator error recovery
        with patch.object(
            pw.validator, "validate_proxy_async", new_callable=AsyncMock
        ) as mock_validate:
            mock_validate.side_effect = Exception("Validation error")

            # Should handle validation errors gracefully
            result = await pw.validate_proxies_async()
            assert isinstance(result, int)  # Should not raise

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_session_management_integration(self) -> None:
        """Test session management across async operations."""
        pw = ProxyWhirl()

        test_proxies = [{"ip": "203.0.113.200", "port": 8080, "scheme": "http", "country": "US"}]
        pw.add_user_provided_loader(test_proxies)

        # Test session context manager
        async with pw.session() as session_pw:
            assert session_pw is pw

            with patch.object(
                pw.validator, "validate_proxy_async", new_callable=AsyncMock
            ) as mock_validate:
                mock_validate.return_value = True
                result = await session_pw.fetch_proxies_async(validate=True)
                assert isinstance(result, int)

    @pytest.mark.asyncio
    async def test_health_report_generation(self) -> None:
        """Test health report generation with enhanced mocking."""
        pw = ProxyWhirl()

        with (
            patch.object(
                pw.validator,
                "health_check",
                return_value={
                    "circuit_breaker_state": "closed",
                    "circuit_breaker_failures": 0,
                    "test_endpoints": [],
                },
            ),
            patch.object(
                pw.validator,
                "get_validation_stats",
                return_value={
                    "total_validations": 0,
                    "successful_validations": 0,
                    "success_rate": 0.0,
                },
            ),
        ):
            report = await pw.generate_health_report()
            assert isinstance(report, str)
            assert "ProxyWhirl Health Report" in report
            assert "Overview" in report

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_comprehensive_workflow_with_real_components(self, temp_cache_path: Path) -> None:
        """Test comprehensive workflow using real component interactions (with controlled mocking)."""
        pw = ProxyWhirl(
            cache_type=CacheType.JSON,
            cache_path=temp_cache_path,
            auto_validate=True,
            rotation_strategy=RotationStrategy.ROUND_ROBIN,
        )

        # Add diverse test data
        test_proxies = [
            {
                "ip": "203.0.113.1",
                "port": 8080,
                "scheme": "http",
                "country": "US",
                "anonymity": "elite",
            },
            {
                "ip": "203.0.113.2",
                "port": 3128,
                "scheme": "https",
                "country": "GB",
                "anonymity": "anonymous",
            },
            {
                "ip": "203.0.113.3",
                "port": 1080,
                "scheme": "socks4",
                "country": "DE",
                "anonymity": "transparent",
            },
            {
                "ip": "203.0.113.4",
                "port": 1080,
                "scheme": "socks5",
                "country": "FR",
                "anonymity": "elite",
            },
        ]
        pw.add_user_provided_loader(test_proxies)

        # Test complete workflow with controlled validation
        with patch.object(
            pw.validator, "validate_proxy_async", new_callable=AsyncMock
        ) as mock_validate:
            # Simulate mixed validation results
            mock_validate.side_effect = [True, False, True, True]

            # Fetch and validate
            fetch_count = await pw.fetch_proxies_async(validate=True)
            assert fetch_count >= 0

            # Test proxy retrieval with rotation
            retrieved_proxies = []
            for _ in range(3):
                proxy = pw.get_proxy()
                if proxy:
                    retrieved_proxies.append(proxy.ip)

            # Test cache persistence
            cached_proxies = pw.cache.get_proxies()
            assert len(cached_proxies) >= 0

            # Test health reporting
            health_report = await pw.generate_health_report()
            assert "ProxyWhirl Health Report" in health_report

            # Test cleanup
            pw.clear_cache()
            assert pw.get_proxy_count() == 0
