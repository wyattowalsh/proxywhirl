"""Environment-backed settings for ProxyWhirl runtime adapters."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any, Literal, cast

from pydantic import BaseModel, Field, HttpUrl, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class ProxyConfiguration(BaseSettings):
    """Global runtime configuration for proxy rotation."""

    timeout: int = 30
    max_retries: int = 3
    verify_ssl: bool = True
    follow_redirects: bool = True
    pool_connections: int = 10
    pool_max_keepalive: int = 20
    pool_timeout: int = 30
    health_check_enabled: bool = True
    health_check_interval_seconds: int = 300
    health_check_url: HttpUrl = Field(default=cast(Any, "http://httpbin.org/ip"))
    health_check_timeout: int = 10
    log_level: str = "WARNING"
    log_format: Literal["auto", "json", "text"] = "auto"
    log_redact_credentials: bool = True
    storage_backend: Literal["memory", "sqlite", "file"] = "memory"
    storage_path: Path | None = None
    queue_enabled: bool = Field(
        default=False, description="Enable request queuing when rate limited"
    )
    queue_size: int = Field(
        default=100, ge=1, le=10000, description="Maximum number of queued requests (1-10000)"
    )

    @field_validator("timeout", "max_retries", "pool_connections", "pool_timeout")
    @classmethod
    def validate_positive(cls, value: int) -> int:
        """Ensure positive integer settings are not zero or negative."""
        if value <= 0:
            raise ValueError("Value must be positive")
        return value

    @model_validator(mode="after")
    def validate_storage(self) -> ProxyConfiguration:
        """Require a path for persistent storage backends."""
        if self.storage_backend in ("sqlite", "file") and self.storage_path is None:
            raise ValueError(f"storage_path required for {self.storage_backend} backend")
        return self

    model_config = SettingsConfigDict(
        env_prefix="PROXYWHIRL_",
        env_nested_delimiter="__",
        frozen=True,
    )


class LoggingSettings(BaseSettings):
    """Loguru configuration values parsed from the environment."""

    level: str = "WARNING"
    format: Literal["auto", "json", "text", "logfmt"] = "auto"
    redact_credentials: bool = True
    diagnose: bool = False
    backtrace: bool = True
    enqueue: bool = True
    rotation: str | None = None
    retention: str | None = None

    model_config = SettingsConfigDict(env_prefix="PROXYWHIRL_LOG_", frozen=True)


class APISettings(BaseSettings):
    """FastAPI adapter settings parsed from ``PROXYWHIRL_*`` variables."""

    storage_path: Path | None = None
    strategy: str = "round-robin"
    timeout: int = 30
    max_retries: int = 3
    require_auth: bool = False
    api_key: SecretStr | None = None
    public_metrics: bool = False
    cors_origins: Annotated[list[str], NoDecode] = Field(default_factory=list)
    cors_allow_credentials: bool = True
    rate_limit: str = "100/minute"
    api_key_rate_limit: str | None = None
    audit_log: bool = True

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        """Accept comma-separated env values or an explicit list."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def validate_cors(self) -> APISettings:
        """Reject wildcard CORS when credentials are enabled."""
        if "*" in self.cors_origins and self.cors_allow_credentials:
            raise ValueError("cannot use wildcard CORS origin with credentials enabled")
        return self

    @property
    def effective_api_key_rate_limit(self) -> str:
        """Return API-key rate limit, falling back to the default rate limit."""
        return self.api_key_rate_limit or self.rate_limit

    model_config = SettingsConfigDict(env_prefix="PROXYWHIRL_", frozen=True)


class MCPSettings(BaseSettings):
    """FastMCP adapter settings parsed from ``PROXYWHIRL_MCP_*`` variables."""

    api_key: SecretStr | None = None
    db: Path = Path("proxywhirl.db")
    log_level: Literal["debug", "info", "warning", "error"] = "info"
    allow_unauthenticated_writes: bool = False

    model_config = SettingsConfigDict(env_prefix="PROXYWHIRL_MCP_", frozen=True)


class CacheSettings(BaseSettings):
    """Cache encryption settings."""

    encryption_key: SecretStr | None = None
    key_previous: SecretStr | None = None

    model_config = SettingsConfigDict(env_prefix="PROXYWHIRL_CACHE_", frozen=True)


class TLSSettings(BaseSettings):
    """TLS-related settings for outbound validation/fetching."""

    ca_bundle: Path | None = None

    model_config = SettingsConfigDict(env_prefix="PROXYWHIRL_", frozen=True)


class AppSettings(BaseModel):
    """Grouped settings used by adapters and tests."""

    runtime: ProxyConfiguration = Field(default_factory=ProxyConfiguration)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    api: APISettings = Field(default_factory=APISettings)
    mcp: MCPSettings = Field(default_factory=MCPSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    tls: TLSSettings = Field(default_factory=TLSSettings)


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Return cached process settings."""
    return AppSettings()


def reload_settings() -> AppSettings:
    """Clear the settings cache and return freshly parsed settings."""
    get_settings.cache_clear()
    return get_settings()


__all__ = [
    "APISettings",
    "AppSettings",
    "CacheSettings",
    "LoggingSettings",
    "MCPSettings",
    "ProxyConfiguration",
    "TLSSettings",
    "get_settings",
    "reload_settings",
]
