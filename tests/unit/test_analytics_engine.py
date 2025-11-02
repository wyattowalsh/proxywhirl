"""Unit tests for analytics engine."""

from datetime import datetime, timedelta

import pytest

from proxywhirl.analytics_engine import AnalyticsEngine
from proxywhirl.analytics_models import AnalysisConfig, AnalysisType, AnalyticsQuery


class TestAnalyticsEngine:
    """Test AnalyticsEngine functionality."""

    def test_engine_initialization(self):
        """Test analytics engine initializes correctly."""
        engine = AnalyticsEngine()
        assert engine is not None
        assert engine.config is not None
        assert isinstance(engine.config, AnalysisConfig)

    def test_record_request(self):
        """Test recording request metrics."""
        engine = AnalyticsEngine()
        
        engine.record_request(
            proxy_id="test-proxy-1",
            proxy_url="http://proxy1.test:8080",
            success=True,
            latency_ms=250.0,
            timestamp=datetime.now(),
            pool="test-pool",
            region="us-east",
        )
        
        metrics = engine.get_proxy_metrics("test-proxy-1")
        assert "test-proxy-1" in metrics
        assert metrics["test-proxy-1"].total_requests == 1
        assert metrics["test-proxy-1"].successful_requests == 1

    def test_multiple_requests(self):
        """Test recording multiple requests updates metrics."""
        engine = AnalyticsEngine()
        
        for i in range(10):
            engine.record_request(
                proxy_id="test-proxy-1",
                proxy_url="http://proxy1.test:8080",
                success=(i % 2 == 0),  # 50% success rate
                latency_ms=100.0 + i * 10,
                timestamp=datetime.now(),
            )
        
        metrics = engine.get_proxy_metrics("test-proxy-1")
        assert metrics["test-proxy-1"].total_requests == 10
        assert metrics["test-proxy-1"].successful_requests == 5
        assert abs(metrics["test-proxy-1"].success_rate - 0.5) < 0.01

    def test_get_request_data_with_filters(self):
        """Test filtering request data."""
        engine = AnalyticsEngine()
        
        now = datetime.now()
        
        # Record requests for different proxies
        for i in range(5):
            engine.record_request(
                proxy_id=f"proxy-{i}",
                proxy_url=f"http://proxy{i}.test:8080",
                success=True,
                latency_ms=100.0,
                timestamp=now,
                pool="test-pool",
            )
        
        # Test filtering by proxy_id
        filtered = engine.get_request_data(filters={"proxy_id": "proxy-0"})
        assert len(filtered) == 1
        assert filtered[0]["proxy_id"] == "proxy-0"

    def test_clear_data(self):
        """Test clearing analytics data."""
        engine = AnalyticsEngine()
        
        # Record some data
        engine.record_request(
            proxy_id="test-proxy",
            proxy_url="http://proxy.test:8080",
            success=True,
            latency_ms=100.0,
        )
        
        # Clear all data
        cleared = engine.clear_data()
        assert cleared == 1
        assert len(engine.get_proxy_metrics()) == 0

    def test_get_stats(self):
        """Test getting engine statistics."""
        engine = AnalyticsEngine()
        
        stats = engine.get_stats()
        assert "total_requests_recorded" in stats
        assert "total_proxies_tracked" in stats
        assert "cache_enabled" in stats

    def test_analyze_empty_data(self):
        """Test analysis with no data."""
        engine = AnalyticsEngine()
        
        query = AnalyticsQuery(analysis_types=[AnalysisType.PERFORMANCE])
        report = engine.analyze(query)
        
        assert report is not None
        assert report.analysis_type == AnalysisType.PERFORMANCE

    def test_analyze_with_data(self):
        """Test analysis with sample data."""
        engine = AnalyticsEngine()
        
        # Record sample data
        for i in range(20):
            engine.record_request(
                proxy_id=f"proxy-{i % 3}",
                proxy_url=f"http://proxy{i % 3}.test:8080",
                success=(i % 5 != 0),  # 80% success rate
                latency_ms=100.0 + i * 5,
                timestamp=datetime.now(),
            )
        
        query = AnalyticsQuery(analysis_types=[AnalysisType.PERFORMANCE])
        report = engine.analyze(query)
        
        assert report is not None
        assert report.performance_results is not None
        assert len(report.performance_results) > 0


class TestAnalysisConfig:
    """Test AnalysisConfig model."""

    def test_default_config(self):
        """Test default configuration values."""
        config = AnalysisConfig()
        assert config.lookback_days == 30
        assert config.min_success_rate == 0.85
        assert config.cache_results is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = AnalysisConfig(
            lookback_days=60,
            min_success_rate=0.90,
            cache_results=False,
        )
        assert config.lookback_days == 60
        assert config.min_success_rate == 0.90
        assert config.cache_results is False

    def test_config_validation(self):
        """Test configuration validation."""
        with pytest.raises(ValueError):
            AnalysisConfig(lookback_days=0)  # Must be >= 1
        
        with pytest.raises(ValueError):
            AnalysisConfig(min_success_rate=1.5)  # Must be <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
