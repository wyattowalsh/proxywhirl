"""Cache stampede prevention via get_or_load singleflight."""

from __future__ import annotations

import threading
import time
from datetime import datetime, timedelta, timezone

import pytest

from proxywhirl.cache.manager import CacheManager
from proxywhirl.cache.models import CacheConfig, CacheEntry, CacheTierConfig


def _entry(key: str, *, proxy_suffix: str = "8080") -> CacheEntry:
    now = datetime.now(timezone.utc)
    return CacheEntry(
        key=key,
        proxy_url=f"http://proxy.example.com:{proxy_suffix}",
        source="stampede-test",
        fetch_time=now,
        last_accessed=now,
        ttl_seconds=3600,
        expires_at=now + timedelta(hours=1),
    )


@pytest.fixture
def cache_manager(tmp_path) -> CacheManager:
    config = CacheConfig(
        l2_cache_dir=str(tmp_path / "l2"),
        l3_database_path=str(tmp_path / "l3.db"),
        enable_background_cleanup=False,
        l1_config=CacheTierConfig(max_entries=50),
        l2_config=CacheTierConfig(max_entries=200),
    )
    return CacheManager(config=config)


class TestCacheStampedePrevention:
    """Stampede tests use real put/get and get_or_load coalescing."""

    def test_get_or_load_hit_skips_loader(self, cache_manager: CacheManager) -> None:
        key = "warm-key"
        entry = _entry(key)
        assert cache_manager.put(key, entry) is True

        calls = 0

        def loader() -> CacheEntry:
            nonlocal calls
            calls += 1
            return _entry(key, proxy_suffix="9999")

        result = cache_manager.get_or_load(key, loader)
        assert result.proxy_url == entry.proxy_url
        assert calls == 0

    def test_concurrent_miss_single_origin_load(self, cache_manager: CacheManager) -> None:
        key = "coalesce-key"
        origin_calls = 0
        origin_lock = threading.Lock()
        barrier = threading.Barrier(8)

        def loader() -> CacheEntry:
            nonlocal origin_calls
            with origin_lock:
                origin_calls += 1
            time.sleep(0.05)
            return _entry(key)

        results: list[CacheEntry] = []
        errors: list[BaseException] = []
        results_lock = threading.Lock()

        def worker() -> None:
            try:
                barrier.wait(timeout=5)
                entry = cache_manager.get_or_load(key, loader)
                with results_lock:
                    results.append(entry)
            except BaseException as exc:
                with results_lock:
                    errors.append(exc)

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)

        assert not errors, f"worker errors: {errors}"
        assert origin_calls == 1
        assert len(results) == 8
        assert all(item.key == key for item in results)
        assert cache_manager.get(key) is not None

    def test_put_then_get_roundtrip(self, cache_manager: CacheManager) -> None:
        key = "roundtrip"
        entry = _entry(key)
        assert cache_manager.put(key, entry) is True
        loaded = cache_manager.get(key)
        assert loaded is not None
        assert loaded.key == key
        assert loaded.proxy_url == entry.proxy_url

    def test_loader_failure_propagates_to_waiters(self, cache_manager: CacheManager) -> None:
        key = "fail-key"
        started = threading.Event()
        release = threading.Event()
        waiter_errors: list[BaseException] = []

        def loader() -> CacheEntry:
            started.set()
            release.wait(timeout=2)
            raise ValueError("origin down")

        def leader_run() -> None:
            try:
                cache_manager.get_or_load(key, loader)
            except BaseException as exc:
                waiter_errors.append(exc)

        def waiter_run() -> None:
            try:
                cache_manager.get_or_load(key, loader)
            except BaseException as exc:
                waiter_errors.append(exc)

        leader = threading.Thread(target=leader_run, name="leader")
        waiter = threading.Thread(target=waiter_run, name="waiter")

        leader.start()
        assert started.wait(timeout=2)
        waiter.start()
        release.set()
        leader.join(timeout=5)
        waiter.join(timeout=5)

        assert len(waiter_errors) == 2
        assert all(isinstance(err, ValueError) for err in waiter_errors)
        assert cache_manager.get(key) is None

        calls = 0

        def loader2() -> CacheEntry:
            nonlocal calls
            calls += 1
            return _entry(key)

        result = cache_manager.get_or_load(key, loader2)
        assert result.key == key
        assert calls == 1
