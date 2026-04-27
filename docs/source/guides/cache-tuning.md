# Cache Tuning Guide

ProxyWhirl uses a three-tier cache (L1 memory, L2 disk, L3 SQLite) to minimize repeated proxy fetches and health checks. Tuning these tiers can dramatically improve latency and reduce load on upstream proxy sources.

## Tier Overview

| Tier | Speed | Persistence | Typical Use |
|------|-------|-------------|-------------|
| L1 (Memory) | Nanoseconds | Ephemeral | Hot proxies for current process |
| L2 (Disk) | Microseconds | Persistent across restarts | Recently used proxies |
| L3 (SQLite) | Milliseconds | Persistent | Long-term archive and statistics |

## Basic Configuration

All tiers are controlled through `CacheConfig`:

```python
from proxywhirl import CacheConfig, CacheManager

config = CacheConfig(
    l1_max_entries=500,
    l2_max_entries=2000,
    l3_max_entries=10000,
    default_ttl_seconds=3600,
    cleanup_interval_seconds=300,
)

manager = CacheManager(config=config)
```

## Tuning L1 (Memory)

L1 is an in-memory LRU cache. Increase its size if your workload repeatedly hits a small set of proxies.

- **Small footprint (CLI tool):** `l1_max_entries=100`
- **Web service (steady traffic):** `l1_max_entries=1000`
- **Scraper (high churn):** `l1_max_entries=5000`

L1 entries are lost on process restart. Rely on L2/L3 for durability.

## Tuning L2 (Disk)

L2 stores serialized `CacheEntry` objects on disk using JSONL or SQLite (configurable via `l2_backend`).

```python
config = CacheConfig(
    l2_backend="sqlite",  # "jsonl" or "sqlite"
    l2_max_entries=5000,
)
```

- **JSONL:** Best for <10K entries. Portable, human-readable, file-based locking.
- **SQLite:** Best for >10K entries. Indexed `O(log n)` lookups and atomic writes.

## Tuning TTL

The `TTLManager` evicts expired entries during background cleanup. Set TTL based on how quickly your proxies rotate.

```python
config = CacheConfig(
    default_ttl_seconds=1800,  # 30 minutes
    per_source_ttl={
        "fast_proxies": 600,
        "slow_proxies": 3600,
    },
)
```

Shorter TTLs reduce stale-proxy risk; longer TTLs reduce fetch frequency.

## Per-Source Overrides

Different proxy sources have different reliability. Use `per_source_ttl` to fine-tune without creating multiple `CacheManager` instances.

## Health-Aware Invalidation

Enable automatic invalidation when a cached proxy fails repeated health checks:

```python
config = CacheConfig(
    health_check_invalidation=True,
    failure_threshold=3,
)
```

After three consecutive failures, the proxy is evicted from all tiers and re-fetched from the source.

## Monitoring Cache Performance

`CacheStatistics` exposes hit rates and eviction counts:

```python
stats = manager.get_statistics()
print(f"L1 hit rate: {stats.l1_stats.hit_rate:.2%}")
print(f"L2 evictions (TTL): {stats.l2_stats.evictions_ttl}")
```

Aim for L1 hit rates above 70%. If L2 hit rate is low, increase L2 size or shorten TTL.

## Common Pitfalls

- **Zero TTL:** Disables caching entirely; every request fetches from the source.
- **Oversized L1:** High memory usage with diminishing returns beyond a few thousand entries.
- **Ignoring cleanup:** Without `cleanup_interval_seconds`, expired entries linger until accessed.

## Summary

| Goal | Recommendation |
|------|----------------|
| Reduce memory | Lower `l1_max_entries`, raise `default_ttl_seconds` |
| Faster restarts | Use `l2_backend="sqlite"` with large `l2_max_entries` |
| Less stale proxies | Shorter `default_ttl_seconds`, enable health invalidation |
| Debug cache issues | Inspect `CacheStatistics` and `CacheEntry` metadata |
