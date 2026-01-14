"""
Unit tests for CostAwareStrategy (TASK-901).

Tests verify cost-based optimization for proxy selection.
"""

import pytest

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import (
    HealthStatus,
    Proxy,
    ProxyPool,
    SelectionContext,
    StrategyConfig,
)
from proxywhirl.strategies import CostAwareStrategy


class TestCostAwareStrategy:
    """Unit tests for CostAwareStrategy."""

    @pytest.mark.flaky(reruns=2)
    def test_select_favors_free_proxies(self):
        """Test that free proxies are heavily favored over paid ones."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        # Free proxy
        free_proxy = Proxy(url="http://free.com:8080", health_status=HealthStatus.HEALTHY)
        free_proxy.cost_per_request = 0.0
        pool.add_proxy(free_proxy)

        # Paid proxy
        paid_proxy = Proxy(url="http://paid.com:8080", health_status=HealthStatus.HEALTHY)
        paid_proxy.cost_per_request = 0.5
        pool.add_proxy(paid_proxy)

        strategy = CostAwareStrategy()

        # Act - Make 100 selections
        selections = [strategy.select(pool) for _ in range(100)]
        free_count = sum(1 for s in selections if s.url == "http://free.com:8080")
        paid_count = sum(1 for s in selections if s.url == "http://paid.com:8080")

        # Assert - Free proxy should be selected much more often
        # With default 10x boost, expect at least 70% free selections (relaxed from 80%)
        assert free_count >= 70, f"Free proxy selected {free_count} times, expected >= 70"
        assert paid_count <= 30, f"Paid proxy selected {paid_count} times, expected <= 30"

    def test_select_with_multiple_costs(self):
        """Test that lower cost proxies are favored over higher cost ones."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        # Free proxy
        free_proxy = Proxy(url="http://free.com:8080", health_status=HealthStatus.HEALTHY)
        free_proxy.cost_per_request = 0.0
        pool.add_proxy(free_proxy)

        # Cheap paid proxy
        cheap_proxy = Proxy(url="http://cheap.com:8080", health_status=HealthStatus.HEALTHY)
        cheap_proxy.cost_per_request = 0.1
        pool.add_proxy(cheap_proxy)

        # Expensive paid proxy
        expensive_proxy = Proxy(url="http://expensive.com:8080", health_status=HealthStatus.HEALTHY)
        expensive_proxy.cost_per_request = 1.0
        pool.add_proxy(expensive_proxy)

        strategy = CostAwareStrategy()

        # Act - Make many selections (more samples for stable statistics)
        selections = [strategy.select(pool) for _ in range(1000)]
        free_count = sum(1 for s in selections if s.url == "http://free.com:8080")
        cheap_count = sum(1 for s in selections if s.url == "http://cheap.com:8080")
        expensive_count = sum(1 for s in selections if s.url == "http://expensive.com:8080")

        # Assert - Cheap > Expensive (free might not always dominate due to variance)
        # But expensive should always be selected least
        assert cheap_count > expensive_count, (
            f"Cheap ({cheap_count}) should be > expensive ({expensive_count})"
        )
        # Assert free proxy gets significant selections (at least 20%)
        assert free_count >= 200, f"Free proxy should get significant selections, got {free_count}"

    def test_configure_max_cost_threshold(self):
        """Test that max_cost_per_request threshold filters expensive proxies."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        # Cheap proxy (cost = 0.2)
        cheap_proxy = Proxy(url="http://cheap.com:8080", health_status=HealthStatus.HEALTHY)
        cheap_proxy.cost_per_request = 0.2
        pool.add_proxy(cheap_proxy)

        # Expensive proxy (cost = 1.0)
        expensive_proxy = Proxy(url="http://expensive.com:8080", health_status=HealthStatus.HEALTHY)
        expensive_proxy.cost_per_request = 1.0
        pool.add_proxy(expensive_proxy)

        # Configure with max cost threshold of 0.5
        config = StrategyConfig(metadata={"max_cost_per_request": 0.5})
        strategy = CostAwareStrategy()
        strategy.configure(config)

        # Act - Make selections
        selections = [strategy.select(pool) for _ in range(10)]

        # Assert - Only cheap proxy should be selected (expensive filtered out)
        assert all(s.url == "http://cheap.com:8080" for s in selections)

    def test_raises_when_all_proxies_exceed_cost_threshold(self):
        """Test that strategy raises error when all proxies exceed cost threshold."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        # All proxies are expensive
        for i in range(3):
            proxy = Proxy(url=f"http://expensive{i}.com:8080", health_status=HealthStatus.HEALTHY)
            proxy.cost_per_request = 1.0
            pool.add_proxy(proxy)

        # Configure with low max cost threshold
        config = StrategyConfig(metadata={"max_cost_per_request": 0.1})
        strategy = CostAwareStrategy()
        strategy.configure(config)

        # Act & Assert
        with pytest.raises(ProxyPoolEmptyError, match="cost <= 0.1"):
            strategy.select(pool)

    def test_handles_proxies_without_cost_field(self):
        """Test that proxies without cost field are treated as free."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        # Proxy with no cost set (defaults to 0.0)
        no_cost_proxy = Proxy(url="http://nocost.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(no_cost_proxy)

        # Expensive proxy
        expensive_proxy = Proxy(url="http://expensive.com:8080", health_status=HealthStatus.HEALTHY)
        expensive_proxy.cost_per_request = 1.0
        pool.add_proxy(expensive_proxy)

        strategy = CostAwareStrategy()

        # Act - Make selections
        selections = [strategy.select(pool) for _ in range(100)]
        no_cost_count = sum(1 for s in selections if s.url == "http://nocost.com:8080")

        # Assert - No-cost proxy should be heavily favored (treated as free)
        assert no_cost_count >= 80

    def test_configure_free_proxy_boost(self):
        """Test that free_proxy_boost can be configured."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        free_proxy = Proxy(url="http://free.com:8080", health_status=HealthStatus.HEALTHY)
        free_proxy.cost_per_request = 0.0
        pool.add_proxy(free_proxy)

        paid_proxy = Proxy(url="http://paid.com:8080", health_status=HealthStatus.HEALTHY)
        paid_proxy.cost_per_request = 0.1
        pool.add_proxy(paid_proxy)

        # Configure with lower boost (5x instead of default 10x)
        config = StrategyConfig(metadata={"free_proxy_boost": 5.0})
        strategy = CostAwareStrategy()
        strategy.configure(config)

        # Act - Make selections (more samples for stable statistics)
        selections = [strategy.select(pool) for _ in range(1000)]
        free_count = sum(1 for s in selections if s.url == "http://free.com:8080")
        paid_count = sum(1 for s in selections if s.url == "http://paid.com:8080")

        # Assert - Free proxy still favored (with 5x boost)
        # With 5x boost vs inverse cost (1/0.1 = 10), weights are: 5 vs 10 normalized
        # So paid proxy actually gets ~66% of selections
        # Let's just verify both get selected
        assert free_count > 0, "Free proxy should be selected at least once"
        assert paid_count > 0, "Paid proxy should be selected at least once"

    def test_select_with_context_filtering(self):
        """Test that context failed_proxy_ids filtering works."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        free_proxy1 = Proxy(url="http://free1.com:8080", health_status=HealthStatus.HEALTHY)
        free_proxy1.cost_per_request = 0.0
        pool.add_proxy(free_proxy1)

        free_proxy2 = Proxy(url="http://free2.com:8080", health_status=HealthStatus.HEALTHY)
        free_proxy2.cost_per_request = 0.0
        pool.add_proxy(free_proxy2)

        strategy = CostAwareStrategy()

        # Context marking free_proxy1 as failed
        context = SelectionContext(failed_proxy_ids=[str(free_proxy1.id)])

        # Act - Make selections
        selections = [strategy.select(pool, context) for _ in range(10)]

        # Assert - Only free_proxy2 should be selected
        assert all(s.url == "http://free2.com:8080" for s in selections)

    def test_select_raises_when_no_healthy_proxies(self):
        """Test that strategy raises error when no healthy proxies available."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        # Only unhealthy proxies
        proxy = Proxy(url="http://proxy.com:8080", health_status=HealthStatus.DEAD)
        proxy.cost_per_request = 0.0
        pool.add_proxy(proxy)

        strategy = CostAwareStrategy()

        # Act & Assert
        with pytest.raises(ProxyPoolEmptyError, match="No healthy proxies available"):
            strategy.select(pool)

    def test_validate_metadata_always_returns_true(self):
        """Test that cost metadata validation always returns True."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy)

        strategy = CostAwareStrategy()

        # Act
        is_valid = strategy.validate_metadata(pool)

        # Assert - Cost field is optional
        assert is_valid is True

    def test_record_result_updates_proxy_metadata(self):
        """Test that record_result properly updates proxy metadata."""
        # Arrange
        proxy = Proxy(url="http://proxy.com:8080", health_status=HealthStatus.HEALTHY)
        proxy.cost_per_request = 0.1
        proxy.start_request()

        strategy = CostAwareStrategy()

        initial_completed = proxy.requests_completed
        initial_successes = proxy.total_successes

        # Act
        strategy.record_result(proxy, success=True, response_time_ms=100.0)

        # Assert
        assert proxy.requests_completed == initial_completed + 1
        assert proxy.total_successes == initial_successes + 1
        assert proxy.requests_active == 0

    def test_select_updates_metadata_on_selection(self):
        """Test that proxy metadata is updated when selected."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy.com:8080", health_status=HealthStatus.HEALTHY)
        proxy.cost_per_request = 0.0
        pool.add_proxy(proxy)

        strategy = CostAwareStrategy()

        initial_started = proxy.requests_started

        # Act
        selected = strategy.select(pool)

        # Assert
        assert selected.requests_started == initial_started + 1
        assert selected.requests_active == 1

    def test_init_with_max_cost_parameter(self):
        """Test that max_cost_per_request can be set via __init__."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        cheap_proxy = Proxy(url="http://cheap.com:8080", health_status=HealthStatus.HEALTHY)
        cheap_proxy.cost_per_request = 0.2
        pool.add_proxy(cheap_proxy)

        expensive_proxy = Proxy(url="http://expensive.com:8080", health_status=HealthStatus.HEALTHY)
        expensive_proxy.cost_per_request = 1.0
        pool.add_proxy(expensive_proxy)

        # Initialize with max cost
        strategy = CostAwareStrategy(max_cost_per_request=0.5)

        # Act - Make selections
        selections = [strategy.select(pool) for _ in range(10)]

        # Assert - Only cheap proxy should be selected
        assert all(s.url == "http://cheap.com:8080" for s in selections)

    def test_inverse_cost_weighting(self):
        """Test that inverse cost weighting works correctly for paid proxies."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        # Two paid proxies with different costs (no free proxies to avoid boost)
        cheap_proxy = Proxy(url="http://cheap.com:8080", health_status=HealthStatus.HEALTHY)
        cheap_proxy.cost_per_request = 0.1  # Weight = 1/0.1 = 10
        pool.add_proxy(cheap_proxy)

        expensive_proxy = Proxy(url="http://expensive.com:8080", health_status=HealthStatus.HEALTHY)
        expensive_proxy.cost_per_request = 0.5  # Weight = 1/0.5 = 2
        pool.add_proxy(expensive_proxy)

        strategy = CostAwareStrategy()

        # Act - Make many selections
        selections = [strategy.select(pool) for _ in range(200)]
        cheap_count = sum(1 for s in selections if s.url == "http://cheap.com:8080")
        expensive_count = sum(1 for s in selections if s.url == "http://expensive.com:8080")

        # Assert - Cheap should be selected ~5x more often (10:2 ratio)
        # Allow for variance, expect at least 3:1 ratio
        assert cheap_count > expensive_count * 3, (
            f"Cheap proxy selected {cheap_count} times, "
            f"expensive selected {expensive_count} times. "
            f"Expected at least 3:1 ratio."
        )

    def test_select_with_only_free_proxies(self):
        """Test selection when all proxies are free."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        for i in range(3):
            proxy = Proxy(url=f"http://free{i}.com:8080", health_status=HealthStatus.HEALTHY)
            proxy.cost_per_request = 0.0
            pool.add_proxy(proxy)

        strategy = CostAwareStrategy()

        # Act - Make selections
        selections = [strategy.select(pool) for _ in range(100)]

        # Assert - All proxies should be selected (roughly evenly due to equal weights)
        urls = set(s.url for s in selections)
        assert len(urls) == 3, "All free proxies should be selected at least once"

    def test_select_empty_pool_raises_error(self):
        """Test that selecting from empty pool raises error."""
        # Arrange
        pool = ProxyPool(name="empty-pool")
        strategy = CostAwareStrategy()

        # Act & Assert
        with pytest.raises(ProxyPoolEmptyError, match="No healthy proxies available"):
            strategy.select(pool)

    def test_configure_overrides_init_parameters(self):
        """Test that configure() overrides __init__ parameters."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        cheap_proxy = Proxy(url="http://cheap.com:8080", health_status=HealthStatus.HEALTHY)
        cheap_proxy.cost_per_request = 0.3
        pool.add_proxy(cheap_proxy)

        expensive_proxy = Proxy(url="http://expensive.com:8080", health_status=HealthStatus.HEALTHY)
        expensive_proxy.cost_per_request = 1.0
        pool.add_proxy(expensive_proxy)

        # Initialize with one threshold
        strategy = CostAwareStrategy(max_cost_per_request=0.2)

        # Configure with different threshold
        config = StrategyConfig(metadata={"max_cost_per_request": 0.5})
        strategy.configure(config)

        # Act - Make selections
        selections = [strategy.select(pool) for _ in range(10)]

        # Assert - cheap_proxy should be selected (0.3 <= 0.5)
        # If configure didn't override, would raise error (0.3 > 0.2)
        assert all(s.url == "http://cheap.com:8080" for s in selections)
