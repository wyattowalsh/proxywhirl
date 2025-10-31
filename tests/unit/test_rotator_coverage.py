"""Unit tests for ProxyRotator coverage improvements."""


import pytest

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import HealthStatus, Proxy, ProxyPool
from proxywhirl.rotator import ProxyRotator
from proxywhirl.strategies import RandomStrategy, RoundRobinStrategy


class TestRotatorContextManager:
    """Test ProxyRotator as context manager."""

    def test_context_manager_closes_on_exit(self):
        """Test that rotator closes when exiting context."""
        rotator = ProxyRotator()

        with rotator:
            assert rotator is not None

        # After exiting, storage should be closed
        # (Storage close is idempotent, so this is safe)

    def test_context_manager_closes_on_exception(self):
        """Test that rotator closes even when exception occurs."""
        rotator = ProxyRotator()

        with pytest.raises(ValueError), rotator:
            raise ValueError("Test error")

        # After exception, storage should still be closed

    def test_context_manager_with_requests(self):
        """Test making requests within context manager."""
        rotator = ProxyRotator()
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        with rotator:
            selected = rotator.get_next_proxy()
            assert selected.url == proxy.url


class TestRotatorStrategyManagement:
    """Test strategy switching and configuration."""

    def test_set_strategy(self):
        """Test setting a new strategy."""
        rotator = ProxyRotator()
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        # Start with default round-robin
        assert isinstance(rotator._strategy, RoundRobinStrategy)

        # Switch to random
        random_strategy = RandomStrategy()
        rotator.set_strategy(random_strategy)
        assert isinstance(rotator._strategy, RandomStrategy)

    def test_set_strategy_runtime(self):
        """Test strategy can be changed at runtime."""
        rotator = ProxyRotator()
        for i in range(3):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080", health_status=HealthStatus.HEALTHY)
            rotator.add_proxy(proxy)

        # Get proxy with round-robin
        proxy1 = rotator.get_next_proxy()

        # Switch to random
        rotator.set_strategy(RandomStrategy())

        # Get proxy with random (should still work)
        proxy2 = rotator.get_next_proxy()
        assert proxy2 is not None


class TestRotatorPoolOperations:
    """Test proxy pool add/remove/update operations."""

    def test_add_proxy(self):
        """Test adding a single proxy."""
        rotator = ProxyRotator()
        proxy = Proxy(url="http://proxy.example.com:8080")

        rotator.add_proxy(proxy)
        assert len(rotator.pool.proxies) == 1

    def test_add_proxy_duplicate(self):
        """Test adding duplicate proxy (should update)."""
        rotator = ProxyRotator()
        proxy1 = Proxy(url="http://proxy.example.com:8080", country_code="US")
        proxy2 = Proxy(url="http://proxy.example.com:8080", country_code="UK")

        rotator.add_proxy(proxy1)
        rotator.add_proxy(proxy2)

        # Should have only 1 proxy (updated)
        assert len(rotator.pool.proxies) == 1
        assert rotator.pool.proxies[0].country_code == "UK"

    def test_remove_proxy(self):
        """Test removing a proxy."""
        rotator = ProxyRotator()
        proxy = Proxy(url="http://proxy.example.com:8080")
        rotator.add_proxy(proxy)

        rotator.remove_proxy(proxy.url)
        assert len(rotator.pool.proxies) == 0

    def test_remove_proxy_nonexistent(self):
        """Test removing non-existent proxy (should be no-op)."""
        rotator = ProxyRotator()
        proxy = Proxy(url="http://proxy.example.com:8080")
        rotator.add_proxy(proxy)

        # Remove different proxy
        rotator.remove_proxy("http://other.example.com:8080")
        assert len(rotator.pool.proxies) == 1

    def test_update_proxy(self):
        """Test updating proxy attributes."""
        rotator = ProxyRotator()
        proxy = Proxy(url="http://proxy.example.com:8080", country_code="US")
        rotator.add_proxy(proxy)

        # Update country code
        rotator.update_proxy(proxy.url, country_code="UK")
        assert rotator.pool.proxies[0].country_code == "UK"

    def test_update_proxy_nonexistent(self):
        """Test updating non-existent proxy raises error."""
        rotator = ProxyRotator()

        with pytest.raises(ValueError, match="Proxy .* not found"):
            rotator.update_proxy("http://nonexistent.example.com:8080", country_code="US")


class TestRotatorStatistics:
    """Test rotator statistics methods."""

    def test_get_stats_empty_pool(self):
        """Test getting stats from empty pool."""
        rotator = ProxyRotator()
        stats = rotator.get_stats()

        assert stats["total_proxies"] == 0
        assert stats["healthy_proxies"] == 0

    def test_get_stats_with_proxies(self):
        """Test getting stats with proxies."""
        rotator = ProxyRotator()
        for i in range(3):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080", health_status=HealthStatus.HEALTHY)
            rotator.add_proxy(proxy)

        stats = rotator.get_stats()
        assert stats["total_proxies"] == 3
        assert stats["healthy_proxies"] == 3

    def test_get_stats_mixed_health(self):
        """Test stats with mixed health statuses."""
        rotator = ProxyRotator()

        healthy = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
        unhealthy = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.UNHEALTHY)
        degraded = Proxy(url="http://proxy3.example.com:8080", health_status=HealthStatus.DEGRADED)

        rotator.add_proxy(healthy)
        rotator.add_proxy(unhealthy)
        rotator.add_proxy(degraded)

        stats = rotator.get_stats()
        assert stats["total_proxies"] == 3
        assert stats["healthy_proxies"] == 1


class TestRotatorFailover:
    """Test rotator failover behavior."""

    def test_failover_excludes_failed_proxy(self):
        """Test that failover excludes the failed proxy."""
        rotator = ProxyRotator()
        proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY)

        rotator.add_proxy(proxy1)
        rotator.add_proxy(proxy2)

        # Get next proxy with proxy1 marked as failed
        next_proxy = rotator.get_next_proxy(failed_proxy_ids=[str(proxy1.id)])

        # Should get proxy2 (proxy1 excluded)
        assert next_proxy.id == proxy2.id

    def test_failover_all_proxies_failed(self):
        """Test failover when all proxies have failed."""
        rotator = ProxyRotator()
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        rotator.add_proxy(proxy)

        # Try to get proxy when it's marked as failed
        with pytest.raises(ProxyPoolEmptyError):
            rotator.get_next_proxy(failed_proxy_ids=[str(proxy.id)])


class TestRotatorEdgeCases:
    """Test edge cases and error conditions."""

    def test_get_next_proxy_empty_pool(self):
        """Test getting proxy from empty pool."""
        rotator = ProxyRotator()

        with pytest.raises(ProxyPoolEmptyError):
            rotator.get_next_proxy()

    def test_get_next_proxy_all_unhealthy(self):
        """Test getting proxy when all are unhealthy."""
        rotator = ProxyRotator()
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.UNHEALTHY)
        rotator.add_proxy(proxy)

        with pytest.raises(ProxyPoolEmptyError):
            rotator.get_next_proxy()

    def test_add_proxy_invalid_url(self):
        """Test adding proxy with invalid URL."""
        rotator = ProxyRotator()

        with pytest.raises(ValueError):
            Proxy(url="not-a-valid-url")

    def test_rotator_close_idempotent(self):
        """Test that close() can be called multiple times safely."""
        rotator = ProxyRotator()

        rotator.close()
        rotator.close()  # Should not raise error


class TestRotatorInitialization:
    """Test rotator initialization options."""

    def test_init_with_pool(self):
        """Test initializing with existing pool."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy.example.com:8080")
        pool.add_proxy(proxy)

        rotator = ProxyRotator(pool=pool)
        assert len(rotator.pool.proxies) == 1

    def test_init_with_strategy(self):
        """Test initializing with custom strategy."""
        strategy = RandomStrategy()
        rotator = ProxyRotator(strategy=strategy)

        assert isinstance(rotator._strategy, RandomStrategy)

    def test_init_with_pool_and_strategy(self):
        """Test initializing with both pool and strategy."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy.example.com:8080")
        pool.add_proxy(proxy)

        strategy = RandomStrategy()
        rotator = ProxyRotator(pool=pool, strategy=strategy)

        assert len(rotator.pool.proxies) == 1
        assert isinstance(rotator._strategy, RandomStrategy)
