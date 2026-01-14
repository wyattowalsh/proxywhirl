"""
Retry execution package with intelligent backoff and circuit breaker integration.

This package provides:
- RetryPolicy: Configuration for retry behavior and backoff strategies
- RetryExecutor: Orchestrates retries with proxy selection and circuit breakers
- RetryMetrics: Collection and aggregation of retry statistics

Usage:
    from proxywhirl.retry import RetryPolicy, RetryExecutor, RetryMetrics

    policy = RetryPolicy(max_attempts=3, backoff_strategy="exponential")
    metrics = RetryMetrics()
    executor = RetryExecutor(policy, metrics=metrics)

    # Sync execution
    result = executor.execute_with_retry(func, proxies, circuit_breakers)

    # Async execution
    result = await executor.execute_with_retry_async(async_func, proxies, circuit_breakers)
"""

from proxywhirl.retry.executor import (
    NonRetryableError,
    RetryableError,
    RetryExecutor,
)
from proxywhirl.retry.metrics import (
    CircuitBreakerEvent,
    HourlyAggregate,
    RetryAttempt,
    RetryMetrics,
    RetryOutcome,
)
from proxywhirl.retry.policy import BackoffStrategy, RetryPolicy

__all__ = [
    # Policy
    "BackoffStrategy",
    "RetryPolicy",
    # Executor
    "RetryExecutor",
    "RetryableError",
    "NonRetryableError",
    # Metrics
    "RetryMetrics",
    "RetryAttempt",
    "RetryOutcome",
    "CircuitBreakerEvent",
    "HourlyAggregate",
]
