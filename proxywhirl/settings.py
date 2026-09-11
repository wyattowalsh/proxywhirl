"""Environment-backed settings for ProxyWhirl runtime adapters."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any, Literal, cast

from pydantic import BaseModel, Field, HttpUrl, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

from proxywhirl.config_core import (
    DEFAULT_FOLLOW_REDIRECTS,
    DEFAULT_HEALTH_CHECK_INTERVAL_SECONDS,
    DEFAULT_LOG_FORMAT,
    DEFAULT_LOG_LEVEL,
    DEFAULT_LOG_REDACT_CREDENTIALS,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RATE_LIMIT,
    DEFAULT_ROTATION_STRATEGY,
    DEFAULT_STORAGE_BACKEND,
    DEFAULT_TIMEOUT,
    DEFAULT_VERIFY_SSL,
)


class ProxyConfiguration(BaseSettings):
    """Global runtime configuration for proxy rotation."""

    timeout: int = DEFAULT_TIMEOUT
    max_retries: int = DEFAULT_MAX_RETRIES
    verify_ssl: bool = DEFAULT_VERIFY_SSL
    follow_redirects: bool = DEFAULT_FOLLOW_REDIRECTS
    pool_connections: int = 10
    pool_max_keepalive: int = 20
    pool_timeout: int = DEFAULT_TIMEOUT
    health_check_enabled: bool = True
    health_check_interval_seconds: int = DEFAULT_HEALTH_CHECK_INTERVAL_SECONDS
    health_check_url: HttpUrl = Field(default=cast(Any, "http://httpbin.org/ip"))
    health_check_timeout: int = 10
    log_level: str = DEFAULT_LOG_LEVEL
    log_format: Literal["auto", "json", "text"] = DEFAULT_LOG_FORMAT
    log_redact_credentials: bool = DEFAULT_LOG_REDACT_CREDENTIALS
    storage_backend: Literal["memory", "sqlite", "file"] = DEFAULT_STORAGE_BACKEND
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

    level: str = DEFAULT_LOG_LEVEL
    format: Literal["auto", "json", "text", "logfmt"] = DEFAULT_LOG_FORMAT
    redact_credentials: bool = DEFAULT_LOG_REDACT_CREDENTIALS
    diagnose: bool = False
    backtrace: bool = True
    enqueue: bool = True
    rotation: str | None = None
    retention: str | None = None

    model_config = SettingsConfigDict(env_prefix="PROXYWHIRL_LOG_", frozen=True)


class APISettings(BaseSettings):
    """FastAPI adapter settings parsed from ``PROXYWHIRL_*`` variables."""

    storage_path: Path | None = None
    strategy: str = DEFAULT_ROTATION_STRATEGY
    timeout: int = DEFAULT_TIMEOUT
    max_retries: int = DEFAULT_MAX_RETRIES
    # Wave 1A security posture — keep on the API adapter (not in SharedRuntimeConfig).
    require_auth: bool = False
    api_key: SecretStr | None = None
    public_metrics: bool = False
    expose_docs: bool | None = None
    cors_origins: Annotated[list[str], NoDecode] = Field(default_factory=list)
    cors_allow_credentials: bool = True
    rate_limit: str = DEFAULT_RATE_LIMIT
    api_key_rate_limit: str | None = None
    audit_log: bool = True
    bind_host: str = "127.0.0.1"
    max_proxied_response_bytes: int = Field(default=1_048_576, ge=1024, le=16_777_216)
    health_check_max_proxies: int = Field(default=100, ge=1, le=1000)
    health_check_concurrency: int = Field(default=10, ge=1, le=100)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        """Accept comma-separated env values or an explicit list."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("expose_docs", mode="before")
    @classmethod
    def parse_expose_docs(cls, value: object) -> object:
        """Accept common truthy/falsey env strings; leave unset as None."""
        if value is None or value == "":
            return None
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on"}:
                return True
            if normalized in {"0", "false", "no", "off"}:
                return False
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

    @property
    def docs_enabled(self) -> bool:
        """Whether OpenAPI docs surfaces are exposed.

        Defaults to False when ``require_auth`` is enabled (production posture),
        and True for local unauthenticated development unless overridden.
        """
        if self.expose_docs is not None:
            return self.expose_docs
        return not self.require_auth

    model_config = SettingsConfigDict(env_prefix="PROXYWHIRL_", frozen=True)


class MCPSettings(BaseSettings):
    """FastMCP adapter settings parsed from ``PROXYWHIRL_MCP_*`` variables."""

    api_key: SecretStr | None = None
    db: Path = Path("proxywhirl.db")
    log_level: Literal["debug", "info", "warning", "error"] = "info"
    allow_unauthenticated_writes: bool = False
    auto_fetch: bool = Field(
        default=False,
        description="Auto-fetch public proxies on cold start (also enabled when api_key is set)",
    )

    @field_validator("auto_fetch", mode="before")
    @classmethod
    def _parse_auto_fetch(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on"}
        return value

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
