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

## 🎯 Key Capabilities

### Rotation Strategies

All strategies are available via string names:

```python
# Round-robin: Sequential rotation through all proxies
rotator = ProxyRotator(proxies=proxies, strategy="round-robin")

# Random: Random selection from pool
rotator = ProxyRotator(proxies=proxies, strategy="random")

# Weighted: Prefer proxies with higher success rates
rotator = ProxyRotator(proxies=proxies, strategy="weighted")

# Least-used: Balance load evenly across all proxies
rotator = ProxyRotator(proxies=proxies, strategy="least-used")
```

### Strategy Switching at Runtime

```python
# Start with one strategy
rotator = ProxyRotator(proxies=proxies, strategy="round-robin")

# Switch to another strategy dynamically
rotator.strategy = RandomStrategy()  # Import from proxywhirl.strategies
```

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
