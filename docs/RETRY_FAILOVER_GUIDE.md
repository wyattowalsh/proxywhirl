# Retry & Failover Logic Guide

**Feature**: 014-retry-failover-logic  
**Version**: 1.0.0  
**Date**: 2025-11-02

---

## Overview

ProxyWhirl includes intelligent retry and failover logic with:
- **Automatic retries** with exponential backoff
- **Circuit breakers** for failing proxies
- **Intelligent proxy selection** based on performance
- **Configurable policies** per request or globally
- **Comprehensive metrics** for monitoring

---

## Quick Start

### Basic Usage

```python
from proxywhirl import ProxyRotator, Proxy

# Create rotator (retry enabled by default)
rotator = ProxyRotator(
    proxies=[
        Proxy(url="http://proxy1.example.com:8080"),
        Proxy(url="http://proxy2.example.com:8080"),
    ]
)

# Make request with automatic retries
response = rotator.get("https://api.example.com/data")
```

**Default behavior**:
- Max 3 retry attempts
- Exponential backoff (1s, 2s, 4s)
- Retries on 502, 503, 504 status codes
- Circuit breakers protect against cascading failures

---

## Configuration

### Retry Policy

```python
from proxywhirl import RetryPolicy, BackoffStrategy

policy = RetryPolicy(
    max_attempts=5,                          # Max retry attempts (1-10)
    backoff_strategy=BackoffStrategy.LINEAR, # EXPONENTIAL, LINEAR, or FIXED
    base_delay=2.0,                          # Base delay in seconds (0.1-60)
    multiplier=2.0,                          # For exponential (1.1-10)
    max_backoff_delay=30.0,                  # Cap delay (1-300s)
    jitter=True,                             # Add randomness (?50%)
    retry_status_codes=[502, 503, 504, 429], # Status codes to retry
    timeout=15.0,                            # Total timeout (optional)
    retry_non_idempotent=False,              # Retry POST/PUT (default: False)
)

rotator = ProxyRotator(proxies=proxies, retry_policy=policy)
```

### Circuit Breaker

Circuit breaker parameters are configured at the module level:

```python
from proxywhirl.circuit_breaker import CircuitBreaker

# When adding proxies, circuit breakers are auto-created with defaults:
# - failure_threshold: 5 (failures to trigger open)
# - window_duration: 60.0 (rolling window in seconds)
# - timeout_duration: 30.0 (seconds until half-open test)
```

---

## Common Use Cases

### 1. High-Volume APIs (Aggressive Retries)

```python
policy = RetryPolicy(
    max_attempts=5,
    backoff_strategy=BackoffStrategy.EXPONENTIAL,
    base_delay=0.5,        # Start fast
    max_backoff_delay=10.0,  # Cap at 10s
    jitter=True,           # Avoid thundering herd
)
```

### 2. Rate-Limited APIs (Conservative Retries)

```python
policy = RetryPolicy(
    max_attempts=3,
    backoff_strategy=BackoffStrategy.LINEAR,
    base_delay=5.0,        # Give API time to recover
    retry_status_codes=[429, 502, 503, 504],  # Include rate limit
)
```

### 3. Critical Operations (Fail Fast)

```python
policy = RetryPolicy(
    max_attempts=2,        # Only 1 retry
    base_delay=1.0,
    timeout=5.0,           # Quick timeout
)
```

### 4. Geo-Targeted Requests

```python
# Tag proxies with regions
proxy_us = Proxy(
    url="http://proxy-us.example.com:8080",
    metadata={"region": "US-EAST"},
)

proxy_eu = Proxy(
    url="http://proxy-eu.example.com:8080",
    metadata={"region": "EU-WEST"},
)

rotator = ProxyRotator(proxies=[proxy_us, proxy_eu])

# System will prefer same-region proxies for retries (10% bonus)
```

---

## Monitoring & Observability

### Check Circuit Breaker States

```python
states = rotator.get_circuit_breaker_states()

for proxy_id, cb in states.items():
    print(f"Proxy: {proxy_id}")
    print(f"  State: {cb.state.value}")
    print(f"  Failures: {cb.failure_count}/{cb.failure_threshold}")
    
    if cb.state == CircuitBreakerState.OPEN:
        # Proxy is excluded from rotation
        print(f"  Next test: {cb.next_test_time}")
```

### Get Retry Metrics

```python
metrics = rotator.get_retry_metrics()
summary = metrics.get_summary()

print(f"Total retries: {summary['total_retries']}")
print(f"Success by attempt: {summary['success_by_attempt']}")

# Example: {0: 850, 1: 120, 2: 25, 3: 5}
# 850 succeeded on first try
# 120 succeeded after 1 retry
# 25 succeeded after 2 retries
# 5 succeeded after 3 retries
```

### Time-Series Data

```python
timeseries = metrics.get_timeseries(hours=24)

for point in timeseries:
    print(f"Hour: {point['timestamp']}")
    print(f"  Total requests: {point['total_requests']}")
    print(f"  Total retries: {point['total_retries']}")
    print(f"  Success rate: {point['success_rate']:.2%}")
```

### Per-Proxy Statistics

```python
stats = metrics.get_by_proxy(hours=24)

for proxy_id, proxy_stats in stats.items():
    print(f"Proxy: {proxy_id}")
    print(f"  Attempts: {proxy_stats['total_attempts']}")
    print(f"  Success: {proxy_stats['success_count']}")
    print(f"  Failures: {proxy_stats['failure_count']}")
    print(f"  Avg latency: {proxy_stats['avg_latency']:.3f}s")
    print(f"  Circuit opens: {proxy_stats['circuit_breaker_opens']}")
```

---

## Troubleshooting

### Problem: All Proxies Have Open Circuit Breakers

**Symptom**: Requests fail with "503 Service Temporarily Unavailable"

**Cause**: All proxies experiencing failures (threshold exceeded)

**Solutions**:

1. **Wait for automatic recovery** (default: 30s until half-open test)
2. **Check proxy health manually**:
   ```python
   states = rotator.get_circuit_breaker_states()
   for proxy_id, cb in states.items():
       print(f"{proxy_id}: {cb.state.value}")
   ```
3. **Manually reset circuit breakers**:
   ```python
   for proxy_id in rotator.circuit_breakers.keys():
       rotator.reset_circuit_breaker(proxy_id)
   ```

---

### Problem: Retries Taking Too Long

**Symptom**: Requests timing out or taking >5 seconds

**Causes**:
- Too many retry attempts
- Backoff delays too long
- No timeout configured

**Solutions**:

1. **Reduce max_attempts**:
   ```python
   policy = RetryPolicy(max_attempts=2)
   ```

2. **Use FIXED backoff**:
   ```python
   policy = RetryPolicy(
       backoff_strategy=BackoffStrategy.FIXED,
       base_delay=1.0,
   )
   ```

3. **Set lower max_backoff_delay**:
   ```python
   policy = RetryPolicy(max_backoff_delay=5.0)
   ```

4. **Add total timeout**:
   ```python
   policy = RetryPolicy(timeout=3.0)  # 3 second hard limit
   ```

---

### Problem: POST Requests Not Retrying

**Symptom**: POST requests fail immediately without retry

**Cause**: POST is non-idempotent (default: no retry)

**Solutions**:

1. **For safe operations** (idempotent despite method):
   ```python
   policy = RetryPolicy(retry_non_idempotent=True)
   rotator._make_request(
       "POST",
       "https://api.example.com/endpoint",
       retry_policy=policy,
   )
   ```

2. **Use idempotent methods** when possible:
   - GET, HEAD, OPTIONS, DELETE ? Always retry
   - PUT ? Can retry if idempotent
   - POST ? Use with caution

---

### Problem: High Memory Usage

**Symptom**: Memory growing over time

**Cause**: Metrics retention (24h default)

**Investigation**:
```python
metrics = rotator.get_retry_metrics()
print(f"Current attempts: {len(metrics.current_attempts)}")
print(f"Hourly aggregates: {len(metrics.hourly_aggregates)}")
print(f"CB events: {len(metrics.circuit_breaker_events)}")
```

**Expected**:
- Current attempts: <10,000 (last hour)
- Hourly aggregates: 24 (last 24 hours)
- CB events: <1,000

**Memory**: Typically <15MB for 10k req/hour

**Solutions**:
- Metrics auto-cleanup after 24h
- Monitor with periodic checks
- Normal operation for high-volume systems

---

### Problem: Circuit Breaker Opens Too Frequently

**Symptom**: Proxies constantly moving to OPEN state

**Causes**:
- Threshold too low
- Window too short
- Proxy genuinely unhealthy

**Solutions**:

1. **Increase failure threshold** (edit at proxy level):
   ```python
   # Current: 5 failures in 60s
   # To adjust, modify CircuitBreaker creation in add_proxy()
   ```

2. **Check proxy health**:
   ```python
   for proxy in rotator.pool.proxies:
       print(f"{proxy.url}: {proxy.success_rate:.2%}")
   ```

3. **Remove unhealthy proxies**:
   ```python
   rotator.clear_unhealthy_proxies()
   ```

---

### Problem: Retries Using Same Failed Proxy

**Symptom**: System keeps retrying with the proxy that just failed

**Cause**: Only one proxy available or all others have open circuits

**Investigation**:
```python
available = [
    p for p in rotator.pool.proxies
    if rotator.circuit_breakers[p.id].should_attempt_request()
]
print(f"Available proxies: {len(available)}")
```

**Solutions**:
- Add more proxies to the pool
- Wait for circuit breakers to recover
- Check proxy diversity

---

### Problem: Metrics Not Updating

**Symptom**: Metrics queries return stale data

**Cause**: Aggregation not running or needs manual trigger

**Solutions**:

1. **Check aggregation timer**:
   ```python
   # Timer runs every 5 minutes automatically
   # Verify rotator is not closed
   ```

2. **Manual aggregation**:
   ```python
   rotator.retry_metrics.aggregate_hourly()
   ```

3. **Check current attempts**:
   ```python
   metrics = rotator.get_retry_metrics()
   print(f"Current attempts: {len(metrics.current_attempts)}")
   ```

---

## Performance Tuning

### Optimize for Success Rate

**Goal**: Maximize request success rate

```python
policy = RetryPolicy(
    max_attempts=5,                # More attempts
    backoff_strategy=BackoffStrategy.EXPONENTIAL,
    base_delay=1.0,
    max_backoff_delay=30.0,
    jitter=True,                   # Avoid thundering herd
)
```

### Optimize for Latency

**Goal**: Minimize total request time

```python
policy = RetryPolicy(
    max_attempts=2,                # Fewer attempts
    backoff_strategy=BackoffStrategy.FIXED,
    base_delay=0.5,                # Short delay
    timeout=3.0,                   # Quick timeout
)
```

### Optimize for Rate-Limited APIs

**Goal**: Respect API rate limits

```python
policy = RetryPolicy(
    max_attempts=3,
    backoff_strategy=BackoffStrategy.LINEAR,
    base_delay=10.0,               # Long delays
    retry_status_codes=[429, 502, 503, 504],
)
```

---

## Best Practices

### ? DO

1. **Use jitter** for high-concurrency scenarios
2. **Set timeouts** for time-sensitive operations
3. **Monitor circuit breakers** regularly
4. **Track metrics** for optimization
5. **Test with real proxies** in staging
6. **Configure per use case** (API-specific policies)

### ? DON'T

1. **Don't retry non-idempotent** operations without verification
2. **Don't set timeout < sum of retries** (will fail early)
3. **Don't disable circuit breakers** (removes protection)
4. **Don't ignore metrics** (losing optimization opportunities)
5. **Don't use excessive max_attempts** (>10 is rarely useful)

---

## REST API Usage

### Get Current Retry Policy

```bash
curl http://localhost:8000/api/v1/retry/policy
```

### Update Retry Policy

```bash
curl -X PUT http://localhost:8000/api/v1/retry/policy \
  -H "Content-Type: application/json" \
  -d '{
    "max_attempts": 5,
    "backoff_strategy": "exponential",
    "base_delay": 1.5,
    "jitter": true
  }'
```

### Check Circuit Breakers

```bash
# All proxies
curl http://localhost:8000/api/v1/circuit-breakers

# Specific proxy
curl http://localhost:8000/api/v1/circuit-breakers/proxy1.example.com:8080
```

### Reset Circuit Breaker

```bash
curl -X POST \
  http://localhost:8000/api/v1/circuit-breakers/proxy1.example.com:8080/reset
```

### Get Retry Metrics

```bash
# Summary
curl http://localhost:8000/api/v1/metrics/retries

# Time-series (last 24 hours)
curl http://localhost:8000/api/v1/metrics/retries/timeseries?hours=24

# Per-proxy stats
curl http://localhost:8000/api/v1/metrics/retries/by-proxy?hours=24
```

---

## Integration with Monitoring

### Export Metrics to Prometheus

```python
import time
import json

def export_to_prometheus():
    metrics = rotator.get_retry_metrics()
    summary = metrics.get_summary()
    
    # Format for Prometheus
    print(f'proxywhirl_total_retries {summary["total_retries"]}')
    print(f'proxywhirl_cb_events {summary["circuit_breaker_events_count"]}')
    
    for attempt, count in summary["success_by_attempt"].items():
        print(f'proxywhirl_success_by_attempt{{attempt="{attempt}"}} {count}')

# Run periodically
while True:
    export_to_prometheus()
    time.sleep(60)
```

### Log Circuit Breaker Events

```python
from loguru import logger

# Circuit breaker events are automatically logged
# Configure log level
logger.add(
    "circuit_breaker.log",
    level="WARNING",
    filter=lambda r: "circuit breaker" in r["message"].lower(),
)
```

### Alert on Widespread Failures

```python
def check_health():
    states = rotator.get_circuit_breaker_states()
    
    open_count = sum(
        1 for cb in states.values()
        if cb.state == CircuitBreakerState.OPEN
    )
    
    total_count = len(states)
    open_percentage = (open_count / total_count) * 100
    
    if open_percentage > 50:
        # Alert! More than 50% of proxies failing
        send_alert(f"WARNING: {open_percentage:.1f}% of proxies have open circuits")
```

---

## Advanced Features

### Intelligent Proxy Selection

The system automatically selects the best proxy for retries using:

**Scoring Formula**:
```
score = (0.7 ? success_rate) + (0.3 ? (1 - normalized_latency))
```

**Geo-Targeting Bonus**: +10% for matching region

**Example**:
```python
# Proxy with region metadata gets priority
proxy_us = Proxy(
    url="http://proxy-us.example.com:8080",
    metadata={"region": "US-EAST"},
)

# When retrying requests to US targets, proxy_us gets 10% bonus
```

### Per-Request Region Hint

```python
# Future feature: pass target_region hint
# Currently automatic based on proxy metadata
```

---

## Debugging

### Enable Detailed Logging

```python
from loguru import logger

logger.add(
    "retry_debug.log",
    level="DEBUG",
    format="{time} | {level} | {message}",
    filter=lambda r: "retry" in r["message"].lower(),
)
```

### Inspect Circuit Breaker State

```python
proxy_id = "proxy1.example.com:8080"
cb = rotator.circuit_breakers[proxy_id]

print(f"State: {cb.state.value}")
print(f"Failures: {cb.failure_count}/{cb.failure_threshold}")
print(f"Window: {cb.window_duration}s")
print(f"Failure times: {list(cb.failure_window)}")
```

### Trace Request Retries

```python
# Retry attempts are logged automatically with:
# - Attempt number
# - Proxy used
# - Delay before retry
# - Outcome (success/failure/timeout)

# Check logs for pattern matching "Retry attempt"
```

---

## Error Handling

### Retryable Errors

These errors trigger automatic retries:
- `httpx.ConnectError` (connection failed)
- `httpx.TimeoutException` (request timed out)
- `httpx.ReadTimeout` (read timed out)
- `httpx.WriteTimeout` (write timed out)
- `httpx.PoolTimeout` (pool exhausted)
- `httpx.NetworkError` (network issue)
- HTTP status codes in `retry_status_codes` list

### Non-Retryable Errors

These errors do NOT trigger retries:
- `ProxyAuthenticationError` (407 Proxy Auth Required)
- HTTP 4xx client errors (except configured codes)
- Non-network exceptions

---

## FAQ

### Q: How many retries should I configure?

**A**: Depends on use case:
- **High-volume APIs**: 3-5 attempts
- **Rate-limited APIs**: 2-3 attempts
- **Critical operations**: 1-2 attempts
- **Best practice**: Start with 3, tune based on metrics

### Q: Should I enable jitter?

**A**: Yes, for high-concurrency scenarios:
- Prevents thundering herd problem
- Distributes retry timing
- Minimal downside (<0.1ms overhead)

### Q: When should I retry POST requests?

**A**: Rarely. Only when:
- Operation is truly idempotent (e.g., idempotency key)
- Failure is clearly retryable (network, not business logic)
- You can tolerate duplicate operations
- **Never** for financial transactions or state changes

### Q: What's the difference between retry and failover?

**A**:
- **Retry**: Reattempt operation after delay (may use same proxy)
- **Failover**: Switch to different proxy after failure
- ProxyWhirl implements **both**: retries with intelligent proxy failover

### Q: How does half-open state work?

**A**: 
1. Circuit opens after threshold failures
2. After timeout (30s), enters half-open
3. Allows **one test request**
4. Success ? closes circuit
5. Failure ? reopens circuit (timeout resets)

### Q: Can I disable retries?

**A**: Yes, in two ways:
```python
# Option 1: Pass None for retry_policy
rotator._make_request("GET", url, retry_policy=None)

# Option 2: Set max_attempts=1 (no retries, just one attempt)
policy = RetryPolicy(max_attempts=1)
```

### Q: How much memory do metrics use?

**A**: Typically <15MB for 10k requests/hour:
- Current attempts: ~2-3 MB (last hour, raw data)
- Hourly aggregates: ~12 KB (24 hours)
- Circuit breaker events: ~150 KB (last 1000)
- **Total**: <15 MB

### Q: Do circuit breakers persist across restarts?

**A**: No, by design (FR-021):
- All circuit breakers reset to CLOSED on startup
- System re-learns proxy health
- Simpler implementation, no storage needed

---

## Performance Considerations

### Memory

**Current attempts** (raw data):
- Retention: Last hour
- Max entries: 10,000
- Memory: ~2-3 MB

**Hourly aggregates**:
- Retention: 24 hours
- Entries: 24
- Memory: ~12 KB

**Circuit breaker events**:
- Retention: Last 1000 events
- Memory: ~150 KB

**Total**: <15 MB typical

### CPU

**Retry overhead**:
- No retries: <0.1ms
- With retries: Dominated by network time
- Circuit breaker check: <0.001ms
- Metrics recording: <0.01ms

### Network

**Retry traffic**:
- Increases based on failure rate
- Circuit breakers reduce wasted traffic
- Intelligent selection improves first-retry success

---

## Migration Guide

### From No Retry to Retry-Enabled

**Old code** (no retry):
```python
rotator = ProxyRotator(proxies=proxies)
response = rotator.get(url)  # Fails immediately on error
```

**New code** (retry enabled by default):
```python
rotator = ProxyRotator(proxies=proxies)
response = rotator.get(url)  # Automatically retries
```

**No changes needed!** Retry is enabled by default with sensible settings.

### Customizing Retry Behavior

**Add custom policy**:
```python
policy = RetryPolicy(max_attempts=5, jitter=True)
rotator = ProxyRotator(proxies=proxies, retry_policy=policy)
```

### Disabling Retry for Specific Requests

**Per-request disable**:
```python
rotator._make_request("GET", url, retry_policy=None)
```

---

## Examples Repository

See `examples/retry_examples.py` for 10 runnable examples covering:
1. Basic automatic retry
2. Custom retry policy
3. Per-request override
4. Circuit breaker monitoring
5. Retry metrics
6. Non-idempotent requests
7. Backoff strategies
8. Geo-targeted retry
9. Manual circuit breaker reset
10. Timeout management

Run: `python examples/retry_examples.py`

---

## Related Documentation

- **Feature Spec**: `/specs/014-retry-failover-logic/spec.md`
- **Quick Start**: `/specs/014-retry-failover-logic/quickstart.md`
- **API Contract**: `/specs/014-retry-failover-logic/contracts/retry-api.yaml`
- **Implementation Summary**: `/RETRY_FAILOVER_IMPLEMENTATION_SUMMARY.md`
- **Feature Complete**: `/RETRY_FAILOVER_FEATURE_COMPLETE.md`

---

## Support

For issues or questions:
1. Check this troubleshooting guide
2. Review examples in `examples/retry_examples.py`
3. Check integration tests for usage patterns
4. Open GitHub issue with:
   - Retry policy configuration
   - Circuit breaker states
   - Metrics summary
   - Error messages

---

**Last Updated**: 2025-11-02  
**Version**: 1.0.0  
**Status**: Production Ready
