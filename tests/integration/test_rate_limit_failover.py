"""Integration tests for rate-limit behavior with failover enabled."""

from __future__ import annotations

from unittest.mock import MagicMock, Mock, patch

import pytest

from proxywhirl import Proxy, ProxyWhirl, RateLimitExceededError
from proxywhirl.orchestration import FailoverPolicy
from proxywhirl.rate_limiting import RateLimiter


class TestRateLimitFailover:
    """Rate limits must not trigger cross-proxy failover."""

    @patch("httpx.Client")
    def test_rate_limit_does_not_rotate_to_second_proxy(self, mock_client_class: MagicMock) -> None:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        mock_rate_limiter = MagicMock(spec=RateLimiter)
        mock_rate_limiter.check_limit.return_value = False

        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        proxy2 = Proxy(url="http://proxy2.example.com:8080")
        rotator = ProxyWhirl(
            proxies=[proxy1, proxy2],
            failover_policy=FailoverPolicy(enabled=True, max_proxy_attempts=2),
            rate_limiter=mock_rate_limiter,
        )

        attempted_ids: list[str] = []
        original_factory = rotator._get_or_create_client

        def spy_get_client(proxy: Proxy, proxy_dict: dict[str, str]):
            attempted_ids.append(str(proxy.id))
            return original_factory(proxy, proxy_dict)

        rotator._get_or_create_client = spy_get_client  # type: ignore[method-assign]

        with pytest.raises(RateLimitExceededError, match="Rate limit exceeded"):
            rotator.get("https://example.com")

        assert len(attempted_ids) <= 1
        mock_client.request.assert_not_called()
