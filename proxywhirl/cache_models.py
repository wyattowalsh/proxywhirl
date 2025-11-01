"""
Pydantic models for cache data structures.

Defines data models for cache entries, configurations, and statistics
used across the three-tier caching system (L1/L2/L3).
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, SecretStr, computed_field, field_validator

__all__ = [
    "HealthStatus",
    "CacheEntry",
    "CacheTierConfig",
    "CacheConfig",
    "TierStatistics",
    "CacheStatistics",
]


class HealthStatus(str, Enum):
    """Proxy health status for cache entries."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class CacheEntry(BaseModel):
    """Container for a single cached proxy with metadata.

    Stores proxy information with TTL, health status, and access tracking.
    Credentials are SecretStr in memory, encrypted at rest in L2/L3.

    Example:
        >>> entry = CacheEntry(
        ...     key="abc123",
        ...     proxy_url="http://proxy.com:8080",
        ...     source="fetched",
        ...     fetch_time=datetime.now(timezone.utc),
        ...     ttl_seconds=3600,
        ... )
        >>> entry.is_expired
        False
    """

    # Identity
    key: str = Field(..., description="Unique cache key (proxy URL hash)")
    proxy_url: str = Field(..., description="Full proxy URL (scheme://host:port)")

    # Credentials (encrypted at rest in L2/L3, SecretStr in L1)
    username: Optional[SecretStr] = Field(None, description="Proxy username")
    password: Optional[SecretStr] = Field(None, description="Proxy password")

    # Metadata
    source: str = Field(..., description="Proxy source identifier")
    fetch_time: datetime = Field(..., description="When proxy was fetched")
    last_accessed: datetime = Field(..., description="Last cache access time")
    access_count: int = Field(default=0, description="Number of cache hits")

    # TTL & Health
    ttl_seconds: int = Field(..., ge=0, description="Time-to-live in seconds")
    expires_at: datetime = Field(..., description="Absolute expiration time")
    health_status: HealthStatus = Field(default=HealthStatus.UNKNOWN)
    failure_count: int = Field(default=0, ge=0, description="Consecutive failures")

    @property
    def is_expired(self) -> bool:
        """Check if entry has expired based on TTL."""
        return datetime.now(timezone.utc) >= self.expires_at

    @property
    def is_healthy(self) -> bool:
        """Check if proxy is healthy enough to use."""
        return self.health_status == HealthStatus.HEALTHY

    class Config:
        """Pydantic config."""

        json_encoders = {
            SecretStr: lambda v: "***",  # Never expose credentials in JSON
            datetime: lambda v: v.isoformat(),
        }


class CacheTierConfig(BaseModel):
    """Configuration for a single cache tier.

    Defines capacity, eviction policy, and enable/disable state for
    one tier (L1, L2, or L3).

    Example:
        >>> config = CacheTierConfig(max_entries=1000, eviction_policy="lru")
    """

    enabled: bool = Field(default=True, description="Enable this tier")
    max_entries: Optional[int] = Field(None, description="Max entries (None=unlimited)")
    eviction_policy: str = Field(default="lru", description="Eviction policy")

    @field_validator("eviction_policy")
    @classmethod
    def validate_policy(cls, v: str) -> str:
        """Validate eviction policy is supported."""
        allowed = ["lru", "lfu", "fifo"]
        if v not in allowed:
            raise ValueError(f"Invalid eviction policy: {v}. Must be one of {allowed}")
        return v


class CacheConfig(BaseModel):
    """Configuration for cache behavior and tier settings.

    Aggregates configuration for all three tiers plus global settings
    like TTL, cleanup intervals, and storage paths.

    Example:
        >>> config = CacheConfig(
        ...     default_ttl_seconds=3600,
        ...     l1_config=CacheTierConfig(max_entries=1000),
        ... )
    """

    # Tier Configuration
    l1_config: CacheTierConfig = Field(
        default_factory=lambda: CacheTierConfig(max_entries=1000),
        description="L1 (Memory) configuration",
    )
    l2_config: CacheTierConfig = Field(
        default_factory=lambda: CacheTierConfig(max_entries=5000),
        description="L2 (JSONL File) configuration",
    )
    l3_config: CacheTierConfig = Field(
        default_factory=lambda: CacheTierConfig(max_entries=None),
        description="L3 (SQLite) configuration",
    )

    # TTL Configuration
    default_ttl_seconds: int = Field(
        default=3600,
        ge=60,
        description="Default TTL for cached proxies (seconds)",
    )
    ttl_cleanup_interval: int = Field(
        default=60,
        ge=10,
        description="Background cleanup interval (seconds)",
    )
    enable_background_cleanup: bool = Field(
        default=False,
        description="Enable background TTL cleanup thread",
    )
    cleanup_interval_seconds: int = Field(
        default=60,
        ge=5,
        description="Interval between background cleanup runs (seconds)",
    )
    per_source_ttl: dict[str, int] = Field(
        default_factory=dict,
        description="Per-source TTL overrides (source_name -> ttl_seconds)",
    )

    # Storage Paths
    l2_cache_dir: str = Field(
        default=".cache/proxies",
        description="Directory for L2 JSONL file cache",
    )
    l3_database_path: str = Field(
        default=".cache/db/proxywhirl.db",
        description="SQLite database path for L3",
    )

    # Encryption
    encryption_key: Optional[SecretStr] = Field(
        None,
        description="Fernet encryption key (from env: PROXYWHIRL_CACHE_ENCRYPTION_KEY)",
    )

    # Health Integration
    health_check_invalidation: bool = Field(
        default=True,
        description="Auto-invalidate on health check failure",
    )
    failure_threshold: int = Field(
        default=3,
        ge=1,
        description="Failures before health invalidation",
    )

    # Performance Tuning
    enable_statistics: bool = Field(default=True, description="Track cache statistics")
    statistics_interval: int = Field(
        default=5, ge=1, description="Stats aggregation interval (seconds)"
    )

    class Config:
        """Pydantic config."""

        json_encoders = {
            SecretStr: lambda v: "***",
        }


class TierStatistics(BaseModel):
    """Statistics for a single cache tier.

    Tracks hits, misses, evictions by reason, and computes hit rate.

    Example:
        >>> stats = TierStatistics(hits=100, misses=20)
        >>> stats.hit_rate
        0.8333...
    """

    hits: int = Field(default=0, ge=0)
    misses: int = Field(default=0, ge=0)
    current_size: int = Field(default=0, ge=0)
    evictions_lru: int = Field(default=0, ge=0)
    evictions_ttl: int = Field(default=0, ge=0)
    evictions_health: int = Field(default=0, ge=0)
    evictions_corruption: int = Field(default=0, ge=0)

    @computed_field  # type: ignore[misc]
    @property
    def hit_rate(self) -> float:
        """Cache hit rate (0.0 to 1.0)."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    @computed_field  # type: ignore[misc]
    @property
    def total_evictions(self) -> int:
        """Total evictions across all reasons."""
        return (
            self.evictions_lru
            + self.evictions_ttl
            + self.evictions_health
            + self.evictions_corruption
        )


class CacheStatistics(BaseModel):
    """Aggregate cache statistics across all tiers.

    Combines tier-level statistics and tracks cross-tier operations
    like promotions and demotions.

    Example:
        >>> stats = CacheStatistics()
        >>> stats.l1_stats.hits = 100
        >>> stats.overall_hit_rate
        1.0
    """

    l1_stats: TierStatistics = Field(default_factory=TierStatistics)
    l2_stats: TierStatistics = Field(default_factory=TierStatistics)
    l3_stats: TierStatistics = Field(default_factory=TierStatistics)

    # Cross-tier operations
    promotions: int = Field(default=0, ge=0, description="L3→L2→L1 promotions")
    demotions: int = Field(default=0, ge=0, description="L1→L2→L3 demotions")

    # Degradation tracking
    l1_degraded: bool = Field(default=False, description="L1 tier unavailable")
    l2_degraded: bool = Field(default=False, description="L2 tier unavailable")
    l3_degraded: bool = Field(default=False, description="L3 tier unavailable")

    @computed_field  # type: ignore[misc]
    @property
    def overall_hit_rate(self) -> float:
        """Overall hit rate across all tiers."""
        total_hits = self.l1_stats.hits + self.l2_stats.hits + self.l3_stats.hits
        total_requests = (
            total_hits
            + self.l1_stats.misses
            + self.l2_stats.misses
            + self.l3_stats.misses
        )
        return total_hits / total_requests if total_requests > 0 else 0.0

    @computed_field  # type: ignore[misc]
    @property
    def total_size(self) -> int:
        """Total cached entries across all tiers."""
        return (
            self.l1_stats.current_size
            + self.l2_stats.current_size
            + self.l3_stats.current_size
        )

    def to_metrics_dict(self) -> dict[str, float]:
        """Convert to flat metrics dict for monitoring systems."""
        return {
            "cache.l1.hit_rate": self.l1_stats.hit_rate,
            "cache.l2.hit_rate": self.l2_stats.hit_rate,
            "cache.l3.hit_rate": self.l3_stats.hit_rate,
            "cache.overall.hit_rate": self.overall_hit_rate,
            "cache.total_size": float(self.total_size),
            "cache.promotions": float(self.promotions),
            "cache.demotions": float(self.demotions),
            "cache.l1.size": float(self.l1_stats.current_size),
            "cache.l2.size": float(self.l2_stats.current_size),
            "cache.l3.size": float(self.l3_stats.current_size),
        }
