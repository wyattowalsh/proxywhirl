"""Tests for retry backoff strategies."""

from __future__ import annotations

import asyncio
import random
import time
from enum import Enum

import pytest


class BackoffStrategy(Enum):
    """Backoff strategy types."""

    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    FIBONACCI = "fibonacci"
    RANDOM = "random"


class RetryBackoff:
    """Manages retry backoff logic."""

    def __init__(self, strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL) -> None:
        """Initialize backoff."""
        self.strategy = strategy
        self.attempt = 0
        self.max_wait = 60.0

    def get_delay(self) -> float:
        """Get delay for next retry."""
        self.attempt += 1

        if self.strategy == BackoffStrategy.LINEAR:
            delay = self.attempt
        elif self.strategy == BackoffStrategy.EXPONENTIAL:
            delay = 2 ** (self.attempt - 1)
        elif self.strategy == BackoffStrategy.FIBONACCI:
            delay = self._fibonacci(self.attempt)
        elif self.strategy == BackoffStrategy.RANDOM:
            delay = random.uniform(1, 10)
        else:
            delay = 1

        return min(delay, self.max_wait)

    def _fibonacci(self, n: int) -> float:
        """Calculate fibonacci value."""
        if n <= 1:
            return float(n)
        a, b = 0, 1
        for _ in range(n - 1):
            a, b = b, a + b
        return float(b)

    def reset(self) -> None:
        """Reset retry counter."""
        self.attempt = 0


class TestSourceRetryBackoff:
    """Test retry backoff strategies."""

    def test_linear_backoff(self) -> None:
        """Test linear backoff."""
        backoff = RetryBackoff(BackoffStrategy.LINEAR)

        assert backoff.get_delay() == 1
        assert backoff.get_delay() == 2
        assert backoff.get_delay() == 3
        assert backoff.get_delay() == 4

    def test_exponential_backoff(self) -> None:
        """Test exponential backoff."""
        backoff = RetryBackoff(BackoffStrategy.EXPONENTIAL)

        assert backoff.get_delay() == 1
        assert backoff.get_delay() == 2
        assert backoff.get_delay() == 4
        assert backoff.get_delay() == 8
        assert backoff.get_delay() == 16

    def test_fibonacci_backoff(self) -> None:
        """Test fibonacci backoff."""
        backoff = RetryBackoff(BackoffStrategy.FIBONACCI)

        delays = [backoff.get_delay() for _ in range(6)]
        # Fibonacci: 1, 1, 2, 3, 5, 8
        assert delays[0] == 1
        assert delays[1] == 1
        assert delays[2] == 2
        assert delays[3] == 3
        assert delays[4] == 5
        assert delays[5] == 8

    def test_random_backoff(self) -> None:
        """Test random backoff."""
        backoff = RetryBackoff(BackoffStrategy.RANDOM)

        for _ in range(5):
            delay = backoff.get_delay()
            assert 1 <= delay <= 10

    def test_max_wait_clamp(self) -> None:
        """Test max wait clamping."""
        backoff = RetryBackoff(BackoffStrategy.EXPONENTIAL)
        backoff.max_wait = 5.0

        backoff.get_delay()  # 1
        backoff.get_delay()  # 2
        backoff.get_delay()  # 4
        delay = backoff.get_delay()  # Would be 8, clamped to 5
        assert delay == 5.0

    def test_reset_backoff(self) -> None:
        """Test resetting backoff."""
        backoff = RetryBackoff(BackoffStrategy.EXPONENTIAL)

        backoff.get_delay()  # 1
        backoff.get_delay()  # 2
        backoff.reset()

        assert backoff.get_delay() == 1

    def test_multiple_strategy_instances(self) -> None:
        """Test multiple backoff instances."""
        linear = RetryBackoff(BackoffStrategy.LINEAR)
        exponential = RetryBackoff(BackoffStrategy.EXPONENTIAL)

        linear_delay = linear.get_delay()
        exp_delay = exponential.get_delay()

        assert linear_delay == 1
        assert exp_delay == 1

    def test_backoff_increases(self) -> None:
        """Test backoff increases with retries."""
        backoff = RetryBackoff(BackoffStrategy.EXPONENTIAL)

        delays = [backoff.get_delay() for _ in range(5)]
        for i in range(len(delays) - 1):
            assert delays[i] <= delays[i + 1]

    def test_attempt_tracking(self) -> None:
        """Test attempt counter."""
        backoff = RetryBackoff(BackoffStrategy.LINEAR)

        assert backoff.attempt == 0
        backoff.get_delay()
        assert backoff.attempt == 1
        backoff.get_delay()
        assert backoff.attempt == 2

    def test_jitter_randomness(self) -> None:
        """Test random strategy produces different values."""
        backoff = RetryBackoff(BackoffStrategy.RANDOM)

        values = [backoff.get_delay() for _ in range(10)]
        # At least some variation
        assert len(set(values)) > 1

    @pytest.mark.asyncio
    async def test_async_backoff_sleep(self) -> None:
        """Test async sleep with backoff."""
        backoff = RetryBackoff(BackoffStrategy.LINEAR)

        start = time.time()
        delay = backoff.get_delay()
        await asyncio.sleep(delay)
        elapsed = time.time() - start

        assert elapsed >= delay

    def test_max_wait_constraint(self) -> None:
        """Test max wait is respected."""
        backoff = RetryBackoff(BackoffStrategy.EXPONENTIAL)
        backoff.max_wait = 2.0

        for _ in range(10):
            delay = backoff.get_delay()
            assert delay <= 2.0
