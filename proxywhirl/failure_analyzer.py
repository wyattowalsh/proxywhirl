"""
Failure analyzer for ProxyWhirl analytics engine.

Analyzes failure patterns, groups failures by common factors, and performs
root cause analysis.
"""

import statistics
from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from loguru import logger

from proxywhirl.analytics_models import (
    AnalysisConfig,
    FailureCluster,
    Recommendation,
    RecommendationPriority,
)


class FailureAnalyzer:
    """
    Analyzes proxy failure patterns for root cause identification.
    
    Groups failures by common factors (proxy, domain, error type) and
    identifies clusters for targeted remediation.
    
    Example:
        ```python
        from proxywhirl import FailureAnalyzer, AnalysisConfig
        
        analyzer = FailureAnalyzer(config=AnalysisConfig())
        
        # Group failures
        clusters = analyzer.detect_failure_clusters(failure_data)
        
        # Analyze root causes
        root_causes = analyzer.identify_root_causes(clusters[0])
        
        # Get recommendations
        recommendations = analyzer.generate_remediation_recommendations(clusters)
        ```
    """

    def __init__(self, config: Optional[AnalysisConfig] = None) -> None:
        """
        Initialize failure analyzer.
        
        Args:
            config: Analysis configuration (default: AnalysisConfig())
        """
        self.config = config or AnalysisConfig()
        logger.debug("Failure analyzer initialized")

    def group_failures_by_proxy(
        self,
        failure_data: list[dict[str, Any]],
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Group failures by proxy ID.
        
        Args:
            failure_data: List of failure records
            
        Returns:
            Dictionary of proxy_id -> list of failures
        """
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        
        for failure in failure_data:
            proxy_id = failure.get("proxy_id")
            if proxy_id:
                grouped[proxy_id].append(failure)
        
        logger.debug(f"Grouped failures by {len(grouped)} proxies")
        return dict(grouped)

    def group_failures_by_domain(
        self,
        failure_data: list[dict[str, Any]],
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Group failures by target domain.
        
        Args:
            failure_data: List of failure records
            
        Returns:
            Dictionary of domain -> list of failures
        """
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        
        for failure in failure_data:
            domain = failure.get("target_domain")
            if domain:
                grouped[domain].append(failure)
        
        logger.debug(f"Grouped failures by {len(grouped)} domains")
        return dict(grouped)

    def group_failures_by_error_type(
        self,
        failure_data: list[dict[str, Any]],
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Group failures by error type.
        
        Args:
            failure_data: List of failure records
            
        Returns:
            Dictionary of error_type -> list of failures
        """
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        
        for failure in failure_data:
            error_type = failure.get("error_type", "unknown")
            grouped[error_type].append(failure)
        
        logger.debug(f"Grouped failures by {len(grouped)} error types")
        return dict(grouped)

    def detect_failure_clusters(
        self,
        failure_data: list[dict[str, Any]],
    ) -> list[FailureCluster]:
        """
        Detect clusters of related failures.
        
        Groups failures with common characteristics and creates clusters
        for analysis.
        
        Args:
            failure_data: List of failure records
            
        Returns:
            List of failure clusters
        """
        if len(failure_data) < self.config.min_cluster_size:
            logger.warning(f"Insufficient failures for clustering: {len(failure_data)}")
            return []
        
        clusters: list[FailureCluster] = []
        
        # Cluster by error type
        by_error = self.group_failures_by_error_type(failure_data)
        for error_type, failures in by_error.items():
            if len(failures) >= self.config.min_cluster_size:
                cluster = self._create_cluster(
                    f"Error Type: {error_type}",
                    failures,
                    error_types=[error_type],
                )
                clusters.append(cluster)
        
        # Cluster by proxy
        by_proxy = self.group_failures_by_proxy(failure_data)
        for proxy_id, failures in by_proxy.items():
            if len(failures) >= self.config.min_cluster_size:
                cluster = self._create_cluster(
                    f"Proxy: {proxy_id}",
                    failures,
                    proxies=[proxy_id],
                )
                clusters.append(cluster)
        
        # Cluster by domain
        by_domain = self.group_failures_by_domain(failure_data)
        for domain, failures in by_domain.items():
            if len(failures) >= self.config.min_cluster_size:
                cluster = self._create_cluster(
                    f"Domain: {domain}",
                    failures,
                    domains=[domain],
                )
                clusters.append(cluster)
        
        logger.info(f"Detected {len(clusters)} failure clusters")
        return clusters

    def _create_cluster(
        self,
        name: str,
        failures: list[dict[str, Any]],
        proxies: Optional[list[str]] = None,
        domains: Optional[list[str]] = None,
        error_types: Optional[list[str]] = None,
    ) -> FailureCluster:
        """Create a failure cluster from failure data."""
        # Extract unique values
        unique_proxies = set(f.get("proxy_id") for f in failures if f.get("proxy_id"))
        unique_domains = set(f.get("target_domain") for f in failures if f.get("target_domain"))
        unique_errors = set(f.get("error_type") for f in failures if f.get("error_type"))
        
        # Get timestamps
        timestamps = [f.get("timestamp") for f in failures if f.get("timestamp")]
        
        # Calculate failure rate
        total_attempts = len(failures)  # Simplified
        failure_rate = 1.0  # All are failures in this dataset
        
        # Identify probable root causes
        root_causes = self._identify_cluster_root_causes(failures)
        
        return FailureCluster(
            cluster_name=name,
            common_proxy_ids=proxies or list(unique_proxies),
            common_domains=domains or list(unique_domains),
            common_error_types=error_types or list(unique_errors),
            failure_count=len(failures),
            affected_proxies=len(unique_proxies),
            failure_rate=failure_rate,
            probable_root_causes=root_causes,
            correlation_factors={},
            first_failure=min(timestamps) if timestamps else datetime.now(),
            last_failure=max(timestamps) if timestamps else datetime.now(),
        )

    def _identify_cluster_root_causes(
        self,
        failures: list[dict[str, Any]],
    ) -> list[str]:
        """Identify probable root causes for a cluster."""
        causes: list[str] = []
        
        # Analyze error types
        error_counter = Counter(f.get("error_type") for f in failures if f.get("error_type"))
        if error_counter:
            most_common_error = error_counter.most_common(1)[0]
            if most_common_error[1] / len(failures) > 0.8:
                causes.append(f"Dominant error type: {most_common_error[0]}")
        
        # Analyze timing
        timestamps = [f.get("timestamp") for f in failures if f.get("timestamp")]
        if timestamps and len(timestamps) >= 2:
            time_range = max(timestamps) - min(timestamps)
            if time_range.total_seconds() < 3600:  # Within 1 hour
                causes.append("Temporal clustering - possible service outage")
        
        # Analyze proxy concentration
        proxy_counter = Counter(f.get("proxy_id") for f in failures if f.get("proxy_id"))
        if proxy_counter:
            most_common_proxy = proxy_counter.most_common(1)[0]
            if most_common_proxy[1] / len(failures) > 0.7:
                causes.append(f"Proxy-specific issue: {most_common_proxy[0]}")
        
        # Analyze domain concentration
        domain_counter = Counter(f.get("target_domain") for f in failures if f.get("target_domain"))
        if domain_counter:
            most_common_domain = domain_counter.most_common(1)[0]
            if most_common_domain[1] / len(failures) > 0.7:
                causes.append(f"Target-specific issue: {most_common_domain[0]}")
        
        return causes

    def identify_root_causes(
        self,
        cluster: FailureCluster,
    ) -> list[str]:
        """
        Identify root causes for a failure cluster.
        
        Args:
            cluster: Failure cluster to analyze
            
        Returns:
            List of probable root causes
        """
        return cluster.probable_root_causes

    def generate_remediation_recommendations(
        self,
        clusters: list[FailureCluster],
    ) -> list[Recommendation]:
        """
        Generate remediation recommendations based on failure clusters.
        
        Args:
            clusters: List of failure clusters
            
        Returns:
            List of prioritized recommendations
        """
        recommendations: list[Recommendation] = []
        
        # Sort clusters by size
        sorted_clusters = sorted(clusters, key=lambda c: c.failure_count, reverse=True)
        
        for cluster in sorted_clusters[:5]:  # Top 5 clusters
            if cluster.affected_proxies == 1 and cluster.common_proxy_ids:
                # Single proxy issue
                recommendations.append(
                    Recommendation(
                        title=f"Investigate Proxy: {cluster.common_proxy_ids[0]}",
                        description=(
                            f"Proxy has {cluster.failure_count} failures clustered together. "
                            f"Root causes: {', '.join(cluster.probable_root_causes)}"
                        ),
                        priority=RecommendationPriority.HIGH,
                        category="failure_remediation",
                        estimated_improvement=f"Eliminate {cluster.failure_count} failures",
                        estimated_effort="Low - replace or remove single proxy",
                        affected_proxies=cluster.common_proxy_ids,
                        supporting_data={
                            "failure_count": cluster.failure_count,
                            "root_causes": cluster.probable_root_causes,
                        },
                    )
                )
            elif cluster.common_domains and len(cluster.common_domains) == 1:
                # Domain-specific issue
                recommendations.append(
                    Recommendation(
                        title=f"Domain Issue: {cluster.common_domains[0]}",
                        description=(
                            f"Multiple proxies failing for domain {cluster.common_domains[0]}. "
                            f"May indicate target blocking or access restrictions."
                        ),
                        priority=RecommendationPriority.MEDIUM,
                        category="failure_remediation",
                        estimated_improvement="Restore access to target domain",
                        estimated_effort="Medium - may require proxy rotation or IP refresh",
                        affected_proxies=cluster.common_proxy_ids or [],
                        supporting_data={
                            "failure_count": cluster.failure_count,
                            "affected_proxies": cluster.affected_proxies,
                        },
                    )
                )
            elif cluster.common_error_types and len(cluster.common_error_types) == 1:
                # Error type specific
                recommendations.append(
                    Recommendation(
                        title=f"Systematic Error: {cluster.common_error_types[0]}",
                        description=(
                            f"Widespread {cluster.common_error_types[0]} affecting "
                            f"{cluster.affected_proxies} proxies. Review error handling "
                            f"and retry logic."
                        ),
                        priority=RecommendationPriority.MEDIUM,
                        category="failure_remediation",
                        estimated_improvement="Reduce error frequency",
                        estimated_effort="Medium - code or configuration changes",
                        affected_proxies=cluster.common_proxy_ids or [],
                        supporting_data={
                            "failure_count": cluster.failure_count,
                            "error_type": cluster.common_error_types[0],
                        },
                    )
                )
        
        logger.info(f"Generated {len(recommendations)} remediation recommendations")
        return recommendations
