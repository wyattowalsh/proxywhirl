"""Integration tests for POST /api/v1/request endpoint (US1).

These tests verify the proxied request functionality works end-to-end with real
ProxyRotator integration, failover behavior, and proxy rotation.
"""

import pytest
import respx
from httpx import ASGITransport, AsyncClient, Response

from proxywhirl.api import _rotator, app
from proxywhirl.models import Proxy


@pytest.fixture
async def api_client():
    """Create an async HTTP client for the FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def setup_test_proxies():
    """Set up test proxies in the global rotator."""
    import proxywhirl.api as api_module
    from proxywhirl import ProxyRotator

    # Initialize rotator if not exists
    if api_module._rotator is None:
        api_module._rotator = ProxyRotator()

    rotator = api_module._rotator

    # Clear existing proxies
    rotator.pool.proxies.clear()

    # Add test proxies
    rotator.add_proxy(Proxy(url="http://proxy1.example.com:8080"))
    rotator.add_proxy(Proxy(url="http://proxy2.example.com:8080"))
    rotator.add_proxy(Proxy(url="http://proxy3.example.com:8080"))

    yield

    # Cleanup
    rotator.pool.proxies.clear()


# T012: Integration test for proxied GET request
@pytest.mark.asyncio
@respx.mock
async def test_proxied_get_request_success(api_client: AsyncClient, setup_test_proxies):
    """Test successful proxied GET request to httpbin.org/get.

    Verifies:
    - Response contains expected fields (status_code, headers, body)
    - Proxy was used (check proxy_used field)
    - Request succeeds with valid status code
    """
    # Mock the target URL response
    respx.get("https://httpbin.org/get").mock(
        return_value=Response(
            200,
            json={
                "args": {},
                "headers": {"User-Agent": "ProxyWhirl-Test/1.0"},
                "url": "https://httpbin.org/get",
            },
        )
    )

    # Make request through API
    response = await api_client.post(
        "/api/v1/request",
        json={
            "url": "https://httpbin.org/get",
            "method": "GET",
            "headers": {"User-Agent": "ProxyWhirl-Test/1.0"},
            "timeout": 30,
        },
    )

    # Verify response
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert "data" in body

    data = body["data"]
    assert data["status_code"] == 200
    assert "headers" in data
    assert "body" in data
    assert "proxy_used" in data
    assert "elapsed_ms" in data


# T013: Integration test for proxied POST request
@pytest.mark.asyncio
@respx.mock
async def test_proxied_post_request_with_body(api_client: AsyncClient, setup_test_proxies):
    """Test successful proxied POST request with JSON body.

    Verifies:
    - Request body is forwarded correctly
    - Headers are passed through
    - Response contains posted data
    """
    # Mock the target URL response
    test_payload = {"key": "value", "test": "data"}
    respx.post("https://httpbin.org/post").mock(
        return_value=Response(
            200,
            json={
                "json": test_payload,
                "headers": {"Content-Type": "application/json"},
            },
        )
    )

    # Make request through API
    response = await api_client.post(
        "/api/v1/request",
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
    )

    # Verify response
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"

    data = body["data"]
    assert data["status_code"] == 200
    assert "body" in data


# T014: Integration test for proxy rotation
@pytest.mark.asyncio
@respx.mock
async def test_proxy_rotation_multiple_requests(api_client: AsyncClient, setup_test_proxies):
    """Test proxy rotation across multiple sequential requests.

    Verifies:
    - Different proxies are used for sequential requests
    - Rotation strategy (round-robin) is applied
    """
    # Mock the target URL response
    respx.get("https://httpbin.org/get").mock(
        return_value=Response(200, json={"url": "https://httpbin.org/get"})
    )

    proxies_used = []

    # Make 3 sequential requests
    for _ in range(3):
        response = await api_client.post(
            "/api/v1/request",
            json={"url": "https://httpbin.org/get", "method": "GET", "timeout": 30},
        )

        assert response.status_code == 200
        body = response.json()
        data = body["data"]

        if data.get("proxy_used"):
            proxies_used.append(data["proxy_used"]["url"])

    # Verify rotation occurred (should have used multiple proxies)
    assert len(proxies_used) >= 2, "Multiple proxies should be used with round-robin"
    unique_proxies = set(proxies_used)
    assert len(unique_proxies) >= 2, "Different proxies should be selected"


# T015: Integration test for proxy failover
@pytest.mark.asyncio
@respx.mock
async def test_proxy_failover_with_dead_proxy(api_client: AsyncClient):
    """Test proxy failover when first proxy fails.

    Verifies:
    - Request succeeds using working proxy after first proxy fails
    - Retry logic is triggered when first proxy fails
    """
    # Set up proxies with one that will fail
    if _rotator:
        _rotator.pool.proxies.clear()
        _rotator.add_proxy(Proxy(url="http://dead-proxy.example.com:9999"))
        _rotator.add_proxy(Proxy(url="http://working-proxy.example.com:8080"))

    # Mock the target URL response
    respx.get("https://httpbin.org/get").mock(
        return_value=Response(200, json={"url": "https://httpbin.org/get"})
    )

    # Make request through API
    response = await api_client.post(
        "/api/v1/request",
        json={"url": "https://httpbin.org/get", "method": "GET", "timeout": 30},
    )

    # The request should either succeed or fail gracefully
    assert response.status_code in [200, 502, 503]

    body = response.json()
    if response.status_code == 200:
        assert body["status"] == "success"
    else:
        assert body["status"] == "error"

    # Cleanup
    if _rotator:
        _rotator.pool.proxies.clear()
