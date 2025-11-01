"""
Cache tier implementations for multi-tier caching strategy.

Defines:
- CacheTier: Abstract base class for cache tier implementations
- MemoryCacheTier: L1 in-memory cache using OrderedDict
- FileCacheTier: L2 JSONL file cache with encryption and file locking
- SQLiteCacheTier: L3 database cache with full persistence
"""

import json
import sqlite3
from abc import ABC, abstractmethod
from collections import OrderedDict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

import portalocker

from proxywhirl.cache_crypto import CredentialEncryptor
from proxywhirl.cache_models import CacheEntry, CacheTierConfig

__all__ = [
    "TierType",
    "CacheTier",
    "MemoryCacheTier",
    "FileCacheTier",
    "SQLiteCacheTier",
]


class TierType(str, Enum):
    """Cache tier types."""

    L1_MEMORY = "l1_memory"
    L2_FILE = "l2_file"
    L3_SQLITE = "l3_sqlite"


class CacheTier(ABC):
    """
    Abstract base class for cache tier implementations.

    Defines the interface that all cache tiers (L1, L2, L3) must implement,
    including graceful degradation on repeated failures.

    Attributes:
        config: Configuration for this tier
        tier_type: Type of tier (L1/L2/L3)
        enabled: Whether tier is operational
        failure_count: Consecutive failures for degradation tracking
        failure_threshold: Failures before auto-disabling tier
    """

    def __init__(self, config: CacheTierConfig, tier_type: TierType) -> None:
        """Initialize cache tier with configuration.

        Args:
            config: Configuration for this tier
            tier_type: Type of tier (L1/L2/L3)
        """
        self.config = config
        self.tier_type = tier_type
        self.enabled = config.enabled
        self.failure_count = 0
        self.failure_threshold = 3

    @abstractmethod
    def get(self, key: str) -> Optional[CacheEntry]:
        """Retrieve entry by key, None if not found or expired.

        Args:
            key: Cache key to lookup

        Returns:
            CacheEntry if found and valid, None otherwise
        """
        pass

    @abstractmethod
    def put(self, key: str, entry: CacheEntry) -> bool:
        """Store entry, return True if successful.

        Args:
            key: Cache key for entry
            entry: CacheEntry to store

        Returns:
            True if stored successfully, False otherwise
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Remove entry by key, return True if existed.

        Args:
            key: Cache key to delete

        Returns:
            True if entry existed and was deleted, False if not found
        """
        pass

    @abstractmethod
    def clear(self) -> int:
        """Clear all entries, return count of removed entries.

        Returns:
            Number of entries removed
        """
        pass

    @abstractmethod
    def size(self) -> int:
        """Return current number of entries.

        Returns:
            Number of entries in tier
        """
        pass

    @abstractmethod
    def keys(self) -> list[str]:
        """Return list of all keys.

        Returns:
            List of cache keys
        """
        pass

    def handle_failure(self, error: Exception) -> None:
        """Handle tier operation failure for graceful degradation.

        Increments failure count and disables tier if threshold exceeded.
        Called by implementations when operations fail.

        Args:
            error: Exception that occurred
        """
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.enabled = False
            # Log degradation (implementations should log specific details)

    def reset_failures(self) -> None:
        """Reset failure count on successful operation.

        Re-enables tier if previously disabled and resets failure counter.
        Implementations should call this after successful operations.
        """
        self.failure_count = 0
        if not self.enabled:
            self.enabled = True
            # Log recovery (implementations should log specific details)


from threading import RLock

class MemoryCacheTier(CacheTier):
    """L1 in-memory cache using OrderedDict for LRU tracking.

    Provides O(1) lookups with automatic LRU eviction when max_entries exceeded.
    """

    def __init__(self, config: CacheTierConfig, tier_type: TierType) -> None:
        """Initialize memory cache with LRU tracking."""
        super().__init__(config, tier_type)
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = RLock()

    def get(self, key: str) -> Optional[CacheEntry]:
        """Retrieve entry, moving to end for LRU."""
        with self._lock:
            if key in self._cache:
                # Move to end (most recently used)
                self._cache.move_to_end(key)
                return self._cache[key]
            return None

    def put(self, key: str, entry: CacheEntry) -> bool:
        """Store entry with LRU eviction."""
        with self._lock:
            try:
                # Update existing or add new
                if key in self._cache:
                    del self._cache[key]
                self._cache[key] = entry

                # Evict LRU if over capacity
                if self.config.max_entries and len(self._cache) > self.config.max_entries:
                    self._cache.popitem(last=False)  # Remove oldest (FIFO end)

                self.reset_failures()
                return True
            except Exception as e:
                self.handle_failure(e)
                return False

    def delete(self, key: str) -> bool:
        """Remove entry by key."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> int:
        """Clear all entries."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count

    def size(self) -> int:
        """Return current number of entries."""
        with self._lock:
            return len(self._cache)

    def keys(self) -> list[str]:
        """Return list of all keys."""
        with self._lock:
            return list(self._cache.keys())



class FileCacheTier(CacheTier):
    """L2 JSONL file cache with encryption and file locking.

    Uses portalocker for safe concurrent access and sharding by key prefix.
    """

    def __init__(
        self,
        config: CacheTierConfig,
        tier_type: TierType,
        cache_dir: Path,
        encryptor: Optional[CredentialEncryptor] = None,
    ) -> None:
        """Initialize file cache with directory."""
        super().__init__(config, tier_type)
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.encryptor = encryptor or CredentialEncryptor()
        self._lock = RLock()

    def _get_shard_path(self, key: str) -> Path:
        """Get shard file path for key (simple: first 2 chars)."""
        shard = key[:2] if len(key) >= 2 else "00"
        return self.cache_dir / f"shard_{shard}.jsonl"

    def get(self, key: str) -> Optional[CacheEntry]:
        """Retrieve entry from JSONL file."""
        with self._lock:
            shard_path = self._get_shard_path(key)
            if not shard_path.exists():
                return None

            try:
                with portalocker.Lock(shard_path, "r", timeout=5) as f:
                    for line in f:
                        data = json.loads(line)
                        if data.get("key") == key:
                            # Decrypt credentials
                            if data.get("username_encrypted"):
                                data["username"] = self.encryptor.decrypt(
                                    bytes.fromhex(data["username_encrypted"])
                                )
                            if data.get("password_encrypted"):
                                data["password"] = self.encryptor.decrypt(
                                    bytes.fromhex(data["password_encrypted"])
                                )
                            # Remove encrypted fields
                            data.pop("username_encrypted", None)
                            data.pop("password_encrypted", None)
                            # Parse timestamps
                            for field in ["fetch_time", "last_accessed", "expires_at"]:
                                if field in data:
                                    data[field] = datetime.fromisoformat(data[field])
                            return CacheEntry(**data)
                return None
            except Exception as e:
                self.handle_failure(e)
                return None

    def put(self, key: str, entry: CacheEntry) -> bool:
        """Store entry in JSONL file with encryption."""
        with self._lock:
            shard_path = self._get_shard_path(key)

            try:
                # Read existing entries
                entries = []
                if shard_path.exists():
                    with portalocker.Lock(shard_path, "r", timeout=5) as f:
                        entries = [json.loads(line) for line in f if line.strip()]

                # Remove existing entry with same key
                entries = [e for e in entries if e.get("key") != key]

                # Prepare new entry with encryption
                data = entry.model_dump(mode="json")
                if entry.username:
                    encrypted_user = self.encryptor.encrypt(entry.username)
                    data["username_encrypted"] = encrypted_user.hex()
                    data.pop("username", None)
                if entry.password:
                    encrypted_pass = self.encryptor.encrypt(entry.password)
                    data["password_encrypted"] = encrypted_pass.hex()
                    data.pop("password", None)

                entries.append(data)

                # Write all entries
                with portalocker.Lock(shard_path, "w", timeout=5) as f:
                    for e in entries:
                        f.write(json.dumps(e) + "\n")

                self.reset_failures()
                return True
            except Exception as e:
                self.handle_failure(e)
                return False

    def delete(self, key: str) -> bool:
        """Remove entry from JSONL file."""
        with self._lock:
            shard_path = self._get_shard_path(key)
            if not shard_path.exists():
                return False

            try:
                # Read all entries except target
                with portalocker.Lock(shard_path, "r", timeout=5) as f:
                    entries = [
                        json.loads(line)
                        for line in f
                        if line.strip() and json.loads(line).get("key") != key
                    ]

                # Rewrite file
                with portalocker.Lock(shard_path, "w", timeout=5) as f:
                    for e in entries:
                        f.write(json.dumps(e) + "\n")

                return True
            except Exception as e:
                self.handle_failure(e)
                return False

    def clear(self) -> int:
        """Clear all entries."""
        with self._lock:
            count = 0
            for shard_file in self.cache_dir.glob("shard_*.jsonl"):
                try:
                    with portalocker.Lock(shard_file, "r", timeout=5) as f:
                        count += sum(1 for line in f if line.strip())
                    shard_file.unlink()
                except Exception:
                    pass
            return count

    def size(self) -> int:
        """Return current number of entries."""
        with self._lock:
            count = 0
            for shard_file in self.cache_dir.glob("shard_*.jsonl"):
                try:
                    with portalocker.Lock(shard_file, "r", timeout=5) as f:
                        count += sum(1 for line in f if line.strip())
                except Exception:
                    pass
            return count

    def keys(self) -> list[str]:
        """Return list of all keys."""
        with self._lock:
            all_keys = []
            for shard_file in self.cache_dir.glob("shard_*.jsonl"):
                try:
                    with portalocker.Lock(shard_file, "r", timeout=5) as f:
                        for line in f:
                            if line.strip():
                                data = json.loads(line)
                                all_keys.append(data["key"])
                except Exception:
                    pass
            return all_keys




class SQLiteCacheTier(CacheTier):
    """L3 SQLite database cache with encrypted credentials.

    Provides durable persistence with SQL indexing for fast lookups.
    """

    def __init__(
        self,
        config: CacheTierConfig,
        tier_type: TierType,
        db_path: Path,
        encryptor: Optional[CredentialEncryptor] = None,
    ) -> None:
        """Initialize SQLite cache."""
        super().__init__(config, tier_type)
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.encryptor = encryptor or CredentialEncryptor()
        self._lock = RLock()
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with self._lock:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    proxy_url TEXT NOT NULL,
                    username_encrypted BLOB,
                    password_encrypted BLOB,
                    source TEXT NOT NULL,
                    fetch_time REAL NOT NULL,
                    last_accessed REAL NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    ttl_seconds INTEGER NOT NULL,
                    expires_at REAL NOT NULL,
                    health_status TEXT DEFAULT 'unknown',
                    failure_count INTEGER DEFAULT 0,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            self._conn.execute("CREATE INDEX IF NOT EXISTS idx_expires_at ON cache_entries(expires_at)")
            self._conn.execute("CREATE INDEX IF NOT EXISTS idx_source ON cache_entries(source)")
            self._conn.execute("CREATE INDEX IF NOT EXISTS idx_health_status ON cache_entries(health_status)")
            self._conn.execute("CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache_entries(last_accessed)")
            self._conn.commit()

    def get(self, key: str) -> Optional[CacheEntry]:
        """Retrieve entry from database."""
        with self._lock:
            try:
                cursor = self._conn.execute(
                    "SELECT * FROM cache_entries WHERE key = ?", (key,)
                )
                row = cursor.fetchone()

                if not row:
                    return None

                # Map row to dict
                columns = [
                    "key", "proxy_url", "username_encrypted", "password_encrypted",
                    "source", "fetch_time", "last_accessed", "access_count",
                    "ttl_seconds", "expires_at", "health_status", "failure_count",
                    "created_at", "updated_at"
                ]
                data = dict(zip(columns, row))

                # Decrypt credentials
                if data["username_encrypted"]:
                    data["username"] = self.encryptor.decrypt(data["username_encrypted"])
                if data["password_encrypted"]:
                    data["password"] = self.encryptor.decrypt(data["password_encrypted"])

                # Convert timestamps
                for field in ["fetch_time", "last_accessed", "expires_at", "created_at", "updated_at"]:
                    data[field] = datetime.fromtimestamp(data[field], tz=timezone.utc)

                # Remove encrypted fields
                data.pop("username_encrypted")
                data.pop("password_encrypted")

                self.reset_failures()
                return CacheEntry(**data)
            except Exception as e:
                self.handle_failure(e)
                return None

    def put(self, key: str, entry: CacheEntry) -> bool:
        """Store entry in database."""
        with self._lock:
            try:
                # Encrypt credentials
                username_encrypted = None
                if entry.username:
                    username_encrypted = self.encryptor.encrypt(entry.username)
                password_encrypted = None
                if entry.password:
                    password_encrypted = self.encryptor.encrypt(entry.password)

                # Convert timestamps to UNIX epoch
                now = datetime.now(timezone.utc).timestamp()

                self._conn.execute("""
                    INSERT OR REPLACE INTO cache_entries (
                        key, proxy_url, username_encrypted, password_encrypted,
                        source, fetch_time, last_accessed, access_count,
                        ttl_seconds, expires_at, health_status, failure_count,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.key,
                    entry.proxy_url,
                    username_encrypted,
                    password_encrypted,
                    entry.source,
                    entry.fetch_time.timestamp(),
                    entry.last_accessed.timestamp(),
                    entry.access_count,
                    entry.ttl_seconds,
                    entry.expires_at.timestamp(),
                    entry.health_status.value,
                    entry.failure_count,
                    now,
                    now,
                ))
                self._conn.commit()

                self.reset_failures()
                return True
            except Exception as e:
                self.handle_failure(e)
                return False

    def delete(self, key: str) -> bool:
        """Remove entry from database."""
        with self._lock:
            try:
                cursor = self._conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                deleted = cursor.rowcount > 0
                self._conn.commit()
                return deleted
            except Exception as e:
                self.handle_failure(e)
                return False

    def clear(self) -> int:
        """Clear all entries."""
        with self._lock:
            try:
                cursor = self._conn.execute("SELECT COUNT(*) FROM cache_entries")
                count = cursor.fetchone()[0]
                self._conn.execute("DELETE FROM cache_entries")
                self._conn.commit()
                return count
            except Exception as e:
                self.handle_failure(e)
                return 0

    def size(self) -> int:
        """Return current number of entries."""
        with self._lock:
            try:
                cursor = self._conn.execute("SELECT COUNT(*) FROM cache_entries")
                result = cursor.fetchone()
                return int(result[0]) if result else 0
            except Exception as e:
                self.handle_failure(e)
                return 0

    def keys(self) -> list[str]:
        """Return all cache keys."""
        with self._lock:
            try:
                cursor = self._conn.execute("SELECT key FROM cache_entries")
                result = [str(row[0]) for row in cursor.fetchall()]
                return result
            except Exception as e:
                self.handle_failure(e)
                return []
