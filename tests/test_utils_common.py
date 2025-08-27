"""Common test utilities for ProxyWhirl test suite.

This module provides reusable patterns, fixtures, and utilities for testing
async code, mocking external dependencies, and creating test data.
"""

import asyncio
from datetime import datetime, timezone
from ipaddress import ip_address
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, Mock

import httpx
import pytest

from proxywhirl.models import (
    AnonymityLevel,
    Proxy,
    Scheme,
    ValidationErrorType,
)
from proxywhirl.validator import ValidationResult


class AsyncTestUtils:
    """Utilities for testing async code."""

    @staticmethod
    async def run_with_timeout(coro, timeout: float = 5.0):
        """Run coroutine with timeout."""
        return await asyncio.wait_for(coro, timeout=timeout)

    @staticmethod
    def create_async_mock(return_value=None, side_effect=None):
        """Create an AsyncMock with optional return value or side effect."""
        mock = AsyncMock()
        if return_value is not None:
            mock.return_value = return_value
        if side_effect is not None:
            mock.side_effect = side_effect
        return mock

    @staticmethod
    def create_async_context_manager(return_value=None, side_effect=None):
        """Create a mock async context manager."""
        mock = MagicMock()
        mock.__aenter__ = AsyncMock(return_value=return_value or mock)
        mock.__aexit__ = AsyncMock(return_value=None)
        if side_effect:
            mock.__aenter__.side_effect = side_effect
        return mock


class HttpxMockUtils:
    """Utilities for mocking httpx requests."""

    @staticmethod
    def create_mock_response(
        status_code: int = 200,
        text: str = "Success",
        json_data: Optional[Dict[str, Any]] = None,
        raises: Optional[Exception] = None,
    ) -> Mock:
        """Create a mock httpx.Response."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = status_code
        mock_response.text = text
        mock_response.headers = {"Content-Type": "text/plain"}  # Add headers attribute
        mock_response.json.return_value = json_data or {"success": True}

        if raises:
            mock_response.raise_for_status.side_effect = raises
        else:
            mock_response.raise_for_status.return_value = None

        return mock_response

    @staticmethod
    def create_mock_client(response_config: Optional[Dict[str, Any]] = None) -> MagicMock:
        """Create a mock httpx.AsyncClient."""
        config = response_config or {}
        response = HttpxMockUtils.create_mock_response(**config)

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=response)
        mock_client.post = AsyncMock(return_value=response)

        return mock_client

    @staticmethod
    def create_error_scenarios() -> Dict[str, Exception]:
        """Create common HTTP error scenarios."""
        return {
            "timeout": httpx.TimeoutException("Request timed out"),
            "connection_error": httpx.ConnectError("Connection failed"),
            "http_404": httpx.HTTPStatusError(
                "404 Not Found", request=Mock(), response=Mock(status_code=404)
            ),
            "http_500": httpx.HTTPStatusError(
                "500 Internal Server Error", request=Mock(), response=Mock(status_code=500)
            ),
        }


class ProxyTestDataFactory:
    """Factory for creating test proxy data."""

    @staticmethod
    def create_proxy(
        host: str = "192.168.1.1",
        port: int = 8080,
        schemes: Optional[List[Scheme]] = None,
        country_code: str = "US",
        anonymity: AnonymityLevel = AnonymityLevel.ELITE,
        response_time: Optional[float] = 0.5,
    ) -> Proxy:
        """Create a test proxy with sensible defaults."""
        if schemes is None:
            schemes = [Scheme.HTTP]

        return Proxy(
            host=host,
            ip=ip_address(host),
            port=port,
            schemes=schemes,
        )

    @staticmethod
    def create_proxy_list(count: int = 5) -> List[Proxy]:
        """Create a list of test proxies."""
        proxies = []
        base_ip = "192.168.1"

        for i in range(count):
            proxy = ProxyTestDataFactory.create_proxy(
                host=f"{base_ip}.{i + 1}", port=8080 + i, response_time=0.1 + (i * 0.1)
            )
            proxies.append(proxy)

        return proxies

    @staticmethod
    def create_proxy_text_data() -> str:
        """Create proxy data in text format (IP:PORT per line)."""
        return "\n".join(
            ["192.168.1.1:8080", "192.168.1.2:3128", "192.168.1.3:1080", "192.168.1.4:8000"]
        )

    @staticmethod
    def create_proxy_json_data() -> Dict:
        """Create proxy data in JSON format."""
        return {
            "proxies": [
                {"ip": "192.168.1.1", "port": 8080, "protocol": "http", "country": "US"},
                {"ip": "192.168.1.2", "port": 3128, "protocol": "http", "country": "GB"},
            ]
        }


class ValidationTestUtils:
    """Utilities for testing proxy validation."""

    @staticmethod
    def create_mock_validator(is_valid: bool = True, response_time: float = 0.5):
        """Create a mock ProxyValidator."""
        mock_validator = MagicMock()
        # Create a minimal proxy for validation result
        test_proxy = ProxyTestDataFactory.create_proxy()
        result = ValidationResult(
            proxy=test_proxy,
            is_valid=is_valid,
            response_time=response_time,
            error_type=None if is_valid else ValidationErrorType.UNKNOWN,
            error_message=None if is_valid else "Validation failed",
            status_code=200 if is_valid else None,
            test_url="https://httpbin.org/ip",
            timestamp=datetime.now(timezone.utc),
        )

        mock_validator.validate_proxy = AsyncMock(return_value=result)
        return mock_validator

    @staticmethod
    def create_validation_scenarios():
        """Create various validation scenarios."""
        return {
            "success": {"is_valid": True, "response_time": 0.5},
            "timeout": {"is_valid": False, "response_time": None, "error": "Timeout"},
            "connection_failed": {
                "is_valid": False,
                "response_time": None,
                "error": "Connection failed",
            },
            "slow_response": {"is_valid": True, "response_time": 5.0},
        }


# Pytest fixtures using the utilities above
@pytest.fixture
def async_utils():
    """Provide async testing utilities."""
    return AsyncTestUtils()


@pytest.fixture
def httpx_mock_utils():
    """Provide httpx mocking utilities."""
    return HttpxMockUtils()


@pytest.fixture
def proxy_factory():
    """Provide proxy test data factory."""
    return ProxyTestDataFactory()


@pytest.fixture
def validation_utils():
    """Provide validation testing utilities."""
    return ValidationTestUtils()


@pytest.fixture
def mock_successful_httpx_client(httpx_mock_utils):
    """Mock httpx client that returns successful responses."""
    return httpx_mock_utils.create_mock_client()


@pytest.fixture
def mock_error_httpx_client(httpx_mock_utils):
    """Mock httpx client that raises connection errors."""
    return httpx_mock_utils.create_mock_client({"raises": httpx.ConnectError("Connection failed")})


# Common test decorators and markers
def async_test(func):
    """Mark function as async test with proper asyncio handling."""
    return pytest.mark.asyncio(func)


def integration_test(func):
    """Mark function as integration test."""
    return pytest.mark.integration(func)


def e2e_test(func):
    """Mark function as end-to-end test."""
    return pytest.mark.e2e(func)
    return pytest.mark.e2e(func)
