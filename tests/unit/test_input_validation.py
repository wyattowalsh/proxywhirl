"""Fuzz-style tests for API input validation.

Session 5 SA-5.2: Validates edge cases such as empty strings, ``None``,
very long strings, and special characters across API request models.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from pydantic import BaseModel, ValidationError

from proxywhirl.api.models import (
    ConfigurationSettings,
    CreateProxyRequest,
    ProxiedRequest,
    UpdateConfigRequest,
)
from proxywhirl.validators import (
    is_non_negative,
    is_positive,
    is_success_rate,
    is_valid_host,
    is_valid_port,
    is_valid_proxy_url,
)


# ============================================================================
# PROXIED REQUEST EDGE CASES
# ============================================================================


class TestProxiedRequestValidation:
    """Edge-case fuzzing for ``ProxiedRequest``."""

    def test_valid_request(self) -> None:
        """Baseline: a well-formed request should instantiate."""
        req = ProxiedRequest(url="https://example.com/path")
        assert str(req.url) == "https://example.com/path"
        assert req.method == "GET"

    def test_empty_url_rejected(self) -> None:
        """Empty URL string must be rejected."""
        with pytest.raises(ValidationError):
            ProxiedRequest(url="")

    def test_none_url_rejected(self) -> None:
        """``None`` as URL must be rejected."""
        with pytest.raises(ValidationError):
            ProxiedRequest(url=None)  # type: ignore[arg-type]

    def test_very_long_url_rejected(self) -> None:
        """URL longer than 2048 characters must be rejected."""
        long_url = "https://example.com/" + "a" * 2048
        with pytest.raises(ValidationError):
            ProxiedRequest(url=long_url)

    @pytest.mark.parametrize(
        "bad_scheme",
        [
            "ftp://example.com",
            "file:///etc/passwd",
            "data:text/plain,hello",
            "javascript:alert(1)",
        ],
    )
    def test_invalid_scheme_rejected(self, bad_scheme: str) -> None:
        """Non-http(s) schemes must be rejected."""
        with pytest.raises(ValidationError):
            ProxiedRequest(url=bad_scheme)

    def test_special_characters_in_path(self) -> None:
        """Special characters in a valid URL path should be accepted."""
        req = ProxiedRequest(url="https://example.com/api/v1/test%20space")
        assert "test%20space" in str(req.url)

    @pytest.mark.parametrize(
        "method",
        ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
    )
    def test_valid_methods(self, method: str) -> None:
        """All allowed HTTP methods should instantiate."""
        req = ProxiedRequest(url="https://example.com", method=method)  # type: ignore[arg-type]
        assert req.method == method

    def test_invalid_method_rejected(self) -> None:
        """An unsupported HTTP method must be rejected."""
        with pytest.raises(ValidationError):
            ProxiedRequest(url="https://example.com", method="TRACE")  # type: ignore[arg-type]

    def test_none_method_rejected(self) -> None:
        """``None`` as method must be rejected."""
        with pytest.raises(ValidationError):
            ProxiedRequest(url="https://example.com", method=None)  # type: ignore[arg-type]

    def test_timeout_at_boundary(self) -> None:
        """Timeout equal to the upper boundary (300) should be accepted."""
        req = ProxiedRequest(url="https://example.com", timeout=300)
        assert req.timeout == 300

    def test_timeout_over_boundary_rejected(self) -> None:
        """Timeout above 300 must be rejected."""
        with pytest.raises(ValidationError):
            ProxiedRequest(url="https://example.com", timeout=301)

    def test_timeout_zero_rejected(self) -> None:
        """Zero timeout must be rejected ( PositiveInt )."""
        with pytest.raises(ValidationError):
            ProxiedRequest(url="https://example.com", timeout=0)

    def test_timeout_none_rejected(self) -> None:
        """``None`` as timeout must be rejected."""
        with pytest.raises(ValidationError):
            ProxiedRequest(url="https://example.com", timeout=None)  # type: ignore[arg-type]

    def test_very_long_header_name_rejected(self) -> None:
        """Header name longer than 256 chars must be rejected."""
        headers = {"x" * 257: "value"}
        with pytest.raises(ValidationError):
            ProxiedRequest(url="https://example.com", headers=headers)

    def test_very_long_header_value_rejected(self) -> None:
        """Header value longer than 2048 chars must be rejected."""
        headers = {"X-Custom": "v" * 2049}
        with pytest.raises(ValidationError):
            ProxiedRequest(url="https://example.com", headers=headers)

    def test_empty_headers_accepted(self) -> None:
        """Empty headers dict should be accepted."""
        req = ProxiedRequest(url="https://example.com", headers={})
        assert req.headers == {}

    def test_body_at_1mb_boundary(self) -> None:
        """Body exactly at 1 MB should be accepted."""
        body = "x" * 1048576
        req = ProxiedRequest(url="https://example.com", body=body)
        assert len(req.body) == 1048576

    def test_body_over_1mb_rejected(self) -> None:
        """Body over 1 MB must be rejected."""
        body = "x" * 1048577
        with pytest.raises(ValidationError):
            ProxiedRequest(url="https://example.com", body=body)

    def test_none_body_accepted(self) -> None:
        """``None`` body should be accepted (optional field)."""
        req = ProxiedRequest(url="https://example.com", body=None)
        assert req.body is None

    def test_special_chars_in_body(self) -> None:
        """Body with special Unicode characters should be accepted."""
        body = "Hello 🌍 \n\t \\ \" ' <script>alert(1)</script>"
        req = ProxiedRequest(url="https://example.com", body=body)
        assert req.body == body


# ============================================================================
# CREATE PROXY REQUEST EDGE CASES
# ============================================================================


class TestCreateProxyRequestValidation:
    """Edge-case fuzzing for ``CreateProxyRequest``."""

    def test_valid_proxy_request(self) -> None:
        """Baseline: a well-formed proxy creation request."""
        req = CreateProxyRequest(url="http://proxy.example.com:8080")
        assert req.url == "http://proxy.example.com:8080"

    def test_empty_url_rejected(self) -> None:
        """Empty URL must be rejected."""
        with pytest.raises(ValidationError):
            CreateProxyRequest(url="")

    def test_none_url_rejected(self) -> None:
        """``None`` as URL must be rejected."""
        with pytest.raises(ValidationError):
            CreateProxyRequest(url=None)  # type: ignore[arg-type]

    def test_very_long_proxy_url_rejected(self) -> None:
        """Proxy URL longer than 2048 chars must be rejected."""
        url = "http://proxy.example.com:8080/" + "a" * 2048
        with pytest.raises(ValidationError):
            CreateProxyRequest(url=url)

    def test_missing_scheme_rejected(self) -> None:
        """Proxy URL without scheme must be rejected."""
        with pytest.raises(ValidationError):
            CreateProxyRequest(url="proxy.example.com:8080")

    def test_invalid_scheme_rejected(self) -> None:
        """Proxy URL with non-proxy scheme must be rejected."""
        with pytest.raises(ValidationError):
            CreateProxyRequest(url="ftp://proxy.example.com:8080")

    def test_missing_port_rejected(self) -> None:
        """Proxy URL without port must be rejected."""
        with pytest.raises(ValidationError):
            CreateProxyRequest(url="http://proxy.example.com")

    def test_port_out_of_range_rejected(self) -> None:
        """Proxy URL with port outside 1-65535 must be rejected."""
        with pytest.raises(ValidationError):
            CreateProxyRequest(url="http://proxy.example.com:99999")

    def test_port_zero_rejected(self) -> None:
        """Proxy URL with port 0 must be rejected."""
        with pytest.raises(ValidationError):
            CreateProxyRequest(url="http://proxy.example.com:0")

    def test_very_long_hostname_rejected(self) -> None:
        """Hostname longer than 256 chars must be rejected."""
        host = "a" * 257 + ".com"
        with pytest.raises(ValidationError):
            CreateProxyRequest(url=f"http://{host}:8080")

    def test_username_at_boundary(self) -> None:
        """Username exactly at 256 chars should be accepted."""
        user = "u" * 256
        req = CreateProxyRequest(url="http://proxy.example.com:8080", username=user)
        assert req.username == user

    def test_username_over_boundary_rejected(self) -> None:
        """Username over 256 chars must be rejected."""
        with pytest.raises(ValidationError):
            CreateProxyRequest(
                url="http://proxy.example.com:8080",
                username="u" * 257,
            )

    def test_none_username_accepted(self) -> None:
        """``None`` username should be accepted (optional)."""
        req = CreateProxyRequest(url="http://proxy.example.com:8080", username=None)
        assert req.username is None

    def test_special_chars_in_url_accepted(self) -> None:
        """Proxy URL with path/query is accepted (validator only checks scheme, host, port)."""
        req = CreateProxyRequest(url="http://proxy.example.com:8080/path?query=1")
        assert req.url == "http://proxy.example.com:8080/path?query=1"


# ============================================================================
# UPDATE CONFIG REQUEST EDGE CASES
# ============================================================================


class TestUpdateConfigRequestValidation:
    """Edge-case fuzzing for ``UpdateConfigRequest``."""

    def test_all_none_accepted(self) -> None:
        """A fully-empty update request (all fields None) should instantiate."""
        req = UpdateConfigRequest()
        assert req.rotation_strategy is None
        assert req.timeout is None

    def test_valid_rotation_strategy(self) -> None:
        """A known rotation strategy should be accepted."""
        req = UpdateConfigRequest(rotation_strategy="round-robin")
        assert req.rotation_strategy == "round-robin"

    def test_invalid_rotation_strategy_rejected(self) -> None:
        """An unknown rotation strategy must be rejected."""
        with pytest.raises(ValidationError):
            UpdateConfigRequest(rotation_strategy="nonexistent-strategy")

    def test_very_long_rotation_strategy_rejected(self) -> None:
        """Rotation strategy longer than 64 chars must be rejected."""
        with pytest.raises(ValidationError):
            UpdateConfigRequest(rotation_strategy="x" * 65)

    def test_timeout_at_boundary(self) -> None:
        """Timeout exactly at 300 should be accepted."""
        req = UpdateConfigRequest(timeout=300)
        assert req.timeout == 300

    def test_timeout_over_boundary_rejected(self) -> None:
        """Timeout over 300 must be rejected."""
        with pytest.raises(ValidationError):
            UpdateConfigRequest(timeout=301)

    def test_timeout_zero_rejected(self) -> None:
        """Zero timeout must be rejected."""
        with pytest.raises(ValidationError):
            UpdateConfigRequest(timeout=0)

    def test_timeout_none_accepted(self) -> None:
        """``None`` timeout should be accepted."""
        req = UpdateConfigRequest(timeout=None)
        assert req.timeout is None

    def test_cors_origin_at_boundary(self) -> None:
        """CORS origin exactly at 256 chars should be accepted."""
        origin = "https://" + "a" * 248
        req = UpdateConfigRequest(cors_origins=[origin])
        assert req.cors_origins == [origin]

    def test_cors_origin_over_boundary_rejected(self) -> None:
        """CORS origin over 256 chars must be rejected."""
        origin = "https://" + "a" * 249
        with pytest.raises(ValidationError):
            UpdateConfigRequest(cors_origins=[origin])

    def test_empty_cors_origins_accepted(self) -> None:
        """Empty CORS origins list should be accepted."""
        req = UpdateConfigRequest(cors_origins=[])
        assert req.cors_origins == []

    def test_none_cors_origins_accepted(self) -> None:
        """``None`` CORS origins should be accepted."""
        req = UpdateConfigRequest(cors_origins=None)
        assert req.cors_origins is None


# ============================================================================
# VALIDATOR TYPEGUARD EDGE CASES
# ============================================================================


class TestValidatorEdgeCases:
    """Edge-case fuzzing for ``proxywhirl.validators``."""

    @pytest.mark.parametrize(
        "value,expected",
        [
            ("", False),
            (None, False),
            ("not a url", False),
            ("http://", False),
            ("http://host", False),
            ("http://host:0", False),
            ("http://host:99999", False),
            ("http://host:8080", True),
            ("https://host:443/path", True),  # path is allowed by is_valid_proxy_url
            ("socks5://host:1080", True),
        ],
    )
    def test_is_valid_proxy_url_edge_cases(self, value: Any, expected: bool) -> None:
        """``is_valid_proxy_url`` must handle edge cases correctly."""
        assert is_valid_proxy_url(value) is expected

    @pytest.mark.parametrize(
        "value,expected",
        [
            ("", False),
            (None, False),
            ("not a host", False),
            ("host", False),
            ("example.com", True),
            ("192.168.1.1", True),
            ("a" * 254, False),  # too long overall
            ("sub.example.com", True),
        ],
    )
    def test_is_valid_host_edge_cases(self, value: Any, expected: bool) -> None:
        """``is_valid_host`` must handle edge cases correctly."""
        assert is_valid_host(value) is expected

    @pytest.mark.parametrize(
        "value,expected",
        [
            (-1, False),
            (0, False),
            (1, True),
            (65535, True),
            (65536, False),
            ("8080", False),
            (None, False),
            (3.14, False),
        ],
    )
    def test_is_valid_port_edge_cases(self, value: Any, expected: bool) -> None:
        """``is_valid_port`` must handle edge cases correctly."""
        assert is_valid_port(value) is expected

    @pytest.mark.parametrize(
        "value,expected",
        [
            (-0.1, False),
            (0.0, True),
            (0.5, True),
            (1.0, True),
            (1.1, False),
            (None, False),
            ("0.5", False),
        ],
    )
    def test_is_success_rate_edge_cases(self, value: Any, expected: bool) -> None:
        """``is_success_rate`` must handle edge cases correctly."""
        assert is_success_rate(value) is expected

    @pytest.mark.parametrize(
        "value,expected",
        [
            (-1, False),
            (0, True),
            (1, True),
            (None, False),
            ("1", False),
        ],
    )
    def test_is_non_negative_edge_cases(self, value: Any, expected: bool) -> None:
        """``is_non_negative`` must handle edge cases correctly."""
        assert is_non_negative(value) is expected

    @pytest.mark.parametrize(
        "value,expected",
        [
            (0, False),
            (1, True),
            (-1, False),
            (None, False),
        ],
    )
    def test_is_positive_edge_cases(self, value: Any, expected: bool) -> None:
        """``is_positive`` must handle edge cases correctly."""
        assert is_positive(value) is expected


# ============================================================================
# JSON SERIALIZATION EDGE CASES
# ============================================================================


class TestSerializationEdgeCases:
    """Test serialization/deserialization of API models with edge-case data."""

    def test_proxied_request_json_roundtrip(self) -> None:
        """A ``ProxiedRequest`` should survive JSON round-trip."""
        req = ProxiedRequest(
            url="https://example.com/api",
            method="POST",
            headers={"Content-Type": "application/json"},
            body='{"key": "value"}',
            timeout=60,
        )
        data = json.loads(req.model_dump_json())
        restored = ProxiedRequest(**data)
        assert restored.method == "POST"
        assert restored.timeout == 60

    def test_create_proxy_request_json_roundtrip(self) -> None:
        """A ``CreateProxyRequest`` should survive JSON round-trip."""
        req = CreateProxyRequest(url="http://proxy.example.com:8080")
        data = json.loads(req.model_dump_json())
        restored = CreateProxyRequest(**data)
        assert restored.url == "http://proxy.example.com:8080"

    def test_update_config_request_json_roundtrip(self) -> None:
        """An ``UpdateConfigRequest`` should survive JSON round-trip."""
        req = UpdateConfigRequest(rotation_strategy="random", timeout=45)
        data = json.loads(req.model_dump_json())
        restored = UpdateConfigRequest(**data)
        assert restored.rotation_strategy == "random"
        assert restored.timeout == 45


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
            if name.startswith("test_") and (inspect.isfunction(member) or inspect.ismethod(member)):
                tests.append(member)
        return tests

    test_funcs = _collect_tests(module)
    for _, cls in inspect.getmembers(module, inspect.isclass):
        test_funcs.extend(_collect_tests(cls))

    assert len(test_funcs) >= 20, f"Expected >= 20 tests, found {len(test_funcs)}"
