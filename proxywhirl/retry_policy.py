"""
Retry policy configuration and backoff strategies.
"""

import random
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class BackoffStrategy(str, Enum):
    """Retry backoff timing strategy."""

    EXPONENTIAL = "exponential"
    LINEAR      = "linear"
    FIXED       = "fixed"


class RetryPolicy(BaseModel):
    """Configuration for retry behavior."""

    max_attempts:        int             = Field(default=3, ge=1, le=10)
    backoff_strategy:    BackoffStrategy = BackoffStrategy.EXPONENTIAL
    base_delay:          float           = Field(default=1.0, gt=0, le=60)
    multiplier:          float           = Field(default=2.0, gt=1, le=10)
    max_backoff_delay:   float           = Field(default=30.0, gt=0, le=300)
    jitter:              bool            = Field(default=False)
    retry_status_codes:  list[int]       = Field(default=[502, 503, 504])
    timeout:             Optional[float] = Field(default=None, gt=0)
    retry_non_idempotent: bool           = Field(default=False)

    @field_validator("retry_status_codes")
    @classmethod
    def validate_status_codes(cls, v: list[int]) -> list[int]:
        """Validate that status codes are 5xx errors."""
        if not all(500 <= code < 600 for code in v):
            raise ValueError("Status codes must be 5xx errors")
        return v

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for given attempt number (0-indexed).

        Args:
            attempt: The attempt number (0 for first retry, 1 for second, etc.)

        Returns:
            Delay in seconds before the next retry attempt
        """
        if self.backoff_strategy == BackoffStrategy.EXPONENTIAL:
            delay = self.base_delay * (self.multiplier**attempt)
        elif self.backoff_strategy == BackoffStrategy.LINEAR:
            delay = self.base_delay * (attempt + 1)
        else:  # FIXED
            delay = self.base_delay

        # Cap at max delay
        delay = min(delay, self.max_backoff_delay)

        # Apply jitter if enabled
        if self.jitter:
            delay = delay * random.uniform(0.5, 1.5)

        return delay
