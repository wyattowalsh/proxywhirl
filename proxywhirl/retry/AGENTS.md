# Retry Subsystem

> Extends: [../../AGENTS.md](../../AGENTS.md)

## Modules

| File | Key Classes |
|------|-------------|
| `policy.py` | `RetryPolicy`, `BackoffStrategy` (enum) |
| `executor.py` | `RetryExecutor`, `RetryableError`, `NonRetryableError` |
| `metrics.py` | `RetryMetrics`, `RetryAttempt`, `RetryOutcome`, `CircuitBreakerEvent` |

## Backoff Strategies

| Strategy | Description |
|----------|-------------|
| `constant` | Fixed delay between retries |
| `linear` | Delay increases linearly |
| `exponential` | Delay doubles each attempt (default) |
| `fibonacci` | Delay follows Fibonacci sequence |

## Usage

```python
from proxywhirl.retry import RetryPolicy, RetryExecutor, RetryMetrics

policy = RetryPolicy(max_attempts=3, backoff_strategy="exponential")
metrics = RetryMetrics()
executor = RetryExecutor(policy, metrics=metrics)

# Sync
result = executor.execute_with_retry(func, proxies, circuit_breakers)

# Async
result = await executor.execute_with_retry_async(async_func, proxies, circuit_breakers)
```

## Boundaries

**Always:**
- Use exponential backoff for network operations
- Set reasonable max_attempts (3-5)
- Log retry attempts with `RetryMetrics`
- Wrap retryable errors in `RetryableError`

**Ask First:**
- Default policy changes
- New backoff strategies
- Metrics schema changes

**Never:**
- Retry indefinitely
- Retry non-idempotent operations without care
- Swallow `NonRetryableError`
