"""Modern cache tests through ProxyWhirl factory.

Comprehensive test suite for modern cache system through ProxyWhirl's 
unified interface, testing memory, JSON, and SQLite cache backends.

pyright: reportMissingImports=false, reportUnknownMemberType=false,
    reportUnknownVariableType=false, reportUnknownArgumentType=false,
    reportUnknownParameterType=false
"""

import json
import sqlite3
from datetime import datetime, timezone
from ipaddress import ip_address
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest
from hypothesis import given
from hypothesis import strategies as st

from proxywhirl.models import AnonymityLevel, CacheType, Proxy, Scheme
from proxywhirl.proxywhirl import ProxyWhirl


def _make_proxy(i: int) -> Proxy:
    """Create test proxy with predictable values."""
    host = f"192.0.2.{i}"
    return Proxy(
        host=host,
        ip=ip_address(host),
        port=8000 + i,
        schemes=[Scheme.HTTP],
        country_code="US",
        country="United States",
        city="New York",
        region="New York",
        isp="Test ISP",
        organization="Test Organization",
        anonymity=AnonymityLevel.ELITE,
        last_checked=datetime.now(timezone.utc),
        response_time=0.5,
        source="test",
        blacklist_reason=None,
    )


# Property-based testing strategies
proxy_strategies = st.builds(
    Proxy,
    host=st.text(min_size=7, max_size=15).filter(lambda x: "." in x and len(x.split(".")) == 4),
    ip=st.from_regex(
        r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    ).map(ip_address),
    port=st.integers(min_value=1, max_value=65535),
    schemes=st.lists(st.sampled_from(list(Scheme)), min_size=1),
    country_code=st.text(min_size=2, max_size=2, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
    anonymity=st.sampled_from(list(AnonymityLevel)),
    last_checked=st.datetimes(min_value=datetime(2020, 1, 1, tzinfo=timezone.utc)),
    response_time=st.floats(min_value=0.01, max_value=10.0),
    source=st.text(min_size=1, max_size=20),
)


def test_memory_cache_add_get_clear():
    """Test basic memory cache operations."""
    pw = ProxyWhirl(cache_type=CacheType.MEMORY)
    p1, p2 = _make_proxy(1), _make_proxy(2)
    pw.cache.add_proxies_sync([p1, p2])
    got = pw.cache.get_proxies_sync()
    assert len(got) == 2
    pw.cache.clear_sync()
    assert pw.cache.get_proxies_sync() == []


def test_json_cache_empty():
    """Test JSON cache behavior when file doesn't exist."""
    path = Path("/nonexistent/path.json")
    pw = ProxyWhirl(cache_type=CacheType.JSON, cache_path=path)
    proxies = pw.cache.get_proxies_sync()
    assert proxies == []


def test_json_cache_persistence_real_file(tmp_path: Path):
    """Test actual JSON persistence with a real file on disk."""
    path = tmp_path / "test.json"
    pw1 = ProxyWhirl(cache_type=CacheType.JSON, cache_path=path)
    p1 = _make_proxy(10)
    pw1.cache.add_proxies_sync([p1])

    # Create a second instance that loads from the same file
    pw2 = ProxyWhirl(cache_type=CacheType.JSON, cache_path=path)
    proxies = pw2.cache.get_proxies_sync()
    assert len(proxies) == 1
    assert proxies[0].host == p1.host


def test_update_and_remove():
    """Test proxy update and removal operations."""
    pw = ProxyWhirl(cache_type=CacheType.MEMORY)
    p1 = _make_proxy(1)
    pw.cache.add_proxies_sync([p1])
    p1.port = 9000
    pw.cache.update_proxy_sync(p1)
    assert pw.cache.get_proxies_sync()[0].port == 9000
    pw.cache.remove_proxy_sync(p1)
    assert pw.cache.get_proxies_sync() == []


def test_sqlite_cache_round_trip(tmp_path: Path):
    """Test SQLite cache operations with database persistence."""
    db_path = tmp_path / "cache.sqlite"
    pw = ProxyWhirl(cache_type=CacheType.SQLITE, cache_path=db_path)
    p1, p2 = _make_proxy(10), _make_proxy(11)
    pw.cache.add_proxies_sync([p1, p2])
    all1 = pw.cache.get_proxies_sync()
    hosts1 = {p.host for p in all1}
    assert {p1.host, p2.host} == hosts1
    # Update one
    p1.port = 9999
    pw.cache.update_proxy_sync(p1)
    # Remove other
    pw.cache.remove_proxy_sync(p2)
    all2 = pw.cache.get_proxies_sync()
    assert len(all2) == 1 and all2[0].port == 9999
    # Clear
    pw.cache.clear_sync()
    assert pw.cache.get_proxies_sync() == []


def test_sqlite_cache_requires_path():
    """Test that SQLite cache requires path parameter."""
    # SQLite cache now gets default path when path is None
    pw = ProxyWhirl(cache_type=CacheType.SQLITE)  # Should work with default path
    assert pw.cache is not None


def test_json_cache_handles_missing_file(tmp_path: Path):
    """Test JSON cache behavior with non-existent file."""
    path = tmp_path / "nonexistent.json"
    cache = ProxyCache(CacheType.JSON, path)
    # Should not fail, should return empty list
    proxies = cache.get_proxies()
    assert proxies == []

    # Add proxy should create file
    p1 = _make_proxy(1)
    cache.add_proxies([p1])
    assert path.exists()

    # New cache instance should load from file
    cache2 = ProxyCache(CacheType.JSON, path)
    proxies = cache2.get_proxies()
    assert len(proxies) == 1
    assert proxies[0].host == p1.host


class TestCacheErrorScenarios:
    """Test cache error handling and edge cases."""

    def test_json_save_error_handling(self, tmp_path: Path):
        """Test JSON save error handling."""
        path = tmp_path / "readonly" / "cache.json"
        # Create readonly parent directory
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only

        cache = ProxyCache(CacheType.JSON, path)
        p1 = _make_proxy(1)

        # Should not raise, but log error
        with patch("proxywhirl.cache.logger") as mock_logger:
            cache.add_proxies([p1])
            mock_logger.error.assert_called_once()

        # Cleanup
        readonly_dir.chmod(0o755)

    def test_json_load_corrupted_file(self, tmp_path: Path):
        """Test JSON load with corrupted file."""
        path = tmp_path / "corrupted.json"
        path.write_text("invalid json content")

        cache = ProxyCache(CacheType.JSON, path)

        with patch("proxywhirl.cache.logger") as mock_logger:
            proxies = cache.get_proxies()
            assert proxies == []
            mock_logger.error.assert_called_once()

    def test_json_load_invalid_proxy_data(self, tmp_path: Path):
        """Test JSON load with invalid proxy data."""
        path = tmp_path / "invalid_proxies.json"
        path.write_text('[{"host": "invalid", "port": "not_a_number"}]')

        cache = ProxyCache(CacheType.JSON, path)

        # Should not raise, should return empty list and log error
        with patch("proxywhirl.cache.logger") as mock_logger:
            proxies = cache.get_proxies()
            assert proxies == []
            mock_logger.error.assert_called_once()

    def test_sqlite_database_error_handling(self, tmp_path: Path):
        """Test SQLite database error scenarios."""
        db_path = tmp_path / "cache.db"
        cache = ProxyCache(CacheType.SQLITE, db_path)

        # Close the connection to simulate error
        if cache._db:
            cache._db.close()
            cache._db = None

        # Operations should handle missing connection gracefully
        p1 = _make_proxy(1)
        cache.add_proxies([p1])  # Should not raise
        proxies = cache.get_proxies()  # Should return empty list
        assert proxies == []


# Property-based tests
class TestCachePropertyBased:
    """Property-based tests for cache operations."""

    @given(st.lists(proxy_strategies, min_size=1, max_size=10))
    def test_memory_cache_roundtrip(self, proxies):
        """Property test: memory cache preserves all added proxies."""
        cache = ProxyCache(CacheType.MEMORY)
        cache.add_proxies(proxies)
        retrieved = cache.get_proxies()

        # Should have same number of proxies
        assert len(retrieved) == len(proxies)

        # All original proxies should be retrievable by host+port
        original_keys = {(p.host, p.port) for p in proxies}
        retrieved_keys = {(p.host, p.port) for p in retrieved}
        assert original_keys.issubset(retrieved_keys)

    @given(proxy_strategies)
    def test_cache_update_operations(self, proxy):
        """Property test: update operations preserve proxy identity."""
        cache = ProxyCache(CacheType.MEMORY)
        cache.add_proxies([proxy])

        # Modify proxy
        original_host, original_port = proxy.host, proxy.port
        proxy.source = "updated_source"

        cache.update_proxy(proxy)
        retrieved = cache.get_proxies()

        assert len(retrieved) == 1
        updated_proxy = retrieved[0]
        assert updated_proxy.host == original_host
        assert updated_proxy.port == original_port
        assert updated_proxy.source == "updated_source"

    @given(st.lists(proxy_strategies, min_size=1, max_size=5))
    def test_json_cache_persistence_property(self, proxies, tmp_path):
        """Property test: JSON cache preserves proxies across instances."""
        path = tmp_path / "test.json"

        # Add proxies to first cache instance
        cache1 = ProxyCache(CacheType.JSON, path)
        cache1.add_proxies(proxies)

        # Load from second cache instance
        cache2 = ProxyCache(CacheType.JSON, path)
        retrieved = cache2.get_proxies()

        # Should have same proxy keys
        original_keys = {(p.host, p.port) for p in proxies}
        retrieved_keys = {(p.host, p.port) for p in retrieved}
        assert original_keys.issubset(retrieved_keys)

    @given(proxy_strategies)
    def test_sqlite_upsert_behavior(self, proxy, tmp_path):
        """Property test: SQLite cache upsert behavior."""
        db_path = tmp_path / "test.db"
        cache = ProxyCache(CacheType.SQLITE, db_path)

        # Add proxy
        cache.add_proxies([proxy])
        assert len(cache.get_proxies()) == 1

        # Add same proxy again (should upsert)
        proxy.source = "updated"
        cache.add_proxies([proxy])

        retrieved = cache.get_proxies()
        assert len(retrieved) == 1
        assert retrieved[0].source == "updated"


# Integration tests
class TestCacheIntegration:
    """Integration tests for cache with real file operations."""

    def test_concurrent_json_cache_access(self, tmp_path: Path):
        """Test concurrent access to JSON cache."""
        path = tmp_path / "concurrent.json"

        cache1 = ProxyCache(CacheType.JSON, path)
        cache2 = ProxyCache(CacheType.JSON, path)

        p1 = _make_proxy(1)
        p2 = _make_proxy(2)

        cache1.add_proxies([p1])
        cache2.add_proxies([p2])

        # Both caches should have their respective data
        # (last write wins in this simple implementation)
        cache1_proxies = cache1.get_proxies()
        cache2_proxies = cache2.get_proxies()

        # At least one should have data
        assert len(cache1_proxies) > 0 or len(cache2_proxies) > 0

    def test_cache_type_switching(self, tmp_path: Path):
        """Test data migration between cache types."""
        # Start with memory cache
        memory_cache = ProxyCache(CacheType.MEMORY)
        p1, p2 = _make_proxy(1), _make_proxy(2)
        memory_cache.add_proxies([p1, p2])
        memory_proxies = memory_cache.get_proxies()

        # Export to JSON
        json_path = tmp_path / "export.json"
        json_cache = ProxyCache(CacheType.JSON, json_path)
        json_cache.add_proxies(memory_proxies)

        # Import to SQLite
        db_path = tmp_path / "import.db"
        sqlite_cache = ProxyCache(CacheType.SQLITE, db_path)
        json_proxies = json_cache.get_proxies()
        sqlite_cache.add_proxies(json_proxies)
        sqlite_proxies = sqlite_cache.get_proxies()

        # All should have same proxy keys
        memory_keys = {(p.host, p.port) for p in memory_proxies}
        json_keys = {(p.host, p.port) for p in json_proxies}
        sqlite_keys = {(p.host, p.port) for p in sqlite_proxies}

        assert memory_keys == json_keys == sqlite_keys


@pytest.mark.parametrize(
    "cache_type,expected_len_after_dupe",
    [
        (CacheType.MEMORY, 2),  # memory is append-only for add_proxies
        (CacheType.JSON, 2),  # json mirrors in-memory list; no dedupe on add
        (CacheType.SQLITE, 1),  # sqlite uses PK(host,port) upsert
    ],
)
def test_add_duplicate_proxies(cache_type, expected_len_after_dupe, tmp_path):
    """Document current duplicate handling per backend."""
    path = tmp_path / "cache.db" if cache_type != CacheType.MEMORY else None
    cache = ProxyCache(cache_type, path)
    p1 = _make_proxy(1)

    cache.add_proxies([p1])
    assert len(cache.get_proxies()) == 1

    # Add the same proxy again
    cache.add_proxies([p1])
    assert len(cache.get_proxies()) == expected_len_after_dupe

    # Update semantics are via update_proxy (not add_proxies) for non-sqlite
    p1_alt = _make_proxy(1)
    p1_alt.source = "new_source"
    cache.update_proxy(p1_alt)

    proxies = cache.get_proxies()
    # For MEMORY/JSON: ensure at least one entry has updated metadata
    # For SQLITE: single row should reflect new metadata
    assert any(getattr(px, "source", None) == "new_source" for px in proxies)


# Performance and stress tests
class TestCachePerformance:
    """Performance tests for cache operations."""

    def test_large_dataset_memory_cache(self, benchmark):
        """Benchmark memory cache with large dataset."""
        cache = ProxyCache(CacheType.MEMORY)
        proxies = [_make_proxy(i) for i in range(1000)]

        @benchmark
        def add_and_retrieve():
            cache.clear()
            cache.add_proxies(proxies)
            return cache.get_proxies()

        result = add_and_retrieve
        assert len(result) == 1000

    def test_sqlite_bulk_operations(self, benchmark, tmp_path):
        """Benchmark SQLite cache bulk operations."""
        db_path = tmp_path / "perf.db"
        cache = ProxyCache(CacheType.SQLITE, db_path)
        proxies = [_make_proxy(i) for i in range(500)]

        @benchmark
        def bulk_insert():
            cache.clear()
            cache.add_proxies(proxies)
            return len(cache.get_proxies())

        result = bulk_insert
        assert result == 500

    def test_json_serialization_performance(self, benchmark, tmp_path):
        """Benchmark JSON cache serialization performance."""
        path = tmp_path / "perf.json"
        cache = ProxyCache(CacheType.JSON, path)
        proxies = [_make_proxy(i) for i in range(200)]

        @benchmark
        def json_roundtrip():
            cache.clear()
            cache.add_proxies(proxies)
            return len(cache.get_proxies())

        result = json_roundtrip
        assert result == 200
