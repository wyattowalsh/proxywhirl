---
title: Reference
---

Authoritative resources for the runtime APIs, configuration knobs, and public data models.

# Reference

## Quick Lookup

::::{tab-set}

:::{tab-item} By Interface
| Interface | Entry Point | Docs |
|-----------|------------|------|
| Python sync | `ProxyWhirl` | {doc}`Python API <python-api>` |
| Python async | `AsyncProxyWhirl` | {doc}`Python API <python-api>` |
| REST API | `GET/POST /api/v1/*` | {doc}`REST API <rest-api>` |
| CLI | `proxywhirl <command>` | {doc}`CLI Reference <../guides/cli-reference>` |
| MCP | `proxywhirl mcp` | {doc}`MCP Server <../guides/mcp-server>` |
:::

:::{tab-item} By Task
| Task | Where to Look |
|------|--------------|
| Configure rotation strategy | {doc}`Configuration <configuration>` -- `[rotation]` section |
| Handle errors | {doc}`Exceptions <exceptions>` -- error codes and hierarchy |
| Set up caching | {doc}`Cache API <cache-api>` -- `CacheConfig`, tier options |
| Rate limit requests | {doc}`Rate Limiting API <rate-limiting-api>` -- token bucket setup |
| Set up authentication | {doc}`REST API <rest-api>` -- API key configuration |
| Tune retry behavior | {doc}`Retry & Failover <../guides/retry-failover>` -- `RetryPolicy` options |
:::

:::{tab-item} By Class
| Class | Module | Docs |
|-------|--------|------|
| `ProxyWhirl` | `proxywhirl.rotator` | [Sync rotator](python-api.md#proxyrotator) |
| `AsyncProxyWhirl` | `proxywhirl.rotator` | [Async rotator](python-api.md#asyncproxyrotator) |
| `ProxyFetcher` | `proxywhirl.fetchers` | [Fetcher](python-api.md#proxyfetcher) |
| `ProxyValidator` | `proxywhirl.fetchers` | [Validator](python-api.md#proxyvalidator) |
| `CacheManager` | `proxywhirl.cache` | {doc}`Cache API <cache-api>` |
| `RateLimiter` | `proxywhirl.rate_limiting` | {doc}`Rate Limiting API <rate-limiting-api>` |
| `SyncRateLimiter` | `proxywhirl.rate_limiting` | [Rate Limiting API](rate-limiting-api.md#syncratelimiter) |
| `AsyncRateLimiter` | `proxywhirl.rate_limiting` | [Rate Limiting API](rate-limiting-api.md#asyncratelimiter) |
| `CircuitBreaker` | `proxywhirl.circuit_breaker` | {doc}`Retry & Failover <../guides/retry-failover>` |
| `RetryExecutor` | `proxywhirl.retry` | [Python API](python-api.md#retryexecutor) |
| `StrategyRegistry` | `proxywhirl.strategies` | [Python API](python-api.md#strategyregistry) |
| `StrategyState` | `proxywhirl.strategies` | [Python API](python-api.md#strategystate) |
| `BrowserRenderer` | `proxywhirl.browser` | [Browser](python-api.md#browserrenderer) |
| `CacheHealthStatus` | `proxywhirl` | [Python API](python-api.md#cachehealthstatus) |
| `HealthMonitor` | `proxywhirl.models` | [Python API](python-api.md#healthmonitor) |
| `SourceStats` | `proxywhirl.models` | [Python API](python-api.md#sourcestats) |
| `HourlyAggregate` | `proxywhirl.retry` | [Python API](python-api.md#hourlyaggregate) |
| `CircuitBreakerEvent` | `proxywhirl.retry` | [Python API](python-api.md#circuitbreakerevent) |
:::

::::

## API Surfaces

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} REST API
:link: rest-api
:link-type: doc
:class-card: sd-shadow-sm

Complete REST endpoint documentation with examples, error codes, and deployment guides.

- [Starting the server](rest-api.md#starting-the-api-server) -- dev mode, production, Docker
- [Authentication](rest-api.md#authentication) -- API key setup
- [Rotation endpoints](rest-api.md#rotation-strategy-configuration) -- GET/PUT config, strategy context
- [Pool management](rest-api.md#pool-management) -- CRUD proxies, health checks
- [Proxied requests](rest-api.md#proxied-requests) -- POST requests through rotating proxies

+++
{bdg-success}`FastAPI` {bdg-info}`OpenAPI`
:::

:::{grid-item-card} Python API
:link: python-api
:link-type: doc
:class-card: sd-shadow-sm

Core classes, strategies, models, and utility functions.

- [ProxyWhirl](python-api.md#proxyrotator) -- sync client with context manager
- [AsyncProxyWhirl](python-api.md#asyncproxyrotator) -- async client, connection pooling
- [Rotation strategies](python-api.md#rotation-strategies) -- all 9 strategy classes
- [ProxyFetcher & Validator](python-api.md#proxyfetcher) -- fetch, validate, enrich
- [BrowserRenderer](python-api.md#browserrenderer) -- Playwright JS-rendered sources

+++
{bdg-primary}`Python` {bdg-secondary}`httpx`
:::

::::

## Configuration & Error Handling

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} Configuration
:link: configuration
:link-type: doc
:class-card: sd-shadow-sm

TOML configuration reference with all options and environment variables.

- [Configuration discovery](configuration.md#configuration-discovery) -- auto-detect paths
- [TOML format](configuration.md#toml-configuration-format) -- complete annotated example
- [File locations](configuration.md#file-locations) -- pyproject.toml, standalone, explicit path
- [Environment variables](configuration.md#complete-configuration-example) -- `PROXYWHIRL_*` overrides

+++
{bdg-secondary}`TOML` {bdg-info}`env vars`
:::

:::{grid-item-card} Exceptions
:link: exceptions
:link-type: doc
:class-card: sd-shadow-sm

Error handling, exception hierarchy, and error codes.

- [Exception hierarchy](exceptions.md#exception-hierarchy) -- tree of all exception types
- [Error codes](exceptions.md#proxyerrorcode-enum) -- `ProxyErrorCode` enum values
- [URL redaction](exceptions.md#utility-functions) -- `redact_url()` for safe logging
- [Per-exception reference](exceptions.md#exception-reference) -- when raised, attributes, resolution

+++
{bdg-danger}`errors` {bdg-warning}`security`
:::

::::

## Subsystem APIs

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} Cache API
:link: cache-api
:link-type: doc
:class-card: sd-shadow-sm

Multi-tier caching system with L1/L2/L3 storage, TTL management, and health-based invalidation.

- [Data models](cache-api.md#data-models) -- `CacheEntry`, `CacheConfig`, `CacheStatistics`
- [CacheEntry fields](cache-api.md#cacheentry) -- key, value, TTL, tier, health status
- [CacheConfig options](cache-api.md#cacheconfig) -- per-tier settings, encryption
- [CacheTierConfig](cache-api.md#cachetierconfig) -- max size, TTL, promotion rules

+++
{bdg-info}`L1/L2/L3` {bdg-secondary}`encryption`
:::

:::{grid-item-card} Rate Limiting API
:link: rate-limiting-api
:link-type: doc
:class-card: sd-shadow-sm

Per-proxy and global rate limiting with token bucket algorithm.

- [RateLimiter](rate-limiting-api.md#ratelimiter-legacy) -- constructor, global vs per-proxy limits
- [SyncRateLimiter](rate-limiting-api.md#syncratelimiter) -- sync per-proxy configuration
- [AsyncRateLimiter](rate-limiting-api.md#asyncratelimiter) -- async token bucket check
- [Overview](rate-limiting-api.md#overview) -- architecture and algorithm details

+++
{bdg-warning}`rate limit` {bdg-info}`token bucket`
:::

::::

---

**Related:** {doc}`Guides <../guides/index>` for usage guides | {doc}`Getting Started <../getting-started/index>` for quickstart | {doc}`Project <../project/index>` for contributing

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
