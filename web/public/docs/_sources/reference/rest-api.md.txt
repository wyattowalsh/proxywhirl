---
title: REST API Usage
---

# ProxyWhirl REST API Usage Guide

Complete guide for using the ProxyWhirl REST API.

:::{seealso}
For deployment and security best practices, see [Deployment Security](../guides/deployment-security.md). For Python API usage, see [Python API](python-api.md).
:::

## Table of Contents

- [Getting Started](#getting-started)
- [Authentication](#authentication)
- [Middleware](#middleware)
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

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PROXYWHIRL_REQUIRE_AUTH` | `false` | Enable API key authentication |
| `PROXYWHIRL_API_KEY` | -- | API key for authentication |
| `PROXYWHIRL_STRATEGY` | `round-robin` | Default rotation strategy |
| `PROXYWHIRL_TIMEOUT` | `30` | Default request timeout (seconds) |
| `PROXYWHIRL_MAX_RETRIES` | `3` | Default max retry attempts |
| `PROXYWHIRL_CORS_ORIGINS` | (empty) | Comma-separated CORS origins |
| `PROXYWHIRL_STORAGE_PATH` | -- | SQLite database path for persistence |
| `PROXYWHIRL_RATE_LIMIT` | `100/minute` | Default rate limit for all endpoints |
| `PROXYWHIRL_API_KEY_RATE_LIMIT` | (same as rate limit) | Per-API-key rate limit |
| `PROXYWHIRL_AUDIT_LOG` | `true` | Enable structured audit logging |

## Authentication

### No Authentication (Default)

By default, the API is open and requires no authentication:

```bash
curl http://localhost:8000/api/v1/health
```

### API Key Authentication

:::{seealso}
For all environment variables and TOML configuration options, see [Configuration](configuration.md).
:::

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

## Middleware

The API applies the following middleware to all requests (in order of execution):

1. **Audit Logging Middleware** -- Structured audit logging for write/admin operations on `/api/` paths. Controlled by the `PROXYWHIRL_AUDIT_LOG` environment variable (default: `true`). Redacts sensitive fields (passwords, tokens, API keys) in request bodies.

2. **Request ID Middleware** -- Adds an `X-Request-ID` header to every response for request tracing. If the client sends an `X-Request-ID` header, that value is used; otherwise a new UUID v4 is generated.

3. **Security Headers Middleware** -- Adds security headers to all responses:
   - `X-Content-Type-Options: nosniff`
   - `X-Frame-Options: DENY`
   - `X-XSS-Protection: 1; mode=block`
   - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
   - `Content-Security-Policy: default-src 'self'; frame-ancestors 'none'`
   - `Referrer-Policy: strict-origin-when-cross-origin`
   - `Permissions-Policy: geolocation=(), microphone=(), camera=()`

4. **Request Logging Middleware** -- Logs all HTTP requests with method, path, client IP, duration, and status code.

5. **CORS Middleware** -- Configured via `PROXYWHIRL_CORS_ORIGINS`. Wildcard origin (`*`) with `allow_credentials=True` raises a startup error (security protection).

6. **SSRF Protection** -- `POST /api/v1/request` validates all target URLs to block localhost, private IPs, link-local addresses, internal domain names, and non-HTTP schemes.

## Endpoint Reference

### Quick Endpoint Summary

| Method | Path | Description | Rate Limit |
|--------|------|-------------|------------|
| {bdg-success}`POST` | `/api/v1/request` | Make proxied HTTP request | 50/min |
| {bdg-primary}`GET` | `/api/v1/proxies` | List all proxies (paginated) | 100/min |
| {bdg-success}`POST` | `/api/v1/proxies` | Add proxy to pool | 10/min |
| {bdg-primary}`GET` | `/api/v1/proxies/{id}` | Get proxy details | 100/min |
| {bdg-danger}`DELETE` | `/api/v1/proxies/{id}` | Remove proxy from pool | 100/min |
| {bdg-success}`POST` | `/api/v1/proxies/health-check` | Run health check on proxies | 100/min |
| {bdg-success}`POST` | `/api/v1/proxies/test` | Health check (deprecated) | 100/min |
| {bdg-primary}`GET` | `/api/v1/health` | Health check for load balancers | 100/min |
| {bdg-primary}`GET` | `/api/v1/ready` | Readiness probe (Kubernetes) | 100/min |
| {bdg-primary}`GET` | `/api/v1/status` | Detailed pool status | 100/min |
| {bdg-primary}`GET` | `/api/v1/stats` | Performance statistics (JSON) | 100/min |
| {bdg-primary}`GET` | `/api/v1/config` | Get current configuration | 100/min |
| {bdg-warning}`PUT` | `/api/v1/config` | Update configuration | 5/min |
| {bdg-primary}`GET` | `/api/v1/circuit-breakers` | List circuit breaker states | 100/min |
| {bdg-primary}`GET` | `/api/v1/circuit-breakers/metrics` | Circuit breaker event history | 100/min |
| {bdg-primary}`GET` | `/api/v1/circuit-breakers/{id}` | Get circuit breaker for proxy | 100/min |
| {bdg-success}`POST` | `/api/v1/circuit-breakers/{id}/reset` | Reset circuit breaker | 10/min |
| {bdg-primary}`GET` | `/api/v1/retry/policy` | Get retry policy | 100/min |
| {bdg-warning}`PUT` | `/api/v1/retry/policy` | Update retry policy | 100/min |
| {bdg-primary}`GET` | `/api/v1/metrics/retries` | Retry metrics summary | 100/min |
| {bdg-primary}`GET` | `/api/v1/metrics/retries/timeseries` | Retry metrics time-series | 100/min |
| {bdg-primary}`GET` | `/api/v1/metrics/retries/by-proxy` | Retry metrics by proxy | 100/min |
| {bdg-primary}`GET` | `/metrics` | Prometheus metrics (text) | None |
| {bdg-primary}`GET` | `/metrics/retry` | Retry statistics (JSON/Prometheus) | 100/min |
| {bdg-primary}`GET` | `/metrics/circuit-breaker` | Circuit breaker metrics | 100/min |

### Rotation Strategy Configuration

#### Understanding Rotation Strategies

The API supports 4 rotation strategies that can be configured at runtime via `PUT /api/v1/config`:

| Strategy | Use Case | Key Feature |
|----------|----------|-------------|
| `round-robin` | Fair distribution | Perfect load balance |
| `random` | Unpredictable patterns | Uniform distribution |
| `weighted` | Prefer best proxies | Success-rate based |
| `least-used` | Even load balance | Tracks request counts |

:::{note}
The full library supports additional strategies (performance-based, session-persistence, geo-targeted), but the REST API config endpoint only accepts the 4 strategies listed above.
:::

#### GET /api/v1/config

Get current configuration:

```bash
curl http://localhost:8000/api/v1/config
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "rotation_strategy": "round-robin",
    "timeout": 30,
    "max_retries": 3,
    "rate_limits": {
      "default_limit": 100,
      "request_endpoint_limit": 50
    },
    "auth_enabled": false,
    "cors_origins": ["*"]
  },
  "error": null,
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-01-01T12:00:00Z",
    "version": "1.0.0"
  }
}
```

#### PUT /api/v1/config

Update configuration at runtime. All fields are optional (partial updates supported).

**Rate limit:** 5 requests/minute.

```bash
curl -X PUT http://localhost:8000/api/v1/config \
  -H "Content-Type: application/json" \
  -d '{
    "rotation_strategy": "weighted"
  }'
```

**Accepted fields:**

| Field | Type | Description |
|-------|------|-------------|
| `rotation_strategy` | string | One of: `round-robin`, `random`, `weighted`, `least-used` |
| `timeout` | int (1-300) | Request timeout in seconds |
| `max_retries` | int (1-10) | Maximum retry attempts |
| `rate_limits` | object | `{default_limit: int, request_endpoint_limit: int}` |
| `cors_origins` | list[string] | CORS allowed origins |

**Response:** `APIResponse[ConfigurationSettings]` envelope:
```json
{
  "status": "success",
  "data": {
    "rotation_strategy": "weighted",
    "timeout": 30,
    "max_retries": 3,
    "rate_limits": {
      "default_limit": 100,
      "request_endpoint_limit": 50
    },
    "auth_enabled": false,
    "cors_origins": ["*"]
  },
  "error": null,
  "meta": {
    "request_id": "...",
    "timestamp": "...",
    "version": "1.0.0"
  }
}
```

**Errors:**
- HTTP 400 if invalid values (e.g., unknown strategy)

### Proxied Requests

#### POST /api/v1/request

Make HTTP requests through rotating proxies. SSRF protection validates all target URLs.

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
    "proxy_used": "http://proxy.example.com:8080",
    "elapsed_ms": 245
  },
  "meta": {
    "timestamp": "2025-01-01T12:00:00Z",
    "request_id": "req-abc123"
  }
}
```

:::{note}
The `proxy_used` field is a string (the proxy URL), not an object.
:::

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
- `page_size` (int, default 50, max 100): Items per page
- `status_filter` (str, optional): Filter by status -- `healthy`, `unhealthy`, or `active`

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
          "avg_latency_ms": 250
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

**Rate limit:** 10 requests/minute.

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
    "status": "active",
    "health": "healthy",
    "stats": {
      "total_requests": 100,
      "successful_requests": 95,
      "failed_requests": 5,
      "avg_latency_ms": 250
    },
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T12:00:00Z"
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

#### POST /api/v1/proxies/health-check

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

#### POST /api/v1/proxies/test

:::{deprecated} 1.0.0
Use `POST /api/v1/proxies/health-check` instead. This endpoint is kept for backward compatibility and will be removed in a future version.
:::

Same request/response format as `/api/v1/proxies/health-check`.

### Monitoring

#### GET /metrics

Prometheus metrics endpoint (text format). Returns metrics for monitoring:

- `proxywhirl_requests_total` -- Total HTTP requests by endpoint, method, and status
- `proxywhirl_request_duration_seconds` -- Request duration histogram
- `proxywhirl_proxies_total` -- Total proxies in pool
- `proxywhirl_proxies_healthy` -- Number of healthy proxies
- `proxywhirl_circuit_breaker_state` -- Circuit breaker states (0=closed, 1=open, 2=half-open)

```bash
curl http://localhost:8000/metrics
```

**Response:** Prometheus text format (`text/plain; version=0.0.4`)

:::{note}
This endpoint is at `/metrics` (not `/api/v1/metrics`). It is not included in the OpenAPI schema but is always available.
:::

#### GET /metrics/retry

Retry statistics with optional Prometheus format.

**Query Parameters:**
- `format` (str, optional): `"prometheus"` for Prometheus text format (default: JSON)
- `hours` (int, default 24): Hours of data to include

**Response (JSON):**
```json
{
  "status": "success",
  "data": {
    "summary": {
      "total_retries": 1250,
      "success_by_attempt": {"0": 850, "1": 300, "2": 80, "3": 20},
      "circuit_breaker_events_count": 15,
      "retention_hours": 24
    },
    "timeseries": [
      {
        "timestamp": "2025-01-01T12:00:00Z",
        "total_requests": 1000,
        "total_retries": 150,
        "success_rate": 0.95,
        "avg_latency": 0.25
      }
    ],
    "by_proxy": {
      "proxy1:8080": {
        "proxy_id": "proxy1:8080",
        "total_attempts": 500,
        "success_count": 450,
        "failure_count": 50,
        "avg_latency": 0.3,
        "circuit_breaker_opens": 2
      }
    }
  }
}
```

#### GET /metrics/circuit-breaker

Circuit breaker metrics with optional Prometheus format.

**Query Parameters:**
- `format` (str, optional): `"prometheus"` for Prometheus text format (default: JSON)
- `hours` (int, default 24): Hours of event history to include

**Response (JSON):**
```json
{
  "status": "success",
  "data": {
    "states": [
      {
        "proxy_id": "proxy-123",
        "state": "closed",
        "failure_count": 2,
        "failure_threshold": 5,
        "window_duration": 60.0,
        "timeout_duration": 30.0,
        "next_test_time": null,
        "last_state_change": "2025-01-01T12:00:00Z"
      }
    ],
    "events": [],
    "total_events": 0,
    "hours": 24
  }
}
```

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

#### GET /api/v1/stats

Performance statistics for monitoring. Returns a `MetricsResponse` with aggregate and per-proxy stats.

**Response:**
```json
{
  "status": "success",
  "data": {
    "requests_total": 1000,
    "requests_per_second": 5.5,
    "avg_latency_ms": 250.0,
    "error_rate": 0.05,
    "proxy_stats": [
      {
        "proxy_id": "proxy-123",
        "requests": 100,
        "successes": 95,
        "failures": 5,
        "avg_latency_ms": 245
      }
    ]
  }
}
```

### Configuration

See [Rotation Strategy Configuration](#rotation-strategy-configuration) above for `GET /api/v1/config` and `PUT /api/v1/config` details.

### Circuit Breakers

#### GET /api/v1/circuit-breakers

List all circuit breaker states.

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "proxy_id": "proxy1.example.com:8080",
      "state": "closed",
      "failure_count": 2,
      "failure_threshold": 5,
      "window_duration": 60.0,
      "timeout_duration": 30.0,
      "next_test_time": null,
      "last_state_change": "2025-01-01T12:00:00Z"
    }
  ]
}
```

:::{note}
The `data` field is a **list** of circuit breaker states, not a dict.
:::

#### GET /api/v1/circuit-breakers/metrics

Get circuit breaker event history (state change events).

**Query Parameters:**
- `hours` (int, default 24): Hours of event history to include

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "proxy_id": "proxy1.example.com:8080",
      "from_state": "closed",
      "to_state": "open",
      "timestamp": "2025-01-01T12:00:00Z",
      "failure_count": 5
    }
  ]
}
```

#### GET /api/v1/circuit-breakers/{proxy_id}

Get circuit breaker state for a specific proxy.

**Errors:**
- HTTP 404 if circuit breaker not found for the given proxy

#### POST /api/v1/circuit-breakers/{proxy_id}/reset

Manually reset a circuit breaker to CLOSED state.

**Rate limit:** 10 requests/minute.

**Errors:**
- HTTP 404 if circuit breaker not found for the given proxy

:::{seealso}
For circuit breaker concepts and configuration, see [Retry & Failover](../guides/retry-failover.md).
:::

### Retry & Failover

#### GET /api/v1/retry/policy

Get current retry policy configuration.

#### PUT /api/v1/retry/policy

Update retry policy at runtime.

#### GET /api/v1/metrics/retries

Get retry metrics summary.

#### GET /api/v1/metrics/retries/timeseries

Get retry metrics as time-series data.

**Query Parameters:**
- `hours` (int, default 24): Number of hours to retrieve

#### GET /api/v1/metrics/retries/by-proxy

Get retry metrics broken down by proxy.

**Query Parameters:**
- `hours` (int, default 24): Number of hours to analyze

## Rate Limiting

The API includes built-in rate limiting per IP address (or per API key for authenticated requests):

| Endpoint | Limit |
|----------|-------|
| Default | 100 requests/minute |
| POST /api/v1/request | 50 requests/minute |
| POST /api/v1/proxies | 10 requests/minute |
| PUT /api/v1/config | 5 requests/minute |
| POST /api/v1/circuit-breakers/{id}/reset | 10 requests/minute |

The default rate limit can be overridden with the `PROXYWHIRL_RATE_LIMIT` environment variable (e.g., `200/minute`). The per-API-key limit can be set separately with `PROXYWHIRL_API_KEY_RATE_LIMIT`.

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
    "details": null,
    "timestamp": "2025-01-01T12:00:00Z"
  },
  "meta": {
    "timestamp": "2025-01-01T12:00:00Z",
    "request_id": "req-abc123",
    "version": "1.0.0"
  }
}
```

### Error Codes

**Validation Errors (4xx):**
- `VALIDATION_ERROR`: Invalid request parameters
- `INVALID_URL`: Invalid URL format
- `INVALID_PROXY_FORMAT`: Malformed proxy URL
- `INVALID_METHOD`: Unsupported HTTP method
- `INVALID_TIMEOUT`: Timeout value out of range

**Proxy Errors:**
- `PROXY_POOL_EMPTY` (503): No proxies configured
- `PROXY_FAILOVER_EXHAUSTED` (502): All proxies failed
- `PROXY_NOT_FOUND` (404): Proxy ID not found
- `PROXY_ALREADY_EXISTS` (409): Duplicate proxy URL
- `PROXY_ERROR` (502): General proxy error

**Target/Request Errors:**
- `TARGET_UNREACHABLE` (504): Cannot reach target server
- `REQUEST_TIMEOUT` (504): Request exceeded timeout
- `REQUEST_FAILED` (502): Request failed for other reasons

**Configuration Errors:**
- `CONFIGURATION_ERROR`: General configuration error
- `INVALID_CONFIGURATION`: Invalid configuration values

**System Errors:**
- `INTERNAL_ERROR` (500): Internal server error
- `SERVICE_UNAVAILABLE` (503): Service not ready

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
watch -n 60 'curl -s http://localhost:8000/api/v1/stats | jq .data.error_rate'
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

> **CRITICAL SECURITY CONSIDERATION**
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

```text
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

```text
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
- **OWASP Web Security Testing Guide:** https://owasp.org/www-project-web-security-testing-guide/
- **RFC 7239 - Forwarded HTTP Extension:** https://datatracker.ietf.org/doc/html/rfc7239
- **MDN X-Forwarded-For:** https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Forwarded-For

## Troubleshooting

### API Won't Start

Check logs for errors:
```bash
uv run uvicorn proxywhirl.api:app --log-level debug
```

### Proxies Not Working

1. Check proxy pool: `GET /api/v1/proxies`
2. Run health check: `POST /api/v1/proxies/health-check`
3. Check stats: `GET /api/v1/stats`

### Rate Limiting Issues

Adjust limits via environment variable:
```bash
export PROXYWHIRL_RATE_LIMIT="200/minute"
```

Or update request endpoint limit via configuration:
```bash
curl -X PUT http://localhost:8000/api/v1/config \
  -H "Content-Type: application/json" \
  -d '{"rate_limits": {"request_endpoint_limit": 100}}'
```

### High Latency

- Check proxy quality with stats endpoint
- Reduce timeout values
- Switch to faster rotation strategy (least-used)
- Remove slow proxies from pool

## See Also

- [Python API](python-api.md) -- Python API reference (ProxyRotator, AsyncProxyRotator)
- [Configuration](configuration.md) -- Configuration options and environment variables
- [Exceptions](exceptions.md) -- Exception types and error codes
- [Rate Limiting API](rate-limiting-api.md) -- Rate limiting API reference
- [Deployment Security](../guides/deployment-security.md) -- Production deployment and security
- [CLI Reference](../guides/cli-reference.md) -- CLI commands reference

## Support

For issues and questions:
- GitHub Issues: https://github.com/wyattowalsh/proxywhirl/issues
- Documentation: See `README.md` and `docs/`
- Examples: See `examples/` directory
