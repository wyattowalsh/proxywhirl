"""Compliance audit logging and reporting for proxy usage.

Provides:
- Audit event recording
- Compliance reporting
- Data retention policies
- Audit trail verification
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4

from loguru import logger


class AuditEventType(str, Enum):
    """Types of auditable events."""

    PROXY_ADDED = "proxy_added"
    PROXY_REMOVED = "proxy_removed"
    PROXY_USED = "proxy_used"
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    CONFIG_CHANGED = "config_changed"
    POOL_ROTATED = "pool_rotated"
    REQUEST_BLOCKED = "request_blocked"
    HEALTH_CHECK = "health_check"
    DATA_EXPORTED = "data_exported"


class ComplianceLevel(str, Enum):
    """Compliance requirements."""

    BASIC = "basic"
    PCI = "pci"
    HIPAA = "hipaa"
    GDPR = "gdpr"
    SOC2 = "soc2"


@dataclass
class AuditEvent:
    """Single audit event record."""

    event_id: str = field(default_factory=lambda: uuid4().hex)
    event_type: AuditEventType = AuditEventType.PROXY_USED
    timestamp: float = field(default_factory=time.time)
    user: str = "system"
    resource: str = ""
    action: str = ""
    result: str = "success"
    details: dict[str, Any] = field(default_factory=dict)
    ip_address: str = ""
    session_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "user": self.user,
            "resource": self.resource,
            "action": self.action,
            "result": self.result,
            "details": self.details,
            "ip_address": self.ip_address,
            "session_id": self.session_id,
        }

    def compute_hash(self) -> str:
        """Compute event hash for integrity verification."""
        data = json.dumps(
            self.to_dict(),
            sort_keys=True,
            default=str,
        )
        return hashlib.sha256(data.encode()).hexdigest()


class ComplianceAuditor:
    """Compliance audit trail manager."""

    def __init__(
        self,
        audit_dir: Path = Path.home() / ".proxywhirl" / "audit",
        compliance_level: ComplianceLevel = ComplianceLevel.BASIC,
        retention_days: int = 90,
    ):
        """Initialize auditor.

        Args:
            audit_dir: Directory for audit logs
            compliance_level: Compliance level (affects retention and logging)
            retention_days: How long to retain audit logs
        """
        self.audit_dir = Path(audit_dir)
        self.compliance_level = compliance_level
        self.retention_days = retention_days
        self.events: list[AuditEvent] = []
        self.audit_dir.mkdir(parents=True, exist_ok=True)

        # Set retention based on compliance level
        if compliance_level == ComplianceLevel.HIPAA:
            self.retention_days = 2555  # 7 years
        elif (
            compliance_level == ComplianceLevel.GDPR
            or compliance_level == ComplianceLevel.SOC2
            or compliance_level == ComplianceLevel.PCI
        ):
            self.retention_days = 365  # 1 year

        logger.info(
            f"Initialized ComplianceAuditor (level={compliance_level}, retention={self.retention_days}d)"
        )

    def record_event(
        self,
        event_type: AuditEventType,
        user: str = "system",
        resource: str = "",
        action: str = "",
        result: str = "success",
        details: dict[str, Any] | None = None,
        ip_address: str = "",
        session_id: str = "",
    ) -> str:
        """Record an audit event.

        Args:
            event_type: Type of event
            user: User who performed action
            resource: Resource affected
            action: Action performed
            result: Result (success/failure)
            details: Additional details
            ip_address: Source IP
            session_id: Associated session

        Returns:
            Event ID
        """
        event = AuditEvent(
            event_type=event_type,
            user=user,
            resource=resource,
            action=action,
            result=result,
            details=details or {},
            ip_address=ip_address,
            session_id=session_id,
        )

        self.events.append(event)
        self._persist_event(event)

        logger.info(
            f"Recorded audit event: {event_type.value} ({event.event_id}) - {user}@{ip_address}",
        )

        return event.event_id

    def _persist_event(self, event: AuditEvent) -> None:
        """Persist event to disk."""
        # Use timestamp-based filename
        date_str = datetime.fromtimestamp(event.timestamp).strftime("%Y-%m-%d")
        log_file = self.audit_dir / f"audit-{date_str}.jsonl"

        try:
            with log_file.open("a") as f:
                event_dict = event.to_dict()
                event_dict["hash"] = event.compute_hash()
                f.write(json.dumps(event_dict) + "\n")
        except Exception as e:
            logger.error(f"Failed to persist audit event: {e}")

    async def generate_compliance_report(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict[str, Any]:
        """Generate compliance report.

        Args:
            start_date: Report start date
            end_date: Report end date

        Returns:
            Compliance report dictionary
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=self.retention_days)
        if not end_date:
            end_date = datetime.now()

        # Collect events
        events_by_type: dict[str, int] = {}
        events_by_user: dict[str, int] = {}
        failures: int = 0

        for event in self.events:
            event_dt = datetime.fromtimestamp(event.timestamp)
            if start_date <= event_dt <= end_date:
                event_type = event.event_type.value
                events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
                events_by_user[event.user] = events_by_user.get(event.user, 0) + 1

                if event.result == "failure":
                    failures += 1

        return {
            "compliance_level": self.compliance_level.value,
            "report_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "total_events": len(self.events),
            "events_in_period": sum(events_by_type.values()),
            "events_by_type": events_by_type,
            "events_by_user": events_by_user,
            "failures": failures,
            "failure_rate": (failures / sum(events_by_type.values() or [1])) * 100,
            "retention_days": self.retention_days,
        }

    def cleanup_expired(self) -> int:
        """Remove expired audit logs.

        Returns:
            Number of log files removed
        """
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        removed = 0

        for log_file in self.audit_dir.glob("audit-*.jsonl"):
            try:
                file_date_str = log_file.stem.replace("audit-", "")
                file_date = datetime.strptime(file_date_str, "%Y-%m-%d")

                if file_date < cutoff_date:
                    log_file.unlink()
                    removed += 1
                    logger.info(f"Removed expired audit log: {log_file.name}")
            except Exception as e:
                logger.error(f"Failed to cleanup audit log {log_file.name}: {e}")

        return removed

    def get_event_count(self) -> int:
        """Get total number of audit events."""
        return len(self.events)

    def get_failure_count(self) -> int:
        """Get number of failed events."""
        return sum(1 for e in self.events if e.result == "failure")
