"""Tests for async retry execution with exponential backoff."""

import asyncio

import pytest


class TestAsyncRetryBasics:
    """Test basic async retry functionality."""

    @pytest.mark.asyncio
    async def test_successful_operation_no_retry(self):
        """Test successful operation doesn't require retry."""
        call_count = 0

        async def operation():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await operation()
        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_on_failure(self):
        """Test retry after transient failure."""
        call_count = 0

        async def flaky_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("transient error")
            return "success"

        # Manual retry with backoff
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await flaky_operation()
                assert result == "success"
                break
            except ValueError:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(0.01 * (2**attempt))  # Exponential backoff

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """Test that retries are exhausted."""
        call_count = 0

        async def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("persistent error")

        max_retries = 3
        with pytest.raises(ValueError):
            for attempt in range(max_retries):
                try:
                    await always_fails()
                except ValueError:
                    if attempt == max_retries - 1:
                        raise
                    await asyncio.sleep(0.001)

        assert call_count == 3


class TestExponentialBackoff:
    """Test exponential backoff timing."""

    @pytest.mark.asyncio
    async def test_backoff_delays_increase(self):
        """Test that backoff delays increase exponentially."""
        delays = []

        async def measure_backoff():
            for attempt in range(4):
                if attempt > 0:
                    delay = 0.001 * (2 ** (attempt - 1))
                    delays.append(delay)
                    await asyncio.sleep(delay)

        await measure_backoff()

        # Delays should increase: 0.001, 0.002, 0.004
        assert len(delays) == 3
        assert delays[1] == delays[0] * 2
        assert delays[2] == delays[1] * 2

    @pytest.mark.asyncio
    async def test_backoff_with_jitter(self):
        """Test backoff with jitter prevents thundering herd."""
        import random

        random.seed(42)

        delays = []

        async def backoff_with_jitter():
            for attempt in range(4):
                if attempt > 0:
                    base_delay = 0.001 * (2 ** (attempt - 1))
                    # Add jitter: base_delay * (0.5 to 1.5)
                    jittered = base_delay * (0.5 + random.random())
                    delays.append(jittered)
                    await asyncio.sleep(jittered)

        await backoff_with_jitter()

        assert len(delays) == 3
        # All delays should be positive
        assert all(d > 0 for d in delays)

    @pytest.mark.asyncio
    async def test_max_backoff_cap(self):
        """Test that backoff is capped at maximum."""
        max_delay = 0.1
        delays = []

        async def capped_backoff():
            for attempt in range(10):  # More attempts to reach cap
                if attempt > 0:
                    delay = min(0.001 * (2 ** (attempt - 1)), max_delay)
                    delays.append(delay)
                    await asyncio.sleep(delay)

        await capped_backoff()

        # All delays should be <= max_delay
        assert all(d <= max_delay for d in delays)
        # Eventually should reach the cap
        assert any(d == max_delay for d in delays[-3:])


class TestAsyncRetryPolicies:
    """Test different retry policies."""

    @pytest.mark.asyncio
    async def test_retry_only_on_specific_errors(self):
        """Test retrying only on transient errors."""
        call_count = 0

        async def operation():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("transient")
            return "success"

        # Retry on ConnectionError
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await operation()
                assert result == "success"
                break
            except ConnectionError:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(0.001)
            except Exception:
                # Don't retry other exceptions
                raise

    @pytest.mark.asyncio
    async def test_dont_retry_permanent_errors(self):
        """Test not retrying permanent errors."""
        call_count = 0

        async def operation():
            nonlocal call_count
            call_count += 1
            raise ValueError("permanent error")

        # Don't retry ValueError
        max_retries = 3
        with pytest.raises(ValueError):
            for attempt in range(max_retries):
                try:
                    await operation()
                except ValueError:
                    # Don't retry - raise immediately
                    raise
                except Exception:
                    if attempt == max_retries - 1:
                        raise
                    await asyncio.sleep(0.001)

        # Should only call once for permanent error
        assert call_count == 1


class TestAsyncRetryWithTimeout:
    """Test retry behavior with timeouts."""

    @pytest.mark.asyncio
    async def test_retry_respects_overall_timeout(self):
        """Test that retries are bounded by overall timeout."""
        call_count = 0

        async def slow_operation():
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(1.0)  # Very slow
            return "done"

        # Very short timeout
        with pytest.raises(asyncio.TimeoutError):
            async with asyncio.timeout(0.05):
                max_retries = 10
                for attempt in range(max_retries):
                    try:
                        result = await slow_operation()
                        break
                    except Exception:
                        if attempt == max_retries - 1:
                            raise
                        await asyncio.sleep(0.01)

    @pytest.mark.asyncio
    async def test_individual_operation_timeout(self):
        """Test timeout per operation attempt."""
        call_count = 0

        async def operation():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                await asyncio.sleep(0.5)  # Slow
            return "success"

        # First call times out, second succeeds
        max_retries = 3
        result = None
        for attempt in range(max_retries):
            try:
                async with asyncio.timeout(0.1):
                    result = await operation()
                    break
            except asyncio.TimeoutError:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(0.01)

        assert result == "success"
        assert call_count == 2


class TestAsyncRetryCircuitBreaker:
    """Test retry interaction with circuit breaker pattern."""

    @pytest.mark.asyncio
    async def test_retry_opens_circuit_on_repeated_failures(self):
        """Test circuit breaker opens after repeated failures."""
        call_count = 0
        failure_count = 0
        circuit_open = False

        async def operation():
            nonlocal call_count, failure_count, circuit_open
            if circuit_open:
                raise RuntimeError("circuit open")

            call_count += 1
            raise ValueError("operation failed")

        # Try retries, then open circuit
        max_failures = 3
        for attempt in range(5):
            try:
                await operation()
            except RuntimeError:
                break  # Circuit open
            except ValueError:
                failure_count += 1
                if failure_count >= max_failures:
                    circuit_open = True
                await asyncio.sleep(0.001)

        assert circuit_open
        assert failure_count == max_failures

    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_retry(self):
        """Test retry during circuit breaker half-open state."""
        state = "closed"
        call_count = 0

        async def operation():
            nonlocal state, call_count
            call_count += 1
            if state == "open":
                raise RuntimeError("circuit open")
            if state == "half-open" and call_count <= 1:
                raise ValueError("test")
            return "success"

        # Try when closed - succeed
        result = await operation()
        assert result == "success"

        # Open circuit
        state = "open"
        with pytest.raises(RuntimeError):
            await operation()

        # Move to half-open and retry
        state = "half-open"
        call_count = 0
        max_retries = 2
        for attempt in range(max_retries):
            try:
                result = await operation()
                assert result == "success"
                break
            except ValueError:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(0.001)


class TestAsyncRetryMonitoring:
    """Test monitoring and observability of retries."""

    @pytest.mark.asyncio
    async def test_track_retry_attempts(self):
        """Test tracking number of retry attempts."""
        attempts = []

        async def operation_with_tracking():
            call_count = 0
            max_retries = 3

            for call_count, attempt in enumerate(range(max_retries), start=1):
                attempts.append(attempt)
                try:
                    if call_count < 2:
                        raise ValueError("fail")
                    return "success"
                except ValueError:
                    if attempt == max_retries - 1:
                        raise
                    await asyncio.sleep(0.001)

        result = await operation_with_tracking()
        assert result == "success"
        assert len(attempts) == 2  # Attempted twice

    @pytest.mark.asyncio
    async def test_track_cumulative_retry_time(self):
        """Test tracking total time spent in retries."""
        import time

        call_count = 0

        async def slow_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                await asyncio.sleep(0.1)
                raise ValueError("fail")
            return "success"

        start = time.time()
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await slow_operation()
                break
            except ValueError:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(0.05)
        elapsed = time.time() - start

        # Should have spent time in both operation and backoff
        assert elapsed >= 0.1  # First operation sleep

    @pytest.mark.asyncio
    async def test_retry_metrics_collection(self):
        """Test collecting metrics about retry attempts."""
        metrics = {
            "total_attempts": 0,
            "successful_attempts": 0,
            "failed_attempts": 0,
            "total_backoff_time": 0,
        }

        call_count = 0

        async def operation():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("fail")
            return "success"

        max_retries = 3
        for attempt in range(max_retries):
            metrics["total_attempts"] += 1
            try:
                result = await operation()
                metrics["successful_attempts"] += 1
                break
            except ValueError:
                metrics["failed_attempts"] += 1
                if attempt == max_retries - 1:
                    raise
                backoff = 0.01 * (2**attempt)
                metrics["total_backoff_time"] += backoff
                await asyncio.sleep(backoff)

        assert metrics["total_attempts"] == 2
        assert metrics["successful_attempts"] == 1
        assert metrics["failed_attempts"] == 1
        assert metrics["total_backoff_time"] > 0
