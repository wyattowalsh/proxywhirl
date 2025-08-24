# ProxyWhirl

An advanced rotating proxy service for efficient web data collection with Python SDK and CLI interfaces.

## 📊 Loader Health Status

*Health report will be updated daily by GitHub Actions.*

## Features

- **Python SDK**: Comprehensive async/sync library with type hints
- **Command Line Interface**: Powerful CLI with rich terminal output  
- **Smart Caching**: Memory, JSON, and SQLite backends
- **Advanced Validation**: Real-time health monitoring and response time tracking
- **Intelligent Rotation**: Round-robin, random, weighted, and health-based strategies
- **Multi-Provider Support**: Free and premium proxy services with failover

## Quick Start

```python
from proxywhirl import ProxyWhirl

# Create instance with auto-validation
proxy_whirl = ProxyWhirl(auto_validate=True)

# Fetch proxies from all sources
await proxy_whirl.fetch_proxies()

# Get a working proxy
proxy = await proxy_whirl.get_proxy()
print(f"Using proxy: {proxy.host}:{proxy.port}")
```

## Installation

```bash
pip install proxywhirl
```

## Documentation

Visit our [documentation site](https://proxywhirl.readthedocs.io) for detailed guides and API reference.

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
