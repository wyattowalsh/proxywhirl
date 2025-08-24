"""proxywhirl/validator.py -- proxy validation functionality"""

import asyncio
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional, TypeVar

import httpx
from loguru import logger
from pydantic import BaseModel, Field, computed_field

from proxywhirl.models import (
    AnonymityLevel,
    Proxy,
    ProxyError,
    TargetDefinition,
    ValidationErrorType,
)

T = TypeVar("T")


class QualityLevel(Enum):
    """Quality levels for proxy validation."""

    BASIC = "basic"  # Simple connectivity test
    STANDARD = "standard"  # Connectivity + response validation
    THOROUGH = "thorough"  # Full feature validation including anonymity


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, requests blocked
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerOpenError(ProxyError):
    """Raised when circuit breaker is open."""


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
        expected_exception: type[Exception] | tuple[type[Exception], ...] = (
            httpx.HTTPError,
            httpx.ConnectError,
            httpx.ProxyError,
            asyncio.TimeoutError,
        ),
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


class ValidationResult(BaseModel):
    """Comprehensive validation result with metrics and error details."""

    proxy: Proxy
    is_valid: bool
    response_time: Optional[float] = None
    error_type: Optional[ValidationErrorType] = None
    error_message: Optional[str] = None
    status_code: Optional[int] = None
    test_url: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    response_headers: Optional[Dict[str, str]] = Field(default_factory=dict)
    ip_detected: Optional[str] = None
    anonymity_detected: Optional[AnonymityLevel] = None
    # Target-based validation results
    target_results: Optional[Dict[str, "TargetValidationResult"]] = None

    @property
    def error(self) -> Optional[str]:
        """Backward compatibility property for tests."""
        return self.error_message

    @computed_field
    @property
    def validation_efficiency_score(self) -> float:
        """Computed field for validation efficiency scoring using Pydantic v2."""
        if not self.is_valid:
            return 0.0

        # Base efficiency score
        base_score = 1.0

        # Response time efficiency (lower is better)
        if self.response_time:
            if self.response_time <= 1.0:
                base_score *= 1.5  # Excellent
            elif self.response_time <= 3.0:
                base_score *= 1.2  # Good
            elif self.response_time <= 5.0:
                base_score *= 1.0  # Average
            elif self.response_time <= 10.0:
                base_score *= 0.8  # Below average
            else:
                base_score *= 0.5  # Poor

        # Anonymity bonus
        if self.anonymity_detected == AnonymityLevel.ELITE:
            base_score *= 1.3
        elif self.anonymity_detected == AnonymityLevel.ANONYMOUS:
            base_score *= 1.1
        elif self.anonymity_detected == AnonymityLevel.TRANSPARENT:
            base_score *= 0.9

        return round(base_score, 2)

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

        # Allow score to exceed 1.0 for exceptional performance
        return score

    @classmethod
    def model_validate_json_fast(cls, json_data: str) -> "ValidationResult":
        """Fast JSON validation using Pydantic v2 performance optimization."""
        return cls.model_validate_json(json_data)

    class Config:
        # Enable arbitrary types for complex objects like Proxy
        arbitrary_types_allowed = True


class TargetValidationResult(BaseModel):
    """Validation result for a specific target."""

    target_id: str
    target_url: str
    is_valid: bool
    response_time: Optional[float] = None
    status_code: Optional[int] = None
    error_type: Optional[ValidationErrorType] = None
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ValidationSummary(BaseModel):
    """Summary of validation results across multiple proxies."""

    total_proxies: int
    valid_proxy_results: List[ValidationResult]
    failed_proxy_results: List[ValidationResult]
    avg_response_time: Optional[float] = None
    min_response_time: Optional[float] = None
    max_response_time: Optional[float] = None
    success_rate: float = 0.0
    error_breakdown: Dict[ValidationErrorType, int] = Field(default_factory=dict)
    validation_duration: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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
        # Target-based validation support
        targets: Optional[Dict[str, TargetDefinition]] = None,
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

        # Target-based validation support
        self.targets = targets or {}

        self.retry_attempts = retry_attempts
        self.enable_anonymity_detection = enable_anonymity_detection
        self.enable_geolocation_detection = enable_geolocation_detection

        # HTTPX connection pooling for performance optimization
        self.limits = httpx.Limits(
            max_keepalive_connections=20, max_connections=100, keepalive_expiry=30.0
        )

        # Event hooks for monitoring and debugging
        self.event_hooks: Dict[str, List[Callable[..., Any]]] = {
            "request": [self._log_request],
            "response": [self._log_response],
        }

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
            "Enhanced ProxyValidator initialized with %d test URLs and %d targets",
            len(self.test_urls),
            len(self.targets),
        )

    def create_trusted_result(
        self, proxy: Proxy, is_valid: bool, response_time: float
    ) -> ValidationResult:
        """Create ValidationResult with trusted data (performance optimization)."""
        return ValidationResult(
            proxy=proxy,
            is_valid=is_valid,
            response_time=response_time,  # Trusted response time
            timestamp=datetime.now(timezone.utc),
            test_url=self.test_urls[0] if self.test_urls else "",
        )

    def _log_request(self, request: httpx.Request) -> None:
        """Log outgoing HTTP requests for monitoring."""
        logger.debug("→ %s %s", request.method, request.url)

    def _log_response(self, response: httpx.Response) -> None:
        """Log incoming HTTP responses for monitoring."""
        logger.debug(
            "← %s %s [%d] %.3fs",
            response.request.method,
            response.url,
            response.status_code,
            response.elapsed.total_seconds() if response.elapsed else 0.0,
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
                # If targets are defined, use target-based validation
                if self.targets:
                    is_valid = await self.circuit_breaker.call(
                        self._validate_proxy_for_targets, proxy, result
                    )
                else:
                    # Use legacy single-URL validation for backward compatibility
                    is_valid = await self.circuit_breaker.call(
                        self._validate_single_proxy, proxy, result
                    )

                result.is_valid = is_valid

                if is_valid:
                    self._successful_validations += 1
                    # Update proxy object with validation results
                    proxy.last_checked = result.timestamp
                    proxy.response_time = result.response_time

            except CircuitBreakerOpenError as e:
                result.error_type = ValidationErrorType.CIRCUIT_BREAKER_OPEN
                result.error_message = str(e)
                logger.debug("Circuit breaker open for %s:%s", proxy.host, proxy.port)

            except (httpx.HTTPError, asyncio.TimeoutError) as e:
                result.error_type = self._categorize_error(e)
                result.error_message = str(e)
                logger.debug("Proxy %s:%s validation failed: %s", proxy.host, proxy.port, e)
            except Exception as e:
                # Catch-all for unexpected errors, but log for investigation
                result.error_type = ValidationErrorType.UNKNOWN
                result.error_message = f"Unexpected error: {str(e)}"
                logger.warning("Unexpected error validating %s:%s: %s", proxy.host, proxy.port, e)

            finally:
                result.response_time = time.time() - start_time
                proxy.last_checked = result.timestamp
                self._validation_history.append(result)

                # Memory management for validation history
                self._manage_validation_history_memory()

            return result

    async def validate_proxies_batch(
        self,
        proxies: List[Proxy],
        *,
        batch_size: int = 50,
        max_concurrent: Optional[int] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[ValidationResult]:
        """
        Efficiently validate a batch of proxies with controlled concurrency and memory management.

        Args:
            proxies: List of proxy objects to validate
            batch_size: Number of proxies to process in each batch (default: 50)
            max_concurrent: Override default concurrency limit (default: use instance setting)
            progress_callback: Optional callback function to report progress (completed, total)

        Returns:
            List of ValidationResult objects
        """
        if not proxies:
            return []

        # Use instance concurrency setting if not overridden
        concurrent_limit = max_concurrent or self.semaphore._value
        semaphore = asyncio.Semaphore(concurrent_limit)

        results: List[ValidationResult] = []
        total_proxies = len(proxies)
        completed = 0

        logger.info(
            f"Starting batch validation of {total_proxies} proxies with batch size {batch_size}"
        )

        # Process proxies in batches to manage memory
        for batch_start in range(0, total_proxies, batch_size):
            batch_end = min(batch_start + batch_size, total_proxies)
            batch_proxies = proxies[batch_start:batch_end]

            logger.debug(
                f"Processing batch {batch_start//batch_size + 1}: proxies {batch_start+1} to {batch_end}"
            )

            # Create validation tasks for the current batch
            async def validate_with_semaphore(proxy: Proxy) -> ValidationResult:
                async with semaphore:
                    result = await self.validate_proxy(proxy)
                    nonlocal completed
                    completed += 1

                    # Report progress if callback provided
                    if progress_callback:
                        progress_callback(completed, total_proxies)

                    return result

            # Execute batch validation concurrently
            batch_tasks = [validate_with_semaphore(proxy) for proxy in batch_proxies]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            # Process results and handle exceptions
            for i, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    # Create error result for failed validation
                    error_result = ValidationResult(
                        proxy=batch_proxies[i],
                        is_valid=False,
                        error_type=ValidationErrorType.CONNECTION_ERROR,
                        error_message=f"Batch validation error: {str(result)}",
                        timestamp=datetime.now(timezone.utc),
                    )
                    results.append(error_result)
                    logger.error(
                        f"Error validating proxy {batch_proxies[i].ip}:{batch_proxies[i].port}: {result}"
                    )
                elif isinstance(result, ValidationResult):
                    results.append(result)

            # Memory management: limit validation history growth
            if len(self._validation_history) > 10000:  # Configurable limit
                # Keep only the most recent 5000 results
                self._validation_history = self._validation_history[-5000:]
                logger.debug("Trimmed validation history to prevent memory bloat")

        logger.info(
            f"Batch validation completed. {len([r for r in results if r.is_valid])} valid out of {total_proxies} proxies"
        )
        return results

    def _manage_validation_history_memory(
        self, max_size: int = 10000, trim_size: int = 5000
    ) -> None:
        """
        Manage validation history memory to prevent memory leaks during long-running sessions.

        Args:
            max_size: Maximum number of results to keep in memory
            trim_size: Number of most recent results to retain when trimming
        """
        if len(self._validation_history) > max_size:
            # Keep only the most recent results
            self._validation_history = self._validation_history[-trim_size:]
            logger.debug(
                f"Trimmed validation history from {max_size}+ to {trim_size} results to prevent memory bloat"
            )

    async def _validate_proxy_for_targets(self, proxy: Proxy, result: ValidationResult) -> bool:
        """Validate a proxy against all defined targets."""
        proxy_url = self._build_proxy_url(proxy)
        target_results: Dict[str, TargetValidationResult] = {}
        overall_success = False

        async with httpx.AsyncClient(
            proxy=proxy_url,
            timeout=httpx.Timeout(self.timeout),
            limits=self.limits,  # ✅ Connection pooling
            event_hooks=self.event_hooks,  # ✅ Monitoring hooks
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                )
            },
        ) as client:

            # Test each target
            for target_id, target_def in self.targets.items():
                target_start_time = time.time()
                target_result = TargetValidationResult(
                    target_id=target_id,
                    target_url=target_def.url,
                    is_valid=False,
                )

                try:
                    # Use target-specific timeout if defined
                    target_timeout = target_def.timeout or self.timeout
                    response = await client.get(
                        target_def.url, timeout=httpx.Timeout(target_timeout)
                    )

                    # Check if status code is expected
                    expected_codes = target_def.expected_status_codes or [200]
                    if response.status_code in expected_codes:
                        target_result.is_valid = True
                        overall_success = True  # At least one target succeeded

                        # Update proxy target health (defensive check)
                        target_response_time = time.time() - target_start_time
                        if hasattr(proxy, "update_target_health") and callable(
                            getattr(proxy, "update_target_health", None)
                        ):
                            proxy.update_target_health(target_id, True, target_response_time)

                        # Use first successful target for overall anonymity detection
                        if (
                            not result.ip_detected
                            and self.enable_anonymity_detection
                            and target_id == next(iter(self.targets))
                        ):  # First target
                            await self._detect_anonymity(response, result, proxy)
                    else:
                        if hasattr(proxy, "update_target_health") and callable(
                            getattr(proxy, "update_target_health", None)
                        ):
                            proxy.update_target_health(target_id, False)
                        target_result.error_message = (
                            f"Unexpected status code: {response.status_code}"
                        )

                    target_result.status_code = response.status_code
                    target_result.response_time = time.time() - target_start_time

                except (httpx.HTTPError, asyncio.TimeoutError) as e:
                    if hasattr(proxy, "update_target_health") and callable(
                        getattr(proxy, "update_target_health", None)
                    ):
                        proxy.update_target_health(target_id, False)
                    target_result.error_type = self._categorize_error(e)
                    target_result.error_message = str(e)
                    target_result.response_time = time.time() - target_start_time
                    logger.debug(
                        "Target %s validation failed for proxy %s:%s: %s",
                        target_id,
                        proxy.host,
                        proxy.port,
                        e,
                    )
                except Exception as e:
                    # Catch-all for unexpected errors in target validation
                    if hasattr(proxy, "update_target_health") and callable(
                        getattr(proxy, "update_target_health", None)
                    ):
                        proxy.update_target_health(target_id, False)
                    target_result.error_type = ValidationErrorType.UNKNOWN
                    target_result.error_message = f"Unexpected target validation error: {str(e)}"
                    target_result.response_time = time.time() - target_start_time
                    logger.warning(
                        "Unexpected error in target %s validation for proxy %s:%s: %s",
                        target_id,
                        proxy.host,
                        proxy.port,
                        e,
                    )

                target_results[target_id] = target_result

            result.target_results = target_results

        if overall_success:
            logger.debug(
                "Proxy %s:%s validated successfully for %d/%d targets",
                proxy.host,
                proxy.port,
                sum(1 for tr in target_results.values() if tr.is_valid),
                len(target_results),
            )

        return overall_success

    async def _validate_single_proxy(self, proxy: Proxy, result: ValidationResult) -> bool:
        """Internal validation logic with enhanced testing."""
        proxy_url = self._build_proxy_url(proxy)

        async with httpx.AsyncClient(
            proxy=proxy_url,
            timeout=httpx.Timeout(self.timeout),
            limits=self.limits,  # ✅ Connection pooling
            event_hooks=self.event_hooks,  # ✅ Monitoring hooks
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                )
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
        if getattr(proxy, "schemes", None) and len(proxy.schemes) > 0:
            first_scheme = proxy.schemes[0]
            # Handle both enum objects and string values (after serialization)
            if hasattr(first_scheme, "value"):
                scheme = first_scheme.value.lower()
            else:
                scheme = str(first_scheme).lower()
        else:
            scheme = "http"

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

        except (httpx.HTTPError, ValueError, KeyError) as e:
            # Handle specific parsing and HTTP errors
            logger.debug(
                "Anonymity detection failed for %s:%s: %s",
                proxy.host,
                proxy.port,
                e,
            )
            result.anonymity_detected = AnonymityLevel.UNKNOWN
        except Exception as e:
            # Catch-all for unexpected errors in anonymity detection
            logger.warning(
                "Unexpected error in anonymity detection for %s:%s: %s",
                proxy.host,
                proxy.port,
                e,
            )
            result.anonymity_detected = AnonymityLevel.UNKNOWN

    async def _validate_additional_urls(
        self, client: httpx.AsyncClient, result: ValidationResult
    ) -> None:
        """Test proxy against additional URLs for reliability."""
        additional_url_success_count = 0
        total_additional_urls = len(self.test_urls) - 1

        for test_url in self.test_urls[1:]:  # Skip first URL (already tested)
            try:
                response = await client.get(test_url, timeout=httpx.Timeout(5.0))
                response.raise_for_status()
                additional_url_success_count += 1
                logger.debug("Additional URL %s validation successful", test_url)
            except (httpx.HTTPError, asyncio.TimeoutError) as e:
                logger.debug("Additional URL %s validation failed: %s", test_url, e)
                # Don't fail the entire validation for secondary URLs
            except Exception as e:
                # Unexpected errors in additional URL validation
                logger.warning("Unexpected error validating additional URL %s: %s", test_url, e)
                # Don't fail the entire validation for secondary URLs

        # Log additional URL validation metrics for debugging
        if total_additional_urls > 0:
            success_rate = additional_url_success_count / total_additional_urls
            logger.debug(
                "Additional URLs validation for %s:%s: %d/%d success (%.1%)",
                result.proxy.host,
                result.proxy.port,
                additional_url_success_count,
                total_additional_urls,
                success_rate * 100,
            )

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
                async with httpx.AsyncClient(
                    timeout=5.0,
                    limits=self.limits,  # ✅ Connection pooling for health checks
                    event_hooks=self.event_hooks,  # ✅ Monitoring hooks
                ) as client:
                    response = await client.get(test_url)
                    health_status["test_endpoints"].append(
                        {
                            "url": test_url,
                            "status": "healthy",
                            "response_time": response.elapsed.total_seconds(),
                            "status_code": response.status_code,
                        }
                    )
            except (httpx.HTTPError, asyncio.TimeoutError) as e:
                health_status["test_endpoints"].append(
                    {"url": test_url, "status": "unhealthy", "error": str(e)}
                )
            except Exception as e:
                # Unexpected errors in health check
                health_status["test_endpoints"].append(
                    {"url": test_url, "status": "unhealthy", "error": f"Unexpected error: {str(e)}"}
                )

        return health_status
