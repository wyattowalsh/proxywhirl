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
from typing import Generic, TypeVar, Any, Optional, Literal, List
from uuid import uuid4

from pydantic import BaseModel, Field, ConfigDict, HttpUrl, PositiveInt, SecretStr


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

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "code": "PROXY_POOL_EMPTY",
            "message": "No proxies available in the pool",
            "details": {"available_proxies": 0, "total_proxies": 0},
            "timestamp": "2025-10-27T12:00:00Z",
        }
    })

    code: ErrorCode = Field(
        description="Machine-readable error code for client handling"
    )
    message: str = Field(
        description="Human-readable error message"
    )
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

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "request_id": "550e8400-e29b-41d4-a716-446655440000",
            "timestamp": "2025-10-27T12:00:00Z",
            "version": "1.0.0",
        }
    })

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

    model_config = ConfigDict(json_schema_extra={
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
    })

    status: str = Field(
        description="Response status: 'success' or 'error'"
    )
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
