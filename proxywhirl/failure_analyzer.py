"""
Failure analyzer for root cause detection.

Implements User Story 3: Failure Analysis and Root Cause
- Group failures by proxy, domain, error type, time period
- Detect failure clusters
- Identify root causes through correlation analysis
- Generate remediation recommendations
"""

from datetime import datetime, timedelta
from typing import Any, Optional
from collections import Counter, defaultdict
from uuid import uuid4

import numpy as np
from loguru import logger

from proxywhirl.analytics_models import (
    AnalysisConfig,
    FailureAnalysisResult,
    FailureCluster,
    RecommendationPriority,
)


class FailureAnalyzer:
    """
    Analyzes failure patterns to identify root causes.
    
    Example:
        ```python
        from proxywhirl import FailureAnalyzer
        
        analyzer = FailureAnalyzer()
        
        # Analyze failures
        result = analyzer.analyze_failures(failure_data)
        
        # Get recommendations
        for cluster in result.clusters:
            print(cluster.remediation_steps)
        ```
    """

    def __init__(self, config: Optional[AnalysisConfig] = None) -> None:
        """
        Initialize failure analyzer.
        
        Args:
            config: Analysis configuration
        """
        self.config = config or AnalysisConfig()
        logger.info("Failure analyzer initialized")

    def group_failures_by_proxy(
        self,
        failure_data: list[dict[str, Any]],
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Group failures by proxy ID.
        
        Args:
            failure_data: List of failure records
            
        Returns:
            Dictionary of failures grouped by proxy_id
        """
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        
        for failure in failure_data:
            proxy_id = failure.get("proxy_id")
            if proxy_id:
                groups[proxy_id].append(failure)
        
        logger.info(
            "Grouped failures by proxy",
            total_proxies=len(groups),
            total_failures=len(failure_data),
        )
        
        return dict(groups)

    def group_failures_by_domain(
        self,
        failure_data: list[dict[str, Any]],
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Group failures by target domain.
        
        Args:
            failure_data: List of failure records
            
        Returns:
            Dictionary of failures grouped by target_domain
        """
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        
        for failure in failure_data:
            domain = failure.get("target_domain", "unknown")
            groups[domain].append(failure)
        
        logger.info(
            "Grouped failures by domain",
            total_domains=len(groups),
        )
        
        return dict(groups)

    def group_failures_by_error_type(
        self,
        failure_data: list[dict[str, Any]],
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Group failures by error type.
        
        Args:
            failure_data: List of failure records
            
        Returns:
            Dictionary of failures grouped by error_type
        """
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        
        for failure in failure_data:
            error_type = failure.get("error_type", "unknown")
            groups[error_type].append(failure)
        
        logger.info(
            "Grouped failures by error type",
            total_error_types=len(groups),
        )
        
        return dict(groups)

    def group_failures_by_time_period(
        self,
        failure_data: list[dict[str, Any]],
        period_hours: int = 1,
    ) -> dict[datetime, list[dict[str, Any]]]:
        """
        Group failures by time period.
        
        Args:
            failure_data: List of failure records
            period_hours: Time period in hours
            
        Returns:
            Dictionary of failures grouped by time period
        """
        groups: dict[datetime, list[dict[str, Any]]] = defaultdict(list)
        
        for failure in failure_data:
            ts = failure.get("timestamp", datetime.now())
            # Round to period
            period_start = ts.replace(
                minute=0,
                second=0,
                microsecond=0,
            ) - timedelta(hours=ts.hour % period_hours)
            groups[period_start].append(failure)
        
        logger.info(
            "Grouped failures by time period",
            total_periods=len(groups),
            period_hours=period_hours,
        )
        
        return dict(groups)

    def detect_failure_clusters(
        self,
        failure_data: list[dict[str, Any]],
        min_cluster_size: Optional[int] = None,
    ) -> list[FailureCluster]:
        """
        Detect failure clusters using grouping and correlation.
        
        Args:
            failure_data: List of failure records
            min_cluster_size: Minimum failures to form cluster
            
        Returns:
            List of detected failure clusters
        """
        if not failure_data:
            return []
        
        min_size = min_cluster_size or self.config.min_cluster_size
        clusters: list[FailureCluster] = []
        
        # Group by multiple dimensions
        by_proxy = self.group_failures_by_proxy(failure_data)
        by_domain = self.group_failures_by_domain(failure_data)
        by_error = self.group_failures_by_error_type(failure_data)
        
        # Detect proxy-based clusters
        for proxy_id, failures in by_proxy.items():
            if len(failures) >= min_size:
                cluster = self._create_cluster_from_proxy(proxy_id, failures)
                clusters.append(cluster)
        
        # Detect domain-based clusters
        for domain, failures in by_domain.items():
            if len(failures) >= min_size:
                cluster = self._create_cluster_from_domain(domain, failures)
                clusters.append(cluster)
        
        # Detect error-type clusters
        for error_type, failures in by_error.items():
            if len(failures) >= min_size:
                cluster = self._create_cluster_from_error(error_type, failures)
                clusters.append(cluster)
        
        # Remove duplicate clusters (same failures)
        clusters = self._deduplicate_clusters(clusters)
        
        logger.info(
            "Detected failure clusters",
            total_clusters=len(clusters),
            min_size=min_size,
        )
        
        return clusters

    def identify_root_causes(
        self,
        cluster: FailureCluster,
    ) -> list[str]:
        """
        Identify potential root causes for a failure cluster.
        
        Args:
            cluster: Failure cluster to analyze
            
        Returns:
            List of suspected root causes
        """
        root_causes: list[str] = []
        
        # Analyze common factors
        if cluster.common_proxies and len(cluster.common_proxies) == 1:
            root_causes.append(
                f"Proxy-specific issue: {cluster.common_proxies[0]} may be misconfigured or blocked"
            )
        
        if cluster.common_domains and len(cluster.common_domains) == 1:
            root_causes.append(
                f"Domain-specific issue: {cluster.common_domains[0]} may be blocking proxies"
            )
        
        if cluster.common_error_types:
            error = cluster.common_error_types[0]
            if "timeout" in error.lower():
                root_causes.append("Network latency or connectivity issues")
            elif "auth" in error.lower():
                root_causes.append("Authentication or credential problems")
            elif "403" in error or "blocked" in error.lower():
                root_causes.append("IP blocking or rate limiting by target")
        
        if cluster.common_regions and len(cluster.common_regions) <= 2:
            root_causes.append(
                f"Geographic issue: Problems localized to {', '.join(cluster.common_regions)}"
            )
        
        # Time-based patterns
        time_span = (cluster.last_occurrence - cluster.first_occurrence).total_seconds()
        if time_span < 300:  # 5 minutes
            root_causes.append("Sudden systemic issue or service disruption")
        elif time_span > 86400:  # 24 hours
            root_causes.append("Persistent configuration or infrastructure problem")
        
        return root_causes

    def analyze_failure_correlations(
        self,
        failure_data: list[dict[str, Any]],
    ) -> dict[str, float]:
        """
        Analyze correlations between different failure factors.
        
        Args:
            failure_data: List of failure records
            
        Returns:
            Dictionary of correlation coefficients
        """
        if len(failure_data) < 10:
            return {}
        
        correlations: dict[str, float] = {}
        
        # Proxy-time correlation
        proxy_times: dict[str, list[datetime]] = defaultdict(list)
        for failure in failure_data:
            proxy_id = failure.get("proxy_id")
            if proxy_id:
                proxy_times[proxy_id].append(failure["timestamp"])
        
        # Calculate time clustering for proxies
        if len(proxy_times) >= 2:
            # Simple correlation: Do failures happen at similar times across proxies?
            all_times = []
            for times in proxy_times.values():
                all_times.extend([t.timestamp() for t in times])
            
            if len(all_times) >= 10:
                # Measure time clustering using coefficient of variation
                time_std = np.std(all_times)
                time_mean = np.mean(all_times)
                cv = time_std / time_mean if time_mean > 0 else 1.0
                # Lower CV means more correlation (clustering)
                correlations["proxy_time"] = max(0.0, 1.0 - cv)
        
        # Domain-error correlation
        domain_errors: dict[str, set[str]] = defaultdict(set)
        for failure in failure_data:
            domain = failure.get("target_domain", "unknown")
            error = failure.get("error_type", "unknown")
            domain_errors[domain].add(error)
        
        # If specific domains have specific errors, there's correlation
        if domain_errors:
            # Calculate how specific the errors are per domain
            error_specificity = []
            for errors in domain_errors.values():
                if len(failure_data) > 0:
                    specificity = len(errors) / len(failure_data)
                    error_specificity.append(specificity)
            
            if error_specificity:
                correlations["domain_error"] = float(1.0 - np.mean(error_specificity))
        
        logger.info(
            "Analyzed failure correlations",
            correlations=correlations,
        )
        
        return correlations

    def generate_remediation_recommendations(
        self,
        cluster: FailureCluster,
    ) -> list[str]:
        """
        Generate remediation steps for a failure cluster.
        
        Args:
            cluster: Failure cluster
            
        Returns:
            List of recommended remediation steps
        """
        steps: list[str] = []
        
        # Based on root causes
        if cluster.common_proxies and len(cluster.common_proxies) <= 3:
            steps.append(
                f"Remove or replace problematic proxies: {', '.join(cluster.common_proxies[:3])}"
            )
        
        if cluster.common_error_types:
            error = cluster.common_error_types[0]
            if "timeout" in error.lower():
                steps.append("Increase timeout thresholds or investigate network connectivity")
            elif "auth" in error.lower():
                steps.append("Verify proxy credentials and refresh authentication")
            elif "blocked" in error.lower() or "403" in error:
                steps.append("Rotate IPs more frequently or use different proxy sources")
        
        if cluster.failure_rate > 0.5:
            steps.append("Consider temporarily removing affected proxies from rotation")
        
        if cluster.common_domains:
            steps.append(
                f"Investigate target domain behavior for: {', '.join(cluster.common_domains[:3])}"
            )
        
        # General recommendations
        steps.append("Monitor cluster for recurrence after remediation")
        steps.append("Update proxy health check configuration based on findings")
        
        return steps

    def analyze_failures(
        self,
        failure_data: list[dict[str, Any]],
    ) -> FailureAnalysisResult:
        """
        Comprehensive failure analysis.
        
        Args:
            failure_data: List of failure records
            
        Returns:
            Complete failure analysis result
        """
        if not failure_data:
            return FailureAnalysisResult(
                total_failures=0,
                total_clusters=0,
                clustered_failures=0,
                unclustered_failures=0,
                clustering_effectiveness=0.0,
                analysis_start=datetime.now(),
                analysis_end=datetime.now(),
            )
        
        # Detect clusters
        clusters = self.detect_failure_clusters(failure_data)
        
        # Identify root causes for each cluster
        for cluster in clusters:
            cluster.suspected_root_causes = self.identify_root_causes(cluster)
            cluster.remediation_steps = self.generate_remediation_recommendations(cluster)
            
            # Calculate confidence based on cluster characteristics
            confidence_factors = []
            if cluster.common_proxies:
                confidence_factors.append(0.3)
            if cluster.common_domains:
                confidence_factors.append(0.3)
            if cluster.common_error_types:
                confidence_factors.append(0.4)
            
            cluster.confidence_score = sum(confidence_factors) if confidence_factors else 0.5
        
        # Calculate overall statistics
        clustered_failures = sum(c.size for c in clusters)
        unclustered = max(0, len(failure_data) - clustered_failures)
        effectiveness = clustered_failures / len(failure_data) if failure_data else 0.0
        
        # Get top failure factors
        by_proxy = self.group_failures_by_proxy(failure_data)
        by_domain = self.group_failures_by_domain(failure_data)
        by_error = self.group_failures_by_error_type(failure_data)
        
        top_proxies = sorted(by_proxy.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        top_domains = sorted(by_domain.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        top_errors = sorted(by_error.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        
        # Generate overall recommendations
        recommendations = self._generate_overall_recommendations(
            clusters, top_proxies, top_domains, top_errors
        )
        
        result = FailureAnalysisResult(
            total_failures=len(failure_data),
            total_clusters=len(clusters),
            clustered_failures=clustered_failures,
            unclustered_failures=unclustered,
            clustering_effectiveness=effectiveness,
            clusters=clusters,
            top_failing_proxies=[(p, len(f)) for p, f in top_proxies],
            top_failing_domains=[(d, len(f)) for d, f in top_domains],
            top_error_types=[(e, len(f)) for e, f in top_errors],
            analysis_start=min(f["timestamp"] for f in failure_data),
            analysis_end=max(f["timestamp"] for f in failure_data),
            recommendations=recommendations,
        )
        
        logger.info(
            "Completed failure analysis",
            total_failures=result.total_failures,
            clusters=result.total_clusters,
            effectiveness=f"{result.clustering_effectiveness:.1%}",
        )
        
        return result

    def _create_cluster_from_proxy(
        self,
        proxy_id: str,
        failures: list[dict[str, Any]],
    ) -> FailureCluster:
        """Create cluster from proxy-grouped failures."""
        domains = {f.get("target_domain", "unknown") for f in failures}
        errors = {f.get("error_type", "unknown") for f in failures}
        regions = {f.get("region") for f in failures if f.get("region")}
        
        timestamps = [f["timestamp"] for f in failures]
        
        return FailureCluster(
            size=len(failures),
            failure_rate=1.0,  # Will be calculated from context
            common_proxies=[proxy_id],
            common_domains=list(domains)[:5],
            common_error_types=list(errors)[:5],
            common_regions=list(regions)[:5],
            first_occurrence=min(timestamps),
            last_occurrence=max(timestamps),
            affected_proxy_count=1,
            affected_domain_count=len(domains),
            total_failed_requests=len(failures),
            confidence_score=0.8,
            priority=RecommendationPriority.HIGH if len(failures) > 50 else RecommendationPriority.MEDIUM,
        )

    def _create_cluster_from_domain(
        self,
        domain: str,
        failures: list[dict[str, Any]],
    ) -> FailureCluster:
        """Create cluster from domain-grouped failures."""
        proxies = {f.get("proxy_id") for f in failures if f.get("proxy_id")}
        errors = {f.get("error_type", "unknown") for f in failures}
        regions = {f.get("region") for f in failures if f.get("region")}
        
        timestamps = [f["timestamp"] for f in failures]
        
        return FailureCluster(
            size=len(failures),
            failure_rate=1.0,
            common_proxies=list(proxies)[:5],
            common_domains=[domain],
            common_error_types=list(errors)[:5],
            common_regions=list(regions)[:5],
            first_occurrence=min(timestamps),
            last_occurrence=max(timestamps),
            affected_proxy_count=len(proxies),
            affected_domain_count=1,
            total_failed_requests=len(failures),
            confidence_score=0.7,
            priority=RecommendationPriority.MEDIUM,
        )

    def _create_cluster_from_error(
        self,
        error_type: str,
        failures: list[dict[str, Any]],
    ) -> FailureCluster:
        """Create cluster from error-type-grouped failures."""
        proxies = {f.get("proxy_id") for f in failures if f.get("proxy_id")}
        domains = {f.get("target_domain", "unknown") for f in failures}
        regions = {f.get("region") for f in failures if f.get("region")}
        
        timestamps = [f["timestamp"] for f in failures]
        
        return FailureCluster(
            size=len(failures),
            failure_rate=1.0,
            common_proxies=list(proxies)[:5],
            common_domains=list(domains)[:5],
            common_error_types=[error_type],
            common_regions=list(regions)[:5],
            first_occurrence=min(timestamps),
            last_occurrence=max(timestamps),
            affected_proxy_count=len(proxies),
            affected_domain_count=len(domains),
            total_failed_requests=len(failures),
            confidence_score=0.6,
            priority=RecommendationPriority.MEDIUM,
        )

    def _deduplicate_clusters(
        self,
        clusters: list[FailureCluster],
    ) -> list[FailureCluster]:
        """Remove duplicate clusters with similar characteristics."""
        # Simple deduplication based on size and common factors
        unique_clusters: list[FailureCluster] = []
        
        for cluster in clusters:
            is_duplicate = False
            for existing in unique_clusters:
                # Check if substantially similar
                if (
                    cluster.size == existing.size
                    and cluster.common_proxies == existing.common_proxies
                    and cluster.common_domains == existing.common_domains
                ):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_clusters.append(cluster)
        
        return unique_clusters

    def _generate_overall_recommendations(
        self,
        clusters: list[FailureCluster],
        top_proxies: list[tuple[str, list[dict[str, Any]]]],
        top_domains: list[tuple[str, list[dict[str, Any]]]],
        top_errors: list[tuple[str, list[dict[str, Any]]]],
    ) -> list[str]:
        """Generate overall recommendations from analysis."""
        recommendations: list[str] = []
        
        if len(clusters) > 10:
            recommendations.append(
                f"High number of failure clusters ({len(clusters)}) indicates systemic issues"
            )
        
        if top_proxies and len(top_proxies[0][1]) > 100:
            recommendations.append(
                f"Top failing proxy ({top_proxies[0][0]}) responsible for {len(top_proxies[0][1])} failures - consider removal"
            )
        
        if top_errors:
            recommendations.append(
                f"Most common error type: {top_errors[0][0]} - prioritize addressing this issue"
            )
        
        recommendations.append("Review and update proxy health check criteria based on failure patterns")
        recommendations.append("Consider implementing automatic proxy rotation on repeated failures")
        
        return recommendations


__all__ = [
    "FailureAnalyzer",
]
