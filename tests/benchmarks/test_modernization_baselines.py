"""Distribution baselines for the 0.4 architecture-modernization seams.

Every benchmark is local and deterministic: HTTP uses ``MockTransport``,
payloads and proxy sets are fixed before timing, and persistent resources are
closed before the test returns. These tests record distributions; they do not
encode host-specific latency thresholds.
"""

from __future__ import annotations

import asyncio
import gc
import threading
import time
import tracemalloc
from collections.abc import AsyncIterator, Coroutine
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, TypeVar

import httpx
import pytest

from proxywhirl.cache.manager import CacheManager
from proxywhirl.cache.models import (
    CacheConfig,
    CacheEntry,
    CacheTierConfig,
    L2BackendType,
)
from proxywhirl.cache.tiers import DiskCacheTier
from proxywhirl.fetchers.parsers import _read_bounded_response_text
from proxywhirl.models import HealthStatus, Proxy
from proxywhirl.pool_snapshot import PoolSnapshot
from proxywhirl.storage import SQLiteStorage

_T = TypeVar("_T")
_HTTP_URL = "https://benchmark.invalid/request"
_MIB = 1024 * 1024
_ROUNDS = 25
_WARMUP_ROUNDS = 3


def _thread_snapshot() -> set[tuple[int, str]]:
    """Return live thread identities for explicit before/after accounting."""
    return {
        (thread.ident, thread.name) for thread in threading.enumerate() if thread.ident is not None
    }


def _assert_threads_restored(
    baseline: set[tuple[int, str]], *, timeout_seconds: float = 3.0
) -> None:
    """Wait briefly for owned workers to exit, then reject residual threads."""
    deadline = time.monotonic() + timeout_seconds
    while True:
        residual = _thread_snapshot() - baseline
        if not residual:
            return
        if time.monotonic() >= deadline:
            raise AssertionError(f"Residual benchmark threads: {sorted(residual)}")
        time.sleep(0.01)


async def _pending_task_count() -> int:
    """Count unfinished tasks other than the current accounting task."""
    current = asyncio.current_task()
    return sum(1 for task in asyncio.all_tasks() if task is not current and not task.done())


async def _settled_pending_task_count() -> int:
    """Let nested httpx async-generator finalizers fully unwind."""
    for _ in range(8):
        await asyncio.sleep(0)
    return await _pending_task_count()


class _AsyncLoopRunner:
    """Own one event loop thread for repeatable synchronous benchmark targets."""

    def __init__(self, name: str) -> None:
        self._loop = asyncio.new_event_loop()
        self._ready = threading.Event()
        self._thread = threading.Thread(target=self._run_loop, name=name)
        self._closed = False
        self._thread.start()
        assert self._ready.wait(timeout=5.0), "Benchmark event loop did not start"

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._ready.set()
        try:
            self._loop.run_forever()
        finally:
            pending = asyncio.all_tasks(self._loop)
            for task in pending:
                task.cancel()
            if pending:
                self._loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            self._loop.close()

    def run(self, coroutine: Coroutine[Any, Any, _T]) -> _T:
        """Run one coroutine on the owned loop and return its result."""
        if self._closed:
            raise RuntimeError("Benchmark event loop is closed")
        future = asyncio.run_coroutine_threadsafe(coroutine, self._loop)
        return future.result(timeout=120.0)

    def close(self) -> None:
        """Prove task balance, then stop and join the event-loop thread."""
        if self._closed:
            return
        assert self.run(_pending_task_count()) == 0
        self._closed = True
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=5.0)
        assert not self._thread.is_alive(), "Benchmark event-loop thread did not stop"


class _FixedAsyncByteStream(httpx.AsyncByteStream):
    """Replay one fixed byte payload in bounded chunks."""

    def __init__(self, payload: bytes, chunk_size: int = 64 * 1024) -> None:
        self._payload = payload
        self._chunk_size = chunk_size
        self.closed = False

    async def __aiter__(self) -> AsyncIterator[bytes]:
        for offset in range(0, len(self._payload), self._chunk_size):
            yield self._payload[offset : offset + self._chunk_size]

    async def aclose(self) -> None:
        self.closed = True


def _make_payload(size: int) -> bytes:
    unit = b"127.0.0.1:8080\n"
    return (unit * ((size // len(unit)) + 1))[:size]


def _make_cache_entry(key: str) -> CacheEntry:
    now = datetime.now(timezone.utc)
    return CacheEntry(
        key=key,
        proxy_url=f"http://{key}.example.invalid:8080",
        source="modernization-benchmark",
        fetch_time=now,
        last_accessed=now,
        ttl_seconds=3600,
        expires_at=now + timedelta(hours=1),
        health_status=HealthStatus.HEALTHY,
    )


def _prewarm_executor(executor: ThreadPoolExecutor, workers: int) -> set[int]:
    """Start every worker before timed stampede operations."""
    barrier = threading.Barrier(workers + 1)

    def wait_for_release() -> int:
        barrier.wait(timeout=5.0)
        return threading.get_ident()

    futures = [executor.submit(wait_for_release) for _ in range(workers)]
    barrier.wait(timeout=5.0)
    worker_ids = {future.result(timeout=5.0) for future in futures}
    assert len(worker_ids) == workers
    return worker_ids


def _checked_out_connections(storage: SQLiteStorage) -> int:
    checker = getattr(storage.engine.pool, "checkedout", None)
    assert callable(checker), "SQLite benchmark pool does not expose checkout accounting"
    return int(checker())


def _checked_in_connections(storage: SQLiteStorage) -> int:
    checker = getattr(storage.engine.pool, "checkedin", None)
    assert callable(checker), "SQLite benchmark pool does not expose checkin accounting"
    return int(checker())


class TestRequestClientReuse:
    """Compare real local requests through reused and fresh clients."""

    @pytest.mark.benchmark(group="modernization-http-sync")
    def test_sync_reused_vs_fresh_client(self, benchmark: Any) -> None:
        baseline_threads = _thread_snapshot()
        request_count = 0
        client_counts = {"created": 1, "closed": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal request_count
            request_count += 1
            return httpx.Response(200, content=b"ok", request=request)

        reused = httpx.Client(transport=httpx.MockTransport(handler))

        def request_pair() -> tuple[int, int]:
            reused_status = reused.get(_HTTP_URL).status_code
            fresh = httpx.Client(transport=httpx.MockTransport(handler))
            client_counts["created"] += 1
            try:
                fresh_status = fresh.get(_HTTP_URL).status_code
            finally:
                fresh.close()
                assert fresh.is_closed
                client_counts["closed"] += 1
            return reused_status, fresh_status

        try:
            result = benchmark.pedantic(
                request_pair,
                rounds=_ROUNDS,
                warmup_rounds=_WARMUP_ROUNDS,
                iterations=1,
            )
        finally:
            reused.close()
            assert reused.is_closed
            client_counts["closed"] += 1

        assert result == (200, 200)
        assert request_count > 0
        assert client_counts["created"] == client_counts["closed"]
        _assert_threads_restored(baseline_threads)
        benchmark.extra_info.update(
            {
                "client_created": client_counts["created"],
                "client_closed": client_counts["closed"],
                "request_count": request_count,
                "transport": "httpx.MockTransport",
            }
        )

    @pytest.mark.benchmark(group="modernization-http-async")
    def test_async_reused_vs_fresh_client(self, benchmark: Any) -> None:
        baseline_threads = _thread_snapshot()
        runner = _AsyncLoopRunner("ModernizationHTTPBenchmarkLoop")
        request_count = 0
        client_counts = {"created": 1, "closed": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal request_count
            request_count += 1
            return httpx.Response(200, content=b"ok", request=request)

        reused = httpx.AsyncClient(transport=httpx.MockTransport(handler))

        async def request_pair() -> tuple[int, int, int]:
            reused_status = (await reused.get(_HTTP_URL)).status_code
            fresh = httpx.AsyncClient(transport=httpx.MockTransport(handler))
            client_counts["created"] += 1
            try:
                fresh_status = (await fresh.get(_HTTP_URL)).status_code
            finally:
                await fresh.aclose()
                assert fresh.is_closed
                client_counts["closed"] += 1
            return reused_status, fresh_status, await _pending_task_count()

        try:
            result = benchmark.pedantic(
                lambda: runner.run(request_pair()),
                rounds=_ROUNDS,
                warmup_rounds=_WARMUP_ROUNDS,
                iterations=1,
            )
        finally:
            runner.run(reused.aclose())
            assert reused.is_closed
            client_counts["closed"] += 1
            runner.close()

        assert result == (200, 200, 0)
        assert request_count > 0
        assert client_counts["created"] == client_counts["closed"]
        _assert_threads_restored(baseline_threads)
        benchmark.extra_info.update(
            {
                "client_created": client_counts["created"],
                "client_closed": client_counts["closed"],
                "pending_tasks_after_round": result[2],
                "request_count": request_count,
                "transport": "httpx.MockTransport",
            }
        )


class TestPoolSnapshot:
    """Measure stable in-memory snapshots across the required pool sizes."""

    @pytest.mark.benchmark(group="modernization-pool-snapshot")
    def test_snapshot_10_100_1000_10000(self, benchmark: Any) -> None:
        baseline_threads = _thread_snapshot()
        sizes = (10, 100, 1000, 10000)
        timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc)
        proxies = [
            Proxy(
                url=f"http://proxy-{index}.example.invalid:{8000 + (index % 1000)}",
                protocol="http",
                health_status=HealthStatus.HEALTHY,
                created_at=timestamp,
                updated_at=timestamp,
            )
            for index in range(max(sizes))
        ]
        fixed_sets = {size: proxies[:size] for size in sizes}

        def snapshot_all_sizes() -> tuple[int, ...]:
            json_lengths: list[int] = []
            for size in sizes:
                snapshot = PoolSnapshot("benchmark-pool", f"snapshot-{size}", timestamp)
                for proxy in fixed_sets[size]:
                    snapshot.add_proxy_state(proxy)
                assert len(snapshot.proxies) == size
                json_lengths.append(len(snapshot.to_json()))
            return tuple(json_lengths)

        result = benchmark.pedantic(
            snapshot_all_sizes,
            rounds=_ROUNDS,
            warmup_rounds=_WARMUP_ROUNDS,
            iterations=1,
        )

        assert len(result) == len(sizes)
        assert all(
            current < following for current, following in zip(result, result[1:], strict=False)
        )
        _assert_threads_restored(baseline_threads)
        benchmark.extra_info.update(
            {
                "proxy_counts": list(sizes),
                "snapshot_json_bytes": list(result),
                "threads_before_after": "balanced",
            }
        )


class TestParserStreaming:
    """Measure the bounded async reader with fixed 1 MiB and 16 MiB streams."""

    @pytest.mark.benchmark(group="modernization-parser-streaming")
    def test_bounded_stream_1mib_16mib(self, benchmark: Any) -> None:
        baseline_threads = _thread_snapshot()
        runner = _AsyncLoopRunner("ModernizationParserBenchmarkLoop")
        sizes = (1 * _MIB, 16 * _MIB)
        payloads = {size: _make_payload(size) for size in sizes}
        stream_counts = {"opened": 0, "closed": 0}

        async def read_one(size: int) -> int:
            stream = _FixedAsyncByteStream(payloads[size])
            stream_counts["opened"] += 1
            response = httpx.Response(
                200,
                request=httpx.Request("GET", _HTTP_URL),
                stream=stream,
            )
            try:
                text = await _read_bounded_response_text(response, max_bytes=size)
                return len(text)
            finally:
                await response.aclose()
                assert stream.closed
                stream_counts["closed"] += 1

        async def read_both_sizes() -> tuple[int, int]:
            lengths = tuple([await read_one(size) for size in sizes])
            return lengths[0], lengths[1]

        gc.collect()
        tracemalloc.start()
        try:
            memory_probe = runner.run(read_both_sizes())
            _, peak_bytes = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()

        peak_limit = (sum(sizes) * 4) + (4 * _MIB)
        assert memory_probe == sizes
        assert runner.run(_settled_pending_task_count()) == 0
        assert peak_bytes <= peak_limit, (
            f"Bounded parser peak {peak_bytes} bytes exceeded {peak_limit} bytes"
        )

        try:
            result = benchmark.pedantic(
                lambda: runner.run(read_both_sizes()),
                rounds=_ROUNDS,
                warmup_rounds=_WARMUP_ROUNDS,
                iterations=1,
            )
        finally:
            pending_tasks_after_rounds = runner.run(_settled_pending_task_count())
            runner.close()

        assert result == sizes
        assert pending_tasks_after_rounds == 0
        assert stream_counts["opened"] == stream_counts["closed"]
        _assert_threads_restored(baseline_threads)
        benchmark.extra_info.update(
            {
                "input_bytes": list(sizes),
                "peak_bytes": peak_bytes,
                "peak_limit_bytes": peak_limit,
                "pending_tasks_after_rounds": pending_tasks_after_rounds,
                "streams_opened": stream_counts["opened"],
                "streams_closed": stream_counts["closed"],
            }
        )


class TestCachePaths:
    """Measure L1, L2, miss, and singleflight stampede paths together."""

    @pytest.mark.benchmark(group="modernization-cache-paths")
    def test_l1_hit_l2_hit_miss_and_stampede(self, tmp_path: Path, benchmark: Any) -> None:
        baseline_threads = _thread_snapshot()
        workers = 8
        executor = ThreadPoolExecutor(
            max_workers=workers,
            thread_name_prefix="ModernizationCacheBenchmark",
        )
        worker_ids = _prewarm_executor(executor, workers)
        manager = CacheManager(
            CacheConfig(
                l1_config=CacheTierConfig(enabled=True, max_entries=512),
                l2_config=CacheTierConfig(enabled=True, max_entries=512),
                l2_backend=L2BackendType.SQLITE,
                l2_cache_dir=str(tmp_path / "l2"),
                l3_config=CacheTierConfig(enabled=False),
                l3_database_path=str(tmp_path / "l3.db"),
                enable_background_cleanup=False,
            )
        )
        assert isinstance(manager.l2_tier, DiskCacheTier)
        assert manager.l2_tier._conn is not None
        round_counter = 0

        def setup_round() -> tuple[tuple[Any, ...], dict[str, Any]]:
            nonlocal round_counter
            round_counter += 1
            manager.clear()
            l1_key = f"l1-{round_counter}"
            l2_key = f"l2-{round_counter}"
            miss_key = f"miss-{round_counter}"
            stampede_key = f"stampede-{round_counter}"
            l1_entry = _make_cache_entry(l1_key)
            l2_entry = _make_cache_entry(l2_key)
            stampede_entry = _make_cache_entry(stampede_key)
            assert manager.l1_tier.put(l1_key, l1_entry)
            assert manager.l2_tier.put(l2_key, l2_entry)

            start_barrier = threading.Barrier(workers + 1)
            leader_started = threading.Event()
            release_loader = threading.Event()
            load_calls = [0]
            load_lock = threading.Lock()

            def loader() -> CacheEntry:
                with load_lock:
                    load_calls[0] += 1
                leader_started.set()
                assert release_loader.wait(timeout=5.0)
                return stampede_entry

            def resolve_stampede() -> CacheEntry:
                start_barrier.wait(timeout=5.0)
                return manager.get_or_load(stampede_key, loader)

            args = (
                l1_key,
                l2_key,
                miss_key,
                stampede_key,
                resolve_stampede,
                start_barrier,
                leader_started,
                release_loader,
                load_calls,
            )
            return args, {}

        def exercise_paths(
            l1_key: str,
            l2_key: str,
            miss_key: str,
            stampede_key: str,
            resolve_stampede: Any,
            start_barrier: threading.Barrier,
            leader_started: threading.Event,
            release_loader: threading.Event,
            load_calls: list[int],
        ) -> tuple[str, str, None, tuple[str, ...], int]:
            l1_result = manager.get(l1_key)
            l2_result = manager.get(l2_key)
            miss_result = manager.get(miss_key)
            futures = [executor.submit(resolve_stampede) for _ in range(workers)]
            try:
                start_barrier.wait(timeout=5.0)
                assert leader_started.wait(timeout=5.0)
                time.sleep(0.005)
            finally:
                release_loader.set()
            stampede_results = tuple(future.result(timeout=5.0).key for future in futures)
            assert l1_result is not None
            assert l2_result is not None
            assert miss_result is None
            assert load_calls[0] == 1
            assert set(stampede_results) == {stampede_key}
            return (
                l1_result.key,
                l2_result.key,
                miss_result,
                stampede_results,
                load_calls[0],
            )

        try:
            result = benchmark.pedantic(
                exercise_paths,
                setup=setup_round,
                rounds=_ROUNDS,
                warmup_rounds=_WARMUP_ROUNDS,
                iterations=1,
            )
        finally:
            connections_before_close = int(manager.l2_tier._conn is not None)
            executor.shutdown(wait=True, cancel_futures=True)
            manager.close()

        assert result[2] is None
        assert result[4] == 1
        assert manager.l2_tier._conn is None
        _assert_threads_restored(baseline_threads)
        benchmark.extra_info.update(
            {
                "l2_backend": "sqlite",
                "l2_connections_before_close": connections_before_close,
                "l2_connections_after_close": 0,
                "singleflight_workers": workers,
                "stampede_loader_calls": result[4],
                "worker_threads": len(worker_ids),
            }
        )


class TestStorageOperations:
    """Measure batch insert, released-row load, and indexed URL query."""

    @pytest.mark.benchmark(group="modernization-storage")
    def test_insert_load_and_indexed_query(self, tmp_path: Path, benchmark: Any) -> None:
        baseline_threads = _thread_snapshot()
        runner = _AsyncLoopRunner("ModernizationStorageBenchmarkLoop")
        storage = SQLiteStorage(tmp_path / "modernization-storage.db")
        proxies = [
            Proxy(
                url=f"http://storage-{index}.example.invalid:{9000 + index}",
                protocol="http",
                health_status=HealthStatus.HEALTHY,
            )
            for index in range(64)
        ]
        indexed_urls = [proxy.url for proxy in proxies[::4]]
        runner.run(storage.initialize())
        assert _checked_out_connections(storage) == 0

        def setup_round() -> None:
            runner.run(storage.clear())
            assert _checked_out_connections(storage) == 0

        async def exercise_storage() -> tuple[int, int, int, int, int]:
            added, skipped = await storage.add_proxies_batch(proxies, validated=True)
            loaded = await storage.load()
            indexed = await storage.get_proxies_batch(indexed_urls)
            return (
                added,
                skipped,
                len(loaded),
                len(indexed),
                _checked_out_connections(storage),
            )

        try:
            result = benchmark.pedantic(
                lambda: runner.run(exercise_storage()),
                setup=setup_round,
                rounds=_ROUNDS,
                warmup_rounds=_WARMUP_ROUNDS,
                iterations=1,
            )
        finally:
            connections_checked_in_before_close = _checked_in_connections(storage)
            runner.run(storage.close())
            connections_checked_in_after_close = _checked_in_connections(storage)
            connections_after_close = _checked_out_connections(storage)
            runner.close()

        assert result == (len(proxies), 0, len(proxies), len(indexed_urls), 0)
        assert connections_after_close == 0
        assert connections_checked_in_before_close > 0
        assert connections_checked_in_after_close == 0
        _assert_threads_restored(baseline_threads)
        benchmark.extra_info.update(
            {
                "inserted_rows": result[0],
                "loaded_rows": result[2],
                "indexed_query_rows": result[3],
                "connections_checked_out_after_round": result[4],
                "connections_checked_out_after_close": connections_after_close,
                "connections_checked_in_before_close": connections_checked_in_before_close,
                "connections_checked_in_after_close": connections_checked_in_after_close,
                "pending_tasks_after_close": 0,
            }
        )
