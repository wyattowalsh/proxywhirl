# ProxyWhirl - Quickstart Tutorials

## Table of Contents

1. [Installation](#installation)
2. [5-Minute Quick Start](#5-minute-quick-start)
3. [Using Free Proxies](#using-free-proxies)
4. [Custom Proxy Sources](#custom-proxy-sources)
5. [Web Scraping Example](#web-scraping-example)
6. [Async/Concurrent Usage](#asyncconcurrent-usage)
7. [Error Handling](#error-handling)
8. [Next Steps](#next-steps)

## Installation

```bash
# Using pip
pip install proxywhirl

# Using uv (faster)
uv pip install proxywhirl

# From source
git clone https://github.com/wyattowalsh/proxywhirl.git
cd proxywhirl
uv sync
```

## 5-Minute Quick Start

### 1. Import and Initialize

```python
from proxywhirl import ProxyWhirl, ProxyConfiguration

# Create a ProxyWhirl instance with defaults
rotator = ProxyWhirl()

# Or customize configuration
config = ProxyConfiguration(
    rotation_strategy="round_robin",
    max_retries=3,
)
rotator = ProxyWhirl(config=config)
```

### 2. Get a Proxy

```python
# Get a single proxy
proxy = rotator.get_proxy()
print(f"{proxy.protocol}://{proxy.host}:{proxy.port}")

# Use in requests
import httpx
response = httpx.get(
    "https://httpbin.org/ip",
    proxies=f"{proxy.protocol}://{proxy.host}:{proxy.port}"
)
print(response.json())
```

### 3. Add Proxies Manually

```python
from proxywhirl.models import Proxy, ProxyCredentials

# Add a single proxy
proxy = Proxy(
    protocol="http",
    host="192.168.1.1",
    port=8080,
)
rotator.add_proxy(proxy)

# Add multiple proxies
proxies = [
    Proxy(protocol="http", host="192.168.1.1", port=8080),
    Proxy(protocol="https", host="192.168.1.2", port=8443),
]
for p in proxies:
    rotator.add_proxy(p)
```

### 4. Check Pool Status

```python
# Get pool information
pool = rotator.get_pool()
print(f"Total proxies: {len(pool.proxies)}")

# Get health statistics
stats = rotator.get_health_stats()
for proxy_id, health in stats.items():
    print(f"{proxy_id}: {health.status}")
```

## Using Free Proxies

ProxyWhirl includes 50+ free proxy sources.

### Option 1: Fetch from All Sources

```python
from proxywhirl import ProxyWhirl
from proxywhirl.fetchers import ProxyFetcher
from proxywhirl.sources import ALL_SOURCES

rotator = ProxyWhirl()
fetcher = ProxyFetcher()

# Fetch from all sources
for source in ALL_SOURCES:
    try:
        proxies = fetcher.fetch(source)
        for proxy in proxies:
            rotator.add_proxy(proxy)
        print(f"Added {len(proxies)} from {source.name}")
    except Exception as e:
        print(f"Failed to fetch from {source.name}: {e}")

print(f"Total proxies: {len(rotator.get_pool().proxies)}")
```

### Option 2: Fetch from Recommended Sources

```python
from proxywhirl import ProxyWhirl
from proxywhirl.fetchers import ProxyFetcher
from proxywhirl.sources import RECOMMENDED_SOURCES

rotator = ProxyWhirl()
fetcher = ProxyFetcher()

# Only fetch from recommended, validated sources
for source in RECOMMENDED_SOURCES:
    try:
        proxies = fetcher.fetch(source)
        for proxy in proxies:
            rotator.add_proxy(proxy)
    except Exception:
        pass

print(f"Total proxies: {len(rotator.get_pool().proxies)}")
```

### Option 3: Fetch Specific Source

```python
from proxywhirl.fetchers import ProxyFetcher
from proxywhirl.sources import ProxySource

rotator = ProxyWhirl()

# Fetch from specific source
source = ProxySource(
    id="free-proxy-list",
    name="Free Proxy List",
    url="https://www.freeproxylists.net/",
)

fetcher = ProxyFetcher()
proxies = fetcher.fetch(source)
for proxy in proxies:
    rotator.add_proxy(proxy)

print(f"Fetched {len(proxies)} proxies")
```

## Custom Proxy Sources

### Parse Custom Format

```python
from proxywhirl.fetchers import ProxyFetcher, PlainTextParser
from proxywhirl.models import Proxy

# Custom proxy list (one per line)
proxy_list = """
192.168.1.1:8080
192.168.1.2:8080
socks5://192.168.1.3:1080
"""

parser = PlainTextParser()
proxies = parser.parse(proxy_list)

rotator = ProxyWhirl()
for proxy in proxies:
    rotator.add_proxy(proxy)
```

### Load from File

```python
# proxies.txt
# 192.168.1.1:8080
# 192.168.1.2:8080
# user:pass@192.168.1.3:8080

from proxywhirl.fetchers import PlainTextParser

with open("proxies.txt") as f:
    content = f.read()

parser = PlainTextParser()
proxies = parser.parse(content)

rotator = ProxyWhirl()
for proxy in proxies:
    rotator.add_proxy(proxy)
```

### Load from CSV

```python
# proxies.csv
# protocol,host,port,username,password
# http,192.168.1.1,8080,,
# https,192.168.1.2,8443,user,pass

from proxywhirl.fetchers import CSVParser

with open("proxies.csv") as f:
    content = f.read()

parser = CSVParser()
proxies = parser.parse(content)

rotator = ProxyWhirl()
for proxy in proxies:
    rotator.add_proxy(proxy)
```

### Load from JSON

```python
# proxies.json
# [
#   {"protocol": "http", "host": "192.168.1.1", "port": 8080},
#   {"protocol": "https", "host": "192.168.1.2", "port": 8443}
# ]

from proxywhirl.fetchers import JSONParser

with open("proxies.json") as f:
    content = f.read()

parser = JSONParser()
proxies = parser.parse(content)

rotator = ProxyWhirl()
for proxy in proxies:
    rotator.add_proxy(proxy)
```

## Web Scraping Example

### Simple Scraper with ProxyWhirl

```python
import httpx
from proxywhirl import ProxyWhirl, ProxyConfiguration
from proxywhirl.sources import RECOMMENDED_SOURCES
from proxywhirl.fetchers import ProxyFetcher
from proxywhirl.models import SelectionContext

# Setup
config = ProxyConfiguration(
    rotation_strategy="round_robin",
    max_retries=3,
)
rotator = ProxyWhirl(config=config)

# Load proxies
fetcher = ProxyFetcher()
for source in RECOMMENDED_SOURCES[:5]:  # First 5 sources
    try:
        proxies = fetcher.fetch(source)
        for proxy in proxies[:10]:  # First 10 from each
            rotator.add_proxy(proxy)
    except:
        pass

# Scrape websites
urls = [
    "https://example.com",
    "https://example.org",
    "https://example.net",
]

for url in urls:
    try:
        # Get proxy with context
        context = SelectionContext(url=url)
        proxy = rotator.get_proxy(context=context)
        
        # Make request
        proxy_url = f"{proxy.protocol}://{proxy.host}:{proxy.port}"
        response = httpx.get(
            url,
            proxies=proxy_url,
            timeout=10.0
        )
        
        # Record success
        print(f"✓ {url} (via {proxy.host})")
        
    except Exception as e:
        print(f"✗ {url}: {e}")
```

### Scraper with Error Handling

```python
import httpx
from proxywhirl import ProxyWhirl
from proxywhirl.exceptions import ProxyPoolEmptyError

rotator = ProxyWhirl()
# ... add proxies ...

for url in urls:
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            proxy = rotator.get_proxy()
            response = httpx.get(
                url,
                proxies=f"{proxy.protocol}://{proxy.host}:{proxy.port}",
                timeout=5.0
            )
            print(f"Success: {url}")
            break  # Success, move to next URL
            
        except ProxyPoolEmptyError:
            print(f"No proxies available for {url}")
            break
            
        except httpx.RequestError as e:
            print(f"Attempt {attempt+1}/{max_attempts} failed: {e}")
            if attempt == max_attempts - 1:
                print(f"Failed: {url}")
```

## Async/Concurrent Usage

### Async Scraper

```python
import asyncio
import httpx
from proxywhirl import AsyncProxyWhirl
from proxywhirl.sources import RECOMMENDED_SOURCES
from proxywhirl.fetchers import ProxyFetcher

async def scrape_urls():
    # Setup
    rotator = AsyncProxyWhirl()
    
    # Load proxies (async)
    fetcher = ProxyFetcher()
    sources = RECOMMENDED_SOURCES[:3]
    for source in sources:
        try:
            proxies = await fetcher.fetch_async(source)
            for proxy in proxies:
                await rotator.add_proxy(proxy)
        except:
            pass
    
    # Scrape concurrently
    urls = [
        "https://example.com",
        "https://example.org",
        "https://example.net",
    ]
    
    tasks = [scrape_url(rotator, url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return results

async def scrape_url(rotator, url):
    try:
        proxy = await rotator.get_proxy()
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                proxies=f"{proxy.protocol}://{proxy.host}:{proxy.port}",
                timeout=10.0
            )
        return (url, "success", response.status_code)
    except Exception as e:
        return (url, "failed", str(e))

# Run
results = asyncio.run(scrape_urls())
for url, status, info in results:
    print(f"{url}: {status} ({info})")
```

### Concurrent Requests (ThreadPool)

```python
from concurrent.futures import ThreadPoolExecutor
from proxywhirl import ProxyWhirl
import httpx

rotator = ProxyWhirl()
# ... add proxies ...

def scrape_url(url):
    try:
        proxy = rotator.get_proxy()
        response = httpx.get(
            url,
            proxies=f"{proxy.protocol}://{proxy.host}:{proxy.port}",
            timeout=10.0
        )
        return (url, response.status_code)
    except Exception as e:
        return (url, f"Error: {e}")

urls = ["https://example.com" for _ in range(100)]

with ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(scrape_url, urls)
    for url, result in results:
        print(f"{url}: {result}")
```

## Error Handling

### Common Error Types

```python
from proxywhirl.exceptions import (
    ProxyWhirlError,
    ProxyPoolEmptyError,
    ProxyConnectionError,
    ProxyValidationError,
    ProxyAuthenticationError,
    ProxyFetchError,
)

try:
    rotator = ProxyWhirl()
    proxy = rotator.get_proxy()
    
except ProxyPoolEmptyError:
    print("No proxies in pool")
    # Fetch more proxies
    
except ProxyConnectionError:
    print("Cannot connect to proxy")
    # Try different proxy
    
except ProxyValidationError:
    print("Proxy format invalid")
    # Check proxy format
    
except ProxyAuthenticationError:
    print("Proxy auth failed")
    # Check credentials
    
except ProxyWhirlError as e:
    print(f"General error: {e}")
```

### Retry on Failure

```python
from proxywhirl import ProxyWhirl, ProxyConfiguration
import httpx

config = ProxyConfiguration(max_retries=5)
rotator = ProxyWhirl(config=config)

def make_request_with_retries(url, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            proxy = rotator.get_proxy()
            response = httpx.get(
                url,
                proxies=f"{proxy.protocol}://{proxy.host}:{proxy.port}",
                timeout=5.0
            )
            return response
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            print(f"Attempt {attempt+1} failed, retrying...")
    
result = make_request_with_retries("https://example.com")
```

### Graceful Degradation

```python
from proxywhirl import ProxyWhirl
import httpx

rotator = ProxyWhirl()

def make_request(url, use_proxy=True):
    try:
        if use_proxy and len(rotator.get_pool().proxies) > 0:
            proxy = rotator.get_proxy()
            proxy_url = f"{proxy.protocol}://{proxy.host}:{proxy.port}"
        else:
            proxy_url = None
        
        response = httpx.get(url, proxies=proxy_url, timeout=10.0)
        return response
        
    except Exception as e:
        print(f"Request failed: {e}")
        if use_proxy:
            # Retry without proxy
            return make_request(url, use_proxy=False)
        raise

response = make_request("https://example.com")
```

## Next Steps

- **Advanced Patterns**: Custom strategies, chaining proxies, caching
- **Performance Tuning**: Benchmarks, optimization, scaling
- **Deployment**: Docker, Kubernetes, cloud platforms
- **Integration**: FastAPI, Django, aiohttp examples
- **Monitoring**: Metrics, logging, health checks

For more information, see the [complete documentation](../README.md).

