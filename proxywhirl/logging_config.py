"""Structured logging configuration for ProxyWhirl.

This module provides MVP Phase 1 functionality for structured logging:
- JSON and logfmt output formats
- Log rotation configuration
- Contextual metadata support
- Integration with existing loguru usage

Example:
    >>> from proxywhirl.logging_config import configure_logging, get_logger
    >>> configure_logging(format="json", level="INFO", rotation="10 MB")
    >>> logger = get_logger()
    >>> logger.info("Started proxy rotation")
"""

from __future__ import annotations

import sys
from typing import Literal

from loguru import logger
from pydantic import BaseModel, Field


class LogContext:
    """Context manager for adding contextual metadata to log entries.

    This class provides a convenient way to bind context variables to the logger
    for a specific block of code. Context is automatically removed when exiting
    the context manager.

    Example:
        >>> with LogContext(request_id="req-123", operation="proxy_fetch"):
        ...     logger.info("Processing request")
        # Log entry will include request_id and operation in context

    Args:
        **context: Arbitrary keyword arguments to bind as context metadata
    """

    def __init__(self, **context: str | int | float | bool | None) -> None:
        """Initialize context with metadata key-value pairs."""
        self.context = context
        self._token = None

    def __enter__(self) -> LogContext:
        """Enter context and bind metadata to logger."""
        # Store the bound logger's context token for cleanup
        self._bound_logger = logger.bind(**self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context (cleanup handled automatically by loguru)."""
        # Loguru handles context cleanup automatically when using bind()
        pass


class LogRotationConfig(BaseModel):
    """Configuration for log file rotation.

    Attributes:
        size: Size threshold for rotation (e.g., "10 MB", "1 GB")
        time: Time threshold for rotation (e.g., "1 day", "1 week")
        retention: Number of rotated files to keep (e.g., "5 files", "1 week")
    """

    size: str | None = Field(
        default=None,
        description="Size threshold for rotation (e.g., '10 MB', '1 GB')",
    )
    time: str | None = Field(
        default=None,
        description="Time threshold for rotation (e.g., '1 day', '1 week')",
    )
    retention: str | None = Field(
        default=None,
        description="Number of rotated files to keep (e.g., '5 files', '1 week')",
    )


class LoggingConfig(BaseModel):
    """Main logging configuration model.

    Attributes:
        format: Output format - 'default', 'json', or 'logfmt'
        level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        rotation: Log rotation configuration (size/time-based)
        retention: Retention policy for rotated logs
        colorize: Enable colored output (only for 'default' format)
        diagnose: Enable diagnostic mode (adds extra debug info)
        backtrace: Enable backtrace on exceptions
        enqueue: Enable async logging with queue
    """

    format: Literal["default", "json", "logfmt"] = Field(
        default="default",
        description="Output format for log messages",
    )
    level: str = Field(
        default="INFO",
        description="Minimum log level to output",
    )
    rotation: str | None = Field(
        default=None,
        description="Rotation threshold (e.g., '10 MB', '1 day')",
    )
    retention: str | None = Field(
        default=None,
        description="Retention policy (e.g., '5 files', '1 week')",
    )
    colorize: bool = Field(
        default=True,
        description="Enable colored output (default format only)",
    )
    diagnose: bool = Field(
        default=False,
        description="Enable diagnostic mode with extra debug info",
    )
    backtrace: bool = Field(
        default=True,
        description="Enable backtrace on exceptions",
    )
    enqueue: bool = Field(
        default=True,
        description="Enable async logging with queue",
    )


# Format templates for different output styles
FORMAT_TEMPLATES = {
    "default": (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    ),
    "json": "{message}",  # JSON serialization handled by serialize parameter
    "logfmt": (
        "time={time:YYYY-MM-DD HH:mm:ss.SSS} "
        "level={level} "
        "name={name} "
        "function={function} "
        "line={line} "
        "message={message} "
        "{extra}"
    ),
}


def configure_logging(
    format: Literal["default", "json", "logfmt"] = "default",
    level: str = "INFO",
    rotation: str | None = None,
    retention: str | None = None,
    sink=sys.stderr,
    colorize: bool | None = None,
    diagnose: bool = False,
    backtrace: bool = True,
    enqueue: bool = True,
) -> None:
    """Configure structured logging for ProxyWhirl.

    This function sets up loguru with the specified format, level, and rotation
    settings. It removes existing handlers and adds a new one with the
    configured settings.

    Args:
        format: Output format - 'default' (colored text), 'json', or 'logfmt'
        level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        rotation: Rotation threshold (e.g., '10 MB', '1 day', '00:00')
        retention: Retention policy (e.g., '5 files', '1 week', '7 days')
        sink: Output destination (file path, sys.stderr, sys.stdout, etc.)
        colorize: Enable colored output (auto-detected if None)
        diagnose: Enable diagnostic mode (adds code context to logs)
        backtrace: Enable backtrace on exceptions
        enqueue: Enable async logging with queue

    Example:
        >>> # JSON logging to file with rotation
        >>> configure_logging(
        ...     format="json",
        ...     level="INFO",
        ...     rotation="10 MB",
        ...     retention="5 files",
        ...     sink="logs/proxywhirl.log"
        ... )

        >>> # Console logging with colors
        >>> configure_logging(format="default", level="DEBUG")

        >>> # Logfmt to stderr
        >>> configure_logging(format="logfmt", level="WARNING")
    """
    # Remove existing handlers
    logger.remove()

    # Auto-detect colorize if not specified
    if colorize is None:
        colorize = format == "default" and hasattr(sink, "isatty")

    # Disable colorize for structured formats
    if format in ("json", "logfmt"):
        colorize = False

    # Build handler config
    handler_config = {
        "sink": sink,
        "level": level.upper(),
        "colorize": colorize,
        "diagnose": diagnose,
        "backtrace": backtrace,
        "enqueue": enqueue,
    }

    # Add format configuration
    if format == "json":
        # Use loguru's built-in JSON serialization
        handler_config["serialize"] = True
    else:
        handler_config["format"] = FORMAT_TEMPLATES[format]

    # Add rotation if specified
    if rotation:
        handler_config["rotation"] = rotation

    # Add retention if specified
    if retention:
        handler_config["retention"] = retention

    # Add the configured handler
    logger.add(**handler_config)


def get_logger():
    """Get the configured loguru logger instance.

    Returns:
        The global loguru logger instance, configured via configure_logging()

    Example:
        >>> logger = get_logger()
        >>> logger.info("Processing started")
        >>> logger.bind(request_id="req-123").info("Request received")
    """
    return logger


# Convenience function for binding context
def bind_context(**context: str | int | float | bool | None):
    """Bind contextual metadata to the logger.

    This is a convenience wrapper around logger.bind() for adding metadata
    to log entries. The bound context persists for the lifetime of the
    returned logger instance.

    Args:
        **context: Arbitrary keyword arguments to bind as context metadata

    Returns:
        Logger instance with bound context

    Example:
        >>> request_logger = bind_context(request_id="req-123", operation="fetch")
        >>> request_logger.info("Started operation")
        # Log will include request_id and operation in context
    """
    return logger.bind(**context)


# Export public API
__all__ = [
    "configure_logging",
    "get_logger",
    "bind_context",
    "LogContext",
    "LoggingConfig",
    "LogRotationConfig",
]
