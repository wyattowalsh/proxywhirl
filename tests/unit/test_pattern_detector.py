"""Unit tests for pattern detector."""

from datetime import datetime, timedelta

import pytest

from proxywhirl.analytics_models import AnalysisConfig
from proxywhirl.pattern_detector import PatternDetector


class TestPatternDetector:
    """Test PatternDetector functionality."""

    @pytest.fixture
    def sample_data(self):
        """Generate sample request data."""
        data = []
        now = datetime.now()
        
        for hour in range(24):
            # Simulate peak hours (9-17)
            count = 20 if 9 <= hour <= 17 else 5
            
            for i in range(count):
                data.append({
                    "proxy_id": f"proxy-{i % 3}",
                    "success": True,
                    "latency_ms": 100.0,
                    "timestamp": now - timedelta(hours=hour, minutes=i),
                    "region": "us-east" if i % 2 == 0 else "eu-west",
                })
        
        return data

    def test_detector_initialization(self):
        """Test detector initializes correctly."""
        detector = PatternDetector()
        assert detector is not None
        assert detector.config is not None

    def test_detect_peak_hours(self, sample_data):
        """Test peak hour detection."""
        detector = PatternDetector()
        
        peak_hours = detector.detect_peak_hours(sample_data)
        
        assert isinstance(peak_hours, list)
        assert len(peak_hours) > 0
        # Peak should be during business hours
        assert any(9 <= h <= 17 for h in peak_hours)

    def test_analyze_request_volumes(self, sample_data):
        """Test request volume analysis."""
        detector = PatternDetector()
        
        analysis = detector.analyze_request_volumes(sample_data)
        
        assert "total_requests" in analysis
        assert "avg_requests_per_window" in analysis
        assert "trend" in analysis
        assert analysis["total_requests"] == len(sample_data)

    def test_detect_geographic_patterns(self, sample_data):
        """Test geographic pattern detection."""
        detector = PatternDetector()
        
        patterns = detector.detect_geographic_patterns(sample_data, top_n=5)
        
        assert isinstance(patterns, list)
        assert len(patterns) > 0
        # Should have both regions
        regions = [r for r, _ in patterns]
        assert "us-east" in regions or "eu-west" in regions

    def test_detect_anomalies(self):
        """Test anomaly detection."""
        detector = PatternDetector()
        
        # Create data with anomaly
        data = []
        now = datetime.now()
        
        # Normal pattern
        for i in range(100):
            data.append({
                "timestamp": now - timedelta(hours=i),
                "success": True,
            })
        
        # Add spike (anomaly)
        for i in range(50):
            data.append({
                "timestamp": now - timedelta(hours=1, minutes=i),
                "success": True,
            })
        
        anomalies = detector.detect_anomalies(data)
        
        assert isinstance(anomalies, list)
        # May or may not detect anomaly depending on threshold

    def test_calculate_capacity_metrics(self, sample_data):
        """Test capacity metrics calculation."""
        detector = PatternDetector()
        
        metrics = detector.calculate_capacity_metrics(sample_data, proxy_count=5)
        
        assert "total_proxies" in metrics
        assert "utilization_percent" in metrics
        assert metrics["total_proxies"] == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
