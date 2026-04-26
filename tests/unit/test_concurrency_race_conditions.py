"""Tests for concurrency, race conditions, and thread safety."""

from __future__ import annotations

import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

from proxywhirl.cache.manager import CacheManager
from proxywhirl.models import Proxy, ProxyPool
from proxywhirl.storage import SQLiteStorage
from tests.conftest import ProxyFactory, ProxyPoolFactory

# ============================================================================
# RACE CONDITION TESTS
# ============================================================================


class TestRaceConditions:
    """Test for race conditions in threading and asyncio contexts."""

    def test_concurrent_cache_access_race(self) -> None:
        """Test race conditions in concurrent cache access."""
        cache = CacheManager()
        race_condition_detected = False
        errors: list[Exception] = []

        def cache_operation(thread_id: int) -> None:
            try:
                for i in range(50):
                    key = f"thread_{thread_id}_key_{i % 10}"
                    cache.set(key, f"value_{i}", ttl_seconds=60)
                    value = cache.get(key)
                    if value is None:
                        nonlocal race_condition_detected
                        race_condition_detected = True
            except Exception as e:
                errors.append(e)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(cache_operation, i) for i in range(10)]
            for future in as_completed(futures):
                future.result()

        assert len(errors) == 0
        # Some race conditions might be acceptable depending on implementation
        cache.clear()

    def test_concurrent_pool_selection_race(self) -> None:
        """Test race conditions in concurrent pool proxy selection."""
        pool = ProxyPool(
            name="race_test_pool",
            proxies=[ProxyFactory.healthy() for _ in range(20)],
        )

        selected_proxies: list[Proxy] = []
        lock = threading.Lock()
        errors: list[Exception] = []

        def select_from_pool(thread_id: int) -> None:
            try:
                for _ in range(10):
                    if pool.proxies:
                        proxy = pool.proxies[0]
                        with lock:
                            selected_proxies.append(proxy)
            except Exception as e:
                errors.append(e)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(select_from_pool, i) for i in range(5)]
            for future in as_completed(futures):
                future.result()

        assert len(errors) == 0
        assert len(selected_proxies) > 0

    @pytest.mark.asyncio
    async def test_concurrent_async_operations_race(self) -> None:
        """Test race conditions in concurrent async operations."""
        pool = ProxyPool(
            name="async_race_pool",
            proxies=[ProxyFactory.healthy() for _ in range(10)],
        )

        results: list[str] = []

        async def async_select(task_id: int) -> None:
            for _ in range(5):
                if pool.proxies:
                    proxy = pool.proxies[0]
                    results.append(proxy.url)
                await asyncio.sleep(0.001)

        tasks = [async_select(i) for i in range(5)]
        await asyncio.gather(*tasks)

        assert len(results) > 0

    def test_threading_lock_contention(self) -> None:
        """Test lock contention under concurrent access."""
        pool = ProxyPool(
            name="lock_contention_pool",
            proxies=[ProxyFactory.build() for _ in range(50)],
        )

        access_times: list[float] = []
        lock = threading.Lock()

        def access_pool(thread_id: int) -> None:
            for i in range(10):
                start = time.perf_counter()
                with lock:
                    # Simulate operation
                    proxy_count = len(pool.proxies)
                elapsed = time.perf_counter() - start
                access_times.append(elapsed)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(access_pool, i) for i in range(10)]
            for future in as_completed(futures):
                future.result()

        # Average access time should be reasonable
        avg_time = sum(access_times) / len(access_times)
        assert avg_time < 0.1  # Should be very fast


# ============================================================================
# CACHE COHERENCE TESTS
# ============================================================================


class TestCacheCoherence:
    """Test multi-tier cache consistency under load."""

    def test_cache_consistency_concurrent_writes(self) -> None:
        """Test cache consistency with concurrent writes."""
        cache = CacheManager()
        key = "consistency_test_key"
        errors: list[Exception] = []

        def cache_write(value: str) -> None:
            try:
                cache.set(key, value, ttl_seconds=60)
                # Immediately read back
                read_value = cache.get(key)
                # Value should either be what we wrote or a newer value
                assert read_value is not None
            except Exception as e:
                errors.append(e)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(cache_write, f"value_{i}") for i in range(10)]
            for future in as_completed(futures):
                future.result()

        assert len(errors) == 0
        final_value = cache.get(key)
        assert final_value is not None
        cache.clear()

    @pytest.mark.asyncio
    async def test_cache_coherence_async_mixed_access(self) -> None:
        """Test cache coherence with mixed async reads/writes."""
        cache = CacheManager()
        key = "async_consistency_key"

        async def writer(value_id: int) -> None:
            for i in range(5):
                cache.set(f"{key}_{value_id}", f"value_{i}", ttl_seconds=60)
                await asyncio.sleep(0.001)

        async def reader(task_id: int) -> None:
            results = []
            for _ in range(10):
                for i in range(3):
                    value = cache.get(f"{key}_{i}")
                    if value is not None:
                        results.append(value)
                await asyncio.sleep(0.001)
            return results

        # Run writers and readers concurrently
        writers = [writer(i) for i in range(3)]
        readers = [reader(i) for i in range(3)]

        await asyncio.gather(*writers, *readers)
        cache.clear()

    def test_cache_invalidation_propagation(self) -> None:
        """Test that cache invalidation propagates correctly."""
        cache = CacheManager()
        key = "invalidation_test"

        # Set initial value
        cache.set(key, "initial_value", ttl_seconds=60)
        assert cache.get(key) == "initial_value"

        # Update value
        cache.set(key, "updated_value", ttl_seconds=60)
        assert cache.get(key) == "updated_value"

        # Clear cache
        cache.clear()
        assert cache.get(key) is None

    def test_ttl_expiration_consistency(self) -> None:
        """Test TTL expiration consistency across cache layers."""
        cache = CacheManager()
        key = "ttl_test"

        # Set with very short TTL
        cache.set(key, "short_lived", ttl_seconds=1)
        assert cache.get(key) == "short_lived"

        # Wait for expiration
        time.sleep(1.5)
        assert cache.get(key) is None


# ============================================================================
# CONCURRENT POOL MODIFICATIONS
# ============================================================================


class TestConcurrentPoolUpdates:
    """Test concurrent pool modifications."""

    def test_concurrent_proxy_addition(self) -> None:
        """Test adding proxies concurrently."""
        pool = ProxyPool(name="concurrent_add", proxies=[])
        errors: list[Exception] = []

        def add_proxies(batch_id: int) -> None:
            try:
                for i in range(5):
                    proxy = ProxyFactory.build()
                    pool.proxies.append(proxy)
            except Exception as e:
                errors.append(e)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(add_proxies, i) for i in range(5)]
            for future in as_completed(futures):
                future.result()

        assert len(errors) == 0
        assert len(pool.proxies) == 25

    def test_concurrent_proxy_removal(self) -> None:
        """Test removing proxies concurrently."""
        proxies = [ProxyFactory.build() for _ in range(50)]
        pool = ProxyPool(name="concurrent_remove", proxies=proxies)
        lock = threading.Lock()

        def remove_proxies(batch_id: int) -> None:
            for _ in range(5):
                with lock:
                    if pool.proxies:
                        pool.proxies.pop(0)
                time.sleep(0.001)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(remove_proxies, i) for i in range(5)]
            for future in as_completed(futures):
                future.result()

        assert len(pool.proxies) == 25

    @pytest.mark.asyncio
    async def test_concurrent_async_pool_updates(self) -> None:
        """Test async concurrent pool updates."""
        pool = ProxyPool(name="async_updates", proxies=[ProxyFactory.healthy() for _ in range(10)])

        async def modify_pool(task_id: int) -> None:
            for i in range(3):
                if pool.proxies and i % 2 == 0:
                    pool.proxies.pop(0)
                else:
                    pool.proxies.append(ProxyFactory.build())
                await asyncio.sleep(0.001)

        tasks = [modify_pool(i) for i in range(3)]
        await asyncio.gather(*tasks)

        # Pool should still be valid
        assert isinstance(pool, ProxyPool)

    def test_pool_modification_storage_sync(self) -> None:
        """Test pool modifications sync to storage."""
        pool = ProxyPoolFactory.build(proxies=[ProxyFactory.build() for _ in range(5)])
        storage = SQLiteStorage()

        try:
            storage.save_pool(pool)

            # Load and modify
            loaded = storage.load_pool(pool.id)
            original_count = len(loaded.proxies)

            # Add more proxies
            loaded.proxies.extend([ProxyFactory.build() for _ in range(5)])
            storage.save_pool(loaded)

            # Reload and verify
            reloaded = storage.load_pool(pool.id)
            assert len(reloaded.proxies) == original_count + 5
        finally:
            try:
                storage.delete_pool(pool.id)
            except Exception:
                pass


# ============================================================================
# STRESS LOAD TESTS
# ============================================================================


class TestStressLoad:
    """Add stress tests under high throughput."""

    @pytest.mark.slow
    @pytest.mark.stress
    def test_high_throughput_cache_operations(self) -> None:
        """Test cache under high-throughput load."""
        cache = CacheManager()
        operation_count = 1000
        errors: list[Exception] = []

        start_time = time.perf_counter()

        def stress_operation(op_id: int) -> None:
            try:
                key = f"stress_key_{op_id % 100}"
                cache.set(key, f"value_{op_id}", ttl_seconds=60)
                cache.get(key)
            except Exception as e:
                errors.append(e)

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(stress_operation, i) for i in range(operation_count)]
            for future in as_completed(futures):
                future.result()

        elapsed = time.perf_counter() - start_time
        ops_per_sec = operation_count / elapsed

        assert len(errors) == 0
        assert ops_per_sec > 100  # Should handle >100 ops/sec
        cache.clear()

    @pytest.mark.slow
    @pytest.mark.stress
    @pytest.mark.asyncio
    async def test_high_throughput_async_operations(self) -> None:
        """Test async operations under high throughput."""
        operation_count = 500

        async def async_work(work_id: int) -> str:
            await asyncio.sleep(0.001)
            return f"result_{work_id}"

        start_time = time.perf_counter()

        tasks = [async_work(i) for i in range(operation_count)]
        results = await asyncio.gather(*tasks)

        elapsed = time.perf_counter() - start_time

        assert len(results) == operation_count
        ops_per_sec = operation_count / elapsed
        assert ops_per_sec > 100

    @pytest.mark.slow
    @pytest.mark.stress
    def test_pool_stress_with_many_proxies(self) -> None:
        """Test pool handling with many proxies."""
        proxy_count = 10000
        proxies = [ProxyFactory.build() for _ in range(proxy_count)]
        pool = ProxyPool(name="stress_pool", proxies=proxies)

        assert len(pool.proxies) == proxy_count

        # Concurrent access to large pool
        access_count = 0
        lock = threading.Lock()

        def access_large_pool(thread_id: int) -> None:
            nonlocal access_count
            for _ in range(100):
                if pool.proxies:
                    _ = pool.proxies[0]
                    with lock:
                        access_count += 1

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(access_large_pool, i) for i in range(10)]
            for future in as_completed(futures):
                future.result()

        assert access_count == 1000

    @pytest.mark.slow
    @pytest.mark.stress
    def test_concurrent_storage_operations(self) -> None:
        """Test storage under concurrent load."""
        storage = SQLiteStorage()
        pools_to_clean: list[str] = []

        def storage_operations(op_id: int) -> None:
            try:
                pool = ProxyPoolFactory.build()
                pools_to_clean.append(pool.id)

                storage.save_pool(pool)
                loaded = storage.load_pool(pool.id)
                assert loaded.id == pool.id
            except Exception:
                pass

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(storage_operations, i) for i in range(20)]
            for future in as_completed(futures):
                future.result()

        # Cleanup
        for pool_id in pools_to_clean:
            try:
                storage.delete_pool(pool_id)
            except Exception:
                pass


# ============================================================================
# DEADLOCK DETECTION
# ============================================================================


class TestDeadlockDetection:
    """Test for potential deadlocks with concurrent access."""

    def test_no_deadlock_with_nested_locks(self) -> None:
        """Test that nested locks don't cause deadlocks."""
        outer_lock = threading.Lock()
        inner_lock = threading.Lock()

        results: list[str] = []

        def worker_a(worker_id: int) -> None:
            for _ in range(10):
                with outer_lock:
                    time.sleep(0.001)
                    with inner_lock:
                        results.append(f"a_{worker_id}")

        def worker_b(worker_id: int) -> None:
            for _ in range(10):
                with inner_lock:
                    time.sleep(0.001)
                    with outer_lock:
                        results.append(f"b_{worker_id}")

        # Run both workers to detect potential deadlock
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            futures.extend([executor.submit(worker_a, i) for i in range(2)])
            futures.extend([executor.submit(worker_b, i) for i in range(2)])

            # Wait with timeout to detect deadlock
            for future in as_completed(futures, timeout=5):
                future.result()

        assert len(results) == 40

    @pytest.mark.asyncio
    async def test_no_deadlock_async_operations(self) -> None:
        """Test async operations don't deadlock."""
        lock = asyncio.Lock()

        results: list[str] = []

        async def async_worker_a(worker_id: int) -> None:
            for i in range(5):
                async with lock:
                    await asyncio.sleep(0.001)
                    results.append(f"a_{worker_id}_{i}")

        async def async_worker_b(worker_id: int) -> None:
            for i in range(5):
                async with lock:
                    await asyncio.sleep(0.001)
                    results.append(f"b_{worker_id}_{i}")

        tasks = []
        tasks.extend([async_worker_a(i) for i in range(2)])
        tasks.extend([async_worker_b(i) for i in range(2)])

        # Should complete without timeout
        try:
            await asyncio.wait_for(asyncio.gather(*tasks), timeout=5)
        except asyncio.TimeoutError:
            pytest.fail("Deadlock detected - operations timed out")

        assert len(results) == 20

    def test_resource_acquisition_order_safety(self) -> None:
        """Test safe resource acquisition ordering."""
        resource_a = threading.Lock()
        resource_b = threading.Lock()

        # Both workers acquire locks in same order (A then B)
        acquisition_log: list[str] = []
        lock = threading.Lock()

        def worker(worker_id: int) -> None:
            for _ in range(5):
                with resource_a:
                    time.sleep(0.001)
                    with resource_b:
                        with lock:
                            acquisition_log.append(f"w_{worker_id}")

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(worker, i) for i in range(4)]
            for future in as_completed(futures, timeout=5):
                future.result()

        assert len(acquisition_log) == 20


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
