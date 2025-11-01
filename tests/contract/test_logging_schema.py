"""
Contract tests for structured log entry schema validation.

These tests ensure that log entries produced by the logging system
conform to the JSON schema defined in contracts/log-entry.schema.json.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jsonschema
import pytest


@pytest.fixture
def log_entry_schema() -> dict[str, Any]:
    """Load the log entry JSON schema."""
    schema_path = Path(__file__).parent.parent.parent / "specs" / "007-logging-system-structured" / "contracts" / "log-entry.schema.json"
    with open(schema_path) as f:
        return json.load(f)


class TestLogEntrySchemaValidation:
    """Test that log entries conform to the defined JSON schema."""

    def test_minimal_valid_log_entry(self, log_entry_schema: dict[str, Any]) -> None:
        """Test that a minimal valid log entry passes schema validation."""
        log_entry = {
            "timestamp": "2025-11-01T12:34:56.789Z",
            "level": "INFO",
            "message": "Test message",
            "module": "proxywhirl.rotator",
            "function": "select_proxy",
            "line": 145,
        }
        
        # Should not raise ValidationError
        jsonschema.validate(instance=log_entry, schema=log_entry_schema)

    def test_full_log_entry_with_context(self, log_entry_schema: dict[str, Any]) -> None:
        """Test that a full log entry with all optional fields passes validation."""
        log_entry = {
            "timestamp": "2025-11-01T12:34:56.789Z",
            "level": "INFO",
            "message": "Proxy selected successfully",
            "module": "proxywhirl.rotator",
            "function": "select_proxy",
            "line": 145,
            "request_id": "550e8400-e29b-41d4-a716-446655440000",
            "operation": "proxy_selection",
            "proxy_url": "http://proxy1.example.com:8080",
            "strategy": "weighted",
            "source": "free_proxy_list",
            "extra": {
                "proxy_weight": 0.75,
                "selection_time_ms": 2.5,
            }
        }
        
        jsonschema.validate(instance=log_entry, schema=log_entry_schema)

    def test_error_log_with_exception(self, log_entry_schema: dict[str, Any]) -> None:
        """Test that error logs with exception details pass validation."""
        log_entry = {
            "timestamp": "2025-11-01T12:35:10.123Z",
            "level": "ERROR",
            "message": "Health check failed for proxy",
            "module": "proxywhirl.health",
            "function": "check_proxy",
            "line": 89,
            "request_id": "550e8400-e29b-41d4-a716-446655440001",
            "operation": "health_check",
            "proxy_url": "http://proxy2.example.com:8080",
            "exception": {
                "type": "TimeoutError",
                "message": "Connection timed out after 5 seconds",
                "traceback": [
                    'File "/app/proxywhirl/health.py", line 89, in check_proxy',
                    "  response = await client.get(url, timeout=5.0)",
                    "..."
                ]
            },
            "extra": {
                "timeout_seconds": 5,
                "retry_count": 3
            }
        }
        
        jsonschema.validate(instance=log_entry, schema=log_entry_schema)

    def test_all_log_levels_are_valid(self, log_entry_schema: dict[str, Any]) -> None:
        """Test that all standard log levels are accepted."""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in levels:
            log_entry = {
                "timestamp": "2025-11-01T12:34:56.789Z",
                "level": level,
                "message": f"Test {level} message",
                "module": "proxywhirl.test",
                "function": "test_func",
                "line": 1,
            }
            jsonschema.validate(instance=log_entry, schema=log_entry_schema)

    def test_invalid_log_level_fails(self, log_entry_schema: dict[str, Any]) -> None:
        """Test that invalid log levels are rejected."""
        log_entry = {
            "timestamp": "2025-11-01T12:34:56.789Z",
            "level": "INVALID",
            "message": "Test message",
            "module": "proxywhirl.test",
            "function": "test_func",
            "line": 1,
        }
        
        with pytest.raises(jsonschema.ValidationError, match="'INVALID' is not one of"):
            jsonschema.validate(instance=log_entry, schema=log_entry_schema)

    def test_missing_required_field_fails(self, log_entry_schema: dict[str, Any]) -> None:
        """Test that missing required fields cause validation to fail."""
        # Missing 'message' field
        log_entry = {
            "timestamp": "2025-11-01T12:34:56.789Z",
            "level": "INFO",
            "module": "proxywhirl.test",
            "function": "test_func",
            "line": 1,
        }
        
        with pytest.raises(jsonschema.ValidationError, match="'message' is a required property"):
            jsonschema.validate(instance=log_entry, schema=log_entry_schema)

    def test_empty_message_fails(self, log_entry_schema: dict[str, Any]) -> None:
        """Test that empty message strings are rejected."""
        log_entry = {
            "timestamp": "2025-11-01T12:34:56.789Z",
            "level": "INFO",
            "message": "",
            "module": "proxywhirl.test",
            "function": "test_func",
            "line": 1,
        }
        
        with pytest.raises(jsonschema.ValidationError, match="minLength"):
            jsonschema.validate(instance=log_entry, schema=log_entry_schema)

    def test_negative_line_number_fails(self, log_entry_schema: dict[str, Any]) -> None:
        """Test that negative line numbers are rejected."""
        log_entry = {
            "timestamp": "2025-11-01T12:34:56.789Z",
            "level": "INFO",
            "message": "Test message",
            "module": "proxywhirl.test",
            "function": "test_func",
            "line": -1,
        }
        
        with pytest.raises(jsonschema.ValidationError, match="minimum"):
            jsonschema.validate(instance=log_entry, schema=log_entry_schema)

    def test_exception_without_type_fails(self, log_entry_schema: dict[str, Any]) -> None:
        """Test that exception objects require type and message fields."""
        log_entry = {
            "timestamp": "2025-11-01T12:34:56.789Z",
            "level": "ERROR",
            "message": "Error occurred",
            "module": "proxywhirl.test",
            "function": "test_func",
            "line": 1,
            "exception": {
                "message": "Something went wrong"
                # Missing required 'type' field
            }
        }
        
        with pytest.raises(jsonschema.ValidationError, match="'type' is a required property"):
            jsonschema.validate(instance=log_entry, schema=log_entry_schema)

    def test_extra_fields_allowed(self, log_entry_schema: dict[str, Any]) -> None:
        """Test that extra structured fields are allowed."""
        log_entry = {
            "timestamp": "2025-11-01T12:34:56.789Z",
            "level": "INFO",
            "message": "Test message",
            "module": "proxywhirl.test",
            "function": "test_func",
            "line": 1,
            "extra": {
                "custom_field_1": "value1",
                "custom_field_2": 42,
                "custom_field_3": True,
                "nested": {
                    "key": "value"
                }
            }
        }
        
        jsonschema.validate(instance=log_entry, schema=log_entry_schema)

    def test_null_optional_fields_allowed(self, log_entry_schema: dict[str, Any]) -> None:
        """Test that optional fields can be null."""
        log_entry = {
            "timestamp": "2025-11-01T12:34:56.789Z",
            "level": "INFO",
            "message": "Test message",
            "module": "proxywhirl.test",
            "function": "test_func",
            "line": 1,
            "request_id": None,
            "operation": None,
            "proxy_url": None,
            "strategy": None,
            "source": None,
            "user_id": None,
            "exception": None,
        }
        
        jsonschema.validate(instance=log_entry, schema=log_entry_schema)

    def test_timestamp_format_validation(self, log_entry_schema: dict[str, Any]) -> None:
        """Test various timestamp formats."""
        valid_timestamps = [
            "2025-11-01T12:34:56.789Z",
            "2025-11-01T12:34:56.789+00:00",
            "2025-11-01T12:34:56+00:00",
            datetime.now(timezone.utc).isoformat(),
        ]
        
        for timestamp in valid_timestamps:
            log_entry = {
                "timestamp": timestamp,
                "level": "INFO",
                "message": "Test message",
                "module": "proxywhirl.test",
                "function": "test_func",
                "line": 1,
            }
            jsonschema.validate(instance=log_entry, schema=log_entry_schema)

    def test_unicode_in_message(self, log_entry_schema: dict[str, Any]) -> None:
        """Test that Unicode characters in messages are handled correctly."""
        log_entry = {
            "timestamp": "2025-11-01T12:34:56.789Z",
            "level": "INFO",
            "message": "???? ?? ???????? ?????????",
            "module": "proxywhirl.test",
            "function": "test_func",
            "line": 1,
        }
        
        jsonschema.validate(instance=log_entry, schema=log_entry_schema)

    def test_redacted_credentials_in_proxy_url(self, log_entry_schema: dict[str, Any]) -> None:
        """Test that redacted credentials in proxy URLs pass validation."""
        log_entry = {
            "timestamp": "2025-11-01T12:34:56.789Z",
            "level": "INFO",
            "message": "Proxy selected",
            "module": "proxywhirl.rotator",
            "function": "select_proxy",
            "line": 145,
            "proxy_url": "http://user:***@proxy2.example.com:3128",
        }
        
        jsonschema.validate(instance=log_entry, schema=log_entry_schema)
