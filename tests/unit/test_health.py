"""Unit tests for HealthChecker class."""

from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest

from proxywhirl.health import HealthChecker
from proxywhirl.health_models import HealthCheckConfig, HealthStatus


class TestHealthChecker:
    """Tests for HealthChecker (T014-T017)."""
    
    def test_init_with_defaults(self) -> None:
        """Test HealthChecker.__init__ with default config (T014)."""
        checker = HealthChecker()
        assert checker.config is not None
        assert isinstance(checker.config, HealthCheckConfig)
        assert not checker._running
        assert checker._proxies == {}
    
    def test_init_with_custom_config(self) -> None:
        """Test HealthChecker.__init__ with custom config (T014)."""
        config = HealthCheckConfig(
            check_interval_seconds=30,
            failure_threshold=5
        )
        checker = HealthChecker(config=config)
        assert checker.config.check_interval_seconds == 30
        assert checker.config.failure_threshold == 5
    
    def test_init_with_cache_integration(self) -> None:
        """Test HealthChecker.__init__ with cache manager (T014)."""
        mock_cache = Mock()
        checker = HealthChecker(cache_manager=mock_cache)
        assert checker.cache_manager is mock_cache
    
    def test_init_callback_registration(self) -> None:
        """Test HealthChecker.__init__ with event callback (T014)."""
        callback = Mock()
        checker = HealthChecker(on_event=callback)
        assert checker.on_event is callback
    
    def test_add_proxy_registers_proxy(self) -> None:
        """Test HealthChecker.add_proxy() registers proxy (T015)."""
        checker = HealthChecker()
        checker.add_proxy("http://proxy1.example.com:8080", source="test")
        
        assert "http://proxy1.example.com:8080" in checker._proxies
        proxy_state = checker._proxies["http://proxy1.example.com:8080"]
        assert proxy_state["source"] == "test"
        assert proxy_state["health_status"] == HealthStatus.UNKNOWN
    
    def test_add_proxy_duplicate_detection(self) -> None:
        """Test HealthChecker.add_proxy() detects duplicates (T015)."""
        checker = HealthChecker()
        checker.add_proxy("http://proxy1.example.com:8080", source="test")
        
        # Adding the same proxy again should not raise, just update
        checker.add_proxy("http://proxy1.example.com:8080", source="test")
        assert len(checker._proxies) == 1
    
    def test_add_proxy_raises_on_invalid_url(self) -> None:
        """Test HealthChecker.add_proxy() raises ValueError for invalid URL (T015)."""
        checker = HealthChecker()
        with pytest.raises(ValueError) as exc_info:
            checker.add_proxy("not-a-valid-url", source="test")
        assert "invalid" in str(exc_info.value).lower() or "url" in str(exc_info.value).lower()
    
    @patch("httpx.Client")
    def test_check_proxy_http_head_request(self, mock_client_class: Mock) -> None:
        """Test HealthChecker.check_proxy() performs HTTP HEAD request (T016)."""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.15
        
        mock_client = Mock()
        mock_client.head.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        checker = HealthChecker()
        result = checker.check_proxy("http://proxy1.example.com:8080")
        
        assert result is not None
        assert result.status == HealthStatus.HEALTHY
        assert result.status_code == 200
        assert result.response_time_ms is not None
    
    @patch("httpx.Client")
    def test_check_proxy_validates_status_code(self, mock_client_class: Mock) -> None:
        """Test HealthChecker.check_proxy() validates status code (T016)."""
        from datetime import timedelta
        
        # Setup mock for non-200 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.elapsed = timedelta(milliseconds=100)
        
        mock_client = Mock()
        mock_client.head.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        checker = HealthChecker()
        result = checker.check_proxy("http://proxy1.example.com:8080")
        
        assert result.status == HealthStatus.UNHEALTHY
        assert result.status_code == 404
    
    @patch("httpx.Client")
    def test_check_proxy_timeout_handling(self, mock_client_class: Mock) -> None:
        """Test HealthChecker.check_proxy() handles timeout (T016)."""
        import httpx
        
        mock_client = Mock()
        mock_client.head.side_effect = httpx.TimeoutException("Request timeout")
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        checker = HealthChecker(config=HealthCheckConfig(check_timeout_seconds=5.0))
        result = checker.check_proxy("http://proxy1.example.com:8080")
        
        assert result.status == HealthStatus.UNHEALTHY
        assert result.error_message is not None
        assert "timeout" in result.error_message.lower()
    
    def test_failure_threshold_logic_tracks_consecutive_failures(self) -> None:
        """Test failure threshold logic tracks consecutive failures (T017)."""
        checker = HealthChecker(config=HealthCheckConfig(failure_threshold=3))
        checker.add_proxy("http://proxy1.example.com:8080", source="test")
        
        # Simulate failures
        for i in range(3):
            with patch.object(checker, "check_proxy") as mock_check:
                mock_check.return_value = Mock(
                    status=HealthStatus.UNHEALTHY,
                    proxy_url="http://proxy1.example.com:8080",
                    check_time=datetime.now(timezone.utc),
                    status_code=None,
                    response_time_ms=None,
                    error_message="Connection failed",
                    check_url="http://www.google.com"
                )
                checker._update_health_status("http://proxy1.example.com:8080", mock_check.return_value)
        
        # After 3 failures, proxy should be marked unhealthy
        proxy_state = checker._proxies["http://proxy1.example.com:8080"]
        assert proxy_state["consecutive_failures"] == 3
        assert proxy_state["health_status"] == HealthStatus.UNHEALTHY
    
    def test_failure_threshold_resets_on_success(self) -> None:
        """Test failure count resets on successful check (T017)."""
        checker = HealthChecker()
        checker.add_proxy("http://proxy1.example.com:8080", source="test")
        
        # Simulate failure
        checker._proxies["http://proxy1.example.com:8080"]["consecutive_failures"] = 2
        
        # Now simulate success
        with patch.object(checker, "check_proxy") as mock_check:
            mock_check.return_value = Mock(
                status=HealthStatus.HEALTHY,
                proxy_url="http://proxy1.example.com:8080",
                check_time=datetime.now(timezone.utc),
                status_code=200,
                response_time_ms=150,
                error_message=None,
                check_url="http://www.google.com"
            )
            checker._update_health_status("http://proxy1.example.com:8080", mock_check.return_value)
        
        # Consecutive failures should be reset
        proxy_state = checker._proxies["http://proxy1.example.com:8080"]
        assert proxy_state["consecutive_failures"] == 0
        assert proxy_state["consecutive_successes"] > 0
