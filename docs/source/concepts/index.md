---
title: Concepts
---

# Concepts

Understanding *why* ProxyWhirl works the way it does. These pages explain the design philosophy and architectural decisions behind the library.

```{admonition} Not API docs
:class: tip
These pages explain concepts and rationale. For class/method reference, see {doc}`/reference/index`. For step-by-step guides, see {doc}`/guides/index`.
```

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} Rotation Strategies
:link: rotation-strategies
:link-type: doc
:class-card: sd-shadow-sm

Why 9 strategies? How they compose. The Protocol + Registry design that makes strategies pluggable.

+++
{bdg-primary}`architecture` {bdg-info}`strategies`
:::

:::{grid-item-card} Cache Architecture
:link: cache-architecture
:link-type: doc
:class-card: sd-shadow-sm

The three-tier L1/L2/L3 cache hierarchy -- why each tier exists, how promotion/demotion works, and credential encryption.

+++
{bdg-info}`performance` {bdg-secondary}`encryption`
:::

:::{grid-item-card} Circuit Breakers
:link: circuit-breakers
:link-type: doc
:class-card: sd-shadow-sm

How ProxyWhirl detects, isolates, and recovers from proxy failures using the circuit breaker state machine.

+++
{bdg-danger}`resilience` {bdg-warning}`fault tolerance`
:::

:::{grid-item-card} Proxy Lifecycle
:link: proxy-lifecycle
:link-type: doc
:class-card: sd-shadow-sm

The complete journey of a proxy: fetch, validate, enrich, rotate, monitor, eject. Each stage and its responsibilities.

+++
{bdg-success}`lifecycle` {bdg-info}`data flow`
:::

:::{grid-item-card} Security Model
:link: security-model
:link-type: doc
:class-card: sd-shadow-sm

Credential handling, Fernet encryption, URL redaction, SSRF protection, and the defense-in-depth approach.

+++
{bdg-danger}`security` {bdg-secondary}`encryption`
:::

::::

```{toctree}
:maxdepth: 2
:hidden:

rotation-strategies
cache-architecture
circuit-breakers
proxy-lifecycle
security-model
```
