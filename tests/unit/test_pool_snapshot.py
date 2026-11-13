"""Unit tests for PoolSnapshot field mapping (Wave 1 P-R-01)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from proxywhirl.models import HealthStatus, Proxy
from proxywhirl.pool_snapshot import PoolSnapshot, SnapshotManager


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


class TestSnapshotPathContainment:
    """Snapshot ids must not escape the storage directory."""

    def test_delete_snapshot_rejects_path_traversal(self, tmp_path: Path) -> None:
        manager = SnapshotManager(tmp_path / "snaps")
        outside = tmp_path / "secret.json"
        outside.write_text("keep", encoding="utf-8")

        with pytest.raises(ValueError, match="Invalid snapshot identifier"):
            manager.delete_snapshot("../secret")

        assert outside.read_text(encoding="utf-8") == "keep"

    def test_restore_snapshot_rejects_path_traversal(self, tmp_path: Path) -> None:
        manager = SnapshotManager(tmp_path / "snaps")
        outside = tmp_path / "secret.json"
        outside.write_text('{"snapshot_id": "secret"}', encoding="utf-8")

        with pytest.raises(ValueError, match="Invalid snapshot identifier"):
            manager.restore_snapshot("../secret")

        assert outside.read_text(encoding="utf-8") == '{"snapshot_id": "secret"}'

    def test_create_and_delete_snapshot_stays_in_storage_dir(self, tmp_path: Path) -> None:
        manager = SnapshotManager(tmp_path / "snaps")
        proxy = Proxy(url="http://proxy.example.com:8080")
        snapshot = manager.create_snapshot("pool-1", [proxy])
        target = manager.storage_dir / f"{snapshot.snapshot_id}.json"

        assert target.is_file()
        assert target.parent == manager.storage_dir.resolve()
        assert manager.delete_snapshot(snapshot.snapshot_id) is True
        assert not target.exists()
