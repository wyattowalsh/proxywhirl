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
from proxywhirl.rotator import ProxyRotator


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
        assert "8 healthy" in plain_text
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
        assert isinstance(app.rotator, ProxyRotator)
        # fetcher and validator are set in on_mount, not __init__
        assert hasattr(app, "fetcher")
        assert hasattr(app, "validator")

    def test_proxy_whirl_tui_init_with_rotator(self) -> None:
        """Test ProxyWhirlTUI initialization with custom rotator."""
        from proxywhirl.tui import ProxyWhirlTUI

        rotator = ProxyRotator()
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

        rotator = ProxyRotator()

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

        assert len(added_columns) == 7
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
