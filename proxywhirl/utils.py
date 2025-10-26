"""
Utility functions for logging, validation, and encryption.
"""

import json
import re
from typing import Any, Optional
from urllib.parse import urlparse

from loguru import logger

from proxywhirl.models import Proxy, ProxySource

# ============================================================================
# LOGGING UTILITIES
# ============================================================================


def configure_logging(
    level: str = "INFO",
    format_type: str = "json",
    redact_credentials: bool = True,
) -> None:
    """
    Configure loguru logging with optional JSON formatting and credential redaction.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: "json" or "text"
        redact_credentials: Whether to redact sensitive data
    """
    # Remove default handler
    logger.remove()

    if format_type == "json":

        def json_sink(message: Any) -> None:
            record = message.record
            log_entry: dict[str, Any] = {
                "timestamp": record["time"].isoformat(),
                "level": record["level"].name,
                "message": record["message"],
                "module": record["module"],
                "function": record["function"],
                "line": record["line"],
            }
            if record["exception"]:
                log_entry["exception"] = {
                    "type": str(record["exception"].type),
                    "value": str(record["exception"].value),
                }
            if record["extra"]:
                log_entry["extra"] = record["extra"]

            # Redact credentials if enabled
            if redact_credentials:
                log_entry = _redact_sensitive_data(log_entry)

            print(json.dumps(log_entry))

        logger.add(json_sink, level=level)
    else:
        # Text format
        logger.add(
            lambda msg: print(msg, end=""),
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=level,
        )


def _redact_sensitive_data(data: Any) -> Any:
    """Recursively redact sensitive data from log entries."""
    if isinstance(data, dict):
        redacted = {}
        for key, value in data.items():
            if any(
                sensitive in key.lower()
                for sensitive in ["password", "secret", "token", "api_key", "credential"]
            ):
                redacted[key] = "**REDACTED**"
            else:
                redacted[key] = _redact_sensitive_data(value)
        return redacted
    elif isinstance(data, (list, tuple)):
        return [_redact_sensitive_data(item) for item in data]
    elif isinstance(data, str):
        # Redact URLs with credentials
        return _redact_url_credentials(data)
    return data


def _redact_url_credentials(url: str) -> str:
    """Redact credentials from URLs."""
    try:
        parsed = urlparse(url)
        if parsed.username or parsed.password:
            # Replace credentials with ****
            netloc_without_creds = parsed.hostname
            if parsed.port:
                netloc_without_creds = f"{netloc_without_creds}:{parsed.port}"
            netloc_with_redacted = f"****:****@{netloc_without_creds}"
            return parsed._replace(netloc=netloc_with_redacted).geturl()
    except Exception:
        pass
    return url


# ============================================================================
# VALIDATION UTILITIES
# ============================================================================


PROXY_URL_PATTERN = re.compile(r"^(https?|socks4|socks5)://(?:([^:@]+):([^@]+)@)?([^:]+):(\d+)/?$")


def is_valid_proxy_url(url: str) -> bool:
    """
    Validate proxy URL format.

    Args:
        url: URL to validate

    Returns:
        True if valid proxy URL
    """
    return PROXY_URL_PATTERN.match(url) is not None


def parse_proxy_url(url: str) -> dict[str, Any]:
    """
    Parse proxy URL into components.

    Args:
        url: Proxy URL to parse

    Returns:
        Dictionary with protocol, host, port, username, password

    Raises:
        ValueError: If URL is invalid
    """
    match = PROXY_URL_PATTERN.match(url)
    if not match:
        raise ValueError(f"Invalid proxy URL format: {url}")

    protocol, username, password, host, port = match.groups()

    return {
        "protocol": protocol,
        "host": host,
        "port": int(port),
        "username": username,
        "password": password,
    }


def validate_proxy_model(proxy: Proxy) -> list[str]:
    """
    Validate a Proxy model instance.

    Args:
        proxy: Proxy to validate

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Check URL format
    if not is_valid_proxy_url(str(proxy.url)):
        errors.append(f"Invalid proxy URL format: {proxy.url}")

    # Check credential consistency
    if (proxy.username is None) != (proxy.password is None):
        errors.append("Username and password must both be present or both absent")

    # Check stats consistency
    if proxy.total_requests < proxy.total_successes + proxy.total_failures:
        errors.append(
            f"Inconsistent stats: total_requests={proxy.total_requests}, "
            f"successes={proxy.total_successes}, failures={proxy.total_failures}"
        )

    # Check consecutive failures
    if proxy.consecutive_failures < 0:
        errors.append(f"Invalid consecutive_failures: {proxy.consecutive_failures}")

    return errors


# ============================================================================
# CRYPTO UTILITIES
# ============================================================================


def encrypt_credentials(plaintext: str, key: Optional[str] = None) -> str:
    """
    Encrypt credentials using Fernet symmetric encryption.

    Args:
        plaintext: Plaintext to encrypt
        key: Optional encryption key (base64-encoded). If None, generates new key.

    Returns:
        Encrypted text (base64-encoded)

    Raises:
        ImportError: If cryptography package not installed
    """
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        raise ImportError(
            "cryptography package required for encryption. "
            "Install with: pip install 'proxywhirl[security]'"
        )

    if key is None:
        key = Fernet.generate_key().decode()

    cipher = Fernet(key.encode())
    encrypted = cipher.encrypt(plaintext.encode())
    return str(encrypted.decode())


def decrypt_credentials(ciphertext: str, key: str) -> str:
    """
    Decrypt credentials using Fernet symmetric encryption.

    Args:
        ciphertext: Encrypted text (base64-encoded)
        key: Encryption key (base64-encoded)

    Returns:
        Decrypted plaintext

    Raises:
        ImportError: If cryptography package not installed
        InvalidToken: If key is incorrect or ciphertext is invalid
    """
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        raise ImportError(
            "cryptography package required for decryption. "
            "Install with: pip install 'proxywhirl[security]'"
        )

    cipher = Fernet(key.encode())
    decrypted = cipher.decrypt(ciphertext.encode())
    return str(decrypted.decode())


def generate_encryption_key() -> str:
    """
    Generate a new Fernet encryption key.

    Returns:
        Base64-encoded encryption key

    Raises:
        ImportError: If cryptography package not installed
    """
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        raise ImportError(
            "cryptography package required for key generation. "
            "Install with: pip install 'proxywhirl[security]'"
        )

    return str(Fernet.generate_key().decode())


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def proxy_to_dict(proxy: Proxy, include_stats: bool = True) -> dict[str, Any]:
    """
    Convert a Proxy instance to a dictionary.

    Args:
        proxy: Proxy to convert
        include_stats: Include statistics

    Returns:
        Dictionary representation
    """
    data: dict[str, Any] = {
        "id": str(proxy.id),
        "url": str(proxy.url),
        "protocol": proxy.protocol,
        "health_status": proxy.health_status.value,
        "source": proxy.source.value,
        "tags": list(proxy.tags),
        "created_at": proxy.created_at.isoformat(),
        "updated_at": proxy.updated_at.isoformat(),
    }

    if include_stats:
        stats_dict: dict[str, Any] = {
            "total_requests": proxy.total_requests,
            "total_successes": proxy.total_successes,
            "total_failures": proxy.total_failures,
            "success_rate": proxy.success_rate,
            "average_response_time_ms": proxy.average_response_time_ms,
            "consecutive_failures": proxy.consecutive_failures,
            "last_success_at": proxy.last_success_at.isoformat() if proxy.last_success_at else None,
            "last_failure_at": proxy.last_failure_at.isoformat() if proxy.last_failure_at else None,
        }
        data["stats"] = stats_dict

    return data


def create_proxy_from_url(
    url: str, source: ProxySource = ProxySource.USER, tags: Optional[set[str]] = None
) -> Proxy:
    """
    Create a Proxy instance from a URL string.

    Args:
        url: Proxy URL
        source: Origin of proxy
        tags: Optional tags

    Returns:
        Proxy instance

    Raises:
        ValueError: If URL is invalid
    """
    from pydantic import ValidationError

    try:
        proxy = Proxy(url=url, source=source, tags=tags or set())
        return proxy
    except ValidationError as e:
        raise ValueError(f"Invalid proxy URL: {url}") from e
