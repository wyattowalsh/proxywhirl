"""Integration tests for health monitoring."""

import time
from unittest.mock import Mock, patch

import pytest

from proxywhirl.health import HealthChecker
from proxywhirl.health_models import HealthCheckConfig, HealthStatus


class TestHealthIntegration:
    """Integration tests for health checker (T020-T021)."""
    
    @patch("httpx.Client")
    def test_end_to_end_health_check_flow(self, mock_client_class: Mock) -> None:
        """Test end-to-end health check flow (T020)."""
        from datetime import timedelta
        
        # Setup mock for successful responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.elapsed = timedelta(milliseconds=100)
        
        mock_client = Mock()
        mock_client.head.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        # Create checker with minimum interval (10s)
        config = HealthCheckConfig(check_interval_seconds=10)
        checker = HealthChecker(config=config)
        
        # Add proxies
        checker.add_proxy("http://proxy1.example.com:8080", source="test")
        checker.add_proxy("http://proxy2.example.com:8080", source="test")
        
        # Manually perform checks instead of waiting for background thread
        # (to avoid slow tests)
        result1 = checker.check_proxy("http://proxy1.example.com:8080")
        checker._update_health_status("http://proxy1.example.com:8080", result1)
        
        result2 = checker.check_proxy("http://proxy2.example.com:8080")
        checker._update_health_status("http://proxy2.example.com:8080", result2)
        
        # Verify checks were executed
        proxy1_state = checker._proxies["http://proxy1.example.com:8080"]
        proxy2_state = checker._proxies["http://proxy2.example.com:8080"]
        
        assert proxy1_state["total_checks"] > 0
        assert proxy2_state["total_checks"] > 0
        assert proxy1_state["health_status"] == HealthStatus.HEALTHY
        assert proxy2_state["health_status"] == HealthStatus.HEALTHY
    
    def test_cache_invalidation_on_health_failure(self) -> None:
        """Test cache invalidation when proxy becomes unhealthy (T021)."""
        # Create mock cache manager
        mock_cache = Mock()
        
        config = HealthCheckConfig(failure_threshold=2)
        checker = HealthChecker(config=config, cache_manager=mock_cache)
        
        # Add proxy
        checker.add_proxy("http://proxy1.example.com:8080", source="test")
        
        # Simulate failures
        from datetime import datetime, timezone
        failure_result = Mock(
            status=HealthStatus.UNHEALTHY,
            proxy_url="http://proxy1.example.com:8080",
            check_time=datetime.now(timezone.utc),
            status_code=None,
            response_time_ms=None,
            error_message="Connection failed",
            check_url="http://www.google.com"
        )
        
        # First failure - should not invalidate yet
        checker._update_health_status("http://proxy1.example.com:8080", failure_result)
        assert mock_cache.invalidate_by_health.call_count == 0

        # Second failure - should invalidate cache
        checker._update_health_status("http://proxy1.example.com:8080", failure_result)
        assert mock_cache.invalidate_by_health.call_count > 0
        
        # Verify proxy is marked unhealthy
        proxy_state = checker._proxies["http://proxy1.example.com:8080"]
        assert proxy_state["health_status"] == HealthStatus.UNHEALTHY
        assert proxy_state["consecutive_failures"] == 2
