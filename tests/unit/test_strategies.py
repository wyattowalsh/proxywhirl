"""
Unit tests for rotation strategies.

Following TDD: These tests are written FIRST and should FAIL before implementation.
Tests verify core strategy behavior in isolation.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import (
    Proxy,
    ProxyPool,
    HealthStatus,
    SelectionContext,
    StrategyConfig,
)
from proxywhirl.strategies import RoundRobinStrategy, RandomStrategy, LeastUsedStrategy


class TestRoundRobinStrategy:
    """Unit tests for RoundRobinStrategy with SelectionContext support."""

    def test_select_cycles_through_proxies_in_order(self):
        """Test that round-robin selects proxies in sequential order."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxies = [
            Proxy(url=f"http://proxy{i}.com:8080", health_status=HealthStatus.HEALTHY)
            for i in range(3)
        ]
        for proxy in proxies:
            pool.add_proxy(proxy)

        strategy = RoundRobinStrategy()
        context = SelectionContext()

        # Act - Select 6 times to see full 2 cycles
        selections = [strategy.select(pool, context) for _ in range(6)]

        # Assert - Should cycle: 0,1,2,0,1,2
        assert selections[0].url == "http://proxy0.com:8080"
        assert selections[1].url == "http://proxy1.com:8080"
        assert selections[2].url == "http://proxy2.com:8080"
        assert selections[3].url == "http://proxy0.com:8080"
        assert selections[4].url == "http://proxy1.com:8080"
        assert selections[5].url == "http://proxy2.com:8080"

    def test_select_skips_unhealthy_proxies(self):
        """Test that round-robin skips unhealthy proxies."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxy0 = Proxy(url="http://proxy0.com:8080", health_status=HealthStatus.HEALTHY)
        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.DEAD)
        proxy2 = Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.HEALTHY)

        pool.add_proxy(proxy0)
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        strategy = RoundRobinStrategy()
        context = SelectionContext()

        # Act - Select 4 times
        selections = [strategy.select(pool, context) for _ in range(4)]

        # Assert - Should skip proxy1 (DEAD): 0,2,0,2
        assert selections[0].url == "http://proxy0.com:8080"
        assert selections[1].url == "http://proxy2.com:8080"
        assert selections[2].url == "http://proxy0.com:8080"
        assert selections[3].url == "http://proxy2.com:8080"

    def test_select_raises_when_pool_empty(self):
        """Test that selecting from empty pool raises ProxyPoolEmptyError."""
        # Arrange
        pool = ProxyPool(name="empty-pool")
        strategy = RoundRobinStrategy()
        context = SelectionContext()

        # Act & Assert
        with pytest.raises(ProxyPoolEmptyError, match="No healthy proxies available"):
            strategy.select(pool, context)

    def test_select_raises_when_all_proxies_unhealthy(self):
        """Test that selecting with all unhealthy proxies raises error."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        pool.add_proxy(Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.DEAD))
        pool.add_proxy(Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.UNHEALTHY))

        strategy = RoundRobinStrategy()
        context = SelectionContext()

        # Act & Assert
        with pytest.raises(ProxyPoolEmptyError, match="No healthy proxies available"):
            strategy.select(pool, context)

    def test_configure_accepts_strategy_config(self):
        """Test that strategy accepts and stores configuration."""
        # Arrange
        strategy = RoundRobinStrategy()
        config = StrategyConfig(
            fallback_strategy="random",
            window_duration_seconds=7200,
        )

        # Act
        strategy.configure(config)

        # Assert - Should not raise, configuration stored
        assert strategy.config == config

    def test_validate_metadata_always_returns_true(self):
        """Test that round-robin doesn't require metadata validation."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        pool.add_proxy(Proxy(url="http://proxy1.com:8080"))

        strategy = RoundRobinStrategy()

        # Act
        is_valid = strategy.validate_metadata(pool)

        # Assert - Round-robin doesn't need metadata
        assert is_valid is True

    def test_record_result_updates_proxy_metadata(self):
        """Test that recording results updates proxy counters and metrics."""
        # Arrange
        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        strategy = RoundRobinStrategy()

        # Act - Record successful request
        strategy.record_result(proxy, success=True, response_time_ms=150.0)

        # Assert - Proxy should have updated stats
        assert proxy.total_requests == 1
        assert proxy.total_successes == 1
        assert proxy.total_failures == 0
        assert proxy.average_response_time_ms == 150.0

    def test_select_with_failed_proxy_ids_in_context(self):
        """Test that selection respects failed_proxy_ids in context."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxy0 = Proxy(url="http://proxy0.com:8080", health_status=HealthStatus.HEALTHY)
        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2 = Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.HEALTHY)

        pool.add_proxy(proxy0)
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        strategy = RoundRobinStrategy()
        
        # Mark proxy0 as failed for this request
        context = SelectionContext(failed_proxy_ids=[str(proxy0.id)])

        # Act
        selected = strategy.select(pool, context)

        # Assert - Should not select proxy0
        assert selected.id != proxy0.id
        assert selected.id in [proxy1.id, proxy2.id]

    def test_wraparound_from_last_to_first_proxy(self):
        """Test that index wraps around correctly from last to first proxy."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxies = [
            Proxy(url=f"http://proxy{i}.com:8080", health_status=HealthStatus.HEALTHY)
            for i in range(3)
        ]
        for proxy in proxies:
            pool.add_proxy(proxy)

        strategy = RoundRobinStrategy()
        context = SelectionContext()

        # Act - Select to get to last proxy, then wrap
        _ = strategy.select(pool, context)  # proxy0
        _ = strategy.select(pool, context)  # proxy1
        last = strategy.select(pool, context)  # proxy2
        first_again = strategy.select(pool, context)  # should wrap to proxy0

        # Assert
        assert last.url == "http://proxy2.com:8080"
        assert first_again.url == "http://proxy0.com:8080"

    def test_metadata_updated_on_selection(self):
        """Test that proxy metadata is updated when selected."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy)

        strategy = RoundRobinStrategy()
        context = SelectionContext()

        # Record initial state
        initial_started = proxy.requests_started
        initial_active = proxy.requests_active

        # Act
        selected = strategy.select(pool, context)

        # Assert - Metadata should be updated via start_request()
        assert selected.requests_started == initial_started + 1
        assert selected.requests_active == initial_active + 1


class TestRandomStrategy:
    """Unit tests for RandomStrategy with SelectionContext support."""

    def test_select_returns_healthy_proxy(self):
        """Test that random selection returns a healthy proxy."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy)

        strategy = RandomStrategy()
        context = SelectionContext()

        # Act
        selected = strategy.select(pool, context)

        # Assert
        assert selected.url == "http://proxy1.com:8080"
        assert selected.health_status == HealthStatus.HEALTHY

    def test_select_skips_unhealthy_proxies(self):
        """Test that random selection skips unhealthy proxies."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        pool.add_proxy(Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.DEAD))
        pool.add_proxy(Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.UNHEALTHY))
        healthy_proxy = Proxy(url="http://proxy3.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(healthy_proxy)

        strategy = RandomStrategy()
        context = SelectionContext()

        # Act - Select multiple times to ensure consistency
        selections = [strategy.select(pool, context) for _ in range(5)]

        # Assert - All selections should be the healthy proxy
        assert all(s.url == "http://proxy3.com:8080" for s in selections)

    def test_select_raises_when_pool_empty(self):
        """Test that selecting from empty pool raises error."""
        # Arrange
        pool = ProxyPool(name="empty-pool")
        strategy = RandomStrategy()
        context = SelectionContext()

        # Act & Assert
        with pytest.raises(ProxyPoolEmptyError, match="No healthy proxies available"):
            strategy.select(pool, context)


class TestLeastUsedStrategy:
    """Unit tests for LeastUsedStrategy with SelectionContext support."""

    def test_select_returns_proxy_with_minimum_requests(self):
        """Test that least-used selects proxy with fewest requests."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxy0 = Proxy(url="http://proxy0.com:8080", health_status=HealthStatus.HEALTHY)
        proxy0.requests_started = 10
        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy1.requests_started = 5  # Least used
        proxy2 = Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2.requests_started = 15

        pool.add_proxy(proxy0)
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        strategy = LeastUsedStrategy()
        context = SelectionContext()

        # Act
        selected = strategy.select(pool, context)

        # Assert
        assert selected.url == "http://proxy1.com:8080"
        # Note: requests_started is now 6 because select() calls start_request()
        assert selected.requests_started == 6
        assert selected.requests_active == 1

    def test_select_skips_unhealthy_proxies(self):
        """Test that least-used skips unhealthy proxies."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxy0 = Proxy(url="http://proxy0.com:8080", health_status=HealthStatus.DEAD)
        proxy0.requests_started = 2  # Would be least used, but unhealthy
        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy1.requests_started = 10

        pool.add_proxy(proxy0)
        pool.add_proxy(proxy1)

        strategy = LeastUsedStrategy()
        context = SelectionContext()

        # Act
        selected = strategy.select(pool, context)

        # Assert - Should skip unhealthy proxy0
        assert selected.url == "http://proxy1.com:8080"

    def test_select_raises_when_pool_empty(self):
        """Test that selecting from empty pool raises error."""
        # Arrange
        pool = ProxyPool(name="empty-pool")
        strategy = LeastUsedStrategy()
        context = SelectionContext()

        # Act & Assert
        with pytest.raises(ProxyPoolEmptyError, match="No healthy proxies available"):
            strategy.select(pool, context)

    def test_validate_metadata_checks_request_counters(self):
        """Test that least-used validates request counter metadata."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy1.com:8080")
        proxy.requests_started = 10  # Has metadata
        pool.add_proxy(proxy)

        strategy = LeastUsedStrategy()

        # Act
        is_valid = strategy.validate_metadata(pool)

        # Assert
        assert is_valid is True
