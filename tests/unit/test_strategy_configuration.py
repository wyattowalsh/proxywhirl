"""Unit tests for strategy configuration methods."""

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
    GeoTargetedStrategy,
    LeastUsedStrategy,
    PerformanceBasedStrategy,
    RandomStrategy,
    RoundRobinStrategy,
    SessionPersistenceStrategy,
    WeightedStrategy,
)


class TestStrategyConfiguration:
    """Test strategy configuration methods."""

    def test_round_robin_configure(self):
        """Test RoundRobinStrategy.configure()."""
        strategy = RoundRobinStrategy()
        config = StrategyConfig()

        strategy.configure(config)
        assert strategy.config == config

    def test_random_configure(self):
        """Test RandomStrategy.configure()."""
        strategy = RandomStrategy()
        config = StrategyConfig()

        strategy.configure(config)
        assert strategy.config == config

    def test_least_used_configure(self):
        """Test LeastUsedStrategy.configure()."""
        strategy = LeastUsedStrategy()
        config = StrategyConfig()

        strategy.configure(config)
        assert strategy.config == config

    def test_weighted_configure(self):
        """Test WeightedStrategy.configure()."""
        strategy = WeightedStrategy()
        config = StrategyConfig()

        strategy.configure(config)
        assert strategy.config == config

    def test_performance_based_configure(self):
        """Test PerformanceBasedStrategy.configure()."""
        strategy = PerformanceBasedStrategy()
        config = StrategyConfig(ema_alpha=0.3)

        strategy.configure(config)
        assert strategy.config == config

    def test_session_persistence_configure(self):
        """Test SessionPersistenceStrategy.configure()."""
        strategy = SessionPersistenceStrategy()
        config = StrategyConfig(session_timeout_seconds=7200)

        strategy.configure(config)
        assert strategy.config == config

    def test_geo_targeted_configure(self):
        """Test GeoTargetedStrategy.configure()."""
        strategy = GeoTargetedStrategy()
        config = StrategyConfig(geo_preferences=["US", "UK"])

        strategy.configure(config)
        assert strategy.config == config


class TestStrategyEdgeCases:
    """Test strategy edge cases and error conditions."""

    def test_round_robin_empty_pool_after_filtering(self):
        """Test round-robin with all proxies filtered out."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy)

        strategy = RoundRobinStrategy()
        context = SelectionContext(failed_proxy_ids=[str(proxy.id)])

        with pytest.raises(
            ProxyPoolEmptyError, match="No healthy proxies available after filtering"
        ):
            strategy.select(pool, context)

    def test_random_empty_pool_after_filtering(self):
        """Test random with all proxies filtered out."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy)

        strategy = RandomStrategy()
        context = SelectionContext(failed_proxy_ids=[str(proxy.id)])

        with pytest.raises(
            ProxyPoolEmptyError, match="No healthy proxies available after filtering"
        ):
            strategy.select(pool, context)

    def test_least_used_empty_pool_after_filtering(self):
        """Test least-used with all proxies filtered out."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy)

        strategy = LeastUsedStrategy()
        context = SelectionContext(failed_proxy_ids=[str(proxy.id)])

        with pytest.raises(
            ProxyPoolEmptyError, match="No healthy proxies available after filtering"
        ):
            strategy.select(pool, context)

    def test_weighted_empty_pool_after_filtering(self):
        """Test weighted with all proxies filtered out."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
        proxy.total_requests = 10
        proxy.total_successes = 5
        pool.add_proxy(proxy)

        strategy = WeightedStrategy()
        context = SelectionContext(failed_proxy_ids=[str(proxy.id)])

        with pytest.raises(
            ProxyPoolEmptyError, match="No healthy proxies available after filtering"
        ):
            strategy.select(pool, context)

    def test_performance_based_empty_pool_after_filtering(self):
        """Test performance-based with all proxies filtered out."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
        proxy.ema_response_time_ms = 100.0
        pool.add_proxy(proxy)

        strategy = PerformanceBasedStrategy()
        context = SelectionContext(failed_proxy_ids=[str(proxy.id)])

        with pytest.raises(
            ProxyPoolEmptyError, match="No healthy proxies available after filtering"
        ):
            strategy.select(pool, context)

    def test_geo_targeted_empty_pool_after_filtering(self):
        """Test geo-targeted with all proxies filtered out."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(
            url="http://proxy1.example.com:8080",
            health_status=HealthStatus.HEALTHY,
            country_code="US",
        )
        pool.add_proxy(proxy)

        strategy = GeoTargetedStrategy()
        context = SelectionContext(failed_proxy_ids=[str(proxy.id)], target_country="US")

        with pytest.raises(
            ProxyPoolEmptyError, match="No healthy proxies available after filtering"
        ):
            strategy.select(pool, context)


class TestStrategyWithContext:
    """Test strategies with SelectionContext."""

    def test_round_robin_with_context_no_failures(self):
        """Test round-robin with context but no failed proxies."""
        pool = ProxyPool(name="test-pool")
        for i in range(3):
            proxy = Proxy(
                url=f"http://proxy{i}.example.com:8080", health_status=HealthStatus.HEALTHY
            )
            pool.add_proxy(proxy)

        strategy = RoundRobinStrategy()
        context = SelectionContext()

        # Should work normally
        proxy = strategy.select(pool, context)
        assert proxy is not None

    def test_random_with_context_no_failures(self):
        """Test random with context but no failed proxies."""
        pool = ProxyPool(name="test-pool")
        for i in range(3):
            proxy = Proxy(
                url=f"http://proxy{i}.example.com:8080", health_status=HealthStatus.HEALTHY
            )
            pool.add_proxy(proxy)

        strategy = RandomStrategy()
        context = SelectionContext()

        # Should work normally
        proxy = strategy.select(pool, context)
        assert proxy is not None

    def test_weighted_with_no_requests_history(self):
        """Test weighted strategy with proxies that have no request history."""
        pool = ProxyPool(name="test-pool")
        for i in range(3):
            proxy = Proxy(
                url=f"http://proxy{i}.example.com:8080", health_status=HealthStatus.HEALTHY
            )
            # Don't set any request history - total_requests = 0
            pool.add_proxy(proxy)

        strategy = WeightedStrategy()

        # Should handle zero-request proxies gracefully
        proxy = strategy.select(pool)
        assert proxy is not None

    def test_performance_based_with_no_metrics(self):
        """Test performance-based strategy with proxies that have no metrics."""
        pool = ProxyPool(name="test-pool")
        for i in range(3):
            proxy = Proxy(
                url=f"http://proxy{i}.example.com:8080", health_status=HealthStatus.HEALTHY
            )
            # Don't set ema_response_time_ms - it's None
            pool.add_proxy(proxy)

        strategy = PerformanceBasedStrategy()

        # Should handle proxies with no metrics
        proxy = strategy.select(pool)
        assert proxy is not None


class TestStrategyResetAndState:
    """Test strategy state management."""

    def test_round_robin_maintains_index(self):
        """Test that round-robin maintains its index across calls."""
        pool = ProxyPool(name="test-pool")
        proxies = []
        for i in range(3):
            proxy = Proxy(
                url=f"http://proxy{i}.example.com:8080", health_status=HealthStatus.HEALTHY
            )
            pool.add_proxy(proxy)
            proxies.append(proxy)

        strategy = RoundRobinStrategy()

        # First three selections should cycle through all proxies
        selected_urls = []
        for _ in range(3):
            proxy = strategy.select(pool)
            selected_urls.append(proxy.url)

        # Should have selected each proxy once
        assert len(set(selected_urls)) == 3

    def test_session_persistence_without_context(self):
        """Test session persistence requires context with session_id."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy)

        strategy = SessionPersistenceStrategy()

        # Should raise error when no context provided
        with pytest.raises(ValueError, match="requires SelectionContext with session_id"):
            strategy.select(pool)

    def test_session_persistence_with_context_no_session_id(self):
        """Test session persistence with context but no session_id."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy)

        strategy = SessionPersistenceStrategy()
        context = SelectionContext()  # No session_id

        # Should raise error when session_id is None
        with pytest.raises(ValueError, match="requires SelectionContext with session_id"):
            strategy.select(pool, context)
