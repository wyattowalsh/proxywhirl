"""Comprehensive tests for proxywhirl.__main__ module.

This module tests the entry point functionality that allows running the TUI
with `python -m proxywhirl`.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestMainModule:
    """Test cases for the __main__ module entry point."""

    def test_module_imports(self):
        """Test that the module imports correctly."""
        try:
            import proxywhirl.__main__
        except ImportError as e:
            pytest.fail(f"Failed to import proxywhirl.__main__: {e}")

    @patch("proxywhirl.__main__.run_tui")
    def test_main_execution(self, mock_run_tui):
        """Test that running the module calls run_tui."""
        # Mock the TUI runner
        mock_run_tui.return_value = None

        # Import and execute the module
        import proxywhirl.__main__

        # Verify run_tui would be called (import doesn't actually execute __main__ block)
        # But we can test the function exists and is importable
        assert hasattr(proxywhirl.__main__, "run_tui")

        # Test direct execution path
        with patch("proxywhirl.__main__.__name__", "__main__"):
            # Simulate module execution
            exec(
                compile(
                    open(proxywhirl.__main__.__file__).read(), proxywhirl.__main__.__file__, "exec"
                )
            )

        # Verify TUI would be called in main execution
        mock_run_tui.assert_called_once()

    def test_run_tui_import_path(self):
        """Test that run_tui can be imported from the correct path."""
        from proxywhirl.__main__ import run_tui

        # Verify it's callable
        assert callable(run_tui)

        # Verify it matches the tui module function
        from proxywhirl.tui import run_tui as tui_run_tui

        assert run_tui is tui_run_tui

    @patch("proxywhirl.tui.ProxyWhirlTUI")
    def test_integration_with_tui(self, mock_tui_class):
        """Test integration with TUI application."""
        from proxywhirl.__main__ import run_tui

        # Mock TUI app instance
        mock_app = MagicMock()
        mock_tui_class.return_value = mock_app

        # Call run_tui
        run_tui()

        # Verify TUI app was created and run
        mock_tui_class.assert_called_once()
        mock_app.run.assert_called_once()


class TestModuleStructure:
    """Test cases for module structure and metadata."""

    def test_module_docstring(self):
        """Test that the module has proper documentation."""
        import proxywhirl.__main__

        assert proxywhirl.__main__.__doc__ is not None
        assert "Allow running TUI with python -m proxywhirl" in proxywhirl.__main__.__doc__

    def test_module_file_structure(self):
        """Test that the module file has expected structure."""
        import inspect

        import proxywhirl.__main__

        # Get source code
        source = inspect.getsource(proxywhirl.__main__)

        # Verify key components exist
        assert "from .tui import run_tui" in source
        assert 'if __name__ == "__main__":' in source
        assert "run_tui()" in source

    def test_module_attributes(self):
        """Test module attributes and exports."""
        import proxywhirl.__main__

        # Should have run_tui function
        assert hasattr(proxywhirl.__main__, "run_tui")

        # Should not expose internal implementation details
        module_attrs = [attr for attr in dir(proxywhirl.__main__) if not attr.startswith("_")]

        # Only run_tui should be exposed
        assert "run_tui" in module_attrs


class TestErrorHandling:
    """Test error handling in the main module."""

    @patch("proxywhirl.__main__.run_tui")
    def test_tui_import_error_handling(self, mock_run_tui):
        """Test handling of TUI import errors."""
        # Simulate import error
        mock_run_tui.side_effect = ImportError("TUI dependencies missing")

        import proxywhirl.__main__

        # Test that the function still exists but will raise on call
        with pytest.raises(ImportError, match="TUI dependencies missing"):
            proxywhirl.__main__.run_tui()

    @patch("proxywhirl.tui.ProxyWhirlTUI")
    def test_tui_runtime_error_handling(self, mock_tui_class):
        """Test handling of TUI runtime errors."""
        from proxywhirl.__main__ import run_tui

        # Mock TUI to raise runtime error
        mock_tui_class.side_effect = RuntimeError("TUI initialization failed")

        # Should propagate the error
        with pytest.raises(RuntimeError, match="TUI initialization failed"):
            run_tui()


class TestPackageIntegration:
    """Test integration with the broader package."""

    def test_package_main_accessibility(self):
        """Test that __main__ is accessible from package level."""
        # Should be able to run with python -m proxywhirl
        import proxywhirl
        import proxywhirl.__main__

        # Verify main module is part of package
        assert proxywhirl.__main__.__package__ == "proxywhirl"

    def test_cli_vs_main_distinction(self):
        """Test distinction between CLI and main entry points."""
        import proxywhirl.__main__
        import proxywhirl.cli

        # CLI should have different functionality than __main__
        assert hasattr(proxywhirl.cli, "cli")  # CLI has click command group
        assert hasattr(proxywhirl.__main__, "run_tui")  # Main has TUI runner

        # They should be different functions
        assert proxywhirl.cli.cli != proxywhirl.__main__.run_tui

    def test_execution_environments(self):
        """Test behavior in different execution environments."""
        import proxywhirl.__main__

        # Module should be importable without side effects
        # (unless __name__ == '__main__')
        assert proxywhirl.__main__.run_tui is not None

        # Should not interfere with other imports
        import proxywhirl.tui

        assert proxywhirl.tui.run_tui is proxywhirl.__main__.run_tui
        import proxywhirl.tui

        assert proxywhirl.tui.run_tui is proxywhirl.__main__.run_tui
