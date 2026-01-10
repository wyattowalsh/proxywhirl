# ADR-003: Strategy Pattern for Proxy Rotation

## Status

Accepted

## Context

ProxyWhirl needs to support multiple proxy selection algorithms to accommodate different use cases:

- **Round-robin**: Simple, fair distribution for general scraping
- **Random**: Unpredictable pattern to avoid detection
- **Weighted**: Favor high-performance or premium proxies
- **Least-used**: Balance load across proxy pool
- **Performance-based**: Select fastest proxies adaptively
- **Session persistence**: Sticky sessions for stateful workflows
- **Geo-targeted**: Filter by geographic location
- **Composite**: Combine multiple strategies (e.g., geo + performance)

Requirements:
1. **Extensibility**: Easy to add custom strategies
2. **Configurability**: Runtime strategy selection
3. **Type Safety**: Compile-time validation of strategy interface
4. **Performance**: <5ms selection time (SC-007)
5. **Thread Safety**: Concurrent selection from multiple threads
6. **Testability**: Isolated testing of each strategy
7. **Plugin Architecture**: User-defined strategies without modifying core

Traditional approaches have limitations:
- If/else chains become unwieldy with many strategies
- Inheritance-based design couples strategies to base class
- Duck typing lacks compile-time validation

## Decision

We implemented the **Strategy Pattern** with a registry-based plugin architecture:

### Core Design

**`RotationStrategy` Protocol** (structural subtyping):
```python
@runtime_checkable
class RotationStrategy(Protocol):
    def select(self, pool: ProxyPool, context: Optional[SelectionContext]) -> Proxy:
        """Select a proxy from the pool."""
        ...

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        """Record request outcome for adaptive strategies."""
        ...
```

**Strategy Registry** (singleton):
```python
class StrategyRegistry:
    _strategies: dict[str, type] = {}

    def register_strategy(self, name: str, strategy_class: type) -> None:
        """Register custom strategy."""
        ...

    def get_strategy(self, name: str) -> type:
        """Retrieve strategy by name."""
        ...
```

**Selection Context** (request metadata):
```python
class SelectionContext(BaseModel):
    session_id: Optional[str]           # For session persistence
    target_country: Optional[str]        # For geo-targeting
    target_region: Optional[str]         # For geo-targeting
    failed_proxy_ids: list[str]         # For retry exclusion
```

### Built-In Strategies

**1. Round-Robin** (`RoundRobinStrategy`):
- Sequential selection with wraparound
- Thread-safe index tracking via `threading.Lock`
- O(1) selection time
- Fair distribution across proxies

**2. Random** (`RandomStrategy`):
- Random selection from healthy proxies
- Uses `random.choice()` (GIL-protected)
- O(1) selection time
- Unpredictable pattern

**3. Weighted** (`WeightedStrategy`):
- Weighted random selection by success rate or custom weights
- Cached weight calculation for performance
- O(n) first call, O(1) subsequent calls (cache hit)
- Normalizes weights to sum=1.0 invariant

**4. Least-Used** (`LeastUsedStrategy`):
- Select proxy with fewest active requests
- Tracks `requests_started` counter
- O(n) selection time (linear scan)
- Load balancing across proxies

**5. Performance-Based** (`PerformanceBasedStrategy`):
- Weighted selection by inverse EMA response time
- Exploration period for new proxies (default: 5 trials)
- O(n) selection time
- Adaptive to proxy performance

**6. Session Persistence** (`SessionPersistenceStrategy`):
- Sticky proxy-to-session mapping
- `SessionManager` with LRU eviction and TTL
- O(1) session lookup
- 99.9% same-proxy guarantee (SC-005)

**7. Geo-Targeted** (`GeoTargetedStrategy`):
- Filter by `country_code` or `region`
- Configurable fallback to any proxy
- O(n) filtering + O(1) or O(n) selection
- 100% correct region selection (SC-006)

**8. Composite** (`CompositeStrategy`):
- Apply filters then selector
- Example: Geo filter → Performance selector
- O(n * filters) + O(selector) selection time
- <5ms total target (SC-007)

### Registry Plugin Architecture

**Registration**:
```python
# User defines custom strategy
class MyCustomStrategy:
    def select(self, pool, context=None):
        return pool.get_all_proxies()[0]

    def record_result(self, proxy, success, response_time_ms):
        pass

# Register it
registry = StrategyRegistry()
registry.register_strategy("my-custom", MyCustomStrategy)
```

**Retrieval**:
```python
strategy_class = registry.get_strategy("my-custom")
strategy = strategy_class()
proxy = strategy.select(pool)
```

**Validation** (optional):
```python
registry.register_strategy("my-custom", MyCustomStrategy, validate=True)
# Raises TypeError if missing required methods
```

## Consequences

### Positive

1. **Extensibility**:
   - Add new strategies without modifying existing code
   - Plugin architecture via registry
   - Protocol-based validation ensures correctness

2. **Type Safety**:
   - `@runtime_checkable` Protocol enables `isinstance()` checks
   - Static type checkers validate implementations
   - Compile-time errors for missing methods

3. **Performance**:
   - Strategy overhead <1ms (validated by tests)
   - Caching in `WeightedStrategy` reduces recalculation
   - Lock-free strategies (Random, Weighted) scale better

4. **Configurability**:
   - Runtime strategy selection via string names
   - `StrategyConfig` for per-strategy customization
   - No code changes required for different deployments

5. **Thread Safety**:
   - Each strategy handles own concurrency
   - Round-robin uses `threading.Lock` for index
   - Random/Weighted use GIL-protected random module
   - Session uses `threading.RLock` in SessionManager

6. **Testability**:
   - Mock `ProxyPool` and `SelectionContext` for unit tests
   - Isolated strategy testing
   - Property-based testing with hypothesis

7. **Observability**:
   - `record_result()` enables adaptive strategies
   - Logging of strategy selection decisions
   - Metrics integration for strategy performance

### Negative

1. **Complexity**:
   - 8 built-in strategies to maintain
   - Registry singleton adds global state
   - Protocol validation requires runtime checks

2. **Performance Variability**:
   - O(n) strategies (Least-Used, Geo) scale poorly with large pools
   - Composite strategies multiply selection time
   - Mitigated by filtering before expensive operations

3. **Memory Overhead**:
   - `WeightedStrategy` caches weights (O(n) memory)
   - `SessionManager` stores session mappings (O(sessions))
   - Mitigated by LRU eviction and TTL

4. **Thread Contention**:
   - Round-robin lock serializes selections
   - Session manager lock serializes session operations
   - Mitigated by lock-free strategies (Random, Weighted)

5. **Strategy Explosion**:
   - Many combinations possible (geo + weighted + session)
   - Composite strategy helps but adds complexity
   - Users may be overwhelmed by choices

### Alternatives Considered

**Class Inheritance**:
```python
class BaseStrategy(ABC):
    @abstractmethod
    def select(self, pool): ...
```
- Tighter coupling to base class
- Harder to test in isolation
- Rejected: Protocol more flexible

**Function-Based Strategies**:
```python
def round_robin_strategy(pool): ...
```
- Simpler for stateless strategies
- No state management (e.g., round-robin index)
- No `record_result()` for adaptive strategies
- Rejected: Insufficient for complex strategies

**Enum-Based Selection**:
```python
class StrategyType(Enum):
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
```
- Simpler than registry
- Requires modifying enum for custom strategies
- No plugin architecture
- Rejected: Not extensible

**External DSL**:
```yaml
strategy:
  type: composite
  filters:
    - geo: {country: US}
  selector:
    type: performance
```
- Configuration-driven
- Adds parsing complexity
- Runtime errors instead of compile-time
- Rejected: YAGNI (not needed yet)

## Implementation Details

### File Structure
```
proxywhirl/
├── strategies.py         # All strategies + registry
├── models.py            # StrategyConfig, SelectionContext
└── rotator.py           # ProxyRotator integration
```

### Key Classes

**`StrategyRegistry`**:
- Singleton pattern with double-checked locking
- Thread-safe registration/retrieval
- Validation via Protocol checking
- <1s load time (SC-010)

**`SelectionContext`**:
```python
class SelectionContext(BaseModel):
    session_id: Optional[str] = None
    target_country: Optional[str] = None
    target_region: Optional[str] = None
    failed_proxy_ids: list[str] = Field(default_factory=list)
```

**`StrategyConfig`**:
```python
class StrategyConfig(BaseModel):
    weights: dict[str, float] = {}                    # For WeightedStrategy
    exploration_count: Optional[int] = None           # For PerformanceBasedStrategy
    session_stickiness_duration_seconds: Optional[int] = None  # For SessionPersistenceStrategy
    geo_fallback_enabled: Optional[bool] = None       # For GeoTargetedStrategy
    geo_secondary_strategy: Optional[str] = None      # For GeoTargetedStrategy
```

### Integration with ProxyRotator

```python
class ProxyRotator:
    def __init__(self, strategy: Union[str, RotationStrategy] = "round-robin"):
        if isinstance(strategy, str):
            registry = StrategyRegistry()
            strategy_class = registry.get_strategy(strategy)
            self.strategy = strategy_class()
        else:
            self.strategy = strategy

    async def get_proxy(self, context: Optional[SelectionContext] = None) -> Proxy:
        proxy = self.strategy.select(self.pool, context)
        # Use proxy...
        success = ...
        response_time_ms = ...
        self.strategy.record_result(proxy, success, response_time_ms)
        return proxy
```

### Thread Safety Patterns

**Round-Robin**:
```python
class RoundRobinStrategy:
    def __init__(self):
        self._current_index = 0
        self._lock = threading.Lock()

    def select(self, pool, context=None):
        with self._lock:
            index = self._current_index % len(pool)
            self._current_index = (self._current_index + 1) % len(pool)
        return pool[index]
```

**Session Manager**:
```python
class SessionManager:
    def __init__(self):
        self._sessions: dict[str, Session] = {}
        self._lock = threading.RLock()

    def get_session(self, session_id: str) -> Optional[Session]:
        with self._lock:
            return self._sessions.get(session_id)
```

**Weighted Strategy** (lock-free):
```python
class WeightedStrategy:
    def select(self, pool, context=None):
        # No lock needed - random.choices is GIL-protected
        weights = self._get_weights(pool)  # Cached
        return random.choices(pool, weights=weights, k=1)[0]
```

## References

- Implementation: `/Users/ww/dev/projects/proxywhirl/proxywhirl/strategies.py`
- Models: `/Users/ww/dev/projects/proxywhirl/proxywhirl/models.py`
- Tests: `/Users/ww/dev/projects/proxywhirl/tests/unit/test_strategies*.py`

## Notes

### Performance Benchmarks

From test suite:
- Round-Robin: <0.1ms per selection
- Random: <0.1ms per selection
- Weighted: <1ms per selection (cached), <5ms (cache miss)
- Least-Used: <1ms per selection (100 proxies)
- Performance-Based: <2ms per selection
- Session: <0.5ms per lookup
- Geo: <3ms per selection (1000 proxies)
- Composite: <5ms total (SC-007 compliant)

### Design Rationale

**Why Protocol over ABC?**
- Structural subtyping (duck typing with validation)
- Third-party classes can be strategies without inheritance
- Easier mocking in tests

**Why Registry Pattern?**
- Decouples strategy names from implementations
- Enables plugin architecture
- Runtime strategy selection from config

**Why SelectionContext?**
- Centralized request metadata
- Avoids strategy-specific parameters
- Extensible without breaking interface

**Why record_result()?**
- Enables adaptive strategies (performance, weighted)
- Separates selection from outcome tracking
- Allows strategies to learn from feedback

### Future Enhancements

1. **Strategy Composition DSL**:
   ```python
   strategy = (GeoTargeted(country="US")
               >> PerformanceBased()
               >> SessionPersistence())
   ```

2. **Strategy Metrics**:
   - Track selection time per strategy
   - Expose success rate by strategy
   - Alert on strategy degradation

3. **ML-Based Selection**:
   - Train model on historical proxy performance
   - Predict optimal proxy for request
   - Integrate with existing strategies

4. **Strategy A/B Testing**:
   - Split traffic between strategies
   - Compare performance metrics
   - Auto-promote winning strategy
