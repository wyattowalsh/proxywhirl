"""Unit tests for logging default changes (ProxyConfiguration + utils.configure_logging).

Tests cover:
- ProxyConfiguration default log_format is "auto"
- ProxyConfiguration default log_level is "WARNING"
- log_format="auto" TTY detection in configure_logging()
- Backward compatibility with explicit log_format="json" and log_format="text"
"""

from __future__ import annotations

from unittest.mock import patch

from proxywhirl.models.core import ProxyConfiguration
from proxywhirl.utils import configure_logging


class TestProxyConfigurationDefaults:
    """Test new default values on ProxyConfiguration."""

    def test_log_format_default_is_auto(self):
        """Default log_format should be 'auto'."""
        config = ProxyConfiguration()
        assert config.log_format == "auto"

    def test_log_level_default_is_warning(self):
        """Default log_level should be 'WARNING'."""
        config = ProxyConfiguration()
        assert config.log_level == "WARNING"

    def test_explicit_json_format(self):
        """Explicit log_format='json' is accepted."""
        config = ProxyConfiguration(log_format="json")
        assert config.log_format == "json"

    def test_explicit_text_format(self):
        """Explicit log_format='text' is accepted."""
        config = ProxyConfiguration(log_format="text")
        assert config.log_format == "text"

    def test_explicit_auto_format(self):
        """Explicit log_format='auto' is accepted."""
        config = ProxyConfiguration(log_format="auto")
        assert config.log_format == "auto"

    def test_explicit_info_level(self):
        """Explicit log_level='INFO' overrides default."""
        config = ProxyConfiguration(log_level="INFO")
        assert config.log_level == "INFO"


class TestConfigureLoggingAutoFormat:
    """Test configure_logging() handling of 'auto' format_type."""

    def test_auto_resolves_to_text_on_tty(self):
        """format_type='auto' resolves to 'text' when stderr is a TTY."""
        with patch("sys.stderr") as mock_stderr:
            mock_stderr.isatty.return_value = True
            # Should not raise — resolves to text format
            configure_logging(format_type="auto")

    def test_auto_resolves_to_json_on_non_tty(self):
        """format_type='auto' resolves to 'json' when stderr is not a TTY."""
        with patch("sys.stderr") as mock_stderr:
            mock_stderr.isatty.return_value = False
            # Should not raise — resolves to json format
            configure_logging(format_type="auto")

    def test_explicit_json_still_works(self):
        """format_type='json' works as before."""
        configure_logging(format_type="json")

    def test_explicit_text_still_works(self):
        """format_type='text' works as before."""
        configure_logging(format_type="text")
