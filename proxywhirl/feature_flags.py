"""Feature flags system with gradual rollout support."""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

from loguru import logger


class FeatureFlagStatus(str, Enum):
    """Feature flag status."""

    DISABLED = "disabled"
    ENABLED = "enabled"
    ROLLOUT = "rollout"


@dataclass
class FeatureFlag:
    """Feature flag definition."""

    name: str
    description: str | None = None
    status: FeatureFlagStatus = FeatureFlagStatus.DISABLED
    rollout_percentage: float = 0.0
    enabled_users: set[str] = field(default_factory=set)
    disabled_users: set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def enabled(self) -> bool:
        """Check if globally enabled."""
        return self.status == FeatureFlagStatus.ENABLED

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Set enabled state."""
        self.status = FeatureFlagStatus.ENABLED if value else FeatureFlagStatus.DISABLED
        self.updated_at = datetime.now(timezone.utc)

    def is_enabled_for_user(self, user_id: str) -> bool:
        """Check if feature is enabled for user.

        Args:
            user_id: User identifier

        Returns:
            True if feature enabled for user
        """
        if user_id in self.disabled_users:
            return False

        if user_id in self.enabled_users:
            return True

        if self.status == FeatureFlagStatus.ENABLED:
            return True

        if self.status == FeatureFlagStatus.ROLLOUT:
            return self._user_in_rollout(user_id)

        return False

    def _user_in_rollout(self, user_id: str) -> bool:
        """Deterministically check if user in rollout.

        Args:
            user_id: User identifier

        Returns:
            True if user in rollout
        """
        if self.rollout_percentage <= 0:
            return False
        if self.rollout_percentage >= 100:
            return True

        hash_val = int(
            hashlib.md5(
                f"{self.name}:{user_id}".encode(),
                usedforsecurity=False,
            ).hexdigest(),
            16,
        )
        bucket = (hash_val % 100) + 1
        return bucket <= self.rollout_percentage

    def enable_for_user(self, user_id: str) -> None:
        """Enable for specific user."""
        self.enabled_users.add(user_id)
        self.disabled_users.discard(user_id)
        self.updated_at = datetime.now(timezone.utc)

    def disable_for_user(self, user_id: str) -> None:
        """Disable for specific user."""
        self.disabled_users.add(user_id)
        self.enabled_users.discard(user_id)
        self.updated_at = datetime.now(timezone.utc)

    def set_rollout(self, percentage: float) -> None:
        """Set rollout percentage (0-100)."""
        self.rollout_percentage = max(0, min(100, percentage))
        self.status = FeatureFlagStatus.ROLLOUT if percentage > 0 else FeatureFlagStatus.DISABLED
        self.updated_at = datetime.now(timezone.utc)

    def enable(self) -> None:
        """Enable feature for all users."""
        self.status = FeatureFlagStatus.ENABLED
        self.rollout_percentage = 100
        self.updated_at = datetime.now(timezone.utc)

    def disable(self) -> None:
        """Disable feature for all users."""
        self.status = FeatureFlagStatus.DISABLED
        self.rollout_percentage = 0
        self.updated_at = datetime.now(timezone.utc)

    def toggle(self) -> None:
        """Toggle feature."""
        self.enabled = not self.enabled


class FeatureFlagManager:
    """Manages feature flags with gradual rollout."""

    def __init__(self):
        """Initialize manager."""
        self.flags: dict[str, FeatureFlag] = {}
        self.hooks: dict[str, list[Callable]] = {}
        self._load_from_env()

    def _load_from_env(self) -> None:
        """Load flags from environment variables."""
        for key, value in os.environ.items():
            if key.startswith("PROXYWHIRL_FEATURE_"):
                flag_name = key[18:].lower()
                enabled = value.lower() in ("true", "1", "yes")
                self.register(flag_name, enabled=enabled)

    def register(
        self,
        name: str,
        enabled: bool = False,
        description: str | None = None,
        **metadata,
    ) -> FeatureFlag:
        """Register a feature flag."""
        status = FeatureFlagStatus.ENABLED if enabled else FeatureFlagStatus.DISABLED
        flag = FeatureFlag(name=name, status=status, description=description, metadata=metadata)
        self.flags[name] = flag
        logger.debug(f"Registered feature flag '{name}'")
        return flag

    def is_enabled(self, name: str, user_id: str = "default") -> bool:
        """Check if feature is enabled."""
        flag = self.flags.get(name)
        if not flag:
            logger.warning(f"Feature flag '{name}' not found")
            return False
        return flag.is_enabled_for_user(user_id)

    def enable(self, name: str) -> None:
        """Enable a feature."""
        if name in self.flags:
            self.flags[name].enable()
            self._notify_hooks(name)

    def disable(self, name: str) -> None:
        """Disable a feature."""
        if name in self.flags:
            self.flags[name].disable()
            self._notify_hooks(name)

    def toggle(self, name: str) -> None:
        """Toggle a feature."""
        if name in self.flags:
            self.flags[name].toggle()
            self._notify_hooks(name)

    def set_rollout(self, name: str, percentage: float) -> bool:
        """Set rollout percentage."""
        if name not in self.flags:
            return False
        self.flags[name].set_rollout(percentage)
        self._notify_hooks(name)
        return True

    def enable_for_user(self, name: str, user_id: str) -> bool:
        """Enable flag for specific user."""
        if name not in self.flags:
            return False
        self.flags[name].enable_for_user(user_id)
        return True

    def disable_for_user(self, name: str, user_id: str) -> bool:
        """Disable flag for specific user."""
        if name not in self.flags:
            return False
        self.flags[name].disable_for_user(user_id)
        return True

    def register_hook(self, name: str, callback: Callable[[FeatureFlag], None]) -> None:
        """Register callback for flag changes."""
        if name not in self.hooks:
            self.hooks[name] = []
        self.hooks[name].append(callback)

    def _notify_hooks(self, name: str) -> None:
        """Notify callbacks of flag change."""
        if name in self.hooks and name in self.flags:
            for callback in self.hooks[name]:
                try:
                    callback(self.flags[name])
                except Exception as e:
                    logger.error(f"Hook error for '{name}': {e}")

    def list_flags(self) -> dict[str, bool]:
        """List all flags and their status."""
        return {name: flag.enabled for name, flag in self.flags.items()}

    def get_all_flags(self) -> dict[str, FeatureFlag]:
        """Get all flag objects."""
        return self.flags.copy()

    def get_flag(self, name: str) -> FeatureFlag | None:
        """Get flag by name."""
        return self.flags.get(name)

    def get_stats(self) -> dict[str, Any]:
        """Get statistics."""
        return {
            "total_flags": len(self.flags),
            "enabled": sum(1 for f in self.flags.values() if f.status == FeatureFlagStatus.ENABLED),
            "rollout": sum(1 for f in self.flags.values() if f.status == FeatureFlagStatus.ROLLOUT),
            "disabled": sum(
                1 for f in self.flags.values() if f.status == FeatureFlagStatus.DISABLED
            ),
        }


# Global manager instance
_manager = FeatureFlagManager()


def get_flag_manager() -> FeatureFlagManager:
    """Get global flag manager."""
    return _manager


def is_enabled(name: str, user_id: str = "default") -> bool:
    """Check if feature is enabled (convenience function)."""
    return _manager.is_enabled(name, user_id)
