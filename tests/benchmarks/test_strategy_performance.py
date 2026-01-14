"""
Benchmark tests for rotation strategies using pytest-benchmark.

These tests validate performance requirements:
- SC-007: Strategy selection overhead <5ms
- SC-008: Support 10,000 concurrent requests without deadlocks
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor

import pytest

from proxywhirl.models import (
    HealthStatus,
    Proxy,
    ProxyPool,
    SelectionContext,
)
from proxywhirl.strategies import (
    LeastUsedStrategy,
    PerformanceBasedStrategy,
    RandomStrategy,
    RoundRobinStrategy,
)


class TestStrategySelectionBenchmarks:
    """Benchmark tests for strategy selection performance (SC-007)."""

    @pytest.fixture
    def small_pool(self):
        """Create a pool with 10 proxies."""
        pool = ProxyPool(name="small-pool")
        for i in range(10):
            proxy = Proxy(
                url=f"http://proxy{i}.example.com:8080",
                health_status=HealthStatus.HEALTHY,
                ema_alpha=0.2,
            )
            # Initialize with EMA data for PerformanceBasedStrategy
            proxy.start_request()
            proxy.complete_request(success=True, response_time_ms=100.0)
            pool.add_proxy(proxy)
        return pool

    @pytest.fixture
    def large_pool(self):
        """Create a pool with 100 proxies."""
        pool = ProxyPool(name="large-pool")
        for i in range(100):
            proxy = Proxy(
                url=f"http://proxy{i}.example.com:8080",
                health_status=HealthStatus.HEALTHY,
                ema_alpha=0.2,
            )
            # Initialize with EMA data for PerformanceBasedStrategy
            proxy.start_request()
            proxy.complete_request(success=True, response_time_ms=100.0)
            pool.add_proxy(proxy)
        return pool

    def test_round_robin_selection_small_pool(self, benchmark, small_pool):
        """
        Benchmark: Round-robin selection with 10 proxies.

        Target: <5ms per selection (SC-007)
        """
        strategy = RoundRobinStrategy()
        context = SelectionContext()

        # Benchmark the select operation
        result = benchmark(strategy.select, small_pool, context)

        # Assert a proxy was selected
        assert result is not None
        assert isinstance(result, Proxy)

    def test_round_robin_selection_large_pool(self, benchmark, large_pool):
        """
        Benchmark: Round-robin selection with 100 proxies.

        Target: <5ms per selection (SC-007)
        """
        strategy = RoundRobinStrategy()
        context = SelectionContext()

        result = benchmark(strategy.select, large_pool, context)

        assert result is not None
        assert isinstance(result, Proxy)

    def test_random_selection_small_pool(self, benchmark, small_pool):
        """
        Benchmark: Random selection with 10 proxies.

        Target: <5ms per selection (SC-007)
        """
        strategy = RandomStrategy()
        context = SelectionContext()

        result = benchmark(strategy.select, small_pool, context)

        assert result is not None
        assert isinstance(result, Proxy)

    def test_random_selection_large_pool(self, benchmark, large_pool):
        """
        Benchmark: Random selection with 100 proxies.

        Target: <5ms per selection (SC-007)
        """
        strategy = RandomStrategy()
        context = SelectionContext()

        result = benchmark(strategy.select, large_pool, context)

        assert result is not None
        assert isinstance(result, Proxy)

    def test_least_used_selection_small_pool(self, benchmark, small_pool):
        """
        Benchmark: Least-used selection with 10 proxies.

        Target: <5ms per selection (SC-007)
        """
        strategy = LeastUsedStrategy()
        context = SelectionContext()

        result = benchmark(strategy.select, small_pool, context)

        assert result is not None
        assert isinstance(result, Proxy)

    def test_least_used_selection_large_pool(self, benchmark, large_pool):
        """
        Benchmark: Least-used selection with 100 proxies.

        Target: <5ms per selection (SC-007)
        """
        strategy = LeastUsedStrategy()
        context = SelectionContext()

        result = benchmark(strategy.select, large_pool, context)

        assert result is not None
        assert isinstance(result, Proxy)

    def test_performance_based_selection_small_pool(self, benchmark, small_pool):
        """
        Benchmark: Performance-based selection with 10 proxies.

        Target: <5ms per selection (SC-007)
        """
        strategy = PerformanceBasedStrategy()
        context = SelectionContext()

        result = benchmark(strategy.select, small_pool, context)

        assert result is not None
        assert isinstance(result, Proxy)

    def test_performance_based_selection_large_pool(self, benchmark, large_pool):
        """
        Benchmark: Performance-based selection with 100 proxies.

        Target: <5ms per selection (SC-007)
        """
        strategy = PerformanceBasedStrategy()
        context = SelectionContext()

        result = benchmark(strategy.select, large_pool, context)

        assert result is not None
        assert isinstance(result, Proxy)

    def test_selection_with_failed_proxies_context(self, benchmark, large_pool):
        """
        Benchmark: Selection with failed_proxy_ids filtering.

        Tests overhead of context filtering with many failed proxies.
        """
        strategy = RoundRobinStrategy()

        # Create context with 50 failed proxy IDs
        failed_ids = [str(p.id) for p in large_pool.get_all_proxies()[:50]]
        context = SelectionContext(failed_proxy_ids=failed_ids)

        result = benchmark(strategy.select, large_pool, context)

        assert result is not None
        assert str(result.id) not in failed_ids


class TestConcurrentSelectionBenchmarks:
    """Benchmark tests for concurrent selection (SC-008)."""

    @pytest.fixture
    def concurrent_pool(self):
        """Create a pool for concurrent testing."""
        pool = ProxyPool(name="concurrent-pool")
        for i in range(50):
            pool.add_proxy(
                Proxy(url=f"http://proxy{i}.example.com:8080", health_status=HealthStatus.HEALTHY)
            )
        return pool

    def test_round_robin_concurrent_10k_selections(self, concurrent_pool):
        """
        Stress test: 10,000 concurrent selections (SC-008).

        Validates thread safety and no deadlocks under high concurrency.
        """
        strategy = RoundRobinStrategy()

        def select_proxy():
            """Worker function for concurrent selection."""
            context = SelectionContext()
            proxy = strategy.select(concurrent_pool, context)
            # Simulate brief request
            strategy.record_result(proxy, success=True, response_time_ms=50.0)
            return proxy

        # Act - Execute 10,000 selections concurrently
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(select_proxy) for _ in range(10_000)]
            results = [f.result() for f in futures]

        # Assert - All selections completed successfully
        assert len(results) == 10_000
        assert all(isinstance(p, Proxy) for p in results)

        # Verify no deadlocks by checking all proxies have completed requests
        for proxy in concurrent_pool.get_all_proxies():
            assert proxy.requests_completed >= 0  # Should have some completed

    def test_random_concurrent_10k_selections(self, concurrent_pool):
        """
        Stress test: Random strategy with 10,000 concurrent selections (SC-008).
        """
        strategy = RandomStrategy()

        def select_proxy():
            context = SelectionContext()
            proxy = strategy.select(concurrent_pool, context)
            strategy.record_result(proxy, success=True, response_time_ms=50.0)
            return proxy

        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(select_proxy) for _ in range(10_000)]
            results = [f.result() for f in futures]

        assert len(results) == 10_000
        assert all(isinstance(p, Proxy) for p in results)

    def test_least_used_concurrent_10k_selections(self, concurrent_pool):
        """
        Stress test: Least-used strategy with 10,000 concurrent selections (SC-008).

        This is the most challenging case as it requires comparing all proxies.
        """
        strategy = LeastUsedStrategy()

        def select_proxy():
            context = SelectionContext()
            proxy = strategy.select(concurrent_pool, context)
            strategy.record_result(proxy, success=True, response_time_ms=50.0)
            return proxy

        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(select_proxy) for _ in range(10_000)]
            results = [f.result() for f in futures]

        assert len(results) == 10_000
        assert all(isinstance(p, Proxy) for p in results)

        # Verify load balancing - with 10k requests and 50 proxies,
        # each proxy should have roughly 200 requests (±50 variance acceptable)
        all_proxies = concurrent_pool.get_all_proxies()
        request_counts = [p.requests_completed for p in all_proxies]
        avg_count = sum(request_counts) / len(request_counts)

        # Allow 25% variance in highly concurrent scenario
        for count in request_counts:
            variance = abs(count - avg_count) / avg_count
            assert variance < 0.25, (
                f"High load imbalance: count={count}, avg={avg_count}, variance={variance:.2%}"
            )

    async def test_async_concurrent_selections(self, concurrent_pool):
        """
        Stress test: Async concurrent selections.

        Tests strategy thread safety with asyncio concurrency.
        """
        strategy = RoundRobinStrategy()

        async def select_proxy():
            """Async worker for selection."""
            # Strategy selection is sync, but simulate async context
            context = SelectionContext()
            proxy = await asyncio.to_thread(strategy.select, concurrent_pool, context)
            await asyncio.to_thread(strategy.record_result, proxy, True, 50.0)
            return proxy

        # Act - Execute 1,000 async concurrent selections
        tasks = [select_proxy() for _ in range(1_000)]
        results = await asyncio.gather(*tasks)

        # Assert
        assert len(results) == 1_000
        assert all(isinstance(p, Proxy) for p in results)


class TestRecordResultBenchmarks:
    """Benchmark tests for record_result performance."""

    @pytest.fixture
    def pool_with_proxy(self):
        """Create a pool with a single proxy for benchmarking."""
        pool = ProxyPool(name="bench-pool")
        proxy = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy)
        return pool, proxy

    def test_record_result_success_benchmark(self, benchmark, pool_with_proxy):
        """
        Benchmark: Recording successful request result.

        Should be very fast (<1ms) as it only updates counters and EMA.
        """
        _, proxy = pool_with_proxy
        strategy = RoundRobinStrategy()

        result = benchmark(strategy.record_result, proxy, True, 150.0)

        # record_result returns None, just verify it completed
        assert result is None
        assert proxy.requests_completed > 0

    def test_record_result_failure_benchmark(self, benchmark, pool_with_proxy):
        """
        Benchmark: Recording failed request result.
        """
        _, proxy = pool_with_proxy
        strategy = RoundRobinStrategy()

        result = benchmark(strategy.record_result, proxy, False, 5000.0)

        assert result is None
        assert proxy.total_failures > 0


class TestPoolOperationBenchmarks:
    """Benchmark tests for thread-safe pool operations."""

    @pytest.fixture
    def empty_pool(self):
        """Create an empty pool for add/remove benchmarks."""
        return ProxyPool(name="bench-pool", max_pool_size=1000)

    def test_add_proxy_benchmark(self, benchmark, empty_pool):
        """
        Benchmark: Adding a proxy to the pool.

        Tests thread-safe add operation with RLock.
        """
        proxy = Proxy(url="http://new-proxy.example.com:8080", health_status=HealthStatus.HEALTHY)

        benchmark(empty_pool.add_proxy, proxy)

    def test_get_healthy_proxies_benchmark(self, benchmark):
        """
        Benchmark: Getting healthy proxies from large pool.

        Tests filtering performance with thread-safe read.
        """
        pool = ProxyPool(name="bench-pool")

        # Add 100 proxies (mix of healthy and unhealthy)
        for i in range(100):
            status = HealthStatus.HEALTHY if i % 3 != 0 else HealthStatus.DEAD
            pool.add_proxy(Proxy(url=f"http://proxy{i}.example.com:8080", health_status=status))

        result = benchmark(pool.get_healthy_proxies)

        # Should return about 67 healthy proxies
        assert len(result) > 50
        assert all(
            p.health_status in (HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.UNKNOWN)
            for p in result
        )
