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

from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional, Any
import os

from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.errors import ServerErrorMiddleware
from loguru import logger

from proxywhirl.rotator import ProxyRotator
from proxywhirl.storage import SQLiteStorage
from proxywhirl.api_models import APIResponse, ErrorCode, ErrorDetail
from proxywhirl.exceptions import ProxyError


# Global singleton instances
_rotator: Optional[ProxyRotator] = None
_storage: Optional[SQLiteStorage] = None
_config: dict[str, Any] = {}


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
    _rotator = ProxyRotator(storage=_storage)
    
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
        _storage.save_proxies(_rotator.proxies)
    
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
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


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
        content=response.model_dump(),
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
        content=response.model_dump(),
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
        content=response.model_dump(),
    )


@app.exception_handler(ProxyError)
async def proxy_error_handler(request: Request, exc: ProxyError) -> JSONResponse:
    """Handle ProxyError exceptions."""
    response: APIResponse[None] = APIResponse.error_response(
        code=ErrorCode.PROXY_ERROR,
        message=str(exc),
        details={"error_type": type(exc).__name__},
    )
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content=response.model_dump(),
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
