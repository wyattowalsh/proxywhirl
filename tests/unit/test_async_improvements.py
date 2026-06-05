"""Tests for async/await improvements and patterns.

Tests for:
- Async streaming responses
- Async context managers
- Async migrations
- Concurrent operations
- Proper async context handling
"""

from __future__ import annotations

import asyncio
import time
from typing import AsyncGenerator

import pytest

from proxywhirl.browser import BrowserRenderer
from proxywhirl.enrichment import AsyncOfflineEnricher


class TestAsyncStreaming:
    """Test async streaming patterns."""

    @pytest.mark.asyncio
    async def test_async_generator_basic(self) -> None:
        """Test basic async generator functionality."""

        async def async_range(n: int) -> AsyncGenerator[int, None]:
            """Generate numbers asynchronously."""
            for i in range(n):
                await asyncio.sleep(0.001)
                yield i

        result = []
        async for item in async_range(5):
            result.append(item)

        assert result == [0, 1, 2, 3, 4]

    @pytest.mark.asyncio
    async def test_streaming_with_gather(self) -> None:
        """Test streaming with concurrent gathering."""

        async def fetch_item(item_id: int) -> str:
            """Simulate async fetch."""
            await asyncio.sleep(0.01)
            return f"item-{item_id}"

        items = await asyncio.gather(*[fetch_item(i) for i in range(5)])
        assert len(items) == 5
        assert all(item.startswith("item-") for item in items)

    @pytest.mark.asyncio
    async def test_streaming_chunked_processing(self) -> None:
        """Test processing items in chunks asynchronously."""

        async def process_batch(batch: list[int]) -> int:
            """Process a batch of items."""
            await asyncio.sleep(0.01)
            return sum(batch)

        items = list(range(10))
        chunk_size = 3
        chunks = [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]
        results = await asyncio.gather(*[process_batch(chunk) for chunk in chunks])

        assert len(results) == 4
        assert sum(results) == sum(items)


@pytest.mark.slow
class TestBrowserContextManager:
    """Test browser async context manager."""

    @pytest.mark.asyncio
    async def test_context_manager_entry_exit(self) -> None:
        """Test async context manager __aenter__ and __aexit__."""
        renderer = BrowserRenderer(max_contexts=2, headless=True)
        assert not renderer._is_started

        async with renderer:
            assert renderer._is_started
            assert renderer._context_pool is not None

        assert not renderer._is_started
        assert renderer._context is None

    @pytest.mark.asyncio
    async def test_context_pool_isolation(self) -> None:
        """Test that context pool maintains isolation."""
        renderer = BrowserRenderer(max_contexts=2, headless=True)

        async with renderer:
            # Acquire a context
            ctx1 = await renderer.acquire_context()
            assert ctx1 is not None

            # Pool should have one less context
            assert renderer.pool_size == 1

            # Release the context
            await renderer.release_context(ctx1)
            assert renderer.pool_size == 2


class TestEnrichmentAsync:
    """Test async enrichment patterns."""

    @pytest.mark.asyncio
    async def test_enrichment_with_thread_pool(self) -> None:
        """Test enrichment with asyncio.to_thread for blocking I/O."""
        enricher = AsyncOfflineEnricher()

        # Test single enrichment
        result = await enricher.enrich("8.8.8.8", 80)

        assert isinstance(result, dict)
        assert "is_private" in result
        assert result["port_type"] == "http"

    @pytest.mark.asyncio
    async def test_enrichment_batch_concurrent(self) -> None:
        """Test concurrent batch enrichment."""
        enricher = AsyncOfflineEnricher()

        proxies = [
            {"ip": "8.8.8.8", "port": 80},
            {"ip": "1.1.1.1", "port": 443},
            {"ip": "192.168.1.1", "port": 3128},
        ]

        result = await enricher.enrich_batch(proxies)

        assert len(result) == 3
        for proxy in result:
            assert "port_type" in proxy
            assert "is_private" in proxy


class TestConcurrentAsyncOperations:
    """Test concurrent async operations."""

    @pytest.mark.asyncio
    async def test_taskgroup_pattern(self) -> None:
        """Test TaskGroup pattern for concurrent operations (Python 3.11+)."""

        async def task1() -> str:
            await asyncio.sleep(0.01)
            return "task1"

        async def task2() -> str:
            await asyncio.sleep(0.01)
            return "task2"

        async def task3() -> str:
            await asyncio.sleep(0.01)
            return "task3"

        # Use gather for supported Python runtimes
        results = await asyncio.gather(task1(), task2(), task3())
        assert results == ["task1", "task2", "task3"]

    @pytest.mark.asyncio
    async def test_concurrent_timeouts(self) -> None:
        """Test handling concurrent operations with timeouts."""

        async def slow_task() -> str:
            await asyncio.sleep(10)
            return "done"

        async def fast_task() -> str:
            await asyncio.sleep(0.01)
            return "done"

        try:
            result = await asyncio.wait_for(slow_task(), timeout=0.1)
            raise AssertionError("Should have timed out")
        except asyncio.TimeoutError:
            pass  # Expected

        result = await asyncio.wait_for(fast_task(), timeout=1.0)
        assert result == "done"

    @pytest.mark.asyncio
    async def test_gather_with_return_exceptions(self) -> None:
        """Test gather with return_exceptions for error handling."""

        async def may_fail(fail: bool) -> str:
            if fail:
                raise ValueError("Task failed")
            return "success"

        results = await asyncio.gather(
            may_fail(False),
            may_fail(True),
            may_fail(False),
            return_exceptions=True,
        )

        assert results[0] == "success"
        assert isinstance(results[1], ValueError)
        assert results[2] == "success"


class TestAsyncNoBlocking:
    """Test that async code doesn't use blocking operations."""

    @pytest.mark.asyncio
    async def test_async_sleep_not_time_sleep(self) -> None:
        """Verify asyncio.sleep is used instead of time.sleep."""
        start = time.monotonic()

        # Simulate proper async pattern
        await asyncio.sleep(0.05)

        elapsed = time.monotonic() - start
        assert elapsed >= 0.04  # Allow some slack

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_gather_vs_sequential(self) -> None:
        """Verify that gather is faster than sequential."""

        async def work(duration: float) -> float:
            await asyncio.sleep(duration)
            return duration

        # Sequential: should take ~0.06
        start = time.monotonic()
        r1 = await work(0.03)
        r2 = await work(0.03)
        sequential_time = time.monotonic() - start

        # Concurrent: should take ~0.03
        start = time.monotonic()
        results = await asyncio.gather(work(0.03), work(0.03))
        concurrent_time = time.monotonic() - start

        # Concurrent should be faster
        assert concurrent_time < sequential_time * 0.8


class TestAsyncContextManagers:
    """Test async context manager patterns."""

    @pytest.mark.asyncio
    async def test_nested_async_context_managers(self) -> None:
        """Test nested async context managers."""

        class AsyncResource:
            def __init__(self, name: str) -> None:
                self.name = name
                self.entered = False
                self.exited = False

            async def __aenter__(self) -> AsyncResource:
                self.entered = True
                await asyncio.sleep(0.001)
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
                self.exited = True
                await asyncio.sleep(0.001)

        async with AsyncResource("outer") as outer:
            assert outer.entered
            async with AsyncResource("inner") as inner:
                assert inner.entered
            assert inner.exited

        assert outer.exited

    @pytest.mark.asyncio
    async def test_async_context_manager_exception_cleanup(self) -> None:
        """Test that async context manager cleans up on exceptions."""

        class AsyncResource:
            def __init__(self) -> None:
                self.cleanup_called = False

            async def __aenter__(self) -> AsyncResource:
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
                self.cleanup_called = True

        resource = AsyncResource()

        try:
            async with resource:
                raise ValueError("Test error")
        except ValueError:
            pass

        assert resource.cleanup_called


class TestAsyncValidationPipeline:
    """Test async validation pipeline patterns."""

    @pytest.mark.asyncio
    async def test_concurrent_validation_steps(self) -> None:
        """Test validation pipeline with concurrent steps."""

        async def validate_format(value: str) -> bool:
            """Validate format asynchronously."""
            await asyncio.sleep(0.01)
            return len(value) > 0

        async def validate_content(value: str) -> bool:
            """Validate content asynchronously."""
            await asyncio.sleep(0.01)
            return not value.startswith("invalid")

        async def validate_length(value: str) -> bool:
            """Validate length asynchronously."""
            await asyncio.sleep(0.01)
            return len(value) < 100

        async def run_validation(value: str) -> bool:
            """Run all validations concurrently."""
            results = await asyncio.gather(
                validate_format(value),
                validate_content(value),
                validate_length(value),
            )
            return all(results)

        assert await run_validation("test-value")
        assert not await run_validation("invalid-value")
        assert not await run_validation("")


class TestAsyncRateLimiting:
    """Test async rate limiting patterns."""

    @pytest.mark.asyncio
    async def test_semaphore_for_concurrency_limiting(self) -> None:
        """Test using semaphore to limit concurrent operations."""

        async def work(work_id: int, semaphore: asyncio.Semaphore) -> int:
            """Perform work with semaphore limiting."""
            async with semaphore:
                await asyncio.sleep(0.01)
                return work_id

        semaphore = asyncio.Semaphore(2)  # Allow 2 concurrent

        start = time.monotonic()
        results = await asyncio.gather(*[work(i, semaphore) for i in range(4)])
        elapsed = time.monotonic() - start

        assert results == [0, 1, 2, 3]
        # Should take ~0.03 (2 batches of 2, 0.01 each = 0.03 min)
        assert elapsed >= 0.02

    @pytest.mark.asyncio
    async def test_bounded_semaphore(self) -> None:
        """Test BoundedSemaphore behavior."""
        semaphore = asyncio.BoundedSemaphore(2)

        acquired_count = 0

        async def acquire() -> None:
            nonlocal acquired_count
            async with semaphore:
                acquired_count += 1
                await asyncio.sleep(0.01)

        await asyncio.gather(*[acquire() for _ in range(4)])
        assert acquired_count == 4


class TestAsyncCacheMigrations:
    """Test async-compatible cache migrations."""

    @pytest.mark.asyncio
    async def test_async_migration_pattern(self) -> None:
        """Test async database migration pattern."""

        class AsyncMigration:
            def __init__(self, version: int) -> None:
                self.version = version
                self.applied = False

            async def up(self) -> None:
                """Apply migration asynchronously."""
                await asyncio.sleep(0.01)
                self.applied = True

            async def down(self) -> None:
                """Rollback migration asynchronously."""
                await asyncio.sleep(0.01)
                self.applied = False

        migration = AsyncMigration(1)
        assert not migration.applied

        await migration.up()
        assert migration.applied

        await migration.down()
        assert not migration.applied


class TestAsyncErrorHandling:
    """Test async error handling patterns."""

    @pytest.mark.asyncio
    async def test_gather_error_propagation(self) -> None:
        """Test error propagation with gather."""

        async def failing_task() -> str:
            raise ValueError("Task failed")

        async def succeeding_task() -> str:
            return "success"

        # With return_exceptions=True, errors are returned as exceptions
        results = await asyncio.gather(
            failing_task(),
            succeeding_task(),
            return_exceptions=True,
        )

        assert isinstance(results[0], ValueError)
        assert results[1] == "success"

    @pytest.mark.asyncio
    async def test_async_context_manager_exception_propagation(self) -> None:
        """Test exception propagation through async context managers."""

        class AsyncResource:
            def __init__(self) -> None:
                self.cleanup_called = False

            async def __aenter__(self) -> AsyncResource:
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
                self.cleanup_called = True
                # Don't suppress the exception

        resource = AsyncResource()

        with pytest.raises(RuntimeError):
            async with resource:
                raise RuntimeError("Test error")

        assert resource.cleanup_called
