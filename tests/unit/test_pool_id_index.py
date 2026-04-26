"""
Unit tests for ProxyPool ID index functionality (PERF-002).

Tests the O(1) ID lookup index to ensure:
1. Index is built correctly during initialization
2. Index stays in sync with proxies list during mutations
3. get_proxy_by_id uses O(1) lookup
"""

from proxywhirl.models import HealthStatus, Proxy, ProxyPool


class TestProxyPoolIDIndex:
    """Test ProxyPool O(1) ID index functionality."""

    def test_index_initialized_with_initial_proxies(self):
        """Test that ID index is built from initial proxies."""
        proxies = [
            Proxy(url="http://proxy1.example.com:8080"),  # type: ignore
            Proxy(url="http://proxy2.example.com:8080"),  # type: ignore
            Proxy(url="http://proxy3.example.com:8080"),  # type: ignore
        ]
        pool = ProxyPool(name="test-pool", proxies=proxies)

        # Index should contain all proxies
        assert len(pool._id_index) == 3
        for proxy in proxies:
            assert proxy.id in pool._id_index
            assert pool._id_index[proxy.id] is proxy

    def test_index_empty_for_empty_pool(self):
        """Test that empty pool has empty index."""
        pool = ProxyPool(name="test-pool")
        assert len(pool._id_index) == 0

    def test_index_updated_on_add_proxy(self):
        """Test that index is updated when adding a proxy."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy.example.com:8080")  # type: ignore

        pool.add_proxy(proxy)

        # Index should contain the new proxy
        assert proxy.id in pool._id_index
        assert pool._id_index[proxy.id] is proxy
        assert len(pool._id_index) == 1

    def test_index_updated_on_remove_proxy(self):
        """Test that index is updated when removing a proxy."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy.example.com:8080")  # type: ignore
        pool.add_proxy(proxy)

        assert proxy.id in pool._id_index

        pool.remove_proxy(proxy.id)

        # Index should no longer contain the proxy
        assert proxy.id not in pool._id_index
        assert len(pool._id_index) == 0

    def test_index_rebuilt_on_clear_unhealthy(self):
        """Test that index is rebuilt when clearing unhealthy proxies."""
        pool = ProxyPool(name="test-pool")
        healthy = Proxy(url="http://healthy.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        dead = Proxy(url="http://dead.example.com:8080", health_status=HealthStatus.DEAD)  # type: ignore

        pool.add_proxy(healthy)
        pool.add_proxy(dead)

        assert len(pool._id_index) == 2
        assert healthy.id in pool._id_index
        assert dead.id in pool._id_index

        pool.clear_unhealthy()

        # Index should only contain healthy proxy
        assert len(pool._id_index) == 1
        assert healthy.id in pool._id_index
        assert dead.id not in pool._id_index

    def test_index_rebuilt_on_clear_expired(self):
        """Test that index is rebuilt when clearing expired proxies."""
        from datetime import datetime, timedelta, timezone

        pool = ProxyPool(name="test-pool")
        # Create proxy with expiration in the past
        expired = Proxy(
            url="http://expired.example.com:8080",
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )  # type: ignore
        valid = Proxy(url="http://valid.example.com:8080")  # type: ignore

        pool.add_proxy(expired)
        pool.add_proxy(valid)

        assert len(pool._id_index) == 2

        pool.clear_expired()

        # Index should only contain valid proxy
        assert len(pool._id_index) == 1
        assert valid.id in pool._id_index
        assert expired.id not in pool._id_index

    def test_get_proxy_by_id_uses_index(self):
        """Test that get_proxy_by_id returns proxy from index."""
        pool = ProxyPool(name="test-pool")
        proxy1 = Proxy(url="http://proxy1.example.com:8080")  # type: ignore
        proxy2 = Proxy(url="http://proxy2.example.com:8080")  # type: ignore

        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        # Should find proxies by ID
        found1 = pool.get_proxy_by_id(proxy1.id)
        found2 = pool.get_proxy_by_id(proxy2.id)

        assert found1 is proxy1
        assert found2 is proxy2

    def test_get_proxy_by_id_returns_none_when_not_found(self):
        """Test that get_proxy_by_id returns None for missing ID."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy.example.com:8080")  # type: ignore

        result = pool.get_proxy_by_id(proxy.id)
        assert result is None

    def test_index_sync_after_multiple_operations(self):
        """Test that index stays in sync after multiple add/remove operations."""
        pool = ProxyPool(name="test-pool")

        # Add multiple proxies
        proxies = []
        for i in range(10):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")  # type: ignore
            pool.add_proxy(proxy)
            proxies.append(proxy)

        assert len(pool._id_index) == 10

        # Remove half of them
        for i in range(0, 10, 2):
            pool.remove_proxy(proxies[i].id)

        assert len(pool._id_index) == 5

        # Verify remaining proxies are in index
        for i in range(1, 10, 2):
            assert proxies[i].id in pool._id_index
            assert pool._id_index[proxies[i].id] is proxies[i]

        # Verify removed proxies are not in index
        for i in range(0, 10, 2):
            assert proxies[i].id not in pool._id_index

    def test_index_handles_duplicate_urls_correctly(self):
        """Test that index handles duplicate URL additions correctly."""
        pool = ProxyPool(name="test-pool")
        proxy1 = Proxy(url="http://proxy.example.com:8080")  # type: ignore
        proxy2 = Proxy(url="http://proxy.example.com:8080")  # type: ignore

        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)  # Should be ignored as duplicate URL

        # Index should only contain first proxy
        assert len(pool._id_index) == 1
        assert proxy1.id in pool._id_index
        assert proxy2.id not in pool._id_index

    def test_index_integrity_with_bulk_operations(self):
        """Test index integrity after bulk clear operations."""
        pool = ProxyPool(name="test-pool")

        # Add mix of healthy and unhealthy proxies
        healthy_proxies = []
        unhealthy_proxies = []

        for i in range(5):
            healthy = Proxy(
                url=f"http://healthy{i}.example.com:8080", health_status=HealthStatus.HEALTHY
            )  # type: ignore
            unhealthy = Proxy(
                url=f"http://unhealthy{i}.example.com:8080", health_status=HealthStatus.DEAD
            )  # type: ignore
            pool.add_proxy(healthy)
            pool.add_proxy(unhealthy)
            healthy_proxies.append(healthy)
            unhealthy_proxies.append(unhealthy)

        assert len(pool._id_index) == 10

        # Clear unhealthy
        pool.clear_unhealthy()

        # Verify index only contains healthy proxies
        assert len(pool._id_index) == 5
        for proxy in healthy_proxies:
            assert proxy.id in pool._id_index
            assert pool._id_index[proxy.id] is proxy
        for proxy in unhealthy_proxies:
            assert proxy.id not in pool._id_index

        # Verify list and index are in sync
        assert len(pool.proxies) == len(pool._id_index)
        for proxy in pool.proxies:
            assert proxy.id in pool._id_index
            assert pool._id_index[proxy.id] is proxy
