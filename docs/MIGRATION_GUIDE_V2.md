# ProxyWhirl v2 Migration Guide

## Overview
ProxyWhirl v2 introduces breaking changes to improve performance, type safety, and maintainability. This guide helps you upgrade from v1.

## Breaking Changes

### 1. Proxy Pool Initialization
**v1:**
```python
pool = ProxyPool(proxies=proxy_list)
```

**v2:**
```python
pool = ProxyPool(proxies=proxy_list)
config = ProxyConfiguration(strategy="round_robin")
rotator = ProxyWhirl(config=config)
rotator.add_pool("default", pool)
```

### 2. Strategy Selection
**v1:**
```python
proxy = pool.select(strategy="weighted")
```

**v2:**
Strategy is set at ProxyWhirl initialization. Strategies support configuration:
```python
config = ProxyConfiguration(
    strategy="weighted",
    strategy_config=StrategyConfig(ema_alpha=0.3)
)
```

### 3. Async Context
**v1:**
Async and sync APIs were mixed.

**v2:**
Explicit separation:
- Sync: `ProxyWhirl` class
- Async: `AsyncProxyWhirl` class

### 4. Cache Configuration
**v1:**
```python
pool = ProxyPool(cache_enabled=True)
```

**v2:**
```python
config = ProxyConfiguration(
    cache_config=CacheConfig(
        max_size=1000,
        ttl_seconds=3600,
        enable_l2=True
    )
)
```

### 5. Error Handling
**v1:**
Generic `ProxyWhirlError` for all failures.

**v2:**
Specific exception hierarchy:
- `ProxyConnectionError` - Network issues
- `ProxyValidationError` - Invalid proxy format
- `ProxyPoolEmptyError` - No proxies available
- `CircuitBreakerOpenError` - Circuit breaker tripped
- `CacheCorruptionError` - Cache integrity issues

### 6. Proxy Credentials
**v1:**
```python
proxy_url = "http://user:pass@proxy.example.com:8080"
```

**v2:**
```python
credentials = ProxyCredentials(username="user", password="pass")
proxy = Proxy(
    host="proxy.example.com",
    port=8080,
    credentials=credentials
)
```

### 7. Metrics & Monitoring
**v1:**
Manual metrics collection.

**v2:**
Built-in Prometheus metrics via `metrics_collector`:
```python
from proxywhirl import MetricsCollector
collector = MetricsCollector()
rotator.attach_metrics(collector)
```

### 8. Configuration Format
**v1:**
Python dict configuration.

**v2:**
TOML configuration with validation:
```toml
[proxywhirl]
strategy = "performance_based"
max_retries = 3

[proxywhirl.cache]
max_size = 5000
ttl_seconds = 7200
```

## Deprecations & Removals

### Removed
- `ProxyPool.select_all()` - Use iteration instead
- `direct_http_request()` - Use httpx directly
- `legacy_proxy_format` parameter

### Deprecated (Still works)
- `Proxy.ema_alpha` field (moved to StrategyConfig)
- `pool.statistics()` - Use `pool.get_stats()` instead

## Migration Checklist

- [ ] Update imports to use v2 classes
- [ ] Replace `ProxyPool` initialization with `ProxyWhirl` pattern
- [ ] Update exception handling for new exception types
- [ ] Migrate YAML configs to TOML
- [ ] Update async code to use `AsyncProxyWhirl`
- [ ] Add type hints using new Literal and Protocol types
- [ ] Test with Python 3.10+ (dropped 3.9 support)

## Backward Compatibility Layer

v2 provides compatibility wrappers for common v1 patterns:
```python
from proxywhirl import ProxyPoolCompat
pool = ProxyPoolCompat(proxies=proxy_list)  # v1-style API
```

**Note:** Compatibility layer will be removed in v3. Migrate as soon as possible.

## Performance Improvements in v2

1. **3-tier Cache**: L1 (in-memory), L2 (encrypted), L3 (disk)
2. **Circuit Breaker**: Prevents cascading failures
3. **Adaptive Timeouts**: Based on proxy performance
4. **Distributed Locking**: Multi-node coordination support
5. **OpenTelemetry**: Distributed tracing integration

## Support

- Documentation: https://proxywhirl.dev/docs
- GitHub Issues: https://github.com/wyattowalsh/proxywhirl/issues
- Discussions: https://github.com/wyattowalsh/proxywhirl/discussions
