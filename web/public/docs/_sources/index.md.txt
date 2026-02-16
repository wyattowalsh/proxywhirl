---
title: ProxyWhirl Docs
---

```{raw} html
<section class="sy-hero">
  <h1>ProxyWhirl</h1>
  <p>Production-grade proxy rotation for Python. 9 intelligent strategies, hundreds of built-in sources, circuit breakers, multi-tier caching, and four interfaces -- all in one library.</p>
  <div class="sd-btn-group">
    <a class="sd-btn sd-btn-primary sd-shadow-sm" href="getting-started/index.html">Get Started</a>
    <a class="sd-btn sd-btn-secondary" href="https://proxywhirl.com/" rel="noopener" target="_blank">Free Proxy Lists</a>
    <a class="sd-btn sd-btn-secondary" href="https://github.com/wyattowalsh/proxywhirl" rel="noopener" target="_blank">GitHub</a>
  </div>
</section>
```

# ProxyWhirl Documentation

::::{grid} 1 1 3 3
:gutter: 2

::: {grid-item}
```{card} 9 Rotation Strategies
:class-card: sd-shadow-lg
Round-robin, random, weighted, least-used, performance-based (EMA), session-persistence, geo-targeted, cost-aware, and composite pipelines.
+++
{bdg-primary}`strategies` | {doc}`Quickstart </getting-started/rotation-strategies>` | {doc}`Deep dive </guides/advanced-strategies>`
```
:::

::: {grid-item}
```{card} Runtime Resilience
:class-card: sd-shadow-lg
Circuit breakers with auto-recovery, retry policies with exponential backoff, EMA latency scoring, multi-tier caching (L1/L2/L3), and proxy lifecycle analytics.
+++
{bdg-info}`resilience` | {doc}`Caching </guides/caching>` | {doc}`Retry & Failover </guides/retry-failover>`
```
:::

::: {grid-item}
```{card} Four Interfaces
:class-card: sd-shadow-lg
Python sync/async API, REST service (FastAPI + OpenAPI), CLI with 9 commands (Typer), and MCP server for AI assistants.
+++
{bdg-success}`interfaces` | {doc}`REST </reference/rest-api>` | {doc}`CLI </guides/cli-reference>` | {doc}`MCP </guides/mcp-server>`
```
:::

::::

## Quick Example

::::{tab-set}

:::{tab-item} Python (sync)
```python
from proxywhirl import ProxyWhirl

rotator = ProxyWhirl(proxies=["http://proxy1:8080", "http://proxy2:8080"])
response = rotator.get("https://httpbin.org/ip")
print(response.json())  # {"origin": "185.x.x.47"}
```
See {doc}`/getting-started/index` for full installation and setup.
:::

:::{tab-item} Python (async)
```python
from proxywhirl import AsyncProxyWhirl

async with AsyncProxyWhirl(proxies=proxies) as rotator:
    response = await rotator.get("https://httpbin.org/ip")
    print(response.json())
```
See {doc}`/guides/async-client` for connection pooling, error handling, and concurrency patterns.
:::

:::{tab-item} Auto-Fetch Proxies
```python
from proxywhirl import ProxyFetcher

# Fetch and validate proxies from all built-in sources
fetcher = ProxyFetcher()
proxies = await fetcher.fetch_all(validate=True)
print(f"Found {len(proxies)} working proxies")
```
See {doc}`/reference/python-api` for `ProxyFetcher`, `ProxyValidator`, and parser classes.
:::

:::{tab-item} REST API
```bash
# Start the API server
uv run uvicorn proxywhirl.api:app --reload

# Get proxies
curl http://localhost:8000/api/v1/proxies

# Rotate to next proxy
curl -X POST http://localhost:8000/api/v1/rotate
```
See {doc}`/reference/rest-api` for endpoint reference, authentication, and Docker deployment.
:::

:::{tab-item} CLI
```bash
# Fetch fresh proxies from all built-in sources
proxywhirl fetch --timeout 5

# Validate proxies
proxywhirl validate --protocol http

# Export stats
proxywhirl export --stats-only
```
See {doc}`/guides/cli-reference` for all 9 commands, global options, and output formats.
:::

:::{tab-item} MCP Server
```bash
# Run the MCP server for AI assistants
uv run proxywhirl mcp --transport stdio

# Or with uvx (no install needed)
uvx proxywhirl mcp
```
See {doc}`/guides/mcp-server` for tool definitions, auto-loading, and Claude/GPT integration.
:::

::::

## Rotation Strategies at a Glance

All 9 strategies implement the `RotationStrategy` protocol and can be hot-swapped at runtime via `StrategyRegistry`.

```{list-table}
:header-rows: 1
:widths: 22 18 60

* - Strategy
  - Class
  - Best For
* - Round-Robin
  - `RoundRobinStrategy`
  - Even distribution across all proxies
* - Random
  - `RandomStrategy`
  - Unpredictable rotation patterns
* - Weighted
  - `WeightedStrategy`
  - Favoring reliable proxies by success rate or custom weights
* - Least-Used
  - `LeastUsedStrategy`
  - Load balancing (min-heap, O(log n) selection)
* - Performance-Based
  - `PerformanceBasedStrategy`
  - Lowest latency (EMA scoring with cold-start exploration)
* - Session Persistence
  - `SessionPersistenceStrategy`
  - Sticky sessions with TTL expiration and LRU eviction
* - Geo-Targeted
  - `GeoTargetedStrategy`
  - Region-aware routing by country/region codes
* - Cost-Aware
  - `CostAwareStrategy`
  - Budget optimization (free proxies boosted 10x)
* - Composite
  - `CompositeStrategy`
  - Chaining filters + selectors (e.g., geo-filter then performance-select)
```

{doc}`Strategy overview </getting-started/rotation-strategies>` | {doc}`Advanced strategies guide </guides/advanced-strategies>` | {doc}`Python API reference </reference/python-api>`

## Documentation Sections

```{toctree}
:maxdepth: 2
:hidden:

getting-started/index
guides/index
reference/index
project/index
```

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} Getting Started
:link: getting-started/index
:link-type: doc
:class-card: sd-shadow-sm

Installation, quickstart examples, and your first rotating proxy setup.

- {doc}`Installation & quickstart </getting-started/index>`
- {doc}`Rotation strategies overview </getting-started/rotation-strategies>`
- [Sync vs async decision guide](getting-started/index.md#quick-start)
- [Using free proxy lists](getting-started/index.md#using-free-proxy-lists)
:::

:::{grid-item-card} Guides
:link: guides/index
:link-type: doc
:class-card: sd-shadow-sm

Deep dives: async patterns, advanced strategies, caching, retry/failover, CLI, and MCP server.

- {doc}`Async client patterns </guides/async-client>` -- connection pools, error handling
- {doc}`Advanced strategies </guides/advanced-strategies>` -- EMA scoring, geo-routing, composites
- {doc}`Retry & failover </guides/retry-failover>` -- circuit breakers, backoff policies
- {doc}`Deployment security </guides/deployment-security>` -- Nginx, Caddy, HAProxy configs
:::

:::{grid-item-card} API Reference
:link: reference/index
:link-type: doc
:class-card: sd-shadow-sm

REST API, Python API, configuration, exceptions, caching, and rate limiting.

- {doc}`REST API endpoints </reference/rest-api>` -- OpenAPI, auth, Docker
- {doc}`Python API </reference/python-api>` -- rotators, strategies, fetchers, validators
- {doc}`Configuration reference </reference/configuration>` -- TOML, env vars, discovery
- {doc}`Exception hierarchy </reference/exceptions>` -- error codes, URL redaction
:::

:::{grid-item-card} Project
:link: project/index
:link-type: doc
:class-card: sd-shadow-sm

Contributing, development setup, CI/CD, changelog, and project status.

- [Development environment setup](project/index.md#development-setup)
- [Contributing guidelines](project/index.md#contributing)
- [CI/CD pipelines](project/index.md#cicd-pipelines)
- [Architecture overview](project/index.md#architecture)
:::

::::

## Key Capabilities

::::{grid} 1 1 2 2
:gutter: 2

:::{grid-item}
**9 Rotation Strategies**
- Round-robin, random, weighted, least-used
- Performance-based with EMA latency scoring -- {doc}`/guides/advanced-strategies`
- Session persistence (sticky sessions with TTL)
- Geo-targeted routing by country/region
- Cost-aware selection and composite pipelines
:::

:::{grid-item}
**Resilience Built-In**
- Circuit breakers (`CircuitBreaker`, `AsyncCircuitBreaker`) with auto-recovery -- {doc}`/guides/retry-failover`
- `RetryExecutor` with exponential/linear backoff and jitter
- Health-based proxy ejection via `HealthMonitor`
- Multi-tier caching: L1 in-memory, L2 encrypted disk, L3 SQLite -- {doc}`/guides/caching`
:::

:::{grid-item}
**Four Interfaces**
- Python sync/async API (`ProxyWhirl`, `AsyncProxyWhirl`) -- {doc}`/reference/python-api`
- REST API with OpenAPI docs (FastAPI) -- {doc}`/reference/rest-api`
- CLI with 9 commands (Typer + Rich) -- {doc}`/guides/cli-reference`
- MCP server for AI assistants (Claude, GPT) -- {doc}`/guides/mcp-server`
:::

:::{grid-item}
**Production Ready**
- 2700+ tests: unit, integration, property-based, contract, benchmarks
- <5 us strategy selection overhead
- SQLite persistence with Fernet encryption -- {doc}`/reference/configuration`
- Hundreds of built-in proxy sources, auto-refreshed every 6 hours via CI
:::

::::

## What's New

- **Composite Strategies** -- chain filters and selectors with <5 us overhead via `CompositeStrategy`
- **Cost-Aware Strategy** -- budget-optimize proxy selection with `CostAwareStrategy`
- **MCP Server** -- Model Context Protocol integration for Claude, GPT, and more
- **Free Proxy Lists** -- updated every 6 hours from hundreds of sources at [proxywhirl.com](https://proxywhirl.com/)
- **Rate Limiting** -- token bucket algorithm with per-proxy and global limits via {doc}`/reference/rate-limiting-api`

```{admonition} Looking for proxy lists?
:class: tip
Visit the [ProxyWhirl Dashboard](https://proxywhirl.com/) to browse, filter, and download free proxy lists updated every 6 hours. Or fetch them programmatically: `await ProxyFetcher().fetch_all(validate=True)`
```
