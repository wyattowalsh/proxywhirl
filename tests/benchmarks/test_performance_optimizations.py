"""Benchmarks for performance optimizations (cache, database, indexes)."""

from __future__ import annotations

import asyncio
import time
from pathlib import Path
from typing import Any

import pytest

from proxywhirl import AsyncProxyWhirl, Proxy, ProxyConfiguration, ProxyPool
from proxywhirl.cache.manager import CacheManager
from proxywhirl.cache.models import CacheConfig
from proxywhirl.models.core import HealthStatus
from proxywhirl.storage import SQLiteStorage


class TestDatabaseIndexPerformance:
    """Benchmarks for database index optimizations."""

    @pytest.mark.benchmark(group="db-indexes")
    async def test_healthy_proxies_query_performance(self, tmp_path: Path, benchmark: Any) -> None:
        """Benchmark get_healthy_proxies with indexes."""
        db_path = tmp_path / "test.db"
        storage = SQLiteStorage(str(db_path))
        await storage.initialize()

        # Insert 1000 proxies with various health statuses
        proxies = []
        for i in range(1000):
            proxy = Proxy(
                url=f"http://proxy{i}.example.com:{8000 + i % 100}",
                protocol="http",
                health_status=HealthStatus.HEALTHY if i % 3 == 0 else HealthStatus.UNHEALTHY,
                is_residential=i % 2 == 0,
            )
            proxies.append(proxy)

        added, _ = await storage.add_proxies_batch(proxies)
        assert added > 0

        async def run_query() -> list[dict[str, Any]]:
            return await storage.get_healthy_proxies(max_age_hours=48, limit=100)

        # Benchmark the query
        result = await asyncio.to_thread(benchmark, asyncio.run, run_query())
        assert len(result) > 0

        await storage.close()

    @pytest.mark.benchmark(group="db-batching")
    async def test_batch_proxy_query_performance(self, tmp_path: Path) -> None:
        """Benchmark batch proxy queries vs individual queries."""
        db_path = tmp_path / "test.db"
        storage = SQLiteStorage(str(db_path))
        await storage.initialize()

        # Insert 500 proxies
        proxies = []
        proxy_urls = []
        for i in range(500):
            url = f"http://proxy{i}.example.com:{8000 + i}"
            proxy = Proxy(url=url, protocol="http")
            proxies.append(proxy)
            proxy_urls.append(url)

        await storage.add_proxies_batch(proxies)

        # Test batch query performance
        start = time.time()
        batch_result = await storage.get_proxies_batch(proxy_urls[:100])
        batch_time = time.time() - start

        # Results should match
        assert len(batch_result) == 100
        assert batch_time < 1.0  # Should complete in < 1 second

        await storage.close()

    @pytest.mark.benchmark(group="db-stats-cache")
    async def test_statistics_caching(self, tmp_path: Path) -> None:
        """Benchmark statistics caching vs repeated queries."""
        db_path = tmp_path / "test.db"
        storage = SQLiteStorage(str(db_path))
        await storage.initialize()

        # Insert some proxies
        proxies = [
            Proxy(url=f"http://proxy{i}.example.com:8000", protocol="http") for i in range(100)
        ]
        await storage.add_proxies_batch(proxies)

        # First call should hit the database
        start = time.time()
        stats1 = await storage.get_stats()
        first_time = time.time() - start

        # Second call within TTL should use cache
        start = time.time()
        stats2 = await storage.get_stats_cached()
        cached_time = time.time() - start

        # Cached call should be significantly faster
        assert stats1 == stats2
        assert cached_time < first_time

        await storage.close()


class TestCachePerformance:
    """Benchmarks for cache optimizations."""

    @pytest.mark.benchmark(group="cache-lru")
    def test_lru_eviction_performance(self) -> None:
        """Benchmark LRU eviction with OrderedDict."""
        from collections import OrderedDict

        # Create a cache with 1000 entries
        cache: OrderedDict[str, int] = OrderedDict()

        start = time.time()
        for i in range(1000):
            cache[f"key_{i}"] = i

            # Evict if over capacity
            if len(cache) > 500:
                cache.popitem(last=False)  # O(1) eviction with OrderedDict

        elapsed = time.time() - start
        assert elapsed < 0.1  # Should complete in < 100ms

    @pytest.mark.benchmark(group="cache-warmup")
    async def test_cache_prewarming_performance(self, tmp_path: Path) -> None:
        """Benchmark cache prewarming from file."""
        config = CacheConfig()
        manager = CacheManager(config)

        # Create a test JSON file with 500 proxy entries
        test_file = tmp_path / "proxies.json"
        proxies_data = [
            {
                "proxy_url": f"http://proxy{i}.example.com:{8000 + i}",
                "protocol": "http",
                "source": "test",
            }
            for i in range(500)
        ]

        import json

        test_file.write_text(json.dumps(proxies_data))

        # Benchmark cache warming
        start = time.time()
        result = manager.warm_from_file(str(test_file))
        elapsed = time.time() - start

        assert result["loaded"] > 0
        assert elapsed < 2.0  # Should complete in < 2 seconds


class TestPoolMembershipPerformance:
    """Benchmarks for O(1) pool membership checking."""

    def test_pool_membership_check_performance(self) -> None:
        """Benchmark O(1) URL-based pool membership checking."""
        pool = ProxyPool(name="test_pool")

        # Add 1000 proxies
        for i in range(1000):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8000", protocol="http")
            pool.add_proxy(proxy)

        # Benchmark membership checks
        start = time.time()
        for i in range(10000):
            idx = i % 1000
            # O(1) check using _url_index
            has_proxy = pool.has_proxy_url(f"http://proxy{idx}.example.com:8000")
            assert has_proxy

        elapsed = time.time() - start
        assert elapsed < 0.5  # 10000 checks should complete in < 500ms


class TestBatchValidationPerformance:
    """Benchmarks for batch proxy validation."""

    @pytest.mark.benchmark(group="batch-validation")
    async def test_parallel_batch_validation_setup(self) -> None:
        """Benchmark setup for parallel batch validation."""
        config = ProxyConfiguration()
        rotator = AsyncProxyWhirl(config=config)

        # Add 100 proxies
        for i in range(100):
            rotator.add_proxy(Proxy(url=f"http://proxy{i}.example.com:8000", protocol="http"))

        # Verify pool can be batch queried
        pool = rotator.pool
        assert pool.size == 100

        # Check membership for 100 proxies (O(1) each)
        start = time.time()
        for i in range(100):
            assert pool.has_proxy_url(f"http://proxy{i}.example.com:8000")
        elapsed = time.time() - start

        assert elapsed < 0.1  # 100 checks should be very fast


class TestWALModePerformance:
    """Benchmarks for WAL mode concurrent access."""

    @pytest.mark.benchmark(group="wal-mode")
    async def test_concurrent_reads_with_wal(self, tmp_path: Path) -> None:
        """Benchmark concurrent read performance with WAL mode."""
        db_path = tmp_path / "test.db"
        storage = SQLiteStorage(str(db_path))
        await storage.initialize()

        # Insert some proxies
        proxies = [
            Proxy(url=f"http://proxy{i}.example.com:8000", protocol="http") for i in range(100)
        ]
        await storage.add_proxies_batch(proxies)

        # Simulate concurrent reads
        async def read_healthy() -> int:
            result = await storage.get_healthy_proxies(limit=50)
            return len(result)

        start = time.time()
        # Run 20 concurrent read tasks
        tasks = [read_healthy() for _ in range(20)]
        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start

        # All reads should succeed
        assert all(r >= 0 for r in results)
        assert elapsed < 5.0  # 20 concurrent reads should complete quickly

        await storage.close()
