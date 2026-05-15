---
title: Quickstart Tutorials
---

# Quickstart Tutorials

## 5-Minute Get Started

### Installation

```bash
pip install proxywhirl
# or with uv
uv pip install proxywhirl
```

### Basic Usage

```python
from proxywhirl import ProxyWhirl

# Create instance (fetches from default sources)
whirl = ProxyWhirl()

# Get a single proxy
proxy = whirl.get()
print(f"Using proxy: {proxy.host}:{proxy.port}")

# Use with requests/httpx
import httpx
with httpx.Client() as client:
    response = client.get(
        "https://httpbin.org/ip",
        proxies=proxy.to_url()
    )
    print(response.json())
```

## Async Quick Start

```python
import asyncio
import httpx
from proxywhirl import AsyncProxyWhirl

async def main():
    whirl = AsyncProxyWhirl()
    
    # Fetch multiple URLs concurrently
    async with httpx.AsyncClient() as client:
        for i in range(5):
            proxy = whirl.get()
            response = await client.get(
                f"https://httpbin.org/delay/1",
                proxies=proxy.to_url()
            )
            print(f"Request {i}: {response.status_code}")

asyncio.run(main())
```

## Rotation Strategies

```python
from proxywhirl import ProxyWhirl, StrategyConfig

# Round-robin (default)
whirl = ProxyWhirl()
proxy1 = whirl.get()  # 1st proxy
proxy2 = whirl.get()  # 2nd proxy
proxy3 = whirl.get()  # 3rd proxy

# Random selection
config = StrategyConfig(name="random")
whirl = ProxyWhirl(strategy_config=config)

# Performance-based (best latency)
config = StrategyConfig(name="performance_based")
whirl = ProxyWhirl(strategy_config=config)

# Weighted by success rate
config = StrategyConfig(name="weighted")
whirl = ProxyWhirl(strategy_config=config)

# Least-used
config = StrategyConfig(name="least_used")
whirl = ProxyWhirl(strategy_config=config)
```

## Filtering Proxies

```python
from proxywhirl import ProxyWhirl, SelectionContext

whirl = ProxyWhirl()

# By country
context = SelectionContext(allowed_countries=["US", "GB", "DE"])
proxy = whirl.get(context=context)

# By protocol
context = SelectionContext(allowed_protocols=["socks5"])
proxy = whirl.get(context=context)

# By latency (performance-based)
context = SelectionContext(max_latency_ms=100)
proxy = whirl.get(context=context)

# Exclude proxies
context = SelectionContext(
    excluded_countries=["CN"],
    excluded_protocols=["socks4"]
)
proxy = whirl.get(context=context)
```

## Caching & Performance

```python
from proxywhirl import ProxyWhirl, CacheConfig

# Enable multi-tier cache
cache = CacheConfig(
    l1_size=100,      # Fast in-memory
    l2_enabled=True,  # Persistent disk
    ttl_seconds=3600  # 1 hour
)

whirl = ProxyWhirl(cache=cache)

# First call: fetches from source
proxy1 = whirl.get()

# Subsequent calls: from cache (fast)
proxy2 = whirl.get()
proxy3 = whirl.get()
```

## Error Handling

```python
from proxywhirl import (
    ProxyWhirl,
    ProxyPoolEmptyError,
    ProxyConnectionError,
    ProxyValidationError
)
import httpx

whirl = ProxyWhirl()

try:
    proxy = whirl.get()
    with httpx.Client() as client:
        response = client.get(
            "https://example.com",
            proxies=proxy.to_url()
        )
except ProxyPoolEmptyError:
    print("No proxies available!")
except ProxyConnectionError as e:
    print(f"Connection failed: {e}")
except ProxyValidationError as e:
    print(f"Validation failed: {e}")
except httpx.RequestError as e:
    print(f"Request failed: {e}")
```

## Custom Proxy Sources

```python
from proxywhirl import ProxyWhirl, ProxySource

# Add custom sources
custom_sources = [
    ProxySource(
        url="https://my-company-proxies.example.com/list.json",
        format="json",
        auth_token="secret123"
    ),
    ProxySource(
        url="file:///home/user/proxies.txt",
        format="plain_text"
    )
]

whirl = ProxyWhirl(sources=custom_sources)
proxies = whirl.bootstrap()  # Fetch from sources
print(f"Loaded {len(proxies)} proxies")
```

## CLI Usage

```bash
# List available proxies
proxywhirl list --count 10

# Test a proxy
proxywhirl validate http://proxy.example.com:8080

# Export to file
proxywhirl export --format json --output proxies.json

# View health status
proxywhirl health

# Audit sources
proxywhirl sources audit
```

## REST API

```bash
# Start server
proxywhirl api --port 8000

# Get a proxy
curl http://localhost:8000/api/proxies

# Get filtered proxy
curl "http://localhost:8000/api/proxies?protocol=https"

# Health check
curl http://localhost:8000/api/health
```

## Integration with Popular Libraries

### httpx

```python
import httpx
from proxywhirl import ProxyWhirl

whirl = ProxyWhirl()
proxy = whirl.get()

client = httpx.Client(proxies=proxy.to_url())
response = client.get("https://example.com")
```

### requests

```python
import requests
from proxywhirl import ProxyWhirl

whirl = ProxyWhirl()
proxy = whirl.get()

response = requests.get(
    "https://example.com",
    proxies={"https": proxy.to_url()}
)
```

### aiohttp

```python
import aiohttp
from proxywhirl import AsyncProxyWhirl

async def main():
    whirl = AsyncProxyWhirl()
    proxy = whirl.get()
    
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://example.com",
            proxy=proxy.to_url()
        ) as response:
            print(await response.text())
```

## Real-World Example: Web Scraper

```python
import asyncio
import httpx
from bs4 import BeautifulSoup
from proxywhirl import AsyncProxyWhirl

async def scrape_urls(urls: list[str]):
    """Scrape multiple URLs with proxy rotation."""
    whirl = AsyncProxyWhirl()
    
    async with httpx.AsyncClient(timeout=15) as client:
        tasks = []
        for url in urls:
            proxy = whirl.get()
            task = scrape_single(client, url, proxy)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

async def scrape_single(client, url, proxy):
    """Scrape single URL."""
    try:
        response = await client.get(
            url,
            proxies=proxy.to_url(),
            headers={"User-Agent": "Mozilla/5.0"}
        )
        soup = BeautifulSoup(response.text, "html.parser")
        
        return {
            "url": url,
            "title": soup.title.string if soup.title else None,
            "status": response.status_code,
            "proxy": str(proxy)
        }
    except Exception as e:
        return {"url": url, "error": str(e)}

# Usage
urls = [
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/page3"
]

results = asyncio.run(scrape_urls(urls))
for result in results:
    if "error" not in result:
        print(f"✓ {result['title']} ({result['proxy']})")
    else:
        print(f"✗ {result['url']}: {result['error']}")
```

## Next Steps

- [Configuration Guide](../reference/configuration.md) - Customize behavior
- [Rotation Strategies](../concepts/rotation-strategies.md) - Choose the best strategy
- [Caching](../guides/caching.md) - Optimize performance
- [Retry & Failover](../guides/retry-failover.md) - Build resilience
- [Integration Examples](./integration-examples.md) - Real-world patterns

See full docs at: https://proxywhirl.com/docs/
