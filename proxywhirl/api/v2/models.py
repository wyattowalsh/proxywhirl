"""API v2 - Enhanced Pydantic models for the next-generation REST API.

v2 introduces structured metadata, distributed tracing, and improved error handling.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Generic, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ErrorCode(str, Enum):
    """API v2 error codes."""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_PROXY_FORMAT = "INVALID_PROXY_FORMAT"
    PROXY_POOL_EMPTY = "PROXY_POOL_EMPTY"
    PROXY_NOT_FOUND = "PROXY_NOT_FOUND"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    PROXY_UNAVAILABLE = "PROXY_UNAVAILABLE"
    TARGET_UNREACHABLE = "TARGET_UNREACHABLE"
    REQUEST_TIMEOUT = "REQUEST_TIMEOUT"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


class ErrorDetail(BaseModel):
    """Detailed error information in API responses."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "PROXY_POOL_EMPTY",
                "message": "No proxies available",
                "details": {"available": 0, "total": 0},
            }
        }
    )

    code: ErrorCode
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RequestMetadata(BaseModel):
    """Metadata about incoming request."""

    model_config = ConfigDict(frozen=True)

    request_id: UUID = Field(default_factory=uuid4, description="Unique request ID")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Request timestamp",
    )
    api_version: str = Field(default="2.0", description="API version")
    client_ip: str | None = Field(None, description="Client IP address")


class ResponseMetadata(BaseModel):
    """Metadata about outgoing response."""

    model_config = ConfigDict(frozen=True)

    request_id: UUID
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time_ms: float = Field(description="Request processing time in ms")
    api_version: str = "2.0"
    trace_id: UUID | None = Field(None, description="Distributed trace ID")


class APIResponse(BaseModel, Generic[T]):
    """Standard API v2 response envelope."""

    model_config = ConfigDict(generic=True)

    success: bool = Field(description="Whether request succeeded")
    data: T | None = Field(None, description="Response payload")
    error: ErrorDetail | None = Field(None, description="Error details if failed")
    metadata: ResponseMetadata


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""

    model_config = ConfigDict(generic=True)

    items: list[T]
    total: int = Field(description="Total items available")
    page: int = Field(ge=1, description="Current page number")
    page_size: int = Field(ge=1, le=1000, description="Items per page")
    total_pages: int = Field(description="Total pages available")
    has_next: bool = Field(description="Whether next page exists")
    has_previous: bool = Field(description="Whether previous page exists")


class ProxyResourceV2(BaseModel):
    """Proxy resource in API v2."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "proxy-uuid-123",
                "protocol": "http",
                "host": "1.2.3.4",
                "port": 8080,
                "is_active": True,
                "last_verified": "2025-10-27T12:00:00Z",
                "custom_headers": {"Authorization": "Bearer token"},
            }
        }
    )

    id: str
    protocol: str
    host: str
    port: int
    is_active: bool
    last_verified: datetime | None = None
    custom_headers: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RateLimitInfo(BaseModel):
    """Rate limit information in response headers."""

    model_config = ConfigDict(frozen=True)

    limit: int = Field(description="Requests allowed per window")
    remaining: int = Field(description="Requests remaining")
    reset_at: datetime = Field(description="When limit resets")
    window_seconds: int = Field(description="Rate limit window in seconds")


class StreamingOptions(BaseModel):
    """Options for streaming responses."""

    format: str = Field(
        default="ndjson",
        description="Streaming format: ndjson, sse, msgpack",
    )
    chunk_size: int = Field(default=100, ge=1, le=10000)
    include_metadata: bool = Field(default=False)
