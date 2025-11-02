"""
Core analytics engine for ProxyWhirl.

Provides comprehensive analytics capabilities including performance analysis,
usage pattern detection, failure analysis, cost/ROI tracking, and predictive forecasting.
"""

import threading
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Optional
from uuid import UUID

from loguru import logger

from proxywhirl.analytics_models import (
    AnalysisConfig,
    AnalysisReport,
    AnalysisType,
    AnalyticsQuery,
    ExportFormat,
    ProxyPerformanceMetrics,
)


class AnalyticsEngine:
    """
    Core analytics engine for proxy performance analysis.
    
    Provides thread-safe data collection and analysis capabilities for:
    - Proxy performance metrics and scoring
    - Usage pattern detection and anomaly identification
    - Failure analysis and root cause detection
    - Cost/ROI analysis and forecasting
    - Predictive analytics for capacity planning
    
    Example:
        ```python
        from proxywhirl import AnalyticsEngine, AnalysisConfig
        
        engine = AnalyticsEngine(config=AnalysisConfig(lookback_days=30))
        
        # Record request metrics
        engine.record_request(
            proxy_id="proxy-1",
            success=True,
            latency_ms=250.0,
            timestamp=datetime.now()
        )
        
        # Generate performance analysis
        report = engine.analyze_performance()
        print(f"Top performers: {report.key_findings}")
        ```
    """

    def __init__(
        self,
        config: Optional[AnalysisConfig] = None,
    ) -> None:
        """
        Initialize analytics engine.
        
        Args:
            config: Analytics configuration (default: AnalysisConfig())
        """
        self.config = config or AnalysisConfig()
        
        # Thread-safe data storage
        self._lock = threading.RLock()
        self._request_data: list[dict[str, Any]] = []
        self._proxy_metrics: dict[str, ProxyPerformanceMetrics] = {}
        
        # Analysis cache
        self._cache_enabled = self.config.cache_results
        self._cache: dict[str, tuple[datetime, AnalysisReport]] = {}
        self._cache_ttl = timedelta(seconds=self.config.cache_ttl_seconds)
        
        logger.info(
            "Analytics engine initialized",
            lookback_days=self.config.lookback_days,
            cache_enabled=self._cache_enabled,
        )

    def record_request(
        self,
        proxy_id: str,
        proxy_url: str,
        success: bool,
        latency_ms: float,
        timestamp: Optional[datetime] = None,
        pool: Optional[str] = None,
        region: Optional[str] = None,
        target_domain: Optional[str] = None,
        error_type: Optional[str] = None,
        **metadata: Any,
    ) -> None:
        """
        Record a proxy request for analytics.
        
        Args:
            proxy_id: Unique proxy identifier
            proxy_url: Proxy URL
            success: Whether request succeeded
            latency_ms: Request latency in milliseconds
            timestamp: Request timestamp (default: now)
            pool: Proxy pool name
            region: Geographic region
            target_domain: Target domain requested
            error_type: Error type if failed
            **metadata: Additional metadata
        """
        timestamp = timestamp or datetime.now()
        
        with self._lock:
            # Record raw request data
            request_record = {
                "proxy_id": proxy_id,
                "proxy_url": proxy_url,
                "success": success,
                "latency_ms": latency_ms,
                "timestamp": timestamp,
                "pool": pool,
                "region": region,
                "target_domain": target_domain,
                "error_type": error_type,
                **metadata,
            }
            self._request_data.append(request_record)
            
            # Update proxy metrics
            if proxy_id not in self._proxy_metrics:
                self._proxy_metrics[proxy_id] = ProxyPerformanceMetrics(
                    proxy_id=proxy_id,
                    proxy_url=proxy_url,
                    first_seen=timestamp,
                    last_seen=timestamp,
                    pool=pool,
                    region=region,
                )
            
            metrics = self._proxy_metrics[proxy_id]
            metrics.total_requests += 1
            
            if success:
                metrics.successful_requests += 1
            else:
                metrics.failed_requests += 1
            
            # Update success rate
            if metrics.total_requests > 0:
                metrics.success_rate = (
                    metrics.successful_requests / metrics.total_requests
                )
            
            # Update latency statistics
            self._update_latency_stats(metrics, latency_ms)
            
            # Update last seen
            metrics.last_seen = timestamp
            
            # Invalidate cache
            if self._cache_enabled:
                self._invalidate_cache()

    def _update_latency_stats(
        self,
        metrics: ProxyPerformanceMetrics,
        latency_ms: float,
    ) -> None:
        """Update latency statistics for proxy metrics."""
        # Simple incremental update (for more accurate stats, store all latencies)
        n = metrics.total_requests
        
        if n == 1:
            metrics.avg_latency_ms = latency_ms
            metrics.min_latency_ms = latency_ms
            metrics.max_latency_ms = latency_ms
            metrics.p50_latency_ms = latency_ms
            metrics.p95_latency_ms = latency_ms
            metrics.p99_latency_ms = latency_ms
        else:
            # Update average (incremental)
            metrics.avg_latency_ms = (
                (metrics.avg_latency_ms * (n - 1) + latency_ms) / n
            )
            
            # Update min/max
            metrics.min_latency_ms = min(metrics.min_latency_ms, latency_ms)
            metrics.max_latency_ms = max(metrics.max_latency_ms, latency_ms)
            
            # Note: Percentiles require full dataset for accuracy
            # For production, consider using quantile sketch algorithms

    def record_proxy_uptime(
        self,
        proxy_id: str,
        uptime_hours: float,
        downtime_hours: float = 0.0,
    ) -> None:
        """
        Record proxy uptime/downtime.
        
        Args:
            proxy_id: Unique proxy identifier
            uptime_hours: Hours proxy was available
            downtime_hours: Hours proxy was unavailable
        """
        with self._lock:
            if proxy_id in self._proxy_metrics:
                metrics = self._proxy_metrics[proxy_id]
                metrics.uptime_hours = uptime_hours
                metrics.downtime_hours = downtime_hours
                
                total_hours = uptime_hours + downtime_hours
                if total_hours > 0:
                    metrics.availability_percent = (
                        (uptime_hours / total_hours) * 100.0
                    )

    def get_proxy_metrics(
        self,
        proxy_id: Optional[str] = None,
    ) -> dict[str, ProxyPerformanceMetrics]:
        """
        Get performance metrics for proxies.
        
        Args:
            proxy_id: Specific proxy ID (None = all proxies)
            
        Returns:
            Dictionary of proxy metrics keyed by proxy_id
        """
        with self._lock:
            if proxy_id:
                return {proxy_id: self._proxy_metrics.get(proxy_id)}  # type: ignore[dict-item]
            return dict(self._proxy_metrics)

    def get_request_data(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """
        Get filtered request data.
        
        Args:
            start_time: Filter start time
            end_time: Filter end time
            filters: Additional filters (pool, region, proxy_id, etc.)
            
        Returns:
            List of request records matching filters
        """
        with self._lock:
            data = self._request_data.copy()
        
        # Apply time filters
        if start_time:
            data = [r for r in data if r["timestamp"] >= start_time]
        if end_time:
            data = [r for r in data if r["timestamp"] <= end_time]
        
        # Apply additional filters
        if filters:
            for key, value in filters.items():
                if value is not None:
                    data = [r for r in data if r.get(key) == value]
        
        return data

    def analyze(
        self,
        query: Optional[AnalyticsQuery] = None,
    ) -> AnalysisReport:
        """
        Run comprehensive analysis based on query.
        
        Args:
            query: Analytics query with analysis types and filters
            
        Returns:
            Complete analysis report with findings and recommendations
        """
        query = query or AnalyticsQuery()
        analysis_start = datetime.now()
        
        # Check cache
        cache_key = self._generate_cache_key(query)
        if self._cache_enabled and cache_key in self._cache:
            cached_time, cached_report = self._cache[cache_key]
            if datetime.now() - cached_time < self._cache_ttl:
                logger.info("Returning cached analysis report", cache_key=cache_key)
                return cached_report
        
        # Determine time range
        if query.start_time and query.end_time:
            start_time = query.start_time
            end_time = query.end_time
        else:
            end_time = datetime.now()
            lookback = query.lookback_days or self.config.lookback_days
            start_time = end_time - timedelta(days=lookback)
        
        # Get filtered data
        filters = {}
        if query.proxy_ids:
            filters["proxy_id"] = query.proxy_ids
        if query.pools:
            filters["pool"] = query.pools
        if query.regions:
            filters["region"] = query.regions
        
        logger.info(
            "Starting analytics analysis",
            analysis_types=query.analysis_types,
            time_range=(start_time, end_time),
            filters=filters,
        )
        
        # Create report
        report = AnalysisReport(
            analysis_type=(
                query.analysis_types[0]
                if query.analysis_types
                else AnalysisType.COMPREHENSIVE
            ),
            title=f"ProxyWhirl Analytics Report - {analysis_start.strftime('%Y-%m-%d %H:%M')}",
            description="Comprehensive analytics analysis of proxy performance and usage",
            analysis_start=start_time,
            analysis_end=end_time,
            total_duration=timedelta(seconds=0),  # Will be updated
            config=self.config,
        )
        
        # Run requested analyses
        if AnalysisType.PERFORMANCE in query.analysis_types:
            self._analyze_performance(report, start_time, end_time, filters)
        
        if AnalysisType.USAGE_PATTERNS in query.analysis_types:
            self._analyze_patterns(report, start_time, end_time, filters)
        
        if AnalysisType.FAILURE_ANALYSIS in query.analysis_types:
            self._analyze_failures(report, start_time, end_time, filters)
        
        if AnalysisType.COST_ROI in query.analysis_types:
            self._analyze_costs(report, start_time, end_time, filters)
        
        if AnalysisType.PREDICTIVE in query.analysis_types:
            self._analyze_predictions(report, start_time, end_time, filters)
        
        # Finalize report
        analysis_end = datetime.now()
        report.total_duration = analysis_end - analysis_start
        
        # Cache result
        if self._cache_enabled:
            self._cache[cache_key] = (datetime.now(), report)
        
        logger.info(
            "Analysis complete",
            duration_seconds=report.total_duration.total_seconds(),
            key_findings_count=len(report.key_findings),
        )
        
        return report

    def _analyze_performance(
        self,
        report: AnalysisReport,
        start_time: datetime,
        end_time: datetime,
        filters: dict[str, Any],
    ) -> None:
        """Analyze proxy performance metrics."""
        # Placeholder - will be implemented by PerformanceAnalyzer
        report.performance_results = self.get_proxy_metrics()
        report.key_findings.append("Performance analysis placeholder")

    def _analyze_patterns(
        self,
        report: AnalysisReport,
        start_time: datetime,
        end_time: datetime,
        filters: dict[str, Any],
    ) -> None:
        """Analyze usage patterns."""
        # Placeholder - will be implemented by PatternDetector
        report.usage_patterns = []
        report.key_findings.append("Pattern analysis placeholder")

    def _analyze_failures(
        self,
        report: AnalysisReport,
        start_time: datetime,
        end_time: datetime,
        filters: dict[str, Any],
    ) -> None:
        """Analyze failure patterns."""
        # Placeholder - will be implemented by FailureAnalyzer
        report.key_findings.append("Failure analysis placeholder")

    def _analyze_costs(
        self,
        report: AnalysisReport,
        start_time: datetime,
        end_time: datetime,
        filters: dict[str, Any],
    ) -> None:
        """Analyze costs and ROI."""
        # Placeholder - will be implemented by CostAnalyzer
        report.key_findings.append("Cost analysis placeholder")

    def _analyze_predictions(
        self,
        report: AnalysisReport,
        start_time: datetime,
        end_time: datetime,
        filters: dict[str, Any],
    ) -> None:
        """Generate predictive forecasts."""
        # Placeholder - will be implemented by PredictiveAnalytics
        report.key_findings.append("Predictive analysis placeholder")

    def export_report(
        self,
        report: AnalysisReport,
        format: ExportFormat,
        output_path: str,
    ) -> None:
        """
        Export analysis report to file.
        
        Args:
            report: Analysis report to export
            format: Export format (CSV, JSON, PDF)
            output_path: Output file path
        """
        import json
        from pathlib import Path
        
        output_file = Path(output_path)
        
        if format == ExportFormat.JSON:
            with open(output_file, "w") as f:
                json.dump(report.model_dump(mode="json"), f, indent=2, default=str)
            logger.info("Exported report to JSON", path=output_path)
        
        elif format == ExportFormat.CSV:
            # CSV export for tabular data
            import csv
            
            with open(output_file, "w", newline="") as f:
                if report.performance_results:
                    writer = csv.DictWriter(
                        f,
                        fieldnames=["proxy_id", "success_rate", "avg_latency_ms", "total_requests"],
                    )
                    writer.writeheader()
                    for metrics in report.performance_results.values():
                        writer.writerow({
                            "proxy_id": metrics.proxy_id,
                            "success_rate": metrics.success_rate,
                            "avg_latency_ms": metrics.avg_latency_ms,
                            "total_requests": metrics.total_requests,
                        })
            logger.info("Exported report to CSV", path=output_path)
        
        else:
            logger.warning("Export format not yet implemented", format=format)
        
        # Update report
        if report.exported_to is None:
            report.exported_to = []
        report.exported_to.append(output_path)

    def clear_data(self, before: Optional[datetime] = None) -> int:
        """
        Clear old data to free memory.
        
        Args:
            before: Clear data before this timestamp (None = clear all)
            
        Returns:
            Number of records cleared
        """
        with self._lock:
            if before is None:
                count = len(self._request_data)
                self._request_data.clear()
                self._proxy_metrics.clear()
                self._cache.clear()
                logger.info("Cleared all analytics data", records_cleared=count)
                return count
            
            original_count = len(self._request_data)
            self._request_data = [
                r for r in self._request_data if r["timestamp"] >= before
            ]
            cleared = original_count - len(self._request_data)
            
            # Clear cache
            self._cache.clear()
            
            logger.info(
                "Cleared old analytics data",
                records_cleared=cleared,
                cutoff_time=before,
            )
            return cleared

    def _generate_cache_key(self, query: AnalyticsQuery) -> str:
        """Generate cache key for query."""
        parts = [
            ",".join(sorted(str(t) for t in query.analysis_types)),
            str(query.start_time),
            str(query.end_time),
            str(query.lookback_days),
            str(sorted(query.proxy_ids or [])),
            str(sorted(query.pools or [])),
            str(sorted(query.regions or [])),
        ]
        return ":".join(parts)

    def _invalidate_cache(self) -> None:
        """Invalidate all cached analysis results."""
        self._cache.clear()

    def get_stats(self) -> dict[str, Any]:
        """
        Get analytics engine statistics.
        
        Returns:
            Dictionary of engine statistics
        """
        with self._lock:
            return {
                "total_requests_recorded": len(self._request_data),
                "total_proxies_tracked": len(self._proxy_metrics),
                "cache_enabled": self._cache_enabled,
                "cached_reports": len(self._cache),
                "config": self.config.model_dump(),
            }


__all__ = [
    "AnalyticsEngine",
]
