# Data Model: REST API

**Feature**: 003-rest-api  
**Date**: 2025-10-27  
**Source**: Extracted from spec.md requirements

## Overview

The REST API data model defines the request/response structures for all HTTP endpoints. Models are implemented using Pydantic v2 for validation and automatic OpenAPI schema generation. The API uses a consistent envelope format for all responses.

## Core Entities

### 1. APIResponse[T] (Generic Envelope)

**Purpose**: Standardize all API responses with metadata

**Fields**:
- `status`: Literal["success", "error"] - Response status indicator
- `data`: Optional[T] - Payload (type varies by endpoint, None for errors)
- `error`: Optional[ErrorDetail] - Error information (None for success)
- `meta`: ResponseMetadata - Request metadata (timestamp, ID, version)

**Validation Rules**:
- Exactly one of `data` or `error` must be present
- `status` determines which field is populated
- `meta` is always present

**Example**:
```json
{
  "status": "success",
  "data": { "proxies": [...] },
  "meta": {
    "timestamp": "2025-10-27T10:30:00Z",
    "request_id": "req_abc123",
    "version": "v1"
  }
}
```

---

### 2. ErrorDetail

**Purpose**: Structured error information

**Fields**:
- `code`: str - Machine-readable error code (e.g., "PROXY_NOT_FOUND")
- `message`: str - Human-readable error message
- `details`: Optional[Dict[str, Any]] - Additional debug information

**Validation Rules**:
- `code` must be UPPERCASE_SNAKE_CASE
- `message` must be non-empty string
- `details` is optional and context-dependent

**Error Codes**:
- `PROXY_NOT_FOUND`: Proxy ID doesn't exist
- `INVALID_PROXY_URL`: URL validation failed
- `NO_PROXIES_AVAILABLE`: Pool is empty
- `PROXY_VALIDATION_FAILED`: Health check failed
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INVALID_API_KEY`: Authentication failed
- `INVALID_REQUEST`: Request body validation failed
- `INTERNAL_ERROR`: Unexpected server error

**Example**:
```json
{
  "code": "PROXY_NOT_FOUND",
  "message": "Proxy with ID 'abc123' not found in pool",
  "details": {
    "proxy_id": "abc123",
    "pool_size": 10
  }
}
```

---

### 3. ResponseMetadata

**Purpose**: Request tracking and versioning

**Fields**:
- `timestamp`: datetime - ISO 8601 formatted response time
- `request_id`: str - Unique request identifier (for tracing)
- `version`: str - API version (e.g., "v1")

**Validation Rules**:
- `timestamp` auto-generated on response creation
- `request_id` format: `req_{uuid4}`
- `version` matches URL path version

---

### 4. ProxiedRequest

**Purpose**: Request to make HTTP call through proxy

**Fields**:
- `url`: HttpUrl - Target URL to fetch (Pydantic validation)
- `method`: str = "GET" - HTTP method (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS)
- `headers`: Optional[Dict[str, str]] - Custom headers to include
- `body`: Optional[str] - Request body (for POST/PUT/PATCH)
- `proxy`: Optional[str] - Override rotation with specific proxy URL
- `retries`: int = 3 - Number of retry attempts on failure
- `timeout`: int = 30 - Request timeout in seconds

**Validation Rules**:
- `url` must be valid HTTP/HTTPS URL
- `method` must be in allowed list
- `headers` keys/values must be strings
- `retries` must be 0-10
- `timeout` must be 1-300 seconds

**Example**:
```json
{
  "url": "https://httpbin.org/get",
  "method": "GET",
  "headers": {
    "User-Agent": "ProxyWhirl/1.0"
  },
  "retries": 3,
  "timeout": 30
}
```

---

### 5. ProxiedResponse

**Purpose**: Result of proxied HTTP request

**Fields**:
- `status_code`: int - HTTP status code from target
- `headers`: Dict[str, str] - Response headers from target
- `body`: str - Response body from target
- `proxy_used`: str - Proxy URL that successfully fetched the response
- `response_time`: float - Time taken in seconds
- `attempts`: int - Number of attempts before success

**Validation Rules**:
- `status_code` must be 100-599
- `response_time` must be positive
- `attempts` must be >= 1

**Example**:
```json
{
  "status_code": 200,
  "headers": {
    "content-type": "application/json"
  },
  "body": "{\"origin\": \"1.2.3.4\"}",
  "proxy_used": "http://proxy1.example.com:8080",
  "response_time": 1.234,
  "attempts": 1
}
```

---

### 6. ProxyResource

**Purpose**: RESTful representation of proxy with health info

**Fields**:
- `id`: str - Unique proxy identifier (UUID)
- `url`: str - Proxy URL
- `username`: Optional[str] - Username (if authenticated)
- `password_set`: bool - Whether password is configured (never expose actual password)
- `health_status`: HealthStatus - Current health (HEALTHY, DEGRADED, UNHEALTHY, UNKNOWN)
- `last_success_at`: Optional[datetime] - Last successful request timestamp
- `last_failure_at`: Optional[datetime] - Last failed request timestamp
- `consecutive_failures`: int - Failure count since last success
- `total_requests`: int - Lifetime request count
- `avg_response_time`: Optional[float] - Average response time in seconds
- `created_at`: datetime - When proxy was added to pool

**Validation Rules**:
- `id` is auto-generated UUID4
- `url` must be valid proxy URL
- `consecutive_failures` must be >= 0
- `total_requests` must be >= 0
- `avg_response_time` must be positive if set

**Example**:
```json
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
```

---

### 7. CreateProxyRequest

**Purpose**: Add new proxy to pool

**Fields**:
- `url`: str - Proxy URL (validated)
- `username`: Optional[str] - Optional username
- `password`: Optional[SecretStr] - Optional password (encrypted in storage)
- `validate`: bool = True - Whether to health-check before adding

**Validation Rules**:
- `url` must be valid HTTP/HTTPS URL with port
- If `username` provided, `password` should be provided too (warning if missing)
- `password` uses Pydantic SecretStr (never logged)

**Example**:
```json
{
  "url": "http://proxy2.example.com:8080",
  "username": "user456",
  "password": "secret123",
  "validate": true
}
```

---

### 8. HealthCheckResult

**Purpose**: Health check results for proxy

**Fields**:
- `proxy_id`: str - Proxy identifier
- `healthy`: bool - Whether proxy passed health check
- `response_time`: Optional[float] - Response time if successful
- `error`: Optional[str] - Error message if failed
- `checked_at`: datetime - When check was performed

**Example**:
```json
{
  "proxy_id": "550e8400-e29b-41d4-a716-446655440000",
  "healthy": true,
  "response_time": 0.234,
  "error": null,
  "checked_at": "2025-10-27T10:30:00Z"
}
```

---

### 9. PoolStatistics

**Purpose**: Proxy pool metrics

**Fields**:
- `total_proxies`: int - Total proxies in pool
- `healthy_proxies`: int - Proxies with HEALTHY status
- `degraded_proxies`: int - Proxies with DEGRADED status
- `unhealthy_proxies`: int - Proxies with UNHEALTHY status
- `unknown_proxies`: int - Proxies with UNKNOWN status
- `avg_response_time`: Optional[float] - Average across all healthy proxies
- `total_requests`: int - Lifetime requests across all proxies

**Validation Rules**:
- Sum of status counts must equal `total_proxies`
- All counts must be >= 0

**Example**:
```json
{
  "total_proxies": 10,
  "healthy_proxies": 8,
  "degraded_proxies": 1,
  "unhealthy_proxies": 1,
  "unknown_proxies": 0,
  "avg_response_time": 0.765,
  "total_requests": 15234
}
```

---

### 10. ConfigurationSettings

**Purpose**: API and rotation configuration

**Fields**:
- `rotation_strategy`: str - Active strategy (round_robin, random, weighted, least_used)
- `health_check_interval`: int - Seconds between health checks
- `timeout`: int - Default request timeout
- `max_retries`: int - Default retry count
- `follow_redirects`: bool - Whether to follow HTTP redirects
- `verify_ssl`: bool - Whether to verify SSL certificates
- `require_auth`: bool - Whether API key auth is enabled
- `rate_limit`: str - Rate limit string (e.g., "100/minute")

**Validation Rules**:
- `rotation_strategy` must be valid strategy name
- `health_check_interval` must be 60-3600 seconds
- `timeout` must be 1-300 seconds
- `max_retries` must be 0-10

**Example**:
```json
{
  "rotation_strategy": "round_robin",
  "health_check_interval": 300,
  "timeout": 30,
  "max_retries": 3,
  "follow_redirects": true,
  "verify_ssl": true,
  "require_auth": false,
  "rate_limit": "100/minute"
}
```

---

### 11. PaginatedResponse[T]

**Purpose**: List responses with pagination

**Fields**:
- `items`: List[T] - Array of resources
- `pagination`: PaginationInfo - Pagination metadata

**PaginationInfo Fields**:
- `total`: int - Total items across all pages
- `page`: int - Current page number (1-indexed)
- `per_page`: int - Items per page
- `pages`: int - Total number of pages

**Validation Rules**:
- `page` must be 1 to `pages`
- `per_page` must be 1-100
- `pages` = ceil(total / per_page)

**Example**:
```json
{
  "items": [...],
  "pagination": {
    "total": 100,
    "page": 1,
    "per_page": 20,
    "pages": 5
  }
}
```

---

## Relationships

```text
ProxiedRequest → ProxiedResponse
  - Request produces response

CreateProxyRequest → ProxyResource
  - Creation request produces resource

ProxyResource → HealthCheckResult
  - Resource has health checks

Pool → PoolStatistics
  - Pool has aggregate statistics

ConfigurationSettings → ProxyRotator
  - Settings control rotation behavior

APIResponse[T] wraps all responses
  - Generic envelope for consistency
```

---

## State Transitions

### Proxy Health Status

```text
UNKNOWN → HEALTHY: First successful health check
UNKNOWN → UNHEALTHY: First failed health check
HEALTHY → DEGRADED: 1-2 consecutive failures
DEGRADED → UNHEALTHY: 3+ consecutive failures
DEGRADED → HEALTHY: Successful request
UNHEALTHY → HEALTHY: Successful request
```

---

## Validation Summary

All models enforce:
- Type safety via Pydantic v2
- Field constraints (min/max, regex, enum)
- Custom validators for business logic
- Automatic OpenAPI schema generation
- Serialization/deserialization handling

**Next Phase**: Generate API contracts (OpenAPI schema)
