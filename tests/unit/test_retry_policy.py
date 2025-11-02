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

    def test_jitter_adds_randomness(self):
        """Test jitter adds randomness to delay."""
        policy = RetryPolicy(
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            base_delay=4.0,
            multiplier=2.0,
            jitter=True,
        )

        # Calculate delay multiple times for the same attempt
        delays = [policy.calculate_delay(0) for _ in range(100)]

        # Base delay for attempt 0 is 4.0
        # With jitter, it should be between 2.0 (4.0 * 0.5) and 6.0 (4.0 * 1.5)
        assert all(2.0 <= d <= 6.0 for d in delays)

        # Delays should vary (not all the same)
        assert len(set(delays)) > 1

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
