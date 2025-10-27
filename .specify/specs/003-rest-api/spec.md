# Feature Specification: REST API

**Feature Branch**: `003-rest-api`  
**Created**: 2025-10-08  
**Status**: Draft  
**Input**: User description: "HTTP API endpoints for remote proxy management"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Make Proxied Requests via API (Priority: P1)

An application needs to make HTTP requests through rotating proxies via REST API. The application sends a request to the API with target URL and receives the response that was fetched through a proxy.

**Why this priority**: Core API functionality - enables remote proxy usage for distributed applications and services.

**Independent Test**: Can be tested by making POST request to API endpoint with target URL and verifying response was proxied.

**Acceptance Scenarios**:

1. **Given** API is running, **When** client sends POST to `/api/v1/request` with target URL, **Then** request is made through a proxy and response is returned
2. **Given** multiple API requests, **When** sent sequentially, **Then** each uses a different proxy from the rotation pool
3. **Given** a failed proxy, **When** API request is made, **Then** system auto-retries with next proxy and returns success

---

### User Story 2 - Manage Proxy Pool via API (Priority: P1)

A system administrator needs to remotely manage the proxy pool (add, remove, list proxies) through REST API endpoints for centralized proxy management across distributed systems.

**Why this priority**: Essential for operational management - enables programmatic proxy pool administration.

**Independent Test**: Can be tested by calling pool management endpoints and verifying proxy pool state changes correctly.

**Acceptance Scenarios**:

1. **Given** API is running, **When** client sends GET to `/api/v1/proxies`, **Then** list of all proxies with status is returned
2. **Given** new proxy URL, **When** client sends POST to `/api/v1/proxies` with proxy details, **Then** proxy is validated and added to pool
3. **Given** existing proxy, **When** client sends DELETE to `/api/v1/proxies/{id}`, **Then** proxy is removed from rotation
4. **Given** proxy pool, **When** client sends POST to `/api/v1/proxies/test`, **Then** all proxies are health-checked and results returned

---

### User Story 3 - Monitor API Health and Status (Priority: P2)

Operations teams need to monitor API health, proxy pool status, and system metrics through dedicated endpoints for observability and alerting.

**Why this priority**: Critical for production operations - enables monitoring, alerting, and troubleshooting.

**Independent Test**: Can be tested by calling health endpoints and verifying accurate status information is returned.

**Acceptance Scenarios**:

1. **Given** API is running, **When** client sends GET to `/api/v1/health`, **Then** API health status and uptime are returned
2. **Given** proxy pool, **When** client sends GET to `/api/v1/status`, **Then** pool statistics (active, failed, total proxies) are returned
3. **Given** API metrics, **When** client sends GET to `/api/v1/metrics`, **Then** performance metrics (requests/sec, latency, errors) are returned

---

### User Story 4 - Configure API Settings (Priority: P3)

Administrators want to update API configuration (rotation strategy, timeouts, limits) through REST endpoints without restarting the service.

**Why this priority**: Enhances operational flexibility - allows runtime configuration changes.

**Independent Test**: Can be tested by updating configuration via API and verifying settings are applied to subsequent requests.

**Acceptance Scenarios**:

1. **Given** API configuration, **When** client sends PUT to `/api/v1/config` with new settings, **Then** configuration is validated and applied
2. **Given** updated settings, **When** subsequent requests are made, **Then** new configuration is in effect
3. **Given** configuration request, **When** client sends GET to `/api/v1/config`, **Then** current configuration is returned

---

### Edge Cases

- What happens when API receives malformed JSON or invalid request bodies?
- How does the API handle requests when no proxies are available?
- What occurs when API rate limits are exceeded?
- How are authentication failures handled for protected endpoints?
- What happens during concurrent proxy pool modifications?
- How does API respond when target URL is unreachable through all proxies?
- What occurs when request payload exceeds size limits?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: API MUST provide POST `/api/v1/request` endpoint to make proxied HTTP requests
- **FR-002**: API MUST support all HTTP methods (GET, POST, PUT, DELETE, PATCH) for proxied requests
- **FR-003**: API MUST provide GET `/api/v1/proxies` endpoint to list all proxies with status
- **FR-004**: API MUST provide POST `/api/v1/proxies` endpoint to add new proxies to pool
- **FR-005**: API MUST provide DELETE `/api/v1/proxies/{id}` endpoint to remove proxies
- **FR-006**: API MUST provide POST `/api/v1/proxies/test` endpoint for proxy health checks
- **FR-007**: API MUST provide GET `/api/v1/health` endpoint for API health status
- **FR-008**: API MUST provide GET `/api/v1/status` endpoint for proxy pool statistics
- **FR-009**: API MUST provide GET `/api/v1/metrics` endpoint for performance metrics
- **FR-010**: API MUST provide GET/PUT `/api/v1/config` endpoints for configuration management
- **FR-011**: API MUST return responses in JSON format with consistent structure
- **FR-012**: API MUST include appropriate HTTP status codes for all responses
- **FR-013**: API MUST support request/response headers passthrough for proxied requests
- **FR-014**: API MUST implement rate limiting to prevent abuse
- **FR-015**: API MUST provide comprehensive error messages with error codes
- **FR-016**: API MUST support CORS for browser-based clients
- **FR-017**: API MUST validate all input parameters and return validation errors
- **FR-018**: API MUST support API versioning in URL path (/api/v1, /api/v2)
- **FR-019**: API MUST provide OpenAPI/Swagger documentation endpoint
- **FR-020**: API MUST log all requests with correlation IDs for tracing

### Key Entities

- **API Request**: Client request to make proxied HTTP call, including target URL, method, headers, body
- **API Response**: Response from proxied request or API operation, including status, data, metadata
- **Proxy Resource**: RESTful representation of proxy with id, URL, status, performance stats
- **API Configuration**: Settings controlling API behavior (rotation strategy, timeouts, limits, authentication)
- **Health Status**: Current API and proxy pool health information (uptime, availability, errors)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: API responds to health check requests in under 100ms
- **SC-002**: API handles 10,000 requests per minute without degradation
- **SC-003**: Proxied requests complete in under 5 seconds including proxy overhead
- **SC-004**: API achieves 99.9% uptime over 30-day period
- **SC-005**: All API endpoints return responses in under 2 seconds for normal operations
- **SC-006**: API documentation is complete with examples for all endpoints
- **SC-007**: 95% of API integration attempts succeed on first try using provided documentation
- **SC-008**: API supports 100 concurrent client connections without errors
- **SC-009**: Configuration updates apply without service interruption
- **SC-010**: API error messages enable problem resolution in 90% of error cases

## Assumptions

- API clients have network connectivity to the API service
- Clients can parse JSON responses and handle HTTP status codes
- API is deployed behind reverse proxy or load balancer for production use
- Rate limiting quotas are sufficient for typical usage patterns
- API authentication (if required) is handled at infrastructure level
- Clients respect API rate limits and implement appropriate backoff strategies

## Dependencies

- Core Python Package for proxy rotation logic
- Health Monitoring for proxy status information
- Configuration Management for settings persistence
- Metrics & Observability for performance data
- Logging System for request/response logging

---

## Technical Clarifications *(added 2025-10-27)*

### 1. API Framework

**Question**: Which Python web framework should be used for the REST API?

**Decision**: **FastAPI** (v0.100+)

**Rationale**:

- Native async/await support aligns with `httpx` and async ProxyRotator
- Auto-generated OpenAPI/Swagger documentation (FR-019)
- Built-in request validation with Pydantic models (already used in core package)
- High performance (Starlette + uvicorn)
- Modern Python 3.9+ type hints support (matches project requirements)
- Extensive ecosystem (middleware for CORS, rate limiting, etc.)

**Implementation Notes**:

- Use Pydantic v2 models for request/response validation (consistency with core)
- Deploy with `uvicorn` ASGI server (production) or `hypercorn` (HTTP/2 support)
- FastAPI dependency injection for ProxyRotator instance management

---

### 2. Authentication & Security

**Question**: How should API authentication and authorization be implemented?

**Decision**: **Optional API Key Authentication** with middleware

**Approach**:

- **Default**: No authentication (for local/development use)
- **Optional**: API key authentication via `X-API-Key` header
- **Configuration**: Enable/disable via environment variable or config file
- **Storage**: API keys stored securely using Fernet encryption (reuse from Phase 2)
- **Rate Limiting**: Built-in per-IP rate limiting using `slowapi` library
  - Default: 100 requests/minute per IP
  - Configurable limits per endpoint
  - Returns HTTP 429 with Retry-After header

**Implementation Notes**:

```python
# Middleware approach
async def api_key_auth(request: Request, api_key: str = Header(None, alias="X-API-Key")):
    if settings.require_auth and not verify_api_key(api_key):
        raise HTTPException(401, "Invalid API key")
```

**Security Headers**: Include standard headers (X-Content-Type-Options, X-Frame-Options, etc.)

---

### 3. Storage & State Management

**Question**: How does the REST API manage proxy pool state and configuration?

**Decision**: **Hybrid approach** with optional persistence

**Architecture**:

- **In-Memory**: Primary proxy pool managed by ProxyRotator instance
  - Single ProxyRotator instance per API server (singleton pattern)
  - Fast access for rotation and health checks
- **Optional Persistence**: SQLiteStorage from Phase 2
  - Enabled via `--storage sqlite:///path/to/db.sqlite` flag
  - Auto-save pool state every 5 minutes or on graceful shutdown
  - Restore pool state on API startup
- **Configuration**: File-based (TOML) + environment variables
  - Config file: `.proxywhirl.toml` or `--config` flag
  - Environment: `PROXYWHIRL_*` prefix for all settings
  - Runtime updates persisted to config file if `--save-config` enabled

**Concurrency Model**: Single-instance deployment (horizontal scaling via load balancer if needed)

---

### 4. Response Format Standards

**Question**: What is the standard JSON response structure for all endpoints?

**Decision**: **Consistent envelope format** with metadata

**Success Response**:

```json
{
  "status": "success",
  "data": { /* endpoint-specific payload */ },
  "meta": {
    "timestamp": "2025-10-27T10:30:00Z",
    "request_id": "req_abc123",
    "version": "v1"
  }
}
```

**Error Response**:

```json
{
  "status": "error",
  "error": {
    "code": "PROXY_NOT_FOUND",
    "message": "Proxy with ID 'abc123' not found",
    "details": { /* optional debug info */ }
  },
  "meta": {
    "timestamp": "2025-10-27T10:30:00Z",
    "request_id": "req_abc123",
    "version": "v1"
  }
}
```

**List/Pagination Response**:

```json
{
  "status": "success",
  "data": {
    "items": [ /* array of resources */ ],
    "pagination": {
      "total": 100,
      "page": 1,
      "per_page": 20,
      "pages": 5
    }
  },
  "meta": { /* ... */ }
}
```

**HTTP Status Codes**:

- 200 OK: Successful GET/PUT requests
- 201 Created: Successful POST (resource creation)
- 204 No Content: Successful DELETE
- 400 Bad Request: Validation errors
- 401 Unauthorized: Missing/invalid authentication
- 404 Not Found: Resource not found
- 429 Too Many Requests: Rate limit exceeded
- 500 Internal Server Error: Unexpected errors
- 503 Service Unavailable: No proxies available

---

### 5. Deployment & Operations

**Question**: How should the REST API be deployed and operated in production?

**Decision**: **Containerized deployment** with health probes

**Deployment Package**:

- **Docker**: Official `Dockerfile` with multi-stage build
  - Base: `python:3.11-slim` (production) or `python:3.11-alpine` (minimal)
  - Entry point: `uvicorn proxywhirl.api:app --host 0.0.0.0 --port 8000`
  - Expose port 8000
  - Health check: `HEALTHCHECK CMD curl -f http://localhost:8000/api/v1/health`
- **Docker Compose**: Example `docker-compose.yml` for quick start
- **Kubernetes**: Optional Helm chart for K8s deployments

**Process Management**:

- **Development**: `uvicorn proxywhirl.api:app --reload`
- **Production**:
  - Single worker: `uvicorn proxywhirl.api:app --workers 1`
  - Multi-worker NOT recommended (shared ProxyRotator state conflicts)
  - Use load balancer + multiple containers for horizontal scaling

**Configuration**:

- Environment variables for sensitive data (API keys, encryption keys)
- Config file for operational settings (timeouts, limits, proxy pool)
- CLI flags for deployment options (port, host, workers)

**Graceful Shutdown**:

- Handle SIGTERM signal
- Complete in-flight requests (30s timeout)
- Save proxy pool state to storage
- Close all connections

**Monitoring Endpoints**:

- `/api/v1/health`: Liveness probe (returns 200 if API responding)
- `/api/v1/ready`: Readiness probe (returns 200 if proxies available)
- `/api/v1/metrics`: Prometheus-compatible metrics (optional)

---

**Clarification Session**: 2025-10-27 (5/5 questions answered)  
**Next Steps**: Create `plan.md`, `tasks.md`, and implementation artifacts

