# Quickstart Guide: Rate Limiting for Request Management

**Date**: 2025-11-02  
**Feature**: 013-rate-limiting-request  
**Purpose**: Quick reference for developers implementing and using rate limiting

## Overview

Rate limiting prevents service overload by enforcing request quotas per user/IP per time window. This guide covers:
- Basic setup and configuration
- Using rate limiting in your code
- Testing rate-limited endpoints
- Common patterns and troubleshooting

---

## Quick Setup (5 Minutes)

### 1. Install Dependencies

Rate limiting requires Redis for distributed state:

```bash
# Add Redis dependency (if not already present)
uv add redis>=5.0.0

# Or for async support
uv add aioredis>=2.0.0
```

### 2. Start Redis

```bash
# Using Docker
docker run -d -p 6379:6379 redis:7-alpine

# Or using local Redis
redis-server
```

### 3. Configure Rate Limits

Create `rate_limit_config.yaml`:

```yaml
enabled: true
default_tier: free
redis_enabled: true
fail_open: false

tiers:
  - name: free
    requests_per_window: 100
    window_size_seconds: 60
    endpoints:
      /api/v1/request: 50  # Stricter for expensive endpoint
    description: "Free tier - 100 req/min"
  
  - name: premium
    requests_per_window: 1000
    window_size_seconds: 60
    description: "Premium tier - 1000 req/min"
  
  - name: enterprise
    requests_per_window: 10000
    window_size_seconds: 60
    description: "Enterprise tier - 10k req/min"
```

### 4. Enable Middleware

In `proxywhirl/api.py`:

```python
from proxywhirl.rate_limit_middleware import RateLimitMiddleware
from proxywhirl.rate_limit_models import RateLimitConfig

# Load config
rate_limit_config = RateLimitConfig.from_yaml("rate_limit_config.yaml")

# Add middleware
app.add_middleware(
    RateLimitMiddleware,
    config=rate_limit_config
)
```

### 5. Test It

```bash
# Start API server
uv run uvicorn proxywhirl.api:app --reload

# Make requests (should work)
curl -i http://localhost:8000/api/v1/health

# Check headers
# X-RateLimit-Limit: 100
# X-RateLimit-Remaining: 99
# X-RateLimit-Reset: 1698825660
```

---

## Usage Examples

### Example 1: Basic Rate Limiting

```python
from proxywhirl import RateLimiter, RateLimitConfig

# Initialize
config = RateLimitConfig(
    enabled=True,
    tiers=[
        {"name": "free", "requests_per_window": 100, "window_size_seconds": 60}
    ]
)
limiter = RateLimiter(config)

# Check rate limit
result = await limiter.check(
    identifier="user-123",
    endpoint="/api/v1/request",
    tier="free"
)

if result.allowed:
    print(f"Request allowed. Remaining: {result.state.remaining}")
else:
    print(f"Rate limited! Retry in {result.state.retry_after_seconds}s")
```

### Example 2: Per-Endpoint Limits

```python
# Config with endpoint overrides
config = RateLimitConfig(
    tiers=[
        {
            "name": "free",
            "requests_per_window": 100,
            "window_size_seconds": 60,
            "endpoints": {
                "/api/v1/request": 50,      # Expensive endpoint
                "/api/v1/health": 1000       # Cheap endpoint
            }
        }
    ]
)

# Different endpoints have different limits
result1 = await limiter.check("user-123", "/api/v1/request", "free")
# limit = 50 (endpoint override)

result2 = await limiter.check("user-123", "/api/v1/health", "free")
# limit = 1000 (endpoint override)

result3 = await limiter.check("user-123", "/api/v1/pool", "free")
# limit = 100 (global tier limit)
```

### Example 3: Tiered Users

```python
# Premium user gets higher limits
result_premium = await limiter.check(
    identifier="premium-user",
    endpoint="/api/v1/request",
    tier="premium"  # 1000 req/min
)

# Free user gets lower limits
result_free = await limiter.check(
    identifier="free-user",
    endpoint="/api/v1/request",
    tier="free"  # 100 req/min (or 50 if endpoint override)
)
```

### Example 4: IP-Based Rate Limiting (Unauthenticated)

```python
# For unauthenticated requests, use IP address
client_ip = "192.168.1.100"

result = await limiter.check(
    identifier=client_ip,  # IP instead of user ID
    endpoint="/api/v1/health",
    tier="free"  # Default tier for unauthenticated
)
```

### Example 5: Whitelist Exemptions

```python
# Config with whitelist
config = RateLimitConfig(
    whitelist=["admin-user-123", "10.0.0.1"],  # Exempt from limits
    tiers=[...]
)

# Whitelisted users bypass rate limiting
result = await limiter.check("admin-user-123", "/api/v1/request", "free")
assert result.allowed  # Always True for whitelisted
```

---

## Testing

### Unit Test: Rate Limit Enforcement

```python
import pytest
from proxywhirl import RateLimiter, RateLimitConfig

@pytest.fixture
def limiter():
    config = RateLimitConfig(
        redis_enabled=False,  # Use in-memory for tests
        tiers=[
            {"name": "test", "requests_per_window": 10, "window_size_seconds": 60}
        ]
    )
    return RateLimiter(config)

@pytest.mark.asyncio
async def test_rate_limit_enforcement(limiter):
    """Test that 11th request is rate limited"""
    # Make 10 requests (allowed)
    for i in range(10):
        result = await limiter.check("user", "/test", "test")
        assert result.allowed, f"Request {i+1} should be allowed"
    
    # 11th request should be rate limited
    result = await limiter.check("user", "/test", "test")
    assert not result.allowed
    assert result.reason == "rate_limit_exceeded"
```

### Integration Test: HTTP 429 Response

```python
from fastapi.testclient import TestClient

def test_rate_limit_429_response(client: TestClient):
    """Test that exceeding limit returns 429"""
    # Make 101 requests (limit is 100)
    for _ in range(100):
        response = client.get("/api/v1/request")
        assert response.status_code == 200
    
    # 101st request should be rate limited
    response = client.get("/api/v1/request")
    assert response.status_code == 429
    assert "Retry-After" in response.headers
    
    body = response.json()
    assert body["error"]["code"] == "rate_limit_exceeded"
    assert body["error"]["details"]["limit"] == 100
```

### Property Test: Correctness

```python
from hypothesis import given, strategies as st
import time

@given(st.integers(min_value=1, max_value=1000))
def test_rate_limit_never_exceeds_limit(n_requests):
    """Property: No more than limit requests ever allowed in window"""
    limiter = RateLimiter(config)
    limit = 100
    
    allowed_count = 0
    for _ in range(n_requests):
        result = limiter.check_sync("user", "/test", "test")
        if result.allowed:
            allowed_count += 1
    
    assert allowed_count <= limit, "Rate limiter allowed too many requests"
```

---

## Configuration Reference

### Environment Variables

All configuration can be overridden via environment variables:

```bash
# Enable/disable rate limiting
export RATE_LIMIT_ENABLED=true

# Default tier for unauthenticated users
export RATE_LIMIT_DEFAULT_TIER=free

# Redis connection
export RATE_LIMIT_REDIS_URL=redis://localhost:6379/1
export RATE_LIMIT_REDIS_ENABLED=true

# Failure mode
export RATE_LIMIT_FAIL_OPEN=false  # Deny requests if Redis down

# Whitelist (comma-separated)
export RATE_LIMIT_WHITELIST=admin-user,10.0.0.1
```

### YAML Configuration

```yaml
# rate_limit_config.yaml
enabled: true
default_tier: free
redis_url: redis://localhost:6379/1
redis_enabled: true
fail_open: false
header_prefix: X-RateLimit-

whitelist:
  - admin-user-id
  - 10.0.0.1

tiers:
  - name: free
    requests_per_window: 100
    window_size_seconds: 60
    description: "Free tier"
    endpoints:
      /api/v1/request: 50
  
  - name: premium
    requests_per_window: 1000
    window_size_seconds: 60
    description: "Premium tier"
  
  - name: unlimited
    requests_per_window: 999999999
    window_size_seconds: 1
    description: "No limits"
```

### Programmatic Configuration

```python
from proxywhirl.rate_limit_models import RateLimitConfig, RateLimitTierConfig

config = RateLimitConfig(
    enabled=True,
    default_tier="free",
    redis_enabled=True,
    tiers=[
        RateLimitTierConfig(
            name="free",
            requests_per_window=100,
            window_size_seconds=60,
            endpoints={"/api/v1/request": 50}
        ),
        RateLimitTierConfig(
            name="premium",
            requests_per_window=1000,
            window_size_seconds=60
        )
    ]
)
```

---

## HTTP Headers Reference

### Request Headers (Optional)

| Header | Description | Example |
|--------|-------------|---------|
| `X-API-Key` | User authentication (determines tier) | `sk_live_abc123` |
| `Authorization` | JWT token (alternative auth) | `Bearer eyJ...` |

### Response Headers (All Requests)

| Header | Description | Example |
|--------|-------------|---------|
| `X-RateLimit-Limit` | Max requests in window | `100` |
| `X-RateLimit-Remaining` | Remaining requests | `42` |
| `X-RateLimit-Reset` | Reset time (Unix timestamp) | `1698825660` |
| `X-RateLimit-Tier` | User's tier | `free` |

### Response Headers (429 Only)

| Header | Description | Example |
|--------|-------------|---------|
| `Retry-After` | Seconds until retry | `59` |

---

## Troubleshooting

### Issue: All Requests Return 429

**Symptoms**: Every request is rate limited, even the first one.

**Possible Causes**:
1. **Redis key collision**: Check Redis key format
2. **Clock skew**: Ensure system time is correct
3. **Config error**: Verify `requests_per_window > 0`

**Solution**:
```bash
# Check Redis keys
redis-cli KEYS "ratelimit:*"

# Check system time
date -u

# Verify config
python -c "from proxywhirl.rate_limit_models import RateLimitConfig; print(RateLimitConfig.from_yaml('config.yaml'))"
```

### Issue: Rate Limits Not Persistent

**Symptoms**: Rate limits reset after server restart.

**Possible Causes**:
1. **In-memory mode**: `redis_enabled=False`
2. **Redis not running**: Connection failure falls back to in-memory
3. **Redis eviction**: Keys expired due to maxmemory policy

**Solution**:
```bash
# Enable Redis
export RATE_LIMIT_REDIS_ENABLED=true

# Check Redis connection
redis-cli PING

# Check Redis memory
redis-cli INFO memory
```

### Issue: 429 Responses Missing Headers

**Symptoms**: HTTP 429 but no `Retry-After` header.

**Possible Causes**:
1. **Middleware not configured**: Missing `app.add_middleware()`
2. **Custom exception handler**: Overriding default handler
3. **Middleware order**: Rate limit middleware after route handler

**Solution**:
```python
# Check middleware order (rate limit should be early)
app.add_middleware(RateLimitMiddleware)  # ← Before other middleware

# Verify exception handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        headers={
            "Retry-After": str(exc.retry_after_seconds),
            # ... other headers
        }
    )
```

### Issue: High Latency (>10ms)

**Symptoms**: Slow API responses, rate limit check takes >10ms.

**Possible Causes**:
1. **Redis network latency**: Redis on remote server
2. **Redis overload**: High CPU/memory usage
3. **Blocking operations**: Not using async Redis client

**Solution**:
```bash
# Check Redis latency
redis-cli --latency

# Use async Redis client
pip install aioredis

# Enable Redis pipelining (batch operations)
```

---

## Performance Tips

### 1. Use Local Redis

Deploy Redis on same host/container as API for <1ms latency:

```yaml
# docker-compose.yml
services:
  api:
    image: proxywhirl:latest
  redis:
    image: redis:7-alpine
    # Same network, local connection
```

### 2. Enable Connection Pooling

Reuse Redis connections (already done in `cache.py`):

```python
# In proxywhirl/rate_limiter.py
redis_pool = redis.ConnectionPool.from_url(
    config.redis_url,
    max_connections=50,
    decode_responses=False  # Binary for performance
)
```

### 3. Use Lua Scripts

Atomic operations reduce round-trips (already implemented):

```python
# Single Redis call instead of 4
result = redis.evalsha(script_sha, 1, key, now, window, limit, req_id)
```

### 4. Tune Window Size

Smaller windows = more Redis operations. Optimize for your use case:

- **High frequency**: 10-second windows, higher limits
- **Low frequency**: 60-second windows, lower limits
- **API Gateway**: 1-second windows, burst limits

---

## Monitoring

### Prometheus Metrics

Rate limiting exposes metrics at `/metrics`:

```python
# Counter: Total rate limit checks
proxywhirl_rate_limit_requests_total{tier="free", endpoint="/api/v1/request", status="allowed"} 14528

# Counter: Throttled requests
proxywhirl_rate_limit_throttled_total{tier="free", endpoint="/api/v1/request"} 892

# Histogram: Check latency
proxywhirl_rate_limit_check_duration_seconds_bucket{le="0.005"} 13500
```

### Grafana Dashboard

Query rate limiting metrics:

```promql
# Throttle rate by tier
rate(proxywhirl_rate_limit_throttled_total[5m]) 
/ 
rate(proxywhirl_rate_limit_requests_total[5m])

# P95 latency
histogram_quantile(0.95, 
  rate(proxywhirl_rate_limit_check_duration_seconds_bucket[5m])
)
```

### Log Output

Rate limit violations logged with structured data:

```json
{
  "level": "WARNING",
  "message": "Rate limit exceeded",
  "user_id": "user-123",
  "tier": "free",
  "endpoint": "/api/v1/request",
  "limit": 100,
  "current_count": 101,
  "window_start": "2025-11-02T10:00:00Z",
  "timestamp": "2025-11-02T10:01:30Z"
}
```

---

## Next Steps

1. **Read Full Spec**: [spec.md](../spec.md) for requirements
2. **Review API Contracts**: [contracts/api-contracts.md](./contracts/api-contracts.md)
3. **Implement Tests**: TDD workflow in tasks.md (Phase 2)
4. **Deploy**: Configure Redis, update API, monitor metrics

---

## Resources

- **Redis Documentation**: https://redis.io/docs/
- **FastAPI Middleware**: https://fastapi.tiangolo.com/advanced/middleware/
- **Rate Limiting Algorithms**: https://en.wikipedia.org/wiki/Rate_limiting
- **Sliding Window**: https://blog.cloudflare.com/counting-things-a-lot-of-different-things/
