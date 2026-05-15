---
title: Integration Examples
---

# Real-World Integration Examples

## Overview

This guide shows production-ready patterns for integrating ProxyWhirl into common applications and frameworks.

## Web Scraping (with httpx + BeautifulSoup)

```python
import httpx
import asyncio
from bs4 import BeautifulSoup
from proxywhirl import AsyncProxyWhirl, ProxyConfiguration, StrategyConfig

# Setup
config = ProxyConfiguration(
    sources=["https://raw.githubusercontent.com/..."],
    strategy_config=StrategyConfig(name="performance_based"),
    circuit_breaker_config={
        "failure_threshold": 3,
        "recovery_timeout": 30
    }
)

whirl = AsyncProxyWhirl(config)

async def scrape_with_rotation(urls: list[str]) -> list[dict]:
    """Scrape multiple URLs with proxy rotation."""
    async with httpx.AsyncClient(timeout=10) as client:
        tasks = []
        for url in urls:
            proxy = whirl.get()
            tasks.append(scrape_single(client, url, proxy))
        return await asyncio.gather(*tasks)

async def scrape_single(client, url, proxy):
    """Scrape a single URL through proxy."""
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
            "status": response.status_code
        }
    except Exception as e:
        return {"url": url, "error": str(e)}

# Run
urls = ["https://example.com", "https://example.org"]
results = asyncio.run(scrape_with_rotation(urls))
for result in results:
    print(result)
```

## FastAPI Integration

```python
from fastapi import FastAPI, HTTPException, Depends
from proxywhirl import ProxyWhirl, ProxyPoolEmptyError
import httpx

app = FastAPI()

# Global instance (use dependency injection in production)
whirl = ProxyWhirl()

async def get_proxy():
    """Dependency to get proxy."""
    try:
        return whirl.get()
    except ProxyPoolEmptyError:
        raise HTTPException(status_code=503, detail="No proxies available")

@app.get("/fetch")
async def fetch_url(url: str, proxy=Depends(get_proxy)):
    """Fetch URL through proxy."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url,
                proxies=proxy.to_url(),
                timeout=10
            )
            return {
                "status": response.status_code,
                "content": response.text[:1000],
                "proxy": str(proxy)
            }
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=str(e))

@app.get("/health")
async def health_check():
    """Check proxy pool health."""
    return {
        "total_proxies": len(whirl.pool.proxies),
        "healthy": len([p for p in whirl.pool.proxies if p.is_active]),
        "cache_size": whirl.cache_manager.size()
    }
```

## Selenium Integration

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from proxywhirl import ProxyWhirl

whirl = ProxyWhirl()

def get_chrome_with_proxy():
    """Create Chrome driver with proxy rotation."""
    proxy = whirl.get()
    
    options = Options()
    options.add_argument(f"--proxy-server={proxy.to_url()}")
    
    driver = webdriver.Chrome(options=options)
    return driver, proxy

# Usage
driver, proxy = get_chrome_with_proxy()
try:
    driver.get("https://example.com")
    print(f"Loaded with proxy: {proxy}")
finally:
    driver.quit()
```

## Playwright Integration

```python
import asyncio
from playwright.async_api import async_playwright
from proxywhirl import AsyncProxyWhirl

async def browse_with_proxy(url: str):
    """Browse with proxy using Playwright."""
    whirl = AsyncProxyWhirl()
    proxy = whirl.get()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            proxy={
                "server": proxy.to_url(),
                "bypass": "localhost"
            }
        )
        page = await browser.new_page()
        await page.goto(url)
        print(f"Title: {await page.title()}")
        await browser.close()

# Run
asyncio.run(browse_with_proxy("https://example.com"))
```

## Django Integration

```python
# settings.py
PROXYWHIRL_CONFIG = {
    "sources": ["https://raw.githubusercontent.com/..."],
    "pool_size": 100,
    "cache": {
        "l1_size": 50,
        "l2_enabled": True,
    }
}

# middleware.py
import httpx
from django.utils.deprecation import MiddlewareMixin
from proxywhirl import ProxyWhirl

class ProxyRotationMiddleware(MiddlewareMixin):
    """Add proxy rotation to outbound requests."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.whirl = ProxyWhirl(settings.PROXYWHIRL_CONFIG)
    
    def process_request(self, request):
        request.proxy = self.whirl.get()
        return None

# views.py
from django.http import JsonResponse
import httpx

def fetch_url(request):
    """Fetch URL with rotated proxy."""
    url = request.GET.get("url")
    proxy = request.proxy
    
    with httpx.Client() as client:
        response = client.get(url, proxies=proxy.to_url())
        return JsonResponse({
            "status": response.status_code,
            "proxy": str(proxy)
        })
```

## APIClient Wrapper

```python
from typing import Any, Optional
import httpx
from proxywhirl import AsyncProxyWhirl, ProxyPoolEmptyError

class ProxiedAPIClient:
    """HTTP client with automatic proxy rotation."""
    
    def __init__(self, base_url: str, config=None):
        self.base_url = base_url
        self.whirl = AsyncProxyWhirl(config)
        self.client = None
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(base_url=self.base_url)
        return self
    
    async def __aexit__(self, *args):
        await self.client.aclose()
    
    async def get(self, path: str, **kwargs) -> httpx.Response:
        """GET with proxy rotation."""
        try:
            proxy = self.whirl.get()
            return await self.client.get(
                path,
                proxies=proxy.to_url(),
                **kwargs
            )
        except ProxyPoolEmptyError:
            # Fallback to direct
            return await self.client.get(path, **kwargs)

# Usage
async def main():
    async with ProxiedAPIClient("https://api.example.com") as api:
        response = await api.get("/users/1")
        print(response.json())

import asyncio
asyncio.run(main())
```

## Rate-Limited Scraper

```python
import asyncio
from proxywhirl import AsyncProxyWhirl
from proxywhirl.rate_limiting import RateLimiter
import httpx

async def rate_limited_scraper():
    """Scrape with rate limiting per proxy."""
    whirl = AsyncProxyWhirl()
    
    # 10 requests per minute per proxy
    limiter = RateLimiter(
        rate=10,
        period=60,
        per_proxy=True  # Limit per proxy, not global
    )
    
    async def fetch(url):
        async with limiter:
            proxy = whirl.get()
            async with httpx.AsyncClient() as client:
                return await client.get(
                    url,
                    proxies=proxy.to_url(),
                    timeout=10
                )
    
    urls = [f"https://example.com/page/{i}" for i in range(100)]
    tasks = [fetch(url) for url in urls]
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    return [r for r in responses if not isinstance(r, Exception)]

# Run
results = asyncio.run(rate_limited_scraper())
print(f"Successfully fetched {len(results)} pages")
```

## Monitoring & Observability

```python
from proxywhirl.metrics_collector import MetricsCollector
import prometheus_client as prom

class ProxyWhirlMetrics:
    """Export ProxyWhirl metrics to Prometheus."""
    
    def __init__(self, whirl):
        self.whirl = whirl
        self.metrics = MetricsCollector()
        
        self.pool_size = prom.Gauge(
            "proxywhirl_pool_size",
            "Total proxies in pool"
        )
        self.healthy_count = prom.Gauge(
            "proxywhirl_healthy_count",
            "Healthy proxies"
        )
        self.cache_hits = prom.Counter(
            "proxywhirl_cache_hits_total",
            "Total cache hits"
        )
        self.errors = prom.Counter(
            "proxywhirl_errors_total",
            "Total errors",
            ["error_type"]
        )
    
    def update(self):
        """Update Prometheus metrics."""
        self.pool_size.set(len(self.whirl.pool.proxies))
        self.healthy_count.set(
            len([p for p in self.whirl.pool.proxies if p.is_active])
        )
        self.cache_hits.inc(self.metrics.cache_hits)

# Usage in FastAPI
from fastapi.responses import Response
from prometheus_client import REGISTRY

@app.get("/api/metrics")
async def metrics():
    """Export Prometheus metrics."""
    return Response(
        REGISTRY.generate_latest(),
        media_type="text/plain"
    )
```

## Testing with Fixtures

```python
import pytest
from proxywhirl import ProxyWhirl, Proxy
from unittest.mock import Mock, patch

@pytest.fixture
def mock_proxy():
    """Mock proxy for testing."""
    return Proxy(
        url="http://127.0.0.1:8080",
        host="127.0.0.1",
        port=8080,
        protocol="http",
        is_active=True
    )

@pytest.fixture
def whirl_with_mocks(respx_mock):
    """ProxyWhirl with mocked sources."""
    with patch.object(ProxyWhirl, "bootstrap") as mock_bootstrap:
        whirl = ProxyWhirl()
        whirl.pool.proxies = [
            Proxy(
                url=f"http://proxy{i}.test:8080",
                host=f"proxy{i}.test",
                port=8080,
                protocol="http",
                is_active=True
            )
            for i in range(3)
        ]
        return whirl

@pytest.mark.asyncio
async def test_integration(whirl_with_mocks):
    """Test integration with mock proxies."""
    proxy = whirl_with_mocks.get()
    assert proxy is not None
    assert proxy.is_active
```

See also: [Python API](../reference/python-api.md), [REST API](../reference/rest-api.md), [CLI Reference](./cli-reference.md)
