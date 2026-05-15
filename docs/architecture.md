# ProxyWhirl Architecture Guide

## Overview

ProxyWhirl is a sophisticated Python proxy rotation library designed for high-performance, concurrent proxy management with advanced features like intelligent rotation strategies, health monitoring, circuit breaking, and adaptive retry logic.

### Core Philosophy

- **Abstraction**: Hide complexity of proxy rotation from users
- **Performance**: Minimize latency and maximize throughput
- **Resilience**: Handle proxy failures gracefully with circuit breakers and retries
- **Observability**: Provide metrics and logging for debugging and monitoring
- **Security**: Encrypt sensitive data, validate inputs, prevent injection attacks
- **Extensibility**: Allow custom strategies, parsers, and storage backends

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Layer                              │
│  (ProxyWhirl, AsyncProxyWhirl, CLI, TUI, API, MCP Server)     │
└────────────────────┬────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│                    Proxy Rotator Core                            │
│  • Rotation strategy selection                                  │
│  • Pool management                                              │
│  • Session state tracking                                       │
└────┬──────────┬──────────┬──────────┬──────────┬────────────────┘
     │          │          │          │          │
┌────▼──┐  ┌───▼──┐  ┌───▼──┐  ┌──▼──┐  ┌──▼────┐
│Health │  │Rate  │  │Circuit│  │Retry│  │Cache  │
│Monitor│  │Limit │  │Breaker│  │Logic│  │System │
└────┬──┘  └───┬──┘  └───┬──┘  └──┬──┘  └──┬────┘
     │         │         │        │        │
┌────▼─────────▼─────────▼────────▼────────▼────┐
│          Storage & Persistence                 │
│  (SQLiteStorage, FileStorage, SQLModel ORM)   │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│         External Integration Points             │
│  (HTTP Clients, Proxy Sources, Databases)     │
└─────────────────────────────────────────────────┘
```

## Core Components

### 1. Rotators (Entry Points)

#### ProxyWhirl (Synchronous)
```python
class ProxyWhirl:
    """Synchronous proxy rotator for blocking I/O workloads."""
    
    def __init__(self, config: ProxyConfiguration, storage_provider=None)
    def get_proxy(self, context: Optional[SelectionContext] = None) -> Proxy
    def get_pool(self) -> ProxyPool
    def validate_proxy(self, proxy: Proxy) -> bool
    def add_proxy(self, proxy: Proxy) -> None
    def get_health_stats(self) -> Dict[str, HealthStatus]
```

**Use Cases:**
- CLI tools and scripts
- Batch processing
- Traditional web scraping
- Simple server applications

#### AsyncProxyWhirl (Asynchronous)
```python
class AsyncProxyWhirl:
    """Asynchronous proxy rotator for high-concurrency workloads."""
    
    async def __init__(self, config: ProxyConfiguration, storage_provider=None)
    async def get_proxy(self, context: Optional[SelectionContext] = None) -> Proxy
    async def get_pool(self) -> ProxyPool
    async def validate_proxy(self, proxy: Proxy) -> bool
    async def add_proxy(self, proxy: Proxy) -> None
    async def get_health_stats(self) -> Dict[str, HealthStatus]
```

**Use Cases:**
- FastAPI/Starlette applications
- High-concurrency web scrapers
- Real-time data pipelines
- Async IoT applications

### 2. Proxy Models

#### Proxy Model
Core data model representing a single proxy with metadata.

```python
@dataclass
class Proxy:
    protocol: str  # "http", "https", "socks4", "socks5"
    host: str
    port: int
    username: Optional[str]
    password: Optional[str]
    credentials: Optional[ProxyCredentials]
    tags: List[str]
    metadata: Dict[str, Any]
    geo_location: Optional[Dict[str, str]]
    health_status: HealthStatus
    success_count: int
    failure_count: int
    last_used_at: Optional[datetime]
    created_at: datetime
```

#### ProxyPool
Container for managing multiple proxies with statistical tracking.

```python
@dataclass
class ProxyPool:
    proxies: List[Proxy]
    rotation_strategy: RotationStrategy
    health_monitor: HealthMonitor
    stats: SourceStats
```

### 3. Rotation Strategies

**Strategy Pattern** implementation with 9 built-in strategies:

1. **RoundRobinStrategy**: Cyclic sequential rotation
2. **RandomStrategy**: Uniform random selection
3. **WeightedStrategy**: Probability-weighted selection
4. **PerformanceBasedStrategy**: Weighted by success rate
5. **LeastUsedStrategy**: Select least-used proxies first
6. **LocationBasedStrategy**: Select by geographic location
7. **LatencyBasedStrategy**: Select by response latency
8. **RandomizedRoundRobinStrategy**: Randomized cycling with fairness
9. **SessionAwareStrategy**: Persistent sessions per proxy

**Strategy Interface:**
```python
class RotationStrategy(Protocol):
    def select(self, pool: ProxyPool, context: Optional[SelectionContext]) -> Proxy
    def record_success(self, proxy: Proxy) -> None
    def record_failure(self, proxy: Proxy) -> None
```

### 4. Health Monitoring

**HealthMonitor** tracks proxy availability and performance:

```python
class HealthMonitor:
    def check_health(self, proxy: Proxy) -> HealthStatus
    async def check_health_async(self, proxy: Proxy) -> HealthStatus
    def get_status(self, proxy: Proxy) -> HealthStatus
    def mark_healthy(self, proxy: Proxy) -> None
    def mark_unhealthy(self, proxy: Proxy) -> None
    def get_stats(self) -> Dict[str, HealthStatus]
```

**HealthStatus Levels:**
- `UNKNOWN`: Not yet tested
- `HEALTHY`: Recent successful connections
- `DEGRADED`: Intermittent failures
- `UNHEALTHY`: Consistent failures
- `INACTIVE`: Explicitly disabled

### 5. Circuit Breaker Pattern

**CircuitBreaker** prevents cascading failures:

```
CLOSED (normal) ──[threshold failures]──> OPEN (failing)
   ▲                                          │
   └──────────[recovery timeout]──────────────┘
                    │
                    ├──> HALF_OPEN (testing)
                    └──[success/failure]──> CLOSED/OPEN
```

```python
class CircuitBreaker:
    def call(self, func: Callable, *args, **kwargs) -> Any
    def reset(self) -> None
    def get_state(self) -> str
```

### 6. Retry Logic

**RetryExecutor** with exponential backoff:

```python
class RetryPolicy:
    max_retries: int
    initial_delay: float
    max_delay: float
    exponential_base: float
    jitter: bool
    retryable_exceptions: List[Type[Exception]]

class RetryExecutor:
    def execute(self, func: Callable, *args, **kwargs) -> Any
    async def execute_async(self, func: Callable, *args, **kwargs) -> Any
```

**Flow:**
1. Execute function
2. Catch retryable exception
3. Wait (initial_delay * exponential_base^attempt + random jitter)
4. Retry up to max_retries times

### 7. Rate Limiting

**RateLimiter** using token bucket algorithm:

```python
class RateLimiter:
    def acquire(self, tokens: int = 1) -> bool  # Non-blocking
    async def acquire_async(self, tokens: int = 1) -> bool
    def wait(self, tokens: int = 1) -> float  # Blocking until available
```

**Use Cases:**
- Respect proxy provider rate limits
- Prevent overwhelming target servers
- Fair resource sharing across requests

### 8. Multi-Tier Caching

**CacheManager** with three tiers:

```
L1 Memory Cache (in-process, fast, volatile)
           │
           ▼
L2 Redis Cache (shared, medium speed, persistent)
           │
           ▼
L3 SQLite Cache (distributed, slower, durable)
```

### 9. Proxy Fetchers & Validators

**ProxyFetcher**: Retrieves proxies from external sources
```python
class ProxyFetcher:
    async def fetch(self, source: ProxySource) -> List[Proxy]
    def validate_proxy(self, proxy: Proxy) -> bool
```

**Parsers** (Pluggable):
- JSONParser: Parse JSON proxy arrays
- CSVParser: Parse CSV format
- PlainTextParser: One proxy per line
- HTMLTableParser: Extract from HTML tables

### 10. Data Persistence

**Storage Interface:**
```python
class Storage(Protocol):
    def save(self, pool: ProxyPool) -> None
    def load(self) -> ProxyPool
    def update(self, proxy: Proxy) -> None
    def delete(self, proxy_id: str) -> None
    def get_stats(self) -> Dict[str, Any]
```

**Implementations:**
- **SQLiteStorage**: Full-featured, local persistence
- **FileStorage**: Simple JSON-based, lightweight
- **SQLModel ORM**: Alembic migrations, relational queries

## Data Flow Diagrams

### Request Flow (Synchronous)

```
User Request
      │
      ▼
ProxyWhirl.get_proxy()
      │
      ├─> SelectionContext setup
      │   (URL, headers, body, tags)
      │
      ├─> Check rate limiter
      │   ├─ No: Acquire tokens
      │   └─ Yes: Wait/fail
      │
      ├─> Apply rotation strategy
      │   (Select from healthy proxies)
      │
      ├─> Check circuit breaker
      │   ├─ OPEN: Use fallback
      │   └─ CLOSED: Continue
      │
      ├─> Check cache
      │   (L1 → L2 → L3)
      │
      ├─> Return cached result OR
      ├─> Perform health check
      │   └─> Update health status
      │
      ▼
Return Proxy + Metadata
```

### Proxy Rotation Workflow

```
Add Proxy Source
      │
      ▼
ProxyFetcher.fetch()
      │
      ├─> HTTP request to source
      ├─> Parse response (JSON/CSV/HTML)
      ├─> Validate each proxy
      │   ├─ Host/port valid?
      │   ├─ No duplicates?
      │   └─ Malware checks?
      │
      ▼
ProxyValidator.validate()
      │
      ├─> Test HTTP connection
      ├─> Test HTTPS connection
      ├─> Extract location data
      ├─> Measure latency
      │
      ▼
Update ProxyPool
      │
      ├─> Save to storage
      ├─> Update health monitor
      ├─> Clear cache (if changed)
      │
      ▼
Ready for rotation
```

### Error Recovery Flow

```
HTTP Request with Proxy
      │
      ▼
  Success?
  ├─ Yes ──> Record success
  │         Update stats
  │         Reset circuit breaker
  │         Return result
  │
  └─ No ──> Is retryable error?
             ├─ Yes ──> CircuitBreaker.call()
             │          ├─ OPEN: Fail fast
             │          └─ CLOSED/HALF_OPEN: Retry
             │          Exponential backoff
             │          Try different proxy
             │
             └─ No ──> Mark proxy unhealthy
                       Record failure
                       Select fallback proxy
                       Return error
```

## Configuration Architecture

**Configuration Hierarchy:**

```
1. Defaults (hardcoded in source)
          ▼
2. TOML file (~/.proxywhirl/config.toml)
          ▼
3. Environment variables (PROXYWHIRL_*)
          ▼
4. Runtime kwargs (highest priority)
```

**Main Config Options:**

```python
class ProxyConfiguration:
    # Pool settings
    rotation_strategy: str
    health_check_interval: int
    max_pool_size: int
    
    # Retry policy
    max_retries: int
    retry_delay_ms: int
    exponential_backoff: bool
    
    # Circuit breaker
    failure_threshold: int
    recovery_timeout: int
    
    # Rate limiting
    requests_per_second: float
    burst_size: int
    
    # Caching
    cache_ttl: int
    cache_max_size: int
    cache_encryption: bool
    
    # Storage
    storage_path: str
    storage_backend: str
```

## Extension Points

### 1. Custom Rotation Strategy
```python
class CustomStrategy(RotationStrategy):
    def select(self, pool, context):
        # Your logic here
        return selected_proxy
```

### 2. Custom Parser
```python
class CustomParser(ProxyParser):
    def parse(self, data: str) -> List[Proxy]:
        # Your parsing logic
        return proxies
```

### 3. Custom Storage
```python
class CustomStorage(Storage):
    def save(self, pool): pass
    def load(self): pass
    # ...
```

### 4. Custom Health Check
```python
def custom_health_check(proxy: Proxy) -> HealthStatus:
    # Your health check logic
    return status
```

## Performance Considerations

### Concurrency Model
- **Sync**: Blocking operations, GIL-bound
- **Async**: Non-blocking operations, CPU-efficient
- **Thread Pool**: For blocking I/O in async context

### Optimization Strategies
1. **Caching**: Reduce health checks
2. **Connection Pooling**: Reuse HTTP connections
3. **Rate Limiting**: Prevent overwhelming proxies
4. **Circuit Breaking**: Fail fast on bad proxies
5. **Lazy Loading**: Load proxies on demand
6. **Batch Operations**: Process multiple proxies at once

### Scaling Guidelines
- **Single Server**: Up to 10k requests/sec
- **Multi-threaded**: 50k requests/sec
- **Async (Asyncio)**: 100k+ requests/sec
- **Distributed**: Multiple instances with shared storage

## Security Architecture

### Credential Management
```
Raw Credentials
      │
      ▼
Encrypt with Fernet
      │
      ▼
Store encrypted in DB/file
      │
      ▼
On use: Decrypt only in memory
      │
      ▼
Clear after use (SecretStr)
```

### Input Validation
- URL parsing (no injection)
- Regex validation (ReDoS prevention)
- Type checking (Pydantic)
- Range validation (bounds checking)

### Network Security
- TLS/SSL for API endpoints
- HTTPS only for proxy fetching
- Authentication tokens (API key)
- CORS protection

## Observability

### Logging Levels
- `DEBUG`: Detailed flow information
- `INFO`: Notable events (health changes)
- `WARNING`: Degraded performance
- `ERROR`: Failures and exceptions

### Metrics Collection
```python
class MetricsCollector:
    - request_count
    - error_rate
    - latency_p50/p95/p99
    - cache_hit_rate
    - proxy_health_distribution
    - circuit_breaker_state_changes
```

### Health Dashboard (TUI)
```
┌─ ProxyWhirl Status ──────────────────┐
│ Pool: 1,250 proxies                  │
│ Healthy: 980 (78%)                   │
│ Requests: 45.2k/min                  │
│ Avg Latency: 234ms                   │
│ Cache Hit Rate: 87%                  │
│ Circuit Breaker: CLOSED              │
└──────────────────────────────────────┘
```

## Integration Points

### API Server
- FastAPI routes at `/api/*`
- Authentication via API key
- Rate limiting per client
- Prometheus metrics export

### CLI
```bash
proxywhirl list      # Show pool
proxywhirl fetch     # Add sources
proxywhirl validate  # Test proxies
proxywhirl stats     # Show metrics
```

### MCP Server
- Claude integration
- Model context protocol
- Tool-based interface
- Async-first design

## Module Dependencies

```
├── models/           → Pydantic data classes
├── strategies/       → RotationStrategy implementations
├── rotator/          → ProxyWhirl, AsyncProxyWhirl
├── storage.py        → Storage backends
├── fetchers.py       → ProxyFetcher, parsers
├── cache/            → CacheManager
├── circuit_breaker/  → CircuitBreaker
├── retry/            → RetryExecutor
├── rate_limiting/    → RateLimiter
├── health/           → HealthMonitor
├── api/              → FastAPI routes
├── cli.py            → Typer CLI
├── tui.py            → Textual dashboard
├── browser.py        → Playwright rendering
└── utils.py          → Helper functions
```

## Deployment Architecture

### Single Instance
```
┌─────────────────┐
│  Application    │
├─────────────────┤
│  ProxyWhirl     │
├─────────────────┤
│ SQLite + Memory │
└─────────────────┘
```

### Multi-Instance
```
┌──────────────┐
│   Load       │  Distributes traffic
│ Balancer     │
└───┬────┬─────┘
    │    │
    ▼    ▼
┌────────────────┐  ┌────────────────┐
│ ProxyWhirl #1  │  │ ProxyWhirl #2  │
└────────────────┘  └────────────────┘
         │                │
         └────┬───────────┘
              ▼
         ┌──────────────┐
         │ Redis Cache  │
         ├──────────────┤
         │ PostgreSQL   │
         └──────────────┘
```

### Kubernetes Deployment
```
┌─────────────────────────────────┐
│  Kubernetes Cluster             │
├─────────────────────────────────┤
│ Deployment (proxywhirl-app)     │
│ ├─ Pod Replica 1               │
│ ├─ Pod Replica 2               │
│ └─ Pod Replica 3               │
├─────────────────────────────────┤
│ Service (ClusterIP/LoadBalancer)│
├─────────────────────────────────┤
│ ConfigMap (config.toml)         │
│ Secret (API keys)               │
├─────────────────────────────────┤
│ PVC (Redis, PostgreSQL)         │
└─────────────────────────────────┘
```

## Future Architecture Enhancements

1. **Distributed Consensus**: Multi-instance health synchronization
2. **Event Streaming**: Kafka for proxy events
3. **ML-based Selection**: ML model for strategy selection
4. **GraphQL API**: In addition to REST
5. **WebSocket Support**: Real-time proxy updates
6. **gRPC Interface**: High-performance RPC
7. **Plugin System**: Dynamic strategy loading
8. **Multi-tenancy**: Isolated pools per tenant

