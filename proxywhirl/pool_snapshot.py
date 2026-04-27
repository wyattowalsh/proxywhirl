"""Pool state snapshots for reproducibility and state recovery.

Allows saving and restoring proxy pool state for reproducibility,
testing, and disaster recovery scenarios.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger

from proxywhirl.models import Proxy


class PoolSnapshot:
    """Represents a point-in-time snapshot of pool state."""

    def __init__(self, pool_id: str, snapshot_id: str, timestamp: datetime) -> None:
        """Initialize snapshot.

        Args:
            pool_id: ID of the pool being snapshotted
            snapshot_id: Unique snapshot identifier
            timestamp: When the snapshot was taken
        """
        self.pool_id = pool_id
        self.snapshot_id = snapshot_id
        self.timestamp = timestamp
        self.proxies: list[dict[str, Any]] = []
        self.metadata: dict[str, Any] = {}

    def add_proxy_state(self, proxy: Proxy) -> None:
        """Add a proxy's state to the snapshot."""
        self.proxies.append(
            {
                "url": proxy.url,
                "status": proxy.status,
                "last_checked": proxy.last_checked.isoformat() if proxy.last_checked else None,
                "failure_count": proxy.failure_count,
                "success_count": proxy.success_count,
                "tags": list(proxy.tags) if proxy.tags else [],
            }
        )

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata about the snapshot."""
        self.metadata[key] = value

    def to_dict(self) -> dict[str, Any]:
        """Convert snapshot to dictionary."""
        return {
            "pool_id": self.pool_id,
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp.isoformat(),
            "proxies": self.proxies,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        """Convert snapshot to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PoolSnapshot:
        """Create snapshot from dictionary."""
        timestamp = datetime.fromisoformat(data["timestamp"])
        snapshot = cls(
            pool_id=data["pool_id"],
            snapshot_id=data["snapshot_id"],
            timestamp=timestamp,
        )
        snapshot.proxies = data.get("proxies", [])
        snapshot.metadata = data.get("metadata", {})
        return snapshot

    @classmethod
    def from_json(cls, json_str: str) -> PoolSnapshot:
        """Create snapshot from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


class SnapshotManager:
    """Manages creation and restoration of pool snapshots."""

    def __init__(self, storage_dir: str | Path | None = None) -> None:
        """Initialize snapshot manager.

        Args:
            storage_dir: Directory for storing snapshot files
        """
        self.storage_dir = Path(storage_dir) if storage_dir else Path.cwd() / ".snapshots"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots: dict[str, PoolSnapshot] = {}

    def create_snapshot(
        self,
        pool_id: str,
        proxies: list[Proxy],
        metadata: dict[str, Any] | None = None,
    ) -> PoolSnapshot:
        """Create a new snapshot of pool state.

        Args:
            pool_id: ID of the pool
            proxies: List of proxies to snapshot
            metadata: Optional metadata about the snapshot

        Returns:
            Created PoolSnapshot
        """
        snapshot_id = f"{pool_id}_{datetime.now().isoformat()}"
        snapshot = PoolSnapshot(pool_id, snapshot_id, datetime.now())

        for proxy in proxies:
            snapshot.add_proxy_state(proxy)

        if metadata:
            for key, value in metadata.items():
                snapshot.set_metadata(key, value)

        self.snapshots[snapshot_id] = snapshot
        self._save_snapshot(snapshot)
        logger.info(f"Created snapshot: {snapshot_id} with {len(proxies)} proxies")
        return snapshot

    def restore_snapshot(self, snapshot_id: str) -> PoolSnapshot | None:
        """Restore a saved snapshot.

        Args:
            snapshot_id: ID of snapshot to restore

        Returns:
            PoolSnapshot if found, None otherwise
        """
        if snapshot_id in self.snapshots:
            return self.snapshots[snapshot_id]

        # Try loading from disk
        snapshot_file = self.storage_dir / f"{snapshot_id}.json"
        if snapshot_file.exists():
            try:
                with open(snapshot_file) as f:
                    snapshot = PoolSnapshot.from_json(f.read())
                    self.snapshots[snapshot_id] = snapshot
                    logger.info(f"Restored snapshot from disk: {snapshot_id}")
                    return snapshot
            except Exception as e:
                logger.error(f"Failed to restore snapshot: {e}")

        return None

    def list_snapshots(self, pool_id: str | None = None) -> list[PoolSnapshot]:
        """List all available snapshots.

        Args:
            pool_id: If provided, only return snapshots for this pool

        Returns:
            List of PoolSnapshot objects
        """
        snapshots = list(self.snapshots.values())
        if pool_id:
            snapshots = [s for s in snapshots if s.pool_id == pool_id]
        return sorted(snapshots, key=lambda s: s.timestamp, reverse=True)

    def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete a snapshot.

        Args:
            snapshot_id: ID of snapshot to delete

        Returns:
            True if deleted, False if not found
        """
        if snapshot_id in self.snapshots:
            del self.snapshots[snapshot_id]

        snapshot_file = self.storage_dir / f"{snapshot_id}.json"
        if snapshot_file.exists():
            snapshot_file.unlink()
            logger.info(f"Deleted snapshot: {snapshot_id}")
            return True

        return False

    def cleanup_old_snapshots(self, days: int = 30) -> int:
        """Delete snapshots older than specified days.

        Args:
            days: Age threshold in days

        Returns:
            Number of snapshots deleted
        """
        cutoff = datetime.now() - __import__("datetime").timedelta(days=days)
        deleted = 0

        for snapshot_id in list(self.snapshots.keys()):
            snapshot = self.snapshots[snapshot_id]
            if snapshot.timestamp < cutoff:
                self.delete_snapshot(snapshot_id)
                deleted += 1

        logger.info(f"Cleaned up {deleted} old snapshots")
        return deleted

    def _save_snapshot(self, snapshot: PoolSnapshot) -> None:
        """Save snapshot to disk."""
        snapshot_file = self.storage_dir / f"{snapshot.snapshot_id}.json"
        try:
            with open(snapshot_file, "w") as f:
                f.write(snapshot.to_json())
            logger.debug(f"Saved snapshot to: {snapshot_file}")
        except Exception as e:
            logger.error(f"Failed to save snapshot: {e}")


_snapshot_manager: SnapshotManager | None = None


def get_snapshot_manager(storage_dir: str | Path | None = None) -> SnapshotManager:
    """Get global snapshot manager instance."""
    global _snapshot_manager
    if _snapshot_manager is None:
        _snapshot_manager = SnapshotManager(storage_dir)
    return _snapshot_manager
