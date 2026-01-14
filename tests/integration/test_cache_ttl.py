"""Integration tests for TTL-based cache expiration.

Tests end-to-end TTL expiration scenarios including timing guarantees
and expired proxy behavior.
"""

import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from pydantic import SecretStr

from proxywhirl.cache.models import CacheConfig, CacheEntry


@pytest.fixture
def encryption_key() -> SecretStr:
    """Generate valid Fernet encryption key for tests."""
    from proxywhirl.cache.crypto import CredentialEncryptor

    encryptor = CredentialEncryptor()
    return SecretStr(encryptor.key.decode("utf-8"))


def test_ttl_expiration_timing(tmp_path: Path, encryption_key: SecretStr) -> None:
    """Test that TTL expiration occurs within 1 minute (SC-006).

    Validates system requirement: expired proxies removed within 60 seconds.
    """
    from proxywhirl.cache import CacheManager

    config = CacheConfig(
        l2_cache_dir=str(tmp_path / "cache"),
        l3_database_path=str(tmp_path / "cache.db"),
        encryption_key=encryption_key,
        enable_background_cleanup=True,
        cleanup_interval_seconds=5,  # Check every 5 seconds
    )
    manager = CacheManager(config)

    # Create entry with 10-second TTL
    now = datetime.now(timezone.utc)
    entry = CacheEntry(
        key="timing_test",
        proxy_url="http://proxy.example.com:8080",
        username=None,
        password=None,
        source="test",
        fetch_time=now,
        last_accessed=now,
        ttl_seconds=10,
        expires_at=now + timedelta(seconds=10),
    )

    manager.put(entry.key, entry)

    # Verify entry exists
    assert manager.get(entry.key) is not None

    # Wait for expiration + cleanup (10s TTL + up to 5s cleanup = 15s max)
    time.sleep(16)

    # Entry should be removed (within 60s requirement)
    retrieved = manager.get(entry.key)
    assert retrieved is None, "Entry should be removed within TTL + cleanup interval"


def test_expired_proxy_unavailable(tmp_path: Path, encryption_key: SecretStr) -> None:
    """Test that expired proxies are treated as unavailable.

    Verifies that expired proxies cannot be retrieved or used.
    """
    from proxywhirl.cache import CacheManager

    config = CacheConfig(
        l2_cache_dir=str(tmp_path / "cache"),
        l3_database_path=str(tmp_path / "cache.db"),
        encryption_key=encryption_key,
    )
    manager = CacheManager(config)

    # Create entry that expires quickly
    now = datetime.now(timezone.utc)
    entry = CacheEntry(
        key="unavailable_test",
        proxy_url="http://proxy.example.com:8080",
        username=SecretStr("user"),
        password=SecretStr("pass"),
        source="test",
        fetch_time=now,
        last_accessed=now,
        ttl_seconds=2,
        expires_at=now + timedelta(seconds=2),
    )

    manager.put(entry.key, entry)

    # Verify entry is available
    retrieved = manager.get(entry.key)
    assert retrieved is not None
    assert retrieved.proxy_url == entry.proxy_url

    # Wait for expiration
    time.sleep(3)

    # Entry should be unavailable
    retrieved = manager.get(entry.key)
    assert retrieved is None, "Expired proxy should be unavailable"

    # Verify it's removed from all tiers
    assert manager.l1_tier.get(entry.key) is None
    assert manager.l2_tier.get(entry.key) is None
    assert manager.l3_tier.get(entry.key) is None
