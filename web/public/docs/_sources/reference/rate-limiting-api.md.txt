# Rate Limiting API Reference

Complete reference for ProxyWhirl's rate limiting system with per-proxy and global rate limits using token bucket algorithm.

```python
from proxywhirl.rate_limiting import RateLimiter, RateLimit, RateLimitEvent
```

## Overview

The rate limiting subsystem provides flexible request throttling for proxies with:
- **Per-proxy limits**: Individual rate limits for each proxy
- **Global limits**: Aggregate rate limit across all proxies
- **Token bucket algorithm**: Burst capacity with sustained rate limiting
- **Thread-safe**: Safe for concurrent access
- **Async support**: Fully async/await compatible

Built on top of `pyrate-limiter` for robust, production-ready rate limiting.

## Core Classes

### RateLimiter

Main rate limiter with per-proxy and global limits using token bucket algorithm.

```python
from proxywhirl.rate_limiting import RateLimiter, RateLimit

# Initialize with global limit
global_limit = RateLimit(
    max_requests=1000,
    time_window=60,  # 1000 requests per 60 seconds
    burst_allowance=100  # Allow bursts up to 100 requests
)

limiter = RateLimiter(global_limit=global_limit)

# Set per-proxy limits
limiter.set_proxy_limit(
    "proxy1",
    RateLimit(max_requests=10, time_window=1)  # 10 req/sec
)

limiter.set_proxy_limit(
    "proxy2",
    RateLimit(max_requests=20, time_window=1)  # 20 req/sec
)

# Check if request is allowed
allowed = await limiter.check_limit("proxy1")
if allowed:
    # Make request
    response = await make_request_with_proxy("proxy1")
else:
    # Rate limited, wait or use different proxy
    print("Rate limit exceeded for proxy1")

# Acquire permission (same as check_limit)
if await limiter.acquire("proxy1"):
    response = await make_request_with_proxy("proxy1")
```

#### Constructor

**Parameters:**
- `global_limit` (RateLimit | None): Global rate limit across all proxies (default: None)

**Attributes:**
- `global_limit` (RateLimit | None): Global rate limit configuration
- `_proxy_limiters` (dict[str, Limiter]): Per-proxy limiter instances
- `_global_limiter` (Limiter | None): Global limiter instance
- `_lock` (RLock): Thread-safe lock for limiter access

**Example:**
```python
# No limits
limiter = RateLimiter()

# Global limit only
limiter = RateLimiter(
    global_limit=RateLimit(max_requests=1000, time_window=60)
)

# Per-proxy limits added later
limiter.set_proxy_limit("proxy1", RateLimit(max_requests=10, time_window=1))
```

---

#### Methods

##### `set_proxy_limit(proxy_id: str, limit: RateLimit) -> None`

Set rate limit for a specific proxy.

**Behavior:**
- Creates a new token bucket limiter for the proxy
- Overwrites existing limit if proxy_id already has one
- Thread-safe with lock protection
- Logs limit configuration at INFO level

**Parameters:**
- `proxy_id` (str): Unique proxy identifier
- `limit` (RateLimit): Rate limit configuration

**Example:**
```python
from proxywhirl.rate_limiting import RateLimiter, RateLimit

limiter = RateLimiter()

# Set different limits for different proxies
limiter.set_proxy_limit(
    "premium_proxy",
    RateLimit(max_requests=100, time_window=1)  # 100 req/sec
)

limiter.set_proxy_limit(
    "free_proxy",
    RateLimit(max_requests=5, time_window=1)  # 5 req/sec
)

# Update existing limit
limiter.set_proxy_limit(
    "premium_proxy",
    RateLimit(max_requests=200, time_window=1)  # Increase to 200 req/sec
)
```

---

##### `check_limit(proxy_id: str) -> bool` (async)

Check if request is allowed for proxy.

**Flow:**
1. Check per-proxy limit (if set)
2. Check global limit (if set)
3. Return True if both allow, False if either denies

**Behavior:**
- Consumes a token from the bucket if allowed
- Logs warning at WARNING level if rate limit exceeded
- Thread-safe with lock protection for limiter access
- Non-blocking (returns immediately)

**Parameters:**
- `proxy_id` (str): Unique proxy identifier

**Returns:**
- `True` if request is allowed
- `False` if rate limit exceeded (either per-proxy or global)

**Logs:**
- WARNING: "Rate limit exceeded for proxy {proxy_id}" (per-proxy limit)
- WARNING: "Global rate limit exceeded" (global limit)

**Example:**
```python
from proxywhirl.rate_limiting import RateLimiter, RateLimit

limiter = RateLimiter(
    global_limit=RateLimit(max_requests=1000, time_window=60)
)
limiter.set_proxy_limit("proxy1", RateLimit(max_requests=10, time_window=1))

# Check before making request
if await limiter.check_limit("proxy1"):
    print("Request allowed")
    response = await make_request("proxy1")
else:
    print("Rate limited, try again later")

# Check multiple times rapidly
results = []
for i in range(15):
    allowed = await limiter.check_limit("proxy1")
    results.append(allowed)

# First 10 will be True, remaining will be False
print(f"Allowed: {sum(results)}/15")  # "Allowed: 10/15"
```

---

##### `acquire(proxy_id: str) -> bool` (async)

Acquire permission to make a request (alias for check_limit).

**Parameters:**
- `proxy_id` (str): Unique proxy identifier

**Returns:**
- `True` if request is allowed
- `False` if rate limit exceeded

**Example:**
```python
# Same as check_limit
if await limiter.acquire("proxy1"):
    response = await make_request("proxy1")
```

---

## Data Models

### RateLimit

Rate limit configuration for token bucket algorithm.

```python
from proxywhirl.rate_limiting import RateLimit

# Basic rate limit
limit = RateLimit(
    max_requests=100,
    time_window=60  # 100 requests per 60 seconds
)

# With burst allowance
limit = RateLimit(
    max_requests=100,
    time_window=60,
    burst_allowance=20  # Allow bursts up to 20 requests beyond sustained rate
)
```

#### Fields

- `max_requests` (int): Maximum requests allowed in time window
- `time_window` (int): Time window in seconds
- `burst_allowance` (int | None): Burst capacity for token bucket (default: None)

**Token Bucket Behavior:**
- **Sustained rate**: `max_requests / time_window` requests per second
- **Burst capacity**: Up to `burst_allowance` additional requests can be consumed rapidly
- **Refill rate**: Tokens refill at sustained rate

**Example Scenarios:**

```python
# Scenario 1: Strict 10 req/sec (no bursts)
limit = RateLimit(max_requests=10, time_window=1)
# Allows exactly 10 requests per second

# Scenario 2: 100 req/min with 20-request burst
limit = RateLimit(max_requests=100, time_window=60, burst_allowance=20)
# Sustained: ~1.67 req/sec
# Can burst up to 20 requests immediately, then throttled to sustained rate

# Scenario 3: 1000 req/hour
limit = RateLimit(max_requests=1000, time_window=3600)
# Sustained: ~0.28 req/sec or ~16.67 req/min
```

---

### RateLimitEvent

Rate limit event for logging and monitoring.

```python
from proxywhirl.rate_limiting import RateLimitEvent
from datetime import datetime, timezone

event = RateLimitEvent(
    timestamp=datetime.now(timezone.utc),
    proxy_id="proxy1",
    event_type="throttled",  # or "exceeded", "adaptive_change"
    details={
        "requests_in_window": 10,
        "limit": 10,
        "time_window": 1
    }
)

print(f"Event: {event.event_type} for {event.proxy_id}")
print(f"Details: {event.details}")
```

#### Fields

- `timestamp` (datetime): When event occurred
- `proxy_id` (str): Proxy identifier
- `event_type` (str): Event type
  - `"throttled"`: Request was throttled (rate limit applied)
  - `"exceeded"`: Rate limit exceeded
  - `"adaptive_change"`: Rate limit adjusted automatically
- `details` (dict): Event-specific details

**Usage:**
- Log to file/database for analysis
- Send to monitoring system (Prometheus, DataDog)
- Trigger alerts on excessive throttling

---

## Usage Examples

### Basic Rate Limiting

```python
from proxywhirl.rate_limiting import RateLimiter, RateLimit

# Create limiter
limiter = RateLimiter()

# Set per-proxy limits
limiter.set_proxy_limit(
    "proxy1",
    RateLimit(max_requests=10, time_window=1)  # 10 req/sec
)

# Check limit before each request
async def make_safe_request(proxy_id, url):
    if await limiter.check_limit(proxy_id):
        return await httpx_client.get(url, proxy=get_proxy_url(proxy_id))
    else:
        raise RateLimitExceeded(f"Rate limit exceeded for {proxy_id}")

# Use in loop
for i in range(20):
    try:
        response = await make_safe_request("proxy1", "https://api.example.com")
        print(f"Request {i}: {response.status_code}")
    except RateLimitExceeded:
        print(f"Request {i}: Rate limited")
        await asyncio.sleep(0.1)  # Wait before retry
```

---

### Global + Per-Proxy Limits

```python
from proxywhirl.rate_limiting import RateLimiter, RateLimit

# Global limit: 1000 req/min across all proxies
# Per-proxy limit: 10 req/sec per proxy
limiter = RateLimiter(
    global_limit=RateLimit(max_requests=1000, time_window=60)
)

for proxy_id in ["proxy1", "proxy2", "proxy3"]:
    limiter.set_proxy_limit(
        proxy_id,
        RateLimit(max_requests=10, time_window=1)
    )

# Request will be limited by whichever constraint is hit first
async def make_request(proxy_id):
    if await limiter.check_limit(proxy_id):
        # Both per-proxy and global limits allow this request
        return await http_client.get("https://api.example.com", proxy=proxy_id)
    else:
        # Either per-proxy or global limit exceeded
        return None
```

---

### Burst Handling

```python
from proxywhirl.rate_limiting import RateLimiter, RateLimit

# Allow bursts up to 50 requests, then throttle to 10 req/sec
limiter = RateLimiter()
limiter.set_proxy_limit(
    "proxy1",
    RateLimit(
        max_requests=10,
        time_window=1,
        burst_allowance=50  # Can burst 50 requests immediately
    )
)

# Burst scenario
results = []
for i in range(100):
    allowed = await limiter.check_limit("proxy1")
    results.append(allowed)

# First ~50 will be True (burst), then throttled to 10/sec
print(f"Allowed: {sum(results)}/100")

# Wait for bucket to refill
await asyncio.sleep(5)  # Wait 5 seconds

# Can burst again
allowed = await limiter.check_limit("proxy1")
assert allowed is True
```

---

### Dynamic Limit Adjustment

```python
from proxywhirl.rate_limiting import RateLimiter, RateLimit

limiter = RateLimiter()

# Start with conservative limit
limiter.set_proxy_limit(
    "proxy1",
    RateLimit(max_requests=5, time_window=1)
)

# Monitor success rate and adjust
async def adaptive_request(proxy_id):
    if await limiter.check_limit(proxy_id):
        try:
            response = await http_client.get("https://api.example.com", proxy=proxy_id)

            # Success - increase limit
            if response.status_code == 200:
                limiter.set_proxy_limit(
                    proxy_id,
                    RateLimit(max_requests=10, time_window=1)
                )

            return response
        except Exception as e:
            # Failure - decrease limit
            limiter.set_proxy_limit(
                proxy_id,
                RateLimit(max_requests=2, time_window=1)
            )
            raise
    else:
        return None
```

---

### Integration with ProxyRotator

```python
from proxywhirl import ProxyRotator
from proxywhirl.rate_limiting import RateLimiter, RateLimit

# Create rotator and limiter
rotator = ProxyRotator()
limiter = RateLimiter(
    global_limit=RateLimit(max_requests=1000, time_window=60)
)

# Add proxies with individual limits
proxies = [
    ("proxy1", RateLimit(max_requests=20, time_window=1)),
    ("proxy2", RateLimit(max_requests=10, time_window=1)),
    ("proxy3", RateLimit(max_requests=5, time_window=1)),
]

for proxy_id, limit in proxies:
    rotator.add_proxy(f"http://{proxy_id}.example.com:8080")
    limiter.set_proxy_limit(proxy_id, limit)

# Make requests with rate limiting
async def make_request_with_rate_limit(url):
    # Get proxy from rotator
    proxy = rotator.get_proxy()
    proxy_id = proxy.id

    # Check rate limit
    if await limiter.check_limit(proxy_id):
        response = await rotator.get(url)
        return response
    else:
        # Rate limited, try different proxy
        return await make_request_with_rate_limit(url)

# Use in application
response = await make_request_with_rate_limit("https://api.example.com")
```

---

### Monitoring and Logging

```python
from proxywhirl.rate_limiting import RateLimiter, RateLimit, RateLimitEvent
from datetime import datetime, timezone
from loguru import logger

limiter = RateLimiter()
limiter.set_proxy_limit("proxy1", RateLimit(max_requests=10, time_window=1))

# Track rate limit events
events = []

async def make_request_with_monitoring(proxy_id, url):
    allowed = await limiter.check_limit(proxy_id)

    if allowed:
        # Request allowed
        event = RateLimitEvent(
            timestamp=datetime.now(timezone.utc),
            proxy_id=proxy_id,
            event_type="allowed",
            details={"url": url}
        )
        events.append(event)
        logger.info(f"Request allowed for {proxy_id}")
        return await http_client.get(url, proxy=proxy_id)
    else:
        # Rate limited
        event = RateLimitEvent(
            timestamp=datetime.now(timezone.utc),
            proxy_id=proxy_id,
            event_type="exceeded",
            details={"url": url}
        )
        events.append(event)
        logger.warning(f"Rate limit exceeded for {proxy_id}")
        return None

# Analyze events
throttled_count = sum(1 for e in events if e.event_type == "exceeded")
print(f"Throttled requests: {throttled_count}/{len(events)}")
```

---

### Retry with Backoff

```python
from proxywhirl.rate_limiting import RateLimiter, RateLimit
import asyncio

limiter = RateLimiter()
limiter.set_proxy_limit("proxy1", RateLimit(max_requests=10, time_window=1))

async def make_request_with_retry(proxy_id, url, max_retries=3):
    for attempt in range(max_retries):
        if await limiter.check_limit(proxy_id):
            try:
                return await http_client.get(url, proxy=proxy_id)
            except Exception as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
        else:
            # Rate limited, wait before retry
            wait_time = 1.0 / 10  # 1 / (requests per second)
            await asyncio.sleep(wait_time)

    raise Exception(f"Failed after {max_retries} retries")

# Use
response = await make_request_with_retry("proxy1", "https://api.example.com")
```

---

## Thread Safety

`RateLimiter` is thread-safe using `threading.RLock`:

```python
import asyncio
from proxywhirl.rate_limiting import RateLimiter, RateLimit

limiter = RateLimiter()
limiter.set_proxy_limit("proxy1", RateLimit(max_requests=100, time_window=1))

async def worker(worker_id):
    for i in range(20):
        if await limiter.check_limit("proxy1"):
            print(f"Worker {worker_id}: Request {i} allowed")
        else:
            print(f"Worker {worker_id}: Request {i} rate limited")
        await asyncio.sleep(0.01)

# Run concurrent workers
async def main():
    tasks = [worker(i) for i in range(10)]
    await asyncio.gather(*tasks)

asyncio.run(main())
```

---

## Performance Considerations

### Token Bucket Algorithm

**Advantages:**
- Allows burst traffic up to bucket capacity
- Smooth rate limiting over time
- Low overhead (O(1) per request)
- No memory growth with large request volumes

**Tuning:**

1. **High-throughput APIs:**
   ```python
   # Allow high sustained rate with moderate bursts
   RateLimit(
       max_requests=1000,
       time_window=1,
       burst_allowance=200
   )
   ```

2. **Rate-limited APIs:**
   ```python
   # Strict limit with small burst
   RateLimit(
       max_requests=10,
       time_window=1,
       burst_allowance=2
   )
   ```

3. **Bursty workloads:**
   ```python
   # Low sustained rate, high burst capacity
   RateLimit(
       max_requests=100,
       time_window=60,  # ~1.67 req/sec sustained
       burst_allowance=50  # Can handle sudden spikes
   )
   ```

### Memory Usage

**Per-Proxy Limiters:**
- Each proxy with a limit creates a `Limiter` instance
- Memory: ~1KB per limiter
- 1000 proxies ≈ 1MB memory overhead

**Optimization:**
```python
# Option 1: Use global limit only (minimal memory)
limiter = RateLimiter(
    global_limit=RateLimit(max_requests=1000, time_window=60)
)

# Option 2: Set limits only for high-traffic proxies
limiter = RateLimiter()
for proxy_id in high_traffic_proxies:
    limiter.set_proxy_limit(proxy_id, RateLimit(max_requests=20, time_window=1))
```

### Concurrency

**Async/Await:**
- `check_limit()` and `acquire()` are async-safe
- Lock contention is minimal (only during limiter access)
- No blocking I/O

**Best Practices:**
```python
# Good: Check limit before expensive operation
if await limiter.check_limit(proxy_id):
    response = await expensive_api_call(proxy_id)

# Bad: Check limit inside expensive operation
async def expensive_api_call(proxy_id):
    if await limiter.check_limit(proxy_id):  # Too late
        return await http_client.get(url)
```

---

## Integration with Monitoring

### Prometheus Metrics

```python
from prometheus_client import Counter, Gauge
from proxywhirl.rate_limiting import RateLimiter, RateLimit

# Define metrics
rate_limit_allowed = Counter(
    'rate_limit_allowed_total',
    'Total requests allowed',
    ['proxy_id']
)
rate_limit_exceeded = Counter(
    'rate_limit_exceeded_total',
    'Total requests rate limited',
    ['proxy_id']
)

limiter = RateLimiter()

async def make_request_with_metrics(proxy_id, url):
    if await limiter.check_limit(proxy_id):
        rate_limit_allowed.labels(proxy_id=proxy_id).inc()
        return await http_client.get(url, proxy=proxy_id)
    else:
        rate_limit_exceeded.labels(proxy_id=proxy_id).inc()
        return None
```

---

### DataDog Integration

```python
from datadog import statsd
from proxywhirl.rate_limiting import RateLimiter, RateLimit

limiter = RateLimiter()

async def make_request_with_datadog(proxy_id, url):
    if await limiter.check_limit(proxy_id):
        statsd.increment('rate_limit.allowed', tags=[f'proxy:{proxy_id}'])
        return await http_client.get(url, proxy=proxy_id)
    else:
        statsd.increment('rate_limit.exceeded', tags=[f'proxy:{proxy_id}'])
        return None
```

---

## Sphinx Integration

Add to your `conf.py`:

```python
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
]

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}
```

In your RST files:

```rst
Rate Limiting API
=================

.. automodule:: proxywhirl.rate_limiting
   :members:
   :undoc-members:
   :show-inheritance:

RateLimiter
-----------

.. autoclass:: proxywhirl.rate_limiting.RateLimiter
   :members:
   :undoc-members:
   :show-inheritance:

Models
------

.. autoclass:: proxywhirl.rate_limiting.RateLimit
   :members:
   :undoc-members:

.. autoclass:: proxywhirl.rate_limiting.RateLimitEvent
   :members:
   :undoc-members:
```

---

## Common Patterns

### Fallback to Different Proxy

```python
async def make_request_with_fallback(url, proxy_ids):
    for proxy_id in proxy_ids:
        if await limiter.check_limit(proxy_id):
            try:
                return await http_client.get(url, proxy=proxy_id)
            except Exception:
                continue

    raise Exception("All proxies rate limited or failed")

# Use
response = await make_request_with_fallback(
    "https://api.example.com",
    ["proxy1", "proxy2", "proxy3"]
)
```

---

### Batch Requests with Rate Limiting

```python
async def batch_request_with_rate_limit(urls, proxy_id, batch_size=10):
    results = []

    for i in range(0, len(urls), batch_size):
        batch = urls[i:i + batch_size]

        # Check if we can make batch_size requests
        allowed_count = 0
        for _ in range(len(batch)):
            if await limiter.check_limit(proxy_id):
                allowed_count += 1
            else:
                break

        # Make allowed requests
        batch_results = await asyncio.gather(*[
            http_client.get(url, proxy=proxy_id)
            for url in batch[:allowed_count]
        ])
        results.extend(batch_results)

        # Wait if rate limited
        if allowed_count < len(batch):
            await asyncio.sleep(1.0)

    return results
```

---

### Circuit Breaker Integration

```python
from proxywhirl.rate_limiting import RateLimiter, RateLimit
from proxywhirl import CircuitBreaker

limiter = RateLimiter()
circuit_breakers = {}

async def make_request_with_circuit_breaker(proxy_id, url):
    # Initialize circuit breaker if needed
    if proxy_id not in circuit_breakers:
        circuit_breakers[proxy_id] = CircuitBreaker(
            proxy_id=proxy_id,
            failure_threshold=5,
            window_duration=60.0,
            timeout_duration=30.0
        )

    breaker = circuit_breakers[proxy_id]

    # Check circuit breaker
    if not breaker.should_attempt_request():
        raise Exception(f"Circuit breaker open for {proxy_id}")

    # Check rate limit
    if not await limiter.check_limit(proxy_id):
        raise Exception(f"Rate limit exceeded for {proxy_id}")

    # Make request
    try:
        response = await http_client.get(url, proxy=proxy_id)
        breaker.record_success()
        return response
    except Exception as e:
        breaker.record_failure()
        raise
```

---

## FAQ

**Q: What's the difference between `check_limit()` and `acquire()`?**

A: They are identical. `acquire()` is an alias for `check_limit()` for API consistency with other rate limiting libraries.

**Q: Can I remove a per-proxy limit?**

A: Currently, no. You can set it to a very high value effectively disabling it:
```python
limiter.set_proxy_limit("proxy1", RateLimit(max_requests=1000000, time_window=1))
```

**Q: Does the limiter persist state across restarts?**

A: No, all state is in-memory. Rate limits reset on process restart.

**Q: Can I use this with synchronous code?**

A: The current implementation is async-only. For sync code, wrap in `asyncio.run()`:
```python
import asyncio

def sync_check_limit(proxy_id):
    return asyncio.run(limiter.check_limit(proxy_id))
```

**Q: How do I calculate the right rate limit for an API?**

A: Check the API's documentation for rate limits. Common formats:
- "100 requests per minute" → `RateLimit(max_requests=100, time_window=60)`
- "10 requests per second" → `RateLimit(max_requests=10, time_window=1)`
- "1000 requests per hour" → `RateLimit(max_requests=1000, time_window=3600)`

**Q: Can I set different limits for different endpoints?**

A: Not directly. Create separate `RateLimiter` instances or use `proxy_id` to encode endpoint information:
```python
limiter.set_proxy_limit("proxy1_api_v1", RateLimit(max_requests=10, time_window=1))
limiter.set_proxy_limit("proxy1_api_v2", RateLimit(max_requests=20, time_window=1))
```
