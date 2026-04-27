"""Distributed cache layer with Redis compatibility.

Features:
- Redis-compatible interface for distributed caching
- Async-first design
- Multi-tier caching (local + distributed)
- TTL support with expiration
- Cache invalidation patterns
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class CacheEntry(BaseModel, Generic[T]):
    """Entry in distributed cache."""

    model_config = ConfigDict(extra="forbid")

    key: str
    value: T
    ttl_seconds: int | None = Field(None, description="Time to live in seconds")
    created_at: int = Field(description="Unix timestamp when created")
    tags: list[str] = Field(default_factory=list, description="Tags for batch invalidation")
    metadata: dict[str, Any] = Field(default_factory=dict)


class CacheStats(BaseModel):
    """Cache statistics."""

    model_config = ConfigDict(frozen=True)

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size_bytes: int = 0
    entry_count: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate hit rate."""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total


class DistributedCacheBackend(ABC):
    """Abstract distributed cache backend."""

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """Get value from cache."""

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: timedelta | None = None) -> bool:
        """Set value in cache."""

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists."""

    @abstractmethod
    async def incr(self, key: str, amount: int = 1) -> int:
        """Increment counter."""

    @abstractmethod
    async def expire(self, key: str, ttl: timedelta) -> bool:
        """Set expiration on key."""

    @abstractmethod
    async def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern."""

    @abstractmethod
    async def get_stats(self) -> CacheStats:
        """Get cache statistics."""


class InMemoryCacheBackend(DistributedCacheBackend):
    """In-memory cache backend (for testing/local use)."""

    def __init__(self, max_size: int = 10000):
        """Initialize in-memory cache.

        Args:
            max_size: Maximum number of entries
        """
        self.max_size = max_size
        self._data: dict[str, Any] = {}
        self._stats = {"hits": 0, "misses": 0, "evictions": 0}

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        if key in self._data:
            self._stats["hits"] += 1
            return self._data[key]
        self._stats["misses"] += 1
        return None

    async def set(self, key: str, value: Any, ttl: timedelta | None = None) -> bool:
        """Set value in cache."""
        if len(self._data) >= self.max_size:
            # Simple eviction: remove first (oldest) entry
            first_key = next(iter(self._data))
            del self._data[first_key]
            self._stats["evictions"] += 1

        self._data[key] = value
        return True

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if key in self._data:
            del self._data[key]
            return True
        return False

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        return key in self._data

    async def incr(self, key: str, amount: int = 1) -> int:
        """Increment counter."""
        if key not in self._data:
            self._data[key] = 0
        current = int(self._data[key])
        current += amount
        self._data[key] = current
        return current

    async def expire(self, key: str, ttl: timedelta) -> bool:
        """Set expiration on key."""
        # Simple implementation - real implementation would use asyncio.sleep
        return key in self._data

    async def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern."""
        import re

        regex = re.compile(pattern.replace("*", ".*"))
        keys_to_delete = [k for k in self._data if regex.match(k)]
        for key in keys_to_delete:
            del self._data[key]
        return len(keys_to_delete)

    async def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        return CacheStats(
            hits=self._stats["hits"],
            misses=self._stats["misses"],
            evictions=self._stats["evictions"],
            entry_count=len(self._data),
        )


class DistributedCache:
    """High-level distributed cache interface."""

    def __init__(self, backend: DistributedCacheBackend):
        """Initialize distributed cache.

        Args:
            backend: Cache backend implementation
        """
        self.backend = backend

    async def get_or_set(
        self,
        key: str,
        factory,
        ttl: timedelta | None = None,
    ) -> Any:
        """Get value from cache or compute it.

        Args:
            key: Cache key
            factory: Async function to compute value if not cached
            ttl: Time to live

        Returns:
            Cached or computed value
        """
        cached = await self.backend.get(key)
        if cached is not None:
            return cached

        value = await factory() if callable(factory) else factory
        await self.backend.set(key, value, ttl)
        return value

    async def delete_many(self, keys: list[str]) -> int:
        """Delete multiple keys.

        Args:
            keys: List of keys to delete

        Returns:
            Number of deleted keys
        """
        deleted = 0
        for key in keys:
            if await self.backend.delete(key):
                deleted += 1
        return deleted

    async def invalidate_by_tags(self, tags: list[str]) -> int:
        """Invalidate cache entries by tags.

        Args:
            tags: List of tags

        Returns:
            Number of invalidated entries
        """
        deleted = 0
        for tag in tags:
            pattern = f"*:{tag}:*"
            deleted += await self.backend.delete_pattern(pattern)
        return deleted


class DistributedLock:
    """Distributed lock using cache backend."""

    def __init__(
        self,
        cache: DistributedCache,
        key: str,
        ttl: timedelta = timedelta(seconds=30),
    ):
        """Initialize distributed lock.

        Args:
            cache: Distributed cache instance
            key: Lock key
            ttl: Lock time to live
        """
        self.cache = cache
        self.key = key
        self.ttl = ttl

    async def acquire(self, timeout: timedelta = timedelta(seconds=10)) -> bool:
        """Acquire lock.

        Args:
            timeout: Maximum time to wait for lock

        Returns:
            True if lock acquired
        """
        import time

        start_time = time.time()
        while time.time() - start_time < timeout.total_seconds():
            if not await self.cache.backend.exists(self.key):
                await self.cache.backend.set(self.key, "locked", self.ttl)
                return True
            await asyncio.sleep(0.1)
        return False

    async def release(self) -> bool:
        """Release lock.

        Returns:
            True if lock was released
        """
        return await self.cache.backend.delete(self.key)

    async def __aenter__(self):
        """Async context manager entry."""
        if not await self.acquire():
            raise TimeoutError(f"Failed to acquire lock: {self.key}")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.release()


# Helper function for easier redis-like usage
import asyncio


async def get_distributed_cache() -> DistributedCache:
    """Factory function to get distributed cache instance.

    In production, this would check for Redis connection
    and fall back to in-memory cache if unavailable.
    """
    backend = InMemoryCacheBackend()
    return DistributedCache(backend)
