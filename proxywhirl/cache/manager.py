"""
Cache management for proxy storage with multi-tier support.

This module provides the CacheManager class for managing cached proxies
across three storage tiers: L1 (memory), L2 (JSONL files), and L3 (SQLite).
"""

from __future__ import annotations

import hashlib
import json
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

from loguru import logger

from .crypto import CredentialEncryptor
from .models import (
    CacheConfig,
    CacheEntry,
    CacheStatistics,
    HealthStatus,
    L2BackendType,
)
from .tiers import (
    DiskCacheTier,
    JsonlCacheTier,
    MemoryCacheTier,
    SQLiteCacheTier,
    TierType,
)

__all__ = ["CacheManager", "TTLManager"]


class TTLManager:
    """
    Manages TTL-based expiration with hybrid lazy + background cleanup.

    Combines two cleanup strategies:
    - Lazy expiration: Check TTL on every get() operation
    - Background cleanup: Periodic scan of all tiers to remove expired entries

    Attributes:
        cache_manager: Reference to parent CacheManager
        cleanup_interval: Seconds between background cleanup runs
        enabled: Whether background cleanup is running
        cleanup_thread: Background thread for cleanup
    """

    def __init__(self, cache_manager: CacheManager, cleanup_interval: int = 60) -> None:
        """Initialize TTL manager.

        Args:
            cache_manager: Parent CacheManager instance
            cleanup_interval: Seconds between cleanup runs
        """
        self.cache_manager = cache_manager
        self.cleanup_interval = cleanup_interval
        self.enabled = False
        self.cleanup_thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        """Start background cleanup thread."""
        if self.enabled:
            return

        self.enabled = True
        self._stop_event.clear()
        self.cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True,
            name="TTLCleanupThread",
        )
        self.cleanup_thread.start()
        logger.info(f"TTL background cleanup started (interval: {self.cleanup_interval}s)")

    def stop(self) -> None:
        """Stop background cleanup thread."""
        if not self.enabled:
            return

        self.enabled = False
        self._stop_event.set()
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
        logger.info("TTL background cleanup stopped")

    def _cleanup_loop(self) -> None:
        """Background cleanup loop - runs periodically."""
        while self.enabled and not self._stop_event.is_set():
            try:
                removed = self._cleanup_expired_entries()
                if removed > 0:
                    logger.debug(f"TTL cleanup removed {removed} expired entries")
            except Exception as e:
                logger.error(f"TTL cleanup error: {e}")

            # Wait for next iteration
            self._stop_event.wait(self.cleanup_interval)

    def _cleanup_expired_entries(self) -> int:
        """Scan all tiers and remove expired entries using bulk operations.

        Uses optimized bulk cleanup methods for each tier instead of iterating
        through individual entries. For SQLite, this reduces cleanup from O(n)
        to O(1) using SQL DELETE with WHERE clause.

        Thread-safe: Acquires cache manager lock during cleanup to prevent
        race conditions with concurrent cache operations.

        Returns:
            Number of entries removed
        """
        with self.cache_manager._lock:
            removed = 0

            # Bulk cleanup L1 (memory)
            if self.cache_manager.l1_tier.enabled:
                removed += self.cache_manager.l1_tier.cleanup_expired()

            # Bulk cleanup L2 (files)
            if self.cache_manager.l2_tier.enabled:
                removed += self.cache_manager.l2_tier.cleanup_expired()

            # Bulk cleanup L3 (SQLite) - most efficient with SQL DELETE
            if self.cache_manager.l3_tier.enabled:
                removed += self.cache_manager.l3_tier.cleanup_expired()

            return removed


class CacheManager:
    """
    Manages multi-tier caching of proxies with automatic promotion/demotion.

    Orchestrates caching across three tiers:
    - L1 (Memory): Fast in-memory cache using OrderedDict (LRU)
    - L2 (Disk): Persistent cache with configurable backend:
        - JSONL: File-based, human-readable, portable (default, best for <10K entries)
        - SQLite: Database-based, faster for >10K entries with O(log n) lookups
    - L3 (SQLite): Database cache for cold storage with full queryability

    Supports TTL-based expiration, health-based invalidation, and graceful
    degradation when tiers fail.

    Example:
        >>> # Default JSONL backend
        >>> config = CacheConfig()
        >>> manager = CacheManager(config)

        >>> # SQLite backend for large caches
        >>> from proxywhirl.cache.models import L2BackendType
        >>> config = CacheConfig(l2_backend=L2BackendType.SQLITE)
        >>> manager = CacheManager(config)
    """

    def __init__(self, config: CacheConfig) -> None:
        """Initialize cache manager with configuration.

        Args:
            config: Cache configuration with tier settings
        """
        self.config = config
        self.statistics = CacheStatistics()

        # Thread-safe lock for multi-tier operations to prevent race conditions
        # Protects against concurrent cache operations corrupting state during:
        # - L1 eviction while L2/L3 writes are in progress
        # - Tier promotions while deletes are happening
        # - Concurrent puts/gets/deletes across multiple threads
        self._lock = threading.RLock()

        # Shared encryptor for credential encryption across tiers
        encryption_key = None
        if config.encryption_key:
            encryption_key = config.encryption_key.get_secret_value().encode("utf-8")
        self.encryptor = CredentialEncryptor(key=encryption_key)

        # Initialize tiers
        # L1 with eviction callback to propagate eviction state to L2/L3
        self.l1_tier = MemoryCacheTier(
            config.l1_config,
            TierType.L1_MEMORY,
            on_evict=self._on_l1_eviction,
        )

        # Initialize L2 (Disk) - choose backend based on configuration
        if self.config.l2_config.enabled:
            if self.config.l2_backend == L2BackendType.JSONL:
                self.l2_tier = JsonlCacheTier(
                    config=self.config.l2_config,
                    tier_type=TierType.L2_FILE,
                    cache_dir=Path(self.config.l2_cache_dir),
                    encryptor=self.encryptor,
                )
                logger.debug("L2 cache initialized with JSONL backend")
            else:
                self.l2_tier = DiskCacheTier(
                    config=self.config.l2_config,
                    tier_type=TierType.L2_FILE,
                    cache_dir=Path(self.config.l2_cache_dir),
                    encryptor=self.encryptor,
                )
                logger.debug("L2 cache initialized with SQLite backend")
        else:
            # If L2 is disabled, create a dummy tier that does nothing
            self.l2_tier = MemoryCacheTier(self.config.l2_config, TierType.L2_FILE)

        try:
            self.l3_tier = SQLiteCacheTier(
                config.l3_config,
                TierType.L3_SQLITE,
                db_path=Path(config.l3_database_path),
                encryptor=self.encryptor,
            )
        except Exception as exc:
            # If L3 cannot initialize (e.g., read-only path), disable it and continue
            logger.warning("L3 initialization failed - disabling tier", error=str(exc))
            disabled_cfg = config.l3_config.model_copy(update={"enabled": False})
            self.l3_tier = MemoryCacheTier(disabled_cfg, TierType.L3_SQLITE)

        logger.info(
            f"CacheManager initialized: L1={config.l1_config.max_entries}, "
            f"L2={config.l2_config.max_entries} ({config.l2_backend.value}), "
            f"L3={config.l3_config.max_entries}"
        )

        # Initialize TTL manager
        self.ttl_manager: TTLManager | None = None
        if config.enable_background_cleanup:
            self.ttl_manager = TTLManager(
                self,
                cleanup_interval=config.cleanup_interval_seconds,
            )
            self.ttl_manager.start()
            logger.info("TTL background cleanup enabled")

    def __del__(self) -> None:
        """Cleanup resources on deletion."""
        if hasattr(self, "ttl_manager") and self.ttl_manager:
            self.ttl_manager.stop()

    def _on_l1_eviction(self, key: str, entry: CacheEntry) -> None:
        """Handle L1 eviction by marking entry as evicted in L2/L3.

        This callback is invoked when L1 evicts an entry due to LRU.
        Instead of deleting from L2/L3, we mark the entry as evicted so
        it can still be retrieved but with lower priority.

        Args:
            key: Cache key of evicted entry
            entry: CacheEntry that was evicted from L1
        """
        # Mark entry as evicted from L1
        evicted_entry = entry.model_copy(update={"evicted_from_l1": True})

        # Update L2/L3 with eviction state (don't delete)
        if self.l2_tier.enabled:
            try:
                self.l2_tier.put(key, evicted_entry)
            except Exception as exc:
                logger.warning(f"L2 eviction state update failed for {key}", error=str(exc))

        if self.l3_tier.enabled:
            try:
                self.l3_tier.put(key, evicted_entry)
            except Exception as exc:
                logger.warning(f"L3 eviction state update failed for {key}", error=str(exc))

        logger.debug(f"L1 eviction propagated: {key}")

    def get(self, key: str) -> CacheEntry | None:
        """Retrieve entry from cache with tier promotion.

        Checks L1 → L2 → L3 in order. Promotes entries to higher tiers on hit.
        Updates access_count and last_accessed on successful retrieval.

        Thread-safe: Uses lock to prevent race conditions during promotion and expiration.

        Args:
            key: Cache key to retrieve

        Returns:
            CacheEntry if found and not expired, None otherwise
        """
        with self._lock:
            # Try L1 first
            if self.l1_tier.enabled:
                entry = self.l1_tier.get(key)
                if entry:
                    if not entry.is_expired:
                        self.statistics.l1_stats.hits += 1
                        logger.debug(f"Cache hit (L1): {key}")
                        # Update access tracking (T073)
                        updated_entry = entry.model_copy(
                            update={
                                "access_count": entry.access_count + 1,
                                "last_accessed": datetime.now(timezone.utc),
                            }
                        )
                        self.l1_tier.put(key, updated_entry)
                        return updated_entry
                    else:
                        # Expired - delete from all tiers
                        logger.debug(f"Cache expired (TTL): {key}")
                        self._delete_internal(key)
                        self.statistics.l1_stats.evictions_ttl += 1
                        return None
                else:
                    self.statistics.l1_stats.misses += 1

            # Try L2
            if self.l2_tier.enabled:
                entry = self.l2_tier.get(key)
                if entry:
                    if not entry.is_expired:
                        self.statistics.l2_stats.hits += 1
                        logger.debug(f"Cache hit (L2): {key} - promoting to L1")
                        # Update access tracking (T073)
                        updated_entry = entry.model_copy(
                            update={
                                "access_count": entry.access_count + 1,
                                "last_accessed": datetime.now(timezone.utc),
                            }
                        )
                        # Promote to L1
                        self.l1_tier.put(key, updated_entry)
                        self.statistics.promotions += 1
                        return updated_entry
                    else:
                        logger.debug(f"Cache expired (TTL): {key}")
                        self._delete_internal(key)
                        self.statistics.l2_stats.evictions_ttl += 1
                        return None
                else:
                    self.statistics.l2_stats.misses += 1

            # Try L3
            if self.l3_tier.enabled:
                entry = self.l3_tier.get(key)
                if entry:
                    if not entry.is_expired:
                        self.statistics.l3_stats.hits += 1
                        logger.debug(f"Cache hit (L3): {key} - promoting to L1/L2")
                        # Update access tracking (T073)
                        updated_entry = entry.model_copy(
                            update={
                                "access_count": entry.access_count + 1,
                                "last_accessed": datetime.now(timezone.utc),
                            }
                        )
                        # Promote to L1 and L2
                        self.l1_tier.put(key, updated_entry)
                        self.l2_tier.put(key, updated_entry)
                        self.statistics.promotions += 2
                        return updated_entry
                    else:
                        logger.debug(f"Cache expired (TTL): {key}")
                        self._delete_internal(key)
                        self.statistics.l3_stats.evictions_ttl += 1
                        return None
                else:
                    self.statistics.l3_stats.misses += 1

            logger.debug(f"Cache miss (all tiers): {key}")
            return None

    def put(self, key: str, entry: CacheEntry) -> bool:
        """Store entry in all enabled tiers.

        Writes to all tiers for redundancy. Credentials are automatically
        redacted in logs.

        Thread-safe: Uses lock to ensure atomic writes across all tiers.

        Args:
            key: Cache key
            entry: CacheEntry to store

        Returns:
            True if stored in at least one tier, False otherwise
        """
        with self._lock:
            success = False

            # Redact credentials for logging
            log_entry = f"key={key}, url={entry.proxy_url}, source={entry.source}"
            if entry.username or entry.password:
                log_entry += ", credentials=***"

            logger.debug(f"Cache put: {log_entry}")

            # Store in L1
            if self.l1_tier.enabled:
                existing_l1 = key in self.l1_tier
                before_size = self.l1_tier.size()
                if self.l1_tier.put(key, entry):
                    after_size = self.l1_tier.size()
                    self.statistics.l1_stats.current_size = after_size
                    # Track LRU evictions when capacity is exceeded
                    if (
                        self.l1_tier.config.max_entries
                        and not existing_l1
                        and before_size >= self.l1_tier.config.max_entries
                    ):
                        self.statistics.l1_stats.evictions_lru += 1
                        # Track demotion when L1 evicts to lower tiers
                        self.statistics.demotions += 1
                    success = True

            # Store in L2
            if self.l2_tier.enabled:
                try:
                    if self.l2_tier.put(key, entry):
                        self.statistics.l2_stats.current_size = self.l2_tier.size()
                        success = True
                except Exception as exc:
                    logger.warning("L2 cache write failed", error=str(exc))
                    self.l2_tier.handle_failure(exc)

            # Store in L3
            if self.l3_tier.enabled:
                try:
                    if self.l3_tier.put(key, entry):
                        self.statistics.l3_stats.current_size = self.l3_tier.size()
                        success = True
                except Exception as exc:
                    logger.warning("L3 cache write failed", error=str(exc))
                    self.l3_tier.handle_failure(exc)

            return success

    def delete(self, key: str) -> bool:
        """Delete entry from all tiers.

        Thread-safe: Uses lock to ensure atomic deletion across all tiers.

        Args:
            key: Cache key to delete

        Returns:
            True if deleted from at least one tier, False if not found
        """
        with self._lock:
            return self._delete_internal(key)

    def _delete_internal(self, key: str) -> bool:
        """Internal delete without locking (assumes caller holds lock).

        Used by get() when expiring entries to avoid nested lock acquisition.

        Args:
            key: Cache key to delete

        Returns:
            True if deleted from at least one tier, False if not found
        """
        deleted = False

        logger.debug(f"Cache delete: {key}")

        if self.l1_tier.enabled and self.l1_tier.delete(key):
            deleted = True
            self.statistics.l1_stats.current_size = self.l1_tier.size()

        if self.l2_tier.enabled and self.l2_tier.delete(key):
            deleted = True
            self.statistics.l2_stats.current_size = self.l2_tier.size()

        if self.l3_tier.enabled and self.l3_tier.delete(key):
            deleted = True
            self.statistics.l3_stats.current_size = self.l3_tier.size()

        return deleted

    def _get_internal(self, key: str) -> CacheEntry | None:
        """Internal get without locking (assumes caller holds lock).

        Retrieves entry from tiers without promotion or access tracking.
        Used by invalidate_by_health() to avoid TOCTOU race conditions.

        Args:
            key: Cache key to retrieve

        Returns:
            CacheEntry if found, None otherwise (does not check expiration)
        """
        # Try L1 first
        if self.l1_tier.enabled:
            entry = self.l1_tier.get(key)
            if entry:
                return entry

        # Try L2
        if self.l2_tier.enabled:
            entry = self.l2_tier.get(key)
            if entry:
                return entry

        # Try L3
        if self.l3_tier.enabled:
            entry = self.l3_tier.get(key)
            if entry:
                return entry

        return None

    def _put_internal(self, key: str, entry: CacheEntry) -> bool:
        """Internal put without locking (assumes caller holds lock).

        Stores entry in all enabled tiers without lock acquisition.
        Used by invalidate_by_health() to avoid TOCTOU race conditions.

        Args:
            key: Cache key
            entry: CacheEntry to store

        Returns:
            True if stored in at least one tier, False otherwise
        """
        success = False

        # Store in L1
        if self.l1_tier.enabled:
            existing_l1 = key in self.l1_tier
            before_size = self.l1_tier.size()
            if self.l1_tier.put(key, entry):
                after_size = self.l1_tier.size()
                self.statistics.l1_stats.current_size = after_size
                # Track LRU evictions when capacity is exceeded
                if (
                    self.l1_tier.config.max_entries
                    and not existing_l1
                    and before_size >= self.l1_tier.config.max_entries
                ):
                    self.statistics.l1_stats.evictions_lru += 1
                    self.statistics.demotions += 1
                success = True

        # Store in L2
        if self.l2_tier.enabled:
            try:
                if self.l2_tier.put(key, entry):
                    self.statistics.l2_stats.current_size = self.l2_tier.size()
                    success = True
            except Exception as exc:
                logger.warning("L2 cache write failed", error=str(exc))
                self.l2_tier.handle_failure(exc)

        # Store in L3
        if self.l3_tier.enabled:
            try:
                if self.l3_tier.put(key, entry):
                    self.statistics.l3_stats.current_size = self.l3_tier.size()
                    success = True
            except Exception as exc:
                logger.warning("L3 cache write failed", error=str(exc))
                self.l3_tier.handle_failure(exc)

        return success

    def invalidate_by_health(self, key: str) -> None:
        """Mark proxy as unhealthy and evict if failure threshold reached.

        Increments the failure_count for the proxy and sets health_status to UNHEALTHY.
        If failure_count reaches the configured failure_threshold, the proxy is removed
        from all cache tiers.

        Thread-safe: Uses lock throughout entire operation to prevent TOCTOU race conditions.

        Args:
            key: Cache key to invalidate

        Note:
            - If health_check_invalidation is disabled, still tracks failures but doesn't evict
            - Logs at DEBUG level for failures, INFO level for evictions
            - Updates statistics for health-based evictions
            - RACE-001 fix: Holds lock throughout entire operation to prevent race between
              get and update/delete operations
        """
        with self._lock:
            # Get current entry using internal lock-free method (RACE-001 fix)
            entry = self._get_internal(key)
            if entry is None:
                logger.debug(f"Health invalidation failed: key not found: {key}")
                return

            # Increment failure count and mark unhealthy
            updated_entry = entry.model_copy(
                update={
                    "failure_count": entry.failure_count + 1,
                    "health_status": HealthStatus.UNHEALTHY,
                }
            )

            logger.debug(
                f"Health check failed: {key}, "
                f"failures={updated_entry.failure_count}/{self.config.failure_threshold}"
            )

            # Check if should evict (only if invalidation is enabled and threshold reached)
            should_evict = (
                self.config.health_check_invalidation
                and updated_entry.failure_count >= self.config.failure_threshold
            )

            if should_evict:
                # Check which tiers contain the entry before deleting
                in_l1 = self.l1_tier.enabled and key in self.l1_tier
                in_l2 = self.l2_tier.enabled and key in self.l2_tier
                in_l3 = self.l3_tier.enabled and key in self.l3_tier

                # Evict from all tiers (use internal method since we hold lock)
                self._delete_internal(key)
                logger.info(
                    f"Proxy evicted (health): {key}, failures={updated_entry.failure_count}"
                )

                # Update eviction statistics only for tiers that actually contained the entry
                if in_l1:
                    self.statistics.l1_stats.evictions_health += 1
                if in_l2:
                    self.statistics.l2_stats.evictions_health += 1
                if in_l3:
                    self.statistics.l3_stats.evictions_health += 1
            else:
                # Update entry with incremented failure_count using internal method
                # (RACE-001 fix: stay within lock to avoid race)
                self._put_internal(key, updated_entry)

    def clear(self) -> int:
        """Clear all entries from all tiers.

        Thread-safe: Uses lock to ensure atomic clearing across all tiers.

        Returns:
            Total number of entries cleared
        """
        with self._lock:
            total = 0

            if self.l1_tier.enabled:
                total += self.l1_tier.clear()
                self.statistics.l1_stats.current_size = 0

            if self.l2_tier.enabled:
                total += self.l2_tier.clear()
                self.statistics.l2_stats.current_size = 0

            if self.l3_tier.enabled:
                total += self.l3_tier.clear()
                self.statistics.l3_stats.current_size = 0

            logger.info(f"Cache cleared: {total} entries")
            return total

    def export_to_file(self, filepath: str) -> dict[str, int]:
        """Export all cache entries to a JSONL file.

        Args:
            filepath: Path to export file

        Returns:
            Dict with 'exported' and 'failed' counts
        """
        exported = 0
        failed = 0

        try:
            # Collect all unique keys from all tiers
            all_keys: set[str] = set()

            if self.l1_tier.enabled:
                all_keys.update(self.l1_tier._cache.keys())

            if self.l2_tier.enabled:
                all_keys.update(self.l2_tier.keys())

            if self.l3_tier.enabled:
                all_keys.update(self.l3_tier.keys())

            # Export each entry
            with open(filepath, "w") as f:
                for key in all_keys:
                    try:
                        entry = self.get(key)
                        if entry:
                            json.dump(entry.model_dump(mode="json"), f)
                            f.write("\n")
                            exported += 1
                    except Exception:
                        failed += 1

            logger.info(f"Exported {exported} entries to {filepath} ({failed} failed)")

        except Exception as e:
            logger.error(f"Export failed: {e}")
            raise

        return {"exported": exported, "failed": failed}

    @staticmethod
    def generate_cache_key(proxy_url: str) -> str:
        """Generate cache key from proxy URL.

        Uses SHA256 hash for consistent, URL-safe keys.

        Args:
            proxy_url: Proxy URL to hash

        Returns:
            Hex-encoded SHA256 hash (first 16 chars)
        """
        return hashlib.sha256(proxy_url.encode("utf-8")).hexdigest()[:16]

    def get_statistics(self) -> CacheStatistics:
        """Get current cache statistics.

        Returns:
            CacheStatistics with hit rates, sizes, and tier status
        """
        # Update current sizes
        if self.l1_tier.enabled:
            self.statistics.l1_stats.current_size = self.l1_tier.size()
        if self.l2_tier.enabled:
            self.statistics.l2_stats.current_size = self.l2_tier.size()
        if self.l3_tier.enabled:
            self.statistics.l3_stats.current_size = self.l3_tier.size()

        # Update degradation status
        self.statistics.l1_degraded = not self.l1_tier.enabled
        self.statistics.l2_degraded = not self.l2_tier.enabled
        self.statistics.l3_degraded = not self.l3_tier.enabled

        return self.statistics.model_copy(deep=True)

    def warm_from_file(self, file_path: str, ttl_override: int | None = None) -> dict[str, int]:
        """Load proxies from a file to pre-populate the cache.

        Supports JSON (array), JSONL (newline-delimited), and CSV formats.
        Invalid entries are skipped with warnings logged.

        Args:
            file_path: Path to file containing proxy data
            ttl_override: Optional TTL in seconds (overrides default_ttl_seconds)

        Returns:
            Dict with counts for loaded, skipped, and failed entries

        Raises:
            No exceptions - errors are logged and failure count is incremented
        """
        import csv
        import json

        path = Path(file_path)

        # Check file exists
        if not path.exists():
            logger.warning(f"Cache warming: file not found: {file_path}")
            return {"loaded": 0, "skipped": 0, "failed": 1}

        # Detect format by extension
        suffix = path.suffix.lower()
        loaded_count = 0
        skipped_count = 0
        failed_count = 0
        total_count = 0
        ttl_seconds = ttl_override if ttl_override is not None else self.config.default_ttl_seconds
        fetch_time = datetime.now(timezone.utc)
        expires_at = fetch_time + timedelta(seconds=ttl_seconds)

        logger.info(f"Cache warming: starting import from {file_path}")

        try:
            if suffix == ".json":
                # JSON array format
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                    if not isinstance(data, list):
                        logger.warning(f"Cache warming: JSON file must contain array: {file_path}")
                        return {"loaded": 0, "skipped": 0, "failed": 1}
                    total_count = len(data)
                    logger.debug(f"Cache warming: found {total_count} entries in JSON array")
                    for idx, item in enumerate(data, start=1):
                        if self._warm_entry(item, fetch_time, expires_at, ttl_seconds):
                            loaded_count += 1
                            # Progress logging every 1000 proxies
                            if loaded_count % 1000 == 0:
                                logger.info(
                                    f"Cache warming: loaded {loaded_count}/{total_count} proxies..."
                                )
                        else:
                            skipped_count += 1

            elif suffix == ".jsonl":
                # JSONL (newline-delimited JSON) format
                with open(path, encoding="utf-8") as f:
                    for line_num, line in enumerate(f, start=1):
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            item = json.loads(line)
                            if self._warm_entry(item, fetch_time, expires_at, ttl_seconds):
                                loaded_count += 1
                                # Progress logging every 1000 proxies
                                if loaded_count % 1000 == 0:
                                    logger.info(f"Cache warming: loaded {loaded_count} proxies...")
                            else:
                                skipped_count += 1
                        except json.JSONDecodeError as e:
                            logger.warning(
                                f"Cache warming: invalid JSON on line {line_num} in {file_path}: {e}"
                            )
                            failed_count += 1

            elif suffix == ".csv":
                # CSV format with header detection
                with open(path, encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if self._warm_entry(row, fetch_time, expires_at, ttl_seconds):
                            loaded_count += 1
                            # Progress logging every 1000 proxies
                            if loaded_count % 1000 == 0:
                                logger.info(f"Cache warming: loaded {loaded_count} proxies...")
                        else:
                            skipped_count += 1

            else:
                logger.warning(f"Cache warming: unsupported format '{suffix}': {file_path}")
                return {"loaded": 0, "skipped": 0, "failed": 1}

        except json.JSONDecodeError as e:
            logger.warning(f"Cache warming: invalid JSON format in {file_path}: {e}")
            return {"loaded": 0, "skipped": 0, "failed": failed_count + 1}
        except Exception as e:
            logger.error(f"Cache warming: error loading from {file_path}: {e}")
            return {"loaded": loaded_count, "skipped": skipped_count, "failed": failed_count + 1}

        if loaded_count > 0:
            logger.info(f"Cache warming: loaded {loaded_count} proxies from {file_path}")

        return {"loaded": loaded_count, "skipped": skipped_count, "failed": failed_count}

    def _warm_entry(
        self,
        data: dict[str, object],
        fetch_time: datetime,
        expires_at: datetime,
        ttl_seconds: int,
    ) -> bool:
        """Parse and load a single proxy entry into cache.

        Args:
            data: Dictionary with proxy data (must have 'proxy_url')
            fetch_time: When the entry was fetched
            expires_at: When the entry expires
            ttl_seconds: TTL in seconds

        Returns:
            True if entry was successfully added, False if skipped
        """
        from pydantic import SecretStr

        # Validate required field
        if "proxy_url" not in data:
            logger.warning("Cache warming: skipping entry without 'proxy_url'")
            return False

        proxy_url = data["proxy_url"]
        if not proxy_url or not isinstance(proxy_url, str):
            logger.warning(f"Cache warming: invalid proxy_url: {proxy_url}")
            return False

        # Build entry with credential encryption
        username = data.get("username")
        password = data.get("password")
        source = data.get("source", "warmed")

        cache_key = str(data.get("key") or self.generate_cache_key(proxy_url))

        try:
            entry = CacheEntry(
                key=cache_key,
                proxy_url=proxy_url,
                username=SecretStr(str(username)) if username else None,
                password=SecretStr(str(password)) if password else None,
                source=str(source),
                fetch_time=fetch_time,
                expires_at=expires_at,
                ttl_seconds=ttl_seconds,
                health_status=HealthStatus.UNKNOWN,
                access_count=0,
                last_accessed=fetch_time,
            )

            # Add to cache
            self.put(entry.key, entry)
            return True

        except Exception as e:
            logger.warning(f"Cache warming: failed to create entry for {proxy_url}: {e}")
            return False
