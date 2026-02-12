---
title: Getting Started
---

Get ProxyWhirl running in minutes with intelligent proxy rotation for your Python applications.

# Getting Started

## What You'll Build

By the end of this guide you will have a working proxy rotator that:

- Rotates through a pool of HTTP/SOCKS proxies on every request
- Automatically ejects dead proxies and deprioritizes slow ones
- Retries failed requests through alternate proxies with circuit-breaker protection
- Works with both synchronous scripts and async frameworks like FastAPI

```{tip}
If you just need a quick proxy list to get started, ProxyWhirl publishes **free, validated lists** updated every 2 hours at [proxywhirl.com](https://proxywhirl.com/).
```

---

## Installation

::::{tab-set}

:::{tab-item} uv (recommended)
```bash
# Add to an existing project
uv add proxywhirl

# Or install globally
uv pip install proxywhirl
```
:::

:::{tab-item} pip
```bash
pip install proxywhirl
```
:::

:::{tab-item} With all extras
```bash
pip install "proxywhirl[all]"
# Includes: storage, security, js, analytics, mcp
```
:::

:::{tab-item} From source
```bash
git clone https://github.com/wyattowalsh/proxywhirl.git
cd proxywhirl
uv sync
```
:::

::::

```{note}
ProxyWhirl requires **Python 3.9+**. SOCKS proxy support needs the optional `httpx-socks` dependency, which is included in the `[all]` extra.
```

---

## Quick Start

### Basic Usage (sync)

```python
from proxywhirl import ProxyRotator

# Create a rotator with your proxies
rotator = ProxyRotator(proxies=[
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080",
    "socks5://proxy3.example.com:1080",
])

# Make requests -- proxies rotate automatically
response = rotator.get("https://httpbin.org/ip")
print(response.json())  # {"origin": "185.x.x.47"}

# Dead proxies are ejected, slow ones deprioritized
response = rotator.get("https://api.example.com/data")
```

### Async Usage

```python
import asyncio
from proxywhirl import AsyncProxyRotator

async def main():
    rotator = AsyncProxyRotator(proxies=[
        "http://proxy1:8080",
        "http://proxy2:8080",
    ])

    # Concurrent requests with automatic rotation
    tasks = [rotator.get(f"https://api.example.com/{i}") for i in range(10)]
    responses = await asyncio.gather(*tasks)

asyncio.run(main())
```

```{tip}
Use `AsyncProxyRotator` when you need high concurrency (100+ parallel requests) or are integrating with an async framework. For simple scripts and sequential work, `ProxyRotator` is simpler to debug. See [Async Client](../guides/async-client.md) for a deeper comparison.
```

### Context Manager Pattern

Both rotators support context managers for clean resource handling:

```python
from proxywhirl import ProxyRotator

with ProxyRotator(proxies=["http://proxy1:8080"]) as rotator:
    response = rotator.get("https://httpbin.org/ip")
    print(response.json())
# httpx clients are closed automatically on exit
```

### Using Free Proxy Lists

ProxyWhirl publishes free proxy lists updated every 2 hours:

```python
import httpx
from proxywhirl import ProxyRotator

# Fetch the free HTTP proxy list
response = httpx.get("https://proxywhirl.com/proxy-lists/http.txt")
proxies = [f"http://{line}" for line in response.text.strip().split("\n")]

rotator = ProxyRotator(proxies=proxies)
response = rotator.get("https://httpbin.org/ip")
```

### Fetching Proxies Programmatically

For more control, use `ProxyFetcher` with the built-in source catalog:

```python
from proxywhirl import ProxyFetcher, ProxyRotator, RECOMMENDED_SOURCES, deduplicate_proxies

fetcher = ProxyFetcher()
raw_proxies = fetcher.fetch(RECOMMENDED_SOURCES)
unique = deduplicate_proxies(raw_proxies)

rotator = ProxyRotator(proxies=unique)
```

---

## Choosing a Rotation Strategy

ProxyWhirl ships with **9 built-in strategies**. Pass a strategy name string or an instantiated strategy object:

```{list-table}
:header-rows: 1
:widths: 18 22 22 38

* - Strategy
  - Behavior
  - Best For
  - Key Detail
* - ``round-robin``
  - A -> B -> C -> A ...
  - Even distribution
  - Default strategy; deterministic ordering
* - ``random``
  - Shuffle each request
  - Rate-limit avoidance
  - Natural jitter masks access patterns
* - ``weighted``
  - High-scorers get more traffic
  - Load balancing
  - Custom weights or auto-derived from success rate
* - ``least-used``
  - Fewest-requests-first
  - Fair usage across a pool
  - Min-heap tracks request totals
* - ``performance-based``
  - Fastest proxies first
  - Speed optimization
  - EMA response time scoring
* - ``session-persistence``
  - Sticky sessions
  - Stateful APIs / cookies
  - Maps session keys to proxies
* - ``geo-targeted``
  - Route by region
  - Geo-specific scraping
  - Filters by country code
* - ``cost-aware``
  - Cheapest proxies first
  - Budget optimization
  - Considers per-request cost metadata
* - ``composite``
  - Filter + select chains
  - Complex rules
  - Combines multiple strategies in a pipeline
```

```python
# Use a specific strategy by name
rotator = ProxyRotator(
    proxies=proxies,
    strategy="performance-based",
)

# Or pass an instantiated strategy for full control
from proxywhirl.strategies import WeightedStrategy, StrategyConfig

weights = StrategyConfig(
    weights={
        "http://fast-proxy:8080": 0.6,
        "http://slow-proxy:8080": 0.4,
    }
)
rotator = ProxyRotator(
    proxies=proxies,
    strategy=WeightedStrategy(config=weights),
)
```

See [Rotation Strategies](rotation-strategies.md) for recipes, a decision matrix, and advanced configuration.

---

## Monitoring Your Pool

Check pool health at any time:

```python
stats = rotator.get_pool_stats()
print(
    f"Total: {stats['total_proxies']} | "
    f"Healthy: {stats['healthy_proxies']} | "
    f"Avg success: {stats['average_success_rate']:.2%}"
)

# Evict unhealthy proxies during long crawls
rotator.clear_unhealthy_proxies()
```

Or use the CLI for a quick check:

```bash
uv run proxywhirl health
uv run proxywhirl pool list
```

See [CLI Reference](../guides/cli-reference.md) for the full command reference.

---

## Troubleshooting

```{list-table}
:header-rows: 1
:widths: 35 65

* - Symptom
  - Fix
* - ``ModuleNotFoundError: proxywhirl``
  - Run ``uv sync`` (or ``pip install proxywhirl``) to install dependencies.
* - ``ProxyPoolEmptyError``
  - All proxies failed health checks. Add more proxies or check network connectivity.
* - SOCKS proxies not working
  - Install ``httpx-socks``: ``uv pip install httpx-socks`` (included in ``[all]`` extra).
* - Async test errors
  - Ensure ``asyncio_mode = "auto"`` is set in ``pyproject.toml`` under ``[tool.pytest.ini_options]``.
* - Slow proxy validation
  - Increase concurrency: ``proxywhirl fetch --concurrency 2000``.
* - Import errors when running tests
  - Always use ``uv run pytest`` instead of bare ``pytest``.
```

---

## Next Steps

::::{grid} 2
:gutter: 3

:::{grid-item-card} Rotation Strategies
:link: rotation-strategies
:link-type: doc

Configure, compose, and build custom proxy selection logic.
:::

:::{grid-item-card} Async Client Guide
:link: ../guides/async-client
:link-type: doc

High-concurrency patterns with `AsyncProxyRotator`.
:::

:::{grid-item-card} Retry & Failover
:link: ../guides/retry-failover
:link-type: doc

Circuit breakers, backoff policies, and automatic failover.
:::

:::{grid-item-card} CLI Reference
:link: ../guides/cli-reference
:link-type: doc

Manage pools, fetch proxies, and monitor health from the terminal.
:::

:::{grid-item-card} REST API
:link: ../reference/rest-api
:link-type: doc

Operate ProxyWhirl over HTTP with the FastAPI server.
:::

:::{grid-item-card} Automation & CI
:link: ../guides/automation
:link-type: doc

GitHub Actions, Docker deployment, and cron-based proxy refreshing.
:::

::::

---

## For Contributors

```{note}
Development requires `uv` for reproducible environments. All Python commands must use `uv run`.
```

```bash
# Clone and setup
git clone https://github.com/wyattowalsh/proxywhirl.git
cd proxywhirl
uv sync --group dev

# Run tests
uv run pytest tests/ -q

# Lint and type-check
uv run ruff check proxywhirl/ tests/
uv run ty check proxywhirl/
```

See [Automation](../guides/automation.md) for CI/CD integration and the full quality-gate pipeline.

```{toctree}
:maxdepth: 2
:hidden:

rotation-strategies
```
