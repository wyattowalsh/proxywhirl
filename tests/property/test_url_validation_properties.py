"""Property-based tests for Proxy URL validation using Hypothesis."""

import ipaddress
from typing import Any

import pytest
from hypothesis import assume, example, given
from hypothesis import strategies as st
from pydantic import ValidationError

from proxywhirl.models import Proxy

# ============================================================================
# STRATEGIES
# ============================================================================


@st.composite
def valid_schemes(draw: Any) -> str:
    """Generate valid proxy schemes."""
    return draw(st.sampled_from(["http", "https", "socks4", "socks5"]))


@st.composite
def invalid_schemes(draw: Any) -> str:
    """Generate invalid proxy schemes."""
    # Common invalid schemes
    common_invalid = ["ftp", "ssh", "telnet", "smtp", "pop3", "imap", "ws", "wss"]
    # Random invalid schemes
    random_invalid = st.text(
        alphabet=st.characters(whitelist_categories=("Ll",), max_codepoint=127),
        min_size=2,
        max_size=10,
    ).filter(lambda x: x not in {"http", "https", "socks4", "socks5"})

    return draw(st.one_of(st.sampled_from(common_invalid), random_invalid))


@st.composite
def valid_ports(draw: Any) -> int:
    """Generate valid port numbers (1-65535)."""
    return draw(st.integers(min_value=1, max_value=65535))


@st.composite
def invalid_ports(draw: Any) -> int:
    """Generate invalid port numbers."""
    return draw(
        st.one_of(
            st.integers(max_value=0),  # Zero or negative
            st.integers(min_value=65536, max_value=99999),  # Above max
        )
    )


@st.composite
def public_hostnames(draw: Any) -> str:
    """Generate valid public hostnames."""
    # Simple domain names
    label = st.text(
        alphabet=st.characters(whitelist_categories=("Ll", "Nd"), blacklist_characters="-"),
        min_size=1,
        max_size=20,
    ).filter(lambda x: x[0].isalpha() if x else False)

    parts = draw(st.lists(label, min_size=2, max_size=4))
    return ".".join(parts)


@st.composite
def localhost_addresses(draw: Any) -> str:
    """Generate localhost/loopback addresses."""
    return draw(
        st.sampled_from(
            [
                "localhost",
                "127.0.0.1",
                "127.0.0.2",
                "127.1.1.1",
                "[::1]",  # IPv6 localhost must use brackets in URLs
            ]
        )
    )


@st.composite
def private_ipv4_addresses(draw: Any) -> str:
    """Generate private IPv4 addresses."""
    range_choice = draw(st.integers(min_value=0, max_value=2))

    if range_choice == 0:
        # 10.0.0.0/8
        return f"10.{draw(st.integers(0, 255))}.{draw(st.integers(0, 255))}.{draw(st.integers(0, 255))}"
    elif range_choice == 1:
        # 172.16.0.0/12
        return f"172.{draw(st.integers(16, 31))}.{draw(st.integers(0, 255))}.{draw(st.integers(0, 255))}"
    else:
        # 192.168.0.0/16
        return f"192.168.{draw(st.integers(0, 255))}.{draw(st.integers(0, 255))}"


@st.composite
def public_ipv4_addresses(draw: Any) -> str:
    """Generate public IPv4 addresses (avoiding private ranges)."""
    # Generate random IPv4, then check if it's public
    while True:
        octets = [draw(st.integers(1, 254)) for _ in range(4)]
        ip_str = ".".join(str(o) for o in octets)

        try:
            ip = ipaddress.ip_address(ip_str)
            # Accept only if it's a global/public IP
            if not (
                ip.is_private
                or ip.is_loopback
                or ip.is_reserved
                or ip.is_link_local
                or ip.is_multicast
            ):
                return ip_str
        except ValueError:
            continue

        # Prevent infinite loop - after 100 tries, use a known public IP
        if draw(st.integers(0, 100)) == 0:
            return draw(st.sampled_from(["8.8.8.8", "1.1.1.1", "208.67.222.222"]))


# ============================================================================
# PROPERTY TESTS - SCHEME VALIDATION
# ============================================================================


class TestSchemeValidationProperties:
    """Property-based tests for proxy scheme validation."""

    @given(valid_schemes(), public_hostnames(), valid_ports())
    def test_valid_schemes_always_accepted(self, scheme: str, host: str, port: int):
        """Property: All valid schemes should be accepted."""
        url = f"{scheme}://{host}:{port}"
        proxy = Proxy(url=url)
        assert proxy.protocol == scheme

    @given(invalid_schemes(), public_hostnames(), valid_ports())
    def test_invalid_schemes_always_rejected(self, scheme: str, host: str, port: int):
        """Property: All invalid schemes should be rejected."""
        assume(scheme not in {"http", "https", "socks4", "socks5"})  # Ensure truly invalid

        url = f"{scheme}://{host}:{port}"
        with pytest.raises(ValidationError, match="Invalid proxy scheme"):
            Proxy(url=url)

    @given(public_hostnames(), valid_ports())
    def test_missing_scheme_rejected(self, host: str, port: int):
        """Property: URLs without schemes should always be rejected."""
        url = f"{host}:{port}"
        with pytest.raises(ValidationError, match="URL must have a scheme"):
            Proxy(url=url)

    @given(st.sampled_from(["HTTP", "HtTp", "HTTPS", "HtTpS", "SOCKS4", "SOCKS5", "SoCkS5"]))
    @example(scheme="HTTP")
    @example(scheme="HtTp")
    @example(scheme="SOCKS5")
    def test_scheme_case_insensitive(self, scheme: str):
        """Property: Scheme validation should be case-insensitive."""
        url = f"{scheme}://proxy.example.com:8080"
        proxy = Proxy(url=url)
        assert proxy.protocol in {"http", "https", "socks4", "socks5"}


# ============================================================================
# PROPERTY TESTS - PORT VALIDATION
# ============================================================================


class TestPortValidationProperties:
    """Property-based tests for port range validation."""

    @given(valid_schemes(), public_hostnames(), valid_ports())
    def test_valid_ports_always_accepted(self, scheme: str, host: str, port: int):
        """Property: All ports in range 1-65535 should be accepted."""
        url = f"{scheme}://{host}:{port}"
        proxy = Proxy(url=url)
        assert proxy.url is not None

    @given(valid_schemes(), public_hostnames(), invalid_ports())
    def test_invalid_ports_always_rejected(self, scheme: str, host: str, port: int):
        """Property: All ports outside range 1-65535 should be rejected."""
        assume(port < 1 or port > 65535)

        url = f"{scheme}://{host}:{port}"
        with pytest.raises(ValidationError, match="Port must be between 1 and 65535"):
            Proxy(url=url)

    @given(valid_schemes(), public_hostnames())
    @example(scheme="http", host="example.com")
    def test_port_1_is_valid(self, scheme: str, host: str):
        """Property: Port 1 (minimum) should always be valid."""
        url = f"{scheme}://{host}:1"
        proxy = Proxy(url=url)
        assert proxy.url is not None

    @given(valid_schemes(), public_hostnames())
    @example(scheme="http", host="example.com")
    def test_port_65535_is_valid(self, scheme: str, host: str):
        """Property: Port 65535 (maximum) should always be valid."""
        url = f"{scheme}://{host}:65535"
        proxy = Proxy(url=url)
        assert proxy.url is not None

    @given(valid_schemes(), public_hostnames())
    @example(scheme="http", host="example.com")
    def test_port_0_is_invalid(self, scheme: str, host: str):
        """Property: Port 0 should always be invalid."""
        url = f"{scheme}://{host}:0"
        with pytest.raises(ValidationError, match="Port must be between 1 and 65535"):
            Proxy(url=url)

    @given(valid_schemes(), public_hostnames(), st.integers(min_value=65536, max_value=99999))
    def test_port_above_65535_is_invalid(self, scheme: str, host: str, port: int):
        """Property: Ports above 65535 should always be invalid."""
        url = f"{scheme}://{host}:{port}"
        with pytest.raises(ValidationError, match="Port must be between 1 and 65535"):
            Proxy(url=url)


# ============================================================================
# PROPERTY TESTS - LOCAL ADDRESS VALIDATION
# ============================================================================


class TestLocalAddressValidationProperties:
    """Property-based tests for localhost/private IP validation."""

    @given(valid_schemes(), localhost_addresses(), valid_ports())
    def test_localhost_rejected_by_default(self, scheme: str, host: str, port: int):
        """Property: All localhost addresses should be rejected by default."""
        url = f"{scheme}://{host}:{port}"
        with pytest.raises(ValidationError, match="Localhost addresses not allowed"):
            Proxy(url=url)

    @given(valid_schemes(), localhost_addresses(), valid_ports())
    def test_localhost_accepted_with_flag(self, scheme: str, host: str, port: int):
        """Property: All localhost addresses should be accepted with allow_local=True."""
        url = f"{scheme}://{host}:{port}"
        proxy = Proxy(url=url, allow_local=True)
        assert proxy.url is not None

    @given(valid_schemes(), private_ipv4_addresses(), valid_ports())
    def test_private_ips_rejected_by_default(self, scheme: str, host: str, port: int):
        """Property: All private IPv4 addresses should be rejected by default."""
        url = f"{scheme}://{host}:{port}"
        with pytest.raises(ValidationError, match="Private/internal IP addresses not allowed"):
            Proxy(url=url)

    @given(valid_schemes(), private_ipv4_addresses(), valid_ports())
    def test_private_ips_accepted_with_flag(self, scheme: str, host: str, port: int):
        """Property: All private IPv4 addresses should be accepted with allow_local=True."""
        url = f"{scheme}://{host}:{port}"
        proxy = Proxy(url=url, allow_local=True)
        assert proxy.url is not None

    @given(valid_schemes(), public_ipv4_addresses(), valid_ports())
    def test_public_ips_always_accepted(self, scheme: str, host: str, port: int):
        """Property: All public IPv4 addresses should always be accepted."""
        url = f"{scheme}://{host}:{port}"
        proxy = Proxy(url=url)
        assert proxy.url is not None

    @given(valid_schemes(), public_hostnames(), valid_ports())
    def test_public_hostnames_always_accepted(self, scheme: str, host: str, port: int):
        """Property: All public hostnames should always be accepted."""
        assume(not host.startswith("localhost"))  # Avoid accidental localhost matches

        url = f"{scheme}://{host}:{port}"
        proxy = Proxy(url=url)
        assert proxy.url is not None


# ============================================================================
# PROPERTY TESTS - URL FORMAT VARIATIONS
# ============================================================================


class TestURLFormatVariations:
    """Property-based tests for various URL format edge cases."""

    @given(
        valid_schemes(),
        public_hostnames(),
        valid_ports(),
        st.text(alphabet=st.characters(whitelist_categories=("Ll", "Nd")), min_size=1, max_size=10),
        st.text(alphabet=st.characters(whitelist_categories=("Ll", "Nd")), min_size=1, max_size=10),
    )
    def test_url_with_credentials_in_string(
        self, scheme: str, host: str, port: int, username: str, password: str
    ):
        """Property: URLs with embedded credentials should validate correctly."""
        url = f"{scheme}://{username}:{password}@{host}:{port}"
        # Should validate without error (credentials in URL string are allowed)
        proxy = Proxy(url=url)
        assert proxy.url is not None

    @given(valid_schemes(), public_hostnames(), valid_ports())
    def test_url_with_trailing_slash(self, scheme: str, host: str, port: int):
        """Property: URLs with trailing slashes should validate correctly."""
        url = f"{scheme}://{host}:{port}/"
        proxy = Proxy(url=url)
        assert proxy.url is not None

    @given(valid_schemes(), public_hostnames(), valid_ports())
    def test_url_with_path(self, scheme: str, host: str, port: int):
        """Property: URLs with paths should validate correctly."""
        url = f"{scheme}://{host}:{port}/some/path"
        proxy = Proxy(url=url)
        assert proxy.url is not None

    @given(valid_schemes(), public_ipv4_addresses(), valid_ports())
    def test_ipv4_addresses_validate(self, scheme: str, ip: str, port: int):
        """Property: IPv4 addresses should validate correctly."""
        url = f"{scheme}://{ip}:{port}"
        proxy = Proxy(url=url)
        assert proxy.url is not None


# ============================================================================
# PROPERTY TESTS - EDGE CASES
# ============================================================================


class TestEdgeCases:
    """Property-based tests for edge cases and boundary conditions."""

    @given(valid_schemes())
    def test_common_proxy_ports(self, scheme: str):
        """Property: Common proxy ports should all be valid."""
        common_ports = [80, 443, 1080, 3128, 8080, 8888, 9050]
        for port in common_ports:
            url = f"{scheme}://proxy.example.com:{port}"
            proxy = Proxy(url=url)
            assert proxy.url is not None

    @given(valid_schemes(), public_hostnames())
    def test_urls_without_explicit_port_skip_port_validation(self, scheme: str, host: str):
        """Property: URLs without explicit ports should not trigger port validation."""
        url = f"{scheme}://{host}"
        # This should work - no port specified means no port validation
        proxy = Proxy(url=url)
        assert proxy.url is not None

    @given(st.integers(min_value=1, max_value=100))
    def test_allow_local_flag_default_false(self, _: int):
        """Property: allow_local should default to False."""
        proxy = Proxy(url="http://example.com:8080")
        assert proxy.allow_local is False

    @given(st.booleans())
    def test_allow_local_flag_can_be_set(self, allow_local: bool):
        """Property: allow_local flag should be settable to any boolean value."""
        proxy = Proxy(url="http://example.com:8080", allow_local=allow_local)
        assert proxy.allow_local == allow_local
