"""
Cost analyzer for ProxyWhirl analytics engine.

Analyzes proxy costs, ROI metrics, and provides cost optimization recommendations.
"""

import statistics
from datetime import datetime, timedelta
from typing import Any, Optional

from loguru import logger

from proxywhirl.analytics_models import (
    AnalysisConfig,
    Prediction,
    Recommendation,
    RecommendationPriority,
)


class CostAnalyzer:
    """
    Analyzes proxy costs and ROI metrics.
    
    Calculates cost per request, cost effectiveness, and provides
    cost optimization recommendations.
    
    Example:
        ```python
        from proxywhirl import CostAnalyzer, AnalysisConfig
        
        analyzer = CostAnalyzer(config=AnalysisConfig())
        
        # Calculate cost metrics
        cost_per_request = analyzer.calculate_cost_per_request(
            total_cost=100.0,
            total_requests=10000
        )
        
        # Compare sources
        comparison = analyzer.compare_source_cost_effectiveness(cost_data)
        
        # Forecast costs
        prediction = analyzer.project_future_costs(historical_costs)
        ```
    """

    def __init__(self, config: Optional[AnalysisConfig] = None) -> None:
        """
        Initialize cost analyzer.
        
        Args:
            config: Analysis configuration (default: AnalysisConfig())
        """
        self.config = config or AnalysisConfig()
        logger.debug("Cost analyzer initialized")

    def calculate_cost_per_request(
        self,
        total_cost: float,
        total_requests: int,
    ) -> float:
        """
        Calculate average cost per request.
        
        Args:
            total_cost: Total proxy costs in dollars
            total_requests: Total number of requests
            
        Returns:
            Cost per request in dollars
        """
        if total_requests == 0:
            return 0.0
        return total_cost / total_requests

    def calculate_cost_per_successful_request(
        self,
        total_cost: float,
        successful_requests: int,
    ) -> float:
        """
        Calculate cost per successful request.
        
        Args:
            total_cost: Total proxy costs in dollars
            successful_requests: Number of successful requests
            
        Returns:
            Cost per successful request in dollars
        """
        if successful_requests == 0:
            return float("inf")
        return total_cost / successful_requests

    def compare_source_cost_effectiveness(
        self,
        source_data: dict[str, dict[str, Any]],
    ) -> dict[str, dict[str, float]]:
        """
        Compare cost effectiveness across proxy sources.
        
        Args:
            source_data: Dictionary of source_name -> {cost, requests, successes}
            
        Returns:
            Dictionary with cost effectiveness metrics per source
        """
        comparison: dict[str, dict[str, float]] = {}
        
        for source_name, data in source_data.items():
            cost = data.get("cost", 0.0)
            requests = data.get("requests", 0)
            successes = data.get("successes", 0)
            
            comparison[source_name] = {
                "cost_per_request": self.calculate_cost_per_request(cost, requests),
                "cost_per_successful_request": self.calculate_cost_per_successful_request(
                    cost, successes
                ),
                "success_rate": successes / requests if requests > 0 else 0.0,
                "total_cost": cost,
                "roi_score": self._calculate_roi_score(cost, requests, successes),
            }
        
        logger.info(f"Compared cost effectiveness across {len(source_data)} sources")
        return comparison

    def _calculate_roi_score(
        self,
        cost: float,
        requests: int,
        successes: int,
    ) -> float:
        """
        Calculate ROI score (higher is better).
        
        Score = (successes / cost) * 100 if cost > 0, else 0
        """
        if cost <= 0 or successes == 0:
            return 0.0
        return (successes / cost) * 100.0

    def calculate_roi_metrics(
        self,
        cost: float,
        revenue: float,
        requests: int,
        successes: int,
    ) -> dict[str, float]:
        """
        Calculate comprehensive ROI metrics.
        
        Args:
            cost: Total proxy costs
            revenue: Revenue generated from successful requests
            requests: Total requests
            successes: Successful requests
            
        Returns:
            Dictionary with ROI metrics
        """
        roi_percentage = ((revenue - cost) / cost * 100) if cost > 0 else 0.0
        profit = revenue - cost
        
        return {
            "roi_percentage": roi_percentage,
            "profit": profit,
            "revenue": revenue,
            "cost": cost,
            "cost_per_request": self.calculate_cost_per_request(cost, requests),
            "cost_per_success": self.calculate_cost_per_successful_request(cost, successes),
            "revenue_per_request": revenue / requests if requests > 0 else 0.0,
            "success_rate": successes / requests if requests > 0 else 0.0,
        }

    def project_future_costs(
        self,
        historical_costs: list[tuple[datetime, float]],
        forecast_days: int = 30,
    ) -> Prediction:
        """
        Project future costs based on historical trends.
        
        Uses simple linear trend projection.
        
        Args:
            historical_costs: List of (date, cost) tuples
            forecast_days: Days to forecast into future
            
        Returns:
            Cost prediction with confidence intervals
        """
        if len(historical_costs) < 2:
            raise ValueError("Insufficient historical data for forecasting")
        
        # Sort by date
        sorted_costs = sorted(historical_costs, key=lambda x: x[0])
        
        # Extract values
        dates = [d for d, _ in sorted_costs]
        costs = [c for _, c in sorted_costs]
        
        # Calculate daily costs
        daily_costs = []
        for i in range(len(dates) - 1):
            days_diff = (dates[i + 1] - dates[i]).days
            if days_diff > 0:
                daily_cost = (costs[i + 1] - costs[i]) / days_diff
                daily_costs.append(daily_cost)
        
        if not daily_costs:
            avg_daily_cost = sum(costs) / len(costs)
        else:
            avg_daily_cost = statistics.mean(daily_costs)
        
        # Project forward
        last_date = dates[-1]
        last_cost = costs[-1]
        predicted_date = last_date + timedelta(days=forecast_days)
        predicted_cost = last_cost + (avg_daily_cost * forecast_days)
        
        # Calculate confidence intervals (?20%)
        margin = abs(predicted_cost) * 0.2
        
        prediction = Prediction(
            metric_name="proxy_cost_usd",
            predicted_value=max(0.0, predicted_cost),
            lower_bound=max(0.0, predicted_cost - margin),
            upper_bound=predicted_cost + margin,
            confidence_level=0.8,
            prediction_horizon_days=forecast_days,
            model_name="linear_trend",
            model_accuracy=0.75,
            prediction_date=predicted_date,
        )
        
        logger.info(f"Projected cost for {forecast_days} days: ${predicted_cost:.2f}")
        return prediction

    def identify_cost_optimization_opportunities(
        self,
        source_comparison: dict[str, dict[str, float]],
    ) -> list[Recommendation]:
        """
        Identify opportunities for cost optimization.
        
        Args:
            source_comparison: Cost effectiveness comparison data
            
        Returns:
            List of cost optimization recommendations
        """
        recommendations: list[Recommendation] = []
        
        if not source_comparison:
            return recommendations
        
        # Find most and least cost-effective sources
        sorted_sources = sorted(
            source_comparison.items(),
            key=lambda x: x[1].get("roi_score", 0),
            reverse=True,
        )
        
        best_source = sorted_sources[0]
        worst_source = sorted_sources[-1]
        
        # Recommend scaling best source
        recommendations.append(
            Recommendation(
                title=f"Scale Cost-Effective Source: {best_source[0]}",
                description=(
                    f"{best_source[0]} shows the best ROI with a score of "
                    f"{best_source[1]['roi_score']:.2f}. Consider increasing "
                    f"allocation to this source for better cost efficiency."
                ),
                priority=RecommendationPriority.HIGH,
                category="cost_optimization",
                estimated_improvement=(
                    f"Potential {(best_source[1]['roi_score'] - worst_source[1]['roi_score']):.1f}% "
                    f"ROI improvement"
                ),
                estimated_effort="Medium - procurement and integration",
                affected_proxies=[],
                supporting_data={
                    "best_source": best_source[0],
                    "best_roi": best_source[1]["roi_score"],
                    "worst_roi": worst_source[1]["roi_score"],
                },
            )
        )
        
        # Recommend reviewing worst source
        if worst_source[1]["roi_score"] < best_source[1]["roi_score"] * 0.5:
            recommendations.append(
                Recommendation(
                    title=f"Review Underperforming Source: {worst_source[0]}",
                    description=(
                        f"{worst_source[0]} has significantly lower ROI "
                        f"({worst_source[1]['roi_score']:.2f}) compared to best source "
                        f"({best_source[1]['roi_score']:.2f}). Consider reducing or "
                        f"eliminating this source."
                    ),
                    priority=RecommendationPriority.MEDIUM,
                    category="cost_optimization",
                    estimated_improvement=(
                        f"Potential cost savings of "
                        f"${worst_source[1].get('total_cost', 0):.2f} per period"
                    ),
                    estimated_effort="Low - reduce or remove allocation",
                    affected_proxies=[],
                    supporting_data={
                        "worst_source": worst_source[0],
                        "worst_roi": worst_source[1]["roi_score"],
                        "total_cost": worst_source[1].get("total_cost", 0),
                    },
                )
            )
        
        logger.info(f"Identified {len(recommendations)} cost optimization opportunities")
        return recommendations
