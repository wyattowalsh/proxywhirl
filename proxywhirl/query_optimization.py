"""
Database query optimization utilities and strategies.

Provides tools for identifying and optimizing slow queries, managing
indexes, and improving database performance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum


class QueryType(str, Enum):
    """Types of database queries."""

    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    INDEX = "index"


@dataclass
class QueryMetrics:
    """Metrics for a database query."""

    query_id: str
    query_text: str
    query_type: QueryType
    execution_time_ms: float
    rows_affected: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_slow: bool = False
    index_used: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "query_id": self.query_id,
            "query_text": self.query_text,
            "query_type": self.query_type.value,
            "execution_time_ms": self.execution_time_ms,
            "rows_affected": self.rows_affected,
            "timestamp": self.timestamp.isoformat(),
            "is_slow": self.is_slow,
            "index_used": self.index_used,
        }


class QueryOptimizer:
    """Optimizes database queries."""

    SLOW_QUERY_THRESHOLD_MS = 100

    def __init__(self):
        """Initialize optimizer."""
        self.queries: list[QueryMetrics] = []
        self.slow_queries: list[QueryMetrics] = []
        self.index_suggestions: dict[str, list[str]] = {}

    def track_query(self, metrics: QueryMetrics) -> None:
        """Track query metrics."""
        metrics.is_slow = metrics.execution_time_ms > self.SLOW_QUERY_THRESHOLD_MS
        self.queries.append(metrics)

        if metrics.is_slow:
            self.slow_queries.append(metrics)

    def get_slow_queries(self, limit: int = 50) -> list[QueryMetrics]:
        """Get slow queries."""
        return sorted(
            self.slow_queries,
            key=lambda x: x.execution_time_ms,
            reverse=True,
        )[:limit]

    def suggest_indexes(self, table_name: str) -> list[str]:
        """Suggest indexes for a table."""
        suggestions = []

        slow_for_table = [
            q for q in self.slow_queries if table_name.lower() in q.query_text.lower()
        ]

        if len(slow_for_table) > 5:
            suggestions.append(f"Table {table_name} has many slow queries")

        where_clauses = [
            q.query_text.split("WHERE")[1] for q in slow_for_table if "WHERE" in q.query_text
        ]

        if where_clauses:
            suggestions.append(f"Consider indexes on WHERE clause columns in {table_name}")

        self.index_suggestions[table_name] = suggestions
        return suggestions

    def get_query_statistics(
        self,
        time_range_minutes: int = 60,
    ) -> dict:
        """Get query statistics."""
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=time_range_minutes)
        recent = [q for q in self.queries if q.timestamp > cutoff]

        if not recent:
            return {
                "total_queries": 0,
                "avg_execution_ms": 0,
                "slow_query_count": 0,
                "slow_percentage": 0,
            }

        slow_count = len([q for q in recent if q.is_slow])
        total_time = sum(q.execution_time_ms for q in recent)

        return {
            "total_queries": len(recent),
            "avg_execution_ms": total_time / len(recent),
            "slow_query_count": slow_count,
            "slow_percentage": (slow_count / len(recent)) * 100,
            "total_time_ms": total_time,
        }

    def get_optimization_report(self) -> dict:
        """Generate optimization report."""
        stats = self.get_query_statistics()
        slow = self.get_slow_queries(10)

        return {
            "statistics": stats,
            "top_slow_queries": [q.to_dict() for q in slow],
            "index_suggestions": self.index_suggestions,
        }


__all__ = ["QueryOptimizer", "QueryMetrics", "QueryType"]
