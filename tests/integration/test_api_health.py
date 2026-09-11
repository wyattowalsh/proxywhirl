"""Integration tests for health/monitoring endpoints (US3)."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.integration
async def test_health_endpoint(async_api_client: AsyncClient, api_test_rotator) -> None:
    """GET /api/health returns structured health payload when the pool is usable."""
    response = await async_api_client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["data"]["status"] in {"healthy", "degraded"}


@pytest.mark.integration
async def test_readiness_endpoint(async_api_client: AsyncClient, api_test_rotator) -> None:
    """GET /api/ready reports readiness when the rotator is initialized."""
    response = await async_api_client.get("/api/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["data"]["ready"] is True


@pytest.mark.integration
async def test_status_endpoint(
    async_api_client: AsyncClient, api_test_rotator, api_auth_headers: dict[str, str]
) -> None:
    """GET /api/status exposes pool aggregates."""
    response = await async_api_client.get("/api/status", headers=api_auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["data"]["pool_stats"]["total"] >= 2


@pytest.mark.integration
async def test_stats_endpoint(
    async_api_client: AsyncClient, api_test_rotator, api_auth_headers: dict[str, str]
) -> None:
    """GET /api/stats returns performance statistics."""
    response = await async_api_client.get("/api/stats", headers=api_auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert "requests_total" in body["data"]
