"""
Pytest configuration and shared fixtures for ProxyWhirl tests.
"""

from collections.abc import Generator

import httpx
import pytest


@pytest.fixture
def sample_proxy_urls() -> list[str]:
    """Sample proxy URLs for testing."""
    return [
        "http://proxy1.example.com:8080",
        "http://proxy2.example.com:8080",
        "http://proxy3.example.com:8080",
    ]


@pytest.fixture
def sample_authenticated_proxy_urls() -> list[str]:
    """Sample authenticated proxy URLs for testing."""
    return [
        "http://user1:pass1@proxy1.example.com:8080",
        "http://user2:pass2@proxy2.example.com:8080",
    ]


@pytest.fixture
def mock_httpx_client() -> Generator[httpx.Client, None, None]:
    """Mock httpx client for testing."""
    client = httpx.Client()
    yield client
    client.close()


@pytest.fixture
def mock_async_httpx_client() -> Generator[httpx.AsyncClient, None, None]:
    """Mock async httpx client for testing."""
    client = httpx.AsyncClient()
    yield client
    # Note: In actual async tests, we'd use async context manager


@pytest.fixture
def sample_retry_policy():
    """Sample retry policy for testing."""
    from proxywhirl.retry_policy import BackoffStrategy, RetryPolicy
    
    return RetryPolicy(
        max_attempts=3,
        backoff_strategy=BackoffStrategy.EXPONENTIAL,
        base_delay=1.0,
        multiplier=2.0,
        max_backoff_delay=30.0,
        jitter=False,
        retry_status_codes=[502, 503, 504],
        timeout=None,
        retry_non_idempotent=False,
    )


@pytest.fixture
def sample_circuit_breaker():
    """Sample circuit breaker for testing."""
    from proxywhirl.circuit_breaker import CircuitBreaker
    
    return CircuitBreaker(
        proxy_id="test-proxy-1",
        failure_threshold=5,
        window_duration=60.0,
        timeout_duration=30.0,
    )


pytest_plugins = ["pytest_asyncio"]
