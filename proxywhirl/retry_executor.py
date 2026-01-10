"""
Retry execution orchestration with intelligent proxy selection.

Provides both synchronous and asynchronous retry execution:
- execute_with_retry: Synchronous execution with time.sleep
- execute_with_retry_async: Asynchronous execution with asyncio.sleep

The async variant avoids blocking the event loop during backoff delays.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from itertools import islice

import httpx
from loguru import logger

from proxywhirl.circuit_breaker import CircuitBreaker
from proxywhirl.exceptions import ProxyConnectionError
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

    Provides both synchronous and asynchronous execution methods:
    - execute_with_retry: Synchronous with time.sleep (for sync contexts)
    - execute_with_retry_async: Asynchronous with asyncio.sleep (for async contexts)

    The async variant avoids blocking the event loop during backoff delays.
    """

    def __init__(
        self,
        retry_policy: RetryPolicy,
        circuit_breakers: dict[str, CircuitBreaker],
        retry_metrics: RetryMetrics,
    ) -> None:
        """
        Initialize retry executor.

        Args:
            retry_policy: Retry configuration
            circuit_breakers: Circuit breakers by proxy ID
            retry_metrics: Metrics collection instance
        """
        self.retry_policy = retry_policy
        self.circuit_breakers = circuit_breakers
        self.retry_metrics = retry_metrics

    def execute_with_retry(
        self,
        request_fn: Callable[[], httpx.Response],
        proxy: Proxy,
        method: str,
        url: str,
        request_id: str | None = None,
    ) -> httpx.Response:
        """
        Execute a request with retry logic (SYNCHRONOUS).

        This method uses time.sleep for backoff delays and should only be called
        from synchronous contexts. For async execution, use
        AsyncProxyClient._execute_async_with_retry instead.

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
                return self._execute_single_attempt(request_fn, proxy, request_id, 0, 0.0)

        # Set up retry with tenacity
        last_exception: Exception | None = None
        start_time = time.time()
        previous_delay: float | None = None  # Track for decorrelated jitter

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
                        request_id,
                        attempt,
                        str(proxy.id),
                        RetryOutcome.TIMEOUT,
                        0.0,
                        0.0,
                        error_message="Total timeout exceeded",
                    )
                    raise ProxyConnectionError(f"Request timeout after {elapsed:.2f}s")

            # Calculate delay for this attempt using decorrelated jitter
            if attempt > 0:
                delay = self.retry_policy.calculate_delay(
                    attempt - 1, previous_delay=previous_delay
                )
                logger.info(
                    f"Retry attempt {attempt + 1}/{self.retry_policy.max_attempts} "
                    f"after {delay:.2f}s delay"
                )
                # SYNCHRONOUS sleep - this is intentional as RetryExecutor is sync-only.
                # For async contexts, use AsyncProxyClient._execute_async_with_retry
                # which uses asyncio.sleep instead.
                time.sleep(delay)
                previous_delay = delay  # Track for decorrelated jitter
            else:
                delay = 0.0
                previous_delay = None

            # Execute attempt
            attempt_start = time.time()
            try:
                response = request_fn()
                latency = time.time() - attempt_start

                # Check if status code is retryable
                if response.status_code in self.retry_policy.retry_status_codes:
                    logger.warning(
                        f"Received retryable status {response.status_code} from proxy {proxy.id}"
                    )
                    self._record_attempt(
                        request_id,
                        attempt,
                        str(proxy.id),
                        RetryOutcome.FAILURE,
                        delay,
                        latency,
                        error_message=f"Status {response.status_code}",
                    )
                    self._record_proxy_failure(proxy)
                    last_exception = ProxyConnectionError(f"Status code {response.status_code}")
                    continue

                # Success!
                self._record_attempt(
                    request_id,
                    attempt,
                    str(proxy.id),
                    RetryOutcome.SUCCESS,
                    delay,
                    latency,
                    status_code=response.status_code,
                )
                self._record_proxy_success(proxy)

                logger.info(f"Request succeeded on attempt {attempt + 1} using proxy {proxy.id}")
                return response

            except (httpx.ConnectError, httpx.TimeoutException) as e:
                latency = time.time() - attempt_start
                logger.warning(f"Connection error with proxy {proxy.id}: {e}")

                self._record_attempt(
                    request_id,
                    attempt,
                    str(proxy.id),
                    RetryOutcome.FAILURE,
                    delay,
                    latency,
                    error_message=str(e),
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
                        request_id,
                        attempt,
                        str(proxy.id),
                        RetryOutcome.FAILURE,
                        delay,
                        latency,
                        error_message=str(e),
                    )
                    self._record_proxy_failure(proxy)
                    last_exception = e
                    continue
                else:
                    logger.error(f"Non-retryable error: {e}")
                    self._record_attempt(
                        request_id,
                        attempt,
                        str(proxy.id),
                        RetryOutcome.FAILURE,
                        delay,
                        latency,
                        error_message=str(e),
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

    async def execute_with_retry_async(
        self,
        request_fn: Callable[[], Awaitable[httpx.Response]],
        proxy: Proxy,
        method: str,
        url: str,
        request_id: str | None = None,
    ) -> httpx.Response:
        """
        Execute a request with retry logic (ASYNCHRONOUS).

        This is the async variant of execute_with_retry that uses asyncio.sleep
        for non-blocking backoff delays instead of time.sleep.

        Args:
            request_fn: Async function that executes the request
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
                return await self._execute_single_attempt_async(
                    request_fn, proxy, request_id, 0, 0.0
                )

        # Set up retry with tenacity
        last_exception: Exception | None = None
        start_time = time.time()
        previous_delay: float | None = None  # Track for decorrelated jitter

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
                        request_id,
                        attempt,
                        str(proxy.id),
                        RetryOutcome.TIMEOUT,
                        0.0,
                        0.0,
                        error_message="Total timeout exceeded",
                    )
                    raise ProxyConnectionError(f"Request timeout after {elapsed:.2f}s")

            # Calculate delay for this attempt using decorrelated jitter
            if attempt > 0:
                delay = self.retry_policy.calculate_delay(
                    attempt - 1, previous_delay=previous_delay
                )
                logger.info(
                    f"Retry attempt {attempt + 1}/{self.retry_policy.max_attempts} "
                    f"after {delay:.2f}s delay"
                )
                # ASYNC sleep - non-blocking delay for event loop
                await asyncio.sleep(delay)
                previous_delay = delay  # Track for decorrelated jitter
            else:
                delay = 0.0
                previous_delay = None

            # Execute attempt
            attempt_start = time.time()
            try:
                response = await request_fn()
                latency = time.time() - attempt_start

                # Check if status code is retryable
                if response.status_code in self.retry_policy.retry_status_codes:
                    logger.warning(
                        f"Received retryable status {response.status_code} from proxy {proxy.id}"
                    )
                    self._record_attempt(
                        request_id,
                        attempt,
                        str(proxy.id),
                        RetryOutcome.FAILURE,
                        delay,
                        latency,
                        error_message=f"Status {response.status_code}",
                    )
                    self._record_proxy_failure(proxy)
                    last_exception = ProxyConnectionError(f"Status code {response.status_code}")
                    continue

                # Success!
                self._record_attempt(
                    request_id,
                    attempt,
                    str(proxy.id),
                    RetryOutcome.SUCCESS,
                    delay,
                    latency,
                    status_code=response.status_code,
                )
                self._record_proxy_success(proxy)

                logger.info(f"Request succeeded on attempt {attempt + 1} using proxy {proxy.id}")
                return response

            except (httpx.ConnectError, httpx.TimeoutException) as e:
                latency = time.time() - attempt_start
                logger.warning(f"Connection error with proxy {proxy.id}: {e}")

                self._record_attempt(
                    request_id,
                    attempt,
                    str(proxy.id),
                    RetryOutcome.FAILURE,
                    delay,
                    latency,
                    error_message=str(e),
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
                        request_id,
                        attempt,
                        str(proxy.id),
                        RetryOutcome.FAILURE,
                        delay,
                        latency,
                        error_message=str(e),
                    )
                    self._record_proxy_failure(proxy)
                    last_exception = e
                    continue
                else:
                    logger.error(f"Non-retryable error: {e}")
                    self._record_attempt(
                        request_id,
                        attempt,
                        str(proxy.id),
                        RetryOutcome.FAILURE,
                        delay,
                        latency,
                        error_message=str(e),
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
                request_id,
                attempt,
                str(proxy.id),
                RetryOutcome.SUCCESS,
                delay,
                latency,
                status_code=response.status_code,
            )
            self._record_proxy_success(proxy)
            return response

        except Exception as e:
            latency = time.time() - attempt_start
            self._record_attempt(
                request_id,
                attempt,
                str(proxy.id),
                RetryOutcome.FAILURE,
                delay,
                latency,
                error_message=str(e),
            )
            self._record_proxy_failure(proxy)
            raise

    async def _execute_single_attempt_async(
        self,
        request_fn: Callable[[], Awaitable[httpx.Response]],
        proxy: Proxy,
        request_id: str,
        attempt: int,
        delay: float,
    ) -> httpx.Response:
        """Execute a single async request attempt without retry."""
        attempt_start = time.time()
        try:
            response = await request_fn()
            latency = time.time() - attempt_start

            self._record_attempt(
                request_id,
                attempt,
                str(proxy.id),
                RetryOutcome.SUCCESS,
                delay,
                latency,
                status_code=response.status_code,
            )
            self._record_proxy_success(proxy)
            return response

        except Exception as e:
            latency = time.time() - attempt_start
            self._record_attempt(
                request_id,
                attempt,
                str(proxy.id),
                RetryOutcome.FAILURE,
                delay,
                latency,
                error_message=str(e),
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
        status_code: int | None = None,
        error_message: str | None = None,
    ) -> None:
        """Record a retry attempt in metrics."""
        attempt = RetryAttempt(
            request_id=request_id,
            attempt_number=attempt_number,
            proxy_id=proxy_id,
            timestamp=datetime.now(timezone.utc),
            outcome=outcome,
            status_code=status_code,
            delay_before=delay_before,
            latency=latency,
            error_message=error_message,
        )
        self.retry_metrics.record_attempt(attempt)

    def _record_proxy_failure(self, proxy: Proxy) -> None:
        """Record a proxy failure in circuit breaker."""
        circuit_breaker = self.circuit_breakers.get(str(proxy.id))
        if circuit_breaker:
            old_state = circuit_breaker.state
            circuit_breaker.record_failure()
            new_state = circuit_breaker.state

            # Record state change if it occurred
            if old_state != new_state:
                event = CircuitBreakerEvent(
                    proxy_id=str(proxy.id),
                    from_state=old_state,
                    to_state=new_state,
                    timestamp=datetime.now(timezone.utc),
                    failure_count=circuit_breaker.failure_count,
                )
                self.retry_metrics.record_circuit_breaker_event(event)
                logger.warning(
                    f"Circuit breaker for proxy {proxy.id} transitioned "
                    f"from {old_state.value} to {new_state.value}"
                )

    def _record_proxy_success(self, proxy: Proxy) -> None:
        """Record a proxy success in circuit breaker."""
        circuit_breaker = self.circuit_breakers.get(str(proxy.id))
        if circuit_breaker:
            old_state = circuit_breaker.state
            circuit_breaker.record_success()
            new_state = circuit_breaker.state

            # Record state change if it occurred
            if old_state != new_state:
                event = CircuitBreakerEvent(
                    proxy_id=str(proxy.id),
                    from_state=old_state,
                    to_state=new_state,
                    timestamp=datetime.now(timezone.utc),
                    failure_count=circuit_breaker.failure_count,
                )
                self.retry_metrics.record_circuit_breaker_event(event)
                logger.info(
                    f"Circuit breaker for proxy {proxy.id} transitioned "
                    f"from {old_state.value} to {new_state.value}"
                )

    def select_retry_proxy(
        self,
        available_proxies: list[Proxy],
        failed_proxy: Proxy,
        target_region: str | None = None,
    ) -> Proxy | None:
        """
        Select best proxy for retry based on performance metrics.

        Uses a weighted scoring formula:
        score = (0.7 ? success_rate) + (0.3 ? (1 - normalized_latency))

        Args:
            available_proxies: List of available proxies
            failed_proxy: The proxy that just failed
            target_region: Optional target region for geo-targeted selection

        Returns:
            Best proxy for retry, or None if no suitable proxy found
        """
        # Filter out failed proxy and check circuit breakers
        candidates = []
        for proxy in available_proxies:
            if proxy.id == failed_proxy.id:
                continue

            circuit_breaker = self.circuit_breakers.get(str(proxy.id))
            if circuit_breaker and not circuit_breaker.should_attempt_request():
                continue

            candidates.append(proxy)

        if not candidates:
            return None

        # Calculate performance scores for candidates
        scored_candidates = []
        for proxy in candidates:
            score = self._calculate_proxy_score(proxy, target_region)
            scored_candidates.append((proxy, score))

        # Sort by score (highest first)
        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        # Return proxy with highest score
        return scored_candidates[0][0]

    def _calculate_proxy_score(
        self,
        proxy: Proxy,
        target_region: str | None = None,
    ) -> float:
        """
        Calculate performance score for a proxy.

        Formula: score = (0.7 ? success_rate) + (0.3 ? (1 - normalized_latency))

        Args:
            proxy: Proxy to score
            target_region: Optional target region for geo-targeting

        Returns:
            Performance score (0.0 to 1.0, higher is better)
        """
        # Get success rate from proxy metrics
        total_requests = proxy.total_requests
        # No history - give neutral score
        success_rate = 0.5 if total_requests == 0 else proxy.success_rate

        # Get average latency from recent attempts
        avg_latency = self._get_proxy_avg_latency(str(proxy.id))

        # Normalize latency (assuming max latency of 10 seconds)
        max_latency = 10.0
        normalized_latency = min(avg_latency / max_latency, 1.0) if avg_latency > 0 else 0.0

        # Calculate base score
        base_score = (0.7 * success_rate) + (0.3 * (1.0 - normalized_latency))

        # Apply geo-targeting bonus if region matches
        if target_region and proxy.metadata:
            proxy_region = proxy.metadata.get("region")
            if proxy_region == target_region:
                # 10% bonus for matching region
                base_score = min(base_score * 1.1, 1.0)

        return base_score

    def _get_proxy_avg_latency(self, proxy_id: str) -> float:
        """
        Get average latency for a proxy from recent attempts.

        Args:
            proxy_id: Proxy ID to get latency for

        Returns:
            Average latency in seconds (last 100 attempts)
        """
        # Get last 100 attempts efficiently using islice (O(100) instead of O(n))
        deque_len = len(self.retry_metrics.current_attempts)
        start_idx = max(0, deque_len - 100)

        # Use islice to get last 100 elements without converting entire deque to list
        recent_attempts = [
            attempt
            for attempt in islice(self.retry_metrics.current_attempts, start_idx, None)
            if attempt.proxy_id == proxy_id and attempt.outcome == RetryOutcome.SUCCESS
        ]

        if not recent_attempts:
            return 0.0

        total_latency = sum(attempt.latency for attempt in recent_attempts)
        return total_latency / len(recent_attempts)
