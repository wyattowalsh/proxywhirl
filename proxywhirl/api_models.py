"""API-specific Pydantic models for REST API request/response validation.

This module contains models specific to the HTTP API layer, separate from
core domain models in models.py. These models define the API contract including:
- Generic response envelope (APIResponse[T])
- Error details and codes
- Request/response metadata
- API-specific entities (ProxyResource, etc.)
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Generic, Literal, Optional, TypeVar
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, PositiveInt, SecretStr

# Generic type variable for response data
T = TypeVar("T")


class ErrorCode(str, Enum):
    """Standard error codes for API responses."""

    # Validation errors (4xx)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_URL = "INVALID_URL"
    INVALID_PROXY_FORMAT = "INVALID_PROXY_FORMAT"
    INVALID_METHOD = "INVALID_METHOD"
    INVALID_TIMEOUT = "INVALID_TIMEOUT"

    # Proxy errors (5xx)
    PROXY_ERROR = "PROXY_ERROR"
    PROXY_POOL_EMPTY = "PROXY_POOL_EMPTY"
    PROXY_FAILOVER_EXHAUSTED = "PROXY_FAILOVER_EXHAUSTED"
    PROXY_NOT_FOUND = "PROXY_NOT_FOUND"
    PROXY_ALREADY_EXISTS = "PROXY_ALREADY_EXISTS"

    # Target/request errors (5xx)
    TARGET_UNREACHABLE = "TARGET_UNREACHABLE"
    REQUEST_TIMEOUT = "REQUEST_TIMEOUT"
    REQUEST_FAILED = "REQUEST_FAILED"

    # Configuration errors (4xx/5xx)
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    INVALID_CONFIGURATION = "INVALID_CONFIGURATION"

    # System errors (5xx)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


class ErrorDetail(BaseModel):
    """Structured error information for API responses."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "PROXY_POOL_EMPTY",
                "message": "No proxies available in the pool",
                "details": {"available_proxies": 0, "total_proxies": 0},
                "timestamp": "2025-10-27T12:00:00Z",
            }
        }
    )

    code: ErrorCode = Field(description="Machine-readable error code for client handling")
    message: str = Field(description="Human-readable error message")
    details: Optional[dict[str, Any]] = Field(
        default=None,
        description="Additional context about the error (e.g., validation failures)",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the error occurred (UTC)",
    )


class MetaInfo(BaseModel):
    """Metadata included in all API responses."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2025-10-27T12:00:00Z",
                "version": "1.0.0",
            }
        }
    )

    request_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique ID for request tracing and correlation",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Response generation timestamp (UTC)",
    )
    version: str = Field(
        default="1.0.0",
        description="API version",
    )


class APIResponse(BaseModel, Generic[T]):
    """Generic envelope for all API responses.

    Provides consistent structure:
    - status: HTTP-like status indicator
    - data: Successful response payload (type T)
    - error: Error details if request failed
    - meta: Request metadata (ID, timestamp, version)

    Example successful response:
        {
            "status": "success",
            "data": {"id": "123", "url": "http://proxy:8080"},
            "error": null,
            "meta": {"request_id": "...", "timestamp": "...", "version": "1.0.0"}
        }

    Example error response:
        {
            "status": "error",
            "data": null,
            "error": {"code": "PROXY_NOT_FOUND", "message": "...", ...},
            "meta": {"request_id": "...", "timestamp": "...", "version": "1.0.0"}
        }
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "status": "success",
                    "data": {"message": "Operation completed successfully"},
                    "error": None,
                    "meta": {
                        "request_id": "550e8400-e29b-41d4-a716-446655440000",
                        "timestamp": "2025-10-27T12:00:00Z",
                        "version": "1.0.0",
                    },
                },
                {
                    "status": "error",
                    "data": None,
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Invalid request parameters",
                        "details": {"field": "url", "reason": "Invalid URL format"},
                        "timestamp": "2025-10-27T12:00:00Z",
                    },
                    "meta": {
                        "request_id": "550e8400-e29b-41d4-a716-446655440001",
                        "timestamp": "2025-10-27T12:00:00Z",
                        "version": "1.0.0",
                    },
                },
            ]
        }
    )

    status: str = Field(description="Response status: 'success' or 'error'")
    data: Optional[T] = Field(
        default=None,
        description="Response payload (present on success)",
    )
    error: Optional[ErrorDetail] = Field(
        default=None,
        description="Error details (present on failure)",
        serialization_alias="error",
    )
    meta: MetaInfo = Field(
        default_factory=MetaInfo,
        description="Response metadata (request ID, timestamp, version)",
    )

    @classmethod
    def success(cls, data: T, **kwargs: Any) -> "APIResponse[T]":
        """Create a successful response with data payload.

        Args:
            data: Response payload
            **kwargs: Additional fields to override (e.g., meta)

        Returns:
            APIResponse with status='success' and data populated
        """
        return cls(status="success", data=data, error=None, **kwargs)

    @classmethod
    def error_response(
        cls,
        code: ErrorCode,
        message: str,
        details: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> "APIResponse[T]":
        """Create an error response with error details.

        Args:
            code: Machine-readable error code
            message: Human-readable error message
            details: Additional error context
            **kwargs: Additional fields to override (e.g., meta)

        Returns:
            APIResponse with status='error' and error populated
        """
        err = ErrorDetail(code=code, message=message, details=details)
        return cls(status="error", data=None, error=err, **kwargs)


# ============================================================================
# REQUEST/RESPONSE MODELS FOR USER STORIES
# ============================================================================


# --- US1: Proxied Requests ---


class ProxiedRequest(BaseModel):
    """Request to make an HTTP request through a proxy."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "url": "https://httpbin.org/ip",
                "method": "GET",
                "headers": {"User-Agent": "ProxyWhirl/1.0"},
                "body": None,
                "timeout": 30,
            }
        }
    )

    url: HttpUrl = Field(description="Target URL to fetch through proxy")
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"] = Field(
        default="GET",
        description="HTTP method",
    )
    headers: dict[str, str] = Field(
        default_factory=dict,
        description="Request headers to pass through",
    )
    body: Optional[str] = Field(
        default=None,
        description="Request body (for POST/PUT/PATCH)",
    )
    timeout: PositiveInt = Field(
        default=30,
        description="Request timeout in seconds",
        le=300,
    )


class ProxiedResponse(BaseModel):
    """Response from a proxied HTTP request."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status_code": 200,
                "headers": {"content-type": "application/json"},
                "body": '{"origin": "1.2.3.4"}',
                "proxy_used": "http://proxy.example.com:8080",
                "elapsed_ms": 1250,
            }
        }
    )

    status_code: int = Field(description="HTTP status code from target")
    headers: dict[str, str] = Field(description="Response headers from target")
    body: str = Field(description="Response body from target")
    proxy_used: Optional[str] = Field(
        default=None,
        description="Proxy URL that was used for this request",
    )
    elapsed_ms: int = Field(description="Request duration in milliseconds")


# --- US2: Manage Proxy Pool ---


class CreateProxyRequest(BaseModel):
    """Request to add a new proxy to the pool."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "url": "http://proxy.example.com:8080",
                "username": "user123",
                "password": "secret456",
            }
        }
    )

    url: HttpUrl = Field(description="Proxy URL (protocol://host:port)")
    username: Optional[str] = Field(default=None, description="Proxy username")
    password: Optional[SecretStr] = Field(default=None, description="Proxy password")


class ProxyResource(BaseModel):
    """RESTful representation of a proxy in the pool."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "url": "http://proxy.example.com:8080",
                "protocol": "http",
                "status": "healthy",
                "health": "healthy",
                "stats": {
                    "total_requests": 42,
                    "successful_requests": 40,
                    "failed_requests": 2,
                    "avg_latency_ms": 250,
                },
                "created_at": "2025-10-27T12:00:00Z",
                "updated_at": "2025-10-27T13:00:00Z",
            }
        }
    )

    id: str = Field(description="Unique proxy identifier")
    url: str = Field(description="Proxy URL")
    protocol: str = Field(description="Proxy protocol (http/https/socks5)")
    status: str = Field(description="Current proxy status")
    health: str = Field(description="Health check status")
    stats: dict[str, Any] = Field(description="Proxy statistics")
    created_at: datetime = Field(description="When proxy was added")
    updated_at: datetime = Field(description="Last update timestamp")


class HealthCheckRequest(BaseModel):
    """Request to health check specific proxies."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "proxy_ids": ["550e8400-e29b-41d4-a716-446655440000"],
            }
        }
    )

    proxy_ids: Optional[list[str]] = Field(
        default=None,
        description="Specific proxy IDs to check (null = check all)",
    )


class HealthCheckResult(BaseModel):
    """Result of a proxy health check."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "proxy_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "working",
                "latency_ms": 125,
                "error": None,
                "tested_at": "2025-10-27T12:00:00Z",
            }
        }
    )

    proxy_id: str
    status: Literal["working", "failed"]
    latency_ms: Optional[int] = None
    error: Optional[str] = None
    tested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list response."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 42,
                "page": 1,
                "page_size": 20,
                "has_next": True,
                "has_prev": False,
            }
        }
    )

    items: list[T]
    total: int
    page: int
    page_size: int
    has_next: bool = Field(default=False)
    has_prev: bool = Field(default=False)


# --- US3: Monitor Health & Status ---


class HealthResponse(BaseModel):
    """API health status response."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "uptime_seconds": 3600,
                "version": "1.0.0",
                "timestamp": "2025-10-27T12:00:00Z",
            }
        }
    )

    status: Literal["healthy", "degraded", "unhealthy"]
    uptime_seconds: int
    version: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReadinessResponse(BaseModel):
    """API readiness status response."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ready": True,
                "checks": {
                    "proxy_pool_initialized": True,
                    "storage_connected": True,
                },
            }
        }
    )

    ready: bool
    checks: dict[str, bool]


class ProxyPoolStats(BaseModel):
    """Statistics about the proxy pool."""

    total: int
    active: int
    failed: int
    healthy_percentage: float
    last_rotation: Optional[datetime] = None


class StatusResponse(BaseModel):
    """API and pool status response."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "pool_stats": {
                    "total": 10,
                    "active": 8,
                    "failed": 2,
                    "healthy_percentage": 80.0,
                    "last_rotation": "2025-10-27T12:00:00Z",
                },
                "rotation_strategy": "round-robin",
                "storage_backend": "memory",
                "config_source": "defaults",
            }
        }
    )

    pool_stats: ProxyPoolStats
    rotation_strategy: str
    storage_backend: Optional[str] = None
    config_source: str = "defaults"


class ProxyMetrics(BaseModel):
    """Per-proxy performance metrics."""

    proxy_id: str
    requests: int
    success_rate: float
    avg_latency_ms: float
    last_used: Optional[datetime] = None


class MetricsResponse(BaseModel):
    """API performance metrics response."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "requests_total": 1000,
                "requests_per_second": 10.5,
                "avg_latency_ms": 250.0,
                "error_rate": 0.05,
                "proxy_stats": [],
            }
        }
    )

    requests_total: int
    requests_per_second: float
    avg_latency_ms: float
    error_rate: float
    proxy_stats: list[ProxyMetrics]


# --- US4: Configure Settings ---


class RateLimitConfig(BaseModel):
    """Rate limiting configuration."""

    default_limit: int = 100
    request_endpoint_limit: int = 50


class ConfigurationSettings(BaseModel):
    """API configuration settings."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rotation_strategy": "round-robin",
                "timeout": 30,
                "max_retries": 3,
                "rate_limits": {
                    "default_limit": 100,
                    "request_endpoint_limit": 50,
                },
                "auth_enabled": False,
                "cors_origins": ["*"],
            }
        }
    )

    rotation_strategy: str = "round-robin"
    timeout: PositiveInt = Field(default=30, le=300)
    max_retries: PositiveInt = Field(default=3, le=10)
    rate_limits: RateLimitConfig = Field(default_factory=RateLimitConfig)
    auth_enabled: bool = False
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])


class UpdateConfigRequest(BaseModel):
    """Request to update API configuration (partial updates allowed)."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rotation_strategy": "round-robin",
                "timeout": 60,
            }
        }
    )

    rotation_strategy: Optional[str] = None
    timeout: Optional[PositiveInt] = Field(default=None, le=300)
    max_retries: Optional[PositiveInt] = Field(default=None, le=10)
    rate_limits: Optional[RateLimitConfig] = None
    cors_origins: Optional[list[str]] = None
