# Cache Subsystem

> Extends: [../../AGENTS.md](../../AGENTS.md)

## Modules

| File | Key Classes |
|------|-------------|
| `manager.py` | `CacheManager` |
| `tiers.py` | `L1Cache`, `L2Cache` |
| `crypto.py` | Encrypt/decrypt utilities |
| `models.py` | `CacheEntry`, `CacheStatistics` |

## Architecture

```
L1 (in-memory, fast) → L2 (LRU, encrypted) → Origin (fetch)
```

## Usage

```python
cache = CacheManager(CacheConfig(l1_max_size=1000, encryption_enabled=True))
await cache.set("key", value, ttl=60)
result = await cache.get("key")
```

## Boundaries

**Always:**
- Set TTL for all cache entries
- Handle cache misses gracefully (return None, not raise)
- Log cache statistics periodically
- Test with encryption enabled AND disabled
- Use atomic operations for concurrent access

**Ask First:**
- Eviction policy changes
- L1/L2 size default changes
- Adding new cache tiers
- Serialization format changes

**Never:**
- Change encryption algorithm without security review
- Break serialization backwards compatibility
- Cache sensitive data without encryption
- Ignore TTL expiration

## Performance Targets

L1 hit < 0.1ms, L2 hit < 1ms, warmup < 5s for 10k entries
