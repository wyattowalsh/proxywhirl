# Phase 1: Data Model & Contracts

**Feature**: 014-retry-failover-logic  
**Date**: 2025-11-02  
**Status**: Complete  
**Prerequisites**: research.md complete

## Overview

This document defines the data models, state machines, and entity relationships for the retry and failover logic feature. All entities use Pydantic v2 for validation and type safety.

---

## Core Entities

### 1. RetryPolicy (Configuration)

**Purpose**: Configuration object defining retry behavior for requests.

**Pydantic Model**:
```python
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class BackoffStrategy(str, Enum):
    """Retry backoff timing strategy"""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIXED = "fixed"

class RetryPolicy(BaseModel):
    """Configuration for retry behavior"""
    
    max_attempts: int = Field(default=3, ge=1, le=10)
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL
    base_delay: float = Field(default=1.0, gt=0, le=60)  # seconds
    multiplier: float = Field(default=2.0, gt=1, le=10)  # for exponential
    max_backoff_delay: float = Field(default=30.0, gt=0, le=300)  # cap
    jitter: bool = Field(default=False)
    retry_status_codes: List[int] = Field(default=[502, 503, 504])
    timeout: Optional[float] = Field(default=None, gt=0)  # total request timeout
    retry_non_idempotent: bool = Field(default=False)
    
    @field_validator('retry_status_codes')
    @classmethod
    def validate_status_codes(cls, v):
        if not all(500 <= code < 600 for code in v):
            raise ValueError("Status codes must be 5xx errors")
        return v
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number (0-indexed)"""
        if self.backoff_strategy == BackoffStrategy.EXPONENTIAL:
            delay = self.base_delay * (self.multiplier ** attempt)
        elif self.backoff_strategy == BackoffStrategy.LINEAR:
            delay = self.base_delay * (attempt + 1)
        else:  # FIXED
            delay = self.base_delay
        
        delay = min(delay, self.max_backoff_delay)
        
        if self.jitter:
            import random
            delay = delay * random.uniform(0.5, 1.5)
        
        return delay
```

**Relationships**:
- One RetryPolicy per ProxyRotator (global)
- Can be overridden per request (request-level)

**Lifecycle**: Immutable once created, replaced to update

---

### 2. CircuitBreaker (State Machine)

**Purpose**: Track proxy failure state and manage availability in rotation pool.

**State Enum**:
```python
class CircuitBreakerState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"        # Normal operation, proxy available
    OPEN = "open"            # Proxy excluded from rotation
    HALF_OPEN = "half_open"  # Testing recovery with limited requests
```

**Pydantic Model**:
```python
from collections import deque
from datetime import datetime, timezone
from threading import Lock
from typing import Deque, Optional

class CircuitBreaker(BaseModel):
    """Circuit breaker for a single proxy"""
    
    proxy_id: str
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = Field(default=0, ge=0)
    failure_window: Deque[float] = Field(default_factory=deque)  # timestamps
    failure_threshold: int = Field(default=5, ge=1)
    window_duration: float = Field(default=60.0, gt=0)  # seconds
    timeout_duration: float = Field(default=30.0, gt=0)  # seconds until half-open
    next_test_time: Optional[float] = None  # Unix timestamp
    last_state_change: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Not serialized - runtime only
    _lock: Lock = Field(default_factory=Lock, exclude=True)
    
    class Config:
        arbitrary_types_allowed = True  # For Lock and deque
    
    def record_failure(self) -> None:
        """Record a failure and update state if threshold reached"""
        with self._lock:
            import time
            now = time.time()
            
            # Add failure to window
            self.failure_window.append(now)
            
            # Remove failures outside rolling window
            cutoff = now - self.window_duration
            while self.failure_window and self.failure_window[0] < cutoff:
                self.failure_window.popleft()
            
            self.failure_count = len(self.failure_window)
            
            # Transition to OPEN if threshold exceeded
            if self.state == CircuitBreakerState.CLOSED and \
               self.failure_count >= self.failure_threshold:
                self._transition_to_open(now)
            elif self.state == CircuitBreakerState.HALF_OPEN:
                # Test failed, reopen circuit
                self._transition_to_open(now)
    
    def record_success(self) -> None:
        """Record a success and potentially close circuit"""
        with self._lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                # Test succeeded, close circuit
                self._transition_to_closed()
    
    def should_attempt_request(self) -> bool:
        """Check if proxy is available for requests"""
        with self._lock:
            import time
            now = time.time()
            
            if self.state == CircuitBreakerState.CLOSED:
                return True
            elif self.state == CircuitBreakerState.OPEN:
                # Check if timeout elapsed, transition to half-open
                if self.next_test_time and now >= self.next_test_time:
                    self._transition_to_half_open()
                    return True
                return False
            else:  # HALF_OPEN
                return True
    
    def _transition_to_open(self, now: float) -> None:
        """Transition to OPEN state"""
        self.state = CircuitBreakerState.OPEN
        self.next_test_time = now + self.timeout_duration
        self.last_state_change = datetime.now(timezone.utc)
    
    def _transition_to_half_open(self) -> None:
        """Transition to HALF_OPEN state"""
        self.state = CircuitBreakerState.HALF_OPEN
        self.last_state_change = datetime.now(timezone.utc)
    
    def _transition_to_closed(self) -> None:
        """Transition to CLOSED state"""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.failure_window.clear()
        self.next_test_time = None
        self.last_state_change = datetime.now(timezone.utc)
```

**State Transition Diagram**:
```
    CLOSED ────────────────────────────> OPEN
      ^          (N failures in window)    │
      │                                    │ (timeout elapsed)
      │                                    ↓
      └───────────────────────────── HALF_OPEN
            (test request succeeds)        │
                                          │ (test fails)
                                          ↓
                                         OPEN
```

**Relationships**:
- One CircuitBreaker per Proxy in rotation pool
- Managed by ProxyRotator
- Consulted before proxy selection

**Lifecycle**: Created on-demand when proxy first used, reset on system restart

---

### 3. RetryAttempt (Metrics Record)

**Purpose**: Record individual retry attempt for metrics and debugging.

**Pydantic Model**:
```python
class RetryOutcome(str, Enum):
    """Outcome of a retry attempt"""
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    CIRCUIT_OPEN = "circuit_open"

class RetryAttempt(BaseModel):
    """Record of a single retry attempt"""
    
    request_id: str
    attempt_number: int = Field(ge=0)
    proxy_id: str
    timestamp: datetime
    outcome: RetryOutcome
    status_code: Optional[int] = None
    delay_before: float = Field(ge=0)  # seconds waited before this attempt
    latency: float = Field(ge=0)  # request duration in seconds
    error_message: Optional[str] = None
```

**Relationships**:
- Multiple RetryAttempts per request
- Aggregated into RetryMetrics

**Lifecycle**: Created per retry attempt, retained for 24 hours, then evicted

---

### 4. RetryMetrics (Aggregated Metrics)

**Purpose**: Collect and expose retry statistics for monitoring and optimization.

**Pydantic Model**:
```python
from typing import Dict, List
from collections import defaultdict, deque

class CircuitBreakerEvent(BaseModel):
    """Circuit breaker state change event"""
    proxy_id: str
    from_state: CircuitBreakerState
    to_state: CircuitBreakerState
    timestamp: datetime
    failure_count: int

class HourlyAggregate(BaseModel):
    """Hourly aggregated metrics"""
    hour: datetime  # Truncated to hour
    total_requests: int = 0
    total_retries: int = 0
    success_by_attempt: Dict[int, int] = Field(default_factory=dict)
    failure_by_reason: Dict[str, int] = Field(default_factory=dict)
    avg_latency: float = 0.0

class RetryMetrics(BaseModel):
    """Aggregated retry metrics"""
    
    # Current period (last hour, raw data)
    current_attempts: Deque[RetryAttempt] = Field(default_factory=deque)
    
    # Historical data (last 24 hours, aggregated)
    hourly_aggregates: Dict[datetime, HourlyAggregate] = Field(default_factory=dict)
    
    # Circuit breaker events
    circuit_breaker_events: List[CircuitBreakerEvent] = Field(default_factory=list)
    
    # Configuration
    retention_hours: int = Field(default=24)
    max_current_attempts: int = Field(default=10000)  # ~1 hour at 10k req/hour
    
    # Runtime (not serialized)
    _lock: Lock = Field(default_factory=Lock, exclude=True)
    
    class Config:
        arbitrary_types_allowed = True
    
    def record_attempt(self, attempt: RetryAttempt) -> None:
        """Record a retry attempt"""
        with self._lock:
            self.current_attempts.append(attempt)
            
            # Trim if exceeds max
            while len(self.current_attempts) > self.max_current_attempts:
                self.current_attempts.popleft()
    
    def record_circuit_breaker_event(self, event: CircuitBreakerEvent) -> None:
        """Record circuit breaker state change"""
        with self._lock:
            self.circuit_breaker_events.append(event)
            
            # Keep last 1000 events
            if len(self.circuit_breaker_events) > 1000:
                self.circuit_breaker_events = self.circuit_breaker_events[-1000:]
    
    def aggregate_hourly(self) -> None:
        """Aggregate current_attempts into hourly summaries"""
        with self._lock:
            # Group attempts by hour
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            cutoff = now - timedelta(hours=self.retention_hours)
            
            # Process current attempts
            attempts_by_hour = defaultdict(list)
            for attempt in self.current_attempts:
                if attempt.timestamp >= cutoff:
                    hour = attempt.timestamp.replace(minute=0, second=0, microsecond=0)
                    attempts_by_hour[hour].append(attempt)
            
            # Create/update hourly aggregates
            for hour, attempts in attempts_by_hour.items():
                if hour not in self.hourly_aggregates:
                    self.hourly_aggregates[hour] = HourlyAggregate(hour=hour)
                
                agg = self.hourly_aggregates[hour]
                agg.total_requests += len(set(a.request_id for a in attempts))
                agg.total_retries += len(attempts)
                
                for attempt in attempts:
                    if attempt.outcome == RetryOutcome.SUCCESS:
                        agg.success_by_attempt[attempt.attempt_number] = \
                            agg.success_by_attempt.get(attempt.attempt_number, 0) + 1
                    else:
                        reason = attempt.error_message or attempt.outcome.value
                        agg.failure_by_reason[reason] = \
                            agg.failure_by_reason.get(reason, 0) + 1
            
            # Remove old aggregates
            self.hourly_aggregates = {
                h: agg for h, agg in self.hourly_aggregates.items()
                if h >= cutoff
            }
    
    def get_summary(self) -> Dict:
        """Get metrics summary for API response"""
        with self._lock:
            total_retries = len(self.current_attempts) + \
                sum(agg.total_retries for agg in self.hourly_aggregates.values())
            
            success_by_attempt = defaultdict(int)
            for agg in self.hourly_aggregates.values():
                for attempt_num, count in agg.success_by_attempt.items():
                    success_by_attempt[attempt_num] += count
            
            return {
                "total_retries": total_retries,
                "success_by_attempt": dict(success_by_attempt),
                "circuit_breaker_events_count": len(self.circuit_breaker_events),
                "retention_hours": self.retention_hours
            }
```

**Relationships**:
- Aggregates multiple RetryAttempt records
- One RetryMetrics instance per ProxyRotator

**Lifecycle**: Continuous accumulation, periodic aggregation (every 5 minutes), 24h retention

---

## Data Flow

### Request Flow with Retry
```
1. User calls rotator.request(url)
2. ProxyRotator checks RetryPolicy
3. If retries enabled:
   a. Check all CircuitBreakers, filter out OPEN proxies
   b. Select proxy from available pool
   c. Attempt request
   d. If failure:
      - Record failure in CircuitBreaker
      - Create RetryAttempt record
      - Calculate backoff delay
      - Go to step 3b (with new proxy)
   e. If success or max attempts:
      - Record final RetryAttempt
      - Return response or error
4. Update RetryMetrics
```

### Circuit Breaker State Updates
```
On request failure:
1. CircuitBreaker.record_failure()
2. Check failure count in rolling window
3. If >= threshold: transition CLOSED → OPEN
4. Record CircuitBreakerEvent in RetryMetrics

On request success in HALF_OPEN:
1. CircuitBreaker.record_success()
2. Transition HALF_OPEN → CLOSED
3. Record CircuitBreakerEvent

On timeout in OPEN state:
1. Next request checks should_attempt_request()
2. If timeout elapsed: transition OPEN → HALF_OPEN
3. Allow one test request
```

---

## Memory Management

**Estimated Memory Usage** (10k requests/hour, 3 retries avg):

| Component | Size per Entry | Count | Total |
|-----------|----------------|-------|-------|
| RetryAttempt (current) | ~200 bytes | 10,000 | ~2 MB |
| HourlyAggregate | ~500 bytes | 24 | ~12 KB |
| CircuitBreaker | ~500 bytes | 100 proxies | ~50 KB |
| CircuitBreakerEvent | ~150 bytes | 1,000 | ~150 KB |
| **Total** | | | **~2.5 MB** |

**Cleanup Strategy**:
- RetryAttempt: Rolling deque, auto-eviction at 10k entries
- HourlyAggregate: Periodic cleanup (every hour), remove >24h old
- CircuitBreakerEvent: Keep last 1000 events
- CircuitBreaker: Reset on system restart, no persistence

---

## Thread Safety

**Concurrency Patterns**:
- CircuitBreaker: `threading.Lock` per instance for state transitions
- RetryMetrics: Single `threading.Lock` for all updates
- RetryPolicy: Immutable, no locking needed

**Lock Acquisition Order** (prevent deadlocks):
1. RetryMetrics lock (if needed)
2. CircuitBreaker lock (if needed)
3. Never acquire in reverse order

---

## API Data Models

See `/specs/014-retry-failover-logic/contracts/retry-api.yaml` for full OpenAPI specification.

**Request Models**:
- `RetryPolicyRequest`: User-provided retry policy configuration
- `CircuitBreakerResetRequest`: Manual circuit breaker reset

**Response Models**:
- `RetryPolicyResponse`: Current retry policy
- `CircuitBreakerResponse`: Circuit breaker state for a proxy
- `RetryMetricsResponse`: Aggregated metrics summary
- `TimeSeriesResponse`: Time-series retry data

---

**Data Model Status**: ✅ Complete - Ready for API contract definition
