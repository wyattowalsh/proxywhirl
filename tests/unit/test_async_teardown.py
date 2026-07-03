"""Unit tests for AsyncProxyWhirl teardown behavior.

Covers gaps identified in openspec/changes/audit-remediation/artifacts/phase-r/r-async-teardown.md:
- Async context manager (`__aenter__`/`__aexit__`) client-pool cleanup
- Explicit `_close_all_clients()` idempotency (double teardown must not raise)
- Cancellation during an in-flight request still results in client cleanup on exit
- Background aggregation thread shutdown (`_stop_event`, `_aggregation_thread.join`)
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from proxywhirl.rotator import AsyncProxyWhirl


class TestAsyncTeardownClientPool:
    """Verify __aexit__ actually closes clients rather than merely not raising."""

    @pytest.mark.asyncio
    async def test_aexit_closes_primary_client(self) -> None:
        """__aexit__ closes self._client and clears the reference."""
        rotator = AsyncProxyWhirl()
        await rotator.__aenter__()
        primary_client = rotator._client
        assert primary_client is not None

        with patch.object(primary_client, "aclose", new=AsyncMock()) as mock_aclose:
            await rotator.__aexit__(None, None, None)
            mock_aclose.assert_awaited_once()
        assert rotator._client is None

    @pytest.mark.asyncio
    async def test_aexit_closes_pooled_clients(self) -> None:
        """__aexit__ closes every pooled per-proxy client via _close_all_clients."""
        rotator = AsyncProxyWhirl()
        await rotator.add_proxy("http://45.33.32.156:8080")
        proxy = rotator.pool.get_all_proxies()[0]

        async with rotator:
            proxy_dict = rotator._get_proxy_dict(proxy)
            client = await rotator._get_or_create_client(proxy, proxy_dict)
            assert str(proxy.id) in rotator._client_pool

        # After exit, the pooled client must be closed and removed.
        assert len(rotator._client_pool) == 0
        assert client.is_closed


class TestCloseAllClientsIdempotency:
    """Explicit teardown must be safe to invoke more than once."""

    @pytest.mark.asyncio
    async def test_close_all_clients_twice_does_not_raise(self) -> None:
        """Calling _close_all_clients() a second time on an empty pool is a no-op."""
        rotator = AsyncProxyWhirl()
        await rotator.add_proxy("http://45.33.32.156:8080")
        proxy = rotator.pool.get_all_proxies()[0]
        proxy_dict = rotator._get_proxy_dict(proxy)
        await rotator._get_or_create_client(proxy, proxy_dict)

        await rotator._close_all_clients()
        assert len(rotator._client_pool) == 0

        # Second call must not raise even though the pool is already empty.
        await rotator._close_all_clients()
        assert len(rotator._client_pool) == 0

    @pytest.mark.asyncio
    async def test_double_aexit_does_not_raise(self) -> None:
        """Calling __aexit__ twice in a row is safe (idempotent teardown)."""
        rotator = AsyncProxyWhirl()
        await rotator.__aenter__()

        await rotator.__aexit__(None, None, None)
        assert rotator._client is None

        # Second exit: self._client is already None, thread already stopped/joined.
        await rotator.__aexit__(None, None, None)
        assert rotator._client is None


class TestCancellationDuringRequest:
    """A cancelled in-flight request must not leak the underlying httpx client."""

    @pytest.mark.asyncio
    async def test_cancelled_request_client_still_closed_on_exit(self) -> None:
        """Cancelling a request mid-flight still allows __aexit__ to close its client."""
        rotator = AsyncProxyWhirl()
        await rotator.add_proxy("http://45.33.32.156:8080")

        async with rotator:
            proxy = rotator.pool.get_all_proxies()[0]
            proxy_dict = rotator._get_proxy_dict(proxy)
            client = await rotator._get_or_create_client(proxy, proxy_dict)

            async def slow_request() -> None:
                await client.get("https://example.invalid", timeout=30)

            task = asyncio.ensure_future(slow_request())
            await asyncio.sleep(0)  # yield control so the task starts
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task

            # Client remains registered in the pool despite the cancellation.
            assert str(proxy.id) in rotator._client_pool

        # __aexit__ must have force-closed the client even though its in-flight
        # request was cancelled rather than completed normally.
        assert client.is_closed
        assert len(rotator._client_pool) == 0


class TestAggregationThreadShutdown:
    """Background metrics-aggregation thread must stop cleanly on teardown."""

    @pytest.mark.asyncio
    async def test_stop_event_set_and_thread_joined_on_exit(self) -> None:
        """__aexit__ sets _stop_event and joins the aggregation thread."""
        rotator = AsyncProxyWhirl()
        await rotator.__aenter__()
        thread = rotator._aggregation_thread
        assert thread.is_alive()
        assert not rotator._stop_event.is_set()

        await rotator.__aexit__(None, None, None)

        assert rotator._stop_event.is_set()
        assert not thread.is_alive()

    @pytest.mark.asyncio
    async def test_exit_joins_thread_even_when_client_is_none(self) -> None:
        """__aexit__ still stops the aggregation thread if __aenter__ was never called."""
        rotator = AsyncProxyWhirl()
        assert rotator._client is None
        thread = rotator._aggregation_thread
        assert thread.is_alive()

        await rotator.__aexit__(None, None, None)

        assert rotator._stop_event.is_set()
        assert not thread.is_alive()

    def test_del_stops_thread_without_context_manager_usage(self) -> None:
        """__del__ provides a cleanup safety net when used without `async with`."""
        rotator = AsyncProxyWhirl()
        thread = rotator._aggregation_thread
        assert thread.is_alive()

        rotator.__del__()

        assert rotator._stop_event.is_set()
        thread.join(timeout=2.0)
        assert not thread.is_alive()
