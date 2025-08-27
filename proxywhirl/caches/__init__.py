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
from .json import JsonProxyCache
from .memory import MemoryProxyCache
from .sqlite import SQLiteProxyCache, AsyncSQLiteProxyCache

__all__ = [
    # Base classes
    "BaseProxyCache",
    "CacheFilters",
    "CacheMetrics",
    # Cache implementations
    "MemoryProxyCache",
    "JsonProxyCache",
    "SQLiteProxyCache",
    "AsyncSQLiteProxyCache",
]
