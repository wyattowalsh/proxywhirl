"""
Data models for ProxyWhirl using Pydantic v2.
"""

from __future__ import annotations

import asyncio
import threading
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Protocol, TypedDict, runtime_checkable
from uuid import UUID, uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    PrivateAttr,
    SecretStr,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings
from loguru import logger

if TYPE_CHECKING:
    import httpx


# ============================================================================
# CONFIGURATION TYPEDDICTS
# ============================================================================


class ProxyPoolConfigDict(TypedDict, total=False):
    """Type definition for proxy pool configuration dictionaries."""

    max_size: int
    health_check_interval: float
    health_check_timeout: float
    stale_proxy_threshold: float
    auto_remove_unhealthy: bool


class StrategyConfigDict(TypedDict, total=False):
    """Type definition for rotation strategy configuration dictionaries."""

    weights: dict[str, float]
    ema_alpha: float
    session_stickiness_duration_seconds: int
    preferred_countries: list[str]
    preferred_regions: list[str]
    geo_fallback_enabled: bool
    geo_secondary_strategy: str


class CircuitBreakerConfigDict(TypedDict, total=False):
    """Type definition for circuit breaker configuration dictionaries."""

    failure_threshold: int
    window_duration: float
    timeout_duration: float


# ============================================================================
# ENUMS
# ============================================================================


class HealthStatus(str, Enum):
    """Proxy health status states."""

    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    DEAD = "dead"


class ProxySource(str, Enum):
    """Origin type of proxy."""

    USER = "user"
    FETCHED = "fetched"
    API = "api"
    FILE = "file"


class ProxyFormat(str, Enum):
    """Supported proxy list formats."""

    JSON = "json"
    CSV = "csv"
    TSV = "tsv"
    PLAIN_TEXT = "plain_text"
    HTML_TABLE = "html_table"
    CUSTOM = "custom"


class RenderMode(str, Enum):
    """Page rendering modes for fetching proxy lists."""

    STATIC = "static"
    JAVASCRIPT = "javascript"
    BROWSER = "browser"  # Full browser rendering with Playwright
    AUTO = "auto"


class ValidationLevel(str, Enum):
    """Proxy validation strictness levels.

    BASIC: Format + TCP connectivity validation (fast, ~100ms)
    STANDARD: BASIC + HTTP request test (medium, ~500ms)
    FULL: STANDARD + Anonymity check (comprehensive, ~2s)
    """

    BASIC = "basic"
    STANDARD = "standard"
    FULL = "full"


# ============================================================================
# STRATEGY MODELS
# ============================================================================


class CircuitBreakerConfig(BaseModel):
    """Configuration for circuit breaker behavior.

    Attributes:
        failure_threshold: Number of failures before opening circuit
        window_duration: Rolling window duration in seconds
        timeout_duration: How long circuit stays open before testing recovery
    """

    failure_threshold: int = Field(default=5, ge=1, description="Failures before opening circuit")
    window_duration: float = Field(
        default=60.0, gt=0, description="Rolling window duration (seconds)"
    )
    timeout_duration: float = Field(
        default=30.0, gt=0, description="Circuit open duration (seconds)"
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)


class StrategyConfig(BaseModel):
    """Configuration for rotation strategies.

    This model provides flexible configuration options for all rotation
    strategies, allowing customization of weights, EMA parameters, session
    settings, and geo-targeting constraints.
    """

    # Weight configuration for weighted strategies
    weights: dict[str, float] | None = Field(
        default=None, description="Proxy weights keyed by proxy ID or URL"
    )

    # EMA configuration for performance-based strategies
    ema_alpha: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="EMA smoothing factor (0-1). Higher = more weight to recent values",
    )

    # Session configuration for session-based strategies
    session_stickiness_duration_seconds: int = Field(
        default=300, ge=0, description="How long a session should stick to the same proxy"
    )

    # Geo-targeting configuration
    preferred_countries: list[str] | None = Field(
        default=None, description="List of ISO 3166-1 alpha-2 country codes (e.g., ['US', 'GB'])"
    )
    preferred_regions: list[str] | None = Field(
        default=None, description="List of region names (e.g., ['North America', 'Europe'])"
    )
    geo_fallback_enabled: bool = Field(
        default=True,
        description="Whether to fallback to any proxy when target location unavailable",
    )
    geo_secondary_strategy: str = Field(
        default="round_robin",
        description="Secondary strategy for selecting from filtered geo proxies",
    )

    # Fallback strategy configuration
    fallback_strategy: str | None = Field(
        default="random",
        description="Strategy to use when primary strategy fails or metadata missing",
    )

    # Performance thresholds
    max_response_time_ms: float | None = Field(
        default=None, description="Maximum acceptable response time in milliseconds"
    )
    min_success_rate: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Minimum acceptable success rate (0-1)"
    )

    # Window configuration
    window_duration_seconds: int = Field(
        default=3600,
        ge=60,
        description="Sliding window duration for counter resets (default 1 hour)",
    )

    # Exploration configuration for performance-based strategies
    exploration_count: int = Field(
        default=5,
        ge=0,
        description="Minimum trials for new proxies before performance-based selection (default 5)",
    )

    # Generic metadata for custom configurations
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional custom metadata for strategy-specific configuration",
    )

    model_config = ConfigDict(extra="forbid")


class SelectionContext(BaseModel):
    """Context information for proxy selection decisions.

    This model captures all the contextual information that might be relevant
    for intelligent proxy selection, including session tracking, target URL
    characteristics, and previous attempt history.
    """

    # Session tracking
    session_id: str | None = Field(
        default=None, description="Unique session identifier for sticky sessions"
    )

    # Target information
    target_url: str | None = Field(
        default=None, description="The URL being accessed (for domain-based routing)"
    )
    target_country: str | None = Field(
        default=None, description="Preferred country for geo-targeting (ISO 3166-1 alpha-2)"
    )
    target_region: str | None = Field(
        default=None, description="Preferred region for geo-targeting"
    )

    # Request metadata
    request_priority: int | None = Field(
        default=None, ge=0, le=10, description="Priority level (0-10, higher = more important)"
    )
    timeout_ms: float | None = Field(default=None, description="Request timeout in milliseconds")

    # Previous attempts (for retry logic)
    failed_proxy_ids: list[str] = Field(
        default_factory=list, description="List of proxy IDs that have failed for this request"
    )
    attempt_number: int = Field(default=1, ge=1, description="Current attempt number (1-indexed)")

    # Custom metadata
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional context for custom selection logic"
    )

    model_config = ConfigDict(extra="allow")  # Allow custom fields for extensibility


class Session(BaseModel):
    """Session tracking for sticky proxy assignments.

    This model maintains the relationship between a session and its assigned
    proxy, with TTL support and usage tracking.
    """

    session_id: str = Field(description="Unique session identifier")
    proxy_id: str = Field(description="ID of the proxy assigned to this session")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the session was created",
    )
    expires_at: datetime = Field(description="When the session expires (TTL)")
    last_used_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last time this session was used",
    )
    request_count: int = Field(
        default=0, ge=0, description="Number of requests made in this session"
    )

    def is_expired(self) -> bool:
        """Check if the session has expired.

        Returns:
            True if current time >= expires_at
        """
        return datetime.now(timezone.utc) >= self.expires_at

    def touch(self) -> None:
        """Update last_used_at timestamp and increment request_count."""
        self.last_used_at = datetime.now(timezone.utc)
        self.request_count += 1

    model_config = ConfigDict(extra="forbid")


# ============================================================================
# MODELS
# ============================================================================


class ProxyCredentials(BaseModel):
    """Secure credential storage for proxy authentication."""

    username: SecretStr
    password: SecretStr
    auth_type: Literal["basic", "digest", "bearer"] = "basic"
    additional_headers: dict[str, str] = Field(default_factory=dict)

    def to_httpx_auth(self) -> httpx.BasicAuth:
        """Convert to httpx BasicAuth object."""
        import httpx

        return httpx.BasicAuth(
            username=self.username.get_secret_value(),
            password=self.password.get_secret_value(),
        )

    def to_dict(self, reveal: bool = False) -> dict[str, Any]:
        """Serialize credentials, optionally revealing secrets."""
        if reveal:
            return {
                "username": self.username.get_secret_value(),
                "password": self.password.get_secret_value(),
                "auth_type": self.auth_type,
                "additional_headers": self.additional_headers,
            }
        return {
            "username": "**********",
            "password": "**********",
            "auth_type": self.auth_type,
            "additional_headers": self.additional_headers,
        }


class Proxy(BaseModel):
    """Represents a single proxy server with connection details and metadata."""

    id: UUID = Field(default_factory=uuid4)
    url: str  # Changed from HttpUrl to allow socks:// URLs
    protocol: Literal["http", "https", "socks4", "socks5"] | None = None
    username: SecretStr | None = None
    password: SecretStr | None = None
    allow_local: bool = Field(
        default=False,
        description="Allow localhost/internal IPs (127.0.0.1, 192.168.x.x, etc.). Default False for production.",
    )
    health_status: HealthStatus = HealthStatus.UNKNOWN
    last_success_at: datetime | None = None
    last_failure_at: datetime | None = None
    # Enhanced request tracking (Phase 2: Intelligent Rotation Strategies)
    requests_started: int = 0  # Total requests initiated
    requests_completed: int = 0  # Total requests finished (success or failure)
    requests_active: int = 0  # Currently in-flight requests
    total_requests: int = 0  # Legacy field for backwards compatibility. Use requests_completed instead. To be removed in v2.0.
    total_successes: int = 0
    total_failures: int = 0
    average_response_time_ms: float | None = None
    latency_ms: float | None = None  # Last measured latency in milliseconds
    # EMA (Exponential Moving Average) tracking for performance-based strategies
    ema_response_time_ms: float | None = None  # Current EMA value
    # DEPRECATED: ema_alpha on Proxy is deprecated. Strategies should use
    # StrategyConfig.ema_alpha and pass alpha to update_metrics/record_success/
    # complete_request methods. This field is retained for storage serialization
    # and backward compatibility only. Strategies using StrategyState manage
    # their own per-proxy metrics with independent alpha values.
    ema_alpha: float = 0.2  # Deprecated in v1.8+: use StrategyConfig.ema_alpha in strategies instead. Will be removed in v2.0. See migration guide: docs/source/guides/migration-v2.md
    # Sliding window for counter staleness prevention
    window_start: datetime | None = None  # Start time of current window
    window_duration_seconds: int = 3600  # Window duration (default 1 hour)
    # Geo-location for geo-targeted strategies
    country_code: str | None = None  # ISO 3166-1 alpha-2 code (e.g., "US", "GB")
    region: str | None = None  # Region/state within country (optional)
    consecutive_failures: int = 0
    # Health monitoring fields (Feature 006)
    last_health_check: datetime | None = None  # Last health check timestamp
    consecutive_successes: int = 0  # Consecutive successful health checks
    recovery_attempt: int = 0  # Current recovery attempt count
    next_check_time: datetime | None = None  # Scheduled next health check
    last_health_error: str | None = None  # Last health check error message
    total_checks: int = 0  # Total health checks performed
    total_health_failures: int = 0  # Total health check failures
    tags: set[str] = Field(default_factory=set)
    source: ProxySource = ProxySource.USER
    source_url: HttpUrl | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    # TTL fields for automatic expiration
    ttl: int | None = None  # Time-to-live in seconds
    expires_at: datetime | None = None  # Explicit expiration timestamp
    # Cost optimization fields
    cost_per_request: float | None = Field(
        default=0.0,
        ge=0.0,
        description="Cost per request in arbitrary units (0.0 = free, higher = more expensive)",
    )

    # Private lock for thread-safe sliding window operations
    _window_lock: threading.Lock = PrivateAttr(default_factory=threading.Lock)

    @field_validator("url")
    @classmethod
    def validate_url_scheme(cls, v: str) -> str:
        """Validate URL has a valid proxy scheme."""
        import re

        # Extract scheme from URL
        scheme_match = re.match(r"^([a-z0-9]+)://", v.lower())
        if not scheme_match:
            raise ValueError(
                f"URL must have a scheme (http://, https://, socks4://, or socks5://): {v}"
            )

        scheme = scheme_match.group(1)
        allowed_schemes = {"http", "https", "socks4", "socks5"}

        if scheme not in allowed_schemes:
            raise ValueError(
                f"Invalid proxy scheme '{scheme}'. Allowed schemes: {', '.join(sorted(allowed_schemes))}"
            )

        return v

    @field_validator("url")
    @classmethod
    def validate_port_range(cls, v: str) -> str:
        """Validate port number is in valid range (1-65535)."""
        import re

        # Extract port from URL - handle various formats:
        # scheme://host:port
        # scheme://user:pass@host:port
        # Also handle negative ports like :-1
        port_match = re.search(r":(-?\d+)(?:/|$)", v)

        if port_match:
            port = int(port_match.group(1))
            if port < 1 or port > 65535:
                raise ValueError(f"Port must be between 1 and 65535, got {port}")

        return v

    @field_validator("url")
    @classmethod
    def validate_proxy_url_format(cls, v: str) -> str:
        """Validate full proxy URL shape using the shared parser."""
        from proxywhirl.utils import parse_proxy_url

        try:
            parse_proxy_url(v)
        except ValueError as exc:
            raise ValueError(f"Invalid proxy URL: {v}") from exc

        return v

    @model_validator(mode="after")
    def validate_local_addresses(self) -> Proxy:
        """Reject localhost/internal IPs unless allow_local=True."""
        import ipaddress
        import re

        if self.allow_local:
            return self  # Skip validation if local addresses are allowed

        # Extract hostname/IP from URL
        # Handle formats: scheme://host:port, scheme://user:pass@host:port
        url_str = str(self.url)

        # Remove scheme
        no_scheme = re.sub(r"^[a-z0-9]+://", "", url_str.lower())

        # Remove credentials if present (user:pass@)
        no_creds = re.sub(r"^[^@]+@", "", no_scheme)

        # Extract host (before : or /) - handle IPv6 brackets
        # For IPv6: [::1]:port or [2001:db8::1]:port
        ipv6_match = re.match(r"\[([^\]]+)\]", no_creds)
        if ipv6_match:
            host = ipv6_match.group(1)
        else:
            host_match = re.match(r"([^:/]+)", no_creds)
            if not host_match:
                return self  # Can't extract host, skip validation
            host = host_match.group(1)

        # Check for localhost patterns
        localhost_patterns = [
            "localhost",
            "127.",  # 127.0.0.1, 127.0.0.2, etc.
            "::1",  # IPv6 localhost
        ]

        for pattern in localhost_patterns:
            if host.startswith(pattern):
                raise ValueError(
                    f"Localhost addresses not allowed in production (set allow_local=True to override): {host}"
                )

        # Try to parse as IP address and check if it's private/reserved
        try:
            ip = ipaddress.ip_address(host)

            # Check for private/internal IP ranges
            if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local:
                raise ValueError(
                    f"Private/internal IP addresses not allowed in production (set allow_local=True to override): {host}"
                )
        except ValueError as e:
            # Check if this is an IP validation error we raised, or just a parsing error
            if "not allowed in production" in str(e):
                # Re-raise our own validation errors
                raise
            # Otherwise it's not an IP address, it's a hostname - that's fine
            pass

        return self

    @model_validator(mode="after")
    def extract_protocol_from_url(self) -> Proxy:
        """Extract protocol from URL if not explicitly provided."""
        if self.protocol is None and self.url:
            url_str = str(self.url).lower()
            if url_str.startswith("http://"):
                self.protocol = "http"
            elif url_str.startswith("https://"):
                self.protocol = "https"
            elif url_str.startswith("socks4://"):
                self.protocol = "socks4"
            elif url_str.startswith("socks5://"):
                self.protocol = "socks5"
        return self

    @model_validator(mode="after")
    def validate_credentials(self) -> Proxy:
        """Ensure username and password are both present or both absent."""
        has_username = self.username is not None
        has_password = self.password is not None
        if has_username != has_password:
            raise ValueError("Both username and password must be provided together")
        return self

    @model_validator(mode="after")
    def set_expiration_from_ttl(self) -> Proxy:
        """Set expires_at timestamp if ttl is provided."""
        if self.ttl is not None and self.expires_at is None:
            self.expires_at = self.created_at + timedelta(seconds=self.ttl)
        return self

    @field_validator("latency_ms")
    @classmethod
    def validate_latency_non_negative(cls, v: float | None) -> float | None:
        """Validate latency_ms is non-negative."""
        if v is not None and v < 0:
            raise ValueError(f"latency_ms must be non-negative, got {v}")
        return v

    @field_validator("average_response_time_ms", "ema_response_time_ms")
    @classmethod
    def validate_response_time_non_negative(cls, v: float | None) -> float | None:
        """Validate response time fields are non-negative."""
        if v is not None and v < 0:
            raise ValueError(f"Response time must be non-negative, got {v}")
        return v

    @field_validator(
        "total_requests",
        "total_successes",
        "total_failures",
        "requests_started",
        "requests_completed",
        "requests_active",
        "consecutive_failures",
        "consecutive_successes",
        "recovery_attempt",
        "total_checks",
        "total_health_failures",
    )
    @classmethod
    def validate_counters_non_negative(cls, v: int) -> int:
        """Validate counter fields are non-negative."""
        if v < 0:
            raise ValueError(f"Counter must be non-negative, got {v}")
        return v

    @property
    def success_rate(self) -> float:
        """Calculate success rate, clamped to [0.0, 1.0]."""
        if self.total_requests == 0:
            return 0.0
        rate = self.total_successes / self.total_requests
        # Clamp to valid range [0.0, 1.0] for safety
        return max(0.0, min(1.0, rate))

    @property
    def is_expired(self) -> bool:
        """Check if proxy has expired based on TTL or explicit expiration time.

        Returns:
            True if proxy has expired, False otherwise. Always False if no TTL/expires_at set.
        """
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def is_healthy(self) -> bool:
        """Check if proxy is healthy."""
        return self.health_status == HealthStatus.HEALTHY

    @property
    def credentials(self) -> ProxyCredentials | None:
        """Get credentials if present."""
        if self.username and self.password:
            return ProxyCredentials(
                username=self.username,
                password=self.password,
            )
        return None

    def update_metrics(self, response_time_ms: float, alpha: float | None = None) -> None:
        """Update EMA and average response time metrics.

        This method centralizes all response time metric updates to ensure
        consistency across the codebase. Both average_response_time_ms and
        ema_response_time_ms use the same alpha value.

        Args:
            response_time_ms: Response time in milliseconds
            alpha: EMA smoothing factor (0-1). Higher values weight recent
                   observations more heavily. If not provided, falls back to
                   self.ema_alpha for backward compatibility. Strategies should
                   pass their configured StrategyConfig.ema_alpha for consistent
                   behavior, or use StrategyState for independent per-proxy metrics.
        """
        # Use provided alpha or fall back to instance's ema_alpha (deprecated path)
        effective_alpha = alpha if alpha is not None else self.ema_alpha

        # Update average response time using EMA with configurable alpha
        if self.average_response_time_ms is None:
            self.average_response_time_ms = response_time_ms
        else:
            self.average_response_time_ms = (
                effective_alpha * response_time_ms
                + (1 - effective_alpha) * self.average_response_time_ms
            )

        # Update EMA response time using the same alpha
        if self.ema_response_time_ms is None:
            self.ema_response_time_ms = response_time_ms
        else:
            # EMA formula: EMA_new = alpha * value + (1 - alpha) * EMA_old
            self.ema_response_time_ms = (
                effective_alpha * response_time_ms
                + (1 - effective_alpha) * self.ema_response_time_ms
            )

    def record_success(self, response_time_ms: float, alpha: float | None = None) -> None:
        """Record a successful request.

        Args:
            response_time_ms: Response time in milliseconds
            alpha: Optional EMA smoothing factor for metrics update
        """
        self.total_requests += 1
        self.total_successes += 1
        self.consecutive_failures = 0
        self.last_success_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

        # Update metrics using centralized method
        self.update_metrics(response_time_ms, alpha=alpha)

        # Update health status
        if self.health_status in (HealthStatus.UNKNOWN, HealthStatus.DEGRADED):
            self.health_status = HealthStatus.HEALTHY

    def record_failure(self, error: str | None = None) -> None:
        """Record a failed request."""
        self.total_requests += 1
        self.total_failures += 1
        self.consecutive_failures += 1
        self.last_failure_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

        # Update health status based on consecutive failures
        if self.consecutive_failures >= 5:
            self.health_status = HealthStatus.DEAD
        elif self.consecutive_failures >= 3:
            self.health_status = HealthStatus.UNHEALTHY
        elif self.consecutive_failures >= 1:
            self.health_status = HealthStatus.DEGRADED

        # Store error in metadata if provided
        if error:
            if "last_errors" not in self.metadata:
                self.metadata["last_errors"] = []
            self.metadata["last_errors"].append(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "error": error,
                }
            )
            # Keep only last 10 errors
            self.metadata["last_errors"] = self.metadata["last_errors"][-10:]

    def start_request(self) -> None:
        """Mark a request as started (for tracking in-flight requests).

        This should be called when a request is about to be made through this proxy.
        Increments both requests_started and requests_active counters.

        Thread-safe: Uses internal lock to prevent race conditions.
        """
        with self._window_lock:
            self.requests_started += 1
            self.requests_active += 1
            self.updated_at = datetime.now(timezone.utc)

            # Initialize window if not set
            if self.window_start is None:
                self.window_start = datetime.now(timezone.utc)

    def complete_request(
        self, success: bool, response_time_ms: float, alpha: float | None = None
    ) -> None:
        """Mark a request as complete and update metrics.

        Args:
            success: Whether the request was successful
            response_time_ms: Response time in milliseconds
            alpha: Optional EMA smoothing factor. Strategies can pass their
                   configured alpha to ensure consistent metric calculations
                   without mutating proxy state.

        This method decrements requests_active, increments requests_completed,
        updates EMA response time, and delegates to record_success/record_failure.

        Thread-safe: Uses internal lock to prevent race conditions.
        """
        with self._window_lock:
            # Decrement active count
            if self.requests_active > 0:
                self.requests_active -= 1

            # Increment completed count
            self.requests_completed += 1

        # Delegate to existing success/failure recording
        # Note: record_success() calls update_metrics() which updates both
        # average_response_time_ms and ema_response_time_ms consistently
        if success:
            self.record_success(response_time_ms, alpha=alpha)
        else:
            self.record_failure()

    def reset_window(self) -> None:
        """Reset the sliding window counters.

        This is called when the window duration has elapsed, preventing
        counter staleness and unbounded memory growth.

        Thread-safe: Uses internal lock to prevent race conditions.
        """
        with self._window_lock:
            now = datetime.now(timezone.utc)
            self.window_start = now
            self.requests_started = 0
            self.requests_completed = 0
            # Note: Don't reset requests_active as those are truly active
            self.updated_at = now

    def is_window_expired(self) -> bool:
        """Check if the current sliding window has expired.

        Returns:
            True if window duration has elapsed since window_start

        Thread-safe: Uses internal lock to prevent race conditions.
        """
        with self._window_lock:
            if self.window_start is None:
                return False

            now = datetime.now(timezone.utc)
            elapsed = (now - self.window_start).total_seconds()
            return elapsed >= self.window_duration_seconds

    def reset_if_expired(self) -> bool:
        """Atomically check if window is expired and reset if needed.

        This method prevents Time-of-Check to Time-of-Use (TOCTOU) race conditions
        by performing the expiration check and reset within a single lock acquisition.

        Returns:
            True if window was expired and has been reset, False otherwise

        Thread-safe: Uses internal lock to ensure atomic check-and-reset.
        """
        with self._window_lock:
            # Double-checked locking pattern: check expiration under lock
            if self.window_start is None:
                return False

            now = datetime.now(timezone.utc)
            elapsed = (now - self.window_start).total_seconds()

            if elapsed >= self.window_duration_seconds:
                # Window is expired, reset it atomically
                self.window_start = now
                self.requests_started = 0
                self.requests_completed = 0
                # Note: Don't reset requests_active as those are truly active
                self.updated_at = now
                return True

            return False


class ProxyChain(BaseModel):
    """Represents a chain of proxies for tunneling requests.

    A proxy chain allows requests to be routed through multiple proxies in sequence,
    where each proxy connects to the next one in the chain. This is useful for:
    - Enhanced anonymity through multi-hop routing
    - Geographic routing through specific locations
    - Bypassing network restrictions

    Note: Full CONNECT tunneling implementation requires additional infrastructure.
    This model provides the data structure and basic support for chaining.

    Example:
        >>> chain = ProxyChain(
        ...     proxies=[
        ...         Proxy(url="http://proxy1.com:8080"),
        ...         Proxy(url="http://proxy2.com:8080"),
        ...     ],
        ...     name="geo_chain",
        ...     description="Route through US then UK"
        ... )
    """

    proxies: list[Proxy] = Field(
        ..., min_length=2, description="Ordered list of proxies to chain (minimum 2 required)"
    )
    name: str | None = Field(default=None, description="Human-readable name for this chain")
    description: str | None = Field(
        default=None, description="Description of the chain's purpose or routing"
    )

    @model_validator(mode="after")
    def validate_chain_length(self) -> ProxyChain:
        """Ensure chain has at least 2 proxies."""
        if len(self.proxies) < 2:
            raise ValueError("Proxy chain must contain at least 2 proxies")
        return self

    @property
    def entry_proxy(self) -> Proxy:
        """Get the first proxy in the chain (entry point)."""
        return self.proxies[0]

    @property
    def exit_proxy(self) -> Proxy:
        """Get the last proxy in the chain (exit point)."""
        return self.proxies[-1]

    @property
    def chain_length(self) -> int:
        """Get the number of proxies in the chain."""
        return len(self.proxies)

    def get_chain_urls(self) -> list[str]:
        """Get list of proxy URLs in chain order.

        Returns:
            List of proxy URLs from entry to exit
        """
        return [proxy.url for proxy in self.proxies]


class ProxyConfiguration(BaseSettings):
    """Global configuration settings for the proxy system."""

    timeout: int = 30
    max_retries: int = 3
    verify_ssl: bool = True
    follow_redirects: bool = True
    pool_connections: int = 10
    pool_max_keepalive: int = 20
    pool_timeout: int = 30
    health_check_enabled: bool = True
    health_check_interval_seconds: int = 300
    health_check_url: HttpUrl = Field(default="http://httpbin.org/ip")  # type: ignore
    health_check_timeout: int = 10
    log_level: str = "WARNING"
    log_format: Literal["auto", "json", "text"] = "auto"
    log_redact_credentials: bool = True
    storage_backend: Literal["memory", "sqlite", "file"] = "memory"
    storage_path: Path | None = None

    # Request queuing configuration
    queue_enabled: bool = Field(
        default=False, description="Enable request queuing when rate limited"
    )
    queue_size: int = Field(
        default=100, ge=1, le=10000, description="Maximum number of queued requests (1-10000)"
    )

    @field_validator("timeout", "max_retries", "pool_connections", "pool_timeout")
    @classmethod
    def validate_positive(cls, v: int) -> int:
        """Ensure value is positive."""
        if v <= 0:
            raise ValueError("Value must be positive")
        return v

    @model_validator(mode="after")
    def validate_storage(self) -> ProxyConfiguration:
        """Validate storage configuration."""
        if self.storage_backend in ("sqlite", "file") and self.storage_path is None:
            raise ValueError(f"storage_path required for {self.storage_backend} backend")
        return self

    model_config = {"frozen": True}


class ProxySourceConfig(BaseModel):
    """Configuration for a proxy list source."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    url: HttpUrl
    format: ProxyFormat = ProxyFormat.JSON
    render_mode: RenderMode = RenderMode.AUTO
    parser: str | None = None
    custom_parser: Any | None = Field(
        default=None,
        description="Custom parser function that takes content string and returns list of proxy dicts",
    )
    protocol: str | None = Field(
        default=None,
        description="Default protocol for plain text sources (http, socks4, socks5). "
        "If None, defaults to http for IP:PORT format.",
    )
    wait_selector: str | None = None
    wait_timeout: int = 30000
    refresh_interval: int = 3600
    enabled: bool = True
    priority: int = 0
    trusted: bool = Field(
        default=False,
        description="Whether this source provides pre-validated/checked proxies",
    )
    headers: dict[str, str] = Field(default_factory=dict)
    auth: tuple[str, str] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class BootstrapConfig(BaseModel):
    """Configuration for the lazy bootstrap that runs on first request when the pool is empty.

    Attributes:
        enabled: Whether automatic bootstrap is enabled (set False to supply proxies manually)
        sources: Explicit list of sources to fetch from. None = random sample from ALL_SOURCES.
        sample_size: How many sources to randomly pick when sources is None
        validate_proxies: Whether to validate fetched proxies
        timeout: Validation timeout in seconds
        max_concurrent: Maximum concurrent validation requests
        show_progress: Show Rich progress bars. None = auto-detect TTY on stderr.
    """

    enabled: bool = True
    sources: list[ProxySourceConfig] | None = None
    sample_size: int = Field(default=10, ge=1)
    validate_proxies: bool = True
    timeout: int = Field(default=10, ge=1)
    max_concurrent: int = Field(default=100, ge=1)
    show_progress: bool | None = None

    max_proxies: int | None = Field(default=None, ge=1)

    model_config = ConfigDict(frozen=True, extra="forbid")


class SourceStats(BaseModel):
    """Statistics for a proxy source."""

    source_url: str
    total_fetched: int = 0
    valid_count: int = 0
    invalid_count: int = 0
    last_fetch_at: datetime | None = None
    last_fetch_duration_ms: float | None = None
    fetch_failure_count: int = 0
    last_error: str | None = None


class ProxyPool(BaseModel):
    """Collection of proxies with management capabilities.

    Thread-safe proxy pool with RLock protection for concurrent access.
    All mutating operations are automatically protected by a reentrant lock.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: UUID = Field(default_factory=uuid4)
    name: str
    proxies: list[Proxy] = Field(default_factory=list)
    max_pool_size: int = 100
    auto_remove_dead: bool = False
    dead_proxy_threshold: int = 5
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Runtime lock (not serialized)
    _lock: threading.RLock = PrivateAttr(default_factory=threading.RLock)
    # O(1) lookup index for proxy IDs (not serialized)
    _id_index: dict[UUID, Proxy] = PrivateAttr(default_factory=dict)
    # O(1) lookup index for proxy URLs (not serialized)
    _url_index: set[str] = PrivateAttr(default_factory=set)

    def __init__(self, **data: Any) -> None:
        """
        Initialize ProxyPool with thread lock and ID/URL indexes.

        Creates a new proxy pool with thread-safe access via RLock.
        Also builds fast O(1) lookup indexes for proxy IDs and URLs.

        Args:
            **data : dict
                Pool configuration including name, proxies list, max_pool_size, etc.

        Returns:
            None

        Example:
            >>> pool = ProxyPool(name="default", proxies=[proxy1, proxy2])
            >>> print(pool.size)  # 2
        """
        super().__init__(**data)
        # Use object.__setattr__ to bypass Pydantic's field validation
        object.__setattr__(self, "_lock", threading.RLock())
        # Build ID index from initial proxies
        id_index: dict[UUID, Proxy] = {}
        url_index: set[str] = set()
        for proxy in self.proxies:
            if proxy.id:
                id_index[proxy.id] = proxy
            url_index.add(proxy.url)
        object.__setattr__(self, "_id_index", id_index)
        # O(1) URL-based membership check
        object.__setattr__(self, "_url_index", url_index)

    @property
    def size(self) -> int:
        """Get pool size (thread-safe)."""
        with self._lock:
            return len(self.proxies)

    @property
    def healthy_count(self) -> int:
        """Count healthy proxies (thread-safe)."""
        with self._lock:
            return sum(1 for p in self.proxies if p.is_healthy)

    @property
    def unhealthy_count(self) -> int:
        """Count unhealthy proxies (thread-safe)."""
        with self._lock:
            return sum(1 for p in self.proxies if not p.is_healthy)

    @property
    def total_requests(self) -> int:
        """Sum of all proxy requests (thread-safe)."""
        with self._lock:
            return sum(p.total_requests for p in self.proxies)

    @property
    def overall_success_rate(self) -> float:
        """Weighted average success rate (thread-safe)."""
        with self._lock:
            if not self.proxies:
                return 0.0

            total_reqs = sum(p.total_requests for p in self.proxies)
            if total_reqs == 0:
                return 0.0

            total_successes = sum(p.total_successes for p in self.proxies)
            return total_successes / total_reqs

    def add_proxy(self, proxy: Proxy) -> None:
        """
        Add proxy to pool with duplicate detection.

        Adds a new proxy to the pool with O(1) duplicate checking.
        Silently ignores duplicate URLs. Thread-safe via RLock.

        Args:
            proxy : Proxy
                Proxy instance to add to the pool.

        Returns:
            None

        Raises:
            ValueError
                If pool is at maximum capacity (max_pool_size).

        Example:
            >>> pool = ProxyPool(name="default")
            >>> proxy = Proxy(url="http://proxy.example.com:8080")
            >>> pool.add_proxy(proxy)
            >>> print(pool.size)  # 1

        Note:
            - Thread-safe: uses RLock for concurrent access
            - O(1) duplicate URL checking via hash set
            - Automatically updates both ID and URL indexes
            - Timestamps updated on successful addition
        """
        with self._lock:
            if self.size >= self.max_pool_size:
                raise ValueError(f"Pool at maximum capacity ({self.max_pool_size})")

            # Check for duplicates using O(1) URL index
            if proxy.url in self._url_index:
                return  # Silently ignore duplicates

            self.proxies.append(proxy)
            # Update ID index
            if proxy.id:
                self._id_index[proxy.id] = proxy
            # Update URL index
            self._url_index.add(proxy.url)
            self.updated_at = datetime.now(timezone.utc)

    def remove_proxy(self, proxy_id: UUID) -> None:
        """
        Remove proxy from pool by ID.

        Removes a proxy from the pool by its UUID, updating all internal
        indexes (ID index, URL index, and proxy list). Thread-safe via RLock.

        Args:
            proxy_id : UUID
                UUID of the proxy to remove.

        Returns:
            None

        Example:
            >>> pool = ProxyPool(name="default", proxies=[proxy1, proxy2])
            >>> pool.remove_proxy(proxy1.id)
            >>> print(pool.size)  # 1

        Note:
            - Thread-safe: uses RLock for concurrent access
            - O(1) removal using ID index
            - Automatically updates all indexes
            - Does not raise error if proxy not found
            - Timestamps updated on removal
        """
        with self._lock:
            # Find and remove proxy
            proxy_to_remove = self._id_index.get(proxy_id) if proxy_id in self._id_index else None

            # Remove from ID index first
            if proxy_id in self._id_index:
                del self._id_index[proxy_id]

            # Remove from URL index
            if proxy_to_remove:
                self._url_index.discard(proxy_to_remove.url)

            # Remove from list
            self.proxies = [p for p in self.proxies if p.id != proxy_id]
            self.updated_at = datetime.now(timezone.utc)

    def has_proxy_url(self, proxy_url: str) -> bool:
        """
        Check if pool contains a proxy with given URL (O(1) hash lookup).

        Performs constant-time membership check using URL hash set.
        Thread-safe via RLock.

        Args:
            proxy_url : str
                Full proxy URL to check (e.g., "http://proxy.example.com:8080").

        Returns:
            bool
                True if proxy URL is in pool, False otherwise.

        Example:
            >>> pool = ProxyPool(name="default", proxies=[proxy1])
            >>> pool.has_proxy_url("http://proxy.example.com:8080")
            True

        Note:
            - O(1) constant-time lookup using hash set
            - Thread-safe: uses RLock
            - Performs exact URL matching
        """
        with self._lock:
            return proxy_url in self._url_index

    def get_proxy_by_id(self, proxy_id: UUID) -> Proxy | None:
        """
        Find proxy by ID using O(1) index lookup.

        Retrieves a proxy from the pool by its UUID with constant-time
        lookup via ID index. Thread-safe via RLock.

        Args:
            proxy_id : UUID
                UUID of the proxy to retrieve.

        Returns:
            Proxy | None
                Proxy instance if found, None otherwise.

        Example:
            >>> pool = ProxyPool(name="default", proxies=[proxy1])
            >>> found = pool.get_proxy_by_id(proxy1.id)
            >>> print(found.url if found else "Not found")

        Note:
            - O(1) constant-time lookup using ID index
            - Thread-safe: uses RLock
            - Returns None if proxy ID not in pool
        """
        with self._lock:
            return self._id_index.get(proxy_id)

    def filter_by_tags(self, tags: set[str]) -> list[Proxy]:
        """
        Get proxies matching all tags.

        Returns proxies that have all the specified tags.
        Thread-safe via RLock.

        Args:
            tags : set[str]
                Set of tags to filter by (all must match).

        Returns:
            list[Proxy]
                List of proxies with all matching tags.

        Example:
            >>> pool = ProxyPool(name="default", proxies=[proxy1, proxy2])
            >>> residential = pool.filter_by_tags({"residential"})
            >>> rotating = pool.filter_by_tags({"rotating", "http"})

        Note:
            - Thread-safe: uses RLock
            - Uses set intersection for matching
            - Returns empty list if no matches found
        """
        with self._lock:
            return [p for p in self.proxies if tags.issubset(p.tags)]

    def filter_by_source(self, source: ProxySource) -> list[Proxy]:
        """
        Get proxies from specific source.

        Returns all proxies originating from a specific source.
        Thread-safe via RLock.

        Args:
            source : ProxySource
                Source to filter by (e.g., ProxySource.CUSTOM, ProxySource.FETCHED).

        Returns:
            list[Proxy]
                List of proxies from the specified source.

        Example:
            >>> from proxywhirl import ProxySource
            >>> pool = ProxyPool(name="default", proxies=[proxy1, proxy2])
            >>> custom = pool.filter_by_source(ProxySource.CUSTOM)

        Note:
            - Thread-safe: uses RLock
            - Returns empty list if no proxies from source found
        """
        with self._lock:
            return [p for p in self.proxies if p.source == source]

    def get_healthy_proxies(self) -> list[Proxy]:
        """
        Get all healthy or unknown (not yet tested) proxies, excluding expired ones.

        Returns only proxies that are in HEALTHY, DEGRADED, or UNKNOWN state
        and have not expired. Thread-safe via RLock.

        Returns:
            list[Proxy]
                List of healthy proxies (not expired).

        Example:
            >>> pool = ProxyPool(name="default", proxies=[proxy1, proxy2, proxy3])
            >>> healthy = pool.get_healthy_proxies()
            >>> print(f"Healthy proxies: {len(healthy)}")

        Note:
            - Thread-safe: uses RLock
            - Filters out DEAD and UNHEALTHY proxies
            - Filters out expired proxies (if TTL set)
            - Returns copy to prevent external modification
        """
        with self._lock:
            return [
                p
                for p in self.proxies
                if p.health_status
                in (HealthStatus.HEALTHY, HealthStatus.UNKNOWN, HealthStatus.DEGRADED)
                and not p.is_expired  # Filter out expired proxies
            ]

    def clear_unhealthy(self) -> int:
        """
        Remove all unhealthy and dead proxies from the pool.

        Removes proxies in DEAD or UNHEALTHY state, rebuilding the ID index.
        Thread-safe via RLock.

        Returns:
            int
                Number of proxies removed.

        Example:
            >>> pool = ProxyPool(name="default", proxies=[proxy1, proxy2, proxy3])
            >>> removed = pool.clear_unhealthy()
            >>> print(f"Removed {removed} unhealthy proxies")

        Note:
            - Thread-safe: uses RLock
            - Rebuilds ID index after bulk removal
            - Updates timestamp
            - Preferred over manual removal for batches
        """
        with self._lock:
            initial_count = self.size
            self.proxies = [
                p
                for p in self.proxies
                if p.health_status not in (HealthStatus.DEAD, HealthStatus.UNHEALTHY)
            ]
            # Rebuild ID index after bulk removal
            object.__setattr__(self, "_id_index", {p.id: p for p in self.proxies if p.id})
            self.updated_at = datetime.now(timezone.utc)
            return initial_count - self.size

    def clear_expired(self) -> int:
        """
        Remove all expired proxies from the pool.

        Removes proxies that have exceeded their TTL (if set).
        Rebuilds ID index. Thread-safe via RLock.

        Returns:
            int
                Number of expired proxies removed.

        Example:
            >>> pool = ProxyPool(name="default", proxies=[proxy1, proxy2, proxy3])
            >>> removed = pool.clear_expired()
            >>> print(f"Removed {removed} expired proxies")

        Note:
            - Thread-safe: uses RLock
            - Checks is_expired property on each proxy
            - Rebuilds ID index after bulk removal
            - Updates timestamp
        """
        with self._lock:
            initial_count = self.size
            self.proxies = [p for p in self.proxies if not p.is_expired]
            # Rebuild ID index after bulk removal
            object.__setattr__(self, "_id_index", {p.id: p for p in self.proxies if p.id})
            self.updated_at = datetime.now(timezone.utc)
            return initial_count - self.size

    def get_all_proxies(self) -> list[Proxy]:
        """
        Get all proxies in the pool as a copy.

        Returns a thread-safe copy of all proxies. Thread-safe via RLock.

        Returns:
            list[Proxy]
                Copy of all proxies in the pool.

        Example:
            >>> pool = ProxyPool(name="default", proxies=[proxy1, proxy2])
            >>> all_proxies = pool.get_all_proxies()
            >>> for proxy in all_proxies:
            ...     print(proxy.url)

        Note:
            - Thread-safe: uses RLock
            - Returns a copy to prevent external modification
            - Safe to iterate while other threads modify pool
        """
        with self._lock:
            return self.proxies.copy()

    def get_source_breakdown(self) -> dict[str, int]:
        """
        Get count of proxies by source.

        Returns a dictionary mapping source names to proxy counts.
        Useful for monitoring pool composition. Thread-safe via RLock.

        Returns:
            dict[str, int]
                Mapping of source name (string) to proxy count.

        Example:
            >>> pool = ProxyPool(name="default", proxies=[proxy1, proxy2, proxy3])
            >>> breakdown = pool.get_source_breakdown()
            >>> print(breakdown)
            {'CUSTOM': 2, 'FETCHED': 1}

        Note:
            - Thread-safe: uses RLock
            - Uses source.value for readable source names
            - Useful for analytics and monitoring
        """
        with self._lock:
            breakdown: dict[str, int] = {}
            for proxy in self.proxies:
                source_key = proxy.source.value
                breakdown[source_key] = breakdown.get(source_key, 0) + 1
            return breakdown


# ============================================================================
# STORAGE PROTOCOLS
# ============================================================================


@runtime_checkable
class StorageBackend(Protocol):
    """Protocol for proxy storage backends.

    This defines the interface that all storage backends must implement,
    allowing for file-based, database, or other storage mechanisms.
    """

    async def save(self, proxies: list[Proxy]) -> None:
        """Save proxies to storage.

        Args:
            proxies: List of proxies to save

        Raises:
            IOError: If save operation fails
        """
        ...

    async def load(self) -> list[Proxy]:
        """Load proxies from storage.

        Returns:
            List of proxies loaded from storage

        Raises:
            FileNotFoundError: If storage doesn't exist
            ValueError: If data is corrupted or invalid
        """
        ...

    async def clear(self) -> None:
        """Clear all proxies from storage.

        Raises:
            IOError: If clear operation fails
        """
        ...


# ============================================================================
# HEALTH MONITORING
# ============================================================================


class HealthMonitor:
    """Continuous health monitoring for proxy pools with auto-eviction.

    Runs background health checks at configurable intervals and automatically
    evicts proxies that fail consecutive checks beyond a threshold.

    Example:
        >>> pool = ProxyPool(name="my_pool")
        >>> pool.add_proxy(Proxy(url="http://proxy.com:8080"))
        >>> monitor = HealthMonitor(pool=pool, check_interval=60, failure_threshold=3)
        >>> await monitor.start()  # Start background checks
        >>> # ... proxies are monitored continuously ...
        >>> await monitor.stop()  # Stop monitoring
    """

    def __init__(
        self,
        pool: ProxyPool,
        check_interval: int = 60,
        failure_threshold: int = 3,
    ) -> None:
        """Initialize health monitor.

        Args:
            pool: ProxyPool to monitor
            check_interval: Seconds between health checks (default: 60)
            failure_threshold: Consecutive failures before eviction (default: 3)

        Raises:
            ValueError: If check_interval or failure_threshold <= 0
        """
        if check_interval <= 0:
            raise ValueError("check_interval must be positive")
        if failure_threshold <= 0:
            raise ValueError("failure_threshold must be positive")

        self.pool = pool
        self.check_interval = check_interval
        self.failure_threshold = failure_threshold
        self.is_running = False
        self._task: asyncio.Task[None] | None = None
        self._failure_counts: dict[str, int] = {}
        self._start_time: datetime | None = None

    async def start(self) -> None:
        """Start background health monitoring.

        Creates an asyncio task that runs health checks periodically.
        Idempotent - calling multiple times won't create duplicate tasks.
        """
        if self.is_running:
            return  # Already running

        import asyncio

        self.is_running = True
        self._start_time = datetime.now(timezone.utc)
        self._task = asyncio.create_task(self._check_health_loop())

    async def stop(self) -> None:
        """Stop background health monitoring.

        Cancels the background task and waits for graceful shutdown.
        Idempotent - safe to call when not running.
        """
        if not self.is_running:
            return  # Not running

        self.is_running = False

        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass  # Expected when cancelling
            except Exception:
                pass  # Other errors also ignored during shutdown

        self._task = None
        self._start_time = None

    async def _check_health_loop(self) -> None:
        """Main health check loop - runs periodically."""
        import asyncio

        while self.is_running:
            try:
                await self._run_health_checks()
            except Exception:
                # Log error but keep running
                pass

            # Sleep until next check
            await asyncio.sleep(self.check_interval)

    async def _run_health_checks(self) -> None:
        """Run health checks on all proxies in pool."""
        # This will be implemented with actual TCP/HTTP checks
        # For now, just a placeholder
        pass

    def _record_failure(self, proxy: Proxy) -> None:
        """Record a health check failure for a proxy.

        Args:
            proxy: Proxy that failed health check
        """
        url = proxy.url
        self._failure_counts[url] = self._failure_counts.get(url, 0) + 1

        # Check if threshold reached
        if self._failure_counts[url] >= self.failure_threshold:
            self._evict_proxy(proxy)

    def _record_success(self, proxy: Proxy) -> None:
        """Record a successful health check for a proxy.

        Args:
            proxy: Proxy that passed health check
        """
        url = proxy.url
        # Reset failure count on success
        if url in self._failure_counts:
            del self._failure_counts[url]

    def _evict_proxy(self, proxy: Proxy) -> None:
        """Evict a proxy from the pool due to excessive failures.

        Args:
            proxy: Proxy to evict (matched by URL, not identity)
        """
        # Find and remove proxy by URL (handles different proxy instances with same URL)
        # Use thread-safe snapshot to avoid race conditions during iteration
        proxy_url = proxy.url
        for p in self.pool.get_all_proxies():
            if p.url == proxy_url:
                self.pool.remove_proxy(p.id)
                break

        # Clean up failure count
        if proxy_url in self._failure_counts:
            del self._failure_counts[proxy_url]

    def get_status(self) -> dict[str, Any]:
        """Get current monitoring status.

        Returns:
            dict[str, Any]: Monitoring status including is_running, check_interval,
            failure_threshold, total_proxies, healthy_proxies, failure_counts,
            and uptime_seconds (if running).
        """
        status: dict[str, Any] = {
            "is_running": self.is_running,
            "check_interval": self.check_interval,
            "failure_threshold": self.failure_threshold,
            "total_proxies": self.pool.size,
            "healthy_proxies": len(self.pool.get_healthy_proxies()),
            "failure_counts": self._failure_counts.copy(),
        }

        if self.is_running and self._start_time:
            uptime = (datetime.now(timezone.utc) - self._start_time).total_seconds()
            status["uptime_seconds"] = uptime

        return status


# ============================================================================
# CLI MODELS
# ============================================================================


class RequestResult(BaseModel):
    """Result of HTTP request made through proxy."""

    url: str
    method: str  # GET, POST, PUT, DELETE, etc.
    status_code: int
    elapsed_ms: float
    proxy_used: str  # URL of proxy that succeeded
    attempts: int  # Number of retries before success
    headers: dict[str, str]  # Response headers
    body: str | None = None  # Response body (truncated if large)
    error: str | None = None  # Error message if failed
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def is_success(self) -> bool:
        """Check if request was successful."""
        return 200 <= self.status_code < 300


class ProxyStatus(BaseModel):
    """Status of a single proxy in the pool."""

    url: str
    health: str  # "healthy", "degraded", "failed", "unknown"
    last_check: datetime | None = None
    response_time_ms: float | None = None
    success_rate: float = 0.0  # 0.0-1.0
    total_requests: int = 0
    failed_requests: int = 0
    is_active: bool = True


class PoolSummary(BaseModel):
    """Summary of entire proxy pool."""

    total_proxies: int
    healthy: int
    degraded: int
    failed: int
    rotation_strategy: str
    current_index: int  # For round-robin
    proxies: list[ProxyStatus]


# ============================================================================
# TIMEZONE HANDLING (integrated from timezone_handling.py)
# ============================================================================


class TimezoneFormat(str, Enum):
    """Timezone representation formats."""

    UTC = "UTC"
    ISO8601 = "ISO8601"
    UNIX_TIMESTAMP = "UNIX_TIMESTAMP"
    LOCAL = "LOCAL"


class TimezoneManager:
    """Manages timezone conversions and normalization."""

    def __init__(self, default_tz: str = "UTC") -> None:
        """Initialize timezone manager."""
        self.default_tz = default_tz
        logger.debug(f"TimezoneManager initialized (default={default_tz})")

    def now_utc(self) -> datetime:
        """Get current time in UTC."""
        return datetime.now(timezone.utc)

    def now_utc_iso(self) -> str:
        """Get current time in UTC ISO format."""
        return self.now_utc().isoformat()

    def now_utc_timestamp(self) -> int:
        """Get current time as Unix timestamp."""
        return int(self.now_utc().timestamp())

    def to_utc(self, dt: datetime) -> datetime:
        """Convert datetime to UTC."""
        if dt.tzinfo is None:
            logger.warning("Naive datetime provided, assuming UTC")
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    def to_iso8601(self, dt: datetime | None = None) -> str:
        """Convert to ISO 8601 format."""
        if dt is None:
            dt = self.now_utc()
        else:
            dt = self.to_utc(dt)
        return dt.isoformat()

    def from_iso8601(self, iso_string: str) -> datetime | None:
        """Parse ISO 8601 string."""
        try:
            return datetime.fromisoformat(iso_string)
        except Exception as e:
            logger.error(f"Failed to parse ISO 8601 string: {e}")
            return None

    def from_timestamp(self, timestamp: int | float) -> datetime:
        """Create datetime from Unix timestamp."""
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)

    def format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        if seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        if seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f}h"
        days = seconds / 86400
        return f"{days:.1f}d"

    def export_metrics(self) -> dict[str, Any]:
        """Export timezone metrics."""
        return {
            "default_timezone": self.default_tz,
            "current_utc": self.now_utc_iso(),
            "current_timestamp": self.now_utc_timestamp(),
        }
