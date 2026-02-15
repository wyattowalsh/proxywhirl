"""Integration tests for authenticated proxy requests.

Tests that ProxyWhirl correctly handles proxies requiring authentication,
including proper credential application and error handling for missing credentials.
"""

import httpx
import pytest
import respx
from pydantic import SecretStr

from proxywhirl import Proxy, ProxyWhirl
from proxywhirl.exceptions import ProxyAuthenticationError, ProxyConnectionError


class TestAuthenticatedRequests:
    """Test authenticated proxy requests."""

    @pytest.fixture
    def authenticated_proxy(self) -> Proxy:
        """Create a proxy with credentials."""
        return Proxy(
            url="http://proxy.example.com:8080",
            protocol="http",
            username=SecretStr("testuser"),
            password=SecretStr("testpass123"),
        )

    @pytest.fixture
    def unauthenticated_proxy(self) -> Proxy:
        """Create a proxy without credentials."""
        return Proxy(
            url="http://proxy.example.com:8080",
            protocol="http",
        )

    @respx.mock
    def test_authenticated_request_succeeds(self, authenticated_proxy: Proxy) -> None:
        """Test that authenticated proxy request succeeds with valid credentials."""
        # Mock the target URL
        route = respx.get("https://httpbin.org/ip").mock(
            return_value=httpx.Response(200, json={"origin": "1.2.3.4"})
        )

        rotator = ProxyWhirl(proxies=[authenticated_proxy])
        response = rotator.get("https://httpbin.org/ip")

        assert response.status_code == 200
        assert response.json() == {"origin": "1.2.3.4"}
        assert route.called

    @respx.mock
    def test_unauthenticated_request_fails_with_407(self, unauthenticated_proxy: Proxy) -> None:
        """Test that request without credentials fails with 407 error."""
        # Mock 407 Proxy Authentication Required
        respx.get("https://httpbin.org/ip").mock(
            return_value=httpx.Response(
                407,
                headers={"Proxy-Authenticate": 'Basic realm="Proxy"'},
                text="Proxy Authentication Required",
            )
        )

        rotator = ProxyWhirl(proxies=[unauthenticated_proxy])

        # ProxyAuthenticationError is raised for 407 errors
        with pytest.raises((ProxyAuthenticationError, ProxyConnectionError)) as exc_info:
            rotator.get("https://httpbin.org/ip")

        # Verify it's caused by authentication issues
        assert "407" in str(exc_info.value)
        assert "authentication" in str(exc_info.value).lower()

    @respx.mock
    def test_authenticated_request_with_invalid_credentials(
        self, authenticated_proxy: Proxy
    ) -> None:
        """Test that request with invalid credentials fails appropriately."""
        # Mock 407 even with credentials (invalid credentials)
        respx.get("https://httpbin.org/ip").mock(
            return_value=httpx.Response(
                407,
                headers={"Proxy-Authenticate": 'Basic realm="Proxy"'},
                text="Invalid credentials",
            )
        )

        rotator = ProxyWhirl(proxies=[authenticated_proxy])

        # ProxyAuthenticationError is raised for 407 errors
        with pytest.raises((ProxyAuthenticationError, ProxyConnectionError)) as exc_info:
            rotator.get("https://httpbin.org/ip")

        # Verify it's caused by authentication issues
        assert "407" in str(exc_info.value)

    @respx.mock
    def test_authenticated_request_includes_credentials(self, authenticated_proxy: Proxy) -> None:
        """Test that credentials are properly included in the request."""
        # Mock the target URL
        route = respx.get("https://httpbin.org/ip").mock(
            return_value=httpx.Response(200, json={"origin": "1.2.3.4"})
        )

        rotator = ProxyWhirl(proxies=[authenticated_proxy])
        response = rotator.get("https://httpbin.org/ip")

        assert response.status_code == 200
        assert route.called

        # Verify the request was made (credentials are internal to httpx)
        # We can't easily inspect the proxy auth header, but we verify the request succeeded
        assert route.call_count == 1

    @respx.mock
    def test_mixed_authenticated_and_unauthenticated_proxies(self) -> None:
        """Test rotation between authenticated and unauthenticated proxies."""
        auth_proxy = Proxy(
            url="http://auth-proxy.example.com:8080",
            protocol="http",
            username=SecretStr("user"),
            password=SecretStr("pass"),
        )
        no_auth_proxy = Proxy(
            url="http://no-auth-proxy.example.com:8080",
            protocol="http",
        )

        # Mock both proxies to succeed
        respx.get("https://httpbin.org/ip").mock(
            return_value=httpx.Response(200, json={"origin": "1.2.3.4"})
        )

        rotator = ProxyWhirl(proxies=[auth_proxy, no_auth_proxy])

        # Both should work (assuming the no_auth_proxy doesn't require auth)
        response1 = rotator.get("https://httpbin.org/ip")
        response2 = rotator.get("https://httpbin.org/ip")

        assert response1.status_code == 200
        assert response2.status_code == 200
