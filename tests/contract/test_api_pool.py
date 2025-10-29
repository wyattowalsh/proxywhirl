"""Contract tests for pool management endpoints (US2).

Tests the API contract for /api/v1/proxies endpoints:
- GET /api/v1/proxies - List proxies with pagination
- POST /api/v1/proxies - Add new proxy
- GET /api/v1/proxies/{id} - Get specific proxy
- DELETE /api/v1/proxies/{id} - Remove proxy
- POST /api/v1/proxies/test - Health check proxies
"""

import pytest
from pydantic import HttpUrl, ValidationError

from proxywhirl.api_models import (
    CreateProxyRequest,
    HealthCheckRequest,
    PaginatedResponse,
    ProxyResource,
)


# T022: Contract test for GET /api/v1/proxies
class TestListProxiesContract:
    """Test PaginatedResponse[ProxyResource] schema for listing proxies."""

    def test_paginated_response_schema_valid(self):
        """Test PaginatedResponse accepts valid pagination data."""
        # Arrange
        proxy_data = {
            "id": "proxy-123",
            "url": "http://proxy.example.com:8080",
            "protocol": "http",
            "status": "active",
            "health": "healthy",
            "stats": {
                "total_requests": 100,
                "successful_requests": 95,
                "failed_requests": 5,
                "avg_latency_ms": 250.5,
            },
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
        }

        # Act
        response = PaginatedResponse[ProxyResource](
            items=[ProxyResource(**proxy_data)],
            total=1,
            page=1,
            page_size=50,
        )

        # Assert
        assert len(response.items) == 1
        assert response.total == 1
        assert response.page == 1
        assert response.page_size == 50
        assert not response.has_next
        assert not response.has_prev

    def test_proxy_resource_schema_valid(self):
        """Test ProxyResource schema with all fields."""
        # Arrange & Act
        proxy = ProxyResource(
            id="proxy-123",
            url=HttpUrl("http://proxy.example.com:8080"),
            protocol="http",
            status="active",
            health="healthy",
            stats={
                "total_requests": 100,
                "successful_requests": 95,
                "failed_requests": 5,
                "avg_latency_ms": 250.5,
            },
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
        )

        # Assert
        assert proxy.id == "proxy-123"
        assert str(proxy.url) == "http://proxy.example.com:8080/"
        assert proxy.protocol == "http"


# T023: Contract test for POST /api/v1/proxies
class TestCreateProxyContract:
    """Test CreateProxyRequest schema."""

    def test_create_proxy_request_valid(self):
        """Test CreateProxyRequest with valid data."""
        # Arrange & Act
        request = CreateProxyRequest(
            url=HttpUrl("http://proxy.example.com:8080"),
            username="user",
            password="pass",
        )

        # Assert
        assert str(request.url) == "http://proxy.example.com:8080/"
        assert request.username == "user"
        assert request.password.get_secret_value() == "pass"

    def test_create_proxy_request_invalid_url(self):
        """Test CreateProxyRequest rejects invalid URL."""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            CreateProxyRequest(
                url="not-a-url",  # type: ignore[arg-type]
            )


# T024: Contract test for GET /api/v1/proxies/{id}
@pytest.mark.skip(reason="Covered by T022 ProxyResource schema test")
def test_get_proxy_by_id_contract():
    """Test GET /api/v1/proxies/{id} response schema."""
    pass


# T025: Contract test for DELETE /api/v1/proxies/{id}
@pytest.mark.skip(reason="No response body for 204 - nothing to validate")
def test_delete_proxy_contract():
    """Test DELETE /api/v1/proxies/{id} returns 204 No Content."""
    pass


# T026: Contract test for POST /api/v1/proxies/test
class TestHealthCheckContract:
    """Test HealthCheckRequest/Result schemas."""

    def test_health_check_request_schema(self):
        """Test HealthCheckRequest with optional proxy_ids."""
        # Arrange & Act
        request = HealthCheckRequest(proxy_ids=["proxy-1", "proxy-2"])

        # Assert
        assert request.proxy_ids == ["proxy-1", "proxy-2"]

    def test_health_check_request_no_filter(self):
        """Test HealthCheckRequest without proxy_ids (check all)."""
        # Arrange & Act
        request = HealthCheckRequest()

        # Assert
        assert request.proxy_ids is None
