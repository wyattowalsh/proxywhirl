---
title: Rotation Strategies Quickstart
---

ProxyWhirl ships four stable rotation strategies with shared instrumentation. This quickstart shows how to configure each one, when to use it, and how to capture pool telemetry.

# Rotation Strategies Quickstart

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

## Strategy selector

```{list-table}
:header-rows: 1
:widths: 18 24 22 36

* - Strategy
  - Ideal for
  - Typical latency
  - Highlights
* - ``round-robin``
  - Fair distribution & predictable workloads
  - ~3 µs
  - Ensures ±1 request variance, deterministic ordering
* - ``random``
  - Load testing & rate-limit avoidance
  - ~7 µs
  - Injects natural jitter to mask access patterns
* - ``weighted``
  - Favoring premium or health scorers
  - ~9 µs
  - Rebalances weights from success / failure metadata
* - ``least-used``
  - Evenly balancing long-running jobs
  - ~3 µs
  - Tracks request totals to avoid hotspots
```

## Strategy recipes

```{tab-set}
```{tab-item} Round-robin
```python
rotator = ProxyRotator(proxies=proxies, strategy="round-robin")
rotator.get("https://example.com")
```
```

```{tab-item} Random
```python
rotator = ProxyRotator(proxies=proxies, strategy="random")
rotator.get("https://api.example.com/data")
```
```

```{tab-item} Weighted
```python
from proxywhirl.strategies import WeightedStrategy, StrategyConfig

weights = StrategyConfig(
    weights={
        "http://proxy1.example.com:8080": 0.55,
        "http://proxy2.example.com:8080": 0.3,
        "http://proxy3.example.com:8080": 0.15,
    }
)
rotator = ProxyRotator(proxies=proxies, strategy=WeightedStrategy(config=weights))
```
```

```{tab-item} Least-used
```python
rotator = ProxyRotator(proxies=proxies, strategy="least-used")
rotator.get("https://httpbin.org/ip")
```
```

```

## Observe the pool

```python
stats = rotator.get_pool_stats()
print(
    f"Total: {stats['total_proxies']} | Healthy: {stats['healthy_proxies']} | "
    f"Average success: {stats['average_success_rate']:.2%}"
)
```

Use :func:`ProxyRotator.clear_unhealthy_proxies` to evict failing endpoints during long-running crawls.

## Advanced strategies (preview)

Additional strategies—performance-based scoring, session persistence, geo-targeted filters, and composite pipelines—are implemented in :mod:`proxywhirl.strategies`. They expect a :class:`proxywhirl.models.SelectionContext` and are still stabilizing. Integrate them directly if you need experimental capabilities, and pin to the commit you validate.

```{note}
Follow ``tests/integration/test_rotation_strategies.py`` when enabling experimental strategies; it captures acceptance criteria for the upcoming release.
```
