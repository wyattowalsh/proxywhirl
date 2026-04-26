"""Tests for API v2 endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from proxywhirl.api.core import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestV2HealthCheck:
    """Test health check endpoint."""

    def test_health_check_returns_200(self, client: TestClient) -> None:
        """Test that health check returns 200."""
        response = client.get("/api/v2/health")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "healthy"
        assert data["timestamp"]
        assert data["trace_id"]

    def test_health_check_response_structure(self, client: TestClient) -> None:
        """Test health check response has correct structure."""
        response = client.get("/api/v2/health")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "data" in data
        assert "timestamp" in data


class TestV2ListProxies:
    """Test proxy listing endpoint."""

    def test_list_proxies_returns_200(self, client: TestClient) -> None:
        """Test that list proxies returns 200."""
        response = client.get("/api/v2/proxies")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "proxies" in data["data"]
        assert "pagination" in data["data"]

    def test_list_proxies_with_limit(self, client: TestClient) -> None:
        """Test list proxies with limit parameter."""
        response = client.get("/api/v2/proxies?limit=20")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["pagination"]["limit"] == 20

    def test_list_proxies_with_offset(self, client: TestClient) -> None:
        """Test list proxies with offset parameter."""
        response = client.get("/api/v2/proxies?offset=10")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["pagination"]["offset"] == 10

    def test_list_proxies_with_protocol_filter(self, client: TestClient) -> None:
        """Test list proxies with protocol filter."""
        response = client.get("/api/v2/proxies?protocol=http")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_list_proxies_with_country_filter(self, client: TestClient) -> None:
        """Test list proxies with country filter."""
        response = client.get("/api/v2/proxies?country=US")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_list_proxies_invalid_limit(self, client: TestClient) -> None:
        """Test list proxies with invalid limit."""
        response = client.get("/api/v2/proxies?limit=1000")
        assert response.status_code == 422  # Validation error


class TestV2ValidateProxy:
    """Test proxy validation endpoint."""

    def test_validate_proxy_returns_200(self, client: TestClient) -> None:
        """Test that validate proxy returns 200."""
        response = client.post(
            "/api/v2/proxies/validate",
            params={"host": "proxy.example.com", "port": 8080, "protocol": "http"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "valid" in data["data"]

    def test_validate_proxy_required_params(self, client: TestClient) -> None:
        """Test validate proxy requires host and port."""
        response = client.post("/api/v2/proxies/validate")
        assert response.status_code == 422

    def test_validate_proxy_invalid_port(self, client: TestClient) -> None:
        """Test validate proxy with invalid port."""
        response = client.post(
            "/api/v2/proxies/validate",
            params={"host": "proxy.example.com", "port": 99999, "protocol": "http"},
        )
        assert response.status_code == 422


class TestV2Pools:
    """Test proxy pool endpoints."""

    def test_list_pools_returns_200(self, client: TestClient) -> None:
        """Test that list pools returns 200."""
        response = client.get("/api/v2/pools")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "pools" in data["data"]
        assert "pagination" in data["data"]

    def test_get_pool_returns_200(self, client: TestClient) -> None:
        """Test that get pool returns 200."""
        response = client.get("/api/v2/pools/pool_123")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["pool_id"] == "pool_123"

    def test_rotate_proxy_returns_200(self, client: TestClient) -> None:
        """Test that rotate proxy returns 200."""
        response = client.get("/api/v2/pools/pool_123/rotate")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "proxy" in data["data"]

    def test_create_pool_empty_proxies(self, client: TestClient) -> None:
        """Test create pool with empty proxies list."""
        response = client.post(
            "/api/v2/pools",
            json={"name": "test", "proxies": [], "rotation_strategy": "round_robin"},
        )
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False


class TestV2Stats:
    """Test stats endpoint."""

    def test_get_stats_returns_200(self, client: TestClient) -> None:
        """Test that get stats returns 200."""
        response = client.get("/api/v2/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "total_proxies" in data["data"]
        assert "total_pools" in data["data"]


class TestV2BatchValidation:
    """Test batch validation endpoint."""

    def test_batch_validate_returns_200(self, client: TestClient) -> None:
        """Test that batch validate returns 200."""
        response = client.post(
            "/api/v2/batches/validate",
            json={
                "proxies": [
                    {"host": "proxy1.example.com", "port": 8080},
                    {"host": "proxy2.example.com", "port": 8080},
                ]
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "batch_id" in data["data"]

    def test_batch_validate_with_timeout(self, client: TestClient) -> None:
        """Test batch validate with timeout parameter."""
        response = client.post(
            "/api/v2/batches/validate",
            params={"timeout": 30.0},
            json={"proxies": [{"host": "proxy.example.com", "port": 8080}]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestV2ResponseFormat:
    """Test response format consistency."""

    def test_all_responses_have_timestamp(self, client: TestClient) -> None:
        """Test that all responses include timestamp."""
        endpoints = [
            "/api/v2/health",
            "/api/v2/proxies",
            "/api/v2/pools",
            "/api/v2/stats",
        ]
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            data = response.json()
            assert "timestamp" in data
            assert isinstance(data["timestamp"], str)

    def test_error_responses_have_error_field(self, client: TestClient) -> None:
        """Test that error responses have error field."""
        # Create pool with empty proxies to trigger error
        response = client.post(
            "/api/v2/pools",
            json={"name": "test", "proxies": [], "rotation_strategy": "round_robin"},
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert data["success"] is False

    def test_success_responses_have_data_field(self, client: TestClient) -> None:
        """Test that success responses have data field."""
        response = client.get("/api/v2/health")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
