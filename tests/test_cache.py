"""ProxyCache tests.

pyright: reportMissingImports=false, reportUnknownMemberType=false,
    reportUnknownVariableType=false, reportUnknownArgumentType=false,
    reportUnknownParameterType=false
"""

from datetime import datetime, timezone
from ipaddress import ip_address
from pathlib import Path

# mypy: ignore-errors
import pytest

from proxywhirl.cache import ProxyCache
from proxywhirl.models import AnonymityLevel, CacheType, Proxy, Scheme


def _make_proxy(i: int) -> Proxy:
    host = f"192.0.2.{i}"
    return Proxy(
        host=host,
        ip=ip_address(host),
        port=8000 + i,
        schemes=[Scheme.HTTP],
        country_code="US",
        anonymity=AnonymityLevel.ELITE,
        last_checked=datetime.now(timezone.utc),
        response_time=0.5,
        source="test",
    )


def test_memory_cache_add_get_clear():
    cache = ProxyCache(CacheType.MEMORY)
    p1, p2 = _make_proxy(1), _make_proxy(2)
    cache.add_proxies([p1, p2])
    got = cache.get_proxies()
    assert len(got) == 2
    cache.clear()
    assert cache.get_proxies() == []


def test_json_cache_persistence(tmp_path: Path):
    path = tmp_path / "c.json"
    cache = ProxyCache(CacheType.JSON, path)
    p1 = _make_proxy(1)
    cache.add_proxies([p1])
    # New instance should read from disk
    cache2 = ProxyCache(CacheType.JSON, path)
    got = cache2.get_proxies()
    assert len(got) == 1 and got[0].host == p1.host


def test_update_and_remove():
    cache = ProxyCache(CacheType.MEMORY)
    p1 = _make_proxy(1)
    cache.add_proxies([p1])
    p1.port = 9000
    cache.update_proxy(p1)
    assert cache.get_proxies()[0].port == 9000
    cache.remove_proxy(p1)
    assert cache.get_proxies() == []


def test_sqlite_cache_round_trip(tmp_path: Path):
    db_path = tmp_path / "cache.sqlite"
    cache = ProxyCache(CacheType.SQLITE, db_path)
    p1, p2 = _make_proxy(10), _make_proxy(11)
    cache.add_proxies([p1, p2])
    all1 = cache.get_proxies()
    hosts1 = {p.host for p in all1}
    assert {p1.host, p2.host} == hosts1
    # Update one
    p1.port = 9999
    cache.update_proxy(p1)
    # Remove other
    cache.remove_proxy(p2)
    all2 = cache.get_proxies()
    assert len(all2) == 1 and all2[0].port == 9999
    # Clear
    cache.clear()
    assert cache.get_proxies() == []


@pytest.mark.parametrize(
    "cache_type,expected_len_after_dupe",
    [
        (CacheType.MEMORY, 2),  # memory is append-only for add_proxies
        (CacheType.JSON, 2),  # json mirrors in-memory list; no dedupe on add
        (CacheType.SQLITE, 1),  # sqlite uses PK(host,port) upsert
    ],
)
def test_add_duplicate_proxies(cache_type, expected_len_after_dupe, tmp_path):
    """Document current duplicate handling per backend."""
    path = tmp_path / "cache.db" if cache_type != CacheType.MEMORY else None
    cache = ProxyCache(cache_type, path)
    p1 = _make_proxy(1)

    cache.add_proxies([p1])
    assert len(cache.get_proxies()) == 1

    # Add the same proxy again
    cache.add_proxies([p1])
    assert len(cache.get_proxies()) == expected_len_after_dupe

    # Update semantics are via update_proxy (not add_proxies) for non-sqlite
    p1_alt = _make_proxy(1)
    p1_alt.source = "new_source"
    cache.update_proxy(p1_alt)

    proxies = cache.get_proxies()
    # For MEMORY/JSON: ensure at least one entry has updated metadata
    # For SQLITE: single row should reflect new metadata
    assert any(getattr(px, "source", None) == "new_source" for px in proxies)
