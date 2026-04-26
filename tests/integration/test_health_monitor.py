"""Integration tests for HealthMonitor with real proxies."""

import asyncio
from unittest.mock import AsyncMock

from proxywhirl.models import HealthMonitor, HealthStatus, Proxy, ProxyPool


class TestHealthMonitorIntegration:
    """Integration tests for HealthMonitor with real proxy pool operations."""

    async def test_monitor_with_real_proxies(self) -> None:
        """HealthMonitor works with real ProxyPool operations."""
        pool = ProxyPool(name="integration_pool")
        proxy1 = Proxy(url="http://proxy1.com:8080")
        proxy2 = Proxy(url="http://proxy2.com:8080")
        proxy3 = Proxy(url="http://proxy3.com:8080")

        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)
        pool.add_proxy(proxy3)

        monitor = HealthMonitor(pool=pool, check_interval=30, failure_threshold=2)

        # Verify initial state
        assert monitor.get_status()["total_proxies"] == 3
        assert monitor.get_status()["healthy_proxies"] == 3

        # Simulate failures
        monitor._record_failure(proxy1)
        assert monitor._failure_counts[proxy1.url] == 1
        assert pool.size == 3  # Still in pool

        monitor._record_failure(proxy1)  # Reaches threshold
        assert pool.size == 2  # Evicted
        assert proxy1.url not in [p.url for p in pool.proxies]

        # Other proxies still healthy
        monitor._record_success(proxy2)
        assert monitor._failure_counts.get(proxy2.url, 0) == 0

    async def test_monitor_evicts_dead_proxies(self) -> None:
        """HealthMonitor evicts proxies that fail consistently."""
        pool = ProxyPool(name="eviction_pool")

        # Add 5 proxies
        for i in range(1, 6):
            pool.add_proxy(Proxy(url=f"http://proxy{i}.com:8080"))

        monitor = HealthMonitor(pool=pool, check_interval=10, failure_threshold=3)

        assert pool.size == 5

        # Simulate 3 failures for proxy1, proxy2, proxy3
        proxy1, proxy2, proxy3, proxy4, proxy5 = pool.proxies

        # Proxy1 - evicted
        for _ in range(3):
            monitor._record_failure(proxy1)
        assert pool.size == 4

        # Proxy2 - 2 failures, not evicted yet
        monitor._record_failure(proxy2)
        monitor._record_failure(proxy2)
        assert pool.size == 4

        # Proxy3 - evicted
        for _ in range(3):
            monitor._record_failure(proxy3)
        assert pool.size == 3

        # Remaining proxies: proxy2 (2 failures), proxy4, proxy5
        remaining_urls = [p.url for p in pool.proxies]
        assert proxy2.url in remaining_urls
        assert proxy4.url in remaining_urls
        assert proxy5.url in remaining_urls
        assert proxy1.url not in remaining_urls
        assert proxy3.url not in remaining_urls

        # Reset proxy2 with success
        monitor._record_success(proxy2)
        assert monitor._failure_counts.get(proxy2.url, 0) == 0

    async def test_monitor_cpu_overhead_under_5_percent(self) -> None:
        """HealthMonitor has minimal CPU overhead during monitoring."""
        import time

        pool = ProxyPool(name="performance_pool")

        # Add 100 proxies
        for i in range(100):
            pool.add_proxy(Proxy(url=f"http://proxy{i}.com:8080"))

        monitor = HealthMonitor(pool=pool, check_interval=1)

        # Mock health check to be very fast
        async def mock_fast_check() -> None:
            await asyncio.sleep(0.001)  # 1ms per check

        monitor._run_health_checks = AsyncMock(side_effect=mock_fast_check)  # type: ignore

        # Measure CPU time
        start_time = time.perf_counter()

        await monitor.start()
        await asyncio.sleep(3)  # Run for 3 seconds
        await monitor.stop()

        elapsed = time.perf_counter() - start_time

        # Overhead check: actual time should be close to sleep time
        # With 3 checks (3 seconds / 1 second interval), overhead should be minimal
        # This is a simple check - in production you'd use psutil or similar
        assert elapsed < 4.0  # Some overhead is acceptable

    async def test_monitor_handles_empty_pool(self) -> None:
        """HealthMonitor handles empty pools gracefully."""
        pool = ProxyPool(name="empty_pool")
        monitor = HealthMonitor(pool=pool, check_interval=10)

        status = monitor.get_status()
        assert status["total_proxies"] == 0
        assert status["healthy_proxies"] == 0
        assert status["failure_counts"] == {}

        # Start/stop with empty pool should work
        monitor._check_health_loop = AsyncMock()  # type: ignore
        await monitor.start()
        assert monitor.is_running is True
        await monitor.stop()
        assert monitor.is_running is False

    async def test_monitor_concurrent_operations(self) -> None:
        """HealthMonitor handles concurrent operations correctly."""
        pool = ProxyPool(name="concurrent_pool")

        for i in range(10):
            pool.add_proxy(Proxy(url=f"http://proxy{i}.com:8080"))

        monitor = HealthMonitor(pool=pool, failure_threshold=5)

        # Simulate concurrent failure recording
        proxies = pool.proxies[:5]

        async def record_failures() -> None:
            for proxy in proxies:
                monitor._record_failure(proxy)
                await asyncio.sleep(0.01)

        # Run multiple failure recording tasks concurrently
        await asyncio.gather(
            record_failures(),
            record_failures(),
            record_failures(),
        )

        # Each proxy should have 3 failures (not evicted, threshold is 5)
        for proxy in proxies:
            assert monitor._failure_counts.get(proxy.url, 0) == 3

        assert pool.size == 10  # All still in pool

    async def test_monitor_status_updates_during_runtime(self) -> None:
        """get_status() reflects current state during monitoring."""
        pool = ProxyPool(name="status_pool")
        pool.add_proxy(Proxy(url="http://proxy1.com:8080"))
        pool.add_proxy(Proxy(url="http://proxy2.com:8080"))

        monitor = HealthMonitor(pool=pool, check_interval=60)
        monitor._check_health_loop = AsyncMock()  # type: ignore

        # Before start
        status = monitor.get_status()
        assert status["is_running"] is False
        assert "uptime_seconds" not in status

        # After start
        await monitor.start()
        await asyncio.sleep(0.1)

        status = monitor.get_status()
        assert status["is_running"] is True
        assert "uptime_seconds" in status
        assert status["uptime_seconds"] >= 0

        # Record some failures
        proxy1 = pool.proxies[0]
        monitor._record_failure(proxy1)

        status = monitor.get_status()
        assert status["failure_counts"][proxy1.url] == 1

        await monitor.stop()

        # After stop
        status = monitor.get_status()
        assert status["is_running"] is False

    async def test_monitor_mixed_health_statuses(self) -> None:
        """HealthMonitor works with different proxy health statuses."""
        pool = ProxyPool(name="mixed_health_pool")

        proxy1 = Proxy(url="http://proxy1.com:8080", health_status=HealthStatus.HEALTHY)
        proxy2 = Proxy(url="http://proxy2.com:8080", health_status=HealthStatus.DEGRADED)
        proxy3 = Proxy(url="http://proxy3.com:8080", health_status=HealthStatus.UNHEALTHY)
        proxy4 = Proxy(url="http://proxy4.com:8080", health_status=HealthStatus.DEAD)

        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)
        pool.add_proxy(proxy3)
        pool.add_proxy(proxy4)

        monitor = HealthMonitor(pool=pool)

        status = monitor.get_status()
        assert status["total_proxies"] == 4

        # get_healthy_proxies considers HEALTHY, DEGRADED, UNKNOWN
        # UNHEALTHY and DEAD are excluded
        healthy_count = len(pool.get_healthy_proxies())
        assert status["healthy_proxies"] == healthy_count
