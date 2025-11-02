# Research: Caching Mechanisms & Storage

**Feature**: 005-caching-mechanisms-storage  
**Date**: 2025-11-01  
**Phase**: 0 (Research & Technical Decisions)

## Overview

This document consolidates research findings and technical decisions for implementing the three-tier caching system. All NEEDS CLARIFICATION items from Technical Context are resolved here.

## Research Questions & Findings

### 1. Credential Encryption at Rest

**Question**: Which encryption approach for credentials in L2 (flat file) and L3 (SQLite)?

**Decision**: Fernet (symmetric encryption) from `cryptography` library

**Rationale**:
- Built on AES-128-CBC with HMAC authentication
- Simple API: `Fernet(key).encrypt(data)` / `decrypt(data)`
- Time-based token support (optional TTL enforcement)
- Well-tested, FIPS 140-2 compliant
- Minimal overhead: ~200 bytes per encrypted value
- Key derivation from password: PBKDF2HMAC (if needed)

**Alternatives Considered**:
- **AES-GCM directly**: More complex API, manual IV management, no built-in auth
- **NaCl/libsodium**: Requires additional binary dependency, overkill for this use case
- **RSA**: Asymmetric unnecessary here (no key exchange needed), much slower

**Implementation**:
```python
from cryptography.fernet import Fernet
from pydantic import SecretStr

class CredentialEncryptor:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
    
    def encrypt(self, secret: SecretStr) -> bytes:
        return self.cipher.encrypt(secret.get_secret_value().encode())
    
    def decrypt(self, encrypted: bytes) -> SecretStr:
        return SecretStr(self.cipher.decrypt(encrypted).decode())
```

**Key Management**:
- Read from `PROXYWHIRL_CACHE_ENCRYPTION_KEY` environment variable
- If not set, generate random key and warn (ephemeral, lost on restart)
- Store in config file NOT RECOMMENDED (security risk)

---

### 2. Cross-Platform File Locking

**Question**: How to implement thread-safe file locking for L2 (flat file) across Windows/Linux/macOS?

**Decision**: Use `portalocker` library (wrapper around fcntl/msvcrt)

**Rationale**:
- Abstracts platform differences (fcntl on Unix, msvcrt on Windows)
- Supports exclusive and shared locks
- Context manager for automatic release
- Timeout support to prevent deadlocks
- Minimal overhead: <1ms lock acquisition

**Alternatives Considered**:
- **Manual fcntl/msvcrt**: Requires conditional imports, error-prone, more code
- **File-based semaphores**: Race conditions, stale lock files
- **No locking**: Data corruption risk with concurrent writes

**Implementation**:
```python
import portalocker
import json

def read_cache_file(path):
    with portalocker.Lock(path, 'r', timeout=5) as f:
        return json.load(f)

def write_cache_file(path, data):
    with portalocker.Lock(path, 'w', timeout=5) as f:
        json.dump(data, f, indent=2)
```

**New Dependency**: `uv add portalocker>=2.8.0`

---

### 3. LRU Eviction Implementation

**Question**: Best data structure for O(1) LRU operations?

**Decision**: OrderedDict from Python stdlib (built-in LRU support)

**Rationale**:
- O(1) move_to_end() for access tracking
- O(1) popitem(last=False) for eviction
- Built-in, no external dependencies
- Thread-safe with external lock
- Memory efficient: ~200 bytes overhead per entry

**Alternatives Considered**:
- **Custom doubly-linked list**: More code, more bugs, no performance gain
- **functools.lru_cache decorator**: Not applicable (need cache invalidation)
- **cachetools library**: Overkill for our needs, adds dependency

**Implementation**:
```python
from collections import OrderedDict
from threading import RLock

class LRUCache:
    def __init__(self, max_size: int):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.lock = RLock()
    
    def get(self, key):
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)  # Mark as recently used
                return self.cache[key]
            return None
    
    def put(self, key, value):
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = value
            if len(self.cache) > self.max_size:
                self.cache.popitem(last=False)  # Evict LRU
```

---

### 4. TTL Expiration Strategy

**Question**: Active vs passive TTL expiration? How to balance performance and memory?

**Decision**: Hybrid approach - lazy expiration on access + periodic background cleanup

**Rationale**:
- **Lazy expiration**: Check TTL on cache hit, O(1) per access, no wasted work
- **Background cleanup**: Every 60s, scan and evict expired entries, prevent memory bloat
- Balances performance (no overhead on hits to valid entries) with memory efficiency (eventual cleanup)
- Background thread can be disabled for testing

**Alternatives Considered**:
- **Active only (immediate expiration)**: High CPU overhead, timers per entry
- **Passive only (lazy check)**: Memory bloat if entries never accessed again
- **Redis-style active+passive**: Overly complex for our scale

**Implementation**:
```python
import time
from threading import Thread, Event

class TTLManager:
    def __init__(self, cache, cleanup_interval=60):
        self.cache = cache
        self.cleanup_interval = cleanup_interval
        self.stop_event = Event()
        self.thread = Thread(target=self._cleanup_loop, daemon=True)
        self.thread.start()
    
    def is_expired(self, entry):
        return time.time() > entry.expires_at
    
    def _cleanup_loop(self):
        while not self.stop_event.wait(self.cleanup_interval):
            expired_keys = [k for k, v in self.cache.items() if self.is_expired(v)]
            for key in expired_keys:
                self.cache.evict(key, reason='ttl_expired')
```

---

### 5. Cache Tier Promotion/Demotion Strategy

**Question**: When to promote from L3→L2→L1? When to demote L1→L2→L3?

**Decision**: 
- **Promotion**: On cache hit, load into next tier up (read-through)
- **Demotion**: On L1 eviction (LRU), write to L2; on L2 eviction, write to L3

**Rationale**:
- Read-through caching: natural hot data rises to faster tiers
- Write-behind: evicted data preserved in slower tiers (no loss)
- Self-optimizing: access patterns determine tier placement
- No manual tier management required

**Alternatives Considered**:
- **Fixed tier placement**: Inflexible, can't adapt to access patterns
- **Configurable promotion threshold**: Added complexity, hard to tune
- **Time-based promotion**: Doesn't reflect actual access patterns

**Implementation Flow**:
```
Cache miss → Check L1 → Miss → Check L2 → Miss → Check L3 → Hit
  ↓
Load from L3 → Write to L2 → Write to L1 → Return to caller
  
L1 full → Evict LRU from L1 → Write to L2
L2 full → Evict LRU from L2 → Write to L3
L3 full → Evict LRU from L3 → Gone
```

---

### 6. Cache Statistics Tracking

**Question**: Which metrics to track? How to minimize performance overhead?

**Decision**: Atomic counters with periodic aggregation

**Metrics to Track**:
- Hit count (per tier)
- Miss count (per tier)
- Eviction count (per tier, per reason: LRU, TTL, health, corruption)
- Cache size (current entries per tier)
- Promotion count (L3→L2→L1)
- Demotion count (L1→L2→L3)

**Rationale**:
- Atomic operations: `threading.local` counters + periodic flush to shared state
- ~10 nanoseconds overhead per operation (negligible)
- Aggregation every 5s reduces lock contention

**Implementation**:
```python
from threading import Lock
from dataclasses import dataclass, field

@dataclass
class CacheStatistics:
    l1_hits: int = 0
    l1_misses: int = 0
    l2_hits: int = 0
    l2_misses: int = 0
    l3_hits: int = 0
    l3_misses: int = 0
    evictions_lru: int = 0
    evictions_ttl: int = 0
    evictions_health: int = 0
    evictions_corruption: int = 0
    
    def hit_rate(self, tier: str) -> float:
        hits = getattr(self, f'{tier}_hits')
        misses = getattr(self, f'{tier}_misses')
        total = hits + misses
        return hits / total if total > 0 else 0.0
```

---

### 7. Graceful Degradation Implementation

**Question**: How to detect tier failures and implement fallback?

**Decision**: Try-except with tier skip flag + health tracking

**Rationale**:
- Catch storage exceptions (IOError, sqlite3.Error, PermissionError)
- Set tier disabled flag on repeated failures (3 consecutive)
- Re-enable on successful operation (self-healing)
- Metrics track degraded state for monitoring

**Implementation**:
```python
class CacheTier:
    def __init__(self):
        self.enabled = True
        self.failure_count = 0
        self.failure_threshold = 3
    
    def get(self, key):
        if not self.enabled:
            return None
        try:
            result = self._get_impl(key)
            self.failure_count = 0  # Reset on success
            return result
        except Exception as e:
            self.failure_count += 1
            logger.error(f"Tier failure: {e}")
            if self.failure_count >= self.failure_threshold:
                self.enabled = False
                logger.error("Tier disabled due to repeated failures")
                emit_metric('cache_tier_degraded', tier=self.name)
            return None
```

---

## Best Practices Applied

### Python 3.9+ Compatibility
- Use `Union[X, Y]` instead of `X | Y`
- Use `datetime.timezone.utc` instead of `datetime.UTC`
- Use `Optional[X]` from typing

### Security Best Practices
- Never log decrypted credentials (test with grep for get_secret_value calls)
- Encryption keys from environment, never hardcoded
- Fernet provides authenticated encryption (prevents tampering)
- Clear credential memory after use (though Python GC handles this)

### Performance Best Practices
- Lock granularity: Per-tier locks, not global cache lock
- Lazy expiration: Only check TTL on access
- Background cleanup: Separate thread, low priority
- Atomic counters: thread-local with periodic aggregation

### Testing Best Practices
- Mock time.time() for deterministic TTL tests
- Use temporary directories for file cache tests
- In-memory SQLite (`:memory:`) for fast L3 tests
- Property tests for LRU invariants (Hypothesis)

---

## Dependencies Summary

**New Dependencies to Add**:
```bash
uv add cryptography>=41.0.0        # Fernet encryption
uv add portalocker>=2.8.0          # Cross-platform file locking
```

**Existing Dependencies Used**:
- `pydantic>=2.0.0` (SecretStr, validation)
- `loguru>=0.7.0` (structured logging)
- stdlib: `collections.OrderedDict`, `threading`, `json`, `sqlite3`, `time`

**Dev Dependencies**:
- `pytest>=7.4.0` (testing)
- `hypothesis>=6.88.0` (property tests)
- `pytest-benchmark>=4.0.0` (performance tests)

---

## Performance Estimates

Based on research and benchmarks:

| Operation | Target | Estimated | Method |
|-----------|--------|-----------|--------|
| L1 lookup | <1ms | ~100μs | OrderedDict + lock |
| L2 lookup | <50ms | ~5-20ms | JSON read + decrypt |
| L3 lookup | <50ms | ~1-10ms | SQLite query |
| Eviction overhead | <10ms | ~100μs | popitem() + write |
| Cache warming (10k) | <5s | ~2-3s | Batch insert |
| Encryption overhead | N/A | ~50μs/credential | Fernet benchmark |

All targets achievable with proposed implementation.

---

## Risk Mitigation

### Risk 1: Encryption key loss
**Impact**: Cannot decrypt cached credentials  
**Mitigation**: Document key backup procedure, support key rotation

### Risk 2: File lock timeout
**Impact**: Cache write fails, data loss  
**Mitigation**: 5s timeout + fallback to L1 only, log warning

### Risk 3: Background thread crash
**Impact**: TTL expiration stops, memory bloat  
**Mitigation**: Exception handling in cleanup loop, restart on crash

### Risk 4: Clock skew (TTL)
**Impact**: Incorrect expiration times  
**Mitigation**: Use monotonic time for TTL calculations, document NTP requirement

---

## Next Steps

Phase 1: Design & Contracts
- Create `data-model.md` with entity schemas
- Generate API contracts in `/contracts/`
- Create `quickstart.md` with usage examples
- Update agent context with new dependencies
