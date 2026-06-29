"""Legacy failover behavior when FailoverPolicy.enabled is False."""

from unittest.mock import MagicMock, Mock, patch

import httpx

from proxywhirl import Proxy, ProxyWhirl
from proxywhirl.orchestration import FailoverPolicy
from proxywhirl.retry import RetryPolicy


class TestFailoverLegacy:
    """With failover disabled, inner retries stay on the same proxy."""

    @patch("httpx.Client")
    def test_disabled_failover_retries_same_proxy(self, mock_client_class: MagicMock) -> None:
        """Legacy path retries the initially selected proxy without rotation."""
        mock_client = MagicMock()
        call_count = {"n": 0}

        def mock_request(*_args, **_kwargs):
            call_count["n"] += 1
            if call_count["n"] < 3:
                raise httpx.ConnectError("transient failure")
            response = Mock(spec=httpx.Response)
            response.status_code = 200
            return response

        mock_client.request.side_effect = mock_request
        mock_client_class.return_value = mock_client

        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        proxy2 = Proxy(url="http://proxy2.example.com:8080")
        rotator = ProxyWhirl(
            proxies=[proxy1, proxy2],
            failover_policy=FailoverPolicy(enabled=False),
            retry_policy=RetryPolicy(max_attempts=3),
        )

        attempted_ids: list[str] = []
        original_factory = rotator._get_or_create_client

        def spy_get_client(proxy: Proxy, proxy_dict: dict[str, str]):
            attempted_ids.append(str(proxy.id))
            return original_factory(proxy, proxy_dict)

        rotator._get_or_create_client = spy_get_client  # type: ignore[method-assign]

        response = rotator.get("https://example.com")
        assert response.status_code == 200
        assert len(set(attempted_ids)) == 1, "Legacy mode must not rotate to a second proxy"
