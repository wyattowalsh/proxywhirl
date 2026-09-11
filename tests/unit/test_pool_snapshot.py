"""Unit tests for PoolSnapshot field mapping (Wave 1 P-R-01)."""

from __future__ import annotations

from datetime import datetime, timezone

from proxywhirl.models import HealthStatus, Proxy
from proxywhirl.pool_snapshot import PoolSnapshot


class TestPoolSnapshotFieldMapping:
    """Snapshot rows must use live Proxy model fields (RV-012)."""

    def test_add_proxy_state_uses_live_proxy_fields(self) -> None:
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            health_status=HealthStatus.DEGRADED,
            total_failures=2,
            total_successes=7,
            tags={"residential", "us"},
        )
        proxy.last_health_check = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)

        snapshot = PoolSnapshot("pool-1", "snap-1", datetime.now(timezone.utc))
        snapshot.add_proxy_state(proxy)

        row = snapshot.proxies[0]
        assert row["id"] == str(proxy.id)
        assert row["url"] == proxy.url
        assert row["health_status"] == HealthStatus.DEGRADED.value
        assert row["total_failures"] == 2
        assert row["total_successes"] == 7
        assert row["tags"] == ["residential", "us"]
        assert row["last_checked"] == proxy.last_health_check.isoformat()
