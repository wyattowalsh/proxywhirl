"""
Unit tests for PerformanceAnalyzer.

Tests proxy performance analysis, scoring, ranking, and recommendations.
"""

from datetime import datetime, timedelta

import pytest

from proxywhirl.analytics_models import (
    AnalysisConfig,
    ProxyPerformanceMetrics,
    TrendDirection,
)
from proxywhirl.performance_analyzer import PerformanceAnalyzer


class TestPerformanceAnalyzer:
    """Test PerformanceAnalyzer functionality."""

    def test_init_default_config(self) -> None:
        """Test initialization with default config."""
        analyzer = PerformanceAnalyzer()
        
        assert analyzer.config is not None
        assert analyzer.config.lookback_days == 30

    def test_init_custom_config(self) -> None:
        """Test initialization with custom config."""
        config = AnalysisConfig(lookback_days=60)
        analyzer = PerformanceAnalyzer(config=config)
        
        assert analyzer.config.lookback_days == 60

    def test_calculate_success_rate(self) -> None:
        """Test success rate calculation."""
        analyzer = PerformanceAnalyzer()
        
        # Normal case
        rate = analyzer.calculate_success_rate(90, 100)
        assert rate == 0.9
        
        # Edge case: zero requests
        rate = analyzer.calculate_success_rate(0, 0)
        assert rate == 0.0
        
        # Perfect success
        rate = analyzer.calculate_success_rate(100, 100)
        assert rate == 1.0

    def test_calculate_average_latency(self) -> None:
        """Test average latency calculation."""
        analyzer = PerformanceAnalyzer()
        
        latencies = [100.0, 200.0, 300.0, 400.0]
        avg = analyzer.calculate_average_latency(latencies)
        assert avg == 250.0
        
        # Empty list
        avg = analyzer.calculate_average_latency([])
        assert avg == 0.0

    def test_calculate_uptime(self) -> None:
        """Test uptime percentage calculation."""
        analyzer = PerformanceAnalyzer()
        
        # 95% uptime
        uptime = analyzer.calculate_uptime(95.0, 5.0)
        assert abs(uptime - 95.0) < 0.01
        
        # Perfect uptime
        uptime = analyzer.calculate_uptime(100.0, 0.0)
        assert uptime == 100.0
        
        # No data
        uptime = analyzer.calculate_uptime(0.0, 0.0)
        assert uptime == 100.0

    def test_calculate_latency_percentiles(self) -> None:
        """Test latency percentile calculation."""
        analyzer = PerformanceAnalyzer()
        
        latencies = [float(i) for i in range(1, 101)]  # 1-100ms
        percentiles = analyzer.calculate_latency_percentiles(latencies)
        
        assert "p50" in percentiles
        assert "p95" in percentiles
        assert "p99" in percentiles
        assert percentiles["min"] == 1.0
        assert percentiles["max"] == 100.0
        
        # p50 should be around 50
        assert 45 < percentiles["p50"] < 55
        
        # p95 should be around 95
        assert 90 < percentiles["p95"] < 100

    def test_calculate_performance_score(self) -> None:
        """Test performance score calculation."""
        analyzer = PerformanceAnalyzer()
        
        metrics = ProxyPerformanceMetrics(
            proxy_id="test-proxy",
            proxy_url="http://test.example.com:8080",
            total_requests=1000,
            successful_requests=950,
            success_rate=0.95,
            avg_latency_ms=250.0,
            uptime_percentage=98.0,
        )
        
        score = analyzer.calculate_performance_score(metrics)
        
        assert score.proxy_id == "test-proxy"
        assert 0 <= score.overall_score <= 100
        assert 0 <= score.success_rate_score <= 100
        assert 0 <= score.latency_score <= 100
        assert 0 <= score.uptime_score <= 100
        
        # High success rate should yield high score
        assert score.success_rate_score > 90

    def test_calculate_performance_scores_multiple(self) -> None:
        """Test calculating scores for multiple proxies."""
        analyzer = PerformanceAnalyzer()
        
        metrics = {
            "proxy-1": ProxyPerformanceMetrics(
                proxy_id="proxy-1",
                proxy_url="http://proxy1.example.com:8080",
                success_rate=0.95,
                avg_latency_ms=200.0,
                uptime_percentage=99.0,
            ),
            "proxy-2": ProxyPerformanceMetrics(
                proxy_id="proxy-2",
                proxy_url="http://proxy2.example.com:8080",
                success_rate=0.85,
                avg_latency_ms=400.0,
                uptime_percentage=95.0,
            ),
        }
        
        scores = analyzer.calculate_performance_scores(metrics)
        
        assert len(scores) == 2
        assert "proxy-1" in scores
        assert "proxy-2" in scores
        
        # Proxy 1 should have better score
        assert scores["proxy-1"].overall_score > scores["proxy-2"].overall_score

    def test_rank_proxies(self) -> None:
        """Test proxy ranking by performance."""
        analyzer = PerformanceAnalyzer()
        
        metrics = {
            f"proxy-{i}": ProxyPerformanceMetrics(
                proxy_id=f"proxy-{i}",
                proxy_url=f"http://proxy{i}.example.com:8080",
                success_rate=0.7 + (i * 0.05),
                avg_latency_ms=500.0 - (i * 50.0),
                uptime_percentage=90.0 + i,
            )
            for i in range(1, 6)
        }
        
        scores = analyzer.calculate_performance_scores(metrics)
        ranked = analyzer.rank_proxies(scores)
        
        assert len(ranked) == 5
        
        # Check descending order
        for i in range(len(ranked) - 1):
            assert ranked[i][1].overall_score >= ranked[i + 1][1].overall_score
        
        # Check ranks are assigned
        assert ranked[0][1].rank == 1
        assert ranked[-1][1].rank == 5

    def test_identify_underperforming_proxies(self) -> None:
        """Test identifying underperforming proxies."""
        analyzer = PerformanceAnalyzer()
        
        metrics = {
            "good-proxy": ProxyPerformanceMetrics(
                proxy_id="good-proxy",
                proxy_url="http://good.example.com:8080",
                success_rate=0.95,
                avg_latency_ms=200.0,
                uptime_percentage=99.0,
            ),
            "bad-proxy": ProxyPerformanceMetrics(
                proxy_id="bad-proxy",
                proxy_url="http://bad.example.com:8080",
                success_rate=0.5,  # Below threshold
                avg_latency_ms=200.0,
                uptime_percentage=99.0,
            ),
        }
        
        underperformers = analyzer.identify_underperforming_proxies(metrics)
        
        assert len(underperformers) == 1
        assert "bad-proxy" in underperformers
        assert "good-proxy" not in underperformers

    def test_detect_degradation_patterns(self) -> None:
        """Test degradation pattern detection."""
        analyzer = PerformanceAnalyzer()
        
        base_time = datetime.now()
        
        # Create declining performance trend
        historical_metrics = [
            ProxyPerformanceMetrics(
                proxy_id="proxy-1",
                proxy_url="http://proxy1.example.com:8080",
                success_rate=1.0 - (i * 0.05),  # Declining from 1.0 to 0.5
                first_seen=base_time + timedelta(hours=i),
                last_seen=base_time + timedelta(hours=i),
            )
            for i in range(10)
        ]
        
        trends = analyzer.detect_degradation_patterns(historical_metrics, window_size=5)
        
        assert "proxy-1" in trends
        assert trends["proxy-1"] == TrendDirection.DECREASING

    def test_generate_performance_recommendations(self) -> None:
        """Test performance recommendation generation."""
        analyzer = PerformanceAnalyzer()
        
        metrics = {
            "good-proxy": ProxyPerformanceMetrics(
                proxy_id="good-proxy",
                proxy_url="http://good.example.com:8080",
                total_requests=1000,
                success_rate=0.95,
                avg_latency_ms=200.0,
                uptime_percentage=99.0,
            ),
            "bad-proxy": ProxyPerformanceMetrics(
                proxy_id="bad-proxy",
                proxy_url="http://bad.example.com:8080",
                total_requests=1000,
                success_rate=0.5,  # Underperforming
                avg_latency_ms=200.0,
                uptime_percentage=99.0,
            ),
        }
        
        scores = analyzer.calculate_performance_scores(metrics)
        recommendations = analyzer.generate_performance_recommendations(metrics, scores)
        
        assert len(recommendations) > 0
        
        # Should recommend removing underperformers
        titles = [rec.title for rec in recommendations]
        assert any("Underperforming" in title or "underperforming" in title.lower() 
                   for title in titles)

    def test_calculate_statistical_summary(self) -> None:
        """Test statistical summary calculation."""
        analyzer = PerformanceAnalyzer()
        
        metrics_list = [
            ProxyPerformanceMetrics(
                proxy_id=f"proxy-{i}",
                proxy_url=f"http://proxy{i}.example.com:8080",
                success_rate=0.8 + (i * 0.02),
                avg_latency_ms=200.0 + (i * 10.0),
                uptime_percentage=95.0 + i,
            )
            for i in range(10)
        ]
        
        summary = analyzer.calculate_statistical_summary(metrics_list)
        
        assert "success_rate" in summary
        assert "avg_latency_ms" in summary
        assert "uptime_percentage" in summary
        
        assert "mean" in summary["success_rate"]
        assert "median" in summary["success_rate"]
        assert "stdev" in summary["success_rate"]
        
        assert summary["total_proxies"] == 10

    def test_edge_case_single_proxy(self) -> None:
        """Test with single proxy edge case."""
        analyzer = PerformanceAnalyzer()
        
        metrics = {
            "proxy-1": ProxyPerformanceMetrics(
                proxy_id="proxy-1",
                proxy_url="http://proxy1.example.com:8080",
                success_rate=0.95,
                avg_latency_ms=250.0,
                uptime_percentage=99.0,
            ),
        }
        
        scores = analyzer.calculate_performance_scores(metrics)
        ranked = analyzer.rank_proxies(scores)
        
        assert len(ranked) == 1
        assert ranked[0][1].rank == 1
        assert ranked[0][1].percentile == 100.0

    def test_edge_case_zero_requests(self) -> None:
        """Test with proxy having zero requests."""
        analyzer = PerformanceAnalyzer()
        
        metrics = ProxyPerformanceMetrics(
            proxy_id="new-proxy",
            proxy_url="http://new.example.com:8080",
            total_requests=0,
            success_rate=0.0,
        )
        
        score = analyzer.calculate_performance_score(metrics)
        
        # Should handle gracefully
        assert score.overall_score >= 0
        assert score.overall_score <= 100
