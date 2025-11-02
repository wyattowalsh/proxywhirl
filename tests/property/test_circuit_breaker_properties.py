"""
Property-based tests for CircuitBreaker state machine with Hypothesis.
"""

import time
from unittest.mock import patch

from hypothesis import given, strategies as st

from proxywhirl.circuit_breaker import CircuitBreaker, CircuitBreakerState


@given(
    failure_sequence=st.lists(
        st.booleans(),
        min_size=1,
        max_size=20,
    ),
    failure_threshold=st.integers(min_value=1, max_value=10),
)
def test_circuit_breaker_state_invariants(
    failure_sequence: list[bool],
    failure_threshold: int,
) -> None:
    """Property: Circuit breaker state transitions follow invariants."""
    cb = CircuitBreaker(
        proxy_id="test-proxy",
        failure_threshold=failure_threshold,
        window_duration=100.0,
        timeout_duration=10.0,
    )

    consecutive_failures = 0
    current_time = 100.0

    for is_success in failure_sequence:
        with patch("time.time", return_value=current_time):
            if is_success:
                cb.record_success()
                consecutive_failures = 0
            else:
                cb.record_failure()
                consecutive_failures += 1

        # Invariant 1: If failures >= threshold, circuit should be OPEN or HALF_OPEN
        if consecutive_failures >= failure_threshold:
            assert cb.state in (CircuitBreakerState.OPEN, CircuitBreakerState.HALF_OPEN)

        # Invariant 2: Failure count should never exceed window size
        assert cb.failure_count <= len(failure_sequence)

        # Invariant 3: If state is CLOSED, should allow requests
        if cb.state == CircuitBreakerState.CLOSED:
            assert cb.should_attempt_request() is True

        current_time += 1.0


@given(
    num_failures=st.integers(min_value=1, max_value=50),
    failure_threshold=st.integers(min_value=1, max_value=10),
)
def test_circuit_opens_after_threshold_failures(
    num_failures: int,
    failure_threshold: int,
) -> None:
    """Property: Circuit opens after threshold failures."""
    cb = CircuitBreaker(
        proxy_id="test-proxy",
        failure_threshold=failure_threshold,
        window_duration=100.0,
    )

    with patch("time.time", return_value=100.0):
        for _ in range(num_failures):
            cb.record_failure()

    if num_failures >= failure_threshold:
        assert cb.state == CircuitBreakerState.OPEN
    else:
        assert cb.state == CircuitBreakerState.CLOSED


@given(
    failure_threshold=st.integers(min_value=2, max_value=10),
    timeout_duration=st.floats(min_value=1.0, max_value=60.0),
)
def test_circuit_transitions_to_half_open_after_timeout(
    failure_threshold: int,
    timeout_duration: float,
) -> None:
    """Property: Circuit transitions to HALF_OPEN after timeout."""
    cb = CircuitBreaker(
        proxy_id="test-proxy",
        failure_threshold=failure_threshold,
        timeout_duration=timeout_duration,
    )

    # Open the circuit
    with patch("time.time", return_value=100.0):
        for _ in range(failure_threshold):
            cb.record_failure()

    assert cb.state == CircuitBreakerState.OPEN

    # Check after timeout
    with patch("time.time", return_value=100.0 + timeout_duration):
        cb.should_attempt_request()

    assert cb.state == CircuitBreakerState.HALF_OPEN


@given(
    failure_threshold=st.integers(min_value=2, max_value=10),
)
def test_success_in_half_open_closes_circuit(
    failure_threshold: int,
) -> None:
    """Property: Success in HALF_OPEN always closes circuit."""
    cb = CircuitBreaker(
        proxy_id="test-proxy",
        failure_threshold=failure_threshold,
        timeout_duration=10.0,
    )

    # Open the circuit
    with patch("time.time", return_value=100.0):
        for _ in range(failure_threshold):
            cb.record_failure()

    # Transition to half-open
    with patch("time.time", return_value=110.0):
        cb.should_attempt_request()

    assert cb.state == CircuitBreakerState.HALF_OPEN

    # Record success
    cb.record_success()

    assert cb.state == CircuitBreakerState.CLOSED
    assert cb.failure_count == 0


@given(
    failure_threshold=st.integers(min_value=2, max_value=10),
)
def test_failure_in_half_open_reopens_circuit(
    failure_threshold: int,
) -> None:
    """Property: Failure in HALF_OPEN always reopens circuit."""
    cb = CircuitBreaker(
        proxy_id="test-proxy",
        failure_threshold=failure_threshold,
        timeout_duration=10.0,
    )

    # Open the circuit
    with patch("time.time", return_value=100.0):
        for _ in range(failure_threshold):
            cb.record_failure()

    # Transition to half-open
    with patch("time.time", return_value=110.0):
        cb.should_attempt_request()

    assert cb.state == CircuitBreakerState.HALF_OPEN

    # Record failure
    with patch("time.time", return_value=111.0):
        cb.record_failure()

    assert cb.state == CircuitBreakerState.OPEN


@given(
    window_duration=st.floats(min_value=1.0, max_value=120.0),
    failure_threshold=st.integers(min_value=3, max_value=10),
)
def test_old_failures_expire_from_window(
    window_duration: float,
    failure_threshold: int,
) -> None:
    """Property: Failures outside window don't count toward threshold."""
    cb = CircuitBreaker(
        proxy_id="test-proxy",
        failure_threshold=failure_threshold,
        window_duration=window_duration,
    )

    # Record failures at time 100
    with patch("time.time", return_value=100.0):
        for _ in range(failure_threshold - 1):
            cb.record_failure()

    # Circuit should still be closed (one below threshold)
    assert cb.state == CircuitBreakerState.CLOSED

    # Record one more failure after window expires
    with patch("time.time", return_value=100.0 + window_duration + 1.0):
        cb.record_failure()

    # Should still be closed (old failures expired)
    assert cb.state == CircuitBreakerState.CLOSED
    assert cb.failure_count == 1
