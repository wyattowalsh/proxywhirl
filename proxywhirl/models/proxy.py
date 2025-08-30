"""proxywhirl/models/proxy.py -- Core proxy models for ProxyWhirl

This module contains the main proxy data models with intelligent features,
advanced validation, and comprehensive quality scoring capabilities.

Features:
- Enhanced canonical proxy model with computed fields
- Strict proxy model for production environments  
- Advanced validation patterns with context awareness
- Target-based health tracking and quality scoring
- Optimized serialization and performance patterns
"""

from __future__ import annotations

from datetime import datetime, timezone
from ipaddress import IPv4Address, IPv6Address, ip_address
from typing import Any, Dict, List, Optional, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
)

from .enums import AnonymityLevel, ProxyStatus, Scheme
from .performance import (
    ProxyCapabilities,
    ProxyCredentials,
    ProxyErrorState,
    ProxyPerformanceMetrics,
)
from .targets import TargetHealthStatus
from .types import CountryCode, PortNumber, QualityScore, ResponseTimeSeconds


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
    target_health: Dict[str, TargetHealthStatus] = Field(
        default_factory=dict,
        description="Per-target health status mapping target_id -> TargetHealthStatus",
    )

    @model_validator(mode="before")
    @classmethod
    def preprocess_data(cls, data: Any) -> Any:
        """Preprocess and normalize input data."""
        if isinstance(data, dict):
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
        if isinstance(v, str):
            # Handle single scheme string
            schemes = [v.lower().strip()]
        elif isinstance(v, list):
            schemes = [str(scheme).lower().strip() for scheme in v]
        else:
            raise ValueError(f"Schemes must be string or list of strings, got {type(v)}")
        
        # Validate each scheme
        valid_schemes = {s.value for s in Scheme}
        validated = []
        
        for scheme in schemes:
            if scheme in valid_schemes:
                validated.append(scheme)
        
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
        location_parts = []
        
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
