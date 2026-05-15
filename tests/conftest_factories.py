"""Test data factories for generating realistic proxy/pool/session objects.

Uses Factory Boy and Faker for generating test data with minimal boilerplate.
"""

import random

from factory import Factory, LazyFunction, fuzzy
from faker import Faker

from proxywhirl.models import (
    HealthStatus,
    Proxy,
    ProxyCredentials,
    ProxyPool,
    Session,
)

fake = Faker()


class ProxyFactory(Factory):
    """Factory for generating realistic Proxy objects."""

    class Meta:
        model = Proxy

    url = LazyFunction(
        lambda: (
            f"{random.choice(['http', 'https', 'socks4', 'socks5'])}://"
            f"{fake.domain_name()}:{random.randint(1024, 65535)}"
        )
    )
    health_status = fuzzy.FuzzyChoice(
        [
            HealthStatus.HEALTHY,
            HealthStatus.UNHEALTHY,
            HealthStatus.UNKNOWN,
        ]
    )
    response_time_ms = fuzzy.FuzzyFloat(10.0, 1000.0, precision=2)
    is_premium = fuzzy.FuzzyChoice([True, False])
    country = fuzzy.FuzzyChoice(["US", "GB", "DE", "FR", "JP", "CN", "RU", "IN", "BR", "MX"])
    city = LazyFunction(fake.city)
    latitude = fuzzy.FuzzyFloat(-90.0, 90.0, precision=4)
    longitude = fuzzy.FuzzyFloat(-180.0, 180.0, precision=4)


class ProxyPoolFactory(Factory):
    """Factory for generating ProxyPool objects."""

    class Meta:
        model = ProxyPool

    name = LazyFunction(lambda: f"pool_{fake.slug()}")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override create to add proxies to pool."""
        pool = model_class(*args, **kwargs)

        # Add random number of proxies
        num_proxies = kwargs.pop("num_proxies", random.randint(5, 20))
        for _ in range(num_proxies):
            proxy = ProxyFactory()
            pool.add_proxy(proxy)

        return pool


class SessionFactory(Factory):
    """Factory for generating Session objects."""

    class Meta:
        model = Session

    id = LazyFunction(fake.uuid4)
    name = LazyFunction(lambda: f"session_{fake.slug()}")
    proxy_url = LazyFunction(
        lambda: f"{random.choice(['http', 'https'])}://{fake.domain_name()}:8080"
    )
    created_at = LazyFunction(fake.iso8601)
    last_used_at = LazyFunction(fake.iso8601)
    request_count = fuzzy.FuzzyInteger(0, 1000)


class ProxyCredentialsFactory(Factory):
    """Factory for generating ProxyCredentials objects."""

    class Meta:
        model = ProxyCredentials

    username = LazyFunction(fake.user_name)
    password = LazyFunction(fake.password)


# Convenience methods for common test scenarios


def create_healthy_proxy() -> Proxy:
    """Create a healthy proxy."""
    return ProxyFactory(health_status=HealthStatus.HEALTHY)


def create_unhealthy_proxy() -> Proxy:
    """Create an unhealthy proxy."""
    return ProxyFactory(health_status=HealthStatus.UNHEALTHY)


def create_proxy_pool_with_healthy_proxies(num_proxies: int = 10) -> ProxyPool:
    """Create a pool with all healthy proxies."""
    pool = ProxyPool(name=f"healthy_pool_{fake.slug()}")
    for _ in range(num_proxies):
        proxy = ProxyFactory(health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy)
    return pool


def create_proxy_pool_with_mixed_health(num_proxies: int = 10) -> ProxyPool:
    """Create a pool with mixed health proxies (70% healthy, 30% unhealthy)."""
    pool = ProxyPool(name=f"mixed_pool_{fake.slug()}")
    for i in range(num_proxies):
        health = HealthStatus.HEALTHY if random.random() < 0.7 else HealthStatus.UNHEALTHY
        proxy = ProxyFactory(health_status=health)
        pool.add_proxy(proxy)
    return pool


def create_proxy_pool_by_country(country: str, num_proxies: int = 10) -> ProxyPool:
    """Create a pool with proxies from a specific country."""
    pool = ProxyPool(name=f"pool_{country.lower()}_{fake.slug()}")
    for _ in range(num_proxies):
        proxy = ProxyFactory(country=country)
        pool.add_proxy(proxy)
    return pool


def create_proxy_pool_with_credentials(
    num_proxies: int = 5,
) -> ProxyPool:
    """Create a pool with proxies that have credentials."""
    pool = ProxyPool(name=f"auth_pool_{fake.slug()}")
    for _ in range(num_proxies):
        credentials = ProxyCredentialsFactory()
        proxy = ProxyFactory()
        proxy.credentials = credentials  # type: ignore
        pool.add_proxy(proxy)
    return pool


def create_diverse_proxy_pool(num_proxies: int = 20) -> ProxyPool:
    """Create a realistic diverse pool with various proxy types and health statuses."""
    pool = ProxyPool(name=f"diverse_pool_{fake.slug()}")

    # Add HTTP proxies
    for _ in range(int(num_proxies * 0.6)):
        proxy = ProxyFactory(health_status=HealthStatus.HEALTHY)
        pool.add_proxy(proxy)

    # Add some unhealthy proxies
    for _ in range(int(num_proxies * 0.3)):
        proxy = ProxyFactory(health_status=HealthStatus.UNHEALTHY)
        pool.add_proxy(proxy)

    # Add some with unknown health
    for _ in range(int(num_proxies * 0.1)):
        proxy = ProxyFactory(health_status=HealthStatus.UNKNOWN)
        pool.add_proxy(proxy)

    return pool
