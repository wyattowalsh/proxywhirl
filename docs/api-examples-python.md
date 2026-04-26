# ProxyWhirl - Python Code Examples

## Complete Real-World Examples

### Example 1: Simple Web Scraper

```python
#!/usr/bin/env python3
"""Simple web scraper with proxy rotation."""

import httpx
from proxywhirl import ProxyWhirl
from proxywhirl.sources import RECOMMENDED_SOURCES
from proxywhirl.fetchers import ProxyFetcher

def setup_rotator():
    """Initialize proxy rotator with free proxies."""
    rotator = ProxyWhirl()
    fetcher = ProxyFetcher()
    
    # Fetch from top 5 sources
    for source in RECOMMENDED_SOURCES[:5]:
        try:
            proxies = fetcher.fetch(source)
            for proxy in proxies[:20]:  # Add 20 from each
                rotator.add_proxy(proxy)
            print(f"✓ Loaded {len(proxies[:20])} from {source.name}")
        except Exception as e:
            print(f"✗ Failed to load {source.name}: {e}")
    
    return rotator

def scrape_url(rotator, url):
    """Scrape single URL with proxy."""
    try:
        proxy = rotator.get_proxy()
        proxy_url = f"{proxy.protocol}://{proxy.host}:{proxy.port}"
        
        response = httpx.get(
            url,
            proxies=proxy_url,
            timeout=10.0,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        
        print(f"✓ {url} ({response.status_code})")
        return response.text
        
    except Exception as e:
        print(f"✗ {url}: {e}")
        return None

if __name__ == "__main__":
    rotator = setup_rotator()
    
    urls = [
        "https://httpbin.org/ip",
        "https://example.com",
        "https://httpbin.org/user-agent",
    ]
    
    for url in urls:
        content = scrape_url(rotator, url)
        if content:
            print(f"  Content length: {len(content)}")
```

### Example 2: Async Scraper with Concurrency

```python
#!/usr/bin/env python3
"""Async web scraper with concurrent requests."""

import asyncio
import httpx
from proxywhirl import AsyncProxyWhirl
from proxywhirl.sources import RECOMMENDED_SOURCES
from proxywhirl.fetchers import ProxyFetcher

async def setup_rotator():
    """Initialize async proxy rotator."""
    rotator = AsyncProxyWhirl()
    fetcher = ProxyFetcher()
    
    for source in RECOMMENDED_SOURCES[:3]:
        try:
            # Async fetch
            proxies = await fetcher.fetch_async(source)
            for proxy in proxies[:15]:
                await rotator.add_proxy(proxy)
        except:
            pass
    
    return rotator

async def scrape_url(rotator, url):
    """Async scrape single URL."""
    try:
        proxy = await rotator.get_proxy()
        proxy_url = f"{proxy.protocol}://{proxy.host}:{proxy.port}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                proxies=proxy_url,
                timeout=10.0
            )
        
        return (url, "success", response.status_code)
        
    except Exception as e:
        return (url, "error", str(e))

async def main():
    """Scrape multiple URLs concurrently."""
    rotator = await setup_rotator()
    
    urls = [
        "https://httpbin.org/ip",
        "https://httpbin.org/user-agent",
        "https://example.com",
    ] * 5  # 15 URLs total
    
    # Scrape 5 URLs concurrently
    tasks = [scrape_url(rotator, url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Display results
    for url, status, info in results:
        print(f"{url}: {status} ({info})")

if __name__ == "__main__":
    asyncio.run(main())
```

### Example 3: FastAPI Integration

```python
#!/usr/bin/env python3
"""FastAPI app with ProxyWhirl integration."""

from fastapi import FastAPI, HTTPException
from proxywhirl import AsyncProxyWhirl, ProxyConfiguration
from proxywhirl.sources import RECOMMENDED_SOURCES
from proxywhirl.fetchers import ProxyFetcher
import httpx
from pydantic import BaseModel

app = FastAPI()

# Global rotator (initialize on startup)
rotator = None

class ProxyResponse(BaseModel):
    proxy: str
    protocol: str
    host: str
    port: int

class FetchResponse(BaseModel):
    url: str
    status_code: int
    content_length: int

@app.on_event("startup")
async def startup_event():
    """Initialize proxy rotator on startup."""
    global rotator
    
    config = ProxyConfiguration(
        rotation_strategy="performance_based",
        health_check_interval_seconds=300,
    )
    rotator = AsyncProxyWhirl(config=config)
    
    # Load proxies
    fetcher = ProxyFetcher()
    for source in RECOMMENDED_SOURCES[:5]:
        try:
            proxies = await fetcher.fetch_async(source)
            for proxy in proxies[:20]:
                await rotator.add_proxy(proxy)
        except:
            pass

@app.get("/proxy")
async def get_proxy():
    """Get a single proxy."""
    proxy = await rotator.get_proxy()
    return ProxyResponse(
        proxy=f"{proxy.protocol}://{proxy.host}:{proxy.port}",
        protocol=proxy.protocol,
        host=proxy.host,
        port=proxy.port,
    )

@app.get("/pool/stats")
async def get_stats():
    """Get pool statistics."""
    pool = await rotator.get_pool()
    return {
        "total": len(pool.proxies),
        "healthy": sum(1 for p in pool.proxies if p.health_status.status == "healthy"),
    }

@app.post("/fetch")
async def fetch_url(url: str):
    """Fetch URL through proxy."""
    try:
        proxy = await rotator.get_proxy()
        proxy_url = f"{proxy.protocol}://{proxy.host}:{proxy.port}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                proxies=proxy_url,
                timeout=10.0
            )
        
        return FetchResponse(
            url=url,
            status_code=response.status_code,
            content_length=len(response.content),
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Example 4: Django Integration

```python
# django_app/middleware.py
"""Django middleware for proxy rotation."""

from django.utils.deprecation import MiddlewareMixin
from proxywhirl import ProxyWhirl
import threading

# Thread-safe rotator
_rotator = None
_lock = threading.Lock()

def get_rotator():
    """Get or create proxy rotator."""
    global _rotator
    
    if _rotator is None:
        with _lock:
            if _rotator is None:
                _rotator = ProxyWhirl()
                # Load proxies here
    
    return _rotator

class ProxyRotationMiddleware(MiddlewareMixin):
    """Inject proxy into outgoing requests."""
    
    def process_request(self, request):
        """Add proxy to request."""
        rotator = get_rotator()
        proxy = rotator.get_proxy()
        
        # Store proxy in request for views
        request.proxy = proxy
        request.proxy_url = f"{proxy.protocol}://{proxy.host}:{proxy.port}"

# views.py
"""Django views using proxies."""

import httpx
from django.http import JsonResponse

def fetch_external(request):
    """Fetch external URL through proxy."""
    url = request.GET.get('url')
    
    try:
        response = httpx.get(
            url,
            proxies=request.proxy_url,
            timeout=10.0
        )
        return JsonResponse({
            "status": response.status_code,
            "content_length": len(response.content),
        })
    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=500
        )
```

### Example 5: Rate-Limited Scraper

```python
#!/usr/bin/env python3
"""Scraper with rate limiting."""

import time
import httpx
from proxywhirl import ProxyWhirl, ProxyConfiguration

config = ProxyConfiguration(
    rotation_strategy="round_robin",
    rate_limit_requests_per_second=5.0,  # 5 requests/sec
    max_retries=3,
)
rotator = ProxyWhirl(config=config)

# Load proxies...

def scrape_batch(urls, delay_seconds=1.0):
    """Scrape URLs with rate limiting."""
    for url in urls:
        try:
            proxy = rotator.get_proxy()
            response = httpx.get(
                url,
                proxies=f"{proxy.protocol}://{proxy.host}:{proxy.port}",
                timeout=10.0
            )
            print(f"✓ {url}")
            
        except Exception as e:
            print(f"✗ {url}: {e}")
        
        # Rate limit
        time.sleep(delay_seconds)

urls = [f"https://example.com/page/{i}" for i in range(100)]
scrape_batch(urls)
```

### Example 6: Proxy Validation

```python
#!/usr/bin/env python3
"""Validate proxies before use."""

from proxywhirl import ProxyWhirl, ProxyConfiguration
from proxywhirl.fetchers import ProxyValidator
import asyncio

async def validate_pool():
    """Validate all proxies in pool."""
    config = ProxyConfiguration(
        health_checks_enabled=True,
        health_check_interval_seconds=60,
    )
    rotator = ProxyWhirl(config=config)
    
    # Load proxies...
    # rotator.add_proxy(...)
    
    # Validate proxies
    validator = ProxyValidator()
    pool = rotator.get_pool()
    
    print(f"Validating {len(pool.proxies)} proxies...")
    
    valid_count = 0
    for proxy in pool.proxies:
        try:
            is_valid = await validator.validate_async(
                proxy,
                timeout_seconds=5
            )
            if is_valid:
                valid_count += 1
        except:
            pass
    
    print(f"Valid: {valid_count}/{len(pool.proxies)}")

asyncio.run(validate_pool())
```

### Example 7: Custom Rotation Strategy

```python
#!/usr/bin/env python3
"""Custom rotation strategy."""

from proxywhirl import ProxyWhirl
from proxywhirl.models import SelectionContext
from proxywhirl.strategies import RotationStrategy
from typing import Optional

class GeographicStrategy(RotationStrategy):
    """Select proxies by geographic location."""
    
    def select(self, pool, context: Optional[SelectionContext]):
        """Select proxy from preferred location."""
        if not context or not context.metadata.get("preferred_location"):
            # Fallback to random
            import random
            return random.choice(pool.proxies)
        
        location = context.metadata["preferred_location"]
        
        # Filter by location
        matching = [
            p for p in pool.proxies
            if p.geo_location and 
            p.geo_location.get("country") == location
        ]
        
        if matching:
            return matching[0]
        return pool.proxies[0]
    
    def record_success(self, proxy):
        pass
    
    def record_failure(self, proxy):
        pass

# Use custom strategy
rotator = ProxyWhirl()
rotator.strategy = GeographicStrategy()

context = SelectionContext(
    url="https://example.com",
    metadata={"preferred_location": "US"}
)
proxy = rotator.get_proxy(context=context)
print(f"Selected: {proxy.geo_location}")
```

### Example 8: Monitoring & Metrics

```python
#!/usr/bin/env python3
"""Monitor proxy performance."""

from proxywhirl import ProxyWhirl
import time

rotator = ProxyWhirl()
# Load proxies...

def monitor_pool(interval_seconds=10, duration_seconds=60):
    """Monitor pool performance."""
    start_time = time.time()
    
    while time.time() - start_time < duration_seconds:
        pool = rotator.get_pool()
        stats = rotator.get_health_stats()
        
        healthy = sum(
            1 for s in stats.values() 
            if s.status == "healthy"
        )
        
        print(f"\n[{time.time()-start_time:.0f}s]")
        print(f"Pool size: {len(pool.proxies)}")
        print(f"Healthy: {healthy}/{len(pool.proxies)}")
        
        time.sleep(interval_seconds)

monitor_pool()
```

### Example 9: Error Recovery

```python
#!/usr/bin/env python3
"""Handle errors gracefully."""

import httpx
from proxywhirl import ProxyWhirl
from proxywhirl.exceptions import (
    ProxyPoolEmptyError,
    ProxyConnectionError,
)

rotator = ProxyWhirl()

def make_request_resilient(url):
    """Make request with automatic fallback."""
    
    # Try with proxy
    for attempt in range(3):
        try:
            proxy = rotator.get_proxy()
            response = httpx.get(
                url,
                proxies=f"{proxy.protocol}://{proxy.host}:{proxy.port}",
                timeout=5.0
            )
            print(f"✓ Success with proxy {proxy.host}")
            return response
            
        except ProxyPoolEmptyError:
            print("No proxies available")
            break
            
        except ProxyConnectionError:
            print(f"Proxy connection failed, retrying...")
            continue
            
        except httpx.RequestError as e:
            print(f"Request failed: {e}")
            if attempt == 2:
                break
    
    # Fallback: request without proxy
    print("Trying without proxy...")
    try:
        response = httpx.get(url, timeout=10.0)
        print("✓ Success without proxy")
        return response
    except Exception as e:
        print(f"✗ Failed: {e}")
        return None

result = make_request_resilient("https://httpbin.org/ip")
```

### Example 10: Export & Import Proxies

```python
#!/usr/bin/env python3
"""Export and import proxy pools."""

import json
from proxywhirl import ProxyWhirl

def export_pool(rotator, filename):
    """Export proxies to JSON file."""
    pool = rotator.get_pool()
    
    proxies_data = [
        {
            "protocol": p.protocol,
            "host": p.host,
            "port": p.port,
            "tags": p.tags,
        }
        for p in pool.proxies
    ]
    
    with open(filename, 'w') as f:
        json.dump(proxies_data, f, indent=2)
    
    print(f"Exported {len(proxies_data)} proxies to {filename}")

def import_pool(filename):
    """Import proxies from JSON file."""
    rotator = ProxyWhirl()
    
    with open(filename) as f:
        proxies_data = json.load(f)
    
    from proxywhirl.models import Proxy
    
    for data in proxies_data:
        proxy = Proxy(
            protocol=data["protocol"],
            host=data["host"],
            port=data["port"],
            tags=data.get("tags", []),
        )
        rotator.add_proxy(proxy)
    
    print(f"Imported {len(proxies_data)} proxies")
    return rotator

# Usage
rotator = ProxyWhirl()
# ... add proxies ...
export_pool(rotator, "proxies.json")

# Later, import
rotator2 = import_pool("proxies.json")
```

