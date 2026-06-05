"""Tests for the canonical unversioned API surface."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import httpx
from fastapi.testclient import TestClient

import proxywhirl.api.routes.proxies as proxy_routes
from proxywhirl.api import APIKeyAuth, app, create_api_key
from proxywhirl.api.core import get_rotator
from proxywhirl.models import Proxy
from proxywhirl.rotator import ProxyWhirl

EXPECTED_OPENAPI_ROUTE_METHODS = {
    "/api/circuit-breakers": ["GET"],
    "/api/circuit-breakers/{proxy_id}": ["GET"],
    "/api/circuit-breakers/{proxy_id}/reset": ["POST"],
    "/api/config": ["GET", "PUT"],
    "/api/health": ["GET"],
    "/api/metrics/circuit-breakers": ["GET"],
    "/api/metrics/retries": ["GET"],
    "/api/metrics/retries/by-proxy": ["GET"],
    "/api/metrics/retries/timeseries": ["GET"],
    "/api/proxies": ["GET", "POST"],
    "/api/proxies/export": ["GET"],
    "/api/proxies/health-check": ["POST"],
    "/api/proxies/stream": ["GET"],
    "/api/proxies/test": ["POST"],
    "/api/proxies/{proxy_id}": ["DELETE", "GET"],
    "/api/ready": ["GET"],
    "/api/request": ["POST"],
    "/api/retry/policy": ["GET", "PUT"],
    "/api/rotate": ["GET"],
    "/api/stats": ["GET"],
    "/api/status": ["GET"],
}


def test_openapi_uses_unversioned_api_paths() -> None:
    """The generated schema exposes only canonical unversioned REST paths."""
    paths = app.openapi()["paths"]
    route_methods = {
        path: sorted(
            method.upper()
            for method in route
            if method in {"get", "post", "put", "patch", "delete"}
        )
        for path, route in paths.items()
    }

    assert route_methods == EXPECTED_OPENAPI_ROUTE_METHODS
    assert "/api/health" in paths
    assert "/api/rotate" in paths
    assert "/api/proxies" in paths
    assert "/api/stats" in paths
    assert "/api/metrics/retries" in paths
    assert "/api/metrics/retries/timeseries" in paths
    assert "/api/metrics/retries/by-proxy" in paths
    assert "/api/metrics/circuit-breakers" in paths
    assert all(not path.startswith("/api/v1") for path in paths)
    assert all(not path.startswith("/api/v2") for path in paths)
    assert all(path == "/api/metrics" or not path.startswith("/metrics") for path in paths)
    assert all(not path.endswith("/metrics") or path.startswith("/api/metrics") for path in paths)


def test_rotate_returns_sanitized_proxy_resource() -> None:
    """GET /api/rotate returns the public proxy representation without credentials."""
    rotator = ProxyWhirl(
        proxies=[Proxy(url="http://user:pass@proxy.example.com:8080")],
        bootstrap=False,
    )
    app.dependency_overrides[get_rotator] = lambda: rotator

    try:
        response = TestClient(app).get("/api/rotate")
    finally:
        app.dependency_overrides.pop(get_rotator, None)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["url"] == "http://proxy.example.com:8080"
    assert "user" not in data["data"]["url"]
    assert "pass" not in data["data"]["url"]


def test_proxied_request_returns_sanitized_proxy_used(monkeypatch) -> None:
    """POST /api/request never exposes proxy credentials in the response."""

    class FakeAsyncClient:
        def __init__(self, **kwargs):
            self.proxy = kwargs["proxy"]

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return False

        async def request(self, **kwargs):
            return httpx.Response(
                status_code=200,
                headers={"content-type": "text/plain"},
                text="ok",
            )

    rotator = ProxyWhirl(
        proxies=[Proxy(url="http://user:pass@proxy.example.com:8080")],
        bootstrap=False,
    )
    app.dependency_overrides[get_rotator] = lambda: rotator
    monkeypatch.setattr(proxy_routes.httpx, "AsyncClient", FakeAsyncClient)

    try:
        response = TestClient(app).post(
            "/api/request",
            json={
                "url": "https://example.com",
                "method": "GET",
                "headers": {},
                "timeout": 30,
            },
        )
    finally:
        app.dependency_overrides.pop(get_rotator, None)

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["proxy_used"] == "http://proxy.example.com:8080"
    assert "user" not in data["data"]["proxy_used"]
    assert "pass" not in data["data"]["proxy_used"]


def test_create_api_key_returns_key_pair() -> None:
    """API key creation returns distinct key id and secret values."""
    key_id, key_secret = create_api_key("test-key")

    assert key_id
    assert key_secret
    assert key_id != key_secret


def test_api_key_auth_expiration_is_timezone_safe() -> None:
    """Expiration checks handle aware and naive timestamps deterministically."""
    expired = APIKeyAuth(
        key_id="expired",
        key_secret="secret",
        name="expired-key",
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
    )
    active = APIKeyAuth(
        key_id="active",
        key_secret="secret",
        name="active-key",
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
    )
    naive_expired = APIKeyAuth(
        key_id="naive-expired",
        key_secret="secret",
        name="naive-expired-key",
        expires_at=datetime.utcnow() - timedelta(seconds=1),
    )

    assert expired.is_expired is True
    assert active.is_expired is False
    assert naive_expired.is_expired is True
