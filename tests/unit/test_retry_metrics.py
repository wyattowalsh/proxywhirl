"""
Unit tests for RetryMetrics.
"""

from datetime import datetime, timedelta, timezone

from proxywhirl.circuit_breaker import CircuitBreakerState
from proxywhirl.retry_metrics import (
    CircuitBreakerEvent,
    RetryAttempt,
    RetryMetrics,
    RetryOutcome,
)


class TestRetryMetricsRecordAttempt:
    """Test RetryMetrics.record_attempt() method."""

    def test_record_single_attempt(self):
        """Test recording a single retry attempt."""
        metrics = RetryMetrics()

        attempt = RetryAttempt(
            request_id="req-1",
            attempt_number=0,
            proxy_id="proxy-1",
            timestamp=datetime.now(timezone.utc),
            outcome=RetryOutcome.SUCCESS,
            delay_before=1.0,
            latency=0.5,
        )

        metrics.record_attempt(attempt)

        assert len(metrics.current_attempts) == 1
        assert metrics.current_attempts[0] == attempt

    def test_trim_exceeds_max(self):
        """Test that attempts are trimmed when exceeding max."""
        metrics = RetryMetrics(max_current_attempts=10)

        # Record 15 attempts
        for i in range(15):
            attempt = RetryAttempt(
                request_id=f"req-{i}",
                attempt_number=0,
                proxy_id="proxy-1",
                timestamp=datetime.now(timezone.utc),
                outcome=RetryOutcome.SUCCESS,
                delay_before=0.0,
                latency=0.5,
            )
            metrics.record_attempt(attempt)

        # Should only keep last 10
        assert len(metrics.current_attempts) == 10

    def test_thread_safety(self):
        """Test concurrent attempt recording is thread-safe."""
        import threading

        metrics = RetryMetrics()

        def record_attempts():
            for i in range(100):
                attempt = RetryAttempt(
                    request_id=f"req-{i}",
                    attempt_number=0,
                    proxy_id="proxy-1",
                    timestamp=datetime.now(timezone.utc),
                    outcome=RetryOutcome.SUCCESS,
                    delay_before=0.0,
                    latency=0.5,
                )
                metrics.record_attempt(attempt)

        # Create 10 threads, each recording 100 attempts
        threads = [threading.Thread(target=record_attempts) for _ in range(10)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Should have exactly 1000 attempts
        assert len(metrics.current_attempts) == 1000


class TestRetryMetricsAggregateHourly:
    """Test RetryMetrics.aggregate_hourly() method."""

    def test_aggregates_attempts_by_hour(self):
        """Test that attempts are aggregated into hourly buckets."""
        metrics = RetryMetrics()

        now = datetime.now(timezone.utc)

        # Record attempts across 3 hours
        for hour_offset in range(3):
            for i in range(10):
                attempt = RetryAttempt(
                    request_id=f"req-{hour_offset}-{i}",
                    attempt_number=0,
                    proxy_id="proxy-1",
                    timestamp=now - timedelta(hours=hour_offset),
                    outcome=RetryOutcome.SUCCESS,
                    delay_before=0.0,
                    latency=0.5,
                )
                metrics.record_attempt(attempt)

        # Aggregate
        metrics.aggregate_hourly()

        # Should have 3 hourly aggregates
        assert len(metrics.hourly_aggregates) == 3

    def test_removes_old_aggregates(self):
        """Test that aggregates older than retention period are removed."""
        metrics = RetryMetrics(retention_hours=24)

        now = datetime.now(timezone.utc)

        # Record attempts 25 hours ago (beyond retention)
        old_time = now - timedelta(hours=25)
        for i in range(5):
            attempt = RetryAttempt(
                request_id=f"req-old-{i}",
                attempt_number=0,
                proxy_id="proxy-1",
                timestamp=old_time,
                outcome=RetryOutcome.SUCCESS,
                delay_before=0.0,
                latency=0.5,
            )
            metrics.record_attempt(attempt)

        # Record recent attempts
        for i in range(5):
            attempt = RetryAttempt(
                request_id=f"req-recent-{i}",
                attempt_number=0,
                proxy_id="proxy-1",
                timestamp=now,
                outcome=RetryOutcome.SUCCESS,
                delay_before=0.0,
                latency=0.5,
            )
            metrics.record_attempt(attempt)

        # Aggregate
        metrics.aggregate_hourly()

        # Should only have recent aggregates (old ones removed)
        assert all(
            agg.hour >= now - timedelta(hours=24) for agg in metrics.hourly_aggregates.values()
        )

    def test_counts_unique_requests(self):
        """Test that total_requests counts unique request IDs."""
        metrics = RetryMetrics()

        now = datetime.now(timezone.utc)

        # Record 3 attempts for same request
        for attempt_num in range(3):
            attempt = RetryAttempt(
                request_id="req-1",
                attempt_number=attempt_num,
                proxy_id="proxy-1",
                timestamp=now,
                outcome=RetryOutcome.SUCCESS,
                delay_before=float(attempt_num),
                latency=0.5,
            )
            metrics.record_attempt(attempt)

        # Record 1 attempt for different request
        attempt = RetryAttempt(
            request_id="req-2",
            attempt_number=0,
            proxy_id="proxy-1",
            timestamp=now,
            outcome=RetryOutcome.SUCCESS,
            delay_before=0.0,
            latency=0.5,
        )
        metrics.record_attempt(attempt)

        # Aggregate
        metrics.aggregate_hourly()

        # Should count 2 unique requests, 4 total retries
        hour = now.replace(minute=0, second=0, microsecond=0)
        agg = metrics.hourly_aggregates[hour]

        assert agg.total_requests == 2
        assert agg.total_retries == 4


class TestRetryMetricsGetSummary:
    """Test RetryMetrics.get_summary() method."""

    def test_summary_includes_totals(self):
        """Test that summary includes total retries."""
        metrics = RetryMetrics()

        # Record some attempts
        for i in range(10):
            attempt = RetryAttempt(
                request_id=f"req-{i}",
                attempt_number=i % 3,  # Vary attempt numbers
                proxy_id="proxy-1",
                timestamp=datetime.now(timezone.utc),
                outcome=RetryOutcome.SUCCESS if i % 2 == 0 else RetryOutcome.FAILURE,
                delay_before=0.0,
                latency=0.5,
            )
            metrics.record_attempt(attempt)

        summary = metrics.get_summary()

        assert summary["total_retries"] == 10
        assert "success_by_attempt" in summary
        assert "retention_hours" in summary

    def test_success_by_attempt_counts(self):
        """Test that success_by_attempt groups correctly."""
        metrics = RetryMetrics()

        now = datetime.now(timezone.utc)

        # Record successes at different attempt numbers
        for attempt_num in [0, 0, 0, 1, 1, 2]:
            attempt = RetryAttempt(
                request_id=f"req-{attempt_num}",
                attempt_number=attempt_num,
                proxy_id="proxy-1",
                timestamp=now,
                outcome=RetryOutcome.SUCCESS,
                delay_before=0.0,
                latency=0.5,
            )
            metrics.record_attempt(attempt)

        # Aggregate first
        metrics.aggregate_hourly()

        summary = metrics.get_summary()

        # Should have counts: {0: 3, 1: 2, 2: 1}
        assert summary["success_by_attempt"][0] == 3
        assert summary["success_by_attempt"][1] == 2
        assert summary["success_by_attempt"][2] == 1


class TestRetryMetricsCircuitBreakerEvents:
    """Test circuit breaker event recording."""

    def test_record_circuit_breaker_event(self):
        """Test recording circuit breaker state change events."""
        metrics = RetryMetrics()

        event = CircuitBreakerEvent(
            proxy_id="proxy-1",
            from_state=CircuitBreakerState.CLOSED,
            to_state=CircuitBreakerState.OPEN,
            timestamp=datetime.now(timezone.utc),
            failure_count=5,
        )

        metrics.record_circuit_breaker_event(event)

        assert len(metrics.circuit_breaker_events) == 1
        assert metrics.circuit_breaker_events[0] == event

    def test_trims_circuit_breaker_events(self):
        """Test that circuit breaker events are trimmed at 1000."""
        metrics = RetryMetrics()

        # Record 1500 events
        for i in range(1500):
            event = CircuitBreakerEvent(
                proxy_id=f"proxy-{i}",
                from_state=CircuitBreakerState.CLOSED,
                to_state=CircuitBreakerState.OPEN,
                timestamp=datetime.now(timezone.utc),
                failure_count=5,
            )
            metrics.record_circuit_breaker_event(event)

        # Should only keep last 1000
        assert len(metrics.circuit_breaker_events) == 1000


class TestRetryMetricsTimeSeries:
    """Test time-series metrics queries."""

    def test_get_timeseries_returns_hourly_data(self):
        """Test that get_timeseries returns hourly data points."""
        metrics = RetryMetrics()

        now = datetime.now(timezone.utc)

        # Record attempts across 3 hours
        for hour_offset in range(3):
            for i in range(10):
                attempt = RetryAttempt(
                    request_id=f"req-{hour_offset}-{i}",
                    attempt_number=0,
                    proxy_id="proxy-1",
                    timestamp=now - timedelta(hours=hour_offset),
                    outcome=RetryOutcome.SUCCESS if i < 8 else RetryOutcome.FAILURE,
                    delay_before=0.0,
                    latency=0.5,
                )
                metrics.record_attempt(attempt)

        # Aggregate
        metrics.aggregate_hourly()

        # Get time series
        timeseries = metrics.get_timeseries(hours=24)

        # Should have 3 data points
        assert len(timeseries) == 3

        # Each point should have required fields
        for point in timeseries:
            assert "timestamp" in point
            assert "total_requests" in point
            assert "total_retries" in point
            assert "success_rate" in point


class TestRetryMetricsByProxy:
    """Test per-proxy metrics queries."""

    def test_get_by_proxy_aggregates_per_proxy(self):
        """Test that get_by_proxy returns per-proxy statistics."""
        metrics = RetryMetrics()

        now = datetime.now(timezone.utc)

        # Record attempts for multiple proxies
        for proxy_num in range(3):
            for i in range(10):
                attempt = RetryAttempt(
                    request_id=f"req-{proxy_num}-{i}",
                    attempt_number=0,
                    proxy_id=f"proxy-{proxy_num}",
                    timestamp=now,
                    outcome=RetryOutcome.SUCCESS if i < 7 else RetryOutcome.FAILURE,
                    delay_before=0.0,
                    latency=0.5,
                )
                metrics.record_attempt(attempt)

        # Get per-proxy stats
        stats = metrics.get_by_proxy(hours=24)

        # Should have 3 proxies
        assert len(stats) == 3

        # Each should have correct counts
        for proxy_id, proxy_stats in stats.items():
            assert proxy_stats["total_attempts"] == 10
            assert proxy_stats["success_count"] == 7
            assert proxy_stats["failure_count"] == 3

    def test_includes_circuit_breaker_opens(self):
        """Test that per-proxy stats include circuit breaker opens."""
        metrics = RetryMetrics()

        now = datetime.now(timezone.utc)

        # Record circuit breaker events
        for i in range(3):
            event = CircuitBreakerEvent(
                proxy_id="proxy-1",
                from_state=CircuitBreakerState.CLOSED,
                to_state=CircuitBreakerState.OPEN,
                timestamp=now,
                failure_count=5,
            )
            metrics.record_circuit_breaker_event(event)

        # Record some attempts for the proxy
        attempt = RetryAttempt(
            request_id="req-1",
            attempt_number=0,
            proxy_id="proxy-1",
            timestamp=now,
            outcome=RetryOutcome.SUCCESS,
            delay_before=0.0,
            latency=0.5,
        )
        metrics.record_attempt(attempt)

        # Get stats
        stats = metrics.get_by_proxy(hours=24)

        # Should show 3 circuit breaker opens
        assert stats["proxy-1"]["circuit_breaker_opens"] == 3
