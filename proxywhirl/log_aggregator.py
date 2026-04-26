"""Log aggregation and centralized logging for proxywhirl.

Provides:
- Log collection from multiple sources
- Log filtering and searching
- Log forwarding to external services
- Log metrics and statistics
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4

from loguru import logger


class LogLevel(str, Enum):
    """Log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogDestination(str, Enum):
    """Log destinations for forwarding."""

    FILE = "file"
    STDOUT = "stdout"
    SYSLOG = "syslog"
    CLOUDWATCH = "cloudwatch"
    DATADOG = "datadog"
    ELASTIC = "elastic"
    SPLUNK = "splunk"


@dataclass
class LogEntry:
    """Single log entry."""

    log_id: str = field(default_factory=lambda: uuid4().hex[:12])
    timestamp: float = field(default_factory=time.time)
    level: LogLevel = LogLevel.INFO
    module: str = ""
    message: str = ""
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "log_id": self.log_id,
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "level": self.level.value,
            "module": self.module,
            "message": self.message,
            "context": self.context,
        }

    def to_json(self) -> str:
        """Convert to JSON."""
        return json.dumps(self.to_dict())


class LogAggregator:
    """Centralized log aggregator."""

    def __init__(
        self,
        log_dir: Path = Path.home() / ".proxywhirl" / "logs",
        max_entries: int = 10000,
        max_file_size_mb: int = 100,
    ):
        """Initialize log aggregator.

        Args:
            log_dir: Directory for log files
            max_entries: Max entries in memory
            max_file_size_mb: Max size per log file
        """
        self.log_dir = Path(log_dir)
        self.max_entries = max_entries
        self.max_file_size_mb = max_file_size_mb
        self.entries: list[LogEntry] = []
        self.filters: dict[str, Any] = {}
        self.destinations: list[LogDestination] = [LogDestination.FILE]
        self.lock = __import__("asyncio").Lock()

        self.log_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized LogAggregator in {self.log_dir}")

    def add_entry(
        self,
        level: LogLevel,
        module: str,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Add log entry.

        Args:
            level: Log level
            module: Module name
            message: Log message
            context: Additional context

        Returns:
            Log entry ID
        """
        entry = LogEntry(
            level=level,
            module=module,
            message=message,
            context=context or {},
        )

        self.entries.append(entry)

        # Maintain max size
        if len(self.entries) > self.max_entries:
            self.entries.pop(0)

        self._persist_entry(entry)
        return entry.log_id

    def _persist_entry(self, entry: LogEntry) -> None:
        """Persist log entry to file."""
        date_str = datetime.fromtimestamp(entry.timestamp).strftime("%Y-%m-%d")
        log_file = self.log_dir / f"proxywhirl-{date_str}.jsonl"

        try:
            with log_file.open("a") as f:
                f.write(entry.to_json() + "\n")
        except Exception as e:
            logger.error(f"Failed to persist log entry: {e}")

    def search(
        self,
        query: str = "",
        level: LogLevel | None = None,
        module: str = "",
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 100,
    ) -> list[LogEntry]:
        """Search log entries.

        Args:
            query: Text query to search
            level: Filter by log level
            module: Filter by module
            start_time: Start datetime
            end_time: End datetime
            limit: Max results

        Returns:
            Matching log entries
        """
        results = []

        for entry in self.entries:
            # Level filter
            if level and entry.level != level:
                continue

            # Module filter
            if module and entry.module != module:
                continue

            # Time range filter
            if start_time:
                start_ts = start_time.timestamp()
                if entry.timestamp < start_ts:
                    continue

            if end_time:
                end_ts = end_time.timestamp()
                if entry.timestamp > end_ts:
                    continue

            # Text search
            if query:
                if query.lower() not in entry.message.lower():
                    continue

            results.append(entry)

            if len(results) >= limit:
                break

        return results

    def get_stats(self) -> dict[str, Any]:
        """Get aggregator statistics."""
        level_counts = {}
        module_counts = {}

        for entry in self.entries:
            level = entry.level.value
            level_counts[level] = level_counts.get(level, 0) + 1

            module_counts[entry.module] = module_counts.get(entry.module, 0) + 1

        return {
            "total_entries": len(self.entries),
            "by_level": level_counts,
            "by_module": module_counts,
            "destinations": [d.value for d in self.destinations],
        }

    def add_filter(self, name: str, filter_func: Any) -> None:
        """Add log filter.

        Args:
            name: Filter name
            filter_func: Filter function
        """
        self.filters[name] = filter_func
        logger.info(f"Added log filter: {name}")

    def add_destination(self, destination: LogDestination) -> None:
        """Add log destination.

        Args:
            destination: Destination type
        """
        if destination not in self.destinations:
            self.destinations.append(destination)
            logger.info(f"Added log destination: {destination.value}")

    def cleanup_old_logs(self, days: int = 30) -> int:
        """Remove log files older than N days.

        Args:
            days: Age threshold in days

        Returns:
            Number of files removed
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        removed = 0

        for log_file in self.log_dir.glob("proxywhirl-*.jsonl"):
            try:
                file_date_str = log_file.stem.replace("proxywhirl-", "")
                file_date = datetime.strptime(file_date_str, "%Y-%m-%d")

                if file_date < cutoff_date:
                    log_file.unlink()
                    removed += 1
                    logger.info(f"Removed old log file: {log_file.name}")
            except Exception as e:
                logger.error(f"Failed to cleanup log file {log_file.name}: {e}")

        return removed

    def export_logs(
        self,
        format: str = "json",
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> str:
        """Export logs in various formats.

        Args:
            format: Export format (json, csv, txt)
            start_time: Start datetime
            end_time: End datetime

        Returns:
            Formatted log data
        """
        entries = self.search(start_time=start_time, end_time=end_time, limit=10000)

        if format == "json":
            return json.dumps([e.to_dict() for e in entries], indent=2)

        elif format == "csv":
            import csv
            import io

            output = io.StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=["timestamp", "level", "module", "message"],
            )
            writer.writeheader()

            for e in entries:
                writer.writerow(
                    {
                        "timestamp": datetime.fromtimestamp(e.timestamp).isoformat(),
                        "level": e.level.value,
                        "module": e.module,
                        "message": e.message,
                    }
                )

            return output.getvalue()

        else:  # txt
            lines = []
            for e in entries:
                dt = datetime.fromtimestamp(e.timestamp).isoformat()
                lines.append(f"[{dt}] {e.level.value:8} {e.module:20} {e.message}")

            return "\n".join(lines)
