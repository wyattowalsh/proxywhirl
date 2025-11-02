"""Configuration management data models for ProxyWhirl.

This module defines the data structures for flexible runtime configuration management,
including multi-source loading, validation, and hot-reload capabilities.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, EmailStr, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigurationSource(str, Enum):
    """Source of a configuration value.
    
    Precedence (highest to lowest):
    1. CLI_ARGUMENT - Command-line arguments
    2. RUNTIME_UPDATE - API/programmatic updates
    3. ENVIRONMENT - Environment variables
    4. ENV_FILE - .env file
    5. YAML_FILE - YAML configuration file
    6. DEFAULT - Model defaults
    """
    
    DEFAULT        = "default"
    YAML_FILE      = "yaml_file"
    ENV_FILE       = "env_file"
    ENVIRONMENT    = "environment"
    CLI_ARGUMENT   = "cli_argument"
    RUNTIME_UPDATE = "runtime_update"


class User(BaseModel):
    """User model for authorization and audit."""
    
    id: str
    username: str
    is_admin: bool = False
    email: EmailStr | None = None
    
    def require_admin(self) -> None:
        """Raise PermissionError if not admin."""
        if not self.is_admin:
            raise PermissionError(
                f"User {self.username} does not have admin privileges"
            )


class ValidationError(BaseModel):
    """Single validation error."""
    
    field: str
    message: str
    value: Any | None = None


class ValidationResult(BaseModel):
    """Result of configuration validation."""
    
    valid: bool
    errors: list[ValidationError] = []
    warnings: list[str] = []
    
    @property
    def has_errors(self) -> bool:
        """Check if validation failed."""
        return not self.valid or len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if validation has warnings."""
        return len(self.warnings) > 0
    
    def raise_if_invalid(self) -> None:
        """Raise exception if validation failed."""
        if self.has_errors:
            error_messages = [f"{e.field}: {e.message}" for e in self.errors]
            raise ValueError(
                f"Configuration validation failed: {'; '.join(error_messages)}"
            )


@dataclass(frozen=True)
class ConfigUpdate:
    """Record of a configuration update.
    
    Immutable record for audit trail and conflict detection.
    """
    
    user_id: str
    username: str
    timestamp: datetime
    changes: dict[str, Any]
    version: int
    source: ConfigurationSource = ConfigurationSource.RUNTIME_UPDATE
    
    def get_changed_keys(self) -> set[str]:
        """Get set of configuration keys changed."""
        return set(self.changes.keys())
    
    def conflicts_with(self, other: ConfigUpdate) -> set[str]:
        """Get keys that conflict with another update.
        
        Args:
            other: Another configuration update
            
        Returns:
            Set of overlapping configuration keys
        """
        return self.get_changed_keys() & other.get_changed_keys()


class ProxyWhirlSettings(BaseSettings):
    """ProxyWhirl runtime configuration with multi-source support.
    
    This is the central configuration schema that defines all settings,
    their types, validation rules, and whether they can be hot-reloaded.
    """
    
    model_config = SettingsConfigDict(
        env_prefix='PROXYWHIRL_',
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        validate_default=True,
        extra='allow',  # Allow extra fields for extensibility
    )
    
    # Request Configuration
    timeout: int = Field(
        default=5,
        ge=1,
        le=300,
        description="Request timeout in seconds",
        json_schema_extra={'hot_reloadable': True}
    )
    
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts",
        json_schema_extra={'hot_reloadable': True}
    )
    
    # Logging Configuration
    log_level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = Field(
        default='INFO',
        description="Logging level",
        json_schema_extra={'hot_reloadable': True}
    )
    
    # Proxy Configuration
    proxy_url: SecretStr | None = Field(
        default=None,
        description="HTTP proxy URL with credentials",
        json_schema_extra={'hot_reloadable': False}  # Requires restart
    )
    
    # Storage Configuration
    database_path: str = Field(
        default='proxywhirl.db',
        description="SQLite database file path",
        json_schema_extra={'hot_reloadable': False}  # Requires restart
    )
    
    # Server Configuration (if 003-rest-api active)
    server_host: str = Field(
        default='0.0.0.0',
        description="API server bind address",
        json_schema_extra={'hot_reloadable': False}  # Requires restart
    )
    
    server_port: int = Field(
        default=8000,
        ge=1024,
        le=65535,
        description="API server port",
        json_schema_extra={'hot_reloadable': False}  # Requires restart
    )
    
    # Rate Limiting
    rate_limit_requests: int = Field(
        default=100,
        ge=1,
        description="Rate limit: requests per minute",
        json_schema_extra={'hot_reloadable': True}
    )
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Ensure log level is uppercase."""
        return v.upper()
    
    @field_validator('database_path')
    @classmethod
    def validate_database_path(cls, v: str) -> str:
        """Ensure database path has .db extension."""
        if not v.endswith('.db'):
            v += '.db'
        return v
    
    def is_hot_reloadable(self, field_name: str) -> bool:
        """Check if a field can be hot-reloaded.
        
        Args:
            field_name: Name of the configuration field
            
        Returns:
            True if field can be updated without restart
        """
        field_info = self.model_fields.get(field_name)
        if field_info and field_info.json_schema_extra:
            return field_info.json_schema_extra.get('hot_reloadable', True)
        return False
    
    def get_restart_required_fields(self) -> set[str]:
        """Get fields that require restart when changed.
        
        Returns:
            Set of field names that require application restart
        """
        return {
            name for name, field_info in self.model_fields.items()
            if field_info.json_schema_extra 
            and not field_info.json_schema_extra.get('hot_reloadable', True)
        }


class ConfigurationSnapshot(BaseModel):
    """Snapshot of configuration for export.
    
    Captures configuration state at a point in time with source attribution
    and credential redaction for safe sharing and backup.
    """
    
    settings: dict[str, Any]
    sources: dict[str, ConfigurationSource]
    timestamp: datetime
    metadata: dict[str, str]
    
    @classmethod
    def from_config(
        cls,
        config: ProxyWhirlSettings,
        sources: dict[str, ConfigurationSource]
    ) -> ConfigurationSnapshot:
        """Create snapshot from current configuration.
        
        Args:
            config: Current configuration settings
            sources: Mapping of field names to their sources
            
        Returns:
            Configuration snapshot with redacted credentials
        """
        # Convert config to dict, redacting SecretStr
        settings_dict: dict[str, Any] = {}
        for field_name, field_info in config.model_fields.items():
            value = getattr(config, field_name)
            if isinstance(value, SecretStr):
                settings_dict[field_name] = "*** REDACTED ***"
            else:
                settings_dict[field_name] = value
        
        # Calculate hot reloadable count
        hot_reloadable_count = sum(
            1 for field_info in config.model_fields.values()
            if field_info.json_schema_extra 
            and field_info.json_schema_extra.get('hot_reloadable', True)
        )
        
        return cls(
            settings=settings_dict,
            sources=sources,
            timestamp=datetime.now(timezone.utc),
            metadata={
                'hot_reloadable_count': str(hot_reloadable_count),
                'total_fields': str(len(config.model_fields)),
            }
        )
    
    def to_yaml(self) -> str:
        """Export snapshot to YAML format with source attribution.
        
        Returns:
            YAML string with comments indicating sources
        """
        lines = [
            "# ProxyWhirl Configuration Snapshot",
            f"# Generated: {self.timestamp.isoformat()}",
            f"# Merged from sources: {', '.join(sorted(set(s.value for s in self.sources.values())))}",
            "",
        ]
        
        for field_name, value in sorted(self.settings.items()):
            source = self.sources.get(field_name, ConfigurationSource.DEFAULT)
            lines.append(f"# Source: {source.value}")
            
            # Handle different value types
            if isinstance(value, str):
                # Quote strings that contain special characters
                if any(c in value for c in [':', '#', '[', ']', '{', '}', ',', '&', '*', '?', '|', '-', '<', '>', '=', '!', '%', '@']):
                    value_str = f"'{value}'"
                else:
                    value_str = value
            elif value is None:
                value_str = "null"
            elif isinstance(value, bool):
                value_str = str(value).lower()
            else:
                value_str = str(value)
            
            lines.append(f"{field_name}: {value_str}")
            lines.append("")
        
        return "\n".join(lines)
