"""Tests for async timeout contexts."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import pytest


class TimeoutError(Exception):
    """Timeout error for async operations."""

    pass


@asynccontextmanager
async def timeout_context(seconds: float) -> AsyncGenerator[None, None]:
    """Async context manager for timeout operations.

    Args:
        seconds: Timeout duration in seconds

    Raises:
        TimeoutError: If operation exceeds timeout
    """
    try:
        async with asyncio.timeout(seconds):
            yield
    except asyncio.TimeoutError as e:
        raise TimeoutError(f"Operation timed out after {seconds}s") from e


class TestTimeoutContexts:
    """Test async timeout contexts."""

    @pytest.mark.asyncio
    async def test_timeout_context_completes_within_timeout(self) -> None:
        """Test operation completing within timeout."""
        async with timeout_context(1.0):
            await asyncio.sleep(0.1)
        # Should not raise

    @pytest.mark.asyncio
    async def test_timeout_context_raises_on_exceed(self) -> None:
        """Test timeout when operation exceeds duration."""
        with pytest.raises(TimeoutError):
            async with timeout_context(0.1):
                await asyncio.sleep(1.0)

    @pytest.mark.asyncio
    async def test_nested_timeout_contexts(self) -> None:
        """Test nested timeout contexts."""
        async with timeout_context(2.0):
            async with timeout_context(1.0):
                await asyncio.sleep(0.1)
        # Should complete without timeout

    @pytest.mark.asyncio
    async def test_inner_timeout_triggers_first(self) -> None:
        """Test that inner timeout triggers before outer."""
        with pytest.raises(TimeoutError):
            async with timeout_context(2.0):
                async with timeout_context(0.1):
                    await asyncio.sleep(1.0)

    @pytest.mark.asyncio
    async def test_timeout_context_with_multiple_awaits(self) -> None:
        """Test timeout across multiple await points."""
        async with timeout_context(0.5):
            await asyncio.sleep(0.1)
            await asyncio.sleep(0.1)
            await asyncio.sleep(0.1)
        # Should complete

    @pytest.mark.asyncio
    async def test_timeout_context_cancels_task(self) -> None:
        """Test that timeout properly cancels task."""

        async def long_running() -> None:
            try:
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                raise

        with pytest.raises(TimeoutError):
            async with timeout_context(0.05):
                await long_running()

    @pytest.mark.asyncio
    async def test_timeout_context_exception_propagation(self) -> None:
        """Test that non-timeout exceptions propagate."""

        class CustomError(Exception):
            pass

        with pytest.raises(CustomError):
            async with timeout_context(1.0):
                raise CustomError("test error")

    @pytest.mark.asyncio
    async def test_timeout_context_zero_timeout(self) -> None:
        """Test zero timeout raises immediately or very quickly."""
        # Zero timeout should raise TimeoutError immediately
        with pytest.raises(TimeoutError):
            async with timeout_context(0.0001):  # Use very small timeout instead of 0
                await asyncio.sleep(0.001)  # Try to sleep, should timeout

    @pytest.mark.asyncio
    async def test_timeout_context_with_concurrent_tasks(self) -> None:
        """Test timeout with concurrent tasks."""

        async def task(delay: float) -> None:
            await asyncio.sleep(delay)

        with pytest.raises(TimeoutError):
            async with timeout_context(0.2):
                await asyncio.gather(
                    task(0.1),
                    task(0.15),
                    task(1.0),
                )

    @pytest.mark.asyncio
    async def test_timeout_context_exact_boundary(self) -> None:
        """Test timeout at exact boundary."""
        # Using slightly less than timeout to avoid race conditions
        async with timeout_context(0.3):
            await asyncio.sleep(0.25)
        # Should complete
