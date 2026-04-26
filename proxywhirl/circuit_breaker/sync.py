"""
Circuit breaker pattern implementation for proxy failure management.

IMPORTANT: This module provides SYNCHRONOUS circuit breaker implementation.

Usage Guidelines:
-----------------
- CircuitBreaker: Use in synchronous contexts only (threading.Lock)
- AsyncCircuitBreaker: Use in async contexts (from circuit_breaker_async module)

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

from threading import Lock
from typing import Any

from pydantic import PrivateAttr

from proxywhirl.circuit_breaker.base import CircuitBreakerBase, CircuitBreakerState
from proxywhirl.models import CircuitBreakerConfig

# Re-export for backward compatibility
__all__ = ["CircuitBreaker", "CircuitBreakerState"]


class CircuitBreaker(CircuitBreakerBase):
    """Circuit breaker for a single proxy (SYNCHRONOUS implementation).

    WARNING: This class uses threading.Lock and is designed for SYNCHRONOUS contexts only.
    For async applications, use AsyncCircuitBreaker from circuit_breaker_async module.

    Attributes:
        proxy_id: Unique identifier for the proxy
        state: Current circuit breaker state (CLOSED, OPEN, HALF_OPEN)
        failure_count: Number of failures in current window
        failure_threshold: Number of failures before opening circuit
        window_duration: Rolling window duration in seconds
        timeout_duration: How long circuit stays open before testing recovery
    """

    _lock: Lock = PrivateAttr(default_factory=Lock)

    def record_failure(self) -> None:
        """Record a failure and update state if threshold reached.

        Thread-safe - acquires threading.Lock for the entire operation.
        """
        with self._lock:
            self._do_record_failure()

    def record_success(self) -> None:
        """Record a success and potentially close circuit.

        Thread-safe - acquires threading.Lock for the entire operation.
        """
        with self._lock:
            self._do_record_success()

    def should_attempt_request(self) -> bool:
        """Check if proxy is available for requests.

        Thread-safe - acquires threading.Lock for the entire operation.

        Returns:
            True if proxy should be attempted, False if circuit is open.
        """
        with self._lock:
            return self._do_should_attempt_request()

    def reset(self) -> None:
        """Manually reset circuit breaker to CLOSED state.

        Thread-safe - acquires threading.Lock before resetting state.
        """
        with self._lock:
            self._do_reset()

    @classmethod
    def create(
        cls,
        proxy_id: str,
        config: CircuitBreakerConfig | None = None,
        **kwargs: Any,
    ) -> CircuitBreaker:
        """Factory method to create a circuit breaker with optional config.

        Args:
            proxy_id: Unique identifier for the proxy
            config: CircuitBreakerConfig with settings
            **kwargs: Additional CircuitBreaker field overrides

        Returns:
            CircuitBreaker instance
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
    ) -> CircuitBreaker:
        """Backward-compatible alias for create()."""
        return cls.create(proxy_id=proxy_id, config=config, **kwargs)
