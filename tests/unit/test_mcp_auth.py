"""Unit tests for MCP authentication.

Tests cover MCPAuth class for authentication and session management.
"""

from __future__ import annotations

from types import SimpleNamespace

from proxywhirl.mcp.auth import MCPAuth


class TestMCPAuthInit:
    """Test MCPAuth initialization."""

    def test_init_without_api_key(self) -> None:
        """Test initialization without API key."""
        auth = MCPAuth()
        assert auth.api_key is None

    def test_init_with_api_key(self) -> None:
        """Test initialization with API key."""
        auth = MCPAuth(api_key="test-key-123")
        assert auth.api_key == "test-key-123"


class TestMCPAuthAuthenticate:
    """Test authentication method."""

    def test_authenticate_no_key_required(self) -> None:
        """Test that no auth is required when no API key is set."""
        auth = MCPAuth()
        assert auth.authenticate({}) is True
        assert auth.authenticate({"api_key": "any-key"}) is True

    def test_authenticate_correct_key(self) -> None:
        """Test successful authentication with correct key."""
        auth = MCPAuth(api_key="secret-key")
        assert auth.authenticate({"api_key": "secret-key"}) is True

    def test_authenticate_header_key(self) -> None:
        """Test successful authentication from HTTP-style headers."""
        auth = MCPAuth(api_key="secret-key")
        credentials = {"headers": {"X-API-Key": "secret-key"}}

        assert auth.authenticate(credentials) is True

    def test_authenticate_bearer_token(self) -> None:
        """Test successful authentication from Authorization bearer metadata."""
        auth = MCPAuth(api_key="secret-key")
        credentials = {"metadata": {"Authorization": "Bearer secret-key"}}

        assert auth.authenticate(credentials) is True

    def test_authenticate_wrong_key(self) -> None:
        """Test failed authentication with wrong key."""
        auth = MCPAuth(api_key="secret-key")
        assert auth.authenticate({"api_key": "wrong-key"}) is False

    def test_authenticate_missing_key(self) -> None:
        """Test failed authentication with missing key."""
        auth = MCPAuth(api_key="secret-key")
        assert auth.authenticate({}) is False

    def test_authenticate_none_key(self) -> None:
        """Test failed authentication with None key."""
        auth = MCPAuth(api_key="secret-key")
        assert auth.authenticate({"api_key": None}) is False


class TestMCPAuthContextCredentials:
    """Test credential extraction from MCP context carriers."""

    def test_extract_context_credentials_from_metadata(self) -> None:
        """Metadata credentials are normalized for middleware auth."""
        auth = MCPAuth(api_key="secret-key")
        context = SimpleNamespace(
            message=SimpleNamespace(params=SimpleNamespace(metadata={"api_key": "secret-key"}))
        )

        assert auth.extract_context_credentials(context) == {"api_key": "secret-key"}

    def test_extract_context_credentials_from_headers(self) -> None:
        """Header credentials are normalized for middleware auth."""
        auth = MCPAuth(api_key="secret-key")
        context = SimpleNamespace(
            message=SimpleNamespace(
                params=SimpleNamespace(metadata={"headers": {"Authorization": "Bearer secret-key"}})
            )
        )

        assert auth.extract_context_credentials(context) == {"api_key": "secret-key"}


class TestMCPAuthCreateSession:
    """Test session creation method."""

    def test_create_session_success(self) -> None:
        """Test successful session creation."""
        auth = MCPAuth(api_key="secret-key")
        session = auth.create_session("session-123", {"api_key": "secret-key"})

        assert session is not None
        assert session["session_id"] == "session-123"
        assert session["authenticated"] is True
        assert "read" in session["permissions"]
        assert "write" in session["permissions"]

    def test_create_session_no_auth_required(self) -> None:
        """Test session creation when no auth required."""
        auth = MCPAuth()
        session = auth.create_session("session-456", {})

        assert session is not None
        assert session["session_id"] == "session-456"
        assert session["authenticated"] is True

    def test_create_session_auth_failed(self) -> None:
        """Test session creation fails with wrong credentials."""
        auth = MCPAuth(api_key="secret-key")
        session = auth.create_session("session-789", {"api_key": "wrong-key"})

        assert session is None

    def test_create_session_missing_credentials(self) -> None:
        """Test session creation fails with missing credentials."""
        auth = MCPAuth(api_key="secret-key")
        session = auth.create_session("session-abc", {})

        assert session is None
