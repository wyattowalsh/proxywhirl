# Phase 0: Research & Technical Decisions

**Feature**: 014-retry-failover-logic  
**Date**: 2025-11-02  
**Status**: Complete

## Overview

This document consolidates research findings and technical decisions for implementing retry and failover logic with circuit breakers. All "NEEDS CLARIFICATION" items from the Technical Context have been resolved.

---

## 1. Circuit Breaker Implementation Patterns

### Research Question
How to implement thread-safe circuit breaker state machine with rolling time windows in Python?

### Findings

**Thread Safety Options**:
- `threading.Lock`: Simple, adequate for state transitions
- `threading.RLock`: Reentrant, useful if nested locking needed
- Lock-free (atomic operations): Complex, unnecessary for our use case

**Rolling Window Data Structures**:
- `collections.deque` with maxlen: O(1) append, automatic eviction, memory-efficient
- List with manual cleanup: O(n) cleanup, less efficient
- Ring buffer: Complex, no significant benefit over deque

**Half-Open Test Timing**:
- Timer-based: Check time elapsed since circuit opened
- Event-driven: Background thread for recovery tests
- Lazy evaluation: Check on next request attempt

### Decision

**Lock Strategy**: Use `threading.Lock`
- **Rationale**: Simple, sufficient for state transitions, well-tested
- **Implementation**: One lock per CircuitBreaker instance
- **Pattern**: Acquire lock for state reads/writes, release quickly

**Rolling Window**: Use `collections.deque`
- **Rationale**: O(1) operations, automatic size management, stdlib
- **Implementation**: Store failure timestamps, filter by time window on each check
- **Memory**: Bounded by max failures (5 default) × timestamp size (~24 bytes)

**Half-Open Timing**: Lazy evaluation with timestamp check
- **Rationale**: No background threads needed, simpler implementation
- **Implementation**: Check `time.time() >= next_test_time` on each request
- **Benefit**: Zero overhead when circuit is closed

---

## 2. Retry Timing Strategies

### Research Question
How to integrate custom backoff strategies with httpx and existing ProxyRotator?

### Findings

**Tenacity Integration**:
- Provides `@retry` decorator and `Retrying` class
- Supports custom `wait` strategies (exponential, linear, fixed)
- Has built-in jitter support (`wait_random_exponential`)
- Can combine multiple wait strategies

**Backoff Calculation**:
```python
# Exponential: delay = base * (multiplier ** attempt)
# With cap: delay = min(base * (multiplier ** attempt), max_delay)
# With jitter: delay = delay * random.uniform(0.5, 1.5)
```

**Async vs Sync**:
- httpx supports both sync and async
- ProxyRotator currently sync-only
- Tenacity supports both via `@retry` (sync) and `@retry_async` (async)

### Decision

**Tenacity Usage**: Custom wait strategy class
- **Rationale**: More control than decorator, explicit retry logic
- **Implementation**: Create `RetryExecutor` class using `tenacity.Retrying`
- **Pattern**:
  ```python
  retrying = Retrying(
      wait=wait_strategy,
      stop=stop_after_attempt(policy.max_attempts),
      retry=retry_if_exception_type(RetryableError)
  )
  for attempt in retrying:
      with attempt:
          return make_request()
  ```

**Backoff Implementation**: Custom wait callable
- **Rationale**: Tenacity allows custom wait functions
- **Implementation**: Convert RetryPolicy to tenacity wait strategy
- **Support**: Exponential, linear, fixed with cap and optional jitter

**Sync First, Async Later**: Start with sync implementation
- **Rationale**: Existing ProxyRotator is sync, reduces initial complexity
- **Future**: Add async support in separate user story if needed
- **Compatibility**: Tenacity supports both patterns

---

## 3. Metrics Collection & Storage

### Research Question
What data structure efficiently stores 24 hours of retry metrics in memory?

### Findings

**Time-Series Storage Options**:
- Dict with timestamp keys: Flexible but unbounded growth
- Deque with time-based eviction: O(1) append, automatic cleanup
- Circular buffer: Fixed size, complex indexing
- External TSDB (Prometheus, InfluxDB): Overkill for in-memory requirement

**Memory Estimation** (10k requests/hour × 24h = 240k records):
- Per RetryAttempt: ~200 bytes (request_id, proxy_id, timestamps, outcome)
- Total: 240k × 200 bytes = 48 MB
- With aggregation: ~5-10 MB (hourly rollups)

**Lock Contention**:
- High write frequency (every retry attempt)
- Lower read frequency (API queries)
- Reader-writer lock vs simple lock

### Decision

**Data Structure**: Deque with periodic aggregation
- **Rationale**: Balance memory efficiency with query performance
- **Implementation**:
  - Raw events in bounded deque (last 1 hour, ~10k entries)
  - Hourly aggregates in dict (last 24 hours, 24 entries)
  - Periodic rollup (every 5 minutes)
- **Memory**: <10 MB for 10k req/hour workload

**Lock Strategy**: Single `threading.Lock` with batching
- **Rationale**: Simple, adequate for expected load
- **Pattern**: Batch updates when possible, quick lock acquire/release
- **Optimization**: Lock-free reads of immutable aggregates

**Query Performance**:
- Recent data (last hour): Direct deque scan
- Historical data (>1 hour ago): Pre-aggregated hourly summaries
- Target: <100ms for 24h queries (SC-007 requirement)

---

## 4. Integration with Existing System

### Research Question
How to extend ProxyRotator without breaking existing functionality?

### Findings

**ProxyRotator Extension Points**:
- Current: `request(url, method, **kwargs)` method
- Strategy pattern: `_select_proxy()` internal method
- No retry logic currently

**Backward Compatibility Patterns**:
- Optional parameter: `retry_policy: Optional[RetryPolicy] = None`
- Feature flag: `enable_retries: bool = True`
- Separate class: `RetryableProxyRotator(ProxyRotator)`

**Health Monitoring Integration**:
- Feature 006 provides `HealthMonitor` class
- Circuit breaker can use health data for initial state
- Avoid duplicate failure tracking

### Decision

**Integration Approach**: Optional parameter with sensible default
- **Rationale**: No breaking changes, explicit opt-in possible
- **Implementation**:
  ```python
  class ProxyRotator:
      def __init__(self, ..., retry_policy: Optional[RetryPolicy] = None):
          self.retry_policy = retry_policy or RetryPolicy()  # Default enabled
          self.circuit_breakers = {}  # proxy_id -> CircuitBreaker
          self.retry_executor = RetryExecutor(self)
  ```

**Strategy Integration**: Modify `_select_proxy()` to filter circuit breaker open proxies
- **Rationale**: Minimal changes, reuses existing strategy logic
- **Pattern**: Pre-filter available proxies before strategy selection

**Health Monitoring Coordination**: Circuit breaker as separate concern
- **Rationale**: Different purposes (retry vs continuous monitoring)
- **Implementation**: Circuit breaker tracks request-level failures independently
- **Future**: Health Monitor can trigger circuit breaker reset if desired

**Backward Compatibility**: 100% compatible
- **Rationale**: Default retry policy provides sensible behavior
- **Verification**: All existing tests pass without modification
- **Opt-out**: Set `retry_policy=None` to disable retries

---

## 5. Testing Strategies

### Research Question
How to test time-dependent retry logic, race conditions, and circuit breaker state machines?

### Findings

**Time-Dependent Testing**:
- Mock `time.time()` and `time.sleep()` 
- Use `freezegun` library for time control
- Fast-forward time in tests instead of actual delays

**Race Condition Testing**:
- `pytest-xdist` for parallel test execution
- Thread pools for concurrent request simulation
- Stress testing with `locust` or custom scripts

**Property-Based Testing** (Hypothesis):
- Generate random state transitions
- Verify invariants (e.g., closed → open only after N failures)
- Find edge cases automatically

### Decision

**Time Mocking**: Use unittest.mock for time control
- **Rationale**: Stdlib, no extra dependencies
- **Pattern**:
  ```python
  with patch('time.time', return_value=1000):
      with patch('time.sleep') as mock_sleep:
          # Test retry timing
          assert mock_sleep.call_args_list == [call(1), call(2), call(4)]
  ```

**Concurrency Testing**: Thread pool + assertions
- **Rationale**: Direct, no test framework magic
- **Implementation**:
  ```python
  with ThreadPoolExecutor(max_workers=100) as executor:
      futures = [executor.submit(rotator.request, url) for _ in range(1000)]
      results = [f.result() for f in futures]
  # Assert no race conditions in circuit breaker states
  ```

**Hypothesis Testing**: State machine property tests
- **Rationale**: Find edge cases in circuit breaker logic
- **Pattern**:
  ```python
  @given(st.lists(st.booleans(), min_size=10))  # success/failure sequence
  def test_circuit_breaker_invariants(outcomes):
      # Verify state transitions follow rules
      # Verify failure count matches outcomes
  ```

**Performance Testing**: Benchmark suite
- **Rationale**: Verify SC-004, SC-006, SC-007 requirements
- **Tools**: pytest-benchmark for timing, custom load generator

---

## Summary of Decisions

| Decision Area | Choice | Rationale |
|---------------|--------|-----------|
| Thread Safety | `threading.Lock` per CircuitBreaker | Simple, sufficient, well-tested |
| Rolling Window | `collections.deque` with timestamp filtering | O(1) ops, auto-eviction, stdlib |
| Half-Open Timing | Lazy evaluation with timestamp check | No background threads, simpler |
| Retry Framework | Tenacity with custom wait strategy | Flexible, mature, explicit control |
| Backoff Implementation | Custom wait callable for Tenacity | Supports all required strategies + jitter |
| Metrics Storage | Deque (1h raw) + Dict (24h aggregates) | Memory-efficient, fast queries |
| ProxyRotator Integration | Optional retry_policy parameter | No breaking changes, explicit opt-in |
| Strategy Integration | Pre-filter proxies before selection | Minimal changes, reuses logic |
| Time Mocking | `unittest.mock` | Stdlib, no extra dependencies |
| Concurrency Testing | ThreadPoolExecutor + assertions | Direct, no magic |
| Property Testing | Hypothesis for state machine | Finds edge cases automatically |

**All "NEEDS CLARIFICATION" items resolved. Ready for Phase 1 (Data Model & Contracts).**
