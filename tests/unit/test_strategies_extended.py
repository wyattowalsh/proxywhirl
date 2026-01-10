"""
Unit tests for extended rotation strategies (Random, Weighted, LeastUsed).
"""

import pytest

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import HealthStatus, Proxy, ProxyPool
from proxywhirl.strategies import LeastUsedStrategy, RandomStrategy, WeightedStrategy

# ==============================================================================
# Parametrized Tests for Common Strategy Behaviors
# ==============================================================================


@pytest.mark.parametrize(
    "strategy_class",
    [RandomStrategy, WeightedStrategy, LeastUsedStrategy],
    ids=["random", "weighted", "least_used"],
)
class TestStrategyCommonBehavior:
    """Parametrized tests for behaviors common to all strategies."""

    def test_empty_pool_raises_error(self, strategy_class):
        """Test that empty pool raises ProxyPoolEmptyError for all strategies."""
        pool = ProxyPool(name="test-pool")
        strategy = strategy_class()

        with pytest.raises(ProxyPoolEmptyError):
            strategy.select(pool)

    def test_skips_unhealthy_proxies(self, strategy_class):
        """Test that all strategies skip unhealthy proxies."""
        pool = ProxyPool(name="test-pool")
        healthy = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        pool.add_proxy(healthy)
        pool.add_proxy(Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.DEAD))  # type: ignore

        strategy = strategy_class()

        # Should only select healthy proxy
        for _ in range(10):
            assert strategy.select(pool).id == healthy.id


# ==============================================================================
# RandomStrategy Tests
# ==============================================================================


class TestRandomStrategy:
    """Test RandomStrategy implementation."""

    def test_random_selection_from_pool(self):
        """Test that random strategy selects from available proxies."""
        pool = ProxyPool(name="test-pool")
        proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        proxy3 = Proxy(url="http://proxy3.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)
        pool.add_proxy(proxy3)

        strategy = RandomStrategy()

        # Make multiple selections
        selected_ids = {strategy.select(pool).id for _ in range(20)}

        # Should select from available proxies (at least 2 different ones in 20 tries)
        assert len(selected_ids) >= 2

    def test_random_distribution(self):
        """Test that random strategy has reasonable distribution."""
        pool = ProxyPool(name="test-pool")
        proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        strategy = RandomStrategy()

        # Count selections
        counts = {proxy1.id: 0, proxy2.id: 0}
        for _ in range(100):
            selected = strategy.select(pool)
            counts[selected.id] += 1

        # Both should be selected at least once
        assert counts[proxy1.id] > 0
        assert counts[proxy2.id] > 0


# ==============================================================================
# WeightedStrategy Tests
# ==============================================================================


class TestWeightedStrategy:
    """Test WeightedStrategy implementation."""

    def test_weighted_selection_prefers_high_success_rate(self):
        """Test that weighted strategy prefers proxies with higher success rates."""
        pool = ProxyPool(name="test-pool")

        # Proxy with high success rate
        proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        proxy1.total_requests = 100
        proxy1.total_successes = 90  # 90% success rate

        # Proxy with low success rate
        proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        proxy2.total_requests = 100
        proxy2.total_successes = 30  # 30% success rate

        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        strategy = WeightedStrategy()

        # Make multiple selections
        counts = {proxy1.id: 0, proxy2.id: 0}
        for _ in range(100):
            selected = strategy.select(pool)
            counts[selected.id] += 1

        # Proxy1 should be selected more often than proxy2
        assert counts[proxy1.id] > counts[proxy2.id]

    def test_weighted_handles_zero_requests(self):
        """Test that weighted strategy handles proxies with zero requests."""
        pool = ProxyPool(name="test-pool")
        proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        strategy = WeightedStrategy()

        # Should not crash when proxies have no history
        selected = strategy.select(pool)
        assert selected in [proxy1, proxy2]

    def test_weighted_equal_weights_random_selection(self):
        """Test that equal weights result in roughly equal selection."""
        pool = ProxyPool(name="test-pool")

        proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        proxy1.total_requests = 100
        proxy1.total_successes = 50

        proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        proxy2.total_requests = 100
        proxy2.total_successes = 50

        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        strategy = WeightedStrategy()

        # Make selections
        counts = {proxy1.id: 0, proxy2.id: 0}
        for _ in range(100):
            selected = strategy.select(pool)
            counts[selected.id] += 1

        # Should be roughly equal (within reasonable variance)
        assert counts[proxy1.id] > 20  # At least 20%
        assert counts[proxy2.id] > 20


# ==============================================================================
# LeastUsedStrategy Tests
# ==============================================================================


class TestLeastUsedStrategy:
    """Test LeastUsedStrategy implementation."""

    def test_selects_least_used_proxy(self):
        """Test that strategy selects proxy with fewest requests."""
        pool = ProxyPool(name="test-pool")

        proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        proxy1.requests_started = 100

        proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        proxy2.requests_started = 50  # Least used

        proxy3 = Proxy(url="http://proxy3.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        proxy3.requests_started = 75

        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)
        pool.add_proxy(proxy3)

        strategy = LeastUsedStrategy()

        # Should select proxy2 (least used)
        selected = strategy.select(pool)
        assert selected.id == proxy2.id

    def test_balances_usage_over_time(self):
        """Test that strategy balances usage across proxies."""
        pool = ProxyPool(name="test-pool")

        proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        proxy1.requests_started = 10

        proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        proxy2.requests_started = 0

        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        strategy = LeastUsedStrategy()

        # First 10 selections should all be proxy2 (0→10 vs proxy1 at 10)
        for i in range(10):
            selected = strategy.select(pool)
            assert selected.id == proxy2.id, f"Selection {i + 1} should be proxy2"
        # After 10 selections, proxy2.requests_started is now 10 (equal to proxy1)

        # Next selection should be proxy1 (both at 10, but proxy1 was added first)
        # Actually, when equal, min() returns the first one in the list
        selected_11 = strategy.select(pool)
        # Either proxy1 or proxy2 is acceptable when tied
        assert selected_11.id in {proxy1.id, proxy2.id}

    def test_handles_equal_usage(self):
        """Test that strategy handles proxies with equal usage."""
        pool = ProxyPool(name="test-pool")

        proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        proxy1.requests_started = 50

        proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        proxy2.requests_started = 50

        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        strategy = LeastUsedStrategy()

        # Should select one of them (both have same usage)
        selected = strategy.select(pool)
        assert selected in [proxy1, proxy2]
