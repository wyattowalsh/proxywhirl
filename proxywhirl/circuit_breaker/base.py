"""
Base circuit breaker implementation with shared state machine logic.

This module provides the core state machine logic shared between
sync (CircuitBreaker) and async (AsyncCircuitBreaker) implementations.
"""

from __future__ import annotations

import time
from collections import deque
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, PrivateAttr


class CircuitBreakerState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation, proxy available
    OPEN = "open"  # Proxy excluded from rotation
    HALF_OPEN = "half_open"  # Testing recovery with limited requests


class CircuitBreakerBase(BaseModel):
    """Base circuit breaker with shared state machine logic.

    This class contains all the state management logic shared between
    sync and async implementations. Subclasses provide the locking mechanism.

    Attributes:
        proxy_id: Unique identifier for the proxy
        state: Current circuit breaker state (CLOSED, OPEN, HALF_OPEN)
        failure_count: Number of failures in current window
        failure_threshold: Number of failures before opening circuit
        window_duration: Rolling window duration in seconds
        timeout_duration: How long circuit stays open before testing recovery
    """

    proxy_id: str
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = Field(default=0, ge=0)
    failure_window: deque[float] = Field(default_factory=lambda: deque(maxlen=10000))
    failure_threshold: int = Field(default=5, ge=1)
    window_duration: float = Field(default=60.0, gt=0)
    timeout_duration: float = Field(default=30.0, gt=0)
    next_test_time: float | None = None
    last_state_change: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Flag to prevent multiple concurrent test requests in HALF_OPEN state
    _half_open_pending: bool = PrivateAttr(default=False)

    class Config:
        arbitrary_types_allowed = True

    def _do_record_failure(self) -> None:
        """Core failure recording logic (call while holding lock)."""
        now = time.time()

        # Remove failures outside rolling window
        cutoff = now - self.window_duration
        while self.failure_window and self.failure_window[0] < cutoff:
            self.failure_window.popleft()

        # Add failure to window
        self.failure_window.append(now)
        self.failure_count = len(self.failure_window)

        # Transition to OPEN if threshold exceeded
        if (
            self.state == CircuitBreakerState.CLOSED
            and self.failure_count >= self.failure_threshold
        ):
            self._transition_to_open(now)
        elif self.state == CircuitBreakerState.HALF_OPEN:
            # Test failed, reopen circuit
            self._half_open_pending = False
            self._transition_to_open(now)

    def _do_record_success(self) -> None:
        """Core success recording logic (call while holding lock)."""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self._half_open_pending = False
            self._transition_to_closed()

    def _do_should_attempt_request(self) -> bool:
        """Core request attempt check logic (call while holding lock)."""
        now = time.time()

        if self.state == CircuitBreakerState.CLOSED:
            return True
        elif self.state == CircuitBreakerState.OPEN:
            if self.next_test_time and now >= self.next_test_time:
                self._transition_to_half_open()
                self._half_open_pending = True
                return True
            return False
        else:  # HALF_OPEN
            if self._half_open_pending:
                return False
            self._half_open_pending = True
            return True

    def _do_reset(self) -> None:
        """Core reset logic (call while holding lock)."""
        self._half_open_pending = False
        self._transition_to_closed()

    def _transition_to_open(self, now: float) -> None:
        """Transition to OPEN state."""
        self.state = CircuitBreakerState.OPEN
        self.next_test_time = now + self.timeout_duration
        self.last_state_change = datetime.now(timezone.utc)
        self._half_open_pending = False

    def _transition_to_half_open(self) -> None:
        """Transition to HALF_OPEN state."""
        self.state = CircuitBreakerState.HALF_OPEN
        self.last_state_change = datetime.now(timezone.utc)

    def _transition_to_closed(self) -> None:
        """Transition to CLOSED state."""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.failure_window.clear()
        self.next_test_time = None
        self.last_state_change = datetime.now(timezone.utc)
        self._half_open_pending = False
