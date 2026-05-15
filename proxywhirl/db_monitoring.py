"""Database monitoring and performance metrics."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger


def _quote_sqlite_identifier(identifier: str) -> str:
    """Quote a SQLite identifier after rejecting malformed names."""
    if "\x00" in identifier:
        raise ValueError("SQLite identifiers cannot contain null bytes")
    return f'"{identifier.replace(chr(34), chr(34) * 2)}"'


@dataclass
class TableStats:
    """Statistics for a database table."""

    table_name: str
    row_count: int
    size_bytes: int
    index_count: int
    primary_key: str | None = None


@dataclass
class QueryPerformance:
    """Query performance metrics."""

    query: str
    duration_ms: float
    timestamp: datetime


@dataclass
class DatabaseMetrics:
    """Overall database metrics."""

    timestamp: datetime
    total_size_bytes: int
    table_count: int
    index_count: int
    vacuum_last_run: datetime | None = None
    integrity_check_passed: bool | None = None


class DatabaseMonitor:
    """Monitors database health and performance."""

    def __init__(self, db_path: str | Path):
        """Initialize monitor.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self._query_log: list[QueryPerformance] = []

    def get_database_size(self) -> int:
        """Get total database size in bytes.

        Returns:
            Size in bytes
        """
        return self.db_path.stat().st_size if self.db_path.exists() else 0

    def get_table_stats(self) -> list[TableStats]:
        """Get statistics for all tables.

        Returns:
            List of table statistics
        """
        stats = []

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [row[0] for row in cursor.fetchall()]

            for table_name in tables:
                # Skip system tables
                if table_name.startswith("sqlite_"):
                    continue

                try:
                    quoted_table_name = _quote_sqlite_identifier(table_name)

                    # Count rows
                    cursor.execute(f"SELECT COUNT(*) FROM {quoted_table_name}")  # nosec B608
                    row_count = cursor.fetchone()[0]

                    # Get table size
                    try:
                        cursor.execute(
                            "SELECT COALESCE(SUM(pgsize), 0) FROM dbstat WHERE name=?",
                            (table_name,),
                        )
                        result = cursor.fetchone()
                        size_bytes = result[0] if result else 0
                    except sqlite3.OperationalError:
                        size_bytes = 0

                    # Count indexes
                    cursor.execute(
                        "SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND tbl_name=?",
                        (table_name,),
                    )
                    index_count = cursor.fetchone()[0]

                    # Get primary key
                    cursor.execute("SELECT name, pk FROM pragma_table_info(?)", (table_name,))
                    primary_key = None
                    for row in cursor.fetchall():
                        if row[1]:  # pk column
                            primary_key = row[0]
                            break

                    stats.append(
                        TableStats(
                            table_name=table_name,
                            row_count=row_count,
                            size_bytes=size_bytes or 0,
                            index_count=index_count,
                            primary_key=primary_key,
                        )
                    )
                except Exception as e:
                    logger.warning(f"Failed to get stats for {table_name}: {e}")

            conn.close()
        except Exception as e:
            logger.error(f"Failed to get table stats: {e}")

        return stats

    def get_metrics(self) -> DatabaseMetrics:
        """Get overall database metrics.

        Returns:
            Database metrics
        """
        total_size = self.get_database_size()

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Count tables
            cursor.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            table_count = cursor.fetchone()[0]

            # Count indexes
            cursor.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'"
            )
            index_count = cursor.fetchone()[0]

            conn.close()
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            table_count = 0
            index_count = 0

        return DatabaseMetrics(
            timestamp=datetime.now(),
            total_size_bytes=total_size,
            table_count=table_count,
            index_count=index_count,
        )

    def check_integrity(self) -> bool:
        """Check database integrity.

        Returns:
            True if integrity check passes
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            conn.close()
            return result == "ok"
        except Exception as e:
            logger.error(f"Integrity check failed: {e}")
            return False

    def get_slow_queries(self, limit: int = 10) -> list[QueryPerformance]:
        """Get slowest queries.

        Args:
            limit: Maximum queries to return

        Returns:
            List of slow queries
        """
        sorted_queries = sorted(self._query_log, key=lambda x: x.duration_ms, reverse=True)
        return sorted_queries[:limit]

    def log_query(self, query: str, duration_ms: float) -> None:
        """Log a query execution.

        Args:
            query: SQL query
            duration_ms: Execution duration
        """
        self._query_log.append(
            QueryPerformance(query=query, duration_ms=duration_ms, timestamp=datetime.now())
        )

        # Keep log bounded
        if len(self._query_log) > 1000:
            self._query_log = self._query_log[-1000:]

    def recommend_indexes(self) -> list[str]:
        """Recommend indexes based on query patterns.

        Returns:
            List of recommendations
        """
        recommendations = []

        # Analyze slow queries for missing indexes
        for query in self.get_slow_queries(limit=20):
            if "WHERE" in query.query.upper() and "SELECT" in query.query.upper():
                # Simple heuristic: SELECT with WHERE likely needs index
                recommendations.append(f"Consider index for: {query.query[:80]}")

        return recommendations[:5]

    def get_statistics(self) -> dict[str, Any]:
        """Get comprehensive statistics.

        Returns:
            Statistics dict
        """
        metrics = self.get_metrics()
        table_stats = self.get_table_stats()
        integrity = self.check_integrity()

        return {
            "timestamp": metrics.timestamp.isoformat(),
            "total_size_bytes": metrics.total_size_bytes,
            "table_count": metrics.table_count,
            "index_count": metrics.index_count,
            "integrity_check_passed": integrity,
            "tables": [
                {
                    "name": ts.table_name,
                    "row_count": ts.row_count,
                    "size_bytes": ts.size_bytes,
                    "index_count": ts.index_count,
                }
                for ts in table_stats
            ],
            "query_count": len(self._query_log),
            "slow_queries": [
                {
                    "query": q.query[:100],
                    "duration_ms": q.duration_ms,
                    "timestamp": q.timestamp.isoformat(),
                }
                for q in self.get_slow_queries(limit=5)
            ],
        }
