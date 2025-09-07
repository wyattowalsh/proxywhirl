"""proxywhirl/cli/state.py -- State management classes for CLI"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from rich.console import Console

from ..caches import CacheType
from ..config import ProxyWhirlSettings
from .theme import PROXYWHIRL_THEME


class ProxyWhirlError(Exception):
    """Custom exception with Rich formatting support"""

    def __init__(self, message: str, suggestion: Optional[str] = None):
        self.message = message
        self.suggestion = suggestion
        super().__init__(message)


class ProxyWhirlState:
    """Shared state across CLI commands for better context management"""

    def __init__(self):
        self.console = Console(theme=PROXYWHIRL_THEME)
        self.debug = False
        self.quiet = False
        self.cache_type = CacheType.MEMORY
        self.cache_path: Optional[Path] = None
        self.config: Optional[ProxyWhirlSettings] = None

    def load_config_file(self, config_path: Optional[Path]) -> None:
        """Load configuration from file."""
        try:
            if config_path and config_path.exists():
                self.config = ProxyWhirlSettings.from_file(config_path)
                if not self.quiet:
                    self.console.print(
                        f"✅ [success]Configuration loaded from {config_path}[/success]"
                    )
            elif config_path:
                raise ProxyWhirlError(
                    f"Configuration file not found: {config_path}",
                    "Check the file path and ensure the file exists.",
                )
            else:
                # Use default configuration
                self.config = ProxyWhirlSettings()
        except Exception as e:
            if isinstance(e, ProxyWhirlError):
                raise
            raise ProxyWhirlError(
                f"Failed to load configuration: {e}",
                "Ensure the YAML file is valid and properly formatted.",
            )

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value with fallback to default."""
        if self.config is None:
            return default
        return getattr(self.config, key, default)
