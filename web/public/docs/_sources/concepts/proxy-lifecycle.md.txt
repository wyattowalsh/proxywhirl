---
title: Proxy Lifecycle
---

# Proxy Lifecycle

A proxy in ProxyWhirl goes through a well-defined lifecycle from discovery to ejection. Understanding this flow helps you diagnose issues and tune behavior.

## The Six Stages

```{mermaid}
flowchart LR
    A[Fetch] --> B[Validate]
    B --> C[Enrich]
    C --> D[Rotate]
    D --> E[Monitor]
    E -->|healthy| D
    E -->|degraded| F[Eject]
    F -->|circuit half-open| D
```

### 1. Fetch

Proxies enter the system via `ProxyFetcher`, which pulls from hundreds of built-in sources (`ALL_SOURCES`) or user-defined endpoints.

Each source has a `ProxySourceConfig` specifying URL, expected format, and protocol. Fetching happens concurrently -- the CLI `fetch` command supports `--concurrency` for parallel source downloads.

**Parsers** handle four formats: `JSONParser`, `CSVParser`, `PlainTextParser`, `HTMLTableParser`. For JavaScript-rendered pages, `BrowserRenderer` (Playwright) renders the page before parsing.

### 2. Validate

`ProxyValidator` tests each proxy by making a real HTTP request (default target: `httpbin.org/ip`).

Validation checks:
- **Connectivity**: Can we establish a connection through the proxy?
- **Protocol support**: Does the proxy handle HTTP/HTTPS/SOCKS correctly?
- **Response correctness**: Does the response contain the expected IP?
- **Latency**: How fast does the proxy respond? (recorded for performance-based strategies)

Proxies that fail validation are discarded before entering the pool. This prevents wasting rotation slots on dead proxies.

### 3. Enrich

Validated proxies are enriched with metadata:

- **Geolocation**: Country and region codes via IP geolocation (`geo.py`)
- **Protocol detection**: HTTP, HTTPS, SOCKS4, SOCKS5
- **Anonymity level**: Transparent, anonymous, elite (based on header analysis)
- **Source tracking**: Which source provided this proxy

Enrichment data powers context-aware strategies (geo-targeted, cost-aware).

### 4. Rotate

This is the steady-state. The rotation strategy (`RotationStrategy.select()`) picks the next proxy for each request. The selection considers:

- **Pool health**: Only healthy proxies are candidates
- **Strategy logic**: Round-robin index, random choice, EMA scores, session mappings, etc.
- **Selection context**: Session IDs, target countries, previously-failed proxies

After each request, `record_result()` feeds the outcome back to the strategy for adaptive learning.

### 5. Monitor

Proxies are continuously monitored via two mechanisms:

**Passive monitoring** (every request):
: Each request's success/failure and response time update the proxy's health metrics. The circuit breaker tracks failures in a rolling window.

**Active monitoring** (periodic):
: `HealthMonitor` runs scheduled health checks (default: every 300 seconds) against a configurable target URL. This catches proxies that died between requests.

Health states:
- **HEALTHY**: Responding normally
- **DEGRADED**: Elevated failure rate or latency
- **DEAD**: Circuit breaker open, excluded from rotation

### 6. Eject (and Recover)

When a proxy's circuit breaker opens (failures exceed threshold), the proxy is **ejected** from rotation. No requests are attempted -- `should_attempt_request()` returns `False` immediately.

But ejection isn't permanent. After the circuit breaker timeout, a **half-open test** allows a single request through. If it succeeds, the proxy re-enters rotation (stage 4). If it fails, the timeout resets.

This automatic recovery is what distinguishes ProxyWhirl from simple blacklisting. See {doc}`circuit-breakers` for the full state machine.

## Persistence Across Restarts

The lifecycle state persists via `SQLiteStorage`:

- **Proxy metadata**: URL, protocol, geolocation, source
- **Health history**: Success rate, average latency, last check time
- **Circuit breaker state** (optional): Current state, failure window, next test time

On application restart, proxies load from storage with their last-known health state, avoiding a cold start where all proxies are tested from scratch.

## Data Flow Summary

| Stage | Component | Input | Output |
|-------|-----------|-------|--------|
| Fetch | `ProxyFetcher` + parsers | Source URLs | Raw proxy URLs |
| Validate | `ProxyValidator` | Raw URLs | Validated `Proxy` objects |
| Enrich | `geo.py`, protocol detection | Validated proxies | Enriched proxies with metadata |
| Rotate | `RotationStrategy.select()` | `ProxyPool` + context | Selected proxy |
| Monitor | `HealthMonitor` + circuit breaker | Request outcomes | Health status updates |
| Eject/Recover | `CircuitBreaker` | Failure counts | State transitions |

## Further Reading

- {doc}`/getting-started/index` -- quickstart with fetching and validation
- {doc}`/reference/python-api` -- `ProxyFetcher`, `ProxyValidator`, `HealthMonitor` API
- {doc}`circuit-breakers` -- circuit breaker state machine details
- {doc}`cache-architecture` -- how cache interacts with the lifecycle
