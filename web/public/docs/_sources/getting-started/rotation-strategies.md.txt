---
title: Rotation Strategies
---

ProxyWhirl ships **9 rotation strategies** covering everything from simple round-robin to composite filter-then-select pipelines. This guide shows how to configure each one, when to use it, and how to build custom strategies.

# Rotation Strategies

## Bootstrap a Rotator

```python
from proxywhirl import ProxyRotator, Proxy
from pydantic import SecretStr

proxies = [
    Proxy(url="http://proxy1.example.com:8080"),
    Proxy(url="http://proxy2.example.com:8080"),
    Proxy(
        url="http://proxy3.example.com:8080",
        username=SecretStr("demo"),
        password=SecretStr("pass"),
    ),
]

rotator = ProxyRotator(proxies=proxies)  # round-robin by default
response = rotator.get("https://httpbin.org/ip")
print(response.json())
```

```{tip}
Need a larger pool? Use {class}`proxywhirl.ProxyFetcher` with {data}`proxywhirl.RECOMMENDED_SOURCES` to hydrate your rotator, then call {func}`proxywhirl.deduplicate_proxies` before adding user-supplied proxies.
```

---

## Decision Matrix

Use this table to pick the right strategy for your workload:

```{list-table}
:header-rows: 1
:widths: 16 20 14 14 36

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
  - GIL-safe
  - EMA smoothing of response times (configurable alpha)
* - ``session-persistence``
  - Stateful APIs, cookie-dependent flows
  - ~5 us
  - Lock-based
  - Maps session keys to proxy IDs with TTL
* - ``geo-targeted``
  - Geo-specific content, localization QA
  - ~8 us
  - Stateless
  - Filters by country code from proxy metadata
* - ``cost-aware``
  - Budget-constrained environments
  - ~10 us
  - GIL-safe
  - Favors free proxies with configurable cost ceiling
* - ``composite``
  - Complex multi-criteria selection
  - varies
  - Inherited
  - Chains filter + select strategies in a pipeline
```

```{note}
All strategies implement the {class}`~proxywhirl.RotationStrategy` protocol, which requires two methods: ``select(pool, context)`` and ``record_result(proxy, success, response_time_ms)``.
```

---

## Quick-Pick Guide

Not sure which strategy to use? Follow this decision tree:

```{list-table}
:header-rows: 1
:widths: 50 25 25

* - Question
  - Yes
  - No
* - Need sticky sessions for stateful APIs?
  - **session-persistence**
  - Continue
* - Need proxies from a specific country?
  - **geo-targeted**
  - Continue
* - Need to minimize proxy costs?
  - **cost-aware**
  - Continue
* - Is latency more important than fairness?
  - **performance-based**
  - Continue
* - Want to avoid detectable rotation patterns?
  - **random**
  - Continue
* - Running a long crawl needing even distribution?
  - **least-used**
  - Continue
* - Have premium proxies that deserve more traffic?
  - **weighted**
  - Continue
* - Need multiple criteria (e.g., geo + speed)?
  - **composite**
  - **round-robin** (default)
```

---

## Strategy Reference

### 1. Round-Robin

**Class:** {class}`~proxywhirl.RoundRobinStrategy` | **Name:** ``"round-robin"``

Cycles through healthy proxies sequentially: A -> B -> C -> A. The default strategy.

**Constructor:** `RoundRobinStrategy()` -- no parameters.

**When to use:** Predictable workloads where even distribution matters more than performance optimization.

```python
from proxywhirl import ProxyRotator, Proxy

proxies = [
    Proxy(url="http://proxy1.example.com:8080"),
    Proxy(url="http://proxy2.example.com:8080"),
    Proxy(url="http://proxy3.example.com:8080"),
]

# By name (simplest)
rotator = ProxyRotator(proxies=proxies, strategy="round-robin")
rotator.get("https://example.com")

# Or by instance (equivalent)
from proxywhirl import RoundRobinStrategy
rotator = ProxyRotator(proxies=proxies, strategy=RoundRobinStrategy())
```

---

### 2. Random

**Class:** {class}`~proxywhirl.RandomStrategy` | **Name:** ``"random"``

Picks a random healthy proxy for each request. No state to track.

**Constructor:** `RandomStrategy()` -- no parameters.

**When to use:** Rate-limit avoidance, load testing, or when you want unpredictable access patterns.

```python
rotator = ProxyRotator(proxies=proxies, strategy="random")
rotator.get("https://api.example.com/data")
```

---

### 3. Weighted

**Class:** {class}`~proxywhirl.WeightedStrategy` | **Name:** ``"weighted"``

Selects proxies using weighted random sampling. Weights can be set explicitly or are auto-derived from each proxy's success rate. Every proxy gets a minimum weight of `0.1` to prevent starvation.

**Constructor:** `WeightedStrategy()` -- no parameters. Configure via {class}`~proxywhirl.StrategyConfig`.

**When to use:** When you have premium/reliable proxies that should receive more traffic, or want health-based load balancing.

::::{tab-set}

:::{tab-item} Auto weights (success rate)
```python
# Weights are automatically derived from proxy success rates
rotator = ProxyRotator(proxies=proxies, strategy="weighted")
```
:::

:::{tab-item} Custom weights
```python
from proxywhirl import WeightedStrategy, StrategyConfig

config = StrategyConfig(
    weights={
        "http://proxy1.example.com:8080": 0.55,
        "http://proxy2.example.com:8080": 0.30,
        "http://proxy3.example.com:8080": 0.15,
    }
)
strategy = WeightedStrategy()
strategy.configure(config)

rotator = ProxyRotator(proxies=proxies, strategy=strategy)
```
:::

::::

---

### 4. Least-Used

**Class:** {class}`~proxywhirl.LeastUsedStrategy` | **Name:** ``"least-used"``

Selects the proxy with the fewest total requests using a min-heap for O(log n) selection. The heap is lazily rebuilt when the pool changes.

**Constructor:** `LeastUsedStrategy()` -- no parameters.

**When to use:** Long-running crawls that need even utilization across all proxies.

```python
rotator = ProxyRotator(proxies=proxies, strategy="least-used")
rotator.get("https://httpbin.org/ip")
```

---

### 5. Performance-Based

**Class:** {class}`~proxywhirl.PerformanceBasedStrategy` | **Name:** ``"performance-based"``

Ranks proxies by inverse EMA (Exponential Moving Average) of response times -- faster proxies get higher selection probability. New proxies without enough data receive "exploration trials" before performance scoring kicks in.

**Constructor parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `exploration_count` | `int` | `5` | Minimum trials for new proxies before performance-based selection applies. Set to `0` to disable exploration. |

**When to use:** Speed-critical scraping or API calls where latency matters.

```python
from proxywhirl import ProxyRotator, PerformanceBasedStrategy, StrategyConfig

# Default: 5 exploration trials per new proxy
strategy = PerformanceBasedStrategy()

# Or tune exploration and EMA alpha
strategy = PerformanceBasedStrategy(exploration_count=3)
config = StrategyConfig(ema_alpha=0.3)  # Higher alpha = react faster to recent times
strategy.configure(config)

rotator = ProxyRotator(proxies=proxies, strategy=strategy)
```

```{tip}
The ``ema_alpha`` parameter controls how quickly the strategy adapts to performance changes. Values closer to `1.0` weight recent observations heavily (reacts fast, noisy). Values closer to `0.0` smooth over longer history (reacts slowly, stable). Default is `0.2`.
```

---

### 6. Session Persistence

**Class:** {class}`~proxywhirl.SessionPersistenceStrategy` | **Name:** ``"session-persistence"``

Maps session IDs to specific proxies so that repeated requests with the same `session_id` always route through the same proxy. If the assigned proxy becomes unhealthy, the session automatically fails over to a new proxy.

**Constructor parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_sessions` | `int` | `10000` | Maximum concurrent sessions before LRU eviction |
| `auto_cleanup_threshold` | `int` | `100` | Operations between automatic expired-session cleanup |

**When to use:** Stateful APIs, cookie-dependent flows, or any workflow where a user/session must consistently use the same proxy.

```python
from proxywhirl import ProxyRotator, SessionPersistenceStrategy, SelectionContext

strategy = SessionPersistenceStrategy(max_sessions=5000)
rotator = ProxyRotator(proxies=proxies, strategy=strategy)

# Select a proxy bound to a session key
context = SelectionContext(session_id="user-12345")
proxy = strategy.select(rotator.pool, context=context)
print(f"Session bound to proxy: {proxy.url}")

# Make requests -- the rotator uses the strategy internally
response = rotator.get("https://api.example.com/profile")

# Later selections with the same session_id return the same proxy
proxy_again = strategy.select(rotator.pool, context=context)
assert proxy.id == proxy_again.id  # Same proxy for same session
```

```{note}
Sessions expire after 1 hour by default. Configure via {class}`~proxywhirl.StrategyConfig` with ``session_stickiness_duration_seconds``.
```

---

### 7. Geo-Targeted

**Class:** {class}`~proxywhirl.GeoTargetedStrategy` | **Name:** ``"geo-targeted"``

Filters the proxy pool by geographic location (country or region) specified in the `SelectionContext`. Falls back to any healthy proxy when no match is found (configurable).

**Constructor:** `GeoTargetedStrategy()` -- no parameters. Configure via {class}`~proxywhirl.StrategyConfig`.

**When to use:** Geo-specific content scraping, localization QA, region-locked API access.

```python
from proxywhirl import ProxyRotator, GeoTargetedStrategy, SelectionContext, Proxy

# Proxies with geo metadata
proxies = [
    Proxy(url="http://us-proxy.example.com:8080", country_code="US"),
    Proxy(url="http://gb-proxy.example.com:8080", country_code="GB"),
    Proxy(url="http://de-proxy.example.com:8080", country_code="DE"),
]

strategy = GeoTargetedStrategy()
rotator = ProxyRotator(proxies=proxies, strategy=strategy)

# Select a US-based proxy using the strategy directly
context = SelectionContext(target_country="US")
proxy = strategy.select(rotator.pool, context=context)
print(f"Selected US proxy: {proxy.url} ({proxy.country_code})")

# Make requests -- the rotator handles proxy selection internally
response = rotator.get("https://api.example.com/local")

# Or target by region
context = SelectionContext(target_region="Europe")
proxy = strategy.select(rotator.pool, context=context)
print(f"Selected European proxy: {proxy.url}")
```

```{tip}
Country codes use ISO 3166-1 alpha-2 format (e.g., ``"US"``, ``"GB"``, ``"DE"``). Enrich proxies with geo data using ``proxywhirl setup-geoip`` or set ``country_code`` directly on the {class}`~proxywhirl.Proxy` model.
```

**Configuration options** via {class}`~proxywhirl.StrategyConfig`:

| Config Field | Default | Description |
|--------------|---------|-------------|
| `geo_fallback_enabled` | `True` | Fall back to any proxy when no geo match found |
| `geo_secondary_strategy` | `"round_robin"` | Strategy for selecting from geo-filtered proxies (`"round_robin"`, `"random"`, `"least_used"`) |

---

### 8. Cost-Aware

**Class:** {class}`~proxywhirl.CostAwareStrategy` | **Name:** ``"cost-aware"``

Prioritizes free proxies over paid ones using inverse-cost weighted random selection. Free proxies receive a configurable boost multiplier (default 10x).

**Constructor parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_cost_per_request` | `float \| None` | `None` | Maximum acceptable cost per request. Proxies exceeding this cost are filtered out. `None` means no limit. |

**When to use:** Budget-constrained environments where you mix free and paid proxies.

```python
from proxywhirl import ProxyRotator, CostAwareStrategy, StrategyConfig, Proxy

proxies = [
    Proxy(url="http://free-proxy.example.com:8080", cost_per_request=0.0),
    Proxy(url="http://cheap-proxy.example.com:8080", cost_per_request=0.01),
    Proxy(url="http://premium-proxy.example.com:8080", cost_per_request=0.10),
]

# Basic: favor free proxies
strategy = CostAwareStrategy()
rotator = ProxyRotator(proxies=proxies, strategy=strategy)

# With cost ceiling: exclude expensive proxies
strategy = CostAwareStrategy(max_cost_per_request=0.05)
rotator = ProxyRotator(proxies=proxies, strategy=strategy)
```

**Configuration options** via {class}`~proxywhirl.StrategyConfig` metadata:

| Metadata Key | Default | Description |
|--------------|---------|-------------|
| `max_cost_per_request` | `None` | Maximum cost threshold (overrides constructor) |
| `free_proxy_boost` | `10.0` | Weight multiplier for free proxies |

```python
config = StrategyConfig(metadata={
    "max_cost_per_request": 0.05,
    "free_proxy_boost": 20.0,
})
strategy = CostAwareStrategy()
strategy.configure(config)
```

---

### 9. Composite

**Class:** {class}`~proxywhirl.CompositeStrategy` | **Name:** ``"composite"``

Chains multiple strategies into a pipeline: **filter** strategies narrow the pool, then a **selector** strategy makes the final pick.

**Constructor parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `filters` | `list[RotationStrategy] \| None` | `[]` | Strategies that filter the proxy pool sequentially |
| `selector` | `RotationStrategy \| None` | `RoundRobinStrategy()` | Strategy that selects from the filtered pool |

**When to use:** Complex selection criteria that require multiple stages (e.g., "from US proxies, pick the fastest").

```python
from proxywhirl import (
    ProxyRotator,
    CompositeStrategy,
    GeoTargetedStrategy,
    PerformanceBasedStrategy,
    SelectionContext,
)

# Filter by geography, then select by performance
strategy = CompositeStrategy(
    filters=[GeoTargetedStrategy()],
    selector=PerformanceBasedStrategy(),
)
rotator = ProxyRotator(proxies=proxies, strategy=strategy)

# Select a proxy: geo-filter to US, then pick the fastest
context = SelectionContext(target_country="US")
proxy = strategy.select(rotator.pool, context=context)
print(f"Selected fastest US proxy: {proxy.url}")

# Make the request
response = rotator.get("https://api.example.com/data")
```

You can also build composites from config dicts:

```python
strategy = CompositeStrategy.from_config({
    "filters": ["geo-targeted"],
    "selector": "performance-based",
})
```

---

## Comparison At a Glance

```{list-table}
:header-rows: 1
:widths: 18 14 14 14 14 26

* - Strategy
  - State
  - Context Needed
  - Metadata Needed
  - Complexity
  - Best Scenario
* - Round-Robin
  - Index counter
  - No
  - None
  - O(1)
  - Default, even distribution
* - Random
  - None
  - No
  - None
  - O(1)
  - Anti-pattern masking
* - Weighted
  - Weight cache
  - No
  - Weights (optional)
  - O(n)
  - Premium proxy prioritization
* - Least-Used
  - Min-heap
  - No
  - None
  - O(log n)
  - Long crawls
* - Performance
  - EMA scores
  - No
  - None (auto-built)
  - O(n)
  - Latency-sensitive
* - Session
  - Session map
  - ``session_id``
  - None
  - O(1) lookup
  - Stateful APIs
* - Geo-Targeted
  - None
  - ``target_country``
  - ``country_code``
  - O(n) filter
  - Region-locked content
* - Cost-Aware
  - None
  - No
  - ``cost_per_request``
  - O(n)
  - Budget optimization
* - Composite
  - Inherited
  - Varies
  - Varies
  - Sum of parts
  - Multi-criteria
```

---

## Hot-Swapping Strategies

Switch strategies at runtime without restarting:

```python
rotator = ProxyRotator(proxies=proxies, strategy="round-robin")

# ... after observing proxy performance ...

# Hot-swap to performance-based
rotator.set_strategy("performance-based")

# Or swap to a custom-configured strategy
from proxywhirl import WeightedStrategy, StrategyConfig

strategy = WeightedStrategy()
strategy.configure(StrategyConfig(weights={
    "http://proxy1.example.com:8080": 0.7,
    "http://proxy2.example.com:8080": 0.3,
}))
rotator.set_strategy(strategy)
```

Hot-swap is atomic and completes in <100ms. In-flight requests finish with their original strategy; new requests immediately use the new one. Supported strategy names for `set_strategy()`: `"round-robin"`, `"random"`, `"weighted"`, `"least-used"`, `"performance-based"`, `"session"`, `"geo-targeted"`.

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

Use `rotator.clear_unhealthy_proxies()` to evict failing endpoints during long-running crawls.

You can also monitor from the command line:

```bash
# One-shot health check
uv run proxywhirl health

# Continuous monitoring every 60 seconds
uv run proxywhirl health --continuous --interval 60

# Retry and circuit breaker statistics
uv run proxywhirl stats --retry --circuit-breaker
```

See {doc}`/guides/cli-reference` for the full CLI reference.

---

## Building a Custom Strategy

Any class implementing the {class}`~proxywhirl.RotationStrategy` protocol can be used as a strategy. The protocol requires two methods:

```python
from proxywhirl import Proxy, ProxyPool, SelectionContext
from proxywhirl.exceptions import ProxyPoolEmptyError

class PriorityStrategy:
    """Always selects the first healthy proxy (simple priority queue)."""

    def select(self, pool: ProxyPool, context: SelectionContext | None = None) -> Proxy:
        healthy = pool.get_healthy_proxies()
        if not healthy:
            raise ProxyPoolEmptyError("No healthy proxies available")
        return healthy[0]

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        proxy.complete_request(success=success, response_time_ms=response_time_ms)
```

Register it globally so other components can look it up by name:

```python
from proxywhirl import StrategyRegistry

registry = StrategyRegistry()
registry.register_strategy("priority", PriorityStrategy)

# Retrieve later
strategy_cls = registry.get_strategy("priority")
rotator = ProxyRotator(proxies=proxies, strategy=strategy_cls())
```

```{warning}
Custom strategies used in multi-threaded code must be thread-safe. Protect shared mutable state with ``threading.Lock`` or use {class}`~proxywhirl.StrategyState` for per-proxy metrics tracking.
```

---

## Further Reading

- {doc}`/guides/advanced-strategies` -- deep dive into composite pipelines and EMA tuning
- {doc}`/guides/retry-failover` -- circuit breakers and retry policies that work alongside strategies
- {doc}`/guides/async-client` -- async patterns with strategy selection
- {doc}`/reference/python-api` -- complete API reference for all strategy classes
