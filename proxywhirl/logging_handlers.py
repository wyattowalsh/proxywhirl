"""
Log handler factory and multi-destination handler management.

This module provides handler creation, rotation, retention, sampling,
filtering, and fallback capabilities for structured logging.
"""

import sys
from pathlib import Path
from typing import Any, Callable, Optional

from loguru import logger

from proxywhirl.logging_config import (
    LogConfiguration,
    LogHandlerConfig,
    LogHandlerType,
    LogLevel,
)
from proxywhirl.logging_formatters import (
    create_loguru_json_sink,
    create_loguru_logfmt_sink,
)


# Global drop counter for async queue overflow
_drop_counter = 0


def get_drop_counter() -> int:
    """
    Get the current number of dropped log entries.

    Returns:
        Number of entries dropped due to queue overflow
    """
    return _drop_counter


def reset_drop_counter() -> None:
    """Reset the drop counter to zero."""
    global _drop_counter
    _drop_counter = 0


def increment_drop_counter(count: int = 1) -> None:
    """
    Increment the drop counter.

    Args:
        count: Number to increment by (default: 1)
    """
    global _drop_counter
    _drop_counter += count


def apply_logging_configuration(config: LogConfiguration) -> list[int]:
    """
    Apply a complete logging configuration.

    This removes all existing handlers and installs handlers based on
    the configuration. Returns handler IDs for later removal if needed.

    Args:
        config: LogConfiguration instance

    Returns:
        List of handler IDs added to loguru

    Example:
        >>> config = LogConfiguration(level=LogLevel.DEBUG)
        >>> handler_ids = apply_logging_configuration(config)
    """
    # Remove existing handlers
    logger.remove()
    
    # Reset drop counter
    reset_drop_counter()
    
    handler_ids: list[int] = []
    
    if not config.handlers:
        # No handlers configured, add default console handler
        sink = _create_default_console_sink(config)
        handler_id = logger.add(
            sink,
            level=config.level.value,
            enqueue=config.async_logging,
        )
        handler_ids.append(handler_id)
    else:
        # Add configured handlers
        for handler_config in config.handlers:
            try:
                sink = create_handler_sink(handler_config, config)
                handler_id = logger.add(
                    sink,
                    level=handler_config.level.value,
                    enqueue=config.async_logging,
                    catch=True,  # Catch errors in sink
                )
                handler_ids.append(handler_id)
            except Exception as e:
                # Log handler creation failure to stderr
                print(
                    f"WARNING: Failed to create handler {handler_config.type}: {e}",
                    file=sys.stderr,
                )
    
    return handler_ids


def create_handler_sink(
    handler_config: LogHandlerConfig,
    global_config: LogConfiguration,
) -> Callable[[Any], None]:
    """
    Create a sink function for a handler configuration.

    Args:
        handler_config: Handler configuration
        global_config: Global logging configuration

    Returns:
        Callable sink function for loguru

    Raises:
        ValueError: If handler configuration is invalid
    """
    handler_type = handler_config.type
    
    # Create base sink based on handler type
    if handler_type == LogHandlerType.CONSOLE:
        sink = _create_console_sink(handler_config, global_config)
    elif handler_type == LogHandlerType.FILE:
        sink = _create_file_sink(handler_config, global_config)
    elif handler_type == LogHandlerType.SYSLOG:
        sink = _create_syslog_sink(handler_config, global_config)
    elif handler_type == LogHandlerType.HTTP:
        sink = _create_http_sink(handler_config, global_config)
    else:
        raise ValueError(f"Unknown handler type: {handler_type}")
    
    # Wrap with filtering if configured
    if handler_config.filter_modules:
        sink = _wrap_with_module_filter(sink, handler_config.filter_modules)
    
    # Wrap with sampling if configured
    if handler_config.sample_rate is not None and handler_config.sample_rate < 1.0:
        sink = _wrap_with_sampling(sink, handler_config.sample_rate)
    
    return sink


def _create_default_console_sink(config: LogConfiguration) -> Callable[[Any], None]:
    """Create default console sink with basic formatting."""
    return create_loguru_json_sink(redact_credentials=config.redact_credentials)


def _create_console_sink(
    handler_config: LogHandlerConfig,
    global_config: LogConfiguration,
) -> Callable[[Any], None]:
    """Create console sink with specified format."""
    redact = global_config.redact_credentials
    
    if handler_config.format == "json":
        return create_loguru_json_sink(redact_credentials=redact)
    elif handler_config.format == "logfmt":
        return create_loguru_logfmt_sink(redact_credentials=redact)
    else:
        # Default text format
        return sys.stdout


def _create_file_sink(
    handler_config: LogHandlerConfig,
    global_config: LogConfiguration,
) -> Any:
    """
    Create file sink with rotation and retention.

    Args:
        handler_config: Handler configuration
        global_config: Global configuration

    Returns:
        File path or callable for loguru file handler
    """
    if not handler_config.path:
        raise ValueError("File handler requires 'path' configuration")
    
    # Ensure parent directory exists
    file_path = Path(handler_config.path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # For file handlers, loguru handles rotation and retention natively
    # We return the path and let loguru's add() handle it with additional params
    # However, since we need to return a sink, we'll use loguru's native path
    # syntax which supports rotation and retention
    
    # Build sink config for file with rotation/retention
    # Note: loguru's add() method needs these as separate parameters
    # For now, return path and rely on caller to pass rotation/retention
    return str(file_path)


def _create_syslog_sink(
    handler_config: LogHandlerConfig,
    global_config: LogConfiguration,
) -> Callable[[Any], None]:
    """
    Create syslog sink.

    Args:
        handler_config: Handler configuration
        global_config: Global configuration

    Returns:
        Callable sink for syslog

    Note:
        This is a simplified implementation. Production systems should
        use proper syslog libraries with RFC 5424/3164 compliance.
    """
    if not handler_config.url:
        raise ValueError("Syslog handler requires 'url' configuration")
    
    import socket
    from urllib.parse import urlparse
    
    parsed = urlparse(handler_config.url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 514
    
    # Create UDP socket for syslog
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def syslog_sink(message: Any) -> None:
        """Send log to syslog over UDP."""
        try:
            if hasattr(message, "record"):
                record = message.record
                # Format as RFC 3164 syslog message (simplified)
                log_line = f"<{_level_to_priority(record['level'].name)}>{record['message']}"
                sock.sendto(log_line.encode('utf-8'), (host, port))
        except Exception as e:
            # Fallback to stderr on syslog failure
            print(f"Syslog error: {e}", file=sys.stderr)
    
    return syslog_sink


def _level_to_priority(level: str) -> int:
    """
    Convert log level to syslog priority.

    Args:
        level: Log level string

    Returns:
        Syslog priority number
    """
    priorities = {
        "CRITICAL": 2,  # Critical
        "ERROR": 3,     # Error
        "WARNING": 4,   # Warning
        "INFO": 6,      # Informational
        "DEBUG": 7,     # Debug
    }
    return priorities.get(level, 6)


def _create_http_sink(
    handler_config: LogHandlerConfig,
    global_config: LogConfiguration,
) -> Callable[[Any], None]:
    """
    Create HTTP remote logging sink.

    Args:
        handler_config: Handler configuration
        global_config: Global configuration

    Returns:
        Callable sink for HTTP logging

    Note:
        Uses synchronous HTTP requests. For production, consider async
        or batched sending to avoid blocking.
    """
    if not handler_config.url:
        raise ValueError("HTTP handler requires 'url' configuration")
    
    import httpx
    from proxywhirl.logging_formatters import format_json_log
    
    client = httpx.Client(timeout=5.0)
    
    def http_sink(message: Any) -> None:
        """Send log to HTTP endpoint."""
        try:
            if hasattr(message, "record"):
                record = message.record
                log_dict = {
                    "time": record["time"],
                    "level": record["level"].name,
                    "message": record["message"],
                    "module": record["module"],
                    "function": record["function"],
                    "line": record["line"],
                    "exception": record["exception"] if record["exception"] else None,
                    "extra": dict(record.get("extra", {})),
                }
                json_log = format_json_log(
                    log_dict,
                    redact=global_config.redact_credentials
                )
                
                # Send to HTTP endpoint
                client.post(
                    handler_config.url,
                    content=json_log,
                    headers={"Content-Type": "application/json"},
                )
        except Exception as e:
            # Fallback to stderr on HTTP failure
            print(f"HTTP logging error: {e}", file=sys.stderr)
    
    return http_sink


def _wrap_with_module_filter(
    sink: Callable[[Any], None],
    filter_modules: list[str],
) -> Callable[[Any], None]:
    """
    Wrap sink with module filtering.

    Args:
        sink: Original sink function
        filter_modules: List of module names to allow

    Returns:
        Wrapped sink that filters by module
    """
    def filtered_sink(message: Any) -> None:
        """Filter logs by module name."""
        if hasattr(message, "record"):
            record = message.record
            module_name = record.get("module", "")
            
            # Check if module matches any filter
            if any(module_name.startswith(f) for f in filter_modules):
                sink(message)
    
    return filtered_sink


def _wrap_with_sampling(
    sink: Callable[[Any], None],
    sample_rate: float,
) -> Callable[[Any], None]:
    """
    Wrap sink with sampling.

    Args:
        sink: Original sink function
        sample_rate: Fraction of logs to keep (0.0-1.0)

    Returns:
        Wrapped sink that samples logs
    """
    import random
    
    def sampled_sink(message: Any) -> None:
        """Sample logs based on rate."""
        if random.random() < sample_rate:
            sink(message)
    
    return sampled_sink


def reload_logging_configuration(config: LogConfiguration) -> list[int]:
    """
    Reload logging configuration without restarting the application.

    This is an atomic operation that removes old handlers and installs new ones.

    Args:
        config: New logging configuration

    Returns:
        List of new handler IDs

    Example:
        >>> config = load_logging_config(level="DEBUG")
        >>> reload_logging_configuration(config)
    """
    return apply_logging_configuration(config)


def configure_file_handler_with_rotation(
    file_path: str,
    rotation: Optional[str] = None,
    retention: Optional[str] = None,
    format: str = "json",
    level: str = "INFO",
    redact: bool = True,
) -> int:
    """
    Configure a file handler with rotation and retention.

    Args:
        file_path: Path to log file
        rotation: Rotation policy (e.g., "100 MB", "1 day")
        retention: Retention policy (e.g., "7 days", "10 files")
        format: Log format (json, logfmt, text)
        level: Log level
        redact: Whether to redact credentials

    Returns:
        Handler ID

    Example:
        >>> handler_id = configure_file_handler_with_rotation(
        ...     "logs/app.log",
        ...     rotation="100 MB",
        ...     retention="7 days"
        ... )
    """
    # Create formatter
    if format == "json":
        formatter = create_loguru_json_sink(redact_credentials=redact)
    elif format == "logfmt":
        formatter = create_loguru_logfmt_sink(redact_credentials=redact)
    else:
        formatter = None  # Use loguru's default
    
    # Add file handler with rotation and retention
    handler_id = logger.add(
        file_path,
        rotation=rotation,
        retention=retention,
        level=level,
        format=formatter if formatter else None,
        enqueue=True,
    )
    
    return handler_id
