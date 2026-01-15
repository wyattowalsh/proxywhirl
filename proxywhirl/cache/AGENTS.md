# Cache Subsystem

> Extends: [../../AGENTS.md](../../AGENTS.md)

## Modules

| File | Classes |
|------|---------|
| `manager.py` | `CacheManager` |
| `tiers.py` | `L1Cache`, `L2Cache` |
| `crypto.py` | `get_fernet_key()`, `rotate_encryption_key()` |
| `models.py` | `CacheEntry`, `CacheStatistics`, `CacheConfig` |

## Architecture

`L1 (in-memory) → L2 (LRU, encrypted) → Origin`

## Environment Variables

`PROXYWHIRL_CACHE_ENCRYPTION_KEY` (Fernet key), `PROXYWHIRL_CACHE_KEY_PREVIOUS` (rotation)

## Usage

```python
from proxywhirl import CacheManager
from proxywhirl.cache.models import CacheConfig
cache = CacheManager(CacheConfig(l1_max_size=1000, encryption_enabled=True))
await cache.set("key", value, ttl=60)
```

## Boundaries

**Always:** Set TTL, handle misses gracefully (None), atomic ops, test with/without encryption

**Never:** Change encryption without review, cache sensitive data unencrypted, log keys

## Performance

L1 < 0.1ms, L2 < 1ms, warmup < 5s/10k entries
