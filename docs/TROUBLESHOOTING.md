# ProxyWhirl Troubleshooting Guide

## Common Issues and Solutions

### 1. No Proxies Available Error

**Error:**
```
ProxyPoolEmptyError: All proxies are exhausted or dead
```

**Causes:**
- All proxies failed validation
- Circuit breaker opened due to failures
- Timeout too aggressive

**Solutions:**
```python
# Increase timeout
config = ProxyConfiguration(
    validation_level=ValidationLevel.BASIC,  # Use faster validation
    http_timeout=30  # Increase from default 10s
)

# Check proxy sources
from proxywhirl import RECOMMENDED_SOURCES
pool = ProxyPool()
pool.fetch_proxies(RECOMMENDED_SOURCES)  # Use reliable sources

# Lower failure threshold
circuit_breaker_config = CircuitBreakerConfig(
    failure_threshold=10,  # More tolerance
    window_duration=300  # 5 min window
)
```

### 2. All Proxies Marked Dead

**Symptoms:**
- Proxies work in curl but fail in app
- All proxies have `status = dead`

**Causes:**
- Proxy requires specific headers
- Connection pooling issues
- IP-based blocking

**Solutions:**
```python
# Disable validation during setup
pool = ProxyPool(validate_on_add=False)

# Add custom headers
from proxywhirl.custom_headers import CustomHeaderManager
headers = CustomHeaderManager()
headers.add("User-Agent", "Mozilla/5.0 ...")
rotator.attach_headers(headers)

# Increase validation timeout
config = ProxyConfiguration(
    validation_timeout=15,  # seconds
    validation_retries=3
)

# Check individual proxy
proxy = Proxy(url="http://proxy.example.com:8080")
is_valid = await proxy.validate()  # Check if it works
```

### 3. Circuit Breaker Always Open

**Error:**
```
CircuitBreakerOpenError: Circuit breaker is open
```

**Causes:**
- Too many consecutive failures
- Threshold too low
- Timeout too short

**Solutions:**
```python
config = ProxyConfiguration(
    circuit_breaker_config=CircuitBreakerConfig(
        failure_threshold=5,  # More failures allowed
        timeout_duration=60,  # Longer recovery time
        window_duration=600  # Longer observation window
    )
)

# Or reset manually
rotator.circuit_breaker.reset()
```

### 4. Memory Usage Growing Unbounded

**Symptoms:**
- Memory increases over time
- OOM after hours of running

**Causes:**
- Cache not evicting old entries
- Connection pools leaking
- Metrics accumulating

**Solutions:**
```python
# Configure cache limits
cache_config = CacheConfig(
    max_size=5000,  # Limit entries
    max_age_seconds=3600,  # Evict old entries
    enable_l2=True,  # Use disk cache
    l2_path="/var/cache/proxywhirl"
)

# Limit metrics history
from proxywhirl.metrics_collector import MetricsCollector
collector = MetricsCollector(max_samples=1000)

# Close connections periodically
await rotator.cleanup()  # Clean up resources
```

### 5. Performance Degradation Over Time

**Symptoms:**
- Selection takes 1ms initially, 100ms+ after hours
- CPU usage increases

**Causes:**
- Strategy metrics accumulating
- Cache fragmentation
- Connection pool bloat

**Solutions:**
```python
# Enable metrics sampling
config = ProxyConfiguration(
    sampling_rate=0.1  # Only sample 10% of requests
)

# Compact cache periodically
await rotator.cache_manager.compact()

# Reduce metrics retention
config = ProxyConfiguration(
    metrics_retention_seconds=3600  # 1 hour max
)
```

### 6. SOCKS5 Proxies Not Working

**Error:**
```
ProxyConnectionError: SOCKS5 proxy connection failed
```

**Causes:**
- httpx doesn't natively support SOCKS
- Incorrect proxy URL format

**Solutions:**
```python
# Use SOCKS proxy library
import httpx
# httpx requires httpcore[socks] extra
from httpx import AsyncClient
from httpcore.proxy import HTTPProxyTransport, SOCKSProxyTransport

transport = SOCKSProxyTransport.from_url(
    "socks5://localhost:1080",
    verify=False
)

# Or use dedicated SOCKS client
import socksio
# See examples/socks_example.py
```

### 7. Database Locked Error

**Error:**
```
sqlite3.OperationalError: database is locked
```

**Causes:**
- Multiple processes writing simultaneously
- Long-running transaction

**Solutions:**
```python
# Use distributed locking
from proxywhirl.locks import DistributedLock

async with DistributedLock("proxywhirl"):
    # Safe database access
    await rotator.save_state()

# Or increase timeout
import sqlite3
sqlite3.connect(":memory:", timeout=30)
```

### 8. Validation Hangs on Certain Proxies

**Symptoms:**
- Validation process stalls
- Timeout not working

**Causes:**
- Proxy doesn't respond but doesn't close
- Timeout configured incorrectly

**Solutions:**
```python
# Set strict timeout
import asyncio
config = ProxyConfiguration(
    validation_timeout=5  # 5 seconds max
)

# Use validation in separate task
async def validate_with_timeout(proxy):
    try:
        await asyncio.wait_for(
            proxy.validate(),
            timeout=5
        )
    except asyncio.TimeoutError:
        proxy.mark_dead()
```

### 9. CSV/JSON Parsing Errors

**Error:**
```
ProxyFetchError: Failed to parse proxy list
```

**Solutions:**
```python
from proxywhirl.fetchers import ProxyFetcher
from proxywhirl.models import ProxyFormat

fetcher = ProxyFetcher()

# Auto-detect format
proxies = await fetcher.fetch_from_source(
    url="https://example.com/proxies",
    format=ProxyFormat.AUTO  # Auto-detect
)

# Or specify explicit format
proxies = await fetcher.fetch_from_source(
    url="https://example.com/proxies.csv",
    format=ProxyFormat.CSV,
    csv_delimiter="|"
)
```

### 10. AsyncIO Event Loop Issues

**Error:**
```
RuntimeError: Event loop is closed
EventLoopConflictError: Cannot create AsyncProxyWhirl in sync context
```

**Solutions:**
```python
# Use correct class for context
if sync_context:
    rotator = ProxyWhirl()  # Sync
else:
    rotator = AsyncProxyWhirl()  # Async

# Proper async initialization
async def main():
    rotator = AsyncProxyWhirl()
    # Use rotator
    await rotator.close()

asyncio.run(main())
```

## Debug Mode

Enable verbose logging:
```python
import logging
from loguru import logger

logger.enable("proxywhirl")
logger.add("debug.log", level="DEBUG")

# Or via environment
export PROXYWHIRL_LOG_LEVEL=DEBUG
```

## Performance Profiling

```bash
# Memory profiling
python -m memory_profiler examples/basic_usage.py

# CPU profiling
python -m cProfile -s cumtime examples/basic_usage.py

# Async profiling
python -m asyncio_profiler examples/async_example.py
```

## Getting Help

1. **Check logs**: Look in `logs/proxywhirl.log`
2. **Enable debug mode**: Set `PROXYWHIRL_LOG_LEVEL=DEBUG`
3. **Report issue**: GitHub Issues with logs and version
4. **Community**: GitHub Discussions

