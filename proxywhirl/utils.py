"""
Utility functions for logging, validation, and encryption.
"""

from __future__ import annotations

import ipaddress
import json
import re
import socket
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urlsplit, urlunsplit

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
        format_type: "auto", "json", or "text". "auto" detects TTY on stderr.
        redact_credentials: Whether to redact sensitive data
    """
    # Remove default handler
    logger.remove()

    # Resolve "auto" format: text for TTY, json otherwise
    if format_type == "auto":
        format_type = "text" if sys.stderr.isatty() else "json"

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
    from pydantic import SecretStr

    # Handle SecretStr objects
    if isinstance(data, SecretStr):
        return "***"
    elif isinstance(data, dict):
        redacted = {}
        for key, value in data.items():
            if any(
                sensitive in key.lower()
                for sensitive in [
                    "password",
                    "secret",
                    "token",
                    "api_key",
                    "credential",
                    "username",
                ]
            ):
                redacted[key] = "***"
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
    """Redact credentials from URLs (with LRU cache)."""
    return _redact_url_credentials_cached(url)


@lru_cache(maxsize=2048)
def _redact_url_credentials_cached(url: str) -> str:
    """Cached implementation for redacting URL credentials."""
    try:
        parsed = urlparse(url)
        if parsed.username is not None or parsed.password is not None:
            host_port = parsed.netloc.rsplit("@", 1)[-1]
            return parsed._replace(netloc=f"***:***@{host_port}").geturl()
    except Exception:
        return re.sub(r"://[^/@?#]*@", "://***:***@", url)
    return url


def mask_proxy_url(url: str) -> str:
    """
    Mask credentials in a proxy URL for safe display in verbose/debug output.

    Replaces username:password with ***:*** to prevent credential exposure.

    Args:
        url: Proxy URL that may contain credentials

    Returns:
        URL with credentials masked

    Example:
        >>> mask_proxy_url("http://user:pass@proxy.com:8080")
        "http://***:***@proxy.com:8080"
    """
    return _redact_url_credentials(url)


def public_proxy_url(url: str) -> str:
    """Return a proxy URL safe for public API, CLI, and MCP output.

    Unlike :func:`mask_proxy_url`, this strips userinfo entirely so public
    representations cannot reveal that credentials exist.
    """
    try:
        parsed = urlsplit(url)
        netloc = parsed.netloc.rsplit("@", 1)[-1]
        return urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))
    except Exception:
        return re.sub(r"://[^/@?#]*@", "://", url)


def mask_secret_str(secret: Any) -> str:
    """
    Mask a SecretStr or string value for safe display.

    Args:
        secret: SecretStr instance or string to mask

    Returns:
        str: Masked value (always ``"***"``).
    """
    from pydantic import SecretStr

    if isinstance(secret, SecretStr):
        return "***"
    elif isinstance(secret, str):
        return "***" if secret else ""
    return "***"


def scrub_credentials_from_dict(data: dict[str, Any]) -> dict[str, Any]:
    """
    Recursively scrub credentials from a dictionary for safe output.

    Masks:
    - Proxy URLs with credentials
    - SecretStr values
    - Dict keys containing sensitive terms (password, secret, token, etc.)

    Args:
        data: Dictionary that may contain sensitive data

    Returns:
        New dictionary with credentials masked
    """
    from pydantic import SecretStr

    scrubbed = {}
    for key, value in data.items():
        # Check if key indicates sensitive data
        if any(
            sensitive in key.lower()
            for sensitive in ["password", "secret", "token", "api_key", "credential", "username"]
        ):
            if isinstance(value, SecretStr) or value is not None:
                scrubbed[key] = "***"
            else:
                scrubbed[key] = None
        # Check for proxy URL values
        elif isinstance(value, str) and ("://" in value and "@" in value):
            scrubbed[key] = mask_proxy_url(value)
        # Handle SecretStr values
        elif isinstance(value, SecretStr):
            scrubbed[key] = "***"
        # Recursively scrub nested dicts
        elif isinstance(value, dict):
            scrubbed[key] = scrub_credentials_from_dict(value)
        # Recursively scrub lists
        elif isinstance(value, list):
            scrubbed[key] = [
                scrub_credentials_from_dict(item)
                if isinstance(item, dict)
                else mask_proxy_url(item)
                if isinstance(item, str) and ("://" in item and "@" in item)
                else item
                for item in value
            ]
        else:
            scrubbed[key] = value

    return scrubbed


# ============================================================================
# VALIDATION UTILITIES
# ============================================================================


PROXY_URL_SCHEMES = {"http", "https", "socks4", "socks5", "socks5h"}
PROXY_DNS_LABEL_PATTERN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$")


def _normalize_target_ip_address(value: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
    address = ipaddress.ip_address(value)
    if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped:
        return address.ipv4_mapped
    return address


def _raise_forbidden_target_address(address: ipaddress.IPv4Address | ipaddress.IPv6Address) -> None:
    if address.is_loopback:
        raise ValueError(
            "Access to loopback addresses is not allowed. This is blocked to prevent SSRF attacks."
        )

    if address.is_unspecified:
        raise ValueError(
            "Access to unspecified addresses is not allowed. "
            "This is blocked to prevent SSRF attacks."
        )

    if address.is_private:
        raise ValueError(
            "Access to private IP addresses is not allowed. "
            "This is blocked to prevent SSRF attacks."
        )

    if address.is_link_local:
        raise ValueError(
            "Access to link-local addresses is not allowed. "
            "This is blocked to prevent SSRF attacks."
        )

    if address.is_reserved or address.is_multicast:
        raise ValueError(
            "Access to reserved/multicast addresses is not allowed. "
            "This is blocked to prevent SSRF attacks."
        )


def validate_target_url_safe(url: str, allow_private: bool = False) -> None:
    """Validate a target URL to prevent SSRF attacks (API-safe version).

    This function validates URLs to prevent Server-Side Request Forgery (SSRF) attacks
    by blocking access to:
    - Localhost and loopback addresses (127.0.0.0/8, ::1)
    - Private IP ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
    - Link-local addresses (169.254.0.0/16)
    - Internal domain names (.local, .internal, .lan, .corp)

    Args:
        url: The URL to validate
        allow_private: If True, allow private/internal IP addresses (default: False)

    Raises:
        ValueError: If the URL is invalid or potentially dangerous

    Example:
        >>> validate_target_url_safe("https://example.com")  # OK
        >>> validate_target_url_safe("http://localhost:8080")  # Raises ValueError
        >>> validate_target_url_safe("http://192.168.1.1")  # Raises ValueError
        >>> validate_target_url_safe("http://192.168.1.1", allow_private=True)  # OK
    """
    # Parse the URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValueError(f"Invalid URL format: {e}") from e

    # Validate scheme (only http/https allowed for target URLs)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(
            f"Invalid URL scheme '{parsed.scheme}'. Only http:// and https:// are allowed. "
            f"Rejected schemes: file://, data://, gopher://, ftp://, etc."
        )

    # Validate hostname exists
    if not parsed.hostname:
        raise ValueError("URL must include a valid hostname")

    # Check for localhost/private addresses (SSRF protection)
    if not allow_private:
        hostname_lower = parsed.hostname.lower()

        # Block internal domain names first (before DNS resolution)
        internal_domains = [".local", ".internal", ".lan", ".corp"]
        if any(hostname_lower.endswith(domain) for domain in internal_domains):
            raise ValueError(
                f"Access to internal domain names is not allowed: {parsed.hostname}. "
                f"This is blocked to prevent SSRF attacks."
            )

        # Block "localhost" hostname explicitly
        if hostname_lower == "localhost":
            raise ValueError(
                "Access to localhost is not allowed. This is blocked to prevent SSRF attacks."
            )

        # Resolve hostname and validate the resolved IP address
        # This prevents bypasses via decimal/octal IP notation, IPv6-mapped IPv4,
        # DNS rebinding, and other SSRF evasion techniques
        try:
            resolved_addresses = socket.getaddrinfo(
                parsed.hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM
            )
        except socket.gaierror as exception:
            raise ValueError(f"Cannot resolve hostname: {parsed.hostname}") from exception

        checked_addresses: set[ipaddress.IPv4Address | ipaddress.IPv6Address] = set()
        for address_info in resolved_addresses:
            resolved_ip = address_info[4][0]
            try:
                address = _normalize_target_ip_address(resolved_ip)
            except ValueError as exception:
                raise ValueError(f"Cannot resolve hostname: {parsed.hostname}") from exception
            if address in checked_addresses:
                continue
            checked_addresses.add(address)
            _raise_forbidden_target_address(address)


def is_valid_proxy_url(url: str) -> bool:
    """
    Validate proxy URL format with caching.

    Args:
        url: URL to validate

    Returns:
        True if valid proxy URL
    """
    return _is_valid_proxy_url_cached(url)


@lru_cache(maxsize=2048)
def _is_valid_proxy_url_cached(url: str) -> bool:
    """Cached implementation of proxy URL validation."""
    try:
        parse_proxy_url(url)
    except ValueError:
        return False
    return True


def _is_valid_proxy_host(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        pass

    dns_name = host[:-1] if host.endswith(".") else host
    if not dns_name:
        return False
    if len(dns_name) > 253:
        return False

    return all(PROXY_DNS_LABEL_PATTERN.fullmatch(label) for label in dns_name.split("."))


def parse_proxy_url(url: str) -> dict[str, Any]:
    """
    Parse proxy URL into components with LRU cache.

    Args:
        url: Proxy URL to parse

    Returns:
        dict[str, Any]: Parsed URL components with protocol, host, port, username, password.

    Raises:
        ValueError: If URL is invalid
    """
    return _parse_proxy_url_cached(url)


@lru_cache(maxsize=2048)
def _parse_proxy_url_cached(url: str) -> dict[str, Any]:
    """
    Cached implementation of proxy URL parsing.

    Args:
        url: Proxy URL to parse

    Returns:
        dict[str, Any]: Parsed URL components

    Raises:
        ValueError: If URL is invalid
    """
    try:
        parsed = urlparse(url)
    except Exception as exception:
        raise ValueError(f"Invalid proxy URL format: {url}") from exception

    if parsed.scheme not in PROXY_URL_SCHEMES:
        allowed = ", ".join(f"{scheme}://" for scheme in sorted(PROXY_URL_SCHEMES))
        raise ValueError(f"Invalid proxy URL scheme: {url}. Must start with {allowed}")

    if parsed.path not in ("", "/") or parsed.params or parsed.query or parsed.fragment:
        raise ValueError(f"Invalid proxy URL path: {url}. Proxy URLs must not include path/query")

    host = parsed.hostname
    if not host or not _is_valid_proxy_host(host):
        raise ValueError(f"Invalid proxy URL host: {url}")

    username = parsed.username
    password = parsed.password
    if (username is None) != (password is None) or username == "" or password == "":
        raise ValueError(
            f"Invalid proxy URL credentials: {url}. Username and password must both be present"
        )

    try:
        port = parsed.port
    except ValueError as exception:
        raise ValueError(f"Invalid proxy URL port: {url}") from exception

    if port is None:
        raise ValueError(f"Invalid proxy URL port: {url}. Port is required")

    if port < 1 or port > 65535:
        raise ValueError(f"Invalid proxy URL port: {url}. Must be between 1 and 65535")

    return {
        "protocol": parsed.scheme,
        "host": host,
        "port": port,
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


def encrypt_credentials(plaintext: str, key: str | None = None) -> str:
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
    url: str, source: ProxySource = ProxySource.USER, tags: set[str] | None = None
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


# ============================================================================
# FILE OPERATION UTILITIES
# ============================================================================


def atomic_write(path: Path, content: str, encoding: str = "utf-8") -> None:
    """Write content atomically using temp file + rename.

    This prevents partial writes and corruption if the process is
    interrupted during the write operation.

    Args:
        path: Target file path
        content: Content to write
        encoding: File encoding (default: utf-8)

    Raises:
        OSError: If write or rename fails
    """
    import os
    import uuid

    temp_path = path.with_suffix(f".tmp.{uuid.uuid4().hex[:8]}")
    try:
        with open(temp_path, "w", encoding=encoding) as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())  # Ensure data is on disk
        temp_path.replace(path)  # Atomic on POSIX
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def atomic_write_json(path: Path, data: Any, **json_kwargs: Any) -> None:
    """Write JSON data atomically.

    Args:
        path: Target file path
        data: Data to serialize as JSON
        **json_kwargs: Arguments to pass to json.dumps()
    """
    content = json.dumps(data, **json_kwargs)
    atomic_write(path, content)


# ============================================================================
# CLI UTILITIES
# ============================================================================


class CLILock:
    """Context manager for CLI concurrency locking with Typer-aware error handling."""

    def __init__(self, config_dir: Path) -> None:
        """Initialize lock file manager.

        Args:
            config_dir: Directory where lock file will be created
        """
        from filelock import FileLock

        self.lock_path = config_dir / ".proxywhirl.lock"
        self.lock = FileLock(self.lock_path, timeout=0)
        self._lock_data_path = config_dir / ".proxywhirl.lock.json"

    def __enter__(self) -> CLILock:
        """Acquire lock or raise Typer exit."""
        import os
        import sys

        import typer
        from filelock import Timeout

        try:
            self.lock.acquire()
            # Write PID to lock data file
            lock_data = {"pid": os.getpid(), "command": " ".join(sys.argv)}
            with open(self._lock_data_path, "w") as f:
                json.dump(lock_data, f)
            return self
        except Timeout:
            # Read existing lock
            lock_data = {}
            if self._lock_data_path.exists():
                with open(self._lock_data_path) as f:
                    lock_data = json.load(f)

            typer.secho(
                f"Another proxywhirl process is running (PID {lock_data.get('pid', 'unknown')})\n"
                f"Command: {lock_data.get('command', 'unknown')}\n"
                f"Wait for it to finish, or use --force to override (unsafe).",
                err=True,
                fg="red",
            )
            raise typer.Exit(code=4)

    def __exit__(self, *args: Any) -> None:
        """Release lock and cleanup."""
        self.lock.release()
        self._lock_data_path.unlink(missing_ok=True)
