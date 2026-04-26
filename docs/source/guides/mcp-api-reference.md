---
title: MCP API Reference
---

# MCP API Reference

This guide documents all MCP server endpoints, tool actions, resources, and prompts available in ProxyWhirl's Model Context Protocol server.

```{contents}
:local:
:depth: 3
```

## Overview

ProxyWhirl's MCP server provides:
- **Unified Tool**: Single `proxywhirl` tool with action-based operations
- **Resources**: Real-time proxy pool health and configuration data
- **Prompts**: Guided workflows for common proxy management tasks
- **Authentication**: Optional API key-based access control

All endpoints are accessible through the MCP protocol with consistent error handling and response formats.

## Tool: `proxywhirl`

The primary MCP tool provides all proxy management operations through an `action` parameter.

### Action: `list`

List all proxies in the current pool with detailed metrics.

**Request:**
```json
{
  "action": "list",
  "api_key": "optional-key"
}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "proxy-uuid",
      "url": "http://proxy:8080",
      "source": "source-name",
      "protocol": "http",
      "host": "proxy",
      "port": 8080,
      "status": "healthy",
      "last_verified": "2024-04-26T12:00:00Z",
      "success_rate": 0.95,
      "avg_response_time_ms": 245,
      "weight": 1.0,
      "tags": ["premium", "fast"]
    }
  ]
}
```

**Error Codes:**
- `403`: Authentication failed (invalid or missing API key)
- `500`: Internal server error during proxy retrieval

---

### Action: `rotate`

Get the next proxy from the pool using the configured rotation strategy.

**Request:**
```json
{
  "action": "rotate",
  "api_key": "optional-key"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "proxy-uuid",
    "url": "http://proxy:8080",
    "source": "source-name",
    "protocol": "http",
    "host": "proxy",
    "port": 8080,
    "status": "healthy",
    "success_rate": 0.95,
    "avg_response_time_ms": 245
  },
  "message": "Next proxy selected using round-robin strategy"
}
```

**Error Codes:**
- `400`: No proxies available in pool
- `403`: Authentication failed
- `500`: Strategy evaluation error

---

### Action: `status`

Get detailed health and performance metrics for a specific proxy.

**Request:**
```json
{
  "action": "status",
  "proxy_id": "proxy-uuid",
  "api_key": "optional-key"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "proxy-uuid",
    "url": "http://proxy:8080",
    "status": "healthy",
    "health_checks": {
      "total_attempts": 100,
      "successful": 95,
      "failed": 5,
      "last_check": "2024-04-26T12:05:00Z"
    },
    "performance": {
      "avg_response_time_ms": 245,
      "min_response_time_ms": 120,
      "max_response_time_ms": 890,
      "requests_served": 5432
    },
    "circuit_breaker": {
      "state": "closed",
      "failure_count": 2,
      "success_count": 93
    },
    "source": "source-name",
    "age_seconds": 3600,
    "weight": 1.0
  }
}
```

**Error Codes:**
- `404`: Proxy not found
- `403`: Authentication failed
- `500`: Status retrieval error

---

### Action: `recommend`

Get the best proxy based on specified criteria (performance, location, protocol, etc.).

**Request:**
```json
{
  "action": "recommend",
  "criteria": {
    "min_success_rate": 0.9,
    "max_response_time_ms": 500,
    "protocols": ["http", "https"],
    "country": "US",
    "exclude_tags": ["slow"]
  },
  "api_key": "optional-key"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "proxy-uuid",
    "url": "http://proxy:8080",
    "status": "healthy",
    "success_rate": 0.98,
    "avg_response_time_ms": 180,
    "reason": "Highest success rate (0.98) and fast (180ms)"
  }
}
```

**Error Codes:**
- `400`: Invalid criteria or no proxies match criteria
- `403`: Authentication failed
- `500`: Recommendation engine error

---

### Action: `add`

Add a new proxy to the pool.

**Request:**
```json
{
  "action": "add",
  "proxy_url": "http://user:pass@proxy:8080",
  "api_key": "optional-key"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "new-proxy-uuid",
    "url": "http://proxy:8080",
    "status": "pending_validation"
  },
  "message": "Proxy added successfully. Validation in progress."
}
```

**Error Codes:**
- `400`: Invalid proxy URL format
- `409`: Proxy already exists in pool
- `403`: Authentication failed
- `500`: Add operation failed

---

### Action: `remove`

Remove a proxy from the pool.

**Request:**
```json
{
  "action": "remove",
  "proxy_id": "proxy-uuid",
  "api_key": "optional-key"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "proxy-uuid",
    "removed": true
  },
  "message": "Proxy removed successfully"
}
```

**Error Codes:**
- `404`: Proxy not found
- `403`: Authentication failed
- `500`: Remove operation failed

---

### Action: `fetch`

Fetch new proxies from specified sources and add them to the pool.

**Request:**
```json
{
  "action": "fetch",
  "sources": ["recommended", "source-name-1", "source-name-2"],
  "limit": 50,
  "validate": true,
  "api_key": "optional-key"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "fetched": 45,
    "added": 42,
    "failed": 3,
    "total_pool_size": 187,
    "sources_used": ["source-1", "source-2"],
    "validation_summary": {
      "validated": 42,
      "failed_validation": 3,
      "validation_rate": 0.933
    }
  },
  "message": "Fetched 45 proxies, added 42 to pool"
}
```

**Error Codes:**
- `400`: Invalid sources specified
- `403`: Authentication failed
- `503`: Fetch operation timeout or all sources failed

---

### Action: `validate`

Validate a single proxy URL without adding to pool.

**Request:**
```json
{
  "action": "validate",
  "proxy_url": "http://proxy:8080",
  "timeout_seconds": 10,
  "api_key": "optional-key"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "valid": true,
    "url": "http://proxy:8080",
    "protocol": "http",
    "host": "proxy",
    "port": 8080,
    "response_time_ms": 234,
    "details": "Successfully connected and validated"
  }
}
```

**Response (Invalid):**
```json
{
  "success": true,
  "data": {
    "valid": false,
    "url": "http://invalid:8080",
    "error": "Connection timeout after 10 seconds",
    "error_code": "TIMEOUT"
  }
}
```

**Error Codes:**
- `400`: Invalid proxy URL format
- `403`: Authentication failed
- `500`: Validation error

---

### Action: `get_health`

Get overall pool health and statistics.

**Request:**
```json
{
  "action": "get_health",
  "api_key": "optional-key"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "pool_size": 187,
    "healthy": 165,
    "unhealthy": 22,
    "health_percentage": 88.2,
    "avg_success_rate": 0.923,
    "avg_response_time_ms": 267,
    "circuit_breaker_open": 5,
    "last_health_check": "2024-04-26T12:10:00Z",
    "stats": {
      "total_requests": 245612,
      "successful_requests": 226729,
      "failed_requests": 18883,
      "unique_sources": 12
    }
  }
}
```

---

### Action: `reset_circuit_breaker`

Reset circuit breaker for a specific proxy (after maintenance or timeout).

**Request:**
```json
{
  "action": "reset_circuit_breaker",
  "proxy_id": "proxy-uuid",
  "api_key": "optional-key"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "proxy-uuid",
    "circuit_breaker_state": "closed",
    "reset_at": "2024-04-26T12:15:00Z"
  },
  "message": "Circuit breaker reset successfully"
}
```

**Error Codes:**
- `404`: Proxy not found
- `403`: Authentication failed
- `500`: Reset operation failed

---

### Action: `set_strategy`

Change the proxy rotation strategy.

**Request:**
```json
{
  "action": "set_strategy",
  "strategy": "round_robin",
  "config": {
    "param1": "value1"
  },
  "api_key": "optional-key"
}
```

**Available Strategies:**
- `round_robin`: Sequential rotation (default)
- `random`: Random selection
- `weighted`: Weighted by success rate
- `performance_based`: Fastest proxies first
- `least_used`: Least recently used
- `geolocation_aware`: By geographic location
- `latency_optimized`: Lowest latency
- `availability_first`: Highest availability
- `cost_optimized`: Best cost/performance ratio

**Response:**
```json
{
  "success": true,
  "data": {
    "strategy": "round_robin",
    "config": {},
    "message": "Strategy changed successfully"
  }
}
```

**Error Codes:**
- `400`: Invalid strategy name
- `403`: Authentication failed
- `500`: Strategy update failed

---

## Resources

Resources provide read-only access to real-time proxy pool state and configuration.

### Resource: `proxy://health`

Real-time proxy pool health status with aggregated metrics.

**Fetch Pattern:**
```
GET proxy://health
```

**Returns:**
- Pool size and health percentage
- Circuit breaker open count
- Average success rate and response time
- Timestamp of last health check

**Content Type:** `application/json`

---

### Resource: `proxy://config`

Current runtime configuration for proxy rotation and validation.

**Fetch Pattern:**
```
GET proxy://config
```

**Returns:**
- Active rotation strategy
- Health check configuration
- Circuit breaker settings
- Cache configuration
- Rate limiting configuration

**Content Type:** `application/json`

---

## Prompts

Prompts guide AI assistants through common proxy management workflows.

### Prompt: `select-proxy`

Workflow for selecting the best proxy based on use case.

**Context Variables:**
- `use_case`: "web_scraping", "api_testing", "general_browsing"
- `location_requirement`: Geographic requirement (optional)
- `performance_requirement`: "fast", "balanced", "any"

**Includes:**
- Criteria explanation
- Recommendation steps
- Fallback strategies

---

### Prompt: `troubleshoot-proxy`

Guided troubleshooting for proxy issues.

**Context Variables:**
- `proxy_id`: Specific proxy to troubleshoot (optional)
- `error_type`: Type of error encountered
- `recent_activity`: Log snippet (optional)

**Includes:**
- Health status check
- Circuit breaker state
- Recent error analysis
- Recovery recommendations

---

### Prompt: `optimize-pool`

Workflow for optimizing proxy pool performance.

**Includes:**
- Current pool health assessment
- Underperforming proxy identification
- Fetch and validation recommendations
- Strategy optimization suggestions

---

## Error Handling

All endpoints use consistent error response format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": "Additional context (optional)"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Meaning |
|------|-------------|---------|
| `INVALID_REQUEST` | 400 | Request format or parameters invalid |
| `UNAUTHORIZED` | 401 | Missing authentication |
| `FORBIDDEN` | 403 | Authentication failed (invalid API key) |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource already exists |
| `TIMEOUT` | 408 | Request timeout |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |
| `INTERNAL_ERROR` | 500 | Internal server error |

---

## Authentication

### API Key Authentication

Pass API key via tool parameter:
```json
{
  "action": "list",
  "api_key": "your-api-key-here"
}
```

Or set via environment variable:
```bash
export PROXYWHIRL_MCP_API_KEY="your-api-key-here"
```

### Disabling Authentication

By default, authentication is optional. To enforce authentication:
```python
from proxywhirl.mcp.auth import MCPAuth
from proxywhirl.mcp.server import set_auth

auth = MCPAuth(api_key="required-key")
set_auth(auth)
```

---

## Examples

### Example 1: Get Best Proxy for Web Scraping

```json
{
  "action": "recommend",
  "criteria": {
    "min_success_rate": 0.95,
    "max_response_time_ms": 1000,
    "protocols": ["http", "https"],
    "exclude_tags": ["slow", "unstable"]
  }
}
```

### Example 2: Fetch and Validate Proxies

```json
{
  "action": "fetch",
  "sources": ["recommended"],
  "limit": 100,
  "validate": true
}
```

### Example 3: Monitor Pool Health

```json
{
  "action": "get_health"
}
```

Then check individual proxy status:
```json
{
  "action": "status",
  "proxy_id": "proxy-uuid"
}
```

### Example 4: Switch to Performance-Based Strategy

```json
{
  "action": "set_strategy",
  "strategy": "performance_based"
}
```

---

## Rate Limiting

The MCP server respects configured rate limits:
- Per-tool rate limits: Configurable per action
- Authentication rate limits: Failed attempts tracked
- Resource-intensive operations: Fetch, validate, health checks may have longer limits

Rate limit status included in response headers:
```
RateLimit-Limit: 100
RateLimit-Remaining: 95
RateLimit-Reset: 1698067200
```

---

## Versioning

API version: `v1`

Current MCP server version can be retrieved via:
```json
{
  "action": "get_info"
}
```

Response:
```json
{
  "version": "1.x.x",
  "mcp_version": "2.0.0",
  "python_version": "3.10+"
}
```

---

## Best Practices

1. **Pool Warmth**: Fetch proxies on startup or periodically to keep pool fresh
2. **Health Checks**: Monitor pool health with `get_health` before critical operations
3. **Strategy Selection**: Choose strategy based on use case:
   - `round_robin`: Balanced, default choice
   - `performance_based`: Latency-sensitive operations
   - `weighted`: When success rate matters most
   - `geolocation_aware`: Location-specific requirements

4. **Error Recovery**: Implement fallback strategies for failed proxies
5. **Resource Cleanup**: Always close rotator when done:
   ```python
   await cleanup_rotator()
   ```

---

## See Also

- {doc}`mcp-server`: Server setup and configuration
- {doc}`cli-reference`: CLI commands for proxy management
- {doc}`async-client`: Async API usage patterns
