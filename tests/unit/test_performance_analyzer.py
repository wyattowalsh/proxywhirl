"""Unit tests for performance analyzer."""

from datetime import datetime

import pytest

from proxywhirl.analytics_models import AnalysisConfig, ProxyPerformanceMetrics
from proxywhirl.performance_analyzer import PerformanceAnalyzer


class TestPerformanceAnalyzer:
    """Test PerformanceAnalyzer functionality."""

    def test_analyzer_initialization(self):
        """Test analyzer initializes correctly."""
        analyzer = PerformanceAnalyzer()
        assert analyzer is not None
        assert analyzer.config is not None

    def test_calculate_success_rate(self):
        """Test success rate calculation."""
        analyzer = PerformanceAnalyzer()
        
        metrics = ProxyPerformanceMetrics(
            proxy_id="test-proxy",
            proxy_url="http://test:8080",
            total_requests=100,
            successful_requests=85,
            failed_requests=15,
        )
        
        success_rate = analyzer.calculate_success_rate(metrics)
        assert success_rate == 0.85

    def test_rank_proxies(self):
        """Test proxy ranking."""
        analyzer = PerformanceAnalyzer()
        
        # Create sample metrics
        proxy_metrics = {
            "proxy-1": ProxyPerformanceMetrics(
                proxy_id="proxy-1",
                proxy_url="http://proxy1:8080",
                total_requests=100,
                successful_requests=95,
                failed_requests=5,
                success_rate=0.95,
                avg_latency_ms=200.0,
            ),
            "proxy-2": ProxyPerformanceMetrics(
                proxy_id="proxy-2",
                proxy_url="http://proxy2:8080",
                total_requests=100,
                successful_requests=70,
                failed_requests=30,
                success_rate=0.70,
                avg_latency_ms=500.0,
            ),
        }
        
        scores = analyzer.rank_proxies(proxy_metrics)
        
        assert len(scores) == 2
        assert scores[0].proxy_id == "proxy-1"  # Better performer
        assert scores[0].rank == 1
        assert scores[1].rank == 2

    def test_identify_underperforming_proxies(self):
        """Test underperformer identification."""
        analyzer = PerformanceAnalyzer()
        
        proxy_metrics = {
            "good-proxy": ProxyPerformanceMetrics(
                proxy_id="good-proxy",
                proxy_url="http://good:8080",
                total_requests=100,
                successful_requests=90,
                failed_requests=10,
                success_rate=0.90,
                avg_latency_ms=300.0,
            ),
            "bad-proxy": ProxyPerformanceMetrics(
                proxy_id="bad-proxy",
                proxy_url="http://bad:8080",
                total_requests=100,
                successful_requests=50,
                failed_requests=50,
                success_rate=0.50,
                avg_latency_ms=8000.0,
            ),
        }
        
        underperformers = analyzer.identify_underperforming_proxies(proxy_metrics)
        
        assert len(underperformers) == 1
        assert underperformers[0][0] == "bad-proxy"
        assert len(underperformers[0][1]) > 0  # Has issues

    def test_calculate_statistical_summary(self):
        """Test statistical summary calculation."""
        analyzer = PerformanceAnalyzer()
        
        proxy_metrics = {
            f"proxy-{i}": ProxyPerformanceMetrics(
                proxy_id=f"proxy-{i}",
                proxy_url=f"http://proxy{i}:8080",
                total_requests=100,
                successful_requests=80 + i,
                failed_requests=20 - i,
                success_rate=(80 + i) / 100.0,
                avg_latency_ms=100.0 + i * 50,
            )
            for i in range(5)
        }
        
        summary = analyzer.calculate_statistical_summary(proxy_metrics)
        
        assert "total_proxies" in summary
        assert "active_proxies" in summary
        assert "success_rate" in summary
        assert "latency_ms" in summary
        assert summary["total_proxies"] == 5

    def test_generate_performance_recommendations(self):
        """Test recommendation generation."""
        analyzer = PerformanceAnalyzer()
        
        proxy_metrics = {
            "proxy-1": ProxyPerformanceMetrics(
                proxy_id="proxy-1",
                proxy_url="http://proxy1:8080",
                total_requests=100,
                successful_requests=95,
                success_rate=0.95,
                avg_latency_ms=200.0,
            ),
        }
        
        scores = analyzer.rank_proxies(proxy_metrics)
        underperformers = analyzer.identify_underperforming_proxies(proxy_metrics)
        
        recommendations = analyzer.generate_performance_recommendations(
            proxy_metrics, scores, underperformers
        )
        
        assert isinstance(recommendations, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
