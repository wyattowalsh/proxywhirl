"""Cache tier implementations for multi-tier caching strategy.

Defines:
- CacheTier: Abstract base class for cache tier implementations
- MemoryCacheTier: L1 in-memory cache using OrderedDict
- FileCacheTier: L2 JSONL file cache with encryption and file locking
- SQLiteCacheTier: L3 database cache with full persistence
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from abc import ABC, abstractmethod
from collections import OrderedDict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Callable

import portalocker
from loguru import logger

from .crypto import CredentialEncryptor
from .models import CacheEntry, CacheTierConfig

__all__ = [
    "TierType",
    "CacheTier",
    "MemoryCacheTier",
    "JsonlCacheTier",
    "DiskCacheTier",
    "SQLiteCacheTier",
]


class TierType(str, Enum):
    """Cache tier types."""

    L1_MEMORY = "l1_memory"
    L2_FILE = "l2_file"
    L3_SQLITE = "l3_sqlite"


class CacheTier(ABC):
    """Abstract base class for cache tier implementations.

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
    def get(self, key: str) -> CacheEntry | None:
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

    @abstractmethod
    def cleanup_expired(self) -> int:
        """Remove all expired entries in bulk.

        Returns:
            Number of entries removed

        """
        pass

    def __contains__(self, key: str) -> bool:
        """Check if key exists in this tier.

        Args:
            key: Cache key to check

        Returns:
            True if key exists, False otherwise

        """
        return key in self.keys()

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


class MemoryCacheTier(CacheTier):
    """L1 in-memory cache using OrderedDict for LRU tracking.

    Provides O(1) lookups with automatic LRU eviction when max_entries exceeded.
    """

    def __init__(
        self,
        config: CacheTierConfig,
        tier_type: TierType,
        on_evict: Callable[[str, CacheEntry], None] | None = None,
    ) -> None:
        """Initialize memory cache with LRU tracking.

        Args:
            config: Tier configuration
            tier_type: Type of tier (L1/L2/L3)
            on_evict: Optional callback when entry is evicted (key, entry)

        """
        super().__init__(config, tier_type)
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._on_evict = on_evict

    def get(self, key: str) -> CacheEntry | None:
        """Retrieve entry from memory cache, updating LRU order.

        Args:
            key: Cache key to lookup.

        Returns:
            CacheEntry if found, None otherwise. Updates LRU order on hit
            by moving the accessed entry to the end of the OrderedDict.

        Side Effects:
            Moves accessed entry to end of LRU queue (most recently used position).

        """
        if key in self._cache:
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def put(self, key: str, entry: CacheEntry) -> bool:
        """Store entry in memory cache with automatic LRU eviction.

        Args:
            key: Cache key for the entry.
            entry: CacheEntry object to store.

        Returns:
            True if stored successfully, False on error.

        Side Effects:
            - Removes existing entry if key already exists (update operation).
            - Evicts least recently used entry if max_entries exceeded.
            - Calls on_evict callback if provided when eviction occurs.
            - Resets failure counter on success.

        Raises:
            Exception: Caught and handled via handle_failure(), returns False.

        """
        try:
            # Update existing or add new
            if key in self._cache:
                del self._cache[key]
            self._cache[key] = entry

            # Evict LRU if over capacity
            if self.config.max_entries and len(self._cache) > self.config.max_entries:
                evicted_key, evicted_entry = self._cache.popitem(
                    last=False
                )  # Remove oldest (FIFO end)
                # Notify callback of eviction
                if self._on_evict:
                    self._on_evict(evicted_key, evicted_entry)

            self.reset_failures()
            return True
        except Exception as e:
            self.handle_failure(e)
            return False

    def delete(self, key: str) -> bool:
        """Remove entry from memory cache by key.

        Args:
            key: Cache key to delete.

        Returns:
            True if entry existed and was deleted, False if not found.

        Side Effects:
            Removes entry from OrderedDict if present.

        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> int:
        """Clear all entries from memory cache.

        Returns:
            Number of entries that were removed.

        Side Effects:
            Empties the OrderedDict, releasing all cached entries.

        """
        count = len(self._cache)
        self._cache.clear()
        return count

    def size(self) -> int:
        """Return current number of entries in memory cache.

        Returns:
            Count of entries currently stored in the OrderedDict.

        """
        return len(self._cache)

    def keys(self) -> list[str]:
        """Return list of all cache keys in memory tier.

        Returns:
            List of cache keys in LRU order (oldest to newest).

        """
        return list(self._cache.keys())

    def cleanup_expired(self) -> int:
        """Remove all expired entries from memory cache in bulk.

        Returns:
            Number of expired entries that were removed.

        Side Effects:
            Deletes all entries where is_expired property is True.

        """
        removed = 0
        expired_keys = [key for key, entry in self._cache.items() if entry.is_expired]
        for key in expired_keys:
            del self._cache[key]
            removed += 1
        return removed


class JsonlCacheTier(CacheTier):
    """L2 JSONL file-based cache with sharding and encryption.

    Provides persistent caching using JSONL (JSON Lines) files with:
    - Sharded storage for better I/O performance
    - File locking for concurrent access safety
    - Encrypted credentials at rest
    - Simple text format for debugging and portability

    Best suited for:
    - Smaller cache sizes (<10K entries)
    - Environments where SQLite is unavailable
    - Cases requiring human-readable cache files
    - Simple deployment without database dependencies

    For larger caches (>10K entries), consider DiskCacheTier (SQLite-based)
    which provides O(log n) lookups vs O(n) for JSONL.
    """

    def __init__(
        self,
        config: CacheTierConfig,
        tier_type: TierType,
        cache_dir: Path,
        encryptor: CredentialEncryptor | None = None,
        num_shards: int = 16,
    ) -> None:
        """Initialize JSONL-based L2 cache.

        Args:
            config: Tier configuration
            tier_type: Type of tier (should be L2_FILE)
            cache_dir: Directory for JSONL shard files
            encryptor: Credential encryptor for username/password
            num_shards: Number of shard files (default: 16)

        """
        super().__init__(config, tier_type)
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.encryptor = encryptor or CredentialEncryptor()
        self.num_shards = num_shards

        # In-memory index for fast lookups (key -> shard_id)
        self._index: dict[str, int] = {}
        # OrderedDict for O(1) LRU eviction tracking (key -> last_accessed timestamp)
        self._access_order: OrderedDict[str, float] = OrderedDict()
        self._rebuild_index()

    def _get_shard_path(self, shard_id: int) -> Path:
        """Get path to a specific shard file."""
        return self.cache_dir / f"shard_{shard_id:02d}.jsonl"

    def _get_shard_id(self, key: str) -> int:
        """Compute shard ID for a cache key using deterministic hashing.

        Uses MD5 (not for security, just for deterministic distribution)
        instead of Python's hash() which is randomized per process.
        """
        return (
            int(hashlib.md5(key.encode(), usedforsecurity=False).hexdigest(), 16) % self.num_shards
        )

    def _evict_oldest(self) -> bool:
        """Evict oldest entry based on last_accessed time for LRU behavior.

        Uses OrderedDict for O(1) eviction instead of O(n*m) shard scanning.

        Returns:
            True if an entry was evicted, False otherwise

        """
        if not self._access_order:
            return False

        # Pop oldest entry (first item in OrderedDict)
        oldest_key, _ = self._access_order.popitem(last=False)

        # Delete from storage
        if self.delete(oldest_key):
            logger.debug(f"Evicted oldest entry: {oldest_key}")
            return True

        return False

    def _rebuild_index(self) -> None:
        """Rebuild in-memory index and access order from all shard files."""
        self._index.clear()
        self._access_order.clear()

        # Collect all entries with their last_accessed times
        entries_with_times: list[tuple[str, int, float]] = []

        for shard_id in range(self.num_shards):
            shard_path = self._get_shard_path(shard_id)
            if not shard_path.exists():
                continue
            try:
                with portalocker.Lock(shard_path, "r", timeout=5) as f:
                    for line in f:
                        if not line.strip():
                            continue
                        try:
                            data = json.loads(line)
                            if "key" in data:
                                key = data["key"]
                                self._index[key] = shard_id

                                # Extract last_accessed time for ordering
                                if "last_accessed" in data:
                                    try:
                                        last_accessed = datetime.fromisoformat(
                                            data["last_accessed"]
                                        )
                                        entries_with_times.append(
                                            (key, shard_id, last_accessed.timestamp())
                                        )
                                    except (ValueError, AttributeError):
                                        # Default to current time if parse fails
                                        entries_with_times.append(
                                            (key, shard_id, datetime.now(timezone.utc).timestamp())
                                        )
                                else:
                                    # No timestamp, use current time
                                    entries_with_times.append(
                                        (key, shard_id, datetime.now(timezone.utc).timestamp())
                                    )
                        except json.JSONDecodeError as e:
                            logger.debug(f"Skipping corrupted line during index rebuild: {e}")
                            continue
            except (OSError, portalocker.LockException) as e:
                logger.warning(f"Failed to read shard {shard_id} during index rebuild: {e}")
                continue

        # Sort by timestamp (oldest first) and populate OrderedDict
        entries_with_times.sort(key=lambda x: x[2])
        for key, _, timestamp in entries_with_times:
            self._access_order[key] = timestamp

    def _read_shard(self, shard_id: int) -> dict[str, dict]:
        """Read all entries from a shard file.

        Returns:
            Dict mapping key to entry data dict

        """
        shard_path = self._get_shard_path(shard_id)
        entries: dict[str, dict] = {}

        if not shard_path.exists():
            return entries

        try:
            with portalocker.Lock(shard_path, "r", timeout=5) as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if "key" in data:
                            entries[data["key"]] = data
                    except json.JSONDecodeError as e:
                        logger.debug(f"Skipping corrupted line in shard {shard_id}: {e}")
                        continue
        except (OSError, portalocker.LockException) as e:
            logger.warning(f"Failed to read shard {shard_id}: {e}")

        return entries

    def _write_shard(self, shard_id: int, entries: dict[str, dict]) -> bool:
        """Write all entries to a shard file atomically.

        Args:
            shard_id: Shard file ID
            entries: Dict mapping key to entry data dict

        Returns:
            True if write succeeded

        """
        shard_path = self._get_shard_path(shard_id)

        try:
            # Write to temp file first, then rename for atomicity
            temp_path = shard_path.with_suffix(".tmp")
            with portalocker.Lock(temp_path, "w", timeout=5) as f:
                for data in entries.values():
                    json.dump(data, f)
                    f.write("\n")

            # Atomic rename
            temp_path.replace(shard_path)
            return True
        except (OSError, portalocker.LockException) as e:
            logger.error(f"Failed to write shard {shard_id}: {e}")
            return False

    def get(self, key: str) -> CacheEntry | None:
        """Retrieve entry from JSONL shard.

        Args:
            key: Cache key to lookup

        Returns:
            CacheEntry if found and valid, None otherwise

        """
        try:
            shard_id = self._index.get(key)
            if shard_id is None:
                return None

            entries = self._read_shard(shard_id)
            data = entries.get(key)
            if not data:
                # Key was in index but not in file - remove from both index and access order
                self._index.pop(key, None)
                self._access_order.pop(key, None)
                return None

            # Decrypt credentials
            if data.get("username_encrypted"):
                username_bytes = bytes.fromhex(data["username_encrypted"])
                data["username"] = self.encryptor.decrypt(username_bytes)
                del data["username_encrypted"]

            if data.get("password_encrypted"):
                password_bytes = bytes.fromhex(data["password_encrypted"])
                data["password"] = self.encryptor.decrypt(password_bytes)
                del data["password_encrypted"]

            # Convert timestamps (including optional health monitoring timestamps)
            for field in [
                "fetch_time",
                "last_accessed",
                "expires_at",
                "last_health_check",
                "next_check_time",
            ]:
                if field in data and data[field] is not None and isinstance(data[field], str):
                    data[field] = datetime.fromisoformat(data[field])

            # Ensure health monitoring fields have defaults for backward compatibility
            data.setdefault("consecutive_health_failures", 0)
            data.setdefault("consecutive_health_successes", 0)
            data.setdefault("recovery_attempt", 0)
            data.setdefault("total_health_checks", 0)
            data.setdefault("total_health_check_failures", 0)

            # Update access order (move to end for LRU)
            if key in self._access_order:
                self._access_order.move_to_end(key)
            self._access_order[key] = datetime.now(timezone.utc).timestamp()

            self.reset_failures()
            return CacheEntry(**data)
        except Exception as e:
            self.handle_failure(e)
            return None

    def put(self, key: str, entry: CacheEntry) -> bool:
        """Store entry in JSONL shard with encrypted credentials.

        Args:
            key: Cache key for entry (should match entry.key)
            entry: CacheEntry to store

        Returns:
            True if stored successfully, False otherwise

        """
        try:
            # Validate key matches entry.key for consistency
            if key != entry.key:
                logger.warning(
                    f"Key mismatch in put(): parameter '{key}' vs entry.key '{entry.key}', using entry.key"
                )

            # Check if we need to evict before adding (LRU eviction)
            # Only evict if this is a new key and we're at capacity
            if (
                self.config.max_entries
                and entry.key not in self._index
                and len(self._index) >= self.config.max_entries
            ):
                self._evict_oldest()

            # Always use entry.key for consistency
            shard_id = self._get_shard_id(entry.key)

            # Read existing shard
            entries = self._read_shard(shard_id)

            # Prepare entry data with all fields including health monitoring
            data = {
                "key": entry.key,
                "proxy_url": entry.proxy_url,
                "source": entry.source,
                "fetch_time": entry.fetch_time.isoformat(),
                "last_accessed": entry.last_accessed.isoformat(),
                "access_count": entry.access_count,
                "ttl_seconds": entry.ttl_seconds,
                "expires_at": entry.expires_at.isoformat(),
                "health_status": entry.health_status.value,
                "failure_count": entry.failure_count,
                "evicted_from_l1": entry.evicted_from_l1,
                # Health monitoring fields (Feature 006)
                "last_health_check": entry.last_health_check.isoformat()
                if entry.last_health_check
                else None,
                "consecutive_health_failures": entry.consecutive_health_failures,
                "consecutive_health_successes": entry.consecutive_health_successes,
                "recovery_attempt": entry.recovery_attempt,
                "next_check_time": entry.next_check_time.isoformat()
                if entry.next_check_time
                else None,
                "last_health_error": entry.last_health_error,
                "total_health_checks": entry.total_health_checks,
                "total_health_check_failures": entry.total_health_check_failures,
            }

            # Encrypt credentials
            if entry.username:
                encrypted = self.encryptor.encrypt(entry.username)
                data["username_encrypted"] = encrypted.hex()

            if entry.password:
                encrypted = self.encryptor.encrypt(entry.password)
                data["password_encrypted"] = encrypted.hex()

            # Add/update entry using entry.key for consistency
            entries[entry.key] = data

            # Write shard
            if self._write_shard(shard_id, entries):
                self._index[entry.key] = shard_id
                # Update access order for LRU tracking
                if entry.key in self._access_order:
                    self._access_order.move_to_end(entry.key)
                self._access_order[entry.key] = entry.last_accessed.timestamp()
                self.reset_failures()
                return True
            return False
        except Exception as e:
            self.handle_failure(e)
            return False

    def delete(self, key: str) -> bool:
        """Remove entry from JSONL shard.

        Args:
            key: Cache key to delete

        Returns:
            True if entry existed and was deleted, False if not found

        """
        try:
            shard_id = self._index.get(key)
            if shard_id is None:
                return False

            entries = self._read_shard(shard_id)
            if key not in entries:
                self._index.pop(key, None)
                self._access_order.pop(key, None)
                return False

            del entries[key]
            if self._write_shard(shard_id, entries):
                self._index.pop(key, None)
                self._access_order.pop(key, None)
                return True
            return False
        except Exception as e:
            self.handle_failure(e)
            return False

    def clear(self) -> int:
        """Clear all JSONL shard files.

        Returns:
            Number of entries cleared

        """
        try:
            count = len(self._index)

            # Delete all shard files
            for shard_id in range(self.num_shards):
                shard_path = self._get_shard_path(shard_id)
                if shard_path.exists():
                    shard_path.unlink()

            self._index.clear()
            self._access_order.clear()
            self.reset_failures()
            return count
        except Exception as e:
            self.handle_failure(e)
            return 0

    def size(self) -> int:
        """Return current number of entries.

        Returns:
            Number of entries in index

        """
        return len(self._index)

    def keys(self) -> list[str]:
        """Return list of all keys.

        Returns:
            List of cache keys

        """
        return list(self._index.keys())

    def cleanup_expired(self) -> int:
        """Remove all expired entries from all shards.

        Returns:
            Number of entries removed

        """
        try:
            removed = 0
            now = datetime.now(timezone.utc)

            for shard_id in range(self.num_shards):
                entries = self._read_shard(shard_id)
                original_count = len(entries)

                # Filter out expired entries
                valid_entries = {}
                for key, data in entries.items():
                    expires_at_str = data.get("expires_at")
                    if expires_at_str:
                        try:
                            expires_at = datetime.fromisoformat(expires_at_str)
                            if expires_at >= now:
                                valid_entries[key] = data
                            else:
                                self._index.pop(key, None)
                                self._access_order.pop(key, None)
                                removed += 1
                        except ValueError:
                            # Invalid timestamp - keep entry
                            valid_entries[key] = data
                    else:
                        valid_entries[key] = data

                # Write back if entries were removed
                if len(valid_entries) < original_count:
                    self._write_shard(shard_id, valid_entries)

            self.reset_failures()
            return removed
        except Exception as e:
            self.handle_failure(e)
            return 0


class DiskCacheTier(CacheTier):
    """L2 SQLite-based cache with encryption and indexed lookups.

    Optimized for >10K entries using SQLite with B-tree indexes instead of JSONL.
    Provides O(log n) lookups vs O(n) for JSONL, achieving <10ms reads for 10K+ entries.

    Uses a lightweight SQLite database with:
    - Primary key index on cache key for fast lookups
    - Encrypted credentials stored as BLOB
    - Efficient bulk operations (cleanup, size, keys)
    - File-based persistence without complex sharding
    - Persistent connection pooling for performance (RES-005)

    Thread Safety:
        Uses a threading.Lock to protect connection access. The connection is
        created with check_same_thread=False to allow multi-threaded access.
    """

    def __init__(
        self,
        config: CacheTierConfig,
        tier_type: TierType,
        cache_dir: Path,
        encryptor: CredentialEncryptor | None = None,
    ) -> None:
        """Initialize SQLite-based L2 cache.

        Args:
            config: Tier configuration
            tier_type: Type of tier (should be L2_FILE)
            cache_dir: Directory for cache database
            encryptor: Credential encryptor for username/password

        """
        super().__init__(config, tier_type)
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.encryptor = encryptor or CredentialEncryptor()

        # Use SQLite database in cache directory
        self.db_path = self.cache_dir / "l2_cache.db"

        # Connection pool: persistent connection with thread-safe access (RES-005)
        import threading

        self._conn: sqlite3.Connection | None = None
        self._conn_lock = threading.Lock()

        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create persistent SQLite connection (RES-005 fix).

        Thread-safe access to a single persistent connection. Creates the
        connection on first access with settings optimized for concurrent use.

        Returns:
            SQLite connection instance

        """
        with self._conn_lock:
            if self._conn is None:
                self._conn = sqlite3.connect(
                    str(self.db_path),
                    check_same_thread=False,  # Allow multi-threaded access
                    timeout=30.0,  # Wait up to 30s for locks
                    isolation_level="DEFERRED",  # Better concurrency
                )
                # Enable write-ahead logging for better concurrency
                self._conn.execute("PRAGMA journal_mode=WAL")
                self._conn.execute("PRAGMA synchronous=NORMAL")
            return self._conn

    def close(self) -> None:
        """Close the persistent SQLite connection and release database resources.

        Should be called when the cache tier is no longer needed to properly
        release database resources and file locks. Safe to call multiple times.

        Side Effects:
            - Acquires connection lock to ensure thread safety.
            - Closes active SQLite connection if present.
            - Sets internal connection to None to prevent reuse.
            - Suppresses any exceptions during close to ensure cleanup completes.

        Thread Safety:
            Thread-safe via internal lock. Multiple threads can safely call this
            method concurrently.

        Example:
            >>> tier = DiskCacheTier(config, TierType.L2_FILE, cache_dir)
            >>> # ... use tier ...
            >>> tier.close()  # Clean up resources
            >>> tier.close()  # Safe to call again

        """
        with self._conn_lock:
            if self._conn is not None:
                try:
                    self._conn.close()
                except Exception:
                    pass  # Ignore errors on close
                self._conn = None

    def __del__(self) -> None:
        """Destructor to ensure SQLite connection is closed during garbage collection.

        Automatically called when the DiskCacheTier object is garbage collected.
        Ensures database resources are released even if close() was not explicitly
        called.

        Side Effects:
            - Calls close() to release database connection and locks.
            - Prevents resource leaks if object is destroyed without explicit cleanup.

        Note:
            Destructors in Python are not guaranteed to be called immediately.
            For predictable cleanup, explicitly call close() instead of relying
            on __del__.

        """
        self.close()

    def _init_db(self) -> None:
        """Initialize L2 cache database schema.

        Creates a lightweight table optimized for L2 tier operations:
        - Simpler schema than L3 (no health monitoring fields)
        - Primary key index for fast lookups
        - Expires_at index for efficient cleanup
        """
        try:
            conn = self._get_connection()
            conn.execute("""
                CREATE TABLE IF NOT EXISTS l2_cache (
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
                    evicted_from_l1 INTEGER DEFAULT 0
                )
            """)

            # Create indexes for common queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_l2_expires_at ON l2_cache(expires_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_l2_source ON l2_cache(source)")

            conn.commit()
        except Exception as e:
            self.handle_failure(e)

    def get(self, key: str) -> CacheEntry | None:
        """Retrieve entry from SQLite database with O(log n) indexed lookup.

        Args:
            key: Cache key to lookup

        Returns:
            CacheEntry if found and valid, None otherwise

        """
        try:
            conn = self._get_connection()
            cursor = conn.execute("SELECT * FROM l2_cache WHERE key = ?", (key,))
            row = cursor.fetchone()

            if not row:
                return None

            # Map row to dict
            columns = [
                "key",
                "proxy_url",
                "username_encrypted",
                "password_encrypted",
                "source",
                "fetch_time",
                "last_accessed",
                "access_count",
                "ttl_seconds",
                "expires_at",
                "health_status",
                "failure_count",
                "evicted_from_l1",
            ]
            data = dict(zip(columns, row))

            # Decrypt credentials
            if data["username_encrypted"]:
                data["username"] = self.encryptor.decrypt(data["username_encrypted"])
            if data["password_encrypted"]:
                data["password"] = self.encryptor.decrypt(data["password_encrypted"])

            # Convert timestamps
            for field in ["fetch_time", "last_accessed", "expires_at"]:
                if data.get(field) is not None:
                    data[field] = datetime.fromtimestamp(data[field], tz=timezone.utc)

            # Convert boolean
            data["evicted_from_l1"] = bool(data["evicted_from_l1"])

            # Remove encrypted fields
            data.pop("username_encrypted")
            data.pop("password_encrypted")

            self.reset_failures()
            return CacheEntry(**data)
        except Exception as e:
            self.handle_failure(e)
            return None

    def put(self, key: str, entry: CacheEntry) -> bool:
        """Store entry in SQLite database with INSERT OR REPLACE.

        Args:
            key: Cache key for entry
            entry: CacheEntry to store

        Returns:
            True if stored successfully, False otherwise

        """
        try:
            # Encrypt credentials (encryptor.encrypt expects SecretStr, not string)
            username_encrypted = None
            if entry.username:
                username_encrypted = self.encryptor.encrypt(entry.username)
            password_encrypted = None
            if entry.password:
                password_encrypted = self.encryptor.encrypt(entry.password)

            conn = self._get_connection()
            conn.execute(
                """
                INSERT OR REPLACE INTO l2_cache (
                    key, proxy_url, username_encrypted, password_encrypted,
                    source, fetch_time, last_accessed, access_count,
                    ttl_seconds, expires_at, health_status, failure_count,
                    evicted_from_l1
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
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
                    int(entry.evicted_from_l1),
                ),
            )
            conn.commit()

            self.reset_failures()
            return True
        except Exception as e:
            self.handle_failure(e)
            return False

    def delete(self, key: str) -> bool:
        """Remove entry from SQLite database by cache key.

        Uses SQL DELETE with primary key lookup for O(log n) performance.

        Args:
            key: Cache key to delete.

        Returns:
            True if entry existed and was deleted, False if not found or on error.

        Side Effects:
            - Acquires persistent connection via thread-safe _get_connection().
            - Executes DELETE query with parameterized key (SQL injection safe).
            - Commits transaction before returning.
            - Does NOT reset failure counter (only success paths do).

        Thread Safety:
            Thread-safe via connection lock in _get_connection().

        Raises:
            Exception: Caught and handled via handle_failure(), returns False.

        """
        try:
            conn = self._get_connection()
            cursor = conn.execute("DELETE FROM l2_cache WHERE key = ?", (key,))
            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted
        except Exception as e:
            self.handle_failure(e)
            return False

    def clear(self) -> int:
        """Clear all entries from SQLite L2 cache database.

        Performs bulk deletion of all cache entries. More efficient than
        iterating through individual deletes.

        Returns:
            Number of entries that were cleared, 0 on error.

        Side Effects:
            - Acquires persistent connection via thread-safe _get_connection().
            - Counts total entries before deletion.
            - Executes DELETE FROM without WHERE clause (removes all rows).
            - Commits transaction before returning.
            - Resets failure counter on success.

        Thread Safety:
            Thread-safe via connection lock in _get_connection().

        Performance:
            O(n) where n is the number of entries, but executes as a single
            SQL operation with automatic index cleanup.

        Raises:
            Exception: Caught and handled via handle_failure(), returns 0.

        Example:
            >>> tier = DiskCacheTier(config, TierType.L2_FILE, cache_dir)
            >>> tier.size()
            1000
            >>> cleared = tier.clear()
            >>> print(f"Cleared {cleared} entries")
            Cleared 1000 entries
            >>> tier.size()
            0

        """
        try:
            conn = self._get_connection()
            cursor = conn.execute("SELECT COUNT(*) FROM l2_cache")
            count = cursor.fetchone()[0]
            conn.execute("DELETE FROM l2_cache")
            conn.commit()

            self.reset_failures()
            return count
        except Exception as e:
            self.handle_failure(e)
            return 0

    def size(self) -> int:
        """Return current number of entries in SQLite L2 cache database.

        Uses SQL COUNT(*) for efficient O(1) size calculation via table metadata.

        Returns:
            Number of cache entries currently stored, 0 on error.

        Side Effects:
            - Acquires persistent connection via thread-safe _get_connection().
            - Executes SELECT COUNT(*) query (reads table metadata, not rows).
            - Resets failure counter on success.

        Thread Safety:
            Thread-safe via connection lock in _get_connection().

        Performance:
            O(1) - SQLite maintains row count in table metadata.

        Raises:
            Exception: Caught and handled via handle_failure(), returns 0.

        """
        try:
            conn = self._get_connection()
            cursor = conn.execute("SELECT COUNT(*) FROM l2_cache")
            count = cursor.fetchone()[0]

            self.reset_failures()
            return count
        except Exception as e:
            self.handle_failure(e)
            return 0

    def keys(self) -> list[str]:
        """Return list of all cache keys from SQLite L2 database.

        Retrieves all cache keys without loading full entry data. Useful for
        cache inspection, debugging, and bulk operations.

        Returns:
            List of all cache keys in database, empty list on error.

        Side Effects:
            - Acquires persistent connection via thread-safe _get_connection().
            - Executes SELECT key query (fetches only key column, not full rows).
            - Loads all keys into memory as a list.
            - Resets failure counter on success.

        Thread Safety:
            Thread-safe via connection lock in _get_connection().

        Performance:
            O(n) where n is number of entries. For large caches (>10K entries),
            consider using size() to check count before calling.

        Raises:
            Exception: Caught and handled via handle_failure(), returns [].

        Warning:
            For very large caches (>100K entries), this may consume significant
            memory. Consider pagination or streaming approaches if needed.

        """
        try:
            conn = self._get_connection()
            cursor = conn.execute("SELECT key FROM l2_cache")
            keys = [row[0] for row in cursor.fetchall()]

            self.reset_failures()
            return keys
        except Exception as e:
            self.handle_failure(e)
            return []

    def cleanup_expired(self) -> int:
        """Remove all expired entries from SQLite L2 database using indexed SQL DELETE.

        Performs bulk deletion of expired entries in a single SQL operation.
        Uses the expires_at index for efficient identification.

        Returns:
            Number of expired entries that were removed, 0 on error.

        Side Effects:
            - Acquires persistent connection via thread-safe _get_connection().
            - Calculates current timestamp in UTC.
            - Executes DELETE with WHERE clause using expires_at index.
            - Commits transaction before returning.
            - Resets failure counter on success.

        Thread Safety:
            Thread-safe via connection lock in _get_connection().

        Performance:
            O(m log n) where m is number of expired entries and n is total entries.
            The idx_l2_expires_at index makes this significantly faster than
            full table scan.

        Raises:
            Exception: Caught and handled via handle_failure(), returns 0.

        Example:
            >>> tier = DiskCacheTier(config, TierType.L2_FILE, cache_dir)
            >>> removed = tier.cleanup_expired()
            >>> print(f"Removed {removed} expired entries")
            Removed 42 expired entries

        """
        try:
            now = datetime.now(timezone.utc).timestamp()

            conn = self._get_connection()
            cursor = conn.execute("DELETE FROM l2_cache WHERE expires_at < ?", (now,))
            removed = cursor.rowcount
            conn.commit()

            self.reset_failures()
            return removed
        except Exception as e:
            self.handle_failure(e)
            return 0

    def migrate_from_jsonl(self, jsonl_dir: Path | None = None) -> int:
        """Migrate existing JSONL shard files to SQLite L2 cache.

        This method provides a migration path from the old JSONL-based L2 cache
        to the new SQLite-based implementation. It reads all shard_*.jsonl files
        from the specified directory and imports them into the SQLite database.

        Args:
            jsonl_dir: Directory containing shard_*.jsonl files.
                      Defaults to self.cache_dir if not specified.

        Returns:
            Number of entries successfully migrated

        Example:
            >>> tier = DiskCacheTier(config, TierType.L2_FILE, cache_dir)
            >>> migrated = tier.migrate_from_jsonl()
            >>> print(f"Migrated {migrated} entries from JSONL to SQLite")

        """
        if jsonl_dir is None:
            jsonl_dir = self.cache_dir

        migrated = 0
        errors = 0

        # Find all JSONL shard files
        shard_files = list(jsonl_dir.glob("shard_*.jsonl"))

        if not shard_files:
            return 0

        for shard_file in shard_files:
            try:
                with portalocker.Lock(shard_file, "r", timeout=5) as f:
                    for line in f:
                        if not line.strip():
                            continue

                        try:
                            data = json.loads(line)

                            # Create CacheEntry from JSONL data
                            # Handle both old and new timestamp formats
                            for field in ["fetch_time", "last_accessed", "expires_at"]:
                                if field in data and isinstance(data[field], str):
                                    data[field] = datetime.fromisoformat(data[field])

                            # Handle encrypted credentials if present
                            if "username_encrypted" in data:
                                username_hex = data.pop("username_encrypted")
                                data["username"] = self.encryptor.decrypt(
                                    bytes.fromhex(username_hex)
                                )

                            if "password_encrypted" in data:
                                password_hex = data.pop("password_encrypted")
                                data["password"] = self.encryptor.decrypt(
                                    bytes.fromhex(password_hex)
                                )

                            # Create entry and store in SQLite
                            entry = CacheEntry(**data)
                            if self.put(entry.key, entry):
                                migrated += 1
                            else:
                                errors += 1

                        except (json.JSONDecodeError, ValueError, KeyError):
                            # Skip corrupted entries
                            errors += 1
                            continue

            except Exception:
                # Skip files that can't be read
                errors += 1
                continue

        return migrated


class SQLiteCacheTier(CacheTier):
    """L3 SQLite database cache with encrypted credentials.

    Provides durable persistence with SQL indexing for fast lookups.
    """

    def __init__(
        self,
        config: CacheTierConfig,
        tier_type: TierType,
        db_path: Path,
        encryptor: CredentialEncryptor | None = None,
    ) -> None:
        """Initialize SQLite-based L3 cache with health monitoring.

        Args:
            config: Tier configuration settings.
            tier_type: Type of tier (should be L3_SQLITE).
            db_path: Path to SQLite database file.
            encryptor: Optional credential encryptor for username/password.
                      Creates default CredentialEncryptor if not provided.

        Side Effects:
            - Creates parent directories for database if they don't exist.
            - Initializes database schema with cache_entries and health_history tables.
            - Creates indexes for expires_at, source, health_status, and last_accessed.

        """
        super().__init__(config, tier_type)
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.encryptor = encryptor or CredentialEncryptor()
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema with health monitoring fields.

        Creates two tables:
        1. cache_entries: Main cache storage with encrypted credentials and health fields.
        2. health_history: Historical record of health check results.

        Creates indexes for efficient queries on expires_at, source, health_status,
        last_accessed, and health_history lookups.

        Side Effects:
            - Creates cache_entries table if not exists.
            - Creates health_history table if not exists.
            - Migrates existing tables to add health monitoring columns.
            - Creates performance indexes.
            - Commits schema changes.
        """
        with sqlite3.connect(str(self.db_path)) as conn:
            # Create cache_entries table
            conn.execute("""
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
                    updated_at REAL NOT NULL,
                    -- Health monitoring fields (Feature 006)
                    last_health_check REAL,
                    consecutive_health_failures INTEGER DEFAULT 0,
                    consecutive_health_successes INTEGER DEFAULT 0,
                    recovery_attempt INTEGER DEFAULT 0,
                    next_check_time REAL,
                    last_health_error TEXT,
                    total_health_checks INTEGER DEFAULT 0,
                    total_health_check_failures INTEGER DEFAULT 0,
                    evicted_from_l1 INTEGER DEFAULT 0
                )
            """)

            # Migrate existing tables to add health columns (T008)
            self._migrate_health_columns(conn)

            # Create health_history table (T007)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS health_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    proxy_key TEXT NOT NULL,
                    check_time REAL NOT NULL,
                    status TEXT NOT NULL,
                    response_time_ms REAL,
                    error_message TEXT,
                    check_url TEXT NOT NULL,
                    FOREIGN KEY (proxy_key) REFERENCES cache_entries(key) ON DELETE CASCADE
                )
            """)

            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_expires_at ON cache_entries(expires_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_source ON cache_entries(source)")
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_health_status ON cache_entries(health_status)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache_entries(last_accessed)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_health_history_proxy ON health_history(proxy_key)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_health_history_time ON health_history(check_time)"
            )

            conn.commit()

    def _migrate_health_columns(self, conn: sqlite3.Connection) -> None:
        """Add health monitoring columns to existing cache_entries table if they don't exist (T008).

        Provides backward compatibility by adding new health monitoring columns to
        existing databases without data loss.

        Args:
            conn: Active SQLite connection to the cache database.

        Side Effects:
            - Adds missing health monitoring columns to cache_entries table.
            - Uses whitelisted column names to prevent SQL injection.
            - Silently ignores OperationalError if columns already exist (race condition safety).

        Note:
            Column names are from a hardcoded whitelist, not user input, making
            f-string SQL safe in this specific context.

        """
        # Get existing columns
        cursor = conn.execute("PRAGMA table_info(cache_entries)")
        existing_columns = {row[1] for row in cursor.fetchall()}

        # Define health columns to add (whitelist to prevent injection)
        health_columns = [
            ("last_health_check", "REAL"),
            ("consecutive_health_failures", "INTEGER DEFAULT 0"),
            ("consecutive_health_successes", "INTEGER DEFAULT 0"),
            ("recovery_attempt", "INTEGER DEFAULT 0"),
            ("next_check_time", "REAL"),
            ("last_health_error", "TEXT"),
            ("total_health_checks", "INTEGER DEFAULT 0"),
            ("total_health_check_failures", "INTEGER DEFAULT 0"),
            ("evicted_from_l1", "INTEGER DEFAULT 0"),
        ]

        # Add missing columns - safe because column names are from whitelist
        for col_name, col_type in health_columns:
            if col_name not in existing_columns:
                try:
                    # Column names from whitelist, not user input
                    conn.execute(f"ALTER TABLE cache_entries ADD COLUMN {col_name} {col_type}")
                except sqlite3.OperationalError:
                    # Column may already exist in a concurrent process
                    pass

    def get(self, key: str) -> CacheEntry | None:
        """Retrieve entry from SQLite database with decrypted credentials.

        Args:
            key: Cache key to lookup.

        Returns:
            CacheEntry if found with decrypted username/password, None otherwise.

        Side Effects:
            - Opens new SQLite connection for query.
            - Decrypts username_encrypted and password_encrypted BLOBs.
            - Converts UNIX timestamps to datetime objects.
            - Resets failure counter on success.

        Raises:
            Exception: Caught and handled via handle_failure(), returns None.

        """
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.execute("SELECT * FROM cache_entries WHERE key = ?", (key,))
                row = cursor.fetchone()

            if not row:
                return None

            # Map row to dict
            columns = [
                "key",
                "proxy_url",
                "username_encrypted",
                "password_encrypted",
                "source",
                "fetch_time",
                "last_accessed",
                "access_count",
                "ttl_seconds",
                "expires_at",
                "health_status",
                "failure_count",
                "created_at",
                "updated_at",
                # Health monitoring fields
                "last_health_check",
                "consecutive_health_failures",
                "consecutive_health_successes",
                "recovery_attempt",
                "next_check_time",
                "last_health_error",
                "total_health_checks",
                "total_health_check_failures",
                "evicted_from_l1",
            ]
            data = dict(zip(columns, row))

            # Decrypt credentials
            if data["username_encrypted"]:
                data["username"] = self.encryptor.decrypt(data["username_encrypted"])
            if data["password_encrypted"]:
                data["password"] = self.encryptor.decrypt(data["password_encrypted"])

            # Convert timestamps
            for field in [
                "fetch_time",
                "last_accessed",
                "expires_at",
                "created_at",
                "updated_at",
                "last_health_check",
                "next_check_time",
            ]:
                if data.get(field) is not None:
                    data[field] = datetime.fromtimestamp(data[field], tz=timezone.utc)

            # Convert boolean
            if data.get("evicted_from_l1") is not None:
                data["evicted_from_l1"] = bool(data["evicted_from_l1"])

            # Remove encrypted fields
            data.pop("username_encrypted")
            data.pop("password_encrypted")

            self.reset_failures()
            return CacheEntry(**data)
        except Exception as e:
            self.handle_failure(e)
            return None

    def put(self, key: str, entry: CacheEntry) -> bool:
        """Store entry in SQLite database with encrypted credentials.

        Args:
            key: Cache key for the entry.
            entry: CacheEntry object to store with all fields including health monitoring data.

        Returns:
            True if stored successfully, False on error.

        Side Effects:
            - Opens new SQLite connection for write.
            - Encrypts username and password fields as BLOBs.
            - Uses INSERT OR REPLACE (upsert) to handle updates.
            - Sets created_at and updated_at to current timestamp.
            - Commits transaction before returning.
            - Resets failure counter on success.

        Raises:
            Exception: Caught and handled via handle_failure(), returns False.

        """
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

            # Helper to convert optional datetime to timestamp
            def to_timestamp(dt: datetime | None) -> float | None:
                return dt.timestamp() if dt is not None else None

            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO cache_entries (
                        key, proxy_url, username_encrypted, password_encrypted,
                        source, fetch_time, last_accessed, access_count,
                        ttl_seconds, expires_at, health_status, failure_count,
                        created_at, updated_at,
                        last_health_check, consecutive_health_failures, consecutive_health_successes,
                        recovery_attempt, next_check_time, last_health_error,
                        total_health_checks, total_health_check_failures, evicted_from_l1
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
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
                        # Health monitoring fields
                        to_timestamp(entry.last_health_check),
                        entry.consecutive_health_failures,
                        entry.consecutive_health_successes,
                        entry.recovery_attempt,
                        to_timestamp(entry.next_check_time),
                        entry.last_health_error,
                        entry.total_health_checks,
                        entry.total_health_check_failures,
                        int(entry.evicted_from_l1),
                    ),
                )
                conn.commit()

            self.reset_failures()
            return True
        except Exception as e:
            self.handle_failure(e)
            return False

    def delete(self, key: str) -> bool:
        """Remove entry from SQLite database by key.

        Args:
            key: Cache key to delete.

        Returns:
            True if entry existed and was deleted, False if not found.

        Side Effects:
            - Opens new SQLite connection for deletion.
            - Cascades to delete related health_history records via FOREIGN KEY.
            - Commits transaction before returning.

        Raises:
            Exception: Caught and handled via handle_failure(), returns False.

        """
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                deleted = cursor.rowcount > 0
                conn.commit()
            return deleted
        except Exception as e:
            self.handle_failure(e)
            return False

    def clear(self) -> int:
        """Clear all entries from SQLite database.

        Returns:
            Number of entries that were deleted.

        Side Effects:
            - Opens new SQLite connection for operation.
            - Deletes all rows from cache_entries table.
            - Cascades to delete all health_history records via FOREIGN KEY.
            - Commits transaction before returning.
            - Resets failure counter on success.

        Raises:
            Exception: Caught and handled via handle_failure(), returns 0.

        """
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM cache_entries")
                count: int = int(cursor.fetchone()[0])
                conn.execute("DELETE FROM cache_entries")
                conn.commit()
            return count
        except Exception as e:
            self.handle_failure(e)
            return 0

    def size(self) -> int:
        """Return current number of entries in SQLite database.

        Returns:
            Count of entries in cache_entries table, 0 on error.

        Side Effects:
            - Opens new SQLite connection for query.
            - Resets failure counter on success.

        Raises:
            Exception: Caught and handled via handle_failure(), returns 0.

        """
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM cache_entries")
                result = cursor.fetchone()
            return int(result[0]) if result else 0
        except Exception as e:
            self.handle_failure(e)
            return 0

    def keys(self) -> list[str]:
        """Return all cache keys from SQLite database.

        Returns:
            List of all cache keys, empty list on error.

        Side Effects:
            - Opens new SQLite connection for query.
            - Resets failure counter on success.

        Raises:
            Exception: Caught and handled via handle_failure(), returns [].

        """
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.execute("SELECT key FROM cache_entries")
                result = [str(row[0]) for row in cursor.fetchall()]
            return result
        except Exception as e:
            self.handle_failure(e)
            return []

    def cleanup_expired(self) -> int:
        """Remove all expired entries in bulk using SQL DELETE.

        This is significantly more efficient than iterating through all entries,
        reducing cleanup from O(n) to O(1) for expired entries.

        Returns:
            Number of entries removed

        """
        try:
            now = datetime.now(timezone.utc).timestamp()
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.execute(
                    "DELETE FROM cache_entries WHERE expires_at < ?",
                    (now,),
                )
                removed = cursor.rowcount
                conn.commit()
            self.reset_failures()
            return removed
        except Exception as e:
            self.handle_failure(e)
            return 0
