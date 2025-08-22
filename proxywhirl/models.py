"""proxywhirl/models.py -- Enhanced models for ProxyWhirl with modern Pydantic v2 patterns

This module provides intelligent, high-performance proxy data models with:
- Computed fields for quality metrics and derived properties
- Advanced validation patterns with context awareness
- Modern serialization with performance optimizations
- Type safety enhancements and strict mode support
- Extensible architecture for custom proxy sources
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum, auto
from ipaddress import IPv4Address, IPv6Address, ip_address
from typing import Any, Dict, List, Optional, Set, Union, cast

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


def _to_upper(v: Optional[str]) -> Optional[str]:
    """Convert country code to uppercase and validate format."""
    if v is None:
        return None
    upper = str(v).upper()  # Remove unnecessary isinstance check
    # Validate pattern after conversion
    if len(upper) != 2 or not upper.isalpha():
        raise ValueError("Country code must be 2 alphabetic characters")
    return upper


CountryCode = Annotated[Optional[str], AfterValidator(_to_upper)]


# === Advanced Annotated Types with Pydantic v2 Patterns ===

PortNumber = Annotated[
    int,
    Field(ge=1, le=65535),
    WithJsonSchema(
        {
            "example": 8080,
            "description": "Valid TCP port number (1-65535)",
            "type": "integer",
            "minimum": 1,
            "maximum": 65535,
        }
    ),
]

ResponseTimeSeconds = Annotated[
    float,
    Field(ge=0.001, le=300.0),
    AfterValidator(lambda x: round(x, 3)),  # Precision control
    PlainSerializer(lambda x: f"{x:.3f}", when_used="json"),
    WithJsonSchema(
        {
            "example": 1.234,
            "description": "Response time in seconds (0.001-300.0)",
            "type": "number",
            "minimum": 0.001,
            "maximum": 300.0,
        }
    ),
]

QualityScore = Annotated[
    float,
    Field(ge=0.0, le=1.0),
    AfterValidator(lambda x: round(x, 4)),  # High precision for quality
    WithJsonSchema(
        {
            "example": 0.8750,
            "description": "Quality score from 0.0 (poor) to 1.0 (excellent)",
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
        }
    ),
]

SuccessRate = Annotated[
    float,
    Field(ge=0.0, le=1.0),
    AfterValidator(lambda x: round(x, 3)),
    PlainSerializer(lambda x: f"{x*100:.1f}%", when_used="json"),
    WithJsonSchema(
        {
            "example": 0.95,
            "description": "Success rate from 0.0 to 1.0 (serialized as percentage)",
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
        }
    ),
]

UptimePercentage = Annotated[
    float,
    Field(ge=0.0, le=100.0),
    AfterValidator(lambda x: round(x, 2)),
    WithJsonSchema(
        {
            "example": 99.95,
            "description": "Uptime percentage (0.0-100.0)",
            "type": "number",
            "minimum": 0.0,
            "maximum": 100.0,
        }
    ),
]


class AnonymityLevel(StrEnum):
    """Standardized anonymity tiers."""

    TRANSPARENT = auto()
    ANONYMOUS = auto()
    ELITE = auto()
    UNKNOWN = "unknown"


class Scheme(StrEnum):
    """Standardized proxy schemes."""

    HTTP = auto()
    HTTPS = auto()
    SOCKS4 = auto()
    SOCKS5 = auto()


class CacheType(StrEnum):
    """Cache storage types."""

    MEMORY = auto()
    JSON = auto()
    SQLITE = auto()


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


# === Lightweight Models ===


@dataclass(frozen=True, slots=True)
class CoreProxy:
    """
    Lightweight proxy model for high-performance operations.

    Use this for hot paths where you only need basic proxy info.
    Convert to full Proxy model when you need rich metadata.
    """

    host: str
    port: int  # Keep as int for lightweight model
    scheme: Scheme
    source: str = ""

    @property
    def uri(self) -> str:
        """Get proxy URI."""
        return f"{self.scheme.value}://{self.host}:{self.port}"

    def to_proxy(self) -> "Proxy":
        """Convert to full Proxy model with optional rich metadata."""
        return Proxy(
            host=self.host,
            ip=ip_address(self.host),  # Convert string to IP address
            port=self.port,
            schemes=[self.scheme],
            source=self.source,
            credentials=None,
            metrics=None,
            capabilities=None,
            country_code=None,
            country=None,
            city=None,
            region=None,
            isp=None,
            organization=None,
            anonymity=AnonymityLevel.UNKNOWN,
            response_time=None,
            status=ProxyStatus.ACTIVE,
            quality_score=None,
            blacklist_reason=None,
        )


@dataclass(frozen=True, slots=True)
class ErrorEvent:
    """Lightweight error event record."""

    error_type: ValidationErrorType
    timestamp: datetime
    error_message: Optional[str] = None
    http_status: Optional[int] = None


class ProxyErrorState(BaseModel):
    """Tracks error state and history for a proxy."""

    # Current error state
    consecutive_failures: int = 0
    last_error_type: Optional[ValidationErrorType] = None
    last_error_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None

    # Error history (limited to last 10 for memory efficiency)
    error_history: List[ErrorEvent] = Field(default_factory=list)

    # Cooldown state
    is_in_cooldown: bool = False
    cooldown_until: Optional[datetime] = None
    cooldown_policy: Optional[ErrorHandlingPolicy] = None

    # Failure pattern analysis
    failure_rate_1h: float = 0.0  # Failures per hour in last hour
    failure_rate_24h: float = 0.0  # Failures per hour in last 24h

    def add_error(
        self,
        error_type: ValidationErrorType,
        error_message: Optional[str] = None,
        http_status: Optional[int] = None,
    ) -> None:
        """Add a new error event."""
        now = datetime.now(timezone.utc)

        # Update error state
        self.consecutive_failures += 1
        self.last_error_type = error_type
        self.last_error_time = now

        # Add to history (keep only last 10)
        self.error_history.append(
            ErrorEvent(
                error_type=error_type,
                timestamp=now,
                error_message=error_message,
                http_status=http_status,
            )
        )
        if len(self.error_history) > 10:
            self.error_history.pop(0)

    def add_success(self) -> None:
        """Record a successful request."""
        now = datetime.now(timezone.utc)
        self.consecutive_failures = 0
        self.last_success_time = now
        self.last_error_type = None

    def is_available(self) -> bool:
        """Check if proxy is available (not in cooldown)."""
        if not self.is_in_cooldown or not self.cooldown_until:
            return True
        return datetime.now(timezone.utc) >= self.cooldown_until

    def set_cooldown(self, policy: ErrorHandlingPolicy, duration_seconds: int) -> None:
        """Set cooldown period based on error handling policy."""
        now = datetime.now(timezone.utc)
        self.is_in_cooldown = True
        self.cooldown_until = now + timedelta(seconds=duration_seconds)
        self.cooldown_policy = policy

    def clear_cooldown(self) -> None:
        """Clear cooldown state."""
        self.is_in_cooldown = False
        self.cooldown_until = None
        self.cooldown_policy = None


class ProxyCredentials(BaseModel):
    """Authentication credentials for proxy access."""

    username: str
    password: str
    auth_type: str = "basic"  # basic, ntlm, etc.


class ProxyPerformanceMetrics(BaseModel):
    """Enhanced performance and reliability metrics with industry-standard indicators."""

    # Basic request statistics
    success_count: int = 0
    failure_count: int = 0
    total_requests: int = 0

    # Response time metrics (enhanced with percentiles)
    avg_response_time: Optional[ResponseTimeSeconds] = None
    min_response_time: Optional[ResponseTimeSeconds] = None
    max_response_time: Optional[ResponseTimeSeconds] = None
    p50_response_time: Optional[ResponseTimeSeconds] = Field(
        None, description="50th percentile (median) response time"
    )
    p95_response_time: Optional[ResponseTimeSeconds] = Field(
        None, description="95th percentile response time"
    )
    p99_response_time: Optional[ResponseTimeSeconds] = Field(
        None, description="99th percentile response time"
    )

    # Uptime and availability
    uptime_percentage: Optional[UptimePercentage] = None

    # Failure tracking (industry standard)
    consecutive_failures: int = Field(0, description="Consecutive failures since last success")
    max_consecutive_failures: int = Field(0, description="Maximum consecutive failures recorded")

    # Health check metrics
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    last_health_check: Optional[datetime] = None
    health_check_interval: int = Field(30, description="Health check interval in seconds")

    # Connection-specific metrics
    connection_success_rate: Optional[SuccessRate] = Field(
        None, description="TCP connection establishment success rate"
    )
    dns_resolution_time: Optional[ResponseTimeSeconds] = Field(
        None, description="Average DNS resolution time"
    )
    ssl_handshake_time: Optional[ResponseTimeSeconds] = Field(
        None, description="Average SSL handshake time"
    )

    # Bandwidth and throughput
    bytes_transferred: int = Field(0, description="Total bytes transferred through proxy")
    avg_bandwidth_mbps: Optional[float] = Field(
        None, ge=0.0, description="Average bandwidth in Mbps"
    )

    @computed_field
    @property
    def success_rate(self) -> SuccessRate:
        """Calculate success rate percentage with precision."""
        if self.total_requests == 0:
            return 0.0
        rate = (self.success_count / self.total_requests) * 100
        return min(100.0, max(0.0, round(rate, 2)))

    @computed_field
    @property
    def failure_rate(self) -> SuccessRate:
        """Calculate failure rate percentage with precision."""
        if self.total_requests == 0:
            return 0.0
        rate = (self.failure_count / self.total_requests) * 100
        return min(100.0, max(0.0, round(rate, 2)))

    @computed_field
    @property
    def reliability_score(self) -> QualityScore:
        """Enhanced reliability score using industry-standard algorithm."""
        if self.total_requests < 10:
            return 0.5  # Insufficient data baseline

        # Base score from success rate (60% weight)
        base_score = self.success_rate / 100.0 * 0.6

        # Response time factor (20% weight) - penalize high response times
        response_factor = 0.2
        if self.avg_response_time:
            # Normalize response time (1s = good, >5s = poor)
            response_penalty = min(self.avg_response_time / 5.0, 1.0)
            response_factor *= 1.0 - response_penalty

        # Consecutive failures penalty (10% weight)
        failure_penalty = min(self.consecutive_failures / 10.0, 1.0) * 0.1

        # Uptime factor (10% weight)
        uptime_factor = (self.uptime_percentage or 95.0) / 100.0 * 0.1

        final_score = base_score + response_factor - failure_penalty + uptime_factor
        return min(1.0, max(0.0, round(final_score, 3)))

    @computed_field
    @property
    def health_score(self) -> QualityScore:
        """Industry-standard health score for proxy pool management."""
        if self.total_requests == 0:
            return 0.5  # Unknown health baseline

        # Recent activity bonus (last success within health check interval)
        recent_bonus = 0.0
        if self.last_success:
            time_since_success = (datetime.now() - self.last_success).total_seconds()
            if time_since_success <= self.health_check_interval:
                recent_bonus = 0.2
            elif time_since_success <= self.health_check_interval * 2:
                recent_bonus = 0.1

        # Connection reliability (if available) - connection_success_rate is already 0-1
        connection_factor = (self.connection_success_rate or 0.95) * 0.3

        # Base reliability score (50% weight)
        base_health = self.reliability_score * 0.5

        return min(1.0, max(0.0, round(base_health + connection_factor + recent_bonus, 3)))

    @computed_field
    @property
    def is_healthy(self) -> bool:
        """Determine if proxy is healthy based on industry thresholds."""
        return (
            self.health_score >= 0.7 and self.consecutive_failures < 5 and self.success_rate >= 80.0
        )

    @computed_field
    @property
    def performance_stability(self) -> str:
        """Performance stability assessment."""
        if not self.avg_response_time or not self.min_response_time or not self.max_response_time:
            return "unknown"

        # Calculate coefficient of variation (simplified)
        range_ratio = (self.max_response_time - self.min_response_time) / self.avg_response_time

        if range_ratio < 0.2:
            return "very_stable"
        elif range_ratio < 0.5:
            return "stable"
        elif range_ratio < 1.0:
            return "moderate"
        else:
            return "unstable"


class ProxyCapabilities(BaseModel):
    """Proxy feature support information."""

    supports_https: bool = True
    supports_connect_method: bool = True
    supports_udp: bool = False
    max_concurrent_connections: Optional[int] = None
    bandwidth_limit_mbps: Optional[float] = None
    protocol_versions: List[str] = Field(default_factory=list)


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
        serialize_by_alias=False,  # Performance optimization
        validate_assignment=True,  # Enhanced type safety
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

    @model_validator(mode="before")
    @classmethod
    def _resolve_ip_from_host(cls, data: Any) -> Any:
        if isinstance(data, dict):
            d = cast(Dict[str, Any], data)
            host = d.get("host")
            if host and "ip" not in d:
                try:
                    # If host is an IP address, use it as the IP field
                    d["ip"] = ip_address(str(host))
                except ValueError:
                    # If host is a hostname, set ip equal to host for now
                    # The actual IP resolution should happen during validation
                    d["ip"] = str(host)
        return cast(Any, data)

    @field_validator("ip", mode="before")
    @classmethod
    def _validate_ip(cls, v: Any) -> Union[IPv4Address, IPv6Address, str]:
        """Validate IP address field, allowing valid hostnames as fallback."""
        if isinstance(v, (IPv4Address, IPv6Address)):
            return v
        if not isinstance(v, str):
            # Only allow strings and IP address objects
            raise ValueError("IP address must be a string or IP address")

        # Try to parse as IP address first
        try:
            return ip_address(str(v))
        except ValueError:
            pass

        # Check if it's a reasonable hostname format
        hostname = str(v)
        if not hostname or len(hostname) > 253:
            raise ValueError("Invalid hostname format")

        # Basic hostname validation
        # Must not start/end with dots, no consecutive dots
        if hostname.startswith(".") or hostname.endswith(".") or ".." in hostname:
            raise ValueError("Invalid hostname format")

        # Split into labels and check each
        labels = hostname.split(".")
        for label in labels:
            if not label or len(label) > 63:
                raise ValueError("Invalid hostname format")
            # Labels should contain only alphanumeric and hyphens
            # Must not start/end with hyphen
            if not all(c.isalnum() or c == "-" for c in label):
                raise ValueError("Invalid hostname format")
            if label.startswith("-") or label.endswith("-"):
                raise ValueError("Invalid hostname format")

        return hostname

    @field_validator("city", mode="before")
    @classmethod
    def _empty_to_none(cls, v: Any) -> Optional[str]:
        if isinstance(v, str):
            return v.strip() or None
        if v is None:
            return None
        return None

    @field_validator("response_time", mode="before")
    @classmethod
    def _coerce_response_time(cls, v: Any) -> Optional[float]:
        if v is None:
            return None
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    @field_validator("schemes", mode="before")
    @classmethod
    def _validate_schemes(cls, v: List[Any] | str | None) -> List[Scheme]:
        """
        Coerce input to List[Scheme], case-insensitive.
        """
        mapping = {
            "http": Scheme.HTTP,
            "https": Scheme.HTTPS,
            "socks4": Scheme.SOCKS4,
            "socks5": Scheme.SOCKS5,
        }
        items: Set[str] = set()
        if isinstance(v, str):
            for s in v.split(","):
                items.add(s.lower().strip())
        elif isinstance(v, list):
            for s in v:
                try:
                    items.add(str(s).lower().strip())
                except (TypeError, ValueError):
                    continue
        else:
            return []
        return [mapping[s] for s in items if s in mapping]

    @field_validator("anonymity", mode="before")
    @classmethod
    def _normalize_anonymity(cls, v: Any) -> AnonymityLevel:
        mapping = {
            "0": AnonymityLevel.TRANSPARENT,
            "1": AnonymityLevel.ANONYMOUS,
            "2": AnonymityLevel.ELITE,
        }
        if isinstance(v, str) and v.isdigit():
            return mapping.get(v, AnonymityLevel.UNKNOWN)
        if isinstance(v, AnonymityLevel):
            return v
        try:
            return AnonymityLevel(v.lower())
        except (ValueError, AttributeError):
            return AnonymityLevel.UNKNOWN

    @field_serializer("last_checked", when_used="json")
    def _serialize_last_checked(self, v: datetime) -> str:
        """Serialize datetime in clean ISO format for API compatibility."""
        return v.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    @field_serializer("schemes", mode="plain")
    def _serialize_schemes(self, schemes: List[Union[Scheme, str]]) -> List[str]:
        """Serialize schemes as string list for API compatibility."""
        return [s.value if isinstance(s, Scheme) else s for s in schemes]

    @field_serializer("metadata", mode="plain")
    def _serialize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced metadata serialization with computed stats (only when requested)."""
        # For normal serialization, return metadata as-is for round-trip compatibility
        # Computed fields can be accessed separately via the computed_field properties
        return dict(metadata)

    @computed_field
    @property
    def intelligent_quality_score(self) -> float:
        """Computed quality score based on multiple performance factors."""
        # Access field values using __dict__ to avoid FieldInfo issues
        metrics_value = self.__dict__.get("metrics")
        if metrics_value is None:
            return 0.5  # Neutral score for new proxies

        # Multi-factor quality calculation with weighted components
        success_weight = metrics_value.success_rate * 0.4

        # Speed component - faster proxies get higher scores
        speed_weight = 0.0
        if self.response_time is not None and self.response_time > 0:
            # Convert response time to score: 1 second = 0.3, 0.1 second = 1.0
            speed_weight = min(1.0, (1.0 / self.response_time) * 0.1) * 0.3

        # Uptime component
        uptime_weight = (metrics_value.uptime_percentage or 0.5) * 0.2

        # Anonymity premium - higher anonymity levels get bonus points
        anonymity_bonus = {
            AnonymityLevel.ELITE: 0.1,
            AnonymityLevel.ANONYMOUS: 0.07,
            AnonymityLevel.TRANSPARENT: 0.03,
            AnonymityLevel.UNKNOWN: 0.05,
        }.get(self.anonymity, 0.05)

        return min(1.0, success_weight + speed_weight + uptime_weight + anonymity_bonus)

    @computed_field
    @property
    def reliability_tier(self) -> str:
        """Computed reliability classification based on performance."""
        score = self.intelligent_quality_score
        if score >= 0.9:
            return "premium"
        elif score >= 0.7:
            return "standard"
        elif score >= 0.5:
            return "basic"
        else:
            return "unreliable"

    @computed_field
    @property
    def performance_category(self) -> str:
        """Performance category based on response time."""
        if self.response_time is None:
            return "untested"
        elif self.response_time < 0.5:
            return "fast"
        elif self.response_time < 2.0:
            return "moderate"
        elif self.response_time < 5.0:
            return "slow"
        else:
            return "very_slow"

    @computed_field
    @property
    def usage_recommendation(self) -> str:
        """Smart usage recommendation based on proxy characteristics."""
        if self.reliability_tier == "premium" and self.performance_category in ["fast", "moderate"]:
            return "recommended_for_production"
        elif self.reliability_tier in ["standard", "premium"]:
            return "suitable_for_general_use"
        elif self.reliability_tier == "basic":
            return "suitable_for_testing"
        else:
            return "not_recommended"

    @property
    def uris(self) -> Dict[str, str]:
        """Returns a dict of proxy URIs for each supported scheme with RFC 2732 IPv6 compliance."""
        # Format host with IPv6 brackets if needed per RFC 2732
        # Use IP field for proper type detection, fallback to host string
        host_formatted = f"[{self.ip}]" if isinstance(self.ip, IPv6Address) else str(self.host)
        return {scheme: f"{scheme}://{host_formatted}:{self.port}" for scheme in self.schemes}

    @property
    def authenticated_uri(self) -> str:
        """Primary proxy URI with authentication if available and RFC 2732 IPv6 compliance."""
        scheme = self.schemes[0]
        # Schemes are validated as Scheme enum values, extract string value
        scheme_str = scheme.value

        # Format host with IPv6 brackets if needed per RFC 2732
        # Use IP field for proper type detection, fallback to host string
        host_formatted = (
            f"[{self.ip}]"
            if self.ip and isinstance(self.ip, IPv6Address)
            else str(self.ip or self.host)
        )

        # Access field values using __dict__ to avoid FieldInfo issues
        credentials_value = self.__dict__.get("credentials")
        if credentials_value is not None:
            auth = f"{credentials_value.username}:{credentials_value.password}@"
        else:
            auth = ""
        return f"{scheme_str}://{auth}{host_formatted}:{self.port}"

    @property
    def is_healthy(self) -> bool:
        """Quick health check based on recent metrics."""
        if self.status != ProxyStatus.ACTIVE:
            return False
        # Access field values using __dict__ to avoid FieldInfo issues
        metrics_value = self.__dict__.get("metrics")
        if metrics_value is None or metrics_value.total_requests == 0:
            return True  # No data yet, assume healthy
        return metrics_value.success_rate >= 0.7


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
        frozen=True,  # Immutable after creation
        validate_assignment=True,  # Validate on assignment
        use_enum_values=True,
        populate_by_name=True,
        # Performance optimizations
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
    def is_production_ready(self) -> bool:
        """Determine if proxy meets production standards."""
        return (
            self.quality_score >= 0.8
            and self.response_time is not None
            and self.response_time < 2.0
            and self.anonymity in [AnonymityLevel.ANONYMOUS, AnonymityLevel.ELITE]
        )
