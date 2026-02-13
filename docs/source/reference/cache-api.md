# Cache API Reference

Complete reference for ProxyWhirl's multi-tier caching system with L1 (memory), L2 (disk), and L3 (SQLite) support.

:::{seealso}
For cache configuration patterns and optimization tips, see [Caching](../guides/caching.md). For TOML cache configuration options, see [Configuration](configuration.md).
:::

```python
from proxywhirl.cache import (
    CacheManager,
    CacheConfig,
    CacheEntry,
    HealthStatus,
    CacheTierType,
    MemoryCacheTier,
    DiskCacheTier,
    SQLiteCacheTier,
    CredentialEncryptor,
)

# L2BackendType and JsonlCacheTier are available via submodule imports:
from proxywhirl.cache.models import L2BackendType
from proxywhirl.cache.tiers import JsonlCacheTier
```

## Overview

The cache subsystem provides three-tier storage for proxies with automatic promotion, credential encryption, TTL management, and health-based invalidation. It supports graceful degradation when tiers fail and provides comprehensive statistics for monitoring.

**Architecture:**
- **L1 (Memory)**: Fast in-memory cache using OrderedDict with LRU eviction
- **L2 (Disk)**: Configurable persistent cache with two backend options:
  - **JSONL** (default): File-based using sharded JSON Lines files, human-readable, portable, best for <10K entries
  - **SQLite**: Database-based with indexed lookups, faster for >10K entries with O(log n) performance
- **L3 (SQLite)**: Full database cache with SQL indexing, health history tracking, and complete queryability

## Data Models

### CacheEntry

Container for a single cached proxy with metadata, TTL, and health tracking.

```{eval-rst}
.. py:class:: CacheEntry

   Pydantic model that stores proxy information with TTL, health status, and access tracking.
   Credentials are SecretStr in memory, encrypted at rest in L2/L3.

   **Example:**

   .. code-block:: python

      from proxywhirl.cache import CacheEntry, HealthStatus
      from datetime import datetime, timezone, timedelta
      from pydantic import SecretStr

      entry = CacheEntry(
          key="abc123",
          proxy_url="http://proxy.example.com:8080",
          username=SecretStr("user"),
          password=SecretStr("pass"),
          source="api",
          fetch_time=datetime.now(timezone.utc),
          last_accessed=datetime.now(timezone.utc),
          ttl_seconds=3600,
          expires_at=datetime.now(timezone.utc) + timedelta(seconds=3600),
          health_status=HealthStatus.HEALTHY
      )

      # Check expiration
      if entry.is_expired:
          print("Entry has expired")

      # Check health
      if entry.is_healthy:
          print("Proxy is healthy")
```

#### Fields

**Identity:**
- `key` (str): Unique cache key (proxy URL hash)
- `proxy_url` (str): Full proxy URL (scheme://host:port)

**Credentials (encrypted at rest in L2/L3):**
- `username` (SecretStr | None): Proxy username
- `password` (SecretStr | None): Proxy password

**Metadata:**
- `source` (str): Proxy source identifier
- `fetch_time` (datetime): When proxy was fetched
- `last_accessed` (datetime): Last cache access time
- `access_count` (int): Number of cache hits (default: 0)

**TTL & Health:**
- `ttl_seconds` (int): Time-to-live in seconds (≥0)
- `expires_at` (datetime): Absolute expiration time
- `health_status` (HealthStatus): Current health status (default: UNKNOWN)
- `failure_count` (int): Consecutive failures (≥0, default: 0)
- `evicted_from_l1` (bool): Whether entry was evicted from L1 cache (default: False)

**Health Monitoring (Feature 006):**
- `last_health_check` (datetime | None): Last health check timestamp
- `consecutive_health_failures` (int): Consecutive health check failures (≥0, default: 0)
- `consecutive_health_successes` (int): Consecutive successful health checks (≥0, default: 0)
- `recovery_attempt` (int): Current recovery attempt count (≥0, default: 0)
- `next_check_time` (datetime | None): Scheduled next health check
- `last_health_error` (str | None): Last health check error message
- `total_health_checks` (int): Total health checks performed (≥0, default: 0)
- `total_health_check_failures` (int): Total health check failures (≥0, default: 0)

#### Properties

```{eval-rst}
.. py:property:: is_expired
   :type: bool

   Check if entry has expired based on TTL.

   :returns: True if current time ≥ expires_at, False otherwise
```

```{eval-rst}
.. py:property:: is_healthy
   :type: bool

   Check if proxy is healthy enough to use.

   :returns: True if health_status == HEALTHY, False otherwise
```

---

### CacheConfig

Configuration for cache behavior and tier settings.

```{eval-rst}
.. py:class:: CacheConfig

   Pydantic model that aggregates configuration for all three tiers plus global settings
   like TTL, cleanup intervals, and storage paths.

   **Example:**

   .. code-block:: python

      from proxywhirl.cache import CacheConfig, CacheTierConfig, L2BackendType
      from pydantic import SecretStr

      # Default JSONL backend (file-based, portable)
      config = CacheConfig(
          # Tier configurations
          l1_config=CacheTierConfig(
              enabled=True,
              max_entries=1000,
              eviction_policy="lru"
          ),
          l2_config=CacheTierConfig(
              enabled=True,
              max_entries=5000,
              eviction_policy="lru"
          ),
          l2_backend=L2BackendType.JSONL,  # or L2BackendType.SQLITE for large caches
          l3_config=CacheTierConfig(
              enabled=True,
              max_entries=None,  # Unlimited
              eviction_policy="lru"
          ),

          # TTL Configuration
          default_ttl_seconds=3600,
          ttl_cleanup_interval=60,
          enable_background_cleanup=True,
          cleanup_interval_seconds=60,
          per_source_ttl={
              "api": 7200,      # API sources: 2 hours
              "scraper": 1800   # Scrapers: 30 minutes
          },

          # Storage Paths
          l2_cache_dir=".cache/proxies",
          l3_database_path=".cache/db/proxywhirl.db",

          # Encryption
          encryption_key=SecretStr("your-32-byte-url-safe-base64-key"),

          # Health Integration
          health_check_invalidation=True,
          failure_threshold=3,

          # Performance Tuning
          enable_statistics=True,
          statistics_interval=5
      )

      # SQLite backend for large caches (>10K entries)
      large_cache_config = CacheConfig(
          l2_backend=L2BackendType.SQLITE,
          l2_config=CacheTierConfig(max_entries=50000)
      )
```

#### Fields

**Tier Configuration:**
- `l1_config` (CacheTierConfig): L1 (Memory) configuration (default: max_entries=1000)
- `l2_config` (CacheTierConfig): L2 (Disk) configuration (default: max_entries=5000)
- `l2_backend` (L2BackendType): L2 storage backend - "jsonl" or "sqlite" (default: JSONL)
- `l3_config` (CacheTierConfig): L3 (SQLite) configuration (default: max_entries=None)

**TTL Configuration:**
- `default_ttl_seconds` (int): Default TTL for cached proxies (≥60, default: 3600)
- `ttl_cleanup_interval` (int): Background cleanup interval (≥10, default: 60)
- `enable_background_cleanup` (bool): Enable background TTL cleanup thread (default: False)
- `cleanup_interval_seconds` (int): Interval between cleanup runs (≥5, default: 60)
- `per_source_ttl` (dict[str, int]): Per-source TTL overrides (default: empty dict)

**Storage Paths:**
- `l2_cache_dir` (str): Directory for L2 cache (JSONL shards or SQLite database) (default: ".cache/proxies")
- `l3_database_path` (str): SQLite database path for L3 (default: ".cache/db/proxywhirl.db")

**Encryption:**
- `encryption_key` (SecretStr | None): Fernet encryption key (from env: PROXYWHIRL_CACHE_ENCRYPTION_KEY)

**Health Integration:**
- `health_check_invalidation` (bool): Auto-invalidate on health check failure (default: True)
- `failure_threshold` (int): Failures before health invalidation (≥1, default: 3)

**Performance Tuning:**
- `enable_statistics` (bool): Track cache statistics (default: True)
- `statistics_interval` (int): Stats aggregation interval (≥1, default: 5)

---

### CacheTierConfig

Configuration for a single cache tier.

```{eval-rst}
.. py:class:: CacheTierConfig

   Pydantic model that defines capacity, eviction policy, and enable/disable state for
   one tier (L1, L2, or L3).

   **Example:**

   .. code-block:: python

      from proxywhirl.cache import CacheTierConfig

      config = CacheTierConfig(
          enabled=True,
          max_entries=1000,
          eviction_policy="lru"  # "lru", "lfu", or "fifo"
      )
```

#### Fields

- `enabled` (bool): Enable this tier (default: True)
- `max_entries` (int | None): Max entries (None=unlimited, default: None)
- `eviction_policy` (str): Eviction policy: "lru", "lfu", or "fifo" (default: "lru")

#### Validators

```{eval-rst}
.. py:method:: validate_policy(v: str) -> str
   :classmethod:

   Validate eviction policy is supported.

   :param v: Policy name to validate
   :raises ValueError: If policy is not one of ["lru", "lfu", "fifo"]
   :returns: Validated policy name
```

---

### CacheStatistics

Aggregate cache statistics across all tiers.

```{eval-rst}
.. py:class:: CacheStatistics

   Pydantic model that combines tier-level statistics and tracks cross-tier operations
   like promotions and demotions.

   **Example:**

   .. code-block:: python

      from proxywhirl.cache import CacheStatistics

      stats = CacheStatistics()
      stats.l1_stats.hits = 100
      stats.l1_stats.misses = 20

      print(f"L1 hit rate: {stats.l1_stats.hit_rate:.2%}")
      print(f"Overall hit rate: {stats.overall_hit_rate:.2%}")
      print(f"Total size: {stats.total_size}")

      # Export to monitoring
      metrics = stats.to_metrics_dict()
```

#### Fields

**Per-Tier Statistics:**
- `l1_stats` (TierStatistics): L1 statistics (default: empty TierStatistics)
- `l2_stats` (TierStatistics): L2 statistics (default: empty TierStatistics)
- `l3_stats` (TierStatistics): L3 statistics (default: empty TierStatistics)

**Cross-Tier Operations:**
- `promotions` (int): L3→L2→L1 promotions (≥0, default: 0)
- `demotions` (int): L1→L2→L3 demotions (≥0, default: 0)

**Degradation Tracking:**
- `l1_degraded` (bool): L1 tier unavailable (default: False)
- `l2_degraded` (bool): L2 tier unavailable (default: False)
- `l3_degraded` (bool): L3 tier unavailable (default: False)

#### Computed Properties

```{eval-rst}
.. py:property:: overall_hit_rate
   :type: float

   Overall hit rate across all tiers (0.0 to 1.0).

   Uses max of per-tier misses to avoid triple-counting misses that cascade
   through L1→L2→L3 lookups.
```

```{eval-rst}
.. py:property:: total_size
   :type: int

   Total cached entries across all tiers.
```

#### Methods

```{eval-rst}
.. py:method:: to_metrics_dict() -> dict[str, float]

   Convert to flat metrics dict for monitoring systems.

   :returns: Dictionary with metric names and float values

   **Example:**

   .. code-block:: python

      metrics = stats.to_metrics_dict()
      # {
      #     "cache.l1.hit_rate": 0.85,
      #     "cache.l2.hit_rate": 0.60,
      #     "cache.l3.hit_rate": 0.40,
      #     "cache.overall.hit_rate": 0.75,
      #     "cache.total_size": 1500.0,
      #     "cache.promotions": 250.0,
      #     "cache.demotions": 150.0,
      #     "cache.l1.size": 1000.0,
      #     "cache.l2.size": 450.0,
      #     "cache.l3.size": 50.0
      # }
```

---

### TierStatistics

Statistics for a single cache tier.

```{eval-rst}
.. py:class:: TierStatistics

   Pydantic model that tracks hits, misses, evictions by reason, and computes hit rate.

   **Example:**

   .. code-block:: python

      from proxywhirl.cache import TierStatistics

      stats = TierStatistics(hits=100, misses=20)
      print(f"Hit rate: {stats.hit_rate:.2%}")  # 83.33%
      print(f"Total evictions: {stats.total_evictions}")
```

#### Fields

- `hits` (int): Cache hits (≥0, default: 0)
- `misses` (int): Cache misses (≥0, default: 0)
- `current_size` (int): Current number of entries (≥0, default: 0)
- `evictions_lru` (int): LRU evictions (≥0, default: 0)
- `evictions_ttl` (int): TTL-based evictions (≥0, default: 0)
- `evictions_health` (int): Health-based evictions (≥0, default: 0)
- `evictions_corruption` (int): Corruption-based evictions (≥0, default: 0)

#### Computed Properties

```{eval-rst}
.. py:property:: hit_rate
   :type: float

   Cache hit rate (0.0 to 1.0).

   :formula: hits / (hits + misses) if total > 0, else 0.0
```

```{eval-rst}
.. py:property:: total_evictions
   :type: int

   Total evictions across all reasons.

   :formula: evictions_lru + evictions_ttl + evictions_health + evictions_corruption
```

---

### HealthStatus (Enum)

Proxy health status for cache entries (imported from `proxywhirl.models`).

```{eval-rst}
.. py:class:: HealthStatus

   String enum representing proxy health status with 5 states.

   **Values:**

   - ``UNKNOWN = "unknown"`` - Not yet tested (default)
   - ``HEALTHY = "healthy"`` - Working normally
   - ``DEGRADED = "degraded"`` - Partial functionality (some failures)
   - ``UNHEALTHY = "unhealthy"`` - Experiencing issues (many failures)
   - ``DEAD = "dead"`` - Not responding (completely unusable)

   **Example:**

   .. code-block:: python

      from proxywhirl.cache import HealthStatus

      status = HealthStatus.HEALTHY
      print(status.value)  # "healthy"

      # All 5 states are available
      for state in HealthStatus:
          print(f"{state.name}: {state.value}")
```

---

### CacheTierType (Enum)

Type of cache tier.

```{eval-rst}
.. py:class:: CacheTierType

   String enum representing cache tier types.

   **Values:**

   - ``L1 = "l1"`` - Memory tier
   - ``L2 = "l2"`` - Disk tier
   - ``L3 = "l3"`` - SQLite tier

   **Example:**

   .. code-block:: python

      from proxywhirl.cache import CacheTierType

      tier = CacheTierType.L1
      print(tier.value)  # "l1"
```

---

### L2BackendType (Enum)

L2 cache backend type selection.

```{eval-rst}
.. py:class:: L2BackendType

   String enum for selecting the L2 disk cache storage backend.

   **Values:**

   - ``JSONL = "jsonl"`` - File-based JSONL with sharding (default, best for <10K entries)
   - ``SQLITE = "sqlite"`` - SQLite database (faster for >10K entries)

   **Example:**

   .. code-block:: python

      from proxywhirl.cache import CacheConfig, L2BackendType

      # Default JSONL backend
      config = CacheConfig()
      assert config.l2_backend == L2BackendType.JSONL

      # SQLite backend for large caches
      config = CacheConfig(l2_backend=L2BackendType.SQLITE)
```

**When to use each backend:**

| Backend | Best For | Performance | Features |
|---------|----------|-------------|----------|
| JSONL | <10K entries | O(n) lookups | Human-readable, portable, simple debugging |
| SQLite | >10K entries | O(log n) lookups | Indexed queries, faster batch operations |

---

## Tier Implementations

### CacheTier (Abstract Base Class)

Abstract base class for cache tier implementations.

```{eval-rst}
.. py:class:: CacheTier

   Defines the interface that all cache tiers (L1, L2, L3) must implement,
   including graceful degradation on repeated failures.

   **Attributes:**

   - ``config`` (CacheTierConfig) - Configuration for this tier
   - ``tier_type`` (TierType) - Type of tier (L1/L2/L3)
   - ``enabled`` (bool) - Whether tier is operational
   - ``failure_count`` (int) - Consecutive failures for degradation tracking
   - ``failure_threshold`` (int) - Failures before auto-disabling tier (default: 3)
```

#### Constructor

```{eval-rst}
.. py:method:: __init__(config: CacheTierConfig, tier_type: TierType) -> None

   Initialize cache tier with configuration.

   :param config: Configuration for this tier
   :param tier_type: Type of tier (L1/L2/L3)
```

#### Abstract Methods

```{eval-rst}
.. py:method:: get(key: str) -> Optional[CacheEntry]
   :abstractmethod:

   Retrieve entry by key, None if not found or expired.

   :param key: Cache key to lookup
   :returns: CacheEntry if found and valid, None otherwise
```

```{eval-rst}
.. py:method:: put(key: str, entry: CacheEntry) -> bool
   :abstractmethod:

   Store entry, return True if successful.

   :param key: Cache key for entry
   :param entry: CacheEntry to store
   :returns: True if stored successfully, False otherwise
```

```{eval-rst}
.. py:method:: delete(key: str) -> bool
   :abstractmethod:

   Remove entry by key, return True if existed.

   :param key: Cache key to delete
   :returns: True if entry existed and was deleted, False if not found
```

```{eval-rst}
.. py:method:: clear() -> int
   :abstractmethod:

   Clear all entries, return count of removed entries.

   :returns: Number of entries removed
```

```{eval-rst}
.. py:method:: size() -> int
   :abstractmethod:

   Return current number of entries.

   :returns: Number of entries in tier
```

```{eval-rst}
.. py:method:: keys() -> list[str]
   :abstractmethod:

   Return list of all keys.

   :returns: List of cache keys
```

```{eval-rst}
.. py:method:: cleanup_expired() -> int
   :abstractmethod:

   Remove all expired entries in bulk.

   :returns: Number of entries removed
```

#### Concrete Methods

```{eval-rst}
.. py:method:: handle_failure(error: Exception) -> None

   Handle tier operation failure for graceful degradation.

   Increments failure count and disables tier if threshold exceeded.
   Called by implementations when operations fail.

   :param error: Exception that occurred
```

```{eval-rst}
.. py:method:: reset_failures() -> None

   Reset failure count on successful operation.

   Re-enables tier if previously disabled and resets failure counter.
   Implementations should call this after successful operations.
```

---

### MemoryCacheTier

L1 in-memory cache using OrderedDict for LRU tracking.

```{eval-rst}
.. py:class:: MemoryCacheTier(CacheTier)

   Provides O(1) lookups with automatic LRU eviction when max_entries exceeded.

   **Example:**

   .. code-block:: python

      from proxywhirl.cache.tiers import MemoryCacheTier, TierType
      from proxywhirl.cache import CacheTierConfig

      config = CacheTierConfig(max_entries=1000, eviction_policy="lru")
      tier = MemoryCacheTier(config, TierType.L1_MEMORY)

      # Store entry
      tier.put(key, entry)

      # Retrieve entry (moves to end for LRU)
      cached = tier.get(key)

      # Delete entry
      deleted = tier.delete(key)

      # Get all keys
      keys = tier.keys()

      # Get size
      size = tier.size()

      # Clear all
      cleared = tier.clear()

      # Cleanup expired
      removed = tier.cleanup_expired()
```

#### Constructor

```{eval-rst}
.. py:method:: __init__(config: CacheTierConfig, tier_type: TierType, on_evict: Optional[Callable[[str, CacheEntry], None]] = None) -> None
   :noindex:

   Initialize memory cache with LRU tracking.

   :param config: Tier configuration
   :param tier_type: Type of tier (L1/L2/L3)
   :param on_evict: Optional callback when entry is evicted (key, entry)
```

#### Features

- O(1) lookups
- Automatic LRU eviction when max_entries exceeded
- Thread-safe with failure tracking
- No persistence
- Callbacks on eviction for demotion to L2

---

### JsonlCacheTier

L2 file-based cache using sharded JSONL files with encryption.

```{eval-rst}
.. py:class:: JsonlCacheTier(CacheTier)

   File-based cache tier using JSON Lines format with consistent-hash sharding.
   Best for <10K entries. Human-readable, portable, and git-friendly.

   Uses sharded JSONL files with:

   - Consistent hash sharding (default 16 shards)
   - In-memory index for O(1) key→shard lookups
   - File locking (portalocker) for concurrent access safety
   - Fernet encryption for credentials at rest
   - Human-readable JSON Lines format

   **Example:**

   .. code-block:: python

      from proxywhirl.cache.tiers import JsonlCacheTier, TierType
      from proxywhirl.cache import CacheTierConfig, CredentialEncryptor
      from pathlib import Path

      config = CacheTierConfig(max_entries=5000, eviction_policy="lru")
      encryptor = CredentialEncryptor()
      cache_dir = Path(".cache/proxies")

      tier = JsonlCacheTier(
          config=config,
          tier_type=TierType.L2_FILE,
          cache_dir=cache_dir,
          encryptor=encryptor,
          num_shards=16  # Default
      )

      # Store entry (writes to appropriate shard file)
      tier.put(key, entry)

      # Retrieve entry (uses in-memory index for O(1) shard lookup)
      cached = tier.get(key)

      # Delete entry
      deleted = tier.delete(key)

      # Get all keys (from index)
      keys = tier.keys()

      # Get size
      size = tier.size()

      # Clear all (removes all shard files)
      cleared = tier.clear()

      # Cleanup expired entries
      removed = tier.cleanup_expired()
```

#### Constructor

```{eval-rst}
.. py:method:: __init__(config: CacheTierConfig, tier_type: TierType, cache_dir: Path, encryptor: Optional[CredentialEncryptor] = None, num_shards: int = 16) -> None
   :noindex:

   Initialize JSONL file cache with sharding and encryption.

   :param config: Tier configuration
   :param tier_type: Type of tier (L1/L2/L3)
   :param cache_dir: Directory for shard files
   :param encryptor: Optional encryptor for credentials
   :param num_shards: Number of shard files (default: 16)
```

#### File Structure

```text
.cache/proxies/
├── shard_00.jsonl
├── shard_01.jsonl
├── ...
└── shard_15.jsonl
```

Each shard file contains JSON Lines entries:

```text
{"key": "abc123", "proxy_url": "http://proxy:8080", "source": "free-proxy-list", "ttl_seconds": 3600, ...}
{"key": "def456", "proxy_url": "socks5://proxy:1080", "source": "geonode", "ttl_seconds": 7200, ...}
```

#### Features

- Human-readable JSON Lines format
- Portable (can copy/move files)
- Git-friendly for version control
- Consistent-hash sharding for distribution
- In-memory index for fast lookups
- File locking for concurrent access
- Encrypted credentials at rest
- Best for <10K entries

#### When to Use JSONL vs SQLite

| Factor | JSONL (JsonlCacheTier) | SQLite (DiskCacheTier) |
|--------|------------------------|------------------------|
| Entry count | <10K entries | >10K entries |
| Lookup speed | O(n) per shard | O(log n) indexed |
| Portability | Copy files anywhere | Single .db file |
| Git-friendly | Yes | Not recommended |
| Human-readable | Yes | No (binary) |
| Concurrent writes | File locking | WAL mode |

---

### DiskCacheTier

L2 SQLite-based cache with encryption and indexed lookups.

```{eval-rst}
.. py:class:: DiskCacheTier(CacheTier)

   Optimized for >10K entries using SQLite with B-tree indexes instead of JSONL.
   Provides O(log n) lookups vs O(n) for JSONL, achieving <10ms reads for 10K+ entries.

   Uses a lightweight SQLite database with:

   - Primary key index on cache key for fast lookups
   - Encrypted credentials stored as BLOB
   - Efficient bulk operations (cleanup, size, keys)
   - File-based persistence without complex sharding

   **Example:**

   .. code-block:: python

      from proxywhirl.cache.tiers import DiskCacheTier, TierType
      from proxywhirl.cache import CacheTierConfig, CredentialEncryptor
      from pathlib import Path

      config = CacheTierConfig(max_entries=5000, eviction_policy="lru")
      encryptor = CredentialEncryptor()
      cache_dir = Path(".cache/proxies")

      tier = DiskCacheTier(config, TierType.L2_FILE, cache_dir, encryptor)

      # Same interface as MemoryCacheTier
      tier.put(key, entry)
      cached = tier.get(key)
```

#### Constructor

```{eval-rst}
.. py:method:: __init__(config: CacheTierConfig, tier_type: TierType, cache_dir: Path, encryptor: Optional[CredentialEncryptor] = None) -> None
   :noindex:

   Initialize SQLite-based L2 cache.

   :param config: Tier configuration
   :param tier_type: Type of tier (should be L2_FILE)
   :param cache_dir: Directory for cache database
   :param encryptor: Credential encryptor for username/password
```

#### Methods

```{eval-rst}
.. py:method:: migrate_from_jsonl(jsonl_dir: Optional[Path] = None) -> int

   Migrate existing JSONL shard files to SQLite L2 cache.

   This method provides a migration path from the old JSONL-based L2 cache
   to the new SQLite-based implementation. It reads all shard_*.jsonl files
   from the specified directory and imports them into the SQLite database.

   :param jsonl_dir: Directory containing shard_*.jsonl files (defaults to self.cache_dir)
   :returns: Number of entries successfully migrated

   **Example:**

   .. code-block:: python

      tier = DiskCacheTier(config, TierType.L2_FILE, cache_dir)
      migrated = tier.migrate_from_jsonl()
      print(f"Migrated {migrated} entries from JSONL to SQLite")
```

```{eval-rst}
.. py:method:: close() -> None

   Close the persistent SQLite connection and release database resources.

   Should be called when the cache tier is no longer needed to properly
   release database resources and file locks. Safe to call multiple times.
   Thread-safe via internal lock.

   **Example:**

   .. code-block:: python

      tier = DiskCacheTier(config, TierType.L2_FILE, cache_dir, encryptor)
      try:
          tier.put(key, entry)
          cached = tier.get(key)
      finally:
          tier.close()
```

#### Features

- O(log n) indexed lookups using SQLite B-tree
- Encrypted credential storage (BLOB fields)
- Atomic operations with SQLite transactions
- Efficient bulk cleanup using SQL DELETE
- Simple file-based persistence (single .db file)
- Automatic schema initialization

#### Database Schema

```sql
CREATE TABLE l2_cache (
    key TEXT PRIMARY KEY,
    proxy_url TEXT NOT NULL,
    username_encrypted BLOB,
    password_encrypted BLOB,
    source TEXT NOT NULL,
    fetch_time REAL NOT NULL,
    last_accessed REAL NOT NULL,
    access_count INTEGER DEFAULT 0,
    ttl_seconds INTEGER NOT NULL,
    expires_at REAL NOT NULL,
    health_status TEXT DEFAULT 'unknown',
    failure_count INTEGER DEFAULT 0,
    evicted_from_l1 INTEGER DEFAULT 0
);

CREATE INDEX idx_l2_expires_at ON l2_cache(expires_at);
CREATE INDEX idx_l2_source ON l2_cache(source);
```

---

### SQLiteCacheTier

L3 SQLite database cache with encrypted credentials and health history.

```{eval-rst}
.. py:class:: SQLiteCacheTier(CacheTier)

   Provides durable persistence with SQL indexing for fast lookups and comprehensive
   health history tracking.

   **Example:**

   .. code-block:: python

      from proxywhirl.cache.tiers import SQLiteCacheTier, TierType
      from proxywhirl.cache import CacheTierConfig, CredentialEncryptor
      from pathlib import Path

      config = CacheTierConfig(max_entries=None, eviction_policy="lru")  # Unlimited
      encryptor = CredentialEncryptor()
      db_path = Path(".cache/db/proxywhirl.db")

      tier = SQLiteCacheTier(config, TierType.L3_SQLITE, db_path, encryptor)

      # Same interface as other tiers
      tier.put(key, entry)
      cached = tier.get(key)

      # Optimized bulk cleanup with SQL DELETE
      removed = tier.cleanup_expired()  # O(1) instead of O(n)
```

#### Constructor

```{eval-rst}
.. py:method:: __init__(config: CacheTierConfig, tier_type: TierType, db_path: Path, encryptor: Optional[CredentialEncryptor] = None) -> None
   :noindex:

   Initialize SQLite cache.

   :param config: Tier configuration
   :param tier_type: Type of tier (should be L3_SQLITE)
   :param db_path: Path to SQLite database file
   :param encryptor: Credential encryptor for username/password
```

#### Features

- Full persistence
- SQL indexing for fast lookups
- Health history tracking with separate table
- Automatic schema migration
- Optimized bulk cleanup (O(1) using SQL DELETE)
- Credential encryption with BLOB storage
- Foreign key constraints

#### Database Schema

```sql
CREATE TABLE cache_entries (
    key TEXT PRIMARY KEY,
    proxy_url TEXT NOT NULL,
    username_encrypted BLOB,
    password_encrypted BLOB,
    source TEXT NOT NULL,
    fetch_time REAL NOT NULL,
    last_accessed REAL NOT NULL,
    access_count INTEGER DEFAULT 0,
    ttl_seconds INTEGER NOT NULL,
    expires_at REAL NOT NULL,
    health_status TEXT DEFAULT 'unknown',
    failure_count INTEGER DEFAULT 0,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL,
    -- Health monitoring fields
    last_health_check REAL,
    consecutive_health_failures INTEGER DEFAULT 0,
    consecutive_health_successes INTEGER DEFAULT 0,
    recovery_attempt INTEGER DEFAULT 0,
    next_check_time REAL,
    last_health_error TEXT,
    total_health_checks INTEGER DEFAULT 0,
    total_health_check_failures INTEGER DEFAULT 0,
    evicted_from_l1 INTEGER DEFAULT 0
);

CREATE TABLE health_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proxy_key TEXT NOT NULL,
    check_time REAL NOT NULL,
    status TEXT NOT NULL,
    response_time_ms REAL,
    error_message TEXT,
    check_url TEXT NOT NULL,
    FOREIGN KEY (proxy_key) REFERENCES cache_entries(key) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_expires_at ON cache_entries(expires_at);
CREATE INDEX idx_source ON cache_entries(source);
CREATE INDEX idx_health_status ON cache_entries(health_status);
CREATE INDEX idx_last_accessed ON cache_entries(last_accessed);
CREATE INDEX idx_health_history_proxy ON health_history(proxy_key);
CREATE INDEX idx_health_history_time ON health_history(check_time);
```

---

## Utilities

### CredentialEncryptor

:::{warning}
If no encryption key is provided and the `PROXYWHIRL_CACHE_ENCRYPTION_KEY` environment variable is not set, a new key is generated automatically. This means cached data encrypted with a previous key will be unreadable. Always persist your encryption key for production use.
:::

Handles encryption/decryption of proxy credentials using Fernet symmetric encryption (AES-128-CBC + HMAC). Supports **key rotation** via `MultiFernet`: set `PROXYWHIRL_CACHE_KEY_PREVIOUS` to the old key when rotating, allowing decryption of data encrypted with either key while new encryptions use the current key.

```{eval-rst}
.. py:class:: CredentialEncryptor

   Provides Fernet symmetric encryption for proxy credentials at rest (L2/L3 tiers).
   Uses environment variable PROXYWHIRL_CACHE_ENCRYPTION_KEY for key management.

   **Example:**

   .. code-block:: python

      from proxywhirl.cache import CredentialEncryptor
      from pydantic import SecretStr
      import os

      # Option 1: Use environment variable
      os.environ["PROXYWHIRL_CACHE_ENCRYPTION_KEY"] = "your-32-byte-url-safe-base64-key"
      encryptor = CredentialEncryptor()

      # Option 2: Provide key directly
      from cryptography.fernet import Fernet
      key = Fernet.generate_key()
      encryptor = CredentialEncryptor(key=key)

      # Encrypt credentials
      plaintext = SecretStr("mypassword")
      encrypted = encryptor.encrypt(plaintext)  # bytes

      # Decrypt credentials
      decrypted = encryptor.decrypt(encrypted)  # SecretStr
      print(decrypted.get_secret_value())  # "mypassword"
```

#### Constructor

```{eval-rst}
.. py:method:: __init__(key: Optional[bytes] = None) -> None
   :noindex:

   Initialize encryptor with Fernet key.

   :param key: Optional Fernet key (32 url-safe base64-encoded bytes).
               If None, reads from PROXYWHIRL_CACHE_ENCRYPTION_KEY env var.
               If env var not set, generates a new key (WARNING: regenerated keys
               cannot decrypt existing cached data).
   :raises ValueError: If provided key is invalid for Fernet

   **Attributes:**

   - ``key`` (bytes) - Fernet encryption key
   - ``_cipher`` (Fernet) - Fernet cipher instance
```

#### Methods

```{eval-rst}
.. py:method:: encrypt(secret: SecretStr) -> bytes

   Encrypt a SecretStr to bytes.

   :param secret: SecretStr containing plaintext to encrypt
   :returns: Encrypted bytes suitable for storage in BLOB fields
   :raises ValueError: If encryption fails

   **Example:**

   .. code-block:: python

      encrypted = encryptor.encrypt(SecretStr("password123"))
      # b'gAAAAA...'
```

```{eval-rst}
.. py:method:: decrypt(encrypted: bytes) -> SecretStr

   Decrypt encrypted bytes back to SecretStr.

   :param encrypted: Encrypted bytes from storage
   :returns: SecretStr containing decrypted plaintext (never logs value)
   :raises ValueError: If decryption fails (wrong key, corrupted data)

   **Example:**

   .. code-block:: python

      decrypted = encryptor.decrypt(encrypted_bytes)
      print(decrypted.get_secret_value())  # "password123"
```

---

### CacheManager

Main orchestrator for multi-tier proxy caching with automatic promotion/demotion, TTL management, and health-based invalidation.

```{eval-rst}
.. py:class:: CacheManager

   Manages caching across three tiers:

   - **L1 (Memory)**: Fast in-memory cache using OrderedDict (LRU)
   - **L2 (Disk)**: Persistent cache with configurable backend (JSONL or SQLite)
   - **L3 (SQLite)**: Database cache for cold storage with full queryability

   Supports TTL-based expiration, health-based invalidation, and graceful
   degradation when tiers fail. Thread-safe via ``threading.RLock``.

   **Example:**

   .. code-block:: python

      from proxywhirl.cache import CacheManager, CacheConfig, CacheEntry, HealthStatus
      from datetime import datetime, timezone, timedelta

      config = CacheConfig()
      manager = CacheManager(config)

      # Store an entry
      entry = CacheEntry(
          key="abc123",
          proxy_url="http://proxy.example.com:8080",
          source="api",
          fetch_time=datetime.now(timezone.utc),
          last_accessed=datetime.now(timezone.utc),
          ttl_seconds=3600,
          expires_at=datetime.now(timezone.utc) + timedelta(seconds=3600),
          health_status=HealthStatus.HEALTHY
      )
      manager.put(entry.key, entry)

      # Retrieve (promotes to higher tiers on hit)
      retrieved = manager.get(entry.key)

      # Delete from all tiers
      manager.delete(entry.key)

      # Statistics
      stats = manager.get_statistics()
      print(f"Overall hit rate: {stats.overall_hit_rate:.2%}")

      # Export/import
      manager.export_to_file("proxies.jsonl")
      manager.warm_from_file("proxies.jsonl", ttl_override=3600)
```

#### Constructor

```{eval-rst}
.. py:method:: __init__(config: CacheConfig) -> None
   :noindex:

   Initialize cache manager with configuration.

   :param config: Cache configuration with tier settings (required)

   Initializes L1 (memory), L2 (disk), and L3 (SQLite) tiers based on config.
   Starts background TTL cleanup if ``enable_background_cleanup`` is True.
```

#### Methods

```{eval-rst}
.. py:method:: get(key: str) -> CacheEntry | None
   :no-index:

   Retrieve entry from cache with tier promotion.

   Checks L1 → L2 → L3 in order. Promotes entries to higher tiers on hit.
   Updates ``access_count`` and ``last_accessed`` on successful retrieval.
   Expired entries are automatically deleted from all tiers.

   :param key: Cache key to retrieve
   :returns: CacheEntry if found and not expired, None otherwise

.. py:method:: put(key: str, entry: CacheEntry) -> bool
   :no-index:

   Store entry in all enabled tiers.

   Writes to all tiers for redundancy. Credentials are automatically
   redacted in logs.

   :param key: Cache key
   :param entry: CacheEntry to store
   :returns: True if stored in at least one tier, False otherwise

.. py:method:: delete(key: str) -> bool
   :no-index:

   Delete entry from all tiers.

   :param key: Cache key to delete
   :returns: True if deleted from at least one tier, False if not found

.. py:method:: clear() -> int
   :no-index:

   Clear all entries from all tiers.

   :returns: Total number of entries cleared

.. py:method:: invalidate_by_health(key: str) -> None

   Mark proxy as unhealthy and evict if failure threshold reached.

   Increments the ``failure_count`` and sets ``health_status`` to UNHEALTHY.
   If ``failure_count`` reaches the configured ``failure_threshold``, the proxy
   is removed from all cache tiers.

   :param key: Cache key to invalidate

.. py:method:: get_statistics() -> CacheStatistics

   Get current cache statistics.

   :returns: CacheStatistics with hit rates, sizes, and tier degradation status

.. py:method:: export_to_file(filepath: str) -> dict[str, int]

   Export all cache entries to a JSONL file.

   :param filepath: Path to export file
   :returns: Dict with ``exported`` and ``failed`` counts

.. py:method:: warm_from_file(file_path: str, ttl_override: int | None = None) -> dict[str, int]

   Load proxies from a file to pre-populate the cache.

   Supports JSON (array), JSONL (newline-delimited), and CSV formats.
   Invalid entries are skipped with warnings logged.

   :param file_path: Path to file containing proxy data
   :param ttl_override: Optional TTL in seconds (overrides ``default_ttl_seconds``)
   :returns: Dict with ``loaded``, ``skipped``, and ``failed`` counts

.. py:method:: generate_cache_key(proxy_url: str) -> str
   :staticmethod:

   Generate cache key from proxy URL using SHA256 hash.

   :param proxy_url: Proxy URL to hash
   :returns: Hex-encoded SHA256 hash (first 16 chars)
```

---

### Crypto Utilities

The `proxywhirl.cache.crypto` module provides helper functions for encryption key management and rotation.

```python
from proxywhirl.cache.crypto import get_encryption_keys, create_multi_fernet, rotate_key
```

#### `get_encryption_keys() -> list[bytes]`

Get all valid encryption keys for MultiFernet. Returns keys in priority order: current key first, then previous key. Reads from `PROXYWHIRL_CACHE_ENCRYPTION_KEY` and `PROXYWHIRL_CACHE_KEY_PREVIOUS` environment variables. Generates a new key if no env vars are set.

#### `create_multi_fernet() -> MultiFernet`

Create a `MultiFernet` instance with all valid encryption keys. MultiFernet tries keys in order for decryption (newest first). All new encryptions use the first (current) key.

#### `rotate_key(new_key: str) -> None`

Rotate encryption keys by setting a new current key. Moves the current `PROXYWHIRL_CACHE_ENCRYPTION_KEY` to `PROXYWHIRL_CACHE_KEY_PREVIOUS` and sets the new key as current. This allows gradual migration: new data uses the new key, old data can still be decrypted with the previous key.

```python
from cryptography.fernet import Fernet
from proxywhirl.cache.crypto import rotate_key

# Generate new key and rotate
new_key = Fernet.generate_key().decode()
rotate_key(new_key)
# Old data remains readable via PROXYWHIRL_CACHE_KEY_PREVIOUS
```

---

### TTLManager

Manages TTL-based expiration with hybrid lazy + background cleanup. Used internally by `CacheManager` when `enable_background_cleanup=True`.

```{eval-rst}
.. py:class:: TTLManager

   Combines two cleanup strategies:

   - **Lazy expiration**: Check TTL on every ``get()`` operation
   - **Background cleanup**: Periodic scan of all tiers to remove expired entries

   **Example:**

   .. code-block:: python

      from proxywhirl.cache.manager import TTLManager, CacheManager
      from proxywhirl.cache import CacheConfig

      config = CacheConfig(enable_background_cleanup=False)
      manager = CacheManager(config)

      # Manually create and start TTL manager
      ttl_mgr = TTLManager(manager, cleanup_interval=60)
      ttl_mgr.start()

      # ... later ...
      ttl_mgr.stop()
```

#### Constructor

```{eval-rst}
.. py:method:: __init__(cache_manager: CacheManager, cleanup_interval: int = 60) -> None
   :noindex:

   :param cache_manager: Parent CacheManager instance
   :param cleanup_interval: Seconds between cleanup runs (default: 60)
```

#### Methods

```{eval-rst}
.. py:method:: start() -> None

   Start background cleanup thread. Idempotent.

.. py:method:: stop() -> None

   Stop background cleanup thread. Safe to call if not running.
```

#### Attributes

- `enabled` (bool): Whether background cleanup is running
- `cleanup_interval` (int): Seconds between cleanup runs

---

## Usage Examples

### Working with Cache Tiers Directly

```python
from proxywhirl.cache.tiers import MemoryCacheTier, DiskCacheTier, SQLiteCacheTier, TierType
from proxywhirl.cache import CacheTierConfig, CacheEntry, CredentialEncryptor, HealthStatus
from datetime import datetime, timezone, timedelta
from pathlib import Path
from pydantic import SecretStr

# Initialize tiers
config = CacheTierConfig(max_entries=1000, eviction_policy="lru")
encryptor = CredentialEncryptor()

l1 = MemoryCacheTier(config, TierType.L1_MEMORY)
l2 = DiskCacheTier(config, TierType.L2_FILE, Path(".cache/l2"), encryptor)
l3 = SQLiteCacheTier(config, TierType.L3_SQLITE, Path(".cache/l3.db"), encryptor)

# Create entry
entry = CacheEntry(
    key="proxy1",
    proxy_url="http://proxy.example.com:8080",
    username=SecretStr("user"),
    password=SecretStr("pass"),
    source="api",
    fetch_time=datetime.now(timezone.utc),
    last_accessed=datetime.now(timezone.utc),
    ttl_seconds=3600,
    expires_at=datetime.now(timezone.utc) + timedelta(seconds=3600),
    health_status=HealthStatus.HEALTHY
)

# Store in L1
l1.put(entry.key, entry)

# Retrieve from L1 (O(1) lookup)
cached = l1.get(entry.key)
if cached:
    print(f"L1 hit: {cached.proxy_url}")

# Store in L2 (persisted to disk)
l2.put(entry.key, entry)

# Retrieve from L2 (O(log n) SQLite lookup)
cached = l2.get(entry.key)
if cached:
    print(f"L2 hit: {cached.proxy_url}")

# Store in L3 (full database persistence)
l3.put(entry.key, entry)

# Cleanup expired entries
removed_l1 = l1.cleanup_expired()
removed_l2 = l2.cleanup_expired()
removed_l3 = l3.cleanup_expired()
print(f"Removed: L1={removed_l1}, L2={removed_l2}, L3={removed_l3}")
```

---

### Encryption and Security

```python
from proxywhirl.cache import CredentialEncryptor
from cryptography.fernet import Fernet
from pydantic import SecretStr
import os

# Generate and save encryption key
key = Fernet.generate_key()
os.environ["PROXYWHIRL_CACHE_ENCRYPTION_KEY"] = key.decode()

# Initialize encryptor
encryptor = CredentialEncryptor()

# Encrypt credentials
username = SecretStr("admin")
password = SecretStr("secret123")

encrypted_user = encryptor.encrypt(username)
encrypted_pass = encryptor.encrypt(password)

print(f"Encrypted username: {encrypted_user.hex()}")
print(f"Encrypted password: {encrypted_pass.hex()}")

# Decrypt credentials
decrypted_user = encryptor.decrypt(encrypted_user)
decrypted_pass = encryptor.decrypt(encrypted_pass)

print(f"Decrypted: {decrypted_user.get_secret_value()}")  # "admin"
# Password value never logged by SecretStr
```

---

:::{tip}
If you have more than 10,000 cache entries, migrating from JSONL to SQLite L2 backend can significantly improve lookup performance (O(log n) vs O(n)).
:::

### Migration from JSONL to SQLite L2

```python
from proxywhirl.cache.tiers import DiskCacheTier, TierType
from proxywhirl.cache import CacheTierConfig, CredentialEncryptor
from pathlib import Path

# Initialize new SQLite-based L2 tier
config = CacheTierConfig(max_entries=5000)
encryptor = CredentialEncryptor()
cache_dir = Path(".cache/proxies")

tier = DiskCacheTier(config, TierType.L2_FILE, cache_dir, encryptor)

# Migrate from old JSONL shards
migrated = tier.migrate_from_jsonl()
print(f"Successfully migrated {migrated} entries from JSONL to SQLite")

# Old JSONL files can now be safely removed
# for shard in cache_dir.glob("shard_*.jsonl"):
#     shard.unlink()
```

---

## Performance Considerations

### Tier Selection

**L1 (Memory):**
- Fastest (O(1) lookup)
- Limited capacity (default: 1000 entries)
- Use for hot proxies

**L2 (Disk/SQLite):**
- Medium speed (O(log n) indexed lookup)
- Moderate capacity (default: 5000 entries)
- Persistent across restarts
- Use for warm proxies

**L3 (SQLite):**
- Slower (database overhead, but indexed)
- Unlimited capacity
- Full health history tracking
- Use for cold storage and analytics

### Optimization Tips

1. **Tune tier sizes** based on workload
2. **Enable background cleanup** to avoid lazy cleanup overhead
3. **Use encryption** for sensitive credentials in L2/L3
4. **Monitor failure rates** for graceful degradation
5. **Leverage indexes** in L2/L3 for fast queries

---

## Thread Safety

All tier implementations use internal locking for thread-safe operations. The `CacheTier` base class provides `handle_failure()` and `reset_failures()` methods for graceful degradation tracking.

---

## Error Handling

Tiers implement graceful degradation:
- After 3 consecutive failures, tier auto-disables (`enabled = False`)
- Successful operations reset failure counter
- Operations on disabled tiers return failure without attempting
- Parent cache manager can detect degraded tiers via tier.enabled

---

## See Also

- [Python API](python-api.md) -- Main ProxyRotator API (CacheManager, CacheConfig usage)
- [Configuration](configuration.md) -- TOML cache configuration options
- [Exceptions](exceptions.md) -- Cache-specific exceptions (CacheCorruptionError, CacheStorageError, CacheValidationError)
- [Rate Limiting API](rate-limiting-api.md) -- Rate limiting integration
- [Caching](../guides/caching.md) -- Cache configuration patterns and optimization
- [Deployment Security](../guides/deployment-security.md) -- Production cache security
- [Getting Started](../getting-started/index.md) -- Getting started guide
