"""Unit tests for HTTP request validation."""

import httpx
import respx

from proxywhirl.fetchers import ProxyValidator
from proxywhirl.models import ValidationLevel


class TestHTTPValidation:
    """Test HTTP request validation."""

    async def test_http_request_success(self) -> None:
        """T011: Test successful HTTP request through proxy."""
        validator = ProxyValidator(level=ValidationLevel.STANDARD)

        # Use respx to mock the HTTP request (test without proxy for unit test)
        with respx.mock:
            respx.get(validator.test_url).mock(return_value=httpx.Response(200))

            result = await validator._validate_http_request()  # No proxy for unit test

            assert result is True

    async def test_http_request_timeout(self) -> None:
        """T012: Test HTTP request timeout."""
        validator = ProxyValidator(level=ValidationLevel.STANDARD, timeout=2.0)

        # Use respx to mock timeout
        with respx.mock:
            respx.get(validator.test_url).mock(
                side_effect=httpx.TimeoutException("Request timed out")
            )

            result = await validator._validate_http_request()

            assert result is False

    async def test_http_request_invalid_response(self) -> None:
        """T013: Test HTTP request with invalid response."""
        validator = ProxyValidator(level=ValidationLevel.STANDARD)

        # Use respx to mock 500 error
        with respx.mock:
            respx.get(validator.test_url).mock(return_value=httpx.Response(500))

            result = await validator._validate_http_request()

            assert result is False

    async def test_http_request_connection_error(self) -> None:
        """Test HTTP request with connection error."""
        validator = ProxyValidator(level=ValidationLevel.STANDARD)

        # Use respx to mock connection error
        with respx.mock:
            respx.get(validator.test_url).mock(side_effect=httpx.ConnectError("Cannot connect"))

            result = await validator._validate_http_request()

            assert result is False

    async def test_http_request_network_error(self) -> None:
        """Test HTTP request with network error."""
        validator = ProxyValidator(level=ValidationLevel.STANDARD)

        # Use respx to mock network error
        with respx.mock:
            respx.get(validator.test_url).mock(
                side_effect=httpx.NetworkError("Network unreachable")
            )

            result = await validator._validate_http_request()

            assert result is False
