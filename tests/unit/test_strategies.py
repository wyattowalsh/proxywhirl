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
        """Test that performance-based handles proxies without EMA data."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        # Proxy with EMA
        with_ema = Proxy(url="http://with-ema.com:8080", health_status=HealthStatus.HEALTHY)
        with_ema.ema_response_time_ms = 100.0

        # Proxy without EMA (None or 0)
        without_ema = Proxy(url="http://without-ema.com:8080", health_status=HealthStatus.HEALTHY)
        without_ema.ema_response_time_ms = None

        pool.add_proxy(with_ema)
        pool.add_proxy(without_ema)

        strategy = PerformanceBasedStrategy()
        context = SelectionContext()

        # Act
        selected = strategy.select(pool, context)

        # Assert - Should only select proxy with EMA data
        assert selected.url == "http://with-ema.com:8080"

    def test_select_raises_when_no_ema_data_available(self):
        """Test that performance-based raises error when no proxies have EMA data."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy1.ema_response_time_ms = None

        proxy2 = Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2.ema_response_time_ms = None

        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        strategy = PerformanceBasedStrategy()
        context = SelectionContext()

        # Act & Assert
        with pytest.raises(ProxyPoolEmptyError, match="No proxies with EMA data"):
            strategy.select(pool, context)

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

    def test_validate_metadata_checks_ema_availability(self):
        """Test that performance-based validates EMA metadata presence."""
        # Arrange
        pool = ProxyPool(name="test-pool")

        # Pool with EMA data
        proxy_with_ema = Proxy(url="http://proxy1.com:8080")
        proxy_with_ema.ema_response_time_ms = 100.0
        pool.add_proxy(proxy_with_ema)

        strategy = PerformanceBasedStrategy()

        # Act
        is_valid = strategy.validate_metadata(pool)

        # Assert
        assert is_valid is True

        # Now test pool without EMA data
        pool_no_ema = ProxyPool(name="no-ema-pool")
        proxy_no_ema = Proxy(url="http://proxy2.com:8080")
        proxy_no_ema.ema_response_time_ms = None
        pool_no_ema.add_proxy(proxy_no_ema)

        is_valid_no_ema = strategy.validate_metadata(pool_no_ema)
        assert is_valid_no_ema is False

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
        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy1.ema_response_time_ms = 50.0  # Fastest - should have highest weight

        proxy2 = Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2.ema_response_time_ms = 100.0  # Medium

        proxy3 = Proxy(url="http://proxy3.com:8080", health_status=HealthStatus.HEALTHY)
        proxy3.ema_response_time_ms = 200.0  # Slowest - should have lowest weight

        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)
        pool.add_proxy(proxy3)

        strategy = PerformanceBasedStrategy()
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


class TestPluginArchitecture:
    """Unit tests for plugin architecture (Phase 9, T067)."""

    def test_register_custom_strategy(self):
        """
        Test custom strategy registration.

        Validates that custom strategies can be registered and retrieved.
        """
        pytest.skip("StrategyRegistry not yet implemented")

        # TODO: Will be implemented in T070
        # from proxywhirl.strategies import StrategyRegistry
        #
        # # Arrange - Create custom strategy class
        # class CustomStrategy:
        #     def select(self, pool, context):
        #         return pool.get_all_proxies()[0]
        #
        #     def record_result(self, proxy, success, response_time_ms):
        #         pass
        #
        #     def configure(self, config):
        #         pass
        #
        # # Act - Register strategy
        # registry = StrategyRegistry()
        # registry.register_strategy("custom", CustomStrategy)
        #
        # # Assert - Can retrieve registered strategy
        # retrieved = registry.get_strategy("custom")
        # assert retrieved is CustomStrategy

    def test_get_nonexistent_strategy_raises_error(self):
        """Test that getting non-existent strategy raises clear error."""
        pytest.skip("StrategyRegistry not yet implemented")

        # TODO: Will be implemented in T070
        # from proxywhirl.strategies import StrategyRegistry
        # from proxywhirl.exceptions import StrategyNotFoundError
        #
        # registry = StrategyRegistry()
        #
        # with pytest.raises(StrategyNotFoundError, match="nonexistent"):
        #     registry.get_strategy("nonexistent")

    def test_register_invalid_strategy_raises_error(self):
        """Test that registering invalid strategy raises validation error."""
        pytest.skip("StrategyRegistry not yet implemented")

        # TODO: Will be implemented in T070
        # from proxywhirl.strategies import StrategyRegistry
        # from proxywhirl.exceptions import InvalidStrategyError
        #
        # # Arrange - Create class without required methods
        # class InvalidStrategy:
        #     pass
        #
        # registry = StrategyRegistry()
        #
        # # Act & Assert - Should raise validation error
        # with pytest.raises(InvalidStrategyError, match="missing required methods"):
        #     registry.register_strategy("invalid", InvalidStrategy)

    def test_custom_strategy_loading_performance(self):
        """
        Test custom strategy loading meets SC-010 (<1 second).

        Validates plugin load performance requirement.
        """
        pytest.skip("StrategyRegistry not yet implemented")

        # TODO: Will be implemented in T070
        # import time
        # from proxywhirl.strategies import StrategyRegistry
        #
        # # Arrange - Create custom strategy
        # class FastLoadStrategy:
        #     def select(self, pool, context):
        #         return pool.get_all_proxies()[0]
        #
        #     def record_result(self, proxy, success, response_time_ms):
        #         pass
        #
        #     def configure(self, config):
        #         pass
        #
        # registry = StrategyRegistry()
        #
        # # Act - Measure registration time
        # start_time = time.perf_counter()
        # registry.register_strategy("fast-load", FastLoadStrategy)
        # end_time = time.perf_counter()
        #
        # load_time = end_time - start_time
        #
        # # Assert - SC-010: Should load in <1 second
        # assert load_time < 1.0, f"Plugin load took {load_time:.3f}s (target: <1s)"

    def test_registry_is_singleton(self):
        """Test that StrategyRegistry follows singleton pattern."""
        pytest.skip("StrategyRegistry not yet implemented")

        # TODO: Will be implemented in T070
        # from proxywhirl.strategies import StrategyRegistry
        #
        # # Act - Create multiple registry instances
        # registry1 = StrategyRegistry()
        # registry2 = StrategyRegistry()
        #
        # # Assert - Should be same instance
        # assert registry1 is registry2

    def test_register_strategy_with_same_name_replaces(self):
        """Test that re-registering strategy with same name replaces old one."""
        pytest.skip("StrategyRegistry not yet implemented")

        # TODO: Will be implemented in T070
        # from proxywhirl.strategies import StrategyRegistry
        #
        # class Strategy1:
        #     def select(self, pool, context):
        #         return pool.get_all_proxies()[0]
        #
        #     def record_result(self, proxy, success, response_time_ms):
        #         pass
        #
        #     def configure(self, config):
        #         pass
        #
        # class Strategy2:
        #     def select(self, pool, context):
        #         return pool.get_all_proxies()[-1]
        #
        #     def record_result(self, proxy, success, response_time_ms):
        #         pass
        #
        #     def configure(self, config):
        #         pass
        #
        # registry = StrategyRegistry()
        #
        # # Register first strategy
        # registry.register_strategy("test", Strategy1)
        # assert registry.get_strategy("test") is Strategy1
        #
        # # Replace with second strategy
        # registry.register_strategy("test", Strategy2)
        # assert registry.get_strategy("test") is Strategy2
