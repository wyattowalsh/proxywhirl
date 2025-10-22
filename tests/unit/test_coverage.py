"""
Additional tests to reach >90% coverage.
"""

from pathlib import Path

import pytest
from pydantic import SecretStr, ValidationError

from proxywhirl.models import (
    HealthStatus,
    Proxy,
    ProxyConfiguration,
    ProxyCredentials,
    ProxyFormat,
    ProxyPool,
    ProxySource,
    ProxySourceConfig,
    RenderMode,
    SourceStats,
)


class TestProxyCredentialsEdgeCases:
    """Test ProxyCredentials edge cases."""

    def test_credentials_with_custom_auth_type(self):
        """Test credentials with digest auth type."""
        creds = ProxyCredentials(
            username=SecretStr("user"),
            password=SecretStr("pass"),
            auth_type="digest",
        )
        assert creds.auth_type == "digest"

    def test_credentials_with_bearer_auth(self):
        """Test credentials with bearer auth type."""
        creds = ProxyCredentials(
            username=SecretStr("user"),
            password=SecretStr("pass"),
            auth_type="bearer",
        )
        assert creds.auth_type == "bearer"

    def test_credentials_with_additional_headers(self):
        """Test credentials with additional headers."""
        creds = ProxyCredentials(
            username=SecretStr("user"),
            password=SecretStr("pass"),
            additional_headers={"X-Custom": "value", "X-Another": "header"},
        )
        assert len(creds.additional_headers) == 2
        assert creds.additional_headers["X-Custom"] == "value"


class TestProxySourceConfig:
    """Test ProxySourceConfig model."""

    def test_source_config_defaults(self):
        """Test ProxySourceConfig with defaults."""
        config = ProxySourceConfig(
            url="http://proxy-list.example.com/proxies.json",  # type: ignore
            format=ProxyFormat.JSON,
        )
        assert config.render_mode == RenderMode.AUTO
        assert config.enabled is True
        assert config.priority == 0
        assert config.refresh_interval == 3600

    def test_source_config_with_custom_values(self):
        """Test ProxySourceConfig with custom values."""
        config = ProxySourceConfig(
            url="http://proxy-list.example.com/proxies.html",  # type: ignore
            format=ProxyFormat.HTML_TABLE,
            render_mode=RenderMode.JAVASCRIPT,
            wait_selector=".proxy-table",
            wait_timeout=60000,
            refresh_interval=7200,
            enabled=False,
            priority=5,
            headers={"User-Agent": "ProxyBot/1.0"},
        )
        assert config.render_mode == RenderMode.JAVASCRIPT
        assert config.wait_selector == ".proxy-table"
        assert config.wait_timeout == 60000
        assert config.refresh_interval == 7200
        assert config.enabled is False
        assert config.priority == 5

    def test_source_config_with_auth(self):
        """Test ProxySourceConfig with authentication."""
        config = ProxySourceConfig(
            url="http://proxy-list.example.com/proxies.json",  # type: ignore
            format=ProxyFormat.JSON,
            auth=("username", "password"),
        )
        assert config.auth == ("username", "password")

    def test_source_config_with_metadata(self):
        """Test ProxySourceConfig with metadata."""
        config = ProxySourceConfig(
            url="http://proxy-list.example.com/proxies.json",  # type: ignore
            format=ProxyFormat.JSON,
            metadata={"provider": "example", "region": "us-east"},
        )
        assert config.metadata["provider"] == "example"
        assert config.metadata["region"] == "us-east"


class TestSourceStats:
    """Test SourceStats model."""

    def test_source_stats_defaults(self):
        """Test SourceStats with defaults."""
        stats = SourceStats(source_url="http://example.com/proxies")
        assert stats.total_fetched == 0
        assert stats.valid_count == 0
        assert stats.invalid_count == 0
        assert stats.last_fetch_at is None
        assert stats.fetch_failure_count == 0

    def test_source_stats_with_values(self):
        """Test SourceStats with actual values."""
        from datetime import UTC, datetime

        now = datetime.now(UTC)
        stats = SourceStats(
            source_url="http://example.com/proxies",
            total_fetched=100,
            valid_count=85,
            invalid_count=15,
            last_fetch_at=now,
            last_fetch_duration_ms=1500.0,
            fetch_failure_count=2,
            last_error="Connection timeout",
        )
        assert stats.total_fetched == 100
        assert stats.valid_count == 85
        assert stats.invalid_count == 15
        assert stats.last_fetch_duration_ms == 1500.0
        assert stats.fetch_failure_count == 2
        assert stats.last_error == "Connection timeout"


class TestProxyConfigurationStorage:
    """Test ProxyConfiguration storage validation."""

    def test_config_memory_storage_no_path_needed(self):
        """Test that memory storage doesn't require path."""
        config = ProxyConfiguration(storage_backend="memory")
        assert config.storage_backend == "memory"
        assert config.storage_path is None

    def test_config_sqlite_storage_with_path(self):
        """Test sqlite storage with path."""
        config = ProxyConfiguration(
            storage_backend="sqlite", storage_path=Path("/tmp/proxies.db")
        )
        assert config.storage_backend == "sqlite"
        assert config.storage_path == Path("/tmp/proxies.db")

    def test_config_file_storage_with_path(self):
        """Test file storage with path."""
        config = ProxyConfiguration(
            storage_backend="file", storage_path=Path("/tmp/proxies.json")
        )
        assert config.storage_backend == "file"
        assert config.storage_path == Path("/tmp/proxies.json")

    def test_config_is_frozen(self):
        """Test that configuration is immutable (frozen)."""
        config = ProxyConfiguration()
        with pytest.raises(ValidationError):
            config.timeout = 60  # type: ignore


class TestProxyRecordMethods:
    """Test proxy record_success and record_failure edge cases."""

    def test_record_success_from_degraded_to_healthy(self):
        """Test that success from degraded state goes to healthy."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            health_status=HealthStatus.DEGRADED,
        )  # type: ignore
        proxy.record_success(100.0)
        assert proxy.health_status == HealthStatus.HEALTHY

    def test_record_success_from_unknown_to_healthy(self):
        """Test that success from unknown state goes to healthy."""
        proxy = Proxy(url="http://proxy.example.com:8080")  # type: ignore
        assert proxy.health_status == HealthStatus.UNKNOWN
        proxy.record_success(100.0)
        assert proxy.health_status == HealthStatus.HEALTHY

    def test_record_failure_with_error_message(self):
        """Test recording failure with custom error message."""
        proxy = Proxy(url="http://proxy.example.com:8080")  # type: ignore
        proxy.record_failure(error="Connection refused")
        assert len(proxy.metadata["last_errors"]) == 1
        assert proxy.metadata["last_errors"][0]["error"] == "Connection refused"

    def test_record_failure_without_error_message(self):
        """Test recording failure without error message."""
        proxy = Proxy(url="http://proxy.example.com:8080")  # type: ignore
        proxy.record_failure()
        assert "last_errors" not in proxy.metadata or len(proxy.metadata["last_errors"]) == 0


class TestProxyPoolEdgeCases:
    """Test ProxyPool edge cases."""

    def test_pool_size_property(self):
        """Test pool size property."""
        pool = ProxyPool(name="test")
        assert pool.size == 0
        pool.add_proxy(Proxy(url="http://proxy1.example.com:8080"))  # type: ignore
        assert pool.size == 1

    def test_pool_get_proxy_by_id_with_multiple_proxies(self):
        """Test getting specific proxy by ID from multiple."""
        pool = ProxyPool(name="test")
        proxy1 = Proxy(url="http://proxy1.example.com:8080")  # type: ignore
        proxy2 = Proxy(url="http://proxy2.example.com:8080")  # type: ignore
        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)

        found = pool.get_proxy_by_id(proxy2.id)
        assert found is not None
        assert found.id == proxy2.id
        assert found.url == proxy2.url


class TestEnums:
    """Test enum values."""

    def test_health_status_values(self):
        """Test HealthStatus enum values."""
        assert HealthStatus.UNKNOWN.value == "unknown"
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"
        assert HealthStatus.DEAD.value == "dead"

    def test_proxy_source_values(self):
        """Test ProxySource enum values."""
        assert ProxySource.USER.value == "user"
        assert ProxySource.FETCHED.value == "fetched"
        assert ProxySource.API.value == "api"
        assert ProxySource.FILE.value == "file"

    def test_proxy_format_values(self):
        """Test ProxyFormat enum values."""
        assert ProxyFormat.JSON.value == "json"
        assert ProxyFormat.CSV.value == "csv"
        assert ProxyFormat.TSV.value == "tsv"
        assert ProxyFormat.PLAIN_TEXT.value == "plain_text"
        assert ProxyFormat.HTML_TABLE.value == "html_table"
        assert ProxyFormat.CUSTOM.value == "custom"

    def test_render_mode_values(self):
        """Test RenderMode enum values."""
        assert RenderMode.STATIC.value == "static"
        assert RenderMode.JAVASCRIPT.value == "javascript"
        assert RenderMode.AUTO.value == "auto"
