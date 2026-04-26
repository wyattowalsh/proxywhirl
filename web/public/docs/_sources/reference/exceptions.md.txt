---
title: Exceptions Reference
---

# Exceptions Reference

Complete guide to ProxyWhirl's exception hierarchy, error codes, and error handling best practices.

:::{tip}
All ProxyWhirl exceptions support structured error data via `to_dict()` and include a `retry_recommended` flag to help determine whether an operation should be retried. Use `ProxyErrorCode` enum values for reliable programmatic error handling.
:::

## Table of Contents

- [Exception Hierarchy](#exception-hierarchy)
- [ProxyErrorCode Enum](#proxyerrorcode-enum)
- [Utility Functions](#utility-functions)
  - [redact_url()](#redact_url)
- [Error Codes](#error-codes)
- [Exception Reference](#exception-reference)
  - [ProxyWhirlError](#proxywhirlerror)
  - [ProxyValidationError](#proxyvalidationerror)
  - [ProxyPoolEmptyError](#proxypoolemptyerror)
  - [ProxyConnectionError](#proxyconnectionerror)
  - [ProxyAuthenticationError](#proxyauthenticationerror)
  - [ProxyFetchError](#proxyfetcherror)
  - [ProxyStorageError](#proxystorageerror)
  - [CacheCorruptionError](#cachecorruptionerror)
  - [CacheStorageError](#cachestorageerror)
  - [CacheValidationError](#cachevalidationerror)
  - [RequestQueueFullError](#requestqueuefullerror)
- [RetryableError](#retryableerror)
- [NonRetryableError](#nonretryableerror)
- [RegexTimeoutError](#regextimeouterror)
- [RegexComplexityError](#regexcomplexityerror)
- [Error Handling Patterns](#error-handling-patterns)
- [Best Practices](#best-practices)

## Exception Hierarchy

ProxyWhirl uses a hierarchical exception system with a common base class for all library-specific errors:

```
Exception
├── ProxyWhirlError (base)
│   ├── ProxyValidationError
│   ├── ProxyPoolEmptyError
│   ├── ProxyConnectionError
│   ├── ProxyAuthenticationError
│   ├── ProxyFetchError
│   ├── ProxyStorageError
│   ├── CacheCorruptionError
│   ├── CacheStorageError
│   ├── CacheValidationError (also inherits from ValueError)
│   └── RequestQueueFullError
├── RetryableError          (retry module - triggers retry)
├── NonRetryableError       (retry module - skips retry)
├── RegexTimeoutError       (safe_regex module - ReDoS protection)
└── RegexComplexityError    (safe_regex module - ReDoS protection)
```

:::{note}
`ProxyAuthenticationError` inherits directly from `ProxyWhirlError`, not from `ProxyConnectionError`. Catch it separately from connection errors for proper credential handling.
:::

All ProxyWhirl exceptions inherit from `ProxyWhirlError`, making it easy to catch all library-specific errors:

```python
from proxywhirl import ProxyWhirl
from proxywhirl.exceptions import ProxyWhirlError

rotator = ProxyWhirl()

try:
    response = rotator.request("GET", "https://httpbin.org/ip")
except ProxyWhirlError as e:
    # Catches ALL ProxyWhirl-specific errors
    print(f"ProxyWhirl error: {e}")
    print(f"Error code: {e.error_code}")
    print(f"Retry recommended: {e.retry_recommended}")
```

## ProxyErrorCode Enum

The `ProxyErrorCode` enum provides standardized error codes for programmatic error handling. All ProxyWhirl exceptions include an `error_code` attribute that maps to one of these codes.

```python
from proxywhirl.exceptions import ProxyErrorCode

class ProxyErrorCode(str, Enum):
    """Error codes for programmatic error handling."""

    PROXY_POOL_EMPTY = "PROXY_POOL_EMPTY"
    PROXY_VALIDATION_FAILED = "PROXY_VALIDATION_FAILED"
    PROXY_CONNECTION_FAILED = "PROXY_CONNECTION_FAILED"
    PROXY_AUTH_FAILED = "PROXY_AUTH_FAILED"
    PROXY_FETCH_FAILED = "PROXY_FETCH_FAILED"
    PROXY_STORAGE_FAILED = "PROXY_STORAGE_FAILED"
    CACHE_CORRUPTED = "CACHE_CORRUPTED"
    CACHE_STORAGE_FAILED = "CACHE_STORAGE_FAILED"
    CACHE_VALIDATION_FAILED = "CACHE_VALIDATION_FAILED"
    TIMEOUT = "TIMEOUT"
    NETWORK_ERROR = "NETWORK_ERROR"
    INVALID_CONFIGURATION = "INVALID_CONFIGURATION"
    QUEUE_FULL = "QUEUE_FULL"
```

### Usage

Error codes enable reliable programmatic error handling without relying on string matching:

```python
from proxywhirl.exceptions import ProxyWhirlError, ProxyErrorCode

try:
    response = rotator.request("GET", "https://example.com")
except ProxyWhirlError as e:
    # Match by error code (recommended)
    if e.error_code == ProxyErrorCode.PROXY_POOL_EMPTY:
        rotator.auto_fetch()
    elif e.error_code == ProxyErrorCode.TIMEOUT:
        response = rotator.request("GET", url, timeout=60)

    # Also accessible as string value
    print(f"Error code: {e.error_code.value}")  # "PROXY_POOL_EMPTY"
```

## Utility Functions

### redact_url()

:::{important}
ProxyWhirl automatically redacts sensitive information from URLs before including them in error messages. This prevents credentials and API keys from leaking into logs. You only need to call `redact_url()` manually when logging proxy URLs outside of exception handling.
:::

```python
from proxywhirl.exceptions import redact_url

def redact_url(url: str) -> str:
    """
    Redact sensitive information from a URL.

    Removes username and password while preserving scheme, host, port, and path.

    Args:
        url: URL to redact

    Returns:
        Redacted URL string
    """
```

**Examples:**

```python
from proxywhirl.exceptions import redact_url

# Credentials are removed
original = "http://user:password@proxy.example.com:8080"
redacted = redact_url(original)
print(redacted)  # "http://proxy.example.com:8080"

# Sensitive query parameters are masked
original = "https://api.example.com/data?token=secret123&key=abc"
redacted = redact_url(original)
print(redacted)  # "https://api.example.com/data?token=***&key=***"

# Path and port are preserved
original = "socks5://admin:pass@proxy.example.com:1080/path"
redacted = redact_url(original)
print(redacted)  # "socks5://proxy.example.com:1080/path"
```

**Redacted Parameters:**
- Username and password (always removed)
- Query parameters: `password`, `token`, `key`, `secret`, `auth` (case-insensitive)

**Security Note:** All ProxyWhirl exceptions automatically redact URLs in the `proxy_url` attribute and error messages. You only need to call `redact_url()` manually when logging URLs outside of exception handling.

## Error Codes

All exceptions include a programmatic error code for structured error handling:

| Error Code | Exception | Description |
|------------|-----------|-------------|
| `PROXY_POOL_EMPTY` | `ProxyPoolEmptyError` | No proxies available in pool |
| `PROXY_VALIDATION_FAILED` | `ProxyValidationError` | Invalid proxy URL or configuration |
| `PROXY_CONNECTION_FAILED` | `ProxyConnectionError` | Unable to connect through proxy |
| `PROXY_AUTH_FAILED` | `ProxyAuthenticationError` | Proxy authentication failed |
| `PROXY_FETCH_FAILED` | `ProxyFetchError` | Failed to fetch proxies from source |
| `PROXY_STORAGE_FAILED` | `ProxyStorageError` | Storage operation failed |
| `CACHE_CORRUPTED` | `CacheCorruptionError` | Cache data is corrupted |
| `CACHE_STORAGE_FAILED` | `CacheStorageError` | Cache backend unavailable |
| `CACHE_VALIDATION_FAILED` | `CacheValidationError` | Cache entry validation failed |
| `QUEUE_FULL` | `RequestQueueFullError` | Request queue is full |
| `TIMEOUT` | `ProxyConnectionError` | Request timeout (special case) |
| `NETWORK_ERROR` | `ProxyWhirlError` | Generic network error |
| `INVALID_CONFIGURATION` | `ProxyWhirlError` | Invalid configuration |

Use error codes for programmatic error handling:

```python
from proxywhirl.exceptions import ProxyWhirlError, ProxyErrorCode

try:
    response = rotator.request("GET", "https://example.com")
except ProxyWhirlError as e:
    if e.error_code == ProxyErrorCode.PROXY_POOL_EMPTY:
        # Add more proxies
        rotator.add_proxy("http://proxy.example.com:8080")
    elif e.error_code == ProxyErrorCode.TIMEOUT:
        # Increase timeout
        rotator.request("GET", url, timeout=60)
    elif e.error_code == ProxyErrorCode.PROXY_AUTH_FAILED:
        # Update credentials
        logger.error("Invalid proxy credentials")
```

## Exception Reference

### ProxyWhirlError

**Base exception for all ProxyWhirl errors.**

All ProxyWhirl exceptions inherit from this class and support rich metadata for debugging and retry logic.

#### Attributes

- `message` (str): Human-readable error message
- `proxy_url` (str | None): Redacted URL of the proxy that caused the error
- `error_type` (str | None): Type of error (e.g., "timeout", "invalid_credentials")
- `error_code` (ProxyErrorCode): Programmatic error code for handling
- `retry_recommended` (bool): Whether retrying the operation is recommended
- `attempt_count` (int | None): Number of attempts made before this error
- `metadata` (dict): Additional error-specific metadata

#### Methods

```python
def to_dict(self) -> dict[str, Any]:
    """Convert exception to dictionary for logging/serialization."""
```

#### Example

```python
from proxywhirl.exceptions import ProxyWhirlError

try:
    response = rotator.request("GET", "https://example.com")
except ProxyWhirlError as e:
    # Access structured error data
    error_dict = e.to_dict()
    print(f"Error code: {error_dict['error_code']}")
    print(f"Proxy URL: {error_dict['proxy_url']}")  # Redacted for security
    print(f"Retry: {error_dict['retry_recommended']}")
    print(f"Attempt: {error_dict['attempt_count']}")
```

#### Security: URL Redaction

ProxyWhirl automatically redacts sensitive information from proxy URLs in error messages:

```python
# Original URL: http://user:password@proxy.example.com:8080/path?token=secret
# Redacted URL: http://proxy.example.com:8080/path?token=***

# Credentials are always removed for security
```

---

### ProxyValidationError

**Raised when proxy URL or configuration is invalid.**

- **Error Code:** `PROXY_VALIDATION_FAILED`
- **Retry Recommended:** No (invalid input requires correction)

#### When Raised

- Invalid proxy URL format
- Unsupported protocol (not http, https, or socks5)
- Malformed credentials
- Invalid configuration parameters

#### Attributes

Same as `ProxyWhirlError`, plus automatic suggestion appended to message.

#### Example

```python
from proxywhirl import ProxyWhirl
from proxywhirl.exceptions import ProxyValidationError

rotator = ProxyWhirl()

try:
    # Invalid URL format (missing scheme)
    rotator.add_proxy("proxy.example.com:8080")
except ProxyValidationError as e:
    print(e)  # "Invalid proxy URL. Check proxy URL format and protocol."
    # Fix: Add proper scheme
    rotator.add_proxy("http://proxy.example.com:8080")
```

#### Resolution Steps

1. Verify proxy URL format: `protocol://host:port`
2. Ensure protocol is supported (http, https, socks5)
3. Check that credentials are properly URL-encoded
4. Validate port number is within valid range (1-65535)

---

### ProxyPoolEmptyError

**Raised when attempting to select from an empty proxy pool.**

- **Error Code:** `PROXY_POOL_EMPTY`
- **Retry Recommended:** No (pool must be populated first)

#### When Raised

- No proxies configured in the pool
- All proxies filtered out by health checks
- All circuit breakers are open (all proxies failing)
- Geographic filtering excluded all proxies

#### Example

```python
from proxywhirl import ProxyWhirl
from proxywhirl.exceptions import ProxyPoolEmptyError

rotator = ProxyWhirl()

try:
    # No proxies added yet
    response = rotator.request("GET", "https://example.com")
except ProxyPoolEmptyError as e:
    print(e)  # "No proxies available in the pool. Add proxies using add_proxy()..."

    # Solution 1: Add proxies manually
    rotator.add_proxy("http://proxy1.example.com:8080")
    rotator.add_proxy("http://proxy2.example.com:8080")

    # Solution 2: Auto-fetch from sources
    rotator.auto_fetch()

    # Retry request
    response = rotator.request("GET", "https://example.com")
```

#### Resolution Steps

1. Add proxies using `add_proxy()` or `auto_fetch()`
2. Check if proxies were filtered by health checks
3. Verify circuit breakers aren't all open
4. Review geographic targeting settings if applicable
5. Check storage connection if using persistent storage

---

### ProxyConnectionError

**Raised when unable to connect through a proxy.**

- **Error Code:** `PROXY_CONNECTION_FAILED` (or `TIMEOUT` for timeout-specific errors)
- **Retry Recommended:** Yes (transient network issues may resolve)

:::{tip}
When the error message contains "timeout", the `error_code` is automatically set to `ProxyErrorCode.TIMEOUT` instead of `PROXY_CONNECTION_FAILED`. Check `e.error_code` to distinguish between timeout and other connection failures.
:::

#### When Raised

- Proxy is unreachable or offline
- Network connectivity issues
- Proxy doesn't support target protocol
- Request timeout exceeded
- Circuit breaker is open for the proxy

#### Example

```python
from proxywhirl import ProxyWhirl
from proxywhirl.exceptions import ProxyConnectionError, ProxyErrorCode

rotator = ProxyWhirl()
rotator.add_proxy("http://unreachable.proxy.com:8080")

try:
    response = rotator.request("GET", "https://example.com", timeout=5)
except ProxyConnectionError as e:
    if e.error_code == ProxyErrorCode.TIMEOUT:
        print("Request timed out - trying with longer timeout")
        response = rotator.request("GET", "https://example.com", timeout=30)
    else:
        print(f"Connection failed: {e}")
        # Proxy may be offline - try another one
        rotator.remove_proxy("http://unreachable.proxy.com:8080")
```

#### Resolution Steps

1. Verify proxy is reachable (ping, telnet)
2. Check network connectivity and firewall rules
3. Ensure proxy supports the target protocol
4. Increase timeout value for slow proxies
5. Check circuit breaker status
6. Verify proxy provider isn't blocking your IP

---

### ProxyAuthenticationError

**Raised when proxy authentication fails.**

- **Error Code:** `PROXY_AUTH_FAILED`
- **Retry Recommended:** No (credentials must be corrected)

#### When Raised

- Invalid username or password (HTTP 401/407 response)
- Credentials expired or revoked
- Proxy requires different authentication method
- IP whitelist restriction

#### Example

```python
from proxywhirl import ProxyWhirl
from proxywhirl.exceptions import ProxyAuthenticationError

rotator = ProxyWhirl()

try:
    # Wrong credentials
    rotator.add_proxy(
        "http://proxy.example.com:8080",
        username="user",
        password="wrong_password"
    )
    response = rotator.request("GET", "https://example.com")
except ProxyAuthenticationError as e:
    print(e)  # "Proxy authentication failed (407)... Verify username and password..."

    # Fix credentials
    rotator.remove_proxy("http://proxy.example.com:8080")
    rotator.add_proxy(
        "http://proxy.example.com:8080",
        username="user",
        password="correct_password"
    )
    response = rotator.request("GET", "https://example.com")
```

#### Resolution Steps

1. Verify username and password are correct
2. Check if credentials have expired
3. Ensure IP address is whitelisted (if required)
4. Contact proxy provider for credential verification
5. Check if proxy requires specific auth method (Basic, Digest, NTLM)

---

### ProxyFetchError

**Raised when fetching proxies from external sources fails.**

- **Error Code:** `PROXY_FETCH_FAILED`
- **Retry Recommended:** Yes (source may be temporarily unavailable)

#### When Raised

- Source URL is unreachable
- API credentials are invalid
- Response format doesn't match expectations
- Rate limit exceeded
- Malformed JSON/text response

#### Example

```python
from proxywhirl import ProxyWhirl
from proxywhirl.exceptions import ProxyFetchError
import time

rotator = ProxyWhirl()

try:
    # Fetch from external source
    rotator.auto_fetch()
except ProxyFetchError as e:
    print(f"Failed to fetch proxies: {e}")

    # Solution 1: Retry after delay (may be rate limited)
    time.sleep(60)
    rotator.auto_fetch()

    # Solution 2: Add proxies manually as fallback
    rotator.add_proxy("http://fallback-proxy.example.com:8080")
```

#### Resolution Steps

1. Verify source URL is accessible
2. Check API credentials (if required)
3. Review rate limits with provider
4. Validate response format matches expected schema
5. Check proxy provider status page
6. Use manual proxy addition as fallback

---

### ProxyStorageError

**Raised when proxy storage operations fail.**

- **Error Code:** `PROXY_STORAGE_FAILED`
- **Retry Recommended:** No (storage issue must be resolved)

#### When Raised

- Insufficient file system permissions
- Disk space exhausted
- Storage path is not writable
- Database connection failed
- SQLite database is locked

#### Example

```python
from proxywhirl import ProxyWhirl
from proxywhirl.exceptions import ProxyStorageError
import os

try:
    # Using read-only directory
    rotator = ProxyWhirl(storage_path="/read-only/proxywhirl.db")
except ProxyStorageError as e:
    print(f"Storage error: {e}")

    # Solution: Use writable directory
    storage_path = os.path.expanduser("~/.proxywhirl/proxies.db")
    os.makedirs(os.path.dirname(storage_path), exist_ok=True)
    rotator = ProxyWhirl(storage_path=storage_path)
```

#### Resolution Steps

1. Check file system permissions (`chmod`, `chown`)
2. Verify disk space is available (`df -h`)
3. Ensure storage path is writable
4. Check database connection (if using external storage)
5. Close other processes accessing the database
6. Use in-memory storage as temporary fallback

---

### CacheCorruptionError

**Raised when cache data is corrupted and cannot be recovered.**

- **Error Code:** `CACHE_CORRUPTED`
- **Retry Recommended:** No (cache must be cleared)

#### When Raised

- Cache file is corrupted
- Invalid cache format version
- Disk errors or partial writes
- Encryption key mismatch (if using encrypted cache)

#### Example

```python
from proxywhirl.cache import CacheManager
from proxywhirl.exceptions import CacheCorruptionError

cache = CacheManager()

try:
    data = cache.get("my_key")
except CacheCorruptionError as e:
    print(f"Cache corrupted: {e}")

    # Solution: Clear cache and reinitialize
    cache.clear()
    cache = CacheManager()
    print("Cache cleared and reinitialized")
```

#### Resolution Steps

1. Clear the cache directory
2. Reinitialize cache system
3. Check for disk errors (`fsck` on Linux)
4. Verify cache format version compatibility
5. Ensure encryption key is consistent (if applicable)

---

### CacheStorageError

**Raised when cache storage backend is unavailable.**

- **Error Code:** `CACHE_STORAGE_FAILED`
- **Retry Recommended:** Yes (backend may recover)

#### When Raised

- Redis/Memcached server is down
- Network connectivity to cache server lost
- Invalid cache credentials
- Cache server out of memory
- Connection pool exhausted

#### Example

```python
from proxywhirl.cache import CacheManager
from proxywhirl.exceptions import CacheStorageError
import time

cache = CacheManager(backend="redis", redis_url="redis://localhost:6379")

try:
    cache.set("key", "value")
except CacheStorageError as e:
    print(f"Cache backend unavailable: {e}")

    # Solution 1: Retry with exponential backoff
    for i in range(3):
        time.sleep(2 ** i)
        try:
            cache.set("key", "value")
            break
        except CacheStorageError:
            continue

    # Solution 2: Fallback to in-memory cache
    cache = CacheManager(backend="memory")
```

#### Resolution Steps

1. Verify cache backend (Redis, Memcached) is running
2. Check network connectivity to cache server
3. Validate cache credentials
4. Review cache server logs for errors
5. Check server memory and resource limits
6. Use fallback cache (in-memory) temporarily

---

### CacheValidationError

**Raised when cache entry fails validation.**

- **Error Code:** `CACHE_VALIDATION_FAILED`
- **Retry Recommended:** No (data must be corrected)
- **Note:** Also inherits from `ValueError` for compatibility

#### When Raised

- Cache entry format is invalid
- Data types don't match schema
- Required fields are missing
- Validation constraints violated

#### Example

```python
from proxywhirl.cache import CacheManager
from proxywhirl.exceptions import CacheValidationError

cache = CacheManager()

try:
    # Invalid data structure
    cache.set("proxy_stats", {"invalid": "format"})
    stats = cache.get("proxy_stats")
except CacheValidationError as e:
    print(f"Validation failed: {e}")

    # Solution: Use correct data structure
    cache.set("proxy_stats", {
        "total_requests": 100,
        "success_rate": 0.95,
        "avg_latency_ms": 250.0
    })
```

#### Resolution Steps

1. Verify cache entry format matches schema
2. Check data types are correct
3. Ensure required fields are present
4. Validate constraints (ranges, formats)
5. Clear invalid cache entries

---

### RequestQueueFullError

**Raised when the request queue is full and cannot accept more requests.**

- **Error Code:** `QUEUE_FULL`
- **Retry Recommended:** Yes (wait for queue to drain)

#### When Raised

- Request queue has reached maximum capacity
- Too many concurrent requests being processed
- Request rate exceeds processing capacity
- Queue size configuration is too small for workload

#### Attributes

Same as `ProxyWhirlError`, plus:
- `queue_size` (int | None): Maximum queue size (included in metadata)

#### Example

```python
from proxywhirl import ProxyWhirl
from proxywhirl.exceptions import RequestQueueFullError
import time

# Configure with small queue for testing
rotator = ProxyWhirl(queue_size=10)

try:
    # Flood the queue with requests
    for i in range(100):
        rotator.request("GET", f"https://httpbin.org/delay/{i}")
except RequestQueueFullError as e:
    print(f"Queue full: {e}")  # "Request queue is full (max size: 10)..."

    # Solution 1: Wait for queue to drain
    time.sleep(5)
    rotator.request("GET", "https://httpbin.org/ip")

    # Solution 2: Increase queue size
    rotator = ProxyWhirl(queue_size=100)

    # Solution 3: Implement request throttling
    import asyncio
    async def throttled_requests(urls, max_concurrent=10):
        semaphore = asyncio.Semaphore(max_concurrent)
        async def fetch(url):
            async with semaphore:
                return await rotator.request("GET", url)
        tasks = [fetch(url) for url in urls]
        return await asyncio.gather(*tasks)
```

#### Resolution Steps

1. Wait for pending requests to complete
2. Increase `queue_size` in configuration
3. Reduce request rate to match processing capacity
4. Implement request throttling or batching
5. Add more proxy workers to increase throughput
6. Monitor queue metrics to optimize size

---

### RetryableError

**Raised to signal that an operation should be retried by the retry executor.**

- **Module:** `proxywhirl.retry`
- **Inherits:** `Exception` (not `ProxyWhirlError`)

#### When Raised

- Transient network failures during proxied requests
- Temporary proxy unavailability
- Retryable HTTP status codes (502, 503, 504)

#### Example

```python
from proxywhirl import RetryableError

try:
    response = make_request_through_proxy()
except RetryableError:
    # RetryExecutor catches this and retries automatically
    pass
```

---

### NonRetryableError

**Raised to signal that an operation should NOT be retried.**

- **Module:** `proxywhirl.retry`
- **Inherits:** `Exception` (not `ProxyWhirlError`)

#### When Raised

- Authentication failures (401/407)
- Invalid request format
- Permanent proxy configuration errors

#### Example

```python
from proxywhirl import NonRetryableError

try:
    response = make_request_through_proxy()
except NonRetryableError:
    # Do not retry - fix the underlying issue
    logger.error("Non-retryable error, check proxy credentials")
```

---

### RegexTimeoutError

**Raised when regex compilation or matching exceeds the configured timeout.**

- **Module:** `proxywhirl.safe_regex`
- **Inherits:** `Exception` (not `ProxyWhirlError`)
- **Purpose:** ReDoS (Regular Expression Denial of Service) protection

#### When Raised

- Regex pattern takes too long to compile
- Regex matching exceeds timeout threshold
- Catastrophic backtracking detected

#### Example

```python
from proxywhirl import RegexTimeoutError
from proxywhirl.safe_regex import safe_match

try:
    result = safe_match(pattern, text, timeout=1.0)
except RegexTimeoutError:
    logger.warning("Regex timed out - possible ReDoS pattern")
```

---

### RegexComplexityError

**Raised when a regex pattern is too complex or potentially dangerous.**

- **Module:** `proxywhirl.safe_regex`
- **Inherits:** `Exception` (not `ProxyWhirlError`)
- **Purpose:** Prevent ReDoS attacks from user-provided patterns

#### When Raised

- Pattern contains nested quantifiers (e.g., `(a+)+`)
- Pattern exceeds complexity threshold
- Pattern contains known ReDoS-vulnerable constructs

#### Example

```python
from proxywhirl import RegexComplexityError
from proxywhirl.safe_regex import safe_compile

try:
    pattern = safe_compile(user_provided_pattern)
except RegexComplexityError:
    logger.warning("Regex pattern rejected - too complex")
```

---

## Error Handling Patterns

### Basic Error Handling

Catch specific exceptions for targeted error handling:

```python
from proxywhirl import ProxyWhirl
from proxywhirl.exceptions import (
    ProxyPoolEmptyError,
    ProxyConnectionError,
    ProxyAuthenticationError,
)

rotator = ProxyWhirl()

try:
    response = rotator.request("GET", "https://httpbin.org/ip")
    print(f"Success! IP: {response.json()['origin']}")

except ProxyPoolEmptyError:
    print("No proxies available - adding fallback proxy")
    rotator.add_proxy("http://fallback-proxy.example.com:8080")

except ProxyAuthenticationError as e:
    print(f"Authentication failed: {e}")
    # Log error and alert admin
    logger.error("Proxy credentials invalid", extra=e.to_dict())

except ProxyConnectionError as e:
    print(f"Connection failed: {e}")
    if e.retry_recommended:
        # Retry with longer timeout
        response = rotator.request("GET", url, timeout=60)
```

### Catch-All Error Handling

Use `ProxyWhirlError` to catch all library-specific errors:

```python
from proxywhirl import ProxyWhirl
from proxywhirl.exceptions import ProxyWhirlError

rotator = ProxyWhirl()

try:
    response = rotator.request("GET", "https://httpbin.org/ip")
except ProxyWhirlError as e:
    # Structured error logging
    print(f"ProxyWhirl error: {e}")
    logger.error("Request failed", extra={
        "error_code": e.error_code.value,
        "proxy_url": e.proxy_url,
        "retry_recommended": e.retry_recommended,
        "attempt_count": e.attempt_count,
    })
```

### Retry Logic Based on Error Type

Implement smart retry logic based on error metadata:

```python
from proxywhirl import ProxyWhirl
from proxywhirl.exceptions import ProxyWhirlError
import time

def request_with_smart_retry(rotator, url, max_attempts=3):
    """Make request with smart retry logic."""
    for attempt in range(max_attempts):
        try:
            return rotator.request("GET", url)
        except ProxyWhirlError as e:
            if not e.retry_recommended:
                # Don't retry non-retryable errors
                raise

            if attempt < max_attempts - 1:
                # Exponential backoff
                delay = 2 ** attempt
                print(f"Attempt {attempt + 1} failed, retrying in {delay}s...")
                time.sleep(delay)
            else:
                # Final attempt failed
                raise
```

### Async Error Handling

Handle errors in async contexts:

```python
import asyncio
from proxywhirl import AsyncProxyWhirl
from proxywhirl.exceptions import (
    ProxyPoolEmptyError,
    ProxyConnectionError,
)

async def fetch_with_fallback(url):
    """Fetch URL with automatic fallback strategy."""
    rotator = AsyncProxyWhirl()

    try:
        response = await rotator.request("GET", url)
        return response.json()

    except ProxyPoolEmptyError:
        # Fallback: Auto-fetch proxies
        print("No proxies available, fetching from sources...")
        await rotator.auto_fetch()
        response = await rotator.request("GET", url)
        return response.json()

    except ProxyConnectionError as e:
        # Fallback: Try without proxy
        print(f"All proxies failed ({e}), trying direct connection...")
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()

# Usage
result = asyncio.run(fetch_with_fallback("https://httpbin.org/ip"))
```

### REST API Error Handling

:::{seealso}
For the full REST API error code reference, see [REST API](rest-api.md).
:::

Handle exceptions in REST API endpoints:

```python
from fastapi import FastAPI, HTTPException, status
from proxywhirl import ProxyWhirl
from proxywhirl.exceptions import (
    ProxyWhirlError,
    ProxyPoolEmptyError,
    ProxyConnectionError,
)

app = FastAPI()
rotator = ProxyWhirl()

@app.post("/api/v1/request")
async def proxied_request(url: str):
    """Make proxied request with proper error handling."""
    try:
        response = rotator.request("GET", url)
        return {
            "status": "success",
            "data": response.json(),
            "proxy_used": response.headers.get("X-Proxy-ID")
        }

    except ProxyPoolEmptyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error_code": e.error_code.value,
                "message": str(e),
                "suggestion": "Add proxies to the pool"
            }
        )

    except ProxyConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error_code": e.error_code.value,
                "message": str(e),
                "retry_recommended": e.retry_recommended
            }
        )

    except ProxyWhirlError as e:
        # Generic error handler for all other ProxyWhirl errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.to_dict()
        )
```

### Context Manager Pattern

Use context managers for automatic cleanup on errors:

```python
from contextlib import contextmanager
from proxywhirl import ProxyWhirl
from proxywhirl.exceptions import ProxyWhirlError

@contextmanager
def rotator_session(storage_path=None):
    """Context manager for ProxyWhirl with automatic cleanup."""
    rotator = ProxyWhirl(storage_path=storage_path)
    try:
        yield rotator
    except ProxyWhirlError as e:
        # Log error
        print(f"Session error: {e}")
        raise
    finally:
        # Cleanup (close connections, save state, etc.)
        rotator.close()

# Usage
with rotator_session("/tmp/proxies.db") as rotator:
    rotator.add_proxy("http://proxy.example.com:8080")
    response = rotator.request("GET", "https://httpbin.org/ip")
    # Automatic cleanup on exit
```

### Error Aggregation

Aggregate multiple errors for batch operations:

```python
from proxywhirl import ProxyWhirl
from proxywhirl.exceptions import ProxyValidationError
from typing import List, Tuple

def add_proxies_bulk(
    rotator: ProxyWhirl,
    proxy_urls: List[str]
) -> Tuple[int, List[Tuple[str, Exception]]]:
    """Add multiple proxies, collecting errors."""
    success_count = 0
    errors = []

    for url in proxy_urls:
        try:
            rotator.add_proxy(url)
            success_count += 1
        except ProxyValidationError as e:
            errors.append((url, e))

    return success_count, errors

# Usage
urls = [
    "http://proxy1.example.com:8080",
    "invalid-url",  # Will fail
    "http://proxy2.example.com:8080",
]

rotator = ProxyWhirl()
success, errors = add_proxies_bulk(rotator, urls)

print(f"Added {success} proxies")
for url, error in errors:
    print(f"Failed to add {url}: {error}")
```

---

## Best Practices

### 1. Use Specific Exceptions

Catch specific exceptions rather than generic ones:

```python
# Good: Specific exception handling
try:
    response = rotator.request("GET", url)
except ProxyPoolEmptyError:
    rotator.auto_fetch()
except ProxyAuthenticationError:
    update_credentials()

# Bad: Too broad
try:
    response = rotator.request("GET", url)
except Exception:
    # Can't distinguish between different errors
    pass
```

### 2. Check retry_recommended Flag

Respect the `retry_recommended` flag to avoid retrying non-retryable errors:

```python
from proxywhirl.exceptions import ProxyWhirlError

try:
    response = rotator.request("GET", url)
except ProxyWhirlError as e:
    if e.retry_recommended:
        # Retry makes sense
        time.sleep(1)
        response = rotator.request("GET", url)
    else:
        # Don't retry - error requires manual intervention
        logger.error(f"Non-retryable error: {e}")
        raise
```

### 3. Use Error Codes for Programmatic Handling

Use error codes for reliable programmatic error handling:

```python
from proxywhirl.exceptions import ProxyWhirlError, ProxyErrorCode

try:
    response = rotator.request("GET", url)
except ProxyWhirlError as e:
    # More reliable than string matching
    if e.error_code == ProxyErrorCode.PROXY_POOL_EMPTY:
        handle_empty_pool()
    elif e.error_code == ProxyErrorCode.TIMEOUT:
        handle_timeout()
```

### 4. Log Structured Error Data

Use `to_dict()` for structured logging:

```python
from proxywhirl.exceptions import ProxyWhirlError
import json

try:
    response = rotator.request("GET", url)
except ProxyWhirlError as e:
    # Structured logging with all error metadata
    logger.error(
        "Request failed",
        extra=e.to_dict()
    )

    # Or for JSON logging
    print(json.dumps(e.to_dict(), indent=2))
```

### 5. Implement Circuit Breaker Pattern

Use circuit breakers to prevent cascading failures:

```python
from proxywhirl import ProxyWhirl
from proxywhirl.exceptions import ProxyConnectionError

rotator = ProxyWhirl(
    circuit_breaker_enabled=True,
    failure_threshold=5,
    recovery_timeout=60
)

try:
    response = rotator.request("GET", url)
except ProxyConnectionError as e:
    if "circuit breaker is open" in str(e).lower():
        # Circuit breaker is protecting against failing proxy
        # Wait for recovery or remove proxy
        print("Circuit breaker open, waiting for recovery...")
        time.sleep(60)
```

### 6. Provide User-Friendly Error Messages

Catch ProxyWhirl errors and provide context-specific messages:

```python
from proxywhirl.exceptions import (
    ProxyPoolEmptyError,
    ProxyConnectionError,
    ProxyAuthenticationError,
)

def user_friendly_request(url):
    """Make request with user-friendly error messages."""
    try:
        return rotator.request("GET", url)

    except ProxyPoolEmptyError:
        return {
            "success": False,
            "error": "No proxies configured. Please add proxies first.",
            "action": "add_proxies"
        }

    except ProxyAuthenticationError:
        return {
            "success": False,
            "error": "Proxy credentials are invalid. Please check your username and password.",
            "action": "update_credentials"
        }

    except ProxyConnectionError as e:
        return {
            "success": False,
            "error": f"Unable to connect through proxy: {e}",
            "action": "check_proxy_status"
        }
```

### 7. Test Error Handling

Write tests for error scenarios:

```python
import pytest
from proxywhirl import ProxyWhirl
from proxywhirl.exceptions import (
    ProxyPoolEmptyError,
    ProxyValidationError,
)

def test_empty_pool_error():
    """Test that empty pool raises appropriate error."""
    rotator = ProxyWhirl()

    with pytest.raises(ProxyPoolEmptyError) as exc_info:
        rotator.request("GET", "https://httpbin.org/ip")

    assert exc_info.value.error_code.value == "PROXY_POOL_EMPTY"
    assert exc_info.value.retry_recommended is False

def test_invalid_proxy_error():
    """Test that invalid proxy URL raises validation error."""
    rotator = ProxyWhirl()

    with pytest.raises(ProxyValidationError) as exc_info:
        rotator.add_proxy("invalid-url")

    assert exc_info.value.error_code.value == "PROXY_VALIDATION_FAILED"
```

### 8. Monitor Error Rates

Track error rates to identify proxy quality issues:

```python
from collections import defaultdict
from proxywhirl.exceptions import ProxyWhirlError

error_counts = defaultdict(int)

def monitored_request(url):
    """Make request with error monitoring."""
    try:
        return rotator.request("GET", url)
    except ProxyWhirlError as e:
        # Track error types
        error_counts[e.error_code.value] += 1

        # Alert if error rate is high
        total_errors = sum(error_counts.values())
        if total_errors > 100:
            print(f"High error rate detected: {error_counts}")

        raise

# Periodic reporting
def report_error_stats():
    """Report error statistics."""
    print("Error Statistics:")
    for error_code, count in error_counts.items():
        print(f"  {error_code}: {count}")
```

### 9. Handle Async Errors Properly

Use proper async error handling patterns:

```python
import asyncio
from proxywhirl import AsyncProxyWhirl
from proxywhirl.exceptions import ProxyWhirlError

async def async_request_with_timeout(url, timeout=30):
    """Async request with timeout and error handling."""
    rotator = AsyncProxyWhirl()

    try:
        # Add timeout to prevent hanging
        response = await asyncio.wait_for(
            rotator.request("GET", url),
            timeout=timeout
        )
        return response

    except asyncio.TimeoutError:
        print(f"Request timed out after {timeout}s")
        raise

    except ProxyWhirlError as e:
        print(f"ProxyWhirl error: {e}")
        raise

    finally:
        await rotator.close()
```

### 10. Document Error Handling

Document expected errors in docstrings:

```python
def fetch_data(url: str) -> dict:
    """
    Fetch data from URL through proxy.

    Args:
        url: Target URL to fetch

    Returns:
        Parsed JSON response

    Raises:
        ProxyPoolEmptyError: No proxies available in pool
        ProxyConnectionError: Unable to connect through proxy
        ProxyAuthenticationError: Proxy authentication failed

    Example:
        >>> try:
        ...     data = fetch_data("https://api.example.com/data")
        ... except ProxyPoolEmptyError:
        ...     rotator.auto_fetch()
        ...     data = fetch_data("https://api.example.com/data")
    """
    response = rotator.request("GET", url)
    return response.json()
```

---

## Summary

ProxyWhirl's exception system provides:

1. **Hierarchical structure** - All exceptions inherit from `ProxyWhirlError`
2. **Error codes** - Programmatic error handling with `ProxyErrorCode`
3. **Rich metadata** - Proxy URL, attempt count, retry recommendations
4. **Security** - Automatic URL redaction to protect credentials
5. **Actionable guidance** - Each exception includes resolution steps

Use specific exception types for targeted error handling, check the `retry_recommended` flag, and leverage error codes for reliable programmatic handling.

## See Also

- [Python API](python-api.md) -- Main ProxyWhirl API reference
- [REST API](rest-api.md) -- REST API error codes and responses
- [Cache API](cache-api.md) -- Cache-specific error handling
- [Retry & Failover](../guides/retry-failover.md) -- Retry patterns and circuit breaker integration
- [Async Client](../guides/async-client.md) -- Async error handling patterns
- [Deployment Security](../guides/deployment-security.md) -- Production error monitoring

For questions or issues:
- GitHub: https://github.com/wyattowalsh/proxywhirl/issues
