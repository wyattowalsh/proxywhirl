"""
Unit tests for analytics data models.

Tests all Pydantic models used in the analytics engine.
"""

from datetime import datetime, timedelta
from uuid import UUID

import pytest

from proxywhirl.analytics_models import (
    AnalysisConfig,
    AnalysisReport,
    AnalysisType,
    AnalyticsQuery,
    Anomaly,
    AnomalyType,
    ExportFormat,
    FailureCluster,
    PerformanceScore,
    Prediction,
    ProxyPerformanceMetrics,
    Recommendation,
    RecommendationPriority,
    TimeSeriesData,
    TrendDirection,
    UsagePattern,
)


class TestProxyPerformanceMetrics:
    """Test ProxyPerformanceMetrics model."""

    def test_create_default_metrics(self) -> None:
        """Test creating metrics with default values."""
        metrics = ProxyPerformanceMetrics(
            proxy_id="test-proxy-1",
            proxy_url="http://proxy.example.com:8080",
        )
        
        assert metrics.proxy_id == "test-proxy-1"
        assert metrics.total_requests == 0
        assert metrics.success_rate == 0.0
        assert metrics.avg_latency_ms == 0.0
        assert metrics.uptime_percentage == 100.0

    def test_update_metrics(self) -> None:
        """Test updating metrics values."""
        metrics = ProxyPerformanceMetrics(
            proxy_id="test-proxy-1",
            proxy_url="http://proxy.example.com:8080",
        )
        
        metrics.total_requests = 100
        metrics.successful_requests = 95
        metrics.success_rate = 0.95
        
        assert metrics.total_requests == 100
        assert metrics.successful_requests == 95
        assert metrics.success_rate == 0.95

    def test_metrics_with_region_and_pool(self) -> None:
        """Test metrics with optional fields."""
        metrics = ProxyPerformanceMetrics(
            proxy_id="test-proxy-1",
            proxy_url="http://proxy.example.com:8080",
            pool="production",
            region="us-east-1",
        )
        
        assert metrics.pool == "production"
        assert metrics.region == "us-east-1"


class TestPerformanceScore:
    """Test PerformanceScore model."""

    def test_create_performance_score(self) -> None:
        """Test creating a performance score."""
        score = PerformanceScore(
            proxy_id="test-proxy-1",
            overall_score=85.5,
            success_rate_score=90.0,
            latency_score=80.0,
            uptime_score=87.0,
            reliability_score=85.0,
        )
        
        assert score.proxy_id == "test-proxy-1"
        assert score.overall_score == 85.5
        assert score.success_rate_score == 90.0

    def test_score_bounds(self) -> None:
        """Test that scores are bounded 0-100."""
        with pytest.raises(ValueError):
            PerformanceScore(
                proxy_id="test",
                overall_score=150.0,  # Out of bounds
                success_rate_score=90.0,
                latency_score=80.0,
                uptime_score=87.0,
                reliability_score=85.0,
            )

    def test_frozen_score(self) -> None:
        """Test that scores are immutable."""
        score = PerformanceScore(
            proxy_id="test-proxy-1",
            overall_score=85.5,
            success_rate_score=90.0,
            latency_score=80.0,
            uptime_score=87.0,
            reliability_score=85.0,
        )
        
        # Cannot modify frozen model
        with pytest.raises(Exception):  # ValidationError in Pydantic v2
            score.overall_score = 95.0  # type: ignore


class TestUsagePattern:
    """Test UsagePattern model."""

    def test_create_usage_pattern(self) -> None:
        """Test creating a usage pattern."""
        now = datetime.now()
        pattern = UsagePattern(
            pattern_type="peak_hours",
            description="Peak usage during business hours",
            peak_hours=[9, 10, 11, 14, 15, 16],
            start_time=now - timedelta(days=7),
            end_time=now,
        )
        
        assert pattern.pattern_type == "peak_hours"
        assert len(pattern.peak_hours or []) == 6
        assert isinstance(pattern.pattern_id, UUID)

    def test_pattern_with_geographic_data(self) -> None:
        """Test pattern with geographic information."""
        now = datetime.now()
        pattern = UsagePattern(
            pattern_type="geographic",
            description="Regional distribution",
            top_regions={"us-east-1": 1000, "eu-west-1": 500},
            confidence=0.9,
            start_time=now - timedelta(days=7),
            end_time=now,
        )
        
        assert pattern.top_regions is not None
        assert pattern.top_regions["us-east-1"] == 1000
        assert pattern.confidence == 0.9


class TestFailureCluster:
    """Test FailureCluster model."""

    def test_create_failure_cluster(self) -> None:
        """Test creating a failure cluster."""
        now = datetime.now()
        cluster = FailureCluster(
            cluster_name="Timeout Errors",
            common_error_types=["timeout"],
            failure_count=50,
            affected_proxies=5,
            failure_rate=0.15,
            first_failure=now - timedelta(hours=2),
            last_failure=now,
        )
        
        assert cluster.cluster_name == "Timeout Errors"
        assert cluster.failure_count == 50
        assert isinstance(cluster.cluster_id, UUID)


class TestPrediction:
    """Test Prediction model."""

    def test_create_prediction(self) -> None:
        """Test creating a prediction."""
        now = datetime.now()
        prediction = Prediction(
            metric_name="request_volume",
            predicted_value=10000.0,
            lower_bound=9000.0,
            upper_bound=11000.0,
            confidence_level=0.95,
            prediction_horizon_days=7,
            model_name="linear_regression",
            prediction_date=now + timedelta(days=7),
        )
        
        assert prediction.metric_name == "request_volume"
        assert prediction.predicted_value == 10000.0
        assert prediction.lower_bound < prediction.predicted_value < prediction.upper_bound


class TestRecommendation:
    """Test Recommendation model."""

    def test_create_recommendation(self) -> None:
        """Test creating a recommendation."""
        rec = Recommendation(
            title="Scale proxy pool",
            description="Increase capacity by 50%",
            priority=RecommendationPriority.HIGH,
            category="capacity",
            estimated_improvement="50% capacity increase",
            affected_proxies=["proxy-1", "proxy-2"],
        )
        
        assert rec.title == "Scale proxy pool"
        assert rec.priority == RecommendationPriority.HIGH
        assert len(rec.affected_proxies) == 2


class TestAnomaly:
    """Test Anomaly model."""

    def test_create_anomaly(self) -> None:
        """Test creating an anomaly."""
        now = datetime.now()
        anomaly = Anomaly(
            anomaly_type=AnomalyType.USAGE_SPIKE,
            description="Unusual traffic spike",
            severity=0.8,
            expected_value=1000.0,
            actual_value=5000.0,
            deviation=3.5,
            time_period_start=now - timedelta(hours=1),
            time_period_end=now,
        )
        
        assert anomaly.anomaly_type == AnomalyType.USAGE_SPIKE
        assert anomaly.severity == 0.8
        assert anomaly.deviation == 3.5


class TestAnalysisReport:
    """Test AnalysisReport model."""

    def test_create_analysis_report(self) -> None:
        """Test creating a comprehensive analysis report."""
        now = datetime.now()
        report = AnalysisReport(
            report_title="Performance Analysis",
            analysis_type=AnalysisType.PERFORMANCE,
            period_start=now - timedelta(days=30),
            period_end=now,
            executive_summary="Overall performance is good",
            key_findings=["Finding 1", "Finding 2"],
        )
        
        assert report.report_title == "Performance Analysis"
        assert report.analysis_type == AnalysisType.PERFORMANCE
        assert len(report.key_findings) == 2
        assert isinstance(report.report_id, UUID)

    def test_report_with_all_components(self) -> None:
        """Test report with all optional components."""
        now = datetime.now()
        
        metrics = ProxyPerformanceMetrics(
            proxy_id="proxy-1",
            proxy_url="http://proxy.example.com:8080",
        )
        
        score = PerformanceScore(
            proxy_id="proxy-1",
            overall_score=85.0,
            success_rate_score=90.0,
            latency_score=80.0,
            uptime_score=87.0,
            reliability_score=85.0,
        )
        
        report = AnalysisReport(
            report_title="Comprehensive Analysis",
            analysis_type=AnalysisType.COMPREHENSIVE,
            period_start=now - timedelta(days=30),
            period_end=now,
            executive_summary="Comprehensive analysis complete",
            key_findings=["Finding 1"],
            performance_metrics={"proxy-1": metrics},
            performance_scores={"proxy-1": score},
            total_requests_analyzed=10000,
            total_proxies_analyzed=1,
        )
        
        assert report.performance_metrics is not None
        assert report.performance_scores is not None
        assert report.total_requests_analyzed == 10000


class TestAnalysisConfig:
    """Test AnalysisConfig model."""

    def test_default_config(self) -> None:
        """Test creating config with default values."""
        config = AnalysisConfig()
        
        assert config.lookback_days == 30
        assert config.min_success_rate == 0.7
        assert config.cache_results is True

    def test_custom_config(self) -> None:
        """Test creating config with custom values."""
        config = AnalysisConfig(
            lookback_days=60,
            min_success_rate=0.8,
            max_avg_latency_ms=3000.0,
            cache_results=False,
        )
        
        assert config.lookback_days == 60
        assert config.min_success_rate == 0.8
        assert config.max_avg_latency_ms == 3000.0
        assert config.cache_results is False

    def test_config_validation(self) -> None:
        """Test config value validation."""
        with pytest.raises(ValueError):
            AnalysisConfig(min_success_rate=1.5)  # Out of bounds

    def test_weight_configuration(self) -> None:
        """Test performance scoring weights."""
        config = AnalysisConfig(
            success_rate_weight=0.5,
            latency_weight=0.3,
            uptime_weight=0.2,
        )
        
        # Weights should sum to 1.0
        total_weight = (
            config.success_rate_weight +
            config.latency_weight +
            config.uptime_weight
        )
        assert abs(total_weight - 1.0) < 0.01


class TestAnalyticsQuery:
    """Test AnalyticsQuery model."""

    def test_default_query(self) -> None:
        """Test creating query with default values."""
        query = AnalyticsQuery()
        
        assert AnalysisType.PERFORMANCE in query.analysis_types
        assert query.include_recommendations is True
        assert query.top_n_performers == 10

    def test_custom_query(self) -> None:
        """Test creating query with custom values."""
        now = datetime.now()
        query = AnalyticsQuery(
            start_time=now - timedelta(days=7),
            end_time=now,
            proxy_ids=["proxy-1", "proxy-2"],
            pools=["production"],
            analysis_types=[AnalysisType.PERFORMANCE, AnalysisType.COST_ANALYSIS],
        )
        
        assert query.proxy_ids == ["proxy-1", "proxy-2"]
        assert query.pools == ["production"]
        assert len(query.analysis_types) == 2


class TestEnums:
    """Test enum definitions."""

    def test_analysis_type_enum(self) -> None:
        """Test AnalysisType enum values."""
        assert AnalysisType.PERFORMANCE == "performance"
        assert AnalysisType.USAGE_PATTERNS == "usage_patterns"
        assert AnalysisType.COMPREHENSIVE == "comprehensive"

    def test_export_format_enum(self) -> None:
        """Test ExportFormat enum values."""
        assert ExportFormat.JSON == "json"
        assert ExportFormat.CSV == "csv"
        assert ExportFormat.PDF == "pdf"

    def test_trend_direction_enum(self) -> None:
        """Test TrendDirection enum values."""
        assert TrendDirection.INCREASING == "increasing"
        assert TrendDirection.DECREASING == "decreasing"
        assert TrendDirection.STABLE == "stable"
        assert TrendDirection.VOLATILE == "volatile"

    def test_recommendation_priority_enum(self) -> None:
        """Test RecommendationPriority enum values."""
        assert RecommendationPriority.CRITICAL == "critical"
        assert RecommendationPriority.HIGH == "high"
        assert RecommendationPriority.MEDIUM == "medium"
        assert RecommendationPriority.LOW == "low"

    def test_anomaly_type_enum(self) -> None:
        """Test AnomalyType enum values."""
        assert AnomalyType.USAGE_SPIKE == "usage_spike"
        assert AnomalyType.USAGE_DROP == "usage_drop"
        assert AnomalyType.FAILURE_SPIKE == "failure_spike"
