"""
Unit tests for ProxyPool model.
"""

from uuid import uuid4

import pytest

from proxywhirl.models import HealthStatus, Proxy, ProxyPool, ProxySource


class TestProxyPoolBasics:
    """Test basic ProxyPool functionality."""

    def test_empty_pool_initialization(self):
        """Test creating an empty pool."""
        pool = ProxyPool(name="test-pool")
        assert pool.size == 0
        assert pool.healthy_count == 0
        assert pool.unhealthy_count == 0

    def test_pool_with_initial_proxies(self):
        """Test creating pool with initial proxies."""
        proxies = [
            Proxy(url="http://proxy1.example.com:8080"),  # type: ignore
            Proxy(url="http://proxy2.example.com:8080"),  # type: ignore
        ]
        pool = ProxyPool(name="test-pool", proxies=proxies)
        assert pool.size == 2

    def test_add_proxy(self):
        """Test adding proxy to pool."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy.example.com:8080")  # type: ignore
        pool.add_proxy(proxy)
        assert pool.size == 1

    def test_add_duplicate_proxy_ignored(self):
        """Test that adding duplicate proxy is silently ignored."""
        pool = ProxyPool(name="test-pool")
        proxy1 = Proxy(url="http://proxy.example.com:8080")  # type: ignore
        proxy2 = Proxy(url="http://proxy.example.com:8080")  # type: ignore

        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        # Should only have one proxy
        assert pool.size == 1

    def test_add_proxy_exceeds_max_pool_size_raises_error(self):
        """Test that exceeding max_pool_size raises ValueError."""
        pool = ProxyPool(name="test-pool", max_pool_size=2)
        pool.add_proxy(Proxy(url="http://proxy1.example.com:8080"))  # type: ignore
        pool.add_proxy(Proxy(url="http://proxy2.example.com:8080"))  # type: ignore

        with pytest.raises(ValueError, match="maximum capacity"):
            pool.add_proxy(Proxy(url="http://proxy3.example.com:8080"))  # type: ignore

    def test_remove_proxy(self):
        """Test removing proxy from pool."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy.example.com:8080")  # type: ignore
        pool.add_proxy(proxy)
        assert pool.size == 1

        pool.remove_proxy(proxy.id)
        assert pool.size == 0

    def test_remove_nonexistent_proxy_no_error(self):
        """Test that removing non-existent proxy doesn't raise error."""
        pool = ProxyPool(name="test-pool")
        fake_id = uuid4()
        pool.remove_proxy(fake_id)  # Should not raise
        assert pool.size == 0

    def test_get_proxy_by_id(self):
        """Test getting proxy by ID."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy.example.com:8080")  # type: ignore
        pool.add_proxy(proxy)

        found = pool.get_proxy_by_id(proxy.id)
        assert found is not None
        assert found.id == proxy.id

    def test_get_proxy_by_id_not_found(self):
        """Test getting non-existent proxy by ID returns None."""
        pool = ProxyPool(name="test-pool")
        fake_id = uuid4()
        found = pool.get_proxy_by_id(fake_id)
        assert found is None


class TestProxyPoolFiltering:
    """Test ProxyPool filtering methods."""

    def test_filter_by_tags_single_tag(self):
        """Test filtering by single tag."""
        pool = ProxyPool(name="test-pool")
        proxy1 = Proxy(url="http://proxy1.example.com:8080", tags={"fast", "us"})  # type: ignore
        proxy2 = Proxy(url="http://proxy2.example.com:8080", tags={"slow", "eu"})  # type: ignore
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        results = pool.filter_by_tags({"fast"})
        assert len(results) == 1
        assert results[0].id == proxy1.id

    def test_filter_by_tags_multiple_tags(self):
        """Test filtering by multiple tags (AND logic)."""
        pool = ProxyPool(name="test-pool")
        proxy1 = Proxy(url="http://proxy1.example.com:8080", tags={"fast", "us"})  # type: ignore
        proxy2 = Proxy(url="http://proxy2.example.com:8080", tags={"fast"})  # type: ignore
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        results = pool.filter_by_tags({"fast", "us"})
        assert len(results) == 1
        assert results[0].id == proxy1.id

    def test_filter_by_tags_no_matches(self):
        """Test filtering by tags with no matches."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy.example.com:8080", tags={"slow"})  # type: ignore
        pool.add_proxy(proxy)

        results = pool.filter_by_tags({"fast"})
        assert len(results) == 0

    def test_filter_by_source(self):
        """Test filtering by proxy source."""
        pool = ProxyPool(name="test-pool")
        proxy1 = Proxy(url="http://proxy1.example.com:8080", source=ProxySource.USER)  # type: ignore
        proxy2 = Proxy(url="http://proxy2.example.com:8080", source=ProxySource.FETCHED)  # type: ignore
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        results = pool.filter_by_source(ProxySource.USER)
        assert len(results) == 1
        assert results[0].id == proxy1.id

    def test_get_healthy_proxies(self):
        """Test getting only healthy proxies."""
        pool = ProxyPool(name="test-pool")
        proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.DEAD)  # type: ignore
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        results = pool.get_healthy_proxies()
        assert len(results) == 1
        assert results[0].id == proxy1.id

    def test_get_healthy_proxies_empty(self):
        """Test getting healthy proxies from pool with none."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.DEAD)  # type: ignore
        pool.add_proxy(proxy)

        results = pool.get_healthy_proxies()
        assert len(results) == 0


class TestProxyPoolClearUnhealthy:
    """Test ProxyPool clear_unhealthy method."""

    def test_clear_unhealthy_removes_dead_proxies(self):
        """Test that clear_unhealthy removes DEAD proxies."""
        pool = ProxyPool(name="test-pool")
        proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.DEAD)  # type: ignore
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        removed_count = pool.clear_unhealthy()
        assert removed_count == 1
        assert pool.size == 1
        assert pool.proxies[0].id == proxy1.id

    def test_clear_unhealthy_removes_unhealthy_proxies(self):
        """Test that clear_unhealthy removes UNHEALTHY proxies."""
        pool = ProxyPool(name="test-pool")
        proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.UNHEALTHY)  # type: ignore
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        removed_count = pool.clear_unhealthy()
        assert removed_count == 1
        assert pool.size == 1

    def test_clear_unhealthy_keeps_degraded_proxies(self):
        """Test that clear_unhealthy keeps DEGRADED proxies."""
        pool = ProxyPool(name="test-pool")
        proxy1 = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.DEGRADED)  # type: ignore
        proxy2 = Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.DEAD)  # type: ignore
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        removed_count = pool.clear_unhealthy()
        assert removed_count == 1
        assert pool.size == 1
        assert pool.proxies[0].health_status == HealthStatus.DEGRADED

    def test_clear_unhealthy_returns_zero_when_all_healthy(self):
        """Test that clear_unhealthy returns 0 when all proxies are healthy."""
        pool = ProxyPool(name="test-pool")
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)  # type: ignore
        pool.add_proxy(proxy)

        removed_count = pool.clear_unhealthy()
        assert removed_count == 0
        assert pool.size == 1


class TestProxyPoolStats:
    """Test ProxyPool statistics properties."""

    def test_healthy_count(self):
        """Test healthy proxy count."""
        pool = ProxyPool(name="test-pool")
        pool.add_proxy(Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY))  # type: ignore
        pool.add_proxy(Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.HEALTHY))  # type: ignore
        pool.add_proxy(Proxy(url="http://proxy3.example.com:8080", health_status=HealthStatus.DEAD))  # type: ignore

        assert pool.healthy_count == 2

    def test_unhealthy_count(self):
        """Test unhealthy proxy count."""
        pool = ProxyPool(name="test-pool")
        pool.add_proxy(Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY))  # type: ignore
        pool.add_proxy(Proxy(url="http://proxy2.example.com:8080", health_status=HealthStatus.DEAD))  # type: ignore
        pool.add_proxy(Proxy(url="http://proxy3.example.com:8080", health_status=HealthStatus.DEGRADED))  # type: ignore

        assert pool.unhealthy_count == 2

    def test_total_requests(self):
        """Test total requests across all proxies."""
        pool = ProxyPool(name="test-pool")
        proxy1 = Proxy(url="http://proxy1.example.com:8080")  # type: ignore
        proxy2 = Proxy(url="http://proxy2.example.com:8080")  # type: ignore
        proxy1.record_success(100.0)
        proxy1.record_success(100.0)
        proxy2.record_success(100.0)

        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        assert pool.total_requests == 3

    def test_overall_success_rate(self):
        """Test overall success rate calculation."""
        pool = ProxyPool(name="test-pool")
        proxy1 = Proxy(url="http://proxy1.example.com:8080")  # type: ignore
        proxy2 = Proxy(url="http://proxy2.example.com:8080")  # type: ignore

        # proxy1: 2 successes, 0 failures
        proxy1.record_success(100.0)
        proxy1.record_success(100.0)

        # proxy2: 1 success, 1 failure
        proxy2.record_success(100.0)
        proxy2.record_failure()

        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        # 3 successes / 4 total = 0.75
        assert pool.overall_success_rate == 0.75

    def test_overall_success_rate_empty_pool(self):
        """Test overall success rate for empty pool."""
        pool = ProxyPool(name="test-pool")
        assert pool.overall_success_rate == 0.0
