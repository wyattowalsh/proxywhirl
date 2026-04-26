---
title: Rotation Strategies
---

# Rotation Strategies

ProxyWhirl ships 9 rotation strategies. This page explains *why* the strategy system is designed the way it is -- the Protocol pattern, the registry, and how strategies compose.

For strategy configuration and code examples, see {doc}`/guides/advanced-strategies` and {doc}`/reference/python-api`.

## Why a Protocol, Not an Abstract Base Class?

Strategies implement the `RotationStrategy` **Protocol** (structural subtyping) rather than inheriting from an ABC:

```python
@runtime_checkable
class RotationStrategy(Protocol):
    def select(self, pool: ProxyPool, context: SelectionContext | None) -> Proxy: ...
    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None: ...
```

This means any class with matching `select()` and `record_result()` methods is a valid strategy -- no inheritance required. Benefits:

- **Third-party strategies** work without importing ProxyWhirl base classes
- **Easier mocking** in tests (any object with the right shape works)
- **Static type checking** validates implementations at compile time via `@runtime_checkable`

The alternative -- an abstract base class -- was rejected because it couples strategies to a base class and makes third-party plugins harder.

## The Registry Pattern

Strategies are registered by name in a `StrategyRegistry` singleton:

```python
registry = StrategyRegistry()
registry.register_strategy("my-custom", MyCustomStrategy)

# Later, retrieve by name (e.g., from TOML config)
strategy_class = registry.get_strategy("my-custom")
```

This decouples strategy *names* (used in config files and CLI) from *implementations*. You can swap strategies at runtime without changing code, and user-defined strategies sit alongside built-ins.

## The 9 Built-In Strategies

Each strategy targets a different use case. They fall into three categories:

### Simple Selection (Stateless)

| Strategy | Algorithm | Selection Time | Use Case |
|----------|-----------|---------------|----------|
| **Round-Robin** | Sequential index with wraparound | O(1) | Even distribution, general scraping |
| **Random** | `random.choice()` from healthy pool | O(1) | Unpredictable patterns, anti-detection |

These are stateless (aside from round-robin's index counter). They don't learn from results.

### Adaptive Selection (Stateful)

| Strategy | Algorithm | Selection Time | Use Case |
|----------|-----------|---------------|----------|
| **Weighted** | Weighted random by success rate | O(1) cached | Favor reliable proxies |
| **Least-Used** | Min active requests (linear scan) | O(n) | Load balancing |
| **Performance-Based** | Inverse EMA response time | O(n) | Lowest latency |
| **Cost-Aware** | Budget-weighted selection (free proxies boosted 10x) | O(n) | Budget optimization |

These use `record_result()` feedback to adapt over time. Performance-based uses an Exponential Moving Average (EMA) to track latency, with a cold-start exploration period for new proxies.

### Context-Aware Selection

| Strategy | Algorithm | Selection Time | Use Case |
|----------|-----------|---------------|----------|
| **Session Persistence** | Sticky proxy-to-session mapping (LRU + TTL) | O(1) lookup | Stateful workflows |
| **Geo-Targeted** | Filter by `country_code` / `region` | O(n) filter | Region-aware routing |

These use `SelectionContext` metadata (session IDs, target countries) to make decisions.

### Composition

The **Composite** strategy chains multiple strategies into a pipeline:

```
[Geo filter: US only] → [Performance selector: fastest] → selected proxy
```

This is the key design insight: rather than creating an N x M explosion of combined strategies (geo + weighted, geo + performance, session + weighted...), the composite pattern lets you assemble any combination from simple building blocks.

Composite pipelines target <5 us total selection overhead (SC-007).

## Why `record_result()`?

Every strategy has a `record_result(proxy, success, response_time_ms)` method, even simple ones that ignore it. This exists because:

1. **Adaptive strategies need feedback** -- performance-based and weighted strategies learn from outcomes
2. **Uniform interface** -- callers don't need to know whether a strategy is adaptive
3. **Future-proofing** -- a "simple" strategy can become adaptive without interface changes

## Thread Safety

Each strategy handles its own concurrency:

- **Round-Robin**: `threading.Lock` for index counter
- **Session Persistence**: `threading.RLock` in `SessionManager`
- **Random/Weighted**: Lock-free (Python GIL protects `random.choices`)
- **Performance-Based**: Lock on EMA score updates

This per-strategy approach avoids a global lock that would serialize all selections.

## Further Reading

- {doc}`/guides/advanced-strategies` -- configuration examples for each strategy
- {doc}`/reference/python-api` -- full API reference for strategy classes
- [ADR-003: Strategy Pattern](https://github.com/wyattowalsh/proxywhirl/blob/main/docs/adr/003-strategy-pattern.md) -- original decision record
