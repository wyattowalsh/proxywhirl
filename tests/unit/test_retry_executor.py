"""
Unit tests for RetryExecutor.
"""

import asyncio
from unittest.mock import Mock, patch

import httpx
import pytest

from proxywhirl import Proxy
from proxywhirl.circuit_breaker import CircuitBreaker, CircuitBreakerState
from proxywhirl.exceptions import ProxyConnectionError
from proxywhirl.retry import (
    NonRetryableError,
    RetryableError,
    RetryAttempt,
    RetryExecutor,
    RetryMetrics,
    RetryOutcome,
    RetryPolicy,
)


class TestIntelligentProxySelection:
    """Test intelligent proxy selection algorithm."""

    def test_excludes_failed_proxy(self):
        """Test that failed proxy is excluded from selection."""
        policy = RetryPolicy()
        circuit_breakers = {}
        metrics = RetryMetrics()

        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        proxy2 = Proxy(url="http://proxy2.example.com:8080")

        circuit_breakers[str(proxy1.id)] = CircuitBreaker(proxy_id=str(proxy1.id))
        circuit_breakers[str(proxy2.id)] = CircuitBreaker(proxy_id=str(proxy2.id))

        executor = RetryExecutor(policy, circuit_breakers, metrics)

        # Select proxy when proxy1 failed
        selected = executor.select_retry_proxy([proxy1, proxy2], proxy1)

        assert selected == proxy2
        assert selected.id != proxy1.id

    def test_excludes_open_circuit_breakers(self):
        """Test that proxies with open circuit breakers are excluded."""
        policy = RetryPolicy()
        circuit_breakers = {}
        metrics = RetryMetrics()

        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        proxy2 = Proxy(url="http://proxy2.example.com:8080")
        proxy3 = Proxy(url="http://proxy3.example.com:8080")

        circuit_breakers[str(proxy1.id)] = CircuitBreaker(proxy_id=str(proxy1.id))
        circuit_breakers[str(proxy2.id)] = CircuitBreaker(proxy_id=str(proxy2.id))
        circuit_breakers[str(proxy3.id)] = CircuitBreaker(proxy_id=str(proxy3.id))

        # Open circuit for proxy2
        for _ in range(5):
            circuit_breakers[str(proxy2.id)].record_failure()

        assert circuit_breakers[str(proxy2.id)].state == CircuitBreakerState.OPEN

        executor = RetryExecutor(policy, circuit_breakers, metrics)

        # Select proxy when proxy1 failed
        selected = executor.select_retry_proxy([proxy1, proxy2, proxy3], proxy1)

        # Should select proxy3 (proxy1 is failed, proxy2 circuit is open)
        assert selected == proxy3

    def test_prioritizes_high_success_rate(self):
        """Test that proxies with higher success rates are prioritized."""
        policy = RetryPolicy()
        circuit_breakers = {}
        metrics = RetryMetrics()

        # Create proxies with different success rates
        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        proxy1.total_requests = 100
        proxy1.total_successes = 95  # 95% success rate

        proxy2 = Proxy(url="http://proxy2.example.com:8080")
        proxy2.total_requests = 100
        proxy2.total_successes = 60  # 60% success rate

        failed_proxy = Proxy(url="http://failed.example.com:8080")

        circuit_breakers[str(proxy1.id)] = CircuitBreaker(proxy_id=str(proxy1.id))
        circuit_breakers[str(proxy2.id)] = CircuitBreaker(proxy_id=str(proxy2.id))
        circuit_breakers[str(failed_proxy.id)] = CircuitBreaker(proxy_id=str(failed_proxy.id))

        executor = RetryExecutor(policy, circuit_breakers, metrics)

        # Select proxy
        selected = executor.select_retry_proxy([proxy1, proxy2], failed_proxy)

        # Should select proxy1 (higher success rate)
        assert selected == proxy1

    def test_returns_none_when_no_candidates(self):
        """Test that None is returned when no suitable proxies available."""
        policy = RetryPolicy()
        circuit_breakers = {}
        metrics = RetryMetrics()

        proxy1 = Proxy(url="http://proxy1.example.com:8080")

        circuit_breakers[str(proxy1.id)] = CircuitBreaker(proxy_id=str(proxy1.id))

        executor = RetryExecutor(policy, circuit_breakers, metrics)

        # Only one proxy available, and it's the failed one
        selected = executor.select_retry_proxy([proxy1], proxy1)

        assert selected is None

    def test_geo_targeting_awareness(self):
        """Test that geo-targeting gives bonus to matching region."""
        policy = RetryPolicy()
        circuit_breakers = {}
        metrics = RetryMetrics()

        # Create proxies with different regions
        proxy_us = Proxy(
            url="http://proxy-us.example.com:8080",
            metadata={"region": "US-EAST"},
        )
        proxy_us.total_requests = 100
        proxy_us.total_successes = 80  # 80% success rate

        proxy_eu = Proxy(
            url="http://proxy-eu.example.com:8080",
            metadata={"region": "EU-WEST"},
        )
        proxy_eu.total_requests = 100
        proxy_eu.total_successes = 85  # 85% success rate (slightly better)

        failed_proxy = Proxy(url="http://failed.example.com:8080")

        circuit_breakers[str(proxy_us.id)] = CircuitBreaker(proxy_id=str(proxy_us.id))
        circuit_breakers[str(proxy_eu.id)] = CircuitBreaker(proxy_id=str(proxy_eu.id))
        circuit_breakers[str(failed_proxy.id)] = CircuitBreaker(proxy_id=str(failed_proxy.id))

        executor = RetryExecutor(policy, circuit_breakers, metrics)

        # Select proxy with US target region
        selected = executor.select_retry_proxy(
            [proxy_us, proxy_eu], failed_proxy, target_region="US-EAST"
        )

        # Should select proxy_us despite lower success rate (10% region bonus)
        assert selected == proxy_us

    def test_score_calculation(self):
        """Test proxy score calculation."""
        policy = RetryPolicy()
        circuit_breakers = {}
        metrics = RetryMetrics()

        proxy = Proxy(url="http://proxy1.example.com:8080")
        proxy.total_requests = 100
        proxy.total_successes = 90  # 90% success rate

        circuit_breakers[str(proxy.id)] = CircuitBreaker(proxy_id=str(proxy.id))

        executor = RetryExecutor(policy, circuit_breakers, metrics)

        score = executor._calculate_proxy_score(proxy)

        # Base score: (0.7 * 0.9) + (0.3 * 1.0) = 0.63 + 0.3 = 0.93
        # (assuming no latency data, normalized_latency = 0)
        assert score >= 0.9  # Should be high score


class TestRetryableExceptions:
    """Test exception classes."""

    def test_retryable_error(self):
        """Test RetryableError can be raised and caught."""
        with pytest.raises(RetryableError):
            raise RetryableError("Test retryable error")

    def test_non_retryable_error(self):
        """Test NonRetryableError can be raised and caught."""
        with pytest.raises(NonRetryableError):
            raise NonRetryableError("Test non-retryable error")


class TestIsRetryableMethod:
    """Test _is_retryable_method helper."""

    @pytest.fixture
    def executor(self):
        """Create executor for testing."""
        policy = RetryPolicy()
        return RetryExecutor(policy, {}, RetryMetrics())

    def test_get_is_retryable(self, executor):
        """GET should be retryable."""
        assert executor._is_retryable_method("GET") is True
        assert executor._is_retryable_method("get") is True

    def test_head_is_retryable(self, executor):
        """HEAD should be retryable."""
        assert executor._is_retryable_method("HEAD") is True

    def test_options_is_retryable(self, executor):
        """OPTIONS should be retryable."""
        assert executor._is_retryable_method("OPTIONS") is True

    def test_delete_is_retryable(self, executor):
        """DELETE should be retryable."""
        assert executor._is_retryable_method("DELETE") is True

    def test_put_is_retryable(self, executor):
        """PUT should be retryable."""
        assert executor._is_retryable_method("PUT") is True

    def test_post_is_not_retryable(self, executor):
        """POST should not be retryable."""
        assert executor._is_retryable_method("POST") is False

    def test_patch_is_not_retryable(self, executor):
        """PATCH should not be retryable."""
        assert executor._is_retryable_method("PATCH") is False


class TestIsRetryableError:
    """Test _is_retryable_error helper."""

    @pytest.fixture
    def executor(self):
        """Create executor for testing."""
        policy = RetryPolicy()
        return RetryExecutor(policy, {}, RetryMetrics())

    def test_connect_error_is_retryable(self, executor):
        """ConnectError should be retryable."""
        error = httpx.ConnectError("Connection failed")
        assert executor._is_retryable_error(error) is True

    def test_timeout_exception_is_retryable(self, executor):
        """TimeoutException should be retryable."""
        error = httpx.TimeoutException("Timeout")
        assert executor._is_retryable_error(error) is True

    def test_read_timeout_is_retryable(self, executor):
        """ReadTimeout should be retryable."""
        error = httpx.ReadTimeout("Read timeout")
        assert executor._is_retryable_error(error) is True

    def test_write_timeout_is_retryable(self, executor):
        """WriteTimeout should be retryable."""
        error = httpx.WriteTimeout("Write timeout")
        assert executor._is_retryable_error(error) is True

    def test_pool_timeout_is_retryable(self, executor):
        """PoolTimeout should be retryable."""
        error = httpx.PoolTimeout("Pool timeout")
        assert executor._is_retryable_error(error) is True

    def test_network_error_is_retryable(self, executor):
        """NetworkError should be retryable."""
        error = httpx.NetworkError("Network error")
        assert executor._is_retryable_error(error) is True

    def test_value_error_is_not_retryable(self, executor):
        """ValueError should not be retryable."""
        error = ValueError("Invalid value")
        assert executor._is_retryable_error(error) is False

    def test_runtime_error_is_not_retryable(self, executor):
        """RuntimeError should not be retryable."""
        error = RuntimeError("Runtime error")
        assert executor._is_retryable_error(error) is False


class TestExecuteWithRetrySuccess:
    """Test execute_with_retry success scenarios."""

    @pytest.fixture
    def executor(self):
        """Create executor for testing."""
        policy = RetryPolicy(max_attempts=3)
        return RetryExecutor(policy, {}, RetryMetrics())

    def test_success_on_first_attempt(self, executor):
        """Test successful request on first attempt."""
        proxy = Proxy(url="http://proxy.example.com:8080")

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        def request_fn():
            return mock_response

        result = executor.execute_with_retry(request_fn, proxy, "GET", "https://example.com")

        assert result == mock_response
        assert result.status_code == 200

    def test_success_on_retry(self, executor):
        """Test success on second attempt after first failure."""
        proxy = Proxy(url="http://proxy.example.com:8080")

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        attempt_count = 0

        def request_fn():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count == 1:
                raise httpx.ConnectError("First attempt failed")
            return mock_response

        with patch("time.sleep"):  # Skip delay
            result = executor.execute_with_retry(request_fn, proxy, "GET", "https://example.com")

        assert result == mock_response
        assert attempt_count == 2


class TestExecuteWithRetryFailures:
    """Test execute_with_retry failure scenarios."""

    def test_all_retries_exhausted(self):
        """Test ProxyConnectionError raised after all retries exhausted."""
        policy = RetryPolicy(max_attempts=2)
        executor = RetryExecutor(policy, {}, RetryMetrics())

        proxy = Proxy(url="http://proxy.example.com:8080")

        def request_fn():
            raise httpx.ConnectError("Connection failed")

        with (
            patch("time.sleep"),
            pytest.raises(ProxyConnectionError, match="failed after 2 attempts"),
        ):
            executor.execute_with_retry(request_fn, proxy, "GET", "https://example.com")

    def test_retryable_status_code_exhausts_retries(self):
        """Test retryable status code eventually exhausts retries."""
        policy = RetryPolicy(max_attempts=2, retry_status_codes={503})
        executor = RetryExecutor(policy, {}, RetryMetrics())

        proxy = Proxy(url="http://proxy.example.com:8080")

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 503

        def request_fn():
            return mock_response

        with (
            patch("time.sleep"),
            pytest.raises(ProxyConnectionError, match="failed after 2 attempts"),
        ):
            executor.execute_with_retry(request_fn, proxy, "GET", "https://example.com")

    def test_non_retryable_error_raises_immediately(self):
        """Test non-retryable error raises NonRetryableError immediately."""
        policy = RetryPolicy(max_attempts=3)
        executor = RetryExecutor(policy, {}, RetryMetrics())

        proxy = Proxy(url="http://proxy.example.com:8080")

        def request_fn():
            raise ValueError("Invalid request")

        with pytest.raises(NonRetryableError, match="Invalid request"):
            executor.execute_with_retry(request_fn, proxy, "GET", "https://example.com")

    def test_timeout_exceeded(self):
        """Test ProxyConnectionError raised when timeout exceeded."""
        policy = RetryPolicy(max_attempts=10, timeout=1.0)
        executor = RetryExecutor(policy, {}, RetryMetrics())

        proxy = Proxy(url="http://proxy.example.com:8080")

        # Track time progression - start at 0, then jump past timeout
        time_values = [0.0, 0.1, 2.0]  # Third call is past timeout
        time_iter = iter(time_values)

        def mock_time():
            try:
                return next(time_iter)
            except StopIteration:
                return 10.0  # Far past timeout

        def request_fn():
            raise httpx.ConnectError("Connection failed")

        with (
            patch("time.sleep"),
            patch("proxywhirl.retry.executor.time.time", side_effect=mock_time),
            pytest.raises(ProxyConnectionError, match="Request timeout"),
        ):
            executor.execute_with_retry(request_fn, proxy, "GET", "https://example.com")


class TestNonIdempotentMethods:
    """Test handling of non-idempotent HTTP methods."""

    def test_post_without_retry_non_idempotent_flag(self):
        """Test POST executes only once without retry_non_idempotent flag."""
        policy = RetryPolicy(max_attempts=3, retry_non_idempotent=False)
        executor = RetryExecutor(policy, {}, RetryMetrics())

        proxy = Proxy(url="http://proxy.example.com:8080")

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        def request_fn():
            return mock_response

        result = executor.execute_with_retry(request_fn, proxy, "POST", "https://example.com")

        assert result == mock_response

    def test_post_with_retry_non_idempotent_flag(self):
        """Test POST retries with retry_non_idempotent=True."""
        policy = RetryPolicy(max_attempts=3, retry_non_idempotent=True)
        executor = RetryExecutor(policy, {}, RetryMetrics())

        proxy = Proxy(url="http://proxy.example.com:8080")

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        attempt_count = 0

        def request_fn():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count == 1:
                raise httpx.ConnectError("First attempt failed")
            return mock_response

        with patch("time.sleep"):
            result = executor.execute_with_retry(request_fn, proxy, "POST", "https://example.com")

        assert result == mock_response
        assert attempt_count == 2  # Retried

    def test_non_idempotent_single_attempt_failure(self):
        """Test non-idempotent method fails immediately without retry."""
        policy = RetryPolicy(max_attempts=3, retry_non_idempotent=False)
        executor = RetryExecutor(policy, {}, RetryMetrics())

        proxy = Proxy(url="http://proxy.example.com:8080")

        def request_fn():
            raise httpx.ConnectError("Connection failed")

        with pytest.raises(httpx.ConnectError):
            executor.execute_with_retry(request_fn, proxy, "POST", "https://example.com")


class TestRecordProxyFailure:
    """Test _record_proxy_failure circuit breaker integration."""

    def test_records_failure_to_circuit_breaker(self):
        """Test failure is recorded to circuit breaker."""
        policy = RetryPolicy()
        proxy = Proxy(url="http://proxy.example.com:8080")
        circuit_breaker = CircuitBreaker(proxy_id=str(proxy.id))
        circuit_breakers = {str(proxy.id): circuit_breaker}
        metrics = RetryMetrics()

        executor = RetryExecutor(policy, circuit_breakers, metrics)

        initial_failures = circuit_breaker.failure_count
        executor._record_proxy_failure(proxy)

        assert circuit_breaker.failure_count == initial_failures + 1

    def test_records_circuit_breaker_state_change(self):
        """Test circuit breaker state change is recorded in metrics."""
        policy = RetryPolicy()
        proxy = Proxy(url="http://proxy.example.com:8080")
        # Create circuit breaker with low threshold for easy state change
        circuit_breaker = CircuitBreaker(proxy_id=str(proxy.id), failure_threshold=2)
        circuit_breakers = {str(proxy.id): circuit_breaker}
        metrics = RetryMetrics()

        executor = RetryExecutor(policy, circuit_breakers, metrics)

        # Record failures to trigger state change
        executor._record_proxy_failure(proxy)
        executor._record_proxy_failure(proxy)

        assert circuit_breaker.state == CircuitBreakerState.OPEN
        assert len(metrics.circuit_breaker_events) >= 1

    def test_no_circuit_breaker_available(self):
        """Test graceful handling when circuit breaker not found."""
        policy = RetryPolicy()
        proxy = Proxy(url="http://proxy.example.com:8080")
        metrics = RetryMetrics()

        executor = RetryExecutor(policy, {}, metrics)

        # Should not raise
        executor._record_proxy_failure(proxy)


class TestRecordProxySuccess:
    """Test _record_proxy_success circuit breaker integration."""

    def test_records_success_from_half_open(self):
        """Test success in HALF_OPEN state closes circuit and records event."""
        policy = RetryPolicy()
        proxy = Proxy(url="http://proxy.example.com:8080")
        # Create circuit breaker with low threshold
        circuit_breaker = CircuitBreaker(
            proxy_id=str(proxy.id),
            failure_threshold=2,
            timeout_duration=0.001,  # Very short timeout
        )
        circuit_breakers = {str(proxy.id): circuit_breaker}
        metrics = RetryMetrics()

        executor = RetryExecutor(policy, circuit_breakers, metrics)

        # Open the circuit
        circuit_breaker.record_failure()
        circuit_breaker.record_failure()
        assert circuit_breaker.state == CircuitBreakerState.OPEN

        # Wait for timeout and trigger half-open
        import time

        time.sleep(0.002)  # Longer than timeout_duration
        circuit_breaker.should_attempt_request()  # This transitions to HALF_OPEN
        assert circuit_breaker.state == CircuitBreakerState.HALF_OPEN

        # Now record success - should close circuit
        executor._record_proxy_success(proxy)

        assert circuit_breaker.state == CircuitBreakerState.CLOSED
        # Should have recorded state change event
        assert len(metrics.circuit_breaker_events) >= 1

    def test_success_in_closed_state_does_nothing(self):
        """Test success in CLOSED state doesn't change anything."""
        policy = RetryPolicy()
        proxy = Proxy(url="http://proxy.example.com:8080")
        circuit_breaker = CircuitBreaker(proxy_id=str(proxy.id))
        circuit_breakers = {str(proxy.id): circuit_breaker}
        metrics = RetryMetrics()

        executor = RetryExecutor(policy, circuit_breakers, metrics)

        assert circuit_breaker.state == CircuitBreakerState.CLOSED
        initial_events = len(metrics.circuit_breaker_events)

        # Record success in closed state
        executor._record_proxy_success(proxy)

        # State should still be closed, no new events
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
        assert len(metrics.circuit_breaker_events) == initial_events

    def test_no_circuit_breaker_available(self):
        """Test graceful handling when circuit breaker not found."""
        policy = RetryPolicy()
        proxy = Proxy(url="http://proxy.example.com:8080")
        metrics = RetryMetrics()

        executor = RetryExecutor(policy, {}, metrics)

        # Should not raise
        executor._record_proxy_success(proxy)


class TestRecordAttempt:
    """Test _record_attempt metrics recording."""

    def test_records_attempt_in_metrics(self):
        """Test attempt is recorded in metrics."""
        policy = RetryPolicy()
        metrics = RetryMetrics()

        executor = RetryExecutor(policy, {}, metrics)

        initial_count = len(list(metrics.current_attempts))

        executor._record_attempt(
            request_id="test-123",
            attempt_number=0,
            proxy_id="proxy-1",
            outcome=RetryOutcome.SUCCESS,
            delay_before=0.0,
            latency=0.5,
            status_code=200,
        )

        assert len(list(metrics.current_attempts)) == initial_count + 1

    def test_records_failure_attempt_with_error(self):
        """Test failure attempt with error message is recorded."""
        policy = RetryPolicy()
        metrics = RetryMetrics()

        executor = RetryExecutor(policy, {}, metrics)

        executor._record_attempt(
            request_id="test-456",
            attempt_number=1,
            proxy_id="proxy-2",
            outcome=RetryOutcome.FAILURE,
            delay_before=1.0,
            latency=0.1,
            error_message="Connection refused",
        )

        attempts = list(metrics.current_attempts)
        last_attempt = attempts[-1]
        assert last_attempt.outcome == RetryOutcome.FAILURE
        assert last_attempt.error_message == "Connection refused"


class TestGetProxyAvgLatency:
    """Test _get_proxy_avg_latency calculations."""

    def test_no_attempts_returns_zero(self):
        """Test returns 0.0 when no attempts recorded."""
        policy = RetryPolicy()
        metrics = RetryMetrics()

        executor = RetryExecutor(policy, {}, metrics)

        avg = executor._get_proxy_avg_latency("unknown-proxy")
        assert avg == 0.0

    def test_calculates_average_from_successful_attempts(self):
        """Test average is calculated from successful attempts only."""
        policy = RetryPolicy()
        metrics = RetryMetrics()

        executor = RetryExecutor(policy, {}, metrics)

        # Add some successful attempts
        from datetime import datetime, timezone

        for latency in [1.0, 2.0, 3.0]:
            attempt = RetryAttempt(
                request_id="test",
                attempt_number=0,
                proxy_id="proxy-1",
                timestamp=datetime.now(timezone.utc),
                outcome=RetryOutcome.SUCCESS,
                latency=latency,
                delay_before=0.0,
            )
            metrics.record_attempt(attempt)

        # Add a failure that should not be counted
        failure_attempt = RetryAttempt(
            request_id="test",
            attempt_number=0,
            proxy_id="proxy-1",
            timestamp=datetime.now(timezone.utc),
            outcome=RetryOutcome.FAILURE,
            latency=100.0,
            delay_before=0.0,
        )
        metrics.record_attempt(failure_attempt)

        avg = executor._get_proxy_avg_latency("proxy-1")
        assert avg == 2.0  # (1+2+3)/3 = 2.0


class TestExecuteSingleAttempt:
    """Test _execute_single_attempt method."""

    def test_success_records_metrics(self):
        """Test successful single attempt records metrics."""
        policy = RetryPolicy()
        metrics = RetryMetrics()
        executor = RetryExecutor(policy, {}, metrics)

        proxy = Proxy(url="http://proxy.example.com:8080")
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        def request_fn():
            return mock_response

        result = executor._execute_single_attempt(request_fn, proxy, "req-123", 0, 0.0)

        assert result == mock_response
        assert len(list(metrics.current_attempts)) >= 1

    def test_failure_records_and_reraises(self):
        """Test failed single attempt records metrics and re-raises."""
        policy = RetryPolicy()
        metrics = RetryMetrics()
        executor = RetryExecutor(policy, {}, metrics)

        proxy = Proxy(url="http://proxy.example.com:8080")

        def request_fn():
            raise ValueError("Something went wrong")

        with pytest.raises(ValueError, match="Something went wrong"):
            executor._execute_single_attempt(request_fn, proxy, "req-456", 0, 0.0)

        # Should still record the attempt
        attempts = list(metrics.current_attempts)
        assert len(attempts) >= 1
        assert attempts[-1].outcome == RetryOutcome.FAILURE


class TestCalculateProxyScoreEdgeCases:
    """Test _calculate_proxy_score edge cases."""

    @pytest.fixture
    def executor(self):
        """Create executor for testing."""
        policy = RetryPolicy()
        return RetryExecutor(policy, {}, RetryMetrics())

    def test_no_request_history_neutral_score(self, executor):
        """Test proxy with no history gets neutral score."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        # No requests yet

        score = executor._calculate_proxy_score(proxy)

        # Neutral success_rate = 0.5, no latency penalty
        # Score = (0.7 * 0.5) + (0.3 * 1.0) = 0.35 + 0.3 = 0.65
        assert 0.6 <= score <= 0.7

    def test_region_bonus_capped_at_one(self, executor):
        """Test geo-targeting bonus doesn't exceed 1.0."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            metadata={"region": "US-EAST"},
        )
        proxy.total_requests = 100
        proxy.total_successes = 100  # Perfect success rate

        score = executor._calculate_proxy_score(proxy, target_region="US-EAST")

        # Base: (0.7 * 1.0) + (0.3 * 1.0) = 1.0
        # With 10% bonus: min(1.0 * 1.1, 1.0) = 1.0
        assert score == 1.0

    def test_no_metadata_no_region_bonus(self, executor):
        """Test proxy without metadata gets no region bonus."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        proxy.total_requests = 100
        proxy.total_successes = 80

        score_with_target = executor._calculate_proxy_score(proxy, target_region="US-EAST")
        score_without_target = executor._calculate_proxy_score(proxy)

        assert score_with_target == score_without_target


class TestAsyncExecuteWithRetry:
    """Test async execute_with_retry_async method."""

    @pytest.fixture
    def executor(self):
        """Create executor for testing."""
        policy = RetryPolicy(max_attempts=3)
        return RetryExecutor(policy, {}, RetryMetrics())

    async def test_success_on_first_attempt(self, executor):
        """Test successful async request on first attempt."""
        proxy = Proxy(url="http://proxy.example.com:8080")

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        async def request_fn():
            return mock_response

        result = await executor.execute_with_retry_async(
            request_fn, proxy, "GET", "https://example.com"
        )

        assert result == mock_response
        assert result.status_code == 200

    @pytest.mark.slow
    async def test_success_on_retry_with_asyncio_sleep(self, executor):
        """Test success on second attempt using asyncio.sleep.

        Marked @pytest.mark.slow: Tests async retry delays with actual asyncio.sleep
        which is non-blocking but introduces real time delays to verify backoff behavior.
        """
        proxy = Proxy(url="http://proxy.example.com:8080")

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        attempt_count = 0

        async def request_fn():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count == 1:
                raise httpx.ConnectError("First attempt failed")
            return mock_response

        # No need to patch asyncio.sleep - it's non-blocking and doesn't block event loop
        # We measure that the sleep actually happened to verify backoff timing
        import time

        start = time.time()
        result = await executor.execute_with_retry_async(
            request_fn, proxy, "GET", "https://example.com"
        )
        elapsed = time.time() - start

        assert result == mock_response
        assert attempt_count == 2
        # Should have slept for at least the base delay (default is 1 second)
        assert elapsed >= 1.0

    async def test_all_retries_exhausted(self, executor):
        """Test ProxyConnectionError raised after all async retries exhausted."""
        proxy = Proxy(url="http://proxy.example.com:8080")

        async def request_fn():
            raise httpx.ConnectError("Connection failed")

        with pytest.raises(ProxyConnectionError, match="failed after 3 attempts"):
            await executor.execute_with_retry_async(request_fn, proxy, "GET", "https://example.com")

    async def test_retryable_status_code(self, executor):
        """Test async retry on retryable status code."""
        executor.retry_policy.retry_status_codes = {503}
        proxy = Proxy(url="http://proxy.example.com:8080")

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 503

        async def request_fn():
            return mock_response

        with pytest.raises(ProxyConnectionError, match="failed after 3 attempts"):
            await executor.execute_with_retry_async(request_fn, proxy, "GET", "https://example.com")

    async def test_non_retryable_error_raises_immediately(self, executor):
        """Test non-retryable error raises NonRetryableError immediately in async."""
        proxy = Proxy(url="http://proxy.example.com:8080")

        async def request_fn():
            raise ValueError("Invalid request")

        with pytest.raises(NonRetryableError, match="Invalid request"):
            await executor.execute_with_retry_async(request_fn, proxy, "GET", "https://example.com")

    async def test_timeout_exceeded_async(self, executor):
        """Test ProxyConnectionError raised when timeout exceeded in async."""
        executor.retry_policy.timeout = 1.0
        executor.retry_policy.max_attempts = 10
        proxy = Proxy(url="http://proxy.example.com:8080")

        # Track time progression - start at 0, then jump past timeout
        time_values = [0.0, 0.1, 2.0]  # Third call is past timeout
        time_iter = iter(time_values)

        def mock_time():
            try:
                return next(time_iter)
            except StopIteration:
                return 10.0  # Far past timeout

        async def request_fn():
            raise httpx.ConnectError("Connection failed")

        with (
            patch("proxywhirl.retry.executor.time.time", side_effect=mock_time),
            pytest.raises(ProxyConnectionError, match="Request timeout"),
        ):
            await executor.execute_with_retry_async(request_fn, proxy, "GET", "https://example.com")

    async def test_post_without_retry_non_idempotent_flag_async(self, executor):
        """Test async POST executes only once without retry_non_idempotent flag."""
        executor.retry_policy.retry_non_idempotent = False
        proxy = Proxy(url="http://proxy.example.com:8080")

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        async def request_fn():
            return mock_response

        result = await executor.execute_with_retry_async(
            request_fn, proxy, "POST", "https://example.com"
        )

        assert result == mock_response

    async def test_post_with_retry_non_idempotent_flag_async(self, executor):
        """Test async POST retries with retry_non_idempotent=True."""
        executor.retry_policy.retry_non_idempotent = True
        proxy = Proxy(url="http://proxy.example.com:8080")

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        attempt_count = 0

        async def request_fn():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count == 1:
                raise httpx.ConnectError("First attempt failed")
            return mock_response

        result = await executor.execute_with_retry_async(
            request_fn, proxy, "POST", "https://example.com"
        )

        assert result == mock_response
        assert attempt_count == 2  # Retried

    async def test_non_idempotent_single_attempt_failure_async(self, executor):
        """Test async non-idempotent method fails immediately without retry."""
        executor.retry_policy.retry_non_idempotent = False
        proxy = Proxy(url="http://proxy.example.com:8080")

        async def request_fn():
            raise httpx.ConnectError("Connection failed")

        with pytest.raises(httpx.ConnectError):
            await executor.execute_with_retry_async(
                request_fn, proxy, "POST", "https://example.com"
            )


class TestAsyncExecuteSingleAttempt:
    """Test async _execute_single_attempt_async method."""

    @pytest.fixture
    def executor(self):
        """Create executor for testing."""
        policy = RetryPolicy()
        return RetryExecutor(policy, {}, RetryMetrics())

    async def test_success_records_metrics(self, executor):
        """Test successful async single attempt records metrics."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200

        async def request_fn():
            return mock_response

        result = await executor._execute_single_attempt_async(request_fn, proxy, "req-123", 0, 0.0)

        assert result == mock_response
        metrics = executor.retry_metrics
        assert len(list(metrics.current_attempts)) >= 1

    async def test_failure_records_and_reraises(self, executor):
        """Test failed async single attempt records metrics and re-raises."""
        proxy = Proxy(url="http://proxy.example.com:8080")

        async def request_fn():
            raise ValueError("Something went wrong")

        with pytest.raises(ValueError, match="Something went wrong"):
            await executor._execute_single_attempt_async(request_fn, proxy, "req-456", 0, 0.0)

        # Should still record the attempt
        metrics = executor.retry_metrics
        attempts = list(metrics.current_attempts)
        assert len(attempts) >= 1
        assert attempts[-1].outcome == RetryOutcome.FAILURE


class TestAsyncSleepNonBlocking:
    """Test that async sleep doesn't block the event loop."""

    async def test_asyncio_sleep_is_non_blocking(self):
        """Verify that asyncio.sleep allows other tasks to run."""
        policy = RetryPolicy(max_attempts=2, base_delay=0.5)
        executor = RetryExecutor(policy, {}, RetryMetrics())

        proxy = Proxy(url="http://proxy.example.com:8080")

        attempt_count = 0
        task_ran = False

        async def request_fn():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count == 1:
                raise httpx.ConnectError("First attempt failed")
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 200
            return mock_response

        async def other_task():
            """Another task that should run during the sleep."""
            nonlocal task_ran
            await asyncio.sleep(0.1)  # Short delay
            task_ran = True

        # Run both tasks concurrently
        results = await asyncio.gather(
            executor.execute_with_retry_async(request_fn, proxy, "GET", "https://example.com"),
            other_task(),
        )

        # Verify both tasks completed
        assert results[0].status_code == 200
        assert task_ran is True  # Other task ran during retry sleep
        assert attempt_count == 2
