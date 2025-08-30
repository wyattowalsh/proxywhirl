"""proxywhirl/models/targets.py -- Target-based validation models for ProxyWhirl

This module contains models for target-based proxy validation, enabling
sophisticated health checking against multiple endpoints with individual
scoring and performance tracking.

Features:
- Target definition and configuration
- Per-target health status tracking
- Weighted quality scoring
- Success/failure rate tracking
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from .types import ResponseTimeSeconds, SuccessRate


class TargetDefinition(BaseModel):
    """Definition of a validation target with its configuration."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    target_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Unique identifier for this target (alphanumeric, _, - only)",
    )
    url: str = Field(..., min_length=1, description="Target URL to validate against")
    name: Optional[str] = Field(
        None, max_length=100, description="Human-readable name for this target"
    )
    timeout: Optional[float] = Field(
        None, ge=0.1, le=60.0, description="Custom timeout for this target (seconds)"
    )
    weight: float = Field(
        1.0, ge=0.0, le=10.0, description="Weight for quality scoring (higher = more important)"
    )
    expected_status_codes: Optional[List[int]] = Field(
        None, description="Expected HTTP status codes (default: [200])"
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format and scheme."""
        v = v.strip()
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v

    @property
    def effective_expected_status_codes(self) -> List[int]:
        """Get effective expected status codes (with defaults)."""
        return self.expected_status_codes or [200]


class TargetHealthStatus(BaseModel):
    """Health status for a specific target."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    target_id: str = Field(..., description="Target identifier")
    success_rate: SuccessRate = Field(default=0.0, description="Success rate for this target")
    avg_response_time: Optional[ResponseTimeSeconds] = Field(
        default=None, description="Average response time for this target"
    )
    last_success: Optional[datetime] = Field(
        default=None, description="Timestamp of last successful validation"
    )
    last_failure: Optional[datetime] = Field(
        default=None, description="Timestamp of last failed validation"
    )
    consecutive_failures: int = Field(default=0, ge=0, description="Count of consecutive failures")
    consecutive_successes: int = Field(
        default=0, ge=0, description="Count of consecutive successes"
    )
    total_attempts: int = Field(default=0, ge=0, description="Total validation attempts")
    total_successes: int = Field(default=0, ge=0, description="Total successful validations")

    # Computed quality score for this specific target
    @computed_field
    @property
    def quality_score(self) -> float:
        """Calculate quality score based on success rate and response time."""
        if self.total_attempts == 0:
            return 0.0
        
        # Base score from success rate
        base_score = self.success_rate
        
        # Response time bonus/penalty
        if self.avg_response_time is not None:
            if self.avg_response_time < 1.0:  # Fast response
                base_score = min(1.0, base_score * 1.1)
            elif self.avg_response_time > 5.0:  # Slow response
                base_score *= 0.9
        
        # Consecutive failures penalty
        if self.consecutive_failures > 0:
            penalty = min(0.5, self.consecutive_failures * 0.1)
            base_score = max(0.0, base_score - penalty)
        
        return round(base_score, 4)

    def record_success(self, response_time: Optional[float] = None) -> None:
        """Record a successful validation."""
        self.total_attempts += 1
        self.total_successes += 1
        self.consecutive_successes += 1
        self.consecutive_failures = 0
        self.last_success = datetime.now(timezone.utc)
        
        # Update success rate
        self.success_rate = self.total_successes / self.total_attempts
        
        # Update average response time
        if response_time is not None:
            if self.avg_response_time is None:
                self.avg_response_time = response_time
            else:
                # Simple moving average
                self.avg_response_time = (self.avg_response_time + response_time) / 2

    def record_failure(self) -> None:
        """Record a failed validation."""
        self.total_attempts += 1
        self.consecutive_failures += 1
        self.consecutive_successes = 0
        self.last_failure = datetime.now(timezone.utc)
        
        # Update success rate
        self.success_rate = self.total_successes / self.total_attempts
