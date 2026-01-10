"""
Circuit breaker pattern implementation for proxy failure management.

IMPORTANT: This module provides SYNCHRONOUS circuit breaker implementation.

Usage Guidelines:
-----------------
- CircuitBreaker: Use in synchronous contexts only (threading.Lock)
- AsyncCircuitBreaker: Use in async contexts (from circuit_breaker_async module)

The CircuitBreaker class uses threading.Lock for thread-safety and is designed
for synchronous code. For async applications, use AsyncCircuitBreaker which
uses asyncio-compatible locks and provides true async/await support.

Example:
    Synchronous usage:
        >>> cb = CircuitBreaker(proxy_id="proxy-1")
        >>> cb.record_failure()  # Thread-safe
        >>> if cb.should_attempt_request():
        ...     # make request
        ...     cb.record_success()

    Async usage (use AsyncCircuitBreaker instead):
        >>> from proxywhirl.circuit_breaker_async import AsyncCircuitBreaker
        >>> cb = AsyncCircuitBreaker(proxy_id="proxy-1")
        >>> await cb.record_failure()  # Event loop safe
        >>> if await cb.should_attempt_request():
        ...     # make async request
        ...     await cb.record_success()
"""

from __future__ import annotations

import time
from collections import deque
from datetime import datetime, timezone
from enum import Enum
from threading import Lock
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field, PrivateAttr

from proxywhirl.models import CircuitBreakerConfig

if TYPE_CHECKING:
    from proxywhirl.storage import SQLiteStorage


class CircuitBreakerState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation, proxy available
    OPEN = "open"  # Proxy excluded from rotation
    HALF_OPEN = "half_open"  # Testing recovery with limited requests


class CircuitBreaker(BaseModel):
    """Circuit breaker for a single proxy (SYNCHRONOUS implementation).

    WARNING: This class uses threading.Lock and is designed for SYNCHRONOUS contexts only.
    For async applications, use AsyncCircuitBreaker from circuit_breaker_async module.

    The sync methods (record_failure, record_success, should_attempt_request, reset)
    are thread-safe using threading.Lock. The async methods (save_state, load_state,
    delete_state) are provided for I/O operations but should NOT be mixed with
    async event loops in production - use AsyncCircuitBreaker instead.

    Attributes:
        proxy_id: Unique identifier for the proxy
        state: Current circuit breaker state (CLOSED, OPEN, HALF_OPEN)
        failure_count: Number of failures in current window
        failure_threshold: Number of failures before opening circuit
        window_duration: Rolling window duration in seconds
        timeout_duration: How long circuit stays open before testing recovery
        persist_state: Enable state persistence to storage
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

    # Runtime lock (not serialized)
    _lock: Lock = PrivateAttr(default_factory=Lock)
    _storage: SQLiteStorage | None = PrivateAttr(default=None)
    # Flag to prevent multiple concurrent test requests in HALF_OPEN state
    _half_open_pending: bool = PrivateAttr(default=False)

    class Config:
        arbitrary_types_allowed = True  # For Lock and deque

    def record_failure(self) -> None:
        """Record a failure and update state if threshold reached.

        Thread-safe - acquires threading.Lock for the entire operation.
        For async contexts, use AsyncCircuitBreaker.record_failure() instead.
        """
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
        """Record a success and potentially close circuit.

        Thread-safe - acquires threading.Lock for the entire operation.
        For async contexts, use AsyncCircuitBreaker.record_success() instead.
        """
        with self._lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                # Test succeeded, close circuit
                self._transition_to_closed()

    def should_attempt_request(self) -> bool:
        """Check if proxy is available for requests.

        Thread-safe - acquires threading.Lock for the entire operation.
        For async contexts, use AsyncCircuitBreaker.should_attempt_request() instead.

        In HALF_OPEN state, only one test request is allowed at a time.
        The _half_open_pending flag ensures that concurrent threads
        are blocked until the test request completes.

        Returns:
            True if proxy should be attempted, False if circuit is open.
        """
        with self._lock:
            now = time.time()

            if self.state == CircuitBreakerState.CLOSED:
                return True
            elif self.state == CircuitBreakerState.OPEN:
                # Check if timeout elapsed, transition to half-open
                if self.next_test_time and now >= self.next_test_time:
                    self._transition_to_half_open()
                    # Set flag to indicate a test request is in progress
                    self._half_open_pending = True
                    return True
                return False
            else:  # HALF_OPEN
                # Only allow one test request at a time in HALF_OPEN state
                if self._half_open_pending:
                    return False
                self._half_open_pending = True
                return True

    def _transition_to_open(self, now: float) -> None:
        """Transition to OPEN state."""
        self.state = CircuitBreakerState.OPEN
        self.next_test_time = now + self.timeout_duration
        self.last_state_change = datetime.now(timezone.utc)
        # Reset half-open pending flag when leaving HALF_OPEN state
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
        # Reset half-open pending flag when leaving HALF_OPEN state
        self._half_open_pending = False

    def reset(self) -> None:
        """Manually reset circuit breaker to CLOSED state.

        Thread-safe - acquires threading.Lock before resetting state.
        For async contexts, use AsyncCircuitBreaker.reset() which is an async method.
        """
        with self._lock:
            self._transition_to_closed()

    def set_storage(self, storage: SQLiteStorage | None) -> None:
        """Set the storage backend for state persistence.

        Args:
            storage: SQLite storage instance, or None to disable persistence
        """
        self._storage = storage

    @classmethod
    async def create_with_storage(
        cls,
        proxy_id: str,
        storage: SQLiteStorage | None = None,
        config: CircuitBreakerConfig | None = None,
        **kwargs: Any,
    ) -> CircuitBreaker:
        """Factory method to create a circuit breaker with optional state restoration.

        WARNING: This is an async method on a SYNC class. For production async applications,
        use AsyncCircuitBreaker.create_with_storage() from circuit_breaker_async module instead.

        This method is provided for backward compatibility and simple async I/O operations,
        but mixing sync locks (threading.Lock) with async code can block the event loop.

        Args:
            proxy_id: Unique identifier for the proxy
            storage: SQLite storage instance for persistence
            config: CircuitBreakerConfig with persistence settings
            **kwargs: Additional CircuitBreaker field overrides

        Returns:
            CircuitBreaker instance with restored state (if available)

        Example (prefer AsyncCircuitBreaker for async code):
            >>> # For sync contexts:
            >>> storage = SQLiteStorage("proxywhirl.db")
            >>> await storage.initialize()
            >>> config = CircuitBreakerConfig(persist_state=True)
            >>> cb = await CircuitBreaker.create_with_storage(
            ...     proxy_id="proxy-1",
            ...     storage=storage,
            ...     config=config
            ... )
            >>>
            >>> # For async contexts, use this instead:
            >>> from proxywhirl.circuit_breaker_async import AsyncCircuitBreaker
            >>> cb = await AsyncCircuitBreaker.create_with_storage(...)
        """
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

        # Set storage
        if storage:
            cb.set_storage(storage)

        # Try to restore state
        if cb.persist_state and storage:
            await cb.load_state()

        return cb

    async def save_state(self) -> None:
        """Save current circuit breaker state to storage.

        WARNING: This async method uses threading.Lock which can block the event loop.
        For async applications, use AsyncCircuitBreaker.save_state() instead.

        Only saves if persist_state is enabled and storage is configured.
        Thread-safe - acquires lock before reading state, but lock is released
        before async database operations to minimize blocking.

        Note: In production async code, prefer AsyncCircuitBreaker which uses
        asyncio-compatible locks throughout.
        """
        if not self.persist_state or self._storage is None:
            return

        import json

        from sqlmodel import delete
        from sqlmodel.ext.asyncio.session import AsyncSession

        from proxywhirl.storage import CircuitBreakerStateTable

        with self._lock:
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

        # Perform database operation outside lock to avoid blocking
        async with AsyncSession(self._storage.engine) as session:
            # Delete existing state (upsert pattern)
            stmt = delete(CircuitBreakerStateTable).where(
                CircuitBreakerStateTable.proxy_id == self.proxy_id  # type: ignore[arg-type]
            )
            await session.exec(stmt)

            # Insert new state
            session.add(state_record)
            await session.commit()

    async def load_state(self) -> bool:
        """Load circuit breaker state from storage.

        WARNING: This async method uses threading.Lock which can block the event loop.
        For async applications, use AsyncCircuitBreaker.load_state() instead.

        Returns:
            True if state was loaded successfully, False if no state found

        Thread-safe - acquires lock before updating state, but performs async
        database reads outside the lock to minimize blocking.

        Note: In production async code, prefer AsyncCircuitBreaker which uses
        asyncio-compatible locks throughout.
        """
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

            # Deserialize failure window
            failure_window_list = json.loads(state_record.failure_window_json)

            # Update state with lock
            with self._lock:
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
        """Delete persisted state from storage.

        WARNING: This async method should be used in sync contexts only.
        For async applications, use AsyncCircuitBreaker.delete_state() instead.

        Useful for cleanup or when a proxy is removed from the pool.
        Does not use locks as it's a pure async I/O operation.
        """
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
