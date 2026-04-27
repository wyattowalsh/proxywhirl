# Cache Configuration and Tuning Guide

## Cache Architecture

ProxyWhirl uses a 3-tier cache architecture:

```
L1: In-Memory Cache (Dict)
    ├─ Fastest access (<1ms)
    ├─ Limited by RAM
    └─ Lost on restart

L2: Disk Cache (Compressed)
    ├─ Medium speed (1-10ms)
    ├─ Larger capacity
    └─ Persists across restarts

L3: Source Fetch (Network)
    ├─ Slowest (<100ms-5s)
    ├─ Unlimited capacity
    └─ Always fresh
```

## Basic Cache Configuration

```python
from proxywhirl import CacheConfig, ProxyConfiguration

cache_config = CacheConfig(
    enabled=True,
    ttl_seconds=3600,
    max_entries=1000,
    eviction_policy='lru'
)

config = ProxyConfiguration(
    sources=['http://example.com/proxies'],
    cache_config=cache_config
)
```

## Cache Parameters

| Parameter | Default | Impact |
|-----------|---------|--------|
| `enabled` | True | Enable/disable caching |
| `ttl_seconds` | 3600 | Time before entry expires |
| `max_entries` | 1000 | Maximum entries in L1 |
| `eviction_policy` | 'lru' | LRU or FIFO eviction |
| `compression_enabled` | True | Enable L2 compression |
| `compression_level` | 3 | Zstd compression (1-22) |

## Tuning Recommendations

### High-Frequency Requests
```python
cache_config = CacheConfig(
    ttl_seconds=600,          # Shorter TTL
    max_entries=5000,         # Larger L1
    compression_level=1       # Faster compression
)
```

### Memory-Constrained
```python
cache_config = CacheConfig(
    ttl_seconds=300,          # Very short TTL
    max_entries=100,          # Minimal L1
    compression_level=22      # Maximum compression
)
```

### Long-Running Services
```python
cache_config = CacheConfig(
    ttl_seconds=7200,         # Longer TTL
    max_entries=10000,        # Large L1
    compression_level=5       # Balanced compression
)
```

### Development/Testing
```python
cache_config = CacheConfig(
    enabled=True,
    ttl_seconds=60,           # Very short TTL
    max_entries=100
)
```

## Monitoring Cache Performance

```python
from proxywhirl import ProxyWhirl

rotator = ProxyWhirl(config=config)

# Get cache statistics
stats = rotator.cache.get_statistics()
print(f"Hit rate: {stats.hit_rate:.2%}")
print(f"Entries: {stats.entry_count}")
print(f"Size: {stats.size_bytes} bytes")

# Sample output:
# Hit rate: 85.50%
# Entries: 847
# Size: 2457600 bytes
```

## Cache Warming

Pre-populate cache with known proxies:

```python
from proxywhirl import CacheWarmup

warmup = CacheWarmup()
proxies = [...]  # Load from file or API

for proxy in proxies:
    rotator.cache.set(proxy.url, proxy, ttl=3600)
```

## Cache Invalidation Strategies

### Time-Based Expiration
```python
cache_config = CacheConfig(ttl_seconds=3600)
```

### Event-Based Invalidation
```python
# Refresh cache on health check failure
rotator.cache.invalidate(proxy.url)
```

### Batch Invalidation
```python
# Clear entire cache
rotator.cache.clear()

# Clear specific pattern
rotator.cache.clear_pattern('http://*')
```

## Memory Management

### Monitor Cache Growth
```python
import psutil

def check_cache_memory():
    stats = rotator.cache.get_statistics()
    if stats.size_bytes > 500_000_000:  # 500MB
        rotator.cache.clear()
        logger.warning("Cache cleared due to size")
```

### Automatic Cleanup
```python
cache_config = CacheConfig(
    max_entries=5000,
    eviction_policy='lru'  # Auto-evict oldest entries
)
```

## Compression Tuning

### Compression Levels
- 1-3: Fast, less compression
- 4-10: Balanced
- 11-22: Slow, maximum compression

```python
# Fast caching
cache_config = CacheConfig(compression_level=1)

# Balanced
cache_config = CacheConfig(compression_level=5)

# Maximum compression
cache_config = CacheConfig(compression_level=22)
```

## Distributed Caching

For multiple instances:

```python
from proxywhirl import CacheConfig

# Use shared SQLite backend
cache_config = CacheConfig(
    backend='sqlite',  # Shared across instances
    db_path='/var/lib/proxywhirl/cache.db'
)
```

## Troubleshooting

### Low Hit Rate
```python
# Symptom: Hit rate < 50%
# Solution: Increase TTL or max_entries

cache_config = CacheConfig(
    ttl_seconds=7200,   # Double TTL
    max_entries=5000    # Double max entries
)
```

### High Memory Usage
```python
# Symptom: Cache consuming >1GB
# Solution: Reduce TTL or max_entries, increase compression

cache_config = CacheConfig(
    ttl_seconds=300,
    max_entries=1000,
    compression_level=20
)
```

### Cache Corruption
```python
# Clear corrupted cache
rotator.cache.clear()

# Rebuild from sources
rotator.refresh_sources()
```

