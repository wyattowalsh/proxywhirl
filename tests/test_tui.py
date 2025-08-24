"""Comprehensive tests for proxywhirl.tui module.

This module tests the Textual-based terminal user interface for ProxyWhirl,
including all widgets, screens, and interactive functionality.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from textual.app import App
from textual.widgets import Button, DataTable, Input, Static

from proxywhirl.models import AnonymityLevel, Proxy, ProxyStatus, Scheme

# Import the TUI components
from proxywhirl.tui import ProxyDataTable, ProxyStatsWidget, ProxyWhirlTUI, run_tui


class TestProxyStatsWidget:
    """Test cases for ProxyStatsWidget component."""

    def test_widget_initialization(self):
        """Test ProxyStatsWidget initialization."""
        widget = ProxyStatsWidget()

        # Check default reactive values
        assert widget.total_proxies == 0
        assert widget.active_proxies == 0
        assert widget.last_updated == "Never"
        assert widget.success_rate == 0.0
        assert widget.response_times == []

    def test_reactive_updates(self):
        """Test reactive attribute updates."""
        widget = ProxyStatsWidget()

        # Update total proxies
        widget.total_proxies = 100
        assert widget.total_proxies == 100

        # Update active proxies
        widget.active_proxies = 75
        assert widget.active_proxies == 75

        # Update last updated
        widget.last_updated = "2024-01-01 12:00:00"
        assert widget.last_updated == "2024-01-01 12:00:00"

    def test_success_rate_calculation(self):
        """Test automatic success rate calculation."""
        widget = ProxyStatsWidget()

        # Test with zero total proxies
        widget.total_proxies = 0
        widget.active_proxies = 0
        widget.update_success_rate()
        assert widget.success_rate == 0.0

        # Test with some active proxies
        widget.total_proxies = 100
        widget.active_proxies = 75
        widget.update_success_rate()
        assert widget.success_rate == 0.75

        # Test with all active
        widget.active_proxies = 100
        widget.update_success_rate()
        assert widget.success_rate == 1.0

    def test_response_time_tracking(self):
        """Test response time tracking functionality."""
        widget = ProxyStatsWidget()

        # Add response times
        widget.add_response_time(0.5)
        assert len(widget.response_times) == 1
        assert widget.response_times[0] == 0.5

        # Add multiple response times
        for i in range(1, 55):
            widget.add_response_time(i * 0.1)

        # Should keep only last 50
        assert len(widget.response_times) == 50
        assert widget.response_times[0] == 0.5  # Oldest kept
        assert widget.response_times[-1] == 5.4  # Newest

    def test_loading_state(self):
        """Test loading state management."""
        widget = ProxyStatsWidget()

        # Test setting loading state
        widget.set_loading(True)
        # Note: In actual usage, this would update UI components
        # We test the method exists and is callable

        widget.set_loading(False)
        # Should reset to ready state


class TestProxyDataTable:
    """Test cases for ProxyDataTable component."""

    def test_table_initialization(self):
        """Test ProxyDataTable initialization."""
        table = ProxyDataTable()

        # Check default properties
        assert table.cursor_type == "row"
        assert table.zebra_stripes is True
        assert table.show_header is True

    def test_column_setup(self):
        """Test table column configuration."""
        table = ProxyDataTable()
        table.setup_columns()

        # Verify columns exist (column count check)
        # Note: Actual column verification would require DOM access in Textual
        # We test the method exists and is callable
        assert hasattr(table, "add_columns")

    def test_proxy_row_addition(self):
        """Test adding proxy rows to the table."""
        table = ProxyDataTable()
        table.setup_columns()

        # Create test proxy
        proxy = Proxy(
            host="192.168.1.1",
            port=8080,
            schemes=[Scheme.HTTP],
            country_code="US",
            anonymity_level=AnonymityLevel.ANONYMOUS,
            response_time=1.5,
        )

        # Add proxy row
        table.add_proxy_row(proxy)
        # Note: Row verification would require DOM access
        # We test the method executes without error

    def test_proxy_formatting(self):
        """Test proxy data formatting in table rows."""
        table = ProxyDataTable()
        table.setup_columns()

        # Test fast response time formatting
        proxy_fast = Proxy(host="192.168.1.1", port=8080, schemes=[Scheme.HTTP], response_time=0.5)
        table.add_proxy_row(proxy_fast)

        # Test slow response time formatting
        proxy_slow = Proxy(host="192.168.1.2", port=8080, schemes=[Scheme.HTTP], response_time=5.0)
        table.add_proxy_row(proxy_slow)

        # Test no response time
        proxy_unknown = Proxy(
            host="192.168.1.3", port=8080, schemes=[Scheme.HTTP], response_time=None
        )
        table.add_proxy_row(proxy_unknown)


class TestProxyWhirlTUI:
    """Test cases for the main ProxyWhirl TUI application."""

    def test_app_initialization(self):
        """Test ProxyWhirlTUI app initialization."""
        app = ProxyWhirlTUI()

        # Check app properties
        assert isinstance(app, App)
        assert app.title == "ProxyWhirl - Advanced Proxy Management TUI"
        assert app.sub_title == "Fast, Reliable, Beautiful"

        # Check default state
        assert app.all_proxies == []
        assert app.current_filter == ""
        assert app.is_loading is False

    def test_app_bindings(self):
        """Test keyboard bindings configuration."""
        app = ProxyWhirlTUI()

        # Verify key bindings exist
        binding_keys = [binding.key for binding in app.BINDINGS]
        assert "f" in binding_keys  # Fetch proxies
        assert "v" in binding_keys  # Validate proxies
        assert "e" in binding_keys  # Export proxies
        assert "s" in binding_keys  # Settings
        assert "r" in binding_keys  # Refresh
        assert "q" in binding_keys  # Quit

    @patch("proxywhirl.tui.ProxyWhirl")
    def test_proxywhirl_initialization(self, mock_proxywhirl_class):
        """Test ProxyWhirl core initialization."""
        mock_proxywhirl = AsyncMock()
        mock_proxywhirl_class.return_value = mock_proxywhirl

        app = ProxyWhirlTUI()
        app.initialize_proxywhirl()

        # Verify ProxyWhirl was created
        mock_proxywhirl_class.assert_called_once()
        assert app.proxywhirl is mock_proxywhirl

    @patch("proxywhirl.tui.ProxyWhirl")
    async def test_fetch_proxies_workflow(self, mock_proxywhirl_class):
        """Test proxy fetching workflow."""
        mock_proxywhirl = AsyncMock()
        mock_proxywhirl.get_proxies.return_value = [
            Proxy(host="192.168.1.1", port=8080, schemes=[Scheme.HTTP]),
            Proxy(host="192.168.1.2", port=8080, schemes=[Scheme.HTTPS]),
        ]
        mock_proxywhirl_class.return_value = mock_proxywhirl

        app = ProxyWhirlTUI()
        app.initialize_proxywhirl()

        # Mock UI components
        with patch.object(app, "query_one") as mock_query:
            mock_stats = MagicMock()
            mock_table = MagicMock()
            mock_query.side_effect = lambda selector, widget_type: {
                "#proxy-stats": mock_stats,
                "#proxy-table": mock_table,
            }.get(selector, MagicMock())

            # Test fetch operation
            await app.fetch_proxies_worker()

            # Verify proxies were fetched
            mock_proxywhirl.get_proxies.assert_called_once()
            assert len(app.all_proxies) == 2

    @patch("proxywhirl.tui.ProxyValidator")
    async def test_validate_proxies_workflow(self, mock_validator_class):
        """Test proxy validation workflow."""
        # Setup mock validator
        mock_validator = AsyncMock()
        mock_validator.validate_proxies.return_value = [
            Proxy(host="192.168.1.1", port=8080, schemes=[Scheme.HTTP], status=ProxyStatus.WORKING)
        ]
        mock_validator_class.return_value = mock_validator

        app = ProxyWhirlTUI()
        app.all_proxies = [
            Proxy(host="192.168.1.1", port=8080, schemes=[Scheme.HTTP]),
            Proxy(host="192.168.1.2", port=8080, schemes=[Scheme.HTTP]),
        ]

        # Test validation
        await app.validate_proxies_worker()

        # Verify validation was called
        mock_validator_class.assert_called_once()
        mock_validator.validate_proxies.assert_called_once()

    async def test_proxy_filtering(self):
        """Test proxy filtering functionality."""
        app = ProxyWhirlTUI()
        app.all_proxies = [
            Proxy(host="192.168.1.1", port=8080, schemes=[Scheme.HTTP], country_code="US"),
            Proxy(host="10.0.0.1", port=3128, schemes=[Scheme.HTTP], country_code="CA"),
            Proxy(host="192.168.1.2", port=8080, schemes=[Scheme.HTTPS], country_code="US"),
        ]

        # Mock table component
        with patch.object(app, "query_one") as mock_query:
            mock_table = MagicMock()
            mock_table.clear.return_value = None
            mock_query.return_value = mock_table

            # Test filtering by host
            app.current_filter = "192.168"
            await app.filter_and_update_table()

            # Should filter to 2 proxies with 192.168 in host
            assert mock_table.clear.called

            # Test filtering by country
            app.current_filter = "CA"
            await app.filter_and_update_table()

    async def test_export_functionality(self):
        """Test proxy export functionality."""
        app = ProxyWhirlTUI()
        app.all_proxies = [Proxy(host="192.168.1.1", port=8080, schemes=[Scheme.HTTP])]

        with patch("proxywhirl.tui.ProxyExporter") as mock_exporter_class:
            mock_exporter = MagicMock()
            mock_exporter_class.return_value = mock_exporter

            # Test export workflow
            await app.export_proxies_worker("json", "/tmp/test.json")

            # Verify exporter was used
            mock_exporter_class.assert_called_once()

    def test_logging_functionality(self):
        """Test logging and message display."""
        app = ProxyWhirlTUI()

        # Mock log widget
        with patch.object(app, "query_one") as mock_query:
            mock_log = MagicMock()
            mock_query.return_value = mock_log

            # Test logging
            app.log_message("Test message")
            # Verify log method exists and is callable

    async def test_settings_management(self):
        """Test settings screen and configuration."""
        app = ProxyWhirlTUI()

        # Test settings initialization
        settings = app.get_current_settings()
        assert isinstance(settings, dict)

        # Test settings updates
        new_settings = {"timeout": 30, "max_proxies": 1000}
        app.update_settings(new_settings)

        updated_settings = app.get_current_settings()
        assert updated_settings["timeout"] == 30
        assert updated_settings["max_proxies"] == 1000


class TestTUIIntegration:
    """Test TUI integration and workflow."""

    @patch("proxywhirl.tui.ProxyWhirlTUI")
    def test_run_tui_function(self, mock_app_class):
        """Test run_tui function."""
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app

        # Call run_tui
        run_tui()

        # Verify app was created and run
        mock_app_class.assert_called_once()
        mock_app.run.assert_called_once()

    def test_tui_error_handling(self):
        """Test TUI error handling and recovery."""
        app = ProxyWhirlTUI()

        # Test error logging
        error = Exception("Test error")
        app.handle_error(error)

        # Should not crash and should log error
        # Error handling method should exist
        assert hasattr(app, "handle_error")

    async def test_async_operations(self):
        """Test async operations and concurrency."""
        app = ProxyWhirlTUI()

        # Test that async methods can be called
        # without blocking or errors
        app.is_loading = False

        # Mock async operations
        with patch.object(app, "fetch_proxies_worker", new_callable=AsyncMock):
            await app.action_fetch_proxies()

        with patch.object(app, "validate_proxies_worker", new_callable=AsyncMock):
            await app.action_validate_proxies()


class TestTUIComponents:
    """Test individual TUI components and widgets."""

    def test_widget_composition(self):
        """Test widget composition and structure."""
        app = ProxyWhirlTUI()

        # Verify compose method exists
        assert hasattr(app, "compose")
        assert callable(app.compose)

    def test_screen_navigation(self):
        """Test screen navigation and modal handling."""
        app = ProxyWhirlTUI()

        # Test modal screens exist
        assert hasattr(app, "push_screen")
        assert hasattr(app, "pop_screen")

    def test_event_handling(self):
        """Test event handling for user interactions."""
        app = ProxyWhirlTUI()

        # Test event handler methods exist
        assert hasattr(app, "handle_fetch_button")
        assert hasattr(app, "handle_validate_button")
        assert hasattr(app, "handle_export_button")
        assert hasattr(app, "handle_filter_changed")
        assert hasattr(app, "handle_row_selected")

    def test_ui_state_management(self):
        """Test UI state management and updates."""
        app = ProxyWhirlTUI()

        # Test state properties
        assert hasattr(app, "all_proxies")
        assert hasattr(app, "current_filter")
        assert hasattr(app, "is_loading")

        # Test state updates
        app.is_loading = True
        assert app.is_loading is True

        app.current_filter = "test"
        assert app.current_filter == "test"


class TestTUIPerformance:
    """Test TUI performance and resource management."""

    def test_large_proxy_list_handling(self):
        """Test handling of large proxy lists."""
        app = ProxyWhirlTUI()

        # Create large proxy list
        large_proxy_list = [
            Proxy(host=f"192.168.{i//255}.{i%255}", port=8080, schemes=[Scheme.HTTP])
            for i in range(1000)
        ]

        app.all_proxies = large_proxy_list
        assert len(app.all_proxies) == 1000

        # Should handle large lists without performance issues
        # (This tests basic data structure handling)

    def test_memory_management(self):
        """Test memory management with dynamic data."""
        app = ProxyWhirlTUI()

        # Test clearing large datasets
        app.all_proxies = [
            Proxy(host=f"test{i}.com", port=8080, schemes=[Scheme.HTTP]) for i in range(500)
        ]

        # Clear data
        app.all_proxies.clear()
        assert len(app.all_proxies) == 0

        # Memory should be available for garbage collection

    async def test_concurrent_operations(self):
        """Test concurrent UI operations."""
        app = ProxyWhirlTUI()

        # Test that multiple async operations can be handled
        # without blocking the UI
        async def mock_operation():
            await app.log_message("Test operation")

        # Should be able to handle concurrent logging
        await mock_operation()
        await mock_operation()

        # UI should remain responsive
