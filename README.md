# ProxyWhirl 🌀

**Advanced Python Proxy Rotation Library**

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

ProxyWhirl is a production-ready Python library for intelligent proxy rotation with multiple strategies, authentication support, and runtime pool management.

## ✨ Features

### Core Features (v0.1.0)

- 🔄 **Smart Rotation**: Round-robin, random, weighted, and least-used strategies
- 🔐 **Authentication**: Built-in credential handling for authenticated proxies
- 🎯 **Runtime Management**: Add/remove proxies without restarting
- 📊 **Pool Statistics**: Track health, success rates, and performance metrics
- 🌐 **Built-in Proxy Sources**: 16+ pre-configured free proxy APIs and lists
- 📡 **Auto-Fetch**: Fetch proxies from JSON, CSV, plain text, and HTML sources
- ⚡ **High Performance**: <50ms overhead, tested with concurrent requests
- 🛡️ **Resilient**: Automatic failover with retry logic using tenacity
- 🔒 **Secure**: Credential protection with SecretStr, never logged
- 🧪 **Well-Tested**: 357 tests passing, 88% code coverage
- 📦 **Type-Safe**: Full type hints with py.typed marker
- 🔧 **Production-Ready**: Context manager support, structured logging

### Validation & Storage (v0.2.0)

- ✅ **Multi-Level Validation**: BASIC (connectivity), STANDARD (HTTP), FULL (anonymity)
- ✅ **Anonymity Detection**: Detect transparent/anonymous/elite proxies
- ✅ **Batch Validation**: Parallel validation with concurrency control (100+ proxies/sec)
- ✅ **File Storage**: JSON persistence with atomic writes and encryption
- ✅ **SQLite Storage**: Async backend with advanced querying and indexing
- ✅ **Query Support**: Filter by source, health status, protocol
- ✅ **Encryption**: Fernet-based credential encryption at rest
- ✅ **Health Monitoring**: Continuous background health checks with auto-eviction
- ✅ **TTL Expiration**: Automatic proxy expiration based on time-to-live
- ✅ **Browser Rendering**: JavaScript-heavy sites support via Playwright (optional)

## 📦 Installation

```bash
# Basic installation
pip install proxywhirl

# With validation and storage support (Phase 2)
pip install "proxywhirl[storage]"

# With browser rendering support (Phase 2.5, requires Playwright)
pip install "proxywhirl[js]"
playwright install chromium

# All features
pip install "proxywhirl[storage,js]"
playwright install chromium

# Development installation with uv (faster)
uv pip install proxywhirl

# Or clone and install from source
git clone https://github.com/wyattowalsh/proxywhirl.git
cd proxywhirl
uv sync
```

**Phase 2 Dependencies** (included with `[storage]` extra):

- `cryptography` - File encryption support
- `sqlmodel` - SQLite ORM with Pydantic integration
- `aiosqlite` - Async SQLite operations
- `greenlet` - SQLAlchemy async compatibility

**Browser Rendering** (included with `[js]` extra):

- `playwright` - Browser automation for JavaScript rendering

## 📝 Structured Logging

ProxyWhirl includes a comprehensive structured logging system with support for JSON and logfmt formats, multiple output destinations, rotation, and contextual metadata.

### Quick Logging Setup

```python
from proxywhirl import LogConfiguration, LogHandlerConfig, LogHandlerType, apply_logging_configuration

# JSON structured logging to console
config = LogConfiguration(
    level="INFO",
    handlers=[
        LogHandlerConfig(type=LogHandlerType.CONSOLE, format="json")
    ]
)
apply_logging_configuration(config)
```

### Multiple Output Destinations

```python
from proxywhirl import LogConfiguration, LogHandlerConfig, LogHandlerType

config = LogConfiguration(
    level="DEBUG",
    handlers=[
        # Console output with JSON
        LogHandlerConfig(
            type=LogHandlerType.CONSOLE,
            level="INFO",
            format="json"
        ),
        # File output with rotation
        LogHandlerConfig(
            type=LogHandlerType.FILE,
            path="logs/app.log",
            level="DEBUG",
            format="logfmt",
            rotation="100 MB",
            retention="7 days"
        ),
    ]
)
apply_logging_configuration(config)
```

### Contextual Logging

Attach metadata to logs for correlation and debugging:

```python
from proxywhirl import LogContext, bind_context
from loguru import logger

# Using context manager
with LogContext(request_id="req-123", operation="proxy_selection"):
    logger.info("Selecting proxy")
    # Logs include request_id and operation automatically

# Using bind_context
log = bind_context(strategy="weighted", proxy_url="http://proxy1.example.com:8080")
log.info("Proxy selected successfully")
```

### Features

- **Structured Formats**: JSON and logfmt output
- **Multiple Destinations**: Console, file, syslog, HTTP remote logging
- **Automatic Rotation**: Size-based and time-based log rotation
- **Retention Policies**: Automatic cleanup of old log files
- **Credential Redaction**: Automatic redaction of sensitive data
- **Async Logging**: Non-blocking logging with bounded queues
- **Sampling & Filtering**: Reduce log volume with sampling and module filtering
- **Runtime Reconfiguration**: Change log levels without restart

See `examples/structured_logging_demo.py` for comprehensive examples.

## 🚀 Quick Start

### Basic Usage

```python
from proxywhirl import ProxyRotator, Proxy

# Initialize with a list of proxy URLs
with ProxyRotator(proxies=[
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080",
]) as rotator:
    response = rotator.get("https://httpbin.org/ip")
    print(response.json())
```

### Authenticated Proxies

```python
from proxywhirl import ProxyRotator, Proxy
from pydantic import SecretStr

# Create proxies with authentication
proxies = [
    Proxy(
        url="http://proxy1.example.com:8080",
        username="user1",
        password=SecretStr("pass1")
    ),
    Proxy(
        url="http://proxy2.example.com:8080",
        username="user2",
        password=SecretStr("pass2")
    ),
]

with ProxyRotator(proxies=proxies) as rotator:
    response = rotator.get("https://api.example.com")
```

### Custom Rotation Strategy

```python
from proxywhirl import ProxyRotator

# Use string-based strategy configuration
rotator = ProxyRotator(
    proxies=["http://proxy1.com:8080", "http://proxy2.com:8080"],
    strategy="weighted"  # or "random", "least-used", "round-robin"
)

# Make requests
response = rotator.get("https://example.com")
```

### Runtime Pool Management

```python
from proxywhirl import ProxyRotator

rotator = ProxyRotator()

# Add proxies at runtime
rotator.add_proxy("http://proxy1.example.com:8080")
rotator.add_proxy("http://proxy2.example.com:8080")

# Get pool statistics
stats = rotator.get_pool_stats()
print(f"Total proxies: {stats['total_proxies']}")
print(f"Healthy: {stats['healthy_proxies']}")
print(f"Success rate: {stats['average_success_rate']:.2%}")

# Remove unhealthy proxies
removed = rotator.clear_unhealthy_proxies()
print(f"Removed {removed} unhealthy proxies")
```

### Auto-Fetch from Built-in Sources

ProxyWhirl includes 16+ pre-configured proxy sources for easy bootstrapping:

```python
from proxywhirl import ProxyRotator, ProxyFetcher, Proxy
from proxywhirl import RECOMMENDED_SOURCES, ALL_HTTP_SOURCES
from proxywhirl.models import ProxySource
import asyncio

async def main():
    # Fetch from recommended sources (fast, reliable)
    fetcher = ProxyFetcher(sources=RECOMMENDED_SOURCES)
    proxy_dicts = await fetcher.fetch_all(validate=True)
    
    # Create rotator with fetched proxies
    rotator = ProxyRotator()
    for proxy_dict in proxy_dicts:
        proxy = Proxy(
            url=proxy_dict["url"],
            source=ProxySource.FETCHED  # Tag as fetched
        )
        rotator.add_proxy(proxy)
    
    # Mix with your own proxies
    rotator.add_proxy(Proxy(
        url="http://my-premium-proxy.com:8080",
        source=ProxySource.USER,  # Tag as user-provided
        username="myuser",
        password="mypass"
    ))
    
    # Get source breakdown
    stats = rotator.get_statistics()
    print(f"User proxies: {stats['source_breakdown']['USER']}")
    print(f"Fetched proxies: {stats['source_breakdown']['FETCHED']}")
    
    # Use rotator
    response = rotator.get("https://httpbin.org/ip")
    print(response.json())

asyncio.run(main())
```

### Proxy Validation (Phase 2)

Validate proxies before using them with configurable validation levels:

```python
from proxywhirl.models import Proxy, ValidationLevel, ProxyValidator
import asyncio

async def main():
    proxies = [
        Proxy(url="http://proxy1.example.com:8080"),
        Proxy(url="http://proxy2.example.com:8080"),
        Proxy(url="http://proxy3.example.com:8080"),
    ]
    
    # BASIC: Quick connectivity check (~100ms)
    validator = ProxyValidator(level=ValidationLevel.BASIC)
    validated = await validator.validate_batch(proxies)
    
    # STANDARD: TCP + HTTP validation (~500ms)
    validator = ProxyValidator(level=ValidationLevel.STANDARD)
    validated = await validator.validate_batch(proxies)
    
    # FULL: TCP + HTTP + anonymity detection (~1s)
    validator = ProxyValidator(level=ValidationLevel.FULL)
    validated = await validator.validate_batch(proxies, max_concurrent=5)
    
    # Filter healthy proxies
    healthy = [p for p in validated if p.health_status == "healthy"]
    print(f"{len(healthy)}/{len(proxies)} proxies are healthy")
    
    # Check anonymity level
    for proxy in validated:
        if proxy.anonymity_level:
            print(f"{proxy.url}: {proxy.anonymity_level}")

asyncio.run(main())
```

### File Storage with Encryption (Phase 2)

Persist proxies to disk with optional credential encryption:

```python
from proxywhirl.storage import FileStorage
from proxywhirl.models import Proxy
from cryptography.fernet import Fernet
import asyncio

async def main():
    # Generate encryption key (save this securely!)
    key = Fernet.generate_key()
    
    # Create storage with encryption
    storage = FileStorage("proxies.json", encryption_key=key)
    
    # Proxies with credentials
    proxies = [
        Proxy(url="http://proxy.com:8080", username="user", password="secret123"),
    ]
    
    # Save - credentials encrypted at rest
    await storage.save(proxies)
    
    # Load - automatic decryption
    loaded = await storage.load()
    print(loaded[0].username.get_secret_value())  # "user"

asyncio.run(main())
```

### SQLite Storage (Phase 2)

High-performance SQLite backend with advanced querying:

```python
from proxywhirl.storage import SQLiteStorage
from proxywhirl.models import Proxy
import asyncio

async def main():
    storage = SQLiteStorage("proxies.db")
    await storage.initialize()
    
    # Save proxies
    proxies = [
        Proxy(url="http://proxy1.com:8080", source="user"),
        Proxy(url="http://proxy2.com:8080", source="fetched"),
    ]
    await storage.save(proxies)
    
    # Query by source
    user_proxies = await storage.query(source="user")
    print(f"Found {len(user_proxies)} user proxies")
    
    # Query by health status
    healthy = await storage.query(health_status="healthy")
    
    # Load all proxies
    all_proxies = await storage.load()
    
    # Delete specific proxy
    await storage.delete("http://proxy1.com:8080")
    
    await storage.close()

asyncio.run(main())
```

### Health Monitoring (Phase 2.4)

Continuous background health monitoring with automatic eviction:

```python
import asyncio
from proxywhirl.models import HealthMonitor, Proxy, ProxyPool

async def main():
    # Create pool with proxies
    pool = ProxyPool(name="monitored_pool")
    pool.add_proxy(Proxy(url="http://proxy1.com:8080"))
    pool.add_proxy(Proxy(url="http://proxy2.com:8080"))
    
    # Create monitor with custom settings
    monitor = HealthMonitor(
        pool=pool,
        check_interval=30,  # Check every 30 seconds
        failure_threshold=5  # Evict after 5 consecutive failures
    )
    
    # Start background monitoring
    await monitor.start()
    
    # Use pool normally - dead proxies are evicted automatically
    # ... your application code ...
    
    # Check monitoring status
    status = monitor.get_status()
    print(f"Running: {status['is_running']}")
    print(f"Healthy proxies: {status['healthy_proxies']}/{status['total_proxies']}")
    print(f"Uptime: {status['uptime_seconds']}s")
    
    # Stop monitoring
    await monitor.stop()

asyncio.run(main())
```

### TTL Expiration (Phase 2.6)

Automatic proxy expiration based on time-to-live:

```python
from proxywhirl.models import Proxy, ProxyPool
from datetime import datetime, timedelta, timezone

# Proxy with 1-hour TTL
proxy1 = Proxy(url="http://proxy.com:8080", ttl=3600)

# Proxy with explicit expiration
tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
proxy2 = Proxy(url="http://proxy2.com:8080", expires_at=tomorrow)

# Permanent proxy (no TTL)
proxy3 = Proxy(url="http://permanent.com:8080")

# Pool automatically filters expired proxies
pool = ProxyPool(name="ttl_pool")
pool.add_proxy(proxy1)
pool.add_proxy(proxy2)
pool.add_proxy(proxy3)

# Check expiration
if proxy1.is_expired:
    print("Proxy expired!")

# Clean up expired proxies
removed = pool.clear_expired()
print(f"Removed {removed} expired proxies")
```

### Health Monitoring (Phase 2.4)

Continuous background health checks with automatic eviction of failing proxies:

```python
from proxywhirl.models import HealthMonitor, ProxyPool, Proxy
import asyncio

async def main():
    # Create pool with proxies
    pool = ProxyPool(name="monitored_pool")
    pool.add_proxy(Proxy(url="http://proxy1.example.com:8080"))
    pool.add_proxy(Proxy(url="http://proxy2.example.com:8080"))
    
    # Start health monitoring
    monitor = HealthMonitor(
        pool=pool,
        check_interval=60,      # Check every 60 seconds
        failure_threshold=3     # Evict after 3 consecutive failures
    )
    
    await monitor.start()       # Runs in background
    
    # Your application runs here...
    # Monitor automatically evicts unhealthy proxies
    
    await monitor.stop()        # Clean shutdown

asyncio.run(main())
```

### Browser Rendering (Phase 2.5)

Fetch proxies from JavaScript-heavy websites that require browser execution:

```python
from proxywhirl.browser import BrowserRenderer, BrowserConfig, WaitStrategy
from proxywhirl.fetchers import ProxyFetcher, ProxySourceConfig
from proxywhirl.models import RenderMode
import asyncio

async def main():
    # Option 1: Use BrowserRenderer directly
    async with BrowserRenderer() as renderer:
        html = await renderer.render("https://js-heavy-site.com/proxies")
        # Parse HTML manually
    
    # Option 2: Use with ProxyFetcher
    fetcher = ProxyFetcher()
    source = ProxySourceConfig(
        url="https://js-heavy-site.com/proxies",
        format="json",
        render_mode=RenderMode.BROWSER  # Enable browser rendering
    )
    proxies = await fetcher.fetch_from_source(source)
    
    # Option 3: Custom browser configuration
    config = BrowserConfig(
        headless=True,
        browser_type="chromium",
        timeout=30,
        wait_strategy=WaitStrategy.NETWORK_IDLE
    )
    async with BrowserRenderer(config=config) as renderer:
        html = await renderer.render("https://example.com/proxies")

asyncio.run(main())
```

**Installation for browser rendering:**
```bash
pip install "proxywhirl[js]"
playwright install chromium
```

**Available Source Collections:**

- `RECOMMENDED_SOURCES` - Best quality/speed (4 sources)
- `ALL_HTTP_SOURCES` - All HTTP/HTTPS proxies (6 sources)
- `ALL_SOCKS4_SOURCES` - All SOCKS4 proxies (4 sources)
- `ALL_SOCKS5_SOURCES` - All SOCKS5 proxies (5 sources)
- `ALL_SOURCES` - Everything (15 sources)
- `API_SOURCES` - API-based sources only (6 sources)

**Individual Sources:**

```python
from proxywhirl import (
    FREE_PROXY_LIST,
    PROXY_SCRAPE_HTTP,
    GEONODE_HTTP,
    GITHUB_MONOSANS_HTTP,
    # ... and 12 more
)
```

See `proxywhirl/sources.py` for the complete list.

## 📚 Documentation

See [specs/001-core-python-package/](specs/001-core-python-package/) for complete documentation:

- **[Quickstart Guide](specs/001-core-python-package/quickstart.md)**: Get started in 5 minutes
- **[Feature Spec](specs/001-core-python-package/spec.md)**: Full requirements and user stories
- **[Data Model](specs/001-core-python-package/data-model.md)**: Entity definitions
- **[API Contracts](specs/001-core-python-package/contracts/)**: Detailed API reference
- **[Research](specs/001-core-python-package/research.md)**: Technical decisions and optimizations
- **[Implementation Plan](specs/001-core-python-package/plan.md)**: Development roadmap

## 🎯 Intelligent Rotation Strategies (v0.2.0)

ProxyWhirl supports 7 advanced rotation strategies with comprehensive metadata tracking, performance monitoring, and intelligent selection. All strategies support health checking, failover, and can be hot-swapped at runtime.

### Available Strategies

#### 1. Round-Robin Strategy
**Use Case**: Fair distribution, predictable rotation  
**Performance**: ~3μs per selection  
**Features**: Perfect distribution (±1 request variance), automatic health filtering

```python
from proxywhirl import ProxyRotator

rotator = ProxyRotator(proxies=proxies, strategy="round-robin")
# Sequential: proxy0 → proxy1 → proxy2 → proxy0 → ...
```

#### 2. Random Strategy
**Use Case**: Unpredictable patterns, load testing  
**Performance**: ~7μs per selection  
**Features**: Uniform distribution (~20% variance over 1000 requests)

```python
rotator = ProxyRotator(proxies=proxies, strategy="random")
# Random selection from healthy proxies
```

#### 3. Weighted Strategy
**Use Case**: Prefer high-performing proxies  
**Performance**: ~9μs per selection  
**Features**: Success-rate based weights, automatic adjustment

```python
from proxywhirl.strategies import WeightedStrategy, StrategyConfig

config = StrategyConfig(
    weights={"proxy1": 0.5, "proxy2": 0.3, "proxy3": 0.2}
)
rotator = ProxyRotator(proxies=proxies, strategy=WeightedStrategy(config=config))
# Higher success rate = higher selection probability
```

#### 4. Least-Used Strategy
**Use Case**: Perfect load balancing  
**Performance**: ~3μs per selection  
**Features**: Tracks request counts, evens out load automatically

```python
rotator = ProxyRotator(proxies=proxies, strategy="least-used")
# Always selects proxy with fewest completed requests
```

#### 5. Performance-Based Strategy
**Use Case**: Minimize latency, optimize response times  
**Performance**: ~5μs per selection  
**Features**: EMA tracking, 15-25% faster than round-robin

```python
from proxywhirl.strategies import PerformanceBasedStrategy, StrategyConfig

config = StrategyConfig(ema_alpha=0.2)  # Smoothing factor
rotator = ProxyRotator(
    proxies=proxies, 
    strategy=PerformanceBasedStrategy(config=config)
)
# Prefers proxies with lower response times
```

#### 6. Session Persistence Strategy
**Use Case**: Maintain same proxy for related requests (cookies, sessions)  
**Performance**: ~3μs per selection  
**Features**: 99.9% same-proxy guarantee, automatic failover, configurable TTL

```python
from proxywhirl.strategies import SessionPersistenceStrategy, SelectionContext
from proxywhirl import ProxyRotator

rotator = ProxyRotator(proxies=proxies, strategy=SessionPersistenceStrategy())

# Create session
context = SelectionContext(session_id="user-123")
response1 = rotator.get("https://example.com", context=context)
response2 = rotator.get("https://example.com/page2", context=context)
# Both requests use the same proxy
```

#### 7. Geo-Targeted Strategy
**Use Case**: Region-specific content access  
**Performance**: ~5μs per selection  
**Features**: Country/region filtering, automatic fallback

```python
from proxywhirl.strategies import GeoTargetedStrategy, SelectionContext
from proxywhirl.models import Proxy

# Create proxies with geo-location data
proxies = [
    Proxy(url="http://us-proxy.com:8080", country_code="US", region="California"),
    Proxy(url="http://uk-proxy.com:8080", country_code="GB", region="London"),
    Proxy(url="http://jp-proxy.com:8080", country_code="JP", region="Tokyo"),
]

rotator = ProxyRotator(proxies=proxies, strategy=GeoTargetedStrategy())

# Target specific country
context = SelectionContext(target_country="US")
response = rotator.get("https://us-only-content.com", context=context)

# Target specific region
context = SelectionContext(target_country="GB", target_region="London")
response = rotator.get("https://uk-content.com", context=context)
```

### Advanced Features

#### Strategy Composition
Combine multiple strategies for complex selection logic:

```python
from proxywhirl.strategies import CompositeStrategy, GeoTargetedStrategy, PerformanceBasedStrategy

# First filter by geo-location, then select best performer
strategy = CompositeStrategy(strategies=[
    GeoTargetedStrategy(),
    PerformanceBasedStrategy()
])

rotator = ProxyRotator(proxies=proxies, strategy=strategy)
```

#### Hot-Swapping Strategies
Switch strategies at runtime without dropping requests:

```python
from proxywhirl.strategies import RoundRobinStrategy, PerformanceBasedStrategy

rotator = ProxyRotator(proxies=proxies, strategy="round-robin")

# Make some requests...
for _ in range(100):
    rotator.get("https://example.com")

# Switch to performance-based for remaining requests
rotator.set_strategy(PerformanceBasedStrategy())
# < 100ms transition, no dropped requests
```

#### Custom Strategy Plugin
Create your own rotation strategy:

```python
from proxywhirl.strategies import RotationStrategy, StrategyRegistry
from proxywhirl.models import Proxy, ProxyPool, SelectionContext
from typing import Optional

class MyCustomStrategy(RotationStrategy):
    """Custom strategy implementation."""
    
    def select(self, pool: ProxyPool, context: Optional[SelectionContext] = None) -> Proxy:
        # Your selection logic here
        healthy_proxies = pool.get_healthy_proxies()
        return healthy_proxies[0]  # Example: always select first
    
    def record_result(self, proxy: Proxy, success: bool, response_time_ms: Optional[float] = None) -> None:
        # Track results for adaptive behavior
        if success:
            proxy.complete_request(success=True, response_time_ms=response_time_ms)

# Register and use
StrategyRegistry.register("my-custom", MyCustomStrategy)
rotator = ProxyRotator(proxies=proxies, strategy="my-custom")
```

### Performance Comparison

All strategies tested with 10,000 concurrent selections:

| Strategy | Selection Time | Use Case | Distribution |
|----------|---------------|----------|--------------|
| Round-Robin | 2.8-5.6μs | Fair rotation | Perfect (±1 request) |
| Random | 6.7-14μs | Unpredictable | Uniform (~20% variance) |
| Weighted | 8.5-15μs | Prefer best | Success-rate weighted |
| Least-Used | 2.8-17μs | Load balance | Perfect (±1 request) |
| Performance-Based | 4.5-26μs | Minimize latency | EMA-weighted |
| Session Persistence | 3.2-12μs | Sticky sessions | 99.9% same-proxy |
| Geo-Targeted | 5.1-18μs | Region-specific | 100% correct region |

**All strategies exceed performance targets**: <5ms overhead (5000μs target vs 2.8-26μs actual = 192-1785x faster)

### Metadata Tracking

All strategies automatically track comprehensive proxy metadata:

```python
from proxywhirl import ProxyRotator

rotator = ProxyRotator(proxies=proxies, strategy="performance-based")

# Make requests
for _ in range(100):
    response = rotator.get("https://httpbin.org/delay/1")

# Check proxy statistics
for proxy in rotator.pool.get_all_proxies():
    print(f"Proxy: {proxy.url}")
    print(f"  Requests: {proxy.requests_completed}")
    print(f"  Success rate: {proxy.success_rate:.2%}")
    print(f"  Avg response time: {proxy.ema_response_time_ms:.1f}ms")
    print(f"  Health: {proxy.health_status}")
```

### Configuration

Strategies support flexible configuration via `StrategyConfig`:

```python
from proxywhirl.strategies import StrategyConfig

config = StrategyConfig(
    # Weighted strategy: custom weights
    weights={"proxy1": 0.5, "proxy2": 0.3, "proxy3": 0.2},
    
    # Performance-based: EMA smoothing factor (0-1)
    ema_alpha=0.2,
    
    # Session persistence: TTL in seconds
    session_ttl=3600,
    
    # Geo-targeted: fallback behavior
    geo_fallback_enabled=True,
    geo_secondary_strategy="round-robin"
)
```

### Examples

See [examples/rotation_strategies_example.py](examples/rotation_strategies_example.py) for complete usage examples of all strategies, composition, hot-swapping, and custom plugins.

## 🛣️ Roadmap

### ✅ Phase 1 - Core Package (v0.1.0) - **COMPLETE**

- Core proxy rotation with multiple strategies (round-robin, random, weighted, least-used)
- Authentication support with SecretStr credential protection
- Runtime pool management (add/remove/update proxies)
- Auto-fetch proxies from 16+ pre-configured sources
- Multi-format parsing (JSON, CSV, plain text, HTML tables)
- Source tagging (USER vs FETCHED) and statistics
- Advanced error handling with metadata and retry recommendations
- Comprehensive test coverage (300 tests, 88% coverage)

### ✅ Phase 2 - Validation & Storage (v0.2.0) - **COMPLETE**

- ✅ **Multi-level validation**: BASIC (connectivity), STANDARD (HTTP), FULL (anonymity detection)
- ✅ **File storage**: JSON persistence with optional Fernet encryption
- ✅ **SQLite storage**: High-performance async backend with advanced querying
- ✅ **Batch validation**: Parallel validation with concurrency control (100+ proxies/sec)
- ✅ **Health Monitoring**: Continuous background health checks with auto-eviction (Phase 2.4)
- ✅ **Browser Rendering**: JavaScript execution with Playwright for JS-heavy sites (Phase 2.5)
- ✅ **TTL Expiration**: Automatic proxy expiration based on time-to-live (Phase 2.6)

**New in v0.2.0**: See [docs/PHASE2_STATUS.md](docs/PHASE2_STATUS.md) for API reference and migration guide.
**Examples**: See [examples/health_monitoring_example.py](examples/health_monitoring_example.py) and [examples/browser_rendering_example.py](examples/browser_rendering_example.py)

## 🌐 REST API Server (v0.3.0)

ProxyWhirl now includes a production-ready REST API server built with FastAPI for remote proxy pool management and proxied requests.

### Quick Start with Docker

```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Access the API at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

### Manual Start

```bash
# Install with API dependencies
pip install "proxywhirl[storage]"

# Start the API server
uv run uvicorn proxywhirl.api:app --host 0.0.0.0 --port 8000

# Or in development mode with auto-reload
uv run uvicorn proxywhirl.api:app --reload
```

### API Features

- **Proxied Requests**: Make HTTP requests through rotating proxies via REST API
- **Pool Management**: CRUD operations for proxy pool (add, remove, list, health check)
- **Monitoring**: Health checks, readiness probes, metrics, and status endpoints
- **Configuration**: Runtime configuration updates without restart
- **Security**: Optional API key authentication, rate limiting, CORS support
- **Documentation**: Auto-generated OpenAPI/Swagger docs

### API Endpoints

#### Make Proxied Requests

```bash
# POST /api/v1/request - Make a proxied HTTP request
curl -X POST http://localhost:8000/api/v1/request \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://httpbin.org/ip",
    "method": "GET",
    "timeout": 30
  }'
```

#### Manage Proxy Pool

```bash
# GET /api/v1/proxies - List all proxies with pagination
curl http://localhost:8000/api/v1/proxies?page=1&page_size=50

# POST /api/v1/proxies - Add new proxy
curl -X POST http://localhost:8000/api/v1/proxies \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://proxy.example.com:8080",
    "username": "user",
    "password": "pass"
  }'

# GET /api/v1/proxies/{id} - Get specific proxy
curl http://localhost:8000/api/v1/proxies/proxy-123

# DELETE /api/v1/proxies/{id} - Remove proxy
curl -X DELETE http://localhost:8000/api/v1/proxies/proxy-123

# POST /api/v1/proxies/test - Run health check
curl -X POST http://localhost:8000/api/v1/proxies/test \
  -H "Content-Type: application/json" \
  -d '{"proxy_ids": ["proxy-123", "proxy-456"]}'
```

#### Monitoring

```bash
# GET /api/v1/health - Health check
curl http://localhost:8000/api/v1/health

# GET /api/v1/ready - Readiness probe (for Kubernetes)
curl http://localhost:8000/api/v1/ready

# GET /api/v1/status - Pool status and statistics
curl http://localhost:8000/api/v1/status

# GET /api/v1/metrics - Performance metrics
curl http://localhost:8000/api/v1/metrics
```

#### Configuration

```bash
# GET /api/v1/config - Get current configuration
curl http://localhost:8000/api/v1/config

# PUT /api/v1/config - Update configuration
curl -X PUT http://localhost:8000/api/v1/config \
  -H "Content-Type: application/json" \
  -d '{
    "rotation_strategy": "round-robin",
    "timeout": 30,
    "max_retries": 3
  }'
```

### Configuration

Configure the API using environment variables:

```bash
# Rotation strategy
export PROXYWHIRL_STRATEGY=round-robin  # round-robin, random, weighted, least-used

# Request timeout (seconds)
export PROXYWHIRL_TIMEOUT=30

# Maximum retry attempts
export PROXYWHIRL_MAX_RETRIES=3

# Optional: API key authentication
export PROXYWHIRL_REQUIRE_AUTH=true
export PROXYWHIRL_API_KEY=your-secret-key

# Optional: CORS origins (comma-separated)
export PROXYWHIRL_CORS_ORIGINS=http://localhost:3000,https://app.example.com

# Optional: SQLite storage for persistence
export PROXYWHIRL_STORAGE_PATH=/data/proxies.db
```

### Python Client Example

```python
import httpx
import asyncio

async def main():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Make proxied request
        response = await client.post(
            "/api/v1/request",
            json={
                "url": "https://httpbin.org/ip",
                "method": "GET",
                "timeout": 30
            }
        )
        print(response.json())
        
        # Add proxy to pool
        response = await client.post(
            "/api/v1/proxies",
            json={
                "url": "http://proxy.example.com:8080",
                "username": "user",
                "password": "pass"
            }
        )
        print(response.json())
        
        # Get pool status
        response = await client.get("/api/v1/status")
        print(response.json())

asyncio.run(main())
```

### Rate Limiting

The API includes built-in rate limiting:
- Default: 100 requests/minute per IP
- Proxied requests (`/api/v1/request`): 50 requests/minute per IP
- Returns HTTP 429 with `Retry-After` header when exceeded

### API Documentation

Interactive API documentation is available at:
- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>
- **OpenAPI JSON**: <http://localhost:8000/openapi.json>

For more details, see [docs/003-REST-API-PROGRESS.md](docs/003-REST-API-PROGRESS.md).

## 🖥️ Command-Line Interface (CLI)

ProxyWhirl includes a powerful CLI built with Typer and Rich for beautiful terminal output.

### Installation

The CLI is included with the base package:

```bash
pip install proxywhirl
```

### Quick Start

```bash
# Show help
proxywhirl --help

# Make an HTTP request through proxies
proxywhirl request https://httpbin.org/get

# List proxies in pool
proxywhirl pool list

# Add a proxy
proxywhirl pool add http://proxy1.example.com:8080

# Check proxy health
proxywhirl health
```

### Commands

#### Configuration Management

```bash
# Initialize config file
proxywhirl config init

# Show all settings
proxywhirl config show

# Get specific value
proxywhirl config get rotation_strategy

# Update value
proxywhirl config set max_retries 5
```

#### Pool Management

```bash
# List all proxies
proxywhirl pool list

# Add proxy without authentication
proxywhirl pool add http://proxy.example.com:8080

# Add proxy with authentication
proxywhirl pool add http://proxy.example.com:8080 -u username -p password

# Test a proxy
proxywhirl pool test http://proxy.example.com:8080

# Remove a proxy
proxywhirl pool remove http://proxy.example.com:8080
```

#### HTTP Requests

```bash
# Simple GET request
proxywhirl request https://httpbin.org/get

# POST with JSON data
proxywhirl request --method POST --data '{"key":"value"}' https://httpbin.org/post

# Add custom headers
proxywhirl request --header "Authorization: Bearer token" https://api.example.com

# Override proxy for single request
proxywhirl request --proxy http://custom-proxy.com:8080 https://httpbin.org/ip

# Configure retries
proxywhirl request --retries 5 https://httpbin.org/get
```

#### Health Monitoring

```bash
# Single health check
proxywhirl health

# Continuous monitoring (every 60 seconds)
proxywhirl health --continuous --interval 60
```

### Output Formats

All commands support multiple output formats:

```bash
# Human-readable with colors (default)
proxywhirl pool list

# JSON for scripting
proxywhirl --format json pool list

# CSV for spreadsheets
proxywhirl --format csv pool list
```

### Global Options

```bash
# Use specific config file
proxywhirl --config /path/to/config.toml pool list

# Enable verbose logging
proxywhirl --verbose request https://httpbin.org/get

# Disable file locking (use with caution)
proxywhirl --no-lock pool list
```

### Configuration File

ProxyWhirl auto-discovers configuration files in this order:

1. `.proxywhirl.toml` in current directory
2. `~/.config/proxywhirl/config.toml` (user config)
3. Built-in defaults

**Example `.proxywhirl.toml`:**

```toml
[tool.proxywhirl]
rotation_strategy = "round_robin"
health_check_interval = 300
timeout = 30
max_retries = 3
follow_redirects = true
verify_ssl = true
default_format = "text"
color = true
verbose = false
storage_backend = "memory"
encrypt_credentials = false

[[tool.proxywhirl.proxies]]
url = "http://proxy1.example.com:8080"

[[tool.proxywhirl.proxies]]
url = "http://proxy2.example.com:8080"
username = "user"
password = "pass"
```

### Examples

See [examples/cli_examples.sh](examples/cli_examples.sh) for a complete collection of CLI usage examples.

### 🔜 Phase 3 - Async & Monitoring (v0.3.0) - Planned

- Full async API support
- Event hooks and monitoring
- Circuit breaker pattern
- Rate limiting per proxy
- Advanced metrics and profiling

### 🔜 Phase 4 - Production Features (v0.4.0) - Planned

- Redis caching support
- Kubernetes deployment guides
- Docker container examples
- Performance optimization (caching, connection pooling)

## 🏗️ Architecture

```
proxywhirl/
├── models.py       # Data models (Pydantic v2)
├── rotator.py      # Core rotation logic
├── strategies.py   # Rotation algorithms
├── fetchers.py     # Proxy fetching & parsing
├── storage.py      # Storage backends
├── utils.py        # Helper functions
└── exceptions.py   # Custom exceptions
```

**Design Philosophy**: Flat, elegant structure. No nested packages. Easy to navigate and extend.

## 🧪 Testing

All tests must be run using `uv` to ensure proper dependency isolation:

```bash
# Run all tests with uv
uv run -- pytest

# Run with coverage
uv run -- pytest --cov=proxywhirl --cov-report=html

# Run specific test file
uv run -- pytest tests/unit/test_models.py

# Run benchmarks
uv run -- pytest tests/benchmarks/ -v

# Type checking
uv run -- mypy proxywhirl/

# Linting
uv run -- ruff check .

# Formatting
uv run -- black .
```

**Why `uv run --`?** This ensures all commands execute in the correct virtual environment with proper dependencies, preventing system/global Python conflicts.

## 🛠️ Development Setup

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup project
git clone https://github.com/wyattowalsh/proxywhirl.git
cd proxywhirl
uv sync

# Run tests
uv run -- pytest
```

## 📊 Performance

- **Proxy Selection**: <1ms (O(1) for most strategies)
- **Request Overhead**: <50ms
- **Validation Speed**: 100+ proxies/second (parallel)
- **Storage I/O**: 10-50ms for 100 proxies (JSON)
- **Concurrency**: 1000+ simultaneous requests

## 🤝 Contributing

Contributions welcome! This project follows a specification-driven development process. See [specs/](specs/) for active features.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

## 🔗 Links

- **Issues**: [GitHub Issues](https://github.com/wyattowalsh/proxywhirl/issues)
- **Discussions**: [GitHub Discussions](https://github.com/wyattowalsh/proxywhirl/discussions)

---

**Status**: ✅ Phase 2 Complete (v0.2.0) - 357 tests passing, 88% coverage

**Phase 1**: Core rotation, authentication, pool management, proxy fetching (US1-US7 complete)

**Phase 2**: Multi-level validation, file/SQLite storage, anonymity detection (US1-US4 complete)

See [docs/PHASE2_STATUS.md](docs/PHASE2_STATUS.md) for detailed Phase 2 documentation and migration guide.
