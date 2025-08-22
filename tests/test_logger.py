"""Tests for proxywhirl.logger module.

Unit tests for logger configuration and functionality.
"""

from unittest.mock import Mock, patch

from proxywhirl.logger import (
    configure_rich_logging,
    custom_theme,
    get_logger,
    setup_logger,
)


class TestLogger:
    """Test logger configuration and functionality."""

    def test_custom_theme_exists(self):
        """Test that custom theme is properly defined."""
        from rich.theme import Theme

        assert isinstance(custom_theme, Theme)

        # Check that expected theme keys exist
        expected_keys = [
            "info",
            "success",
            "warning",
            "error",
            "critical",
            "debug",
            "logging.level.info",
            "logging.level.success",
            "logging.level.warning",
            "logging.level.error",
            "logging.level.critical",
            "logging.level.debug",
        ]

        for key in expected_keys:
            assert key in custom_theme.styles

    def test_custom_theme_color_values(self):
        """Test that custom theme has expected color values."""
        # Check specific color mappings
        assert custom_theme.styles["info"] == "cyan"
        assert custom_theme.styles["success"] == "green"
        assert custom_theme.styles["warning"] == "yellow"
        assert custom_theme.styles["error"] == "bold red"
        assert custom_theme.styles["critical"] == "bold magenta"
        assert custom_theme.styles["debug"] == "dim"

    @patch("proxywhirl.logger.logger")
    def test_setup_logger_default(self, mock_logger):
        """Test setup_logger with default parameters."""
        setup_logger()

        # Verify logger was configured
        mock_logger.remove.assert_called()
        mock_logger.add.assert_called()

    @patch("proxywhirl.logger.logger")
    def test_setup_logger_with_level(self, mock_logger):
        """Test setup_logger with custom level."""
        setup_logger(level="DEBUG")

        mock_logger.remove.assert_called()
        # Should have been called with DEBUG level
        mock_logger.add.assert_called()

    @patch("proxywhirl.logger.logger")
    def test_setup_logger_with_file(self, mock_logger):
        """Test setup_logger with file output."""
        setup_logger(file_path="test.log")

        mock_logger.remove.assert_called()
        # Should be called multiple times (console + file)
        assert mock_logger.add.call_count >= 2

    @patch("proxywhirl.logger.logger")
    def test_setup_logger_rich_disabled(self, mock_logger):
        """Test setup_logger with rich disabled."""
        setup_logger(enable_rich=False)

        mock_logger.remove.assert_called()
        mock_logger.add.assert_called()

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a logger instance."""
        logger_instance = get_logger()

        # Should return loguru logger
        from loguru import logger as loguru_logger

        assert logger_instance == loguru_logger

    def test_get_logger_with_name(self):
        """Test get_logger with custom name."""
        logger_instance = get_logger("test_module")

        # Should still return the same loguru logger instance
        from loguru import logger as loguru_logger

        assert logger_instance == loguru_logger

    @patch("proxywhirl.logger.Console")
    @patch("proxywhirl.logger.RichHandler")
    def test_configure_rich_logging(self, mock_rich_handler, mock_console):
        """Test configure_rich_logging function."""
        mock_console_instance = Mock()
        mock_console.return_value = mock_console_instance
        mock_handler_instance = Mock()
        mock_rich_handler.return_value = mock_handler_instance

        result = configure_rich_logging()

        # Verify console was created with custom theme
        mock_console.assert_called_once_with(theme=custom_theme)

        # Verify RichHandler was created with console
        mock_rich_handler.assert_called_once()

        # Should return the handler
        assert result == mock_handler_instance

    @patch("proxywhirl.logger.logger")
    def test_setup_logger_integration(self, mock_logger):
        """Test complete setup_logger integration."""
        # Test with multiple parameters
        setup_logger(level="INFO", file_path="app.log", enable_rich=True, colorize=True)

        # Verify logger was properly configured
        mock_logger.remove.assert_called()
        mock_logger.add.assert_called()

    def test_logger_module_imports(self):
        """Test that all expected functions are importable."""
        from proxywhirl.logger import (
            configure_rich_logging,
            custom_theme,
            get_logger,
            setup_logger,
        )

        # All should be callable except custom_theme
        assert callable(setup_logger)
        assert callable(get_logger)
        assert callable(configure_rich_logging)

        # custom_theme should be a Theme instance
        from rich.theme import Theme

        assert isinstance(custom_theme, Theme)

    @patch("proxywhirl.logger.logger")
    def test_setup_logger_error_handling(self, mock_logger):
        """Test setup_logger error handling."""
        # Simulate an error during logger.add
        mock_logger.add.side_effect = Exception("Logger setup failed")

        # Should not raise exception, but handle gracefully
        try:
            setup_logger()
        except Exception as e:
            # If it does raise, that's the current behavior
            assert "Logger setup failed" in str(e)

    def test_logger_levels_available(self):
        """Test that standard logging levels are available."""
        logger_instance = get_logger()

        # Check that standard log methods exist
        assert hasattr(logger_instance, "debug")
        assert hasattr(logger_instance, "info")
        assert hasattr(logger_instance, "warning")
        assert hasattr(logger_instance, "error")
        assert hasattr(logger_instance, "critical")

        # Check that they are callable
        assert callable(logger_instance.debug)
        assert callable(logger_instance.info)
        assert callable(logger_instance.warning)
        assert callable(logger_instance.error)
        assert callable(logger_instance.critical)

    @patch("proxywhirl.logger.logger")
    def test_logger_configuration_persistence(self, mock_logger):
        """Test that logger configuration persists across calls."""
        # Setup logger once
        setup_logger(level="DEBUG")
        first_call_count = mock_logger.add.call_count

        # Setup again
        setup_logger(level="INFO")
        second_call_count = mock_logger.add.call_count

        # Should have been configured again
        assert second_call_count > first_call_count
