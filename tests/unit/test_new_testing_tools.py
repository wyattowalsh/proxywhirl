"""
Example tests demonstrating the new testing tools.

This module showcases the usage of:
- Polyfactory: For generating test data from Pydantic models
- Syrupy: For snapshot testing
- RESPX: For mocking HTTP requests with httpx
- Faker: For generating realistic test data
- Hypothesis: For property-based testing
"""

import httpx
import pytest
from hypothesis import given
from hypothesis import strategies as st

from proxywhirl.models import (
    HealthStatus,
    Proxy,
)

# Import factories from conftest
from tests.conftest import (
    ProxyFactory,
    ProxyPoolFactory,
    SelectionContextFactory,
    SessionFactory,
)


class TestPolyfactoryUsage:
    """Tests demonstrating Polyfactory for test data generation."""

    def test_create_proxy_with_factory(self):
        """Create a basic proxy using the factory."""
        proxy = ProxyFactory.build()

        assert proxy.id is not None
        assert proxy.url.startswith("http")
        assert proxy.health_status == HealthStatus.UNKNOWN

    def test_create_healthy_proxy(self):
        """Create a healthy proxy with realistic metrics."""
        proxy = ProxyFactory.healthy()

        assert proxy.health_status == HealthStatus.HEALTHY
        assert proxy.consecutive_failures == 0
        assert proxy.total_successes >= 8

    def test_create_unhealthy_proxy(self):
        """Create an unhealthy proxy."""
        proxy = ProxyFactory.unhealthy()

        assert proxy.health_status == HealthStatus.UNHEALTHY
        assert proxy.consecutive_failures >= 3

    def test_create_proxy_with_auth(self):
        """Create a proxy with authentication credentials."""
        proxy = ProxyFactory.with_auth(username="admin", password="secret123")

        assert proxy.username is not None
        assert proxy.password is not None
        assert proxy.username.get_secret_value() == "admin"
        assert proxy.password.get_secret_value() == "secret123"

    def test_create_proxy_with_geo(self):
        """Create a proxy with geo-location data."""
        proxy = ProxyFactory.with_geo(country_code="GB", region="London")

        assert proxy.country_code == "GB"
        assert proxy.region == "London"

    def test_create_pool_with_proxies(self):
        """Create a pool with multiple proxies."""
        pool = ProxyPoolFactory.with_proxies(count=10)

        assert pool.size == 10
        assert all(isinstance(p, Proxy) for p in pool.proxies)

    def test_create_pool_with_healthy_proxies(self):
        """Create a pool where all proxies are healthy."""
        pool = ProxyPoolFactory.with_healthy_proxies(count=5)

        assert pool.size == 5
        assert all(p.health_status == HealthStatus.HEALTHY for p in pool.proxies)

    def test_batch_create_proxies(self):
        """Create multiple proxies in batch."""
        proxies = ProxyFactory.batch(size=20)

        assert len(proxies) == 20
        assert len({p.id for p in proxies}) == 20  # All unique IDs


class TestSessionFactory:
    """Tests demonstrating Session factory methods."""

    def test_create_expired_session(self):
        """Create an expired session."""
        session = SessionFactory.expired()

        assert session.is_expired() is True

    def test_create_active_session(self):
        """Create an active session with TTL."""
        session = SessionFactory.active(duration_seconds=600)

        assert session.is_expired() is False


class TestSelectionContextFactory:
    """Tests demonstrating SelectionContext factory methods."""

    def test_create_context_with_session(self):
        """Create a context with session ID."""
        context = SelectionContextFactory.with_session()

        assert context.session_id is not None

    def test_create_context_with_failed_proxies(self):
        """Create a context for retry scenarios."""
        failed_ids = ["proxy-1", "proxy-2", "proxy-3"]
        context = SelectionContextFactory.with_failed_proxies(failed_ids)

        assert context.failed_proxy_ids == failed_ids
        assert context.attempt_number == 4  # 3 failures + 1


class TestRespxMocking:
    """Tests demonstrating RESPX for HTTP mocking."""

    def test_mock_single_request(self, respx_mock):
        """Mock a single HTTP request."""
        respx_mock.get("https://api.example.com/proxies").respond(
            json={"proxies": ["1.2.3.4:8080", "5.6.7.8:3128"]}
        )

        with httpx.Client() as client:
            response = client.get("https://api.example.com/proxies")

        assert response.status_code == 200
        assert response.json()["proxies"] == ["1.2.3.4:8080", "5.6.7.8:3128"]

    def test_mock_with_pattern(self, respx_mock):
        """Mock requests matching a URL pattern."""
        respx_mock.get(url__regex=r".*httpbin.*").respond(json={"origin": "1.2.3.4"})

        with httpx.Client() as client:
            response = client.get("https://httpbin.org/ip")

        assert response.json()["origin"] == "1.2.3.4"

    def test_mock_error_response(self, respx_mock):
        """Mock an error response."""
        respx_mock.get("https://api.example.com/fail").respond(
            status_code=500, json={"error": "Internal server error"}
        )

        with httpx.Client() as client:
            response = client.get("https://api.example.com/fail")

        assert response.status_code == 500

    def test_mock_timeout(self, respx_mock):
        """Mock a timeout scenario."""
        respx_mock.get("https://slow.example.com").mock(
            side_effect=httpx.TimeoutException("Connection timed out")
        )

        with httpx.Client() as client, pytest.raises(httpx.TimeoutException):
            client.get("https://slow.example.com")

    def test_using_mock_proxy_validation_fixture(self, mock_proxy_validation):
        """Use the pre-configured proxy validation mock fixture."""
        with httpx.Client() as client:
            response = client.get("http://httpbin.org/ip")

        assert response.json()["origin"] == "1.2.3.4"

    async def test_async_mock(self, respx_mock):
        """Mock an async HTTP request."""
        respx_mock.get("https://api.example.com/async").respond(json={"status": "ok"})

        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.example.com/async")

        assert response.json()["status"] == "ok"


class TestFakerUsage:
    """Tests demonstrating Faker for test data generation."""

    def test_faker_fixture(self, faker):
        """Use Faker to generate test data."""
        email = faker.email()
        ip = faker.ipv4()
        port = faker.random_int(1024, 65535)

        assert "@" in email
        assert len(ip.split(".")) == 4
        assert 1024 <= port <= 65535

    def test_fake_proxy_urls(self, fake_proxy_urls):
        """Use the fake_proxy_urls fixture."""
        assert len(fake_proxy_urls) == 5
        for url in fake_proxy_urls:
            assert url.startswith("http://proxy")
            assert ".example.com:" in url


@pytest.mark.snapshot
class TestSnapshotTesting:
    """Tests demonstrating Syrupy for snapshot testing."""

    def test_proxy_serialization_snapshot(self, snapshot):
        """Verify proxy JSON serialization matches snapshot."""
        proxy = Proxy(
            url="http://test.proxy.com:8080",
            protocol="http",
            health_status=HealthStatus.HEALTHY,
        )

        # Convert to dict for snapshot comparison (exclude dynamic fields)
        proxy_data = {
            "url": proxy.url,
            "protocol": proxy.protocol,
            "health_status": proxy.health_status.value,
        }

        assert proxy_data == snapshot

    def test_pool_summary_snapshot(self, snapshot):
        """Verify pool summary format matches snapshot."""
        summary = {
            "total_proxies": 10,
            "healthy": 7,
            "degraded": 2,
            "unhealthy": 1,
            "sources": {
                "fetched": 6,
                "user": 4,
            },
        }

        assert summary == snapshot


class TestHypothesisPropertyBased:
    """Tests demonstrating Hypothesis for property-based testing."""

    @given(st.integers(min_value=1, max_value=100))
    def test_pool_size_matches_proxy_count(self, count: int):
        """Property: Pool size always equals number of proxies added."""
        pool = ProxyPoolFactory.with_proxies(count=count)

        assert pool.size == count
        assert len(pool.proxies) == count

    @given(st.integers(min_value=0, max_value=1000))
    def test_success_rate_calculation(self, successes: int):
        """Property: Success rate is always between 0 and 1."""
        proxy = ProxyFactory.build()
        proxy.total_requests = successes + 10  # Ensure total > successes
        proxy.total_successes = successes

        rate = proxy.success_rate

        assert 0.0 <= rate <= 1.0

    @given(st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=10))
    def test_tags_are_stored_correctly(self, tags: list[str]):
        """Property: Tags added to proxy are preserved."""
        proxy = ProxyFactory.build()
        proxy.tags = set(tags)

        assert all(tag in proxy.tags for tag in tags)


class TestCombinedUsage:
    """Tests combining multiple testing tools."""

    def test_factory_with_respx_and_faker(self, respx_mock, faker):
        """Combine factory, mocking, and fake data."""
        # Generate fake data
        proxy_ip = faker.ipv4()
        proxy_port = faker.random_int(1024, 65535)
        proxy_url = f"http://{proxy_ip}:{proxy_port}"

        # Create proxy with factory
        proxy = ProxyFactory.build(url=proxy_url)

        # Mock validation endpoint
        respx_mock.get("http://httpbin.org/ip").respond(json={"origin": proxy_ip})

        # Verify proxy was created correctly
        assert proxy.url == proxy_url
        assert proxy_ip in proxy.url

    def test_pool_operations_with_hypothesis(self):
        """Test pool operations with generated data."""
        pool = ProxyPoolFactory.with_healthy_proxies(count=5)

        # Verify pool size
        assert pool.size == 5

        # All proxies should be healthy
        assert all(p.health_status == HealthStatus.HEALTHY for p in pool.proxies)

        # Get source breakdown
        breakdown = pool.get_source_breakdown()
        assert sum(breakdown.values()) == 5
