"""Integration tests for proxy pool management endpoints (US2)."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from proxywhirl.api import core as api_core
from proxywhirl.api.models import HealthCheckResult


@pytest.mark.integration
async def test_list_proxies(
    async_api_client: AsyncClient, api_test_rotator, api_auth_headers: dict[str, str]
) -> None:
    """GET /api/proxies lists pool members with pagination metadata."""
    response = await async_api_client.get(
        "/api/proxies",
        params={"page": 1, "page_size": 10},
        headers=api_auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    data = body["data"]
    assert data["total"] >= 2
    assert len(data["items"]) >= 2


@pytest.mark.integration
async def test_add_proxy(
    async_api_client: AsyncClient, api_test_rotator, api_auth_headers: dict[str, str]
) -> None:
    """POST /api/proxies adds a new proxy to the pool."""
    response = await async_api_client.post(
        "/api/proxies",
        json={"url": "http://added-proxy.example.com:9090"},
        headers=api_auth_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "success"
    assert "added-proxy.example.com" in body["data"]["url"]


@pytest.mark.integration
async def test_get_proxy_by_id(
    async_api_client: AsyncClient, api_test_rotator, api_auth_headers: dict[str, str]
) -> None:
    """GET /api/proxies/{id} returns a single proxy resource."""
    proxy = (await api_test_rotator.pool.aget_all_proxies())[0]
    proxy_id = api_core._get_proxy_id(proxy)
    response = await async_api_client.get(f"/api/proxies/{proxy_id}", headers=api_auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["data"]["id"] == proxy_id


@pytest.mark.integration
async def test_delete_proxy(
    async_api_client: AsyncClient, api_test_rotator, api_auth_headers: dict[str, str]
) -> None:
    """DELETE /api/proxies/{id} removes a proxy from the pool."""
    added = await async_api_client.post(
        "/api/proxies",
        json={"url": "http://delete-me.example.com:7070"},
        headers=api_auth_headers,
    )
    assert added.status_code == 201
    proxy_id = added.json()["data"]["id"]
    deleted = await async_api_client.delete(f"/api/proxies/{proxy_id}", headers=api_auth_headers)
    assert deleted.status_code == 204
    missing = await async_api_client.get(f"/api/proxies/{proxy_id}", headers=api_auth_headers)
    assert missing.status_code == 404


@pytest.mark.integration
async def test_health_check(
    async_api_client: AsyncClient, api_test_rotator, api_auth_headers: dict[str, str]
) -> None:
    """POST /api/proxies/health-check validates selected proxies."""
    proxy = (await api_test_rotator.pool.aget_all_proxies())[0]
    proxy_id = api_core._get_proxy_id(proxy)
    mocked_result = HealthCheckResult(
        proxy_id=proxy_id,
        status="working",
        latency_ms=12,
        error=None,
        tested_at=datetime.now(timezone.utc),
    )
    with patch(
        "proxywhirl.api.routes.proxies._check_proxy_health",
        new_callable=AsyncMock,
        return_value=mocked_result,
    ):
        response = await async_api_client.post(
            "/api/proxies/health-check",
            json={"proxy_ids": [proxy_id]},
            headers=api_auth_headers,
        )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["data"][0]["proxy_id"] == proxy_id
    assert body["data"][0]["status"] == "working"
