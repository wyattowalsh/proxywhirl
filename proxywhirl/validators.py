"""
TypeGuard validators for ProxyWhirl models and common validation patterns.

TypeGuards provide type-safe validation utilities that can be used throughout
the codebase for runtime type checking and validation.
"""

from __future__ import annotations

import re
from typing import Any, TypeGuard
from urllib.parse import urlparse

from proxywhirl.models import HealthStatus, Proxy, ProxyPool, Session

# ============================================================================
# PROXY VALIDATION TYPEGUARDS
# ============================================================================


def is_valid_proxy(obj: Any) -> TypeGuard[Proxy]:
    """Check if object is a valid Proxy instance with required fields.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a valid Proxy with url and id
    """
    return (
        isinstance(obj, Proxy)
        and hasattr(obj, "url")
        and obj.url is not None
        and hasattr(obj, "id")
        and obj.id is not None
    )


def is_proxy(obj: Any) -> TypeGuard[Proxy]:
    """Check if object is a Proxy instance.

    Alias for is_valid_proxy for backward compatibility.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a valid Proxy instance
    """
    return is_valid_proxy(obj)


def is_healthy_proxy(obj: Any) -> TypeGuard[Proxy]:
    """Check if object is a Proxy with healthy status.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a Proxy with HEALTHY status
    """
    return (
        is_valid_proxy(obj)
        and hasattr(obj, "health_status")
        and obj.health_status == HealthStatus.HEALTHY
    )


def is_working_proxy(obj: Any) -> TypeGuard[Proxy]:
    """Check if object is a Proxy that is not dead.

    A working proxy is one with status other than DEAD.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a Proxy with non-DEAD status
    """
    return (
        is_valid_proxy(obj)
        and hasattr(obj, "health_status")
        and obj.health_status != HealthStatus.DEAD
    )


def is_pool(obj: Any) -> TypeGuard[ProxyPool]:
    """Check if object is a valid ProxyPool instance.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a ProxyPool with proxies collection
    """
    return isinstance(obj, ProxyPool) and hasattr(obj, "proxies") and isinstance(obj.proxies, dict)


def is_session(obj: Any) -> TypeGuard[Session]:
    """Check if object is a valid Session instance.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a Session with id and created_at
    """
    return (
        isinstance(obj, Session)
        and hasattr(obj, "id")
        and obj.id is not None
        and hasattr(obj, "created_at")
        and obj.created_at is not None
    )


# ============================================================================
# URL AND FORMAT VALIDATION TYPEGUARDS
# ============================================================================


def is_valid_proxy_url(url: str) -> TypeGuard[str]:
    """Check if string is a valid proxy URL format.

    Valid formats:
    - http://host:port
    - https://host:port
    - socks4://host:port
    - socks5://host:port
    - socks5h://host:port

    Args:
        url: String to validate

    Returns:
        True if url is a valid proxy URL
    """
    try:
        parsed = urlparse(url)
        valid_schemes = ("http", "https", "socks4", "socks5", "socks5h")

        if parsed.scheme not in valid_schemes:
            return False

        # Check for host and port
        if not parsed.hostname or parsed.port is None:
            return False

        # Validate port is in valid range
        return 1 <= parsed.port <= 65535
    except (ValueError, AttributeError):
        return False


def is_valid_host(host: str) -> TypeGuard[str]:
    """Check if string is a valid hostname or IP address.

    Args:
        host: String to validate

    Returns:
        True if host is valid hostname or IP
    """
    try:
        # Try IPv4
        parts = host.split(".")
        if len(parts) == 4 and all(0 <= int(p) <= 255 for p in parts):
            return True

        # Check for valid hostname pattern
        # Labels must be 1-63 chars, overall max 253 chars
        if len(host) > 253:
            return False

        labels = host.split(".")
        if len(labels) < 2:
            return False

        for label in labels:
            if not label or len(label) > 63:
                return False
            if not re.match(r"^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$", label):
                return False

        return True
    except (ValueError, AttributeError):
        return False


def is_valid_port(port: Any) -> TypeGuard[int]:
    """Check if value is a valid port number.

    Args:
        port: Value to validate

    Returns:
        True if port is 1-65535
    """
    return isinstance(port, int) and 1 <= port <= 65535


# ============================================================================
# STATUS VALIDATION TYPEGUARDS
# ============================================================================


def is_health_status(value: Any) -> TypeGuard[HealthStatus]:
    """Check if value is a valid HealthStatus enum value.

    Args:
        value: Value to validate

    Returns:
        True if value is a HealthStatus
    """
    return isinstance(value, HealthStatus)


def is_healthy_status(value: Any) -> TypeGuard[HealthStatus]:
    """Check if value is HEALTHY status.

    Args:
        value: Value to validate

    Returns:
        True if value is HealthStatus.HEALTHY
    """
    return value == HealthStatus.HEALTHY


def is_degraded_status(value: Any) -> TypeGuard[HealthStatus]:
    """Check if value is DEGRADED status.

    Args:
        value: Value to validate

    Returns:
        True if value is HealthStatus.DEGRADED
    """
    return value == HealthStatus.DEGRADED


def is_dead_status(value: Any) -> TypeGuard[HealthStatus]:
    """Check if value is DEAD status.

    Args:
        value: Value to validate

    Returns:
        True if value is HealthStatus.DEAD
    """
    return value == HealthStatus.DEAD


# ============================================================================
# COLLECTION VALIDATION TYPEGUARDS
# ============================================================================


def is_proxy_list(obj: Any) -> TypeGuard[list[Proxy]]:
    """Check if object is a list of valid Proxy instances.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a list of Proxies
    """
    return isinstance(obj, list) and all(is_valid_proxy(p) for p in obj)


def is_healthy_proxy_list(obj: Any) -> TypeGuard[list[Proxy]]:
    """Check if object is a list of healthy Proxy instances.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a list of healthy Proxies
    """
    return isinstance(obj, list) and all(is_healthy_proxy(p) for p in obj)


def is_proxy_dict(obj: Any) -> TypeGuard[dict[str, Proxy]]:
    """Check if object is a dict mapping to Proxy instances.

    Args:
        obj: Object to validate

    Returns:
        True if obj is dict[str, Proxy]
    """
    return isinstance(obj, dict) and all(
        isinstance(k, str) and is_valid_proxy(v) for k, v in obj.items()
    )


# ============================================================================
# NUMERIC VALIDATION TYPEGUARDS
# ============================================================================


def is_success_rate(value: Any) -> TypeGuard[float]:
    """Check if value is a valid success rate (0.0 to 1.0).

    Args:
        value: Value to validate

    Returns:
        True if value is float in [0.0, 1.0]
    """
    return isinstance(value, (int, float)) and 0.0 <= value <= 1.0


def is_non_negative(value: Any) -> TypeGuard[float]:
    """Check if value is a non-negative number.

    Args:
        value: Value to validate

    Returns:
        True if value is >= 0
    """
    return isinstance(value, (int, float)) and value >= 0


def is_positive(value: Any) -> TypeGuard[float]:
    """Check if value is a positive number.

    Args:
        value: Value to validate

    Returns:
        True if value is > 0
    """
    return isinstance(value, (int, float)) and value > 0
