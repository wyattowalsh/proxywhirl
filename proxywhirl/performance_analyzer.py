"""
Performance analyzer for proxy metrics.

Implements User Story 1: Proxy Performance Analysis
- Calculate success rates, latency metrics, and uptime
- Rank proxies by performance criteria
- Identify underperforming proxies
- Detect degradation patterns
"""

from datetime import datetime, timedelta
from typing import Any, Optional
from collections import defaultdict

import numpy as np
from loguru import logger

from proxywhirl.analytics_models import (
    AnalysisConfig,
    PerformanceScore,
    ProxyPerformanceMetrics,
    RecommendationPriority,
    TrendDirection,
)


class PerformanceAnalyzer:
    """
    Analyzes proxy performance metrics to identify top and underperforming proxies.
    
    Example:
        ```python
        from proxywhirl import PerformanceAnalyzer, AnalysisConfig
        
        analyzer = PerformanceAnalyzer(config=AnalysisConfig())
        
        # Analyze proxy metrics
        scores = analyzer.rank_proxies(proxy_metrics)
        
        # Identify underperformers
        underperformers = analyzer.identify_underperforming_proxies(proxy_metrics)
        ```
    """

    def __init__(self, config: Optional[AnalysisConfig] = None) -> None:
        """
        Initialize performance analyzer.
        
        Args:
            config: Analysis configuration
        """
        self.config = config or AnalysisConfig()
        logger.info("Performance analyzer initialized")

    def calculate_success_rate(
        self,
        metrics: ProxyPerformanceMetrics,
    ) -> float:
        """
        Calculate success rate for a proxy.
        
        Args:
            metrics: Proxy performance metrics
            
        Returns:
            Success rate (0.0 to 1.0)
        """
        if metrics.total_requests == 0:
            return 0.0
        
        return metrics.successful_requests / metrics.total_requests

    def calculate_average_latency(
        self,
        metrics: ProxyPerformanceMetrics,
    ) -> float:
        """
        Calculate average latency for a proxy.
        
        Args:
            metrics: Proxy performance metrics
            
        Returns:
            Average latency in milliseconds
        """
        return metrics.avg_latency_ms

    def calculate_uptime(
        self,
        metrics: ProxyPerformanceMetrics,
    ) -> float:
        """
        Calculate uptime percentage for a proxy.
        
        Args:
            metrics: Proxy performance metrics
            
        Returns:
            Uptime percentage (0.0 to 100.0)
        """
        return metrics.availability_percent

    def rank_proxies(
        self,
        proxy_metrics: dict[str, ProxyPerformanceMetrics],
        weights: Optional[dict[str, float]] = None,
    ) -> list[PerformanceScore]:
        """
        Rank proxies by performance with multi-criteria scoring.
        
        Args:
            proxy_metrics: Dictionary of proxy metrics keyed by proxy_id
            weights: Scoring weights (success_rate, latency, availability)
                    Default: {"success_rate": 0.5, "latency": 0.3, "availability": 0.2}
            
        Returns:
            List of performance scores sorted by overall score (best first)
        """
        if not proxy_metrics:
            return []
        
        # Default weights
        if weights is None:
            weights = {
                "success_rate": 0.5,
                "latency": 0.3,
                "availability": 0.2,
            }
        
        # Normalize weights
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}
        
        scores: list[PerformanceScore] = []
        
        # Calculate individual component scores
        latencies = [m.avg_latency_ms for m in proxy_metrics.values() if m.total_requests > 0]
        max_latency = max(latencies) if latencies else 1.0
        
        for proxy_id, metrics in proxy_metrics.items():
            # Skip proxies with no requests
            if metrics.total_requests == 0:
                continue
            
            # Success rate score (already 0-1)
            success_rate_score = metrics.success_rate
            
            # Latency score (inverse - lower is better, normalized to 0-1)
            if max_latency > 0:
                latency_score = 1.0 - (metrics.avg_latency_ms / max_latency)
            else:
                latency_score = 1.0
            latency_score = max(0.0, latency_score)  # Ensure non-negative
            
            # Availability score (convert percentage to 0-1)
            availability_score = metrics.availability_percent / 100.0
            
            # Calculate weighted overall score
            overall_score = (
                weights.get("success_rate", 0.5) * success_rate_score
                + weights.get("latency", 0.3) * latency_score
                + weights.get("availability", 0.2) * availability_score
            )
            
            score = PerformanceScore(
                proxy_id=proxy_id,
                success_rate_score=success_rate_score,
                latency_score=latency_score,
                availability_score=availability_score,
                overall_score=overall_score,
                weights=weights,
            )
            scores.append(score)
        
        # Sort by overall score (descending)
        scores.sort(key=lambda s: s.overall_score, reverse=True)
        
        # Assign ranks and percentiles
        total_proxies = len(scores)
        for idx, score in enumerate(scores, start=1):
            score.rank = idx
            score.percentile = ((total_proxies - idx + 1) / total_proxies) * 100.0
            
            # Mark top/bottom performers (top/bottom 10%)
            if score.percentile >= 90.0:
                score.is_top_performer = True
            elif score.percentile <= 10.0:
                score.is_underperformer = True
        
        logger.info(
            "Ranked proxies by performance",
            total_proxies=total_proxies,
            top_score=scores[0].overall_score if scores else 0.0,
        )
        
        return scores

    def identify_underperforming_proxies(
        self,
        proxy_metrics: dict[str, ProxyPerformanceMetrics],
        thresholds: Optional[dict[str, float]] = None,
    ) -> list[tuple[str, list[str]]]:
        """
        Identify proxies failing to meet performance thresholds.
        
        Args:
            proxy_metrics: Dictionary of proxy metrics
            thresholds: Performance thresholds
                       Default: uses config values (min_success_rate, max_latency_ms, etc.)
            
        Returns:
            List of tuples: (proxy_id, list of issues)
        """
        if thresholds is None:
            thresholds = {
                "min_success_rate": self.config.min_success_rate,
                "max_latency_ms": self.config.max_latency_ms,
                "min_uptime_hours": self.config.min_uptime_hours,
            }
        
        underperformers: list[tuple[str, list[str]]] = []
        
        for proxy_id, metrics in proxy_metrics.items():
            if metrics.total_requests == 0:
                continue
            
            issues: list[str] = []
            
            # Check success rate
            if metrics.success_rate < thresholds.get("min_success_rate", 0.85):
                issues.append(
                    f"Low success rate: {metrics.success_rate:.2%} "
                    f"(threshold: {thresholds.get('min_success_rate', 0.85):.2%})"
                )
            
            # Check latency
            if metrics.avg_latency_ms > thresholds.get("max_latency_ms", 5000):
                issues.append(
                    f"High latency: {metrics.avg_latency_ms:.0f}ms "
                    f"(threshold: {thresholds.get('max_latency_ms', 5000)}ms)"
                )
            
            # Check uptime
            if metrics.uptime_hours < thresholds.get("min_uptime_hours", 24):
                issues.append(
                    f"Insufficient uptime: {metrics.uptime_hours:.1f}h "
                    f"(threshold: {thresholds.get('min_uptime_hours', 24)}h)"
                )
            
            if issues:
                underperformers.append((proxy_id, issues))
        
        logger.info(
            "Identified underperforming proxies",
            count=len(underperformers),
            total_proxies=len(proxy_metrics),
        )
        
        return underperformers

    def detect_degradation_patterns(
        self,
        historical_data: list[dict[str, Any]],
        window_hours: int = 24,
    ) -> dict[str, dict[str, Any]]:
        """
        Detect performance degradation trends over time.
        
        Args:
            historical_data: List of historical request records
            window_hours: Time window for trend analysis
            
        Returns:
            Dictionary of degradation patterns by proxy_id
        """
        if not historical_data:
            return {}
        
        # Group by proxy and time window
        now = datetime.now()
        window_start = now - timedelta(hours=window_hours)
        
        proxy_windows: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for record in historical_data:
            if record["timestamp"] >= window_start:
                proxy_windows[record["proxy_id"]].append(record)
        
        degradation_patterns: dict[str, dict[str, Any]] = {}
        
        for proxy_id, records in proxy_windows.items():
            if len(records) < 10:  # Need minimum data points
                continue
            
            # Sort by timestamp
            records.sort(key=lambda r: r["timestamp"])
            
            # Split into two halves for comparison
            mid = len(records) // 2
            first_half = records[:mid]
            second_half = records[mid:]
            
            # Calculate metrics for each half
            first_success_rate = sum(1 for r in first_half if r["success"]) / len(first_half)
            second_success_rate = sum(1 for r in second_half if r["success"]) / len(second_half)
            
            first_avg_latency = np.mean([r["latency_ms"] for r in first_half])
            second_avg_latency = np.mean([r["latency_ms"] for r in second_half])
            
            # Detect degradation
            success_rate_change = second_success_rate - first_success_rate
            latency_change = second_avg_latency - first_avg_latency
            
            # Significant degradation thresholds
            if success_rate_change < -0.1 or latency_change > 1000:
                pattern = {
                    "proxy_id": proxy_id,
                    "success_rate_change": success_rate_change,
                    "latency_change_ms": latency_change,
                    "first_half_success_rate": first_success_rate,
                    "second_half_success_rate": second_success_rate,
                    "first_half_avg_latency": first_avg_latency,
                    "second_half_avg_latency": second_avg_latency,
                    "trend": self._determine_trend(success_rate_change, latency_change),
                    "severity": self._calculate_severity(success_rate_change, latency_change),
                }
                degradation_patterns[proxy_id] = pattern
        
        logger.info(
            "Detected degradation patterns",
            degraded_proxies=len(degradation_patterns),
            window_hours=window_hours,
        )
        
        return degradation_patterns

    def generate_performance_recommendations(
        self,
        proxy_metrics: dict[str, ProxyPerformanceMetrics],
        scores: list[PerformanceScore],
        underperformers: list[tuple[str, list[str]]],
    ) -> list[dict[str, Any]]:
        """
        Generate actionable performance recommendations.
        
        Args:
            proxy_metrics: Dictionary of proxy metrics
            scores: Performance scores
            underperformers: List of underperforming proxies
            
        Returns:
            List of recommendations with priority and details
        """
        recommendations: list[dict[str, Any]] = []
        
        # Recommend removing severely underperforming proxies
        for proxy_id, issues in underperformers:
            metrics = proxy_metrics.get(proxy_id)
            if not metrics:
                continue
            
            severity_score = len(issues)
            if metrics.success_rate < 0.5:
                severity_score += 2
            
            if severity_score >= 3:
                recommendations.append({
                    "priority": RecommendationPriority.CRITICAL,
                    "action": "remove_proxy",
                    "proxy_id": proxy_id,
                    "reason": f"Severe performance issues: {'; '.join(issues)}",
                    "impact": "Removing this proxy will improve overall pool quality",
                })
            else:
                recommendations.append({
                    "priority": RecommendationPriority.MEDIUM,
                    "action": "investigate_proxy",
                    "proxy_id": proxy_id,
                    "reason": f"Performance issues detected: {'; '.join(issues)}",
                    "impact": "Investigation may reveal fixable issues",
                })
        
        # Recommend increasing capacity with top performers
        top_performers = [s for s in scores if s.is_top_performer]
        if top_performers:
            recommendations.append({
                "priority": RecommendationPriority.LOW,
                "action": "expand_top_performers",
                "proxy_ids": [s.proxy_id for s in top_performers[:5]],
                "reason": f"Identified {len(top_performers)} top-performing proxies",
                "impact": "Adding more proxies from these sources will improve reliability",
            })
        
        # Check for latency issues
        high_latency_proxies = [
            (pid, m) for pid, m in proxy_metrics.items()
            if m.avg_latency_ms > self.config.max_latency_ms and m.total_requests > 10
        ]
        
        if high_latency_proxies:
            recommendations.append({
                "priority": RecommendationPriority.MEDIUM,
                "action": "optimize_latency",
                "proxy_count": len(high_latency_proxies),
                "reason": f"{len(high_latency_proxies)} proxies exceeding latency threshold",
                "impact": "Consider geographic optimization or connection tuning",
            })
        
        logger.info(
            "Generated performance recommendations",
            total_recommendations=len(recommendations),
        )
        
        return recommendations

    def calculate_statistical_summary(
        self,
        proxy_metrics: dict[str, ProxyPerformanceMetrics],
    ) -> dict[str, Any]:
        """
        Calculate statistical summary of performance metrics.
        
        Args:
            proxy_metrics: Dictionary of proxy metrics
            
        Returns:
            Dictionary with statistical summaries
        """
        if not proxy_metrics:
            return {}
        
        metrics_list = list(proxy_metrics.values())
        active_metrics = [m for m in metrics_list if m.total_requests > 0]
        
        if not active_metrics:
            return {}
        
        # Success rates
        success_rates = [m.success_rate for m in active_metrics]
        
        # Latencies
        latencies = [m.avg_latency_ms for m in active_metrics]
        
        # Availability
        availabilities = [m.availability_percent for m in active_metrics]
        
        summary = {
            "total_proxies": len(proxy_metrics),
            "active_proxies": len(active_metrics),
            "success_rate": {
                "mean": float(np.mean(success_rates)),
                "median": float(np.median(success_rates)),
                "std": float(np.std(success_rates)),
                "min": float(np.min(success_rates)),
                "max": float(np.max(success_rates)),
            },
            "latency_ms": {
                "mean": float(np.mean(latencies)),
                "median": float(np.median(latencies)),
                "p50": float(np.percentile(latencies, 50)),
                "p95": float(np.percentile(latencies, 95)),
                "p99": float(np.percentile(latencies, 99)),
                "min": float(np.min(latencies)),
                "max": float(np.max(latencies)),
            },
            "availability_percent": {
                "mean": float(np.mean(availabilities)),
                "median": float(np.median(availabilities)),
                "min": float(np.min(availabilities)),
                "max": float(np.max(availabilities)),
            },
        }
        
        return summary

    def _determine_trend(
        self,
        success_rate_change: float,
        latency_change: float,
    ) -> TrendDirection:
        """Determine overall trend direction."""
        if success_rate_change < -0.1 or latency_change > 1000:
            return TrendDirection.DECREASING
        elif success_rate_change > 0.1 or latency_change < -1000:
            return TrendDirection.INCREASING
        else:
            return TrendDirection.STABLE

    def _calculate_severity(
        self,
        success_rate_change: float,
        latency_change: float,
    ) -> float:
        """Calculate degradation severity (0-1)."""
        # Combine both factors
        success_severity = max(0, -success_rate_change)  # Negative change = bad
        latency_severity = max(0, latency_change / 5000.0)  # Normalize to 5s
        
        return min(1.0, (success_severity + latency_severity) / 2.0)


__all__ = [
    "PerformanceAnalyzer",
]
