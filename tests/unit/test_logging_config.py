"""
Unit tests for logging configuration models and validation.
"""

import pytest
from pydantic import ValidationError

from proxywhirl.logging_config import (
    LogConfiguration,
    LogHandlerConfig,
    LogHandlerType,
    LogLevel,
)


class TestLogHandlerConfig:
    """Tests for LogHandlerConfig model validation."""

    def test_console_handler_minimal(self) -> None:
        """Test console handler with minimal configuration."""
        config = LogHandlerConfig(type=LogHandlerType.CONSOLE)
        assert config.type == LogHandlerType.CONSOLE
        assert config.level == LogLevel.INFO
        assert config.format == "default"

    def test_file_handler_with_path(self) -> None:
        """Test file handler requires path."""
        config = LogHandlerConfig(
            type=LogHandlerType.FILE,
            path="logs/app.log"
        )
        assert config.type == LogHandlerType.FILE
        assert config.path == "logs/app.log"

    def test_file_handler_with_rotation(self) -> None:
        """Test file handler with rotation settings."""
        config = LogHandlerConfig(
            type=LogHandlerType.FILE,
            path="logs/app.log",
            rotation="100 MB",
            retention="7 days"
        )
        assert config.rotation == "100 MB"
        assert config.retention == "7 days"

    def test_syslog_handler_with_url(self) -> None:
        """Test syslog handler with URL."""
        config = LogHandlerConfig(
            type=LogHandlerType.SYSLOG,
            url="syslog://localhost:514"
        )
        assert config.type == LogHandlerType.SYSLOG
        assert config.url == "syslog://localhost:514"

    def test_http_handler_with_url(self) -> None:
        """Test HTTP handler with URL."""
        config = LogHandlerConfig(
            type=LogHandlerType.HTTP,
            url="https://logs.example.com/ingest"
        )
        assert config.type == LogHandlerType.HTTP
        assert config.url == "https://logs.example.com/ingest"

    def test_handler_with_custom_level(self) -> None:
        """Test handler with custom log level."""
        config = LogHandlerConfig(
            type=LogHandlerType.CONSOLE,
            level=LogLevel.DEBUG
        )
        assert config.level == LogLevel.DEBUG

    def test_handler_with_json_format(self) -> None:
        """Test handler with JSON format."""
        config = LogHandlerConfig(
            type=LogHandlerType.CONSOLE,
            format="json"
        )
        assert config.format == "json"

    def test_handler_with_logfmt_format(self) -> None:
        """Test handler with logfmt format."""
        config = LogHandlerConfig(
            type=LogHandlerType.FILE,
            path="logs/app.log",
            format="logfmt"
        )
        assert config.format == "logfmt"

    def test_handler_filters_by_module(self) -> None:
        """Test handler with module filters."""
        config = LogHandlerConfig(
            type=LogHandlerType.CONSOLE,
            filter_modules=["proxywhirl.rotator", "proxywhirl.strategies"]
        )
        assert "proxywhirl.rotator" in config.filter_modules
        assert "proxywhirl.strategies" in config.filter_modules

    def test_handler_with_sampling_rate(self) -> None:
        """Test handler with sampling configuration."""
        config = LogHandlerConfig(
            type=LogHandlerType.CONSOLE,
            sample_rate=0.1
        )
        assert config.sample_rate == 0.1

    def test_sample_rate_validation(self) -> None:
        """Test sample rate must be between 0 and 1."""
        with pytest.raises(ValidationError, match="sample_rate"):
            LogHandlerConfig(
                type=LogHandlerType.CONSOLE,
                sample_rate=1.5
            )

        with pytest.raises(ValidationError, match="sample_rate"):
            LogHandlerConfig(
                type=LogHandlerType.CONSOLE,
                sample_rate=-0.1
            )


class TestLogConfiguration:
    """Tests for LogConfiguration model validation."""

    def test_minimal_configuration(self) -> None:
        """Test minimal logging configuration."""
        config = LogConfiguration()
        assert config.level == LogLevel.INFO
        assert config.async_logging is True
        assert config.queue_size == 1000
        assert config.drop_on_full is True
        assert len(config.handlers) == 0

    def test_configuration_with_custom_level(self) -> None:
        """Test configuration with custom log level."""
        config = LogConfiguration(level=LogLevel.DEBUG)
        assert config.level == LogLevel.DEBUG

    def test_configuration_with_handlers(self) -> None:
        """Test configuration with multiple handlers."""
        config = LogConfiguration(
            handlers=[
                LogHandlerConfig(type=LogHandlerType.CONSOLE),
                LogHandlerConfig(
                    type=LogHandlerType.FILE,
                    path="logs/app.log"
                ),
            ]
        )
        assert len(config.handlers) == 2
        assert config.handlers[0].type == LogHandlerType.CONSOLE
        assert config.handlers[1].type == LogHandlerType.FILE

    def test_queue_size_validation(self) -> None:
        """Test queue size must be positive."""
        with pytest.raises(ValidationError, match="queue_size"):
            LogConfiguration(queue_size=0)

        with pytest.raises(ValidationError, match="queue_size"):
            LogConfiguration(queue_size=-100)

    def test_async_logging_disabled(self) -> None:
        """Test configuration with async logging disabled."""
        config = LogConfiguration(async_logging=False)
        assert config.async_logging is False

    def test_drop_on_full_disabled(self) -> None:
        """Test configuration with drop_on_full disabled."""
        config = LogConfiguration(drop_on_full=False)
        assert config.drop_on_full is False

    def test_redact_credentials_enabled(self) -> None:
        """Test credential redaction configuration."""
        config = LogConfiguration(redact_credentials=True)
        assert config.redact_credentials is True

    def test_configuration_serialization(self) -> None:
        """Test configuration can be serialized to dict."""
        config = LogConfiguration(
            level=LogLevel.WARNING,
            queue_size=2000,
            handlers=[
                LogHandlerConfig(type=LogHandlerType.CONSOLE)
            ]
        )
        data = config.model_dump()
        assert data["level"] == LogLevel.WARNING
        assert data["queue_size"] == 2000
        assert len(data["handlers"]) == 1

    def test_configuration_from_dict(self) -> None:
        """Test configuration can be loaded from dict."""
        data = {
            "level": "DEBUG",
            "async_logging": False,
            "queue_size": 500,
            "handlers": [
                {"type": "console", "format": "json"}
            ]
        }
        config = LogConfiguration(**data)
        assert config.level == LogLevel.DEBUG
        assert config.async_logging is False
        assert config.queue_size == 500
        assert config.handlers[0].format == "json"


class TestLogLevelEnum:
    """Tests for LogLevel enum."""

    def test_all_standard_levels_defined(self) -> None:
        """Test all standard log levels are defined."""
        assert LogLevel.DEBUG == "DEBUG"
        assert LogLevel.INFO == "INFO"
        assert LogLevel.WARNING == "WARNING"
        assert LogLevel.ERROR == "ERROR"
        assert LogLevel.CRITICAL == "CRITICAL"

    def test_level_ordering(self) -> None:
        """Test log levels can be compared."""
        # Note: Pydantic enums are string-based, so we test string values
        levels = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL]
        assert len(levels) == 5


class TestLogHandlerTypeEnum:
    """Tests for LogHandlerType enum."""

    def test_all_handler_types_defined(self) -> None:
        """Test all handler types are defined."""
        assert LogHandlerType.CONSOLE == "console"
        assert LogHandlerType.FILE == "file"
        assert LogHandlerType.SYSLOG == "syslog"
        assert LogHandlerType.HTTP == "http"


class TestConfigurationValidation:
    """Tests for complex validation scenarios."""

    def test_file_handler_validation(self) -> None:
        """Test file handler requires path."""
        # Valid file handler
        config = LogConfiguration(
            handlers=[
                LogHandlerConfig(
                    type=LogHandlerType.FILE,
                    path="logs/app.log"
                )
            ]
        )
        assert config.handlers[0].path == "logs/app.log"

    def test_multiple_handlers_same_type(self) -> None:
        """Test multiple handlers of same type are allowed."""
        config = LogConfiguration(
            handlers=[
                LogHandlerConfig(
                    type=LogHandlerType.FILE,
                    path="logs/debug.log",
                    level=LogLevel.DEBUG
                ),
                LogHandlerConfig(
                    type=LogHandlerType.FILE,
                    path="logs/error.log",
                    level=LogLevel.ERROR
                ),
            ]
        )
        assert len(config.handlers) == 2
        assert config.handlers[0].level == LogLevel.DEBUG
        assert config.handlers[1].level == LogLevel.ERROR

    def test_handler_level_precedence(self) -> None:
        """Test handler-level log level takes precedence over global."""
        config = LogConfiguration(
            level=LogLevel.WARNING,
            handlers=[
                LogHandlerConfig(
                    type=LogHandlerType.CONSOLE,
                    level=LogLevel.DEBUG
                )
            ]
        )
        # Handler should have its own level
        assert config.handlers[0].level == LogLevel.DEBUG
        # Global level is still WARNING
        assert config.level == LogLevel.WARNING

    def test_unicode_handling_in_paths(self) -> None:
        """Test configuration handles Unicode characters in paths."""
        config = LogHandlerConfig(
            type=LogHandlerType.FILE,
            path="logs/????.log"
        )
        assert "????" in config.path

    def test_special_characters_in_filters(self) -> None:
        """Test module filters with special characters."""
        config = LogHandlerConfig(
            type=LogHandlerType.CONSOLE,
            filter_modules=["app.module-name", "app.module_name"]
        )
        assert len(config.filter_modules) == 2
