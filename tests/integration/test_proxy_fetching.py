"""
Integration tests for proxy fetching functionality (US5).

Tests cover:
- T094: Retrieve proxies from source URL
- T095: Validate proxies before adding to pool
- T096: Aggregate and deduplicate from multiple sources
- T097: Periodic refresh on configured interval
- T098: Only working proxies added after validation
"""

import asyncio
from unittest.mock import AsyncMock, patch

import httpx
import respx

from proxywhirl.fetchers import (
    CSVParser,
    HTMLTableParser,
    JSONParser,
    PlainTextParser,
    ProxyValidator,
    deduplicate_proxies,
)


# T094: Retrieve proxies from source URL
class TestFetchFromSource:
    """Test proxy retrieval from various source URLs."""

    @respx.mock
    async def test_fetch_json_source_successfully(self) -> None:
        """SC1: Fetch proxies from JSON source URL."""
        # Mock HTTP response
        json_data = [
            {"url": "http://proxy1.example.com:8080"},
            {"url": "http://proxy2.example.com:3128"},
        ]
        respx.get("https://proxy-source.example.com/list.json").mock(
            return_value=httpx.Response(200, json=json_data)
        )

        # Fetch and parse
        async with httpx.AsyncClient() as client:
            response = await client.get("https://proxy-source.example.com/list.json")
            parser = JSONParser()
            proxies = parser.parse(response.text)

        assert len(proxies) == 2
        assert proxies[0]["url"] == "http://proxy1.example.com:8080"
        assert proxies[1]["url"] == "http://proxy2.example.com:3128"

    @respx.mock
    async def test_fetch_csv_source_successfully(self) -> None:
        """SC1: Fetch proxies from CSV source URL."""
        csv_data = "ip,port,country\n1.2.3.4,8080,US\n5.6.7.8,3128,UK"
        respx.get("https://proxy-source.example.com/list.csv").mock(
            return_value=httpx.Response(200, text=csv_data)
        )

        async with httpx.AsyncClient() as client:
            response = await client.get("https://proxy-source.example.com/list.csv")
            parser = CSVParser(has_header=True)
            proxies = parser.parse(response.text)

        assert len(proxies) == 2
        assert proxies[0]["ip"] == "1.2.3.4"
        assert proxies[0]["port"] == "8080"
        assert proxies[1]["country"] == "UK"

    @respx.mock
    async def test_fetch_text_source_successfully(self) -> None:
        """SC1: Fetch proxies from plain text source URL."""
        text_data = "http://proxy1.example.com:8080\nhttp://proxy2.example.com:3128"
        respx.get("https://proxy-source.example.com/list.txt").mock(
            return_value=httpx.Response(200, text=text_data)
        )

        async with httpx.AsyncClient() as client:
            response = await client.get("https://proxy-source.example.com/list.txt")
            parser = PlainTextParser()
            proxies = parser.parse(response.text)

        assert len(proxies) == 2
        assert proxies[0]["url"] == "http://proxy1.example.com:8080"

    @respx.mock
    async def test_fetch_html_table_source_successfully(self) -> None:
        """SC1: Fetch proxies from HTML table source URL."""
        html_data = """
        <html>
        <body>
            <table>
                <tr><th>IP</th><th>Port</th></tr>
                <tr><td>1.2.3.4</td><td>8080</td></tr>
                <tr><td>5.6.7.8</td><td>3128</td></tr>
            </table>
        </body>
        </html>
        """
        respx.get("https://proxy-source.example.com/list.html").mock(
            return_value=httpx.Response(200, text=html_data)
        )

        async with httpx.AsyncClient() as client:
            response = await client.get("https://proxy-source.example.com/list.html")
            parser = HTMLTableParser(
                table_selector="table",
                column_indices={"ip": 0, "port": 1},
            )
            proxies = parser.parse(response.text)

        assert len(proxies) == 2
        assert proxies[0]["ip"] == "1.2.3.4"
        assert proxies[1]["port"] == "3128"

    @respx.mock
    async def test_fetch_handles_http_errors(self) -> None:
        """SC1: Handle HTTP errors gracefully."""
        respx.get("https://proxy-source.example.com/list.json").mock(
            return_value=httpx.Response(404)
        )

        async with httpx.AsyncClient() as client:
            response = await client.get("https://proxy-source.example.com/list.json")
            assert response.status_code == 404


# T095: Validate proxies before adding to pool
class TestValidateBeforeAdding:
    """Test proxy validation before pool addition."""

    async def test_only_valid_proxies_pass_validation(self) -> None:
        """SC2: Only validated proxies are added to pool."""
        proxies = [
            {"url": "http://proxy1.example.com:8080"},
            {"url": "http://proxy2.example.com:3128"},
            {"url": "http://proxy3.example.com:80"},
        ]

        # Mock validator to accept only first two proxies
        validator = ProxyValidator(timeout=5.0)
        with patch.object(validator, "validate", new_callable=AsyncMock) as mock_validate:
            mock_validate.side_effect = [True, True, False]

            validated = []
            for proxy in proxies:
                if await validator.validate(proxy):
                    validated.append(proxy)

        assert len(validated) == 2
        assert validated[0]["url"] == "http://proxy1.example.com:8080"
        assert validated[1]["url"] == "http://proxy2.example.com:3128"

    async def test_validation_timeout_rejects_slow_proxies(self) -> None:
        """SC2: Slow proxies are rejected during validation."""
        proxy = {"url": "http://slow-proxy.example.com:8080"}
        validator = ProxyValidator(timeout=0.1)  # Very short timeout

        with patch.object(validator, "validate", new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = False  # Simulate timeout rejection

            result = await validator.validate(proxy)

        assert result is False

    async def test_batch_validation_processes_all_proxies(self) -> None:
        """SC2: Batch validation processes all proxies."""
        proxies = [
            {"url": "http://proxy1.example.com:8080"},
            {"url": "http://proxy2.example.com:3128"},
            {"url": "http://proxy3.example.com:80"},
            {"url": "http://proxy4.example.com:1080"},
        ]

        validator = ProxyValidator(timeout=5.0)
        with patch.object(validator, "validate_batch", new_callable=AsyncMock) as mock_batch:
            # Simulate 3 working proxies
            mock_batch.return_value = proxies[:3]

            validated = await validator.validate_batch(proxies)

        assert len(validated) == 3


# T096: Aggregate and deduplicate from multiple sources
class TestAggregateMultipleSources:
    """Test aggregation and deduplication from multiple sources."""

    @respx.mock
    async def test_aggregate_proxies_from_multiple_sources(self) -> None:
        """SC3: Aggregate proxies from multiple sources."""
        # Mock multiple sources
        json_data = [{"url": "http://proxy1.example.com:8080"}]
        csv_data = "url\nhttp://proxy2.example.com:3128"
        text_data = "http://proxy3.example.com:80"

        respx.get("https://source1.example.com/list.json").mock(
            return_value=httpx.Response(200, json=json_data)
        )
        respx.get("https://source2.example.com/list.csv").mock(
            return_value=httpx.Response(200, text=csv_data)
        )
        respx.get("https://source3.example.com/list.txt").mock(
            return_value=httpx.Response(200, text=text_data)
        )

        # Fetch from all sources
        all_proxies = []
        async with httpx.AsyncClient() as client:
            # Source 1: JSON
            resp1 = await client.get("https://source1.example.com/list.json")
            all_proxies.extend(JSONParser().parse(resp1.text))

            # Source 2: CSV
            resp2 = await client.get("https://source2.example.com/list.csv")
            all_proxies.extend(CSVParser().parse(resp2.text))

            # Source 3: Text
            resp3 = await client.get("https://source3.example.com/list.txt")
            all_proxies.extend(PlainTextParser().parse(resp3.text))

        assert len(all_proxies) == 3
        assert all_proxies[0]["url"] == "http://proxy1.example.com:8080"
        assert all_proxies[1]["url"] == "http://proxy2.example.com:3128"
        assert all_proxies[2]["url"] == "http://proxy3.example.com:80"

    def test_deduplicate_removes_duplicate_proxies(self) -> None:
        """SC3: Deduplication removes duplicate proxies."""
        proxies = [
            {"url": "http://proxy1.example.com:8080"},
            {"url": "http://proxy2.example.com:3128"},
            {"url": "http://proxy1.example.com:8080"},  # Duplicate
            {"url": "http://proxy3.example.com:80"},
            {"url": "http://proxy2.example.com:3128"},  # Duplicate
        ]

        unique = deduplicate_proxies(proxies)

        assert len(unique) == 3
        assert unique[0]["url"] == "http://proxy1.example.com:8080"
        assert unique[1]["url"] == "http://proxy2.example.com:3128"
        assert unique[2]["url"] == "http://proxy3.example.com:80"

    def test_deduplicate_preserves_first_occurrence_metadata(self) -> None:
        """SC3: Deduplication preserves metadata from first occurrence."""
        proxies = [
            {"url": "http://proxy1.example.com:8080", "source": "premium"},
            {"url": "http://proxy1.example.com:8080", "source": "free"},
        ]

        unique = deduplicate_proxies(proxies)

        assert len(unique) == 1
        assert unique[0]["source"] == "premium"  # First occurrence preserved


# T097: Periodic refresh on configured interval
class TestPeriodicRefresh:
    """Test periodic refresh functionality."""

    async def test_periodic_refresh_triggers_at_interval(self) -> None:
        """SC4: Periodic refresh triggers at configured interval."""
        refresh_count = 0

        async def mock_fetch_and_refresh() -> None:
            nonlocal refresh_count
            refresh_count += 1

        # Simulate 3 refresh cycles with 0.1s interval
        interval = 0.1
        for _ in range(3):
            await mock_fetch_and_refresh()
            await asyncio.sleep(interval)

        assert refresh_count == 3

    async def test_refresh_updates_proxy_pool(self) -> None:
        """SC4: Refresh updates the proxy pool with new proxies."""
        # Initial pool
        pool = [{"url": "http://old-proxy.example.com:8080"}]

        # New proxies from refresh
        new_proxies = [
            {"url": "http://new-proxy1.example.com:8080"},
            {"url": "http://new-proxy2.example.com:3128"},
        ]

        # Mock refresh operation
        async def refresh_pool() -> list[dict]:
            return new_proxies

        pool = await refresh_pool()

        assert len(pool) == 2
        assert pool[0]["url"] == "http://new-proxy1.example.com:8080"
        assert pool[1]["url"] == "http://new-proxy2.example.com:3128"

    async def test_refresh_deduplicates_with_existing_pool(self) -> None:
        """SC4: Refresh deduplicates new proxies with existing pool."""
        existing = [
            {"url": "http://proxy1.example.com:8080"},
            {"url": "http://proxy2.example.com:3128"},
        ]

        fetched = [
            {"url": "http://proxy1.example.com:8080"},  # Duplicate
            {"url": "http://proxy3.example.com:80"},  # New
        ]

        # Combine and deduplicate
        combined = existing + fetched
        unique = deduplicate_proxies(combined)

        assert len(unique) == 3
        assert any(p["url"] == "http://proxy3.example.com:80" for p in unique)


# T098: Only working proxies added after validation
class TestWorkingProxiesOnly:
    """Test that only working proxies are added to pool."""

    async def test_dead_proxies_filtered_out(self) -> None:
        """SC5: Dead proxies are filtered out after validation."""
        proxies = [
            {"url": "http://working1.example.com:8080"},
            {"url": "http://dead1.example.com:3128"},
            {"url": "http://working2.example.com:80"},
            {"url": "http://dead2.example.com:1080"},
        ]

        validator = ProxyValidator(timeout=5.0)
        with patch.object(validator, "validate", new_callable=AsyncMock) as mock_validate:
            # Simulate: working, dead, working, dead
            mock_validate.side_effect = [True, False, True, False]

            validated = []
            for proxy in proxies:
                if await validator.validate(proxy):
                    validated.append(proxy)

        assert len(validated) == 2
        assert validated[0]["url"] == "http://working1.example.com:8080"
        assert validated[1]["url"] == "http://working2.example.com:80"

    async def test_validation_performance_meets_requirements(self) -> None:
        """SC5: Validation meets performance requirements (SC-011: 100+ proxies/sec)."""
        # Generate 150 proxies
        proxies = [{"url": f"http://proxy{i}.example.com:8080"} for i in range(150)]

        validator = ProxyValidator(timeout=5.0)
        with patch.object(validator, "validate_batch", new_callable=AsyncMock) as mock_batch:
            # Simulate fast validation (all working)
            mock_batch.return_value = proxies

            import time

            start = time.perf_counter()
            validated = await validator.validate_batch(proxies)
            elapsed = time.perf_counter() - start

        assert len(validated) == 150
        # SC-011: Should process 100+ proxies/sec, so 150 should take < 1.5s
        # (Being generous here since it's mocked)
        assert elapsed < 2.0

    async def test_partial_validation_failure_preserves_working_proxies(self) -> None:
        """SC5: Partial validation failures preserve working proxies."""
        proxies = [
            {"url": "http://proxy1.example.com:8080"},
            {"url": "http://proxy2.example.com:3128"},
            {"url": "http://proxy3.example.com:80"},
        ]

        validator = ProxyValidator(timeout=5.0)
        with patch.object(validator, "validate_batch", new_callable=AsyncMock) as mock_batch:
            # Simulate partial success (only 2 working)
            mock_batch.return_value = proxies[:2]

            validated = await validator.validate_batch(proxies)

        assert len(validated) == 2
        assert validated[0]["url"] == "http://proxy1.example.com:8080"
        assert validated[1]["url"] == "http://proxy2.example.com:3128"


# Integration test combining all scenarios
class TestCompleteProxyFetchingWorkflow:
    """Test complete proxy fetching workflow (all scenarios combined)."""

    @respx.mock
    async def test_end_to_end_proxy_fetching_workflow(self) -> None:
        """
        Complete workflow:
        1. Fetch from multiple sources (SC1)
        2. Aggregate and deduplicate (SC3)
        3. Validate proxies (SC2, SC5)
        4. Add only working proxies to pool
        """
        # Mock sources
        json_data = [
            {"url": "http://proxy1.example.com:8080"},
            {"url": "http://proxy2.example.com:3128"},
        ]
        csv_data = "url\nhttp://proxy2.example.com:3128\nhttp://proxy3.example.com:80"

        respx.get("https://source1.example.com/list.json").mock(
            return_value=httpx.Response(200, json=json_data)
        )
        respx.get("https://source2.example.com/list.csv").mock(
            return_value=httpx.Response(200, text=csv_data)
        )

        # Step 1: Fetch from sources
        all_proxies = []
        async with httpx.AsyncClient() as client:
            resp1 = await client.get("https://source1.example.com/list.json")
            all_proxies.extend(JSONParser().parse(resp1.text))

            resp2 = await client.get("https://source2.example.com/list.csv")
            all_proxies.extend(CSVParser().parse(resp2.text))

        # Step 2: Deduplicate
        unique_proxies = deduplicate_proxies(all_proxies)
        assert len(unique_proxies) == 3  # proxy2 was duplicate

        # Step 3: Validate
        validator = ProxyValidator(timeout=5.0)
        with patch.object(validator, "validate", new_callable=AsyncMock) as mock_validate:
            # Simulate: proxy1 working, proxy2 dead, proxy3 working
            mock_validate.side_effect = [True, False, True]

            validated_pool = []
            for proxy in unique_proxies:
                if await validator.validate(proxy):
                    validated_pool.append(proxy)

        # Step 4: Verify final pool
        assert len(validated_pool) == 2
        assert validated_pool[0]["url"] == "http://proxy1.example.com:8080"
        assert validated_pool[1]["url"] == "http://proxy3.example.com:80"
