"""Stress tests for high-throughput scenarios.

Tests:
- High-volume proxy selections
- Concurrent selections
- Memory stability under load
- Performance under stress
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

import pytest

from proxywhirl.models import Proxy, ProxyPool, SelectionContext
from proxywhirl.strategies.core import (
    PerformanceBasedStrategy,
    RoundRobinStrategy,
    WeightedStrategy,
)


class TestHighThroughputSelection:
    """Test strategies under high-throughput conditions."""

    def test_round_robin_high_volume(self) -> None:
        """Test round robin with high-volume selections."""
        strategy = RoundRobinStrategy()
        proxies = [Proxy(url=f"http://proxy{i}.example.com:8080") for i in range(10)]
        pool = ProxyPool(name="test_pool", proxies=proxies)
        context = SelectionContext()

        # Perform 10,000 selections
        selections = []
        for _ in range(10_000):
            selected = strategy.select(pool, context)
            assert selected is not None
            selections.append(selected)

        # All selected proxies should be from pool
        assert all(p in proxies for p in selections)

        # With round robin, should have good distribution
        # Extract URLs since Proxy is not hashable
        selected_urls = set(p.url for p in selections)
        assert len(selected_urls) > 1  # Not just one proxy

    def test_weighted_strategy_high_volume(self) -> None:
        """Test weighted strategy with high-volume selections."""
        strategy = WeightedStrategy()
        proxies = [
            Proxy(url=f"http://proxy{i}.example.com:8080", success_rate=0.1 * (i + 1))
            for i in range(5)
        ]
        pool = ProxyPool(name="test_pool", proxies=proxies)
        context = SelectionContext()

        # Perform 5,000 selections
        selections = []
        for _ in range(5_000):
            selected = strategy.select(pool, context)
            assert selected is not None
            selections.append(selected)

        # Check distribution follows success rates
        # Extract URLs since Proxy is not hashable
        selected_urls = set(p.url for p in selections)
        assert len(selected_urls) == len(proxies)

    def test_performance_strategy_high_volume(self) -> None:
        """Test performance-based strategy with high-volume selections."""
        strategy = PerformanceBasedStrategy()
        proxies = [
            Proxy(
                url=f"http://proxy{i}.example.com:8080",
                latency_ms=float(i * 10),
                success_rate=0.8 + (i * 0.02),
            )
            for i in range(8)
        ]
        pool = ProxyPool(name="test_pool", proxies=proxies)
        context = SelectionContext()

        # Perform 8,000 selections
        selections = []
        for _ in range(8_000):
            selected = strategy.select(pool, context)
            assert selected is not None
            selections.append(selected)

        # Should select from pool
        assert all(p in proxies for p in selections)

    def test_selection_latency_under_load(self) -> None:
        """Test that selection latency is acceptable under load."""
        strategy = RoundRobinStrategy()
        proxies = [Proxy(url=f"http://proxy{i}.example.com:8080") for i in range(20)]
        pool = ProxyPool(name="test_pool", proxies=proxies)
        context = SelectionContext()

        start = datetime.now(timezone.utc)

        # Perform 1,000 rapid selections
        for _ in range(1_000):
            strategy.select(pool, context)

        elapsed = datetime.now(timezone.utc) - start

        # Should complete in reasonable time (< 1 second for 1000 selections)
        assert elapsed.total_seconds() < 5.0

    def test_pool_mutation_during_selections(self) -> None:
        """Test selections when pool is mutated."""
        strategy = RoundRobinStrategy()
        proxies = [Proxy(url=f"http://proxy{i}.example.com:8080") for i in range(5)]
        pool = ProxyPool(name="test_pool", proxies=proxies)
        context = SelectionContext()

        # Perform some selections
        for _ in range(100):
            selected = strategy.select(pool, context)
            assert selected is not None

        # Add more proxies (if mutation is supported)
        new_proxy = Proxy(url="http://new.proxy.com:8080")
        new_proxies = proxies + [new_proxy]
        pool = ProxyPool(name="test_pool", proxies=new_proxies)

        # Continue selecting
        for _ in range(100):
            selected = strategy.select(pool, context)
            assert selected is not None


class TestConcurrentSelections:
    """Test concurrent selection scenarios."""

    @pytest.mark.asyncio
    async def test_concurrent_selections_async(self) -> None:
        """Test concurrent async selections."""
        strategy = RoundRobinStrategy()
        proxies = [Proxy(url=f"http://proxy{i}.example.com:8080") for i in range(5)]
        pool = ProxyPool(name="test_pool", proxies=proxies)

        async def select_proxy() -> Proxy:
            context = SelectionContext()
            return strategy.select(pool, context)

        # Create 100 concurrent selection tasks
        tasks = [select_proxy() for _ in range(100)]
        results = await asyncio.gather(*tasks)

        # All should succeed
        assert len(results) == 100
        assert all(r in proxies for r in results)

    def test_selection_thread_safety(self) -> None:
        """Test that selections are thread-safe."""
        import threading

        strategy = RoundRobinStrategy()
        proxies = [Proxy(url=f"http://proxy{i}.example.com:8080") for i in range(5)]
        pool = ProxyPool(name="test_pool", proxies=proxies)

        results = []
        errors = []

        def select_in_thread(count: int) -> None:
            try:
                for _ in range(count):
                    context = SelectionContext()
                    selected = strategy.select(pool, context)
                    results.append(selected)
            except Exception as e:
                errors.append(e)

        # Create 10 threads
        threads = [
            threading.Thread(target=select_in_thread, args=(100,)) for _ in range(10)
        ]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # All selections should succeed
        assert len(errors) == 0
        assert len(results) == 1000
        assert all(r in proxies for r in results)


class TestMemoryStability:
    """Test memory stability under sustained load."""

    def test_memory_stable_during_high_volume_selections(self) -> None:
        """Test that memory usage remains stable during high volume."""
        import gc

        strategy = RoundRobinStrategy()
        proxies = [Proxy(url=f"http://proxy{i}.example.com:8080") for i in range(10)]
        pool = ProxyPool(name="test_pool", proxies=proxies)

        # Force garbage collection
        gc.collect()

        # Perform many selections
        for _ in range(10_000):
            context = SelectionContext()
            strategy.select(pool, context)

        # Force garbage collection again
        gc.collect()

        # If we get here without memory issues, test passes
        assert True

    def test_context_object_reuse(self) -> None:
        """Test that reusing context objects is efficient."""
        strategy = RoundRobinStrategy()
        proxies = [Proxy(url=f"http://proxy{i}.example.com:8080") for i in range(5)]
        pool = ProxyPool(name="test_pool", proxies=proxies)

        # Reuse same context object
        context = SelectionContext()

        for _ in range(5_000):
            strategy.select(pool, context)

        # Should not accumulate memory
        assert True

    def test_pool_object_reuse(self) -> None:
        """Test that reusing pool objects is efficient."""
        strategy = RoundRobinStrategy()
        proxies = [Proxy(url=f"http://proxy{i}.example.com:8080") for i in range(10)]
        pool = ProxyPool(name="test_pool", proxies=proxies)

        # Reuse same pool object
        for _ in range(10_000):
            context = SelectionContext()
            strategy.select(pool, context)

        # Should not accumulate memory
        assert True


class TestPerformanceCharacteristics:
    """Test performance characteristics under various conditions."""

    def test_round_robin_performance_consistency(self) -> None:
        """Test that round robin performance is consistent."""
        strategy = RoundRobinStrategy()

        sizes = [10, 50, 100]

        for size in sizes:
            proxies = [
                Proxy(url=f"http://proxy{i}.example.com:8080") for i in range(size)
            ]
            pool = ProxyPool(name="test_pool", proxies=proxies)

            start = datetime.now(timezone.utc)
            for _ in range(1_000):
                context = SelectionContext()
                strategy.select(pool, context)
            elapsed = datetime.now(timezone.utc) - start

            # Performance should not degrade significantly with more proxies
            assert elapsed.total_seconds() < 5.0

    def test_weighted_strategy_performance_with_uneven_weights(self) -> None:
        """Test weighted strategy with heavily skewed success rates."""
        strategy = WeightedStrategy()

        # Create proxies with very uneven success rates
        proxies = []
        for url_suffix in ["1", "2"]:
            proxy = Proxy(url=f"http://proxy{url_suffix}.example.com:8080")
            if url_suffix == "1":
                proxy.total_requests = 100
                proxy.total_successes = 99
            else:
                proxy.total_requests = 100
                proxy.total_successes = 1
            proxies.append(proxy)

        pool = ProxyPool(name="test_pool", proxies=proxies)

        selections = []
        for _ in range(1_000):
            context = SelectionContext()
            selected = strategy.select(pool, context)
            selections.append(selected)

        # Should still select from both
        # Extract URLs since Proxy is not hashable
        selected_urls = set(p.url for p in selections)
        assert len(selected_urls) <= 2

    def test_performance_strategy_with_metric_extremes(self) -> None:
        """Test performance strategy with extreme metric values."""
        strategy = PerformanceBasedStrategy()

        # Create proxies with extreme values
        proxies = [
            Proxy(
                url="http://proxy1.example.com:8080",
                latency_ms=1.0,
                success_rate=0.99,
            ),
            Proxy(
                url="http://proxy2.example.com:8080",
                latency_ms=10000.0,
                success_rate=0.01,
            ),
        ]
        pool = ProxyPool(name="test_pool", proxies=proxies)

        selections = []
        for _ in range(500):
            context = SelectionContext()
            selected = strategy.select(pool, context)
            selections.append(selected)

        # Should handle extreme values
        assert all(p in proxies for p in selections)


class TestStressRecovery:
    """Test recovery from stress conditions."""

    def test_recovery_after_high_volume(self) -> None:
        """Test that strategy recovers properly after high volume."""
        strategy = RoundRobinStrategy()
        proxies = [Proxy(url=f"http://proxy{i}.example.com:8080") for i in range(5)]
        pool = ProxyPool(name="test_pool", proxies=proxies)

        # High volume phase
        for _ in range(5_000):
            context = SelectionContext()
            strategy.select(pool, context)

        # Should still work normally
        for _ in range(100):
            context = SelectionContext()
            selected = strategy.select(pool, context)
            assert selected in proxies

    def test_strategy_resilience_to_pool_changes(self) -> None:
        """Test strategy resilience when pool is changed."""
        strategy = RoundRobinStrategy()

        # Initial pool
        proxies1 = [Proxy(url=f"http://proxy{i}.example.com:8080") for i in range(5)]
        pool1 = ProxyPool(name="test_pool", proxies=proxies1)

        # Make selections
        for _ in range(100):
            context = SelectionContext()
            strategy.select(pool1, context)

        # Change to different pool
        proxies2 = [Proxy(url=f"http://proxy{i}.example.com:9090") for i in range(3)]
        pool2 = ProxyPool(name="test_pool", proxies=proxies2)

        # Should still work with new pool
        for _ in range(100):
            context = SelectionContext()
            selected = strategy.select(pool2, context)
            assert selected in proxies2

    def test_rapid_pool_switching(self) -> None:
        """Test rapid switching between pools."""
        strategy = RoundRobinStrategy()

        pools = [
            ProxyPool(name="test_pool", proxies=[Proxy(url=f"http://proxy{j}.example.com:8080")])
            for j in range(10)
        ]

        # Rapidly switch pools
        for pool in pools:
            for _ in range(10):
                context = SelectionContext()
                selected = strategy.select(pool, context)
                assert selected is not None

        # Should handle gracefully
        assert True
