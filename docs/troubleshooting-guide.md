# ProxyWhirl Troubleshooting Guide

## Common Issues and Solutions

### No Proxies Returned

**Symptom:** `ProxyPoolEmptyError` when calling `get_proxy()`

**Causes:**
1. Pool not loaded
2. All proxies marked unhealthy
3. All proxies removed/filtered

**Solutions:**

```python
# Check pool status
pool = rotator.get_pool()
print(f"Pool size: {len(pool.proxies)}")

if len(pool.proxies) == 0:
    # Add proxies
    from proxywhirl.fetchers import ProxyFetcher
    from proxywhirl.sources import RECOMMENDED_SOURCES
    
    fetcher = ProxyFetcher()
    for source in RECOMMENDED_SOURCES[:5]:
        proxies = fetcher.fetch(source)
        for p in proxies:
            rotator.add_proxy(p)

# Check health stats
stats = rotator.get_health_stats()
healthy = sum(1 for s in stats.values() if s.status == "healthy")
print(f"Healthy proxies: {healthy}")
```

### Connection Timeout

**Symptom:** Requests timeout when using proxy

**Causes:**
1. Proxy is down or slow
2. Firewall blocking connection
3. Timeout too short
4. Wrong proxy address

**Solutions:**

```python
# Increase timeout
proxy = rotator.get_proxy()
response = httpx.get(
    url,
    proxies=f"{proxy.protocol}://{proxy.host}:{proxy.port}",
    timeout=30.0  # Increase from default 5
)

# Validate proxy format
proxy_url = f"{proxy.protocol}://{proxy.host}:{proxy.port}"
print(f"Testing: {proxy_url}")

# Test with different proxy
try:
    proxy1 = rotator.get_proxy()
    # use proxy1
except:
    proxy2 = rotator.get_proxy()
    # use proxy2
```

### Authentication Failed

**Symptom:** 407 Proxy Authentication Required

**Causes:**
1. Wrong credentials
2. Credentials not properly formatted
3. Proxy requires specific auth method

**Solutions:**

```python
# Use credentials correctly
from proxywhirl.models import Proxy, ProxyCredentials

proxy = Proxy(
    protocol="http",
    host="192.168.1.1",
    port=8080,
    username="user",
    password="pass",
)

# Or use credentials object
proxy = Proxy(
    protocol="http",
    host="192.168.1.1",
    port=8080,
    credentials=ProxyCredentials(username="user", password="pass")
)

# Test auth
import httpx
proxy_url = f"{proxy.protocol}://{proxy.username}:{proxy.password}@{proxy.host}:{proxy.port}"
response = httpx.get("https://httpbin.org/ip", proxies=proxy_url)
```

### Invalid Proxy Format

**Symptom:** `ProxyValidationError` when adding proxy

**Causes:**
1. Missing port
2. Invalid protocol
3. Malformed URL

**Solutions:**

```python
# Correct format
# protocol://[username:password@]host:port

# Valid examples
http://192.168.1.1:8080
https://proxy.example.com:8443
socks5://192.168.1.1:1080
socks5://user:pass@192.168.1.1:1080

# Invalid examples (will fail)
192.168.1.1:8080  # Missing protocol
http://192.168.1.1  # Missing port
http://192.168.1.1:abc  # Invalid port
```

### Rate Limited by Proxy Provider

**Symptom:** 429 Too Many Requests errors

**Causes:**
1. Too many requests per second
2. IP-based rate limit
3. Account limit reached

**Solutions:**

```python
from proxywhirl import ProxyConfiguration

# Add rate limiting
config = ProxyConfiguration(
    rate_limit_requests_per_second=10.0,  # Reduce rate
)
rotator = ProxyWhirl(config=config)

# Or use time.sleep
import time
for url in urls:
    proxy = rotator.get_proxy()
    # make request
    time.sleep(0.1)  # 100ms delay between requests
```

### Proxy No Longer Works

**Symptom:** Proxies were working, now they fail

**Causes:**
1. Proxy service down
2. Proxy credentials expired
3. IP rotated/changed

**Solutions:**

```python
# Remove outdated proxies
rotator.remove_proxy(proxy_id)

# Refresh proxy list
from proxywhirl.fetchers import ProxyFetcher
from proxywhirl.sources import RECOMMENDED_SOURCES

fetcher = ProxyFetcher()
rotator.get_pool().proxies.clear()  # Clear old pool

for source in RECOMMENDED_SOURCES[:3]:
    proxies = fetcher.fetch(source)
    for p in proxies:
        rotator.add_proxy(p)

# Validate new proxies
from proxywhirl.fetchers import ProxyValidator
validator = ProxyValidator()
for proxy in rotator.get_pool().proxies:
    if not validator.validate(proxy):
        rotator.remove_proxy(proxy.id)
```

### Memory Leak

**Symptom:** Memory usage grows over time

**Causes:**
1. Cache not clearing
2. Pool unbounded growth
3. Circular references

**Solutions:**

```python
from proxywhirl import ProxyConfiguration

config = ProxyConfiguration(
    # Limit pool size
    max_pool_size=5000,
    
    # Limit cache size
    cache_max_size=10000,
    
    # Cache TTL (expire old entries)
    cache_ttl_seconds=300,
)
rotator = ProxyWhirl(config=config)

# Manual cleanup
if len(rotator.get_pool().proxies) > 5000:
    # Export healthy proxies
    pool = rotator.get_pool()
    healthy = [p for p in pool.proxies if p.health_status.status == "healthy"]
    
    # Clear and reimport
    rotator.get_pool().proxies = healthy[:5000]
```

### Circuit Breaker Stuck Open

**Symptom:** Never getting proxies, circuit breaker stuck

**Causes:**
1. Too many failures
2. Threshold too low
3. Recovery timeout not elapsed

**Solutions:**

```python
from proxywhirl import ProxyConfiguration

config = ProxyConfiguration(
    circuit_breaker_enabled=True,
    circuit_breaker_failure_threshold=20,  # Increase threshold
    circuit_breaker_recovery_timeout_seconds=120,  # Recovery time
)
rotator = ProxyWhirl(config=config)

# Manual reset if stuck
# (Note: this is internal, use with caution)
if hasattr(rotator, '_circuit_breaker'):
    rotator._circuit_breaker.reset()
```

### Inconsistent Health Status

**Symptom:** Proxy marked healthy then unhealthy randomly

**Causes:**
1. Intermittent connectivity issues
2. Network flakiness
3. Test URL unreliable

**Solutions:**

```python
from proxywhirl import ProxyConfiguration

config = ProxyConfiguration(
    # Use more reliable test URL
    validator_test_url="https://httpbin.org/status/200",
    
    # Longer validation timeout
    validator_timeout_seconds=10,
    
    # More samples before marking unhealthy
    health_check_sampling_rate=0.1,
)
rotator = ProxyWhirl(config=config)
```

### Proxy Lists Outdated

**Symptom:** Most proxies in list are dead

**Causes:**
1. Proxy source quality
2. Proxies age quickly
3. Not validating fetched proxies

**Solutions:**

```python
from proxywhirl import ProxyConfiguration
from proxywhirl.fetchers import ProxyFetcher
from proxywhirl.sources import RECOMMENDED_SOURCES

config = ProxyConfiguration(
    # Validate on fetch
    validator_validate_on_fetch=True,
    validator_timeout_seconds=3,
)
rotator = ProxyWhirl(config=config)

# Use only recommended sources (quality filter)
fetcher = ProxyFetcher()
for source in RECOMMENDED_SOURCES:  # Better than ALL_SOURCES
    proxies = fetcher.fetch(source)
    for proxy in proxies:
        # Validate before adding
        from proxywhirl.fetchers import ProxyValidator
        if ProxyValidator().validate(proxy):
            rotator.add_proxy(proxy)

# Regular refresh
import schedule
import time

def refresh_proxies():
    # Clear old, fetch new
    rotator.get_pool().proxies = []
    for source in RECOMMENDED_SOURCES[:5]:
        proxies = fetcher.fetch(source)
        for p in proxies[:20]:
            rotator.add_proxy(p)

schedule.every().hours(6).do(refresh_proxies)
```

### High Latency

**Symptom:** All proxies are slow

**Causes:**
1. Free proxies are naturally slow
2. Geographic distance
3. Proxy congestion

**Solutions:**

```python
from proxywhirl import ProxyConfiguration

# Use latency-based strategy
config = ProxyConfiguration(
    rotation_strategy="latency_based",  # Select fastest
)
rotator = ProxyWhirl(config=config)

# Or use location preference
from proxywhirl.models import SelectionContext

context = SelectionContext(
    url="https://example.com",
    metadata={"preferred_location": "US"}
)
proxy = rotator.get_proxy(context=context)

# Filter by latency
pool = rotator.get_pool()
fast_proxies = [
    p for p in pool.proxies
    if p.latency_ms and p.latency_ms < 500
]
print(f"Fast proxies: {len(fast_proxies)}")
```

## Debugging

### Enable Debug Logging

```python
from proxywhirl import ProxyWhirl
from proxywhirl.utils import configure_logging

# Enable debug logging
configure_logging(level="DEBUG")

rotator = ProxyWhirl()
proxy = rotator.get_proxy()  # Will log detailed info
```

### CLI Debug Mode

```bash
proxywhirl --log-level DEBUG list
```

### Inspect Pool State

```python
pool = rotator.get_pool()

# Check pool size
print(f"Total proxies: {len(pool.proxies)}")

# Check by protocol
by_protocol = {}
for p in pool.proxies:
    by_protocol[p.protocol] = by_protocol.get(p.protocol, 0) + 1
print(f"By protocol: {by_protocol}")

# Check health distribution
by_status = {}
for p in pool.proxies:
    status = p.health_status.status
    by_status[status] = by_status.get(status, 0) + 1
print(f"By status: {by_status}")

# Check location distribution
by_location = {}
for p in pool.proxies:
    if p.geo_location:
        country = p.geo_location.get("country", "Unknown")
        by_location[country] = by_location.get(country, 0) + 1
print(f"By location: {by_location}")
```

### Test Single Proxy

```python
import httpx
from proxywhirl.fetchers import ProxyValidator

proxy_url = "http://192.168.1.1:8080"

# Direct HTTP test
try:
    response = httpx.get(
        "https://httpbin.org/ip",
        proxies=proxy_url,
        timeout=5.0
    )
    print(f"✓ Proxy working: {response.json()}")
except Exception as e:
    print(f"✗ Proxy failed: {e}")

# Using validator
from proxywhirl.models import Proxy
proxy = Proxy(protocol="http", host="192.168.1.1", port=8080)
validator = ProxyValidator()
is_valid = validator.validate(proxy)
print(f"Validator: {'Valid' if is_valid else 'Invalid'}")
```

### Capture Network Traffic

```python
import httpx
import logging

# Enable httpx logging
logging.basicConfig()
logging.getLogger("httpx").setLevel(logging.DEBUG)

proxy = rotator.get_proxy()
response = httpx.get(
    "https://httpbin.org/ip",
    proxies=f"{proxy.protocol}://{proxy.host}:{proxy.port}",
    timeout=10.0
)
# Will print HTTP details
```

## Performance Issues

### Slow Proxy Selection

```python
# Use simpler strategy
from proxywhirl import ProxyConfiguration

config = ProxyConfiguration(
    rotation_strategy="round_robin",  # Fastest
    # Avoid: "performance_based" (calculates weights)
)
rotator = ProxyWhirl(config=config)
```

### Slow Health Checks

```python
from proxywhirl import ProxyConfiguration

config = ProxyConfiguration(
    health_checks_enabled=True,
    health_check_interval_seconds=600,  # Increase interval
    health_check_sampling_rate=0.01,  # Check only 1% of pool
)
rotator = ProxyWhirl(config=config)
```

### High CPU Usage

```python
# Disable unnecessary features
config = ProxyConfiguration(
    cache_enabled=True,  # Use caching to reduce work
    health_checks_enabled=False,  # If not needed
    metrics_enabled=False,  # Disable metrics collection
)
rotator = ProxyWhirl(config=config)
```

## Getting Help

When reporting issues, include:

1. **Version Info**
   ```bash
   python -c "import proxywhirl; print(proxywhirl.__version__)"
   ```

2. **Configuration**
   ```bash
   proxywhirl config show
   ```

3. **Pool Status**
   ```bash
   proxywhirl stats
   ```

4. **Error Log**
   ```bash
   proxywhirl --log-level DEBUG <command> 2>&1 | head -100
   ```

5. **Minimal Reproduction Code**
   ```python
   from proxywhirl import ProxyWhirl
   # Minimal code that reproduces the issue
   ```

