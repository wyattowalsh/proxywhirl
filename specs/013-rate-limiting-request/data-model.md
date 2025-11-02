# Data Model: Rate Limiting for Request Management

**Date**: 2025-11-02  
**Feature**: 013-rate-limiting-request  
**Purpose**: Define entities, relationships, and validation rules for rate limiting

## Core Entities

### 1. RateLimitConfig

**Purpose**: Configuration for rate limiting system (global and per-tier settings)

**Attributes**:
- `enabled: bool` - Whether rate limiting is enabled globally (default: True)
- `default_tier: str` - Default tier name for unauthenticated users (default: "free")
- `tiers: List[RateLimitTierConfig]` - List of tier configurations
- `redis_url: SecretStr` - Redis connection URL (default: "redis://localhost:6379/1")
- `redis_enabled: bool` - Whether to use Redis (default: True, fallback: in-memory)
- `fail_open: bool` - Allow requests if Redis unavailable (default: False)
- `header_prefix: str` - Prefix for rate limit headers (default: "X-RateLimit-")
- `whitelist: List[str]` - User IDs or IPs exempt from rate limiting (default: [])

**Validation Rules**:
- `default_tier` must exist in `tiers` list
- `tiers` must not be empty
- `redis_url` must be valid Redis URL if `redis_enabled=True`
- `whitelist` entries must be valid user IDs (UUIDs) or IP addresses (IPv4/IPv6)

**Source**: FR-001, FR-014 (configurable limits, runtime updates)

**Pydantic Model**:
```python
class RateLimitConfig(BaseSettings):
    enabled: bool = True
    default_tier: str = "free"
    tiers: List[RateLimitTierConfig]
    redis_url: SecretStr = SecretStr("redis://localhost:6379/1")
    redis_enabled: bool = True
    fail_open: bool = False
    header_prefix: str = "X-RateLimit-"
    whitelist: List[str] = Field(default_factory=list)
    
    @field_validator("default_tier")
    @classmethod
    def validate_default_tier(cls, v: str, info: ValidationInfo) -> str:
        if "tiers" in info.data:
            tier_names = [t.name for t in info.data["tiers"]]
            if v not in tier_names:
                raise ValueError(f"default_tier '{v}' not found in tiers")
        return v
    
    @field_validator("whitelist")
    @classmethod
    def validate_whitelist_entries(cls, v: List[str]) -> List[str]:
        for entry in v:
            # Validate UUID or IP address
            try:
                uuid.UUID(entry)
            except ValueError:
                try:
                    ipaddress.ip_address(entry)
                except ValueError:
                    raise ValueError(f"Invalid whitelist entry: {entry}")
        return v
    
    class Config:
        env_file = ".env"
        env_prefix = "RATE_LIMIT_"
```

---

### 2. RateLimitTierConfig

**Purpose**: Configuration for a single tier (free, premium, enterprise, unlimited)

**Attributes**:
- `name: str` - Tier identifier (e.g., "free", "premium", "enterprise")
- `requests_per_window: int` - Maximum requests allowed in time window
- `window_size_seconds: int` - Time window size in seconds (e.g., 60 for 1 minute)
- `endpoints: Dict[str, int]` - Per-endpoint limit overrides (endpoint path → limit)
- `description: str` - Human-readable tier description (optional)

**Validation Rules**:
- `name` must be non-empty, alphanumeric + underscore (no spaces)
- `requests_per_window` must be positive integer
- `window_size_seconds` must be positive integer (1-3600 range)
- `endpoints` keys must start with "/" (valid API paths)
- `endpoints` values must be positive integers <= `requests_per_window`

**Source**: FR-006, FR-007 (tiered limits, per-endpoint limits)

**Pydantic Model**:
```python
class RateLimitTierConfig(BaseModel):
    name: str = Field(..., pattern=r"^[a-z0-9_]+$")
    requests_per_window: int = Field(..., gt=0)
    window_size_seconds: int = Field(..., ge=1, le=3600)
    endpoints: Dict[str, int] = Field(default_factory=dict)
    description: str = ""
    
    @field_validator("endpoints")
    @classmethod
    def validate_endpoints(cls, v: Dict[str, int], info: ValidationInfo) -> Dict[str, int]:
        global_limit = info.data.get("requests_per_window", 0)
        for path, limit in v.items():
            if not path.startswith("/"):
                raise ValueError(f"Endpoint path must start with '/': {path}")
            if limit <= 0:
                raise ValueError(f"Endpoint limit must be positive: {path}")
            # Note: Endpoint limits CAN be stricter (lower) than tier limits (FR-008: most restrictive wins)
            # Validation only ensures positive values and valid paths
        return v
```

---

### 3. RateLimitState

**Purpose**: Tracks current rate limit state for a user/IP + endpoint combination

**Attributes**:
- `key: str` - Rate limit key (format: "ratelimit:{identifier}:{endpoint}")
- `identifier: str` - User ID (UUID) or IP address
- `endpoint: str` - API endpoint path (e.g., "/api/v1/request")
- `tier: str` - User's tier name (e.g., "free", "premium")
- `current_count: int` - Number of requests in current window
- `limit: int` - Maximum requests allowed in window
- `window_start_ms: int` - Window start timestamp (Unix ms)
- `window_size_seconds: int` - Window size in seconds
- `reset_at: datetime` - When rate limit resets (window_start + window_size)

**Validation Rules**:
- `identifier` must be valid UUID or IP address
- For unauthenticated requests, extract client IP using priority order: (1) X-Forwarded-For header (first IP if comma-separated), (2) X-Real-IP header, (3) request.client.host (direct connection)
- `endpoint` must start with "/"
- `current_count` must be non-negative
- `limit` must be positive
- `window_start_ms` must be valid Unix timestamp (milliseconds)
- `window_size_seconds` must be positive

**Source**: FR-004, FR-005 (per-user, per-IP tracking)

**Pydantic Model**:
```python
class RateLimitState(BaseModel):
    key: str
    identifier: str
    endpoint: str
    tier: str
    current_count: int = Field(..., ge=0)
    limit: int = Field(..., gt=0)
    window_start_ms: int = Field(..., gt=0)
    window_size_seconds: int = Field(..., gt=0)
    reset_at: datetime
    
    @computed_field
    @property
    def remaining(self) -> int:
        """Remaining requests in current window"""
        return max(0, self.limit - self.current_count)
    
    @computed_field
    @property
    def is_exceeded(self) -> bool:
        """Whether rate limit is exceeded"""
        return self.current_count >= self.limit
    
    @computed_field
    @property
    def retry_after_seconds(self) -> int:
        """Seconds until rate limit resets"""
        now = datetime.now(timezone.utc)
        delta = (self.reset_at - now).total_seconds()
        return max(0, int(delta))
```

---

### 4. RateLimitResult

**Purpose**: Result of a rate limit check operation

**Attributes**:
- `allowed: bool` - Whether request is allowed (not rate limited)
- `state: RateLimitState` - Current rate limit state
- `reason: Optional[str]` - Reason for denial (if not allowed)

**Validation Rules**:
- If `allowed=False`, `reason` must be non-empty

**Source**: FR-002, FR-003 (HTTP 429 responses, Retry-After header)

**Pydantic Model**:
```python
class RateLimitResult(BaseModel):
    allowed: bool
    state: RateLimitState
    reason: Optional[str] = None
    
    @model_validator(mode="after")
    def validate_reason(self) -> "RateLimitResult":
        if not self.allowed and not self.reason:
            raise ValueError("reason required when allowed=False")
        return self
```

---

### 5. RateLimitMetrics

**Purpose**: Aggregated metrics for rate limiting activity

**Attributes**:
- `total_requests: int` - Total rate limit checks performed
- `throttled_requests: int` - Total requests throttled (429 responses)
- `allowed_requests: int` - Total requests allowed
- `by_tier: Dict[str, int]` - Throttled requests by tier
- `by_endpoint: Dict[str, int]` - Throttled requests by endpoint
- `avg_check_latency_ms: float` - Average rate limit check latency (milliseconds)
- `p95_check_latency_ms: float` - P95 rate limit check latency
- `redis_errors: int` - Redis connection/operation errors

**Validation Rules**:
- All counts must be non-negative
- `throttled_requests + allowed_requests == total_requests`
- Latencies must be non-negative

**Source**: FR-012, SC-007 (metrics exposition)

**Pydantic Model**:
```python
class RateLimitMetrics(BaseModel):
    total_requests: int = Field(..., ge=0)
    throttled_requests: int = Field(..., ge=0)
    allowed_requests: int = Field(..., ge=0)
    by_tier: Dict[str, int] = Field(default_factory=dict)
    by_endpoint: Dict[str, int] = Field(default_factory=dict)
    avg_check_latency_ms: float = Field(..., ge=0.0)
    p95_check_latency_ms: float = Field(..., ge=0.0)
    redis_errors: int = Field(..., ge=0)
    
    @model_validator(mode="after")
    def validate_totals(self) -> "RateLimitMetrics":
        if self.throttled_requests + self.allowed_requests != self.total_requests:
            raise ValueError("throttled + allowed must equal total")
        return self
```

---

## Entity Relationships

```
RateLimitConfig (1)
  └── contains ──> (N) RateLimitTierConfig

RateLimitTierConfig (1)
  └── defines limits for ──> (N) RateLimitState

RateLimitState (1)
  └── produced by rate limit check ──> (1) RateLimitResult

RateLimitMetrics (aggregates)
  └── tracks ──> (N) RateLimitResult
```

**Key Relationships**:
- **One-to-Many**: One `RateLimitConfig` contains multiple `RateLimitTierConfig` instances
- **Hierarchy**: `RateLimitState` determines effective limit by applying tier + endpoint overrides
- **Aggregation**: `RateLimitMetrics` aggregates multiple `RateLimitResult` outcomes

---

## State Transitions

### RateLimitState Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                     Rate Limit State                        │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ First request in window
                           ▼
                    ┌─────────────┐
                    │  NEW STATE  │
                    │ count = 1   │
                    │ reset_at =  │
                    │  now + W    │
                    └─────────────┘
                           │
                           │ Within window, count < limit
                           ▼
                    ┌─────────────┐
                    │   ACTIVE    │
                    │ count += 1  │
                    │ allowed=true│
                    └─────────────┘
                           │
                           │ count >= limit
                           ▼
                    ┌─────────────┐
                    │  EXCEEDED   │
                    │ allowed=    │
                    │   false     │
                    │ HTTP 429    │
                    └─────────────┘
                           │
                           │ Window expires (now >= reset_at)
                           ▼
                    ┌─────────────┐
                    │   EXPIRED   │
                    │ Redis ZREM  │
                    │  old entries│
                    └─────────────┘
                           │
                           │ Next request starts new window
                           ▼
                    ┌─────────────┐
                    │  NEW STATE  │
                    │  (cycle)    │
                    └─────────────┘
```

**Transitions**:
1. **NEW → ACTIVE**: First request creates state, increments count to 1
2. **ACTIVE → ACTIVE**: Subsequent requests increment count (if < limit)
3. **ACTIVE → EXCEEDED**: Count reaches limit, requests denied with 429
4. **EXCEEDED → EXCEEDED**: Additional requests continue to be denied
5. **EXCEEDED → EXPIRED**: Window expires (time >= reset_at)
6. **EXPIRED → NEW**: Next request starts fresh window

---

## Validation Rules Summary

| Entity | Rule | Source |
|--------|------|--------|
| RateLimitConfig | `default_tier` must exist in `tiers` | FR-006 |
| RateLimitConfig | `whitelist` must be valid UUIDs or IPs | FR-015 |
| RateLimitTierConfig | `name` must be alphanumeric + underscore | FR-006 |
| RateLimitTierConfig | `requests_per_window` must be positive | FR-001 |
| RateLimitTierConfig | `window_size_seconds` in range [1, 3600] | FR-001 |
| RateLimitTierConfig | Endpoint limits ≤ tier limit | FR-008 |
| RateLimitState | `identifier` must be UUID or IP | FR-004, FR-005 |
| RateLimitState | `current_count` ≥ 0, `limit` > 0 | FR-001 |
| RateLimitResult | `reason` required if not allowed | FR-002 |
| RateLimitMetrics | `throttled + allowed == total` | FR-012 |

---

## Storage Schema

### Redis Keys

**Format**: `ratelimit:{identifier}:{endpoint}`

**Examples**:
- `ratelimit:550e8400-e29b-41d4-a716-446655440000:/api/v1/request`
- `ratelimit:192.168.1.100:/api/v1/health`

**Data Structure**: Redis Sorted Set
- **Score**: Unix timestamp (milliseconds) when request occurred
- **Value**: Request ID (UUID4) for uniqueness
- **TTL**: 2x window size (automatic cleanup)

**Operations**:
- `ZADD`: Add request timestamp
- `ZREMRANGEBYSCORE`: Remove expired entries
- `ZCARD`: Count requests in window
- `EXPIRE`: Set key TTL

**Example Redis State**:
```
ratelimit:user123:/api/v1/request → SortedSet {
    "req-001": 1698825600000,  # Timestamp 1
    "req-002": 1698825601000,  # Timestamp 2
    ...
    "req-100": 1698825659000   # Timestamp 100
}
TTL: 120 seconds
```

---

## Example Scenarios

### Scenario 1: Free Tier User Hits Global Limit

**Initial State**:
- User: `550e8400-e29b-41d4-a716-446655440000` (free tier)
- Endpoint: `/api/v1/request`
- Tier Config: 100 req/min, no endpoint overrides

**Sequence**:
1. User makes 100th request at `t=0s`
   - Redis: `ZCARD` returns 99
   - Action: `ZADD` request, return 200 OK
   - Headers: `X-RateLimit-Remaining: 0`, `X-RateLimit-Reset: 60`

2. User makes 101st request at `t=1s`
   - Redis: `ZCARD` returns 100
   - Action: Return 429 Too Many Requests
   - Headers: `Retry-After: 59`

3. User waits until `t=61s` (window expires)
   - Redis: `ZREMRANGEBYSCORE` removes old entries
   - Action: New request allowed, fresh window starts

---

### Scenario 2: Premium User with Per-Endpoint Override

**Initial State**:
- User: `premium-user-001` (premium tier)
- Endpoint: `/api/v1/request`
- Tier Config: 1000 req/min global, `/api/v1/request: 50` override

**Sequence**:
1. User makes 50th request to `/api/v1/request` at `t=0s`
   - Effective Limit: `min(1000, 50) = 50`
   - Redis: `ZCARD` returns 49
   - Action: `ZADD`, return 200 OK

2. User makes 51st request to `/api/v1/request` at `t=1s`
   - Redis: `ZCARD` returns 50
   - Action: Return 429 (endpoint limit hit)

3. User makes 1st request to `/api/v1/health` at `t=2s`
   - Effective Limit: `min(1000, None) = 1000` (no override)
   - Redis key: `ratelimit:premium-user-001:/api/v1/health`
   - Action: `ZADD`, return 200 OK (independent limit)

---

## Integration with Existing Models

### With API Models (003-rest-api)

- `RateLimitResult` → HTTP response headers injection
- `RateLimitException` → FastAPI exception handler → 429 JSON response

### With Cache Models (005-caching-mechanisms-storage)

- Reuse `RedisConnection` from `cache.py` for connection pooling
- Share Redis instance (different key prefix: `ratelimit:` vs `cache:`)

### With Metrics Models (008-metrics-observability-performance)

- Export `RateLimitMetrics` via Prometheus `/metrics` endpoint
- Counter: `proxywhirl_rate_limit_throttled_total`
- Histogram: `proxywhirl_rate_limit_check_duration_seconds`
