"""proxywhirl/validator.py -- proxy validation functionality"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional, TypeVar

import httpx
from loguru import logger

from proxywhirl.models import AnonymityLevel, Proxy, ProxyError, ValidationErrorType

T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, requests blocked
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerOpenError(ProxyError):
    """Raised when circuit breaker is open."""

    pass


class CircuitBreaker:
    """
    Circuit breaker implementation for proxy operations.

    Prevents cascading failures by temporarily blocking requests
    to failing services and allowing them time to recover.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type[Exception] | tuple[type[Exception], ...] = Exception,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        # State management
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._lock = asyncio.Lock()

    @property
    def state(self) -> CircuitState:
        """Get current circuit breaker state."""
        return self._state

    @property
    def failure_count(self) -> int:
        """Get current failure count."""
        return self._failure_count

    async def call(self, func: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any) -> T:
        """
        Execute function through circuit breaker.

        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerOpenError: When circuit is open
            Exception: Original exception from function
        """
        async with self._lock:
            # Check if we should transition from OPEN to HALF_OPEN
            if (
                self._state == CircuitState.OPEN
                and self._last_failure_time
                and time.time() - self._last_failure_time > self.recovery_timeout
            ):
                self._state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker transitioning to HALF_OPEN")

            # Block requests when circuit is OPEN
            if self._state == CircuitState.OPEN:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is OPEN. "
                    f"Failed {self._failure_count} times. "
                    f"Try again in {self.recovery_timeout}s"
                )

        # Execute the function
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except self.expected_exception as e:
            await self._on_failure()
            raise e

    async def _on_success(self) -> None:
        """Handle successful function execution."""
        async with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                logger.info("Circuit breaker transitioning to CLOSED after success")
                self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._last_failure_time = None

    async def _on_failure(self) -> None:
        """Handle failed function execution."""
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()

            if self._failure_count >= self.failure_threshold:
                if self._state != CircuitState.OPEN:
                    logger.warning(f"Circuit breaker OPENING after {self._failure_count} failures")
                    self._state = CircuitState.OPEN

    async def reset(self) -> None:
        """Manually reset circuit breaker to CLOSED state."""
        async with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._last_failure_time = None
            logger.info("Circuit breaker manually reset to CLOSED")


@dataclass
class ValidationResult:
    """Comprehensive validation result with metrics and error details."""

    proxy: Proxy
    is_valid: bool
    response_time: Optional[float] = None
    error_type: Optional[ValidationErrorType] = None
    error_message: Optional[str] = None
    status_code: Optional[int] = None
    test_url: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    response_headers: Optional[Dict[str, str]] = field(default_factory=dict)
    ip_detected: Optional[str] = None
    anonymity_detected: Optional[AnonymityLevel] = None

    @property
    def health_score(self) -> float:
        """Calculate a health score based on validation results."""
        if not self.is_valid:
            return 0.0

        score = 1.0

        # Penalize based on response time
        if self.response_time:
            if self.response_time > 10.0:
                score *= 0.5
            elif self.response_time > 5.0:
                score *= 0.8
            elif self.response_time < 1.0:
                score *= 1.1  # Bonus for fast proxies

        # Bonus for detecting anonymity level
        if self.anonymity_detected == AnonymityLevel.ELITE:
            score *= 1.2
        elif self.anonymity_detected == AnonymityLevel.ANONYMOUS:
            score *= 1.1
        elif self.anonymity_detected == AnonymityLevel.TRANSPARENT:
            score *= 0.8

        return min(score, 1.0)


@dataclass
class ValidationSummary:
    """Summary of validation results across multiple proxies."""

    total_proxies: int
    valid_proxy_results: List[ValidationResult]
    failed_proxy_results: List[ValidationResult]
    avg_response_time: Optional[float] = None
    min_response_time: Optional[float] = None
    max_response_time: Optional[float] = None
    success_rate: float = 0.0
    error_breakdown: Dict[ValidationErrorType, int] = field(default_factory=dict)
    validation_duration: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def valid_proxies(self) -> List[Proxy]:
        """Get list of valid proxy objects."""
        return [result.proxy for result in self.valid_proxy_results]

    @property
    def valid_proxy_count(self) -> int:
        """Get count of valid proxies."""
        return len(self.valid_proxy_results)

    @property
    def failed_proxy_count(self) -> int:
        """Get count of failed proxies."""
        return len(self.failed_proxy_results)

    @property
    def quality_tier(self) -> str:
        """Determine quality tier based on success rate."""
        if self.success_rate >= 0.9:
            return "Premium"
        elif self.success_rate >= 0.7:
            return "Standard"
        elif self.success_rate >= 0.5:
            return "Basic"
        else:
            return "Poor"


class ProxyValidator:
    """Enhanced proxy validator with comprehensive metrics and error handling."""

    def __init__(
        self,
        timeout: float = 10.0,
        test_urls: Optional[List[str]] = None,
        # Back-compat alias accepted by tests
        test_url: Optional[str] = None,
        max_concurrent: int = 10,
        circuit_breaker_threshold: int = 10,
        retry_attempts: int = 2,
        enable_anonymity_detection: bool = True,
        enable_geolocation_detection: bool = True,
    ):
        self.timeout = timeout
        # Normalize test URLs with alias support
        if test_url and not test_urls:
            test_urls = [test_url]
        self.test_urls = test_urls or [
            "https://httpbin.org/ip",
            "https://ifconfig.me/ip",
            "https://api.ipify.org?format=json",
        ]
        self.primary_test_url = self.test_urls[0]
        self.retry_attempts = retry_attempts
        self.enable_anonymity_detection = enable_anonymity_detection
        self.enable_geolocation_detection = enable_geolocation_detection

        # Concurrency control
        self.semaphore = asyncio.Semaphore(max_concurrent)

        # Circuit breaker for validation endpoints
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=circuit_breaker_threshold,
            recovery_timeout=30.0,
            expected_exception=(httpx.HTTPError, asyncio.TimeoutError),
        )

        # Validation metrics
        self._total_validations = 0
        self._successful_validations = 0
        self._validation_history: List[ValidationResult] = []

        logger.info(
            "Enhanced ProxyValidator initialized with %d test URLs",
            len(self.test_urls),
        )

    # Back-compat convenience property expected by tests
    @property
    def test_url(self) -> str:
        return self.primary_test_url

    @test_url.setter
    def test_url(self, value: str) -> None:
        # Update both primary and list to keep consistency
        self.primary_test_url = value
        if self.test_urls:
            self.test_urls[0] = value
        else:
            self.test_urls = [value]

    async def validate_proxy(self, proxy: Proxy) -> ValidationResult:
        """Validate a single proxy with comprehensive error handling and metrics."""
        async with self.semaphore:
            self._total_validations += 1

            start_time = time.time()
            result = ValidationResult(
                proxy=proxy,
                is_valid=False,
                test_url=self.primary_test_url,
            )

            try:
                # Use circuit breaker for resilient validation
                is_valid = await self.circuit_breaker.call(
                    self._validate_single_proxy, proxy, result
                )
                result.is_valid = is_valid

                if is_valid:
                    self._successful_validations += 1
                    # Update proxy object with validation results
                    proxy.last_checked = result.timestamp
                    proxy.response_time = result.response_time
                    # if hasattr(proxy, "health_score"):
                    #     # mypy: dynamic attribute for optional health metric
                    #     proxy.health_score = result.health_score  # type: ignore[attr-defined]

            except CircuitBreakerOpenError as e:
                result.error_type = ValidationErrorType.CIRCUIT_BREAKER_OPEN
                result.error_message = str(e)
                logger.debug("Circuit breaker open for %s:%s", proxy.host, proxy.port)

            except Exception as e:
                result.error_type = self._categorize_error(e)
                result.error_message = str(e)
                logger.debug("Proxy %s:%s validation failed: %s", proxy.host, proxy.port, e)

            finally:
                result.response_time = time.time() - start_time
                proxy.last_checked = result.timestamp
                self._validation_history.append(result)

            return result

    async def _validate_single_proxy(self, proxy: Proxy, result: ValidationResult) -> bool:
        """Internal validation logic with enhanced testing."""
        proxy_url = self._build_proxy_url(proxy)

        async with httpx.AsyncClient(
            proxy=proxy_url,
            timeout=httpx.Timeout(self.timeout),
            follow_redirects=True,
            headers={
                "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            },
        ) as client:
            # Test with primary URL
            response = await client.get(self.primary_test_url)
            response.raise_for_status()

            result.status_code = response.status_code
            result.response_headers = dict(response.headers)

            # Extract and analyze response for anonymity detection
            if self.enable_anonymity_detection:
                await self._detect_anonymity(response, result, proxy)

            # Test with additional URLs for reliability (if configured)
            if len(self.test_urls) > 1:
                await self._validate_additional_urls(client, result)

        logger.debug(
            "Proxy %s:%s validated successfully (anonymity: %s)",
            proxy.host,
            proxy.port,
            result.anonymity_detected,
        )
        return True

    def _build_proxy_url(self, proxy: Proxy) -> str:
        """Build proxy URL based on proxy scheme and credentials."""
        # Default to HTTP; prefer the first declared scheme if available
        scheme = proxy.schemes[0].value.lower() if getattr(proxy, "schemes", None) else "http"

        if hasattr(proxy, "credentials") and proxy.credentials:
            auth = f"{proxy.credentials.username}:{proxy.credentials.password}@"
            return f"{scheme}://{auth}{proxy.host}:{proxy.port}"
        else:
            return f"{scheme}://{proxy.host}:{proxy.port}"

    async def _detect_anonymity(
        self, response: httpx.Response, result: ValidationResult, proxy: Proxy
    ) -> None:
        """Detect proxy anonymity level based on response analysis."""
        try:
            # Parse response to extract IP information
            response_data = (
                response.json()
                if response.headers.get("content-type", "").startswith("application/json")
                else {}
            )

            detected_ip = (
                response_data.get("origin") or response_data.get("ip") or response.text.strip()
            )
            result.ip_detected = detected_ip

            headers = result.response_headers or {}

            # Check for forwarded headers that reveal original IP
            forwarded_headers = [
                "x-forwarded-for",
                "x-real-ip",
                "x-originating-ip",
                "x-remote-ip",
                "x-client-ip",
                "via",
                "forwarded",
            ]

            has_forwarded_headers = any(header.lower() in headers for header in forwarded_headers)

            if has_forwarded_headers:
                result.anonymity_detected = AnonymityLevel.TRANSPARENT
            elif detected_ip != proxy.host:  # IP changed, likely anonymous
                result.anonymity_detected = AnonymityLevel.ELITE
            else:
                result.anonymity_detected = AnonymityLevel.ANONYMOUS

        except Exception as e:
            logger.debug(
                "Anonymity detection failed for %s:%s: %s",
                proxy.host,
                proxy.port,
                e,
            )
            result.anonymity_detected = AnonymityLevel.UNKNOWN

    async def _validate_additional_urls(
        self, client: httpx.AsyncClient, result: ValidationResult
    ) -> None:
        """Test proxy against additional URLs for reliability."""
        for test_url in self.test_urls[1:]:  # Skip first URL (already tested)
            try:
                response = await client.get(test_url, timeout=httpx.Timeout(5.0))
                response.raise_for_status()
                logger.debug("Additional URL %s validation successful", test_url)
            except Exception as e:
                logger.debug("Additional URL %s validation failed: %s", test_url, e)
                # Don't fail the entire validation for secondary URLs

    def _categorize_error(self, error: Exception) -> ValidationErrorType:
        """Categorize validation errors for better reporting."""
        error_str = str(error).lower()

        if isinstance(error, asyncio.TimeoutError) or "timeout" in error_str:
            return ValidationErrorType.TIMEOUT
        elif isinstance(error, httpx.ConnectError) or "connection" in error_str:
            return ValidationErrorType.CONNECTION_ERROR
        elif isinstance(error, httpx.ProxyError) or "proxy" in error_str:
            return ValidationErrorType.PROXY_ERROR
        elif isinstance(error, httpx.HTTPStatusError):
            if error.response.status_code == 429:
                return ValidationErrorType.RATE_LIMITED
            elif 400 <= error.response.status_code < 500:
                return ValidationErrorType.AUTHENTICATION_ERROR
            else:
                return ValidationErrorType.HTTP_ERROR
        elif isinstance(error, CircuitBreakerOpenError):
            return ValidationErrorType.CIRCUIT_BREAKER_OPEN
        elif "ssl" in error_str or "certificate" in error_str:
            return ValidationErrorType.SSL_ERROR
        else:
            return ValidationErrorType.UNKNOWN

    async def validate_proxies(self, proxies: List[Proxy]) -> ValidationSummary:
        """Validate multiple proxies and return comprehensive summary."""
        if not proxies:
            return ValidationSummary(
                total_proxies=0,
                valid_proxy_results=[],
                failed_proxy_results=[],
            )

        start_time = time.time()
        logger.info("Validating %d proxies with enhanced validation...", len(proxies))

        # Create validation tasks for all proxies
        tasks = [self.validate_proxy(proxy) for proxy in proxies]

        # Run validations concurrently
        results: List[ValidationResult] = await asyncio.gather(*tasks, return_exceptions=False)

        # Process results and build summary
        valid_results = [r for r in results if r.is_valid]
        failed_results = [r for r in results if not r.is_valid]

        response_times = [r.response_time for r in valid_results if r.response_time is not None]

        # Error breakdown
        error_breakdown: Dict[ValidationErrorType, int] = {}
        for result in failed_results:
            if result.error_type:
                error_breakdown[result.error_type] = error_breakdown.get(result.error_type, 0) + 1

        summary = ValidationSummary(
            total_proxies=len(proxies),
            valid_proxy_results=valid_results,
            failed_proxy_results=failed_results,
            success_rate=len(valid_results) / len(proxies) if proxies else 0.0,
            error_breakdown=error_breakdown,
            validation_duration=time.time() - start_time,
            avg_response_time=(
                sum(response_times) / len(response_times) if response_times else None
            ),
            min_response_time=min(response_times) if response_times else None,
            max_response_time=max(response_times) if response_times else None,
        )

        logger.info(
            "Validation complete: %d/%d valid (%s) in %.1fs [Quality: %s]",
            summary.valid_proxy_count,
            summary.total_proxies,
            f"{summary.success_rate:.1%}",
            summary.validation_duration,
            summary.quality_tier,
        )

        return summary

    def get_validation_stats(self) -> Dict[str, Any]:
        """Get overall validation statistics."""
        return {
            "total_validations": self._total_validations,
            "successful_validations": self._successful_validations,
            "success_rate": (
                self._successful_validations / self._total_validations
                if self._total_validations
                else 0.0
            ),
            "recent_validations": len(self._validation_history[-100:]),  # Last 100
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on validation endpoints."""
        health_status: Dict[str, Any] = {
            "circuit_breaker_state": self.circuit_breaker.state.value,
            "circuit_breaker_failures": self.circuit_breaker.failure_count,
            "test_endpoints": [],
        }

        for test_url in self.test_urls:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(test_url)
                    health_status["test_endpoints"].append(
                        {
                            "url": test_url,
                            "status": "healthy",
                            "response_time": response.elapsed.total_seconds(),
                            "status_code": response.status_code,
                        }
                    )
            except Exception as e:
                health_status["test_endpoints"].append(
                    {"url": test_url, "status": "unhealthy", "error": str(e)}
                )

        return health_status
