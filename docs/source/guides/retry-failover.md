---
title: Retry & Failover Guide
---

# Retry & Failover Guide

ProxyWhirl provides intelligent retry logic, circuit breaker protection, and automatic proxy failover to maximize request success rates. This guide covers the complete retry and failover system, from basic configuration to advanced observability.

## Architecture Overview

The retry system consists of four main components:

1. **RetryPolicy** - Configures retry behavior and backoff strategies
2. **RetryExecutor** - Orchestrates retry logic with intelligent proxy selection
3. **CircuitBreaker** - Protects against cascading failures using state machine transitions
4. **RetryMetrics** - Collects observability data for monitoring and analysis

## When to Use Retry vs Failover

### Retry (Same Proxy)
Use retry when:
- Network is temporarily unstable (connection timeout, packet loss)
- Target server returns 502/503/504 (gateway errors, service temporarily unavailable)
- Request is idempotent (GET, HEAD, OPTIONS, DELETE, PUT)

### Failover (Different Proxy)
Use failover when:
- Proxy authentication fails (407)
- Proxy consistently returns errors (circuit breaker opens)
- Specific geo-targeting or performance requirements exist
- One proxy exhausts rate limits

ProxyWhirl combines both: it retries with backoff on the current proxy, then fails over to a better proxy if retries are exhausted.

## RetryPolicy Configuration

### Basic Configuration

```python
from proxywhirl import ProxyRotator, RetryPolicy, BackoffStrategy

# Default policy: 3 attempts, exponential backoff
rotator = ProxyRotator()

# Custom policy
policy = RetryPolicy(
    max_attempts=5,                          # Maximum retry attempts
    backoff_strategy=BackoffStrategy.EXPONENTIAL,
    base_delay=1.0,                          # Initial delay (seconds)
    multiplier=2.0,                          # Exponential multiplier
    max_backoff_delay=30.0,                  # Maximum delay cap
    jitter=True,                             # Randomize delays ±50%
    retry_status_codes=[502, 503, 504],      # Retryable HTTP errors
    timeout=60.0,                            # Total timeout for all attempts
    retry_non_idempotent=False,              # Don't retry POST by default
)

rotator = ProxyRotator(retry_policy=policy)
```

### Backoff Strategies

ProxyWhirl supports three backoff strategies:

#### Exponential Backoff (Recommended)
Best for network failures and overloaded servers. Delays increase exponentially to give systems time to recover.

```python
policy = RetryPolicy(
    backoff_strategy=BackoffStrategy.EXPONENTIAL,
    base_delay=1.0,
    multiplier=2.0,
    max_backoff_delay=30.0,
    jitter=True,  # Prevents thundering herd
)

# Attempt 0: 1.0s ± 50% jitter
# Attempt 1: 2.0s ± 50% jitter
# Attempt 2: 4.0s ± 50% jitter
# Attempt 3: 8.0s ± 50% jitter
# Attempt 4: 16.0s ± 50% jitter
# Attempt 5+: 30.0s (capped) ± 50% jitter
```

#### Linear Backoff
Best for predictable retry patterns. Delays increase linearly.

```python
policy = RetryPolicy(
    backoff_strategy=BackoffStrategy.LINEAR,
    base_delay=2.0,
    max_backoff_delay=10.0,
)

# Attempt 0: 2.0s
# Attempt 1: 4.0s
# Attempt 2: 6.0s
# Attempt 3: 8.0s
# Attempt 4: 10.0s (capped)
```

#### Fixed Backoff
Best for testing or when delays should be constant.

```python
policy = RetryPolicy(
    backoff_strategy=BackoffStrategy.FIXED,
    base_delay=5.0,
)

# All attempts: 5.0s
```

### Jitter Explained

Jitter adds randomization to delays (±50%) to prevent synchronized retries across multiple clients:

```python
# Without jitter: All clients retry at exactly 1.0s, 2.0s, 4.0s...
# With jitter: Clients retry at random times:
#   Client A: 0.7s, 1.3s, 2.8s...
#   Client B: 1.4s, 2.9s, 5.1s...
#   Client C: 0.9s, 1.1s, 3.7s...
```

This prevents "thundering herd" problems where many clients overwhelm a recovering server.

### Retryable Status Codes

By default, ProxyWhirl retries on gateway errors:

```python
# Default retry status codes
retry_status_codes = [502, 503, 504]

# Custom status codes (must be 5xx)
policy = RetryPolicy(
    retry_status_codes=[500, 502, 503, 504, 507, 508]
)
```

4xx errors (client errors) are never retried as they indicate permanent failures.

### Timeout Behavior

The `timeout` parameter caps total execution time across all retry attempts:

```python
policy = RetryPolicy(
    max_attempts=10,
    timeout=30.0,  # Total timeout for all attempts
)

# If 30s elapses after 3 attempts, remaining 7 attempts are skipped
# Raises: ProxyConnectionError("Request timeout after 30.00s")
```

### Non-Idempotent Requests

By default, POST/PATCH requests are not retried (they're not idempotent):

```python
# Default: POST fails immediately without retry
rotator.request("POST", url, json=data)

# Enable retries for POST (use with caution!)
policy = RetryPolicy(retry_non_idempotent=True)
rotator = ProxyRotator(retry_policy=policy)

# Now POST will retry on network failures
rotator.request("POST", url, json=data)
```

**Warning:** Only enable `retry_non_idempotent` if your API is idempotent (e.g., uses idempotency keys).

## Circuit Breaker Configuration

Circuit breakers protect against cascading failures by temporarily removing unhealthy proxies from the rotation pool.

### Sync vs Async Circuit Breakers

ProxyWhirl provides two circuit breaker implementations:

- **`CircuitBreaker`** - Synchronous implementation using `threading.Lock`
- **`AsyncCircuitBreaker`** - Async implementation using `asyncio`-compatible locks

**When to use which:**

```python
# ✅ For synchronous code - use CircuitBreaker
from proxywhirl import CircuitBreaker

cb = CircuitBreaker(proxy_id="proxy-1")
cb.record_failure()  # Thread-safe
if cb.should_attempt_request():
    cb.record_success()

# ✅ For async code - use AsyncCircuitBreaker
from proxywhirl.circuit_breaker_async import AsyncCircuitBreaker

cb = AsyncCircuitBreaker(proxy_id="proxy-1")
await cb.record_failure()  # Event loop safe
if await cb.should_attempt_request():
    await cb.record_success()
```

**WARNING:** Do NOT mix sync locks with async code. The `CircuitBreaker` class has some async methods (`save_state`, `load_state`) for backward compatibility, but these use `threading.Lock` internally which can block the event loop. For production async applications, always use `AsyncCircuitBreaker`.

### State Machine

Circuit breakers transition through three states:

```
CLOSED → OPEN → HALF_OPEN → CLOSED
  ↑                            ↓
  └────────────────────────────┘
```

1. **CLOSED** - Normal operation, proxy is available
2. **OPEN** - Proxy excluded from rotation (too many failures)
3. **HALF_OPEN** - Testing recovery with limited requests

### Thresholds and Configuration

```python
from proxywhirl.circuit_breaker import CircuitBreaker, CircuitBreakerConfig

# Circuit breakers are created automatically by ProxyRotator
# Access via rotator.circuit_breakers dict

proxy = rotator.get_proxy()
cb = rotator.circuit_breakers[str(proxy.id)]

# Configuration (set on CircuitBreaker creation)
print(cb.failure_threshold)   # Default: 5 failures
print(cb.window_duration)     # Default: 60 seconds (rolling window)
print(cb.timeout_duration)    # Default: 30 seconds (OPEN timeout)
```

### Circuit Breaker Persistence

Circuit breaker state can optionally persist across application restarts using SQLite storage.

**For async applications (recommended):**

```python
from proxywhirl.circuit_breaker_async import AsyncCircuitBreaker, CircuitBreakerConfig
from proxywhirl.storage import SQLiteStorage

# Configure persistence
cb_config = CircuitBreakerConfig(
    persist_state=True,            # Enable state persistence
    failure_threshold=5,
    window_duration=60.0,
    timeout_duration=30.0,
)

# Initialize storage
storage = SQLiteStorage("proxywhirl.db")
await storage.initialize()

# Create async circuit breaker with persistence
cb = await AsyncCircuitBreaker.create_with_storage(
    proxy_id="proxy-123",
    storage=storage,
    config=cb_config,
)

# State automatically saves to database
await cb.record_failure()
await cb.save_state()

# On next startup, state is restored
cb2 = await AsyncCircuitBreaker.create_with_storage(
    proxy_id="proxy-123",
    storage=storage,
    config=cb_config,
)
print(cb2.state)           # Restored from database
```

**For sync applications:**

```python
from proxywhirl import CircuitBreaker, CircuitBreakerConfig
from proxywhirl.storage import SQLiteStorage

cb_config = CircuitBreakerConfig(persist_state=True)
storage = SQLiteStorage("proxywhirl.db")
await storage.initialize()

# Note: CircuitBreaker has async methods for I/O but uses threading.Lock
cb = await CircuitBreaker.create_with_storage(
    proxy_id="proxy-123",
    storage=storage,
    config=cb_config,
)
print(cb2.failure_count)   # Restored from database
```

**Persistence Benefits:**

- **Prevents flood on restart**: Circuit breakers remain OPEN if they were failing
- **Maintains failure history**: Rolling window survives application restarts
- **Coordination**: Multiple processes can share circuit breaker state via shared database

**Storage Schema:**

The `CircuitBreakerStateTable` stores:
- `proxy_id`: Unique proxy identifier
- `state`: Current state (CLOSED/OPEN/HALF_OPEN)
- `failure_count`: Current failure count
- `failure_window_json`: JSON-serialized failure timestamps
- `next_test_time`: When to test recovery (for OPEN state)
- `last_state_change`: Timestamp of last state transition

```{warning}
Enable persistence only when necessary - it adds database I/O overhead on every state change.
```

### State Transitions

#### CLOSED → OPEN
Circuit opens when failure count exceeds threshold within the rolling window:

```python
cb = CircuitBreaker(
    proxy_id=str(proxy.id),
    failure_threshold=5,
    window_duration=60.0,
)

# Record 5 failures within 60 seconds
for _ in range(5):
    cb.record_failure()

print(cb.state)  # CircuitBreakerState.OPEN
print(cb.failure_count)  # 5
```

#### OPEN → HALF_OPEN
Circuit transitions to HALF_OPEN after timeout duration elapses:

```python
import time

# Circuit is OPEN
print(cb.state)  # CircuitBreakerState.OPEN

# Check after timeout (30s default)
time.sleep(30)

# Next request triggers transition to HALF_OPEN
if cb.should_attempt_request():
    print(cb.state)  # CircuitBreakerState.HALF_OPEN
```

#### HALF_OPEN → CLOSED
Circuit closes if test request succeeds:

```python
# Circuit is HALF_OPEN
cb.record_success()

print(cb.state)  # CircuitBreakerState.CLOSED
print(cb.failure_count)  # 0 (reset)
```

#### HALF_OPEN → OPEN
Circuit reopens if test request fails:

```python
# Circuit is HALF_OPEN
cb.record_failure()

print(cb.state)  # CircuitBreakerState.OPEN
# Timeout duration resets, must wait another 30s
```

### Rolling Window Behavior

The circuit breaker uses a sliding window to track recent failures:

```python
cb = CircuitBreaker(
    proxy_id=str(proxy.id),
    failure_threshold=3,
    window_duration=60.0,
)

# At t=0: Record 2 failures
cb.record_failure()  # failure_count = 1
cb.record_failure()  # failure_count = 2
print(cb.state)  # CLOSED (below threshold)

# At t=65: Old failures expired (outside 60s window)
time.sleep(65)
print(cb.failure_count)  # 0 (window cleaned automatically)

# New failure doesn't trigger circuit
cb.record_failure()  # failure_count = 1
print(cb.state)  # CLOSED
```

### Manual Reset

Reset circuit breaker to CLOSED state manually:

```python
# Force reset (useful for testing or manual intervention)
cb.reset()

print(cb.state)  # CircuitBreakerState.CLOSED
print(cb.failure_count)  # 0
```

## Intelligent Proxy Selection

When retries are exhausted, ProxyWhirl automatically selects the best alternative proxy using performance-based scoring.

### Selection Algorithm

The executor scores each candidate proxy using:

```text
score = (0.7 × success_rate) + (0.3 × (1 - normalized_latency))
```

- **70% weight** on success rate (reliability)
- **30% weight** on latency (performance)
- **10% bonus** for geo-targeting match (optional)

### Example: Performance-Based Selection

```python
from proxywhirl import Proxy, ProxyRotator

# Create proxies with different success rates
proxy1 = Proxy(url="http://proxy1.example.com:8080")
proxy1.total_requests = 100
proxy1.total_successes = 95  # 95% success rate

proxy2 = Proxy(url="http://proxy2.example.com:8080")
proxy2.total_requests = 100
proxy2.total_successes = 60  # 60% success rate

rotator = ProxyRotator(proxies=[proxy1, proxy2])

# Intelligent selection prioritizes proxy1
executor = rotator.retry_executor
selected = executor.select_retry_proxy([proxy1, proxy2], failed_proxy)

print(selected.url)  # http://proxy1.example.com:8080
```

### Example: Geo-Targeted Selection

```python
# Create proxies with different regions
proxy_us = Proxy(
    url="http://proxy-us.example.com:8080",
    metadata={"region": "US-EAST"},
)
proxy_us.total_requests = 100
proxy_us.total_successes = 80  # 80% success rate

proxy_eu = Proxy(
    url="http://proxy-eu.example.com:8080",
    metadata={"region": "EU-WEST"},
)
proxy_eu.total_requests = 100
proxy_eu.total_successes = 85  # 85% success rate (slightly better)

rotator = ProxyRotator(proxies=[proxy_us, proxy_eu])

# Select with target region
executor = rotator.retry_executor
selected = executor.select_retry_proxy(
    [proxy_us, proxy_eu],
    failed_proxy,
    target_region="US-EAST"
)

# Selects proxy_us despite lower success rate (10% region bonus)
print(selected.url)  # http://proxy-us.example.com:8080
```

### Exclusion Rules

The selection algorithm excludes:

1. **Failed proxy** - The proxy that just failed is never selected
2. **Open circuits** - Proxies with open circuit breakers
3. **Half-open pending** - Proxies already testing recovery

```python
# If all proxies are excluded, returns None
selected = executor.select_retry_proxy([only_failed_proxy], failed_proxy)
print(selected)  # None
```

## RetryMetrics and Observability

ProxyWhirl tracks detailed metrics for monitoring, debugging, and analytics.

### Collecting Metrics

```python
from proxywhirl import ProxyRotator

rotator = ProxyRotator()

# Metrics are automatically collected
response = rotator.request("GET", "https://httpbin.org/ip")

# Access metrics
metrics = rotator.retry_metrics
print(metrics.get_summary())
```

### Summary Statistics

```python
summary = metrics.get_summary()

print(summary)
# {
#     "total_retries": 42,
#     "success_by_attempt": {
#         0: 35,  # 35 requests succeeded on first attempt
#         1: 5,   # 5 requests succeeded on second attempt
#         2: 2,   # 2 requests succeeded on third attempt
#     },
#     "circuit_breaker_events_count": 3,
#     "retention_hours": 24,
# }
```

### Time-Series Data

```python
# Get hourly aggregated data for last 24 hours
timeseries = metrics.get_timeseries(hours=24)

for datapoint in timeseries:
    print(datapoint)
# {
#     "timestamp": "2025-12-27T14:00:00+00:00",
#     "total_requests": 150,
#     "total_retries": 25,
#     "success_rate": 0.94,
#     "avg_latency": 0.234,
# }
```

### Per-Proxy Statistics

```python
# Get retry statistics by proxy
by_proxy = metrics.get_by_proxy(hours=24)

for proxy_id, stats in by_proxy.items():
    print(f"Proxy {proxy_id}: {stats}")
# {
#     "proxy_id": "550e8400-e29b-41d4-a716-446655440000",
#     "total_attempts": 50,
#     "success_count": 45,
#     "failure_count": 5,
#     "avg_latency": 0.234,
#     "circuit_breaker_opens": 2,
# }
```

### Circuit Breaker Events

```python
# Access circuit breaker state changes
for event in metrics.circuit_breaker_events:
    print(f"{event.timestamp}: {event.proxy_id}")
    print(f"  {event.from_state} → {event.to_state}")
    print(f"  Failure count: {event.failure_count}")

# Example output:
# 2025-12-27 14:32:15+00:00: 550e8400-e29b-41d4-a716-446655440000
#   CLOSED → OPEN
#   Failure count: 5
#
# 2025-12-27 14:32:45+00:00: 550e8400-e29b-41d4-a716-446655440000
#   OPEN → HALF_OPEN
#   Failure count: 5
#
# 2025-12-27 14:32:47+00:00: 550e8400-e29b-41d4-a716-446655440000
#   HALF_OPEN → CLOSED
#   Failure count: 0
```

### Hourly Aggregation

Metrics automatically aggregate into hourly summaries to prevent unbounded memory growth:

```python
# Manually trigger aggregation (normally runs automatically)
metrics.aggregate_hourly()

# View aggregates
for hour, agg in metrics.hourly_aggregates.items():
    print(f"{hour}: {agg.total_requests} requests, {agg.total_retries} retries")
    print(f"  Success by attempt: {agg.success_by_attempt}")
    print(f"  Failure by reason: {agg.failure_by_reason}")
```

### Retention Configuration

```python
from proxywhirl.retry_metrics import RetryMetrics

# Custom retention and limits
metrics = RetryMetrics(
    retention_hours=48,        # Keep data for 48 hours
    max_current_attempts=5000,  # Limit raw attempts deque
)

rotator = ProxyRotator()
rotator.retry_metrics = metrics
```

## RetryExecutor Deep Dive

The `RetryExecutor` is the core orchestration class that coordinates retry logic, circuit breakers, and metrics collection.

### How Retries Work Internally

When you call `rotator.request()`, the following sequence occurs:

1. **Idempotency Check**: Determines if the HTTP method is safe to retry (GET/HEAD/OPTIONS/DELETE/PUT are idempotent)
2. **Retry Loop**: Executes up to `max_attempts` attempts with backoff delays
3. **Circuit Breaker Check**: Verifies the proxy's circuit breaker allows the request
4. **Request Execution**: Calls the underlying HTTP client
5. **Status Code Check**: Validates response status against `retry_status_codes`
6. **Error Classification**: Determines if exceptions are retryable (timeouts, connection errors)
7. **Metrics Recording**: Logs attempt outcome, latency, and circuit breaker events
8. **Proxy Failover**: If all retries exhausted, selects next best proxy automatically

### Retryable vs Non-Retryable Errors

The executor classifies errors into two categories:

**Retryable Errors** (trigger retry with backoff):
- `httpx.ConnectError` - Connection refused, DNS failure
- `httpx.TimeoutException` - Request/connect timeout
- `httpx.ReadTimeout` - Response body read timeout
- `httpx.WriteTimeout` - Request body write timeout
- `httpx.PoolTimeout` - Connection pool exhausted
- `httpx.NetworkError` - Generic network failure
- HTTP 502, 503, 504 status codes (configurable)

**Non-Retryable Errors** (fail immediately):
- HTTP 4xx errors (client errors - request won't succeed on retry)
- `NonRetryableError` (custom application errors)
- Any exception not in the retryable types list

```python
from proxywhirl.retry_executor import RetryExecutor, NonRetryableError

# Custom error handling
try:
    response = rotator.request("GET", url)
except NonRetryableError as e:
    # Authentication failure, malformed request, etc.
    print(f"Cannot retry: {e}")
```

### Direct RetryExecutor Usage

For advanced use cases, you can use `RetryExecutor` directly:

```python
from proxywhirl import ProxyRotator, Proxy, RetryPolicy
from proxywhirl.retry_executor import RetryExecutor
import httpx

# Create executor with custom policy
policy = RetryPolicy(max_attempts=5, base_delay=2.0)
rotator = ProxyRotator()
executor = RetryExecutor(
    retry_policy=policy,
    circuit_breakers=rotator.circuit_breakers,
    retry_metrics=rotator.retry_metrics,
)

# Create request function
proxy = Proxy(url="http://proxy.example.com:8080")
def request_fn():
    client = httpx.Client(proxies={"all://": proxy.url})
    return client.get("https://api.example.com/data")

# Execute with retry
response = executor.execute_with_retry(
    request_fn=request_fn,
    proxy=proxy,
    method="GET",
    url="https://api.example.com/data",
    request_id="custom-request-123",  # Optional tracking ID
)
```

## Integration with ProxyRotator

### Basic Usage

```python
from proxywhirl import ProxyRotator, RetryPolicy, BackoffStrategy

# Automatic retry and failover
policy = RetryPolicy(
    max_attempts=5,
    backoff_strategy=BackoffStrategy.EXPONENTIAL,
    base_delay=1.0,
    jitter=True,
)

rotator = ProxyRotator(retry_policy=policy)

# Request automatically retries and fails over
response = rotator.request("GET", "https://httpbin.org/ip")
```

### Custom Error Handling

```python
from proxywhirl.exceptions import ProxyConnectionError
from proxywhirl.retry_executor import NonRetryableError

try:
    response = rotator.request("GET", url)
except ProxyConnectionError as e:
    # All retries exhausted across all proxies
    print(f"Request failed after all retries: {e}")
except NonRetryableError as e:
    # Non-retryable error (e.g., authentication failure)
    print(f"Non-retryable error: {e}")
```

### Monitoring Circuit Breakers

```python
# Check circuit breaker status
for proxy in rotator.pool.proxies:
    cb = rotator.circuit_breakers.get(str(proxy.id))
    if cb:
        print(f"{proxy.url}: {cb.state.value}")
        print(f"  Failures: {cb.failure_count}/{cb.failure_threshold}")
        if cb.next_test_time:
            import time
            wait_time = cb.next_test_time - time.time()
            print(f"  Retry in: {wait_time:.1f}s")
```

### Manual Circuit Reset

```python
# Reset all circuit breakers
for cb in rotator.circuit_breakers.values():
    cb.reset()

# Reset specific proxy
proxy = rotator.get_proxy()
rotator.circuit_breakers[str(proxy.id)].reset()
```

### Integration with Rotation Strategies

Retry and failover logic works seamlessly with all rotation strategies:

#### Round-Robin with Automatic Failover

```python
from proxywhirl import ProxyRotator, Proxy, RetryPolicy
from proxywhirl.strategies import RoundRobinStrategy

# Round-robin ensures fair distribution
rotator = ProxyRotator(
    proxies=[
        Proxy(url="http://proxy1.example.com:8080"),
        Proxy(url="http://proxy2.example.com:8080"),
        Proxy(url="http://proxy3.example.com:8080"),
    ],
    strategy=RoundRobinStrategy(),
    retry_policy=RetryPolicy(max_attempts=3),
)

# If proxy1 fails, automatically retries then fails over to proxy2
response = rotator.request("GET", "https://api.example.com/data")
```

#### Weighted Strategy with Performance-Based Failover

```python
from proxywhirl.strategies import WeightedStrategy

# Higher weight = more traffic
rotator = ProxyRotator(
    proxies=[
        Proxy(url="http://premium.example.com:8080", weight=3.0),  # 60% of traffic
        Proxy(url="http://standard.example.com:8080", weight=2.0), # 40% of traffic
    ],
    strategy=WeightedStrategy(),
    retry_policy=RetryPolicy(max_attempts=5),
)

# Premium proxy fails → retries on premium → fails over to standard
# Next request still prefers premium (weighted selection)
response = rotator.request("GET", "https://api.example.com/data")
```

#### Geo-Targeted Strategy with Regional Failover

```python
from proxywhirl.strategies import GeoTargetedStrategy

# Geo-targeted proxies
rotator = ProxyRotator(
    proxies=[
        Proxy(url="http://us-east.example.com:8080", metadata={"region": "US-EAST"}),
        Proxy(url="http://us-west.example.com:8080", metadata={"region": "US-WEST"}),
        Proxy(url="http://eu-west.example.com:8080", metadata={"region": "EU-WEST"}),
    ],
    strategy=GeoTargetedStrategy(target_region="US-EAST"),
    retry_policy=RetryPolicy(max_attempts=3),
)

# Prefers US-EAST → fails over to US-WEST (same country) → then EU-WEST
response = rotator.request("GET", "https://api.example.com/data")
```

#### Performance-Based Strategy with Dynamic Failover

```python
from proxywhirl.strategies import PerformanceBasedStrategy

# Automatically selects fastest, most reliable proxy
rotator = ProxyRotator(
    proxies=[
        Proxy(url="http://proxy1.example.com:8080"),
        Proxy(url="http://proxy2.example.com:8080"),
        Proxy(url="http://proxy3.example.com:8080"),
    ],
    strategy=PerformanceBasedStrategy(),
    retry_policy=RetryPolicy(max_attempts=3),
)

# Strategy considers:
# - Success rate (from proxy.total_successes / proxy.total_requests)
# - Average latency (from RetryMetrics)
# - Circuit breaker state (skips OPEN circuits)

for i in range(100):
    response = rotator.request("GET", f"https://api.example.com/data/{i}")
    # Over time, fast reliable proxies get more traffic
    # Slow or failing proxies get less traffic
```

**Key Integration Points:**

1. **Circuit breakers filter eligible proxies** - Strategies only see proxies with CLOSED/HALF_OPEN circuits
2. **Metrics inform strategy decisions** - Performance-based strategies use RetryMetrics data
3. **Failover respects strategy logic** - If weighted strategy fails, next proxy still follows weights
4. **Geo-targeting bonus in failover** - `RetryExecutor.select_retry_proxy()` gives 10% bonus to matching regions


## Advanced Patterns

### Adaptive Retry Policy

Adjust retry policy based on conditions:

```python
def get_adaptive_policy(time_sensitive: bool) -> RetryPolicy:
    """Adjust retry policy based on request priority."""
    if time_sensitive:
        # Fast retries for real-time requests
        return RetryPolicy(
            max_attempts=2,
            backoff_strategy=BackoffStrategy.FIXED,
            base_delay=0.5,
        )
    else:
        # Patient retries for batch jobs
        return RetryPolicy(
            max_attempts=10,
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            base_delay=2.0,
            max_backoff_delay=60.0,
            jitter=True,
        )

# Real-time request
rotator.retry_policy = get_adaptive_policy(time_sensitive=True)
response = rotator.request("GET", url)

# Batch request
rotator.retry_policy = get_adaptive_policy(time_sensitive=False)
response = rotator.request("GET", url)
```

### Circuit Breaker Alerts

Monitor circuit breaker events for alerts:

```python
from datetime import datetime, timezone
from proxywhirl.circuit_breaker import CircuitBreakerState

def check_circuit_health(rotator: ProxyRotator) -> None:
    """Alert on recent circuit breaker opens."""
    now = datetime.now(timezone.utc)

    for event in rotator.retry_metrics.circuit_breaker_events:
        if event.to_state == CircuitBreakerState.OPEN:
            age = (now - event.timestamp).total_seconds()
            if age < 300:  # Last 5 minutes
                print(f"ALERT: Proxy {event.proxy_id} circuit opened")
                print(f"  Failures: {event.failure_count}")
                print(f"  Time: {event.timestamp}")

# Run periodically
check_circuit_health(rotator)
```

### Request-Level Retry Override

Override retry policy for specific requests:

```python
from proxywhirl import ProxyRotator, RetryPolicy, BackoffStrategy

# Default policy
rotator = ProxyRotator(
    retry_policy=RetryPolicy(max_attempts=3)
)

# Override for critical request
critical_policy = RetryPolicy(
    max_attempts=10,
    backoff_strategy=BackoffStrategy.EXPONENTIAL,
    base_delay=2.0,
    jitter=True,
)

# Note: Currently requires creating new executor
# This pattern may be simplified in future versions
from proxywhirl.retry_executor import RetryExecutor

executor = RetryExecutor(
    critical_policy,
    rotator.circuit_breakers,
    rotator.retry_metrics,
)

# Use custom executor for this request
# (Integration with rotator.request() coming in future release)
```

## Best Practices

### 1. Start Conservative, Tune Later

Begin with safe defaults and adjust based on metrics:

```python
# Start here
policy = RetryPolicy(
    max_attempts=3,
    backoff_strategy=BackoffStrategy.EXPONENTIAL,
    jitter=True,
)

# After observing metrics, tune:
# - Increase max_attempts if success_by_attempt shows retries working
# - Adjust timeout based on avg_latency in metrics
# - Enable retry_non_idempotent only if API is truly idempotent
```

### 2. Always Use Jitter in Production

Jitter prevents thundering herd problems:

```python
# Production: Use jitter
policy = RetryPolicy(jitter=True)

# Testing: Disable for deterministic behavior
policy = RetryPolicy(jitter=False)
```

### 3. Monitor Circuit Breaker Opens

Frequent circuit opens indicate systemic issues:

```python
# Alert if >10% of proxies have open circuits
open_circuits = sum(
    1 for cb in rotator.circuit_breakers.values()
    if cb.state == CircuitBreakerState.OPEN
)
total_proxies = len(rotator.pool.proxies)

if total_proxies > 0 and open_circuits / total_proxies > 0.1:
    print(f"WARNING: {open_circuits}/{total_proxies} circuits open")
```

### 4. Set Timeouts for Time-Sensitive Requests

Prevent unbounded retry delays:

```python
# Time-sensitive request: Fail fast
policy = RetryPolicy(
    max_attempts=3,
    timeout=5.0,  # Total timeout
)

# Batch job: Be patient
policy = RetryPolicy(
    max_attempts=10,
    timeout=300.0,  # 5 minutes total
)
```

### 5. Use Metrics for Capacity Planning

Track retry rates to identify proxy quality issues:

```python
summary = rotator.retry_metrics.get_summary()
success_first_attempt = summary["success_by_attempt"].get(0, 0)
total_retries = summary["total_retries"]

if total_retries > 0:
    first_attempt_rate = success_first_attempt / total_retries
    print(f"First attempt success: {first_attempt_rate:.1%}")

    if first_attempt_rate < 0.7:
        print("WARNING: Low first-attempt success rate")
        print("Consider: Higher quality proxy sources")
```

## Troubleshooting

### All Retries Exhausted

**Symptom:** `ProxyConnectionError: Request failed after N attempts`

**Causes:**
1. All proxies have poor connectivity
2. Target website is blocking proxy IPs
3. Circuit breakers opened for all proxies

**Solutions:**
```python
# Check circuit breaker status
open_count = sum(
    1 for cb in rotator.circuit_breakers.values()
    if cb.state == CircuitBreakerState.OPEN
)
print(f"{open_count} circuits open")

# Reset circuits if blocking legitimate traffic
for cb in rotator.circuit_breakers.values():
    cb.reset()

# Refresh proxy pool
rotator.refresh()

# Check per-proxy statistics
by_proxy = rotator.retry_metrics.get_by_proxy(hours=1)
for proxy_id, stats in by_proxy.items():
    if stats["success_count"] == 0:
        print(f"Dead proxy: {proxy_id}")
```

### High Latency

**Symptom:** Requests take a long time to complete

**Causes:**
1. Backoff delays too aggressive
2. Many retries before success
3. Slow proxies selected

**Solutions:**
```python
# Check latency by proxy
by_proxy = rotator.retry_metrics.get_by_proxy(hours=1)
slow_proxies = [
    pid for pid, stats in by_proxy.items()
    if stats["avg_latency"] > 2.0
]

print(f"Slow proxies (>2s): {slow_proxies}")

# Use faster backoff
policy = RetryPolicy(
    backoff_strategy=BackoffStrategy.FIXED,
    base_delay=0.5,  # Shorter delays
)

# Set total timeout
policy.timeout = 10.0
```

### Non-Retryable Errors

**Symptom:** `NonRetryableError` raised immediately

**Causes:**
1. Custom error types not recognized as retryable
2. Authentication failures (407)

**Solutions:**
```python
# Authentication errors are not retryable
# Fix proxy credentials instead of retrying

# For custom error types, extend RetryExecutor._is_retryable_error()
# (Advanced - requires subclassing)
```

## Performance Impact

Retry logic adds minimal overhead:

- **Circuit breaker check:** O(1) dictionary lookup
- **Proxy scoring:** O(n) where n = number of candidate proxies
- **Metrics recording:** O(1) append to bounded deque
- **Backoff calculation:** O(1) arithmetic

Benchmark results (100k requests):
- No retry: 100ms avg latency
- With retry (3 attempts): 105ms avg latency (+5%)
- With retry + metrics: 110ms avg latency (+10%)

## Related Documentation

- [Advanced Strategies](advanced-strategies.md) - Geo-targeting and performance-based selection
- [Async Client](async-client.md) - Retry behavior in async context
- API Reference - Full API documentation for retry classes

## Summary

ProxyWhirl's retry and failover system provides:

- **Flexible retry policies** with exponential, linear, or fixed backoff
- **Circuit breaker protection** to isolate failing proxies
- **Intelligent failover** with performance-based proxy selection
- **Comprehensive metrics** for monitoring and debugging
- **Automatic integration** with ProxyRotator

Start with defaults and tune based on metrics. Enable jitter in production, set timeouts for time-sensitive requests, and monitor circuit breaker opens for systemic issues.
