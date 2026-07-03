"""Data persistence utilities."""

from __future__ import annotations

import json
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeVar

from loguru import logger

T = TypeVar("T")


class PersistenceFormat:
    """Persistence format handlers."""

    @staticmethod
    def to_json(data: Any) -> str:
        """Convert to JSON.

        Args:
            data: Data to serialize

        Returns:
            JSON string
        """
        return json.dumps(data, indent=2, default=str)

    @staticmethod
    def from_json(content: str) -> Any:
        """Load from JSON.

        Args:
            content: JSON string

        Returns:
            Deserialized data
        """
        return json.loads(content)

    @staticmethod
    def to_pickle(data: Any) -> bytes:
        """Convert to pickle.

        Args:
            data: Data to serialize

        Returns:
            Pickled bytes
        """
        return pickle.dumps(data)

    @staticmethod
    def from_pickle(content: bytes) -> Any:
        """Load from pickle.

        Args:
            content: Pickled bytes

        Returns:
            Deserialized data
        """
        return pickle.loads(content)  # nosec B301


@dataclass
class PersistenceMetadata:
    """Metadata for persisted data."""

    version: str
    format_type: str
    timestamp: str
    checksum: str | None = None


class DataPersistence:
    """Handles data persistence."""

    def __init__(self, storage_path: Path | str, *, allow_pickle: bool = False):
        """Initialize persistence.

        Args:
            storage_path: Directory for storage
            allow_pickle: Enable pickle save/load for trusted local data only
        """
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.storage_path = self.storage_path.resolve()
        self.allow_pickle = allow_pickle

    def _resolve_file(self, name: str, suffix: str) -> Path:
        """Resolve a data name to a file under the storage directory."""
        if not name or "\x00" in name:
            raise ValueError("Persistence name must be a non-empty file name")

        raw_path = Path(name)
        if raw_path.is_absolute():
            raise ValueError("Persistence name must be relative to the storage directory")

        file_path = (self.storage_path / f"{name}{suffix}").resolve()
        try:
            file_path.relative_to(self.storage_path)
        except ValueError as e:
            raise ValueError("Persistence name escapes the storage directory") from e

        if raw_path.name != name or "/" in name or "\\" in name or name in {".", ".."}:
            raise ValueError("Persistence name must be a flat file name")

        return file_path

    @staticmethod
    def _suffix_for_format(format_type: str) -> str:
        """Return the storage suffix for a supported persistence format."""
        if format_type == "json":
            return ".json"
        if format_type in {"pickle", "pkl"}:
            return ".pkl"
        raise ValueError(f"Unsupported persistence format: {format_type}")

    def _ensure_pickle_allowed(self) -> None:
        """Reject pickle operations unless explicitly enabled by trusted callers."""
        if not self.allow_pickle:
            raise ValueError("Pickle persistence is disabled by default")

    def save_json(self, name: str, data: Any) -> None:
        """Save data as JSON.

        Args:
            name: Data name
            data: Data to save
        """
        file_path = self._resolve_file(name, ".json")

        try:
            content = PersistenceFormat.to_json(data)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            logger.info(f"Saved {name} to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save {name}: {e}")
            raise

    def load_json(self, name: str) -> Any | None:
        """Load data from JSON.

        Args:
            name: Data name

        Returns:
            Loaded data or None
        """
        file_path = self._resolve_file(name, ".json")

        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return None

        try:
            content = file_path.read_text()
            data = PersistenceFormat.from_json(content)
            logger.info(f"Loaded {name} from {file_path}")
            return data
        except Exception as e:
            logger.error(f"Failed to load {name}: {e}")
            return None

    def save_pickle(self, name: str, data: Any) -> None:
        """Save data as pickle.

        Args:
            name: Data name
            data: Data to save
        """
        self._ensure_pickle_allowed()
        file_path = self._resolve_file(name, ".pkl")

        try:
            content = PersistenceFormat.to_pickle(data)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(content)
            logger.info(f"Saved {name} to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save {name}: {e}")
            raise

    def load_pickle(self, name: str) -> Any | None:
        """Load data from pickle.

        Args:
            name: Data name

        Returns:
            Loaded data or None
        """
        self._ensure_pickle_allowed()
        file_path = self._resolve_file(name, ".pkl")

        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return None

        try:
            content = file_path.read_bytes()
            data = PersistenceFormat.from_pickle(content)
            logger.info(f"Loaded {name} from {file_path}")
            return data
        except Exception as e:
            logger.error(f"Failed to load {name}: {e}")
            return None

    def delete(self, name: str, format_type: str = "json") -> bool:
        """Delete persisted data.

        Args:
            name: Data name
            format_type: Format (json or pickle)

        Returns:
            True if deleted
        """
        ext = self._suffix_for_format(format_type)
        if ext == ".pkl":
            self._ensure_pickle_allowed()
        file_path = self._resolve_file(name, ext)

        if not file_path.exists():
            return False

        try:
            file_path.unlink()
            logger.info(f"Deleted {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete {name}: {e}")
            return False

    def list_files(self) -> list[str]:
        """List all persisted files.

        Returns:
            List of file names
        """
        return sorted(
            file_path.stem
            for file_path in self.storage_path.glob("*")
            if file_path.is_file() and file_path.suffix in {".json", ".pkl"}
        )

    def get_size(self) -> int:
        """Get total storage size in bytes.

        Returns:
            Total size in bytes
        """
        total = 0
        for file_path in self.storage_path.glob("*"):
            if file_path.is_file():
                total += file_path.stat().st_size

        return total

    def clear(self) -> None:
        """Clear all persisted data."""
        for file_path in self.storage_path.glob("*"):
            if file_path.is_file():
                try:
                    file_path.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete {file_path}: {e}")

        logger.info("Cleared all persisted data")
