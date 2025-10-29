"""
Unit tests for rotation strategies.
"""

import pytest

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import HealthStatus, Proxy, ProxyPool
from proxywhirl.strategies import (
    LeastUsedStrategy,
    RandomStrategy,
    RoundRobinStrategy,
    WeightedStrategy,
)


class TestRoundRobinStrategy:
    """Test RoundRobinStrategy implementation."""

    def test_sequential_selection(self):
        """Test that proxies are selected sequentially."""
        pool = ProxyPool(name="test-pool")
        pool.add_proxy(
            Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
        )  # type: ignore
        pool.add_proxy(
            Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY)
        )  # type: ignore
        pool.add_proxy(
            Proxy(url="http://proxy3.example.com:8080", health_status=HealthStatus.HEALTHY)
        )  # type: ignore

        strategy = RoundRobinStrategy()

        # First selection should be proxy1
        proxy1 = strategy.select(pool)
        # Second selection should be proxy2
        proxy2 = strategy.select(pool)
        # Third selection should be proxy3
        proxy3 = strategy.select(pool)

        # Verify they're all different
        assert proxy1.id != proxy2.id
        assert proxy2.id != proxy3.id
        assert proxy1.id != proxy3.id

    def test_wraparound_after_last_proxy(self):
        """Test that selection wraps around to first proxy after last."""
        pool = ProxyPool(name="test-pool")
        pool.add_proxy(
            Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
        )  # type: ignore
        pool.add_proxy(
            Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY)
        )  # type: ignore

        strategy = RoundRobinStrategy()

        # Select all proxies
        first_round = [strategy.select(pool) for _ in range(2)]

        # Select again - should wrap around
        second_round_first = strategy.select(pool)

        # Should get the same proxy as first selection
        assert second_round_first.id == first_round[0].id

    def test_empty_pool_raises_error(self):
        """Test that selecting from empty pool raises ProxyPoolEmptyError."""
        pool = ProxyPool(name="test-pool")
        strategy = RoundRobinStrategy()

        with pytest.raises(ProxyPoolEmptyError):
            strategy.select(pool)

    def test_only_unhealthy_proxies_raises_error(self):
        """Test that pool with only unhealthy proxies raises error."""
        pool = ProxyPool(name="test-pool")
        pool.add_proxy(Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.DEAD))  # type: ignore
        pool.add_proxy(
            Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.UNHEALTHY)
        )  # type: ignore

        strategy = RoundRobinStrategy()

        with pytest.raises(ProxyPoolEmptyError, match="No healthy proxies"):
            strategy.select(pool)

    def test_skips_unhealthy_proxies(self):
        """Test that strategy skips unhealthy proxies."""
        pool = ProxyPool(name="test-pool")
        healthy_proxy = Proxy(
            url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY
        )  # type: ignore
        pool.add_proxy(healthy_proxy)
        pool.add_proxy(Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.DEAD))  # type: ignore

        strategy = RoundRobinStrategy()

        # Should only select the healthy proxy
        for _ in range(3):
            selected = strategy.select(pool)
            assert selected.id == healthy_proxy.id

    def test_record_result_updates_proxy_stats(self):
        """Test that record_result updates proxy statistics."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        pool.add_proxy(proxy)

        strategy = RoundRobinStrategy()
        strategy.record_result(proxy, success=True, response_time_ms=150.0)

        assert proxy.total_successes == 1
        assert proxy.average_response_time_ms == 150.0

    def test_record_result_failure_updates_stats(self):
        """Test that record_result updates stats on failure."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        pool.add_proxy(proxy)

        strategy = RoundRobinStrategy()
        strategy.record_result(proxy, success=False, response_time_ms=0.0)

        assert proxy.total_failures == 1
        assert proxy.consecutive_failures == 1

    def test_multiple_instances_independent_state(self):
        """Test that multiple strategy instances maintain independent state."""
        pool = ProxyPool(name="test-pool")
        pool.add_proxy(
            Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
        )  # type: ignore
        pool.add_proxy(
            Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY)
        )  # type: ignore

        strategy1 = RoundRobinStrategy()
        strategy2 = RoundRobinStrategy()

        # Both should start from same position
        proxy1_s1 = strategy1.select(pool)
        proxy1_s2 = strategy2.select(pool)

        assert proxy1_s1.id == proxy1_s2.id


class TestRandomStrategy:
    """Test RandomStrategy implementation."""

    def test_random_selection(self):
        """Test that selection is random (probabilistic test)."""
        pool = ProxyPool(name="test-pool")
        for i in range(5):
            pool.add_proxy(
                Proxy(url=f"http://proxy{i}.example.com:8080", health_status=HealthStatus.HEALTHY)
            )  # type: ignore

        strategy = RandomStrategy()

        # Select multiple times and check we get different proxies
        selections = [strategy.select(pool).url for _ in range(20)]

        # Should have at least 2 different proxies selected
        unique_selections = set(selections)
        assert len(unique_selections) >= 2

    def test_empty_pool_raises_error(self):
        """Test that selecting from empty pool raises ProxyPoolEmptyError."""
        pool = ProxyPool(name="test-pool")
        strategy = RandomStrategy()

        with pytest.raises(ProxyPoolEmptyError):
            strategy.select(pool)


class TestWeightedStrategy:
    """Test WeightedStrategy implementation."""

    def test_higher_success_rate_selected_more(self):
        """Test that proxies with higher success rates are favored."""
        pool = ProxyPool(name="test-pool")

        # Create proxy with high success rate
        good_proxy = Proxy(url="http://good.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        good_proxy.total_requests = 100
        good_proxy.total_successes = 95
        pool.add_proxy(good_proxy)

        # Create proxy with low success rate
        bad_proxy = Proxy(url="http://bad.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        bad_proxy.total_requests = 100
        bad_proxy.total_successes = 50
        pool.add_proxy(bad_proxy)

        strategy = WeightedStrategy()

        # Select many times and count
        selections = [strategy.select(pool).url for _ in range(100)]
        good_count = sum(1 for url in selections if "good" in url)
        bad_count = sum(1 for url in selections if "bad" in url)

        # Good proxy should be selected more often
        assert good_count > bad_count

    def test_untested_proxies_have_default_weight(self):
        """Test that proxies with no requests get default weight."""
        pool = ProxyPool(name="test-pool")

        # Proxy with no requests
        new_proxy = Proxy(url="http://new.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        pool.add_proxy(new_proxy)

        # Proxy with requests
        tested_proxy = Proxy(
            url="http://tested.example.com:8080", health_status=HealthStatus.HEALTHY
        )  # type: ignore
        tested_proxy.total_requests = 10
        tested_proxy.total_successes = 8
        pool.add_proxy(tested_proxy)

        strategy = WeightedStrategy()

        # Should be able to select both (increase iterations for reliability)
        selections = [strategy.select(pool).url for _ in range(100)]
        assert any("new" in url for url in selections)
        assert any("tested" in url for url in selections)


class TestLeastUsedStrategy:
    """Test LeastUsedStrategy implementation."""

    def test_selects_least_used_proxy(self):
        """Test that proxy with fewest requests is selected."""
        pool = ProxyPool(name="test-pool")

        # Create proxies with different usage counts
        proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        proxy1.total_requests = 10
        pool.add_proxy(proxy1)

        proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        proxy2.total_requests = 5
        pool.add_proxy(proxy2)

        proxy3 = Proxy(url="http://proxy3.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        proxy3.total_requests = 15
        pool.add_proxy(proxy3)

        strategy = LeastUsedStrategy()

        # Should select proxy2 (least used)
        selected = strategy.select(pool)
        assert selected.url == "http://proxy2.example.com:8080"

    def test_distributes_evenly(self):
        """Test that strategy distributes load evenly over time."""
        pool = ProxyPool(name="test-pool")

        for i in range(3):
            pool.add_proxy(
                Proxy(url=f"http://proxy{i}.example.com:8080", health_status=HealthStatus.HEALTHY)
            )  # type: ignore

        strategy = LeastUsedStrategy()

        # Select multiple times and update counts
        for _ in range(30):
            proxy = strategy.select(pool)
            strategy.record_result(proxy, success=True, response_time_ms=100.0)

        # All proxies should have been used approximately equally
        request_counts = [p.total_requests for p in pool.proxies]
        max_diff = max(request_counts) - min(request_counts)

        # Difference should be small (at most 1 since we distribute evenly)
        assert max_diff <= 1
