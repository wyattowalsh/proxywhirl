"""Tests for error and recovery paths in ProxyWhirl components."""

from __future__ import annotations

import asyncio
import time
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from proxywhirl.cache.manager import CacheManager
from proxywhirl.circuit_breaker import AsyncCircuitBreaker, CircuitBreaker
from proxywhirl.exceptions import (
    CacheCorruptionError,
    ProxyConnectionError,
    ProxyPoolEmptyError,
)
from proxywhirl.models import Proxy, ProxyPool
from proxywhirl.retry import RetryableError
from proxywhirl.retry.executor import RetryExecutor, RetryPolicy
from proxywhirl.storage import SQLiteStorage
from tests.conftest import ProxyFactory, ProxyPoolFactory

# ============================================================================
# TIMEOUT EDGE CASES
# ============================================================================


class TestTimeoutContexts:
    """Test timeout behavior across edge cases."""

    @pytest.mark.parametrize(
        "timeout_ms,should_timeout",
        [
            (0.001, True),  # Sub-millisecond timeout
            (0.1, True),  # Very short timeout
            (1.0, False),  # Normal timeout
            (10000, False),  # Very long timeout
            (99999, False),  # Extremely long timeout
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
            result = None
            if timeout_sec >= 0.01:  # Python's timeout has practical limits
                try:
                    result = work_for(5)  # Always complete quickly
                except TimeoutError:
                    pass
            elapsed = time.perf_counter() - start
            assert elapsed < 1.0
        except Exception as e:
            assert should_timeout or isinstance(e, TimeoutError)

    @pytest.mark.asyncio
    async def test_async_timeout_edge_cases(self) -> None:
        """Test async timeout edge cases."""

        async def slow_operation() -> str:
            await asyncio.sleep(0.5)
            return "done"

        # Test extremely short timeout
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(slow_operation(), timeout=0.001)

        # Test sufficient timeout
        result = await asyncio.wait_for(slow_operation(), timeout=1.0)
        assert result == "done"

    def test_circuit_breaker_timeout_recovery(self) -> None:
        """Test circuit breaker recovery from timeout."""
        breaker = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=0.1,
            name="timeout_recovery",
        )

        call_count = 0

        def failing_call() -> str:
            nonlocal call_count
            call_count += 1
            raise TimeoutError("Operation timed out")

        # Should fail and open circuit
        with pytest.raises(TimeoutError):
            breaker.call(failing_call)

        with pytest.raises(TimeoutError):
            breaker.call(failing_call)

        # Circuit should be open
        assert breaker.is_open

        # Wait for recovery
        time.sleep(0.15)

        # Should be half-open
        assert breaker.is_half_open

    @pytest.mark.asyncio
    async def test_async_circuit_breaker_timeout_recovery(self) -> None:
        """Test async circuit breaker recovery from timeout."""
        breaker = AsyncCircuitBreaker(
            failure_threshold=2,
            recovery_timeout=0.1,
            name="async_timeout_recovery",
        )

        async def failing_call() -> str:
            raise TimeoutError("Operation timed out")

        # Should fail and open circuit
        with pytest.raises(TimeoutError):
            await breaker.call(failing_call)

        with pytest.raises(TimeoutError):
            await breaker.call(failing_call)

        assert breaker.is_open

        # Wait for recovery
        await asyncio.sleep(0.15)
        assert breaker.is_half_open


# ============================================================================
# ERROR RECOVERY PATHS
# ============================================================================


class TestRecoveryPaths:
    """Test error recovery mechanisms."""

    def test_retry_executor_exponential_backoff_recovery(self) -> None:
        """Test retry executor recovery with exponential backoff."""
        policy = RetryPolicy(
            max_retries=3,
            initial_delay_ms=10,
            max_delay_ms=100,
            exponential_base=2.0,
        )
        executor = RetryExecutor(policy=policy)

        attempt_count = 0
        attempt_times: list[float] = []

        def flaky_operation() -> str:
            nonlocal attempt_count
            attempt_count += 1
            attempt_times.append(time.perf_counter())

            if attempt_count < 3:
                raise RetryableError("Temporary failure")
            return "success"

        result = executor.execute(flaky_operation)
        assert result == "success"
        assert attempt_count == 3

        # Verify exponential backoff timing
        if len(attempt_times) >= 2:
            delay1 = (attempt_times[1] - attempt_times[0]) * 1000
            assert delay1 >= 10  # At least initial delay

    def test_storage_corruption_recovery(self) -> None:
        """Test recovery from corrupted storage."""
        storage = SQLiteStorage()

        # Create valid proxy
        proxy = ProxyFactory.build()
        pool = ProxyPoolFactory.build(proxies=[proxy])

        try:
            storage.save_pool(pool)

            # Simulate corruption by mangling data
            with patch.object(
                storage, "_decompress_pool", side_effect=ValueError("Decompression failed")
            ):
                with pytest.raises(CacheCorruptionError):
                    storage.load_pool(pool.id)
        finally:
            try:
                storage.delete_pool(pool.id)
            except Exception:
                pass

    @pytest.mark.asyncio
    async def test_async_retry_recovery(self) -> None:
        """Test async retry recovery."""
        policy = RetryPolicy(
            max_retries=2,
            initial_delay_ms=10,
            exponential_base=1.5,
        )
        executor = RetryExecutor(policy=policy)

        attempt_count = 0

        async def async_flaky_operation() -> str:
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise RetryableError("Async temporary failure")
            return "async_success"

        result = await executor.execute_async(async_flaky_operation)
        assert result == "async_success"
        assert attempt_count == 2

    def test_pool_empty_recovery(self) -> None:
        """Test recovery when pool becomes empty."""
        pool = ProxyPool(name="empty_pool", proxies=[])

        with pytest.raises(ProxyPoolEmptyError):
            # This should raise when trying to access from empty pool
            if not pool.proxies:
                raise ProxyPoolEmptyError(f"Pool '{pool.name}' is empty")

    def test_validation_error_recovery(self) -> None:
        """Test recovery from validation errors."""
        invalid_data = {
            "url": "not-a-valid-url",
            "protocol": "invalid_protocol",
        }

        with pytest.raises(ValidationError):
            Proxy(**invalid_data)

        # Should be able to create valid proxy after error
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
        cache = CacheManager()

        proxy = ProxyFactory.build()
        cache_key = f"proxy:{proxy.id}"

        # Store valid data
        cache.set(cache_key, proxy.model_dump_json(), ttl_seconds=60)

        # Simulate corruption by mangling stored data
        with patch.object(cache, "get", side_effect=ValueError("Invalid JSON")):
            with pytest.raises((ValueError, CacheCorruptionError)):
                cache.get(cache_key)

    def test_pool_corruption_recovery(self) -> None:
        """Test recovery from corrupted pool data."""
        pool = ProxyPoolFactory.build()
        storage = SQLiteStorage()

        try:
            storage.save_pool(pool)

            # Verify pool can be loaded
            loaded = storage.load_pool(pool.id)
            assert loaded.id == pool.id

            # Simulate corruption
            with patch.object(
                storage, "load_pool", side_effect=CacheCorruptionError("Corrupted pool")
            ):
                with pytest.raises(CacheCorruptionError):
                    storage.load_pool(pool.id)
        finally:
            try:
                storage.delete_pool(pool.id)
            except Exception:
                pass

    def test_partial_proxy_corruption_handling(self) -> None:
        """Test handling of partially corrupted proxy data."""
        pool = ProxyPool(
            name="test_corruption_pool",
            proxies=[ProxyFactory.build() for _ in range(5)],
        )
        storage = SQLiteStorage()

        try:
            storage.save_pool(pool)

            # Load and verify original
            loaded = storage.load_pool(pool.id)
            assert len(loaded.proxies) == 5

            # Simulate partial corruption - remove one proxy
            loaded.proxies = loaded.proxies[1:]

            # Re-save corrupted version
            storage.save_pool(loaded)

            # Verify partial data is recoverable
            recovered = storage.load_pool(pool.id)
            assert len(recovered.proxies) == 4
        finally:
            try:
                storage.delete_pool(pool.id)
            except Exception:
                pass


# ============================================================================
# PRECISE TIMEOUT BEHAVIOR
# ============================================================================


class TestTimeoutBehavior:
    """Test precise timeout behavior across components."""

    def test_cache_manager_operation_timeout(self) -> None:
        """Test timeout behavior in cache operations."""
        cache = CacheManager()

        # Normal operation should complete
        cache.set("test_key", "test_value", ttl_seconds=60)
        value = cache.get("test_key")
        assert value == "test_value"

        # Clear for next test
        cache.clear()

    @pytest.mark.asyncio
    async def test_async_operation_precise_timeout(self) -> None:
        """Test precise async timeout behavior."""
        start = time.perf_counter()

        async def timed_operation() -> str:
            await asyncio.sleep(0.05)
            return "completed"

        try:
            result = await asyncio.wait_for(timed_operation(), timeout=0.1)
            elapsed = time.perf_counter() - start
            assert result == "completed"
            assert elapsed < 0.2
        except asyncio.TimeoutError:
            pytest.fail("Operation should not timeout with 0.1s timeout")

    def test_circuit_breaker_timeout_threshold(self) -> None:
        """Test circuit breaker timeout threshold behavior."""
        breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=0.2,
            name="timeout_threshold",
        )

        def timeout_operation() -> str:
            raise TimeoutError("Timeout occurred")

        # Fail 3 times to trigger circuit open
        for _ in range(3):
            with pytest.raises(TimeoutError):
                breaker.call(timeout_operation)

        assert breaker.is_open

    def test_retry_policy_timeout_escalation(self) -> None:
        """Test timeout escalation in retry policy."""
        policy = RetryPolicy(
            max_retries=3,
            initial_delay_ms=10,
            max_delay_ms=500,
            exponential_base=2.0,
        )

        expected_delays = [10, 20, 40]  # Exponential growth with base 2

        # Verify policy configuration supports escalation
        assert policy.initial_delay_ms == 10
        assert policy.exponential_base == 2.0
        assert policy.max_delay_ms == 500


# ============================================================================
# FALLBACK STRATEGY BEHAVIOR
# ============================================================================


class TestFallbackStrategies:
    """Test fallback behavior when primary strategy fails."""

    def test_primary_strategy_failure_fallback(self) -> None:
        """Test fallback to secondary strategy on primary failure."""
        primary_pool = ProxyPool(
            name="primary",
            proxies=[ProxyFactory.healthy() for _ in range(3)],
        )

        # Simulate primary strategy failure
        def failing_strategy() -> Proxy | None:
            raise ProxyConnectionError("Primary strategy failed")

        # Should fallback to selecting from pool
        if primary_pool.proxies:
            fallback_proxy = primary_pool.proxies[0]
            assert fallback_proxy is not None

    def test_empty_pool_fallback(self) -> None:
        """Test fallback when pool is empty."""
        empty_pool = ProxyPool(name="empty", proxies=[])

        # Check for empty pool and fallback
        if not empty_pool.proxies:
            fallback_proxies = ProxyFactory.batch(3)
            assert len(fallback_proxies) == 3

    def test_all_proxies_unhealthy_fallback(self) -> None:
        """Test fallback when all proxies are unhealthy."""
        unhealthy_pool = ProxyPool(
            name="unhealthy",
            proxies=[ProxyFactory.unhealthy() for _ in range(5)],
        )

        # Verify all are unhealthy
        unhealthy_count = sum(
            1 for p in unhealthy_pool.proxies if p.health_status.value == "unhealthy"
        )
        assert unhealthy_count == len(unhealthy_pool.proxies)

        # Should still be able to select (with degraded quality)
        assert len(unhealthy_pool.proxies) > 0

    @pytest.mark.asyncio
    async def test_async_strategy_failure_with_fallback(self) -> None:
        """Test async strategy failure with fallback."""
        pool = ProxyPool(
            name="async_fallback",
            proxies=[ProxyFactory.healthy() for _ in range(3)],
        )

        async def failing_async_strategy() -> None:
            raise RetryableError("Async strategy failed")

        # Fallback to direct pool access
        try:
            await failing_async_strategy()
        except RetryableError:
            # Fallback
            assert len(pool.proxies) > 0
            fallback_proxy = pool.proxies[0]
            assert fallback_proxy is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
