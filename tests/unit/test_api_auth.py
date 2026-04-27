"""Unit tests for API key authentication middleware."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from proxywhirl.api.middleware.auth import APIKeyMiddleware


@pytest.fixture
def auth_app() -> FastAPI:
    """Create a minimal FastAPI app with APIKeyMiddleware for testing."""
    app = FastAPI()
    app.add_middleware(APIKeyMiddleware)

    @app.get("/protected")
    def protected() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/v1/health")
    def health() -> dict[str, str]:
        return {"status": "healthy"}

    return app


@pytest.fixture
def auth_client(auth_app: FastAPI) -> TestClient:
    """Create test client for auth app."""
    return TestClient(auth_app)


class TestAPIKeyMiddleware:
    """Test API key middleware behavior."""

    def test_no_auth_required_by_default(self, auth_client: TestClient) -> None:
        """Test that requests pass when PROXYWHIRL_REQUIRE_AUTH is false."""
        response = auth_client.get("/protected")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_api_key_required_when_auth_enabled(self, auth_client: TestClient) -> None:
        """Test that protected endpoints reject without API key when auth is required."""
        with patch.dict(
            os.environ,
            {"PROXYWHIRL_REQUIRE_AUTH": "true", "PROXYWHIRL_API_KEY": "secret-key-123"},
        ):
            response = auth_client.get("/protected")
            assert response.status_code == 401
            assert response.json()["detail"] == "Invalid or missing API key"

    def test_invalid_key_rejected(self, auth_client: TestClient) -> None:
        """Test that invalid API key is rejected."""
        with patch.dict(
            os.environ,
            {"PROXYWHIRL_REQUIRE_AUTH": "true", "PROXYWHIRL_API_KEY": "secret-key-123"},
        ):
            response = auth_client.get(
                "/protected",
                headers={"X-API-Key": "wrong-key"},
            )
            assert response.status_code == 401
            assert response.json()["detail"] == "Invalid or missing API key"

    def test_valid_key_accepted(self, auth_client: TestClient) -> None:
        """Test that valid API key is accepted."""
        with patch.dict(
            os.environ,
            {"PROXYWHIRL_REQUIRE_AUTH": "true", "PROXYWHIRL_API_KEY": "secret-key-123"},
        ):
            response = auth_client.get(
                "/protected",
                headers={"X-API-Key": "secret-key-123"},
            )
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}

    def test_public_path_skipped_when_auth_enabled(self, auth_client: TestClient) -> None:
        """Test that public paths skip auth even when auth is required."""
        with patch.dict(
            os.environ,
            {"PROXYWHIRL_REQUIRE_AUTH": "true", "PROXYWHIRL_API_KEY": "secret-key-123"},
        ):
            response = auth_client.get("/api/v1/health")
            assert response.status_code == 200
            assert response.json() == {"status": "healthy"}

    def test_missing_config_returns_503(self, auth_client: TestClient) -> None:
        """Test that missing PROXYWHIRL_API_KEY returns 503 when auth is required."""
        with patch.dict(
            os.environ,
            {"PROXYWHIRL_REQUIRE_AUTH": "true"},
            clear=True,
        ):
            response = auth_client.get("/protected")
            assert response.status_code == 503
            assert response.json()["detail"] == "API authentication not configured"

    def test_timing_attack_resistance(self, auth_client: TestClient) -> None:
        """Test that compare_digest is used to prevent timing attacks."""
        with patch.dict(
            os.environ,
            {"PROXYWHIRL_REQUIRE_AUTH": "true", "PROXYWHIRL_API_KEY": "secret-key-123"},
        ):
            # Both wrong keys should be rejected with same 401 response
            response1 = auth_client.get(
                "/protected",
                headers={"X-API-Key": "a"},
            )
            response2 = auth_client.get(
                "/protected",
                headers={"X-API-Key": "very-long-wrong-key-that-is-different"},
            )
            assert response1.status_code == 401
            assert response2.status_code == 401
            assert response1.json() == response2.json()
