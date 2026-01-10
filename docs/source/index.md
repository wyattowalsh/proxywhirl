---
title: ProxyWhirl Docs
---

```{raw} html
<section class="sy-hero">
  <h1>ProxyWhirl</h1>
  <p>Production-grade proxy rotation for Python, REST, and automation teams. Explore strategies, APIs, and workflows designed to keep high-volume scraping and integration pipelines resilient.</p>
  <div class="sd-btn-group">
    <a class="sd-btn sd-btn-primary sd-shadow-sm" href="getting-started/index.html">Start in 10 minutes</a>
    <a class="sd-btn sd-btn-secondary" href="https://github.com/wyattowalsh/proxywhirl" rel="noopener" target="_blank">View on GitHub</a>
  </div>
</section>
```

# ProxyWhirl Documentation

::::{grid} 1 1 3 3
:gutter: 2

::: {grid-item}
```{card} Intelligent rotation
:class-card: sd-shadow-lg
Choose from 8 strategies: round-robin, random, weighted, least-used, performance-based, session-persistence, geo-targeted, and composite.
```
:::

::: {grid-item}
```{card} Runtime observability
:class-card: sd-shadow-lg
Health metrics, EMA latency, circuit breakers, multi-tier caching, and proxy lifecycle analytics out-of-the-box.
```
:::

::: {grid-item}
```{card} Multi-surface delivery
:class-card: sd-shadow-lg
Use the Python API, REST service, or CLI utilities interchangeably. Hot-swap strategies without downtime.
```
:::

::::

```{tab-set}
```{tab-item} Python client
```python
from proxywhirl import ProxyRotator

rotator = ProxyRotator(proxies=["http://proxy1", "http://proxy2"])
with rotator as pool:
    response = pool.get("https://httpbin.org/ip")
    print(response.json())
```
```

```{tab-item} REST API
```bash
uv run uvicorn proxywhirl.api:app --reload
curl http://localhost:8000/api/v1/proxies
```
```
```

## Navigation

```{toctree}
:maxdepth: 2
:hidden:

getting-started/index
getting-started/rotation-strategies
guides/index
reference/index
project/index
```

- :doc:`getting-started/index` — installation, environment setup, and a validated quickstart script.
- :doc:`guides/index` — advanced rotation recipes, automation runbooks, and CI guidance.
- :doc:`reference/index` — REST resources, configuration tables, and API signatures.
- :doc:`project/index` — release cadence, roadmap milestones, and contribution workflow.

## What's new

- ✅ Intelligent composition of rotation strategies with <5 µs selection overhead.
- ✅ REST API hot-swaps strategy configs with full validation and observability.
- ✅ Algolia DocSearch ready—export credentials before building the docs to enable it.
- ✅ Automated quickstart validator keeps code examples regression-safe.

```{admonition} Looking for the REST payloads?
:class: tip
Jump straight to :doc:`reference/rest-api` for hot-swap requests, performance tuning endpoints, and rate limits.
```
