"""
Pytest configuration and shared fixtures for ProxyWhirl tests.

This module provides:
- Polyfactory factories for generating test data from Pydantic models
- Faker fixtures for generating realistic test data
- RESPX fixtures for mocking HTTP requests
- Syrupy configuration for snapshot testing
- httpx client fixtures for sync/async testing
"""

from collections.abc import AsyncGenerator, Generator
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import httpx
import pytest
import respx
from faker import Faker
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import SecretStr

from proxywhirl.models import (
    HealthStatus,
    Proxy,
    ProxyPool,
    ProxySource,
    SelectionContext,
    Session,
    StrategyConfig,
)

# ============================================================================
# POLYFACTORY FACTORIES
# ============================================================================


class ProxyFactory(ModelFactory[Proxy]):
    """Factory for generating Proxy instances with realistic test data."""

    __model__ = Proxy
    __randomize_collection_length__ = False

    # Override specific fields with sensible defaults
    id = lambda: uuid4()  # noqa: E731
    url = (
        lambda: f"http://proxy{Faker().random_int(1, 999)}.example.com:{Faker().random_int(1024, 65535)}"
    )  # noqa: E731
    protocol = lambda: Faker().random_element(["http", "https", "socks5"])  # noqa: E731
    health_status = lambda: HealthStatus.UNKNOWN  # noqa: E731
    source = lambda: ProxySource.FETCHED  # noqa: E731
    tags = lambda: set()  # noqa: E731
    metadata = lambda: {}  # noqa: E731
    # Ensure numeric fields have valid non-negative values
    latency_ms = lambda: Faker().pyfloat(min_value=0, max_value=5000)  # noqa: E731
    success_rate = lambda: Faker().pyfloat(min_value=0, max_value=1)  # noqa: E731
    ema_response_time_ms = lambda: Faker().pyfloat(min_value=0, max_value=5000)  # noqa: E731
    average_response_time_ms = lambda: Faker().pyfloat(min_value=0, max_value=5000)  # noqa: E731
    total_requests = lambda: Faker().random_int(min=0, max=1000)  # noqa: E731
    total_successes = lambda: Faker().random_int(min=0, max=1000)  # noqa: E731
    total_failures = lambda: Faker().random_int(min=0, max=100)  # noqa: E731
    consecutive_failures = lambda: Faker().random_int(min=0, max=10)  # noqa: E731
    # Credentials must be both None or both set - default to None
    username = None
    password = None

    @classmethod
    def healthy(cls, **kwargs: Any) -> Proxy:
        """Create a healthy proxy."""
        return cls.build(
            health_status=HealthStatus.HEALTHY,
            total_requests=Faker().random_int(10, 100),
            total_successes=Faker().random_int(8, 100),
            total_failures=Faker().random_int(0, 2),
            consecutive_failures=0,
            average_response_time_ms=Faker().pyfloat(min_value=50, max_value=500),
            **kwargs,
        )

    @classmethod
    def unhealthy(cls, **kwargs: Any) -> Proxy:
        """Create an unhealthy proxy."""
        return cls.build(
            health_status=HealthStatus.UNHEALTHY,
            total_failures=Faker().random_int(5, 20),
            consecutive_failures=Faker().random_int(3, 5),
            **kwargs,
        )

    @classmethod
    def with_auth(cls, username: str = "user", password: str = "pass", **kwargs: Any) -> Proxy:
        """Create a proxy with authentication credentials."""
        return cls.build(
            username=SecretStr(username),
            password=SecretStr(password),
            **kwargs,
        )

    @classmethod
    def with_geo(cls, country_code: str = "US", region: str | None = None, **kwargs: Any) -> Proxy:
        """Create a proxy with geo-location data."""
        return cls.build(
            country_code=country_code,
            region=region or Faker().state(),
            **kwargs,
        )


class ProxyPoolFactory(ModelFactory[ProxyPool]):
    """Factory for generating ProxyPool instances."""

    __model__ = ProxyPool

    name = lambda: f"pool_{Faker().slug()}"  # noqa: E731
    proxies = lambda: []  # noqa: E731
    max_pool_size = lambda: 100  # noqa: E731

    @classmethod
    def with_proxies(cls, count: int = 5, **kwargs: Any) -> ProxyPool:
        """Create a pool with the specified number of proxies."""
        proxies = [ProxyFactory.build() for _ in range(count)]
        return cls.build(proxies=proxies, **kwargs)

    @classmethod
    def with_healthy_proxies(cls, count: int = 5, **kwargs: Any) -> ProxyPool:
        """Create a pool with healthy proxies."""
        proxies = [ProxyFactory.healthy() for _ in range(count)]
        return cls.build(proxies=proxies, **kwargs)


class StrategyConfigFactory(ModelFactory[StrategyConfig]):
    """Factory for generating StrategyConfig instances."""

    __model__ = StrategyConfig


class SelectionContextFactory(ModelFactory[SelectionContext]):
    """Factory for generating SelectionContext instances."""

    __model__ = SelectionContext

    @classmethod
    def with_session(cls, session_id: str | None = None, **kwargs: Any) -> SelectionContext:
        """Create a context with session ID."""
        return cls.build(
            session_id=session_id or str(uuid4()),
            **kwargs,
        )

    @classmethod
    def with_failed_proxies(cls, proxy_ids: list[str], **kwargs: Any) -> SelectionContext:
        """Create a context with failed proxy IDs for retry logic."""
        return cls.build(
            failed_proxy_ids=proxy_ids,
            attempt_number=len(proxy_ids) + 1,
            **kwargs,
        )


class SessionFactory(ModelFactory[Session]):
    """Factory for generating Session instances."""

    __model__ = Session

    session_id = lambda: str(uuid4())  # noqa: E731
    proxy_id = lambda: str(uuid4())  # noqa: E731

    @classmethod
    def expired(cls, **kwargs: Any) -> Session:
        """Create an expired session."""
        past = datetime.now(timezone.utc) - timedelta(hours=1)
        return cls.build(
            created_at=past - timedelta(hours=1),
            expires_at=past,
            **kwargs,
        )

    @classmethod
    def active(cls, duration_seconds: int = 300, **kwargs: Any) -> Session:
        """Create an active session with specified TTL."""
        now = datetime.now(timezone.utc)
        return cls.build(
            created_at=now,
            expires_at=now + timedelta(seconds=duration_seconds),
            last_used_at=now,
            **kwargs,
        )


# ============================================================================
# FAKER FIXTURES
# ============================================================================


@pytest.fixture
def faker() -> Faker:
    """Provide a seeded Faker instance for reproducible test data."""
    fake = Faker()
    Faker.seed(12345)  # Seed for reproducibility
    return fake


@pytest.fixture
def fake_proxy_url(faker: Faker) -> str:
    """Generate a fake proxy URL."""
    return f"http://proxy{faker.random_int(1, 999)}.example.com:{faker.random_int(1024, 65535)}"


@pytest.fixture
def fake_proxy_urls(faker: Faker) -> list[str]:
    """Generate a list of fake proxy URLs."""
    return [f"http://proxy{i}.example.com:{faker.random_int(1024, 65535)}" for i in range(1, 6)]


# ============================================================================
# RESPX FIXTURES (HTTP MOCKING)
# ============================================================================


@pytest.fixture
def respx_mock() -> Generator[respx.MockRouter, None, None]:
    """Provide a RESPX mock router for HTTP request mocking.

    Usage:
        def test_http_call(respx_mock):
            respx_mock.get("https://api.example.com/data").respond(json={"key": "value"})
            # ... make HTTP request
    """
    with respx.mock(assert_all_called=False) as router:
        yield router


@pytest.fixture
async def respx_mock_async() -> AsyncGenerator[respx.MockRouter, None]:
    """Provide a RESPX mock router for async HTTP request mocking."""
    async with respx.mock(assert_all_called=False) as router:
        yield router


@pytest.fixture
def mock_proxy_validation(respx_mock: respx.MockRouter) -> respx.MockRouter:
    """Set up mock responses for proxy validation endpoints."""
    # Mock common proxy validation endpoints
    respx_mock.get("http://httpbin.org/ip").respond(json={"origin": "1.2.3.4"})
    respx_mock.get("https://httpbin.org/ip").respond(json={"origin": "1.2.3.4"})
    respx_mock.get("http://api.ipify.org").respond(text="1.2.3.4")
    respx_mock.get("https://api.ipify.org").respond(text="1.2.3.4")
    return respx_mock


@pytest.fixture
def mock_proxy_sources(respx_mock: respx.MockRouter) -> respx.MockRouter:
    """Set up mock responses for proxy source fetching."""
    # Mock a simple proxy list response
    proxy_list = "1.2.3.4:8080\n5.6.7.8:3128\n9.10.11.12:8888"
    respx_mock.get(url__regex=r".*proxy.*list.*").respond(text=proxy_list)
    return respx_mock


# ============================================================================
# HTTPX CLIENT FIXTURES
# ============================================================================


@pytest.fixture
def httpx_client() -> Generator[httpx.Client, None, None]:
    """Provide a configured httpx Client for sync testing."""
    client = httpx.Client(timeout=10.0)
    yield client
    client.close()


@pytest.fixture
async def async_httpx_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Provide a configured httpx AsyncClient for async testing."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        yield client


# ============================================================================
# PROXY FIXTURES (CONVENIENCE)
# ============================================================================


@pytest.fixture
def sample_proxy_urls() -> list[str]:
    """Sample proxy URLs for testing (backwards compatibility)."""
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
def sample_proxy() -> Proxy:
    """Provide a single sample Proxy instance."""
    return ProxyFactory.build()


@pytest.fixture
def sample_healthy_proxy() -> Proxy:
    """Provide a healthy Proxy instance."""
    return ProxyFactory.healthy()


@pytest.fixture
def sample_proxy_pool() -> ProxyPool:
    """Provide a ProxyPool with 5 proxies."""
    return ProxyPoolFactory.with_proxies(count=5)


@pytest.fixture
def sample_healthy_pool() -> ProxyPool:
    """Provide a ProxyPool with 5 healthy proxies."""
    return ProxyPoolFactory.with_healthy_proxies(count=5)


# ============================================================================
# RETRY AND CIRCUIT BREAKER FIXTURES
# ============================================================================


@pytest.fixture
def sample_retry_policy():
    """Sample retry policy for testing."""
    from proxywhirl.retry import BackoffStrategy, RetryPolicy

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


# ============================================================================
# SYRUPY CONFIGURATION
# ============================================================================


@pytest.fixture
def snapshot_json(snapshot):
    """Provide snapshot fixture configured for JSON serialization."""
    return snapshot.use_extension(extension_class=None)


# ============================================================================
# HYPOTHESIS CONFIGURATION
# ============================================================================

# Register hypothesis profiles
from hypothesis import Phase, Verbosity, settings

settings.register_profile(
    "ci",
    max_examples=100,
    deadline=None,
    suppress_health_check=[],
)
settings.register_profile(
    "dev",
    max_examples=10,
    deadline=None,
    verbosity=Verbosity.verbose,
)
settings.register_profile(
    "debug",
    max_examples=10,
    deadline=None,
    verbosity=Verbosity.verbose,
    phases=[Phase.explicit, Phase.reuse, Phase.generate],
)

# Load profile from environment or use dev as default
import os

settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "dev"))


# ============================================================================
# PYTEST PLUGINS
# ============================================================================

pytest_plugins = ["pytest_asyncio"]
