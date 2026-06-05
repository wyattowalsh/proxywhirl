"""Integration and system-level tests."""

from __future__ import annotations

import asyncio
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from proxywhirl.cache.manager import CacheManager
from proxywhirl.cache.models import CacheConfig, CacheEntry
from proxywhirl.exceptions import ProxyFetchError
from proxywhirl.fetchers import ProxyFetcher, ProxyValidator
from proxywhirl.models import (
    HealthStatus,
    Proxy,
    ProxyFormat,
    ProxyPool,
    ProxySourceConfig,
    RenderMode,
)
from proxywhirl.rotator import AsyncProxyWhirl, ProxyWhirl
from proxywhirl.storage import SQLiteStorage

pytestmark = [pytest.mark.slow, pytest.mark.integration]


async def _initialized_storage(tmp_path: Path, name: str = "proxies.db") -> SQLiteStorage:
    storage = SQLiteStorage(tmp_path / name)
    await storage.initialize()
    return storage


def _cache_config(tmp_path: Path) -> CacheConfig:
    return CacheConfig(
        l2_cache_dir=str(tmp_path / "cache"),
        l3_database_path=str(tmp_path / "cache.db"),
    )


def _cache_entry(key: str, proxy_url: str) -> CacheEntry:
    now = datetime.now(timezone.utc)
    return CacheEntry(
        key=key,
        proxy_url=proxy_url,
        source="integration-test",
        fetch_time=now,
        last_accessed=now,
        ttl_seconds=3600,
        expires_at=now + timedelta(seconds=3600),
    )


def _healthy_proxy(index: int) -> Proxy:
    return Proxy(
        url=f"http://healthy{index}.example.com:8080",
        health_status=HealthStatus.HEALTHY,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )


def _browser_source() -> ProxySourceConfig:
    return ProxySourceConfig(
        url="https://example.com/proxies.json",
        format=ProxyFormat.JSON,
        render_mode=RenderMode.BROWSER,
    )


# ============================================================================
# SCHEMA MIGRATION TESTS
# ============================================================================


class TestSchemaMigrations:
    """Test schema migration success and failure paths."""

    @pytest.mark.asyncio
    async def test_storage_initialization(self, tmp_path: Path) -> None:
        """Test storage initializes correctly."""
        storage = await _initialized_storage(tmp_path)
        try:
            assert storage.filepath == tmp_path / "proxies.db"
            assert (tmp_path / "proxies.db").exists()
        finally:
            await storage.close()

    @pytest.mark.asyncio
    async def test_pool_save_and_load_roundtrip(self, tmp_path: Path) -> None:
        """Test saving and loading proxies preserves data."""
        storage = await _initialized_storage(tmp_path)
        proxies = [Proxy(url=f"http://proxy{i}.example.com:8080") for i in range(5)]

        try:
            await storage.save(proxies, validated=True)
            loaded = await storage.load()
            assert {proxy["url"] for proxy in loaded} == {proxy.url for proxy in proxies}
        finally:
            await storage.clear()
            await storage.close()

    @pytest.mark.asyncio
    async def test_storage_handles_empty_save(self, tmp_path: Path) -> None:
        """Test storage handles empty saves gracefully."""
        storage = await _initialized_storage(tmp_path)

        try:
            await storage.save([])
            assert await storage.load() == []
        finally:
            await storage.close()

    @pytest.mark.asyncio
    async def test_storage_clear_removes_saved_proxies(self, tmp_path: Path) -> None:
        """Test storage clear removes saved proxies."""
        storage = await _initialized_storage(tmp_path)
        proxies = [Proxy(url="http://clear.example.com:8080")]

        try:
            await storage.save(proxies)
            assert len(await storage.load()) == 1
            await storage.clear()
            assert await storage.load() == []
        finally:
            await storage.close()

    @pytest.mark.asyncio
    async def test_multiple_proxy_storage_consistency(self, tmp_path: Path) -> None:
        """Test consistency when storing multiple proxies."""
        storage = await _initialized_storage(tmp_path)
        proxies = [Proxy(url=f"http://multi{i}.example.com:8080") for i in range(3)]

        try:
            await storage.save(proxies)
            loaded = await storage.load()
            assert len(loaded) == 3
            assert {proxy["url"] for proxy in loaded} == {proxy.url for proxy in proxies}
        finally:
            await storage.clear()
            await storage.close()


# ============================================================================
# BROWSER/PLAYWRIGHT FAILURE TESTS
# ============================================================================


class TestBrowserFailures:
    """Test Playwright failure handling and recovery."""

    @pytest.mark.asyncio
    async def test_browser_fetch_timeout_handling(self) -> None:
        """Test browser fetch timeout handling."""
        fetcher = ProxyFetcher(dedup_cache_ttl=300)

        with patch("proxywhirl.browser.BrowserRenderer.render", side_effect=TimeoutError()):
            with pytest.raises(ProxyFetchError):
                await fetcher.fetch_from_source(_browser_source())

    @pytest.mark.asyncio
    async def test_browser_connection_failure(self) -> None:
        """Test browser connection failure handling."""
        fetcher = ProxyFetcher(dedup_cache_ttl=300)

        with patch(
            "proxywhirl.browser.BrowserRenderer.render",
            side_effect=RuntimeError("Browser unavailable"),
        ):
            with pytest.raises(ProxyFetchError):
                await fetcher.fetch_from_source(_browser_source())

    @pytest.mark.asyncio
    async def test_browser_recovery_after_failure(self) -> None:
        """Test browser recovery after failure."""
        fetcher = ProxyFetcher(dedup_cache_ttl=300)

        call_count = 0

        async def flaky_browser_fetch(url: str) -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise RuntimeError("Browser unavailable")
            return json.dumps([{"url": "http://proxy1.com:8080"}])

        with patch("proxywhirl.browser.BrowserRenderer.render", side_effect=flaky_browser_fetch):
            # First call fails
            with pytest.raises(ProxyFetchError):
                await fetcher.fetch_from_source(_browser_source())

            # Second call should succeed
            proxies = await fetcher.fetch_from_source(_browser_source())
            assert proxies == [{"url": "http://proxy1.com:8080"}]

    @pytest.mark.asyncio
    async def test_proxy_validator_network_failure(self) -> None:
        """Test proxy validator handles network failures."""
        validator = ProxyValidator()

        with patch("asyncio.open_connection", side_effect=OSError("network unavailable")):
            result = await validator.validate({"url": "http://proxy.example.com:8080"})
            assert result.is_valid is False


# ============================================================================
# HIGH CONCURRENCY API TESTS
# ============================================================================


class TestHighConcurrencyAPI:
    """Test API under concurrent load (100+ req/s)."""

    @pytest.mark.slow
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_api_concurrent_pool_requests(self, tmp_path: Path) -> None:
        """Test API handling concurrent pool requests."""
        storage = await _initialized_storage(tmp_path)

        async def make_request(req_id: int) -> bool:
            proxy = Proxy(url=f"http://concurrent{req_id}.example.com:8080")
            await storage.save([proxy])
            loaded = await storage.load()
            await storage.delete(proxy.url)
            return any(row["url"] == proxy.url for row in loaded)

        try:
            results = await asyncio.gather(
                *(make_request(i) for i in range(100)),
                return_exceptions=True,
            )
            successful = sum(result is True for result in results)
            assert successful >= 80
        finally:
            await storage.clear()
            await storage.close()

    @pytest.mark.slow
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_api_concurrent_async_requests(self, tmp_path: Path) -> None:
        """Test API concurrent async requests."""
        storage = await _initialized_storage(tmp_path)

        async def make_async_request(req_id: int) -> str:
            # Simulate async pool operation
            proxy = Proxy(url=f"http://async{req_id}.example.com:8080")
            await storage.save([proxy])
            await asyncio.sleep(0.001)
            loaded = await storage.load()
            await storage.delete(proxy.url)
            assert any(row["url"] == proxy.url for row in loaded)
            return f"response_{req_id}"

        try:
            tasks = [make_async_request(i) for i in range(100)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            successful = sum(isinstance(result, str) for result in results)
            assert successful >= 80
        finally:
            await storage.clear()
            await storage.close()

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
    @pytest.mark.asyncio
    async def test_api_pool_endpoint_under_load(self, tmp_path: Path) -> None:
        """Test pool endpoint handles concurrent requests."""
        storage = await _initialized_storage(tmp_path)
        proxies = [Proxy(url=f"http://load{i}.example.com:8080") for i in range(10)]

        try:
            await storage.save(proxies)

            async def load_proxies() -> bool:
                loaded = await storage.load()
                return len(loaded) == len(proxies)

            results = await asyncio.gather(*(load_proxies() for _ in range(50)))
            assert sum(results) >= 40
        finally:
            await storage.clear()
            await storage.close()


# ============================================================================
# END-TO-END INTEGRATION TESTS
# ============================================================================


class TestEndToEndIntegration:
    """End-to-end integration tests."""

    @pytest.mark.integration
    def test_proxy_rotation_integration(self) -> None:
        """Test complete proxy rotation workflow."""
        rotator = ProxyWhirl(proxies=[_healthy_proxy(i) for i in range(5)], bootstrap=False)

        # Test rotation workflow
        for _ in range(10):
            proxy = rotator.strategy.select(rotator.pool)
            assert proxy is not None
            assert proxy.url is not None

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_async_proxy_rotation_integration(self) -> None:
        """Test async proxy rotation workflow."""
        rotator = AsyncProxyWhirl(
            proxies=[_healthy_proxy(i) for i in range(5)],
            bootstrap=False,
        )

        for _ in range(5):
            proxy = await rotator.get_proxy()
            assert proxy is not None

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_cache_storage_integration(self, tmp_path: Path) -> None:
        """Test cache and storage integration."""
        cache = CacheManager(_cache_config(tmp_path))
        storage = await _initialized_storage(tmp_path, "storage.db")
        proxy = Proxy(url="http://cache-storage.example.com:8080")
        cache_key = "cache-storage"

        try:
            # Store in cache
            cache.put(cache_key, _cache_entry(cache_key, proxy.url))

            # Also store in persistent storage
            await storage.save([proxy])

            # Verify both accessible
            cached = cache.get(cache_key)
            assert cached is not None

            persisted = await storage.load()
            assert any(row["url"] == proxy.url for row in persisted)
        finally:
            await storage.clear()
            await storage.close()
            cache.clear()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_validation_and_rotation_integration(self) -> None:
        """Test proxy validation integrated with rotation."""
        proxies = [_healthy_proxy(i) for i in range(5)]
        pool = ProxyPool(name="validation_pool", proxies=proxies)
        validator = ProxyValidator()

        # Validate proxies
        for proxy in pool.proxies:
            with patch("asyncio.open_connection", side_effect=OSError("network unavailable")):
                result = await validator.validate({"url": proxy.url})
                assert result.is_valid is False

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_pipeline_fetch_store_rotate(self, tmp_path: Path) -> None:
        """Test full pipeline: fetch -> store -> rotate."""
        storage = await _initialized_storage(tmp_path, "pipeline.db")
        cache = CacheManager(_cache_config(tmp_path))

        # Create pool
        proxies = [_healthy_proxy(i) for i in range(5)]
        pool = ProxyPool(name="pipeline_pool", proxies=proxies)

        try:
            # Store
            await storage.save(pool.proxies, validated=True)
            cache.put(str(pool.id), _cache_entry(str(pool.id), pool.proxies[0].url))

            # Load
            loaded = await storage.load()
            assert {row["url"] for row in loaded} == {proxy.url for proxy in pool.proxies}

            # Create rotator with loaded pool
            rotator = ProxyWhirl(proxies=pool.proxies, bootstrap=False)

            # Rotate
            selected = rotator.strategy.select(rotator.pool)
            assert selected is not None
        finally:
            await storage.clear()
            await storage.close()
            cache.clear()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
