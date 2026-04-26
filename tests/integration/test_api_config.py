"""Integration tests for configuration endpoints (US4)."""

import pytest
from httpx import AsyncClient

from proxywhirl.api import app


@pytest.fixture
async def api_client():
    """Create an async HTTP client for the FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# T061-T065: Integration tests for US4 - All skipped (implementation pending)
@pytest.mark.skip(reason="Integration tests pending implementation")
async def test_get_configuration(api_client: AsyncClient):
    """T061: Test GET /api/v1/config."""


@pytest.mark.skip(reason="Integration tests pending implementation")
async def test_update_rotation_strategy(api_client: AsyncClient):
    """T062: Test updating rotation strategy."""


@pytest.mark.skip(reason="Integration tests pending implementation")
async def test_update_timeout(api_client: AsyncClient):
    """T063: Test updating timeout configuration."""


@pytest.mark.skip(reason="Integration tests pending implementation")
async def test_update_rate_limits(api_client: AsyncClient):
    """T064: Test updating rate limit configuration."""


@pytest.mark.skip(reason="Integration tests pending implementation")
async def test_validation_errors(api_client: AsyncClient):
    """T065: Test configuration validation errors."""
