"""Data models for rate limiting."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class RateLimit(BaseModel):
    """Rate limit configuration."""

    max_requests: int = Field(..., description="Maximum requests allowed")
    time_window: int = Field(..., description="Time window in seconds")
    burst_allowance: int | None = Field(None, description="Burst capacity (token bucket)")


class RateLimitEvent(BaseModel):
    """Rate limit event for logging."""

    timestamp: datetime
    proxy_id: str
    event_type: str  # throttled, exceeded, adaptive_change
    details: dict
