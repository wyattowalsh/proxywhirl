"""proxywhirl/caches/base.py -- Abstract base class for cache implementations

Provides unified interface for all cache backends with consistent async/sync patterns,
health metrics, and extensible architecture for custom cache implementations.
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, TypeVar

from pydantic import BaseModel, Field

from proxywhirl.models import CacheType, Proxy

if TYPE_CHECKING:
    pass

T = TypeVar("T")


class DuplicateStrategy(StrEnum):
    """Strategy for handling duplicate proxies based on (host, port) key."""

    UPDATE = "update"  # Update existing proxy with new data (default)
    IGNORE = "ignore"  # Keep existing proxy, ignore new data
    ERROR = "error"  # Raise error when duplicate detected


class CacheMetrics(BaseModel):
    """Comprehensive cache performance and health metrics with advanced analytics."""

    # Basic proxy counts
    total_proxies: int = 0
    healthy_proxies: int = 0
    unhealthy_proxies: int = 0

    # Cache performance
    cache_hits: int = 0
    cache_misses: int = 0
    cache_evictions: int = 0

    # Response metrics
    last_updated: Optional[datetime] = None
    avg_response_time: Optional[float] = None
    success_rate: float = 0.0

    # Advanced analytics
    geographic_distribution: Dict[str, int] = Field(default_factory=dict)
    source_reliability: Dict[str, float] = Field(default_factory=dict)
    quality_distribution: Dict[str, int] = Field(default_factory=dict)

    # Performance trends (last 24h)
    hourly_success_rates: List[float] = Field(default_factory=list)
    hourly_response_times: List[Optional[float]] = Field(default_factory=list)

    # Health monitoring
    last_health_check: Optional[datetime] = None
    health_check_count: int = 0
    critical_failures: int = 0

    # Resource utilization (for memory/SQLite)
    memory_usage_mb: Optional[float] = None
    disk_usage_mb: Optional[float] = None
    connection_pool_active: Optional[int] = None
    connection_pool_idle: Optional[int] = None

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0

    @property
    def health_rate(self) -> float:
        """Calculate proxy health rate."""
        return self.healthy_proxies / self.total_proxies if self.total_proxies > 0 else 0.0

    @property
    def cache_efficiency(self) -> float:
        """Calculate cache efficiency score (hit rate weighted by evictions)."""
        if self.cache_hits == 0:
            return 0.0
        hit_rate = self.hit_rate
        # Penalize high eviction rates
        eviction_penalty = self.cache_evictions / max(1, self.cache_hits + self.cache_misses)
        return max(0.0, hit_rate - (eviction_penalty * 0.1))

    @property
    def overall_health_score(self) -> float:
        """Calculate comprehensive health score combining multiple factors."""
        if self.total_proxies == 0:
            return 0.0

        # Component scores (0-1)
        proxy_health = self.health_rate
        cache_performance = self.cache_efficiency
        response_quality = (
            min(1.0, 1.0 / max(1.0, self.avg_response_time or 1.0))
            if self.avg_response_time
            else 1.0
        )

        # Weighted average
        score = (proxy_health * 0.5) + (cache_performance * 0.3) + (response_quality * 0.2)
        return round(score, 3)


class HealthMetricsCollector:
    """Unified metrics collection interface for all cache backends."""

    def __init__(self, cache: BaseProxyCache):
        self.cache = cache
        self._collection_interval = 60  # seconds
        self._last_collection: Optional[datetime] = None

    async def collect_comprehensive_metrics(self) -> CacheMetrics:
        """Collect comprehensive metrics from cache backend."""
        base_metrics = await self.cache.get_health_metrics()

        # Enhance with backend-specific analytics
        if hasattr(self.cache, "get_geographic_analytics"):
            try:
                geo_analytics: Any = await self.cache.get_geographic_analytics()  # type: ignore
                if geo_analytics and isinstance(geo_analytics, dict):
                    base_metrics.geographic_distribution = {
                        item["country_code"]: item["total_proxies"]
                        for item in geo_analytics.get("geographic", [])
                        if isinstance(item, dict)
                        and "country_code" in item
                        and "total_proxies" in item
                    }
                    base_metrics.source_reliability = {
                        item["source"]: item["avg_quality"]
                        for item in geo_analytics.get("source_reliability", [])
                        if isinstance(item, dict) and "source" in item and "avg_quality" in item
                    }
            except Exception:
                pass  # Graceful fallback on analytics errors

        # Add performance trends if available
        if hasattr(self.cache, "get_performance_trends"):
            try:
                trends: Any = await self.cache.get_performance_trends(hours=24)  # type: ignore
                if trends and isinstance(trends, dict):
                    hourly_data = trends.get("hourly_trends", [])
                    if isinstance(hourly_data, list):
                        base_metrics.hourly_success_rates = [
                            item.get("avg_success_rate", 0.0) or 0.0
                            for item in hourly_data[-24:]
                            if isinstance(item, dict)
                        ]
                        base_metrics.hourly_response_times = [
                            item.get("avg_response_time")
                            for item in hourly_data[-24:]
                            if isinstance(item, dict)
                        ]
            except Exception:
                pass  # Graceful fallback on trends errors

        # Resource utilization for memory caches
        if hasattr(self.cache, "get_memory_usage"):
            try:
                base_metrics.memory_usage_mb = await self.cache.get_memory_usage()  # type: ignore
            except Exception:
                pass

        # Connection pool metrics for SQLite
        if hasattr(self.cache, "get_connection_metrics"):
            try:
                conn_metrics: Any = await self.cache.get_connection_metrics()  # type: ignore
                if conn_metrics and isinstance(conn_metrics, dict):
                    base_metrics.connection_pool_active = conn_metrics.get("active_connections")
                    base_metrics.connection_pool_idle = conn_metrics.get("idle_connections")
            except Exception:
                pass

        base_metrics.last_health_check = datetime.now(timezone.utc)
        self._last_collection = base_metrics.last_health_check

        return base_metrics

    async def should_collect_metrics(self) -> bool:
        """Check if metrics collection is due."""
        if self._last_collection is None:
            return True
        elapsed = (datetime.now(timezone.utc) - self._last_collection).total_seconds()
        return elapsed >= self._collection_interval

    def set_collection_interval(self, seconds: int) -> None:
        """Configure metrics collection frequency."""
        self._collection_interval = max(10, seconds)  # Minimum 10 seconds


class CacheFilters(BaseModel):
    """Standardized filter parameters for cache queries."""

    healthy_only: bool = False
    country_codes: Optional[List[str]] = None
    schemes: Optional[List[str]] = None
    min_response_time: Optional[float] = None
    max_response_time: Optional[float] = None
    min_success_rate: Optional[float] = None
    sources: Optional[List[str]] = None
    limit: Optional[int] = None
    offset: int = 0


class BaseProxyCache(ABC):
    """Abstract base class for proxy cache implementations.

    Provides unified interface for memory, JSON, SQLite, and future cache backends
    with consistent async patterns, health metrics, and filtering capabilities.
    """

    def __init__(
        self,
        cache_type: CacheType,
        cache_path: Optional[Path] = None,
        duplicate_strategy: DuplicateStrategy = DuplicateStrategy.UPDATE,
    ):
        self.cache_type = cache_type
        self.cache_path = cache_path
        self.duplicate_strategy = duplicate_strategy
        self._metrics = CacheMetrics()
        self._initialized = False

    @abstractmethod
    async def add_proxies(self, proxies: List[Proxy]) -> None:
        """Add proxies to cache with backend-specific optimizations."""
        pass

    @abstractmethod
    async def get_proxies(self, filters: Optional[CacheFilters] = None) -> List[Proxy]:
        """Get proxies from cache with optional filtering."""
        pass

    @abstractmethod
    async def update_proxy(self, proxy: Proxy) -> None:
        """Update a proxy in cache."""
        pass

    @abstractmethod
    async def remove_proxy(self, proxy: Proxy) -> None:
        """Remove a proxy from cache."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all proxies from cache."""
        pass

    @abstractmethod
    async def get_health_metrics(self) -> CacheMetrics:
        """Get cache health and performance metrics."""
        pass

    # === Duplicate Handling Utilities ===

    def _handle_duplicate(
        self, existing_proxy: Optional[Proxy], new_proxy: Proxy
    ) -> tuple[bool, Optional[Proxy]]:
        """Handle duplicate proxy based on configured strategy.

        Returns:
            tuple: (should_add_or_update, proxy_to_use)
            - should_add_or_update: True if proxy should be added/updated
            - proxy_to_use: The proxy object to use (None if ignoring)
        """
        if existing_proxy is None:
            return True, new_proxy  # No duplicate, add new proxy

        if self.duplicate_strategy == DuplicateStrategy.UPDATE:
            return True, new_proxy  # Update existing with new data
        elif self.duplicate_strategy == DuplicateStrategy.IGNORE:
            return False, existing_proxy  # Keep existing, ignore new
        elif self.duplicate_strategy == DuplicateStrategy.ERROR:
            raise ValueError(f"Duplicate proxy detected: {new_proxy.host}:{new_proxy.port}")
        else:
            # Default to UPDATE for unknown strategies
            return True, new_proxy

    def _get_proxy_key(self, proxy: Proxy) -> tuple[str, int]:
        """Get standardized deduplication key for proxy."""
        return (proxy.host, proxy.port)

    # === Health Analysis Methods (Backend-Specific Implementation) ===

    async def get_trending_proxies(self, hours: int = 24, limit: int = 10) -> List[Proxy]:
        """Get proxies with improving health trends (default implementation)."""
        # Base implementation - backends can override with optimized queries
        # Note: hours parameter for future backend-specific implementations
        proxies = await self.get_proxies(CacheFilters(healthy_only=True, limit=limit))
        return proxies[:limit]

    async def get_geographic_stats(self) -> Dict[str, int]:
        """Get proxy distribution by country (default implementation)."""
        proxies = await self.get_proxies()
        stats: Dict[str, int] = {}
        for proxy in proxies:
            country = proxy.country_code or "Unknown"
            stats[country] = stats.get(country, 0) + 1
        return stats

    async def get_source_reliability(self) -> Dict[str, float]:
        """Get success rate by proxy source (default implementation)."""
        proxies = await self.get_proxies()
        source_stats: Dict[str, Dict[str, int]] = {}

        for proxy in proxies:
            source = proxy.source or "Unknown"
            if source not in source_stats:
                source_stats[source] = {"total": 0, "healthy": 0}

            source_stats[source]["total"] += 1
            if hasattr(proxy, "is_healthy") and proxy.is_healthy:
                source_stats[source]["healthy"] += 1

        return {
            source: stats["healthy"] / stats["total"] if stats["total"] > 0 else 0.0
            for source, stats in source_stats.items()
        }

    # === Utility Methods ===

    def _apply_filters(self, proxies: List[Proxy], filters: Optional[CacheFilters]) -> List[Proxy]:
        """Apply filters to proxy list (used by backends)."""
        if not filters:
            return proxies

        result = proxies.copy()

        if filters.healthy_only:
            result = [p for p in result if getattr(p, "is_healthy", True)]

        if filters.country_codes:
            result = [p for p in result if p.country_code in filters.country_codes]

        if filters.schemes:
            result = [p for p in result if any(s.value in filters.schemes for s in p.schemes)]

        if filters.min_response_time is not None:
            result = [
                p
                for p in result
                if p.response_time and p.response_time >= filters.min_response_time
            ]

        if filters.max_response_time is not None:
            result = [
                p
                for p in result
                if p.response_time and p.response_time <= filters.max_response_time
            ]

        if filters.sources:
            result = [p for p in result if p.source in filters.sources]

        # Apply pagination
        if filters.offset > 0:
            result = result[filters.offset :]

        if filters.limit is not None:
            result = result[: filters.limit]

        return result

    def _update_metrics(self, proxies: List[Proxy]) -> None:
        """Update cache metrics based on current proxy list."""
        self._metrics.total_proxies = len(proxies)
        self._metrics.healthy_proxies = sum(1 for p in proxies if getattr(p, "is_healthy", True))
        self._metrics.unhealthy_proxies = (
            self._metrics.total_proxies - self._metrics.healthy_proxies
        )
        self._metrics.last_updated = datetime.now(timezone.utc)

        if proxies:
            response_times = [p.response_time for p in proxies if p.response_time is not None]
            self._metrics.avg_response_time = (
                sum(response_times) / len(response_times) if response_times else None
            )
            self._metrics.success_rate = self._metrics.healthy_proxies / self._metrics.total_proxies
        else:
            self._metrics.avg_response_time = None
            self._metrics.success_rate = 0.0

    # === Sync Wrappers for Backward Compatibility ===

    def add_proxies_sync(self, proxies: List[Proxy]) -> None:
        """Synchronous wrapper for add_proxies."""
        asyncio.run(self.add_proxies(proxies))

    def get_proxies_sync(self, filters: Optional[CacheFilters] = None) -> List[Proxy]:
        """Synchronous wrapper for get_proxies."""
        return asyncio.run(self.get_proxies(filters))

    def clear_sync(self) -> None:
        """Synchronous wrapper for clear."""
        asyncio.run(self.clear())

    def get_health_metrics_sync(self) -> CacheMetrics:
        """Synchronous wrapper for get_health_metrics."""
        return asyncio.run(self.get_health_metrics())

    def update_proxy_sync(self, proxy: Proxy) -> None:
        """Synchronous wrapper for update_proxy."""
        asyncio.run(self.update_proxy(proxy))

    def remove_proxy_sync(self, proxy: Proxy) -> None:
        """Synchronous wrapper for remove_proxy."""
        asyncio.run(self.remove_proxy(proxy))

    def get_stats_sync(self) -> Dict[str, Any]:
        """Synchronous wrapper for get_stats if available."""
        if hasattr(self, "get_stats"):
            return asyncio.run(self.get_stats())  # type: ignore
        return {}
