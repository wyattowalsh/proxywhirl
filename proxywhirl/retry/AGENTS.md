# Retry Subsystem

> Extends: [../../AGENTS.md](../../AGENTS.md)

## Modules

`policy.py` (`RetryPolicy`, `BackoffStrategy`), `executor.py` (`RetryExecutor`, `RetryableError`), `metrics.py` (`RetryMetrics`)

## Backoff Strategies

`constant`, `linear`, `exponential` (default), `fibonacci`

## Usage

```python
from proxywhirl.retry import RetryPolicy, RetryExecutor
policy = RetryPolicy(max_attempts=3, backoff_strategy="exponential")
executor = RetryExecutor(policy)
# Sync
result = executor.execute_with_retry(request_fn, proxy, method, url)
# Async
result = await executor.execute_with_retry_async(func, proxies, circuit_breakers)
```

## Boundaries

**Always:** Exponential backoff for network, max_attempts 3-5, log with `RetryMetrics`

**Never:** Retry indefinitely, retry non-idempotent blindly, swallow `NonRetryableError`
