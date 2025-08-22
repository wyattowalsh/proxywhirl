# pyright: reportMissingImports=false, reportUnknownMemberType=false,
#   reportUnknownArgumentType=false, reportUnknownParameterType=false
# mypy: ignore-errors
import types
from ipaddress import ip_address

import pytest

from proxywhirl.models import AnonymityLevel, Proxy, Scheme
from proxywhirl.validator import ProxyValidator


class DummyResponse:
    def __init__(self, status_code: int = 200):
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError("bad status")


class DummyAsyncClient:
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail

    async def __aenter__(self) -> "DummyAsyncClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:  # type: ignore[no-untyped-def]
        return False

    async def get(self, url: str):
        if self.should_fail:
            return DummyResponse(500)
        return DummyResponse(200)


@pytest.mark.asyncio
async def test_validate_proxy_success(monkeypatch):
    pv = ProxyValidator()

    # Patch httpx.AsyncClient used inside ProxyValidator
    import proxywhirl.core as core

    monkeypatch.setattr(
        core,
        "httpx",
        types.SimpleNamespace(AsyncClient=lambda **_: DummyAsyncClient(False)),
    )

    p = Proxy(
        host="192.0.2.1",
        ip=ip_address("192.0.2.1"),
        port=8080,
        schemes=[Scheme.HTTP],
        anonymity=AnonymityLevel.UNKNOWN,
    )
    ok = await pv.validate_proxy(p)
    assert ok is True and p.response_time is not None


@pytest.mark.asyncio
async def test_validate_proxy_failure(monkeypatch):
    pv = ProxyValidator()
    import proxywhirl.core as core

    monkeypatch.setattr(
        core,
        "httpx",
        types.SimpleNamespace(AsyncClient=lambda **_: DummyAsyncClient(True)),
    )

    p = Proxy(
        host="192.0.2.1",
        ip=ip_address("192.0.2.1"),
        port=8080,
        schemes=[Scheme.HTTP],
        anonymity=AnonymityLevel.UNKNOWN,
    )
    ok = await pv.validate_proxy(p)
    assert ok is False
