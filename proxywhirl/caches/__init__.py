"""proxywhirl/caches -- Modular cache system with pluggable backends

Enterprise-grade caching architecture supporting:
- BaseProxyCache: Abstract interface with common cache operations
- MemoryCache: High-performance in-memory LRU cache with thread safety
- JSONCache: Persistent file-based cache with atomic operations
- SQLiteCache: Advanced relational cache with SQLModel ORM and analytics (optional)
- AsyncSQLiteCache: Production-ready async SQLite with connection pooling (optional)

Each backend is optimized for its specific use case while maintaining
a consistent interface through the base class abstraction.

Note: SQLite-based caches require optional dependencies (sqlalchemy, sqlmodel).
If these dependencies are not available, only memory and JSON caches will be supported.
"""

# Always available imports
from .base import BaseProxyCache, CacheFilters, CacheMetrics
from .json import JsonProxyCache
from .memory import MemoryProxyCache

# Optional SQLite imports with graceful fallback
_SQLITE_AVAILABLE = False
_SQLITE_IMPORT_ERROR = None

try:
    from .sqlite import SQLiteProxyCache, AsyncSQLiteProxyCache
    _SQLITE_AVAILABLE = True
except ImportError as e:
    _SQLITE_IMPORT_ERROR = e
    # Create placeholder classes for SQLite caches
    class SQLiteProxyCache:
        def __init__(self, *args, **kwargs):
            raise ImportError(
                f"SQLite cache requires optional dependencies (sqlalchemy, sqlmodel). "
                f"Install with: pip install sqlalchemy sqlmodel. Original error: {_SQLITE_IMPORT_ERROR}"
            )
    
    class AsyncSQLiteProxyCache:
        def __init__(self, *args, **kwargs):
            raise ImportError(
                f"Async SQLite cache requires optional dependencies (sqlalchemy, sqlmodel, aiosqlite). "
                f"Install with: pip install sqlalchemy sqlmodel aiosqlite. Original error: {_SQLITE_IMPORT_ERROR}"
            )

__all__ = [
    # Base classes
    "BaseProxyCache",
    "CacheFilters", 
    "CacheMetrics",
    # Cache implementations (always available)
    "MemoryProxyCache",
    "JsonProxyCache",
    # SQLite implementations (may raise ImportError if dependencies missing)
    "SQLiteProxyCache",
    "AsyncSQLiteProxyCache",
]

def is_sqlite_available() -> bool:
    """Check if SQLite cache backends are available."""
    return _SQLITE_AVAILABLE

def get_sqlite_import_error() -> Exception:
    """Get the import error for SQLite backends, if any."""
    return _SQLITE_IMPORT_ERROR
