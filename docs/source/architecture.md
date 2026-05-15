# Architecture Overview

ProxyWhirl is designed with a modular, layered architecture optimized for scalability, performance, and reliability.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Application Layer                     │
│  ┌──────────────────────────────────────────────────┐   │
│  │  CLI (typer) │ REST API (FastAPI) │ TUI (Textual)│  │
│  └──────────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│                 Core Rotator Layer                      │
│  ┌────────────────────────────────────────────────┐    │
│  │  ProxyWhirl (sync) │ AsyncProxyWhirl (async)   │    │
│  └────────────────────────────────────────────────┘    │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│              Strategy & Selection Layer                 │
│  ┌────────────────────────────────────────────────┐    │
│  │  RoundRobinStrategy │ WeightedStrategy │ ...   │    │
│  │  SelectionContext   │ RotationStrategy         │    │
│  └────────────────────────────────────────────────┘    │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│            Support Components Layer                     │
│  ┌────────────────────────────────────────────────┐    │
│  │ Cache │ CircuitBreaker │ Retry │ RateLimit    │    │
│  │ HealthMonitor │ Metrics │ Geo  │ Enrichment   │    │
│  └────────────────────────────────────────────────┘    │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│         Fetching & Validation Layer                     │
│  ┌────────────────────────────────────────────────┐    │
│  │  ProxyFetcher │ ProxyValidator │ Parsers       │    │
│  │  JSONParser   │ CSVParser      │ HTMLParser    │    │
│  │  BrowserRenderer │ SourceManager               │    │
│  └────────────────────────────────────────────────┘    │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│          Storage & Persistence Layer                    │
│  ┌────────────────────────────────────────────────┐    │
│  │  SQLiteStorage │ FileStorage │ ProxyTable      │    │
│  │  Database Migrations │ Persistence Config      │    │
│  └────────────────────────────────────────────────┘    │
└──────────────────┬──────────────────────────────────────┘
                   │
          External Data Sources
          (Proxy APIs, HTML Lists)
```

## Core Components

### 1. Rotator (ProxyWhirl / AsyncProxyWhirl)

**Responsibility:** Main entry point for proxy selection and rotation.

**Key Methods:**
- `get_next_proxy()` / `async get_next_proxy()` - Get single proxy
- `get_proxies(limit)` / `async get_proxies(limit)` - Get multiple proxies
- `validate()` / `async validate()` - Validate pool
- `add_proxy()` / `async add_proxy()` - Add proxy to pool
- `remove_proxy()` / `async remove_proxy()` - Remove proxy

**Sync vs Async:**
- **Sync (ProxyWhirl):** Blocks on I/O, suitable for scripts/CLI
- **Async (AsyncProxyWhirl):** Non-blocking, for async frameworks (FastAPI, etc.)

### 2. Strategy Layer

Implements various rotation strategies:

| Strategy | Use Case | Configuration |
|----------|----------|---|
| **RoundRobin** | Even distribution | Default, no config |
| **Random** | No order preference | Simple, fast |
| **Weighted** | Bias by quality/location | Weights: `{country: score}` |
| **PerformanceBased** | Prefer fast proxies | Auto-update by response time |
| **LeastUsed** | Balance load | Track usage per proxy |
| **GeoOptimized** | Route by geography | Geo-aware selection |
| **AnonymityBased** | Prefer anonymous | Score by anonymity level |
| **SessionPreserving** | Sticky sessions | Affinity key-based |
| **Probabilistic** | Markov-based selection | Historical patterns |

**Selection Flow:**
```
SelectionContext → StrategyRegistry.get_strategy() 
  → Strategy.select(proxies, context)
  → Selected Proxy
```

### 3. Cache Layer

**Multi-tier caching:**

1. **L1 Cache (Memory):** In-process, < 1ms latency
2. **L2 Cache (Local):** File-based, encrypted
3. **L3 Cache (Distributed):** Redis (optional)

**Manager Methods:**
- `get()` / `set()` - Cache operations
- `invalidate()` - Clear cache entry
- `get_or_fetch()` - Lazy load with fallback

### 4. Validation & Health Monitoring

**ProxyValidator:**
- Validates proxy URL format
- Tests connectivity (HTTP/HTTPS/SOCKS)
- Checks anonymity level
- Measures response time

**HealthMonitor:**
- Periodic validation (configurable interval)
- Failure tracking
- Automatic removal after threshold
- Recovery handling

### 5. Storage Layer

**SQLiteStorage (Default):**
- ACID compliance
- Persistent pool state
- Query proxies by attributes
- Transaction support

**FileStorage (Alternative):**
- JSON/CSV formats
- Lightweight, no DB setup
- Limited query capabilities

### 6. Fetcher & Parser

**ProxyFetcher:**
- Multi-source fetching
- Concurrent requests
- Error handling & retries
- Deduplication

**Parsers:**
- **JSONParser** - JSON API responses
- **CSVParser** - CSV files
- **PlainTextParser** - Line-separated IPs
- **HTMLTableParser** - Table extraction
- **BrowserRenderer** - JS-rendered sources

### 7. Circuit Breaker

**Pattern:** Fail-fast on repeated failures

**States:**
```
CLOSED (normal) ─error─→ OPEN (blocking)
     ↑                        │
     │                        │
     └←─success after timeout─┘
```

**Configuration:**
```python
CircuitBreakerConfig(
    failure_threshold=5,        # Fail count to open
    recovery_timeout=60,        # Seconds to retry
    expected_exception=Exception
)
```

### 8. Retry & Exponential Backoff

**Policy:**
```python
RetryPolicy(
    max_retries=3,
    initial_delay=1,            # seconds
    max_delay=60,
    backoff_factor=2.0,
    jitter=True
)
```

**Backoff Formula:**
```
delay = min(initial_delay * (backoff_factor ** attempt), max_delay)
actual_delay = delay + random(0, jitter)
```

### 9. Rate Limiting

**Token Bucket Algorithm:**

```
Available tokens: min(capacity, tokens + rate * time_passed)
Request: if tokens >= cost:
    tokens -= cost
    allow()
else:
    block()
```

**Configuration:**
```python
RateLimiter(
    requests_per_second=100,
    burst_size=200
)
```

## Data Flow

### 1. Proxy Selection Flow

```
rotator.get_next_proxy()
    ├─ Check cache (L1)
    │   └─ Return if hit
    ├─ Apply selection strategy
    │   ├─ SelectionContext.filter() → eligible proxies
    │   └─ Strategy.select() → chosen proxy
    ├─ Health check (circuit breaker)
    │   └─ Skip if unhealthy
    ├─ Cache result (L1, L2)
    └─ Return Proxy object
```

### 2. Proxy Validation Flow

```
ProxyValidator.validate(proxy)
    ├─ Format validation
    ├─ DNS resolution
    ├─ Connection test
    │   ├─ HTTP CONNECT
    │   ├─ HTTPS tunnel
    │   └─ SOCKS handshake
    ├─ Response analysis
    │   ├─ Status code
    │   ├─ Response time
    │   └─ Anonymity check
    ├─ Update health status
    └─ Return ValidationResult
```

### 3. Fetching & Persistence Flow

```
rotator.load_proxies(sources)
    ├─ ProxyFetcher.fetch_all(sources)
    │   ├─ Concurrent HTTP requests
    │   ├─ Parser selection by content-type
    │   └─ Extract proxy list
    ├─ Deduplication
    ├─ ProxyValidator.validate_batch()
    ├─ Storage.save_proxies()
    │   └─ SQLiteStorage.insert_bulk()
    └─ Update statistics
```

## Concurrency Model

### Thread-based (Sync)
- I/O blocking acceptable
- Simpler debugging
- Good for scripts/CLI

### Async/Await (Async)
- Non-blocking I/O
- High concurrency
- Required for FastAPI/ASGI

### Parallelization Points
- Fetching (concurrent requests)
- Validation (thread pool)
- Metric collection (background tasks)

## Error Handling Strategy

```
ProxyWhirlError (base)
├─ RetryableError
│   ├─ ProxyConnectionError
│   ├─ ProxyTimeoutError
│   └─ TemporaryServiceError
├─ NonRetryableError
│   ├─ ProxyValidationError
│   ├─ ProxyAuthenticationError
│   └─ ProxyFormatError
└─ SystemError
    ├─ ProxyPoolEmptyError
    ├─ StorageError
    └─ ConfigurationError
```

## Database Schema

**ProxyTable:**
```
┌─────────────────────────┐
│ Proxy                   │
├─────────────────────────┤
│ id (PK)                 │
│ host (string)           │
│ port (int)              │
│ protocol (string)       │
│ username (string?)      │
│ password (string?)      │
│ country (string?)       │
│ anonymity (string?)     │
│ response_time (float)   │
│ last_checked (datetime) │
│ is_healthy (bool)       │
│ fail_count (int)        │
│ created_at (datetime)   │
│ updated_at (datetime)   │
└─────────────────────────┘
```

## Configuration Hierarchy

```
Defaults (in code)
    ↓
TOML Config (proxywhirl.toml)
    ↓
Environment Variables (PROXYWHIRL_*)
    ↓
Constructor Arguments (ProxyConfiguration)
    ↓
Runtime Overrides (method parameters)
```

## Performance Characteristics

| Operation | Time Complexity | Space Complexity | Notes |
|-----------|---|---|---|
| Get next proxy | O(1) avg | O(n) | Strategy-dependent |
| Validate proxy | O(1) | O(1) | Network I/O dominant |
| Add proxy | O(1) avg | O(1) | Database insert |
| Remove proxy | O(1) avg | O(1) | Database delete |
| Filter proxies | O(n log n) | O(k) | k = result size |
| Bulk fetch | O(n*m) | O(n) | n sources, m requests |

## Deployment Architecture

```
┌─────────────────────────────────────────┐
│         Load Balancer (nginx)           │
└──────────────────┬──────────────────────┘
                   │
      ┌────────────┼────────────┐
      │            │            │
┌─────▼───┐  ┌─────▼───┐  ┌─────▼───┐
│Container│  │Container│  │Container│
│  API 1  │  │  API 2  │  │  API 3  │
└─────┬───┘  └─────┬───┘  └─────┬───┘
      │            │            │
      └────────────┼────────────┘
                   │
         ┌─────────▼─────────┐
         │   SQLite DB       │
         │ (Persistent Vol)  │
         └───────────────────┘
```

## Extension Points

1. **Custom Strategies** - Implement `RotationStrategy` protocol
2. **Custom Parsers** - Extend `BaseParser` class
3. **Custom Fetchers** - Implement `ProxyFetcher` interface
4. **Custom Storage** - Implement `StorageBackend` protocol
5. **Middleware** - Add FastAPI/ASGI middleware
6. **Webhooks** - Register event handlers

See [Custom Strategies Guide](guides/custom-strategies.md) for details.
