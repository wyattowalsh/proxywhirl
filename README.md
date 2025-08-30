# ProxyWhirl

**Python 3.13+ library for managing rotating proxies with pluggable proxy source loaders, flexible caching, and comprehensive validation.**

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Quality](https://img.shields.io/badge/code%20quality-high-brightgreen.svg)](#)

## 🌟 Key Features

### 🔄 **Intelligent Proxy Management**
- **8+ Built-in Loaders**: TheSpeedX, Clarketm, Monosans, ProxyScrape, Proxifly, JetkaiProxy, VakhovFresh, UserProvided
- **5 Rotation Strategies**: Round-robin, random, weighted, health-based, and least-used
- **Multi-backend Caching**: Memory (default), JSON file, and SQLite database storage

### 🔍 **Advanced Validation & Health Monitoring**
- **Circuit Breaker Pattern**: Prevents cascading failures during validation
- **3 Quality Levels**: BASIC, STANDARD, THOROUGH validation with configurable depth
- **Real-time Health Tracking**: Response times, success rates, and automatic recovery

### 🖥️ **Multiple Interfaces**
- **Python API**: First-class async/sync support with comprehensive error handling  
- **Rich CLI**: 8+ commands with beautiful terminal output and progress indicators
- **Interactive TUI**: Real-time dashboard built with Textual for visual proxy management

### 📤 **Flexible Export System**
- **7+ Export Formats**: JSON, CSV, XML, TXT, YAML, SQL, PAC files
- **Advanced Filtering**: Geography, performance, anonymity level, and status-based filtering
- **Volume Controls**: Sampling, limits, and distribution strategies

## 🚀 Quick Start

### Basic Usage

```python
import asyncio
import httpx
from proxywhirl import ProxyWhirl

async def main():
    # Initialize with health-based rotation and auto-validation
    proxy_whirl = ProxyWhirl(
        rotation_strategy="health_based",
        auto_validate=True
    )
    
    # Fetch and validate proxies from all sources
    count = await proxy_whirl.fetch_proxies()
    print(f"✅ Loaded {count} working proxies")
    
    # Get a proxy and use it
    proxy = await proxy_whirl.get_proxy()
    if proxy:
        proxy_url = f"http://{proxy.host}:{proxy.port}"
        async with httpx.AsyncClient(proxies=proxy_url) as client:
            response = await client.get("https://httpbin.org/ip")
            print(f"🌐 Your IP through proxy: {response.json()}")

# Run the async function
asyncio.run(main())
```

### Command Line Interface

```bash
# Install ProxyWhirl
pip install proxywhirl

# Fetch proxies and validate them
proxywhirl fetch --validate

# List cached proxies with details
proxywhirl list --limit 10

# Get a single working proxy
proxywhirl get

# Generate health report for all loaders
proxywhirl health-report

# Launch interactive TUI dashboard
proxywhirl tui

# Export proxies in different formats
proxywhirl export --format json --output proxies.json
proxywhirl export --format csv --country US --anonymity elite
```

## 📦 Installation

### Requirements
- **Python 3.13+** (required)
- **Operating System**: Linux, macOS, Windows

### Install from PyPI

```bash
pip install proxywhirl
```

### Development Installation

```bash
git clone https://github.com/wyattowalsh/proxywhirl.git
cd proxywhirl
make setup  # Creates venv and installs dependencies
make quality  # Run complete quality pipeline
```

## 🏗️ Architecture

ProxyWhirl follows a modular, layered architecture with pluggable components:

```
🎯 User Interfaces → ⚙️ Core Orchestrator → 📡 Data Sources
   (CLI/TUI/API)      (ProxyWhirl)        (8+ Loaders)
                           ↓
💾 Multi-backend Cache ← 🔒 Validation Engine → 🔄 Rotation Engine
   (Memory/JSON/SQLite)    (Circuit Breaker)     (5 Strategies)
                           ↓
                    📤 Export System
                    (7+ Formats)
```

**Core Components:**
- **ProxyWhirl** (`proxywhirl.py`, 1200+ lines): Main orchestrator with unified sync/async API
- **ProxyValidator** (`validator.py`, 788+ lines): Async validation with circuit breaker patterns
- **ProxyRotator** (`rotator.py`, 402+ lines): Intelligent rotation with health tracking
- **ProxyExporter** (`exporter.py`, 742+ lines): Multi-format export with advanced filtering

## 📖 Documentation

Visit our comprehensive documentation:

- **[Getting Started Guide](docs/content/docs/usage.mdx)**: Complete setup and basic usage
- **[API Reference](docs/content/docs/reference.mdx)**: Full Python API documentation  
- **[CLI Reference](docs/content/docs/usage.mdx#command-line-interface-cli)**: All command-line options
- **[Architecture Deep Dive](docs/content/docs/architecture.mdx)**: System design and components
- **[Contributing](docs/content/docs/contributing.mdx)**: Development workflow and guidelines

## 🤝 Contributing

We welcome contributions! Please check our [Contributing Guide](docs/content/docs/contributing.mdx) for:

- **Development Setup**: `make setup` → `make quality` → `make test`
- **Code Standards**: Black formatting, Ruff/Pylint linting, MyPy type checking  
- **Testing**: Pytest with async support, coverage reports, CI/CD integration
- **Pull Request Process**: Feature branches from `dev`, comprehensive testing

## 📊 Project Status

- ✅ **Stable API**: Production-ready with comprehensive test coverage
- 🔄 **Active Development**: Regular updates and improvements
- 📈 **Growing Ecosystem**: 8+ proxy loaders with more being added
- 🛡️ **Security Focused**: Automated dependency scanning and security audits

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ for the web scraping community**
