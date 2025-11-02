"""FastAPI REST API for ProxyWhirl proxy rotation service.

This module provides HTTP endpoints for:
- Making proxied HTTP requests
- Managing proxy pool (CRUD operations)
- Monitoring health and status
- Configuring runtime settings

The API uses:
- FastAPI for async request handling and auto-generated OpenAPI docs
- slowapi for rate limiting
- Optional API key authentication
- Singleton ProxyRotator for proxy management
"""

import os
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Literal, Optional

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from loguru import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware

from proxywhirl.api_models import (
    APIResponse,
    ConfigurationSettings,
    CreateProxyRequest,
    ErrorCode,
    HealthCheckRequest,
    HealthCheckResult,
    HealthResponse,
    MetricsResponse,
    PaginatedResponse,
    ProxiedRequest,
    ProxiedResponse,
    ProxyResource,
    ReadinessResponse,
    StatusResponse,
    UpdateConfigRequest,
)
from proxywhirl.exceptions import ProxyWhirlError, RateLimitExceeded as ProxyWhirlRateLimitExceeded
from proxywhirl.rotator import ProxyRotator
from proxywhirl.storage import SQLiteStorage

# Global singleton instances
_rotator: Optional[ProxyRotator] = None
_storage: Optional[SQLiteStorage] = None
_config: dict[str, Any] = {}

# Track app start time for uptime calculation
_app_start_time = datetime.now(timezone.utc)


# Rate limiter configuration
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


# API key authentication (optional)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: Optional[str] = Depends(api_key_header)) -> None:
    """Verify API key if authentication is required.

    Args:
        api_key: API key from X-API-Key header

    Raises:
        HTTPException: If auth is required and key is invalid
    """
    require_auth = os.getenv("PROXYWHIRL_REQUIRE_AUTH", "false").lower() == "true"

    if not require_auth:
        return

    expected_key = os.getenv("PROXYWHIRL_API_KEY")
    if not expected_key:
        logger.warning("PROXYWHIRL_REQUIRE_AUTH=true but PROXYWHIRL_API_KEY not set")
        return

    if not api_key or api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager for startup and shutdown.

    Handles:
    - ProxyRotator initialization on startup
    - Optional SQLiteStorage initialization
    - Graceful cleanup on shutdown
    """
    global _rotator, _storage, _config

    # Startup
    logger.info("Initializing ProxyWhirl API...")

    # Initialize storage if configured
    storage_path = os.getenv("PROXYWHIRL_STORAGE_PATH")
    if storage_path:
        logger.info(f"Initializing SQLiteStorage: {storage_path}")
        _storage = SQLiteStorage(storage_path)

    # Initialize rotator
    logger.info("Initializing ProxyRotator...")
    _rotator = ProxyRotator()

    # Load proxies from storage if available
    if _storage:
        try:
            stored_proxies = await _storage.load()
            for proxy in stored_proxies:
                _rotator.add_proxy(proxy)
            logger.info(f"Loaded {len(stored_proxies)} proxies from storage")
        except Exception as e:
            logger.warning(f"Failed to load proxies from storage: {e}")

    # Load initial configuration
    _config = {
        "rotation_strategy": os.getenv("PROXYWHIRL_STRATEGY", "round-robin"),
        "timeout": int(os.getenv("PROXYWHIRL_TIMEOUT", "30")),
        "max_retries": int(os.getenv("PROXYWHIRL_MAX_RETRIES", "3")),
        "rate_limits": {
            "default_limit": 100,
            "request_endpoint_limit": 50,
        },
        "auth_enabled": os.getenv("PROXYWHIRL_REQUIRE_AUTH", "false").lower() == "true",
        "cors_origins": os.getenv("PROXYWHIRL_CORS_ORIGINS", "*").split(","),
    }

    logger.info("ProxyWhirl API initialized successfully")

    yield

    # Shutdown
    logger.info("Shutting down ProxyWhirl API...")

    # Save state if storage configured
    if _storage and _rotator:
        logger.info("Saving proxy pool state...")
        await _storage.save(_rotator.pool.proxies)

    logger.info("ProxyWhirl API shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="ProxyWhirl API",
    version="1.0.0",
    description=(
        "REST API for advanced proxy rotation with auto-fetching, "
        "validation, and persistence. Manage proxy pools, make proxied "
        "requests, and monitor system health through RESTful endpoints."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]


# CORS middleware
cors_origins = os.getenv("PROXYWHIRL_CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next: Any) -> Any:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response


app.add_middleware(SecurityHeadersMiddleware)


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Any) -> JSONResponse:
    """Handle 404 Not Found errors."""
    response: APIResponse[None] = APIResponse.error_response(
        code=ErrorCode.VALIDATION_ERROR,
        message=f"Endpoint not found: {request.url.path}",
        details={"path": request.url.path, "method": request.method},
    )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=response.model_dump(mode="json"),
    )


@app.exception_handler(422)
async def validation_error_handler(request: Request, exc: Any) -> JSONResponse:
    """Handle 422 Validation errors."""
    response: APIResponse[None] = APIResponse.error_response(
        code=ErrorCode.VALIDATION_ERROR,
        message="Request validation failed",
        details={"errors": exc.errors() if hasattr(exc, "errors") else str(exc)},
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response.model_dump(mode="json"),
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle 500 Internal Server errors."""
    logger.error(f"Internal server error: {exc}", exc_info=True)
    response: APIResponse[None] = APIResponse.error_response(
        code=ErrorCode.INTERNAL_ERROR,
        message="Internal server error occurred",
        details={"error_type": type(exc).__name__},
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response.model_dump(mode="json"),
    )


@app.exception_handler(ProxyWhirlRateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: ProxyWhirlRateLimitExceeded) -> JSONResponse:
    """Handle rate limit exceeded errors (HTTP 429)."""
    logger.warning(f"Rate limit exceeded: {exc.identifier} on {exc.endpoint}")
    
    headers = {
        "X-RateLimit-Limit": str(exc.limit),
        "X-RateLimit-Remaining": "0",
        "X-RateLimit-Reset": str(exc.metadata.get("reset_at", 0)),
        "X-RateLimit-Tier": exc.tier,
        "Retry-After": str(exc.retry_after_seconds),
    }
    
    body = {
        "error": {
            "code": "rate_limit_exceeded",
            "message": str(exc),
            "details": {
                "limit": exc.limit,
                "current_count": exc.current_count,
                "window_size": exc.window_size_seconds,
                "reset_at": exc.metadata.get("reset_at_iso"),
                "retry_after_seconds": exc.retry_after_seconds,
                "tier": exc.tier,
                "endpoint": exc.endpoint,
            },
        }
    }
    
    return JSONResponse(status_code=429, content=body, headers=headers)


@app.exception_handler(ProxyWhirlError)
async def proxy_error_handler(request: Request, exc: ProxyWhirlError) -> JSONResponse:
    """Handle ProxyWhirlError exceptions."""
    response: APIResponse[None] = APIResponse.error_response(
        code=ErrorCode.PROXY_ERROR,
        message=str(exc),
        details={"error_type": type(exc).__name__},
    )
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content=response.model_dump(mode="json"),
    )


# Dependency injection
def get_rotator() -> ProxyRotator:
    """Get the singleton ProxyRotator instance.

    Returns:
        ProxyRotator instance

    Raises:
        HTTPException: If rotator not initialized
    """
    if _rotator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ProxyRotator not initialized",
        )
    return _rotator


def get_storage() -> Optional[SQLiteStorage]:
    """Get the optional SQLiteStorage instance.

    Returns:
        SQLiteStorage instance or None if not configured
    """
    return _storage


def get_config() -> dict[str, Any]:
    """Get current API configuration.

    Returns:
        Configuration dictionary
    """
    return _config


# OpenAPI customization
app.openapi_tags = [
    {
        "name": "Proxied Requests",
        "description": "Make HTTP requests through rotating proxies",
    },
    {
        "name": "Pool Management",
        "description": "Manage proxy pool (add, remove, list proxies)",
    },
    {
        "name": "Monitoring",
        "description": "Health checks, status, and metrics endpoints",
    },
    {
        "name": "Configuration",
        "description": "Runtime configuration management",
    },
]


# Root endpoint
@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    """Root endpoint - redirect to docs."""
    return {
        "message": "ProxyWhirl API",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
    }


# =============================================================================
# USER STORY 1: Make Proxied Requests via API
# =============================================================================


@app.post(
    "/api/v1/request",
    response_model=APIResponse[ProxiedResponse],
    tags=["Proxied Requests"],
    summary="Make proxied HTTP request",
)
@limiter.limit("50/minute")
async def make_proxied_request(
    request_data: ProxiedRequest,
    request: Request,
    rotator: ProxyRotator = Depends(get_rotator),
    api_key: None = Depends(verify_api_key),
) -> APIResponse[ProxiedResponse]:
    """Make an HTTP request through a rotating proxy.

    This endpoint routes your HTTP request through the proxy pool, automatically
    handling rotation and failover.

    Args:
        request_data: Request details (URL, method, headers, body, timeout)
        rotator: ProxyRotator dependency injection
        api_key: API key verification dependency

    Returns:
        APIResponse with proxied response data

    Raises:
        HTTPException: For various error conditions
    """
    start_time = time.time()
    max_retries = 3
    last_error: Optional[Exception] = None

    for attempt in range(max_retries):
        try:
            # Get next proxy from rotator using strategy
            proxy = rotator.strategy.select(rotator.pool)
            if not proxy:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="No proxies available in the pool",
                )

            # Build proxy URL for httpx
            proxy_url = str(proxy.url)

            # Make the HTTP request through the proxy
            async with httpx.AsyncClient(proxy=proxy_url) as client:
                response = await client.request(
                    method=request_data.method,
                    url=str(request_data.url),
                    headers=request_data.headers,
                    content=request_data.body.encode() if request_data.body else None,
                    timeout=request_data.timeout,
                )

            elapsed_ms = int((time.time() - start_time) * 1000)

            # Build successful response
            response_data = ProxiedResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                body=response.text,
                proxy_used=proxy_url,
                elapsed_ms=elapsed_ms,
            )

            return APIResponse.success(data=response_data)

        except (httpx.ProxyError, httpx.ConnectError, httpx.TimeoutException) as e:
            # Proxy-related error, try next proxy
            last_error = e
            logger.warning(f"Proxy attempt {attempt + 1} failed: {e}")
            continue

        except ProxyWhirlError as e:
            # Handle ProxyWhirl-specific errors
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(e),
            )

        except Exception as e:
            logger.error(f"Unexpected error in proxied request: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error: {str(e)}",
            )

    # All retries exhausted
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=f"All {max_retries} proxy attempts failed. Last error: {str(last_error)}",
    )


# =============================================================================
# USER STORY 2: Manage Proxy Pool via API
# =============================================================================


@app.get(
    "/api/v1/proxies",
    response_model=APIResponse[PaginatedResponse[ProxyResource]],
    tags=["Pool Management"],
    summary="List all proxies",
)
async def list_proxies(
    page: int = 1,
    page_size: int = 50,
    status_filter: Optional[str] = None,
    rotator: ProxyRotator = Depends(get_rotator),
    api_key: None = Depends(verify_api_key),
) -> APIResponse[PaginatedResponse[ProxyResource]]:
    """List all proxies in the pool with pagination and filtering.

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page (max 100)
        status_filter: Filter by health status (optional)
        rotator: ProxyRotator dependency
        api_key: API key verification

    Returns:
        Paginated list of proxy resources
    """
    # Validate pagination
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1")
    if page_size < 1 or page_size > 100:
        raise HTTPException(status_code=400, detail="Page size must be between 1 and 100")

    # Get all proxies
    all_proxies = rotator.pool.proxies

    # Apply status filter if provided
    if status_filter:
        # TODO: Implement status filtering based on health status
        pass

    # Calculate pagination
    total = len(all_proxies)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_proxies = all_proxies[start_idx:end_idx]

    # Convert to ProxyResource models
    proxy_resources = []
    for proxy in page_proxies:
        resource = ProxyResource(
            id=str(id(proxy)),  # Use object ID as temporary ID
            url=str(proxy.url),
            protocol=proxy.protocol or "http",
            status="active",  # TODO: Get actual status
            health="healthy",  # TODO: Get actual health
            stats={
                "total_requests": 0,  # TODO: Track these metrics
                "successful_requests": 0,
                "failed_requests": 0,
                "avg_latency_ms": 0,
            },
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        proxy_resources.append(resource)

    # Build paginated response
    paginated = PaginatedResponse[ProxyResource](
        items=proxy_resources,
        total=total,
        page=page,
        page_size=page_size,
        has_next=end_idx < total,
        has_prev=page > 1,
    )

    return APIResponse.success(data=paginated)


@app.post(
    "/api/v1/proxies",
    response_model=APIResponse[ProxyResource],
    status_code=status.HTTP_201_CREATED,
    tags=["Pool Management"],
    summary="Add new proxy",
)
async def add_proxy(
    proxy_data: CreateProxyRequest,
    rotator: ProxyRotator = Depends(get_rotator),
    api_key: None = Depends(verify_api_key),
) -> APIResponse[ProxyResource]:
    """Add a new proxy to the pool.

    Args:
        proxy_data: Proxy URL and optional credentials
        rotator: ProxyRotator dependency
        api_key: API key verification

    Returns:
        Created proxy resource
    """
    from proxywhirl.models import Proxy

    # Check for duplicate
    proxy_url_str = str(proxy_data.url)
    for existing_proxy in rotator.pool.proxies:
        if str(existing_proxy.url) == proxy_url_str:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Proxy already exists: {proxy_url_str}",
            )

    # Create proxy
    try:
        from pydantic import SecretStr

        new_proxy = Proxy(
            url=proxy_url_str,
            username=SecretStr(proxy_data.username) if proxy_data.username else None,
            password=proxy_data.password,
        )

        # Add to rotator
        rotator.add_proxy(new_proxy)

        # Build response
        resource = ProxyResource(
            id=str(id(new_proxy)),
            url=str(new_proxy.url),
            protocol=new_proxy.protocol or "http",
            status="active",
            health="healthy",
            stats={
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "avg_latency_ms": 0,
            },
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        return APIResponse.success(data=resource)

    except Exception as e:
        logger.error(f"Error adding proxy: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid proxy: {str(e)}",
        )


@app.get(
    "/api/v1/proxies/{proxy_id}",
    response_model=APIResponse[ProxyResource],
    tags=["Pool Management"],
    summary="Get proxy by ID",
)
async def get_proxy(
    proxy_id: str,
    rotator: ProxyRotator = Depends(get_rotator),
    api_key: None = Depends(verify_api_key),
) -> APIResponse[ProxyResource]:
    """Get details of a specific proxy.

    Args:
        proxy_id: Proxy identifier
        rotator: ProxyRotator dependency
        api_key: API key verification

    Returns:
        Proxy resource
    """
    # Find proxy by ID
    for proxy in rotator.pool.proxies:
        if str(id(proxy)) == proxy_id:
            resource = ProxyResource(
                id=str(id(proxy)),
                url=str(proxy.url),
                protocol=proxy.protocol or "http",
                status="active",
                health="healthy",
                stats={
                    "total_requests": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "avg_latency_ms": 0,
                },
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            return APIResponse.success(data=resource)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Proxy not found: {proxy_id}",
    )


@app.delete(
    "/api/v1/proxies/{proxy_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Pool Management"],
    summary="Delete proxy",
)
async def delete_proxy(
    proxy_id: str,
    rotator: ProxyRotator = Depends(get_rotator),
    storage: Optional[SQLiteStorage] = Depends(get_storage),
    api_key: None = Depends(verify_api_key),
) -> None:
    """Remove a proxy from the pool.

    Args:
        proxy_id: Proxy identifier
        rotator: ProxyRotator dependency
        storage: Optional storage dependency
        api_key: API key verification
    """
    # Find and remove proxy
    for i, proxy in enumerate(rotator.pool.proxies):
        if str(id(proxy)) == proxy_id:
            rotator.pool.proxies.pop(i)

            # Persist if storage configured
            if storage:
                await storage.save(rotator.pool.proxies)

            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Proxy not found: {proxy_id}",
    )


@app.post(
    "/api/v1/proxies/test",
    response_model=APIResponse[list[HealthCheckResult]],
    tags=["Pool Management"],
    summary="Health check proxies",
)
async def health_check_proxies(
    request_data: HealthCheckRequest,
    rotator: ProxyRotator = Depends(get_rotator),
    api_key: None = Depends(verify_api_key),
) -> APIResponse[list[HealthCheckResult]]:
    """Run health checks on specified proxies.

    Args:
        request_data: Optional list of proxy IDs to check
        rotator: ProxyRotator dependency
        api_key: API key verification

    Returns:
        List of health check results
    """
    import httpx

    # Determine which proxies to check
    proxies_to_check = rotator.pool.proxies
    if request_data.proxy_ids:
        proxies_to_check = [p for p in rotator.pool.proxies if str(id(p)) in request_data.proxy_ids]

    results = []
    test_url = "https://httpbin.org/get"

    for proxy in proxies_to_check:
        start_time = time.time()
        try:
            async with httpx.AsyncClient(proxy=str(proxy.url), timeout=10.0) as client:
                response = await client.get(test_url)
                latency_ms = int((time.time() - start_time) * 1000)

                result = HealthCheckResult(
                    proxy_id=str(id(proxy)),
                    status="working" if response.status_code == 200 else "failed",
                    latency_ms=latency_ms,
                    error=None,
                    tested_at=datetime.now(timezone.utc),
                )
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            result = HealthCheckResult(
                proxy_id=str(id(proxy)),
                status="failed",
                latency_ms=latency_ms,
                error=str(e),
                tested_at=datetime.now(timezone.utc),
            )

        results.append(result)

    return APIResponse.success(data=results)


# =============================================================================
# USER STORY 3: Monitor API Health and Status
# =============================================================================


@app.get(
    "/api/v1/health",
    response_model=APIResponse[HealthResponse],
    tags=["Monitoring"],
    summary="API health check",
)
async def health_check(
    rotator: ProxyRotator = Depends(get_rotator),
) -> JSONResponse:
    """Check API health status.

    Returns 200 if healthy, 503 if unhealthy.

    Args:
        rotator: ProxyRotator dependency

    Returns:
        Health status response
    """
    uptime_seconds = int((datetime.now(timezone.utc) - _app_start_time).total_seconds())

    # Determine health based on proxy pool
    total_proxies = len(rotator.pool.proxies)
    if total_proxies == 0:
        health_status: Literal["healthy", "degraded", "unhealthy"] = "unhealthy"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        # TODO: Check actual health of proxies
        health_status = "healthy"
        status_code = status.HTTP_200_OK

    health_response = HealthResponse(
        status=health_status,
        uptime_seconds=uptime_seconds,
        version="1.0.0",
        timestamp=datetime.now(timezone.utc),
    )

    return JSONResponse(
        status_code=status_code,
        content=APIResponse.success(data=health_response).model_dump(mode="json"),
    )


@app.get(
    "/api/v1/ready",
    response_model=APIResponse[ReadinessResponse],
    tags=["Monitoring"],
    summary="API readiness check",
)
async def readiness_check(
    rotator: ProxyRotator = Depends(get_rotator),
    storage: Optional[SQLiteStorage] = Depends(get_storage),
) -> JSONResponse:
    """Check if API is ready to serve requests.

    Returns 200 if ready, 503 if not ready.

    Args:
        rotator: ProxyRotator dependency
        storage: Optional storage dependency

    Returns:
        Readiness status response
    """
    checks = {
        "proxy_pool_initialized": rotator is not None,
        "storage_connected": storage is not None if storage else True,
    }

    ready = all(checks.values())
    status_code = status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE

    readiness_response = ReadinessResponse(
        ready=ready,
        checks=checks,
    )

    return JSONResponse(
        status_code=status_code,
        content=APIResponse.success(data=readiness_response).model_dump(mode="json"),
    )


@app.get(
    "/api/v1/status",
    response_model=APIResponse[StatusResponse],
    tags=["Monitoring"],
    summary="Get system status",
)
async def get_status(
    rotator: ProxyRotator = Depends(get_rotator),
    storage: Optional[SQLiteStorage] = Depends(get_storage),
    config: dict[str, Any] = Depends(get_config),
) -> APIResponse[StatusResponse]:
    """Get detailed system status including pool stats.

    Args:
        rotator: ProxyRotator dependency
        storage: Optional storage dependency
        config: Configuration dependency

    Returns:
        System status response
    """
    from proxywhirl.api_models import ProxyPoolStats

    total = len(rotator.pool.proxies)
    # TODO: Calculate active/failed based on actual health checks
    active = total
    failed = 0
    healthy_percentage = (active / total * 100) if total > 0 else 0.0

    pool_stats = ProxyPoolStats(
        total=total,
        active=active,
        failed=failed,
        healthy_percentage=healthy_percentage,
        last_rotation=None,  # TODO: Track last rotation time
    )

    storage_backend = "memory"
    if storage:
        storage_backend = "sqlite"

    status_response = StatusResponse(
        pool_stats=pool_stats,
        rotation_strategy=config.get("rotation_strategy", "round-robin"),
        storage_backend=storage_backend,
        config_source="environment",
    )

    return APIResponse.success(data=status_response)


@app.get(
    "/api/v1/metrics",
    response_model=APIResponse[MetricsResponse],
    tags=["Monitoring"],
    summary="Get performance metrics",
)
async def get_metrics(
    rotator: ProxyRotator = Depends(get_rotator),
) -> APIResponse[MetricsResponse]:
    """Get API performance metrics.

    Args:
        rotator: ProxyRotator dependency

    Returns:
        Performance metrics response
    """
    # TODO: Implement actual metrics tracking
    metrics_response = MetricsResponse(
        requests_total=0,
        requests_per_second=0.0,
        avg_latency_ms=0.0,
        error_rate=0.0,
        proxy_stats=[],
    )

    return APIResponse.success(data=metrics_response)


# =============================================================================
# USER STORY 4: Configure API Settings
# =============================================================================


@app.get(
    "/api/v1/config",
    response_model=APIResponse[ConfigurationSettings],
    tags=["Configuration"],
    summary="Get current configuration",
)
async def get_configuration(
    config: dict[str, Any] = Depends(get_config),
    api_key: None = Depends(verify_api_key),
) -> APIResponse[ConfigurationSettings]:
    """Get current API configuration.

    Args:
        config: Configuration dependency
        api_key: API key verification

    Returns:
        Current configuration settings
    """
    from proxywhirl.api_models import RateLimitConfig

    config_settings = ConfigurationSettings(
        rotation_strategy=config.get("rotation_strategy", "round-robin"),
        timeout=config.get("timeout", 30),
        max_retries=config.get("max_retries", 3),
        rate_limits=RateLimitConfig(**config.get("rate_limits", {})),
        auth_enabled=config.get("auth_enabled", False),
        cors_origins=config.get("cors_origins", ["*"]),
    )

    return APIResponse.success(data=config_settings)


@app.put(
    "/api/v1/config",
    response_model=APIResponse[ConfigurationSettings],
    tags=["Configuration"],
    summary="Update configuration",
)
async def update_configuration(
    update_data: UpdateConfigRequest,
    config: dict[str, Any] = Depends(get_config),
    rotator: ProxyRotator = Depends(get_rotator),
    api_key: None = Depends(verify_api_key),
) -> APIResponse[ConfigurationSettings]:
    """Update API configuration at runtime.

    Args:
        update_data: Configuration updates (partial)
        config: Configuration dependency
        rotator: ProxyRotator dependency
        api_key: API key verification

    Returns:
        Updated configuration settings
    """
    from proxywhirl.api_models import RateLimitConfig

    # Apply updates
    if update_data.rotation_strategy is not None:
        config["rotation_strategy"] = update_data.rotation_strategy
        # TODO: Update rotator strategy

    if update_data.timeout is not None:
        config["timeout"] = update_data.timeout

    if update_data.max_retries is not None:
        config["max_retries"] = update_data.max_retries

    if update_data.rate_limits is not None:
        config["rate_limits"] = update_data.rate_limits.model_dump()

    if update_data.cors_origins is not None:
        config["cors_origins"] = update_data.cors_origins

    # Return updated config
    config_settings = ConfigurationSettings(
        rotation_strategy=config.get("rotation_strategy", "round-robin"),
        timeout=config.get("timeout", 30),
        max_retries=config.get("max_retries", 3),
        rate_limits=RateLimitConfig(**config.get("rate_limits", {})),
        auth_enabled=config.get("auth_enabled", False),
        cors_origins=config.get("cors_origins", ["*"]),
    )

    return APIResponse.success(data=config_settings)
