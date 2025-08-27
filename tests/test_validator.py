# pyright: reportMissingImports=false, reportUnknownMemberType=false,
#   reportUnknownArgumentType=false, reportUnknownParameterType=false
# mypy: ignore-errors
import asyncio
import types
from datetime import datetime, timezone
from ipaddress import ip_address
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from proxywhirl.models import (
    AnonymityLevel,
    Proxy,
    ProxyStatus,
    Scheme,
    TargetDefinition,
    ValidationErrorType,
)
from proxywhirl.validator import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitState,
    ProxyValidator,
    QualityLevel,
    TargetValidationResult,
    ValidationResult,
    ValidationSummary,
)


class DummyResponse:
    def __init__(self, status_code: int = 200, text: str = "192.0.2.1"):
        self.status_code = status_code
        self.text = text
        self.headers = {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError("bad status")

    def json(self):
        return {"ip": self.text}


class DummyAsyncClient:
    def __init__(self, should_fail: bool = False, responses_by_url: dict = None):
        self.should_fail = should_fail
        self.responses_by_url = responses_by_url or {}

    async def __aenter__(self) -> "DummyAsyncClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:  # type: ignore[no-untyped-def]
        return False

    async def get(self, url: str, **kwargs):
        if url in self.responses_by_url:
            return self.responses_by_url[url]
        if self.should_fail:
            return DummyResponse(500)
        return DummyResponse(200)


# pyright: reportMissingImports=false, reportUnknownMemberType=false,
#   reportUnknownArgumentType=false, reportUnknownParameterType=false
# mypy: ignore-errors
import asyncio
import types
from datetime import datetime, timezone
from ipaddress import ip_address
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
from hypothesis import given
from hypothesis import strategies as st

from proxywhirl.models import (
    AnonymityLevel,
    Proxy,
    ProxyStatus,
    Scheme,
    TargetDefinition,
    ValidationErrorType,
)
from proxywhirl.validator import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitState,
    ProxyValidator,
    QualityLevel,
    TargetValidationResult,
    ValidationResult,
    ValidationSummary,
)

# ============================================================================
# ENHANCED ASYNC CLIENT MOCKS
# ============================================================================


class EnhancedAsyncHttpMock:
    """Enhanced async HTTP client mock with comprehensive scenario support."""

    def __init__(
        self,
        default_response_status: int = 200,
        default_response_text: str = "192.0.2.1",
        response_delays: float = 0.0,
        failure_probability: float = 0.0,
        custom_responses: dict = None,
    ):
        self.default_status = default_response_status
        self.default_text = default_response_text
        self.response_delays = response_delays
        self.failure_probability = failure_probability
        self.custom_responses = custom_responses or {}
        self.request_count = 0
        self.request_history = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return None

    async def get(self, url: str, **kwargs):
        """Enhanced get method with comprehensive scenario handling."""
        self.request_count += 1
        self.request_history.append({"url": url, "kwargs": kwargs})

        # Simulate network delay if specified
        if self.response_delays > 0:
            await asyncio.sleep(self.response_delays)

        # Handle custom responses for specific URLs
        if url in self.custom_responses:
            response_config = self.custom_responses[url]
            if isinstance(response_config, Exception):
                raise response_config
            return self._create_response(**response_config)

        # Handle failure probability for chaos testing
        import random

        if self.failure_probability > 0 and random.random() < self.failure_probability:
            raise httpx.TimeoutException("Random failure for chaos testing")

        return self._create_response(self.default_status, self.default_text)

    def _create_response(
        self, status_code: int = 200, text: str = "192.0.2.1", headers: dict = None
    ):
        """Create mock response object."""
        response = Mock(spec=httpx.Response)
        response.status_code = status_code
        response.text = text
        response.headers = headers or {}
        response.json.return_value = {"ip": text}

        if status_code >= 400:
            response.raise_for_status.side_effect = httpx.HTTPStatusError(
                f"HTTP {status_code}", request=Mock(), response=response
            )
        else:
            response.raise_for_status.return_value = None

        return response


class DummyResponse:
    """Legacy response class for backwards compatibility."""

    def __init__(self, status_code: int = 200, text: str = "192.0.2.1"):
        self.status_code = status_code
        self.text = text
        self.headers = {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError("bad status")

    def json(self):
        return {"ip": self.text}


class DummyAsyncClient:
    """Legacy async client for backwards compatibility."""

    def __init__(self, should_fail: bool = False, responses_by_url: dict = None):
        self.should_fail = should_fail
        self.responses_by_url = responses_by_url or {}

    async def __aenter__(self) -> "DummyAsyncClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:  # type: ignore[no-untyped-def]
        return False

    async def get(self, url: str, **kwargs):
        if url in self.responses_by_url:
            return self.responses_by_url[url]
        if self.should_fail:
            return DummyResponse(500)
        return DummyResponse(200)


# ============================================================================
# ENHANCED VALIDATOR TESTS WITH ASYNC PATTERNS
# ============================================================================


@pytest.mark.asyncio
class TestProxyValidatorEnhanced:
    """Enhanced test class with comprehensive async testing patterns."""

    async def test_validate_proxy_success_enhanced(self, mock_async_httpx_client):
        """Test successful proxy validation with enhanced mocking."""
        pv = ProxyValidator()

        with patch("proxywhirl.validator.httpx.AsyncClient", return_value=mock_async_httpx_client):
            proxy = Proxy(
                host="192.0.2.1",
                ip=ip_address("192.0.2.1"),
                port=8080,
                schemes=[Scheme.HTTP],
                anonymity=AnonymityLevel.UNKNOWN,
            )

            result = await pv.validate_proxy(proxy)

            assert result.is_valid is True
            assert result.response_time is not None
            assert result.response_time >= 0.0
            assert result.error is None
            assert isinstance(result.timestamp, datetime)

    async def test_validate_proxy_with_custom_timeout(self, mock_async_httpx_client):
        """Test proxy validation with custom timeout settings."""
        pv = ProxyValidator(timeout=5.0)

        # Configure mock to simulate delay but within timeout
        mock_async_httpx_client.response_delays = 2.0

        with patch("proxywhirl.validator.httpx.AsyncClient", return_value=mock_async_httpx_client):
            proxy = Proxy(
                host="192.0.2.1",
                ip=ip_address("192.0.2.1"),
                port=8080,
                schemes=[Scheme.HTTP],
                anonymity=AnonymityLevel.UNKNOWN,
            )

            result = await pv.validate_proxy(proxy)

            assert result.is_valid is True
            assert result.response_time >= 2.0  # Should include the delay

    async def test_validate_proxy_timeout_failure(self):
        """Test proxy validation timeout handling."""
        pv = ProxyValidator(timeout=1.0)

        # Create mock that always times out
        timeout_mock = EnhancedAsyncHttpMock(response_delays=2.0)

        with patch("proxywhirl.validator.httpx.AsyncClient", return_value=timeout_mock):
            proxy = Proxy(
                host="192.0.2.1",
                ip=ip_address("192.0.2.1"),
                port=8080,
                schemes=[Scheme.HTTP],
                anonymity=AnonymityLevel.UNKNOWN,
            )

            result = await pv.validate_proxy(proxy)

            assert result.is_valid is False
            assert result.error is not None

    async def test_validate_proxy_http_error_scenarios(self):
        """Test various HTTP error scenarios."""
        pv = ProxyValidator()

        error_scenarios = [
            (404, "Not Found"),
            (500, "Internal Server Error"),
            (502, "Bad Gateway"),
            (503, "Service Unavailable"),
        ]

        for status_code, error_text in error_scenarios:
            error_mock = EnhancedAsyncHttpMock(
                default_response_status=status_code, default_response_text=error_text
            )

            with patch("proxywhirl.validator.httpx.AsyncClient", return_value=error_mock):
                proxy = Proxy(
                    host="192.0.2.1",
                    ip=ip_address("192.0.2.1"),
                    port=8080,
                    schemes=[Scheme.HTTP],
                    anonymity=AnonymityLevel.UNKNOWN,
                )

                result = await pv.validate_proxy(proxy)

                assert result.is_valid is False
                assert result.error is not None
                assert f"{status_code}" in str(result.error) or error_text in str(result.error)

    @given(
        st.builds(
            Proxy,
            host=st.text(
                alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")),
                min_size=5,
                max_size=15,
            ),
            ip=st.builds(
                ip_address,
                st.integers(min_value=16777216, max_value=3758096383).map(
                    lambda x: f"{(x>>24)&255}.{(x>>16)&255}.{(x>>8)&255}.{x&255}"
                ),
            ),
            port=st.integers(min_value=1, max_value=65535),
            schemes=st.lists(
                st.sampled_from([Scheme.HTTP, Scheme.HTTPS, Scheme.SOCKS4, Scheme.SOCKS5]),
                min_size=1,
                max_size=2,
            ),
            anonymity=st.sampled_from(
                [AnonymityLevel.ELITE, AnonymityLevel.ANONYMOUS, AnonymityLevel.TRANSPARENT]
            ),
        )
    )
    async def test_property_validate_proxy_structure(self, proxy: Proxy):
        """Property-based test for proxy validation structure."""
        pv = ProxyValidator()

        success_mock = EnhancedAsyncHttpMock(default_response_status=200)

        with patch("proxywhirl.validator.httpx.AsyncClient", return_value=success_mock):
            result = await pv.validate_proxy(proxy)

            # Properties that should always hold regardless of input
            assert isinstance(result, ValidationResult)
            assert isinstance(result.is_valid, bool)
            assert isinstance(result.timestamp, datetime)
            assert result.proxy == proxy

            # If validation successful, response_time should be non-negative
            if result.is_valid:
                assert result.response_time is not None
                assert result.response_time >= 0.0
                assert result.error is None
            else:
                # Failed validations may or may not have response_time
                if result.error is not None:
                    assert isinstance(result.error, str)

    async def test_concurrent_validation_patterns(self):
        """Test concurrent proxy validation patterns."""
        pv = ProxyValidator()

        # Create multiple proxies for concurrent testing
        proxies = [
            Proxy(
                host=f"192.0.2.{i}",
                ip=ip_address(f"192.0.2.{i}"),
                port=8080 + i,
                schemes=[Scheme.HTTP],
                anonymity=AnonymityLevel.UNKNOWN,
            )
            for i in range(1, 6)  # 5 proxies
        ]

        success_mock = EnhancedAsyncHttpMock(default_response_status=200)

        with patch("proxywhirl.validator.httpx.AsyncClient", return_value=success_mock):
            # Test concurrent validation
            tasks = [pv.validate_proxy(proxy) for proxy in proxies]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # All should succeed and be ValidationResult instances
            assert len(results) == len(proxies)
            for result in results:
                assert isinstance(result, ValidationResult)
                assert result.is_valid is True


@pytest.mark.asyncio
async def test_validate_proxy_success(monkeypatch):
    pv = ProxyValidator()

    # Create a comprehensive httpx mock
    import httpx

    import proxywhirl.validator as validator

    # Create the mock namespace with all required httpx components
    mock_httpx = types.SimpleNamespace(
        AsyncClient=lambda **_: DummyAsyncClient(False),
        HTTPError=httpx.HTTPError,
        ConnectError=httpx.ConnectError,
        ProxyError=httpx.ProxyError,
        Timeout=httpx.Timeout,
        Limits=httpx.Limits,
        Request=httpx.Request,
        Response=httpx.Response,
    )

    monkeypatch.setattr(validator, "httpx", mock_httpx)

    p = Proxy(
        host="192.0.2.1",
        ip=ip_address("192.0.2.1"),
        port=8080,
        schemes=[Scheme.HTTP],
        anonymity=AnonymityLevel.UNKNOWN,
    )
    result = await pv.validate_proxy(p)
    assert result.is_valid is True and result.response_time is not None


@pytest.mark.asyncio
async def test_validate_proxy_failure(monkeypatch):
    pv = ProxyValidator()
    import httpx

    import proxywhirl.validator as validator

    # Create the mock namespace with all required httpx components
    mock_httpx = types.SimpleNamespace(
        AsyncClient=lambda **_: DummyAsyncClient(True),
        HTTPError=httpx.HTTPError,
        ConnectError=httpx.ConnectError,
        ProxyError=httpx.ProxyError,
        Timeout=httpx.Timeout,
        Limits=httpx.Limits,
        Request=httpx.Request,
        Response=httpx.Response,
    )

    monkeypatch.setattr(validator, "httpx", mock_httpx)

    p = Proxy(
        host="192.0.2.1",
        ip=ip_address("192.0.2.1"),
        port=8080,
        schemes=[Scheme.HTTP],
        anonymity=AnonymityLevel.UNKNOWN,
    )
    result = await pv.validate_proxy(p)
    assert result.is_valid is False


@pytest.mark.asyncio
async def test_target_based_validation_success(monkeypatch):
    """Test target-based validation with multiple targets."""
    targets = {
        "google": TargetDefinition(
            target_id="google", url="https://www.google.com", name="Google Search"
        ),
        "api": TargetDefinition(target_id="api", url="https://api.ipify.org", name="IP API"),
    }

    pv = ProxyValidator(targets=targets)

    # Mock responses for different URLs
    responses = {
        "https://www.google.com": DummyResponse(200, "OK"),
        "https://api.ipify.org": DummyResponse(200, '{"ip": "192.0.2.1"}'),
    }

    import proxywhirl.validator as validator

    # Comprehensive httpx mock with all required components
    mock_httpx = types.SimpleNamespace(
        AsyncClient=lambda **_: DummyAsyncClient(False, responses),  # type: ignore[misc]
        HTTPError=httpx.HTTPError,
        ConnectError=httpx.ConnectError,
        ProxyError=httpx.ProxyError,
        Timeout=httpx.Timeout,
        Limits=httpx.Limits,
        Request=httpx.Request,
        Response=httpx.Response,
        ReadTimeout=httpx.ReadTimeout,
        WriteTimeout=httpx.WriteTimeout,
        ConnectTimeout=httpx.ConnectTimeout,
        PoolTimeout=httpx.PoolTimeout,
    )

    monkeypatch.setattr(validator, "httpx", mock_httpx)

    p = Proxy(  # type: ignore[misc]
        host="192.0.2.1",
        ip=ip_address("192.0.2.1"),
        port=8080,
        schemes=[Scheme.HTTP],
        anonymity=AnonymityLevel.UNKNOWN,
    )

    result = await pv.validate_proxy(p)

    # Should succeed overall
    assert result.is_valid is True
    assert result.target_results is not None
    assert len(result.target_results) == 2

    # Check individual target results
    assert "google" in result.target_results
    assert "api" in result.target_results
    assert result.target_results["google"].is_valid is True
    assert result.target_results["api"].is_valid is True

    # Check proxy target health was updated
    google_health = p.get_target_health("google")
    api_health = p.get_target_health("api")
    assert google_health is not None
    assert api_health is not None
    assert google_health.total_successes == 1
    assert api_health.total_successes == 1


@pytest.mark.asyncio
async def test_target_based_validation_partial_failure(monkeypatch):
    """Test target-based validation where some targets fail."""
    targets = {
        "working": TargetDefinition(target_id="working", url="https://working.example.com"),  # type: ignore[misc]
        "failing": TargetDefinition(target_id="failing", url="https://failing.example.com"),  # type: ignore[misc]
    }

    pv = ProxyValidator(targets=targets)

    # Mock responses - one succeeds, one fails
    responses = {
        "https://working.example.com": DummyResponse(200, "OK"),
        "https://failing.example.com": DummyResponse(500, "Error"),
    }

    import proxywhirl.validator as validator

    monkeypatch.setattr(
        validator,
        "httpx",
        types.SimpleNamespace(
            AsyncClient=lambda **_: DummyAsyncClient(False, responses),  # type: ignore[misc]
            HTTPError=httpx.HTTPError,
            ConnectError=httpx.ConnectError,
            ProxyError=httpx.ProxyError,
            Timeout=httpx.Timeout,
            Limits=httpx.Limits,
            Request=httpx.Request,
            Response=httpx.Response,
            ReadTimeout=httpx.ReadTimeout,
            WriteTimeout=httpx.WriteTimeout,
            ConnectTimeout=httpx.ConnectTimeout,
            PoolTimeout=httpx.PoolTimeout,
        ),
    )

    p = Proxy(  # type: ignore[misc]
        host="192.0.2.1",
        ip=ip_address("192.0.2.1"),
        port=8080,
        schemes=[Scheme.HTTP],
        anonymity=AnonymityLevel.UNKNOWN,
    )

    result = await pv.validate_proxy(p)

    # Should succeed overall (at least one target worked)
    assert result.is_valid is True
    assert result.target_results is not None

    # Check individual results
    assert result.target_results["working"].is_valid is True
    assert result.target_results["failing"].is_valid is False

    # Check proxy health tracking
    working_health = p.get_target_health("working")
    failing_health = p.get_target_health("failing")
    assert working_health is not None
    assert failing_health is not None
    assert working_health.total_successes == 1
    assert failing_health.total_attempts - failing_health.total_successes == 1  # total failures


@pytest.mark.asyncio
async def test_target_validation_with_custom_timeouts(monkeypatch):
    """Test targets with custom timeouts."""
    targets = {
        "fast": TargetDefinition(target_id="fast", url="https://fast.example.com", timeout=1.0),  # type: ignore[misc]
        "slow": TargetDefinition(target_id="slow", url="https://slow.example.com", timeout=30.0),  # type: ignore[misc]
    }

    pv = ProxyValidator(targets=targets, timeout=10.0)

    responses = {
        "https://fast.example.com": DummyResponse(200, "Fast"),
        "https://slow.example.com": DummyResponse(200, "Slow"),
    }

    import proxywhirl.validator as validator

    monkeypatch.setattr(
        validator,
        "httpx",
        types.SimpleNamespace(
            AsyncClient=lambda **_: DummyAsyncClient(False, responses),  # type: ignore[misc]
            HTTPError=httpx.HTTPError,
            ConnectError=httpx.ConnectError,
            ProxyError=httpx.ProxyError,
            Timeout=httpx.Timeout,
            Limits=httpx.Limits,
            Request=httpx.Request,
            Response=httpx.Response,
            ReadTimeout=httpx.ReadTimeout,
            WriteTimeout=httpx.WriteTimeout,
            ConnectTimeout=httpx.ConnectTimeout,
            PoolTimeout=httpx.PoolTimeout,
        ),
    )

    p = Proxy(  # type: ignore[misc]
        host="192.0.2.1",
        ip=ip_address("192.0.2.1"),
        port=8080,
        schemes=[Scheme.HTTP],
        anonymity=AnonymityLevel.UNKNOWN,
    )

    result = await pv.validate_proxy(p)
    assert result.is_valid is True
    assert result.target_results is not None
    assert len(result.target_results) == 2


def test_target_definition_validation():
    """Test TargetDefinition model validation."""
    # Test TargetDefinition model validation with minimal required parameters
    target = TargetDefinition(target_id="test_target", url="https://example.com")
    assert target.target_id == "test_target"
    assert target.url == "https://example.com"
    assert target.display_name == "test_target"

    # Target with name
    target_with_name = TargetDefinition(
        target_id="api_target", url="https://api.example.com", name="Example API"
    )
    assert target_with_name.display_name == "Example API"

    # Invalid URL should raise validation error
    with pytest.raises(Exception):
        TargetDefinition(target_id="invalid", url="not-a-url")

    # Invalid target_id should raise validation error
    with pytest.raises(Exception):
        TargetDefinition(target_id="invalid id with spaces!", url="https://example.com")


# ============================================================================
# VALIDATION RESULT HEALTH SCORE TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_validation_result_health_score():
    """Test ValidationResult health_score property calculations."""
    now = datetime.now(timezone.utc)
    proxy = Proxy(
        host="192.0.2.1",
        ip=ip_address("192.0.2.1"),
        port=8080,
        schemes=[Scheme.HTTP],
        credentials=None,
        metrics=None,
        capabilities=None,
        country_code="US",
        country=None,
        city=None,
        region=None,
        isp=None,
        organization=None,
        anonymity=AnonymityLevel.UNKNOWN,
        last_checked=now,
        response_time=None,
        source="test",
        status=ProxyStatus.ACTIVE,
        quality_score=None,
        blacklist_reason=None,
    )

    # Invalid proxy should have 0.0 health score
    invalid_result = ValidationResult(proxy=proxy, is_valid=False, timestamp=now)
    assert invalid_result.health_score == 0.0

    # Valid proxy with fast response should have high score
    fast_result = ValidationResult(
        proxy=proxy,
        is_valid=True,
        response_time=0.5,
        anonymity_detected=AnonymityLevel.ELITE,
        timestamp=now,
    )
    assert fast_result.health_score > 1.0  # Should get bonuses

    # Valid proxy with slow response should have lower score
    slow_result = ValidationResult(
        proxy=proxy,
        is_valid=True,
        response_time=12.0,
        anonymity_detected=AnonymityLevel.TRANSPARENT,
        timestamp=now,
    )
    assert slow_result.health_score < 0.5  # Should get penalties

    # Valid proxy with no response time should have base score
    base_result = ValidationResult(proxy=proxy, is_valid=True, response_time=None, timestamp=now)
    assert base_result.health_score == 1.0


# ============================================================================
# VALIDATION SUMMARY TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_validation_summary_properties():
    """Test ValidationSummary properties and calculations."""
    now = datetime.now(timezone.utc)

    # Create test proxies
    proxy1 = Proxy(
        host="192.0.2.1",
        ip=ip_address("192.0.2.1"),
        port=8080,
        schemes=[Scheme.HTTP],
        credentials=None,
        metrics=None,
        capabilities=None,
        country_code="US",
        country=None,
        city=None,
        region=None,
        isp=None,
        organization=None,
        anonymity=AnonymityLevel.UNKNOWN,
        last_checked=now,
        response_time=None,
        source="test",
        status=ProxyStatus.ACTIVE,
        quality_score=None,
        blacklist_reason=None,
    )
    proxy2 = Proxy(
        host="192.0.2.2",
        ip=ip_address("192.0.2.2"),
        port=3128,
        schemes=[Scheme.HTTP],
        credentials=None,
        metrics=None,
        capabilities=None,
        country_code="CA",
        country=None,
        city=None,
        region=None,
        isp=None,
        organization=None,
        anonymity=AnonymityLevel.UNKNOWN,
        last_checked=now,
        response_time=None,
        source="test",
        status=ProxyStatus.ACTIVE,
        quality_score=None,
        blacklist_reason=None,
    )
    proxy3 = Proxy(
        host="192.0.2.3",
        ip=ip_address("192.0.2.3"),
        port=1080,
        schemes=[Scheme.SOCKS5],
        credentials=None,
        metrics=None,
        capabilities=None,
        country_code="GB",
        country=None,
        city=None,
        region=None,
        isp=None,
        organization=None,
        anonymity=AnonymityLevel.UNKNOWN,
        last_checked=now,
        response_time=None,
        source="test",
        status=ProxyStatus.ACTIVE,
        quality_score=None,
        blacklist_reason=None,
    )

    # Create validation results
    valid_results = [
        ValidationResult(proxy=proxy1, is_valid=True, response_time=1.0, timestamp=now),
        ValidationResult(proxy=proxy2, is_valid=True, response_time=2.0, timestamp=now),
    ]

    failed_results = [
        ValidationResult(
            proxy=proxy3,
            is_valid=False,
            error_type=ValidationErrorType.CONNECTION_ERROR,
            timestamp=now,
        )
    ]

    summary = ValidationSummary(
        total_proxies=3,
        valid_proxy_results=valid_results,
        failed_proxy_results=failed_results,
        avg_response_time=1.5,
        min_response_time=1.0,
        max_response_time=2.0,
        success_rate=0.67,
        error_breakdown={ValidationErrorType.CONNECTION_ERROR: 1},
        validation_duration=5.0,
        timestamp=now,
    )

    # Test properties
    assert summary.valid_proxy_count == 2
    assert summary.failed_proxy_count == 1
    assert len(summary.valid_proxies) == 2
    assert summary.valid_proxies[0] == proxy1
    assert summary.valid_proxies[1] == proxy2

    # Test quality tier
    assert summary.quality_tier == "Basic"  # 0.67 success rate

    # Test different quality tiers
    premium_summary = ValidationSummary(
        total_proxies=10,
        valid_proxy_results=valid_results * 5,  # 10 valid results
        failed_proxy_results=[],
        success_rate=1.0,
    )
    assert premium_summary.quality_tier == "Premium"

    poor_summary = ValidationSummary(
        total_proxies=10,
        valid_proxy_results=[valid_results[0]],  # 1 valid result
        failed_proxy_results=failed_results * 9,  # 9 failed results
        success_rate=0.1,
    )
    assert poor_summary.quality_tier == "Poor"


# ============================================================================
# CIRCUIT BREAKER COMPREHENSIVE TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_circuit_breaker_closed_state():
    """Test circuit breaker in CLOSED state (normal operation)."""
    cb = CircuitBreaker(failure_threshold=3)

    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0

    # Successful calls should keep circuit closed
    async def success_func():
        return "success"

    result = await cb.call(success_func)
    assert result == "success"
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0


@pytest.mark.asyncio
async def test_circuit_breaker_failure_counting():
    """Test circuit breaker failure counting behavior."""
    cb = CircuitBreaker(failure_threshold=3)

    async def fail_func():
        raise httpx.ConnectError("Connection failed")

    # First failure
    with pytest.raises(httpx.ConnectError):
        await cb.call(fail_func)
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 1

    # Second failure
    with pytest.raises(httpx.ConnectError):
        await cb.call(fail_func)
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 2

    # Third failure - should open circuit
    with pytest.raises(httpx.ConnectError):
        await cb.call(fail_func)
    assert cb.state == CircuitState.OPEN
    assert cb.failure_count == 3


@pytest.mark.asyncio
async def test_circuit_breaker_open_state():
    """Test circuit breaker in OPEN state (blocking requests)."""
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1.0)

    async def fail_func():
        raise httpx.ConnectError("Connection failed")

    # Trigger failures to open circuit
    for _ in range(2):
        with pytest.raises(httpx.ConnectError):
            await cb.call(fail_func)

    assert cb.state == CircuitState.OPEN

    # Now all requests should be blocked
    async def any_func():
        return "should not execute"

    with pytest.raises(CircuitBreakerOpenError) as exc_info:
        await cb.call(any_func)

    assert "Circuit breaker is OPEN" in str(exc_info.value)
    assert "Failed 2 times" in str(exc_info.value)


@pytest.mark.asyncio
async def test_circuit_breaker_half_open_recovery():
    """Test circuit breaker HALF_OPEN state and recovery."""
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)  # Short timeout for testing

    async def fail_func():
        raise httpx.ConnectError("Connection failed")

    # Open the circuit
    for _ in range(2):
        with pytest.raises(httpx.ConnectError):
            await cb.call(fail_func)

    assert cb.state == CircuitState.OPEN

    # Wait for recovery timeout
    await asyncio.sleep(0.2)

    # Next call should transition to HALF_OPEN
    async def success_func():
        return "recovered"

    result = await cb.call(success_func)
    assert result == "recovered"
    assert cb.state == CircuitState.CLOSED  # Should close after successful call
    assert cb.failure_count == 0


@pytest.mark.asyncio
async def test_circuit_breaker_half_open_failure():
    """Test circuit breaker HALF_OPEN state handling additional failures."""
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)

    async def fail_func():
        raise httpx.ConnectError("Connection failed")

    # Open the circuit
    with pytest.raises(httpx.ConnectError):
        await cb.call(fail_func)

    assert cb.state == CircuitState.OPEN

    # Wait for recovery timeout
    await asyncio.sleep(0.2)

    # Failure in HALF_OPEN should go back to OPEN
    with pytest.raises(httpx.ConnectError):
        await cb.call(fail_func)

    assert cb.state == CircuitState.OPEN
    assert cb.failure_count == 2  # Should increment


@pytest.mark.asyncio
async def test_circuit_breaker_manual_reset():
    """Test manual circuit breaker reset."""
    cb = CircuitBreaker(failure_threshold=1)

    async def fail_func():
        raise httpx.ConnectError("Connection failed")

    # Open the circuit
    with pytest.raises(httpx.ConnectError):
        await cb.call(fail_func)

    assert cb.state == CircuitState.OPEN
    assert cb.failure_count == 1

    # Manual reset
    await cb.reset()

    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0

    # Should work normally after reset
    async def success_func():
        return "success after reset"

    result = await cb.call(success_func)
    assert result == "success after reset"


@pytest.mark.asyncio
async def test_circuit_breaker_custom_exceptions():
    """Test circuit breaker with custom expected exceptions."""
    cb = CircuitBreaker(failure_threshold=2, expected_exception=(httpx.HTTPError, ValueError))

    async def http_error_func():
        raise httpx.HTTPError("HTTP Error")

    async def value_error_func():
        raise ValueError("Value Error")

    async def runtime_error_func():
        raise RuntimeError("Runtime Error")

    # HTTP errors should be counted
    with pytest.raises(httpx.HTTPError):
        await cb.call(http_error_func)
    assert cb.failure_count == 1

    # Value errors should be counted
    with pytest.raises(ValueError):
        await cb.call(value_error_func)
    assert cb.failure_count == 2
    assert cb.state == CircuitState.OPEN

    # Runtime errors should not be counted (unexpected exception)
    # But circuit is already open, so should raise CircuitBreakerOpenError
    with pytest.raises(CircuitBreakerOpenError):
        await cb.call(runtime_error_func)


@pytest.mark.asyncio
async def test_circuit_breaker_concurrent_access():
    """Test circuit breaker thread safety with concurrent access."""
    cb = CircuitBreaker(failure_threshold=5)

    async def success_func(value):
        await asyncio.sleep(0.01)  # Small delay to test concurrency
        return f"success_{value}"

    # Run multiple concurrent operations
    tasks = [cb.call(success_func, i) for i in range(10)]
    concurrent_results = await asyncio.gather(*tasks)

    assert len(concurrent_results) == 10
    assert all("success_" in result for result in concurrent_results)
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0


# ============================================================================
# ADVANCED PROXY VALIDATOR TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_proxy_validator_multiple_test_urls():
    """Test ProxyValidator with multiple test URLs."""
    test_urls = [
        "https://httpbin.org/ip",
        "https://ifconfig.me/ip",
        "https://api.ipify.org?format=json",
    ]

    pv = ProxyValidator(test_urls=test_urls)

    assert len(pv.test_urls) == 3
    assert pv.primary_test_url == "https://httpbin.org/ip"
    assert pv.test_url == "https://httpbin.org/ip"  # Backward compatibility

    # Test URL setter backward compatibility
    pv.test_url = "https://custom.test.url"
    assert pv.primary_test_url == "https://custom.test.url"
    assert pv.test_urls[0] == "https://custom.test.url"


@pytest.mark.asyncio
async def test_proxy_validator_circuit_breaker_integration(monkeypatch):
    """Test ProxyValidator integration with circuit breaker."""
    pv = ProxyValidator(circuit_breaker_threshold=2)

    import proxywhirl.validator as validator

    # Mock client that always fails
    failing_client = DummyAsyncClient(should_fail=True)
    monkeypatch.setattr(
        validator,
        "httpx",
        types.SimpleNamespace(
            AsyncClient=lambda **_: failing_client,  # type: ignore[misc]
            HTTPError=httpx.HTTPError,
            ConnectError=httpx.ConnectError,
            ProxyError=httpx.ProxyError,
            Timeout=httpx.Timeout,
            Limits=httpx.Limits,
            Request=httpx.Request,
            Response=httpx.Response,
            ReadTimeout=httpx.ReadTimeout,
            WriteTimeout=httpx.WriteTimeout,
            ConnectTimeout=httpx.ConnectTimeout,
            PoolTimeout=httpx.PoolTimeout,
        ),
    )

    proxy = Proxy(
        host="192.0.2.1",
        ip=ip_address("192.0.2.1"),
        port=8080,
        schemes=[Scheme.HTTP],
        credentials=None,
        metrics=None,
        capabilities=None,
        country_code="US",
        country=None,
        city=None,
        region=None,
        isp=None,
        organization=None,
        anonymity=AnonymityLevel.UNKNOWN,
        last_checked=datetime.now(timezone.utc),
        response_time=None,
        source="test",
        status=ProxyStatus.ACTIVE,
        quality_score=None,
        blacklist_reason=None,
    )

    # First two validations should fail normally
    result1 = await pv.validate_proxy(proxy)
    assert result1.is_valid is False
    assert result1.error_type != ValidationErrorType.CIRCUIT_BREAKER_OPEN

    result2 = await pv.validate_proxy(proxy)
    assert result2.is_valid is False
    assert result2.error_type != ValidationErrorType.CIRCUIT_BREAKER_OPEN

    # Third validation should trigger circuit breaker
    result3 = await pv.validate_proxy(proxy)
    assert result3.is_valid is False
    assert result3.error_type == ValidationErrorType.CIRCUIT_BREAKER_OPEN
    assert "Circuit breaker is OPEN" in result3.error_message


@pytest.mark.asyncio
async def test_proxy_validator_validation_history():
    """Test ProxyValidator validation history tracking."""
    pv = ProxyValidator()

    import proxywhirl.validator as validator

    with patch.object(
        validator,
        "httpx",
        types.SimpleNamespace(
            AsyncClient=lambda **_: DummyAsyncClient(should_fail=False),  # type: ignore[misc]
            HTTPError=httpx.HTTPError,
            ConnectError=httpx.ConnectError,
            ProxyError=httpx.ProxyError,
            Timeout=httpx.Timeout,
            Limits=httpx.Limits,
            Request=httpx.Request,
            Response=httpx.Response,
            ReadTimeout=httpx.ReadTimeout,
            WriteTimeout=httpx.WriteTimeout,
            ConnectTimeout=httpx.ConnectTimeout,
            PoolTimeout=httpx.PoolTimeout,
        ),
    ):
        proxy1 = Proxy(
            host="192.0.2.1",
            ip=ip_address("192.0.2.1"),
            port=8080,
            schemes=[Scheme.HTTP],
            credentials=None,
            metrics=None,
            capabilities=None,
            country_code="US",
            country=None,
            city=None,
            region=None,
            isp=None,
            organization=None,
            anonymity=AnonymityLevel.UNKNOWN,
            last_checked=datetime.now(timezone.utc),
            response_time=None,
            source="test",
            status=ProxyStatus.ACTIVE,
            quality_score=None,
            blacklist_reason=None,
        )
        proxy2 = Proxy(
            host="192.0.2.2",
            ip=ip_address("192.0.2.2"),
            port=3128,
            schemes=[Scheme.HTTP],
            credentials=None,
            metrics=None,
            capabilities=None,
            country_code="CA",
            country=None,
            city=None,
            region=None,
            isp=None,
            organization=None,
            anonymity=AnonymityLevel.UNKNOWN,
            last_checked=datetime.now(timezone.utc),
            response_time=None,
            source="test",
            status=ProxyStatus.ACTIVE,
            quality_score=None,
            blacklist_reason=None,
        )

        # Validate proxies
        await pv.validate_proxy(proxy1)
        await pv.validate_proxy(proxy2)

        # Check metrics
        assert pv._total_validations == 2
        assert pv._successful_validations == 2
        assert len(pv._validation_history) == 2


@pytest.mark.asyncio
async def test_proxy_validator_concurrency_limiting():
    """Test ProxyValidator semaphore-based concurrency limiting."""
    pv = ProxyValidator(max_concurrent=2)

    assert pv.semaphore._value == 2  # Should have capacity of 2

    # This test verifies the semaphore exists and is properly configured
    # Actual concurrency testing would require more complex mocking


@pytest.mark.asyncio
async def test_proxy_validator_quality_levels():
    """Test QualityLevel enum values."""
    assert QualityLevel.BASIC.value == "basic"
    assert QualityLevel.STANDARD.value == "standard"
    assert QualityLevel.THOROUGH.value == "thorough"


@pytest.mark.asyncio
async def test_proxy_validator_error_categorization(monkeypatch):
    """Test ProxyValidator error categorization."""
    pv = ProxyValidator()

    import proxywhirl.validator as validator

    # Test connection error
    connection_client = Mock()
    connection_client.__aenter__ = AsyncMock(side_effect=httpx.ConnectError("Connection failed"))
    connection_client.__aexit__ = AsyncMock(return_value=None)

    monkeypatch.setattr(
        validator,
        "httpx",
        types.SimpleNamespace(
            AsyncClient=lambda **_: connection_client,  # type: ignore[misc]
            HTTPError=httpx.HTTPError,
            ConnectError=httpx.ConnectError,
            ProxyError=httpx.ProxyError,
            Timeout=httpx.Timeout,
            Limits=httpx.Limits,
            Request=httpx.Request,
            Response=httpx.Response,
            ReadTimeout=httpx.ReadTimeout,
            WriteTimeout=httpx.WriteTimeout,
            ConnectTimeout=httpx.ConnectTimeout,
            PoolTimeout=httpx.PoolTimeout,
        ),
    )

    proxy = Proxy(
        host="192.0.2.1",
        ip=ip_address("192.0.2.1"),
        port=8080,
        schemes=[Scheme.HTTP],
        credentials=None,
        metrics=None,
        capabilities=None,
        country_code="US",
        country=None,
        city=None,
        region=None,
        isp=None,
        organization=None,
        anonymity=AnonymityLevel.UNKNOWN,
        last_checked=datetime.now(timezone.utc),
        response_time=None,
        source="test",
        status=ProxyStatus.ACTIVE,
        quality_score=None,
        blacklist_reason=None,
    )

    result = await pv.validate_proxy(proxy)
    assert result.is_valid is False
    assert result.error_type == ValidationErrorType.CONNECTION_ERROR

    # Test timeout error
    timeout_client = Mock()
    timeout_client.__aenter__ = AsyncMock(side_effect=asyncio.TimeoutError("Request timed out"))
    timeout_client.__aexit__ = AsyncMock(return_value=None)

    monkeypatch.setattr(
        validator,
        "httpx",
        types.SimpleNamespace(
            AsyncClient=lambda **_: timeout_client,  # type: ignore[misc]
            HTTPError=httpx.HTTPError,
            ConnectError=httpx.ConnectError,
            ProxyError=httpx.ProxyError,
            Timeout=httpx.Timeout,
            Limits=httpx.Limits,
            Request=httpx.Request,
            Response=httpx.Response,
            ReadTimeout=httpx.ReadTimeout,
            WriteTimeout=httpx.WriteTimeout,
            ConnectTimeout=httpx.ConnectTimeout,
            PoolTimeout=httpx.PoolTimeout,
        ),
    )

    result = await pv.validate_proxy(proxy)
    assert result.is_valid is False
    assert result.error_type == ValidationErrorType.TIMEOUT


@pytest.mark.asyncio
async def test_target_validation_result_properties():
    """Test TargetValidationResult dataclass properties."""
    now = datetime.now(timezone.utc)

    result = TargetValidationResult(
        target_id="test_target",
        target_url="https://test.example.com",
        is_valid=True,
        response_time=1.5,
        status_code=200,
        error_type=None,
        error_message=None,
        timestamp=now,
    )

    assert result.target_id == "test_target"
    assert result.target_url == "https://test.example.com"
    assert result.is_valid is True
    assert result.response_time == 1.5
    assert result.status_code == 200
    assert result.error_type is None
    assert result.error_message is None
    assert result.timestamp == now
    assert result.target_url == "https://test.example.com"
    assert result.is_valid is True
    assert result.response_time == 1.5
    assert result.status_code == 200
    assert result.error_type is None
    assert result.error_message is None
    assert result.timestamp == now
    assert result.error_message is None
    assert result.timestamp == now
