"""
Structured log formatters for JSON and logfmt output formats.

This module provides formatters that serialize log records into structured
formats (JSON, logfmt) with Unicode safety and credential redaction.
"""

import json
import traceback
from datetime import datetime
from typing import Any, Optional
from urllib.parse import urlparse


def redact_sensitive_data(data: Any, max_depth: int = 10, _current_depth: int = 0) -> Any:
    """
    Recursively redact sensitive data from log entries.

    Args:
        data: Data structure to redact (dict, list, str, or primitive)
        max_depth: Maximum recursion depth to prevent infinite loops
        _current_depth: Current recursion depth (internal use)

    Returns:
        Redacted copy of the data structure
    """
    # Prevent infinite recursion
    if _current_depth >= max_depth:
        return str(data)

    # Sensitive field patterns (case-insensitive)
    sensitive_patterns = [
        "password",
        "passwd",
        "pwd",
        "secret",
        "token",
        "api_key",
        "apikey",
        "credential",
        "auth",
        "private_key",
        "access_key",
    ]

    if isinstance(data, dict):
        redacted = {}
        for key, value in data.items():
            # Check if key contains sensitive pattern (case-insensitive)
            # Only redact if value is a primitive (not dict/list)
            key_lower = key.lower()
            is_sensitive = any(pattern in key_lower for pattern in sensitive_patterns)
            
            if is_sensitive and not isinstance(value, (dict, list)):
                # Redact primitive sensitive values
                redacted[key] = "**REDACTED**"
            else:
                # Recursively process nested structures and non-sensitive values
                redacted[key] = redact_sensitive_data(
                    value, max_depth, _current_depth + 1
                )
        return redacted

    elif isinstance(data, (list, tuple)):
        return [
            redact_sensitive_data(item, max_depth, _current_depth + 1)
            for item in data
        ]

    elif isinstance(data, str):
        # Redact URLs with credentials
        return _redact_url_credentials(data)

    # Return primitives as-is
    return data


def _redact_url_credentials(url: str) -> str:
    """
    Redact credentials from URLs.

    Args:
        url: URL string that may contain credentials

    Returns:
        URL with credentials redacted if present
    """
    try:
        parsed = urlparse(url)
        if parsed.username or parsed.password:
            # Replace credentials with ****
            netloc_without_creds = parsed.hostname or ""
            if parsed.port:
                netloc_without_creds = f"{netloc_without_creds}:{parsed.port}"
            netloc_with_redacted = f"****:****@{netloc_without_creds}"
            return parsed._replace(netloc=netloc_with_redacted).geturl()
    except Exception:
        # If parsing fails, return original (safer than exposing partial data)
        pass
    return url


def serialize_exception(exc: BaseException) -> dict[str, Any]:
    """
    Serialize an exception to a structured dict.

    Args:
        exc: Exception instance to serialize

    Returns:
        Dictionary with exception type, message, and traceback
    """
    return {
        "type": type(exc).__name__,
        "message": str(exc),
        "traceback": [
            line.strip()
            for line in traceback.format_exception(type(exc), exc, exc.__traceback__)
        ],
    }


def format_json_log(record: dict[str, Any], redact: bool = True) -> str:
    """
    Format a log record as JSON.

    Args:
        record: Log record dictionary with fields:
            - time: datetime object
            - level: log level string
            - message: log message
            - module: module name
            - function: function name
            - line: line number
            - exception: optional exception object
            - extra: dict of extra fields
        redact: Whether to redact sensitive data

    Returns:
        JSON-formatted log entry string
    """
    # Build structured log entry
    log_entry: dict[str, Any] = {
        "timestamp": record["time"].isoformat() if isinstance(record["time"], datetime) else record["time"],
        "level": record["level"],
        "message": record["message"],
        "module": record["module"],
        "function": record["function"],
        "line": record["line"],
    }

    # Add exception if present
    if record.get("exception"):
        log_entry["exception"] = serialize_exception(record["exception"])

    # Merge extra fields into top level
    if record.get("extra"):
        for key, value in record["extra"].items():
            # Avoid overwriting standard fields
            if key not in log_entry:
                log_entry[key] = value

    # Apply redaction if enabled
    if redact:
        log_entry = redact_sensitive_data(log_entry)

    # Serialize to JSON with Unicode support
    return json.dumps(log_entry, ensure_ascii=False)


def format_logfmt_log(record: dict[str, Any], redact: bool = True) -> str:
    """
    Format a log record as logfmt (key=value pairs).

    Args:
        record: Log record dictionary (same structure as format_json_log)
        redact: Whether to redact sensitive data

    Returns:
        logfmt-formatted log entry string
    """
    # Build structured log entry (same as JSON)
    log_entry: dict[str, Any] = {
        "timestamp": record["time"].isoformat() if isinstance(record["time"], datetime) else record["time"],
        "level": record["level"],
        "message": record["message"],
        "module": record["module"],
        "function": record["function"],
        "line": record["line"],
    }

    # Add exception if present
    if record.get("exception"):
        exc_data = serialize_exception(record["exception"])
        log_entry["exception_type"] = exc_data["type"]
        log_entry["exception_message"] = exc_data["message"]

    # Merge extra fields
    if record.get("extra"):
        for key, value in record["extra"].items():
            if key not in log_entry:
                log_entry[key] = value

    # Apply redaction if enabled
    if redact:
        log_entry = redact_sensitive_data(log_entry)

    # Format as logfmt
    return _format_logfmt_dict(log_entry)


def _format_logfmt_dict(data: dict[str, Any]) -> str:
    """
    Format a dictionary as logfmt string.

    Args:
        data: Dictionary to format

    Returns:
        logfmt-formatted string
    """
    pairs = []
    for key, value in data.items():
        # Skip None values
        if value is None:
            continue

        # Convert value to string
        if isinstance(value, str):
            # Quote values with spaces or special characters
            if " " in value or '"' in value or "=" in value:
                # Escape quotes
                escaped_value = value.replace('"', r'\"')
                pairs.append(f'{key}="{escaped_value}"')
            else:
                pairs.append(f"{key}={value}")
        elif isinstance(value, bool):
            pairs.append(f"{key}={str(value).lower()}")
        elif isinstance(value, (int, float)):
            pairs.append(f"{key}={value}")
        elif isinstance(value, (dict, list)):
            # Serialize complex types as JSON strings
            json_str = json.dumps(value, ensure_ascii=False)
            escaped_json = json_str.replace('"', r'\"')
            pairs.append(f'{key}="{escaped_json}"')
        else:
            # Default string conversion
            str_value = str(value)
            if " " in str_value:
                pairs.append(f'{key}="{str_value}"')
            else:
                pairs.append(f"{key}={str_value}")

    return " ".join(pairs)


def create_loguru_json_sink(redact_credentials: bool = True) -> Any:
    """
    Create a loguru sink that outputs JSON-formatted logs.

    Args:
        redact_credentials: Whether to redact sensitive data

    Returns:
        Callable sink function for loguru
    """

    def json_sink(message: Any) -> None:
        """Sink function that formats and prints JSON logs."""
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
            formatted = format_json_log(log_dict, redact=redact_credentials)
            print(formatted)

    return json_sink


def create_loguru_logfmt_sink(redact_credentials: bool = True) -> Any:
    """
    Create a loguru sink that outputs logfmt-formatted logs.

    Args:
        redact_credentials: Whether to redact sensitive data

    Returns:
        Callable sink function for loguru
    """

    def logfmt_sink(message: Any) -> None:
        """Sink function that formats and prints logfmt logs."""
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
            formatted = format_logfmt_log(log_dict, redact=redact_credentials)
            print(formatted)

    return logfmt_sink
