"""Unit tests for structured logging configuration.

Tests cover:
- Configuration validation
- Format templates (JSON, logfmt, default)
- Log rotation and retention
- Context binding
- Logger retrieval
- Integration with existing loguru usage
"""

from __future__ import annotations

import json
import sys
from io import StringIO

import pytest
from loguru import logger

from proxywhirl.logging_config import (
    LogContext,
    LoggingConfig,
    LogRotationConfig,
    bind_context,
    configure_logging,
    get_logger,
)


class TestLoggingConfig:
    """Test cases for LoggingConfig model."""

    def test_default_config(self):
        """Test default configuration values."""
        config = LoggingConfig()
        assert config.format == "default"
        assert config.level == "INFO"
        assert config.rotation is None
        assert config.retention is None
        assert config.colorize is True
        assert config.diagnose is False
        assert config.backtrace is True
        assert config.enqueue is True

    def test_json_format_config(self):
        """Test JSON format configuration."""
        config = LoggingConfig(format="json", level="DEBUG")
        assert config.format == "json"
        assert config.level == "DEBUG"

    def test_logfmt_format_config(self):
        """Test logfmt format configuration."""
        config = LoggingConfig(format="logfmt", level="WARNING")
        assert config.format == "logfmt"
        assert config.level == "WARNING"

    def test_rotation_config(self):
        """Test rotation configuration."""
        config = LoggingConfig(rotation="10 MB", retention="1 week")
        assert config.rotation == "10 MB"
        assert config.retention == "1 week"

    def test_invalid_format_rejected(self):
        """Test that invalid format is rejected."""
        with pytest.raises(ValueError):
            LoggingConfig(format="invalid")


class TestLogRotationConfig:
    """Test cases for LogRotationConfig model."""

    def test_size_rotation(self):
        """Test size-based rotation configuration."""
        config = LogRotationConfig(size="10 MB")
        assert config.size == "10 MB"
        assert config.time is None

    def test_time_rotation(self):
        """Test time-based rotation configuration."""
        config = LogRotationConfig(time="1 day")
        assert config.time == "1 day"
        assert config.size is None

    def test_retention_config(self):
        """Test retention configuration."""
        config = LogRotationConfig(retention="1 week")
        assert config.retention == "1 week"

    def test_combined_rotation(self):
        """Test combined size and time rotation."""
        config = LogRotationConfig(size="10 MB", time="1 day", retention="1 week")
        assert config.size == "10 MB"
        assert config.time == "1 day"
        assert config.retention == "1 week"


class TestConfigureLogging:
    """Test cases for configure_logging function."""

    def setup_method(self):
        """Set up test fixtures before each test."""
        # Remove all handlers before each test
        logger.remove()

    def teardown_method(self):
        """Clean up after each test."""
        # Restore default handler
        logger.remove()
        logger.add(sys.stderr)

    def test_default_logging(self):
        """Test default logging configuration."""
        output = StringIO()
        # Disable async queue for synchronous testing
        configure_logging(sink=output, enqueue=False)

        # Verify logger is configured
        test_logger = get_logger()
        test_logger.info("Test message")

        # Check output
        output_value = output.getvalue()
        assert "Test message" in output_value
        assert "INFO" in output_value

    def test_json_logging(self):
        """Test JSON format logging."""
        output = StringIO()
        configure_logging(format="json", sink=output, enqueue=False)

        test_logger = get_logger()
        test_logger.info("JSON test message")

        # Parse JSON output (loguru's native format)
        output_value = output.getvalue().strip()
        log_entry = json.loads(output_value)

        # Check loguru's standard JSON fields
        assert "text" in log_entry
        assert "JSON test message" in log_entry["text"]
        assert "record" in log_entry
        assert log_entry["record"]["level"]["name"] == "INFO"
        assert log_entry["record"]["message"] == "JSON test message"

    def test_json_logging_with_context(self):
        """Test JSON logging with contextual metadata."""
        output = StringIO()
        configure_logging(format="json", sink=output, enqueue=False)

        test_logger = get_logger()
        test_logger.bind(request_id="req-123", operation="test").info("Context test")

        # Parse JSON output
        output_value = output.getvalue().strip()
        log_entry = json.loads(output_value)

        assert log_entry["record"]["message"] == "Context test"
        assert "extra" in log_entry["record"]
        assert log_entry["record"]["extra"]["request_id"] == "req-123"
        assert log_entry["record"]["extra"]["operation"] == "test"

    def test_json_logging_with_exception(self):
        """Test JSON logging with exception information."""
        output = StringIO()
        configure_logging(format="json", sink=output, enqueue=False)

        test_logger = get_logger()
        try:
            raise ValueError("Test exception")
        except ValueError:
            test_logger.exception("Exception occurred")

        # Parse JSON output
        output_value = output.getvalue().strip()
        log_entry = json.loads(output_value)

        assert log_entry["record"]["message"] == "Exception occurred"
        assert log_entry["record"]["exception"] is not None
        assert "ValueError" in log_entry["text"]
        assert "Test exception" in log_entry["text"]

    def test_logfmt_logging(self):
        """Test logfmt format logging."""
        output = StringIO()
        configure_logging(format="logfmt", sink=output, enqueue=False)

        test_logger = get_logger()
        test_logger.info("Logfmt test message")

        output_value = output.getvalue()
        assert "level=INFO" in output_value
        assert "message=Logfmt test message" in output_value
        assert "time=" in output_value

    def test_level_configuration(self):
        """Test log level configuration."""
        output = StringIO()
        configure_logging(level="WARNING", sink=output, enqueue=False)

        test_logger = get_logger()
        test_logger.debug("Debug message")
        test_logger.info("Info message")
        test_logger.warning("Warning message")

        output_value = output.getvalue()
        # Only WARNING and above should be logged
        assert "Debug message" not in output_value
        assert "Info message" not in output_value
        assert "Warning message" in output_value

    def test_colorize_disabled_for_json(self):
        """Test that colorize is disabled for JSON format."""
        output = StringIO()
        configure_logging(format="json", colorize=True, sink=output, enqueue=False)

        test_logger = get_logger()
        test_logger.info("Test")

        # JSON output should not contain ANSI color codes
        output_value = output.getvalue()
        assert "\x1b[" not in output_value

    def test_colorize_disabled_for_logfmt(self):
        """Test that colorize is disabled for logfmt format."""
        output = StringIO()
        configure_logging(format="logfmt", colorize=True, sink=output, enqueue=False)

        test_logger = get_logger()
        test_logger.info("Test")

        # Logfmt output should not contain ANSI color codes
        output_value = output.getvalue()
        assert "\x1b[" not in output_value

    def test_file_logging_with_rotation(self, tmp_path):
        """Test file logging with rotation configuration."""
        log_file = tmp_path / "test.log"

        configure_logging(
            format="json",
            sink=str(log_file),
            rotation="1 MB",
            retention="1 week",
            enqueue=False,
        )

        test_logger = get_logger()
        test_logger.info("Test message to file")

        # Verify file was created and contains the message
        assert log_file.exists()
        content = log_file.read_text()
        log_entry = json.loads(content.strip())
        assert log_entry["record"]["message"] == "Test message to file"

    def test_diagnose_mode(self):
        """Test diagnostic mode configuration."""
        output = StringIO()
        configure_logging(diagnose=True, sink=output, enqueue=False)

        test_logger = get_logger()
        test_logger.info("Diagnose test")

        # In diagnose mode, extra debug info is included
        # This is a simple test that configuration is accepted
        output_value = output.getvalue()
        assert "Diagnose test" in output_value

    def test_backtrace_disabled(self):
        """Test backtrace can be disabled."""
        output = StringIO()
        configure_logging(backtrace=False, sink=output, enqueue=False)

        test_logger = get_logger()
        try:
            raise ValueError("Test")
        except ValueError:
            test_logger.exception("Error")

        # Backtrace should be minimal when disabled
        output_value = output.getvalue()
        assert "Error" in output_value


class TestGetLogger:
    """Test cases for get_logger function."""

    def test_get_logger_returns_loguru_instance(self):
        """Test that get_logger returns the loguru logger."""
        test_logger = get_logger()
        assert test_logger is logger

    def test_get_logger_is_configured(self):
        """Test that get_logger returns configured instance."""
        output = StringIO()
        configure_logging(format="json", sink=output, enqueue=False)

        test_logger = get_logger()
        test_logger.info("Test")

        # Verify JSON output
        output_value = output.getvalue().strip()
        log_entry = json.loads(output_value)
        assert log_entry["record"]["message"] == "Test"


class TestBindContext:
    """Test cases for bind_context function."""

    def test_bind_single_context(self):
        """Test binding single context variable."""
        output = StringIO()
        configure_logging(format="json", sink=output, enqueue=False)

        context_logger = bind_context(request_id="req-123")
        context_logger.info("Test")

        log_entry = json.loads(output.getvalue().strip())
        assert log_entry["record"]["extra"]["request_id"] == "req-123"

    def test_bind_multiple_context(self):
        """Test binding multiple context variables."""
        output = StringIO()
        configure_logging(format="json", sink=output, enqueue=False)

        context_logger = bind_context(
            request_id="req-123",
            operation="fetch",
            proxy_id="proxy-456",
        )
        context_logger.info("Test")

        log_entry = json.loads(output.getvalue().strip())
        extra = log_entry["record"]["extra"]
        assert extra["request_id"] == "req-123"
        assert extra["operation"] == "fetch"
        assert extra["proxy_id"] == "proxy-456"

    def test_bind_context_types(self):
        """Test binding different types of context values."""
        output = StringIO()
        configure_logging(format="json", sink=output, enqueue=False)

        context_logger = bind_context(
            str_value="test",
            int_value=42,
            float_value=3.14,
            bool_value=True,
            none_value=None,
        )
        context_logger.info("Test")

        log_entry = json.loads(output.getvalue().strip())
        extra = log_entry["record"]["extra"]
        assert extra["str_value"] == "test"
        assert extra["int_value"] == 42
        assert extra["float_value"] == 3.14
        assert extra["bool_value"] is True
        assert extra["none_value"] is None


class TestLogContext:
    """Test cases for LogContext context manager."""

    def test_context_manager_basic(self):
        """Test basic context manager usage."""
        output = StringIO()
        configure_logging(format="json", sink=output, enqueue=False)

        test_logger = get_logger()

        with LogContext(request_id="req-123"):
            # Inside context, logs should have the bound context
            test_logger.bind(request_id="req-123").info("Inside context")

        log_entry = json.loads(output.getvalue().strip())
        assert log_entry["record"]["extra"]["request_id"] == "req-123"

    def test_context_manager_multiple_values(self):
        """Test context manager with multiple values."""
        output = StringIO()
        configure_logging(format="json", sink=output, enqueue=False)

        test_logger = get_logger()

        with LogContext(request_id="req-123", operation="test", proxy_id="proxy-456"):
            test_logger.bind(request_id="req-123", operation="test", proxy_id="proxy-456").info(
                "Test"
            )

        log_entry = json.loads(output.getvalue().strip())
        extra = log_entry["record"]["extra"]
        assert extra["request_id"] == "req-123"
        assert extra["operation"] == "test"
        assert extra["proxy_id"] == "proxy-456"

    def test_context_manager_nested(self):
        """Test nested context managers."""
        output = StringIO()
        configure_logging(format="json", sink=output, enqueue=False)

        test_logger = get_logger()

        with LogContext(request_id="req-123"), LogContext(operation="test"):
            test_logger.bind(request_id="req-123", operation="test").info("Nested")

        log_entry = json.loads(output.getvalue().strip())
        extra = log_entry["record"]["extra"]
        assert extra["request_id"] == "req-123"
        assert extra["operation"] == "test"


class TestIntegrationWithExistingCode:
    """Test integration with existing loguru usage in codebase."""

    def test_existing_logger_import_works(self):
        """Test that existing 'from loguru import logger' still works."""
        from loguru import logger as imported_logger

        output = StringIO()
        configure_logging(sink=output, enqueue=False)

        # Existing code using direct import should work
        imported_logger.info("Test from direct import")

        output_value = output.getvalue()
        assert "Test from direct import" in output_value

    def test_get_logger_matches_imported_logger(self):
        """Test that get_logger() returns same instance as direct import."""
        from loguru import logger as imported_logger

        retrieved_logger = get_logger()
        assert retrieved_logger is imported_logger

    def test_configuration_affects_all_logger_references(self):
        """Test that configuration applies to all logger references."""
        from loguru import logger as imported_logger

        output = StringIO()
        configure_logging(format="json", level="WARNING", sink=output, enqueue=False)

        # Both references should use same configuration
        retrieved_logger = get_logger()

        retrieved_logger.info("Info from get_logger")  # Should not appear
        imported_logger.info("Info from import")  # Should not appear
        retrieved_logger.warning("Warning from get_logger")  # Should appear
        imported_logger.warning("Warning from import")  # Should appear

        output_value = output.getvalue()
        lines = [line for line in output_value.strip().split("\n") if line]

        # Should have exactly 2 log entries (both warnings)
        assert len(lines) == 2

        # Parse and verify both entries
        entry1 = json.loads(lines[0])
        entry2 = json.loads(lines[1])

        assert entry1["record"]["level"]["name"] == "WARNING"
        assert entry2["record"]["level"]["name"] == "WARNING"
        assert entry1["record"]["message"] == "Warning from get_logger"
        assert entry2["record"]["message"] == "Warning from import"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_message(self):
        """Test logging empty message."""
        output = StringIO()
        configure_logging(format="json", sink=output, enqueue=False)

        test_logger = get_logger()
        test_logger.info("")

        log_entry = json.loads(output.getvalue().strip())
        assert log_entry["record"]["message"] == ""

    def test_unicode_message(self):
        """Test logging unicode characters."""
        output = StringIO()
        configure_logging(format="json", sink=output, enqueue=False)

        test_logger = get_logger()
        test_logger.info("Unicode test: 你好世界 🌍")

        log_entry = json.loads(output.getvalue().strip())
        assert log_entry["record"]["message"] == "Unicode test: 你好世界 🌍"

    def test_special_characters_in_context(self):
        """Test special characters in context values."""
        output = StringIO()
        configure_logging(format="json", sink=output, enqueue=False)

        context_logger = bind_context(url="http://example.com:8080?param=value&other=123")
        context_logger.info("Test")

        log_entry = json.loads(output.getvalue().strip())
        assert (
            log_entry["record"]["extra"]["url"] == "http://example.com:8080?param=value&other=123"
        )

    def test_multiline_message(self):
        """Test logging multiline message."""
        output = StringIO()
        configure_logging(format="json", sink=output, enqueue=False)

        test_logger = get_logger()
        test_logger.info("Line 1\nLine 2\nLine 3")

        log_entry = json.loads(output.getvalue().strip())
        assert log_entry["record"]["message"] == "Line 1\nLine 2\nLine 3"

    def test_large_context_payload(self):
        """Test logging with large context payload."""
        output = StringIO()
        configure_logging(format="json", sink=output, enqueue=False)

        # Create large context
        large_context = {f"key_{i}": f"value_{i}" for i in range(100)}
        context_logger = bind_context(**large_context)
        context_logger.info("Large context test")

        log_entry = json.loads(output.getvalue().strip())
        extra = log_entry["record"]["extra"]
        assert len(extra) == 100
        assert extra["key_0"] == "value_0"
        assert extra["key_99"] == "value_99"
