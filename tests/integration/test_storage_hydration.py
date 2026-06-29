"""Integration tests for storage dict hydration."""

from __future__ import annotations

import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from sqlalchemy import text

from proxywhirl.models import HealthStatus, Proxy, ProxySource
from proxywhirl.storage import SQLiteStorage, dict_to_proxy
from proxywhirl.utils import proxy_to_dict


def test_dict_to_proxy_round_trip() -> None:
    """dict_to_proxy should reconstruct proxies produced by proxy_to_dict."""
    original = Proxy(
        url="http://hydration-proxy.example.com:8080",
        health_status=HealthStatus.HEALTHY,
        source=ProxySource.USER,
        tags={"test", "hydration"},
    )
    original.total_requests = 12
    original.total_successes = 10

    serialized = proxy_to_dict(original, include_stats=True)
    row = {
        "url": serialized["url"],
        "protocol": serialized["protocol"],
        "health_status": serialized["health_status"],
        "source": serialized["source"],
        "total_successes": serialized["stats"]["total_successes"],
        "total_checks": serialized["stats"]["total_requests"],
    }

    restored = dict_to_proxy(row)
    round_trip = proxy_to_dict(restored, include_stats=True)

    assert str(restored.url) == serialized["url"]
    assert restored.health_status == original.health_status
    assert restored.source == original.source
    assert restored.total_successes == original.total_successes
    assert round_trip["url"] == serialized["url"]
    assert round_trip["health_status"] == serialized["health_status"]


@pytest.mark.asyncio
async def test_load_preserves_last_check_at() -> None:
    """SQLiteStorage.load must emit last_check_at for dict_to_proxy hydration."""
    proxy_url = "http://hydration-last-check.example.com:8080"
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "proxies.db"
        storage = SQLiteStorage(db_path)
        await storage.initialize()
        await storage.save([Proxy(url=proxy_url)])
        await storage.record_validation(proxy_url, is_valid=True, response_time_ms=42.0)

        rows = await storage.load()
        row = next(item for item in rows if item["url"] == proxy_url)
        restored = dict_to_proxy(row)

        assert row.get("last_check_at") is not None
        assert restored.last_health_check is not None
        await storage.close()


@pytest.mark.asyncio
async def test_load_preserves_expires_at() -> None:
    """expires_at on identity rows must round-trip through load and dict_to_proxy."""
    proxy_url = "http://hydration-expires.example.com:8080"
    expires_at = datetime.now(timezone.utc) + timedelta(hours=2)
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "proxies.db"
        storage = SQLiteStorage(db_path)
        await storage.initialize()
        await storage.save([Proxy(url=proxy_url)])

        async with storage.engine.begin() as conn:
            await conn.execute(
                text("UPDATE proxy_identities SET expires_at = :expires_at WHERE url = :url"),
                {"expires_at": expires_at, "url": proxy_url},
            )

        rows = await storage.load()
        row = next(item for item in rows if item["url"] == proxy_url)
        restored = dict_to_proxy(row)

        assert row.get("expires_at") == expires_at
        assert restored.expires_at == expires_at
        await storage.close()
