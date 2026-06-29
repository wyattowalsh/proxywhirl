"""Integration tests for opt-in cross-proxy failover."""

from unittest.mock import MagicMock, Mock, patch

import httpx

from proxywhirl import Proxy, ProxyWhirl
from proxywhirl.orchestration import FailoverPolicy
from proxywhirl.retry import RetryPolicy


class TestTrueFailover:
    """Verify FailoverPolicy(enabled=True) rotates across distinct proxies."""

    @patch("httpx.Client")
    def test_uses_different_proxy_ids_on_failover(self, mock_client_class: MagicMock) -> None:
        """When the first proxy fails, a second distinct proxy must be attempted."""
        mock_client = MagicMock()
        call_count = {"n": 0}

        def mock_request(*_args, **_kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise httpx.ConnectError("first proxy down")
            response = Mock(spec=httpx.Response)
            response.status_code = 200
            return response

        mock_client.request.side_effect = mock_request
        mock_client_class.return_value = mock_client

        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        proxy2 = Proxy(url="http://proxy2.example.com:8080")
        rotator = ProxyWhirl(
            proxies=[proxy1, proxy2],
            failover_policy=FailoverPolicy(enabled=True, max_proxy_attempts=2),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        attempted_ids: list[str] = []
        original_factory = rotator._get_or_create_client

        def spy_get_client(proxy: Proxy, proxy_dict: dict[str, str]):
            attempted_ids.append(str(proxy.id))
            return original_factory(proxy, proxy_dict)

        rotator._get_or_create_client = spy_get_client  # type: ignore[method-assign]

        response = rotator.get("https://example.com")
        assert response.status_code == 200
        assert len(attempted_ids) >= 2
        assert len(set(attempted_ids)) >= 2, "Failover should try multiple distinct proxy IDs"
