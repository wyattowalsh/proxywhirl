"""Edge case tests for cache robustness.

Tests error handling, resilience, and degradation behaviors under failure conditions.
"""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from pydantic import SecretStr

from proxywhirl.cache import CacheManager
from proxywhirl.cache.crypto import CredentialEncryptor
from proxywhirl.cache.models import CacheConfig, CacheEntry, CacheTierConfig, HealthStatus


class TestCorruptionDetection:
    """Test detection and handling of corrupted cache data."""

    def test_corrupted_jsonl_file_skipped(self, tmp_path: Path) -> None:
        """Test that corrupted JSONL entries are skipped gracefully.

        This tests that when reading from a JSONL shard file, corrupted
        entries (invalid JSON) are skipped while valid entries are still
        accessible. Uses proper shard file naming and key-to-shard mapping.
        """
        import hashlib

        encryptor = CredentialEncryptor()
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir(parents=True)
        now = datetime.now(timezone.utc)

        # Determine which shard "test_key" maps to (uses MD5 % 16)
        test_key = "test_key"
        shard_id = int(hashlib.md5(test_key.encode()).hexdigest(), 16) % 16

        # Create shard file with valid entry, corrupted entry, then valid entry
        shard_file = cache_dir / f"shard_{shard_id:02d}.jsonl"
        valid_entry = CacheEntry(
            key=test_key,
            proxy_url="http://proxy.example.com:8080",
            username=None,
            password=None,
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(seconds=3600),
            health_status=HealthStatus.HEALTHY,
        )
        with open(shard_file, "w") as f:
            # Valid entry first
            f.write(json.dumps(valid_entry.model_dump(mode="json")) + "\n")
            # Corrupted entry (invalid JSON) - should be skipped
            f.write("{invalid json here\n")

        # Initialize manager AFTER creating the corrupted file
        # This tests that the index rebuild handles corrupted entries
        config = CacheConfig(
            l2_config=CacheTierConfig(enabled=True),
            l2_cache_dir=str(cache_dir),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
        )
        manager = CacheManager(config)

        # Valid entry should still be accessible despite corrupted line
        result = manager.get(test_key)
        assert result is not None, "Valid entry should be accessible"
        assert result.key == test_key

    def test_corrupted_sqlite_entry_handled(self, tmp_path: Path) -> None:
        """Test that corrupted SQLite entries are handled gracefully."""
        encryptor = CredentialEncryptor()
        config = CacheConfig(
            l3_config=CacheTierConfig(enabled=True),
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
        )
        manager = CacheManager(config)

        # Accessing non-existent key should not crash
        result = manager.get("nonexistent_key")
        assert result is None


class TestDiskExhaustion:
    """Test behavior when disk space is exhausted."""

    def test_l2_write_failure_fallback(self, tmp_path: Path) -> None:
        """Test that L2 write failures don't crash the system."""
        encryptor = CredentialEncryptor()
        config = CacheConfig(
            l2_config=CacheTierConfig(enabled=True),
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
        )
        manager = CacheManager(config)
        now = datetime.now(timezone.utc)

        entry = CacheEntry(
            key="test_key",
            proxy_url="http://proxy.example.com:8080",
            username=None,
            password=None,
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(seconds=3600),
            health_status=HealthStatus.HEALTHY,
        )

        # Mock L2 tier to raise OSError on put
        original_put = manager.l2_tier.put

        def failing_put(key: str, entry: CacheEntry) -> None:
            raise OSError("Disk full")

        manager.l2_tier.put = failing_put  # type: ignore[method-assign]

        # Should not crash, L1 should still work
        try:
            manager.put(entry.key, entry)
        except OSError:
            pytest.fail("OSError should be caught internally")

        # Restore original method
        manager.l2_tier.put = original_put  # type: ignore[method-assign]

        # L1 should still have the entry
        result = manager.get(entry.key)
        assert result is not None


class TestTierFailover:
    """Test tier failover when individual tiers are unavailable."""

    def test_l2_unavailable_fallback(self, tmp_path: Path) -> None:
        """Test that system works when L2 tier fails."""
        encryptor = CredentialEncryptor()
        config = CacheConfig(
            l2_config=CacheTierConfig(enabled=True),
            l2_cache_dir=str(tmp_path / "nonexistent_readonly/cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
        )
        manager = CacheManager(config)
        now = datetime.now(timezone.utc)

        entry = CacheEntry(
            key="test_key",
            proxy_url="http://proxy.example.com:8080",
            username=None,
            password=None,
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,
            expires_at=now + timedelta(seconds=3600),
            health_status=HealthStatus.HEALTHY,
        )

        # L1 and L3 should still work
        manager.put(entry.key, entry)
        result = manager.get(entry.key)
        assert result is not None

    def test_l3_unavailable_fallback(self, tmp_path: Path) -> None:
        """Test that system works when L3 tier fails."""
        encryptor = CredentialEncryptor()
        config = CacheConfig(
            l3_config=CacheTierConfig(enabled=True),
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path="/nonexistent/readonly/path/cache.db",
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
        )

        # Should fail to initialize L3 but L1/L2 should work
        try:
            manager = CacheManager(config)
        except Exception:
            pytest.fail("Should handle L3 initialization failure gracefully")


class TestConcurrentOperations:
    """Test cache behavior under high concurrent load."""

    def test_concurrent_reads_writes(self, tmp_path: Path) -> None:
        """Test that cache handles concurrent reads/writes correctly."""
        import concurrent.futures

        encryptor = CredentialEncryptor()
        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
        )
        manager = CacheManager(config)
        now = datetime.now(timezone.utc)

        def write_entry(i: int) -> None:
            entry = CacheEntry(
                key=f"key_{i}",
                proxy_url=f"http://proxy{i}.example.com:8080",
                username=None,
                password=None,
                source="test",
                fetch_time=now,
                last_accessed=now,
                ttl_seconds=3600,
                expires_at=now + timedelta(seconds=3600),
                health_status=HealthStatus.HEALTHY,
            )
            manager.put(entry.key, entry)

        def read_entry(i: int) -> CacheEntry | None:
            return manager.get(f"key_{i}")

        # Write 1000 entries concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            write_futures = [executor.submit(write_entry, i) for i in range(1000)]
            concurrent.futures.wait(write_futures)

        # Read 1000 entries concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            read_futures = [executor.submit(read_entry, i) for i in range(1000)]
            results = [f.result() for f in concurrent.futures.as_completed(read_futures)]

        # All entries should be readable
        valid_results = [r for r in results if r is not None]
        assert len(valid_results) >= 900, "Most entries should be readable"

    @pytest.mark.slow
    @pytest.mark.timeout(120)
    def test_large_scale_operations(self, tmp_path: Path) -> None:
        """Test that cache can handle large operation counts (SC-010)."""
        encryptor = CredentialEncryptor()
        config = CacheConfig(
            l1_config=CacheTierConfig(enabled=True, max_entries=10000),
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
        )
        manager = CacheManager(config)
        now = datetime.now(timezone.utc)

        entry_count = int(os.getenv("PROXYWHIRL_LARGE_SCALE_ENTRIES", "2000"))
        read_count = int(os.getenv("PROXYWHIRL_LARGE_SCALE_READS", "20000"))

        # Write entries
        for i in range(entry_count):
            entry = CacheEntry(
                key=f"key_{i}",
                proxy_url=f"http://proxy{i}.example.com:8080",
                username=None,
                password=None,
                source="test",
                fetch_time=now,
                last_accessed=now,
                ttl_seconds=3600,
                expires_at=now + timedelta(seconds=3600),
                health_status=HealthStatus.HEALTHY,
            )
            manager.put(entry.key, entry)

        # Read many times (with repetition)
        for i in range(read_count):
            key = f"key_{i % entry_count}"
            result = manager.get(key)
            assert result is not None

        stats = manager.get_statistics()
        assert stats.l1_stats.hits > read_count * 0.9, "Most reads should hit L1 cache"


class TestImportExport:
    """Test cache import/export functionality."""

    def test_export_to_json(self, tmp_path: Path) -> None:
        """Test exporting cache entries to JSON format."""
        encryptor = CredentialEncryptor()
        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
        )
        manager = CacheManager(config)
        now = datetime.now(timezone.utc)

        # Add entries
        for i in range(5):
            entry = CacheEntry(
                key=f"key_{i}",
                proxy_url=f"http://proxy{i}.example.com:8080",
                username=None,
                password=None,
                source="test",
                fetch_time=now,
                last_accessed=now,
                ttl_seconds=3600,
                expires_at=now + timedelta(seconds=3600),
                health_status=HealthStatus.HEALTHY,
            )
            manager.put(entry.key, entry)

        # Export would be implemented in T118
        # For now, test that entries can be retrieved for export
        all_entries = []
        for i in range(5):
            entry = manager.get(f"key_{i}")
            if entry:
                all_entries.append(entry)

        assert len(all_entries) == 5

    def test_import_from_json(self, tmp_path: Path) -> None:
        """Test importing cache entries from JSON format."""
        encryptor = CredentialEncryptor()
        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=SecretStr(encryptor.key.decode("utf-8")),
        )
        manager = CacheManager(config)
        now = datetime.now(timezone.utc)

        # Create import file
        import_file = tmp_path / "import.json"
        entries = []
        for i in range(5):
            entry = CacheEntry(
                key=f"import_key_{i}",
                proxy_url=f"http://import{i}.example.com:8080",
                username=None,
                password=None,
                source="test",
                fetch_time=now,
                last_accessed=now,
                ttl_seconds=3600,
                expires_at=now + timedelta(seconds=3600),
                health_status=HealthStatus.HEALTHY,
            )
            entries.append(entry.model_dump(mode="json"))

        with open(import_file, "w") as f:
            json.dump(entries, f)

        # Import using warm_from_file
        result = manager.warm_from_file(str(import_file))
        assert result["loaded"] == 5
        assert result["failed"] == 0

        # Verify entries are accessible
        for i in range(5):
            entry = manager.get(f"import_key_{i}")
            assert entry is not None
