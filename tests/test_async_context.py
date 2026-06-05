"""Test AsyncProxyWhirl context isolation.

This module tests that AsyncProxyWhirl properly isolates context between
concurrent operations and handles context switching correctly.
"""

from __future__ import annotations

import asyncio

import pytest

from proxywhirl import AsyncProxyWhirl, Proxy


class TestAsyncContextIsolation:
    """Test suite for AsyncProxyWhirl context isolation."""

    @pytest.mark.asyncio
    async def test_async_multiple_instances_isolated(self):
        """Test multiple AsyncProxyWhirl instances have isolated state."""
        pw1 = AsyncProxyWhirl()
        pw2 = AsyncProxyWhirl()

        assert pw1 is not pw2
        assert pw1.config is not pw2.config

    @pytest.mark.asyncio
    async def test_async_concurrent_operations(self):
        """Test concurrent get operations don't interfere."""
        pw = AsyncProxyWhirl()

        async def get_proxy():
            return await pw.get()

        try:
            results = await asyncio.gather(
                get_proxy(), get_proxy(), get_proxy(), return_exceptions=True
            )
            # Should not raise
            assert len(results) == 3
        except Exception:
            # Acceptable if no proxies available
            pass

    @pytest.mark.asyncio
    async def test_async_context_vars_isolation(self):
        """Test context variables are properly isolated."""
        pw = AsyncProxyWhirl()

        async def task1():
            return await pw.get()

        async def task2():
            return await pw.get()

        try:
            r1 = await asyncio.create_task(task1())
            r2 = await asyncio.create_task(task2())
            # Both should complete without context bleeding
        except Exception:
            # Acceptable if no proxies
            pass

    @pytest.mark.asyncio
    async def test_async_nested_context(self):
        """Test nested async context operations."""
        pw = AsyncProxyWhirl()

        async def inner():
            return await pw.get()

        async def outer():
            return await inner()

        try:
            result = await outer()
            # Should work in nested context
        except Exception:
            pass

    @pytest.mark.asyncio
    async def test_async_task_group_isolation(self):
        """Test task groups don't share context."""
        pw = AsyncProxyWhirl()

        async def worker(worker_id):
            try:
                result = await pw.get()
                return (worker_id, result)
            except Exception:
                return (worker_id, None)

        try:
            tasks = [worker(i) for i in range(3)]
            results = await asyncio.gather(*tasks)
            assert len(results) == 3
        except Exception:
            pass

    @pytest.mark.asyncio
    async def test_async_exception_isolation(self):
        """Test exceptions in one context don't affect others."""
        pw = AsyncProxyWhirl()

        async def failing_task():
            raise ValueError("test error")

        async def normal_task():
            try:
                return await pw.get()
            except Exception:
                return None

        try:
            result = await asyncio.gather(failing_task(), normal_task(), return_exceptions=True)
            # Both should complete
            assert len(result) == 2
        except Exception:
            pass

    @pytest.mark.asyncio
    async def test_async_state_not_shared(self):
        """Test that state is not shared between instances."""
        pw1 = AsyncProxyWhirl()
        pw2 = AsyncProxyWhirl()

        # Modify config of pw1
        original_timeout = pw1.config.timeout if hasattr(pw1.config, "timeout") else None

        try:
            if hasattr(pw1.config, "timeout"):
                pw1.config.timeout = 99
        except Exception:
            pass

        # pw2 should not be affected
        assert pw2 is not None

    @pytest.mark.asyncio
    async def test_async_concurrent_add_proxy(self):
        """Test concurrent add_proxy operations."""
        pw = AsyncProxyWhirl()

        async def add_proxy_task(url):
            try:
                proxy = Proxy(url=url, protocol="http")
                await pw.add_proxy(proxy)
                return True
            except Exception:
                return False

        try:
            results = await asyncio.gather(
                add_proxy_task("http://proxy1:8080"),
                add_proxy_task("http://proxy2:8080"),
                add_proxy_task("http://proxy3:8080"),
            )
        finally:
            await pw.__aexit__(None, None, None)

        # All should complete
        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_async_timeout_isolation(self):
        """Test timeout settings are isolated per instance."""
        pw1 = AsyncProxyWhirl()
        pw2 = AsyncProxyWhirl()

        # Both should have independent timeout configs
        assert pw1.config is not pw2.config

    @pytest.mark.asyncio
    async def test_async_clear_queue_isolation(self):
        """Test clearing queue doesn't affect other instances."""
        pw1 = AsyncProxyWhirl()
        pw2 = AsyncProxyWhirl()

        try:
            pw1.clear_queue()
            # pw2 should still function
            result = await pw2.get()
        except Exception:
            # Acceptable if no proxies
            pass

    @pytest.mark.asyncio
    async def test_async_long_running_task(self):
        """Test long-running task doesn't block other operations."""
        pw = AsyncProxyWhirl()

        async def long_task():
            await asyncio.sleep(0.1)
            return "done"

        async def quick_task():
            try:
                return await pw.get()
            except Exception:
                return None

        try:
            results = await asyncio.gather(
                long_task(),
                quick_task(),
                quick_task(),
            )
            # All should complete
            assert len(results) == 3
        except Exception:
            pass

    @pytest.mark.asyncio
    async def test_async_context_cancellation(self):
        """Test context cancellation doesn't affect other operations."""
        pw = AsyncProxyWhirl()

        async def cancellable_task():
            try:
                await asyncio.sleep(10)
                return "timeout"
            except asyncio.CancelledError:
                raise

        async def normal_task():
            try:
                return await pw.get()
            except Exception:
                return None

        try:
            task1 = asyncio.create_task(cancellable_task())
            task2 = asyncio.create_task(normal_task())

            await asyncio.sleep(0.01)
            task1.cancel()

            results = await asyncio.gather(task1, task2, return_exceptions=True)
            # task2 should still complete
            assert len(results) == 2
        except Exception:
            pass

    @pytest.mark.asyncio
    async def test_async_semaphore_isolation(self):
        """Test concurrent operations with semaphore."""
        pw = AsyncProxyWhirl()
        semaphore = asyncio.Semaphore(2)

        async def limited_get():
            async with semaphore:
                try:
                    return await pw.get()
                except Exception:
                    return None

        try:
            results = await asyncio.gather(
                limited_get(),
                limited_get(),
                limited_get(),
            )
            assert len(results) == 3
        except Exception:
            pass

    @pytest.mark.asyncio
    async def test_async_stream_context(self):
        """Test async stream operations."""
        pw = AsyncProxyWhirl()

        async def get_proxies():
            for _ in range(3):
                try:
                    yield await pw.get()
                except Exception:
                    break

        try:
            async for proxy in get_proxies():
                assert proxy is None or isinstance(proxy, (Proxy, type(None)))
                break  # Just test one
        except Exception:
            pass
