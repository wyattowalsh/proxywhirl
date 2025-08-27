"""proxywhirl/settings.py -- Production-ready configuration management

This module provides environment-based configuration using Pydantic Settings
for secure, type-safe configuration management across environments.

Features:
- Environment variable support with validation
- Secure secret handling with SecretStr
- Development/production environment detection
- CORS and security configuration
- Database and Redis connection strings
"""

from __future__ import annotations

from typing import Any, List, Optional

from pydantic import Field, SecretStr, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class APISettings(BaseSettings):
    """
    Comprehensive API configuration with environment-based settings.

    Environment Variables:
    - PROXYWHIRL_SECRET_KEY: JWT secret key (required in production)
    - PROXYWHIRL_ENVIRONMENT: dev/prod/test (default: dev)
    - PROXYWHIRL_DEBUG: Enable debug mode (default: False in prod)
    - PROXYWHIRL_CORS_ORIGINS: Comma-separated allowed origins
    - PROXYWHIRL_DATABASE_URL: Database connection string
    - PROXYWHIRL_LOG_LEVEL: Logging level (default: INFO)
    """

    model_config = SettingsConfigDict(
        env_prefix="PROXYWHIRL_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # === Core Application Settings ===
    app_name: str = "ProxyWhirl API"
    version: str = "1.0.0"
    description: str = "Comprehensive REST API for ProxyWhirl rotating proxy service"

    # === Security Settings ===
    secret_key: SecretStr = Field(
        default=SecretStr("development-key-change-in-production-must-be-32-chars-min"),
        description="JWT secret key - must be set in production",
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, ge=5, le=10080)  # 5min to 1week

    # === Environment Configuration ===
    environment: str = Field(default="development", pattern=r"^(development|production|testing)$")
    debug: bool = Field(default=True)  # Will be auto-set by validator

    # === CORS Settings ===
    cors_origins: List[str] = Field(default_factory=list)
    cors_credentials: bool = True
    cors_methods: List[str] = Field(default=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"])
    cors_headers: List[str] = Field(
        default=[
            "Accept",
            "Accept-Language",
            "Authorization",
            "Content-Language",
            "Content-Type",
            "X-Requested-With",
        ]
    )

    # === Trusted Hosts Settings ===
    trusted_hosts: List[str] = Field(default_factory=list)

    # === Rate Limiting ===
    rate_limit_enabled: bool = True
    rate_limit_default: str = "100/hour"
    rate_limit_auth: str = "10/minute"
    rate_limit_validation: str = "5/minute"

    # === Database Settings ===
    database_url: Optional[str] = None
    database_pool_size: int = Field(default=20, ge=1, le=100)
    database_max_overflow: int = Field(default=30, ge=0, le=100)
    database_pool_timeout: int = Field(default=30, ge=5, le=300)
    database_timeout: float = Field(default=30.0, ge=1.0, le=300.0)

    # === Monitoring & Observability ===
    log_level: str = Field(default="INFO", pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    enable_metrics: bool = True
    metrics_path: str = "/metrics"
    health_check_path: str = "/health"

    # === Performance Settings ===
    max_request_size: int = Field(default=10 * 1024 * 1024, ge=1024)  # 10MB default
    max_concurrent_requests: int = Field(default=100, ge=1, le=1000)
    request_timeout: float = Field(default=30.0, ge=1.0, le=300.0)

    # === WebSocket Settings ===
    websocket_ping_interval: float = Field(default=20.0, ge=5.0, le=300.0)
    websocket_ping_timeout: float = Field(default=10.0, ge=1.0, le=60.0)
    websocket_max_connections: int = Field(default=100, ge=1, le=1000)

    # === Background Tasks ===
    max_background_tasks: int = Field(default=50, ge=1, le=1000)
    task_result_ttl: int = Field(default=3600, ge=60, le=86400)  # 1 hour to 1 day

    @field_validator("environment", mode="before")
    @classmethod
    def normalize_environment(cls, v: str) -> str:
        """Normalize environment to lowercase for case insensitive matching."""
        return v.lower()

    @field_validator("log_level", mode="before")
    @classmethod
    def normalize_log_level(cls, v: str) -> str:
        """Normalize log level to uppercase for case insensitive matching."""
        return v.upper()

    @field_validator("debug")
    @classmethod
    def set_debug_from_environment(cls, v: bool, info: ValidationInfo) -> bool:
        """Auto-set debug based on environment if not explicitly provided."""
        # Override debug based on environment
        return info.data.get("environment") == "development"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse comma-separated CORS origins string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v or []

    @field_validator("trusted_hosts", mode="before")
    @classmethod
    def parse_trusted_hosts(cls, v: str | List[str]) -> List[str]:
        """Parse comma-separated trusted hosts string."""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",") if host.strip()]
        return v or []

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key_in_production(cls, v: SecretStr, info: ValidationInfo) -> SecretStr:
        """Ensure secret key is properly set in production."""
        if info.data.get("environment") == "production":
            secret_value = v.get_secret_value()
            if not secret_value or len(secret_value) < 32:
                raise ValueError("SECRET_KEY must be at least 32 characters in production")
        return v

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"

    @property
    def is_testing(self) -> bool:
        """Check if running in test mode."""
        return self.environment == "testing"

    def get_cors_config(self) -> dict[str, Any]:
        """Get CORS configuration for middleware with security-first approach."""
        origins = self.cors_origins

        # Define trusted development origins (no wildcard even in dev)
        if self.is_development and not origins:
            origins = [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:8000",
                "http://127.0.0.1:8000",
                "http://localhost:5173",  # Vite dev server
                "http://127.0.0.1:5173",  # Vite dev server
            ]

        # In production, origins must be explicitly configured - no fallback
        if self.is_production and not origins:
            raise ValueError(
                "CORS origins must be explicitly configured in production. "
                "Set PROXYWHIRL_CORS_ORIGINS environment variable with comma-separated trusted domains."
            )

        return {
            "allow_origins": origins,
            "allow_credentials": self.cors_credentials,
            "allow_methods": self.cors_methods,
            "allow_headers": self.cors_headers,
        }


class ProxyWhirlSettings(BaseSettings):
    """
    ProxyWhirl-specific configuration settings.

    Separate from API settings to allow different configuration
    of the core proxy functionality.
    """

    model_config = SettingsConfigDict(
        env_prefix="PROXYWHIRL_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # === Cache Settings ===
    cache_type: str = Field(default="memory", pattern=r"^(memory|json|sqlite)$")
    cache_path: Optional[str] = None
    cache_ttl: int = Field(default=3600, ge=60, le=86400)  # 1 hour to 1 day

    # === Validation Settings ===
    validation_timeout: float = Field(default=10.0, ge=1.0, le=60.0)
    validation_concurrency: int = Field(default=10, ge=1, le=100)
    circuit_breaker_threshold: int = Field(default=10, ge=1, le=100)

    # === Proxy Source Settings ===
    max_fetch_proxies: Optional[int] = Field(default=None, ge=1, le=10000)
    auto_validate: bool = True
    rotation_strategy: str = Field(default="round_robin")

    # === Health Check Settings ===
    health_check_interval: int = Field(default=300, ge=60, le=3600)  # 5min to 1hour
    proxy_health_threshold: float = Field(default=0.7, ge=0.1, le=1.0)


# Global settings instance
api_settings = APISettings()
proxywhirl_settings = ProxyWhirlSettings()


def get_api_settings() -> APISettings:
    """Get API settings instance."""
    return api_settings


def get_proxywhirl_settings() -> ProxyWhirlSettings:
    """Get ProxyWhirl settings instance."""
    return proxywhirl_settings


# Environment detection helpers
def is_development() -> bool:
    """Check if running in development environment."""
    return api_settings.is_development


def is_production() -> bool:
    """Check if running in production environment."""
    return api_settings.is_production


def is_testing() -> bool:
    """Check if running in testing environment."""
    return api_settings.is_testing
