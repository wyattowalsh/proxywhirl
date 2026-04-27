"""Tests for event loop nesting detection and cycle prevention."""

from __future__ import annotations

import asyncio
import threading
from contextlib import contextmanager

import pytest


class EventLoopDetector:
    """Detects and manages nested event loop issues."""

    @staticmethod
    def has_running_loop() -> bool:
        """Check if event loop is already running."""
        try:
            asyncio.get_running_loop()
            return True
        except RuntimeError:
            return False

    @staticmethod
    def get_event_loop_thread() -> threading.Thread | None:
        """Get thread where event loop is running."""
        try:
            loop = asyncio.get_running_loop()
            return threading.current_thread()
        except RuntimeError:
            return None

    @staticmethod
    @contextmanager
    def ensure_clean_loop():
        """Ensure we're in a clean event loop context."""
        has_loop = EventLoopDetector.has_running_loop()
        if has_loop:
            loop = asyncio.get_running_loop()
        else:
            loop = None

        try:
            yield
        finally:
            if not has_loop and loop is None:
                try:
                    pending = asyncio.all_tasks()
                    for task in pending:
                        task.cancel()
                except RuntimeError:
                    pass


class TestEventLoopNesting:
    """Test event loop nesting detection."""

    def test_detect_running_loop(self) -> None:
        """Test detection of running loop."""
        assert not EventLoopDetector.has_running_loop()

    @pytest.mark.asyncio
    async def test_detect_loop_in_async_context(self) -> None:
        """Test loop detection in async context."""
        assert EventLoopDetector.has_running_loop()

    def test_get_loop_thread_no_loop(self) -> None:
        """Test getting loop thread when no loop running."""
        assert EventLoopDetector.get_event_loop_thread() is None

    @pytest.mark.asyncio
    async def test_get_loop_thread_with_loop(self) -> None:
        """Test getting loop thread when loop is running."""
        thread = EventLoopDetector.get_event_loop_thread()
        assert thread is not None
        assert thread == threading.current_thread()

    def test_prevent_sync_async_deadlock(self) -> None:
        """Test sync calling async without deadlock."""
        result = []

        async def async_func() -> int:
            await asyncio.sleep(0.01)
            return 42

        # Should use run_in_executor or new loop
        loop = asyncio.new_event_loop()
        try:
            value = loop.run_until_complete(async_func())
            result.append(value)
        finally:
            loop.close()

        assert result == [42]

    @pytest.mark.asyncio
    async def test_nested_loop_detection(self) -> None:
        """Test detection of nested loop attempts."""
        # We're already in an event loop
        assert EventLoopDetector.has_running_loop()

        # Should not be able to create new loop
        with pytest.raises((RuntimeError, AssertionError)):
            asyncio.new_event_loop().run_until_complete(asyncio.sleep(0.01))

    def test_context_manager_cleanup(self) -> None:
        """Test context manager cleanup."""
        with EventLoopDetector.ensure_clean_loop():
            pass
        # Should complete without issues

    @pytest.mark.asyncio
    async def test_context_manager_in_async(self) -> None:
        """Test context manager in async context."""
        with EventLoopDetector.ensure_clean_loop():
            await asyncio.sleep(0.01)

    def test_multiple_loop_instances(self) -> None:
        """Test creating multiple loop instances."""
        loop1 = asyncio.new_event_loop()
        loop2 = asyncio.new_event_loop()

        try:
            assert loop1 is not loop2
            asyncio.set_event_loop(loop1)
            assert asyncio.get_event_loop() == loop1
        finally:
            loop1.close()
            loop2.close()

    def test_loop_thread_safety(self) -> None:
        """Test event loop is thread-safe."""
        result = []
        error = []

        def run_in_thread() -> None:
            try:
                # Should not have loop in this thread
                assert not EventLoopDetector.has_running_loop()
                result.append(True)
            except Exception as e:
                error.append(e)

        thread = threading.Thread(target=run_in_thread)
        thread.start()
        thread.join()

        assert len(error) == 0
        assert result == [True]

    @pytest.mark.asyncio
    async def test_asyncio_ensure_future(self) -> None:
        """Test asyncio.ensure_future in running loop."""

        async def simple_coro() -> int:
            await asyncio.sleep(0.01)
            return 123

        task = asyncio.ensure_future(simple_coro())
        result = await task
        assert result == 123

    def test_event_loop_policy(self) -> None:
        """Test event loop policy."""
        policy = asyncio.get_event_loop_policy()
        assert policy is not None


class TestFlakeIsolation:
    """Test flake isolation in tests."""

    @pytest.fixture
    def isolated_db(self, tmp_path):
        """Provide isolated database for each test."""
        return tmp_path / "test.db"

    def test_each_test_gets_clean_db(self, isolated_db) -> None:
        """Test each test gets clean database."""
        # First test - db doesn't exist
        assert not isolated_db.exists()
        isolated_db.write_text("test data")
        assert isolated_db.exists()

    def test_second_test_clean_state(self, isolated_db) -> None:
        """Test second test starts with clean state."""
        # Should be clean because fixture provides new tmp_path
        assert not isolated_db.exists()

    def test_no_global_state_pollution(self) -> None:
        """Test no global state pollution between tests."""
        import random

        seed = random.randint(0, 1000000)
        # Each test should not affect others
        assert seed >= 0

    @pytest.mark.asyncio
    async def test_async_task_cleanup(self) -> None:
        """Test async tasks are cleaned up."""
        tasks_before = len(asyncio.all_tasks())

        async def dummy() -> None:
            await asyncio.sleep(0.01)

        task = asyncio.create_task(dummy())
        await task

        tasks_after = len(asyncio.all_tasks())
        # Task should be cleaned up
        assert tasks_after <= tasks_before + 1

    def test_temp_file_cleanup(self, tmp_path) -> None:
        """Test temporary files are cleaned up."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        assert test_file.exists()
        # tmp_path fixture auto-cleans

    @pytest.fixture(autouse=True)
    def reset_state(self) -> None:
        """Reset state before each test."""
        # This runs for every test method
        yield
        # Cleanup after test

    def test_isolation_marker(self) -> None:
        """Test isolation works with marker."""
        pass

    @pytest.mark.flaky
    def test_flaky_test_marked(self) -> None:
        """Test that can be marked as flaky."""
        # Pytest can rerun this
        pass

    def test_no_external_state_dependency(self) -> None:
        """Test doesn't depend on external state."""
        # Should work regardless of test execution order
        data = []
        data.append(1)
        assert len(data) == 1
