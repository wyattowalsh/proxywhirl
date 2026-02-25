# Python API

This page provides a guided tour of ProxyWhirl's Python API. For complete
auto-generated reference documentation with all parameters, return types, and
source links, see the {doc}`full API reference <../autoapi/proxywhirl/index>`.

:::{tip}
For hands-on tutorials, see the {doc}`../guides/index` section. For
async-specific patterns, see {doc}`../guides/async-client`.
:::

---

## Rotators

ProxyWhirl ships two main rotator classes: **ProxyWhirl** (synchronous) and
**AsyncProxyWhirl** (async/await). Both provide HTTP methods that automatically
rotate through a pool of proxies with intelligent failover.

(proxywhirl)=
### Synchronous usage

```python
from proxywhirl import ProxyWhirl, Proxy

with ProxyWhirl() as rotator:
    rotator.add_proxy("http://proxy1.example.com:8080")
    rotator.add_proxy(Proxy(url="http://proxy2.example.com:8080"))

    response = rotator.get("https://httpbin.org/ip")
    response = rotator.post("https://httpbin.org/post", json={"key": "value"})
```

Key capabilities:

- HTTP methods: `get`, `post`, `put`, `delete`, `patch`, `head`, `options`
- Pool management: `add_proxy`, `remove_proxy`, `add_chain`, `remove_chain`
- Hot-swap strategies at runtime with `set_strategy()` (<100 ms)
- Monitoring: `get_pool_stats()`, `get_statistics()`, `get_circuit_breaker_states()`

(asyncproxywhirl)=
### Async usage

```python
from proxywhirl import AsyncProxyWhirl

async with AsyncProxyWhirl() as rotator:
    await rotator.add_proxy("http://proxy1.example.com:8080")
    response = await rotator.get("https://httpbin.org/ip")
```

AsyncProxyWhirl mirrors the synchronous API but all methods are coroutines.

:::{seealso}
- {doc}`../autoapi/proxywhirl/rotator/index` -- full parameter reference
- {doc}`../guides/async-client` -- async usage patterns and best practices
:::

---

## Rotation Strategies

All strategies implement the `RotationStrategy` protocol:

```python
class RotationStrategy(Protocol):
    def select(self, pool: ProxyPool, context: SelectionContext | None = None) -> Proxy: ...
    def record_result(self, proxy: Proxy, success: bool, response_time_ms: float) -> None: ...
```

### Strategy overview

| Strategy | Class | Use case | Complexity |
|----------|-------|----------|------------|
| `round-robin` | `RoundRobinStrategy` | Default sequential rotation | O(1) |
| `random` | `RandomStrategy` | Unpredictable rotation patterns | O(1) |
| `weighted` | `WeightedStrategy` | Custom probability distribution | O(1) cached |
| `least-used` | `LeastUsedStrategy` | Even load distribution | O(n) |
| `performance-based` | `PerformanceBasedStrategy` | Adaptive selection via EMA response times | O(n) |
| `session` | `SessionPersistenceStrategy` | Sticky sessions with TTL | O(1) lookup |
| `geo-targeted` | `GeoTargetedStrategy` | Country/region-based filtering | O(n) filter |
| `cost-aware` | `CostAwareStrategy` | Prefer free/cheap proxies | O(n) |
| `composite` | `CompositeStrategy` | Chain filters + final selector | varies |

### Example: composing strategies

```python
from proxywhirl import CompositeStrategy, GeoTargetedStrategy, PerformanceBasedStrategy

# Filter by geography, then select by performance
strategy = CompositeStrategy(
    filters=[GeoTargetedStrategy()],
    selector=PerformanceBasedStrategy()
)
```

### StrategyRegistry

Register and discover strategies at runtime:

```python
from proxywhirl import StrategyRegistry

registry = StrategyRegistry()
registry.register_strategy("my-strategy", MyStrategy, validate=True)
strategies = registry.list_strategies()
```

(strategystate)=
### StrategyState

Per-strategy mutable metrics including EMA response times, success rates, and
sliding windows. Each strategy maintains its own `StrategyState` instance for
adaptive selection decisions.

See {doc}`../autoapi/proxywhirl/strategies/core/index` for the full API reference.

:::{seealso}
- {doc}`../autoapi/proxywhirl/strategies/index` -- full strategy API reference
- {doc}`../guides/advanced-strategies` -- strategy selection guide with real-world patterns
:::

---

## Models

ProxyWhirl's data layer is built on Pydantic models with strict validation
(`frozen=True`, `extra="forbid"`). Below are the key models; each links to its
full auto-generated documentation.

| Model | Purpose |
|-------|---------|
| `Proxy` | Single proxy server with URL, credentials, health status, performance metrics, geo-location, and TTL |
| `ProxyPool` | Collection of proxies with health filtering, source breakdown, and cleanup |
| `ProxyChain` | Ordered sequence of proxies for multi-hop routing |
| `ProxyCredentials` | Secure credential storage with httpx integration and redacted serialization |
| `ProxyConfiguration` | HTTP settings, connection pool, health checks, logging, storage, and request queuing |
| `SelectionContext` | Context for intelligent proxy selection (session ID, geo target, priority, retry state) |
| `StrategyConfig` | Per-strategy configuration (weights, EMA alpha, session TTL, geo preferences) |
| `Session` | Sticky session tracking with TTL and usage counters |
| `HealthMonitor` | Continuous background health monitoring with automatic eviction |
| `SourceStats` | Per-source fetch statistics and error tracking |
| `StrategyState` | Per-strategy mutable metrics (EMA, success rates, sliding windows) |
| `ProxyMetrics` | Per-proxy performance metrics maintained by strategies |

### Quick example

```python
from proxywhirl import Proxy
from pydantic import SecretStr

proxy = Proxy(
    url="http://proxy.example.com:8080",
    username=SecretStr("user"),
    password=SecretStr("pass"),
    country_code="US",
    tags={"premium", "rotating"},
    cost_per_request=0.01,
    ttl=3600,
)

proxy.start_request()
proxy.complete_request(success=True, response_time_ms=150.0)
print(proxy.success_rate, proxy.is_healthy, proxy.is_expired)
```

### Enumerations

| Enum | Values |
|------|--------|
| `HealthStatus` | `UNKNOWN`, `HEALTHY`, `DEGRADED`, `UNHEALTHY`, `DEAD` |
| `ProxySource` | `USER`, `FETCHED`, `API`, `FILE` |
| `ProxyFormat` | `JSON`, `CSV`, `TSV`, `PLAIN_TEXT`, `HTML_TABLE`, `CUSTOM` |
| `RenderMode` | `STATIC`, `JAVASCRIPT`, `BROWSER`, `AUTO` |
| `ValidationLevel` | `BASIC` (~100 ms), `STANDARD` (~500 ms), `FULL` (~2 s) |
| `BackoffStrategy` | `EXPONENTIAL`, `LINEAR`, `FIXED` |
| `CircuitBreakerState` | `CLOSED`, `OPEN`, `HALF_OPEN` |

(healthmonitor)=
### HealthMonitor

Continuous background health monitoring with automatic eviction of unhealthy
proxies. Runs periodic checks against a configurable target URL and updates
proxy health status.

See {doc}`../autoapi/proxywhirl/models/index` for the full API reference.

(sourcestats)=
### SourceStats

Per-source fetch statistics and error tracking. Records success/failure counts,
latency, and last-fetched timestamps for each configured proxy source.

See {doc}`../autoapi/proxywhirl/models/index` for the full API reference.

:::{seealso}
{doc}`../autoapi/proxywhirl/models/index` -- full model and enum reference
:::

---

## Fetchers and Validators

### ProxyFetcher

Fetch proxies from multiple sources in parallel with automatic parsing and
deduplication.

```python
from proxywhirl import ProxyFetcher, ProxyValidator, ProxySourceConfig

validator = ProxyValidator(timeout=5.0, concurrency=50)
fetcher = ProxyFetcher(sources=[], validator=validator)

fetcher.add_source(ProxySourceConfig(
    url="https://api.example.com/proxies",
    format="json",
    refresh_interval=3600,
))

proxies = await fetcher.fetch_all(validate=True, deduplicate=True)
```

### ProxyValidator

Validate proxy connectivity and anonymity at configurable levels:

- **BASIC** -- format + TCP connectivity
- **STANDARD** -- BASIC + HTTP request test
- **FULL** -- STANDARD + anonymity check (transparent / anonymous / elite)

### Parsers

Four built-in parsers handle common proxy list formats:

| Parser | Format |
|--------|--------|
| `JSONParser` | JSON arrays or objects with key extraction |
| `CSVParser` | CSV with header detection and column mapping |
| `PlainTextParser` | One proxy URL per line (skips comments) |
| `HTMLTableParser` | HTML tables with CSS selector and column mapping |

### Built-in sources

ProxyWhirl ships pre-configured sources ready for immediate use:

```python
from proxywhirl import RECOMMENDED_SOURCES, ProxyFetcher

fetcher = ProxyFetcher(sources=RECOMMENDED_SOURCES)
proxies = await fetcher.fetch_all(validate=True, deduplicate=True)
```

Source collections: `ALL_SOURCES`, `RECOMMENDED_SOURCES`, `ALL_HTTP_SOURCES`,
`ALL_SOCKS4_SOURCES`, `ALL_SOCKS5_SOURCES`, `API_SOURCES`.

:::{seealso}
- {doc}`../autoapi/proxywhirl/fetchers/index` -- full fetcher/parser API reference
- {doc}`../autoapi/proxywhirl/sources/index` -- source definitions
- {doc}`../guides/automation` -- automated fetching with scheduling
:::

---

## Cache

ProxyWhirl provides a multi-tier caching system (L1 memory, L2 JSONL file, L3
SQLite) via `CacheManager`. Features include TTL management, background cleanup,
health-based invalidation, Fernet encryption at rest, and cross-tier
promotion/demotion.

```python
from proxywhirl import CacheManager, CacheConfig

config = CacheConfig(default_ttl_seconds=3600, enable_background_cleanup=True)
manager = CacheManager(config)

manager.put(key, entry)
retrieved = manager.get(key)
stats = manager.get_statistics()
```

(cachehealthstatus)=
### CacheHealthStatus

Health status reporting for the multi-tier cache system. Provides per-tier
availability, hit/miss ratios, and storage utilization metrics.

See {doc}`cache-api` for the full cache API reference.

:::{seealso}
- {doc}`cache-api` -- dedicated cache system reference
- {doc}`../autoapi/proxywhirl/cache/index` -- auto-generated cache API
- {doc}`../guides/caching` -- caching configuration patterns
:::

---

## Circuit Breaker and Retry

### CircuitBreaker

Implements the circuit breaker pattern with three states (CLOSED, OPEN,
HALF_OPEN) and a rolling failure window. Prevents cascading failures by
temporarily excluding unreliable proxies.

(retryexecutor)=
### RetryExecutor and RetryPolicy

`RetryPolicy` configures backoff strategies (exponential, linear, fixed) with
jitter, status code filtering, and total timeout. `RetryExecutor` integrates
retry logic with circuit breakers and metrics collection.

```python
from proxywhirl import RetryPolicy, BackoffStrategy

policy = RetryPolicy(
    max_attempts=3,
    backoff_strategy=BackoffStrategy.EXPONENTIAL,
    base_delay=1.0,
    jitter=True,
)
```

### RetryMetrics

Tracks retry attempts, circuit breaker events, and hourly aggregates for
monitoring. Provides `get_summary()`, `get_timeseries()`, and `get_by_proxy()`
for observability.

(hourlyaggregate)=
### HourlyAggregate

Hourly aggregated retry and circuit breaker statistics. Used by `RetryMetrics`
for time-series monitoring and trend analysis.

See {doc}`../autoapi/proxywhirl/retry/index` for the full API reference.

(circuitbreakerevent)=
### CircuitBreakerEvent

Records individual circuit breaker state transitions (CLOSED, OPEN, HALF_OPEN)
with timestamps and trigger context. Used for observability and debugging.

See {doc}`../autoapi/proxywhirl/retry/index` for the full API reference.

:::{seealso}
- {doc}`../autoapi/proxywhirl/circuit_breaker/index` -- circuit breaker API reference
- {doc}`../autoapi/proxywhirl/retry/index` -- retry API reference
- {doc}`../guides/retry-failover` -- retry and failover patterns
:::

---

(browserrenderer)=
## Browser Renderer

`BrowserRenderer` uses Playwright for proxy sources that require full JavaScript
execution or dynamic content loading.

```python
from proxywhirl import BrowserRenderer

async with BrowserRenderer(headless=True) as renderer:
    html = await renderer.render(
        "https://example.com/proxies",
        wait_for_selector=".proxy-list",
        wait_for_timeout=2000,
    )
```

Supports Chromium, Firefox, and WebKit engines with configurable viewport, user
agent, and navigation wait conditions.

:::{seealso}
{doc}`../autoapi/proxywhirl/browser/index` -- full BrowserRenderer API reference
:::

---

## Utilities

Key utility functions exported from `proxywhirl`:

| Function | Purpose |
|----------|---------|
| `configure_logging(level, format_type, redact_credentials)` | Set up loguru with JSON/text output and automatic credential redaction |
| `encrypt_credentials(plaintext, key)` | Fernet-encrypt a credential string |
| `decrypt_credentials(ciphertext, key)` | Decrypt a Fernet-encrypted credential |
| `generate_encryption_key()` | Generate a base64-encoded Fernet key |
| `is_valid_proxy_url(url)` | Validate proxy URL format (scheme, host, port) |
| `parse_proxy_url(url)` | Parse a proxy URL into protocol, host, port, and credentials |
| `create_proxy_from_url(url, **kwargs)` | Create a `Proxy` instance from a URL string |
| `validate_proxy_model(proxy)` | Return a list of validation errors for a `Proxy` instance |
| `proxy_to_dict(proxy, include_stats)` | Serialize a `Proxy` to a dictionary |
| `deduplicate_proxies(proxies)` | Deduplicate proxy dicts by host:port (keeps first occurrence) |

:::{warning}
Never hardcode encryption keys. Use the `PROXYWHIRL_KEY` environment variable
or the auto-generated key file at `~/.config/proxywhirl/key.enc`.
:::

:::{seealso}
{doc}`../autoapi/proxywhirl/utils/index` -- full utility function reference
:::

---

## Exceptions

All ProxyWhirl exceptions inherit from `ProxyWhirlError`:

```
ProxyWhirlError
├── ProxyValidationError
├── ProxyPoolEmptyError
├── ProxyConnectionError
├── ProxyAuthenticationError
├── ProxyFetchError
├── ProxyStorageError
├── CacheCorruptionError
├── CacheStorageError
├── CacheValidationError
└── RequestQueueFullError
RetryableError          (triggers retry)
NonRetryableError       (skips retry)
RegexTimeoutError       (ReDoS protection)
RegexComplexityError    (ReDoS protection)
```

:::{seealso}
{doc}`exceptions` -- comprehensive exception reference with error handling patterns
:::

---

## See Also

- {doc}`rest-api` -- HTTP REST API documentation
- {doc}`cache-api` -- cache system reference
- {doc}`rate-limiting-api` -- rate limiting reference
- {doc}`configuration` -- configuration options
- {doc}`exceptions` -- exception types and handling
- {doc}`../guides/async-client` -- async usage guide
- {doc}`../guides/advanced-strategies` -- strategy selection guide
- {doc}`../guides/retry-failover` -- retry and failover patterns
- {doc}`../guides/caching` -- caching configuration guide
- {doc}`../guides/deployment-security` -- production deployment guide
