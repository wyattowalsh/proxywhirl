# Implementation Plan: Intelligent Rotation Strategies

**Branch**: `004-rotation-strategies-intelligent` | **Date**: 2025-10-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `.specify/specs/004-rotation-strategies-intelligent/spec.md`

## Summary

The Intelligent Rotation Strategies feature enhances ProxyWhirl's existing basic rotation strategies (round-robin, random, weighted, least-used) with advanced, data-driven selection algorithms. The implementation adds comprehensive request metadata tracking (started, completed, successful, failed, in-flight), performance-based selection using Exponential Moving Average (EMA) for response times, session persistence with configurable timeouts, geo-targeted proxy selection, strategy composition (filtering + selection), and plugin architecture for custom strategies. All strategies skip unhealthy proxies, support thread-safe concurrent access, enable hot-swapping without request drops, and validate required metadata with configurable fallback strategies. The system uses sliding time windows (default 1 hour) to prevent counter staleness and maintains <5ms strategy selection overhead while supporting 10,000+ concurrent requests.

## Technical Context

**Language/Version**: Python 3.9+ (target: 3.9, 3.10, 3.11, 3.12, 3.13)

**Primary Dependencies**:
- `pydantic>=2.0.0` - Data validation and settings (already used in core)
- Standard library: `threading` (locks for thread safety), `collections.defaultdict` (metadata storage), `typing.Protocol` (strategy interface)
- Optional: `typing_extensions>=4.0.0` for Python 3.9 compatibility (if needed for Protocol features)

**Storage**:
- **In-Memory Primary**: Proxy metadata stored in `ProxyRotator` instance
  - `Dict[UUID, ProxyMetadata]` - Comprehensive request tracking per proxy
  - `Dict[str, ProxySession]` - Session ID to proxy assignment mapping
  - Thread-safe access via `threading.Lock`
- **Sliding Window**: Time-based circular buffers for request counts (configurable window, default 1 hour)
- **EMA State**: Per-proxy exponential moving average state (current average + alpha parameter)
- **Optional Persistence**: Metadata can be saved/restored via existing `storage.py` backends

**Testing**: 
- `pytest>=7.4.0` with `pytest-asyncio>=0.21.0` for async tests
- `hypothesis>=6.88.0` for property-based testing of strategy invariants
- `pytest-benchmark` for performance validation (<5ms overhead, 10k req/s throughput)
- `pytest-timeout` for deadlock detection in concurrent tests

**Target Platform**: Cross-platform library (Linux, macOS, Windows) - pure Python, no platform-specific dependencies

**Project Type**: Single project - enhancements to existing `proxywhirl/` package (modify `strategies.py`, `models.py`, `rotator.py`)

**Performance Goals**:
- Strategy selection overhead: <5ms per request (SC-007)
- Concurrent request handling: 10,000 requests without deadlocks (SC-008)
- Strategy hot-swap: <100ms for new requests (SC-009)
- Custom plugin loading: <1 second (SC-010)
- Round-robin distribution: ±1 request variance (SC-001)
- Random distribution: 10% variance over 1000 requests (SC-002)
- Performance-based strategy: 15-25% latency reduction vs round-robin (SC-004)

**Constraints**:
- Thread-safe: All strategy operations must support concurrent access
- No blocking I/O: Strategy selection must be synchronous and fast
- Backward compatibility: Existing strategies (RoundRobinStrategy, RandomStrategy, WeightedStrategy, LeastUsedStrategy) must continue working unchanged
- Memory efficiency: Sliding window must not grow unbounded
- Session persistence: 99.9% same-proxy guarantee for same-session requests (SC-005)

**Scale/Scope**:
- Strategy count: 6 built-in strategies (round-robin, random, weighted, least-used, performance-based, session, geo-targeted)
- Metadata fields per proxy: 8+ (requests started/completed/successful/failed/active, EMA state, session assignments, geo-location)
- Concurrent sessions: 100+ active sessions simultaneously
- Pool size: Optimized for 10-1000 proxies per pool
- Request tracking window: Configurable (default 1 hour), auto-pruning old data

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Library-First Architecture ✅ PASS

- All rotation strategies are pure Python classes implementing `RotationStrategy` protocol
- No CLI/web dependencies - strategies usable via direct Python import
- Clear public API: `proxywhirl.strategies` module exports all strategy classes
- Context manager support not required (strategies are stateless or maintain internal state only)
- Full type hints with `py.typed` marker (constitutional requirement already met)
- **Validation**: Feature works via `from proxywhirl.strategies import PerformanceBasedStrategy`

### II. Test-First Development ✅ PASS

- Tests MUST be written BEFORE implementation (per tasks.md workflow)
- Property-based tests with Hypothesis for strategy invariants:
  - Round-robin: Sequential selection property
  - Random: Uniform distribution property
  - Performance-based: Faster proxies selected more frequently
  - Session: Same proxy for same session ID
- Integration tests validate all 6 user stories independently
- Coverage target: 85%+ (consistent with existing codebase: 88%+)
- **Validation**: Task phases show tests written and failing before implementation

### III. Type Safety & Runtime Validation ✅ PASS

- All strategy classes fully type-hinted with Protocol interface
- Pydantic models for metadata structures (`ProxyMetadata`, `ProxySession`, `StrategyConfig`)
- Runtime validation for:
  - Missing metadata (reject with clear error per FR-021)
  - Invalid session IDs (validate format before lookup)
  - Configuration parameters (alpha ∈ (0,1), window duration > 0)
- Pass `mypy --strict` (constitutional requirement)
- **Validation**: All PRs pass mypy and demonstrate validation for invalid inputs

### IV. Independent User Stories ✅ PASS

- US1 (Round-Robin): Independent - enhances existing strategy, no new dependencies
- US2 (Random Selection): Independent - enhances existing strategy
- US3 (Least-Used): Independent - adds metadata tracking, self-contained
- US4 (Performance-Based): Independent - requires EMA tracking only
- US5 (Session Persistence): Independent - requires session mapping only
- US6 (Geo-Targeted): Independent - requires geo-location metadata only
- Each story has standalone value and can be tested in isolation
- **Validation**: spec.md defines independent acceptance scenarios for each story

### V. Performance Standards ✅ PASS

- Strategy selection: <5ms overhead (SC-007) - measured via `pytest-benchmark`
- Concurrent requests: 10,000 without deadlocks (SC-008) - validated with `asyncio.gather` stress test
- Hot-swap: <100ms (SC-009) - measured with atomic strategy reference swap
- Thread-safe lock contention: <1% overhead via fine-grained locking (per-proxy locks where possible)
- Memory: Sliding window auto-prunes, bounded memory regardless of request count
- **Validation**: Benchmark suite in `tests/benchmarks/test_strategy_performance.py`

### VI. Security-First Design ✅ PASS

- No credential handling in strategies (credentials remain in `Proxy.username/password` using `SecretStr`)
- Session IDs validated to prevent injection (alphanumeric + hyphens only)
- Geo-location data sourced from trusted metadata (no external API calls in selection path)
- Thread-safe access prevents race conditions that could expose sensitive state
- Logging redacts session IDs and proxy credentials
- **Validation**: Security audit focuses on metadata access patterns and logging

### VII. Simplicity & Flat Architecture ✅ PASS

- No new modules: Enhancements to existing `strategies.py` (add 3 new strategy classes)
- Modifications to existing modules:
  - `models.py`: Add `ProxyMetadata`, `ProxySession`, `StrategyConfig` models
  - `rotator.py`: Add metadata tracking, session management methods
- Total modules after feature: 15 (unchanged from current)
- No sub-packages, no circular dependencies
- **Validation**: Single-module enhancement preserves flat architecture

**Overall: ✅ FULL PASS** (No constitutional violations)

## Project Structure

### Documentation (this feature)

```text
.specify/specs/004-rotation-strategies-intelligent/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── strategy-interface.md  # Protocol definition and guarantees
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
proxywhirl/                      # Existing package (flat structure maintained)
├── __init__.py                  # Public API exports (add new strategies)
├── models.py                    # MODIFIED: Add ProxyMetadata, ProxySession, StrategyConfig, GeoLocation
├── rotator.py                   # MODIFIED: Add metadata tracking, session management, strategy composition
├── strategies.py                # MODIFIED: Enhance existing + add PerformanceBasedStrategy, SessionStrategy, GeoTargetedStrategy
├── fetchers.py                  # (existing - unchanged)
├── storage.py                   # (existing - unchanged)
├── browser.py                   # (existing - unchanged)
├── utils.py                     # (existing - unchanged)
├── exceptions.py                # MODIFIED: Add StrategyMetadataError, SessionNotFoundError
├── cli.py                       # (existing - unchanged for this feature)
├── config.py                    # MODIFIED: Add strategy configuration options
├── api.py                       # (existing - unchanged for this feature)
└── py.typed                     # (existing - type marker)

tests/
├── unit/
│   ├── test_strategies.py              # MODIFIED: Expand for new strategies
│   ├── test_strategy_metadata.py       # NEW: Test metadata tracking
│   ├── test_strategy_sessions.py       # NEW: Test session persistence
│   ├── test_strategy_composition.py    # NEW: Test strategy chaining
│   └── test_strategy_config.py         # NEW: Test configuration validation
├── integration/
│   ├── test_roundrobin_rotation.py     # MODIFIED: Enhanced acceptance tests
│   ├── test_random_rotation.py         # MODIFIED: Enhanced acceptance tests
│   ├── test_leastused_rotation.py      # MODIFIED: Enhanced acceptance tests
│   ├── test_performance_rotation.py    # NEW: Performance-based strategy integration
│   ├── test_session_persistence.py     # NEW: Session strategy integration
│   ├── test_geo_targeting.py           # NEW: Geo-targeted strategy integration
│   └── test_strategy_hotswap.py        # NEW: Hot-swapping integration tests
├── property/
│   ├── test_strategy_invariants.py     # NEW: Hypothesis property tests
│   └── test_ema_convergence.py         # NEW: EMA correctness properties
└── benchmarks/
    └── test_strategy_performance.py    # NEW: Performance validation (<5ms, 10k req/s)

examples/
├── strategy_examples.py         # NEW: Example usage of all strategies
└── custom_strategy_plugin.py    # NEW: Example custom strategy implementation
```

**Structure Decision**: Single project structure maintained. All enhancements contained within existing modules (`strategies.py`, `models.py`, `rotator.py`). This preserves the flat architecture while adding sophisticated rotation capabilities. No new modules created, keeping total count at 15. Strategy implementations follow Protocol pattern for extensibility without requiring abstract base classes or complex inheritance.

## Complexity Tracking

> **No constitutional violations - this section is empty per template guidance**

No complexity threshold exceeded. Feature enhances existing modules without adding new modules or sub-packages.

---

## Phase 0: Research & Design Foundation

**Goal**: Establish algorithmic foundations and validate technical approach for intelligent rotation strategies.

**Duration**: 1-2 days

### Research Areas

#### 1. Exponential Moving Average (EMA) for Response Time Tracking

**Research Questions**:
- What alpha values provide optimal balance between responsiveness and stability for proxy performance tracking?
- How does EMA compare to simple moving average (SMA) for proxy latency tracking in high-variance scenarios?
- What initialization strategy should be used when a proxy has no prior response time data?

**Approach**:
- Literature review: EMA in network latency monitoring, time-series smoothing
- Simulation: Test alpha values (0.1, 0.2, 0.3, 0.5) against synthetic proxy latency data with sudden degradation events
- Benchmark: Compare EMA vs SMA memory usage and computational cost
- **Deliverable**: `research.md` section documenting recommended alpha range (default: 0.2-0.3) with rationale

#### 2. Sliding Time Window Implementation

**Research Questions**:
- What data structure efficiently implements sliding time windows with automatic pruning?
- How should window boundaries be handled (fixed intervals vs continuous sliding)?
- What pruning strategy minimizes overhead while preventing unbounded growth?

**Approach**:
- Survey implementations: `collections.deque`, circular buffer, bucketed time windows
- Prototype: Implement 3 approaches and measure memory + pruning overhead
- Trade-off analysis: Accuracy vs efficiency for different window sizes (1 min, 1 hour, 24 hours)
- **Deliverable**: `research.md` section documenting chosen approach (likely: bucketed time windows with lazy pruning)

#### 3. Thread-Safe Concurrent Access Patterns

**Research Questions**:
- Where should locks be placed to minimize contention while ensuring correctness?
- Should locking be coarse-grained (entire pool) or fine-grained (per-proxy)?
- How do read-write locks compare to standard locks for mostly-read workloads?

**Approach**:
- Pattern review: Lock striping, reader-writer locks, lock-free algorithms
- Contention analysis: Measure lock wait times under 1k, 5k, 10k concurrent requests
- Deadlock prevention: Validate no cyclic lock dependencies in proposed design
- **Deliverable**: `research.md` section documenting locking strategy with contention benchmarks

#### 4. Strategy Composition Architecture

**Research Questions**:
- How should strategies compose (filtering + selection)?
- Should composition be explicit (wrapper classes) or implicit (strategy chains)?
- How does composition affect performance and testability?

**Approach**:
- Design patterns: Decorator, Chain of Responsibility, Strategy composition
- Prototype: Implement geo-filtering + performance-based selection using each pattern
- Trade-off: Flexibility vs complexity vs performance
- **Deliverable**: `research.md` section documenting chosen composition pattern

#### 5. Plugin Architecture for Custom Strategies

**Research Questions**:
- How should custom strategies be discovered and loaded (entry points, directory scanning, explicit registration)?
- What validation should occur when loading custom strategies?
- How can plugin errors be isolated to prevent system-wide failures?

**Approach**:
- Survey approaches: setuptools entry points, importlib, explicit factory registration
- Security review: Prevent arbitrary code execution, validate protocol conformance
- Error handling: Plugin load failures should not crash ProxyRotator
- **Deliverable**: `research.md` section documenting plugin loading mechanism (likely: explicit registration via `ProxyRotator.register_strategy()`)

### Research Deliverable: `research.md`

**Contents**:
1. **EMA Analysis**: Recommended alpha range (0.2-0.3), initialization strategy (use first request RTT), convergence properties
2. **Sliding Window Design**: Bucketed time windows with 1-minute buckets, lazy pruning on access, memory bounds
3. **Concurrency Model**: Fine-grained per-proxy locks for metadata updates, coarse lock for pool modifications, read-write lock for strategy hot-swap
4. **Composition Pattern**: Explicit filtering + selection via `CompositeStrategy` wrapper class
5. **Plugin Architecture**: Explicit registration via `register_strategy(name, strategy_class)`, protocol validation at registration time

---

## Phase 1: Data Model & Contracts Design

**Goal**: Define comprehensive data models for metadata tracking and establish strategy contracts.

**Duration**: 2-3 days

### 1.1 Enhanced Data Models (`models.py`)

**New Models**:

```python
class ProxyMetadata(BaseModel):
    """Comprehensive request tracking metadata per proxy."""
    proxy_id: UUID
    requests_started: int = 0
    requests_completed: int = 0
    requests_successful: int = 0
    requests_failed: int = 0
    requests_active: int = 0  # In-flight requests
    ema_response_time_ms: Optional[float] = None
    ema_alpha: float = 0.25  # Configurable smoothing factor
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Sliding window tracking (bucketed by time)
    request_window: Dict[datetime, int] = Field(default_factory=dict)  # timestamp -> count
    window_duration_seconds: int = 3600  # Default 1 hour
    
    def increment_started(self) -> None:
        """Atomically increment requests_started and active counters."""
        self.requests_started += 1
        self.requests_active += 1
        self._update_window()
    
    def record_completion(self, success: bool, response_time_ms: float) -> None:
        """Record request completion and update EMA."""
        self.requests_completed += 1
        self.requests_active -= 1
        if success:
            self.requests_successful += 1
        else:
            self.requests_failed += 1
        
        # Update EMA
        if self.ema_response_time_ms is None:
            self.ema_response_time_ms = response_time_ms
        else:
            self.ema_response_time_ms = (
                self.ema_alpha * response_time_ms +
                (1 - self.ema_alpha) * self.ema_response_time_ms
            )
        
        self.last_updated = datetime.now(timezone.utc)
        self._prune_window()
    
    def _update_window(self) -> None:
        """Add current timestamp to sliding window."""
        bucket = self._get_current_bucket()
        self.request_window[bucket] = self.request_window.get(bucket, 0) + 1
    
    def _prune_window(self) -> None:
        """Remove expired entries from sliding window."""
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=self.window_duration_seconds)
        self.request_window = {
            ts: count for ts, count in self.request_window.items()
            if ts > cutoff
        }
    
    def _get_current_bucket(self) -> datetime:
        """Get current 1-minute bucket timestamp."""
        now = datetime.now(timezone.utc)
        return now.replace(second=0, microsecond=0)
    
    @property
    def window_request_count(self) -> int:
        """Get total requests in current sliding window."""
        self._prune_window()
        return sum(self.request_window.values())


class ProxySession(BaseModel):
    """Session tracking for sticky proxy assignments."""
    session_id: str
    proxy_id: UUID
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_accessed: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    timeout_seconds: int = 1800  # Default 30 minutes
    request_count: int = 0
    
    @property
    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.now(timezone.utc) > self.last_accessed + timedelta(seconds=self.timeout_seconds)
    
    def touch(self) -> None:
        """Update last accessed timestamp."""
        self.last_accessed = datetime.now(timezone.utc)
        self.request_count += 1


class GeoLocation(BaseModel):
    """Geographic location metadata for proxies."""
    country_code: str  # ISO 3166-1 alpha-2 (e.g., "US", "UK", "JP")
    country_name: Optional[str] = None
    region: Optional[str] = None  # State/province
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = None
    
    @field_validator('country_code')
    @classmethod
    def validate_country_code(cls, v: str) -> str:
        """Ensure country code is uppercase and 2 characters."""
        if len(v) != 2:
            raise ValueError("Country code must be 2 characters (ISO 3166-1 alpha-2)")
        return v.upper()


class StrategyConfig(BaseModel):
    """Configuration for rotation strategies."""
    strategy_name: str
    
    # EMA configuration
    ema_alpha: float = Field(default=0.25, ge=0.0, le=1.0)
    
    # Sliding window configuration
    window_duration_seconds: int = Field(default=3600, gt=0)  # 1 hour
    
    # Session configuration
    session_timeout_seconds: int = Field(default=1800, gt=0)  # 30 minutes
    
    # Fallback strategy configuration
    fallback_strategy: Optional[str] = None  # Strategy name to use when primary fails
    
    # Geo-targeting configuration
    preferred_countries: List[str] = Field(default_factory=list)
    
    # Performance thresholds
    max_response_time_ms: Optional[float] = None  # Exclude proxies slower than this
    min_success_rate: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    
    # Composition configuration
    enable_filtering: bool = True
    enable_fallback: bool = True
```

**Modified Models**:

```python
# In Proxy model, add:
class Proxy(BaseModel):
    # ... existing fields ...
    geo_location: Optional[GeoLocation] = None  # NEW: Geographic location metadata
```

### 1.2 Strategy Protocol Enhancement

**Updated Protocol** (in `strategies.py`):

```python
@runtime_checkable
class RotationStrategy(Protocol):
    """Protocol defining interface for proxy rotation strategies."""
    
    def select(
        self,
        pool: ProxyPool,
        metadata: Dict[UUID, ProxyMetadata],
        context: Optional[SelectionContext] = None
    ) -> Proxy:
        """
        Select a proxy from the pool based on strategy logic.
        
        Args:
            pool: The proxy pool to select from
            metadata: Comprehensive metadata for all proxies
            context: Optional request context (session ID, geo preference, etc.)
        
        Returns:
            Selected proxy
        
        Raises:
            ProxyPoolEmptyError: If no suitable proxy is available
            StrategyMetadataError: If required metadata is missing
        """
        ...
    
    def record_result(
        self,
        proxy: Proxy,
        metadata: ProxyMetadata,
        success: bool,
        response_time_ms: float
    ) -> None:
        """
        Record the result of using a proxy.
        
        Args:
            proxy: The proxy that was used
            metadata: Metadata object for this proxy
            success: Whether the request succeeded
            response_time_ms: Response time in milliseconds
        """
        ...
    
    def validate_requirements(
        self,
        pool: ProxyPool,
        metadata: Dict[UUID, ProxyMetadata]
    ) -> bool:
        """
        Validate that pool has required metadata for this strategy.
        
        Args:
            pool: The proxy pool
            metadata: Available metadata
        
        Returns:
            True if requirements met, False otherwise
        """
        ...
    
    @property
    def requires_metadata(self) -> Set[str]:
        """Set of required metadata fields for this strategy."""
        ...


class SelectionContext(BaseModel):
    """Context information for proxy selection."""
    session_id: Optional[str] = None
    preferred_country: Optional[str] = None
    max_response_time_ms: Optional[float] = None
    min_success_rate: Optional[float] = None
    exclude_proxy_ids: Set[UUID] = Field(default_factory=set)
```

### 1.3 Contract Documentation

**Deliverable**: `contracts/strategy-interface.md`

**Contents**:
1. **Protocol Guarantees**:
   - All strategies MUST skip unhealthy proxies
   - All strategies MUST be thread-safe for concurrent calls
   - Selection MUST complete in <5ms
   - Strategies MUST validate metadata requirements before selection

2. **Metadata Contract**:
   - `ProxyMetadata` lifecycle: Created on first request, updated atomically, pruned automatically
   - EMA convergence: Stabilizes within 10 requests for typical alpha (0.2-0.3)
   - Sliding window: Accurate to 1-minute granularity, auto-prunes on access

3. **Session Contract**:
   - Session IDs MUST be unique strings (UUID format recommended)
   - Sessions auto-expire after configurable timeout (default 30 min)
   - Expired sessions automatically pruned on next access
   - Session proxy remains sticky until expiration or proxy failure

4. **Strategy Composition**:
   - Filtering strategies: Remove proxies not meeting criteria (geo, performance)
   - Selection strategies: Choose one proxy from filtered set
   - Composition order: Filter → Select
   - Fallback: Triggered when filter leaves no candidates

5. **Error Handling**:
   - `StrategyMetadataError`: Required metadata missing (with list of missing fields)
   - `SessionNotFoundError`: Session ID not found or expired
   - `ProxyPoolEmptyError`: No healthy proxies available after filtering

### 1.4 Quick Start Guide

**Deliverable**: `quickstart.md`

**Contents**:
```markdown
# Intelligent Rotation Strategies Quick Start

## Basic Usage

### Performance-Based Strategy

```python
from proxywhirl import ProxyRotator
from proxywhirl.strategies import PerformanceBasedStrategy

rotator = ProxyRotator(strategy=PerformanceBasedStrategy(alpha=0.25))
rotator.add_proxies(["http://proxy1.com:8080", "http://proxy2.com:8080"])

# Faster proxies automatically selected more frequently
response = rotator.request("GET", "https://example.com")
```

### Session Persistence

```python
from proxywhirl.strategies import SessionStrategy

strategy = SessionStrategy(timeout_seconds=1800)
rotator = ProxyRotator(strategy=strategy)

# All requests in same session use same proxy
with rotator.session("user-session-123") as session:
    response1 = session.request("GET", "https://api.example.com/login")
    response2 = session.request("GET", "https://api.example.com/profile")
    # Both requests use identical proxy
```

### Geo-Targeted Selection

```python
from proxywhirl.strategies import GeoTargetedStrategy

strategy = GeoTargetedStrategy(
    preferred_countries=["US", "CA"],
    fallback_strategy="round-robin"
)
rotator = ProxyRotator(strategy=strategy)

# Only US/CA proxies selected; falls back to round-robin if none available
response = rotator.request("GET", "https://example.com")
```

### Strategy Composition

```python
from proxywhirl.strategies import CompositeStrategy, GeoTargetedStrategy, PerformanceBasedStrategy

# Filter by geo, then select by performance
strategy = CompositeStrategy(
    filters=[GeoTargetedStrategy(preferred_countries=["US"])],
    selector=PerformanceBasedStrategy(alpha=0.3)
)
rotator = ProxyRotator(strategy=strategy)
```

## Advanced Configuration

### Custom EMA Alpha

```python
# More responsive to recent changes (higher alpha)
strategy = PerformanceBasedStrategy(alpha=0.5)  # Default: 0.25

# More stable, less reactive (lower alpha)
strategy = PerformanceBasedStrategy(alpha=0.1)
```

### Custom Sliding Window

```python
from proxywhirl.config import StrategyConfig

config = StrategyConfig(
    strategy_name="least-used",
    window_duration_seconds=7200  # 2 hours instead of default 1 hour
)
rotator = ProxyRotator(strategy=LeastUsedStrategy(), config=config)
```

### Hot-Swapping Strategies

```python
# Start with round-robin
rotator = ProxyRotator(strategy=RoundRobinStrategy())

# ... after some requests ...

# Switch to performance-based without restarting
rotator.set_strategy(PerformanceBasedStrategy())
# In-flight requests complete with old strategy
# New requests use new strategy immediately
```

## Custom Strategy Plugin

```python
from proxywhirl.strategies import RotationStrategy
from proxywhirl.models import Proxy, ProxyPool, ProxyMetadata

class MyCustomStrategy:
    """Custom strategy implementation."""
    
    @property
    def requires_metadata(self) -> Set[str]:
        return {"ema_response_time_ms"}  # Required metadata fields
    
    def validate_requirements(self, pool: ProxyPool, metadata: Dict[UUID, ProxyMetadata]) -> bool:
        return all(
            meta.ema_response_time_ms is not None
            for meta in metadata.values()
        )
    
    def select(self, pool: ProxyPool, metadata: Dict[UUID, ProxyMetadata], context: Optional[SelectionContext] = None) -> Proxy:
        healthy = pool.get_healthy_proxies()
        if not healthy:
            raise ProxyPoolEmptyError("No healthy proxies")
        
        # Your custom selection logic here
        return min(healthy, key=lambda p: metadata[p.id].ema_response_time_ms or float('inf'))
    
    def record_result(self, proxy: Proxy, metadata: ProxyMetadata, success: bool, response_time_ms: float) -> None:
        metadata.record_completion(success, response_time_ms)

# Register and use
rotator.register_strategy("my-custom", MyCustomStrategy)
rotator.set_strategy("my-custom")
```
```

---

## Phase 2: Foundation Implementation

**Goal**: Implement core metadata tracking and strategy infrastructure.

**Duration**: 3-4 days

### Task Breakdown

**Phase 2.1: Metadata Models** [Sequential]
1. Implement `ProxyMetadata` model with EMA and sliding window logic
2. Implement `ProxySession` model with expiration logic
3. Implement `GeoLocation` model with validation
4. Implement `StrategyConfig` model with constraints
5. Write unit tests for all models (test-first)
6. Validate thread-safety of metadata updates

**Phase 2.2: ProxyRotator Enhancements** [Sequential, depends on 2.1]
1. Add metadata storage (`Dict[UUID, ProxyMetadata]`) to `ProxyRotator`
2. Add session storage (`Dict[str, ProxySession]`) to `ProxyRotator`
3. Implement thread-safe metadata access with locks
4. Add metadata initialization on proxy addition
5. Add metadata cleanup on proxy removal
6. Implement session management methods (`create_session`, `get_session`, `cleanup_expired_sessions`)
7. Write unit tests for metadata lifecycle

**Phase 2.3: Strategy Protocol Update** [Sequential, depends on 2.2]
1. Update `RotationStrategy` protocol with new signature
2. Add `validate_requirements` method to protocol
3. Add `requires_metadata` property to protocol
4. Update existing strategies to conform to new protocol
5. Write property tests for protocol conformance

**Checkpoint**: All foundational infrastructure in place, existing tests pass

---

## Phase 3-8: User Story Implementation

Each phase implements one user story with test-first approach.

### Phase 3: US1 - Round-Robin Enhancement (P1)

**Goal**: Enhance existing round-robin with metadata tracking and window-based distribution.

**Tasks**:
1. Write integration tests for enhanced round-robin (test-first)
2. Update `RoundRobinStrategy` to use `ProxyMetadata`
3. Implement perfect distribution validation (±1 request variance)
4. Add wraparound behavior tests
5. Add health check skip tests
6. Validate SC-001: Perfect distribution achieved

### Phase 4: US2 - Random Selection Enhancement (P2)

**Goal**: Enhance random strategy with weighted selection based on success rates.

**Tasks**:
1. Write integration tests for enhanced random (test-first)
2. Update `RandomStrategy` to use `ProxyMetadata`
3. Implement weighted random selection (success rate weights)
4. Add uniform distribution validation (10% variance over 1000 requests)
5. Write property tests for distribution convergence
6. Validate SC-002: 10% variance achieved

### Phase 5: US3 - Least-Used Enhancement (P2)

**Goal**: Enhance least-used strategy with sliding window request counts.

**Tasks**:
1. Write integration tests for least-used (test-first)
2. Update `LeastUsedStrategy` to use sliding window counts
3. Implement tie-breaking (deterministic or random configurable)
4. Add window-based load balancing tests
5. Validate SC-003: <20% variance across proxies

### Phase 6: US4 - Performance-Based Strategy (P2)

**Goal**: Implement new performance-based strategy using EMA.

**Tasks**:
1. Write integration tests for performance-based (test-first)
2. Implement `PerformanceBasedStrategy` class
3. Implement EMA-weighted selection
4. Add fallback to round-robin when all proxies slow
5. Add performance degradation detection tests
6. Write property tests for EMA convergence
7. Validate SC-004: 15-25% latency reduction

### Phase 7: US5 - Session Persistence Strategy (P3)

**Goal**: Implement session-based sticky proxy selection.

**Tasks**:
1. Write integration tests for session persistence (test-first)
2. Implement `SessionStrategy` class
3. Implement session creation and lookup
4. Add session expiration handling
5. Add session proxy failure handling (fallback to new proxy)
6. Write tests for session lifecycle
7. Validate SC-005: 99.9% same-proxy for same session

### Phase 8: US6 - Geo-Targeted Strategy (P3)

**Goal**: Implement geographic region-based proxy selection.

**Tasks**:
1. Write integration tests for geo-targeting (test-first)
2. Implement `GeoTargetedStrategy` class
3. Implement country code filtering
4. Add fallback behavior (error or any region configurable)
5. Add secondary strategy application (round-robin among geo-matched)
6. Write tests for geo-filtering
7. Validate SC-006: 100% correct region selection

---

## Phase 9: Advanced Features

**Goal**: Implement strategy composition, hot-swapping, and plugin architecture.

**Duration**: 2-3 days

### Phase 9.1: Strategy Composition

**Tasks**:
1. Write integration tests for composed strategies (test-first)
2. Implement `CompositeStrategy` class (filter + select pattern)
3. Add geo-filtering + performance-based example
4. Add fallback chain support
5. Validate composition performance (<5ms still)

### Phase 9.2: Hot-Swapping

**Tasks**:
1. Write integration tests for hot-swapping (test-first)
2. Implement atomic strategy reference swap in `ProxyRotator`
3. Add in-flight request isolation (old strategy completes, new starts immediately)
4. Add hot-swap notification hooks (optional callbacks)
5. Validate SC-009: <100ms swap time, no dropped requests

### Phase 9.3: Plugin Architecture

**Tasks**:
1. Write integration tests for custom strategies (test-first)
2. Implement `register_strategy(name, strategy_class)` in `ProxyRotator`
3. Add protocol validation at registration time
4. Add plugin error isolation (errors don't crash rotator)
5. Write example custom strategy
6. Validate SC-010: <1s plugin loading time

---

## Phase 10: Performance & Concurrency

**Goal**: Validate performance targets and thread-safety.

**Duration**: 2 days

### Phase 10.1: Performance Benchmarks

**Tasks**:
1. Implement benchmark suite in `tests/benchmarks/test_strategy_performance.py`
2. Measure strategy selection overhead (target: <5ms)
3. Measure throughput (target: 10k concurrent requests)
4. Measure hot-swap latency (target: <100ms)
5. Measure plugin loading time (target: <1s)
6. Generate performance report

### Phase 10.2: Concurrency Testing

**Tasks**:
1. Implement stress tests with 10k concurrent requests
2. Test for deadlocks (pytest-timeout)
3. Test for race conditions (property-based with concurrent threads)
4. Measure lock contention overhead
5. Validate thread-safety with `ThreadSanitizer` (if available)

---

## Phase 11: Documentation & Examples

**Goal**: Complete user-facing documentation and examples.

**Duration**: 1 day

### Tasks:
1. Complete API documentation (docstrings for all new methods)
2. Add examples in `examples/strategy_examples.py`
3. Add custom plugin example in `examples/custom_strategy_plugin.py`
4. Update README.md with strategy feature overview
5. Generate API reference documentation (Sphinx or mkdocs)

---

## Phase 12: Integration & Validation

**Goal**: End-to-end validation against spec acceptance criteria.

**Duration**: 1 day

### Tasks:
1. Run full test suite (unit + integration + property + benchmarks)
2. Validate all success criteria (SC-001 through SC-010)
3. Validate all acceptance scenarios from spec.md
4. Run security audit (credential redaction, no sensitive data in logs)
5. Run `mypy --strict` validation
6. Generate coverage report (target: >85%)
7. Create validation report

---

## Risk Assessment & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| EMA alpha selection suboptimal | Medium | Medium | Extensive simulation with various alpha values; make configurable |
| Lock contention under high concurrency | Medium | High | Fine-grained per-proxy locks; benchmark early in Phase 10 |
| Sliding window memory growth | Low | High | Auto-pruning on every access; hard limit on window duration |
| Strategy composition complexity | Medium | Medium | Start with simple filter+select pattern; extensive property tests |
| Hot-swap race conditions | Medium | High | Atomic reference swap with RW lock; thorough concurrency testing |
| Plugin security vulnerabilities | Low | High | Protocol validation at registration; error isolation; no eval/exec |

## Success Metrics

- [ ] All 10 success criteria (SC-001 through SC-010) validated
- [ ] All 20+ acceptance scenarios passing
- [ ] Test coverage >85% (target: match existing 88%+)
- [ ] Performance benchmarks: <5ms selection, 10k req/s throughput
- [ ] Zero security vulnerabilities in audit
- [ ] `mypy --strict` passes
- [ ] Documentation complete with examples

## Timeline Estimate

- **Phase 0 (Research)**: 1-2 days
- **Phase 1 (Design)**: 2-3 days
- **Phase 2 (Foundation)**: 3-4 days
- **Phases 3-8 (User Stories)**: 6-8 days (1-1.5 days per story)
- **Phase 9 (Advanced Features)**: 2-3 days
- **Phase 10 (Performance)**: 2 days
- **Phase 11 (Documentation)**: 1 day
- **Phase 12 (Validation)**: 1 day

**Total: 18-24 days** (3-4 weeks with 1 engineer)

With 2 engineers working in parallel on independent user stories: **12-16 days** (2-3 weeks)

---

## Next Steps

1. **Review this plan** with team for feedback
2. **Run Phase 0 research** to validate technical approach
3. **Create tasks.md** via `/speckit.tasks` command (breaks down each phase into atomic tasks)
4. **Begin Phase 1** design work once research validates approach
5. **Iterate** on design based on Phase 0 findings

**Command to proceed**: `/speckit.tasks` (generates detailed task breakdown with checkpoints)
