"""
Security utilities and protections for ProxyWhirl.

This module provides:
- IP blocklist for SSRF protection (IP-based and hostname-based)
- Credential redaction filters
- Input validation utilities
- TLS verification helpers
- PBKDF2-based key derivation
- Safe DNS resolution with blocklist checking
"""

from __future__ import annotations

import concurrent.futures
import hashlib
import hmac
import ipaddress
import logging
import os
import re
import socket
from enum import Enum
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse

from loguru import logger

# ============================================================================
# BLOCKLISTS & ENUMS
# ============================================================================


class BlocklistCategory(str, Enum):
    """Categories of IP blocklists."""

    LOOPBACK = "loopback"
    PRIVATE = "private"
    LINK_LOCAL = "link_local"
    RESERVED = "reserved"
    MULTICAST = "multicast"
    METADATA_SERVICES = "metadata_services"


# AWS Metadata Service blocklist (CVE-style SSRF)
AWS_METADATA_BLOCKLIST = {
    ipaddress.IPv4Address("169.254.169.254"),
}

# GCP Metadata Service (uses same IP as AWS, but also checks hostname)
GCP_METADATA_BLOCKLIST = {
    ipaddress.IPv4Address("169.254.169.254"),
}

# Azure Metadata Service
AZURE_METADATA_BLOCKLIST = {
    ipaddress.IPv4Address("169.254.169.254"),
}

# Alibaba Metadata Service
ALIBABA_METADATA_BLOCKLIST = {
    ipaddress.IPv4Address("100.100.100.200"),
}

# Docker host metadata (internal)
DOCKER_METADATA_BLOCKLIST = {
    ipaddress.IPv4Address("127.0.0.11"),
}

# Combined metadata services blocklist
METADATA_SERVICES_BLOCKLIST = (
    AWS_METADATA_BLOCKLIST
    | GCP_METADATA_BLOCKLIST
    | AZURE_METADATA_BLOCKLIST
    | ALIBABA_METADATA_BLOCKLIST
    | DOCKER_METADATA_BLOCKLIST
)

# ============================================================================
# BLOCKLIST VALIDATION
# ============================================================================


def is_ip_blocked(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> tuple[bool, str]:
    """
    Check if an IP address is blocked by any security policy.

    Args:
        ip: IP address to check

    Returns:
        Tuple of (is_blocked, reason)
    """
    # Check IPv6-mapped IPv4 addresses
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        return is_ip_blocked(ip.ipv4_mapped)

    # Check metadata services (highest priority)
    if ip in METADATA_SERVICES_BLOCKLIST:
        return True, f"Metadata service blocked: {ip}"

    # Check standard blocklists — most specific first
    if ip.is_loopback:
        return True, "Loopback address blocked"

    if ip.is_link_local:
        return True, "Link-local address blocked"

    if ip.is_multicast:
        return True, "Multicast address blocked"

    if ip.is_reserved:
        return True, "Reserved address blocked"

    if ip.is_unspecified:
        return True, "Unspecified address blocked"

    if ip.is_private:
        return True, "Private IP address blocked"

    return False, ""


def _resolve_hostname_addresses_with_timeout(hostname: str, timeout: float = 2.0) -> set[str]:
    """Resolve a hostname to all IPv4/IPv6 addresses without mutating socket timeouts."""

    def _resolve_all() -> set[str]:
        addresses: set[str] = set()
        for family, _, _, _, sockaddr in socket.getaddrinfo(hostname, None):
            if family in {socket.AF_INET, socket.AF_INET6}:
                addresses.add(sockaddr[0])
        return addresses

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_resolve_all)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError as exc:
            raise TimeoutError(f"DNS resolution timed out for {hostname}") from exc


def validate_proxy_url_safety(url: str) -> tuple[bool, str]:
    """
    Validate that a proxy URL doesn't point to internal/blocked addresses.

    This prevents using proxy servers to access internal resources (SSRF).

    Args:
        url: Proxy URL to validate

    Returns:
        Tuple of (is_safe, reason)
    """
    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"Invalid URL format: {e}"

    if not parsed.hostname:
        return False, "URL must include a valid hostname"

    # Try to parse as IP first (faster path)
    try:
        ip = ipaddress.ip_address(parsed.hostname)
        blocked, reason = is_ip_blocked(ip)
        return not blocked, reason if blocked else ""
    except ValueError:
        # Not an IP, try DNS resolution with blocklist check
        pass

    # Skip resolution for known internal TLDs
    internal_tlds = {".local", ".internal", ".lan", ".corp", ".localhost"}
    hostname_lower = parsed.hostname.lower()
    if any(hostname_lower.endswith(tld) for tld in internal_tlds):
        return False, f"Internal domain name blocked: {parsed.hostname}"

    # Check for common metadata service hostnames
    metadata_hostnames = {
        "metadata.google.internal",
        "gce-metadata.appspot.com",
        "instance-data",
        "instance-metadata",
        "169.254.169.254",
        "100.100.100.200",
        "127.0.0.11",
        "docker.host",
        "host.docker.internal",
    }
    if hostname_lower in metadata_hostnames or any(
        hostname_lower.endswith("." + m) for m in metadata_hostnames
    ):
        return False, f"Metadata service hostname blocked: {parsed.hostname}"

    # Try DNS resolution (with timeout to prevent DoS; no global socket mutation)
    try:
        ip_strings = _resolve_hostname_addresses_with_timeout(parsed.hostname, timeout=2.0)
        if not ip_strings:
            return False, f"DNS resolution returned no addresses for {parsed.hostname}"

        for ip_str in ip_strings:
            ip = ipaddress.ip_address(ip_str)
            blocked, reason = is_ip_blocked(ip)
            if blocked:
                return False, reason
        return True, ""
    except (TimeoutError, socket.gaierror, OSError) as exc:
        return False, f"DNS resolution failed for {parsed.hostname}: {exc}"
    except Exception as exc:
        return False, f"DNS safety validation failed for {parsed.hostname}: {exc}"


# ============================================================================
# CREDENTIAL REDACTION
# ============================================================================


SENSITIVE_QUERY_PARAMS = {
    "auth",
    "authorization",
    "credential",
    "credentials",
    "key",
    "pass",
    "passwd",
    "password",
    "secret",
    "token",
    "api_key",
    "apikey",
}

SENSITIVE_LOG_KEYS = {
    "password",
    "passwd",
    "secret",
    "token",
    "api_key",
    "apikey",
    "credential",
    "credentials",
    "authorization",
    "auth",
}


def is_sensitive_param_name(param_name: str) -> bool:
    """Check if a parameter name indicates sensitive data."""
    normalized = re.sub(r"[^a-z0-9_]+", "_", param_name.lower()).strip("_")
    return normalized in SENSITIVE_QUERY_PARAMS or any(
        sensitive in normalized for sensitive in SENSITIVE_QUERY_PARAMS
    )


def redact_url(url: str) -> str:
    """
    Redact credentials and sensitive parameters from a URL.

    Args:
        url: URL to redact

    Returns:
        Redacted URL string
    """
    try:
        parsed = urlparse(url)

        # Redact credentials in netloc
        if parsed.username is not None or parsed.password is not None:
            host_port = parsed.netloc.rsplit("@", 1)[-1]
            redacted_netloc = f"***:***@{host_port}"
            parsed = parsed._replace(netloc=redacted_netloc)

        # Redact sensitive query parameters
        if parsed.query:
            query_items = [
                (key, "***" if is_sensitive_param_name(key) else value)
                for key, value in parse_qsl(parsed.query, keep_blank_values=True)
            ]
            query = urlencode(query_items).replace("%2A%2A%2A", "***")
            parsed = parsed._replace(query=query)

        return parsed.geturl()
    except Exception:
        # Fallback to regex-based redaction
        return re.sub(r"://[^/@?#]*@", "://***:***@", url)


def redact_dict(data: Any) -> Any:
    """
    Recursively redact sensitive data from a dictionary.

    Args:
        data: Dictionary or value to redact

    Returns:
        Redacted data
    """
    from pydantic import SecretStr

    if isinstance(data, SecretStr):
        return "***"
    elif isinstance(data, dict):
        return {
            key: (
                redact_dict(value)
                if any(s in key.lower() for s in SENSITIVE_LOG_KEYS)
                and isinstance(value, (dict, list, tuple))
                else (
                    "***"
                    if any(s in key.lower() for s in SENSITIVE_LOG_KEYS)
                    else redact_dict(value)
                )
            )
            for key, value in data.items()
        }
    elif isinstance(data, (list, tuple)):
        return [redact_dict(item) for item in data]
    elif isinstance(data, str):
        if "://" in data and "@" in data:
            return redact_url(data)
        return data
    return data


# ============================================================================
# LOGGING FILTER FOR REDACTION
# ============================================================================


class RedactionFilter(logging.Filter):
    """Logging filter that redacts sensitive data from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Redact sensitive data from log record."""
        # Redact message
        if isinstance(record.msg, str):
            record.msg = _redact_string_secrets(record.msg)

        # Redact message arguments
        if record.args:
            if isinstance(record.args, dict):
                record.args = redact_dict(record.args)
            elif isinstance(record.args, (tuple, list)):
                record.args = tuple(
                    _redact_string_secrets(str(arg)) if isinstance(arg, str) else arg
                    for arg in record.args
                )

        # Redact extra fields
        if hasattr(record, "__dict__"):
            for key in list(record.__dict__.keys()):
                if any(s in key.lower() for s in SENSITIVE_LOG_KEYS):
                    record.__dict__[key] = "***"

        return True


def _redact_string_secrets(text: str) -> str:
    """Redact common secret patterns from a string."""
    # Redact URLs with credentials
    text = re.sub(r"([a-z][a-z0-9+.-]*://)[^/@\s?#]+@", r"\1***:***@", text)

    # Redact values after known secret parameter names
    text = re.sub(
        r"(?i)(password|token|api_?key|secret|credential)([\"']?\s*[:=]\s*[\"']?)([^\"'\s&,}]+)",
        r"\1\2***",
        text,
    )

    return text


# ============================================================================
# LOGURU INTEGRATION
# ============================================================================


def add_redaction_to_loguru() -> None:
    """Add redaction filter to loguru logger."""
    logger.enable("proxywhirl")

    def redacting_patcher(record: dict[str, Any]) -> None:
        # Redact message
        if isinstance(record["message"], str):
            record["message"] = _redact_string_secrets(record["message"])

        # Redact extra context
        if record["extra"]:
            record["extra"] = redact_dict(record["extra"])

    logger.configure(patcher=redacting_patcher)


# ============================================================================
# INPUT VALIDATION
# ============================================================================


def validate_input_string(value: str, max_length: int = 2048, pattern: str | None = None) -> str:
    """
    Validate and sanitize a string input.

    Args:
        value: String to validate
        max_length: Maximum allowed length
        pattern: Optional regex pattern for validation

    Returns:
        Validated string

    Raises:
        ValueError: If validation fails
    """
    if not isinstance(value, str):
        raise ValueError(f"Expected string, got {type(value).__name__}")

    if len(value) > max_length:
        raise ValueError(f"String exceeds maximum length of {max_length}")

    if pattern and not re.match(pattern, value):
        raise ValueError("String does not match required pattern")

    return value


def validate_input_port(port: int | str) -> int:
    """
    Validate a port number.

    Args:
        port: Port number to validate

    Returns:
        Validated port as integer

    Raises:
        ValueError: If port is invalid
    """
    try:
        port_int = int(port)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Port must be an integer, got {type(port).__name__}") from e

    if not 1 <= port_int <= 65535:
        raise ValueError(f"Port must be between 1 and 65535, got {port_int}")

    return port_int


def validate_proxy_credentials(
    username: str | None, password: str | None
) -> tuple[str | None, str | None]:
    """
    Validate proxy credentials.

    Args:
        username: Optional username
        password: Optional password

    Returns:
        Tuple of (username, password)

    Raises:
        ValueError: If validation fails
    """
    if username is not None:
        username = validate_input_string(username, max_length=256)

    if password is not None:
        password = validate_input_string(password, max_length=256)

    # Both must be present or both must be absent
    if (username is None) != (password is None):
        raise ValueError("Both username and password must be provided together")

    return username, password


# ============================================================================
# PBKDF2 KEY DERIVATION (for encryption key generation)
# ============================================================================


def derive_key_pbkdf2(
    password: str,
    salt: bytes | None = None,
    iterations: int = 100000,
    hash_name: str = "sha256",
    dklen: int = 32,
) -> tuple[bytes, bytes]:
    """
    Derive a cryptographic key from a password using PBKDF2.

    Args:
        password: Password/passphrase to derive key from
        salt: Salt bytes (random 16 bytes generated if not provided)
        iterations: Number of PBKDF2 iterations (100k recommended for security)
        hash_name: Hash algorithm to use ('sha256', 'sha512', etc.)
        dklen: Desired key length in bytes (32 for 256-bit keys)

    Returns:
        Tuple of (derived_key, salt) - salt needed for later verification

    Raises:
        ValueError: If parameters are invalid
    """
    if not password:
        raise ValueError("Password cannot be empty")

    if iterations < 10000:
        raise ValueError(f"Iterations must be >= 10000, got {iterations}")

    if dklen < 16:
        raise ValueError(f"Key length must be >= 16 bytes, got {dklen}")

    # Generate random salt if not provided
    if salt is None:
        salt = os.urandom(16)

    if len(salt) < 8:
        raise ValueError(f"Salt must be >= 8 bytes, got {len(salt)}")

    try:
        # Use PBKDF2 to derive key
        key = hashlib.pbkdf2_hmac(
            hash_name,
            password.encode("utf-8"),
            salt,
            iterations,
            dklen=dklen,
        )
        return key, salt
    except ValueError as e:
        raise ValueError(f"Invalid hash algorithm: {hash_name}") from e


def verify_pbkdf2_key(
    password: str,
    stored_key: bytes,
    salt: bytes,
    iterations: int = 100000,
    hash_name: str = "sha256",
    dklen: int = 32,
) -> bool:
    """
    Verify a password against a stored PBKDF2-derived key.

    Args:
        password: Password to verify
        stored_key: Previously derived key from derive_key_pbkdf2()
        salt: Salt that was used in derive_key_pbkdf2()
        iterations: Number of iterations (must match original)
        hash_name: Hash algorithm (must match original)
        dklen: Key length (must match original)

    Returns:
        True if password matches, False otherwise
    """
    try:
        derived_key, _ = derive_key_pbkdf2(
            password,
            salt=salt,
            iterations=iterations,
            hash_name=hash_name,
            dklen=dklen,
        )
        # Constant-time comparison to prevent timing attacks
        return hmac.compare_digest(stored_key, derived_key)
    except Exception:
        return False


__all__ = [
    "BlocklistCategory",
    "is_ip_blocked",
    "validate_proxy_url_safety",
    "redact_url",
    "redact_dict",
    "RedactionFilter",
    "add_redaction_to_loguru",
    "validate_input_string",
    "validate_input_port",
    "validate_proxy_credentials",
    "derive_key_pbkdf2",
    "verify_pbkdf2_key",
]
