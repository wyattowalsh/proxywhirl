# Quickstart: REST API

**Feature**: 003-rest-api  
**Date**: 2025-10-27  
**Audience**: Developers integrating with ProxyWhirl REST API

## Overview

This quickstart guide demonstrates how to use the ProxyWhirl REST API for making proxied HTTP requests and managing proxy pools. The API provides HTTP endpoints for all core ProxyWhirl functionality.

---

## Prerequisites

- ProxyWhirl REST API server running (see Deployment section)
- HTTP client (curl, httpx, requests, or similar)
- (Optional) API key if authentication is enabled

---

## Starting the API Server

### Local Development

```bash
# Install ProxyWhirl with API dependencies
uv add proxywhirl[api]

# Start API server (development mode with auto-reload)
uvicorn proxywhirl.api:app --reload

# Server starts at http://localhost:8000
```

### Production (Docker)

```bash
# Build Docker image
docker build -t proxywhirl-api .

# Run container
docker run -p 8000:8000 proxywhirl-api

# Or use docker-compose
docker-compose up
```

---

## Basic Usage

### 1. Check API Health

Verify the API is running:

```bash
curl http://localhost:8000/api/v1/health
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "healthy": true,
    "uptime_seconds": 120,
    "version": "1.0.0"
  },
  "meta": {
    "timestamp": "2025-10-27T10:30:00Z",
    "request_id": "req_abc123",
    "version": "v1"
  }
}
```

---

### 2. Add Proxies to Pool

```bash
curl -X POST http://localhost:8000/api/v1/proxies \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://proxy1.example.com:8080",
    "username": "user123",
    "password": "secret",
    "validate": true
  }'
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "url": "http://proxy1.example.com:8080",
    "username": "user123",
    "password_set": true,
    "health_status": "HEALTHY",
    "created_at": "2025-10-27T10:30:00Z"
  },
  "meta": { ... }
}
```

---

### 3. Make Proxied Request

Make an HTTP request through rotating proxies:

```bash
curl -X POST http://localhost:8000/api/v1/request \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://httpbin.org/get",
    "method": "GET"
  }'
```

**Response**:
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
  "meta": { ... }
}
```

---

### 4. List Proxies

View all proxies with health status:

```bash
curl http://localhost:8000/api/v1/proxies
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "url": "http://proxy1.example.com:8080",
        "health_status": "HEALTHY",
        "total_requests": 152,
        "avg_response_time": 0.856
      }
    ],
    "pagination": {
      "total": 1,
      "page": 1,
      "per_page": 20,
      "pages": 1
    }
  },
  "meta": { ... }
}
```

---

### 5. Get Pool Status

Check proxy pool statistics:

```bash
curl http://localhost:8000/api/v1/status
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "total_proxies": 5,
    "healthy_proxies": 4,
    "degraded_proxies": 1,
    "unhealthy_proxies": 0,
    "avg_response_time": 0.765
  },
  "meta": { ... }
}
```

---

## Python Client Example

Using `httpx` for async requests:

```python
import httpx
import asyncio

async def main():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Add a proxy
        add_response = await client.post(
            "/api/v1/proxies",
            json={
                "url": "http://proxy1.example.com:8080",
                "username": "user",
                "password": "pass",
                "validate": True
            }
        )
        proxy = add_response.json()["data"]
        print(f"Added proxy: {proxy['id']}")
        
        # Make proxied request
        request_response = await client.post(
            "/api/v1/request",
            json={
                "url": "https://httpbin.org/get",
                "method": "GET"
            }
        )
        result = request_response.json()["data"]
        print(f"Request status: {result['status_code']}")
        print(f"Proxy used: {result['proxy_used']}")
        print(f"Response time: {result['response_time']}s")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Authentication (Optional)

If API key authentication is enabled:

```bash
curl http://localhost:8000/api/v1/proxies \
  -H "X-API-Key: your-api-key-here"
```

---

## Configuration Management

### View Current Configuration

```bash
curl http://localhost:8000/api/v1/config
```

### Update Configuration

```bash
curl -X PUT http://localhost:8000/api/v1/config \
  -H "Content-Type: application/json" \
  -d '{
    "rotation_strategy": "weighted",
    "timeout": 45,
    "max_retries": 5
  }'
```

---

## Interactive Documentation

FastAPI auto-generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

Use Swagger UI to:
- Browse all endpoints
- View request/response schemas
- Try out endpoints with "Try it out" button
- See authentication requirements

---

## Error Handling

All errors return consistent format:

```bash
curl http://localhost:8000/api/v1/proxies/invalid-id
```

**Error Response** (404):
```json
{
  "status": "error",
  "error": {
    "code": "PROXY_NOT_FOUND",
    "message": "Proxy with ID 'invalid-id' not found",
    "details": {
      "proxy_id": "invalid-id"
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

## Rate Limiting

API enforces rate limits per IP:

```bash
# Too many requests
curl http://localhost:8000/api/v1/request
```

**Rate Limit Response** (429):
```json
{
  "status": "error",
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded: 100 requests per minute"
  },
  "meta": { ... }
}
```

Check rate limit headers:
- `X-RateLimit-Limit`: 100
- `X-RateLimit-Remaining`: 0
- `X-RateLimit-Reset`: 1698409860
- `Retry-After`: 42

---

## Next Steps

- See [API Contracts](contracts/api-endpoints.md) for complete endpoint reference
- See [Data Model](data-model.md) for request/response schemas
- See [Deployment Guide] for production setup (coming soon)
- Check `/docs` endpoint for interactive API explorer

---

## Common Workflows

### Workflow 1: Initial Setup

1. Start API server
2. Check health: `GET /api/v1/health`
3. Add proxies: `POST /api/v1/proxies` (repeat for each proxy)
4. Test proxies: `POST /api/v1/proxies/test`
5. Configure strategy: `PUT /api/v1/config` (set rotation_strategy)

### Workflow 2: Make Requests

1. Check readiness: `GET /api/v1/ready` (ensure proxies available)
2. Make request: `POST /api/v1/request`
3. Check status: `GET /api/v1/status` (monitor pool health)

### Workflow 3: Monitor & Maintain

1. Get pool status: `GET /api/v1/status`
2. List proxies: `GET /api/v1/proxies?status=UNHEALTHY`
3. Remove bad proxies: `DELETE /api/v1/proxies/{id}`
4. Add new proxies: `POST /api/v1/proxies`
5. Test pool: `POST /api/v1/proxies/test`

---

**Ready to implement?** See `tasks.md` (generated by `/speckit.tasks`) for detailed implementation phases.
