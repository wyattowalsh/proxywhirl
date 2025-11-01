"""Configuration management for ProxyWhirl CLI.

This module handles TOML configuration discovery, loading, saving, and credential encryption
for the CLI interface.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet
from pydantic import BaseModel, Field, SecretStr, field_validator

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib

import tomli_w
from platformdirs import user_config_dir


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
