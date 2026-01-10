"""
Benchmark tests for AsyncProxyRotator performance.

These tests validate performance requirements for the async hot path:
- Async proxy selection latency
- LRU client pool operations
- Concurrent async throughput
- Async circuit breaker operations

Performance Targets:
- SC-007: Strategy selection overhead <5ms
- SC-008: Support 10,000 concurrent requests without deadlocks
- SC-010: Async operations should not block event loop
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncGenerator
from typing import Any

import httpx
import pytest

from proxywhirl.async_client import AsyncProxyRotator, LRUAsyncClientPool
from proxywhirl.circuit_breaker import CircuitBreaker
from proxywhirl.circuit_breaker_async import AsyncCircuitBreaker
from proxywhirl.models import (
    HealthStatus,
    Proxy,
    ProxyPool,
)

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def sample_proxies() -> list[Proxy]:
    """Create a list of 50 healthy proxies for benchmarking."""
    proxies = []
    for i in range(50):
        proxy = Proxy(
            url=f"http://proxy{i}.example.com:8080",
            health_status=HealthStatus.HEALTHY,
            ema_alpha=0.2,
        )
        # Initialize with EMA data
        proxy.start_request()
        proxy.complete_request(success=True, response_time_ms=100.0)
        proxies.append(proxy)
    return proxies


@pytest.fixture
def large_proxy_pool(sample_proxies: list[Proxy]) -> ProxyPool:
    """Create a pool with 50 proxies."""
    pool = ProxyPool(name="benchmark-pool", proxies=sample_proxies)
    return pool


@pytest.fixture
def async_rotator_sync(sample_proxies: list[Proxy]) -> AsyncProxyRotator:
    """Create an AsyncProxyRotator without context manager (for sync benchmark tests)."""
    return AsyncProxyRotator(proxies=sample_proxies)


@pytest.fixture
async def async_rotator(sample_proxies: list[Proxy]) -> AsyncGenerator[AsyncProxyRotator, None]:
    """Create an AsyncProxyRotator with context manager (for async tests)."""
    rotator = AsyncProxyRotator(proxies=sample_proxies)
    async with rotator:
        yield rotator


# ============================================================================
# ASYNC PROXY SELECTION BENCHMARKS (pytest-benchmark)
# ============================================================================


class TestAsyncProxySelectionBenchmarks:
    """Benchmark tests for async proxy selection performance (SC-007)."""

    def test_async_get_proxy_latency(
        self, benchmark: Any, async_rotator_sync: AsyncProxyRotator
    ) -> None:
        """
        Benchmark: Async proxy selection latency using pytest-benchmark.

        Target: <5ms per selection (SC-007)
        """
        rotator = async_rotator_sync

        def get_proxy_sync() -> Proxy:
            """Wrapper to run async function synchronously for benchmark fixture."""
            return asyncio.get_event_loop().run_until_complete(rotator.get_proxy())

        # Benchmark the selection operation
        result = benchmark(get_proxy_sync)

        assert result is not None
        assert isinstance(result, Proxy)

    def test_async_get_proxy_with_circuit_breaker_check(
        self, benchmark: Any, async_rotator_sync: AsyncProxyRotator
    ) -> None:
        """
        Benchmark: Async proxy selection with circuit breaker filtering.

        Target: <5ms per selection (SC-007)
        """
        rotator = async_rotator_sync

        def get_proxy_with_cb() -> Proxy:
            return asyncio.get_event_loop().run_until_complete(rotator.get_proxy())

        result = benchmark(get_proxy_with_cb)

        assert result is not None
        assert isinstance(result, Proxy)


# ============================================================================
# LRU CLIENT POOL BENCHMARKS (pytest-benchmark)
# ============================================================================


class TestLRUClientPoolBenchmarks:
    """Benchmark tests for LRU async client pool operations."""

    @pytest.fixture
    def populated_client_pool(self) -> LRUAsyncClientPool:
        """Create and populate an LRU client pool."""
        pool = LRUAsyncClientPool(maxsize=100)

        async def populate():
            for i in range(50):
                client = httpx.AsyncClient()
                await pool.put(f"proxy-{i}", client)

        asyncio.get_event_loop().run_until_complete(populate())
        return pool

    def test_client_pool_get_latency(
        self, benchmark: Any, populated_client_pool: LRUAsyncClientPool
    ) -> None:
        """
        Benchmark: LRU client pool GET operation latency.

        Target: <1ms for cache hit
        """
        pool = populated_client_pool
        target_key = "proxy-25"  # Middle entry

        def get_client() -> httpx.AsyncClient | None:
            return asyncio.get_event_loop().run_until_complete(pool.get(target_key))

        result = benchmark(get_client)
        assert result is not None

    def test_client_pool_put_latency(self, benchmark: Any) -> None:
        """
        Benchmark: LRU client pool PUT operation latency.

        Target: <2ms for put operation (no eviction)
        """
        pool = LRUAsyncClientPool(maxsize=100)
        counter = [0]

        def put_client() -> None:
            client = httpx.AsyncClient()
            key = f"bench-proxy-{counter[0]}"
            counter[0] += 1
            asyncio.get_event_loop().run_until_complete(pool.put(key, client))

        benchmark(put_client)

        # Cleanup
        asyncio.get_event_loop().run_until_complete(pool.clear())


# ============================================================================
# CIRCUIT BREAKER BENCHMARKS (pytest-benchmark)
# ============================================================================


class TestAsyncCircuitBreakerBenchmarks:
    """Benchmark tests for async circuit breaker operations."""

    def test_async_circuit_breaker_check_latency(self, benchmark: Any) -> None:
        """
        Benchmark: Async circuit breaker should_attempt_request latency.

        Target: <1ms per check
        """
        cb = AsyncCircuitBreaker(proxy_id="bench-proxy")

        def check_cb() -> bool:
            return asyncio.get_event_loop().run_until_complete(cb.should_attempt_request())

        result = benchmark(check_cb)
        assert result is True

    def test_async_circuit_breaker_record_success_latency(self, benchmark: Any) -> None:
        """
        Benchmark: Async circuit breaker record_success latency.

        Target: <1ms per record
        """
        cb = AsyncCircuitBreaker(proxy_id="bench-proxy")

        def record_success() -> None:
            asyncio.get_event_loop().run_until_complete(cb.record_success())

        benchmark(record_success)

    def test_async_circuit_breaker_record_failure_latency(self, benchmark: Any) -> None:
        """
        Benchmark: Async circuit breaker record_failure latency.

        Target: <2ms per record (includes deque operations)
        """
        cb = AsyncCircuitBreaker(
            proxy_id="bench-proxy",
            failure_threshold=10000,  # High threshold to avoid state transitions
        )

        def record_failure() -> None:
            asyncio.get_event_loop().run_until_complete(cb.record_failure())

        benchmark(record_failure)

    def test_sync_circuit_breaker_check_latency(self, benchmark: Any) -> None:
        """
        Benchmark: Sync circuit breaker should_attempt_request latency.

        Target: <1ms per check (reference for async comparison)
        """
        cb = CircuitBreaker(proxy_id="bench-proxy")

        result = benchmark(cb.should_attempt_request)
        assert result is True


# ============================================================================
# STRATEGY HOT-SWAP BENCHMARKS (pytest-benchmark)
# ============================================================================


class TestStrategyHotSwapBenchmarks:
    """Benchmark tests for strategy hot-swap performance (SC-009)."""

    def test_strategy_hot_swap_latency(
        self, benchmark: Any, async_rotator_sync: AsyncProxyRotator
    ) -> None:
        """
        Benchmark: Strategy hot-swap latency.

        Target: <100ms for hot-swap completion (SC-009)
        """
        rotator = async_rotator_sync
        counter = [0]
        strategies = ["round-robin", "random", "least-used", "weighted"]

        def swap_strategy() -> None:
            strategy = strategies[counter[0] % len(strategies)]
            counter[0] += 1
            rotator.set_strategy(strategy)

        benchmark(swap_strategy)


# ============================================================================
# POOL STATS BENCHMARKS (pytest-benchmark)
# ============================================================================


class TestPoolStatsBenchmarks:
    """Benchmark tests for pool statistics operations."""

    def test_get_pool_stats_latency(
        self, benchmark: Any, async_rotator_sync: AsyncProxyRotator
    ) -> None:
        """
        Benchmark: get_pool_stats latency.

        Target: <10ms for stats calculation
        """
        rotator = async_rotator_sync

        result = benchmark(rotator.get_pool_stats)
        assert "total_proxies" in result

    def test_get_statistics_latency(
        self, benchmark: Any, async_rotator_sync: AsyncProxyRotator
    ) -> None:
        """
        Benchmark: get_statistics (comprehensive) latency.

        Target: <20ms for full stats calculation
        """
        rotator = async_rotator_sync

        result = benchmark(rotator.get_statistics)
        assert "total_proxies" in result
        assert "source_breakdown" in result


# ============================================================================
# CONCURRENT ASYNC THROUGHPUT STRESS TESTS (Manual timing)
# ============================================================================


class TestConcurrentAsyncThroughputStress:
    """Stress tests for concurrent async throughput (SC-008).

    These tests don't use pytest-benchmark fixture because they measure
    concurrent/parallel operations rather than single function calls.
    Run with: pytest tests/benchmarks/test_async_rotator_benchmark.py -v
    Skip with: pytest --benchmark-only (these will be skipped)
    """

    async def test_concurrent_get_proxy_throughput_100(
        self, async_rotator_sync: AsyncProxyRotator
    ) -> None:
        """
        Stress test: 100 concurrent async proxy selections.

        Tests basic concurrency without overwhelming the system.
        """
        rotator = async_rotator_sync

        async def select_proxy() -> Proxy:
            return await rotator.get_proxy()

        # Execute 100 concurrent selections
        start = time.perf_counter()
        tasks = [select_proxy() for _ in range(100)]
        results = await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        # All should complete successfully
        assert len(results) == 100
        assert all(isinstance(p, Proxy) for p in results)

        # Total time should be reasonable (not sequential)
        assert elapsed < 0.5, f"100 concurrent selections took {elapsed:.3f}s, should be <0.5s"

    async def test_concurrent_get_proxy_throughput_1000(
        self, async_rotator_sync: AsyncProxyRotator
    ) -> None:
        """
        Stress test: 1,000 concurrent async proxy selections.

        Tests medium-level concurrency.
        """
        rotator = async_rotator_sync

        async def select_proxy() -> Proxy:
            return await rotator.get_proxy()

        # Execute 1,000 concurrent selections
        start = time.perf_counter()
        tasks = [select_proxy() for _ in range(1_000)]
        results = await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        assert len(results) == 1_000
        assert all(isinstance(p, Proxy) for p in results)

        # Should complete in reasonable time
        assert elapsed < 2.0, f"1,000 concurrent selections took {elapsed:.3f}s, should be <2s"

    async def test_concurrent_get_proxy_throughput_10k(
        self, async_rotator_sync: AsyncProxyRotator
    ) -> None:
        """
        Stress test: 10,000 concurrent async proxy selections (SC-008).

        Validates thread safety and no deadlocks under high concurrency.
        """
        rotator = async_rotator_sync

        async def select_proxy() -> Proxy:
            return await rotator.get_proxy()

        # Execute 10,000 concurrent selections
        start = time.perf_counter()
        tasks = [select_proxy() for _ in range(10_000)]
        results = await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        # All should complete successfully (no deadlocks)
        assert len(results) == 10_000
        assert all(isinstance(p, Proxy) for p in results)

        # Log performance for analysis
        throughput = 10_000 / elapsed
        print(f"\n10k concurrent selections: {elapsed:.3f}s ({throughput:.0f} ops/sec)")

        # Should complete without timeout (generous limit for CI)
        assert (
            elapsed < 10.0
        ), f"10,000 concurrent selections took {elapsed:.3f}s, should be <10s (no deadlocks)"

    async def test_batched_concurrent_throughput(
        self, async_rotator_sync: AsyncProxyRotator
    ) -> None:
        """
        Stress test: Batched concurrent selections (real-world pattern).

        Tests repeated batches of concurrent requests.
        """
        rotator = async_rotator_sync
        batch_size = 100
        num_batches = 50

        async def batch_select() -> list[Proxy]:
            tasks = [rotator.get_proxy() for _ in range(batch_size)]
            return await asyncio.gather(*tasks)

        # Execute batches
        start = time.perf_counter()
        all_results = []
        for _ in range(num_batches):
            batch_results = await batch_select()
            all_results.extend(batch_results)
        elapsed = time.perf_counter() - start

        total_requests = batch_size * num_batches
        assert len(all_results) == total_requests
        assert all(isinstance(p, Proxy) for p in all_results)

        avg_batch_time_ms = (elapsed / num_batches) * 1000
        assert (
            avg_batch_time_ms < 100.0
        ), f"Avg batch time {avg_batch_time_ms:.3f}ms, should be <100ms"

    async def test_concurrent_circuit_breaker_checks(self) -> None:
        """
        Stress test: Concurrent async circuit breaker checks.

        Tests RWLock performance under contention.
        """
        cb = AsyncCircuitBreaker(proxy_id="bench-proxy")

        async def check_cb() -> bool:
            return await cb.should_attempt_request()

        # Execute 1000 concurrent checks
        start = time.perf_counter()
        tasks = [check_cb() for _ in range(1_000)]
        results = await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

        assert all(r is True for r in results)

        # Should handle concurrency efficiently
        assert elapsed < 1.0, f"1000 concurrent CB checks took {elapsed:.3f}s, should be <1s"

    async def test_strategy_swap_during_concurrent_requests(
        self, async_rotator_sync: AsyncProxyRotator
    ) -> None:
        """
        Stress test: Strategy hot-swap during concurrent request processing.

        Validates that hot-swap doesn't cause request failures.
        """
        rotator = async_rotator_sync
        errors: list[Exception] = []

        async def make_requests() -> None:
            for _ in range(100):
                try:
                    await rotator.get_proxy()
                    await asyncio.sleep(0.001)  # Small delay
                except Exception as e:
                    errors.append(e)

        async def swap_strategies() -> None:
            strategies = ["round-robin", "random", "least-used"]
            for i in range(10):
                rotator.set_strategy(strategies[i % len(strategies)])
                await asyncio.sleep(0.01)

        # Run requests and swaps concurrently
        start = time.perf_counter()
        await asyncio.gather(make_requests(), swap_strategies())
        elapsed = time.perf_counter() - start

        # No errors should occur
        assert len(errors) == 0, f"Errors during concurrent swap: {errors}"

        # Should complete reasonably quickly
        assert elapsed < 2.0, f"Concurrent requests with swaps took {elapsed:.3f}s, should be <2s"


# ============================================================================
# LRU CLIENT POOL STRESS TESTS (Manual timing)
# ============================================================================


class TestLRUClientPoolStress:
    """Stress tests for LRU client pool under high load."""

    async def test_client_pool_eviction_under_load(self) -> None:
        """
        Stress test: LRU eviction performance under load.

        Tests that eviction doesn't cause delays during high throughput.
        """
        # Create a small pool to trigger frequent evictions
        pool = LRUAsyncClientPool(maxsize=10)

        # Perform many puts that trigger evictions
        iterations = 100
        start = time.perf_counter()
        for i in range(iterations):
            client = httpx.AsyncClient()
            await pool.put(f"stress-{i}", client)
        elapsed = time.perf_counter() - start

        avg_time_ms = (elapsed / iterations) * 1000

        # Allow more time for eviction operations (involves async close)
        assert (
            avg_time_ms < 20.0
        ), f"PUT with eviction averaged {avg_time_ms:.3f}ms, should be <20ms"

        # Cleanup
        await pool.clear()

    async def test_client_pool_concurrent_access(self) -> None:
        """
        Stress test: Concurrent get/put operations.

        Tests lock contention under concurrent access.
        """
        pool = LRUAsyncClientPool(maxsize=50)

        # Pre-populate
        for i in range(25):
            client = httpx.AsyncClient()
            await pool.put(f"initial-{i}", client)

        async def reader() -> int:
            count = 0
            for i in range(100):
                result = await pool.get(f"initial-{i % 25}")
                if result is not None:
                    count += 1
            return count

        async def writer() -> None:
            for i in range(50):
                client = httpx.AsyncClient()
                await pool.put(f"writer-{i}", client)

        # Run readers and writers concurrently
        start = time.perf_counter()
        results = await asyncio.gather(
            reader(),
            reader(),
            reader(),
            writer(),
        )
        elapsed = time.perf_counter() - start

        # Readers should have gotten some hits
        read_results = results[:3]
        assert all(r > 0 for r in read_results)

        # Should complete reasonably fast
        assert elapsed < 2.0, f"Concurrent pool access took {elapsed:.3f}s, should be <2s"

        # Cleanup
        await pool.clear()


# ============================================================================
# ASYNC LATENCY VALIDATION TESTS (Assertion-based)
# ============================================================================


class TestAsyncLatencyValidation:
    """Tests that validate latency requirements with assertions.

    These tests perform manual timing and assert latency targets.
    Use these for CI validation without pytest-benchmark overhead.
    """

    async def test_async_proxy_selection_latency_target(
        self, async_rotator_sync: AsyncProxyRotator
    ) -> None:
        """
        Validate: Async proxy selection meets <5ms target (SC-007).
        """
        rotator = async_rotator_sync
        iterations = 1000

        # Warm-up
        for _ in range(10):
            await rotator.get_proxy()

        # Benchmark
        start = time.perf_counter()
        for _ in range(iterations):
            proxy = await rotator.get_proxy()
            assert proxy is not None
        elapsed = time.perf_counter() - start

        avg_time_ms = (elapsed / iterations) * 1000
        assert avg_time_ms < 5.0, f"Async get_proxy took {avg_time_ms:.3f}ms, should be <5ms"

    async def test_lru_pool_get_latency_target(self) -> None:
        """
        Validate: LRU pool GET meets <1ms target.
        """
        pool = LRUAsyncClientPool(maxsize=100)

        # Populate
        for i in range(50):
            client = httpx.AsyncClient()
            await pool.put(f"proxy-{i}", client)

        iterations = 1000
        target_key = "proxy-25"

        start = time.perf_counter()
        for _ in range(iterations):
            result = await pool.get(target_key)
            assert result is not None
        elapsed = time.perf_counter() - start

        avg_time_ms = (elapsed / iterations) * 1000
        assert avg_time_ms < 1.0, f"LRU GET took {avg_time_ms:.3f}ms, should be <1ms"

        await pool.clear()

    async def test_circuit_breaker_check_latency_target(self) -> None:
        """
        Validate: Circuit breaker check meets <1ms target.
        """
        cb = AsyncCircuitBreaker(proxy_id="bench-proxy")
        iterations = 1000

        start = time.perf_counter()
        for _ in range(iterations):
            result = await cb.should_attempt_request()
            assert result is True
        elapsed = time.perf_counter() - start

        avg_time_ms = (elapsed / iterations) * 1000
        assert avg_time_ms < 1.0, f"CB check took {avg_time_ms:.3f}ms, should be <1ms"
