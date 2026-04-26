"""
Benchmark tests for L2 cache performance with SQLite backend.

Tests verify that the optimized SQLite-based L2 cache achieves <10ms read
performance for 10K+ entries, compared to the old JSONL implementation.
"""

import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from proxywhirl.cache.models import CacheEntry, CacheTierConfig
from proxywhirl.cache.tiers import DiskCacheTier, TierType


@pytest.fixture
def tier_config() -> CacheTierConfig:
    """Create a basic tier configuration."""
    return CacheTierConfig(
        enabled=True,
        max_entries=None,  # No limit for benchmarking
        ttl_seconds=3600,
    )


@pytest.fixture
def large_dataset() -> list[CacheEntry]:
    """Create a large dataset of 10K cache entries for benchmarking."""
    entries = []
    now = datetime.now(timezone.utc)

    for i in range(10000):
        entry = CacheEntry(
            key=f"bench_key_{i:05d}",
            proxy_url=f"http://proxy{i}.example.com:8080",
            source="benchmark",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(hours=1),
        )
        entries.append(entry)

    return entries


class TestL2CachePerformance:
    """Performance benchmarks for optimized L2 cache."""

    def test_write_10k_entries_performance(
        self, tier_config: CacheTierConfig, tmp_path: Path, large_dataset: list[CacheEntry]
    ) -> None:
        """Benchmark: Write 10K entries to L2 cache.

        Acceptance: Should complete in reasonable time (faster than JSONL).
        """
        tier = DiskCacheTier(tier_config, TierType.L2_FILE, tmp_path)

        start_time = time.perf_counter()

        for entry in large_dataset:
            tier.put(entry.key, entry)

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Verify all entries written
        assert tier.size() == 10000

        print(f"\n✓ Write 10K entries: {elapsed_ms:.2f}ms ({elapsed_ms / 10000:.3f}ms per entry)")

    def test_read_10k_entries_performance(
        self, tier_config: CacheTierConfig, tmp_path: Path, large_dataset: list[CacheEntry]
    ) -> None:
        """Benchmark: Read performance with 10K entries in cache.

        Acceptance: Individual reads should average <10ms with 10K entries.
        This is the key optimization - SQLite indexed lookups vs JSONL scans.
        """
        tier = DiskCacheTier(tier_config, TierType.L2_FILE, tmp_path)

        # Populate cache
        for entry in large_dataset:
            tier.put(entry.key, entry)

        assert tier.size() == 10000

        # Benchmark reads - sample 100 random keys
        sample_keys = [f"bench_key_{i:05d}" for i in range(0, 10000, 100)]

        read_times = []
        for key in sample_keys:
            start = time.perf_counter()
            result = tier.get(key)
            elapsed_ms = (time.perf_counter() - start) * 1000
            read_times.append(elapsed_ms)
            assert result is not None
            assert result.key == key

        avg_read_ms = sum(read_times) / len(read_times)
        max_read_ms = max(read_times)
        min_read_ms = min(read_times)

        print("\n✓ Read performance (10K entries):")
        print(f"  Average: {avg_read_ms:.3f}ms")
        print(f"  Min: {min_read_ms:.3f}ms")
        print(f"  Max: {max_read_ms:.3f}ms")

        # ACCEPTANCE CRITERIA: Average read time should be <10ms
        assert avg_read_ms < 10.0, f"Average read time {avg_read_ms:.3f}ms exceeds 10ms threshold"

    def test_cleanup_expired_10k_entries_performance(
        self, tier_config: CacheTierConfig, tmp_path: Path
    ) -> None:
        """Benchmark: Cleanup of expired entries with 10K total entries.

        Acceptance: Bulk cleanup should be fast using indexed SQL DELETE.
        """
        tier = DiskCacheTier(tier_config, TierType.L2_FILE, tmp_path)

        now = datetime.now(timezone.utc)

        # Create 5K expired and 5K valid entries
        for i in range(5000):
            # Expired entries
            expired_entry = CacheEntry(
                key=f"expired_{i:05d}",
                proxy_url=f"http://expired{i}.example.com:8080",
                source="benchmark",
                fetch_time=now - timedelta(hours=2),
                last_accessed=now - timedelta(hours=2),
                ttl_seconds=3600,
                expires_at=now - timedelta(hours=1),  # Already expired
            )
            tier.put(expired_entry.key, expired_entry)

            # Valid entries
            valid_entry = CacheEntry(
                key=f"valid_{i:05d}",
                proxy_url=f"http://valid{i}.example.com:8080",
                source="benchmark",
                fetch_time=now,
                last_accessed=now,
                ttl_seconds=3600,
                expires_at=now + timedelta(hours=1),
            )
            tier.put(valid_entry.key, valid_entry)

        assert tier.size() == 10000

        # Benchmark cleanup
        start_time = time.perf_counter()
        removed = tier.cleanup_expired()
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        assert removed == 5000
        assert tier.size() == 5000

        print(f"\n✓ Cleanup 5K expired (from 10K total): {elapsed_ms:.2f}ms")

        # Cleanup should be very fast with indexed SQL DELETE
        assert elapsed_ms < 100.0, f"Cleanup took {elapsed_ms:.2f}ms, should be <100ms"

    def test_size_operation_performance(
        self, tier_config: CacheTierConfig, tmp_path: Path, large_dataset: list[CacheEntry]
    ) -> None:
        """Benchmark: Size operation with 10K entries.

        Acceptance: COUNT(*) query should be near-instant.
        """
        tier = DiskCacheTier(tier_config, TierType.L2_FILE, tmp_path)

        # Populate cache
        for entry in large_dataset:
            tier.put(entry.key, entry)

        # Benchmark size operation
        start_time = time.perf_counter()
        size = tier.size()
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        assert size == 10000

        print(f"\n✓ Size operation (10K entries): {elapsed_ms:.3f}ms")

        # Should be essentially instant
        assert elapsed_ms < 10.0

    def test_keys_operation_performance(
        self, tier_config: CacheTierConfig, tmp_path: Path, large_dataset: list[CacheEntry]
    ) -> None:
        """Benchmark: Keys operation with 10K entries.

        Acceptance: SELECT key query should complete quickly.
        """
        tier = DiskCacheTier(tier_config, TierType.L2_FILE, tmp_path)

        # Populate cache
        for entry in large_dataset:
            tier.put(entry.key, entry)

        # Benchmark keys operation
        start_time = time.perf_counter()
        keys = tier.keys()
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        assert len(keys) == 10000

        print(f"\n✓ Keys operation (10K entries): {elapsed_ms:.2f}ms")

        # Should complete quickly
        assert elapsed_ms < 100.0

    def test_database_file_size(
        self, tier_config: CacheTierConfig, tmp_path: Path, large_dataset: list[CacheEntry]
    ) -> None:
        """Verify SQLite database file size is reasonable for 10K entries."""
        tier = DiskCacheTier(tier_config, TierType.L2_FILE, tmp_path)

        # Populate cache
        for entry in large_dataset:
            tier.put(entry.key, entry)

        # Check database file size
        db_size_bytes = tier.db_path.stat().st_size
        db_size_mb = db_size_bytes / (1024 * 1024)

        print(f"\n✓ Database size for 10K entries: {db_size_mb:.2f} MB")

        # Should be reasonable - SQLite is efficient
        # Rough estimate: ~1-5 MB for 10K simple entries
        assert db_size_mb < 50.0, f"Database size {db_size_mb:.2f}MB seems too large"


class TestL2CacheMigration:
    """Test migration from JSONL to SQLite."""

    def test_migration_from_jsonl(self, tier_config: CacheTierConfig, tmp_path: Path) -> None:
        """Test migration utility can import JSONL files."""
        # Create mock JSONL file with sample entries
        jsonl_dir = tmp_path / "old_cache"
        jsonl_dir.mkdir()

        shard_file = jsonl_dir / "shard_te.jsonl"

        now = datetime.now(timezone.utc)
        entries_data = []

        for i in range(100):
            entry_dict = {
                "key": f"test_key_{i}",
                "proxy_url": f"http://proxy{i}.example.com:8080",
                "source": "test_source",
                "fetch_time": now.isoformat(),
                "last_accessed": now.isoformat(),
                "access_count": 0,
                "ttl_seconds": 3600,
                "expires_at": (now + timedelta(hours=1)).isoformat(),
                "health_status": "unknown",
                "failure_count": 0,
            }
            entries_data.append(entry_dict)

        # Write JSONL file
        import json

        with open(shard_file, "w") as f:
            for entry_dict in entries_data:
                f.write(json.dumps(entry_dict) + "\n")

        # Create new SQLite-based tier in different directory
        sqlite_dir = tmp_path / "new_cache"
        sqlite_dir.mkdir()

        tier = DiskCacheTier(tier_config, TierType.L2_FILE, sqlite_dir)

        # Run migration
        migrated = tier.migrate_from_jsonl(jsonl_dir)

        assert migrated == 100
        assert tier.size() == 100

        # Verify entries are accessible
        for i in range(100):
            entry = tier.get(f"test_key_{i}")
            assert entry is not None
            assert entry.proxy_url == f"http://proxy{i}.example.com:8080"

        print(f"\n✓ Successfully migrated {migrated} entries from JSONL to SQLite")
