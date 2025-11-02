"""Tests for real-time pool status tracking (US3)."""

import pytest

from proxywhirl.health import HealthChecker
from proxywhirl.health_models import HealthCheckConfig, HealthStatus


class TestPoolStatus:
    """Tests for PoolStatus model and computed properties (T044)."""

    def test_pool_status_health_percentage(self) -> None:
        """Test PoolStatus health_percentage property."""
        from proxywhirl.health_models import PoolStatus

        # 8 out of 10 healthy = 80%
        status = PoolStatus(total_proxies=10, healthy_proxies=8, unhealthy_proxies=2)
        assert status.health_percentage == 80.0

        # Empty pool = 0%
        empty_status = PoolStatus(total_proxies=0)
        assert empty_status.health_percentage == 0.0

    def test_pool_status_is_degraded(self) -> None:
        """Test PoolStatus is_degraded property."""
        from proxywhirl.health_models import PoolStatus

        # Less than 50% = degraded
        degraded = PoolStatus(total_proxies=10, healthy_proxies=4, unhealthy_proxies=6)
        assert degraded.is_degraded is True

        # 50% or more = not degraded
        healthy = PoolStatus(total_proxies=10, healthy_proxies=5, unhealthy_proxies=5)
        assert healthy.is_degraded is False

        very_healthy = PoolStatus(total_proxies=10, healthy_proxies=9, unhealthy_proxies=1)
        assert very_healthy.is_degraded is False


class TestSourceStatus:
    """Tests for SourceStatus model (T045)."""

    def test_source_status_health_percentage(self) -> None:
        """Test SourceStatus health_percentage property."""
        from proxywhirl.health_models import SourceStatus

        status = SourceStatus(
            source_name="premium", total_proxies=20, healthy_proxies=18
        )
        assert status.health_percentage == 90.0

        # Empty source
        empty = SourceStatus(source_name="empty", total_proxies=0)
        assert empty.health_percentage == 0.0


class TestHealthCheckerPoolStatus:
    """Tests for HealthChecker.get_pool_status() (T046)."""

    def test_get_pool_status_accurate_counts(self) -> None:
        """Test that get_pool_status returns accurate counts."""
        checker = HealthChecker()

        # Add proxies with different statuses
        checker.add_proxy("http://proxy1.example.com:8080", source="premium")
        checker.add_proxy("http://proxy2.example.com:8080", source="premium")
        checker.add_proxy("http://proxy3.example.com:8080", source="free")

        # Set some statuses manually
        checker._proxies["http://proxy1.example.com:8080"][
            "health_status"
        ] = HealthStatus.HEALTHY
        checker._proxies["http://proxy2.example.com:8080"][
            "health_status"
        ] = HealthStatus.UNHEALTHY
        checker._proxies["http://proxy3.example.com:8080"][
            "health_status"
        ] = HealthStatus.UNKNOWN

        status = checker.get_pool_status()

        assert status.total_proxies == 3
        assert status.healthy_proxies == 1
        assert status.unhealthy_proxies == 1
        assert status.unknown_proxies == 1

    def test_get_pool_status_by_source_breakdown(self) -> None:
        """Test that get_pool_status includes by_source breakdown."""
        checker = HealthChecker()

        checker.add_proxy("http://proxy1.example.com:8080", source="premium")
        checker.add_proxy("http://proxy2.example.com:8080", source="premium")
        checker.add_proxy("http://proxy3.example.com:8080", source="free")

        checker._proxies["http://proxy1.example.com:8080"][
            "health_status"
        ] = HealthStatus.HEALTHY
        checker._proxies["http://proxy2.example.com:8080"][
            "health_status"
        ] = HealthStatus.HEALTHY
        checker._proxies["http://proxy3.example.com:8080"][
            "health_status"
        ] = HealthStatus.UNHEALTHY

        status = checker.get_pool_status()

        assert "premium" in status.by_source
        assert "free" in status.by_source
        assert status.by_source["premium"].total_proxies == 2
        assert status.by_source["premium"].healthy_proxies == 2
        assert status.by_source["free"].total_proxies == 1
        assert status.by_source["free"].unhealthy_proxies == 1

    def test_get_pool_status_empty_pool(self) -> None:
        """Test get_pool_status with empty pool."""
        checker = HealthChecker()
        status = checker.get_pool_status()

        assert status.total_proxies == 0
        assert status.healthy_proxies == 0
        assert status.health_percentage == 0.0


class TestHealthCheckerProxyStatus:
    """Tests for HealthChecker.get_proxy_status() (T047)."""

    def test_get_proxy_status_returns_state(self) -> None:
        """Test that get_proxy_status returns ProxyHealthState."""
        checker = HealthChecker()
        checker.add_proxy("http://proxy1.example.com:8080", source="test")

        status = checker.get_proxy_status("http://proxy1.example.com:8080")

        assert status is not None
        assert status.proxy_url == "http://proxy1.example.com:8080"
        assert status.health_status == HealthStatus.UNKNOWN
        assert status.consecutive_failures == 0

    def test_get_proxy_status_returns_none_for_unknown(self) -> None:
        """Test that get_proxy_status returns None for unregistered proxy."""
        checker = HealthChecker()
        status = checker.get_proxy_status("http://unknown.example.com:8080")
        assert status is None
