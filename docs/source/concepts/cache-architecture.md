---
title: Cache Architecture
---

# Cache Architecture

ProxyWhirl uses a three-tier cache hierarchy to balance speed, persistence, and scalability. This page explains the design rationale -- for configuration, see {doc}`/guides/caching` and {doc}`/reference/cache-api`.

## Why Three Tiers?

Single-tier caching forces a tradeoff: in-memory is fast but volatile, disk is durable but slow. ProxyWhirl avoids this by using **three tiers with automatic promotion and demotion**:

| Tier | Technology | Capacity | Access Time | Persistence |
|------|-----------|----------|-------------|-------------|
| **L1** (Hot) | Python `OrderedDict` + LRU | 1,000 entries | <1 ms | None (volatile) |
| **L2** (Warm) | JSONL files with sharding | 5,000 entries | 1-5 ms | Durable to disk |
| **L3** (Cold) | SQLite with indexes | Unlimited | 5-10 ms | ACID durable |

In a typical workload, **80%+ of lookups hit L1** -- the database is only touched on cold starts and cache misses.

### Alternatives Considered

- **Single-tier SQLite**: Simpler, but every lookup costs 5-10 ms vs <1 ms
- **Two-tier (memory + database)**: Missing the warm cache for recently evicted entries, causing higher L3 load
- **Redis/Memcached**: External dependency, network overhead, overkill for single-process use

## Promotion and Demotion

Data flows between tiers automatically:

```{mermaid}
graph LR
    A[Request] -->|cache miss| B[L3 SQLite]
    B -->|promote| C[L2 Disk]
    C -->|promote| D[L1 Memory]
    D -->|LRU evict| C
    C -->|FIFO evict| B
    B -->|TTL expire| E[Deleted]
    D -->|hit| D
```

**Read path (promotion):**
- L3 hit → promote to L2 and L1
- L2 hit → promote to L1
- L1 hit → update access tracking (LRU)

**Eviction path (demotion):**
- L1 full → LRU eviction demotes entry to L2
- L2 full → FIFO eviction demotes entry to L3
- L3 entries expire by TTL only

This means hot proxies "bubble up" to L1 naturally, while cold proxies sink to L3 without being lost.

## Credential Security Across Tiers

Proxy credentials receive different protection at each tier:

| Tier | Mechanism | Protection |
|------|-----------|-----------|
| **L1** | Pydantic `SecretStr` | Redacted in logs and serialization |
| **L2** | Fernet encryption (AES-128-CBC) | Encrypted at rest on disk |
| **L3** | Fernet-encrypted BLOBs | Encrypted in database |

The encryption key is provided via `PROXYWHIRL_CACHE_ENCRYPTION_KEY` (a Fernet key). Without it, L2/L3 store credentials in plaintext -- suitable for development but not production.

The encryption adds ~1-2 ms to L2/L3 reads/writes, which is acceptable since L1 serves most requests.

## Graceful Degradation

Each tier tracks consecutive failures and auto-disables after 3 failures. The cache continues with remaining healthy tiers:

- L2 disk full? L1 and L3 continue serving.
- L3 database locked? L1 and L2 continue serving.
- All tiers fail? Operations proceed without caching (slower but functional).

Per-tier health statistics are exposed via `CacheManager.get_stats()`.

## TTL Management

Entries expire via two mechanisms:

1. **Lazy expiration**: Every `get()` checks TTL before returning. Expired entries are silently removed.
2. **Background cleanup** (optional): A `TTLManager` thread periodically purges expired entries in bulk -- using `DELETE WHERE expires_at < ?` for L3 and per-shard cleanup for L2.

Lazy expiration is sufficient for most workloads. The background thread is useful when expired entries would otherwise consume significant disk or memory.

## Thread Safety

`CacheManager` uses a single `threading.RLock` for cross-tier operations. This serializes promotion/demotion but keeps the design simple. Individual tiers also have their own mechanisms:

- **L1**: Protected by the manager lock
- **L2**: `portalocker` for file-level locking (safe for multi-process)
- **L3**: SQLite's built-in connection-level locking

For most workloads, the single lock isn't a bottleneck because L1 hits (the common case) resolve quickly.

## Further Reading

- {doc}`/guides/caching` -- configuration guide
- {doc}`/reference/cache-api` -- `CacheEntry`, `CacheConfig`, `CacheManager` API
- [ADR-001: Three-Tier Cache](https://github.com/wyattowalsh/proxywhirl/blob/main/docs/adr/001-three-tier-cache.md) -- original decision record
