# ADR-001: Three-Tier Cache Architecture

## Status

Accepted

## Context

ProxyWhirl needs to efficiently cache proxy information across application restarts while maintaining fast lookup times and managing memory consumption. The system must handle:

- **Performance**: Sub-millisecond lookups for frequently accessed proxies
- **Persistence**: Proxy data retention across application restarts
- **Scalability**: Support for thousands to millions of proxies
- **Resource Constraints**: Limited memory for in-memory caching
- **Data Security**: Safe storage of proxy credentials
- **Reliability**: Graceful degradation when storage layers fail
- **TTL Management**: Automatic expiration of stale proxy entries

Traditional single-tier caching approaches (memory-only or database-only) present tradeoffs:
- Pure in-memory caching loses data on restart and has memory limits
- Pure database caching incurs I/O overhead for every lookup
- Hybrid approaches without clear separation lead to complexity

## Decision

We implemented a **three-tier cache hierarchy** with automatic promotion/demotion:

### Tier Architecture

**L1 - Memory Cache (`MemoryCacheTier`)**
- **Technology**: Python `OrderedDict` with LRU eviction
- **Capacity**: 1,000 entries (configurable)
- **Purpose**: Hot cache for frequently accessed proxies
- **Performance**: O(1) lookups, <1ms access time
- **Eviction**: LRU policy when capacity exceeded
- **Persistence**: None (volatile)

**L2 - File Cache (`DiskCacheTier`)**
- **Technology**: JSONL (newline-delimited JSON) with file sharding
- **Capacity**: 5,000 entries (configurable)
- **Purpose**: Warm cache for recently used proxies
- **Performance**: O(1) per shard, ~1-5ms access time
- **Eviction**: FIFO within shards
- **Persistence**: Durable to disk
- **Security**: Credential encryption via `CredentialEncryptor`
- **Concurrency**: File-level locking using `portalocker`

**L3 - Database Cache (`SQLiteCacheTier`)**
- **Technology**: SQLite with indexed queries
- **Capacity**: Unlimited (configurable)
- **Purpose**: Cold storage for all cached proxies
- **Performance**: O(log n) indexed lookups, ~5-10ms access time
- **Eviction**: TTL-based expiration only
- **Persistence**: Durable with ACID guarantees
- **Security**: Encrypted credential BLOBs
- **Queryability**: Full SQL query support

### Key Mechanisms

**Cache Promotion** (read path):
```
L3 hit → Promote to L2 + L1
L2 hit → Promote to L1
L1 hit → Update access tracking
```

**Cache Demotion** (write path):
```
L1 eviction → Demote to L2
L2 eviction → Demote to L3
L3 eviction → TTL expiry only
```

**Credential Security**:
- L1: Pydantic `SecretStr` (redacted in logs/serialization)
- L2: Fernet encryption (symmetric AES-128-CBC)
- L3: Fernet-encrypted BLOBs in database

**TTL Management**:
- Lazy expiration on every `get()` operation
- Optional background cleanup thread (`TTLManager`)
- Bulk expiration using SQL `DELETE WHERE expires_at < ?` (L3)
- Per-shard cleanup for L2 JSONL files

**Graceful Degradation**:
- Each tier tracks consecutive failures
- Auto-disable tier after 3 failures
- Cache continues with remaining tiers
- Statistics track degradation status

## Consequences

### Positive

1. **Performance**:
   - Hot proxies served from L1 with <1ms latency
   - 80%+ hit rate on L1 for typical workloads
   - Database only accessed for cold starts and cache misses

2. **Persistence**:
   - L2/L3 survive application restarts
   - SQLite provides ACID durability guarantees
   - No data loss on graceful shutdown

3. **Scalability**:
   - L1 bounded memory usage (1K entries ≈ 1-2 MB)
   - L2 file sharding prevents single-file bottlenecks
   - L3 SQLite scales to millions of entries

4. **Security**:
   - Credentials never logged or serialized in plaintext
   - At-rest encryption in L2/L3 via Fernet
   - SecretStr prevents accidental exposure in L1

5. **Reliability**:
   - Graceful degradation on tier failures
   - L1 always available (in-memory)
   - Can operate with any subset of tiers

6. **Observability**:
   - Per-tier hit/miss statistics
   - Eviction reason tracking (LRU, TTL, health)
   - Promotion/demotion metrics

### Negative

1. **Complexity**:
   - Three separate implementations to maintain
   - Coordination between tiers requires careful locking
   - Testing requires multiple storage backends

2. **Storage Overhead**:
   - Same proxy may exist in L1, L2, and L3 simultaneously
   - ~3x storage cost for hot proxies
   - Mitigated by LRU eviction keeping L1/L2 small

3. **Concurrency**:
   - File locking in L2 can cause contention under high load
   - Single `threading.RLock` in `CacheManager` serializes cross-tier operations
   - Mitigated by L1 serving most requests

4. **Credential Encryption Overhead**:
   - Fernet encryption adds ~1-2ms to L2/L3 reads/writes
   - Memory overhead for storing encrypted + decrypted copies
   - Acceptable tradeoff for security requirements

5. **Background Cleanup Thread**:
   - Optional TTL cleanup thread adds complexity
   - Lazy expiration sufficient for most use cases
   - Thread can be disabled if not needed

### Alternatives Considered

**Single-Tier SQLite Cache**:
- Simpler implementation
- Every lookup requires disk I/O (5-10ms vs <1ms)
- Rejected due to performance requirements

**Two-Tier (Memory + Database)**:
- Reduced complexity vs three-tier
- Missing warm cache for recently evicted entries
- Higher L3 load on L1 misses
- Rejected to optimize cache hit rate

**Redis/Memcached**:
- External dependency (deployment complexity)
- Network overhead even for localhost
- Overkill for single-process use case
- Rejected for simplicity

**Write-Through vs Write-Around**:
- Write-through: Write to all tiers on `put()` (chosen)
- Write-around: Only write to lowest tier, promote on read
- Chose write-through for data redundancy

## Implementation Details

### File Structure
```
proxywhirl/cache/
├── manager.py       # CacheManager orchestration
├── tiers.py         # Tier implementations (L1/L2/L3)
├── models.py        # Pydantic models (CacheEntry, configs)
├── crypto.py        # Fernet credential encryption
└── __init__.py      # Public API exports
```

### Key Classes
- `CacheManager`: Orchestrates multi-tier operations with promotion/demotion
- `CacheTier` (ABC): Base interface for all tiers
- `MemoryCacheTier`: L1 OrderedDict implementation
- `DiskCacheTier`: L2 JSONL file cache
- `SQLiteCacheTier`: L3 SQLite database cache
- `TTLManager`: Background cleanup thread
- `CredentialEncryptor`: Fernet-based encryption wrapper

### Thread Safety
- `CacheManager` uses `threading.RLock` for cross-tier operations
- L1 (OrderedDict) protected by manager lock
- L2 uses `portalocker` for file-level locking
- L3 SQLite has built-in connection-level locking

## References

- Implementation: `/Users/ww/dev/projects/proxywhirl/proxywhirl/cache/`
- Tests: `/Users/ww/dev/projects/proxywhirl/tests/unit/test_cache_*.py`
- Related: ADR-004 (Storage Backend Decisions)

## Notes

This ADR documents the cache architecture as implemented. Future optimizations could include:
- Async I/O for L2/L3 operations (currently synchronous)
- Read-write locks instead of single mutex (higher concurrency)
- Probabilistic data structures (Bloom filters) to avoid L3 lookups
- LFU eviction policy as alternative to LRU
