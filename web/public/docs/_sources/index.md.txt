---
title: ProxyWhirl Docs
---

```{raw} html
<section class="sy-hero">
  <h1>ProxyWhirl</h1>
  <p>Production-grade proxy rotation for Python. Auto-fetching, validation, circuit breakers, and 8 intelligent rotation strategies out of the box.</p>
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
```{card} 🔄 Intelligent Rotation
:class-card: sd-shadow-lg
8 strategies: round-robin, random, weighted, least-used, performance-based, session-persistence, geo-targeted, and composite.
```
:::

::: {grid-item}
```{card} 📊 Runtime Observability
:class-card: sd-shadow-lg
Health metrics, EMA latency, circuit breakers, multi-tier caching, and proxy lifecycle analytics.
```
:::

::: {grid-item}
```{card} 🚀 Multi-Surface Delivery
:class-card: sd-shadow-lg
Python API, REST service, CLI utilities, and MCP server for AI assistants—all interchangeable.
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
:::

:::{tab-item} Async
```python
from proxywhirl import AsyncProxyRotator

async with AsyncProxyRotator(proxies=proxies) as rotator:
    response = await rotator.get("https://httpbin.org/ip")
    print(response.json())
```
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

:::{grid-item-card} 🚀 Getting Started
:link: getting-started/index
:link-type: doc

Installation, quickstart examples, and your first rotating proxy setup.
:::

:::{grid-item-card} �� Guides
:link: guides/index
:link-type: doc

Deep dives: async patterns, advanced strategies, caching, retry/failover, CLI, and MCP server.
:::

:::{grid-item-card} 📖 API Reference
:link: reference/index
:link-type: doc

REST API, Python API, configuration, exceptions, caching, and rate limiting.
:::

:::{grid-item-card} 📋 Project
:link: project/index
:link-type: doc

Roadmap, changelog, contributing guidelines, and project status.
:::

::::

## Key Features

::::{grid} 1 1 2 2
:gutter: 2

:::{grid-item}
**8 Rotation Strategies**
- Round-robin, random, weighted, least-used
- Performance-based (EMA latency scoring)
- Session persistence (sticky sessions)
- Geo-targeted routing
- Composite pipelines
:::

:::{grid-item}
**Resilience Built-In**
- Circuit breakers with automatic recovery
- Retry policies with exponential backoff
- Health-based proxy ejection
- Multi-tier caching (L1/L2/L3)
:::

:::{grid-item}
**Multiple Interfaces**
- Python sync/async API
- REST API with OpenAPI docs
- Full CLI with 9 commands
- MCP server for AI assistants
:::

:::{grid-item}
**Production Ready**
- 2700+ tests, property-based testing
- <5 µs strategy selection overhead
- SQLite persistence with encryption
- Comprehensive observability
:::

::::

## What's New

- ✅ **Free Proxy Lists** — Updated every 6 hours from 64+ sources
- ✅ **Composite Strategies** — Chain filters and selectors with <5 µs overhead
- ✅ **MCP Server** — AI assistant integration for Claude, GPT, and more
- ✅ **Interactive Dashboard** — Browse, filter, and export proxies at [proxywhirl.com](https://proxywhirl.com/)

```{admonition} Looking for proxy lists?
:class: tip
Visit the [ProxyWhirl Dashboard](https://proxywhirl.com/) to browse, filter, and download free proxy lists updated every 6 hours.
```
