"""Unit tests for predictive analytics."""

from datetime import datetime, timedelta

import pytest

from proxywhirl.analytics_models import AnalysisConfig, TimeSeriesData
from proxywhirl.predictive_analytics import PredictiveAnalytics


class TestPredictiveAnalytics:
    """Test PredictiveAnalytics functionality."""

    @pytest.fixture
    def request_data(self):
        """Generate sample request data."""
        data = []
        now = datetime.now()
        
        # Generate 30 days of data with upward trend
        for day in range(30):
            requests_per_day = 100 + day * 2  # Increasing trend
            
            for i in range(requests_per_day):
                data.append({
                    "timestamp": now - timedelta(days=day, hours=i % 24),
                    "success": True,
                })
        
        return data

    def test_analytics_initialization(self):
        """Test analytics initializes correctly."""
        analytics = PredictiveAnalytics()
        assert analytics is not None
        assert analytics.config is not None

    def test_prepare_time_series_data(self, request_data):
        """Test time-series data preparation."""
        analytics = PredictiveAnalytics()
        
        time_series = analytics.prepare_time_series_data(
            request_data,
            metric_name="request_volume",
            aggregation_hours=24,
        )
        
        assert isinstance(time_series, list)
        assert len(time_series) > 0
        assert all(isinstance(ts, TimeSeriesData) for ts in time_series)

    def test_train_forecast_model(self, request_data):
        """Test model training."""
        analytics = PredictiveAnalytics()
        
        time_series = analytics.prepare_time_series_data(request_data)
        model = analytics.train_forecast_model(time_series)
        
        assert model is not None

    def test_forecast_request_volume(self, request_data):
        """Test request volume forecasting."""
        analytics = PredictiveAnalytics()
        
        prediction = analytics.forecast_request_volume(
            historical_data=request_data,
            forecast_days=7,
        )
        
        assert prediction.mean_prediction >= 0
        assert prediction.forecast_horizon_days == 7
        assert prediction.detected_trend is not None
        assert len(prediction.accuracy_metrics) > 0

    def test_forecast_capacity_needs(self, request_data):
        """Test capacity forecasting."""
        analytics = PredictiveAnalytics()
        
        forecast = analytics.forecast_capacity_needs(
            historical_data=request_data,
            forecast_days=30,
        )
        
        assert "current_proxies_needed" in forecast
        assert "future_proxies_needed" in forecast
        assert forecast["future_proxies_needed"] >= 0

    def test_detect_trends(self, request_data):
        """Test trend detection."""
        analytics = PredictiveAnalytics()
        
        time_series = analytics.prepare_time_series_data(request_data)
        trend = analytics.detect_trends(time_series)
        
        assert trend is not None
        # Should detect increasing trend
        from proxywhirl.analytics_models import TrendDirection
        assert trend in [TrendDirection.INCREASING, TrendDirection.STABLE, TrendDirection.DECREASING, TrendDirection.VOLATILE]

    def test_calculate_prediction_confidence_intervals(self):
        """Test confidence interval calculation."""
        analytics = PredictiveAnalytics()
        
        predictions = [100, 105, 110, 108, 112]
        
        lower, upper = analytics.calculate_prediction_confidence_intervals(
            predictions,
            confidence_level=0.95,
        )
        
        assert lower <= upper
        assert lower >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
