---
title: Rotation Strategies
---

ProxyWhirl ships **9 rotation strategies** covering everything from simple round-robin to composite filter-then-select pipelines. This guide shows how to configure each one, when to use it, and how to build custom strategies.

# Rotation Strategies

## Bootstrap a rotator

```python
from proxywhirl import ProxyRotator, Proxy
from pydantic import SecretStr

proxies = [
    Proxy(url="http://proxy1.example.com:8080"),
    Proxy(url="http://proxy2.example.com:8080"),
    Proxy(
        url="http://proxy3.example.com:8080",
        username="demo",
        password=SecretStr("pass"),
    ),
]

rotator = ProxyRotator(proxies=proxies)  # round-robin by default
response = rotator.get("https://httpbin.org/ip")
print(response.json())
```

```{tip}
Need a larger pool? Use :class:`proxywhirl.ProxyFetcher` with :data:`proxywhirl.RECOMMENDED_SOURCES` to hydrate your rotator, then call :func:`proxywhirl.deduplicate_proxies` before adding user-supplied proxies.
```

---

## Decision Matrix

Use this table to pick the right strategy for your workload:

```{list-table}
:header-rows: 1
:widths: 16 20 18 18 28

* - Strategy
  - Ideal For
  - Latency
  - Thread-Safe
  - Highlights
* - ``round-robin``
  - Fair distribution, predictable workloads
  - ~3 us
  - Lock-based
  - +/-1 request variance; deterministic ordering
* - ``random``
  - Load testing, rate-limit avoidance
  - ~7 us
  - GIL-safe
  - Natural jitter masks access patterns
* - ``weighted``
  - Premium proxies, health-based routing
  - ~9 us
  - Lock-based
  - Custom weights or auto-derived from success rate
* - ``least-used``
  - Long-running jobs, even balancing
  - ~3 us
  - Lock-based
  - Min-heap tracks request totals
* - ``performance-based``
  - Speed-critical scraping
  - ~12 us
  - Lock-based
  - EMA smoothing of response times (configurable alpha)
* - ``session-persistence``
  - Stateful APIs, cookie-dependent flows
  - ~5 us
  - Lock-based
  - Maps session keys to proxy IDs with TTL
* - ``geo-targeted``
  - Geo-specific content, localization QA
  - ~8 us
  - Lock-based
  - Filters by country code from proxy metadata
* - ``cost-aware``
  - Budget-constrained environments
  - ~10 us
  - Lock-based
  - Considers per-request cost metadata
* - ``composite``
  - Complex multi-criteria selection
  - varies
  - Lock-based
  - Chains filter + select strategies in a pipeline
```

```{note}
All strategies implement the :class:`proxywhirl.strategies.RotationStrategy` protocol, which requires two methods: ``select(pool, context)`` and ``record_result(proxy, success, response_time_ms)``.
```

---

## Strategy Recipes

### Core Strategies

::::{tab-set}

:::{tab-item} Round-robin
```python
rotator = ProxyRotator(proxies=proxies, strategy="round-robin")
rotator.get("https://example.com")
```
Cycles A -> B -> C -> A sequentially. Best for predictable, even distribution.
:::

:::{tab-item} Random
```python
rotator = ProxyRotator(proxies=proxies, strategy="random")
rotator.get("https://api.example.com/data")
```
Picks a random healthy proxy each time. Use when you want to avoid detectable patterns.
:::

:::{tab-item} Weighted
```python
from proxywhirl.strategies import WeightedStrategy, StrategyConfig

weights = StrategyConfig(
    weights={
        "http://proxy1.example.com:8080": 0.55,
        "http://proxy2.example.com:8080": 0.30,
        "http://proxy3.example.com:8080": 0.15,
    }
)
rotator = ProxyRotator(
    proxies=proxies,
    strategy=WeightedStrategy(config=weights),
)
```
When no custom weights are provided, weights are auto-derived from each proxy's ``success_rate``. A minimum weight of ``0.1`` ensures every proxy has a selection chance.
:::

:::{tab-item} Least-used
```python
rotator = ProxyRotator(proxies=proxies, strategy="least-used")
rotator.get("https://httpbin.org/ip")
```
Selects the proxy with the fewest total requests. Ideal for long-running crawls that need even utilization.
:::

::::

### Advanced Strategies

::::{tab-set}

:::{tab-item} Performance-based
```python
from proxywhirl.strategies import PerformanceBasedStrategy, StrategyConfig

config = StrategyConfig(ema_alpha=0.3)  # Higher alpha = more weight to recent times
strategy = PerformanceBasedStrategy(config=config)

rotator = ProxyRotator(proxies=proxies, strategy=strategy)
```
Ranks proxies by exponential moving average (EMA) of response times. The ``ema_alpha`` parameter controls how quickly the strategy adapts: higher values respond faster to recent performance changes.
:::

:::{tab-item} Session persistence
```python
from proxywhirl.strategies import SessionPersistenceStrategy
from proxywhirl.models import SelectionContext

strategy = SessionPersistenceStrategy()
rotator = ProxyRotator(proxies=proxies, strategy=strategy)

# Bind a session key to a consistent proxy
context = SelectionContext(session_id="user-12345")
response = rotator.get("https://api.example.com/profile", context=context)
```
Maps session keys to proxy IDs so that repeated requests with the same ``session_id`` always route through the same proxy -- essential for cookie-dependent or stateful APIs.
:::

:::{tab-item} Geo-targeted
```python
from proxywhirl.strategies import GeoTargetedStrategy
from proxywhirl.models import SelectionContext

strategy = GeoTargetedStrategy()
rotator = ProxyRotator(proxies=proxies, strategy=strategy)

# Route through US-based proxies only
context = SelectionContext(target_countries=["US"])
response = rotator.get("https://api.example.com/local", context=context)
```
Filters the pool by country code from proxy metadata. Requires proxies enriched with geo data (see ``proxywhirl setup-geoip``).
:::

:::{tab-item} Composite
```python
from proxywhirl.strategies import CompositeStrategy, GeoTargetedStrategy, PerformanceBasedStrategy

# First filter by geography, then pick the fastest
strategy = CompositeStrategy(
    strategies=[GeoTargetedStrategy(), PerformanceBasedStrategy()],
)
rotator = ProxyRotator(proxies=proxies, strategy=strategy)
```
Chains multiple strategies into a pipeline: earlier strategies filter the pool and later strategies make the final selection.
:::

::::

---

## Observe the Pool

```python
stats = rotator.get_pool_stats()
print(
    f"Total: {stats['total_proxies']} | "
    f"Healthy: {stats['healthy_proxies']} | "
    f"Average success: {stats['average_success_rate']:.2%}"
)
```

Use :func:`ProxyRotator.clear_unhealthy_proxies` to evict failing endpoints during long-running crawls.

You can also monitor from the command line:

```bash
# One-shot health check
uv run proxywhirl health

# Continuous monitoring every 60 seconds
uv run proxywhirl health --continuous --interval 60

# Retry and circuit breaker statistics
uv run proxywhirl stats --retry --circuit-breaker
```

See [CLI Reference](../guides/cli-reference.md) for the full CLI reference.

---

## Building a Custom Strategy

Any class implementing the :class:`~proxywhirl.strategies.RotationStrategy` protocol can be used as a strategy. The protocol requires two methods:

```python
from proxywhirl.models import Proxy, ProxyPool, SelectionContext

class PriorityStrategy:
    """Always selects the first healthy proxy (simple priority queue)."""

    def select(self, pool: ProxyPool, context: SelectionContext | None = None) -> Proxy:
        healthy = pool.get_healthy_proxies()
        if not healthy:
            from proxywhirl.exceptions import ProxyPoolEmptyError
            raise ProxyPoolEmptyError("No healthy proxies available")
        return healthy[0]

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        proxy.complete_request(success=success, response_time_ms=response_time_ms)
```

Register it globally so other components can look it up by name:

```python
from proxywhirl.strategies import StrategyRegistry

registry = StrategyRegistry()
registry.register_strategy("priority", PriorityStrategy)

# Retrieve later
strategy_cls = registry.get_strategy("priority")
rotator = ProxyRotator(proxies=proxies, strategy=strategy_cls())
```

```{warning}
Custom strategies used in multi-threaded code must be thread-safe. Protect shared mutable state with ``threading.Lock`` or use :class:`proxywhirl.strategies.StrategyState` for per-proxy metrics tracking.
```

---

## Further Reading

- [Advanced Strategies](../guides/advanced-strategies.md) -- deep dive into composite pipelines and EMA tuning
- [Retry & Failover](../guides/retry-failover.md) -- circuit breakers and retry policies that work alongside strategies
- [Async Client](../guides/async-client.md) -- async patterns with strategy selection
- [Python API](../reference/python-api.md) -- complete API reference for all strategy classes
