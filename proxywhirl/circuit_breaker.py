"""
Circuit breaker pattern implementation for proxy failure management.
"""

import time
from collections import deque
from datetime import datetime, timezone
from enum import Enum
from threading import Lock
from typing import Deque

from pydantic import BaseModel, Field


class CircuitBreakerState(str, Enum):
    """Circuit breaker states."""

    CLOSED    = "closed"      # Normal operation, proxy available
    OPEN      = "open"        # Proxy excluded from rotation
    HALF_OPEN = "half_open"   # Testing recovery with limited requests


class CircuitBreaker(BaseModel):
    """Circuit breaker for a single proxy."""

    proxy_id:         str
    state:            CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count:    int                 = Field(default=0, ge=0)
    failure_window:   Deque[float]        = Field(default_factory=deque)
    failure_threshold: int                = Field(default=5, ge=1)
    window_duration:  float               = Field(default=60.0, gt=0)
    timeout_duration: float               = Field(default=30.0, gt=0)
    next_test_time:   float | None        = None
    last_state_change: datetime           = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # Runtime lock (not serialized)
    _lock: Lock = Field(default_factory=Lock, exclude=True, repr=False)

    class Config:
        arbitrary_types_allowed = True  # For Lock and deque

    def record_failure(self) -> None:
        """Record a failure and update state if threshold reached."""
        with self._lock:
            now = time.time()

            # Add failure to window
            self.failure_window.append(now)

            # Remove failures outside rolling window
            cutoff = now - self.window_duration
            while self.failure_window and self.failure_window[0] < cutoff:
                self.failure_window.popleft()

            self.failure_count = len(self.failure_window)

            # Transition to OPEN if threshold exceeded
            if (
                self.state == CircuitBreakerState.CLOSED
                and self.failure_count >= self.failure_threshold
            ):
                self._transition_to_open(now)
            elif self.state == CircuitBreakerState.HALF_OPEN:
                # Test failed, reopen circuit
                self._transition_to_open(now)

    def record_success(self) -> None:
        """Record a success and potentially close circuit."""
        with self._lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                # Test succeeded, close circuit
                self._transition_to_closed()

    def should_attempt_request(self) -> bool:
        """Check if proxy is available for requests."""
        with self._lock:
            now = time.time()

            if self.state == CircuitBreakerState.CLOSED:
                return True
            elif self.state == CircuitBreakerState.OPEN:
                # Check if timeout elapsed, transition to half-open
                if self.next_test_time and now >= self.next_test_time:
                    self._transition_to_half_open()
                    return True
                return False
            else:  # HALF_OPEN
                return True

    def _transition_to_open(self, now: float) -> None:
        """Transition to OPEN state."""
        self.state             = CircuitBreakerState.OPEN
        self.next_test_time    = now + self.timeout_duration
        self.last_state_change = datetime.now(timezone.utc)

    def _transition_to_half_open(self) -> None:
        """Transition to HALF_OPEN state."""
        self.state             = CircuitBreakerState.HALF_OPEN
        self.last_state_change = datetime.now(timezone.utc)

    def _transition_to_closed(self) -> None:
        """Transition to CLOSED state."""
        self.state             = CircuitBreakerState.CLOSED
        self.failure_count     = 0
        self.failure_window.clear()
        self.next_test_time    = None
        self.last_state_change = datetime.now(timezone.utc)

    def reset(self) -> None:
        """Manually reset circuit breaker to CLOSED state."""
        with self._lock:
            self._transition_to_closed()
