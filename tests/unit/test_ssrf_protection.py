"""Tests for SSRF protection and validation."""

from __future__ import annotations

import ipaddress
from typing import Any

import pytest


class SSRFBlocklist:
    """SSRF protection with blocklist."""

    DEFAULT_BLOCKED = {
        "127.0.0.1",
        "localhost",
        "0.0.0.0",
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16",
        "169.254.0.0/16",
        "::1",
        "::",
        "fc00::/7",
    }

    def __init__(self, extra_blocked: set[str] | None = None) -> None:
        """Initialize SSRF blocklist."""
        self.blocked = self.DEFAULT_BLOCKED.copy()
        if extra_blocked:
            self.blocked.update(extra_blocked)

    def is_blocked(self, host: str) -> bool:
        """Check if host is blocked."""
        if host in self.blocked:
            return True
        
        try:
            ip = ipaddress.ip_address(host)
            for block in self.blocked:
                try:
                    network = ipaddress.ip_network(block, strict=False)
                    if ip in network:
                        return True
                except ValueError:
                    pass
        except ValueError:
            # Not an IP address
            if host.lower() in self.blocked:
                return True
        
        return False

    def add_blocked(self, host: str) -> None:
        """Add host to blocklist."""
        self.blocked.add(host)

    def remove_blocked(self, host: str) -> None:
        """Remove host from blocklist."""
        self.blocked.discard(host)


class TestSSRFProtection:
    """Test SSRF protection."""

    @pytest.fixture
    def blocklist(self) -> SSRFBlocklist:
        """Provide blocklist."""
        return SSRFBlocklist()

    def test_localhost_blocked(self, blocklist) -> None:
        """Test localhost is blocked."""
        assert blocklist.is_blocked("localhost")
        assert blocklist.is_blocked("127.0.0.1")

    def test_loopback_blocked(self, blocklist) -> None:
        """Test loopback is blocked."""
        assert blocklist.is_blocked("127.0.0.1")
        assert blocklist.is_blocked("127.0.0.2")

    def test_private_ip_blocked(self, blocklist) -> None:
        """Test private IPs are blocked."""
        assert blocklist.is_blocked("192.168.1.1")
        assert blocklist.is_blocked("10.0.0.1")
        assert blocklist.is_blocked("172.16.0.1")

    def test_link_local_blocked(self, blocklist) -> None:
        """Test link-local addresses are blocked."""
        assert blocklist.is_blocked("169.254.1.1")

    def test_public_ip_allowed(self, blocklist) -> None:
        """Test public IPs are allowed."""
        assert not blocklist.is_blocked("8.8.8.8")
        assert not blocklist.is_blocked("1.1.1.1")

    def test_ipv6_loopback_blocked(self, blocklist) -> None:
        """Test IPv6 loopback is blocked."""
        assert blocklist.is_blocked("::1")

    def test_ipv6_private_blocked(self, blocklist) -> None:
        """Test IPv6 private is blocked."""
        assert blocklist.is_blocked("fc00::1")
        assert blocklist.is_blocked("fd00::1")

    def test_add_blocked_host(self, blocklist) -> None:
        """Test adding to blocklist."""
        blocklist.add_blocked("evil.com")
        assert blocklist.is_blocked("evil.com")

    def test_remove_blocked_host(self, blocklist) -> None:
        """Test removing from blocklist."""
        blocklist.add_blocked("test.com")
        assert blocklist.is_blocked("test.com")
        blocklist.remove_blocked("test.com")
        assert not blocklist.is_blocked("test.com")

    def test_case_insensitive_hostname(self, blocklist) -> None:
        """Test hostname matching is case-insensitive."""
        blocklist.add_blocked("example.com")
        assert blocklist.is_blocked("EXAMPLE.COM")
        assert blocklist.is_blocked("Example.Com")

    def test_custom_blocked_list(self) -> None:
        """Test custom blocked list."""
        extra = {"malicious.com", "blocked.org"}
        blocklist = SSRFBlocklist(extra_blocked=extra)
        
        assert blocklist.is_blocked("malicious.com")
        assert blocklist.is_blocked("blocked.org")

    def test_zero_address_blocked(self, blocklist) -> None:
        """Test 0.0.0.0 is blocked."""
        assert blocklist.is_blocked("0.0.0.0")

    def test_metadata_service_not_blocked_by_name(self, blocklist) -> None:
        """Test metadata service hostname not in default blocklist."""
        # 169.254.169.254 would be blocked as link-local
        assert not blocklist.is_blocked("metadata.service")

    def test_metadata_service_ip_blocked(self, blocklist) -> None:
        """Test AWS metadata service IP is blocked."""
        # This is 169.254.x.x which is link-local
        assert blocklist.is_blocked("169.254.169.254")

    def test_empty_host(self, blocklist) -> None:
        """Test empty host."""
        assert not blocklist.is_blocked("")

    def test_valid_proxy_url_domains(self, blocklist) -> None:
        """Test valid proxy domains are not blocked."""
        valid_domains = [
            "proxy1.example.com",
            "vpn-server.org",
            "squid.proxy.net",
        ]
        for domain in valid_domains:
            assert not blocklist.is_blocked(domain)

    def test_ipv4_subnet_blocking(self, blocklist) -> None:
        """Test IPv4 subnet blocking."""
        # 10.0.0.0/8 should block all 10.x.x.x
        assert blocklist.is_blocked("10.0.0.0")
        assert blocklist.is_blocked("10.255.255.255")
        assert blocklist.is_blocked("10.123.45.67")

    def test_ipv6_subnet_blocking(self, blocklist) -> None:
        """Test IPv6 subnet blocking."""
        # fc00::/7 should block fc00 and fd00
        assert blocklist.is_blocked("fc00::1")
        assert blocklist.is_blocked("fd00::1")
