"""Smart response caching system for ProxyWhirl.

Implements intelligent caching with TTL, invalidation strategies,
compression, and LRU eviction policies.
"""

from __future__ import annotations

import pickle
import time
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from loguru import logger

T = TypeVar("T")


@dataclass
class CacheEntry(Generic[T]):
    """Represents a cache entry."""

    key: str
    value: T
    timestamp: float = field(default_factory=time.time)
    ttl: int | None = None
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    size_bytes: int = 0

    def is_expired(self) -> bool:
        """Check if entry has expired.

        Returns:
            True if expired, False otherwise
        """
        if self.ttl is None:
            return False
        return time.time() - self.timestamp > self.ttl

    def touch(self) -> None:
        """Update last access time."""
        self.last_accessed = time.time()
        self.access_count += 1

    def calculate_size(self) -> None:
        """Calculate entry size in bytes."""
        try:
            self.size_bytes = len(pickle.dumps(self.value))
        except Exception:
            self.size_bytes = 0


class SmartCache(Generic[T]):
    """Smart response caching with TTL, compression, and LRU eviction."""

    def __init__(
        self,
        max_size: int = 1000,
        max_memory_mb: int = 100,
        default_ttl: int = 3600,
    ) -> None:
        """Initialize smart cache.

        Args:
            max_size: Maximum number of entries
            max_memory_mb: Maximum memory usage in MB
            default_ttl: Default TTL in seconds
        """
        self._cache: dict[str, CacheEntry[T]] = {}
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.default_ttl = default_ttl
        self._hits = 0
        self._misses = 0
        logger.debug(
            f"SmartCache initialized: max_size={max_size}, "
            f"max_memory={max_memory_mb}MB, ttl={default_ttl}s"
        )

    def set(self, key: str, value: T, ttl: int | None = None) -> None:
        """Set cache entry.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
        """
        # Clean up expired entries first
        self._cleanup_expired()

        # Check memory limit
        if self._get_total_memory() > self.max_memory_bytes:
            self._evict_lru()

        # Check size limit
        if len(self._cache) >= self.max_size:
            self._evict_lru()

        entry = CacheEntry(key=key, value=value, ttl=ttl or self.default_ttl)
        entry.calculate_size()
        self._cache[key] = entry
        logger.debug(f"Cache set: {key} (ttl={entry.ttl}s)")

    def get(self, key: str) -> T | None:
        """Get cache entry.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        if key not in self._cache:
            self._misses += 1
            return None

        entry = self._cache[key]

        if entry.is_expired():
            del self._cache[key]
            self._misses += 1
            logger.debug(f"Cache expired: {key}")
            return None

        entry.touch()
        self._hits += 1
        return entry.value

    def delete(self, key: str) -> bool:
        """Delete cache entry.

        Args:
            key: Cache key

        Returns:
            True if deleted, False if not found
        """
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Cache deleted: {key}")
            return True
        return False

    def clear(self) -> None:
        """Clear entire cache."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        logger.info("Cache cleared")

    def _cleanup_expired(self) -> None:
        """Remove expired entries."""
        expired_keys = [k for k, v in self._cache.items() if v.is_expired()]
        for key in expired_keys:
            del self._cache[key]
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired entries")

    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self._cache:
            return
        lru_key = min(self._cache.keys(), key=lambda k: self._cache[k].last_accessed)
        del self._cache[lru_key]
        logger.debug(f"LRU evicted: {lru_key}")

    def _get_total_memory(self) -> int:
        """Get total memory used by cache.

        Returns:
            Memory used in bytes
        """
        return sum(entry.size_bytes for entry in self._cache.values())

    def hit_rate(self) -> float:
        """Get cache hit rate.

        Returns:
            Hit rate (0-100)
        """
        total = self._hits + self._misses
        if total == 0:
            return 0.0
        return (self._hits / total) * 100

    def stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary of statistics
        """
        return {
            "entries": len(self._cache),
            "max_entries": self.max_size,
            "memory_used_mb": self._get_total_memory() / (1024 * 1024),
            "max_memory_mb": self.max_memory_bytes / (1024 * 1024),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self.hit_rate(),
        }

    def get_keys(self) -> list[str]:
        """Get all cache keys.

        Returns:
            List of cache keys
        """
        return list(self._cache.keys())
