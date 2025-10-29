"""Tests for TTL enforcement in ProxyPool."""

from datetime import datetime, timedelta, timezone

from proxywhirl.models import Proxy, ProxyPool


class TestProxyPoolTTL:
    """Test TTL enforcement in ProxyPool operations."""

    def test_pool_filters_expired_proxies(self) -> None:
        """Test that get_healthy_proxies excludes expired proxies."""
        pool = ProxyPool(name="test_pool")

        # Add mix of valid and expired proxies
        valid_proxy1 = Proxy(
            url="http://valid1.proxy.com:8080",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        valid_proxy2 = Proxy(
            url="http://valid2.proxy.com:8080",
            ttl=3600,  # 1 hour from now
        )
        expired_proxy1 = Proxy(
            url="http://expired1.proxy.com:8080",
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        expired_proxy2 = Proxy(
            url="http://expired2.proxy.com:8080",
            ttl=-3600,  # Expired 1 hour ago
        )
        no_ttl_proxy = Proxy(url="http://permanent.proxy.com:8080")

        pool.add_proxy(valid_proxy1)
        pool.add_proxy(valid_proxy2)
        pool.add_proxy(expired_proxy1)
        pool.add_proxy(expired_proxy2)
        pool.add_proxy(no_ttl_proxy)

        # get_healthy_proxies should exclude expired ones
        healthy = pool.get_healthy_proxies()

        assert len(healthy) == 3  # valid1, valid2, no_ttl
        assert valid_proxy1 in healthy
        assert valid_proxy2 in healthy
        assert no_ttl_proxy in healthy
        assert expired_proxy1 not in healthy
        assert expired_proxy2 not in healthy

    def test_clear_expired_removes_expired_proxies(self) -> None:
        """Test that clear_expired removes only expired proxies."""
        pool = ProxyPool(name="test_pool")

        valid_proxy = Proxy(
            url="http://valid.proxy.com:8080",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        expired_proxy1 = Proxy(
            url="http://expired1.proxy.com:8080",
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        expired_proxy2 = Proxy(
            url="http://expired2.proxy.com:8080",
            ttl=-1800,  # Expired 30 min ago
        )

        pool.add_proxy(valid_proxy)
        pool.add_proxy(expired_proxy1)
        pool.add_proxy(expired_proxy2)

        assert pool.size == 3

        # Clear expired proxies
        removed_count = pool.clear_expired()

        assert removed_count == 2
        assert pool.size == 1
        assert pool.proxies[0] == valid_proxy

    def test_clear_expired_no_expired_proxies(self) -> None:
        """Test clear_expired when no proxies are expired."""
        pool = ProxyPool(name="test_pool")

        proxy1 = Proxy(
            url="http://valid1.proxy.com:8080",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        proxy2 = Proxy(url="http://valid2.proxy.com:8080")  # No TTL

        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        removed_count = pool.clear_expired()

        assert removed_count == 0
        assert pool.size == 2

    def test_clear_expired_all_expired(self) -> None:
        """Test clear_expired when all proxies are expired."""
        pool = ProxyPool(name="test_pool")

        expired1 = Proxy(
            url="http://expired1.proxy.com:8080",
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        expired2 = Proxy(
            url="http://expired2.proxy.com:8080",
            ttl=-3600,
        )

        pool.add_proxy(expired1)
        pool.add_proxy(expired2)

        removed_count = pool.clear_expired()

        assert removed_count == 2
        assert pool.size == 0

    def test_expired_proxies_not_counted_in_healthy_count(self) -> None:
        """Test that expired proxies don't count as healthy."""
        pool = ProxyPool(name="test_pool")

        # Add valid healthy proxy
        valid_proxy = Proxy(
            url="http://valid.proxy.com:8080",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )

        # Add expired but marked as healthy
        expired_proxy = Proxy(
            url="http://expired.proxy.com:8080",
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )

        pool.add_proxy(valid_proxy)
        pool.add_proxy(expired_proxy)

        # healthy_count counts based on get_healthy_proxies which filters expired
        assert len(pool.get_healthy_proxies()) == 1
        assert pool.size == 2  # Total size unchanged
