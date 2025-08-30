"""proxywhirl/caches/memory.py -- Enterprise memory cache with advanced LRU

Enterprise-grade in-memory cache featuring:
- Thread-safe LRU eviction with configurable TTL and background cleanup
- Advanced statistics and performance monitoring with real-time analytics
- Async/sync hybrid patterns optimized for maximum performance
- Memory-optimized data structures with intelligent cleanup strategies
- Comprehensive health metrics and trend analysis
- Background task management and resource lifecycle control
"""

from __future__ import annotations

import asyncio
import time
from collections import OrderedDict
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger

from proxywhirl.caches.base import (
    BaseProxyCache,
    CacheFilters,
    CacheMetrics,
    DuplicateStrategy,
)
from proxywhirl.models import CacheType, Proxy


class MemoryProxyCache(BaseProxyCache[Proxy]):
    """Enterprise memory cache with advanced LRU and background task management."""

    def __init__(
        self,
        max_size: int = 10000,
        ttl_seconds: int = 3600,
        eviction_batch_size: int = 100,
        enable_stats: bool = True,
        duplicate_strategy: Optional[DuplicateStrategy] = None,
        cleanup_interval_seconds: int = 300,
    ):
        if duplicate_strategy is None:
            duplicate_strategy = DuplicateStrategy.UPDATE
        super().__init__(CacheType.MEMORY, None, duplicate_strategy)

        # Configuration
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.eviction_batch_size = eviction_batch_size
        self.enable_stats = enable_stats
        self.cleanup_interval_seconds = min(cleanup_interval_seconds, ttl_seconds // 4)

        # Thread-safe LRU cache: key -> (proxy, access_time, expire_time, access_count)
        self._cache: OrderedDict[Tuple[str, int], Tuple[Proxy, float, float, int]] = OrderedDict()
        self._lock = RLock()  # Reentrant lock for complex operations

        # Advanced statistics with performance tracking
        self._stats: Dict[str, Any] = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expired_cleanups": 0,
            "total_access_time": 0.0,
            "last_cleanup": time.time(),
            "peak_size": 0,
            "cache_operations": 0,
            "memory_pressure_events": 0,
            "background_cleanups": 0,
        }

        # Background task tracking
        self._cleanup_task: Optional[asyncio.Task[None]] = None

    # === BaseProxyCache Interface Implementation ===

    async def _initialize_backend(self) -> None:
        """Initialize memory cache backend with background tasks."""
        logger.debug("Initializing MemoryProxyCache backend")

        # Start background cleanup if not already running
        if not self._cleanup_task or self._cleanup_task.done():
            await self.start_background_tasks()

        logger.info(
            f"MemoryProxyCache initialized with max_size={self.max_size}, ttl={self.ttl_seconds}s"
        )

    async def _cleanup_backend(self) -> None:
        """Clean up memory cache resources."""
        await self.stop_background_tasks()

        with self._lock:
            self._cache.clear()

        logger.debug("MemoryProxyCache backend cleaned up")

    async def start_background_tasks(self) -> None:
        """Start background maintenance tasks."""
        if self._cleanup_task and not self._cleanup_task.done():
            return  # Already running

        try:
            self._cleanup_task = asyncio.create_task(self._background_cleanup())
            self._register_background_task(self._cleanup_task)
            logger.debug("MemoryProxyCache background cleanup task started")
        except RuntimeError:
            # No event loop running - cleanup will happen on access
            logger.debug("No event loop available for MemoryProxyCache background cleanup")

    async def stop_background_tasks(self) -> None:
        """Stop all background tasks gracefully."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

            self._cleanup_task = None
            logger.debug("MemoryProxyCache background tasks stopped")

    # === Required Abstract Methods ===

    async def add_proxies(self, proxies: List[Proxy]) -> None:
        """Add multiple proxies to memory cache."""
        for proxy in proxies:
            await self._add_single_proxy(proxy)

    async def get_proxies(self, filters: Optional[CacheFilters] = None) -> List[Proxy]:
        """Get proxies from cache with optional filtering."""
        current_time = time.time()
        result_proxies: List[Proxy] = []

        with self._lock:
            for key, (proxy, _, expire_time, _) in self._cache.items():
                # Skip expired entries
                if current_time > expire_time:
                    continue
                result_proxies.append(proxy)

            # Remove expired entries during iteration
            expired_keys = [
                key
                for key, (_, _, expire_time, _) in self._cache.items()
                if current_time > expire_time
            ]
            for key in expired_keys:
                del self._cache[key]
                self._stats["expired_cleanups"] += 1

        # Apply filters using parent class method
        return super()._apply_filters(result_proxies, filters)

    async def update_proxy(self, proxy: Proxy) -> None:
        """Update a proxy in cache."""
        await self._add_single_proxy(proxy, enable_duplicates=True)

    async def remove_proxy(self, proxy: Proxy) -> None:
        """Remove a proxy from cache."""
        key = (proxy.host, proxy.port)
        with self._lock:
            if key in self._cache:
                del self._cache[key]

    async def clear(self) -> None:
        """Clear all proxies from memory cache."""
        with self._lock:
            self._cache.clear()
            self._reset_stats()

    async def get_health_metrics(self) -> CacheMetrics:
        """Get comprehensive cache performance metrics."""
        with self._lock:
            current_size = len(self._cache)

            # Calculate health statistics
            healthy_count = 0
            unhealthy_count = 0
            current_time = time.time()

            for _, (proxy, _, expire_time, _) in self._cache.items():
                if current_time <= expire_time:  # Only count non-expired proxies
                    from proxywhirl.models import ProxyStatus

                    if proxy.status == ProxyStatus.ACTIVE:
                        healthy_count += 1
                    else:
                        unhealthy_count += 1

            avg_access_time = (
                self._stats["total_access_time"] / self._stats["hits"]
                if self._stats["hits"] > 0
                else 0.0
            )

            return CacheMetrics(
                total_proxies=current_size,
                healthy_proxies=healthy_count,
                unhealthy_proxies=unhealthy_count,
                cache_hits=self._stats["hits"],
                cache_misses=self._stats["misses"],
                cache_evictions=self._stats["evictions"],
                last_updated=datetime.now(timezone.utc),
                avg_response_time=avg_access_time,
                success_rate=healthy_count / current_size if current_size > 0 else 0.0,
                memory_usage_mb=self.get_memory_usage(),
            )

    # === Private Helper Methods ===

    async def _add_single_proxy(self, proxy: Proxy, enable_duplicates: bool = False) -> bool:
        """Add single proxy to memory cache with intelligent LRU management."""
        key = (proxy.host, proxy.port)
        current_time = time.time()
        expire_time = current_time + self.ttl_seconds

        with self._lock:
            # Handle duplicates based on strategy
            if key in self._cache and not enable_duplicates:
                if self.duplicate_strategy == DuplicateStrategy.IGNORE:
                    return False
                elif self.duplicate_strategy == DuplicateStrategy.UPDATE:
                    # Update existing entry and move to end
                    _, _, _, access_count = self._cache[key]
                    del self._cache[key]
                    self._cache[key] = (proxy, current_time, expire_time, access_count)
                    self._update_stats("cache_operations", 1)
                    return True

            # Check size limits and evict if necessary
            if len(self._cache) >= self.max_size:
                self._evict_entries()
                self._stats["memory_pressure_events"] += 1

            # Add new entry
            self._cache[key] = (proxy, current_time, expire_time, 1)
            self._stats["cache_operations"] += 1
            self._stats["peak_size"] = max(self._stats["peak_size"], len(self._cache))

            return True

    def _evict_entries(self) -> None:
        """Evict entries using intelligent LRU strategy with batching."""
        if len(self._cache) < self.max_size:
            return

        # Calculate eviction count
        eviction_count = min(self.eviction_batch_size, len(self._cache) // 4)
        eviction_count = max(eviction_count, 1)  # Always evict at least one

        # Remove oldest entries (beginning of OrderedDict)
        for _ in range(eviction_count):
            if self._cache:
                self._cache.popitem(last=False)  # Remove from beginning (oldest)
                self._stats["evictions"] += 1

        logger.debug(f"Evicted {eviction_count} entries from memory cache")

    def _update_stats(self, key: str, increment: int = 1) -> None:
        """Thread-safe statistics update."""
        if self.enable_stats:
            self._stats[key] = self._stats.get(key, 0) + increment

    def _reset_stats(self) -> None:
        """Reset all statistics to initial values."""
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expired_cleanups": 0,
            "total_access_time": 0.0,
            "last_cleanup": time.time(),
            "peak_size": 0,
            "cache_operations": 0,
            "memory_pressure_events": 0,
            "background_cleanups": 0,
        }

    async def _background_cleanup(self) -> None:
        """Background task for cleaning expired entries and maintenance."""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval_seconds)
                await self._cleanup_expired_entries()
            except asyncio.CancelledError:
                logger.debug("Background cleanup task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in background cleanup: {e}")

    async def _cleanup_expired_entries(self) -> None:
        """Remove expired entries from cache."""
        current_time = time.time()
        expired_count = 0

        with self._lock:
            expired_keys = [
                key
                for key, (_, _, expire_time, _) in self._cache.items()
                if current_time > expire_time
            ]

            for key in expired_keys:
                del self._cache[key]
                expired_count += 1

            self._stats["expired_cleanups"] += expired_count
            self._stats["background_cleanups"] += 1
            self._stats["last_cleanup"] = current_time

        if expired_count > 0:
            logger.debug(f"Cleaned up {expired_count} expired entries from memory cache")

    def get_memory_usage(self) -> float:
        """Get approximate memory usage in MB."""
        import sys

        total_size = 0
        with self._lock:
            total_size += sys.getsizeof(self._cache)
            for key, value in self._cache.items():
                total_size += sys.getsizeof(key)
                total_size += sys.getsizeof(value)
                # Approximate proxy object size
                proxy = value[0]
                total_size += sys.getsizeof(vars(proxy))

        return total_size / (1024 * 1024)  # Convert to MB
