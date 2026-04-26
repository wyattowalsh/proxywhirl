# ProxyWhirl API Reference - v1

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All requests require an API key header:

```
Authorization: Bearer YOUR_API_KEY
```

Set the API key via:
- Environment variable: `PROXYWHIRL_API_KEY`
- Configuration file: `api.api_key` in config.toml
- Command line: `--api-key` flag

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error code",
  "detail": "Human-readable error message",
  "timestamp": "2024-04-26T12:34:56Z",
  "request_id": "req_abc123"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (invalid input) |
| 401 | Unauthorized (invalid/missing API key) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 429 | Rate Limited |
| 500 | Server Error |
| 503 | Service Unavailable |

## Endpoints

### Pool Management

#### GET /pool
Retrieve the current proxy pool.

**Query Parameters:**
- `filter` (string): Filter by proxy status: `healthy`, `degraded`, `unhealthy`, `inactive`
- `limit` (integer): Maximum proxies to return (default: 100, max: 1000)
- `offset` (integer): Pagination offset (default: 0)
- `tags` (string): Comma-separated tags to filter by
- `protocol` (string): Filter by protocol: `http`, `https`, `socks4`, `socks5`

**Response:**
```json
{
  "pool": {
    "total": 1250,
    "healthy": 980,
    "degraded": 200,
    "unhealthy": 70,
    "proxies": [
      {
        "id": "proxy_123",
        "protocol": "http",
        "host": "192.168.1.1",
        "port": 8080,
        "username": null,
        "password": null,
        "tags": ["us", "fast"],
        "health_status": "healthy",
        "success_count": 1523,
        "failure_count": 12,
        "latency_ms": 234,
        "last_used_at": "2024-04-26T12:30:00Z",
        "created_at": "2024-04-20T08:15:00Z"
      }
    ]
  },
  "timestamp": "2024-04-26T12:34:56Z"
}
```

**Example:**
```bash
curl -H "Authorization: Bearer sk_abc123" \
  "http://localhost:8000/api/v1/pool?filter=healthy&limit=50"
```

#### GET /pool/stats
Get detailed statistics about the proxy pool.

**Response:**
```json
{
  "stats": {
    "total_proxies": 1250,
    "healthy": 980,
    "degraded": 200,
    "unhealthy": 70,
    "health_percentage": 78.4,
    "avg_latency_ms": 234.5,
    "p50_latency_ms": 210,
    "p95_latency_ms": 420,
    "p99_latency_ms": 580,
    "success_rate": 0.9923,
    "total_requests": 45230,
    "total_failures": 350,
    "uptime_percentage": 99.23,
    "cache_hit_rate": 0.87,
    "circuit_breaker_state": "closed",
    "by_protocol": {
      "http": 600,
      "https": 400,
      "socks4": 150,
      "socks5": 100
    },
    "by_location": {
      "us": 450,
      "gb": 280,
      "de": 230,
      "fr": 290
    },
    "last_updated": "2024-04-26T12:34:56Z"
  }
}
```

#### GET /pool/health
Get health status of all proxies.

**Query Parameters:**
- `status` (string): Filter by status
- `sort_by` (string): Sort by: `latency`, `success_rate`, `last_used`

**Response:**
```json
{
  "health": [
    {
      "proxy_id": "proxy_123",
      "status": "healthy",
      "latency_ms": 234,
      "success_rate": 0.98,
      "consecutive_failures": 0,
      "last_check": "2024-04-26T12:33:00Z",
      "next_check": "2024-04-26T12:38:00Z"
    }
  ]
}
```

### Proxy Selection

#### GET /proxy
Get a single proxy with optional context.

**Query Parameters:**
- `protocol` (string): Preferred protocol
- `location` (string): Preferred geographic location
- `min_success_rate` (float): Minimum success rate (0.0-1.0)
- `tags` (string): Required tags (comma-separated)
- `exclude_tags` (string): Excluded tags

**Response:**
```json
{
  "proxy": {
    "id": "proxy_123",
    "protocol": "http",
    "host": "192.168.1.1",
    "port": 8080,
    "username": null,
    "password": null,
    "tags": ["us", "fast"],
    "health_status": "healthy",
    "success_count": 1523,
    "failure_count": 12,
    "latency_ms": 234,
    "created_at": "2024-04-20T08:15:00Z"
  },
  "session_id": "sess_xyz789",
  "timestamp": "2024-04-26T12:34:56Z"
}
```

**Example:**
```bash
curl -H "Authorization: Bearer sk_abc123" \
  "http://localhost:8000/api/v1/proxy?protocol=https&location=us"
```

#### POST /proxy/feedback
Report success or failure for a proxy.

**Request Body:**
```json
{
  "proxy_id": "proxy_123",
  "session_id": "sess_xyz789",
  "status": "success",
  "latency_ms": 234,
  "error_code": null,
  "error_message": null
}
```

**Status Values:** `success`, `failure`, `timeout`, `auth_failed`, `connection_refused`

**Response:**
```json
{
  "success": true,
  "message": "Feedback recorded",
  "proxy": {
    "id": "proxy_123",
    "health_status": "healthy",
    "success_count": 1524,
    "failure_count": 12
  }
}
```

### Proxy Management

#### POST /proxy
Add a new proxy to the pool.

**Request Body:**
```json
{
  "protocol": "http",
  "host": "192.168.1.1",
  "port": 8080,
  "username": "user",
  "password": "pass",
  "tags": ["us", "fast"],
  "metadata": {"custom": "data"}
}
```

**Response:**
```json
{
  "proxy": {
    "id": "proxy_456",
    "protocol": "http",
    "host": "192.168.1.1",
    "port": 8080,
    "tags": ["us", "fast"],
    "created_at": "2024-04-26T12:34:56Z"
  },
  "message": "Proxy added successfully"
}
```

#### POST /proxy/batch
Add multiple proxies.

**Request Body:**
```json
{
  "proxies": [
    {"protocol": "http", "host": "192.168.1.1", "port": 8080},
    {"protocol": "https", "host": "192.168.1.2", "port": 8443}
  ]
}
```

**Response:**
```json
{
  "added": 2,
  "duplicates": 0,
  "invalid": 0,
  "proxies": [...]
}
```

#### GET /proxy/{proxy_id}
Get details for a specific proxy.

**Response:**
```json
{
  "proxy": {
    "id": "proxy_123",
    "protocol": "http",
    "host": "192.168.1.1",
    "port": 8080,
    "tags": ["us", "fast"],
    "health_status": "healthy",
    "success_count": 1523,
    "failure_count": 12,
    "latency_ms": 234,
    "geo_location": {
      "country": "US",
      "city": "New York",
      "latitude": 40.7128,
      "longitude": -74.0060
    },
    "created_at": "2024-04-20T08:15:00Z",
    "last_used_at": "2024-04-26T12:33:00Z"
  }
}
```

#### PUT /proxy/{proxy_id}
Update a proxy's metadata or tags.

**Request Body:**
```json
{
  "tags": ["us", "fast", "premium"],
  "metadata": {"tier": "premium"}
}
```

**Response:**
```json
{
  "proxy": {...},
  "message": "Proxy updated"
}
```

#### DELETE /proxy/{proxy_id}
Remove a proxy from the pool.

**Response:**
```json
{
  "success": true,
  "message": "Proxy deleted",
  "id": "proxy_123"
}
```

#### DELETE /pool
Clear all proxies from the pool.

**Query Parameters:**
- `filter` (string): Only delete with specific health status

**Response:**
```json
{
  "success": true,
  "deleted": 1250,
  "message": "Pool cleared"
}
```

### Proxy Sources

#### GET /sources
List all available proxy sources.

**Response:**
```json
{
  "sources": [
    {
      "id": "free-proxy-list",
      "name": "Free Proxy List",
      "url": "https://www.freeproxylists.net",
      "type": "free",
      "protocols": ["http", "https"],
      "proxy_count": 500,
      "last_fetched": "2024-04-26T12:00:00Z",
      "next_fetch": "2024-04-26T18:00:00Z",
      "enabled": true
    }
  ],
  "total": 42
}
```

#### POST /sources/fetch
Manually fetch proxies from sources.

**Request Body:**
```json
{
  "source_ids": ["free-proxy-list"],
  "validate": true,
  "replace_pool": false
}
```

**Response:**
```json
{
  "fetched": 500,
  "added": 480,
  "duplicates": 20,
  "invalid": 0,
  "errors": []
}
```

#### GET /sources/{source_id}
Get details for a specific source.

**Response:**
```json
{
  "source": {
    "id": "free-proxy-list",
    "name": "Free Proxy List",
    "url": "https://www.freeproxylists.net",
    "type": "free",
    "protocols": ["http", "https"],
    "proxy_count": 500,
    "last_fetched": "2024-04-26T12:00:00Z",
    "next_fetch": "2024-04-26T18:00:00Z",
    "enabled": true,
    "error_rate": 0.04,
    "avg_validity": 0.96
  }
}
```

### Strategy Management

#### GET /strategies
List available rotation strategies.

**Response:**
```json
{
  "strategies": [
    {
      "id": "round_robin",
      "name": "Round Robin",
      "description": "Cyclic sequential rotation",
      "parameters": {
        "fairness": true
      }
    },
    {
      "id": "weighted",
      "name": "Weighted",
      "description": "Probability-weighted selection",
      "parameters": {
        "weight_field": "success_rate"
      }
    }
  ]
}
```

#### GET /strategies/current
Get the currently active strategy.

**Response:**
```json
{
  "strategy": {
    "id": "round_robin",
    "name": "Round Robin",
    "config": {}
  }
}
```

#### POST /strategies/switch
Switch to a different rotation strategy.

**Request Body:**
```json
{
  "strategy_id": "weighted",
  "config": {}
}
```

**Response:**
```json
{
  "success": true,
  "previous": "round_robin",
  "current": "weighted",
  "message": "Strategy switched"
}
```

### Sessions

#### GET /sessions
List active sessions.

**Query Parameters:**
- `limit` (integer): Maximum results
- `active_only` (boolean): Only active sessions

**Response:**
```json
{
  "sessions": [
    {
      "id": "sess_abc123",
      "proxy_id": "proxy_456",
      "created_at": "2024-04-26T12:00:00Z",
      "last_used_at": "2024-04-26T12:34:56Z",
      "request_count": 125,
      "metadata": {}
    }
  ],
  "total": 42
}
```

#### POST /sessions
Create a new session.

**Request Body:**
```json
{
  "proxy_id": "proxy_456",
  "metadata": {"user_agent": "Mozilla/5.0"}
}
```

**Response:**
```json
{
  "session": {
    "id": "sess_xyz789",
    "proxy_id": "proxy_456",
    "created_at": "2024-04-26T12:34:56Z"
  }
}
```

#### GET /sessions/{session_id}
Get session details.

**Response:**
```json
{
  "session": {
    "id": "sess_abc123",
    "proxy_id": "proxy_456",
    "created_at": "2024-04-26T12:00:00Z",
    "last_used_at": "2024-04-26T12:34:56Z",
    "request_count": 125,
    "success_count": 120,
    "failure_count": 5,
    "metadata": {}
  }
}
```

#### DELETE /sessions/{session_id}
End a session.

**Response:**
```json
{
  "success": true,
  "message": "Session ended"
}
```

### Health Checks

#### POST /health/check
Perform immediate health check on proxies.

**Request Body:**
```json
{
  "proxy_ids": ["proxy_123", "proxy_456"],
  "url": "https://httpbin.org/ip",
  "timeout_seconds": 5
}
```

**Response:**
```json
{
  "results": [
    {
      "proxy_id": "proxy_123",
      "healthy": true,
      "latency_ms": 234,
      "status_code": 200
    }
  ],
  "duration_seconds": 2.3
}
```

#### GET /health/report
Get comprehensive health report.

**Response:**
```json
{
  "report": {
    "total": 1250,
    "healthy": 980,
    "degraded": 200,
    "unhealthy": 70,
    "circuit_breaker": {
      "state": "closed",
      "failure_count": 2,
      "failure_threshold": 10
    },
    "checks_today": 12500,
    "avg_check_time_ms": 2.3
  }
}
```

### Validation

#### POST /validate
Validate proxy URLs or individual proxies.

**Request Body:**
```json
{
  "proxies": [
    "http://192.168.1.1:8080",
    "socks5://user:pass@proxy.example.com:1080"
  ]
}
```

**Response:**
```json
{
  "results": [
    {
      "input": "http://192.168.1.1:8080",
      "valid": true,
      "proxy": {
        "protocol": "http",
        "host": "192.168.1.1",
        "port": 8080
      }
    }
  ]
}
```

### Configuration

#### GET /config
Get current configuration (sanitized).

**Response:**
```json
{
  "config": {
    "rotation_strategy": "round_robin",
    "health_check_interval_seconds": 300,
    "max_pool_size": 5000,
    "cache_ttl_seconds": 300,
    "rate_limit_requests_per_second": 100,
    "circuit_breaker": {
      "failure_threshold": 10,
      "recovery_timeout_seconds": 60
    }
  }
}
```

#### PUT /config
Update configuration.

**Request Body:**
```json
{
  "rotation_strategy": "weighted",
  "health_check_interval_seconds": 600,
  "rate_limit_requests_per_second": 50
}
```

**Response:**
```json
{
  "config": {...},
  "message": "Configuration updated"
}
```

### Monitoring

#### GET /metrics
Export Prometheus metrics.

**Response (Plain Text):**
```
# HELP proxywhirl_pool_size Total proxies in pool
# TYPE proxywhirl_pool_size gauge
proxywhirl_pool_size 1250

# HELP proxywhirl_healthy_proxies Number of healthy proxies
# TYPE proxywhirl_healthy_proxies gauge
proxywhirl_healthy_proxies 980

# HELP proxywhirl_request_total Total requests
# TYPE proxywhirl_request_total counter
proxywhirl_request_total{status="success"} 45000
proxywhirl_request_total{status="failure"} 350

# HELP proxywhirl_latency_seconds Request latency
# TYPE proxywhirl_latency_seconds histogram
proxywhirl_latency_seconds_bucket{le="0.1"} 5000
proxywhirl_latency_seconds_bucket{le="0.5"} 40000
proxywhirl_latency_seconds_bucket{le="1.0"} 45000
```

#### GET /logs
Stream recent logs.

**Query Parameters:**
- `level` (string): Filter by log level (DEBUG, INFO, WARNING, ERROR)
- `limit` (integer): Number of logs to return (default: 100)

**Response:**
```json
{
  "logs": [
    {
      "timestamp": "2024-04-26T12:34:56Z",
      "level": "INFO",
      "message": "Proxy pool updated",
      "proxy_id": "proxy_123"
    }
  ]
}
```

### Export/Import

#### GET /export
Export current pool as JSON or CSV.

**Query Parameters:**
- `format` (string): `json` or `csv`
- `include_metadata` (boolean): Include metadata

**Response:**
```json
{
  "proxies": [
    {
      "protocol": "http",
      "host": "192.168.1.1",
      "port": 8080,
      "tags": ["us"]
    }
  ]
}
```

#### POST /import
Import proxies from JSON or CSV.

**Request Body:**
```json
{
  "format": "json",
  "proxies": [
    {"protocol": "http", "host": "192.168.1.1", "port": 8080}
  ],
  "merge": true
}
```

**Response:**
```json
{
  "imported": 100,
  "duplicates": 5,
  "invalid": 0
}
```

## Rate Limiting

API rate limits are enforced per API key:

- **Free tier**: 100 requests/minute
- **Standard tier**: 1,000 requests/minute
- **Premium tier**: 10,000 requests/minute

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640000000
```

When rate limited, you'll receive a 429 status with:

```json
{
  "error": "rate_limited",
  "detail": "Rate limit exceeded. Reset at 2024-04-26T13:00:00Z",
  "retry_after_seconds": 60
}
```

## Pagination

Endpoints that return lists support pagination:

**Query Parameters:**
- `limit` (integer): Results per page (default: 20, max: 100)
- `offset` (integer): Pagination offset (default: 0)

**Response:**
```json
{
  "results": [...],
  "pagination": {
    "limit": 20,
    "offset": 0,
    "total": 1250,
    "has_next": true,
    "has_previous": false
  }
}
```

## Webhook Events

ProxyWhirl can send webhook events for important changes:

**Event Types:**
- `proxy.added`: New proxy added
- `proxy.removed`: Proxy removed
- `proxy.health_changed`: Health status changed
- `pool.updated`: Pool configuration changed
- `circuit_breaker.triggered`: Circuit breaker opened/closed

**Webhook Payload:**
```json
{
  "event": "proxy.health_changed",
  "timestamp": "2024-04-26T12:34:56Z",
  "data": {
    "proxy_id": "proxy_123",
    "previous_status": "healthy",
    "current_status": "degraded"
  }
}
```

## WebSocket Streaming

Connect to `/ws/stream` for real-time events:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/stream?api_key=sk_abc123');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Event:', data.type, data.data);
};
```

**Event Types on WebSocket:**
- `pool_updated`: Pool changed
- `proxy_health_changed`: Proxy health changed
- `metrics_snapshot`: Metrics update
- `error`: Error occurred

