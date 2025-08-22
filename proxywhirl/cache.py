"""proxywhirl/cache.py -- proxy caching functionality"""

import json
import sqlite3
from pathlib import Path
from typing import List, Optional

from loguru import logger

from proxywhirl.models import CacheType, Proxy


class ProxyCache:
    """Multi-backend proxy cache supporting memory, JSON, and SQLite storage."""

    def __init__(self, cache_type: CacheType, cache_path: Optional[Path] = None):
        self.cache_type = cache_type
        self.cache_path = cache_path
        self._proxies: List[Proxy] = []
        self._db: Optional[sqlite3.Connection] = None
        if self.cache_type == CacheType.SQLITE:
            if not self.cache_path:
                raise ValueError("cache_path is required for SQLITE cache")
            self._db = sqlite3.connect(self.cache_path)
            self._init_db()

    def add_proxies(self, proxies: List[Proxy]) -> None:
        """Add proxies to cache."""
        if self.cache_type == CacheType.SQLITE and self._db:
            self._insert_many(proxies)
        else:
            self._proxies.extend(proxies)
            if self.cache_type == CacheType.JSON and self.cache_path:
                self._save_to_json()

    def get_proxies(self) -> List[Proxy]:
        """Get all proxies from cache."""
        if self.cache_type == CacheType.SQLITE and self._db:
            return self._load_from_db()
        if self.cache_type == CacheType.JSON and self.cache_path:
            self._load_from_json()
        return self._proxies.copy()

    def update_proxy(self, proxy: Proxy) -> None:
        """Update a proxy in cache."""
        if self.cache_type == CacheType.SQLITE and self._db:
            self._upsert(proxy)
        else:
            for i, cached_proxy in enumerate(self._proxies):
                if cached_proxy.host == proxy.host and cached_proxy.port == proxy.port:
                    self._proxies[i] = proxy
                    break
            if self.cache_type == CacheType.JSON and self.cache_path:
                self._save_to_json()

    def remove_proxy(self, proxy: Proxy) -> None:
        """Remove a proxy from cache."""
        if self.cache_type == CacheType.SQLITE and self._db:
            cur = self._db.cursor()
            cur.execute(
                "DELETE FROM proxies WHERE host=? AND port=?",
                (proxy.host, proxy.port),
            )
            self._db.commit()
        else:
            self._proxies = [
                p for p in self._proxies if not (p.host == proxy.host and p.port == proxy.port)
            ]
            if self.cache_type == CacheType.JSON and self.cache_path:
                self._save_to_json()

    def clear(self) -> None:
        """Clear all proxies from cache."""
        if self.cache_type == CacheType.SQLITE and self._db:
            cur = self._db.cursor()
            cur.execute("DELETE FROM proxies")
            self._db.commit()
        else:
            self._proxies.clear()
            if self.cache_type == CacheType.JSON and self.cache_path:
                self._save_to_json()

    def _save_to_json(self) -> None:
        """Save proxies to JSON file."""
        if not self.cache_path:
            return
        try:
            data = [proxy.model_dump() for proxy in self._proxies]
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save cache to {self.cache_path}: {e}")

    def _load_from_json(self) -> None:
        """Load proxies from JSON file."""
        if not self.cache_path or not self.cache_path.exists():
            return
        try:
            with open(self.cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._proxies = [Proxy(**item) for item in data]
        except Exception as e:
            logger.error(f"Failed to load cache from {self.cache_path}: {e}")

    # --- SQLite helpers ---
    def _init_db(self) -> None:
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

    def _upsert(self, proxy: Proxy) -> None:
        assert self._db is not None
        cur = self._db.cursor()
        # For updates, we need to handle the case where port might have changed
        # Delete any existing records with the same host first
        cur.execute("DELETE FROM proxies WHERE host = ?", (proxy.host,))

        data = json.dumps(proxy.model_dump(mode="json"), default=str)
        cur.execute(
            "INSERT INTO proxies(host, port, data) VALUES (?, ?, ?)",
            (proxy.host, proxy.port, data),
        )
        self._db.commit()

    def _insert_many(self, proxies: List[Proxy]) -> None:
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
