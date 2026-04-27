"""Tests for API v2 core functionality."""

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from proxywhirl.api.v2.auth import APIKeyAuth, create_api_key
from proxywhirl.api.v2.core import API_KEYS, RATE_LIMITS, app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def api_key():
    """Create a test API key."""
    key_id, key_secret = create_api_key("test-key")
    api_key = APIKeyAuth(
        key_id=key_id,
        key_secret=key_secret,
        name="test-key",
        requests_per_minute=100,
        requests_per_hour=10000,
    )
    API_KEYS[key_id] = api_key
    yield api_key
    # Cleanup
    if key_id in API_KEYS:
        del API_KEYS[key_id]
    if key_id in RATE_LIMITS:
        del RATE_LIMITS[key_id]


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/v2/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "2.0.0"


def test_list_proxies_without_auth(client):
    """Test listing proxies without authentication."""
    response = client.get("/api/v2/proxies")
    assert response.status_code == 401


def test_list_proxies_with_auth(client, api_key):
    """Test listing proxies with valid authentication."""
    headers = {"Authorization": f"Bearer {api_key.key_id}"}
    response = client.get("/api/v2/proxies", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "metadata" in data
    assert data["data"]["total"] == 10
    assert data["data"]["page"] == 1


def test_get_proxy(client, api_key):
    """Test getting a specific proxy."""
    headers = {"Authorization": f"Bearer {api_key.key_id}"}
    response = client.get("/api/v2/proxies/proxy-123", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == "proxy-123"
    assert data["data"]["protocol"] == "http"


def test_invalid_api_key(client):
    """Test with invalid API key."""
    headers = {"Authorization": "Bearer invalid-key"}
    response = client.get("/api/v2/proxies", headers=headers)
    assert response.status_code == 401


def test_malformed_auth_header(client):
    """Test with malformed authorization header."""
    headers = {"Authorization": "InvalidFormat"}
    response = client.get("/api/v2/proxies", headers=headers)
    assert response.status_code == 401


def test_expired_api_key(client):
    """Test with expired API key."""
    key_id, key_secret = create_api_key("expired-key")
    api_key = APIKeyAuth(
        key_id=key_id,
        key_secret=key_secret,
        name="expired-key",
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    API_KEYS[key_id] = api_key

    headers = {"Authorization": f"Bearer {key_id}"}
    response = client.get("/api/v2/proxies", headers=headers)
    assert response.status_code == 403

    # Cleanup
    del API_KEYS[key_id]


def test_inactive_api_key(client):
    """Test with inactive API key."""
    key_id, key_secret = create_api_key("inactive-key")
    api_key = APIKeyAuth(
        key_id=key_id,
        key_secret=key_secret,
        name="inactive-key",
        is_active=False,
    )
    API_KEYS[key_id] = api_key

    headers = {"Authorization": f"Bearer {key_id}"}
    response = client.get("/api/v2/proxies", headers=headers)
    assert response.status_code == 403

    # Cleanup
    del API_KEYS[key_id]


def test_pagination(client, api_key):
    """Test pagination parameters."""
    headers = {"Authorization": f"Bearer {api_key.key_id}"}

    # Page 1
    response = client.get("/api/v2/proxies?page=1&page_size=5", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["page"] == 1
    assert data["data"]["page_size"] == 5
    assert len(data["data"]["items"]) == 5

    # Page 2
    response = client.get("/api/v2/proxies?page=2&page_size=5", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["page"] == 2
    assert data["data"]["has_previous"] is True
    assert data["data"]["has_next"] is False


def test_response_metadata(client, api_key):
    """Test response metadata is included."""
    headers = {"Authorization": f"Bearer {api_key.key_id}"}
    response = client.get("/api/v2/proxies", headers=headers)

    data = response.json()
    assert "metadata" in data
    assert "request_id" in data["metadata"]
    assert "timestamp" in data["metadata"]
    assert "processing_time_ms" in data["metadata"]
    assert data["metadata"]["api_version"] == "2.0"
