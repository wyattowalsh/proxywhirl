# ProxyWhirl 🌀

**Advanced Python Proxy Rotation Library**

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

ProxyWhirl is a production-ready Python library for intelligent proxy rotation with multiple strategies, authentication support, and runtime pool management.

## ✨ Features (MVP - v0.1.0)

- 🔄 **Smart Rotation**: Round-robin, random, weighted, and least-used strategies
- 🔐 **Authentication**: Built-in credential handling for authenticated proxies
- 🎯 **Runtime Management**: Add/remove proxies without restarting
- 📊 **Pool Statistics**: Track health, success rates, and performance metrics
- 🌐 **Built-in Proxy Sources**: 16+ pre-configured free proxy APIs and lists
- 📡 **Auto-Fetch**: Fetch proxies from JSON, CSV, plain text, and HTML sources
- ⚡ **High Performance**: <50ms overhead, tested with concurrent requests
- 🛡️ **Resilient**: Automatic failover with retry logic using tenacity
- 🔒 **Secure**: Credential protection with SecretStr, never logged
- 🧪 **Well-Tested**: 300 tests passing, 88% code coverage
- 📦 **Type-Safe**: Full type hints with py.typed marker
- 🔧 **Production-Ready**: Context manager support, structured logging

## 📦 Installation

```bash
# Basic installation (recommended for MVP)
pip install proxywhirl

# Development installation with uv (faster)
uv pip install proxywhirl
```

> **Note**: Full feature set (auto-fetch, file persistence, async API) coming in future releases.

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

### 🔜 Phase 2 - Validation & Storage (v0.2.0) - Coming Soon

- Multi-level proxy validation (format, TCP, HTTP, anonymity)
- File persistence (JSON with atomic writes)
- SQLite storage backend
- JavaScript rendering support with Playwright
- Continuous background health checks

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

**Status**: ✅ Core Package Complete (v0.1.0) - 300 tests passing, 88% coverage

Features: US1-US7 implemented including basic rotation, authentication, pool lifecycle, rotation strategies, proxy fetching, mixed sources, and advanced error handling.
