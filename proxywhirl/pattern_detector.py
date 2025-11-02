"""
Pattern detector for usage analysis.

Implements User Story 2: Usage Pattern Detection
- Detect peak hours and usage trends
- Analyze request volumes
- Identify geographic patterns
- Detect anomalies
"""

from datetime import datetime, timedelta
from typing import Any, Optional
from collections import Counter, defaultdict
from uuid import uuid4

import numpy as np
from loguru import logger

from proxywhirl.analytics_models import (
    AnalysisConfig,
    Anomaly,
    AnomalyType,
    TrendDirection,
    UsagePattern,
)


class PatternDetector:
    """
    Detects usage patterns in proxy traffic.
    
    Example:
        ```python
        from proxywhirl import PatternDetector
        
        detector = PatternDetector()
        
        # Detect peak hours
        peak_hours = detector.detect_peak_hours(request_data)
        
        # Detect anomalies
        anomalies = detector.detect_anomalies(request_data)
        ```
    """

    def __init__(self, config: Optional[AnalysisConfig] = None) -> None:
        """
        Initialize pattern detector.
        
        Args:
            config: Analysis configuration
        """
        self.config = config or AnalysisConfig()
        logger.info("Pattern detector initialized")

    def detect_peak_hours(
        self,
        request_data: list[dict[str, Any]],
        percentile: Optional[float] = None,
    ) -> list[int]:
        """
        Detect peak usage hours using time-series analysis.
        
        Args:
            request_data: List of request records with timestamps
            percentile: Percentile threshold for peak detection (default: from config)
            
        Returns:
            List of hours (0-23) identified as peak hours
        """
        if not request_data:
            return []
        
        percentile = percentile or self.config.peak_hour_percentile
        
        # Count requests per hour
        hourly_counts = Counter()
        for record in request_data:
            hour = record["timestamp"].hour
            hourly_counts[hour] += 1
        
        if not hourly_counts:
            return []
        
        # Calculate percentile threshold
        counts = list(hourly_counts.values())
        threshold = np.percentile(counts, percentile * 100)
        
        # Identify peak hours
        peak_hours = [
            hour for hour, count in hourly_counts.items()
            if count >= threshold
        ]
        
        peak_hours.sort()
        
        logger.info(
            "Detected peak hours",
            peak_hours=peak_hours,
            percentile=percentile,
            threshold=threshold,
        )
        
        return peak_hours

    def analyze_request_volumes(
        self,
        request_data: list[dict[str, Any]],
        time_window_hours: int = 1,
    ) -> dict[str, Any]:
        """
        Analyze request volumes with trend detection.
        
        Args:
            request_data: List of request records
            time_window_hours: Time window for aggregation
            
        Returns:
            Dictionary with volume analysis results
        """
        if not request_data:
            return {}
        
        # Sort by timestamp
        sorted_data = sorted(request_data, key=lambda r: r["timestamp"])
        
        # Group into time windows
        windows: dict[datetime, int] = defaultdict(int)
        for record in sorted_data:
            # Round to time window
            ts = record["timestamp"]
            window_start = ts.replace(
                minute=0,
                second=0,
                microsecond=0,
            ) - timedelta(hours=ts.hour % time_window_hours)
            windows[window_start] += 1
        
        if not windows:
            return {}
        
        # Calculate statistics
        volumes = list(windows.values())
        
        # Detect trend
        if len(volumes) >= 3:
            # Simple linear regression for trend
            x = np.arange(len(volumes))
            y = np.array(volumes)
            slope = np.polyfit(x, y, 1)[0]
            
            if slope > 1.0:
                trend = TrendDirection.INCREASING
            elif slope < -1.0:
                trend = TrendDirection.DECREASING
            else:
                trend = TrendDirection.STABLE
        else:
            trend = TrendDirection.STABLE
        
        analysis = {
            "total_requests": len(request_data),
            "time_windows": len(windows),
            "avg_requests_per_window": float(np.mean(volumes)),
            "peak_requests_per_window": int(np.max(volumes)),
            "min_requests_per_window": int(np.min(volumes)),
            "std_requests_per_window": float(np.std(volumes)),
            "trend": trend,
            "window_hours": time_window_hours,
        }
        
        logger.info(
            "Analyzed request volumes",
            total_requests=analysis["total_requests"],
            trend=trend,
        )
        
        return analysis

    def detect_geographic_patterns(
        self,
        request_data: list[dict[str, Any]],
        top_n: int = 10,
    ) -> list[tuple[str, int]]:
        """
        Detect geographic usage patterns.
        
        Args:
            request_data: List of request records with region data
            top_n: Number of top regions to return
            
        Returns:
            List of (region, count) tuples sorted by count
        """
        if not request_data:
            return []
        
        # Count by region
        region_counts = Counter()
        for record in request_data:
            region = record.get("region")
            if region:
                region_counts[region] += 1
        
        # Get top N regions
        top_regions = region_counts.most_common(top_n)
        
        logger.info(
            "Detected geographic patterns",
            total_regions=len(region_counts),
            top_region=top_regions[0] if top_regions else None,
        )
        
        return top_regions

    def detect_anomalies(
        self,
        request_data: list[dict[str, Any]],
        metric_name: str = "request_volume",
        time_window_hours: int = 1,
    ) -> list[Anomaly]:
        """
        Detect anomalies using statistical methods (z-score, IQR).
        
        Args:
            request_data: List of request records
            metric_name: Name of metric to analyze
            time_window_hours: Time window for aggregation
            
        Returns:
            List of detected anomalies
        """
        if not request_data or len(request_data) < 10:
            return []
        
        # Group into time windows
        windows: dict[datetime, int] = defaultdict(int)
        for record in request_data:
            ts = record["timestamp"]
            window_start = ts.replace(
                minute=0,
                second=0,
                microsecond=0,
            ) - timedelta(hours=ts.hour % time_window_hours)
            windows[window_start] += 1
        
        if len(windows) < 10:
            return []
        
        # Calculate statistics
        values = np.array(list(windows.values()))
        mean = np.mean(values)
        std = np.std(values)
        
        # Z-score method
        threshold = self.config.anomaly_std_threshold
        anomalies: list[Anomaly] = []
        
        for window_time, value in windows.items():
            if std > 0:
                z_score = abs((value - mean) / std)
                
                if z_score > threshold:
                    # Determine anomaly type
                    if value > mean:
                        anomaly_type = AnomalyType.SPIKE
                    else:
                        anomaly_type = AnomalyType.DROP
                    
                    # Calculate severity
                    severity = min(1.0, z_score / (threshold * 2))
                    
                    anomaly = Anomaly(
                        anomaly_type=anomaly_type,
                        metric_name=metric_name,
                        expected_value=float(mean),
                        actual_value=float(value),
                        deviation=float(z_score),
                        severity=severity,
                        is_critical=(z_score > threshold * 2),
                        timestamp=window_time,
                        possible_causes=[
                            "Sudden traffic surge" if anomaly_type == AnomalyType.SPIKE
                            else "Service disruption or outage",
                        ],
                        recommendations=[
                            "Investigate traffic source and scaling needs"
                            if anomaly_type == AnomalyType.SPIKE
                            else "Check proxy health and availability",
                        ],
                    )
                    anomalies.append(anomaly)
        
        logger.info(
            "Detected anomalies",
            count=len(anomalies),
            metric=metric_name,
            threshold=threshold,
        )
        
        return anomalies

    def identify_seasonal_patterns(
        self,
        request_data: list[dict[str, Any]],
        min_cycles: int = 2,
    ) -> list[UsagePattern]:
        """
        Identify seasonal/recurring patterns in usage.
        
        Args:
            request_data: List of request records
            min_cycles: Minimum number of cycles to confirm pattern
            
        Returns:
            List of detected seasonal patterns
        """
        if not request_data or len(request_data) < 100:
            return []
        
        patterns: list[UsagePattern] = []
        
        # Analyze daily cycles
        daily_pattern = self._analyze_daily_cycle(request_data)
        if daily_pattern:
            patterns.append(daily_pattern)
        
        # Analyze weekly cycles
        weekly_pattern = self._analyze_weekly_cycle(request_data)
        if weekly_pattern:
            patterns.append(weekly_pattern)
        
        logger.info(
            "Identified seasonal patterns",
            count=len(patterns),
        )
        
        return patterns

    def _analyze_daily_cycle(
        self,
        request_data: list[dict[str, Any]],
    ) -> Optional[UsagePattern]:
        """Analyze daily usage cycle."""
        # Count by hour
        hourly_counts = Counter()
        for record in request_data:
            hour = record["timestamp"].hour
            hourly_counts[hour] += 1
        
        if len(hourly_counts) < 10:
            return None
        
        # Find peak hours
        mean_count = np.mean(list(hourly_counts.values()))
        peak_hours = [
            hour for hour, count in hourly_counts.items()
            if count > mean_count * 1.5
        ]
        
        if not peak_hours:
            return None
        
        # Calculate confidence based on consistency
        values = list(hourly_counts.values())
        cv = np.std(values) / np.mean(values) if np.mean(values) > 0 else 1.0
        confidence = max(0.0, min(1.0, 1.0 - cv))
        
        pattern = UsagePattern(
            pattern_type="daily_cycle",
            description=f"Daily usage peaks during hours {peak_hours}",
            confidence=confidence,
            peak_hours=peak_hours,
            avg_requests_per_hour=mean_count,
            peak_requests_per_hour=max(hourly_counts.values()),
            trend=TrendDirection.STABLE,
            time_range_start=min(r["timestamp"] for r in request_data),
            time_range_end=max(r["timestamp"] for r in request_data),
            data_points=len(request_data),
        )
        
        return pattern

    def _analyze_weekly_cycle(
        self,
        request_data: list[dict[str, Any]],
    ) -> Optional[UsagePattern]:
        """Analyze weekly usage cycle."""
        # Count by day of week (0=Monday, 6=Sunday)
        daily_counts = Counter()
        for record in request_data:
            day = record["timestamp"].weekday()
            daily_counts[day] += 1
        
        if len(daily_counts) < 5:
            return None
        
        # Find peak days
        mean_count = np.mean(list(daily_counts.values()))
        peak_days = [
            day for day, count in daily_counts.items()
            if count > mean_count * 1.2
        ]
        
        if not peak_days:
            return None
        
        # Calculate confidence
        values = list(daily_counts.values())
        cv = np.std(values) / np.mean(values) if np.mean(values) > 0 else 1.0
        confidence = max(0.0, min(1.0, 1.0 - cv))
        
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        peak_day_names = [day_names[d] for d in peak_days]
        
        pattern = UsagePattern(
            pattern_type="weekly_cycle",
            description=f"Weekly usage peaks on {', '.join(peak_day_names)}",
            confidence=confidence,
            peak_days=peak_days,
            trend=TrendDirection.STABLE,
            time_range_start=min(r["timestamp"] for r in request_data),
            time_range_end=max(r["timestamp"] for r in request_data),
            data_points=len(request_data),
        )
        
        return pattern

    def calculate_capacity_metrics(
        self,
        request_data: list[dict[str, Any]],
        proxy_count: int,
    ) -> dict[str, Any]:
        """
        Calculate capacity and utilization metrics.
        
        Args:
            request_data: List of request records
            proxy_count: Number of proxies in pool
            
        Returns:
            Dictionary with capacity metrics
        """
        if not request_data or proxy_count <= 0:
            return {}
        
        # Calculate time span
        timestamps = [r["timestamp"] for r in request_data]
        time_span = (max(timestamps) - min(timestamps)).total_seconds() / 3600  # hours
        
        if time_span <= 0:
            return {}
        
        # Calculate request rate
        requests_per_hour = len(request_data) / time_span
        requests_per_proxy_per_hour = requests_per_hour / proxy_count
        
        # Estimate capacity utilization
        # Assume each proxy can handle ~100 requests/hour at full capacity
        estimated_max_capacity = proxy_count * 100
        utilization_percent = (requests_per_hour / estimated_max_capacity) * 100
        
        metrics = {
            "total_proxies": proxy_count,
            "time_span_hours": time_span,
            "total_requests": len(request_data),
            "requests_per_hour": requests_per_hour,
            "requests_per_proxy_per_hour": requests_per_proxy_per_hour,
            "estimated_max_capacity": estimated_max_capacity,
            "utilization_percent": min(100.0, utilization_percent),
            "headroom_percent": max(0.0, 100.0 - utilization_percent),
        }
        
        logger.info(
            "Calculated capacity metrics",
            utilization=f"{metrics['utilization_percent']:.1f}%",
        )
        
        return metrics


__all__ = [
    "PatternDetector",
]
