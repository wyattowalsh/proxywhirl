"""Integration tests for analytics engine end-to-end workflows."""

from datetime import datetime, timedelta

import pytest

from proxywhirl import (
    AnalyticsEngine,
    AnalysisConfig,
    AnalysisType,
    AnalyticsQuery,
    PerformanceAnalyzer,
    PatternDetector,
    FailureAnalyzer,
)


class TestAnalyticsE2E:
    """End-to-end integration tests for analytics."""

    @pytest.fixture
    def sample_data(self):
        """Generate sample request data for testing."""
        data = []
        now = datetime.now()
        
        for day in range(7):
            for hour in range(24):
                # Simulate realistic traffic patterns
                requests_per_hour = 10 + (hour % 12) * 2  # Peak during mid-hours
                
                for req in range(requests_per_hour):
                    data.append({
                        "proxy_id": f"proxy-{req % 3}",
                        "proxy_url": f"http://proxy{req % 3}.test:8080",
                        "success": (req % 5 != 0),  # 80% success rate
                        "latency_ms": 100.0 + (req * 10),
                        "timestamp": now - timedelta(days=day, hours=hour, minutes=req),
                        "pool": "test-pool",
                        "region": "us-east" if req % 2 == 0 else "eu-west",
                        "target_domain": "api.example.com",
                        "error_type": None if (req % 5 != 0) else "timeout",
                    })
        
        return data

    def test_complete_analytics_workflow(self, sample_data):
        """Test complete analytics workflow from data recording to report generation."""
        # Initialize engine
        config = AnalysisConfig(lookback_days=7)
        engine = AnalyticsEngine(config=config)
        
        # Record all sample data
        for record in sample_data:
            engine.record_request(**record)
        
        # Verify data was recorded
        stats = engine.get_stats()
        assert stats["total_requests_recorded"] == len(sample_data)
        assert stats["total_proxies_tracked"] > 0
        
        # Generate comprehensive report
        query = AnalyticsQuery(
            analysis_types=[
                AnalysisType.PERFORMANCE,
                AnalysisType.USAGE_PATTERNS,
                AnalysisType.FAILURE_ANALYSIS,
            ],
            lookback_days=7,
        )
        
        report = engine.analyze(query)
        
        # Verify report contents
        assert report is not None
        assert report.report_id is not None
        assert report.performance_results is not None
        assert len(report.key_findings) > 0

    def test_performance_analysis_integration(self, sample_data):
        """Test performance analysis integration."""
        engine = AnalyticsEngine()
        
        # Record data
        for record in sample_data:
            engine.record_request(**record)
        
        # Analyze performance
        analyzer = PerformanceAnalyzer(engine.config)
        proxy_metrics = engine.get_proxy_metrics()
        
        scores = analyzer.rank_proxies(proxy_metrics)
        assert len(scores) > 0
        assert scores[0].rank == 1
        
        # Verify scores are properly ranked
        for i in range(len(scores) - 1):
            assert scores[i].overall_score >= scores[i + 1].overall_score

    def test_pattern_detection_integration(self, sample_data):
        """Test pattern detection integration."""
        engine = AnalyticsEngine()
        
        for record in sample_data:
            engine.record_request(**record)
        
        detector = PatternDetector(engine.config)
        
        # Detect patterns
        peak_hours = detector.detect_peak_hours(sample_data)
        assert isinstance(peak_hours, list)
        assert len(peak_hours) > 0
        
        volume_analysis = detector.analyze_request_volumes(sample_data)
        assert "total_requests" in volume_analysis
        assert volume_analysis["total_requests"] == len(sample_data)

    def test_failure_analysis_integration(self, sample_data):
        """Test failure analysis integration."""
        engine = AnalyticsEngine()
        
        for record in sample_data:
            engine.record_request(**record)
        
        analyzer = FailureAnalyzer(engine.config)
        
        # Get failure data
        failure_data = [r for r in sample_data if not r["success"]]
        assert len(failure_data) > 0
        
        # Analyze failures
        result = analyzer.analyze_failures(failure_data)
        
        assert result.total_failures == len(failure_data)
        assert result.total_clusters >= 0
        assert 0.0 <= result.clustering_effectiveness <= 1.0

    def test_multi_proxy_analysis(self, sample_data):
        """Test analysis across multiple proxies."""
        engine = AnalyticsEngine()
        
        for record in sample_data:
            engine.record_request(**record)
        
        proxy_metrics = engine.get_proxy_metrics()
        
        # Verify we have multiple proxies
        assert len(proxy_metrics) > 1
        
        # Verify each proxy has metrics
        for proxy_id, metrics in proxy_metrics.items():
            assert metrics.total_requests > 0
            assert 0.0 <= metrics.success_rate <= 1.0

    def test_time_range_filtering(self, sample_data):
        """Test time range filtering in queries."""
        engine = AnalyticsEngine()
        
        for record in sample_data:
            engine.record_request(**record)
        
        # Query recent data only
        recent_start = datetime.now() - timedelta(days=3)
        query = AnalyticsQuery(
            analysis_types=[AnalysisType.PERFORMANCE],
            start_time=recent_start,
            end_time=datetime.now(),
        )
        
        report = engine.analyze(query)
        assert report is not None

    def test_export_functionality(self, sample_data, tmp_path):
        """Test report export functionality."""
        engine = AnalyticsEngine()
        
        for record in sample_data:
            engine.record_request(**record)
        
        query = AnalyticsQuery(analysis_types=[AnalysisType.PERFORMANCE])
        report = engine.analyze(query)
        
        # Export to JSON
        from proxywhirl.analytics_models import ExportFormat
        output_path = str(tmp_path / "test_report.json")
        engine.export_report(report, ExportFormat.JSON, output_path)
        
        # Verify file was created
        import os
        assert os.path.exists(output_path)

    def test_cache_functionality(self, sample_data):
        """Test analytics caching."""
        config = AnalysisConfig(cache_results=True, cache_ttl_seconds=60)
        engine = AnalyticsEngine(config=config)
        
        for record in sample_data:
            engine.record_request(**record)
        
        query = AnalyticsQuery(analysis_types=[AnalysisType.PERFORMANCE])
        
        # First query - should compute
        report1 = engine.analyze(query)
        
        # Second query - should use cache
        report2 = engine.analyze(query)
        
        # Reports should have same ID (from cache)
        assert report1.report_id == report2.report_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
