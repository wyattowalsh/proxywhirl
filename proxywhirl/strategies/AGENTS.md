# Strategies Subsystem

> Extends: [../../AGENTS.md](../../AGENTS.md)

## Modules

| File | Key Classes |
|------|-------------|
| `core.py` | `RotationStrategy` (Protocol), `StrategyRegistry`, all strategy implementations |

## Available Strategies (9)

| Strategy | Class | Use Case |
|----------|-------|----------|
| `round_robin` | `RoundRobinStrategy` | Equal distribution, default |
| `random` | `RandomStrategy` | Simple random selection |
| `weighted` | `WeightedStrategy` | Prioritize by success rate/custom weights |
| `least_used` | `LeastUsedStrategy` | Balance load (min-heap) |
| `performance` | `PerformanceBasedStrategy` | Optimize for EMA response time |
| `session` | `SessionPersistenceStrategy` | Sticky sessions per domain |
| `geo` | `GeoTargetedStrategy` | Location-based selection |
| `cost` | `CostAwareStrategy` | Cost-aware selection |
| `composite` | `CompositeStrategy` | Combine multiple strategies |

## Usage

```python
from proxywhirl.strategies import StrategyRegistry, RoundRobinStrategy

# Via registry
strategy = StrategyRegistry.get("round_robin")

# Direct instantiation
strategy = RoundRobinStrategy()
proxy = strategy.select(pool)
```

## Boundaries

**Always:**
- Implement `RotationStrategy` protocol for new strategies
- Handle empty pool gracefully (raise `ProxyPoolEmptyError`)
- Register new strategies in `StrategyRegistry`
- Use thread-safe operations for stateful strategies

**Ask First:**
- New strategy implementations
- Default strategy changes
- Strategy registry modifications

**Never:**
- Modify strategy state without locks
- Return None from `select()` (raise instead)
- Access pool internals directly
