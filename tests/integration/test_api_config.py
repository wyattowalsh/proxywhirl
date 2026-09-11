"""Integration tests for configuration endpoints (US4)."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from proxywhirl.api import runtime as api_runtime


@pytest.mark.integration
async def test_get_configuration(
    async_api_client: AsyncClient, api_test_rotator, api_auth_headers: dict[str, str]
) -> None:
    """GET /api/config returns the active runtime configuration."""
    api_runtime.set_config(
        {
            "rotation_strategy": "round-robin",
            "timeout": 30,
            "max_retries": 3,
            "rate_limits": {"default_limit": 100, "request_endpoint_limit": 50},
            "auth_enabled": False,
            "cors_origins": [],
        }
    )
    response = await async_api_client.get("/api/config", headers=api_auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["data"]["rotation_strategy"] == "round-robin"
    assert body["data"]["timeout"] == 30


@pytest.mark.integration
async def test_update_rotation_strategy(
    async_api_client: AsyncClient, api_test_rotator, api_auth_headers: dict[str, str]
) -> None:
    """PUT /api/config can switch the active rotation strategy."""
    api_runtime.set_config({"rotation_strategy": "round-robin", "timeout": 30})
    response = await async_api_client.put(
        "/api/config",
        json={"rotation_strategy": "random"},
        headers=api_auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["data"]["rotation_strategy"] == "random"


@pytest.mark.integration
async def test_update_timeout(
    async_api_client: AsyncClient, api_test_rotator, api_auth_headers: dict[str, str]
) -> None:
    """PUT /api/config updates timeout values."""
    api_runtime.set_config({"rotation_strategy": "round-robin", "timeout": 10})
    response = await async_api_client.put(
        "/api/config",
        json={"timeout": 45},
        headers=api_auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["data"]["timeout"] == 45


@pytest.mark.integration
async def test_update_rate_limits(
    async_api_client: AsyncClient, api_test_rotator, api_auth_headers: dict[str, str]
) -> None:
    """PUT /api/config merges rate limit settings."""
    api_runtime.set_config(
        {
            "rotation_strategy": "round-robin",
            "rate_limits": {"default_limit": 10, "request_endpoint_limit": 5},
        }
    )
    response = await async_api_client.put(
        "/api/config",
        json={"rate_limits": {"default_limit": 20, "request_endpoint_limit": 8}},
        headers=api_auth_headers,
    )
    assert response.status_code == 200
    limits = response.json()["data"]["rate_limits"]
    assert limits["default_limit"] == 20
    assert limits["request_endpoint_limit"] == 8


@pytest.mark.integration
async def test_validation_errors(
    async_api_client: AsyncClient, api_test_rotator, api_auth_headers: dict[str, str]
) -> None:
    """Invalid configuration payloads return HTTP 422."""
    response = await async_api_client.put(
        "/api/config",
        json={"timeout": -1},
        headers=api_auth_headers,
    )
    assert response.status_code == 422
