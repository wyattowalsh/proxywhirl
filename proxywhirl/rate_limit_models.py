"""
Rate limiting Pydantic models.

Defines configuration, state, and metrics models for rate limiting system.
All models use Pydantic v2 for validation and serialization.
"""

import ipaddress
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from pydantic import (
    BaseModel,
    Field,
    SecretStr,
    computed_field,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic.types import DirectoryPath


class RateLimitTierConfig(BaseModel):
    """
    Configuration for a single rate limit tier.

    Defines request limits, window size, and optional per-endpoint overrides.
    """

    name: str = Field(..., pattern=r"^[a-z0-9_]+$", description="Tier identifier")
    requests_per_window: int = Field(..., gt=0, description="Max requests in window")
    window_size_seconds: int = Field(
        ..., ge=1, le=3600, description="Window size (1-3600 seconds)"
    )
    endpoints: Dict[str, int] = Field(
        default_factory=dict, description="Per-endpoint limit overrides"
    )
    description: str = Field(default="", description="Human-readable tier description")

    @field_validator("endpoints")
    @classmethod
    def validate_endpoints(cls, v: Dict[str, int]) -> Dict[str, int]:
        """Validate endpoint paths and limits."""
        for path, limit in v.items():
            if not path.startswith("/"):
                raise ValueError(f"Endpoint path must start with '/': {path}")
            if limit <= 0:
                raise ValueError(f"Endpoint limit must be positive: {path}")
            # Note: Endpoint limits CAN be stricter (lower) than tier limits
            # (FR-008: most restrictive wins). Validation only ensures
            # positive values and valid paths.
        return v


class RateLimitConfig(BaseSettings):
    """
    Global rate limiting configuration.

    Loaded from YAML file or environment variables.
    Uses Pydantic Settings for automatic environment variable binding.
    """

    model_config = SettingsConfigDict(
        env_prefix="RATE_LIMIT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    enabled: bool = Field(default=True, description="Enable rate limiting globally")
    default_tier: str = Field(
        default="free", description="Default tier for unauthenticated users"
    )
    tiers: List[RateLimitTierConfig] = Field(
        ..., description="List of rate limit tier configurations"
    )
    redis_url: SecretStr = Field(
        default=SecretStr("redis://localhost:6379/1"), description="Redis connection URL"
    )
    redis_enabled: bool = Field(
        default=True, description="Use Redis (fallback: in-memory)"
    )
    fail_open: bool = Field(
        default=False, description="Allow requests if Redis unavailable"
    )
    header_prefix: str = Field(
        default="X-RateLimit-", description="Prefix for rate limit headers"
    )
    whitelist: List[str] = Field(
        default_factory=list, description="User IDs or IPs exempt from rate limiting"
    )

    @model_validator(mode="after")
    def validate_default_tier(self) -> "RateLimitConfig":
        """Ensure default_tier exists in tiers list."""
        tier_names = [t.name for t in self.tiers]
        if self.default_tier not in tier_names:
            raise ValueError(f"default_tier '{self.default_tier}' not found in tiers")
        return self

    @field_validator("whitelist")
    @classmethod
    def validate_whitelist_entries(cls, v: List[str]) -> List[str]:
        """Validate whitelist entries are UUIDs or IP addresses."""
        for entry in v:
            # Try UUID
            try:
                uuid.UUID(entry)
                continue
            except ValueError:
                pass
            # Try IP address
            try:
                ipaddress.ip_address(entry)
                continue
            except ValueError:
                pass
            raise ValueError(
                f"Invalid whitelist entry '{entry}': must be UUID or IP address"
            )
        return v

    @classmethod
    def from_yaml(cls, path: Union[Path, str]) -> "RateLimitConfig":
        """
        Load configuration from YAML file.

        Args:
            path: Path to YAML configuration file

        Returns:
            Loaded RateLimitConfig instance

        Raises:
            FileNotFoundError: If YAML file doesn't exist
            ValueError: If YAML is malformed or validation fails
        """
        config_path = Path(path)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return cls(**data)

    def get_tier_config(self, tier_name: str) -> Optional[RateLimitTierConfig]:
        """
        Get tier configuration by name.

        Args:
            tier_name: Name of the tier to retrieve

        Returns:
            RateLimitTierConfig if found, None otherwise
        """
        for tier in self.tiers:
            if tier.name == tier_name:
                return tier
        return None


class RateLimitState(BaseModel):
    """
    Current rate limit state for a user/IP + endpoint combination.

    Tracks request count, limit, and window timing information.
    """

    key: str = Field(..., description="Redis key (ratelimit:{identifier}:{endpoint})")
    identifier: str = Field(..., description="User ID (UUID) or IP address")
    endpoint: str = Field(..., description="API endpoint path")
    tier: str = Field(..., description="User's tier name")
    current_count: int = Field(..., ge=0, description="Requests in current window")
    limit: int = Field(..., gt=0, description="Max requests in window")
    window_start_ms: int = Field(..., gt=0, description="Window start (Unix ms)")
    window_size_seconds: int = Field(..., gt=0, description="Window size (seconds)")
    reset_at: datetime = Field(..., description="When rate limit resets (UTC)")

    @field_validator("identifier")
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        """Validate identifier is UUID or IP address."""
        # Try UUID
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            pass
        # Try IP address
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            raise ValueError(
                f"Invalid identifier '{v}': must be UUID or IP address"
            )

    @field_validator("endpoint")
    @classmethod
    def validate_endpoint(cls, v: str) -> str:
        """Validate endpoint starts with '/'."""
        if not v.startswith("/"):
            raise ValueError(f"Endpoint must start with '/': {v}")
        return v

    @computed_field  # type: ignore[prop-decorator]
    @property
    def remaining(self) -> int:
        """Remaining requests in current window."""
        return max(0, self.limit - self.current_count)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_exceeded(self) -> bool:
        """Whether rate limit is exceeded."""
        return self.current_count >= self.limit

    @computed_field  # type: ignore[prop-decorator]
    @property
    def retry_after_seconds(self) -> int:
        """Seconds until rate limit resets."""
        now = datetime.now(timezone.utc)
        delta = (self.reset_at - now).total_seconds()
        return max(0, int(delta))


class RateLimitResult(BaseModel):
    """
    Result of a rate limit check operation.

    Indicates whether request is allowed and provides current state.
    """

    allowed: bool = Field(..., description="Whether request is allowed")
    state: RateLimitState = Field(..., description="Current rate limit state")
    reason: Optional[str] = Field(None, description="Reason for denial (if not allowed)")

    @model_validator(mode="after")
    def validate_reason(self) -> "RateLimitResult":
        """Ensure reason is provided when not allowed."""
        if not self.allowed and not self.reason:
            raise ValueError("reason required when allowed=False")
        return self


class RateLimitMetrics(BaseModel):
    """
    Aggregated rate limiting metrics.

    Tracks request counts, throttling rates, and performance metrics.
    """

    total_requests: int = Field(..., ge=0, description="Total rate limit checks")
    throttled_requests: int = Field(..., ge=0, description="Total throttled (429)")
    allowed_requests: int = Field(..., ge=0, description="Total allowed requests")
    by_tier: Dict[str, int] = Field(
        default_factory=dict, description="Throttled requests by tier"
    )
    by_endpoint: Dict[str, int] = Field(
        default_factory=dict, description="Throttled requests by endpoint"
    )
    avg_check_latency_ms: float = Field(..., ge=0.0, description="Avg check latency (ms)")
    p95_check_latency_ms: float = Field(..., ge=0.0, description="P95 check latency (ms)")
    redis_errors: int = Field(..., ge=0, description="Redis connection/operation errors")

    @model_validator(mode="after")
    def validate_totals(self) -> "RateLimitMetrics":
        """Ensure throttled + allowed equals total."""
        if self.throttled_requests + self.allowed_requests != self.total_requests:
            raise ValueError("throttled + allowed must equal total")
        return self
