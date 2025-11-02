"""
Unit tests for CircuitBreaker.
"""

import time
from unittest.mock import patch

import pytest

from proxywhirl.circuit_breaker import CircuitBreaker, CircuitBreakerState


class TestCircuitBreakerRecordFailure:
    """Test CircuitBreaker.record_failure() method."""

    def test_record_single_failure_stays_closed(self):
        """Test that a single failure keeps circuit breaker CLOSED."""
        cb = CircuitBreaker(proxy_id="test-proxy", failure_threshold=5)

        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0

        cb.record_failure()

        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 1

    def test_record_failures_opens_circuit(self):
        """Test that threshold failures open the circuit."""
        cb = CircuitBreaker(proxy_id="test-proxy", failure_threshold=3)

        # Record 2 failures - should stay closed
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 2

        # Record 3rd failure - should open
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        assert cb.failure_count == 3

    def test_rolling_window_cleanup(self):
        """Test that old failures are removed from rolling window."""
        cb = CircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=3,
            window_duration=2.0,  # 2 second window
        )

        # Record 2 failures
        with patch("time.time", return_value=100.0):
            cb.record_failure()
            cb.record_failure()

        assert cb.failure_count == 2

        # Wait for window to expire (mock time + 3 seconds)
        with patch("time.time", return_value=103.0):
            cb.record_failure()  # This should clean up old failures

        # Only the latest failure should count (old ones expired)
        assert cb.failure_count == 1
        assert cb.state == CircuitBreakerState.CLOSED

    def test_failure_in_half_open_reopens_circuit(self):
        """Test that failure in HALF_OPEN state reopens the circuit."""
        cb = CircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=2,
            timeout_duration=1.0,
        )

        # Open the circuit
        with patch("time.time", return_value=100.0):
            cb.record_failure()
            cb.record_failure()

        assert cb.state == CircuitBreakerState.OPEN

        # Transition to half-open
        with patch("time.time", return_value=101.0):
            cb.should_attempt_request()

        assert cb.state == CircuitBreakerState.HALF_OPEN

        # Record failure in half-open state
        with patch("time.time", return_value=101.5):
            cb.record_failure()

        # Should reopen
        assert cb.state == CircuitBreakerState.OPEN


class TestCircuitBreakerRecordSuccess:
    """Test CircuitBreaker.record_success() method."""

    def test_success_in_closed_state_no_change(self):
        """Test that success in CLOSED state doesn't change state."""
        cb = CircuitBreaker(proxy_id="test-proxy")

        assert cb.state == CircuitBreakerState.CLOSED

        cb.record_success()

        assert cb.state == CircuitBreakerState.CLOSED

    def test_success_in_half_open_closes_circuit(self):
        """Test that success in HALF_OPEN state closes the circuit."""
        cb = CircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=2,
            timeout_duration=1.0,
        )

        # Open the circuit
        with patch("time.time", return_value=100.0):
            cb.record_failure()
            cb.record_failure()

        assert cb.state == CircuitBreakerState.OPEN
        assert cb.failure_count == 2

        # Transition to half-open
        with patch("time.time", return_value=101.0):
            cb.should_attempt_request()

        assert cb.state == CircuitBreakerState.HALF_OPEN

        # Record success
        cb.record_success()

        # Should close and reset
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0
        assert len(cb.failure_window) == 0


class TestCircuitBreakerShouldAttemptRequest:
    """Test CircuitBreaker.should_attempt_request() method."""

    def test_closed_allows_requests(self):
        """Test that CLOSED state allows requests."""
        cb = CircuitBreaker(proxy_id="test-proxy")

        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.should_attempt_request() is True

    def test_open_blocks_requests(self):
        """Test that OPEN state blocks requests before timeout."""
        cb = CircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=2,
            timeout_duration=10.0,
        )

        # Open the circuit
        with patch("time.time", return_value=100.0):
            cb.record_failure()
            cb.record_failure()

        assert cb.state == CircuitBreakerState.OPEN

        # Immediately check - should block
        with patch("time.time", return_value=100.5):
            assert cb.should_attempt_request() is False

        # After 5 seconds (still before timeout) - should block
        with patch("time.time", return_value=105.0):
            assert cb.should_attempt_request() is False

    def test_open_transitions_to_half_open_after_timeout(self):
        """Test that OPEN state transitions to HALF_OPEN after timeout."""
        cb = CircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=2,
            timeout_duration=5.0,
        )

        # Open the circuit at time 100
        with patch("time.time", return_value=100.0):
            cb.record_failure()
            cb.record_failure()

        assert cb.state == CircuitBreakerState.OPEN
        assert cb.next_test_time == 105.0

        # Check at time 105 (timeout elapsed)
        with patch("time.time", return_value=105.0):
            result = cb.should_attempt_request()

        assert result is True
        assert cb.state == CircuitBreakerState.HALF_OPEN

    def test_half_open_allows_requests(self):
        """Test that HALF_OPEN state allows requests."""
        cb = CircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=2,
            timeout_duration=1.0,
        )

        # Open and transition to half-open
        with patch("time.time", return_value=100.0):
            cb.record_failure()
            cb.record_failure()

        with patch("time.time", return_value=101.0):
            cb.should_attempt_request()

        assert cb.state == CircuitBreakerState.HALF_OPEN
        assert cb.should_attempt_request() is True


class TestCircuitBreakerStateTransitions:
    """Test CircuitBreaker state transition logic."""

    def test_full_lifecycle_closed_to_open_to_half_open_to_closed(self):
        """Test complete circuit breaker lifecycle."""
        cb = CircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=3,
            window_duration=60.0,
            timeout_duration=10.0,
        )

        # Start CLOSED
        assert cb.state == CircuitBreakerState.CLOSED

        # Record failures to open circuit
        with patch("time.time", return_value=100.0):
            cb.record_failure()
            cb.record_failure()
            cb.record_failure()

        # Now OPEN
        assert cb.state == CircuitBreakerState.OPEN
        assert cb.next_test_time == 110.0

        # Wait for timeout
        with patch("time.time", return_value=110.0):
            cb.should_attempt_request()

        # Now HALF_OPEN
        assert cb.state == CircuitBreakerState.HALF_OPEN

        # Record success
        cb.record_success()

        # Now CLOSED
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0

    def test_half_open_to_open_on_failure(self):
        """Test HALF_OPEN reopens on failure."""
        cb = CircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=2,
            timeout_duration=5.0,
        )

        # Open circuit
        with patch("time.time", return_value=100.0):
            cb.record_failure()
            cb.record_failure()

        # Transition to half-open
        with patch("time.time", return_value=105.0):
            cb.should_attempt_request()

        assert cb.state == CircuitBreakerState.HALF_OPEN

        # Record failure (should reopen)
        with patch("time.time", return_value=105.5):
            cb.record_failure()

        assert cb.state == CircuitBreakerState.OPEN
        # New timeout should be set
        assert cb.next_test_time == 110.5  # 105.5 + 5.0


class TestCircuitBreakerReset:
    """Test CircuitBreaker.reset() method."""

    def test_reset_from_open_state(self):
        """Test manual reset from OPEN state."""
        cb = CircuitBreaker(proxy_id="test-proxy", failure_threshold=2)

        # Open the circuit
        cb.record_failure()
        cb.record_failure()

        assert cb.state == CircuitBreakerState.OPEN
        assert cb.failure_count == 2

        # Reset
        cb.reset()

        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0
        assert len(cb.failure_window) == 0
        assert cb.next_test_time is None

    def test_reset_from_half_open_state(self):
        """Test manual reset from HALF_OPEN state."""
        cb = CircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=2,
            timeout_duration=1.0,
        )

        # Open and transition to half-open
        with patch("time.time", return_value=100.0):
            cb.record_failure()
            cb.record_failure()

        with patch("time.time", return_value=101.0):
            cb.should_attempt_request()

        assert cb.state == CircuitBreakerState.HALF_OPEN

        # Reset
        cb.reset()

        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0


class TestCircuitBreakerThreadSafety:
    """Test CircuitBreaker thread safety."""

    def test_concurrent_failure_recording(self):
        """Test that concurrent failure recording is thread-safe."""
        import threading

        cb = CircuitBreaker(proxy_id="test-proxy", failure_threshold=100)

        def record_failures():
            for _ in range(10):
                cb.record_failure()

        # Create 10 threads, each recording 10 failures
        threads = [threading.Thread(target=record_failures) for _ in range(10)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Should have exactly 100 failures
        assert cb.failure_count == 100

    def test_concurrent_state_transitions(self):
        """Test concurrent state transitions don't cause race conditions."""
        import threading

        cb = CircuitBreaker(
            proxy_id="test-proxy",
            failure_threshold=5,
            timeout_duration=1.0,
        )

        results = []

        def record_and_check():
            with patch("time.time", return_value=100.0):
                cb.record_failure()
                results.append(cb.state)

        # Create multiple threads recording failures
        threads = [threading.Thread(target=record_and_check) for _ in range(10)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Circuit should be open (threshold is 5, we recorded 10 failures)
        assert cb.state == CircuitBreakerState.OPEN
