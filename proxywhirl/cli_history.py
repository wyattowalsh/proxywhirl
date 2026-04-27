"""Command history search and management.

Provides utilities for searching and managing CLI command history.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger


@dataclass
class HistoryEntry:
    """A single command history entry."""

    command: str
    timestamp: datetime
    exit_code: int | None = None
    duration_seconds: float = 0.0
    tags: list[str] = field(default_factory=list)


class CommandHistory:
    """Manages CLI command history.

    Example:
        >>> history = CommandHistory()
        >>> history.add("proxywhirl validate")
        >>> results = history.search("validate")
    """

    def __init__(self, history_file: str | Path | None = None) -> None:
        """Initialize command history.

        Args:
            history_file: Path to history file
        """
        self.entries: list[HistoryEntry] = []
        self.history_file = history_file or Path.home() / ".proxywhirl" / "command_history.jsonl"

    def add(
        self,
        command: str,
        exit_code: int | None = None,
        duration_seconds: float = 0.0,
        tags: list[str] | None = None,
    ) -> None:
        """Add command to history.

        Args:
            command: Command string
            exit_code: Exit code of command
            duration_seconds: How long command took
            tags: Tags for categorization
        """
        entry = HistoryEntry(
            command=command,
            timestamp=datetime.now(),
            exit_code=exit_code,
            duration_seconds=duration_seconds,
            tags=tags or [],
        )
        self.entries.append(entry)
        self._save_entry(entry)
        logger.debug(f"Added history entry: {command}")

    def search(
        self,
        query: str,
        limit: int = 10,
        fuzzy: bool = False,
    ) -> list[HistoryEntry]:
        """Search command history.

        Args:
            query: Search query
            limit: Max results to return
            fuzzy: Use fuzzy matching if True

        Returns:
            Matching history entries
        """
        results = []

        for entry in reversed(self.entries):
            if fuzzy:
                if self._fuzzy_match(query, entry.command):
                    results.append(entry)
            else:
                if query.lower() in entry.command.lower():
                    results.append(entry)

            if len(results) >= limit:
                break

        return results

    def search_by_tag(
        self,
        tag: str,
        limit: int = 10,
    ) -> list[HistoryEntry]:
        """Search history by tag.

        Args:
            tag: Tag to search for
            limit: Max results to return

        Returns:
            Matching history entries
        """
        results = [entry for entry in reversed(self.entries) if tag in entry.tags]
        return results[:limit]

    def get_recent(self, count: int = 10) -> list[HistoryEntry]:
        """Get most recent commands.

        Args:
            count: Number of commands to return

        Returns:
            Recent history entries
        """
        return list(reversed(self.entries[-count:]))

    def clear(self) -> None:
        """Clear all history."""
        self.entries = []
        if self.history_file.exists():
            self.history_file.unlink()
        logger.info("History cleared")

    def get_stats(self) -> dict[str, Any]:
        """Get history statistics.

        Returns:
            Dict with statistics
        """
        if not self.entries:
            return {
                "total_commands": 0,
                "success_count": 0,
                "failure_count": 0,
                "success_rate": 0.0,
                "total_time": 0.0,
            }

        successful = [e for e in self.entries if e.exit_code == 0]
        failed = [e for e in self.entries if e.exit_code != 0]
        total_time = sum(e.duration_seconds for e in self.entries)

        return {
            "total_commands": len(self.entries),
            "success_count": len(successful),
            "failure_count": len(failed),
            "success_rate": (len(successful) / len(self.entries) * 100 if self.entries else 0),
            "total_time": total_time,
            "avg_time": total_time / len(self.entries) if self.entries else 0,
        }

    def _fuzzy_match(self, query: str, text: str) -> bool:
        """Perform fuzzy matching.

        Args:
            query: Search query
            text: Text to match against

        Returns:
            True if fuzzy match successful
        """
        query_lower = query.lower()
        text_lower = text.lower()
        idx = 0

        for char in query_lower:
            idx = text_lower.find(char, idx)
            if idx == -1:
                return False
            idx += 1

        return True

    def _save_entry(self, entry: HistoryEntry) -> None:
        """Save single entry to file.

        Args:
            entry: Entry to save
        """
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)

            import json

            with open(self.history_file, "a") as f:
                data = {
                    "command": entry.command,
                    "timestamp": entry.timestamp.isoformat(),
                    "exit_code": entry.exit_code,
                    "duration_seconds": entry.duration_seconds,
                    "tags": entry.tags,
                }
                f.write(json.dumps(data) + "\n")
        except Exception as e:
            logger.warning(f"Failed to save history entry: {e}")

    def load(self) -> None:
        """Load history from file."""
        if not self.history_file.exists():
            return

        try:
            import json

            with open(self.history_file) as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            entry = HistoryEntry(
                                command=data["command"],
                                timestamp=datetime.fromisoformat(data["timestamp"]),
                                exit_code=data.get("exit_code"),
                                duration_seconds=data.get("duration_seconds", 0.0),
                                tags=data.get("tags", []),
                            )
                            self.entries.append(entry)
                        except (json.JSONDecodeError, ValueError) as e:
                            logger.warning(f"Failed to parse history entry: {e}")
        except Exception as e:
            logger.warning(f"Failed to load history: {e}")
