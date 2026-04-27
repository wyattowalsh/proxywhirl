"""Cache optimization and management."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from loguru import logger


class CachePolicy(str, Enum):
    """Cache policies."""

    LRU = "lru"  # Least recently used
    LFU = "lfu"  # Least frequently used
    FIFO = "fifo"  # First in, first out
    TTL = "ttl"  # Time-to-live


@dataclass
class CacheStatistics:
    """Cache statistics."""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_requests: int = 0

    @property
    def hit_rate(self) -> float:
        """Get hit rate as percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.hits / self.total_requests) * 100


@dataclass
class CacheEntry:
    """Cache entry."""

    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    ttl_seconds: int | None = None

    def is_expired(self) -> bool:
        """Check if entry is expired.

        Returns:
            True if expired
        """
        if self.ttl_seconds is None:
            return False

        elapsed = (datetime.now() - self.created_at).total_seconds()
        return elapsed > self.ttl_seconds


class OptimizedCache:
    """Optimized cache with configurable policy."""

    def __init__(self, max_size: int = 1000, policy: CachePolicy = CachePolicy.LRU):
        """Initialize cache.

        Args:
            max_size: Maximum entries
            policy: Eviction policy
        """
        self.max_size = max_size
        self.policy = policy
        self._cache: dict[str, CacheEntry] = {}
        self._stats = CacheStatistics()

    def get(self, key: str) -> Any | None:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        entry = self._cache.get(key)

        if entry is None:
            self._stats.misses += 1
            self._stats.total_requests += 1
            return None

        # Check expiration
        if entry.is_expired():
            del self._cache[key]
            self._stats.misses += 1
            self._stats.total_requests += 1
            return None

        # Update statistics
        entry.access_count += 1
        entry.last_accessed = datetime.now()
        self._stats.hits += 1
        self._stats.total_requests += 1

        return entry.value

    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time-to-live in seconds
        """
        entry = CacheEntry(
            key=key,
            value=value,
            ttl_seconds=ttl_seconds,
        )

        self._cache[key] = entry

        # Enforce size limit
        if len(self._cache) > self.max_size:
            self._evict()

    def _evict(self) -> None:
        """Evict entry based on policy."""
        if not self._cache:
            return

        key_to_remove = None

        if self.policy == CachePolicy.LRU:
            # Remove least recently used
            key_to_remove = min(
                self._cache.keys(),
                key=lambda k: self._cache[k].last_accessed,
            )
        elif self.policy == CachePolicy.LFU:
            # Remove least frequently used
            key_to_remove = min(
                self._cache.keys(),
                key=lambda k: self._cache[k].access_count,
            )
        elif self.policy == CachePolicy.FIFO:
            # Remove oldest entry
            key_to_remove = min(
                self._cache.keys(),
                key=lambda k: self._cache[k].created_at,
            )

        if key_to_remove:
            del self._cache[key_to_remove]
            self._stats.evictions += 1

    def clear(self) -> None:
        """Clear cache."""
        self._cache.clear()
        logger.info("Cache cleared")

    def cleanup_expired(self) -> int:
        """Remove expired entries.

        Returns:
            Number of entries removed
        """
        expired_keys = [key for key, entry in self._cache.items() if entry.is_expired()]

        for key in expired_keys:
            del self._cache[key]

        return len(expired_keys)

    def get_statistics(self) -> CacheStatistics:
        """Get cache statistics.

        Returns:
            Cache statistics
        """
        return self._stats

    def get_size(self) -> int:
        """Get current cache size.

        Returns:
            Number of entries
        """
        return len(self._cache)


class CacheWarmup:
    """Pre-warms cache with data."""

    def __init__(self, cache: OptimizedCache):
        """Initialize cache warmup.

        Args:
            cache: OptimizedCache instance
        """
        self.cache = cache

    def warmup_from_dict(self, data: dict[str, Any], ttl_seconds: int | None = None) -> None:
        """Warm up cache from dict.

        Args:
            data: Dict of key-value pairs
            ttl_seconds: TTL for all entries
        """
        for key, value in data.items():
            self.cache.set(key, value, ttl_seconds)

        logger.info(f"Warmed up cache with {len(data)} entries")

    def warmup_from_callable(
        self,
        loader: callable,
        keys: list[str],
        ttl_seconds: int | None = None,
    ) -> None:
        """Warm up cache by calling loader function.

        Args:
            loader: Function that loads value for key
            keys: Keys to load
            ttl_seconds: TTL for all entries
        """
        loaded = 0

        for key in keys:
            try:
                value = loader(key)
                self.cache.set(key, value, ttl_seconds)
                loaded += 1
            except Exception as e:
                logger.warning(f"Failed to load key {key}: {e}")

        logger.info(f"Warmed up cache with {loaded}/{len(keys)} entries")
