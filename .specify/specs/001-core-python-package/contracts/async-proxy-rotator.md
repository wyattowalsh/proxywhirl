# AsyncProxyRotator API Contract

**Component**: `AsyncProxyRotator` (Async API)  
**Module**: `proxywhirl.client`

## Class Definition

```python
class AsyncProxyRotator:
    """
    Asynchronous proxy rotation client.
    
    Manages a pool of proxies and rotates through them using a configurable
    strategy. All methods are async (non-blocking).
    """
```

---

## Constructor

### `__init__()`

**Signature**:

```python
def __init__(
    self,
    proxies: list[str | Proxy] | None = None,
    strategy: RotationStrategy | Literal["round-robin", "random", "weighted", "least-used"] = "round-robin",
    config: ProxyConfiguration | None = None,
    pool_name: str = "default",
) -> None:
    """
    Initialize an AsyncProxyRotator instance.
    
    Args:
        proxies: List of proxy URLs (strings) or Proxy objects
        strategy: Rotation strategy instance or strategy name
        config: Configuration object (uses defaults if not provided)
        pool_name: Name for the internal proxy pool
        
    Raises:
        ProxyValidationError: If any proxy URL is invalid
        ValueError: If strategy name is not recognized
    """
```

**Example**:

```python
# With URLs
rotator = AsyncProxyRotator(
    proxies=["http://proxy1.com:8080", "http://proxy2.com:8080"],
    strategy="round-robin"
)

# With Proxy objects
proxy1 = Proxy(url="http://proxy1.com:8080", username="user", password="pass")
rotator = AsyncProxyRotator(proxies=[proxy1], strategy="weighted")
```

---

## HTTP Methods

### `get()`

**Signature**:

```python
async def get(
    self,
    url: str,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    **kwargs: Any,
) -> httpx.Response:
    """
    Perform an async GET request through a rotated proxy.
    
    Args:
        url: Target URL for the request
        params: Query parameters
        headers: HTTP headers
        **kwargs: Additional arguments passed to httpx.AsyncClient.request()
        
    Returns:
        httpx.Response object
        
    Raises:
        ProxyPoolEmptyError: If no proxies are available
        ProxyConnectionError: If all retry attempts fail
        httpx.HTTPError: For HTTP-level errors
    """
```

**Example**:

```python
response = await rotator.get("https://api.example.com/data", params={"key": "value"})
print(response.status_code)
data = response.json()
```

---

### `post()`

**Signature**:

```python
async def post(
    self,
    url: str,
    data: dict[str, Any] | str | bytes | None = None,
    json: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    **kwargs: Any,
) -> httpx.Response:
    """
    Perform an async POST request through a rotated proxy.
    
    Args:
        url: Target URL for the request
        data: Form data or raw body
        json: JSON body (alternative to data)
        headers: HTTP headers
        **kwargs: Additional arguments passed to httpx.AsyncClient.request()
        
    Returns:
        httpx.Response object
        
    Raises:
        ProxyPoolEmptyError: If no proxies are available
        ProxyConnectionError: If all retry attempts fail
    """
```

**Example**:

```python
response = await rotator.post(
    "https://api.example.com/submit",
    json={"field": "value"}
)
```

---

### `request()`

**Signature**:

```python
async def request(
    self,
    method: str,
    url: str,
    **kwargs: Any,
) -> httpx.Response:
    """
    Perform a generic async HTTP request through a rotated proxy.
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        url: Target URL
        **kwargs: Arguments passed to httpx.AsyncClient.request()
        
    Returns:
        httpx.Response object
        
    Raises:
        ProxyPoolEmptyError: If no proxies are available
        ProxyConnectionError: If all retry attempts fail
    """
```

**Example**:

```python
response = await rotator.request("PATCH", "https://api.example.com/resource/123", json={...})
```

---

## Pool Management Methods

### `add_proxy()`

**Signature**:

```python
async def add_proxy(
    self,
    proxy: str | Proxy,
) -> None:
    """
    Add a proxy to the pool (async version for consistency).
    
    Args:
        proxy: Proxy URL string or Proxy object
        
    Raises:
        ProxyValidationError: If proxy URL is invalid
        ValueError: If pool is at max capacity
    """
```

**Example**:

```python
await rotator.add_proxy("http://proxy3.com:8080")
```

---

### `remove_proxy()`

**Signature**:

```python
async def remove_proxy(
    self,
    proxy_id: UUID | str,
) -> None:
    """
    Remove a proxy from the pool by ID or URL.
    
    Args:
        proxy_id: UUID of the proxy or URL string
        
    Raises:
        ValueError: If proxy not found in pool
    """
```

**Example**:

```python
await rotator.remove_proxy(proxy.id)
```

---

### `get_pool_stats()`

**Signature**:

```python
async def get_pool_stats(self) -> dict[str, Any]:
    """
    Get statistics about the proxy pool.
    
    Returns:
        Dictionary with pool statistics:
        - total_proxies: Total number of proxies
        - healthy_proxies: Number of healthy proxies
        - total_requests: Total requests made
        - overall_success_rate: Success rate across all proxies
        - current_strategy: Name of the rotation strategy
    """
```

**Example**:

```python
stats = await rotator.get_pool_stats()
print(f"Healthy proxies: {stats['healthy_proxies']}/{stats['total_proxies']}")
```

---

### `clear_unhealthy_proxies()`

**Signature**:

```python
async def clear_unhealthy_proxies(self) -> int:
    """
    Remove all unhealthy proxies from the pool.
    
    Returns:
        Number of proxies removed
    """
```

**Example**:

```python
removed_count = await rotator.clear_unhealthy_proxies()
print(f"Removed {removed_count} unhealthy proxies")
```

---

## Concurrent Request Methods

### `batch_get()`

**Signature**:

```python
async def batch_get(
    self,
    urls: list[str],
    max_concurrent: int = 10,
    **kwargs: Any,
) -> list[httpx.Response | Exception]:
    """
    Perform multiple GET requests concurrently through rotated proxies.
    
    Args:
        urls: List of URLs to request
        max_concurrent: Maximum number of concurrent requests
        **kwargs: Additional arguments passed to each request
        
    Returns:
        List of Response objects or Exceptions (in same order as urls)
    """
```

**Example**:

```python
urls = [f"https://api.example.com/data/{i}" for i in range(100)]
responses = await rotator.batch_get(urls, max_concurrent=20)

for url, response in zip(urls, responses):
    if isinstance(response, Exception):
        print(f"{url} failed: {response}")
    else:
        print(f"{url} succeeded: {response.status_code}")
```

---

### `stream_get()`

**Signature**:

```python
async def stream_get(
    self,
    url: str,
    **kwargs: Any,
) -> AsyncIterator[bytes]:
    """
    Stream response content from a GET request.
    
    Args:
        url: Target URL
        **kwargs: Additional arguments passed to httpx.AsyncClient.stream()
        
    Yields:
        Chunks of response content as bytes
        
    Raises:
        ProxyPoolEmptyError: If no proxies are available
        ProxyConnectionError: If connection fails
    """
```

**Example**:

```python
async for chunk in rotator.stream_get("https://example.com/large-file.bin"):
    process_chunk(chunk)
```

---

## Context Manager Support

### `__aenter__()` / `__aexit__()`

**Signature**:

```python
async def __aenter__(self) -> "AsyncProxyRotator":
    """Enter async context manager."""
    return self

async def __aexit__(
    self,
    exc_type: type[BaseException] | None,
    exc_val: BaseException | None,
    exc_tb: TracebackType | None,
) -> None:
    """Exit async context manager and cleanup resources."""
    await self.aclose()
```

**Example**:

```python
async with AsyncProxyRotator(proxies=[...]) as rotator:
    response = await rotator.get("https://example.com")
# Cleanup happens automatically
```

---

### `aclose()`

**Signature**:

```python
async def aclose(self) -> None:
    """
    Close all async connections and cleanup resources.
    
    Should be called when done using the rotator, especially if not using
    async context manager.
    """
```

**Example**:

```python
rotator = AsyncProxyRotator(proxies=[...])
try:
    response = await rotator.get("https://example.com")
finally:
    await rotator.aclose()
```

---

## Properties

### `pool`

**Signature**:

```python
@property
def pool(self) -> ProxyPool:
    """Get the underlying ProxyPool instance."""
```

**Example**:

```python
print(f"Pool size: {rotator.pool.size}")
```

---

### `config`

**Signature**:

```python
@property
def config(self) -> ProxyConfiguration:
    """Get the configuration object."""
```

**Example**:

```python
print(f"Timeout: {rotator.config.timeout}s")
```

---

## Error Handling

All methods may raise:

- `ProxyPoolEmptyError`: When pool has no available proxies
- `ProxyConnectionError`: When all retry attempts fail
- `ProxyAuthenticationError`: When proxy authentication fails
- `ProxyValidationError`: When proxy URL or configuration is invalid
- `httpx.HTTPError`: For HTTP-level errors

**Example**:

```python
from proxywhirl.exceptions import ProxyPoolEmptyError, ProxyConnectionError

try:
    response = await rotator.get("https://example.com")
except ProxyPoolEmptyError:
    print("No proxies available")
except ProxyConnectionError as e:
    print(f"All proxies failed: {e}")
except httpx.HTTPError as e:
    print(f"HTTP error: {e}")
```

---

## Concurrency Safety

✅ **Async-safe** - Can be used with `asyncio.gather()` and other async concurrency primitives.

⚠️ **Not thread-safe** - Use separate instances per thread if mixing async with threading.

**Example**:

```python
import asyncio

async def main():
    async with AsyncProxyRotator(proxies=[...]) as rotator:
        # Make 100 concurrent requests
        tasks = [rotator.get(f"https://api.example.com/data/{i}") for i in range(100)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"Request {i} failed: {response}")
            else:
                print(f"Request {i}: {response.status_code}")

asyncio.run(main())
```

---

## Performance Characteristics

- **Proxy Selection**: O(1) for round-robin/random, O(n) for weighted/least-used
- **Request Overhead**: <50ms for proxy selection and setup
- **Concurrency**: Supports 1000+ concurrent requests with proper connection pooling
- **Connection Pooling**: Reuses async connections per proxy
- **Memory**: ~1KB per proxy + httpx async client overhead

---

## Complete Usage Example

```python
import asyncio
from proxywhirl import AsyncProxyRotator, ProxyConfiguration

async def main():
    # Configure
    config = ProxyConfiguration(
        timeout=30,
        max_retries=3,
        verify_ssl=True,
        pool_connections=50,  # Support high concurrency
        health_check_enabled=True
    )
    
    # Create rotator
    proxies = [
        "http://user1:pass1@proxy1.com:8080",
        "http://user2:pass2@proxy2.com:8080",
        "http://user3:pass3@proxy3.com:8080",
    ]
    
    async with AsyncProxyRotator(proxies=proxies, strategy="weighted", config=config) as rotator:
        # Single request
        response = await rotator.get("https://api.example.com/data")
        print(f"Single request: {response.status_code}")
        
        # Batch requests
        urls = [f"https://api.example.com/data/{i}" for i in range(50)]
        responses = await rotator.batch_get(urls, max_concurrent=10)
        success_count = sum(1 for r in responses if not isinstance(r, Exception))
        print(f"Batch: {success_count}/{len(urls)} succeeded")
        
        # Stream large file
        async for chunk in rotator.stream_get("https://example.com/large-file.bin"):
            # Process chunk
            pass
        
        # Check stats
        stats = await rotator.get_pool_stats()
        print(f"Success rate: {stats['overall_success_rate']:.2%}")
        
        # Cleanup dead proxies
        removed = await rotator.clear_unhealthy_proxies()
        print(f"Removed {removed} unhealthy proxies")

asyncio.run(main())
```

---

## Differences from Sync API

| Feature | Sync (`ProxyRotator`) | Async (`AsyncProxyRotator`) |
|---------|------------------------|------------------------------|
| All methods | Blocking | Non-blocking (await) |
| HTTP client | `httpx.Client` | `httpx.AsyncClient` |
| Context manager | `with` / `__enter__` | `async with` / `__aenter__` |
| Cleanup | `.close()` | `await .aclose()` |
| Batch requests | Not available | `batch_get()` |
| Streaming | Not available | `stream_get()` |
| Concurrency | Thread-based | Async-based (event loop) |
| Performance | Good for I/O bound | Excellent for high concurrency |

---

## Migration from Sync to Async

```python
# Sync version
from proxywhirl import ProxyRotator

with ProxyRotator(proxies=[...]) as rotator:
    response = rotator.get("https://example.com")

# Async version
import asyncio
from proxywhirl import AsyncProxyRotator

async def main():
    async with AsyncProxyRotator(proxies=[...]) as rotator:
        response = await rotator.get("https://example.com")

asyncio.run(main())
```
