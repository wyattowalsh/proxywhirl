"""Reusable type checking and validation functions."""

from __future__ import annotations

from typing import Any

from proxywhirl.exceptions import ProxyValidationError


def is_valid_proxy_type(obj: Any) -> bool:
    """
    Check if an object is a valid Proxy type.

    Args:
        obj: Object to check

    Returns:
        True if object is a Proxy instance, False otherwise
    """
    try:
        from proxywhirl.models import Proxy

        return isinstance(obj, Proxy)
    except ImportError:
        return False


def is_valid_proxy_url(url: str) -> bool:
    """
    Validate proxy URL format.

    Args:
        url: URL string to validate

    Returns:
        True if URL is a valid proxy URL, False otherwise
    """
    if not isinstance(url, str) or not url:
        return False

    try:
        from urllib.parse import urlparse

        parsed = urlparse(url)
        if not parsed.scheme or not parsed.hostname or not parsed.port:
            return False

        valid_schemes = {"http", "https", "socks4", "socks5", "socks5h"}
        return parsed.scheme in valid_schemes
    except Exception:
        return False


def is_valid_strategy(strategy: Any) -> bool:
    """
    Check if an object implements the RotationStrategy protocol.

    Args:
        strategy: Object to check

    Returns:
        True if object is a valid strategy, False otherwise
    """
    try:
        # Check for required methods
        required_methods = {"select", "reset", "get_stats"}
        return all(hasattr(strategy, method) and callable(getattr(strategy, method))
                   for method in required_methods)
    except Exception:
        return False


def is_valid_config_dict(config: Any) -> bool:
    """
    Validate that a config object is a valid dictionary.

    Args:
        config: Object to validate

    Returns:
        True if valid config dictionary, False otherwise
    """
    if not isinstance(config, dict):
        return False

    try:
        # Check for common config keys and types
        if "timeout" in config and not isinstance(config["timeout"], (int, float)):
            return False
        if "max_retries" in config and not isinstance(config["max_retries"], int):
            return False
        return "pool_size" not in config or isinstance(config["pool_size"], int)
    except Exception:
        return False


def validate_proxy_list(proxies: Any) -> bool:
    """
    Validate that proxies is a valid list of Proxy objects.

    Args:
        proxies: Object to validate

    Returns:
        True if valid proxy list, False otherwise
    """
    if not isinstance(proxies, list):
        return False

    try:
        from proxywhirl.models import Proxy

        return all(isinstance(p, Proxy) for p in proxies)
    except Exception:
        return False


def validate_config_dict(
    config: dict[str, Any],
    *,
    required_keys: set[str] | None = None,
    allowed_keys: set[str] | None = None,
    type_hints: dict[str, type] | None = None,
) -> tuple[bool, list[str]]:
    """
    Validate a configuration dictionary with constraints.

    Args:
        config: Configuration dictionary to validate
        required_keys: Set of keys that must be present
        allowed_keys: Set of keys that are allowed (if provided)
        type_hints: Dictionary mapping keys to expected types

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors: list[str] = []

    if not isinstance(config, dict):
        errors.append("Config must be a dictionary")
        return False, errors

    # Check required keys
    if required_keys:
        missing = required_keys - set(config.keys())
        if missing:
            errors.append(f"Missing required keys: {missing}")

    # Check allowed keys
    if allowed_keys:
        extra = set(config.keys()) - allowed_keys
        if extra:
            errors.append(f"Extra keys not allowed: {extra}")

    # Check types
    if type_hints:
        for key, expected_type in type_hints.items():
            if key in config:
                value = config[key]
                if not isinstance(value, expected_type):
                    errors.append(
                        f"Key '{key}' has type {type(value).__name__}, "
                        f"expected {expected_type.__name__}"
                    )

    return len(errors) == 0, errors


def is_valid_anonymity_level(level: Any) -> bool:
    """
    Check if a value is a valid anonymity level.

    Args:
        level: Value to check

    Returns:
        True if valid anonymity level, False otherwise
    """
    valid_levels = {"transparent", "anonymous", "elite"}
    return isinstance(level, str) and level in valid_levels


def is_valid_protocol(protocol: Any) -> bool:
    """
    Check if a value is a valid proxy protocol.

    Args:
        protocol: Value to check

    Returns:
        True if valid protocol, False otherwise
    """
    valid_protocols = {"http", "https", "socks4", "socks5", "socks5h"}
    return isinstance(protocol, str) and protocol in valid_protocols


def is_valid_health_status(status: Any) -> bool:
    """
    Check if a value is a valid health status.

    Args:
        status: Value to check

    Returns:
        True if valid health status, False otherwise
    """
    valid_statuses = {"healthy", "unhealthy", "unknown", "pending"}
    return isinstance(status, str) and status in valid_statuses


def assert_valid_proxy_type(obj: Any, msg: str = "Invalid proxy type") -> None:
    """
    Assert that an object is a valid Proxy type.

    Args:
        obj: Object to validate
        msg: Custom error message

    Raises:
        ProxyValidationError: If validation fails
    """
    if not is_valid_proxy_type(obj):
        raise ProxyValidationError(msg)


def assert_valid_proxy_url(url: str, msg: str = "Invalid proxy URL") -> None:
    """
    Assert that a URL is a valid proxy URL.

    Args:
        url: URL to validate
        msg: Custom error message

    Raises:
        ProxyValidationError: If validation fails
    """
    if not is_valid_proxy_url(url):
        raise ProxyValidationError(msg)


def assert_valid_protocol(protocol: str, msg: str = "Invalid protocol") -> None:
    """
    Assert that a protocol is valid.

    Args:
        protocol: Protocol to validate
        msg: Custom error message

    Raises:
        ProxyValidationError: If validation fails
    """
    if not is_valid_protocol(protocol):
        raise ProxyValidationError(msg)
