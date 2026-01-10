"""Authentication for MCP server."""

from __future__ import annotations

import secrets


class MCPAuth:
    """Authentication handler for MCP connections."""

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize auth handler."""
        self.api_key = api_key

    def authenticate(self, credentials: dict) -> bool:
        """
        Authenticate an MCP connection.

        Args:
            credentials: Authentication credentials

        Returns:
            True if authenticated, False otherwise
        """
        if not self.api_key:
            # No authentication required
            return True

        provided_key = credentials.get("api_key")
        return secrets.compare_digest(provided_key or "", self.api_key or "")

    def create_session(self, session_id: str, credentials: dict) -> dict | None:
        """
        Create an authenticated session.

        Args:
            session_id: Unique session identifier
            credentials: Authentication credentials

        Returns:
            Session info if authenticated, None otherwise
        """
        if not self.authenticate(credentials):
            return None

        return {
            "session_id": session_id,
            "authenticated": True,
            "permissions": ["read", "write"],
        }
