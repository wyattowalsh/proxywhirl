"""Unit tests for failure analyzer."""

from datetime import datetime, timedelta

import pytest

from proxywhirl.analytics_models import AnalysisConfig
from proxywhirl.failure_analyzer import FailureAnalyzer


class TestFailureAnalyzer:
    """Test FailureAnalyzer functionality."""

    @pytest.fixture
    def failure_data(self):
        """Generate sample failure data."""
        data = []
        now = datetime.now()
        
        # Failures from proxy-1
        for i in range(20):
            data.append({
                "proxy_id": "proxy-1",
                "target_domain": "api.example.com",
                "error_type": "timeout",
                "timestamp": now - timedelta(hours=i),
                "region": "us-east",
            })
        
        # Failures from proxy-2 (different error)
        for i in range(15):
            data.append({
                "proxy_id": "proxy-2",
                "target_domain": "data.example.com",
                "error_type": "connection_refused",
                "timestamp": now - timedelta(hours=i),
                "region": "eu-west",
            })
        
        return data

    def test_analyzer_initialization(self):
        """Test analyzer initializes correctly."""
        analyzer = FailureAnalyzer()
        assert analyzer is not None
        assert analyzer.config is not None

    def test_group_failures_by_proxy(self, failure_data):
        """Test grouping failures by proxy."""
        analyzer = FailureAnalyzer()
        
        groups = analyzer.group_failures_by_proxy(failure_data)
        
        assert "proxy-1" in groups
        assert "proxy-2" in groups
        assert len(groups["proxy-1"]) == 20
        assert len(groups["proxy-2"]) == 15

    def test_group_failures_by_domain(self, failure_data):
        """Test grouping failures by domain."""
        analyzer = FailureAnalyzer()
        
        groups = analyzer.group_failures_by_domain(failure_data)
        
        assert "api.example.com" in groups
        assert "data.example.com" in groups

    def test_group_failures_by_error_type(self, failure_data):
        """Test grouping failures by error type."""
        analyzer = FailureAnalyzer()
        
        groups = analyzer.group_failures_by_error_type(failure_data)
        
        assert "timeout" in groups
        assert "connection_refused" in groups

    def test_detect_failure_clusters(self, failure_data):
        """Test failure cluster detection."""
        analyzer = FailureAnalyzer()
        
        clusters = analyzer.detect_failure_clusters(failure_data, min_cluster_size=5)
        
        assert isinstance(clusters, list)
        assert len(clusters) > 0
        
        for cluster in clusters:
            assert cluster.size >= 5
            assert cluster.confidence_score >= 0.0

    def test_identify_root_causes(self, failure_data):
        """Test root cause identification."""
        analyzer = FailureAnalyzer()
        
        clusters = analyzer.detect_failure_clusters(failure_data)
        
        if clusters:
            cluster = clusters[0]
            root_causes = analyzer.identify_root_causes(cluster)
            
            assert isinstance(root_causes, list)

    def test_analyze_failures(self, failure_data):
        """Test comprehensive failure analysis."""
        analyzer = FailureAnalyzer()
        
        result = analyzer.analyze_failures(failure_data)
        
        assert result.total_failures == len(failure_data)
        assert result.total_clusters >= 0
        assert 0.0 <= result.clustering_effectiveness <= 1.0
        assert len(result.top_failing_proxies) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
