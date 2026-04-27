# Troubleshooting Common Issues

This guide covers frequent issues encountered when running ProxyWhirl in development and production, along with diagnostic steps and fixes.

## ProxyPoolEmptyError: No Proxies Available

**Symptoms:**
```
proxywhirl.exceptions.ProxyPoolEmptyError: No healthy proxies available in the pool
```

**Causes & Fixes:**

| Cause | Fix |
|-------|-----|
| Source returned empty list | Verify source URL; check API keys or rate limits. |
| All proxies expired | Reduce `default_ttl_seconds` or trigger a manual refresh. |
| Circuit breakers are OPEN | Wait for `timeout_duration` or call `breaker.reset(proxy_id)`. |
| Filter too strict | Relax geolocation or protocol filters. |

**Diagnostic:**

```python
from proxywhirl import ProxyWhirl

rotator = ProxyWhirl()
print(rotator.pool.size)
print(rotator.pool.healthy_count)
print(rotator.circuit_breaker.states)
```

## All Requests Time Out

**Symptoms:** Every request raises `ProxyConnectionError` or `RetryableError` after retries.

**Causes & Fixes:**

- **Network issue:** Verify outbound connectivity from the host.
- **Proxy blacklist:** The target site may block your proxy IPs. Rotate to a fresher pool.
- **Overly aggressive timeout:** Increase `RetryPolicy.timeout` or `httpx` client timeout.

```python
from proxywhirl import RetryPolicy

policy = RetryPolicy(
    max_attempts=3,
    timeout=10.0,  # Increase from default if needed
)
```

## Cache Corruption Errors

**Symptoms:** `CacheCorruptionError` on startup or during reads.

**Fix:**

```python
from proxywhirl.cache import CacheManager

manager = CacheManager()
manager.rebuild_l2()  # Rebuild disk cache from scratch
manager.rebuild_l3()  # Rebuild SQLite archive
```

To prevent corruption, avoid sharing L2 JSONL files across multiple processes without file locking. Use `l2_backend="sqlite"` for better concurrency safety.

## High Memory Usage

**Symptoms:** Process RSS grows continuously.

**Causes & Fixes:**

- **L1 too large:** Lower `l1_max_entries`.
- **Memory leak in custom strategy:** Ensure `deregister()` cleans up internal mappings.
- **Unbounded failure windows:** Circuit breaker `deque(maxlen=10000)` is usually safe; reduce if memory-constrained.

```python
from proxywhirl import CacheConfig

config = CacheConfig(l1_max_entries=250)
```

## Circuit Breaker Stuck in OPEN

**Symptoms:** A proxy never recovers even though it is healthy.

**Diagnostic:**

```python
breaker = rotator.circuit_breaker.get("proxy-42")
print(breaker.state)          # Should eventually be HALF_OPEN
print(breaker.next_test_time) # Must be <= now() to test
```

If `next_test_time` is far in the future, you may have set `timeout_duration` too high. Lower it or call `breaker.reset()` after confirming upstream health.

## Regex Timeout Errors

**Symptoms:** `RegexTimeoutError` during proxy list parsing.

**Fix:** Validate parser regexes with `safe_compile_regex` before use. Avoid nested quantifiers like `(a+)+` or `(.*)*`.

```python
from proxywhirl.safe_regex import safe_compile_regex

pattern = safe_compile_regex(
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+",
    max_complexity=500,
)
```

## Slow Rotation / High Latency

**Symptoms:** Requests take seconds even with fast proxies.

**Causes & Fixes:**

- **Synchronous health checks blocking async loop:** Use `AsyncProxyWhirl` with background health checks.
- **L3 SQLite contention:** Increase `cleanup_interval_seconds` or move L3 to a separate disk.
- **DNS resolution delays:** Use `httpx` with `http2=True` or cache DNS locally.

## Getting Help

If an issue persists:

1. Enable debug logging: `configure_logging(level="DEBUG", redact_credentials=True)`.
2. Capture `RetryMetrics` and `CacheStatistics` output.
3. Open an issue with the stack trace, config, and proxy source (redact credentials).
