"""Integration tests for TTL expiration workflow."""

from datetime import datetime, timedelta, timezone

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import Proxy, ProxyPool
from proxywhirl.strategies import RandomStrategy, RoundRobinStrategy


class TestTTLIntegration:
    """Integration tests for TTL expiration with rotation strategies."""

    def test_ttl_expiration_workflow_round_robin(self) -> None:
        """Test complete TTL workflow with round-robin strategy."""
        pool = ProxyPool(name="test_pool")
        strategy = RoundRobinStrategy()

        # Add mix of proxies
        valid_proxy1 = Proxy(
            url="http://valid1.proxy.com:8080",
            ttl=3600,  # Expires in 1 hour
        )
        valid_proxy2 = Proxy(
            url="http://valid2.proxy.com:8080",
            ttl=7200,  # Expires in 2 hours
        )
        expired_proxy = Proxy(
            url="http://expired.proxy.com:8080",
            ttl=-1800,  # Expired 30 min ago
        )

        pool.add_proxy(valid_proxy1)
        pool.add_proxy(valid_proxy2)
        pool.add_proxy(expired_proxy)

        assert pool.size == 3

        # Strategy should only select from valid proxies
        selected1 = strategy.select(pool)
        assert selected1 in [valid_proxy1, valid_proxy2]
        assert selected1 != expired_proxy

        selected2 = strategy.select(pool)
        assert selected2 in [valid_proxy1, valid_proxy2]
        assert selected2 != expired_proxy

        # Clean up expired proxies
        removed = pool.clear_expired()
        assert removed == 1
        assert pool.size == 2

        # Continue rotating through remaining valid proxies
        selected3 = strategy.select(pool)
        assert selected3 in [valid_proxy1, valid_proxy2]

    def test_ttl_expiration_workflow_random(self) -> None:
        """Test complete TTL workflow with random strategy."""
        pool = ProxyPool(name="test_pool")
        strategy = RandomStrategy()

        # Add mix of proxies
        valid_proxies = [Proxy(url=f"http://valid{i}.proxy.com:8080", ttl=3600) for i in range(5)]
        expired_proxies = [
            Proxy(url=f"http://expired{i}.proxy.com:8080", ttl=-1800) for i in range(3)
        ]

        for proxy in valid_proxies + expired_proxies:
            pool.add_proxy(proxy)

        assert pool.size == 8

        # Random selections should only pick valid proxies
        for _ in range(20):  # Multiple selections
            selected = strategy.select(pool)
            assert selected in valid_proxies
            assert selected not in expired_proxies

        # Clean up expired
        removed = pool.clear_expired()
        assert removed == 3
        assert pool.size == 5

    def test_ttl_all_proxies_expired_raises_error(self) -> None:
        """Test that strategy raises error when all proxies are expired."""
        pool = ProxyPool(name="test_pool")
        strategy = RoundRobinStrategy()

        # Add only expired proxies
        for i in range(3):
            pool.add_proxy(Proxy(url=f"http://expired{i}.proxy.com:8080", ttl=-3600))

        assert pool.size == 3

        # Should raise ProxyPoolEmptyError since all are expired
        try:
            strategy.select(pool)
            raise AssertionError("Expected ProxyPoolEmptyError")
        except ProxyPoolEmptyError as e:
            assert "No healthy proxies available" in str(e)

    def test_ttl_dynamic_expiration_during_use(self) -> None:
        """Test scenario where proxy expires during runtime."""
        pool = ProxyPool(name="test_pool")

        # Add proxy that expires very soon
        short_lived = Proxy(
            url="http://short-lived.proxy.com:8080",
            ttl=1,  # Expires in 1 second
        )
        long_lived = Proxy(
            url="http://long-lived.proxy.com:8080",
            ttl=3600,  # Expires in 1 hour
        )

        pool.add_proxy(short_lived)
        pool.add_proxy(long_lived)

        # Initially both proxies available
        assert len(pool.get_healthy_proxies()) == 2

        # After expiration, only long_lived should be available
        # Note: This test is timing-sensitive, so we explicitly set expires_at
        short_lived.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)

        healthy = pool.get_healthy_proxies()
        assert len(healthy) == 1
        assert healthy[0] == long_lived

    def test_ttl_mixed_with_unhealthy_proxies(self) -> None:
        """Test TTL filtering combined with health status filtering."""
        pool = ProxyPool(name="test_pool")
        strategy = RoundRobinStrategy()

        # Valid + healthy
        valid_healthy = Proxy(
            url="http://valid-healthy.proxy.com:8080",
            ttl=3600,
        )

        # Valid + unhealthy (should be filtered by health)
        valid_unhealthy = Proxy(
            url="http://valid-unhealthy.proxy.com:8080",
            ttl=3600,
        )
        # Mark as unhealthy by recording failures
        for _ in range(6):  # Threshold is 5 consecutive failures
            valid_unhealthy.record_failure()

        # Expired + healthy (should be filtered by TTL)
        expired_healthy = Proxy(
            url="http://expired-healthy.proxy.com:8080",
            ttl=-1800,
        )

        # Expired + unhealthy (should be filtered by both)
        expired_unhealthy = Proxy(
            url="http://expired-unhealthy.proxy.com:8080",
            ttl=-1800,
        )
        for _ in range(6):
            expired_unhealthy.record_failure()

        pool.add_proxy(valid_healthy)
        pool.add_proxy(valid_unhealthy)
        pool.add_proxy(expired_healthy)
        pool.add_proxy(expired_unhealthy)

        assert pool.size == 4

        # Only valid_healthy should be selectable
        healthy = pool.get_healthy_proxies()
        assert len(healthy) == 1
        assert healthy[0] == valid_healthy

        # Strategy should only return valid_healthy
        selected = strategy.select(pool)
        assert selected == valid_healthy

    def test_ttl_no_ttl_proxies_never_expire(self) -> None:
        """Test that proxies without TTL continue working indefinitely."""
        pool = ProxyPool(name="test_pool")
        strategy = RoundRobinStrategy()

        # Add proxies without TTL
        permanent1 = Proxy(url="http://permanent1.proxy.com:8080")
        permanent2 = Proxy(url="http://permanent2.proxy.com:8080")

        # Add proxy with TTL that expires
        temporary = Proxy(url="http://temporary.proxy.com:8080", ttl=-3600)

        pool.add_proxy(permanent1)
        pool.add_proxy(permanent2)
        pool.add_proxy(temporary)

        # Permanent proxies should still be available
        healthy = pool.get_healthy_proxies()
        assert len(healthy) == 2
        assert permanent1 in healthy
        assert permanent2 in healthy
        assert temporary not in healthy

        # Can select from permanent proxies
        selected = strategy.select(pool)
        assert selected in [permanent1, permanent2]
