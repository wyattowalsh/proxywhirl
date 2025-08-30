"""proxywhirl/models.py -- Enhanced models for ProxyWhirl with modern Pydantic v2 patterns

This module provides intelligent, high-performance proxy data models with:
- Computed fields for quality metrics and derived properties
- Advanced validation patterns with context awareness
- Modern serialization with performance optimizations
- Type safety enhancements and strict mode support
- Extensible architecture for custom proxy sources
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum, auto
from ipaddress import IPv4Address, IPv6Address, ip_address
from typing import Any, Dict, List, Optional, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PlainSerializer,
    WithJsonSchema,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
)
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated

# === Exception Types ===


class ProxyError(Exception):
    """Base exception for all proxy-related errors."""


class ProxyValidationError(ProxyError):
    """Error during proxy validation or health checking."""


class ProxySourceError(ProxyError):
    """Error loading proxies from a source."""


class ProxyConfigError(ProxyError):
    """Error in proxy configuration."""


# === Enumeration Types ===


class AnonymityLevel(StrEnum):
    """Standardized anonymity tiers."""

    TRANSPARENT = auto()
    ANONYMOUS = auto()
    ELITE = auto()
    UNKNOWN = "unknown"


class Scheme(StrEnum):
    """Standardized proxy schemes (lowercase values for I/O and URIs)."""

    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"


class ProxyStatus(StrEnum):
    """Proxy operational status states."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    BLACKLISTED = "blacklisted"
    TESTING = "testing"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"


class RotationStrategy(StrEnum):
    """Proxy rotation strategies."""

    ROUND_ROBIN = "round_robin"
    RANDOM = auto()
    WEIGHTED = auto()
    HEALTH_BASED = "health_based"
    LEAST_USED = "least_used"
    # Enhanced rotation strategies
    ASYNC_ROUND_ROBIN = "async_round_robin"
    CIRCUIT_BREAKER = "circuit_breaker"
    METRICS_AWARE = "metrics_aware"
    ML_ADAPTIVE = "ml_adaptive"
    CONSISTENT_HASH = "consistent_hash"
    GEO_AWARE = "geo_aware"


class ValidationErrorType(StrEnum):
    """Types of validation errors for categorization."""

    TIMEOUT = auto()
    CONNECTION_ERROR = "connection_error"
    AUTHENTICATION_ERROR = "auth_error"
    PROXY_ERROR = "proxy_error"
    HTTP_ERROR = "http_error"
    SSL_ERROR = "ssl_error"
    RATE_LIMITED = "rate_limited"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"
    UNKNOWN = auto()


class ErrorHandlingPolicy(StrEnum):
    """How to handle different error types."""

    REMOVE_IMMEDIATELY = "remove_immediately"  # Dead proxies
    COOLDOWN_SHORT = "cooldown_short"  # Temporary issues (5-15 seconds)
    COOLDOWN_MEDIUM = "cooldown_medium"  # Rate limiting (1-5 minutes)
    COOLDOWN_LONG = "cooldown_long"  # Severe issues (10-30 minutes)
    BLACKLIST = "blacklist"  # Permanently ban proxy


class CircuitState(StrEnum):
    """Circuit breaker states for enhanced error handling."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit breaker tripped, blocking requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class MLFeatureType(StrEnum):
    """Types of ML features for adaptive proxy selection."""

    SUCCESS_RATE = "success_rate"
    RESPONSE_TIME = "response_time"
    TOTAL_REQUESTS = "total_requests"
    CONSECUTIVE_FAILURES = "consecutive_failures"
    TIME_SINCE_LAST_CHECK = "time_since_last_check"
    ANONYMITY_SCORE = "anonymity_score"
    COUNTRY_RELIABILITY = "country_reliability"
    HOUR_OF_DAY = "hour_of_day"
    DAY_OF_WEEK = "day_of_week"


# === Type Definitions ===


def _to_upper(v: Optional[str]) -> Optional[str]:
    """Convert string to uppercase, preserving None values."""
    return v.upper() if v else v


def _validate_port(v: int) -> int:
    """Validate port number is in valid range."""
    if not (1 <= v <= 65535):
        raise ValueError(f"Port must be between 1 and 65535, got {v}")
    return v


CountryCode = Annotated[Optional[str], AfterValidator(_to_upper)]

PortNumber = Annotated[
    int,
    Field(ge=1, le=65535),
    WithJsonSchema(
        {
            "type": "integer", 
            "minimum": 1,
            "maximum": 65535,
            "description": "TCP/UDP port number (1-65535)"
        }
    ),
    AfterValidator(_validate_port),
]

ResponseTimeSeconds = Annotated[
    float,
    Field(ge=0.001, le=300.0),
    AfterValidator(lambda x: round(x, 3)),  # Precision control
    PlainSerializer(lambda x: f"{x:.3f}", when_used="json"),
    WithJsonSchema(
        {
            "type": "number",
            "minimum": 0.001,
            "maximum": 300.0,
            "multipleOf": 0.001,
            "description": "Response time in seconds (max 5 minutes)"
        }
    ),
]

QualityScore = Annotated[
    float,
    Field(ge=0.0, le=1.0),
    AfterValidator(lambda x: round(x, 4)),  # High precision for quality
    WithJsonSchema(
        {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "multipleOf": 0.0001,
            "description": "Quality score from 0.0 (worst) to 1.0 (best)"
        }
    ),
]

SuccessRate = Annotated[
    float,
    Field(ge=0.0, le=1.0),
    AfterValidator(lambda x: round(x, 3)),
    WithJsonSchema(
        {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "description": "Success rate from 0.0 to 1.0"
        }
    ),
]


# === Performance and Error Tracking ===


@dataclass
class ProxyCredentials:
    """Authentication credentials for proxy access."""
    username: str
    password: str
    auth_type: str = "basic"  # basic, digest, etc.


@dataclass  
class ProxyCapabilities:
    """Proxy feature support information."""
    supports_https: bool = False
    supports_socks: bool = False
    supports_ipv6: bool = False
    max_connections: Optional[int] = None
    bandwidth_limit: Optional[str] = None  # e.g., "100Mbps"


class ProxyErrorState(BaseModel):
    """Error tracking and cooldown management for proxies."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    consecutive_failures: int = Field(default=0, ge=0)
    last_error: Optional[ValidationErrorType] = Field(default=None)
    last_error_time: Optional[datetime] = Field(default=None)
    cooldown_until: Optional[datetime] = Field(default=None)
    total_failures: int = Field(default=0, ge=0)
    
    def record_failure(
        self, 
        error_type: ValidationErrorType = ValidationErrorType.UNKNOWN,
        cooldown_seconds: Optional[int] = None
    ) -> None:
        """Record a failure and set cooldown if needed."""
        self.consecutive_failures += 1
        self.total_failures += 1
        self.last_error = error_type
        self.last_error_time = datetime.now(timezone.utc)
        
        if cooldown_seconds:
            self.cooldown_until = datetime.now(timezone.utc) + timedelta(seconds=cooldown_seconds)
    
    def record_success(self) -> None:
        """Record a successful operation, clearing failure state."""
        self.consecutive_failures = 0
        self.last_error = None
        self.cooldown_until = None
    
    @property
    def is_in_cooldown(self) -> bool:
        """Check if proxy is currently in cooldown period."""
        if self.cooldown_until is None:
            return False
        return datetime.now(timezone.utc) < self.cooldown_until
    
    def is_available(self) -> bool:
        """Check if proxy is available (not in cooldown)."""
        return not self.is_in_cooldown


class ProxyPerformanceMetrics(BaseModel):
    """Advanced performance metrics with computed insights."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
    )

    # Basic metrics
    total_requests: int = Field(default=0, ge=0)
    successful_requests: int = Field(default=0, ge=0) 
    failed_requests: int = Field(default=0, ge=0)
    
    # Timing metrics
    avg_response_time: Optional[float] = Field(default=None, ge=0)
    min_response_time: Optional[float] = Field(default=None, ge=0)
    max_response_time: Optional[float] = Field(default=None, ge=0)
    
    # Quality indicators
    last_success_time: Optional[datetime] = Field(default=None)
    uptime_percentage: Optional[float] = Field(default=None, ge=0, le=100)
    
    # Advanced metrics (percentiles)
    response_time_p50: Optional[float] = Field(default=None, ge=0)
    response_time_p95: Optional[float] = Field(default=None, ge=0)
    response_time_p99: Optional[float] = Field(default=None, ge=0)

    @computed_field
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    @computed_field
    @property
    def reliability_score(self) -> float:
        """Compute reliability score (0.0-1.0) based on success rate and consistency."""
        base_score = self.success_rate
        
        # Penalize if we have very few requests
        if self.total_requests < 10:
            base_score *= 0.5
        
        # Bonus for high uptime
        if self.uptime_percentage and self.uptime_percentage > 95:
            base_score = min(1.0, base_score * 1.05)
        
        return round(base_score, 4)
    
    @computed_field  
    @property
    def performance_score(self) -> float:
        """Compute performance score (0.0-1.0) based on response times."""
        if not self.avg_response_time:
            return 0.5  # Neutral score for unknown performance
        
        # Score based on average response time
        if self.avg_response_time <= 1.0:
            score = 1.0
        elif self.avg_response_time <= 3.0:
            score = 0.8
        elif self.avg_response_time <= 5.0:
            score = 0.6
        elif self.avg_response_time <= 10.0:
            score = 0.4
        else:
            score = 0.2
        
        # Adjust based on consistency (using p95 if available)
        if self.response_time_p95 and self.avg_response_time:
            consistency_ratio = self.avg_response_time / self.response_time_p95
            if consistency_ratio > 0.8:  # Very consistent
                score = min(1.0, score * 1.1)
            elif consistency_ratio < 0.3:  # Very inconsistent
                score *= 0.8
        
        return round(score, 4)

    @computed_field
    @property
    def is_healthy(self) -> bool:
        """Determine if proxy is considered healthy based on metrics."""
        return (
            self.reliability_score > 0.7 and
            self.performance_score > 0.5 and
            (self.total_requests == 0 or self.success_rate > 0.6)
        )


# === Target Validation Models ===


class TargetDefinition(BaseModel):
    """Configuration for proxy validation targets."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    target_id: str = Field(..., min_length=1, max_length=50)
    url: str = Field(..., min_length=1)
    method: str = Field(default="GET", pattern=r"^(GET|POST|HEAD|OPTIONS)$")
    expected_status: int = Field(default=200, ge=100, le=599)
    timeout: float = Field(default=10.0, ge=0.1, le=60.0)
    weight: float = Field(default=1.0, ge=0.1, le=10.0)
    headers: Dict[str, str] = Field(default_factory=dict)
    verify_ssl: bool = Field(default=True)

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Basic URL validation."""
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


class TargetHealthStatus(BaseModel):
    """Health status tracking for individual targets."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    target_id: str = Field(..., min_length=1)
    consecutive_successes: int = Field(default=0, ge=0)
    consecutive_failures: int = Field(default=0, ge=0)
    last_check_time: Optional[datetime] = Field(default=None)
    last_success_time: Optional[datetime] = Field(default=None)
    last_response_time: Optional[float] = Field(default=None, ge=0)
    total_checks: int = Field(default=0, ge=0)
    successful_checks: int = Field(default=0, ge=0)
    avg_response_time: Optional[float] = Field(default=None, ge=0)

    @computed_field
    @property
    def success_rate(self) -> float:
        """Calculate success rate for this target."""
        if self.total_checks == 0:
            return 0.0
        return self.successful_checks / self.total_checks

    @computed_field
    @property  
    def quality_score(self) -> float:
        """Calculate quality score for this target."""
        if self.total_checks == 0:
            return 0.0
            
        base_score = self.success_rate * 0.7
        
        # Response time factor
        if self.avg_response_time is not None:
            if self.avg_response_time < 2.0:
                base_score += 0.2
            elif self.avg_response_time < 5.0:
                base_score += 0.1
            elif self.avg_response_time > 15.0:
                base_score -= 0.1
        
        # Penalize consecutive failures
        if self.consecutive_failures > 2:
            base_score -= min(0.3, self.consecutive_failures * 0.1)
        
        return max(0.0, min(1.0, base_score))

    def record_success(self, response_time: Optional[float] = None) -> None:
        """Record successful check."""
        self.consecutive_successes += 1
        self.consecutive_failures = 0
        self.total_checks += 1
        self.successful_checks += 1
        self.last_check_time = datetime.now(timezone.utc)
        self.last_success_time = self.last_check_time
        
        if response_time is not None:
            self.last_response_time = response_time
            if self.avg_response_time is None:
                self.avg_response_time = response_time
            else:
                # Exponential moving average
                self.avg_response_time = 0.8 * self.avg_response_time + 0.2 * response_time

    def record_failure(self) -> None:
        """Record failed check."""
        self.consecutive_failures += 1
        self.consecutive_successes = 0
        self.total_checks += 1
        self.last_check_time = datetime.now(timezone.utc)


# === Session Management ===


class SessionConfig(BaseModel):
    """Configuration model for proxy session management."""

    model_config = ConfigDict(
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        use_enum_values=True,
    )

    # Session persistence settings
    enable_sticky_sessions: bool = Field(
        default=False,
        description="Enable sticky sessions for consistent proxy assignment",
    )
    session_ttl_seconds: int = Field(
        default=300,
        ge=10,
        le=86400,
        description="Session TTL in seconds (10 seconds to 24 hours)",
    )
    max_sessions: int = Field(
        default=1000,
        ge=1,
        le=100000,
        description="Maximum number of concurrent sessions",
    )
    cleanup_interval_seconds: int = Field(
        default=60,
        ge=10,
        le=3600,
        description="Interval for session cleanup in seconds",
    )
    
    # Session binding options
    bind_by_ip: bool = Field(
        default=True,
        description="Bind sessions to client IP addresses",
    )
    bind_by_user_agent: bool = Field(
        default=False,
        description="Include User-Agent in session binding",
    )
    
    # Performance settings
    session_pool_size: int = Field(
        default=50,
        ge=1,
        le=1000,
        description="Initial session pool size",
    )

    @field_validator("session_ttl_seconds")
    @classmethod
    def validate_session_ttl(cls, v: int) -> int:
        """Validate session TTL is within reasonable bounds."""
        if v < 10:
            raise ValueError("Session TTL must be at least 10 seconds")
        if v > 86400:
            raise ValueError("Session TTL cannot exceed 24 hours")
        return v


class ProxySession(BaseModel):
    """
    Proxy session model for sticky session management.
    
    Manages the binding between client identifiers and specific proxy assignments
    with automatic expiration and cleanup handling.
    """

    model_config = ConfigDict(
        extra="allow",
        validate_default=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    # Session identification
    session_id: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Unique session identifier",
    )
    client_identifier: str = Field(
        ...,
        min_length=1,
        max_length=256,
        description="Client identification string (IP, hash, etc.)",
    )
    
    # Proxy assignment
    assigned_proxy_host: str = Field(
        ...,
        description="Host of assigned proxy",
    )
    assigned_proxy_port: int = Field(
        ...,
        ge=1,
        le=65535,
        description="Port of assigned proxy",
    )
    
    # Session timing
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when session was created",
    )
    expires_at: datetime = Field(
        ...,
        description="UTC timestamp when session expires",
    )
    last_used_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of last session usage",
    )
    
    # Session metadata
    use_count: int = Field(
        default=0,
        ge=0,
        description="Number of times this session has been used",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional session metadata",
    )
    
    # Thread safety - private attribute
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def __init__(self, **data: Any):
        """Initialize session with automatic expiration time and thread lock."""
        if "expires_at" not in data and "session_ttl_seconds" in data:
            ttl_seconds: int = data.pop("session_ttl_seconds")
            data["expires_at"] = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
        
        super().__init__(**data)
        
        # Initialize thread lock after parent initialization
        self._lock = threading.RLock()

    @field_validator("expires_at", mode="before")
    @classmethod
    def validate_expires_at(cls, v: Any) -> datetime:
        """Ensure expires_at is a UTC datetime."""
        if isinstance(v, datetime):
            if v.tzinfo is None:
                return v.replace(tzinfo=timezone.utc)
            return v
        
        # Handle string ISO format
        if isinstance(v, str):
            dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
            return dt.astimezone(timezone.utc)
        
        raise ValueError(f"Invalid expires_at format: {v}")

    @computed_field
    @property
    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.now(timezone.utc) >= self.expires_at

    @computed_field
    @property
    def time_remaining_seconds(self) -> float:
        """Get remaining time in seconds."""
        remaining = self.expires_at - datetime.now(timezone.utc)
        return max(0.0, remaining.total_seconds())

    @computed_field
    @property
    def proxy_url(self) -> str:
        """Generate proxy URL from assigned proxy."""
        return f"http://{self.assigned_proxy_host}:{self.assigned_proxy_port}"

    def touch(self) -> None:
        """Update last_used_at timestamp and increment use count."""
        with self._lock:
            self.last_used_at = datetime.now(timezone.utc)
            self.use_count += 1

    def extend_session(self, additional_seconds: int) -> None:
        """Extend session expiration time."""
        with self._lock:
            self.expires_at = self.expires_at + timedelta(seconds=additional_seconds)

    def is_valid_for_client(self, client_identifier: str) -> bool:
        """Check if session is valid for the given client."""
        return (
            not self.is_expired and
            self.client_identifier == client_identifier
        )


class SessionManager(BaseModel):
    """
    Session manager for handling proxy session lifecycle.
    
    Provides thread-safe session creation, retrieval, cleanup,
    and expiration management.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_default=True,
        arbitrary_types_allowed=True,
    )

    config: SessionConfig = Field(default_factory=SessionConfig)
    
    def model_post_init(self, __context: Any = None) -> None:
        """Initialize non-serializable attributes after Pydantic initialization."""
        # Internal session storage (not Pydantic fields)
        self._sessions: Dict[str, ProxySession] = {}
        self._lock = threading.RLock()
        self._last_cleanup = datetime.now(timezone.utc)

    @computed_field
    @property
    def session_count(self) -> int:
        """Get current number of active sessions."""
        return len(self._sessions)

    @computed_field
    @property
    def expired_session_count(self) -> int:
        """Count expired sessions that need cleanup."""
        with self._lock:
            return sum(1 for session in self._sessions.values() if session.is_expired)

    def create_session(
        self,
        session_id: str,
        client_identifier: str,
        assigned_proxy_host: str,
        assigned_proxy_port: int,
        **metadata: Any,
    ) -> ProxySession:
        """Create a new proxy session."""
        if not self.config.enable_sticky_sessions:
            raise ValueError("Sticky sessions are not enabled")
        
        with self._lock:
            # Check session limit
            if len(self._sessions) >= self.config.max_sessions:
                self._cleanup_expired_sessions()
                if len(self._sessions) >= self.config.max_sessions:
                    raise ValueError("Maximum session limit reached")
            
            # Create session
            session = ProxySession(
                session_id=session_id,
                client_identifier=client_identifier,
                assigned_proxy_host=assigned_proxy_host,
                assigned_proxy_port=assigned_proxy_port,
                session_ttl_seconds=self.config.session_ttl_seconds,
                metadata=metadata,
            )
            
            self._sessions[session_id] = session
            return session

    def get_session(self, session_id: str) -> Optional[ProxySession]:
        """Get session by ID, return None if expired or not found."""
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return None
            
            if session.is_expired:
                # Clean up expired session
                del self._sessions[session_id]
                return None
            
            return session

    def get_session_for_client(self, client_identifier: str) -> Optional[ProxySession]:
        """Find active session for the given client identifier."""
        with self._lock:
            for session in self._sessions.values():
                if session.is_valid_for_client(client_identifier):
                    return session
            return None

    def touch_session(self, session_id: str) -> bool:
        """Touch session to update last_used_at and use_count."""
        session = self.get_session(session_id)
        if session is None:
            return False
        
        session.touch()
        return True

    def remove_session(self, session_id: str) -> bool:
        """Remove session by ID."""
        with self._lock:
            return self._sessions.pop(session_id, None) is not None

    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and return count removed."""
        return self._cleanup_expired_sessions()

    def _cleanup_expired_sessions(self) -> int:
        """Internal method to clean up expired sessions."""
        with self._lock:
            expired_ids = [
                session_id for session_id, session in self._sessions.items()
                if session.is_expired
            ]
            
            for session_id in expired_ids:
                del self._sessions[session_id]
            
            self._last_cleanup = datetime.now(timezone.utc)
            return len(expired_ids)

    def should_cleanup(self) -> bool:
        """Check if cleanup should be performed based on interval."""
        cleanup_interval = timedelta(seconds=self.config.cleanup_interval_seconds)
        return datetime.now(timezone.utc) - self._last_cleanup > cleanup_interval

    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        with self._lock:
            total_sessions = len(self._sessions)
            expired_count = sum(1 for s in self._sessions.values() if s.is_expired)
            active_count = total_sessions - expired_count
            
            if self._sessions:
                total_uses = sum(s.use_count for s in self._sessions.values())
                avg_uses = total_uses / total_sessions
            else:
                avg_uses = 0.0
            
            return {
                "total_sessions": total_sessions,
                "active_sessions": active_count,
                "expired_sessions": expired_count,
                "average_uses_per_session": avg_uses,
                "max_sessions": self.config.max_sessions,
                "session_utilization": active_count / self.config.max_sessions,
                "last_cleanup": self._last_cleanup.isoformat(),
            }

    def clear_all_sessions(self) -> int:
        """Clear all sessions and return count removed."""
        with self._lock:
            count = len(self._sessions)
            self._sessions.clear()
            return count


# === Core Proxy Models ===


class Proxy(BaseModel):
    """
    Enhanced canonical proxy data model with intelligent features.

    Features:
    - Computed quality scoring and performance metrics
    - Advanced validation with context awareness
    - Optimized serialization patterns
    - Type safety enhancements
    - Extensible architecture for custom sources
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
        str_strip_whitespace=True,
        validate_default=True,
        use_enum_values=True,
        serialize_by_alias=False,
        validate_assignment=True,
        json_schema_extra={
            "examples": [
                {
                    "host": "192.0.2.123",
                    "ip": "192.0.2.123",
                    "port": 8080,
                    "schemes": ["http", "https"],
                    "country_code": "US",
                    "country": "United States",
                    "city": "New York",
                    "anonymity": "elite",
                    "last_checked": "2025-06-21T12:00:00Z",
                    "response_time": 0.234,
                    "source": "free-proxy-list.org",
                    "metadata": {"checks_up": 1200, "checks_down": 5},
                }
            ]
        },
    )

    # Core required fields with enhanced validation
    host: str = Field(
        ..., min_length=1, max_length=253, description="Hostname or IP address of the proxy"
    )
    ip: Union[IPv4Address, IPv6Address, str] = Field(..., description="IP address of the proxy")
    port: PortNumber = Field(..., description="TCP port")
    schemes: List[Scheme] = Field(
        ..., min_length=1, description="Protocols supported: http, https, socks4, socks5"
    )

    # Enhanced fields for comprehensive proxy management
    credentials: Optional[ProxyCredentials] = Field(
        None, description="Authentication credentials if required"
    )
    metrics: Optional[ProxyPerformanceMetrics] = Field(
        None, description="Performance and reliability metrics with computed insights"
    )
    capabilities: Optional[ProxyCapabilities] = Field(
        None, description="Proxy feature support information"
    )

    # Geographic and network information
    country_code: Optional[CountryCode] = Field(
        None,
        description="ISO 3166-1 alpha-2 country code (auto-converted to uppercase)",
    )
    country: Optional[str] = Field(None, max_length=100, description="Country name")
    city: Optional[str] = Field(None, max_length=100, description="City or region")
    region: Optional[str] = Field(None, max_length=100, description="Region or state")
    isp: Optional[str] = Field(None, max_length=200, description="Internet service provider")
    organization: Optional[str] = Field(None, max_length=200, description="Organization name")

    # Quality and status tracking
    anonymity: AnonymityLevel = Field(
        AnonymityLevel.UNKNOWN, description="Anonymity classification"
    )
    last_checked: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of last health check",
    )
    response_time: Optional[ResponseTimeSeconds] = Field(
        None, description="Last observed latency in seconds"
    )
    source: Optional[str] = Field(
        None, max_length=100, description="Identifier of the proxy provider"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Provider-specific additional fields and computed metrics"
    )

    # Status and quality tracking with enhanced validation
    status: ProxyStatus = Field(
        ProxyStatus.ACTIVE,
        description="Proxy operational status with type safety",
    )
    error_state: ProxyErrorState = Field(
        default_factory=ProxyErrorState, description="Error tracking and cooldown management"
    )
    quality_score: Optional[QualityScore] = Field(
        None,
        description="Overall quality score 0.0-1.0 (deprecated: use intelligent_quality_score)",
    )
    blacklist_reason: Optional[str] = Field(
        None, max_length=500, description="Reason for blacklisting"
    )

    # Target-based health tracking  
    def __init__(self, **data: Any) -> None:
        """Initialize proxy with target health tracking."""
        super().__init__(**data)
        # Initialize target_health as a regular dict, not a Pydantic field
        if not hasattr(self, 'target_health'):
            self.target_health: Dict[str, TargetHealthStatus] = {}

    @model_validator(mode="before")
    @classmethod
    def preprocess_data(cls, data: Any) -> Any:
        """Preprocess and normalize input data."""
        if isinstance(data, dict):
            data = dict(data)  # Ensure we have a mutable dict
            # Handle legacy scheme field
            if "scheme" in data and "schemes" not in data:
                data["schemes"] = [data.pop("scheme")]
            
            # Handle protocol alias
            if "protocol" in data and "schemes" not in data:
                data["schemes"] = [data.pop("protocol")]
        
        return data

    @field_validator("ip", mode="before")
    @classmethod
    def validate_ip(cls, v: Any) -> Union[IPv4Address, IPv6Address, str]:
        """Validate IP address format."""
        if isinstance(v, (IPv4Address, IPv6Address)):
            return v
        
        if isinstance(v, str):
            v = v.strip()
            try:
                return ip_address(v)
            except ValueError:
                # Keep as string for hostname resolution
                return v
        
        raise ValueError(f"Invalid IP address format: {v}")

    @field_validator("city", mode="before")
    @classmethod
    def normalize_city(cls, v: Optional[str]) -> Optional[str]:
        """Normalize city names."""
        if v is None:
            return None
        
        city = str(v).strip()
        if not city:
            return None
        
        # Basic normalization
        city = city.title()
        return city

    @field_validator("response_time", mode="before")
    @classmethod
    def convert_response_time(cls, v: Any) -> Optional[float]:
        """Convert response time to float with validation."""
        if v is None:
            return None
        
        try:
            rt = float(v)
            return rt if rt > 0 else None
        except (ValueError, TypeError):
            return None

    @field_validator("schemes", mode="before")
    @classmethod
    def normalize_schemes(cls, v: Any) -> List[str]:
        """Normalize and validate proxy schemes."""
        schemes: List[str] = []
        
        if isinstance(v, str):
            schemes = [v.lower().strip()]
        elif hasattr(v, '__iter__') and not isinstance(v, (str, bytes)):
            try:
                # Type ignore for dynamic conversion
                schemes = [str(item).lower().strip() for item in v]  # type: ignore
            except (ValueError, TypeError) as e:
                raise ValueError(f"Cannot convert schemes to strings: {v}") from e
        else:
            raise ValueError(f"Schemes must be string or iterable, got {type(v)}")
        
        # Validate each scheme against available options
        valid_schemes = {s.value for s in Scheme}
        validated: List[str] = [s for s in schemes if s in valid_schemes]
        
        if not validated:
            raise ValueError(f"No valid schemes found in: {v}")
        
        return validated

    @field_validator("anonymity", mode="before")
    @classmethod
    def normalize_anonymity(cls, v: Any) -> str:
        """Normalize anonymity level."""
        if v is None:
            return AnonymityLevel.UNKNOWN
        
        if isinstance(v, AnonymityLevel):
            return v
        
        v_str = str(v).upper()
        
        # Handle common variations
        if v_str in ["HIGH", "ELITE", "ANONYMOUS"]:
            return AnonymityLevel.ELITE
        elif v_str in ["LOW", "TRANSPARENT"]:
            return AnonymityLevel.TRANSPARENT
        elif v_str in ["MEDIUM", "ANONYMOUS"]:
            return AnonymityLevel.ANONYMOUS
        else:
            return AnonymityLevel.UNKNOWN

    @field_serializer("last_checked", when_used="json")
    def serialize_datetime(self, dt: datetime) -> str:
        """Serialize datetime as ISO format string."""
        return dt.isoformat()

    @field_serializer("schemes", mode="plain")
    def serialize_schemes(self, schemes: List[Scheme]) -> List[str]:
        """Serialize schemes as string list."""
        return [s.value if hasattr(s, 'value') else str(s) for s in schemes]

    @field_serializer("metadata", mode="plain")
    def serialize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure metadata is JSON-serializable."""
        return {k: v for k, v in metadata.items() if v is not None}

    @computed_field
    @property
    def intelligent_quality_score(self) -> float:
        """
        Compute intelligent quality score using multiple factors.
        
        This replaces the simple quality_score with a weighted calculation
        that considers target-specific performance, global factors, and
        legacy compatibility.
        """
        # If we have target-specific health data, use it
        target_score = self._compute_target_weighted_score()
        if target_score > 0:
            return self._apply_global_quality_factors(target_score)
        
        # Fall back to legacy quality score computation
        return self._compute_legacy_quality_score()

    def _compute_target_weighted_score(self) -> float:
        """Compute weighted quality score from target health data."""
        if not self.target_health:
            return 0.0
        
        total_weight = 0.0
        weighted_sum = 0.0
        
        for target_health in self.target_health.values():
            # Use weight from target definition if available, otherwise default to 1.0
            weight = 1.0  # Would be retrieved from TargetDefinition in practice
            
            weighted_sum += target_health.quality_score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def _compute_legacy_quality_score(self) -> float:
        """Compute quality score using legacy factors."""
        if self.quality_score is not None:
            return float(self.quality_score)
        
        # Basic scoring based on available metrics
        base_score = 0.5  # Default neutral score
        
        # Response time factor
        if self.response_time is not None:
            if self.response_time < 1.0:
                base_score += 0.2
            elif self.response_time < 3.0:
                base_score += 0.1
            elif self.response_time > 10.0:
                base_score -= 0.2
        
        # Status factor
        if self.status == ProxyStatus.ACTIVE:
            base_score += 0.1
        elif self.status == ProxyStatus.BLACKLISTED:
            base_score = 0.0
        
        # Consecutive failures penalty
        if self.error_state.consecutive_failures > 0:
            penalty = min(0.3, self.error_state.consecutive_failures * 0.1)
            base_score -= penalty
        
        return max(0.0, min(1.0, base_score))

    def _apply_global_quality_factors(self, base_score: float) -> float:
        """Apply global factors to the base quality score."""
        adjusted_score = base_score
        
        # Anonymity bonus
        if self.anonymity == AnonymityLevel.ELITE:
            adjusted_score = min(1.0, adjusted_score * 1.05)
        elif self.anonymity == AnonymityLevel.TRANSPARENT:
            adjusted_score *= 0.95
        
        # HTTPS support bonus
        if Scheme.HTTPS in self.schemes:
            adjusted_score = min(1.0, adjusted_score * 1.02)
        
        # Error state penalties
        if self.error_state.is_in_cooldown:
            adjusted_score *= 0.8
        
        return max(0.0, min(1.0, adjusted_score))

    def get_target_health(self, target_id: str) -> Optional[TargetHealthStatus]:
        """Get health status for a specific target."""
        return self.target_health.get(target_id)

    def update_target_health(
        self, target_id: str, success: bool, response_time: Optional[float] = None
    ) -> None:
        """Update health status for a specific target."""
        if target_id not in self.target_health:
            self.target_health[target_id] = TargetHealthStatus(target_id=target_id)
        
        target_health = self.target_health[target_id]
        
        if success:
            target_health.record_success(response_time)
        else:
            target_health.record_failure()

    def get_target_quality_score(self, target_id: str) -> float:
        """Get quality score for a specific target."""
        target_health = self.get_target_health(target_id)
        if target_health is None:
            return 0.0
        return target_health.quality_score

    @computed_field
    @property
    def is_healthy(self) -> bool:
        """Determine if proxy is currently healthy."""
        # Check error state first
        if not self.error_state.is_available():
            return False
        
        # Check status
        if self.status in [ProxyStatus.BLACKLISTED, ProxyStatus.INACTIVE]:
            return False
        
        # Use metrics if available
        if self.metrics is not None:
            return self.metrics.is_healthy
        
        # Basic health check
        return (
            self.error_state.consecutive_failures < 3 and
            (self.response_time is None or self.response_time < 10.0)
        )

    @computed_field
    @property
    def url(self) -> str:
        """Generate primary proxy URL."""
        primary_scheme = self.schemes[0] if self.schemes else "http"
        return f"{primary_scheme}://{self.host}:{self.port}"

    @computed_field
    @property
    def display_name(self) -> str:
        """Generate human-readable display name."""
        location_parts: List[str] = []
        
        if self.city:
            location_parts.append(self.city)
        if self.country_code:
            location_parts.append(self.country_code)
        
        location = ", ".join(location_parts) if location_parts else "Unknown"
        
        return f"{self.host}:{self.port} ({location})"

    @property
    def primary_scheme(self) -> Scheme:
        """Get the primary/preferred scheme for this proxy."""
        if not self.schemes:
            return Scheme.HTTP
        
        # Prefer HTTPS if available
        if Scheme.HTTPS in self.schemes:
            return Scheme.HTTPS
        
        # Then SOCKS5
        if Scheme.SOCKS5 in self.schemes:
            return Scheme.SOCKS5
        
        # Return first available
        return self.schemes[0]

    @property
    def supports_https(self) -> bool:
        """Check if proxy supports HTTPS."""
        return Scheme.HTTPS in self.schemes

    @property
    def is_socks(self) -> bool:
        """Check if proxy supports SOCKS protocols."""
        return any(scheme in [Scheme.SOCKS4, Scheme.SOCKS5] for scheme in self.schemes)


class StrictProxy(BaseModel):
    """
    Ultra-strict proxy model for production environments.

    Features:
    - Immutable after creation (frozen=True)
    - Strict type validation
    - No string IP addresses allowed
    - Enhanced validation on assignment
    - Optimized for performance and type safety
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_default=True,
        extra="forbid",
        frozen=True,
        validate_assignment=True,
        use_enum_values=True,
        populate_by_name=True,
        arbitrary_types_allowed=False,
    )

    # Core fields with strict validation
    host: str = Field(..., min_length=1, max_length=253)
    ip: Union[IPv4Address, IPv6Address] = Field(
        ..., description="IP address (strict mode - no strings)"
    )
    port: int = Field(..., ge=1, le=65535)
    schemes: List[Scheme] = Field(..., min_length=1)

    # Optional fields with constraints
    country_code: CountryCode = Field(None)
    anonymity: AnonymityLevel = Field(AnonymityLevel.UNKNOWN)

    # Validated metrics with constraints
    response_time: Optional[ResponseTimeSeconds] = Field(None)
    quality_score: QualityScore = Field(0.5)

    # Strict datetime handling
    last_checked: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @computed_field
    @property
    def url(self) -> str:
        """Generate proxy URL with primary scheme."""
        primary_scheme = self.schemes[0] if self.schemes else Scheme.HTTP
        return f"{primary_scheme}://{self.host}:{self.port}"


# Legacy aliases for backward compatibility
ProxyScheme = Scheme
