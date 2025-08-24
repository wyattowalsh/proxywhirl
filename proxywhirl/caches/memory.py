"""proxywhirl/caches/memory.py -- Production-ready memory cache with advanced LRU

Enterprise-grade in-memory cache with:
- Thread-safe LRU eviction with configurable TTL
- Advanced statistics and performance monitoring
- Async/sync hybrid patterns for maximum performance
- Memory-optimized data structures and cleanup
"""

from __future__ import annotations

import asyncio
import time
from collections import OrderedDict
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger

from proxywhirl.caches.base import BaseProxyCache, CacheFilters, CacheMetrics
from proxywhirl.models import CacheType, Proxy


class MemoryProxyCache(BaseProxyCache):
    """Production-ready high-performance LRU memory cache with advanced features."""

    def __init__(
        self,
        max_size: int = 10000,
        ttl_seconds: int = 3600,
        eviction_batch_size: int = 100,
        enable_stats: bool = True,
    ):
        super().__init__(CacheType.MEMORY, None)

        # Configuration
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.eviction_batch_size = eviction_batch_size
        self.enable_stats = enable_stats

        # Thread-safe LRU cache: key -> (proxy, access_time, expire_time, access_count)
        self._cache: OrderedDict[Tuple[str, int], Tuple[Proxy, float, float, int]] = OrderedDict()
        self._lock = RLock()  # Reentrant lock for complex operations
        self._initialized = True

        # Advanced statistics with proper typing
        self._stats: Dict[str, Any] = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expired_cleanups": 0,
            "total_access_time": 0.0,
            "last_cleanup": time.time(),
            "peak_size": 0,
        }

        # Background cleanup task
        self._cleanup_task: Optional[asyncio.Task[None]] = None
        self._start_background_cleanup()

    def _start_background_cleanup(self) -> None:
        """Start background cleanup task for expired entries."""
        try:
            if self._cleanup_task is None or self._cleanup_task.done():
                self._cleanup_task = asyncio.create_task(self._background_cleanup())
        except RuntimeError:
            # No event loop running - cleanup will happen on access
            logger.debug("No event loop available for background cleanup")

    async def _background_cleanup(self) -> None:
        """Background task to clean up expired entries."""
        try:
            while True:
                await asyncio.sleep(min(300, self.ttl_seconds // 4))
                await self._cleanup_expired_entries()
        except asyncio.CancelledError:
            logger.debug("Memory cache background cleanup cancelled")
        except Exception as e:
            logger.error(f"Memory cache background cleanup error: {e}")

    async def _cleanup_expired_entries(self) -> int:
        """Clean up expired entries and return count of removed entries."""
        current_time = time.time()
        expired_keys: List[Tuple[str, int]] = []

        with self._lock:
            for key, (_, _, expire_time, _) in self._cache.items():
                if current_time > expire_time:
                    expired_keys.append(key)

            for key in expired_keys:
                del self._cache[key]
                self._stats["expired_cleanups"] += 1

            self._stats["last_cleanup"] = current_time

        return len(expired_keys)

    async def add_proxies(self, proxies: List[Proxy]) -> None:
        """Add proxies with intelligent LRU management and batch optimization."""
        if not proxies:
            return

        current_time = time.time()
        expire_time = current_time + self.ttl_seconds

        with self._lock:
            for proxy in proxies:
                key = (proxy.host, proxy.port)

                # Add/update proxy with access count
                if key in self._cache:
                    # Update existing entry and mark as recently used
                    _, _, _, access_count = self._cache[key]
                    self._cache[key] = (proxy, current_time, expire_time, access_count + 1)
                    self._cache.move_to_end(key)  # Mark as recently used
                else:
                    self._cache[key] = (proxy, current_time, expire_time, 1)

                # Memory pressure eviction
                if len(self._cache) > self.max_size:
                    self._evict_lru_batch()

            # Update peak size tracking
            self._stats["peak_size"] = max(self._stats["peak_size"], len(self._cache))

        # Schedule background cleanup if needed
        self._start_background_cleanup()

        # Update metrics
        self._update_metrics_from_cache()

    def _evict_lru_batch(self) -> None:
        """Evict least recently used entries in batches for better performance."""
        evict_count = min(
            self.eviction_batch_size, len(self._cache) - self.max_size + self.eviction_batch_size
        )

        for _ in range(evict_count):
            if self._cache:
                self._cache.popitem(last=False)  # Remove oldest (LRU)
                self._stats["evictions"] += 1

    async def get_proxies(self, filters: Optional[CacheFilters] = None) -> List[Proxy]:
        """Get proxies with LRU update and intelligent filtering."""
        start_time = time.time()
        current_time = start_time
        proxies: List[Proxy] = []
        expired_keys: List[Tuple[str, int]] = []

        with self._lock:
            # Collect valid proxies and identify expired ones
            for key, (proxy, access_time, expire_time, access_count) in self._cache.items():
                if current_time > expire_time:
                    expired_keys.append(key)
                else:
                    # Update access time and count for active entries
                    self._cache[key] = (proxy, current_time, expire_time, access_count + 1)
                    proxies.append(proxy)
                    self._cache.move_to_end(key)  # Mark as recently used

            # Clean up expired entries
            for key in expired_keys:
                del self._cache[key]
                self._stats["expired_cleanups"] += 1

            # Update statistics
            if proxies:
                self._stats["hits"] += len(proxies)
            else:
                self._stats["misses"] += 1

        # Apply filters (outside lock for better concurrency)
        filtered_proxies = self._apply_filters(proxies, filters)

        # Update performance metrics
        access_time = time.time() - start_time
        self._stats["total_access_time"] += access_time

        # Update cache metrics
        self._update_metrics_from_cache()

        return filtered_proxies

    async def update_proxy(self, proxy: Proxy) -> None:
        """Update proxy with LRU positioning."""
        current_time = time.time()
        expire_time = current_time + self.ttl_seconds
        key = (proxy.host, proxy.port)

        with self._lock:
            if key in self._cache:
                _, _, _, access_count = self._cache[key]
                self._cache[key] = (proxy, current_time, expire_time, access_count)
                self._cache.move_to_end(key)  # Mark as recently used
            else:
                self._cache[key] = (proxy, current_time, expire_time, 1)

        self._update_metrics_from_cache()

    async def remove_proxy(self, proxy: Proxy) -> None:
        """Remove proxy from cache."""
        key = (proxy.host, proxy.port)

        with self._lock:
            if key in self._cache:
                del self._cache[key]

        self._update_metrics_from_cache()

    async def clear(self) -> None:
        """Clear all cached proxies."""
        with self._lock:
            self._cache.clear()
            # Reset statistics except cumulative ones
            self._stats.update(
                {"hits": 0, "misses": 0, "evictions": 0, "expired_cleanups": 0, "peak_size": 0}
            )

        self._update_metrics_from_cache()

    def _update_metrics_from_cache(self) -> None:
        """Update cache metrics from current cache state."""
        with self._lock:
            current_proxies = [proxy for proxy, _, _, _ in self._cache.values()]
        self._update_metrics(current_proxies)

    async def get_health_metrics(self) -> CacheMetrics:
        """Get comprehensive cache health metrics."""
        with self._lock:
            cache_size = len(self._cache)

            # Update base metrics
            self._metrics.cache_hits = self._stats["hits"]
            self._metrics.cache_misses = self._stats["misses"]
            self._metrics.total_proxies = cache_size
            self._metrics.last_updated = datetime.now(timezone.utc)

        return self._metrics

    # === Advanced Memory Cache Analytics ===

    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Get detailed cache performance statistics."""
        with self._lock:
            total_ops = self._stats["hits"] + self._stats["misses"]

            return {
                **self._stats.copy(),
                "cache_size": len(self._cache),
                "hit_rate": self._stats["hits"] / total_ops if total_ops > 0 else 0.0,
                "memory_efficiency": len(self._cache) / self.max_size if self.max_size > 0 else 0.0,
                "average_access_time": (
                    self._stats["total_access_time"] / self._stats["hits"]
                    if self._stats["hits"] > 0
                    else 0.0
                ),
                "cache_pressure": len(self._cache) / self.max_size if self.max_size > 0 else 0.0,
            }

    async def get_hot_proxies(self, limit: int = 10) -> List[Tuple[Proxy, int]]:
        """Get most frequently accessed proxies."""
        with self._lock:
            # Sort by access count (4th element in tuple)
            sorted_items = sorted(
                self._cache.items(), key=lambda x: x[1][3], reverse=True  # access_count
            )

            return [
                (proxy, access_count) for _, (proxy, _, _, access_count) in sorted_items[:limit]
            ]

    def __del__(self):
        """Cleanup background task on destruction."""
        if hasattr(self, "_cleanup_task") and self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
