"""Unit tests for HealthMonitor continuous health checking."""

import asyncio
from io import StringIO
from unittest.mock import AsyncMock, patch

import pytest
from loguru import logger

from proxywhirl.fetchers import ValidationResult
from proxywhirl.models import HealthMonitor, HealthStatus, Proxy, ProxyPool


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


class TestHealthMonitorChecks:
    """Test one bounded health-check cycle with mocked validation I/O."""

    async def test_cycle_updates_health_fields_without_request_metrics(self) -> None:
        """Health checks update health telemetry without counting user requests."""
        pool = ProxyPool(name="test_pool")
        healthy = Proxy(
            url="https://healthy.example.com:8443",
            protocol="https",
            username="user@tenant",
            password="p:ss/word",
            total_requests=7,
            total_successes=5,
            total_failures=2,
            consecutive_failures=4,
            requests_started=8,
            requests_completed=7,
            requests_active=1,
        )
        failing = Proxy(
            url="socks5://failing.example.com:1080",
            protocol="socks5",
            total_requests=4,
            total_successes=3,
            total_failures=1,
            consecutive_failures=2,
        )
        await pool.aadd_proxy(healthy)
        await pool.aadd_proxy(failing)
        monitor = HealthMonitor(pool=pool, check_interval=30, failure_threshold=3)

        healthy_request_metrics = {
            "total_requests": healthy.total_requests,
            "total_successes": healthy.total_successes,
            "total_failures": healthy.total_failures,
            "consecutive_failures": healthy.consecutive_failures,
            "requests_started": healthy.requests_started,
            "requests_completed": healthy.requests_completed,
            "requests_active": healthy.requests_active,
            "last_success_at": healthy.last_success_at,
            "last_failure_at": healthy.last_failure_at,
        }
        failing_request_metrics = {
            "total_requests": failing.total_requests,
            "total_successes": failing.total_successes,
            "total_failures": failing.total_failures,
            "consecutive_failures": failing.consecutive_failures,
            "requests_started": failing.requests_started,
            "requests_completed": failing.requests_completed,
            "requests_active": failing.requests_active,
            "last_success_at": failing.last_success_at,
            "last_failure_at": failing.last_failure_at,
        }

        validator = AsyncMock()
        validator.validate.side_effect = [
            ValidationResult(is_valid=True, response_time_ms=12.5),
            ValidationResult(is_valid=False, response_time_ms=None),
        ]

        with patch("proxywhirl.fetchers.ProxyValidator") as validator_type:
            validator_type.return_value.__aenter__.return_value = validator
            await monitor._run_health_checks()

        validator_type.assert_called_once_with(
            timeout=monitor._VALIDATION_TIMEOUT_SECONDS,
            concurrency=monitor._MAX_CONCURRENT_CHECKS,
            cache_ttl_seconds=0,
        )
        validator_type.return_value.__aexit__.assert_awaited_once()
        first_payload, second_payload = [
            awaited.args[0] for awaited in validator.validate.await_args_list
        ]
        assert first_payload == {
            "url": "https://user%40tenant:p%3Ass%2Fword@healthy.example.com:8443",
            "protocol": "https",
        }
        assert second_payload == {
            "url": "socks5://failing.example.com:1080",
            "protocol": "socks5",
        }

        assert healthy.health_status == HealthStatus.HEALTHY
        assert healthy.last_health_check is not None
        assert healthy.next_check_time is not None
        assert (healthy.next_check_time - healthy.last_health_check).total_seconds() == 30
        assert healthy.consecutive_successes == 1
        assert healthy.recovery_attempt == 0
        assert healthy.last_health_error is None
        assert healthy.total_checks == 1
        assert healthy.total_health_failures == 0
        assert healthy.latency_ms == 12.5

        assert failing.health_status == HealthStatus.DEGRADED
        assert failing.last_health_check is not None
        assert failing.next_check_time is not None
        assert failing.consecutive_successes == 0
        assert failing.recovery_attempt == 1
        assert failing.last_health_error == "Proxy validation failed"
        assert failing.total_checks == 1
        assert failing.total_health_failures == 1
        assert monitor._failure_counts == {failing.url: 1}

        assert {
            name: getattr(healthy, name) for name in healthy_request_metrics
        } == healthy_request_metrics
        assert {
            name: getattr(failing, name) for name in failing_request_metrics
        } == failing_request_metrics

    async def test_cycle_resets_failures_and_evicts_at_threshold(self) -> None:
        """A success resets monitor failures; repeated failures evict asynchronously."""
        pool = ProxyPool(name="test_pool")
        proxy = Proxy(url="http://flaky.example.com:8080")
        await pool.aadd_proxy(proxy)
        monitor = HealthMonitor(pool=pool, failure_threshold=2)

        validator = AsyncMock()
        validator.validate.side_effect = [
            ValidationResult(is_valid=False, response_time_ms=None),
            ValidationResult(is_valid=True, response_time_ms=8.0),
            ValidationResult(is_valid=False, response_time_ms=None),
            ValidationResult(is_valid=False, response_time_ms=None),
        ]

        with patch("proxywhirl.fetchers.ProxyValidator") as validator_type:
            validator_type.return_value.__aenter__.return_value = validator

            await monitor._run_health_checks()
            assert monitor._failure_counts[proxy.url] == 1

            await monitor._run_health_checks()
            assert proxy.url not in monitor._failure_counts
            assert proxy.consecutive_failures == 0
            assert proxy.health_status == HealthStatus.HEALTHY

            await monitor._run_health_checks()
            assert await pool.asize() == 1
            assert proxy.health_status == HealthStatus.DEGRADED

            await monitor._run_health_checks()

        assert await pool.asize() == 0
        assert proxy.health_status == HealthStatus.DEAD
        assert proxy.url not in monitor._failure_counts
        assert proxy.total_checks == 4
        assert proxy.total_health_failures == 3
        assert proxy.total_requests == 0
        assert proxy.total_successes == 0
        assert proxy.total_failures == 0

    async def test_cycle_skips_validator_for_empty_snapshot(self) -> None:
        """An empty async snapshot completes without allocating validator resources."""
        monitor = HealthMonitor(pool=ProxyPool(name="empty"))

        with patch("proxywhirl.fetchers.ProxyValidator") as validator_type:
            await monitor._run_health_checks()

        validator_type.assert_not_called()


class TestHealthMonitorScheduler:
    """Test background task scheduling."""

    async def test_cycle_failure_logs_type_without_secret_and_loop_continues(self) -> None:
        """A failed cycle is sanitized and does not stop later health checks."""
        monitor = HealthMonitor(pool=ProxyPool(name="test_pool"), check_interval=1)
        secret_marker = "health-cycle-secret-marker"
        cycle_count = 0

        async def run_cycle() -> None:
            nonlocal cycle_count
            cycle_count += 1
            if cycle_count == 1:
                raise RuntimeError(f"validation failed with {secret_marker}")
            monitor.is_running = False

        monitor._run_health_checks = AsyncMock(side_effect=run_cycle)
        monitor.is_running = True
        output = StringIO()
        sink_id = logger.add(output, format="{message}|{extra}")

        try:
            with patch("proxywhirl.models.core.asyncio.sleep", new_callable=AsyncMock):
                await monitor._check_health_loop()
        finally:
            logger.remove(sink_id)

        log_output = output.getvalue()
        assert cycle_count == 2
        assert "Health monitor health-check cycle failed" in log_output
        assert "RuntimeError" in log_output
        assert secret_marker not in log_output

    async def test_stop_surfaces_failed_task_without_secret(self) -> None:
        """Stopping consumes and safely surfaces a completed task failure."""
        monitor = HealthMonitor(pool=ProxyPool(name="test_pool"))
        secret_marker = "health-stop-secret-marker"

        async def fail_background_task() -> None:
            raise ValueError(f"background failure with {secret_marker}")

        monitor.is_running = True
        monitor._task = asyncio.create_task(fail_background_task())
        await asyncio.sleep(0)
        output = StringIO()
        sink_id = logger.add(output, format="{message}|{extra}")

        try:
            with pytest.raises(
                RuntimeError,
                match="Health monitor background task failed during shutdown",
            ) as raised:
                await monitor.stop()
        finally:
            logger.remove(sink_id)

        log_output = output.getvalue()
        assert secret_marker not in str(raised.value)
        assert "Health monitor background task failed during shutdown" in log_output
        assert "ValueError" in log_output
        assert secret_marker not in log_output
        assert monitor.is_running is False
        assert monitor._task is None
        assert monitor._start_time is None

    async def test_monitor_start_schedules_task(self) -> None:
        """start() creates background task and sets is_running."""
        pool = ProxyPool(name="test_pool")
        await pool.aadd_proxy(Proxy(url="http://proxy1.com:8080"))
        monitor = HealthMonitor(pool=pool, check_interval=10)

        # Mock the _check_health_loop to avoid actual running
        monitor._check_health_loop = AsyncMock()

        await monitor.start()

        assert monitor.is_running is True
        assert monitor._task is not None
        assert not monitor._task.done()

        # Cleanup
        await monitor.stop()

    async def test_monitor_stop_cancels_task(self) -> None:
        """stop() cancels background task and sets is_running to False."""
        pool = ProxyPool(name="test_pool")
        await pool.aadd_proxy(Proxy(url="http://proxy1.com:8080"))
        monitor = HealthMonitor(pool=pool, check_interval=10)
        monitor._check_health_loop = AsyncMock()

        await monitor.start()
        assert monitor.is_running is True

        await monitor.stop()

        assert monitor.is_running is False
        assert monitor._task is None or monitor._task.cancelled()

    async def test_monitor_checks_run_periodically(self) -> None:
        """Health checks run periodically at configured interval."""
        pool = ProxyPool(name="test_pool")
        await pool.aadd_proxy(Proxy(url="http://proxy1.com:8080"))
        monitor = HealthMonitor(pool=pool, check_interval=1)  # 1 second for testing

        check_count = 0

        async def mock_check() -> None:
            nonlocal check_count
            check_count += 1

        monitor._run_health_checks = AsyncMock(side_effect=mock_check)

        await monitor.start()

        # Wait for at least 2 checks (2+ seconds)
        await asyncio.sleep(2.5)

        await monitor.stop()

        # Should have run at least 2 checks
        assert check_count >= 2

    async def test_monitor_start_idempotent(self) -> None:
        """Calling start() twice doesn't create multiple tasks."""
        pool = ProxyPool(name="test_pool")
        await pool.aadd_proxy(Proxy(url="http://proxy1.com:8080"))
        monitor = HealthMonitor(pool=pool, check_interval=10)
        monitor._check_health_loop = AsyncMock()

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
        await pool.aadd_proxy(proxy1)
        await pool.aadd_proxy(proxy2)

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
        await pool.aadd_proxy(proxy)

        monitor = HealthMonitor(pool=pool, failure_threshold=3)

        # Record failures up to threshold
        monitor._record_failure(proxy)
        monitor._record_failure(proxy)
        assert await pool.asize() == 1  # Still in pool

        await asyncio.to_thread(monitor._record_failure, proxy)  # Reaches threshold
        assert await pool.asize() == 0  # Evicted

    async def test_monitor_resets_failures_on_success(self) -> None:
        """Successful health check resets failure count."""
        pool = ProxyPool(name="test_pool")
        proxy = Proxy(url="http://proxy.com:8080")
        await pool.aadd_proxy(proxy)

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
        await pool.aadd_proxy(proxy1)
        await pool.aadd_proxy(proxy2)

        monitor = HealthMonitor(pool=pool, failure_threshold=2)

        # Evict proxy1
        monitor._record_failure(proxy1)
        await asyncio.to_thread(monitor._record_failure, proxy1)

        assert await pool.asize() == 1
        remaining = await pool.aget_all_proxies()
        assert proxy1.url not in [p.url for p in remaining]
        assert proxy2.url in [p.url for p in remaining]


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
        await pool.aadd_proxy(Proxy(url="http://proxy.com:8080"))
        monitor = HealthMonitor(pool=pool, check_interval=60)
        monitor._check_health_loop = AsyncMock()

        await monitor.start()

        await asyncio.sleep(0.1)  # Brief delay

        status = await asyncio.to_thread(monitor.get_status)

        assert status["is_running"] is True
        assert "uptime_seconds" in status
        assert status["uptime_seconds"] >= 0

        await monitor.stop()
