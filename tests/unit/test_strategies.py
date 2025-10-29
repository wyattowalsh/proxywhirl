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
from proxywhirl.strategies import RoundRobinStrategy, RandomStrategy, LeastUsedStrategy, WeightedStrategy


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

    def test_same_proxy_can_be_selected_consecutively(self):
        """Test that random selection can select the same proxy multiple times in a row."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        for i in range(3):
            pool.add_proxy(Proxy(url=f"http://proxy{i}.com:8080", health_status=HealthStatus.HEALTHY))

        strategy = RandomStrategy()
        context = SelectionContext()

        # Act - Select 100 times (with random seed for reproducibility this could pick same one)
        selections = [strategy.select(pool, context) for _ in range(100)]

        # Assert - At least some selections should be the same proxy consecutively
        # (This is probabilistic but highly likely with 100 selections from 3 proxies)
        has_consecutive = False
        for i in range(len(selections) - 1):
            if selections[i].url == selections[i + 1].url:
                has_consecutive = True
                break

        assert has_consecutive, "Random selection should allow consecutive selections of same proxy"

    def test_metadata_updates_on_selection(self):
        """Test that proxy metadata is updated when selected."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy)

        strategy = RandomStrategy()
        context = SelectionContext()

        initial_started = proxy.requests_started

        # Act
        selected = strategy.select(pool, context)

        # Assert - start_request() should have been called
        assert selected.requests_started == initial_started + 1
        assert selected.requests_active == 1

    def test_configure_accepts_strategy_config(self):
        """Test that RandomStrategy accepts configuration."""
        # Arrange
        strategy = RandomStrategy()
        config = StrategyConfig()

        # Act
        strategy.configure(config)

        # Assert
        assert strategy.config == config

    def test_validate_metadata_always_returns_true(self):
        """Test that random selection doesn't require metadata validation."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        pool.add_proxy(Proxy(url="http://proxy1.com:8080"))

        strategy = RandomStrategy()

        # Act
        is_valid = strategy.validate_metadata(pool)

        # Assert
        assert is_valid is True

    def test_record_result_updates_proxy_metadata(self):
        """Test that record_result properly updates proxy metadata."""
        # Arrange
        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy.start_request()  # Simulate request start

        strategy = RandomStrategy()

        initial_completed = proxy.requests_completed
        initial_successes = proxy.total_successes

        # Act
        strategy.record_result(proxy, success=True, response_time_ms=100.0)

        # Assert
        assert proxy.requests_completed == initial_completed + 1
        assert proxy.total_successes == initial_successes + 1
        assert proxy.requests_active == 0  # Should be decremented


class TestWeightedStrategy:
    """Unit tests for WeightedStrategy (weighted random selection)."""

    def test_select_returns_healthy_proxy(self):
        """Test that weighted selection returns a healthy proxy."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy.total_requests = 10
        proxy.total_successes = 8  # 80% success rate
        pool.add_proxy(proxy)

        strategy = WeightedStrategy()

        # Act
        selected = strategy.select(pool)

        # Assert
        assert selected.url == "http://proxy1.com:8080"
        assert selected.health_status == HealthStatus.HEALTHY

    def test_high_performing_proxies_selected_more_frequently(self):
        """Test that proxies with higher success rates are selected more often."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        # High performer (90% success rate)
        high_performer = Proxy(url="http://high.com:8080", health_status=HealthStatus.HEALTHY)
        high_performer.total_requests = 100
        high_performer.total_successes = 90  # 90% success rate
        pool.add_proxy(high_performer)

        # Low performer (20% success rate)
        low_performer = Proxy(url="http://low.com:8080", health_status=HealthStatus.HEALTHY)
        low_performer.total_requests = 100
        low_performer.total_successes = 20  # 20% success rate
        pool.add_proxy(low_performer)

        strategy = WeightedStrategy()

        # Act - Select 1000 times to see distribution
        selections = [strategy.select(pool) for _ in range(1000)]
        high_count = sum(1 for s in selections if s.url == "http://high.com:8080")
        low_count = sum(1 for s in selections if s.url == "http://low.com:8080")

        # Assert - High performer should be selected significantly more often
        # With 90% vs 20% success rates, we expect roughly 4.5:1 ratio
        # Allow for variance: at least 2:1 ratio (conservative check)
        assert high_count > low_count * 2, (
            f"High performer selected {high_count} times, "
            f"low performer selected {low_count} times. "
            f"Expected at least 2:1 ratio."
        )

    def test_handles_zero_success_rate_proxies(self):
        """Test that proxies with zero success rate still get minimum weight."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        # Proxy with 0% success rate
        zero_proxy = Proxy(url="http://zero.com:8080", health_status=HealthStatus.HEALTHY)
        zero_proxy.total_requests = 10
        zero_proxy.total_successes = 0  # 0% success rate
        pool.add_proxy(zero_proxy)

        # Proxy with 50% success rate
        normal_proxy = Proxy(url="http://normal.com:8080", health_status=HealthStatus.HEALTHY)
        normal_proxy.total_requests = 10
        normal_proxy.total_successes = 5  # 50% success rate
        pool.add_proxy(normal_proxy)

        strategy = WeightedStrategy()

        # Act - Should not raise error, zero weight proxy gets minimum weight (0.1)
        selections = [strategy.select(pool) for _ in range(100)]

        # Assert - Both proxies should be selected (zero proxy gets base weight)
        zero_count = sum(1 for s in selections if s.url == "http://zero.com:8080")
        normal_count = sum(1 for s in selections if s.url == "http://normal.com:8080")

        assert zero_count > 0, "Zero success rate proxy should still be selected with base weight"
        assert normal_count > zero_count, "Normal proxy should be selected more often"

    def test_handles_new_proxies_without_history(self):
        """Test that new proxies without request history are handled correctly."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        # New proxy (no requests yet)
        new_proxy = Proxy(url="http://new.com:8080", health_status=HealthStatus.HEALTHY)
        # total_requests and total_successes default to 0
        pool.add_proxy(new_proxy)

        strategy = WeightedStrategy()

        # Act - Should not raise error
        selected = strategy.select(pool)

        # Assert - New proxy should be selectable (gets base weight 0.1)
        assert selected.url == "http://new.com:8080"

    def test_skips_unhealthy_proxies(self):
        """Test that weighted selection skips unhealthy proxies."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        # Unhealthy proxy with high success rate
        unhealthy = Proxy(url="http://unhealthy.com:8080", health_status=HealthStatus.DEAD)
        unhealthy.total_requests = 100
        unhealthy.total_successes = 95
        pool.add_proxy(unhealthy)

        # Healthy proxy with lower success rate
        healthy = Proxy(url="http://healthy.com:8080", health_status=HealthStatus.HEALTHY)
        healthy.total_requests = 100
        healthy.total_successes = 50
        pool.add_proxy(healthy)

        strategy = WeightedStrategy()

        # Act - Select multiple times
        selections = [strategy.select(pool) for _ in range(10)]

        # Assert - All selections should be the healthy proxy
        assert all(s.url == "http://healthy.com:8080" for s in selections)

    def test_raises_when_no_healthy_proxies(self):
        """Test that weighted selection raises error when no healthy proxies available."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        pool.add_proxy(Proxy(url="http://dead.com:8080", health_status=HealthStatus.DEAD))

        strategy = WeightedStrategy()

        # Act & Assert
        with pytest.raises(ProxyPoolEmptyError, match="No healthy proxies available"):
            strategy.select(pool)

    def test_record_result_success_updates_metrics(self):
        """Test that recording success updates proxy metrics correctly."""
        # Arrange
        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        initial_requests = proxy.total_requests
        initial_successes = proxy.total_successes

        strategy = WeightedStrategy()

        # Act
        strategy.record_result(proxy, success=True, response_time_ms=150.0)

        # Assert
        assert proxy.total_requests == initial_requests + 1
        assert proxy.total_successes == initial_successes + 1

    def test_record_result_failure_updates_metrics(self):
        """Test that recording failure updates proxy metrics correctly."""
        # Arrange
        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        initial_requests = proxy.total_requests
        initial_failures = proxy.total_failures

        strategy = WeightedStrategy()

        # Act
        strategy.record_result(proxy, success=False, response_time_ms=5000.0)

        # Assert
        assert proxy.total_requests == initial_requests + 1
        assert proxy.total_failures == initial_failures + 1

    def test_select_with_custom_weights_from_config(self):
        """Test that custom weights from StrategyConfig are respected."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy1.total_requests = 100
        proxy1.total_successes = 50  # 50% success rate
        pool.add_proxy(proxy1)

        proxy2 = Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2.total_requests = 100
        proxy2.total_successes = 50  # 50% success rate
        pool.add_proxy(proxy2)

        # Configure custom weights heavily favoring proxy1
        config = StrategyConfig(
            weights={
                "http://proxy1.com:8080": 10.0,  # High weight
                "http://proxy2.com:8080": 1.0,   # Low weight
            }
        )

        strategy = WeightedStrategy()
        strategy.configure(config)

        # Act - Select 100 times
        selections = [strategy.select(pool) for _ in range(100)]
        proxy1_count = sum(1 for s in selections if s.url == "http://proxy1.com:8080")

        # Assert - proxy1 should be selected much more frequently
        # With 10:1 weight ratio, expect at least 70% selections for proxy1
        assert proxy1_count >= 70, f"Expected at least 70 proxy1 selections, got {proxy1_count}"

    def test_select_with_context_filters_failed_proxies(self):
        """Test that SelectionContext filters out failed proxies."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy1)

        proxy2 = Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy2)

        strategy = WeightedStrategy()

        # Context marking proxy1 as failed
        context = SelectionContext(failed_proxy_ids=[str(proxy1.id)])

        # Act - Select multiple times
        selections = [strategy.select(pool, context) for _ in range(10)]

        # Assert - All selections should be proxy2 (proxy1 is filtered)
        assert all(s.url == "http://proxy2.com:8080" for s in selections)

    def test_select_updates_metadata_on_selection(self):
        """Test that proxy metadata is updated when selected."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy)

        strategy = WeightedStrategy()

        initial_started = proxy.requests_started

        # Act
        selected = strategy.select(pool)

        # Assert - start_request() should have been called
        assert selected.requests_started == initial_started + 1
        assert selected.requests_active == 1

    def test_fallback_to_uniform_weights_when_all_zero(self):
        """Test fallback to uniform weights when all weights are invalid."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy1)

        proxy2 = Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy2)

        # Configure with zero/negative weights (invalid)
        config = StrategyConfig(
            weights={
                "http://proxy1.com:8080": 0.0,
                "http://proxy2.com:8080": -1.0,
            }
        )

        strategy = WeightedStrategy()
        strategy.configure(config)

        # Act - Should fall back to success_rate (both are 0.0), then use base weight 0.1
        # This should work without error
        selected = strategy.select(pool)

        # Assert - Should successfully select a proxy
        assert selected is not None


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
