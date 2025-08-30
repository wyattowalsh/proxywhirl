"""proxywhirl/caches/db/__init__.py -- SQLite cache module initialization

This module provides a complete SQLite cache implementation broken down into
logical components for better maintainability and code organization.

Modules:
- base: Common utilities and base classes
- models: SQLModel table definitions and utilities
- sync: Synchronous SQLite cache implementation 
- async_impl: Asynchronous SQLite cache implementation
- health: Health monitoring and scoring utilities
- analytics: Analytics and reporting capabilities

Usage:
    from proxywhirl.caches.db import SQLiteProxyCache, AsyncSQLiteProxyCache
    from proxywhirl.caches.db.health import SQLiteHealthMonitor
    from proxywhirl.caches.db.analytics import CacheAnalytics
    from proxywhirl.caches.db.models import ProxyRecord, get_table_models
"""

from .async_impl import AsyncSQLiteProxyCache
from .base import SQLiteBase
from .models import (
    ProxyRecord,
    HealthMetric,
    PerformanceHistory,
    Tag,
    ProxyTagLink,
    CacheMetadata,
    get_table_models,
    get_foreign_key_relationships,
)
from .sync import SQLiteProxyCache

__all__ = [
    "SQLiteProxyCache",
    "AsyncSQLiteProxyCache", 
    "SQLiteBase",
    "ProxyRecord",
    "HealthMetric",
    "PerformanceHistory",
    "Tag",
    "ProxyTagLink",
    "CacheMetadata",
    "get_table_models",
    "get_foreign_key_relationships",
]
