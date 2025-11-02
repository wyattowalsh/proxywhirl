# Quick Start: Retry & Failover Logic

**Feature**: 014-retry-failover-logic  
**Date**: 2025-11-02

## Overview

This guide provides quick examples for using retry and failover logic with ProxyWhirl. All examples assume you have the core `proxywhirl` package installed and configured.

---

## Basic Usage

### 1. Enable Automatic Retries (Default Behavior)

```python
from proxywhirl import ProxyRotator, Proxy

# Create rotator with retry enabled by default
proxies = [
    Proxy(url="http://proxy1.example.com:8080"),
    Proxy(url="http://proxy2.example.com:8080"),
    Proxy(url="http://proxy3.example.com:8080"),
]

rotator = ProxyRotator(proxies=proxies)

# Request with automatic retries (default: 3 attempts, exponential backoff)
response = rotator.request("https://api.example.com/data")
print(response.status_code)
```

**What happens**:
- If request fails (5xx error), automatically retries with exponential backoff
- 1st retry: wait 1 second
- 2nd retry: wait 2 seconds  
- 3rd retry: wait 4 seconds
- If all fail, raises exception

---

### 2. Custom Retry Policy

```python
from proxywhirl import ProxyRotator, RetryPolicy, BackoffStrategy

# Custom retry policy
policy = RetryPolicy(
    max_attempts=5,                          # Try up to 5 times
    backoff_strategy=BackoffStrategy.LINEAR, # Linear backoff (2s, 4s, 6s, 8s)
    base_delay=2.0,                          # Base delay 2 seconds
    retry_status_codes=[502, 503, 504, 429], # Also retry on 429 Too Many Requests
    jitter=True                              # Add random jitter to delays
)

rotator = ProxyRotator(proxies=proxies, retry_policy=policy)

# All requests use custom policy
response = rotator.request("https://api.example.com/data")
```

**Available Backoff Strategies**:
- `EXPONENTIAL`: delay = base × (multiplier ^ attempt)
- `LINEAR`: delay = base × (attempt + 1)
- `FIXED`: delay = base (constant)

---

### 3. Per-Request Policy Override

```python
from proxywhirl import ProxyRotator, RetryPolicy

# Global policy: retry 3 times
rotator = ProxyRotator(
    proxies=proxies,
    retry_policy=RetryPolicy(max_attempts=3)
)

# Override for specific request: only 1 retry
response = rotator.request(
    "https://api.example.com/critical",
    retry_policy=RetryPolicy(max_attempts=1, base_delay=0.5)
)

# Or disable retries for this request
response = rotator.request(
    "https://api.example.com/no-retry",
    retry_policy=None  # No retries
)
```

---

### 4. Circuit Breaker Monitoring

```python
# Check circuit breaker states
states = rotator.get_circuit_breaker_states()

for proxy_id, circuit_breaker in states.items():
    print(f"Proxy: {proxy_id}")
    print(f"  State: {circuit_breaker.state.value}")
    print(f"  Failures: {circuit_breaker.failure_count}/{circuit_breaker.failure_threshold}")
    
    if circuit_breaker.state == CircuitBreakerState.OPEN:
        print(f"  Next test: {circuit_breaker.next_test_time}")
```

**Circuit Breaker States**:
- `CLOSED`: Proxy working normally
- `OPEN`: Proxy excluded (too many failures)
- `HALF_OPEN`: Testing recovery

---

### 5. Retry Metrics

```python
# Get retry statistics
metrics = rotator.get_retry_metrics()

print(f"Total retries: {metrics.total_retries}")
print(f"Success by attempt: {metrics.success_by_attempt}")
# Example output: {0: 850, 1: 120, 2: 25, 3: 5}
# 850 succeeded on first try, 120 on second retry, etc.

print(f"Circuit breaker events: {len(metrics.circuit_breaker_events)}")
```

---

## Advanced Examples

### 6. Non-Idempotent Requests

```python
# By default, POST/PUT requests don't retry (not idempotent)
response = rotator.request("https://api.example.com/create", method="POST", json=data)
# No retries unless explicitly enabled

# Enable retries for non-idempotent request (use with caution)
policy = RetryPolicy(retry_non_idempotent=True)
response = rotator.request(
    "https://api.example.com/create",
    method="POST",
    json=data,
    retry_policy=policy
)
```

---

### 7. Custom Status Codes for Retry

```python
# Retry on specific status codes only
policy = RetryPolicy(
    retry_status_codes=[502, 503, 504, 408],  # Include 408 Request Timeout
    max_attempts=3
)

rotator = ProxyRotator(proxies=proxies, retry_policy=policy)
```

---

### 8. Timeout Management

```python
# Set total timeout (including all retries)
policy = RetryPolicy(
    max_attempts=5,
    base_delay=2.0,
    timeout=15.0  # Total timeout: 15 seconds
)

# If retries would exceed 15s, stops early
response = rotator.request("https://api.example.com/data", retry_policy=policy)
```

---

## REST API Usage

If you're running the ProxyWhirl REST API server (feature 003):

### Get Global Retry Policy

```bash
curl http://localhost:8000/api/v1/retry/policy
```

### Update Global Retry Policy

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

### Check Circuit Breaker States

```bash
# All proxies
curl http://localhost:8000/api/v1/circuit-breakers

# Specific proxy
curl http://localhost:8000/api/v1/circuit-breakers/proxy1.example.com:8080
```

### Manually Reset Circuit Breaker

```bash
curl -X POST http://localhost:8000/api/v1/circuit-breakers/proxy1.example.com:8080/reset
```

### Get Retry Metrics

```bash
# Summary
curl http://localhost:8000/api/v1/metrics/retries

# Time-series data (last 24 hours)
curl http://localhost:8000/api/v1/metrics/retries/timeseries

# Per-proxy statistics
curl http://localhost:8000/api/v1/metrics/retries/by-proxy?hours=24
```

---

## Configuration Best Practices

### For High-Volume APIs

```python
# Aggressive retries, fast failover
policy = RetryPolicy(
    max_attempts=5,
    backoff_strategy=BackoffStrategy.EXPONENTIAL,
    base_delay=0.5,  # Start fast
    max_backoff_delay=10.0,  # Cap at 10s
    jitter=True  # Avoid thundering herd
)
```

### For Rate-Limited APIs

```python
# Conservative retries, longer waits
policy = RetryPolicy(
    max_attempts=3,
    backoff_strategy=BackoffStrategy.LINEAR,
    base_delay=5.0,  # Give API time to recover
    retry_status_codes=[429, 502, 503, 504]  # Include rate limit errors
)
```

### For Critical Operations

```python
# Fewer retries, fail fast
policy = RetryPolicy(
    max_attempts=2,  # Only 1 retry
    base_delay=1.0,
    timeout=5.0  # Quick timeout
)
```

---

## Monitoring & Observability

### Log Retry Attempts

Retry attempts are automatically logged using `loguru`:

```python
# Logs include:
# - Retry attempt number
# - Proxy used
# - Delay before retry
# - Outcome

# Configure log level
from loguru import logger
logger.add("retry.log", level="INFO", filter=lambda record: "retry" in record["message"])
```

### Integrate with Monitoring Systems

```python
# Export metrics periodically
import time
import json

def export_metrics():
    metrics = rotator.get_retry_metrics()
    
    # Export to monitoring system
    metrics_data = {
        "timestamp": time.time(),
        "total_retries": metrics.total_retries,
        "success_by_attempt": metrics.success_by_attempt,
        "circuit_breaker_events": len(metrics.circuit_breaker_events)
    }
    
    # Send to Prometheus, DataDog, etc.
    print(json.dumps(metrics_data))

# Run periodically (every 60s)
import threading
timer = threading.Timer(60.0, export_metrics)
timer.start()
```

---

## Troubleshooting

### All Proxies Have Open Circuit Breakers

**Symptom**: Requests fail with "503 Service Temporarily Unavailable"

**Cause**: All proxies experiencing failures

**Solution**:
1. Check proxy health manually
2. Wait for circuit breakers to enter half-open state (default: 30s)
3. Or manually reset: `rotator.reset_circuit_breaker(proxy_id)`

### Retries Taking Too Long

**Symptom**: Requests timing out or taking >5 seconds

**Solutions**:
- Reduce `max_attempts`
- Use `FIXED` backoff strategy
- Set lower `max_backoff_delay`
- Add `timeout` to policy

```python
policy = RetryPolicy(
    max_attempts=2,
    backoff_strategy=BackoffStrategy.FIXED,
    base_delay=1.0,
    timeout=3.0  # Hard limit
)
```

### High Memory Usage

**Symptom**: Memory growing over time

**Cause**: Metrics retention

**Solution**: Configure shorter retention (default: 24h)

```python
# Not directly configurable in v1, metrics auto-cleanup after 24h
# Monitor with: len(rotator.get_retry_metrics().current_attempts)
```

---

## Next Steps

- **Full Documentation**: See `/docs/RETRY_FAILOVER_GUIDE.md`
- **API Reference**: See `/specs/014-retry-failover-logic/contracts/retry-api.yaml`
- **Examples**: See `/examples/retry_examples.py`
- **Testing**: See `/tests/integration/test_retry_integration.py`

**Questions?** Open an issue on GitHub or check the FAQ in the main documentation.
