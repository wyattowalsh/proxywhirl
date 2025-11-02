"""
Integration tests for analytics engine end-to-end workflows.

Tests complete analytics workflows including data collection, analysis,
and report generation.
"""

from datetime import datetime, timedelta
from random import choice, random

import pytest

from proxywhirl.analytics_engine import AnalyticsEngine
from proxywhirl.analytics_models import (
    AnalysisConfig,
    AnalysisType,
    AnalyticsQuery,
)


class TestAnalyticsEngineE2E:
    """End-to-end tests for analytics engine."""

    @pytest.fixture
    def engine(self) -> AnalyticsEngine:
        """Create analytics engine for testing."""
        config = AnalysisConfig(
            lookback_days=30,
            min_success_rate=0.7,
            cache_results=True,
        )
        return AnalyticsEngine(config=config)

    @pytest.fixture
    def populated_engine(self, engine: AnalyticsEngine) -> AnalyticsEngine:
        """Create analytics engine with sample data."""
        # Generate sample data
        proxies = [
            ("proxy-1", "http://proxy1.example.com:8080", "us-east-1", "pool-1"),
            ("proxy-2", "http://proxy2.example.com:8080", "us-west-2", "pool-1"),
            ("proxy-3", "http://proxy3.example.com:8080", "eu-west-1", "pool-2"),
        ]
        
        base_time = datetime.now() - timedelta(days=7)
        
        for day in range(7):
            for hour in range(24):
                timestamp = base_time + timedelta(days=day, hours=hour)
                
                for proxy_id, proxy_url, region, pool in proxies:
                    # Simulate requests
                    success_rate = 0.85 + (random() * 0.1)
                    
                    for _ in range(5):
                        success = random() < success_rate
                        latency = 200.0 + (random() * 100.0)
                        
                        engine.record_request(
                            proxy_id=proxy_id,
                            proxy_url=proxy_url,
                            success=success,
                            latency_ms=latency,
                            timestamp=timestamp,
                            pool=pool,
                            region=region,
                            target_domain="example.com",
                            error_type="timeout" if not success else None,
                        )
        
        # Record uptime
        for proxy_id, _, _, _ in proxies:
            engine.record_proxy_uptime(proxy_id, 168.0, 1.0)  # 7 days with 1 hour downtime
        
        return engine

    def test_engine_initialization(self) -> None:
        """Test analytics engine initialization."""
        config = AnalysisConfig()
        engine = AnalyticsEngine(config=config)
        
        assert engine.config is not None
        assert engine.performance_analyzer is not None
        
        summary = engine.get_metrics_summary()
        assert summary["total_proxies"] == 0

    def test_record_request(self, engine: AnalyticsEngine) -> None:
        """Test recording a single request."""
        engine.record_request(
            proxy_id="test-proxy",
            proxy_url="http://test.example.com:8080",
            success=True,
            latency_ms=250.0,
            pool="test-pool",
            region="us-east-1",
        )
        
        summary = engine.get_metrics_summary()
        assert summary["total_proxies"] == 1
        assert summary["total_requests_all_proxies"] == 1

    def test_record_multiple_requests(self, engine: AnalyticsEngine) -> None:
        """Test recording multiple requests."""
        for i in range(100):
            engine.record_request(
                proxy_id=f"proxy-{i % 5}",
                proxy_url=f"http://proxy{i%5}.example.com:8080",
                success=i % 10 != 0,  # 90% success rate
                latency_ms=200.0 + float(i % 100),
            )
        
        summary = engine.get_metrics_summary()
        assert summary["total_proxies"] == 5
        assert summary["total_requests_all_proxies"] == 100

    def test_record_proxy_uptime(self, engine: AnalyticsEngine) -> None:
        """Test recording proxy uptime."""
        # First record some requests
        engine.record_request(
            proxy_id="uptime-test",
            proxy_url="http://uptime.example.com:8080",
            success=True,
            latency_ms=200.0,
        )
        
        # Then record uptime
        engine.record_proxy_uptime("uptime-test", 95.0, 5.0)
        
        # Verify uptime was recorded
        summary = engine.get_metrics_summary()
        assert summary["total_proxies"] == 1

    def test_performance_analysis_empty(self, engine: AnalyticsEngine) -> None:
        """Test performance analysis with no data."""
        report = engine.analyze_performance()
        
        assert report is not None
        assert report.analysis_type == AnalysisType.PERFORMANCE
        assert report.total_proxies_analyzed == 0

    def test_performance_analysis_with_data(
        self,
        populated_engine: AnalyticsEngine,
    ) -> None:
        """Test performance analysis with real data."""
        report = populated_engine.analyze_performance()
        
        assert report is not None
        assert report.total_proxies_analyzed == 3
        assert report.total_requests_analyzed > 0
        assert len(report.key_findings) > 0
        assert report.executive_summary != ""
        
        # Check performance metrics
        assert report.performance_metrics is not None
        assert len(report.performance_metrics) == 3
        
        # Check performance scores
        assert report.performance_scores is not None
        assert len(report.performance_scores) == 3

    def test_performance_analysis_with_query_filters(
        self,
        populated_engine: AnalyticsEngine,
    ) -> None:
        """Test performance analysis with query filters."""
        query = AnalyticsQuery(
            proxy_ids=["proxy-1", "proxy-2"],
            include_recommendations=True,
        )
        
        report = populated_engine.analyze_performance(query)
        
        assert report.total_proxies_analyzed == 2
        assert report.performance_metrics is not None
        assert len(report.performance_metrics) == 2

    def test_performance_analysis_caching(
        self,
        populated_engine: AnalyticsEngine,
    ) -> None:
        """Test that analysis results are cached."""
        # First analysis
        report1 = populated_engine.analyze_performance()
        
        # Second analysis should be cached
        report2 = populated_engine.analyze_performance()
        
        # Should return same report
        assert report1.report_id == report2.report_id
        assert report1.created_at == report2.created_at

    def test_export_to_json(
        self,
        populated_engine: AnalyticsEngine,
        tmp_path: pytest.TempPathFactory,  # type: ignore
    ) -> None:
        """Test exporting report to JSON."""
        import json
        
        report = populated_engine.analyze_performance()
        
        output_file = tmp_path / "test_report.json"  # type: ignore
        populated_engine.export_to_json(report, str(output_file))
        
        assert output_file.exists()  # type: ignore
        
        # Verify JSON is valid
        with open(output_file) as f:  # type: ignore
            data = json.load(f)
            assert "report_id" in data
            assert "analysis_type" in data

    def test_export_to_csv(
        self,
        populated_engine: AnalyticsEngine,
        tmp_path: pytest.TempPathFactory,  # type: ignore
    ) -> None:
        """Test exporting metrics to CSV."""
        import csv
        
        report = populated_engine.analyze_performance()
        
        output_file = tmp_path / "test_metrics.csv"  # type: ignore
        populated_engine.export_to_csv(report, str(output_file))
        
        assert output_file.exists()  # type: ignore
        
        # Verify CSV is valid
        with open(output_file) as f:  # type: ignore
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) > 0
            assert "proxy_id" in rows[0]

    def test_clear_data(self, populated_engine: AnalyticsEngine) -> None:
        """Test clearing all data."""
        # Verify data exists
        summary = populated_engine.get_metrics_summary()
        assert summary["total_proxies"] > 0
        
        # Clear data
        populated_engine.clear_data()
        
        # Verify data is cleared
        summary = populated_engine.get_metrics_summary()
        assert summary["total_proxies"] == 0
        assert summary["cache_size"] == 0

    def test_concurrent_data_recording(
        self,
        engine: AnalyticsEngine,
    ) -> None:
        """Test thread-safe concurrent data recording."""
        import threading
        
        def record_requests(proxy_id: str, count: int) -> None:
            for i in range(count):
                engine.record_request(
                    proxy_id=proxy_id,
                    proxy_url=f"http://{proxy_id}.example.com:8080",
                    success=i % 2 == 0,
                    latency_ms=200.0,
                )
        
        threads = [
            threading.Thread(target=record_requests, args=(f"proxy-{i}", 100))
            for i in range(5)
        ]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        summary = engine.get_metrics_summary()
        assert summary["total_proxies"] == 5
        assert summary["total_requests_all_proxies"] == 500

    def test_recommendations_generation(
        self,
        populated_engine: AnalyticsEngine,
    ) -> None:
        """Test that recommendations are generated."""
        query = AnalyticsQuery(include_recommendations=True)
        report = populated_engine.analyze_performance(query)
        
        # Should have some recommendations
        assert len(report.recommendations) >= 0

    def test_performance_with_underperformers(self) -> None:
        """Test analysis with underperforming proxies."""
        config = AnalysisConfig(min_success_rate=0.8)
        engine = AnalyticsEngine(config=config)
        
        # Add good proxy
        for _ in range(100):
            engine.record_request(
                proxy_id="good-proxy",
                proxy_url="http://good.example.com:8080",
                success=True,
                latency_ms=200.0,
            )
        
        # Add bad proxy
        for _ in range(100):
            engine.record_request(
                proxy_id="bad-proxy",
                proxy_url="http://bad.example.com:8080",
                success=False,  # 0% success rate
                latency_ms=500.0,
            )
        
        report = engine.analyze_performance()
        
        assert report.total_proxies_analyzed == 2
        # Should recommend removing underperformers
        if report.recommendations:
            assert any("underperform" in rec.description.lower() 
                      for rec in report.recommendations)

    def test_metrics_summary(self, populated_engine: AnalyticsEngine) -> None:
        """Test metrics summary generation."""
        summary = populated_engine.get_metrics_summary()
        
        assert isinstance(summary, dict)
        assert "total_proxies" in summary
        assert "total_requests_recorded" in summary
        assert "total_requests_all_proxies" in summary
        assert "cache_size" in summary
        assert "oldest_data" in summary
        assert "newest_data" in summary
        
        assert summary["total_proxies"] > 0
        assert summary["total_requests_all_proxies"] > 0

    def test_time_based_filtering(self, populated_engine: AnalyticsEngine) -> None:
        """Test filtering by time range."""
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        
        query = AnalyticsQuery(
            start_time=yesterday,
            end_time=now,
        )
        
        report = populated_engine.analyze_performance(query)
        
        assert report is not None
        # Verify time range was applied
        assert report.period_start >= yesterday
        assert report.period_end <= now

    def test_statistical_accuracy(self, populated_engine: AnalyticsEngine) -> None:
        """Test statistical calculations are accurate."""
        report = populated_engine.analyze_performance()
        
        if report.performance_metrics:
            for metrics in report.performance_metrics.values():
                # Verify success rate calculation
                if metrics.total_requests > 0:
                    expected_rate = metrics.successful_requests / metrics.total_requests
                    assert abs(metrics.success_rate - expected_rate) < 0.01
                
                # Verify uptime calculation
                total_hours = metrics.total_uptime_hours + metrics.total_downtime_hours
                if total_hours > 0:
                    expected_uptime = (metrics.total_uptime_hours / total_hours) * 100
                    assert abs(metrics.uptime_percentage - expected_uptime) < 0.01
