"""Database backup and recovery utilities.

Provides backup, restore, and recovery capabilities for the proxy database.
"""

from __future__ import annotations

import gzip
import shutil
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from loguru import logger


@dataclass
class BackupInfo:
    """Information about a database backup."""

    filepath: Path
    timestamp: datetime
    size_bytes: int
    compressed: bool
    original_size_bytes: int | None = None
    checksum: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict."""
        return {
            "filepath": str(self.filepath),
            "timestamp": self.timestamp.isoformat(),
            "size_bytes": self.size_bytes,
            "compressed": self.compressed,
            "original_size_bytes": self.original_size_bytes,
            "checksum": self.checksum,
        }


class DatabaseBackup:
    """Manages database backups."""

    def __init__(self, db_path: str | Path, backup_dir: str | Path):
        """Initialize backup manager.

        Args:
            db_path: Path to database file
            backup_dir: Directory to store backups
        """
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(
        self, compress: bool = True, with_wal: bool = True
    ) -> BackupInfo:
        """Create a database backup.

        Args:
            compress: Whether to gzip compress backup
            with_wal: Whether to include WAL files

        Returns:
            Backup information

        Raises:
            FileNotFoundError: If database not found
        """
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")

        timestamp = datetime.now()
        backup_name = f"backup_{timestamp.strftime('%Y%m%d_%H%M%S')}.db"
        backup_path = self.backup_dir / backup_name

        try:
            # Copy database file
            shutil.copy2(self.db_path, backup_path)
            original_size = backup_path.stat().st_size

            # Copy WAL files if requested
            wal_files = []
            if with_wal:
                wal_path = Path(str(self.db_path) + "-wal")
                shm_path = Path(str(self.db_path) + "-shm")

                if wal_path.exists():
                    wal_backup = backup_path.with_suffix(".db-wal")
                    shutil.copy2(wal_path, wal_backup)
                    wal_files.append(wal_backup)

                if shm_path.exists():
                    shm_backup = backup_path.with_suffix(".db-shm")
                    shutil.copy2(shm_path, shm_backup)
                    wal_files.append(shm_backup)

            # Compress if requested
            final_path = backup_path
            compressed = False

            if compress:
                compressed_path = backup_path.with_suffix(".db.gz")

                with open(backup_path, "rb") as f_in:
                    with gzip.open(compressed_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)

                final_path.unlink()
                final_path = compressed_path
                compressed = True

                # Compress WAL files too
                for wal_file in wal_files:
                    compressed_wal = wal_file.with_suffix(".gz")
                    with open(wal_file, "rb") as f_in:
                        with gzip.open(compressed_wal, "wb") as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    wal_file.unlink()

            size_bytes = final_path.stat().st_size

            backup_info = BackupInfo(
                filepath=final_path,
                timestamp=timestamp,
                size_bytes=size_bytes,
                compressed=compressed,
                original_size_bytes=original_size if compressed else None,
            )

            logger.info(f"Created backup: {final_path} ({size_bytes} bytes)")
            return backup_info

        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            # Cleanup on failure
            backup_path.unlink(missing_ok=True)
            raise

    def restore_backup(
        self, backup_path: str | Path, verify: bool = True
    ) -> None:
        """Restore database from backup.

        Args:
            backup_path: Path to backup file
            verify: Whether to verify backup integrity

        Raises:
            FileNotFoundError: If backup not found
            ValueError: If backup is invalid
        """
        backup_path = Path(backup_path)

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")

        try:
            # Verify backup if requested
            if verify:
                self._verify_backup(backup_path)

            # Handle compressed backup
            if backup_path.suffix == ".gz":
                with gzip.open(backup_path, "rb") as f_in:
                    with open(self.db_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(backup_path, self.db_path)

            logger.info(f"Restored database from backup: {backup_path}")

        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            raise

    def _verify_backup(self, backup_path: Path) -> None:
        """Verify backup integrity.

        Args:
            backup_path: Path to backup file

        Raises:
            ValueError: If backup is invalid
        """
        try:
            # Create temp file for verification
            temp_path = backup_path.parent / ".verify_temp.db"

            # Handle compressed backup
            if backup_path.suffix == ".gz":
                with gzip.open(backup_path, "rb") as f_in:
                    with open(temp_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(backup_path, temp_path)

            # Try to open and query database
            conn = sqlite3.connect(temp_path)
            conn.execute("PRAGMA integrity_check;")
            conn.close()

            temp_path.unlink()
            logger.debug(f"Backup verification passed: {backup_path}")

        except Exception as e:
            logger.warning(f"Backup verification failed: {e}")
            raise ValueError(f"Backup is invalid or corrupt: {e}")

    def list_backups(self) -> list[BackupInfo]:
        """List all available backups.

        Returns:
            List of backup information, sorted by timestamp
        """
        backups = []

        for backup_file in self.backup_dir.glob("backup_*"):
            try:
                # Parse timestamp from filename
                timestamp_str = backup_file.stem.replace("backup_", "").split(".")[0]
                timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")

                info = BackupInfo(
                    filepath=backup_file,
                    timestamp=timestamp,
                    size_bytes=backup_file.stat().st_size,
                    compressed=backup_file.suffix == ".gz",
                )
                backups.append(info)
            except Exception as e:
                logger.warning(f"Failed to parse backup info: {backup_file}: {e}")

        return sorted(backups, key=lambda x: x.timestamp, reverse=True)

    def cleanup_old_backups(self, keep_days: int = 30) -> int:
        """Delete backups older than specified days.

        Args:
            keep_days: Number of days to keep backups

        Returns:
            Number of backups deleted
        """
        cutoff = datetime.now() - timedelta(days=keep_days)
        deleted = 0

        for backup in self.list_backups():
            if backup.timestamp < cutoff:
                try:
                    backup.filepath.unlink()
                    deleted += 1
                    logger.info(f"Deleted old backup: {backup.filepath}")
                except Exception as e:
                    logger.error(f"Failed to delete backup: {e}")

        return deleted

    def get_backup_statistics(self) -> dict[str, Any]:
        """Get backup statistics.

        Returns:
            Statistics dict
        """
        backups = self.list_backups()

        if not backups:
            return {
                "total_backups": 0,
                "total_size_bytes": 0,
                "oldest_backup": None,
                "newest_backup": None,
            }

        total_size = sum(b.size_bytes for b in backups)

        return {
            "total_backups": len(backups),
            "total_size_bytes": total_size,
            "oldest_backup": backups[-1].timestamp.isoformat(),
            "newest_backup": backups[0].timestamp.isoformat(),
            "backups": [b.to_dict() for b in backups[:10]],
        }
