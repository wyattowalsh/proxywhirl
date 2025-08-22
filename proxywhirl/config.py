"""proxywhirl/config.py -- Comprehensive configuration system for ProxyWhirl

Provides hierarchical configuration with support for environment variables,
configuration files, and programmatic settings using pydantic-settings.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from proxywhirl.models import CacheType, RotationStrategy


class LoaderConfig(BaseModel):
    """Configuration for individual proxy loaders."""

    timeout: float = Field(20.0, ge=1.0, le=300.0, description="HTTP timeout in seconds")
    max_retries: int = Field(3, ge=0, le=10, description="Maximum retry attempts")
    retry_delay: float = Field(1.0, ge=0.1, le=10.0, description="Initial retry delay")
    max_retry_delay: float = Field(15.0, ge=1.0, le=60.0, description="Maximum retry delay")
    rate_limit: Optional[float] = Field(None, ge=0.1, description="Requests per second limit")
    enabled: bool = Field(True, description="Enable/disable this loader")

    model_config = {
        "json_schema_extra": {
            "examples": [{"timeout": 30.0, "max_retries": 5, "rate_limit": 2.0, "enabled": True}]
        }
    }


class ValidationConfig(BaseModel):
    """Configuration for proxy validation."""

    timeout: float = Field(10.0, ge=1.0, le=60.0, description="Validation timeout")
    test_url: str = Field("https://httpbin.org/ip", description="URL for testing proxies")
    concurrent_limit: int = Field(10, ge=1, le=100, description="Max concurrent validations")
    min_success_rate: float = Field(0.7, ge=0.0, le=1.0, description="Minimum success rate")
    max_response_time: float = Field(30.0, ge=0.1, description="Max acceptable response time")

    # Quality thresholds
    premium_success_rate: float = Field(0.95, ge=0.0, le=1.0)
    standard_success_rate: float = Field(0.8, ge=0.0, le=1.0)
    basic_success_rate: float = Field(0.6, ge=0.0, le=1.0)


class CircuitBreakerConfig(BaseModel):
    """Configuration for circuit breaker resilience."""

    enabled: bool = Field(True, description="Enable circuit breaker")
    failure_threshold: int = Field(5, ge=1, le=20, description="Failures before opening")
    recovery_timeout_seconds: int = Field(300, ge=30, le=3600, description="Recovery timeout")
    half_open_max_calls: int = Field(3, ge=1, le=10, description="Test calls in half-open state")


class ProxyWhirlSettings(BaseSettings):
    """Comprehensive ProxyWhirl configuration with env var support."""

    model_config = SettingsConfigDict(
        env_prefix="PROXYWHIRL_", env_file=".env", env_nested_delimiter="__", extra="ignore"
    )

    # Core settings
    cache_type: CacheType = CacheType.MEMORY
    cache_path: Optional[Path] = None
    rotation_strategy: RotationStrategy = RotationStrategy.ROUND_ROBIN

    # Health and monitoring
    health_check_interval: int = Field(
        30, ge=10, le=3600, description="Health check interval in seconds"
    )
    auto_validate: bool = Field(True, description="Auto-validate proxies on fetch")

    # Validation settings
    validation_timeout: float = Field(10.0, ge=1.0, le=60.0, description="Validation timeout")
    validation_test_url: str = Field(
        "https://httpbin.org/ip", description="URL for testing proxies"
    )
    validation_concurrent_limit: int = Field(
        10, ge=1, le=100, description="Max concurrent validations"
    )
    validation_min_success_rate: float = Field(
        0.7, ge=0.0, le=1.0, description="Minimum success rate"
    )
    validation_max_response_time: float = Field(
        30.0, ge=0.1, description="Max acceptable response time"
    )

    # Loader settings
    loader_timeout: float = Field(20.0, ge=1.0, le=300.0, description="Default loader timeout")
    loader_max_retries: int = Field(3, ge=0, le=10, description="Default max retries")
    loader_rate_limit: Optional[float] = Field(None, ge=0.1, description="Default rate limit")

    # Circuit breaker settings
    circuit_breaker_enabled: bool = Field(True, description="Enable circuit breaker")
    circuit_breaker_failure_threshold: int = Field(
        5, ge=1, le=20, description="Failures before opening"
    )
    circuit_breaker_recovery_timeout: int = Field(
        300, ge=30, le=3600, description="Recovery timeout seconds"
    )

    # Advanced features
    enable_metrics: bool = Field(True, description="Enable performance metrics collection")
    enable_proxy_auth: bool = Field(False, description="Enable authenticated proxy support")
    enable_rate_limiting: bool = Field(True, description="Enable request rate limiting")
    enable_geolocation: bool = Field(False, description="Enable geolocation enrichment")

    # Performance tuning
    max_concurrent_validations: int = Field(50, ge=1, le=200)
    cache_refresh_interval: int = Field(3600, ge=300, le=86400)  # seconds

    # Logging and debugging
    log_level: str = Field("INFO", description="Logging level")
    enable_debug_metrics: bool = Field(False, description="Enable detailed debug metrics")

    def get_loader_config(self, loader_name: str) -> LoaderConfig:
        """Get configuration for a specific loader, falling back to default."""
        # Create a default LoaderConfig since we flattened the structure
        default_config = LoaderConfig(
            timeout=self.loader_timeout,
            max_retries=self.loader_max_retries,
            rate_limit=self.loader_rate_limit,
        )
        return default_config

    def is_loader_enabled(self, loader_name: str) -> bool:
        """Check if a loader is enabled."""
        config = self.get_loader_config(loader_name)
        return config.enabled

    @classmethod
    def from_file(cls, config_path: Path) -> ProxyWhirlSettings:
        """Load settings from a configuration file."""
        if config_path.suffix.lower() == ".json":
            import json

            with open(config_path) as f:
                data = json.load(f)
        elif config_path.suffix.lower() in (".yaml", ".yml"):
            import yaml

            with open(config_path) as f:
                data = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported config file format: {config_path.suffix}")

        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return self.model_dump(mode="json")

    def merge(self, other: ProxyWhirlSettings) -> ProxyWhirlSettings:
        """Merge with another settings instance, with other taking precedence."""
        merged_data = self.to_dict()
        other_data = other.to_dict()

        # Deep merge dictionaries
        def deep_merge(base: Dict, override: Dict) -> Dict:
            result = base.copy()
            for key, value in override.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result

        merged_data = deep_merge(merged_data, other_data)
        return ProxyWhirlSettings(**merged_data)


# Convenience functions
def load_config(config_file: Optional[Path] = None, **overrides) -> ProxyWhirlSettings:
    """Load configuration from file and environment with optional overrides."""
    if config_file and config_file.exists():
        settings = ProxyWhirlSettings.from_file(config_file)
    else:
        settings = ProxyWhirlSettings()

    # Apply any programmatic overrides
    if overrides:
        override_settings = ProxyWhirlSettings(**overrides)
        settings = settings.merge(override_settings)

    return settings


def create_development_config() -> ProxyWhirlSettings:
    """Create a development-friendly configuration."""
    return ProxyWhirlSettings(
        cache_type=CacheType.MEMORY,
        validation=ValidationConfig(timeout=5.0, concurrent_limit=20),
        default_loader_config=LoaderConfig(timeout=10.0, max_retries=2, rate_limit=5.0),
        enable_debug_metrics=True,
        log_level="DEBUG",
    )


def create_production_config() -> ProxyWhirlSettings:
    """Create a production-ready configuration."""
    return ProxyWhirlSettings(
        cache_type=CacheType.SQLITE,
        validation=ValidationConfig(timeout=15.0, concurrent_limit=10, min_success_rate=0.8),
        default_loader_config=LoaderConfig(timeout=20.0, max_retries=3, rate_limit=2.0),
        circuit_breaker=CircuitBreakerConfig(
            enabled=True, failure_threshold=3, recovery_timeout_seconds=600
        ),
        enable_metrics=True,
        log_level="INFO",
    )
