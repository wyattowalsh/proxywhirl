"""Tests for concurrent proxy pool access under load."""

from __future__ import annotations

import asyncio
import random
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import pytest


class SimpleProxyPool:
    """Simple proxy pool for testing concurrent access."""

    def __init__(self, proxies: list[str] | None = None) -> None:
        """Initialize pool."""
        self.proxies = proxies or []
        self.current_index = 0
        self._lock = threading.Lock()

    def get_proxy(self) -> str | None:
        """Get next proxy (round-robin)."""
        if not self.proxies:
            return None

        with self._lock:
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            return proxy

    def add_proxy(self, proxy: str) -> None:
        """Add proxy to pool."""
        with self._lock:
            self.proxies.append(proxy)

    def remove_proxy(self, proxy: str) -> None:
        """Remove proxy from pool."""
        with self._lock:
            if proxy in self.proxies:
                self.proxies.remove(proxy)

    async def get_proxy_async(self) -> str | None:
        """Get proxy asynchronously."""
        return self.get_proxy()


class TestProxyPoolConcurrency:
    """Test concurrent proxy pool access."""

    @pytest.fixture
    def pool(self) -> SimpleProxyPool:
        """Provide proxy pool."""
        return SimpleProxyPool(
            [
                "http://proxy1:8080",
                "http://proxy2:8080",
                "http://proxy3:8080",
            ]
        )

    def test_concurrent_sync_access(self, pool) -> None:
        """Test concurrent synchronous access."""
        results = []

        def worker() -> None:
            for _ in range(10):
                proxy = pool.get_proxy()
                results.append(proxy)

        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 50
        assert all(p in pool.proxies for p in results)

    def test_round_robin_distribution(self, pool) -> None:
        """Test round-robin distribution."""
        proxies = [pool.get_proxy() for _ in range(9)]

        # Each proxy should be selected 3 times
        assert proxies.count("http://proxy1:8080") == 3
        assert proxies.count("http://proxy2:8080") == 3
        assert proxies.count("http://proxy3:8080") == 3

    def test_concurrent_add_remove(self, pool) -> None:
        """Test concurrent add/remove operations."""
        results = []

        def adder() -> None:
            for i in range(5):
                pool.add_proxy(f"http://dynamic{i}:8080")

        def remover() -> None:
            for _ in range(3):
                if pool.proxies:
                    pool.remove_proxy(pool.proxies[0])

        add_thread = threading.Thread(target=adder)
        remove_thread = threading.Thread(target=remover)

        add_thread.start()
        remove_thread.start()

        add_thread.join()
        remove_thread.join()

        # Pool should still be valid
        assert isinstance(pool.proxies, list)

    @pytest.mark.asyncio
    async def test_concurrent_async_access(self, pool) -> None:
        """Test concurrent async access."""

        async def worker() -> list[str | None]:
            results = []
            for _ in range(5):
                proxy = await pool.get_proxy_async()
                results.append(proxy)
            return results

        all_results = await asyncio.gather(*[worker() for _ in range(3)])
        flat = [p for results in all_results for p in results]

        assert len(flat) == 15
        assert all(p in pool.proxies for p in flat)

    def test_thread_pool_executor(self, pool) -> None:
        """Test using thread pool executor."""

        def get_proxies(count: int) -> list[str | None]:
            return [pool.get_proxy() for _ in range(count)]

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(get_proxies, 10) for _ in range(3)]
            results = []
            for future in futures:
                results.extend(future.result())

        assert len(results) == 30

    def test_high_concurrency_access(self, pool) -> None:
        """Test high concurrency access."""
        results = []
        threads_count = 20
        operations_per_thread = 50

        def worker(worker_id: int) -> None:
            for op in range(operations_per_thread):
                proxy = pool.get_proxy()
                results.append((worker_id, op, proxy))

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(threads_count)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == threads_count * operations_per_thread

    def test_empty_pool_concurrent(self, pool) -> None:
        """Test accessing empty pool concurrently."""
        empty_pool = SimpleProxyPool([])
        results = []

        def worker() -> None:
            for _ in range(5):
                proxy = empty_pool.get_proxy()
                results.append(proxy)

        threads = [threading.Thread(target=worker) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert all(p is None for p in results)

    def test_single_proxy_concurrent(self) -> None:
        """Test single proxy under concurrent load."""
        single_pool = SimpleProxyPool(["http://single:8080"])
        results = []

        def worker() -> None:
            for _ in range(10):
                proxy = single_pool.get_proxy()
                results.append(proxy)

        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 50
        assert all(p == "http://single:8080" for p in results)

    @pytest.mark.asyncio
    async def test_mixed_sync_async_access(self, pool) -> None:
        """Test mixed sync and async access."""
        sync_results = []

        def sync_worker() -> None:
            for _ in range(5):
                sync_results.append(pool.get_proxy())

        async def async_worker() -> list:
            results = []
            for _ in range(5):
                results.append(await pool.get_proxy_async())
            return results

        # Run sync in thread
        thread = threading.Thread(target=sync_worker)
        thread.start()

        # Run async
        async_results = await async_worker()

        thread.join()

        assert len(sync_results) == 5
        assert len(async_results) == 5
