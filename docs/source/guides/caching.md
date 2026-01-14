---
title: Caching Subsystem Guide
---

# Caching Subsystem Guide

ProxyWhirl implements a sophisticated three-tier caching system for proxy persistence, performance optimization, and credential security. This guide covers architecture, configuration, encryption, and performance tuning.

## Architecture Overview

The caching subsystem uses a hierarchical three-tier design for optimal performance and durability:

```{list-table}
:header-rows: 1
:widths: 10 15 20 25 30

* - Tier
  - Storage
  - Typical Latency
  - Capacity
  - Use Case
* - **L1**
  - In-Memory (OrderedDict)
  - ~100 ns
  - 1,000 entries (default)
  - Hot proxies, LRU eviction
* - **L2**
  - SQLite (l2_cache.db)
  - ~1-10 ms
  - 5,000 entries (default)
  - Warm storage, B-tree indexed
* - **L3**
  - SQLite Database
  - ~5-50 ms
  - Unlimited (default)
  - Cold storage, full queryability
```

### Tier Promotion & Demotion

Proxies automatically promote from slower to faster tiers on access:

- **L3 → L2 → L1**: On cache hit, entry copies to higher tiers
- **L1 → L2 → L3**: When L1 is full, LRU entry evicts to lower tiers

```{tip}
This design minimizes latency for frequently-used proxies while maintaining full persistence in L3.
```

### L2 vs L3 SQLite Differences

Both L2 and L3 use SQLite databases, but with different schemas and purposes:

**L2 (l2_cache.db)**:
- Simpler schema optimized for fast lookups
- Stores basic cache fields (proxy_url, credentials, TTL, health status)
- Uses `l2_cache` table
- Designed for ~5,000 entries with LRU eviction
- Separate database file in cache directory

**L3 (proxywhirl.db)**:
- Full schema with health monitoring fields
- Includes `cache_entries` table with health check history
- Additional `health_history` table for tracking check results over time
- Unlimited capacity (no eviction)
- Main application database

```{note}
The dual-SQLite design provides performance benefits:
- L2 uses a lighter schema for faster writes during rotation
- L3 maintains full historical data for analytics and monitoring
- Both use B-tree indexes for O(log n) lookups instead of O(n) JSONL scans
```

## Core Components

### CacheManager

Central orchestrator for all cache operations across tiers.

```python
from proxywhirl.cache import CacheManager, CacheConfig

config = CacheConfig(
    default_ttl_seconds=3600,
    l1_config=CacheTierConfig(max_entries=1000),
    l2_config=CacheTierConfig(max_entries=5000),
    l3_config=CacheTierConfig(max_entries=None),  # unlimited
)

manager = CacheManager(config)
```

**Key Methods:**

- `get(key)`: Retrieve entry with automatic tier promotion
- `put(key, entry)`: Store entry in all enabled tiers
- `delete(key)`: Remove entry from all tiers
- `invalidate_by_health(key)`: Mark unhealthy and evict if threshold exceeded
- `clear()`: Remove all entries from all tiers
- `get_statistics()`: Retrieve hit rates, sizes, and degradation status

### CacheEntry

Pydantic model representing a single cached proxy with metadata.

```python
from proxywhirl.cache import CacheEntry, HealthStatus
from pydantic import SecretStr
from datetime import datetime, timezone, timedelta

entry = CacheEntry(
    key="abc123",
    proxy_url="http://proxy.example.com:8080",
    username=SecretStr("user"),
    password=SecretStr("pass"),
    source="fetched",
    fetch_time=datetime.now(timezone.utc),
    ttl_seconds=3600,
    expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    health_status=HealthStatus.HEALTHY,
    access_count=0,
    last_accessed=datetime.now(timezone.utc),
)

# Check expiration
if entry.is_expired:
    print("Entry expired")

# Check health
if entry.is_healthy:
    print("Proxy is healthy")
```

**Key Fields:**

- `key`: SHA256 hash of proxy URL (first 16 chars)
- `proxy_url`: Full proxy URL (scheme://host:port)
- `username`, `password`: SecretStr in memory, encrypted at rest
- `ttl_seconds`, `expires_at`: Time-to-live configuration
- `health_status`: HEALTHY | UNHEALTHY | UNKNOWN
- `failure_count`: Consecutive failures for health invalidation
- `access_count`, `last_accessed`: Access tracking for LRU

**Health Monitoring Fields** (Feature 006):

- `last_health_check`: Last health check timestamp
- `consecutive_health_failures`: Consecutive health check failures
- `consecutive_health_successes`: Consecutive successful checks
- `recovery_attempt`: Current recovery attempt count
- `next_check_time`: Scheduled next health check
- `last_health_error`: Last health check error message
- `total_health_checks`: Total health checks performed
- `total_health_check_failures`: Total failures across lifetime

### CacheConfig

Comprehensive configuration for cache behavior and tier settings.

```python
from proxywhirl.cache import CacheConfig, CacheTierConfig
from pydantic import SecretStr

config = CacheConfig(
    # Tier configuration
    l1_config=CacheTierConfig(
        enabled=True,
        max_entries=1000,
        eviction_policy="lru",  # lru | lfu | fifo
    ),
    l2_config=CacheTierConfig(
        enabled=True,
        max_entries=5000,
        eviction_policy="lru",
    ),
    l3_config=CacheTierConfig(
        enabled=True,
        max_entries=None,  # unlimited
        eviction_policy="lru",
    ),

    # TTL configuration
    default_ttl_seconds=3600,
    ttl_cleanup_interval=60,
    enable_background_cleanup=True,
    cleanup_interval_seconds=60,
    per_source_ttl={
        "premium": 7200,
        "free": 1800,
    },

    # Storage paths
    l2_cache_dir=".cache/proxies",           # L2 SQLite: .cache/proxies/l2_cache.db
    l3_database_path=".cache/db/proxywhirl.db",  # L3 SQLite main database

    # Encryption
    encryption_key=SecretStr("..."),  # or set PROXYWHIRL_CACHE_ENCRYPTION_KEY

    # Health integration
    health_check_invalidation=True,
    failure_threshold=3,

    # Performance tuning
    enable_statistics=True,
    statistics_interval=5,
)
```

### CacheStatistics

Real-time statistics across all tiers for monitoring and optimization.

```python
stats = manager.get_statistics()

# Per-tier statistics
print(f"L1 hit rate: {stats.l1_stats.hit_rate:.2%}")
print(f"L2 hit rate: {stats.l2_stats.hit_rate:.2%}")
print(f"L3 hit rate: {stats.l3_stats.hit_rate:.2%}")

# Aggregate statistics
print(f"Overall hit rate: {stats.overall_hit_rate:.2%}")
print(f"Total size: {stats.total_size} entries")
print(f"Promotions: {stats.promotions}")
print(f"Demotions: {stats.demotions}")

# Degradation status
if stats.l1_degraded:
    print("WARNING: L1 tier degraded")
if stats.l2_degraded:
    print("WARNING: L2 tier degraded")
if stats.l3_degraded:
    print("WARNING: L3 tier degraded")

# Export to monitoring systems (Prometheus, Datadog, etc.)
metrics = stats.to_metrics_dict()
# {
#   "cache.l1.hit_rate": 0.85,
#   "cache.overall.hit_rate": 0.92,
#   "cache.total_size": 6234.0,
#   ...
# }
```

**TierStatistics Fields:**

- `hits`, `misses`: Cache hit/miss counts
- `current_size`: Current number of entries
- `evictions_lru`: LRU-based evictions
- `evictions_ttl`: TTL-based evictions
- `evictions_health`: Health-based evictions
- `evictions_corruption`: Corruption-based evictions
- `hit_rate`: Computed hit rate (hits / (hits + misses))
- `total_evictions`: Sum of all eviction types

## Credential Encryption

The `CredentialEncryptor` class provides Fernet symmetric encryption (AES-128-CBC + HMAC) for proxy credentials stored in L2 (JSONL files) and L3 (SQLite database).

### Encryption Setup

Set the encryption key via environment variable:

```bash
export PROXYWHIRL_CACHE_ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
```

Or provide it explicitly in code:

```python
from pydantic import SecretStr

config = CacheConfig(
    encryption_key=SecretStr("your-fernet-key-here")
)
```

```{warning}
**Key Management Best Practices:**
- Store keys in environment variables, not in code
- Rotate keys periodically using the key rotation feature
- Lost keys = permanently encrypted data
- Use cloud secret managers (AWS Secrets Manager, GCP Secret Manager) in production
```

### Key Rotation

ProxyWhirl supports gradual key rotation using MultiFernet, allowing you to rotate encryption keys without downtime or data loss.

**How Key Rotation Works:**

1. **Current Key**: New data is encrypted with `PROXYWHIRL_CACHE_ENCRYPTION_KEY`
2. **Previous Key**: Old data can be decrypted with `PROXYWHIRL_CACHE_KEY_PREVIOUS`
3. **Automatic Fallback**: MultiFernet tries current key first, then previous key

**Performing Key Rotation:**

```python
from cryptography.fernet import Fernet
from proxywhirl.cache.crypto import rotate_key

# Generate new key
new_key = Fernet.generate_key().decode()

# Rotate to new key (moves current to previous)
rotate_key(new_key)

# Verify rotation
import os
print(f"Current: {os.environ['PROXYWHIRL_CACHE_ENCRYPTION_KEY'][:20]}...")
print(f"Previous: {os.environ['PROXYWHIRL_CACHE_KEY_PREVIOUS'][:20]}...")
```

**Manual Rotation via Environment Variables:**

```bash
# Step 1: Generate new key
NEW_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

# Step 2: Move current key to previous
export PROXYWHIRL_CACHE_KEY_PREVIOUS=$PROXYWHIRL_CACHE_ENCRYPTION_KEY

# Step 3: Set new key as current
export PROXYWHIRL_CACHE_ENCRYPTION_KEY=$NEW_KEY
```

**Key Rotation Workflow:**

```python
# Before rotation: old key encrypts and decrypts
old_encryptor = CredentialEncryptor()
encrypted_old = old_encryptor.encrypt(SecretStr("password"))

# Perform rotation
rotate_key(Fernet.generate_key().decode())

# After rotation: new encryptor can decrypt old data
new_encryptor = CredentialEncryptor()
decrypted_old = new_encryptor.decrypt(encrypted_old)  # Still works!

# New data encrypted with new key
encrypted_new = new_encryptor.encrypt(SecretStr("new_password"))
```

**Re-encryption Strategy:**

After rotation, gradually re-encrypt old data to remove dependency on previous key:

```python
from proxywhirl.cache import CacheManager

manager = CacheManager(config)

# Iterate all cache entries
for key in manager.list_all_keys():  # hypothetical method
    entry = manager.get(key)
    if entry:
        # Get triggers decryption with previous key
        # Put triggers re-encryption with current key
        manager.put(key, entry)
```

```{note}
You can have at most 2 keys active simultaneously (current + previous). For multiple-key scenarios, chain rotations over time.
```

### Encryption Behavior

- **L1 (Memory)**: Credentials stored as `SecretStr` (not encrypted)
- **L2 (SQLite)**: Credentials encrypted as BLOB fields in `l2_cache.db`
- **L3 (SQLite)**: Credentials encrypted as BLOB fields in main database

**Automatic Encryption/Decryption:**

```python
# Put: encrypts credentials before writing to L2/L3
entry = CacheEntry(
    key="abc123",
    proxy_url="http://proxy.example.com:8080",
    username=SecretStr("myuser"),
    password=SecretStr("mypassword"),
    # ... other fields ...
)
manager.put(entry.key, entry)

# Get: decrypts credentials when reading from L2/L3
retrieved = manager.get("abc123")
print(retrieved.username.get_secret_value())  # "myuser"
print(retrieved.password.get_secret_value())  # "mypassword"
```

```{note}
`SecretStr` prevents accidental credential leakage in logs, JSON serialization, and repr() output. Always use `.get_secret_value()` to access the plaintext.
```

## TTL and Expiration

### TTL Configuration

Proxies have configurable time-to-live (TTL) with per-source overrides:

```python
config = CacheConfig(
    default_ttl_seconds=3600,  # 1 hour default
    per_source_ttl={
        "premium": 7200,       # 2 hours for premium sources
        "free": 1800,          # 30 minutes for free sources
        "custom": 10800,       # 3 hours for custom sources
    },
)
```

### Expiration Strategies

ProxyWhirl uses **hybrid lazy + background cleanup**:

1. **Lazy Expiration**: On every `get()` operation, checks `entry.is_expired` and deletes if expired
2. **Background Cleanup**: Periodic scan of all tiers to bulk-remove expired entries (optional)

```python
# Enable background cleanup
config = CacheConfig(
    enable_background_cleanup=True,
    cleanup_interval_seconds=60,  # runs every 60 seconds
)

manager = CacheManager(config)
# Background thread automatically starts
```

**Bulk Cleanup Performance:**

- **L1 (Memory)**: O(n) scan, filters expired entries
- **L2 (SQLite)**: O(1) with indexed DELETE query on `l2_cache.db`
- **L3 (SQLite)**: O(1) with indexed DELETE query on main database

```sql
-- L2/L3 cleanup (both use efficient indexed DELETE)
DELETE FROM cache_entries WHERE expires_at < ?
-- or for L2:
DELETE FROM l2_cache WHERE expires_at < ?
```

```{tip}
For write-heavy workloads, disable background cleanup and rely on lazy expiration to reduce I/O.
```

## Health Invalidation

The cache integrates with the health monitoring system to automatically evict failing proxies.

### Configuration

```python
config = CacheConfig(
    health_check_invalidation=True,  # enable auto-eviction
    failure_threshold=3,              # evict after 3 consecutive failures
)
```

### Invalidation Workflow

1. Health check fails for a proxy
2. `invalidate_by_health(key)` increments `failure_count`
3. Sets `health_status = UNHEALTHY`
4. If `failure_count >= failure_threshold`, evicts from all tiers
5. Updates `evictions_health` statistics

```python
# Manual health invalidation
manager.invalidate_by_health("abc123")

# After 3 consecutive failures, the proxy is evicted
# and statistics.l1_stats.evictions_health += 1
```

```{note}
Even if `health_check_invalidation=False`, failure counts are still tracked. This allows post-hoc analysis without automatic eviction.
```

## Migration from JSONL L2 Cache

ProxyWhirl previously used JSONL files for L2 cache but has migrated to SQLite for better performance. The `DiskCacheTier` class provides a migration utility for existing JSONL cache data.

### Migrating Legacy JSONL Caches

If you have existing `shard_*.jsonl` files from a previous version, migrate them to the new SQLite L2 cache:

```python
from pathlib import Path
from proxywhirl.cache import CacheConfig, CacheManager
from proxywhirl.cache.tiers import DiskCacheTier, TierType

# Initialize L2 tier
config = CacheConfig(l2_cache_dir=".cache/proxies")
tier = DiskCacheTier(
    config=config.l2_config,
    tier_type=TierType.L2_FILE,
    cache_dir=Path(config.l2_cache_dir),
)

# Migrate from JSONL files in the same directory
migrated = tier.migrate_from_jsonl()
print(f"Migrated {migrated} entries from JSONL to SQLite L2 cache")
```

The migration:
- Reads all `shard_*.jsonl` files in the cache directory
- Decrypts credentials (if encrypted in JSONL)
- Imports entries into the SQLite `l2_cache.db` database
- Preserves all metadata (TTL, health status, access counts)
- Skips corrupted entries and continues

```{tip}
After successful migration, delete the old `shard_*.jsonl` files to free up disk space.
```

## Cache Warming

Pre-populate the cache from external proxy lists for faster startup.

### Supported Formats

- **JSON**: Array of proxy objects
- **JSONL**: Newline-delimited JSON objects
- **CSV**: Header-based with `proxy_url`, `username`, `password`, `source` columns

### Warming from File

```python
# Warm cache from JSONL file
result = manager.warm_from_file(
    file_path="proxies.jsonl",
    ttl_override=7200,  # optional: override default TTL
)

print(f"Loaded: {result['loaded']}")
print(f"Skipped: {result['skipped']}")
print(f"Failed: {result['failed']}")
```

**Example JSONL format:**

```json
{"proxy_url": "http://proxy1.example.com:8080", "source": "warmed"}
{"proxy_url": "http://user:pass@proxy2.example.com:8080", "source": "warmed"}
{"proxy_url": "http://proxy3.example.com:8080", "username": "user", "password": "pass", "source": "warmed"}
```

**Example CSV format:**

```text
proxy_url,username,password,source
http://proxy1.example.com:8080,,,warmed
http://proxy2.example.com:8080,user,pass,warmed
```

```{tip}
Use `warm_from_file()` with large proxy lists to bypass slow fetch operations during application startup.
```

## Performance Tuning

### Tier Sizing Recommendations

**Low-memory environments** (serverless, containers):

```python
config = CacheConfig(
    l1_config=CacheTierConfig(max_entries=100),
    l2_config=CacheTierConfig(enabled=False),  # disable L2
    l3_config=CacheTierConfig(max_entries=None),
)
```

**High-throughput applications** (web scrapers, load balancers):

```python
config = CacheConfig(
    l1_config=CacheTierConfig(max_entries=10000),
    l2_config=CacheTierConfig(max_entries=50000),
    l3_config=CacheTierConfig(max_entries=None),
    enable_background_cleanup=True,
)
```

**Read-heavy workloads**:

```python
config = CacheConfig(
    l1_config=CacheTierConfig(max_entries=5000),  # larger L1
    l2_config=CacheTierConfig(enabled=False),     # skip L2
    l3_config=CacheTierConfig(max_entries=None),
)
```

### Eviction Policy Selection

```{list-table}
:header-rows: 1
:widths: 15 25 30 30

* - Policy
  - Best For
  - Pros
  - Cons
* - `lru`
  - General-purpose, time-sensitive data
  - Simple, fast, predictable
  - Ignores frequency
* - `lfu`
  - Frequently-accessed data
  - Optimizes for hot entries
  - Requires frequency tracking
* - `fifo`
  - Sequential access patterns
  - Zero overhead
  - No recency/frequency awareness
```

```{tip}
For most use cases, **LRU** (Least Recently Used) provides the best balance of simplicity and performance.
```

### Performance Characteristics

**Operation Latencies** (approximate):

| Operation | L1 | L2 | L3 |
|-----------|----|----|---|
| `get()` | ~100 ns | ~1-10 ms | ~5-50 ms |
| `put()` | ~200 ns | ~2-20 ms | ~10-100 ms |
| `delete()` | ~100 ns | ~2-10 ms | ~5-50 ms |
| `cleanup_expired()` | ~1 µs/entry | ~1 µs (SQL DELETE) | ~1 µs (SQL DELETE) |

**Memory Usage** (approximate):

- **L1**: ~500 bytes per entry (Python object overhead)
- **L2**: ~400 bytes per entry (SQLite storage in `l2_cache.db`)
- **L3**: ~450 bytes per entry (SQLite storage with health fields)

```{warning}
Large L1 caches (>10,000 entries) may trigger Python garbage collection pauses. Monitor GC stats with `import gc; gc.get_stats()`.
```

### Graceful Degradation

If a tier fails repeatedly (e.g., disk full, database locked), it auto-disables after 3 consecutive failures:

```python
# L2 disk full → tier disabled
manager.put(key, entry)
# L1 and L3 still work

stats = manager.get_statistics()
if stats.l2_degraded:
    print("WARNING: L2 tier degraded, running on L1+L3 only")
```

Tiers automatically re-enable after a successful operation.

## CLI Integration

The CLI exposes cache configuration via TOML config file:

```toml
# ~/.config/proxywhirl/config.toml
cache_enabled = true
cache_l1_max_entries = 1000
cache_l2_max_entries = 5000
cache_l3_max_entries = 0  # 0 = unlimited
cache_default_ttl = 3600
cache_cleanup_interval = 60
cache_l2_dir = ".cache/proxies"
cache_l3_db_path = ".cache/db/proxywhirl.db"
cache_encryption_key_env = "PROXYWHIRL_CACHE_ENCRYPTION_KEY"
cache_health_invalidation = true
cache_failure_threshold = 3
```

## Best Practices

### Security

1. **Always encrypt credentials**: Set `PROXYWHIRL_CACHE_ENCRYPTION_KEY` in production
2. **Rotate encryption keys**: Re-encrypt cache data periodically
3. **Restrict file permissions**: L2 cache directory should be mode 0700 (owner-only)
4. **Use SecretStr**: Never log or serialize credentials directly

### Performance

1. **Size L1 appropriately**: Too large → GC pauses, too small → excessive L2/L3 access
2. **Enable background cleanup**: For write-heavy workloads with short TTLs
3. **Disable unused tiers**: If you don't need L2, disable it to reduce I/O
4. **Monitor hit rates**: Aim for >80% overall hit rate

### Reliability

1. **Handle degraded tiers**: Check `CacheStatistics.l{1,2,3}_degraded` in metrics
2. **Monitor eviction reasons**: High `evictions_health` → upstream proxy issues
3. **Test encryption key recovery**: Ensure you can restore from backups
4. **Use per-source TTLs**: Premium sources can have longer TTLs

## Example: Complete Cache Setup

```python
import os
from proxywhirl.cache import CacheManager, CacheConfig, CacheTierConfig, CacheEntry, HealthStatus
from pydantic import SecretStr
from datetime import datetime, timezone, timedelta

# 1. Configure cache
config = CacheConfig(
    # Tier configuration
    l1_config=CacheTierConfig(max_entries=1000, eviction_policy="lru"),
    l2_config=CacheTierConfig(max_entries=5000, eviction_policy="lru"),
    l3_config=CacheTierConfig(max_entries=None, eviction_policy="lru"),

    # TTL configuration
    default_ttl_seconds=3600,
    enable_background_cleanup=True,
    cleanup_interval_seconds=60,
    per_source_ttl={
        "premium": 7200,
        "free": 1800,
    },

    # Storage paths
    l2_cache_dir=".cache/proxies",           # L2 SQLite: .cache/proxies/l2_cache.db
    l3_database_path=".cache/db/proxywhirl.db",  # L3 SQLite main database

    # Encryption
    encryption_key=SecretStr(os.environ.get("PROXYWHIRL_CACHE_ENCRYPTION_KEY", "")),

    # Health integration
    health_check_invalidation=True,
    failure_threshold=3,
)

# 2. Initialize manager
manager = CacheManager(config)

# 3. Warm cache from file
result = manager.warm_from_file("proxies.jsonl", ttl_override=7200)
print(f"Warmed cache: {result['loaded']} entries")

# 4. Add new proxy
entry = CacheEntry(
    key=CacheManager.generate_cache_key("http://proxy.example.com:8080"),
    proxy_url="http://proxy.example.com:8080",
    username=SecretStr("user"),
    password=SecretStr("pass"),
    source="premium",
    fetch_time=datetime.now(timezone.utc),
    ttl_seconds=7200,  # 2 hours
    expires_at=datetime.now(timezone.utc) + timedelta(hours=2),
    health_status=HealthStatus.HEALTHY,
    access_count=0,
    last_accessed=datetime.now(timezone.utc),
)
manager.put(entry.key, entry)

# 5. Retrieve proxy (with tier promotion)
retrieved = manager.get(entry.key)
if retrieved and not retrieved.is_expired:
    print(f"Retrieved proxy: {retrieved.proxy_url}")
    print(f"Access count: {retrieved.access_count}")

# 6. Invalidate unhealthy proxy
manager.invalidate_by_health(entry.key)

# 7. Monitor statistics
stats = manager.get_statistics()
print(f"Overall hit rate: {stats.overall_hit_rate:.2%}")
print(f"Total size: {stats.total_size} entries")
print(f"Promotions: {stats.promotions}, Demotions: {stats.demotions}")

# 8. Export metrics
metrics = stats.to_metrics_dict()
# Send to monitoring system (Prometheus, Datadog, etc.)
```

## Troubleshooting

### Low Hit Rates

**Symptom**: `overall_hit_rate < 0.5`

**Solutions**:
- Increase L1 capacity
- Increase TTL for stable sources
- Enable background cleanup to prevent expired entries from polluting cache
- Warm cache at startup

### High Memory Usage

**Symptom**: Python process RSS > expected

**Solutions**:
- Reduce L1 `max_entries`
- Disable L2 tier and rely on L1+L3 only
- Monitor with `gc.get_stats()` and adjust eviction policy

### Encryption Errors

**Symptom**: `ValueError: Decryption failed`

**Solutions**:
- Verify `PROXYWHIRL_CACHE_ENCRYPTION_KEY` is set correctly
- Check if encryption key changed (requires cache clear)
- Inspect L2/L3 files for corruption

### Tier Degradation

**Symptom**: `l2_degraded=True` or `l3_degraded=True`

**Solutions**:
- Check disk space for L2 cache directory
- Check file permissions (should be 0700)
- Verify SQLite database is not locked by another process
- Review logs for tier-specific errors

## See Also

- {doc}`/reference/index` - API reference for `CacheManager`, `CacheEntry`, `CacheConfig`
- {doc}`/guides/automation` - CI/CD integration for cache monitoring
- {doc}`/getting-started/index` - QuickStart for basic ProxyWhirl usage
