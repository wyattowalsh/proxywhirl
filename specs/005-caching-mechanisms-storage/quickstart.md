# Quickstart: Caching Mechanisms & Storage

**Feature**: 005-caching-mechanisms-storage  
**Last Updated**: 2025-11-01

## Overview

This guide demonstrates how to use ProxyWhirl's three-tier caching system (L1 memory, L2 flat file, L3 SQLite) for efficient proxy reuse with TTL-based expiration, health-based invalidation, and credential encryption.

## Installation

Add the caching dependencies:

```bash
uv add cryptography>=41.0.0
uv add portalocker>=2.8.0
```

## Basic Usage

### 1. Initialize Cache Manager

```python
from proxywhirl.cache import CacheManager
from proxywhirl.cache_models import CacheConfig

# Use default configuration (1000 L1, 5000 L2, unlimited L3)
cache = CacheManager()

# Or customize configuration
config = CacheConfig(
    default_ttl_seconds=7200,  # 2 hours
    l1_config=CacheTierConfig(max_entries=2000),
    l2_config=CacheTierConfig(max_entries=10000),
    encryption_key=SecretStr("your-32-byte-fernet-key-here")
)
cache = CacheManager(config)
```

### 2. Cache a Proxy

```python
from proxywhirl.models import Proxy
from proxywhirl.cache_models import CacheEntry
from datetime import datetime, timedelta, timezone
from pydantic import SecretStr

# Create proxy
proxy = Proxy(
    url="http://proxy1.example.com:8080",
    username="user",
    password=SecretStr("pass"),
    source="free-proxy-list"
)

# Create cache entry
entry = CacheEntry(
    key=generate_cache_key(proxy.url),  # URL hash
    proxy_url=proxy.url,
    username=proxy.username,
    password=proxy.password,
    source=proxy.source,
    fetch_time=datetime.now(timezone.utc),
    last_accessed=datetime.now(timezone.utc),
    ttl_seconds=3600,  # 1 hour
    expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
)

# Cache it (writes to L1, L2, L3)
success = cache.put(entry.key, entry)
print(f"Cached: {success}")
```

### 3. Retrieve from Cache

```python
# Get cached proxy (automatic tier promotion)
entry = cache.get("proxy_key_abc123")

if entry:
    print(f"Cache hit! Proxy: {entry.proxy_url}")
    print(f"Last accessed: {entry.last_accessed}")
    print(f"Access count: {entry.access_count}")
    print(f"Expires at: {entry.expires_at}")
else:
    print("Cache miss - proxy not found or expired")
```

### 4. Health-Based Invalidation

```python
# After health check failure
unhealthy_key = "proxy_key_xyz789"
invalidated = cache.invalidate_by_health(unhealthy_key)

if invalidated:
    print("Unhealthy proxy removed from cache")
```

### 5. Cache Statistics

```python
# Get performance metrics
stats = cache.get_statistics()

print(f"Overall hit rate: {stats.overall_hit_rate:.2%}")
print(f"L1 hit rate: {stats.l1_stats.hit_rate:.2%}")
print(f"L2 hit rate: {stats.l2_stats.hit_rate:.2%}")
print(f"L3 hit rate: {stats.l3_stats.hit_rate:.2%}")
print(f"Total cached: {stats.total_size} proxies")
print(f"Evictions (TTL): {stats.l1_stats.evictions_ttl}")
print(f"Evictions (LRU): {stats.l1_stats.evictions_lru}")
```

## Integration with ProxyRotator

### Automatic Caching

```python
from proxywhirl import ProxyRotator
from proxywhirl.cache import CacheManager

# Initialize rotator with cache
cache = CacheManager()
rotator = ProxyRotator(cache=cache)

# Add proxies - automatically cached
rotator.add_proxy("http://proxy1.com:8080", username="user1", password="pass1")
rotator.add_proxy("http://proxy2.com:8080", username="user2", password="pass2")

# Get proxy - checks cache first
proxy = rotator.get_proxy()  # Fast! From L1 cache

# After restart, proxies restored from L2/L3
rotator = ProxyRotator(cache=CacheManager())  # Loads persisted proxies
proxy = rotator.get_proxy()  # Still fast!
```

## Advanced Features

### Cache Warming

Pre-populate cache from file during startup:

```python
# Import proxy list from JSON/JSONL/CSV
imported = cache.warm_from_file("proxies.json", ttl_seconds=7200)
print(f"Warmed cache with {imported} proxies")
```

**proxies.json format**:
```json
[
  {
    "url": "http://proxy1.com:8080",
    "username": "user1",
    "password": "pass1",
    "source": "import"
  },
  {
    "url": "http://proxy2.com:8080",
    "username": "user2",
    "password": "pass2",
    "source": "import"
  }
]
```

### Cache Export (Backup)

```python
# Export all cached proxies for backup
exported = cache.export_to_file("backup.jsonl")
print(f"Exported {exported} proxies")

# Export specific tier only
exported_l1 = cache.export_to_file("l1_backup.jsonl", tier="l1")
```

### Manual Cache Clearing

```python
# Clear all caches
cleared = cache.clear()
print(f"Cleared {cleared} entries from all tiers")

# Clear specific tier
cache.l1_tier.clear()  # Memory only
cache.l2_tier.clear()  # Flat files only
cache.l3_tier.clear()  # SQLite only
```

### Graceful Degradation

Cache automatically handles storage failures:

```python
# If L3 (SQLite) fails (disk full, permission denied)
# → Cache disables L3, continues with L1+L2
# → Logs ERROR and emits metric 'cache_tier_degraded'

# If L2 (files) fails
# → Cache disables L2, continues with L1 only
# → System still operational, just reduced persistence

# Check degradation status
stats = cache.get_statistics()
if stats.l3_degraded:
    print("WARNING: L3 cache tier degraded - reduced persistence")
```

## Configuration

### Environment Variables

```bash
# Encryption key for credentials (required for L2/L3)
export PROXYWHIRL_CACHE_ENCRYPTION_KEY="your-32-byte-base64-key"

# Generate new key:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Configuration File

```python
from proxywhirl.cache_models import CacheConfig, CacheTierConfig
from pydantic import SecretStr
import os

config = CacheConfig(
    # Tier sizes
    l1_config=CacheTierConfig(max_entries=1000),  # Memory
    l2_config=CacheTierConfig(max_entries=5000),  # Files
    l3_config=CacheTierConfig(max_entries=None),  # SQLite (unlimited)
    
    # TTL settings
    default_ttl_seconds=3600,  # 1 hour default
    ttl_cleanup_interval=60,   # Cleanup every 60 seconds
    
    # Storage paths
    l2_cache_dir=".cache/proxies",
    l3_database_path=".cache/proxywhirl.db",
    
    # Security
    encryption_key=SecretStr(os.environ.get("PROXYWHIRL_CACHE_ENCRYPTION_KEY", "")),
    
    # Health integration
    health_check_invalidation=True,
    failure_threshold=3,  # Invalidate after 3 failures
    
    # Performance
    enable_statistics=True,
    statistics_interval=5  # Aggregate every 5 seconds
)

cache = CacheManager(config)
```

## Testing

### Unit Tests

```python
import pytest
from proxywhirl.cache import CacheManager
from proxywhirl.cache_models import CacheEntry
import time

def test_cache_ttl_expiration():
    """Test TTL-based expiration"""
    cache = CacheManager()
    
    # Cache entry with 1-second TTL
    entry = CacheEntry(
        key="test_key",
        proxy_url="http://test.com:8080",
        source="test",
        fetch_time=datetime.now(timezone.utc),
        last_accessed=datetime.now(timezone.utc),
        ttl_seconds=1,
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=1)
    )
    
    cache.put(entry.key, entry)
    assert cache.get(entry.key) is not None  # Found
    
    time.sleep(2)  # Wait for expiration
    assert cache.get(entry.key) is None  # Expired
```

### Integration Tests

```python
def test_cache_persistence_across_restarts():
    """Test US1: Persist fetched proxies"""
    # First session: cache proxy
    cache1 = CacheManager()
    entry = create_test_entry()
    cache1.put(entry.key, entry)
    del cache1  # Simulate shutdown
    
    # Second session: load from persistence
    cache2 = CacheManager()
    retrieved = cache2.get(entry.key)
    assert retrieved is not None
    assert retrieved.proxy_url == entry.proxy_url
```

## Performance Benchmarks

Expected performance (from SC-* criteria):

| Operation | Target | Typical |
|-----------|--------|---------|
| L1 lookup | <1ms | ~100μs |
| L2 lookup | <50ms | ~10ms |
| L3 lookup | <50ms | ~5ms |
| Cache warming (10k) | <5s | ~3s |
| Eviction overhead | <10ms | ~100μs |

Run benchmarks:

```bash
uv run pytest tests/benchmarks/test_cache_performance.py -v
```

## Troubleshooting

### High Cache Miss Rate

```python
stats = cache.get_statistics()
if stats.overall_hit_rate < 0.5:  # <50%
    # Possible causes:
    # 1. TTL too short → increase default_ttl_seconds
    # 2. Proxies changing frequently → adjust TTL per source
    # 3. L1 size too small → increase l1_config.max_entries
    pass
```

### Disk Space Exhausted

```python
# Cache automatically disables L2/L3 and logs ERROR
# Check logs for: "cache_tier_degraded" metrics
# Solution: Clear old cache files or increase disk space

# Manual recovery:
cache.l2_tier.clear()  # Free up file space
cache.l3_tier.clear()  # Free up SQLite space
```

### Encryption Key Lost

```python
# If PROXYWHIRL_CACHE_ENCRYPTION_KEY is lost:
# → Cannot decrypt cached credentials
# → Cache will fail to load L2/L3 entries
# → Solution: Clear cache and re-populate

cache.clear()  # Remove encrypted entries
cache.warm_from_file("proxies.json")  # Re-import with new key
```

## Next Steps

- Read [data-model.md](./data-model.md) for detailed entity schemas
- Review [research.md](./research.md) for implementation decisions
- Check [contracts/cache-api.json](./contracts/cache-api.json) for full API
- See [tasks.md](./tasks.md) for implementation phases (coming soon)

## API Reference

Full API documentation generated from code:

```bash
uv run python -m pydoc proxywhirl.cache
uv run python -m pydoc proxywhirl.cache_models
```
