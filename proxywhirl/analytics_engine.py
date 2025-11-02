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
    PerformanceScore,
    ProxyPerformanceMetrics,
    TimeSeriesData,
)
from proxywhirl.performance_analyzer import PerformanceAnalyzer


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
            proxy_url="http://proxy1.example.com:8080",
            success=True,
            latency_ms=250.0,
            timestamp=datetime.now()
        )
        
        # Generate performance analysis
        report = engine.analyze_performance()
        print(f"Top performers: {report.key_findings}")
        
        # Export report
        engine.export_to_json(report, "analytics_report.json")
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
        
        # Component analyzers
        self.performance_analyzer = PerformanceAnalyzer(config=self.config)
        
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
                if error_type:
                    metrics.error_counts[error_type] = metrics.error_counts.get(error_type, 0) + 1
            
            # Update success rate
            if metrics.total_requests > 0:
                metrics.success_rate = (
                    metrics.successful_requests / metrics.total_requests
                )
            
            # Update latency statistics (simplified incremental update)
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
            # For production, consider using t-digest or DDSketch algorithms

    def record_proxy_uptime(
        self,
        proxy_id: str,
        uptime_hours: float,
        downtime_hours: float = 0.0,
    ) -> None:
        """
        Record proxy uptime/downtime for availability tracking.
        
        Args:
            proxy_id: Unique proxy identifier
            uptime_hours: Hours of uptime to add
            downtime_hours: Hours of downtime to add
        """
        with self._lock:
            if proxy_id in self._proxy_metrics:
                metrics = self._proxy_metrics[proxy_id]
                metrics.total_uptime_hours += uptime_hours
                metrics.total_downtime_hours += downtime_hours
                
                # Recalculate uptime percentage
                total_hours = metrics.total_uptime_hours + metrics.total_downtime_hours
                if total_hours > 0:
                    metrics.uptime_percentage = (
                        metrics.total_uptime_hours / total_hours
                    ) * 100.0

    def analyze_performance(
        self,
        query: Optional[AnalyticsQuery] = None,
    ) -> AnalysisReport:
        """
        Perform comprehensive proxy performance analysis.
        
        Analyzes success rates, latency, uptime, and generates performance
        scores with rankings and recommendations.
        
        Args:
            query: Optional query parameters for filtering and configuration
            
        Returns:
            Analysis report with findings and recommendations
        """
        start_time = datetime.now()
        query = query or AnalyticsQuery()
        
        # Check cache
        cache_key = self._generate_cache_key("performance", query)
        if self._cache_enabled and cache_key in self._cache:
            cached_time, cached_report = self._cache[cache_key]
            if datetime.now() - cached_time < self._cache_ttl:
                logger.info("Returning cached performance analysis")
                return cached_report
        
        with self._lock:
            # Filter metrics based on query
            filtered_metrics = self._filter_metrics(query)
            
            if not filtered_metrics:
                logger.warning("No metrics available for performance analysis")
                return self._create_empty_report(
                    "Performance Analysis",
                    AnalysisType.PERFORMANCE,
                    query,
                )
            
            # Calculate performance scores
            scores = self.performance_analyzer.calculate_performance_scores(filtered_metrics)
            
            # Rank proxies
            ranked = self.performance_analyzer.rank_proxies(scores)
            
            # Identify underperformers
            underperformers = self.performance_analyzer.identify_underperforming_proxies(
                filtered_metrics
            )
            
            # Generate recommendations
            recommendations = self.performance_analyzer.generate_performance_recommendations(
                filtered_metrics,
                scores,
            )
            
            # Calculate statistical summary
            stats = self.performance_analyzer.calculate_statistical_summary(
                list(filtered_metrics.values())
            )
            
            # Generate key findings
            key_findings = self._generate_performance_findings(
                filtered_metrics,
                scores,
                ranked,
                underperformers,
                stats,
            )
            
            # Create report
            end_time = datetime.now()
            analysis_duration = (end_time - start_time).total_seconds()
            
            report = AnalysisReport(
                report_title="Proxy Performance Analysis",
                analysis_type=AnalysisType.PERFORMANCE,
                period_start=query.start_time or (end_time - timedelta(days=self.config.lookback_days)),
                period_end=query.end_time or end_time,
                executive_summary=self._generate_performance_summary(
                    len(filtered_metrics),
                    len(underperformers),
                    stats,
                ),
                key_findings=key_findings,
                performance_metrics=filtered_metrics,
                performance_scores=scores,
                recommendations=recommendations if query.include_recommendations else [],
                total_requests_analyzed=sum(m.total_requests for m in filtered_metrics.values()),
                total_proxies_analyzed=len(filtered_metrics),
                analysis_duration_seconds=analysis_duration,
                export_formats_available=self.config.export_formats,
            )
            
            # Cache result
            if self._cache_enabled:
                self._cache[cache_key] = (datetime.now(), report)
            
            logger.info(
                "Performance analysis complete",
                proxies_analyzed=len(filtered_metrics),
                underperformers=len(underperformers),
                duration_seconds=analysis_duration,
            )
            
            return report

    def _filter_metrics(
        self,
        query: AnalyticsQuery,
    ) -> dict[str, ProxyPerformanceMetrics]:
        """Filter proxy metrics based on query parameters."""
        filtered: dict[str, ProxyPerformanceMetrics] = {}
        
        for proxy_id, metrics in self._proxy_metrics.items():
            # Apply proxy_id filter
            if query.proxy_ids and proxy_id not in query.proxy_ids:
                continue
            
            # Apply pool filter
            if query.pools and metrics.pool not in query.pools:
                continue
            
            # Apply region filter
            if query.regions and metrics.region not in query.regions:
                continue
            
            # Apply time filter
            if query.start_time and metrics.last_seen < query.start_time:
                continue
            if query.end_time and metrics.first_seen > query.end_time:
                continue
            
            filtered[proxy_id] = metrics
        
        # Apply limit
        config = query.config or self.config
        if config.max_proxies_analyzed and len(filtered) > config.max_proxies_analyzed:
            # Keep top N by request count
            sorted_proxies = sorted(
                filtered.items(),
                key=lambda x: x[1].total_requests,
                reverse=True,
            )
            filtered = dict(sorted_proxies[:config.max_proxies_analyzed])
        
        return filtered

    def _generate_cache_key(self, analysis_type: str, query: AnalyticsQuery) -> str:
        """Generate cache key for analysis results."""
        return f"{analysis_type}:{hash(str(query))}"

    def _invalidate_cache(self) -> None:
        """Invalidate all cached analysis results."""
        self._cache.clear()

    def _create_empty_report(
        self,
        title: str,
        analysis_type: AnalysisType,
        query: AnalyticsQuery,
    ) -> AnalysisReport:
        """Create empty analysis report when no data is available."""
        end_time = datetime.now()
        return AnalysisReport(
            report_title=title,
            analysis_type=analysis_type,
            period_start=query.start_time or (end_time - timedelta(days=self.config.lookback_days)),
            period_end=query.end_time or end_time,
            executive_summary="No data available for analysis.",
            key_findings=["Insufficient data for analysis"],
            total_requests_analyzed=0,
            total_proxies_analyzed=0,
            analysis_duration_seconds=0.0,
            export_formats_available=self.config.export_formats,
        )

    def _generate_performance_findings(
        self,
        metrics: dict[str, ProxyPerformanceMetrics],
        scores: dict[str, PerformanceScore],
        ranked: list[tuple[str, PerformanceScore]],
        underperformers: dict[str, ProxyPerformanceMetrics],
        stats: dict[str, Any],
    ) -> list[str]:
        """Generate key findings for performance analysis."""
        findings: list[str] = []
        
        # Overall statistics
        total_proxies = len(metrics)
        total_requests = sum(m.total_requests for m in metrics.values())
        findings.append(
            f"Analyzed {total_proxies} proxies with {total_requests:,} total requests"
        )
        
        # Average performance
        if "success_rate" in stats:
            avg_success = stats["success_rate"]["mean"] * 100
            findings.append(
                f"Average success rate: {avg_success:.1f}% "
                f"(range: {stats['success_rate']['min']*100:.1f}% - "
                f"{stats['success_rate']['max']*100:.1f}%)"
            )
        
        if "avg_latency_ms" in stats:
            avg_latency = stats["avg_latency_ms"]["mean"]
            findings.append(
                f"Average latency: {avg_latency:.0f}ms "
                f"(median: {stats['avg_latency_ms']['median']:.0f}ms)"
            )
        
        # Top performers
        if ranked:
            top_5 = ranked[:min(5, len(ranked))]
            top_scores = [score.overall_score for _, score in top_5]
            findings.append(
                f"Top 5 performers have scores ranging from "
                f"{min(top_scores):.1f} to {max(top_scores):.1f}"
            )
        
        # Underperformers
        if underperformers:
            underperformer_pct = (len(underperformers) / total_proxies) * 100
            findings.append(
                f"{len(underperformers)} proxies ({underperformer_pct:.1f}%) "
                f"are underperforming and need attention"
            )
        else:
            findings.append("All proxies meet minimum performance thresholds")
        
        return findings

    def _generate_performance_summary(
        self,
        total_proxies: int,
        underperformer_count: int,
        stats: dict[str, Any],
    ) -> str:
        """Generate executive summary for performance analysis."""
        avg_success = stats.get("success_rate", {}).get("mean", 0) * 100
        avg_latency = stats.get("avg_latency_ms", {}).get("mean", 0)
        
        if underperformer_count == 0:
            health_assessment = "All proxies are performing within acceptable thresholds."
        else:
            underperformer_pct = (underperformer_count / total_proxies) * 100
            health_assessment = (
                f"{underperformer_count} proxies ({underperformer_pct:.1f}%) "
                f"require attention due to underperformance."
            )
        
        return (
            f"Performance analysis of {total_proxies} proxies shows an average "
            f"success rate of {avg_success:.1f}% with {avg_latency:.0f}ms average latency. "
            f"{health_assessment}"
        )

    def get_metrics_summary(self) -> dict[str, Any]:
        """
        Get summary of collected metrics.
        
        Returns:
            Dictionary with metrics summary statistics
        """
        with self._lock:
            return {
                "total_proxies": len(self._proxy_metrics),
                "total_requests_recorded": len(self._request_data),
                "total_requests_all_proxies": sum(
                    m.total_requests for m in self._proxy_metrics.values()
                ),
                "cache_size": len(self._cache),
                "oldest_data": (
                    min(m.first_seen for m in self._proxy_metrics.values())
                    if self._proxy_metrics else None
                ),
                "newest_data": (
                    max(m.last_seen for m in self._proxy_metrics.values())
                    if self._proxy_metrics else None
                ),
            }

    def clear_data(self) -> None:
        """Clear all collected data and cached results."""
        with self._lock:
            self._request_data.clear()
            self._proxy_metrics.clear()
            self._cache.clear()
            logger.info("Analytics data and cache cleared")

    def export_to_json(self, report: AnalysisReport, filepath: str) -> None:
        """
        Export analysis report to JSON file.
        
        Args:
            report: Analysis report to export
            filepath: Path to output JSON file
        """
        import json
        
        with open(filepath, "w") as f:
            json.dump(report.model_dump(mode="json"), f, indent=2, default=str)
        
        logger.info(f"Report exported to JSON: {filepath}")

    def export_to_csv(self, report: AnalysisReport, filepath: str) -> None:
        """
        Export performance metrics to CSV file.
        
        Args:
            report: Analysis report to export
            filepath: Path to output CSV file
        """
        import csv
        
        if not report.performance_metrics:
            logger.warning("No performance metrics to export")
            return
        
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "proxy_id",
                    "proxy_url",
                    "pool",
                    "region",
                    "total_requests",
                    "successful_requests",
                    "failed_requests",
                    "success_rate",
                    "avg_latency_ms",
                    "p95_latency_ms",
                    "uptime_percentage",
                ],
            )
            writer.writeheader()
            
            for metrics in report.performance_metrics.values():
                writer.writerow({
                    "proxy_id": metrics.proxy_id,
                    "proxy_url": metrics.proxy_url,
                    "pool": metrics.pool or "",
                    "region": metrics.region or "",
                    "total_requests": metrics.total_requests,
                    "successful_requests": metrics.successful_requests,
                    "failed_requests": metrics.failed_requests,
                    "success_rate": f"{metrics.success_rate:.4f}",
                    "avg_latency_ms": f"{metrics.avg_latency_ms:.2f}",
                    "p95_latency_ms": f"{metrics.p95_latency_ms:.2f}",
                    "uptime_percentage": f"{metrics.uptime_percentage:.2f}",
                })
        
        logger.info(f"Metrics exported to CSV: {filepath}")
