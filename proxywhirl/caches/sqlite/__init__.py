"""SQLite cache package exports."""

from .async_impl import AsyncSQLiteProxyCache

# For backwards compatibility, alias AsyncSQLiteProxyCache as SQLiteProxyCache
SQLiteProxyCache = AsyncSQLiteProxyCache

__all__ = [
    "AsyncSQLiteProxyCache",
    "SQLiteProxyCache", 
]