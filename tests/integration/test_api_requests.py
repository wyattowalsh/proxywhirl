"""Integration tests for POST /api/v1/request endpoint (US1).

These tests verify the proxied request functionality works end-to-end with real
ProxyRotator integration, failover behavior, and proxy rotation.

NOTE: These tests require the API to be running with proxies configured.
For now, we'll skip them and mark them as expected to fail until we have
a proper test environment with mocked proxies.
"""

import pytest
from httpx import AsyncClient

from proxywhirl.api import app


@pytest.fixture
async def api_client():
    """Create an async HTTP client for the FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# T012: Integration test for proxied GET request
@pytest.mark.skip(reason="Requires external dependencies - implement with mocked proxies")
@pytest.mark.asyncio
async def test_proxied_get_request_success(api_client: AsyncClient):
    """Test successful proxied GET request to httpbin.org/get.

    Verifies:
    - Response contains expected fields (status_code, headers, body)
    - Proxy was used (check proxy_used field)
    - Request succeeds with valid status code
    """
    pass


# T013: Integration test for proxied POST request
@pytest.mark.skip(reason="Requires external dependencies - implement with mocked proxies")
@pytest.mark.asyncio
async def test_proxied_post_request_with_body(api_client: AsyncClient):
    """Test successful proxied POST request with JSON body.

    Verifies:
    - Request body is forwarded correctly
    - Headers are passed through
    - Response contains posted data
    """
    pass


# T014: Integration test for proxy rotation
@pytest.mark.skip(reason="Requires external dependencies - implement with mocked proxies")
@pytest.mark.asyncio
async def test_proxy_rotation_multiple_requests(api_client: AsyncClient):
    """Test proxy rotation across multiple sequential requests.

    Verifies:
    - Different proxies are used for sequential requests
    - Rotation strategy (round-robin) is applied
    """
    pass


# T015: Integration test for proxy failover
@pytest.mark.skip(reason="Requires external dependencies - implement with mocked proxies")
@pytest.mark.asyncio
async def test_proxy_failover_with_dead_proxy(api_client: AsyncClient):
    """Test proxy failover when first proxy fails.

    Verifies:
    - Request succeeds using working proxy after first proxy fails
    - Retry logic is triggered when first proxy fails
    """
    pass
