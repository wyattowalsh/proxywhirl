---
title: Async Client Guide
---

# Async Client Guide

ProxyWhirl provides `AsyncProxyWhirl`, a fully async implementation of proxy rotation built on `httpx.AsyncClient`. This guide covers when to use async vs sync, initialization patterns, async/await usage, and performance considerations.

```{contents}
:local:
:depth: 2
```

## When to Use Async vs Sync

### Use AsyncProxyWhirl when:

- **High concurrency**: Making many requests in parallel (100+ concurrent requests)
- **I/O-bound workloads**: Most time spent waiting for network responses
- **Existing async code**: Integrating with FastAPI, aiohttp, or other async frameworks
- **Resource efficiency**: Need to handle thousands of connections with minimal memory
- **Web scraping at scale**: Concurrent crawling of multiple sites

### Use ProxyWhirl (sync) when:

- **Simple scripts**: Quick one-off tasks or small automation scripts
- **Sequential processing**: Requests must happen one at a time
- **Existing sync code**: Integrating with Flask, requests, or other sync frameworks
- **Simpler debugging**: Sync code is easier to debug and reason about
- **Low concurrency**: Making fewer than 10 concurrent requests

```{note}
Both `AsyncProxyWhirl` and `ProxyWhirl` share the same strategy system, retry logic, and circuit breaker implementation. The only difference is the async/sync execution model. See {doc}`advanced-strategies` for strategy details and {doc}`retry-failover` for circuit breaker configuration.
```

## Initialization

### Basic Initialization

```python
from proxywhirl import AsyncProxyWhirl

# Default initialization (round-robin strategy)
async with AsyncProxyWhirl() as rotator:
    await rotator.add_proxy("http://proxy1.example.com:8080")
    await rotator.add_proxy("http://proxy2.example.com:8080")

    response = await rotator.get("https://httpbin.org/ip")
    print(response.json())
```

### With Initial Proxies

```python
from proxywhirl import AsyncProxyWhirl, Proxy

# Pre-populate proxy pool
proxies = [
    Proxy(url="http://proxy1.example.com:8080"),
    Proxy(url="http://proxy2.example.com:8080"),
    Proxy(url="http://proxy3.example.com:8080"),
]

async with AsyncProxyWhirl(proxies=proxies) as rotator:
    response = await rotator.get("https://httpbin.org/ip")
```

### With Custom Strategy

```python
from proxywhirl import AsyncProxyWhirl

# Strategy from string aliases
async with AsyncProxyWhirl(strategy="random") as rotator:
    # Uses RandomStrategy
    pass

# Available string aliases at init:
# - "round-robin" (default)
# - "random"
# - "weighted"
# - "least-used"
# - "performance-based"
# - "session" (or "session-persistence")
# - "geo-targeted"
#
# Underscore aliases are also accepted (e.g., "round_robin", "geo_targeted").
# For cost-aware and composite, use set_strategy() after init or pass a strategy
# instance directly:
#   from proxywhirl.strategies import PerformanceBasedStrategy
#   async with AsyncProxyWhirl(strategy=PerformanceBasedStrategy()) as rotator:
```

:::{seealso}
For detailed strategy configuration including EMA tuning, session persistence, geo-targeting, cost-aware selection, and composite strategies, see {doc}`advanced-strategies`.
:::

### With Custom Configuration

```python
from proxywhirl import AsyncProxyWhirl, ProxyConfiguration, RetryPolicy

config = ProxyConfiguration(
    timeout=60,
    verify_ssl=False,
    pool_connections=50,
    pool_max_keepalive=20,
)

retry_policy = RetryPolicy(
    max_attempts=5,
    base_delay=1.5,
)

async with AsyncProxyWhirl(
    strategy="round-robin",
    config=config,
    retry_policy=retry_policy
) as rotator:
    # Hot-swap to performance-based after init if needed
    rotator.set_strategy("performance-based")
    pass
```

## Context Manager Usage

### Async Context Manager (Recommended)

Always use `async with` to ensure proper cleanup of HTTP clients and background threads:

```python
import asyncio
from proxywhirl import AsyncProxyWhirl

async def main():
    async with AsyncProxyWhirl() as rotator:
        await rotator.add_proxy("http://proxy1.example.com:8080")

        # Make requests
        response = await rotator.get("https://httpbin.org/ip")

        # Client is automatically closed on exit

    # All resources cleaned up here

asyncio.run(main())
```

### Manual Lifecycle Management (Advanced)

For advanced use cases where you need explicit control:

```python
rotator = AsyncProxyWhirl()

# Manually enter context
await rotator.__aenter__()

try:
    await rotator.add_proxy("http://proxy1.example.com:8080")
    response = await rotator.get("https://httpbin.org/ip")
finally:
    # Manually exit context
    await rotator.__aexit__(None, None, None)
```

```{warning}
Manual lifecycle management requires careful exception handling to prevent resource leaks. Always prefer `async with` unless you have a specific reason not to.
```

## HTTP Request Methods

### All HTTP Methods

`AsyncProxyWhirl` provides async versions of all standard HTTP methods:

```python
async with AsyncProxyWhirl() as rotator:
    await rotator.add_proxy("http://proxy1.example.com:8080")

    # GET request
    response = await rotator.get("https://api.example.com/data")

    # POST request with JSON body
    response = await rotator.post(
        "https://api.example.com/submit",
        json={"key": "value"}
    )

    # PUT request
    response = await rotator.put(
        "https://api.example.com/resource/123",
        json={"updated": "data"}
    )

    # DELETE request
    response = await rotator.delete("https://api.example.com/resource/123")

    # PATCH request
    response = await rotator.patch(
        "https://api.example.com/resource/123",
        json={"partial": "update"}
    )

    # HEAD request
    response = await rotator.head("https://api.example.com/resource")

    # OPTIONS request
    response = await rotator.options("https://api.example.com/resource")
```

### Request Parameters

All methods accept standard `httpx` parameters:

```python
async with AsyncProxyWhirl() as rotator:
    await rotator.add_proxy("http://proxy1.example.com:8080")

    # Headers
    response = await rotator.get(
        "https://api.example.com/data",
        headers={"User-Agent": "MyBot/1.0"}
    )

    # Query parameters
    response = await rotator.get(
        "https://api.example.com/search",
        params={"q": "python", "limit": 10}
    )

    # Form data
    response = await rotator.post(
        "https://api.example.com/form",
        data={"field1": "value1", "field2": "value2"}
    )

    # JSON body
    response = await rotator.post(
        "https://api.example.com/api",
        json={"key": "value"}
    )

    # Cookies
    response = await rotator.get(
        "https://api.example.com/protected",
        cookies={"session": "abc123"}
    )
```

## Proxy Management

### Adding Proxies

```python
from proxywhirl import AsyncProxyWhirl, Proxy

async with AsyncProxyWhirl() as rotator:
    # Add from URL string
    await rotator.add_proxy("http://proxy1.example.com:8080")

    # Add from Proxy object
    proxy = Proxy(
        url="http://proxy2.example.com:8080",
        username="user",
        password="pass"
    )
    await rotator.add_proxy(proxy)

    # Check pool size
    print(f"Pool size: {rotator.pool.size}")
```

### Removing Proxies

```python
async with AsyncProxyWhirl() as rotator:
    await rotator.add_proxy("http://proxy1.example.com:8080")
    proxy = await rotator.get_proxy()

    # Remove by proxy ID
    await rotator.remove_proxy(str(proxy.id))

    # Cleanup unhealthy proxies
    removed_count = await rotator.clear_unhealthy_proxies()
    print(f"Removed {removed_count} unhealthy proxies")
```

### Getting Proxy Statistics

```python
async with AsyncProxyWhirl() as rotator:
    await rotator.add_proxy("http://proxy1.example.com:8080")
    await rotator.add_proxy("http://proxy2.example.com:8080")

    # Pool statistics
    stats = rotator.get_pool_stats()
    print(f"Total proxies: {stats['total_proxies']}")
    print(f"Healthy proxies: {stats['healthy_proxies']}")
    print(f"Average success rate: {stats['average_success_rate']:.2%}")

    # Comprehensive statistics with source breakdown
    stats = rotator.get_statistics()
    print(f"Source breakdown: {stats['source_breakdown']}")
```

## Hot-Swapping Strategies

Change rotation strategies at runtime without restarting. For a full list of available strategies and their configuration options, see {doc}`advanced-strategies`.

```python
async with AsyncProxyWhirl(strategy="round-robin") as rotator:
    await rotator.add_proxy("http://proxy1.example.com:8080")
    await rotator.add_proxy("http://proxy2.example.com:8080")

    # Make some requests with round-robin
    await rotator.get("https://httpbin.org/ip")

    # Hot-swap to performance-based strategy
    rotator.set_strategy("performance-based")

    # New requests use performance-based strategy
    await rotator.get("https://httpbin.org/ip")
```

```{note}
Strategy hot-swapping completes in <100ms and is thread-safe. In-flight requests complete with their original strategy.
```

## Error Handling

### Basic Exception Handling

```python
from proxywhirl import (
    AsyncProxyWhirl,
    ProxyPoolEmptyError,
    ProxyConnectionError,
    ProxyAuthenticationError
)

async with AsyncProxyWhirl() as rotator:
    try:
        await rotator.add_proxy("http://proxy1.example.com:8080")
        response = await rotator.get("https://httpbin.org/ip")
        print(response.json())

    except ProxyPoolEmptyError:
        print("No healthy proxies available")

    except ProxyAuthenticationError:
        print("Proxy authentication failed")

    except ProxyConnectionError as e:
        print(f"Connection failed: {e}")
```

### Retry Policy Override

Override retry behavior per request. See {doc}`retry-failover` for complete retry policy configuration, backoff strategies, and circuit breaker details.

```python
from proxywhirl import AsyncProxyWhirl, RetryPolicy

async with AsyncProxyWhirl() as rotator:
    await rotator.add_proxy("http://proxy1.example.com:8080")

    # Custom retry policy for this request
    custom_policy = RetryPolicy(max_attempts=10, base_delay=2.0)

    response = await rotator.get(
        "https://api.example.com/flaky-endpoint",
        retry_policy=custom_policy
    )
```

### Circuit Breaker Management

For detailed circuit breaker configuration, state transitions, and persistence options, see {doc}`retry-failover`.

```python
async with AsyncProxyWhirl() as rotator:
    await rotator.add_proxy("http://proxy1.example.com:8080")
    proxy = await rotator.get_proxy()

    # Get circuit breaker states
    states = rotator.get_circuit_breaker_states()
    for proxy_id, breaker in states.items():
        print(f"Proxy {proxy_id}: {breaker.state}")

    # Manually reset a circuit breaker
    rotator.reset_circuit_breaker(str(proxy.id))
```

## Concurrent Requests with asyncio.gather

### Parallel Requests to Different URLs

```python
import asyncio
from proxywhirl import AsyncProxyWhirl

async def fetch_url(rotator, url):
    """Fetch a single URL through the proxy pool."""
    try:
        response = await rotator.get(url)
        return {"url": url, "status": response.status_code, "data": response.json()}
    except Exception as e:
        return {"url": url, "error": str(e)}

async def main():
    urls = [
        "https://httpbin.org/ip",
        "https://httpbin.org/user-agent",
        "https://httpbin.org/headers",
        "https://httpbin.org/get",
    ]

    async with AsyncProxyWhirl(strategy="round-robin") as rotator:
        # Add proxy pool
        await rotator.add_proxy("http://proxy1.example.com:8080")
        await rotator.add_proxy("http://proxy2.example.com:8080")
        await rotator.add_proxy("http://proxy3.example.com:8080")

        # Fetch all URLs concurrently
        tasks = [fetch_url(rotator, url) for url in urls]
        results = await asyncio.gather(*tasks)

        # Process results
        for result in results:
            if "error" in result:
                print(f"Failed: {result['url']} - {result['error']}")
            else:
                print(f"Success: {result['url']} - Status {result['status']}")

asyncio.run(main())
```

### Rate-Limited Concurrent Scraping

```python
import asyncio
from proxywhirl import AsyncProxyWhirl

async def scrape_with_semaphore(rotator, url, semaphore):
    """Scrape with concurrency limit."""
    async with semaphore:
        response = await rotator.get(url)
        return response.json()

async def main():
    # Limit to 10 concurrent requests
    semaphore = asyncio.Semaphore(10)

    # Generate 100 URLs to scrape
    urls = [f"https://httpbin.org/delay/{i % 3}" for i in range(100)]

    async with AsyncProxyWhirl(strategy="least-used") as rotator:
        # Add proxy pool
        for i in range(5):
            await rotator.add_proxy(f"http://proxy{i}.example.com:8080")

        # Scrape with rate limiting
        tasks = [scrape_with_semaphore(rotator, url, semaphore) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Count successes and failures
        successes = sum(1 for r in results if not isinstance(r, Exception))
        failures = len(results) - successes

        print(f"Completed: {successes} successes, {failures} failures")

asyncio.run(main())
```

### Production-Scale Web Scraping

```python
import asyncio
from typing import List
from dataclasses import dataclass
from proxywhirl import AsyncProxyWhirl, ProxyConfiguration

@dataclass
class ScrapedPage:
    url: str
    status_code: int
    content: str
    proxy_used: str

async def scrape_page(rotator, url) -> ScrapedPage:
    """Scrape a single page with error handling."""
    try:
        response = await rotator.get(url, timeout=30.0)
        proxy = await rotator.get_proxy()

        return ScrapedPage(
            url=url,
            status_code=response.status_code,
            content=response.text,
            proxy_used=str(proxy.url)
        )
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        raise

async def batch_scrape(urls: List[str], max_concurrent: int = 50):
    """Scrape URLs in batches with concurrency control."""
    config = ProxyConfiguration(
        timeout=30,
        pool_connections=100,
        pool_max_keepalive=50,
    )

    async with AsyncProxyWhirl(config=config) as rotator:
        # Use performance-based strategy (swap after init)
        rotator.set_strategy("performance-based")

        # Add proxy pool
        await rotator.add_proxy("http://proxy1.example.com:8080")
        await rotator.add_proxy("http://proxy2.example.com:8080")
        await rotator.add_proxy("http://proxy3.example.com:8080")

        # Create semaphore for rate limiting
        semaphore = asyncio.Semaphore(max_concurrent)

        async def scrape_with_limit(url):
            async with semaphore:
                return await scrape_page(rotator, url)

        # Scrape all URLs
        tasks = [scrape_with_limit(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter successful results
        pages = [r for r in results if isinstance(r, ScrapedPage)]
        errors = [r for r in results if isinstance(r, Exception)]

        print(f"Scraped {len(pages)} pages successfully")
        print(f"Failed: {len(errors)} pages")

        # Get performance statistics
        stats = rotator.get_pool_stats()
        print(f"Average success rate: {stats['average_success_rate']:.2%}")

        return pages

# Usage
urls = [f"https://example.com/page/{i}" for i in range(1000)]
asyncio.run(batch_scrape(urls, max_concurrent=50))
```

## Performance Considerations

### Connection Pooling

`AsyncProxyWhirl` maintains an LRU cache of `httpx.AsyncClient` instances:

```python
from proxywhirl import AsyncProxyWhirl

# Client pool caches up to 100 clients (default)
# LRU eviction prevents unbounded memory growth
async with AsyncProxyWhirl() as rotator:
    # Add many proxies
    for i in range(200):
        await rotator.add_proxy(f"http://proxy{i}.example.com:8080")

    # Only 100 most recently used clients are cached
    # Older clients are automatically closed and evicted
```

### Connection Limits

Configure connection pooling per client:

```python
from proxywhirl import AsyncProxyWhirl, ProxyConfiguration

config = ProxyConfiguration(
    pool_connections=50,        # Max concurrent connections per proxy
    pool_max_keepalive=20,      # Max keep-alive connections per proxy
)

async with AsyncProxyWhirl(config=config) as rotator:
    # Each proxy client has 50 max connections
    # And keeps 20 connections alive for reuse
    pass
```

### Memory Management

The async client automatically manages memory:

- **LRU client pool**: Limits total cached clients to 100
- **Automatic eviction**: Least recently used clients are closed when limit reached
- **Circuit breaker cleanup**: Removed proxies have their circuit breakers deleted
- **Background thread cleanup**: Metrics aggregation thread is stopped on exit

### Performance Benchmarks

Expected performance characteristics:

| Metric | AsyncProxyWhirl | ProxyWhirl (sync) | Notes |
|--------|-------------------|---------------------|-------|
| Strategy hot-swap | <100ms | <100ms | Both use atomic reference swap |
| Request overhead | ~1-2ms | ~1-2ms | Minimal proxy selection overhead |
| Max concurrent requests | 1000+ | ~50-100 | Async scales better with I/O |
| Memory per proxy client | ~50KB | ~50KB | Similar client footprint |
| Client pool eviction | O(1) | O(1) | Both use OrderedDict |
| Throughput (10 proxies, 100 URLs) | ~10-20 req/sec | ~5-10 req/sec | Async is 2x faster |
| Latency (single request) | ~100-200ms | ~100-200ms | Similar for single requests |
| Memory overhead | ~5-10MB | ~5-10MB | Similar baseline |
| CPU usage (100 concurrent) | ~10-20% | ~20-40% | Async is more efficient |

#### Real-World Performance Example

Here's a simple benchmark comparing async vs sync:

```python
import asyncio
import time
from proxywhirl import AsyncProxyWhirl, ProxyWhirl

async def benchmark_async(urls, proxy_url):
    """Benchmark async implementation."""
    start = time.perf_counter()

    async with AsyncProxyWhirl() as rotator:
        await rotator.add_proxy(proxy_url)

        # Concurrent requests with semaphore
        semaphore = asyncio.Semaphore(50)

        async def fetch_with_limit(url):
            async with semaphore:
                try:
                    return await rotator.get(url, timeout=10.0)
                except:
                    return None

        tasks = [fetch_with_limit(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    elapsed = time.perf_counter() - start
    successes = sum(1 for r in results if r is not None)

    return {
        "total_time": elapsed,
        "successes": successes,
        "requests_per_second": len(urls) / elapsed
    }

def benchmark_sync(urls, proxy_url):
    """Benchmark sync implementation."""
    import concurrent.futures

    start = time.perf_counter()

    with ProxyWhirl() as rotator:
        rotator.add_proxy(proxy_url)

        # Threaded concurrent requests
        def fetch(url):
            try:
                return rotator.get(url, timeout=10.0)
            except:
                return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            results = list(executor.map(fetch, urls))

    elapsed = time.perf_counter() - start
    successes = sum(1 for r in results if r is not None)

    return {
        "total_time": elapsed,
        "successes": successes,
        "requests_per_second": len(urls) / elapsed
    }

# Run benchmark
urls = [f"https://httpbin.org/delay/{i % 3}" for i in range(100)]

# Async version
async_results = asyncio.run(benchmark_async(urls, "http://proxy.example.com:8080"))
print(f"Async: {async_results['requests_per_second']:.2f} req/s in {async_results['total_time']:.2f}s")

# Sync version
sync_results = benchmark_sync(urls, "http://proxy.example.com:8080")
print(f"Sync: {sync_results['requests_per_second']:.2f} req/s in {sync_results['total_time']:.2f}s")

# Speedup
speedup = async_results['requests_per_second'] / sync_results['requests_per_second']
print(f"Async is {speedup:.2f}x faster")
```

**Expected Output:**
```
Async: 18.52 req/s in 5.40s
Sync: 9.23 req/s in 10.83s
Async is 2.01x faster
```

#### When Async Shines

Async provides the most benefit when:

1. **High I/O wait time**: Network requests with 100ms+ latency
2. **Many concurrent operations**: 50+ concurrent requests
3. **Large-scale scraping**: 1000+ URLs to fetch
4. **Real-time applications**: WebSocket servers, API gateways
5. **Resource-constrained environments**: Lower CPU usage than threading

#### When Sync is Fine

Sync is sufficient when:

1. **Low concurrency**: <10 concurrent requests
2. **Simple scripts**: One-off automation tasks
3. **Sequential processing**: Requests must happen in order
4. **Simpler debugging**: Stack traces are easier to read
5. **Existing sync codebase**: Integration with Flask, Django, etc.

## Asyncio Integration Patterns

### With FastAPI

:::{tip}
For production FastAPI deployments, see {doc}`deployment-security` for reverse proxy configuration and rate limiting setup.
:::

```python
from fastapi import FastAPI
from proxywhirl import AsyncProxyWhirl

app = FastAPI()

# Initialize rotator at startup
@app.on_event("startup")
async def startup():
    app.state.rotator = AsyncProxyWhirl(strategy="round-robin")
    await app.state.rotator.__aenter__()
    app.state.rotator.set_strategy("performance-based")

    # Add proxies
    await app.state.rotator.add_proxy("http://proxy1.example.com:8080")
    await app.state.rotator.add_proxy("http://proxy2.example.com:8080")

@app.on_event("shutdown")
async def shutdown():
    await app.state.rotator.__aexit__(None, None, None)

@app.get("/fetch")
async def fetch_url(url: str):
    response = await app.state.rotator.get(url)
    return response.json()
```

### With aiohttp

ProxyWhirl can work alongside aiohttp for more advanced use cases:

```python
import aiohttp
from proxywhirl import AsyncProxyWhirl

async def fetch_with_aiohttp(url):
    """Use ProxyWhirl to select proxy, then use aiohttp for request."""
    async with AsyncProxyWhirl() as rotator:
        await rotator.add_proxy("http://proxy1.example.com:8080")
        await rotator.add_proxy("http://proxy2.example.com:8080")

        # Get next proxy from pool
        proxy = await rotator.get_proxy()
        proxy_url = str(proxy.url)

        # Add credentials if present
        if proxy.username and proxy.password:
            username = proxy.username.get_secret_value()
            password = proxy.password.get_secret_value()
            proxy_auth = aiohttp.BasicAuth(username, password)
        else:
            proxy_auth = None

        # Use proxy with aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                proxy=proxy_url,
                proxy_auth=proxy_auth
            ) as response:
                return await response.text()

# Advanced: Rotate proxies with aiohttp for each request
async def fetch_multiple_with_rotation(urls):
    """Fetch multiple URLs, rotating proxies with aiohttp."""
    async with AsyncProxyWhirl(strategy="least-used") as rotator:
        # Add proxy pool
        await rotator.add_proxy("http://proxy1.example.com:8080")
        await rotator.add_proxy("http://proxy2.example.com:8080")
        await rotator.add_proxy("http://proxy3.example.com:8080")

        results = []
        async with aiohttp.ClientSession() as session:
            for url in urls:
                # Get next proxy for this request
                proxy = await rotator.get_proxy()
                proxy_url = str(proxy.url)

                try:
                    async with session.get(url, proxy=proxy_url, timeout=30) as response:
                        data = await response.text()
                        results.append({"url": url, "status": response.status, "data": data})

                        # Record success
                        rotator.strategy.record_result(proxy, success=True, response_time_ms=0.0)
                except Exception as e:
                    # Record failure
                    rotator.strategy.record_result(proxy, success=False, response_time_ms=0.0)
                    results.append({"url": url, "error": str(e)})

        return results
```

```{tip}
While ProxyWhirl's built-in HTTP methods use httpx, you can use the proxy selection logic with any HTTP library. Just call `await rotator.get_proxy()` to get the next proxy and use it with your preferred client.
```

### Advanced httpx Integration

Since ProxyWhirl uses httpx internally, you can access advanced httpx features:

```python
import httpx
from proxywhirl import AsyncProxyWhirl

async def advanced_httpx_example():
    """Use ProxyWhirl's built-in methods with advanced httpx features."""
    async with AsyncProxyWhirl() as rotator:
        await rotator.add_proxy("http://proxy1.example.com:8080")

        # Custom headers
        response = await rotator.get(
            "https://api.example.com/data",
            headers={
                "User-Agent": "Mozilla/5.0 (ProxyWhirl/1.0)",
                "Accept": "application/json",
                "Authorization": "Bearer token123"
            }
        )

        # Streaming responses (useful for large files)
        # Note: ProxyWhirl returns httpx.Response objects
        async def stream_download(url):
            response = await rotator.get(url)

            # Access the underlying response
            async for chunk in response.aiter_bytes(chunk_size=8192):
                # Process chunk
                print(f"Downloaded {len(chunk)} bytes")

        # Custom timeout per request
        response = await rotator.get(
            "https://slow-api.example.com/data",
            timeout=60.0  # Override default timeout
        )

        # Follow redirects (enabled by default)
        response = await rotator.get(
            "https://example.com/redirect",
            follow_redirects=True
        )

        # Access response details
        print(f"Status: {response.status_code}")
        print(f"Headers: {response.headers}")
        print(f"Encoding: {response.encoding}")
        print(f"URL: {response.url}")  # Final URL after redirects

async def custom_httpx_client():
    """Use custom httpx client configuration with ProxyWhirl proxy selection."""
    async with AsyncProxyWhirl() as rotator:
        await rotator.add_proxy("http://proxy1.example.com:8080")

        # Get proxy for manual httpx usage
        proxy = await rotator.get_proxy()
        proxy_url = str(proxy.url)

        # Create custom httpx client with advanced settings
        async with httpx.AsyncClient(
            proxy=proxy_url,
            timeout=httpx.Timeout(10.0, connect=5.0),
            limits=httpx.Limits(max_keepalive_connections=10),
            http2=True,  # Enable HTTP/2
            verify=False,  # Disable SSL verification
        ) as client:
            response = await client.get("https://httpbin.org/ip")
            print(response.json())

            # Record result in ProxyWhirl's strategy
            rotator.strategy.record_result(proxy, success=True, response_time_ms=0.0)
```

### With asyncio.Queue

```python
import asyncio
from proxywhirl import AsyncProxyWhirl

async def worker(queue, rotator, results):
    """Worker that processes URLs from queue."""
    while True:
        url = await queue.get()

        if url is None:  # Sentinel for shutdown
            break

        try:
            response = await rotator.get(url)
            results.append({"url": url, "status": response.status_code})
        except Exception as e:
            results.append({"url": url, "error": str(e)})
        finally:
            queue.task_done()

async def main():
    urls = [f"https://httpbin.org/delay/{i % 3}" for i in range(100)]
    queue = asyncio.Queue()
    results = []

    # Populate queue
    for url in urls:
        await queue.put(url)

    async with AsyncProxyWhirl() as rotator:
        await rotator.add_proxy("http://proxy1.example.com:8080")
        await rotator.add_proxy("http://proxy2.example.com:8080")

        # Create workers
        num_workers = 10
        workers = [
            asyncio.create_task(worker(queue, rotator, results))
            for _ in range(num_workers)
        ]

        # Wait for all tasks to complete
        await queue.join()

        # Stop workers
        for _ in range(num_workers):
            await queue.put(None)

        await asyncio.gather(*workers)

    print(f"Processed {len(results)} URLs")

asyncio.run(main())
```

## Comparison: Async vs Sync

### Feature Parity

Both `AsyncProxyWhirl` and `ProxyWhirl` support:

- ✅ All rotation strategies (round-robin, random, weighted, etc.)
- ✅ Retry logic with configurable backoff
- ✅ Circuit breakers for automatic failover
- ✅ Connection pooling and keep-alive
- ✅ Hot-swapping strategies
- ✅ Health monitoring and statistics
- ✅ Proxy authentication
- ✅ SSL verification control
- ✅ Custom timeouts and configuration

### Key Differences

| Feature | AsyncProxyWhirl | ProxyWhirl |
|---------|-------------------|--------------|
| **Execution Model** | `async`/`await` | Synchronous |
| **Concurrency** | Native (asyncio) | Threading |
| **HTTP Client** | `httpx.AsyncClient` | `httpx.Client` |
| **Context Manager** | `async with` | `with` |
| **Method Calls** | `await rotator.get()` | `rotator.get()` |
| **Background Tasks** | `asyncio.Event` | `threading.Timer` |
| **Client Pool Lock** | `asyncio.Lock` | `threading.Lock` |
| **Best For** | I/O-bound, high concurrency | CPU-bound, simple scripts |

### Migration Example

Converting sync to async is straightforward:

```python
# Sync version
from proxywhirl import ProxyWhirl

with ProxyWhirl() as rotator:
    rotator.add_proxy("http://proxy1.example.com:8080")
    response = rotator.get("https://httpbin.org/ip")
    print(response.json())
```

```python
# Async version
import asyncio
from proxywhirl import AsyncProxyWhirl

async def main():
    async with AsyncProxyWhirl() as rotator:
        await rotator.add_proxy("http://proxy1.example.com:8080")
        response = await rotator.get("https://httpbin.org/ip")
        print(response.json())

asyncio.run(main())
```

Changes required:
1. Add `import asyncio`
2. Change `ProxyWhirl` → `AsyncProxyWhirl`
3. Change `with` → `async with`
4. Add `await` before async method calls (`add_proxy`, `get`, etc.)
5. Wrap in `async def main()` and call with `asyncio.run(main())`

## Best Practices and Common Patterns

### 1. Always Use Context Managers

```python
# ✅ GOOD: Automatic cleanup
async with AsyncProxyWhirl() as rotator:
    await rotator.add_proxy("http://proxy1.example.com:8080")
    response = await rotator.get("https://httpbin.org/ip")

# ❌ BAD: Manual cleanup required, easy to forget
rotator = AsyncProxyWhirl()
await rotator.__aenter__()
response = await rotator.get("https://httpbin.org/ip")
# Forgot to call __aexit__! Resources leaked!
```

### 2. Use Semaphores for Concurrency Control

```python
# ✅ GOOD: Controlled concurrency
async def scrape_urls(urls):
    semaphore = asyncio.Semaphore(50)  # Max 50 concurrent requests

    async def fetch_with_limit(url):
        async with semaphore:
            return await rotator.get(url)

    async with AsyncProxyWhirl() as rotator:
        await rotator.add_proxy("http://proxy1.example.com:8080")
        tasks = [fetch_with_limit(url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)

# ❌ BAD: Unbounded concurrency can crash your program
async def scrape_urls_bad(urls):
    async with AsyncProxyWhirl() as rotator:
        await rotator.add_proxy("http://proxy1.example.com:8080")
        # Creating 10,000 tasks at once! Memory explosion!
        tasks = [rotator.get(url) for url in urls]
        return await asyncio.gather(*tasks)
```

### 3. Handle Exceptions Gracefully

```python
# ✅ GOOD: Per-request error handling with gather
async def fetch_all(urls):
    async with AsyncProxyWhirl() as rotator:
        await rotator.add_proxy("http://proxy1.example.com:8080")

        async def safe_fetch(url):
            try:
                response = await rotator.get(url, timeout=30.0)
                return {"url": url, "status": response.status_code, "data": response.json()}
            except Exception as e:
                return {"url": url, "error": str(e)}

        tasks = [safe_fetch(url) for url in urls]
        # return_exceptions=True keeps going even if some fail
        return await asyncio.gather(*tasks, return_exceptions=True)

# ❌ BAD: One failure stops everything
async def fetch_all_bad(urls):
    async with AsyncProxyWhirl() as rotator:
        await rotator.add_proxy("http://proxy1.example.com:8080")
        tasks = [rotator.get(url) for url in urls]
        # First exception stops all other tasks!
        return await asyncio.gather(*tasks)
```

### 4. Reuse Rotator Instances

```python
# ✅ GOOD: Single rotator for entire application
class Application:
    def __init__(self):
        self.rotator = None

    async def startup(self):
        self.rotator = AsyncProxyWhirl(strategy="round-robin")
        await self.rotator.__aenter__()
        self.rotator.set_strategy("performance-based")
        await self.rotator.add_proxy("http://proxy1.example.com:8080")
        await self.rotator.add_proxy("http://proxy2.example.com:8080")

    async def shutdown(self):
        await self.rotator.__aexit__(None, None, None)

    async def fetch(self, url):
        return await self.rotator.get(url)

# ❌ BAD: Creating new rotator for each request
async def fetch_bad(url):
    # Expensive: creates new clients, circuit breakers, metrics every time!
    async with AsyncProxyWhirl() as rotator:
        await rotator.add_proxy("http://proxy1.example.com:8080")
        return await rotator.get(url)
```

### 5. Monitor Circuit Breaker States

```python
# ✅ GOOD: Check circuit breakers periodically
async def health_check_task(rotator):
    """Background task to monitor proxy health."""
    while True:
        await asyncio.sleep(60)  # Check every minute

        states = rotator.get_circuit_breaker_states()
        open_breakers = [
            proxy_id for proxy_id, cb in states.items()
            if cb.state.name == "OPEN"
        ]

        if open_breakers:
            print(f"Warning: {len(open_breakers)} proxies have open circuit breakers")
            # Optional: Remove unhealthy proxies
            await rotator.clear_unhealthy_proxies()

async def main():
    async with AsyncProxyWhirl() as rotator:
        await rotator.add_proxy("http://proxy1.example.com:8080")

        # Start background health monitoring
        health_task = asyncio.create_task(health_check_task(rotator))

        # Do your work...
        await rotator.get("https://httpbin.org/ip")

        # Cleanup
        health_task.cancel()
```

### 6. Use Appropriate Retry Policies

```python
# ✅ GOOD: Different retry policies for different endpoints
async with AsyncProxyWhirl() as rotator:
    await rotator.add_proxy("http://proxy1.example.com:8080")

    # Critical endpoint: More aggressive retries
    critical_policy = RetryPolicy(max_attempts=10, base_delay=2.0)
    critical_data = await rotator.get(
        "https://api.example.com/critical",
        retry_policy=critical_policy
    )

    # Non-critical: Fail fast
    fast_fail_policy = RetryPolicy(max_attempts=2, base_delay=1.0)
    optional_data = await rotator.get(
        "https://api.example.com/optional",
        retry_policy=fast_fail_policy
    )
```

### 7. Profile and Optimize Connection Pooling

```python
# ✅ GOOD: Configure pool limits based on your workload
from proxywhirl import AsyncProxyWhirl, ProxyConfiguration

# For high-throughput scraping (many concurrent requests)
high_throughput_config = ProxyConfiguration(
    pool_connections=100,      # More concurrent connections
    pool_max_keepalive=50,     # More keep-alive connections
    timeout=30,
)

async with AsyncProxyWhirl(config=high_throughput_config) as rotator:
    # Can handle 100+ concurrent requests efficiently
    pass

# For low-latency API calls (fewer but faster requests)
low_latency_config = ProxyConfiguration(
    pool_connections=20,       # Fewer connections
    pool_max_keepalive=10,     # Fewer keep-alive
    timeout=5,                 # Shorter timeout
)

async with AsyncProxyWhirl(config=low_latency_config) as rotator:
    # Optimized for speed, not throughput
    pass
```

### 8. Use Strategy Hot-Swapping for Adaptive Behavior

```python
# ✅ GOOD: Adapt strategy based on performance
async def adaptive_scraping(urls):
    async with AsyncProxyWhirl(strategy="round-robin") as rotator:
        await rotator.add_proxy("http://proxy1.example.com:8080")
        await rotator.add_proxy("http://proxy2.example.com:8080")

        # Start with round-robin
        results = []
        for i, url in enumerate(urls):
            response = await rotator.get(url)
            results.append(response)

            # Switch to performance-based after collecting data
            if i == 50:
                stats = rotator.get_pool_stats()
                if stats['average_success_rate'] < 0.8:
                    rotator.set_strategy("performance-based")
                    print("Switched to performance-based strategy")

        return results
```

### 9. Clean Up Resources Properly

```python
# ✅ GOOD: Clean up unhealthy proxies periodically
async def periodic_cleanup(rotator):
    """Background task to clean up failed proxies."""
    while True:
        await asyncio.sleep(300)  # Every 5 minutes

        removed = await rotator.clear_unhealthy_proxies()
        if removed > 0:
            print(f"Cleaned up {removed} unhealthy proxies")

            # Get fresh statistics
            stats = rotator.get_pool_stats()
            print(f"Pool now has {stats['healthy_proxies']} healthy proxies")

async def main():
    async with AsyncProxyWhirl() as rotator:
        # Add proxies
        await rotator.add_proxy("http://proxy1.example.com:8080")
        await rotator.add_proxy("http://proxy2.example.com:8080")

        # Start cleanup task
        cleanup_task = asyncio.create_task(periodic_cleanup(rotator))

        try:
            # Do work...
            await rotator.get("https://httpbin.org/ip")
        finally:
            cleanup_task.cancel()
            await asyncio.gather(cleanup_task, return_exceptions=True)
```

### 10. Avoid Common Pitfalls

```python
# ❌ COMMON PITFALL 1: Blocking operations in async code
async def bad_example():
    async with AsyncProxyWhirl() as rotator:
        await rotator.add_proxy("http://proxy1.example.com:8080")

        # BAD: time.sleep blocks the event loop!
        import time
        time.sleep(1)  # Use asyncio.sleep(1) instead

# ❌ COMMON PITFALL 2: Not awaiting async operations
async def bad_example2():
    async with AsyncProxyWhirl() as rotator:
        # BAD: Forgot to await! This creates a coroutine but doesn't run it!
        rotator.add_proxy("http://proxy1.example.com:8080")

        # Should be: await rotator.add_proxy(...)

# ❌ COMMON PITFALL 3: Creating too many rotator instances
async def bad_example3():
    urls = ["https://example.com"] * 100

    # BAD: Creates 100 rotator instances, wastes resources!
    for url in urls:
        async with AsyncProxyWhirl() as rotator:
            await rotator.add_proxy("http://proxy1.example.com:8080")
            await rotator.get(url)

    # GOOD: Reuse single rotator instance
    async with AsyncProxyWhirl() as rotator:
        await rotator.add_proxy("http://proxy1.example.com:8080")
        for url in urls:
            await rotator.get(url)

# ❌ COMMON PITFALL 4: Ignoring circuit breaker states
async def bad_example4():
    async with AsyncProxyWhirl() as rotator:
        await rotator.add_proxy("http://bad-proxy.example.com:8080")

        # BAD: Keeps trying even after circuit breaker opens
        for _ in range(1000):
            try:
                await rotator.get("https://httpbin.org/ip")
            except:
                pass  # Silently failing, doesn't check breaker state

        # GOOD: Monitor circuit breaker states
        states = rotator.get_circuit_breaker_states()
        if all(cb.state.name == "OPEN" for cb in states.values()):
            print("All circuit breakers open, stopping requests")
```

## See Also

::::{grid} 2
:gutter: 3

:::{grid-item-card} Advanced Strategies
:link: /guides/advanced-strategies
:link-type: doc

Performance-based, geo-targeted, session persistence, and composite strategy patterns.
:::

:::{grid-item-card} Retry & Failover
:link: /guides/retry-failover
:link-type: doc

Circuit breakers, backoff strategies, and intelligent proxy failover.
:::

:::{grid-item-card} Caching Subsystem
:link: /guides/caching
:link-type: doc

Three-tier caching architecture, encryption, and performance tuning.
:::

:::{grid-item-card} CLI Reference
:link: /guides/cli-reference
:link-type: doc

Command-line proxy management, health checks, and data export.
:::

:::{grid-item-card} MCP Server
:link: /guides/mcp-server
:link-type: doc

AI assistant integration via the Model Context Protocol.
:::

:::{grid-item-card} REST API Reference
:link: /reference/rest-api
:link-type: doc

Full REST API documentation for the ProxyWhirl HTTP server.
:::

:::{grid-item-card} Python API Reference
:link: /reference/python-api
:link-type: doc

Complete Python API docs for `AsyncProxyWhirl`, `ProxyWhirl`, and all models.
:::

:::{grid-item-card} Rotation Strategies Overview
:link: /getting-started/rotation-strategies
:link-type: doc

Getting started with basic rotation strategies and selection.
:::
::::
