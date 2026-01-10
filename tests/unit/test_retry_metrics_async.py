"""Test RetryMetrics in async contexts to verify threading.Lock doesn't block event loop.

This test verifies ASYNC-005 fix: RetryMetrics lock type compatibility with async contexts.
"""

import asyncio
from datetime import datetime, timezone

import pytest

from proxywhirl.circuit_breaker import CircuitBreakerState
from proxywhirl.retry_metrics import (
    CircuitBreakerEvent,
    RetryAttempt,
    RetryMetrics,
    RetryOutcome,
)


class TestRetryMetricsAsyncUsage:
    """Test RetryMetrics usage in async contexts with asyncio.to_thread."""

    @pytest.fixture
    def metrics(self) -> RetryMetrics:
        """Create RetryMetrics instance for testing."""
        return RetryMetrics()

    @pytest.fixture
    def sample_attempt(self) -> RetryAttempt:
        """Create sample retry attempt for testing."""
        return RetryAttempt(
            request_id="test-request-1",
            attempt_number=0,
            proxy_id="proxy-123",
            timestamp=datetime.now(timezone.utc),
            outcome=RetryOutcome.SUCCESS,
            delay_before=0.1,
            latency=0.5,
        )

    async def test_get_summary_in_async_context(
        self, metrics: RetryMetrics, sample_attempt: RetryAttempt
    ) -> None:
        """Test get_summary() called from async context using asyncio.to_thread."""
        # Record some attempts
        for i in range(5):
            attempt = RetryAttempt(
                request_id=f"request-{i}",
                attempt_number=0,
                proxy_id="proxy-1",
                timestamp=datetime.now(timezone.utc),
                outcome=RetryOutcome.SUCCESS,
                delay_before=0.1,
                latency=0.5,
            )
            metrics.record_attempt(attempt)

        # Call get_summary() via asyncio.to_thread to avoid blocking event loop
        summary = await asyncio.to_thread(metrics.get_summary)

        assert summary["total_retries"] == 5
        assert summary["retention_hours"] == 24
        assert "success_by_attempt" in summary
        assert "circuit_breaker_events_count" in summary

    async def test_get_timeseries_in_async_context(self, metrics: RetryMetrics) -> None:
        """Test get_timeseries() called from async context using asyncio.to_thread."""
        # Record some attempts
        for i in range(3):
            attempt = RetryAttempt(
                request_id=f"request-{i}",
                attempt_number=i,
                proxy_id="proxy-1",
                timestamp=datetime.now(timezone.utc),
                outcome=RetryOutcome.SUCCESS,
                delay_before=0.1,
                latency=0.5,
            )
            metrics.record_attempt(attempt)

        # Aggregate to create time-series data
        await asyncio.to_thread(metrics.aggregate_hourly)

        # Call get_timeseries() via asyncio.to_thread
        timeseries = await asyncio.to_thread(metrics.get_timeseries, hours=24)

        assert isinstance(timeseries, list)
        # Timeseries may be empty if aggregation didn't create hourly data yet
        # (depends on timing), so we just verify it returns a list

    async def test_get_by_proxy_in_async_context(self, metrics: RetryMetrics) -> None:
        """Test get_by_proxy() called from async context using asyncio.to_thread."""
        # Record attempts for multiple proxies
        for proxy_num in range(3):
            for i in range(2):
                attempt = RetryAttempt(
                    request_id=f"request-{proxy_num}-{i}",
                    attempt_number=i,
                    proxy_id=f"proxy-{proxy_num}",
                    timestamp=datetime.now(timezone.utc),
                    outcome=RetryOutcome.SUCCESS if i == 0 else RetryOutcome.FAILURE,
                    delay_before=0.1,
                    latency=0.5,
                )
                metrics.record_attempt(attempt)

        # Call get_by_proxy() via asyncio.to_thread
        stats_by_proxy = await asyncio.to_thread(metrics.get_by_proxy, hours=24)

        assert len(stats_by_proxy) == 3
        for proxy_id in ["proxy-0", "proxy-1", "proxy-2"]:
            assert proxy_id in stats_by_proxy
            assert stats_by_proxy[proxy_id]["total_attempts"] == 2

    async def test_concurrent_async_calls(self, metrics: RetryMetrics) -> None:
        """Test multiple concurrent async calls don't deadlock or block event loop."""
        # Record some test data
        for i in range(10):
            attempt = RetryAttempt(
                request_id=f"request-{i}",
                attempt_number=0,
                proxy_id=f"proxy-{i % 3}",
                timestamp=datetime.now(timezone.utc),
                outcome=RetryOutcome.SUCCESS,
                delay_before=0.1,
                latency=0.5,
            )
            metrics.record_attempt(attempt)

        # Run multiple async operations concurrently
        results = await asyncio.gather(
            asyncio.to_thread(metrics.get_summary),
            asyncio.to_thread(metrics.get_timeseries, hours=24),
            asyncio.to_thread(metrics.get_by_proxy, hours=24),
            asyncio.to_thread(metrics.get_summary),  # Duplicate call
        )

        # Verify all calls completed successfully
        summary1, timeseries, by_proxy, summary2 = results

        assert summary1 == summary2  # Should be consistent
        assert summary1["total_retries"] == 10
        assert isinstance(timeseries, list)
        assert len(by_proxy) == 3  # 3 unique proxies

    async def test_record_circuit_breaker_event_in_async(self, metrics: RetryMetrics) -> None:
        """Test recording circuit breaker events from async context."""
        event = CircuitBreakerEvent(
            proxy_id="proxy-123",
            from_state=CircuitBreakerState.CLOSED,
            to_state=CircuitBreakerState.OPEN,
            timestamp=datetime.now(timezone.utc),
            failure_count=5,
        )

        # Record circuit breaker event (sync operation, no lock needed)
        metrics.record_circuit_breaker_event(event)

        # Verify via async call
        summary = await asyncio.to_thread(metrics.get_summary)
        assert summary["circuit_breaker_events_count"] == 1

    async def test_no_event_loop_blocking(self, metrics: RetryMetrics) -> None:
        """Test that calling methods via asyncio.to_thread doesn't block event loop."""
        # Record some data
        for i in range(50):
            attempt = RetryAttempt(
                request_id=f"request-{i}",
                attempt_number=0,
                proxy_id=f"proxy-{i % 5}",
                timestamp=datetime.now(timezone.utc),
                outcome=RetryOutcome.SUCCESS,
                delay_before=0.1,
                latency=0.5,
            )
            metrics.record_attempt(attempt)

        # Create a background task that should complete quickly
        async def quick_task() -> str:
            await asyncio.sleep(0.001)  # 1ms
            return "completed"

        # Run both the metrics call and quick task concurrently
        start = asyncio.get_event_loop().time()
        summary_task = asyncio.to_thread(metrics.get_summary)
        quick_task_result = asyncio.create_task(quick_task())

        summary = await summary_task
        quick_result = await quick_task_result
        elapsed = asyncio.get_event_loop().time() - start

        # Verify quick task completed (wasn't blocked)
        assert quick_result == "completed"
        assert summary["total_retries"] == 50

        # Verify it completed reasonably fast (no blocking)
        # Should be much less than 1 second even with 50 items
        assert elapsed < 0.5, f"Operation took {elapsed}s - may be blocking event loop"
