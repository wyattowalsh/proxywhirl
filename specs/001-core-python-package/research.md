# Phase 0: Research & Technical Decisions

**Feature**: Core Python Package  
**Date**: 2025-10-21

## Research Tasks Completed

All technical context questions were pre-specified in the user input. No NEEDS CLARIFICATION items remained.

## Technology Decisions

### 1. HTTP Client: httpx

**Decision**: Use httpx as the primary HTTP client library

**Rationale**:
- Modern async/sync dual API (supports both operation modes required by FR-015)
- Built-in connection pooling (Constitution III: Performance & Efficiency)
- Excellent proxy support (HTTP, HTTPS, SOCKS via httpx[socks])
- Type-safe with full type hints (Constitution Quality Gates)
- Active maintenance and widespread adoption
- Drop-in replacement API similar to requests

**Alternatives Considered**:
- `requests`: Mature but sync-only, no native async support
- `aiohttp`: Async-only, would require duplicate code for sync mode
- `urllib3`: Too low-level, would require significant wrapper code

### 2. Data Validation: Pydantic v2

**Decision**: Use Pydantic v2 for all data validation and models

**Rationale**:
- Fast validation with Rust core (performance requirement)
- Excellent type safety and IDE support (Constitution Quality Gates)
- JSON schema generation for API documentation
- Built-in validation for URLs, credentials, configuration
- Native support for both sync and async validation
- Integrates seamlessly with pydantic-settings and SQLModel

**Alternatives Considered**:
- `marshmallow`: Slower, less type-safe
- `attrs` + `validators`: More manual validation code required
- `dataclasses` only: No built-in validation logic

### 3. Configuration: pydantic-settings

**Decision**: Use pydantic-settings for configuration management

**Rationale**:
- Built on Pydantic v2 for consistency
- Automatic environment variable loading (12-factor app)
- Type-safe configuration with validation
- Multiple source support (env vars, .env files, JSON, YAML)
- Minimal code required for configuration management

**Alternatives Considered**:
- `dynaconf`: More features but heavier dependency
- `python-decouple`: Less type-safe
- Custom solution: Would duplicate pydantic-settings functionality

### 4. Storage: SQLModel

**Decision**: Use SQLModel for optional persistent storage

**Rationale**:
- Combines Pydantic v2 + SQLAlchemy (best of both worlds)
- Same models work for validation AND database
- Optional dependency - users can use in-memory only
- Type-safe ORM with modern Python syntax
- Async support via SQLAlchemy 2.0

**Alternatives Considered**:
- `SQLAlchemy` alone: Would need separate Pydantic models
- `Tortoise ORM`: Less mature, smaller ecosystem
- `Peewee`: Sync-only, less type-safe

### 5. Retry Logic: tenacity

**Decision**: Use tenacity for retry mechanisms

**Rationale**:
- Declarative retry configuration
- Multiple backoff strategies (exponential, fibonacci, etc.)
- Async support
- Highly customizable (predicates, callbacks, stats)
- Battle-tested in production systems
- Integrates well with both sync and async code

**Alternatives Considered**:
- `backoff`: Simpler but less flexible
- `retry`: Less maintained, fewer features
- Custom implementation: Would violate DRY principle

### 6. Logging: loguru

**Decision**: Use loguru for structured logging

**Rationale**:
- Simple API with powerful features
- Native structured logging (JSON support)
- Automatic context capture
- Async-safe logging
- Lazy evaluation for performance
- Excellent error formatting with stack traces
- No configuration required for basic use

**Alternatives Considered**:
- `structlog`: More complex setup required
- Standard `logging`: Requires significant boilerplate
- `python-json-logger`: Less feature-rich

### 7. Testing: pytest + pytest-asyncio + hypothesis

**Decision**: Use pytest ecosystem for testing

**Rationale**:
- **pytest**: De facto standard, excellent fixture system
- **pytest-asyncio**: Seamless async test support
- **hypothesis**: Property-based testing for rotation algorithms (Constitution V)
- Great plugin ecosystem
- Excellent error reporting
- Supports both unit and integration tests

**Alternatives Considered**:
- `unittest`: More verbose, less powerful fixtures
- `nose2`: Less actively maintained
- `ward`: Too new, smaller ecosystem

## Architecture Decisions

### 1. Protocol-Based Plugin System

**Decision**: Use Python Protocols (PEP 544) for pluggable components

**Rationale**:
- Type-safe duck typing (structural subtyping)
- No need for explicit inheritance
- Clear contracts without tight coupling
- IDE support for protocol checking
- Follows Constitution IV: Modular Architecture

**Components with Protocols**:
- Rotation strategies (`RotationStrategy` protocol)
- Storage backends (`ProxyStorage` protocol)
- Health checkers (`HealthChecker` protocol)

### 2. Async-First Design with Sync Wrappers

**Decision**: Build async core with sync wrappers

**Rationale**:
- Async is harder to retrofit, sync is easy to wrap
- Better performance for concurrent operations
- httpx provides both APIs naturally
- Can support both sync and async users
- Future-proof as Python moves toward async

**Implementation**:
- Core classes have async methods
- Sync methods wrap async with `asyncio.run()` or `loop.run_until_complete()`
- Clear naming: `async def get_proxy()` vs `def get_proxy_sync()`

### 3. Credential Security

**Decision**: In-memory encryption optional, secure defaults mandatory

**Rationale**:
- Never log credentials in any form (Constitution II)
- Encrypt in-memory storage optional (via `cryptography` extra)
- Store as SecretStr in Pydantic models
- Clear credentials from memory on pool destruction
- Provide secure defaults, allow users to opt-in to encryption

### 4. Error Handling Strategy

**Decision**: Custom exception hierarchy with rich context

**Rationale**:
- Clear exception types for different failure modes
- All exceptions include proxy details without credentials
- Structured error information for programmatic handling
- Follows Constitution VI: Error Context requirement

**Exception Types**:
- `ProxyError` (base)
- `ProxyConnectionError`
- `ProxyAuthenticationError`
- `ProxyPoolEmptyError`
- `ProxyValidationError`

### 5. Connection Pooling

**Decision**: Leverage httpx connection pools, expose configuration

**Rationale**:
- httpx handles pooling internally
- Expose pool limits as configuration options
- Per-proxy connection limits supported
- Reuse connections when safe (same proxy + auth)
- Follows Constitution III: Connection pooling required

## Performance Considerations

### 1. Proxy Selection Overhead

**Target**: <50ms overhead for proxy selection

**Approach**:
- In-memory data structures (no DB queries for selection)
- Lazy loading of proxy validation
- Cache strategy results when deterministic
- Benchmark all rotation strategies

### 2. Concurrent Request Handling

**Target**: 1000+ concurrent requests

**Approach**:
- Async core enables high concurrency
- Connection pooling reduces overhead
- No global locks in hot path
- Thread-safe for sync callers

### 3. Memory Efficiency

**Target**: Support 100+ proxy pool efficiently

**Approach**:
- Lazy loading of proxy metadata
- Stream responses, don't buffer
- Periodic cleanup of stale connections
- Configurable pool size limits

## Integration Patterns

### 1. Usage Patterns

Sync usage:
```python
from proxywhirl import ProxyRotator

rotator = ProxyRotator(proxies=["http://proxy1.com", "http://proxy2.com"])
response = rotator.get("https://example.com")
```

Async usage:
```python
from proxywhirl import AsyncProxyRotator

rotator = AsyncProxyRotator(proxies=["http://proxy1.com"])
response = await rotator.get("https://example.com")
```

### 2. Configuration Patterns

Environment variables:
```bash
PROXYWHIRL_STRATEGY=round-robin
PROXYWHIRL_TIMEOUT=30
PROXYWHIRL_POOL_SIZE=50
```

Config file:
```yaml
strategy: round-robin
timeout: 30
pool_size: 50
proxies:
  - url: http://proxy1.com
    username: user1
    password: pass1
```

### 3. Custom Strategy Pattern

```python
from proxywhirl.strategies import RotationStrategy
from proxywhirl.models import Proxy

class CustomStrategy(RotationStrategy):
    def select_proxy(self, pool: list[Proxy]) -> Proxy:
        # Custom logic
        return pool[0]

rotator = ProxyRotator(proxies=[...], strategy=CustomStrategy())
```

## Dependencies & Versions

### Core Dependencies
- `httpx >= 0.27.0` - HTTP client with proxy support
- `httpx[socks] >= 0.27.0` - SOCKS proxy support
- `pydantic >= 2.0.0, < 3.0.0` - Data validation
- `pydantic-settings >= 2.0.0` - Configuration management
- `tenacity >= 8.0.0` - Retry logic
- `loguru >= 0.7.0` - Logging

### Optional Dependencies
- `sqlmodel >= 0.0.14` - Persistent storage (extra: `storage`)
- `cryptography >= 41.0.0` - Credential encryption (extra: `security`)
- `aiosqlite >= 0.19.0` - Async SQLite (extra: `storage`)

### Development Dependencies
- `pytest >= 7.0.0`
- `pytest-asyncio >= 0.21.0`
- `pytest-cov >= 4.0.0`
- `hypothesis >= 6.0.0`
- `ruff >= 0.1.0` - Linting
- `black >= 23.0.0` - Formatting
- `mypy >= 1.0.0` - Type checking

## Open Questions & Future Research

None - all technical decisions finalized for Phase 1.

---

## Additional Research: Proxy Fetching & Validation

### 8. Proxy List Fetching

**Decision**: Build custom fetcher with pluggable parsers + JavaScript rendering support

**Rationale**:
- No existing library provides comprehensive free proxy aggregation
- Custom solution allows support for multiple formats
- Pluggable parser system for extensibility
- Many modern proxy list sites use JavaScript/React/Vue
- Can add rate limiting and caching at fetcher level

**Rendering Options**:
- **Static HTML**: Use httpx for fast fetching (no JS needed)
- **JavaScript Pages**: Use playwright for headless browser rendering
- **Auto-detection**: Attempt static first, fall back to JS rendering if needed

**Supported Formats**:
- **JSON**: Standard JSON arrays with proxy objects
- **CSV/TSV**: Comma/tab-separated proxy lists
- **Plain text**: Line-delimited proxy URLs
- **HTML tables**: Parse `<table>` elements from web pages (static or JS-rendered)
- **Custom**: User-defined parsers via Protocol

**Built-in Sources** (examples, user can add their own):
- Free-proxy-list.net (static HTML)
- ProxyScrape.com API (JSON)
- GeoNode free proxy API (JSON)
- ProxyNova.com (JavaScript-rendered)
- Custom user-provided URLs

**Implementation**:
```python
from proxywhirl.fetchers import ProxyFetcher, RenderMode

fetcher = ProxyFetcher(
    sources=[
        # JSON API - static fetch
        "https://api.proxyscrape.com/v2/?request=get&protocol=http&format=json",
        # JavaScript-rendered page
        {"url": "https://www.proxy-list.download/HTTP", "render_mode": RenderMode.JAVASCRIPT},
        # Static HTML table
        {"url": "https://www.free-proxy-list.net", "render_mode": RenderMode.STATIC}
    ],
    refresh_interval=3600,  # 1 hour
    validate_before_add=True
)

proxies = await fetcher.fetch()  # Returns validated proxies
```

**JavaScript Rendering**:
- Uses Playwright (async, lightweight)
- Headless Chromium for rendering
- Wait for network idle before parsing
- Configurable wait selectors/timeouts
- Optional: screenshot on failure for debugging

**Dependencies**:
- `playwright` (optional, install with `pip install proxywhirl[js]`)
- Auto-installs browser on first use
- Falls back gracefully if playwright not installed

---

### 8b. Local File Storage

**Decision**: Support JSON file storage for proxy pool persistence

**Rationale**:
- Simple, human-readable format for debugging
- No database required (zero-config)
- Easy backup/restore (just copy files)
- Version control friendly (can commit proxy lists)
- Cross-platform compatible
- Atomic writes prevent corruption

**Storage Formats**:
- **JSON**: Human-readable, supports metadata
- **JSONL** (JSON Lines): Append-friendly, streaming support
- **Auto-save**: Periodic persistence (configurable interval)
- **Lazy-load**: Load only what's needed for large pools

**File Structure**:
```json
{
  "version": "1.0",
  "pool_name": "default",
  "last_updated": "2025-10-21T10:30:00Z",
  "proxies": [
    {
      "id": "uuid-here",
      "url": "http://proxy1.com:8080",
      "username": null,
      "password": null,
      "source": "USER",
      "health_status": "HEALTHY",
      "total_requests": 150,
      "total_successes": 145,
      "total_failures": 5,
      "average_response_time_ms": 234.5,
      "tags": ["premium", "us-west"],
      "created_at": "2025-10-21T10:00:00Z",
      "updated_at": "2025-10-21T10:30:00Z"
    }
  ],
  "config": {
    "strategy": "weighted",
    "max_pool_size": 100,
    "auto_remove_dead": true
  }
}
```

**Implementation**:
```python
from proxywhirl import ProxyRotator

# Auto-save to file every 5 minutes
rotator = ProxyRotator(
    proxies=[...],
    storage_backend="file",
    storage_path="./data/proxies.json",
    auto_save_interval=300,  # 5 minutes
    atomic_writes=True  # Use temp file + rename
)

# Save manually
rotator.save()

# Load from file
rotator = ProxyRotator.from_file("./data/proxies.json")
```

**Performance**:
- Write: ~10-50ms for 100 proxies
- Read: ~5-20ms for 100 proxies (lazy loading available)
- Atomic writes prevent corruption during crashes

**Optimizations**:
- Gzip compression for large pools (optional)
- Incremental saves (only changed proxies)
- Background save thread (non-blocking)
- File locking for concurrent access

---

### 9. Proxy Validation Strategy

**Decision**: Multi-stage validation with timeout-based filtering

**Rationale**:
- Free proxies are often unreliable
- Multi-stage validation balances speed and accuracy
- Configurable validation strictness
- Async validation for performance

**Validation Stages**:
1. **Format Validation**: URL structure, port range, protocol
2. **Connectivity Test**: TCP connection attempt (fast)
3. **HTTP Test**: Make test request through proxy (slower but accurate)
4. **Anonymity Check**: Verify proxy doesn't leak real IP (optional)

**Validation Configuration**:
```python
from proxywhirl import ProxyValidator, ValidationLevel

validator = ProxyValidator(
    level=ValidationLevel.MEDIUM,  # Format + connectivity
    test_url="http://httpbin.org/ip",
    timeout=5,
    anonymity_required=False
)

valid_proxies = await validator.validate_batch(proxies)
```

**Performance**: Async validation supports 100+ proxies/second

### 10. Source Tagging & Priority

**Decision**: Tag-based proxy source tracking with weighted selection

**Rationale**:
- Users need visibility into proxy sources
- Weighted strategies can prioritize user proxies over free proxies
- Tags enable filtering and analytics

**Tagging System**:
- Source tags: `source:user`, `source:fetched`, `source:proxyscrape`
- Quality tags: `quality:premium`, `quality:free`
- Auto-tags based on validation results

**Priority System**:
```python
from proxywhirl import ProxyRotator, WeightedStrategy

rotator = ProxyRotator(
    user_proxies=[...],  # Auto-tagged as source:user
    auto_fetch_sources=["https://..."],  # Auto-tagged as source:fetched
    strategy=WeightedStrategy(
        weights={
            "source:user": 0.8,      # 80% selection probability
            "source:fetched": 0.2    # 20% selection probability
        }
    )
)
```

### 11. Refresh & Deduplication

**Decision**: Periodic refresh with smart deduplication

**Rationale**:
- Free proxy lists change frequently
- Deduplication prevents duplicate proxies from multiple sources
- Periodic refresh keeps pool healthy

**Deduplication Strategy**:
- Hash proxies by (URL, port, protocol)
- Keep proxy with best health metrics if duplicates found
- Merge tags from duplicate sources

**Refresh Mechanism**:
```python
# Auto-refresh every hour
rotator = ProxyRotator(
    auto_fetch_sources=[...],
    refresh_interval=3600,
    remove_dead_on_refresh=True
)

# Manual refresh
await rotator.refresh_proxies()
```

---

## Performance Optimizations

### 1. Connection Pooling & Reuse

**Decision**: Aggressive connection pooling with keep-alive

**Rationale**:
- Reusing connections saves ~100-200ms per request
- httpx pools connections automatically
- Configure limits based on proxy pool size

**Configuration**:
```python
config = ProxyConfiguration(
    pool_connections=100,      # Max connections per proxy
    pool_max_keepalive=200,    # Max keepalive connections total
    keepalive_timeout=300,     # 5 minutes keepalive
    max_concurrent_requests=1000  # Semaphore limit
)
```

**Benefits**:
- 2-3x faster requests after warmup
- Reduced load on proxy servers
- Better handling of burst traffic

### 2. Async-First Architecture

**Decision**: Build async core, wrap for sync

**Rationale**:
- Async I/O enables true concurrency
- Can handle 1000+ requests simultaneously
- Sync wrapper adds minimal overhead (~1ms)

**Implementation**:
- Core classes are async
- Sync API wraps with `asyncio.run()`
- Both APIs available to users

### 3. Proxy Health Caching

**Decision**: Cache health check results with TTL

**Rationale**:
- Avoid redundant health checks
- Faster proxy selection
- Configurable TTL based on reliability

**Implementation**:
```python
class Proxy:
    _health_cache_ttl = 300  # 5 minutes
    _last_health_check = None
    
    @property
    def is_healthy(self) -> bool:
        if self._cache_valid():
            return self._cached_health
        return self._check_health()
```

### 4. Smart Validation

**Decision**: Multi-level validation with early exit

**Rationale**:
- Format validation is instant
- TCP check faster than HTTP
- Only validate deeply when needed

**Levels**:
1. **Format**: <1ms (regex)
2. **DNS**: ~10ms (cached)
3. **TCP**: ~100ms (connection attempt)
4. **HTTP**: ~500ms (full request)
5. **Anonymity**: ~1000ms (IP leak test)

**Optimization**:
- Validate in batches (async)
- Stop at first failure
- Cache DNS resolutions
- Parallel validation (100+ proxies/sec)

### 5. Lazy Loading & Pagination

**Decision**: Load proxies on-demand from storage

**Rationale**:
- Large pools (1000+) don't need all in memory
- Faster startup time
- Lower memory footprint

**Implementation**:
```python
# Load metadata only, proxies on-demand
pool = ProxyPool.from_file("large_pool.json", lazy=True)

# Loads proxies as needed
proxy = pool.select_next()  # Only loads this proxy
```

### 6. Deduplication Algorithm

**Decision**: Hash-based dedup with bloom filter

**Rationale**:
- O(1) duplicate detection
- Minimal memory overhead
- False positives acceptable (rare)

**Implementation**:
```python
from pybloom_live import BloomFilter

class ProxyPool:
    def __init__(self):
        self._bloom = BloomFilter(capacity=10000, error_rate=0.001)
    
    def add_proxy(self, proxy: Proxy):
        key = f"{proxy.url}:{proxy.port}"
        if key in self._bloom:
            return  # Likely duplicate
        self._bloom.add(key)
        self._proxies.append(proxy)
```

### 7. Request Timeout Optimization

**Decision**: Dynamic timeout based on history

**Rationale**:
- Fast proxies deserve shorter timeouts
- Slow proxies need longer timeouts
- Adapt to proxy performance

**Implementation**:
```python
def calculate_timeout(proxy: Proxy) -> int:
    if proxy.average_response_time_ms:
        # 3x average + 2s buffer
        return (proxy.average_response_time_ms * 3) / 1000 + 2
    return 30  # Default 30s
```

### 8. Strategy Optimization

**Decision**: Pre-compute weights for weighted strategy

**Rationale**:
- Avoid recalculating on every selection
- Update weights periodically
- 10x faster proxy selection

**Implementation**:
```python
class WeightedStrategy:
    def __init__(self):
        self._weights_cache = []
        self._cache_valid_until = 0
    
    def select_proxy(self, pool: list[Proxy]) -> Proxy:
        if time.time() > self._cache_valid_until:
            self._recompute_weights(pool)
            self._cache_valid_until = time.time() + 60  # 1 min TTL
        return random.choices(pool, weights=self._weights_cache)[0]
```

### 9. Background Tasks

**Decision**: Non-blocking background workers

**Rationale**:
- Health checks shouldn't block requests
- Auto-refresh runs in background
- Auto-save runs in background

**Implementation**:
- Use `asyncio.create_task()` for background work
- Graceful shutdown with task cancellation
- Error handling in background tasks

### 10. Memory Optimization

**Decision**: Limit metadata retention

**Rationale**:
- Full request history expensive
- Keep rolling window only
- Aggregate old data

**Implementation**:
```python
class Proxy:
    max_history_entries = 100  # Last 100 requests
    
    def record_request(self, success: bool, duration_ms: float):
        if len(self._history) >= self.max_history_entries:
            # Aggregate oldest half before discarding
            self._aggregate_history()
        self._history.append(...)
```

---

## Monitoring & Observability

### 1. Event Hooks

**Decision**: Callback-based event system

**Rationale**:
- Pluggable monitoring without code changes
- Users can integrate with their own monitoring
- No external dependencies required

**Events**:
- `on_proxy_selected`: Before using a proxy
- `on_request_success`: After successful request
- `on_request_failure`: After failed request
- `on_proxy_health_check`: After health check
- `on_proxy_removed`: When proxy removed from pool
- `on_fetch_complete`: After fetching from source

**Implementation**:
```python
from proxywhirl import ProxyRotator, ProxyEvent

def log_proxy_selection(event: ProxyEvent):
    print(f"Selected proxy: {event.proxy.url}")

def track_failures(event: ProxyEvent):
    if event.error:
        metrics.increment("proxy.failures", tags=[f"proxy:{event.proxy.url}"])

rotator = ProxyRotator(proxies=[...])
rotator.on("proxy_selected", log_proxy_selection)
rotator.on("request_failure", track_failures)
```

### 2. Metrics Collection

**Decision**: Optional metrics via hooks

**Rationale**:
- Built-in basic metrics
- External metrics via hooks
- No forced dependency on monitoring system

**Built-in Metrics**:
- Total requests per proxy
- Success/failure rates
- Average response time
- Health check results
- Pool size changes

**Integration Example**:
```python
# Prometheus integration
from prometheus_client import Counter, Histogram

request_counter = Counter("proxy_requests_total", "Total requests", ["proxy", "status"])
request_duration = Histogram("proxy_request_duration_seconds", "Request duration")

def record_metrics(event: ProxyEvent):
    status = "success" if event.success else "failure"
    request_counter.labels(proxy=event.proxy.url, status=status).inc()
    request_duration.observe(event.duration_ms / 1000)

rotator.on("request_complete", record_metrics)
```

### 3. Structured Logging

**Decision**: Use loguru with structured fields

**Rationale**:
- Rich context in logs
- Easy to parse and search
- JSON output for log aggregators

**Log Levels**:
- **DEBUG**: Proxy selection details, rotation logic
- **INFO**: Successful requests, health checks, pool changes
- **WARNING**: Failed requests, unhealthy proxies, slow responses
- **ERROR**: Configuration errors, storage failures
- **CRITICAL**: Pool empty, all proxies dead

**Implementation**:
```python
from loguru import logger

logger.add(
    "logs/proxywhirl.log",
    format="{time} {level} {message}",
    serialize=True  # JSON output
)

# Example log entries
logger.info("proxy_selected", proxy_url="http://proxy1.com", strategy="weighted")
logger.warning("proxy_slow", proxy_url="http://proxy2.com", duration_ms=5000)
logger.error("proxy_failed", proxy_url="http://proxy3.com", error="ConnectionTimeout")
```

### 4. Health Dashboards

**Decision**: Provide health status API

**Rationale**:
- Easy integration with monitoring dashboards
- Standard health check endpoints
- Machine-readable status

**Health Status**:
```python
health = rotator.get_health_status()
# Returns:
{
    "status": "healthy",  # healthy | degraded | unhealthy
    "pool_size": 15,
    "healthy_proxies": 12,
    "unhealthy_proxies": 3,
    "overall_success_rate": 0.85,
    "average_response_time_ms": 250,
    "last_health_check": "2025-01-21T10:30:00Z",
    "warnings": [
        "3 proxies marked unhealthy",
        "Average response time > 200ms"
    ]
}
```

### 5. Performance Profiling

**Decision**: Optional performance tracking

**Rationale**:
- Identify bottlenecks
- Optimize proxy selection
- Debug slow requests

**Profiling Points**:
- Proxy selection time
- Connection establishment time
- Request/response time
- Validation time
- Storage I/O time

**Implementation**:
```python
rotator = ProxyRotator(proxies=[...], enable_profiling=True)

# After usage
profile = rotator.get_performance_profile()
# Returns:
{
    "proxy_selection_avg_ms": 0.5,
    "connection_establish_avg_ms": 120,
    "request_avg_ms": 250,
    "validation_avg_ms": 500,
    "storage_save_avg_ms": 15
}
```

---

## Security & Rate Limiting

### 1. Per-Proxy Rate Limiting

**Decision**: Token bucket algorithm per proxy

**Rationale**:
- Prevent proxy bans from overuse
- Configurable limits per proxy
- Burst support with sustained rate

**Implementation**:
```python
from proxywhirl import ProxyRotator, RateLimiter

rotator = ProxyRotator(
    proxies=[...],
    rate_limiter=RateLimiter(
        requests_per_second=10,  # Max 10 req/sec per proxy
        burst_size=20            # Allow bursts up to 20
    )
)

# Automatically rate-limited
for i in range(100):
    response = rotator.get(f"https://api.example.com/data/{i}")
    # Will throttle if exceeding rate limit
```

### 2. Credential Rotation

**Decision**: Automatic credential refresh

**Rationale**:
- Security best practice
- Prevent credential leaks
- Support expiring credentials

**Implementation**:
```python
from proxywhirl import ProxyRotator, CredentialRotator

def get_fresh_credentials():
    # Fetch from secrets manager
    return {"username": "user123", "password": "newpass"}

rotator = ProxyRotator(
    proxies=["http://proxy.com:8080"],
    credential_rotator=CredentialRotator(
        refresh_callback=get_fresh_credentials,
        refresh_interval=3600  # Refresh every hour
    )
)
```

### 3. Circuit Breaker

**Decision**: Automatic circuit breaking for failing proxies

**Rationale**:
- Fast-fail for dead proxies
- Reduce wasted retries
- Auto-recovery when proxy recovers

**States**:
- **CLOSED**: Normal operation
- **OPEN**: Proxy failing, skip temporarily
- **HALF_OPEN**: Testing if proxy recovered

**Implementation**:
```python
from proxywhirl import ProxyRotator, CircuitBreaker

rotator = ProxyRotator(
    proxies=[...],
    circuit_breaker=CircuitBreaker(
        failure_threshold=5,    # Open after 5 failures
        timeout=60,             # Stay open for 60 seconds
        success_threshold=2     # Close after 2 successes
    )
)

# Automatically skips failing proxies
response = rotator.get("https://api.example.com")
```

---

## Performance Benchmarks & SLAs

### 1. Target Performance Metrics

**Proxy Selection**:
- Round-robin: <0.1ms (O(1))
- Random: <0.1ms (O(1))
- Weighted: <1ms (O(n) but cached)
- Least-used: <5ms (O(n))

**Request Overhead**:
- Proxy selection + setup: <50ms
- First request (cold): <200ms (connection establishment)
- Subsequent requests (warm): <10ms overhead

**Storage Performance**:
- In-memory save: <1ms
- SQLite save (100 proxies): <20ms
- JSON save (100 proxies): 10-50ms
- JSON load (100 proxies): 5-20ms
- JSON save with gzip: 15-70ms

**Fetching Performance**:
- Static page fetch: <2s per source
- JavaScript-rendered page: <5s per source
- Validation (100 proxies):
  - Format validation: <100ms
  - TCP check: <10s (parallel)
  - HTTP check: <30s (parallel)

**Concurrency**:
- Handle 1000+ concurrent requests
- Connection pool: 100 connections per proxy
- Global connection limit: Configurable (default 10,000)

### 2. Benchmark Suite

**Decision**: Built-in benchmark suite

**Rationale**:
- Verify performance targets
- Regression testing
- Optimize bottlenecks

**Benchmark Tests**:
```python
# Run benchmarks
pytest tests/benchmarks/ -v

# Example output:
# test_proxy_selection_speed ...................... PASSED (0.05ms avg)
# test_request_throughput ......................... PASSED (2000 req/s)
# test_storage_save_speed ......................... PASSED (12ms avg)
# test_concurrent_requests ........................ PASSED (1000 concurrent)
# test_memory_usage ............................... PASSED (50MB for 1000 proxies)
```

**Benchmark Categories**:

1. **Selection Speed**: Measure proxy selection time for each strategy
2. **Request Throughput**: Requests per second with different pool sizes
3. **Storage I/O**: Save/load times for different backends
4. **Validation Speed**: Validation rate (proxies/second)
5. **Memory Usage**: Memory footprint per proxy
6. **Concurrency**: Max concurrent requests before degradation

### 3. Load Testing

**Decision**: Provide load testing tools

**Example**:
```python
from proxywhirl.testing import LoadTest

# Load test configuration
load_test = LoadTest(
    rotator=rotator,
    target_url="https://api.example.com",
    duration_seconds=60,
    requests_per_second=100,
    concurrent_users=50
)

results = load_test.run()
print(f"Average latency: {results.avg_latency_ms}ms")
print(f"Success rate: {results.success_rate:.2%}")
print(f"Throughput: {results.requests_per_second} req/s")
```

### 4. Performance Monitoring

**Real-time Metrics**:
```python
rotator = ProxyRotator(proxies=[...], enable_metrics=True)

# After usage
metrics = rotator.get_metrics()
# Returns:
{
    "total_requests": 10000,
    "avg_latency_ms": 250,
    "p50_latency_ms": 200,
    "p95_latency_ms": 450,
    "p99_latency_ms": 800,
    "success_rate": 0.95,
    "requests_per_second": 100,
    "active_proxies": 15,
    "unhealthy_proxies": 2
}
```

---

## Next Steps

Proceed to Phase 1:
1. Create `data-model.md` with entity models
2. Create `/contracts/` with API specifications
3. Create `quickstart.md` with usage examples
4. Run `.specify/scripts/bash/update-agent-context.sh copilot`
