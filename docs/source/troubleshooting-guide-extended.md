# Troubleshooting Guide

## Common Issues and Solutions

### No Proxies Available

**Symptom:** ProxyPoolEmptyError

**Causes:**
1. Sources not configured correctly
2. All proxies failed validation
3. Sources are down

**Solutions:**
```python
# 1. Check configured sources
config = ProxyConfiguration()
print(config.sources)

# 2. Refresh sources
rotator.refresh_sources()

# 3. Use different sources
config = ProxyConfiguration(
    sources=[
        'http://free-proxy-list.net',
        'http://proxylist.geonode.com'
    ]
)

# 4. Reduce validation strictness
config = ProxyConfiguration(
    validation_level='light'
)
```

### High Latency

**Symptom:** Slow proxy selection

**Causes:**
1. Network latency
2. Cache misses
3. Validation overhead

**Solutions:**
```python
# 1. Enable caching
cache_config = CacheConfig(
    enabled=True,
    ttl_seconds=3600
)

# 2. Reduce validation timeout
config = ProxyConfiguration(
    timeout_seconds=5
)

# 3. Use light validation
config = ProxyConfiguration(
    validation_level='light'
)
```

### Memory Usage Too High

**Symptom:** Application consuming excessive RAM

**Causes:**
1. Cache too large
2. Too many proxies in pool
3. Memory leak

**Solutions:**
```python
# 1. Reduce cache size
cache_config = CacheConfig(
    max_entries=1000,
    compression_level=20
)

# 2. Check cache statistics
stats = rotator.cache.get_statistics()
print(f"Memory: {stats.size_bytes} bytes")

# 3. Clear cache periodically
rotator.cache.clear()

# 4. Monitor with profiling
import tracemalloc
tracemalloc.start()
```

### SSL/TLS Errors

**Symptom:** `SSLError: certificate_verify_failed`

**Causes:**
1. Invalid certificate
2. Self-signed certificate
3. Certificate mismatch

**Solutions:**
```python
# 1. Disable verification (NOT recommended)
import httpx
client = httpx.Client(verify=False)

# 2. Use custom CA bundle
client = httpx.Client(verify='/path/to/ca-bundle.crt')

# 3. Trust self-signed certs
import ssl
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
client = httpx.Client(verify=context)
```

### Proxy Connection Timeout

**Symptom:** Requests hanging or timing out

**Causes:**
1. Proxy unreachable
2. Timeout too short
3. Network issues

**Solutions:**
```python
# 1. Increase timeout
config = ProxyConfiguration(
    timeout_seconds=30
)

# 2. Use shorter timeout for validation
validator = ProxyValidator(timeout=5)

# 3. Mark proxy unhealthy
rotator.mark_unhealthy(proxy)

# 4. Implement timeout handling
try:
    proxy = rotator.get_proxy()
except TimeoutError:
    proxy = rotator.get_proxy()  # Try next
```

### Authentication Failures

**Symptom:** Proxy requires authentication but failing

**Causes:**
1. Wrong credentials
2. Credentials not provided
3. Expired credentials

**Solutions:**
```python
# 1. Provide credentials
proxy = Proxy(
    url='http://192.168.1.1:8080',
    username='user',
    password='pass'
)

# 2. Use encrypted storage
from proxywhirl import encrypt_credentials

key = os.environ['KEY']
encrypted = encrypt_credentials('user', 'pass', key)

# 3. Update credentials
rotator.update_proxy_credentials(proxy.url, 'newuser', 'newpass')
```

## Performance Issues

### Slow Proxy Selection

```python
# Profile selection speed
import time

start = time.time()
proxy = rotator.get_proxy()
elapsed = time.time() - start

print(f"Selection took {elapsed*1000:.2f}ms")

# Expected: <1ms with cache, <100ms without
```

### High Validation Latency

```python
# Check validation performance
from proxywhirl import ProxyValidator

validator = ProxyValidator(timeout=10)
proxies = [...]

import time
start = time.time()
results = validator.validate_batch(proxies)
elapsed = time.time() - start

print(f"Validated {len(results)} in {elapsed}s")
```

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or with loguru
from loguru import logger
logger.enable("proxywhirl")
logger.add(sys.stderr, level="DEBUG")
```

### Inspect Cache

```python
stats = rotator.cache.get_statistics()
print(f"Hit rate: {stats.hit_rate:.2%}")
print(f"Entries: {stats.entry_count}")
print(f"Size: {stats.size_bytes}")
```

### Check Pool Health

```python
health = rotator.check_health()
print(f"Total: {health.total_proxies}")
print(f"Healthy: {health.healthy_count}")
print(f"Unhealthy: {health.unhealthy_count}")
```

