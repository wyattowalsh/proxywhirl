"""Proxy validation performance optimization.

Optimizes validation workflows to reduce latency
and resource consumption.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from loguru import logger


@dataclass
class ValidationMetrics:
    """Metrics for validation performance."""

    total_validated: int = 0
    successful: int = 0
    failed: int = 0
    avg_time_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0


class ValidationOptimizer:
    """Optimizes proxy validation performance."""

    def __init__(self) -> None:
        """Initialize validation optimizer."""
        self._metrics = ValidationMetrics()
        self._validation_cache: dict[str, dict[str, Any]] = {}
        logger.debug("ValidationOptimizer initialized")

    def cache_validation_result(
        self, proxy_id: str, result: dict[str, Any], ttl_seconds: int = 3600
    ) -> bool:
        """Cache validation result.

        Args:
            proxy_id: Proxy ID
            result: Validation result
            ttl_seconds: Cache TTL

        Returns:
            True if cached
        """
        import time

        self._validation_cache[proxy_id] = {
            "result": result,
            "cached_at": time.time(),
            "ttl": ttl_seconds,
        }
        logger.debug(f"Validation result cached: {proxy_id}")
        return True

    def get_cached_result(self, proxy_id: str) -> dict[str, Any] | None:
        """Get cached validation result.

        Args:
            proxy_id: Proxy ID

        Returns:
            Validation result or None
        """
        import time

        if proxy_id not in self._validation_cache:
            self._metrics.cache_misses += 1
            return None

        cached = self._validation_cache[proxy_id]
        age_seconds = time.time() - cached["cached_at"]

        if age_seconds > cached["ttl"]:
            del self._validation_cache[proxy_id]
            self._metrics.cache_misses += 1
            return None

        self._metrics.cache_hits += 1
        logger.debug(f"Cache hit: {proxy_id}")
        return cached["result"]

    def invalidate_cache(self, proxy_id: str | None = None) -> int:
        """Invalidate cache entries.

        Args:
            proxy_id: Proxy ID (None for all)

        Returns:
            Number of invalidated entries
        """
        if proxy_id is None:
            count = len(self._validation_cache)
            self._validation_cache.clear()
            logger.info(f"Cache cleared: {count} entries")
            return count

        if proxy_id in self._validation_cache:
            del self._validation_cache[proxy_id]
            logger.debug(f"Cache invalidated: {proxy_id}")
            return 1

        return 0

    def record_validation(self, duration_ms: float, success: bool) -> None:
        """Record validation metrics.

        Args:
            duration_ms: Validation duration
            success: Whether validation succeeded
        """
        self._metrics.total_validated += 1
        if success:
            self._metrics.successful += 1
        else:
            self._metrics.failed += 1

        total_time = self._metrics.avg_time_ms * (self._metrics.total_validated - 1)
        self._metrics.avg_time_ms = (total_time + duration_ms) / self._metrics.total_validated

    def export_metrics(self) -> dict[str, Any]:
        """Export validation metrics.

        Returns:
            Dictionary of metrics
        """
        cache_ratio = (
            (self._metrics.cache_hits / (self._metrics.cache_hits + self._metrics.cache_misses))
            if (self._metrics.cache_hits + self._metrics.cache_misses) > 0
            else 0.0
        )

        return {
            "total_validated": self._metrics.total_validated,
            "successful": self._metrics.successful,
            "failed": self._metrics.failed,
            "avg_time_ms": self._metrics.avg_time_ms,
            "cache_size": len(self._validation_cache),
            "cache_hits": self._metrics.cache_hits,
            "cache_misses": self._metrics.cache_misses,
            "cache_hit_ratio": cache_ratio,
        }
