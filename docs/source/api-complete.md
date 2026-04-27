# Complete API Reference

## Overview

This document provides comprehensive API documentation for all public functions in ProxyWhirl.

## Core Rotators

### ProxyWhirl (Synchronous)

```python
from proxywhirl import ProxyWhirl, ProxyConfiguration

config = ProxyConfiguration(
    sources=['http://free-proxy-list.net'],
    validation_level='strict',
    cache_config={'enabled': True, 'ttl_seconds': 3600}
)

rotator = ProxyWhirl(config=config)

# Get next proxy
proxy = rotator.get_proxy()

# Get specific number of proxies
proxies = rotator.get_proxies(count=5)

# Check health
health = rotator.check_health()

# Custom selection
from proxywhirl import SelectionContext
ctx = SelectionContext(
    country='US',
    proxy_type='http',
    prefer_fresh=True
)
proxy = rotator.select_proxy(ctx)

# Refresh sources
rotator.refresh_sources()

# Shutdown
rotator.shutdown()
```

### AsyncProxyWhirl (Asynchronous)

```python
from proxywhirl import AsyncProxyWhirl, ProxyConfiguration
import asyncio

async def main():
    config = ProxyConfiguration(
        sources=['http://free-proxy-list.net'],
        validation_level='strict'
    )
    
    async with AsyncProxyWhirl(config=config) as rotator:
        # Get next proxy
        proxy = await rotator.get_proxy()
        
        # Get multiple proxies
        proxies = await rotator.get_proxies(count=5)
        
        # Check health
        health = await rotator.check_health()
        
        # Custom selection
        from proxywhirl import SelectionContext
        ctx = SelectionContext(country='US')
        proxy = await rotator.select_proxy(ctx)

asyncio.run(main())
```

## Configuration Models

### ProxyConfiguration

Primary configuration object:

```python
from proxywhirl import ProxyConfiguration, StrategyConfig, CacheConfig

config = ProxyConfiguration(
    sources=['source1', 'source2'],
    strategy_config=StrategyConfig(
        name='round_robin',
        weight_distribution={'source1': 0.7, 'source2': 0.3}
    ),
    cache_config=CacheConfig(
        enabled=True,
        ttl_seconds=3600,
        max_entries=1000
    ),
    validation_level='strict',
    max_retries=3,
    timeout_seconds=10,
    user_agent_rotation=True
)
```

### StrategyConfig

```python
from proxywhirl import StrategyConfig

config = StrategyConfig(
    name='weighted_round_robin',
    weight_distribution={
        'high_quality_source': 0.6,
        'standard_source': 0.4
    }
)
```

### CacheConfig

```python
from proxywhirl import CacheConfig

config = CacheConfig(
    enabled=True,
    ttl_seconds=3600,
    max_entries=1000,
    eviction_policy='lru',
    compression_enabled=True
)
```

## Health Monitoring

### HealthMonitor

```python
from proxywhirl import HealthMonitor

monitor = HealthMonitor()

# Check single proxy
health = monitor.check_proxy('http://proxy.example.com:8080')

# Check multiple proxies
healths = monitor.check_proxies(proxies)

# Get health statistics
stats = monitor.get_statistics()
```

## Validation

### ProxyValidator

```python
from proxywhirl import ProxyValidator

validator = ProxyValidator(timeout=10)

# Validate single proxy
is_valid = validator.validate_proxy('http://proxy.example.com:8080')

# Validate batch
results = validator.validate_batch(proxies)

# Get validation stats
stats = validator.get_stats()
```

## Proxy Models

### Proxy

```python
from proxywhirl import Proxy, HealthStatus

proxy = Proxy(
    url='http://192.168.1.1:8080',
    protocol='http',
    country='US',
    is_residential=False,
    last_checked=None,
    health_status=HealthStatus.HEALTHY
)

# Access properties
ip = proxy.ip
port = proxy.port
is_anonymous = proxy.is_anonymous
```

### ProxyPool

```python
from proxywhirl import ProxyPool

pool = ProxyPool(proxies=[...])

# Get statistics
stats = pool.get_statistics()

# Filter proxies
filtered = pool.filter(country='US', proxy_type='http')

# Get healthy proxies
healthy = pool.get_healthy_proxies()
```

## Circuit Breaker

### CircuitBreaker

```python
from proxywhirl import CircuitBreaker, CircuitBreakerConfig

config = CircuitBreakerConfig(
    failure_threshold=5,
    recovery_timeout=60,
    half_open_max_calls=2
)

breaker = CircuitBreaker(config=config)

# Execute with circuit breaker
result = breaker.call(
    lambda: make_request_with_proxy(proxy)
)

# Check state
is_open = breaker.is_open()
state = breaker.get_state()
```

## Retry Executor

### RetryExecutor

```python
from proxywhirl import RetryExecutor, RetryPolicy

policy = RetryPolicy(
    max_retries=3,
    backoff_factor=2,
    backoff_type='exponential'
)

executor = RetryExecutor(policy=policy)

# Execute with retries
result = executor.execute(
    lambda: make_request_with_proxy(proxy)
)
```

## Rate Limiter

### RateLimiter

```python
from proxywhirl import RateLimiter

limiter = RateLimiter(
    requests_per_second=10,
    burst_size=20
)

# Check if allowed
if limiter.is_allowed():
    # Make request
    response = make_request()

# Wait until allowed
limiter.wait_until_allowed()
make_request()
```

## Data Export

### DataExporter

```python
from proxywhirl import DataExporter, ExportFormat

exporter = DataExporter()

# Export to JSON
exporter.to_json(proxies, 'proxies.json')

# Export to CSV
exporter.to_csv(proxies, 'proxies.csv')

# Export to YAML
exporter.to_yaml(proxies, 'proxies.yaml')

# Get formatted string
json_str = exporter.format(proxies, ExportFormat.JSON)
```

## Fetchers

### ProxyFetcher

```python
from proxywhirl import ProxyFetcher

fetcher = ProxyFetcher()

# Fetch from source
proxies = fetcher.fetch('http://free-proxy-list.net')

# Fetch with timeout
proxies = fetcher.fetch(
    'http://free-proxy-list.net',
    timeout=30
)
```

## Cache Management

### CacheManager

```python
from proxywhirl import CacheManager

cache = CacheManager()

# Get cached value
proxy = cache.get('proxy_key')

# Set cached value
cache.set('proxy_key', proxy, ttl=3600)

# Get statistics
stats = cache.get_statistics()

# Clear cache
cache.clear()
```

## Error Handling

All functions raise exceptions from the `ProxyWhirlError` hierarchy:

```python
from proxywhirl import (
    ProxyWhirlError,
    ProxyPoolEmptyError,
    ProxyValidationError,
    ProxyConnectionError,
    ProxyAuthenticationError,
    ProxyFetchError,
    ProxyStorageError,
    RetryableError,
    NonRetryableError
)

try:
    proxy = rotator.get_proxy()
except ProxyPoolEmptyError:
    print("No proxies available")
except ProxyValidationError as e:
    print(f"Validation failed: {e}")
except ProxyWhirlError as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

1. **Always use context managers** for async rotators
2. **Configure timeouts** appropriately for your use case
3. **Use health monitoring** to track proxy quality
4. **Implement retries** for transient failures
5. **Cache proxies** to reduce validation overhead
6. **Monitor metrics** for performance insights
7. **Use structured logging** for debugging
8. **Test with real scenarios** before production

## Examples

See `examples/` directory for complete working examples.

