"""
Async circuit breaker implementation with RWLock for reduced contention.

This is the new async-first implementation that uses AsyncRWLock for
better performance in high-concurrency scenarios.
"""

from __future__ import annotations

import asyncio
import time
from collections import deque
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field, PrivateAttr

from proxywhirl.models import CircuitBreakerConfig
from proxywhirl.rwlock import AsyncRWLock

if TYPE_CHECKING:
    from proxywhirl.storage import SQLiteStorage


class CircuitBreakerState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation, proxy available
    OPEN = "open"  # Proxy excluded from rotation
    HALF_OPEN = "half_open"  # Testing recovery with limited requests


class AsyncCircuitBreaker(BaseModel):
    """Async circuit breaker for a single proxy with RWLock for high concurrency.

    This is the ASYNCHRONOUS implementation designed for async/await contexts.
    Uses AsyncRWLock (from proxywhirl.rwlock) for event-loop-safe operations
    with reduced lock contention compared to simple asyncio.Lock.

    Key Features:
        - Event-loop safe: All methods are async and use asyncio-compatible locks
        - High concurrency: RWLock allows multiple readers or single writer
        - State persistence: Optional async storage backend for crash recovery
        - Zero blocking: Never blocks the event loop with synchronous operations

    For synchronous contexts, use CircuitBreaker from circuit_breaker module instead.

    Attributes:
        proxy_id: Unique identifier for the proxy
        state: Current circuit breaker state (CLOSED, OPEN, HALF_OPEN)
        failure_count: Number of failures in current window
        failure_threshold: Number of failures before opening circuit
        window_duration: Rolling window duration in seconds
        timeout_duration: How long circuit stays open before testing recovery
        persist_state: Enable state persistence to storage

    Example:
        >>> from proxywhirl.circuit_breaker_async import AsyncCircuitBreaker
        >>> cb = AsyncCircuitBreaker(proxy_id="proxy-1")
        >>> await cb.record_failure()  # Event-loop safe
        >>> if await cb.should_attempt_request():
        ...     # make async request
        ...     await cb.record_success()
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
    persist_state: bool = Field(default=False, description="Enable state persistence")

    # Runtime lock (not serialized) - RWLock for reduced contention
    _lock: AsyncRWLock = PrivateAttr(default_factory=AsyncRWLock)
    _half_open_pending: bool = PrivateAttr(default=False)
    _storage: SQLiteStorage | None = PrivateAttr(default=None)

    class Config:
        arbitrary_types_allowed = True  # For AsyncRWLock and deque

    async def record_failure(self) -> None:
        """Record a failure and update state if threshold reached."""
        async with self._lock.write_lock():
            now = time.time()

            # Remove failures outside rolling window FIRST
            cutoff = now - self.window_duration
            while self.failure_window and self.failure_window[0] < cutoff:
                self.failure_window.popleft()

            # Add failure to window AFTER cleaning
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

    async def record_success(self) -> None:
        """Record a success and potentially close circuit."""
        async with self._lock.write_lock():
            if self.state == CircuitBreakerState.HALF_OPEN:
                # Test succeeded, close circuit
                self._half_open_pending = False
                self._transition_to_closed()

    async def should_attempt_request(self) -> bool:
        """Check if proxy is available for requests.

        Uses write lock throughout to prevent lock upgrade race conditions.
        While this reduces concurrency for reads, it ensures state consistency
        and prevents TOCTOU (Time-of-Check to Time-of-Use) bugs.
        """
        async with self._lock.write_lock():
            now = time.time()

            if self.state == CircuitBreakerState.CLOSED:
                return True
            elif self.state == CircuitBreakerState.OPEN:
                # Check if timeout elapsed, transition to half-open
                if self.next_test_time and now >= self.next_test_time:
                    self._transition_to_half_open()
                    self._half_open_pending = True
                    return True
                return False
            else:  # HALF_OPEN
                # Only allow one test request at a time
                if self._half_open_pending:
                    return False
                self._half_open_pending = True
                return True

    def _transition_to_open(self, now: float) -> None:
        """Transition to OPEN state."""
        self.state = CircuitBreakerState.OPEN
        self.next_test_time = now + self.timeout_duration
        self.last_state_change = datetime.now(timezone.utc)
        self._schedule_persist()

    def _transition_to_half_open(self) -> None:
        """Transition to HALF_OPEN state."""
        self.state = CircuitBreakerState.HALF_OPEN
        self.last_state_change = datetime.now(timezone.utc)
        self._schedule_persist()

    def _transition_to_closed(self) -> None:
        """Transition to CLOSED state."""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.failure_window.clear()
        self.next_test_time = None
        self.last_state_change = datetime.now(timezone.utc)
        self._schedule_persist()

    def _schedule_persist(self) -> None:
        """Schedule state persistence in background (non-blocking)."""
        if not self.persist_state or self._storage is None:
            return

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.save_state())
        except RuntimeError:
            pass  # No event loop running

    async def reset(self) -> None:
        """Manually reset circuit breaker to CLOSED state."""
        async with self._lock.write_lock():
            self._half_open_pending = False
            self._transition_to_closed()

    def set_storage(self, storage: SQLiteStorage | None) -> None:
        """Set the storage backend for state persistence."""
        self._storage = storage

    @classmethod
    async def create_with_storage(
        cls,
        proxy_id: str,
        storage: SQLiteStorage | None = None,
        config: CircuitBreakerConfig | None = None,
        **kwargs: Any,
    ) -> AsyncCircuitBreaker:
        """Factory method to create a circuit breaker with optional state restoration."""
        # Build circuit breaker with explicit parameters
        # Start with defaults from config if provided, otherwise use class defaults
        if config:
            # Extract config-controlled parameters from kwargs if present (for override)
            failure_threshold = kwargs.pop("failure_threshold", config.failure_threshold)
            window_duration = kwargs.pop("window_duration", config.window_duration)
            timeout_duration = kwargs.pop("timeout_duration", config.timeout_duration)
            persist_state = kwargs.pop("persist_state", config.persist_state)

            cb = cls(
                proxy_id=proxy_id,
                persist_state=persist_state,
                failure_threshold=failure_threshold,
                window_duration=window_duration,
                timeout_duration=timeout_duration,
                **kwargs,  # Any remaining kwargs
            )
        else:
            cb = cls(
                proxy_id=proxy_id,
                **kwargs,  # Use class defaults unless overridden
            )

        if storage:
            cb.set_storage(storage)

        if cb.persist_state and storage:
            await cb.load_state()

        return cb

    async def save_state(self) -> None:
        """Save current circuit breaker state to storage."""
        if not self.persist_state or self._storage is None:
            return

        import json

        from sqlmodel import delete
        from sqlmodel.ext.asyncio.session import AsyncSession

        from proxywhirl.storage import CircuitBreakerStateTable

        async with self._lock.read_lock():
            # Serialize failure window to JSON
            failure_window_list = list(self.failure_window)
            failure_window_json = json.dumps(failure_window_list)

            # Create state record
            now = datetime.now(timezone.utc)
            state_record = CircuitBreakerStateTable(
                proxy_id=self.proxy_id,
                state=self.state.value,
                failure_count=self.failure_count,
                failure_window_json=failure_window_json,
                next_test_time=self.next_test_time,
                last_state_change=self.last_state_change,
                failure_threshold=self.failure_threshold,
                window_duration=self.window_duration,
                timeout_duration=self.timeout_duration,
                created_at=now,
                updated_at=now,
            )

        # Perform database operation outside lock
        async with AsyncSession(self._storage.engine) as session:
            stmt = delete(CircuitBreakerStateTable).where(
                CircuitBreakerStateTable.proxy_id == self.proxy_id  # type: ignore[arg-type]
            )
            await session.exec(stmt)
            session.add(state_record)
            await session.commit()

    async def load_state(self) -> bool:
        """Load circuit breaker state from storage."""
        if not self.persist_state or self._storage is None:
            return False

        import json

        from sqlmodel import select
        from sqlmodel.ext.asyncio.session import AsyncSession

        from proxywhirl.storage import CircuitBreakerStateTable

        async with AsyncSession(self._storage.engine) as session:
            stmt = select(CircuitBreakerStateTable).where(
                CircuitBreakerStateTable.proxy_id == self.proxy_id  # type: ignore[arg-type]
            )
            result = await session.exec(stmt)
            state_record = result.first()

            if state_record is None:
                return False

            failure_window_list = json.loads(state_record.failure_window_json)

            async with self._lock.write_lock():
                self.state = CircuitBreakerState(state_record.state)
                self.failure_count = state_record.failure_count
                self.failure_window = deque(failure_window_list)
                self.next_test_time = state_record.next_test_time
                self.last_state_change = state_record.last_state_change
                self.failure_threshold = state_record.failure_threshold
                self.window_duration = state_record.window_duration
                self.timeout_duration = state_record.timeout_duration

            return True

    async def delete_state(self) -> None:
        """Delete persisted state from storage."""
        if not self.persist_state or self._storage is None:
            return

        from sqlmodel import delete
        from sqlmodel.ext.asyncio.session import AsyncSession

        from proxywhirl.storage import CircuitBreakerStateTable

        async with AsyncSession(self._storage.engine) as session:
            stmt = delete(CircuitBreakerStateTable).where(
                CircuitBreakerStateTable.proxy_id == self.proxy_id  # type: ignore[arg-type]
            )
            await session.exec(stmt)
            await session.commit()
