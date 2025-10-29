"""Integration tests for switching rotation strategies at runtime."""

from proxywhirl import (
    LeastUsedStrategy,
    Proxy,
    ProxyPool,
    RandomStrategy,
    RoundRobinStrategy,
    WeightedStrategy,
)
from proxywhirl.models import HealthStatus


class TestStrategySwitching:
    """Test switching between different rotation strategies."""

    def test_switch_from_round_robin_to_random(self):
        """Test switching from round-robin to random strategy."""
        # Create pool with proxies
        pool = ProxyPool(name="test-pool")
        proxies = []
        for i in range(3):
            proxy = Proxy(url=f"http://proxy{i + 1}.example.com:8080")
            proxy.health_status = HealthStatus.HEALTHY
            pool.add_proxy(proxy)
            proxies.append(proxy)

        # Start with round-robin
        strategy = RoundRobinStrategy()

        # Verify round-robin behavior - deterministic order
        first_sequence = [strategy.select(pool).url for _ in range(3)]
        expected_urls = [p.url for p in proxies]
        assert first_sequence == expected_urls, "Round-robin should follow predictable order"

        # Switch to random strategy
        strategy = RandomStrategy()

        # Verify random behavior - collect multiple sequences
        sequences = []
        for _ in range(10):
            sequence = [strategy.select(pool).url for _ in range(3)]
            sequences.append(tuple(sequence))

        # With random selection, we should see variation
        unique_sequences = len(set(sequences))
        assert unique_sequences > 1, (
            f"Random strategy should produce varied sequences, got {unique_sequences} unique"
        )

    def test_switch_from_random_to_weighted(self):
        """Test switching from random to weighted strategy."""
        pool = ProxyPool(name="test-pool")
        proxies = []
        for i in range(3):
            proxy = Proxy(url=f"http://proxy{i + 1}.example.com:8080")
            proxy.health_status = HealthStatus.HEALTHY
            pool.add_proxy(proxy)
            proxies.append(proxy)

        # Start with random
        strategy = RandomStrategy()

        # Use random for a while
        for _ in range(10):
            proxy_selection = strategy.select(pool)
            assert proxy_selection is not None

        # Give first proxy high success rate
        proxies[0].total_requests = 100
        proxies[0].total_successes = 95  # 95% success rate

        # Give others low success rate
        proxies[1].total_requests = 100
        proxies[1].total_successes = 10  # 10% success rate
        proxies[2].total_requests = 100
        proxies[2].total_successes = 10  # 10% success rate

        # Switch to weighted strategy
        strategy = WeightedStrategy()

        # First proxy should be selected more often
        selection_counts = {p.url: 0 for p in proxies}
        for _ in range(500):
            proxy_selection = strategy.select(pool)
            selection_counts[proxy_selection.url] += 1

        # First proxy (high success rate) should dominate
        assert selection_counts[proxies[0].url] > selection_counts[proxies[1].url]
        assert selection_counts[proxies[0].url] > selection_counts[proxies[2].url]

    def test_switch_from_weighted_to_least_used(self):
        """Test switching from weighted to least-used strategy."""
        pool = ProxyPool(name="test-pool")
        proxies = []
        for i in range(3):
            proxy = Proxy(url=f"http://proxy{i + 1}.example.com:8080")
            proxy.health_status = HealthStatus.HEALTHY
            pool.add_proxy(proxy)
            proxies.append(proxy)

        # Start with weighted
        strategy = WeightedStrategy()

        # Use weighted for a while
        for _ in range(30):
            proxy_selection = strategy.select(pool)
            assert proxy_selection is not None

        # Manually create uneven usage
        proxies[0].total_requests = 100
        proxies[1].total_requests = 50
        proxies[2].total_requests = 10

        # Switch to least-used strategy
        strategy = LeastUsedStrategy()

        # Should now favor least-used proxy (proxy3)
        next_proxy = strategy.select(pool)
        assert next_proxy.url == proxies[2].url, "Should select least-used proxy first"

        # Mark as used - increment enough to exceed proxy2's usage
        proxies[2].total_requests = 51  # Now more than proxy2 (50)

        # Should now select second-least-used (proxy2)
        next_proxy = strategy.select(pool)
        assert next_proxy.url == proxies[1].url, "Should select second-least-used proxy"

    def test_no_errors_during_strategy_switch(self):
        """Test that switching strategies mid-rotation doesn't cause errors."""
        pool = ProxyPool(name="test-pool")
        proxies = []
        for i in range(10):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            proxy.health_status = HealthStatus.HEALTHY
            pool.add_proxy(proxy)
            proxies.append(proxy)

        # Start with round-robin
        strategy = RoundRobinStrategy()

        # Start rotating
        for _ in range(5):
            proxy_selection = strategy.select(pool)
            assert proxy_selection is not None
            proxy_selection.total_requests += 1
            proxy_selection.total_successes += 1

        # Switch strategy in the middle
        strategy = RandomStrategy()

        # Continue rotating - should not error
        for _ in range(10):
            proxy_selection = strategy.select(pool)
            assert proxy_selection is not None
            proxy_selection.total_requests += 1
            proxy_selection.total_successes += 1

        # Switch again
        strategy = WeightedStrategy()

        # Continue rotating
        for _ in range(10):
            proxy_selection = strategy.select(pool)
            assert proxy_selection is not None
            proxy_selection.total_requests += 1
            proxy_selection.total_successes += 1

        # Switch one more time
        strategy = LeastUsedStrategy()

        # Final rotations
        for _ in range(10):
            proxy_selection = strategy.select(pool)
            assert proxy_selection is not None
            proxy_selection.total_requests += 1
            proxy_selection.total_successes += 1

        # Verify all strategies worked without errors
        total_requests = sum(p.total_requests for p in proxies)
        assert total_requests == 35  # 5 + 10 + 10 + 10


class TestStrategyStatePreservation:
    """Test that strategy switching preserves proxy pool state."""

    def test_proxy_stats_preserved_across_strategy_changes(self):
        """Test that proxy statistics are preserved when switching strategies."""
        pool = ProxyPool(name="test-pool")
        proxies = []
        for i in range(2):
            proxy = Proxy(url=f"http://proxy{i + 1}.example.com:8080")
            proxy.health_status = HealthStatus.HEALTHY
            pool.add_proxy(proxy)
            proxies.append(proxy)

        # Start with round-robin
        strategy = RoundRobinStrategy()

        # Build up some stats
        for _ in range(10):
            proxy_selection = strategy.select(pool)
            proxy_selection.total_requests += 1
            proxy_selection.total_successes += 1

        # Record stats before switch
        stats_before = {p.url: (p.total_requests, p.total_successes) for p in proxies}

        # Switch strategy
        strategy = RandomStrategy()

        # Stats should be preserved
        stats_after = {p.url: (p.total_requests, p.total_successes) for p in proxies}
        assert stats_after == stats_before, (
            "Proxy stats should be preserved across strategy changes"
        )

    def test_pool_composition_unchanged_after_strategy_switch(self):
        """Test that the proxy pool itself doesn't change when switching strategies."""
        pool = ProxyPool(name="test-pool")
        proxies = []
        for i in range(5):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            proxy.health_status = HealthStatus.HEALTHY
            pool.add_proxy(proxy)
            proxies.append(proxy)

        # Record pool state
        original_urls = {p.url for p in pool.proxies}
        original_pool_size = len(pool.proxies)

        # Switch strategy multiple times (strategies don't modify pool)
        strategy1 = RoundRobinStrategy()
        strategy2 = RandomStrategy()
        strategy3 = WeightedStrategy()
        strategy4 = LeastUsedStrategy()

        # Use each strategy
        for strategy in [strategy1, strategy2, strategy3, strategy4]:
            for _ in range(5):
                proxy_selection = strategy.select(pool)
                assert proxy_selection is not None

        # Pool should be unchanged
        current_urls = {p.url for p in pool.proxies}
        current_pool_size = len(pool.proxies)

        assert current_urls == original_urls, "Pool URLs should be unchanged"
        assert current_pool_size == original_pool_size, "Pool size should be unchanged"
