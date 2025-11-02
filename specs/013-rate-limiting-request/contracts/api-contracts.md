# API Contracts: Rate Limiting for Request Management

**Date**: 2025-11-02  
**Feature**: 013-rate-limiting-request  
**Purpose**: Define HTTP API contracts for rate limiting integration

## Overview

Rate limiting is enforced transparently via FastAPI middleware. The following contracts define:
1. HTTP headers added to all API responses
2. HTTP 429 error response format
3. Configuration management endpoints (optional, for US4 monitoring)

---

## HTTP Headers (All Endpoints)

### Rate Limit Headers

Added to **all** API responses (2xx, 4xx, 5xx) when rate limiting is enabled, including non-rate-limiting errors (e.g., 401 Unauthorized, 403 Forbidden, 500 Internal Server Error). This provides clients with rate limit status even when requests fail for other reasons.

**Headers**:

| Header | Type | Description | Example |
|--------|------|-------------|---------|
| `X-RateLimit-Limit` | Integer | Maximum requests allowed in window | `100` |
| `X-RateLimit-Remaining` | Integer | Remaining requests in current window | `42` |
| `X-RateLimit-Reset` | Integer (Unix timestamp) | When rate limit resets (UTC) | `1698825660` |
| `X-RateLimit-Tier` | String | User's rate limit tier | `free` |

**Example Response** (200 OK):
```http
HTTP/1.1 200 OK
Content-Type: application/json
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 42
X-RateLimit-Reset: 1698825660
X-RateLimit-Tier: free

{
  "status": "success",
  "data": { ... }
}
```

**Source**: FR-009

---

## HTTP 429 Too Many Requests

### Response Format

Returned when rate limit is exceeded.

**Status Code**: `429 Too Many Requests`

**Headers**:

| Header | Type | Description | Example |
|--------|------|-------------|---------|
| `X-RateLimit-Limit` | Integer | Maximum requests allowed in window | `100` |
| `X-RateLimit-Remaining` | Integer | Always `0` for 429 responses | `0` |
| `X-RateLimit-Reset` | Integer (Unix timestamp) | When rate limit resets | `1698825660` |
| `X-RateLimit-Tier` | String | User's rate limit tier | `free` |
| `Retry-After` | Integer (seconds) | Seconds until rate limit resets | `59` |

**Response Body**:
```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Please retry after 59 seconds.",
    "details": {
      "limit": 100,
      "window_size": 60,
      "reset_at": "2025-11-02T10:01:00Z",
      "retry_after_seconds": 59,
      "tier": "free",
      "endpoint": "/api/v1/request"
    }
  }
}
```

**Example**:
```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1698825660
X-RateLimit-Tier: free
Retry-After: 59

{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Please retry after 59 seconds.",
    "details": {
      "limit": 100,
      "window_size": 60,
      "reset_at": "2025-11-02T10:01:00Z",
      "retry_after_seconds": 59,
      "tier": "free",
      "endpoint": "/api/v1/request"
    }
  }
}
```

**Source**: FR-002, FR-003

---

## Configuration Endpoints (Optional - US4)

### GET /api/v1/rate-limit/config

Retrieve current rate limit configuration.

**Authentication**: Required (admin only)

**Admin Authentication Method**: API key with `admin` role or JWT token with `admin` scope. Admin credentials configured via `PROXYWHIRL_ADMIN_API_KEY` environment variable. This reuses the existing authentication system from 003-rest-api.

**Request**:
```http
GET /api/v1/rate-limit/config HTTP/1.1
X-API-Key: admin-key-here
```

**Response** (200 OK):
```json
{
  "enabled": true,
  "default_tier": "free",
  "tiers": [
    {
      "name": "free",
      "requests_per_window": 100,
      "window_size_seconds": 60,
      "endpoints": {
        "/api/v1/request": 50
      },
      "description": "Free tier with limited access"
    },
    {
      "name": "premium",
      "requests_per_window": 1000,
      "window_size_seconds": 60,
      "endpoints": {},
      "description": "Premium tier with increased limits"
    }
  ],
  "redis_enabled": true,
  "fail_open": false,
  "whitelist": ["550e8400-e29b-41d4-a716-446655440000"]
}
```

**Error Response** (401 Unauthorized):
```json
{
  "error": {
    "code": "unauthorized",
    "message": "Admin authentication required"
  }
}
```

**Source**: FR-014 (config inspection)

---

### PUT /api/v1/rate-limit/config

Update rate limit configuration (hot reload).

**Authentication**: Required (admin only)

**Request**:
```http
PUT /api/v1/rate-limit/config HTTP/1.1
Content-Type: application/json
X-API-Key: admin-key-here

{
  "enabled": true,
  "default_tier": "free",
  "tiers": [
    {
      "name": "free",
      "requests_per_window": 150,
      "window_size_seconds": 60,
      "endpoints": {
        "/api/v1/request": 75
      },
      "description": "Updated free tier limits"
    }
  ]
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "message": "Rate limit configuration updated",
  "applied_at": "2025-11-02T10:05:00Z"
}
```

**Error Response** (400 Bad Request):
```json
{
  "error": {
    "code": "validation_error",
    "message": "Invalid configuration",
    "details": {
      "field": "tiers[0].requests_per_window",
      "error": "Must be positive integer"
    }
  }
}
```

**Source**: FR-014 (runtime config updates)

---

### GET /api/v1/rate-limit/metrics

Retrieve rate limiting metrics.

**Authentication**: Optional (public endpoint)

**Request**:
```http
GET /api/v1/rate-limit/metrics HTTP/1.1
```

**Response** (200 OK):
```json
{
  "total_requests": 15420,
  "throttled_requests": 892,
  "allowed_requests": 14528,
  "throttle_rate": 0.0578,
  "by_tier": {
    "free": 450,
    "premium": 342,
    "enterprise": 100
  },
  "by_endpoint": {
    "/api/v1/request": 720,
    "/api/v1/pool": 172
  },
  "avg_check_latency_ms": 2.3,
  "p95_check_latency_ms": 4.8,
  "redis_errors": 0,
  "timestamp": "2025-11-02T10:05:00Z"
}
```

**Source**: FR-012, SC-007 (metrics exposition)

---

### GET /api/v1/rate-limit/status/{identifier}

Check rate limit status for a specific user or IP.

**Authentication**: Required (admin only, or self-query)

**Path Parameters**:
- `identifier` (string): User ID (UUID) or IP address

**Request**:
```http
GET /api/v1/rate-limit/status/550e8400-e29b-41d4-a716-446655440000 HTTP/1.1
X-API-Key: user-key-here
```

**Response** (200 OK):
```json
{
  "identifier": "550e8400-e29b-41d4-a716-446655440000",
  "tier": "free",
  "limits": [
    {
      "endpoint": "/api/v1/request",
      "limit": 50,
      "current_count": 23,
      "remaining": 27,
      "reset_at": "2025-11-02T10:06:00Z",
      "window_size_seconds": 60
    },
    {
      "endpoint": "/api/v1/health",
      "limit": 100,
      "current_count": 5,
      "remaining": 95,
      "reset_at": "2025-11-02T10:06:00Z",
      "window_size_seconds": 60
    }
  ],
  "is_whitelisted": false
}
```

**Error Response** (404 Not Found):
```json
{
  "error": {
    "code": "not_found",
    "message": "No rate limit state found for identifier"
  }
}
```

**Source**: US4 (monitoring user-specific limits)

---

## Middleware Integration Contract

### Request Processing Flow

```
1. Request arrives → FastAPI
2. Authentication middleware (existing 003-rest-api)
3. Rate Limit Middleware (NEW)
   ├─ Extract identifier (user ID or IP)
   ├─ Determine tier
   ├─ Check rate limit (Redis/in-memory)
   ├─ If exceeded: Return 429
   └─ If allowed: Add headers, continue
4. Route handler
5. Response returned
```

### Middleware Configuration

**Integration Point**: `proxywhirl/api.py`

```python
from proxywhirl.rate_limit_middleware import RateLimitMiddleware

app = FastAPI(...)

# Add rate limit middleware
app.add_middleware(
    RateLimitMiddleware,
    config=rate_limit_config  # RateLimitConfig instance
)
```

### Identifier Extraction Order

1. **Authenticated User**: Extract user ID from JWT token or API key
2. **Unauthenticated**: Extract IP address from:
   - `X-Forwarded-For` header (if behind proxy)
   - `X-Real-IP` header (if behind Nginx)
   - `request.client.host` (direct connection)

### Whitelist Bypass

If identifier in `config.whitelist`, skip rate limiting entirely (no headers added, no Redis check).

**Source**: FR-015

---

## OpenAPI Schema Extension

### Rate Limit Headers Schema

All endpoints in OpenAPI spec should document rate limit headers:

```yaml
components:
  headers:
    X-RateLimit-Limit:
      description: Maximum requests allowed in window
      schema:
        type: integer
        example: 100
    X-RateLimit-Remaining:
      description: Remaining requests in current window
      schema:
        type: integer
        example: 42
    X-RateLimit-Reset:
      description: Unix timestamp when rate limit resets (UTC)
      schema:
        type: integer
        example: 1698825660
    X-RateLimit-Tier:
      description: User's rate limit tier
      schema:
        type: string
        enum: [free, premium, enterprise, unlimited]
        example: free

  responses:
    RateLimitExceeded:
      description: Rate limit exceeded
      headers:
        X-RateLimit-Limit:
          $ref: '#/components/headers/X-RateLimit-Limit'
        X-RateLimit-Remaining:
          $ref: '#/components/headers/X-RateLimit-Remaining'
        X-RateLimit-Reset:
          $ref: '#/components/headers/X-RateLimit-Reset'
        X-RateLimit-Tier:
          $ref: '#/components/headers/X-RateLimit-Tier'
        Retry-After:
          description: Seconds until rate limit resets
          schema:
            type: integer
            example: 59
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/RateLimitError'

  schemas:
    RateLimitError:
      type: object
      required: [error]
      properties:
        error:
          type: object
          required: [code, message, details]
          properties:
            code:
              type: string
              enum: [rate_limit_exceeded]
            message:
              type: string
              example: "Rate limit exceeded. Please retry after 59 seconds."
            details:
              type: object
              properties:
                limit:
                  type: integer
                  example: 100
                window_size:
                  type: integer
                  example: 60
                reset_at:
                  type: string
                  format: date-time
                  example: "2025-11-02T10:01:00Z"
                retry_after_seconds:
                  type: integer
                  example: 59
                tier:
                  type: string
                  example: "free"
                endpoint:
                  type: string
                  example: "/api/v1/request"
```

### Example Endpoint with Rate Limiting

```yaml
paths:
  /api/v1/request:
    post:
      summary: Make proxied request
      responses:
        '200':
          description: Successful request
          headers:
            X-RateLimit-Limit:
              $ref: '#/components/headers/X-RateLimit-Limit'
            X-RateLimit-Remaining:
              $ref: '#/components/headers/X-RateLimit-Remaining'
            X-RateLimit-Reset:
              $ref: '#/components/headers/X-RateLimit-Reset'
            X-RateLimit-Tier:
              $ref: '#/components/headers/X-RateLimit-Tier'
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ProxyResponse'
        '429':
          $ref: '#/components/responses/RateLimitExceeded'
```

---

## Testing Contracts

### Contract Test Requirements

1. **Header Presence**: All responses must include `X-RateLimit-*` headers
2. **Header Values**: Values must match `RateLimitState` (limit, remaining, reset)
3. **429 Response**: Must include `Retry-After` header with correct value
4. **429 Body**: Must match schema with all required fields
5. **Configuration Endpoints**: Must validate Pydantic models
6. **Metrics Endpoint**: Must return valid `RateLimitMetrics` schema

### Example Contract Test (pytest)

```python
def test_rate_limit_headers_present(client):
    """All responses must include rate limit headers"""
    response = client.get("/api/v1/health")
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers
    assert "X-RateLimit-Tier" in response.headers

def test_429_response_format(client):
    """429 response must match contract"""
    # Make 101 requests to exceed limit (100 req/min)
    for _ in range(101):
        response = client.get("/api/v1/request")
    
    assert response.status_code == 429
    assert "Retry-After" in response.headers
    
    body = response.json()
    assert body["error"]["code"] == "rate_limit_exceeded"
    assert "retry_after_seconds" in body["error"]["details"]
    assert body["error"]["details"]["limit"] == 100
```

---

## Summary

**Contracts Defined**:
1. ✅ Rate limit headers (all responses)
2. ✅ HTTP 429 error format
3. ✅ Configuration management endpoints (GET/PUT)
4. ✅ Metrics endpoint (GET)
5. ✅ Status endpoint (GET)
6. ✅ OpenAPI schema extensions
7. ✅ Middleware integration contract
8. ✅ Contract test requirements

**Ready for Implementation**: All API contracts are fully specified and testable.
