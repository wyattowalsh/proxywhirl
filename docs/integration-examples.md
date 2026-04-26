# ProxyWhirl Integration Examples

## FastAPI Integration

### Basic Setup

```python
# main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from proxywhirl import AsyncProxyWhirl, ProxyConfiguration
from proxywhirl.sources import RECOMMENDED_SOURCES
from proxywhirl.fetchers import ProxyFetcher
import httpx

app = FastAPI(title="ProxyWhirl API")

# Global rotator
rotator: AsyncProxyWhirl = None

@app.on_event("startup")
async def startup():
    """Initialize proxy rotator."""
    global rotator
    
    config = ProxyConfiguration(
        rotation_strategy="performance_based",
        health_check_interval_seconds=300,
        rate_limit_requests_per_second=100.0,
    )
    rotator = AsyncProxyWhirl(config=config)
    
    # Load proxies
    fetcher = ProxyFetcher()
    for source in RECOMMENDED_SOURCES[:5]:
        try:
            proxies = await fetcher.fetch_async(source)
            for proxy in proxies[:30]:
                await rotator.add_proxy(proxy)
        except:
            pass

@app.get("/")
async def root():
    pool = await rotator.get_pool()
    return {"proxies": len(pool.proxies), "status": "ready"}

@app.get("/fetch")
async def fetch_url(url: str):
    """Fetch URL through random proxy."""
    try:
        proxy = await rotator.get_proxy()
        proxy_url = f"{proxy.protocol}://{proxy.host}:{proxy.port}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, proxies=proxy_url, timeout=10.0)
        
        return {
            "url": url,
            "status_code": response.status_code,
            "proxy": proxy.host,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Django Integration

### Middleware

```python
# middleware.py
from django.utils.deprecation import MiddlewareMixin
from proxywhirl import ProxyWhirl
import threading

_rotator = None
_lock = threading.Lock()

def get_rotator():
    global _rotator
    if _rotator is None:
        with _lock:
            if _rotator is None:
                _rotator = ProxyWhirl()
                # Load proxies...
    return _rotator

class ProxyRotationMiddleware(MiddlewareMixin):
    """Add proxy to each request."""
    
    def process_request(self, request):
        rotator = get_rotator()
        proxy = rotator.get_proxy()
        request.proxy = proxy
        request.proxy_url = f"{proxy.protocol}://{proxy.host}:{proxy.port}"
```

### Views

```python
# views.py
import httpx
from django.http import JsonResponse
from django.views import View

class ProxyFetchView(View):
    def get(self, request):
        url = request.GET.get('url')
        try:
            response = httpx.get(
                url,
                proxies=request.proxy_url,
                timeout=10.0
            )
            return JsonResponse({
                "status": response.status_code,
                "proxy": request.proxy.host,
            })
        except Exception as e:
            return JsonResponse(
                {"error": str(e)},
                status=500
            )
```

## aiohttp Integration

```python
import aiohttp
import asyncio
from proxywhirl import AsyncProxyWhirl

async def main():
    rotator = AsyncProxyWhirl()
    # Load proxies...
    
    urls = ["https://example.com"] * 10
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, rotator, url) for url in urls]
        results = await asyncio.gather(*tasks)
    
    for result in results:
        print(result)

async def fetch_url(session, rotator, url):
    try:
        proxy = await rotator.get_proxy()
        proxy_url = f"{proxy.protocol}://{proxy.host}:{proxy.port}"
        
        async with session.get(
            url,
            proxy=proxy_url,
            timeout=aiohttp.ClientTimeout(total=10)
        ) as response:
            return (url, response.status)
    except Exception as e:
        return (url, f"Error: {e}")

asyncio.run(main())
```

## Requests Library Integration

```python
import requests
from proxywhirl import ProxyWhirl

def main():
    rotator = ProxyWhirl()
    # Load proxies...
    
    urls = [
        "https://httpbin.org/ip",
        "https://example.com",
        "https://httpbin.org/user-agent",
    ]
    
    for url in urls:
        try:
            proxy = rotator.get_proxy()
            proxies = {
                "http": f"{proxy.protocol}://{proxy.host}:{proxy.port}",
                "https": f"{proxy.protocol}://{proxy.host}:{proxy.port}",
            }
            
            response = requests.get(
                url,
                proxies=proxies,
                timeout=10
            )
            
            print(f"✓ {url}: {response.status_code}")
            
        except Exception as e:
            print(f"✗ {url}: {e}")

if __name__ == "__main__":
    main()
```

## Selenium/Playwright Integration

### Selenium

```python
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from proxywhirl import ProxyWhirl

def main():
    rotator = ProxyWhirl()
    # Load proxies...
    
    proxy = rotator.get_proxy()
    proxy_url = f"{proxy.host}:{proxy.port}"
    
    # Setup Selenium proxy
    selenium_proxy = Proxy()
    selenium_proxy.proxy_type = ProxyType.MANUAL
    selenium_proxy.http_proxy = proxy_url
    selenium_proxy.ssl_proxy = proxy_url
    
    # Create driver
    options = webdriver.ChromeOptions()
    selenium_proxy.add_to_capabilities(options.to_capabilities())
    
    driver = webdriver.Chrome(options=options)
    driver.get("https://example.com")
    
    # ...
    
    driver.quit()

if __name__ == "__main__":
    main()
```

### Playwright

```python
import asyncio
from playwright.async_api import async_playwright
from proxywhirl import AsyncProxyWhirl

async def main():
    rotator = AsyncProxyWhirl()
    # Load proxies...
    
    proxy = await rotator.get_proxy()
    proxy_url = f"{proxy.protocol}://{proxy.host}:{proxy.port}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            proxy={"server": proxy_url}
        )
        
        page = await browser.new_page()
        await page.goto("https://example.com")
        
        # ...
        
        await browser.close()

asyncio.run(main())
```

## Scrapy Integration

```python
# middlewares.py
from proxywhirl import ProxyWhirl

class ProxyWhirlDownloaderMiddleware:
    def __init__(self):
        self.rotator = ProxyWhirl()
        # Load proxies...
    
    def process_request(self, request, spider):
        proxy = self.rotator.get_proxy()
        proxy_url = f"{proxy.protocol}://{proxy.host}:{proxy.port}"
        
        request.meta['proxy'] = proxy_url
        
        # Add auth if needed
        if proxy.username and proxy.password:
            request.meta['proxy_credentials'] = {
                'username': proxy.username,
                'password': proxy.password,
            }

# settings.py
DOWNLOADER_MIDDLEWARES = {
    'myproject.middlewares.ProxyWhirlDownloaderMiddleware': 610,
}
```

## Celery Integration

```python
from celery import Celery
from proxywhirl import ProxyWhirl
import httpx

app = Celery('myproject')
app.config_from_object('celeryconfig')

# Global rotator
rotator = ProxyWhirl()

@app.task
def fetch_url(url):
    """Celery task to fetch URL with proxy."""
    try:
        proxy = rotator.get_proxy()
        response = httpx.get(
            url,
            proxies=f"{proxy.protocol}://{proxy.host}:{proxy.port}",
            timeout=10
        )
        return {
            "url": url,
            "status": response.status_code,
            "proxy": proxy.host,
        }
    except Exception as e:
        return {
            "url": url,
            "error": str(e),
        }

# Usage
from myproject.tasks import fetch_url

urls = ["https://example.com"] * 100
for url in urls:
    fetch_url.delay(url)
```

## APScheduler Integration

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from proxywhirl import ProxyWhirl
import httpx

scheduler = BackgroundScheduler()
rotator = ProxyWhirl()

def refresh_proxies():
    """Refresh proxy pool."""
    from proxywhirl.sources import RECOMMENDED_SOURCES
    from proxywhirl.fetchers import ProxyFetcher
    
    fetcher = ProxyFetcher()
    rotator.get_pool().proxies = []
    
    for source in RECOMMENDED_SOURCES[:5]:
        try:
            proxies = fetcher.fetch(source)
            for p in proxies[:20]:
                rotator.add_proxy(p)
        except:
            pass

def validate_proxies():
    """Validate all proxies."""
    rotator.get_health_stats()

def cleanup_dead_proxies():
    """Remove unhealthy proxies."""
    pool = rotator.get_pool()
    pool.proxies = [
        p for p in pool.proxies
        if p.health_status.status != "unhealthy"
    ]

# Schedule jobs
scheduler.add_job(refresh_proxies, CronTrigger(hour=0, minute=0))
scheduler.add_job(validate_proxies, CronTrigger(hour="*/2"))
scheduler.add_job(cleanup_dead_proxies, CronTrigger(hour=3))

scheduler.start()
```

## Streamlit Integration

```python
import streamlit as st
from proxywhirl import ProxyWhirl
import httpx

@st.cache_resource
def get_rotator():
    rotator = ProxyWhirl()
    # Load proxies...
    return rotator

def main():
    st.title("ProxyWhirl Dashboard")
    
    rotator = get_rotator()
    
    # Pool stats
    col1, col2, col3 = st.columns(3)
    with col1:
        pool = rotator.get_pool()
        st.metric("Total Proxies", len(pool.proxies))
    
    with col2:
        stats = rotator.get_health_stats()
        healthy = sum(1 for s in stats.values() if s.status == "healthy")
        st.metric("Healthy", healthy)
    
    with col3:
        st.metric("Unhealthy", len(stats) - healthy)
    
    # URL fetcher
    url = st.text_input("URL to fetch:")
    if url:
        try:
            proxy = rotator.get_proxy()
            response = httpx.get(
                url,
                proxies=f"{proxy.protocol}://{proxy.host}:{proxy.port}",
                timeout=10
            )
            st.success(f"Status: {response.status_code}")
            st.write(f"Proxy: {proxy.host}:{proxy.port}")
        except Exception as e:
            st.error(f"Error: {e}")
    
    # Pool visualization
    protocol_counts = {}
    for p in pool.proxies:
        protocol_counts[p.protocol] = protocol_counts.get(p.protocol, 0) + 1
    
    st.bar_chart(protocol_counts)

if __name__ == "__main__":
    main()
```

