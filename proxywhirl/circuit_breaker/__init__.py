"""
Circuit breaker pattern implementation for proxy failure management.

This package provides both synchronous and asynchronous circuit breaker
implementations for managing proxy failures and automatic recovery.

Usage:
    Synchronous:
        >>> from proxywhirl.circuit_breaker import CircuitBreaker
        >>> cb = CircuitBreaker(proxy_id="proxy-1")

    Asynchronous:
        >>> from proxywhirl.circuit_breaker import AsyncCircuitBreaker
        >>> cb = AsyncCircuitBreaker(proxy_id="proxy-1")
"""

from proxywhirl.circuit_breaker.async_ import AsyncCircuitBreaker
from proxywhirl.circuit_breaker.base import CircuitBreakerBase, CircuitBreakerState
from proxywhirl.circuit_breaker.sync import CircuitBreaker

__all__ = [
    "CircuitBreaker",
    "AsyncCircuitBreaker",
    "CircuitBreakerBase",
    "CircuitBreakerState",
]
