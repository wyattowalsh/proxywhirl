"""
Performance analyzer for ProxyWhirl analytics engine.

Provides comprehensive proxy performance analysis including success rate,
latency metrics, uptime tracking, and performance scoring.
"""

import statistics
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Optional

from loguru import logger

from proxywhirl.analytics_models import (
    AnalysisConfig,
    PerformanceScore,
    ProxyPerformanceMetrics,
    Recommendation,
    RecommendationPriority,
    TrendDirection,
)


class PerformanceAnalyzer:
    """
    Analyzes proxy performance metrics and provides rankings and recommendations.
    
    Calculates success rates, latency statistics, uptime percentages, and
    generates performance scores with multi-criteria ranking.
    
    Example:
        ```python
        from proxywhirl import PerformanceAnalyzer, AnalysisConfig
        
        analyzer = PerformanceAnalyzer(config=AnalysisConfig())
        
        # Calculate performance scores
        scores = analyzer.calculate_performance_scores(proxy_metrics)
        
        # Rank proxies
        ranked = analyzer.rank_proxies(scores)
        
        # Identify underperformers
        underperformers = analyzer.identify_underperforming_proxies(proxy_metrics)
        ```
    """

    def __init__(self, config: Optional[AnalysisConfig] = None) -> None:
        """
        Initialize performance analyzer.
        
        Args:
            config: Analysis configuration (default: AnalysisConfig())
        """
        self.config = config or AnalysisConfig()
        logger.debug("Performance analyzer initialized", config=self.config.model_dump())

    def calculate_success_rate(
        self,
        successful_requests: int,
        total_requests: int,
    ) -> float:
        """
        Calculate success rate for proxy.
        
        Args:
            successful_requests: Number of successful requests
            total_requests: Total number of requests
            
        Returns:
            Success rate as float between 0.0 and 1.0
        """
        if total_requests == 0:
            return 0.0
        return successful_requests / total_requests

    def calculate_average_latency(self, latencies: list[float]) -> float:
        """
        Calculate average latency from latency measurements.
        
        Args:
            latencies: List of latency measurements in milliseconds
            
        Returns:
            Average latency in milliseconds
        """
        if not latencies:
            return 0.0
        return statistics.mean(latencies)

    def calculate_uptime(
        self,
        uptime_hours: float,
        downtime_hours: float,
    ) -> float:
        """
        Calculate uptime percentage.
        
        Args:
            uptime_hours: Total uptime in hours
            downtime_hours: Total downtime in hours
            
        Returns:
            Uptime percentage (0.0 to 100.0)
        """
        total_hours = uptime_hours + downtime_hours
        if total_hours == 0:
            return 100.0
        return (uptime_hours / total_hours) * 100.0

    def calculate_latency_percentiles(
        self,
        latencies: list[float],
    ) -> dict[str, float]:
        """
        Calculate latency percentiles (p50, p95, p99).
        
        Args:
            latencies: List of latency measurements in milliseconds
            
        Returns:
            Dictionary with percentile values
        """
        if not latencies:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0, "min": 0.0, "max": 0.0}
        
        sorted_latencies = sorted(latencies)
        
        return {
            "p50":  statistics.quantiles(sorted_latencies, n=100)[49],  # 50th percentile
            "p95":  statistics.quantiles(sorted_latencies, n=100)[94],  # 95th percentile
            "p99":  statistics.quantiles(sorted_latencies, n=100)[98],  # 99th percentile
            "min":  min(sorted_latencies),
            "max":  max(sorted_latencies),
        }

    def calculate_performance_score(
        self,
        metrics: ProxyPerformanceMetrics,
    ) -> PerformanceScore:
        """
        Calculate comprehensive performance score for a proxy.
        
        Combines success rate, latency, and uptime into weighted overall score.
        
        Args:
            metrics: Proxy performance metrics
            
        Returns:
            Performance score with component breakdowns
        """
        # Calculate component scores (0-100 scale)
        
        # Success rate score (0-100): direct conversion from 0-1 to 0-100
        success_rate_score = metrics.success_rate * 100.0
        
        # Latency score (0-100): inverse relationship, capped at max threshold
        # Score = 100 * (1 - latency / max_latency)
        max_latency = self.config.max_avg_latency_ms
        if metrics.avg_latency_ms >= max_latency:
            latency_score = 0.0
        else:
            latency_score = 100.0 * (1.0 - (metrics.avg_latency_ms / max_latency))
        
        # Uptime score (0-100): direct conversion from percentage
        uptime_score = metrics.uptime_percentage
        
        # Reliability score: based on request count and consistency
        # Higher request counts with consistent performance = higher reliability
        if metrics.total_requests < 10:
            reliability_score = 50.0  # Low confidence
        elif metrics.total_requests < 100:
            reliability_score = 75.0  # Medium confidence
        else:
            # High confidence, factor in error distribution
            if metrics.error_counts:
                error_diversity = len(metrics.error_counts)
                # More diverse errors = lower reliability
                reliability_score = 100.0 - (error_diversity * 5.0)
                reliability_score = max(0.0, reliability_score)
            else:
                reliability_score = 100.0
        
        # Calculate weighted overall score
        overall_score = (
            success_rate_score * self.config.success_rate_weight +
            latency_score * self.config.latency_weight +
            uptime_score * self.config.uptime_weight
        )
        
        return PerformanceScore(
            proxy_id=metrics.proxy_id,
            overall_score=overall_score,
            success_rate_score=success_rate_score,
            latency_score=latency_score,
            uptime_score=uptime_score,
            reliability_score=reliability_score,
            calculated_at=datetime.now(),
        )

    def calculate_performance_scores(
        self,
        proxy_metrics: dict[str, ProxyPerformanceMetrics],
    ) -> dict[str, PerformanceScore]:
        """
        Calculate performance scores for multiple proxies.
        
        Args:
            proxy_metrics: Dictionary of proxy_id -> ProxyPerformanceMetrics
            
        Returns:
            Dictionary of proxy_id -> PerformanceScore
        """
        scores: dict[str, PerformanceScore] = {}
        
        for proxy_id, metrics in proxy_metrics.items():
            scores[proxy_id] = self.calculate_performance_score(metrics)
        
        logger.info(f"Calculated performance scores for {len(scores)} proxies")
        return scores

    def rank_proxies(
        self,
        scores: dict[str, PerformanceScore],
        descending: bool = True,
    ) -> list[tuple[str, PerformanceScore]]:
        """
        Rank proxies by performance score.
        
        Args:
            scores: Dictionary of proxy_id -> PerformanceScore
            descending: Rank from highest to lowest (default: True)
            
        Returns:
            List of (proxy_id, score) tuples sorted by overall score
        """
        ranked = sorted(
            scores.items(),
            key=lambda x: x[1].overall_score,
            reverse=descending,
        )
        
        # Update rank and percentile in scores
        total_proxies = len(ranked)
        for rank_position, (proxy_id, score) in enumerate(ranked, start=1):
            # Create new score with updated rank (since scores are frozen)
            updated_score = score.model_copy(update={
                "rank": rank_position,
                "percentile": (rank_position / total_proxies) * 100.0,
            })
            ranked[rank_position - 1] = (proxy_id, updated_score)
        
        logger.info(f"Ranked {total_proxies} proxies by performance")
        return ranked

    def identify_underperforming_proxies(
        self,
        proxy_metrics: dict[str, ProxyPerformanceMetrics],
    ) -> dict[str, ProxyPerformanceMetrics]:
        """
        Identify proxies that don't meet minimum performance thresholds.
        
        Args:
            proxy_metrics: Dictionary of proxy_id -> ProxyPerformanceMetrics
            
        Returns:
            Dictionary of underperforming proxies
        """
        underperformers: dict[str, ProxyPerformanceMetrics] = {}
        
        for proxy_id, metrics in proxy_metrics.items():
            is_underperforming = (
                metrics.success_rate < self.config.min_success_rate or
                metrics.avg_latency_ms > self.config.max_avg_latency_ms or
                metrics.uptime_percentage < self.config.min_uptime_percentage
            )
            
            if is_underperforming:
                underperformers[proxy_id] = metrics
        
        logger.warning(
            f"Identified {len(underperformers)} underperforming proxies "
            f"out of {len(proxy_metrics)} total"
        )
        return underperformers

    def detect_degradation_patterns(
        self,
        historical_metrics: list[ProxyPerformanceMetrics],
        window_size: int = 5,
    ) -> dict[str, TrendDirection]:
        """
        Detect performance degradation trends over time.
        
        Uses moving window analysis to identify proxies with declining performance.
        
        Args:
            historical_metrics: List of metrics ordered by time
            window_size: Number of data points for trend analysis
            
        Returns:
            Dictionary of proxy_id -> TrendDirection
        """
        if len(historical_metrics) < window_size:
            logger.warning(
                f"Insufficient data for trend analysis: {len(historical_metrics)} < {window_size}"
            )
            return {}
        
        # Group metrics by proxy
        proxy_series: dict[str, list[ProxyPerformanceMetrics]] = defaultdict(list)
        for metrics in historical_metrics:
            proxy_series[metrics.proxy_id].append(metrics)
        
        trends: dict[str, TrendDirection] = {}
        
        for proxy_id, series in proxy_series.items():
            if len(series) < window_size:
                continue
            
            # Analyze success rate trend
            success_rates = [m.success_rate for m in series[-window_size:]]
            
            # Calculate linear trend (simple slope)
            x = list(range(len(success_rates)))
            slope = self._calculate_trend_slope(x, success_rates)
            
            # Determine trend direction
            if abs(slope) < 0.01:  # Threshold for stability
                trends[proxy_id] = TrendDirection.STABLE
            elif slope > 0.05:  # Significant improvement
                trends[proxy_id] = TrendDirection.INCREASING
            elif slope < -0.05:  # Significant degradation
                trends[proxy_id] = TrendDirection.DECREASING
            else:
                # Check volatility
                std_dev = statistics.stdev(success_rates) if len(success_rates) > 1 else 0
                if std_dev > 0.15:
                    trends[proxy_id] = TrendDirection.VOLATILE
                else:
                    trends[proxy_id] = TrendDirection.STABLE
        
        logger.info(f"Analyzed degradation patterns for {len(trends)} proxies")
        return trends

    def _calculate_trend_slope(self, x: list[int], y: list[float]) -> float:
        """
        Calculate slope of linear trend line.
        
        Uses simple linear regression: slope = ?((x - x?)(y - ?)) / ?((x - x?)?)
        
        Args:
            x: X values (time indices)
            y: Y values (metric values)
            
        Returns:
            Slope of trend line
        """
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(y)
        
        numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
        denominator = sum((xi - x_mean) ** 2 for xi in x)
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator

    def generate_performance_recommendations(
        self,
        proxy_metrics: dict[str, ProxyPerformanceMetrics],
        scores: dict[str, PerformanceScore],
    ) -> list[Recommendation]:
        """
        Generate actionable recommendations based on performance analysis.
        
        Args:
            proxy_metrics: Dictionary of proxy_id -> ProxyPerformanceMetrics
            scores: Dictionary of proxy_id -> PerformanceScore
            
        Returns:
            List of prioritized recommendations
        """
        recommendations: list[Recommendation] = []
        
        # Identify underperformers
        underperformers = self.identify_underperforming_proxies(proxy_metrics)
        
        if underperformers:
            underperformer_ids = list(underperformers.keys())
            recommendations.append(
                Recommendation(
                    title="Remove Underperforming Proxies",
                    description=(
                        f"Found {len(underperformers)} proxies that don't meet minimum "
                        f"performance thresholds. Consider removing these proxies to improve "
                        f"overall pool quality and reduce failure rates."
                    ),
                    priority=RecommendationPriority.HIGH,
                    category="performance",
                    estimated_improvement="10-30% reduction in failures",
                    estimated_effort="Low - automated removal",
                    affected_proxies=underperformer_ids,
                    supporting_data={
                        "underperformer_count": len(underperformers),
                        "min_success_rate": self.config.min_success_rate,
                        "max_avg_latency_ms": self.config.max_avg_latency_ms,
                    },
                )
            )
        
        # Identify top performers for scaling
        ranked = self.rank_proxies(scores)
        top_10_percent = max(1, len(ranked) // 10)
        top_performers = ranked[:top_10_percent]
        
        if top_performers:
            top_performer_ids = [proxy_id for proxy_id, _ in top_performers]
            avg_top_score = statistics.mean(score.overall_score for _, score in top_performers)
            
            recommendations.append(
                Recommendation(
                    title="Scale Top-Performing Proxies",
                    description=(
                        f"Identified {len(top_performers)} top-performing proxies with average "
                        f"score of {avg_top_score:.1f}. Consider increasing utilization or "
                        f"acquiring similar proxies from the same sources/regions."
                    ),
                    priority=RecommendationPriority.MEDIUM,
                    category="optimization",
                    estimated_improvement="20-40% improvement in overall pool performance",
                    estimated_effort="Medium - source evaluation and procurement",
                    affected_proxies=top_performer_ids,
                    supporting_data={
                        "top_performer_count": len(top_performers),
                        "avg_score": avg_top_score,
                    },
                )
            )
        
        # Check for high latency proxies
        high_latency_proxies = [
            (proxy_id, metrics)
            for proxy_id, metrics in proxy_metrics.items()
            if metrics.avg_latency_ms > self.config.max_avg_latency_ms * 0.8
        ]
        
        if high_latency_proxies:
            high_latency_ids = [proxy_id for proxy_id, _ in high_latency_proxies]
            recommendations.append(
                Recommendation(
                    title="Investigate High Latency Proxies",
                    description=(
                        f"Found {len(high_latency_proxies)} proxies with latency approaching "
                        f"the maximum threshold. Investigate root causes and consider geographic "
                        f"alternatives or upgrading to premium proxies."
                    ),
                    priority=RecommendationPriority.MEDIUM,
                    category="performance",
                    estimated_improvement="15-25% latency reduction",
                    estimated_effort="Medium - investigation and sourcing",
                    affected_proxies=high_latency_ids,
                    supporting_data={
                        "high_latency_count": len(high_latency_proxies),
                        "threshold": self.config.max_avg_latency_ms,
                    },
                )
            )
        
        # Check for low uptime proxies
        low_uptime_proxies = [
            (proxy_id, metrics)
            for proxy_id, metrics in proxy_metrics.items()
            if metrics.uptime_percentage < self.config.min_uptime_percentage
        ]
        
        if low_uptime_proxies:
            low_uptime_ids = [proxy_id for proxy_id, _ in low_uptime_proxies]
            recommendations.append(
                Recommendation(
                    title="Address Low Uptime Proxies",
                    description=(
                        f"Identified {len(low_uptime_proxies)} proxies with uptime below "
                        f"{self.config.min_uptime_percentage}%. These proxies may be unreliable "
                        f"and should be replaced or moved to backup pools."
                    ),
                    priority=RecommendationPriority.HIGH,
                    category="reliability",
                    estimated_improvement="Improved availability and reliability",
                    estimated_effort="Low - replacement from existing sources",
                    affected_proxies=low_uptime_ids,
                    supporting_data={
                        "low_uptime_count": len(low_uptime_proxies),
                        "min_uptime": self.config.min_uptime_percentage,
                    },
                )
            )
        
        logger.info(f"Generated {len(recommendations)} performance recommendations")
        return recommendations

    def calculate_statistical_summary(
        self,
        metrics: list[ProxyPerformanceMetrics],
    ) -> dict[str, Any]:
        """
        Calculate statistical summary for proxy metrics.
        
        Args:
            metrics: List of proxy performance metrics
            
        Returns:
            Dictionary with mean, median, percentile statistics
        """
        if not metrics:
            return {}
        
        success_rates = [m.success_rate for m in metrics]
        latencies = [m.avg_latency_ms for m in metrics]
        uptimes = [m.uptime_percentage for m in metrics]
        
        return {
            "success_rate": {
                "mean":   statistics.mean(success_rates),
                "median": statistics.median(success_rates),
                "stdev":  statistics.stdev(success_rates) if len(success_rates) > 1 else 0.0,
                "min":    min(success_rates),
                "max":    max(success_rates),
            },
            "avg_latency_ms": {
                "mean":   statistics.mean(latencies),
                "median": statistics.median(latencies),
                "stdev":  statistics.stdev(latencies) if len(latencies) > 1 else 0.0,
                "min":    min(latencies),
                "max":    max(latencies),
            },
            "uptime_percentage": {
                "mean":   statistics.mean(uptimes),
                "median": statistics.median(uptimes),
                "stdev":  statistics.stdev(uptimes) if len(uptimes) > 1 else 0.0,
                "min":    min(uptimes),
                "max":    max(uptimes),
            },
            "total_proxies": len(metrics),
        }
