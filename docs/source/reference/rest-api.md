---
title: REST API Usage
---

# ProxyWhirl REST API Usage Guide

Complete guide for using the ProxyWhirl REST API.

## Table of Contents

- [Getting Started](#getting-started)
- [Authentication](#authentication)
- [Endpoint Reference](#endpoint-reference)
- [Rate Limiting](#rate-limiting)
- [Error Handling](#error-handling)
- [Performance Tips](#performance-tips)
- [Security Best Practices](#security-best-practices)
  - [X-Forwarded-For Security](#x-forwarded-for-security-warning)
  - [Deployment Examples](#deployment-examples)
  - [Security Checklist](#x-forwarded-for-security-checklist)
- [Troubleshooting](#troubleshooting)

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

### Rotation Strategy Configuration

#### Understanding Rotation Strategies

ProxyWhirl supports 7 advanced rotation strategies that can be configured via the API:

| Strategy | Use Case | Performance | Key Feature |
|----------|----------|-------------|-------------|
| `round-robin` | Fair distribution | ~3μs | Perfect load balance |
| `random` | Unpredictable patterns | ~7μs | Uniform distribution |
| `weighted` | Prefer best proxies | ~9μs | Success-rate based |
| `least-used` | Even load balance | ~3μs | Tracks request counts |
| `performance-based` | Minimize latency | ~5μs | 15-25% faster |
| `session-persistence` | Sticky sessions | ~3μs | 99.9% same-proxy |
| `geo-targeted` | Region-specific | ~5μs | Country/region filter |

#### GET /api/v1/config

Get current rotation strategy and configuration:

```bash
curl http://localhost:8000/api/v1/config
```

**Response:**
```json
{
  "rotation_strategy": "round-robin",
  "timeout": 30,
  "max_retries": 3,
  "strategy_config": {
    "ema_alpha": 0.2,
    "session_ttl": 3600,
    "geo_fallback_enabled": false
  }
}
```

#### PUT /api/v1/config

Update rotation strategy at runtime (hot-swapping):

**Basic Strategy Change:**
```bash
curl -X PUT http://localhost:8000/api/v1/config \
  -H "Content-Type: application/json" \
  -d '{
    "rotation_strategy": "performance-based"
  }'
```

**With Strategy Configuration:**
```bash
# Performance-based with custom EMA alpha
curl -X PUT http://localhost:8000/api/v1/config \
  -H "Content-Type: application/json" \
  -d '{
    "rotation_strategy": "performance-based",
    "strategy_config": {
      "ema_alpha": 0.3
    }
  }'

# Weighted strategy with custom weights
curl -X PUT http://localhost:8000/api/v1/config \
  -H "Content-Type: application/json" \
  -d '{
    "rotation_strategy": "weighted",
    "strategy_config": {
      "weights": {
        "http://proxy1.com:8080": 0.5,
        "http://proxy2.com:8080": 0.3,
        "http://proxy3.com:8080": 0.2
      }
    }
  }'

# Session persistence with custom TTL
curl -X PUT http://localhost:8000/api/v1/config \
  -H "Content-Type: application/json" \
  -d '{
    "rotation_strategy": "session-persistence",
    "strategy_config": {
      "session_ttl": 7200
    }
  }'

# Geo-targeted with fallback
curl -X PUT http://localhost:8000/api/v1/config \
  -H "Content-Type: application/json" \
  -d '{
    "rotation_strategy": "geo-targeted",
    "strategy_config": {
      "geo_fallback_enabled": true,
      "geo_secondary_strategy": "round-robin"
    }
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "Configuration updated",
  "config": {
    "rotation_strategy": "performance-based",
    "timeout": 30,
    "max_retries": 3,
    "strategy_config": {
      "ema_alpha": 0.3
    }
  }
}
```

#### Strategy-Specific Request Context

Some strategies support request-specific context via headers:

**Session Persistence:**
```bash
curl -X POST http://localhost:8000/api/v1/request \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: user-123" \
  -d '{
    "url": "https://example.com/login",
    "method": "POST"
  }'
```

**Geo-Targeting:**
```bash
curl -X POST http://localhost:8000/api/v1/request \
  -H "Content-Type: application/json" \
  -H "X-Target-Country: US" \
  -H "X-Target-Region: California" \
  -d '{
    "url": "https://us-content.com/data",
    "method": "GET"
  }'
```

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
    "headers": {"Content-Type": "application/json"},
    "body": "{\"result\": \"data\"}",
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
    "protocol": "http",
    "health": "healthy"
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
8. **Configure Trusted Proxies** to prevent IP spoofing (see below)

### X-Forwarded-For Security Warning

> **⚠️ CRITICAL SECURITY CONSIDERATION**
>
> When deploying ProxyWhirl behind a reverse proxy (Nginx, Caddy, HAProxy,
> cloud load balancers), the rate limiting feature uses the client IP address
> to track request counts. However, the `X-Forwarded-For` header can be
> spoofed by malicious clients to bypass rate limits.

**The Problem:**

1. Client sends request with forged `X-Forwarded-For: 1.2.3.4`
2. Reverse proxy appends real IP: `X-Forwarded-For: 1.2.3.4, 5.6.7.8`
3. If ProxyWhirl reads the first (leftmost) IP, rate limiting is bypassed

**The Solution:**

Your reverse proxy must be configured to:
1. **Clear or overwrite** untrusted `X-Forwarded-For` headers
2. **Set `X-Real-IP`** or `X-Forwarded-For` with only the client's real IP
3. **ProxyWhirl should only trust the rightmost IP** added by your proxy

**Best Practices:**

- Always deploy ProxyWhirl behind a reverse proxy in production
- Configure your proxy to set `X-Real-IP` to the actual client IP
- Never trust `X-Forwarded-For` values from untrusted sources
- Consider IP allowlisting for the `/api/v1/config` endpoints

## Deployment Examples

### Nginx Reverse Proxy (Secure Configuration)

```nginx
server {
    listen 80;
    server_name api.example.com;

    # Security: Clear any client-provided X-Forwarded-For
    # and set X-Real-IP to the actual connecting IP
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;

        # Critical: Use $remote_addr which cannot be spoofed
        proxy_set_header X-Real-IP $remote_addr;

        # For multi-proxy chains, use realip module to get true client IP
        # set_real_ip_from 10.0.0.0/8;  # Trust internal proxy network
        # real_ip_header X-Forwarded-For;
        # real_ip_recursive on;

        # Set clean X-Forwarded-For from trusted source only
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Note:** The above configuration overwrites `X-Forwarded-For` with `$remote_addr`,
which is the IP address of the connecting client (cannot be spoofed). This is the
safest approach for single-proxy deployments.

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

### Caddy Reverse Proxy (Secure Configuration)

```caddy
api.example.com {
    # Modern, secure defaults with X-Forwarded-For protection
    reverse_proxy localhost:8000 {
        # Replace X-Forwarded-For with real client IP
        header_up -X-Forwarded-For
        header_up X-Forwarded-For {http.request.remote.host}

        # Set X-Real-IP to the actual client IP
        header_up X-Real-IP {http.request.remote.host}

        # Preserve other forwarded headers
        header_up X-Forwarded-Proto {http.request.proto}
        header_up X-Forwarded-Host {http.request.host}

        # Enable compression for performance
        header_up Connection "Upgrade"
        header_up Upgrade "websocket"
    }
}
```

**Note:** Caddy automatically removes untrusted `X-Forwarded-For` headers from clients,
making it a secure choice for production deployments.

### HAProxy Reverse Proxy (Secure Configuration)

```haproxy
global
    log stdout local0
    maxconn 4096

defaults
    log global
    mode http
    timeout connect 5s
    timeout client 50s
    timeout server 50s

frontend api_frontend
    bind 0.0.0.0:80
    default_backend api_backend

    # Log original client IP
    option forwardfor except 127.0.0.0/8

    # Security: Normalize headers to prevent spoofing
    http-request set-header X-Forwarded-For %[src]
    http-request set-header X-Real-IP %[src]
    http-request set-header X-Forwarded-Proto http

backend api_backend
    balance roundrobin
    server api1 localhost:8000 check

    # Preserve original client IP in logs
    option forwardfor

    # Additional security headers
    http-response set-header Strict-Transport-Security "max-age=31536000; includeSubDomains"
```

**Note:** HAProxy's `option forwardfor` overwrites `X-Forwarded-For` with the real
client IP (`%[src]`), preventing spoofing attacks.

### AWS Application Load Balancer (ALB) Security

When deploying ProxyWhirl behind AWS ALB:

1. **Enable "Preserve client IP" option** in ALB target group attributes
2. **Configure ALB to add `X-Forwarded-For`** (enabled by default)
3. **Trust only ALB's IP range** in ProxyWhirl's IP extraction logic

**AWS ALB Headers:**
```
X-Forwarded-For: <real-client-ip>  (ALB appends here)
X-Forwarded-Proto: https
X-Forwarded-Port: 443
```

**Configuration:**
```bash
# Only trust requests from ALB security group
export PROXYWHIRL_TRUSTED_PROXIES="10.0.0.0/8"

# Or use ALB-specific header
export PROXYWHIRL_CLIENT_IP_HEADER="X-Forwarded-For"
```

## X-Forwarded-For Security Checklist

Before deploying to production, verify:

- [ ] Reverse proxy **clears client-provided `X-Forwarded-For`** headers
- [ ] Reverse proxy **sets `X-Real-IP` or `X-Forwarded-For`** with real client IP
- [ ] ProxyWhirl **trusts only the rightmost IP** in the header chain
- [ ] **IP allowlisting** is configured for sensitive endpoints (`/api/v1/config`)
- [ ] **Rate limiting** is tested to ensure it works correctly
- [ ] **Access logs** verify correct client IP attribution
- [ ] **No direct internet exposure** of ProxyWhirl (always use reverse proxy)

## Security References

For additional information on HTTP header security and IP validation:

- **OWASP HTTP Response Splitting:** https://owasp.org/www-community/attacks/HTTP_Response_Splitting
- **OWASP Proxy Security:** https://owasp.org/www-community/attacks/Manipulating_User-Controlled_Variables
- **RFC 7239 - Forwarded HTTP Extension:** https://tools.ietf.org/html/rfc7239
- **IETF X-Forwarded-For:** https://tools.ietf.org/html/draft-ietf-httpbis-forwarded

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
- Documentation: See `README.md` and `docs/`
- Examples: See `examples/` directory
