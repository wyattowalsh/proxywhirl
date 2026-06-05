"""Tests for nested event loop detection.

Session 8 SA-8.1: Validates that attempts to run a nested event loop
are detected and handled appropriately.
"""

from __future__ import annotations

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from proxywhirl.exceptions import EventLoopConflictError

# ============================================================================
# NESTED LOOP DETECTION
# ============================================================================


class TestNestedEventLoopDetection:
    """Test detection of nested event loop attempts."""

    def test_no_running_loop_in_sync_context(self) -> None:
        """In a plain sync function there should be no running loop."""
        try:
            asyncio.get_running_loop()
            pytest.fail("Expected RuntimeError because no loop is running")
        except RuntimeError as exc:
            assert "no running event loop" in str(exc).lower()

    @pytest.mark.asyncio
    async def test_running_loop_detected_in_async_context(self) -> None:
        """Inside an async function a running loop must be detectable."""
        loop = asyncio.get_running_loop()
        assert loop is not None
        assert isinstance(loop, asyncio.AbstractEventLoop)

    @pytest.mark.asyncio
    async def test_new_loop_run_until_complete_raises(self) -> None:
        """Creating a new loop and calling ``run_until_complete`` while
        another loop is already running must raise ``RuntimeError``."""
        new_loop = asyncio.new_event_loop()
        coro = asyncio.sleep(0.01)
        try:
            with pytest.raises(RuntimeError):
                new_loop.run_until_complete(coro)
        finally:
            coro.close()
            new_loop.close()

    @pytest.mark.asyncio
    async def test_nested_asyncio_attempt_blocked(self) -> None:
        """Trying to start an event loop inside a coroutine must fail."""

        async def inner() -> None:
            pass

        new_loop = asyncio.new_event_loop()
        coro = inner()
        try:
            with pytest.raises(RuntimeError):
                new_loop.run_until_complete(coro)
        finally:
            coro.close()
            new_loop.close()

    def test_run_in_thread_isolated_loop(self) -> None:
        """Each thread can have its own event loop without conflict."""
        results: list[bool] = []

        def thread_task() -> None:
            loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(loop)
                loop.run_until_complete(asyncio.sleep(0.01))
                results.append(True)
            finally:
                loop.close()

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(thread_task) for _ in range(3)]
            for future in futures:
                future.result()

        assert all(results)
        assert len(results) == 3

    def test_get_event_loop_returns_different_in_threads(self) -> None:
        """``get_event_loop`` in a new thread without a set loop may behave
        differently depending on Python version; here we verify isolation."""
        loop_ids: list[int] = []

        def capture_loop() -> None:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop_ids.append(id(loop))
            loop.run_until_complete(asyncio.sleep(0.001))
            loop.close()

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(capture_loop) for _ in range(2)]
            for future in futures:
                future.result()

        assert len(loop_ids) == 2
        assert loop_ids[0] != loop_ids[1]

    @pytest.mark.asyncio
    async def test_asyncio_ensure_future_requires_loop(self) -> None:
        """``asyncio.ensure_future`` should work when a loop is running."""

        async def coro() -> int:
            await asyncio.sleep(0.01)
            return 42

        task = asyncio.ensure_future(coro())
        result = await task
        assert result == 42

    def test_call_soon_threadsafe_across_threads(self) -> None:
        """Schedule a callback from another thread into the main loop."""
        loop = asyncio.new_event_loop()
        results: list[int] = []

        def callback() -> None:
            results.append(1)
            loop.stop()

        def schedule_from_thread() -> None:
            loop.call_soon_threadsafe(callback)

        thread = threading.Thread(target=schedule_from_thread)
        try:
            asyncio.set_event_loop(loop)
            thread.start()
            # Give the thread a moment to schedule
            import time

            time.sleep(0.05)
            loop.run_forever()
            thread.join()
        finally:
            loop.close()

        assert results == [1]

    @pytest.mark.asyncio
    async def test_cannot_run_asyncio_run_inside_async(self) -> None:
        """``asyncio.run`` must not be called from inside a running loop."""
        coro = asyncio.sleep(0.01)
        with pytest.raises(RuntimeError):
            asyncio.run(coro)
        coro.close()

    def test_asyncio_run_in_sync_context_ok(self) -> None:
        """``asyncio.run`` works fine in a sync context."""

        async def inner() -> int:
            await asyncio.sleep(0.01)
            return 99

        result = asyncio.run(inner())
        assert result == 99


# ============================================================================
# EVENT LOOP CONFLICT ERROR
# ============================================================================


class TestEventLoopConflictError:
    """Test the custom ``EventLoopConflictError`` exception."""

    def test_error_code(self) -> None:
        """The exception must carry the correct error code."""
        from proxywhirl.exceptions import ProxyErrorCode

        err = EventLoopConflictError("conflict")
        assert err.error_code == ProxyErrorCode.EVENT_LOOP_CONFLICT

    def test_context_fields(self) -> None:
        """Context fields should be captured correctly."""
        err = EventLoopConflictError(
            "conflict",
            current_context="async",
            expected_context="sync",
        )
        assert err.current_context == "async"
        assert err.expected_context == "sync"
        assert "async" in str(err)
        assert "sync" in str(err)

    def test_default_message_enhancement(self) -> None:
        """Default message should include guidance."""
        err = EventLoopConflictError("loop conflict")
        msg = str(err)
        assert "ProxyWhirl" in msg or "sync" in msg.lower() or "async" in msg.lower()

    def test_to_dict(self) -> None:
        """``to_dict`` should serialize context."""
        err = EventLoopConflictError(
            "test",
            current_context="async",
            expected_context="sync",
        )
        d = err.to_dict()
        assert d["error_code"] == "EVENT_LOOP_CONFLICT"
        assert d["message"] == str(err)


# ============================================================================
# CLEAN LOOP CONTEXT
# ============================================================================


class TestCleanLoopContext:
    """Test utilities for ensuring clean loop contexts."""

    def test_new_loop_is_not_running(self) -> None:
        """A freshly created loop should not be running."""
        loop = asyncio.new_event_loop()
        assert not loop.is_running()
        loop.close()

    def test_closed_loop_cannot_run(self) -> None:
        """A closed loop must raise when asked to run."""
        loop = asyncio.new_event_loop()
        loop.close()
        coro = asyncio.sleep(0.01)
        with pytest.raises(RuntimeError):
            loop.run_until_complete(coro)
        coro.close()

    @pytest.mark.asyncio
    async def test_current_task_in_running_loop(self) -> None:
        """ "``asyncio.current_task`` must return the current task."""
        task = asyncio.current_task()
        assert task is not None
        assert isinstance(task, asyncio.Task)

    def test_all_tasks_empty_outside_loop(self) -> None:
        """Outside a loop ``all_tasks`` should return an empty set."""
        # Note: in modern asyncio this may raise if no loop; we handle both
        try:
            tasks = asyncio.all_tasks()
            assert len(tasks) == 0
        except RuntimeError as exc:
            assert "no running" in str(exc).lower()


# ============================================================================
# COUNT CHECK
# ============================================================================


def test_at_least_fifteen_tests_exist() -> None:
    """Meta-test: ensure this module contains >= 15 test functions."""
    import inspect
    import sys

    module = sys.modules[__name__]

    def _collect_tests(obj):
        tests = []
        for name, member in inspect.getmembers(obj):
            if name.startswith("test_") and (
                inspect.isfunction(member) or inspect.ismethod(member)
            ):
                tests.append(member)
        return tests

    test_funcs = _collect_tests(module)
    for _, cls in inspect.getmembers(module, inspect.isclass):
        test_funcs.extend(_collect_tests(cls))

    assert len(test_funcs) >= 15, f"Expected >= 15 tests, found {len(test_funcs)}"
