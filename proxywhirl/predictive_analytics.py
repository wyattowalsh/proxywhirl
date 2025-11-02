"""
Predictive analytics for capacity planning.

Implements User Story 5: Predictive Analytics for Capacity
- Forecast future request volumes
- Predict capacity needs
- Detect trends (linear, exponential, seasonal)
- Generate capacity recommendations
"""

from datetime import datetime, timedelta
from typing import Any, Optional
from collections import defaultdict

import numpy as np
from loguru import logger

try:
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available, using basic forecasting methods")

from proxywhirl.analytics_models import (
    AnalysisConfig,
    Prediction,
    TimeSeriesData,
    TrendDirection,
)


class PredictiveAnalytics:
    """
    Provides predictive analytics for capacity planning.
    
    Example:
        ```python
        from proxywhirl import PredictiveAnalytics
        
        analytics = PredictiveAnalytics()
        
        # Forecast request volume
        prediction = analytics.forecast_request_volume(
            historical_data=requests,
            forecast_days=7
        )
        
        # Get capacity recommendations
        recommendations = prediction.capacity_recommendations
        ```
    """

    def __init__(self, config: Optional[AnalysisConfig] = None) -> None:
        """
        Initialize predictive analytics.
        
        Args:
            config: Analysis configuration
        """
        self.config = config or AnalysisConfig()
        self.models: dict[str, Any] = {}
        logger.info(
            "Predictive analytics initialized",
            sklearn_available=SKLEARN_AVAILABLE,
        )

    def prepare_time_series_data(
        self,
        request_data: list[dict[str, Any]],
        metric_name: str = "request_volume",
        aggregation_hours: int = 1,
    ) -> list[TimeSeriesData]:
        """
        Prepare time-series data for model input.
        
        Args:
            request_data: List of request records
            metric_name: Name of metric to extract
            aggregation_hours: Hours to aggregate data
            
        Returns:
            List of time-series data points
        """
        if not request_data:
            return []
        
        # Group by time window
        windows: dict[datetime, int] = defaultdict(int)
        for record in request_data:
            ts = record["timestamp"]
            # Round to aggregation window
            window_start = ts.replace(
                minute=0,
                second=0,
                microsecond=0,
            ) - timedelta(hours=ts.hour % aggregation_hours)
            windows[window_start] += 1
        
        # Convert to TimeSeriesData
        time_series = [
            TimeSeriesData(
                timestamp=ts,
                value=float(count),
                metric_name=metric_name,
            )
            for ts, count in sorted(windows.items())
        ]
        
        logger.info(
            "Prepared time-series data",
            data_points=len(time_series),
            metric=metric_name,
        )
        
        return time_series

    def train_forecast_model(
        self,
        time_series: list[TimeSeriesData],
        model_type: str = "linear",
    ) -> Any:
        """
        Train forecasting model.
        
        Args:
            time_series: Time-series data for training
            model_type: Type of model ("linear", "exponential")
            
        Returns:
            Trained model object
        """
        if not time_series or len(time_series) < 3:
            logger.warning("Insufficient data for model training")
            return None
        
        # Prepare features
        X = np.arange(len(time_series)).reshape(-1, 1)
        y = np.array([point.value for point in time_series])
        
        if SKLEARN_AVAILABLE and model_type == "linear":
            model = LinearRegression()
            model.fit(X, y)
            logger.info("Trained sklearn LinearRegression model")
        else:
            # Fallback: simple linear regression using numpy
            coeffs = np.polyfit(X.flatten(), y, 1)
            model = {"type": "numpy_linear", "coeffs": coeffs}
            logger.info("Trained numpy linear model")
        
        return model

    def forecast_request_volume(
        self,
        historical_data: list[dict[str, Any]],
        forecast_days: int = 7,
        aggregation_hours: int = 1,
    ) -> Prediction:
        """
        Forecast future request volumes.
        
        Args:
            historical_data: Historical request records
            forecast_days: Days to forecast
            aggregation_hours: Aggregation window
            
        Returns:
            Prediction with forecasted values
        """
        # Prepare time series
        time_series = self.prepare_time_series_data(
            historical_data,
            metric_name="request_volume",
            aggregation_hours=aggregation_hours,
        )
        
        if not time_series or len(time_series) < 3:
            # Return empty prediction
            return Prediction(
                metric_name="request_volume",
                forecast_horizon_days=forecast_days,
                mean_prediction=0.0,
                median_prediction=0.0,
                confidence_interval_lower=0.0,
                confidence_interval_upper=0.0,
                model_type="none",
                accuracy_metrics={},
                detected_trend=TrendDirection.STABLE,
                trained_on_data_points=0,
                training_period_start=datetime.now(),
                training_period_end=datetime.now(),
            )
        
        # Train model
        model = self.train_forecast_model(time_series, model_type="linear")
        
        # Make predictions
        X_train = np.arange(len(time_series))
        y_train = np.array([point.value for point in time_series])
        
        # Forecast future values
        forecast_hours = forecast_days * 24
        forecast_steps = forecast_hours // aggregation_hours
        X_future = np.arange(len(time_series), len(time_series) + forecast_steps).reshape(-1, 1)
        
        if SKLEARN_AVAILABLE and hasattr(model, "predict"):
            y_pred_train = model.predict(X_train.reshape(-1, 1))
            y_future = model.predict(X_future)
        else:
            # Numpy fallback
            coeffs = model["coeffs"]
            y_pred_train = np.polyval(coeffs, X_train)
            y_future = np.polyval(coeffs, X_future.flatten())
        
        # Calculate accuracy metrics on training data
        mae = float(mean_absolute_error(y_train, y_pred_train))
        rmse = float(np.sqrt(mean_squared_error(y_train, y_pred_train)))
        mape = float(np.mean(np.abs((y_train - y_pred_train) / (y_train + 1e-10))) * 100)
        
        accuracy_metrics = {
            "mae": mae,
            "rmse": rmse,
            "mape": mape,
        }
        
        # Generate prediction time series
        last_timestamp = time_series[-1].timestamp
        predictions: list[TimeSeriesData] = []
        
        for i, value in enumerate(y_future):
            future_time = last_timestamp + timedelta(hours=(i + 1) * aggregation_hours)
            predictions.append(
                TimeSeriesData(
                    timestamp=future_time,
                    value=float(max(0, value)),  # Ensure non-negative
                    metric_name="request_volume_forecast",
                )
            )
        
        # Calculate statistics
        future_values = [p.value for p in predictions]
        mean_pred = float(np.mean(future_values))
        median_pred = float(np.median(future_values))
        
        # Confidence intervals (simple approach: ?2 * RMSE)
        ci_lower = float(max(0, mean_pred - 2 * rmse))
        ci_upper = float(mean_pred + 2 * rmse)
        
        # Detect trend
        trend = self.detect_trends(time_series)
        
        # Generate capacity recommendations
        current_volume = float(np.mean(y_train[-7:]))  # Last 7 data points
        recommendations = self._generate_capacity_recommendations(
            current_volume, mean_pred, trend
        )
        
        # Estimate recommended pool size
        # Assume each proxy can handle ~100 requests/hour
        requests_per_hour = mean_pred / (forecast_days * 24 / aggregation_hours)
        recommended_pool_size = int(np.ceil(requests_per_hour / 100))
        
        prediction = Prediction(
            metric_name="request_volume",
            forecast_horizon_days=forecast_days,
            predictions=predictions,
            mean_prediction=mean_pred,
            median_prediction=median_pred,
            confidence_interval_lower=ci_lower,
            confidence_interval_upper=ci_upper,
            model_type="linear_regression" if SKLEARN_AVAILABLE else "numpy_linear",
            accuracy_metrics=accuracy_metrics,
            detected_trend=trend,
            seasonality_detected=False,  # Would need more sophisticated analysis
            capacity_recommendations=recommendations,
            recommended_pool_size=recommended_pool_size,
            trained_on_data_points=len(time_series),
            training_period_start=time_series[0].timestamp,
            training_period_end=time_series[-1].timestamp,
        )
        
        logger.info(
            "Generated forecast",
            forecast_days=forecast_days,
            mean_prediction=mean_pred,
            mape=f"{mape:.1f}%",
        )
        
        return prediction

    def forecast_capacity_needs(
        self,
        historical_data: list[dict[str, Any]],
        forecast_days: int = 30,
        target_utilization: float = 0.70,
    ) -> dict[str, Any]:
        """
        Forecast capacity requirements.
        
        Args:
            historical_data: Historical request data
            forecast_days: Days to forecast
            target_utilization: Target capacity utilization (0-1)
            
        Returns:
            Dictionary with capacity forecast
        """
        # Get volume forecast
        volume_prediction = self.forecast_request_volume(
            historical_data, forecast_days
        )
        
        # Calculate current capacity metrics
        current_requests = len(historical_data)
        time_span_hours = (
            max(r["timestamp"] for r in historical_data)
            - min(r["timestamp"] for r in historical_data)
        ).total_seconds() / 3600
        
        current_rate = current_requests / time_span_hours if time_span_hours > 0 else 0
        
        # Projected request rate
        projected_rate = volume_prediction.mean_prediction / (forecast_days * 24)
        
        # Calculate capacity needs
        # Assume each proxy handles 100 requests/hour at 100% utilization
        proxy_capacity = 100.0
        
        current_proxies_needed = int(np.ceil(current_rate / (proxy_capacity * target_utilization)))
        future_proxies_needed = int(np.ceil(projected_rate / (proxy_capacity * target_utilization)))
        
        capacity_change = future_proxies_needed - current_proxies_needed
        
        forecast = {
            "current_request_rate_per_hour": current_rate,
            "projected_request_rate_per_hour": projected_rate,
            "rate_change_percent": ((projected_rate / current_rate - 1) * 100) if current_rate > 0 else 0.0,
            "current_proxies_needed": current_proxies_needed,
            "future_proxies_needed": future_proxies_needed,
            "capacity_change": capacity_change,
            "target_utilization": target_utilization,
            "trend": volume_prediction.detected_trend,
            "confidence": 1.0 - (volume_prediction.accuracy_metrics.get("mape", 100) / 100),
        }
        
        logger.info(
            "Forecasted capacity needs",
            future_proxies_needed=future_proxies_needed,
            capacity_change=capacity_change,
        )
        
        return forecast

    def detect_trends(
        self,
        time_series: list[TimeSeriesData],
    ) -> TrendDirection:
        """
        Detect trend direction in time series.
        
        Args:
            time_series: Time-series data
            
        Returns:
            Detected trend direction
        """
        if len(time_series) < 3:
            return TrendDirection.STABLE
        
        values = np.array([point.value for point in time_series])
        x = np.arange(len(values))
        
        # Linear regression for trend
        slope = np.polyfit(x, values, 1)[0]
        
        # Calculate relative slope
        mean_value = np.mean(values)
        relative_slope = slope / mean_value if mean_value > 0 else 0
        
        # Determine trend
        if relative_slope > 0.05:  # 5% increase per period
            return TrendDirection.INCREASING
        elif relative_slope < -0.05:
            return TrendDirection.DECREASING
        else:
            # Check volatility
            cv = np.std(values) / mean_value if mean_value > 0 else 0
            if cv > 0.5:  # High coefficient of variation
                return TrendDirection.VOLATILE
            return TrendDirection.STABLE

    def calculate_prediction_confidence_intervals(
        self,
        predictions: list[float],
        confidence_level: float = 0.95,
    ) -> tuple[float, float]:
        """
        Calculate confidence intervals for predictions.
        
        Args:
            predictions: Array of predicted values
            confidence_level: Confidence level (0-1)
            
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        if not predictions:
            return (0.0, 0.0)
        
        predictions_array = np.array(predictions)
        mean = np.mean(predictions_array)
        std = np.std(predictions_array)
        
        # Z-score for confidence level
        if confidence_level == 0.95:
            z_score = 1.96
        elif confidence_level == 0.99:
            z_score = 2.58
        else:
            z_score = 1.96
        
        margin = z_score * std
        
        return (float(mean - margin), float(mean + margin))

    def _generate_capacity_recommendations(
        self,
        current_volume: float,
        predicted_volume: float,
        trend: TrendDirection,
    ) -> list[str]:
        """Generate capacity planning recommendations."""
        recommendations: list[str] = []
        
        change_percent = (
            ((predicted_volume / current_volume - 1) * 100)
            if current_volume > 0
            else 0.0
        )
        
        if trend == TrendDirection.INCREASING:
            if change_percent > 50:
                recommendations.append(
                    f"Significant volume increase expected (+{change_percent:.0f}%) - "
                    "Consider proactive capacity expansion"
                )
            elif change_percent > 20:
                recommendations.append(
                    f"Moderate volume increase expected (+{change_percent:.0f}%) - "
                    "Plan gradual capacity scaling"
                )
            else:
                recommendations.append(
                    "Slight volume increase - Current capacity likely sufficient with monitoring"
                )
        
        elif trend == TrendDirection.DECREASING:
            if change_percent < -30:
                recommendations.append(
                    f"Significant volume decrease expected ({change_percent:.0f}%) - "
                    "Consider reducing proxy pool to optimize costs"
                )
            else:
                recommendations.append(
                    "Volume decrease detected - Monitor for cost optimization opportunities"
                )
        
        elif trend == TrendDirection.VOLATILE:
            recommendations.append(
                "High volatility detected - Implement auto-scaling policies to handle spikes"
            )
            recommendations.append(
                "Consider maintaining buffer capacity for unexpected surges"
            )
        
        else:  # STABLE
            recommendations.append(
                "Stable volume trend - Current capacity planning appears adequate"
            )
        
        recommendations.append(
            "Review forecast accuracy monthly and adjust capacity plans accordingly"
        )
        
        return recommendations


__all__ = [
    "PredictiveAnalytics",
]
