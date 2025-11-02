# Research: REST API Implementation

**Feature**: 003-rest-api  
**Date**: 2025-10-27  
**Status**: Complete

## Research Tasks

### 1. FastAPI Best Practices for Proxy Services

**Question**: What are the best practices for implementing a proxy service with FastAPI?

**Decision**: Use FastAPI dependency injection with singleton ProxyRotator pattern

**Rationale**:
- FastAPI's dependency injection system allows sharing a single ProxyRotator instance across all requests
- Singleton pattern prevents resource conflicts and ensures consistent rotation state
- Async route handlers align with httpx async client used in core library
- Built-in exception handling with custom exception handlers for ProxyWhirl exceptions

**Key Patterns**:
```python
# Singleton dependency
_rotator: Optional[ProxyRotator] = None

def get_rotator() -> ProxyRotator:
    global _rotator
    if _rotator is None:
        # Initialize from config
        _rotator = ProxyRotator(...)
    return _rotator

@app.get("/api/v1/request")
async def make_request(
    url: str,
    rotator: ProxyRotator = Depends(get_rotator)
):
    async with rotator.rotate() as proxy:
        # Make request
```

**Alternatives Considered**:
- **Per-request ProxyRotator**: Rejected - wastes resources and loses rotation state
- **Global variable**: Rejected - not testable, violates dependency injection principles
- **Class-based views**: Rejected - adds unnecessary complexity over function-based routes

**References**:
- FastAPI dependency injection docs: https://fastapi.tiangolo.com/tutorial/dependencies/
- FastAPI startup/shutdown events: https://fastapi.tiangolo.com/advanced/events/

---

### 2. Rate Limiting Implementation

**Question**: What's the best approach for rate limiting in FastAPI?

**Decision**: Use `slowapi` library with IP-based rate limiting

**Rationale**:
- `slowapi` is a FastAPI-compatible port of Flask-Limiter
- Supports in-memory storage (single instance) and Redis (distributed)
- Per-IP and per-route rate limiting
- Returns standard HTTP 429 with Retry-After header
- Minimal configuration: `@limiter.limit("100/minute")`

**Implementation**:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/v1/request")
@limiter.limit("100/minute")
async def make_request(...):
    ...
```

**Alternatives Considered**:
- **Custom middleware**: Rejected - reinvents the wheel, harder to test
- **fastapi-limiter**: Rejected - requires Redis, more complex for single-instance use case
- **NGINX rate limiting**: Rejected - infrastructure concern, not portable for local development

**References**:
- slowapi GitHub: https://github.com/laurentS/slowapi
- FastAPI rate limiting discussion: https://github.com/tiangolo/fastapi/discussions/4182

---

### 3. API Key Authentication Pattern

**Question**: How should optional API key authentication be implemented?

**Decision**: Use FastAPI security utilities with optional dependency

**Rationale**:
- FastAPI's `APIKeyHeader` provides built-in support for header-based API keys
- Optional dependency pattern allows disabling auth for local development
- Integrates with OpenAPI/Swagger for automatic "Authorize" button
- Clean separation: security.py module handles auth logic

**Implementation**:
```python
from fastapi.security import APIKeyHeader
from fastapi import Security, HTTPException, status

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(
    api_key: Optional[str] = Security(api_key_header)
) -> Optional[str]:
    if not settings.require_auth:
        return None  # Auth disabled
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key"
        )
    
    # Verify against encrypted storage (reuse Fernet from Phase 2)
    if not is_valid_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return api_key

# Use in routes
@app.get("/api/v1/proxies")
async def list_proxies(
    auth: Optional[str] = Depends(verify_api_key)
):
    ...
```

**Alternatives Considered**:
- **JWT tokens**: Rejected - overkill for simple API key auth, adds complexity
- **OAuth2**: Rejected - too complex for this use case, requires additional services
- **Basic Auth**: Rejected - API keys are more flexible and don't require username/password

**References**:
- FastAPI security docs: https://fastapi.tiangolo.com/tutorial/security/
- APIKeyHeader: https://fastapi.tiangolo.com/reference/security/

---

### 4. Graceful Shutdown Pattern

**Question**: How to implement graceful shutdown for saving proxy pool state?

**Decision**: Use FastAPI lifespan context manager (modern approach)

**Rationale**:
- Lifespan context manager is the modern FastAPI pattern (replaces deprecated startup/shutdown events)
- Async context manager supports cleanup operations
- Integrates with SIGTERM signal handling
- Allows timeout for in-flight requests

**Implementation**:
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load proxy pool
    rotator = get_rotator()
    await rotator.load_from_storage()
    
    yield  # Application runs
    
    # Shutdown: Save proxy pool
    await rotator.save_to_storage()
    await rotator.close()

app = FastAPI(lifespan=lifespan)
```

**Alternatives Considered**:
- **@app.on_event("startup")/@app.on_event("shutdown")**: Deprecated in FastAPI 0.109+
- **Signal handlers only**: Rejected - doesn't integrate with ASGI server lifecycle
- **No graceful shutdown**: Rejected - risks losing proxy pool state

**References**:
- FastAPI lifespan: https://fastapi.tiangolo.com/advanced/events/#lifespan
- FastAPI migration guide: https://fastapi.tiangolo.com/release-notes/#0109

---

### 5. OpenAPI Schema Customization

**Question**: How to enhance auto-generated OpenAPI schema with examples?

**Decision**: Use Pydantic Field() with examples parameter and OpenAPI schema customization

**Rationale**:
- Pydantic v2 `Field(examples=[...])` adds examples to schema automatically
- FastAPI's `openapi_extra` allows custom schema extensions
- Examples improve API documentation usability
- Validates against actual request/response models

**Implementation**:
```python
from pydantic import BaseModel, Field

class ProxyRequest(BaseModel):
    url: str = Field(
        ..., 
        description="Target URL to fetch through proxy",
        examples=["https://httpbin.org/get"]
    )
    method: str = Field(
        default="GET",
        examples=["GET", "POST", "PUT"]
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "url": "https://httpbin.org/get",
                "method": "GET",
                "headers": {"User-Agent": "MyApp/1.0"}
            }
        }
    }
```

**Alternatives Considered**:
- **Manual OpenAPI schema**: Rejected - loses type safety and sync with models
- **Separate example files**: Rejected - duplicates model definitions
- **No examples**: Rejected - poor developer experience for API consumers

**References**:
- Pydantic examples: https://docs.pydantic.dev/latest/concepts/json_schema/
- FastAPI OpenAPI customization: https://fastapi.tiangolo.com/advanced/extending-openapi/

---

### 6. Docker Multi-Stage Build Best Practices

**Question**: What's the optimal Dockerfile structure for FastAPI applications?

**Decision**: Multi-stage build with uv for dependency management

**Rationale**:
- Multi-stage build reduces final image size (dev dependencies excluded)
- `uv` is already used in the project, provides fast dependency installation
- Non-root user for security
- Health check built into Dockerfile

**Implementation**:
```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /build
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --no-dev

# Stage 2: Runtime
FROM python:3.11-slim

RUN useradd -m -u 1000 proxywhirl
WORKDIR /app

COPY --from=builder /build/.venv /app/.venv
COPY proxywhirl/ /app/proxywhirl/

USER proxywhirl
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "proxywhirl.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Alternatives Considered**:
- **Single-stage build**: Rejected - includes dev dependencies, larger image
- **Alpine base**: Rejected - compilation issues with some Python packages
- **Root user**: Rejected - security risk

**References**:
- FastAPI Docker docs: https://fastapi.tiangolo.com/deployment/docker/
- Docker best practices: https://docs.docker.com/develop/dev-best-practices/

---

## Summary

All research questions have been answered with concrete decisions:

1. ✅ **FastAPI Architecture**: Dependency injection with singleton ProxyRotator
2. ✅ **Rate Limiting**: slowapi library with IP-based limiting
3. ✅ **Authentication**: Optional API key via X-API-Key header
4. ✅ **Graceful Shutdown**: Lifespan context manager for pool persistence
5. ✅ **OpenAPI Schema**: Pydantic Field examples and model_config
6. ✅ **Docker Deployment**: Multi-stage build with uv and non-root user

**Next Phase**: Phase 1 - Design data models and API contracts
