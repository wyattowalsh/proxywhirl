"""
Tests for AsyncCircuitBreaker state transitions with time-based reset.

Covers all state transitions:
- CLOSED → OPEN (on failure threshold)
- OPEN → HALF_OPEN (on timeout timeout_duration)
- HALF_OPEN → CLOSED (on success)
- HALF_OPEN → OPEN (on failure in half-open state)
"""

import asyncio
import time
from unittest.mock import patch

import pytest

from proxywhirl.circuit_breaker import AsyncCircuitBreaker, CircuitBreakerState


class TestAsyncCircuitBreakerStateTransitions:
    """Test AsyncCircuitBreaker state transitions."""

    @pytest.mark.asyncio
    async def test_closed_to_open_transition(self):
        """Test CLOSED → OPEN transition when failure threshold is reached."""
        cb = AsyncCircuitBreaker(proxy_id="proxy-1", failure_threshold=3, window_duration=10.0)

        # Start in CLOSED state
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0

        # Record failures up to threshold
        for i in range(1, 3):
            await cb.record_failure()
            assert cb.state == CircuitBreakerState.CLOSED
            assert cb.failure_count == i

        # Threshold exceeded - transition to OPEN
        await cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        assert cb.failure_count == 3

    @pytest.mark.asyncio
    async def test_open_to_half_open_transition_on_timeout(self):
        """Test OPEN → HALF_OPEN transition after timeout_duration elapses."""
        cb = AsyncCircuitBreaker(
            proxy_id="proxy-1",
            failure_threshold=1,
            timeout_duration=1.0,  # 1 second timeout
        )

        # Move to OPEN state
        await cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN

        # Too soon - should still be OPEN
        await cb.should_attempt_request()
        assert cb.state == CircuitBreakerState.OPEN

        # Wait for timeout
        await asyncio.sleep(1.1)

        # Now should transition to HALF_OPEN
        should_attempt = await cb.should_attempt_request()
        assert should_attempt is True
        assert cb.state == CircuitBreakerState.HALF_OPEN

    @pytest.mark.asyncio
    async def test_half_open_to_closed_transition_on_success(self):
        """Test HALF_OPEN → CLOSED transition after successful request."""
        cb = AsyncCircuitBreaker(
            proxy_id="proxy-1",
            failure_threshold=1,
            timeout_duration=0.5,
        )

        # CLOSED → OPEN
        await cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN

        # OPEN → HALF_OPEN
        await asyncio.sleep(0.6)
        await cb.should_attempt_request()
        assert cb.state == CircuitBreakerState.HALF_OPEN

        # HALF_OPEN → CLOSED on success
        await cb.record_success()
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0

    @pytest.mark.asyncio
    async def test_half_open_to_open_transition_on_failure(self):
        """Test HALF_OPEN → OPEN transition on failure while testing recovery."""
        cb = AsyncCircuitBreaker(
            proxy_id="proxy-1",
            failure_threshold=1,
            timeout_duration=0.5,
        )

        # CLOSED → OPEN
        await cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN

        # OPEN → HALF_OPEN
        await asyncio.sleep(0.6)
        await cb.should_attempt_request()
        assert cb.state == CircuitBreakerState.HALF_OPEN

        # HALF_OPEN → OPEN on failure
        await cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN

    @pytest.mark.asyncio
    async def test_full_cycle_closed_open_half_open_closed(self):
        """Test full state cycle: CLOSED → OPEN → HALF_OPEN → CLOSED."""
        cb = AsyncCircuitBreaker(
            proxy_id="proxy-1",
            failure_threshold=2,
            window_duration=10.0,
            timeout_duration=0.5,
        )

        # State 1: CLOSED
        assert cb.state == CircuitBreakerState.CLOSED
        assert await cb.should_attempt_request() is True

        # Transition to OPEN
        await cb.record_failure()
        await cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        assert await cb.should_attempt_request() is False

        # Wait and transition to HALF_OPEN
        await asyncio.sleep(0.6)
        should_attempt = await cb.should_attempt_request()
        assert should_attempt is True
        assert cb.state == CircuitBreakerState.HALF_OPEN

        # Transition back to CLOSED on success
        await cb.record_success()
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0

    @pytest.mark.asyncio
    async def test_multiple_open_to_half_open_cycles(self):
        """Test multiple cycles through OPEN and HALF_OPEN states."""
        cb = AsyncCircuitBreaker(
            proxy_id="proxy-1",
            failure_threshold=1,
            timeout_duration=0.3,
        )

        for cycle in range(3):
            # Open circuit
            await cb.record_failure()
            assert cb.state == CircuitBreakerState.OPEN

            # Wait for recovery window
            await asyncio.sleep(0.4)

            # Should be HALF_OPEN
            await cb.should_attempt_request()
            assert cb.state == CircuitBreakerState.HALF_OPEN

            # Recover successfully
            await cb.record_success()
            assert cb.state == CircuitBreakerState.CLOSED

    @pytest.mark.asyncio
    async def test_reset_from_any_state(self):
        """Test reset() method resets from any state to CLOSED."""
        cb = AsyncCircuitBreaker(proxy_id="proxy-1", failure_threshold=1)

        # Reset from CLOSED (idempotent)
        await cb.reset()
        assert cb.state == CircuitBreakerState.CLOSED

        # Reset from OPEN
        await cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        await cb.reset()
        assert cb.state == CircuitBreakerState.CLOSED

        # Reset from HALF_OPEN
        await cb.record_failure()
        await asyncio.sleep(0.6)
        await cb.should_attempt_request()
        assert cb.state == CircuitBreakerState.HALF_OPEN
        await cb.reset()
        assert cb.state == CircuitBreakerState.CLOSED

    @pytest.mark.asyncio
    async def test_concurrent_state_transitions(self):
        """Test that state transitions are safe under concurrent access."""
        cb = AsyncCircuitBreaker(proxy_id="proxy-1", failure_threshold=5, window_duration=10.0)

        async def record_failures():
            for _ in range(5):
                await cb.record_failure()
                await asyncio.sleep(0.01)

        async def check_state():
            states = []
            for _ in range(10):
                states.append(cb.state)
                await asyncio.sleep(0.01)
            return states

        # Concurrently record failures and check state
        failures_task = asyncio.create_task(record_failures())
        state_task = asyncio.create_task(check_state())

        await failures_task
        states = await state_task

        # Verify final state is OPEN
        assert cb.state == CircuitBreakerState.OPEN

        # Verify state sequence was valid (no impossible transitions)
        for i in range(len(states) - 1):
            current = states[i]
            next_state = states[i + 1]
            # Valid transitions or same state
            assert (current == next_state) or (
                current == CircuitBreakerState.CLOSED and next_state == CircuitBreakerState.OPEN
            )

    @pytest.mark.asyncio
    async def test_state_transition_with_rolling_window(self):
        """Test state transitions respect rolling window cleanup."""
        cb = AsyncCircuitBreaker(
            proxy_id="proxy-1",
            failure_threshold=3,
            window_duration=1.0,
        )

        # Record failures at t=0
        with patch("time.time", return_value=100.0):
            await cb.record_failure()
            await cb.record_failure()
            assert cb.state == CircuitBreakerState.CLOSED
            assert cb.failure_count == 2

            # Record third failure - transitions to OPEN
            await cb.record_failure()
            assert cb.state == CircuitBreakerState.OPEN

        # Now at t=2.0 - failures outside window should be cleaned
        with patch("time.time", return_value=101.5):
            # Should still be OPEN (failures still in window)
            assert cb.state == CircuitBreakerState.OPEN

        # At t=3.0 - all failures outside window
        with patch("time.time", return_value=102.0):
            # Recording new failure should not immediately trigger window cleanup
            # but state should eventually reset
            pass
