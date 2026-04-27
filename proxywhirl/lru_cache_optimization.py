"""LRU cache optimization and tuning."""

from collections import OrderedDict
from typing import Optional, Any, Generic, TypeVar
from dataclasses import dataclass

T = TypeVar("T")


@dataclass
class CacheStats:
    """Cache statistics."""

    hits: int = 0
    misses: int = 0
    evictions: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class OptimizedLRUCache(Generic[T]):
    """Optimized LRU cache with statistics."""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: OrderedDict = OrderedDict()
        self.stats = CacheStats()

    def get(self, key: str) -> Optional[T]:
        """Get from cache."""
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.stats.hits += 1
            return self.cache[key]

        self.stats.misses += 1
        return None

    def put(self, key: str, value: T) -> None:
        """Put into cache."""
        if key in self.cache:
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.max_size:
                # Remove least recently used
                removed_key, _ = self.cache.popitem(last=False)
                self.stats.evictions += 1

        self.cache[key] = value

    def clear(self) -> None:
        """Clear cache."""
        self.cache.clear()

    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        return self.stats

    def get_size(self) -> int:
        """Get current cache size."""
        return len(self.cache)

    def evict_lru(self) -> Optional[T]:
        """Evict least recently used item."""
        if self.cache:
            _, value = self.cache.popitem(last=False)
            self.stats.evictions += 1
            return value
        return None
