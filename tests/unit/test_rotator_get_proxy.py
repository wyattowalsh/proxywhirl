"""Rotator get_proxy bootstrap parity tests (Wave 1 P-R-04)."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import Proxy
from proxywhirl.rotator.async_ import AsyncProxyWhirl
from proxywhirl.rotator.sync import ProxyWhirl


class TestGetProxyBootstrapParity:
    """Sync and async get_proxy share lazy bootstrap semantics."""

    def test_sync_get_proxy_bootstraps_empty_pool(self) -> None:
        rotator = ProxyWhirl()
        bootstrap_proxy = Proxy(url="http://bootstrap-sync.example.com:8080")

        def bootstrap_once() -> int:
            rotator.add_proxy(bootstrap_proxy)
            return 1

        with patch.object(
            rotator,
            "_bootstrap_pool_if_empty",
            side_effect=bootstrap_once,
        ) as bootstrap_mock:
            selected = rotator.get_proxy()

        assert bootstrap_mock.call_count == 1
        assert selected.url == bootstrap_proxy.url

    async def test_async_get_proxy_bootstraps_empty_pool(self) -> None:
        rotator = AsyncProxyWhirl()
        bootstrap_proxy = Proxy(url="http://bootstrap-async.example.com:8080")

        async def bootstrap_once() -> int:
            await rotator.add_proxy(bootstrap_proxy)
            return 1

        with patch.object(
            rotator,
            "_bootstrap_pool_if_empty",
            side_effect=bootstrap_once,
        ) as bootstrap_mock:
            async with rotator:
                selected = await rotator.get_proxy()

        assert bootstrap_mock.call_count == 1
        assert selected.url == bootstrap_proxy.url

    def test_sync_get_proxy_cached_bootstrap_error(self) -> None:
        rotator = ProxyWhirl()
        message = "Lazy auto-fetch bootstrap yielded zero proxies"

        with patch.object(
            rotator,
            "_bootstrap_pool_if_empty",
            side_effect=ProxyPoolEmptyError(message),
        ) as bootstrap_mock:
            with pytest.raises(ProxyPoolEmptyError, match=message):
                rotator.get_proxy()
            with pytest.raises(ProxyPoolEmptyError, match=message):
                rotator.get_proxy()

        assert bootstrap_mock.call_count == 1

    async def test_async_get_proxy_cached_bootstrap_error(self) -> None:
        rotator = AsyncProxyWhirl()
        message = "Lazy auto-fetch bootstrap yielded zero proxies"

        with patch.object(
            rotator,
            "_bootstrap_pool_if_empty",
            side_effect=ProxyPoolEmptyError(message),
        ) as bootstrap_mock:
            async with rotator:
                with pytest.raises(ProxyPoolEmptyError, match=message):
                    await rotator.get_proxy()
                with pytest.raises(ProxyPoolEmptyError, match=message):
                    await rotator.get_proxy()

        assert bootstrap_mock.call_count == 1
