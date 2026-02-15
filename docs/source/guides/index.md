---
title: Guides
---

Deep dives and operational runbooks that extend the quickstart. Each guide mirrors an integration test so you can adopt changes with confidence.

# Guides

## Choosing a Guide

```{admonition} Not sure where to start?
:class: tip
- **Building a scraper or crawler?** Start with {doc}`async-client` and {doc}`advanced-strategies`
- **Deploying to production?** Read {doc}`retry-failover` then {doc}`deployment-security`
- **Automating proxy management?** See {doc}`cli-reference` and {doc}`automation`
- **Integrating with AI tools?** Jump to {doc}`mcp-server`
```

## Client & Concurrency

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} Async Client
:link: async-client
:link-type: doc
:class-card: sd-shadow-sm

Use `AsyncProxyWhirl` for high-concurrency workloads with asyncio.

- [When to use async vs sync](async-client.md#when-to-use-async-vs-sync)
- [Initialization patterns](async-client.md#initialization) -- basic, with proxies, custom strategy
- [Connection pooling & context managers](async-client.md#basic-initialization)
- [Error handling & proxy ejection](async-client.md#with-custom-configuration)

+++
{bdg-primary}`asyncio` {bdg-info}`httpx`
:::

:::{grid-item-card} Advanced Strategies
:link: advanced-strategies
:link-type: doc
:class-card: sd-shadow-sm

Performance-based, session-persistent, geo-targeted, and composite strategies.

- [Performance-based strategy](advanced-strategies.md#performance-based-strategy) -- EMA scoring, warmup periods
- [Session persistence](advanced-strategies.md#session-persistence-strategy) -- sticky sessions, TTL cleanup
- [Geo-targeted routing](advanced-strategies.md#geo-targeted-strategy) -- region-aware filtering
- [Composite pipelines](advanced-strategies.md#composite-strategy) -- filter + select chains

+++
{bdg-primary}`strategies` {bdg-warning}`advanced`
:::

::::

## Resilience & Caching

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} Caching
:link: caching
:link-type: doc
:class-card: sd-shadow-sm

Multi-tier cache architecture (L1/L2/L3) with encryption support.

- [Architecture overview](caching.md#architecture-overview) -- L1 in-memory, L2 encrypted disk, L3 SQLite
- [Tier promotion & demotion](caching.md#tier-promotion--demotion)
- [CacheManager API](caching.md#cachemanager) -- get, set, invalidate, warmup
- [CacheConfig options](caching.md#cacheconfig) -- TTL, max size, encryption keys

+++
{bdg-info}`performance` {bdg-secondary}`encryption`
:::

:::{grid-item-card} Retry & Failover
:link: retry-failover
:link-type: doc
:class-card: sd-shadow-sm

Circuit breakers, retry policies, and automatic proxy failover.

- [Retry vs failover](retry-failover.md#when-to-use-retry-vs-failover) -- same proxy vs different proxy
- [RetryPolicy configuration](retry-failover.md#retrypolicy-configuration) -- attempts, backoff, jitter
- [Backoff strategies](retry-failover.md#backoff-strategies) -- exponential, linear, custom
- [Circuit breaker patterns](retry-failover.md#architecture-overview)

+++
{bdg-danger}`resilience` {bdg-info}`production`
:::

::::

## Operations & Deployment

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} Deployment Security
:link: deployment-security
:link-type: doc
:class-card: sd-shadow-sm

Reverse proxy configuration, X-Forwarded-For security, and production hardening.

- [X-Forwarded-For attack surface](deployment-security.md#x-forwarded-for-security) -- spoofing defense
- [Nginx configuration](deployment-security.md#nginx) -- rate limiting, trusted proxies
- [Caddy configuration](deployment-security.md#caddy) -- automatic TLS
- [HAProxy, Traefik, AWS ALB, GCP](deployment-security.md#haproxy) -- cloud load balancers

+++
{bdg-danger}`security` {bdg-warning}`production`
:::

:::{grid-item-card} CLI Reference
:link: cli-reference
:link-type: doc
:class-card: sd-shadow-sm

Complete command-line interface documentation for all 12 commands.

- [Global options](cli-reference.md#global-options) -- config path, verbosity, output format
- [`request` command](cli-reference.md#request) -- GET/POST with proxy rotation
- [`pool` command](cli-reference.md#pool) -- list, add, remove, test proxies
- [`fetch`, `export`, `cleanup`](cli-reference.md#fetch) -- manage proxy data
- [`tui` dashboard](cli-reference.md#tui) -- interactive terminal UI

+++
{bdg-success}`CLI` {bdg-secondary}`typer`
:::

::::

## Automation & AI

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} Automation
:link: automation
:link-type: doc
:class-card: sd-shadow-sm

CI/CD integration, pre-flight checks, and release automation.

- [Pre-flight checks](automation.md#pre-flight-checks) -- lint, test, type-check gates
- [Smoke tests](automation.md#smoke-tests-for-docs-examples) -- docs example validation
- [Release automation](automation.md#automating-releases) -- tag, build, publish
- [CI stage pipeline](automation.md#ci-stage-summary)

+++
{bdg-secondary}`CI/CD` {bdg-info}`GitHub Actions`
:::

:::{grid-item-card} MCP Server
:link: mcp-server
:link-type: doc
:class-card: sd-shadow-sm

Model Context Protocol server for AI assistant integration.

- [Quick start](mcp-server.md#quick-start) -- install, run, auto-load proxies
- [Available actions](mcp-server.md#available-actions) -- list, rotate, validate, stats
- [Claude Desktop integration](mcp-server.md#running-the-server) -- stdio transport
- [CLI options](mcp-server.md#cli-options) -- transport, host, port, database path

+++
{bdg-primary}`AI` {bdg-success}`MCP`
:::

::::

---

**Related:** {doc}`/getting-started/index` for installation | {doc}`/reference/index` for API specs | {doc}`/project/index` for contributing

```{toctree}
:maxdepth: 2
:hidden:

async-client
advanced-strategies
caching
retry-failover
deployment-security
cli-reference
automation
mcp-server
```
