"""Unit tests for ProxyCredentials model."""

from pydantic import SecretStr

from proxywhirl.models import ProxyCredentials


class TestProxyCredentialsBasic:
    """Tests for ProxyCredentials basic functionality."""

    def test_create_credentials_with_username_and_password(self):
        """Test creating credentials with both username and password."""
        creds = ProxyCredentials(username=SecretStr("testuser"), password=SecretStr("testpass"))

        assert creds.username.get_secret_value() == "testuser"
        assert creds.password.get_secret_value() == "testpass"

    def test_credentials_to_dict_redacts_secrets(self):
        """Test that to_dict() redacts sensitive information."""
        creds = ProxyCredentials(username=SecretStr("testuser"), password=SecretStr("testpass"))

        result = creds.model_dump()

        # Pydantic SecretStr automatically redacts in repr/dict
        assert "testuser" not in str(result)
        assert "testpass" not in str(result)

    def test_credentials_string_representation_redacts_secrets(self):
        """Test that str() and repr() don't expose secrets."""
        creds = ProxyCredentials(username=SecretStr("testuser"), password=SecretStr("testpass"))

        str_repr = str(creds)
        repr_str = repr(creds)

        assert "testuser" not in str_repr
        assert "testpass" not in str_repr
        assert "testuser" not in repr_str
        assert "testpass" not in repr_str


class TestProxyCredentialsHttpxAuth:
    """Tests for to_httpx_auth() method."""

    def test_to_httpx_auth_returns_basic_auth(self):
        """Test that to_httpx_auth() returns httpx BasicAuth."""
        creds = ProxyCredentials(username=SecretStr("user"), password=SecretStr("pass"))

        auth = creds.to_httpx_auth()

        # Check it's the right type
        from httpx import BasicAuth

        assert isinstance(auth, BasicAuth)

    def test_to_httpx_auth_with_empty_password(self):
        """Test auth creation with empty password."""
        creds = ProxyCredentials(username=SecretStr("user"), password=SecretStr(""))

        auth = creds.to_httpx_auth()
        assert auth is not None

    def test_to_httpx_auth_with_special_characters(self):
        """Test auth with special characters in credentials."""
        creds = ProxyCredentials(
            username=SecretStr("user@domain.com"), password=SecretStr("p@ss:w0rd!")
        )

        auth = creds.to_httpx_auth()
        assert auth is not None
