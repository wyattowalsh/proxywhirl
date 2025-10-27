# API Contracts: REST API Endpoints

**Feature**: 003-rest-api  
**Date**: 2025-10-27  
**API Version**: v1  
**Base URL**: `http://localhost:8000/api/v1`

## Overview

This document defines all REST API endpoints, request/response formats, and HTTP status codes. The API follows RESTful principles with consistent envelope responses.

---

## Global Headers

### Request Headers

- `X-API-Key` (optional): API key for authentication (when auth enabled)
- `Content-Type`: `application/json` (for POST/PUT requests with body)
- `Accept`: `application/json` (optional, defaults to JSON)

### Response Headers

- `Content-Type`: `application/json`
- `X-RateLimit-Limit`: Max requests per window
- `X-RateLimit-Remaining`: Requests remaining in window
- `X-RateLimit-Reset`: Unix timestamp when limit resets
- `Retry-After`: Seconds to wait (only on 429 responses)

---

## Endpoints

### 1. Make Proxied Request

**POST** `/api/v1/request`

Make an HTTP request through a rotating proxy.

**Rate Limit**: 100 requests/minute per IP

**Request Body**:
```json
{
  "url": "https://httpbin.org/get",
  "method": "GET",
  "headers": {
    "User-Agent": "MyApp/1.0"
  },
  "body": null,
  "proxy": null,
  "retries": 3,
  "timeout": 30
}
```

**Success Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "status_code": 200,
    "headers": {
      "content-type": "application/json"
    },
    "body": "{\"origin\": \"1.2.3.4\"}",
    "proxy_used": "http://proxy1.example.com:8080",
    "response_time": 1.234,
    "attempts": 1
  },
  "meta": {
    "timestamp": "2025-10-27T10:30:00Z",
    "request_id": "req_abc123",
    "version": "v1"
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid URL or method
- `503 Service Unavailable`: No proxies available
- `500 Internal Server Error`: All proxies failed

---

### 2. List Proxies

**GET** `/api/v1/proxies`

List all proxies in the pool with health status.

**Rate Limit**: 100 requests/minute per IP

**Query Parameters**:
- `page` (int, optional): Page number (default: 1)
- `per_page` (int, optional): Items per page (default: 20, max: 100)
- `status` (string, optional): Filter by health status (HEALTHY, DEGRADED, UNHEALTHY, UNKNOWN)

**Example**: `GET /api/v1/proxies?page=1&per_page=20&status=HEALTHY`

**Success Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "url": "http://proxy1.example.com:8080",
        "username": "user123",
        "password_set": true,
        "health_status": "HEALTHY",
        "last_success_at": "2025-10-27T10:25:00Z",
        "last_failure_at": null,
        "consecutive_failures": 0,
        "total_requests": 1523,
        "avg_response_time": 0.856,
        "created_at": "2025-10-20T08:00:00Z"
      }
    ],
    "pagination": {
      "total": 100,
      "page": 1,
      "per_page": 20,
      "pages": 5
    }
  },
  "meta": {
    "timestamp": "2025-10-27T10:30:00Z",
    "request_id": "req_def456",
    "version": "v1"
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid pagination parameters

---

### 3. Add Proxy

**POST** `/api/v1/proxies`

Add a new proxy to the pool.

**Rate Limit**: 20 requests/minute per IP

**Request Body**:
```json
{
  "url": "http://proxy2.example.com:8080",
  "username": "user456",
  "password": "secret123",
  "validate": true
}
```

**Success Response** (201 Created):
```json
{
  "status": "success",
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "url": "http://proxy2.example.com:8080",
    "username": "user456",
    "password_set": true,
    "health_status": "HEALTHY",
    "last_success_at": "2025-10-27T10:30:00Z",
    "last_failure_at": null,
    "consecutive_failures": 0,
    "total_requests": 0,
    "avg_response_time": null,
    "created_at": "2025-10-27T10:30:00Z"
  },
  "meta": {
    "timestamp": "2025-10-27T10:30:00Z",
    "request_id": "req_ghi789",
    "version": "v1"
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid proxy URL or validation failed
- `409 Conflict`: Proxy already exists in pool

---

### 4. Get Proxy

**GET** `/api/v1/proxies/{proxy_id}`

Get details of a specific proxy.

**Rate Limit**: 100 requests/minute per IP

**Path Parameters**:
- `proxy_id` (UUID): Proxy identifier

**Success Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "url": "http://proxy1.example.com:8080",
    "username": "user123",
    "password_set": true,
    "health_status": "HEALTHY",
    "last_success_at": "2025-10-27T10:25:00Z",
    "last_failure_at": null,
    "consecutive_failures": 0,
    "total_requests": 1523,
    "avg_response_time": 0.856,
    "created_at": "2025-10-20T08:00:00Z"
  },
  "meta": {
    "timestamp": "2025-10-27T10:30:00Z",
    "request_id": "req_jkl012",
    "version": "v1"
  }
}
```

**Error Responses**:
- `404 Not Found`: Proxy ID not found

---

### 5. Delete Proxy

**DELETE** `/api/v1/proxies/{proxy_id}`

Remove a proxy from the pool.

**Rate Limit**: 20 requests/minute per IP

**Path Parameters**:
- `proxy_id` (UUID): Proxy identifier

**Success Response** (204 No Content): (empty body)

**Error Responses**:
- `404 Not Found`: Proxy ID not found

---

### 6. Test Proxies

**POST** `/api/v1/proxies/test`

Run health checks on all proxies (or specific proxies).

**Rate Limit**: 10 requests/minute per IP

**Request Body** (optional):
```json
{
  "proxy_ids": ["550e8400-e29b-41d4-a716-446655440000"]
}
```

**Success Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "results": [
      {
        "proxy_id": "550e8400-e29b-41d4-a716-446655440000",
        "healthy": true,
        "response_time": 0.234,
        "error": null,
        "checked_at": "2025-10-27T10:30:00Z"
      }
    ]
  },
  "meta": {
    "timestamp": "2025-10-27T10:30:00Z",
    "request_id": "req_mno345",
    "version": "v1"
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid proxy IDs

---

### 7. API Health Check

**GET** `/api/v1/health`

Check API health status (liveness probe).

**Rate Limit**: None (unrestricted)

**Success Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "healthy": true,
    "uptime_seconds": 86400,
    "version": "1.0.0"
  },
  "meta": {
    "timestamp": "2025-10-27T10:30:00Z",
    "request_id": "req_pqr678",
    "version": "v1"
  }
}
```

**Error Responses**:
- `503 Service Unavailable`: API is unhealthy

---

### 8. Readiness Check

**GET** `/api/v1/ready`

Check if API is ready to serve requests (readiness probe).

**Rate Limit**: None (unrestricted)

**Success Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "ready": true,
    "proxies_available": 10
  },
  "meta": {
    "timestamp": "2025-10-27T10:30:00Z",
    "request_id": "req_stu901",
    "version": "v1"
  }
}
```

**Error Responses**:
- `503 Service Unavailable`: No proxies available or API not ready

---

### 9. Pool Status

**GET** `/api/v1/status`

Get proxy pool statistics.

**Rate Limit**: 100 requests/minute per IP

**Success Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "total_proxies": 10,
    "healthy_proxies": 8,
    "degraded_proxies": 1,
    "unhealthy_proxies": 1,
    "unknown_proxies": 0,
    "avg_response_time": 0.765,
    "total_requests": 15234
  },
  "meta": {
    "timestamp": "2025-10-27T10:30:00Z",
    "request_id": "req_vwx234",
    "version": "v1"
  }
}
```

---

### 10. Get Configuration

**GET** `/api/v1/config`

Get current API and rotation configuration.

**Rate Limit**: 100 requests/minute per IP

**Success Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "rotation_strategy": "round_robin",
    "health_check_interval": 300,
    "timeout": 30,
    "max_retries": 3,
    "follow_redirects": true,
    "verify_ssl": true,
    "require_auth": false,
    "rate_limit": "100/minute"
  },
  "meta": {
    "timestamp": "2025-10-27T10:30:00Z",
    "request_id": "req_yza567",
    "version": "v1"
  }
}
```

---

### 11. Update Configuration

**PUT** `/api/v1/config`

Update API and rotation configuration.

**Rate Limit**: 10 requests/minute per IP

**Request Body** (partial updates allowed):
```json
{
  "rotation_strategy": "weighted",
  "timeout": 45
}
```

**Success Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "rotation_strategy": "weighted",
    "health_check_interval": 300,
    "timeout": 45,
    "max_retries": 3,
    "follow_redirects": true,
    "verify_ssl": true,
    "require_auth": false,
    "rate_limit": "100/minute"
  },
  "meta": {
    "timestamp": "2025-10-27T10:30:00Z",
    "request_id": "req_bcd890",
    "version": "v1"
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid configuration values

---

### 12. API Metrics (Optional)

**GET** `/api/v1/metrics`

Get API performance metrics (Prometheus format optional).

**Rate Limit**: 100 requests/minute per IP

**Query Parameters**:
- `format` (string, optional): Response format (json, prometheus)

**Success Response** (200 OK, JSON):
```json
{
  "status": "success",
  "data": {
    "requests_per_second": 12.5,
    "avg_latency_ms": 234.5,
    "p95_latency_ms": 567.8,
    "p99_latency_ms": 890.1,
    "error_rate": 0.02
  },
  "meta": {
    "timestamp": "2025-10-27T10:30:00Z",
    "request_id": "req_efg123",
    "version": "v1"
  }
}
```

---

## HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful GET/PUT requests |
| 201 | Created | Successful POST (resource creation) |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation errors, malformed JSON |
| 401 | Unauthorized | Missing or invalid API key |
| 404 | Not Found | Resource not found (proxy ID) |
| 409 | Conflict | Resource already exists |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected errors |
| 503 | Service Unavailable | No proxies available, API not ready |

---

## Error Response Format

All errors follow consistent format:

```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional context"
    }
  },
  "meta": {
    "timestamp": "2025-10-27T10:30:00Z",
    "request_id": "req_xyz789",
    "version": "v1"
  }
}
```

---

## Authentication

Optional API key authentication via `X-API-Key` header:

```http
X-API-Key: your-api-key-here
```

When authentication is enabled (`require_auth: true` in config):
- All endpoints except `/health` and `/ready` require valid API key
- Invalid/missing API key returns 401 Unauthorized
- API keys are stored encrypted using Fernet (Phase 2 encryption)

---

## Rate Limiting

Per-IP rate limiting with limits specified per endpoint:
- Header `X-RateLimit-Limit`: Max requests in window
- Header `X-RateLimit-Remaining`: Remaining requests
- Header `X-RateLimit-Reset`: Unix timestamp when limit resets
- On limit exceeded: 429 response with `Retry-After` header

---

## CORS

Configurable CORS support:
- Default: Disabled (same-origin only)
- Optional: Allow specific origins via configuration
- Supports credentials when configured

---

## OpenAPI Documentation

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

---

**Next Phase**: Generate quickstart guide and example client code
