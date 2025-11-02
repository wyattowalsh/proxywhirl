# Feature Specification: Caching Mechanisms

**Feature Branch**: `005-caching-mechanisms-storage`  
**Created**: 2025-10-08  
**Status**: Draft  
**Input**: User description: "Storage and management of fetched proxies for efficient reuse"

## Clarifications

### Session 2025-11-01

- Q: Which storage backend(s) should be implemented for the multi-tier caching system? → A: In-memory, flat file, and SQLite (three-tier architecture)
- Q: How should proxy credentials be secured in cache storage? → A: Encrypt credentials at rest, use SecretStr in memory (aligns with existing security practices)
- Q: What is the default memory tier (L1) size limit? → A: 1000 proxies (10MB memory)
- Q: What happens when cache storage becomes full (disk space exhausted)? → A: Log error, stop caching to disk, continue in-memory only (graceful degradation)
- Q: How should cache corruption or invalid cache entries be handled? → A: Evict corrupted entry, log warning, continue (surgical removal)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Persist Fetched Proxies (Priority: P1)

A proxy scraping service fetches hundreds of proxies from various sources and needs to store them locally to avoid re-fetching the same proxies repeatedly, reducing external API calls and improving performance.

**Why this priority**: Core caching functionality - enables efficient proxy reuse and reduces dependency on external proxy sources.

**Independent Test**: Can be tested by fetching proxies, shutting down the system, restarting, and verifying cached proxies are available without re-fetching.

**Acceptance Scenarios**:

1. **Given** proxies are fetched from external sources, **When** stored in cache, **Then** proxies persist to local storage (file, database, memory)
2. **Given** cached proxies exist, **When** system restarts, **Then** previously cached proxies are loaded and available
3. **Given** new proxies are fetched, **When** they already exist in cache, **Then** existing entries are updated with latest metadata

---

### User Story 2 - TTL-Based Proxy Expiration (Priority: P1)

A user wants cached proxies to automatically expire after a configurable time period (TTL) because proxy validity degrades over time, ensuring only fresh proxies are used.

**Why this priority**: Prevents stale proxy usage - critical for maintaining proxy pool quality and success rates.

**Independent Test**: Can be tested by setting short TTL, caching proxies, waiting for expiration, and verifying expired proxies are removed.

**Acceptance Scenarios**:

1. **Given** proxies cached with 1-hour TTL, **When** 1 hour elapses, **Then** proxies are automatically evicted from cache
2. **Given** cached proxy is accessed, **When** TTL has expired, **Then** proxy is treated as unavailable and re-fetched
3. **Given** TTL configuration is updated, **When** system reloads config, **Then** new TTL applies to subsequently cached proxies

---

### User Story 3 - Cache Invalidation by Health Status (Priority: P2)

Operations team needs to automatically invalidate cached proxies that fail health checks, preventing continued use of dead or blocked proxies.

**Why this priority**: Maintains cache quality - ensures only working proxies remain cached, improving success rates.

**Independent Test**: Can be tested by marking cached proxies as unhealthy and verifying they are removed from cache.

**Acceptance Scenarios**:

1. **Given** cached proxy fails health check, **When** failure threshold is reached, **Then** proxy is removed from cache
2. **Given** proxy becomes unhealthy, **When** in cache, **Then** proxy is marked for re-validation before next use
3. **Given** cached proxy pool, **When** bulk health check runs, **Then** all failed proxies are evicted automatically

---

### User Story 4 - Multi-Tier Caching Strategy (Priority: P2)

A high-performance application needs multi-tier caching (memory, disk, distributed) to optimize for speed while maintaining persistence, with hot proxies in memory and cold storage on disk.

**Why this priority**: Performance optimization - balances speed and persistence for different access patterns.

**Independent Test**: Can be tested by accessing proxies and verifying cache hits from appropriate tier (memory vs. disk).

**Acceptance Scenarios**:

1. **Given** frequently accessed proxies, **When** requested, **Then** served from in-memory cache with sub-millisecond latency
2. **Given** less frequently used proxies, **When** requested, **Then** loaded from disk cache and promoted to memory
3. **Given** memory cache is full, **When** new proxy is cached, **Then** least-recently-used proxy is evicted to disk

---

### User Story 5 - Cache Warming from Sources (Priority: P3)

A system administrator wants to pre-populate (cache warming) the cache from proxy lists or previous exports during startup to avoid cold-start delays.

**Why this priority**: Improves startup performance - ensures proxies are immediately available without initial fetch delays.

**Independent Test**: Can be tested by importing proxy list during startup and verifying cache is populated before first request.

**Acceptance Scenarios**:

1. **Given** proxy list file exists, **When** system starts with cache warming enabled, **Then** proxies are loaded into cache
2. **Given** cache warming source, **When** proxies are imported, **Then** TTL and metadata are set appropriately
3. **Given** warming fails for some proxies, **When** import continues, **Then** valid proxies are cached and errors are logged

---

### User Story 6 - Cache Statistics and Monitoring (Priority: P3)

Operations team needs visibility into cache performance (hit rate, size, evictions) to tune cache configuration and understand system behavior.

**Why this priority**: Operational insight - enables optimization and troubleshooting of cache performance.

**Independent Test**: Can be tested by making requests and verifying cache statistics are accurately tracked and exposed.

**Acceptance Scenarios**:

1. **Given** cache is in use, **When** requests are made, **Then** cache hit/miss rates are tracked and exposed via API
2. **Given** cache operations, **When** evictions occur, **Then** eviction counts and reasons are recorded
3. **Given** cache statistics, **When** accessed via monitoring endpoint, **Then** metrics include size, hit rate, TTL stats, and turnover

---

### Edge Cases

- Disk space exhausted: Log error, disable persistent caching (L2/L3), continue in-memory only with alerting
- Cache corruption: Evict corrupted entry, log WARNING with entry details, increment corruption metric, continue operations
- Multiple processes updating same proxy: Use portalocker file locking for L2 (exclusive write lock with 5s timeout), SQLite WAL mode for L3 (concurrent reads, serialized writes), RLock per tier for L1 (in-process thread safety). Cross-process coordination limited to file/database locking mechanisms.
- Cache backend unavailable: Degrade gracefully to higher tier (L3 fails → use L2, L2 fails → use L1 only)
- Imported cache data with conflicting TTL/metadata: Use most recent fetch_time as source of truth, update existing entry with new metadata, log INFO about merge conflict resolution
- Rapid proxy fetching exceeding cache capacity: LRU eviction maintains capacity limits, oldest entries demoted to lower tiers or evicted. No explicit backpressure - fetcher continues, cache absorbs via eviction. Monitor eviction rate via statistics.
- Proxy metadata conflicts with newly fetched: Update existing entry with new metadata (fetch_time, health_status, TTL), preserve access_count and last_accessed statistics, log DEBUG about update

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support persistent caching of fetched proxies across restarts
- **FR-002**: System MUST support configurable TTL (time-to-live) for cached proxies
- **FR-003**: System MUST automatically evict expired proxies based on TTL
- **FR-004**: System MUST support cache invalidation based on health check failures
- **FR-005**: System MUST support three-tier caching architecture: in-memory (L1), flat file (L2), and SQLite (L3)
- **FR-006**: System MUST provide cache warming from proxy lists or previous exports
- **FR-007**: System MUST track cache statistics (hit rate, miss rate, size, evictions)
- **FR-008**: System MUST support manual cache clearing/flushing operations
- **FR-009**: System MUST handle cache storage backend failures gracefully via tier degradation: log ERROR, disable failed tier, emit degradation metric, continue operations with remaining tiers (L3 fails → use L2+L1, L2 fails → use L1 only, L1 never fails as it's in-memory)
- **FR-010**: System MUST support configurable cache size limits with defaults: L1=1000 proxies, L2=5000 proxies, L3=unlimited
- **FR-011**: System MUST implement LRU (Least Recently Used) eviction when cache is full
- **FR-012**: System MUST store proxy metadata alongside cached proxy (last used, fetch time, health)
- **FR-013**: System MUST support cache import/export for backup and migration
- **FR-014**: System MUST provide cache key collision handling for duplicate proxies
- **FR-015**: System MUST support per-proxy-source TTL configuration
- **FR-016**: System MUST log cache operations for debugging and auditing
- **FR-017**: System MUST support cache locking for thread-safe operations
- **FR-018**: System MUST provide cache health checks and self-healing capabilities including automatic corruption detection and eviction (cache tier is healthy if failure_count < 3 and last successful operation within 60 seconds)
- **FR-019**: [Future Enhancement] System SHOULD support cache partitioning by proxy type or source (not included in MVP - Phase 1 implementation focuses on unified cache)
- **FR-020**: System MUST expose cache metrics via monitoring endpoints
- **FR-021**: System MUST protect proxy credentials using: (a) SecretStr for in-memory storage (L1), (b) Fernet symmetric encryption for at-rest storage (L2/L3), (c) never log or expose decrypted credentials, (d) secure key management via environment variable. See data-model.md CacheEntry schema and cache_crypto.py implementation for technical details.
- **FR-022**: System MUST log ERROR and emit metrics when disk storage exhausted, then disable L2/L3 tiers
- **FR-023**: System MUST continue operations with degraded caching when persistent tiers fail
- **FR-024**: System MUST detect corrupted cache entries via validation (schema, decryption, data integrity)
- **FR-025**: System MUST automatically evict corrupted entries and log WARNING with entry identifier and corruption reason

### Key Entities

- **Cached Proxy**: Stored proxy with metadata (URL, credentials, fetch time, last used, TTL, health status, source)
- **Cache Entry**: Container for cached proxy with key, value, TTL, and metadata
- **Cache Tier**: Storage level with specific characteristics:
  - **L1 (Memory)**: In-memory cache for hot proxies, sub-millisecond access, default limit 1000 proxies (~10MB)
  - **L2 (JSONL Flat File)**: JSONL file cache for warm proxies, moderate persistence
  - **L3 (SQLite)**: Database cache for cold storage, full persistence and queryability
- **Cache Statistics**: Metrics tracking cache performance (hits, misses, evictions, size, hit rate)
- **Cache Configuration**: Settings controlling cache behavior (TTL, size limits, eviction policy, backend type)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Cache hit rate achieves 80% or higher for typical workloads
- **SC-002**: Memory cache lookups complete in under 1ms
- **SC-003**: Disk cache lookups complete in under 50ms
- **SC-004**: Cache reduces external proxy fetches by 60% or more
- **SC-005**: Cached proxies persist correctly across 100 system restarts
- **SC-006**: TTL-based expiration removes proxies within 1 minute of expiration time
- **SC-007**: Cache warming loads 10,000 proxies in under 5 seconds
- **SC-008**: Cache handles 100,000 concurrent access operations without corruption
- **SC-009**: Cache eviction maintains performance with less than 10ms overhead
- **SC-010**: Cache storage uses less than 100MB for 10,000 proxies

## Assumptions

- Cache storage backend has sufficient capacity for expected proxy volumes (graceful degradation handles exhaustion)
- TTL values are configured appropriately for proxy lifespan
- File system or cache backend supports concurrent access patterns
- Cache warming sources contain valid proxy data
- System has sufficient memory for hot proxy cache tier
- Cache corruption is rare and handled automatically via self-healing (eviction + logging)

## Dependencies

- Core Python Package for proxy data structures
- Health Monitoring for cache invalidation triggers
- Configuration Management for cache settings
- Logging System for cache operation logging
- Metrics & Observability for cache statistics
- **New Dependencies**:
  - `cryptography>=41.0.0` - Fernet symmetric encryption for credential protection at rest
  - `portalocker>=2.8.0` - Cross-platform file locking for L2 cache tier (fcntl on Unix, msvcrt on Windows)

```
