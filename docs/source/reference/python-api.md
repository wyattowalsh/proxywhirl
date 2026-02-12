# Python API Reference

Complete reference for ProxyWhirl's Python API, covering all public classes, functions, and types.

:::{tip}
For guided tutorials on using these APIs, see the [Guides](../guides/index.md) section. For async-specific patterns, see [Async Client](../guides/async-client.md).
:::

```{doctest}
>>> import proxywhirl
>>> proxywhirl.__name__
'proxywhirl'
```

## Core Classes

### ProxyRotator

Main synchronous proxy rotation class with automatic failover.

Provides HTTP methods (GET, POST, PUT, DELETE, PATCH) that automatically rotate through a pool of proxies with intelligent failover on connection errors.

```python
from proxywhirl import ProxyRotator, Proxy

# Initialize with default round-robin strategy
rotator = ProxyRotator()

# Initialize with specific strategy
rotator = ProxyRotator(
    proxies=[proxy1, proxy2],
    strategy="performance-based",  # or strategy instance
    config=ProxyConfiguration(),
    retry_policy=RetryPolicy(),
    rate_limiter=None
)

# Add proxies
rotator.add_proxy("http://proxy1.example.com:8080")
rotator.add_proxy(Proxy(url="http://proxy2.example.com:8080"))

# Make HTTP requests with automatic rotation
response = rotator.get("https://httpbin.org/ip")
response = rotator.post("https://httpbin.org/post", json={"key": "value"})

# Context manager usage
with ProxyRotator() as rotator:
    rotator.add_proxy("http://proxy.example.com:8080")
    response = rotator.get("https://httpbin.org/ip")
```

:::{note}
The constructor accepts a limited set of strategy names. To use advanced strategies like `"performance-based"`, `"session"`, or `"geo-targeted"`, pass a strategy instance directly or call `set_strategy()` after construction.
:::

**Constructor Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `proxies` | `list[Proxy] \| None` | `None` | Initial list of Proxy instances |
| `strategy` | `RotationStrategy \| str \| None` | `RoundRobinStrategy()` | Rotation strategy instance or name (`"round-robin"`, `"random"`, `"weighted"`, `"least-used"`) |
| `config` | `ProxyConfiguration \| None` | `ProxyConfiguration()` | Configuration settings (timeout, SSL verification, etc.) |
| `retry_policy` | `RetryPolicy \| None` | `RetryPolicy()` | Retry policy configuration |
| `rate_limiter` | `SyncRateLimiter \| None` | `None` | Synchronous rate limiter for controlling request rates |

:::{important}
The `rate_limiter` parameter accepts a `SyncRateLimiter` (not `RateLimiter`). For async rotators, use `AsyncRateLimiter`. See [Rate Limiting API](rate-limiting-api.md) for details.
:::

**HTTP Methods:**

- `get(url: str, **kwargs) -> httpx.Response` - Make GET request
- `post(url: str, **kwargs) -> httpx.Response` - Make POST request
- `put(url: str, **kwargs) -> httpx.Response` - Make PUT request
- `delete(url: str, **kwargs) -> httpx.Response` - Make DELETE request
- `patch(url: str, **kwargs) -> httpx.Response` - Make PATCH request
- `head(url: str, **kwargs) -> httpx.Response` - Make HEAD request
- `options(url: str, **kwargs) -> httpx.Response` - Make OPTIONS request

**Pool Management:**

- `add_proxy(proxy: Union[Proxy, str])` - Add a proxy to the pool
- `remove_proxy(proxy_id: str)` - Remove a proxy from the pool by ID
- `add_chain(chain: ProxyChain)` - Add a proxy chain for multi-hop routing
- `remove_chain(chain_name: str) -> bool` - Remove a proxy chain by name
- `get_chains() -> list[ProxyChain]` - Get all registered proxy chains

**Strategy Management:**

- `set_strategy(strategy: Union[RotationStrategy, str], atomic: bool = True)` - Hot-swap the rotation strategy without restarting (<100ms). Supports all strategy names: `"round-robin"`, `"random"`, `"weighted"`, `"least-used"`, `"performance-based"`, `"session"`, `"geo-targeted"`. See [Advanced Strategies](../guides/advanced-strategies.md).

**Statistics & Monitoring:**

- `get_pool_stats() -> dict` - Get proxy pool statistics (total, healthy, unhealthy, dead proxies)
- `get_statistics() -> dict` - Get comprehensive statistics including source breakdown
- `clear_unhealthy_proxies() -> int` - Remove unhealthy/dead proxies from pool
- `get_circuit_breaker_states() -> dict[str, CircuitBreaker]` - Get circuit breaker states for all proxies
- `reset_circuit_breaker(proxy_id: str)` - Manually reset a circuit breaker to CLOSED state
- `get_retry_metrics() -> RetryMetrics` - Get retry metrics
- `get_queue_stats() -> dict` - Get request queue statistics (if enabled)
- `clear_queue() -> int` - Clear all pending requests from queue

---

### AsyncProxyRotator

Async proxy rotator with automatic failover and intelligent rotation.

Provides async HTTP methods that automatically rotate through a pool of proxies with the same functionality as ProxyRotator but using async/await.

:::{seealso}
For detailed async usage patterns and best practices, see [Async Client](../guides/async-client.md).
:::

```python
from proxywhirl import AsyncProxyRotator

async with AsyncProxyRotator() as rotator:
    await rotator.add_proxy("http://proxy1.example.com:8080")
    await rotator.add_proxy("http://proxy2.example.com:8080")

    response = await rotator.get("https://httpbin.org/ip")
    print(response.json())
```

**Constructor Parameters:** Same as ProxyRotator

**HTTP Methods:** Same as ProxyRotator but all async (prefixed with `await`)

- `async get(url: str, **kwargs) -> httpx.Response`
- `async post(url: str, **kwargs) -> httpx.Response`
- `async put(url: str, **kwargs) -> httpx.Response`
- `async delete(url: str, **kwargs) -> httpx.Response`
- `async patch(url: str, **kwargs) -> httpx.Response`
- `async head(url: str, **kwargs) -> httpx.Response`
- `async options(url: str, **kwargs) -> httpx.Response`

**Pool Management:**

- `async add_proxy(proxy: Union[Proxy, str])` - Add proxy to pool
- `async remove_proxy(proxy_id: str)` - Remove proxy from pool
- `async get_proxy() -> Proxy` - Get the next proxy using rotation strategy
- `async clear_unhealthy_proxies() -> int` - Remove unhealthy/dead proxies

**Statistics:** Same synchronous methods as ProxyRotator

---

### ProxyFetcher

Fetch proxies from various sources with automatic parsing and validation.

:::{seealso}
For automated proxy fetching with scheduling, see [Automation](../guides/automation.md).
:::

```python
from proxywhirl import ProxyFetcher, ProxyValidator
from proxywhirl.fetchers import ProxySourceConfig
from proxywhirl.models import RenderMode

# Initialize with validator
validator = ProxyValidator(timeout=5.0, concurrency=50)
fetcher = ProxyFetcher(sources=[], validator=validator)

# Add sources
fetcher.add_source(ProxySourceConfig(
    url="https://api.example.com/proxies",
    format="json",
    refresh_interval=3600,
    render_mode=RenderMode.STATIC,
    trusted=False  # Set True to skip validation for pre-validated sources
))

# Fetch all proxies with validation
proxies = await fetcher.fetch_all(validate=True, deduplicate=True)

# Start periodic refresh (runs in background)
await fetcher.start_periodic_refresh(
    callback=lambda proxies: print(f"Fetched {len(proxies)} proxies"),
    interval=3600
)
```

**Constructor Parameters:**

- `sources` (list[ProxySourceConfig], optional): List of proxy source configurations
- `validator` (ProxyValidator, optional): Validator instance for fetched proxies

**Methods:**

- `add_source(source: ProxySourceConfig)` - Add a proxy source
- `remove_source(url: str)` - Remove source by URL
- `async fetch_from_source(source: ProxySourceConfig) -> list[dict]` - Fetch from single source (with retries)
- `async fetch_all(validate: bool = True, deduplicate: bool = True) -> list[dict]` - Fetch from all sources in parallel
- `async start_periodic_refresh(callback=None, interval=None)` - Start automatic refresh loop

---

### ProxyValidator

Validate proxy connectivity and anonymity with configurable validation levels.

```python
from proxywhirl import ProxyValidator
from proxywhirl.models import ValidationLevel

validator = ProxyValidator(
    timeout=5.0,
    test_url="http://httpbin.org/ip",
    level=ValidationLevel.STANDARD,  # BASIC, STANDARD, or FULL
    concurrency=50  # Max concurrent validations
)

# Validate single proxy (TCP + HTTP test)
proxy = {"url": "http://proxy.example.com:8080"}
is_valid = await validator.validate(proxy)

# Validate batch with concurrency control
proxies = [{"url": f"http://proxy{i}.com:8080"} for i in range(100)]
working_proxies = await validator.validate_batch(proxies)

# Check anonymity level
anonymity = await validator.check_anonymity("http://proxy.example.com:8080")
print(anonymity)  # "transparent", "anonymous", "elite", or "unknown"
```

**Constructor Parameters:**

- `timeout` (float): Connection timeout in seconds (default: 5.0)
- `test_url` (str): URL to use for connectivity testing (default: "http://httpbin.org/ip")
- `level` (ValidationLevel): Validation strictness level
  - `BASIC`: Format + TCP connectivity (~100ms)
  - `STANDARD`: BASIC + HTTP request test (~500ms)
  - `FULL`: STANDARD + Anonymity check (~2s)
- `concurrency` (int): Maximum number of concurrent validations (default: 50)

**Methods:**

- `async validate(proxy: dict) -> bool` - Validate single proxy (TCP pre-check + HTTP test)
- `async validate_batch(proxies: list[dict]) -> list[dict]` - Validate multiple proxies with concurrency control
- `async check_anonymity(proxy_url: str) -> Optional[str]` - Check proxy anonymity level
  - Returns: "transparent" (leaks IP), "anonymous" (hides IP but reveals proxy usage), "elite" (fully anonymous), or "unknown"

---

### BrowserRenderer

Browser-based page renderer using Playwright for JavaScript execution.

Useful for proxy sources that require full browser JavaScript execution or dynamic content loading.

```python
from proxywhirl import BrowserRenderer

# Context manager usage (recommended)
async with BrowserRenderer(headless=True) as renderer:
    html = await renderer.render(
        "https://example.com/proxies",
        wait_for_selector=".proxy-list",  # Wait for this element
        wait_for_timeout=2000  # Additional 2s wait
    )

# Manual usage
renderer = BrowserRenderer(
    headless=True,
    browser_type="chromium",  # or "firefox", "webkit"
    timeout=30000,
    wait_until="load",  # or "domcontentloaded", "networkidle"
    user_agent="Custom User Agent",
    viewport={"width": 1920, "height": 1080}
)
await renderer.start()
html = await renderer.render("https://example.com/proxies")
await renderer.close()
```

**Constructor Parameters:**

- `headless` (bool): Run browser in headless mode (default: True)
- `browser_type` (Literal["chromium", "firefox", "webkit"]): Browser engine (default: "chromium")
- `timeout` (int): Page load timeout in milliseconds (default: 30000)
- `wait_until` (Literal["load", "domcontentloaded", "networkidle"]): When to consider navigation complete (default: "load")
- `user_agent` (Optional[str]): Custom user agent string
- `viewport` (Optional[dict]): Custom viewport size, e.g. `{"width": 1280, "height": 720}`

**Methods:**

- `async start()` - Start the browser instance (idempotent)
- `async render(url: str, wait_for_selector: Optional[str] = None, wait_for_timeout: Optional[int] = None) -> str` - Render page and return HTML content
- `async close()` - Close the browser instance (safe to call multiple times)

---

## Rotation Strategies

:::{seealso}
For a guided walkthrough of all strategies with real-world usage patterns, see [Advanced Strategies](../guides/advanced-strategies.md).
:::

All strategies implement the `RotationStrategy` protocol with two core methods:

- `select(pool: ProxyPool, context: Optional[SelectionContext] = None) -> Proxy`
- `record_result(proxy: Proxy, success: bool, response_time_ms: float)`

### RoundRobinStrategy

Select proxies in sequential order with wraparound (circular rotation).

```{doctest}
>>> from proxywhirl.strategies import RoundRobinStrategy
>>> strategy = RoundRobinStrategy()
>>> hasattr(strategy, 'select')
True
```

```python
from proxywhirl import RoundRobinStrategy, ProxyRotator

strategy = RoundRobinStrategy()
rotator = ProxyRotator(strategy=strategy)
# Or use string name
rotator = ProxyRotator(strategy="round-robin")
```

**Thread Safety:** Uses `threading.Lock` for atomic index increment, preventing proxy skipping or duplicate selection in multi-threaded environments.

**Performance:** O(1) selection time.

:::{seealso}
For strategy comparison and selection guidance, see [Advanced Strategies](../guides/advanced-strategies.md).
:::

---

### RandomStrategy

Randomly select proxies from the pool of healthy proxies.

```python
from proxywhirl import RandomStrategy

strategy = RandomStrategy()
```

**Thread Safety:** Uses Python's thread-safe `random` module (GIL-protected).

**Use Cases:** Unpredictable rotation patterns, avoiding sequential detection.

---

### WeightedStrategy

Select proxies based on custom weights or success rates using weighted random selection.

```python
from proxywhirl import WeightedStrategy, StrategyConfig

strategy = WeightedStrategy()
strategy.configure(StrategyConfig(
    weights={
        "http://proxy1.com:8080": 0.7,  # 70% selection probability
        "http://proxy2.com:8080": 0.3   # 30% selection probability
    }
))
```

**Features:**

- Custom weights via `StrategyConfig.weights` (proxy URL → weight mapping)
- Fallback to success_rate-based weights if no custom weights provided
- Minimum weight (0.1) ensures all proxies have selection chance
- Weight caching to avoid O(n) recalculation on every selection
- Automatically normalizes weights to sum to 1.0

**Performance:** O(1) selection (when cache valid), O(n) when recalculating weights.

---

### LeastUsedStrategy

Select proxy with fewest started requests for load balancing.

```python
from proxywhirl import LeastUsedStrategy

strategy = LeastUsedStrategy()
```

**Selection Criteria:** Minimum `requests_started` counter (tracks in-flight requests).

**Use Cases:** Even load distribution, preventing proxy overload.

---

### PerformanceBasedStrategy

Performance-based selection using EMA (Exponential Moving Average) response times.

Faster proxies receive higher selection weights. Includes cold-start exploration for new proxies.

```python
from proxywhirl import PerformanceBasedStrategy, StrategyConfig

strategy = PerformanceBasedStrategy(exploration_count=5)
strategy.configure(StrategyConfig(
    ema_alpha=0.2  # Smoothing factor (0-1, higher = more weight to recent values)
))
```

**Constructor Parameters:**

- `exploration_count` (int): Minimum trials for new proxies before performance-based selection applies (default: 5)

**Features:**

- Adaptive selection based on EMA response times
- Inverse weighting: lower EMA = higher selection probability
- Cold-start handling: new proxies get exploration trials before being evaluated
- Configurable EMA alpha (smoothing factor)

**Performance:** O(n) selection (must scan for exploration vs. exploitation split).

---

### SessionPersistenceStrategy

Maintain consistent proxy assignment per session ID (sticky sessions).

Ensures that all requests within a session use the same proxy unless the proxy becomes unavailable.

```python
from proxywhirl import SessionPersistenceStrategy, SelectionContext, StrategyConfig

strategy = SessionPersistenceStrategy(
    max_sessions=10000,  # LRU eviction threshold
    auto_cleanup_threshold=100  # Auto-cleanup every 100 operations
)
strategy.configure(StrategyConfig(
    session_stickiness_duration_seconds=3600  # 1 hour TTL
))

# Use with context
context = SelectionContext(session_id="user-123")
proxy = strategy.select(pool, context)
```

**Constructor Parameters:**

- `max_sessions` (int): Maximum active sessions before LRU eviction (default: 10000)
- `auto_cleanup_threshold` (int): Number of operations between auto-cleanups (default: 100)

**Features:**

- Session-to-proxy binding with configurable TTL
- Automatic failover when assigned proxy becomes unhealthy
- Thread-safe session management with `threading.RLock`
- LRU eviction when max_sessions reached
- 99.9% same-proxy guarantee per session (SC-005)
- Automatic expiration and cleanup

**Methods:**

- `close_session(session_id: str)` - Explicitly close a session
- `cleanup_expired_sessions() -> int` - Remove expired sessions
- `get_session_stats() -> dict` - Get session statistics

**Performance:** O(1) session lookup.

---

### GeoTargetedStrategy

Select proxies based on geographical location (country or region filtering).

```python
from proxywhirl import GeoTargetedStrategy, SelectionContext, StrategyConfig

strategy = GeoTargetedStrategy()
strategy.configure(StrategyConfig(
    geo_fallback_enabled=True,  # Fallback to any proxy if no matches
    geo_secondary_strategy="round_robin"  # Strategy for filtered selection
))

# Target specific country (ISO 3166-1 alpha-2)
context = SelectionContext(target_country="US")
proxy = strategy.select(pool, context)

# Target specific region
context = SelectionContext(target_region="Europe")
proxy = strategy.select(pool, context)
```

**Features:**

- Country-based filtering using ISO 3166-1 alpha-2 codes (e.g., "US", "GB", "FR")
- Region-based filtering (custom region names)
- Country takes precedence over region when both specified
- Configurable fallback behavior (use any proxy vs. raise error)
- Secondary strategy for selection from filtered proxies

**Success Criteria:** 100% correct region selection when available (SC-006).

**Performance:** O(n) filtering + O(1) or O(n) secondary selection.

---

### CostAwareStrategy

Cost-aware proxy selection prioritizing free/cheap proxies.

Uses weighted random selection based on inverse cost - lower cost proxies are more likely to be selected.

```python
from proxywhirl import CostAwareStrategy, StrategyConfig

strategy = CostAwareStrategy(max_cost_per_request=0.5)
strategy.configure(StrategyConfig(
    metadata={
        "max_cost_per_request": 0.5,  # Filter out proxies exceeding this cost
        "free_proxy_boost": 10.0  # Weight multiplier for free proxies
    }
))
```

**Constructor Parameters:**

- `max_cost_per_request` (Optional[float]): Maximum acceptable cost per request (filters out expensive proxies)

**Features:**

- Free proxies (cost_per_request = 0.0) are heavily favored (10x weight by default)
- Paid proxies selected based on inverse cost weighting: weight = 1 / (cost + 0.001)
- Configurable cost threshold to filter out expensive proxies
- Fallback to any proxy when no low-cost options available

---

### CompositeStrategy

Composite strategy applying filters then selector (filter + select pattern).

```python
from proxywhirl import CompositeStrategy, GeoTargetedStrategy, PerformanceBasedStrategy

# Filter by geography, then select by performance
strategy = CompositeStrategy(
    filters=[GeoTargetedStrategy()],
    selector=PerformanceBasedStrategy()
)

# Or use configuration
strategy = CompositeStrategy.from_config({
    "filters": ["geo-targeted"],
    "selector": "performance-based"
})

# Use with context
context = SelectionContext(target_country="US")
proxy = strategy.select(pool, context)
```

**Constructor Parameters:**

- `filters` (Optional[list[RotationStrategy]]): List of filtering strategies applied sequentially
- `selector` (Optional[RotationStrategy]): Final selection strategy to choose from filtered pool

**Features:**

- Sequential filter application (each filter narrows the pool)
- Final selector chooses from filtered set
- Configurable filter chain
- Target: <5ms total selection time (SC-007)

**Methods:**

- `configure(config: StrategyConfig)` - Configure all component strategies
- `@classmethod from_config(config: dict) -> CompositeStrategy` - Create from configuration dictionary

**Thread Safety:** Thread-safe if all component strategies are thread-safe.

---

### StrategyRegistry

Singleton registry for custom rotation strategies with thread-safe registration.

```python
from proxywhirl import StrategyRegistry

registry = StrategyRegistry()

# Register custom strategy
class MyStrategy:
    def select(self, pool, context=None):
        return pool.get_all_proxies()[0]

    def record_result(self, proxy, success, response_time_ms):
        pass

registry.register_strategy("my-strategy", MyStrategy, validate=True)

# Retrieve and use
StrategyClass = registry.get_strategy("my-strategy")
strategy = StrategyClass()

# List all strategies
strategies = registry.list_strategies()

# Unregister
registry.unregister_strategy("my-strategy")
```

**Methods:**

- `register_strategy(name: str, strategy_class: type, validate: bool = True)` - Register a custom strategy
  - Validates strategy implements `RotationStrategy` protocol if `validate=True`
  - Allows re-registration (replacement)
  - Target: <1s load time (SC-010)
- `get_strategy(name: str) -> type` - Retrieve strategy class by name (raises `KeyError` if not found)
- `list_strategies() -> list[str]` - List all registered strategy names
- `unregister_strategy(name: str)` - Remove strategy from registry
- `@classmethod reset()` - Reset singleton instance (testing only)

**Thread Safety:** Uses `threading.RLock` for thread-safe operations.

---

## Data Models

### Proxy

Represents a single proxy server with connection details, performance metrics, and metadata.

```{doctest}
>>> from proxywhirl import Proxy
>>> from proxywhirl.models import HealthStatus
>>> proxy = Proxy(url="http://example.com:8080")
>>> proxy.protocol
'http'
>>> proxy.health_status
<HealthStatus.UNKNOWN: 'unknown'>
```

```python
from proxywhirl import Proxy
from pydantic import SecretStr

proxy = Proxy(
    url="http://proxy.example.com:8080",
    protocol="http",
    username=SecretStr("user"),
    password=SecretStr("pass"),
    country_code="US",
    region="California",
    tags={"premium", "rotating"},
    cost_per_request=0.01,
    ttl=3600  # Expire after 1 hour
)

# Properties
success_rate = proxy.success_rate  # Calculate success rate (0.0-1.0)
is_healthy = proxy.is_healthy  # Check if proxy is healthy
is_expired = proxy.is_expired  # Check if TTL expired

# Track request lifecycle
proxy.start_request()  # Increment requests_started, requests_active
proxy.complete_request(success=True, response_time_ms=150.0)  # Updates metrics, EMA
```

**Core Fields:**

- `id` (UUID): Unique identifier (auto-generated)
- `url` (str): Proxy URL (scheme://host:port)
- `protocol` (Optional[Literal["http", "https", "socks4", "socks5"]]): Protocol type (auto-extracted from URL)
- `username`, `password` (Optional[SecretStr]): Authentication credentials (secure storage)
- `allow_local` (bool): Allow localhost/internal IPs (default: False for production)

**Health & Status:**

- `health_status` (HealthStatus): Current health state (UNKNOWN, HEALTHY, DEGRADED, UNHEALTHY, DEAD)
- `last_success_at`, `last_failure_at` (Optional[datetime]): Timestamp of last success/failure
- `consecutive_failures` (int): Consecutive failure count
- `consecutive_successes` (int): Consecutive success count (for health monitoring)

**Request Tracking:**

- `requests_started` (int): Total requests initiated
- `requests_completed` (int): Total requests finished
- `requests_active` (int): Currently in-flight requests
- `total_requests`, `total_successes`, `total_failures` (int): Legacy counters

**Performance Metrics:**

- `average_response_time_ms` (Optional[float]): Simple average response time
- `ema_response_time_ms` (Optional[float]): EMA response time (adaptive)
- `ema_alpha` (float): EMA smoothing factor (default: 0.2)
- `latency_ms` (Optional[float]): Last measured latency

**Geo-Location:**

- `country_code` (Optional[str]): ISO 3166-1 alpha-2 code (e.g., "US", "GB")
- `region` (Optional[str]): Region/state within country

**Health Monitoring (Feature 006):**

- `last_health_check` (Optional[datetime]): Last health check timestamp
- `recovery_attempt` (int): Current recovery attempt count
- `next_check_time` (Optional[datetime]): Scheduled next health check
- `last_health_error` (Optional[str]): Last health check error message
- `total_checks`, `total_health_failures` (int): Health check counters

**Metadata:**

- `tags` (set[str]): Custom tags for categorization
- `source` (ProxySource): Origin type (USER, FETCHED, API, FILE)
- `source_url` (Optional[HttpUrl]): Source URL if fetched
- `metadata` (dict[str, Any]): Custom metadata
- `created_at`, `updated_at` (datetime): Timestamps

**TTL & Expiration:**

- `ttl` (Optional[int]): Time-to-live in seconds
- `expires_at` (Optional[datetime]): Absolute expiration timestamp (auto-set from TTL)

**Cost:**

- `cost_per_request` (Optional[float]): Cost per request (0.0 = free, higher = more expensive)

**Methods:**

- `start_request()` - Mark proxy as handling a request (increments `requests_started`, `requests_active`)
- `complete_request(success: bool, response_time_ms: float)` - Complete request and update metrics (decrements `requests_active`, updates EMA, records success/failure)
- `@property success_rate -> float` - Calculate success rate (0.0-1.0)
- `@property is_healthy -> bool` - Check if proxy is healthy (HEALTHY or UNKNOWN status)
- `@property is_expired -> bool` - Check if proxy has expired based on TTL

**Validators:**

- URL scheme validation (http, https, socks4, socks5)
- Port range validation (1-65535)
- Localhost/internal IP blocking (unless `allow_local=True`)
- Credential consistency (username and password must both be present or both absent)

---

### ProxyPool

Collection of proxies with health filtering and statistics.

```python
from proxywhirl import ProxyPool, Proxy

pool = ProxyPool(name="my_pool", proxies=[proxy1, proxy2])

# Add/remove proxies
pool.add_proxy(proxy3)
pool.remove_proxy(proxy1.id)

# Get proxies
all_proxies = pool.get_all_proxies()
healthy_proxies = pool.get_healthy_proxies()  # Only HEALTHY, UNKNOWN, DEGRADED
proxy_by_id = pool.get_proxy_by_id(proxy.id)

# Statistics
stats = pool.get_source_breakdown()  # Count by source (USER, FETCHED, etc.)
size = pool.size  # Total proxy count

# Cleanup
removed_count = pool.clear_unhealthy()  # Remove UNHEALTHY and DEAD proxies
```

**Fields:**

- `name` (str): Pool name/identifier
- `proxies` (list[Proxy]): List of proxies in pool

**Methods:**

- `add_proxy(proxy: Proxy)` - Add proxy to pool
- `remove_proxy(proxy_id: UUID)` - Remove proxy by ID
- `get_proxy_by_id(proxy_id: UUID) -> Optional[Proxy]` - Get proxy by ID
- `get_healthy_proxies() -> list[Proxy]` - Get all healthy proxies (HEALTHY, UNKNOWN, DEGRADED)
- `get_all_proxies() -> list[Proxy]` - Get all proxies regardless of health
- `clear_unhealthy() -> int` - Remove UNHEALTHY and DEAD proxies, return count removed
- `get_source_breakdown() -> dict[ProxySource, int]` - Count proxies by source type
- `@property size -> int` - Get total proxy count

---

### ProxyChain

Sequence of proxies for multi-hop routing (chain/tunnel pattern).

```python
from proxywhirl import ProxyChain, Proxy

chain = ProxyChain(
    name="secure_chain",
    proxies=[proxy1, proxy2, proxy3],
    description="Three-hop proxy chain for anonymity"
)

# Access chain properties
entry_proxy = chain.entry_proxy  # First proxy (client connects to this)
exit_proxy = chain.exit_proxy  # Last proxy (final hop before destination)
length = chain.chain_length  # Number of proxies in chain
urls = chain.get_chain_urls()  # List of all proxy URLs
```

**Fields:**

- `name` (Optional[str]): Chain name/identifier
- `proxies` (list[Proxy]): Ordered list of proxies in chain (entry → exit)
- `description` (Optional[str]): Human-readable description

**Methods:**

- `@property entry_proxy -> Proxy` - Get first proxy in chain (entry point)
- `@property exit_proxy -> Proxy` - Get last proxy in chain (exit point)
- `@property chain_length -> int` - Get number of proxies in chain
- `get_chain_urls() -> list[str]` - Get all proxy URLs in order

**Note:** Full CONNECT tunneling implementation is not yet supported. Currently, only the entry proxy is used for routing, with chain metadata stored for future multi-hop implementation.

---

### ProxyCredentials

Secure credential storage for proxy authentication with httpx integration.

```python
from proxywhirl import ProxyCredentials
from pydantic import SecretStr

creds = ProxyCredentials(
    username=SecretStr("user"),
    password=SecretStr("pass"),
    auth_type="basic",  # or "digest", "bearer"
    additional_headers={"X-Custom": "value"}
)

# Convert to httpx auth
httpx_auth = creds.to_httpx_auth()

# Export (redacted or revealed)
dict_redacted = creds.to_dict(reveal=False)  # {"username": "**********", ...}
dict_revealed = creds.to_dict(reveal=True)  # {"username": "user", ...}
```

**Fields:**

- `username` (SecretStr): Username (secure storage)
- `password` (SecretStr): Password (secure storage)
- `auth_type` (Literal["basic", "digest", "bearer"]): Authentication type (default: "basic")
- `additional_headers` (dict[str, str]): Additional HTTP headers for authentication

**Methods:**

- `to_httpx_auth() -> httpx.BasicAuth` - Convert to httpx BasicAuth object
- `to_dict(reveal: bool = False) -> dict` - Serialize credentials (redacted by default)

---

### ProxyConfiguration

Configuration settings for ProxyRotator and AsyncProxyRotator.

```python
from proxywhirl.models import ProxyConfiguration

config = ProxyConfiguration(
    # HTTP settings
    timeout=30.0,
    verify_ssl=True,
    follow_redirects=True,

    # Connection pool settings
    pool_connections=100,
    pool_max_keepalive=20,

    # Logging settings
    log_level="INFO",
    log_format="json",  # or "text"
    log_redact_credentials=True,

    # Request queuing (optional)
    queue_enabled=False,
    queue_size=100
)
```

**HTTP Settings:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `timeout` | `int` | `30` | Request timeout in seconds |
| `max_retries` | `int` | `3` | Maximum retry attempts |
| `verify_ssl` | `bool` | `True` | Verify SSL certificates |
| `follow_redirects` | `bool` | `True` | Follow HTTP redirects |

**Connection Pool:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `pool_connections` | `int` | `10` | Maximum connections per proxy |
| `pool_max_keepalive` | `int` | `20` | Maximum keepalive connections |
| `pool_timeout` | `int` | `30` | Pool timeout in seconds |

**Health Checks:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `health_check_enabled` | `bool` | `True` | Enable health checking |
| `health_check_interval_seconds` | `int` | `300` | Seconds between checks |
| `health_check_url` | `HttpUrl` | `http://httpbin.org/ip` | URL for health checks |
| `health_check_timeout` | `int` | `10` | Health check timeout (seconds) |

**Logging:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `log_level` | `str` | `"INFO"` | Log level |
| `log_format` | `Literal["json", "text"]` | `"json"` | Log output format |
| `log_redact_credentials` | `bool` | `True` | Redact credentials in logs |

**Storage:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `storage_backend` | `Literal["memory", "sqlite", "file"]` | `"memory"` | Storage backend type |
| `storage_path` | `Path \| None` | `None` | Storage file path |

**Request Queuing:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `queue_enabled` | `bool` | `False` | Enable request queuing when rate limited |
| `queue_size` | `int` | `100` | Maximum queue size (1-10000) |

:::{seealso}
For TOML file configuration, see [Configuration](configuration.md).
:::

---

### SelectionContext

Context information for proxy selection decisions, used by strategies to make intelligent selections.

```python
from proxywhirl import SelectionContext

context = SelectionContext(
    # Session tracking
    session_id="user-123",

    # Target information
    target_url="https://example.com/api",
    target_country="US",  # ISO 3166-1 alpha-2
    target_region="California",

    # Request metadata
    request_priority=5,  # 0-10, higher = more important
    timeout_ms=5000,

    # Retry context
    failed_proxy_ids=["proxy-1", "proxy-2"],  # Proxies that have failed
    attempt_number=2,  # Current attempt (1-indexed)

    # Custom metadata
    metadata={"api_key": "secret", "user_tier": "premium"}
)
```

**Fields:**

- `session_id` (Optional[str]): Unique session identifier for sticky sessions
- `target_url` (Optional[str]): The URL being accessed (for domain-based routing)
- `target_country` (Optional[str]): Preferred country for geo-targeting (ISO 3166-1 alpha-2)
- `target_region` (Optional[str]): Preferred region for geo-targeting
- `request_priority` (Optional[int]): Priority level (0-10, higher = more important)
- `timeout_ms` (Optional[float]): Request timeout in milliseconds
- `failed_proxy_ids` (list[str]): List of proxy IDs that have failed for this request
- `attempt_number` (int): Current attempt number (1-indexed, default: 1)
- `metadata` (dict[str, Any]): Additional context for custom selection logic

**Config:** Allows extra fields for extensibility.

---

### StrategyConfig

Configuration for rotation strategies with support for all strategy types.

```python
from proxywhirl import StrategyConfig

config = StrategyConfig(
    # Weighted strategy
    weights={"http://proxy1.com:8080": 0.7, "http://proxy2.com:8080": 0.3},

    # Performance-based strategy
    ema_alpha=0.2,  # EMA smoothing factor (0-1)
    exploration_count=5,  # Min trials for new proxies

    # Session persistence strategy
    session_stickiness_duration_seconds=3600,  # 1 hour TTL

    # Geo-targeted strategy
    preferred_countries=["US", "GB"],
    preferred_regions=["North America", "Europe"],
    geo_fallback_enabled=True,
    geo_secondary_strategy="round_robin",

    # Fallback strategy
    fallback_strategy="random",

    # Performance thresholds
    max_response_time_ms=5000.0,
    min_success_rate=0.8,

    # Sliding window
    window_duration_seconds=3600,  # 1 hour

    # Generic metadata
    metadata={"custom_key": "custom_value"}
)
```

**Fields:**

- `weights` (Optional[dict[str, float]]): Proxy weights keyed by URL for weighted strategies
- `ema_alpha` (float): EMA smoothing factor (0-1, default: 0.2)
- `session_stickiness_duration_seconds` (int): Session TTL in seconds (default: 300)
- `preferred_countries` (Optional[list[str]]): Preferred country codes (ISO 3166-1 alpha-2)
- `preferred_regions` (Optional[list[str]]): Preferred region names
- `geo_fallback_enabled` (bool): Fallback to any proxy when target unavailable (default: True)
- `geo_secondary_strategy` (str): Secondary strategy for geo-filtered selection (default: "round_robin")
- `fallback_strategy` (Optional[str]): Strategy when primary fails (default: "random")
- `max_response_time_ms` (Optional[float]): Maximum acceptable response time
- `min_success_rate` (Optional[float]): Minimum acceptable success rate (0-1)
- `window_duration_seconds` (int): Sliding window duration for counter resets (default: 3600)
- `exploration_count` (int): Min trials for new proxies in performance-based strategy (default: 5)
- `metadata` (dict[str, Any]): Additional custom metadata for strategy-specific configuration

---

### Session

Session tracking for sticky proxy assignments with TTL and usage tracking.

```python
from proxywhirl.models import Session
from datetime import datetime, timezone, timedelta

session = Session(
    session_id="user-123",
    proxy_id="proxy-uuid-here",
    created_at=datetime.now(timezone.utc),
    expires_at=datetime.now(timezone.utc) + timedelta(seconds=300),
    last_used_at=datetime.now(timezone.utc),
    request_count=0
)

# Check expiration
is_expired = session.is_expired()  # True if current time >= expires_at

# Update last usage
session.touch()  # Updates last_used_at and increments request_count
```

**Fields:**

- `session_id` (str): Unique session identifier
- `proxy_id` (str): ID of the proxy assigned to this session
- `created_at` (datetime): When the session was created
- `expires_at` (datetime): When the session expires (TTL)
- `last_used_at` (datetime): Last time this session was used
- `request_count` (int): Number of requests made in this session (default: 0)

**Methods:**

- `is_expired() -> bool` - Check if session has expired (current time >= expires_at)
- `touch()` - Update last_used_at timestamp and increment request_count

---

## Cache Components

:::{seealso}
For detailed cache system documentation, see [Cache API](cache-api.md). For cache configuration patterns, see [Caching](../guides/caching.md).
:::

### CacheManager

Multi-tier caching system with L1 (memory), L2 (JSONL file), L3 (SQLite).

```python
from proxywhirl import CacheManager, CacheConfig, CacheEntry, CacheTierConfig

config = CacheConfig(
    l1_config=CacheTierConfig(enabled=True, max_entries=1000),
    l2_config=CacheTierConfig(enabled=True, max_entries=10000),
    l3_config=CacheTierConfig(enabled=True, max_entries=100000),
    enable_background_cleanup=True,
    health_check_invalidation=True,
    failure_threshold=3
)

manager = CacheManager(config)

# Store and retrieve entries
entry = CacheEntry(...)
manager.put(entry.key, entry)
retrieved = manager.get(entry.key)

# Invalidation
manager.invalidate_by_health(entry.key)
manager.delete(entry.key)

# Statistics
stats = manager.get_statistics()

# Export/import
manager.export_to_file("proxies.jsonl")
manager.warm_from_file("proxies.jsonl", ttl_override=3600)
```

**Note:** CacheManager is currently a minimal stub implementation. Full functionality is planned for future releases.

---

### CacheConfig

Configuration for CacheManager with tier settings, TTL, and encryption.

```python
from proxywhirl import CacheConfig, CacheTierConfig
from pydantic import SecretStr

config = CacheConfig(
    # Tier configuration
    l1_config=CacheTierConfig(enabled=True, max_entries=1000, eviction_policy="lru"),
    l2_config=CacheTierConfig(enabled=True, max_entries=10000, eviction_policy="lru"),
    l3_config=CacheTierConfig(enabled=True, max_entries=None, eviction_policy="lru"),

    # Storage paths
    l2_cache_dir="~/.cache/proxywhirl",
    l3_database_path="~/.cache/proxywhirl/cache.db",

    # TTL configuration
    default_ttl_seconds=3600,  # 1 hour default
    enable_background_cleanup=True,
    cleanup_interval_seconds=60,
    per_source_ttl={"premium_source": 7200},  # Per-source TTL overrides

    # Health integration
    health_check_invalidation=True,
    failure_threshold=3,

    # Encryption
    encryption_key=SecretStr("your-fernet-key-here"),

    # Performance
    enable_statistics=True,
    statistics_interval=5
)
```

**Tier Configuration:**

- `l1_config` (CacheTierConfig): L1 (memory) tier configuration
- `l2_config` (CacheTierConfig): L2 (JSONL file) tier configuration
- `l3_config` (CacheTierConfig): L3 (SQLite) tier configuration

**Storage Paths:**

- `l2_cache_dir` (str): Directory for L2 JSONL file cache (default: ".cache/proxies")
- `l3_database_path` (str): SQLite database path for L3 (default: ".cache/db/proxywhirl.db")

**TTL Configuration:**

- `default_ttl_seconds` (int): Default TTL for cached proxies (default: 3600)
- `ttl_cleanup_interval` (int): Background cleanup interval (default: 60)
- `enable_background_cleanup` (bool): Enable background TTL cleanup thread (default: False)
- `cleanup_interval_seconds` (int): Interval between cleanup runs (default: 60)
- `per_source_ttl` (dict[str, int]): Per-source TTL overrides

**Encryption:**

- `encryption_key` (Optional[SecretStr]): Fernet encryption key (from env: `PROXYWHIRL_CACHE_ENCRYPTION_KEY`)

**Health Integration:**

- `health_check_invalidation` (bool): Auto-invalidate on health check failure (default: True)
- `failure_threshold` (int): Failures before health invalidation (default: 3)

**Performance:**

- `enable_statistics` (bool): Track cache statistics (default: True)
- `statistics_interval` (int): Stats aggregation interval in seconds (default: 5)

---

### CacheEntry

Individual cache entry with TTL, health tracking, and secure credential storage.

```python
from proxywhirl import CacheEntry
from proxywhirl.cache_models import HealthStatus
from datetime import datetime, timezone, timedelta
from pydantic import SecretStr

entry = CacheEntry(
    key="cache_key_123",
    proxy_url="http://proxy.example.com:8080",
    username=SecretStr("user"),
    password=SecretStr("pass"),
    source="premium_source",
    fetch_time=datetime.now(timezone.utc),
    last_accessed=datetime.now(timezone.utc),
    access_count=0,
    ttl_seconds=3600,
    expires_at=datetime.now(timezone.utc) + timedelta(seconds=3600),
    health_status=HealthStatus.HEALTHY,
    failure_count=0
)

# Check expiration
is_expired = entry.is_expired  # Property
is_healthy = entry.is_healthy  # Property
```

**Fields:**

- `key` (str): Unique cache key (proxy URL hash)
- `proxy_url` (str): Full proxy URL (scheme://host:port)
- `username`, `password` (Optional[SecretStr]): Proxy credentials (encrypted at rest)
- `source` (str): Proxy source identifier
- `fetch_time` (datetime): When proxy was fetched
- `last_accessed` (datetime): Last cache access time
- `access_count` (int): Number of cache hits (default: 0)
- `ttl_seconds` (int): Time-to-live in seconds
- `expires_at` (datetime): Absolute expiration time
- `health_status` (HealthStatus): Current health status (UNKNOWN, HEALTHY, DEGRADED, UNHEALTHY, DEAD)
- `failure_count` (int): Consecutive failures (default: 0)

**Health Monitoring Fields (Feature 006):**

- `last_health_check` (Optional[datetime]): Last health check timestamp
- `consecutive_health_failures` (int): Consecutive health check failures
- `consecutive_health_successes` (int): Consecutive successful health checks
- `recovery_attempt` (int): Current recovery attempt count
- `next_check_time` (Optional[datetime]): Scheduled next health check
- `last_health_error` (Optional[str]): Last health check error message
- `total_health_checks` (int): Total health checks performed
- `total_health_check_failures` (int): Total health check failures

**Properties:**

- `@property is_expired -> bool` - Check if entry has expired based on TTL
- `@property is_healthy -> bool` - Check if proxy is healthy (health_status == HEALTHY)

---

### CacheStatistics

Aggregate cache statistics across all tiers with hit rates and promotions.

```python
from proxywhirl import CacheManager

manager = CacheManager(config)
stats = manager.get_statistics()

# L1 (memory) tier stats
print(f"L1 hits: {stats.l1_stats.hits}")
print(f"L1 misses: {stats.l1_stats.misses}")
print(f"L1 hit rate: {stats.l1_stats.hit_rate}")  # Computed property
print(f"L1 current size: {stats.l1_stats.current_size}")
print(f"L1 evictions: {stats.l1_stats.total_evictions}")  # Computed property

# L2 (file) tier stats
print(f"L2 hit rate: {stats.l2_stats.hit_rate}")

# L3 (SQLite) tier stats
print(f"L3 hit rate: {stats.l3_stats.hit_rate}")

# Cross-tier operations
print(f"Promotions (L3→L2→L1): {stats.promotions}")
print(f"Demotions (L1→L2→L3): {stats.demotions}")

# Overall stats
print(f"Overall hit rate: {stats.overall_hit_rate}")  # Computed property
print(f"Total cached entries: {stats.total_size}")  # Computed property

# Degradation tracking
print(f"L1 degraded: {stats.l1_degraded}")
print(f"L2 degraded: {stats.l2_degraded}")
print(f"L3 degraded: {stats.l3_degraded}")
```

**Fields:**

- `l1_stats` (TierStatistics): L1 tier statistics
- `l2_stats` (TierStatistics): L2 tier statistics
- `l3_stats` (TierStatistics): L3 tier statistics
- `promotions` (int): Cross-tier promotions (L3→L2→L1)
- `demotions` (int): Cross-tier demotions (L1→L2→L3)
- `l1_degraded`, `l2_degraded`, `l3_degraded` (bool): Tier degradation flags

**Computed Properties:**

- `@property overall_hit_rate -> float` - Overall hit rate across all tiers (0.0-1.0)
- `@property total_size -> int` - Total cached entries across all tiers

**TierStatistics Fields:**

- `hits` (int): Cache hits
- `misses` (int): Cache misses
- `current_size` (int): Current number of entries
- `evictions_lru` (int): LRU evictions
- `evictions_ttl` (int): TTL expirations
- `evictions_health` (int): Health-based evictions
- `evictions_corruption` (int): Corruption-based evictions
- `@property hit_rate -> float` - Cache hit rate (0.0-1.0)
- `@property total_evictions -> int` - Total evictions across all reasons

---

## Retry & Failover

:::{seealso}
For retry and failover configuration patterns, see [Retry & Failover](../guides/retry-failover.md).
:::

### RetryPolicy

Configuration for retry behavior with configurable backoff strategies.

```python
from proxywhirl import RetryPolicy, BackoffStrategy

policy = RetryPolicy(
    max_attempts=3,  # 1-10
    backoff_strategy=BackoffStrategy.EXPONENTIAL,
    base_delay=1.0,  # Base delay in seconds
    multiplier=2.0,  # Backoff multiplier for exponential
    max_backoff_delay=30.0,  # Cap at 30 seconds
    jitter=True,  # Add random jitter (0.5x-1.5x)
    retry_status_codes=[502, 503, 504],  # Retry on these 5xx errors
    timeout=60.0,  # Total timeout in seconds
    retry_non_idempotent=False  # Don't retry POST/PUT/PATCH by default
)

# Calculate delay for attempt
delay = policy.calculate_delay(attempt=0)  # First retry delay
delay = policy.calculate_delay(attempt=1)  # Second retry delay
```

**Fields:**

- `max_attempts` (int): Maximum retry attempts (1-10, default: 3)
- `backoff_strategy` (BackoffStrategy): Timing strategy
  - `EXPONENTIAL`: base_delay * (multiplier ^ attempt)
  - `LINEAR`: base_delay * (attempt + 1)
  - `FIXED`: base_delay (constant)
- `base_delay` (float): Base delay in seconds (0-60, default: 1.0)
- `multiplier` (float): Backoff multiplier (1-10, default: 2.0)
- `max_backoff_delay` (float): Maximum backoff delay (0-300, default: 30.0)
- `jitter` (bool): Add random jitter to delays (default: False)
- `retry_status_codes` (list[int]): HTTP status codes to retry (default: [502, 503, 504])
- `timeout` (Optional[float]): Total timeout in seconds (optional)
- `retry_non_idempotent` (bool): Retry non-idempotent methods (POST/PUT/PATCH, default: False)

**Methods:**

- `calculate_delay(attempt: int) -> float` - Calculate delay for given attempt number (0-indexed)
  - Applies backoff strategy
  - Caps at max_backoff_delay
  - Adds jitter if enabled (0.5x-1.5x random multiplier)

**Validators:**

- `retry_status_codes` must be 5xx errors (500-599)

---

### RetryExecutor

Execute requests with automatic retry logic, circuit breaker integration, and metrics collection.

```python
from proxywhirl import RetryExecutor, RetryPolicy, RetryMetrics, CircuitBreaker

policy = RetryPolicy(max_attempts=3)
circuit_breakers = {
    "proxy-1": CircuitBreaker(proxy_id="proxy-1"),
    "proxy-2": CircuitBreaker(proxy_id="proxy-2")
}
metrics = RetryMetrics()

executor = RetryExecutor(policy, circuit_breakers, metrics)

# Execute with retry
def request_fn():
    return client.get("https://httpbin.org/ip")

response = executor.execute_with_retry(
    request_fn,
    proxy,
    method="GET",
    url="https://httpbin.org/ip",
    request_id="optional-request-id"
)
```

**Constructor Parameters:**

- `retry_policy` (RetryPolicy): Retry configuration
- `circuit_breakers` (dict[str, CircuitBreaker]): Circuit breakers by proxy ID
- `retry_metrics` (RetryMetrics): Metrics collection instance

**Methods:**

- `execute_with_retry(request_fn, proxy, method, url, request_id=None) -> httpx.Response`
  - Executes request with retry logic
  - Checks circuit breaker state before each attempt
  - Records metrics for each attempt
  - Applies backoff delays between retries
  - Respects total timeout if configured
  - Raises `NonRetryableError` for non-retryable errors (e.g., auth failures)
  - Raises `ProxyConnectionError` if all retries exhausted

**Exceptions:**

- `RetryableError`: Exception that triggers a retry
- `NonRetryableError`: Exception that does not trigger a retry (e.g., authentication failures)

---

### CircuitBreaker

Circuit breaker pattern for proxy failure management with rolling failure window.

Implements three states: CLOSED (normal), OPEN (proxy excluded), HALF_OPEN (testing recovery).

```python
from proxywhirl import CircuitBreaker, CircuitBreakerState

breaker = CircuitBreaker(
    proxy_id="proxy-1",
    failure_threshold=5,  # Open after 5 failures
    window_duration=60.0,  # 60s rolling window
    timeout_duration=30.0,  # Stay open for 30s
    persist_state=False  # Enable persistence across restarts
)

# Check if proxy is available
if breaker.should_attempt_request():
    try:
        # Make request
        response = client.get("https://httpbin.org/ip")
        breaker.record_success()  # Close circuit if HALF_OPEN
    except Exception:
        breaker.record_failure()  # May open circuit if threshold reached

# Manual reset
breaker.reset()  # Force CLOSED state

# Check state
print(breaker.state)  # CLOSED, OPEN, or HALF_OPEN
print(breaker.failure_count)
print(breaker.next_test_time)
```

**Constructor Parameters:**

- `proxy_id` (str): Unique proxy identifier
- `failure_threshold` (int): Number of failures before opening circuit (default: 5)
- `window_duration` (float): Rolling window duration in seconds (default: 60.0)
- `timeout_duration` (float): Circuit open duration in seconds (default: 30.0)
- `persist_state` (bool): Enable state persistence across restarts (default: False)

**Fields:**

- `proxy_id` (str): Unique proxy identifier
- `state` (CircuitBreakerState): Current state (CLOSED, OPEN, HALF_OPEN)
- `failure_count` (int): Current failure count in window
- `failure_window` (deque[float]): Rolling window of failure timestamps
- `next_test_time` (Optional[float]): When to attempt recovery (OPEN → HALF_OPEN)
- `last_state_change` (datetime): When state last changed

**States:**

- `CLOSED`: Normal operation, proxy available
- `OPEN`: Proxy excluded from rotation (too many failures)
- `HALF_OPEN`: Testing recovery with limited requests (one test request allowed)

**Methods:**

- `record_failure()` - Record a failure and update state
  - Adds failure to rolling window
  - Removes failures outside window (older than window_duration)
  - Transitions to OPEN if failure_count >= failure_threshold
  - If in HALF_OPEN, transitions back to OPEN (test failed)
- `record_success()` - Record a success
  - If in HALF_OPEN, transitions to CLOSED (recovery successful)
- `should_attempt_request() -> bool` - Check if proxy is available for requests
  - Returns `True` if CLOSED
  - Returns `False` if OPEN (unless timeout elapsed, then transitions to HALF_OPEN and returns `True`)
  - Returns `True` if HALF_OPEN
- `reset()` - Manually reset to CLOSED state (clears failure window)
- `set_storage(storage)` - Set storage backend for state persistence

**Factory Method:**

- `@classmethod async create_with_storage(proxy_id, storage=None, config=None, **kwargs) -> CircuitBreaker`
  - Creates circuit breaker with optional state restoration from storage
  - Recommended for persistence-enabled circuit breakers

**Thread Safety:** Uses `threading.Lock` for thread-safe state updates.

---

### RetryMetrics

Track retry attempts, circuit breaker events, and hourly aggregates for monitoring.

```python
from proxywhirl import RetryMetrics, RetryAttempt, RetryOutcome

metrics = RetryMetrics(
    retention_hours=24,  # Keep data for 24 hours
    max_current_attempts=10000  # Max raw attempts before auto-eviction
)

# Record attempt (done automatically by RetryExecutor)
attempt = RetryAttempt(
    request_id="req-123",
    attempt_number=0,
    proxy_id="proxy-1",
    timestamp=datetime.now(timezone.utc),
    outcome=RetryOutcome.SUCCESS,
    status_code=200,
    delay_before=0.0,
    latency=150.0,
    error_message=None
)
metrics.record_attempt(attempt)

# Aggregate current attempts into hourly summaries
metrics.aggregate_hourly()

# Get summary statistics
summary = metrics.get_summary()
print(summary)
# {
#     "total_retries": 1234,
#     "success_by_attempt": {0: 800, 1: 300, 2: 100},
#     "circuit_breaker_events_count": 45,
#     "retention_hours": 24
# }

# Get time-series data
timeseries = metrics.get_timeseries(hours=24)
# [
#     {
#         "timestamp": "2023-01-01T00:00:00+00:00",
#         "total_requests": 100,
#         "total_retries": 120,
#         "success_rate": 0.95,
#         "avg_latency": 150.0
#     },
#     ...
# ]

# Get per-proxy statistics
by_proxy = metrics.get_by_proxy(hours=24)
# {
#     "proxy-1": {
#         "total_attempts": 100,
#         "success_count": 95,
#         "failure_count": 5,
#         "total_latency": 15000.0,
#         "circuit_breaker_opens": 2
#     },
#     ...
# }
```

**Constructor Parameters:**

- `retention_hours` (int): How long to keep historical data (default: 24)
- `max_current_attempts` (int): Max raw attempts before auto-eviction (default: 10000)

**Fields:**

- `current_attempts` (deque[RetryAttempt]): Raw attempts in current period (bounded by `max_current_attempts`)
- `hourly_aggregates` (dict[datetime, HourlyAggregate]): Historical hourly summaries
- `circuit_breaker_events` (list[CircuitBreakerEvent]): Circuit breaker state changes (max 1000)

**Methods:**

- `record_attempt(attempt: RetryAttempt)` - Record a retry attempt (auto-evicts oldest when at max_current_attempts)
- `record_circuit_breaker_event(event: CircuitBreakerEvent)` - Record circuit breaker state change
- `aggregate_hourly()` - Aggregate current_attempts into hourly summaries (removes old data)
- `get_summary() -> dict` - Get metrics summary (total retries, success by attempt, circuit breaker events)
- `get_timeseries(hours: int = 24) -> list[dict]` - Get time-series data for specified hours
- `get_by_proxy(hours: int = 24) -> dict` - Get per-proxy retry statistics

**Data Models:**

- `RetryAttempt`: Single retry attempt record
  - `request_id` (str): Request identifier
  - `attempt_number` (int): Attempt number (0-indexed)
  - `proxy_id` (str): Proxy ID
  - `timestamp` (datetime): When attempt occurred
  - `outcome` (RetryOutcome): SUCCESS, FAILURE, TIMEOUT, or CIRCUIT_OPEN
  - `status_code` (Optional[int]): HTTP status code
  - `delay_before` (float): Delay before this attempt
  - `latency` (float): Request latency
  - `error_message` (Optional[str]): Error message if failed

- `RetryOutcome` (Enum): SUCCESS, FAILURE, TIMEOUT, CIRCUIT_OPEN

- `CircuitBreakerEvent`: Circuit breaker state change
  - `proxy_id` (str): Proxy ID
  - `from_state` (CircuitBreakerState): Previous state
  - `to_state` (CircuitBreakerState): New state
  - `timestamp` (datetime): When state changed
  - `failure_count` (int): Failure count at time of change

- `HourlyAggregate`: Hourly aggregated metrics
  - `hour` (datetime): Hour timestamp (truncated)
  - `total_requests` (int): Total requests in this hour
  - `total_retries` (int): Total retries in this hour
  - `success_by_attempt` (dict[int, int]): Success count by attempt number
  - `failure_by_reason` (dict[str, int]): Failure count by error reason
  - `avg_latency` (float): Average latency

**Thread Safety:** Uses `threading.Lock` for thread-safe operations.

---

## Parsers

### JSONParser

Parse JSON-formatted proxy lists with key extraction and field validation.

```python
from proxywhirl import JSONParser

# Parse array directly
parser = JSONParser()
proxies = parser.parse('[{"host": "1.2.3.4", "port": 8080}]')

# Extract from key
parser = JSONParser(key="proxies")
proxies = parser.parse('{"proxies": [{"host": "1.2.3.4", "port": 8080}]}')

# Require specific fields
parser = JSONParser(
    key="proxies",
    required_fields=["host", "port", "protocol"]
)
proxies = parser.parse('{"proxies": [{"host": "1.2.3.4", "port": 8080, "protocol": "http"}]}')
```

**Constructor Parameters:**

- `key` (Optional[str]): Optional key to extract from JSON object (if JSON is an object, not array)
- `required_fields` (Optional[list[str]]): Fields that must be present in each proxy

**Methods:**

- `parse(data: str) -> list[dict]` - Parse JSON proxy data
  - Validates JSON format
  - Extracts from key if specified
  - Ensures result is a list
  - Validates required fields if specified
  - Raises `ProxyFetchError` for invalid JSON
  - Raises `ProxyValidationError` for missing required fields

---

### CSVParser

Parse CSV-formatted proxy lists with header detection and column mapping.

```python
from proxywhirl import CSVParser

# Parse with header row
parser = CSVParser(has_header=True)
proxies = parser.parse("""
host,port,protocol
1.2.3.4,8080,http
2.3.4.5,8080,https
""")

# Parse without header (provide column names)
parser = CSVParser(
    has_header=False,
    columns=["host", "port", "protocol"]
)
proxies = parser.parse("1.2.3.4,8080,http")

# Skip invalid rows
parser = CSVParser(has_header=True, skip_invalid=True)
proxies = parser.parse(csv_data)  # Skips malformed rows
```

**Constructor Parameters:**

- `has_header` (bool): Whether CSV has header row (default: True)
- `columns` (Optional[list[str]]): Column names if no header (required if `has_header=False`)
- `skip_invalid` (bool): Skip malformed rows instead of raising error (default: False)

**Methods:**

- `parse(data: str) -> list[dict]` - Parse CSV proxy data
  - Returns list of dictionaries with column names as keys
  - Raises `ProxyFetchError` for malformed CSV (unless `skip_invalid=True`)

---

### PlainTextParser

Parse plain text proxy lists (one proxy per line).

```python
from proxywhirl import PlainTextParser

parser = PlainTextParser(skip_invalid=True)

proxies = parser.parse("""
http://proxy1.example.com:8080
http://user:pass@proxy2.example.com:8080
# This is a comment (skipped)

socks5://proxy3.example.com:1080
""")
# Returns: [
#     {"url": "http://proxy1.example.com:8080"},
#     {"url": "http://user:pass@proxy2.example.com:8080"},
#     {"url": "socks5://proxy3.example.com:1080"}
# ]
```

**Constructor Parameters:**

- `skip_invalid` (bool): Skip invalid URLs instead of raising error (default: False)

**Methods:**

- `parse(data: str) -> list[dict]` - Parse plain text proxy data
  - Returns list of dictionaries with `url` key
  - Skips empty lines
  - Skips comments (lines starting with `#`)
  - Validates URL format (scheme and netloc required)
  - Raises `ProxyFetchError` for invalid URLs (unless `skip_invalid=True`)

---

### HTMLTableParser

Parse HTML table-formatted proxy lists with CSS selector and column mapping.

```python
from proxywhirl import HTMLTableParser

# Parse with column indices
parser = HTMLTableParser(
    table_selector="table.proxies",
    column_indices={"host": 0, "port": 1, "protocol": 2}
)
proxies = parser.parse(html_data)

# Parse with header mapping
parser = HTMLTableParser(
    table_selector="table#proxy-list",
    column_map={"IP Address": "host", "Port": "port", "Type": "protocol"}
)
proxies = parser.parse(html_data)
```

**Constructor Parameters:**

- `table_selector` (str): CSS selector for table element (default: "table")
- `column_map` (Optional[dict[str, str]]): Map header names to proxy fields (e.g., `{"IP Address": "host"}`)
- `column_indices` (Optional[dict[str, int]]): Map field names to column indices (e.g., `{"host": 0}`)

**Methods:**

- `parse(data: str) -> list[dict]` - Parse HTML table proxy data
  - Uses BeautifulSoup for HTML parsing
  - Returns list of dictionaries with extracted fields
  - Auto-detects header row (looks for `<th>` elements)
  - Returns empty list if table not found

---

## Utility Functions

### configure_logging

Configure loguru logging with JSON formatting and credential redaction.

```python
from proxywhirl import configure_logging

# JSON logging (for production)
configure_logging(
    level="INFO",
    format_type="json",
    redact_credentials=True
)

# Text logging (for development)
configure_logging(
    level="DEBUG",
    format_type="text",
    redact_credentials=True
)
```

**Parameters:**

- `level` (str): Log level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
- `format_type` (str): "json" or "text"
- `redact_credentials` (bool): Whether to redact sensitive data (passwords, tokens, API keys)

**Features:**

- Removes default loguru handler
- JSON format includes: timestamp, level, message, module, function, line, exception, extra
- Text format includes: timestamp, level, name, function, line, message (with color)
- Automatic credential redaction:
  - SecretStr values → "***"
  - Dict keys containing "password", "secret", "token", "api_key", "credential", "username" → "***"
  - Proxy URLs with credentials → masked

---

### is_valid_proxy_url

Validate proxy URL format using regex pattern.

```python
from proxywhirl import is_valid_proxy_url

# Valid URLs
is_valid_proxy_url("http://proxy.example.com:8080")  # True
is_valid_proxy_url("socks5://user:pass@proxy.com:1080")  # True
is_valid_proxy_url("https://192.168.1.1:3128")  # True

# Invalid URLs
is_valid_proxy_url("http://proxy.com")  # False (no port)
is_valid_proxy_url("proxy.com:8080")  # False (no scheme)
is_valid_proxy_url("ftp://proxy.com:8080")  # False (unsupported scheme)
```

**Parameters:**

- `url` (str): URL to validate

**Returns:**

- `bool`: True if valid proxy URL (scheme://[user:pass@]host:port)

**Supported Schemes:** http, https, socks4, socks5

---

### parse_proxy_url

Parse proxy URL into components (protocol, host, port, credentials).

```python
from proxywhirl import parse_proxy_url

parsed = parse_proxy_url("http://user:pass@proxy.example.com:8080")
# Returns: {
#     "protocol": "http",
#     "host": "proxy.example.com",
#     "port": 8080,
#     "username": "user",
#     "password": "pass"
# }

parsed = parse_proxy_url("socks5://proxy.com:1080")
# Returns: {
#     "protocol": "socks5",
#     "host": "proxy.com",
#     "port": 1080,
#     "username": None,
#     "password": None
# }
```

**Parameters:**

- `url` (str): Proxy URL to parse

**Returns:**

- `dict[str, Any]`: Dictionary with protocol, host, port, username, password

**Raises:**

- `ValueError`: If URL format is invalid

---

### validate_proxy_model

Validate a Proxy model instance and return list of validation errors.

```python
from proxywhirl import validate_proxy_model, Proxy

proxy = Proxy(url="http://proxy.example.com:8080")
errors = validate_proxy_model(proxy)

if errors:
    print("Validation errors:", errors)
else:
    print("Proxy is valid")
```

**Parameters:**

- `proxy` (Proxy): Proxy instance to validate

**Returns:**

- `list[str]`: List of validation error messages (empty if valid)

**Validations:**

- URL format
- Credential consistency (both username and password or neither)
- Stats consistency (total_requests >= successes + failures)
- Consecutive failures non-negative

---

### encrypt_credentials / decrypt_credentials

:::{warning}
Never hardcode encryption keys in source code. Use environment variables (`PROXYWHIRL_KEY`) or the auto-generated key file at `~/.config/proxywhirl/key.enc`. See [Configuration](configuration.md) for security best practices.
:::

Encrypt/decrypt credentials using Fernet symmetric encryption.

```python
from proxywhirl import encrypt_credentials, decrypt_credentials, generate_encryption_key

# Generate key
key = generate_encryption_key()  # Returns base64-encoded Fernet key

# Encrypt
encrypted = encrypt_credentials("secret_password", key)

# Decrypt
decrypted = decrypt_credentials(encrypted, key)
assert decrypted == "secret_password"
```

**Functions:**

- `generate_encryption_key() -> str` - Generate base64-encoded Fernet key
- `encrypt_credentials(plaintext: str, key: Optional[str] = None) -> str` - Encrypt plaintext (generates new key if not provided)
- `decrypt_credentials(ciphertext: str, key: str) -> str` - Decrypt ciphertext using key

**Uses:** Fernet symmetric encryption (AES 128 in CBC mode with HMAC for authentication)

---

### proxy_to_dict

Convert Proxy instance to dictionary (for serialization).

```python
from proxywhirl import proxy_to_dict, Proxy

proxy = Proxy(url="http://proxy.example.com:8080")
data = proxy_to_dict(proxy, include_stats=True)
```

**Parameters:**

- `proxy` (Proxy): Proxy instance to convert
- `include_stats` (bool): Whether to include statistics (default: True)

**Returns:**

- `dict[str, Any]`: Dictionary representation of proxy

---

### create_proxy_from_url

Create Proxy instance from URL string with optional metadata.

```python
from proxywhirl import create_proxy_from_url
from proxywhirl.models import ProxySource

# Simple URL
proxy = create_proxy_from_url("http://proxy.example.com:8080")

# With credentials and metadata
proxy = create_proxy_from_url(
    "http://user:pass@proxy.example.com:8080",
    source=ProxySource.USER,
    tags={"premium", "fast"},
    country_code="US"
)
```

**Parameters:**

- `url` (str): Proxy URL (with or without credentials)
- `source` (ProxySource): Proxy source type (default: ProxySource.USER)
- `tags` (set[str]): Custom tags (optional)
- Additional keyword arguments forwarded to Proxy constructor

**Returns:**

- `Proxy`: Proxy instance

---

### deduplicate_proxies

Deduplicate proxy list by URL+port combination (keeps first occurrence).

```python
from proxywhirl import deduplicate_proxies

proxies = [
    {"url": "http://proxy1.example.com:8080"},
    {"url": "http://proxy1.example.com:8080"},  # Duplicate
    {"url": "http://proxy2.example.com:8080"}
]

unique_proxies = deduplicate_proxies(proxies)
# Returns: [
#     {"url": "http://proxy1.example.com:8080"},
#     {"url": "http://proxy2.example.com:8080"}
# ]
```

**Parameters:**

- `proxies` (list[dict[str, Any]]): List of proxy dictionaries

**Returns:**

- `list[dict[str, Any]]`: Deduplicated list (first occurrence kept)

**Deduplication Key:** host:port (from URL or explicit host/port fields)

---

## Enumerations

### HealthStatus

Proxy health status states for tracking proxy availability.

```python
from proxywhirl.models import HealthStatus

HealthStatus.UNKNOWN     # Not yet tested (default)
HealthStatus.HEALTHY     # Working normally
HealthStatus.DEGRADED    # Partial functionality (some failures)
HealthStatus.UNHEALTHY   # Experiencing issues (many failures)
HealthStatus.DEAD        # Not responding (completely unusable)
```

---

### ProxySource

Origin type of proxy for tracking where proxies came from.

```python
from proxywhirl.models import ProxySource

ProxySource.USER      # Manually added by user
ProxySource.FETCHED   # Auto-fetched from proxy source
ProxySource.API       # Retrieved from API
ProxySource.FILE      # Loaded from file
```

---

### ProxyFormat

Supported proxy list formats for parsing.

```python
from proxywhirl.models import ProxyFormat

ProxyFormat.JSON          # JSON format
ProxyFormat.CSV           # CSV format
ProxyFormat.TSV           # Tab-separated values
ProxyFormat.PLAIN_TEXT    # Plain text (one per line)
ProxyFormat.HTML_TABLE    # HTML table
ProxyFormat.CUSTOM        # Custom parser
```

---

### RenderMode

Page rendering modes for fetching proxy lists.

```python
from proxywhirl.models import RenderMode

RenderMode.STATIC       # Static HTTP request (fast)
RenderMode.JAVASCRIPT   # JavaScript evaluation needed
RenderMode.BROWSER      # Full browser rendering with Playwright (slow but comprehensive)
RenderMode.AUTO         # Automatic detection based on response
```

---

### ValidationLevel

Proxy validation strictness levels with different speed/accuracy tradeoffs.

```python
from proxywhirl.models import ValidationLevel

ValidationLevel.BASIC     # Format + TCP connectivity (~100ms)
ValidationLevel.STANDARD  # BASIC + HTTP request test (~500ms)
ValidationLevel.FULL      # STANDARD + Anonymity check (~2s)
```

---

### BackoffStrategy

Retry backoff timing strategies for calculating delays between retry attempts.

```python
from proxywhirl import BackoffStrategy

BackoffStrategy.EXPONENTIAL  # base_delay * (multiplier ^ attempt)
BackoffStrategy.LINEAR       # base_delay * (attempt + 1)
BackoffStrategy.FIXED        # base_delay (constant)
```

---

### CircuitBreakerState

Circuit breaker states for tracking proxy availability.

```python
from proxywhirl import CircuitBreakerState

CircuitBreakerState.CLOSED      # Normal operation, proxy available
CircuitBreakerState.OPEN        # Proxy excluded from rotation (too many failures)
CircuitBreakerState.HALF_OPEN   # Testing recovery with limited requests
```

---

## Built-in Proxy Sources

ProxyWhirl provides pre-configured proxy sources for immediate use.

### Individual Sources

```python
from proxywhirl import (
    # ProxyScrape (API-based, high quality)
    PROXY_SCRAPE_HTTP,
    PROXY_SCRAPE_SOCKS4,
    PROXY_SCRAPE_SOCKS5,

    # Geonode (API-based, geo-targeting)
    GEONODE_HTTP,
    GEONODE_SOCKS4,
    GEONODE_SOCKS5,

    # GitHub: TheSpeedX (community-maintained, large pool)
    GITHUB_THESPEEDX_HTTP,
    GITHUB_THESPEEDX_SOCKS4,
    GITHUB_THESPEEDX_SOCKS5,

    # GitHub: monosans (frequently updated)
    GITHUB_MONOSANS_HTTP,
    GITHUB_MONOSANS_SOCKS4,
    GITHUB_MONOSANS_SOCKS5,

    # GitHub: Proxifly (validated proxies)
    GITHUB_PROXIFLY_HTTP,
    GITHUB_PROXIFLY_SOCKS4,
    GITHUB_PROXIFLY_SOCKS5,

    # GitHub: Komutan (reliable sources)
    GITHUB_KOMUTAN_HTTP,
    GITHUB_KOMUTAN_SOCKS4,
    GITHUB_KOMUTAN_SOCKS5
)
```

### Source Collections

```python
from proxywhirl import (
    ALL_HTTP_SOURCES,      # All HTTP proxy sources
    ALL_SOCKS4_SOURCES,    # All SOCKS4 proxy sources
    ALL_SOCKS5_SOURCES,    # All SOCKS5 proxy sources
    ALL_SOURCES,           # All sources combined (HTTP + SOCKS4 + SOCKS5)
    RECOMMENDED_SOURCES,   # Recommended high-quality sources (curated subset)
    API_SOURCES            # API-based sources only (ProxyScrape, Geonode)
)

# Use with ProxyFetcher
from proxywhirl import ProxyFetcher

fetcher = ProxyFetcher(sources=RECOMMENDED_SOURCES)
proxies = await fetcher.fetch_all(validate=True, deduplicate=True)
```

**Recommended Usage:**

- `RECOMMENDED_SOURCES`: Best balance of quality and quantity
- `API_SOURCES`: Most reliable but may have rate limits
- Protocol-specific collections: Use when you need specific protocol support

---

## Exceptions

All ProxyWhirl exceptions inherit from `ProxyWhirlError` base exception.

```python
from proxywhirl import (
    ProxyWhirlError,           # Base exception for all ProxyWhirl errors
    ProxyValidationError,      # Proxy validation failed
    ProxyPoolEmptyError,       # No healthy proxies available
    ProxyConnectionError,      # Proxy connection failed
    ProxyAuthenticationError,  # Proxy authentication failed (401/407)
    ProxyFetchError,           # Fetching proxies from source failed
    ProxyStorageError,         # Storage operation failed
    CacheCorruptionError,      # Cache data corruption detected
    CacheStorageError,         # Cache storage operation failed
    CacheValidationError,      # Cache validation failed
    RequestQueueFullError      # Request queue is full (when queuing enabled)
)

# Usage
try:
    response = rotator.get("https://httpbin.org/ip")
except ProxyConnectionError as e:
    print(f"Connection failed: {e}")
except ProxyPoolEmptyError as e:
    print(f"No proxies available: {e}")
except ProxyAuthenticationError as e:
    print(f"Authentication failed: {e}")
except ProxyWhirlError as e:
    print(f"ProxyWhirl error: {e}")
```

**Exception Hierarchy:**

```
Exception
└── ProxyWhirlError (base)
    ├── ProxyValidationError
    ├── ProxyPoolEmptyError
    ├── ProxyConnectionError
    ├── ProxyAuthenticationError
    ├── ProxyFetchError
    ├── ProxyStorageError
    ├── CacheCorruptionError
    ├── CacheStorageError
    ├── CacheValidationError (also inherits ValueError)
    └── RequestQueueFullError
```

:::{seealso}
For comprehensive error handling patterns, see [Exceptions](exceptions.md).
:::

---

## Type Annotations

ProxyWhirl is fully type-annotated for use with type checkers (mypy, pyright, etc.).

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from proxywhirl import (
        ProxyRotator,
        Proxy,
        RotationStrategy,
        RetryPolicy,
        ProxyConfiguration
    )

def setup_rotator(
    strategy: RotationStrategy,
    retry_policy: RetryPolicy
) -> ProxyRotator:
    """Create and configure a ProxyRotator instance."""
    rotator: ProxyRotator = ProxyRotator(
        strategy=strategy,
        retry_policy=retry_policy
    )
    return rotator

def add_proxy_to_rotator(
    rotator: ProxyRotator,
    proxy: Proxy | str
) -> None:
    """Add a proxy to the rotator."""
    rotator.add_proxy(proxy)
```

**Protocol Types:**

- `RotationStrategy`: Protocol for rotation strategies (runtime checkable)

**Type Checking:**

```bash
# Install type checker
pip install mypy

# Run type checking
mypy your_code.py
```

---

## Version

```python
import proxywhirl

print(proxywhirl.__version__)  # "1.0.0"
```

---

## See Also

- [REST API](rest-api.md) -- HTTP REST API documentation
- [Cache API](cache-api.md) -- Detailed cache system documentation
- [Rate Limiting API](rate-limiting-api.md) -- Rate limiting system reference
- [Configuration](configuration.md) -- Configuration options
- [Exceptions](exceptions.md) -- All exception types
- [Async Client](../guides/async-client.md) -- Async client usage guide
- [Advanced Strategies](../guides/advanced-strategies.md) -- Strategy selection guide
- [Retry & Failover](../guides/retry-failover.md) -- Retry and failover patterns
- [Caching](../guides/caching.md) -- Caching configuration guide
- [Deployment Security](../guides/deployment-security.md) -- Production deployment guide
