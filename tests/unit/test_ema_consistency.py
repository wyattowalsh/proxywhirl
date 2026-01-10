"""
Unit tests for EMA calculation consistency.

Tests that EMA (Exponential Moving Average) calculations are consistent
between Proxy.update_metrics(), Proxy.record_success(), and Proxy.complete_request().
"""

import pytest

from proxywhirl.models import Proxy, StrategyConfig
from proxywhirl.strategies import (
    LeastUsedStrategy,
    PerformanceBasedStrategy,
    RandomStrategy,
    RoundRobinStrategy,
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
    """Test that strategies configure proxy ema_alpha from StrategyConfig."""

    def test_round_robin_configures_ema_alpha(self):
        """Test that RoundRobinStrategy configures proxy ema_alpha from config."""
        from proxywhirl.models import ProxyPool

        strategy = RoundRobinStrategy()
        config = StrategyConfig(ema_alpha=0.4)
        strategy.configure(config)

        # Create pool with proxy
        pool = ProxyPool(name="test")
        proxy = Proxy(url="http://proxy.example.com:8080", ema_alpha=0.2)
        pool.add_proxy(proxy)

        # Select proxy - should apply config ema_alpha
        selected = strategy.select(pool)

        # Verify ema_alpha was updated
        assert selected.ema_alpha == 0.4

    def test_random_strategy_configures_ema_alpha(self):
        """Test that RandomStrategy configures proxy ema_alpha from config."""
        from proxywhirl.models import ProxyPool

        strategy = RandomStrategy()
        config = StrategyConfig(ema_alpha=0.6)
        strategy.configure(config)

        # Create pool with proxy
        pool = ProxyPool(name="test")
        proxy = Proxy(url="http://proxy.example.com:8080", ema_alpha=0.2)
        pool.add_proxy(proxy)

        # Select proxy - should apply config ema_alpha
        selected = strategy.select(pool)

        # Verify ema_alpha was updated
        assert selected.ema_alpha == 0.6

    def test_weighted_strategy_configures_ema_alpha(self):
        """Test that WeightedStrategy configures proxy ema_alpha from config."""
        from proxywhirl.models import ProxyPool

        strategy = WeightedStrategy()
        config = StrategyConfig(ema_alpha=0.35)
        strategy.configure(config)

        # Create pool with proxy
        pool = ProxyPool(name="test")
        proxy = Proxy(url="http://proxy.example.com:8080", ema_alpha=0.2)
        pool.add_proxy(proxy)

        # Select proxy - should apply config ema_alpha
        selected = strategy.select(pool)

        # Verify ema_alpha was updated
        assert selected.ema_alpha == 0.35

    def test_least_used_strategy_configures_ema_alpha(self):
        """Test that LeastUsedStrategy configures proxy ema_alpha from config."""
        from proxywhirl.models import ProxyPool

        strategy = LeastUsedStrategy()
        config = StrategyConfig(ema_alpha=0.15)
        strategy.configure(config)

        # Create pool with proxy
        pool = ProxyPool(name="test")
        proxy = Proxy(url="http://proxy.example.com:8080", ema_alpha=0.2)
        pool.add_proxy(proxy)

        # Select proxy - should apply config ema_alpha
        selected = strategy.select(pool)

        # Verify ema_alpha was updated
        assert selected.ema_alpha == 0.15

    def test_performance_based_strategy_configures_ema_alpha(self):
        """Test that PerformanceBasedStrategy configures proxy ema_alpha from config."""
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

        # Select proxy - should apply config ema_alpha
        selected = strategy.select(pool)

        # Verify ema_alpha was updated
        assert selected.ema_alpha == 0.8

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
        """Test that strategy select -> record_result maintains EMA consistency."""
        from proxywhirl.models import ProxyPool

        strategy = RoundRobinStrategy()
        config = StrategyConfig(ema_alpha=0.3)
        strategy.configure(config)

        # Create pool
        pool = ProxyPool(name="test")
        proxy = Proxy(url="http://proxy.example.com:8080")
        pool.add_proxy(proxy)

        # Select proxy
        selected = strategy.select(pool)
        assert selected.ema_alpha == 0.3

        # Record result
        strategy.record_result(selected, success=True, response_time_ms=100.0)

        # Check EMA was updated with configured alpha
        assert selected.average_response_time_ms == 100.0
        assert selected.ema_response_time_ms == 100.0

        # Record another result
        strategy.record_result(selected, success=True, response_time_ms=200.0)

        # Should use alpha=0.3
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
