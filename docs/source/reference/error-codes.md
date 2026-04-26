---
title: Error Codes & Troubleshooting
---

# Error Codes Reference

## Overview

ProxyWhirl uses structured error codes and exception hierarchy for predictable error handling and debugging.

## Exception Hierarchy

```
ProxyWhirlError (base)
├── ProxyPoolEmptyError         -- No proxies available
├── ProxyValidationError         -- Validation failed
├── ProxyConnectionError         -- Connection failed
├── ProxyAuthenticationError     -- Auth failed
├── ProxyFetchError              -- Fetch failed
├── ProxyStorageError            -- Storage failed
├── RetryableError               -- Retryable error
├── NonRetryableError            -- Non-retryable error
├── RegexTimeoutError            -- Regex timeout (ReDoS)
├── RegexComplexityError         -- Regex too complex
├── CacheCorruptionError         -- Cache corrupted
├── CacheStorageError            -- Cache storage failed
├── CacheValidationError         -- Cache validation failed
└── RequestQueueFullError        -- Queue full
```

## Error Codes

### Pool & Selection Errors

| Code | Exception | Cause | Resolution |
|------|-----------|-------|-----------|
| `E001` | `ProxyPoolEmptyError` | No proxies in pool | Fetch proxies: `whirl.bootstrap()` or `add_sources()` |
| `E002` | `ProxyPoolEmptyError` | All proxies filtered out | Check filter criteria or expand source list |
| `E003` | `ProxyPoolEmptyError` | Circuit breaker opened all | Wait for recovery (30-60s) or reset: `whirl.circuit_breaker.reset()` |

### Validation Errors

| Code | Exception | Cause | Resolution |
|------|-----------|-------|-----------|
| `E010` | `ProxyValidationError` | Invalid proxy URL | Ensure format: `protocol://[user:pass@]host:port` |
| `E011` | `ProxyValidationError` | Unsupported protocol | Use: `http`, `https`, `socks4`, `socks5` |
| `E012` | `ProxyValidationError` | Invalid host/port | Check IP/hostname and port range (1-65535) |
| `E013` | `ProxyValidationError` | Credentials invalid | Provide valid username and password |
| `E014` | `ProxyValidationError` | Timeout validation failed | Increase timeout or check proxy |

### Connection Errors

| Code | Exception | Cause | Resolution |
|------|-----------|-------|-----------|
| `E020` | `ProxyConnectionError` | Connection timeout | Increase timeout or check network |
| `E021` | `ProxyConnectionError` | Connection refused | Proxy not responding, mark as inactive |
| `E022` | `ProxyConnectionError` | DNS resolution failed | Check proxy hostname or DNS settings |
| `E023` | `ProxyConnectionError` | TLS handshake failed | Check HTTPS proxy support |
| `E024` | `ProxyConnectionError` | Connection reset | Network unstable, retry or switch proxy |

### Authentication Errors

| Code | Exception | Cause | Resolution |
|------|-----------|-------|-----------|
| `E030` | `ProxyAuthenticationError` | 407 Proxy Auth Required | Check credentials in proxy URL |
| `E031` | `ProxyAuthenticationError` | 401 Unauthorized | Verify username and password |
| `E032` | `ProxyAuthenticationError` | Credentials expired | Refresh credentials or use new proxy |

### Fetch Errors

| Code | Exception | Cause | Resolution |
|------|-----------|-------|-----------|
| `E040` | `ProxyFetchError` | Source fetch failed | Check source URL, network, or rate limit |
| `E041` | `ProxyFetchError` | Invalid response format | Source may have changed, check parser |
| `E042` | `ProxyFetchError` | Parser error | Validate response format matches parser type |
| `E043` | `ProxyFetchError` | Rate limit hit | Add backoff or use `respx_mock` in tests |
| `E044` | `ProxyFetchError` | Source timeout | Increase timeout or check source |

### Storage Errors

| Code | Exception | Cause | Resolution |
|------|-----------|-------|-----------|
| `E050` | `ProxyStorageError` | Database connection failed | Check database path and permissions |
| `E051` | `ProxyStorageError` | SQL query failed | Check database integrity: `PRAGMA integrity_check;` |
| `E052` | `ProxyStorageError` | Disk full | Free disk space or rotate old proxies |
| `E053` | `ProxyStorageError` | Permission denied | Check file/directory permissions |

### Retry Errors

| Code | Exception | Cause | Resolution |
|------|-----------|-------|-----------|
| `E060` | `RetryableError` | Temporary failure | Retry with backoff (automatic with `RetryExecutor`) |
| `E061` | `NonRetryableError` | Permanent failure | Switch proxy or source |

### Regex & Security Errors

| Code | Exception | Cause | Resolution |
|------|-----------|-------|-----------|
| `E070` | `RegexTimeoutError` | ReDoS attack detected | Use `safe_regex.py` utilities |
| `E071` | `RegexComplexityError` | Regex too complex | Simplify pattern or use non-regex parsing |

### Cache Errors

| Code | Exception | Cause | Resolution |
|------|-----------|-------|-----------|
| `E080` | `CacheCorruptionError` | Cache data corrupted | Clear cache: `cache_mgr.clear()` |
| `E081` | `CacheStorageError` | Cache write failed | Check disk permissions and space |
| `E082` | `CacheValidationError` | Cache checksum failed | Verify encryption key (`PROXYWHIRL_CACHE_ENCRYPTION_KEY`) |

### Queue Errors

| Code | Exception | Cause | Resolution |
|------|-----------|-------|-----------|
| `E090` | `RequestQueueFullError` | Queue capacity exceeded | Reduce concurrency or increase queue size |

## Exception Handling Examples

### Graceful Degradation

```python
from proxywhirl import ProxyWhirl, ProxyPoolEmptyError

whirl = ProxyWhirl(config)

try:
    proxy = whirl.get()
except ProxyPoolEmptyError:
    # Fall back to direct connection
    logger.warning("No proxies available, using direct connection")
    proxy = None
```

### Retry on Specific Errors

```python
from proxywhirl import ProxyConnectionError, ProxyValidationError
import time

for attempt in range(3):
    try:
        proxy = whirl.get()
        response = client.get(url, proxies=proxy.to_url())
        break
    except (ProxyConnectionError, ProxyValidationError) as e:
        logger.error(f"Attempt {attempt+1} failed: {e.error_code}")
        if attempt < 2:
            time.sleep(2 ** attempt)
        else:
            raise
```

### Extracting Error Information

```python
try:
    proxy = whirl.get()
except Exception as e:
    # All ProxyWhirlError subclasses have these attributes
    error_code = getattr(e, 'error_code', 'UNKNOWN')
    retryable = getattr(e, 'retryable', False)
    
    print(f"Error Code: {error_code}")
    print(f"Retryable: {retryable}")
    print(f"Message: {str(e)}")
```

## Debugging Tips

### Enable Debug Logging

```python
from proxywhirl.logging_config import configure_logging

configure_logging(level="DEBUG")

# Or via environment
export PROXYWHIRL_LOG_LEVEL=DEBUG
```

### Inspect Exception Chain

```python
import traceback

try:
    proxy = whirl.get()
except Exception as e:
    traceback.print_exc()  # Full stack trace
    print(f"Root cause: {e.__cause__}")
```

### Check Proxy Health

```python
# Before attempting use
proxy = whirl.get()
print(f"Health: {proxy.health_status}")
print(f"Last checked: {proxy.last_validated}")
print(f"Success rate: {proxy.success_rate}%")
```

## Common Scenarios

### Scenario 1: Connection Timeout

```
Error: E020 - ProxyConnectionError: Connection timeout after 30s
Cause: Proxy slow or unreachable
Solutions:
  1. Increase timeout: config.timeout_seconds = 60
  2. Switch proxy: whirl.get(exclude_countries=['slow_proxy_country'])
  3. Check network: ping proxy_host
```

### Scenario 2: All Breakers Open

```
Error: E003 - ProxyPoolEmptyError: All circuit breakers open
Cause: Too many failures, automatic failsafe triggered
Solutions:
  1. Wait 30-60s for automatic recovery
  2. Manually reset: whirl.circuit_breaker.reset_all()
  3. Reduce failure threshold: config.circuit_breaker.failure_threshold = 10
```

### Scenario 3: Database Lock

```
Error: E051 - ProxyStorageError: SQL query failed: database is locked
Cause: High concurrency or long transaction
Solutions:
  1. Enable WAL mode: PRAGMA journal_mode=WAL;
  2. Reduce transaction time
  3. Use AsyncProxyWhirl for concurrency
```

### Scenario 4: Cache Corruption

```
Error: E080 - CacheCorruptionError: Checksum mismatch
Cause: Incomplete write or missing encryption key
Solutions:
  1. Clear cache: whirl.cache_manager.clear()
  2. Verify encryption key: echo $PROXYWHIRL_CACHE_ENCRYPTION_KEY
  3. Restore from backup
```

## Monitoring & Alerting

### Track Error Rates

```python
from proxywhirl.metrics_collector import MetricsCollector

metrics = MetricsCollector()
error_rate = metrics.error_rate_percent
if error_rate > 5:
    logger.error(f"High error rate: {error_rate}%")
```

### Setup Alerts

```python
# In your monitoring system
if error_code in ['E003', 'E020', 'E001']:
    alert_on_channel("critical", f"ProxyWhirl error: {error_code}")
```

## See Also

- [Troubleshooting Guide](../guides/troubleshooting.md)
- [Exception Hierarchy](../reference/exceptions.md)
- [Retry & Failover](../guides/retry-failover.md)
- [Circuit Breakers](../concepts/circuit-breakers.md)
