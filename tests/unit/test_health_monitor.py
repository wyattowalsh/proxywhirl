"""Unit tests for HealthMonitor continuous health checking."""

from unittest.mock import AsyncMock

import pytest

from proxywhirl.models import HealthMonitor, Proxy, ProxyPool


class TestHealthMonitorInit:
    """Test HealthMonitor initialization."""

    def test_monitor_init_with_defaults(self) -> None:
        """HealthMonitor initializes with default configuration."""
        pool = ProxyPool(name="test_pool")
        monitor = HealthMonitor(pool=pool)

        assert monitor.pool == pool
        assert monitor.check_interval == 60  # 60 seconds default
        assert monitor.failure_threshold == 3  # 3 consecutive failures default
        assert monitor.is_running is False
        assert monitor._task is None
        assert monitor._failure_counts == {}

    def test_monitor_init_with_custom_config(self) -> None:
        """HealthMonitor accepts custom interval and threshold."""
        pool = ProxyPool(name="test_pool")
        monitor = HealthMonitor(
            pool=pool,
            check_interval=30,  # Check every 30 seconds
            failure_threshold=5,  # Evict after 5 failures
        )

        assert monitor.pool == pool
        assert monitor.check_interval == 30
        assert monitor.failure_threshold == 5
        assert monitor.is_running is False

    def test_monitor_init_validates_interval(self) -> None:
        """HealthMonitor rejects invalid check intervals."""
        pool = ProxyPool(name="test_pool")

        with pytest.raises(ValueError, match="check_interval must be positive"):
            HealthMonitor(pool=pool, check_interval=0)

        with pytest.raises(ValueError, match="check_interval must be positive"):
            HealthMonitor(pool=pool, check_interval=-10)

    def test_monitor_init_validates_threshold(self) -> None:
        """HealthMonitor rejects invalid failure thresholds."""
        pool = ProxyPool(name="test_pool")

        with pytest.raises(ValueError, match="failure_threshold must be positive"):
            HealthMonitor(pool=pool, failure_threshold=0)

        with pytest.raises(ValueError, match="failure_threshold must be positive"):
            HealthMonitor(pool=pool, failure_threshold=-5)


class TestHealthMonitorScheduler:
    """Test background task scheduling."""

    async def test_monitor_start_schedules_task(self) -> None:
        """start() creates background task and sets is_running."""
        pool = ProxyPool(name="test_pool")
        pool.add_proxy(Proxy(url="http://proxy1.com:8080"))
        monitor = HealthMonitor(pool=pool, check_interval=10)

        # Mock the _check_health_loop to avoid actual running
        monitor._check_health_loop = AsyncMock()  # type: ignore

        await monitor.start()

        assert monitor.is_running is True
        assert monitor._task is not None
        assert not monitor._task.done()

        # Cleanup
        await monitor.stop()

    async def test_monitor_stop_cancels_task(self) -> None:
        """stop() cancels background task and sets is_running to False."""
        pool = ProxyPool(name="test_pool")
        pool.add_proxy(Proxy(url="http://proxy1.com:8080"))
        monitor = HealthMonitor(pool=pool, check_interval=10)
        monitor._check_health_loop = AsyncMock()  # type: ignore

        await monitor.start()
        assert monitor.is_running is True

        await monitor.stop()

        assert monitor.is_running is False
        assert monitor._task is None or monitor._task.cancelled()

    async def test_monitor_checks_run_periodically(self) -> None:
        """Health checks run periodically at configured interval."""
        pool = ProxyPool(name="test_pool")
        pool.add_proxy(Proxy(url="http://proxy1.com:8080"))
        monitor = HealthMonitor(pool=pool, check_interval=1)  # 1 second for testing

        check_count = 0

        async def mock_check() -> None:
            nonlocal check_count
            check_count += 1

        monitor._run_health_checks = AsyncMock(side_effect=mock_check)  # type: ignore

        await monitor.start()

        # Wait for at least 2 checks (2+ seconds)
        import asyncio

        await asyncio.sleep(2.5)

        await monitor.stop()

        # Should have run at least 2 checks
        assert check_count >= 2

    async def test_monitor_start_idempotent(self) -> None:
        """Calling start() twice doesn't create multiple tasks."""
        pool = ProxyPool(name="test_pool")
        pool.add_proxy(Proxy(url="http://proxy1.com:8080"))
        monitor = HealthMonitor(pool=pool, check_interval=10)
        monitor._check_health_loop = AsyncMock()  # type: ignore

        await monitor.start()
        first_task = monitor._task

        await monitor.start()  # Second call
        second_task = monitor._task

        # Should be the same task
        assert first_task == second_task

        await monitor.stop()

    async def test_monitor_stop_idempotent(self) -> None:
        """Calling stop() when not running is safe."""
        pool = ProxyPool(name="test_pool")
        monitor = HealthMonitor(pool=pool)

        # Stop without starting - should not raise
        await monitor.stop()

        assert monitor.is_running is False


class TestHealthMonitorFailureTracking:
    """Test failure tracking and auto-eviction."""

    async def test_monitor_tracks_consecutive_failures(self) -> None:
        """Monitor tracks consecutive failures per proxy."""
        pool = ProxyPool(name="test_pool")
        proxy1 = Proxy(url="http://proxy1.com:8080")
        proxy2 = Proxy(url="http://proxy2.com:8080")
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        monitor = HealthMonitor(pool=pool, failure_threshold=3)

        # Manually record failures
        monitor._record_failure(proxy1)
        assert monitor._failure_counts[proxy1.url] == 1

        monitor._record_failure(proxy1)
        assert monitor._failure_counts[proxy1.url] == 2

        # Different proxy
        monitor._record_failure(proxy2)
        assert monitor._failure_counts[proxy2.url] == 1

    async def test_monitor_evicts_after_threshold(self) -> None:
        """Proxy is evicted after reaching failure threshold."""
        pool = ProxyPool(name="test_pool")
        proxy = Proxy(url="http://dead-proxy.com:8080")
        pool.add_proxy(proxy)

        monitor = HealthMonitor(pool=pool, failure_threshold=3)

        # Record failures up to threshold
        monitor._record_failure(proxy)
        monitor._record_failure(proxy)
        assert pool.size == 1  # Still in pool

        monitor._record_failure(proxy)  # Reaches threshold
        assert pool.size == 0  # Evicted

    async def test_monitor_resets_failures_on_success(self) -> None:
        """Successful health check resets failure count."""
        pool = ProxyPool(name="test_pool")
        proxy = Proxy(url="http://proxy.com:8080")
        pool.add_proxy(proxy)

        monitor = HealthMonitor(pool=pool, failure_threshold=5)

        # Record some failures
        monitor._record_failure(proxy)
        monitor._record_failure(proxy)
        assert monitor._failure_counts[proxy.url] == 2

        # Successful check resets
        monitor._record_success(proxy)
        assert monitor._failure_counts.get(proxy.url, 0) == 0

    async def test_monitor_eviction_updates_pool(self) -> None:
        """Evicted proxies are removed from pool."""
        pool = ProxyPool(name="test_pool")
        proxy1 = Proxy(url="http://proxy1.com:8080")
        proxy2 = Proxy(url="http://proxy2.com:8080")
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        monitor = HealthMonitor(pool=pool, failure_threshold=2)

        # Evict proxy1
        monitor._record_failure(proxy1)
        monitor._record_failure(proxy1)

        assert pool.size == 1
        assert proxy1.url not in [p.url for p in pool.proxies]
        assert proxy2.url in [p.url for p in pool.proxies]


class TestHealthMonitorStatus:
    """Test status monitoring API."""

    def test_monitor_get_status(self) -> None:
        """get_status() returns current monitoring state."""
        pool = ProxyPool(name="test_pool")
        proxy1 = Proxy(url="http://proxy1.com:8080")
        proxy2 = Proxy(url="http://proxy2.com:8080")
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        monitor = HealthMonitor(pool=pool, check_interval=30, failure_threshold=5)

        # Record some failures
        monitor._record_failure(proxy1)
        monitor._record_failure(proxy1)

        status = monitor.get_status()

        assert status["is_running"] is False
        assert status["check_interval"] == 30
        assert status["failure_threshold"] == 5
        assert status["total_proxies"] == 2
        assert status["healthy_proxies"] == 2
        assert len(status["failure_counts"]) == 1
        assert status["failure_counts"][proxy1.url] == 2

    async def test_monitor_status_includes_runtime(self) -> None:
        """Status includes uptime when monitor is running."""
        pool = ProxyPool(name="test_pool")
        pool.add_proxy(Proxy(url="http://proxy.com:8080"))
        monitor = HealthMonitor(pool=pool, check_interval=60)
        monitor._check_health_loop = AsyncMock()  # type: ignore

        await monitor.start()

        import asyncio

        await asyncio.sleep(0.1)  # Brief delay

        status = monitor.get_status()

        assert status["is_running"] is True
        assert "uptime_seconds" in status
        assert status["uptime_seconds"] >= 0

        await monitor.stop()
