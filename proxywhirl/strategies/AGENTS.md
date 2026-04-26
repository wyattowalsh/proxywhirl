# Strategies Subsystem

> Extends: [../../AGENTS.md](../../AGENTS.md)

## Module

`core.py` — `RotationStrategy` (Protocol), `StrategyRegistry`, all implementations

## Strategies (9)

| Name | Class | Use Case |
|------|-------|----------|
| `round_robin` | `RoundRobinStrategy` | Equal distribution (default) |
| `random` | `RandomStrategy` | Random selection |
| `weighted` | `WeightedStrategy` | By success rate/weights |
| `least_used` | `LeastUsedStrategy` | Load balancing (min-heap) |
| `performance` | `PerformanceBasedStrategy` | EMA response time |
| `session` | `SessionPersistenceStrategy` | Sticky sessions |
| `geo` | `GeoTargetedStrategy` | Location-based |
| `cost` | `CostAwareStrategy` | Cost optimization |
| `composite` | `CompositeStrategy` | Combine strategies |

## Usage

```python
from proxywhirl.strategies import StrategyRegistry, RoundRobinStrategy
strategy = StrategyRegistry.get("round_robin")  # or RoundRobinStrategy()
proxy = strategy.select(pool)
```

## Boundaries

**Always:** Implement `RotationStrategy` protocol, raise `ProxyPoolEmptyError` on empty, thread-safe state

**Never:** Return None from `select()`, modify state without locks
