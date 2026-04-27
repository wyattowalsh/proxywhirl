# Performance Optimization & Tuning

## Application Tuning

### Connection Pools
```python
DATABASE_POOL_SIZE = 20  # connections
DATABASE_POOL_TIMEOUT = 30  # seconds
REDIS_POOL_SIZE = 50
```

### Caching Strategy
```
L1 Cache (in-memory): 100ms TTL for frequently accessed proxies
L2 Cache (Redis): 5min TTL for proxy lists
L3 Cache (S3): Backup cache for persistence
```

### Async Optimization
```python
# Use asyncio for I/O-bound operations
async with httpx.AsyncClient() as client:
    tasks = [client.get(url) for url in proxy_urls]
    results = await asyncio.gather(*tasks)
```

## Database Tuning

### Indexes
```sql
-- High-cardinality columns
CREATE INDEX idx_proxy_last_check ON proxies(last_check_time DESC);
CREATE INDEX idx_session_created ON sessions(created_at DESC);

-- Composite indexes for common queries
CREATE INDEX idx_health_status ON proxies(health_status, last_check_time);
```

### Query Optimization
```
- Use EXPLAIN ANALYZE before optimizing
- Avoid SELECT * (specify columns)
- Use prepared statements
- Batch operations (INSERT...SELECT)
```

## Infrastructure Scaling

### Horizontal
- Add more API instances (load balanced)
- Add more database replicas (read-only)
- Partition proxy data by region

### Vertical
- Increase container/instance resources
- Upgrade to faster storage (NVMe)
- Increase buffer pools

## Benchmarking

```bash
# Load test
wrk -t4 -c100 -d30s http://api.proxywhirl.local/proxies

# Database benchmark
pgbench -U proxywhirl -d proxywhirl -r -T 60
```
