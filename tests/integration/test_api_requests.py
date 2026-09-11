"""Integration tests for POST /api/request endpoint (US1).

These tests verify the proxied request functionality works end-to-end with real
ProxyWhirl integration, failover behavior, and proxy rotation.
"""

import asyncio
from unittest.mock import patch

import pytest
from httpx import AsyncClient, Response

from proxywhirl.api import runtime as api_runtime
from proxywhirl.models import Proxy


@pytest.fixture
def setup_test_proxies():
    """Set up test proxies in the global rotator."""
    from proxywhirl import ProxyWhirl

    rotator = ProxyWhirl(bootstrap=False)
    api_runtime.set_rotator(rotator)

    rotator.add_proxy(Proxy(url="http://proxy1.example.com:8080"))
    rotator.add_proxy(Proxy(url="http://proxy2.example.com:8080"))
    rotator.add_proxy(Proxy(url="http://proxy3.example.com:8080"))

    yield rotator

    api_runtime.set_rotator(None)


@pytest.mark.integration
async def test_proxied_get_request_success(
    async_api_client: AsyncClient, setup_test_proxies, api_auth_headers: dict[str, str]
) -> None:
    """POST /api/request returns proxied GET payload through the rotator."""
    rotator = setup_test_proxies
    mock_response = Response(
        200,
        json={
            "args": {},
            "headers": {"User-Agent": "ProxyWhirl-Test/1.0"},
            "url": "https://httpbin.org/get",
        },
    )
    with patch.object(rotator, "_make_request", return_value=mock_response):
        response = await async_api_client.post(
            "/api/request",
            json={
                "url": "https://httpbin.org/get",
                "method": "GET",
                "headers": {"User-Agent": "ProxyWhirl-Test/1.0"},
                "timeout": 30,
            },
            headers=api_auth_headers,
        )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    data = body["data"]
    assert data["status_code"] == 200
    assert "proxy_used" in data
    assert "elapsed_ms" in data


@pytest.mark.integration
async def test_proxied_post_request_with_body(
    async_api_client: AsyncClient, setup_test_proxies, api_auth_headers: dict[str, str]
) -> None:
    """POST /api/request forwards JSON bodies via the rotator."""
    rotator = setup_test_proxies
    test_payload = {"key": "value", "test": "data"}
    mock_response = Response(
        200,
        json={
            "json": test_payload,
            "headers": {"Content-Type": "application/json"},
        },
    )
    with patch.object(rotator, "_make_request", return_value=mock_response):
        response = await async_api_client.post(
            "/api/request",
            json={
                "url": "https://httpbin.org/post",
                "method": "POST",
                "headers": {
                    "Content-Type": "application/json",
                    "User-Agent": "ProxyWhirl-Test/1.0",
                },
                "body": str(test_payload),
                "timeout": 30,
            },
            headers=api_auth_headers,
        )

    assert response.status_code == 200
    assert response.json()["status"] == "success"


@pytest.mark.integration
async def test_proxy_rotation_multiple_requests(
    async_api_client: AsyncClient, setup_test_proxies, api_auth_headers: dict[str, str]
) -> None:
    """Sequential proxied requests rotate across multiple proxies."""
    rotator = setup_test_proxies
    mock_response = Response(200, json={"url": "https://httpbin.org/get"})
    proxies_used: list[str] = []

    def _rotate_and_respond(method: str, url: str, **kwargs: object) -> Response:
        rotator._last_used_proxy = rotator.get_proxy()
        return mock_response

    with patch.object(rotator, "_make_request", side_effect=_rotate_and_respond):
        for _ in range(3):
            response = await async_api_client.post(
                "/api/request",
                json={"url": "https://httpbin.org/get", "method": "GET", "timeout": 30},
                headers=api_auth_headers,
            )
            assert response.status_code == 200
            proxy_used = response.json()["data"].get("proxy_used")
            if proxy_used:
                proxies_used.append(proxy_used)

    assert len(set(proxies_used)) >= 2


@pytest.mark.integration
async def test_proxy_failover_with_dead_proxy(
    async_api_client: AsyncClient, api_auth_headers: dict[str, str]
) -> None:
    """Failover path returns structured errors when rotator cannot satisfy the request."""
    from proxywhirl import ProxyWhirl
    from proxywhirl.exceptions import ProxyConnectionError

    rotator = await asyncio.to_thread(ProxyWhirl, bootstrap=False)
    await asyncio.to_thread(rotator.add_proxy, Proxy(url="http://dead-proxy.example.com:9999"))
    await asyncio.to_thread(
        rotator.add_proxy,
        Proxy(url="http://working-proxy.example.com:8080"),
    )
    api_runtime.set_rotator(rotator)

    with patch.object(
        rotator,
        "_make_request",
        side_effect=ProxyConnectionError("all proxies failed"),
    ):
        response = await async_api_client.post(
            "/api/request",
            json={"url": "https://httpbin.org/get", "method": "GET", "timeout": 30},
            headers=api_auth_headers,
        )

    api_runtime.set_rotator(None)
    assert response.status_code == 502
    assert response.json()["status"] == "error"


@pytest.mark.integration
async def test_proxied_request_uses_rotator_path(
    async_api_client: AsyncClient, setup_test_proxies, api_auth_headers: dict[str, str]
) -> None:
    """Verify /api/request delegates to rotator._make_request."""
    rotator = setup_test_proxies
    mock_response = Response(200, json={"url": "https://httpbin.org/get"})

    with patch.object(rotator, "_make_request", wraps=rotator._make_request) as mock_make:
        mock_make.return_value = mock_response
        response = await async_api_client.post(
            "/api/request",
            json={"url": "https://httpbin.org/get", "method": "GET", "timeout": 30},
            headers=api_auth_headers,
        )

    assert response.status_code == 200
    mock_make.assert_called_once()
