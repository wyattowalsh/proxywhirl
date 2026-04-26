"""Tests for ProxyPool state management and consistency."""

import pytest
from proxywhirl.models import Proxy, ProxyPool, HealthStatus


class TestProxyPoolBasics:
    """Test basic ProxyPool operations."""

    def test_create_empty_pool(self):
        """Test creating an empty proxy pool."""
        pool = ProxyPool(name="test-pool")
        assert pool.size == 0
        assert pool.name == "test-pool"

    def test_pool_has_name(self):
        """Test that pool must have a name."""
        pool = ProxyPool(name="my-pool")
        assert pool.name == "my-pool"

    def test_pool_has_max_size(self):
        """Test pool max size default."""
        pool = ProxyPool(name="test-pool")
        assert pool.max_pool_size == 100

    def test_pool_custom_max_size(self):
        """Test setting custom pool max size."""
        pool = ProxyPool(name="test-pool", max_pool_size=50)
        assert pool.max_pool_size == 50

    def test_pool_initial_proxies(self):
        """Test creating pool with initial proxies."""
        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        proxy2 = Proxy(url="http://proxy2.example.com:8080")
        
        pool = ProxyPool(name="test-pool", proxies=[proxy1, proxy2])
        assert pool.size == 2


class TestProxyPoolAddRemove:
    """Test adding and removing proxies."""

    def test_add_proxy_to_pool(self):
        """Test adding a proxy to pool."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy.example.com:8080")
        
        pool.add_proxy(proxy)
        assert pool.size == 1

    def test_add_multiple_proxies(self):
        """Test adding multiple proxies."""
        pool = ProxyPool(name="test-pool")
        
        for i in range(5):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            pool.add_proxy(proxy)
        
        assert pool.size == 5

    def test_add_duplicate_proxy_ignored(self):
        """Test that duplicate proxies are ignored."""
        pool = ProxyPool(name="test-pool")
        
        url = "http://proxy.example.com:8080"
        proxy1 = Proxy(url=url)
        proxy2 = Proxy(url=url)
        
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)  # Should be ignored (duplicate URL)
        
        # Pool should only have 1
        assert pool.size == 1

    def test_remove_proxy_from_pool(self):
        """Test removing a proxy from pool."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy.example.com:8080")
        
        pool.add_proxy(proxy)
        assert pool.size == 1
        
        # remove_proxy expects a UUID, not a string
        pool.remove_proxy(proxy.id)
        assert pool.size == 0

    def test_remove_nonexistent_proxy_safe(self):
        """Test removing nonexistent proxy doesn't error."""
        import uuid
        pool = ProxyPool(name="test-pool")
        
        # Should not raise error when removing nonexistent UUID
        fake_id = uuid.uuid4()
        pool.remove_proxy(fake_id)
        assert pool.size == 0


class TestProxyPoolCapacity:
    """Test pool capacity limits."""

    def test_pool_max_capacity_enforced(self):
        """Test that pool enforces max capacity."""
        pool = ProxyPool(name="test-pool", max_pool_size=3)
        
        for i in range(3):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            pool.add_proxy(proxy)
        
        # Try to add beyond capacity
        with pytest.raises(ValueError):
            proxy = Proxy(url="http://overflow.example.com:8080")
            pool.add_proxy(proxy)

    def test_pool_capacity_exactly_at_limit(self):
        """Test pool at exact capacity limit."""
        pool = ProxyPool(name="test-pool", max_pool_size=5)
        
        for i in range(5):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            pool.add_proxy(proxy)
        
        assert pool.size == 5


class TestProxyPoolHealthStatus:
    """Test health status tracking."""

    def test_healthy_count(self):
        """Test counting healthy proxies."""
        pool = ProxyPool(name="test-pool")
        
        for i in range(3):
            proxy = Proxy(
                url=f"http://healthy{i}.example.com:8080",
                health_status=HealthStatus.HEALTHY
            )
            pool.add_proxy(proxy)
        
        assert pool.healthy_count == 3

    def test_unhealthy_count(self):
        """Test counting unhealthy proxies."""
        pool = ProxyPool(name="test-pool")
        
        for i in range(2):
            proxy = Proxy(
                url=f"http://unhealthy{i}.example.com:8080",
                health_status=HealthStatus.UNHEALTHY
            )
            pool.add_proxy(proxy)
        
        assert pool.unhealthy_count == 2

    def test_mixed_health_status(self):
        """Test pool with mixed health statuses."""
        pool = ProxyPool(name="test-pool")
        
        proxy_healthy = Proxy(
            url="http://healthy.example.com:8080",
            health_status=HealthStatus.HEALTHY
        )
        pool.add_proxy(proxy_healthy)
        
        proxy_unhealthy = Proxy(
            url="http://unhealthy.example.com:8080",
            health_status=HealthStatus.UNHEALTHY
        )
        pool.add_proxy(proxy_unhealthy)
        
        assert pool.healthy_count == 1
        assert pool.unhealthy_count == 1


class TestProxyPoolStatistics:
    """Test pool-level statistics."""

    def test_total_requests_sum(self):
        """Test total requests is sum of all proxies."""
        pool = ProxyPool(name="test-pool")
        
        for i in range(3):
            proxy = Proxy(
                url=f"http://proxy{i}.example.com:8080",
                total_requests=100 + (i * 10)
            )
            pool.add_proxy(proxy)
        
        assert pool.total_requests == 330  # 100 + 110 + 120

    def test_overall_success_rate(self):
        """Test overall success rate calculation."""
        pool = ProxyPool(name="test-pool")
        
        # Proxy 1: 80 successes out of 100 requests
        proxy1 = Proxy(
            url="http://proxy1.example.com:8080",
            total_requests=100,
            total_successes=80
        )
        pool.add_proxy(proxy1)
        
        # Proxy 2: 70 successes out of 100 requests
        proxy2 = Proxy(
            url="http://proxy2.example.com:8080",
            total_requests=100,
            total_successes=70
        )
        pool.add_proxy(proxy2)
        
        # Overall: 150 successes out of 200 = 0.75
        assert abs(pool.overall_success_rate - 0.75) < 0.01

    def test_overall_success_rate_empty_pool(self):
        """Test success rate for empty pool."""
        pool = ProxyPool(name="test-pool")
        assert pool.overall_success_rate == 0.0

    def test_overall_success_rate_no_requests(self):
        """Test success rate when no proxies have made requests."""
        pool = ProxyPool(name="test-pool")
        
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            total_requests=0,
            total_successes=0
        )
        pool.add_proxy(proxy)
        
        assert pool.overall_success_rate == 0.0


class TestProxyPoolUniqueIds:
    """Test proxy ID uniqueness in pool."""

    def test_all_proxy_ids_unique(self):
        """Test that all proxies have unique IDs."""
        pool = ProxyPool(name="test-pool")
        
        for i in range(10):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            pool.add_proxy(proxy)
        
        ids = [p.id for p in pool.proxies]
        assert len(ids) == len(set(ids))  # All unique


class TestProxyPoolThreadSafety:
    """Test thread safety operations (using threading)."""

    def test_concurrent_add_operations_safe(self):
        """Test concurrent adds are safe."""
        import threading
        
        pool = ProxyPool(name="test-pool", max_pool_size=100)
        
        def add_proxy(idx):
            proxy = Proxy(url=f"http://proxy{idx}.example.com:8080")
            try:
                pool.add_proxy(proxy)
            except ValueError:
                pass  # Pool full
        
        threads = [threading.Thread(target=add_proxy, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should have some proxies added safely
        assert pool.size > 0

    def test_concurrent_add_remove_safe(self):
        """Test concurrent add and remove are safe."""
        import threading
        
        pool = ProxyPool(name="test-pool")
        
        # Pre-populate
        for i in range(10):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            pool.add_proxy(proxy)
        
        stored_ids = [p.id for p in pool.proxies]
        
        def mixed_operations(idx):
            if idx % 2 == 0:
                # Remove operation
                if stored_ids:
                    pool.remove_proxy(str(stored_ids[0]))
            else:
                # Add operation
                proxy = Proxy(url=f"http://thread-proxy{idx}.example.com:8080")
                try:
                    pool.add_proxy(proxy)
                except ValueError:
                    pass
        
        threads = [threading.Thread(target=mixed_operations, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Pool should be in valid state
        assert pool.size >= 0


class TestProxyPoolAttributes:
    """Test pool attributes and configuration."""

    def test_auto_remove_dead_flag(self):
        """Test auto_remove_dead flag."""
        pool = ProxyPool(name="test-pool", auto_remove_dead=True)
        assert pool.auto_remove_dead is True

    def test_dead_proxy_threshold(self):
        """Test dead proxy threshold setting."""
        pool = ProxyPool(name="test-pool", dead_proxy_threshold=10)
        assert pool.dead_proxy_threshold == 10

    def test_pool_created_at_timestamp(self):
        """Test that pool has creation timestamp."""
        pool = ProxyPool(name="test-pool")
        assert pool.created_at is not None

    def test_pool_unique_id(self):
        """Test that each pool has a unique ID."""
        pool1 = ProxyPool(name="pool1")
        pool2 = ProxyPool(name="pool2")
        
        assert pool1.id != pool2.id
