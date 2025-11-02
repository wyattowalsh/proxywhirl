# Quickstart Guide

**Feature**: Core Python Package

Get started with ProxyWhirl in minutes. This guide covers installation, basic usage, and common patterns.

---

## Installation

### From PyPI (when published)

```bash
pip install proxywhirl
```

### With Optional Dependencies

```bash
# With persistent storage support
pip install proxywhirl[storage]

# With credential encryption
pip install proxywhirl[security]

# With JavaScript rendering (Playwright for JS-heavy proxy sites)
pip install proxywhirl[js]

# With all extras
pip install proxywhirl[all]
```

### From Source (Development)

```bash
git clone https://github.com/yourusername/proxywhirl.git
cd proxywhirl
pip install -e ".[dev]"
```

---

## Basic Usage

### Synchronous API

```python
from proxywhirl import ProxyRotator

# Create rotator with proxy list
proxies = [
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080",
    "http://proxy3.example.com:8080",
]

rotator = ProxyRotator(proxies=proxies)

# Make requests
response = rotator.get("https://httpbin.org/ip")
print(response.json())

# Clean up
rotator.close()
```

### Using Context Manager (Recommended)

```python
from proxywhirl import ProxyRotator

with ProxyRotator(proxies=["http://proxy1.com:8080"]) as rotator:
    response = rotator.get("https://api.example.com/data")
    print(response.status_code)
    print(response.json())
# Automatic cleanup
```

---

## Auto-Fetching Proxies

### Fetch from Free Proxy Sources

ProxyWhirl can automatically fetch and validate proxies from free public sources:

```python
from proxywhirl import ProxyRotator

# Auto-fetch from free sources
with ProxyRotator(
    auto_fetch_sources=[
        "https://api.proxyscrape.com/v2/?request=get&protocol=http&format=json",
        "https://www.free-proxy-list.net"
    ],
    auto_fetch_interval=3600,  # Refresh every hour
    validate_fetched=True       # Only add working proxies
) as rotator:
    response = rotator.get("https://api.example.com/data")
    print(response.json())
```

### Mix User Proxies with Auto-Fetched

Combine your premium proxies with free proxies for fallback:

```python
from proxywhirl import ProxyRotator

# Your premium proxies (prioritized)
user_proxies = [
    "http://user:pass@premium-proxy1.com:8080",
    "http://user:pass@premium-proxy2.com:8080"
]

# Auto-fetch free proxies as backup
with ProxyRotator(
    proxies=user_proxies,  # Tagged as source:user
    auto_fetch_sources=[
        "https://api.proxyscrape.com/v2/?request=get&protocol=http&format=json"
    ],
    strategy="weighted",  # Prioritize user proxies
    auto_fetch_interval=1800  # Refresh every 30 minutes
) as rotator:
    # Make requests - will prefer user proxies, fall back to free proxies
    for i in range(100):
        response = rotator.get(f"https://api.example.com/data/{i}")
        print(f"Request {i}: {response.status_code}")
```

### Custom Source Configuration

For more control over fetching behavior, including JavaScript-rendered pages:

```python
from proxywhirl import ProxyRotator, ProxySourceConfig, ProxyFormat, RenderMode

sources = [
    # JSON API (static fetch)
    ProxySourceConfig(
        url="https://api.proxyscrape.com/v2/?request=get&protocol=http&format=json",
        format=ProxyFormat.JSON,
        render_mode=RenderMode.STATIC,
        refresh_interval=1800,  # 30 minutes
        priority=5              # Higher priority
    ),
    
    # Static HTML table
    ProxySourceConfig(
        url="https://www.free-proxy-list.net",
        format=ProxyFormat.HTML_TABLE,
        render_mode=RenderMode.STATIC,
        parser="table.table-striped",  # CSS selector
        refresh_interval=3600
    ),
    
    # JavaScript-rendered page (React/Vue/Angular)
    ProxySourceConfig(
        url="https://www.proxy-list.download/HTTP",
        format=ProxyFormat.HTML_TABLE,
        render_mode=RenderMode.JAVASCRIPT,
        wait_selector="table#proxylisttable",  # Wait for this element
        wait_timeout=10000,  # 10 seconds max
        priority=3
    ),
    
    # Auto-detect (tries static first, falls back to JS)
    ProxySourceConfig(
        url="https://unknown-proxy-site.com",
        format=ProxyFormat.HTML_TABLE,
        render_mode=RenderMode.AUTO,  # Smart detection
        parser="table"
    )
]

with ProxyRotator(auto_fetch_sources=sources) as rotator:
    # Check what was fetched
    stats = rotator.get_fetch_stats()
    for source_url, stat in stats.items():
        print(f"{source_url}: {stat.valid_count} valid proxies")
        if stat.render_mode_used:
            print(f"  Rendered with: {stat.render_mode_used}")
    
    # Make requests
    response = rotator.get("https://api.example.com")
```

**Note**: JavaScript rendering requires the optional `playwright` dependency:

```bash
pip install proxywhirl[js]
# Or install all extras
pip install proxywhirl[all]
```

On first use, Playwright will auto-install Chromium browser (~100MB).

### Manual Refresh

Trigger proxy refresh on-demand:

```python
from proxywhirl import ProxyRotator

with ProxyRotator(
    auto_fetch_sources=["https://api.proxyscrape.com/..."],
    auto_fetch_interval=0  # Disable auto-refresh
) as rotator:
    # Initial fetch happens automatically
    
    # Later, manually refresh when needed
    refresh_stats = rotator.refresh_proxies()
    print(f"Fetched {refresh_stats['valid_count']} new proxies")
    print(f"Skipped {refresh_stats['duplicate_count']} duplicates")
```

### Filter by Source

View and filter proxies by their source:

```python
from proxywhirl import ProxyRotator
from proxywhirl.models import ProxySource

with ProxyRotator(
    proxies=["http://my-proxy.com:8080"],
    auto_fetch_sources=["https://api.proxyscrape.com/..."]
) as rotator:
    # Get only user-provided proxies
    user_proxies = rotator.filter_proxies_by_source(ProxySource.USER)
    print(f"User proxies: {len(user_proxies)}")
    
    # Get only fetched proxies
    fetched_proxies = rotator.filter_proxies_by_source(ProxySource.FETCHED)
    print(f"Fetched proxies: {len(fetched_proxies)}")
    
    # Get proxies from specific source URL
    specific_source = rotator.filter_proxies_by_source(
        "https://api.proxyscrape.com/..."
    )
    print(f"From ProxyScrape: {len(specific_source)}")
```

---

## Asynchronous API

### Basic Async Usage

```python
import asyncio
from proxywhirl import AsyncProxyRotator

async def main():
    proxies = [
        "http://proxy1.example.com:8080",
        "http://proxy2.example.com:8080",
    ]
    
    async with AsyncProxyRotator(proxies=proxies) as rotator:
        response = await rotator.get("https://httpbin.org/ip")
        print(response.json())

asyncio.run(main())
```

### Concurrent Requests

```python
import asyncio
from proxywhirl import AsyncProxyRotator

async def main():
    async with AsyncProxyRotator(proxies=[...]) as rotator:
        # Make 10 requests concurrently
        tasks = [
            rotator.get(f"https://api.example.com/data/{i}")
            for i in range(10)
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"Request {i} failed: {response}")
            else:
                print(f"Request {i}: {response.status_code}")

asyncio.run(main())
```

---

## Proxy Authentication

### HTTP Basic Auth

```python
from proxywhirl import ProxyRotator, Proxy

# Option 1: Include credentials in URL
proxies = ["http://username:password@proxy1.com:8080"]

# Option 2: Use Proxy objects
proxy = Proxy(
    url="http://proxy1.com:8080",
    username="myuser",
    password="mypassword"
)

rotator = ProxyRotator(proxies=[proxy])
```

### Multiple Proxies with Different Credentials

```python
from proxywhirl import ProxyRotator, Proxy

proxies = [
    Proxy(url="http://proxy1.com:8080", username="user1", password="pass1"),
    Proxy(url="http://proxy2.com:8080", username="user2", password="pass2"),
    Proxy(url="http://proxy3.com:8080", username="user3", password="pass3"),
]

with ProxyRotator(proxies=proxies) as rotator:
    response = rotator.get("https://api.example.com")
```

---

## Rotation Strategies

### Round-Robin (Default)

Rotates through proxies in order.

```python
from proxywhirl import ProxyRotator

rotator = ProxyRotator(
    proxies=[...],
    strategy="round-robin"  # Default
)
```

### Random Selection

Randomly selects a proxy for each request.

```python
from proxywhirl import ProxyRotator

rotator = ProxyRotator(
    proxies=[...],
    strategy="random"
)
```

### Weighted by Success Rate

Selects proxies based on their success rates (better proxies used more often).

```python
from proxywhirl import ProxyRotator

rotator = ProxyRotator(
    proxies=[...],
    strategy="weighted"
)
```

### Least Used

Always selects the proxy with the fewest total requests.

```python
from proxywhirl import ProxyRotator

rotator = ProxyRotator(
    proxies=[...],
    strategy="least-used"
)
```

### Custom Strategy

```python
from proxywhirl import ProxyRotator
from proxywhirl.strategies import RotationStrategy
from proxywhirl.models import Proxy

class FastestProxyStrategy(RotationStrategy):
    """Select proxy with lowest average response time."""
    
    def select_proxy(self, pool: list[Proxy]) -> Proxy:
        if not pool:
            raise ValueError("Pool is empty")
        
        # Filter to healthy proxies
        healthy = [p for p in pool if p.is_healthy]
        if not healthy:
            healthy = pool  # Fall back to all proxies
        
        # Select fastest
        return min(
            healthy,
            key=lambda p: p.average_response_time_ms or float('inf')
        )
    
    def on_success(self, proxy: Proxy) -> None:
        pass
    
    def on_failure(self, proxy: Proxy, error: Exception) -> None:
        pass
    
    def reset(self) -> None:
        pass

# Use custom strategy
rotator = ProxyRotator(
    proxies=[...],
    strategy=FastestProxyStrategy()
)
```

---

## Configuration

### Basic Configuration

```python
from proxywhirl import ProxyRotator, ProxyConfiguration

config = ProxyConfiguration(
    timeout=60,          # Request timeout in seconds
    max_retries=5,       # Retry attempts per request
    verify_ssl=True,     # Verify SSL certificates
    follow_redirects=True
)

rotator = ProxyRotator(proxies=[...], config=config)
```

### Environment Variables

ProxyWhirl supports configuration via environment variables:

```bash
export PROXYWHIRL_TIMEOUT=60
export PROXYWHIRL_MAX_RETRIES=5
export PROXYWHIRL_VERIFY_SSL=true
export PROXYWHIRL_LOG_LEVEL=DEBUG
```

```python
from proxywhirl import ProxyRotator, ProxyConfiguration

# Automatically loads from environment variables
config = ProxyConfiguration()
rotator = ProxyRotator(proxies=[...], config=config)
```

### Configuration File

Create a `.env` file:

```env
PROXYWHIRL_TIMEOUT=60
PROXYWHIRL_MAX_RETRIES=5
PROXYWHIRL_POOL_CONNECTIONS=50
PROXYWHIRL_LOG_LEVEL=INFO
```

```python
from proxywhirl import ProxyConfiguration

config = ProxyConfiguration()  # Loads from .env
```

---

## File Persistence

### Save & Load Proxy Pool

```python
from proxywhirl import ProxyRotator
from pathlib import Path

# Create and configure rotator
with ProxyRotator(
    auto_fetch_sources=["https://api.proxyscrape.com/..."],
    validate_fetched=True
) as rotator:
    # Use rotator...
    rotator.get("https://example.com")
    
    # Save pool to file
    rotator.save_to_file("./data/proxies.json")

# Later, load from file
rotator = ProxyRotator.load_from_file("./data/proxies.json")
response = rotator.get("https://example.com")
rotator.close()
```

### Auto-Save to File

```python
from proxywhirl import ProxyRotator

with ProxyRotator(
    auto_fetch_sources=["https://api.proxyscrape.com/..."],
    validate_fetched=True
) as rotator:
    # Start auto-save (every 5 minutes)
    rotator.auto_save_start("./data/proxies.json", interval=300)
    
    # Use rotator...
    for i in range(1000):
        rotator.get(f"https://api.example.com/data/{i}")
    
    # Stop auto-save (final save happens automatically)
    rotator.auto_save_stop()
```

### Compressed Storage

```python
from proxywhirl import ProxyRotator

with ProxyRotator(proxies=[...]) as rotator:
    # Save with gzip compression (50-70% smaller)
    rotator.save_to_file("./data/proxies.json.gz", compression=True)

# Load compressed file
rotator = ProxyRotator.load_from_file("./data/proxies.json.gz", compression=True)
```

### Lazy Loading for Large Pools

```python
from proxywhirl import ProxyRotator, FileStorage
from pathlib import Path

# For very large pools (1000+ proxies)
storage = FileStorage(
    storage_path=Path("./data/large_pool.json"),
    lazy_load=True  # Only load metadata, proxies loaded on-demand
)

rotator = ProxyRotator.load_from_file(
    "./data/large_pool.json"
)
# Proxies loaded as needed during rotation
```

---

## Pool Management

### Adding Proxies Dynamically

```python
from proxywhirl import ProxyRotator

with ProxyRotator(proxies=[]) as rotator:
    # Add proxies on the fly
    rotator.add_proxy("http://proxy1.com:8080")
    rotator.add_proxy("http://proxy2.com:8080")
    
    response = rotator.get("https://example.com")
```

### Removing Proxies

```python
from proxywhirl import ProxyRotator

with ProxyRotator(proxies=[...]) as rotator:
    # Remove by URL
    rotator.remove_proxy("http://proxy1.com:8080")
    
    # Remove by proxy ID
    proxy = rotator.pool.proxies[0]
    rotator.remove_proxy(proxy.id)
```

### Monitoring Pool Health

```python
from proxywhirl import ProxyRotator

with ProxyRotator(proxies=[...]) as rotator:
    # Make some requests
    for i in range(100):
        try:
            rotator.get(f"https://api.example.com/data/{i}")
        except Exception:
            pass
    
    # Check pool statistics
    stats = rotator.get_pool_stats()
    print(f"Total proxies: {stats['total_proxies']}")
    print(f"Healthy proxies: {stats['healthy_proxies']}")
    print(f"Total requests: {stats['total_requests']}")
    print(f"Success rate: {stats['overall_success_rate']:.2%}")
    
    # Remove unhealthy proxies
    removed = rotator.clear_unhealthy_proxies()
    print(f"Removed {removed} unhealthy proxies")
```

### Accessing Individual Proxy Stats

```python
from proxywhirl import ProxyRotator

with ProxyRotator(proxies=[...]) as rotator:
    # Make requests...
    
    # Inspect each proxy
    for proxy in rotator.pool.proxies:
        print(f"Proxy: {proxy.url}")
        print(f"  Success rate: {proxy.success_rate:.2%}")
        print(f"  Total requests: {proxy.total_requests}")
        print(f"  Avg response time: {proxy.average_response_time_ms}ms")
        print(f"  Health: {proxy.health_status.name}")
        print()
```

---

## Error Handling

### Handling Common Errors

```python
from proxywhirl import ProxyRotator
from proxywhirl.exceptions import (
    ProxyPoolEmptyError,
    ProxyConnectionError,
    ProxyAuthenticationError,
)
import httpx

with ProxyRotator(proxies=[...]) as rotator:
    try:
        response = rotator.get("https://api.example.com")
        print(response.json())
    except ProxyPoolEmptyError:
        print("No proxies available in pool")
    except ProxyConnectionError as e:
        print(f"All proxies failed: {e}")
    except ProxyAuthenticationError as e:
        print(f"Proxy authentication failed: {e}")
    except httpx.TimeoutException:
        print("Request timed out")
    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e.response.status_code}")
```

### Retry with Fallback

```python
from proxywhirl import ProxyRotator
from proxywhirl.exceptions import ProxyConnectionError

primary_proxies = ["http://proxy1.com:8080", "http://proxy2.com:8080"]
fallback_proxies = ["http://backup1.com:8080", "http://backup2.com:8080"]

try:
    with ProxyRotator(proxies=primary_proxies) as rotator:
        response = rotator.get("https://api.example.com")
except ProxyConnectionError:
    print("Primary proxies failed, trying fallback...")
    with ProxyRotator(proxies=fallback_proxies) as rotator:
        response = rotator.get("https://api.example.com")

print(response.json())
```

---

## HTTP Methods

### GET Request

```python
response = rotator.get(
    "https://api.example.com/users",
    params={"page": 1, "limit": 10},
    headers={"Authorization": "Bearer token123"}
)
```

### POST Request

```python
# JSON body
response = rotator.post(
    "https://api.example.com/users",
    json={"name": "John", "email": "john@example.com"}
)

# Form data
response = rotator.post(
    "https://api.example.com/submit",
    data={"field1": "value1", "field2": "value2"}
)
```

### Other HTTP Methods

```python
# PUT
response = rotator.request(
    "PUT",
    "https://api.example.com/users/123",
    json={"name": "Jane"}
)

# DELETE
response = rotator.request("DELETE", "https://api.example.com/users/123")

# PATCH
response = rotator.request(
    "PATCH",
    "https://api.example.com/users/123",
    json={"email": "newemail@example.com"}
)
```

---

## Advanced Patterns

### Session Persistence

```python
from proxywhirl import ProxyRotator

# Use same rotator for multiple requests to maintain session
with ProxyRotator(proxies=[...]) as rotator:
    # Login
    login_response = rotator.post(
        "https://api.example.com/login",
        json={"username": "user", "password": "pass"}
    )
    token = login_response.json()["token"]
    
    # Make authenticated requests
    headers = {"Authorization": f"Bearer {token}"}
    data = rotator.get("https://api.example.com/data", headers=headers)
    
    # Logout
    rotator.post("https://api.example.com/logout", headers=headers)
```

### Rate Limiting Protection

```python
import time
from proxywhirl import ProxyRotator

with ProxyRotator(proxies=[...]) as rotator:
    for i in range(1000):
        response = rotator.get(f"https://api.example.com/data/{i}")
        print(f"Request {i}: {response.status_code}")
        
        # Sleep to avoid rate limits
        time.sleep(0.1)  # 10 requests per second
```

### Filtering Proxies by Tags

```python
from proxywhirl import ProxyRotator, Proxy

proxies = [
    Proxy(url="http://us-proxy1.com:8080", tags={"region:us", "speed:fast"}),
    Proxy(url="http://eu-proxy1.com:8080", tags={"region:eu", "speed:fast"}),
    Proxy(url="http://us-proxy2.com:8080", tags={"region:us", "speed:slow"}),
]

with ProxyRotator(proxies=proxies) as rotator:
    # Get only US proxies
    us_proxies = rotator.pool.filter_by_tags({"region:us"})
    print(f"US proxies: {len(us_proxies)}")
    
    # Get fast proxies
    fast_proxies = rotator.pool.filter_by_tags({"speed:fast"})
    print(f"Fast proxies: {len(fast_proxies)}")
```

---

## Logging

ProxyWhirl uses structured logging with loguru. Configure logging level:

```python
from loguru import logger

# Set log level
logger.remove()  # Remove default handler
logger.add(
    "proxywhirl.log",
    level="DEBUG",
    format="{time} {level} {message}",
    rotation="10 MB"
)

# Now logs will be written to file
from proxywhirl import ProxyRotator
rotator = ProxyRotator(proxies=[...])
```

Or via configuration:

```python
from proxywhirl import ProxyConfiguration

config = ProxyConfiguration(
    log_level="DEBUG",
    log_format="json",  # JSON structured logs
    log_redact_credentials=True  # Never log passwords
)
```

---

## Testing

### Using in Tests

```python
import pytest
from proxywhirl import ProxyRotator

def test_api_integration():
    proxies = ["http://test-proxy.com:8080"]
    
    with ProxyRotator(proxies=proxies) as rotator:
        response = rotator.get("https://httpbin.org/ip")
        assert response.status_code == 200
        assert "origin" in response.json()

@pytest.mark.asyncio
async def test_async_api():
    from proxywhirl import AsyncProxyRotator
    
    proxies = ["http://test-proxy.com:8080"]
    
    async with AsyncProxyRotator(proxies=proxies) as rotator:
        response = await rotator.get("https://httpbin.org/ip")
        assert response.status_code == 200
```

---

## Next Steps

- **CLI Interface**: See Feature 002 for command-line usage
- **REST API**: See Feature 003 for REST API integration
- **Advanced Strategies**: See Feature 004 for custom rotation algorithms
- **Monitoring**: See Feature 006 for health monitoring and metrics
- **Documentation**: See Feature 016 for full API reference

---

## Common Troubleshooting

### Issue: "ProxyPoolEmptyError"

**Cause**: No proxies in the pool or all proxies are dead.

**Solution**:
```python
# Check pool stats before making requests
stats = rotator.get_pool_stats()
if stats['healthy_proxies'] == 0:
    print("No healthy proxies available")
    # Add more proxies or wait for health checks
```

### Issue: "ProxyAuthenticationError"

**Cause**: Invalid proxy credentials.

**Solution**:
```python
# Verify credentials are correct
proxy = Proxy(
    url="http://proxy.com:8080",
    username="correct_username",
    password="correct_password"
)
```

### Issue: Slow performance

**Cause**: Connection pooling not configured properly.

**Solution**:
```python
config = ProxyConfiguration(
    pool_connections=50,      # Increase pool size
    pool_max_keepalive=100,   # More keepalive connections
    timeout=30                # Adjust timeout
)
```

---

## Production Deployment

### Best Practices

```python
from proxywhirl import ProxyRotator, ProxyConfiguration, CircuitBreaker, RateLimiter
from pathlib import Path
import logging

# Configure structured logging
logger = logging.getLogger("proxywhirl")
logger.setLevel(logging.INFO)

# Production configuration
config = ProxyConfiguration(
    timeout=30,
    max_retries=3,
    verify_ssl=True,
    pool_connections=100,
    pool_max_keepalive=200,
    health_check_enabled=True,
    health_check_interval=300  # 5 minutes
)

# Initialize with monitoring hooks
def on_failure(event):
    logger.error(f"Proxy failed: {event.proxy.url}", extra={"error": event.error})

def on_success(event):
    logger.debug(f"Request succeeded via {event.proxy.url}")

rotator = ProxyRotator(
    # User-provided premium proxies (priority)
    proxies=[
        "http://user:pass@premium-proxy1.com:8080",
        "http://user:pass@premium-proxy2.com:8080",
    ],
    # Auto-fetch free proxies as backup
    auto_fetch_sources=[
        "https://api.proxyscrape.com/v2/?request=get&protocol=http&format=json"
    ],
    auto_fetch_interval=3600,
    validate_fetched=True,
    # Configuration
    strategy="weighted",
    config=config,
    # Rate limiting
    rate_limiter=RateLimiter(requests_per_second=10),
    # Circuit breaker
    circuit_breaker=CircuitBreaker(
        failure_threshold=5,
        timeout=60,
        success_threshold=2
    )
)

# Register event handlers
rotator.on("request_failure", on_failure)
rotator.on("request_success", on_success)

# Start auto-save
rotator.auto_save_start(Path("./data/proxies.json"), interval=300)

# Use in production
try:
    response = rotator.get("https://api.example.com/data")
    logger.info("Request completed", extra={"status": response.status_code})
finally:
    rotator.auto_save_stop()
    rotator.close()
```

### Docker Deployment

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install with extras
RUN pip install proxywhirl[all]

# Copy application
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Run application
CMD ["python", "main.py"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  proxywhirl-app:
    build: .
    volumes:
      - ./data:/app/data
    environment:
      - PROXY_POOL_PATH=/app/data/proxies.json
      - AUTO_SAVE_INTERVAL=300
      - LOG_LEVEL=INFO
    restart: unless-stopped
```

### Kubernetes Deployment

**deployment.yaml**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: proxywhirl-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: proxywhirl
  template:
    metadata:
      labels:
        app: proxywhirl
    spec:
      containers:
      - name: app
        image: proxywhirl-app:latest
        volumeMounts:
        - name: proxy-storage
          mountPath: /app/data
        env:
        - name: PROXY_POOL_PATH
          value: /app/data/proxies.json
        - name: AUTO_SAVE_INTERVAL
          value: "300"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
      volumes:
      - name: proxy-storage
        persistentVolumeClaim:
          claimName: proxy-storage-pvc
```

### Monitoring Integration

**Prometheus Metrics**:
```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Define metrics
proxy_requests = Counter("proxy_requests_total", "Total requests", ["proxy", "status"])
proxy_latency = Histogram("proxy_request_duration_seconds", "Request duration")
active_proxies = Gauge("proxy_pool_active", "Active proxies in pool")

# Integrate with ProxyWhirl
def record_metrics(event):
    status = "success" if event.success else "failure"
    proxy_requests.labels(proxy=event.proxy.url, status=status).inc()
    proxy_latency.observe(event.duration_ms / 1000)

rotator.on("request_complete", record_metrics)

# Update pool size periodically
def update_pool_metrics():
    active_proxies.set(len(rotator.pool.healthy_proxies))

# Start metrics server
start_http_server(8000)
```

---

## Getting Help

- **Documentation**: <https://proxywhirl.readthedocs.io>
- **Issues**: <https://github.com/yourusername/proxywhirl/issues>
- **Discussions**: <https://github.com/yourusername/proxywhirl/discussions>
