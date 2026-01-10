"""
Tests for AsyncCircuitBreaker with RWLock implementation.

Tests verify that the RWLock-based circuit breaker provides:
1. Correct functionality (same as threading.Lock version)
2. Reduced lock contention under high concurrency
3. Improved throughput for read-heavy workloads
"""

import asyncio
import time
from unittest.mock import patch

from proxywhirl.circuit_breaker_async import AsyncCircuitBreaker, CircuitBreakerState


class TestAsyncCircuitBreakerRecordFailure:
    """Test AsyncCircuitBreaker.record_failure() method."""

    async def test_record_single_failure_stays_closed(self):
        """Test that a single failure keeps circuit breaker CLOSED."""
        cb = AsyncCircuitBreaker(proxy_id="test-proxy", failure_threshold=5)

        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0

        await cb.record_failure()

        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 1

    async def test_record_failures_opens_circuit(self):
        """Test that threshold failures open the circuit."""
        cb = AsyncCircuitBreaker(proxy_id="test-proxy", failure_threshold=3)

        # Record 2 failures - should stay closed
        await cb.record_failure()
        await cb.record_failure()
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 2

        # Record 3rd failure - should open
        await cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        assert cb.failure_count == 3

    async def test_rolling_window_cleanup(self):
        """Test that old failures are removed from rolling window."""
        cb = AsyncCircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=3,
            window_duration=2.0,  # 2 second window
        )

        # Record 2 failures
        with patch("time.time", return_value=100.0):
            await cb.record_failure()
            await cb.record_failure()

        assert cb.failure_count == 2

        # Wait for window to expire (mock time + 3 seconds)
        with patch("time.time", return_value=103.0):
            await cb.record_failure()  # This should clean up old failures

        # Only the latest failure should count (old ones expired)
        assert cb.failure_count == 1
        assert cb.state == CircuitBreakerState.CLOSED

    async def test_failure_in_half_open_reopens_circuit(self):
        """Test that failure in HALF_OPEN state reopens the circuit."""
        cb = AsyncCircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=2,
            timeout_duration=1.0,
        )

        # Open the circuit
        with patch("time.time", return_value=100.0):
            await cb.record_failure()
            await cb.record_failure()

        assert cb.state == CircuitBreakerState.OPEN

        # Transition to half-open
        with patch("time.time", return_value=101.0):
            await cb.should_attempt_request()

        assert cb.state == CircuitBreakerState.HALF_OPEN

        # Record failure in half-open state
        with patch("time.time", return_value=101.5):
            await cb.record_failure()

        # Should reopen
        assert cb.state == CircuitBreakerState.OPEN


class TestAsyncCircuitBreakerRecordSuccess:
    """Test AsyncCircuitBreaker.record_success() method."""

    async def test_success_in_closed_state_no_change(self):
        """Test that success in CLOSED state doesn't change state."""
        cb = AsyncCircuitBreaker(proxy_id="test-proxy")

        assert cb.state == CircuitBreakerState.CLOSED

        await cb.record_success()

        assert cb.state == CircuitBreakerState.CLOSED

    async def test_success_in_half_open_closes_circuit(self):
        """Test that success in HALF_OPEN state closes the circuit."""
        cb = AsyncCircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=2,
            timeout_duration=1.0,
        )

        # Open the circuit
        with patch("time.time", return_value=100.0):
            await cb.record_failure()
            await cb.record_failure()

        assert cb.state == CircuitBreakerState.OPEN
        assert cb.failure_count == 2

        # Transition to half-open
        with patch("time.time", return_value=101.0):
            await cb.should_attempt_request()

        assert cb.state == CircuitBreakerState.HALF_OPEN

        # Record success
        await cb.record_success()

        # Should close and reset
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0
        assert len(cb.failure_window) == 0


class TestAsyncCircuitBreakerShouldAttemptRequest:
    """Test AsyncCircuitBreaker.should_attempt_request() method."""

    async def test_closed_allows_requests(self):
        """Test that CLOSED state allows requests."""
        cb = AsyncCircuitBreaker(proxy_id="test-proxy")

        assert cb.state == CircuitBreakerState.CLOSED
        assert await cb.should_attempt_request() is True

    async def test_open_blocks_requests(self):
        """Test that OPEN state blocks requests before timeout."""
        cb = AsyncCircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=2,
            timeout_duration=10.0,
        )

        # Open the circuit
        with patch("time.time", return_value=100.0):
            await cb.record_failure()
            await cb.record_failure()

        assert cb.state == CircuitBreakerState.OPEN

        # Immediately check - should block
        with patch("time.time", return_value=100.5):
            assert await cb.should_attempt_request() is False

        # After 5 seconds (still before timeout) - should block
        with patch("time.time", return_value=105.0):
            assert await cb.should_attempt_request() is False

    async def test_open_transitions_to_half_open_after_timeout(self):
        """Test that OPEN state transitions to HALF_OPEN after timeout."""
        cb = AsyncCircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=2,
            timeout_duration=5.0,
        )

        # Open the circuit at time 100
        with patch("time.time", return_value=100.0):
            await cb.record_failure()
            await cb.record_failure()

        assert cb.state == CircuitBreakerState.OPEN
        assert cb.next_test_time == 105.0

        # Check at time 105 (timeout elapsed)
        with patch("time.time", return_value=105.0):
            result = await cb.should_attempt_request()

        assert result is True
        assert cb.state == CircuitBreakerState.HALF_OPEN

    async def test_half_open_allows_single_request(self):
        """Test that HALF_OPEN state allows only one test request."""
        cb = AsyncCircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=2,
            timeout_duration=1.0,
        )

        # Open and transition to half-open
        with patch("time.time", return_value=100.0):
            await cb.record_failure()
            await cb.record_failure()

        with patch("time.time", return_value=101.0):
            await cb.should_attempt_request()

        assert cb.state == CircuitBreakerState.HALF_OPEN

        # Second request should be blocked (pending flag set)
        assert await cb.should_attempt_request() is False


class TestAsyncCircuitBreakerReset:
    """Test AsyncCircuitBreaker.reset() method."""

    async def test_reset_from_open_state(self):
        """Test manual reset from OPEN state."""
        cb = AsyncCircuitBreaker(proxy_id="test-proxy", failure_threshold=2)

        # Open the circuit
        await cb.record_failure()
        await cb.record_failure()

        assert cb.state == CircuitBreakerState.OPEN
        assert cb.failure_count == 2

        # Reset
        await cb.reset()

        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0
        assert len(cb.failure_window) == 0
        assert cb.next_test_time is None

    async def test_reset_from_half_open_state(self):
        """Test manual reset from HALF_OPEN state."""
        cb = AsyncCircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=2,
            timeout_duration=1.0,
        )

        # Open and transition to half-open
        with patch("time.time", return_value=100.0):
            await cb.record_failure()
            await cb.record_failure()

        with patch("time.time", return_value=101.0):
            await cb.should_attempt_request()

        assert cb.state == CircuitBreakerState.HALF_OPEN

        # Reset
        await cb.reset()

        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0


class TestAsyncCircuitBreakerConcurrency:
    """Test AsyncCircuitBreaker concurrency and performance."""

    async def test_concurrent_read_operations(self):
        """Test that multiple concurrent reads don't block each other."""
        cb = AsyncCircuitBreaker(proxy_id="test-proxy")

        # Measure time for concurrent reads
        start = time.perf_counter()
        tasks = [cb.should_attempt_request() for _ in range(100)]
        results = await asyncio.gather(*tasks)
        duration = time.perf_counter() - start

        # All should succeed
        assert all(results)

        # Should be fast (< 1ms per operation on average)
        assert duration < 0.1, f"100 concurrent reads took {duration}s (expected < 0.1s)"

    async def test_concurrent_mixed_operations(self):
        """Test mixed read/write operations under concurrency."""
        cb = AsyncCircuitBreaker(proxy_id="test-proxy", failure_threshold=1000)

        async def reader():
            for _ in range(50):
                await cb.should_attempt_request()
                await asyncio.sleep(0.001)

        async def writer():
            for _ in range(10):
                await cb.record_failure()
                await asyncio.sleep(0.005)

        # Run 10 readers and 2 writers concurrently
        readers = [reader() for _ in range(10)]
        writers = [writer() for _ in range(2)]

        start = time.perf_counter()
        await asyncio.gather(*readers, *writers)
        duration = time.perf_counter() - start

        # Verify state is consistent
        assert cb.failure_count == 20  # 2 writers * 10 failures each
        assert cb.state == CircuitBreakerState.CLOSED  # Below threshold

        # Should complete reasonably fast
        assert duration < 1.0, f"Mixed operations took {duration}s (expected < 1s)"

    async def test_benchmark_read_heavy_workload(self):
        """Benchmark read-heavy workload showing RWLock advantage."""
        cb = AsyncCircuitBreaker(proxy_id="test-proxy")

        # Simulate read-heavy workload (95% reads, 5% writes)
        async def workload():
            for i in range(100):
                if i % 20 == 0:  # 5% writes
                    await cb.record_failure()
                else:  # 95% reads
                    await cb.should_attempt_request()

        # Run workload with high concurrency
        tasks = [workload() for _ in range(20)]  # 20 concurrent workers

        start = time.perf_counter()
        await asyncio.gather(*tasks)
        duration = time.perf_counter() - start

        total_operations = 20 * 100  # 2000 operations
        ops_per_second = total_operations / duration

        print("\nRWLock Benchmark:")
        print(f"  Total operations: {total_operations}")
        print(f"  Duration: {duration:.3f}s")
        print(f"  Throughput: {ops_per_second:.0f} ops/sec")

        # Should handle at least 10,000 ops/sec with RWLock
        assert (
            ops_per_second > 10000
        ), f"Throughput {ops_per_second:.0f} ops/sec is too low (expected > 10,000)"

    async def test_concurrent_state_transitions(self):
        """Test that concurrent operations maintain state consistency."""
        cb = AsyncCircuitBreaker(proxy_id="test-proxy", failure_threshold=5)

        # Concurrent failures
        await asyncio.gather(*[cb.record_failure() for _ in range(10)])

        # Circuit should be open (threshold is 5, we recorded 10 failures)
        assert cb.state == CircuitBreakerState.OPEN
        assert cb.failure_count >= 5  # At least threshold failures

    async def test_full_lifecycle_under_concurrency(self):
        """Test complete circuit breaker lifecycle with concurrent requests."""
        cb = AsyncCircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=3,
            window_duration=60.0,
            timeout_duration=0.1,  # Short timeout for testing
        )

        # Start CLOSED
        assert cb.state == CircuitBreakerState.CLOSED

        # Concurrent failures to open circuit
        await asyncio.gather(*[cb.record_failure() for _ in range(5)])

        # Now OPEN
        assert cb.state == CircuitBreakerState.OPEN

        # Wait for timeout
        await asyncio.sleep(0.15)

        # Transition to HALF_OPEN
        result = await cb.should_attempt_request()
        assert result is True
        assert cb.state == CircuitBreakerState.HALF_OPEN

        # Record success
        await cb.record_success()

        # Now CLOSED
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0
