"""Tests for smart response caching module."""

import time

from proxywhirl.response_caching import CacheEntry, SmartCache


class TestCacheEntry:
    """Test CacheEntry class."""

    def test_cache_entry_creation(self):
        """Test cache entry creation."""
        entry = CacheEntry(key="test", value="value", ttl=60)
        assert entry.key == "test"
        assert entry.value == "value"
        assert entry.ttl == 60

    def test_is_expired_no_ttl(self):
        """Test expiration with no TTL."""
        entry = CacheEntry(key="test", value="value", ttl=None)
        assert not entry.is_expired()

    def test_is_expired_valid(self):
        """Test non-expired entry."""
        entry = CacheEntry(key="test", value="value", ttl=60)
        assert not entry.is_expired()

    def test_is_expired_invalid(self):
        """Test expired entry."""
        entry = CacheEntry(key="test", value="value", ttl=1)
        time.sleep(1.1)
        assert entry.is_expired()

    def test_touch(self):
        """Test touching entry."""
        entry = CacheEntry(key="test", value="value")
        assert entry.access_count == 0
        old_time = entry.last_accessed
        entry.touch()
        assert entry.access_count == 1
        assert entry.last_accessed > old_time


class TestSmartCache:
    """Test SmartCache class."""

    def test_cache_creation(self):
        """Test cache creation."""
        cache = SmartCache(max_size=100, max_memory_mb=10)
        assert cache.max_size == 100

    def test_set_and_get(self):
        """Test setting and getting values."""
        cache = SmartCache()
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_missing_key(self):
        """Test getting missing key."""
        cache = SmartCache()
        assert cache.get("missing") is None

    def test_get_expired_entry(self):
        """Test getting expired entry."""
        cache = SmartCache()
        cache.set("key1", "value1", ttl=1)
        time.sleep(1.1)
        assert cache.get("key1") is None

    def test_delete(self):
        """Test deleting entry."""
        cache = SmartCache()
        cache.set("key1", "value1")
        assert cache.delete("key1")
        assert cache.get("key1") is None

    def test_delete_missing_key(self):
        """Test deleting missing key."""
        cache = SmartCache()
        assert not cache.delete("missing")

    def test_clear(self):
        """Test clearing cache."""
        cache = SmartCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_hit_rate(self):
        """Test hit rate calculation."""
        cache = SmartCache()
        cache.set("key1", "value1")
        cache.get("key1")
        cache.get("key1")
        cache.get("missing")
        hit_rate = cache.hit_rate()
        assert hit_rate > 0

    def test_stats(self):
        """Test statistics export."""
        cache = SmartCache()
        cache.set("key1", "value1")
        cache.get("key1")
        cache.get("missing")
        stats = cache.stats()
        assert "entries" in stats
        assert "hits" in stats
        assert "misses" in stats
        assert "hit_rate" in stats

    def test_get_keys(self):
        """Test getting all keys."""
        cache = SmartCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        keys = cache.get_keys()
        assert "key1" in keys
        assert "key2" in keys

    def test_max_size_eviction(self):
        """Test LRU eviction on max size."""
        cache = SmartCache(max_size=2)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        # key1 should be evicted
        assert len(cache.get_keys()) == 2
