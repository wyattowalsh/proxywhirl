---
title: Performance Tuning
---

# Performance Tuning Guide

## Overview

This guide covers optimization techniques for ProxyWhirl in production environments, focusing on latency, throughput, and resource utilization.

## Caching Strategy Optimization

### Multi-Tier Cache Configuration

```python
from proxywhirl import ProxyWhirl, CacheConfig

config = ProxyWhirl.ProxyConfiguration(
    cache=CacheConfig(
        l1_size=100,           # In-memory fast cache
        l2_size=1000,          # Disk-backed larger cache
        l3_enabled=True,       # Remote cache (Redis, etc.)
        ttl_seconds=3600,      # Cache validity period
        encryption=True        # L2/L3 encryption
    )
)
```

### Cache Hit Optimization

- **L1 Cache**: Fast memory (100-500 proxies) for high-frequency requests
- **L2 Cache**: Persistent disk cache (1000+ proxies) for recovery
- **L3 Cache**: Distributed cache for multi-instance deployments

## Strategy Performance Characteristics

| Strategy | CPU | Memory | Latency | Best For |
|----------|-----|--------|---------|----------|
| RoundRobin | ⭐ | ⭐ | ⭐⭐ | Uniform load |
| Weighted | ⭐⭐ | ⭐ | ⭐⭐ | Heterogeneous proxies |
| PerformanceBased | ⭐⭐⭐ | ⭐⭐ | ⭐ | Latency-sensitive |
| Random | ⭐ | ⭐ | ⭐⭐⭐ | Unpredictable patterns |
| CostAware | ⭐⭐ | ⭐ | ⭐⭐ | Budget-constrained |

## Connection Pooling

### Optimal Pool Sizes

```python
# For concurrent requests (n workers)
pool_size = min(n_workers * 2, len(healthy_proxies))

# With circuit breaker
pool_size = int(len(proxies) * healthy_ratio * 0.8)
```

### Connection Reuse

```python
import httpx
from proxywhirl import ProxyWhirl

whirl = ProxyWhirl(config)

# Reuse httpx client for connection pooling
async with httpx.AsyncClient(limits=httpx.Limits(
    max_keepalive_connections=20,
    max_connections=40
)) as client:
    for _ in range(1000):
        proxy = whirl.get()
        response = await client.get(url, proxies=proxy.to_url())
```

## Batch Operations

### Efficient Proxy Rotation

```python
# Poor: Creates new proxy object each iteration
for i in range(1000):
    proxy = whirl.get()
    # ... use proxy

# Better: Batch fetch with strategy
proxies = whirl.get_multiple(n=100)
for proxy in proxies:
    # ... use proxy
```

## Monitoring & Profiling

### Key Metrics

```python
from proxywhirl.metrics_collector import MetricsCollector

metrics = MetricsCollector()
print(f"Cache hit rate: {metrics.cache_hit_rate}")
print(f"Avg selection latency: {metrics.avg_selection_latency_ms}ms")
print(f"Strategy distribution: {metrics.strategy_distribution}")
```

### Performance Profiling

```bash
# Profile with Python's cProfile
python -m cProfile -s cumtime -m pytest tests/benchmark/

# Memory profiling
python -m memory_profiler proxywhirl/rotator.py

# Async profiling
python -m asyncio --debug proxywhirl/async_rotator.py
```

## Common Bottlenecks & Solutions

| Bottleneck | Symptom | Solution |
|-----------|---------|----------|
| Cache thrashing | High L1 miss rate | Increase L1/L2 size or TTL |
| Strategy overhead | High CPU% | Switch to RoundRobin or Random |
| Network latency | Slow response times | Use PerformanceBased strategy |
| Lock contention | Serialization delays | Use AsyncProxyWhirl |

## Database Tuning

### SQLite Optimizations

```python
# In config.py or environment
PROXYWHIRL_STORAGE_PATH = "file:proxywhirl.db?mode=rwc&cache=shared"

# Enable WAL mode for concurrent access
import sqlite3
conn = sqlite3.connect("proxywhirl.db")
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA synchronous=NORMAL")
```

## Scaling Strategies

### Horizontal Scaling

- Use Redis for L3 cache in multi-instance setups
- Use MCP server for load-balanced proxy distribution
- Implement consistent hashing for proxy selection across instances

### Vertical Scaling

- Increase cache sizes proportionally to memory
- Use ProcessPoolExecutor for CPU-bound operations
- Tune async worker pool sizes

## Benchmarking

### Running Benchmarks

```bash
# Unit benchmarks
uv run pytest tests/benchmarks/ -v --benchmark-only

# Custom benchmark
python -c "
import timeit
from proxywhirl import ProxyWhirl

whirl = ProxyWhirl()
t = timeit.timeit(lambda: whirl.get(), number=10000)
print(f'10000 selections in {t:.2f}s ({10000/t:.0f} ops/sec)')
"
```

## Production Checklist

- [ ] Cache configured with appropriate L1/L2/L3 sizes
- [ ] Strategy choice validated for workload patterns
- [ ] Connection pooling enabled in HTTP client
- [ ] Monitoring metrics collected and dashboarded
- [ ] Performance profiling completed and bottlenecks identified
- [ ] Database indexes optimized
- [ ] Circuit breaker tuned for failure patterns
- [ ] Retry policy configured for flaky sources

See also: [Caching Guide](./caching.md), [Retry & Failover](./retry-failover.md)
