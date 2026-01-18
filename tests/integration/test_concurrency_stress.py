"""Integration stress tests for concurrent proxy pool modifications.

This module tests the thread-safety of ProxyPool under heavy concurrent load,
including simultaneous add/remove/select operations and strategy switching under
contention.
"""

from __future__ import annotations

import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TYPE_CHECKING

import pytest

from proxywhirl import (
    LeastUsedStrategy,
    PerformanceBasedStrategy,
    Proxy,
    ProxyPool,
    RandomStrategy,
    RoundRobinStrategy,
    WeightedStrategy,
)
from proxywhirl.models import HealthStatus

if TYPE_CHECKING:
    from concurrent.futures import Future


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def stress_pool() -> ProxyPool:
    """Create a ProxyPool with 20 proxies for stress testing."""
    pool = ProxyPool(name="stress-test-pool", max_pool_size=200)
    for i in range(20):
        proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
        proxy.health_status = HealthStatus.HEALTHY
        # Give proxies some initial stats for strategy testing
        proxy.total_requests = random.randint(10, 100)
        proxy.total_successes = random.randint(5, proxy.total_requests)
        proxy.average_response_time_ms = random.uniform(50, 500)
        pool.add_proxy(proxy)
    return pool


@pytest.fixture
def strategy_pool() -> ProxyPool:
    """Create a ProxyPool with varied proxy statistics for strategy testing."""
    pool = ProxyPool(name="strategy-pool", max_pool_size=100)
    # Create proxies with diverse performance characteristics
    for i in range(15):
        proxy = Proxy(url=f"http://strategy-proxy{i}.example.com:8080")
        proxy.health_status = HealthStatus.HEALTHY

        # Create performance tiers
        if i < 5:  # High performers
            proxy.total_requests = 100
            proxy.total_successes = 95
            proxy.average_response_time_ms = 50.0
            proxy.requests_started = 10
        elif i < 10:  # Medium performers
            proxy.total_requests = 100
            proxy.total_successes = 70
            proxy.average_response_time_ms = 200.0
            proxy.requests_started = 50
        else:  # Low performers
            proxy.total_requests = 100
            proxy.total_successes = 40
            proxy.average_response_time_ms = 800.0
            proxy.requests_started = 90

        pool.add_proxy(proxy)
    return pool


# ============================================================================
# CONCURRENT ADD OPERATIONS
# ============================================================================


@pytest.mark.slow
class TestConcurrentAdds:
    """Test concurrent proxy additions to the pool."""

    def test_concurrent_add_100_proxies(self, stress_pool: ProxyPool) -> None:
        """Add 100 proxies concurrently from 10 workers."""
        initial_size = stress_pool.size
        new_proxies = [Proxy(url=f"http://new-proxy{i}.example.com:8080") for i in range(100)]

        def add_proxy_task(proxy: Proxy) -> str:
            """Add a single proxy and return its URL."""
            stress_pool.add_proxy(proxy)
            return proxy.url

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures: list[Future[str]] = [
                executor.submit(add_proxy_task, proxy) for proxy in new_proxies
            ]
            results = [f.result() for f in as_completed(futures)]

        # All proxies should be added
        assert len(results) == 100
        assert stress_pool.size == initial_size + 100

        # Verify no duplicates
        urls = {p.url for p in stress_pool.proxies}
        assert len(urls) == stress_pool.size

    def test_concurrent_add_with_duplicates(self, stress_pool: ProxyPool) -> None:
        """Test that duplicate adds are handled correctly under concurrency."""
        # Create 50 proxies, but submit 100 tasks (each proxy added twice)
        base_proxies = [Proxy(url=f"http://dup-proxy{i}.example.com:8080") for i in range(50)]
        # Duplicate the list
        all_proxies = base_proxies + base_proxies.copy()

        initial_size = stress_pool.size

        def add_proxy_safe(proxy: Proxy) -> bool:
            """Add proxy and return success status."""
            try:
                stress_pool.add_proxy(proxy)
                return True
            except Exception:
                return False

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(add_proxy_safe, proxy) for proxy in all_proxies]
            results = [f.result() for f in as_completed(futures)]

        # Pool should only contain unique proxies
        final_size = stress_pool.size
        assert final_size == initial_size + 50  # Only 50 unique proxies added

        # Verify no URL duplicates
        urls = [p.url for p in stress_pool.proxies]
        assert len(urls) == len(set(urls))

    def test_concurrent_add_respects_max_pool_size(self) -> None:
        """Test that max_pool_size is enforced under concurrent additions."""
        pool = ProxyPool(name="limited-pool", max_pool_size=50)

        # Try to add 100 proxies to a pool limited to 50
        new_proxies = [Proxy(url=f"http://limited{i}.example.com:8080") for i in range(100)]

        successful_adds = []
        failed_adds = []

        def add_with_size_limit(proxy: Proxy) -> bool:
            """Add proxy and return whether it succeeded."""
            try:
                pool.add_proxy(proxy)
                return True
            except ValueError:  # Pool at maximum capacity
                return False

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(add_with_size_limit, proxy) for proxy in new_proxies]
            for future in as_completed(futures):
                if future.result():
                    successful_adds.append(True)
                else:
                    failed_adds.append(True)

        # Pool should be at max capacity
        assert pool.size == 50
        # Some adds should have succeeded, some failed
        assert len(successful_adds) == 50
        assert len(failed_adds) == 50


# ============================================================================
# CONCURRENT REMOVE OPERATIONS
# ============================================================================


@pytest.mark.slow
class TestConcurrentRemoves:
    """Test concurrent proxy removals from the pool."""

    def test_concurrent_remove_50_proxies(self, stress_pool: ProxyPool) -> None:
        """Remove 50% of proxies concurrently from 10 workers."""
        # Get half the proxy IDs to remove
        proxy_ids_to_remove = [p.id for p in stress_pool.proxies[:10]]
        initial_size = stress_pool.size

        def remove_proxy_task(proxy_id: str) -> str:
            """Remove a proxy by ID and return the ID."""
            stress_pool.remove_proxy(proxy_id)
            return str(proxy_id)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(remove_proxy_task, pid) for pid in proxy_ids_to_remove]
            results = [f.result() for f in as_completed(futures)]

        # All removals should complete
        assert len(results) == 10
        assert stress_pool.size == initial_size - 10

        # Verify removed proxies are gone
        remaining_ids = {p.id for p in stress_pool.proxies}
        for removed_id in proxy_ids_to_remove:
            assert removed_id not in remaining_ids

    def test_concurrent_remove_same_proxy(self, stress_pool: ProxyPool) -> None:
        """Test that removing the same proxy concurrently is handled safely."""
        # Get one proxy to remove
        target_proxy = stress_pool.proxies[0]
        target_id = target_proxy.id
        initial_size = stress_pool.size

        def remove_same_proxy() -> bool:
            """Try to remove the same proxy."""
            try:
                stress_pool.remove_proxy(target_id)
                return True
            except Exception:
                return False

        # Submit 20 tasks to remove the same proxy
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(remove_same_proxy) for _ in range(20)]
            results = [f.result() for f in as_completed(futures)]

        # All should complete without error
        assert len(results) == 20
        # Proxy should be removed exactly once
        assert stress_pool.size == initial_size - 1
        # Proxy should not be in pool
        assert target_id not in {p.id for p in stress_pool.proxies}

    def test_concurrent_remove_nonexistent_proxies(self, stress_pool: ProxyPool) -> None:
        """Test that removing non-existent proxies doesn't corrupt the pool."""
        from uuid import uuid4

        # Generate fake IDs that don't exist
        fake_ids = [uuid4() for _ in range(50)]
        initial_size = stress_pool.size

        def remove_fake_proxy(fake_id: str) -> bool:
            """Try to remove a non-existent proxy."""
            try:
                stress_pool.remove_proxy(fake_id)
                return True
            except Exception:
                return False

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(remove_fake_proxy, fid) for fid in fake_ids]
            results = [f.result() for f in as_completed(futures)]

        # All should complete
        assert len(results) == 50
        # Pool size should be unchanged
        assert stress_pool.size == initial_size


# ============================================================================
# CONCURRENT MIXED OPERATIONS
# ============================================================================


@pytest.mark.slow
class TestConcurrentMixedOperations:
    """Test concurrent combinations of add, remove, and select operations."""

    def test_concurrent_add_remove_select(self, stress_pool: ProxyPool) -> None:
        """Test simultaneous adds, removes, and selections from 20 workers."""
        initial_size = stress_pool.size
        strategy = RoundRobinStrategy()

        add_count = 0
        remove_count = 0
        select_count = 0
        error_count = 0

        lock = threading.Lock()

        def add_task(idx: int) -> None:
            """Add a new proxy."""
            nonlocal add_count, error_count
            try:
                proxy = Proxy(url=f"http://added-proxy{idx}.example.com:8080")
                proxy.health_status = HealthStatus.HEALTHY
                stress_pool.add_proxy(proxy)
                with lock:
                    add_count += 1
            except Exception:
                with lock:
                    error_count += 1

        def remove_task() -> None:
            """Remove a random proxy."""
            nonlocal remove_count, error_count
            try:
                if stress_pool.size > 5:  # Keep minimum pool size
                    proxy_to_remove = random.choice(stress_pool.proxies)
                    stress_pool.remove_proxy(proxy_to_remove.id)
                    with lock:
                        remove_count += 1
            except Exception:
                with lock:
                    error_count += 1

        def select_task() -> None:
            """Select a proxy using the strategy."""
            nonlocal select_count, error_count
            try:
                if stress_pool.size > 0:
                    proxy = strategy.select(stress_pool)
                    if proxy is not None:
                        with lock:
                            select_count += 1
            except Exception:
                with lock:
                    error_count += 1

        # Create mixed workload: 50 adds, 30 removes, 120 selects
        tasks = []
        tasks.extend([lambda idx=i: add_task(idx) for i in range(50)])
        tasks.extend([remove_task for _ in range(30)])
        tasks.extend([select_task for _ in range(120)])

        # Shuffle to ensure random interleaving
        random.shuffle(tasks)

        # Execute with 20 concurrent workers
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(task) for task in tasks]
            for future in as_completed(futures):
                future.result()  # Wait for completion

        # Verify operations completed
        assert add_count + remove_count + select_count + error_count == 200
        # Most operations should succeed (allow some failures for edge cases)
        assert error_count < 20  # Less than 10% failure rate

        # Pool should be in valid state
        final_size = stress_pool.size
        assert final_size == initial_size + add_count - remove_count
        # All proxies should have unique URLs
        urls = [p.url for p in stress_pool.proxies]
        assert len(urls) == len(set(urls))

    def test_stress_test_1000_operations(self, stress_pool: ProxyPool) -> None:
        """Heavy stress test with 1000 operations from 50 workers."""
        strategy = WeightedStrategy()
        operation_results = {"add": 0, "remove": 0, "select": 0, "error": 0}
        lock = threading.Lock()

        def random_operation(idx: int) -> str:
            """Perform a random operation and return the operation type."""
            try:
                operation = random.choice(["add", "remove", "select", "select", "select"])

                if operation == "add" and stress_pool.size < 180:
                    proxy = Proxy(url=f"http://stress-proxy{idx}.example.com:8080")
                    proxy.health_status = HealthStatus.HEALTHY
                    stress_pool.add_proxy(proxy)
                    return "add"

                elif operation == "remove" and stress_pool.size > 10:
                    proxy_to_remove = random.choice(stress_pool.proxies)
                    stress_pool.remove_proxy(proxy_to_remove.id)
                    return "remove"

                elif operation == "select" and stress_pool.size > 0:
                    proxy = strategy.select(stress_pool)
                    if proxy:
                        # Simulate some work with the proxy
                        proxy.total_requests += 1
                        proxy.total_successes += random.choice([0, 1])
                        return "select"

                return "skip"

            except Exception:
                return "error"

        # Execute 1000 random operations
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(random_operation, i) for i in range(1000)]
            for future in as_completed(futures):
                result = future.result()
                with lock:
                    if result in operation_results:
                        operation_results[result] += 1

        # Verify heavy load completed with minimal errors
        assert operation_results["error"] < 50  # Less than 5% failure rate
        # Pool should still be functional
        assert 10 <= stress_pool.size <= 180
        # All proxies should have unique URLs
        urls = [p.url for p in stress_pool.proxies]
        assert len(urls) == len(set(urls))


# ============================================================================
# CONCURRENT STRATEGY SWITCHING
# ============================================================================


@pytest.mark.slow
class TestConcurrentStrategySwitching:
    """Test strategy switching under high concurrent load."""

    def test_strategy_switch_during_heavy_selection(self, strategy_pool: ProxyPool) -> None:
        """Switch strategies while 100 threads are actively selecting proxies."""
        strategies = [
            RoundRobinStrategy(),
            RandomStrategy(),
            WeightedStrategy(),
            LeastUsedStrategy(),
            PerformanceBasedStrategy(),
        ]

        current_strategy_idx = 0
        strategy_lock = threading.Lock()
        selection_count = 0
        selection_lock = threading.Lock()
        switch_count = 0

        def select_task() -> bool:
            """Continuously select proxies using current strategy."""
            nonlocal selection_count
            try:
                with strategy_lock:
                    strategy = strategies[current_strategy_idx]

                if strategy_pool.size > 0:
                    proxy = strategy.select(strategy_pool)
                    if proxy:
                        with selection_lock:
                            selection_count += 1
                        return True
                return False
            except Exception:
                return False

        def switch_strategy_task() -> int:
            """Switch to next strategy."""
            nonlocal current_strategy_idx, switch_count
            with strategy_lock:
                current_strategy_idx = (current_strategy_idx + 1) % len(strategies)
                switch_count += 1
            # Small delay between switches
            time.sleep(0.01)
            return current_strategy_idx

        # Start 100 selection tasks and 20 strategy switches
        with ThreadPoolExecutor(max_workers=30) as executor:
            # Submit selection tasks
            select_futures = [executor.submit(select_task) for _ in range(100)]

            # Submit strategy switch tasks with slight delays
            switch_futures = []
            for i in range(20):
                future = executor.submit(switch_strategy_task)
                switch_futures.append(future)
                time.sleep(0.005)  # Small delay between switch submissions

            # Wait for all to complete
            for future in as_completed(select_futures + switch_futures):
                future.result()

        # Verify operations completed
        assert selection_count >= 80  # At least 80% of selections succeeded
        assert switch_count == 20  # All strategy switches completed

        # Pool should remain consistent
        assert strategy_pool.size == 15
        urls = [p.url for p in strategy_pool.proxies]
        assert len(urls) == len(set(urls))

    def test_strategy_switch_with_concurrent_modifications(self, strategy_pool: ProxyPool) -> None:
        """Switch strategies while adding/removing proxies and selecting."""
        strategies = [
            RoundRobinStrategy(),
            WeightedStrategy(),
            LeastUsedStrategy(),
        ]

        current_strategy = [strategies[0]]  # Use list for mutability
        operation_counts = {"add": 0, "remove": 0, "select": 0, "switch": 0}
        lock = threading.Lock()

        def add_proxy_task(idx: int) -> None:
            """Add a proxy."""
            if strategy_pool.size < 90:
                proxy = Proxy(url=f"http://switch-test{idx}.example.com:8080")
                proxy.health_status = HealthStatus.HEALTHY
                proxy.total_requests = random.randint(10, 100)
                proxy.total_successes = random.randint(5, 95)
                strategy_pool.add_proxy(proxy)
                with lock:
                    operation_counts["add"] += 1

        def remove_proxy_task() -> None:
            """Remove a proxy."""
            if strategy_pool.size > 5:
                proxy_to_remove = random.choice(strategy_pool.proxies)
                strategy_pool.remove_proxy(proxy_to_remove.id)
                with lock:
                    operation_counts["remove"] += 1

        def select_proxy_task() -> None:
            """Select a proxy using current strategy."""
            if strategy_pool.size > 0:
                proxy = current_strategy[0].select(strategy_pool)
                if proxy:
                    with lock:
                        operation_counts["select"] += 1

        def switch_strategy_task() -> None:
            """Switch to a random strategy."""
            current_strategy[0] = random.choice(strategies)
            with lock:
                operation_counts["switch"] += 1
            time.sleep(0.01)

        # Create workload: 30 adds, 20 removes, 80 selects, 15 switches
        tasks = []
        tasks.extend([lambda idx=i: add_proxy_task(idx) for i in range(30)])
        tasks.extend([remove_proxy_task for _ in range(20)])
        tasks.extend([select_proxy_task for _ in range(80)])
        tasks.extend([switch_strategy_task for _ in range(15)])

        random.shuffle(tasks)

        # Execute with 25 workers
        with ThreadPoolExecutor(max_workers=25) as executor:
            futures = [executor.submit(task) for task in tasks]
            for future in as_completed(futures):
                future.result()

        # Verify all operations completed
        total_ops = sum(operation_counts.values())
        assert total_ops >= 140  # Allow some operations to skip due to constraints

        # Pool should be in valid state
        assert 5 <= strategy_pool.size <= 90
        urls = [p.url for p in strategy_pool.proxies]
        assert len(urls) == len(set(urls))


# ============================================================================
# CONCURRENT HEALTH STATUS UPDATES
# ============================================================================


@pytest.mark.slow
class TestConcurrentHealthUpdates:
    """Test concurrent health status updates during active operations."""

    def test_concurrent_health_updates_with_selections(self, stress_pool: ProxyPool) -> None:
        """Update proxy health while actively selecting proxies."""
        strategy = PerformanceBasedStrategy()
        health_statuses = [
            HealthStatus.HEALTHY,
            HealthStatus.DEGRADED,
            HealthStatus.UNHEALTHY,
            HealthStatus.HEALTHY,
        ]

        selection_count = 0
        health_update_count = 0
        lock = threading.Lock()

        def select_task() -> None:
            """Select proxies continuously."""
            nonlocal selection_count
            if stress_pool.size > 0:
                try:
                    proxy = strategy.select(stress_pool)
                    if proxy:
                        with lock:
                            selection_count += 1
                except Exception:
                    pass

        def update_health_task() -> None:
            """Randomly update proxy health statuses."""
            nonlocal health_update_count
            if stress_pool.proxies:
                proxy = random.choice(stress_pool.proxies)
                proxy.health_status = random.choice(health_statuses)
                with lock:
                    health_update_count += 1

        # Create workload: 100 selections, 50 health updates
        tasks = [select_task for _ in range(100)] + [update_health_task for _ in range(50)]
        random.shuffle(tasks)

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(task) for task in tasks]
            for future in as_completed(futures):
                future.result()

        # Verify operations completed
        assert selection_count >= 70  # At least 70% of selections succeeded
        assert health_update_count == 50  # All health updates completed

        # Pool should remain consistent
        assert stress_pool.size == 20
        assert all(isinstance(p.health_status, HealthStatus) for p in stress_pool.proxies)


# ============================================================================
# CONCURRENT STATISTICS UPDATES
# ============================================================================


@pytest.mark.slow
class TestConcurrentStatisticsUpdates:
    """Test concurrent proxy statistics updates."""

    def test_concurrent_stat_updates_with_selections(self, stress_pool: ProxyPool) -> None:
        """Update proxy statistics while selecting proxies."""
        strategy = WeightedStrategy()

        def update_stats_task(proxy: Proxy) -> None:
            """Update proxy statistics."""
            proxy.total_requests += 1
            proxy.total_successes += random.choice([0, 1])
            proxy.average_response_time_ms = random.uniform(50, 1000)

        def select_and_update_task() -> bool:
            """Select a proxy and update its stats."""
            if stress_pool.size > 0:
                try:
                    proxy = strategy.select(stress_pool)
                    if proxy:
                        update_stats_task(proxy)
                        return True
                except Exception:
                    pass
            return False

        # Execute 200 concurrent select-and-update operations
        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = [executor.submit(select_and_update_task) for _ in range(200)]
            results = [f.result() for f in as_completed(futures)]

        # Most operations should succeed
        successful = sum(1 for r in results if r)
        assert successful >= 180  # At least 90% success rate

        # Verify statistics were updated
        total_requests = sum(p.total_requests for p in stress_pool.proxies)
        assert total_requests >= 200  # Initial stats + new requests


# ============================================================================
# EDGE CASES AND RACE CONDITIONS
# ============================================================================


@pytest.mark.slow
class TestConcurrencyEdgeCases:
    """Test edge cases and potential race conditions."""

    def test_concurrent_empty_pool_selections(self) -> None:
        """Test selecting from pool while it's being emptied."""
        pool = ProxyPool(name="empty-test", max_pool_size=50)
        # Start with a few proxies
        for i in range(10):
            proxy = Proxy(url=f"http://empty-test{i}.example.com:8080")
            proxy.health_status = HealthStatus.HEALTHY
            pool.add_proxy(proxy)

        strategy = RoundRobinStrategy()
        successful_selections = []
        failed_selections = []

        def select_task() -> None:
            """Try to select a proxy."""
            try:
                if pool.size > 0:
                    proxy = strategy.select(pool)
                    if proxy:
                        successful_selections.append(proxy)
                else:
                    failed_selections.append(None)
            except Exception:
                failed_selections.append(None)

        def remove_all_task() -> None:
            """Remove all proxies."""
            while pool.size > 0:
                if pool.proxies:
                    proxy = pool.proxies[0]
                    pool.remove_proxy(proxy.id)
                time.sleep(0.001)  # Small delay

        # Start selection tasks and removal task concurrently
        with ThreadPoolExecutor(max_workers=15) as executor:
            # Start many selection tasks
            select_futures = [executor.submit(select_task) for _ in range(100)]
            # Start removal task
            remove_future = executor.submit(remove_all_task)

            # Wait for all to complete
            for future in as_completed(select_futures + [remove_future]):
                future.result()

        # Pool should be empty
        assert pool.size == 0
        # No crashes or deadlocks should occur
        # Some selections should have succeeded, some failed
        assert len(successful_selections) + len(failed_selections) == 100

    def test_concurrent_access_to_same_proxy(self, stress_pool: ProxyPool) -> None:
        """Test concurrent access to the same proxy object."""
        target_proxy = stress_pool.proxies[0]
        initial_requests = target_proxy.total_requests

        def increment_proxy_stats() -> None:
            """Increment the target proxy's request count."""
            target_proxy.total_requests += 1

        # Execute 100 concurrent increments
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(increment_proxy_stats) for _ in range(100)]
            for future in as_completed(futures):
                future.result()

        # Verify all increments occurred
        # Note: Without proxy-level locking, this may not be exactly 100
        # due to race conditions on the proxy object itself
        assert target_proxy.total_requests >= initial_requests + 80  # Allow some loss
