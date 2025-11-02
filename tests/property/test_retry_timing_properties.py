"""
Property-based tests for retry timing with Hypothesis.
"""

from hypothesis import given, strategies as st

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

    assert delay <= max_backoff_delay, (
        f"Delay {delay} exceeds max {max_backoff_delay}"
    )


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
    """Property: Jitter keeps delay within 50%-150% of calculated delay."""
    policy = RetryPolicy(
        backoff_strategy=BackoffStrategy.EXPONENTIAL,
        base_delay=base_delay,
        multiplier=multiplier,
        max_backoff_delay=max_backoff_delay,
        jitter=True,
    )

    # Calculate delays multiple times
    delays = [policy.calculate_delay(attempt) for _ in range(10)]

    # All delays should be positive and within max
    assert all(0 < d <= max_backoff_delay for d in delays)

    # Without jitter, what would the delay be?
    policy_no_jitter = RetryPolicy(
        backoff_strategy=BackoffStrategy.EXPONENTIAL,
        base_delay=base_delay,
        multiplier=multiplier,
        max_backoff_delay=max_backoff_delay,
        jitter=False,
    )
    base_calculated = policy_no_jitter.calculate_delay(attempt)

    # With jitter, delays should be between 50% and 150% of base
    min_expected = base_calculated * 0.5
    max_expected = min(base_calculated * 1.5, max_backoff_delay)

    for delay in delays:
        assert min_expected <= delay <= max_expected, (
            f"Delay {delay} outside jitter bounds [{min_expected}, {max_expected}]"
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
        max_backoff_delay=1000.0,  # High cap to test monotonicity
        jitter=False,
    )

    # Calculate delays for first 5 attempts
    delays = [policy.calculate_delay(i) for i in range(5)]

    # Should be strictly increasing (or equal if capped)
    for i in range(len(delays) - 1):
        assert delays[i] <= delays[i + 1], (
            f"Delay decreased: {delays[i]} -> {delays[i + 1]}"
        )


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
        max_backoff_delay=1000.0,  # High cap
        jitter=False,
    )

    # Calculate delays for first 5 attempts
    delays = [policy.calculate_delay(i) for i in range(5)]

    # Should be strictly increasing
    for i in range(len(delays) - 1):
        assert delays[i] < delays[i + 1], (
            f"Delay not increasing: {delays[i]} -> {delays[i + 1]}"
        )


@given(
    attempt=st.integers(min_value=0, max_value=10),
)
def test_delay_always_positive(attempt: int) -> None:
    """Property: Delay is always positive."""
    policy = RetryPolicy()

    delay = policy.calculate_delay(attempt)

    assert delay > 0
