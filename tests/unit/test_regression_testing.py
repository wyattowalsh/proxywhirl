"""Tests for regression testing module."""

from proxywhirl.regression_testing import (
    Baseline,
    BaselineStore,
    RegressionDetector,
    RegressionType,
)


class TestBaseline:
    """Test Baseline dataclass."""

    def test_baseline_creation(self):
        """Test baseline creation."""
        baseline = Baseline(name="test", value=100.0, unit="ms")
        assert baseline.name == "test"
        assert baseline.value == 100.0
        assert baseline.unit == "ms"

    def test_baseline_repr(self):
        """Test baseline representation."""
        baseline = Baseline(name="test", value=100.0, unit="ms")
        assert "test: 100.0 ms" in str(baseline)


class TestBaselineStore:
    """Test BaselineStore class."""

    def test_save_baseline(self):
        """Test saving baseline."""
        store = BaselineStore()
        baseline = Baseline(name="test", value=100.0, unit="ms")
        store.save_baseline(baseline)
        assert store.get_baseline("test") == baseline

    def test_get_baseline_not_found(self):
        """Test getting non-existent baseline."""
        store = BaselineStore()
        assert store.get_baseline("missing") is None

    def test_clear_baseline(self):
        """Test clearing baseline."""
        store = BaselineStore()
        baseline = Baseline(name="test", value=100.0, unit="ms")
        store.save_baseline(baseline)
        assert store.clear_baseline("test")
        assert store.get_baseline("test") is None

    def test_clear_baseline_not_found(self):
        """Test clearing non-existent baseline."""
        store = BaselineStore()
        assert not store.clear_baseline("missing")

    def test_get_all_baselines(self):
        """Test getting all baselines."""
        store = BaselineStore()
        b1 = Baseline(name="test1", value=100.0, unit="ms")
        b2 = Baseline(name="test2", value=200.0, unit="ms")
        store.save_baseline(b1)
        store.save_baseline(b2)
        all_baselines = store.get_all_baselines()
        assert len(all_baselines) == 2
        assert "test1" in all_baselines
        assert "test2" in all_baselines


class TestRegressionDetector:
    """Test RegressionDetector class."""

    def test_detect_performance_regression_no_regression(self):
        """Test detecting no regression."""
        detector = RegressionDetector()
        result = detector.detect_performance_regression(
            "test", baseline_value=100.0, current_value=105.0, threshold=0.1
        )
        assert not result.is_regressed

    def test_detect_performance_regression_regression(self):
        """Test detecting regression."""
        detector = RegressionDetector()
        result = detector.detect_performance_regression(
            "test", baseline_value=100.0, current_value=120.0, threshold=0.1
        )
        assert result.is_regressed

    def test_detect_memory_regression(self):
        """Test memory regression detection."""
        detector = RegressionDetector()
        result = detector.detect_memory_regression(
            "test", baseline_value=100.0, current_value=120.0, threshold=0.1
        )
        assert result.regression_type == RegressionType.MEMORY

    def test_detect_latency_regression(self):
        """Test latency regression detection."""
        detector = RegressionDetector()
        result = detector.detect_latency_regression(
            "test",
            baseline_value=100.0,
            current_value=110.0,
            percentile=95,
            threshold=0.05,
        )
        assert result.regression_type == RegressionType.LATENCY

    def test_get_results(self):
        """Test getting results."""
        detector = RegressionDetector()
        detector.detect_performance_regression("test1", 100.0, 105.0, threshold=0.1)
        detector.detect_performance_regression("test2", 100.0, 120.0, threshold=0.1)
        results = detector.get_results()
        assert len(results) == 2

    def test_get_results_regressed_only(self):
        """Test getting only regressed results."""
        detector = RegressionDetector()
        detector.detect_performance_regression("test1", 100.0, 105.0, threshold=0.1)
        detector.detect_performance_regression("test2", 100.0, 120.0, threshold=0.1)
        results = detector.get_results(regressed_only=True)
        assert len(results) == 1

    def test_clear_results(self):
        """Test clearing results."""
        detector = RegressionDetector()
        detector.detect_performance_regression("test1", 100.0, 105.0)
        assert len(detector.get_results()) == 1
        detector.clear_results()
        assert len(detector.get_results()) == 0

    def test_summary(self):
        """Test summary generation."""
        detector = RegressionDetector()
        detector.detect_performance_regression("test1", 100.0, 105.0, threshold=0.1)
        detector.detect_performance_regression("test2", 100.0, 120.0, threshold=0.1)
        summary = detector.summary()
        assert summary["total_tests"] == 2
        assert summary["regressed_tests"] == 1
        assert "pass_rate" in summary
