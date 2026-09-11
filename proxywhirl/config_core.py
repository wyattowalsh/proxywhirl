"""Shared configuration defaults — single source of truth for cross-adapter knobs.

CLI TOML (``config.py``), env-backed settings (``settings.py``), and the API
``ConfigurationSettings`` model all pull shared defaults from this module so
timeouts, retries, storage, and logging levels cannot drift independently.

Adapter-specific fields (e.g. Wave 1A ``expose_docs`` / ``bind_host`` /
``require_auth``, CLI cache/encryption knobs) stay on their respective models.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# --- Canonical numeric / string defaults -------------------------------------

DEFAULT_TIMEOUT: int = 30
DEFAULT_MAX_RETRIES: int = 3
DEFAULT_VERIFY_SSL: bool = True
DEFAULT_FOLLOW_REDIRECTS: bool = True
DEFAULT_HEALTH_CHECK_INTERVAL_SECONDS: int = 300
DEFAULT_ROTATION_STRATEGY: str = "round-robin"
DEFAULT_LOG_LEVEL: str = "WARNING"
DEFAULT_LOG_FORMAT: Literal["auto", "json", "text"] = "auto"
DEFAULT_LOG_REDACT_CREDENTIALS: bool = True
DEFAULT_STORAGE_BACKEND: Literal["memory", "sqlite", "file"] = "memory"
# CLI prefers on-disk persistence when no explicit backend is configured.
DEFAULT_CLI_STORAGE_BACKEND: Literal["memory", "sqlite", "file"] = "file"
DEFAULT_RATE_LIMIT: str = "100/minute"
DEFAULT_RATE_LIMIT_DEFAULT: int = 100
DEFAULT_RATE_LIMIT_REQUEST_ENDPOINT: int = 50
DEFAULT_CORS_ORIGINS: tuple[str, ...] = ()


class SharedRuntimeConfig(BaseModel):
    """Canonical shared knobs used by CLI, env, and API adapters.

    This model is not loaded from the environment directly — adapters wrap or
    copy these defaults into ``BaseSettings`` / TOML / API response models.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    timeout: int = Field(default=DEFAULT_TIMEOUT, gt=0)
    max_retries: int = Field(default=DEFAULT_MAX_RETRIES, ge=0)
    verify_ssl: bool = DEFAULT_VERIFY_SSL
    follow_redirects: bool = DEFAULT_FOLLOW_REDIRECTS
    health_check_interval_seconds: int = Field(default=DEFAULT_HEALTH_CHECK_INTERVAL_SECONDS, ge=0)
    rotation_strategy: str = DEFAULT_ROTATION_STRATEGY
    log_level: str = DEFAULT_LOG_LEVEL
    log_format: Literal["auto", "json", "text"] = DEFAULT_LOG_FORMAT
    log_redact_credentials: bool = DEFAULT_LOG_REDACT_CREDENTIALS
    storage_backend: Literal["memory", "sqlite", "file"] = DEFAULT_STORAGE_BACKEND
    rate_limit: str = DEFAULT_RATE_LIMIT
    rate_limit_default: int = Field(default=DEFAULT_RATE_LIMIT_DEFAULT, ge=1)
    rate_limit_request_endpoint: int = Field(default=DEFAULT_RATE_LIMIT_REQUEST_ENDPOINT, ge=1)


def shared_runtime_defaults() -> SharedRuntimeConfig:
    """Return a frozen instance of the canonical shared defaults."""
    return SharedRuntimeConfig()


def shared_runtime_defaults_dict() -> dict[str, Any]:
    """Return shared defaults as a plain dict (handy for tests / mapping)."""
    return shared_runtime_defaults().model_dump()


def configuration_settings_defaults() -> dict[str, Any]:
    """Defaults dict for API ``ConfigurationSettings`` construction."""
    shared = shared_runtime_defaults()
    return {
        "rotation_strategy": shared.rotation_strategy,
        "timeout": shared.timeout,
        "max_retries": shared.max_retries,
        "rate_limits": {
            "default_limit": shared.rate_limit_default,
            "request_endpoint_limit": shared.rate_limit_request_endpoint,
        },
        "auth_enabled": False,
        "cors_origins": list(DEFAULT_CORS_ORIGINS),
    }


__all__ = [
    "DEFAULT_CLI_STORAGE_BACKEND",
    "DEFAULT_CORS_ORIGINS",
    "DEFAULT_FOLLOW_REDIRECTS",
    "DEFAULT_HEALTH_CHECK_INTERVAL_SECONDS",
    "DEFAULT_LOG_FORMAT",
    "DEFAULT_LOG_LEVEL",
    "DEFAULT_LOG_REDACT_CREDENTIALS",
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_RATE_LIMIT",
    "DEFAULT_RATE_LIMIT_DEFAULT",
    "DEFAULT_RATE_LIMIT_REQUEST_ENDPOINT",
    "DEFAULT_ROTATION_STRATEGY",
    "DEFAULT_STORAGE_BACKEND",
    "DEFAULT_TIMEOUT",
    "DEFAULT_VERIFY_SSL",
    "SharedRuntimeConfig",
    "configuration_settings_defaults",
    "shared_runtime_defaults",
    "shared_runtime_defaults_dict",
]
