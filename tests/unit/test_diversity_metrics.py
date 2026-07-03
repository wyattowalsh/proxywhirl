"""Unit tests for diversity metrics."""

from proxywhirl.diversity_metrics import DiversityAnalyzer
from proxywhirl.models import Proxy


def test_diversity_analyzer_uses_current_proxy_geo_fields() -> None:
    """Diversity metrics should read Proxy.country_code and geo metadata."""
    proxies = [
        Proxy(
            url="http://us.example.com:8080", country_code="US", region="CA", metadata={"asn": 1}
        ),
        Proxy(
            url="http://gb.example.com:8080",
            country_code="GB",
            metadata={"city": "London", "asn": 2},
        ),
    ]

    metrics = DiversityAnalyzer.calculate_metrics(proxies)

    assert metrics.country_count == 2
    assert metrics.as_count == 2
    assert metrics.city_count == 2
    assert metrics.country_distribution == {"US": 1, "GB": 1}
