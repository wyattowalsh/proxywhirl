"""proxywhirl/models/enums.py -- Enumeration types for ProxyWhirl

This module contains all enumeration types used throughout ProxyWhirl for
standardized values and type safety.

Features:
- String-based enums for serialization compatibility
- Comprehensive status and type definitions
- Enhanced rotation strategies and error handling policies
- ML feature types for adaptive proxy selection
"""

from __future__ import annotations

from enum import StrEnum, auto


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


# Legacy aliases for backward compatibility
ProxyScheme = Scheme
