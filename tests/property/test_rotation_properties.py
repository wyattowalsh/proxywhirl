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


# ============================================================================
# UNIVERSAL STRATEGY PROPERTIES
# ============================================================================


class TestUniversalStrategyProperties:
    """Property-based tests that apply to ALL rotation strategies."""

    @given(st.integers(min_value=1, max_value=20))
    def test_strategy_always_returns_valid_proxy_from_pool_roundrobin(self, num_proxies: int):
        """Property: RoundRobinStrategy always returns a proxy that exists in the pool."""
        pool = ProxyPool(name="test-pool")
        pool_proxy_ids = set()

        for i in range(num_proxies):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            proxy.health_status = HealthStatus.HEALTHY
            pool.add_proxy(proxy)
            pool_proxy_ids.add(proxy.id)

        strategy = RoundRobinStrategy()

        # Select many times and verify each result is from the pool
        for _ in range(num_proxies * 3):
            selected = strategy.select(pool)
            assert selected is not None, "Strategy should return a proxy"
            assert selected.id in pool_proxy_ids, (
                f"Selected proxy {selected.id} not in pool. Pool contains: {pool_proxy_ids}"
            )

    @given(st.integers(min_value=1, max_value=20))
    def test_strategy_always_returns_valid_proxy_from_pool_random(self, num_proxies: int):
        """Property: RandomStrategy always returns a proxy that exists in the pool."""
        pool = ProxyPool(name="test-pool")
        pool_proxy_ids = set()

        for i in range(num_proxies):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            proxy.health_status = HealthStatus.HEALTHY
            pool.add_proxy(proxy)
            pool_proxy_ids.add(proxy.id)

        strategy = RandomStrategy()

        # Select many times and verify each result is from the pool
        for _ in range(num_proxies * 3):
            selected = strategy.select(pool)
            assert selected is not None, "Strategy should return a proxy"
            assert selected.id in pool_proxy_ids, (
                f"Selected proxy {selected.id} not in pool. Pool contains: {pool_proxy_ids}"
            )

    @given(st.integers(min_value=1, max_value=20))
    def test_strategy_always_returns_valid_proxy_from_pool_weighted(self, num_proxies: int):
        """Property: WeightedStrategy always returns a proxy that exists in the pool."""
        pool = ProxyPool(name="test-pool")
        pool_proxy_ids = set()

        for i in range(num_proxies):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            proxy.health_status = HealthStatus.HEALTHY
            # Give some variety in success rates for weighting
            proxy.total_requests = 100
            proxy.total_successes = 50 + (i * 5) % 50  # 50-100 successes
            pool.add_proxy(proxy)
            pool_proxy_ids.add(proxy.id)

        strategy = WeightedStrategy()

        # Select many times and verify each result is from the pool
        for _ in range(num_proxies * 3):
            selected = strategy.select(pool)
            assert selected is not None, "Strategy should return a proxy"
            assert selected.id in pool_proxy_ids, (
                f"Selected proxy {selected.id} not in pool. Pool contains: {pool_proxy_ids}"
            )

    @given(st.integers(min_value=1, max_value=20))
    def test_strategy_always_returns_valid_proxy_from_pool_least_used(self, num_proxies: int):
        """Property: LeastUsedStrategy always returns a proxy that exists in the pool."""
        pool = ProxyPool(name="test-pool")
        pool_proxy_ids = set()

        for i in range(num_proxies):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            proxy.health_status = HealthStatus.HEALTHY
            pool.add_proxy(proxy)
            pool_proxy_ids.add(proxy.id)

        strategy = LeastUsedStrategy()

        # Select many times and verify each result is from the pool
        for _ in range(num_proxies * 3):
            selected = strategy.select(pool)
            assert selected is not None, "Strategy should return a proxy"
            assert selected.id in pool_proxy_ids, (
                f"Selected proxy {selected.id} not in pool. Pool contains: {pool_proxy_ids}"
            )
            # Mark as used for the strategy to work properly
            selected.total_requests += 1


class TestWeightedStrategyDistribution:
    """Property tests for WeightedStrategy weight distribution."""

    @given(st.integers(min_value=2, max_value=8))
    def test_weighted_strategy_respects_weight_distribution(self, num_proxies: int):
        """Property: WeightedStrategy selection distribution respects weights over many calls."""
        pool = ProxyPool(name="test-pool")
        proxies = []

        # Create proxies with deliberately different success rates
        # First proxy: 100% success rate (should be selected most)
        # Others: decreasing success rates
        for i in range(num_proxies):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            proxy.health_status = HealthStatus.HEALTHY
            proxy.total_requests = 100

            if i == 0:
                proxy.total_successes = 100  # 100% success rate
            else:
                # Decreasing success rates: 50%, 40%, 30%, etc.
                proxy.total_successes = max(10, 60 - i * 10)

            pool.add_proxy(proxy)
            proxies.append(proxy)

        strategy = WeightedStrategy()

        # Track selection counts
        selection_counts = {str(p.id): 0 for p in proxies}

        # Many selections to observe distribution
        num_selections = 2000
        for _ in range(num_selections):
            selected = strategy.select(pool)
            selection_counts[str(selected.id)] += 1

        # The highest success rate proxy should be selected most often
        best_proxy_id = str(proxies[0].id)
        best_count = selection_counts[best_proxy_id]

        # It should have the highest selection count
        for proxy_id, count in selection_counts.items():
            if proxy_id != best_proxy_id:
                assert best_count >= count, (
                    f"Best proxy (100% success) should be selected at least as often "
                    f"as others. Best: {best_count}, Other: {count}"
                )

    @given(
        weights=st.lists(
            st.floats(min_value=0.1, max_value=10.0),
            min_size=2,
            max_size=5,
        )
    )
    def test_custom_weights_influence_distribution(self, weights: list[float]):
        """Property: Custom weights directly influence selection probability."""
        pool = ProxyPool(name="test-pool")
        proxies = []

        for i, weight in enumerate(weights):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            proxy.health_status = HealthStatus.HEALTHY
            pool.add_proxy(proxy)
            proxies.append(proxy)

        # Create strategy with custom weights
        from proxywhirl.models import StrategyConfig

        weight_dict = {proxy.url: weight for proxy, weight in zip(proxies, weights)}
        config = StrategyConfig(weights=weight_dict)

        strategy = WeightedStrategy()
        strategy.configure(config)

        # Track selection counts
        selection_counts = {str(p.id): 0 for p in proxies}

        # Many selections
        num_selections = 1000
        for _ in range(num_selections):
            selected = strategy.select(pool)
            selection_counts[str(selected.id)] += 1

        # Find the proxy with the highest custom weight
        max_weight_idx = weights.index(max(weights))
        max_weight_proxy_id = str(proxies[max_weight_idx].id)

        # The highest weighted proxy should have a high selection count
        # Allow for statistical variation, but it should be above average
        avg_count = num_selections / len(weights)
        high_weight_count = selection_counts[max_weight_proxy_id]

        # It should be selected at least as often as average (statistical variation allowed)
        assert high_weight_count >= avg_count * 0.5, (
            f"Highest weighted proxy should be selected frequently. "
            f"Expected at least {avg_count * 0.5:.0f}, got {high_weight_count}"
        )


class TestRoundRobinCycleProperties:
    """Additional property tests for RoundRobin cycling behavior."""

    @given(st.integers(min_value=2, max_value=15))
    def test_roundrobin_cycles_through_all_proxies_exactly(self, num_proxies: int):
        """Property: RoundRobin visits each proxy exactly once per complete cycle."""
        pool = ProxyPool(name="test-pool")
        proxies = []

        for i in range(num_proxies):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            proxy.health_status = HealthStatus.HEALTHY
            pool.add_proxy(proxy)
            proxies.append(proxy)

        strategy = RoundRobinStrategy()

        # Track one complete cycle
        cycle_ids = []
        for _ in range(num_proxies):
            selected = strategy.select(pool)
            cycle_ids.append(selected.id)

        # Should have visited exactly N unique proxies
        unique_ids = set(cycle_ids)
        expected_ids = {p.id for p in proxies}

        assert unique_ids == expected_ids, (
            f"RoundRobin should cycle through all {num_proxies} proxies exactly once. "
            f"Expected {expected_ids}, got {unique_ids}"
        )

        # No duplicates in a single cycle
        assert len(cycle_ids) == len(unique_ids), (
            f"No duplicates should occur in one cycle. Got {len(cycle_ids)} selections "
            f"but only {len(unique_ids)} unique"
        )

    @given(st.integers(min_value=2, max_value=10), st.integers(min_value=2, max_value=5))
    def test_roundrobin_repeats_pattern_across_cycles(self, num_proxies: int, num_cycles: int):
        """Property: RoundRobin repeats the same pattern across multiple cycles."""
        pool = ProxyPool(name="test-pool")

        for i in range(num_proxies):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            proxy.health_status = HealthStatus.HEALTHY
            pool.add_proxy(proxy)

        strategy = RoundRobinStrategy()

        # Collect all selections
        all_urls = []
        for _ in range(num_proxies * num_cycles):
            selected = strategy.select(pool)
            all_urls.append(selected.url)

        # Split into cycles
        cycles = [all_urls[i * num_proxies : (i + 1) * num_proxies] for i in range(num_cycles)]

        # All cycles should have the same pattern
        first_cycle = cycles[0]
        for i, cycle in enumerate(cycles[1:], start=2):
            assert cycle == first_cycle, (
                f"Cycle {i} should match cycle 1. Cycle 1: {first_cycle}, Cycle {i}: {cycle}"
            )
