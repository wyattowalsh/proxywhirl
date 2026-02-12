---
title: ProxyWhirl Docs
---

```{raw} html
<section class="sy-hero">
  <h1>ProxyWhirl</h1>
  <p>Production-grade proxy rotation for Python. Auto-fetching, validation, circuit breakers, and 9 intelligent rotation strategies out of the box.</p>
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
```{card} Intelligent Rotation
:class-card: sd-shadow-lg
9 strategies: round-robin, random, weighted, least-used, performance-based, session-persistence, geo-targeted, composite, and failover chaining.
+++
{bdg-primary}`strategies` | [Quickstart](getting-started/rotation-strategies.md) | [Deep dive](guides/advanced-strategies.md)
```
:::

::: {grid-item}
```{card} Runtime Observability
:class-card: sd-shadow-lg
Health metrics, EMA latency, circuit breakers, multi-tier caching, and proxy lifecycle analytics.
+++
{bdg-info}`resilience` | [Caching](guides/caching.md) | [Retry & Failover](guides/retry-failover.md)
```
:::

::: {grid-item}
```{card} Multi-Surface Delivery
:class-card: sd-shadow-lg
Python API, REST service, CLI utilities, and MCP server for AI assistants -- all interchangeable.
+++
{bdg-success}`interfaces` | [REST](reference/rest-api.md) | [CLI](guides/cli-reference.md) | [MCP](guides/mcp-server.md)
```
:::

::::

## Quick Example

::::{tab-set}

:::{tab-item} Python
```python
from proxywhirl import ProxyRotator

rotator = ProxyRotator(proxies=["http://proxy1:8080", "http://proxy2:8080"])
response = rotator.get("https://httpbin.org/ip")
print(response.json())  # {"origin": "185.x.x.47"}
```
See the [Getting Started guide](getting-started/index.md) for full setup instructions.
:::

:::{tab-item} Async
```python
from proxywhirl import AsyncProxyRotator

async with AsyncProxyRotator(proxies=proxies) as rotator:
    response = await rotator.get("https://httpbin.org/ip")
    print(response.json())
```
See [Async Client](guides/async-client.md) for connection pooling, error handling, and concurrency patterns.
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
See [REST API](reference/rest-api.md) for full endpoint reference including authentication and Docker deployment.
:::

:::{tab-item} CLI
```bash
# Fetch fresh proxies from 64+ sources
proxywhirl fetch --timeout 5

# Export stats
proxywhirl export --stats-only

# Validate proxies
proxywhirl validate --protocol http
```
See [CLI Reference](guides/cli-reference.md) for all 9 commands, global options, and output formats.
:::

:::{tab-item} MCP Server
```bash
# Run the MCP server for AI assistants
uv run proxywhirl mcp --transport stdio

# Or with uvx (no install needed)
uvx proxywhirl mcp
```
See [MCP Server](guides/mcp-server.md) for tool definitions, auto-loading, and Claude/GPT integration.
:::

::::

## Documentation Sections

```{toctree}
:maxdepth: 2
:hidden:

getting-started/index
getting-started/rotation-strategies
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

- [Installation & quickstart](getting-started/index.md)
- [Rotation strategies overview](getting-started/rotation-strategies.md)
- [Sync vs async decision guide](getting-started/index.md#quick-start)
- [Free proxy list usage](getting-started/index.md#using-free-proxy-lists)
:::

:::{grid-item-card} Guides
:link: guides/index
:link-type: doc
:class-card: sd-shadow-sm

Deep dives: async patterns, advanced strategies, caching, retry/failover, CLI, and MCP server.

- [Async client patterns](guides/async-client.md) -- connection pools, error handling
- [Advanced strategies](guides/advanced-strategies.md) -- EMA scoring, geo-routing, composites
- [Retry & failover](guides/retry-failover.md) -- circuit breakers, backoff policies
- [Deployment security](guides/deployment-security.md) -- Nginx, Caddy, HAProxy configs
:::

:::{grid-item-card} API Reference
:link: reference/index
:link-type: doc
:class-card: sd-shadow-sm

REST API, Python API, configuration, exceptions, caching, and rate limiting.

- [REST API endpoints](reference/rest-api.md) -- OpenAPI, auth, Docker
- [Python API](reference/python-api.md) -- rotators, strategies, fetchers, validators
- [Configuration reference](reference/configuration.md) -- TOML, env vars, discovery
- [Exception hierarchy](reference/exceptions.md) -- error codes, URL redaction
:::

:::{grid-item-card} Project
:link: project/index
:link-type: doc
:class-card: sd-shadow-sm

Contributing, development setup, CI/CD, changelog, and project status.

- [Development environment setup](project/index.md#development-setup)
- [Contributing guidelines](project/index.md#contributing)
- [CI/CD pipelines](project/index.md#cicd-pipelines)
- [Changelog highlights](project/index.md#changelog-highlights)
:::

::::

## Key Features

::::{grid} 1 1 2 2
:gutter: 2

:::{grid-item}
**9 Rotation Strategies**
- Round-robin, random, weighted, least-used
- Performance-based (EMA latency scoring) -- [guide](guides/advanced-strategies.md)
- Session persistence (sticky sessions)
- Geo-targeted routing
- Composite pipelines and failover chains
:::

:::{grid-item}
**Resilience Built-In**
- Circuit breakers with automatic recovery -- [guide](guides/retry-failover.md)
- Retry policies with exponential backoff
- Health-based proxy ejection
- Multi-tier caching (L1/L2/L3) -- [guide](guides/caching.md)
:::

:::{grid-item}
**Multiple Interfaces**
- Python sync/async API -- [reference](reference/python-api.md)
- REST API with OpenAPI docs -- [reference](reference/rest-api.md)
- Full CLI with 9 commands -- [guide](guides/cli-reference.md)
- MCP server for AI assistants -- [guide](guides/mcp-server.md)
:::

:::{grid-item}
**Production Ready**
- 2700+ tests, property-based testing
- <5 us strategy selection overhead
- SQLite persistence with encryption -- [config](reference/configuration.md)
- Comprehensive observability
:::

::::

## What's New

- **Free Proxy Lists** -- Updated every 6 hours from 64+ sources
- **Composite Strategies** -- Chain filters and selectors with <5 us overhead
- **MCP Server** -- AI assistant integration for Claude, GPT, and more
- **Interactive Dashboard** -- Browse, filter, and export proxies at [proxywhirl.com](https://proxywhirl.com/)

```{admonition} Looking for proxy lists?
:class: tip
Visit the [ProxyWhirl Dashboard](https://proxywhirl.com/) to browse, filter, and download free proxy lists updated every 6 hours.
```
