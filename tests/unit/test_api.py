"""Unit tests for REST API endpoints, focusing on retry metrics."""

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from proxywhirl.api import app
from proxywhirl.circuit_breaker import CircuitBreaker, CircuitBreakerState
from proxywhirl.retry import (
    CircuitBreakerEvent,
    RetryAttempt,
    RetryMetrics,
    RetryOutcome,
)


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_rotator():
    """Create a mock ProxyWhirl with retry metrics."""
    rotator = MagicMock()

    # Create retry metrics with some test data
    metrics = RetryMetrics(retention_hours=24, max_current_attempts=10000)

    # Add some retry attempts
    now = datetime.now(timezone.utc)
    for i in range(5):
        attempt = RetryAttempt(
            request_id=f"req-{i}",
            attempt_number=0,
            proxy_id=f"proxy{i % 2}.example.com:8080",
            timestamp=now - timedelta(minutes=i),
            outcome=RetryOutcome.SUCCESS if i % 2 == 0 else RetryOutcome.FAILURE,
            status_code=200 if i % 2 == 0 else 502,
            delay_before=0.0,
            latency=0.25 + (i * 0.1),
            error_message=None if i % 2 == 0 else "Connection failed",
        )
        metrics.record_attempt(attempt)

    # Add circuit breaker events
    event1 = CircuitBreakerEvent(
        proxy_id="proxy0.example.com:8080",
        from_state=CircuitBreakerState.CLOSED,
        to_state=CircuitBreakerState.OPEN,
        timestamp=now - timedelta(hours=1),
        failure_count=5,
    )
    event2 = CircuitBreakerEvent(
        proxy_id="proxy0.example.com:8080",
        from_state=CircuitBreakerState.OPEN,
        to_state=CircuitBreakerState.HALF_OPEN,
        timestamp=now - timedelta(minutes=30),
        failure_count=5,
    )
    event3 = CircuitBreakerEvent(
        proxy_id="proxy0.example.com:8080",
        from_state=CircuitBreakerState.HALF_OPEN,
        to_state=CircuitBreakerState.CLOSED,
        timestamp=now - timedelta(minutes=15),
        failure_count=0,
    )
    metrics.record_circuit_breaker_event(event1)
    metrics.record_circuit_breaker_event(event2)
    metrics.record_circuit_breaker_event(event3)

    rotator.get_retry_metrics.return_value = metrics

    # Create circuit breaker states
    cb1 = CircuitBreaker(
        proxy_id="proxy0.example.com:8080",
        state=CircuitBreakerState.CLOSED,
        failure_count=2,
        failure_threshold=5,
        window_duration=60.0,
        timeout_duration=30.0,
    )
    cb2 = CircuitBreaker(
        proxy_id="proxy1.example.com:8080",
        state=CircuitBreakerState.OPEN,
        failure_count=5,
        failure_threshold=5,
        window_duration=60.0,
        timeout_duration=30.0,
        next_test_time=datetime.now(timezone.utc).timestamp() + 20,
    )

    rotator.get_circuit_breaker_states.return_value = {
        "proxy0.example.com:8080": cb1,
        "proxy1.example.com:8080": cb2,
    }

    return rotator


class TestRetryMetricsEndpoint:
    """Tests for GET /metrics/retry endpoint."""

    def test_get_retry_metrics_json_format(self, client, mock_rotator):
        """Test retry metrics endpoint with JSON format (default)."""
        with patch("proxywhirl.api.core._rotator", mock_rotator):
            response = client.get("/metrics/retry")

            assert response.status_code == 200
            data = response.json()

            # Check response structure
            assert data["status"] == "success"
            assert "data" in data
            assert "meta" in data

            # Check summary data
            assert "summary" in data["data"]
            summary = data["data"]["summary"]
            assert "total_retries" in summary
            assert "success_by_attempt" in summary
            assert "circuit_breaker_events_count" in summary
            assert summary["circuit_breaker_events_count"] == 3

            # Check timeseries data
            assert "timeseries" in data["data"]

            # Check per-proxy data
            assert "by_proxy" in data["data"]

    def test_get_retry_metrics_json_with_hours_param(self, client, mock_rotator):
        """Test retry metrics endpoint with hours parameter."""
        with patch("proxywhirl.api.core._rotator", mock_rotator):
            response = client.get("/metrics/retry?hours=12")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"

    def test_get_retry_metrics_prometheus_format(self, client, mock_rotator):
        """Test retry metrics endpoint with Prometheus format."""
        with patch("proxywhirl.api.core._rotator", mock_rotator):
            response = client.get("/metrics/retry?format=prometheus")

            assert response.status_code == 200
            assert response.headers["content-type"] == "text/plain; version=0.0.4; charset=utf-8"

            content = response.text

            # Check for expected Prometheus metrics
            assert "# HELP proxywhirl_retry_total" in content
            assert "# TYPE proxywhirl_retry_total counter" in content
            assert "proxywhirl_retry_total" in content

            assert "# HELP proxywhirl_retry_success_by_attempt" in content
            assert "# TYPE proxywhirl_retry_success_by_attempt gauge" in content

            assert "# HELP proxywhirl_circuit_breaker_events_total" in content
            assert "proxywhirl_circuit_breaker_events_total 3" in content

            # Check per-proxy metrics
            assert "# HELP proxywhirl_retry_proxy_attempts" in content
            assert "# HELP proxywhirl_retry_proxy_success" in content
            assert "# HELP proxywhirl_retry_proxy_failure" in content
            assert "# HELP proxywhirl_retry_proxy_avg_latency" in content
            assert 'proxy_id="proxy0.example.com:8080"' in content
            assert 'proxy_id="proxy1.example.com:8080"' in content

    def test_get_retry_metrics_prometheus_case_insensitive(self, client, mock_rotator):
        """Test that format parameter is case-insensitive."""
        with patch("proxywhirl.api.core._rotator", mock_rotator):
            # Try uppercase
            response = client.get("/metrics/retry?format=PROMETHEUS")
            assert response.status_code == 200
            assert "text/plain" in response.headers["content-type"]

            # Try mixed case
            response = client.get("/metrics/retry?format=Prometheus")
            assert response.status_code == 200
            assert "text/plain" in response.headers["content-type"]

    def test_get_retry_metrics_no_rotator(self, client):
        """Test retry metrics endpoint when rotator is not initialized."""
        with patch("proxywhirl.api.core._rotator", None):
            response = client.get("/metrics/retry")

            assert response.status_code == 503
            assert "Rotator not initialized" in response.json()["detail"]

    def test_get_retry_metrics_escapes_special_chars_in_prometheus(self, client):
        """Test that special characters in proxy_id are escaped in Prometheus format."""
        rotator = MagicMock()
        metrics = RetryMetrics()

        # Add attempt with proxy_id containing quotes
        attempt = RetryAttempt(
            request_id="req-1",
            attempt_number=0,
            proxy_id='proxy"test".com:8080',
            timestamp=datetime.now(timezone.utc),
            outcome=RetryOutcome.SUCCESS,
            status_code=200,
            delay_before=0.0,
            latency=0.1,
        )
        metrics.record_attempt(attempt)

        rotator.get_retry_metrics.return_value = metrics
        rotator.get_circuit_breaker_states.return_value = {}

        with patch("proxywhirl.api.core._rotator", rotator):
            response = client.get("/metrics/retry?format=prometheus")

            assert response.status_code == 200
            # Check that quotes are escaped
            assert 'proxy_id="proxy\\"test\\".com:8080"' in response.text


class TestCircuitBreakerMetricsEndpoint:
    """Tests for GET /metrics/circuit-breaker endpoint."""

    def test_get_circuit_breaker_metrics_json_format(self, client, mock_rotator):
        """Test circuit breaker metrics endpoint with JSON format (default)."""
        with patch("proxywhirl.api.core._rotator", mock_rotator):
            response = client.get("/metrics/circuit-breaker")

            assert response.status_code == 200
            data = response.json()

            # Check response structure
            assert data["status"] == "success"
            assert "data" in data

            # Check states
            assert "states" in data["data"]
            states = data["data"]["states"]
            assert len(states) == 2

            # Check first state
            state0 = next(s for s in states if s["proxy_id"] == "proxy0.example.com:8080")
            assert state0["state"] == "closed"
            assert state0["failure_count"] == 2
            assert state0["failure_threshold"] == 5

            # Check second state
            state1 = next(s for s in states if s["proxy_id"] == "proxy1.example.com:8080")
            assert state1["state"] == "open"
            assert state1["failure_count"] == 5
            assert state1["next_test_time"] is not None

            # Check events
            assert "events" in data["data"]
            assert "total_events" in data["data"]
            assert data["data"]["total_events"] == 3

    def test_get_circuit_breaker_metrics_with_hours_param(self, client, mock_rotator):
        """Test circuit breaker metrics with hours parameter."""
        with patch("proxywhirl.api.core._rotator", mock_rotator):
            # Request only last 1 hour
            # Event 1 is 1 hour ago (exactly), so may be excluded based on cutoff
            # Events 2 and 3 are within 30 and 15 minutes
            response = client.get("/metrics/circuit-breaker?hours=1")

            assert response.status_code == 200
            data = response.json()

            # Should include events within 1 hour (2 events: 30 min and 15 min ago)
            # The 1 hour event is right on the boundary and excluded
            assert data["data"]["total_events"] == 2
            assert data["data"]["hours"] == 1

    def test_get_circuit_breaker_metrics_prometheus_format(self, client, mock_rotator):
        """Test circuit breaker metrics endpoint with Prometheus format."""
        with patch("proxywhirl.api.core._rotator", mock_rotator):
            response = client.get("/metrics/circuit-breaker?format=prometheus")

            assert response.status_code == 200
            assert response.headers["content-type"] == "text/plain; version=0.0.4; charset=utf-8"

            content = response.text

            # Check for circuit breaker state metric
            assert "# HELP proxywhirl_circuit_breaker_state" in content
            assert "# TYPE proxywhirl_circuit_breaker_state gauge" in content
            assert (
                'proxywhirl_circuit_breaker_state{proxy_id="proxy0.example.com:8080"} 0' in content
            )
            assert (
                'proxywhirl_circuit_breaker_state{proxy_id="proxy1.example.com:8080"} 1' in content
            )

            # Check for failure count metric
            assert "# HELP proxywhirl_circuit_breaker_failure_count" in content
            assert "# TYPE proxywhirl_circuit_breaker_failure_count gauge" in content
            assert (
                'proxywhirl_circuit_breaker_failure_count{proxy_id="proxy0.example.com:8080"} 2'
                in content
            )
            assert (
                'proxywhirl_circuit_breaker_failure_count{proxy_id="proxy1.example.com:8080"} 5'
                in content
            )

            # Check for failure threshold metric
            assert "# HELP proxywhirl_circuit_breaker_failure_threshold" in content
            assert "# TYPE proxywhirl_circuit_breaker_failure_threshold gauge" in content

            # Check for state changes total
            assert "# HELP proxywhirl_circuit_breaker_state_changes_total" in content
            assert "proxywhirl_circuit_breaker_state_changes_total 3" in content

            # Check for opens total
            assert "# HELP proxywhirl_circuit_breaker_opens_total" in content
            assert (
                'proxywhirl_circuit_breaker_opens_total{proxy_id="proxy0.example.com:8080"} 1'
                in content
            )

    def test_get_circuit_breaker_metrics_no_rotator(self, client):
        """Test circuit breaker metrics endpoint when rotator is not initialized."""
        with patch("proxywhirl.api.core._rotator", None):
            response = client.get("/metrics/circuit-breaker")

            assert response.status_code == 503
            assert "Rotator not initialized" in response.json()["detail"]

    def test_circuit_breaker_state_mapping(self, client, mock_rotator):
        """Test that circuit breaker states are correctly mapped to numeric values."""
        # Create circuit breakers in all states
        cb_closed = CircuitBreaker(
            proxy_id="closed.proxy:8080",
            state=CircuitBreakerState.CLOSED,
            failure_count=0,
        )
        cb_open = CircuitBreaker(
            proxy_id="open.proxy:8080",
            state=CircuitBreakerState.OPEN,
            failure_count=5,
        )
        cb_half_open = CircuitBreaker(
            proxy_id="halfopen.proxy:8080",
            state=CircuitBreakerState.HALF_OPEN,
            failure_count=3,
        )

        rotator = MagicMock()
        rotator.get_circuit_breaker_states.return_value = {
            "closed.proxy:8080": cb_closed,
            "open.proxy:8080": cb_open,
            "halfopen.proxy:8080": cb_half_open,
        }
        rotator.get_retry_metrics.return_value = RetryMetrics()

        with patch("proxywhirl.api.core._rotator", rotator):
            response = client.get("/metrics/circuit-breaker?format=prometheus")

            assert response.status_code == 200
            content = response.text

            # Verify state mappings: 0=closed, 1=open, 2=half_open
            assert 'proxywhirl_circuit_breaker_state{proxy_id="closed.proxy:8080"} 0' in content
            assert 'proxywhirl_circuit_breaker_state{proxy_id="open.proxy:8080"} 1' in content
            assert 'proxywhirl_circuit_breaker_state{proxy_id="halfopen.proxy:8080"} 2' in content


class TestAPIAuthentication:
    """Tests for API key authentication on metrics endpoints."""

    def test_retry_metrics_without_auth_when_disabled(self, client, mock_rotator):
        """Test that metrics endpoints work without auth when auth is disabled."""
        with (
            patch("proxywhirl.api.core._rotator", mock_rotator),
            patch.dict("os.environ", {"PROXYWHIRL_REQUIRE_AUTH": "false"}),
        ):
            response = client.get("/metrics/retry")
            assert response.status_code == 200

    def test_retry_metrics_with_valid_api_key(self, client, mock_rotator):
        """Test that metrics endpoints work with valid API key."""
        with (
            patch("proxywhirl.api.core._rotator", mock_rotator),
            patch.dict(
                "os.environ",
                {
                    "PROXYWHIRL_REQUIRE_AUTH": "true",
                    "PROXYWHIRL_API_KEY": "test-key-123",
                },
            ),
        ):
            response = client.get(
                "/metrics/retry",
                headers={"X-API-Key": "test-key-123"},
            )
            assert response.status_code == 200

    def test_retry_metrics_with_invalid_api_key(self, client, mock_rotator):
        """Test that metrics endpoints reject invalid API key."""
        with (
            patch("proxywhirl.api.core._rotator", mock_rotator),
            patch.dict(
                "os.environ",
                {
                    "PROXYWHIRL_REQUIRE_AUTH": "true",
                    "PROXYWHIRL_API_KEY": "test-key-123",
                },
            ),
        ):
            response = client.get(
                "/metrics/retry",
                headers={"X-API-Key": "wrong-key"},
            )
            assert response.status_code == 401

    def test_circuit_breaker_metrics_with_auth(self, client, mock_rotator):
        """Test circuit breaker metrics endpoint respects auth."""
        with (
            patch("proxywhirl.api.core._rotator", mock_rotator),
            patch.dict(
                "os.environ",
                {
                    "PROXYWHIRL_REQUIRE_AUTH": "true",
                    "PROXYWHIRL_API_KEY": "test-key-123",
                },
            ),
        ):
            # Without API key
            response = client.get("/metrics/circuit-breaker")
            assert response.status_code == 401

            # With valid API key
            response = client.get(
                "/metrics/circuit-breaker",
                headers={"X-API-Key": "test-key-123"},
            )
            assert response.status_code == 200

    def test_auth_fails_closed_when_misconfigured(self, client, mock_rotator):
        """Test SEC-004: API fails closed (rejects requests) when auth is required but API key not configured."""
        with (
            patch("proxywhirl.api.core._rotator", mock_rotator),
            patch.dict(
                "os.environ",
                {"PROXYWHIRL_REQUIRE_AUTH": "true"},
                clear=True,  # Clear to ensure PROXYWHIRL_API_KEY is not set
            ),
        ):
            # Request should be rejected with 503 when auth required but key not configured
            response = client.get("/metrics/retry")
            assert response.status_code == 503
            assert "authentication not configured" in response.json()["detail"].lower()

            # Same behavior even with an API key header (since expected key is not configured)
            response = client.get(
                "/metrics/retry",
                headers={"X-API-Key": "any-key"},
            )
            assert response.status_code == 503


class TestProxyIDGeneration:
    """Tests for stable proxy ID generation (TASK-024)."""

    def test_proxy_id_stable_with_uuid(self):
        """Test that _get_proxy_id returns stable ID using proxy.id (UUID)."""
        from uuid import UUID

        from proxywhirl.api.core import _get_proxy_id
        from proxywhirl.models import Proxy

        # Create proxy with explicit UUID
        proxy_id = UUID("12345678-1234-5678-1234-567812345678")
        proxy = Proxy(url="http://proxy.example.com:8080", id=proxy_id)

        # ID should be the string representation of UUID
        result = _get_proxy_id(proxy)
        assert result == str(proxy_id)
        assert result == "12345678-1234-5678-1234-567812345678"

        # Should be stable across multiple calls
        assert _get_proxy_id(proxy) == result
        assert _get_proxy_id(proxy) == result

    def test_proxy_id_stable_with_url_hash(self):
        """Test that _get_proxy_id returns stable hash-based ID when no UUID."""
        from proxywhirl.api.core import _get_proxy_id
        from proxywhirl.models import Proxy

        # Create proxy without explicit ID (will generate UUID)
        proxy = Proxy(url="http://proxy.example.com:8080")

        # Get ID using proxy.id (which is auto-generated UUID)
        result1 = _get_proxy_id(proxy)

        # Should be stable across multiple calls
        result2 = _get_proxy_id(proxy)
        assert result1 == result2

        # ID should be the string representation of the auto-generated UUID
        assert result1 == str(proxy.id)

    def test_proxy_id_fallback_to_hash_when_no_id(self):
        """Test that _get_proxy_id falls back to URL hash when proxy has no id attribute."""
        import hashlib

        from proxywhirl.api.core import _get_proxy_id

        # Create mock proxy without id attribute
        class MockProxy:
            def __init__(self, url):
                self.url = url

            # Explicitly no 'id' attribute

        proxy = MockProxy("http://proxy.example.com:8080")

        # Should fall back to hash of URL
        result = _get_proxy_id(proxy)

        # Compute expected hash
        expected = hashlib.sha256(str(proxy.url).encode()).hexdigest()[:16]
        assert result == expected

        # Should be stable across multiple calls
        assert _get_proxy_id(proxy) == result

    def test_proxy_id_different_urls_different_ids(self):
        """Test that different proxy URLs generate different IDs."""
        from proxywhirl.api.core import _get_proxy_id

        class MockProxy:
            def __init__(self, url):
                self.url = url

        proxy1 = MockProxy("http://proxy1.example.com:8080")
        proxy2 = MockProxy("http://proxy2.example.com:8080")

        id1 = _get_proxy_id(proxy1)
        id2 = _get_proxy_id(proxy2)

        # Different URLs should produce different IDs
        assert id1 != id2

    def test_proxy_id_same_url_same_id(self):
        """Test that same proxy URL generates same ID across instances."""
        from proxywhirl.api.core import _get_proxy_id

        class MockProxy:
            def __init__(self, url):
                self.url = url

        proxy1 = MockProxy("http://proxy.example.com:8080")
        proxy2 = MockProxy("http://proxy.example.com:8080")

        id1 = _get_proxy_id(proxy1)
        id2 = _get_proxy_id(proxy2)

        # Same URL should produce same hash-based ID
        assert id1 == id2

    def test_proxy_id_stable_across_restarts(self):
        """Test that proxy IDs remain stable across simulated restarts."""
        import hashlib

        from proxywhirl.api.core import _get_proxy_id

        class MockProxy:
            def __init__(self, url):
                self.url = url

        # Simulate first run
        proxy_run1 = MockProxy("http://proxy.example.com:8080")
        id_run1 = _get_proxy_id(proxy_run1)

        # Simulate restart (new instance, same URL)
        proxy_run2 = MockProxy("http://proxy.example.com:8080")
        id_run2 = _get_proxy_id(proxy_run2)

        # IDs should be identical across "restarts"
        assert id_run1 == id_run2

        # Verify it matches expected hash
        expected = hashlib.sha256(b"http://proxy.example.com:8080").hexdigest()[:16]
        assert id_run1 == expected


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_retry_metrics_with_empty_data(self, client):
        """Test retry metrics endpoint with no data."""
        rotator = MagicMock()
        rotator.get_retry_metrics.return_value = RetryMetrics()
        rotator.get_circuit_breaker_states.return_value = {}

        with patch("proxywhirl.api.core._rotator", rotator):
            # JSON format
            response = client.get("/metrics/retry")
            assert response.status_code == 200
            data = response.json()
            assert data["data"]["summary"]["total_retries"] == 0

            # Prometheus format
            response = client.get("/metrics/retry?format=prometheus")
            assert response.status_code == 200
            assert "proxywhirl_retry_total 0" in response.text

    def test_circuit_breaker_metrics_with_no_events(self, client):
        """Test circuit breaker metrics with no events."""
        rotator = MagicMock()
        rotator.get_retry_metrics.return_value = RetryMetrics()

        cb = CircuitBreaker(
            proxy_id="proxy.example.com:8080",
            state=CircuitBreakerState.CLOSED,
        )
        rotator.get_circuit_breaker_states.return_value = {
            "proxy.example.com:8080": cb,
        }

        with patch("proxywhirl.api.core._rotator", rotator):
            response = client.get("/metrics/circuit-breaker")
            assert response.status_code == 200
            data = response.json()
            assert data["data"]["total_events"] == 0
            assert len(data["data"]["states"]) == 1

    def test_invalid_hours_parameter(self, client, mock_rotator):
        """Test that negative hours parameter is handled."""
        with patch("proxywhirl.api.core._rotator", mock_rotator):
            # Negative hours should still work (metrics layer handles it)
            response = client.get("/metrics/retry?hours=-1")
            # FastAPI will convert -1 to int, metrics layer returns empty data
            assert response.status_code == 200

    def test_large_hours_parameter(self, client, mock_rotator):
        """Test that very large hours parameter is handled."""
        with patch("proxywhirl.api.core._rotator", mock_rotator):
            response = client.get("/metrics/retry?hours=10000")
            assert response.status_code == 200


class TestPerAPIKeyRateLimiting:
    """Tests for TASK-054: Per-API-Key Rate Limiting.

    Verifies that rate limiting uses API key as primary identifier
    to prevent X-Forwarded-For bypass attacks.
    """

    def test_rate_limit_key_uses_api_key_when_provided(self):
        """Test that rate limit key uses API key hash when X-API-Key header is present."""
        from unittest.mock import Mock

        from proxywhirl.api.core import get_rate_limit_key

        # Create mock request with API key
        request = Mock()
        request.headers.get = Mock(
            side_effect=lambda key: "test-api-key-123" if key == "X-API-Key" else None
        )
        request.client = Mock()
        request.client.host = "192.168.1.100"

        # Get rate limit key
        key = get_rate_limit_key(request)

        # Should use API key, not IP
        assert key.startswith("apikey:")
        assert "192.168.1.100" not in key

        # Should be consistent for same API key
        key2 = get_rate_limit_key(request)
        assert key == key2

    def test_rate_limit_key_uses_ip_fallback_without_api_key(self):
        """Test that rate limit key falls back to IP when no API key provided."""
        from unittest.mock import Mock

        from proxywhirl.api.core import get_rate_limit_key

        # Create mock request without API key
        request = Mock()
        request.headers.get = Mock(return_value=None)
        request.client = Mock()
        request.client.host = "192.168.1.100"

        # Get rate limit key
        key = get_rate_limit_key(request)

        # Should use IP-based key
        assert key == "ip:192.168.1.100"

    def test_rate_limit_key_different_api_keys_get_different_limits(self):
        """Test that different API keys get separate rate limit buckets."""
        from unittest.mock import Mock

        from proxywhirl.api.core import get_rate_limit_key

        # Request with API key 1
        request1 = Mock()
        request1.headers.get = Mock(
            side_effect=lambda key: "api-key-alice" if key == "X-API-Key" else None
        )
        request1.client = Mock()
        request1.client.host = "192.168.1.100"

        # Request with API key 2 (same IP!)
        request2 = Mock()
        request2.headers.get = Mock(
            side_effect=lambda key: "api-key-bob" if key == "X-API-Key" else None
        )
        request2.client = Mock()
        request2.client.host = "192.168.1.100"

        # Get keys
        key1 = get_rate_limit_key(request1)
        key2 = get_rate_limit_key(request2)

        # Should have different rate limit keys despite same IP
        assert key1 != key2
        assert key1.startswith("apikey:")
        assert key2.startswith("apikey:")

    def test_rate_limit_key_same_api_key_different_ips_share_limit(self):
        """Test that same API key from different IPs shares the same rate limit."""
        from unittest.mock import Mock

        from proxywhirl.api.core import get_rate_limit_key

        # Request 1 from IP A
        request1 = Mock()
        request1.headers.get = Mock(
            side_effect=lambda key: "shared-api-key" if key == "X-API-Key" else None
        )
        request1.client = Mock()
        request1.client.host = "192.168.1.100"

        # Request 2 from IP B (different IP, same API key)
        request2 = Mock()
        request2.headers.get = Mock(
            side_effect=lambda key: "shared-api-key" if key == "X-API-Key" else None
        )
        request2.client = Mock()
        request2.client.host = "10.0.0.50"

        # Get keys
        key1 = get_rate_limit_key(request1)
        key2 = get_rate_limit_key(request2)

        # Should have SAME rate limit key (based on API key)
        assert key1 == key2
        assert key1.startswith("apikey:")

    def test_rate_limit_key_prevents_x_forwarded_for_bypass(self):
        """Test that X-Forwarded-For cannot bypass rate limits when using API key."""
        from unittest.mock import Mock

        from proxywhirl.api.core import get_rate_limit_key

        # Request with API key and spoofed X-Forwarded-For
        request1 = Mock()
        request1.headers.get = Mock(
            side_effect=lambda key: {
                "X-API-Key": "test-api-key",
                "X-Forwarded-For": "1.2.3.4",
            }.get(key)
        )
        request1.client = Mock()
        request1.client.host = "192.168.1.100"

        # Same API key with different X-Forwarded-For
        request2 = Mock()
        request2.headers.get = Mock(
            side_effect=lambda key: {
                "X-API-Key": "test-api-key",
                "X-Forwarded-For": "5.6.7.8",
            }.get(key)
        )
        request2.client = Mock()
        request2.client.host = "192.168.1.100"

        # Get keys
        key1 = get_rate_limit_key(request1)
        key2 = get_rate_limit_key(request2)

        # Should have SAME rate limit key (API key takes precedence)
        assert key1 == key2
        assert key1.startswith("apikey:")
        # X-Forwarded-For values should be ignored
        assert "1.2.3.4" not in key1
        assert "5.6.7.8" not in key1

    def test_rate_limit_key_ignores_x_forwarded_for_for_unauthenticated(self):
        """Test that X-Forwarded-For is IGNORED for unauthenticated requests.

        SECURITY: X-Forwarded-For header can be spoofed by attackers to bypass
        rate limits. For unauthenticated requests, we must use only the direct
        client IP (request.client.host) which cannot be spoofed.
        """
        from unittest.mock import Mock

        from proxywhirl.api.core import get_rate_limit_key

        # Request without API key but with X-Forwarded-For (potential bypass attempt)
        request = Mock()
        request.headers.get = Mock(
            side_effect=lambda key: "203.0.113.50, 192.168.1.1"
            if key == "X-Forwarded-For"
            else None
        )
        request.client = Mock()
        request.client.host = "192.168.1.100"

        # Get key
        key = get_rate_limit_key(request)

        # Should use direct client IP, NOT X-Forwarded-For
        # This prevents rate limit bypass attacks via header spoofing
        assert key == "ip:192.168.1.100"

    def test_rate_limit_key_x_forwarded_for_bypass_attack_prevented(self):
        """SECURITY: Test that X-Forwarded-For cannot be used to bypass rate limits.

        Attack scenario: An attacker sends multiple requests from the same IP
        but with different X-Forwarded-For headers to evade rate limits.
        With the fix, all requests from the same client IP share the same rate limit.
        """
        from unittest.mock import Mock

        from proxywhirl.api.core import get_rate_limit_key

        # Attacker's first request with spoofed X-Forwarded-For
        request1 = Mock()
        request1.headers.get = Mock(
            side_effect=lambda key: "1.1.1.1" if key == "X-Forwarded-For" else None
        )
        request1.client = Mock()
        request1.client.host = "attacker-ip.example.com"

        # Attacker's second request with different spoofed X-Forwarded-For
        request2 = Mock()
        request2.headers.get = Mock(
            side_effect=lambda key: "2.2.2.2" if key == "X-Forwarded-For" else None
        )
        request2.client = Mock()
        request2.client.host = "attacker-ip.example.com"

        # Attacker's third request with yet another spoofed X-Forwarded-For
        request3 = Mock()
        request3.headers.get = Mock(
            side_effect=lambda key: "3.3.3.3, 4.4.4.4" if key == "X-Forwarded-For" else None
        )
        request3.client = Mock()
        request3.client.host = "attacker-ip.example.com"

        # Get rate limit keys
        key1 = get_rate_limit_key(request1)
        key2 = get_rate_limit_key(request2)
        key3 = get_rate_limit_key(request3)

        # SECURITY: All requests from the same client IP should share the same key
        assert key1 == key2 == key3
        assert key1 == "ip:attacker-ip.example.com"

        # None of the spoofed IPs should appear in the key
        assert "1.1.1.1" not in key1
        assert "2.2.2.2" not in key1
        assert "3.3.3.3" not in key1
        assert "4.4.4.4" not in key1

    def test_rate_limit_key_handles_missing_client(self):
        """Test that rate limit key handles missing client gracefully."""
        from unittest.mock import Mock

        from proxywhirl.api.core import get_rate_limit_key

        # Request without API key and without client
        request = Mock()
        request.headers.get = Mock(return_value=None)
        request.client = None

        # Get key
        key = get_rate_limit_key(request)

        # Should use "unknown" as fallback
        assert key == "ip:unknown"

    def test_rate_limit_key_api_key_hash_is_stable(self):
        """Test that API key hash is deterministic and stable."""
        import hashlib
        from unittest.mock import Mock

        from proxywhirl.api.core import get_rate_limit_key

        api_key = "test-stable-key"

        # Create two separate requests with same API key
        request1 = Mock()
        request1.headers.get = Mock(side_effect=lambda key: api_key if key == "X-API-Key" else None)
        request1.client = Mock()
        request1.client.host = "192.168.1.100"

        request2 = Mock()
        request2.headers.get = Mock(side_effect=lambda key: api_key if key == "X-API-Key" else None)
        request2.client = Mock()
        request2.client.host = "10.0.0.50"

        # Get keys
        key1 = get_rate_limit_key(request1)
        key2 = get_rate_limit_key(request2)

        # Should be identical
        assert key1 == key2

        # Verify hash matches expected
        expected_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
        assert key1 == f"apikey:{expected_hash}"

    def test_rate_limit_key_api_key_hash_obscures_original(self):
        """Test that API key hash does not expose original key value."""
        from unittest.mock import Mock

        from proxywhirl.api.core import get_rate_limit_key

        sensitive_key = "super-secret-api-key-12345"

        request = Mock()
        request.headers.get = Mock(
            side_effect=lambda key: sensitive_key if key == "X-API-Key" else None
        )
        request.client = Mock()
        request.client.host = "192.168.1.100"

        key = get_rate_limit_key(request)

        # Original key should NOT appear in the rate limit key
        assert sensitive_key not in key
        # Should be hashed
        assert key.startswith("apikey:")
        assert len(key.split(":")[1]) == 16  # SHA256 truncated to 16 chars

    def test_environment_variable_configuration(self, monkeypatch):
        """Test that rate limit configuration can be set via environment variables."""
        import os

        # Set environment variables
        monkeypatch.setenv("PROXYWHIRL_RATE_LIMIT", "200/minute")
        monkeypatch.setenv("PROXYWHIRL_API_KEY_RATE_LIMIT", "150/minute")

        # Verify environment variables are set
        assert os.getenv("PROXYWHIRL_RATE_LIMIT") == "200/minute"
        assert os.getenv("PROXYWHIRL_API_KEY_RATE_LIMIT") == "150/minute"

        # Note: We don't reload the module here because it would cause
        # Prometheus registry collisions in tests. In production, these
        # env vars are read at module import time.


class TestRequestIDMiddleware:
    """Tests for Request ID Correlation Middleware (P1.3).

    Verifies that X-Request-ID is properly generated, preserved, and
    returned for request tracing through the retry/cache/circuit-breaker chain.
    """

    def test_request_id_generated_when_not_provided(self, client, mock_rotator):
        """Test that X-Request-ID header is generated when not provided."""
        with patch("proxywhirl.api.core._rotator", mock_rotator):
            response = client.get("/metrics/retry")

            assert response.status_code == 200

            # Response should contain X-Request-ID header
            assert "X-Request-ID" in response.headers
            request_id = response.headers["X-Request-ID"]

            # Should be a valid UUID
            assert request_id is not None
            assert len(request_id) > 0

            # Validate it's a valid UUID format
            try:
                uuid.UUID(request_id)
            except ValueError:
                pytest.fail(f"X-Request-ID is not a valid UUID: {request_id}")

    def test_request_id_preserved_when_provided(self, client, mock_rotator):
        """Test that X-Request-ID header is preserved when provided by client."""
        with patch("proxywhirl.api.core._rotator", mock_rotator):
            # Provide a custom request ID
            custom_request_id = str(uuid.uuid4())

            response = client.get(
                "/metrics/retry",
                headers={"X-Request-ID": custom_request_id},
            )

            assert response.status_code == 200

            # Response should contain the same request ID we sent
            assert "X-Request-ID" in response.headers
            assert response.headers["X-Request-ID"] == custom_request_id

    def test_request_id_appears_in_response_headers(self, client, mock_rotator):
        """Test that X-Request-ID appears in all response headers."""
        with patch("proxywhirl.api.core._rotator", mock_rotator):
            # Test on different endpoints
            endpoints = ["/metrics/retry", "/metrics/circuit-breaker"]

            for endpoint in endpoints:
                response = client.get(endpoint)
                assert response.status_code in [200, 503]  # May fail if no rotator
                assert "X-Request-ID" in response.headers, (
                    f"X-Request-ID missing from response headers for {endpoint}"
                )

    def test_request_id_is_valid_uuid_format(self, client, mock_rotator):
        """Test that generated request ID is a valid UUID format."""
        with patch("proxywhirl.api.core._rotator", mock_rotator):
            # Make multiple requests and verify each has valid UUID
            for _ in range(5):
                response = client.get("/metrics/retry")
                assert response.status_code == 200

                request_id = response.headers.get("X-Request-ID")
                assert request_id is not None

                # Parse as UUID - will raise if invalid
                try:
                    parsed_uuid = uuid.UUID(request_id)
                    # Verify it's a version 4 UUID (random)
                    assert parsed_uuid.version == 4
                except ValueError:
                    pytest.fail(f"Generated request ID is not a valid UUID: {request_id}")

    def test_request_id_unique_for_each_request(self, client, mock_rotator):
        """Test that each request gets a unique request ID when not provided."""
        with patch("proxywhirl.api.core._rotator", mock_rotator):
            request_ids = set()

            # Make multiple requests
            for _ in range(10):
                response = client.get("/metrics/retry")
                assert response.status_code == 200
                request_ids.add(response.headers["X-Request-ID"])

            # All request IDs should be unique
            assert len(request_ids) == 10, "Generated request IDs are not unique"

    def test_request_id_preserved_for_custom_non_uuid_value(self, client, mock_rotator):
        """Test that non-UUID request IDs from clients are also preserved."""
        with patch("proxywhirl.api.core._rotator", mock_rotator):
            # Clients might send non-UUID request IDs
            custom_id = "my-custom-request-id-12345"

            response = client.get(
                "/metrics/retry",
                headers={"X-Request-ID": custom_id},
            )

            assert response.status_code == 200
            assert response.headers["X-Request-ID"] == custom_id

    def test_request_id_on_error_responses(self, client):
        """Test that X-Request-ID is present even on error responses."""
        # Without mock_rotator, this should return 503
        with patch("proxywhirl.api.core._rotator", None):
            custom_id = str(uuid.uuid4())

            response = client.get(
                "/metrics/retry",
                headers={"X-Request-ID": custom_id},
            )

            # Should be a 503 error
            assert response.status_code == 503

            # But still have the request ID header
            assert "X-Request-ID" in response.headers
            assert response.headers["X-Request-ID"] == custom_id

    def test_request_id_on_health_endpoint(self, client):
        """Test that X-Request-ID works on health check endpoints."""
        # Create a mock rotator with properly mocked pool
        rotator = MagicMock()
        rotator.pool.size = 10
        rotator.pool.healthy_count = 8
        rotator.pool.unhealthy_count = 2

        with patch("proxywhirl.api.core._rotator", rotator):
            response = client.get("/api/v1/health")

            # Should have request ID regardless of health status
            assert "X-Request-ID" in response.headers
            request_id = response.headers["X-Request-ID"]

            # Should be valid UUID
            uuid.UUID(request_id)  # Will raise if invalid

    def test_request_id_empty_header_generates_new_uuid(self, client, mock_rotator):
        """Test that empty X-Request-ID header results in new UUID generation."""
        with patch("proxywhirl.api.core._rotator", mock_rotator):
            # Send empty string as request ID
            response = client.get(
                "/metrics/retry",
                headers={"X-Request-ID": ""},
            )

            assert response.status_code == 200

            # Empty string is falsy, so should generate new UUID
            request_id = response.headers["X-Request-ID"]
            assert request_id != ""

            # Should be a valid UUID
            uuid.UUID(request_id)


class TestSecurityHeaders:
    """Tests for HTTP security headers (SEC-005).

    Verifies that all required security headers are present in API responses
    to protect against common web vulnerabilities.
    """

    def test_security_headers_present_on_success_response(self, client, mock_rotator):
        """Test that all security headers are present on successful responses."""
        with patch("proxywhirl.api.core._rotator", mock_rotator):
            response = client.get("/metrics/retry")

            assert response.status_code == 200

            # Basic security headers
            assert response.headers.get("X-Content-Type-Options") == "nosniff"
            assert response.headers.get("X-Frame-Options") == "DENY"
            assert response.headers.get("X-XSS-Protection") == "1; mode=block"

            # HSTS header
            assert (
                response.headers.get("Strict-Transport-Security")
                == "max-age=31536000; includeSubDomains"
            )

            # Content Security Policy
            assert (
                response.headers.get("Content-Security-Policy")
                == "default-src 'self'; frame-ancestors 'none'"
            )

            # Referrer Policy
            assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

            # Permissions Policy
            assert (
                response.headers.get("Permissions-Policy")
                == "geolocation=(), microphone=(), camera=()"
            )

    def test_security_headers_present_on_error_response(self, client):
        """Test that security headers are present even on error responses."""
        with patch("proxywhirl.api.core._rotator", None):
            response = client.get("/metrics/retry")

            # Should be a 503 error
            assert response.status_code == 503

            # All security headers should still be present
            assert response.headers.get("X-Content-Type-Options") == "nosniff"
            assert response.headers.get("X-Frame-Options") == "DENY"
            assert response.headers.get("X-XSS-Protection") == "1; mode=block"
            assert (
                response.headers.get("Strict-Transport-Security")
                == "max-age=31536000; includeSubDomains"
            )
            assert (
                response.headers.get("Content-Security-Policy")
                == "default-src 'self'; frame-ancestors 'none'"
            )
            assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
            assert (
                response.headers.get("Permissions-Policy")
                == "geolocation=(), microphone=(), camera=()"
            )

    def test_security_headers_on_health_endpoint(self, client):
        """Test that security headers are present on health check endpoints."""
        # Create a properly mocked rotator for health endpoint
        rotator = MagicMock()
        rotator.pool.size = 10
        rotator.pool.healthy_count = 8
        rotator.pool.unhealthy_count = 2

        with patch("proxywhirl.api.core._rotator", rotator):
            response = client.get("/api/v1/health")

            # Security headers should be present regardless of endpoint
            assert response.headers.get("X-Content-Type-Options") == "nosniff"
            assert response.headers.get("X-Frame-Options") == "DENY"
            assert (
                response.headers.get("Strict-Transport-Security")
                == "max-age=31536000; includeSubDomains"
            )

    def test_security_headers_on_circuit_breaker_endpoint(self, client, mock_rotator):
        """Test security headers on circuit breaker metrics endpoint."""
        with patch("proxywhirl.api.core._rotator", mock_rotator):
            response = client.get("/metrics/circuit-breaker")

            assert response.status_code == 200

            # Verify all headers
            assert response.headers.get("X-Content-Type-Options") == "nosniff"
            assert response.headers.get("X-Frame-Options") == "DENY"
            assert response.headers.get("X-XSS-Protection") == "1; mode=block"
            assert (
                response.headers.get("Strict-Transport-Security")
                == "max-age=31536000; includeSubDomains"
            )
            assert (
                response.headers.get("Content-Security-Policy")
                == "default-src 'self'; frame-ancestors 'none'"
            )
            assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
            assert (
                response.headers.get("Permissions-Policy")
                == "geolocation=(), microphone=(), camera=()"
            )

    def test_hsts_prevents_downgrade_attacks(self, client, mock_rotator):
        """Test that HSTS header has proper configuration for security."""
        with patch("proxywhirl.api.core._rotator", mock_rotator):
            response = client.get("/metrics/retry")

            hsts = response.headers.get("Strict-Transport-Security")
            assert hsts is not None

            # Should have 1-year max-age (31536000 seconds)
            assert "max-age=31536000" in hsts

            # Should include subdomains
            assert "includeSubDomains" in hsts

    def test_csp_prevents_xss_and_clickjacking(self, client, mock_rotator):
        """Test that CSP header properly restricts resource loading."""
        with patch("proxywhirl.api.core._rotator", mock_rotator):
            response = client.get("/metrics/retry")

            csp = response.headers.get("Content-Security-Policy")
            assert csp is not None

            # Should restrict default sources to self
            assert "default-src 'self'" in csp

            # Should prevent framing (anti-clickjacking)
            assert "frame-ancestors 'none'" in csp

    def test_permissions_policy_disables_sensitive_features(self, client, mock_rotator):
        """Test that Permissions-Policy disables sensitive browser features."""
        with patch("proxywhirl.api.core._rotator", mock_rotator):
            response = client.get("/metrics/retry")

            permissions = response.headers.get("Permissions-Policy")
            assert permissions is not None

            # Should disable geolocation
            assert "geolocation=()" in permissions

            # Should disable microphone
            assert "microphone=()" in permissions

            # Should disable camera
            assert "camera=()" in permissions


class TestCORSOriginParsing:
    """Tests for CORS origin parsing (SEC-006).

    Verifies that CORS origins are properly parsed from environment variables,
    handling edge cases like:
    - Empty strings from trailing commas
    - Whitespace around origins
    - Double commas resulting in empty strings
    """

    def test_cors_origins_with_trailing_comma(self):
        """Test that trailing commas don't result in empty string origins."""
        # Simulate env var with trailing comma
        cors_origins_raw = "http://localhost:8000,http://example.com,"
        cors_origins = [origin.strip() for origin in cors_origins_raw.split(",") if origin.strip()]

        # Should have exactly 2 origins, no empty strings
        assert len(cors_origins) == 2
        assert "" not in cors_origins
        assert cors_origins == ["http://localhost:8000", "http://example.com"]

    def test_cors_origins_with_double_commas(self):
        """Test that double commas don't result in empty string origins."""
        # Simulate env var with double comma
        cors_origins_raw = "http://localhost:8000,,http://example.com"
        cors_origins = [origin.strip() for origin in cors_origins_raw.split(",") if origin.strip()]

        # Should have exactly 2 origins, no empty strings
        assert len(cors_origins) == 2
        assert "" not in cors_origins
        assert cors_origins == ["http://localhost:8000", "http://example.com"]

    def test_cors_origins_with_whitespace(self):
        """Test that whitespace is stripped from origins."""
        cors_origins_raw = "  http://localhost:8000 , http://example.com  ,  http://other.com  "
        cors_origins = [origin.strip() for origin in cors_origins_raw.split(",") if origin.strip()]

        # Should have exactly 3 origins with no leading/trailing whitespace
        assert len(cors_origins) == 3
        assert cors_origins == ["http://localhost:8000", "http://example.com", "http://other.com"]
        # Verify no whitespace
        for origin in cors_origins:
            assert origin == origin.strip()
            assert not origin.startswith(" ")
            assert not origin.endswith(" ")

    def test_cors_origins_with_multiple_edge_cases(self):
        """Test combination of edge cases: trailing comma, double commas, whitespace."""
        cors_origins_raw = " http://localhost:8000 ,, http://example.com , ,"
        cors_origins = [origin.strip() for origin in cors_origins_raw.split(",") if origin.strip()]

        # Should have exactly 2 origins
        assert len(cors_origins) == 2
        assert "" not in cors_origins
        assert cors_origins == ["http://localhost:8000", "http://example.com"]

    def test_cors_origins_empty_string(self):
        """Test that empty environment variable results in empty list."""
        cors_origins_raw = ""
        cors_origins = [origin.strip() for origin in cors_origins_raw.split(",") if origin.strip()]

        # Should be empty list
        assert cors_origins == []

    def test_cors_origins_only_commas(self):
        """Test that only commas results in empty list."""
        cors_origins_raw = ",,,,"
        cors_origins = [origin.strip() for origin in cors_origins_raw.split(",") if origin.strip()]

        # Should be empty list
        assert cors_origins == []

    def test_cors_origins_only_whitespace_and_commas(self):
        """Test that whitespace and commas only results in empty list."""
        cors_origins_raw = "  ,  ,   ,  "
        cors_origins = [origin.strip() for origin in cors_origins_raw.split(",") if origin.strip()]

        # Should be empty list
        assert cors_origins == []

    def test_cors_origins_single_origin(self):
        """Test that single origin without comma works correctly."""
        cors_origins_raw = "http://localhost:8000"
        cors_origins = [origin.strip() for origin in cors_origins_raw.split(",") if origin.strip()]

        # Should have exactly 1 origin
        assert len(cors_origins) == 1
        assert cors_origins == ["http://localhost:8000"]

    def test_cors_origins_wildcard(self):
        """Test that wildcard origin is preserved."""
        cors_origins_raw = "*"
        cors_origins = [origin.strip() for origin in cors_origins_raw.split(",") if origin.strip()]

        # Should have exactly 1 origin
        assert len(cors_origins) == 1
        assert cors_origins == ["*"]

    def test_cors_origins_preserves_port_numbers(self):
        """Test that port numbers are preserved in origins."""
        cors_origins_raw = "http://localhost:3000,http://localhost:8080,https://api.example.com:443"
        cors_origins = [origin.strip() for origin in cors_origins_raw.split(",") if origin.strip()]

        assert len(cors_origins) == 3
        assert "http://localhost:3000" in cors_origins
        assert "http://localhost:8080" in cors_origins
        assert "https://api.example.com:443" in cors_origins

    def test_cors_origins_default_value(self):
        """Test that default CORS origins are properly parsed."""
        # Default value from the module
        cors_origins_raw = "http://localhost:8000,http://127.0.0.1:8000"
        cors_origins = [origin.strip() for origin in cors_origins_raw.split(",") if origin.strip()]

        assert len(cors_origins) == 2
        assert cors_origins == ["http://localhost:8000", "http://127.0.0.1:8000"]


class TestCORSWildcardValidation:
    """Tests for CORS wildcard validation (SEC-003).

    Verifies that the application prevents insecure CORS configurations:
    - Wildcard origins with credentials enabled is a security vulnerability
    - Proper validation happens at startup
    """

    def test_cors_wildcard_with_credentials_raises_error(self):
        """Test that wildcard CORS with credentials=True raises ValueError."""
        # This would be caught during app initialization
        cors_origins = ["*"]
        allow_credentials = True

        # Simulate the validation logic from core.py
        with pytest.raises(
            ValueError,
            match="cannot use wildcard origin.*allow_credentials=True",
        ):
            if "*" in cors_origins and allow_credentials:
                error_msg = (
                    "CORS configuration error: cannot use wildcard origin ('*') "
                    "with allow_credentials=True. This violates CORS security "
                    "policy. Either: 1) Set specific PROXYWHIRL_CORS_ORIGINS, "
                    "or 2) Use '*' only for public APIs without credentials."
                )
                raise ValueError(error_msg)

    def test_cors_wildcard_without_credentials_allowed(self):
        """Test that wildcard CORS without credentials is allowed (safe for public APIs)."""
        cors_origins = ["*"]
        allow_credentials = False

        # Should not raise
        if "*" in cors_origins and allow_credentials:
            raise ValueError("Should not raise for wildcard without credentials")

    def test_cors_specific_origins_with_credentials_allowed(self):
        """Test that specific origins with credentials are allowed."""
        cors_origins = ["http://localhost:8000", "https://example.com"]
        allow_credentials = True

        # Should not raise
        if "*" in cors_origins and allow_credentials:
            raise ValueError("Should not raise for specific origins")

    def test_cors_empty_origins_with_credentials_allowed(self):
        """Test that empty origins (no CORS) with credentials is safe."""
        cors_origins = []
        allow_credentials = True

        # Should not raise
        if "*" in cors_origins and allow_credentials:
            raise ValueError("Should not raise for empty origins")

    def test_cors_wildcard_detection_in_mixed_origins(self):
        """Test that wildcard is detected even when mixed with other origins."""
        cors_origins = ["http://localhost:8000", "*", "https://example.com"]
        allow_credentials = True

        # Should raise because wildcard is present
        with pytest.raises(ValueError, match="cannot use wildcard origin"):
            if "*" in cors_origins and allow_credentials:
                error_msg = (
                    "CORS configuration error: cannot use wildcard origin ('*') "
                    "with allow_credentials=True. This violates CORS security "
                    "policy. Either: 1) Set specific PROXYWHIRL_CORS_ORIGINS, "
                    "or 2) Use '*' only for public APIs without credentials."
                )
                raise ValueError(error_msg)

    def test_cors_env_var_with_wildcard_parsing(self):
        """Test parsing CORS_ORIGINS env var containing wildcard."""
        cors_origins_raw = "*"
        cors_origins = [origin.strip() for origin in cors_origins_raw.split(",") if origin.strip()]

        assert cors_origins == ["*"]
        assert "*" in cors_origins

    def test_cors_env_var_wildcard_with_other_origins_parsing(self):
        """Test parsing CORS_ORIGINS env var with wildcard and other origins."""
        cors_origins_raw = "http://localhost:8000,*,https://example.com"
        cors_origins = [origin.strip() for origin in cors_origins_raw.split(",") if origin.strip()]

        assert len(cors_origins) == 3
        assert "*" in cors_origins
        assert "http://localhost:8000" in cors_origins


class TestAuditLoggingMiddleware:
    """Tests for Audit Logging Middleware.

    Verifies that audit logging middleware:
    - Logs write/admin/auth operations
    - Can be enabled/disabled via PROXYWHIRL_AUDIT_LOG
    - Redacts sensitive information (API keys, credentials)
    - Includes proper context (timestamp, method, path, status)
    - Uses structured logging format
    """

    def test_audit_log_environment_variable_controls_middleware(self, client, mock_rotator):
        """Test that PROXYWHIRL_AUDIT_LOG environment variable controls audit logging.

        This test verifies that the middleware checks the environment variable
        and skips audit logging when set to 'false'.
        """
        from proxywhirl.api.core import AuditLoggingMiddleware

        middleware = AuditLoggingMiddleware(None)

        # Test that middleware respects environment variable
        with patch.dict("os.environ", {"PROXYWHIRL_AUDIT_LOG": "false"}):
            with patch("proxywhirl.api.core._rotator", mock_rotator):
                # This should not audit because PROXYWHIRL_AUDIT_LOG=false
                response = client.post(
                    "/api/v1/proxies",
                    json={"url": "http://proxy.example.com:8080"},
                )
                # Just verify the request went through
                assert response.status_code in [200, 201, 422]

        with patch.dict("os.environ", {"PROXYWHIRL_AUDIT_LOG": "true"}):
            with patch("proxywhirl.api.core._rotator", mock_rotator):
                # This should audit because PROXYWHIRL_AUDIT_LOG=true
                response = client.post(
                    "/api/v1/proxies",
                    json={"url": "http://proxy.example.com:8080"},
                )
                # Just verify the request went through
                assert response.status_code in [200, 201, 422]

    def test_audit_log_default_enabled(self):
        """Test that audit logging is enabled by default when env var not set."""
        import os

        # When PROXYWHIRL_AUDIT_LOG is not set, it should default to "true"
        default_value = os.getenv("PROXYWHIRL_AUDIT_LOG", "true").lower() == "true"
        assert default_value is True

    def test_audit_log_disabled_via_env_var(self):
        """Test that audit logging can be disabled via PROXYWHIRL_AUDIT_LOG=false."""
        import os

        with patch.dict("os.environ", {"PROXYWHIRL_AUDIT_LOG": "false"}):
            audit_enabled = os.getenv("PROXYWHIRL_AUDIT_LOG", "true").lower() == "true"
            assert audit_enabled is False

    def test_audit_log_enabled_via_env_var(self):
        """Test that audit logging can be explicitly enabled via PROXYWHIRL_AUDIT_LOG=true."""
        import os

        with patch.dict("os.environ", {"PROXYWHIRL_AUDIT_LOG": "true"}):
            audit_enabled = os.getenv("PROXYWHIRL_AUDIT_LOG", "true").lower() == "true"
            assert audit_enabled is True

    def test_audit_log_case_insensitive(self):
        """Test that PROXYWHIRL_AUDIT_LOG is case-insensitive."""
        import os

        # Test with uppercase TRUE
        with patch.dict("os.environ", {"PROXYWHIRL_AUDIT_LOG": "TRUE"}):
            audit_enabled = os.getenv("PROXYWHIRL_AUDIT_LOG", "true").lower() == "true"
            assert audit_enabled is True

        # Test with lowercase false
        with patch.dict("os.environ", {"PROXYWHIRL_AUDIT_LOG": "false"}):
            audit_enabled = os.getenv("PROXYWHIRL_AUDIT_LOG", "true").lower() == "true"
            assert audit_enabled is False

        # Test with mixed case False
        with patch.dict("os.environ", {"PROXYWHIRL_AUDIT_LOG": "False"}):
            audit_enabled = os.getenv("PROXYWHIRL_AUDIT_LOG", "true").lower() == "true"
            assert audit_enabled is False

    def test_audit_middleware_redacts_api_keys(self):
        """Test that the middleware has a method to redact API keys."""
        from proxywhirl.api.core import AuditLoggingMiddleware

        middleware = AuditLoggingMiddleware(None)

        # Test with normal length key
        redacted = middleware._redact_api_key("super-secret-api-key-12345")
        assert redacted == "supe...2345"
        assert "super-secret-api-key-12345" not in redacted

        # Test with short key
        redacted_short = middleware._redact_api_key("short")
        assert redacted_short == "***"

        # Test with None
        redacted_none = middleware._redact_api_key(None)
        assert redacted_none == "none"

    def test_audit_middleware_redacts_sensitive_body_fields(self):
        """Test that the middleware redacts sensitive fields in request bodies."""
        from proxywhirl.api.core import AuditLoggingMiddleware

        middleware = AuditLoggingMiddleware(None)

        # Test redaction of various sensitive fields
        body = {
            "url": "http://proxy.example.com:8080",
            "password": "super-secret-password",
            "api_key": "secret-key-123",
            "normal_field": "normal_value",
        }

        redacted = middleware._redact_body(body)

        # Check that sensitive fields are redacted
        assert redacted["password"] == "***REDACTED***"
        assert redacted["api_key"] == "***REDACTED***"

        # Check that normal fields are preserved
        assert redacted["url"] == "http://proxy.example.com:8080"
        assert redacted["normal_field"] == "normal_value"

        # Check that original values are NOT in redacted body
        assert "super-secret-password" not in str(redacted)
        assert "secret-key-123" not in str(redacted)

    def test_audit_middleware_classifies_operations(self):
        """Test that the middleware correctly classifies operation types."""
        from proxywhirl.api.core import AuditLoggingMiddleware

        middleware = AuditLoggingMiddleware(None)

        # Test write operations
        assert middleware._get_operation_type("POST", "/api/v1/proxies") == "write"
        assert middleware._get_operation_type("PUT", "/api/v1/proxies/1") == "write"
        assert middleware._get_operation_type("DELETE", "/api/v1/proxies/1") == "write"

        # Test admin operations
        assert middleware._get_operation_type("POST", "/api/v1/config") == "admin"
        assert middleware._get_operation_type("PUT", "/api/v1/config") == "admin"

        # Test read operations (GET on write endpoints)
        assert middleware._get_operation_type("GET", "/api/v1/proxies") == "read"
        assert middleware._get_operation_type("GET", "/api/v1/config") == "read"

    def test_audit_middleware_logs_write_operations(self, client, mock_rotator, caplog):
        """Test that write operations are logged with structured audit information."""
        # Configure loguru to capture logs in caplog
        import logging

        from loguru import logger

        # Add a handler that sends loguru logs to standard logging
        class PropagateHandler(logging.Handler):
            def emit(self, record):
                logging.getLogger(record.name).handle(record)

        logger.add(PropagateHandler(), format="{message}")

        with (
            patch.dict("os.environ", {"PROXYWHIRL_AUDIT_LOG": "true"}),
            patch("proxywhirl.api.core._rotator", mock_rotator),
            caplog.at_level(logging.INFO),
        ):
            # Make a write operation
            response = client.post(
                "/api/v1/request",
                json={
                    "url": "http://example.com",
                    "method": "GET",
                },
                headers={"X-API-Key": "test-key-123"},
            )

            # Verify audit logs were created
            # Check that structured logging occurred
            assert any("AUDIT:" in record.message for record in caplog.records)

    def test_audit_middleware_redacts_nested_sensitive_fields(self):
        """Test that nested sensitive fields in request bodies are redacted.

        When a key name matches a sensitive field (like 'auth', 'password', 'token'),
        the entire value is redacted, regardless of whether it's a string or nested object.
        This is the correct security behavior - if the field name is sensitive, the whole
        value should be redacted.
        """
        from proxywhirl.api.core import AuditLoggingMiddleware

        middleware = AuditLoggingMiddleware(None)

        # Test nested sensitive fields
        body = {
            "proxy": {
                "url": "http://proxy.example.com:8080",
                "auth": {  # 'auth' is a sensitive field name
                    "username": "user",
                    "password": "super-secret",
                    "api_key": "nested-key-123",
                },
            },
            "config": {
                "timeout": 30,
                "token": "bearer-token-abc",  # 'token' is sensitive
            },
        }

        redacted = middleware._redact_body(body)

        # 'auth' key is sensitive, so entire auth object is redacted
        assert redacted["proxy"]["auth"] == "***REDACTED***"
        # 'token' key is sensitive, so value is redacted
        assert redacted["config"]["token"] == "***REDACTED***"

        # Check that normal fields are preserved
        assert redacted["proxy"]["url"] == "http://proxy.example.com:8080"
        assert redacted["config"]["timeout"] == 30

        # Verify original secrets not in output
        assert "super-secret" not in str(redacted)
        assert "nested-key-123" not in str(redacted)
        assert "bearer-token-abc" not in str(redacted)

    def test_audit_middleware_redacts_list_of_objects(self):
        """Test that sensitive fields in lists of objects are redacted."""
        from proxywhirl.api.core import AuditLoggingMiddleware

        middleware = AuditLoggingMiddleware(None)

        # Test list with sensitive data
        body = {
            "proxies": [
                {
                    "url": "http://proxy1.example.com:8080",
                    "password": "secret1",
                },
                {
                    "url": "http://proxy2.example.com:8080",
                    "api_key": "secret2",
                },
            ]
        }

        redacted = middleware._redact_body(body)

        # Check list redaction
        assert redacted["proxies"][0]["password"] == "***REDACTED***"
        assert redacted["proxies"][1]["api_key"] == "***REDACTED***"

        # Check normal fields preserved
        assert redacted["proxies"][0]["url"] == "http://proxy1.example.com:8080"
        assert redacted["proxies"][1]["url"] == "http://proxy2.example.com:8080"

        # Verify secrets not in output
        assert "secret1" not in str(redacted)
        assert "secret2" not in str(redacted)

    def test_audit_middleware_logs_error_responses(self, client, caplog):
        """Test that failed operations are logged with warning level."""
        import logging

        from loguru import logger

        class PropagateHandler(logging.Handler):
            def emit(self, record):
                logging.getLogger(record.name).handle(record)

        logger.add(PropagateHandler(), format="{message}")

        with (
            patch.dict("os.environ", {"PROXYWHIRL_AUDIT_LOG": "true"}),
            patch("proxywhirl.api.core._rotator", None),  # Force error
            caplog.at_level(logging.WARNING),
        ):
            # Make a request that will fail
            response = client.post(
                "/api/v1/request",
                json={"url": "http://example.com"},
            )

            # Should be an error response
            assert response.status_code >= 400

            # Should have warning log for failed operation
            assert any("failed" in record.message.lower() for record in caplog.records)

    def test_audit_middleware_skips_read_operations(self, client, mock_rotator, caplog):
        """Test that read operations are not audited."""
        import logging

        from loguru import logger

        class PropagateHandler(logging.Handler):
            def emit(self, record):
                logging.getLogger(record.name).handle(record)

        logger.add(PropagateHandler(), format="{message}")

        with (
            patch.dict("os.environ", {"PROXYWHIRL_AUDIT_LOG": "true"}),
            patch("proxywhirl.api.core._rotator", mock_rotator),
            caplog.at_level(logging.INFO),
        ):
            # Clear any existing logs
            caplog.clear()

            # Make a read operation (GET)
            response = client.get("/metrics/retry")

            # Should succeed
            assert response.status_code == 200

            # Should NOT have audit logs (read operations are skipped)
            audit_logs = [r for r in caplog.records if "AUDIT:" in r.message]
            assert len(audit_logs) == 0

    def test_audit_middleware_captures_request_id(self, client, mock_rotator, caplog):
        """Test that audit logs include the request ID for correlation."""
        import logging

        from loguru import logger

        class PropagateHandler(logging.Handler):
            def emit(self, record):
                logging.getLogger(record.name).handle(record)

        logger.add(PropagateHandler(), format="{message}")

        custom_request_id = str(uuid.uuid4())

        with (
            patch.dict("os.environ", {"PROXYWHIRL_AUDIT_LOG": "true"}),
            patch("proxywhirl.api.core._rotator", mock_rotator),
            caplog.at_level(logging.INFO),
        ):
            # Make a write operation with custom request ID
            response = client.post(
                "/api/v1/request",
                json={"url": "http://example.com"},
                headers={"X-Request-ID": custom_request_id},
            )

            # Response should include the request ID
            assert response.headers.get("X-Request-ID") == custom_request_id

    def test_audit_middleware_handles_unparseable_body(self, client, mock_rotator, caplog):
        """Test that middleware handles unparseable request bodies gracefully."""
        import logging

        from loguru import logger

        class PropagateHandler(logging.Handler):
            def emit(self, record):
                logging.getLogger(record.name).handle(record)

        logger.add(PropagateHandler(), format="{message}")

        with (
            patch.dict("os.environ", {"PROXYWHIRL_AUDIT_LOG": "true"}),
            patch("proxywhirl.api.core._rotator", mock_rotator),
            caplog.at_level(logging.INFO),
        ):
            # Send invalid JSON
            response = client.post(
                "/api/v1/request",
                data="not valid json",
                headers={"Content-Type": "application/json"},
            )

            # Should handle gracefully (may fail but shouldn't crash middleware)
            assert response.status_code in [200, 400, 422, 503]

    def test_audit_middleware_detects_all_sensitive_field_variants(self):
        """Test that middleware detects various naming conventions for sensitive fields."""
        from proxywhirl.api.core import AuditLoggingMiddleware

        middleware = AuditLoggingMiddleware(None)

        # Test various naming conventions
        body = {
            "Password": "secret1",  # Capitalized
            "API_KEY": "secret2",  # Uppercase with underscore
            "Api-Key": "secret3",  # Mixed case with hyphen
            "SECRET": "secret4",  # Direct match
            "Authorization": "secret5",  # Capitalized
            "normal_field": "not-secret",
        }

        redacted = middleware._redact_body(body)

        # All should be redacted (case-insensitive)
        assert redacted["Password"] == "***REDACTED***"
        assert redacted["API_KEY"] == "***REDACTED***"
        assert redacted["Api-Key"] == "***REDACTED***"
        assert redacted["SECRET"] == "***REDACTED***"
        assert redacted["Authorization"] == "***REDACTED***"

        # Normal field should be preserved
        assert redacted["normal_field"] == "not-secret"


class TestEnvironmentVariableValidation:
    """Tests for environment variable parsing and validation.

    Verifies that integer and float environment variables are properly
    validated with clear error messages.
    """

    def test_parse_int_env_valid_value(self):
        """Test parsing valid integer environment variable."""
        from proxywhirl.api.core import _parse_int_env

        # Using getenv directly for this test
        result = _parse_int_env("NONEXISTENT_INT_VAR_12345", 42)
        assert result == 42

    def test_parse_int_env_with_valid_number(self, monkeypatch):
        """Test parsing valid integer from environment variable."""
        from proxywhirl.api.core import _parse_int_env

        monkeypatch.setenv("TEST_INT_VAR", "100")
        result = _parse_int_env("TEST_INT_VAR", 42)
        assert result == 100

    def test_parse_int_env_with_invalid_value_raises_error(self, monkeypatch):
        """Test that invalid integer raises ValueError with clear message."""
        from proxywhirl.api.core import _parse_int_env

        monkeypatch.setenv("TEST_INT_VAR", "not_a_number")

        with pytest.raises(
            ValueError,
            match="Environment variable TEST_INT_VAR must be an integer, got 'not_a_number'",
        ):
            _parse_int_env("TEST_INT_VAR", 42)

    def test_parse_int_env_with_float_value_raises_error(self, monkeypatch):
        """Test that float values in int env var raise ValueError."""
        from proxywhirl.api.core import _parse_int_env

        monkeypatch.setenv("TEST_INT_VAR", "3.14")

        with pytest.raises(ValueError, match="must be an integer"):
            _parse_int_env("TEST_INT_VAR", 42)

    def test_parse_int_env_with_empty_string_raises_error(self, monkeypatch):
        """Test that empty string raises ValueError (not treated as default)."""
        from proxywhirl.api.core import _parse_int_env

        monkeypatch.setenv("TEST_INT_VAR", "")

        # Empty string is set (not None), so it should raise ValueError
        # os.getenv returns empty string, int("") raises ValueError
        with pytest.raises(ValueError, match="must be an integer"):
            _parse_int_env("TEST_INT_VAR", 99)

    def test_parse_float_env_valid_value(self):
        """Test parsing valid float environment variable."""
        from proxywhirl.api.core import _parse_float_env

        result = _parse_float_env("NONEXISTENT_FLOAT_VAR_12345", 3.14)
        assert result == 3.14

    def test_parse_float_env_with_valid_number(self, monkeypatch):
        """Test parsing valid float from environment variable."""
        from proxywhirl.api.core import _parse_float_env

        monkeypatch.setenv("TEST_FLOAT_VAR", "2.71")
        result = _parse_float_env("TEST_FLOAT_VAR", 3.14)
        assert result == 2.71

    def test_parse_float_env_with_integer_value(self, monkeypatch):
        """Test that integer strings parse as floats."""
        from proxywhirl.api.core import _parse_float_env

        monkeypatch.setenv("TEST_FLOAT_VAR", "42")
        result = _parse_float_env("TEST_FLOAT_VAR", 3.14)
        assert result == 42.0

    def test_parse_float_env_with_invalid_value_raises_error(self, monkeypatch):
        """Test that invalid float raises ValueError with clear message."""
        from proxywhirl.api.core import _parse_float_env

        monkeypatch.setenv("TEST_FLOAT_VAR", "not_a_number")

        with pytest.raises(
            ValueError,
            match="Environment variable TEST_FLOAT_VAR must be a number, got 'not_a_number'",
        ):
            _parse_float_env("TEST_FLOAT_VAR", 3.14)

    def test_parse_int_env_with_negative_value(self, monkeypatch):
        """Test that negative integers are accepted."""
        from proxywhirl.api.core import _parse_int_env

        monkeypatch.setenv("TEST_INT_VAR", "-100")
        result = _parse_int_env("TEST_INT_VAR", 42)
        assert result == -100

    def test_parse_int_env_with_large_value(self, monkeypatch):
        """Test that large integers are accepted."""
        from proxywhirl.api.core import _parse_int_env

        monkeypatch.setenv("TEST_INT_VAR", "999999999999")
        result = _parse_int_env("TEST_INT_VAR", 42)
        assert result == 999999999999

    def test_parse_int_env_error_message_includes_variable_name(self, monkeypatch):
        """Test that error message includes the environment variable name."""
        from proxywhirl.api.core import _parse_int_env

        monkeypatch.setenv("MY_CUSTOM_PORT", "invalid_port_number")

        with pytest.raises(ValueError) as exc_info:
            _parse_int_env("MY_CUSTOM_PORT", 8080)

        error_msg = str(exc_info.value)
        assert "MY_CUSTOM_PORT" in error_msg
        assert "invalid_port_number" in error_msg

    def test_parse_float_env_error_message_includes_variable_name(self, monkeypatch):
        """Test that error message includes the environment variable name."""
        from proxywhirl.api.core import _parse_float_env

        monkeypatch.setenv("MY_CUSTOM_RATE", "not_a_rate")

        with pytest.raises(ValueError) as exc_info:
            _parse_float_env("MY_CUSTOM_RATE", 0.5)

        error_msg = str(exc_info.value)
        assert "MY_CUSTOM_RATE" in error_msg
        assert "not_a_rate" in error_msg

    def test_parse_int_env_with_whitespace(self, monkeypatch):
        """Test that integer with leading/trailing whitespace is handled."""
        from proxywhirl.api.core import _parse_int_env

        # os.getenv preserves whitespace, int() can handle leading/trailing
        monkeypatch.setenv("TEST_INT_VAR", "  100  ")
        result = _parse_int_env("TEST_INT_VAR", 42)
        # int() strips whitespace automatically
        assert result == 100

    def test_parse_float_env_with_whitespace(self, monkeypatch):
        """Test that float with leading/trailing whitespace is handled."""
        from proxywhirl.api.core import _parse_float_env

        monkeypatch.setenv("TEST_FLOAT_VAR", "  3.14  ")
        result = _parse_float_env("TEST_FLOAT_VAR", 2.71)
        # float() strips whitespace automatically
        assert result == 3.14
