"""
Logging configuration models for ProxyWhirl structured logging system.

This module provides Pydantic models for configuring structured logging with
support for multiple output destinations, formats, rotation, and sampling.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevel(str, Enum):
    """Standard log levels."""

    DEBUG    = "DEBUG"
    INFO     = "INFO"
    WARNING  = "WARNING"
    ERROR    = "ERROR"
    CRITICAL = "CRITICAL"


class LogHandlerType(str, Enum):
    """Supported log handler types."""

    CONSOLE = "console"
    FILE    = "file"
    SYSLOG  = "syslog"
    HTTP    = "http"


class LogHandlerConfig(BaseModel):
    """Configuration for a single log handler (sink).

    Attributes:
        type: Handler type (console, file, syslog, http)
        level: Log level for this handler (default: INFO)
        format: Output format (default, json, logfmt)
        path: File path (required for file handlers)
        rotation: Rotation policy (e.g., "100 MB", "1 day")
        retention: Retention policy (e.g., "7 days", "10 files")
        url: URL for remote handlers (syslog, http)
        filter_modules: Only log from these modules (empty = all)
        sample_rate: Sampling rate (0.0-1.0, 1.0 = no sampling)
    """

    type: LogHandlerType
    level: LogLevel               = LogLevel.INFO
    format: str                   = "default"
    path: Optional[str]           = None
    rotation: Optional[str]       = None
    retention: Optional[str]      = None
    url: Optional[str]            = None
    filter_modules: list[str]     = Field(default_factory=list)
    sample_rate: Optional[float]  = None

    @field_validator("sample_rate")
    @classmethod
    def validate_sample_rate(cls, v: Optional[float]) -> Optional[float]:
        """Validate sample rate is between 0 and 1."""
        if v is not None and (v < 0.0 or v > 1.0):
            raise ValueError("sample_rate must be between 0.0 and 1.0")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "type": "console",
                    "level": "INFO",
                    "format": "json"
                },
                {
                    "type": "file",
                    "path": "logs/app.log",
                    "rotation": "100 MB",
                    "retention": "7 days"
                },
                {
                    "type": "http",
                    "url": "https://logs.example.com/ingest",
                    "format": "json"
                }
            ]
        }
    }


class LogConfiguration(BaseSettings):
    """Main logging configuration model.

    Can be loaded from environment variables with PROXYWHIRL_LOG_ prefix
    or from a configuration file.

    Attributes:
        level: Global log level (default: INFO)
        async_logging: Enable async logging with background thread
        queue_size: Size of async logging queue
        drop_on_full: Drop logs when queue is full (vs blocking)
        redact_credentials: Redact sensitive data from logs
        handlers: List of log handlers to configure
    """

    level: LogLevel          = LogLevel.INFO
    async_logging: bool      = True
    queue_size: int          = 1000
    drop_on_full: bool       = True
    redact_credentials: bool = True
    handlers: list[LogHandlerConfig] = Field(default_factory=list)

    model_config = SettingsConfigDict(
        env_prefix="PROXYWHIRL_LOG_",
        env_nested_delimiter="__",
        case_sensitive=False,
    )

    @field_validator("queue_size")
    @classmethod
    def validate_queue_size(cls, v: int) -> int:
        """Validate queue size is positive."""
        if v <= 0:
            raise ValueError("queue_size must be positive")
        return v

    def get_handler_by_type(self, handler_type: LogHandlerType) -> list[LogHandlerConfig]:
        """Get all handlers of a specific type.

        Args:
            handler_type: Type of handler to retrieve

        Returns:
            List of matching handlers (may be empty)
        """
        return [h for h in self.handlers if h.type == handler_type]

    def has_handler_type(self, handler_type: LogHandlerType) -> bool:
        """Check if configuration has handler of specific type.

        Args:
            handler_type: Type of handler to check

        Returns:
            True if at least one handler of this type exists
        """
        return any(h.type == handler_type for h in self.handlers)


def load_logging_config(
    config_file: Optional[str] = None,
    **overrides: object,
) -> LogConfiguration:
    """Load logging configuration from environment and optional config file.

    Configuration precedence (highest to lowest):
    1. Explicit keyword overrides
    2. Environment variables (PROXYWHIRL_LOG_*)
    3. Configuration file (if provided)
    4. Defaults from LogConfiguration model

    Args:
        config_file: Optional path to config file (JSON/TOML)
        **overrides: Explicit configuration overrides

    Returns:
        Loaded and validated configuration

    Example:
        >>> config = load_logging_config(level="DEBUG")
        >>> config = load_logging_config(config_file="logging.json")
    """
    # Start with defaults and environment
    config = LogConfiguration(**overrides)

    # TODO: Add config file loading in future enhancement
    # if config_file:
    #     with open(config_file) as f:
    #         file_data = json.load(f)
    #         config = LogConfiguration(**{**file_data, **overrides})

    return config


def create_default_console_handler(
    level: LogLevel = LogLevel.INFO,
    format: str = "default",
) -> LogHandlerConfig:
    """Create a default console handler configuration.

    Args:
        level: Log level for console output
        format: Output format (default, json, logfmt)

    Returns:
        Console handler configuration
    """
    return LogHandlerConfig(
        type=LogHandlerType.CONSOLE,
        level=level,
        format=format,
    )


def create_file_handler(
    path: str,
    level: LogLevel = LogLevel.INFO,
    format: str = "default",
    rotation: Optional[str] = None,
    retention: Optional[str] = None,
) -> LogHandlerConfig:
    """Create a file handler configuration.

    Args:
        path: Path to log file
        level: Log level for file output
        format: Output format (default, json, logfmt)
        rotation: Rotation policy (e.g., "100 MB", "1 day")
        retention: Retention policy (e.g., "7 days", "10 files")

    Returns:
        File handler configuration
    """
    return LogHandlerConfig(
        type=LogHandlerType.FILE,
        path=path,
        level=level,
        format=format,
        rotation=rotation,
        retention=retention,
    )


def create_http_handler(
    url: str,
    level: LogLevel = LogLevel.INFO,
    format: str = "json",
) -> LogHandlerConfig:
    """Create an HTTP remote logging handler configuration.

    Args:
        url: HTTP endpoint URL for log ingestion
        level: Log level for remote output
        format: Output format (typically json)

    Returns:
        HTTP handler configuration
    """
    return LogHandlerConfig(
        type=LogHandlerType.HTTP,
        url=url,
        level=level,
        format=format,
    )


def create_syslog_handler(
    url: str,
    level: LogLevel = LogLevel.INFO,
) -> LogHandlerConfig:
    """Create a syslog handler configuration.

    Args:
        url: Syslog server URL (e.g., "syslog://localhost:514")
        level: Log level for syslog output

    Returns:
        Syslog handler configuration
    """
    return LogHandlerConfig(
        type=LogHandlerType.SYSLOG,
        url=url,
        level=level,
    )
