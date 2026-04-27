"""User consent and privacy management for ProxyWhirl.

Manages user consent preferences for data collection,
analytics, and tracking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from loguru import logger


class ConsentType(str, Enum):
    """Types of user consent."""

    ANALYTICS = "analytics"
    TELEMETRY = "telemetry"
    MARKETING = "marketing"
    CRASH_REPORTING = "crash_reporting"
    PERFORMANCE_MONITORING = "performance_monitoring"


@dataclass
class ConsentRecord:
    """Record of user consent."""

    user_id: str
    consent_type: ConsentType
    granted: bool
    granted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Check if consent is expired.

        Returns:
            True if expired
        """
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    def is_active(self) -> bool:
        """Check if consent is active.

        Returns:
            True if active and not expired
        """
        return self.granted and not self.is_expired()


class ConsentManager:
    """Manages user consent preferences."""

    def __init__(self) -> None:
        """Initialize consent manager."""
        self._consents: dict[str, dict[ConsentType, ConsentRecord]] = {}
        logger.debug("ConsentManager initialized")

    def grant_consent(
        self,
        user_id: str,
        consent_type: ConsentType,
        expires_in_days: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Grant consent for user.

        Args:
            user_id: User ID
            consent_type: Type of consent
            expires_in_days: Days until expiration
            metadata: Optional metadata

        Returns:
            True if granted
        """
        from datetime import timedelta

        if user_id not in self._consents:
            self._consents[user_id] = {}

        expires_at = None
        if expires_in_days:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

        record = ConsentRecord(
            user_id=user_id,
            consent_type=consent_type,
            granted=True,
            expires_at=expires_at,
            metadata=metadata or {},
        )
        self._consents[user_id][consent_type] = record
        logger.info(f"Consent granted: {user_id} - {consent_type.value}")
        return True

    def revoke_consent(self, user_id: str, consent_type: ConsentType) -> bool:
        """Revoke consent for user.

        Args:
            user_id: User ID
            consent_type: Type of consent

        Returns:
            True if revoked
        """
        if user_id not in self._consents:
            return False

        if consent_type in self._consents[user_id]:
            record = self._consents[user_id][consent_type]
            record.granted = False
            logger.info(f"Consent revoked: {user_id} - {consent_type.value}")
            return True

        return False

    def has_active_consent(self, user_id: str, consent_type: ConsentType) -> bool:
        """Check if user has active consent.

        Args:
            user_id: User ID
            consent_type: Type of consent

        Returns:
            True if has active consent
        """
        if user_id not in self._consents:
            return False

        if consent_type not in self._consents[user_id]:
            return False

        record = self._consents[user_id][consent_type]
        return record.is_active()

    def get_user_consents(self, user_id: str) -> dict[str, bool]:
        """Get all consent statuses for user.

        Args:
            user_id: User ID

        Returns:
            Dictionary of consent type to status
        """
        if user_id not in self._consents:
            return {}

        return {ct.value: record.is_active() for ct, record in self._consents[user_id].items()}

    def export_metrics(self) -> dict[str, Any]:
        """Export consent metrics.

        Returns:
            Dictionary of metrics
        """
        total_users = len(self._consents)
        consent_counts: dict[str, int] = {}

        for user_consents in self._consents.values():
            for ct, record in user_consents.items():
                if record.is_active():
                    key = ct.value
                    consent_counts[key] = consent_counts.get(key, 0) + 1

        return {
            "total_users": total_users,
            "active_consents_by_type": consent_counts,
        }
