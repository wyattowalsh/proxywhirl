# Rate Limiting Configuration Guide

## Overview

ProxyWhirl includes token bucket rate limiting to prevent request flooding.

## Basic Configuration

```python
from proxywhirl import RateLimiter

limiter = RateLimiter(
    requests_per_second=10,
    burst_size=20
)
```

## Configuration Examples

### Low Rate Limit (Conservative)
```python
limiter = RateLimiter(
    requests_per_second=1,
    burst_size=5
)
```

### High Rate Limit (Aggressive)
```python
limiter = RateLimiter(
    requests_per_second=100,
    burst_size=500
)
```

### Per-Source Rate Limiting

```python
from proxywhirl import RateLimitConfig

config = RateLimitConfig(
    per_source_limits={
        'source1': {'rps': 5, 'burst': 10},
        'source2': {'rps': 10, 'burst': 20}
    }
)
```

## Usage Patterns

### Check Before Request

```python
if limiter.is_allowed():
    proxy = rotator.get_proxy()
else:
    # Wait or use fallback
    time.sleep(0.1)
    proxy = rotator.get_proxy()
```

### Wait Until Allowed

```python
limiter.wait_until_allowed()
proxy = rotator.get_proxy()
```

### Batch Requests

```python
proxies = []
for i in range(10):
    limiter.wait_until_allowed()
    proxy = rotator.get_proxy()
    proxies.append(proxy)
```

## Advanced Tuning

### Adaptive Rate Limiting

```python
from proxywhirl import AdaptiveRateLimiter

limiter = AdaptiveRateLimiter(
    initial_rps=10,
    min_rps=1,
    max_rps=100,
    adjust_interval=60
)
```

### Distributed Rate Limiting

```python
from proxywhirl import DistributedRateLimiter

limiter = DistributedRateLimiter(
    redis_url='redis://localhost:6379',
    requests_per_second=100
)
```

## Monitoring

```python
stats = limiter.get_statistics()
print(f"Allowed: {stats.allowed_count}")
print(f"Rejected: {stats.rejected_count}")
print(f"Queue time: {stats.avg_queue_time}s")
```

