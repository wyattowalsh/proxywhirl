"""Configuration management for ProxyWhirl.

This module handles both:
1. CLI configuration (TOML-based) for the command-line interface
2. Runtime configuration management (multi-source: YAML, ENV, CLI args) with hot-reload

The ConfigurationManager provides comprehensive runtime configuration with:
- Multi-source loading (CLI > ENV > YAML > Defaults)
- Runtime updates with authorization
- Hot-reload from files
- Configuration export and backup
"""

from __future__ import annotations

import argparse
import os
import signal
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

import yaml
from cryptography.fernet import Fernet
from loguru import logger
from pydantic import BaseModel, Field, SecretStr, field_validator
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib

import tomli_w
from platformdirs import user_config_dir

from proxywhirl.config_models import (
    ConfigUpdate,
    ConfigurationSnapshot,
    ConfigurationSource,
    ProxyWhirlSettings,
    User,
    ValidationError as ConfigValidationError,
    ValidationResult,
)


class ProxyConfig(BaseModel):
    """Configuration for a single proxy."""

    url: str
    username: Optional[SecretStr] = None
    password: Optional[SecretStr] = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate proxy URL format."""
        if not v.startswith(("http://", "https://", "socks4://", "socks5://")):
            raise ValueError(
                f"Invalid proxy URL scheme: {v}. "
                "Must start with http://, https://, socks4://, or socks5://"
            )
        return v


class CLIConfig(BaseModel):
    """Complete CLI configuration."""

    # Proxy pool
    proxies: list[ProxyConfig] = Field(default_factory=list, description="List of proxies")
    proxy_file: Optional[Path] = Field(None, description="Path to proxy list file")

    # Rotation settings
    rotation_strategy: str = Field("round-robin", description="Rotation strategy")
    health_check_interval: int = Field(
        300, description="Seconds between health checks (0=disabled)"
    )

    # Request settings
    timeout: int = Field(30, description="Request timeout in seconds")
    max_retries: int = Field(3, description="Max retry attempts per request")
    follow_redirects: bool = Field(True, description="Follow HTTP redirects")
    verify_ssl: bool = Field(True, description="Verify SSL certificates")

    # Output settings
    default_format: str = Field("human", description="Default output format")
    color: bool = Field(True, description="Enable colored output")
    verbose: bool = Field(False, description="Verbose output mode")

    # Storage settings
    storage_backend: str = Field("file", description="Storage backend type")
    storage_path: Optional[Path] = Field(None, description="Path for file/sqlite storage")

    # Cache settings (005-caching-mechanisms-storage)
    cache_enabled: bool = Field(True, description="Enable three-tier caching system")
    cache_l1_max_entries: int = Field(1000, description="L1 (memory) max entries")
    cache_l2_max_entries: int = Field(5000, description="L2 (JSONL) max entries")
    cache_l3_max_entries: Optional[int] = Field(None, description="L3 (SQLite) max entries (None=unlimited)")
    cache_default_ttl: int = Field(3600, ge=60, description="Default cache TTL in seconds")
    cache_cleanup_interval: int = Field(60, ge=10, description="Background cleanup interval (seconds)")
    cache_l2_dir: str = Field(".cache/proxies", description="L2 cache directory")
    cache_l3_db_path: str = Field(".cache/db/proxywhirl.db", description="L3 SQLite database path")
    cache_encryption_key_env: str = Field("PROXYWHIRL_CACHE_ENCRYPTION_KEY", description="Env var for cache encryption key")
    cache_health_invalidation: bool = Field(True, description="Auto-invalidate on health check failure")
    cache_failure_threshold: int = Field(3, ge=1, description="Failures before health invalidation")

    # Security
    encrypt_credentials: bool = Field(True, description="Encrypt credentials in config file")
    encryption_key_env: str = Field("PROXYWHIRL_KEY", description="Env var for encryption key")

    @field_validator("rotation_strategy")
    @classmethod
    def validate_strategy(cls, v: str) -> str:
        """Validate rotation strategy."""
        valid = {"round-robin", "random", "weighted", "least-used"}
        if v not in valid:
            raise ValueError(f"Invalid rotation strategy. Must be one of: {valid}")
        return v

    @field_validator("default_format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        """Validate output format."""
        valid = {"human", "json", "table", "csv"}
        if v not in valid:
            raise ValueError(f"Invalid output format. Must be one of: {valid}")
        return v

    class Config:
        """Pydantic config."""

        use_enum_values = True


def discover_config(explicit_path: Optional[Path] = None) -> Optional[Path]:
    """Discover configuration file location.

    Args:
        explicit_path: User-provided config file path (highest priority)

    Returns:
        Path to config file, or None if not found

    Priority:
        1. Explicit path provided by user
        2. ./pyproject.toml (project-local)
        3. ~/.config/proxywhirl/config.toml (user-global)
        4. None (use defaults)
    """
    # 1. Explicit path
    if explicit_path:
        if explicit_path.exists():
            return explicit_path
        raise FileNotFoundError(f"Config file not found: {explicit_path}")

    # 2. Project-local pyproject.toml
    project_config = Path.cwd() / "pyproject.toml"
    if project_config.exists():
        # Check if it has [tool.proxywhirl] section
        with open(project_config, "rb") as f:
            data = tomllib.load(f)
            if "tool" in data and "proxywhirl" in data["tool"]:
                return project_config

    # 3. User-global config
    config_dir = Path(user_config_dir("proxywhirl", "proxywhirl"))
    user_config = config_dir / "config.toml"
    if user_config.exists():
        return user_config

    # 4. No config found
    return None


def load_config(path: Optional[Path] = None) -> CLIConfig:
    """Load and validate TOML configuration.

    Args:
        path: Path to config file (if None, uses defaults)

    Returns:
        Validated CLIConfig instance
    """
    if path is None:
        # Return defaults - model_validate handles Field defaults properly
        return CLIConfig.model_validate({})

    with open(path, "rb") as f:
        data = tomllib.load(f)

    # Extract [tool.proxywhirl] section if present
    if "tool" in data and "proxywhirl" in data["tool"]:
        config_data = data["tool"]["proxywhirl"]
    else:
        config_data = data

    # Decrypt credentials if needed
    config = CLIConfig(**config_data)
    if config.encrypt_credentials:
        config = decrypt_credentials(config)

    return config


def save_config(config: CLIConfig, path: Path) -> None:
    """Save configuration to TOML file with credential encryption.

    Args:
        config: Configuration to save
        path: Destination file path
    """
    # Encrypt credentials if needed
    if config.encrypt_credentials:
        config = encrypt_credentials(config)

    # Convert to dict
    config_dict = config.model_dump(mode="json", exclude_none=True)

    # Wrap in [tool.proxywhirl] if saving to pyproject.toml
    if path.name == "pyproject.toml":
        # Load existing pyproject.toml
        if path.exists():
            with open(path, "rb") as f:
                existing = tomllib.load(f)
        else:
            existing = {}

        # Update tool.proxywhirl section
        if "tool" not in existing:
            existing["tool"] = {}
        existing["tool"]["proxywhirl"] = config_dict
        output_dict = existing
    else:
        output_dict = config_dict

    # Write TOML
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        tomli_w.dump(output_dict, f)

    # Set permissions to 600 (owner read/write only)
    os.chmod(path, 0o600)


def get_encryption_key(config: CLIConfig) -> bytes:
    """Get or generate encryption key from environment.

    Args:
        config: CLI configuration

    Returns:
        Encryption key bytes
    """
    key_env = config.encryption_key_env
    if key_env in os.environ:
        return os.environ[key_env].encode()

    # Generate new key and warn user
    new_key = Fernet.generate_key()
    print(
        f"Warning: No encryption key found in {key_env}. "
        f"Generated new key. Set it in your environment:\n"
        f"export {key_env}='{new_key.decode()}'",
        file=sys.stderr,
    )
    return new_key


def encrypt_credentials(config: CLIConfig) -> CLIConfig:
    """Encrypt all SecretStr fields in proxy configurations.

    Args:
        config: Configuration with plain credentials

    Returns:
        Configuration with encrypted credentials
    """
    if not config.proxies:
        return config

    key = get_encryption_key(config)
    fernet = Fernet(key)

    encrypted_proxies = []
    for proxy in config.proxies:
        encrypted_proxy = proxy.model_copy()
        if proxy.username:
            encrypted_username = fernet.encrypt(proxy.username.get_secret_value().encode()).decode()
            encrypted_proxy.username = SecretStr(encrypted_username)
        if proxy.password:
            encrypted_password = fernet.encrypt(proxy.password.get_secret_value().encode()).decode()
            encrypted_proxy.password = SecretStr(encrypted_password)
        encrypted_proxies.append(encrypted_proxy)

    config.proxies = encrypted_proxies
    return config


def decrypt_credentials(config: CLIConfig) -> CLIConfig:
    """Decrypt all encrypted credential fields.

    Args:
        config: Configuration with encrypted credentials

    Returns:
        Configuration with plain credentials
    """
    if not config.proxies:
        return config

    key = get_encryption_key(config)
    fernet = Fernet(key)

    decrypted_proxies = []
    for proxy in config.proxies:
        decrypted_proxy = proxy.model_copy()
        if proxy.username:
            try:
                decrypted_username = fernet.decrypt(
                    proxy.username.get_secret_value().encode()
                ).decode()
                decrypted_proxy.username = SecretStr(decrypted_username)
            except Exception:
                # Not encrypted or invalid encryption - use as-is
                pass
        if proxy.password:
            try:
                decrypted_password = fernet.decrypt(
                    proxy.password.get_secret_value().encode()
                ).decode()
                decrypted_proxy.password = SecretStr(decrypted_password)
            except Exception:
                # Not encrypted or invalid encryption - use as-is
                pass
        decrypted_proxies.append(decrypted_proxy)

    config.proxies = decrypted_proxies
    return config


# ============================================================================
# Runtime Configuration Management
# ============================================================================


class ConfigFileHandler(FileSystemEventHandler):
    """File system event handler for configuration file changes."""
    
    def __init__(
        self,
        reload_callback: Callable[[], None],
        debounce_seconds: float = 1.0
    ):
        """Initialize file handler.
        
        Args:
            reload_callback: Function to call on file change
            debounce_seconds: Seconds to wait before triggering reload
        """
        self.reload_callback = reload_callback
        self.debounce_seconds = debounce_seconds
        self._last_modified: float = 0.0
    
    def on_modified(self, event: Any) -> None:
        """Handle file modification event.
        
        Args:
            event: File system event
        """
        if event.is_directory:
            return
        
        # Debouncing: Only reload if enough time has passed
        current_time = time.time()
        if current_time - self._last_modified < self.debounce_seconds:
            return
        
        self._last_modified = current_time
        logger.info(f"Configuration file changed: {event.src_path}")
        
        # Trigger reload
        try:
            self.reload_callback()
        except Exception as e:
            logger.error(f"Configuration reload failed: {e}")


class ConfigurationManager:
    """Manages runtime configuration with multi-source loading and hot-reload.
    
    Features:
    - Multi-source loading (CLI > ENV > YAML > Defaults)
    - Runtime updates with admin authorization
    - Hot-reload from configuration files
    - Configuration export and backup
    - Concurrent update handling with conflict detection
    """
    
    def __init__(
        self,
        config: Optional[ProxyWhirlSettings] = None,
        config_path: Optional[str | Path] = None,
        reload_callback: Optional[Callable[[], None]] = None,
        debounce_seconds: float = 1.0
    ):
        """Initialize configuration manager.
        
        Args:
            config: Initial configuration (if None, loads from sources)
            config_path: Path to YAML configuration file
            reload_callback: Callback function after successful reload
            debounce_seconds: Debounce interval for file watching
        """
        self._config_lock = threading.Lock()
        self._config: ProxyWhirlSettings = config or ProxyWhirlSettings()
        self._previous_config: Optional[ProxyWhirlSettings] = None
        self._sources: dict[str, ConfigurationSource] = {}
        self._config_path: Optional[Path] = Path(config_path) if config_path else None
        self._reload_callback = reload_callback
        self._debounce_seconds = debounce_seconds
        
        # Concurrent update tracking
        self._config_version: int = 1
        self._recent_updates: list[ConfigUpdate] = []
        self._update_lock = threading.Lock()
        
        # File watching
        self._observer: Optional[Observer] = None
        
        # Track sources for each field
        self._track_sources()
    
    def _track_sources(self) -> None:
        """Track the source of each configuration field."""
        # For now, mark all current fields as DEFAULT
        # This will be enhanced when loading from actual sources
        for field_name in self._config.model_fields.keys():
            if field_name not in self._sources:
                self._sources[field_name] = ConfigurationSource.DEFAULT
    
    def get_config(self) -> ProxyWhirlSettings:
        """Get current configuration (thread-safe).
        
        Returns:
            Current configuration settings
        """
        with self._config_lock:
            return self._config
    
    def get_sources(self) -> dict[str, ConfigurationSource]:
        """Get source mapping for all configuration fields.
        
        Returns:
            Dictionary mapping field names to their sources
        """
        with self._config_lock:
            return self._sources.copy()
    
    def validate_updates(self, updates: dict[str, Any]) -> ValidationResult:
        """Validate configuration updates without applying them.
        
        Args:
            updates: Dictionary of field names to new values
            
        Returns:
            Validation result with errors and warnings
        """
        errors: list[ConfigValidationError] = []
        warnings: list[str] = []
        
        # Check if fields are hot-reloadable
        restart_required = self._config.get_restart_required_fields()
        for field_name in updates.keys():
            if field_name in restart_required:
                errors.append(ConfigValidationError(
                    field=field_name,
                    message="Cannot update restart-required field at runtime",
                    value=updates[field_name]
                ))
        
        # Try to validate with Pydantic
        if not errors:
            try:
                # Create a copy with updates
                current_dict = self._config.model_dump()
                current_dict.update(updates)
                test_config = ProxyWhirlSettings(**current_dict)
                
                # Check for warnings (e.g., very low timeout)
                if 'timeout' in updates and updates['timeout'] == 1:
                    warnings.append(
                        "timeout value is very low (1s), may cause frequent timeouts"
                    )
                
            except Exception as e:
                # Parse Pydantic validation errors
                error_msg = str(e)
                for field_name in updates.keys():
                    if field_name in error_msg:
                        errors.append(ConfigValidationError(
                            field=field_name,
                            message=error_msg,
                            value=updates.get(field_name)
                        ))
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def update_runtime_config(
        self,
        updates: dict[str, Any],
        user: User
    ) -> None:
        """Update configuration at runtime (admin-only, hot-reloadable fields).
        
        Args:
            updates: Dictionary of configuration updates
            user: User performing the update
            
        Raises:
            PermissionError: If user is not admin
            ValueError: If validation fails
        """
        # Authorization check
        user.require_admin()
        logger.info(f"Config update authorized for admin user {user.username}")
        
        # Validate updates
        validation_result = self.validate_updates(updates)
        if validation_result.has_errors:
            error_msg = "; ".join(f"{e.field}: {e.message}" for e in validation_result.errors)
            raise ValueError(f"Configuration validation failed: {error_msg}")
        
        # Log warnings
        for warning in validation_result.warnings:
            logger.warning(warning)
        
        # Check for concurrent conflicts
        with self._update_lock:
            self._check_conflicts(updates, user)
        
        # Apply updates atomically
        with self._config_lock:
            # Save previous config for rollback
            self._previous_config = self._config
            
            # Create updated configuration
            current_dict = self._config.model_dump()
            current_dict.update(updates)
            self._config = ProxyWhirlSettings(**current_dict)
            
            # Update sources
            for field_name in updates.keys():
                self._sources[field_name] = ConfigurationSource.RUNTIME_UPDATE
            
            # Increment version
            self._config_version += 1
        
        # Record update
        with self._update_lock:
            update_record = ConfigUpdate(
                user_id=user.id,
                username=user.username,
                timestamp=datetime.now(timezone.utc),
                changes=updates,
                version=self._config_version,
                source=ConfigurationSource.RUNTIME_UPDATE
            )
            self._recent_updates.append(update_record)
            self._cleanup_old_updates()
        
        # Audit logging
        changed_fields = ", ".join(f"{k}={v}" for k, v in updates.items())
        logger.info(
            f"Configuration updated by {user.username} ({user.id}): {changed_fields}"
        )
    
    def _check_conflicts(self, updates: dict[str, Any], user: User) -> None:
        """Check for concurrent update conflicts.
        
        Args:
            updates: Proposed updates
            user: User making the update
        """
        # Check recent updates (within 5 seconds)
        cutoff_time = datetime.now(timezone.utc).timestamp() - 5.0
        recent = [
            u for u in self._recent_updates
            if u.timestamp.timestamp() > cutoff_time
        ]
        
        proposed_keys = set(updates.keys())
        for recent_update in recent:
            conflict_keys = proposed_keys & recent_update.get_changed_keys()
            if conflict_keys:
                logger.warning(
                    f"Concurrent configuration conflict detected: "
                    f"User {user.username} updating fields {conflict_keys} "
                    f"previously updated by {recent_update.username} at {recent_update.timestamp}"
                )
    
    def _cleanup_old_updates(self) -> None:
        """Remove updates older than 1 hour."""
        cutoff_time = datetime.now(timezone.utc).timestamp() - 3600.0
        self._recent_updates = [
            u for u in self._recent_updates
            if u.timestamp.timestamp() > cutoff_time
        ]
    
    def rollback(self) -> bool:
        """Rollback to previous configuration.
        
        Returns:
            True if rollback successful, False if no previous config
        """
        with self._config_lock:
            if self._previous_config is None:
                logger.warning("No previous configuration to rollback to")
                return False
            
            # Swap configs
            old_config = self._config
            self._config = self._previous_config
            self._previous_config = old_config
            
            logger.info("Configuration rolled back to previous version")
            return True
    
    def reload(self) -> None:
        """Reload configuration from all sources.
        
        Validates new configuration before applying. Rolls back on failure.
        
        Raises:
            FileNotFoundError: If config file not found
            ValueError: If validation fails
        """
        logger.info("Reloading configuration from sources...")
        
        # Load from YAML file if configured
        new_config_dict: dict[str, Any] = {}
        new_sources: dict[str, ConfigurationSource] = {}
        
        if self._config_path and self._config_path.exists():
            try:
                with open(self._config_path, 'r') as f:
                    yaml_config = yaml.safe_load(f) or {}
                    new_config_dict.update(yaml_config)
                    for key in yaml_config.keys():
                        new_sources[key] = ConfigurationSource.YAML_FILE
                logger.info(f"Loaded configuration from {self._config_path}")
            except Exception as e:
                logger.error(f"Failed to load YAML config: {e}")
                raise
        
        # Validate new configuration
        try:
            new_config = ProxyWhirlSettings(**new_config_dict)
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            raise ValueError(f"Invalid configuration: {e}")
        
        # Apply atomically
        with self._config_lock:
            self._previous_config = self._config
            self._config = new_config
            self._sources.update(new_sources)
            self._config_version += 1
        
        logger.info("Configuration reloaded successfully")
        
        # Trigger callback if configured
        if self._reload_callback:
            try:
                self._reload_callback()
            except Exception as e:
                logger.error(f"Reload callback failed: {e}")
    
    def enable_file_watching(self) -> Observer:
        """Enable automatic reload on configuration file changes.
        
        Returns:
            Watchdog Observer instance (call .stop() and .join() to stop)
            
        Raises:
            ValueError: If no config_path configured
        """
        if not self._config_path:
            raise ValueError("No config_path configured for file watching")
        
        if self._observer is not None:
            logger.warning("File watching already enabled")
            return self._observer
        
        # Create event handler
        handler = ConfigFileHandler(
            reload_callback=self.reload,
            debounce_seconds=self._debounce_seconds
        )
        
        # Start observer
        self._observer = Observer()
        self._observer.schedule(
            handler,
            path=str(self._config_path.parent),
            recursive=False
        )
        self._observer.start()
        
        logger.info(f"Watching configuration file: {self._config_path}")
        return self._observer
    
    def export_config(self) -> str:
        """Export current configuration to YAML format.
        
        Returns:
            YAML string with source attribution and redacted credentials
        """
        with self._config_lock:
            snapshot = ConfigurationSnapshot.from_config(
                self._config,
                self._sources
            )
        
        return snapshot.to_yaml()
    
    def export_config_to_file(self, path: str | Path) -> None:
        """Export current configuration to a file.
        
        Args:
            path: Destination file path
        """
        yaml_content = self.export_config()
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(yaml_content)
        
        logger.info(f"Configuration exported to {output_path}")
    
    def get_config_history(
        self,
        limit: int = 50,
        since: Optional[datetime] = None
    ) -> list[ConfigUpdate]:
        """Get recent configuration update history.
        
        Args:
            limit: Maximum number of records to return
            since: Only return updates after this time
            
        Returns:
            List of configuration updates (most recent first)
        """
        with self._update_lock:
            updates = self._recent_updates.copy()
        
        # Filter by time if specified
        if since:
            updates = [u for u in updates if u.timestamp >= since]
        
        # Sort by timestamp (most recent first) and limit
        updates.sort(key=lambda u: u.timestamp, reverse=True)
        return updates[:limit]


def load_yaml_config(path: str | Path) -> dict[str, Any]:
    """Load configuration from YAML file.
    
    Args:
        path: Path to YAML configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If file does not exist
        yaml.YAMLError: If file is not valid YAML
    """
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f) or {}
    
    return config


def parse_cli_args(
    args: Optional[list[str]] = None
) -> dict[str, Any]:
    """Parse command-line arguments for configuration.
    
    Args:
        args: Command-line arguments (if None, uses sys.argv)
        
    Returns:
        Dictionary of configuration overrides from CLI
    """
    parser = argparse.ArgumentParser(
        description="ProxyWhirl Configuration",
        add_help=False  # Don't interfere with main CLI help
    )
    
    # Configuration arguments
    parser.add_argument('--timeout', type=int, help='Request timeout in seconds')
    parser.add_argument('--max-retries', type=int, dest='max_retries', help='Maximum retry attempts')
    parser.add_argument('--log-level', type=str, dest='log_level', help='Logging level')
    parser.add_argument('--config', type=str, help='Path to YAML configuration file')
    
    # Parse known args (ignore unknown for flexibility)
    parsed, _ = parser.parse_known_args(args)
    
    # Extract non-None values
    cli_config = {
        k: v for k, v in vars(parsed).items()
        if v is not None and k != 'config'
    }
    
    return cli_config


def validate_config(config_dict: dict[str, Any]) -> ValidationResult:
    """Validate configuration dictionary against schema.
    
    Args:
        config_dict: Configuration to validate
        
    Returns:
        Validation result with errors and warnings
    """
    errors: list[ConfigValidationError] = []
    warnings: list[str] = []
    
    try:
        # Validate with Pydantic
        config = ProxyWhirlSettings(**config_dict)
        
        # Add warnings for potentially problematic values
        if config.timeout == 1:
            warnings.append("timeout value is very low (1s), may cause frequent timeouts")
        
        if config.max_retries == 0:
            warnings.append("max_retries is 0, requests will not be retried")
        
    except Exception as e:
        # Parse validation errors
        error_msg = str(e)
        errors.append(ConfigValidationError(
            field='unknown',
            message=error_msg,
            value=None
        ))
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )
