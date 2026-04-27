"""
Audit logging for proxy changes and operations.

Tracks all modifications to proxy data, configuration, and operations
for compliance and debugging purposes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4


class AuditAction(str, Enum):
    """Types of audit actions."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ACTIVATE = "activate"
    DEACTIVATE = "deactivate"
    HEALTH_CHECK = "health_check"
    ROTATE = "rotate"
    FETCH = "fetch"
    VALIDATE = "validate"


@dataclass
class AuditEntry:
    """Single audit log entry."""

    entry_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    action: AuditAction = AuditAction.UPDATE
    resource_type: str = "proxy"
    resource_id: str = ""
    changes: dict[str, Any] = field(default_factory=dict)
    user_id: str | None = None
    source_ip: str | None = None
    status: str = "success"
    error_message: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp.isoformat(),
            "action": self.action.value,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "changes": self.changes,
            "user_id": self.user_id,
            "source_ip": self.source_ip,
            "status": self.status,
            "error_message": self.error_message,
        }


class AuditTrail:
    """Manages audit logging."""

    def __init__(self, max_entries: int = 10000):
        """Initialize audit trail."""
        self.entries: list[AuditEntry] = []
        self.max_entries = max_entries

    def log_action(
        self,
        action: AuditAction,
        resource_type: str,
        resource_id: str,
        changes: dict[str, Any],
        user_id: str | None = None,
        source_ip: str | None = None,
    ) -> AuditEntry:
        """Log an action."""
        entry = AuditEntry(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            changes=changes,
            user_id=user_id,
            source_ip=source_ip,
        )
        self.entries.append(entry)

        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries :]

        return entry

    def log_error(
        self,
        action: AuditAction,
        resource_type: str,
        resource_id: str,
        error_message: str,
        user_id: str | None = None,
    ) -> AuditEntry:
        """Log an error action."""
        entry = AuditEntry(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            status="error",
            error_message=error_message,
            user_id=user_id,
        )
        self.entries.append(entry)
        return entry

    def get_entries(
        self,
        resource_id: str | None = None,
        action: AuditAction | None = None,
        limit: int = 100,
    ) -> list[AuditEntry]:
        """Get audit entries with optional filtering."""
        filtered = self.entries

        if resource_id:
            filtered = [e for e in filtered if e.resource_id == resource_id]

        if action:
            filtered = [e for e in filtered if e.action == action]

        return filtered[-limit:]

    def clear(self) -> None:
        """Clear all entries."""
        self.entries = []


__all__ = ["AuditTrail", "AuditEntry", "AuditAction"]
