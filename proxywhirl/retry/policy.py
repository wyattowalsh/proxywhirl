"""
Retry policy configuration and backoff strategies.
"""

from __future__ import annotations

import random
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class BackoffStrategy(str, Enum):
    """Retry backoff timing strategy."""

    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIXED = "fixed"


class RetryPolicy(BaseModel):
    """Configuration for retry behavior."""

    max_attempts: int = Field(default=3, ge=1, le=10)
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL
    base_delay: float = Field(default=1.0, gt=0, le=60)
    multiplier: float = Field(default=2.0, gt=1, le=10)
    max_backoff_delay: float = Field(default=30.0, gt=0, le=300)
    jitter: bool = Field(default=False)
    retry_status_codes: list[int] = Field(default=[502, 503, 504])
    timeout: float | None = Field(default=None, gt=0)
    retry_non_idempotent: bool = Field(default=False)

    @field_validator("retry_status_codes")
    @classmethod
    def validate_status_codes(cls, v: list[int]) -> list[int]:
        """Validate that status codes are 5xx errors."""
        if not all(500 <= code < 600 for code in v):
            raise ValueError("Status codes must be 5xx errors")
        return v

    def calculate_delay(self, attempt: int, previous_delay: float | None = None) -> float:
        """
        Calculate delay for given attempt number (0-indexed).

        Uses AWS decorrelated jitter algorithm when jitter is enabled to prevent
        the thundering herd problem. The decorrelated jitter ensures that retry
        delays depend on previous delay values, spreading retries across time.

        AWS decorrelated jitter formula:
            delay = min(cap, random(base, previous_delay * 3))

        Reference: https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/

        Args:
            attempt: The attempt number (0 for first retry, 1 for second, etc.)
            previous_delay: The delay from the previous attempt (for decorrelated jitter).
                          If None and jitter is enabled, uses base_delay as seed.

        Returns:
            Delay in seconds before the next retry attempt
        """
        if self.backoff_strategy == BackoffStrategy.EXPONENTIAL:
            base = self.base_delay * (self.multiplier**attempt)
        elif self.backoff_strategy == BackoffStrategy.LINEAR:
            base = self.base_delay * (attempt + 1)
        else:  # FIXED
            base = self.base_delay

        # Apply decorrelated jitter if enabled (AWS algorithm)
        if self.jitter:
            if previous_delay is not None:
                # AWS decorrelated jitter: delay = min(cap, random(base, previous * 3))
                # This ensures delays are spread out and depend on previous delay
                delay = min(
                    self.max_backoff_delay,
                    random.uniform(self.base_delay, previous_delay * 3),
                )
            else:
                # First attempt with jitter: use uniform distribution from 0 to base
                # This spreads initial retries across the time window
                delay = random.uniform(0, min(base, self.max_backoff_delay))
        else:
            # No jitter: use deterministic delay capped at max
            delay = min(base, self.max_backoff_delay)

        return delay
