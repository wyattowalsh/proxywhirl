"""
Base circuit breaker implementation with shared state machine logic.

This module provides the core state machine logic shared between
sync (CircuitBreaker) and async (AsyncCircuitBreaker) implementations.
"""

from __future__ import annotations

import asyncio
import time
from collections import deque
from datetime import datetime, timezone
from enum import Enum
from threading import Lock
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from proxywhirl.models import CircuitBreakerConfig


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
    half_open_probe_timeout: float = Field(
        default=30.0,
        gt=0,
        description="Seconds before an abandoned HALF_OPEN probe slot is released",
    )
    next_test_time: float | None = None
    last_state_change: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Flag to prevent multiple concurrent test requests in HALF_OPEN state
    _half_open_pending: bool = PrivateAttr(default=False)
    _half_open_probe_acquired_at: float | None = PrivateAttr(default=None)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    _MIN_REALISTIC_EPOCH = 946684800.0  # 2000-01-01 UTC

    def _prune_failure_window_at(self, now: float) -> None:
        """Drop failures that have aged out of the rolling window at a known time."""
        cutoff = now - self.window_duration
        while self.failure_window and self.failure_window[0] < cutoff:
            self.failure_window.popleft()
        self.failure_count = len(self.failure_window)

    def _clear_stale_half_open_probe(self, now: float) -> None:
        """Release abandoned HALF_OPEN probe reservations after the probe timeout."""
        if not self._half_open_pending:
            return
        if self._half_open_probe_acquired_at is None:
            return
        if now - self._half_open_probe_acquired_at >= self.half_open_probe_timeout:
            self._half_open_pending = False
            self._half_open_probe_acquired_at = None

    def _do_is_eligible(self, now: float) -> bool:
        """Pure eligibility check (no state transitions, no probe acquisition)."""
        self._prune_failure_window_at(now)
        self._clear_stale_half_open_probe(now)

        if self.state == CircuitBreakerState.CLOSED:
            return True
        if self.state == CircuitBreakerState.OPEN:
            return self.next_test_time is not None and now >= self.next_test_time
        return not self._half_open_pending

    def _do_try_acquire_probe(self, now: float) -> bool:
        """Reserve a probe slot; may transition OPEN → HALF_OPEN."""
        self._clear_stale_half_open_probe(now)

        if self.state == CircuitBreakerState.CLOSED:
            return True
        if self.state == CircuitBreakerState.OPEN:
            if self.next_test_time and now >= self.next_test_time:
                self._transition_to_half_open()
                self._half_open_pending = True
                self._half_open_probe_acquired_at = now
                return True
            return False
        if self._half_open_pending:
            return False
        self._half_open_pending = True
        self._half_open_probe_acquired_at = now
        return True

    def _do_record_failure(self) -> None:
        """Core failure recording logic (call while holding lock)."""
        now = time.time()

        # Remove failures outside rolling window
        self._prune_failure_window_at(now)

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
            self._half_open_probe_acquired_at = None
            self._transition_to_open(now)

    def _do_record_success(self) -> None:
        """Core success recording logic (call while holding lock)."""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self._half_open_pending = False
            self._half_open_probe_acquired_at = None
            self._transition_to_closed()

    def _do_should_attempt_request(self) -> bool:
        """Acquire a probe when eligible (legacy combined check)."""
        now = time.time()
        if not self._do_is_eligible(now):
            return False
        return self._do_try_acquire_probe(now)

    def _do_reset(self) -> None:
        """Core reset logic (call while holding lock)."""
        self._half_open_pending = False
        self._half_open_probe_acquired_at = None
        self._transition_to_closed()

    def _transition_to_open(self, now: float) -> None:
        """Transition to OPEN state."""
        self.state = CircuitBreakerState.OPEN
        self.next_test_time = now + self.timeout_duration
        self.last_state_change = datetime.now(timezone.utc)
        self._half_open_pending = False
        self._half_open_probe_acquired_at = None

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
        self._half_open_probe_acquired_at = None


class CircuitBreaker(CircuitBreakerBase):
    """Circuit breaker for a single proxy in synchronous contexts."""

    _lock: Lock = PrivateAttr(default_factory=Lock)

    def record_failure(self) -> None:
        """Record a failure and update state if threshold reached."""
        with self._lock:
            self._do_record_failure()

    def record_success(self) -> None:
        """Record a success and potentially close circuit."""
        with self._lock:
            self._do_record_success()

    def is_eligible(self) -> bool:
        """Return whether the proxy may be considered for selection (no side effects)."""
        with self._lock:
            return self._do_is_eligible(time.time())

    def try_acquire_probe(self) -> bool:
        """Reserve an in-flight probe slot when eligible (mutates HALF_OPEN pending)."""
        with self._lock:
            now = time.time()
            if not self._do_is_eligible(now):
                return False
            return self._do_try_acquire_probe(now)

    def should_attempt_request(self) -> bool:
        """Check eligibility and acquire a probe slot for an actual request."""
        with self._lock:
            return self._do_should_attempt_request()

    def reset(self) -> None:
        """Manually reset circuit breaker to CLOSED state."""
        with self._lock:
            self._do_reset()

    @classmethod
    def create(
        cls,
        proxy_id: str,
        config: CircuitBreakerConfig | None = None,
        **kwargs: Any,
    ) -> CircuitBreaker:
        """Create a circuit breaker with optional config."""
        if config:
            failure_threshold = kwargs.pop("failure_threshold", config.failure_threshold)
            window_duration = kwargs.pop("window_duration", config.window_duration)
            timeout_duration = kwargs.pop("timeout_duration", config.timeout_duration)
            half_open_probe_timeout = kwargs.pop(
                "half_open_probe_timeout",
                config.timeout_duration,
            )

            return cls(
                proxy_id=proxy_id,
                failure_threshold=failure_threshold,
                window_duration=window_duration,
                timeout_duration=timeout_duration,
                half_open_probe_timeout=half_open_probe_timeout,
                **kwargs,
            )
        return cls(proxy_id=proxy_id, **kwargs)


class AsyncCircuitBreaker(CircuitBreakerBase):
    """Circuit breaker for a single proxy in async contexts."""

    _lock: asyncio.Lock = PrivateAttr(default_factory=asyncio.Lock)

    async def record_failure(self) -> None:
        """Record a failure and update state if threshold reached."""
        async with self._lock:
            self._do_record_failure()

    async def record_success(self) -> None:
        """Record a success and potentially close circuit."""
        async with self._lock:
            self._do_record_success()

    async def is_eligible(self) -> bool:
        """Return whether the proxy may be considered for selection (no side effects)."""
        async with self._lock:
            return self._do_is_eligible(time.time())

    async def try_acquire_probe(self) -> bool:
        """Reserve an in-flight probe slot when eligible (mutates HALF_OPEN pending)."""
        async with self._lock:
            now = time.time()
            if not self._do_is_eligible(now):
                return False
            return self._do_try_acquire_probe(now)

    async def should_attempt_request(self) -> bool:
        """Check eligibility and acquire a probe slot for an actual request."""
        async with self._lock:
            return self._do_should_attempt_request()

    async def reset(self) -> None:
        """Manually reset circuit breaker to CLOSED state."""
        async with self._lock:
            self._do_reset()

    @classmethod
    def create(
        cls,
        proxy_id: str,
        config: CircuitBreakerConfig | None = None,
        **kwargs: Any,
    ) -> AsyncCircuitBreaker:
        """Create an async circuit breaker with optional config."""
        if config:
            failure_threshold = kwargs.pop("failure_threshold", config.failure_threshold)
            window_duration = kwargs.pop("window_duration", config.window_duration)
            timeout_duration = kwargs.pop("timeout_duration", config.timeout_duration)
            half_open_probe_timeout = kwargs.pop(
                "half_open_probe_timeout",
                config.timeout_duration,
            )

            return cls(
                proxy_id=proxy_id,
                failure_threshold=failure_threshold,
                window_duration=window_duration,
                timeout_duration=timeout_duration,
                half_open_probe_timeout=half_open_probe_timeout,
                **kwargs,
            )
        return cls(proxy_id=proxy_id, **kwargs)
