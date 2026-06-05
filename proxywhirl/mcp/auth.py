"""Authentication for MCP server."""

from __future__ import annotations

import secrets
from collections.abc import Mapping
from typing import Any

_API_KEY_HEADER_NAMES = {"x-api-key", "proxywhirl-api-key", "api-key"}


class MCPAuth:
    """Authentication handler for MCP connections."""

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize auth handler."""
        self.api_key = api_key

    def authenticate(self, credentials: object | None) -> bool:
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

        provided_key = self.extract_credentials(credentials).get("api_key")
        if not isinstance(provided_key, str):
            return False
        return secrets.compare_digest(provided_key or "", self.api_key or "")

    def create_session(self, session_id: str, credentials: object | None) -> dict | None:
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

    def extract_credentials(self, credentials: object | None) -> dict[str, str]:
        """Normalize supported MCP credential carriers to an internal credential dict.

        MCP clients should pass credentials out-of-band via metadata or transport
        headers. Direct-call tests may still pass ``{"api_key": "..."}``.
        """
        api_key = self._extract_api_key(credentials)
        return {"api_key": api_key} if api_key else {}

    def extract_context_credentials(self, context: object | None) -> dict[str, str]:
        """Extract credentials from common FastMCP context metadata/header locations."""
        candidates: list[object | None] = [context]

        for attr in ("metadata", "meta", "headers", "request", "request_context"):
            candidates.append(getattr(context, attr, None))

        message = getattr(context, "message", None)
        candidates.append(message)
        params = getattr(message, "params", None)
        candidates.append(params)

        for attr in ("metadata", "meta", "_meta", "headers"):
            candidates.append(getattr(params, attr, None))

        request_context = getattr(context, "request_context", None)
        request = getattr(request_context, "request", None)
        candidates.append(request)
        for attr in ("metadata", "meta", "headers"):
            candidates.append(getattr(request_context, attr, None))
            candidates.append(getattr(request, attr, None))

        for candidate in candidates:
            credentials = self.extract_credentials(candidate)
            if credentials:
                return credentials
        return {}

    def _extract_api_key(self, source: object | None, seen: set[int] | None = None) -> str | None:
        """Find an API key in mappings, headers, metadata, or simple objects."""
        if source is None:
            return None

        if seen is None:
            seen = set()
        source_id = id(source)
        if source_id in seen:
            return None
        seen.add(source_id)

        if isinstance(source, Mapping):
            direct_key = source.get("api_key")
            if isinstance(direct_key, str) and direct_key:
                return direct_key

            header_key = self._extract_api_key_from_headers(source)
            if header_key:
                return header_key

            for nested_key in ("headers", "metadata", "meta", "_meta"):
                nested_value = source.get(nested_key)
                nested_key_value = self._extract_api_key(nested_value, seen)
                if nested_key_value:
                    return nested_key_value

        for attr in ("api_key", "headers", "metadata", "meta", "_meta"):
            nested_value = getattr(source, attr, None)
            if attr == "api_key" and isinstance(nested_value, str) and nested_value:
                return nested_value
            nested_key_value = self._extract_api_key(nested_value, seen)
            if nested_key_value:
                return nested_key_value

        return None

    @staticmethod
    def _extract_api_key_from_headers(headers: Mapping[str, Any]) -> str | None:
        """Extract API keys from common HTTP-style header names."""
        normalized = {str(key).lower(): value for key, value in headers.items()}

        for header_name in _API_KEY_HEADER_NAMES:
            header_value = normalized.get(header_name)
            if isinstance(header_value, str) and header_value:
                return header_value

        authorization = normalized.get("authorization")
        if isinstance(authorization, str):
            scheme, _, token = authorization.partition(" ")
            if scheme.lower() == "bearer" and token:
                return token

        return None
