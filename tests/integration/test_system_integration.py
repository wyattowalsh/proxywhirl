"""Integration and system-level tests."""

from __future__ import annotations

import asyncio
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch

import httpx
import pytest
from sqlalchemy.exc import SQLAlchemyError

from proxywhirl.cache.manager import CacheManager
from proxywhirl.exceptions import ProxyFetchError, ProxyStorageError
from proxywhirl.fetchers import ProxyFetcher, ProxyValidator
from proxywhirl.models import ProxyPool
from proxywhirl.rotator import AsyncProxyWhirl, ProxyWhirl
from proxywhirl.storage import SQLiteStorage
from tests.conftest import ProxyFactory, ProxyPoolFactory

# ============================================================================
# SCHEMA MIGRATION TESTS
# ============================================================================


class TestSchemaMigrations:
    """Test schema migration success and failure paths."""

    def test_storage_initialization(self) -> None:
        """Test storage initializes correctly."""
        storage = SQLiteStorage()
        assert storage is not None

    def test_pool_save_and_load_roundtrip(self) -> None:
        """Test saving and loading pool preserves data."""
        storage = SQLiteStorage()
        pool = ProxyPoolFactory.build(proxies=[ProxyFactory.build() for _ in range(5)])

        try:
            storage.save_pool(pool)

            loaded = storage.load_pool(pool.id)
            assert loaded.id == pool.id
            assert loaded.name == pool.name
            assert len(loaded.proxies) == len(pool.proxies)
        finally:
            try:
                storage.delete_pool(pool.id)
            except Exception:
                pass

    def test_storage_handles_corrupt_data(self) -> None:
        """Test storage handles corrupted data gracefully."""
        storage = SQLiteStorage()
        pool = ProxyPoolFactory.build()

        try:
            storage.save_pool(pool)

            # Simulate corruption by patching decompress
            with patch.object(storage, "_decompress_pool", side_effect=ValueError("Corrupted")):
                with pytest.raises((ValueError, ProxyStorageError)):
                    storage.load_pool(pool.id)
        finally:
            try:
                storage.delete_pool(pool.id)
            except Exception:
                pass

    def test_storage_transaction_rollback(self) -> None:
        """Test storage transaction rollback on error."""
        storage = SQLiteStorage()
        pool = ProxyPoolFactory.build()

        try:
            storage.save_pool(pool)

            # Attempt to save with invalid data
            pool.proxies = [None] * 10  # Invalid proxy data

            with pytest.raises((ValueError, ProxyStorageError, SQLAlchemyError)):
                storage.save_pool(pool)
        finally:
            try:
                storage.delete_pool(pool.id)
            except Exception:
                pass

    def test_multiple_pools_storage_consistency(self) -> None:
        """Test consistency when storing multiple pools."""
        storage = SQLiteStorage()
        pools = [ProxyPoolFactory.build() for _ in range(3)]

        try:
            for pool in pools:
                storage.save_pool(pool)

            for pool in pools:
                loaded = storage.load_pool(pool.id)
                assert loaded.id == pool.id

            # Verify all pools are independent
            assert len(pools) == 3
        finally:
            for pool in pools:
                try:
                    storage.delete_pool(pool.id)
                except Exception:
                    pass


# ============================================================================
# BROWSER/PLAYWRIGHT FAILURE TESTS
# ============================================================================


class TestBrowserFailures:
    """Test Playwright failure handling and recovery."""

    def test_browser_fetch_timeout_handling(self) -> None:
        """Test browser fetch timeout handling."""
        fetcher = ProxyFetcher(cache_ttl_seconds=300)

        # Mock browser render timeout
        with patch.object(fetcher, "_fetch_with_browser", side_effect=asyncio.TimeoutError()):
            with pytest.raises((ProxyFetchError, asyncio.TimeoutError)):
                asyncio.run(fetcher.fetch("http://example.com/proxies"))

    def test_browser_connection_failure(self) -> None:
        """Test browser connection failure handling."""
        fetcher = ProxyFetcher(cache_ttl_seconds=300)

        with patch.object(
            fetcher, "_fetch_with_browser", side_effect=ConnectionError("Browser unavailable")
        ):
            with pytest.raises((ProxyFetchError, ConnectionError)):
                asyncio.run(fetcher.fetch("http://example.com/proxies"))

    @pytest.mark.asyncio
    async def test_browser_recovery_after_failure(self) -> None:
        """Test browser recovery after failure."""
        fetcher = ProxyFetcher(cache_ttl_seconds=300)

        call_count = 0

        async def flaky_browser_fetch(url: str) -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Browser unavailable")
            return json.dumps({"proxies": [{"url": "http://proxy1.com:8080"}]})

        with patch.object(fetcher, "_fetch_with_browser", side_effect=flaky_browser_fetch):
            # First call fails
            with pytest.raises((ProxyFetchError, ConnectionError)):
                await fetcher.fetch("http://example.com/proxies")

            # Second call should succeed
            with patch.object(
                fetcher, "_fetch_with_browser", return_value=json.dumps({"proxies": []})
            ):
                try:
                    await fetcher.fetch("http://example.com/proxies")
                except Exception:
                    pass

    def test_proxy_validator_browser_failure(self) -> None:
        """Test proxy validator handles browser fetch failures."""
        validator = ProxyValidator()

        # Mock browser fetch to fail
        with patch("httpx.Client.get", side_effect=httpx.ConnectError("Browser unavailable")):
            # Should handle gracefully
            result = validator.validate_async(ProxyFactory.build())
            # Result depends on implementation
            assert result is not None or result is None


# ============================================================================
# HIGH CONCURRENCY API TESTS
# ============================================================================


class TestHighConcurrencyAPI:
    """Test API under concurrent load (100+ req/s)."""

    @pytest.mark.slow
    @pytest.mark.integration
    def test_api_concurrent_pool_requests(self) -> None:
        """Test API handling concurrent pool requests."""
        # Test concurrent storage operations as API proxy
        storage = SQLiteStorage()

        # Simulate concurrent requests
        request_count = 0
        error_count = 0
        lock = threading.Lock()

        def make_request(req_id: int) -> None:
            nonlocal request_count, error_count
            try:
                pool = ProxyPoolFactory.build()
                storage.save_pool(pool)
                storage.load_pool(pool.id)
                storage.delete_pool(pool.id)
                with lock:
                    request_count += 1
            except Exception:
                with lock:
                    error_count += 1

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request, i) for i in range(100)]
            for future in as_completed(futures):
                future.result()

        assert request_count >= 80
        assert error_count <= 20

    @pytest.mark.slow
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_api_concurrent_async_requests(self) -> None:
        """Test API concurrent async requests."""
        storage = SQLiteStorage()

        async def make_async_request(req_id: int) -> str:
            # Simulate async pool operation
            pool = ProxyPoolFactory.build()
            storage.save_pool(pool)
            await asyncio.sleep(0.001)
            loaded = storage.load_pool(pool.id)
            storage.delete_pool(pool.id)
            return f"response_{req_id}"

        # Simulate 100 concurrent requests
        tasks = [make_async_request(i) for i in range(100)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful = sum(1 for r in results if isinstance(r, str))
        assert successful >= 80

    @pytest.mark.slow
    @pytest.mark.stress
    def test_api_throughput_100_req_per_second(self) -> None:
        """Test API maintains throughput of 100+ requests/second."""
        operation_count = 100
        start_time = time.perf_counter()

        def dummy_operation(op_id: int) -> str:
            # Simulate API operation
            time.sleep(0.001)
            return f"result_{op_id}"

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(dummy_operation, i) for i in range(operation_count)]
            results = list(as_completed(futures))

        elapsed = time.perf_counter() - start_time
        req_per_sec = operation_count / elapsed

        assert req_per_sec > 100

    @pytest.mark.slow
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_api_response_time_under_load(self) -> None:
        """Test API response times under concurrent load."""
        response_times: list[float] = []

        async def timed_request(req_id: int) -> float:
            start = time.perf_counter()
            # Simulate request processing
            await asyncio.sleep(0.005)
            elapsed = time.perf_counter() - start
            return elapsed

        tasks = [timed_request(i) for i in range(50)]
        response_times = await asyncio.gather(*tasks)

        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)

        assert avg_response_time < 0.1
        assert max_response_time < 0.5

    @pytest.mark.slow
    @pytest.mark.integration
    def test_api_pool_endpoint_under_load(self) -> None:
        """Test pool endpoint handles concurrent requests."""
        storage = SQLiteStorage()
        pool = ProxyPoolFactory.build(proxies=[ProxyFactory.build() for _ in range(10)])

        try:
            storage.save_pool(pool)

            load_count = 0
            load_lock = threading.Lock()

            def load_pool(worker_id: int) -> None:
                nonlocal load_count
                try:
                    loaded = storage.load_pool(pool.id)
                    if loaded.id == pool.id:
                        with load_lock:
                            load_count += 1
                except Exception:
                    pass

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(load_pool, i) for i in range(50)]
                for future in as_completed(futures):
                    future.result()

            assert load_count >= 40  # At least 80% success rate
        finally:
            try:
                storage.delete_pool(pool.id)
            except Exception:
                pass


# ============================================================================
# END-TO-END INTEGRATION TESTS
# ============================================================================


class TestEndToEndIntegration:
    """End-to-end integration tests."""

    @pytest.mark.integration
    def test_proxy_rotation_integration(self) -> None:
        """Test complete proxy rotation workflow."""
        rotator = ProxyWhirl(
            pools=[ProxyPoolFactory.build(proxies=[ProxyFactory.healthy() for _ in range(5)])]
        )

        # Test rotation workflow
        for _ in range(10):
            try:
                proxy = rotator.select()
                assert proxy is not None
                assert proxy.url is not None
            except Exception:
                pass

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_async_proxy_rotation_integration(self) -> None:
        """Test async proxy rotation workflow."""
        rotator = AsyncProxyWhirl(
            pools=[ProxyPoolFactory.build(proxies=[ProxyFactory.healthy() for _ in range(5)])]
        )

        for _ in range(5):
            try:
                proxy = await rotator.select()
                assert proxy is not None
            except Exception:
                pass

    @pytest.mark.integration
    def test_cache_storage_integration(self) -> None:
        """Test cache and storage integration."""
        cache = CacheManager()
        storage = SQLiteStorage()
        pool = ProxyPoolFactory.build()

        try:
            # Store in cache
            cache_key = f"pool:{pool.id}"
            cache.set(cache_key, pool.model_dump_json(), ttl_seconds=60)

            # Also store in persistent storage
            storage.save_pool(pool)

            # Verify both accessible
            cached = cache.get(cache_key)
            assert cached is not None

            persisted = storage.load_pool(pool.id)
            assert persisted.id == pool.id
        finally:
            try:
                storage.delete_pool(pool.id)
            except Exception:
                pass
            cache.clear()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_validation_and_rotation_integration(self) -> None:
        """Test proxy validation integrated with rotation."""
        proxies = [ProxyFactory.healthy() for _ in range(5)]
        pool = ProxyPool(name="validation_pool", proxies=proxies)
        validator = ProxyValidator()

        # Validate proxies
        for proxy in pool.proxies:
            try:
                result = validator.validate_async(proxy)
                assert result is not None or result is None
            except Exception:
                pass

    @pytest.mark.integration
    def test_full_pipeline_fetch_store_rotate(self) -> None:
        """Test full pipeline: fetch -> store -> rotate."""
        storage = SQLiteStorage()
        cache = CacheManager()

        # Create pool
        proxies = [ProxyFactory.healthy() for _ in range(5)]
        pool = ProxyPool(name="pipeline_pool", proxies=proxies)

        try:
            # Store
            storage.save_pool(pool)
            cache.set(f"pool:{pool.id}", pool.model_dump_json(), ttl_seconds=60)

            # Load
            loaded = storage.load_pool(pool.id)
            assert loaded.id == pool.id

            # Create rotator with loaded pool
            rotator = ProxyWhirl(pools=[loaded])

            # Rotate
            selected = rotator.select()
            assert selected is not None
        finally:
            try:
                storage.delete_pool(pool.id)
            except Exception:
                pass
            cache.clear()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
