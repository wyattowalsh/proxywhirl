"""Proxy credential rotation for changing proxy authentication.

Supports rotating credentials (username/password) for authenticated proxies
without needing to reset the entire proxy pool.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from loguru import logger

from proxywhirl.models import Proxy


@dataclass
class CredentialRotationPolicy:
    """Policy for rotating proxy credentials."""

    rotation_interval: int = 3600  # seconds
    max_rotations: int = 10
    track_history: bool = True


class CredentialRotationManager:
    """Manages proxy credential rotation."""

    def __init__(self) -> None:
        """Initialize credential rotation manager."""
        self.rotation_history: dict[str, list[dict[str, Any]]] = {}
        self.current_credentials: dict[str, dict[str, str]] = {}
        self.rotation_policy = CredentialRotationPolicy()

    def set_credentials(self, proxy_url: str, username: str, password: str) -> None:
        """Set credentials for a proxy.

        Args:
            proxy_url: Proxy URL
            username: Username
            password: Password
        """
        self.current_credentials[proxy_url] = {"username": username, "password": password}
        self._record_rotation(proxy_url, username)
        logger.debug(f"Set credentials for proxy: {proxy_url}")

    def get_credentials(self, proxy_url: str) -> dict[str, str] | None:
        """Get current credentials for a proxy.

        Args:
            proxy_url: Proxy URL

        Returns:
            Dict with 'username' and 'password' keys or None
        """
        return self.current_credentials.get(proxy_url)

    def rotate_credentials(self, proxy_url: str, new_username: str, new_password: str) -> None:
        """Rotate credentials for a proxy.

        Args:
            proxy_url: Proxy URL
            new_username: New username
            new_password: New password
        """
        if proxy_url not in self.current_credentials:
            logger.warning(f"No credentials found for proxy: {proxy_url}")
            return

        old_creds = self.current_credentials[proxy_url]
        self.current_credentials[proxy_url] = {"username": new_username, "password": new_password}

        self._record_rotation(proxy_url, new_username, old_creds.get("username"))
        logger.info(f"Rotated credentials for proxy: {proxy_url}")

    def apply_credentials_to_proxy(self, proxy: Proxy) -> Proxy:
        """Apply current credentials to a proxy.

        Args:
            proxy: Proxy object to update

        Returns:
            Proxy with updated credentials
        """
        creds = self.get_credentials(proxy.url)
        if creds:
            # Create new proxy with credentials
            proxy_copy = proxy.model_copy(update={})
            proxy_copy.username = creds.get("username")
            proxy_copy.password = creds.get("password")
            return proxy_copy
        return proxy

    def _record_rotation(
        self, proxy_url: str, new_username: str, old_username: str | None = None
    ) -> None:
        """Record credential rotation in history."""
        if proxy_url not in self.rotation_history:
            self.rotation_history[proxy_url] = []

        record = {
            "timestamp": datetime.now().isoformat(),
            "old_username": old_username,
            "new_username": new_username,
        }

        history = self.rotation_history[proxy_url]
        history.append(record)

        # Trim history if needed
        if len(history) > self.rotation_policy.max_rotations:
            history.pop(0)

    def get_rotation_history(self, proxy_url: str) -> list[dict[str, Any]]:
        """Get rotation history for a proxy.

        Args:
            proxy_url: Proxy URL

        Returns:
            List of rotation records
        """
        return self.rotation_history.get(proxy_url, [])

    def clear_credentials(self, proxy_url: str) -> None:
        """Clear credentials for a proxy.

        Args:
            proxy_url: Proxy URL
        """
        if proxy_url in self.current_credentials:
            del self.current_credentials[proxy_url]
            logger.debug(f"Cleared credentials for proxy: {proxy_url}")

    def clear_all_credentials(self) -> None:
        """Clear all stored credentials."""
        self.current_credentials.clear()
        logger.info("Cleared all proxy credentials")


_rotation_manager: CredentialRotationManager | None = None


def get_credential_rotation_manager() -> CredentialRotationManager:
    """Get global credential rotation manager instance."""
    global _rotation_manager
    if _rotation_manager is None:
        _rotation_manager = CredentialRotationManager()
    return _rotation_manager
