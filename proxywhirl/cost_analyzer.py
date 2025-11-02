"""
Cost analyzer for ROI tracking.

Implements User Story 4: Cost and ROI Analysis
- Calculate cost per request and per successful request
- Compare cost-effectiveness across proxy sources
- Calculate ROI metrics
- Project future costs with trend-based forecasting
"""

from datetime import datetime, timedelta
from typing import Any, Optional

import numpy as np
from loguru import logger

from proxywhirl.analytics_models import (
    AnalysisConfig,
    CostForecast,
    CostMetrics,
    TrendDirection,
)


class CostAnalyzer:
    """
    Analyzes proxy costs and ROI.
    
    Example:
        ```python
        from proxywhirl import CostAnalyzer
        
        analyzer = CostAnalyzer()
        
        # Calculate costs
        metrics = analyzer.calculate_cost_metrics(
            total_cost=100.0,
            request_data=requests,
            source="premium_proxies"
        )
        
        # Project future costs
        forecast = analyzer.project_future_costs(historical_data)
        ```
    """

    def __init__(self, config: Optional[AnalysisConfig] = None) -> None:
        """
        Initialize cost analyzer.
        
        Args:
            config: Analysis configuration
        """
        self.config = config or AnalysisConfig()
        logger.info("Cost analyzer initialized")

    def calculate_cost_per_request(
        self,
        total_cost: float,
        total_requests: int,
    ) -> float:
        """
        Calculate cost per request.
        
        Args:
            total_cost: Total cost in currency units
            total_requests: Total number of requests
            
        Returns:
            Cost per request
        """
        if total_requests <= 0:
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
            total_cost: Total cost
            successful_requests: Number of successful requests
            
        Returns:
            Cost per successful request
        """
        if successful_requests <= 0:
            return 0.0
        
        return total_cost / successful_requests

    def calculate_cost_metrics(
        self,
        total_cost: float,
        request_data: list[dict[str, Any]],
        source: str,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
    ) -> CostMetrics:
        """
        Calculate comprehensive cost metrics.
        
        Args:
            total_cost: Total cost for the period
            request_data: List of request records
            source: Proxy source identifier
            period_start: Start of cost period
            period_end: End of cost period
            
        Returns:
            Complete cost metrics
        """
        if not request_data:
            return CostMetrics(
                total_cost=total_cost,
                cost_per_request=0.0,
                cost_per_successful_request=0.0,
                total_requests=0,
                successful_requests=0,
                cost_efficiency_score=0.0,
                source=source,
                period_start=period_start or datetime.now(),
                period_end=period_end or datetime.now(),
            )
        
        # Count requests
        total_requests = len(request_data)
        successful_requests = sum(1 for r in request_data if r.get("success", False))
        
        # Calculate costs
        cost_per_request = self.calculate_cost_per_request(total_cost, total_requests)
        cost_per_successful = self.calculate_cost_per_successful_request(
            total_cost, successful_requests
        )
        
        # Calculate efficiency score (0-1, higher is better)
        # Based on success rate and cost-effectiveness
        success_rate = successful_requests / total_requests if total_requests > 0 else 0.0
        
        # Normalize cost (assume $0.10 per request as baseline)
        baseline_cost = 0.10
        cost_factor = baseline_cost / cost_per_request if cost_per_request > 0 else 1.0
        cost_factor = min(1.0, cost_factor)  # Cap at 1.0
        
        # Combine success rate and cost factor
        efficiency_score = (success_rate * 0.6) + (cost_factor * 0.4)
        
        metrics = CostMetrics(
            total_cost=total_cost,
            cost_per_request=cost_per_request,
            cost_per_successful_request=cost_per_successful,
            total_requests=total_requests,
            successful_requests=successful_requests,
            cost_efficiency_score=efficiency_score,
            source=source,
            period_start=period_start or min(r["timestamp"] for r in request_data),
            period_end=period_end or max(r["timestamp"] for r in request_data),
        )
        
        logger.info(
            "Calculated cost metrics",
            source=source,
            total_cost=total_cost,
            efficiency_score=f"{efficiency_score:.2f}",
        )
        
        return metrics

    def compare_source_cost_effectiveness(
        self,
        source_metrics: list[CostMetrics],
    ) -> list[CostMetrics]:
        """
        Compare cost-effectiveness across proxy sources.
        
        Args:
            source_metrics: List of cost metrics for different sources
            
        Returns:
            List of metrics sorted by cost-effectiveness (best first)
        """
        if not source_metrics:
            return []
        
        # Sort by efficiency score
        sorted_metrics = sorted(
            source_metrics,
            key=lambda m: m.cost_efficiency_score,
            reverse=True,
        )
        
        # Assign ranks
        for idx, metrics in enumerate(sorted_metrics, start=1):
            metrics.rank_by_cost_effectiveness = idx
        
        logger.info(
            "Compared source cost-effectiveness",
            total_sources=len(source_metrics),
            best_source=sorted_metrics[0].source if sorted_metrics else None,
        )
        
        return sorted_metrics

    def calculate_roi_metrics(
        self,
        total_cost: float,
        total_revenue: Optional[float] = None,
        request_data: Optional[list[dict[str, Any]]] = None,
        value_per_successful_request: float = 1.0,
    ) -> dict[str, Any]:
        """
        Calculate ROI metrics.
        
        Args:
            total_cost: Total cost of proxies
            total_revenue: Total revenue generated (if known)
            request_data: Request records for value calculation
            value_per_successful_request: Value assigned to each successful request
            
        Returns:
            Dictionary with ROI metrics
        """
        if total_cost <= 0:
            return {"roi_percent": 0.0}
        
        # Calculate value/revenue
        if total_revenue is not None:
            value = total_revenue
        elif request_data:
            successful = sum(1 for r in request_data if r.get("success", False))
            value = successful * value_per_successful_request
        else:
            value = 0.0
        
        # Calculate ROI
        profit = value - total_cost
        roi_percent = (profit / total_cost) * 100 if total_cost > 0 else 0.0
        
        metrics = {
            "total_cost": total_cost,
            "total_value": value,
            "profit": profit,
            "roi_percent": roi_percent,
            "break_even": (profit >= 0),
            "payback_period_days": None,  # Would need historical data
        }
        
        logger.info(
            "Calculated ROI metrics",
            roi_percent=f"{roi_percent:.1f}%",
            break_even=metrics["break_even"],
        )
        
        return metrics

    def project_future_costs(
        self,
        historical_cost_data: list[tuple[datetime, float]],
        forecast_days: int = 30,
        confidence_level: float = 0.95,
    ) -> CostForecast:
        """
        Project future costs with trend-based forecasting.
        
        Args:
            historical_cost_data: List of (timestamp, cost) tuples
            forecast_days: Days to forecast into future
            confidence_level: Confidence level for intervals (0.0-1.0)
            
        Returns:
            Cost forecast with projections and confidence intervals
        """
        if not historical_cost_data or len(historical_cost_data) < 3:
            # Not enough data for forecasting
            now = datetime.now()
            return CostForecast(
                forecast_start=now,
                forecast_end=now + timedelta(days=forecast_days),
                projected_total_cost=0.0,
                projected_requests=0,
                projected_cost_per_request=0.0,
                confidence_interval_lower=0.0,
                confidence_interval_upper=0.0,
                confidence_level=confidence_level,
                trend=TrendDirection.STABLE,
                trend_strength=0.0,
            )
        
        # Sort by timestamp
        historical_cost_data.sort(key=lambda x: x[0])
        
        # Extract timestamps and costs
        timestamps = [ts.timestamp() for ts, _ in historical_cost_data]
        costs = [cost for _, cost in historical_cost_data]
        
        # Linear regression for trend
        x = np.arange(len(costs))
        y = np.array(costs)
        
        # Fit linear model
        coeffs = np.polyfit(x, y, 1)
        slope = coeffs[0]
        intercept = coeffs[1]
        
        # Determine trend
        if slope > 0.01 * np.mean(costs):
            trend = TrendDirection.INCREASING
            trend_strength = min(1.0, abs(slope) / np.mean(costs))
        elif slope < -0.01 * np.mean(costs):
            trend = TrendDirection.DECREASING
            trend_strength = min(1.0, abs(slope) / np.mean(costs))
        else:
            trend = TrendDirection.STABLE
            trend_strength = 0.0
        
        # Project future values
        future_x = np.arange(len(costs), len(costs) + forecast_days)
        projected_costs = slope * future_x + intercept
        
        # Calculate confidence intervals
        # Simple approach: use standard error of regression
        residuals = y - (slope * x + intercept)
        std_error = np.std(residuals)
        
        # Z-score for confidence level
        if confidence_level == 0.95:
            z_score = 1.96
        elif confidence_level == 0.99:
            z_score = 2.58
        else:
            z_score = 1.96  # Default to 95%
        
        projected_total = np.sum(projected_costs)
        margin_of_error = z_score * std_error * np.sqrt(forecast_days)
        
        # Estimate requests (assume constant request rate)
        time_span_hours = (timestamps[-1] - timestamps[0]) / 3600
        if time_span_hours > 0:
            total_cost = sum(costs)
            avg_cost_per_hour = total_cost / time_span_hours
            forecast_hours = forecast_days * 24
            projected_cost_from_rate = avg_cost_per_hour * forecast_hours
        else:
            projected_cost_from_rate = projected_total
        
        # Use average of trend-based and rate-based projections
        projected_total = (projected_total + projected_cost_from_rate) / 2
        
        forecast = CostForecast(
            forecast_start=historical_cost_data[-1][0],
            forecast_end=historical_cost_data[-1][0] + timedelta(days=forecast_days),
            projected_total_cost=float(projected_total),
            projected_requests=0,  # Would need request volume data
            projected_cost_per_request=0.0,
            confidence_interval_lower=float(max(0, projected_total - margin_of_error)),
            confidence_interval_upper=float(projected_total + margin_of_error),
            confidence_level=confidence_level,
            trend=trend,
            trend_strength=trend_strength,
        )
        
        logger.info(
            "Projected future costs",
            forecast_days=forecast_days,
            projected_cost=projected_total,
            trend=trend,
        )
        
        return forecast

    def identify_cost_optimization_opportunities(
        self,
        source_metrics: list[CostMetrics],
        current_allocation: dict[str, float],
    ) -> list[str]:
        """
        Identify opportunities to optimize proxy spending.
        
        Args:
            source_metrics: Cost metrics for each source
            current_allocation: Current budget allocation by source
            
        Returns:
            List of optimization recommendations
        """
        if not source_metrics:
            return []
        
        opportunities: list[str] = []
        
        # Sort by efficiency
        sorted_metrics = self.compare_source_cost_effectiveness(source_metrics)
        
        # Identify inefficient sources
        if len(sorted_metrics) >= 2:
            best = sorted_metrics[0]
            worst = sorted_metrics[-1]
            
            efficiency_gap = best.cost_efficiency_score - worst.cost_efficiency_score
            
            if efficiency_gap > 0.2:
                opportunities.append(
                    f"Shift budget from {worst.source} "
                    f"(efficiency: {worst.cost_efficiency_score:.2f}) to "
                    f"{best.source} (efficiency: {best.cost_efficiency_score:.2f})"
                )
        
        # Check for high-cost sources
        avg_cost = np.mean([m.cost_per_request for m in source_metrics])
        for metrics in source_metrics:
            if metrics.cost_per_request > avg_cost * 1.5:
                opportunities.append(
                    f"Source {metrics.source} costs {metrics.cost_per_request:.4f} per request, "
                    f"{((metrics.cost_per_request / avg_cost - 1) * 100):.0f}% above average"
                )
        
        # Check success rates
        for metrics in source_metrics:
            success_rate = (
                metrics.successful_requests / metrics.total_requests
                if metrics.total_requests > 0
                else 0.0
            )
            if success_rate < 0.8:
                opportunities.append(
                    f"Source {metrics.source} has low success rate ({success_rate:.1%}), "
                    "consider replacing with more reliable source"
                )
        
        # General recommendations
        if len(source_metrics) > 5:
            opportunities.append(
                "Consider consolidating proxy sources to reduce management overhead"
            )
        
        logger.info(
            "Identified cost optimization opportunities",
            opportunities_count=len(opportunities),
        )
        
        return opportunities

    def calculate_total_cost_of_ownership(
        self,
        direct_costs: float,
        operational_hours: float = 0.0,
        hourly_rate: float = 50.0,
        infrastructure_costs: float = 0.0,
    ) -> dict[str, Any]:
        """
        Calculate total cost of ownership including operational overhead.
        
        Args:
            direct_costs: Direct proxy subscription/usage costs
            operational_hours: Hours spent managing proxies
            hourly_rate: Cost per operational hour
            infrastructure_costs: Infrastructure costs (servers, etc.)
            
        Returns:
            Dictionary with TCO breakdown
        """
        operational_costs = operational_hours * hourly_rate
        total_cost = direct_costs + operational_costs + infrastructure_costs
        
        tco = {
            "direct_costs": direct_costs,
            "operational_costs": operational_costs,
            "infrastructure_costs": infrastructure_costs,
            "total_cost_of_ownership": total_cost,
            "direct_cost_percent": (direct_costs / total_cost * 100) if total_cost > 0 else 0.0,
            "operational_cost_percent": (operational_costs / total_cost * 100) if total_cost > 0 else 0.0,
            "infrastructure_cost_percent": (infrastructure_costs / total_cost * 100) if total_cost > 0 else 0.0,
        }
        
        logger.info(
            "Calculated total cost of ownership",
            tco=total_cost,
        )
        
        return tco


__all__ = [
    "CostAnalyzer",
]
