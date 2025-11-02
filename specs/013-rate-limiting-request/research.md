# Research: Rate Limiting for Request Management

**Date**: 2025-11-02  
**Feature**: 013-rate-limiting-request  
**Purpose**: Resolve technical decisions and best practices for rate limiting implementation

## Research Tasks

### 1. Rate Limiting Algorithm Selection

**Decision**: Sliding Window Counter algorithm

**Rationale**:
- **Precision**: Sliding window provides more accurate rate limiting than fixed window by considering request timestamps within the window, preventing burst attacks at window boundaries
- **Performance**: O(1) time complexity using Redis sorted sets (ZADD + ZCOUNT + ZREMRANGEBYSCORE)
- **Memory**: Efficient - only stores timestamps within the active window, auto-expires old entries
- **Distributed**: Works correctly across multiple API instances with Redis as shared state
- **Industry Standard**: Used by Cloudflare, AWS API Gateway, Kong

**Alternatives Considered**:
1. **Fixed Window Counter**: Rejected - vulnerable to burst attacks at window boundaries (user can send 2x limit by splitting requests across adjacent windows)
2. **Token Bucket**: Rejected - more complex to implement, harder to reason about remaining quota, requires background token refill process
3. **Leaky Bucket**: Rejected - smooths traffic too aggressively, penalizes legitimate burst patterns (e.g., user refreshing dashboard)
4. **Sliding Window Log**: Rejected - high memory overhead (stores every request timestamp indefinitely)

**Implementation Details**:
- Redis sorted set key: `ratelimit:{user_id}:{endpoint}` (or `ratelimit:{ip}:{endpoint}` for unauthenticated)
- Score: Unix timestamp in milliseconds
- Value: Unique request ID (UUID)
- Algorithm:
  ```python
  now = time.time()
  window_start = now - window_size
  # Remove expired entries
  redis.zremrangebyscore(key, '-inf', window_start)
  # Count requests in current window
  count = redis.zcard(key)
  if count >= limit:
      return 429  # Rate limited
  # Add current request
  redis.zadd(key, {request_id: now})
  redis.expire(key, window_size * 2)  # Safety cleanup
  return 200
  ```

### 2. Redis vs In-Memory Storage

**Decision**: Redis primary, in-memory fallback

**Rationale**:
- **Distributed**: Multiple API instances need shared rate limit state (constitution requires horizontal scalability)
- **Persistence**: Redis RDB/AOF ensures rate limit windows survive restarts (FR-010, SC-004)
- **Atomic Operations**: Redis sorted set operations are atomic, preventing race conditions
- **TTL Support**: Automatic expiry of old rate limit windows reduces memory pressure
- **Performance**: Redis achieves <1ms latency for sorted set operations at scale

**Alternatives Considered**:
1. **In-Memory Only**: Rejected - fails in distributed deployments (each instance has independent state), loses state on restart
2. **SQLite**: Rejected - no built-in TTL, requires manual cleanup, slower than Redis for high-concurrency writes
3. **PostgreSQL**: Rejected - overkill for ephemeral state, higher latency than Redis, no native TTL
4. **Memcached**: Rejected - no sorted set support, counter-based approach is less accurate

**Implementation Details**:
- Use existing `cache.py` Redis connection pool (005-caching-mechanisms-storage)
- Fallback to `collections.defaultdict` for single-instance testing (pytest)
- Configuration: `RATE_LIMIT_REDIS_URL` env var (default: `redis://localhost:6379/1`)
- Error handling: If Redis unavailable, optionally fail open (allow requests) or fail closed (deny requests) based on `RATE_LIMIT_FAIL_OPEN` setting

### 3. FastAPI Middleware Integration

**Decision**: Custom async middleware with dependency injection

**Rationale**:
- **Transparency**: Middleware runs before all route handlers, ensuring consistent enforcement
- **Separation of Concerns**: Rate limiting logic decoupled from business logic
- **Performance**: Async middleware doesn't block event loop (<5ms overhead per SC-002)
- **Testability**: Middleware can be tested independently from API routes
- **FastAPI Native**: Uses starlette.middleware.base for proper ASGI integration

**Alternatives Considered**:
1. **Decorator Pattern** (`@rate_limit(100, 60)`): Rejected - requires decorating every route, easy to forget, inconsistent enforcement
2. **Dependency Injection Only** (`Depends(check_rate_limit)`): Rejected - must add to every route, verbose, no automatic header injection
3. **Third-Party Library** (slowapi): Considered - good but adds dependency, less control over Redis integration, harder to customize for tiers
4. **API Gateway** (Nginx, Kong): Rejected - adds deployment complexity, requires external configuration, harder to test

**Implementation Details**:
- Middleware processes requests in order: auth → rate limit → route handler
- Extract user identifier from: (1) API key header, (2) JWT token, (3) IP address (fallback)
- Inject rate limit headers into response: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- For 429 responses, add `Retry-After` header (seconds until window resets)
- Integration point: `app.add_middleware(RateLimitMiddleware)` in `api.py`

### 4. Tiered Rate Limiting Configuration

**Decision**: Pydantic Settings with YAML/JSON file + environment variable overrides

**Rationale**:
- **Type Safety**: Pydantic validates tier configs at startup, catching errors early
- **Flexibility**: Supports environment variables for container deployments (12-factor app)
- **Hot Reload**: Can reload config without restart by watching file changes (FR-014)
- **Documentation**: Pydantic auto-generates JSON schema for configuration
- **Existing Pattern**: Aligns with existing ProxyWhirl config system (config.py)

**Alternatives Considered**:
1. **Database Storage**: Rejected - adds latency to every request, requires migrations, overkill for mostly-static config
2. **Hardcoded Tiers**: Rejected - inflexible, requires code changes to adjust limits
3. **CLI Arguments**: Rejected - too verbose for multiple tiers/endpoints, harder to manage
4. **Environment Variables Only**: Rejected - difficult to express complex nested config (per-endpoint limits)

**Implementation Details**:
```python
class RateLimitTierConfig(BaseModel):
    name: str  # "free", "premium", "enterprise", "unlimited"
    requests_per_window: int  # e.g., 100
    window_size_seconds: int  # e.g., 60
    endpoints: Dict[str, int] = {}  # endpoint-specific overrides

class RateLimitConfig(BaseSettings):
    enabled: bool = True
    default_tier: str = "free"
    tiers: List[RateLimitTierConfig]
    redis_url: SecretStr = "redis://localhost:6379/1"
    fail_open: bool = False  # Allow requests if Redis down
    
    class Config:
        env_file = ".env"
        env_prefix = "RATE_LIMIT_"
```

Example YAML:
```yaml
rate_limit:
  enabled: true
  default_tier: free
  tiers:
    - name: free
      requests_per_window: 100
      window_size_seconds: 60
      endpoints:
        /api/v1/request: 50  # Stricter for expensive endpoint
    - name: premium
      requests_per_window: 1000
      window_size_seconds: 60
    - name: enterprise
      requests_per_window: 10000
      window_size_seconds: 60
    - name: unlimited
      requests_per_window: 999999999
      window_size_seconds: 1
```

### 5. Per-Endpoint Rate Limiting Strategy

**Decision**: Hierarchical limit application (most restrictive wins)

**Rationale**:
- **Intuitive**: Admin expects "per-endpoint limit overrides global limit if stricter"
- **Protection**: Prevents expensive endpoints from being abused even by high-tier users
- **Flexibility**: Can relax limits on cheap endpoints (health checks) while restricting expensive ones (proxied requests)
- **Composition**: Allows mixing global, tier, and endpoint limits naturally

**Alternatives Considered**:
1. **Endpoint-Only Limits**: Rejected - must configure every endpoint explicitly, no sensible defaults
2. **Additive Limits** (global + endpoint): Rejected - confusing math, users expect override behavior
3. **Separate Limit Pools**: Rejected - complexity, users must understand multiple quota types

**Implementation Details**:
- Limit precedence: `min(endpoint_limit, tier_limit, global_limit)`
- Example: Free tier has 100 req/min global, but `/api/v1/request` has 50 req/min override
  - User hits 50 requests to `/api/v1/request` → rate limited
  - User hits 100 requests to `/api/v1/health` (no override) → rate limited
- Configuration: Endpoint limits stored in `RateLimitTierConfig.endpoints` dict
- Middleware logic:
  ```python
  global_limit = tier_config.requests_per_window
  endpoint_limit = tier_config.endpoints.get(endpoint_path, global_limit)
  effective_limit = min(global_limit, endpoint_limit)
  ```

### 6. Rate Limit Metrics and Observability

**Decision**: Prometheus metrics + structured logging (integrate with 008-metrics-observability-performance)

**Rationale**:
- **Existing Infrastructure**: 008-metrics already provides Prometheus integration
- **Standard Metrics**: Counter for throttled requests, histogram for enforcement latency
- **Alerting**: Prometheus AlertManager can notify on-call when throttle rate exceeds threshold
- **Grafana Dashboard**: Visualize throttle rates by endpoint, tier, time window
- **Structured Logs**: Loguru integration (already in dependencies) for detailed audit trail

**Alternatives Considered**:
1. **Custom Metrics System**: Rejected - reinventing the wheel, incompatible with existing monitoring
2. **Database Logging Only**: Rejected - high write volume, difficult to query/aggregate
3. **No Metrics**: Rejected - violates FR-012, SC-007 (metrics requirement)

**Implementation Details**:
- Metrics:
  ```python
  rate_limit_requests_total = Counter('proxywhirl_rate_limit_requests_total', 
      'Total rate limit checks', ['tier', 'endpoint', 'status'])
  rate_limit_throttled_total = Counter('proxywhirl_rate_limit_throttled_total',
      'Total throttled requests', ['tier', 'endpoint', 'reason'])
  rate_limit_check_duration_seconds = Histogram('proxywhirl_rate_limit_check_duration_seconds',
      'Rate limit check latency', ['tier', 'endpoint'])
  ```
- Structured logs (Loguru):
  ```python
  logger.warning("Rate limit exceeded", 
      user_id=user_id, tier=tier, endpoint=endpoint, 
      limit=limit, current_count=count, window_start=window_start)
  ```
- Integration: Import metrics from `metrics_collector.py` (008) if available, gracefully degrade if not

### 7. Sliding Window Implementation with Redis

**Decision**: Redis Sorted Sets with atomic Lua scripting

**Rationale**:
- **Atomicity**: Lua script runs atomically on Redis server, preventing race conditions
- **Efficiency**: Single round-trip to Redis instead of multiple ZREMRANGEBYSCORE + ZADD + ZCARD commands
- **Correctness**: Guarantees "check-then-increment" is atomic (critical for SC-008: zero false positives)
- **Performance**: Redis Lua execution is highly optimized, <1ms for typical workloads

**Alternatives Considered**:
1. **Pipeline Commands**: Rejected - not atomic, race conditions possible in high concurrency
2. **WATCH/MULTI/EXEC**: Rejected - optimistic locking causes retries, higher latency
3. **Application-Level Locking**: Rejected - distributed locks add complexity, latency, failure modes

**Implementation Details**:
Lua script stored in `rate_limiter.py`:
```lua
-- KEYS[1] = rate limit key (e.g., "ratelimit:user123:/api/v1/request")
-- ARGV[1] = current timestamp (ms)
-- ARGV[2] = window size (seconds)
-- ARGV[3] = rate limit (max requests)
-- ARGV[4] = request ID (UUID)

local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2]) * 1000  -- Convert to ms
local limit = tonumber(ARGV[3])
local request_id = ARGV[4]

-- Remove expired entries (older than window start)
local window_start = now - window
redis.call('ZREMRANGEBYSCORE', key, '-inf', window_start)

-- Count current requests in window
local count = redis.call('ZCARD', key)

-- Check if limit exceeded
if count >= limit then
    return {0, count, limit}  -- Throttled
end

-- Add current request
redis.call('ZADD', key, now, request_id)

-- Set expiry (2x window size for safety)
redis.call('EXPIRE', key, window * 2 / 1000)

-- Return success with updated count
return {1, count + 1, limit}  -- Allowed
```

Python integration:
```python
script_sha = redis.script_load(lua_script)
result = redis.evalsha(script_sha, 1, key, now_ms, window_sec, limit, request_id)
allowed, current_count, limit = result
if not allowed:
    raise RateLimitExceeded(...)
```

### 8. Testing Strategy for Correctness

**Decision**: Property-based testing with Hypothesis + time-travel mocking

**Rationale**:
- **Correctness**: SC-008 requires zero false positives - property tests validate invariants
- **Edge Cases**: Hypothesis discovers boundary conditions (window edges, concurrent requests)
- **Regression**: Failed test cases become regression tests automatically
- **Time Control**: `freezegun` or `time-machine` allows testing window expiry without waiting

**Alternatives Considered**:
1. **Manual Test Cases Only**: Rejected - can't cover all edge cases, misses subtle race conditions
2. **Chaos Testing**: Rejected - too heavyweight for unit tests, belongs in integration/load testing
3. **Formal Verification**: Rejected - overkill, requires specialized tools

**Implementation Details**:
Property test invariants:
```python
@given(st.lists(st.floats(min_value=0, max_value=120), min_size=1))
def test_rate_limit_correctness(request_times):
    """Property: No more than N requests allowed in any W-second window"""
    limit = 10
    window = 60
    
    for t in sorted(request_times):
        with freeze_time(t):
            result = rate_limiter.check(user_id, endpoint)
            # Count requests in [t-window, t]
            recent = [r for r in request_times if t - window <= r <= t]
            if len(recent) < limit:
                assert result.allowed
            else:
                assert not result.allowed
```

Integration tests with `fakeredis`:
```python
def test_concurrent_requests_no_overcommit():
    """Test that concurrent requests don't exceed limit"""
    limit = 100
    tasks = [rate_limiter.check_async(user_id, endpoint) for _ in range(200)]
    results = await asyncio.gather(*tasks)
    allowed_count = sum(1 for r in results if r.allowed)
    assert allowed_count == limit  # Exactly limit allowed
```

## Summary

**Key Decisions**:
1. Sliding window counter algorithm (accuracy + performance)
2. Redis primary storage with in-memory fallback (distributed + persistent)
3. FastAPI async middleware (transparency + performance)
4. Pydantic Settings with YAML config (type safety + flexibility)
5. Hierarchical limit precedence (intuitive + protective)
6. Prometheus metrics + Loguru logs (existing infrastructure)
7. Atomic Lua scripting (correctness + efficiency)
8. Property-based testing (SC-008 zero false positives)

**No Further Clarifications Needed**: All technical decisions resolved.

**Ready for Phase 1**: Data model and contract generation.
