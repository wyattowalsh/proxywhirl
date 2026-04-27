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
- Singleton ProxyWhirl for proxy management
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
from datetime import datetime, timezone
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from loguru import logger
from prometheus_client import Counter, Gauge, Histogram
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from proxywhirl.api.middleware.auth import APIKeyMiddleware
from proxywhirl.api.models import APIResponse, ErrorCode, ProxiedRequest
from proxywhirl.exceptions import ProxyWhirlError
from proxywhirl.rotator import ProxyWhirl
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
_rotator: ProxyWhirl | None = None
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
        str: Rate limit key in the form ``apikey:{hash}`` or ``ip:{address}``.
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
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL is blocked by security policy (SSRF protection)",
        )
    return request_data


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager for startup and shutdown.

    Handles:
    - ProxyWhirl initialization on startup
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
    logger.info("Initializing ProxyWhirl...")
    _rotator = ProxyWhirl()

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
    cors_origins_raw = os.getenv("PROXYWHIRL_CORS_ORIGINS", "")
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
# Security: Default to no CORS (empty list = CORS disabled)
# Only enable CORS if explicitly configured via PROXYWHIRL_CORS_ORIGINS environment variable
cors_origins_raw = os.getenv("PROXYWHIRL_CORS_ORIGINS", "")
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
        # Validate client-supplied request IDs to prevent log injection
        supplied_id = request.headers.get("X-Request-ID")
        if (
            supplied_id
            and len(supplied_id) <= 128
            and supplied_id.isprintable()
            and supplied_id.isascii()
        ):
            request_id = supplied_id
        else:
            request_id = str(uuid.uuid4())

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

        # Extract audit context - log both real and claimed IPs
        socket_ip = request.client.host if request.client else "unknown"
        client_ip = socket_ip
        forwarded_for = request.headers.get("X-Forwarded-For")
        claimed_ip = forwarded_for.split(",")[0].strip() if forwarded_for else None

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
            claimed_ip=claimed_ip,
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

        # Extract client IP - use socket IP (do not trust X-Forwarded-For)
        client_ip = request.client.host if request.client else "unknown"

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
app.add_middleware(APIKeyMiddleware)


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
    """Handle 500 Internal Server errors (without exposing stack traces)."""
    # Log full error with stack trace for debugging (internal logs only)
    logger.error(f"Internal server error: {exc}", exc_info=True)

    # Return generic error message to client (no stack trace exposure)
    response: APIResponse[None] = APIResponse.error_response(
        code=ErrorCode.INTERNAL_ERROR,
        message="Internal server error occurred",
        details=None,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response.model_dump(mode="json"),
    )


@app.exception_handler(ProxyWhirlError)
async def proxy_error_handler(request: Request, exc: ProxyWhirlError) -> JSONResponse:
    """Handle ProxyWhirlError exceptions (with safe error details)."""
    # Log the error with full context (internal logs only)
    logger.bind(
        error_code=exc.error_code.value if hasattr(exc, "error_code") else "UNKNOWN",
        error_type=type(exc).__name__,
        proxy_url=exc.proxy_url if hasattr(exc, "proxy_url") else None,
        attempt_count=exc.attempt_count if hasattr(exc, "attempt_count") else None,
        retry_recommended=exc.retry_recommended if hasattr(exc, "retry_recommended") else False,
    ).error(f"Proxy error: {exc}", exc_info=True)

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

    # Build error response with SAFE details (no stack traces, no sensitive info)
    error_details = {
        "error_type": type(exc).__name__,
        "error_code": exc.error_code.value if hasattr(exc, "error_code") else "UNKNOWN",
        "retry_recommended": exc.retry_recommended if hasattr(exc, "retry_recommended") else False,
    }

    # Add attempt count if available
    if hasattr(exc, "attempt_count") and exc.attempt_count is not None:
        error_details["attempt_count"] = exc.attempt_count

    # Only include safe metadata (never include credentials, URLs, or internal state)
    if hasattr(exc, "metadata") and exc.metadata:
        # Filter out sensitive keys from metadata
        safe_metadata = {
            k: v
            for k, v in exc.metadata.items()
            if k not in {"url", "proxy_url", "password", "token", "credential", "key", "secret"}
        }
        error_details.update(safe_metadata)

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
def get_rotator() -> ProxyWhirl:
    """Get the singleton ProxyWhirl instance.

    Returns:
        ProxyWhirl instance

    Raises:
        HTTPException: If rotator not initialized
    """
    if _rotator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ProxyWhirl not initialized",
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
# Import and register route modules
# =============================================================================

from proxywhirl.api.routes import health_router, pools_router, proxies_router  # noqa: E402

app.include_router(proxies_router)
app.include_router(health_router)
app.include_router(pools_router)
