# API Reference

Complete documentation for all public APIs in ProxyWhirl.

## REST API Endpoints

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
If `PROXYWHIRL_REQUIRE_AUTH=true`, include header:
```
Authorization: Bearer YOUR_API_KEY
```

### Health Check
```http
GET /api/v1/health
```

**Response** (200 OK):
```json
{
  "status": "healthy",
  "version": "0.3.3",
  "uptime_seconds": 12345,
  "proxies_loaded": 150
}
```

### Get Next Proxy
```http
GET /api/v1/proxy/next
```

**Query Parameters:**
- `timeout` (int): Request timeout in seconds (default: 30)
- `format` (string): Return format - `url`, `dict`, `json` (default: `dict`)

**Response** (200 OK):
```json
{
  "host": "192.168.1.1",
  "port": 8080,
  "protocol": "http",
  "username": "user",
  "password": "pass",
  "country": "US",
  "anonymity": "elite",
  "response_time": 0.45,
  "last_checked": "2024-01-15T10:30:00Z"
}
```

**Example:**
```bash
curl -s http://localhost:8000/api/v1/proxy/next?format=url
# Output: http://user:pass@192.168.1.1:8080
```

### Validate Proxy
```http
POST /api/v1/proxy/validate
```

**Request Body:**
```json
{
  "host": "192.168.1.1",
  "port": 8080,
  "protocol": "http",
  "username": "user",
  "password": "pass"
}
```

**Response** (200 OK):
```json
{
  "is_valid": true,
  "response_time": 0.32,
  "status_code": 200,
  "can_access_https": true
}
```

### Get Pool Statistics
```http
GET /api/v1/stats
```

**Response** (200 OK):
```json
{
  "total_proxies": 150,
  "healthy_proxies": 142,
  "average_response_time": 0.45,
  "protocols": {
    "http": 80,
    "https": 50,
    "socks4": 15,
    "socks5": 5
  },
  "countries": {
    "US": 60,
    "GB": 45,
    "DE": 30,
    "FR": 15
  }
}
```

## Python Client API

### Basic Usage
```python
from proxywhirl import ProxyWhirl

rotator = ProxyWhirl()

# Get next proxy
proxy = rotator.get_next_proxy()
print(proxy)
# Output: Proxy(host='192.168.1.1', port=8080, ...)

# Use in requests
import httpx
with httpx.Client(proxies=proxy.to_url()) as client:
    response = client.get('https://example.com')
```

### Async Usage
```python
from proxywhirl import AsyncProxyWhirl
import asyncio

async def main():
    rotator = AsyncProxyWhirl()
    proxy = await rotator.get_next_proxy()
    print(proxy)

asyncio.run(main())
```

### Configuration
```python
from proxywhirl import ProxyWhirl, ProxyConfiguration, StrategyConfig

config = ProxyConfiguration(
    strategy=StrategyConfig(type="weighted", weights={"US": 0.5, "GB": 0.3}),
    rotation_interval=5,
    validation_enabled=True,
    cache_enabled=True
)

rotator = ProxyWhirl(config=config)
```

## Configuration Options

### ProxyConfiguration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `strategy` | StrategyConfig | round-robin | Rotation strategy |
| `rotation_interval` | int | 10 | Seconds between rotations |
| `validation_enabled` | bool | True | Enable proxy validation |
| `cache_enabled` | bool | True | Enable caching |
| `max_retries` | int | 3 | Max retry attempts |
| `timeout` | int | 30 | Request timeout (seconds) |
| `persistence_enabled` | bool | True | Persist to database |

### StrategyConfig

**Types:** `round-robin`, `random`, `weighted`, `performance-based`, `least-used`

**Example - Weighted Strategy:**
```python
config = StrategyConfig(
    type="weighted",
    weights={"US": 0.5, "GB": 0.3, "DE": 0.2}
)
```

## Error Handling

All exceptions inherit from `ProxyWhirlError`:

```python
from proxywhirl import (
    ProxyWhirlError,
    ProxyPoolEmptyError,
    ProxyValidationError,
    ProxyConnectionError
)

try:
    proxy = rotator.get_next_proxy()
except ProxyPoolEmptyError:
    print("No healthy proxies available")
except ProxyValidationError as e:
    print(f"Validation failed: {e}")
except ProxyWhirlError as e:
    print(f"Error: {e}")
```

## Rate Limiting

The API implements rate limiting (default: 100 requests per 60 seconds).

**Response when limit exceeded** (429 Too Many Requests):
```json
{
  "detail": "Rate limit exceeded: 100 requests per 60 seconds"
}
```

## Pagination

List endpoints support pagination:
```
GET /api/v1/proxies?limit=50&offset=0
```

**Parameters:**
- `limit` (int): Results per page (default: 50, max: 1000)
- `offset` (int): Starting position (default: 0)

## Filtering

Filter proxies by multiple criteria:
```
GET /api/v1/proxies?country=US&protocol=http&anonymity=elite
```

**Available Filters:**
- `country` (string): ISO country code
- `protocol` (string): http, https, socks4, socks5
- `anonymity` (string): transparent, anonymous, elite
- `min_response_time` (float): Minimum response time in seconds
- `max_response_time` (float): Maximum response time in seconds

## Webhooks

Register webhooks for pool events:

```http
POST /api/v1/webhooks
```

**Request Body:**
```json
{
  "url": "https://example.com/webhook",
  "events": ["proxy_added", "proxy_removed", "validation_failed"],
  "secret": "your-webhook-secret"
}
```

## CLI Commands

### List available commands
```bash
proxywhirl --help
```

### Fetch proxies
```bash
proxywhirl fetch --sources free --limit 100 --save
```

### Validate pool
```bash
proxywhirl validate --concurrency 10
```

### Export proxies
```bash
proxywhirl export --format json --output proxies.json
```

### Run interactive TUI
```bash
proxywhirl tui
```

## Rate Limiting Guide

Configure rate limiting per source:

```python
from proxywhirl import RateLimiter

limiter = RateLimiter(
    requests_per_second=10,
    burst_size=20
)

# Check if request allowed
if limiter.allow_request():
    # Make request
    pass
else:
    # Rate limited
    pass
```

## Performance Tips

1. **Use connection pooling:**
   ```python
   with httpx.Client() as client:
       for _ in range(100):
           proxy = rotator.get_next_proxy()
           client.get(url, proxies=proxy.to_url())
   ```

2. **Enable caching:**
   ```python
   config = ProxyConfiguration(cache_enabled=True)
   ```

3. **Batch operations:**
   ```python
   proxies = rotator.get_proxies(limit=100)
   ```

4. **Use async for I/O-bound work:**
   ```python
   async_rotator = AsyncProxyWhirl()
   ```

See [Performance Tuning Guide](performance-tuning.md) for more.
