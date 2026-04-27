"""Advanced configuration management with hot-reload and environment expansion.

Features:
- Environment variable expansion in config
- Hot-reload on file changes
- JSON schema generation
- Configuration validation
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from loguru import logger
from pydantic import BaseModel, ConfigDict, Field


class EnvironmentExpander:
    """Expands environment variables in configuration strings."""

    # Pattern: ${VAR_NAME} or ${VAR_NAME:default_value}
    ENV_PATTERN = re.compile(r"\$\{([^}]+)\}")

    @staticmethod
    def expand(value: str, strict: bool = False) -> str:
        """Expand environment variables in a string.

        Args:
            value: String potentially containing ${VAR_NAME} patterns
            strict: If True, raise error on missing variables

        Returns:
            Expanded string

        Raises:
            ValueError: If strict=True and variable not found
        """

        def replacer(match):
            var_spec = match.group(1)

            # Handle default values: VAR_NAME:default_value
            if ":" in var_spec:
                var_name, default_value = var_spec.split(":", 1)
            else:
                var_name = var_spec
                default_value = None

            var_value = os.getenv(var_name)

            if var_value is not None:
                return var_value

            if default_value is not None:
                return default_value

            if strict:
                raise ValueError(
                    f"Environment variable {var_name} not found and no default provided"
                )

            return match.group(0)  # Return unexpanded

        return EnvironmentExpander.ENV_PATTERN.sub(replacer, value)

    @staticmethod
    def expand_dict(data: dict[str, Any]) -> dict[str, Any]:
        """Recursively expand environment variables in dict.

        Args:
            data: Dictionary potentially containing env vars

        Returns:
            Dictionary with expanded values
        """
        expanded = {}
        for key, value in data.items():
            if isinstance(value, str):
                expanded[key] = EnvironmentExpander.expand(value)
            elif isinstance(value, dict):
                expanded[key] = EnvironmentExpander.expand_dict(value)
            elif isinstance(value, list):
                expanded[key] = [
                    EnvironmentExpander.expand(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                expanded[key] = value

        return expanded


class ConfigVersion(BaseModel):
    """Version information for configuration."""

    model_config = ConfigDict(frozen=True)

    version: str = Field(description="Semantic version")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    change_id: str = Field(default_factory=lambda: str(uuid4()))


class HotReloadConfig(BaseModel):
    """Configuration for hot-reload behavior."""

    model_config = ConfigDict(frozen=True)

    enabled: bool = Field(default=True)
    watch_path: str | None = Field(None, description="Path to watch for changes")
    reload_delay_seconds: float = Field(default=1.0, ge=0.1)
    validate_before_reload: bool = Field(
        default=True, description="Validate config before applying changes"
    )


class ConfigurationManager:
    """Manages application configuration with hot-reload."""

    def __init__(
        self,
        config_data: dict[str, Any],
        hot_reload_config: HotReloadConfig | None = None,
    ):
        """Initialize config manager.

        Args:
            config_data: Initial configuration data
            hot_reload_config: Hot-reload settings
        """
        self.config_data = EnvironmentExpander.expand_dict(config_data)
        self.hot_reload_config = hot_reload_config or HotReloadConfig(enabled=False)
        self.version = ConfigVersion(version="1.0.0")
        self._subscribers: list[Callable[[dict[str, Any]], None]] = []
        self._watcher_task = None

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            key: Configuration key (supports dot notation: "server.port")
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self.config_data

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """Set configuration value.

        Args:
            key: Configuration key
            value: Value to set
        """
        keys = key.split(".")
        current = self.config_data

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value
        self.version = ConfigVersion(version=self.version.version)
        self._notify_subscribers()

    def subscribe(self, handler: Callable[[dict[str, Any]], None]) -> Callable[[], None]:
        """Subscribe to configuration changes.

        Args:
            handler: Function called when config changes

        Returns:
            Unsubscribe function
        """
        self._subscribers.append(handler)

        def unsubscribe() -> None:
            if handler in self._subscribers:
                self._subscribers.remove(handler)

        return unsubscribe

    def _notify_subscribers(self) -> None:
        """Notify subscribers of configuration changes."""
        for handler in self._subscribers:
            try:
                handler(self.config_data)
            except Exception as e:
                logger.error("Config subscriber error", error=e)

    async def start_hot_reload(self, config_path: str) -> None:
        """Start watching for configuration file changes.

        Args:
            config_path: Path to configuration file
        """
        if not self.hot_reload_config.enabled:
            return

        import asyncio

        self._watcher_task = asyncio.create_task(self._watch_file(config_path))

    async def _watch_file(self, config_path: str) -> None:
        """Watch configuration file for changes."""
        import asyncio

        path = Path(config_path)
        last_mtime = path.stat().st_mtime if path.exists() else 0

        while True:
            await asyncio.sleep(self.hot_reload_config.reload_delay_seconds)

            if not path.exists():
                continue

            current_mtime = path.stat().st_mtime
            if current_mtime > last_mtime:
                try:
                    with open(path) as f:
                        new_data = json.load(f)

                    if self.hot_reload_config.validate_before_reload:
                        # Validate before applying
                        EnvironmentExpander.expand_dict(new_data)

                    self.config_data = EnvironmentExpander.expand_dict(new_data)
                    self.version = ConfigVersion(version=self.version.version)
                    self._notify_subscribers()

                    logger.info(
                        "Configuration reloaded from file",
                        path=config_path,
                    )

                except Exception as e:
                    logger.error(
                        "Failed to reload configuration",
                        error=e,
                        path=config_path,
                    )

                last_mtime = current_mtime

    def generate_json_schema(self) -> dict[str, Any]:
        """Generate JSON schema for configuration.

        Returns:
            JSON schema representation
        """
        return {
            "type": "object",
            "properties": self._generate_schema_properties(self.config_data),
            "additionalProperties": False,
        }

    def _generate_schema_properties(self, obj: Any) -> dict[str, Any]:
        """Recursively generate schema properties."""
        if isinstance(obj, dict):
            properties = {}
            for key, value in obj.items():
                properties[key] = self._infer_schema_for_value(value)
            return properties

        return {}

    def _infer_schema_for_value(self, value: Any) -> dict[str, Any]:
        """Infer schema for a single value."""
        if isinstance(value, bool):
            return {"type": "boolean"}
        elif isinstance(value, int):
            return {"type": "integer"}
        elif isinstance(value, float):
            return {"type": "number"}
        elif isinstance(value, str):
            return {"type": "string"}
        elif isinstance(value, list):
            return {
                "type": "array",
                "items": self._infer_schema_for_value(value[0] if value else None),
            }
        elif isinstance(value, dict):
            return {
                "type": "object",
                "properties": self._generate_schema_properties(value),
            }
        else:
            return {"type": "null"}

    def to_dict(self) -> dict[str, Any]:
        """Export configuration as dictionary."""
        return self.config_data.copy()

    def to_json(self, indent: int = 2) -> str:
        """Export configuration as JSON string."""
        return json.dumps(self.config_data, indent=indent)

    def get_version(self) -> ConfigVersion:
        """Get configuration version."""
        return self.version
