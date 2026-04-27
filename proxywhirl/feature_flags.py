"""Feature flags system."""

from enum import Enum
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import os


@dataclass
class FeatureFlag:
    """Feature flag definition."""
    name: str
    enabled: bool = False
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class FeatureFlagManager:
    """Manages feature flags."""
    
    def __init__(self):
        self.flags: Dict[str, FeatureFlag] = {}
        self._load_from_env()
    
    def _load_from_env(self):
        """Load flags from environment variables."""
        for key, value in os.environ.items():
            if key.startswith('PROXYWHIRL_FEATURE_'):
                flag_name = key[18:].lower()
                self.register(
                    flag_name,
                    value.lower() in ('true', '1', 'yes')
                )
    
    def register(self, name: str, enabled: bool = False, **metadata) -> None:
        """Register a feature flag."""
        self.flags[name] = FeatureFlag(
            name=name,
            enabled=enabled,
            metadata=metadata
        )
    
    def is_enabled(self, name: str) -> bool:
        """Check if feature is enabled."""
        flag = self.flags.get(name)
        return flag.enabled if flag else False
    
    def enable(self, name: str) -> None:
        """Enable a feature."""
        if name in self.flags:
            self.flags[name].enabled = True
    
    def disable(self, name: str) -> None:
        """Disable a feature."""
        if name in self.flags:
            self.flags[name].enabled = False
    
    def toggle(self, name: str) -> None:
        """Toggle a feature."""
        if name in self.flags:
            self.flags[name].enabled = not self.flags[name].enabled
    
    def list_flags(self) -> Dict[str, bool]:
        """List all flags and their status."""
        return {name: flag.enabled for name, flag in self.flags.items()}

