# ProxyWhirl Architecture Guide

## System Design

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Application                          │
├─────────────────────────────────────────────────────────────────┤
│                   ProxyWhirl Interface Layer                      │
│              (ProxyWhirl / AsyncProxyWhirl)                      │
├─────────────────────────────────────────────────────────────────┤
│                    Rotation Strategy Layer                        │
│  (RoundRobin, Weighted, PerformanceBased, GeoTargeted, etc.)   │
├─────────────────────────────────────────────────────────────────┤
│                  Resilience & Reliability                         │
│  (CircuitBreaker, Retry, RateLimit, CacheManager)              │
├─────────────────────────────────────────────────────────────────┤
│                    Health & Validation Layer                      │
│            (HealthMonitor, ProxyValidator)                       │
├─────────────────────────────────────────────────────────────────┤
│                    Persistence & Storage                          │
│         (SQLiteStorage, FileStorage, Cache)                      │
├─────────────────────────────────────────────────────────────────┤
│                   Proxy Data Sources                              │
│          (HTTP, WebSocket, Browser, Premium APIs)               │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Rotator Layer
- **ProxyWhirl**: Synchronous rotator
- **AsyncProxyWhirl**: Asynchronous rotator
- Handles proxy selection, refresh, and lifecycle

### 2. Strategy Layer
Nine rotation strategies:
- RoundRobinStrategy
- WeightedRoundRobinStrategy
- PerformanceBasedStrategy
- GeoTargetedStrategy
- LeastConnectionsStrategy
- RandomStrategy
- ConsistentHashingStrategy
- AntiPatternStrategy
- ResilientStrategy

### 3. Resilience Layer
- **CircuitBreaker**: Prevents cascading failures
- **RetryExecutor**: Handles transient failures
- **RateLimiter**: Controls request rate
- **CacheManager**: Multi-tier caching

### 4. Validation Layer
- **ProxyValidator**: Validates proxy functionality
- **HealthMonitor**: Tracks proxy health
- Supports custom health checks

### 5. Data Layer
- **SQLiteStorage**: Primary persistent storage
- **FileStorage**: File-based storage
- **CacheManager**: In-memory caching
- **DataExporter**: Export to JSON/CSV/YAML

### 6. Source Layer
- **ProxyFetcher**: Fetches proxies from sources
- **BrowserRenderer**: JavaScript-rendered sources
- Multiple source parsers (JSON, CSV, PlainText, HTMLTable)
- ~150+ predefined sources

## Key Design Patterns

### Strategy Pattern
```python
# Plugin architecture for rotation strategies
class RotationStrategy(Protocol):
    def select(self, proxies: List[Proxy]) -> Proxy: ...
    def get_weight(self, proxy: Proxy) -> float: ...
    def on_success(self, proxy: Proxy) -> None: ...
    def on_failure(self, proxy: Proxy) -> None: ...
```

### Circuit Breaker Pattern
```
CLOSED → (failures > threshold) → OPEN
  ↓                                 ↓
  ← (timeout) → HALF_OPEN ← (success)
```

### Multi-Tier Cache Pattern
```
L1: In-Memory (fast, limited)
    ↓ (miss)
L2: Compressed Disk (medium, larger)
    ↓ (miss)
L3: Source Fetch (slow, unlimited)
```

### Async/Await Pattern
- Fully async-compatible for high concurrency
- Context managers for resource management
- Proper exception handling and cleanup

## Data Models

### Proxy Model
```python
class Proxy:
    url: str
    protocol: str
    country: Optional[str]
    is_residential: bool
    last_checked: Optional[datetime]
    health_status: HealthStatus
```

### ProxyPool Model
```python
class ProxyPool:
    proxies: List[Proxy]
    stats: PoolStatistics
    filters: Optional[Dict]
    last_updated: datetime
```

### Configuration Model
```python
class ProxyConfiguration:
    sources: List[str]
    strategy_config: StrategyConfig
    cache_config: CacheConfig
    validation_level: str
    max_retries: int
    timeout_seconds: float
```

## Request Flow

```
User Request
    ↓
[ProxyWhirl/AsyncProxyWhirl]
    ↓
[RateLimiter] - Check rate limit
    ↓
[SelectionStrategy] - Select proxy from pool
    ↓
[CircuitBreaker] - Check circuit state
    ↓
[ProxyValidator] - Validate before use
    ↓
[Return Proxy to User]
    ↓
[on_success/on_failure] - Update metrics
```

## Concurrency Model

### Synchronous (ProxyWhirl)
- Thread-safe using locks
- Blocking operations
- Suitable for single-threaded or GIL-bound apps

### Asynchronous (AsyncProxyWhirl)
- Fully non-blocking
- asyncio-compatible
- Suitable for web frameworks, high concurrency
- Task-safe with no race conditions

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Get proxy (cached) | <1ms | L1 cache hit |
| Get proxy (L2) | 1-10ms | Decompressed from disk |
| Get proxy (fetch) | 100-500ms | Full source fetch |
| Validate proxy | 5-30s | Depends on timeout |
| Health check all | 30s-5m | Batch validation |

## Storage Architecture

### SQLite Storage
- `proxies` table: Proxy data
- `proxy_sources` table: Source metadata
- `health_checks` table: Health history
- Indexed for fast queries

### File Storage
- YAML/JSON serialization
- Suitable for small deployments
- Not suitable for large-scale

### Cache Storage
- L1: Memory (dict)
- L2: Compressed disk (zstd)
- LRU eviction policy

## Extension Points

### Custom Strategies
```python
class CustomStrategy(RotationStrategy):
    def select(self, proxies: List[Proxy]) -> Proxy:
        # Custom selection logic
        return proxies[0]
```

### Custom Health Checks
```python
class CustomHealthCheck(HealthCheck):
    async def check(self, proxy: Proxy) -> HealthStatus:
        # Custom validation logic
        return HealthStatus.HEALTHY
```

### Custom Sources
```python
# Register custom source
from proxywhirl import register_source

register_source(
    name='my_source',
    url='https://example.com/proxies',
    parser='json'
)
```

## Deployment Architectures

### Single Instance
- One ProxyWhirl instance per process
- Shared SQLite database
- Suitable for: Scripts, CLI tools, small services

### Service Cluster
- Multiple instances with shared database
- Distributed cache coherency
- Suitable for: Microservices, high availability

### Kubernetes
- Helm chart for easy deployment
- StatefulSet for data persistence
- Horizontal scaling with service mesh

## Monitoring & Observability

### Metrics
- Prometheus-compatible metrics
- OpenTelemetry export support
- Performance monitoring

### Logging
- Structured logging with Loguru
- Multiple log levels (DEBUG, INFO, WARNING, ERROR)
- Log aggregation support

### Tracing
- Jaeger integration
- Request tracing across components
- Distributed tracing support

## Security Architecture

### Credential Management
- Encrypted storage of proxy credentials
- Secret key derivation
- No hardcoded secrets

### Input Validation
- URL validation and parsing
- ReDoS-safe regex utilities
- Proxy format validation

### Rate Limiting
- Token bucket algorithm
- Per-source rate limits
- User-configurable

## Failure Scenarios

### Proxy Failures
- Automatic fallback to next proxy
- Exponential backoff retry
- Circuit breaker isolation

### Source Failures
- Resilient fetching with retries
- Fallback sources
- Graceful degradation

### Storage Failures
- In-memory cache fallback
- Graceful error handling
- Data persistence recovery

