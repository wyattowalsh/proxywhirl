"""Contract tests for health/monitoring endpoints (US3).

Tests API contracts for:
- GET /api/v1/health - Health check
- GET /api/v1/ready - Readiness probe
- GET /api/v1/status - Status information
- GET /api/v1/stats - Performance statistics (renamed from /api/v1/metrics)
"""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from proxywhirl.api_models import (
    HealthResponse,
    MetricsResponse,
    ProxyMetrics,
    ProxyPoolStats,
    ProxyStats,
    ReadinessResponse,
    StatusResponse,
)


# T042: Contract test for GET /api/v1/health
class TestHealthResponseContract:
    """Test HealthResponse schema for health check endpoint."""

    def test_health_response_schema_healthy(self):
        """Test HealthResponse with healthy status."""
        # Arrange & Act
        response = HealthResponse(
            status="healthy",
            uptime_seconds=3600,
            version="1.0.0",
            timestamp=datetime.now(timezone.utc),
        )

        # Assert
        assert response.status == "healthy"
        assert response.uptime_seconds == 3600
        assert response.version == "1.0.0"
        assert response.timestamp is not None

    def test_health_response_schema_degraded(self):
        """Test HealthResponse with degraded status."""
        # Arrange & Act
        response = HealthResponse(
            status="degraded",
            uptime_seconds=7200,
            version="1.0.0",
        )

        # Assert
        assert response.status == "degraded"
        assert response.uptime_seconds == 7200

    def test_health_response_schema_unhealthy(self):
        """Test HealthResponse with unhealthy status."""
        # Arrange & Act
        response = HealthResponse(
            status="unhealthy",
            uptime_seconds=0,
            version="1.0.0",
        )

        # Assert
        assert response.status == "unhealthy"

    def test_health_response_invalid_status(self):
        """Test HealthResponse rejects invalid status values."""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            HealthResponse(
                status="invalid_status",  # type: ignore[arg-type]
                uptime_seconds=100,
                version="1.0.0",
            )

    def test_health_response_timestamp_default(self):
        """Test HealthResponse generates timestamp by default."""
        # Arrange & Act
        response = HealthResponse(
            status="healthy",
            uptime_seconds=100,
            version="1.0.0",
        )

        # Assert
        assert response.timestamp is not None
        assert isinstance(response.timestamp, datetime)


# T043: Contract test for GET /api/v1/ready
class TestReadinessResponseContract:
    """Test ReadinessResponse schema for readiness probe endpoint."""

    def test_readiness_response_ready(self):
        """Test ReadinessResponse when system is ready."""
        # Arrange & Act
        response = ReadinessResponse(
            ready=True,
            checks={
                "proxy_pool_initialized": True,
                "storage_connected": True,
            },
        )

        # Assert
        assert response.ready is True
        assert response.checks["proxy_pool_initialized"] is True
        assert response.checks["storage_connected"] is True

    def test_readiness_response_not_ready(self):
        """Test ReadinessResponse when system is not ready."""
        # Arrange & Act
        response = ReadinessResponse(
            ready=False,
            checks={
                "proxy_pool_initialized": True,
                "storage_connected": False,
            },
        )

        # Assert
        assert response.ready is False
        assert response.checks["proxy_pool_initialized"] is True
        assert response.checks["storage_connected"] is False

    def test_readiness_response_empty_checks(self):
        """Test ReadinessResponse with empty checks dict."""
        # Arrange & Act
        response = ReadinessResponse(
            ready=True,
            checks={},
        )

        # Assert
        assert response.ready is True
        assert response.checks == {}

    def test_readiness_response_multiple_checks(self):
        """Test ReadinessResponse with multiple check types."""
        # Arrange & Act
        response = ReadinessResponse(
            ready=True,
            checks={
                "proxy_pool_initialized": True,
                "storage_connected": True,
                "cache_ready": True,
                "rate_limiter_ready": True,
            },
        )

        # Assert
        assert len(response.checks) == 4
        assert all(response.checks.values())


# T044: Contract test for GET /api/v1/status
class TestStatusResponseContract:
    """Test StatusResponse schema for system status endpoint."""

    def test_status_response_full(self):
        """Test StatusResponse with all fields populated."""
        # Arrange
        pool_stats = ProxyPoolStats(
            total=10,
            active=8,
            failed=2,
            healthy_percentage=80.0,
            last_rotation=datetime.now(timezone.utc),
        )

        # Act
        response = StatusResponse(
            pool_stats=pool_stats,
            rotation_strategy="round-robin",
            storage_backend="sqlite",
            config_source="environment",
        )

        # Assert
        assert response.pool_stats.total == 10
        assert response.pool_stats.active == 8
        assert response.pool_stats.failed == 2
        assert response.pool_stats.healthy_percentage == 80.0
        assert response.rotation_strategy == "round-robin"
        assert response.storage_backend == "sqlite"
        assert response.config_source == "environment"

    def test_status_response_memory_backend(self):
        """Test StatusResponse with memory storage backend."""
        # Arrange
        pool_stats = ProxyPoolStats(
            total=5,
            active=5,
            failed=0,
            healthy_percentage=100.0,
        )

        # Act
        response = StatusResponse(
            pool_stats=pool_stats,
            rotation_strategy="random",
            storage_backend="memory",
        )

        # Assert
        assert response.storage_backend == "memory"
        assert response.config_source == "defaults"  # Default value

    def test_status_response_no_last_rotation(self):
        """Test StatusResponse when no rotation has occurred."""
        # Arrange
        pool_stats = ProxyPoolStats(
            total=0,
            active=0,
            failed=0,
            healthy_percentage=0.0,
            last_rotation=None,
        )

        # Act
        response = StatusResponse(
            pool_stats=pool_stats,
            rotation_strategy="round-robin",
        )

        # Assert
        assert response.pool_stats.last_rotation is None
        assert response.pool_stats.total == 0

    def test_proxy_pool_stats_schema(self):
        """Test ProxyPoolStats schema independently."""
        # Arrange & Act
        stats = ProxyPoolStats(
            total=100,
            active=90,
            failed=10,
            healthy_percentage=90.0,
        )

        # Assert
        assert stats.total == 100
        assert stats.active == 90
        assert stats.failed == 10
        assert stats.healthy_percentage == 90.0


# T045: Contract test for GET /api/v1/stats
class TestMetricsResponseContract:
    """Test MetricsResponse schema for performance statistics endpoint."""

    def test_metrics_response_empty_pool(self):
        """Test MetricsResponse with empty proxy pool."""
        # Arrange & Act
        response = MetricsResponse(
            requests_total=0,
            requests_per_second=0.0,
            avg_latency_ms=0.0,
            error_rate=0.0,
            proxy_stats=[],
        )

        # Assert
        assert response.requests_total == 0
        assert response.requests_per_second == 0.0
        assert response.avg_latency_ms == 0.0
        assert response.error_rate == 0.0
        assert len(response.proxy_stats) == 0

    def test_metrics_response_with_stats(self):
        """Test MetricsResponse with populated statistics."""
        # Arrange - ProxyStats has different fields than ProxyMetrics
        proxy_stat = ProxyStats(
            proxy_id="proxy-123",
            requests=100,
            successes=95,
            failures=5,
            avg_latency_ms=250,
        )

        # Act
        response = MetricsResponse(
            requests_total=1000,
            requests_per_second=10.5,
            avg_latency_ms=250.0,
            error_rate=0.05,
            proxy_stats=[proxy_stat],
        )

        # Assert
        assert response.requests_total == 1000
        assert response.requests_per_second == 10.5
        assert response.avg_latency_ms == 250.0
        assert response.error_rate == 0.05
        assert len(response.proxy_stats) == 1
        assert response.proxy_stats[0].proxy_id == "proxy-123"

    def test_metrics_response_multiple_proxies(self):
        """Test MetricsResponse with multiple proxy statistics."""
        # Arrange - Use ProxyStats, not ProxyMetrics
        proxy_stats = [
            ProxyStats(
                proxy_id=f"proxy-{i}",
                requests=100 * i,
                successes=90 * i,
                failures=10 * i,
                avg_latency_ms=200 + i * 10,
            )
            for i in range(1, 4)
        ]

        # Act
        response = MetricsResponse(
            requests_total=600,
            requests_per_second=5.0,
            avg_latency_ms=220.0,
            error_rate=0.07,
            proxy_stats=proxy_stats,
        )

        # Assert
        assert len(response.proxy_stats) == 3
        assert response.proxy_stats[0].proxy_id == "proxy-1"
        assert response.proxy_stats[1].proxy_id == "proxy-2"
        assert response.proxy_stats[2].proxy_id == "proxy-3"

    def test_proxy_metrics_schema(self):
        """Test ProxyMetrics schema independently."""
        # Arrange & Act
        metrics = ProxyMetrics(
            proxy_id="proxy-abc",
            requests=500,
            success_rate=0.98,
            avg_latency_ms=150.0,
            last_used=datetime.now(timezone.utc),
        )

        # Assert
        assert metrics.proxy_id == "proxy-abc"
        assert metrics.requests == 500
        assert metrics.success_rate == 0.98
        assert metrics.avg_latency_ms == 150.0
        assert metrics.last_used is not None

    def test_proxy_metrics_without_last_used(self):
        """Test ProxyMetrics when last_used is None."""
        # Arrange & Act
        metrics = ProxyMetrics(
            proxy_id="proxy-new",
            requests=0,
            success_rate=0.0,
            avg_latency_ms=0.0,
            last_used=None,
        )

        # Assert
        assert metrics.last_used is None
        assert metrics.requests == 0
