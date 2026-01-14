"""
Property-based tests for retry timing with Hypothesis.
"""

from hypothesis import given
from hypothesis import strategies as st

from proxywhirl.retry_policy import BackoffStrategy, RetryPolicy


@given(
    base_delay=st.floats(min_value=0.1, max_value=60.0),
    multiplier=st.floats(min_value=1.1, max_value=10.0),
    max_backoff_delay=st.floats(min_value=1.0, max_value=300.0),
    attempt=st.integers(min_value=0, max_value=10),
)
def test_exponential_backoff_never_exceeds_max(
    base_delay: float,
    multiplier: float,
    max_backoff_delay: float,
    attempt: int,
) -> None:
    """Property: Exponential backoff delay never exceeds max_backoff_delay."""
    policy = RetryPolicy(
        backoff_strategy=BackoffStrategy.EXPONENTIAL,
        base_delay=base_delay,
        multiplier=multiplier,
        max_backoff_delay=max_backoff_delay,
        jitter=False,
    )

    delay = policy.calculate_delay(attempt)

    assert delay <= max_backoff_delay, f"Delay {delay} exceeds max {max_backoff_delay}"


@given(
    base_delay=st.floats(min_value=0.1, max_value=60.0),
    max_backoff_delay=st.floats(min_value=1.0, max_value=300.0),
    attempt=st.integers(min_value=0, max_value=10),
)
def test_linear_backoff_never_exceeds_max(
    base_delay: float,
    max_backoff_delay: float,
    attempt: int,
) -> None:
    """Property: Linear backoff delay never exceeds max_backoff_delay."""
    policy = RetryPolicy(
        backoff_strategy=BackoffStrategy.LINEAR,
        base_delay=base_delay,
        max_backoff_delay=max_backoff_delay,
        jitter=False,
    )

    delay = policy.calculate_delay(attempt)

    assert delay <= max_backoff_delay


@given(
    base_delay=st.floats(min_value=0.1, max_value=60.0),
    max_backoff_delay=st.floats(min_value=1.0, max_value=300.0),
    attempt=st.integers(min_value=0, max_value=10),
)
def test_fixed_backoff_always_returns_base_delay(
    base_delay: float,
    max_backoff_delay: float,
    attempt: int,
) -> None:
    """Property: Fixed backoff always returns base_delay (or max if lower)."""
    policy = RetryPolicy(
        backoff_strategy=BackoffStrategy.FIXED,
        base_delay=base_delay,
        max_backoff_delay=max_backoff_delay,
        jitter=False,
    )

    delay = policy.calculate_delay(attempt)

    expected = min(base_delay, max_backoff_delay)
    assert delay == expected


@given(
    base_delay=st.floats(min_value=0.1, max_value=60.0),
    multiplier=st.floats(min_value=1.1, max_value=10.0),
    max_backoff_delay=st.floats(min_value=1.0, max_value=300.0),
    attempt=st.integers(min_value=0, max_value=10),
)
def test_jitter_stays_within_bounds(
    base_delay: float,
    multiplier: float,
    max_backoff_delay: float,
    attempt: int,
) -> None:
    """Property: AWS decorrelated jitter stays within expected bounds.

    The AWS decorrelated jitter algorithm works as follows:
    - First attempt (no previous_delay): uniform(0, min(base, max_backoff_delay))
    - Subsequent attempts: min(cap, uniform(base_delay, previous_delay * 3))

    For first attempts without previous_delay, delays are in [0, base].
    """
    policy = RetryPolicy(
        backoff_strategy=BackoffStrategy.EXPONENTIAL,
        base_delay=base_delay,
        multiplier=multiplier,
        max_backoff_delay=max_backoff_delay,
        jitter=True,
    )

    # Test first attempt without previous_delay
    first_delays = [policy.calculate_delay(attempt) for _ in range(10)]

    # Calculate the base delay for this attempt
    base_calculated = base_delay * (multiplier**attempt)
    expected_max = min(base_calculated, max_backoff_delay)

    # First attempts with jitter: uniform(0, min(base_calculated, max_backoff_delay))
    # All delays should be non-negative and within expected_max
    for delay in first_delays:
        assert 0 <= delay <= expected_max, (
            f"First attempt delay {delay} outside bounds [0, {expected_max}]"
        )

    # Test decorrelated jitter with previous_delay
    # Use a small previous_delay that's guaranteed to work with the cap
    previous_delay = min(base_delay, max_backoff_delay)
    correlated_delays = [
        policy.calculate_delay(attempt, previous_delay=previous_delay) for _ in range(10)
    ]

    # Decorrelated jitter: min(cap, uniform(base_delay, previous_delay * 3))
    # The lower bound is base_delay, but if base_delay > max_backoff_delay,
    # all delays are capped at max_backoff_delay
    correlated_min = min(base_delay, max_backoff_delay)
    correlated_max = min(max_backoff_delay, previous_delay * 3)

    for delay in correlated_delays:
        assert correlated_min <= delay <= correlated_max, (
            f"Correlated delay {delay} outside bounds [{correlated_min}, {correlated_max}]"
        )


@given(
    base_delay=st.floats(min_value=0.1, max_value=60.0),
    multiplier=st.floats(min_value=1.1, max_value=10.0),
)
def test_exponential_backoff_is_monotonic_until_cap(
    base_delay: float,
    multiplier: float,
) -> None:
    """Property: Exponential backoff increases monotonically until cap."""
    policy = RetryPolicy(
        backoff_strategy=BackoffStrategy.EXPONENTIAL,
        base_delay=base_delay,
        multiplier=multiplier,
        max_backoff_delay=300.0,  # Max allowed by RetryPolicy validation
        jitter=False,
    )

    # Calculate delays for first 5 attempts
    delays = [policy.calculate_delay(i) for i in range(5)]

    # Should be strictly increasing (or equal if capped)
    for i in range(len(delays) - 1):
        assert delays[i] <= delays[i + 1], f"Delay decreased: {delays[i]} -> {delays[i + 1]}"


@given(
    base_delay=st.floats(min_value=0.1, max_value=60.0),
)
def test_linear_backoff_is_strictly_monotonic(
    base_delay: float,
) -> None:
    """Property: Linear backoff increases strictly monotonically."""
    policy = RetryPolicy(
        backoff_strategy=BackoffStrategy.LINEAR,
        base_delay=base_delay,
        max_backoff_delay=300.0,  # Max allowed by RetryPolicy validation
        jitter=False,
    )

    # Calculate delays for first 5 attempts
    delays = [policy.calculate_delay(i) for i in range(5)]

    # Should be strictly increasing
    for i in range(len(delays) - 1):
        assert delays[i] < delays[i + 1], f"Delay not increasing: {delays[i]} -> {delays[i + 1]}"


@given(
    attempt=st.integers(min_value=0, max_value=10),
)
def test_delay_always_positive(attempt: int) -> None:
    """Property: Delay is always positive."""
    policy = RetryPolicy()

    delay = policy.calculate_delay(attempt)

    assert delay > 0
