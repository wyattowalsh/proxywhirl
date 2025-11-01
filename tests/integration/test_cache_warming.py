"""Integration tests for cache warming functionality.

Tests cache warming performance and startup scenarios to validate:
- SC-007: Load 10,000 proxies in <5 seconds
- Cache warming during application startup
"""

import json
import time
from datetime import timedelta
from pathlib import Path

from pydantic import SecretStr

from proxywhirl.cache import CacheManager
from proxywhirl.cache_crypto import CredentialEncryptor
from proxywhirl.cache_models import CacheConfig


def test_cache_warming_performance(tmp_path: Path) -> None:
    """Test that cache warming loads 10,000 proxies in <5 seconds (SC-007).

    This validates the performance requirement for cache warming operations.
    """
    # Create test file with 10,000 proxies
    proxies_file = tmp_path / "proxies_10k.json"
    proxies = []
    for i in range(10000):
        proxies.append(
            {
                "proxy_url": f"http://proxy{i}.example.com:8080",
                "source": "performance_test",
            }
        )

    proxies_file.write_text(json.dumps(proxies))

    # Initialize cache manager
    encryptor = CredentialEncryptor()
    encryption_key = SecretStr(encryptor.key.decode("utf-8"))

    config = CacheConfig(
        l2_cache_dir=str(tmp_path / "cache"),
        l3_database_path=str(tmp_path / "cache.db"),
        encryption_key=encryption_key,
    )

    manager = CacheManager(config)

    # Measure warming time
    start_time = time.perf_counter()
    result = manager.warm_from_file(str(proxies_file))
    elapsed = time.perf_counter() - start_time

    # Validate results
    assert result["loaded"] == 10000, f"Expected 10000 proxies loaded, got {result['loaded']}"
    assert result["skipped"] == 0, "Should have no skipped entries"
    assert elapsed < 5.0, f"Cache warming took {elapsed:.2f}s, should be <5s (SC-007)"

    # Verify proxies are accessible
    stats = manager.get_statistics()
    total_size = (
        stats.l1_stats.current_size + stats.l2_stats.current_size + stats.l3_stats.current_size
    )
    assert total_size == 10000, f"Expected 10000 cached proxies, got {total_size}"


def test_startup_cache_warming(tmp_path: Path) -> None:
    """Test cache warming during application startup.

    Simulates a typical startup scenario where cached proxies are loaded
    before the application begins serving requests.
    """
    # Create test file with sample proxies
    proxies_file = tmp_path / "startup_proxies.json"
    proxies = []
    for i in range(100):
        proxies.append(
            {
                "proxy_url": f"http://startup{i}.example.com:8080",
                "source": "startup_test",
                "username": f"user{i}",
                "password": f"pass{i}",
            }
        )

    proxies_file.write_text(json.dumps(proxies))

    # Initialize cache manager (simulating startup)
    encryptor = CredentialEncryptor()
    encryption_key = SecretStr(encryptor.key.decode("utf-8"))

    config = CacheConfig(
        l2_cache_dir=str(tmp_path / "cache"),
        l3_database_path=str(tmp_path / "cache.db"),
        encryption_key=encryption_key,
        default_ttl_seconds=7200,  # 2 hours
    )

    manager = CacheManager(config)

    # Warm cache during startup
    result = manager.warm_from_file(str(proxies_file))

    assert result["loaded"] == 100, "Should load all 100 proxies"
    assert result["skipped"] == 0, "Should skip no proxies"

    # Verify proxies are immediately available (no fetch needed)
    test_key = manager._generate_cache_key("http://startup50.example.com:8080")
    cached_proxy = manager.get(test_key)

    assert cached_proxy is not None, "Warmed proxy should be immediately available"
    assert cached_proxy.proxy_url == "http://startup50.example.com:8080"
    assert cached_proxy.source == "startup_test"

    # Verify credentials were encrypted and stored
    assert cached_proxy.username is not None
    assert cached_proxy.username.get_secret_value() == "user50"
    assert cached_proxy.password is not None
    assert cached_proxy.password.get_secret_value() == "pass50"

    # Verify TTL was set correctly
    assert not cached_proxy.is_expired, "Newly warmed proxy should not be expired"
    expected_ttl = timedelta(seconds=7200)
    actual_ttl = cached_proxy.expires_at - cached_proxy.fetch_time
    assert abs((actual_ttl - expected_ttl).total_seconds()) < 5, "TTL should match config"


def test_cache_warming_with_custom_ttl(tmp_path: Path) -> None:
    """Test cache warming with custom TTL override.

    Validates that custom TTL values can be applied during warming,
    useful for different proxy sources with varying freshness requirements.
    """
    proxies_file = tmp_path / "custom_ttl_proxies.json"
    proxies = [
        {"proxy_url": "http://proxy1.example.com:8080", "source": "premium"},
        {"proxy_url": "http://proxy2.example.com:8080", "source": "premium"},
    ]
    proxies_file.write_text(json.dumps(proxies))

    encryptor = CredentialEncryptor()
    encryption_key = SecretStr(encryptor.key.decode("utf-8"))

    config = CacheConfig(
        l2_cache_dir=str(tmp_path / "cache"),
        l3_database_path=str(tmp_path / "cache.db"),
        encryption_key=encryption_key,
        default_ttl_seconds=3600,
    )

    manager = CacheManager(config)

    # Warm with custom TTL (longer for premium proxies)
    custom_ttl = 14400  # 4 hours
    result = manager.warm_from_file(str(proxies_file), ttl_seconds=custom_ttl)

    assert result["loaded"] == 2

    # Verify custom TTL was applied
    key1 = manager._generate_cache_key("http://proxy1.example.com:8080")
    cached = manager.get(key1)

    assert cached is not None
    assert cached.ttl_seconds == custom_ttl, f"Expected TTL {custom_ttl}, got {cached.ttl_seconds}"
