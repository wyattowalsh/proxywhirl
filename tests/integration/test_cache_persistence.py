"""Integration tests for cache persistence.

Tests end-to-end persistence scenarios including system restarts,
cross-tier synchronization, and data durability.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from pydantic import SecretStr

from proxywhirl.cache_models import CacheConfig, CacheEntry, HealthStatus


def test_persistence_across_restarts(tmp_path: Path) -> None:
    """Test that cached proxies persist across system restarts.

    This tests the core User Story 1 requirement: persistent caching.
    """
    from proxywhirl.cache import CacheManager
    from proxywhirl.cache.crypto import CredentialEncryptor

    # Generate shared encryption key for both sessions
    encryptor = CredentialEncryptor()
    encryption_key = SecretStr(encryptor.key.decode("utf-8"))

    config = CacheConfig(
        l2_cache_dir=str(tmp_path / "cache"),
        l3_database_path=str(tmp_path / "cache.db"),
        encryption_key=encryption_key,
    )

    # Create entry
    now = datetime.now(timezone.utc)
    entry = CacheEntry(
        key="persistent_key",
        proxy_url="http://proxy.example.com:8080",
        username=SecretStr("user"),
        password=SecretStr("pass"),
        source="test",
        fetch_time=now,
        last_accessed=now,
        ttl_seconds=7200,
        expires_at=now + timedelta(seconds=7200),
        health_status=HealthStatus.HEALTHY,
    )

    # First session: cache proxy
    manager1 = CacheManager(config)
    manager1.put(entry.key, entry)
    del manager1  # Simulate shutdown

    # Second session: verify persistence
    manager2 = CacheManager(config)
    retrieved = manager2.get(entry.key)

    assert retrieved is not None, "Entry should persist across restarts"
    assert retrieved.key == entry.key
    assert retrieved.proxy_url == entry.proxy_url
    assert retrieved.username is not None
    assert retrieved.username.get_secret_value() == "user"


def test_update_existing_entries(tmp_path: Path) -> None:
    """Test updating existing cache entries with new metadata.

    Verifies that updates work correctly across all tiers.
    """
    from proxywhirl.cache import CacheManager
    from proxywhirl.cache.crypto import CredentialEncryptor

    # Generate shared encryption key
    encryptor = CredentialEncryptor()
    encryption_key = SecretStr(encryptor.key.decode("utf-8"))

    config = CacheConfig(
        l2_cache_dir=str(tmp_path / "cache"),
        l3_database_path=str(tmp_path / "cache.db"),
        encryption_key=encryption_key,
    )
    manager = CacheManager(config)

    # Create initial entry
    now = datetime.now(timezone.utc)
    entry1 = CacheEntry(
        key="update_test",
        proxy_url="http://proxy.example.com:8080",
        username=None,
        password=None,
        source="test",
        fetch_time=now,
        last_accessed=now,
        access_count=1,
        ttl_seconds=3600,
        expires_at=now + timedelta(seconds=3600),
        health_status=HealthStatus.HEALTHY,
    )
    manager.put(entry1.key, entry1)

    # Update entry with new metadata
    entry2 = CacheEntry(
        key="update_test",
        proxy_url="http://proxy.example.com:8080",
        username=None,
        password=None,
        source="test",
        fetch_time=now,
        last_accessed=now + timedelta(seconds=10),
        access_count=5,  # Updated
        ttl_seconds=3600,
        expires_at=now + timedelta(seconds=3600),
        health_status=HealthStatus.UNHEALTHY,  # Updated
    )
    manager.put(entry2.key, entry2)

    # Retrieve and verify update (get increments access_count by 1)
    retrieved = manager.get(entry2.key)
    assert retrieved is not None
    assert retrieved.access_count == 6, "Access count should be updated (5 + 1 from get)"
    assert retrieved.health_status == HealthStatus.UNHEALTHY, "Health status should be updated"
