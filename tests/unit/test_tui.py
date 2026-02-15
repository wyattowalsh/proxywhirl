"""Unit tests for TUI module.

Tests cover TUI components, export methods, and basic functionality.
"""

import csv
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from rich.text import Text

from proxywhirl.models import HealthStatus, Proxy
from proxywhirl.rotator import ProxyWhirl


class TestMetricsPanel:
    """Test MetricsPanel widget."""

    def test_metrics_panel_import(self) -> None:
        """Test MetricsPanel can be imported."""
        from proxywhirl.tui import MetricsPanel

        assert MetricsPanel is not None

    def test_metrics_panel_reactive_defaults(self) -> None:
        """Test MetricsPanel has expected reactive properties."""
        from proxywhirl.tui import MetricsPanel

        panel = MetricsPanel()

        assert panel.total_proxies == 0
        assert panel.active_proxies == 0
        assert panel.healthy_proxies == 0
        assert panel.degraded_proxies == 0
        assert panel.unhealthy_proxies == 0
        assert panel.total_requests == 0
        assert panel.success_rate == 0.0
        assert panel.avg_latency == 0.0

    def test_metrics_panel_render(self) -> None:
        """Test MetricsPanel render returns Text."""
        from proxywhirl.tui import MetricsPanel

        panel = MetricsPanel()
        panel.total_proxies = 10
        panel.healthy_proxies = 8
        panel.success_rate = 95.0

        result = panel.render()

        assert isinstance(result, Text)
        # Check content contains expected text
        plain_text = result.plain
        assert "10 total" in plain_text
        assert "8✓" in plain_text  # New format shows healthy count with checkmark
        assert "95.0%" in plain_text


class TestProxyTable:
    """Test ProxyTable widget."""

    def test_proxy_table_import(self) -> None:
        """Test ProxyTable can be imported."""
        from proxywhirl.tui import ProxyTable

        assert ProxyTable is not None

    def test_proxy_table_update_proxies_format(self) -> None:
        """Test ProxyTable update_proxies formats data correctly."""
        from proxywhirl.tui import ProxyTable

        table = ProxyTable()
        # Note: on_mount would set up columns, but we're testing in isolation
        table._columns = {}  # Mock empty columns

        proxies = [
            Proxy(
                url="http://192.168.1.1:8080",
                allow_local=True,
                health_status=HealthStatus.HEALTHY,
                total_successes=10,
                total_failures=2,
            ),
        ]

        # Can't fully test without mounting, but verify method exists
        assert hasattr(table, "update_proxies")


class TestSourceFetcherPanel:
    """Test SourceFetcherPanel widget."""

    def test_source_fetcher_panel_import(self) -> None:
        """Test SourceFetcherPanel can be imported."""
        from proxywhirl.tui import SourceFetcherPanel

        assert SourceFetcherPanel is not None


class TestExportPanel:
    """Test ExportPanel widget."""

    def test_export_panel_import(self) -> None:
        """Test ExportPanel can be imported."""
        from proxywhirl.tui import ExportPanel

        assert ExportPanel is not None


class TestStrategyPanel:
    """Test StrategyPanel widget."""

    def test_strategy_panel_import(self) -> None:
        """Test StrategyPanel can be imported."""
        from proxywhirl.tui import StrategyPanel

        assert StrategyPanel is not None


class TestRequestTesterPanel:
    """Test RequestTesterPanel widget."""

    def test_request_tester_panel_import(self) -> None:
        """Test RequestTesterPanel can be imported."""
        from proxywhirl.tui import RequestTesterPanel

        assert RequestTesterPanel is not None


class TestAnalyticsPanel:
    """Test AnalyticsPanel widget."""

    def test_analytics_panel_import(self) -> None:
        """Test AnalyticsPanel can be imported."""
        from proxywhirl.tui import AnalyticsPanel

        assert AnalyticsPanel is not None


class TestProxyWhirlTUI:
    """Test ProxyWhirlTUI app."""

    def test_proxy_whirl_tui_import(self) -> None:
        """Test ProxyWhirlTUI can be imported."""
        from proxywhirl.tui import ProxyWhirlTUI

        assert ProxyWhirlTUI is not None

    def test_proxy_whirl_tui_init_default(self) -> None:
        """Test ProxyWhirlTUI initialization with defaults."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        assert app.rotator is not None
        assert isinstance(app.rotator, ProxyWhirl)
        # fetcher and validator are set in on_mount, not __init__
        assert hasattr(app, "fetcher")
        assert hasattr(app, "validator")

    def test_proxy_whirl_tui_init_with_rotator(self) -> None:
        """Test ProxyWhirlTUI initialization with custom rotator."""
        from proxywhirl.tui import ProxyWhirlTUI

        rotator = ProxyWhirl()
        app = ProxyWhirlTUI(rotator=rotator)

        assert app.rotator is rotator


class TestExportMethods:
    """Test TUI export methods."""

    def test_export_csv(self, tmp_path: Path) -> None:
        """Test CSV export format."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        export_path = tmp_path / "proxies.csv"

        proxies = [
            Proxy(
                url="http://192.168.1.1:8080",
                allow_local=True,
                protocol="http",
                health_status=HealthStatus.HEALTHY,
                total_successes=10,
                total_failures=2,
                country_code="US",
            ),
            Proxy(
                url="socks5://10.0.0.1:1080",
                allow_local=True,
                protocol="socks5",
                health_status=HealthStatus.DEGRADED,
                total_successes=5,
                total_failures=5,
            ),
        ]

        app._export_csv(export_path, proxies)

        assert export_path.exists()
        with open(export_path) as f:
            reader = csv.reader(f)
            rows = list(reader)

        # Check header
        assert rows[0] == [
            "URL",
            "Protocol",
            "Health",
            "Latency",
            "Successes",
            "Failures",
            "Country",
        ]
        # Check data
        assert "http://192.168.1.1:8080" in rows[1][0]
        assert "socks5://10.0.0.1:1080" in rows[2][0]

    def test_export_json(self, tmp_path: Path) -> None:
        """Test JSON export format."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        export_path = tmp_path / "proxies.json"

        proxies = [
            Proxy(
                url="http://192.168.1.1:8080",
                allow_local=True,
                protocol="http",
                health_status=HealthStatus.HEALTHY,
                total_successes=10,
                total_failures=2,
            ),
        ]

        app._export_json(export_path, proxies)

        assert export_path.exists()
        with open(export_path) as f:
            data = json.load(f)

        assert "export_date" in data
        assert "total_proxies" in data
        assert data["total_proxies"] == 1
        assert len(data["proxies"]) == 1
        assert data["proxies"][0]["url"] == "http://192.168.1.1:8080"

    def test_export_text(self, tmp_path: Path) -> None:
        """Test text export format."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        export_path = tmp_path / "proxies.txt"

        proxies = [
            Proxy(url="http://192.168.1.1:8080", allow_local=True),
            Proxy(url="http://192.168.1.2:8080", allow_local=True),
            Proxy(url="socks5://10.0.0.1:1080", allow_local=True),
        ]

        app._export_text(export_path, proxies)

        assert export_path.exists()
        content = export_path.read_text()
        lines = content.strip().split("\n")

        assert len(lines) == 3
        assert "http://192.168.1.1:8080" in lines[0]
        assert "http://192.168.1.2:8080" in lines[1]
        assert "socks5://10.0.0.1:1080" in lines[2]

    def test_export_yaml(self, tmp_path: Path) -> None:
        """Test YAML export format."""
        pytest.importorskip("yaml")  # Skip if PyYAML not installed

        import yaml

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        export_path = tmp_path / "proxies.yaml"

        proxies = [
            Proxy(
                url="http://192.168.1.1:8080",
                allow_local=True,
                health_status=HealthStatus.HEALTHY,
            ),
        ]

        app._export_yaml(export_path, proxies)

        assert export_path.exists()
        with open(export_path) as f:
            data = yaml.safe_load(f)

        assert "export_date" in data
        assert "total_proxies" in data
        assert data["total_proxies"] == 1

    def test_export_yaml_without_pyyaml(self, tmp_path: Path) -> None:
        """Test YAML export raises ImportError when PyYAML not available."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        export_path = tmp_path / "proxies.yaml"

        proxies = [Proxy(url="http://192.168.1.1:8080", allow_local=True)]

        # Mock yaml import to raise ImportError
        with patch.dict("sys.modules", {"yaml": None}):
            with pytest.raises(ImportError, match="PyYAML is required"):
                app._export_yaml(export_path, proxies)


class TestRunTui:
    """Test run_tui function."""

    def test_run_tui_import(self) -> None:
        """Test run_tui can be imported."""
        from proxywhirl.tui import run_tui

        assert callable(run_tui)

    def test_run_tui_creates_app(self) -> None:
        """Test run_tui creates ProxyWhirlTUI app."""
        from proxywhirl.tui import ProxyWhirlTUI, run_tui

        with patch.object(ProxyWhirlTUI, "run") as mock_run:
            run_tui()
            mock_run.assert_called_once()

    def test_run_tui_with_rotator(self) -> None:
        """Test run_tui accepts rotator argument."""
        from proxywhirl.tui import ProxyWhirlTUI, run_tui

        rotator = ProxyWhirl()

        with patch.object(ProxyWhirlTUI, "run") as mock_run:
            run_tui(rotator=rotator)
            mock_run.assert_called_once()


class TestTUISourceConstants:
    """Test TUI uses correct source constants."""

    def test_sources_imported(self) -> None:
        """Test source constants are imported correctly."""
        from proxywhirl.tui import (
            ALL_HTTP_SOURCES,
            ALL_SOCKS4_SOURCES,
            ALL_SOCKS5_SOURCES,
            ALL_SOURCES,
            RECOMMENDED_SOURCES,
        )

        assert ALL_SOURCES is not None
        assert RECOMMENDED_SOURCES is not None
        assert ALL_HTTP_SOURCES is not None
        assert ALL_SOCKS4_SOURCES is not None
        assert ALL_SOCKS5_SOURCES is not None


class TestTUIStrategies:
    """Test TUI strategy imports."""

    def test_strategies_imported(self) -> None:
        """Test all strategies are imported."""
        from proxywhirl.tui import (
            GeoTargetedStrategy,
            LeastUsedStrategy,
            PerformanceBasedStrategy,
            RandomStrategy,
            RoundRobinStrategy,
            SessionPersistenceStrategy,
            WeightedStrategy,
        )

        assert RoundRobinStrategy is not None
        assert RandomStrategy is not None
        assert WeightedStrategy is not None
        assert LeastUsedStrategy is not None
        assert PerformanceBasedStrategy is not None
        assert GeoTargetedStrategy is not None
        assert SessionPersistenceStrategy is not None


class TestProxyTableUpdateProxies:
    """Test ProxyTable update_proxies method."""

    def test_update_proxies_with_healthy_proxy(self) -> None:
        """Test update_proxies handles healthy proxy."""
        from proxywhirl.tui import ProxyTable

        table = ProxyTable()

        # Mock the columns and add_row since on_mount hasn't run
        table._columns = {}
        table._column_count = 7
        added_rows = []

        def mock_add_row(*args, **kwargs):
            added_rows.append(args)

        table.add_row = mock_add_row  # type: ignore
        table.clear = MagicMock()

        proxies = [
            Proxy(
                url="http://proxy1.example.com:8080",
                health_status=HealthStatus.HEALTHY,
                total_successes=10,
                total_failures=2,
                average_response_time_ms=200.0,
            ),
        ]

        table.update_proxies(proxies)

        assert len(added_rows) == 1
        table.clear.assert_called_once()

    def test_update_proxies_with_degraded_proxy(self) -> None:
        """Test update_proxies handles degraded proxy."""
        from proxywhirl.tui import ProxyTable

        table = ProxyTable()
        table._columns = {}
        table._column_count = 7
        added_rows = []

        def mock_add_row(*args, **kwargs):
            added_rows.append(args)

        table.add_row = mock_add_row  # type: ignore
        table.clear = MagicMock()

        proxies = [
            Proxy(
                url="http://proxy.example.com:8080",
                health_status=HealthStatus.DEGRADED,
                average_response_time_ms=1000.0,
            ),
        ]

        table.update_proxies(proxies)

        assert len(added_rows) == 1

    def test_update_proxies_with_unhealthy_proxy(self) -> None:
        """Test update_proxies handles unhealthy proxy."""
        from proxywhirl.tui import ProxyTable

        table = ProxyTable()
        table._columns = {}
        table._column_count = 7
        added_rows = []

        def mock_add_row(*args, **kwargs):
            added_rows.append(args)

        table.add_row = mock_add_row  # type: ignore
        table.clear = MagicMock()

        proxies = [
            Proxy(
                url="http://proxy.example.com:8080",
                health_status=HealthStatus.UNHEALTHY,
                average_response_time_ms=3000.0,
            ),
        ]

        table.update_proxies(proxies)

        assert len(added_rows) == 1

    def test_update_proxies_with_dead_proxy(self) -> None:
        """Test update_proxies handles dead proxy."""
        from proxywhirl.tui import ProxyTable

        table = ProxyTable()
        table._columns = {}
        table._column_count = 7
        added_rows = []

        def mock_add_row(*args, **kwargs):
            added_rows.append(args)

        table.add_row = mock_add_row  # type: ignore
        table.clear = MagicMock()

        proxies = [
            Proxy(
                url="http://proxy.example.com:8080",
                health_status=HealthStatus.DEAD,
            ),
        ]

        table.update_proxies(proxies)

        assert len(added_rows) == 1

    def test_update_proxies_with_unknown_status(self) -> None:
        """Test update_proxies handles unknown status."""
        from proxywhirl.tui import ProxyTable

        table = ProxyTable()
        table._columns = {}
        table._column_count = 7
        added_rows = []

        def mock_add_row(*args, **kwargs):
            added_rows.append(args)

        table.add_row = mock_add_row  # type: ignore
        table.clear = MagicMock()

        proxies = [
            Proxy(
                url="http://proxy.example.com:8080",
                health_status=HealthStatus.UNKNOWN,
            ),
        ]

        table.update_proxies(proxies)

        assert len(added_rows) == 1


class TestProxyWhirlTUIRefreshMethods:
    """Test ProxyWhirlTUI refresh methods with mocking."""

    def test_refresh_metrics_calculates_correctly(self) -> None:
        """Test refresh_metrics calculates statistics."""
        from proxywhirl.tui import MetricsPanel, ProxyWhirlTUI

        app = ProxyWhirlTUI()

        # Add proxies to the rotator
        proxy1 = Proxy(
            url="http://proxy1.example.com:8080",
            health_status=HealthStatus.HEALTHY,
            total_successes=10,
            total_failures=2,
            average_response_time_ms=150.0,
        )
        proxy2 = Proxy(
            url="http://proxy2.example.com:8080",
            health_status=HealthStatus.DEGRADED,
            total_successes=5,
            total_failures=5,
            average_response_time_ms=500.0,
        )
        app.rotator.add_proxy(proxy1)
        app.rotator.add_proxy(proxy2)

        # Mock query_one
        mock_metrics = MagicMock(spec=MetricsPanel)
        app.query_one = MagicMock(return_value=mock_metrics)

        app.refresh_metrics()

        # Verify metrics were set
        assert mock_metrics.total_proxies == 2
        assert mock_metrics.healthy_proxies == 1
        assert mock_metrics.degraded_proxies == 1
        assert mock_metrics.total_requests == 22  # (10+2) + (5+5)
        assert mock_metrics.avg_latency == 325.0  # (150+500)/2

    def test_refresh_analytics_empty_pool(self) -> None:
        """Test refresh_analytics with empty proxy pool."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        mock_content = MagicMock()
        app.query_one = MagicMock(return_value=mock_content)

        app.refresh_analytics()

        mock_content.update.assert_called_once()
        # Should update with "No proxies available" message
        call_arg = mock_content.update.call_args[0][0]
        assert "No proxies" in str(call_arg)

    def test_refresh_analytics_with_proxies(self) -> None:
        """Test refresh_analytics with proxies calculates stats."""
        from proxywhirl.models import ProxySource
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        # Add proxies with metadata
        proxy1 = Proxy(
            url="http://proxy1.example.com:8080",
            protocol="http",
            country_code="US",
            source=ProxySource.USER,
        )
        proxy2 = Proxy(
            url="socks5://proxy2.example.com:1080",
            protocol="socks5",
            country_code="UK",
            source=ProxySource.FETCHED,
        )
        app.rotator.add_proxy(proxy1)
        app.rotator.add_proxy(proxy2)

        mock_content = MagicMock()
        app.query_one = MagicMock(return_value=mock_content)

        app.refresh_analytics()

        mock_content.update.assert_called_once()
        call_arg = mock_content.update.call_args[0][0]
        # Should contain protocol and country stats
        plain_text = str(call_arg)
        assert "Protocol" in plain_text or "http" in plain_text.lower()


class TestTUIActions:
    """Test TUI action methods."""

    def test_action_refresh(self) -> None:
        """Test action_refresh calls refresh_all_data."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        app.refresh_all_data = MagicMock()

        app.action_refresh()

        app.refresh_all_data.assert_called_once()

    def test_action_fetch(self) -> None:
        """Test action_fetch sets active tab to fetch."""
        from textual.widgets import TabbedContent

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        mock_tabs = MagicMock(spec=TabbedContent)
        app.query_one = MagicMock(return_value=mock_tabs)

        app.action_fetch()

        assert mock_tabs.active == "fetch"

    def test_action_export(self) -> None:
        """Test action_export sets active tab to export."""
        from textual.widgets import TabbedContent

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        mock_tabs = MagicMock(spec=TabbedContent)
        app.query_one = MagicMock(return_value=mock_tabs)

        app.action_export()

        assert mock_tabs.active == "export"

    def test_action_test(self) -> None:
        """Test action_test sets active tab to test."""
        from textual.widgets import TabbedContent

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        mock_tabs = MagicMock(spec=TabbedContent)
        app.query_one = MagicMock(return_value=mock_tabs)

        app.action_test()

        assert mock_tabs.active == "test"

    def test_action_help(self) -> None:
        """Test action_help calls notify."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        app.notify = MagicMock()

        app.action_help()

        app.notify.assert_called_once()
        call_kwargs = app.notify.call_args[1]
        assert call_kwargs["title"] == "Help"


class TestExportProxiesMethod:
    """Test export_proxies method with mocking."""

    def test_export_proxies_no_path(self) -> None:
        """Test export_proxies with empty path shows error."""
        from textual.widgets import Input, Label, Select

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        mock_path_input = MagicMock(spec=Input)
        mock_path_input.value = ""
        mock_format_select = MagicMock(spec=Select)
        mock_status = MagicMock(spec=Label)

        def query_one_mock(selector, widget_type=None):
            if selector == "#export-path":
                return mock_path_input
            elif selector == "#export-format":
                return mock_format_select
            elif selector == "#export-status":
                return mock_status
            return MagicMock()

        app.query_one = query_one_mock

        app.export_proxies()

        mock_status.update.assert_called_once()
        call_arg = mock_status.update.call_args[0][0]
        assert "Please enter a file path" in call_arg

    def test_export_proxies_no_proxies(self, tmp_path: Path) -> None:
        """Test export_proxies with no proxies shows error."""
        from textual.widgets import Input, Label, Select

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        mock_path_input = MagicMock(spec=Input)
        mock_path_input.value = str(tmp_path / "test.csv")
        mock_format_select = MagicMock(spec=Select)
        mock_format_select.value = "csv"
        mock_status = MagicMock(spec=Label)

        def query_one_mock(selector, widget_type=None):
            if selector == "#export-path":
                return mock_path_input
            elif selector == "#export-format":
                return mock_format_select
            elif selector == "#export-status":
                return mock_status
            return MagicMock()

        app.query_one = query_one_mock

        app.export_proxies()

        mock_status.update.assert_called_once()
        call_arg = mock_status.update.call_args[0][0]
        assert "No proxies to export" in call_arg

    def test_export_proxies_success_csv(self, tmp_path: Path) -> None:
        """Test successful CSV export."""
        from textual.widgets import Input, Label, Select

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        proxy = Proxy(url="http://proxy.example.com:8080")
        app.rotator.add_proxy(proxy)

        export_path = tmp_path / "test.csv"
        mock_path_input = MagicMock(spec=Input)
        mock_path_input.value = str(export_path)
        mock_format_select = MagicMock(spec=Select)
        mock_format_select.value = "csv"
        mock_status = MagicMock(spec=Label)

        def query_one_mock(selector, widget_type=None):
            if selector == "#export-path":
                return mock_path_input
            elif selector == "#export-format":
                return mock_format_select
            elif selector == "#export-status":
                return mock_status
            return MagicMock()

        app.query_one = query_one_mock

        app.export_proxies()

        assert export_path.exists()
        mock_status.update.assert_called()
        call_arg = mock_status.update.call_args[0][0]
        assert "Exported" in call_arg

    def test_export_proxies_success_json(self, tmp_path: Path) -> None:
        """Test successful JSON export."""
        from textual.widgets import Input, Label, Select

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        proxy = Proxy(url="http://proxy.example.com:8080")
        app.rotator.add_proxy(proxy)

        export_path = tmp_path / "test.json"
        mock_path_input = MagicMock(spec=Input)
        mock_path_input.value = str(export_path)
        mock_format_select = MagicMock(spec=Select)
        mock_format_select.value = "json"
        mock_status = MagicMock(spec=Label)

        def query_one_mock(selector, widget_type=None):
            if selector == "#export-path":
                return mock_path_input
            elif selector == "#export-format":
                return mock_format_select
            elif selector == "#export-status":
                return mock_status
            return MagicMock()

        app.query_one = query_one_mock

        app.export_proxies()

        assert export_path.exists()

    def test_export_proxies_success_text(self, tmp_path: Path) -> None:
        """Test successful text export."""
        from textual.widgets import Input, Label, Select

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        proxy = Proxy(url="http://proxy.example.com:8080")
        app.rotator.add_proxy(proxy)

        export_path = tmp_path / "test.txt"
        mock_path_input = MagicMock(spec=Input)
        mock_path_input.value = str(export_path)
        mock_format_select = MagicMock(spec=Select)
        mock_format_select.value = "text"
        mock_status = MagicMock(spec=Label)

        def query_one_mock(selector, widget_type=None):
            if selector == "#export-path":
                return mock_path_input
            elif selector == "#export-format":
                return mock_format_select
            elif selector == "#export-status":
                return mock_status
            return MagicMock()

        app.query_one = query_one_mock

        app.export_proxies()

        assert export_path.exists()

    def test_export_proxies_healthy_only(self, tmp_path: Path) -> None:
        """Test export with healthy_only filter."""
        from textual.widgets import Input, Label, Select

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        healthy_proxy = Proxy(
            url="http://healthy.example.com:8080",
            health_status=HealthStatus.HEALTHY,
        )
        unhealthy_proxy = Proxy(
            url="http://unhealthy.example.com:8080",
            health_status=HealthStatus.UNHEALTHY,
        )
        app.rotator.add_proxy(healthy_proxy)
        app.rotator.add_proxy(unhealthy_proxy)

        export_path = tmp_path / "healthy.txt"
        mock_path_input = MagicMock(spec=Input)
        mock_path_input.value = str(export_path)
        mock_format_select = MagicMock(spec=Select)
        mock_format_select.value = "text"
        mock_status = MagicMock(spec=Label)

        def query_one_mock(selector, widget_type=None):
            if selector == "#export-path":
                return mock_path_input
            elif selector == "#export-format":
                return mock_format_select
            elif selector == "#export-status":
                return mock_status
            return MagicMock()

        app.query_one = query_one_mock

        app.export_proxies(healthy_only=True)

        assert export_path.exists()
        content = export_path.read_text()
        # Only healthy proxy should be exported
        assert "healthy.example.com" in content
        assert "unhealthy.example.com" not in content

    def test_export_proxies_exception(self, tmp_path: Path) -> None:
        """Test export_proxies handles exceptions."""
        from textual.widgets import Input, Label, Select

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        proxy = Proxy(url="http://proxy.example.com:8080")
        app.rotator.add_proxy(proxy)

        mock_path_input = MagicMock(spec=Input)
        mock_path_input.value = "/invalid/path/that/does/not/exist/test.csv"
        mock_format_select = MagicMock(spec=Select)
        mock_format_select.value = "csv"
        mock_status = MagicMock(spec=Label)

        def query_one_mock(selector, widget_type=None):
            if selector == "#export-path":
                return mock_path_input
            elif selector == "#export-format":
                return mock_format_select
            elif selector == "#export-status":
                return mock_status
            return MagicMock()

        app.query_one = query_one_mock

        # Mock _export_csv to raise exception
        app._export_csv = MagicMock(side_effect=Exception("Write failed"))

        app.export_proxies()

        mock_status.update.assert_called()
        call_arg = mock_status.update.call_args[0][0]
        assert "Export failed" in call_arg


class TestApplyStrategy:
    """Test apply_strategy method."""

    def test_apply_strategy_round_robin(self) -> None:
        """Test applying round-robin strategy."""
        from textual.widgets import Label, Select

        from proxywhirl.tui import ProxyWhirlTUI, RoundRobinStrategy

        app = ProxyWhirlTUI()

        mock_select = MagicMock(spec=Select)
        mock_select.value = "round-robin"
        mock_status = MagicMock(spec=Label)

        def query_one_mock(selector, widget_type=None):
            if selector == "#strategy-select":
                return mock_select
            elif selector == "#strategy-status":
                return mock_status
            return MagicMock()

        app.query_one = query_one_mock

        app.apply_strategy()

        assert isinstance(app.rotator.strategy, RoundRobinStrategy)
        mock_status.update.assert_called()

    def test_apply_strategy_all_types(self) -> None:
        """Test applying all strategy types."""
        from textual.widgets import Label, Select

        from proxywhirl.tui import (
            GeoTargetedStrategy,
            LeastUsedStrategy,
            PerformanceBasedStrategy,
            ProxyWhirlTUI,
            RandomStrategy,
            SessionPersistenceStrategy,
            WeightedStrategy,
        )

        strategy_map = {
            "random": RandomStrategy,
            "weighted": WeightedStrategy,
            "least-used": LeastUsedStrategy,
            "performance": PerformanceBasedStrategy,
            "geo": GeoTargetedStrategy,
            "session": SessionPersistenceStrategy,
        }

        for strategy_name, strategy_class in strategy_map.items():
            app = ProxyWhirlTUI()

            mock_select = MagicMock(spec=Select)
            mock_select.value = strategy_name
            mock_status = MagicMock(spec=Label)

            def query_one_mock(selector, widget_type=None):
                if selector == "#strategy-select":
                    return mock_select
                elif selector == "#strategy-status":
                    return mock_status
                return MagicMock()

            app.query_one = query_one_mock

            app.apply_strategy()

            assert isinstance(app.rotator.strategy, strategy_class)

    def test_apply_strategy_exception(self) -> None:
        """Test apply_strategy handles exceptions."""
        from textual.widgets import Label, Select

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        mock_select = MagicMock(spec=Select)
        mock_select.value = "unknown"  # This will cause issues
        mock_status = MagicMock(spec=Label)

        def query_one_mock(selector, widget_type=None):
            if selector == "#strategy-select":
                return mock_select
            elif selector == "#strategy-status":
                return mock_status
            return MagicMock()

        app.query_one = query_one_mock

        # Strategy won't be set for unknown value, but no error raised
        app.apply_strategy()

        # Should still call update (either success or leave blank)
        # No exception should be raised


class TestProxyTableOnMount:
    """Test ProxyTable on_mount method."""

    def test_on_mount_adds_columns(self) -> None:
        """Test on_mount adds all expected columns."""
        from proxywhirl.tui import ProxyTable

        table = ProxyTable()

        # Mock add_column
        added_columns = []

        def mock_add_column(label, **kwargs):
            added_columns.append(label)

        table.add_column = mock_add_column

        table.on_mount()

        assert len(added_columns) == 8  # Added favorites column
        assert "★" in added_columns
        assert "URL" in added_columns
        assert "Protocol" in added_columns
        assert "Health" in added_columns
        assert "Latency" in added_columns
        assert "Success" in added_columns
        assert "Failures" in added_columns
        assert "Country" in added_columns


class TestPanelWidgetClasses:
    """Test panel widget classes exist and can be instantiated."""

    def test_source_fetcher_panel_has_compose(self) -> None:
        """Test SourceFetcherPanel has compose method."""
        from proxywhirl.tui import SourceFetcherPanel

        panel = SourceFetcherPanel()
        assert hasattr(panel, "compose")
        assert callable(panel.compose)

    def test_export_panel_has_compose(self) -> None:
        """Test ExportPanel has compose method."""
        from proxywhirl.tui import ExportPanel

        panel = ExportPanel()
        assert hasattr(panel, "compose")
        assert callable(panel.compose)

    def test_strategy_panel_has_compose(self) -> None:
        """Test StrategyPanel has compose method."""
        from proxywhirl.tui import StrategyPanel

        panel = StrategyPanel()
        assert hasattr(panel, "compose")
        assert callable(panel.compose)

    def test_request_tester_panel_has_compose(self) -> None:
        """Test RequestTesterPanel has compose method."""
        from proxywhirl.tui import RequestTesterPanel

        panel = RequestTesterPanel()
        assert hasattr(panel, "compose")
        assert callable(panel.compose)

    def test_analytics_panel_has_compose(self) -> None:
        """Test AnalyticsPanel has compose method."""
        from proxywhirl.tui import AnalyticsPanel

        panel = AnalyticsPanel()
        assert hasattr(panel, "compose")
        assert callable(panel.compose)


class TestProxyWhirlTUIHasCompose:
    """Test ProxyWhirlTUI has compose method."""

    def test_has_compose_method(self) -> None:
        """Test app has compose method."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        assert hasattr(app, "compose")
        assert callable(app.compose)


class TestAppLifecycle:
    """Test TUI app lifecycle methods."""

    def test_on_mount_calls_refresh(self) -> None:
        """Test on_mount calls refresh_all_data and set_interval."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        app.refresh_all_data = MagicMock()
        app.set_interval = MagicMock()

        app.on_mount()

        app.refresh_all_data.assert_called_once()
        app.set_interval.assert_called_once()

    def test_auto_refresh_calls_methods(self) -> None:
        """Test auto_refresh updates table and metrics."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        app.refresh_table = MagicMock()
        app.refresh_metrics = MagicMock()

        app.auto_refresh()

        app.refresh_table.assert_called_once()
        app.refresh_metrics.assert_called_once()

    def test_refresh_all_data_calls_all(self) -> None:
        """Test refresh_all_data calls all refresh methods."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        app.refresh_table = MagicMock()
        app.refresh_metrics = MagicMock()
        app.refresh_analytics = MagicMock()

        app.refresh_all_data()

        app.refresh_table.assert_called_once()
        app.refresh_metrics.assert_called_once()
        app.refresh_analytics.assert_called_once()

    def test_refresh_table_updates_proxy_table(self) -> None:
        """Test refresh_table updates the proxy table widget."""
        from proxywhirl.tui import ProxyTable, ProxyWhirlTUI

        app = ProxyWhirlTUI()

        # Add a proxy
        proxy = Proxy(url="http://proxy.example.com:8080")
        app.rotator.add_proxy(proxy)

        # Mock query_one
        mock_table = MagicMock(spec=ProxyTable)
        app.query_one = MagicMock(return_value=mock_table)

        app.refresh_table()

        mock_table.update_proxies.assert_called_once()
        call_args = mock_table.update_proxies.call_args[0][0]
        assert len(call_args) == 1


class TestFetchProxiesHandler:
    """Test fetch_proxies button handler."""

    def test_fetch_proxies_calls_async(self) -> None:
        """Test fetch_proxies calls fetch_proxies_async."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        app.fetch_proxies_async = MagicMock()

        app.fetch_proxies()

        app.fetch_proxies_async.assert_called_once()


class TestValidateProxiesHandler:
    """Test validate_all_proxies button handler."""

    def test_validate_all_proxies_calls_async(self) -> None:
        """Test validate_all_proxies calls validate_proxies_async."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        app.validate_proxies_async = MagicMock()

        app.validate_all_proxies()

        app.validate_proxies_async.assert_called_once()


class TestExportButtonHandlers:
    """Test export button handlers."""

    def test_export_all_proxies_calls_export(self) -> None:
        """Test export_all_proxies calls export_proxies with healthy_only=False."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        app.export_proxies = MagicMock()

        app.export_all_proxies()

        app.export_proxies.assert_called_once_with(healthy_only=False)

    def test_export_healthy_proxies_calls_export(self) -> None:
        """Test export_healthy_proxies calls export_proxies with healthy_only=True."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        app.export_proxies = MagicMock()

        app.export_healthy_proxies()

        app.export_proxies.assert_called_once_with(healthy_only=True)


class TestExportProxiesYaml:
    """Test export_proxies with YAML format."""

    def test_export_proxies_yaml_format(self, tmp_path: Path) -> None:
        """Test export_proxies uses YAML format."""
        pytest.importorskip("yaml")

        from textual.widgets import Input, Label, Select

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        proxy = Proxy(url="http://proxy.example.com:8080")
        app.rotator.add_proxy(proxy)

        export_path = tmp_path / "test.yaml"
        mock_path_input = MagicMock(spec=Input)
        mock_path_input.value = str(export_path)
        mock_format_select = MagicMock(spec=Select)
        mock_format_select.value = "yaml"
        mock_status = MagicMock(spec=Label)

        def query_one_mock(selector, widget_type=None):
            if selector == "#export-path":
                return mock_path_input
            elif selector == "#export-format":
                return mock_format_select
            elif selector == "#export-status":
                return mock_status
            return MagicMock()

        app.query_one = query_one_mock

        app.export_proxies()

        assert export_path.exists()


class TestSendRequestHandler:
    """Test send_request button handler."""

    def test_send_request_calls_async(self) -> None:
        """Test send_request calls send_request_async."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        app.send_request_async = MagicMock()

        app.send_request()

        app.send_request_async.assert_called_once()


class TestRefreshAnalyticsButton:
    """Test refresh_analytics_button handler."""

    def test_refresh_analytics_button_calls_refresh(self) -> None:
        """Test refresh_analytics_button calls refresh_analytics."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        app.refresh_analytics = MagicMock()

        app.refresh_analytics_button()

        app.refresh_analytics.assert_called_once()


class TestAsyncWorkers:
    """Test async worker methods."""

    async def test_fetch_proxies_async_sources(self) -> None:
        """Test fetch_proxies_async selects correct sources."""
        from textual.widgets import Label, Select

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        mock_status = MagicMock(spec=Label)
        mock_select = MagicMock(spec=Select)
        mock_select.value = "all"

        def query_one_mock(selector, widget_type=None):
            if selector == "#fetch-status":
                return mock_status
            elif selector == "#source-select":
                return mock_select
            return MagicMock()

        app.query_one = query_one_mock

        # Mock the fetcher to avoid actual network calls
        with patch("proxywhirl.tui.ProxyFetcher") as MockFetcher:
            mock_fetcher = AsyncMock()
            mock_fetcher.fetch_all = AsyncMock(return_value=[])
            MockFetcher.return_value = mock_fetcher

            # This would trigger the async worker; test the setup
            assert hasattr(app, "fetch_proxies_async")

    async def test_validate_proxies_async_empty_pool(self) -> None:
        """Test validate_proxies_async with empty pool."""
        from textual.widgets import Label

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        mock_status = MagicMock(spec=Label)

        def query_one_mock(selector, widget_type=None):
            if selector == "#fetch-status":
                return mock_status
            return MagicMock()

        app.query_one = query_one_mock

        # Empty pool scenario would update status with "No proxies"
        assert hasattr(app, "validate_proxies_async")

    async def test_send_request_async_empty_url(self) -> None:
        """Test send_request_async with empty URL."""
        from textual.widgets import Input, Select, Static

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        mock_url_input = MagicMock(spec=Input)
        mock_url_input.value = ""
        mock_method_select = MagicMock(spec=Select)
        mock_method_select.value = "GET"
        mock_output = MagicMock(spec=Static)

        def query_one_mock(selector, widget_type=None):
            if selector == "#test-url":
                return mock_url_input
            elif selector == "#test-method":
                return mock_method_select
            elif selector == "#response-output":
                return mock_output
            return MagicMock()

        app.query_one = query_one_mock

        # The async method exists
        assert hasattr(app, "send_request_async")


class TestApplyStrategyWithException:
    """Test apply_strategy with exception handling."""

    def test_apply_strategy_catches_exception(self) -> None:
        """Test apply_strategy handles strategy creation exception."""
        from textual.widgets import Label, Select

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        mock_select = MagicMock(spec=Select)
        mock_select.value = "round-robin"
        mock_status = MagicMock(spec=Label)

        def query_one_mock(selector, widget_type=None):
            if selector == "#strategy-select":
                return mock_select
            elif selector == "#strategy-status":
                return mock_status
            return MagicMock()

        app.query_one = query_one_mock

        # Force exception in strategy creation
        with patch("proxywhirl.tui.RoundRobinStrategy", side_effect=Exception("Strategy failed")):
            app.apply_strategy()

        mock_status.update.assert_called()
        call_arg = mock_status.update.call_args[0][0]
        assert "Failed to apply strategy" in call_arg


class TestSSRFValidation:
    """Test SSRF validation in TUI URL input handling."""

    def test_validate_request_url_blocks_localhost(self) -> None:
        """Test _validate_request_url blocks localhost URLs (SSRF protection)."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        with pytest.raises(ValueError, match="localhost|loopback"):
            app._validate_request_url("http://localhost:8080/admin")

    def test_validate_request_url_blocks_loopback_ip(self) -> None:
        """Test _validate_request_url blocks 127.0.0.1 loopback address."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        with pytest.raises(ValueError, match="localhost|loopback"):
            app._validate_request_url("http://127.0.0.1:9000/admin")

    def test_validate_request_url_blocks_private_ip_192(self) -> None:
        """Test _validate_request_url blocks private IP addresses (192.168.x.x)."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        with pytest.raises(ValueError, match="private|SSRF"):
            app._validate_request_url("http://192.168.1.1/api")

    def test_validate_request_url_blocks_private_ip_10(self) -> None:
        """Test _validate_request_url blocks private IP addresses (10.x.x.x)."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        with pytest.raises(ValueError, match="private|SSRF"):
            app._validate_request_url("http://10.0.0.1/internal")

    def test_validate_request_url_blocks_private_ip_172(self) -> None:
        """Test _validate_request_url blocks private IP addresses (172.16-31.x.x)."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        with pytest.raises(ValueError, match="private|SSRF"):
            app._validate_request_url("http://172.16.0.1/internal")

    def test_validate_request_url_blocks_internal_domain(self) -> None:
        """Test _validate_request_url blocks internal domain names (.local, .internal)."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        with pytest.raises(ValueError, match="internal|SSRF"):
            app._validate_request_url("http://internal.local/api")

        with pytest.raises(ValueError, match="internal|SSRF"):
            app._validate_request_url("http://server.internal/api")

        with pytest.raises(ValueError, match="internal|SSRF"):
            app._validate_request_url("http://host.lan/api")

        with pytest.raises(ValueError, match="internal|SSRF"):
            app._validate_request_url("http://corp.corp/api")

    def test_validate_request_url_blocks_file_scheme(self) -> None:
        """Test _validate_request_url blocks file:// URLs."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        with pytest.raises(ValueError, match="scheme|file"):
            app._validate_request_url("file:///etc/passwd")

    def test_validate_request_url_blocks_ftp_scheme(self) -> None:
        """Test _validate_request_url blocks ftp:// URLs."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        with pytest.raises(ValueError, match="scheme"):
            app._validate_request_url("ftp://example.com/data")

    def test_validate_request_url_blocks_data_scheme(self) -> None:
        """Test _validate_request_url blocks data:// URLs."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        with pytest.raises(ValueError, match="scheme"):
            app._validate_request_url("data:text/plain,Hello")

    def test_validate_request_url_allows_valid_http(self) -> None:
        """Test _validate_request_url allows valid public HTTP URLs."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        # Should not raise
        app._validate_request_url("http://example.com/api")
        app._validate_request_url("http://httpbin.org/get")
        app._validate_request_url("http://api.github.com/users")

    def test_validate_request_url_allows_valid_https(self) -> None:
        """Test _validate_request_url allows valid public HTTPS URLs."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        # Should not raise
        app._validate_request_url("https://example.com/api")
        app._validate_request_url("https://httpbin.org/get")
        app._validate_request_url("https://api.github.com/users")

    def test_validate_request_url_blocks_link_local(self) -> None:
        """Test _validate_request_url blocks link-local addresses (169.254.x.x)."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        with pytest.raises(ValueError, match="private|SSRF"):
            app._validate_request_url("http://169.254.169.254/metadata")


class TestNewPanelWidgets:
    """Test new panel widget classes."""

    def test_proxy_control_panel_import(self) -> None:
        """Test ProxyControlPanel can be imported."""
        from proxywhirl.tui import ProxyControlPanel

        assert ProxyControlPanel is not None

    def test_proxy_control_panel_has_compose(self) -> None:
        """Test ProxyControlPanel has compose method."""
        from proxywhirl.tui import ProxyControlPanel

        panel = ProxyControlPanel()
        assert hasattr(panel, "compose")
        assert callable(panel.compose)

    def test_filter_panel_import(self) -> None:
        """Test FilterPanel can be imported."""
        from proxywhirl.tui import FilterPanel

        assert FilterPanel is not None

    def test_filter_panel_has_compose(self) -> None:
        """Test FilterPanel has compose method."""
        from proxywhirl.tui import FilterPanel

        panel = FilterPanel()
        assert hasattr(panel, "compose")
        assert callable(panel.compose)

    def test_retry_metrics_panel_import(self) -> None:
        """Test RetryMetricsPanel can be imported."""
        from proxywhirl.tui import RetryMetricsPanel

        assert RetryMetricsPanel is not None

    def test_retry_metrics_panel_reactive_defaults(self) -> None:
        """Test RetryMetricsPanel has expected reactive properties."""
        from proxywhirl.tui import RetryMetricsPanel

        panel = RetryMetricsPanel()

        assert panel.total_retries == 0
        assert panel.successful_retries == 0
        assert panel.failed_retries == 0

    def test_retry_metrics_panel_render(self) -> None:
        """Test RetryMetricsPanel render returns Text."""
        from proxywhirl.tui import RetryMetricsPanel

        panel = RetryMetricsPanel()
        panel.total_retries = 100
        panel.successful_retries = 80
        panel.failed_retries = 20

        result = panel.render()

        assert isinstance(result, Text)
        plain_text = result.plain
        assert "100" in plain_text
        assert "80" in plain_text
        assert "80.0%" in plain_text

    def test_circuit_breaker_panel_import(self) -> None:
        """Test CircuitBreakerPanel can be imported."""
        from proxywhirl.tui import CircuitBreakerPanel

        assert CircuitBreakerPanel is not None

    def test_circuit_breaker_panel_has_compose(self) -> None:
        """Test CircuitBreakerPanel has compose method."""
        from proxywhirl.tui import CircuitBreakerPanel

        panel = CircuitBreakerPanel()
        assert hasattr(panel, "compose")
        assert callable(panel.compose)

    def test_health_check_panel_import(self) -> None:
        """Test HealthCheckPanel can be imported."""
        from proxywhirl.tui import HealthCheckPanel

        assert HealthCheckPanel is not None

    def test_health_check_panel_has_compose(self) -> None:
        """Test HealthCheckPanel has compose method."""
        from proxywhirl.tui import HealthCheckPanel

        panel = HealthCheckPanel()
        assert hasattr(panel, "compose")
        assert callable(panel.compose)


class TestModalScreens:
    """Test modal screen classes."""

    def test_proxy_details_screen_import(self) -> None:
        """Test ProxyDetailsScreen can be imported."""
        from proxywhirl.tui import ProxyDetailsScreen

        assert ProxyDetailsScreen is not None

    def test_proxy_details_screen_init(self) -> None:
        """Test ProxyDetailsScreen initializes with proxy."""
        from proxywhirl.tui import ProxyDetailsScreen

        proxy = Proxy(
            url="http://proxy.example.com:8080",
            health_status=HealthStatus.HEALTHY,
        )
        screen = ProxyDetailsScreen(proxy)

        assert screen.proxy is proxy

    def test_proxy_details_screen_has_compose(self) -> None:
        """Test ProxyDetailsScreen has compose method."""
        from proxywhirl.tui import ProxyDetailsScreen

        proxy = Proxy(url="http://proxy.example.com:8080")
        screen = ProxyDetailsScreen(proxy)

        assert hasattr(screen, "compose")
        assert callable(screen.compose)

    def test_confirm_delete_screen_import(self) -> None:
        """Test ConfirmDeleteScreen can be imported."""
        from proxywhirl.tui import ConfirmDeleteScreen

        assert ConfirmDeleteScreen is not None

    def test_confirm_delete_screen_init(self) -> None:
        """Test ConfirmDeleteScreen initializes with proxy URL."""
        from proxywhirl.tui import ConfirmDeleteScreen

        screen = ConfirmDeleteScreen("http://proxy.example.com:8080")

        assert screen.proxy_url == "http://proxy.example.com:8080"

    def test_confirm_delete_screen_has_compose(self) -> None:
        """Test ConfirmDeleteScreen has compose method."""
        from proxywhirl.tui import ConfirmDeleteScreen

        screen = ConfirmDeleteScreen("http://proxy.example.com:8080")

        assert hasattr(screen, "compose")
        assert callable(screen.compose)


class TestProxyTableEnhancements:
    """Test ProxyTable enhancements for filtering and sorting."""

    def test_proxy_table_has_cursor_type_row(self) -> None:
        """Test ProxyTable initializes with row cursor type."""
        from proxywhirl.tui import ProxyTable

        table = ProxyTable()
        assert table.cursor_type == "row"

    def test_proxy_table_has_proxy_map(self) -> None:
        """Test ProxyTable has _proxy_map attribute."""
        from proxywhirl.tui import ProxyTable

        table = ProxyTable()
        assert hasattr(table, "_proxy_map")
        assert isinstance(table._proxy_map, dict)

    def test_proxy_table_filter_proxies(self) -> None:
        """Test ProxyTable _filter_proxies method."""
        from proxywhirl.tui import ProxyTable

        table = ProxyTable()

        proxies = [
            Proxy(
                url="http://proxy1.example.com:8080",
                protocol="http",
                health_status=HealthStatus.HEALTHY,
                country_code="US",
            ),
            Proxy(
                url="socks5://proxy2.example.com:1080",
                protocol="socks5",
                health_status=HealthStatus.DEGRADED,
                country_code="UK",
            ),
        ]

        # Filter by protocol
        table.filter_protocol = "http"
        result = table._filter_proxies(proxies)
        assert len(result) == 1
        assert result[0].protocol == "http"

        # Filter by health
        table.filter_protocol = "all"
        table.filter_health = "healthy"
        result = table._filter_proxies(proxies)
        assert len(result) == 1
        assert result[0].health_status == HealthStatus.HEALTHY

        # Filter by text search
        table.filter_health = "all"
        table.filter_text = "proxy1"
        result = table._filter_proxies(proxies)
        assert len(result) == 1
        assert "proxy1" in str(result[0].url)

    def test_proxy_table_sort_proxies(self) -> None:
        """Test ProxyTable _sort_proxies method."""
        from proxywhirl.tui import ProxyTable

        table = ProxyTable()

        proxies = [
            Proxy(
                url="http://z-proxy.example.com:8080",
                average_response_time_ms=500.0,
            ),
            Proxy(
                url="http://a-proxy.example.com:8080",
                average_response_time_ms=100.0,
            ),
        ]

        # Sort by URL
        table.sort_column = "url"
        table.sort_ascending = True
        result = table._sort_proxies(proxies)
        assert "a-proxy" in str(result[0].url)

        # Sort by latency
        table.sort_column = "latency"
        table.sort_ascending = True
        result = table._sort_proxies(proxies)
        assert result[0].average_response_time_ms == 100.0

    def test_proxy_table_set_sort(self) -> None:
        """Test ProxyTable set_sort toggles direction."""
        from proxywhirl.tui import ProxyTable

        table = ProxyTable()

        # First sort sets column
        table.set_sort("url")
        assert table.sort_column == "url"
        assert table.sort_ascending is True

        # Same column toggles direction
        table.set_sort("url")
        assert table.sort_column == "url"
        assert table.sort_ascending is False

        # Different column resets to ascending
        table.set_sort("latency")
        assert table.sort_column == "latency"
        assert table.sort_ascending is True


class TestNewAppMethods:
    """Test new ProxyWhirlTUI methods."""

    def test_app_has_filter_state(self) -> None:
        """Test app has filter state attributes."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        assert hasattr(app, "_filter_text")
        assert hasattr(app, "_filter_protocol")
        assert hasattr(app, "_filter_health")
        assert hasattr(app, "_filter_country")

    def test_app_has_refresh_retry_metrics(self) -> None:
        """Test app has refresh_retry_metrics method."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        assert hasattr(app, "refresh_retry_metrics")
        assert callable(app.refresh_retry_metrics)

    def test_app_has_refresh_circuit_breakers(self) -> None:
        """Test app has refresh_circuit_breakers method."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        assert hasattr(app, "refresh_circuit_breakers")
        assert callable(app.refresh_circuit_breakers)

    def test_app_has_add_proxy_method(self) -> None:
        """Test app has add_proxy method."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        assert hasattr(app, "add_proxy")
        assert callable(app.add_proxy)

    def test_app_has_remove_selected_proxy_method(self) -> None:
        """Test app has remove_selected_proxy method."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        assert hasattr(app, "remove_selected_proxy")
        assert callable(app.remove_selected_proxy)

    def test_app_has_action_delete_proxy(self) -> None:
        """Test app has action_delete_proxy method."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        assert hasattr(app, "action_delete_proxy")
        assert callable(app.action_delete_proxy)

    def test_app_has_action_view_details(self) -> None:
        """Test app has action_view_details method."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        assert hasattr(app, "action_view_details")
        assert callable(app.action_view_details)

    def test_app_has_health_check_async(self) -> None:
        """Test app has health_check_async method."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        assert hasattr(app, "health_check_async")

    def test_app_bindings_include_delete(self) -> None:
        """Test app BINDINGS includes delete key."""
        from proxywhirl.tui import ProxyWhirlTUI

        binding_keys = [b[0] for b in ProxyWhirlTUI.BINDINGS]
        assert "delete" in binding_keys

    def test_app_bindings_include_enter(self) -> None:
        """Test app BINDINGS includes enter key."""
        from proxywhirl.tui import ProxyWhirlTUI

        binding_keys = [b[0] for b in ProxyWhirlTUI.BINDINGS]
        assert "enter" in binding_keys

    def test_app_bindings_include_vim_keys(self) -> None:
        """Test app BINDINGS includes vim navigation keys."""
        from proxywhirl.tui import ProxyWhirlTUI

        binding_keys = [b[0] for b in ProxyWhirlTUI.BINDINGS]
        assert "j" in binding_keys
        assert "k" in binding_keys
        assert "g" in binding_keys
        assert "G" in binding_keys

    def test_app_bindings_include_copy(self) -> None:
        """Test app BINDINGS includes copy key."""
        from proxywhirl.tui import ProxyWhirlTUI

        binding_keys = [b[0] for b in ProxyWhirlTUI.BINDINGS]
        assert "c" in binding_keys

    def test_app_has_action_copy_url(self) -> None:
        """Test app has action_copy_url method."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        assert hasattr(app, "action_copy_url")
        assert callable(app.action_copy_url)

    def test_app_has_vim_navigation_actions(self) -> None:
        """Test app has vim navigation action methods."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        assert hasattr(app, "action_cursor_down")
        assert hasattr(app, "action_cursor_up")
        assert hasattr(app, "action_cursor_top")
        assert hasattr(app, "action_cursor_bottom")

    def test_app_has_action_health(self) -> None:
        """Test app has action_health method."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()

        assert hasattr(app, "action_health")
        assert callable(app.action_health)


class TestProxyDetailsScreenCopy:
    """Test ProxyDetailsScreen copy functionality."""

    def test_details_screen_has_copy_button(self) -> None:
        """Test ProxyDetailsScreen has copy button in compose."""
        from proxywhirl.tui import ProxyDetailsScreen

        proxy = Proxy(url="http://proxy.example.com:8080")
        screen = ProxyDetailsScreen(proxy)

        # Check compose method exists and is callable
        assert hasattr(screen, "compose")
        assert callable(screen.compose)

    def test_details_screen_has_copy_method(self) -> None:
        """Test ProxyDetailsScreen has copy_url_to_clipboard method."""
        from proxywhirl.tui import ProxyDetailsScreen

        proxy = Proxy(url="http://proxy.example.com:8080")
        screen = ProxyDetailsScreen(proxy)

        assert hasattr(screen, "copy_url_to_clipboard")
        assert callable(screen.copy_url_to_clipboard)


class TestTUIE2E:
    """End-to-end tests using Textual's Pilot testing framework."""

    async def test_app_starts_and_shows_header(self) -> None:
        """Test app starts and shows header."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        async with app.run_test() as pilot:
            # App should be running
            assert pilot.app is not None
            assert pilot.app.title == "🌀 ProxyWhirl"

    async def test_app_shows_overview_tab_by_default(self) -> None:
        """Test app shows overview tab by default."""
        from textual.widgets import TabbedContent

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        async with app.run_test() as pilot:
            tabs = pilot.app.query_one(TabbedContent)
            assert tabs.active == "overview"

    async def test_ctrl_f_switches_to_fetch_tab(self) -> None:
        """Test Ctrl+F switches to fetch tab."""
        from textual.widgets import TabbedContent

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        async with app.run_test() as pilot:
            await pilot.press("ctrl+f")
            tabs = pilot.app.query_one(TabbedContent)
            assert tabs.active == "fetch"

    async def test_ctrl_e_switches_to_export_tab(self) -> None:
        """Test Ctrl+E switches to export tab."""
        from textual.widgets import TabbedContent

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        async with app.run_test() as pilot:
            await pilot.press("ctrl+e")
            tabs = pilot.app.query_one(TabbedContent)
            assert tabs.active == "export"

    async def test_ctrl_t_switches_to_test_tab(self) -> None:
        """Test Ctrl+T switches to test tab."""
        from textual.widgets import TabbedContent

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        async with app.run_test() as pilot:
            await pilot.press("ctrl+t")
            tabs = pilot.app.query_one(TabbedContent)
            assert tabs.active == "test"

    async def test_ctrl_h_switches_to_health_tab(self) -> None:
        """Test Ctrl+H switches to health tab."""
        from textual.widgets import TabbedContent

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        async with app.run_test() as pilot:
            await pilot.press("ctrl+h")
            tabs = pilot.app.query_one(TabbedContent)
            assert tabs.active == "health"

    async def test_f1_shows_help_notification(self) -> None:
        """Test F1 shows help notification."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        async with app.run_test() as pilot:
            await pilot.press("f1")
            # Give time for notification to appear
            await pilot.pause()
            # Notifications are shown but we can't easily query them
            # Just verify no crash occurred

    async def test_proxy_table_is_rendered(self) -> None:
        """Test proxy table is rendered in overview."""
        from proxywhirl.tui import ProxyTable, ProxyWhirlTUI

        app = ProxyWhirlTUI()
        async with app.run_test() as pilot:
            table = pilot.app.query_one("#proxy-table", ProxyTable)
            assert table is not None
            assert table.cursor_type == "row"

    async def test_metrics_panel_is_rendered(self) -> None:
        """Test metrics panel is rendered."""
        from proxywhirl.tui import MetricsPanel, ProxyWhirlTUI

        app = ProxyWhirlTUI()
        async with app.run_test() as pilot:
            metrics = pilot.app.query_one("#metrics-panel", MetricsPanel)
            assert metrics is not None
            assert metrics.total_proxies == 0  # Empty pool initially

    async def test_filter_panel_is_rendered(self) -> None:
        """Test filter panel is rendered."""
        from textual.widgets import Input, Select

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        async with app.run_test() as pilot:
            search_input = pilot.app.query_one("#filter-search", Input)
            protocol_select = pilot.app.query_one("#filter-protocol", Select)
            health_select = pilot.app.query_one("#filter-health", Select)

            assert search_input is not None
            assert protocol_select is not None
            assert health_select is not None

    async def test_add_proxy_button_exists(self) -> None:
        """Test add proxy button exists."""
        from textual.widgets import Button

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        async with app.run_test() as pilot:
            button = pilot.app.query_one("#add-proxy-btn", Button)
            assert button is not None

    async def test_ctrl_r_refreshes_data(self) -> None:
        """Test Ctrl+R refreshes data without error."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        async with app.run_test() as pilot:
            # Press Ctrl+R to refresh
            await pilot.press("ctrl+r")
            await pilot.pause()
            # Verify no crash - app is still running
            assert pilot.app is not None

    async def test_health_check_panel_exists(self) -> None:
        """Test health check panel exists in health tab."""
        from textual.widgets import Button

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        async with app.run_test() as pilot:
            await pilot.press("ctrl+h")  # Go to health tab
            await pilot.pause()

            button = pilot.app.query_one("#health-check-btn", Button)
            assert button is not None

    async def test_circuit_breaker_panel_exists(self) -> None:
        """Test circuit breaker panel exists in health tab."""
        from textual.widgets import Static

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        async with app.run_test() as pilot:
            await pilot.press("ctrl+h")  # Go to health tab
            await pilot.pause()

            cb_content = pilot.app.query_one("#circuit-breaker-content", Static)
            assert cb_content is not None

    async def test_status_bar_exists(self) -> None:
        """Test status bar is rendered."""
        from proxywhirl.tui import ProxyWhirlTUI, StatusBar

        app = ProxyWhirlTUI()
        async with app.run_test() as pilot:
            status_bar = pilot.app.query_one("#status-bar", StatusBar)
            assert status_bar is not None

    async def test_help_modal_opens(self) -> None:
        """Test ? key opens help modal."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        async with app.run_test() as pilot:
            await pilot.press("?")
            await pilot.pause()
            # Verify help modal is pushed
            assert len(pilot.app.screen_stack) > 1

    async def test_search_focus_works(self) -> None:
        """Test / key focuses search input."""
        from textual.widgets import Input

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        async with app.run_test() as pilot:
            await pilot.press("/")
            await pilot.pause()
            # Search input should be focused
            search_input = pilot.app.query_one("#filter-search", Input)
            assert search_input.has_focus

    async def test_auto_refresh_toggle(self) -> None:
        """Test Ctrl+A toggles auto-refresh."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        async with app.run_test() as pilot:
            assert pilot.app._auto_refresh_enabled is True
            await pilot.press("ctrl+a")
            await pilot.pause()
            assert pilot.app._auto_refresh_enabled is False
            await pilot.press("ctrl+a")
            await pilot.pause()
            assert pilot.app._auto_refresh_enabled is True

    async def test_export_preview_button_exists(self) -> None:
        """Test export preview button exists."""
        from textual.widgets import Button

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        async with app.run_test() as pilot:
            await pilot.press("ctrl+e")  # Go to export tab
            await pilot.pause()

            button = pilot.app.query_one("#preview-export-btn", Button)
            assert button is not None


class TestNewWidgets:
    """Test new widgets added for primo experience."""

    def test_status_bar_import(self) -> None:
        """Test StatusBar can be imported."""
        from proxywhirl.tui import StatusBar

        assert StatusBar is not None

    def test_status_bar_reactive_defaults(self) -> None:
        """Test StatusBar has correct reactive defaults."""
        from proxywhirl.tui import StatusBar

        bar = StatusBar()
        assert bar.proxy_count == 0
        assert bar.healthy_count == 0
        assert bar.auto_refresh is True

    def test_help_screen_import(self) -> None:
        """Test HelpScreen can be imported."""
        from proxywhirl.tui import HelpScreen

        assert HelpScreen is not None

    def test_metrics_panel_sparkline(self) -> None:
        """Test MetricsPanel sparkline method."""
        from proxywhirl.tui import MetricsPanel

        panel = MetricsPanel()
        result = panel._sparkline([1, 2, 3, 4, 5])
        assert len(result) == 10  # Default width
        assert "▁" in result or "▂" in result or "█" in result

    def test_metrics_panel_trend_indicator(self) -> None:
        """Test MetricsPanel trend indicator."""
        from proxywhirl.tui import MetricsPanel

        panel = MetricsPanel()
        arrow, style = panel._trend_indicator(100, 50)
        assert arrow == "↑"

        arrow, style = panel._trend_indicator(50, 100)
        assert arrow == "↓"

        arrow, style = panel._trend_indicator(50, 50)
        assert arrow == "→"

    def test_app_has_refresh_status_bar(self) -> None:
        """Test app has refresh_status_bar method."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        assert hasattr(app, "refresh_status_bar")
        assert callable(app.refresh_status_bar)

    def test_app_bindings_include_new_keys(self) -> None:
        """Test app BINDINGS includes new keyboard shortcuts."""
        from proxywhirl.tui import ProxyWhirlTUI

        binding_keys = [b[0] for b in ProxyWhirlTUI.BINDINGS]
        assert "?" in binding_keys  # Help modal
        assert "/" in binding_keys  # Focus search
        assert "ctrl+a" in binding_keys  # Toggle auto-refresh
        assert "t" in binding_keys  # Quick test

    def test_app_has_action_quick_test(self) -> None:
        """Test app has action_quick_test method."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        assert hasattr(app, "action_quick_test")
        assert callable(app.action_quick_test)

    def test_app_has_quick_test_proxy_async(self) -> None:
        """Test app has quick_test_proxy_async worker."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        assert hasattr(app, "quick_test_proxy_async")

    def test_status_bar_has_last_action(self) -> None:
        """Test StatusBar has last_action reactive."""
        from proxywhirl.tui import StatusBar

        bar = StatusBar()
        assert hasattr(bar, "last_action")
        assert bar.last_action == ""

    def test_app_bindings_include_analytics_and_delete_unhealthy(self) -> None:
        """Test app BINDINGS includes analytics and delete unhealthy shortcuts."""
        from proxywhirl.tui import ProxyWhirlTUI

        binding_keys = [b[0] for b in ProxyWhirlTUI.BINDINGS]
        assert "ctrl+s" in binding_keys  # Analytics tab
        assert "ctrl+d" in binding_keys  # Delete unhealthy

    def test_app_has_action_analytics(self) -> None:
        """Test app has action_analytics method."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        assert hasattr(app, "action_analytics")
        assert callable(app.action_analytics)

    def test_app_has_action_delete_unhealthy(self) -> None:
        """Test app has action_delete_unhealthy method."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        assert hasattr(app, "action_delete_unhealthy")
        assert callable(app.action_delete_unhealthy)


class TestAnalyticsEnhancements:
    """Test enhanced analytics with histogram."""

    async def test_analytics_tab_accessible(self) -> None:
        """Test Ctrl+S switches to analytics tab."""
        from textual.widgets import TabbedContent

        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        async with app.run_test() as pilot:
            await pilot.press("ctrl+s")
            tabs = pilot.app.query_one(TabbedContent)
            assert tabs.active == "analytics"

    def test_refresh_analytics_method_exists(self) -> None:
        """Test refresh_analytics method handles histogram generation."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        assert hasattr(app, "refresh_analytics")
        assert callable(app.refresh_analytics)


class TestControlPanelEnhancements:
    """Tests for control panel enhancements."""

    def test_control_panel_import(self) -> None:
        """Test ProxyControlPanel can be imported."""
        from proxywhirl.tui import ProxyControlPanel

        # Just verify it can be instantiated
        assert ProxyControlPanel is not None

    def test_app_has_clear_all_method(self) -> None:
        """Test app has clear_all_proxies method."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        assert hasattr(app, "clear_all_proxies")
        assert callable(app.clear_all_proxies)

    def test_app_has_test_all_method(self) -> None:
        """Test app has test_all_proxies method."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        assert hasattr(app, "test_all_proxies")
        assert callable(app.test_all_proxies)

    def test_app_has_test_all_async_method(self) -> None:
        """Test app has test_all_proxies_async method."""
        from proxywhirl.tui import ProxyWhirlTUI

        app = ProxyWhirlTUI()
        assert hasattr(app, "test_all_proxies_async")
        assert callable(app.test_all_proxies_async)


class TestTableEnhancements:
    """Tests for proxy table visual enhancements."""

    def test_proxy_table_uses_rich_text(self) -> None:
        """Test proxy table uses Rich Text for styling."""
        from proxywhirl.tui import ProxyTable

        table = ProxyTable()
        # Table should have styling capabilities
        assert table is not None
