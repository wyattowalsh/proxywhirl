"""Tests for lazy sync request bootstrap behavior."""

from __future__ import annotations

import threading
import time
from unittest.mock import MagicMock, Mock, patch

import httpx
import pytest

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import Proxy
from proxywhirl.rotator.sync import ProxyWhirl


class TestSyncRequestBootstrap:
    """Test lazy bootstrap behavior in sync request execution."""

    def test_bootstrap_failure_is_clear_and_only_attempted_once(self) -> None:
        """Empty bootstrap should raise clear error and avoid repeated fetch attempts."""
        rotator = ProxyWhirl()
        message = "Lazy auto-fetch bootstrap yielded zero proxies from built-in public sources"

        with patch.object(
            rotator, "_bootstrap_pool_if_empty", side_effect=ProxyPoolEmptyError(message)
        ) as bootstrap_mock:
            with pytest.raises(ProxyPoolEmptyError, match="Lazy auto-fetch bootstrap yielded zero"):
                rotator.get("https://httpbin.org/get")
            with pytest.raises(ProxyPoolEmptyError, match="Lazy auto-fetch bootstrap yielded zero"):
                rotator.get("https://httpbin.org/get")

        assert bootstrap_mock.call_count == 1

    @patch("httpx.Client")
    def test_empty_pool_bootstraps_once_then_request_flow_continues(
        self, mock_client_class: MagicMock
    ) -> None:
        """Request flow should continue normally after lazy bootstrap populates the pool."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        rotator = ProxyWhirl()
        bootstrap_proxy = Proxy(url="http://bootstrap.example.com:8080")

        def bootstrap_once() -> int:
            rotator.add_proxy(bootstrap_proxy)
            return 1

        with patch.object(
            rotator, "_bootstrap_pool_if_empty", side_effect=bootstrap_once
        ) as mock_boot:
            response = rotator.get("https://httpbin.org/get")
            assert response.status_code == 200
            rotator.get("https://httpbin.org/get")

        assert mock_boot.call_count == 1
        assert mock_client.request.call_count == 2

    def test_bootstrap_guard_is_thread_safe_and_one_time(self) -> None:
        """Concurrent request-time bootstrap checks should trigger one bootstrap call."""
        rotator = ProxyWhirl()
        call_count = 0
        counter_lock = threading.Lock()

        def bootstrap_once() -> int:
            nonlocal call_count
            time.sleep(0.05)
            with counter_lock:
                call_count += 1
            rotator.add_proxy(Proxy(url="http://thread-safe-bootstrap.example.com:8080"))
            return 1

        with patch.object(rotator, "_bootstrap_pool_if_empty", side_effect=bootstrap_once):
            threads = [
                threading.Thread(target=rotator._ensure_bootstrap_for_empty_pool) for _ in range(5)
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

        assert call_count == 1

    def test_successful_bootstrap_populates_pool_with_proxies(self) -> None:
        """Successful bootstrap should populate pool with fetched proxies."""
        rotator = ProxyWhirl()
        bootstrap_proxies = [Proxy(url=f"http://bootstrap{i}.example.com:8080") for i in range(3)]

        def mock_bootstrap() -> int:
            for proxy in bootstrap_proxies:
                rotator.add_proxy(proxy)
            return len(bootstrap_proxies)

        with patch.object(rotator, "_bootstrap_pool_if_empty", side_effect=mock_bootstrap):
            with patch("httpx.Client") as mock_client_class:
                mock_response = Mock(spec=httpx.Response)
                mock_response.status_code = 200
                mock_client = MagicMock()
                mock_client.request.return_value = mock_response
                mock_client_class.return_value = mock_client

                rotator.get("https://httpbin.org/get")

        assert rotator.pool.size == 3

    def test_bootstrap_skipped_when_pool_not_empty(self) -> None:
        """Bootstrap should be skipped when pool already has proxies."""
        initial_proxy = Proxy(url="http://initial.example.com:8080")
        rotator = ProxyWhirl(proxies=[initial_proxy])

        with patch.object(rotator, "_bootstrap_pool_if_empty", return_value=0) as bootstrap_mock:
            with patch("httpx.Client") as mock_client_class:
                mock_response = Mock(spec=httpx.Response)
                mock_response.status_code = 200
                mock_client = MagicMock()
                mock_client.request.return_value = mock_response
                mock_client_class.return_value = mock_client

                rotator.get("https://httpbin.org/get")

        # Bootstrap should never be called since pool was not empty
        bootstrap_mock.assert_not_called()

    def test_bootstrap_error_cached_for_subsequent_requests(self) -> None:
        """Bootstrap failure error should be cached and re-raised without re-attempting."""
        rotator = ProxyWhirl()
        error_message = "Lazy auto-fetch bootstrap yielded zero proxies"

        call_count = 0

        def failing_bootstrap() -> int:
            nonlocal call_count
            call_count += 1
            raise ProxyPoolEmptyError(error_message)

        with patch.object(rotator, "_bootstrap_pool_if_empty", side_effect=failing_bootstrap):
            # First request triggers bootstrap
            with pytest.raises(ProxyPoolEmptyError, match=error_message):
                rotator._ensure_bootstrap_for_empty_pool()

            # Second request should raise cached error without calling bootstrap again
            with pytest.raises(ProxyPoolEmptyError, match=error_message):
                rotator._ensure_bootstrap_for_empty_pool()

        # Bootstrap should only be attempted once
        assert call_count == 1
