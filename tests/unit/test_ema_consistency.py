"""
Unit tests for EMA calculation consistency.

Tests that EMA (Exponential Moving Average) calculations are consistent
between Proxy.update_metrics(), Proxy.record_success(), and Proxy.complete_request().

Also tests the new StrategyState pattern which separates mutable EMA state
from proxy identity, allowing different strategies to maintain independent
per-proxy metrics.
"""

from uuid import uuid4

import pytest

from proxywhirl.models import Proxy, StrategyConfig
from proxywhirl.strategies import (
    LeastUsedStrategy,
    PerformanceBasedStrategy,
    ProxyMetrics,
    RandomStrategy,
    RoundRobinStrategy,
    StrategyState,
    WeightedStrategy,
)


class TestEMAConsistency:
    """Test EMA calculation consistency across Proxy methods."""

    def test_update_metrics_initializes_both_ema_fields(self):
        """Test that update_metrics initializes both average and ema fields."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        proxy.update_metrics(response_time_ms=100.0)

        assert proxy.average_response_time_ms == 100.0
        assert proxy.ema_response_time_ms == 100.0

    def test_update_metrics_uses_same_alpha_for_both_fields(self):
        """Test that update_metrics uses ema_alpha for both average and ema."""
        proxy = Proxy(url="http://proxy.example.com:8080", ema_alpha=0.3)

        # Initialize with first value
        proxy.update_metrics(response_time_ms=100.0)
        assert proxy.average_response_time_ms == 100.0
        assert proxy.ema_response_time_ms == 100.0

        # Update with second value
        proxy.update_metrics(response_time_ms=200.0)

        # Both should use ema_alpha=0.3
        expected = 0.3 * 200.0 + 0.7 * 100.0  # 130.0
        assert proxy.average_response_time_ms == expected
        assert proxy.ema_response_time_ms == expected

    def test_record_success_uses_configurable_alpha(self):
        """Test that record_success uses proxy's ema_alpha, not hardcoded value."""
        proxy = Proxy(url="http://proxy.example.com:8080", ema_alpha=0.5)

        # First success
        proxy.record_success(response_time_ms=100.0)
        assert proxy.average_response_time_ms == 100.0

        # Second success - should use alpha=0.5
        proxy.record_success(response_time_ms=200.0)

        expected = 0.5 * 200.0 + 0.5 * 100.0  # 150.0
        assert proxy.average_response_time_ms == expected
        assert proxy.ema_response_time_ms == expected

    def test_complete_request_updates_ema_via_record_success(self):
        """Test that complete_request delegates EMA updates to record_success."""
        proxy = Proxy(url="http://proxy.example.com:8080", ema_alpha=0.2)

        # Mark request start
        proxy.start_request()

        # Complete request with success
        proxy.complete_request(success=True, response_time_ms=100.0)

        # Both fields should be initialized
        assert proxy.average_response_time_ms == 100.0
        assert proxy.ema_response_time_ms == 100.0

        # Mark another request
        proxy.start_request()

        # Complete with different time
        proxy.complete_request(success=True, response_time_ms=200.0)

        # Should use alpha=0.2
        expected = 0.2 * 200.0 + 0.8 * 100.0  # 120.0
        assert proxy.average_response_time_ms == expected
        assert proxy.ema_response_time_ms == expected

    def test_ema_alpha_default_value(self):
        """Test that ema_alpha has correct default value."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        assert proxy.ema_alpha == 0.2

    def test_ema_alpha_configurable(self):
        """Test that ema_alpha can be configured."""
        proxy = Proxy(url="http://proxy.example.com:8080", ema_alpha=0.7)
        assert proxy.ema_alpha == 0.7

    def test_update_metrics_separate_from_complete_request(self):
        """Test that update_metrics can be called independently."""
        proxy = Proxy(url="http://proxy.example.com:8080", ema_alpha=0.25)

        # Call update_metrics directly
        proxy.update_metrics(response_time_ms=80.0)

        # Check values are updated
        assert proxy.average_response_time_ms == 80.0
        assert proxy.ema_response_time_ms == 80.0

        # Call again
        proxy.update_metrics(response_time_ms=120.0)

        expected = 0.25 * 120.0 + 0.75 * 80.0  # 90.0
        assert proxy.average_response_time_ms == expected
        assert proxy.ema_response_time_ms == expected

    def test_ema_consistency_across_multiple_updates(self):
        """Test that EMA remains consistent across many updates."""
        proxy = Proxy(url="http://proxy.example.com:8080", ema_alpha=0.3)

        response_times = [100.0, 150.0, 200.0, 250.0, 300.0]

        for i, rt in enumerate(response_times):
            proxy.update_metrics(response_time_ms=rt)

            # Both fields should always be equal
            assert proxy.average_response_time_ms == proxy.ema_response_time_ms

            # Verify they're not just both None
            assert proxy.average_response_time_ms is not None


class TestStrategyConfigurationEMA:
    """Test that strategies use StrategyConfig.ema_alpha without mutating proxy state.

    Note: Proxy.ema_alpha is deprecated. Strategies should NOT mutate this field.
    Instead, strategies pass their configured alpha to proxy methods like
    complete_request() and record_success(). This separation ensures that:
    1. Proxy identity remains immutable
    2. Different strategies can use different alpha values independently
    3. The same proxy can be used by multiple strategies without conflicts
    """

    def test_round_robin_preserves_proxy_ema_alpha(self):
        """Test that RoundRobinStrategy does NOT mutate proxy.ema_alpha."""
        from proxywhirl.models import ProxyPool

        strategy = RoundRobinStrategy()
        config = StrategyConfig(ema_alpha=0.4)
        strategy.configure(config)

        # Create pool with proxy
        pool = ProxyPool(name="test")
        proxy = Proxy(url="http://proxy.example.com:8080", ema_alpha=0.2)
        pool.add_proxy(proxy)

        # Select proxy - should NOT mutate proxy.ema_alpha
        selected = strategy.select(pool)

        # Proxy's ema_alpha should remain unchanged (proxy identity is immutable)
        assert selected.ema_alpha == 0.2
        # Strategy's config should have the configured value
        assert strategy.config.ema_alpha == 0.4

    def test_random_strategy_preserves_proxy_ema_alpha(self):
        """Test that RandomStrategy does NOT mutate proxy.ema_alpha."""
        from proxywhirl.models import ProxyPool

        strategy = RandomStrategy()
        config = StrategyConfig(ema_alpha=0.6)
        strategy.configure(config)

        # Create pool with proxy
        pool = ProxyPool(name="test")
        proxy = Proxy(url="http://proxy.example.com:8080", ema_alpha=0.2)
        pool.add_proxy(proxy)

        # Select proxy - should NOT mutate proxy.ema_alpha
        selected = strategy.select(pool)

        # Proxy's ema_alpha should remain unchanged
        assert selected.ema_alpha == 0.2
        # Strategy's config should have the configured value
        assert strategy.config.ema_alpha == 0.6

    def test_weighted_strategy_preserves_proxy_ema_alpha(self):
        """Test that WeightedStrategy does NOT mutate proxy.ema_alpha."""
        from proxywhirl.models import ProxyPool

        strategy = WeightedStrategy()
        config = StrategyConfig(ema_alpha=0.35)
        strategy.configure(config)

        # Create pool with proxy
        pool = ProxyPool(name="test")
        proxy = Proxy(url="http://proxy.example.com:8080", ema_alpha=0.2)
        pool.add_proxy(proxy)

        # Select proxy - should NOT mutate proxy.ema_alpha
        selected = strategy.select(pool)

        # Proxy's ema_alpha should remain unchanged
        assert selected.ema_alpha == 0.2
        # Strategy's config should have the configured value
        assert strategy.config.ema_alpha == 0.35

    def test_least_used_strategy_preserves_proxy_ema_alpha(self):
        """Test that LeastUsedStrategy does NOT mutate proxy.ema_alpha."""
        from proxywhirl.models import ProxyPool

        strategy = LeastUsedStrategy()
        config = StrategyConfig(ema_alpha=0.15)
        strategy.configure(config)

        # Create pool with proxy
        pool = ProxyPool(name="test")
        proxy = Proxy(url="http://proxy.example.com:8080", ema_alpha=0.2)
        pool.add_proxy(proxy)

        # Select proxy - should NOT mutate proxy.ema_alpha
        selected = strategy.select(pool)

        # Proxy's ema_alpha should remain unchanged
        assert selected.ema_alpha == 0.2
        # Strategy's config should have the configured value
        assert strategy.config.ema_alpha == 0.15

    def test_performance_based_strategy_preserves_proxy_ema_alpha(self):
        """Test that PerformanceBasedStrategy does NOT mutate proxy.ema_alpha."""
        from proxywhirl.models import ProxyPool

        strategy = PerformanceBasedStrategy()
        config = StrategyConfig(ema_alpha=0.8)
        strategy.configure(config)

        # Create pool with proxy that has EMA data
        pool = ProxyPool(name="test")
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            ema_alpha=0.2,
            ema_response_time_ms=100.0,  # Required for performance-based selection
        )
        pool.add_proxy(proxy)

        # Select proxy - should NOT mutate proxy.ema_alpha
        selected = strategy.select(pool)

        # Proxy's ema_alpha should remain unchanged
        assert selected.ema_alpha == 0.2
        # Strategy's config should have the configured value
        assert strategy.config.ema_alpha == 0.8

    def test_strategy_config_default_ema_alpha(self):
        """Test that StrategyConfig has correct default ema_alpha."""
        config = StrategyConfig()
        assert config.ema_alpha == 0.2

    def test_strategy_config_ema_alpha_range_validation(self):
        """Test that StrategyConfig validates ema_alpha range."""
        from pydantic import ValidationError

        # Valid values
        assert StrategyConfig(ema_alpha=0.0).ema_alpha == 0.0
        assert StrategyConfig(ema_alpha=0.5).ema_alpha == 0.5
        assert StrategyConfig(ema_alpha=1.0).ema_alpha == 1.0

        # Invalid values
        with pytest.raises(ValidationError):
            StrategyConfig(ema_alpha=-0.1)

        with pytest.raises(ValidationError):
            StrategyConfig(ema_alpha=1.1)


class TestEMAIntegration:
    """Integration tests for EMA consistency across workflows."""

    def test_strategy_select_and_record_result_consistent(self):
        """Test that strategy select -> record_result maintains EMA consistency.

        The strategy passes its configured alpha to proxy methods, ensuring
        consistent EMA calculations without mutating proxy.ema_alpha.
        """
        from proxywhirl.models import ProxyPool

        strategy = RoundRobinStrategy()
        config = StrategyConfig(ema_alpha=0.3)
        strategy.configure(config)

        # Create pool
        pool = ProxyPool(name="test")
        proxy = Proxy(url="http://proxy.example.com:8080")
        pool.add_proxy(proxy)

        # Select proxy - proxy.ema_alpha should NOT change
        selected = strategy.select(pool)
        assert selected.ema_alpha == 0.2  # Default, unchanged

        # Record result - strategy passes config.ema_alpha to proxy methods
        strategy.record_result(selected, success=True, response_time_ms=100.0)

        # Check EMA was updated with strategy's configured alpha
        assert selected.average_response_time_ms == 100.0
        assert selected.ema_response_time_ms == 100.0

        # Record another result
        strategy.record_result(selected, success=True, response_time_ms=200.0)

        # Should use strategy's alpha=0.3 (passed to proxy.complete_request)
        expected = 0.3 * 200.0 + 0.7 * 100.0  # 130.0
        assert selected.average_response_time_ms == expected
        assert selected.ema_response_time_ms == expected

    def test_multiple_strategies_share_same_ema_calculation(self):
        """Test that different strategies use the same EMA calculation."""
        from proxywhirl.models import ProxyPool

        # Test with two different strategies
        for strategy_class in [RoundRobinStrategy, RandomStrategy]:
            strategy = strategy_class()
            config = StrategyConfig(ema_alpha=0.4)
            strategy.configure(config)

            pool = ProxyPool(name="test")
            proxy = Proxy(url="http://proxy.example.com:8080")
            pool.add_proxy(proxy)

            # Select and record
            selected = strategy.select(pool)
            strategy.record_result(selected, success=True, response_time_ms=100.0)
            strategy.record_result(selected, success=True, response_time_ms=200.0)

            # Both strategies should produce same EMA
            expected = 0.4 * 200.0 + 0.6 * 100.0  # 140.0
            assert selected.average_response_time_ms == expected
            assert selected.ema_response_time_ms == expected


class TestStrategyState:
    """Test the StrategyState class for independent per-proxy metrics management."""

    def test_strategy_state_records_success(self):
        """Test that StrategyState correctly records successful requests."""
        state = StrategyState(ema_alpha=0.3)
        proxy_id = uuid4()

        state.record_success(proxy_id, response_time_ms=100.0)

        metrics = state.get_metrics(proxy_id)
        assert metrics.total_requests == 1
        assert metrics.total_successes == 1
        assert metrics.total_failures == 0
        assert metrics.ema_response_time_ms == 100.0

    def test_strategy_state_records_failure(self):
        """Test that StrategyState correctly records failed requests."""
        state = StrategyState(ema_alpha=0.3)
        proxy_id = uuid4()

        state.record_failure(proxy_id)

        metrics = state.get_metrics(proxy_id)
        assert metrics.total_requests == 1
        assert metrics.total_successes == 0
        assert metrics.total_failures == 1
        assert metrics.ema_response_time_ms is None

    def test_strategy_state_calculates_ema(self):
        """Test that StrategyState correctly calculates EMA."""
        state = StrategyState(ema_alpha=0.5)
        proxy_id = uuid4()

        state.record_success(proxy_id, response_time_ms=100.0)
        assert state.get_ema_response_time(proxy_id) == 100.0

        state.record_success(proxy_id, response_time_ms=200.0)
        # EMA = 0.5 * 200 + 0.5 * 100 = 150
        assert state.get_ema_response_time(proxy_id) == 150.0

    def test_strategy_state_success_rate(self):
        """Test that StrategyState correctly calculates success rate."""
        state = StrategyState(ema_alpha=0.2)
        proxy_id = uuid4()

        # 3 successes, 2 failures = 60% success rate
        state.record_success(proxy_id, response_time_ms=100.0)
        state.record_success(proxy_id, response_time_ms=100.0)
        state.record_success(proxy_id, response_time_ms=100.0)
        state.record_failure(proxy_id)
        state.record_failure(proxy_id)

        assert state.get_success_rate(proxy_id) == pytest.approx(0.6)

    def test_strategy_state_independent_per_proxy(self):
        """Test that StrategyState maintains independent metrics per proxy."""
        state = StrategyState(ema_alpha=0.3)
        proxy1_id = uuid4()
        proxy2_id = uuid4()

        state.record_success(proxy1_id, response_time_ms=100.0)
        state.record_success(proxy2_id, response_time_ms=500.0)
        state.record_failure(proxy1_id)

        metrics1 = state.get_metrics(proxy1_id)
        metrics2 = state.get_metrics(proxy2_id)

        assert metrics1.total_requests == 2
        assert metrics2.total_requests == 1
        assert metrics1.ema_response_time_ms == 100.0
        assert metrics2.ema_response_time_ms == 500.0

    def test_different_strategy_states_independent(self):
        """Test that different StrategyState instances are independent."""
        state1 = StrategyState(ema_alpha=0.3)
        state2 = StrategyState(ema_alpha=0.7)
        proxy_id = uuid4()

        # Record to both states
        state1.record_success(proxy_id, response_time_ms=100.0)
        state1.record_success(proxy_id, response_time_ms=200.0)

        state2.record_success(proxy_id, response_time_ms=100.0)
        state2.record_success(proxy_id, response_time_ms=200.0)

        # Different alphas produce different EMAs
        # State1: 0.3 * 200 + 0.7 * 100 = 130
        # State2: 0.7 * 200 + 0.3 * 100 = 170
        assert state1.get_ema_response_time(proxy_id) == pytest.approx(130.0)
        assert state2.get_ema_response_time(proxy_id) == pytest.approx(170.0)

    def test_strategy_state_clear_all(self):
        """Test that clear_all removes all metrics."""
        state = StrategyState(ema_alpha=0.3)
        proxy1_id = uuid4()
        proxy2_id = uuid4()

        state.record_success(proxy1_id, response_time_ms=100.0)
        state.record_success(proxy2_id, response_time_ms=200.0)

        state.clear_all()

        assert state.get_request_count(proxy1_id) == 0
        assert state.get_request_count(proxy2_id) == 0

    def test_proxy_metrics_update_ema(self):
        """Test ProxyMetrics.update_ema calculation."""
        metrics = ProxyMetrics()

        # First update initializes EMA
        metrics.update_ema(100.0, alpha=0.4)
        assert metrics.ema_response_time_ms == 100.0

        # Second update applies EMA formula
        metrics.update_ema(200.0, alpha=0.4)
        # EMA = 0.4 * 200 + 0.6 * 100 = 140
        assert metrics.ema_response_time_ms == pytest.approx(140.0)
