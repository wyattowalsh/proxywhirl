"""proxywhirl/caches/base.py -- Abstract base class for cache implementations

Provides unified interface for all cache backends with consistent async/sync patterns,
health metrics, and extensible architecture for custom cache implementations.
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, TypeVar

from pydantic import BaseModel

from proxywhirl.models import CacheType, Proxy

T = TypeVar("T")


class CacheMetrics(BaseModel):
    """Cache performance and health metrics."""

    total_proxies: int = 0
    healthy_proxies: int = 0
    unhealthy_proxies: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    last_updated: Optional[datetime] = None
    avg_response_time: Optional[float] = None
    success_rate: float = 0.0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0

    @property
    def health_rate(self) -> float:
        """Calculate proxy health rate."""
        return self.healthy_proxies / self.total_proxies if self.total_proxies > 0 else 0.0


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

    def __init__(self, cache_type: CacheType, cache_path: Optional[Path] = None):
        self.cache_type = cache_type
        self.cache_path = cache_path
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
