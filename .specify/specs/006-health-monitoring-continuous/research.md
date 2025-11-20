# Research: Health Monitoring

**Feature**: 006-health-monitoring-continuous  
**Date**: 2025-11-01  
**Status**: Complete

## Overview

Research findings for implementing continuous health monitoring with background thread-per-source architecture, cache integration, and self-healing recovery mechanisms.

## Key Decisions

### 1. Threading Model: Background Thread Per Source with Shared Pool

**Decision**: Use one background thread per proxy source with a shared thread pool (ThreadPoolExecutor) for executing individual health checks.

**Rationale**:
- **Isolation**: Each source can have independent check intervals without interference
- **Resource Control**: Shared ThreadPoolExecutor limits total concurrent checks (prevents resource exhaustion)
- **Scalability**: Thread pool size configurable based on system resources
- **Simplicity**: Standard library `threading` and `concurrent.futures` (no external dependencies)
- **Python GIL Compatibility**: Health checks are I/O-bound (HTTP requests), where threading performs well despite GIL

**Alternatives Considered**:
- **Single sequential thread**: Too slow for large proxy pools, fails SC-010 (10k proxies in 5 min)
- **Async/await with asyncio**: Requires httpx AsyncClient, increases complexity, mixing sync/async challenging
- **Process pool**: Excessive overhead for I/O-bound tasks, pickle serialization issues with Pydantic models
- **No background checks**: Breaks US1 (continuous monitoring), requires on-demand only

**Implementation Details**:
```python
# One HealthWorker thread per proxy source
# Each worker submits checks to shared ThreadPoolExecutor
thread_pool = ThreadPoolExecutor(max_workers=100)  # Configurable
workers = {source: HealthWorker(source, pool) for source in sources}
```

---

### 2. Cache Integration: Automatic Invalidation on Health Failure

**Decision**: Health checker automatically calls `CacheManager.invalidate_by_health()` when proxy becomes unhealthy.

**Rationale**:
- **Consistency**: Cache and health state stay synchronized without manual intervention
- **Existing Infrastructure**: Reuses cache invalidation from 005-caching (US3: health-based invalidation)
- **Performance**: No polling needed, immediate invalidation on failure detection
- **Testability**: Clear integration point, easy to mock and verify

**Alternatives Considered**:
- **Cache polls health status**: Adds latency, violates single responsibility
- **Separate health flag in cache**: Duplicates state, risk of desync
- **Manual refresh required**: User burden, prone to errors

**Implementation**:
```python
def _mark_unhealthy(self, proxy: Proxy) -> None:
    proxy.health_status = HealthStatus.UNHEALTHY
    if self.cache:
        self.cache.invalidate_by_health(proxy.cache_key)
```

---

### 3. Health Check Method: HTTP HEAD Requests

**Decision**: Use HTTP HEAD requests to configurable health check URLs (default: http://httpbin.org/status/200).

**Rationale**:
- **Efficiency**: HEAD returns only headers, no body transfer (faster, less bandwidth)
- **Standard**: HTTP HEAD is standard method for checking resource availability
- **Proxy Compatibility**: Most proxies support HEAD requests
- **Customizable**: Users can configure target URL for their use case (FR-007)

**Alternatives Considered**:
- **GET requests**: Transfers full body, wastes bandwidth for health checks
- **OPTIONS requests**: Some proxies/servers don't support OPTIONS
- **TCP connection only**: Doesn't verify HTTP-level proxy functionality
- **Custom protocol**: Adds complexity, reduces compatibility

**Validation Logic**:
```python
# Success: 2xx status code (default)
# Timeout: Configurable (default 10s)
# Expected pattern: User-configurable regex (FR-009)
response = httpx.head(url, proxy=proxy_url, timeout=10)
is_healthy = 200 <= response.status_code < 300
```

---

### 4. State Persistence: L3 SQLite Cache Tier

**Decision**: Store health state (status, last_check, failure_count, history) in existing L3 SQLite cache tier.

**Rationale**:
- **Reuse Infrastructure**: Leverages existing SQLite setup from 005-caching
- **Durability**: Survives restarts (SC-008: zero data loss on proper shutdown)
- **Performance**: SQLite indexed queries fast enough for pool status (<50ms, SC-004)
- **History Retention**: Easily query 24-hour history (SC-009)
- **Schema Evolution**: SQLite supports schema migrations

**Alternatives Considered**:
- **Separate SQLite database**: Duplicates infrastructure, adds complexity
- **In-memory only**: Loses state on restart, fails SC-008
- **Flat files (JSON/JSONL)**: Slower queries, no indexing, concurrency issues
- **Redis**: External dependency, overkill for this use case

**Schema Extension**:
```sql
-- Extend existing cache_entries table from 005-caching
ALTER TABLE cache_entries ADD COLUMN health_status TEXT DEFAULT 'unknown';
ALTER TABLE cache_entries ADD COLUMN last_health_check REAL;
ALTER TABLE cache_entries ADD COLUMN failure_count INTEGER DEFAULT 0;
ALTER TABLE cache_entries ADD COLUMN last_health_error TEXT;

-- New table for health history
CREATE TABLE health_history (
    id INTEGER PRIMARY KEY,
    proxy_key TEXT NOT NULL,
    check_time REAL NOT NULL,
    status TEXT NOT NULL,
    response_time_ms REAL,
    error_message TEXT,
    FOREIGN KEY (proxy_key) REFERENCES cache_entries(key)
);
CREATE INDEX idx_health_history_time ON health_history(check_time);
```

---

### 5. Notification Mechanism: Structured Logging with Event Callbacks

**Decision**: Use loguru structured logging for all health events with optional callback registration for custom notifications.

**Rationale**:
- **Existing Infrastructure**: Loguru already in use throughout proxywhirl
- **Structured Data**: Log events as structured JSON for easy parsing/filtering
- **Flexibility**: Callbacks allow webhook/email/custom integrations without bloating core
- **Performance**: Non-blocking logging with async handlers
- **Observability**: Integrates with existing logging infrastructure

**Alternatives Considered**:
- **Built-in webhook/email**: Adds external dependencies, config complexity
- **Event bus/queue**: Overkill for this use case, adds dependencies
- **File-based events**: Requires polling, adds latency
- **No notifications**: Fails US6 (health event notifications)

**Implementation**:
```python
# Structured logging
logger.warning(
    "Proxy health failed",
    extra={
        "event": "proxy_unhealthy",
        "proxy": proxy.url,
        "failure_count": proxy.failure_count,
        "threshold": threshold
    }
)

# Optional callbacks for custom notifications
class HealthChecker:
    def __init__(self, on_unhealthy: Optional[Callable] = None):
        self.on_unhealthy = on_unhealthy
    
    def _mark_unhealthy(self, proxy: Proxy) -> None:
        logger.warning("proxy_unhealthy", proxy=proxy.url)
        if self.on_unhealthy:
            self.on_unhealthy(HealthEvent(proxy=proxy, event="unhealthy"))
```

---

### 6. Recovery Strategy: Exponential Backoff with Max Retries

**Decision**: Use exponential backoff for recovery attempts (cooldown doubles on each failure) with configurable max retries (default: 5).

**Rationale**:
- **Efficiency**: Avoids hammering unhealthy proxies, reduces wasted checks
- **Adaptive**: Gives proxies time to recover naturally
- **Resource Friendly**: Reduces load on both proxy and health check system
- **Proven Pattern**: Standard retry pattern in distributed systems

**Alternatives Considered**:
- **Fixed interval retries**: Wastes resources on persistently dead proxies
- **Linear backoff**: Too slow, delays recovery detection
- **No backoff**: Excessive resource usage, potential rate limiting
- **No recovery**: Fails US5 (automatic recovery), permanent proxy loss

**Implementation**:
```python
# Cooldown calculation
base_cooldown = 60  # 1 minute
cooldown = base_cooldown * (2 ** recovery_attempt)
# Attempt 1: 60s, 2: 120s, 3: 240s, 4: 480s, 5: 960s (16 min)

# After max retries, mark as permanently failed
if recovery_attempt >= max_retries:
    proxy.health_status = HealthStatus.PERMANENTLY_FAILED
    pool.remove(proxy)
```

---

### 7. Thread Safety: Read-Write Locks for Pool Status

**Decision**: Use `threading.RLock` (reentrant lock) for protecting proxy pool state during health checks.

**Rationale**:
- **Thread Safety**: Multiple health workers accessing shared pool state
- **Reentrant**: Allows same thread to acquire lock multiple times (needed for nested calls)
- **Standard Library**: No external dependencies
- **Performance**: RLock is fast for read-heavy workloads (most operations are reads)

**Alternatives Considered**:
- **No locking**: Race conditions, data corruption
- **Global lock**: Excessive contention, fails SC-003 (<5% CPU overhead)
- **Lock-free structures**: Complex implementation, harder to test
- **Database-level locking**: Slower, adds latency to status queries

**Implementation**:
```python
class HealthChecker:
    def __init__(self):
        self._lock = threading.RLock()
    
    def _update_proxy_status(self, proxy: Proxy, status: HealthStatus) -> None:
        with self._lock:
            proxy.health_status = status
            self._persist_to_cache(proxy)
```

---

### 8. False Positive Mitigation: Failure Threshold with Jitter

**Decision**: Require N consecutive failures (default: 3) before marking unhealthy, with small random jitter (±10%) in check intervals.

**Rationale**:
- **Reliability**: Single transient failure doesn't trigger invalidation
- **SC-007 Compliance**: Reduces false positive rate to <1%
- **Jitter**: Prevents thundering herd (all proxies checked simultaneously)
- **Configurable**: Users can adjust threshold based on their reliability requirements

**Alternatives Considered**:
- **Single failure**: Too sensitive, high false positive rate
- **Time-based window**: More complex, harder to reason about
- **No jitter**: All proxies checked at same interval boundaries (spike load)
- **Probabilistic sampling**: Reduces coverage, misses real failures

**Implementation**:
```python
def should_mark_unhealthy(self, proxy: Proxy) -> bool:
    return proxy.consecutive_failures >= self.failure_threshold

def get_next_check_time(self, interval: int) -> float:
    jitter = random.uniform(-0.1, 0.1) * interval
    return time.time() + interval + jitter
```

---

## Performance Considerations

### Concurrency Limits

**Thread Pool Sizing**:
```python
# Conservative default based on Python threading overhead
default_workers = min(100, (cpu_count() * 10))

# SC-006: Must handle 1000 concurrent checks
# With 100-worker pool and 10s timeout:
#   Throughput = 100 checks / 10s = 10 checks/sec
#   1000 checks = 100 seconds (acceptable)
```

**CPU Overhead** (SC-003: <5%):
- Health checks are I/O-bound (HTTP requests)
- Thread overhead ~1-2% CPU per 100 threads
- Target: 100-200 worker threads max

### Memory Management

**History Retention** (SC-009: 24 hours):
```python
# Auto-cleanup old history
DELETE FROM health_history WHERE check_time < (now - 86400);

# Run every hour in background
```

**Pool Status Caching**:
```python
# Cache pool status for 1 second to reduce query load
@cached(ttl=1.0)
def get_pool_status() -> PoolStatus:
    return self._calculate_status()
```

---

## Testing Strategy

### Unit Tests
- Health status state transitions
- Failure threshold logic
- Recovery backoff calculations
- Thread-safe status updates
- Event callback triggering

### Integration Tests
- Cache invalidation on health failure
- L3 persistence and recovery after restart
- Thread pool behavior under load
- End-to-end health check flow

### Property Tests (Hypothesis)
- Health status never invalid
- Failure count monotonically increasing until reset
- Recovery cooldown always >= previous cooldown
- Pool status counts always sum to total

### Benchmark Tests
- SC-001: Detection within 1 minute
- SC-004: Status queries <50ms
- SC-006: 1000 concurrent checks
- SC-010: 10k proxies in 5 minutes

---

## Dependencies

### Existing (No New External Deps)
- `httpx`: HTTP client for health checks (already in use)
- `threading`: Background workers (stdlib)
- `concurrent.futures`: Thread pool (stdlib)
- `loguru`: Structured logging (already in use)
- `pydantic`: Data models (already in use)

### Integration Points
- `cache.py`: Cache invalidation, L3 persistence
- `rotator.py`: Proxy pool access, exclusion of unhealthy proxies
- `models.py`: Proxy model extension with health fields

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Health checks overwhelm proxy pool | Thread pool limits, configurable intervals, jitter |
| False positives from transient failures | N-consecutive failure threshold (default: 3) |
| Memory leak from unbounded history | Auto-cleanup after 24 hours, bounded cache |
| Thread safety bugs | Comprehensive concurrency tests, lock verification |
| Health system failure crashes service | Graceful degradation (FR-018), isolated threads |
| Slow health checks block service | Background threads, non-blocking design |

---

## Open Questions

None - all clarifications resolved in spec clarification phase.

---

## References

- Python threading best practices: https://docs.python.org/3/library/threading.html
- ThreadPoolExecutor: https://docs.python.org/3/library/concurrent.futures.html
- HTTP HEAD method: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/HEAD
- Exponential backoff: https://en.wikipedia.org/wiki/Exponential_backoff
- SQLite concurrency: https://www.sqlite.org/threadsafe.html
