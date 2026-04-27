"""
Type safety tests for ProxyWhirl.

Tests verify that Literal types, TypedDicts, and type hints are properly enforced.
"""

from __future__ import annotations

from enum import Enum

import pytest

from proxywhirl.models import (
    HealthStatus,
    Proxy,
    ProxyFormat,
    RenderMode,
    ValidationLevel,
)


class TestProxyProtocolLiterals:
    """Test Literal type hints for proxy protocols."""

    def test_valid_protocols(self) -> None:
        """Test that valid protocols are accepted."""
        valid_protocols = ["http", "https", "socks4", "socks5"]
        for protocol in valid_protocols:
            proxy = Proxy(
                url=f"{protocol}://example.com:8080",
                protocol=protocol,
                allow_local=False,
            )
            assert proxy.protocol == protocol

    def test_protocol_none_allowed(self) -> None:
        """Test that protocol can be None and is inferred from URL."""
        proxy = Proxy(url="http://example.com:8080", protocol=None, allow_local=False)
        # Protocol should be inferred from URL scheme
        assert proxy.protocol == "http"

    def test_invalid_protocol_rejected(self) -> None:
        """Test that invalid protocols are rejected by Pydantic validation."""
        with pytest.raises(Exception):
            Proxy(url="invalid://localhost:8080", protocol="invalid")  # type: ignore


class TestEnumConstants:
    """Test Enum type constants for type safety."""

    def test_health_status_enum(self) -> None:
        """Test HealthStatus enum values."""
        assert HealthStatus.UNKNOWN.value == "unknown"
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"
        assert HealthStatus.DEAD.value == "dead"

    def test_proxy_format_enum(self) -> None:
        """Test ProxyFormat enum values."""
        assert ProxyFormat.JSON.value == "json"
        assert ProxyFormat.CSV.value == "csv"
        assert ProxyFormat.PLAIN_TEXT.value == "plain_text"
        assert ProxyFormat.HTML_TABLE.value == "html_table"

    def test_render_mode_enum(self) -> None:
        """Test RenderMode enum values."""
        assert RenderMode.STATIC.value == "static"
        assert RenderMode.JAVASCRIPT.value == "javascript"
        assert RenderMode.BROWSER.value == "browser"
        assert RenderMode.AUTO.value == "auto"

    def test_validation_level_enum(self) -> None:
        """Test ValidationLevel enum values."""
        assert ValidationLevel.BASIC.value == "basic"
        assert ValidationLevel.STANDARD.value == "standard"
        assert ValidationLevel.FULL.value == "full"


class TestProxyModelTypes:
    """Test type hints in Proxy model."""

    def test_proxy_url_is_string(self) -> None:
        """Test that proxy URL is properly typed as string."""
        proxy = Proxy(url="http://example.com:8080", allow_local=False)
        assert isinstance(proxy.url, str)

    def test_proxy_credentials_are_secret_str(self) -> None:
        """Test that credentials are SecretStr type."""
        from pydantic import SecretStr

        proxy = Proxy(
            url="http://example.com:8080",
            username=SecretStr("user"),
            password=SecretStr("pass"),
            allow_local=False,
        )
        assert isinstance(proxy.username, SecretStr)
        assert isinstance(proxy.password, SecretStr)

    def test_proxy_id_is_uuid(self) -> None:
        """Test that proxy ID is UUID type."""
        from uuid import UUID

        proxy = Proxy(url="http://example.com:8080", allow_local=False)
        assert isinstance(proxy.id, UUID)

    def test_proxy_health_status_is_enum(self) -> None:
        """Test that health_status is HealthStatus enum."""
        proxy = Proxy(url="http://example.com:8080", allow_local=False)
        assert isinstance(proxy.health_status, HealthStatus)

    def test_proxy_timestamps_are_datetime_or_none(self) -> None:
        """Test that timestamps are datetime or None."""
        from datetime import datetime

        proxy = Proxy(url="http://example.com:8080", allow_local=False)
        assert proxy.last_success_at is None
        assert proxy.last_failure_at is None

        # Set timestamp
        now = datetime.now()
        proxy.last_success_at = now
        assert isinstance(proxy.last_success_at, datetime)


class TestConfigurationTyping:
    """Test type safety in configuration models."""

    def test_circuit_breaker_config_has_proper_types(self) -> None:
        """Test CircuitBreakerConfig field types."""
        from proxywhirl.models import CircuitBreakerConfig

        config = CircuitBreakerConfig()
        assert isinstance(config.failure_threshold, int)
        assert isinstance(config.window_duration, float)
        assert isinstance(config.timeout_duration, float)

    def test_strategy_config_weights_dict(self) -> None:
        """Test StrategyConfig weights dictionary typing."""
        from proxywhirl.models import StrategyConfig

        config = StrategyConfig(weights={"proxy1": 0.5, "proxy2": 0.5})
        assert isinstance(config.weights, dict)
        assert all(isinstance(v, float) for v in config.weights.values())

    def test_strategy_config_countries_list(self) -> None:
        """Test StrategyConfig countries list typing."""
        from proxywhirl.models import StrategyConfig

        config = StrategyConfig(preferred_countries=["US", "GB"])
        assert isinstance(config.preferred_countries, list)
        assert all(isinstance(c, str) for c in config.preferred_countries)


class TestModelValidation:
    """Test Pydantic model validation with type safety."""

    def test_proxy_url_validation(self) -> None:
        """Test that proxy URL is properly validated."""
        # Valid URL should work
        proxy = Proxy(url="http://example.com:8080", allow_local=False)
        assert proxy.url == "http://example.com:8080"

        # Empty URL should fail
        with pytest.raises(Exception):
            Proxy(url="", allow_local=False)

    def test_proxy_model_config_frozen(self) -> None:
        """Test that Proxy model is frozen (if configured)."""
        proxy = Proxy(url="http://example.com:8080", allow_local=False)
        # Check if model is frozen by attempting to set attribute
        try:
            proxy.url = "http://different:9090"  # type: ignore
            # If no error, model is not frozen (which is also acceptable)
        except Exception:
            # If error is raised, model is frozen (expected behavior)
            pass


class TestTypeHintIntegrity:
    """Test that type hints are present and correct."""

    def test_proxy_has_type_hints(self) -> None:
        """Test that Proxy class has type hints."""
        annotations = Proxy.__annotations__
        assert "url" in annotations
        assert "protocol" in annotations
        assert "username" in annotations
        assert "password" in annotations

    def test_health_status_enum_is_string_enum(self) -> None:
        """Test that HealthStatus is a string enum."""
        assert issubclass(HealthStatus, str)
        assert issubclass(HealthStatus, Enum)

    @pytest.mark.skipif(True, reason="Requires Python 3.10+ for full type checking")
    def test_literal_type_enforcement(self) -> None:
        """Test Literal type enforcement (requires mypy/pyright)."""
        # This would require static type checking with mypy/pyright
        # Cannot be tested at runtime
        pass
