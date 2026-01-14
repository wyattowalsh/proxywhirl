"""
Property-based tests for rotation strategies using Hypothesis.

These tests verify that strategies maintain key invariants across
many randomly-generated test cases.
"""

from collections import Counter

from hypothesis import given, settings
from hypothesis import strategies as st

from proxywhirl.models import (
    HealthStatus,
    Proxy,
    ProxyPool,
    SelectionContext,
)
from proxywhirl.strategies import (
    LeastUsedStrategy,
    RandomStrategy,
    RoundRobinStrategy,
    WeightedStrategy,
)


class TestRoundRobinPropertyTests:
    """Property-based tests for RoundRobinStrategy."""

    @given(
        num_proxies=st.integers(min_value=1, max_value=20),
        num_selections=st.integers(min_value=10, max_value=100),
    )
    @settings(max_examples=50, deadline=None)
    def test_round_robin_achieves_uniform_distribution(self, num_proxies: int, num_selections: int):
        """
        Property: Round-robin should distribute requests uniformly (±1 variance).

        Given N healthy proxies and M selections (where M >> N),
        each proxy should be selected approximately M/N times,
        with at most ±1 request variance.
        """
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxies = [
            Proxy(url=f"http://proxy{i}.com:8080", health_status=HealthStatus.HEALTHY)
            for i in range(num_proxies)
        ]
        for proxy in proxies:
            pool.add_proxy(proxy)

        strategy = RoundRobinStrategy()
        context = SelectionContext()

        # Act - Make selections
        selections = [strategy.select(pool, context) for _ in range(num_selections)]

        # Assert - Count selections per proxy
        selection_counts = Counter(p.url for p in selections)

        # Calculate expected count and allowed variance
        expected_count = num_selections / num_proxies
        min_count = int(expected_count)  # Floor
        max_count = min_count + 1  # Ceiling

        # Every proxy should be selected between min_count and max_count times
        for count in selection_counts.values():
            assert min_count <= count <= max_count, (
                f"Selection count {count} outside expected range [{min_count}, {max_count}]. "
                f"Distribution: {selection_counts}"
            )

    @given(
        num_healthy=st.integers(min_value=1, max_value=10),
        num_unhealthy=st.integers(min_value=1, max_value=10),
        num_selections=st.integers(min_value=5, max_value=50),
    )
    @settings(max_examples=30, deadline=None)
    def test_round_robin_never_selects_unhealthy_proxies(
        self, num_healthy: int, num_unhealthy: int, num_selections: int
    ):
        """
        Property: Round-robin should never select unhealthy proxies.

        Given a pool with both healthy and unhealthy proxies,
        all selections should be from the healthy set.
        """
        # Arrange
        pool = ProxyPool(name="test-pool")

        # Add healthy proxies
        healthy_urls = {f"http://healthy{i}.com:8080" for i in range(num_healthy)}
        for url in healthy_urls:
            pool.add_proxy(Proxy(url=url, health_status=HealthStatus.HEALTHY))

        # Add unhealthy proxies
        for i in range(num_unhealthy):
            pool.add_proxy(Proxy(url=f"http://dead{i}.com:8080", health_status=HealthStatus.DEAD))

        strategy = RoundRobinStrategy()
        context = SelectionContext()

        # Act - Make selections
        selections = [strategy.select(pool, context) for _ in range(num_selections)]

        # Assert - All selections should be from healthy set
        selected_urls = {p.url for p in selections}
        assert selected_urls.issubset(healthy_urls), (
            f"Selected unhealthy proxy! Selected: {selected_urls}, Healthy: {healthy_urls}"
        )

    @given(
        num_proxies=st.integers(min_value=2, max_value=10),
    )
    @settings(max_examples=20, deadline=None)
    def test_round_robin_cycles_through_all_proxies(self, num_proxies: int):
        """
        Property: Round-robin should cycle through all proxies exactly once per cycle.

        Given N proxies, after N selections, all proxies should have been selected
        exactly once before any proxy is selected a second time.
        """
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxy_urls = [f"http://proxy{i}.com:8080" for i in range(num_proxies)]
        for url in proxy_urls:
            pool.add_proxy(Proxy(url=url, health_status=HealthStatus.HEALTHY))

        strategy = RoundRobinStrategy()
        context = SelectionContext()

        # Act - Select exactly N times (one complete cycle)
        first_cycle = [strategy.select(pool, context) for _ in range(num_proxies)]
        second_cycle = [strategy.select(pool, context) for _ in range(num_proxies)]

        # Assert - First cycle covers all proxies exactly once
        first_cycle_urls = [p.url for p in first_cycle]
        assert sorted(first_cycle_urls) == sorted(proxy_urls), (
            f"First cycle didn't cover all proxies. Got: {first_cycle_urls}"
        )

        # Assert - Second cycle is identical to first cycle (deterministic)
        second_cycle_urls = [p.url for p in second_cycle]
        assert first_cycle_urls == second_cycle_urls, (
            f"Second cycle differs from first. First: {first_cycle_urls}, "
            f"Second: {second_cycle_urls}"
        )


class TestRandomPropertyTests:
    """Property-based tests for RandomStrategy."""

    @given(
        num_proxies=st.integers(min_value=2, max_value=10),
        multiplier=st.integers(min_value=15, max_value=30),
    )
    @settings(max_examples=30, deadline=None)
    def test_random_eventually_selects_all_proxies(self, num_proxies: int, multiplier: int):
        """
        Property: Random strategy should eventually select all healthy proxies.

        Given enough selections (15-30x the number of proxies), all proxies
        should be selected at least once with high probability.
        """
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxy_urls = [f"http://proxy{i}.com:8080" for i in range(num_proxies)]
        for url in proxy_urls:
            pool.add_proxy(Proxy(url=url, health_status=HealthStatus.HEALTHY))

        strategy = RandomStrategy()
        context = SelectionContext()

        # Act - Make many selections (multiplier * num_proxies)
        num_selections = multiplier * num_proxies
        selections = [strategy.select(pool, context) for _ in range(num_selections)]

        # Assert - All proxies should appear at least once
        selected_urls = {p.url for p in selections}
        assert selected_urls == set(proxy_urls), (
            f"Not all proxies selected after {num_selections} selections. "
            f"Expected: {set(proxy_urls)}, Got: {selected_urls}"
        )

    @given(
        num_healthy=st.integers(min_value=1, max_value=10),
        num_unhealthy=st.integers(min_value=1, max_value=10),
        num_selections=st.integers(min_value=10, max_value=50),
    )
    @settings(max_examples=30, deadline=None)
    def test_random_never_selects_unhealthy_proxies(
        self, num_healthy: int, num_unhealthy: int, num_selections: int
    ):
        """
        Property: Random strategy should never select unhealthy proxies.
        """
        # Arrange
        pool = ProxyPool(name="test-pool")

        # Add healthy proxies
        healthy_urls = {f"http://healthy{i}.com:8080" for i in range(num_healthy)}
        for url in healthy_urls:
            pool.add_proxy(Proxy(url=url, health_status=HealthStatus.HEALTHY))

        # Add unhealthy proxies
        for i in range(num_unhealthy):
            pool.add_proxy(Proxy(url=f"http://dead{i}.com:8080", health_status=HealthStatus.DEAD))

        strategy = RandomStrategy()
        context = SelectionContext()

        # Act
        selections = [strategy.select(pool, context) for _ in range(num_selections)]

        # Assert
        selected_urls = {p.url for p in selections}
        assert selected_urls.issubset(healthy_urls), (
            f"Selected unhealthy proxy! Selected: {selected_urls}, Healthy: {healthy_urls}"
        )


class TestWeightedPropertyTests:
    """Property-based tests for WeightedStrategy."""

    @given(
        num_proxies=st.integers(min_value=2, max_value=10),
        num_selections=st.integers(min_value=500, max_value=1000),
    )
    @settings(max_examples=30, deadline=None)
    def test_weighted_distribution_within_variance(self, num_proxies: int, num_selections: int):
        """
        Property: Weighted selection should distribute with reasonable variance.

        Over many selections (500-1000), the distribution should roughly
        follow the weights (within 25% variance for uniform weights).
        Random selection has inherent statistical variance, especially
        with smaller sample sizes or more proxies.
        """
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxies = []
        for i in range(num_proxies):
            proxy = Proxy(url=f"http://proxy{i}.com:8080", health_status=HealthStatus.HEALTHY)
            # Give all proxies similar success rates (0.4-0.6 range)
            proxy.total_requests = 100
            proxy.total_successes = 50  # 50% success rate
            proxies.append(proxy)
            pool.add_proxy(proxy)

        strategy = WeightedStrategy()

        # Act
        selections = [strategy.select(pool) for _ in range(num_selections)]

        # Assert - With uniform weights, variance should be reasonable
        selection_counts = Counter(p.url for p in selections)
        expected_count = num_selections / num_proxies

        for count in selection_counts.values():
            variance = abs(count - expected_count) / expected_count
            assert variance <= 0.30, (  # 30% variance allows for statistical reality
                f"Selection variance {variance:.2%} exceeds 30% threshold. "
                f"Count: {count}, Expected: {expected_count:.1f}, "
                f"Distribution: {selection_counts}"
            )

    @given(
        num_selections=st.integers(min_value=100, max_value=500),
    )
    @settings(max_examples=20, deadline=None)
    def test_weighted_favors_high_performers(self, num_selections: int):
        """
        Property: Proxies with higher success rates should be selected more often.
        """
        # Arrange
        pool = ProxyPool(name="test-pool")

        # High performer (80% success rate)
        high = Proxy(url="http://high.com:8080", health_status=HealthStatus.HEALTHY)
        high.total_requests = 100
        high.total_successes = 80  # 80% success rate
        pool.add_proxy(high)

        # Low performer (20% success rate)
        low = Proxy(url="http://low.com:8080", health_status=HealthStatus.HEALTHY)
        low.total_requests = 100
        low.total_successes = 20  # 20% success rate
        pool.add_proxy(low)

        strategy = WeightedStrategy()

        # Act
        selections = [strategy.select(pool) for _ in range(num_selections)]
        high_count = sum(1 for s in selections if s.url == "http://high.com:8080")
        low_count = sum(1 for s in selections if s.url == "http://low.com:8080")

        # Assert - High performer should be selected at least 1.5x more often
        # (Conservative check given 80% vs 20% = 4:1 weight ratio)
        assert high_count > low_count * 1.5, (
            f"High performer not favored enough. High: {high_count}, Low: {low_count}"
        )

    @given(
        num_healthy=st.integers(min_value=1, max_value=10),
        num_unhealthy=st.integers(min_value=1, max_value=10),
        num_selections=st.integers(min_value=10, max_value=50),
    )
    @settings(max_examples=30, deadline=None)
    def test_weighted_never_selects_unhealthy_proxies(
        self, num_healthy: int, num_unhealthy: int, num_selections: int
    ):
        """
        Property: Weighted strategy should never select unhealthy proxies.
        """
        # Arrange
        pool = ProxyPool(name="test-pool")

        # Add healthy proxies
        healthy_urls = {f"http://healthy{i}.com:8080" for i in range(num_healthy)}
        for url in healthy_urls:
            proxy = Proxy(url=url, health_status=HealthStatus.HEALTHY)
            proxy.total_requests = 100
            proxy.total_successes = 50
            pool.add_proxy(proxy)

        # Add unhealthy proxies with HIGH success rates (tempting but should be ignored)
        for i in range(num_unhealthy):
            proxy = Proxy(url=f"http://dead{i}.com:8080", health_status=HealthStatus.DEAD)
            proxy.total_requests = 100
            proxy.total_successes = 95  # 95% success rate (very tempting!)
            pool.add_proxy(proxy)

        strategy = WeightedStrategy()

        # Act
        selections = [strategy.select(pool) for _ in range(num_selections)]

        # Assert
        selected_urls = {p.url for p in selections}
        assert selected_urls.issubset(healthy_urls), (
            f"Selected unhealthy proxy! Selected: {selected_urls}, Healthy: {healthy_urls}"
        )


class TestLeastUsedPropertyTests:
    """Property-based tests for LeastUsedStrategy."""

    @given(
        num_proxies=st.integers(min_value=2, max_value=15),
        num_selections=st.integers(min_value=10, max_value=100),
    )
    @settings(max_examples=30, deadline=None)
    def test_least_used_balances_load_over_time(self, num_proxies: int, num_selections: int):
        """
        Property: Least-used should balance load across proxies.

        After many selections, the variance in requests_started should be
        minimal (at most 1 request difference between any two proxies).
        """
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxies = [
            Proxy(url=f"http://proxy{i}.com:8080", health_status=HealthStatus.HEALTHY)
            for i in range(num_proxies)
        ]
        for proxy in proxies:
            pool.add_proxy(proxy)

        strategy = LeastUsedStrategy()
        context = SelectionContext()

        # Act - Make selections (without completing requests)
        for _ in range(num_selections):
            strategy.select(pool, context)

        # Assert - Check load distribution
        request_counts = [p.requests_started for p in pool.get_all_proxies()]
        min_count = min(request_counts)
        max_count = max(request_counts)

        # Variance should be at most 1 (perfect or near-perfect balance)
        assert max_count - min_count <= 1, (
            f"Load imbalance detected. Min: {min_count}, Max: {max_count}. Counts: {request_counts}"
        )

    @given(
        num_proxies=st.integers(min_value=2, max_value=10),
    )
    @settings(max_examples=20, deadline=None)
    def test_least_used_always_selects_minimum(self, num_proxies: int):
        """
        Property: Least-used should always select the proxy with fewest started requests.
        """
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxies = [
            Proxy(url=f"http://proxy{i}.com:8080", health_status=HealthStatus.HEALTHY)
            for i in range(num_proxies)
        ]

        # Set different request counts
        for i, proxy in enumerate(proxies):
            proxy.requests_started = i * 10  # 0, 10, 20, ...
            pool.add_proxy(proxy)

        strategy = LeastUsedStrategy()
        context = SelectionContext()

        # Act
        selected = strategy.select(pool, context)

        # Assert - Should select proxy0 with 0 requests (after incrementing by start_request, it becomes 1)
        assert selected.url == "http://proxy0.com:8080"
        # After selection, requests_started is incremented
        assert selected.requests_started == 1

    @given(
        num_healthy=st.integers(min_value=1, max_value=10),
        num_unhealthy=st.integers(min_value=1, max_value=10),
        num_selections=st.integers(min_value=5, max_value=50),
    )
    @settings(max_examples=30, deadline=None)
    def test_least_used_never_selects_unhealthy_proxies(
        self, num_healthy: int, num_unhealthy: int, num_selections: int
    ):
        """
        Property: Least-used should never select unhealthy proxies.
        """
        # Arrange
        pool = ProxyPool(name="test-pool")

        # Add healthy proxies
        healthy_urls = {f"http://healthy{i}.com:8080" for i in range(num_healthy)}
        for url in healthy_urls:
            pool.add_proxy(Proxy(url=url, health_status=HealthStatus.HEALTHY))

        # Add unhealthy proxies with LOW request counts (tempting but should be ignored)
        for i in range(num_unhealthy):
            proxy = Proxy(url=f"http://dead{i}.com:8080", health_status=HealthStatus.DEAD)
            proxy.requests_started = 0  # Most tempting (least used)
            pool.add_proxy(proxy)

        strategy = LeastUsedStrategy()
        context = SelectionContext()

        # Act
        selections = [strategy.select(pool, context) for _ in range(num_selections)]

        # Assert
        selected_urls = {p.url for p in selections}
        assert selected_urls.issubset(healthy_urls), (
            f"Selected unhealthy proxy! Selected: {selected_urls}, Healthy: {healthy_urls}"
        )
