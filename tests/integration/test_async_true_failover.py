"""Integration tests for async opt-in cross-proxy failover."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from proxywhirl import AsyncProxyWhirl, Proxy
from proxywhirl.orchestration import FailoverPolicy
from proxywhirl.retry import RetryPolicy


@pytest.mark.asyncio
class TestAsyncTrueFailover:
    """Verify async FailoverPolicy(enabled=True) rotates across distinct proxies."""

    @patch("httpx.AsyncClient")
    async def test_uses_different_proxy_ids_on_failover(self, mock_client_class: MagicMock) -> None:
        mock_client = AsyncMock()
        call_count = {"n": 0}

        async def mock_request(*_args, **_kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise httpx.ConnectError("first proxy down")
            response = MagicMock(spec=httpx.Response)
            response.status_code = 200
            return response

        mock_client.request.side_effect = mock_request
        mock_client_class.return_value = mock_client

        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        proxy2 = Proxy(url="http://proxy2.example.com:8080")
        rotator = AsyncProxyWhirl(
            proxies=[proxy1, proxy2],
            failover_policy=FailoverPolicy(enabled=True, max_proxy_attempts=2),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        attempted_ids: list[str] = []
        original_factory = rotator._get_or_create_client

        async def spy_get_client(proxy: Proxy, proxy_dict: dict[str, str]):
            attempted_ids.append(str(proxy.id))
            return await original_factory(proxy, proxy_dict)

        rotator._get_or_create_client = spy_get_client  # type: ignore[method-assign]

        response = await rotator.get("https://example.com")
        assert response.status_code == 200
        assert len(attempted_ids) >= 2
        assert len(set(attempted_ids)) >= 2
