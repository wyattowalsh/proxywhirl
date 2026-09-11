"""Tests for credential-safe proxy view helpers."""

from __future__ import annotations

import warnings
from unittest.mock import MagicMock

import pytest

from proxywhirl._proxy_views import list_proxy_views_async, proxy_to_view
from proxywhirl.models import Proxy, ProxyPool


def test_proxy_to_view_redacts_sensitive_source_url() -> None:
    """Proxy views must not expose source URL userinfo or secret query values."""
    rotator = MagicMock()
    rotator.get_circuit_breaker_states.return_value = {}
    proxy = Proxy(
        url="http://proxy.example.com:8080",
        source_url="https://user:pass@sources.example.com/list.txt?token=secret&format=json",
    )

    view = proxy_to_view(rotator, proxy)

    assert view.source_url == ("https://***:***@sources.example.com/list.txt?token=***&format=json")
    assert "user" not in view.source_url
    assert "pass" not in view.source_url
    assert "secret" not in view.source_url


@pytest.mark.asyncio
async def test_list_proxy_views_async_does_not_take_pool_rlock_on_event_loop() -> None:
    """Async adapters must use ProxyPool's offloaded snapshot helper."""
    proxy = Proxy(url="http://proxy.example.com:8080")
    rotator = MagicMock()
    rotator.pool = ProxyPool(proxies=[proxy])
    rotator.get_circuit_breaker_states.return_value = {}

    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        views = await list_proxy_views_async(rotator)

    assert [view.id for view in views] == [str(proxy.id)]
