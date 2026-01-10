"""Configuration management for ProxyWhirl CLI.

This module handles TOML configuration discovery, loading, saving, and credential encryption
for the CLI interface.
"""

from __future__ import annotations

import os
from pathlib import Path

from cryptography.fernet import Fernet
from loguru import logger
from pydantic import BaseModel, Field, SecretStr, field_validator

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib

import tomli_w
from platformdirs import user_config_dir


class DataStorageConfig(BaseModel):
    """Configuration for what data to persist to the database.

    All fields are configurable to allow users to:
    - Reduce storage by disabling less-critical fields
    - Improve privacy by opting out of geo/IP data
    - Balance performance vs analytics granularity
    """

    # Storage backend driver configuration
    async_driver: bool = Field(
        default=True,
        description="Enable async SQLite driver (aiosqlite) for non-blocking I/O. "
        "Currently always uses aiosqlite; this option is reserved for "
        "future compatibility enhancements and configuration consistency.",
    )

    # Connection pooling configuration
    pool_size: int = Field(
        default=5,
        ge=1,
        le=100,
        description="SQLite connection pool size (max concurrent connections)",
    )
    pool_max_overflow: int = Field(
        default=10, ge=0, le=100, description="Max overflow connections beyond pool_size"
    )
    pool_timeout: float = Field(
        default=30.0,
        ge=1.0,
        le=300.0,
        description="Timeout in seconds when getting connection from pool",
    )
    pool_recycle: int = Field(
        default=3600, ge=-1, description="Recycle connections after N seconds (-1 to disable)"
    )

    # Request timing analytics
    persist_latency_percentiles: bool = Field(
        default=True, description="Store P50, P95, P99 response time percentiles"
    )
    persist_response_time_stats: bool = Field(
        default=True, description="Store min/max/stddev response times"
    )

    # Error tracking
    persist_error_types: bool = Field(
        default=True, description="Store error type counts (timeout, ssl, etc.)"
    )
    persist_error_messages: bool = Field(
        default=True, description="Store last error message for debugging"
    )
    max_error_history: int = Field(
        default=20, ge=0, le=100, description="Maximum error history entries to keep"
    )

    # Geographic & IP intelligence (privacy-sensitive)
    persist_geo_data: bool = Field(
        default=False, description="Store country/region/city (opt-in for privacy)"
    )
    persist_ip_intelligence: bool = Field(
        default=False, description="Store is_residential/is_datacenter/is_vpn flags"
    )
    persist_coordinates: bool = Field(
        default=False, description="Store latitude/longitude coordinates"
    )

    # Protocol details
    persist_protocol_details: bool = Field(default=True, description="Store HTTP/TLS version info")
    persist_capabilities: bool = Field(
        default=True, description="Store supports_https/http2/connect flags"
    )

    # Health tracking
    persist_health_transitions: bool = Field(
        default=True, description="Store health status change history"
    )
    persist_consecutive_streaks: bool = Field(
        default=True, description="Store success/failure streak counts"
    )
    max_health_transitions: int = Field(
        default=50, ge=0, le=500, description="Maximum health transitions to keep in history"
    )

    # Source metadata
    persist_source_metadata: bool = Field(
        default=True, description="Store source name, fetch time, validation info"
    )
    persist_fetch_duration: bool = Field(default=True, description="Store how long fetch took")

    # Advanced (expensive storage)
    persist_request_logs: bool = Field(
        default=False, description="Store individual request logs (heavy storage)"
    )
    persist_daily_aggregates: bool = Field(
        default=False, description="Store daily aggregate statistics"
    )

    class Config:
        """Pydantic config."""

        extra = "forbid"


class ProxyConfig(BaseModel):
    """Configuration for a single proxy."""

    url: str
    username: SecretStr | None = None
    password: SecretStr | None = None

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
    proxy_file: Path | None = Field(None, description="Path to proxy list file")

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
    storage_path: Path | None = Field(None, description="Path for file/sqlite storage")

    # Cache settings (005-caching-mechanisms-storage)
    cache_enabled: bool = Field(True, description="Enable three-tier caching system")
    cache_l1_max_entries: int = Field(1000, description="L1 (memory) max entries")
    cache_l2_max_entries: int = Field(5000, description="L2 (JSONL) max entries")
    cache_l3_max_entries: int | None = Field(
        None, description="L3 (SQLite) max entries (None=unlimited)"
    )
    cache_default_ttl: int = Field(3600, ge=60, description="Default cache TTL in seconds")
    cache_cleanup_interval: int = Field(
        60, ge=10, description="Background cleanup interval (seconds)"
    )
    cache_l2_dir: str = Field(".cache/proxies", description="L2 cache directory")
    cache_l3_db_path: str = Field(".cache/db/proxywhirl.db", description="L3 SQLite database path")
    cache_encryption_key_env: str = Field(
        "PROXYWHIRL_CACHE_ENCRYPTION_KEY", description="Env var for cache encryption key"
    )
    cache_health_invalidation: bool = Field(
        True, description="Auto-invalidate on health check failure"
    )
    cache_failure_threshold: int = Field(3, ge=1, description="Failures before health invalidation")

    # Security
    encrypt_credentials: bool = Field(True, description="Encrypt credentials in config file")
    encryption_key_env: str = Field("PROXYWHIRL_KEY", description="Env var for encryption key")

    # API Rate Limiting
    rate_limit_by_key: bool = Field(
        True, description="Enable per-API-key rate limiting (prevents X-Forwarded-For bypass)"
    )
    rate_limit_per_key: str = Field(
        "100/minute", description="Rate limit per API key (format: 'N/minute' or 'N/hour')"
    )
    rate_limit_per_ip: str = Field(
        "100/minute",
        description="Rate limit per IP address when no API key provided (format: 'N/minute' or 'N/hour')",
    )

    # Data Storage Configuration
    data_storage: DataStorageConfig = Field(
        default_factory=DataStorageConfig,
        description="Configure which fields get persisted to the database",
    )

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


def discover_config(explicit_path: Path | None = None) -> Path | None:
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


def load_config(path: Path | None = None) -> CLIConfig:
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

    # Write TOML atomically
    path.parent.mkdir(parents=True, exist_ok=True)

    # Import atomic_write functionality
    import io

    # Serialize TOML to string first
    buffer = io.BytesIO()
    tomli_w.dump(output_dict, buffer)
    toml_content = buffer.getvalue().decode("utf-8")

    # Write atomically using temp file + rename
    from proxywhirl.utils import atomic_write

    atomic_write(path, toml_content, encoding="utf-8")

    # Set permissions to 600 (owner read/write only)
    os.chmod(path, 0o600)


def get_encryption_key(config: CLIConfig) -> bytes:
    """Get or create the encryption key.

    Priority:
    1. Environment variable (if set)
    2. Persisted key file (~/.config/proxywhirl/key.enc)
    3. Generate new key and persist it

    Args:
        config: CLI configuration

    Returns:
        Encryption key bytes
    """
    key_env = config.encryption_key_env

    # 1. Check environment variable first
    if key_env in os.environ:
        return os.environ[key_env].encode()

    # 2. Check for persisted key file
    key_file = Path.home() / ".config" / "proxywhirl" / "key.enc"

    if key_file.exists():
        try:
            return key_file.read_bytes()
        except Exception as e:
            logger.warning(f"Failed to read encryption key from {key_file}: {e}")

    # 3. Generate and persist new key
    key_file.parent.mkdir(parents=True, exist_ok=True)
    new_key = Fernet.generate_key()

    try:
        # Write key atomically to prevent corruption
        import uuid

        temp_key_file = key_file.with_suffix(f".tmp.{uuid.uuid4().hex[:8]}")
        try:
            temp_key_file.write_bytes(new_key)
            temp_key_file.chmod(0o600)  # Owner read/write only
            temp_key_file.replace(key_file)  # Atomic on POSIX
        except Exception:
            temp_key_file.unlink(missing_ok=True)
            raise

        logger.info(f"Generated new encryption key saved to {key_file}")
        logger.info(f"For portability, set: export {key_env}=$(cat {key_file})")
    except Exception as e:
        logger.warning(f"Could not persist key to {key_file}: {e}")
        logger.warning("Key will be regenerated on next run - credentials may be lost!")

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
            except Exception as e:
                # Not encrypted or invalid encryption - use as-is
                logger.warning(
                    f"Failed to decrypt username for proxy {proxy.url}: {e}. "
                    "Using value as-is (may be plaintext or encrypted with different key)."
                )
        if proxy.password:
            try:
                decrypted_password = fernet.decrypt(
                    proxy.password.get_secret_value().encode()
                ).decode()
                decrypted_proxy.password = SecretStr(decrypted_password)
            except Exception as e:
                # Not encrypted or invalid encryption - use as-is
                logger.warning(
                    f"Failed to decrypt password for proxy {proxy.url}: {e}. "
                    "Using value as-is (may be plaintext or encrypted with different key)."
                )
        decrypted_proxies.append(decrypted_proxy)

    config.proxies = decrypted_proxies
    return config
