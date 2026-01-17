"""Unit tests for geo utilities."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

import pytest
import respx
from httpx import Response

from proxywhirl.geo import batch_geolocate, enrich_proxies_with_geo


@pytest.mark.asyncio
async def test_batch_geolocate_empty_list() -> None:
    """Empty input should return empty results."""
    assert await batch_geolocate([]) == {}


@pytest.mark.asyncio
@respx.mock
async def test_batch_geolocate_multiple_batches(monkeypatch) -> None:
    """Multiple batches should sleep between requests and return results."""
    sleep_mock = AsyncMock()
    monkeypatch.setattr(asyncio, "sleep", sleep_mock)

    route = respx.post("http://ip-api.com/batch?fields=query,country,countryCode,status")
    route.side_effect = [
        Response(
            200,
            json=[
                {"query": "1.1.1.1", "status": "success", "country": "A", "countryCode": "AA"},
                {"query": "2.2.2.2", "status": "fail"},
            ],
        ),
        Response(
            200,
            json=[{"query": "3.3.3.3", "status": "success", "country": "B", "countryCode": "BB"}],
        ),
    ]

    result = await batch_geolocate(
        ["1.1.1.1", "2.2.2.2", "3.3.3.3"],
        batch_size=2,
        max_batches=10,
    )

    assert result["1.1.1.1"]["countryCode"] == "AA"
    assert result["3.3.3.3"]["countryCode"] == "BB"
    assert "2.2.2.2" not in result
    sleep_mock.assert_awaited_once()


def test_enrich_proxies_with_geo() -> None:
    """Proxy dicts should get country fields from geo data."""
    proxies = [{"ip": "1.1.1.1"}, {"ip": "2.2.2.2"}]
    geo_data = {"1.1.1.1": {"country": "A", "countryCode": "AA"}}

    enriched = enrich_proxies_with_geo(proxies, geo_data)
    assert enriched[0]["country"] == "A"
    assert enriched[0]["country_code"] == "AA"
    assert enriched[1]["country"] is None
