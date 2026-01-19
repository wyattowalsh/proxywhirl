"""Unit tests for parallel batch validation."""

import asyncio
from unittest.mock import patch

import httpx

from proxywhirl.fetchers import ProxyValidator, ValidationResult
from proxywhirl.models import ValidationLevel


class TestParallelValidation:
    """Test batch validation with concurrency control."""

    async def test_validate_batch_parallel(self) -> None:
        """T021: Test batch validation runs proxies in parallel."""
        validator = ProxyValidator(level=ValidationLevel.STANDARD, concurrency=10)

        # Create 5 test proxies
        proxies = [{"url": f"http://proxy{i}.example.com:8080"} for i in range(5)]

        # Mock validate to track concurrent execution
        call_times = []

        async def mock_validate(proxy):
            call_times.append(asyncio.get_event_loop().time())
            await asyncio.sleep(0.1)  # Simulate validation time
            return ValidationResult(is_valid=True, response_time_ms=10.0)

        with patch.object(validator, "validate", side_effect=mock_validate):
            results = await validator.validate_batch(proxies)

            # All proxies should be validated
            assert len(results) == 5

            # All calls should start within a small time window (parallel execution)
            time_spread = max(call_times) - min(call_times)
            assert time_spread < 0.05  # All should start within 50ms

    async def test_validate_batch_concurrency_limit(self) -> None:
        """T022: Test batch validation respects concurrency limit."""
        validator = ProxyValidator(level=ValidationLevel.STANDARD, concurrency=2)

        # Create 5 test proxies (more than concurrency limit)
        proxies = [{"url": f"http://proxy{i}.example.com:8080"} for i in range(5)]

        # Track active concurrent validations
        active_count = 0
        max_concurrent = 0

        async def mock_validate(proxy):
            nonlocal active_count, max_concurrent
            active_count += 1
            max_concurrent = max(max_concurrent, active_count)
            await asyncio.sleep(0.05)
            active_count -= 1
            return ValidationResult(is_valid=True, response_time_ms=10.0)

        with patch.object(validator, "validate", side_effect=mock_validate):
            results = await validator.validate_batch(proxies)

            assert len(results) == 5
            # Should never exceed concurrency limit
            assert max_concurrent <= 2

    async def test_validate_batch_partial_failures(self) -> None:
        """T023: Test batch validation handles partial failures correctly."""
        validator = ProxyValidator(level=ValidationLevel.STANDARD)

        proxies = [
            {"url": "http://good1.proxy.com:8080"},
            {"url": "http://bad1.proxy.com:8080"},
            {"url": "http://good2.proxy.com:8080"},
            {"url": "http://bad2.proxy.com:8080"},
        ]

        # Mock validate to return success for "good" proxies
        async def mock_validate(proxy):
            url = proxy.get("url", "")
            is_valid = "good" in url
            return ValidationResult(is_valid=is_valid, response_time_ms=10.0 if is_valid else None)

        with patch.object(validator, "validate", side_effect=mock_validate):
            results = await validator.validate_batch(proxies)

            # Only 2 good proxies should be returned
            assert len(results) == 2
            assert all("good" in p["url"] for p in results)

    async def test_validate_batch_timeout_handling(self) -> None:
        """T024: Test batch validation handles timeouts gracefully."""
        validator = ProxyValidator(level=ValidationLevel.STANDARD, timeout=0.1)

        proxies = [
            {"url": "http://fast.proxy.com:8080"},
            {"url": "http://slow.proxy.com:8080"},
            {"url": "http://normal.proxy.com:8080"},
        ]

        # Mock validate with different timing
        async def mock_validate(proxy):
            url = proxy.get("url", "")
            if "slow" in url:
                await asyncio.sleep(0.2)  # Exceeds timeout
                return ValidationResult(is_valid=False, response_time_ms=None)
            await asyncio.sleep(0.05)
            return ValidationResult(is_valid=True, response_time_ms=50.0)

        with patch.object(validator, "validate", side_effect=mock_validate):
            results = await validator.validate_batch(proxies)

            # Slow proxy should be filtered out
            assert len(results) == 2
            assert not any("slow" in p["url"] for p in results)

    async def test_validate_batch_empty_list(self) -> None:
        """Test batch validation with empty proxy list."""
        validator = ProxyValidator(level=ValidationLevel.STANDARD)

        results = await validator.validate_batch([])

        assert results == []

    async def test_validate_batch_single_proxy(self) -> None:
        """Test batch validation with single proxy."""
        validator = ProxyValidator(level=ValidationLevel.STANDARD)

        proxies = [{"url": "http://proxy.example.com:8080"}]

        with patch.object(
            validator,
            "validate",
            return_value=ValidationResult(is_valid=True, response_time_ms=10.0),
        ):
            results = await validator.validate_batch(proxies)

            assert len(results) == 1
            assert results[0]["url"] == "http://proxy.example.com:8080"

    async def test_validate_batch_all_failures(self) -> None:
        """Test batch validation when all proxies fail."""
        validator = ProxyValidator(level=ValidationLevel.STANDARD)

        proxies = [
            {"url": "http://bad1.proxy.com:8080"},
            {"url": "http://bad2.proxy.com:8080"},
        ]

        with patch.object(
            validator,
            "validate",
            return_value=ValidationResult(is_valid=False, response_time_ms=None),
        ):
            results = await validator.validate_batch(proxies)

            assert results == []

    async def test_validate_batch_exception_handling(self) -> None:
        """Test batch validation handles exceptions in individual validations."""
        validator = ProxyValidator(level=ValidationLevel.STANDARD)

        proxies = [
            {"url": "http://proxy1.example.com:8080"},
            {"url": "http://proxy2.example.com:8080"},
            {"url": "http://proxy3.example.com:8080"},
        ]

        # Mock validate to raise exception for second proxy
        call_count = 0

        async def mock_validate(proxy):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise httpx.NetworkError("Network error")
            return ValidationResult(is_valid=True, response_time_ms=10.0)

        with patch.object(validator, "validate", side_effect=mock_validate):
            results = await validator.validate_batch(proxies)

            # Should get 2 successful results (1st and 3rd proxies)
            assert len(results) == 2
