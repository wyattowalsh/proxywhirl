"""
Retry execution orchestration with intelligent proxy selection.
"""

import time
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

import httpx
from loguru import logger
from tenacity import (
    RetryCallState,
    RetryError,
    Retrying,
    retry_if_exception,
    stop_after_attempt,
    wait_fixed,
)

from proxywhirl.circuit_breaker import CircuitBreaker, CircuitBreakerState
from proxywhirl.exceptions import ProxyConnectionError, ProxyPoolEmptyError
from proxywhirl.models import Proxy
from proxywhirl.retry_metrics import (
    CircuitBreakerEvent,
    RetryAttempt,
    RetryMetrics,
    RetryOutcome,
)
from proxywhirl.retry_policy import RetryPolicy


class RetryableError(Exception):
    """Exception that triggers a retry."""

    pass


class NonRetryableError(Exception):
    """Exception that does not trigger a retry."""

    pass


class RetryExecutor:
    """
    Orchestrates retry logic with exponential backoff and circuit breaker integration.
    """

    def __init__(
        self,
        retry_policy: RetryPolicy,
        circuit_breakers: Dict[str, CircuitBreaker],
        retry_metrics: RetryMetrics,
    ) -> None:
        """
        Initialize retry executor.

        Args:
            retry_policy: Retry configuration
            circuit_breakers: Circuit breakers by proxy ID
            retry_metrics: Metrics collection instance
        """
        self.retry_policy     = retry_policy
        self.circuit_breakers = circuit_breakers
        self.retry_metrics    = retry_metrics

    def execute_with_retry(
        self,
        request_fn: Callable[[], httpx.Response],
        proxy: Proxy,
        method: str,
        url: str,
        request_id: Optional[str] = None,
    ) -> httpx.Response:
        """
        Execute a request with retry logic.

        Args:
            request_fn: Function that executes the request
            proxy: Initial proxy to use
            method: HTTP method
            url: Request URL
            request_id: Optional request ID for tracking

        Returns:
            HTTP response

        Raises:
            ProxyConnectionError: If all retries exhausted
            NonRetryableError: If error is not retryable
        """
        if request_id is None:
            request_id = str(uuid.uuid4())

        # Check if request is idempotent
        if not self._is_retryable_method(method):
            logger.debug(
                f"Non-idempotent method {method} - retries disabled unless explicitly enabled"
            )
            if not self.retry_policy.retry_non_idempotent:
                # Execute once without retry
                return self._execute_single_attempt(
                    request_fn, proxy, request_id, 0, 0.0
                )

        # Set up retry with tenacity
        attempt_number = 0
        last_exception: Exception | None = None
        start_time = time.time()

        for attempt in range(self.retry_policy.max_attempts):
            # Check timeout
            if self.retry_policy.timeout:
                elapsed = time.time() - start_time
                if elapsed >= self.retry_policy.timeout:
                    logger.warning(
                        f"Request timeout exceeded ({self.retry_policy.timeout}s) "
                        f"after {attempt} attempts"
                    )
                    self._record_attempt(
                        request_id, attempt, proxy.id, RetryOutcome.TIMEOUT, 0.0, 0.0,
                        error_message="Total timeout exceeded"
                    )
                    raise ProxyConnectionError(f"Request timeout after {elapsed:.2f}s")

            # Calculate delay for this attempt
            if attempt > 0:
                delay = self.retry_policy.calculate_delay(attempt - 1)
                logger.info(
                    f"Retry attempt {attempt + 1}/{self.retry_policy.max_attempts} "
                    f"after {delay:.2f}s delay"
                )
                time.sleep(delay)
            else:
                delay = 0.0

            # Execute attempt
            attempt_start = time.time()
            try:
                response = request_fn()
                latency = time.time() - attempt_start

                # Check if status code is retryable
                if response.status_code in self.retry_policy.retry_status_codes:
                    logger.warning(
                        f"Received retryable status {response.status_code} from "
                        f"proxy {proxy.id}"
                    )
                    self._record_attempt(
                        request_id, attempt, proxy.id, RetryOutcome.FAILURE,
                        delay, latency, error_message=f"Status {response.status_code}"
                    )
                    self._record_proxy_failure(proxy)
                    last_exception = ProxyConnectionError(
                        f"Status code {response.status_code}"
                    )
                    continue

                # Success!
                self._record_attempt(
                    request_id, attempt, proxy.id, RetryOutcome.SUCCESS,
                    delay, latency, status_code=response.status_code
                )
                self._record_proxy_success(proxy)

                logger.info(
                    f"Request succeeded on attempt {attempt + 1} using proxy {proxy.id}"
                )
                return response

            except (httpx.ConnectError, httpx.TimeoutException) as e:
                latency = time.time() - attempt_start
                logger.warning(f"Connection error with proxy {proxy.id}: {e}")

                self._record_attempt(
                    request_id, attempt, proxy.id, RetryOutcome.FAILURE,
                    delay, latency, error_message=str(e)
                )
                self._record_proxy_failure(proxy)
                last_exception = e
                continue

            except Exception as e:
                latency = time.time() - attempt_start
                # Check if error is retryable
                if self._is_retryable_error(e):
                    logger.warning(f"Retryable error with proxy {proxy.id}: {e}")
                    self._record_attempt(
                        request_id, attempt, proxy.id, RetryOutcome.FAILURE,
                        delay, latency, error_message=str(e)
                    )
                    self._record_proxy_failure(proxy)
                    last_exception = e
                    continue
                else:
                    logger.error(f"Non-retryable error: {e}")
                    self._record_attempt(
                        request_id, attempt, proxy.id, RetryOutcome.FAILURE,
                        delay, latency, error_message=str(e)
                    )
                    raise NonRetryableError(str(e)) from e

        # All retries exhausted
        logger.error(
            f"All {self.retry_policy.max_attempts} retry attempts exhausted "
            f"for request {request_id}"
        )
        if last_exception:
            raise ProxyConnectionError(
                f"Request failed after {self.retry_policy.max_attempts} attempts"
            ) from last_exception
        else:
            raise ProxyConnectionError(
                f"Request failed after {self.retry_policy.max_attempts} attempts"
            )

    def _execute_single_attempt(
        self,
        request_fn: Callable[[], httpx.Response],
        proxy: Proxy,
        request_id: str,
        attempt: int,
        delay: float,
    ) -> httpx.Response:
        """Execute a single request attempt without retry."""
        attempt_start = time.time()
        try:
            response = request_fn()
            latency = time.time() - attempt_start

            self._record_attempt(
                request_id, attempt, proxy.id, RetryOutcome.SUCCESS,
                delay, latency, status_code=response.status_code
            )
            self._record_proxy_success(proxy)
            return response

        except Exception as e:
            latency = time.time() - attempt_start
            self._record_attempt(
                request_id, attempt, proxy.id, RetryOutcome.FAILURE,
                delay, latency, error_message=str(e)
            )
            self._record_proxy_failure(proxy)
            raise

    def _is_retryable_method(self, method: str) -> bool:
        """Check if HTTP method is safe to retry (idempotent)."""
        idempotent_methods = {"GET", "HEAD", "OPTIONS", "DELETE", "PUT"}
        return method.upper() in idempotent_methods

    def _is_retryable_error(self, error: Exception) -> bool:
        """Determine if an error should trigger a retry."""
        retryable_types = (
            httpx.ConnectError,
            httpx.TimeoutException,
            httpx.ReadTimeout,
            httpx.WriteTimeout,
            httpx.PoolTimeout,
            httpx.NetworkError,
        )
        return isinstance(error, retryable_types)

    def _record_attempt(
        self,
        request_id: str,
        attempt_number: int,
        proxy_id: str,
        outcome: RetryOutcome,
        delay_before: float,
        latency: float,
        status_code: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """Record a retry attempt in metrics."""
        attempt = RetryAttempt(
            request_id     = request_id,
            attempt_number = attempt_number,
            proxy_id       = proxy_id,
            timestamp      = datetime.now(timezone.utc),
            outcome        = outcome,
            status_code    = status_code,
            delay_before   = delay_before,
            latency        = latency,
            error_message  = error_message,
        )
        self.retry_metrics.record_attempt(attempt)

    def _record_proxy_failure(self, proxy: Proxy) -> None:
        """Record a proxy failure in circuit breaker."""
        circuit_breaker = self.circuit_breakers.get(proxy.id)
        if circuit_breaker:
            old_state = circuit_breaker.state
            circuit_breaker.record_failure()
            new_state = circuit_breaker.state

            # Record state change if it occurred
            if old_state != new_state:
                event = CircuitBreakerEvent(
                    proxy_id      = proxy.id,
                    from_state    = old_state,
                    to_state      = new_state,
                    timestamp     = datetime.now(timezone.utc),
                    failure_count = circuit_breaker.failure_count,
                )
                self.retry_metrics.record_circuit_breaker_event(event)
                logger.warning(
                    f"Circuit breaker for proxy {proxy.id} transitioned "
                    f"from {old_state.value} to {new_state.value}"
                )

    def _record_proxy_success(self, proxy: Proxy) -> None:
        """Record a proxy success in circuit breaker."""
        circuit_breaker = self.circuit_breakers.get(proxy.id)
        if circuit_breaker:
            old_state = circuit_breaker.state
            circuit_breaker.record_success()
            new_state = circuit_breaker.state

            # Record state change if it occurred
            if old_state != new_state:
                event = CircuitBreakerEvent(
                    proxy_id      = proxy.id,
                    from_state    = old_state,
                    to_state      = new_state,
                    timestamp     = datetime.now(timezone.utc),
                    failure_count = circuit_breaker.failure_count,
                )
                self.retry_metrics.record_circuit_breaker_event(event)
                logger.info(
                    f"Circuit breaker for proxy {proxy.id} transitioned "
                    f"from {old_state.value} to {new_state.value}"
                )

    def select_retry_proxy(
        self,
        available_proxies: List[Proxy],
        failed_proxy: Proxy,
    ) -> Proxy | None:
        """
        Select best proxy for retry based on performance metrics.

        Args:
            available_proxies: List of available proxies
            failed_proxy: The proxy that just failed

        Returns:
            Best proxy for retry, or None if no suitable proxy found
        """
        # Filter out failed proxy and check circuit breakers
        candidates = []
        for proxy in available_proxies:
            if proxy.id == failed_proxy.id:
                continue

            circuit_breaker = self.circuit_breakers.get(proxy.id)
            if circuit_breaker and not circuit_breaker.should_attempt_request():
                continue

            candidates.append(proxy)

        if not candidates:
            return None

        # For now, return first candidate
        # TODO: Implement intelligent selection based on success rates (US3)
        return candidates[0]
