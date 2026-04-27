"""Enhanced response caching with smart cache control."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Any, Optional

from loguru import logger


@dataclass
class CacheEntry:
    """Cache entry with metadata."""

    key: str
    value: Any
    created_at: float
    ttl_seconds: int
    etag: Optional[str] = None
    cache_control: Optional[str] = None
    access_count: int = 0
    last_accessed: float = 0.0

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        return time.time() - self.created_at > self.ttl_seconds

    def touch(self) -> None:
        """Update access statistics."""
        self.access_count += 1
        self.last_accessed = time.time()


class SmartCacheManager:
    """
    Enhanced cache manager with smart cache control.

    Features:
    - ETag validation
    - Cache-Control header support
    - Smart TTL based on content type
    - Access tracking for eviction
    """

    def __init__(self, max_entries: int = 1000):
        """
        Initialize smart cache manager.

        Args:
            max_entries: Maximum cache entries
        """
        self.cache: dict[str, CacheEntry] = {}
        self.max_entries = max_entries
        self.etag_index: dict[str, str] = {}  # Maps etag -> cache key

    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int = 300,
        etag: Optional[str] = None,
        cache_control: Optional[str] = None,
    ) -> None:
        """
        Set cache entry with optional ETag and cache-control.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds
            etag: Optional ETag for validation
            cache_control: Optional Cache-Control header value
        """
        # Evict if at capacity
        if len(self.cache) >= self.max_entries:
            self._evict_lru()

        # Compute ETag if not provided
        if etag is None:
            etag = self._compute_etag(value)

        entry = CacheEntry(
            key=key,
            value=value,
            created_at=time.time(),
            ttl_seconds=ttl_seconds,
            etag=etag,
            cache_control=cache_control,
        )

        self.cache[key] = entry
        if etag:
            self.etag_index[etag] = key

        logger.debug(f"Cached {key} (TTL: {ttl_seconds}s, ETag: {etag})")

    def get(self, key: str) -> Optional[Any]:
        """
        Get cache entry.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        if key not in self.cache:
            return None

        entry = self.cache[key]

        if entry.is_expired():
            del self.cache[key]
            if entry.etag:
                del self.etag_index[entry.etag]
            logger.debug(f"Cache expired: {key}")
            return None

        entry.touch()
        return entry.value

    def validate_etag(self, key: str, etag: str) -> bool:
        """
        Validate ETag for a cached entry.

        Args:
            key: Cache key
            etag: ETag to validate against

        Returns:
            True if ETag matches and entry is valid
        """
        if key not in self.cache:
            return False

        entry = self.cache[key]

        if entry.is_expired():
            del self.cache[key]
            return False

        return entry.etag == etag

    def get_cache_control(self, key: str) -> Optional[str]:
        """
        Get Cache-Control header for entry.

        Args:
            key: Cache key

        Returns:
            Cache-Control header or None
        """
        if key not in self.cache:
            return None

        entry = self.cache[key]

        if entry.is_expired():
            del self.cache[key]
            return None

        return entry.cache_control

    def delete(self, key: str) -> None:
        """
        Delete cache entry.

        Args:
            key: Cache key
        """
        if key in self.cache:
            entry = self.cache[key]
            del self.cache[key]
            if entry.etag:
                del self.etag_index[entry.etag]
            logger.debug(f"Deleted cache: {key}")

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.etag_index.clear()
        logger.debug("Cleared all cache entries")

    def cleanup_expired(self) -> int:
        """
        Remove all expired entries.

        Returns:
            Number of entries removed
        """
        expired_keys = [key for key, entry in self.cache.items() if entry.is_expired()]

        for key in expired_keys:
            self.delete(key)

        if expired_keys:
            logger.debug(f"Cleaned {len(expired_keys)} expired cache entries")

        return len(expired_keys)

    def get_stats(self) -> dict[str, int | float]:
        """
        Get cache statistics.

        Returns:
            Dictionary with stats
        """
        total_accesses = sum(entry.access_count for entry in self.cache.values())

        return {
            "entries": len(self.cache),
            "max_entries": self.max_entries,
            "utilization_percent": (len(self.cache) / self.max_entries * 100)
            if self.max_entries
            else 0.0,
            "total_accesses": total_accesses,
            "avg_accesses": (total_accesses / len(self.cache)) if self.cache else 0.0,
        }

    def _compute_etag(self, value: Any) -> str:
        """
        Compute ETag for a value.

        Args:
            value: Value to compute ETag for

        Returns:
            ETag string (first 16 chars of SHA256 hash)
        """
        value_str = str(value)
        return hashlib.sha256(value_str.encode()).hexdigest()[:16]

    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self.cache:
            return

        # Find LRU entry
        lru_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k].last_accessed,
        )

        self.delete(lru_key)
        logger.debug(f"Evicted LRU cache entry: {lru_key}")
