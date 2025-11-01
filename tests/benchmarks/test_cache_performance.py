"""Benchmark tests for cache performance.

Tests performance requirements:
- SC-002: L1 (memory) lookups <1ms
- SC-003: L2/L3 (disk) lookups <50ms
- SC-009: Eviction overhead <10ms
"""

import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pydantic import SecretStr

from proxywhirl.cache import CacheManager
from proxywhirl.cache_crypto import CredentialEncryptor
from proxywhirl.cache_models import CacheConfig, CacheEntry, HealthStatus


def test_l1_lookup_latency(tmp_path: Path, benchmark) -> None:  # type: ignore[no-untyped-def]
    """Test that L1 (memory) cache lookups are <1ms (SC-002).

    Benchmark performs 1000 lookups and verifies average is under 1ms.
    """
    encryptor = CredentialEncryptor()
    encryption_key = SecretStr(encryptor.key.decode("utf-8"))

    config = CacheConfig(
        l2_cache_dir=str(tmp_path / "cache"),
        l3_database_path=str(tmp_path / "cache.db"),
        encryption_key=encryption_key,
    )

    manager = CacheManager(config)
    now = datetime.now(timezone.utc)

    # Populate L1 with test entries
    for i in range(100):
        entry = CacheEntry(
            key=f"bench_key_{i}",
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

    # Benchmark L1 lookups
    def lookup_l1() -> None:
        """Perform a single L1 lookup."""
        key = f"bench_key_{50}"  # Middle entry
        result = manager.get(key)
        assert result is not None

    # Run benchmark
    result = benchmark(lookup_l1)

    # Verify <1ms requirement (SC-002)
    avg_time_ms = result.stats.mean * 1000
    assert avg_time_ms < 1.0, f"L1 lookup took {avg_time_ms:.3f}ms, should be <1ms"


def test_disk_lookup_latency(tmp_path: Path) -> None:
    """Test that L2/L3 (disk) cache lookups are <50ms (SC-003).

    Tests cold start scenario where L1 is empty and lookup must go to disk.
    """
    encryptor = CredentialEncryptor()
    encryption_key = SecretStr(encryptor.key.decode("utf-8"))

    config = CacheConfig(
        l2_cache_dir=str(tmp_path / "cache"),
        l3_database_path=str(tmp_path / "cache.db"),
        encryption_key=encryption_key,
    )

    manager = CacheManager(config)
    now = datetime.now(timezone.utc)

    # Store entry in L3 only
    entry = CacheEntry(
        key="disk_test",
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
    manager.l3_tier.put(entry.key, entry)

    # Measure disk lookup time (cold L1)
    start = time.perf_counter()
    result = manager.get(entry.key)
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert result is not None, "Entry should be found on disk"
    assert elapsed_ms < 50.0, f"Disk lookup took {elapsed_ms:.3f}ms, should be <50ms"


def test_eviction_overhead(tmp_path: Path, benchmark) -> None:  # type: ignore[no-untyped-def]
    """Test that eviction overhead is <10ms (SC-009).

    Measures time to evict oldest entry when L1 reaches capacity.
    """
    from proxywhirl.cache_models import CacheTierConfig

    encryptor = CredentialEncryptor()
    encryption_key = SecretStr(encryptor.key.decode("utf-8"))

    config = CacheConfig(
        l1_config=CacheTierConfig(enabled=True, max_entries=100),
        l2_cache_dir=str(tmp_path / "cache"),
        l3_database_path=str(tmp_path / "cache.db"),
        encryption_key=encryption_key,
    )

    manager = CacheManager(config)
    now = datetime.now(timezone.utc)

    # Fill L1 to capacity
    for i in range(100):
        entry = CacheEntry(
            key=f"evict_key_{i}",
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

    # Benchmark eviction (adding 101st entry)
    def trigger_eviction() -> None:
        """Add entry to trigger LRU eviction."""
        entry = CacheEntry(
            key="evict_trigger",
            proxy_url="http://proxy_trigger.example.com:8080",
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

    result = benchmark(trigger_eviction)

    # Verify <10ms requirement (SC-009)
    avg_time_ms = result.stats.mean * 1000
    assert avg_time_ms < 10.0, f"Eviction took {avg_time_ms:.3f}ms, should be <10ms"
