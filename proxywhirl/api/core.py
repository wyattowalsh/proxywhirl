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

# ruff: noqa: B008

from __future__ import annotations

import asyncio
import hashlib
import os
import secrets
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from loguru import logger
from prometheus_client import REGISTRY, Counter, Gauge, Histogram, generate_latest
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from proxywhirl.api.models import (
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
from proxywhirl.utils import validate_target_url_safe


def _parse_int_env(name: str, default: int) -> int:
    """Parse an integer environment variable with validation.

    Args:
        name: Environment variable name
        default: Default value if not set

    Returns:
        Parsed integer value

    Raises:
        ValueError: If value is set but not a valid integer
    """
    value = os.getenv(name)
    if value is None:
        return default

    try:
        return int(value)
    except ValueError as e:
        raise ValueError(f"Environment variable {name} must be an integer, got '{value}'") from e


def _parse_float_env(name: str, default: float) -> float:
    """Parse a float environment variable with validation.

    Args:
        name: Environment variable name
        default: Default value if not set

    Returns:
        Parsed float value

    Raises:
        ValueError: If value is set but not a valid float
    """
    value = os.getenv(name)
    if value is None:
        return default

    try:
        return float(value)
    except ValueError as e:
        raise ValueError(f"Environment variable {name} must be a number, got '{value}'") from e


# Global singleton instances
_rotator: ProxyRotator | None = None
_storage: SQLiteStorage | None = None
_config: dict[str, Any] = {}

# Track app start time for uptime calculation
_app_start_time = datetime.now(timezone.utc)

# Track last rotation time (updated on each proxy selection)
_last_rotation_time: datetime | None = None
_last_rotation_lock = asyncio.Lock()


# =============================================================================
# Helper Functions
# =============================================================================


def _get_proxy_id(proxy: Any) -> str:
    """Get stable identifier for a proxy.

    Uses proxy.id if available, otherwise generates a hash from the URL.
    This ensures IDs remain stable across application restarts.

    Args:
        proxy: Proxy instance

    Returns:
        Stable string identifier for the proxy
    """
    # Try to get proxy.id safely using getattr
    proxy_id = getattr(proxy, "id", None)
    if proxy_id:
        return str(proxy_id)
    # Fallback: hash of URL for stability
    return hashlib.sha256(str(proxy.url).encode()).hexdigest()[:16]


# =============================================================================
# Prometheus Metrics
# =============================================================================

# Request metrics
proxywhirl_requests_total = Counter(
    "proxywhirl_requests_total",
    "Total number of HTTP requests",
    ["endpoint", "method", "status"],
)

proxywhirl_request_duration_seconds = Histogram(
    "proxywhirl_request_duration_seconds",
    "HTTP request duration in seconds",
    ["endpoint", "method"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0),
)

# Proxy pool metrics
proxywhirl_proxies_total = Gauge(
    "proxywhirl_proxies_total",
    "Total number of proxies in the pool",
)

proxywhirl_proxies_healthy = Gauge(
    "proxywhirl_proxies_healthy",
    "Number of healthy proxies in the pool",
)

# Circuit breaker metrics
proxywhirl_circuit_breaker_state = Gauge(
    "proxywhirl_circuit_breaker_state",
    "Circuit breaker state (0=closed, 1=open, 2=half-open)",
    ["proxy_id"],
)


# =============================================================================
# Rate Limiting - Per-API-Key Strategy
# =============================================================================


def get_rate_limit_key(request: Request) -> str:
    """Extract rate limit key from request.

    SECURITY: This function is designed to prevent rate limit bypass attacks.

    For authenticated requests (with API key):
        - Uses hashed API key as rate limit key
        - This ensures rate limiting is per-API-key, not per-IP

    For unauthenticated requests:
        - Uses ONLY direct client IP (request.client.host)
        - NEVER trusts X-Forwarded-For header to prevent spoofing attacks
        - Attackers cannot bypass rate limits by sending fake X-Forwarded-For headers

    Note: If you need to trust X-Forwarded-For (e.g., behind a reverse proxy),
    configure your reverse proxy to set the real client IP in request.client,
    or use a trusted proxy middleware that validates the header chain.

    Args:
        request: FastAPI Request object

    Returns:
        Rate limit key in format "apikey:{hash}" or "ip:{address}"
    """
    # Check for API key first (primary identifier for authenticated requests)
    api_key = request.headers.get("X-API-Key")
    if api_key:
        # Hash the API key to avoid exposing it in logs
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
        return f"apikey:{key_hash}"

    # SECURITY: For unauthenticated requests, use direct client IP only.
    # NEVER trust X-Forwarded-For header as it can be spoofed by attackers
    # to bypass rate limits.
    client_ip = request.client.host if request.client else "unknown"
    return f"ip:{client_ip}"


# Rate limiter configuration
# Use per-API-key rate limiting to prevent X-Forwarded-For bypass
# Default limit can be overridden via environment variables
_default_rate_limit = os.getenv("PROXYWHIRL_RATE_LIMIT", "100/minute")
_api_key_rate_limit = os.getenv("PROXYWHIRL_API_KEY_RATE_LIMIT", _default_rate_limit)

limiter = Limiter(key_func=get_rate_limit_key, default_limits=[_default_rate_limit])


# API key authentication (optional)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str | None = Depends(api_key_header)) -> None:
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
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API authentication not configured",
        )

    if not api_key or not secrets.compare_digest(api_key, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


def validate_proxied_request_url(request_data: ProxiedRequest) -> ProxiedRequest:
    """Dependency to validate target URL for SSRF protection.

    This dependency runs BEFORE other dependencies to ensure SSRF validation
    happens first, preventing malicious URLs from being processed.

    Args:
        request_data: The proxied request data

    Returns:
        The validated request data

    Raises:
        HTTPException: If URL is invalid or blocked for security reasons
    """
    try:
        validate_target_url_safe(str(request_data.url), allow_private=False)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    return request_data


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
    cors_origins_raw = os.getenv(
        "PROXYWHIRL_CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000"
    )
    cors_origins_config = [
        origin.strip()
        for origin in cors_origins_raw.split(",")
        if origin.strip()  # Filter empty strings from trailing commas or double commas
    ]
    _config = {
        "rotation_strategy": os.getenv("PROXYWHIRL_STRATEGY", "round-robin"),
        "timeout": _parse_int_env("PROXYWHIRL_TIMEOUT", 30),
        "max_retries": _parse_int_env("PROXYWHIRL_MAX_RETRIES", 3),
        "rate_limits": {
            "default_limit": 100,
            "request_endpoint_limit": 50,
        },
        "auth_enabled": os.getenv("PROXYWHIRL_REQUIRE_AUTH", "false").lower() == "true",
        "cors_origins": cors_origins_config,
    }

    logger.info("ProxyWhirl API initialized successfully")

    yield

    # Shutdown
    logger.info("Shutting down ProxyWhirl API...")

    # Save state if storage configured
    if _storage and _rotator:
        logger.info("Saving proxy pool state...")
        # Use thread-safe snapshot for saving
        await _storage.save(_rotator.pool.get_all_proxies())

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
cors_origins_raw = os.getenv(
    "PROXYWHIRL_CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000"
)
cors_origins = [
    origin.strip()
    for origin in cors_origins_raw.split(",")
    if origin.strip()  # Filter empty strings from trailing commas or double commas
]

# Security: Validate CORS configuration
# SEC-003: Wildcard CORS with credentials is a security vulnerability (CVE-like)
# The browser will reject `Access-Control-Allow-Origin: *` with credentials anyway,
# but we enforce safe defaults at the application level.
allow_credentials = True

# Validate: wildcard origins + credentials = error
if "*" in cors_origins and allow_credentials:
    error_msg = (
        "CORS configuration error: cannot use wildcard origin ('*') "
        "with allow_credentials=True. This violates CORS security policy. "
        "Either: 1) Set specific PROXYWHIRL_CORS_ORIGINS, "
        "or 2) Use '*' only for public APIs without credentials."
    )
    logger.error(error_msg)
    raise ValueError(error_msg)

# Default to no CORS if wildcard is explicitly set (fail-safe)
if "*" in cors_origins:
    logger.warning(
        "CORS is configured to allow all origins (*). "
        "This is insecure and should only be used in development. "
        "Set PROXYWHIRL_CORS_ORIGINS to specific origins for production."
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next: Any) -> Any:
        response = await call_next(request)
        # Basic security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # HSTS - enforce HTTPS with 1-year max-age
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        # CSP - restrict resource loading to same origin, prevent framing
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"
        # Referrer-Policy - send origin only on cross-origin requests
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Permissions-Policy - disable sensitive browser features
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response


# Request ID middleware for request tracing
class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add request ID correlation for request tracing.

    This middleware ensures every request has a unique identifier that can be
    used for tracing requests through the retry/cache/circuit-breaker chain.

    The request ID is:
    - Taken from the X-Request-ID header if provided by the client
    - Generated as a new UUID v4 if not provided
    - Added to loguru context for all downstream logging
    - Included in the response X-Request-ID header
    """

    async def dispatch(self, request: Request, call_next: Any) -> Any:
        """Process request and add request ID correlation."""
        # Use existing header or generate new UUID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Add to loguru context for all downstream logging
        with logger.contextualize(request_id=request_id):
            response = await call_next(request)

        # Include in response headers
        response.headers["X-Request-ID"] = request_id
        return response


# Audit logging middleware for security-sensitive operations
class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """Structured audit logging for API operations.

    Provides security audit trail including:
    - Authentication context (API key used, redacted)
    - Operation classification (read, write, admin, auth)
    - Resource identification for mutating operations
    - Request body logging for writes (with sensitive data redaction)

    All logs use structured JSON format for easy parsing by SIEM tools.
    """

    # Paths that require audit logging
    AUDIT_PATHS = {
        # Admin/config operations
        "/api/v1/config": "admin",
        # Write operations
        "/api/v1/proxies": "write",
        "/api/v1/request": "write",
        # Auth-related
        "/api/v1/auth": "auth",
    }

    # Sensitive fields to redact in request bodies
    SENSITIVE_FIELDS = frozenset(
        {
            "password",
            "api_key",
            "apikey",
            "api-key",
            "secret",
            "token",
            "auth",
            "authorization",
            "credential",
            "key",
        }
    )

    def _get_operation_type(self, method: str, path: str) -> str:
        """Classify the operation type for audit purposes."""
        # Check specific paths first
        for audit_path, op_type in self.AUDIT_PATHS.items():
            if path.startswith(audit_path):
                if method in ("POST", "PUT", "PATCH", "DELETE"):
                    return op_type
                return "read"

        # Default classification by method
        if method in ("POST", "PUT", "PATCH", "DELETE"):
            return "write"
        return "read"

    def _redact_api_key(self, api_key: str | None) -> str:
        """Redact API key for safe logging (show first/last 4 chars)."""
        if not api_key:
            return "none"
        if len(api_key) <= 8:
            return "***"
        return f"{api_key[:4]}...{api_key[-4:]}"

    def _redact_body(self, body: dict[str, Any]) -> dict[str, Any]:
        """Recursively redact sensitive fields in request body."""
        redacted = {}
        for key, value in body.items():
            if key.lower() in self.SENSITIVE_FIELDS:
                redacted[key] = "***REDACTED***"
            elif isinstance(value, dict):
                redacted[key] = self._redact_body(value)
            elif isinstance(value, list):
                redacted[key] = [self._redact_body(v) if isinstance(v, dict) else v for v in value]
            else:
                redacted[key] = value
        return redacted

    async def dispatch(self, request: Request, call_next: Any) -> Any:
        """Process request and emit audit log for sensitive operations."""
        # Check if audit logging is enabled via environment variable
        audit_enabled = os.getenv("PROXYWHIRL_AUDIT_LOG", "true").lower() == "true"
        if not audit_enabled:
            return await call_next(request)

        path = str(request.url.path)
        method = request.method

        # Skip audit logging for non-API paths and GET requests to non-sensitive endpoints
        if not path.startswith("/api/"):
            return await call_next(request)

        operation_type = self._get_operation_type(method, path)

        # Only audit write/admin/auth operations
        if operation_type == "read":
            return await call_next(request)

        # Extract audit context
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()

        api_key = request.headers.get("X-API-Key")
        request_id = request.headers.get("X-Request-ID", "unknown")

        # Try to capture request body for mutating operations
        body_summary = None
        if method in ("POST", "PUT", "PATCH"):
            try:
                body_bytes = await request.body()
                if body_bytes:
                    import json

                    body = json.loads(body_bytes)
                    body_summary = self._redact_body(body)
            except Exception:
                body_summary = {"_parse_error": "Could not parse request body"}

        # Emit audit log before processing
        logger.bind(
            event="audit",
            audit_type="api_request",
            operation=operation_type,
            method=method,
            path=path,
            client_ip=client_ip,
            api_key_used=self._redact_api_key(api_key),
            request_id=request_id,
            body_summary=body_summary,
        ).info(f"AUDIT: {operation_type.upper()} operation {method} {path}")

        # Process request
        response = await call_next(request)

        # Log outcome for write operations
        if response.status_code >= 400:
            logger.bind(
                event="audit",
                audit_type="api_response",
                operation=operation_type,
                method=method,
                path=path,
                client_ip=client_ip,
                request_id=request_id,
                status_code=response.status_code,
                success=False,
            ).warning(f"AUDIT: {operation_type.upper()} operation failed: {response.status_code}")
        else:
            logger.bind(
                event="audit",
                audit_type="api_response",
                operation=operation_type,
                method=method,
                path=path,
                request_id=request_id,
                status_code=response.status_code,
                success=True,
            ).info(f"AUDIT: {operation_type.upper()} operation succeeded: {response.status_code}")

        return response


# Request logging middleware
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all HTTP requests with structured JSON logging.

    Logs:
    - Request method, path, and query parameters (redacted)
    - Client IP address
    - Request duration in milliseconds
    - Response status code
    - Sensitive data redaction (passwords, tokens, API keys)
    """

    async def dispatch(self, request: Request, call_next: Any) -> Any:
        """Process request and log details."""
        start_time = time.time()

        # Extract client IP
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain (original client)
            client_ip = forwarded_for.split(",")[0].strip()

        # Redact sensitive information from URL
        path = str(request.url.path)
        query_string = str(request.url.query) if request.url.query else ""
        if query_string:
            # Redact sensitive query parameters
            import re

            query_string = re.sub(
                r"(password|token|key|secret|auth|api_key|api-key)=[^&]*",
                r"\1=***",
                query_string,
                flags=re.IGNORECASE,
            )
            full_path = f"{path}?{query_string}"
        else:
            full_path = path

        # Log request start
        logger.bind(
            event="request_start",
            method=request.method,
            path=full_path,
            client_ip=client_ip,
            user_agent=request.headers.get("User-Agent", "unknown"),
        ).debug("HTTP request started")

        # Process request
        try:
            response = await call_next(request)
            duration_ms = int((time.time() - start_time) * 1000)
            duration_seconds = time.time() - start_time

            # Record Prometheus metrics (skip /metrics endpoint to avoid recursion)
            if path != "/metrics":
                proxywhirl_requests_total.labels(
                    endpoint=path,
                    method=request.method,
                    status=str(response.status_code),
                ).inc()

                proxywhirl_request_duration_seconds.labels(
                    endpoint=path,
                    method=request.method,
                ).observe(duration_seconds)

            # Log successful request
            logger.bind(
                event="request_complete",
                method=request.method,
                path=full_path,
                client_ip=client_ip,
                status_code=response.status_code,
                duration_ms=duration_ms,
            ).info(f"{request.method} {path} - {response.status_code} ({duration_ms}ms)")

            return response

        except Exception as exc:
            duration_ms = int((time.time() - start_time) * 1000)
            duration_seconds = time.time() - start_time

            # Record Prometheus metrics for failed requests (skip /metrics endpoint)
            if path != "/metrics":
                # Use 5xx for uncaught exceptions
                proxywhirl_requests_total.labels(
                    endpoint=path,
                    method=request.method,
                    status="500",
                ).inc()

                proxywhirl_request_duration_seconds.labels(
                    endpoint=path,
                    method=request.method,
                ).observe(duration_seconds)

            # Log failed request
            logger.bind(
                event="request_failed",
                method=request.method,
                path=full_path,
                client_ip=client_ip,
                duration_ms=duration_ms,
                error_type=type(exc).__name__,
                error_message=str(exc),
            ).error(f"{request.method} {path} - Failed ({duration_ms}ms): {exc}")

            # Re-raise to let FastAPI handle it
            raise


app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(AuditLoggingMiddleware)  # Runs first (added last)


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
    """Handle 422 Validation errors.

    Returns 400 Bad Request for client input validation failures,
    which is more semantically appropriate than 422 Unprocessable Entity.
    """
    # Extract validation errors and make them more user-friendly
    errors = exc.errors() if hasattr(exc, "errors") else [{"msg": str(exc)}]

    # Format error messages to be more helpful
    formatted_errors = []
    for error in errors:
        field = " -> ".join(str(loc) for loc in error.get("loc", []))
        message = error.get("msg", "Validation failed")

        # Extract the actual error message from ValueError if present
        if "Value error," in message:
            message = message.split("Value error,", 1)[1].strip()

        formatted_errors.append(
            {
                "field": field,
                "message": message,
                "type": error.get("type", "validation_error"),
            }
        )

    response: APIResponse[None] = APIResponse.error_response(
        code=ErrorCode.VALIDATION_ERROR,
        message="Request validation failed. Please check your input and try again.",
        details={"errors": formatted_errors},
    )

    # Return 400 Bad Request instead of 422 for better HTTP semantics
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
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
    """Handle ProxyWhirlError exceptions with enhanced error details."""
    # Log the error with full context
    logger.bind(
        error_code=exc.error_code.value if hasattr(exc, "error_code") else "UNKNOWN",
        error_type=type(exc).__name__,
        proxy_url=exc.proxy_url if hasattr(exc, "proxy_url") else None,
        attempt_count=exc.attempt_count if hasattr(exc, "attempt_count") else None,
        retry_recommended=exc.retry_recommended if hasattr(exc, "retry_recommended") else False,
    ).error(f"Proxy error: {exc}")

    # Determine HTTP status code based on error type
    status_code_map = {
        "ProxyPoolEmptyError": status.HTTP_503_SERVICE_UNAVAILABLE,
        "ProxyValidationError": status.HTTP_400_BAD_REQUEST,
        "ProxyAuthenticationError": status.HTTP_502_BAD_GATEWAY,
        "ProxyConnectionError": status.HTTP_502_BAD_GATEWAY,
        "ProxyFetchError": status.HTTP_503_SERVICE_UNAVAILABLE,
        "ProxyStorageError": status.HTTP_500_INTERNAL_SERVER_ERROR,
    }

    http_status = status_code_map.get(type(exc).__name__, status.HTTP_502_BAD_GATEWAY)

    # Build error response with enhanced details
    error_details = {
        "error_type": type(exc).__name__,
        "error_code": exc.error_code.value if hasattr(exc, "error_code") else "UNKNOWN",
        "retry_recommended": exc.retry_recommended if hasattr(exc, "retry_recommended") else False,
    }

    # Add attempt count if available
    if hasattr(exc, "attempt_count") and exc.attempt_count is not None:
        error_details["attempt_count"] = exc.attempt_count

    # Add additional metadata if available
    if hasattr(exc, "metadata") and exc.metadata:
        error_details.update(exc.metadata)

    response: APIResponse[None] = APIResponse.error_response(
        code=ErrorCode.PROXY_ERROR,
        message=str(exc),
        details=error_details,
    )
    return JSONResponse(
        status_code=http_status,
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


def get_storage() -> SQLiteStorage | None:
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


def update_prometheus_metrics() -> None:
    """Update Prometheus metrics for proxy pool and circuit breakers."""
    if not _rotator:
        return

    # Update proxy pool metrics (use thread-safe method)
    total_proxies = _rotator.pool.size
    proxywhirl_proxies_total.set(total_proxies)

    # Calculate healthy proxies based on actual health status
    healthy_proxies = _rotator.pool.healthy_count
    proxywhirl_proxies_healthy.set(healthy_proxies)

    # Update circuit breaker metrics
    try:
        circuit_breakers = _rotator.get_circuit_breaker_states()
        for proxy_id, cb in circuit_breakers.items():
            # Map circuit breaker state to numeric value
            # 0=CLOSED, 1=OPEN, 2=HALF_OPEN
            state_value = 0
            if cb.state.value == "OPEN":
                state_value = 1
            elif cb.state.value == "HALF_OPEN":
                state_value = 2

            proxywhirl_circuit_breaker_state.labels(proxy_id=proxy_id).set(state_value)
    except Exception as e:
        logger.warning(f"Failed to update circuit breaker metrics: {e}")


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
# Prometheus Metrics Endpoint
# =============================================================================


@app.get(
    "/metrics",
    tags=["Monitoring"],
    summary="Prometheus metrics endpoint",
    response_class=Response,
    include_in_schema=False,
)
async def metrics() -> Response:
    """Expose Prometheus metrics in text format.

    This endpoint returns metrics in Prometheus exposition format, including:
    - proxywhirl_requests_total: Total HTTP requests by endpoint, method, and status
    - proxywhirl_request_duration_seconds: Request duration histogram
    - proxywhirl_proxies_total: Total proxies in pool
    - proxywhirl_proxies_healthy: Number of healthy proxies
    - proxywhirl_circuit_breaker_state: Circuit breaker states (0=closed, 1=open, 2=half-open)

    Returns:
        Prometheus metrics in text format
    """
    # Update proxy pool and circuit breaker metrics before returning
    update_prometheus_metrics()

    # Generate Prometheus text format
    metrics_output = generate_latest(REGISTRY)

    return Response(
        content=metrics_output,
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


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
    request: Request,
    request_data: ProxiedRequest = Depends(validate_proxied_request_url),
    rotator: ProxyRotator = Depends(get_rotator),
    api_key: None = Depends(verify_api_key),
) -> APIResponse[ProxiedResponse]:
    """Make an HTTP request through a rotating proxy.

    This endpoint routes your HTTP request through the proxy pool, automatically
    handling rotation and failover.

    SECURITY: All target URLs are validated to prevent SSRF attacks. The following
    are blocked by default:
    - Localhost and loopback addresses (127.0.0.0/8, ::1)
    - Private IP ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
    - Link-local addresses (169.254.0.0/16)
    - Internal domain names (.local, .internal, .lan, .corp)
    - Non-HTTP/HTTPS schemes (file://, data://, etc.)

    Args:
        request_data: Request details (URL, method, headers, body, timeout) - validated for SSRF
        rotator: ProxyRotator dependency injection
        api_key: API key verification dependency

    Returns:
        APIResponse with proxied response data

    Raises:
        HTTPException: For various error conditions including SSRF protection
    """

    global _last_rotation_time

    start_time = time.time()
    max_retries = 3
    last_error: Exception | None = None

    for attempt in range(max_retries):
        try:
            # Get next proxy from rotator using strategy
            proxy = rotator.strategy.select(rotator.pool)
            if not proxy:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="No proxies available in the pool",
                )

            # Track last rotation time
            _last_rotation_time = datetime.now(timezone.utc)

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
            ) from e

        except Exception as e:
            logger.error(f"Unexpected error in proxied request: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error: {str(e)}",
            ) from e

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
    status_filter: str | None = None,
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

    # Get all proxies (thread-safe snapshot)
    all_proxies = rotator.pool.get_all_proxies()

    # Apply status filter if provided
    if status_filter:
        status_lower = status_filter.lower()
        if status_lower == "healthy":
            all_proxies = [p for p in all_proxies if p.is_healthy]
        elif status_lower == "unhealthy":
            all_proxies = [p for p in all_proxies if not p.is_healthy]
        elif status_lower == "active":
            # Active means proxy is available (not in a failed circuit breaker state)
            circuit_breakers = rotator.get_circuit_breaker_states()
            all_proxies = [
                p
                for p in all_proxies
                if _get_proxy_id(p) not in circuit_breakers
                or circuit_breakers[_get_proxy_id(p)].state.value != "OPEN"
            ]

    # Calculate pagination
    total = len(all_proxies)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_proxies = all_proxies[start_idx:end_idx]

    # Convert to ProxyResource models
    proxy_resources = []
    circuit_breakers = rotator.get_circuit_breaker_states()
    for proxy in page_proxies:
        proxy_id = _get_proxy_id(proxy)
        cb = circuit_breakers.get(proxy_id)

        # Determine status based on circuit breaker state
        if cb and cb.state.value == "OPEN":
            proxy_status = "failed"
        elif cb and cb.state.value == "HALF_OPEN":
            proxy_status = "degraded"
        else:
            proxy_status = "active"

        # Map health status to string
        health_value = proxy.health_status.value if proxy.health_status else "unknown"

        resource = ProxyResource(
            id=proxy_id,
            url=str(proxy.url),
            protocol=proxy.protocol or "http",
            status=proxy_status,
            health=health_value,
            stats={
                "total_requests": proxy.requests_started,
                "successful_requests": proxy.requests_completed,
                "failed_requests": proxy.total_failures,
                "avg_latency_ms": int(proxy.average_response_time_ms or 0),
            },
            created_at=proxy.created_at,
            updated_at=proxy.updated_at,
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
@limiter.limit("10/minute")
async def add_proxy(
    request: Request,
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

    # Check for duplicate (thread-safe snapshot)
    proxy_url_str = str(proxy_data.url)
    for existing_proxy in rotator.pool.get_all_proxies():
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
        proxy_id = _get_proxy_id(new_proxy)
        health_value = new_proxy.health_status.value if new_proxy.health_status else "unknown"

        resource = ProxyResource(
            id=proxy_id,
            url=str(new_proxy.url),
            protocol=new_proxy.protocol or "http",
            status="active",
            health=health_value,
            stats={
                "total_requests": new_proxy.requests_started,
                "successful_requests": new_proxy.requests_completed,
                "failed_requests": new_proxy.total_failures,
                "avg_latency_ms": int(new_proxy.average_response_time_ms or 0),
            },
            created_at=new_proxy.created_at,
            updated_at=new_proxy.updated_at,
        )

        return APIResponse.success(data=resource)

    except Exception as e:
        logger.error(f"Error adding proxy: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid proxy: {str(e)}",
        ) from e


async def _check_proxy_health(
    proxy: Any,
    test_url: str,
    timeout: float = 10.0,
) -> HealthCheckResult:
    """Check health of a single proxy.

    Args:
        proxy: Proxy instance to check
        test_url: URL to use for health check
        timeout: Request timeout in seconds

    Returns:
        HealthCheckResult with test outcome

    Note:
        Each proxy check creates its own client since httpx requires
        proxy configuration at client instantiation time.
    """
    start_time = time.time()
    try:
        # Create client with proxy configuration
        # Note: httpx requires proxy to be set at client creation time
        async with httpx.AsyncClient(
            proxy=str(proxy.url),
            timeout=timeout,
        ) as client:
            response = await client.get(test_url)

        latency_ms = int((time.time() - start_time) * 1000)

        return HealthCheckResult(
            proxy_id=_get_proxy_id(proxy),
            status="working" if response.status_code == 200 else "failed",
            latency_ms=latency_ms,
            error=None,
            tested_at=datetime.now(timezone.utc),
        )
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        return HealthCheckResult(
            proxy_id=_get_proxy_id(proxy),
            status="failed",
            latency_ms=latency_ms,
            error=str(e),
            tested_at=datetime.now(timezone.utc),
        )


@app.post(
    "/api/v1/proxies/health-check",
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
    # Determine which proxies to check (thread-safe snapshot)
    all_proxies = rotator.pool.get_all_proxies()
    proxies_to_check = all_proxies
    if request_data.proxy_ids:
        proxies_to_check = [p for p in all_proxies if _get_proxy_id(p) in request_data.proxy_ids]

    test_url = "https://httpbin.org/get"

    # Run health checks concurrently
    # Note: Each proxy check creates its own client since httpx requires
    # proxy configuration at client instantiation time (not per-request)
    tasks = [_check_proxy_health(proxy, test_url) for proxy in proxies_to_check]
    results = await asyncio.gather(*tasks, return_exceptions=False)

    return APIResponse.success(data=results)


# Deprecated - kept for backward compatibility
@app.post(
    "/api/v1/proxies/test",
    response_model=APIResponse[list[HealthCheckResult]],
    tags=["Pool Management"],
    summary="Health check proxies (deprecated)",
    deprecated=True,
)
async def health_check_proxies_deprecated(
    request_data: HealthCheckRequest,
    rotator: ProxyRotator = Depends(get_rotator),
    api_key: None = Depends(verify_api_key),
) -> APIResponse[list[HealthCheckResult]]:
    """Run health checks on specified proxies.

    **DEPRECATED:** Use `/api/v1/proxies/health-check` instead.
    This endpoint is kept for backward compatibility and will be removed in a future version.

    Args:
        request_data: Optional list of proxy IDs to check
        rotator: ProxyRotator dependency
        api_key: API key verification

    Returns:
        List of health check results
    """
    logger.warning(
        "Deprecated endpoint used: POST /api/v1/proxies/test. "
        "Please migrate to /api/v1/proxies/health-check"
    )
    return await health_check_proxies(request_data, rotator, api_key)


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
    # Find proxy by ID (thread-safe snapshot)
    circuit_breakers = rotator.get_circuit_breaker_states()
    for proxy in rotator.pool.get_all_proxies():
        if _get_proxy_id(proxy) == proxy_id:
            cb = circuit_breakers.get(proxy_id)

            # Determine status based on circuit breaker state
            if cb and cb.state.value == "OPEN":
                proxy_status = "failed"
            elif cb and cb.state.value == "HALF_OPEN":
                proxy_status = "degraded"
            else:
                proxy_status = "active"

            # Map health status to string
            health_value = proxy.health_status.value if proxy.health_status else "unknown"

            resource = ProxyResource(
                id=proxy_id,
                url=str(proxy.url),
                protocol=proxy.protocol or "http",
                status=proxy_status,
                health=health_value,
                stats={
                    "total_requests": proxy.requests_started,
                    "successful_requests": proxy.requests_completed,
                    "failed_requests": proxy.total_failures,
                    "avg_latency_ms": int(proxy.average_response_time_ms or 0),
                },
                created_at=proxy.created_at,
                updated_at=proxy.updated_at,
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
    storage: SQLiteStorage | None = Depends(get_storage),
    api_key: None = Depends(verify_api_key),
) -> None:
    """Remove a proxy from the pool.

    Args:
        proxy_id: Proxy identifier
        rotator: ProxyRotator dependency
        storage: Optional storage dependency
        api_key: API key verification
    """
    # Find and remove proxy (thread-safe)
    # First find the proxy by ID
    target_proxy = None
    for proxy in rotator.pool.get_all_proxies():
        if _get_proxy_id(proxy) == proxy_id:
            target_proxy = proxy
            break

    if target_proxy:
        # Use thread-safe remove method
        rotator.pool.remove_proxy(target_proxy.id)

        # Persist if storage configured
        if storage:
            await storage.save(rotator.pool.get_all_proxies())

        return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Proxy not found: {proxy_id}",
    )


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

    # Determine health based on proxy pool (use thread-safe property)
    total_proxies = rotator.pool.size
    if total_proxies == 0:
        health_status: Literal["healthy", "degraded", "unhealthy"] = "unhealthy"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        # Check actual health of proxies
        healthy_proxies = rotator.pool.healthy_count
        unhealthy_proxies = rotator.pool.unhealthy_count

        if healthy_proxies == 0:
            health_status = "unhealthy"
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        elif unhealthy_proxies > healthy_proxies:
            health_status = "degraded"
            status_code = status.HTTP_200_OK
        else:
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
    storage: SQLiteStorage | None = Depends(get_storage),
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
    storage: SQLiteStorage | None = Depends(get_storage),
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
    from proxywhirl.api.models import ProxyPoolStats

    # Use thread-safe property
    total = rotator.pool.size
    # Calculate active/failed based on circuit breaker states and health checks
    circuit_breakers = rotator.get_circuit_breaker_states()
    failed = sum(1 for cb in circuit_breakers.values() if cb.state.value == "OPEN")
    healthy = rotator.pool.healthy_count
    active = total - failed
    healthy_percentage = (healthy / total * 100) if total > 0 else 0.0

    pool_stats = ProxyPoolStats(
        total=total,
        active=active,
        failed=failed,
        healthy_percentage=healthy_percentage,
        last_rotation=_last_rotation_time,
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
    "/api/v1/stats",
    response_model=APIResponse[MetricsResponse],
    tags=["Monitoring"],
    summary="Get performance statistics",
)
async def get_stats(
    rotator: ProxyRotator = Depends(get_rotator),
) -> APIResponse[MetricsResponse]:
    """Get API performance statistics (general aggregate metrics).

    This endpoint provides high-level performance statistics for the API,
    distinct from the detailed Prometheus metrics available at /metrics.

    Args:
        rotator: ProxyRotator dependency

    Returns:
        Performance statistics response

    Note:
        This endpoint provides aggregate metrics. For detailed metrics, use:
        - /metrics - Prometheus format metrics
        - /api/v1/metrics/retries - Retry-specific metrics
        - /metrics/retry - Comprehensive retry metrics with JSON/Prometheus format
    """
    from proxywhirl.api.models import ProxyStats

    # Calculate aggregate metrics from all proxies (thread-safe snapshot)
    all_proxies = rotator.pool.get_all_proxies()
    total_requests = sum(p.requests_started for p in all_proxies)
    total_completed = sum(p.requests_completed for p in all_proxies)
    total_failed = sum(p.total_failures for p in all_proxies)

    # Calculate overall error rate
    error_rate = (total_failed / total_requests * 100) if total_requests > 0 else 0.0

    # Calculate weighted average latency (average_response_time_ms is already in ms)
    total_latency_weighted = sum(
        (p.average_response_time_ms or 0) * p.requests_completed
        for p in all_proxies
        if p.average_response_time_ms
    )
    avg_latency_ms = total_latency_weighted / total_completed if total_completed > 0 else 0.0

    # Calculate requests per second based on uptime
    uptime_seconds = (datetime.now(timezone.utc) - _app_start_time).total_seconds()
    requests_per_second = total_requests / uptime_seconds if uptime_seconds > 0 else 0.0

    # Build per-proxy stats
    proxy_stats_list = []
    for proxy in all_proxies:
        proxy_stats_list.append(
            ProxyStats(
                proxy_id=_get_proxy_id(proxy),
                requests=proxy.requests_started,
                successes=proxy.requests_completed,
                failures=proxy.total_failures,
                avg_latency_ms=int(proxy.average_response_time_ms or 0),
            )
        )

    metrics_response = MetricsResponse(
        requests_total=total_requests,
        requests_per_second=round(requests_per_second, 2),
        avg_latency_ms=round(avg_latency_ms, 2),
        error_rate=round(error_rate, 2),
        proxy_stats=proxy_stats_list,
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
    from proxywhirl.api.models import RateLimitConfig

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
@limiter.limit("5/minute")
async def update_configuration(
    request: Request,
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
    from proxywhirl.api.models import RateLimitConfig

    # Apply updates
    if update_data.rotation_strategy is not None:
        config["rotation_strategy"] = update_data.rotation_strategy
        # Update rotator strategy dynamically using hot-swap
        try:
            rotator.set_strategy(update_data.rotation_strategy, atomic=True)
            logger.info(f"Rotation strategy updated to: {update_data.rotation_strategy}")
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid rotation strategy: {str(e)}",
            ) from e

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
) -> APIResponse[RetryPolicyResponse]:
    """Get the current global retry policy configuration.

    Returns:
        Current retry policy settings
    """
    from proxywhirl.api.models import RetryPolicyResponse

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
    policy_request: RetryPolicyRequest,
    api_key: None = Depends(verify_api_key),
) -> APIResponse[RetryPolicyResponse]:
    """Update the global retry policy configuration.

    Args:
        policy_request: New retry policy settings

    Returns:
        Updated retry policy
    """
    from proxywhirl.api.models import RetryPolicyResponse
    from proxywhirl.retry import BackoffStrategy, RetryPolicy

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
        ) from e


@app.get(
    "/api/v1/circuit-breakers",
    response_model=APIResponse[list["CircuitBreakerResponse"]],
    tags=["Retry & Failover"],
    summary="List all circuit breaker states",
)
async def list_circuit_breakers(
    api_key: None = Depends(verify_api_key),
) -> APIResponse[list[CircuitBreakerResponse]]:
    """Get circuit breaker states for all proxies.

    Returns:
        List of circuit breaker states
    """
    from proxywhirl.api.models import CircuitBreakerResponse

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
    "/api/v1/circuit-breakers/metrics",
    response_model=APIResponse[list["CircuitBreakerEventResponse"]],
    tags=["Retry & Failover"],
    summary="Get circuit breaker metrics",
)
async def get_circuit_breaker_metrics(
    hours: int = 24,
    api_key: None = Depends(verify_api_key),
) -> APIResponse[list[CircuitBreakerEventResponse]]:
    """Get circuit breaker state change events.

    Args:
        hours: Number of hours to retrieve (default: 24)

    Returns:
        List of circuit breaker events
    """
    from proxywhirl.api.models import CircuitBreakerEventResponse

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
    "/api/v1/circuit-breakers/{proxy_id}",
    response_model=APIResponse["CircuitBreakerResponse"],
    tags=["Retry & Failover"],
    summary="Get circuit breaker state for specific proxy",
)
async def get_circuit_breaker(
    proxy_id: str,
    api_key: None = Depends(verify_api_key),
) -> APIResponse[CircuitBreakerResponse]:
    """Get circuit breaker state for a specific proxy.

    Args:
        proxy_id: Proxy ID to get circuit breaker for

    Returns:
        Circuit breaker state
    """
    from proxywhirl.api.models import CircuitBreakerResponse

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
@limiter.limit("10/minute")
async def reset_circuit_breaker(
    request: Request,
    proxy_id: str,
    api_key: None = Depends(verify_api_key),
) -> APIResponse[CircuitBreakerResponse]:
    """Manually reset a circuit breaker to CLOSED state.

    Args:
        proxy_id: Proxy ID whose circuit breaker to reset

    Returns:
        Updated circuit breaker state
    """
    from proxywhirl.api.models import CircuitBreakerResponse

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
    "/api/v1/metrics/retries",
    response_model=APIResponse["RetryMetricsResponse"],
    tags=["Retry & Failover"],
    summary="Get retry metrics summary",
)
async def get_retry_metrics(
    api_key: None = Depends(verify_api_key),
) -> APIResponse[RetryMetricsResponse]:
    """Get aggregated retry metrics.

    Returns:
        Retry metrics summary
    """
    from proxywhirl.api.models import RetryMetricsResponse

    if not _rotator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rotator not initialized",
        )

    metrics = _rotator.get_retry_metrics()
    # Use asyncio.to_thread to avoid blocking event loop with threading.Lock
    summary = await asyncio.to_thread(metrics.get_summary)

    response = RetryMetricsResponse(
        total_retries=summary["total_retries"],
        success_by_attempt={str(k): v for k, v in summary["success_by_attempt"].items()},
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
) -> APIResponse[TimeSeriesResponse]:
    """Get hourly retry metrics for the specified time range.

    Args:
        hours: Number of hours to retrieve (default: 24)

    Returns:
        Time-series retry data
    """
    from proxywhirl.api.models import TimeSeriesDataPoint, TimeSeriesResponse

    if not _rotator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rotator not initialized",
        )

    metrics = _rotator.get_retry_metrics()
    # Use asyncio.to_thread to avoid blocking event loop with threading.Lock
    timeseries_data = await asyncio.to_thread(metrics.get_timeseries, hours=hours)

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
) -> APIResponse[ProxyRetryStatsResponse]:
    """Get retry statistics grouped by proxy.

    Args:
        hours: Number of hours to analyze (default: 24)

    Returns:
        Per-proxy retry statistics
    """
    from proxywhirl.api.models import ProxyRetryStats, ProxyRetryStatsResponse

    if not _rotator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rotator not initialized",
        )

    metrics = _rotator.get_retry_metrics()
    # Use asyncio.to_thread to avoid blocking event loop with threading.Lock
    stats_by_proxy = await asyncio.to_thread(metrics.get_by_proxy, hours=hours)

    proxies = {proxy_id: ProxyRetryStats(**stats) for proxy_id, stats in stats_by_proxy.items()}

    response = ProxyRetryStatsResponse(proxies=proxies)

    return APIResponse.success(data=response)


# =============================================================================
# TASK-701: Expose Retry Metrics via REST API
# =============================================================================


@app.get(
    "/metrics/retry",
    tags=["Monitoring"],
    summary="Get retry statistics with optional Prometheus format",
)
async def get_retry_metrics_endpoint(
    format: str | None = None,
    hours: int = 24,
    api_key: None = Depends(verify_api_key),
) -> Response:
    """Get retry statistics in JSON or Prometheus format.

    This endpoint provides comprehensive retry metrics including:
    - Total retry attempts
    - Success rate by attempt number
    - Time-series data (hourly aggregates)
    - Per-proxy statistics

    Args:
        format: Output format ('prometheus' for Prometheus text format, default: JSON)
        hours: Number of hours of data to include (default: 24)
        api_key: API key verification

    Returns:
        Retry metrics in requested format

    Example Prometheus format:
        # HELP proxywhirl_retry_total Total number of retry attempts
        # TYPE proxywhirl_retry_total counter
        proxywhirl_retry_total 1250

        # HELP proxywhirl_retry_success_by_attempt Successful requests by attempt number
        # TYPE proxywhirl_retry_success_by_attempt gauge
        proxywhirl_retry_success_by_attempt{attempt="0"} 850
        proxywhirl_retry_success_by_attempt{attempt="1"} 300
    """
    if not _rotator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rotator not initialized",
        )

    metrics = _rotator.get_retry_metrics()

    # Get all metrics data
    summary = metrics.get_summary()
    timeseries_data = metrics.get_timeseries(hours=hours)
    stats_by_proxy = metrics.get_by_proxy(hours=hours)

    # Prometheus format
    if format and format.lower() == "prometheus":
        lines = []

        # Total retries
        lines.append("# HELP proxywhirl_retry_total Total number of retry attempts")
        lines.append("# TYPE proxywhirl_retry_total counter")
        lines.append(f"proxywhirl_retry_total {summary['total_retries']}")
        lines.append("")

        # Success by attempt
        lines.append(
            "# HELP proxywhirl_retry_success_by_attempt Successful requests by attempt number"
        )
        lines.append("# TYPE proxywhirl_retry_success_by_attempt gauge")
        for attempt_num, count in summary["success_by_attempt"].items():
            lines.append(f'proxywhirl_retry_success_by_attempt{{attempt="{attempt_num}"}} {count}')
        lines.append("")

        # Circuit breaker events count
        lines.append(
            "# HELP proxywhirl_circuit_breaker_events_total Total circuit breaker state changes"
        )
        lines.append("# TYPE proxywhirl_circuit_breaker_events_total counter")
        lines.append(
            f"proxywhirl_circuit_breaker_events_total {summary['circuit_breaker_events_count']}"
        )
        lines.append("")

        # Per-proxy metrics
        lines.append("# HELP proxywhirl_retry_proxy_attempts Total retry attempts per proxy")
        lines.append("# TYPE proxywhirl_retry_proxy_attempts gauge")
        for proxy_id, stats in stats_by_proxy.items():
            # Escape proxy_id for Prometheus label
            safe_proxy_id = proxy_id.replace('"', '\\"')
            lines.append(
                f'proxywhirl_retry_proxy_attempts{{proxy_id="{safe_proxy_id}"}} {stats["total_attempts"]}'
            )
        lines.append("")

        lines.append("# HELP proxywhirl_retry_proxy_success Total successful requests per proxy")
        lines.append("# TYPE proxywhirl_retry_proxy_success gauge")
        for proxy_id, stats in stats_by_proxy.items():
            safe_proxy_id = proxy_id.replace('"', '\\"')
            lines.append(
                f'proxywhirl_retry_proxy_success{{proxy_id="{safe_proxy_id}"}} {stats["success_count"]}'
            )
        lines.append("")

        lines.append("# HELP proxywhirl_retry_proxy_failure Total failed requests per proxy")
        lines.append("# TYPE proxywhirl_retry_proxy_failure gauge")
        for proxy_id, stats in stats_by_proxy.items():
            safe_proxy_id = proxy_id.replace('"', '\\"')
            lines.append(
                f'proxywhirl_retry_proxy_failure{{proxy_id="{safe_proxy_id}"}} {stats["failure_count"]}'
            )
        lines.append("")

        lines.append(
            "# HELP proxywhirl_retry_proxy_avg_latency Average latency per proxy in seconds"
        )
        lines.append("# TYPE proxywhirl_retry_proxy_avg_latency gauge")
        for proxy_id, stats in stats_by_proxy.items():
            safe_proxy_id = proxy_id.replace('"', '\\"')
            lines.append(
                f'proxywhirl_retry_proxy_avg_latency{{proxy_id="{safe_proxy_id}"}} {stats["avg_latency"]:.6f}'
            )
        lines.append("")

        prometheus_output = "\n".join(lines)
        return Response(
            content=prometheus_output,
            media_type="text/plain; version=0.0.4; charset=utf-8",
        )

    # JSON format (default)

    # Build comprehensive response
    response_data = {
        "summary": {
            "total_retries": summary["total_retries"],
            "success_by_attempt": {str(k): v for k, v in summary["success_by_attempt"].items()},
            "circuit_breaker_events_count": summary["circuit_breaker_events_count"],
            "retention_hours": summary["retention_hours"],
        },
        "timeseries": [
            {
                "timestamp": point["timestamp"],
                "total_requests": point["total_requests"],
                "total_retries": point["total_retries"],
                "success_rate": point["success_rate"],
                "avg_latency": point["avg_latency"],
            }
            for point in timeseries_data
        ],
        "by_proxy": {
            proxy_id: {
                "proxy_id": stats["proxy_id"],
                "total_attempts": stats["total_attempts"],
                "success_count": stats["success_count"],
                "failure_count": stats["failure_count"],
                "avg_latency": stats["avg_latency"],
                "circuit_breaker_opens": stats["circuit_breaker_opens"],
            }
            for proxy_id, stats in stats_by_proxy.items()
        },
    }

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=APIResponse.success(data=response_data).model_dump(mode="json"),
    )


@app.get(
    "/metrics/circuit-breaker",
    tags=["Monitoring"],
    summary="Get circuit breaker states with optional Prometheus format",
)
async def get_circuit_breaker_metrics_endpoint(
    format: str | None = None,
    hours: int = 24,
    api_key: None = Depends(verify_api_key),
) -> Response:
    """Get circuit breaker states and events in JSON or Prometheus format.

    This endpoint provides circuit breaker information including:
    - Current state of all circuit breakers
    - State change events (history)
    - Failure counts and thresholds

    Args:
        format: Output format ('prometheus' for Prometheus text format, default: JSON)
        hours: Number of hours of event history to include (default: 24)
        api_key: API key verification

    Returns:
        Circuit breaker metrics in requested format

    Example Prometheus format:
        # HELP proxywhirl_circuit_breaker_state Circuit breaker state (0=closed, 1=open, 2=half_open)
        # TYPE proxywhirl_circuit_breaker_state gauge
        proxywhirl_circuit_breaker_state{proxy_id="proxy1:8080"} 0

        # HELP proxywhirl_circuit_breaker_failure_count Current failure count
        # TYPE proxywhirl_circuit_breaker_failure_count gauge
        proxywhirl_circuit_breaker_failure_count{proxy_id="proxy1:8080"} 2
    """
    if not _rotator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rotator not initialized",
        )

    # Get circuit breaker states
    circuit_breakers = _rotator.get_circuit_breaker_states()

    # Get circuit breaker events
    metrics = _rotator.get_retry_metrics()
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    events = [event for event in metrics.circuit_breaker_events if event.timestamp >= cutoff]

    # Prometheus format
    if format and format.lower() == "prometheus":
        lines = []

        # Circuit breaker state
        lines.append(
            "# HELP proxywhirl_circuit_breaker_state Circuit breaker state (0=closed, 1=open, 2=half_open)"
        )
        lines.append("# TYPE proxywhirl_circuit_breaker_state gauge")
        for proxy_id, cb in circuit_breakers.items():
            safe_proxy_id = proxy_id.replace('"', '\\"')
            # Map state to numeric value
            state_value = 0
            if cb.state.value == "open":
                state_value = 1
            elif cb.state.value == "half_open":
                state_value = 2
            lines.append(
                f'proxywhirl_circuit_breaker_state{{proxy_id="{safe_proxy_id}"}} {state_value}'
            )
        lines.append("")

        # Failure count
        lines.append(
            "# HELP proxywhirl_circuit_breaker_failure_count Current failure count within window"
        )
        lines.append("# TYPE proxywhirl_circuit_breaker_failure_count gauge")
        for proxy_id, cb in circuit_breakers.items():
            safe_proxy_id = proxy_id.replace('"', '\\"')
            lines.append(
                f'proxywhirl_circuit_breaker_failure_count{{proxy_id="{safe_proxy_id}"}} {cb.failure_count}'
            )
        lines.append("")

        # Failure threshold
        lines.append(
            "# HELP proxywhirl_circuit_breaker_failure_threshold Failure threshold before opening"
        )
        lines.append("# TYPE proxywhirl_circuit_breaker_failure_threshold gauge")
        for proxy_id, cb in circuit_breakers.items():
            safe_proxy_id = proxy_id.replace('"', '\\"')
            lines.append(
                f'proxywhirl_circuit_breaker_failure_threshold{{proxy_id="{safe_proxy_id}"}} {cb.failure_threshold}'
            )
        lines.append("")

        # State change events count
        lines.append(
            "# HELP proxywhirl_circuit_breaker_state_changes_total Total state changes in time window"
        )
        lines.append("# TYPE proxywhirl_circuit_breaker_state_changes_total counter")
        lines.append(f"proxywhirl_circuit_breaker_state_changes_total {len(events)}")
        lines.append("")

        # Count of opens per proxy
        from collections import defaultdict

        opens_by_proxy: dict[str, int] = defaultdict(int)
        for event in events:
            if event.to_state.value == "open":
                opens_by_proxy[event.proxy_id] += 1

        lines.append(
            "# HELP proxywhirl_circuit_breaker_opens_total Total circuit breaker opens per proxy"
        )
        lines.append("# TYPE proxywhirl_circuit_breaker_opens_total counter")
        for proxy_id, count in opens_by_proxy.items():
            safe_proxy_id = proxy_id.replace('"', '\\"')
            lines.append(
                f'proxywhirl_circuit_breaker_opens_total{{proxy_id="{safe_proxy_id}"}} {count}'
            )
        lines.append("")

        prometheus_output = "\n".join(lines)
        return Response(
            content=prometheus_output,
            media_type="text/plain; version=0.0.4; charset=utf-8",
        )

    # JSON format (default)
    from proxywhirl.api.models import CircuitBreakerEventResponse, CircuitBreakerResponse

    # Build circuit breaker states response
    states = []
    for proxy_id, cb in circuit_breakers.items():
        states.append(
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

    # Build events response
    event_responses = [
        CircuitBreakerEventResponse(
            proxy_id=event.proxy_id,
            from_state=event.from_state.value,
            to_state=event.to_state.value,
            timestamp=event.timestamp,
            failure_count=event.failure_count,
        )
        for event in events
    ]

    response_data = {
        "states": [state.model_dump(mode="json") for state in states],
        "events": [event.model_dump(mode="json") for event in event_responses],
        "total_events": len(event_responses),
        "hours": hours,
    }

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=APIResponse.success(data=response_data).model_dump(mode="json"),
    )
