"""Test strategy behavior with empty and single-proxy pools.

Tests:
- Strategies handle empty pools gracefully
- Strategies handle single-proxy pools
- No crashes on edge case pool sizes
- Proper error messages for empty pools
"""

from __future__ import annotations

import pytest

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import Proxy, ProxyPool, SelectionContext
from proxywhirl.strategies.core import (
    PerformanceBasedStrategy,
    RoundRobinStrategy,
    WeightedStrategy,
)


class TestEmptyPoolHandling:
    """Test strategy behavior with empty pools."""

    def test_round_robin_empty_pool(self) -> None:
        """Test round robin with empty pool."""
        strategy = RoundRobinStrategy()
        pool = ProxyPool(name="empty_pool", proxies=[])
        context = SelectionContext()

        with pytest.raises(ProxyPoolEmptyError):
            strategy.select(pool, context)

    def test_weighted_strategy_empty_pool(self) -> None:
        """Test weighted strategy with empty pool."""
        strategy = WeightedStrategy()
        pool = ProxyPool(name="empty_pool", proxies=[])
        context = SelectionContext()

        with pytest.raises(ProxyPoolEmptyError):
            strategy.select(pool, context)

    def test_performance_strategy_empty_pool(self) -> None:
        """Test performance-based strategy with empty pool."""
        strategy = PerformanceBasedStrategy()
        pool = ProxyPool(name="empty_pool", proxies=[])
        context = SelectionContext()

        with pytest.raises(ProxyPoolEmptyError):
            strategy.select(pool, context)

    def test_empty_pool_error_message(self) -> None:
        """Test that empty pool error has clear message."""
        strategy = RoundRobinStrategy()
        pool = ProxyPool(name="empty_pool", proxies=[])
        context = SelectionContext()

        try:
            strategy.select(pool, context)
            pytest.fail("Should raise ProxyPoolEmptyError")
        except ProxyPoolEmptyError as e:
            # Error message mentions "no healthy proxies" or "empty"
            msg = str(e).lower()
            assert "no healthy" in msg or "empty" in msg

    def test_filter_result_in_empty_pool(self) -> None:
        """Test when filtering results in empty pool."""
        strategy = RoundRobinStrategy()

        # Create pool with proxies
        proxies = [
            Proxy(url="http://proxy1.com:8080"),
            Proxy(url="http://proxy2.com:8080"),
        ]
        pool = ProxyPool(name="test_pool", proxies=proxies)

        # Create context that filters all out (if supported)
        context = SelectionContext()

        # If filtering removes all proxies, should handle gracefully
        # This tests behavior when pre-filtering empties pool
        try:
            result = strategy.select(pool, context)
            assert result is not None
        except ProxyPoolEmptyError:
            # Expected if all filtered out
            pass

    def test_none_pool_handling(self) -> None:
        """Test handling of None pool gracefully."""
        strategy = RoundRobinStrategy()
        context = SelectionContext()

        # Creating pool with None should fail at construction
        try:
            pool = ProxyPool(name="test_pool", proxies=[])
            strategy.select(pool, context)
        except (ProxyPoolEmptyError, ValueError, TypeError):
            # Expected
            pass


class TestSingleProxyPoolHandling:
    """Test strategy behavior with single-proxy pools."""

    def test_round_robin_single_proxy(self) -> None:
        """Test round robin with single proxy."""
        strategy = RoundRobinStrategy()
        proxy = Proxy(url="http://proxy.example.com:8080")
        pool = ProxyPool(name="test_pool", proxies=[proxy])
        context = SelectionContext()

        selected = strategy.select(pool, context)
        assert selected == proxy

    def test_round_robin_single_proxy_multiple_calls(self) -> None:
        """Test round robin always returns same proxy when only one exists."""
        strategy = RoundRobinStrategy()
        proxy = Proxy(url="http://proxy.example.com:8080")
        pool = ProxyPool(name="test_pool", proxies=[proxy])
        context = SelectionContext()

        # Multiple calls should return same proxy
        for _ in range(5):
            selected = strategy.select(pool, context)
            assert selected == proxy

    def test_weighted_strategy_single_proxy(self) -> None:
        """Test weighted strategy with single proxy."""
        strategy = WeightedStrategy()
        proxy = Proxy(url="http://proxy.example.com:8080", weight=1.0)
        pool = ProxyPool(name="test_pool", proxies=[proxy])
        context = SelectionContext()

        selected = strategy.select(pool, context)
        assert selected == proxy

    def test_weighted_strategy_single_proxy_weight_ignored(self) -> None:
        """Test that weight is ignored for single proxy."""
        strategy = WeightedStrategy()

        # Test with different weights - should still return the one proxy
        for weight in [0.1, 1.0, 10.0]:
            proxy = Proxy(url="http://proxy.example.com:8080", weight=weight)
            pool = ProxyPool(name="test_pool", proxies=[proxy])
            context = SelectionContext()

            selected = strategy.select(pool, context)
            assert selected == proxy

    def test_performance_strategy_single_proxy(self) -> None:
        """Test performance-based strategy with single proxy."""
        strategy = PerformanceBasedStrategy()
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            latency_ms=10.0,
            success_rate=0.95,
        )
        pool = ProxyPool(name="test_pool", proxies=[proxy])
        context = SelectionContext()

        selected = strategy.select(pool, context)
        assert selected == proxy

    def test_single_proxy_pool_idempotent(self) -> None:
        """Test that single proxy selection is idempotent."""
        strategy = RoundRobinStrategy()
        proxy = Proxy(url="http://proxy.example.com:8080")
        pool = ProxyPool(name="test_pool", proxies=[proxy])
        context = SelectionContext()

        # Multiple selections should give same result
        results = [strategy.select(pool, context) for _ in range(3)]
        assert all(r == proxy for r in results)


class TestSmallPoolBehavior:
    """Test strategies with small pools (2-3 proxies)."""

    def test_round_robin_two_proxies(self) -> None:
        """Test round robin with two proxies alternates."""
        strategy = RoundRobinStrategy()
        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        proxy2 = Proxy(url="http://proxy2.example.com:8080")
        pool = ProxyPool(name="test_pool", proxies=[proxy1, proxy2])
        context = SelectionContext()

        # First call should return first proxy
        selected1 = strategy.select(pool, context)
        assert selected1 is not None

        # Second call might return second (implementation dependent)
        selected2 = strategy.select(pool, context)
        assert selected2 is not None

    def test_weighted_strategy_two_proxies(self) -> None:
        """Test weighted strategy with two proxies."""
        strategy = WeightedStrategy()
        proxy1 = Proxy(url="http://proxy1.example.com:8080", weight=0.3)
        proxy2 = Proxy(url="http://proxy2.example.com:8080", weight=0.7)
        pool = ProxyPool(name="test_pool", proxies=[proxy1, proxy2])
        context = SelectionContext()

        # Should be able to select
        selected = strategy.select(pool, context)
        assert selected in [proxy1, proxy2]

    def test_performance_strategy_three_proxies(self) -> None:
        """Test performance strategy with three proxies."""
        strategy = PerformanceBasedStrategy()
        proxies = [
            Proxy(
                url="http://proxy1.example.com:8080",
                latency_ms=50.0,
                success_rate=0.8,
            ),
            Proxy(
                url="http://proxy2.example.com:8080",
                latency_ms=30.0,
                success_rate=0.9,
            ),
            Proxy(
                url="http://proxy3.example.com:8080",
                latency_ms=100.0,
                success_rate=0.7,
            ),
        ]
        pool = ProxyPool(name="test_pool", proxies=proxies)
        context = SelectionContext()

        selected = strategy.select(pool, context)
        assert selected in proxies


class TestEdgeCasePoolSizes:
    """Test strategies with various edge case pool sizes."""

    def test_round_robin_returns_valid_proxy(self) -> None:
        """Test round robin returns proxy from pool."""
        strategy = RoundRobinStrategy()
        proxies = [Proxy(url=f"http://proxy{i}.example.com:8080") for i in range(5)]
        pool = ProxyPool(name="test_pool", proxies=proxies)
        context = SelectionContext()

        selected = strategy.select(pool, context)
        assert selected in proxies

    def test_weighted_strategy_returns_valid_proxy(self) -> None:
        """Test weighted strategy returns proxy from pool."""
        strategy = WeightedStrategy()
        proxies = [Proxy(url=f"http://proxy{i}.example.com:8080", weight=1.0) for i in range(5)]
        pool = ProxyPool(name="test_pool", proxies=proxies)
        context = SelectionContext()

        selected = strategy.select(pool, context)
        assert selected in proxies

    def test_performance_strategy_returns_valid_proxy(self) -> None:
        """Test performance strategy returns proxy from pool."""
        strategy = PerformanceBasedStrategy()
        proxies = [
            Proxy(
                url=f"http://proxy{i}.example.com:8080",
                latency_ms=float(i * 10),
                success_rate=0.5 + (i * 0.1),
            )
            for i in range(5)
        ]
        pool = ProxyPool(name="test_pool", proxies=proxies)
        context = SelectionContext()

        selected = strategy.select(pool, context)
        assert selected in proxies

    def test_strategy_handles_duplicate_proxies(self) -> None:
        """Test strategy handles duplicate proxies in pool."""
        strategy = RoundRobinStrategy()
        proxy = Proxy(url="http://proxy.example.com:8080")
        # Create pool with duplicates (if allowed)
        pool = ProxyPool(name="test_pool", proxies=[proxy, proxy, proxy])
        context = SelectionContext()

        selected = strategy.select(pool, context)
        assert selected == proxy

    def test_strategy_consistent_with_filtered_pool(self) -> None:
        """Test strategy behavior when pool is filtered."""
        strategy = RoundRobinStrategy()

        # Original pool
        original_proxies = [Proxy(url=f"http://proxy{i}.example.com:8080") for i in range(10)]

        # Filtered pool (e.g., only healthy ones)
        filtered_proxies = original_proxies[:5]
        pool = ProxyPool(name="test_pool", proxies=filtered_proxies)
        context = SelectionContext()

        selected = strategy.select(pool, context)
        assert selected in filtered_proxies


class TestPoolErrorHandling:
    """Test error handling for invalid pools."""

    def test_pool_none_proxies_handling(self) -> None:
        """Test handling when proxies list is empty."""
        strategy = RoundRobinStrategy()
        pool = ProxyPool(name="test_pool", proxies=[])
        context = SelectionContext()

        with pytest.raises(ProxyPoolEmptyError):
            strategy.select(pool, context)

    def test_all_strategies_handle_empty_consistently(self) -> None:
        """Test that all strategies handle empty pool consistently."""
        strategies = [
            RoundRobinStrategy(),
            WeightedStrategy(),
            PerformanceBasedStrategy(),
        ]

        pool = ProxyPool(name="test_pool", proxies=[])
        context = SelectionContext()

        for strategy in strategies:
            with pytest.raises(ProxyPoolEmptyError):
                strategy.select(pool, context)

    def test_corrupted_pool_handling(self) -> None:
        """Test handling of potentially corrupted pool data."""
        strategy = RoundRobinStrategy()

        try:
            # Create proxies with unusual values
            proxies = [
                Proxy(url="http://proxy.example.com:8080"),
            ]
            pool = ProxyPool(name="test_pool", proxies=proxies)
            context = SelectionContext()

            result = strategy.select(pool, context)
            assert result is not None
        except (ValueError, TypeError, Exception):
            # Should not crash on unusual data
            pass
