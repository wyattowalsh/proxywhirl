"""
Retry execution orchestration with intelligent proxy selection.

Inner request retries use :mod:`tenacity` ``Retrying`` / ``AsyncRetrying`` with
``RetryPolicy``-driven backoff, circuit-breaker hooks, and per-attempt metrics.

Provides both synchronous and asynchronous retry execution:
- execute_with_retry: Synchronous execution with time.sleep
- execute_with_retry_async: Asynchronous execution with asyncio.sleep

The async variant avoids blocking the event loop during backoff delays.
"""

from __future__ import annotations

import asyncio
import random
import time
import uuid
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from itertools import islice
from typing import Any, NoReturn

import httpx
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, field_validator
from tenacity import (
    AsyncRetrying,
    RetryCallState,
    Retrying,
    retry_if_exception,
    stop_after_attempt,
)

from proxywhirl.circuit_breaker import CircuitBreaker, CircuitBreakerState
from proxywhirl.exceptions import ProxyConnectionError
from proxywhirl.models import Proxy


class BackoffStrategy(str, Enum):
    """Retry backoff timing strategy."""

    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIXED = "fixed"


class RetryPolicy(BaseModel):
    """Configuration for retry behavior."""

    max_attempts: int = Field(default=3, ge=1, le=10)
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL
    base_delay: float = Field(default=1.0, gt=0, le=60)
    multiplier: float = Field(default=2.0, gt=1, le=10)
    max_backoff_delay: float = Field(default=30.0, gt=0, le=300)
    jitter: bool = Field(default=False)
    retry_status_codes: list[int] = Field(default=[502, 503, 504])
    timeout: float | None = Field(default=None, gt=0)
    retry_non_idempotent: bool = Field(default=False)

    @field_validator("retry_status_codes")
    @classmethod
    def validate_status_codes(cls, v: list[int]) -> list[int]:
        """Validate that status codes are 5xx errors."""
        if not all(500 <= code < 600 for code in v):
            raise ValueError("Status codes must be 5xx errors")
        return v

    def calculate_delay(self, attempt: int, previous_delay: float | None = None) -> float:
        """Calculate delay for given attempt number (0-indexed)."""
        if self.backoff_strategy == BackoffStrategy.EXPONENTIAL:
            base = self.base_delay * (self.multiplier**attempt)
        elif self.backoff_strategy == BackoffStrategy.LINEAR:
            base = self.base_delay * (attempt + 1)
        else:
            base = self.base_delay

        if self.jitter:
            if previous_delay is not None:
                # Non-cryptographic randomness is sufficient for retry jitter.
                retry_jitter = random.uniform(  # nosec B311
                    self.base_delay,
                    previous_delay * 3,
                )
                delay = min(self.max_backoff_delay, retry_jitter)
            else:
                jitter_cap = min(base, self.max_backoff_delay)
                # Non-cryptographic randomness is sufficient for retry jitter.
                delay = random.uniform(  # nosec B311
                    0,
                    jitter_cap,
                )
        else:
            delay = min(base, self.max_backoff_delay)

        return delay


class RetryOutcome(str, Enum):
    """Outcome of a retry attempt."""

    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    CIRCUIT_OPEN = "circuit_open"


class RetryAttempt(BaseModel):
    """Record of a single retry attempt."""

    request_id: str
    attempt_number: int = Field(ge=0)
    proxy_id: str
    timestamp: datetime
    outcome: RetryOutcome
    status_code: int | None = None
    delay_before: float = Field(ge=0)
    latency: float = Field(ge=0)
    error_message: str | None = None
    failover_round: int = Field(default=0, ge=0)


class CircuitBreakerEvent(BaseModel):
    """Circuit breaker state change event."""

    proxy_id: str
    from_state: CircuitBreakerState
    to_state: CircuitBreakerState
    timestamp: datetime
    failure_count: int


class HourlyAggregate(BaseModel):
    """Hourly aggregated metrics."""

    hour: datetime
    total_requests: int = 0
    total_retries: int = 0
    success_by_attempt: dict[int, int] = Field(default_factory=dict)
    failure_by_reason: dict[str, int] = Field(default_factory=dict)
    avg_latency: float = 0.0


class RetryMetrics(BaseModel):
    """Aggregated retry metrics collection."""

    current_attempts: deque[RetryAttempt] = Field(default_factory=deque)
    hourly_aggregates: dict[datetime, HourlyAggregate] = Field(default_factory=dict)
    circuit_breaker_events: list[CircuitBreakerEvent] = Field(default_factory=list)
    retention_hours: int = Field(default=24)
    max_current_attempts: int = Field(default=10000)

    _lock: Any = PrivateAttr(default_factory=__import__("threading").Lock)
    _hourly_request_ids: dict[datetime, set[str]] = PrivateAttr(default_factory=dict)
    _proxy_hourly_aggregates: dict[datetime, dict[str, dict[str, Any]]] = PrivateAttr(
        default_factory=dict
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data):
        """Initialize with maxlen-bounded deque."""
        super().__init__(**data)
        max_attempts = data.get("max_current_attempts", 10000)
        self.current_attempts = deque(self.current_attempts, maxlen=max_attempts)
        existing_attempts = list(self.current_attempts)
        self.hourly_aggregates = {}
        self._hourly_request_ids = {}
        self._proxy_hourly_aggregates = {}
        for attempt in existing_attempts:
            self._record_attempt_aggregate(attempt)
        self._prune_aggregates()

    def record_attempt(self, attempt: RetryAttempt) -> None:
        """Record a retry attempt."""
        with self._lock:
            self.current_attempts.append(attempt)
            self._record_attempt_aggregate(attempt)
            self._prune_aggregates()

    def record_circuit_breaker_event(self, event: CircuitBreakerEvent) -> None:
        """Record circuit breaker state change."""
        with self._lock:
            self.circuit_breaker_events.append(event)
            if len(self.circuit_breaker_events) > 1000:
                self.circuit_breaker_events = self.circuit_breaker_events[-1000:]

    def aggregate_hourly(self) -> None:
        """Prune retained hourly summaries.

        Attempts are folded into hourly aggregates when recorded. This maintenance
        method is intentionally idempotent so periodic callers do not inflate counts.
        """
        with self._lock:
            self._prune_aggregates()

    def get_summary(self) -> dict[str, Any]:
        """Get metrics summary for API response."""
        with self._lock:
            self._prune_aggregates()
            total_retries = sum(agg.total_retries for agg in self.hourly_aggregates.values())

            success_by_attempt: dict[int, int] = defaultdict(int)
            for agg in self.hourly_aggregates.values():
                for attempt_num, count in agg.success_by_attempt.items():
                    success_by_attempt[attempt_num] += count

            return {
                "total_retries": total_retries,
                "success_by_attempt": dict(success_by_attempt),
                "circuit_breaker_events_count": len(self.circuit_breaker_events),
                "retention_hours": self.retention_hours,
            }

    def get_timeseries(self, hours: int = 24) -> list[dict[str, Any]]:
        """Get time-series data for the specified hours."""
        with self._lock:
            self._prune_aggregates()
            cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

            data_points = []
            for hour, agg in sorted(self.hourly_aggregates.items()):
                if hour >= cutoff:
                    success_count = sum(agg.success_by_attempt.values())
                    total_attempts = agg.total_retries
                    success_rate = success_count / total_attempts if total_attempts > 0 else 0.0

                    data_points.append(
                        {
                            "timestamp": hour.isoformat(),
                            "total_requests": agg.total_requests,
                            "total_retries": agg.total_retries,
                            "success_rate": success_rate,
                            "avg_latency": agg.avg_latency,
                        }
                    )

            return data_points

    def get_by_proxy(self, hours: int = 24) -> dict[str, dict[str, Any]]:
        """Get per-proxy retry statistics."""
        with self._lock:
            self._prune_aggregates()
            cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
            proxy_stats: dict[str, dict[str, Any]] = defaultdict(
                lambda: {
                    "total_attempts": 0,
                    "success_count": 0,
                    "failure_count": 0,
                    "total_latency": 0.0,
                    "circuit_breaker_opens": 0,
                }
            )

            for hour, per_proxy in self._proxy_hourly_aggregates.items():
                if hour < cutoff:
                    continue
                for proxy_id, retained_stats in per_proxy.items():
                    stats = proxy_stats[proxy_id]
                    stats["total_attempts"] += retained_stats["total_attempts"]
                    stats["success_count"] += retained_stats["success_count"]
                    stats["failure_count"] += retained_stats["failure_count"]
                    stats["total_latency"] += retained_stats["total_latency"]

            for event in self.circuit_breaker_events:
                if event.timestamp >= cutoff and event.to_state == CircuitBreakerState.OPEN:
                    proxy_stats[event.proxy_id]["circuit_breaker_opens"] += 1

            result = {}
            for proxy_id, stats in proxy_stats.items():
                avg_latency = (
                    stats["total_latency"] / stats["total_attempts"]
                    if stats["total_attempts"] > 0
                    else 0.0
                )
                result[proxy_id] = {
                    "proxy_id": proxy_id,
                    "total_attempts": stats["total_attempts"],
                    "success_count": stats["success_count"],
                    "failure_count": stats["failure_count"],
                    "avg_latency": avg_latency,
                    "circuit_breaker_opens": stats["circuit_breaker_opens"],
                }

            return result

    def _record_attempt_aggregate(self, attempt: RetryAttempt) -> None:
        """Fold one attempt into retained hourly and per-proxy aggregates."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self.retention_hours)
        if attempt.timestamp < cutoff:
            return

        hour = attempt.timestamp.replace(minute=0, second=0, microsecond=0)
        agg = self.hourly_aggregates.setdefault(hour, HourlyAggregate(hour=hour))
        request_ids = self._hourly_request_ids.setdefault(hour, set())

        if attempt.request_id not in request_ids:
            request_ids.add(attempt.request_id)
            agg.total_requests += 1

        previous_total = agg.total_retries
        agg.total_retries += 1
        agg.avg_latency = ((agg.avg_latency * previous_total) + attempt.latency) / agg.total_retries

        if attempt.outcome == RetryOutcome.SUCCESS:
            agg.success_by_attempt[attempt.attempt_number] = (
                agg.success_by_attempt.get(attempt.attempt_number, 0) + 1
            )
        else:
            reason = attempt.error_message or attempt.outcome.value
            agg.failure_by_reason[reason] = agg.failure_by_reason.get(reason, 0) + 1

        per_proxy = self._proxy_hourly_aggregates.setdefault(hour, {})
        proxy_stats = per_proxy.setdefault(
            attempt.proxy_id,
            {
                "total_attempts": 0,
                "success_count": 0,
                "failure_count": 0,
                "total_latency": 0.0,
            },
        )
        proxy_stats["total_attempts"] += 1
        proxy_stats["total_latency"] += attempt.latency
        if attempt.outcome == RetryOutcome.SUCCESS:
            proxy_stats["success_count"] += 1
        else:
            proxy_stats["failure_count"] += 1

    def _prune_aggregates(self) -> None:
        """Drop retained aggregates outside the configured retention window."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self.retention_hours)
        self.hourly_aggregates = {
            hour: agg for hour, agg in self.hourly_aggregates.items() if hour >= cutoff
        }
        self._hourly_request_ids = {
            hour: request_ids
            for hour, request_ids in self._hourly_request_ids.items()
            if hour >= cutoff
        }
        self._proxy_hourly_aggregates = {
            hour: per_proxy
            for hour, per_proxy in self._proxy_hourly_aggregates.items()
            if hour >= cutoff
        }


class RetryableError(Exception):
    """Exception that triggers a retry."""

    pass


class NonRetryableError(Exception):
    """Exception that does not trigger a retry."""

    pass


@dataclass
class _RetryRunContext:
    """Mutable per-request state shared across tenacity attempts."""

    request_id: str
    proxy: Proxy
    failover_round: int
    start_time: float
    previous_delay: float | None = None
    last_exception: Exception | None = None


def _make_retry_predicate(executor: RetryExecutor) -> Any:
    """Build tenacity retry predicate honoring proxy-specific retry rules."""

    def _should_retry(exc: BaseException) -> bool:
        if isinstance(exc, (NonRetryableError, ProxyConnectionError)):
            return False
        if isinstance(exc, RetryableError):
            return True
        return executor._is_retryable_error(exc)

    return retry_if_exception(_should_retry)


def _make_wait(policy: RetryPolicy, ctx: _RetryRunContext) -> Callable[[RetryCallState], float]:
    """Map RetryPolicy backoff to tenacity wait_custom."""

    def _wait(retry_state: RetryCallState) -> float:
        delay = policy.calculate_delay(
            retry_state.attempt_number - 1,
            previous_delay=ctx.previous_delay,
        )
        ctx.previous_delay = delay
        return delay

    return _wait


def _make_before_sleep(
    policy: RetryPolicy, ctx: _RetryRunContext
) -> Callable[[RetryCallState], None]:
    """Log upcoming retry attempt before tenacity sleeps."""

    def _before_sleep(retry_state: RetryCallState) -> None:
        delay = ctx.previous_delay or 0.0
        logger.info(
            f"Retry attempt {retry_state.attempt_number + 1}/{policy.max_attempts} "
            f"after {delay:.2f}s delay"
        )

    return _before_sleep


def _make_retry_error_callback(
    policy: RetryPolicy, ctx: _RetryRunContext
) -> Callable[[RetryCallState], None]:
    """Translate exhausted tenacity retries into ProxyConnectionError."""

    def _on_exhausted(retry_state: RetryCallState) -> None:
        del retry_state
        logger.error(
            f"All {policy.max_attempts} retry attempts exhausted for request {ctx.request_id}"
        )
        if ctx.last_exception:
            raise ProxyConnectionError(
                f"Request failed after {policy.max_attempts} attempts"
            ) from ctx.last_exception
        raise ProxyConnectionError(f"Request failed after {policy.max_attempts} attempts")

    return _on_exhausted


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
        failover_round: int = 0,
    ) -> httpx.Response:
        """
        Execute a request with retry logic (SYNCHRONOUS).

        This method uses time.sleep for backoff delays and should only be called
        from synchronous contexts. For async execution, use
        execute_with_retry_async instead.

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
                    request_fn, proxy, request_id, 0, 0.0, failover_round=failover_round
                )

        ctx = _RetryRunContext(
            request_id=request_id,
            proxy=proxy,
            failover_round=failover_round,
            start_time=time.time(),
        )
        retrying = Retrying(
            stop=stop_after_attempt(self.retry_policy.max_attempts),
            wait=_make_wait(self.retry_policy, ctx),
            retry=_make_retry_predicate(self),
            before_sleep=_make_before_sleep(self.retry_policy, ctx),
            retry_error_callback=_make_retry_error_callback(self.retry_policy, ctx),
            reraise=False,
            sleep=time.sleep,
        )

        for attempt in retrying:
            with attempt:
                attempt_index = attempt.retry_state.attempt_number - 1
                delay_before = 0.0 if attempt_index == 0 else (ctx.previous_delay or 0.0)
                return self._run_one_attempt(
                    request_fn,
                    proxy,
                    request_id,
                    attempt_index,
                    delay_before,
                    ctx,
                )

        raise AssertionError("tenacity retry_error_callback must raise")

    async def execute_with_retry_async(
        self,
        request_fn: Callable[[], Awaitable[httpx.Response]],
        proxy: Proxy,
        method: str,
        url: str,
        request_id: str | None = None,
        failover_round: int = 0,
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
                    request_fn,
                    proxy,
                    request_id,
                    0,
                    0.0,
                    failover_round=failover_round,
                )

        ctx = _RetryRunContext(
            request_id=request_id,
            proxy=proxy,
            failover_round=failover_round,
            start_time=time.time(),
        )
        retrying = AsyncRetrying(
            stop=stop_after_attempt(self.retry_policy.max_attempts),
            wait=_make_wait(self.retry_policy, ctx),
            retry=_make_retry_predicate(self),
            before_sleep=_make_before_sleep(self.retry_policy, ctx),
            retry_error_callback=_make_retry_error_callback(self.retry_policy, ctx),
            reraise=False,
            sleep=asyncio.sleep,
        )

        async for attempt in retrying:
            with attempt:
                attempt_index = attempt.retry_state.attempt_number - 1
                delay_before = 0.0 if attempt_index == 0 else (ctx.previous_delay or 0.0)
                return await self._run_one_attempt_async(
                    request_fn,
                    proxy,
                    request_id,
                    attempt_index,
                    delay_before,
                    ctx,
                )

        raise AssertionError("tenacity retry_error_callback must raise")

    def _check_attempt_timeout(
        self,
        request_id: str,
        attempt: int,
        proxy: Proxy,
        ctx: _RetryRunContext,
    ) -> None:
        """Raise ProxyConnectionError when the total retry timeout is exceeded."""
        if not self.retry_policy.timeout:
            return

        elapsed = time.time() - ctx.start_time
        if elapsed >= self.retry_policy.timeout:
            logger.warning(
                f"Request timeout exceeded ({self.retry_policy.timeout}s) after {attempt} attempts"
            )
            self._record_attempt(
                request_id,
                attempt,
                str(proxy.id),
                RetryOutcome.TIMEOUT,
                0.0,
                0.0,
                error_message="Total timeout exceeded",
                failover_round=ctx.failover_round,
            )
            raise ProxyConnectionError(f"Request timeout after {elapsed:.2f}s")

    def _evaluate_response_for_retry(
        self,
        response: httpx.Response,
        request_id: str,
        attempt: int,
        proxy: Proxy,
        delay_before: float,
        latency: float,
        ctx: _RetryRunContext,
    ) -> httpx.Response:
        """Record success or raise RetryableError for retryable HTTP status codes."""
        if response.status_code in self.retry_policy.retry_status_codes:
            logger.warning(
                f"Received retryable status {response.status_code} from proxy {proxy.id}"
            )
            self._record_attempt(
                request_id,
                attempt,
                str(proxy.id),
                RetryOutcome.FAILURE,
                delay_before,
                latency,
                error_message=f"Status {response.status_code}",
                failover_round=ctx.failover_round,
            )
            self._record_proxy_failure(proxy)
            ctx.last_exception = ProxyConnectionError(f"Status code {response.status_code}")
            raise RetryableError(f"Status {response.status_code}")

        self._record_attempt(
            request_id,
            attempt,
            str(proxy.id),
            RetryOutcome.SUCCESS,
            delay_before,
            latency,
            status_code=response.status_code,
            failover_round=ctx.failover_round,
        )
        self._record_proxy_success(proxy)
        logger.info(f"Request succeeded on attempt {attempt + 1} using proxy {proxy.id}")
        return response

    def _handle_attempt_error(
        self,
        error: Exception,
        request_id: str,
        attempt: int,
        proxy: Proxy,
        delay_before: float,
        attempt_start: float,
        ctx: _RetryRunContext,
    ) -> NoReturn:
        """Record attempt failure and re-raise or wrap for tenacity."""
        latency = time.time() - attempt_start

        if isinstance(error, (httpx.ConnectError, httpx.TimeoutException)):
            logger.warning(f"Connection error with proxy {proxy.id}: {error}")
            self._record_attempt(
                request_id,
                attempt,
                str(proxy.id),
                RetryOutcome.FAILURE,
                delay_before,
                latency,
                error_message=str(error),
                failover_round=ctx.failover_round,
            )
            self._record_proxy_failure(proxy)
            ctx.last_exception = error
            raise error

        if self._is_retryable_error(error):
            logger.warning(f"Retryable error with proxy {proxy.id}: {error}")
            self._record_attempt(
                request_id,
                attempt,
                str(proxy.id),
                RetryOutcome.FAILURE,
                delay_before,
                latency,
                error_message=str(error),
                failover_round=ctx.failover_round,
            )
            self._record_proxy_failure(proxy)
            ctx.last_exception = error
            raise error

        logger.error(f"Non-retryable error: {error}")
        self._record_attempt(
            request_id,
            attempt,
            str(proxy.id),
            RetryOutcome.FAILURE,
            delay_before,
            latency,
            error_message=str(error),
            failover_round=ctx.failover_round,
        )
        raise NonRetryableError(str(error)) from error

    def _run_one_attempt(
        self,
        request_fn: Callable[[], httpx.Response],
        proxy: Proxy,
        request_id: str,
        attempt: int,
        delay_before: float,
        ctx: _RetryRunContext,
    ) -> httpx.Response:
        """Execute one synchronous attempt; raise RetryableError to trigger tenacity retry."""
        self._check_attempt_timeout(request_id, attempt, proxy, ctx)

        attempt_start = time.time()
        try:
            response = request_fn()
            latency = time.time() - attempt_start
            return self._evaluate_response_for_retry(
                response,
                request_id,
                attempt,
                proxy,
                delay_before,
                latency,
                ctx,
            )
        except (NonRetryableError, RetryableError):
            raise
        except Exception as e:
            self._handle_attempt_error(
                e,
                request_id,
                attempt,
                proxy,
                delay_before,
                attempt_start,
                ctx,
            )

    async def _run_one_attempt_async(
        self,
        request_fn: Callable[[], Awaitable[httpx.Response]],
        proxy: Proxy,
        request_id: str,
        attempt: int,
        delay_before: float,
        ctx: _RetryRunContext,
    ) -> httpx.Response:
        """Execute one asynchronous attempt; raise RetryableError to trigger tenacity retry."""
        self._check_attempt_timeout(request_id, attempt, proxy, ctx)

        attempt_start = time.time()
        try:
            response = await request_fn()
            latency = time.time() - attempt_start
            return self._evaluate_response_for_retry(
                response,
                request_id,
                attempt,
                proxy,
                delay_before,
                latency,
                ctx,
            )
        except (NonRetryableError, RetryableError):
            raise
        except Exception as e:
            self._handle_attempt_error(
                e,
                request_id,
                attempt,
                proxy,
                delay_before,
                attempt_start,
                ctx,
            )

    def _execute_single_attempt(
        self,
        request_fn: Callable[[], httpx.Response],
        proxy: Proxy,
        request_id: str,
        attempt: int,
        delay: float,
        *,
        failover_round: int = 0,
    ) -> httpx.Response:
        """Execute a single request attempt without retry."""
        attempt_start = time.time()
        try:
            response = request_fn()
            latency = time.time() - attempt_start

            if response.status_code in self.retry_policy.retry_status_codes:
                self._record_attempt(
                    request_id,
                    attempt,
                    str(proxy.id),
                    RetryOutcome.FAILURE,
                    delay,
                    latency,
                    status_code=response.status_code,
                    error_message=f"Status {response.status_code}",
                    failover_round=failover_round,
                )
                self._record_proxy_failure(proxy)
                return response

            self._record_attempt(
                request_id,
                attempt,
                str(proxy.id),
                RetryOutcome.SUCCESS,
                delay,
                latency,
                status_code=response.status_code,
                failover_round=failover_round,
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
                failover_round=failover_round,
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
        *,
        failover_round: int = 0,
    ) -> httpx.Response:
        """Execute a single async request attempt without retry."""
        attempt_start = time.time()
        try:
            response = await request_fn()
            latency = time.time() - attempt_start

            if response.status_code in self.retry_policy.retry_status_codes:
                self._record_attempt(
                    request_id,
                    attempt,
                    str(proxy.id),
                    RetryOutcome.FAILURE,
                    delay,
                    latency,
                    status_code=response.status_code,
                    error_message=f"Status {response.status_code}",
                    failover_round=failover_round,
                )
                self._record_proxy_failure(proxy)
                return response

            self._record_attempt(
                request_id,
                attempt,
                str(proxy.id),
                RetryOutcome.SUCCESS,
                delay,
                latency,
                status_code=response.status_code,
                failover_round=failover_round,
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
                failover_round=failover_round,
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
        failover_round: int = 0,
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
            failover_round=failover_round,
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
