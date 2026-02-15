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
If you just need a quick proxy list to get started, ProxyWhirl publishes **free, validated lists** updated every 6 hours at [proxywhirl.com](https://proxywhirl.com/).
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

:::{tab-item} Extras
```bash
# Install with specific extras
pip install "proxywhirl[storage]"     # SQLite persistence (sqlmodel)
pip install "proxywhirl[security]"    # Credential encryption (cryptography)
pip install "proxywhirl[js]"          # JS-rendered proxy sources (playwright)
pip install "proxywhirl[analytics]"   # Analytics & ML (pandas, numpy, scikit-learn)
pip install "proxywhirl[mcp]"         # MCP server for AI assistants (Python 3.10+)

# Install everything
pip install "proxywhirl[all]"
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
ProxyWhirl requires **Python 3.9+**. SOCKS proxy support uses `httpx-socks`, which is included in the core dependencies. The `[mcp]` extra requires Python 3.10+.
```

---

## Quick Start

### Basic Usage (sync)

```python
from proxywhirl import ProxyWhirl, Proxy

# Create Proxy objects and pass them to the rotator
proxies = [
    Proxy(url="http://proxy1.example.com:8080"),
    Proxy(url="http://proxy2.example.com:8080"),
    Proxy(url="socks5://proxy3.example.com:1080"),
]

rotator = ProxyWhirl(proxies=proxies)

# Make requests -- proxies rotate automatically
response = rotator.get("https://httpbin.org/ip")
print(response.json())  # {"origin": "185.x.x.47"}

# Dead proxies are ejected, slow ones deprioritized
response = rotator.get("https://api.example.com/data")
```

You can also add proxies from URL strings after construction:

```python
rotator = ProxyWhirl()
rotator.add_proxy("http://proxy1.example.com:8080")
rotator.add_proxy("socks5://proxy2.example.com:1080")
```

### Async Usage

```python
import asyncio
from proxywhirl import AsyncProxyWhirl, Proxy

async def main():
    proxies = [
        Proxy(url="http://proxy1.example.com:8080"),
        Proxy(url="http://proxy2.example.com:8080"),
    ]

    async with AsyncProxyWhirl(proxies=proxies) as rotator:
        # Concurrent requests with automatic rotation
        tasks = [rotator.get(f"https://api.example.com/{i}") for i in range(10)]
        responses = await asyncio.gather(*tasks)

asyncio.run(main())
```

```{tip}
Use `AsyncProxyWhirl` when you need high concurrency (100+ parallel requests) or are integrating with an async framework. For simple scripts and sequential work, `ProxyWhirl` is simpler to debug. See {doc}`/guides/async-client` for a deeper comparison.
```

### Context Manager Pattern

Both rotators support context managers for clean resource handling:

```python
from proxywhirl import ProxyWhirl, Proxy

with ProxyWhirl(proxies=[Proxy(url="http://proxy1.example.com:8080")]) as rotator:
    response = rotator.get("https://httpbin.org/ip")
    print(response.json())
# httpx clients are closed automatically on exit
```

### Authenticated Proxies

Pass credentials directly on the `Proxy` model:

```python
from pydantic import SecretStr
from proxywhirl import ProxyWhirl, Proxy

rotator = ProxyWhirl(proxies=[
    Proxy(
        url="http://proxy.example.com:8080",
        username=SecretStr("user"),
        password=SecretStr("pass"),
    ),
])
response = rotator.get("https://httpbin.org/ip")
```

### Using Free Proxy Lists

ProxyWhirl publishes free proxy lists updated every 6 hours:

```python
import httpx
from proxywhirl import ProxyWhirl, Proxy

# Fetch the free HTTP proxy list
response = httpx.get("https://proxywhirl.com/proxy-lists/http.txt")
proxies = [
    Proxy(url=f"http://{line}")
    for line in response.text.strip().split("\n")
    if line.strip()
]

rotator = ProxyWhirl(proxies=proxies)
response = rotator.get("https://httpbin.org/ip")
```

### Fetching Proxies Programmatically

For more control, use `ProxyFetcher` with the built-in source catalog:

```python
from proxywhirl import ProxyFetcher, ProxyWhirl, RECOMMENDED_SOURCES, deduplicate_proxies

fetcher = ProxyFetcher()
raw_proxies = fetcher.fetch(RECOMMENDED_SOURCES)
unique = deduplicate_proxies(raw_proxies)

rotator = ProxyWhirl(proxies=unique)
```

```{seealso}
ProxyWhirl ships many built-in proxy sources organized by protocol. See {data}`proxywhirl.ALL_SOURCES`, {data}`proxywhirl.ALL_HTTP_SOURCES`, {data}`proxywhirl.ALL_SOCKS4_SOURCES`, and {data}`proxywhirl.ALL_SOCKS5_SOURCES` for the full catalog.
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
# Use a strategy by name (for round-robin, random, weighted, least-used)
rotator = ProxyWhirl(
    proxies=proxies,
    strategy="random",
)

# Or instantiate for full control over parameters
from proxywhirl import PerformanceBasedStrategy

rotator = ProxyWhirl(
    proxies=proxies,
    strategy=PerformanceBasedStrategy(exploration_count=3),
)
```

```{note}
The ``strategy`` string shorthand in `ProxyWhirl` and `AsyncProxyWhirl` supports: ``"round-robin"``, ``"random"``, ``"weighted"``, and ``"least-used"``. For other strategies (``performance-based``, ``session-persistence``, ``geo-targeted``, ``cost-aware``, ``composite``), pass an instantiated strategy object. You can also hot-swap strategies at runtime with {meth}`set_strategy() <proxywhirl.ProxyWhirl.set_strategy>`.
```

See {doc}`rotation-strategies` for detailed recipes, a decision matrix, and configuration for all 9 strategies.

---

## Configuring Retry and Circuit Breakers

ProxyWhirl includes built-in retry logic and circuit breakers to handle failures gracefully:

```python
from proxywhirl import ProxyWhirl, Proxy, RetryPolicy

rotator = ProxyWhirl(
    proxies=[Proxy(url="http://proxy1.example.com:8080")],
    retry_policy=RetryPolicy(
        max_attempts=5,
        base_delay=1.0,
        max_backoff_delay=30.0,
    ),
)

# Requests automatically retry with backoff on failure
response = rotator.get("https://api.example.com/data")
```

See {doc}`/guides/retry-failover` for circuit breaker configuration and advanced failover patterns.

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

See {doc}`/guides/cli-reference` for the full command reference.

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
  - ``httpx-socks`` is included in core dependencies. Run ``uv sync`` to ensure it's installed.
* - Async test errors
  - Ensure ``asyncio_mode = "auto"`` is set in ``pyproject.toml`` under ``[tool.pytest.ini_options]``.
* - Slow proxy validation
  - Increase concurrency: ``proxywhirl fetch --concurrency 2000``.
* - Import errors when running tests
  - Always use ``uv run pytest`` instead of bare ``pytest``.
* - Strings rejected by ``ProxyWhirl(proxies=...)``
  - The ``proxies`` parameter expects ``list[Proxy]`` objects. Use ``Proxy(url="http://...")`` or add strings via ``rotator.add_proxy("http://...")``.
```

---

## Next Steps

::::{grid} 2
:gutter: 3

:::{grid-item-card} Rotation Strategies
:link: rotation-strategies
:link-type: doc

Configure, compose, and build custom proxy selection logic with all 9 built-in strategies.
:::

:::{grid-item-card} Advanced Strategies
:link: /guides/advanced-strategies
:link-type: doc

Deep dive into composite pipelines, EMA tuning, and custom strategy development.
:::

:::{grid-item-card} Async Client Guide
:link: /guides/async-client
:link-type: doc

High-concurrency patterns with `AsyncProxyWhirl`.
:::

:::{grid-item-card} Retry & Failover
:link: /guides/retry-failover
:link-type: doc

Circuit breakers, backoff policies, and automatic failover.
:::

:::{grid-item-card} CLI Reference
:link: /guides/cli-reference
:link-type: doc

Manage pools, fetch proxies, and monitor health from the terminal.
:::

:::{grid-item-card} REST API
:link: /reference/rest-api
:link-type: doc

Operate ProxyWhirl over HTTP with the FastAPI server.
:::

:::{grid-item-card} Caching
:link: /guides/caching
:link-type: doc

Multi-tier caching for proxy data and validation results.
:::

:::{grid-item-card} Automation & CI
:link: /guides/automation
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

See {doc}`/guides/automation` for CI/CD integration and the full quality-gate pipeline.

```{toctree}
:maxdepth: 2
:hidden:

rotation-strategies
```
