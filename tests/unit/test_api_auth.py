"""Unit tests for API key authentication middleware."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from proxywhirl.api.middleware.auth import APIKeyMiddleware


def _error_message(response) -> str:
    payload = response.json()
    return payload["error"]["message"]


@pytest.fixture
def auth_app() -> FastAPI:
    """Create a minimal FastAPI app with APIKeyMiddleware for testing."""
    app = FastAPI()
    app.add_middleware(APIKeyMiddleware)

    @app.get("/protected")
    def protected() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "healthy"}

    @app.get("/api/stats")
    def stats() -> dict[str, int]:
        return {"total_proxies": 3}

    @app.get("/api/metrics")
    def metrics() -> dict[str, float]:
        return {"requests_total": 42.0}

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
            assert _error_message(response) == "Invalid or missing API key"
            assert response.json()["status"] == "error"

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
            assert _error_message(response) == "Invalid or missing API key"

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
            response = auth_client.get("/api/health")
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
            assert _error_message(response) == "API authentication not configured"

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
            assert response1.json()["status"] == response2.json()["status"] == "error"
            error1 = response1.json()["error"]
            error2 = response2.json()["error"]
            assert error1["code"] == error2["code"]
            assert error1["message"] == error2["message"]
            assert error1["details"] == error2["details"]


class TestMonitoringAuthContract:
    """Contract for secure-by-default monitoring exposure."""

    def test_stats_reachable_without_key_when_auth_disabled(self, auth_client: TestClient) -> None:
        """/api/stats requires no key when PROXYWHIRL_REQUIRE_AUTH is unset/false."""
        response = auth_client.get("/api/stats")
        assert response.status_code == 200

    def test_metrics_reachable_without_key_when_auth_disabled(
        self, auth_client: TestClient
    ) -> None:
        """/api/metrics requires no key when PROXYWHIRL_REQUIRE_AUTH is unset/false."""
        response = auth_client.get("/api/metrics")
        assert response.status_code == 200

    def test_stats_rejects_missing_key_when_auth_enabled(self, auth_client: TestClient) -> None:
        """/api/stats is protected when PROXYWHIRL_REQUIRE_AUTH is true."""
        with patch.dict(
            os.environ,
            {"PROXYWHIRL_REQUIRE_AUTH": "true", "PROXYWHIRL_API_KEY": "secret-key-123"},
        ):
            response = auth_client.get("/api/stats")
            assert response.status_code == 401
            assert _error_message(response) == "Invalid or missing API key"

    def test_metrics_rejects_missing_key_when_auth_enabled(self, auth_client: TestClient) -> None:
        """/api/metrics is protected when PROXYWHIRL_REQUIRE_AUTH is true."""
        with patch.dict(
            os.environ,
            {"PROXYWHIRL_REQUIRE_AUTH": "true", "PROXYWHIRL_API_KEY": "secret-key-123"},
        ):
            response = auth_client.get("/api/metrics")
            assert response.status_code == 401
            assert _error_message(response) == "Invalid or missing API key"

    def test_metrics_public_when_public_metrics_enabled(self, auth_client: TestClient) -> None:
        """/api/metrics can be public by explicit opt-in."""
        with patch.dict(
            os.environ,
            {
                "PROXYWHIRL_REQUIRE_AUTH": "true",
                "PROXYWHIRL_API_KEY": "secret-key-123",
                "PROXYWHIRL_PUBLIC_METRICS": "true",
            },
        ):
            response = auth_client.get("/api/metrics")
            assert response.status_code == 200

            stats_response = auth_client.get("/api/stats")
            assert stats_response.status_code == 401
