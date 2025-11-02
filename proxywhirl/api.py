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
from datetime import datetime, timedelta, timezone
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
    CircuitBreakerEventResponse,
    CircuitBreakerResponse,
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
    ProxyRetryStatsResponse,
    ReadinessResponse,
    RetryMetricsResponse,
    RetryPolicyRequest,
    RetryPolicyResponse,
    StatusResponse,
    TimeSeriesResponse,
    UpdateConfigRequest,
)
from proxywhirl.exceptions import ProxyWhirlError
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


# ============================================================================
# EXPORT ENDPOINTS
# ============================================================================


def get_export_manager() -> "ExportManager":
    """Dependency to get or create ExportManager instance."""
    from proxywhirl.export_manager import ExportManager
    
    if not hasattr(get_export_manager, "_manager"):
        if _rotator:
            get_export_manager._manager = ExportManager(
                proxy_pool=_rotator.pool,
                storage=_storage,
            )
        else:
            get_export_manager._manager = ExportManager()
    
    return get_export_manager._manager


@app.post(
    "/api/v1/exports",
    response_model=APIResponse[dict[str, Any]],
    tags=["Export"],
    summary="Create data export",
    status_code=status.HTTP_201_CREATED,
)
async def create_export(
    export_request: "ExportRequest",
    export_manager: "ExportManager" = Depends(get_export_manager),
    api_key: None = Depends(verify_api_key),
) -> APIResponse[dict[str, Any]]:
    """Create a new data export job.
    
    Supports exporting:
    - Proxy lists (CSV, JSON, JSONL, YAML, text, markdown)
    - Metrics data with time range filtering
    - Log data with filtering
    - System configuration
    - Health status
    - Cache data
    
    Args:
        export_request: Export configuration
        export_manager: ExportManager dependency
        api_key: API key verification
        
    Returns:
        Export result with job ID and status
        
    Raises:
        HTTPException: If export fails
    """
    from proxywhirl.api_models import ExportRequest
    from proxywhirl.export_manager import ExportError
    from proxywhirl.export_models import (
        CompressionType,
        ConfigurationExportFilter,
        ExportConfig,
        ExportFormat,
        ExportType,
        LocalFileDestination,
        LogExportFilter,
        MemoryDestination,
        MetricsExportFilter,
        ProxyExportFilter,
    )
    
    try:
        # Build export config from request
        export_type   = ExportType(export_request.export_type)
        export_format = ExportFormat(export_request.export_format)
        compression   = CompressionType(export_request.compression)
        
        # Build destination
        if export_request.destination_type == "local_file":
            if not export_request.file_path:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="file_path required for local_file destination",
                )
            destination = LocalFileDestination(
                file_path=export_request.file_path,
                overwrite=export_request.overwrite,
            )
        else:
            destination = MemoryDestination()
        
        # Build filters based on export type
        proxy_filter   = None
        metrics_filter = None
        log_filter     = None
        config_filter  = None
        
        if export_type == ExportType.PROXIES:
            proxy_filter = ProxyExportFilter(
                health_status=export_request.health_status,
                source=export_request.source,
                protocol=export_request.protocol,
                min_success_rate=export_request.min_success_rate,
            )
        elif export_type == ExportType.METRICS:
            if not export_request.start_time or not export_request.end_time:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="start_time and end_time required for metrics export",
                )
            metrics_filter = MetricsExportFilter(
                start_time=export_request.start_time,
                end_time=export_request.end_time,
            )
        elif export_type == ExportType.LOGS:
            log_filter = LogExportFilter(
                start_time=export_request.start_time,
                end_time=export_request.end_time,
                log_levels=export_request.log_levels,
            )
        elif export_type == ExportType.CONFIGURATION:
            config_filter = ConfigurationExportFilter(
                redact_secrets=export_request.redact_secrets,
            )
        
        # Create export config
        config = ExportConfig(
            export_type=export_type,
            export_format=export_format,
            destination=destination,
            compression=compression,
            proxy_filter=proxy_filter,
            metrics_filter=metrics_filter,
            log_filter=log_filter,
            config_filter=config_filter,
            pretty_print=export_request.pretty_print,
            include_metadata=export_request.include_metadata,
        )
        
        # Execute export
        result = export_manager.export(config)
        
        # Build response
        response_data = {
            "job_id": str(result.job_id),
            "status": "completed" if result.success else "failed",
            "export_type": result.export_type.value,
            "export_format": result.export_format.value,
            "records_exported": result.records_exported,
            "file_size_bytes": result.file_size_bytes,
            "duration_seconds": result.duration_seconds,
            "destination_path": result.destination_path,
            "error": result.error,
        }
        
        return APIResponse.success(data=response_data)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid export configuration: {e}",
        )
    except ExportError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        logger.exception("Export creation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {e}",
        )


@app.get(
    "/api/v1/exports/{job_id}",
    response_model=APIResponse["ExportStatusResponse"],
    tags=["Export"],
    summary="Get export status",
)
async def get_export_status(
    job_id: str,
    export_manager: "ExportManager" = Depends(get_export_manager),
    api_key: None = Depends(verify_api_key),
) -> APIResponse["ExportStatusResponse"]:
    """Get status of an export job.
    
    Args:
        job_id: Export job ID
        export_manager: ExportManager dependency
        api_key: API key verification
        
    Returns:
        Export job status and progress
        
    Raises:
        HTTPException: If job not found
    """
    from uuid import UUID
    
    from proxywhirl.api_models import ExportStatusResponse
    
    try:
        job_uuid = UUID(job_id)
        job = export_manager.get_job_status(job_uuid)
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Export job not found: {job_id}",
            )
        
        # Build response
        response = ExportStatusResponse(
            job_id=str(job.job_id),
            status=job.status.value,
            export_type=job.config.export_type.value,
            export_format=job.config.export_format.value,
            total_records=job.progress.total_records,
            processed_records=job.progress.processed_records,
            progress_percentage=job.progress.progress_percentage,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
            duration_seconds=job.duration_seconds,
            result_path=job.result_path,
            error_message=job.error_message,
        )
        
        return APIResponse.success(data=response)
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid job ID format: {job_id}",
        )
    except Exception as e:
        logger.exception("Failed to get export status")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@app.get(
    "/api/v1/exports/history",
    response_model=APIResponse["ExportHistoryResponse"],
    tags=["Export"],
    summary="Get export history",
)
async def get_export_history(
    limit: int = 100,
    export_manager: "ExportManager" = Depends(get_export_manager),
    api_key: None = Depends(verify_api_key),
) -> APIResponse["ExportHistoryResponse"]:
    """Get export history.
    
    Args:
        limit: Maximum number of entries to return (default: 100)
        export_manager: ExportManager dependency
        api_key: API key verification
        
    Returns:
        List of export history entries
    """
    from proxywhirl.api_models import ExportHistoryResponse
    
    try:
        history = export_manager.get_export_history(limit=limit)
        
        # Convert to dict
        history_dicts = [entry.model_dump() for entry in history]
        
        response = ExportHistoryResponse(
            total_exports=len(history_dicts),
            exports=history_dicts,
        )
        
        return APIResponse.success(data=response)
        
    except Exception as e:
        logger.exception("Failed to get export history")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ============================================================================
# RETRY & FAILOVER API ENDPOINTS
# ============================================================================


@app.get(
    "/api/v1/retry/policy",
    response_model=APIResponse["RetryPolicyResponse"],
    tags=["Retry & Failover"],
    summary="Get global retry policy",
)
async def get_retry_policy(
    api_key: None = Depends(verify_api_key),
) -> APIResponse["RetryPolicyResponse"]:
    """Get the current global retry policy configuration.

    Returns:
        Current retry policy settings
    """
    from proxywhirl.api_models import RetryPolicyResponse

    if not _rotator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rotator not initialized",
        )

    policy = _rotator.retry_policy

    response = RetryPolicyResponse(
        max_attempts=policy.max_attempts,
        backoff_strategy=policy.backoff_strategy.value,
        base_delay=policy.base_delay,
        multiplier=policy.multiplier,
        max_backoff_delay=policy.max_backoff_delay,
        jitter=policy.jitter,
        retry_status_codes=policy.retry_status_codes,
        timeout=policy.timeout,
        retry_non_idempotent=policy.retry_non_idempotent,
    )

    return APIResponse.success(data=response)


@app.put(
    "/api/v1/retry/policy",
    response_model=APIResponse["RetryPolicyResponse"],
    tags=["Retry & Failover"],
    summary="Update global retry policy",
)
async def update_retry_policy(
    policy_request: "RetryPolicyRequest",
    api_key: None = Depends(verify_api_key),
) -> APIResponse["RetryPolicyResponse"]:
    """Update the global retry policy configuration.

    Args:
        policy_request: New retry policy settings

    Returns:
        Updated retry policy
    """
    from proxywhirl.api_models import RetryPolicyRequest, RetryPolicyResponse
    from proxywhirl.retry_policy import BackoffStrategy, RetryPolicy

    if not _rotator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rotator not initialized",
        )

    # Build new policy from request (only update provided fields)
    current_policy = _rotator.retry_policy

    policy_dict = current_policy.model_dump()

    if policy_request.max_attempts is not None:
        policy_dict["max_attempts"] = policy_request.max_attempts

    if policy_request.backoff_strategy is not None:
        policy_dict["backoff_strategy"] = BackoffStrategy(policy_request.backoff_strategy)

    if policy_request.base_delay is not None:
        policy_dict["base_delay"] = policy_request.base_delay

    if policy_request.multiplier is not None:
        policy_dict["multiplier"] = policy_request.multiplier

    if policy_request.max_backoff_delay is not None:
        policy_dict["max_backoff_delay"] = policy_request.max_backoff_delay

    if policy_request.jitter is not None:
        policy_dict["jitter"] = policy_request.jitter

    if policy_request.retry_status_codes is not None:
        policy_dict["retry_status_codes"] = policy_request.retry_status_codes

    if policy_request.timeout is not None:
        policy_dict["timeout"] = policy_request.timeout

    if policy_request.retry_non_idempotent is not None:
        policy_dict["retry_non_idempotent"] = policy_request.retry_non_idempotent

    # Create new policy
    try:
        new_policy = RetryPolicy(**policy_dict)
        _rotator.retry_policy = new_policy
        _rotator.retry_executor.retry_policy = new_policy

        response = RetryPolicyResponse(
            max_attempts=new_policy.max_attempts,
            backoff_strategy=new_policy.backoff_strategy.value,
            base_delay=new_policy.base_delay,
            multiplier=new_policy.multiplier,
            max_backoff_delay=new_policy.max_backoff_delay,
            jitter=new_policy.jitter,
            retry_status_codes=new_policy.retry_status_codes,
            timeout=new_policy.timeout,
            retry_non_idempotent=new_policy.retry_non_idempotent,
        )

        return APIResponse.success(data=response)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid policy configuration: {e}",
        )


@app.get(
    "/api/v1/circuit-breakers",
    response_model=APIResponse[list["CircuitBreakerResponse"]],
    tags=["Retry & Failover"],
    summary="List all circuit breaker states",
)
async def list_circuit_breakers(
    api_key: None = Depends(verify_api_key),
) -> APIResponse[list["CircuitBreakerResponse"]]:
    """Get circuit breaker states for all proxies.

    Returns:
        List of circuit breaker states
    """
    from proxywhirl.api_models import CircuitBreakerResponse

    if not _rotator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rotator not initialized",
        )

    circuit_breakers = _rotator.get_circuit_breaker_states()

    responses = []
    for proxy_id, cb in circuit_breakers.items():
        responses.append(
            CircuitBreakerResponse(
                proxy_id=proxy_id,
                state=cb.state.value,
                failure_count=cb.failure_count,
                failure_threshold=cb.failure_threshold,
                window_duration=cb.window_duration,
                timeout_duration=cb.timeout_duration,
                next_test_time=datetime.fromtimestamp(cb.next_test_time, timezone.utc)
                if cb.next_test_time
                else None,
                last_state_change=cb.last_state_change,
            )
        )

    return APIResponse.success(data=responses)


@app.get(
    "/api/v1/circuit-breakers/{proxy_id}",
    response_model=APIResponse["CircuitBreakerResponse"],
    tags=["Retry & Failover"],
    summary="Get circuit breaker state for specific proxy",
)
async def get_circuit_breaker(
    proxy_id: str,
    api_key: None = Depends(verify_api_key),
) -> APIResponse["CircuitBreakerResponse"]:
    """Get circuit breaker state for a specific proxy.

    Args:
        proxy_id: Proxy ID to get circuit breaker for

    Returns:
        Circuit breaker state
    """
    from proxywhirl.api_models import CircuitBreakerResponse

    if not _rotator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rotator not initialized",
        )

    circuit_breakers = _rotator.get_circuit_breaker_states()

    if proxy_id not in circuit_breakers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Circuit breaker not found for proxy: {proxy_id}",
        )

    cb = circuit_breakers[proxy_id]

    response = CircuitBreakerResponse(
        proxy_id=proxy_id,
        state=cb.state.value,
        failure_count=cb.failure_count,
        failure_threshold=cb.failure_threshold,
        window_duration=cb.window_duration,
        timeout_duration=cb.timeout_duration,
        next_test_time=datetime.fromtimestamp(cb.next_test_time, timezone.utc)
        if cb.next_test_time
        else None,
        last_state_change=cb.last_state_change,
    )

    return APIResponse.success(data=response)


@app.post(
    "/api/v1/circuit-breakers/{proxy_id}/reset",
    response_model=APIResponse["CircuitBreakerResponse"],
    tags=["Retry & Failover"],
    summary="Manually reset circuit breaker",
)
async def reset_circuit_breaker(
    proxy_id: str,
    api_key: None = Depends(verify_api_key),
) -> APIResponse["CircuitBreakerResponse"]:
    """Manually reset a circuit breaker to CLOSED state.

    Args:
        proxy_id: Proxy ID whose circuit breaker to reset

    Returns:
        Updated circuit breaker state
    """
    from proxywhirl.api_models import CircuitBreakerResponse

    if not _rotator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rotator not initialized",
        )

    try:
        _rotator.reset_circuit_breaker(proxy_id)

        # Get updated state
        circuit_breakers = _rotator.get_circuit_breaker_states()
        cb = circuit_breakers[proxy_id]

        response = CircuitBreakerResponse(
            proxy_id=proxy_id,
            state=cb.state.value,
            failure_count=cb.failure_count,
            failure_threshold=cb.failure_threshold,
            window_duration=cb.window_duration,
            timeout_duration=cb.timeout_duration,
            next_test_time=datetime.fromtimestamp(cb.next_test_time, timezone.utc)
            if cb.next_test_time
            else None,
            last_state_change=cb.last_state_change,
        )

        return APIResponse.success(data=response)

    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Circuit breaker not found for proxy: {proxy_id}",
        )


@app.get(
    "/api/v1/circuit-breakers/metrics",
    response_model=APIResponse[list["CircuitBreakerEventResponse"]],
    tags=["Retry & Failover"],
    summary="Get circuit breaker metrics",
)
async def get_circuit_breaker_metrics(
    hours: int = 24,
    api_key: None = Depends(verify_api_key),
) -> APIResponse[list["CircuitBreakerEventResponse"]]:
    """Get circuit breaker state change events.

    Args:
        hours: Number of hours to retrieve (default: 24)

    Returns:
        List of circuit breaker events
    """
    from proxywhirl.api_models import CircuitBreakerEventResponse

    if not _rotator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rotator not initialized",
        )

    metrics = _rotator.get_retry_metrics()
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    events = [
        CircuitBreakerEventResponse(
            proxy_id=event.proxy_id,
            from_state=event.from_state.value,
            to_state=event.to_state.value,
            timestamp=event.timestamp,
            failure_count=event.failure_count,
        )
        for event in metrics.circuit_breaker_events
        if event.timestamp >= cutoff
    ]

    return APIResponse.success(data=events)


@app.get(
    "/api/v1/metrics/retries",
    response_model=APIResponse["RetryMetricsResponse"],
    tags=["Retry & Failover"],
    summary="Get retry metrics summary",
)
async def get_retry_metrics(
    api_key: None = Depends(verify_api_key),
) -> APIResponse["RetryMetricsResponse"]:
    """Get aggregated retry metrics.

    Returns:
        Retry metrics summary
    """
    from proxywhirl.api_models import RetryMetricsResponse

    if not _rotator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rotator not initialized",
        )

    metrics = _rotator.get_retry_metrics()
    summary = metrics.get_summary()

    response = RetryMetricsResponse(
        total_retries=summary["total_retries"],
        success_by_attempt={
            str(k): v for k, v in summary["success_by_attempt"].items()
        },
        circuit_breaker_events_count=summary["circuit_breaker_events_count"],
        retention_hours=summary["retention_hours"],
    )

    return APIResponse.success(data=response)


@app.get(
    "/api/v1/metrics/retries/timeseries",
    response_model=APIResponse["TimeSeriesResponse"],
    tags=["Retry & Failover"],
    summary="Get time-series retry data",
)
async def get_retry_timeseries(
    hours: int = 24,
    api_key: None = Depends(verify_api_key),
) -> APIResponse["TimeSeriesResponse"]:
    """Get hourly retry metrics for the specified time range.

    Args:
        hours: Number of hours to retrieve (default: 24)

    Returns:
        Time-series retry data
    """
    from proxywhirl.api_models import TimeSeriesDataPoint, TimeSeriesResponse

    if not _rotator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rotator not initialized",
        )

    metrics = _rotator.get_retry_metrics()
    timeseries_data = metrics.get_timeseries(hours=hours)

    data_points = [
        TimeSeriesDataPoint(
            timestamp=datetime.fromisoformat(point["timestamp"]),
            total_requests=point["total_requests"],
            total_retries=point["total_retries"],
            success_rate=point["success_rate"],
            avg_latency=point["avg_latency"],
        )
        for point in timeseries_data
    ]

    response = TimeSeriesResponse(data_points=data_points)

    return APIResponse.success(data=response)


@app.get(
    "/api/v1/metrics/retries/by-proxy",
    response_model=APIResponse["ProxyRetryStatsResponse"],
    tags=["Retry & Failover"],
    summary="Get per-proxy retry statistics",
)
async def get_retry_stats_by_proxy(
    hours: int = 24,
    api_key: None = Depends(verify_api_key),
) -> APIResponse["ProxyRetryStatsResponse"]:
    """Get retry statistics grouped by proxy.

    Args:
        hours: Number of hours to analyze (default: 24)

    Returns:
        Per-proxy retry statistics
    """
    from proxywhirl.api_models import ProxyRetryStats, ProxyRetryStatsResponse

    if not _rotator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rotator not initialized",
        )

    metrics = _rotator.get_retry_metrics()
    stats_by_proxy = metrics.get_by_proxy(hours=hours)

    proxies = {
        proxy_id: ProxyRetryStats(**stats)
        for proxy_id, stats in stats_by_proxy.items()
    }

    response = ProxyRetryStatsResponse(proxies=proxies)

    return APIResponse.success(data=response)
