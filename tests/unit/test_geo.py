"""Unit tests for geo utilities."""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
import respx
from httpx import Response

from proxywhirl.geo import (
    batch_geolocate,
    continent_for_country,
    enrich_proxies_with_geo,
    reset_geo_cache,
)


@pytest.mark.asyncio
async def test_batch_geolocate_empty_list() -> None:
    """Empty input should return empty results."""
    assert await batch_geolocate([]) == {}


@pytest.mark.asyncio
@respx.mock
async def test_batch_geolocate_does_not_call_external_api_by_default() -> None:
    """Missing local DB should not leak IPs to a third-party API by default."""
    route = respx.post("https://ip-api.com/batch?fields=query,country,countryCode,status")

    result = await batch_geolocate(["1.1.1.1"], db_path=Path("/does/not/exist.mmdb"))

    assert result == {}
    assert route.called is False


@pytest.mark.asyncio
@respx.mock
async def test_batch_geolocate_multiple_batches(monkeypatch) -> None:
    """Multiple batches should sleep between requests and return results."""
    sleep_mock = AsyncMock()
    monkeypatch.setattr(asyncio, "sleep", sleep_mock)

    route = respx.post("https://ip-api.com/batch?fields=query,country,countryCode,status")
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
        allow_external_api=True,
    )

    assert result["1.1.1.1"]["countryCode"] == "AA"
    assert result["3.3.3.3"]["countryCode"] == "BB"
    assert "2.2.2.2" not in result
    sleep_mock.assert_awaited_once()


def test_enrich_proxies_with_geo() -> None:
    """Proxy dicts should get country fields from geo data."""
    proxies = [{"ip": "1.1.1.1"}, {"ip": "2.2.2.2"}]
    geo_data = {
        "1.1.1.1": {"country": "United States", "countryCode": "US", "continentCode": "NA"},
    }

    enriched = enrich_proxies_with_geo(proxies, geo_data)
    assert enriched[0]["country"] == "United States"
    assert enriched[0]["country_code"] == "US"
    assert enriched[0]["continent_code"] == "NA"
    assert enriched[1]["country"] is None


def test_continent_for_country_mapping() -> None:
    assert continent_for_country("de") == "EU"
    assert continent_for_country("ZZ") == "AS"


@pytest.mark.asyncio
@respx.mock
async def test_batch_geolocate_api_sets_continent(monkeypatch) -> None:
    """External API results should include continent codes."""
    reset_geo_cache()
    route = respx.post("https://ip-api.com/batch?fields=query,country,countryCode,status")
    route.return_value = Response(
        200,
        json=[
            {
                "query": "8.8.8.8",
                "status": "success",
                "country": "United States",
                "countryCode": "US",
            }
        ],
    )

    result = await batch_geolocate(
        ["8.8.8.8"],
        allow_external_api=True,
        db_path=Path("/does/not/exist.mmdb"),
    )

    assert result["8.8.8.8"]["continentCode"] == "NA"
