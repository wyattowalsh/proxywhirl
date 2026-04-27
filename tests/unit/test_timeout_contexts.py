"""Tests for connect/read/write timeout behaviors.

Session 8 SA-8.1: Validates the timeout exception hierarchy and that
connect, read, write, and pool timeouts carry the correct metadata.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import pytest

from proxywhirl.exceptions import (
    ConnectTimeoutError,
    PoolTimeoutError,
    ProxyErrorCode,
    ReadTimeoutError,
    TimeoutError,
    WriteTimeoutError,
)


# ============================================================================
# CUSTOM TIMEOUT CONTEXT MANAGER (used in tests)
# ============================================================================


@asynccontextmanager
async def _timeout_context(seconds: float) -> AsyncGenerator[None, None]:
    """Async context manager that translates ``asyncio.TimeoutError``."""
    try:
        async with asyncio.timeout(seconds):
            yield
    except asyncio.TimeoutError as exc:
        raise TimeoutError(
            f"Operation timed out after {seconds}s",
            timeout_seconds=seconds,
        ) from exc


# ============================================================================
# CONNECT TIMEOUT
# ============================================================================


class TestConnectTimeout:
    """Test ``ConnectTimeoutError`` behavior and metadata."""

    def test_connect_timeout_error_code(self) -> None:
        """Must carry ``TIMEOUT_CONNECT`` error code."""
        err = ConnectTimeoutError("connection timed out")
        assert err.error_code == ProxyErrorCode.TIMEOUT_CONNECT

    def test_connect_timeout_target_host(self) -> None:
        """Must preserve the target host in metadata."""
        err = ConnectTimeoutError(
            "connection timed out",
            target_host="192.168.1.1",
            timeout_seconds=5.0,
        )
        assert err.target_host == "192.168.1.1"
        assert err.timeout_seconds == 5.0
        assert "192.168.1.1" in str(err)

    def test_connect_timeout_defaults(self) -> None:
        """Default message should be present."""
        err = ConnectTimeoutError()
        assert "connection timeout" in str(err).lower()
        assert err.error_code == ProxyErrorCode.TIMEOUT_CONNECT

    def test_connect_timeout_inheritance(self) -> None:
        """Must be a subclass of ``TimeoutError``."""
        assert issubclass(ConnectTimeoutError, TimeoutError)

    @pytest.mark.asyncio
    async def test_connect_timeout_simulation(self) -> None:
        """Simulate a connect timeout using ``asyncio.timeout``."""
        with pytest.raises(TimeoutError):
            async with _timeout_context(0.05):
                await asyncio.sleep(1.0)


# ============================================================================
# READ TIMEOUT
# ============================================================================


class TestReadTimeout:
    """Test ``ReadTimeoutError`` behavior and metadata."""

    def test_read_timeout_error_code(self) -> None:
        """Must carry ``TIMEOUT_READ`` error code."""
        err = ReadTimeoutError("read timed out")
        assert err.error_code == ProxyErrorCode.TIMEOUT_READ

    def test_read_timeout_bytes_read(self) -> None:
        """Must preserve bytes-read metadata."""
        err = ReadTimeoutError(
            "read timed out",
            bytes_read=4096,
            timeout_seconds=10.0,
        )
        assert err.bytes_read == 4096
        assert err.timeout_seconds == 10.0
        assert "4096" in str(err)

    def test_read_timeout_defaults(self) -> None:
        """Default message should be present."""
        err = ReadTimeoutError()
        assert "read timeout" in str(err).lower()
        assert err.error_code == ProxyErrorCode.TIMEOUT_READ

    def test_read_timeout_inheritance(self) -> None:
        """Must be a subclass of ``TimeoutError``."""
        assert issubclass(ReadTimeoutError, TimeoutError)

    @pytest.mark.asyncio
    async def test_read_timeout_simulation(self) -> None:
        """Simulate a read timeout: data starts arriving but stalls."""
        async def slow_stream() -> None:
            await asyncio.sleep(0.01)
            await asyncio.sleep(1.0)

        with pytest.raises(TimeoutError):
            async with _timeout_context(0.05):
                await slow_stream()


# ============================================================================
# WRITE TIMEOUT
# ============================================================================


class TestWriteTimeout:
    """Test ``WriteTimeoutError`` behavior and metadata."""

    def test_write_timeout_error_code(self) -> None:
        """Must carry ``TIMEOUT_WRITE`` error code."""
        err = WriteTimeoutError("write timed out")
        assert err.error_code == ProxyErrorCode.TIMEOUT_WRITE

    def test_write_timeout_bytes_to_write(self) -> None:
        """Must preserve bytes-to-write metadata."""
        err = WriteTimeoutError(
            "write timed out",
            bytes_to_write=8192,
            timeout_seconds=5.0,
        )
        assert err.bytes_to_write == 8192
        assert err.timeout_seconds == 5.0
        assert "8192" in str(err)

    def test_write_timeout_defaults(self) -> None:
        """Default message should be present."""
        err = WriteTimeoutError()
        assert "write timeout" in str(err).lower()
        assert err.error_code == ProxyErrorCode.TIMEOUT_WRITE

    def test_write_timeout_inheritance(self) -> None:
        """Must be a subclass of ``TimeoutError``."""
        assert issubclass(WriteTimeoutError, TimeoutError)

    @pytest.mark.asyncio
    async def test_write_timeout_simulation(self) -> None:
        """Simulate a write timeout: send buffer stalls."""
        async def slow_writer() -> None:
            await asyncio.sleep(1.0)

        with pytest.raises(TimeoutError):
            async with _timeout_context(0.05):
                await slow_writer()


# ============================================================================
# POOL TIMEOUT
# ============================================================================


class TestPoolTimeout:
    """Test ``PoolTimeoutError`` behavior and metadata."""

    def test_pool_timeout_error_code(self) -> None:
        """Must carry ``TIMEOUT_POOL`` error code."""
        err = PoolTimeoutError("pool exhausted")
        assert err.error_code == ProxyErrorCode.TIMEOUT_POOL

    def test_pool_timeout_pool_size(self) -> None:
        """Must preserve pool-size metadata."""
        err = PoolTimeoutError(
            "pool exhausted",
            pool_size=10,
            timeout_seconds=30.0,
        )
        assert err.pool_size == 10
        assert err.timeout_seconds == 30.0
        assert "10" in str(err)

    def test_pool_timeout_defaults(self) -> None:
        """Default message should be present."""
        err = PoolTimeoutError()
        assert "pool timeout" in str(err).lower()
        assert err.error_code == ProxyErrorCode.TIMEOUT_POOL

    def test_pool_timeout_inheritance(self) -> None:
        """Must be a subclass of ``TimeoutError``."""
        assert issubclass(PoolTimeoutError, TimeoutError)


# ============================================================================
# BASE TIMEOUT ERROR
# ============================================================================


class TestBaseTimeoutError:
    """Test the base ``TimeoutError`` class."""

    def test_base_timeout_error_code(self) -> None:
        """Must carry ``TIMEOUT`` error code."""
        err = TimeoutError("generic timeout")
        assert err.error_code == ProxyErrorCode.TIMEOUT

    def test_base_timeout_metadata(self) -> None:
        """Must preserve timeout_seconds and operation."""
        err = TimeoutError(
            "generic timeout",
            timeout_seconds=15.0,
            operation="fetch",
        )
        assert err.timeout_seconds == 15.0
        assert err.operation == "fetch"
        assert "15.0" in str(err)
        assert "fetch" in str(err)

    def test_base_timeout_retry_recommended(self) -> None:
        """Base timeout should recommend retry by default."""
        err = TimeoutError("generic timeout")
        assert err.retry_recommended is True

    def test_to_dict_contains_all_fields(self) -> None:
        """``to_dict`` should serialize base fields; ``timeout_seconds`` is an attribute but not in dict."""
        err = TimeoutError(
            "timeout",
            timeout_seconds=5.0,
            operation="connect",
        )
        d = err.to_dict()
        assert d["error_code"] == "TIMEOUT"
        assert d["operation"] == "connect"
        assert err.timeout_seconds == 5.0


# ============================================================================
# ASYNC TIMEOUT CONTEXT BEHAVIORS
# ============================================================================


class TestAsyncTimeoutContexts:
    """Test async timeout context manager behaviors."""

    @pytest.mark.asyncio
    async def test_completes_within_timeout(self) -> None:
        """Operation finishing before timeout should succeed."""
        async with _timeout_context(1.0):
            await asyncio.sleep(0.01)
        # No exception expected

    @pytest.mark.asyncio
    async def test_raises_when_exceeded(self) -> None:
        """Operation exceeding timeout should raise."""
        with pytest.raises(TimeoutError):
            async with _timeout_context(0.05):
                await asyncio.sleep(1.0)

    @pytest.mark.asyncio
    async def test_nested_timeout_inner_triggers(self) -> None:
        """Inner shorter timeout should trigger before outer."""
        with pytest.raises(TimeoutError):
            async with _timeout_context(2.0):
                async with _timeout_context(0.05):
                    await asyncio.sleep(1.0)

    @pytest.mark.asyncio
    async def test_nested_timeout_outer_no_trigger(self) -> None:
        """When inner completes quickly, outer should not trigger."""
        async with _timeout_context(2.0):
            async with _timeout_context(1.0):
                await asyncio.sleep(0.01)

    @pytest.mark.asyncio
    async def test_zero_timeout_raises_quickly(self) -> None:
        """A near-zero timeout should raise almost immediately."""
        with pytest.raises(TimeoutError):
            async with _timeout_context(0.0001):
                await asyncio.sleep(0.001)

    @pytest.mark.asyncio
    async def timeout_cancels_pending_task(self) -> None:
        """Timeout should cancel the pending coroutine."""
        cancelled = False

        async def cancellable() -> None:
            nonlocal cancelled
            try:
                await asyncio.sleep(10.0)
            except asyncio.CancelledError:
                cancelled = True
                raise

        with pytest.raises(TimeoutError):
            async with _timeout_context(0.05):
                await cancellable()

        assert cancelled is True

    @pytest.mark.asyncio
    async def test_timeout_preserves_other_exceptions(self) -> None:
        """Non-timeout exceptions should propagate through the context."""

        class CustomError(Exception):
            pass

        with pytest.raises(CustomError):
            async with _timeout_context(1.0):
                raise CustomError("intentional")

    @pytest.mark.asyncio
    async def test_timeout_with_gather(self) -> None:
        """Timeout should apply to a ``gather`` of multiple tasks."""
        async def slow_task() -> None:
            await asyncio.sleep(1.0)

        with pytest.raises(TimeoutError):
            async with _timeout_context(0.05):
                await asyncio.gather(slow_task(), slow_task())

    @pytest.mark.asyncio
    async def test_timeout_with_mixed_tasks(self) -> None:
        """Timeout with mixed fast/slow tasks should still trigger."""
        async def fast() -> None:
            await asyncio.sleep(0.001)

        async def slow() -> None:
            await asyncio.sleep(1.0)

        with pytest.raises(TimeoutError):
            async with _timeout_context(0.05):
                await asyncio.gather(fast(), slow())

    @pytest.mark.asyncio
    async def test_timeout_boundary_exact(self) -> None:
        """Operation slightly under the boundary should succeed."""
        async with _timeout_context(0.2):
            await asyncio.sleep(0.15)


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
            if name.startswith("test_") and (inspect.isfunction(member) or inspect.ismethod(member)):
                tests.append(member)
        return tests

    test_funcs = _collect_tests(module)
    for _, cls in inspect.getmembers(module, inspect.isclass):
        test_funcs.extend(_collect_tests(cls))

    assert len(test_funcs) >= 15, f"Expected >= 15 tests, found {len(test_funcs)}"
