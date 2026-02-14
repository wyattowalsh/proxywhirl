---
title: Advanced Rotation Strategies
---

# Advanced Rotation Strategies

ProxyWhirl provides 9 built-in rotation strategies for intelligent proxy selection. This guide covers the advanced strategies beyond basic round-robin and random selection, including performance-based routing, session persistence, geo-targeting, cost optimization, and composite strategies.

```{contents}
:local:
:depth: 2
```

## Overview

All strategies implement the `RotationStrategy` protocol:

```python
from typing import Protocol, Optional
from proxywhirl.models import Proxy, ProxyPool, SelectionContext

class RotationStrategy(Protocol):
    """Protocol defining interface for proxy rotation strategies."""

    def select(self, pool: ProxyPool, context: Optional[SelectionContext] = None) -> Proxy:
        """Select a proxy from the pool based on strategy logic."""
        ...

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        """Record the result of using a proxy."""
        ...
```

### Available Strategies

| Strategy | Use Case | Key Feature |
|----------|----------|-------------|
| `RoundRobinStrategy` | Even distribution | Sequential rotation |
| `RandomStrategy` | Unpredictable patterns | Random selection |
| `WeightedStrategy` | Custom prioritization | Configurable weights |
| `LeastUsedStrategy` | Load balancing | Tracks request count |
| `PerformanceBasedStrategy` | Speed optimization | EMA response times |
| `SessionPersistenceStrategy` | Sticky sessions | Session-to-proxy binding |
| `GeoTargetedStrategy` | Geographic routing | Country/region filtering |
| `CostAwareStrategy` | Cost optimization | Free proxy prioritization |
| `CompositeStrategy` | Complex requirements | Combines multiple strategies |

## Performance-Based Strategy

Selects proxies using weighted random selection based on inverse EMA (Exponential Moving Average) response times. Faster proxies receive higher selection weights, adaptively favoring better-performing proxies while still giving all proxies a chance.

```{note}
Uses the cold-start exploration pattern: new proxies get equal selection probability for the first N requests (default: 5) before being subject to performance-based weighting.
```

### When to Use

- **Speed is critical** (latency-sensitive applications)
- **Proxy performance varies significantly** across your pool
- **Need automatic adaptation** to changing conditions
- **Heterogeneous proxy pools** with mixed performance characteristics

### Performance Characteristics

- **Selection overhead:** <1ms (weighted random with exploration)
- **Performance gain:** 15-25% faster average response times vs round-robin
- **Adaptation speed:** Configurable via `ema_alpha` (0.0-1.0)
- **Cold start:** Exploration trials (default: 5) prevent proxy starvation

### Configuration

```python
from proxywhirl import ProxyRotator, Proxy, StrategyConfig
from proxywhirl.strategies import PerformanceBasedStrategy

# Create proxies
proxies = [
    Proxy(url="http://proxy1.example.com:8080"),
    Proxy(url="http://proxy2.example.com:8080"),
    Proxy(url="http://proxy3.example.com:8080"),
]

# Configure strategy with EMA parameters via StrategyConfig (not on Proxy)
config = StrategyConfig(
    ema_alpha=0.2,  # Smoothing factor: higher = more weight to recent values
)

strategy = PerformanceBasedStrategy()
strategy.configure(config)

# Use with rotator
rotator = ProxyRotator(proxies=proxies, strategy=strategy)
response = rotator.get("https://api.example.com/data")
```

### How It Works

The strategy uses **inverse EMA response time** as selection weight:

```python
weight = 1.0 / proxy.ema_response_time_ms
```

Faster proxies (lower EMA) get exponentially higher selection probability.

**EMA Update Formula:**
```
EMA_new = alpha * current_value + (1 - alpha) * EMA_old
```

**Alpha Tuning:**
- `alpha=0.1`: Slow adaptation, stable (10% weight to new samples)
- `alpha=0.2`: Balanced (default)
- `alpha=0.5`: Fast adaptation, reactive

### Warmup Period

New proxies need historical data before they can be selected:

```python
from proxywhirl.models import ProxyPool

pool = ProxyPool(name="perf-pool")

# Warm up new proxies with initial requests
for proxy in proxies:
    proxy.start_request()
    proxy.complete_request(success=True, response_time_ms=100.0)
    pool.add_proxy(proxy)

strategy = PerformanceBasedStrategy()

# Now strategy can select from proxies with EMA data
selected = strategy.select(pool)
```

```{tip}
Use `LeastUsedStrategy` or `RoundRobinStrategy` during initial warmup to distribute requests evenly, then switch to `PerformanceBasedStrategy` once all proxies have EMA data. See {doc}`async-client` for hot-swapping strategies at runtime.
```

### Adaptation Example

The strategy automatically adapts to changing proxy performance:

```python
from proxywhirl.models import SelectionContext

# Simulate proxy performance changes
proxy_speeds = {
    "http://proxy1.example.com:8080": 50.0,   # Fast
    "http://proxy2.example.com:8080": 200.0,  # Medium
    "http://proxy3.example.com:8080": 500.0,  # Slow
}

# Phase 1: Initial performance profile
for _ in range(50):
    proxy = strategy.select(pool)
    response_time = proxy_speeds[proxy.url]
    strategy.record_result(proxy, success=True, response_time_ms=response_time)

# Phase 2: Proxy 3 improves dramatically
proxy_speeds["http://proxy3.example.com:8080"] = 30.0  # Now fastest!

# Strategy adapts over ~20-30 requests (with alpha=0.2)
for _ in range(30):
    proxy = strategy.select(pool)
    response_time = proxy_speeds[proxy.url]
    strategy.record_result(proxy, success=True, response_time_ms=response_time)

# Proxy 3 now gets selected most frequently
```

### Success Criteria

- **SC-004:** 15-25% response time reduction vs round-robin
- **SC-007:** <5ms selection overhead (meets target at ~9µs)
- **Adaptation:** Reacts to speed changes within 20-30 requests (alpha=0.2)

## Session Persistence Strategy

Maintains consistent proxy assignment for a session ID across multiple requests. Ensures all requests in a session use the same proxy (sticky sessions).

:::{tip}
Session persistence works well with {doc}`retry-failover` -- when a session's assigned proxy fails, the strategy automatically fails over to a new proxy while maintaining the session binding.
:::

### When to Use

- **Stateful web scraping** where cookies/sessions matter
- **Shopping cart flows** requiring consistent identity
- **API rate limits** tied to IP addresses
- **Login workflows** with IP-based security

### Performance Characteristics

- **Selection overhead:** <1ms (O(1) hash lookup)
- **Session capacity:** 10,000 active sessions (default, configurable)
- **Memory:** ~200 bytes per session
- **Same-proxy guarantee:** 99.9% (SC-005)

### Configuration

```python
from proxywhirl import StrategyConfig, SelectionContext
from proxywhirl.strategies import SessionPersistenceStrategy

# Create strategy with session limits
strategy = SessionPersistenceStrategy(
    max_sessions=10000,           # Maximum active sessions
    auto_cleanup_threshold=100,   # Cleanup frequency
)

# Configure session TTL
config = StrategyConfig(
    session_stickiness_duration_seconds=3600,  # 1 hour TTL
)
strategy.configure(config)

# Select proxy with session ID
context = SelectionContext(session_id="user-12345")
proxy = strategy.select(pool, context)

# Subsequent requests with same session ID get same proxy
context2 = SelectionContext(session_id="user-12345")
proxy2 = strategy.select(pool, context2)

assert proxy.id == proxy2.id  # Same proxy!
```

### Session Lifecycle

```{mermaid}
graph LR
    A[New Session ID] --> B{Existing Session?}
    B -->|No| C[Select New Proxy]
    B -->|Yes| D{Proxy Healthy?}
    D -->|Yes| E[Reuse Same Proxy]
    D -->|No| F[Failover: Select New Proxy]
    C --> G[Create Session Record]
    F --> G
    G --> H[Update last_used_at]
    E --> H
```

### Session Management

```python
# Get session statistics
stats = strategy.get_session_stats()
print(f"Active sessions: {stats['total_sessions']}/{stats['max_sessions']}")

# Manually close session (optional)
strategy.close_session("user-12345")

# Cleanup expired sessions (automatic every 100 operations)
expired_count = strategy.cleanup_expired_sessions()
print(f"Removed {expired_count} expired sessions")
```

### Failover Behavior

When the assigned proxy becomes unhealthy, the strategy automatically fails over:

```python
from proxywhirl.models import HealthStatus

# Session initially assigned to proxy1
context = SelectionContext(session_id="session-abc")
proxy1 = strategy.select(pool, context)

# Mark proxy1 as dead
proxy1.health_status = HealthStatus.DEAD

# Failover: strategy assigns new proxy for session
proxy2 = strategy.select(pool, context)

assert proxy2.id != proxy1.id  # Different proxy
assert proxy2.health_status == HealthStatus.HEALTHY

# Future requests continue with proxy2
proxy3 = strategy.select(pool, context)
assert proxy3.id == proxy2.id  # Sticky to new proxy
```

### TTL and Expiration

Sessions automatically expire after the configured TTL:

```python
from datetime import datetime, timedelta, timezone

# Create session with 5-minute TTL
config = StrategyConfig(session_stickiness_duration_seconds=300)
strategy.configure(config)

context = SelectionContext(session_id="short-lived")
proxy1 = strategy.select(pool, context)

# Simulate 6 minutes passing
import time
time.sleep(360)

# Session expired, new proxy assigned
proxy2 = strategy.select(pool, context)
# proxy2 may differ from proxy1 (new session created)
```

### LRU Eviction

When `max_sessions` limit is reached, least recently used sessions are evicted:

```python
strategy = SessionPersistenceStrategy(max_sessions=3)

# Create 3 sessions (fills capacity)
for i in range(3):
    context = SelectionContext(session_id=f"session-{i}")
    strategy.select(pool, context)

# Touch session-1 to mark as recently used
context = SelectionContext(session_id="session-1")
strategy.select(pool, context)

# Create 4th session - evicts session-0 (LRU)
context = SelectionContext(session_id="session-3")
strategy.select(pool, context)

# session-0 is gone, session-1 and session-2 remain
```

### Success Criteria

- **SC-005:** 99.9% same-proxy guarantee for session requests
- **Performance:** <1ms session lookup overhead
- **Capacity:** Supports 10,000+ active sessions

## Geo-Targeted Strategy

Filters proxies by geographical location (country or region) before selection.

### When to Use

- **Region-locked content** (streaming, news sites)
- **Geo-distributed testing** (CDN behavior, localization)
- **Regulatory compliance** (data sovereignty requirements)
- **Performance optimization** (select proxies near target servers)

### Performance Characteristics

- **Selection overhead:** ~2-4ms (O(n) filtering + secondary selection)
- **Filter accuracy:** 100% when geo metadata available (SC-006)
- **Fallback:** Configurable (use any proxy or strict filtering)

### Configuration

```python
from proxywhirl import StrategyConfig, SelectionContext, Proxy
from proxywhirl.strategies import GeoTargetedStrategy

# Create proxies with country codes
proxies = [
    Proxy(url="http://us-proxy1.com:8080", country_code="US", region="California"),
    Proxy(url="http://us-proxy2.com:8080", country_code="US", region="New York"),
    Proxy(url="http://uk-proxy1.com:8080", country_code="GB", region="London"),
    Proxy(url="http://de-proxy1.com:8080", country_code="DE", region="Berlin"),
]

# Configure strategy
strategy = GeoTargetedStrategy()
config = StrategyConfig(
    geo_fallback_enabled=True,         # Fallback to any proxy if no match
    geo_secondary_strategy="round_robin",  # Selection from filtered set
)
strategy.configure(config)

# Select US proxy
context = SelectionContext(target_country="US")
proxy = strategy.select(pool, context)
assert proxy.country_code == "US"

# Select by region (more specific)
context = SelectionContext(target_region="California")
proxy = strategy.select(pool, context)
assert proxy.region == "California"
```

### Country Codes

Use **ISO 3166-1 alpha-2** country codes:

```python
# Common country codes
context = SelectionContext(target_country="US")  # United States
context = SelectionContext(target_country="GB")  # United Kingdom
context = SelectionContext(target_country="DE")  # Germany
context = SelectionContext(target_country="FR")  # France
context = SelectionContext(target_country="JP")  # Japan
context = SelectionContext(target_country="AU")  # Australia
```

### Filtering Logic

The strategy applies filters in this order:

1. **Country filter** (if `target_country` specified) - takes precedence
2. **Region filter** (if `target_region` specified and no country)
3. **Failed proxy filter** (excludes `failed_proxy_ids`)
4. **Fallback** (if no matches and `geo_fallback_enabled=True`)

```python
from proxywhirl.models import HealthStatus

# Country takes precedence over region
context = SelectionContext(
    target_country="US",      # Country filter applied
    target_region="London",   # Ignored (country specified)
)
proxy = strategy.select(pool, context)
assert proxy.country_code == "US"  # Not London/GB

# Region-only filtering
context = SelectionContext(target_region="London")
proxy = strategy.select(pool, context)
assert proxy.region == "London"
```

### Fallback Modes

**Enabled fallback** (default):
```python
config = StrategyConfig(geo_fallback_enabled=True)
strategy.configure(config)

# No proxies in Antarctica - falls back to any healthy proxy
context = SelectionContext(target_country="AQ")
proxy = strategy.select(pool, context)  # Returns any healthy proxy
```

**Disabled fallback** (strict):
```python
from proxywhirl.exceptions import ProxyPoolEmptyError

config = StrategyConfig(geo_fallback_enabled=False)
strategy.configure(config)

# No proxies in Antarctica - raises error
context = SelectionContext(target_country="AQ")
try:
    proxy = strategy.select(pool, context)
except ProxyPoolEmptyError as e:
    print(f"No proxies for target location: {e}")
```

### Secondary Selection Strategies

Choose how to select from the geo-filtered proxy set:

```python
config = StrategyConfig(
    geo_secondary_strategy="round_robin",  # Default: even distribution
    # geo_secondary_strategy="random",     # Random selection
    # geo_secondary_strategy="least_used", # Load balancing
)
strategy.configure(config)

# Filter to US proxies, then round-robin among them
context = SelectionContext(target_country="US")
for _ in range(10):
    proxy = strategy.select(pool, context)
    print(f"Selected: {proxy.url} ({proxy.country_code})")
```

### Retry Integration

Works seamlessly with {doc}`retry-failover` to exclude failed proxies:

```python
# First attempt
context = SelectionContext(
    target_country="US",
    failed_proxy_ids=[],  # No failures yet
)
proxy1 = strategy.select(pool, context)

# Simulate failure
strategy.record_result(proxy1, success=False, response_time_ms=5000.0)

# Retry with failed proxy excluded
context = SelectionContext(
    target_country="US",
    failed_proxy_ids=[str(proxy1.id)],  # Exclude failed proxy
)
proxy2 = strategy.select(pool, context)

assert proxy2.id != proxy1.id  # Different US proxy
assert proxy2.country_code == "US"
```

### Success Criteria

- **SC-006:** 100% correct region selection when geo data available
- **Performance:** <5ms selection overhead (meets target)
- **Coverage:** Supports ISO 3166-1 alpha-2 country codes

## Cost-Aware Strategy

Prioritizes free proxies over paid ones using weighted random selection based on inverse cost. Lower cost proxies are more likely to be selected, with free proxies (cost = 0.0) receiving a significant boost multiplier.

```{note}
Free proxies get a default 10x weight boost, making them highly favored while still allowing paid proxies to be selected when needed.
```

### When to Use

- **Mixed free/paid proxy pools** where cost optimization is important
- **High-volume scraping** with budget constraints
- **Cost-conscious operations** requiring proxy diversity

### Configuration

```python
from proxywhirl import AsyncProxyRotator, Proxy, StrategyConfig
from proxywhirl.strategies import CostAwareStrategy

# Create cost-aware strategy instance
strategy = CostAwareStrategy()

async with AsyncProxyRotator(strategy=strategy) as rotator:
    # Add proxies with cost metadata
    await rotator.add_proxy(Proxy(
        url="http://free-proxy1.com:8080",
        cost_per_request=0.0  # Free
    ))
    await rotator.add_proxy(Proxy(
        url="http://cheap-proxy.com:8080",
        cost_per_request=0.01  # $0.01 per request
    ))
    await rotator.add_proxy(Proxy(
        url="http://premium-proxy.com:8080",
        cost_per_request=0.10  # $0.10 per request
    ))

    # Free proxy heavily favored (~91% selection probability)
    for _ in range(100):
        proxy = await rotator.get_proxy()
        # Likely free-proxy1
```

### Weight Calculation

The strategy calculates inverse cost weights:

```
For free proxy (cost = 0.0):
    weight = free_proxy_boost (default: 10.0)

For paid proxy (cost > 0.0):
    weight = 1.0 / (cost + 0.001)

Weights are normalized to sum to 1.0
```

### Cost Threshold Filtering

```python
from proxywhirl import AsyncProxyRotator, Proxy, StrategyConfig
from proxywhirl.strategies import CostAwareStrategy

# Configure strategy with cost thresholds
config = StrategyConfig(
    metadata={
        "max_cost_per_request": 0.05,  # Filter out expensive proxies
        "free_proxy_boost": 10.0,      # Weight multiplier for free proxies
    }
)

strategy = CostAwareStrategy()
strategy.configure(config)

async with AsyncProxyRotator(strategy=strategy) as rotator:
    await rotator.add_proxy(Proxy(url="http://cheap.com:8080", cost_per_request=0.01))
    await rotator.add_proxy(Proxy(url="http://expensive.com:8080", cost_per_request=0.20))

    # expensive-proxy filtered out (exceeds max_cost_per_request)
    proxy = await rotator.get_proxy()
    assert proxy.cost_per_request <= 0.05
```

### Best Practices

**Configuration tips:**
- Set `max_cost_per_request` to hard budget limit
- Adjust `free_proxy_boost` based on free proxy reliability (lower if unreliable)
- Combine with `PerformanceBasedStrategy` via `CompositeStrategy` for cost + speed optimization

```python
from proxywhirl import AsyncProxyRotator, StrategyConfig
from proxywhirl.strategies import CostAwareStrategy

# Recommended production configuration
config = StrategyConfig(
    metadata={
        "max_cost_per_request": 0.05,  # $0.05 budget ceiling
        "free_proxy_boost": 5.0,       # Lower boost if free proxies unreliable
    }
)

strategy = CostAwareStrategy()
strategy.configure(config)

async with AsyncProxyRotator(strategy=strategy) as rotator:
    # Add proxies with cost metadata
    pass
```

## Composite Strategy

Composes multiple strategies into a filter → select pipeline. Apply filtering strategies first, then selection strategy on the filtered set.

### When to Use

- **Multi-criteria selection** (e.g., geo + performance)
- **Complex business logic** requiring multiple stages
- **Reusable filter chains** for different use cases

### Performance Characteristics

- **Selection overhead:** Sum of filter + selector times (target <5ms total)
- **Flexibility:** Arbitrary filter chains
- **Composability:** Can nest composite strategies

### Architecture

```{mermaid}
graph LR
    A[Proxy Pool] --> B[Filter 1: Geo]
    B --> C[Filter 2: ...]
    C --> D[Selector: Performance]
    D --> E[Selected Proxy]
```

### Basic Composition

```python
from proxywhirl import SelectionContext
from proxywhirl.strategies import (
    CompositeStrategy,
    GeoTargetedStrategy,
    PerformanceBasedStrategy,
)

# Geo-filter + performance-based selection
strategy = CompositeStrategy(
    filters=[GeoTargetedStrategy()],
    selector=PerformanceBasedStrategy(),
)

# Select fastest US proxy
context = SelectionContext(target_country="US")
proxy = strategy.select(pool, context)

assert proxy.country_code == "US"
# proxy is also the fastest US proxy based on EMA
```

### Common Patterns

**Pattern 1: Geo + Performance**
```python
# Select fastest proxy in target region
geo_filter = GeoTargetedStrategy()
perf_selector = PerformanceBasedStrategy()

strategy = CompositeStrategy(
    filters=[geo_filter],
    selector=perf_selector,
)

# Get fastest UK proxy
context = SelectionContext(target_country="GB")
proxy = strategy.select(pool, context)
```

**Pattern 2: Geo + Load Balancing**
```python
# Evenly distribute load within region
from proxywhirl.strategies import LeastUsedStrategy

strategy = CompositeStrategy(
    filters=[GeoTargetedStrategy()],
    selector=LeastUsedStrategy(),
)

# Balance load across US proxies
context = SelectionContext(target_country="US")
for _ in range(100):
    proxy = strategy.select(pool, context)
    proxy.start_request()
```

**Pattern 3: Multi-Stage Filtering**
```python
# Multiple filters applied sequentially
filter1 = GeoTargetedStrategy()
filter2 = CustomHealthFilter()  # Your custom filter

strategy = CompositeStrategy(
    filters=[filter1, filter2],
    selector=PerformanceBasedStrategy(),
)
```

### Configuration from Dict

Create composite strategies from configuration:

```python
config = {
    "filters": ["geo-targeted"],
    "selector": "performance-based",
}

strategy = CompositeStrategy.from_config(config)

# Equivalent to:
# strategy = CompositeStrategy(
#     filters=[GeoTargetedStrategy()],
#     selector=PerformanceBasedStrategy(),
# )
```

### Validation Example

```python
from proxywhirl import Proxy, ProxyPool, HealthStatus, SelectionContext
from proxywhirl.strategies import CompositeStrategy, GeoTargetedStrategy, PerformanceBasedStrategy
from collections import Counter

# Create diverse pool
pool = ProxyPool(name="global-pool")

us_proxies = [
    Proxy(url=f"http://us{i}.com:8080", country_code="US",
          health_status=HealthStatus.HEALTHY)
    for i in range(5)
]
uk_proxies = [
    Proxy(url=f"http://uk{i}.com:8080", country_code="GB",
          health_status=HealthStatus.HEALTHY)
    for i in range(5)
]

# Different performance profiles
for i, proxy in enumerate(us_proxies):
    pool.add_proxy(proxy)
    proxy.start_request()
    proxy.complete_request(success=True, response_time_ms=100.0 + i * 50)

for proxy in uk_proxies:
    pool.add_proxy(proxy)
    proxy.start_request()
    proxy.complete_request(success=True, response_time_ms=200.0)

# Use composite strategy
strategy = CompositeStrategy(
    filters=[GeoTargetedStrategy()],
    selector=PerformanceBasedStrategy(),
)

context = SelectionContext(target_country="US")

# Make selections - should favor faster US proxies
selections = Counter()
for _ in range(100):
    proxy = strategy.select(pool, context)
    selections[proxy.url] += 1

# Validate: all US proxies, fastest selected most
assert all("us" in url for url in selections.keys())
assert selections["http://us0.com:8080"] > selections["http://us4.com:8080"]
```

### Performance Considerations

The composite strategy must still meet the <5ms overhead target:

```python
from proxywhirl import Proxy, ProxyPool, HealthStatus, SelectionContext
from proxywhirl.strategies import CompositeStrategy, GeoTargetedStrategy, PerformanceBasedStrategy
import time

# Create large pool
pool = ProxyPool(name="perf-test")
for i in range(100):
    country = "US" if i < 50 else "GB"
    proxy = Proxy(
        url=f"http://proxy{i}.com:8080",
        country_code=country,
        health_status=HealthStatus.HEALTHY,
    )
    proxy.start_request()
    proxy.complete_request(success=True, response_time_ms=100.0)
    pool.add_proxy(proxy)

strategy = CompositeStrategy(
    filters=[GeoTargetedStrategy()],
    selector=PerformanceBasedStrategy(),
)

# Measure performance
context = SelectionContext(target_country="US")
start = time.perf_counter()

for _ in range(1000):
    strategy.select(pool, context)

elapsed_ms = (time.perf_counter() - start) * 1000
avg_ms = elapsed_ms / 1000

print(f"Average selection time: {avg_ms:.3f}ms")
assert avg_ms < 5.0  # Meets SC-007
```

### Success Criteria

- **SC-007:** <5ms total selection overhead
- **SC-009:** Strategy composition completes in <100ms
- **Correctness:** All filters applied in order

## Strategy Registry

Register custom strategies for reuse and configuration-driven instantiation.

### Registration

```python
from proxywhirl.strategies import StrategyRegistry

# Define custom strategy
class MyCustomStrategy:
    def select(self, pool, context=None):
        # Custom selection logic
        proxies = pool.get_healthy_proxies()
        return proxies[0] if proxies else None

    def record_result(self, proxy, success, response_time_ms):
        # Track results
        pass

# Register strategy
registry = StrategyRegistry()
registry.register_strategy("my-custom", MyCustomStrategy)

# Retrieve and use
strategy_class = registry.get_strategy("my-custom")
strategy = strategy_class()
```

### Validation

The registry validates strategies implement the `RotationStrategy` protocol:

```python
# Missing required methods
class BadStrategy:
    pass

try:
    registry.register_strategy("bad", BadStrategy)
except TypeError as e:
    print(f"Validation failed: {e}")
    # "Strategy BadStrategy missing required methods: select, record_result"
```

### Thread Safety

The registry is a thread-safe singleton:

```python
# Multiple threads can safely register/retrieve strategies
import threading

def register_strategies():
    registry = StrategyRegistry()  # Same instance
    registry.register_strategy("thread-safe", MyCustomStrategy)

threads = [threading.Thread(target=register_strategies) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

# All registrations succeed (last one wins if duplicate names)
```

### Listing Strategies

```python
registry = StrategyRegistry()

# List all registered strategies
strategies = registry.list_strategies()
print(f"Available strategies: {strategies}")

# Unregister a strategy
registry.unregister_strategy("my-custom")
```

## SelectionContext

The `SelectionContext` model provides contextual information for intelligent proxy selection.

### Fields

```python
from proxywhirl import SelectionContext

context = SelectionContext(
    # Session tracking
    session_id="user-12345",

    # Geo-targeting
    target_country="US",
    target_region="California",

    # Request metadata
    target_url="https://api.example.com",
    request_priority=8,
    timeout_ms=5000.0,

    # Retry tracking
    failed_proxy_ids=["uuid-1", "uuid-2"],
    attempt_number=3,

    # Custom data
    metadata={"user_tier": "premium"},
)
```

### Usage with Strategies

All advanced strategies accept `SelectionContext`:

```python
# Session persistence requires session_id
context = SelectionContext(session_id="session-abc")
proxy = session_strategy.select(pool, context)

# Geo-targeting uses target_country/target_region
context = SelectionContext(target_country="US")
proxy = geo_strategy.select(pool, context)

# Retry logic uses failed_proxy_ids
context = SelectionContext(
    failed_proxy_ids=[str(failed_proxy.id)],
    attempt_number=2,
)
proxy = any_strategy.select(pool, context)
```

## StrategyConfig

The `StrategyConfig` model provides configuration for all strategies.

### Fields

```python
from proxywhirl import StrategyConfig
from proxywhirl.strategies import PerformanceBasedStrategy

config = StrategyConfig(
    # Weighted strategy
    weights={
        "http://proxy1.com:8080": 0.5,
        "http://proxy2.com:8080": 0.3,
        "http://proxy3.com:8080": 0.2,
    },

    # Performance-based strategy
    ema_alpha=0.2,  # EMA smoothing factor

    # Session persistence
    session_stickiness_duration_seconds=3600,  # 1 hour TTL

    # Geo-targeting
    preferred_countries=["US", "GB"],
    preferred_regions=["California", "London"],
    geo_fallback_enabled=True,
    geo_secondary_strategy="round_robin",

    # Fallback behavior
    fallback_strategy="random",

    # Performance thresholds
    max_response_time_ms=5000.0,
    min_success_rate=0.8,

    # Sliding window
    window_duration_seconds=3600,  # 1 hour
)

# Apply to strategy
strategy = PerformanceBasedStrategy()
strategy.configure(config)
```

### Per-Strategy Configuration

Different strategies use different fields:

```python
from proxywhirl import StrategyConfig
from proxywhirl.strategies import PerformanceBasedStrategy, SessionPersistenceStrategy, GeoTargetedStrategy

# Performance-based: uses ema_alpha
perf_config = StrategyConfig(ema_alpha=0.3)
perf_strategy = PerformanceBasedStrategy()
perf_strategy.configure(perf_config)

# Session persistence: uses session_stickiness_duration_seconds
session_config = StrategyConfig(session_stickiness_duration_seconds=1800)
session_strategy = SessionPersistenceStrategy()
session_strategy.configure(session_config)

# Geo-targeted: uses geo_* fields
geo_config = StrategyConfig(
    geo_fallback_enabled=False,
    geo_secondary_strategy="least_used",
)
geo_strategy = GeoTargetedStrategy()
geo_strategy.configure(geo_config)
```

## Custom Strategy Implementation

Create custom strategies by implementing the `RotationStrategy` protocol. For the full API surface, see {doc}`/reference/python-api`.

### Implementing the Protocol

```python
from typing import Optional
from proxywhirl import Proxy, ProxyPool, SelectionContext
from proxywhirl.exceptions import ProxyPoolEmptyError

class PriorityStrategy:
    """Select proxies based on custom priority field."""

    def __init__(self):
        self.config = None

    def select(self, pool: ProxyPool, context: Optional[SelectionContext] = None) -> Proxy:
        """Select highest priority healthy proxy."""
        healthy_proxies = pool.get_healthy_proxies()

        if not healthy_proxies:
            raise ProxyPoolEmptyError("No healthy proxies available")

        # Filter by failed proxies from context
        if context and context.failed_proxy_ids:
            failed_ids = set(context.failed_proxy_ids)
            healthy_proxies = [p for p in healthy_proxies if str(p.id) not in failed_ids]

            if not healthy_proxies:
                raise ProxyPoolEmptyError("No healthy proxies after filtering")

        # Select proxy with highest priority (from metadata)
        proxy = max(healthy_proxies, key=lambda p: p.metadata.get("priority", 0))

        # Mark request start
        proxy.start_request()

        return proxy

    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None:
        """Record request result."""
        proxy.complete_request(success=success, response_time_ms=response_time_ms)

    def configure(self, config):
        """Optional: accept configuration."""
        self.config = config
```

### Registering Custom Strategies

Use `StrategyRegistry` to register and reuse custom strategies. Registered strategies are also available through the {doc}`cli-reference` (`proxywhirl config set rotation_strategy ...`) and the {doc}`mcp-server` (`set_strategy` action).

```python
from proxywhirl import AsyncProxyRotator, Proxy
from proxywhirl.strategies import StrategyRegistry

# Register the strategy
registry = StrategyRegistry()
registry.register_strategy("priority", PriorityStrategy)

# Use the custom strategy instance
strategy = PriorityStrategy()

async with AsyncProxyRotator(strategy=strategy) as rotator:
    # Add proxies with priority metadata
    await rotator.add_proxy(Proxy(
        url="http://proxy1.com:8080",
        metadata={"priority": 10}
    ))
    await rotator.add_proxy(Proxy(
        url="http://proxy2.com:8080",
        metadata={"priority": 5}
    ))

    # Selects proxy1 (higher priority)
    proxy = await rotator.get_proxy()
```

## StrategyRegistry Usage

The `StrategyRegistry` provides a singleton registry for custom rotation strategies.

### Registration and Validation

```python
from proxywhirl.strategies import StrategyRegistry

# Get singleton instance
registry = StrategyRegistry()

# Register strategy with validation
registry.register_strategy("custom", CustomStrategy, validate=True)

# List all strategies
strategies = registry.list_strategies()
print(f"Available: {strategies}")

# Retrieve strategy class
strategy_class = registry.get_strategy("custom")
strategy = strategy_class()
```

### Strategy Validation

The registry validates strategies on registration:

```python
class InvalidStrategy:
    """Missing required methods."""
    def select(self, pool):
        return pool.get_all_proxies()[0]
    # Missing record_result() method!

registry = StrategyRegistry()

try:
    registry.register_strategy("invalid", InvalidStrategy)
except TypeError as e:
    print(f"Validation failed: {e}")
    # Output: Strategy InvalidStrategy missing required methods: record_result
```

### Thread Safety

The registry is thread-safe with double-checked locking:

```python
import concurrent.futures
from proxywhirl.strategies import StrategyRegistry

def register_strategy(name, strategy_class):
    registry = StrategyRegistry()
    registry.register_strategy(name, strategy_class)

# Safe to register from multiple threads
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [
        executor.submit(register_strategy, f"strategy-{i}", CustomStrategy)
        for i in range(10)
    ]
    concurrent.futures.wait(futures)
```

### Unregistering Strategies

```python
registry = StrategyRegistry()

# Register
registry.register_strategy("custom", CustomStrategy)

# Unregister
registry.unregister_strategy("custom")

# Verify removal
try:
    registry.get_strategy("custom")
except KeyError as e:
    print(f"Strategy removed: {e}")
```

### Testing with Registry Reset

```python
from proxywhirl.strategies import StrategyRegistry

def test_custom_strategy():
    # Reset to clean state
    StrategyRegistry.reset()

    registry = StrategyRegistry()
    registry.register_strategy("test-strategy", TestStrategy)

    # Test the strategy
    # ...

    # Cleanup
    StrategyRegistry.reset()
```

```{warning}
`StrategyRegistry.reset()` should only be used in tests. Calling it in production will clear all registered strategies.
```

### Performance Requirements

- **SC-010**: Strategy registration <1 second load time
- **Validation**: <1ms per strategy
- **Retrieval**: O(1) lookup

## Best Practices

### 1. Choose the Right Strategy

```python
# Stateful scraping? Use session persistence
if requires_cookies_or_login:
    strategy = SessionPersistenceStrategy()

# Geo-locked content? Use geo-targeting
elif requires_specific_region:
    strategy = GeoTargetedStrategy()

# Performance-critical? Use performance-based
elif latency_sensitive:
    strategy = PerformanceBasedStrategy()

# Complex requirements? Use composite
else:
    strategy = CompositeStrategy(
        filters=[GeoTargetedStrategy()],
        selector=PerformanceBasedStrategy(),
    )
```

### 2. Warm Up Performance-Based Strategies

```python
# Don't use performance-based immediately
pool = ProxyPool(name="new-pool")
for proxy in fetch_new_proxies():
    pool.add_proxy(proxy)

# Warm up with round-robin first
warmup_strategy = RoundRobinStrategy()
for _ in range(len(pool.proxies) * 5):  # 5 requests per proxy
    proxy = warmup_strategy.select(pool)
    # Make request and record result
    warmup_strategy.record_result(proxy, success=True, response_time_ms=100.0)

# Now switch to performance-based
strategy = PerformanceBasedStrategy()
```

### 3. Monitor Session Memory

```python
strategy = SessionPersistenceStrategy(max_sessions=10000)

# Periodically check session count
stats = strategy.get_session_stats()
if stats['total_sessions'] > 8000:  # 80% capacity
    print("Warning: High session count")
    strategy.cleanup_expired_sessions()
```

### 4. Use SelectionContext Consistently

```python
# Build context once per request
context = SelectionContext(
    session_id=user_session_id,
    target_country=user_country,
    failed_proxy_ids=[],
)

# Reuse for retries
for attempt in range(max_retries):
    try:
        proxy = strategy.select(pool, context)
        response = make_request(proxy, url)
        strategy.record_result(proxy, success=True, response_time_ms=elapsed)
        break
    except Exception:
        strategy.record_result(proxy, success=False, response_time_ms=5000.0)
        context.failed_proxy_ids.append(str(proxy.id))
        context.attempt_number += 1
```

### 5. Validate Geo Data Availability

```python
# Check if geo data is available before using geo-targeting
pool = ProxyPool(name="global")
for proxy in proxies:
    pool.add_proxy(proxy)

geo_coverage = sum(1 for p in pool.proxies if p.country_code) / len(pool.proxies)
print(f"Geo coverage: {geo_coverage:.1%}")

if geo_coverage > 0.5:  # At least 50% have geo data
    strategy = GeoTargetedStrategy()
else:
    print("Warning: Low geo coverage, using alternative strategy")
    strategy = PerformanceBasedStrategy()
```

## Troubleshooting

### ProxyPoolEmptyError: No proxies with EMA data

```python
# Problem: Using PerformanceBasedStrategy on new proxies
strategy = PerformanceBasedStrategy()
proxy = strategy.select(pool)  # Error!

# Solution: Warm up proxies first
for proxy in pool.get_all_proxies():
    proxy.start_request()
    proxy.complete_request(success=True, response_time_ms=100.0)

# Now it works
proxy = strategy.select(pool)
```

### SessionPersistenceStrategy requires SelectionContext with session_id

```python
# Problem: Missing session_id
proxy = session_strategy.select(pool)  # Error!

# Solution: Always provide session_id
context = SelectionContext(session_id="user-session-123")
proxy = session_strategy.select(pool, context)
```

### Geo-targeting returns unexpected proxies

```python
# Problem: Fallback enabled, returns any proxy when no match
config = StrategyConfig(geo_fallback_enabled=True)
strategy.configure(config)

context = SelectionContext(target_country="ZZ")  # Invalid country
proxy = strategy.select(pool, context)  # Returns any proxy

# Solution: Disable fallback for strict filtering
config = StrategyConfig(geo_fallback_enabled=False)
strategy.configure(config)

try:
    proxy = strategy.select(pool, context)
except ProxyPoolEmptyError:
    print("No proxies for target country")
```

### Composite strategy too slow

```python
# Problem: Too many filters or large pool
strategy = CompositeStrategy(
    filters=[Filter1(), Filter2(), Filter3()],
    selector=PerformanceBasedStrategy(),
)

# Solution: Reduce filter count or optimize filters
strategy = CompositeStrategy(
    filters=[GeoTargetedStrategy()],  # Single filter
    selector=PerformanceBasedStrategy(),
)

# Or: Pre-filter pool outside strategy
us_proxies = [p for p in pool.proxies if p.country_code == "US"]
filtered_pool = ProxyPool(name="us-only", proxies=us_proxies)
strategy = PerformanceBasedStrategy()
proxy = strategy.select(filtered_pool)
```

## Testing Strategies

All strategies have comprehensive integration tests in `tests/integration/test_rotation_strategies.py`. Use these as examples:

```python
import pytest
from proxywhirl import ProxyPool, Proxy, HealthStatus, SelectionContext
from proxywhirl.strategies import PerformanceBasedStrategy

def test_my_use_case():
    """Test performance-based strategy with my specific scenario."""
    # Arrange
    pool = ProxyPool(name="test-pool")

    # Create proxies matching your scenario
    for i in range(10):
        proxy = Proxy(
            url=f"http://proxy{i}.example.com:8080",
            health_status=HealthStatus.HEALTHY,
        )
        # Warm up
        proxy.start_request()
        proxy.complete_request(success=True, response_time_ms=100.0)
        pool.add_proxy(proxy)

    strategy = PerformanceBasedStrategy()

    # Act
    proxy = strategy.select(pool)

    # Assert
    assert proxy is not None
    assert proxy.ema_response_time_ms is not None
```

## Performance Benchmarks

### Selection Time

| Strategy | Time (ms) | Complexity | Notes |
|----------|-----------|------------|-------|
| Round-robin | <0.1 | O(1) | Index increment |
| Random | <0.1 | O(1) | Random choice |
| Weighted | <0.5 | O(n) | Weight calculation (cached) |
| Least-used | <0.3 | O(n) | Min search |
| Performance-based | <1.0 | O(n) | Exploration + weighted choice |
| Session | <1.0 | O(1) | Session lookup + fallback |
| Geo-targeted | <2.0 | O(n) | Filtering + secondary selection |
| Cost-aware | <0.5 | O(n) | Inverse cost weights |
| Composite (2 filters) | <5.0 | O(n) | Sum of component times |

### Memory Usage

| Component | Memory per Item |
|-----------|-----------------|
| Strategy instance | <1 KB |
| WeightedStrategy cache | ~100 bytes per proxy |
| SessionManager | ~200 bytes per session |
| PerformanceBasedStrategy | No additional memory |

### Success Criteria

- **SC-004**: Performance-based - 15-25% response time reduction
- **SC-005**: Session persistence - 99.9% same-proxy guarantee
- **SC-006**: Geo-targeting - 100% correct region selection
- **SC-007**: Composite strategy - <5ms total selection time
- **SC-010**: Strategy registration - <1 second load time

## See Also

::::{grid} 2
:gutter: 3

:::{grid-item-card} Async Client Guide
:link: /guides/async-client
:link-type: doc

Using `AsyncProxyRotator` with all strategies, concurrency patterns, and integration with FastAPI/aiohttp.
:::

:::{grid-item-card} Retry & Failover
:link: /guides/retry-failover
:link-type: doc

Circuit breakers, backoff strategies, and intelligent proxy failover that work with all strategies.
:::

:::{grid-item-card} Caching Subsystem
:link: /guides/caching
:link-type: doc

Three-tier caching for proxy persistence and credential encryption.
:::

:::{grid-item-card} Python API Reference
:link: /reference/python-api
:link-type: doc

Complete API docs for `RotationStrategy`, `StrategyRegistry`, `SelectionContext`, and all strategy classes.
:::

:::{grid-item-card} Rotation Strategies Overview
:link: /getting-started/rotation-strategies
:link-type: doc

Introduction to basic rotation strategies and getting started with proxy selection.
:::

:::{grid-item-card} CLI Reference
:link: /guides/cli-reference
:link-type: doc

Set strategies and monitor proxy health from the command line.
:::
::::

**Additional Resources:**
- **Integration Tests:** `tests/integration/test_rotation_strategies.py`
- **Specs:** `.specify/specs/014-retry-failover-logic/`
