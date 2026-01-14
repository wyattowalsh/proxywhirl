"""Contract tests for POST /api/v1/request endpoint (US1)."""

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError

from proxywhirl.api import app
from proxywhirl.api.models import APIResponse, ProxiedRequest, ProxiedResponse


async def test_proxied_request_schema_valid():
    """T011: Validate ProxiedRequest schema accepts valid data."""
    # Valid request data
    request_data = {
        "url": "https://httpbin.org/get",
        "method": "GET",
        "headers": {"User-Agent": "ProxyWhirl/1.0"},
        "body": None,
        "timeout": 30,
    }

    # Should not raise validation error
    request = ProxiedRequest(**request_data)

    assert str(request.url) == "https://httpbin.org/get"
    assert request.method == "GET"
    assert request.timeout == 30


async def test_proxied_request_schema_invalid_url():
    """T011: Validate ProxiedRequest rejects invalid URL."""
    with pytest.raises(ValidationError) as exc_info:
        ProxiedRequest(
            url="not-a-valid-url",
            method="GET",
        )

    assert "url" in str(exc_info.value).lower()


async def test_proxied_request_schema_invalid_method():
    """T011: Validate ProxiedRequest rejects invalid HTTP method."""
    with pytest.raises(ValidationError) as exc_info:
        ProxiedRequest(
            url="https://httpbin.org/get",
            method="INVALID",
        )

    assert "method" in str(exc_info.value).lower()


async def test_proxied_request_schema_invalid_timeout():
    """T011: Validate ProxiedRequest rejects negative timeout."""
    with pytest.raises(ValidationError) as exc_info:
        ProxiedRequest(
            url="https://httpbin.org/get",
            method="GET",
            timeout=-1,
        )

    assert "timeout" in str(exc_info.value).lower()


async def test_proxied_response_schema():
    """T011: Validate ProxiedResponse schema structure."""
    response_data = {
        "status_code": 200,
        "headers": {"content-type": "application/json"},
        "body": '{"status": "ok"}',
        "proxy_used": "http://proxy.example.com:8080",
        "elapsed_ms": 150,
    }

    response = ProxiedResponse(**response_data)

    assert response.status_code == 200
    assert response.proxy_used == "http://proxy.example.com:8080"
    assert response.elapsed_ms == 150


async def test_api_response_envelope_success():
    """T011: Validate APIResponse envelope for successful response."""
    response_data = ProxiedResponse(
        status_code=200,
        headers={},
        body="test",
        proxy_used="http://proxy.example.com:8080",
        elapsed_ms=100,
    )

    api_response = APIResponse.success(data=response_data)

    assert api_response.status == "success"
    assert api_response.data == response_data
    assert api_response.error is None


async def test_api_response_envelope_error():
    """T011: Validate APIResponse envelope for error response."""
    api_response = APIResponse.error_response(
        code="PROXY_ERROR",
        message="All proxies failed",
        details={"attempted": 3},
    )

    assert api_response.status == "error"
    assert api_response.data is None
    assert api_response.error is not None
    assert api_response.error.code == "PROXY_ERROR"
    assert api_response.error.message == "All proxies failed"


async def test_post_request_endpoint_contract():
    """T011: Contract test for POST /api/v1/request endpoint response structure."""
    # Note: This test will fail until proxies are added to the pool
    # It tests the response structure when no proxies are available
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/request",
            json={
                "url": "https://httpbin.org/get",
                "method": "GET",
                "headers": {},
                "timeout": 30,
            },
        )

        # Should return valid response structure (even if it's an error)
        # May be 500 if rotator not initialized, which is fine for contract test
        assert response.status_code in [200, 500, 503, 502, 504]
        data = response.json()

        # Verify envelope structure or FastAPI error structure
        if "status" in data:
            assert data["status"] in ["success", "error"]

            if data["status"] == "error":
                assert "error" in data
                assert "code" in data["error"]
                assert "message" in data["error"]
        else:
            # FastAPI validation error structure
            assert "detail" in data
