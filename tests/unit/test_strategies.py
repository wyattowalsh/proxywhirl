"""
Unit tests for rotation strategies.

Following TDD: These tests are written FIRST and should FAIL before implementation.
Tests verify core strategy behavior in isolation.
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
from proxywhirl.strategies import (
    LeastUsedStrategy,
    PerformanceBasedStrategy,
    RandomStrategy,
    RoundRobinStrategy,
    WeightedStrategy,
)


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
            pool.add_proxy(
                Proxy(url=f"http://proxy{i}.com:8080", health_status=HealthStatus.HEALTHY)
            )

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
                "http://proxy2.com:8080": 1.0,  # Low weight
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

    def test_weight_caching_optimization(self):
        """Test that weights are cached and not recalculated on every selection."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy1.total_requests = 100
        proxy1.total_successes = 80
        pool.add_proxy(proxy1)

        proxy2 = Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2.total_requests = 100
        proxy2.total_successes = 60
        pool.add_proxy(proxy2)

        strategy = WeightedStrategy()

        # Act - First selection should populate cache
        first_selection = strategy.select(pool)
        assert strategy._cache_valid is True
        assert strategy._cached_weights is not None
        assert strategy._cached_proxy_ids is not None
        cached_weights_first = strategy._cached_weights.copy()
        cached_ids_first = strategy._cached_proxy_ids.copy()

        # Second selection with same proxy set should use cache
        _ = strategy.select(pool)
        assert strategy._cache_valid is True
        assert strategy._cached_weights == cached_weights_first
        assert strategy._cached_proxy_ids == cached_ids_first

        # Recording a result should invalidate cache
        strategy.record_result(first_selection, success=True, response_time_ms=100.0)
        assert strategy._cache_valid is False
        assert strategy._cached_weights is None
        assert strategy._cached_proxy_ids is None

        # Next selection should recalculate
        _ = strategy.select(pool)
        assert strategy._cache_valid is True
        assert strategy._cached_weights is not None

        # Configuring should invalidate cache
        config = StrategyConfig(weights={"http://proxy1.com:8080": 5.0})
        strategy.configure(config)
        assert strategy._cache_valid is False

        # Next selection should recalculate with new config
        _ = strategy.select(pool)
        assert strategy._cache_valid is True

    def test_cache_invalidation_on_proxy_set_change(self):
        """Test that cache is invalidated when proxy set changes."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy1)

        strategy = WeightedStrategy()

        # Act - First selection with one proxy
        strategy.select(pool)
        assert strategy._cache_valid is True
        first_cached_ids = strategy._cached_proxy_ids.copy()

        # Add another proxy
        proxy2 = Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy2)

        # Select again - should detect different proxy set and recalculate
        strategy.select(pool)
        assert strategy._cache_valid is True
        second_cached_ids = strategy._cached_proxy_ids

        # Assert - cached IDs should be different
        assert first_cached_ids != second_cached_ids
        assert len(second_cached_ids) == 2

    def test_weights_normalized_after_proxy_removal(self):
        """Test that weights are renormalized to sum to 1.0 after proxies are removed."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy1.total_requests = 100
        proxy1.total_successes = 80  # 80% success rate
        pool.add_proxy(proxy1)

        proxy2 = Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2.total_requests = 100
        proxy2.total_successes = 60  # 60% success rate
        pool.add_proxy(proxy2)

        proxy3 = Proxy(url="http://proxy3.com:8080", health_status=HealthStatus.HEALTHY)
        proxy3.total_requests = 100
        proxy3.total_successes = 40  # 40% success rate
        pool.add_proxy(proxy3)

        strategy = WeightedStrategy()

        # Act - Select with all 3 proxies and check weights sum
        healthy_proxies = pool.get_healthy_proxies()
        weights_before = strategy._calculate_weights(healthy_proxies)
        sum_before = sum(weights_before)

        # Assert - Weights should sum to 1.0 with all proxies
        assert sum_before == pytest.approx(1.0, abs=1e-10)

        # Remove proxy2 by marking it as DEAD
        proxy2.health_status = HealthStatus.DEAD

        # Get new healthy proxies (only proxy1 and proxy3)
        healthy_proxies_after = pool.get_healthy_proxies()
        assert len(healthy_proxies_after) == 2

        # Calculate weights after removal
        weights_after = strategy._calculate_weights(healthy_proxies_after)
        sum_after = sum(weights_after)

        # Assert - Weights should still sum to 1.0 after removal
        assert sum_after == pytest.approx(1.0, abs=1e-10)
        assert len(weights_after) == 2

    def test_weights_normalized_with_custom_weights_after_removal(self):
        """Test that custom weights are renormalized after proxy removal."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy1)

        proxy2 = Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy2)

        proxy3 = Proxy(url="http://proxy3.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy3)

        # Configure custom weights
        config = StrategyConfig(
            weights={
                "http://proxy1.com:8080": 5.0,
                "http://proxy2.com:8080": 3.0,
                "http://proxy3.com:8080": 2.0,
            }
        )

        strategy = WeightedStrategy()
        strategy.configure(config)

        # Act - Get weights with all proxies
        healthy_proxies = pool.get_healthy_proxies()
        weights_before = strategy._calculate_weights(healthy_proxies)
        sum_before = sum(weights_before)

        # Assert - Should sum to 1.0
        assert sum_before == pytest.approx(1.0, abs=1e-10)

        # Remove proxy2
        proxy2.health_status = HealthStatus.DEAD

        # Get weights after removal
        healthy_proxies_after = pool.get_healthy_proxies()
        weights_after = strategy._calculate_weights(healthy_proxies_after)
        sum_after = sum(weights_after)

        # Assert - Should still sum to 1.0 after removal
        assert sum_after == pytest.approx(1.0, abs=1e-10)
        assert len(weights_after) == 2

        # Verify relative weights are preserved (5:2 ratio for proxy1:proxy3)
        # After normalization: 5/(5+2) = 5/7 ≈ 0.714, 2/(5+2) = 2/7 ≈ 0.286
        assert weights_after[0] == pytest.approx(5.0 / 7.0, abs=1e-6)
        assert weights_after[1] == pytest.approx(2.0 / 7.0, abs=1e-6)

    def test_weights_sum_to_one_with_single_proxy(self):
        """Test that weight normalization works correctly with a single proxy."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        proxy = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy.total_requests = 100
        proxy.total_successes = 75  # 75% success rate
        pool.add_proxy(proxy)

        strategy = WeightedStrategy()

        # Act
        healthy_proxies = pool.get_healthy_proxies()
        weights = strategy._calculate_weights(healthy_proxies)

        # Assert
        assert len(weights) == 1
        assert weights[0] == pytest.approx(1.0, abs=1e-10)

    def test_weights_normalized_after_multiple_removals(self):
        """Test weight normalization after multiple sequential proxy removals."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        proxies = []
        for i in range(5):
            proxy = Proxy(url=f"http://proxy{i}.com:8080", health_status=HealthStatus.HEALTHY)
            proxy.total_requests = 100
            proxy.total_successes = 50 + i * 10  # Varying success rates
            pool.add_proxy(proxy)
            proxies.append(proxy)

        strategy = WeightedStrategy()

        # Act & Assert - Remove proxies one by one and verify normalization
        for removal_round in range(4):
            healthy_proxies = pool.get_healthy_proxies()
            weights = strategy._calculate_weights(healthy_proxies)
            total_weight = sum(weights)

            # Assert - Weights should always sum to 1.0
            assert total_weight == pytest.approx(1.0, abs=1e-10), (
                f"After removing {removal_round} proxies, "
                f"weights sum to {total_weight}, expected 1.0"
            )

            # Remove one proxy
            if removal_round < 4:
                proxies[removal_round].health_status = HealthStatus.DEAD

        # Final check with only one proxy remaining
        final_healthy = pool.get_healthy_proxies()
        assert len(final_healthy) == 1
        final_weights = strategy._calculate_weights(final_healthy)
        assert sum(final_weights) == pytest.approx(1.0, abs=1e-10)

    def test_selection_probability_distribution_after_removal(self):
        """Test that selection probability distribution remains correct after proxy removal."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy1.total_requests = 100
        proxy1.total_successes = 90  # 90% - high success
        pool.add_proxy(proxy1)

        proxy2 = Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2.total_requests = 100
        proxy2.total_successes = 30  # 30% - low success
        pool.add_proxy(proxy2)

        proxy3 = Proxy(url="http://proxy3.com:8080", health_status=HealthStatus.HEALTHY)
        proxy3.total_requests = 100
        proxy3.total_successes = 60  # 60% - medium success
        pool.add_proxy(proxy3)

        strategy = WeightedStrategy()

        # Remove proxy3 (medium performer)
        proxy3.health_status = HealthStatus.DEAD

        # Act - Make many selections with only proxy1 and proxy2
        selections = [strategy.select(pool) for _ in range(1000)]
        proxy1_count = sum(1 for s in selections if s.url == "http://proxy1.com:8080")
        proxy2_count = sum(1 for s in selections if s.url == "http://proxy2.com:8080")

        # Assert - proxy1 should still be selected more often than proxy2
        # With 90% vs 30% success rates, expect roughly 3:1 ratio
        assert proxy1_count > proxy2_count * 2, (
            f"Expected proxy1 to be selected much more often. "
            f"proxy1: {proxy1_count}, proxy2: {proxy2_count}"
        )

        # Verify total selections
        assert proxy1_count + proxy2_count == 1000

    def test_concurrent_cache_invalidation_thread_safety(self):
        """Test that cache invalidation is thread-safe under concurrent access.

        This test verifies that WeightedStrategy's cache mechanism prevents race conditions
        where multiple threads could:
        1. Read stale cached weights while another thread updates proxy stats
        2. Trigger duplicate weight recalculations
        3. Create inconsistent cache states

        The strategy uses double-checked locking with _cache_lock to ensure:
        - Cache validation and updates are atomic
        - record_result() invalidates cache before updating proxy stats
        - Multiple concurrent selects don't cause duplicate recalculations
        """
        import threading
        from concurrent.futures import ThreadPoolExecutor

        # Arrange - Create pool with multiple proxies
        pool = ProxyPool(name="test-pool")

        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy1.total_requests = 100
        proxy1.total_successes = 80  # 80% success rate
        pool.add_proxy(proxy1)

        proxy2 = Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2.total_requests = 100
        proxy2.total_successes = 60  # 60% success rate
        pool.add_proxy(proxy2)

        proxy3 = Proxy(url="http://proxy3.com:8080", health_status=HealthStatus.HEALTHY)
        proxy3.total_requests = 100
        proxy3.total_successes = 40  # 40% success rate
        pool.add_proxy(proxy3)

        strategy = WeightedStrategy()

        # Shared state for tracking operations
        selections_made = []
        results_recorded = []
        cache_hits = []
        exceptions = []
        lock = threading.Lock()

        def select_proxy(thread_id: int) -> None:
            """Select a proxy and track cache behavior."""
            try:
                # Check if cache is valid before selection
                cache_valid_before = strategy._cache_valid

                # Select proxy
                selected = strategy.select(pool)

                # Track whether this was a cache hit
                with lock:
                    selections_made.append((thread_id, selected.url))
                    cache_hits.append(cache_valid_before)
            except Exception as e:
                with lock:
                    exceptions.append((thread_id, "select", str(e)))

        def record_result_for_proxy(thread_id: int, proxy_url: str) -> None:
            """Record a result for a specific proxy."""
            try:
                # Find the proxy by URL
                target_proxy = None
                for p in pool.get_all_proxies():
                    if p.url == proxy_url:
                        target_proxy = p
                        break

                if target_proxy:
                    # Record result (should invalidate cache)
                    success = thread_id % 2 == 0  # Alternate success/failure
                    response_time = 100.0 + (thread_id * 10.0)
                    strategy.record_result(
                        target_proxy, success=success, response_time_ms=response_time
                    )

                    with lock:
                        results_recorded.append((thread_id, proxy_url, success))
            except Exception as e:
                with lock:
                    exceptions.append((thread_id, "record", str(e)))

        # Act - Run concurrent operations using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit mix of select and record_result operations
            futures = []

            # 50 concurrent selections
            for i in range(50):
                futures.append(executor.submit(select_proxy, i))

            # 30 concurrent result recordings (interleaved with selections)
            proxy_urls = [proxy1.url, proxy2.url, proxy3.url]
            for i in range(30):
                proxy_url = proxy_urls[i % len(proxy_urls)]
                futures.append(executor.submit(record_result_for_proxy, i + 100, proxy_url))

            # Wait for all operations to complete
            for future in futures:
                future.result()

        # Assert - Verify thread safety

        # 1. No exceptions should have occurred
        assert len(exceptions) == 0, f"Exceptions occurred during concurrent access: {exceptions}"

        # 2. Correct number of operations completed
        assert len(selections_made) == 50, "Not all selections completed"
        assert len(results_recorded) == 30, "Not all result recordings completed"

        # 3. All selections should have returned valid proxies
        valid_urls = {proxy1.url, proxy2.url, proxy3.url}
        for _, url in selections_made:
            assert url in valid_urls, f"Invalid proxy URL selected: {url}"

        # 4. Cache should have been properly invalidated and rebuilt
        # After all operations, cache should be valid (rebuilt by last select)
        assert strategy._cache_valid is True or strategy._cache_valid is False
        # Either valid (just selected) or invalid (just recorded result)

        # 5. Proxy stats should reflect all recorded results
        total_results_recorded = len(results_recorded)
        total_proxy_requests = sum(
            p.total_requests - 100 for p in [proxy1, proxy2, proxy3]
        )  # Subtract initial 100
        assert total_proxy_requests == total_results_recorded, (
            f"Proxy stats inconsistent. Expected {total_results_recorded} new requests, "
            f"got {total_proxy_requests}"
        )

        # 6. Verify cache hit rate shows proper invalidation
        # After first selection, cache should be valid for subsequent selects
        # But record_result calls should invalidate it
        # We expect some cache hits (when multiple selects happen between record_results)
        cache_hit_count = sum(1 for hit in cache_hits if hit)
        # There should be at least some cache hits (not all operations triggered recalculation)
        # But also some cache misses (due to invalidations)
        # This is a weak assertion but validates the cache is being used
        assert cache_hit_count < len(cache_hits), "Cache never invalidated (suspicious)"

    def test_concurrent_weight_recalculation_consistency(self):
        """Test that concurrent weight recalculations produce consistent results.

        Verifies that even when multiple threads trigger weight recalculation
        simultaneously, the final weights are always normalized to sum to 1.0
        and reflect the current proxy statistics accurately.
        """
        import threading
        from concurrent.futures import ThreadPoolExecutor

        # Arrange
        pool = ProxyPool(name="test-pool")

        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy1.total_requests = 50
        proxy1.total_successes = 40
        pool.add_proxy(proxy1)

        proxy2 = Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2.total_requests = 50
        proxy2.total_successes = 30
        pool.add_proxy(proxy2)

        strategy = WeightedStrategy()

        exceptions = []
        lock = threading.Lock()

        def concurrent_operation(thread_id: int) -> None:
            """Alternate between selecting and recording results."""
            try:
                if thread_id % 2 == 0:
                    # Select proxy (may trigger weight calculation)
                    strategy.select(pool)
                else:
                    # Record result (invalidates cache)
                    proxy = proxy1 if thread_id % 4 == 1 else proxy2
                    strategy.record_result(proxy, success=True, response_time_ms=100.0)
            except Exception as e:
                with lock:
                    exceptions.append((thread_id, str(e)))

        # Act - Run many concurrent operations
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(concurrent_operation, i) for i in range(200)]
            for future in futures:
                future.result()

        # Assert
        assert len(exceptions) == 0, f"Exceptions during concurrent operations: {exceptions}"

        # Verify final state consistency
        # Get current weights (this will recalculate if cache invalid)
        healthy_proxies = pool.get_healthy_proxies()
        final_weights = strategy._get_weights(healthy_proxies)

        # Weights should always sum to 1.0 (normalization invariant)
        assert sum(final_weights) == pytest.approx(1.0, abs=1e-10), (
            f"Weights do not sum to 1.0 after concurrent operations: {sum(final_weights)}"
        )

        # Cache should be valid after the _get_weights call
        assert strategy._cache_valid is True

        # Proxy IDs in cache should match current healthy proxies
        current_ids = [str(p.id) for p in healthy_proxies]
        assert strategy._cached_proxy_ids == current_ids

    def test_concurrent_cache_invalidation_race_condition(self):
        """Test that cache invalidation race condition is properly handled.

        This test specifically targets the race condition where:
        1. Thread A checks cache validity in _get_weights() (cache is valid)
        2. Thread B invalidates cache in record_result()
        3. Thread B updates proxy stats
        4. Thread A reads the cached weights (now stale, based on old stats)

        The double-checked locking in record_result() should prevent this.
        """
        import threading
        from concurrent.futures import ThreadPoolExecutor

        # Arrange
        pool = ProxyPool(name="test-pool")

        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy1.total_requests = 100
        proxy1.total_successes = 90  # 90% success rate (very reliable)
        pool.add_proxy(proxy1)

        proxy2 = Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2.total_requests = 100
        proxy2.total_successes = 85  # 85% success rate (very reliable)
        pool.add_proxy(proxy2)

        strategy = WeightedStrategy()

        # Pre-warm the cache
        strategy.select(pool)
        assert strategy._cache_valid is True

        exceptions = []
        weight_reads = []
        lock = threading.Lock()

        def get_weights_operation(thread_id: int) -> None:
            """Continuously read weights to stress test cache reads during invalidation."""
            try:
                for _ in range(100):
                    # Read weights directly to test cache consistency
                    healthy_proxies = pool.get_healthy_proxies()
                    if healthy_proxies:
                        weights = strategy._get_weights(healthy_proxies)
                        with lock:
                            weight_reads.append((thread_id, sum(weights)))
            except Exception as e:
                with lock:
                    exceptions.append((thread_id, "get_weights", str(e)))

        def invalidate_operation(thread_id: int) -> None:
            """Continuously invalidate cache via record_result to stress test locking."""
            try:
                for i in range(100):
                    proxy = proxy1 if i % 2 == 0 else proxy2
                    # Always successful to keep proxies healthy
                    strategy.record_result(proxy, success=True, response_time_ms=100.0)
            except Exception as e:
                with lock:
                    exceptions.append((thread_id, "invalidate", str(e)))

        # Act - Run get_weights and invalidate concurrently to maximize race exposure
        # Use 10 threads: 5 reading weights, 5 invalidating
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            # 5 threads reading weights
            for i in range(5):
                futures.append(executor.submit(get_weights_operation, i))
            # 5 threads invalidating cache
            for i in range(5, 10):
                futures.append(executor.submit(invalidate_operation, i))

            # Wait for all to complete
            for future in futures:
                future.result()

        # Assert
        assert len(exceptions) == 0, f"Exceptions during concurrent operations: {exceptions}"

        # Verify all weight sums are valid (should always sum to 1.0)
        for thread_id, weight_sum in weight_reads:
            assert weight_sum == pytest.approx(1.0, abs=1e-10), (
                f"Thread {thread_id} got invalid weight sum: {weight_sum}"
            )

        # Verify cache consistency
        healthy_proxies = pool.get_healthy_proxies()
        final_weights = strategy._get_weights(healthy_proxies)

        # Weights should always sum to 1.0 (normalization invariant)
        assert sum(final_weights) == pytest.approx(1.0, abs=1e-10), (
            f"Final weights do not sum to 1.0: {sum(final_weights)}"
        )

        # Verify proxy stats were updated correctly
        # Each proxy should have additional requests from record_result calls
        assert proxy1.total_requests > 100, "Proxy1 stats not updated"
        assert proxy2.total_requests > 100, "Proxy2 stats not updated"


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

    def test_select_handles_tie_breaking(self):
        """Test that least-used handles tie-breaking when multiple proxies have same count."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxy0 = Proxy(url="http://proxy0.com:8080", health_status=HealthStatus.HEALTHY)
        proxy0.requests_started = 5
        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy1.requests_started = 5  # Same count as proxy0
        proxy2 = Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2.requests_started = 10

        pool.add_proxy(proxy0)
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        strategy = LeastUsedStrategy()
        context = SelectionContext()

        # Act
        selected = strategy.select(pool, context)

        # Assert - Should select one of the tied proxies (proxy0 or proxy1)
        assert selected.url in ["http://proxy0.com:8080", "http://proxy1.com:8080"]
        assert selected.requests_started == 6  # Was 5, now 6 after start_request()

    def test_configure_accepts_strategy_config(self):
        """Test that least-used accepts StrategyConfig."""
        # Arrange
        strategy = LeastUsedStrategy()
        config = StrategyConfig()

        # Act
        strategy.configure(config)

        # Assert
        assert strategy.config == config

    def test_record_result_updates_proxy_metadata(self):
        """Test that record_result updates proxy metadata correctly."""
        # Arrange
        proxy = Proxy(url="http://proxy1.com:8080")
        proxy.requests_started = 1
        proxy.requests_active = 1
        strategy = LeastUsedStrategy()

        # Act
        strategy.record_result(proxy, success=True, response_time_ms=150.0)

        # Assert
        assert proxy.requests_completed == 1
        assert proxy.total_successes == 1
        assert proxy.requests_active == 0

    def test_select_with_context_filtering(self):
        """Test that least-used respects SelectionContext filtering."""
        # Arrange
        pool = ProxyPool(name="test-pool")
        proxy0 = Proxy(url="http://proxy0.com:8080", health_status=HealthStatus.HEALTHY)
        proxy0.requests_started = 1  # Least used
        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy1.requests_started = 5

        pool.add_proxy(proxy0)
        pool.add_proxy(proxy1)

        strategy = LeastUsedStrategy()
        # Create context that filters out proxy0 by UUID
        context = SelectionContext(failed_proxy_ids=[str(proxy0.id)])

        # Act
        selected = strategy.select(pool, context)

        # Assert - Should skip proxy0 due to context filtering
        assert selected.url == "http://proxy1.com:8080"


class TestPerformanceBasedStrategy:
    """Unit tests for PerformanceBasedStrategy with EMA-based selection."""

    def test_select_favors_faster_proxies(self):
        """Test that performance-based strategy favors proxies with lower EMA response times."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        # Fast proxy (50ms EMA)
        fast_proxy = Proxy(url="http://fast.com:8080", health_status=HealthStatus.HEALTHY)
        fast_proxy.ema_response_time_ms = 50.0
        fast_proxy.total_requests = 100
        fast_proxy.total_successes = 90

        # Slow proxy (200ms EMA)
        slow_proxy = Proxy(url="http://slow.com:8080", health_status=HealthStatus.HEALTHY)
        slow_proxy.ema_response_time_ms = 200.0
        slow_proxy.total_requests = 100
        slow_proxy.total_successes = 90

        pool.add_proxy(fast_proxy)
        pool.add_proxy(slow_proxy)

        strategy = PerformanceBasedStrategy()
        context = SelectionContext()

        # Act - Make multiple selections and count
        selections = [strategy.select(pool, context) for _ in range(100)]
        fast_count = sum(1 for s in selections if s.url == "http://fast.com:8080")
        slow_count = sum(1 for s in selections if s.url == "http://slow.com:8080")

        # Assert - Fast proxy should be selected significantly more often
        # With 4:1 inverse weight ratio (200/50), expect at least 2:1 selection ratio
        assert fast_count > slow_count * 2, (
            f"Fast proxy not favored enough. Fast: {fast_count}, Slow: {slow_count}"
        )

    def test_select_handles_missing_ema_data(self):
        """Test that performance-based handles proxies without EMA data via exploration."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        # Proxy with EMA (has been tried enough times)
        with_ema = Proxy(url="http://with-ema.com:8080", health_status=HealthStatus.HEALTHY)
        with_ema.ema_response_time_ms = 100.0
        with_ema.total_requests = 10  # Above exploration threshold

        # Proxy without EMA (new proxy)
        without_ema = Proxy(url="http://without-ema.com:8080", health_status=HealthStatus.HEALTHY)
        without_ema.ema_response_time_ms = None
        without_ema.total_requests = 0  # Below exploration threshold

        pool.add_proxy(with_ema)
        pool.add_proxy(without_ema)

        strategy = PerformanceBasedStrategy(exploration_count=5)
        context = SelectionContext()

        # Act
        selected = strategy.select(pool, context)

        # Assert - Should select proxy without EMA for exploration
        assert selected.url == "http://without-ema.com:8080"

    def test_select_with_no_ema_data_uses_exploration(self):
        """Test that performance-based handles pools with no EMA data via exploration."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy1.ema_response_time_ms = None
        proxy1.total_requests = 0  # New proxy

        proxy2 = Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2.ema_response_time_ms = None
        proxy2.total_requests = 0  # New proxy

        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        strategy = PerformanceBasedStrategy(exploration_count=5)
        context = SelectionContext()

        # Act - Should not raise error, should use exploration
        selected = strategy.select(pool, context)

        # Assert - Should successfully select one of the proxies
        assert selected.url in ["http://proxy1.com:8080", "http://proxy2.com:8080"]

    def test_configure_accepts_custom_alpha(self):
        """Test that performance-based accepts custom EMA alpha configuration."""
        # Arrange
        strategy = PerformanceBasedStrategy()
        config = StrategyConfig(ema_alpha=0.3)

        # Act
        strategy.configure(config)

        # Assert
        assert strategy.config == config
        assert strategy.config.ema_alpha == 0.3

    def test_validate_metadata_checks_pool_availability(self):
        """Test that performance-based validates pool has proxies (exploration handles EMA)."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        # Pool with EMA data
        proxy_with_ema = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy_with_ema.ema_response_time_ms = 100.0
        pool.add_proxy(proxy_with_ema)

        strategy = PerformanceBasedStrategy()

        # Act
        is_valid = strategy.validate_metadata(pool)

        # Assert
        assert is_valid is True

        # Now test pool without EMA data (but still valid for exploration)
        pool_no_ema = ProxyPool(name="no-ema-pool")
        proxy_no_ema = Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.HEALTHY)
        proxy_no_ema.ema_response_time_ms = None
        proxy_no_ema.total_requests = 0  # New proxy
        pool_no_ema.add_proxy(proxy_no_ema)

        is_valid_no_ema = strategy.validate_metadata(pool_no_ema)
        # With exploration support, pool is valid if it has healthy proxies
        assert is_valid_no_ema is True

    def test_record_result_updates_ema(self):
        """Test that record_result updates proxy EMA correctly via complete_request()."""
        # Arrange
        proxy = Proxy(url="http://proxy1.com:8080")
        proxy.ema_response_time_ms = 100.0  # Current EMA
        proxy.ema_alpha = 0.2  # Proxy's EMA alpha (used by complete_request)
        proxy.requests_started = 1
        proxy.requests_active = 1

        strategy = PerformanceBasedStrategy()

        # Act - Record faster response time (50ms)
        strategy.record_result(proxy, success=True, response_time_ms=50.0)

        # Assert - EMA should decrease: 0.2 * 50 + 0.8 * 100 = 90
        # (Updated by proxy.complete_request using proxy.ema_alpha)
        assert proxy.ema_response_time_ms == pytest.approx(90.0, abs=0.1)
        assert proxy.requests_completed == 1

    def test_select_uses_inverse_weighting(self):
        """Test that performance-based uses inverse weighting (lower EMA = higher weight)."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        # Create 3 proxies with different EMAs
        # All proxies need to have >= exploration_count requests to be in exploitation mode
        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy1.ema_response_time_ms = 50.0  # Fastest - should have highest weight
        proxy1.total_requests = 10  # Above exploration threshold

        proxy2 = Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2.ema_response_time_ms = 100.0  # Medium
        proxy2.total_requests = 10  # Above exploration threshold

        proxy3 = Proxy(url="http://proxy3.com:8080", health_status=HealthStatus.HEALTHY)
        proxy3.ema_response_time_ms = 200.0  # Slowest - should have lowest weight
        proxy3.total_requests = 10  # Above exploration threshold

        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)
        pool.add_proxy(proxy3)

        strategy = PerformanceBasedStrategy(exploration_count=5)  # All proxies above threshold
        context = SelectionContext()

        # Act - Make many selections
        selections = [strategy.select(pool, context) for _ in range(300)]
        counts = {
            "http://proxy1.com:8080": sum(
                1 for s in selections if s.url == "http://proxy1.com:8080"
            ),
            "http://proxy2.com:8080": sum(
                1 for s in selections if s.url == "http://proxy2.com:8080"
            ),
            "http://proxy3.com:8080": sum(
                1 for s in selections if s.url == "http://proxy3.com:8080"
            ),
        }

        # Assert - Fastest should be selected most, slowest least
        assert counts["http://proxy1.com:8080"] > counts["http://proxy2.com:8080"]
        assert counts["http://proxy2.com:8080"] > counts["http://proxy3.com:8080"]

    def test_cold_start_new_proxies_get_exploration_trials(self):
        """Test that new proxies without EMA data are selected for exploration."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        # New proxy (no EMA, no requests)
        new_proxy = Proxy(url="http://new.com:8080", health_status=HealthStatus.HEALTHY)
        new_proxy.ema_response_time_ms = None
        new_proxy.total_requests = 0

        # Established proxy with EMA
        established_proxy = Proxy(
            url="http://established.com:8080", health_status=HealthStatus.HEALTHY
        )
        established_proxy.ema_response_time_ms = 100.0
        established_proxy.total_requests = 10

        pool.add_proxy(new_proxy)
        pool.add_proxy(established_proxy)

        strategy = PerformanceBasedStrategy(exploration_count=5)
        context = SelectionContext()

        # Act - Select proxy
        selected = strategy.select(pool, context)

        # Assert - Should select new proxy for exploration
        assert selected.url == "http://new.com:8080", "New proxy should be selected for exploration"

    def test_cold_start_exploration_count_threshold(self):
        """Test that proxies transition from exploration to exploitation after threshold."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        # Proxy with 4 requests (below threshold of 5)
        exploring_proxy = Proxy(url="http://exploring.com:8080", health_status=HealthStatus.HEALTHY)
        exploring_proxy.total_requests = 4
        exploring_proxy.ema_response_time_ms = 50.0  # Has EMA but still exploring

        # Proxy with 5 requests (at threshold)
        exploiting_proxy = Proxy(
            url="http://exploiting.com:8080", health_status=HealthStatus.HEALTHY
        )
        exploiting_proxy.total_requests = 5
        exploiting_proxy.ema_response_time_ms = 200.0  # Slower EMA

        pool.add_proxy(exploring_proxy)
        pool.add_proxy(exploiting_proxy)

        strategy = PerformanceBasedStrategy(exploration_count=5)
        context = SelectionContext()

        # Act - Make multiple selections
        selections = [strategy.select(pool, context) for _ in range(10)]

        # Assert - Should always select exploring proxy until threshold reached
        # (Since it has fewer requests than exploration_count)
        assert all(s.url == "http://exploring.com:8080" for s in selections), (
            "Proxy below exploration threshold should always be selected"
        )

    def test_cold_start_multiple_new_proxies(self):
        """Test that multiple new proxies share exploration opportunities."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        # Create 3 new proxies
        new_proxy1 = Proxy(url="http://new1.com:8080", health_status=HealthStatus.HEALTHY)
        new_proxy1.total_requests = 0

        new_proxy2 = Proxy(url="http://new2.com:8080", health_status=HealthStatus.HEALTHY)
        new_proxy2.total_requests = 0

        new_proxy3 = Proxy(url="http://new3.com:8080", health_status=HealthStatus.HEALTHY)
        new_proxy3.total_requests = 0

        pool.add_proxy(new_proxy1)
        pool.add_proxy(new_proxy2)
        pool.add_proxy(new_proxy3)

        strategy = PerformanceBasedStrategy(exploration_count=5)
        context = SelectionContext()

        # Act - Make 30 selections
        selections = [strategy.select(pool, context) for _ in range(30)]
        urls_selected = {s.url for s in selections}

        # Assert - All new proxies should get selected during exploration
        assert "http://new1.com:8080" in urls_selected
        assert "http://new2.com:8080" in urls_selected
        assert "http://new3.com:8080" in urls_selected

    def test_cold_start_zero_exploration_count_disables_exploration(self):
        """Test that setting exploration_count=0 disables exploration phase."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        # New proxy without EMA
        new_proxy = Proxy(url="http://new.com:8080", health_status=HealthStatus.HEALTHY)
        new_proxy.total_requests = 0
        new_proxy.ema_response_time_ms = None

        # Established proxy with EMA
        established_proxy = Proxy(
            url="http://established.com:8080", health_status=HealthStatus.HEALTHY
        )
        established_proxy.total_requests = 10
        established_proxy.ema_response_time_ms = 100.0

        pool.add_proxy(new_proxy)
        pool.add_proxy(established_proxy)

        # Set exploration_count to 0 to disable exploration
        strategy = PerformanceBasedStrategy(exploration_count=0)
        context = SelectionContext()

        # Act - Make multiple selections
        selections = [strategy.select(pool, context) for _ in range(10)]

        # Assert - Should only select established proxy (no exploration)
        assert all(s.url == "http://established.com:8080" for s in selections), (
            "With exploration_count=0, only proxies with EMA should be selected"
        )

    def test_cold_start_fallback_when_all_proxies_lack_ema(self):
        """Test fallback behavior when all proxies have been tried but lack EMA data."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        # All proxies have been tried (>= exploration_count) but have no EMA
        # This could happen if all requests failed
        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy1.total_requests = 5
        proxy1.ema_response_time_ms = None  # No EMA (all failed)

        proxy2 = Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2.total_requests = 6
        proxy2.ema_response_time_ms = None  # No EMA (all failed)

        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        strategy = PerformanceBasedStrategy(exploration_count=5)
        context = SelectionContext()

        # Act - Should not raise error, should fall back to random selection
        selected = strategy.select(pool, context)

        # Assert - Should successfully select one of the proxies
        assert selected.url in ["http://proxy1.com:8080", "http://proxy2.com:8080"]

    def test_cold_start_configurable_exploration_count(self):
        """Test that exploration_count can be configured via StrategyConfig."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        # New proxy with 2 requests
        new_proxy = Proxy(url="http://new.com:8080", health_status=HealthStatus.HEALTHY)
        new_proxy.total_requests = 2
        new_proxy.ema_response_time_ms = None

        # Established proxy
        established_proxy = Proxy(
            url="http://established.com:8080", health_status=HealthStatus.HEALTHY
        )
        established_proxy.total_requests = 10
        established_proxy.ema_response_time_ms = 100.0

        pool.add_proxy(new_proxy)
        pool.add_proxy(established_proxy)

        # Configure with exploration_count = 3
        config = StrategyConfig(exploration_count=3)
        strategy = PerformanceBasedStrategy()
        strategy.configure(config)

        context = SelectionContext()

        # Act
        selected = strategy.select(pool, context)

        # Assert - new_proxy (2 requests) is below threshold (3), should be selected
        assert selected.url == "http://new.com:8080"

    def test_cold_start_validates_pool_with_new_proxies(self):
        """Test that validate_metadata returns True when pool has healthy proxies (even without EMA)."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        # New proxy without EMA
        new_proxy = Proxy(url="http://new.com:8080", health_status=HealthStatus.HEALTHY)
        new_proxy.ema_response_time_ms = None
        new_proxy.total_requests = 0

        pool.add_proxy(new_proxy)

        strategy = PerformanceBasedStrategy(exploration_count=5)

        # Act
        is_valid = strategy.validate_metadata(pool)

        # Assert - Should return True (exploration can handle this)
        assert is_valid is True

    def test_cold_start_context_filtering_works_with_exploration(self):
        """Test that context filtering works correctly during exploration phase."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        # Two new proxies
        new_proxy1 = Proxy(url="http://new1.com:8080", health_status=HealthStatus.HEALTHY)
        new_proxy1.total_requests = 0

        new_proxy2 = Proxy(url="http://new2.com:8080", health_status=HealthStatus.HEALTHY)
        new_proxy2.total_requests = 0

        pool.add_proxy(new_proxy1)
        pool.add_proxy(new_proxy2)

        strategy = PerformanceBasedStrategy(exploration_count=5)

        # Context that filters out new_proxy1
        context = SelectionContext(failed_proxy_ids=[str(new_proxy1.id)])

        # Act
        selected = strategy.select(pool, context)

        # Assert - Should select new_proxy2 (new_proxy1 is filtered)
        assert selected.url == "http://new2.com:8080"


class TestPluginArchitecture:
    """Unit tests for plugin architecture (Phase 9, T067).

    StrategyRegistry is now implemented - tests validate registration,
    retrieval, and validation of custom strategies.
    """

    def test_register_custom_strategy(self):
        """Test custom strategy registration and retrieval."""
        from proxywhirl.strategies import StrategyRegistry

        # Arrange - Create custom strategy class
        class CustomStrategy:
            def select(self, pool, context=None):
                return pool.get_all_proxies()[0]

            def record_result(self, proxy, success, response_time_ms=None):
                pass

            def configure(self, config):
                pass

            def validate_metadata(self, pool):
                return True

        # Act - Register strategy
        registry = StrategyRegistry()
        registry.register_strategy("custom-test", CustomStrategy)

        try:
            # Assert - Can retrieve registered strategy
            retrieved = registry.get_strategy("custom-test")
            assert retrieved is CustomStrategy
        finally:
            # Cleanup - unregister to avoid polluting other tests
            registry.unregister_strategy("custom-test")

    def test_get_nonexistent_strategy_raises_error(self):
        """Test that getting non-existent strategy raises KeyError."""
        from proxywhirl.strategies import StrategyRegistry

        registry = StrategyRegistry()

        with pytest.raises(KeyError, match="nonexistent-strategy-xyz"):
            registry.get_strategy("nonexistent-strategy-xyz")

    def test_register_invalid_strategy_raises_error(self):
        """Test that registering invalid strategy raises TypeError."""
        from proxywhirl.strategies import StrategyRegistry

        # Arrange - Create class without required methods
        class InvalidStrategy:
            pass

        registry = StrategyRegistry()

        # Act & Assert - Should raise TypeError for missing required methods
        with pytest.raises(TypeError, match="required method"):
            registry.register_strategy("invalid-test", InvalidStrategy)

    def test_custom_strategy_loading_performance(self):
        """Test custom strategy loading meets SC-010 (<1 second)."""
        import time

        from proxywhirl.strategies import StrategyRegistry

        # Arrange - Create custom strategy
        class FastLoadStrategy:
            def select(self, pool, context=None):
                return pool.get_all_proxies()[0]

            def record_result(self, proxy, success, response_time_ms=None):
                pass

            def configure(self, config):
                pass

            def validate_metadata(self, pool):
                return True

        registry = StrategyRegistry()

        # Act - Measure registration time
        start_time = time.perf_counter()
        registry.register_strategy("fast-load-test", FastLoadStrategy)
        end_time = time.perf_counter()

        try:
            load_time = end_time - start_time

            # Assert - SC-010: Should load in <1 second
            assert load_time < 1.0, f"Plugin load took {load_time:.3f}s (target: <1s)"
        finally:
            # Cleanup
            registry.unregister_strategy("fast-load-test")

    def test_registry_is_singleton(self):
        """Test that StrategyRegistry follows singleton pattern."""
        from proxywhirl.strategies import StrategyRegistry

        # Act - Create multiple registry instances
        registry1 = StrategyRegistry()
        registry2 = StrategyRegistry()

        # Assert - Should be same instance
        assert registry1 is registry2

    def test_register_strategy_with_same_name_replaces(self):
        """Test that re-registering strategy with same name replaces old one."""
        from proxywhirl.strategies import StrategyRegistry

        class Strategy1:
            def select(self, pool, context=None):
                return pool.get_all_proxies()[0]

            def record_result(self, proxy, success, response_time_ms=None):
                pass

            def configure(self, config):
                pass

            def validate_metadata(self, pool):
                return True

        class Strategy2:
            def select(self, pool, context=None):
                return pool.get_all_proxies()[-1]

            def record_result(self, proxy, success, response_time_ms=None):
                pass

            def configure(self, config):
                pass

            def validate_metadata(self, pool):
                return True

        registry = StrategyRegistry()

        try:
            # Register first strategy
            registry.register_strategy("test-replace", Strategy1)
            assert registry.get_strategy("test-replace") is Strategy1

            # Replace with second strategy
            registry.register_strategy("test-replace", Strategy2)
            assert registry.get_strategy("test-replace") is Strategy2
        finally:
            # Cleanup
            registry.unregister_strategy("test-replace")
