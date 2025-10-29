"""Integration tests for health/monitoring endpoints (US3)."""

import pytest
from httpx import AsyncClient

from proxywhirl.api import app


@pytest.fixture
async def api_client():
    """Create an async HTTP client for the FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# T046-T049: Integration tests for US3 - All skipped (implementation pending)
@pytest.mark.skip(reason="Integration tests pending implementation")
@pytest.mark.asyncio
async def test_health_endpoint(api_client: AsyncClient):
    """T046: Test /api/v1/health endpoint."""


@pytest.mark.skip(reason="Integration tests pending implementation")
@pytest.mark.asyncio
async def test_readiness_endpoint(api_client: AsyncClient):
    """T047: Test /api/v1/ready endpoint."""


@pytest.mark.skip(reason="Integration tests pending implementation")
@pytest.mark.asyncio
async def test_status_endpoint(api_client: AsyncClient):
    """T048: Test /api/v1/status endpoint."""


@pytest.mark.skip(reason="Integration tests pending implementation")
@pytest.mark.asyncio
async def test_metrics_endpoint(api_client: AsyncClient):
    """T049: Test /api/v1/metrics endpoint."""
