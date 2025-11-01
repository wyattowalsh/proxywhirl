"""
Unit tests for structured log formatters (JSON and logfmt).
"""

import json
from datetime import datetime, timezone
from typing import Any

import pytest

from proxywhirl.logging_formatters import (
    format_json_log,
    format_logfmt_log,
    redact_sensitive_data,
    serialize_exception,
)


class TestRedactSensitiveData:
    """Tests for sensitive data redaction."""

    def test_redact_password_in_dict(self) -> None:
        """Test redaction of password field in dictionary."""
        data = {"username": "admin", "password": "secret123"}
        redacted = redact_sensitive_data(data)
        assert redacted["username"] == "admin"
        assert redacted["password"] == "**REDACTED**"

    def test_redact_nested_credentials(self) -> None:
        """Test redaction of nested credential fields."""
        data = {
            "proxy": {
                "host": "proxy.example.com",
                "credentials": {
                    "username": "user",
                    "password": "pass",
                    "api_key": "key123"
                }
            }
        }
        redacted = redact_sensitive_data(data)
        assert redacted["proxy"]["host"] == "proxy.example.com"
        assert redacted["proxy"]["credentials"]["username"] == "user"
        assert redacted["proxy"]["credentials"]["password"] == "**REDACTED**"
        assert redacted["proxy"]["credentials"]["api_key"] == "**REDACTED**"

    def test_redact_url_with_credentials(self) -> None:
        """Test redaction of credentials in URLs."""
        url = "http://user:pass@proxy.example.com:8080"
        redacted = redact_sensitive_data(url)
        assert "****:****@proxy.example.com:8080" in redacted
        assert "user" not in redacted
        assert "pass" not in redacted

    def test_redact_token_fields(self) -> None:
        """Test redaction of token and secret fields."""
        data = {
            "auth_token": "bearer_xyz",
            "secret_key": "secret",
            "api_token": "token123",
        }
        redacted = redact_sensitive_data(data)
        assert redacted["auth_token"] == "**REDACTED**"
        assert redacted["secret_key"] == "**REDACTED**"
        assert redacted["api_token"] == "**REDACTED**"

    def test_redact_preserves_non_sensitive_data(self) -> None:
        """Test that non-sensitive data is not redacted."""
        data = {
            "user_id": "12345",
            "operation": "proxy_selection",
            "result": "success",
            "duration_ms": 42.5,
        }
        redacted = redact_sensitive_data(data)
        assert redacted == data

    def test_redact_handles_lists(self) -> None:
        """Test redaction in list structures."""
        data = [
            {"password": "secret1"},
            {"password": "secret2"},
            "normal string",
        ]
        redacted = redact_sensitive_data(data)
        assert redacted[0]["password"] == "**REDACTED**"
        assert redacted[1]["password"] == "**REDACTED**"
        assert redacted[2] == "normal string"

    def test_redact_unicode_data(self) -> None:
        """Test redaction with Unicode characters."""
        data = {"message": "????", "password": "??123"}
        redacted = redact_sensitive_data(data)
        assert redacted["message"] == "????"
        assert redacted["password"] == "**REDACTED**"

    def test_redact_circular_reference_protection(self) -> None:
        """Test that circular references don't cause infinite recursion."""
        data: dict[str, Any] = {"key": "value"}
        data["self"] = data  # Circular reference
        
        # Should not raise RecursionError
        redacted = redact_sensitive_data(data, max_depth=5)
        assert redacted["key"] == "value"

    def test_redact_case_insensitive(self) -> None:
        """Test that field name matching is case-insensitive."""
        data = {
            "Password": "secret1",
            "API_KEY": "key123",
            "secret_TOKEN": "token456",
        }
        redacted = redact_sensitive_data(data)
        assert redacted["Password"] == "**REDACTED**"
        assert redacted["API_KEY"] == "**REDACTED**"
        assert redacted["secret_TOKEN"] == "**REDACTED**"


class TestSerializeException:
    """Tests for exception serialization."""

    def test_serialize_simple_exception(self) -> None:
        """Test serialization of simple exception."""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            serialized = serialize_exception(e)
            assert serialized["type"] == "ValueError"
            assert serialized["message"] == "Test error"
            assert isinstance(serialized["traceback"], list)
            assert len(serialized["traceback"]) > 0

    def test_serialize_nested_exception(self) -> None:
        """Test serialization of exception with cause."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise RuntimeError("Wrapped error") from e
        except RuntimeError as e:
            serialized = serialize_exception(e)
            assert serialized["type"] == "RuntimeError"
            assert serialized["message"] == "Wrapped error"

    def test_serialize_exception_without_message(self) -> None:
        """Test serialization of exception without message."""
        try:
            raise Exception()
        except Exception as e:
            serialized = serialize_exception(e)
            assert serialized["type"] == "Exception"
            assert serialized["message"] == ""

    def test_serialize_exception_with_unicode(self) -> None:
        """Test serialization of exception with Unicode message."""
        try:
            raise ValueError("???? ??")
        except ValueError as e:
            serialized = serialize_exception(e)
            assert "???? ??" in serialized["message"]


class TestFormatJsonLog:
    """Tests for JSON log formatting."""

    def test_format_minimal_json_log(self) -> None:
        """Test JSON formatting of minimal log record."""
        record = {
            "time": datetime(2025, 11, 1, 12, 34, 56, 789000, tzinfo=timezone.utc),
            "level": "INFO",
            "message": "Test message",
            "module": "test",
            "function": "test_func",
            "line": 42,
            "exception": None,
            "extra": {},
        }
        
        formatted = format_json_log(record)
        parsed = json.loads(formatted)
        
        assert parsed["level"] == "INFO"
        assert parsed["message"] == "Test message"
        assert parsed["module"] == "test"
        assert parsed["function"] == "test_func"
        assert parsed["line"] == 42

    def test_format_json_with_extra_fields(self) -> None:
        """Test JSON formatting with extra context fields."""
        record = {
            "time": datetime(2025, 11, 1, 12, 34, 56, 789000, tzinfo=timezone.utc),
            "level": "INFO",
            "message": "Proxy selected",
            "module": "proxywhirl.rotator",
            "function": "select_proxy",
            "line": 145,
            "exception": None,
            "extra": {
                "request_id": "req-123",
                "operation": "proxy_selection",
                "proxy_url": "http://proxy1.example.com:8080",
            },
        }
        
        formatted = format_json_log(record)
        parsed = json.loads(formatted)
        
        assert parsed["request_id"] == "req-123"
        assert parsed["operation"] == "proxy_selection"
        assert parsed["proxy_url"] == "http://proxy1.example.com:8080"

    def test_format_json_with_exception(self) -> None:
        """Test JSON formatting with exception information."""
        try:
            raise ValueError("Test error")
        except ValueError as exc:
            record = {
                "time": datetime(2025, 11, 1, 12, 34, 56, 789000, tzinfo=timezone.utc),
                "level": "ERROR",
                "message": "Error occurred",
                "module": "test",
                "function": "test_func",
                "line": 42,
                "exception": exc,
                "extra": {},
            }
            
            formatted = format_json_log(record)
            parsed = json.loads(formatted)
            
            assert parsed["level"] == "ERROR"
            assert "exception" in parsed
            assert parsed["exception"]["type"] == "ValueError"
            assert parsed["exception"]["message"] == "Test error"

    def test_format_json_with_redaction(self) -> None:
        """Test JSON formatting with credential redaction."""
        record = {
            "time": datetime(2025, 11, 1, 12, 34, 56, 789000, tzinfo=timezone.utc),
            "level": "INFO",
            "message": "Auth attempt",
            "module": "test",
            "function": "test_func",
            "line": 42,
            "exception": None,
            "extra": {
                "username": "admin",
                "password": "secret123",
            },
        }
        
        formatted = format_json_log(record, redact=True)
        parsed = json.loads(formatted)
        
        assert parsed["username"] == "admin"
        assert parsed["password"] == "**REDACTED**"

    def test_format_json_unicode_handling(self) -> None:
        """Test JSON formatting with Unicode characters."""
        record = {
            "time": datetime(2025, 11, 1, 12, 34, 56, 789000, tzinfo=timezone.utc),
            "level": "INFO",
            "message": "???? ?? ???????? ?????????",
            "module": "test",
            "function": "test_func",
            "line": 42,
            "exception": None,
            "extra": {"key": "?"},
        }
        
        formatted = format_json_log(record)
        parsed = json.loads(formatted)
        
        assert "???? ??" in parsed["message"]
        assert parsed["key"] == "?"

    def test_format_json_produces_valid_json(self) -> None:
        """Test that formatted output is always valid JSON."""
        record = {
            "time": datetime(2025, 11, 1, 12, 34, 56, 789000, tzinfo=timezone.utc),
            "level": "INFO",
            "message": "Test",
            "module": "test",
            "function": "test_func",
            "line": 42,
            "exception": None,
            "extra": {},
        }
        
        formatted = format_json_log(record)
        
        # Should not raise JSONDecodeError
        json.loads(formatted)


class TestFormatLogfmtLog:
    """Tests for logfmt formatting."""

    def test_format_minimal_logfmt_log(self) -> None:
        """Test logfmt formatting of minimal log record."""
        record = {
            "time": datetime(2025, 11, 1, 12, 34, 56, 789000, tzinfo=timezone.utc),
            "level": "INFO",
            "message": "Test message",
            "module": "test",
            "function": "test_func",
            "line": 42,
            "exception": None,
            "extra": {},
        }
        
        formatted = format_logfmt_log(record)
        
        assert 'level=INFO' in formatted
        assert 'message="Test message"' in formatted
        assert 'module=test' in formatted
        assert 'function=test_func' in formatted
        assert 'line=42' in formatted

    def test_format_logfmt_with_extra_fields(self) -> None:
        """Test logfmt formatting with extra context fields."""
        record = {
            "time": datetime(2025, 11, 1, 12, 34, 56, 789000, tzinfo=timezone.utc),
            "level": "INFO",
            "message": "Proxy selected",
            "module": "proxywhirl.rotator",
            "function": "select_proxy",
            "line": 145,
            "exception": None,
            "extra": {
                "request_id": "req-123",
                "operation": "proxy_selection",
            },
        }
        
        formatted = format_logfmt_log(record)
        
        assert 'request_id=req-123' in formatted
        assert 'operation=proxy_selection' in formatted

    def test_format_logfmt_quotes_values_with_spaces(self) -> None:
        """Test that logfmt quotes values containing spaces."""
        record = {
            "time": datetime(2025, 11, 1, 12, 34, 56, 789000, tzinfo=timezone.utc),
            "level": "INFO",
            "message": "Message with spaces",
            "module": "test",
            "function": "test_func",
            "line": 42,
            "exception": None,
            "extra": {},
        }
        
        formatted = format_logfmt_log(record)
        
        assert 'message="Message with spaces"' in formatted

    def test_format_logfmt_escapes_quotes(self) -> None:
        """Test that logfmt escapes quotes in values."""
        record = {
            "time": datetime(2025, 11, 1, 12, 34, 56, 789000, tzinfo=timezone.utc),
            "level": "INFO",
            "message": 'Message with "quotes"',
            "module": "test",
            "function": "test_func",
            "line": 42,
            "exception": None,
            "extra": {},
        }
        
        formatted = format_logfmt_log(record)
        
        # Quotes should be escaped
        assert r'\"' in formatted or "'" in formatted

    def test_format_logfmt_with_numeric_values(self) -> None:
        """Test logfmt formatting with numeric extra fields."""
        record = {
            "time": datetime(2025, 11, 1, 12, 34, 56, 789000, tzinfo=timezone.utc),
            "level": "INFO",
            "message": "Performance metric",
            "module": "test",
            "function": "test_func",
            "line": 42,
            "exception": None,
            "extra": {
                "duration_ms": 42.5,
                "count": 10,
            },
        }
        
        formatted = format_logfmt_log(record)
        
        assert 'duration_ms=42.5' in formatted
        assert 'count=10' in formatted

    def test_format_logfmt_unicode_handling(self) -> None:
        """Test logfmt formatting with Unicode characters."""
        record = {
            "time": datetime(2025, 11, 1, 12, 34, 56, 789000, tzinfo=timezone.utc),
            "level": "INFO",
            "message": "????",
            "module": "test",
            "function": "test_func",
            "line": 42,
            "exception": None,
            "extra": {},
        }
        
        formatted = format_logfmt_log(record)
        
        assert "????" in formatted

    def test_format_logfmt_with_redaction(self) -> None:
        """Test logfmt formatting with credential redaction."""
        record = {
            "time": datetime(2025, 11, 1, 12, 34, 56, 789000, tzinfo=timezone.utc),
            "level": "INFO",
            "message": "Auth attempt",
            "module": "test",
            "function": "test_func",
            "line": 42,
            "exception": None,
            "extra": {
                "username": "admin",
                "password": "secret123",
            },
        }
        
        formatted = format_logfmt_log(record, redact=True)
        
        assert 'username=admin' in formatted
        assert 'password="**REDACTED**"' in formatted or 'password=**REDACTED**' in formatted


class TestFormatterEdgeCases:
    """Tests for edge cases in formatters."""

    def test_format_with_none_values(self) -> None:
        """Test formatting with None values in extra fields."""
        record = {
            "time": datetime(2025, 11, 1, 12, 34, 56, 789000, tzinfo=timezone.utc),
            "level": "INFO",
            "message": "Test",
            "module": "test",
            "function": "test_func",
            "line": 42,
            "exception": None,
            "extra": {
                "nullable_field": None,
            },
        }
        
        # Should not raise errors
        json_formatted = format_json_log(record)
        logfmt_formatted = format_logfmt_log(record)
        
        assert json_formatted is not None
        assert logfmt_formatted is not None

    def test_format_with_empty_message(self) -> None:
        """Test formatting with empty message."""
        record = {
            "time": datetime(2025, 11, 1, 12, 34, 56, 789000, tzinfo=timezone.utc),
            "level": "INFO",
            "message": "",
            "module": "test",
            "function": "test_func",
            "line": 42,
            "exception": None,
            "extra": {},
        }
        
        # Should handle empty message gracefully
        json_formatted = format_json_log(record)
        logfmt_formatted = format_logfmt_log(record)
        
        parsed = json.loads(json_formatted)
        assert parsed["message"] == ""

    def test_format_with_large_extra_data(self) -> None:
        """Test formatting with large extra data structures."""
        record = {
            "time": datetime(2025, 11, 1, 12, 34, 56, 789000, tzinfo=timezone.utc),
            "level": "INFO",
            "message": "Large data",
            "module": "test",
            "function": "test_func",
            "line": 42,
            "exception": None,
            "extra": {
                f"field_{i}": f"value_{i}" for i in range(100)
            },
        }
        
        # Should handle large data without errors
        json_formatted = format_json_log(record)
        parsed = json.loads(json_formatted)
        
        assert len(parsed.keys()) > 100
