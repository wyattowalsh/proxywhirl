# Configuration Management API Endpoints

**Feature**: 012-configuration-management-flexible  
**Date**: 2025-11-02  
**Integration**: Extends 003-rest-api with configuration management endpoints

## Base Path

All endpoints under: `/api/v1/config`

## Authentication

All endpoints require:
- API key authentication (if `PROXYWHIRL_REQUIRE_AUTH=true`)
- Admin role for write operations (POST, PATCH, PUT)

## Endpoints

### 1. Get Current Configuration

**Endpoint**: `GET /api/v1/config`

**Description**: Retrieve current configuration (redacted credentials)

**Authorization**: Any authenticated user

**Response**: `200 OK`

```json
{
  "settings": {
    "timeout": 10,
    "max_retries": 5,
    "log_level": "DEBUG",
    "proxy_url": "*** REDACTED ***",
    "database_path": "proxywhirl.db",
    "server_host": "0.0.0.0",
    "server_port": 8000,
    "rate_limit_requests": 100
  },
  "sources": {
    "timeout": "cli_argument",
    "max_retries": "yaml_file",
    "log_level": "environment",
    "proxy_url": "yaml_file",
    "database_path": "default",
    "server_host": "default",
    "server_port": "default",
    "rate_limit_requests": "default"
  },
  "hot_reloadable": {
    "timeout": true,
    "max_retries": true,
    "log_level": true,
    "proxy_url": false,
    "database_path": false,
    "server_host": false,
    "server_port": false,
    "rate_limit_requests": true
  },
  "version": 42
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid API key
- `500 Internal Server Error`: Configuration retrieval failed

---

### 2. Update Configuration (Runtime)

**Endpoint**: `PATCH /api/v1/config`

**Description**: Update configuration at runtime (hot-reloadable fields only)

**Authorization**: Admin user only

**Request Body**:

```json
{
  "updates": {
    "timeout": 15,
    "log_level": "INFO"
  }
}
```

**Response**: `200 OK`

```json
{
  "status": "updated",
  "updated_fields": ["timeout", "log_level"],
  "restart_required": false,
  "version": 43,
  "timestamp": "2025-11-02T14:30:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid configuration values or non-hot-reloadable fields
  ```json
  {
    "detail": "Cannot update restart-required fields at runtime: proxy_url"
  }
  ```
- `401 Unauthorized`: Missing or invalid API key
- `403 Forbidden`: User does not have admin privileges
  ```json
  {
    "detail": "Admin privileges required"
  }
  ```
- `422 Validation Error`: Configuration validation failed
  ```json
  {
    "detail": "Validation errors",
    "errors": [
      {
        "field": "timeout",
        "message": "Must be between 1 and 300",
        "value": -5
      }
    ]
  }
  ```

---

### 3. Validate Configuration

**Endpoint**: `POST /api/v1/config/validate`

**Description**: Validate configuration without applying changes

**Authorization**: Any authenticated user

**Request Body**:

```json
{
  "settings": {
    "timeout": 1000,
    "max_retries": 3
  }
}
```

**Response**: `200 OK`

```json
{
  "valid": false,
  "errors": [
    {
      "field": "timeout",
      "message": "Must be at most 300",
      "value": 1000
    }
  ],
  "warnings": []
}
```

**Success Example** (valid configuration):

```json
{
  "valid": true,
  "errors": [],
  "warnings": [
    "timeout value is very low (1s), may cause frequent timeouts"
  ]
}
```

**Error Responses**:
- `400 Bad Request`: Invalid request body
- `401 Unauthorized`: Missing or invalid API key

---

### 4. Export Configuration

**Endpoint**: `GET /api/v1/config/export`

**Description**: Export current configuration as YAML with source attribution

**Authorization**: Any authenticated user

**Query Parameters**:
- `format` (optional): `yaml` (default) or `json`

**Response**: `200 OK`

**Content-Type**: `text/yaml` or `application/json`

**YAML Response**:

```yaml
# ProxyWhirl Configuration Export
# Generated: 2025-11-02T14:30:00Z
# Merged from: CLI, ENV, config.yaml

# Request timeout in seconds (source: CLI argument)
timeout: 10

# Maximum retry attempts (source: environment variable)
max_retries: 5

# Logging level (source: config.yaml)
log_level: DEBUG

# Proxy URL (source: config.yaml, CREDENTIALS REDACTED)
proxy_url: *** REDACTED ***
```

**JSON Response** (format=json):

```json
{
  "settings": {
    "timeout": 10,
    "max_retries": 5,
    "log_level": "DEBUG",
    "proxy_url": "*** REDACTED ***"
  },
  "sources": {
    "timeout": "cli_argument",
    "max_retries": "environment",
    "log_level": "yaml_file",
    "proxy_url": "yaml_file"
  },
  "timestamp": "2025-11-02T14:30:00Z",
  "metadata": {
    "version": "42",
    "hot_reloadable_count": "5"
  }
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid API key
- `500 Internal Server Error`: Export failed

---

### 5. Reload Configuration from File

**Endpoint**: `POST /api/v1/config/reload`

**Description**: Manually trigger configuration reload from file

**Authorization**: Admin user only

**Request Body**: None (empty)

**Response**: `200 OK`

```json
{
  "status": "reloaded",
  "version": 44,
  "timestamp": "2025-11-02T14:31:00Z",
  "changes": {
    "timeout": 10,
    "max_retries": 7
  }
}
```

**Error Responses**:
- `400 Bad Request`: Configuration file not found or invalid
  ```json
  {
    "detail": "Configuration file not found: proxywhirl.yaml"
  }
  ```
- `401 Unauthorized`: Missing or invalid API key
- `403 Forbidden`: User does not have admin privileges
- `422 Validation Error`: New configuration invalid
  ```json
  {
    "detail": "Configuration reload failed: validation errors",
    "errors": [...]
  }
  ```

---

### 6. Rollback Configuration

**Endpoint**: `POST /api/v1/config/rollback`

**Description**: Rollback to previous configuration

**Authorization**: Admin user only

**Request Body**: None (empty)

**Response**: `200 OK`

```json
{
  "status": "rolled_back",
  "version": 43,
  "timestamp": "2025-11-02T14:32:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: No previous configuration available
  ```json
  {
    "detail": "No previous configuration to rollback to"
  }
  ```
- `401 Unauthorized`: Missing or invalid API key
- `403 Forbidden`: User does not have admin privileges

---

### 7. Get Configuration History

**Endpoint**: `GET /api/v1/config/history`

**Description**: Get recent configuration changes (audit trail)

**Authorization**: Admin user only

**Query Parameters**:
- `limit` (optional): Maximum number of records (default: 50, max: 500)
- `since` (optional): ISO 8601 timestamp (only changes after this time)

**Response**: `200 OK`

```json
{
  "updates": [
    {
      "version": 43,
      "user_id": "admin123",
      "username": "admin",
      "timestamp": "2025-11-02T14:30:00Z",
      "changes": {
        "timeout": 15,
        "log_level": "INFO"
      },
      "source": "runtime_update"
    },
    {
      "version": 42,
      "user_id": "admin123",
      "username": "admin",
      "timestamp": "2025-11-02T14:25:00Z",
      "changes": {
        "max_retries": 7
      },
      "source": "runtime_update"
    }
  ],
  "total": 2
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid API key
- `403 Forbidden`: User does not have admin privileges

---

### 8. Get Configuration Schema

**Endpoint**: `GET /api/v1/config/schema`

**Description**: Get JSON schema for configuration validation

**Authorization**: Any authenticated user

**Response**: `200 OK`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ProxyWhirlSettings",
  "type": "object",
  "properties": {
    "timeout": {
      "type": "integer",
      "minimum": 1,
      "maximum": 300,
      "default": 5,
      "description": "Request timeout in seconds"
    },
    "max_retries": {
      "type": "integer",
      "minimum": 0,
      "maximum": 10,
      "default": 3,
      "description": "Maximum retry attempts"
    },
    "log_level": {
      "type": "string",
      "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
      "default": "INFO",
      "description": "Logging level"
    }
  },
  "required": []
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid API key

---

## API Models

### ConfigUpdateRequest

```python
from pydantic import BaseModel

class ConfigUpdateRequest(BaseModel):
    """Request to update configuration."""
    updates: dict[str, Any]
```

### ConfigUpdateResponse

```python
from pydantic import BaseModel
from datetime import datetime

class ConfigUpdateResponse(BaseModel):
    """Response after configuration update."""
    status: str
    updated_fields: list[str]
    restart_required: bool
    version: int
    timestamp: datetime
```

### ValidationRequest

```python
from pydantic import BaseModel

class ValidationRequest(BaseModel):
    """Request to validate configuration."""
    settings: dict[str, Any]
```

### ValidationResponse

```python
from pydantic import BaseModel

class ValidationError(BaseModel):
    field: str
    message: str
    value: Any | None = None

class ValidationResponse(BaseModel):
    """Response from validation."""
    valid: bool
    errors: list[ValidationError]
    warnings: list[str]
```

---

## Rate Limiting

All configuration endpoints inherit rate limiting from 003-rest-api:

- Default: 100 requests/minute
- Write endpoints (POST, PATCH): 50 requests/minute
- Export endpoint: 20 requests/minute (heavier operation)

Rate limit headers included in responses:
- `X-RateLimit-Limit`: Total requests allowed per window
- `X-RateLimit-Remaining`: Requests remaining in window
- `X-RateLimit-Reset`: UTC timestamp when window resets

---

## WebSocket Support (Future)

Optional WebSocket endpoint for real-time configuration change notifications:

**Endpoint**: `WS /api/v1/config/watch`

**Messages**:

```json
{
  "type": "config_updated",
  "version": 44,
  "changes": {
    "timeout": 15
  },
  "timestamp": "2025-11-02T14:30:00Z"
}
```

---

## Integration with Existing Endpoints

### Health Check Enhancement

`GET /health` includes configuration status:

```json
{
  "status": "healthy",
  "timestamp": "2025-11-02T14:30:00Z",
  "config": {
    "version": 43,
    "hot_reload_enabled": true,
    "last_reload": "2025-11-02T14:25:00Z"
  }
}
```

### Metrics Enhancement

`GET /metrics` includes configuration metrics:

```
proxywhirl_config_version 43
proxywhirl_config_reloads_total 5
proxywhirl_config_validation_errors_total 2
proxywhirl_config_update_conflicts_total 1
```

---

## Error Response Format

All endpoints follow standard error response format from 003-rest-api:

```json
{
  "detail": "Human-readable error message",
  "status_code": 400,
  "timestamp": "2025-11-02T14:30:00Z",
  "path": "/api/v1/config",
  "request_id": "req_abc123"
}
```

---

## Testing with cURL

### Get Current Configuration

```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:8000/api/v1/config
```

### Update Configuration

```bash
curl -X PATCH \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"updates": {"timeout": 15, "log_level": "INFO"}}' \
  http://localhost:8000/api/v1/config
```

### Validate Configuration

```bash
curl -X POST \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"settings": {"timeout": 1000}}' \
  http://localhost:8000/api/v1/config/validate
```

### Export Configuration

```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:8000/api/v1/config/export > config_backup.yaml
```

---

## Summary

**Total Endpoints**: 8 (7 HTTP + 1 WebSocket future)

**Admin-Only**: 4 endpoints (PATCH /config, POST /reload, POST /rollback, GET /history)

**Public** (authenticated): 4 endpoints (GET /config, POST /validate, GET /export, GET /schema)

**Integration**: Seamless with existing 003-rest-api infrastructure

**Ready for implementation**: Complete API contract with request/response schemas.
