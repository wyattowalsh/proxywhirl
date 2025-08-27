"""proxywhirl/cache.py -- proxy caching functionality with backward compatibility

This module provides backward compatibility for the original ProxyCache interface
while leveraging the new advanced cache system from proxywhirl.caches.

The ProxyCache class now acts as a facade that delegates to the appropriate
backend cache implementation based on the cache type.
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Optional

from loguru import logger

from proxywhirl.caches import (
    BaseProxyCache,
    JsonProxyCache, 
    MemoryProxyCache,
    SQLiteProxyCache,
    is_sqlite_available
)
from proxywhirl.models import CacheType, Proxy


class ProxyCache:
    """
    Backward-compatible proxy cache supporting memory, JSON, and SQLite storage.
    
    This class acts as a facade over the new advanced cache system, providing
    the same interface as the original simple cache while leveraging enhanced
    features like compression, backups, and analytics.
    
    For new code, consider using the advanced cache classes directly from
    proxywhirl.caches for better performance and features.
    """

    def __init__(self, cache_type: CacheType, cache_path: Optional[Path] = None):
        self.cache_type = cache_type
        self.cache_path = cache_path
        
        # Create the appropriate backend cache
        self._backend = self._create_backend_cache(cache_type, cache_path)
        
        logger.info(f"ProxyCache initialized with {cache_type} backend")

    def _create_backend_cache(self, cache_type: CacheType, cache_path: Optional[Path]) -> BaseProxyCache:
        """Create the appropriate backend cache implementation."""
        if cache_type == CacheType.MEMORY:
            return MemoryProxyCache()
        
        elif cache_type == CacheType.JSON:
            if not cache_path:
                raise ValueError("cache_path is required for JSON cache")
            return JsonProxyCache(
                cache_path=cache_path,
                compression=False,  # Keep simple for backward compatibility
                enable_backups=False,
                integrity_checks=False,
            )
        
        elif cache_type == CacheType.SQLITE:
            if not cache_path:
                raise ValueError("cache_path is required for SQLITE cache")
            
            # For now, use legacy SQLite implementation to avoid complex relationship issues
            # TODO: Fix advanced SQLite cache relationship annotations
            logger.info("Using legacy SQLite cache implementation for better compatibility")
            return LegacySQLiteCache(cache_path)
        
        else:
            raise ValueError(f"Unknown cache type: {cache_type}")

    def add_proxies(self, proxies: List[Proxy]) -> None:
        """Add proxies to cache."""
        self._backend.add_proxies_sync(proxies)

    def get_proxies(self) -> List[Proxy]:
        """Get all proxies from cache."""
        return self._backend.get_proxies_sync()

    def update_proxy(self, proxy: Proxy) -> None:
        """Update a proxy in cache."""
        self._backend.update_proxy_sync(proxy)

    def remove_proxy(self, proxy: Proxy) -> None:
        """Remove a proxy from cache."""
        self._backend.remove_proxy_sync(proxy)

    def clear(self) -> None:
        """Clear all proxies from cache."""
        self._backend.clear_sync()


class LegacySQLiteCache(BaseProxyCache):
    """
    Legacy SQLite cache implementation for backward compatibility.
    
    This implementation uses the original sqlite3 approach when advanced
    SQLite features (SQLModel, SQLAlchemy) are not available.
    """
    
    def __init__(self, cache_path: Path):
        super().__init__(CacheType.SQLITE, cache_path)
        self.cache_path = cache_path
        self._db: Optional[sqlite3.Connection] = sqlite3.connect(cache_path)
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database tables."""
        assert self._db is not None
        cur = self._db.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS proxies (
              host TEXT NOT NULL,
              port INTEGER NOT NULL,
              data TEXT NOT NULL,
              PRIMARY KEY(host, port)
            )
            """
        )
        self._db.commit()
    
    async def add_proxies(self, proxies: List[Proxy]) -> None:
        """Add proxies to cache (async)."""
        if self._db:
            self._insert_many(proxies)
    
    async def get_proxies(self, filters=None) -> List[Proxy]:
        """Get proxies from cache (async)."""
        if self._db:
            return self._load_from_db()
        return []
    
    async def update_proxy(self, proxy: Proxy) -> None:
        """Update proxy in cache (async)."""
        if self._db:
            self._upsert(proxy)
    
    async def remove_proxy(self, proxy: Proxy) -> None:
        """Remove proxy from cache (async)."""
        if self._db:
            cur = self._db.cursor()
            cur.execute(
                "DELETE FROM proxies WHERE host=? AND port=?",
                (proxy.host, proxy.port),
            )
            self._db.commit()
    
    async def clear(self) -> None:
        """Clear cache (async)."""
        if self._db:
            cur = self._db.cursor()
            cur.execute("DELETE FROM proxies")
            self._db.commit()
    
    async def get_health_metrics(self):
        """Get health metrics (async)."""
        from proxywhirl.caches.base import CacheMetrics
        proxies = await self.get_proxies()
        return CacheMetrics(
            total_proxies=len(proxies),
            healthy_proxies=len(proxies),  # Assume all are healthy for legacy
        )
    
    def _upsert(self, proxy: Proxy) -> None:
        """Update or insert proxy."""
        assert self._db is not None
        cur = self._db.cursor()
        cur.execute("DELETE FROM proxies WHERE host = ?", (proxy.host,))
        data = json.dumps(proxy.model_dump(mode="json"), default=str)
        cur.execute(
            "INSERT INTO proxies(host, port, data) VALUES (?, ?, ?)",
            (proxy.host, proxy.port, data),
        )
        self._db.commit()

    def _insert_many(self, proxies: List[Proxy]) -> None:
        """Insert multiple proxies."""
        assert self._db is not None
        rows: List[tuple[str, int, str]] = []
        for p in proxies:
            rows.append(
                (
                    p.host,
                    p.port,
                    json.dumps(p.model_dump(mode="json"), default=str),
                )
            )
        cur = self._db.cursor()
        cur.executemany(
            ("INSERT OR REPLACE INTO proxies(host, port, data) VALUES (?, ?, ?)"),
            rows,
        )
        self._db.commit()

    def _load_from_db(self) -> List[Proxy]:
        """Load proxies from database."""
        assert self._db is not None
        cur = self._db.cursor()
        cur.execute("SELECT data FROM proxies")
        rows = cur.fetchall()
        result: List[Proxy] = []
        for (data_str,) in rows:
            try:
                data = json.loads(data_str)
                result.append(Proxy(**data))
            except Exception as e:  # pragma: no cover - defensive
                logger.debug(f"Failed to parse proxy row: {e}")
        return result
