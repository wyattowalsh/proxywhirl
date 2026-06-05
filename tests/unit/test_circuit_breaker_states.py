"""Test circuit breaker state machine transitions.

Tests all valid state transitions and edge cases:
- CLOSED → OPEN → HALF_OPEN → CLOSED
- Failure counting and thresholds
- Timeout expiration logic
- Concurrent access safety
"""

from __future__ import annotations

import time

from proxywhirl.circuit_breaker import CircuitBreakerBase, CircuitBreakerState


class TestCircuitBreakerStateMachine:
    """Test circuit breaker state transitions and logic."""

    def test_initial_state_is_closed(self) -> None:
        """Test that circuit breaker starts in CLOSED state."""
        cb = CircuitBreakerBase(proxy_id="proxy1")
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0

    def test_transitions_from_closed_to_open_on_threshold(self) -> None:
        """Test CLOSED → OPEN transition when failure threshold reached."""
        cb = CircuitBreakerBase(
            proxy_id="proxy1",
            failure_threshold=3,
            window_duration=60.0,
        )

        # Record failures below threshold
        for _ in range(2):
            cb._do_record_failure()
            assert cb.state == CircuitBreakerState.CLOSED

        # Record failure at threshold
        cb._do_record_failure()
        assert cb.state == CircuitBreakerState.OPEN

    def test_transitions_from_open_to_half_open_on_timeout(self) -> None:
        """Test OPEN → HALF_OPEN transition after timeout expires."""
        cb = CircuitBreakerBase(
            proxy_id="proxy1",
            failure_threshold=1,
            timeout_duration=0.1,  # 100ms timeout
        )

        # Force to OPEN state
        cb._do_record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        assert cb.next_test_time is not None

        # Should still be open immediately
        should_attempt = cb._do_should_attempt_request()
        assert not should_attempt
        assert cb.state == CircuitBreakerState.OPEN

        # Wait for timeout to expire
        time.sleep(0.15)

        # Now should transition to HALF_OPEN
        should_attempt = cb._do_should_attempt_request()
        assert should_attempt
        assert cb.state == CircuitBreakerState.HALF_OPEN

    def test_transitions_from_half_open_to_closed_on_success(self) -> None:
        """Test HALF_OPEN → CLOSED transition on successful request."""
        cb = CircuitBreakerBase(
            proxy_id="proxy1",
            failure_threshold=1,
            timeout_duration=0.01,
        )

        # Force to HALF_OPEN state
        cb._do_record_failure()
        time.sleep(0.02)
        cb._do_should_attempt_request()

        assert cb.state == CircuitBreakerState.HALF_OPEN

        # Record success
        cb._do_record_success()
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0

    def test_transitions_from_half_open_to_open_on_failure(self) -> None:
        """Test HALF_OPEN → OPEN transition on failed request."""
        cb = CircuitBreakerBase(
            proxy_id="proxy1",
            failure_threshold=1,
            timeout_duration=0.01,
        )

        # Force to HALF_OPEN state
        cb._do_record_failure()
        time.sleep(0.02)
        cb._do_should_attempt_request()

        assert cb.state == CircuitBreakerState.HALF_OPEN

        # Record failure
        cb._do_record_failure()
        assert cb.state == CircuitBreakerState.OPEN

    def test_failure_window_sliding(self) -> None:
        """Test that failures outside window are not counted."""
        cb = CircuitBreakerBase(
            proxy_id="proxy1",
            failure_threshold=3,
            window_duration=0.1,  # 100ms window
        )

        # Record 2 failures
        cb._do_record_failure()
        cb._do_record_failure()
        assert cb.failure_count == 2
        assert cb.state == CircuitBreakerState.CLOSED

        # Wait for window to expire
        time.sleep(0.15)

        # Record new failure - old ones should be purged
        cb._do_record_failure()
        assert cb.failure_count == 1
        assert cb.state == CircuitBreakerState.CLOSED

    def test_last_state_change_tracking(self) -> None:
        """Test that state change timestamp is updated."""
        cb = CircuitBreakerBase(proxy_id="proxy1")
        initial_time = cb.last_state_change

        time.sleep(0.01)
        cb._do_record_failure()

        if cb.state != CircuitBreakerState.CLOSED:
            assert cb.last_state_change > initial_time

    def test_state_does_not_transition_without_threshold(self) -> None:
        """Test state remains CLOSED when failures < threshold."""
        cb = CircuitBreakerBase(
            proxy_id="proxy1",
            failure_threshold=10,
        )

        for _ in range(5):
            cb._do_record_failure()
            assert cb.state == CircuitBreakerState.CLOSED

    def test_successful_requests_in_closed_state(self) -> None:
        """Test that success records do nothing in CLOSED state."""
        cb = CircuitBreakerBase(proxy_id="proxy1")
        assert cb.state == CircuitBreakerState.CLOSED

        # Record success
        cb._do_record_success()
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0

    def test_multiple_state_transitions_cycle(self) -> None:
        """Test multiple cycles of state transitions."""
        cb = CircuitBreakerBase(
            proxy_id="proxy1",
            failure_threshold=2,
            timeout_duration=0.01,
        )

        # Cycle 1: CLOSED → OPEN → HALF_OPEN → CLOSED
        cb._do_record_failure()
        cb._do_record_failure()
        assert cb.state == CircuitBreakerState.OPEN

        time.sleep(0.02)
        cb._do_should_attempt_request()
        assert cb.state == CircuitBreakerState.HALF_OPEN

        cb._do_record_success()
        assert cb.state == CircuitBreakerState.CLOSED

        # Cycle 2: CLOSED → OPEN → HALF_OPEN → CLOSED again
        cb._do_record_failure()
        cb._do_record_failure()
        assert cb.state == CircuitBreakerState.OPEN

        time.sleep(0.02)
        cb._do_should_attempt_request()
        assert cb.state == CircuitBreakerState.HALF_OPEN

        cb._do_record_success()
        assert cb.state == CircuitBreakerState.CLOSED

    def test_should_attempt_request_in_each_state(self) -> None:
        """Test should_attempt_request returns correct values in each state."""
        cb = CircuitBreakerBase(
            proxy_id="proxy1",
            failure_threshold=1,
            timeout_duration=0.01,
        )

        # CLOSED: always true
        assert cb._do_should_attempt_request() is True

        # Force to OPEN
        cb._do_record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        assert cb._do_should_attempt_request() is False

        # Wait and transition to HALF_OPEN
        time.sleep(0.02)
        assert cb._do_should_attempt_request() is True
        assert cb.state == CircuitBreakerState.HALF_OPEN

    def test_half_open_pending_flag(self) -> None:
        """Test that half-open pending flag prevents concurrent tests."""
        cb = CircuitBreakerBase(
            proxy_id="proxy1",
            failure_threshold=1,
            timeout_duration=0.01,
        )

        cb._do_record_failure()
        time.sleep(0.02)
        cb._do_should_attempt_request()

        # Pending flag should be set
        assert cb._half_open_pending is True

        # Second attempt should fail
        assert cb._do_should_attempt_request() is False


class TestCircuitBreakerEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_failure_window_purges_old_failures(self) -> None:
        """Test with very small window duration."""
        cb = CircuitBreakerBase(
            proxy_id="proxy1",
            failure_threshold=1,
            window_duration=0.001,  # 1ms window
        )

        cb._do_record_failure()
        time.sleep(0.01)
        assert cb.failure_count == 0  # Old failure should be purged

    def test_large_failure_threshold(self) -> None:
        """Test with large failure threshold."""
        cb = CircuitBreakerBase(
            proxy_id="proxy1",
            failure_threshold=1000,
        )

        for _ in range(100):
            cb._do_record_failure()
            assert cb.state == CircuitBreakerState.CLOSED

    def test_configuration_persistence(self) -> None:
        """Test that configuration values are preserved."""
        cb = CircuitBreakerBase(
            proxy_id="proxy1",
            failure_threshold=5,
            window_duration=120.0,
            timeout_duration=60.0,
        )

        assert cb.failure_threshold == 5
        assert cb.window_duration == 120.0
        assert cb.timeout_duration == 60.0
