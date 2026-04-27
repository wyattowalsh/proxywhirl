"""Audit trail for tracking database changes and operations.

Records all significant operations for compliance, debugging, and analysis.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from loguru import logger


class AuditAction(str, Enum):
    """Types of auditable actions."""

    PROXY_ADDED = "proxy.added"
    PROXY_REMOVED = "proxy.removed"
    PROXY_UPDATED = "proxy.updated"
    PROXY_VALIDATED = "proxy.validated"
    POOL_CREATED = "pool.created"
    POOL_DELETED = "pool.deleted"
    POOL_MODIFIED = "pool.modified"
    SOURCE_ADDED = "source.added"
    SOURCE_REMOVED = "source.removed"
    HEALTH_CHECK = "health.check"
    ROTATION_EXECUTED = "rotation.executed"
    CONFIG_CHANGED = "config.changed"
    DATABASE_EXPORTED = "database.exported"
    DATABASE_IMPORTED = "database.imported"
    DATABASE_BACKUP = "database.backup"
    SESSION_CREATED = "session.created"
    SESSION_CLOSED = "session.closed"
    AUTHENTICATION_ATTEMPT = "auth.attempt"


@dataclass
class AuditEntry:
    """Single audit trail entry."""

    action: AuditAction
    timestamp: datetime = field(default_factory=datetime.now)
    user: str | None = None
    resource_type: str | None = None
    resource_id: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error_message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for serialization."""
        return {
            "action": self.action.value,
            "timestamp": self.timestamp.isoformat(),
            "user": self.user,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": self.details,
            "success": self.success,
            "error_message": self.error_message,
        }

    def to_json_line(self) -> str:
        """Convert to JSON line for JSONL format."""
        return json.dumps(self.to_dict(), default=str)


class AuditTrail:
    """Manages audit trail recording and querying."""

    def __init__(self, max_entries: int = 10000):
        """Initialize audit trail.

        Args:
            max_entries: Maximum entries to keep in memory
        """
        self._entries: list[AuditEntry] = []
        self._max_entries = max_entries
        self._action_counts: dict[AuditAction, int] = dict.fromkeys(
            AuditAction, 0
        )

    def record(
        self,
        action: AuditAction,
        resource_type: str | None = None,
        resource_id: str | None = None,
        user: str | None = None,
        details: dict[str, Any] | None = None,
        success: bool = True,
        error_message: str | None = None,
    ) -> AuditEntry:
        """Record an audit entry.

        Args:
            action: Type of action
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            user: User performing action
            details: Additional details
            success: Whether action succeeded
            error_message: Error message if failed

        Returns:
            Recorded audit entry
        """
        entry = AuditEntry(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user=user,
            details=details or {},
            success=success,
            error_message=error_message,
        )

        self._entries.append(entry)
        self._action_counts[action] += 1

        # Keep list bounded
        if len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries :]

        # Log significant events
        log_level = "info" if success else "warning"
        logger.log(
            log_level,
            f"Audit: {action.value} "
            f"({resource_type}:{resource_id}) "
            f"by {user or 'system'}",
        )

        return entry

    def get_entries(
        self,
        action: AuditAction | None = None,
        resource_type: str | None = None,
        user: str | None = None,
        success: bool | None = None,
        limit: int = 100,
    ) -> list[AuditEntry]:
        """Query audit entries.

        Args:
            action: Filter by action type
            resource_type: Filter by resource type
            user: Filter by user
            success: Filter by success status
            limit: Maximum entries to return

        Returns:
            Matching audit entries (most recent first)
        """
        results = list(reversed(self._entries))

        if action:
            results = [e for e in results if e.action == action]

        if resource_type:
            results = [e for e in results if e.resource_type == resource_type]

        if user:
            results = [e for e in results if e.user == user]

        if success is not None:
            results = [e for e in results if e.success == success]

        return results[:limit]

    def get_action_count(self, action: AuditAction | None = None) -> int:
        """Get count of actions.

        Args:
            action: Specific action or None for all

        Returns:
            Count of actions
        """
        if action:
            return self._action_counts.get(action, 0)
        return sum(self._action_counts.values())

    def get_summary(self) -> dict[str, int]:
        """Get summary of all actions.

        Returns:
            Dict mapping action names to counts
        """
        return {
            action.value: count for action, count in self._action_counts.items()
        }

    def export_jsonl(self, filepath: str) -> None:
        """Export audit trail to JSONL file.

        Args:
            filepath: Path to output file
        """
        try:
            with open(filepath, 'w') as f:
                for entry in self._entries:
                    f.write(entry.to_json_line() + '\n')
            logger.info(f"Exported {len(self._entries)} audit entries to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export audit trail: {e}")
            raise

    def clear(self) -> int:
        """Clear all audit entries.

        Returns:
            Number of entries cleared
        """
        count = len(self._entries)
        self._entries.clear()
        self._action_counts = dict.fromkeys(AuditAction, 0)
        logger.info(f"Cleared {count} audit entries")
        return count

    def get_statistics(self) -> dict[str, Any]:
        """Get audit trail statistics.

        Returns:
            Statistics dict
        """
        if not self._entries:
            return {
                "total_entries": 0,
                "actions": {},
                "success_rate": 0.0,
                "users": [],
            }

        successful = sum(1 for e in self._entries if e.success)
        users = {e.user for e in self._entries if e.user}

        return {
            "total_entries": len(self._entries),
            "actions": self.get_summary(),
            "success_rate": successful / len(self._entries),
            "users": sorted(users),
            "earliest_entry": self._entries[0].timestamp.isoformat(),
            "latest_entry": self._entries[-1].timestamp.isoformat(),
        }
