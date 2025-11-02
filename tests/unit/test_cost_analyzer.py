"""Unit tests for cost analyzer."""

from datetime import datetime, timedelta

import pytest

from proxywhirl.analytics_models import AnalysisConfig, CostMetrics
from proxywhirl.cost_analyzer import CostAnalyzer


class TestCostAnalyzer:
    """Test CostAnalyzer functionality."""

    @pytest.fixture
    def request_data(self):
        """Generate sample request data."""
        data = []
        now = datetime.now()
        
        for i in range(100):
            data.append({
                "proxy_id": f"proxy-{i % 3}",
                "success": (i % 5 != 0),  # 80% success
                "timestamp": now - timedelta(hours=i),
            })
        
        return data

    def test_analyzer_initialization(self):
        """Test analyzer initializes correctly."""
        analyzer = CostAnalyzer()
        assert analyzer is not None
        assert analyzer.config is not None

    def test_calculate_cost_per_request(self):
        """Test cost per request calculation."""
        analyzer = CostAnalyzer()
        
        cost = analyzer.calculate_cost_per_request(
            total_cost=100.0,
            total_requests=1000,
        )
        
        assert cost == 0.1

    def test_calculate_cost_per_successful_request(self):
        """Test cost per successful request."""
        analyzer = CostAnalyzer()
        
        cost = analyzer.calculate_cost_per_successful_request(
            total_cost=100.0,
            successful_requests=800,
        )
        
        assert cost == 0.125

    def test_calculate_cost_metrics(self, request_data):
        """Test comprehensive cost metrics."""
        analyzer = CostAnalyzer()
        
        metrics = analyzer.calculate_cost_metrics(
            total_cost=150.0,
            request_data=request_data,
            source="test-source",
        )
        
        assert isinstance(metrics, CostMetrics)
        assert metrics.total_cost == 150.0
        assert metrics.total_requests == 100
        assert metrics.cost_per_request > 0
        assert 0.0 <= metrics.cost_efficiency_score <= 1.0

    def test_compare_source_cost_effectiveness(self):
        """Test source comparison."""
        analyzer = CostAnalyzer()
        
        metrics_list = [
            CostMetrics(
                total_cost=100.0,
                cost_per_request=0.1,
                cost_per_successful_request=0.125,
                total_requests=1000,
                successful_requests=800,
                cost_efficiency_score=0.8,
                source="source-1",
                period_start=datetime.now(),
                period_end=datetime.now(),
            ),
            CostMetrics(
                total_cost=150.0,
                cost_per_request=0.15,
                cost_per_successful_request=0.2,
                total_requests=1000,
                successful_requests=750,
                cost_efficiency_score=0.6,
                source="source-2",
                period_start=datetime.now(),
                period_end=datetime.now(),
            ),
        ]
        
        ranked = analyzer.compare_source_cost_effectiveness(metrics_list)
        
        assert len(ranked) == 2
        assert ranked[0].source == "source-1"  # Better efficiency
        assert ranked[0].rank_by_cost_effectiveness == 1

    def test_calculate_roi_metrics(self, request_data):
        """Test ROI calculation."""
        analyzer = CostAnalyzer()
        
        roi = analyzer.calculate_roi_metrics(
            total_cost=100.0,
            request_data=request_data,
            value_per_successful_request=2.0,
        )
        
        assert "roi_percent" in roi
        assert "total_value" in roi
        assert "profit" in roi

    def test_project_future_costs(self):
        """Test cost forecasting."""
        analyzer = CostAnalyzer()
        
        historical_data = [
            (datetime.now() - timedelta(days=i), 10.0 + i)
            for i in range(30)
        ]
        
        forecast = analyzer.project_future_costs(
            historical_cost_data=historical_data,
            forecast_days=7,
        )
        
        assert forecast.projected_total_cost >= 0
        assert forecast.trend is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
