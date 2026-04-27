# Error Recovery Patterns

ProxyWhirl’s resilience stack combines **retry policies**, **circuit breakers**, and a **structured exception hierarchy** to handle transient failures gracefully while isolating persistently broken proxies.

## Exception Hierarchy

All ProxyWhirl errors inherit from `ProxyWhirlError`. Knowing the base classes helps you catch the right failures.

```
ProxyWhirlError
├── ProxyPoolEmptyError
├── ProxyValidationError
├── ProxyConnectionError
├── ProxyAuthenticationError
├── ProxyFetchError
├── ProxyStorageError
├── RetryableError
├── NonRetryableError
├── CacheCorruptionError
└── RequestQueueFullError
```

- **RetryableError:** Safe to retry (timeouts, 502/503/504).
- **NonRetryableError:** Do not retry (auth failures, malformed URLs).
- **ProxyPoolEmptyError:** No proxies available. Usually requires refetching from sources.

## Configuring Retries

`RetryPolicy` controls how the `RetryExecutor` reattempts failed requests.

```python
from proxywhirl import RetryPolicy, BackoffStrategy

policy = RetryPolicy(
    max_attempts=5,
    backoff_strategy=BackoffStrategy.EXPONENTIAL,
    base_delay=1.0,
    max_backoff_delay=30.0,
    retry_status_codes=[502, 503, 504],
    retry_non_idempotent=False,
)
```

Set `retry_non_idempotent=True` only if your endpoints are safe to replay (e.g., idempotent GET/PUT).

## Circuit Breaker Integration

Each proxy has its own `CircuitBreaker` (sync) or `AsyncCircuitBreaker` (async) instance. After a proxy exceeds the failure threshold, the breaker **opens** and blocks traffic for `timeout_duration` seconds before a single **half-open** test request is allowed.

```python
from proxywhirl import CircuitBreakerConfig

config = CircuitBreakerConfig(
    failure_threshold=5,
    window_duration=60.0,
    timeout_duration=30.0,
)
```

States:

| State | Behavior |
|-------|----------|
| `CLOSED` | Normal operation; failures are counted. |
| `OPEN` | Proxy excluded from rotation. |
| `HALF_OPEN` | One test request allowed to verify recovery. |

## Combining Retry and Circuit Breaker

A typical request flow:

1. Rotator selects a proxy.
2. Circuit breaker checks if the proxy is `CLOSED` or eligible for `HALF_OPEN`.
3. Request is sent.
4. On `RetryableError`, `RetryExecutor` retries with exponential backoff.
5. After exhausting `max_attempts`, the failure is recorded in the circuit breaker.
6. If failures exceed `failure_threshold`, the breaker opens.

## Metrics and Observability

Both `RetryExecutor` and circuit breakers expose metrics for monitoring.

```python
from proxywhirl.retry import RetryMetrics

metrics = RetryMetrics()
print(f"Total attempts: {metrics.total_attempts}")
print(f"Retries due to 503: {metrics.retries_by_status[503]}")
```

Log these metrics to detect proxies that degrade over time.

## Recovery Patterns

### Graceful Degradation

When the pool is empty, fall back to a direct request or a static proxy list.

```python
from proxywhirl import ProxyPoolEmptyError

try:
    response = rotator.get("https://api.example.com")
except ProxyPoolEmptyError:
    response = httpx.get("https://api.example.com")
```

### Manual Circuit Reset

After a known outage resolves, reset a breaker manually instead of waiting for the timeout.

```python
rotator.circuit_breaker.reset(proxy_id="proxy-42")
```

### Bulk Failure Handling

If all proxies fail simultaneously, check upstream source health or reduce `failure_threshold` to catch issues earlier.

## Summary

| Layer | Responsibility |
|-------|----------------|
| Exception types | Classify retryable vs fatal |
| Retry policy | Backoff and attempt limits |
| Circuit breaker | Isolate unhealthy proxies |
| Metrics | Visibility into failure trends |
