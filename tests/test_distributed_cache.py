"""Tests for distributed cache layer."""

import asyncio
from datetime import timedelta

import pytest

from proxywhirl.cache.distributed import (
    DistributedCache,
    DistributedLock,
    InMemoryCacheBackend,
)


@pytest.fixture
async def cache():
    """Create a test distributed cache."""
    backend = InMemoryCacheBackend()
    return DistributedCache(backend)


@pytest.mark.asyncio
async def test_cache_set_get(cache):
    """Test basic set and get operations."""
    await cache.backend.set("key1", "value1")
    value = await cache.backend.get("key1")
    assert value == "value1"


@pytest.mark.asyncio
async def test_cache_get_missing(cache):
    """Test getting missing key returns None."""
    value = await cache.backend.get("nonexistent")
    assert value is None


@pytest.mark.asyncio
async def test_cache_delete(cache):
    """Test deleting keys."""
    await cache.backend.set("key1", "value1")
    assert await cache.backend.exists("key1")

    result = await cache.backend.delete("key1")
    assert result is True
    assert not await cache.backend.exists("key1")


@pytest.mark.asyncio
async def test_cache_exists(cache):
    """Test checking key existence."""
    assert not await cache.backend.exists("key1")
    await cache.backend.set("key1", "value1")
    assert await cache.backend.exists("key1")


@pytest.mark.asyncio
async def test_cache_incr(cache):
    """Test incrementing counter."""
    value = await cache.backend.incr("counter", 1)
    assert value == 1

    value = await cache.backend.incr("counter", 5)
    assert value == 6


@pytest.mark.asyncio
async def test_cache_incr_new_key(cache):
    """Test incrementing non-existent key."""
    value = await cache.backend.incr("new_counter", 10)
    assert value == 10


@pytest.mark.asyncio
async def test_cache_delete_pattern(cache):
    """Test deleting keys by pattern."""
    await cache.backend.set("user:1:name", "Alice")
    await cache.backend.set("user:2:name", "Bob")
    await cache.backend.set("user:3:email", "alice@example.com")

    # Delete all user:*:name keys
    deleted = await cache.backend.delete_pattern("user:*:name")
    assert deleted == 2

    assert not await cache.backend.exists("user:1:name")
    assert not await cache.backend.exists("user:2:name")
    assert await cache.backend.exists("user:3:email")


@pytest.mark.asyncio
async def test_cache_stats(cache):
    """Test cache statistics."""
    stats = await cache.backend.get_stats()
    assert stats.hits == 0
    assert stats.misses == 0

    await cache.backend.set("key1", "value1")
    await cache.backend.get("key1")  # Hit
    await cache.backend.get("key2")  # Miss

    stats = await cache.backend.get_stats()
    assert stats.hits == 1
    assert stats.misses == 1
    assert stats.hit_rate == 0.5


@pytest.mark.asyncio
async def test_cache_get_or_set_cached(cache):
    """Test get_or_set with cached value."""
    await cache.backend.set("key1", "cached_value")

    async def factory():
        return "computed_value"

    value = await cache.get_or_set("key1", factory)
    assert value == "cached_value"


@pytest.mark.asyncio
async def test_cache_get_or_set_compute(cache):
    """Test get_or_set computes value if not cached."""

    async def factory():
        return "computed_value"

    value = await cache.get_or_set("key1", factory)
    assert value == "computed_value"

    # Should be cached now
    cached = await cache.backend.get("key1")
    assert cached == "computed_value"


@pytest.mark.asyncio
async def test_cache_delete_many(cache):
    """Test deleting multiple keys."""
    await cache.backend.set("key1", "value1")
    await cache.backend.set("key2", "value2")
    await cache.backend.set("key3", "value3")

    deleted = await cache.delete_many(["key1", "key2"])
    assert deleted == 2

    assert not await cache.backend.exists("key1")
    assert not await cache.backend.exists("key2")
    assert await cache.backend.exists("key3")


@pytest.mark.asyncio
async def test_cache_max_size(cache):
    """Test cache respects max size limit."""
    cache = DistributedCache(InMemoryCacheBackend(max_size=3))

    await cache.backend.set("key1", "value1")
    await cache.backend.set("key2", "value2")
    await cache.backend.set("key3", "value3")

    stats = await cache.backend.get_stats()
    assert stats.entry_count == 3

    # Adding 4th key should evict one
    await cache.backend.set("key4", "value4")

    stats = await cache.backend.get_stats()
    assert stats.entry_count == 3
    assert stats.evictions == 1


@pytest.mark.asyncio
async def test_distributed_lock_acquire(cache):
    """Test acquiring a lock."""
    lock = DistributedLock(cache, "test_lock")
    result = await lock.acquire()
    assert result is True

    # Should exist now
    assert await cache.backend.exists("test_lock")

    # Release
    result = await lock.release()
    assert result is True
    assert not await cache.backend.exists("test_lock")


@pytest.mark.asyncio
async def test_distributed_lock_context_manager(cache):
    """Test lock as context manager."""
    lock = DistributedLock(cache, "test_lock")

    async with lock:
        assert await cache.backend.exists("test_lock")

    assert not await cache.backend.exists("test_lock")


@pytest.mark.asyncio
async def test_distributed_lock_timeout(cache):
    """Test lock timeout on already acquired lock."""
    lock1 = DistributedLock(cache, "test_lock")
    await lock1.acquire()

    lock2 = DistributedLock(cache, "test_lock")
    result = await lock2.acquire(timeout=timedelta(milliseconds=100))
    assert result is False

    await lock1.release()


@pytest.mark.asyncio
async def test_distributed_lock_context_timeout(cache):
    """Test lock context manager timeout."""
    lock1 = DistributedLock(cache, "test_lock")
    await lock1.acquire()

    lock2 = DistributedLock(cache, "test_lock")
    with pytest.raises(TimeoutError):
        async with lock2:
            pass

    await lock1.release()


@pytest.mark.asyncio
async def test_cache_complex_values(cache):
    """Test caching complex values."""
    data = {
        "id": 123,
        "name": "Proxy",
        "tags": ["http", "fast"],
        "metrics": {"hits": 100, "misses": 5},
    }

    await cache.backend.set("complex", data)
    cached = await cache.backend.get("complex")
    assert cached == data


@pytest.mark.asyncio
async def test_cache_concurrent_access(cache):
    """Test concurrent cache access."""

    async def worker(worker_id):
        for i in range(10):
            key = f"worker:{worker_id}:item:{i}"
            await cache.backend.set(key, f"value-{i}")

    await asyncio.gather(*[worker(i) for i in range(5)])

    stats = await cache.backend.get_stats()
    assert stats.entry_count == 50
