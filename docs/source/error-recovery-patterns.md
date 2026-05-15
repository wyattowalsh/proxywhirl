# Error Handling and Recovery Patterns

## Exception Hierarchy

```text
ProxyWhirlError (base)
├─ ProxyPoolEmptyError
├─ ProxyValidationError
├─ ProxyConnectionError
├─ ProxyAuthenticationError
├─ ProxyFetchError
├─ ProxyStorageError
├─ RetryableError
└─ NonRetryableError
```

## Common Error Scenarios

### 1. No Proxies Available

```python
from proxywhirl import ProxyWhirl, ProxyPoolEmptyError

rotator = ProxyWhirl()

try:
    proxy = rotator.get_proxy()
except ProxyPoolEmptyError:
    # Fallback strategy
    rotator.refresh_sources()
    proxies = rotator.get_proxies(count=10)
    if proxies:
        proxy = proxies[0]
    else:
        raise  # Re-raise if still empty
```

### 2. Validation Failures

```python
from proxywhirl import ProxyValidationError

try:
    proxy = rotator.get_proxy()
    # Try to use proxy
except ProxyValidationError as e:
    print(f"Validation failed: {e}")
    # Mark as unhealthy
    rotator.mark_unhealthy(proxy)
    # Try next proxy
    proxy = rotator.get_proxy()
```

### 3. Connection Failures

```python
from proxywhirl import ProxyConnectionError
import httpx

try:
    proxy = rotator.get_proxy()
    client = httpx.Client(proxies=proxy)
    response = client.get('https://example.com')
except ProxyConnectionError as e:
    # Network error, retry with next proxy
    rotator.mark_unhealthy(proxy)
    proxy = rotator.get_proxy()
    response = client.get('https://example.com')
```

### 4. Authentication Failures

```python
from proxywhirl import ProxyAuthenticationError

try:
    proxy = rotator.get_proxy()
    # Use proxy with auth
    response = client.get(
        'https://example.com',
        auth=(proxy.username, proxy.password)
    )
except ProxyAuthenticationError as e:
    print(f"Auth failed: {e}")
    # Try different proxy
    proxy = rotator.get_proxy()
```

## Retry Patterns

### Automatic Retries with Circuit Breaker

```python
from proxywhirl import CircuitBreaker, CircuitBreakerConfig, RetryPolicy

retry_policy = RetryPolicy(
    max_retries=3,
    backoff_factor=2,
    backoff_type='exponential'
)

breaker = CircuitBreaker(
    config=CircuitBreakerConfig(
        failure_threshold=5,
        recovery_timeout=60
    )
)

def make_request():
    try:
        result = breaker.call(lambda: request_with_proxy())
        return result
    except Exception:
        return retry_executor.execute(
            lambda: request_with_proxy()
        )
```

### Exponential Backoff with Jitter

```python
import time
import random

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            # Exponential backoff with jitter
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait_time)
```

## Graceful Degradation

### Fallback Strategy

```python
def get_proxy_with_fallback():
    strategies = [
        lambda: rotator.select_proxy(
            SelectionContext(validation='strict')
        ),
        lambda: rotator.select_proxy(
            SelectionContext(validation='moderate')
        ),
        lambda: rotator.select_proxy(
            SelectionContext(validation='light')
        ),
        lambda: get_cached_proxy()
    ]
    
    for strategy in strategies:
        try:
            return strategy()
        except Exception:
            continue
    
    raise ProxyPoolEmptyError("All strategies failed")
```

### Timeout Handling

```python
import signal
from contextlib import contextmanager

@contextmanager
def timeout(seconds):
    def signal_handler(signum, frame):
        raise TimeoutError()
    
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

try:
    with timeout(30):
        proxy = rotator.get_proxy()
except TimeoutError:
    # Use pre-fetched backup proxy
    proxy = get_backup_proxy()
```

## Health Monitoring and Recovery

### Proactive Health Checks

```python
import asyncio
from proxywhirl import HealthMonitor

async def monitor_health():
    monitor = HealthMonitor()
    while True:
        unhealthy = rotator.get_unhealthy_proxies()
        if unhealthy:
            print(f"Found {len(unhealthy)} unhealthy proxies")
            rotator.remove_proxies(unhealthy)
            rotator.refresh_sources()
        await asyncio.sleep(300)  # Check every 5 minutes

asyncio.run(monitor_health())
```

### Recovery from Storage Failures

```python
def get_proxy_with_fallback():
    try:
        # Try SQLite storage
        proxy = rotator.get_proxy()
        return proxy
    except ProxyStorageError:
        print("Storage error, using cache")
        # Fall back to in-memory cache
        cached = rotator.cache.get_random()
        if cached:
            return cached
        # Final fallback
        rotator.refresh_sources()
        return rotator.get_proxy()
```

## Logging Best Practices

```python
from loguru import logger

def handle_proxy_error(proxy, error):
    logger.error(
        "Proxy operation failed",
        proxy=proxy.url,
        error_type=type(error).__name__,
        error_msg=str(error),
        timestamp=datetime.now(),
        extra={
            'proxy_country': proxy.country,
            'proxy_type': proxy.protocol,
            'is_residential': proxy.is_residential
        }
    )
```

## Distributed Systems Patterns

### Circuit Breaker with Fallback

```python
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class ResilientProxy:
    def __init__(self, rotator):
        self.rotator = rotator
        self.circuit_state = CircuitState.CLOSED
        self.failure_count = 0
        self.threshold = 5
    
    def get_proxy(self):
        if self.circuit_state == CircuitState.OPEN:
            # Use backup proxy list
            return self.rotator.get_backup_proxy()
        
        try:
            proxy = self.rotator.get_proxy()
            self.failure_count = 0
            self.circuit_state = CircuitState.CLOSED
            return proxy
        except Exception as e:
            self.failure_count += 1
            if self.failure_count >= self.threshold:
                self.circuit_state = CircuitState.OPEN
            raise
```

### Bulkhead Pattern

```python
from concurrent.futures import ThreadPoolExecutor

class BulkheadProxy:
    def __init__(self, max_workers=5):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def get_proxy(self):
        # Limit concurrent operations
        future = self.executor.submit(
            self.rotator.get_proxy
        )
        return future.result(timeout=30)
```
