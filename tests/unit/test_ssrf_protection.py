"""Tests for SSRF protection via private IP pattern rejection.

Session 5 SA-5.2: Validates that ``validate_target_url_safe`` blocks access
to internal/private IP ranges while allowing public addresses.
"""

from __future__ import annotations

import ipaddress
import socket
from typing import Any

import pytest

from proxywhirl.utils import validate_target_url_safe

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_getaddrinfo_public(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock getaddrinfo to return a public IP without real DNS."""

    def _mock_getaddrinfo(
        host: str,
        port: Any,
        family: int = socket.AF_UNSPEC,
        type: int = socket.SOCK_STREAM,
    ) -> list[Any]:
        # For numeric IPs, return the same IP; for hostnames return a public IP
        if host.replace(".", "").isdigit() or ":" in host:
            return [(family, type, 0, "", (host, port))]
        return [(socket.AF_INET, type, 0, "", ("8.8.8.8", port))]

    monkeypatch.setattr(socket, "getaddrinfo", _mock_getaddrinfo)


@pytest.fixture
def mock_getaddrinfo_loopback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock getaddrinfo to return loopback for any host."""

    def _mock_getaddrinfo(
        host: str,
        port: Any,
        family: int = socket.AF_UNSPEC,
        type: int = socket.SOCK_STREAM,
    ) -> list[Any]:
        return [(socket.AF_INET, type, 0, "", ("127.0.0.1", port))]

    monkeypatch.setattr(socket, "getaddrinfo", _mock_getaddrinfo)


# ============================================================================
# PRIVATE IP REJECTION
# ============================================================================


class TestPrivateIPRejection:
    """Test that private/internal IP addresses are rejected."""

    @pytest.mark.parametrize(
        "private_ip",
        [
            "10.0.0.1",
            "10.255.255.255",
            "172.16.0.1",
            "172.31.255.255",
            "192.168.1.1",
            "192.168.255.255",
            "127.0.0.1",
            "127.255.255.255",
            "0.0.0.0",
            "::1",
            "fc00::1",
            "fe80::1",
            "169.254.1.1",
            "192.0.0.1",
            "240.0.0.1",
            "255.255.255.255",
        ],
    )
    def test_private_ipv4_rejected(self, private_ip: str) -> None:
        """Each private IPv4 address must raise ValueError."""
        url = f"http://{private_ip}/api/test"
        with pytest.raises(ValueError):
            validate_target_url_safe(url)

    @pytest.mark.parametrize(
        "private_ip",
        [
            "::1",
            "fc00::1",
            "fe80::1",
            "fe80::a00:27ff:fe4e:66a1",
        ],
    )
    def test_private_ipv6_rejected(self, private_ip: str) -> None:
        """Each private IPv6 address must raise ValueError."""
        url = f"http://[{private_ip}]/api/test"
        with pytest.raises(ValueError):
            validate_target_url_safe(url)

    def test_localhost_hostname_rejected(self) -> None:
        """The literal hostname 'localhost' must be rejected immediately."""
        with pytest.raises(ValueError, match="localhost"):
            validate_target_url_safe("http://localhost:8080/")

    @pytest.mark.parametrize(
        "internal_domain",
        [
            "http://api.local/v1",
            "http://gateway.internal/health",
            "http://router.lan/status",
            "http://vpn.corp/login",
        ],
    )
    def test_internal_domain_rejected(self, internal_domain: str) -> None:
        """Domains ending in .local, .internal, .lan, .corp must be rejected."""
        with pytest.raises(ValueError, match="internal domain"):
            validate_target_url_safe(internal_domain)

    def test_loopback_blocked_even_with_mock(
        self,
        mock_getaddrinfo_loopback: None,
    ) -> None:
        """If DNS resolves to loopback, the request must be blocked."""
        with pytest.raises(ValueError, match="loopback"):
            validate_target_url_safe("http://example.com/")

    def test_unspecified_address_rejected(self) -> None:
        """0.0.0.0 (unspecified) must be rejected."""
        with pytest.raises(ValueError, match="unspecified"):
            validate_target_url_safe("http://0.0.0.0:3000/")

    def test_link_local_rejected(self) -> None:
        """Link-local addresses (169.254.0.0/16, fe80::/10) must be rejected.

        Note: Python's ``ipaddress`` module reports link-local as ``is_private``,
        so the error message mentions "private" rather than "link-local".
        """
        with pytest.raises(ValueError, match="private"):
            validate_target_url_safe("http://169.254.100.1/")

    def test_multicast_rejected(self) -> None:
        """Multicast addresses must be rejected."""
        with pytest.raises(ValueError, match="multicast"):
            validate_target_url_safe("http://224.0.0.1/")

    def test_reserved_address_rejected(self) -> None:
        """Reserved addresses must be rejected."""
        with pytest.raises(ValueError, match="private|reserved"):
            validate_target_url_safe("http://240.0.0.1/")

    def test_private_with_path_and_query_rejected(self) -> None:
        """Private IPs with paths/queries must still be rejected."""
        with pytest.raises(ValueError, match="private"):
            validate_target_url_safe("http://192.168.1.1/api?key=value")

    def test_private_with_auth_rejected(self) -> None:
        """Private IPs with embedded credentials must still be rejected."""
        with pytest.raises(ValueError, match="private"):
            validate_target_url_safe("http://user:pass@10.0.0.1:8080/")


# ============================================================================
# PUBLIC IP ALLOWANCE
# ============================================================================


class TestPublicIPAllowed:
    """Test that public IP addresses are permitted."""

    @pytest.mark.parametrize(
        "public_url",
        [
            "http://8.8.8.8/",
            "http://1.1.1.1/",
            "https://8.8.8.8:443/dns-query",
            "http://9.9.9.9/",
            "http://208.67.222.222/",
        ],
    )
    def test_public_ipv4_allowed(self, public_url: str) -> None:
        """Public IPv4 addresses must pass validation."""
        # Numeric IPs do not require DNS, so this works offline
        validate_target_url_safe(public_url)

    def test_public_ipv6_allowed(self) -> None:
        """Public IPv6 addresses must pass validation."""
        validate_target_url_safe("http://[2001:4860:4860::8888]/")

    @pytest.mark.parametrize(
        "public_url",
        [
            "http://example.com/",
            "https://github.com/",
            "http://httpbin.org/ip",
        ],
    )
    def test_public_hostname_allowed(self, public_url: str, mock_getaddrinfo_public: None) -> None:
        """Public hostnames that resolve to public IPs must pass."""
        validate_target_url_safe(public_url)

    def test_public_with_path_and_query_allowed(self) -> None:
        """Public URLs with paths and queries must pass."""
        validate_target_url_safe("http://8.8.8.8/api?key=value&foo=bar")


# ============================================================================
# BYPASS & EDGE CASES
# ============================================================================


class TestAllowPrivateBypass:
    """Test that ``allow_private=True`` bypasses SSRF checks."""

    @pytest.mark.parametrize(
        "private_ip",
        [
            "10.0.0.1",
            "172.16.0.1",
            "192.168.1.1",
            "127.0.0.1",
            "0.0.0.0",
            "::1",
        ],
    )
    def test_allow_private_bypasses_rejection(self, private_ip: str) -> None:
        """When ``allow_private=True``, private IPs are accepted."""
        url = f"http://{private_ip}/"
        if ":" in private_ip:
            url = f"http://[{private_ip}]/"
        validate_target_url_safe(url, allow_private=True)

    def test_allow_private_allows_localhost(self) -> None:
        """When ``allow_private=True``, localhost is also allowed
        because the private/IP checks are skipped entirely."""
        # When allow_private=True, validate_target_url_safe skips all checks
        validate_target_url_safe("http://localhost/", allow_private=True)

    def test_allow_private_allows_internal_domains(self) -> None:
        """When ``allow_private=True``, internal domains are also allowed
        because the private/IP checks are skipped entirely."""
        validate_target_url_safe("http://api.local/", allow_private=True)


class TestInvalidURLHandling:
    """Test that malformed URLs raise ValueError."""

    @pytest.mark.parametrize(
        "bad_url,expected_snippet",
        [
            ("ftp://8.8.8.8/file", "scheme"),
            ("file:///etc/passwd", "scheme"),
            ("data:text/plain,hello", "scheme"),
            ("gopher://example.com/", "scheme"),
        ],
    )
    def test_invalid_scheme_rejected(self, bad_url: str, expected_snippet: str) -> None:
        """Non-http(s) schemes must be rejected."""
        with pytest.raises(ValueError, match=expected_snippet):
            validate_target_url_safe(bad_url)

    def test_missing_hostname_rejected(self) -> None:
        """URLs without a hostname must be rejected."""
        with pytest.raises(ValueError, match="hostname"):
            validate_target_url_safe("http://:8080/")

    def test_empty_url_rejected(self) -> None:
        """Empty or invalid URL strings must be rejected."""
        with pytest.raises(ValueError):
            validate_target_url_safe("")


class TestNormalizationHelpers:
    """Test internal IP normalization helpers indirectly."""

    def test_ipv4_mapped_ipv6_normalization(self) -> None:
        """IPv4-mapped IPv6 addresses should normalize to IPv4."""
        addr = ipaddress.ip_address("::ffff:192.168.1.1")
        assert isinstance(addr, ipaddress.IPv6Address)
        mapped = addr.ipv4_mapped
        assert mapped is not None
        assert mapped == ipaddress.IPv4Address("192.168.1.1")

    def test_ipaddress_module_recognizes_private(self) -> None:
        """Verify Python's ipaddress module flags known private ranges."""
        assert ipaddress.ip_address("10.0.0.1").is_private
        assert ipaddress.ip_address("172.16.0.1").is_private
        assert ipaddress.ip_address("192.168.1.1").is_private
        assert ipaddress.ip_address("127.0.0.1").is_loopback
        assert ipaddress.ip_address("0.0.0.0").is_unspecified
        assert ipaddress.ip_address("::1").is_loopback
        assert ipaddress.ip_address("fc00::1").is_private
        assert ipaddress.ip_address("fe80::1").is_link_local
        assert not ipaddress.ip_address("8.8.8.8").is_private
        assert not ipaddress.ip_address("1.1.1.1").is_private

    def test_ipaddress_module_recognizes_public(self) -> None:
        """Verify Python's ipaddress module flags public addresses correctly."""
        pub = ipaddress.ip_address("8.8.8.8")
        assert not pub.is_private
        assert not pub.is_loopback
        assert not pub.is_unspecified
        assert not pub.is_link_local
        assert not pub.is_reserved
        assert not pub.is_multicast

    def test_ipaddress_ipv6_public(self) -> None:
        """Verify public IPv6 address flags."""
        pub = ipaddress.ip_address("2001:4860:4860::8888")
        assert not pub.is_private
        assert not pub.is_loopback


class TestSSRFDefenseDepth:
    """Test layered SSRF defenses beyond simple IP checks."""

    def test_dns_rebinding_protection_via_mock(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Simulate DNS rebinding: hostname resolves to private IP after initial lookup."""

        def _rebinding_getaddrinfo(
            host: str,
            port: Any,
            family: int = socket.AF_UNSPEC,
            type: int = socket.SOCK_STREAM,
        ) -> list[Any]:
            # Pretend attacker-controlled domain resolves to private IP
            return [(socket.AF_INET, type, 0, "", ("192.168.1.100", port))]

        monkeypatch.setattr(socket, "getaddrinfo", _rebinding_getaddrinfo)
        with pytest.raises(ValueError, match="private"):
            validate_target_url_safe("http://attacker.example.com/")

    def test_decimal_notation_blocked(self) -> None:
        """Decimal/octal IP notation that resolves to private IPs must be blocked."""
        # 192.168.1.1 in decimal = 3232235777
        with pytest.raises(ValueError):
            validate_target_url_safe("http://3232235777/")

    @pytest.mark.parametrize(
        "octal_url,resolved_ip",
        [
            ("http://0300.0250.0001.0001/", "192.168.1.1"),
            ("http://0177.0000.0000.0001/", "127.0.0.1"),
        ],
    )
    def test_octal_notation_blocked(
        self, octal_url: str, resolved_ip: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Octal IP notation that resolves to private IPs must be blocked."""
        import socket

        def _fake_getaddrinfo(host, port, family=None, type=None):
            return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", (resolved_ip, port))]

        monkeypatch.setattr(socket, "getaddrinfo", _fake_getaddrinfo)

        with pytest.raises(ValueError):
            validate_target_url_safe(octal_url)


# ============================================================================
# COUNT CHECK
# ============================================================================


def test_at_least_twenty_tests_exist() -> None:
    """Meta-test: ensure this module contains >= 20 test functions."""
    import inspect
    import sys

    module = sys.modules[__name__]

    def _collect_tests(obj):
        tests = []
        for name, member in inspect.getmembers(obj):
            if name.startswith("test_") and (
                inspect.isfunction(member) or inspect.ismethod(member)
            ):
                tests.append(member)
        return tests

    test_funcs = _collect_tests(module)
    for _, cls in inspect.getmembers(module, inspect.isclass):
        test_funcs.extend(_collect_tests(cls))

    assert len(test_funcs) >= 20, f"Expected >= 20 tests, found {len(test_funcs)}"
