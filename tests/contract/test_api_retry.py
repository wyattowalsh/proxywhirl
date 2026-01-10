"""Contract tests for retry/failover API endpoints (Retry & Failover).

Tests the API contract for all 13 retry/failover endpoints:
1. GET /api/v1/retry/policy - Get global retry policy
2. PUT /api/v1/retry/policy - Update global retry policy
3. GET /api/v1/circuit-breakers - List all circuit breaker states
4. GET /api/v1/circuit-breakers/metrics - Get circuit breaker metrics
5. GET /api/v1/circuit-breakers/{proxy_id} - Get circuit breaker state for specific proxy
6. POST /api/v1/circuit-breakers/{proxy_id}/reset - Manually reset circuit breaker
7. GET /api/v1/metrics/retries - Get retry metrics summary
8. GET /api/v1/metrics/retries/timeseries - Get time-series retry data
9. GET /api/v1/metrics/retries/by-proxy - Get per-proxy retry statistics
10. GET /metrics/retry - Get retry statistics (JSON/Prometheus)
11. GET /metrics/circuit-breaker - Get circuit breaker metrics (JSON/Prometheus)
"""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from proxywhirl.api_models import (
    CircuitBreakerEventResponse,
    CircuitBreakerResponse,
    ProxyRetryStats,
    ProxyRetryStatsResponse,
    RetryMetricsResponse,
    RetryPolicyRequest,
    RetryPolicyResponse,
    TimeSeriesDataPoint,
    TimeSeriesResponse,
)


# T301: Contract test for GET /api/v1/retry/policy
class TestGetRetryPolicyContract:
    """Test RetryPolicyResponse schema for getting retry policy."""

    def test_retry_policy_response_schema_valid(self):
        """Test RetryPolicyResponse accepts valid policy data."""
        # Arrange & Act
        response = RetryPolicyResponse(
            max_attempts=5,
            backoff_strategy="exponential",
            base_delay=1.5,
            multiplier=2.0,
            max_backoff_delay=30.0,
            jitter=True,
            retry_status_codes=[502, 503, 504],
            timeout=60.0,
            retry_non_idempotent=False,
        )

        # Assert
        assert response.max_attempts == 5
        assert response.backoff_strategy == "exponential"
        assert response.base_delay == 1.5
        assert response.multiplier == 2.0
        assert response.max_backoff_delay == 30.0
        assert response.jitter is True
        assert response.retry_status_codes == [502, 503, 504]
        assert response.timeout == 60.0
        assert response.retry_non_idempotent is False
        assert isinstance(response.updated_at, datetime)

    def test_retry_policy_response_schema_null_timeout(self):
        """Test RetryPolicyResponse accepts None for optional timeout."""
        # Arrange & Act
        response = RetryPolicyResponse(
            max_attempts=3,
            backoff_strategy="linear",
            base_delay=1.0,
            multiplier=1.5,
            max_backoff_delay=10.0,
            jitter=False,
            retry_status_codes=[500, 502, 503],
            timeout=None,  # Optional field
            retry_non_idempotent=False,
        )

        # Assert
        assert response.timeout is None


# T302: Contract test for PUT /api/v1/retry/policy
class TestUpdateRetryPolicyContract:
    """Test RetryPolicyRequest schema for updating retry policy."""

    def test_retry_policy_request_schema_valid_full(self):
        """Test RetryPolicyRequest with all fields."""
        # Arrange & Act
        request = RetryPolicyRequest(
            max_attempts=5,
            backoff_strategy="exponential",
            base_delay=2.0,
            multiplier=3.0,
            max_backoff_delay=60.0,
            jitter=True,
            retry_status_codes=[502, 503],
            timeout=120.0,
            retry_non_idempotent=True,
        )

        # Assert
        assert request.max_attempts == 5
        assert request.backoff_strategy == "exponential"
        assert request.base_delay == 2.0
        assert request.multiplier == 3.0
        assert request.max_backoff_delay == 60.0
        assert request.jitter is True
        assert request.retry_status_codes == [502, 503]
        assert request.timeout == 120.0
        assert request.retry_non_idempotent is True

    def test_retry_policy_request_schema_partial(self):
        """Test RetryPolicyRequest with only some fields (partial update)."""
        # Arrange & Act
        request = RetryPolicyRequest(
            max_attempts=10,
            backoff_strategy="linear",
        )

        # Assert
        assert request.max_attempts == 10
        assert request.backoff_strategy == "linear"
        assert request.base_delay is None
        assert request.multiplier is None
        assert request.max_backoff_delay is None
        assert request.jitter is None

    def test_retry_policy_request_schema_empty(self):
        """Test RetryPolicyRequest with no fields (all optional)."""
        # Arrange & Act
        request = RetryPolicyRequest()

        # Assert
        assert request.max_attempts is None
        assert request.backoff_strategy is None
        assert request.base_delay is None

    def test_retry_policy_request_schema_invalid_max_attempts(self):
        """Test RetryPolicyRequest rejects invalid max_attempts."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            RetryPolicyRequest(max_attempts=0)  # Must be >= 1

        errors = exc_info.value.errors()
        assert any("greater_than_equal" in str(e["type"]) for e in errors)

    def test_retry_policy_request_schema_invalid_max_attempts_too_high(self):
        """Test RetryPolicyRequest rejects max_attempts > 10."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            RetryPolicyRequest(max_attempts=11)  # Must be <= 10

        errors = exc_info.value.errors()
        assert any("less_than_equal" in str(e["type"]) for e in errors)

    def test_retry_policy_request_schema_invalid_base_delay(self):
        """Test RetryPolicyRequest rejects invalid base_delay."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            RetryPolicyRequest(base_delay=0.0)  # Must be > 0

        errors = exc_info.value.errors()
        assert any("greater_than" in str(e["type"]) for e in errors)

    def test_retry_policy_request_schema_invalid_multiplier(self):
        """Test RetryPolicyRequest rejects invalid multiplier."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            RetryPolicyRequest(multiplier=1.0)  # Must be > 1

        errors = exc_info.value.errors()
        assert any("greater_than" in str(e["type"]) for e in errors)


# T303: Contract test for GET /api/v1/circuit-breakers
class TestListCircuitBreakersContract:
    """Test CircuitBreakerResponse schema for listing circuit breakers."""

    def test_circuit_breaker_response_schema_valid(self):
        """Test CircuitBreakerResponse accepts valid circuit breaker data."""
        # Arrange & Act
        response = CircuitBreakerResponse(
            proxy_id="proxy1.example.com:8080",
            state="closed",
            failure_count=2,
            failure_threshold=5,
            window_duration=60.0,
            timeout_duration=30.0,
            next_test_time=None,
            last_state_change=datetime.now(timezone.utc),
        )

        # Assert
        assert response.proxy_id == "proxy1.example.com:8080"
        assert response.state == "closed"
        assert response.failure_count == 2
        assert response.failure_threshold == 5
        assert response.window_duration == 60.0
        assert response.timeout_duration == 30.0
        assert response.next_test_time is None
        assert isinstance(response.last_state_change, datetime)

    def test_circuit_breaker_response_schema_open_state(self):
        """Test CircuitBreakerResponse with open state and next_test_time."""
        # Arrange
        next_test = datetime.now(timezone.utc)

        # Act
        response = CircuitBreakerResponse(
            proxy_id="proxy2.example.com:8080",
            state="open",
            failure_count=5,
            failure_threshold=5,
            window_duration=60.0,
            timeout_duration=30.0,
            next_test_time=next_test,
            last_state_change=datetime.now(timezone.utc),
        )

        # Assert
        assert response.state == "open"
        assert response.failure_count == 5
        assert response.next_test_time == next_test

    def test_circuit_breaker_response_schema_half_open_state(self):
        """Test CircuitBreakerResponse with half_open state."""
        # Arrange & Act
        response = CircuitBreakerResponse(
            proxy_id="proxy3.example.com:8080",
            state="half_open",
            failure_count=0,
            failure_threshold=5,
            window_duration=60.0,
            timeout_duration=30.0,
            next_test_time=None,
            last_state_change=datetime.now(timezone.utc),
        )

        # Assert
        assert response.state == "half_open"
        assert response.failure_count == 0


# T304: Contract test for GET /api/v1/circuit-breakers/metrics
class TestCircuitBreakerMetricsContract:
    """Test CircuitBreakerEventResponse schema for circuit breaker events."""

    def test_circuit_breaker_event_response_schema_valid(self):
        """Test CircuitBreakerEventResponse accepts valid event data."""
        # Arrange & Act
        response = CircuitBreakerEventResponse(
            proxy_id="proxy1.example.com:8080",
            from_state="closed",
            to_state="open",
            timestamp=datetime.now(timezone.utc),
            failure_count=5,
        )

        # Assert
        assert response.proxy_id == "proxy1.example.com:8080"
        assert response.from_state == "closed"
        assert response.to_state == "open"
        assert isinstance(response.timestamp, datetime)
        assert response.failure_count == 5

    def test_circuit_breaker_event_response_schema_recovery(self):
        """Test CircuitBreakerEventResponse for recovery event."""
        # Arrange & Act
        response = CircuitBreakerEventResponse(
            proxy_id="proxy2.example.com:8080",
            from_state="half_open",
            to_state="closed",
            timestamp=datetime.now(timezone.utc),
            failure_count=0,
        )

        # Assert
        assert response.from_state == "half_open"
        assert response.to_state == "closed"
        assert response.failure_count == 0


# T305: Contract test for GET /api/v1/circuit-breakers/{proxy_id}
@pytest.mark.skip(reason="Covered by T303 CircuitBreakerResponse schema test")
def test_get_circuit_breaker_by_id_contract():
    """Test GET /api/v1/circuit-breakers/{proxy_id} response schema."""
    pass


# T306: Contract test for POST /api/v1/circuit-breakers/{proxy_id}/reset
@pytest.mark.skip(reason="Covered by T303 CircuitBreakerResponse schema test")
def test_reset_circuit_breaker_contract():
    """Test POST /api/v1/circuit-breakers/{proxy_id}/reset response schema."""
    pass


# T307: Contract test for GET /api/v1/metrics/retries
class TestGetRetryMetricsContract:
    """Test RetryMetricsResponse schema for retry metrics summary."""

    def test_retry_metrics_response_schema_valid(self):
        """Test RetryMetricsResponse accepts valid metrics data."""
        # Arrange & Act
        response = RetryMetricsResponse(
            total_retries=1250,
            success_by_attempt={
                "0": 850,
                "1": 300,
                "2": 80,
                "3": 20,
            },
            circuit_breaker_events_count=15,
            retention_hours=24,
        )

        # Assert
        assert response.total_retries == 1250
        assert response.success_by_attempt["0"] == 850
        assert response.success_by_attempt["1"] == 300
        assert response.circuit_breaker_events_count == 15
        assert response.retention_hours == 24

    def test_retry_metrics_response_schema_zero_retries(self):
        """Test RetryMetricsResponse with zero retries."""
        # Arrange & Act
        response = RetryMetricsResponse(
            total_retries=0,
            success_by_attempt={},
            circuit_breaker_events_count=0,
            retention_hours=24,
        )

        # Assert
        assert response.total_retries == 0
        assert response.success_by_attempt == {}
        assert response.circuit_breaker_events_count == 0


# T308: Contract test for GET /api/v1/metrics/retries/timeseries
class TestGetRetryTimeseriesContract:
    """Test TimeSeriesResponse schema for time-series retry data."""

    def test_time_series_data_point_schema_valid(self):
        """Test TimeSeriesDataPoint accepts valid data."""
        # Arrange & Act
        point = TimeSeriesDataPoint(
            timestamp=datetime.now(timezone.utc),
            total_requests=1000,
            total_retries=150,
            success_rate=0.95,
            avg_latency=0.25,
        )

        # Assert
        assert isinstance(point.timestamp, datetime)
        assert point.total_requests == 1000
        assert point.total_retries == 150
        assert point.success_rate == 0.95
        assert point.avg_latency == 0.25

    def test_time_series_response_schema_valid(self):
        """Test TimeSeriesResponse with multiple data points."""
        # Arrange
        point1 = TimeSeriesDataPoint(
            timestamp=datetime.now(timezone.utc),
            total_requests=1000,
            total_retries=150,
            success_rate=0.95,
            avg_latency=0.25,
        )
        point2 = TimeSeriesDataPoint(
            timestamp=datetime.now(timezone.utc),
            total_requests=1100,
            total_retries=140,
            success_rate=0.96,
            avg_latency=0.22,
        )

        # Act
        response = TimeSeriesResponse(data_points=[point1, point2])

        # Assert
        assert len(response.data_points) == 2
        assert response.data_points[0].total_requests == 1000
        assert response.data_points[1].total_requests == 1100

    def test_time_series_data_point_schema_invalid_success_rate(self):
        """Test TimeSeriesDataPoint rejects invalid success_rate."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            TimeSeriesDataPoint(
                timestamp=datetime.now(timezone.utc),
                total_requests=1000,
                total_retries=150,
                success_rate=1.5,  # Must be <= 1.0
                avg_latency=0.25,
            )

        errors = exc_info.value.errors()
        assert any("less_than_equal" in str(e["type"]) for e in errors)


# T309: Contract test for GET /api/v1/metrics/retries/by-proxy
class TestGetRetryStatsByProxyContract:
    """Test ProxyRetryStatsResponse schema for per-proxy retry statistics."""

    def test_proxy_retry_stats_schema_valid(self):
        """Test ProxyRetryStats accepts valid statistics data."""
        # Arrange & Act
        stats = ProxyRetryStats(
            proxy_id="proxy1.example.com:8080",
            total_attempts=500,
            success_count=450,
            failure_count=50,
            avg_latency=0.3,
            circuit_breaker_opens=2,
        )

        # Assert
        assert stats.proxy_id == "proxy1.example.com:8080"
        assert stats.total_attempts == 500
        assert stats.success_count == 450
        assert stats.failure_count == 50
        assert stats.avg_latency == 0.3
        assert stats.circuit_breaker_opens == 2

    def test_proxy_retry_stats_response_schema_valid(self):
        """Test ProxyRetryStatsResponse with multiple proxies."""
        # Arrange
        stats1 = ProxyRetryStats(
            proxy_id="proxy1.example.com:8080",
            total_attempts=500,
            success_count=450,
            failure_count=50,
            avg_latency=0.3,
            circuit_breaker_opens=2,
        )
        stats2 = ProxyRetryStats(
            proxy_id="proxy2.example.com:8080",
            total_attempts=300,
            success_count=290,
            failure_count=10,
            avg_latency=0.2,
            circuit_breaker_opens=0,
        )

        # Act
        response = ProxyRetryStatsResponse(
            proxies={
                "proxy1.example.com:8080": stats1,
                "proxy2.example.com:8080": stats2,
            }
        )

        # Assert
        assert len(response.proxies) == 2
        assert "proxy1.example.com:8080" in response.proxies
        assert "proxy2.example.com:8080" in response.proxies
        assert response.proxies["proxy1.example.com:8080"].total_attempts == 500
        assert response.proxies["proxy2.example.com:8080"].total_attempts == 300

    def test_proxy_retry_stats_schema_zero_attempts(self):
        """Test ProxyRetryStats with zero attempts (new proxy)."""
        # Arrange & Act
        stats = ProxyRetryStats(
            proxy_id="proxy-new.example.com:8080",
            total_attempts=0,
            success_count=0,
            failure_count=0,
            avg_latency=0.0,
            circuit_breaker_opens=0,
        )

        # Assert
        assert stats.total_attempts == 0
        assert stats.success_count == 0
        assert stats.failure_count == 0
        assert stats.avg_latency == 0.0


# T310: Contract test for GET /metrics/retry (JSON format)
@pytest.mark.skip(reason="GET /metrics/retry returns dynamic JSON - covered by integration tests")
def test_retry_metrics_endpoint_json_contract():
    """Test GET /metrics/retry JSON response format."""
    pass


# T311: Contract test for GET /metrics/retry?format=prometheus
@pytest.mark.skip(
    reason="GET /metrics/retry?format=prometheus returns Prometheus text - covered by integration tests"
)
def test_retry_metrics_endpoint_prometheus_contract():
    """Test GET /metrics/retry?format=prometheus response format."""
    pass


# T312: Contract test for GET /metrics/circuit-breaker (JSON format)
@pytest.mark.skip(
    reason="GET /metrics/circuit-breaker returns dynamic JSON - covered by integration tests"
)
def test_circuit_breaker_metrics_endpoint_json_contract():
    """Test GET /metrics/circuit-breaker JSON response format."""
    pass


# T313: Contract test for GET /metrics/circuit-breaker?format=prometheus
@pytest.mark.skip(
    reason="GET /metrics/circuit-breaker?format=prometheus returns Prometheus text - covered by integration tests"
)
def test_circuit_breaker_metrics_endpoint_prometheus_contract():
    """Test GET /metrics/circuit-breaker?format=prometheus response format."""
    pass


# ============================================================================
# ADDITIONAL VALIDATION TESTS
# ============================================================================


class TestRetryPolicyValidationEdgeCases:
    """Test edge cases and boundary validation for retry policy models."""

    def test_retry_policy_request_valid_boundaries(self):
        """Test RetryPolicyRequest with boundary values."""
        # Arrange & Act
        request = RetryPolicyRequest(
            max_attempts=1,  # Minimum
            base_delay=0.1,  # Small but > 0
            multiplier=1.1,  # Just > 1
            max_backoff_delay=300.0,  # Maximum
        )

        # Assert
        assert request.max_attempts == 1
        assert request.base_delay == 0.1
        assert request.multiplier == 1.1
        assert request.max_backoff_delay == 300.0

    def test_circuit_breaker_response_invalid_negative_failure_count(self):
        """Test CircuitBreakerResponse rejects negative failure count."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            CircuitBreakerResponse(
                proxy_id="proxy1.example.com:8080",
                state="closed",
                failure_count=-1,  # Invalid
                failure_threshold=5,
                window_duration=60.0,
                timeout_duration=30.0,
                last_state_change=datetime.now(timezone.utc),
            )

        errors = exc_info.value.errors()
        assert any("greater_than_equal" in str(e["type"]) for e in errors)

    def test_proxy_retry_stats_invalid_negative_attempts(self):
        """Test ProxyRetryStats rejects negative total_attempts."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ProxyRetryStats(
                proxy_id="proxy1.example.com:8080",
                total_attempts=-10,  # Invalid
                success_count=0,
                failure_count=0,
                avg_latency=0.0,
                circuit_breaker_opens=0,
            )

        errors = exc_info.value.errors()
        assert any("greater_than_equal" in str(e["type"]) for e in errors)
