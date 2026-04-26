# ADR-002: Circuit Breaker Pattern for Proxy Failure Management

## Status

Accepted

## Context

Proxy servers frequently become unavailable due to:
- Network failures (connection refused, timeouts)
- Proxy server crashes or restarts
- Rate limiting or IP bans
- Geographic restrictions
- ISP-level blocking

Without intelligent failure handling, ProxyWhirl would:
- Repeatedly attempt to use failed proxies
- Waste time and resources on known-bad proxies
- Degrade user experience with cascading failures
- Fail to detect proxy recovery after temporary issues

The system needs a mechanism to:
1. **Detect failures**: Track proxy health across multiple requests
2. **Isolate failures**: Stop using failed proxies temporarily
3. **Test recovery**: Periodically check if failed proxies have recovered
4. **Persist state**: Remember failures across application restarts
5. **Scale efficiently**: Handle thousands of proxies without overhead

Traditional approaches have limitations:
- Simple retry logic doesn't prevent repeated failures
- Manual proxy blacklisting requires user intervention
- Stateless systems can't learn from historical failures

## Decision

We implemented the **Circuit Breaker pattern** with three states and persistence:

### Circuit States

**CLOSED** (Normal Operation):
- Proxy available for all requests
- Failures tracked in rolling time window
- Transitions to OPEN when failure threshold exceeded

**OPEN** (Proxy Excluded):
- Proxy excluded from rotation
- No requests attempted (fail-fast)
- Automatic timeout triggers transition to HALF_OPEN
- Duration: Configurable timeout (default: 30 seconds)

**HALF_OPEN** (Testing Recovery):
- Single test request allowed
- Success → Transition to CLOSED (proxy recovered)
- Failure → Transition back to OPEN (reset timeout)
- Only one in-flight test request permitted

### State Transitions

```
CLOSED --[failures ≥ threshold]--> OPEN
OPEN --[timeout elapsed]--> HALF_OPEN
HALF_OPEN --[test success]--> CLOSED
HALF_OPEN --[test failure]--> OPEN
```

### Key Design Choices

**Rolling Time Window**:
- Use `collections.deque` to track failure timestamps
- Default window: 60 seconds
- Failures outside window automatically pruned
- Prevents permanent exclusion from transient failures

**Configuration** (per-proxy `CircuitBreaker`):
```python
failure_threshold: int = 5        # Failures before opening
window_duration: float = 60.0     # Rolling window (seconds)
timeout_duration: float = 30.0    # Circuit open duration (seconds)
persist_state: bool = False       # Enable state persistence
```

**State Persistence** (optional):
- Store state to SQLite via `SQLiteStorage`
- Table: `circuit_breaker_states`
- Serialized fields: state, failure_count, failure_window, timestamps
- Restore on startup to prevent retry storms after restart
- Asynchronous saves to avoid blocking requests

**Thread Safety**:
- Each `CircuitBreaker` has a `threading.Lock`
- Protects state transitions and failure_window updates
- Lock-free `should_attempt_request()` for read-heavy workloads
- `AsyncRWLock` for high-concurrency scenarios (optional)

**Half-Open Gating**:
- `_half_open_pending` flag prevents concurrent test requests
- Only one thread can test recovery at a time
- Prevents thundering herd on timeout expiration

## Consequences

### Positive

1. **Fast Failure Detection**:
   - Failed proxies excluded after 5 failures in 60 seconds
   - Prevents wasted retry attempts
   - Improves overall request success rate

2. **Automatic Recovery**:
   - Failed proxies automatically re-tested after timeout
   - No manual intervention required
   - Proxies return to rotation when recovered

3. **Persistent Failure Memory**:
   - Optional state persistence across restarts
   - Prevents retry storms on application startup
   - SQLite storage provides durability

4. **Low Overhead**:
   - O(1) state check in `should_attempt_request()`
   - Deque cleanup is O(k) where k = failures in window
   - Async persistence doesn't block request path

5. **Configurable Sensitivity**:
   - Adjustable `failure_threshold` and `window_duration`
   - Tune for different proxy quality/reliability
   - Per-proxy configuration support

6. **Graceful Degradation**:
   - Circuit breaker failures don't crash system
   - Proxy simply excluded from rotation
   - Other proxies continue serving requests

### Negative

1. **State Complexity**:
   - Three-state machine adds complexity
   - Requires careful testing of transitions
   - Half-open state needs special handling

2. **Persistence Overhead**:
   - Optional SQLite writes on state changes
   - Async saves can be lost on hard crash
   - Database table adds schema migration burden

3. **Lock Contention**:
   - Per-proxy lock serializes state updates
   - High-frequency failures can cause bottleneck
   - Mitigated by lock-free reads

4. **Recovery Delay**:
   - Proxies excluded for minimum `timeout_duration`
   - May miss early recovery opportunities
   - Tradeoff for preventing retry storms

5. **False Positives**:
   - Transient network issues can open circuit
   - Overly aggressive thresholds exclude good proxies
   - Requires tuning for specific environments

### Alternatives Considered

**Simple Retry with Backoff**:
- Simpler implementation
- No state machine complexity
- Doesn't prevent repeated failures across requests
- Rejected: Insufficient isolation

**Health Check Background Thread**:
- Active health monitoring
- Detects failures before user requests
- Adds complexity and resource overhead
- Rejected: Prefer reactive failure handling

**Proxy Blacklisting**:
- Manual exclusion by user
- No automatic recovery
- Requires external coordination
- Rejected: Lacks automation

**Leaky Bucket Rate Limiting**:
- Gradual recovery instead of half-open state
- More complex implementation
- Doesn't provide hard exclusion
- Rejected: Circuit breaker better fits use case

**Hystrix-Style Circuit Breaker**:
- Request volume threshold
- Sliding window statistics
- More complex than needed
- Rejected: Simpler approach sufficient

## Implementation Details

### Key Components

**`CircuitBreaker` Class** (`proxywhirl/circuit_breaker.py`):
```python
class CircuitBreaker(BaseModel):
    proxy_id: str
    state: CircuitBreakerState  # CLOSED, OPEN, HALF_OPEN
    failure_window: deque[float]
    failure_threshold: int
    window_duration: float
    timeout_duration: float
    next_test_time: Optional[float]
    _lock: Lock
    _half_open_pending: bool
    _storage: Optional[SQLiteStorage]
```

**Core Methods**:
- `record_failure()`: Add failure to window, check threshold
- `record_success()`: Clear failures, close circuit
- `should_attempt_request()`: Check if proxy available
- `save_state()` / `load_state()`: Persistence operations

**Storage Schema** (`CircuitBreakerStateTable`):
```sql
CREATE TABLE circuit_breaker_states (
    proxy_id TEXT PRIMARY KEY,
    state TEXT,
    failure_count INTEGER,
    failure_window_json TEXT,  -- JSON array
    next_test_time REAL,
    last_state_change TIMESTAMP,
    -- Configuration
    failure_threshold INTEGER,
    window_duration REAL,
    timeout_duration REAL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

**Integration with `ProxyWhirl`**:
```python
# Before making request
if not circuit_breaker.should_attempt_request():
    # Try next proxy
    continue

try:
    response = await http_client.get(url, proxy=proxy)
    circuit_breaker.record_success()
except ProxyError:
    circuit_breaker.record_failure()
```

### Thread Safety Patterns

**Lock-Free Read Path**:
```python
def should_attempt_request(self) -> bool:
    with self._lock:  # Brief lock
        if self.state == CLOSED:
            return True
        # Check timeout, update state
        return self._check_timeout()
```

**Async Persistence** (non-blocking):
```python
def _schedule_persist(self) -> None:
    if not self.persist_state:
        return
    loop = asyncio.get_running_loop()
    loop.create_task(self.save_state())  # Fire and forget
```

**RWLock for High Concurrency** (optional):
```python
class AsyncRWLock:
    async def acquire_read(self): ...   # Shared reads
    async def acquire_write(self): ...  # Exclusive writes
```

## References

- Implementation: `/Users/ww/dev/projects/proxywhirl/proxywhirl/circuit_breaker.py`
- Storage: `/Users/ww/dev/projects/proxywhirl/proxywhirl/storage.py` (CircuitBreakerStateTable)
- Tests: `/Users/ww/dev/projects/proxywhirl/tests/unit/test_circuit_breaker_*.py`

## Notes

### Future Enhancements

1. **Adaptive Thresholds**:
   - Dynamically adjust `failure_threshold` based on proxy success rate
   - Lower threshold for historically unreliable proxies

2. **Exponential Backoff**:
   - Increase `timeout_duration` on repeated failures
   - Reset on successful recovery

3. **Circuit Breaker Pool**:
   - Share failure knowledge across multiple `ProxyWhirl` instances
   - Distributed circuit breaker with Redis backend

4. **Metrics Integration**:
   - Expose circuit state transitions as Prometheus metrics
   - Alert on high circuit open rate

### Design Rationale

The circuit breaker pattern was chosen over alternatives because:
- **Proven Pattern**: Well-understood failure isolation mechanism
- **Automatic**: No manual intervention required
- **Efficient**: Minimal overhead in steady state
- **Observable**: Clear state transitions for debugging
- **Extensible**: Easy to add custom failure detection logic

The three-state design (vs two-state) enables safe recovery testing without exposing users to failed proxies immediately after timeout.
