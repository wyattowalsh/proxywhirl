---
title: Reference
---

Authoritative resources for the runtime APIs, configuration knobs, and public data models.

# Reference

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} REST API
:link: rest-api
:link-type: doc

Complete REST endpoint documentation with examples, error codes, and deployment guides.
:::

:::{grid-item-card} Python API
:link: python-api
:link-type: doc

Core classes, strategies, models, and utility functions.
:::

:::{grid-item-card} Configuration
:link: configuration
:link-type: doc

TOML configuration reference with all options and environment variables.
:::

:::{grid-item-card} Exceptions
:link: exceptions
:link-type: doc

Error handling, exception hierarchy, and error codes.
:::

:::{grid-item-card} Cache API
:link: cache-api
:link-type: doc

Multi-tier caching system with L1/L2/L3 storage, TTL management, and health-based invalidation.
:::

:::{grid-item-card} Rate Limiting API
:link: rate-limiting-api
:link-type: doc

Per-proxy and global rate limiting with token bucket algorithm.
:::

::::

```{toctree}
:maxdepth: 2
:hidden:

rest-api
python-api
configuration
exceptions
cache-api
rate-limiting-api
```
