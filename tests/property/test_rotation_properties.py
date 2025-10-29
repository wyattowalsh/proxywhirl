"""Property-based tests for rotation strategies using Hypothesis."""

from hypothesis import given
from hypothesis import strategies as st

from proxywhirl import (
    LeastUsedStrategy,
    Proxy,
    ProxyPool,
    RandomStrategy,
    RoundRobinStrategy,
    WeightedStrategy,
)
from proxywhirl.models import HealthStatus


class TestRoundRobinProperties:
    """Property-based tests for RoundRobinStrategy."""

    @given(st.integers(min_value=1, max_value=20))
    def test_all_proxies_eventually_selected(self, num_proxies: int):
        """Property: Given N healthy proxies, all N proxies are selected within N selections."""
        # Create pool with N proxies
        pool = ProxyPool(name="test-pool")
        proxies = []
        for i in range(num_proxies):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            proxy.health_status = HealthStatus.HEALTHY
            pool.add_proxy(proxy)
            proxies.append(proxy)

        strategy = RoundRobinStrategy()

        # Select N times
        selected_ids = set()
        for _ in range(num_proxies):
            proxy = strategy.select(pool)
            assert proxy is not None, "Strategy should always return a proxy with healthy proxies"
            selected_ids.add(proxy.id)

        # All proxy IDs should have been selected
        expected_ids = {p.id for p in proxies}
        assert selected_ids == expected_ids, (
            f"All {num_proxies} proxies should be selected within {num_proxies} selections. "
            f"Expected: {expected_ids}, Got: {selected_ids}"
        )

    @given(st.integers(min_value=1, max_value=20))
    def test_no_duplicates_before_full_cycle(self, num_proxies: int):
        """Property: Given N healthy proxies, no proxy is selected twice before all N have been selected once."""
        # Create pool with N proxies
        pool = ProxyPool(name="test-pool")
        proxies = []
        for i in range(num_proxies):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            proxy.health_status = HealthStatus.HEALTHY
            pool.add_proxy(proxy)
            proxies.append(proxy)

        strategy = RoundRobinStrategy()

        # Track selection order
        selected_ids = []
        for _ in range(num_proxies):
            proxy = strategy.select(pool)
            assert proxy is not None
            selected_ids.append(proxy.id)

        # Check no duplicates before completing one full cycle
        assert len(selected_ids) == len(set(selected_ids)), (
            f"No duplicates should occur in first {num_proxies} selections. "
            f"Got duplicates in: {selected_ids}"
        )

    @given(st.integers(min_value=2, max_value=20), st.integers(min_value=1, max_value=10))
    def test_wraparound_after_full_cycle(self, num_proxies: int, num_cycles: int):
        """Property: After selecting all N proxies, the pattern repeats (wraparound)."""
        # Create pool with N proxies
        pool = ProxyPool(name="test-pool")
        proxies = []
        for i in range(num_proxies):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            proxy.health_status = HealthStatus.HEALTHY
            pool.add_proxy(proxy)
            proxies.append(proxy)

        strategy = RoundRobinStrategy()

        # Collect selection pattern for multiple cycles
        selections_per_cycle = []
        for cycle in range(num_cycles):
            cycle_selections = []
            for _ in range(num_proxies):
                proxy = strategy.select(pool)
                assert proxy is not None
                cycle_selections.append(proxy.id)
            selections_per_cycle.append(cycle_selections)

        # All cycles should have the same selection pattern
        first_cycle = selections_per_cycle[0]
        for cycle_num, cycle_selections in enumerate(selections_per_cycle[1:], start=2):
            assert cycle_selections == first_cycle, (
                f"Cycle {cycle_num} should match cycle 1. "
                f"Cycle 1: {first_cycle}, Cycle {cycle_num}: {cycle_selections}"
            )

    @given(st.integers(min_value=3, max_value=20), st.integers(min_value=1, max_value=5))
    def test_healthy_proxies_only(self, num_total: int, num_healthy: int):
        """Property: Only healthy proxies are selected when both healthy and unhealthy proxies exist."""
        # Ensure we have at least 1 healthy proxy
        num_healthy = min(num_healthy, num_total)
        if num_healthy == 0:
            num_healthy = 1

        # Create pool with mix of healthy and unhealthy proxies
        pool = ProxyPool(name="test-pool")
        healthy_ids = set()

        # Add healthy proxies
        for i in range(num_healthy):
            proxy = Proxy(url=f"http://healthy{i}.example.com:8080")
            proxy.health_status = HealthStatus.HEALTHY
            pool.add_proxy(proxy)
            healthy_ids.add(proxy.id)

        # Add unhealthy/dead proxies
        for i in range(num_total - num_healthy):
            proxy = Proxy(url=f"http://unhealthy{i}.example.com:8080")
            proxy.health_status = HealthStatus.UNHEALTHY if i % 2 == 0 else HealthStatus.DEAD
            pool.add_proxy(proxy)

        strategy = RoundRobinStrategy()

        # Select multiple times (2 full cycles of healthy proxies)
        for _ in range(num_healthy * 2):
            proxy = strategy.select(pool)
            assert proxy is not None, "Should select a proxy when healthy proxies exist"
            assert proxy.id in healthy_ids, (
                f"Only healthy proxies should be selected. "
                f"Got proxy with health status: {proxy.health_status}"
            )

    @given(st.integers(min_value=1, max_value=20))
    def test_deterministic_order(self, num_proxies: int):
        """Property: Given the same pool, selections are deterministic and predictable."""
        # Create two identical pools
        pool1 = ProxyPool(name="test-pool-1")
        pool2 = ProxyPool(name="test-pool-2")

        for i in range(num_proxies):
            proxy1 = Proxy(url=f"http://proxy{i}.example.com:8080")
            proxy1.health_status = HealthStatus.HEALTHY
            pool1.add_proxy(proxy1)

            proxy2 = Proxy(url=f"http://proxy{i}.example.com:8080")
            proxy2.health_status = HealthStatus.HEALTHY
            pool2.add_proxy(proxy2)

        strategy1 = RoundRobinStrategy()
        strategy2 = RoundRobinStrategy()

        # Select from both pools
        selections1 = []
        selections2 = []

        for _ in range(num_proxies * 2):
            proxy1 = strategy1.select(pool1)
            proxy2 = strategy2.select(pool2)
            assert proxy1 is not None and proxy2 is not None
            selections1.append(proxy1.url)
            selections2.append(proxy2.url)

        # Both should have the same selection order (by URL since IDs will differ)
        assert selections1 == selections2, "Selection order should be deterministic"

    @given(st.integers(min_value=2, max_value=10))
    def test_fair_distribution(self, num_proxies: int):
        """Property: Over many selections, all healthy proxies are selected roughly equally."""
        # Create pool with N proxies
        pool = ProxyPool(name="test-pool")
        proxies = []
        for i in range(num_proxies):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            proxy.health_status = HealthStatus.HEALTHY
            pool.add_proxy(proxy)
            proxies.append(proxy)

        strategy = RoundRobinStrategy()

        # Select many times (10 full cycles)
        num_selections = num_proxies * 10
        selection_counts = {p.id: 0 for p in proxies}

        for _ in range(num_selections):
            proxy = strategy.select(pool)
            assert proxy is not None
            selection_counts[proxy.id] += 1

        # Each proxy should be selected exactly 10 times (perfect distribution)
        expected_count = 10
        for proxy_id, count in selection_counts.items():
            assert count == expected_count, (
                f"Proxy {proxy_id} should be selected {expected_count} times, "
                f"but was selected {count} times. Distribution: {selection_counts}"
            )


class TestRandomStrategyProperties:
    """Property-based tests for RandomStrategy."""

    @given(st.integers(min_value=2, max_value=20))
    def test_all_proxies_can_be_selected(self, num_proxies: int):
        """Property: Over many selections, all proxies should eventually be selected."""
        pool = ProxyPool(name="test-pool")
        proxies = []
        for i in range(num_proxies):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            proxy.health_status = HealthStatus.HEALTHY
            pool.add_proxy(proxy)
            proxies.append(proxy)

        strategy = RandomStrategy()

        # Use coupon collector's problem: E[tries] ≈ n*ln(n)
        # Use 5*n as a safe upper bound to see all proxies
        selected_ids = set()
        max_tries = num_proxies * 5

        for _ in range(max_tries):
            proxy = strategy.select(pool)
            assert proxy is not None
            selected_ids.add(proxy.id)
            if len(selected_ids) == num_proxies:
                break

        # All proxies should have been seen
        expected_ids = {p.id for p in proxies}
        assert selected_ids == expected_ids, (
            f"All {num_proxies} proxies should be selected within {max_tries} tries. "
            f"Expected: {expected_ids}, Got: {selected_ids}"
        )

    @given(st.integers(min_value=3, max_value=20), st.integers(min_value=1, max_value=5))
    def test_healthy_proxies_only(self, num_total: int, num_healthy: int):
        """Property: Only healthy proxies are selected when both healthy and unhealthy proxies exist."""
        # Ensure we have at least 1 healthy proxy
        num_healthy = min(num_healthy, num_total)
        if num_healthy == 0:
            num_healthy = 1

        pool = ProxyPool(name="test-pool")
        healthy_ids = set()

        # Add healthy proxies
        for i in range(num_healthy):
            proxy = Proxy(url=f"http://healthy{i}.example.com:8080")
            proxy.health_status = HealthStatus.HEALTHY
            pool.add_proxy(proxy)
            healthy_ids.add(proxy.id)

        # Add unhealthy/dead proxies
        for i in range(num_total - num_healthy):
            proxy = Proxy(url=f"http://unhealthy{i}.example.com:8080")
            proxy.health_status = HealthStatus.UNHEALTHY if i % 2 == 0 else HealthStatus.DEAD
            pool.add_proxy(proxy)

        strategy = RandomStrategy()

        # Select multiple times
        for _ in range(num_healthy * 5):
            proxy = strategy.select(pool)
            assert proxy is not None, "Should select a proxy when healthy proxies exist"
            assert proxy.id in healthy_ids, (
                f"Only healthy proxies should be selected. "
                f"Got proxy with health status: {proxy.health_status}"
            )


class TestWeightedStrategyProperties:
    """Property-based tests for WeightedStrategy."""

    @given(st.integers(min_value=2, max_value=20))
    def test_all_proxies_can_be_selected(self, num_proxies: int):
        """Property: All proxies can be selected (even with default weight)."""
        pool = ProxyPool(name="test-pool")
        proxies = []
        for i in range(num_proxies):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            proxy.health_status = HealthStatus.HEALTHY
            pool.add_proxy(proxy)
            proxies.append(proxy)

        strategy = WeightedStrategy()

        # Try many times to see all proxies
        selected_ids = set()
        max_tries = num_proxies * 10

        for _ in range(max_tries):
            proxy = strategy.select(pool)
            assert proxy is not None
            selected_ids.add(proxy.id)
            if len(selected_ids) == num_proxies:
                break

        # All proxies should have been seen
        expected_ids = {p.id for p in proxies}
        assert selected_ids == expected_ids, (
            f"All {num_proxies} proxies should be selected within {max_tries} tries. "
            f"Expected: {expected_ids}, Got: {selected_ids}"
        )

    @given(st.integers(min_value=2, max_value=10))
    def test_higher_success_rate_selected_more_often(self, num_proxies: int):
        """Property: Proxies with higher success rates should be selected more frequently."""
        pool = ProxyPool(name="test-pool")
        proxies = []

        # Create proxies with varying success rates
        for i in range(num_proxies):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            proxy.health_status = HealthStatus.HEALTHY

            if i == 0:
                # First proxy: high success rate (95%)
                proxy.total_requests = 100
                proxy.total_successes = 95
            else:
                # Other proxies: lower success rate (20%)
                proxy.total_requests = 100
                proxy.total_successes = 20

            pool.add_proxy(proxy)
            proxies.append(proxy)

        strategy = WeightedStrategy()

        # Select many times
        selection_counts = {p.id: 0 for p in proxies}
        num_selections = 1000

        for _ in range(num_selections):
            proxy = strategy.select(pool)
            assert proxy is not None
            selection_counts[proxy.id] += 1

        # First proxy (high success rate) should be selected most often
        first_proxy_count = selection_counts[proxies[0].id]

        # It should be selected more than any other proxy
        for i, proxy in enumerate(proxies[1:], start=1):
            other_count = selection_counts[proxy.id]
            assert first_proxy_count > other_count, (
                f"High-success proxy (95%) should be selected more often than low-success proxy (20%). "
                f"High-success count: {first_proxy_count}, Low-success count: {other_count}"
            )


class TestLeastUsedStrategyProperties:
    """Property-based tests for LeastUsedStrategy."""

    @given(st.integers(min_value=2, max_value=20))
    def test_all_proxies_eventually_selected(self, num_proxies: int):
        """Property: Every proxy should be selected within N iterations."""
        pool = ProxyPool(name="test-pool")
        proxies = []
        for i in range(num_proxies):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            proxy.health_status = HealthStatus.HEALTHY
            pool.add_proxy(proxy)
            proxies.append(proxy)

        strategy = LeastUsedStrategy()

        # Select N times, incrementing usage count after each selection
        selected_ids = set()
        for _ in range(num_proxies):
            proxy = strategy.select(pool)
            assert proxy is not None
            selected_ids.add(proxy.id)
            # Mark as used so next selection picks a different one
            proxy.total_requests += 1

        # All proxies should have been selected at least once
        expected_ids = {p.id for p in proxies}
        assert selected_ids == expected_ids, (
            f"All {num_proxies} proxies should be selected within {num_proxies} selections. "
            f"Expected: {expected_ids}, Got: {selected_ids}"
        )

    @given(st.integers(min_value=2, max_value=15))
    def test_distributes_load_evenly(self, num_proxies: int):
        """Property: Load should be distributed evenly across all proxies."""
        pool = ProxyPool(name="test-pool")
        proxies = []
        for i in range(num_proxies):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            proxy.health_status = HealthStatus.HEALTHY
            pool.add_proxy(proxy)
            proxies.append(proxy)

        strategy = LeastUsedStrategy()

        # Select N * 10 times and mark each as used
        num_selections = num_proxies * 10
        for _ in range(num_selections):
            proxy = strategy.select(pool)
            assert proxy is not None
            # Mark as used
            proxy.total_requests += 1

        # Check distribution - all proxies should have similar usage counts
        usage_counts = [p.total_requests for p in proxies]

        # With perfect load balancing, all should be 10
        assert all(count == 10 for count in usage_counts), (
            f"All proxies should be used exactly 10 times with least-used strategy. "
            f"Usage counts: {usage_counts}"
        )

    @given(st.integers(min_value=3, max_value=20), st.integers(min_value=1, max_value=5))
    def test_healthy_proxies_only(self, num_total: int, num_healthy: int):
        """Property: Only healthy proxies are selected when both healthy and unhealthy proxies exist."""
        # Ensure we have at least 1 healthy proxy
        num_healthy = min(num_healthy, num_total)
        if num_healthy == 0:
            num_healthy = 1

        pool = ProxyPool(name="test-pool")
        healthy_ids = set()

        # Add healthy proxies
        for i in range(num_healthy):
            proxy = Proxy(url=f"http://healthy{i}.example.com:8080")
            proxy.health_status = HealthStatus.HEALTHY
            pool.add_proxy(proxy)
            healthy_ids.add(proxy.id)

        # Add unhealthy/dead proxies
        for i in range(num_total - num_healthy):
            proxy = Proxy(url=f"http://unhealthy{i}.example.com:8080")
            proxy.health_status = HealthStatus.UNHEALTHY if i % 2 == 0 else HealthStatus.DEAD
            pool.add_proxy(proxy)

        strategy = LeastUsedStrategy()

        # Select multiple times
        for _ in range(num_healthy * 3):
            proxy = strategy.select(pool)
            assert proxy is not None, "Should select a proxy when healthy proxies exist"
            assert proxy.id in healthy_ids, (
                f"Only healthy proxies should be selected. "
                f"Got proxy with health status: {proxy.health_status}"
            )
