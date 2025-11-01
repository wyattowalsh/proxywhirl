# ProxyRotator API Contract

**Component**: `ProxyRotator` (Sync API)  
**Module**: `proxywhirl.client`

## Class Definition

```python
class ProxyRotator:
    """
    Synchronous proxy rotation client.
    
    Manages a pool of proxies and rotates through them using a configurable
    strategy. All methods are synchronous (blocking).
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
    auto_fetch_sources: list[str | ProxySourceConfig] | None = None,
    auto_fetch_interval: int = 3600,
    validate_fetched: bool = True,
) -> None:
    """
    Initialize a ProxyRotator instance.
    
    Args:
        proxies: List of proxy URLs (strings) or Proxy objects (user-provided)
        strategy: Rotation strategy instance or strategy name
        config: Configuration object (uses defaults if not provided)
        pool_name: Name for the internal proxy pool
        auto_fetch_sources: URLs or configs to fetch proxies from automatically
        auto_fetch_interval: Interval in seconds for auto-refresh (0 = disabled)
        validate_fetched: Validate auto-fetched proxies before adding to pool
        
    Raises:
        ProxyValidationError: If any proxy URL is invalid
        ValueError: If strategy name is not recognized
    """
```

**Example**:

```python
# With URLs only
rotator = ProxyRotator(
    proxies=["http://proxy1.com:8080", "http://proxy2.com:8080"],
    strategy="round-robin"
)

# With Proxy objects
proxy1 = Proxy(url="http://proxy1.com:8080", username="user", password="pass")
rotator = ProxyRotator(proxies=[proxy1], strategy="weighted")

# With auto-fetch from free sources
rotator = ProxyRotator(
    proxies=["http://my-premium-proxy.com:8080"],  # User proxies (priority)
    auto_fetch_sources=[
        "https://api.proxyscrape.com/v2/?request=get&protocol=http&format=json",
        "https://www.free-proxy-list.net"
    ],
    auto_fetch_interval=3600,  # Refresh every hour
    validate_fetched=True
)

# With custom source configuration
from proxywhirl import ProxySourceConfig, ProxyFormat

rotator = ProxyRotator(
    auto_fetch_sources=[
        ProxySourceConfig(
            url="https://api.example.com/proxies",
            format=ProxyFormat.JSON,
            headers={"API-Key": "my-key"},
            priority=5
        )
    ]
)

# With custom config
config = ProxyConfiguration(timeout=45, max_retries=5)
rotator = ProxyRotator(proxies=[...], config=config)
```

---

## HTTP Methods

### `get()`

**Signature**:

```python
def get(
    self,
    url: str,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    **kwargs: Any,
) -> httpx.Response:
    """
    Perform a GET request through a rotated proxy.
    
    Args:
        url: Target URL for the request
        params: Query parameters
        headers: HTTP headers
        **kwargs: Additional arguments passed to httpx.request()
        
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
response = rotator.get("https://api.example.com/data", params={"key": "value"})
print(response.status_code)
print(response.json())
```

---

### `post()`

**Signature**:

```python
def post(
    self,
    url: str,
    data: dict[str, Any] | str | bytes | None = None,
    json: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    **kwargs: Any,
) -> httpx.Response:
    """
    Perform a POST request through a rotated proxy.
    
    Args:
        url: Target URL for the request
        data: Form data or raw body
        json: JSON body (alternative to data)
        headers: HTTP headers
        **kwargs: Additional arguments passed to httpx.request()
        
    Returns:
        httpx.Response object
        
    Raises:
        ProxyPoolEmptyError: If no proxies are available
        ProxyConnectionError: If all retry attempts fail
    """
```

**Example**:

```python
response = rotator.post(
    "https://api.example.com/submit",
    json={"field": "value"}
)
```

---

### `request()`

**Signature**:

```python
def request(
    self,
    method: str,
    url: str,
    **kwargs: Any,
) -> httpx.Response:
    """
    Perform a generic HTTP request through a rotated proxy.
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        url: Target URL
        **kwargs: Arguments passed to httpx.request()
        
    Returns:
        httpx.Response object
        
    Raises:
        ProxyPoolEmptyError: If no proxies are available
        ProxyConnectionError: If all retry attempts fail
    """
```

**Example**:

```python
response = rotator.request("PATCH", "https://api.example.com/resource/123", json={...})
```

---

## Pool Management Methods

### `add_proxy()`

**Signature**:

```python
def add_proxy(
    self,
    proxy: str | Proxy,
) -> None:
    """
    Add a proxy to the pool.
    
    Args:
        proxy: Proxy URL string or Proxy object
        
    Raises:
        ProxyValidationError: If proxy URL is invalid
        ValueError: If pool is at max capacity
    """
```

**Example**:

```python
rotator.add_proxy("http://proxy3.com:8080")
rotator.add_proxy(Proxy(url="http://proxy4.com:8080", username="user", password="pass"))
```

---

### `remove_proxy()`

**Signature**:

```python
def remove_proxy(
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
rotator.remove_proxy(proxy.id)
rotator.remove_proxy("http://proxy1.com:8080")
```

---

### `get_pool_stats()`

**Signature**:

```python
def get_pool_stats(self) -> dict[str, Any]:
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
stats = rotator.get_pool_stats()
print(f"Healthy proxies: {stats['healthy_proxies']}/{stats['total_proxies']}")
print(f"Success rate: {stats['overall_success_rate']:.2%}")
```

---

### `clear_unhealthy_proxies()`

**Signature**:

```python
def clear_unhealthy_proxies(self) -> int:
    """
    Remove all unhealthy proxies from the pool.
    
    Returns:
        Number of proxies removed
    """
```

**Example**:

```python
removed_count = rotator.clear_unhealthy_proxies()
print(f"Removed {removed_count} unhealthy proxies")
```

---

### `reset_strategy()`

**Signature**:

```python
def reset_strategy(self) -> None:
    """
    Reset the rotation strategy to its initial state.
    
    Useful for strategies that maintain internal state (e.g., round-robin index).
    """
```

**Example**:

```python
rotator.reset_strategy()  # Start round-robin from beginning
```

---

### `refresh_proxies()`

**Signature**:

```python
def refresh_proxies(self) -> dict[str, int]:
    """
    Manually trigger proxy refresh from all auto-fetch sources.
    
    Returns:
        Dictionary with refresh statistics:
        - total_fetched: Total proxies fetched from all sources
        - valid_count: Number of valid proxies added
        - duplicate_count: Number of duplicates skipped
        - failed_sources: List of source URLs that failed
    
    Raises:
        ValueError: If no auto-fetch sources configured
    """
```

**Example**:

```python
stats = rotator.refresh_proxies()
print(f"Fetched {stats['valid_count']} new proxies")
print(f"Skipped {stats['duplicate_count']} duplicates")
if stats['failed_sources']:
    print(f"Failed sources: {stats['failed_sources']}")
```

---

### `add_fetch_source()`

**Signature**:

```python
def add_fetch_source(
    self,
    source: str | ProxySourceConfig,
) -> None:
    """
    Add a new proxy fetch source.
    
    Args:
        source: URL string or ProxySourceConfig object
        
    Raises:
        ValueError: If source URL is invalid or already exists
    """
```

**Example**:

```python
# Add simple URL
rotator.add_fetch_source("https://api.newproxysite.com/list")

# Add with configuration
from proxywhirl import ProxySourceConfig, ProxyFormat

rotator.add_fetch_source(
    ProxySourceConfig(
        url="https://api.example.com/proxies",
        format=ProxyFormat.JSON,
        priority=10
    )
)
```

---

### `remove_fetch_source()`

**Signature**:

```python
def remove_fetch_source(
    self,
    source_url: str,
) -> None:
    """
    Remove a proxy fetch source.
    
    Args:
        source_url: URL of the source to remove
        
    Raises:
        ValueError: If source not found
    """
```

**Example**:

```python
```python
rotator.remove_fetch_source("https://api.slowproxysite.com/list")
```

---

## File Storage Methods

### `save_to_file()`

**Signature**:

```python
def save_to_file(
    self,
    path: str | Path,
    compression: bool = False,
    pretty_print: bool = True,
) -> None:
    """
    Save the proxy pool to a JSON file.
    
    Args:
        path: File path to save to
        compression: Enable gzip compression
        pretty_print: Human-readable formatting
        
    Raises:
        IOError: If file cannot be written
    """
```

**Example**:

```python
from pathlib import Path

# Save to JSON
rotator.save_to_file("./data/proxies.json")

# Save with compression
rotator.save_to_file(Path("./data/proxies.json.gz"), compression=True)
```

---

### `load_from_file()` (Class Method)

**Signature**:

```python
@classmethod
def load_from_file(
    cls,
    path: str | Path,
    compression: bool | None = None,
) -> "ProxyRotator":
    """
    Load a proxy pool from a JSON file.
    
    Args:
        path: File path to load from
        compression: Enable gzip decompression (auto-detected if None)
        
    Returns:
        ProxyRotator instance with loaded pool
        
    Raises:
        IOError: If file cannot be read
        ValueError: If file format is invalid
    """
```

**Example**:

```python
# Load from file
rotator = ProxyRotator.load_from_file("./data/proxies.json")

# Load compressed file
rotator = ProxyRotator.load_from_file("./data/proxies.json.gz", compression=True)
```

---

### `auto_save_start()`

**Signature**:

```python
def auto_save_start(
    self,
    path: str | Path,
    interval: int = 300,
    compression: bool = False,
) -> None:
    """
    Start background auto-save to file.
    
    Args:
        path: File path to save to
        interval: Save interval in seconds
        compression: Enable gzip compression
        
    Raises:
        ValueError: If auto-save already started
    """
```

**Example**:

```python
# Auto-save every 5 minutes
rotator.auto_save_start("./data/proxies.json", interval=300)
```

---

### `auto_save_stop()`

**Signature**:

```python
def auto_save_stop(self) -> None:
    """
    Stop background auto-save.
    
    Performs final save before stopping.
    """
```

**Example**:

```python
rotator.auto_save_stop()
```

---

## Context Manager & Cleanup

### `__enter__()` / `__exit__()`
```

---

### `get_fetch_stats()`

**Signature**:

```python
def get_fetch_stats(self) -> dict[str, SourceStats]:
    """
    Get statistics for all auto-fetch sources.
    
    Returns:
        Dictionary mapping source URLs to SourceStats objects with:
        - total_fetched: Total proxies fetched
        - valid_count: Valid proxies
        - invalid_count: Invalid proxies
        - last_fetch_at: Timestamp of last fetch
        - fetch_failure_count: Number of failed fetches
    """
```

**Example**:

```python
stats = rotator.get_fetch_stats()
for source_url, stat in stats.items():
    print(f"{source_url}:")
    print(f"  Valid: {stat.valid_count}/{stat.total_fetched}")
    print(f"  Last fetch: {stat.last_fetch_at}")
    if stat.fetch_failure_count > 0:
        print(f"  Failures: {stat.fetch_failure_count}")
```

---

### `filter_proxies_by_source()`

**Signature**:

```python
def filter_proxies_by_source(
    self,
    source: ProxySource | str,
) -> list[Proxy]:
    """
    Get proxies filtered by source type or URL.
    
    Args:
        source: ProxySource enum value or source URL string
        
    Returns:
        List of proxies matching the source filter
    """
```

**Example**:

```python
from proxywhirl.models import ProxySource

# Get only user-provided proxies
user_proxies = rotator.filter_proxies_by_source(ProxySource.USER)

# Get only fetched proxies
fetched_proxies = rotator.filter_proxies_by_source(ProxySource.FETCHED)

# Get proxies from specific source URL
source_proxies = rotator.filter_proxies_by_source("https://api.proxyscrape.com/...")
```

---

## Context Manager Support

### `__enter__()` / `__exit__()`

**Signature**:

```python
def __enter__(self) -> "ProxyRotator":
    """Enter context manager."""
    return self

def __exit__(
    self,
    exc_type: type[BaseException] | None,
    exc_val: BaseException | None,
    exc_tb: TracebackType | None,
) -> None:
    """Exit context manager and cleanup resources."""
    self.close()
```

**Example**:

```python
with ProxyRotator(proxies=[...]) as rotator:
    response = rotator.get("https://example.com")
# Cleanup happens automatically
```

---

### `close()`

**Signature**:

```python
def close(self) -> None:
    """
    Close all connections and cleanup resources.
    
    Should be called when done using the rotator, especially if not using
    context manager.
    """
```

**Example**:

```python
rotator = ProxyRotator(proxies=[...])
try:
    response = rotator.get("https://example.com")
finally:
    rotator.close()
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
for proxy in rotator.pool.proxies:
    print(f"Proxy: {proxy.url}, Success rate: {proxy.success_rate:.2%}")
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
print(f"Max retries: {rotator.config.max_retries}")
```

---

## Error Handling

All methods may raise:

- `ProxyPoolEmptyError`: When pool has no available proxies
- `ProxyConnectionError`: When all retry attempts fail
- `ProxyAuthenticationError`: When proxy authentication fails
- `ProxyValidationError`: When proxy URL or configuration is invalid
- `httpx.HTTPError`: For HTTP-level errors (timeouts, connection errors, etc.)

**Example**:

```python
from proxywhirl.exceptions import ProxyPoolEmptyError, ProxyConnectionError

try:
    response = rotator.get("https://example.com")
except ProxyPoolEmptyError:
    print("No proxies available")
except ProxyConnectionError as e:
    print(f"All proxies failed: {e}")
except httpx.HTTPError as e:
    print(f"HTTP error: {e}")
```

---

## Thread Safety

⚠️ **Not thread-safe** - Use separate `ProxyRotator` instances per thread, or wrap calls in `threading.Lock`.

**Example**:

```python
import threading

lock = threading.Lock()

def make_request():
    with lock:
        response = rotator.get("https://example.com")
    return response
```

---

## Performance Characteristics

- **Proxy Selection**: O(1) for round-robin/random, O(n) for weighted/least-used
- **Request Overhead**: <50ms for proxy selection and setup
- **Connection Pooling**: Reuses connections per proxy (up to `pool_connections` limit)
- **Memory**: ~1KB per proxy in pool

---

## Complete Usage Example

```python
from proxywhirl import ProxyRotator, ProxyConfiguration

# Configure
config = ProxyConfiguration(
    timeout=30,
    max_retries=3,
    verify_ssl=True,
    health_check_enabled=True
)

# Create rotator
proxies = [
    "http://user1:pass1@proxy1.com:8080",
    "http://user2:pass2@proxy2.com:8080",
    "http://user3:pass3@proxy3.com:8080",
]

with ProxyRotator(proxies=proxies, strategy="weighted", config=config) as rotator:
    # Make requests
    for i in range(10):
        try:
            response = rotator.get(f"https://api.example.com/data/{i}")
            print(f"Request {i}: Status {response.status_code}")
        except Exception as e:
            print(f"Request {i} failed: {e}")
    
    # Check stats
    stats = rotator.get_pool_stats()
    print(f"Success rate: {stats['overall_success_rate']:.2%}")
    
    # Cleanup dead proxies
    removed = rotator.clear_unhealthy_proxies()
    print(f"Removed {removed} unhealthy proxies")
```
