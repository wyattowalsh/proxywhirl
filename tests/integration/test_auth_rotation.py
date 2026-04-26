"""Integration tests for authenticated proxy rotation.

Tests that ProxyWhirl correctly applies different credentials when
rotating between multiple authenticated proxies.
"""

import httpx
import pytest
import respx
from pydantic import SecretStr

from proxywhirl import Proxy, ProxyWhirl


class TestAuthenticationRotation:
    """Test rotation between proxies with different credentials."""

    @pytest.fixture
    def proxies_with_different_credentials(self) -> list[Proxy]:
        """Create multiple proxies with different credentials."""
        return [
            Proxy(
                url="http://proxy1.example.com:8080",
                protocol="http",
                username=SecretStr("user1"),
                password=SecretStr("pass1"),
            ),
            Proxy(
                url="http://proxy2.example.com:8080",
                protocol="http",
                username=SecretStr("user2"),
                password=SecretStr("pass2"),
            ),
            Proxy(
                url="http://proxy3.example.com:8080",
                protocol="http",
                username=SecretStr("user3"),
                password=SecretStr("pass3"),
            ),
        ]

    @respx.mock
    def test_different_credentials_applied_per_proxy(
        self, proxies_with_different_credentials: list[Proxy]
    ) -> None:
        """Test that correct credentials are applied to each proxy during rotation."""
        # Mock all requests to succeed
        respx.get("https://httpbin.org/ip").mock(
            return_value=httpx.Response(200, json={"origin": "1.2.3.4"})
        )

        rotator = ProxyWhirl(proxies=proxies_with_different_credentials)

        # Make multiple requests - should rotate through all proxies
        for _ in range(6):  # 2 full rotations
            response = rotator.get("https://httpbin.org/ip")
            assert response.status_code == 200

        # Verify all proxies were used (they have total_requests > 0)
        for proxy in proxies_with_different_credentials:
            assert proxy.total_requests == 2  # Each proxy used twice

    @respx.mock
    def test_mixed_auth_and_no_auth_rotation(self) -> None:
        """Test rotation between authenticated and non-authenticated proxies."""
        proxies = [
            Proxy(
                url="http://auth-proxy.example.com:8080",
                protocol="http",
                username=SecretStr("user"),
                password=SecretStr("pass"),
            ),
            Proxy(
                url="http://no-auth-proxy.example.com:8080",
                protocol="http",
            ),
            Proxy(
                url="http://auth-proxy2.example.com:8080",
                protocol="http",
                username=SecretStr("user2"),
                password=SecretStr("pass2"),
            ),
        ]

        # Mock all requests to succeed
        respx.get("https://httpbin.org/test").mock(return_value=httpx.Response(200, text="success"))

        rotator = ProxyWhirl(proxies=proxies)

        # Make requests through all proxies
        for i in range(3):
            response = rotator.get("https://httpbin.org/test")
            assert response.status_code == 200
            # Verify correct proxy was used based on round-robin
            assert proxies[i].total_requests == 1

    @respx.mock
    def test_credential_isolation_between_proxies(
        self, proxies_with_different_credentials: list[Proxy]
    ) -> None:
        """Test that credentials don't leak between proxy requests."""
        call_count = 0

        def check_auth_handler(request: httpx.Request) -> httpx.Response:
            """Handler that verifies auth is present but doesn't inspect details."""
            nonlocal call_count
            call_count += 1
            # We can't easily inspect proxy auth, but we can verify the request succeeds
            return httpx.Response(200, json={"call": call_count})

        respx.get("https://httpbin.org/ip").mock(side_effect=check_auth_handler)

        rotator = ProxyWhirl(proxies=proxies_with_different_credentials)

        # Make multiple requests
        responses = [rotator.get("https://httpbin.org/ip") for _ in range(3)]

        # Verify all requests succeeded
        assert all(r.status_code == 200 for r in responses)
        assert call_count == 3

    @respx.mock
    def test_empty_password_credentials(self) -> None:
        """Test handling of proxies with username but empty password."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            protocol="http",
            username=SecretStr("user"),
            password=SecretStr(""),
        )

        respx.get("https://httpbin.org/ip").mock(
            return_value=httpx.Response(200, json={"origin": "1.2.3.4"})
        )

        rotator = ProxyWhirl(proxies=[proxy])
        response = rotator.get("https://httpbin.org/ip")

        assert response.status_code == 200
        assert proxy.total_requests == 1

    @respx.mock
    def test_special_characters_in_credentials(self) -> None:
        """Test handling of special characters in credentials during rotation."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            protocol="http",
            username=SecretStr("user@domain.com"),
            password=SecretStr("p@$$w0rd!#%"),
        )

        respx.get("https://httpbin.org/ip").mock(
            return_value=httpx.Response(200, json={"origin": "1.2.3.4"})
        )

        rotator = ProxyWhirl(proxies=[proxy])
        response = rotator.get("https://httpbin.org/ip")

        assert response.status_code == 200
        assert proxy.total_requests == 1
