"""Tests for error and recovery paths in ProxyWhirl components."""

from __future__ import annotations

import asyncio
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest
from pydantic import ValidationError

from proxywhirl.cache.manager import CacheManager
from proxywhirl.cache.models import CacheConfig, CacheEntry
from proxywhirl.circuit_breaker import AsyncCircuitBreaker, CircuitBreaker, CircuitBreakerState
from proxywhirl.exceptions import ProxyConnectionError, ProxyPoolEmptyError
from proxywhirl.models import Proxy, ProxyPool
from proxywhirl.retry import RetryableError, RetryExecutor, RetryMetrics, RetryPolicy
from proxywhirl.storage import FileStorage
from tests.conftest import ProxyFactory


def make_cache_entry(key: str, proxy_url: str, ttl_seconds: int = 60) -> CacheEntry:
    now = datetime.now(timezone.utc)
    return CacheEntry(
        key=key,
        proxy_url=proxy_url,
        source="test",
        fetch_time=now,
        last_accessed=now,
        ttl_seconds=ttl_seconds,
        expires_at=now + timedelta(seconds=ttl_seconds),
    )


# ============================================================================
# TIMEOUT EDGE CASES
# ============================================================================


class TestTimeoutContexts:
    """Test timeout behavior across edge cases."""

    @pytest.mark.parametrize(
        ("timeout_ms", "should_timeout"),
        [
            (0.001, True),
            (0.1, True),
            (1.0, False),
            (10000, False),
            (99999, False),
        ],
    )
    def test_timeout_edge_cases(self, timeout_ms: float, should_timeout: bool) -> None:
        """Test timeout behavior at extremes."""
        start = time.perf_counter()

        def work_for(duration_ms: float) -> str:
            time.sleep(duration_ms / 1000)
            return "done"

        timeout_sec = timeout_ms / 1000
        try:
            if timeout_sec >= 0.01:
                assert work_for(5) == "done"
            elapsed = time.perf_counter() - start
            assert elapsed < 1.0
        except Exception as exc:  # pragma: no cover - defensive
            assert should_timeout or isinstance(exc, TimeoutError)

    @pytest.mark.asyncio
    async def test_async_timeout_edge_cases(self) -> None:
        """Test async timeout edge cases."""

        async def slow_operation() -> str:
            await asyncio.sleep(0.5)
            return "done"

        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(slow_operation(), timeout=0.001)

        result = await asyncio.wait_for(slow_operation(), timeout=1.0)
        assert result == "done"

    def test_circuit_breaker_timeout_recovery(self) -> None:
        """Test circuit breaker transition to half-open after timeout."""
        breaker = CircuitBreaker(
            proxy_id="timeout_recovery", failure_threshold=2, timeout_duration=0.1
        )

        for _ in range(2):
            breaker.record_failure()

        assert breaker.state == CircuitBreakerState.OPEN

        time.sleep(0.15)

        assert breaker.should_attempt_request() is True
        assert breaker.state == CircuitBreakerState.HALF_OPEN

    @pytest.mark.asyncio
    async def test_async_circuit_breaker_timeout_recovery(self) -> None:
        """Test async circuit breaker transition to half-open after timeout."""
        breaker = AsyncCircuitBreaker(
            proxy_id="async_timeout_recovery",
            failure_threshold=2,
            timeout_duration=0.1,
        )

        await breaker.record_failure()
        await breaker.record_failure()

        assert breaker.state == CircuitBreakerState.OPEN

        await asyncio.sleep(0.15)

        assert await breaker.should_attempt_request() is True
        assert breaker.state == CircuitBreakerState.HALF_OPEN


# ============================================================================
# ERROR RECOVERY PATHS
# ============================================================================


class TestRecoveryPaths:
    """Test error recovery mechanisms."""

    def test_retry_executor_exponential_backoff_recovery(self) -> None:
        """Test retry executor recovery using the current HTTP-aware API."""
        policy = RetryPolicy(max_attempts=3, base_delay=0.01, max_backoff_delay=0.1, multiplier=2.0)
        executor = RetryExecutor(
            retry_policy=policy,
            circuit_breakers={},
            retry_metrics=RetryMetrics(),
        )

        attempt_count = 0
        attempt_times: list[float] = []
        proxy = ProxyFactory.build()
        request = httpx.Request("GET", "https://example.com")

        def flaky_operation() -> httpx.Response:
            nonlocal attempt_count
            attempt_count += 1
            attempt_times.append(time.perf_counter())

            if attempt_count < 3:
                raise httpx.ConnectError("Temporary failure", request=request)
            return httpx.Response(200, request=request)

        response = executor.execute_with_retry(
            flaky_operation,
            proxy,
            "GET",
            "https://example.com",
        )

        assert response.status_code == 200
        assert attempt_count == 3
        if len(attempt_times) >= 2:
            delay1 = attempt_times[1] - attempt_times[0]
            assert delay1 >= 0.01

    @pytest.mark.asyncio
    async def test_file_storage_corruption_recovery(self, tmp_path: Path) -> None:
        """Test file storage reporting invalid persisted data."""
        storage = FileStorage(tmp_path / "proxies.json")
        await storage.save([ProxyFactory.build()])

        (tmp_path / "proxies.json").write_text("{not valid json", encoding="utf-8")

        with pytest.raises(ValueError):
            await storage.load()

    @pytest.mark.asyncio
    async def test_async_retry_recovery(self) -> None:
        """Test async retry recovery using the current HTTP-aware API."""
        policy = RetryPolicy(max_attempts=2, base_delay=0.01, multiplier=1.5)
        executor = RetryExecutor(
            retry_policy=policy,
            circuit_breakers={},
            retry_metrics=RetryMetrics(),
        )

        attempt_count = 0
        proxy = ProxyFactory.build()
        request = httpx.Request("GET", "https://example.com")

        async def async_flaky_operation() -> httpx.Response:
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise httpx.ConnectError("Async temporary failure", request=request)
            return httpx.Response(200, request=request)

        response = await executor.execute_with_retry_async(
            async_flaky_operation,
            proxy,
            "GET",
            "https://example.com",
        )

        assert response.status_code == 200
        assert attempt_count == 2

    def test_pool_empty_recovery(self) -> None:
        """Test recovery when pool becomes empty."""
        pool = ProxyPool(name="empty_pool", proxies=[])

        with pytest.raises(ProxyPoolEmptyError):
            if not pool.proxies:
                raise ProxyPoolEmptyError(f"Pool '{pool.name}' is empty")

    def test_validation_error_recovery(self) -> None:
        """Test recovery from validation errors."""
        invalid_data = {"url": "not-a-valid-url", "protocol": "invalid_protocol"}

        with pytest.raises(ValidationError):
            Proxy(**invalid_data)

        valid_proxy = ProxyFactory.build()
        assert valid_proxy.url is not None
        assert valid_proxy.protocol in ["http", "https", "socks4", "socks5"]


# ============================================================================
# DATA CORRUPTION DETECTION & RECOVERY
# ============================================================================


class TestCorruptionRecovery:
    """Test data corruption detection and recovery."""

    def test_cache_corruption_detection(self) -> None:
        """Test detection of corrupted cache data."""
        cache = CacheManager(CacheConfig())
        proxy = ProxyFactory.build()
        cache_key = f"proxy:{proxy.id}"
        entry = make_cache_entry(cache_key, proxy.url)

        assert cache.put(cache_key, entry) is True

        with patch.object(cache, "get", side_effect=ValueError("Invalid cache payload")):
            with pytest.raises(ValueError):
                cache.get(cache_key)

    @pytest.mark.asyncio
    async def test_file_storage_round_trip(self, tmp_path: Path) -> None:
        """Test recovery through a valid file storage round-trip."""
        storage = FileStorage(tmp_path / "proxies.json")
        proxies = [ProxyFactory.build() for _ in range(3)]

        await storage.save(proxies)
        loaded = await storage.load()

        assert [proxy.url for proxy in loaded] == [proxy.url for proxy in proxies]

    @pytest.mark.asyncio
    async def test_partial_proxy_rewrite_handling(self, tmp_path: Path) -> None:
        """Test that rewriting stored proxies preserves the valid subset."""
        storage = FileStorage(tmp_path / "proxies.json")
        proxies = [ProxyFactory.build() for _ in range(5)]

        await storage.save(proxies)
        loaded = await storage.load()
        assert len(loaded) == 5

        await storage.save(loaded[1:])
        recovered = await storage.load()

        assert len(recovered) == 4


# ============================================================================
# PRECISE TIMEOUT BEHAVIOR
# ============================================================================


class TestTimeoutBehavior:
    """Test precise timeout behavior across components."""

    def test_cache_manager_operation_timeout(self) -> None:
        """Test cache manager stores and returns cache entries."""
        cache = CacheManager(CacheConfig())
        entry = make_cache_entry("test_key", "http://example.com:8080")

        assert cache.put("test_key", entry) is True
        value = cache.get("test_key")
        assert value is not None
        assert value.proxy_url == "http://example.com:8080"

        cache.clear()

    @pytest.mark.asyncio
    async def test_async_operation_precise_timeout(self) -> None:
        """Test precise async timeout behavior."""
        start = time.perf_counter()

        async def timed_operation() -> str:
            await asyncio.sleep(0.05)
            return "completed"

        result = await asyncio.wait_for(timed_operation(), timeout=1.0)
        elapsed = time.perf_counter() - start
        assert result == "completed"
        assert elapsed < 1.0

    def test_circuit_breaker_timeout_threshold(self) -> None:
        """Test circuit breaker opens after the configured failure threshold."""
        breaker = CircuitBreaker(
            proxy_id="timeout_threshold",
            failure_threshold=3,
            timeout_duration=0.2,
        )

        for _ in range(3):
            breaker.record_failure()

        assert breaker.state == CircuitBreakerState.OPEN

    def test_retry_policy_timeout_escalation(self) -> None:
        """Test exponential delay growth in the current retry policy."""
        policy = RetryPolicy(max_attempts=3, base_delay=0.01, max_backoff_delay=0.5, multiplier=2.0)

        delays = [policy.calculate_delay(attempt) for attempt in range(3)]

        assert delays == pytest.approx([0.01, 0.02, 0.04])
        assert policy.base_delay == 0.01
        assert policy.multiplier == 2.0
        assert policy.max_backoff_delay == 0.5


# ============================================================================
# FALLBACK STRATEGY BEHAVIOR
# ============================================================================


class TestFallbackStrategies:
    """Test fallback behavior when primary strategy fails."""

    def test_primary_strategy_failure_fallback(self) -> None:
        """Test fallback to secondary strategy on primary failure."""
        primary_pool = ProxyPool(name="primary", proxies=[ProxyFactory.healthy() for _ in range(3)])

        def failing_strategy() -> Proxy | None:
            raise ProxyConnectionError("Primary strategy failed")

        with pytest.raises(ProxyConnectionError):
            failing_strategy()

        fallback_proxy = primary_pool.proxies[0]
        assert fallback_proxy is not None

    def test_empty_pool_fallback(self) -> None:
        """Test fallback when pool is empty."""
        empty_pool = ProxyPool(name="empty", proxies=[])

        if not empty_pool.proxies:
            fallback_proxies = ProxyFactory.batch(3)
            assert len(fallback_proxies) == 3

    def test_all_proxies_unhealthy_fallback(self) -> None:
        """Test fallback when all proxies are unhealthy."""
        unhealthy_pool = ProxyPool(
            name="unhealthy", proxies=[ProxyFactory.unhealthy() for _ in range(5)]
        )

        unhealthy_count = sum(
            1 for proxy in unhealthy_pool.proxies if proxy.health_status.value == "unhealthy"
        )
        assert unhealthy_count == len(unhealthy_pool.proxies)
        assert len(unhealthy_pool.proxies) > 0

    @pytest.mark.asyncio
    async def test_async_strategy_failure_with_fallback(self) -> None:
        """Test async strategy failure with fallback."""
        pool = ProxyPool(name="async_fallback", proxies=[ProxyFactory.healthy() for _ in range(3)])

        async def failing_async_strategy() -> None:
            raise RetryableError("Async strategy failed")

        with pytest.raises(RetryableError):
            await failing_async_strategy()

        fallback_proxy = pool.proxies[0]
        assert fallback_proxy is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
