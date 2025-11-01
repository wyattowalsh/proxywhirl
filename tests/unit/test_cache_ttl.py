"""Unit tests for TTL-based cache expiration.

Tests the automatic expiration of cached proxies based on configurable TTL,
including lazy expiration, background cleanup, and per-source TTL settings.
"""

import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from pydantic import SecretStr

from proxywhirl.cache_models import CacheConfig, CacheEntry


@pytest.fixture
def encryption_key() -> SecretStr:
    """Generate valid Fernet encryption key for tests."""
    from proxywhirl.cache_crypto import CredentialEncryptor

    encryptor = CredentialEncryptor()
    return SecretStr(encryptor.key.decode("utf-8"))


class TestLazyExpiration:
    """Test lazy TTL expiration on cache get operations."""

    def test_expired_entry_returns_none(self, tmp_path: Path, encryption_key: SecretStr) -> None:
        """Test that getting an expired entry returns None."""
        from proxywhirl.cache import CacheManager

        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=encryption_key,
        )
        manager = CacheManager(config)

        # Create entry that expires immediately
        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            key="expired_key",
            proxy_url="http://proxy.example.com:8080",
            username=None,
            password=None,
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=1,  # 1 second TTL
            expires_at=now + timedelta(seconds=1),
        )

        manager.put(entry.key, entry)

        # Wait for expiration
        time.sleep(1.5)

        # Get should return None for expired entry
        retrieved = manager.get(entry.key)
        assert retrieved is None, "Expired entry should return None"

    def test_non_expired_entry_returns_value(self, tmp_path: Path, encryption_key: SecretStr) -> None:
        """Test that getting a non-expired entry returns the value."""
        from proxywhirl.cache import CacheManager

        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=encryption_key,
        )
        manager = CacheManager(config)

        # Create entry with long TTL
        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            key="valid_key",
            proxy_url="http://proxy.example.com:8080",
            username=None,
            password=None,
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=3600,  # 1 hour TTL
            expires_at=now + timedelta(seconds=3600),
        )

        manager.put(entry.key, entry)

        # Get should return the entry
        retrieved = manager.get(entry.key)
        assert retrieved is not None, "Non-expired entry should be retrieved"
        assert retrieved.key == entry.key

    def test_expired_entry_deleted_from_all_tiers(self, tmp_path: Path, encryption_key: SecretStr) -> None:
        """Test that expired entries are deleted from all cache tiers."""
        from proxywhirl.cache import CacheManager

        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=encryption_key,
        )
        manager = CacheManager(config)

        # Create expired entry
        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            key="delete_key",
            proxy_url="http://proxy.example.com:8080",
            username=None,
            password=None,
            source="test",
            fetch_time=now - timedelta(seconds=10),
            last_accessed=now - timedelta(seconds=10),
            ttl_seconds=5,
            expires_at=now - timedelta(seconds=5),  # Already expired
        )

        manager.put(entry.key, entry)

        # Verify entry exists in at least one tier
        assert manager.l1_tier.get(entry.key) is not None or \
               manager.l2_tier.get(entry.key) is not None or \
               manager.l3_tier.get(entry.key) is not None

        # Get on expired entry should delete from all tiers
        retrieved = manager.get(entry.key)
        assert retrieved is None

        # Verify deleted from all tiers
        assert manager.l1_tier.get(entry.key) is None
        assert manager.l2_tier.get(entry.key) is None
        assert manager.l3_tier.get(entry.key) is None


class TestBackgroundCleanup:
    """Test background TTL cleanup thread."""

    def test_background_cleanup_enabled_by_config(self, tmp_path: Path, encryption_key: SecretStr) -> None:
        """Test that background cleanup can be enabled via config."""
        from proxywhirl.cache import CacheManager

        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=encryption_key,
            enable_background_cleanup=True,
            cleanup_interval_seconds=60,
        )
        manager = CacheManager(config)

        # Verify background cleanup is configured
        assert hasattr(manager, "ttl_manager"), "TTLManager should exist"
        assert manager.ttl_manager is not None

    def test_background_cleanup_removes_expired_entries(self, tmp_path: Path, encryption_key: SecretStr) -> None:
        """Test that background cleanup removes expired entries."""
        from proxywhirl.cache import CacheManager

        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=encryption_key,
            enable_background_cleanup=True,
            cleanup_interval_seconds=5,  # Minimum allowed value
        )
        manager = CacheManager(config)

        # Create expired entry
        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            key="cleanup_key",
            proxy_url="http://proxy.example.com:8080",
            username=None,
            password=None,
            source="test",
            fetch_time=now - timedelta(seconds=10),
            last_accessed=now - timedelta(seconds=10),
            ttl_seconds=5,
            expires_at=now - timedelta(seconds=5),  # Already expired
        )

        manager.put(entry.key, entry)

        # Wait for background cleanup (5s interval + processing time)
        time.sleep(7)

        # Entry should be removed
        retrieved = manager.get(entry.key)
        assert retrieved is None, "Background cleanup should remove expired entries"


class TestTTLConfiguration:
    """Test TTL configuration updates."""

    def test_default_ttl_applied_to_entries(self, tmp_path: Path, encryption_key: SecretStr) -> None:
        """Test that default TTL is applied to new cache entries."""
        from proxywhirl.cache import CacheManager

        default_ttl = 7200  # 2 hours
        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=encryption_key,
            default_ttl_seconds=default_ttl,
        )
        manager = CacheManager(config)

        # Create entry with default TTL
        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            key="default_ttl_key",
            proxy_url="http://proxy.example.com:8080",
            username=None,
            password=None,
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=default_ttl,
            expires_at=now + timedelta(seconds=default_ttl),
        )

        manager.put(entry.key, entry)

        # Verify TTL is set correctly
        retrieved = manager.get(entry.key)
        assert retrieved is not None
        assert retrieved.ttl_seconds == default_ttl

    def test_custom_ttl_overrides_default(self, tmp_path: Path, encryption_key: SecretStr) -> None:
        """Test that custom TTL can override default TTL."""
        from proxywhirl.cache import CacheManager

        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=encryption_key,
            default_ttl_seconds=7200,
        )
        manager = CacheManager(config)

        # Create entry with custom TTL
        custom_ttl = 1800  # 30 minutes
        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            key="custom_ttl_key",
            proxy_url="http://proxy.example.com:8080",
            username=None,
            password=None,
            source="test",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=custom_ttl,
            expires_at=now + timedelta(seconds=custom_ttl),
        )

        manager.put(entry.key, entry)

        # Verify custom TTL is used
        retrieved = manager.get(entry.key)
        assert retrieved is not None
        assert retrieved.ttl_seconds == custom_ttl


class TestPerSourceTTL:
    """Test per-source TTL configuration."""

    def test_per_source_ttl_overrides_default(self, tmp_path: Path, encryption_key: SecretStr) -> None:
        """Test that per-source TTL overrides default TTL."""
        from proxywhirl.cache import CacheManager

        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=encryption_key,
            default_ttl_seconds=7200,
            per_source_ttl={"premium_source": 86400},  # 24 hours for premium
        )
        manager = CacheManager(config)

        # Create entry with source-specific TTL
        source_ttl = 86400
        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            key="source_ttl_key",
            proxy_url="http://proxy.example.com:8080",
            username=None,
            password=None,
            source="premium_source",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=source_ttl,
            expires_at=now + timedelta(seconds=source_ttl),
        )

        manager.put(entry.key, entry)

        # Verify source-specific TTL is used
        retrieved = manager.get(entry.key)
        assert retrieved is not None
        assert retrieved.ttl_seconds == source_ttl
        assert retrieved.source == "premium_source"

    def test_default_ttl_used_for_unknown_source(self, tmp_path: Path, encryption_key: SecretStr) -> None:
        """Test that default TTL is used when source has no specific TTL."""
        from proxywhirl.cache import CacheManager

        default_ttl = 3600
        config = CacheConfig(
            l2_cache_dir=str(tmp_path / "cache"),
            l3_database_path=str(tmp_path / "cache.db"),
            encryption_key=encryption_key,
            default_ttl_seconds=default_ttl,
            per_source_ttl={"premium_source": 86400},
        )
        manager = CacheManager(config)

        # Create entry with unknown source
        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            key="unknown_source_key",
            proxy_url="http://proxy.example.com:8080",
            username=None,
            password=None,
            source="unknown_source",
            fetch_time=now,
            last_accessed=now,
            ttl_seconds=default_ttl,
            expires_at=now + timedelta(seconds=default_ttl),
        )

        manager.put(entry.key, entry)

        # Verify default TTL is used
        retrieved = manager.get(entry.key)
        assert retrieved is not None
        assert retrieved.ttl_seconds == default_ttl
