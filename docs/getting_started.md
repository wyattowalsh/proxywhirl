# Getting Started with ProxyWhirl

## Free Proxy Lists 🎁

**Download fresh, aggregated proxy lists** updated every 6 hours from many free sources:

| Format | HTTP/HTTPS | SOCKS4 | SOCKS5 | All Combined |
|--------|-----------|--------|--------|--------------|
| **TXT** | [http.txt](proxy-lists/http.txt) | [socks4.txt](proxy-lists/socks4.txt) | [socks5.txt](proxy-lists/socks5.txt) | [all.txt](proxy-lists/all.txt) |
| **JSON** | - | - | - | [proxies.json](proxy-lists/proxies.json) |

📊 **Metadata**: [metadata.json](proxy-lists/metadata.json) - View stats and generation timestamp

> **Note**: These lists are automatically generated every 6 hours from many free proxy sources.
> Quality may vary - always verify proxies before use in production.

---

## Installation

Install ProxyWhirl using pip or uv:

```bash
pip install proxywhirl
# or
uv pip install proxywhirl
```

## Quick Start

Here's a minimal example to get you started:

```python
from proxywhirl import ProxyWhirl

# Create a proxy rotator
rotator = ProxyWhirl()

# Add proxies
rotator.add_proxy("http://proxy1.example.com:8080")
rotator.add_proxy("http://proxy2.example.com:8080")

# Make requests with rotating proxies
import httpx

proxy = rotator.get_next()
response = httpx.get("https://example.com", proxies=proxy)
```

## Use Pre-Aggregated Proxy Lists

Instead of manually adding proxies, use our free lists:

```python
from proxywhirl import ProxyWhirl
import httpx

# Download and load our free HTTP proxy list
response = httpx.get("https://your-docs-site.com/proxy-lists/http.txt")
proxies = response.text.strip().split("\n")

rotator = ProxyWhirl()
for proxy in proxies:
    rotator.add_proxy(f"http://{proxy}")

# Now use the rotator
proxy = rotator.get_next()
```

## Features

- **Proxy Rotation**: Multiple rotation strategies (round-robin, random, weighted)
- **Health Monitoring**: Automatic health checks and circuit breakers
- **Rate Limiting**: Per-proxy and global rate limits with burst support
- **Retry Logic**: Intelligent retry with exponential backoff
- **Analytics**: Performance tracking and analysis
- **REST API**: Optional REST API for remote proxy management

## Next Steps

- Check out the [tutorials](tutorials/index.md) for in-depth guides
- See the [API reference](api/index.md) for detailed documentation
- Browse the [examples notebook](../examples.ipynb) for common use cases
