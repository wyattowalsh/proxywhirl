# Cache Subsystem Agent Guidelines

> Extends: [../../AGENTS.md](../../AGENTS.md)

Agent guidelines for the multi-tier caching subsystem.

## Overview

The cache subsystem provides high-performance, multi-tier caching with encryption support for proxy data and validation results.

## Module Structure

| File | Purpose | Key Classes |
|------|---------|-------------|
| `__init__.py` | Public exports | `CacheManager`, `CacheConfig` |
| `manager.py` | Main cache manager | `CacheManager` |
| `tiers.py` | Multi-tier implementation | `L1Cache`, `L2Cache`, tier logic |
| `crypto.py` | Encryption utilities | Key generation, encrypt/decrypt |
| `models.py` | Data models | `CacheEntry`, `CacheStatistics` |

## Quick Reference

```bash
# Run cache-specific tests
uv run pytest tests/unit/test_cache_*.py -v
uv run pytest tests/integration/test_cache_*.py -v

# Run cache benchmarks
uv run pytest tests/benchmarks/test_cache_performance.py --benchmark-only
```

## Key Patterns

### CacheManager Usage

```python
from proxywhirl.cache import CacheManager, CacheConfig

config = CacheConfig(
    l1_max_size=1000,
    l2_max_size=10000,
    default_ttl=300,
    encryption_enabled=True,
)

cache = CacheManager(config)

# Store and retrieve
await cache.set("key", value, ttl=60)
result = await cache.get("key")

# Statistics
stats = cache.get_statistics()
```

### Multi-Tier Architecture

```
┌─────────────────┐
│   L1 Cache      │  ← Fast, in-memory, limited size
│   (dict-based)  │
└────────┬────────┘
         │ miss
         ▼
┌─────────────────┐
│   L2 Cache      │  ← Larger, optional encryption
│   (LRU-based)   │
└────────┬────────┘
         │ miss
         ▼
┌─────────────────┐
│   Origin        │  ← Fetch from source
│   (ProxyFetcher)│
└─────────────────┘
```

## Boundaries

### Always Do

- Use TTL for all cache entries
- Handle cache misses gracefully
- Log cache statistics periodically
- Test with encryption enabled AND disabled

### Ask First

- Changing cache eviction policies
- Modifying L1/L2 size defaults
- Adding new cache tiers

### Never Touch

- Encryption key generation algorithm without security review
- Cache serialization format (breaks backwards compatibility)

## Test Coverage

```bash
# Unit tests
uv run pytest tests/unit/test_cache_manager.py -v
uv run pytest tests/unit/test_cache_tiers.py -v
uv run pytest tests/unit/test_cache_crypto.py -v
uv run pytest tests/unit/test_cache_ttl.py -v

# Integration tests
uv run pytest tests/integration/test_cache_*.py -v

# Property tests
uv run pytest tests/property/test_cache_properties.py -v
```

## Performance Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| L1 hit latency | < 0.1ms | `test_cache_performance.py` |
| L2 hit latency | < 1ms | `test_cache_performance.py` |
| Cache warmup | < 5s for 10k entries | `test_cache_warming.py` |
