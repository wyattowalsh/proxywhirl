"""
Predictive analytics for ProxyWhirl analytics engine.

Provides forecasting and predictive modeling for capacity planning.
"""

import statistics
from datetime import datetime, timedelta
from typing import Any, Optional

try:
    import numpy as np
    from sklearn.linear_model import LinearRegression
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    np = None  # type: ignore
    LinearRegression = None  # type: ignore

from loguru import logger

from proxywhirl.analytics_models import (
    AnalysisConfig,
    Prediction,
    Recommendation,
    RecommendationPriority,
    TrendDirection,
)


class PredictiveAnalytics:
    """
    Provides predictive analytics and forecasting capabilities.
    
    Forecasts future metrics like request volume and capacity needs using
    statistical and machine learning models.
    
    Example:
        ```python
        from proxywhirl import PredictiveAnalytics, AnalysisConfig
        
        predictor = PredictiveAnalytics(config=AnalysisConfig())
        
        # Forecast request volume
        prediction = predictor.forecast_request_volume(historical_data)
        
        # Forecast capacity needs
        capacity = predictor.forecast_capacity_needs(historical_data)
        
        # Generate recommendations
        recommendations = predictor.generate_capacity_recommendations(prediction)
        ```
    """

    def __init__(self, config: Optional[AnalysisConfig] = None) -> None:
        """
        Initialize predictive analytics.
        
        Args:
            config: Analysis configuration (default: AnalysisConfig())
        """
        self.config = config or AnalysisConfig()
        self.use_ml = SKLEARN_AVAILABLE
        
        if not self.use_ml:
            logger.warning(
                "scikit-learn not available, using statistical forecasting only"
            )
        
        logger.debug("Predictive analytics initialized", use_ml=self.use_ml)

    def prepare_time_series_data(
        self,
        data_points: list[tuple[datetime, float]],
    ) -> tuple[list[float], list[float]]:
        """
        Prepare time-series data for model training.
        
        Args:
            data_points: List of (timestamp, value) tuples
            
        Returns:
            Tuple of (X, y) where X is time indices and y is values
        """
        if not data_points:
            raise ValueError("No data points provided")
        
        # Sort by timestamp
        sorted_data = sorted(data_points, key=lambda x: x[0])
        
        # Convert to numerical representation
        base_time = sorted_data[0][0]
        
        X = []
        y = []
        
        for timestamp, value in sorted_data:
            # Convert timestamp to days since base
            days_since_base = (timestamp - base_time).total_seconds() / 86400
            X.append(days_since_base)
            y.append(value)
        
        return X, y

    def forecast_request_volume(
        self,
        historical_data: list[tuple[datetime, float]],
        forecast_days: Optional[int] = None,
    ) -> Prediction:
        """
        Forecast future request volume.
        
        Args:
            historical_data: List of (date, request_count) tuples
            forecast_days: Days to forecast (default: from config)
            
        Returns:
            Prediction with forecasted request volume
        """
        forecast_days = forecast_days or self.config.prediction_horizon_days
        
        if len(historical_data) < self.config.min_training_days:
            raise ValueError(
                f"Insufficient training data: {len(historical_data)} days, "
                f"need at least {self.config.min_training_days} days"
            )
        
        X, y = self.prepare_time_series_data(historical_data)
        
        if self.use_ml and np is not None and LinearRegression is not None:
            # Use ML-based forecasting
            predicted_value, confidence_interval = self._ml_forecast(
                X, y, forecast_days
            )
        else:
            # Use statistical forecasting
            predicted_value, confidence_interval = self._statistical_forecast(
                X, y, forecast_days
            )
        
        last_date = historical_data[-1][0]
        forecast_date = last_date + timedelta(days=forecast_days)
        
        prediction = Prediction(
            metric_name="request_volume",
            predicted_value=max(0.0, predicted_value),
            lower_bound=max(0.0, confidence_interval[0]),
            upper_bound=confidence_interval[1],
            confidence_level=self.config.prediction_confidence,
            prediction_horizon_days=forecast_days,
            model_name="linear_regression" if self.use_ml else "statistical_trend",
            model_accuracy=self._estimate_model_accuracy(X, y),
            prediction_date=forecast_date,
        )
        
        logger.info(
            f"Forecasted request volume for {forecast_days} days: "
            f"{predicted_value:.0f} requests"
        )
        return prediction

    def _ml_forecast(
        self,
        X: list[float],
        y: list[float],
        forecast_days: int,
    ) -> tuple[float, tuple[float, float]]:
        """Forecast using machine learning (scikit-learn)."""
        if not SKLEARN_AVAILABLE or np is None or LinearRegression is None:
            return self._statistical_forecast(X, y, forecast_days)
        
        # Prepare data
        X_train = np.array(X).reshape(-1, 1)
        y_train = np.array(y)
        
        # Train model
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Predict
        forecast_x = X[-1] + forecast_days
        forecast_point = np.array([[forecast_x]])
        predicted_value = float(model.predict(forecast_point)[0])
        
        # Calculate confidence interval using residuals
        predictions = model.predict(X_train)
        residuals = y_train - predictions
        std_error = float(np.std(residuals))
        
        margin = 1.96 * std_error  # 95% confidence interval
        confidence_interval = (
            predicted_value - margin,
            predicted_value + margin,
        )
        
        return predicted_value, confidence_interval

    def _statistical_forecast(
        self,
        X: list[float],
        y: list[float],
        forecast_days: int,
    ) -> tuple[float, tuple[float, float]]:
        """Forecast using statistical methods."""
        # Simple linear trend
        if len(X) < 2:
            # Not enough data for trend
            avg_value = statistics.mean(y)
            return avg_value, (avg_value * 0.8, avg_value * 1.2)
        
        # Calculate trend (slope)
        x_mean = statistics.mean(X)
        y_mean = statistics.mean(y)
        
        numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(X, y))
        denominator = sum((xi - x_mean) ** 2 for xi in X)
        
        if denominator == 0:
            # No trend
            avg_value = y_mean
            return avg_value, (avg_value * 0.8, avg_value * 1.2)
        
        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        
        # Forecast
        forecast_x = X[-1] + forecast_days
        predicted_value = slope * forecast_x + intercept
        
        # Confidence interval (?20%)
        margin = abs(predicted_value) * 0.2
        confidence_interval = (
            predicted_value - margin,
            predicted_value + margin,
        )
        
        return predicted_value, confidence_interval

    def _estimate_model_accuracy(
        self,
        X: list[float],
        y: list[float],
    ) -> float:
        """Estimate model accuracy using simple validation."""
        if len(X) < 4:
            return 0.7  # Default moderate accuracy
        
        # Use last 20% as validation
        split_idx = int(len(X) * 0.8)
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        # Simple trend-based prediction
        predictions = []
        for x_val in X_val:
            pred, _ = self._statistical_forecast(X_train, y_train, int(x_val - X_train[-1]))
            predictions.append(pred)
        
        # Calculate accuracy (1 - MAPE)
        if not predictions or not y_val:
            return 0.7
        
        errors = [abs(pred - actual) / max(actual, 1) for pred, actual in zip(predictions, y_val)]
        mape = statistics.mean(errors)
        accuracy = max(0.0, 1.0 - mape)
        
        return min(1.0, accuracy)

    def forecast_capacity_needs(
        self,
        historical_data: list[tuple[datetime, float]],
        current_capacity: int,
        forecast_days: Optional[int] = None,
    ) -> Prediction:
        """
        Forecast future capacity needs based on request volume trends.
        
        Args:
            historical_data: Historical request volume data
            current_capacity: Current proxy pool capacity
            forecast_days: Days to forecast
            
        Returns:
            Prediction with recommended capacity
        """
        # First forecast request volume
        volume_prediction = self.forecast_request_volume(
            historical_data,
            forecast_days,
        )
        
        # Estimate capacity needs (with 20% buffer)
        predicted_capacity = volume_prediction.predicted_value * 1.2
        
        forecast_date = volume_prediction.prediction_date
        
        prediction = Prediction(
            metric_name="required_proxy_capacity",
            predicted_value=max(current_capacity, predicted_capacity),
            lower_bound=volume_prediction.lower_bound * 1.1,
            upper_bound=volume_prediction.upper_bound * 1.3,
            confidence_level=volume_prediction.confidence_level,
            prediction_horizon_days=volume_prediction.prediction_horizon_days,
            model_name=volume_prediction.model_name,
            model_accuracy=volume_prediction.model_accuracy,
            prediction_date=forecast_date,
        )
        
        logger.info(
            f"Forecasted capacity needs: {predicted_capacity:.0f} proxies "
            f"(current: {current_capacity})"
        )
        return prediction

    def detect_trends(
        self,
        data_points: list[tuple[datetime, float]],
    ) -> tuple[TrendDirection, float]:
        """
        Detect trend direction and strength in time-series data.
        
        Args:
            data_points: List of (timestamp, value) tuples
            
        Returns:
            Tuple of (TrendDirection, trend_strength)
        """
        if len(data_points) < 3:
            return TrendDirection.STABLE, 0.0
        
        X, y = self.prepare_time_series_data(data_points)
        
        # Calculate trend slope
        if len(X) < 2:
            return TrendDirection.STABLE, 0.0
        
        x_mean = statistics.mean(X)
        y_mean = statistics.mean(y)
        
        numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(X, y))
        denominator = sum((xi - x_mean) ** 2 for xi in X)
        
        if denominator == 0:
            return TrendDirection.STABLE, 0.0
        
        slope = numerator / denominator
        
        # Normalize slope by mean value
        if y_mean != 0:
            normalized_slope = slope / y_mean
        else:
            normalized_slope = 0.0
        
        # Determine direction and strength
        if abs(normalized_slope) < 0.01:
            return TrendDirection.STABLE, abs(normalized_slope)
        elif normalized_slope > 0.05:
            return TrendDirection.INCREASING, normalized_slope
        elif normalized_slope < -0.05:
            return TrendDirection.DECREASING, abs(normalized_slope)
        else:
            # Check volatility
            std_dev = statistics.stdev(y) if len(y) > 1 else 0
            if std_dev > y_mean * 0.3:
                return TrendDirection.VOLATILE, std_dev / y_mean
            return TrendDirection.STABLE, abs(normalized_slope)

    def generate_capacity_recommendations(
        self,
        capacity_prediction: Prediction,
        current_capacity: int,
    ) -> list[Recommendation]:
        """
        Generate capacity planning recommendations.
        
        Args:
            capacity_prediction: Predicted capacity needs
            current_capacity: Current proxy pool capacity
            
        Returns:
            List of capacity recommendations
        """
        recommendations: list[Recommendation] = []
        
        predicted_need = capacity_prediction.predicted_value
        capacity_gap = predicted_need - current_capacity
        
        if capacity_gap > current_capacity * 0.2:
            # Significant capacity increase needed
            recommendations.append(
                Recommendation(
                    title="Scale Up Proxy Capacity",
                    description=(
                        f"Predicted capacity needs ({predicted_need:.0f} proxies) "
                        f"exceed current capacity ({current_capacity} proxies) by "
                        f"{capacity_gap:.0f} proxies. Scale up to meet demand."
                    ),
                    priority=RecommendationPriority.HIGH,
                    category="capacity_planning",
                    estimated_improvement=f"Meet {predicted_need:.0f} proxy capacity needs",
                    estimated_effort="High - procurement and deployment required",
                    affected_proxies=[],
                    supporting_data={
                        "current_capacity": current_capacity,
                        "predicted_need": predicted_need,
                        "capacity_gap": capacity_gap,
                    },
                )
            )
        elif capacity_gap < -current_capacity * 0.3:
            # Significant over-capacity
            recommendations.append(
                Recommendation(
                    title="Optimize Proxy Pool Size",
                    description=(
                        f"Current capacity ({current_capacity} proxies) significantly "
                        f"exceeds predicted needs ({predicted_need:.0f} proxies). "
                        f"Consider reducing pool size for cost savings."
                    ),
                    priority=RecommendationPriority.MEDIUM,
                    category="capacity_planning",
                    estimated_improvement=f"Reduce costs by {abs(capacity_gap):.0f} proxies",
                    estimated_effort="Medium - gradual capacity reduction",
                    affected_proxies=[],
                    supporting_data={
                        "current_capacity": current_capacity,
                        "predicted_need": predicted_need,
                        "excess_capacity": abs(capacity_gap),
                    },
                )
            )
        
        logger.info(f"Generated {len(recommendations)} capacity recommendations")
        return recommendations
