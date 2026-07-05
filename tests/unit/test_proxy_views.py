"""Tests for credential-safe proxy view helpers."""

from __future__ import annotations

from unittest.mock import MagicMock

from proxywhirl._proxy_views import proxy_to_view
from proxywhirl.models import Proxy


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
