"""
Pytest configuration and shared fixtures for ProxyWhirl tests.

This module provides:
- Polyfactory factories for generating test data from Pydantic models
- Faker fixtures for generating realistic test data
- RESPX fixtures for mocking HTTP requests
- Syrupy configuration for snapshot testing
- httpx client fixtures for sync/async testing
"""

from __future__ import annotations

import os
import socket
from collections.abc import AsyncGenerator, Generator
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import httpx
import pytest
import respx
from cryptography.fernet import Fernet
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
from proxywhirl.rotator import ProxyWhirl

# Durable crypto policy refuses ephemeral keys. Provide a stable test-session key
# so cache/storage suites can construct CredentialEncryptor without inventing keys
# inside production code.
if not os.environ.get("PROXYWHIRL_CACHE_ENCRYPTION_KEY"):
    os.environ["PROXYWHIRL_CACHE_ENCRYPTION_KEY"] = Fernet.generate_key().decode()

# ============================================================================
# POLYFACTORY FACTORIES
# ============================================================================

# Shared Faker instance — constructing Faker() per field made bulk ProxyFactory.build()
# slow enough to flake under full-suite pytest-timeout pressure.
_FAKER = Faker()
_PROXY_URL_COUNTER = 0


def _next_proxy_url() -> str:
    """Deterministic unique proxy URL without per-call Faker construction."""
    global _PROXY_URL_COUNTER
    _PROXY_URL_COUNTER += 1
    host_n = (_PROXY_URL_COUNTER % 999) + 1
    port = 1024 + (_PROXY_URL_COUNTER % 64511)
    return f"http://proxy{host_n}.example.com:{port}"


class ProxyFactory(ModelFactory[Proxy]):
    """Factory for generating Proxy instances with realistic test data."""

    __model__ = Proxy
    __randomize_collection_length__ = False

    # Override specific fields with sensible defaults
    id = lambda: uuid4()
    url = _next_proxy_url
    protocol = "http"
    health_status = HealthStatus.UNKNOWN
    source = ProxySource.FETCHED
    # Prevent polyfactory from inventing random HttpUrl values for optional fields
    source_url = None
    tags = lambda: set()
    metadata = lambda: {}
    # Ensure numeric fields have valid non-negative values (shared Faker)
    latency_ms = lambda: _FAKER.pyfloat(min_value=0, max_value=5000)
    success_rate = lambda: _FAKER.pyfloat(min_value=0, max_value=1)
    ema_response_time_ms = lambda: _FAKER.pyfloat(min_value=0, max_value=5000)
    average_response_time_ms = lambda: _FAKER.pyfloat(min_value=0, max_value=5000)
    total_requests = lambda: _FAKER.random_int(min=0, max=1000)
    total_successes = lambda: _FAKER.random_int(min=0, max=1000)
    total_failures = lambda: _FAKER.random_int(min=0, max=100)
    consecutive_failures = lambda: _FAKER.random_int(min=0, max=10)
    # Credentials must be both None or both set - default to None
    username = None
    password = None

    @classmethod
    def healthy(cls, **kwargs: Any) -> Proxy:
        """Create a healthy proxy."""
        return cls.build(
            health_status=HealthStatus.HEALTHY,
            total_requests=_FAKER.random_int(10, 100),
            total_successes=_FAKER.random_int(8, 100),
            total_failures=_FAKER.random_int(0, 2),
            consecutive_failures=0,
            average_response_time_ms=_FAKER.pyfloat(min_value=50, max_value=500),
            **kwargs,
        )

    @classmethod
    def unhealthy(cls, **kwargs: Any) -> Proxy:
        """Create an unhealthy proxy."""
        return cls.build(
            health_status=HealthStatus.UNHEALTHY,
            total_failures=_FAKER.random_int(5, 20),
            consecutive_failures=_FAKER.random_int(3, 5),
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
            region=region or _FAKER.state(),
            **kwargs,
        )

    @classmethod
    def batch(cls, size: int = 10, **kwargs: Any) -> list[Proxy]:
        """Create a list of proxies quickly for concurrency/load tests."""
        return [cls.build(**kwargs) for _ in range(size)]


class ProxyPoolFactory(ModelFactory[ProxyPool]):
    """Factory for generating ProxyPool instances."""

    __model__ = ProxyPool

    name = lambda: f"pool_{Faker().slug()}"
    proxies = lambda: []
    max_pool_size = lambda: 100

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

    session_id = lambda: str(uuid4())
    proxy_id = lambda: str(uuid4())

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
def respx_mock_strict() -> Generator[respx.MockRouter, None, None]:
    """RESPX router that fails the test when a registered route was not used."""
    with respx.mock(assert_all_called=True) as router:
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


_BOOTSTRAP_FETCH_EXEMPT = (
    "test_sources.py",
    "test_async_request_bootstrap.py",
    "test_sync_request_bootstrap.py",
    "test_bootstrap_config.py",
)


@pytest.fixture(autouse=True)
def mock_lazy_bootstrap_fetch(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mock lazy bootstrap fetches except in suites that assert real orchestration."""

    node_path = str(request.fspath)
    if any(name in node_path for name in _BOOTSTRAP_FETCH_EXEMPT):
        return
    if request.node.get_closest_marker("network"):
        return

    async def _fetch_all_sources_mock(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return []

    monkeypatch.setattr(
        "proxywhirl.rotator._bootstrap.fetch_all_sources",
        _fetch_all_sources_mock,
    )


# ============================================================================
# API RUNTIME FIXTURES
# ============================================================================

_API_TEST_PATH_MARKERS = (
    "/tests/api/",
    "/tests/integration/test_api_",
    "/tests/contract/test_api_",
)


@pytest.fixture(autouse=True)
def deterministic_public_dns(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Resolve example.com hostnames to a public address for SSRF validation in API tests."""
    if not any(marker in str(request.fspath) for marker in _API_TEST_PATH_MARKERS):
        return

    original_getaddrinfo = socket.getaddrinfo

    def _getaddrinfo(
        host: object,
        port: object,
        family: int = socket.AF_UNSPEC,
        type: int = socket.SOCK_STREAM,
        *args: object,
        **kwargs: object,
    ) -> list[tuple]:
        host_text = str(host).rstrip(".").lower()
        if host_text.endswith(".example.com") or host_text == "example.com":
            return [(socket.AF_INET, type, 0, "", ("93.184.216.34", port or 80))]
        return original_getaddrinfo(host, port, family, type, *args, **kwargs)

    monkeypatch.setattr(socket, "getaddrinfo", _getaddrinfo)


@pytest.fixture(autouse=True)
def reset_api_runtime_state(request: pytest.FixtureRequest) -> Generator[None, None, None]:
    """Reset global API runtime between API-scoped tests to avoid cross-test pollution."""
    from proxywhirl.api import app
    from proxywhirl.api import runtime as api_runtime

    if not any(marker in str(request.fspath) for marker in _API_TEST_PATH_MARKERS):
        yield
        return

    api_runtime.reset_api_state()
    app.dependency_overrides.clear()
    yield
    api_runtime.reset_api_state()
    app.dependency_overrides.clear()


@pytest.fixture
async def async_api_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Async HTTP client wired to the FastAPI ASGI app."""
    from httpx import ASGITransport, AsyncClient

    from proxywhirl.api import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


_API_TEST_KEY = "integration-test-api-key"


@pytest.fixture
def api_auth_headers(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """Headers and env for routes that require configured API authentication."""
    monkeypatch.setenv("PROXYWHIRL_API_KEY", _API_TEST_KEY)
    return {"X-API-Key": _API_TEST_KEY}


@pytest.fixture
def api_test_rotator() -> Generator[ProxyWhirl, None, None]:
    """Process-global rotator with two healthy proxies for API integration tests."""
    from proxywhirl.api import runtime as api_runtime
    from proxywhirl.models import HealthStatus

    rotator = ProxyWhirl(
        proxies=[
            ProxyFactory.healthy(url="http://proxy1.example.com:8080"),
            ProxyFactory.healthy(url="http://proxy2.example.com:8080"),
        ],
        bootstrap=False,
    )
    for proxy in rotator.pool.get_all_proxies():
        proxy.health_status = HealthStatus.HEALTHY
    api_runtime.set_rotator(rotator)
    yield rotator
    api_runtime.set_rotator(None)


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


class _AmbrSnapshotItem(pytest.Item):
    """Trivial item so explicit ``pytest path/to/*.ambr`` invocations collect cleanly.

    Agent stop-hooks often re-run modified paths under ``tests/``; syrupy snapshot
    files (``.ambr``) are data, not modules. Collect them as a presence check so
    those runs do not fail with ``ERROR: not found: ...ambr``.
    """

    def runtest(self) -> None:
        assert self.path.is_file(), f"Missing syrupy snapshot file: {self.path}"
        text = self.path.read_text(encoding="utf-8")
        assert text.startswith("# serializer version:"), (
            f"Unexpected syrupy snapshot header in {self.path}"
        )

    def reportinfo(self) -> tuple[Any, int | None, str]:
        return self.path, None, f"ambr:{self.name}"


class _AmbrSnapshotFile(pytest.File):
    """Collector for syrupy ``.ambr`` snapshot files."""

    def collect(self) -> Any:
        yield _AmbrSnapshotItem.from_parent(self, name=self.path.name)


def pytest_collect_file(file_path: Any, parent: Any) -> Any:
    """Collect ``.ambr`` snapshot files when passed as explicit pytest paths."""
    if file_path.suffix == ".ambr":
        return _AmbrSnapshotFile.from_parent(parent, path=file_path)
    return None


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

# Reproducibility notes:
# - `faker` seeds Faker at 12345 for stable synthetic URLs and labels.
# - CI sets HYPOTHESIS_PROFILE=ci (see justfile coverage / GitHub Actions test job).
# - `@pytest.mark.flaky(reruns=N)` is honored by pytest-rerunfailures; pair with
#   `just test-rerun` locally when debugging ordering-sensitive integration tests.


# ============================================================================
# PYTEST PLUGINS
# ============================================================================

pytest_plugins = ["pytest_asyncio"]
