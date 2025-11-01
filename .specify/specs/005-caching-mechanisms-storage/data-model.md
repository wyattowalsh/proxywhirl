# Data Model: Caching Mechanisms & Storage

**Feature**: 005-caching-mechanisms-storage  
**Date**: 2025-11-01  
**Phase**: 1 (Design & Contracts)

## Overview

This document defines the data structures, relationships, and validation rules for the three-tier caching system.

## Core Entities

### 1. CacheEntry

**Purpose**: Container for a single cached proxy with metadata

**Schema**:
```python
from pydantic import BaseModel, Field, SecretStr
from typing import Optional
from datetime import datetime
from enum import Enum

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class CacheEntry(BaseModel):
    # Identity
    key: str = Field(..., description="Unique cache key (proxy URL hash)")
    proxy_url: str = Field(..., description="Full proxy URL (scheme://host:port)")
    
    # Credentials (encrypted at rest in L2/L3, SecretStr in L1)
    username: Optional[SecretStr] = Field(None, description="Proxy username")
    password: Optional[SecretStr] = Field(None, description="Proxy password")
    
    # Metadata
    source: str = Field(..., description="Proxy source identifier")
    fetch_time: datetime = Field(..., description="When proxy was fetched")
    last_accessed: datetime = Field(..., description="Last cache access time")
    access_count: int = Field(default=0, description="Number of cache hits")
    
    # TTL & Health
    ttl_seconds: int = Field(..., ge=0, description="Time-to-live in seconds")
    expires_at: datetime = Field(..., description="Absolute expiration time")
    health_status: HealthStatus = Field(default=HealthStatus.UNKNOWN)
    failure_count: int = Field(default=0, ge=0, description="Consecutive failures")
    
    # Validation
    @property
    def is_expired(self) -> bool:
        """Check if entry has expired based on TTL"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) >= self.expires_at
    
    @property
    def is_healthy(self) -> bool:
        """Check if proxy is healthy enough to use"""
        return self.health_status == HealthStatus.HEALTHY
    
    class Config:
        json_encoders = {
            SecretStr: lambda v: "***",  # Never expose credentials in JSON
            datetime: lambda v: v.isoformat()
        }
```

**Relationships**:
- One CacheEntry per unique proxy URL
- Referenced by CacheKey in CacheTier implementations
- Associated with CacheStatistics via tier tracking

**State Transitions**:
```
[Fetched] → [Cached (L1)] → [Accessed] → [Accessed] → ...
                ↓
           [Expired] → [Evicted]
                ↓
         [Promoted to L2] → [Promoted to L1]
                ↓
         [Demoted to L3] → [Evicted permanently]
                ↓
         [Health Failed] → [Invalidated]
```

**Validation Rules**:
- `key` must be non-empty, URL-safe hash
- `proxy_url` must be valid URL (validated by Pydantic HttpUrl)
- `ttl_seconds` >= 0
- `expires_at` must be in the future for new entries
- `access_count` >= 0
- `failure_count` >= 0

---

### 2. CacheConfig

**Purpose**: Configuration for cache behavior and tier settings

**Schema**:
```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class CacheTierConfig(BaseModel):
    """Configuration for a single cache tier"""
    enabled: bool = Field(default=True, description="Enable this tier")
    max_entries: Optional[int] = Field(None, description="Max entries (None=unlimited)")
    eviction_policy: str = Field(default="lru", description="Eviction policy")
    
    @field_validator('eviction_policy')
    @classmethod
    def validate_policy(cls, v: str) -> str:
        allowed = ['lru', 'lfu', 'fifo']
        if v not in allowed:
            raise ValueError(f"Invalid eviction policy: {v}. Must be one of {allowed}")
        return v

class CacheConfig(BaseModel):
    # Tier Configuration
    l1_config: CacheTierConfig = Field(
        default_factory=lambda: CacheTierConfig(max_entries=1000),
        description="L1 (Memory) configuration"
    )
    l2_config: CacheTierConfig = Field(
        default_factory=lambda: CacheTierConfig(max_entries=5000),
        description="L2 (Flat File) configuration"
    )
    l3_config: CacheTierConfig = Field(
        default_factory=lambda: CacheTierConfig(max_entries=None),
        description="L3 (SQLite) configuration"
    )
    
    # TTL Configuration
    default_ttl_seconds: int = Field(
        default=3600,
        ge=60,
        description="Default TTL for cached proxies (seconds)"
    )
    ttl_cleanup_interval: int = Field(
        default=60,
        ge=10,
        description="Background cleanup interval (seconds)"
    )
    
    # Storage Paths
    l2_cache_dir: str = Field(
        default=".cache/proxies",
        description="Directory for L2 flat file cache"
    )
    l3_database_path: str = Field(
        default=".cache/proxywhirl.db",
        description="SQLite database path for L3"
    )
    
    # Encryption
    encryption_key: Optional[SecretStr] = Field(
        None,
        description="Fernet encryption key (from env: PROXYWHIRL_CACHE_ENCRYPTION_KEY)"
    )
    
    # Health Integration
    health_check_invalidation: bool = Field(
        default=True,
        description="Auto-invalidate on health check failure"
    )
    failure_threshold: int = Field(
        default=3,
        ge=1,
        description="Failures before health invalidation"
    )
    
    # Performance Tuning
    enable_statistics: bool = Field(default=True, description="Track cache statistics")
    statistics_interval: int = Field(default=5, ge=1, description="Stats aggregation interval (seconds)")
    
    class Config:
        json_encoders = {
            SecretStr: lambda v: "***"
        }
```

**Validation Rules**:
- `default_ttl_seconds` >= 60 (minimum 1 minute)
- `ttl_cleanup_interval` >= 10 (minimum 10 seconds)
- `failure_threshold` >= 1
- `statistics_interval` >= 1
- Paths must be writable (checked at runtime)

---

### 3. CacheStatistics

**Purpose**: Performance metrics and operational insights

**Schema**:
```python
from pydantic import BaseModel, Field, computed_field
from typing import Dict

class TierStatistics(BaseModel):
    """Statistics for a single cache tier"""
    hits: int = Field(default=0, ge=0)
    misses: int = Field(default=0, ge=0)
    current_size: int = Field(default=0, ge=0)
    evictions_lru: int = Field(default=0, ge=0)
    evictions_ttl: int = Field(default=0, ge=0)
    evictions_health: int = Field(default=0, ge=0)
    evictions_corruption: int = Field(default=0, ge=0)
    
    @computed_field
    @property
    def hit_rate(self) -> float:
        """Cache hit rate (0.0 to 1.0)"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    @computed_field
    @property
    def total_evictions(self) -> int:
        """Total evictions across all reasons"""
        return (self.evictions_lru + self.evictions_ttl + 
                self.evictions_health + self.evictions_corruption)

class CacheStatistics(BaseModel):
    """Aggregate cache statistics across all tiers"""
    l1_stats: TierStatistics = Field(default_factory=TierStatistics)
    l2_stats: TierStatistics = Field(default_factory=TierStatistics)
    l3_stats: TierStatistics = Field(default_factory=TierStatistics)
    
    # Cross-tier operations
    promotions: int = Field(default=0, ge=0, description="L3→L2→L1 promotions")
    demotions: int = Field(default=0, ge=0, description="L1→L2→L3 demotions")
    
    # Degradation tracking
    l1_degraded: bool = Field(default=False, description="L1 tier unavailable")
    l2_degraded: bool = Field(default=False, description="L2 tier unavailable")
    l3_degraded: bool = Field(default=False, description="L3 tier unavailable")
    
    @computed_field
    @property
    def overall_hit_rate(self) -> float:
        """Overall hit rate across all tiers"""
        total_hits = self.l1_stats.hits + self.l2_stats.hits + self.l3_stats.hits
        total_requests = (total_hits + self.l1_stats.misses + 
                         self.l2_stats.misses + self.l3_stats.misses)
        return total_hits / total_requests if total_requests > 0 else 0.0
    
    @computed_field
    @property
    def total_size(self) -> int:
        """Total cached entries across all tiers"""
        return (self.l1_stats.current_size + 
                self.l2_stats.current_size + 
                self.l3_stats.current_size)
    
    def to_metrics_dict(self) -> Dict[str, float]:
        """Convert to flat metrics dict for monitoring systems"""
        return {
            'cache.l1.hit_rate': self.l1_stats.hit_rate,
            'cache.l2.hit_rate': self.l2_stats.hit_rate,
            'cache.l3.hit_rate': self.l3_stats.hit_rate,
            'cache.overall.hit_rate': self.overall_hit_rate,
            'cache.total_size': float(self.total_size),
            'cache.promotions': float(self.promotions),
            'cache.demotions': float(self.demotions),
            'cache.l1.size': float(self.l1_stats.current_size),
            'cache.l2.size': float(self.l2_stats.current_size),
            'cache.l3.size': float(self.l3_stats.current_size),
        }
```

**Relationships**:
- One CacheStatistics instance per CacheManager
- Aggregated from TierStatistics for each tier
- Exported via monitoring endpoints (if REST API enabled)

---

### 4. CacheTier (Interface)

**Purpose**: Abstract interface for cache tier implementations

**Schema**:
```python
from abc import ABC, abstractmethod
from typing import Optional, List
from enum import Enum

class TierType(str, Enum):
    L1_MEMORY = "l1_memory"
    L2_FILE = "l2_file"
    L3_SQLITE = "l3_sqlite"

class CacheTier(ABC):
    """Abstract base class for cache tier implementations"""
    
    def __init__(self, config: CacheTierConfig, tier_type: TierType):
        self.config = config
        self.tier_type = tier_type
        self.enabled = config.enabled
        self.failure_count = 0
        self.failure_threshold = 3
    
    @abstractmethod
    def get(self, key: str) -> Optional[CacheEntry]:
        """Retrieve entry by key, None if not found or expired"""
        pass
    
    @abstractmethod
    def put(self, key: str, entry: CacheEntry) -> bool:
        """Store entry, return True if successful"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Remove entry by key, return True if existed"""
        pass
    
    @abstractmethod
    def clear(self) -> int:
        """Clear all entries, return count of removed entries"""
        pass
    
    @abstractmethod
    def size(self) -> int:
        """Return current number of entries"""
        pass
    
    @abstractmethod
    def keys(self) -> List[str]:
        """Return list of all keys"""
        pass
    
    def handle_failure(self, error: Exception) -> None:
        """Handle tier operation failure"""
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.enabled = False
            # Log and emit metric
    
    def reset_failures(self) -> None:
        """Reset failure count on successful operation"""
        self.failure_count = 0
        if not self.enabled:
            self.enabled = True
            # Log recovery
```

**Implementations**:
- `MemoryCacheTier(CacheTier)`: OrderedDict-based L1 cache
- `FileCacheTier(CacheTier)`: JSON file-based L2 cache with file locking
- `SQLiteCacheTier(CacheTier)`: SQLite database L3 cache (extends storage.py)

---

### 5. CacheManager

**Purpose**: Orchestrates multi-tier caching with automatic tier promotion/demotion

**Initialization Signature**:
```python
class CacheManager:
    def __init__(
        self,
        config: CacheConfig,
        encryptor: Optional[CredentialEncryptor] = None
    ) -> None:
        """
        Initialize cache manager with configuration.
        
        Args:
            config: Cache configuration (tier settings, TTL, paths)
            encryptor: Optional credential encryptor (created from config if None)
        
        Initializes:
            - L1 (Memory), L2 (File), L3 (SQLite) tiers based on config
            - TTL cleanup background thread
            - Statistics tracking
            - Tier degradation monitoring
        """
        self.config = config
        self.encryptor = encryptor or CredentialEncryptor.from_config(config)
        self.l1_tier = MemoryCacheTier(config.l1_config, TierType.L1_MEMORY)
        self.l2_tier = FileCacheTier(config.l2_config, TierType.L2_FILE, self.encryptor, config.l2_cache_dir)
        self.l3_tier = SQLiteCacheTier(config.l3_config, TierType.L3_SQLITE, self.encryptor, config.l3_database_path)
        self.statistics = CacheStatistics()
        self._lock = threading.RLock()
        self._ttl_manager = TTLManager(self, config.ttl_cleanup_interval)
        self._ttl_manager.start()
```

**See**: contracts/cache-api.json for complete CacheManager public API methods

---

## Database Schema (L3 - SQLite)

### Table: `cache_entries`

```sql
CREATE TABLE IF NOT EXISTS cache_entries (
    key TEXT PRIMARY KEY,
    proxy_url TEXT NOT NULL,
    username_encrypted BLOB,  -- Fernet-encrypted
    password_encrypted BLOB,  -- Fernet-encrypted
    source TEXT NOT NULL,
    fetch_time REAL NOT NULL,  -- Unix timestamp
    last_accessed REAL NOT NULL,  -- Unix timestamp
    access_count INTEGER DEFAULT 0,
    ttl_seconds INTEGER NOT NULL,
    expires_at REAL NOT NULL,  -- Unix timestamp
    health_status TEXT DEFAULT 'unknown',
    failure_count INTEGER DEFAULT 0,
    created_at REAL DEFAULT (julianday('now')),
    updated_at REAL DEFAULT (julianday('now'))
);

CREATE INDEX IF NOT EXISTS idx_expires_at ON cache_entries(expires_at);
CREATE INDEX IF NOT EXISTS idx_source ON cache_entries(source);
CREATE INDEX IF NOT EXISTS idx_health_status ON cache_entries(health_status);
CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache_entries(last_accessed);
```

**Rationale for Schema Design**:
- `key` as PRIMARY KEY: Unique constraint, fast lookups
- `expires_at` index: Efficient TTL cleanup queries
- `last_accessed` index: LRU eviction queries
- `source` index: Per-source TTL queries
- BLOBs for encrypted credentials: Binary storage for Fernet ciphertext
- `created_at`/`updated_at`: Database-only audit fields (not exposed in CacheEntry Pydantic model for simplicity, tracked internally by SQLite)

---

## File Format (L2 - Flat File)

### Format: JSON Lines (JSONL)

Each line is a JSON object representing a CacheEntry:

```json
{"key": "abc123", "proxy_url": "http://proxy1.com:8080", "username_encrypted": "gAAAAA...", "password_encrypted": "gAAAAA...", "source": "free-proxy-list", "fetch_time": "2025-11-01T12:00:00Z", "last_accessed": "2025-11-01T12:05:00Z", "access_count": 3, "ttl_seconds": 3600, "expires_at": "2025-11-01T13:00:00Z", "health_status": "healthy", "failure_count": 0}
{"key": "def456", "proxy_url": "http://proxy2.com:8080", ...}
```

**Rationale**:
- One entry per line: Append-only writes, easy to parse
- Base64-encoded encrypted fields: JSON-safe storage
- Atomic writes with file locking: Prevents corruption
- Compact format: ~200-300 bytes per entry

**File Naming Convention**:
```
.cache/proxies/
├── cache_0.jsonl      # Shard 0 (keys starting 0-3)
├── cache_1.jsonl      # Shard 1 (keys starting 4-7)
├── cache_2.jsonl      # Shard 2 (keys starting 8-b)
└── cache_3.jsonl      # Shard 3 (keys starting c-f)
```

Sharding by key prefix reduces lock contention on concurrent access.

---

## Entity Relationships Diagram

```
CacheManager
    ├── CacheConfig
    │   ├── l1_config: CacheTierConfig
    │   ├── l2_config: CacheTierConfig
    │   └── l3_config: CacheTierConfig
    │
    ├── CacheTier (L1 - Memory)
    │   └── stores: Dict[str, CacheEntry]
    │
    ├── CacheTier (L2 - File)
    │   └── stores: JSONL files (CacheEntry per line)
    │
    ├── CacheTier (L3 - SQLite)
    │   └── stores: cache_entries table (CacheEntry per row)
    │
    ├── CacheStatistics
    │   ├── l1_stats: TierStatistics
    │   ├── l2_stats: TierStatistics
    │   └── l3_stats: TierStatistics
    │
    └── TTLManager
        └── references: CacheTier instances for cleanup
```

---

## Validation & Constraints Summary

| Entity | Constraint | Enforcement |
|--------|-----------|-------------|
| CacheEntry | `ttl_seconds >= 0` | Pydantic validator |
| CacheEntry | `expires_at` in future for new entries | Application logic |
| CacheEntry | `proxy_url` valid URL | Pydantic HttpUrl |
| CacheConfig | `default_ttl_seconds >= 60` | Pydantic validator |
| CacheConfig | `failure_threshold >= 1` | Pydantic validator |
| CacheTier | `max_entries` respected | LRU eviction |
| CacheTier | Unique keys | Dict/SQLite PRIMARY KEY |
| CacheStatistics | All counts >= 0 | Pydantic validator |

---

## Data Flow

### Cache Write (Put Operation)
```
ProxyRotator.add_proxy(proxy)
    ↓
CacheManager.put(entry)
    ↓
L1.put(entry)  [Memory write, <1μs]
    ↓
L2.put(entry)  [Async write-behind, encrypted, ~5ms]
    ↓
L3.put(entry)  [Async write-behind, encrypted, ~2ms]
```

### Cache Read (Get Operation with Miss)
```
CacheManager.get(key)
    ↓
L1.get(key)  [Miss, ~100μs]
    ↓
L2.get(key)  [Miss, ~10ms]
    ↓
L3.get(key)  [Hit, ~3ms]
    ↓
L2.put(key, entry)  [Promotion, ~5ms]
    ↓
L1.put(key, entry)  [Promotion, ~1μs]
    ↓
Return entry to caller
```

### TTL Expiration (Background Cleanup)
```
TTLManager (every 60s)
    ↓
For each tier:
    Get expired keys (expires_at < now)
    ↓
    tier.delete(key)
    ↓
    stats.evictions_ttl += 1
```

---

## Next Steps

- Generate API contracts in `/contracts/cache-api.json`
- Create `quickstart.md` with usage examples
- Update agent context with new dependencies (cryptography, portalocker)
