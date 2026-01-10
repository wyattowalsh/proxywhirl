"""
Unit tests for RetryPolicy.
"""

import pytest

from proxywhirl.retry_policy import BackoffStrategy, RetryPolicy


class TestRetryPolicyValidation:
    """Test RetryPolicy Pydantic validation."""

    def test_valid_policy_creation(self):
        """Test creating a valid retry policy."""
        policy = RetryPolicy(
            max_attempts=5,
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            base_delay=2.0,
            multiplier=3.0,
            max_backoff_delay=60.0,
            jitter=True,
            retry_status_codes=[502, 503, 504],
        )

        assert policy.max_attempts == 5
        assert policy.backoff_strategy == BackoffStrategy.EXPONENTIAL
        assert policy.base_delay == 2.0
        assert policy.multiplier == 3.0
        assert policy.jitter is True

    def test_default_values(self):
        """Test default values are applied correctly."""
        policy = RetryPolicy()

        assert policy.max_attempts == 3
        assert policy.backoff_strategy == BackoffStrategy.EXPONENTIAL
        assert policy.base_delay == 1.0
        assert policy.multiplier == 2.0
        assert policy.max_backoff_delay == 30.0
        assert policy.jitter is False
        assert policy.retry_status_codes == [502, 503, 504]
        assert policy.timeout is None
        assert policy.retry_non_idempotent is False

    def test_invalid_status_codes(self):
        """Test validation rejects non-5xx status codes."""
        with pytest.raises(ValueError, match="Status codes must be 5xx errors"):
            RetryPolicy(retry_status_codes=[200, 404, 502])

    def test_max_attempts_range(self):
        """Test max_attempts must be in valid range."""
        # Too low
        with pytest.raises(ValueError):
            RetryPolicy(max_attempts=0)

        # Too high
        with pytest.raises(ValueError):
            RetryPolicy(max_attempts=11)

        # Valid boundaries
        RetryPolicy(max_attempts=1)  # Min valid
        RetryPolicy(max_attempts=10)  # Max valid

    def test_base_delay_range(self):
        """Test base_delay validation."""
        # Too low
        with pytest.raises(ValueError):
            RetryPolicy(base_delay=0.0)

        # Too high
        with pytest.raises(ValueError):
            RetryPolicy(base_delay=61.0)

        # Valid boundaries
        RetryPolicy(base_delay=0.1)  # Min valid
        RetryPolicy(base_delay=60.0)  # Max valid

    def test_multiplier_range(self):
        """Test multiplier validation."""
        # Too low
        with pytest.raises(ValueError):
            RetryPolicy(multiplier=1.0)

        # Too high
        with pytest.raises(ValueError):
            RetryPolicy(multiplier=11.0)

        # Valid boundaries
        RetryPolicy(multiplier=1.1)  # Min valid
        RetryPolicy(multiplier=10.0)  # Max valid


class TestRetryPolicyCalculateDelay:
    """Test RetryPolicy.calculate_delay() method."""

    def test_exponential_backoff_no_jitter(self):
        """Test exponential backoff calculation without jitter."""
        policy = RetryPolicy(
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            base_delay=1.0,
            multiplier=2.0,
            jitter=False,
        )

        # Attempt 0: 1.0 * (2.0 ^ 0) = 1.0
        assert policy.calculate_delay(0) == 1.0

        # Attempt 1: 1.0 * (2.0 ^ 1) = 2.0
        assert policy.calculate_delay(1) == 2.0

        # Attempt 2: 1.0 * (2.0 ^ 2) = 4.0
        assert policy.calculate_delay(2) == 4.0

        # Attempt 3: 1.0 * (2.0 ^ 3) = 8.0
        assert policy.calculate_delay(3) == 8.0

    def test_linear_backoff_no_jitter(self):
        """Test linear backoff calculation without jitter."""
        policy = RetryPolicy(
            backoff_strategy=BackoffStrategy.LINEAR,
            base_delay=2.0,
            jitter=False,
        )

        # Attempt 0: 2.0 * (0 + 1) = 2.0
        assert policy.calculate_delay(0) == 2.0

        # Attempt 1: 2.0 * (1 + 1) = 4.0
        assert policy.calculate_delay(1) == 4.0

        # Attempt 2: 2.0 * (2 + 1) = 6.0
        assert policy.calculate_delay(2) == 6.0

        # Attempt 3: 2.0 * (3 + 1) = 8.0
        assert policy.calculate_delay(3) == 8.0

    def test_fixed_backoff_no_jitter(self):
        """Test fixed backoff calculation without jitter."""
        policy = RetryPolicy(
            backoff_strategy=BackoffStrategy.FIXED,
            base_delay=3.0,
            jitter=False,
        )

        # All attempts should return base_delay
        assert policy.calculate_delay(0) == 3.0
        assert policy.calculate_delay(1) == 3.0
        assert policy.calculate_delay(2) == 3.0
        assert policy.calculate_delay(10) == 3.0

    def test_exponential_backoff_with_cap(self):
        """Test exponential backoff respects max_backoff_delay cap."""
        policy = RetryPolicy(
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            base_delay=1.0,
            multiplier=2.0,
            max_backoff_delay=5.0,  # Cap at 5 seconds
            jitter=False,
        )

        # Attempt 0: 1.0 (no cap needed)
        assert policy.calculate_delay(0) == 1.0

        # Attempt 1: 2.0 (no cap needed)
        assert policy.calculate_delay(1) == 2.0

        # Attempt 2: 4.0 (no cap needed)
        assert policy.calculate_delay(2) == 4.0

        # Attempt 3: would be 8.0, but capped at 5.0
        assert policy.calculate_delay(3) == 5.0

        # Attempt 4: would be 16.0, but capped at 5.0
        assert policy.calculate_delay(4) == 5.0

    def test_jitter_first_attempt_spreads_delays(self):
        """Test first attempt jitter spreads delays from 0 to base delay."""
        policy = RetryPolicy(
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            base_delay=4.0,
            multiplier=2.0,
            jitter=True,
        )

        # Calculate delay multiple times for the first attempt (no previous_delay)
        delays = [policy.calculate_delay(0) for _ in range(100)]

        # First attempt with jitter: uniform(0, min(base, max_backoff_delay))
        # Base for attempt 0 is 4.0, so delays should be in [0, 4.0)
        assert all(0 <= d <= 4.0 for d in delays)

        # Delays should vary (not all the same)
        assert len(set(delays)) > 1

        # Check reasonable spread across the range
        min_delay = min(delays)
        max_delay = max(delays)
        assert max_delay - min_delay > 1.0  # Should have reasonable spread

    def test_decorrelated_jitter_depends_on_previous_delay(self):
        """Test decorrelated jitter depends on previous delay value."""
        policy = RetryPolicy(
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            base_delay=1.0,
            multiplier=2.0,
            max_backoff_delay=30.0,
            jitter=True,
        )

        # With small previous_delay, range is [base_delay, previous_delay * 3]
        small_previous = 2.0
        delays_small = [
            policy.calculate_delay(1, previous_delay=small_previous) for _ in range(100)
        ]
        # Range should be [1.0, 6.0]
        assert all(1.0 <= d <= 6.0 for d in delays_small)

        # With larger previous_delay, range expands
        large_previous = 10.0
        delays_large = [
            policy.calculate_delay(1, previous_delay=large_previous) for _ in range(100)
        ]
        # Range should be [1.0, 30.0] (capped at max_backoff_delay)
        assert all(1.0 <= d <= 30.0 for d in delays_large)

        # Larger previous should produce larger average delay
        avg_small = sum(delays_small) / len(delays_small)
        avg_large = sum(delays_large) / len(delays_large)
        assert avg_large > avg_small

    def test_decorrelated_jitter_respects_max_backoff_cap(self):
        """Test decorrelated jitter respects max_backoff_delay cap."""
        policy = RetryPolicy(
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            base_delay=1.0,
            multiplier=2.0,
            max_backoff_delay=5.0,  # Low cap
            jitter=True,
        )

        # Even with very large previous_delay, cap is respected
        large_previous = 100.0
        delays = [policy.calculate_delay(2, previous_delay=large_previous) for _ in range(100)]

        # All delays must be <= max_backoff_delay
        assert all(d <= 5.0 for d in delays)
        # Delays should still be >= base_delay
        assert all(d >= 1.0 for d in delays)

    def test_decorrelated_jitter_statistical_distribution(self):
        """Test decorrelated jitter produces well-distributed delays."""
        policy = RetryPolicy(
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            base_delay=1.0,
            multiplier=2.0,
            max_backoff_delay=30.0,
            jitter=True,
        )

        # Simulate a sequence of retries with decorrelated jitter
        previous_delay = None
        all_delays = []

        for _ in range(1000):
            delay = policy.calculate_delay(1, previous_delay=previous_delay)
            all_delays.append(delay)
            previous_delay = delay

        # Check distribution properties
        min_d = min(all_delays)
        max_d = max(all_delays)

        # Delays should cover a range (not clustered)
        assert max_d - min_d > 5.0  # Reasonable spread

        # Check that we don't have synchronized values (thundering herd prevention)
        unique_delays = {round(d, 2) for d in all_delays}
        assert len(unique_delays) > 100  # Many distinct values

    def test_decorrelated_jitter_first_vs_subsequent_attempts(self):
        """Test first attempt uses different logic than subsequent attempts."""
        policy = RetryPolicy(
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            base_delay=2.0,
            multiplier=2.0,
            jitter=True,
        )

        # First attempt (no previous_delay): uniform(0, base)
        first_delays = [policy.calculate_delay(0) for _ in range(100)]
        assert all(0 <= d <= 2.0 for d in first_delays)  # Range is [0, base]

        # Subsequent attempt with previous_delay: uniform(base, previous * 3)
        subsequent_delays = [policy.calculate_delay(1, previous_delay=2.0) for _ in range(100)]
        assert all(2.0 <= d <= 6.0 for d in subsequent_delays)  # Range is [base, prev*3]

    def test_linear_backoff_with_cap(self):
        """Test linear backoff respects max_backoff_delay cap."""
        policy = RetryPolicy(
            backoff_strategy=BackoffStrategy.LINEAR,
            base_delay=5.0,
            max_backoff_delay=12.0,
            jitter=False,
        )

        # Attempt 0: 5.0
        assert policy.calculate_delay(0) == 5.0

        # Attempt 1: 10.0
        assert policy.calculate_delay(1) == 10.0

        # Attempt 2: would be 15.0, but capped at 12.0
        assert policy.calculate_delay(2) == 12.0

        # Attempt 3: would be 20.0, but capped at 12.0
        assert policy.calculate_delay(3) == 12.0
