# ProxyWhirl REST API Usage Guide

Complete guide for using the ProxyWhirl REST API.

## Table of Contents

- [Getting Started](#getting-started)
- [Authentication](#authentication)
- [Endpoint Reference](#endpoint-reference)
- [Rate Limiting](#rate-limiting)
- [Error Handling](#error-handling)
- [Performance Tips](#performance-tips)

## Getting Started

### Starting the API Server

```bash
# Development mode with auto-reload
uv run uvicorn proxywhirl.api:app --reload

# Production mode
uv run uvicorn proxywhirl.api:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Docker

```bash
# Start with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Accessing Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Authentication

### No Authentication (Default)

By default, the API is open and requires no authentication:

```bash
curl http://localhost:8000/api/v1/health
```

### API Key Authentication

Enable authentication with environment variables:

```bash
export PROXYWHIRL_REQUIRE_AUTH=true
export PROXYWHIRL_API_KEY=your-secret-key-here
```

Include the API key in requests:

```bash
curl http://localhost:8000/api/v1/proxies \
  -H "X-API-Key: your-secret-key-here"
```

## Endpoint Reference

### Proxied Requests

#### POST /api/v1/request

Make HTTP requests through rotating proxies.

**Request Body:**
```json
{
  "url": "https://httpbin.org/ip",
  "method": "GET",
  "headers": {
    "User-Agent": "MyApp/1.0"
  },
  "body": null,
  "timeout": 30
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "status_code": 200,
    "headers": {...},
    "body": "{...}",
    "proxy_used": {
      "id": "proxy-123",
      "url": "http://proxy.example.com:8080"
    },
    "elapsed_ms": 245
  },
  "meta": {
    "timestamp": "2025-01-01T12:00:00Z",
    "request_id": "req-abc123"
  }
}
```

**Supported Methods:**
- GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS

**Error Codes:**
- `PROXY_POOL_EMPTY` (503): No proxies available
- `PROXY_FAILOVER_EXHAUSTED` (502): All proxies failed
- `TARGET_UNREACHABLE` (504): Target server unreachable
- `REQUEST_TIMEOUT` (504): Request timed out

### Pool Management

#### GET /api/v1/proxies

List all proxies with pagination.

**Query Parameters:**
- `page` (int, default 1): Page number
- `page_size` (int, default 50): Items per page
- `status_filter` (str, optional): Filter by status (active, failed, validating)

**Response:**
```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "id": "proxy-123",
        "url": "http://proxy.example.com:8080",
        "protocol": "http",
        "status": "active",
        "health": "healthy",
        "stats": {
          "total_requests": 100,
          "successful_requests": 95,
          "failed_requests": 5,
          "avg_latency_ms": 250.5
        },
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T12:00:00Z"
      }
    ],
    "total": 10,
    "page": 1,
    "page_size": 50,
    "has_next": false,
    "has_prev": false
  }
}
```

#### POST /api/v1/proxies

Add a new proxy to the pool.

**Request Body:**
```json
{
  "url": "http://proxy.example.com:8080",
  "username": "user",
  "password": "pass"
}
```

**Response:** HTTP 201 with proxy details

**Errors:**
- HTTP 409 if proxy already exists
- HTTP 400 if invalid proxy format

#### GET /api/v1/proxies/{id}

Get details for a specific proxy.

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "proxy-123",
    "url": "http://proxy.example.com:8080",
    ...
  }
}
```

**Errors:**
- HTTP 404 if proxy not found

#### DELETE /api/v1/proxies/{id}

Remove a proxy from the pool.

**Response:** HTTP 204 No Content

**Errors:**
- HTTP 404 if proxy not found

#### POST /api/v1/proxies/test

Run health check on proxies.

**Request Body:**
```json
{
  "proxy_ids": ["proxy-123", "proxy-456"]
}
```

Omit `proxy_ids` to check all proxies.

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "proxy_id": "proxy-123",
      "status": "working",
      "latency_ms": 245,
      "error": null,
      "tested_at": "2025-01-01T12:00:00Z"
    }
  ]
}
```

### Monitoring

#### GET /api/v1/health

Health check endpoint for load balancers.

**Response:**
```json
{
  "status": "healthy",
  "uptime_seconds": 3600,
  "version": "1.0.0",
  "timestamp": "2025-01-01T12:00:00Z"
}
```

**Status Values:**
- `healthy`: All proxies working
- `degraded`: Some proxies failing
- `unhealthy`: All proxies failing (returns HTTP 503)

#### GET /api/v1/ready

Readiness probe for Kubernetes.

**Response:**
```json
{
  "ready": true,
  "checks": {
    "proxy_pool_initialized": true,
    "storage_connected": true
  }
}
```

Returns HTTP 503 if not ready.

#### GET /api/v1/status

Detailed pool status and statistics.

**Response:**
```json
{
  "pool_stats": {
    "total": 10,
    "active": 8,
    "failed": 2,
    "healthy_percentage": 80.0,
    "last_rotation": "2025-01-01T12:00:00Z"
  },
  "rotation_strategy": "round-robin",
  "storage_backend": "memory",
  "config_source": "environment"
}
```

#### GET /api/v1/metrics

Performance metrics for monitoring.

**Response:**
```json
{
  "requests_total": 1000,
  "requests_per_second": 5.5,
  "avg_latency_ms": 250.0,
  "error_rate": 0.05,
  "proxy_stats": [
    {
      "proxy_id": "proxy-123",
      "requests": 100,
      "success_rate": 0.95,
      "avg_latency_ms": 245.0,
      "last_used": "2025-01-01T12:00:00Z"
    }
  ]
}
```

### Configuration

#### GET /api/v1/config

Get current configuration.

**Response:**
```json
{
  "rotation_strategy": "round-robin",
  "timeout": 30,
  "max_retries": 3,
  "rate_limits": {
    "default_limit": 100,
    "request_endpoint_limit": 50
  },
  "auth_enabled": false,
  "cors_origins": ["*"]
}
```

#### PUT /api/v1/config

Update configuration at runtime.

**Request Body:**
```json
{
  "rotation_strategy": "random",
  "timeout": 60,
  "max_retries": 5
}
```

All fields are optional (partial updates supported).

**Response:** Updated configuration

**Errors:**
- HTTP 400 if invalid values

## Rate Limiting

The API includes built-in rate limiting per IP address:

| Endpoint | Limit |
|----------|-------|
| Default | 100 requests/minute |
| POST /api/v1/request | 50 requests/minute |

When exceeded, the API returns:
- HTTP 429 Too Many Requests
- `Retry-After` header with seconds to wait

## Error Handling

All errors follow a consistent format:

```json
{
  "status": "error",
  "error": {
    "code": "PROXY_POOL_EMPTY",
    "message": "No proxies available in pool",
    "details": null
  },
  "meta": {
    "timestamp": "2025-01-01T12:00:00Z",
    "request_id": "req-abc123"
  }
}
```

### Error Codes

**Proxied Requests:**
- `PROXY_POOL_EMPTY`: No proxies configured
- `PROXY_FAILOVER_EXHAUSTED`: All proxies failed
- `TARGET_UNREACHABLE`: Cannot reach target server
- `REQUEST_TIMEOUT`: Request exceeded timeout

**Pool Management:**
- `PROXY_NOT_FOUND`: Proxy ID not found
- `PROXY_ALREADY_EXISTS`: Duplicate proxy URL
- `INVALID_PROXY_FORMAT`: Malformed proxy URL

**Configuration:**
- `VALIDATION_ERROR`: Invalid configuration values
- `INVALID_STRATEGY`: Unknown rotation strategy

## Performance Tips

### 1. Use Connection Pooling

Reuse HTTP clients for multiple requests:

```python
import httpx
import asyncio

async def main():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Reuse client for multiple requests
        for _ in range(100):
            response = await client.post("/api/v1/request", json={...})
```

### 2. Enable Response Compression

Add compression middleware for large responses:

```bash
# Configure reverse proxy (nginx/caddy) with gzip
```

### 3. Use Health Checks Efficiently

- Set up periodic health checks (every 30-60 seconds)
- Use `proxy_ids` filter to check specific proxies
- Don't run full pool checks on every request

### 4. Monitor Metrics

Track key metrics to optimize performance:

```bash
# Check every minute
watch -n 60 'curl -s http://localhost:8000/api/v1/metrics | jq .error_rate'
```

### 5. Configure Appropriate Timeouts

Balance between reliability and speed:

```bash
# Fast proxies (e.g., premium)
export PROXYWHIRL_TIMEOUT=15

# Slow proxies (e.g., free)
export PROXYWHIRL_TIMEOUT=60
```

### 6. Use Persistent Storage

Enable SQLite storage for persistence across restarts:

```bash
export PROXYWHIRL_STORAGE_PATH=/data/proxies.db
```

### 7. Optimize Retry Logic

Adjust retries based on your proxy quality:

```bash
# High-quality proxies (fewer retries needed)
export PROXYWHIRL_MAX_RETRIES=2

# Low-quality proxies (more retries needed)
export PROXYWHIRL_MAX_RETRIES=5
```

## Security Best Practices

1. **Enable API Key Authentication** in production
2. **Configure CORS** to restrict origins
3. **Use HTTPS** with a reverse proxy (nginx, Caddy)
4. **Set Rate Limits** appropriate for your use case
5. **Encrypt Storage** if persisting credentials
6. **Monitor Access Logs** for suspicious activity
7. **Keep Dependencies Updated** for security patches

## Deployment Examples

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name api.example.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: proxywhirl-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: proxywhirl-api
  template:
    metadata:
      labels:
        app: proxywhirl-api
    spec:
      containers:
      - name: api
        image: proxywhirl-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: PROXYWHIRL_STRATEGY
          value: "round-robin"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /api/v1/ready
            port: 8000
          initialDelaySeconds: 3
          periodSeconds: 10
```

## Troubleshooting

### API Won't Start

Check logs for errors:
```bash
uv run uvicorn proxywhirl.api:app --log-level debug
```

### Proxies Not Working

1. Check proxy pool: `GET /api/v1/proxies`
2. Run health check: `POST /api/v1/proxies/test`
3. Check metrics: `GET /api/v1/metrics`

### Rate Limiting Issues

Adjust limits via configuration:
```bash
# Increase limits
curl -X PUT http://localhost:8000/api/v1/config \
  -H "Content-Type: application/json" \
  -d '{"rate_limits": {"request_endpoint_limit": 100}}'
```

### High Latency

- Check proxy quality with metrics
- Reduce timeout values
- Switch to faster rotation strategy (least-used)
- Remove slow proxies from pool

## Support

For issues and questions:
- GitHub Issues: https://github.com/wyattowalsh/proxywhirl/issues
- Documentation: See README.md and docs/
- Examples: See examples/ directory
