"""proxywhirl/config.py -- Comprehensive configuration system for ProxyWhirl

Provides hierarchical configuration with support for environment variables,
configuration files, and programmatic settings using pydantic-settings.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from proxywhirl.caches.config import CacheType
from proxywhirl.models import RotationStrategy


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
        300, ge=60, le=3600, description="Health check interval in seconds"
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
        return LoaderConfig(
            timeout=self.loader_timeout,
            max_retries=self.loader_max_retries,
            rate_limit=self.loader_rate_limit,
            retry_delay=1.0,
            max_retry_delay=15.0,
            enabled=True,
        )

    def is_loader_enabled(self, loader_name: str) -> bool:
        """Check if a loader is enabled."""
        config = self.get_loader_config(loader_name)
        return config.enabled

    @classmethod
    def from_file(cls, config_path: Path) -> ProxyWhirlSettings:
        """Load settings from a configuration file with enhanced YAML support.

        Args:
            config_path: Path to the configuration file (.json, .yaml, or .yml)

        Returns:
            ProxyWhirlSettings instance with loaded configuration

        Raises:
            ValueError: For unsupported file formats or invalid configuration
            FileNotFoundError: If the configuration file doesn't exist
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            if config_path.suffix.lower() == ".json":
                data = cls._load_json_config(config_path)
            elif config_path.suffix.lower() in (".yaml", ".yml"):
                data = cls._load_yaml_config(config_path)
            else:
                raise ValueError(
                    f"Unsupported config file format: {config_path.suffix}. "
                    "Supported formats: .json, .yaml, .yml"
                )

            # Validate that we have valid configuration structure
            # Note: data is already validated as Dict[str, Any] by return type of _load_yaml_config

            return cls(**data)

        except Exception as e:
            if isinstance(e, (ValueError, FileNotFoundError)):
                raise
            raise ValueError(f"Failed to load configuration from {config_path}: {e}") from e

    @classmethod
    def _load_json_config(cls, config_path: Path) -> Dict[str, Any]:
        """Load JSON configuration with error handling."""
        import json

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON in {config_path} at line {e.lineno}, column {e.colno}: {e.msg}"
            ) from e

    @classmethod
    def _load_yaml_config(cls, config_path: Path) -> Dict[str, Any]:
        """Load YAML configuration with enhanced error handling and validation."""
        import yaml
        from yaml.constructor import ConstructorError
        from yaml.parser import ParserError
        from yaml.scanner import ScannerError

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                # Use safe_load to prevent arbitrary code execution
                data = yaml.safe_load(f)
                return data if data is not None else {}

        except (ParserError, ScannerError) as e:
            # YAML syntax errors
            line_info = ""
            if hasattr(e, "problem_mark") and e.problem_mark is not None:
                line_info = f" at line {e.problem_mark.line + 1}"
            raise ValueError(f"YAML syntax error in {config_path}{line_info}: {e.problem}") from e
        except ConstructorError as e:
            # YAML construction errors (e.g., duplicate keys, invalid references)
            line_info = ""
            if hasattr(e, "problem_mark") and e.problem_mark is not None:
                line_info = f" at line {e.problem_mark.line + 1}"
            raise ValueError(
                f"YAML structure error in {config_path}{line_info}: {e.problem}"
            ) from e
        except UnicodeDecodeError as e:
            raise ValueError(
                f"File encoding error in {config_path}: {e}. " "Ensure the file is UTF-8 encoded."
            ) from e

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return self.model_dump(mode="json")

    def merge(self, other: ProxyWhirlSettings) -> ProxyWhirlSettings:
        """Merge with another settings instance, with other taking precedence."""
        # Use model_copy with update to preserve base values while applying overrides
        other_data = other.model_dump(exclude_unset=True, exclude_none=True)
        return self.model_copy(update=other_data)


# Convenience functions
def load_config(config_file: Optional[Path] = None, **overrides: Any) -> ProxyWhirlSettings:
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
        validation_timeout=5.0,
        validation_concurrent_limit=20,
        loader_timeout=10.0,
        loader_max_retries=2,
        loader_rate_limit=5.0,
        enable_debug_metrics=True,
        log_level="DEBUG",
    )


def create_production_config() -> ProxyWhirlSettings:
    """Create a production-ready configuration."""
    return ProxyWhirlSettings(
        cache_type=CacheType.SQLITE,
        validation_timeout=15.0,
        validation_concurrent_limit=10,
        validation_min_success_rate=0.8,
        loader_timeout=20.0,
        loader_max_retries=3,
        loader_rate_limit=2.0,
        circuit_breaker_enabled=True,
        circuit_breaker_failure_threshold=3,
        circuit_breaker_recovery_timeout=600,
        enable_metrics=True,
        log_level="INFO",
    )
