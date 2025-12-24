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

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    PositiveInt,
    SecretStr,
    field_validator,
)

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

    @field_validator("url")
    @classmethod
    def validate_url_scheme(cls, v: HttpUrl) -> HttpUrl:
        """Validate that URL uses http or https scheme only.

        Args:
            v: URL to validate

        Returns:
            Validated URL

        Raises:
            ValueError: If URL scheme is not http or https
        """
        url_str = str(v)

        # Check length limit (2048 chars max for URLs)
        if len(url_str) > 2048:
            raise ValueError("URL must be 2048 characters or less")

        # Check scheme (only http/https allowed for target URLs)
        if hasattr(v, "scheme"):
            scheme = v.scheme
        else:
            scheme = url_str.split("://")[0] if "://" in url_str else ""

        if scheme.lower() not in ("http", "https"):
            raise ValueError(
                f"Invalid URL scheme '{scheme}'. "
                f"Only 'http' and 'https' are allowed for target URLs"
            )

        return v

    @field_validator("headers")
    @classmethod
    def validate_headers(cls, v: dict[str, str]) -> dict[str, str]:
        """Validate header names and values length.

        Args:
            v: Headers dict to validate

        Returns:
            Validated headers

        Raises:
            ValueError: If header name or value exceeds length limit
        """
        for name, value in v.items():
            if len(name) > 256:
                raise ValueError(f"Header name '{name[:50]}...' exceeds 256 character limit")
            if len(value) > 2048:
                raise ValueError(f"Header value for '{name}' exceeds 2048 character limit")
        return v

    @field_validator("body")
    @classmethod
    def validate_body(cls, v: Optional[str]) -> Optional[str]:
        """Validate body length.

        Args:
            v: Body string to validate

        Returns:
            Validated body

        Raises:
            ValueError: If body exceeds length limit
        """
        if v is not None and len(v) > 1048576:  # 1MB limit
            raise ValueError("Request body must be 1MB (1,048,576 characters) or less")
        return v


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

    url: str = Field(description="Proxy URL (protocol://host:port)")
    username: Optional[str] = Field(default=None, description="Proxy username")
    password: Optional[SecretStr] = Field(default=None, description="Proxy password")

    @field_validator("url")
    @classmethod
    def validate_proxy_url(cls, v: str) -> str:
        """Validate proxy URL scheme, port, and length.

        Args:
            v: Proxy URL to validate

        Returns:
            Validated URL

        Raises:
            ValueError: If URL is invalid
        """
        from urllib.parse import urlparse

        # Check length limit (2048 chars max for URLs)
        if len(v) > 2048:
            raise ValueError("Proxy URL must be 2048 characters or less")

        # Parse the URL
        if "://" not in v:
            raise ValueError("Proxy URL must include a scheme (e.g., http://proxy:8080)")

        try:
            parsed = urlparse(v)
        except Exception as e:
            raise ValueError(f"Invalid proxy URL format: {e}")

        # Check scheme (http/https/socks4/socks5 allowed for proxies)
        scheme = parsed.scheme
        allowed_schemes = ("http", "https", "socks4", "socks5")
        if scheme.lower() not in allowed_schemes:
            raise ValueError(
                f"Invalid proxy URL scheme '{scheme}'. "
                f"Allowed schemes: {', '.join(allowed_schemes)}"
            )

        # Check hostname exists and length
        host = parsed.hostname
        if not host:
            raise ValueError("Proxy URL must include a hostname")
        if len(host) > 256:
            raise ValueError("Proxy hostname must be 256 characters or less")

        # Check port exists and range (1-65535)
        port = parsed.port
        if port is None:
            raise ValueError("Proxy URL must include a port number")
        if not (1 <= port <= 65535):
            raise ValueError(f"Port {port} is out of valid range (1-65535)")

        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        """Validate username length.

        Args:
            v: Username to validate

        Returns:
            Validated username

        Raises:
            ValueError: If username exceeds length limit
        """
        if v is not None and len(v) > 256:
            raise ValueError("Username must be 256 characters or less")
        return v


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

    @field_validator("rotation_strategy")
    @classmethod
    def validate_rotation_strategy(cls, v: Optional[str]) -> Optional[str]:
        """Validate rotation strategy is from allowed set.

        Args:
            v: Rotation strategy to validate

        Returns:
            Validated rotation strategy

        Raises:
            ValueError: If rotation strategy is invalid
        """
        if v is not None:
            # Check length limit
            if len(v) > 64:
                raise ValueError("Rotation strategy name must be 64 characters or less")

            # Check against valid strategies
            valid_strategies = {"round-robin", "random", "weighted", "least-used"}
            if v.lower() not in valid_strategies:
                raise ValueError(
                    f"Invalid rotation strategy '{v}'. "
                    f"Allowed strategies: {', '.join(sorted(valid_strategies))}"
                )
        return v

    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Validate CORS origins length.

        Args:
            v: CORS origins to validate

        Returns:
            Validated CORS origins

        Raises:
            ValueError: If any origin exceeds length limit
        """
        if v is not None:
            for origin in v:
                if len(origin) > 256:
                    raise ValueError(
                        f"CORS origin '{origin[:50]}...' must be 256 characters or less"
                    )
        return v


# ============================================================================
# EXPORT API MODELS
# ============================================================================


class ExportRequest(BaseModel):
    """Request model for creating an export."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "export_type": "proxies",
                "export_format": "csv",
                "destination_type": "local_file",
                "file_path": "exports/proxies.csv",
                "compression": "gzip",
                "health_status": ["healthy"],
                "pretty_print": True,
            }
        }
    )

    export_type: str = Field(description="Type of data to export (proxies, metrics, logs, configuration, health_status, cache_data)")
    export_format: str = Field(description="Output format (csv, json, jsonl, yaml, text, markdown)")

    # Destination
    destination_type: str = Field("local_file", description="Destination type (local_file, memory)")
    file_path: Optional[str] = Field(None, description="File path for local_file destination")
    overwrite: bool = Field(False, description="Overwrite existing file")

    # Compression
    compression: str = Field("none", description="Compression type (none, gzip, zip)")

    # Filters (optional, depending on export type)
    health_status: Optional[list[str]] = Field(None, description="Filter proxies by health status")
    source: Optional[list[str]] = Field(None, description="Filter proxies by source")
    protocol: Optional[list[str]] = Field(None, description="Filter proxies by protocol")
    min_success_rate: Optional[float] = Field(None, description="Minimum success rate for proxy filter")

    # Metrics filters
    start_time: Optional[datetime] = Field(None, description="Start time for metrics/logs export")
    end_time: Optional[datetime] = Field(None, description="End time for metrics/logs export")

    # Log filters
    log_levels: Optional[list[str]] = Field(None, description="Filter logs by level")

    # Config filters
    redact_secrets: bool = Field(True, description="Redact sensitive data in config export")

    # Options
    pretty_print: bool = Field(True, description="Pretty-print JSON/YAML")
    include_metadata: bool = Field(True, description="Include export metadata")


class ExportStatusResponse(BaseModel):
    """Response model for export status query."""

    model_config = ConfigDict(extra="forbid")

    job_id: str = Field(description="Export job ID")
    status: str = Field(description="Current status (pending, running, completed, failed, cancelled)")
    export_type: str = Field(description="Type of data being exported")
    export_format: str = Field(description="Output format")

    # Progress
    total_records: int = Field(0, description="Total records to export")
    processed_records: int = Field(0, description="Records processed")
    progress_percentage: float = Field(0.0, description="Progress percentage")

    # Timestamps
    created_at: datetime = Field(description="When export was created")
    started_at: Optional[datetime] = Field(None, description="When export started")
    completed_at: Optional[datetime] = Field(None, description="When export completed")
    duration_seconds: Optional[float] = Field(None, description="Export duration")

    # Results
    result_path: Optional[str] = Field(None, description="Path to exported file")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class ExportHistoryResponse(BaseModel):
    """Response model for export history query."""

    model_config = ConfigDict(extra="forbid")

    total_exports: int = Field(description="Total number of exports in history")
    exports: list[dict[str, Any]] = Field(description="List of export history entries")


# ============================================================================
# RETRY & FAILOVER API MODELS
# ============================================================================


class RetryPolicyRequest(BaseModel):
    """Request model for updating retry policy."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "max_attempts": 5,
                "backoff_strategy": "exponential",
                "base_delay": 1.5,
                "multiplier": 2.0,
                "max_backoff_delay": 30.0,
                "jitter": True,
                "retry_status_codes": [502, 503, 504],
                "timeout": None,
                "retry_non_idempotent": False,
            }
        },
    )

    max_attempts: Optional[int] = Field(None, ge=1, le=10, description="Maximum retry attempts")
    backoff_strategy: Optional[str] = Field(
        None,
        description="Backoff strategy (exponential, linear, fixed)",
    )
    base_delay: Optional[float] = Field(None, gt=0, le=60, description="Base delay in seconds")
    multiplier: Optional[float] = Field(
        None, gt=1, le=10, description="Multiplier for exponential backoff"
    )
    max_backoff_delay: Optional[float] = Field(
        None, gt=0, le=300, description="Maximum backoff delay in seconds"
    )
    jitter: Optional[bool] = Field(None, description="Enable random jitter")
    retry_status_codes: Optional[list[int]] = Field(
        None, description="HTTP status codes that trigger retries"
    )
    timeout: Optional[float] = Field(None, gt=0, description="Total request timeout in seconds")
    retry_non_idempotent: Optional[bool] = Field(
        None, description="Allow retries for non-idempotent requests (POST, PUT)"
    )


class RetryPolicyResponse(BaseModel):
    """Response model for retry policy."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "max_attempts": 3,
                "backoff_strategy": "exponential",
                "base_delay": 1.0,
                "multiplier": 2.0,
                "max_backoff_delay": 30.0,
                "jitter": False,
                "retry_status_codes": [502, 503, 504],
                "timeout": None,
                "retry_non_idempotent": False,
                "updated_at": "2025-11-02T12:00:00Z",
            }
        }
    )

    max_attempts: int
    backoff_strategy: str
    base_delay: float
    multiplier: float
    max_backoff_delay: float
    jitter: bool
    retry_status_codes: list[int]
    timeout: Optional[float]
    retry_non_idempotent: bool
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CircuitBreakerResponse(BaseModel):
    """Response model for circuit breaker state."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "proxy_id": "proxy1.example.com:8080",
                "state": "closed",
                "failure_count": 2,
                "failure_threshold": 5,
                "window_duration": 60.0,
                "timeout_duration": 30.0,
                "next_test_time": None,
                "last_state_change": "2025-11-02T12:00:00Z",
            }
        }
    )

    proxy_id: str
    state: str = Field(description="Circuit breaker state (closed, open, half_open)")
    failure_count: int = Field(ge=0)
    failure_threshold: int = Field(ge=1)
    window_duration: float = Field(gt=0, description="Failure window duration in seconds")
    timeout_duration: float = Field(gt=0, description="Timeout before half-open in seconds")
    next_test_time: Optional[datetime] = Field(
        None, description="Next recovery test time (ISO 8601)"
    )
    last_state_change: datetime


class CircuitBreakerEventResponse(BaseModel):
    """Response model for circuit breaker state change event."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "proxy_id": "proxy1.example.com:8080",
                "from_state": "closed",
                "to_state": "open",
                "timestamp": "2025-11-02T12:00:00Z",
                "failure_count": 5,
            }
        }
    )

    proxy_id: str
    from_state: str
    to_state: str
    timestamp: datetime
    failure_count: int


class RetryMetricsResponse(BaseModel):
    """Response model for retry metrics summary."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_retries": 1250,
                "success_by_attempt": {
                    "0": 850,
                    "1": 300,
                    "2": 80,
                    "3": 20,
                },
                "circuit_breaker_events_count": 15,
                "retention_hours": 24,
            }
        }
    )

    total_retries: int = Field(ge=0, description="Total retry attempts in retention period")
    success_by_attempt: dict[str, int] = Field(
        description="Success count by attempt number (0=first try)"
    )
    circuit_breaker_events_count: int = Field(
        ge=0, description="Number of circuit breaker state changes"
    )
    retention_hours: int = Field(ge=1, description="Metrics retention period in hours")


class TimeSeriesDataPoint(BaseModel):
    """Single data point in time-series metrics."""

    timestamp: datetime
    total_requests: int = Field(ge=0)
    total_retries: int = Field(ge=0)
    success_rate: float = Field(ge=0.0, le=1.0)
    avg_latency: float = Field(ge=0.0, description="Average latency in seconds")


class TimeSeriesResponse(BaseModel):
    """Response model for time-series retry data."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data_points": [
                    {
                        "timestamp": "2025-11-02T12:00:00Z",
                        "total_requests": 1000,
                        "total_retries": 150,
                        "success_rate": 0.95,
                        "avg_latency": 0.25,
                    }
                ]
            }
        }
    )

    data_points: list[TimeSeriesDataPoint]


class ProxyRetryStats(BaseModel):
    """Per-proxy retry statistics."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "proxy_id": "proxy1.example.com:8080",
                "total_attempts": 500,
                "success_count": 450,
                "failure_count": 50,
                "avg_latency": 0.3,
                "circuit_breaker_opens": 2,
            }
        }
    )

    proxy_id: str
    total_attempts: int = Field(ge=0)
    success_count: int = Field(ge=0)
    failure_count: int = Field(ge=0)
    avg_latency: float = Field(ge=0.0, description="Average latency in seconds")
    circuit_breaker_opens: int = Field(ge=0, description="Number of times circuit opened")


class ProxyRetryStatsResponse(BaseModel):
    """Response model for per-proxy retry statistics."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "proxies": {
                    "proxy1.example.com:8080": {
                        "proxy_id": "proxy1.example.com:8080",
                        "total_attempts": 500,
                        "success_count": 450,
                        "failure_count": 50,
                        "avg_latency": 0.3,
                        "circuit_breaker_opens": 2,
                    }
                }
            }
        }
    )

    proxies: dict[str, ProxyRetryStats]
