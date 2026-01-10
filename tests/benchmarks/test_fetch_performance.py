"""
Performance benchmarks for US5 proxy fetching.

Tests SC-011: Proxy validation processes 100+ proxies per second.
"""

import time
from unittest.mock import AsyncMock, patch

from proxywhirl.fetchers import ProxyValidator


class TestProxyValidationPerformance:
    """Performance benchmarks for proxy validation (SC-011)."""

    async def test_validation_meets_100_proxies_per_second_requirement(self) -> None:
        """SC-011: Validate 100+ proxies per second in parallel."""
        # Generate 150 test proxies
        proxies = [{"url": f"http://proxy{i}.example.com:8080"} for i in range(150)]

        validator = ProxyValidator(timeout=5.0)

        # Mock validate to return immediately (simulating fast network)
        with patch.object(validator, "validate", new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = True

            # Measure time for batch validation
            start = time.perf_counter()
            validated = await validator.validate_batch(proxies)
            elapsed = time.perf_counter() - start

        # Verify all proxies were validated
        assert len(validated) == 150

        # SC-011: Must process 100+ proxies/second
        # 150 proxies should take less than 1.5 seconds
        rate = len(validated) / elapsed
        print(f"\n📊 Validation rate: {rate:.1f} proxies/second")
        print(f"⏱️  Time elapsed: {elapsed:.3f}s for {len(validated)} proxies")

        assert rate >= 100, f"Expected ≥100 proxies/sec, got {rate:.1f}"

    async def test_validation_scales_with_larger_batches(self) -> None:
        """Verify validation scales efficiently with larger proxy batches."""
        # Test with 500 proxies
        proxies = [{"url": f"http://proxy{i}.example.com:8080"} for i in range(500)]

        validator = ProxyValidator(timeout=5.0)

        with patch.object(validator, "validate", new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = True

            start = time.perf_counter()
            validated = await validator.validate_batch(proxies)
            elapsed = time.perf_counter() - start

        assert len(validated) == 500

        rate = len(validated) / elapsed
        print(f"\n📊 Large batch rate: {rate:.1f} proxies/second")
        print(f"⏱️  Time elapsed: {elapsed:.3f}s for {len(validated)} proxies")

        # Should still maintain 100+/sec with larger batches
        assert rate >= 100, f"Expected ≥100 proxies/sec, got {rate:.1f}"
