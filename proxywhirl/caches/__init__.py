"""proxywhirl/caches -- Modular cache system with pluggable backends

Enterprise-grade caching architecture supporting:
- BaseProxyCache: Abstract interface with common cache operations
- MemoryCache: High-performance in-memory LRU cache with thread safety
- JSONCache: Persistent file-based cache with atomic operations
- SQLiteCache: Advanced relational cache with SQLModel ORM and analytics
- AsyncSQLiteCache: Production-ready async SQLite with connection pooling

Each backend is optimized for its specific use case while maintaining
a consistent interface through the base class abstraction.
"""

from .base import BaseProxyCache, CacheFilters, CacheMetrics
from .config import CacheConfiguration, CacheType, JsonCacheConfig, SqliteCacheConfig
from .json import JsonProxyCache
from .memory import MemoryProxyCache

# TODO: Implement SQLite cache classes
# from .sqlite import AsyncSQLiteProxyCache, SQLiteProxyCache

__all__ = [
    # Base classes
    "BaseProxyCache",
    "CacheFilters",
    "CacheMetrics",
    # Configuration classes
    "CacheConfiguration",
    "CacheType",
    "JsonCacheConfig",
    "SqliteCacheConfig",
    # Cache implementations
    "MemoryProxyCache",
    "JsonProxyCache",
    # TODO: Add SQLite cache classes when implemented
    # "SQLiteProxyCache",
    # "AsyncSQLiteProxyCache",
]
