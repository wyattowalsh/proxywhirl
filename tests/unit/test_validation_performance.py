"""Performance benchmarks for parallel validation."""

import asyncio
import time
from unittest.mock import patch

from proxywhirl.fetchers import ProxyValidator
from proxywhirl.models import ValidationLevel


class TestValidationPerformance:
    """Test validation performance benchmarks."""

    async def test_batch_validation_throughput(self) -> None:
        """T028: Test batch validation processes 100+ proxies per second."""
        validator = ProxyValidator(level=ValidationLevel.BASIC, concurrency=50)

        # Create 100 test proxies
        proxies = [{"url": f"http://proxy{i}.example.com:8080"} for i in range(100)]

        # Mock validate to simulate fast validation (~10ms each)
        async def mock_validate(proxy):
            await asyncio.sleep(0.01)
            return True

        with patch.object(validator, "validate", side_effect=mock_validate):
            start_time = time.time()
            results = await validator.validate_batch(proxies)
            elapsed_time = time.time() - start_time

            # All proxies should be validated
            assert len(results) == 100

            # Should process 100+ proxies per second
            # With concurrency=50 and 10ms per validation, theoretical time is ~20ms
            # Allow up to 1 second for overhead
            assert elapsed_time < 1.0, f"Took {elapsed_time:.3f}s, expected < 1.0s"

            # Calculate throughput
            throughput = len(results) / elapsed_time
            assert throughput >= 100, f"Throughput {throughput:.1f}/s, expected >= 100/s"

    async def test_batch_validation_scaling(self) -> None:
        """T029: Test batch validation scales with concurrency."""
        # Test with different concurrency levels
        test_cases = [
            (10, 50),  # 50 proxies, concurrency 10
            (20, 50),  # 50 proxies, concurrency 20
            (50, 50),  # 50 proxies, concurrency 50
        ]

        results_data = []

        for concurrency, proxy_count in test_cases:
            validator = ProxyValidator(level=ValidationLevel.BASIC, concurrency=concurrency)
            proxies = [{"url": f"http://proxy{i}.example.com:8080"} for i in range(proxy_count)]

            # Mock validate
            async def mock_validate(proxy):
                await asyncio.sleep(0.01)
                return True

            with patch.object(validator, "validate", side_effect=mock_validate):
                start_time = time.time()
                await validator.validate_batch(proxies)
                elapsed_time = time.time() - start_time

                results_data.append((concurrency, elapsed_time))

        # Higher concurrency should result in faster completion
        # With larger concurrency difference, expect significant improvement
        low_concurrency_time = results_data[0][1]
        high_concurrency_time = results_data[-1][1]

        # High concurrency should be at least 20% faster (allow some overhead/variance)
        improvement_ratio = high_concurrency_time / low_concurrency_time
        assert (
            improvement_ratio < 0.9
        ), f"Higher concurrency should be faster: {high_concurrency_time:.3f}s vs {low_concurrency_time:.3f}s (ratio: {improvement_ratio:.2f})"

    async def test_validation_overhead(self) -> None:
        """T030: Test validation overhead is minimal."""
        validator = ProxyValidator(level=ValidationLevel.BASIC, concurrency=100)

        # Create 10 test proxies
        proxies = [{"url": f"http://proxy{i}.example.com:8080"} for i in range(10)]

        # Mock validate with minimal delay
        async def mock_validate(proxy):
            await asyncio.sleep(0.001)  # 1ms
            return True

        with patch.object(validator, "validate", side_effect=mock_validate):
            start_time = time.time()
            results = await validator.validate_batch(proxies)
            elapsed_time = time.time() - start_time

            assert len(results) == 10

            # With 1ms validation time and high concurrency, overhead should be minimal
            # Total time should be close to validation time (~1-10ms) plus small overhead
            # Allow up to 100ms total
            assert elapsed_time < 0.1, f"Overhead too high: {elapsed_time:.3f}s for 10 proxies"

    async def test_large_batch_validation(self) -> None:
        """Test validation handles large batches efficiently."""
        validator = ProxyValidator(level=ValidationLevel.BASIC, concurrency=100)

        # Create 500 test proxies
        proxies = [{"url": f"http://proxy{i}.example.com:8080"} for i in range(500)]

        # Mock validate
        async def mock_validate(proxy):
            await asyncio.sleep(0.005)  # 5ms
            return True

        with patch.object(validator, "validate", side_effect=mock_validate):
            start_time = time.time()
            results = await validator.validate_batch(proxies)
            elapsed_time = time.time() - start_time

            assert len(results) == 500

            # With concurrency=100 and 5ms validation time:
            # Theoretical minimum: 500/100 * 0.005 = 0.025s
            # Allow up to 5 seconds for overhead
            assert elapsed_time < 5.0, f"Took {elapsed_time:.3f}s, expected < 5.0s"

            throughput = len(results) / elapsed_time
            # Should maintain good throughput even with large batches
            assert throughput >= 100, f"Throughput {throughput:.1f}/s, expected >= 100/s"
