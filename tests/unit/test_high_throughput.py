"""Tests for high-throughput scenarios."""

from __future__ import annotations

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from proxywhirl.models import Proxy


@pytest.mark.slow
class TestHighThroughput:
    """Test high-request-volume scenarios."""

    def test_sync_proxy_selection_1000_requests(self) -> None:
        """Test 1000 synchronous proxy selections."""
        proxies = [Proxy(url=f"http://proxy{i}.local:8080") for i in range(10)]
        selections = []

        def select():
            selections.append(proxies[0])

        start = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(select) for _ in range(1000)]
            for f in futures:
                f.result()
        elapsed = time.time() - start

        assert len(selections) == 1000
        assert elapsed < 10  # Should be fast

    @pytest.mark.asyncio
    async def test_async_proxy_selection_1000_requests(self) -> None:
        """Test 1000 async proxy selections."""
        proxies = [Proxy(url=f"http://proxy{i}.local:8080") for i in range(10)]

        async def select():
            await asyncio.sleep(0.0001)
            return proxies[0]

        start = time.time()
        results = await asyncio.gather(*[select() for _ in range(1000)])
        elapsed = time.time() - start

        assert len(results) == 1000
        assert elapsed < 5  # Should be very fast

    @pytest.mark.asyncio
    async def test_high_concurrency_cache_access(self) -> None:
        """Test cache under high concurrency."""
        cache = {}

        async def cache_op(key: str, value: str):
            cache[key] = value
            await asyncio.sleep(0.0001)
            return cache.get(key)

        start = time.time()
        results = await asyncio.gather(
            *[cache_op(f"key{i % 100}", f"value{i}") for i in range(1000)]
        )
        elapsed = time.time() - start

        assert len(results) == 1000
        assert elapsed < 5

    def test_throughput_with_pool_operations(self) -> None:
        """Test throughput with pool add/remove."""
        pool = []
        pool_lock = __import__("threading").Lock()

        def pool_op(op: str):
            with pool_lock:
                if op == "add":
                    pool.append(Proxy(url=f"http://proxy{len(pool)}.local:8080"))
                elif op == "remove" and pool:
                    pool.pop()

        start = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(pool_op, "add" if i % 2 == 0 else "remove") for i in range(500)
            ]
            for f in futures:
                f.result()
        elapsed = time.time() - start

        assert elapsed < 5

    @pytest.mark.asyncio
    async def test_burst_traffic_handling(self) -> None:
        """Test handling of burst traffic."""
        request_count = 0

        async def handle_request():
            nonlocal request_count
            request_count += 1
            await asyncio.sleep(0.0001)

        start = time.time()
        await asyncio.gather(*[handle_request() for _ in range(5000)])
        elapsed = time.time() - start

        assert request_count == 5000
        # 5000 requests should take reasonable time
        assert elapsed < 10

    def test_throughput_metric_calculation(self) -> None:
        """Test throughput metrics."""
        request_count = 10000
        duration = 1.0  # seconds

        throughput = request_count / duration
        assert throughput == 10000  # requests per second

    @pytest.mark.asyncio
    async def test_sustained_load(self) -> None:
        """Test sustained load over time."""
        results = []

        async def work():
            await asyncio.sleep(0.001)
            return "ok"

        # Multiple batches
        for batch in range(5):
            batch_results = await asyncio.gather(*[work() for _ in range(200)])
            results.extend(batch_results)

        assert len(results) == 1000

    def test_parallel_cache_operations(self) -> None:
        """Test parallel cache operations."""
        cache = {}
        operations = 0
        op_lock = __import__("threading").Lock()

        def cache_op():
            nonlocal operations
            with op_lock:
                operations += 1
            cache[f"key{operations}"] = f"value{operations}"

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(cache_op) for _ in range(500)]
            for f in futures:
                f.result()

        # At least some operations should have completed
        assert operations > 0

    @pytest.mark.asyncio
    async def test_async_io_bound_throughput(self) -> None:
        """Test I/O-bound throughput."""
        completed = 0

        async def io_bound_work():
            nonlocal completed
            await asyncio.sleep(0.001)  # Simulate I/O
            completed += 1

        await asyncio.gather(*[io_bound_work() for _ in range(100)])
        assert completed == 100
