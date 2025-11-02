"""
Usage pattern detector for ProxyWhirl analytics engine.

Detects usage patterns including peak hours, request volumes, geographic
distribution, and anomalies.
"""

import statistics
from collections import Counter, defaultdict
from datetime import datetime, time, timedelta
from typing import Any, Optional

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
    Detects usage patterns in proxy request data.
    
    Analyzes temporal patterns, geographic distribution, and identifies
    anomalies in usage behavior.
    
    Example:
        ```python
        from proxywhirl import PatternDetector, AnalysisConfig
        
        detector = PatternDetector(config=AnalysisConfig())
        
        # Detect peak hours
        peak_hours = detector.detect_peak_hours(request_data)
        
        # Analyze geographic patterns
        geo_patterns = detector.detect_geographic_patterns(request_data)
        
        # Detect anomalies
        anomalies = detector.detect_anomalies(request_data)
        ```
    """

    def __init__(self, config: Optional[AnalysisConfig] = None) -> None:
        """
        Initialize pattern detector.
        
        Args:
            config: Analysis configuration (default: AnalysisConfig())
        """
        self.config = config or AnalysisConfig()
        logger.debug("Pattern detector initialized")

    def detect_peak_hours(
        self,
        request_data: list[dict[str, Any]],
    ) -> UsagePattern:
        """
        Detect peak usage hours from request data.
        
        Args:
            request_data: List of request records with timestamps
            
        Returns:
            Usage pattern with peak hour information
        """
        if not request_data:
            raise ValueError("No request data provided")
        
        # Count requests by hour
        hourly_counts = Counter()
        for record in request_data:
            timestamp = record.get("timestamp")
            if isinstance(timestamp, datetime):
                hourly_counts[timestamp.hour] += 1
        
        if not hourly_counts:
            raise ValueError("No valid timestamps in request data")
        
        # Calculate average and threshold
        avg_requests_per_hour = statistics.mean(hourly_counts.values())
        threshold = avg_requests_per_hour * self.config.peak_hour_threshold
        
        # Identify peak hours
        peak_hours = [
            hour for hour, count in hourly_counts.items()
            if count >= threshold
        ]
        
        # Determine trend
        hours_sorted = sorted(hourly_counts.items())
        first_half_avg = statistics.mean(count for _, count in hours_sorted[:12])
        second_half_avg = statistics.mean(count for _, count in hours_sorted[12:])
        
        if second_half_avg > first_half_avg * 1.2:
            trend = TrendDirection.INCREASING
        elif second_half_avg < first_half_avg * 0.8:
            trend = TrendDirection.DECREASING
        else:
            trend = TrendDirection.STABLE
        
        # Get time range
        timestamps = [r["timestamp"] for r in request_data if "timestamp" in r]
        start_time = min(timestamps)
        end_time = max(timestamps)
        
        pattern = UsagePattern(
            pattern_type="peak_hours",
            description=f"Detected {len(peak_hours)} peak usage hours with "
                       f"traffic exceeding {threshold:.0f} requests/hour",
            peak_hours=sorted(peak_hours),
            avg_requests_per_hour=avg_requests_per_hour,
            max_requests_per_hour=max(hourly_counts.values()),
            trend_direction=trend,
            confidence=0.9,
            start_time=start_time,
            end_time=end_time,
        )
        
        logger.info(f"Detected peak hours: {peak_hours}")
        return pattern

    def analyze_request_volumes(
        self,
        request_data: list[dict[str, Any]],
        interval_hours: int = 1,
    ) -> UsagePattern:
        """
        Analyze request volume trends over time.
        
        Args:
            request_data: List of request records with timestamps
            interval_hours: Time interval for aggregation
            
        Returns:
            Usage pattern with volume trend information
        """
        if not request_data:
            raise ValueError("No request data provided")
        
        # Group by time intervals
        interval_counts: dict[datetime, int] = defaultdict(int)
        
        for record in request_data:
            timestamp = record.get("timestamp")
            if isinstance(timestamp, datetime):
                # Round to interval
                interval_key = timestamp.replace(
                    minute=0, second=0, microsecond=0
                )
                interval_counts[interval_key] += 1
        
        if not interval_counts:
            raise ValueError("No valid timestamps in request data")
        
        # Calculate statistics
        counts = list(interval_counts.values())
        avg_volume = statistics.mean(counts)
        max_volume = max(counts)
        
        # Determine trend using linear regression
        sorted_intervals = sorted(interval_counts.items())
        volumes = [count for _, count in sorted_intervals]
        
        if len(volumes) >= 2:
            # Simple trend detection
            first_third = volumes[:len(volumes)//3]
            last_third = volumes[-len(volumes)//3:]
            
            first_avg = statistics.mean(first_third)
            last_avg = statistics.mean(last_third)
            
            if last_avg > first_avg * 1.3:
                trend = TrendDirection.INCREASING
            elif last_avg < first_avg * 0.7:
                trend = TrendDirection.DECREASING
            else:
                # Check volatility
                std_dev = statistics.stdev(volumes) if len(volumes) > 1 else 0
                if std_dev > avg_volume * 0.5:
                    trend = TrendDirection.VOLATILE
                else:
                    trend = TrendDirection.STABLE
        else:
            trend = TrendDirection.STABLE
        
        timestamps = [r["timestamp"] for r in request_data if "timestamp" in r]
        
        pattern = UsagePattern(
            pattern_type="volume_trend",
            description=f"Request volume averaging {avg_volume:.1f} requests per "
                       f"{interval_hours}h with {trend.value} trend",
            avg_requests_per_hour=avg_volume / interval_hours,
            max_requests_per_hour=max_volume / interval_hours,
            trend_direction=trend,
            confidence=0.85,
            start_time=min(timestamps),
            end_time=max(timestamps),
        )
        
        logger.info(f"Analyzed request volumes: {trend.value} trend")
        return pattern

    def detect_geographic_patterns(
        self,
        request_data: list[dict[str, Any]],
    ) -> UsagePattern:
        """
        Detect geographic usage patterns.
        
        Args:
            request_data: List of request records with region information
            
        Returns:
            Usage pattern with geographic distribution
        """
        if not request_data:
            raise ValueError("No request data provided")
        
        # Count requests by region
        region_counts = Counter()
        total_requests = 0
        
        for record in request_data:
            region = record.get("region")
            if region:
                region_counts[region] += 1
                total_requests += 1
        
        if not region_counts:
            raise ValueError("No region data available")
        
        # Get top regions
        top_regions = dict(region_counts.most_common(10))
        
        # Calculate concentration
        top_region_count = region_counts.most_common(1)[0][1]
        concentration = (top_region_count / total_requests) * 100
        
        timestamps = [r["timestamp"] for r in request_data if "timestamp" in r]
        
        pattern = UsagePattern(
            pattern_type="geographic_distribution",
            description=f"Top region accounts for {concentration:.1f}% of traffic "
                       f"across {len(region_counts)} total regions",
            top_regions=top_regions,
            confidence=0.9,
            start_time=min(timestamps) if timestamps else datetime.now(),
            end_time=max(timestamps) if timestamps else datetime.now(),
        )
        
        logger.info(f"Detected geographic patterns across {len(region_counts)} regions")
        return pattern

    def detect_anomalies(
        self,
        request_data: list[dict[str, Any]],
        metric: str = "count",
    ) -> list[Anomaly]:
        """
        Detect anomalies in request data using statistical methods.
        
        Uses z-score method to identify outliers.
        
        Args:
            request_data: List of request records
            metric: Metric to analyze for anomalies (count, latency, etc.)
            
        Returns:
            List of detected anomalies
        """
        if not request_data:
            return []
        
        anomalies: list[Anomaly] = []
        
        # Group by hourly intervals
        hourly_data: dict[datetime, list[float]] = defaultdict(list)
        
        for record in request_data:
            timestamp = record.get("timestamp")
            if not isinstance(timestamp, datetime):
                continue
            
            hour_key = timestamp.replace(minute=0, second=0, microsecond=0)
            
            if metric == "count":
                hourly_data[hour_key].append(1.0)
            elif metric == "latency":
                latency = record.get("latency_ms")
                if latency is not None:
                    hourly_data[hour_key].append(float(latency))
        
        # Calculate hourly aggregates
        hourly_values = {
            hour: sum(values) if metric == "count" else statistics.mean(values)
            for hour, values in hourly_data.items()
        }
        
        if len(hourly_values) < 3:
            return []
        
        # Calculate mean and standard deviation
        values = list(hourly_values.values())
        mean_value = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        
        if std_dev == 0:
            return []
        
        # Detect outliers using z-score
        for hour, value in hourly_values.items():
            z_score = (value - mean_value) / std_dev
            
            if abs(z_score) >= self.config.anomaly_threshold:
                anomaly_type = (
                    AnomalyType.USAGE_SPIKE if z_score > 0
                    else AnomalyType.USAGE_DROP
                )
                
                anomalies.append(
                    Anomaly(
                        anomaly_type=anomaly_type,
                        description=f"Unusual {metric} detected: {value:.1f} vs "
                                   f"expected {mean_value:.1f}",
                        severity=min(abs(z_score) / 10, 1.0),
                        expected_value=mean_value,
                        actual_value=value,
                        deviation=z_score,
                        affected_entities=[],
                        time_period_start=hour,
                        time_period_end=hour + timedelta(hours=1),
                    )
                )
        
        logger.info(f"Detected {len(anomalies)} anomalies in {metric}")
        return anomalies
