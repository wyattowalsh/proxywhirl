"""
Async circuit breaker implementation with RWLock for reduced contention.

This is the async-first implementation that uses AsyncRWLock for
better performance in high-concurrency scenarios.
"""

from __future__ import annotations

from typing import Any

from pydantic import PrivateAttr

from proxywhirl.circuit_breaker.base import CircuitBreakerBase, CircuitBreakerState
from proxywhirl.models import CircuitBreakerConfig
from proxywhirl.rwlock import AsyncRWLock

# Re-export for backward compatibility
__all__ = ["AsyncCircuitBreaker", "CircuitBreakerState"]


class AsyncCircuitBreaker(CircuitBreakerBase):
    """Async circuit breaker for a single proxy with RWLock for high concurrency.

    This is the ASYNCHRONOUS implementation designed for async/await contexts.
    Uses AsyncRWLock for event-loop-safe operations with reduced lock contention.

    Key Features:
        - Event-loop safe: All methods are async and use asyncio-compatible locks
        - High concurrency: RWLock allows multiple readers or single writer
        - Zero blocking: Never blocks the event loop with synchronous operations

    For synchronous contexts, use CircuitBreaker from circuit_breaker module instead.

    Attributes:
        proxy_id: Unique identifier for the proxy
        state: Current circuit breaker state (CLOSED, OPEN, HALF_OPEN)
        failure_count: Number of failures in current window
        failure_threshold: Number of failures before opening circuit
        window_duration: Rolling window duration in seconds
        timeout_duration: How long circuit stays open before testing recovery

    Example:
        >>> from proxywhirl.circuit_breaker_async import AsyncCircuitBreaker
        >>> cb = AsyncCircuitBreaker(proxy_id="proxy-1")
        >>> await cb.record_failure()  # Event-loop safe
        >>> if await cb.should_attempt_request():
        ...     # make async request
        ...     await cb.record_success()
    """

    _lock: AsyncRWLock = PrivateAttr(default_factory=AsyncRWLock)

    async def record_failure(self) -> None:
        """Record a failure and update state if threshold reached."""
        async with self._lock.write_lock():
            self._do_record_failure()

    async def record_success(self) -> None:
        """Record a success and potentially close circuit."""
        async with self._lock.write_lock():
            self._do_record_success()

    async def should_attempt_request(self) -> bool:
        """Check if proxy is available for requests.

        Uses write lock to prevent TOCTOU race conditions.

        Returns:
            True if proxy should be attempted, False if circuit is open.
        """
        async with self._lock.write_lock():
            return self._do_should_attempt_request()

    async def reset(self) -> None:
        """Manually reset circuit breaker to CLOSED state."""
        async with self._lock.write_lock():
            self._do_reset()

    @classmethod
    def create(
        cls,
        proxy_id: str,
        config: CircuitBreakerConfig | None = None,
        **kwargs: Any,
    ) -> AsyncCircuitBreaker:
        """Factory method to create a circuit breaker with optional config.

        Args:
            proxy_id: Unique identifier for the proxy
            config: CircuitBreakerConfig with settings
            **kwargs: Additional AsyncCircuitBreaker field overrides

        Returns:
            AsyncCircuitBreaker instance
        """
        if config:
            failure_threshold = kwargs.pop("failure_threshold", config.failure_threshold)
            window_duration = kwargs.pop("window_duration", config.window_duration)
            timeout_duration = kwargs.pop("timeout_duration", config.timeout_duration)

            return cls(
                proxy_id=proxy_id,
                failure_threshold=failure_threshold,
                window_duration=window_duration,
                timeout_duration=timeout_duration,
                **kwargs,
            )
        return cls(proxy_id=proxy_id, **kwargs)

    @classmethod
    def from_config(
        cls,
        proxy_id: str,
        config: CircuitBreakerConfig | None = None,
        **kwargs: Any,
    ) -> AsyncCircuitBreaker:
        """Backward-compatible alias for create()."""
        return cls.create(proxy_id=proxy_id, config=config, **kwargs)
