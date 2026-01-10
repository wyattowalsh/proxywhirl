"""
Integration tests for intelligent failover selection.
"""

from datetime import datetime, timezone

from proxywhirl import Proxy, ProxyRotator
from proxywhirl.retry_metrics import RetryAttempt, RetryOutcome


class TestPerformanceBasedSelection:
    """Integration tests for performance-based proxy selection."""

    def test_selects_higher_performing_proxy(self):
        """Test that system selects proxy with better performance."""
        # Create proxies with different success rates
        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        proxy1.total_requests = 100
        proxy1.total_successes = 95  # 95% success rate

        proxy2 = Proxy(url="http://proxy2.example.com:8080")
        proxy2.total_requests = 100
        proxy2.total_successes = 60  # 60% success rate

        rotator = ProxyRotator(proxies=[proxy1, proxy2])

        # Test intelligent selection
        executor = rotator.retry_executor

        selected = executor.select_retry_proxy([proxy1, proxy2], proxy2)

        # Should select proxy1 (higher success rate)
        assert selected == proxy1

    def test_considers_latency_in_scoring(self):
        """Test that latency is considered in proxy scoring."""
        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        proxy1.total_requests = 100
        proxy1.total_successes = 90

        proxy2 = Proxy(url="http://proxy2.example.com:8080")
        proxy2.total_requests = 100
        proxy2.total_successes = 90

        rotator = ProxyRotator(proxies=[proxy1, proxy2])

        # Add latency data for proxy1 (slower)
        for i in range(10):
            rotator.retry_metrics.record_attempt(
                RetryAttempt(
                    request_id=f"req-{i}",
                    attempt_number=0,
                    proxy_id=proxy1.id,
                    timestamp=datetime.now(timezone.utc),
                    outcome=RetryOutcome.SUCCESS,
                    delay_before=0.0,
                    latency=2.0,  # 2 seconds
                )
            )

        # Add latency data for proxy2 (faster)
        for i in range(10):
            rotator.retry_metrics.record_attempt(
                RetryAttempt(
                    request_id=f"req-{i}",
                    attempt_number=0,
                    proxy_id=proxy2.id,
                    timestamp=datetime.now(timezone.utc),
                    outcome=RetryOutcome.SUCCESS,
                    delay_before=0.0,
                    latency=0.5,  # 0.5 seconds (faster)
                )
            )

        executor = rotator.retry_executor

        failed_proxy = Proxy(url="http://failed.example.com:8080")
        selected = executor.select_retry_proxy([proxy1, proxy2], failed_proxy)

        # Should select proxy2 (lower latency)
        assert selected == proxy2

    def test_new_proxy_gets_neutral_score(self):
        """Test that proxies with no history get neutral score."""
        proxy_new = Proxy(url="http://proxy-new.example.com:8080")
        # No requests yet

        proxy_known = Proxy(url="http://proxy-known.example.com:8080")
        proxy_known.total_requests = 100
        proxy_known.total_successes = 50  # 50% success rate

        rotator = ProxyRotator(proxies=[proxy_new, proxy_known])

        executor = rotator.retry_executor

        # Calculate scores
        score_new = executor._calculate_proxy_score(proxy_new)
        score_known = executor._calculate_proxy_score(proxy_known)

        # New proxy gets neutral score (0.5 success rate assumption)
        assert 0.4 <= score_new <= 0.6
        assert 0.4 <= score_known <= 0.6


class TestGeoTargetingAwareness:
    """Integration tests for geo-targeted proxy selection."""

    def test_prioritizes_region_match(self):
        """Test that region-matching proxies are prioritized."""
        proxy_us = Proxy(
            url="http://proxy-us.example.com:8080",
            metadata={"region": "US-EAST"},
        )
        proxy_us.total_requests = 100
        proxy_us.total_successes = 75  # 75% success rate

        proxy_eu = Proxy(
            url="http://proxy-eu.example.com:8080",
            metadata={"region": "EU-WEST"},
        )
        proxy_eu.total_requests = 100
        proxy_eu.total_successes = 80  # 80% success rate (slightly better)

        rotator = ProxyRotator(proxies=[proxy_us, proxy_eu])

        executor = rotator.retry_executor

        failed_proxy = Proxy(url="http://failed.example.com:8080")

        # Select with US target region
        selected = executor.select_retry_proxy(
            [proxy_us, proxy_eu], failed_proxy, target_region="US-EAST"
        )

        # Should select proxy_us (region bonus outweighs slightly lower success rate)
        assert selected == proxy_us

    def test_no_region_metadata_no_bonus(self):
        """Test that proxies without region metadata don't get bonus."""
        proxy_no_region = Proxy(url="http://proxy-no-region.example.com:8080")
        proxy_no_region.total_requests = 100
        proxy_no_region.total_successes = 70  # 70% success rate

        proxy_with_region = Proxy(
            url="http://proxy-with-region.example.com:8080",
            metadata={"region": "US-EAST"},
        )
        proxy_with_region.total_requests = 100
        proxy_with_region.total_successes = 75  # 75% success rate

        rotator = ProxyRotator(proxies=[proxy_no_region, proxy_with_region])

        executor = rotator.retry_executor

        failed_proxy = Proxy(url="http://failed.example.com:8080")

        # Select with US target region
        selected = executor.select_retry_proxy(
            [proxy_no_region, proxy_with_region],
            failed_proxy,
            target_region="US-EAST",
        )

        # Should select proxy_with_region (has region match)
        assert selected == proxy_with_region

    def test_region_mismatch_no_bonus(self):
        """Test that mismatched regions don't get bonus."""
        proxy_us = Proxy(
            url="http://proxy-us.example.com:8080",
            metadata={"region": "US-EAST"},
        )
        proxy_us.total_requests = 100
        proxy_us.total_successes = 70

        proxy_eu = Proxy(
            url="http://proxy-eu.example.com:8080",
            metadata={"region": "EU-WEST"},
        )
        proxy_eu.total_requests = 100
        proxy_eu.total_successes = 85

        rotator = ProxyRotator(proxies=[proxy_us, proxy_eu])

        executor = rotator.retry_executor

        failed_proxy = Proxy(url="http://failed.example.com:8080")

        # Select with EU target region
        selected = executor.select_retry_proxy(
            [proxy_us, proxy_eu], failed_proxy, target_region="EU-WEST"
        )

        # Should select proxy_eu (matches region)
        assert selected == proxy_eu


class TestRetrySuccessRateImprovement:
    """Test that intelligent selection improves retry success rates."""

    def test_retry_success_rate_better_than_random(self):
        """Test that intelligent selection outperforms random selection."""
        # Create proxies with varied success rates
        proxy_good = Proxy(url="http://proxy-good.example.com:8080")
        proxy_good.total_requests = 100
        proxy_good.total_successes = 95  # 95% success rate

        proxy_bad = Proxy(url="http://proxy-bad.example.com:8080")
        proxy_bad.total_requests = 100
        proxy_bad.total_successes = 30  # 30% success rate

        rotator = ProxyRotator(proxies=[proxy_good, proxy_bad])

        executor = rotator.retry_executor

        failed_proxy = Proxy(url="http://failed.example.com:8080")

        # Simulate 100 retry selections
        selections = []
        for _ in range(100):
            selected = executor.select_retry_proxy([proxy_good, proxy_bad], failed_proxy)
            selections.append(selected)

        # Count selections
        good_selections = sum(1 for s in selections if s == proxy_good)

        # Should heavily favor good proxy (>80% of time)
        assert good_selections > 80
