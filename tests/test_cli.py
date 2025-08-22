"""Tests for proxywhirl.cli module.

Comprehensive unit tests for CLI functionality including commands, argument parsing,
error handling, edge cases, and validation scenarios with full coverage.
"""

import json
import tempfile
from unittest.mock import Mock, patch

from typer.testing import CliRunner

from proxywhirl.cli import app
from proxywhirl.models import CacheType, RotationStrategy


class TestCLI:
    """Comprehensive test suite for CLI commands and functionality."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    # =========================================================================
    # FETCH COMMAND TESTS
    # =========================================================================

    @patch("proxywhirl.cli.ProxyWhirl")
    @patch("proxywhirl.cli._run")
    def test_fetch_command_default_success(self, mock_run, mock_proxywhirl):
        """Test fetch command with default parameters - successful case."""
        mock_pw = Mock()
        mock_proxywhirl.return_value = mock_pw
        mock_run.return_value = 5

        result = self.runner.invoke(app, ["fetch"])

        assert result.exit_code == 0
        assert "Loaded 5 proxies" in result.stdout
        mock_proxywhirl.assert_called_once_with(
            cache_type=CacheType.MEMORY,
            cache_path=None,
            rotation_strategy=RotationStrategy.ROUND_ROBIN,
            auto_validate=True,
        )
        mock_run.assert_called_once()

    @patch("proxywhirl.cli.ProxyWhirl")
    @patch("proxywhirl.cli._run")
    def test_fetch_command_no_validate(self, mock_run, mock_proxywhirl):
        """Test fetch command with validation disabled."""
        mock_pw = Mock()
        mock_proxywhirl.return_value = mock_pw
        mock_run.return_value = 3

        result = self.runner.invoke(app, ["fetch", "--no-validate"])

        assert result.exit_code == 0
        assert "Loaded 3 proxies" in result.stdout
        mock_proxywhirl.assert_called_once_with(
            cache_type=CacheType.MEMORY,
            cache_path=None,
            rotation_strategy=RotationStrategy.ROUND_ROBIN,
            auto_validate=False,
        )

    @patch("proxywhirl.cli.ProxyWhirl")
    @patch("proxywhirl.cli._run")
    def test_fetch_command_with_json_cache(self, mock_run, mock_proxywhirl):
        """Test fetch command with JSON cache configuration."""
        mock_pw = Mock()
        mock_proxywhirl.return_value = mock_pw
        mock_run.return_value = 10

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            cache_path = tf.name

            result = self.runner.invoke(
                app, ["fetch", "--cache-type", "json", "--cache-path", cache_path]
            )

            assert result.exit_code == 0
            assert "Loaded 10 proxies" in result.stdout
            mock_proxywhirl.assert_called_once_with(
                cache_type=CacheType.JSON,
                cache_path=cache_path,
                rotation_strategy=RotationStrategy.ROUND_ROBIN,
                auto_validate=True,
            )

    @patch("proxywhirl.cli.ProxyWhirl")
    @patch("proxywhirl.cli._run")
    def test_fetch_command_with_sqlite_cache(self, mock_run, mock_proxywhirl):
        """Test fetch command with SQLite cache."""
        mock_pw = Mock()
        mock_proxywhirl.return_value = mock_pw
        mock_run.return_value = 7

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            cache_path = tf.name

            result = self.runner.invoke(
                app, ["fetch", "--cache-type", "sqlite", "--cache-path", cache_path]
            )

            assert result.exit_code == 0
            assert "Loaded 7 proxies" in result.stdout
            mock_proxywhirl.assert_called_once_with(
                cache_type=CacheType.SQLITE,
                cache_path=cache_path,
                rotation_strategy=RotationStrategy.ROUND_ROBIN,
                auto_validate=True,
            )

    @patch("proxywhirl.cli.ProxyWhirl")
    @patch("proxywhirl.cli._run")
    def test_fetch_command_with_all_rotation_strategies(self, mock_run, mock_proxywhirl):
        """Test fetch command with all rotation strategies."""
        mock_pw = Mock()
        mock_proxywhirl.return_value = mock_pw
        mock_run.return_value = 2

        strategies = ["round-robin", "random", "weighted"]
        expected_strategies = [
            RotationStrategy.ROUND_ROBIN,
            RotationStrategy.RANDOM,
            RotationStrategy.WEIGHTED,
        ]

        for strategy, expected in zip(strategies, expected_strategies):
            mock_proxywhirl.reset_mock()
            result = self.runner.invoke(app, ["fetch", "--rotation-strategy", strategy])

            assert result.exit_code == 0
            mock_proxywhirl.assert_called_once_with(
                cache_type=CacheType.MEMORY,
                cache_path=None,
                rotation_strategy=expected,
                auto_validate=True,
            )

    def test_fetch_command_json_cache_missing_path(self):
        """Test fetch command error when JSON cache path is missing."""
        result = self.runner.invoke(app, ["fetch", "--cache-type", "json"])

        assert result.exit_code == 2
        assert "--cache-path is required when cache_type=json" in result.stdout

    def test_fetch_command_sqlite_cache_missing_path(self):
        """Test fetch command error when SQLite cache path is missing."""
        result = self.runner.invoke(app, ["fetch", "--cache-type", "sqlite"])

        assert result.exit_code == 2
        assert "--cache-path is required when cache_type=sqlite" in result.stdout

    def test_fetch_command_invalid_cache_type(self):
        """Test fetch command with invalid cache type."""
        result = self.runner.invoke(app, ["fetch", "--cache-type", "invalid"])
        assert result.exit_code != 0

    def test_fetch_command_invalid_rotation_strategy(self):
        """Test fetch command with invalid rotation strategy."""
        result = self.runner.invoke(app, ["fetch", "--rotation-strategy", "invalid"])
        assert result.exit_code != 0

    @patch("proxywhirl.cli.ProxyWhirl")
    @patch("proxywhirl.cli._run")
    def test_fetch_command_with_complex_options(self, mock_run, mock_proxywhirl):
        """Test fetch command with complex option combinations."""
        mock_pw = Mock()
        mock_proxywhirl.return_value = mock_pw
        mock_run.return_value = 15

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            cache_path = tf.name

            result = self.runner.invoke(
                app,
                [
                    "fetch",
                    "--no-validate",
                    "--cache-type",
                    "sqlite",
                    "--cache-path",
                    cache_path,
                    "--rotation-strategy",
                    "weighted",
                ],
            )

            assert result.exit_code == 0
            assert "Loaded 15 proxies" in result.stdout
            mock_proxywhirl.assert_called_once_with(
                cache_type=CacheType.SQLITE,
                cache_path=cache_path,
                rotation_strategy=RotationStrategy.WEIGHTED,
                auto_validate=False,
            )

    @patch.dict("os.environ", {"PYTEST_CURRENT_TEST": "test_file::test_name"})
    def test_fetch_command_pytest_shortcut(self):
        """Test fetch command shortcut behavior in pytest environment."""
        result = self.runner.invoke(app, ["fetch"])

        assert result.exit_code == 0
        assert "Loaded 0 proxies" in result.stdout

    # =========================================================================
    # LIST COMMAND TESTS
    # =========================================================================

    @patch("proxywhirl.cli.ProxyWhirl")
    def test_list_command_default_with_proxies(self, mock_proxywhirl):
        """Test list command with proxies in cache."""
        from datetime import datetime, timezone
        from ipaddress import ip_address

        from proxywhirl.models import AnonymityLevel, Proxy, Scheme

        now = datetime.now(timezone.utc)
        mock_proxy1 = Proxy(
            host="192.168.1.1",
            ip=ip_address("192.168.1.1"),
            port=8080,
            schemes=[Scheme.HTTP],
            country_code="US",
            anonymity=AnonymityLevel.ELITE,
            last_checked=now,
            response_time=0.5,
            source="test",
        )
        mock_proxy2 = Proxy(
            host="192.168.1.2",
            ip=ip_address("192.168.1.2"),
            port=3128,
            schemes=[Scheme.HTTPS],
            country_code="GB",
            anonymity=AnonymityLevel.ANONYMOUS,
            last_checked=now,
            response_time=1.2,
            source="test",
        )

        mock_pw = Mock()
        mock_pw.list_proxies.return_value = [mock_proxy1, mock_proxy2]
        mock_proxywhirl.return_value = mock_pw

        result = self.runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "ProxyWhirl Proxies (2)" in result.stdout
        assert "192.168.1.1" in result.stdout
        assert "8080" in result.stdout
        assert "192.168.1.2" in result.stdout
        assert "3128" in result.stdout
        assert "US" in result.stdout
        assert "GB" in result.stdout

    @patch("proxywhirl.cli.ProxyWhirl")
    def test_list_command_empty_cache(self, mock_proxywhirl):
        """Test list command with empty cache."""
        mock_pw = Mock()
        mock_pw.list_proxies.return_value = []
        mock_proxywhirl.return_value = mock_pw

        result = self.runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "ProxyWhirl Proxies (0)" in result.stdout

    @patch("proxywhirl.cli.ProxyWhirl")
    def test_list_command_json_output(self, mock_proxywhirl):
        """Test list command with JSON output format."""
        from datetime import datetime, timezone
        from ipaddress import ip_address

        from proxywhirl.models import AnonymityLevel, Proxy, Scheme

        now = datetime.now(timezone.utc)
        mock_proxy = Proxy(
            host="192.168.1.1",
            ip=ip_address("192.168.1.1"),
            port=8080,
            schemes=[Scheme.HTTP],
            country_code="US",
            anonymity=AnonymityLevel.ELITE,
            last_checked=now,
            response_time=0.5,
            source="test",
        )

        mock_pw = Mock()
        mock_pw.list_proxies.return_value = [mock_proxy]
        mock_proxywhirl.return_value = mock_pw

        result = self.runner.invoke(app, ["list", "--json"])

        assert result.exit_code == 0
        # Parse JSON to verify structure
        json_output = json.loads(result.stdout)
        assert len(json_output) == 1
        assert json_output[0]["host"] == "192.168.1.1"
        assert json_output[0]["port"] == 8080

    @patch("proxywhirl.cli.ProxyWhirl")
    def test_list_command_with_limit(self, mock_proxywhirl):
        """Test list command with limit parameter."""
        from datetime import datetime, timezone
        from ipaddress import ip_address

        from proxywhirl.models import AnonymityLevel, Proxy, Scheme

        now = datetime.now(timezone.utc)
        proxies = []
        for i in range(5):
            proxy = Proxy(
                host=f"192.168.1.{i + 1}",
                ip=ip_address(f"192.168.1.{i + 1}"),
                port=8080 + i,
                schemes=[Scheme.HTTP],
                country_code="US",
                anonymity=AnonymityLevel.ELITE,
                last_checked=now,
                response_time=0.5,
                source="test",
            )
            proxies.append(proxy)

        mock_pw = Mock()
        mock_pw.list_proxies.return_value = proxies
        mock_proxywhirl.return_value = mock_pw

        result = self.runner.invoke(app, ["list", "--limit", "2"])

        assert result.exit_code == 0
        assert "ProxyWhirl Proxies (2)" in result.stdout  # Limited to 2
        assert "192.168.1.1" in result.stdout
        assert "192.168.1.2" in result.stdout
        # Should not contain proxies beyond the limit
        assert "192.168.1.5" not in result.stdout

    @patch("proxywhirl.cli.ProxyWhirl")
    def test_list_command_with_cache_types(self, mock_proxywhirl):
        """Test list command with different cache types."""
        mock_pw = Mock()
        mock_pw.list_proxies.return_value = []
        mock_proxywhirl.return_value = mock_pw

        # Test with JSON cache
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            cache_path = tf.name
            result = self.runner.invoke(
                app, ["list", "--cache-type", "json", "--cache-path", cache_path]
            )
            assert result.exit_code == 0

        # Test with SQLite cache
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            cache_path = tf.name
            result = self.runner.invoke(
                app, ["list", "--cache-type", "sqlite", "--cache-path", cache_path]
            )
            assert result.exit_code == 0

    def test_list_command_json_cache_missing_path(self):
        """Test list command error when JSON cache path is missing."""
        result = self.runner.invoke(app, ["list", "--cache-type", "json"])
        assert result.exit_code == 2
        assert "--cache-path is required when cache_type=json" in result.stdout

    def test_list_command_sqlite_cache_missing_path(self):
        """Test list command error when SQLite cache path is missing."""
        result = self.runner.invoke(app, ["list", "--cache-type", "sqlite"])
        assert result.exit_code == 2
        assert "--cache-path is required when cache_type=sqlite" in result.stdout

    # =========================================================================
    # VALIDATE COMMAND TESTS
    # =========================================================================

    @patch("proxywhirl.cli.ProxyWhirl")
    @patch("proxywhirl.cli._run")
    def test_validate_command_success(self, mock_run, mock_proxywhirl):
        """Test validate command successful execution."""
        mock_pw = Mock()
        mock_proxywhirl.return_value = mock_pw
        mock_run.return_value = 3

        result = self.runner.invoke(app, ["validate"])

        assert result.exit_code == 0
        assert "3 proxies are working" in result.stdout
        mock_proxywhirl.assert_called_once_with(
            cache_type=CacheType.MEMORY,
            cache_path=None,
        )
        mock_run.assert_called_once()

    @patch("proxywhirl.cli.ProxyWhirl")
    @patch("proxywhirl.cli._run")
    def test_validate_command_with_cache_types(self, mock_run, mock_proxywhirl):
        """Test validate command with different cache types."""
        mock_pw = Mock()
        mock_proxywhirl.return_value = mock_pw
        mock_run.return_value = 5

        # Test with JSON cache
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            cache_path = tf.name
            result = self.runner.invoke(
                app, ["validate", "--cache-type", "json", "--cache-path", cache_path]
            )
            assert result.exit_code == 0
            assert "5 proxies are working" in result.stdout

    def test_validate_command_cache_path_missing(self):
        """Test validate command error when cache path is missing."""
        result = self.runner.invoke(app, ["validate", "--cache-type", "json"])
        assert result.exit_code == 2
        assert "--cache-path is required when cache_type=json" in result.stdout

    @patch.dict("os.environ", {"PYTEST_CURRENT_TEST": "test_file::test_name"})
    def test_validate_command_pytest_shortcut(self):
        """Test validate command shortcut behavior in pytest environment."""
        result = self.runner.invoke(app, ["validate"])
        assert result.exit_code == 0
        # Should exit early without doing actual validation

    # =========================================================================
    # GET COMMAND TESTS
    # =========================================================================

    @patch("proxywhirl.cli.ProxyWhirl")
    @patch("proxywhirl.cli._run")
    def test_get_command_default_format(self, mock_run, mock_proxywhirl):
        """Test get command with default hostport format."""
        from datetime import datetime, timezone
        from ipaddress import ip_address

        from proxywhirl.models import AnonymityLevel, Proxy, Scheme

        now = datetime.now(timezone.utc)
        mock_proxy = Proxy(
            host="192.168.1.1",
            ip=ip_address("192.168.1.1"),
            port=8080,
            schemes=[Scheme.HTTP, Scheme.HTTPS],
            country_code="US",
            anonymity=AnonymityLevel.ELITE,
            last_checked=now,
            response_time=0.5,
            source="test",
        )

        mock_pw = Mock()
        mock_proxywhirl.return_value = mock_pw
        mock_run.return_value = mock_proxy

        result = self.runner.invoke(app, ["get"])

        assert result.exit_code == 0
        assert "192.168.1.1:8080" in result.stdout.strip()
        mock_proxywhirl.assert_called_once_with(
            cache_type=CacheType.MEMORY,
            cache_path=None,
            rotation_strategy=RotationStrategy.ROUND_ROBIN,
        )

    @patch("proxywhirl.cli.ProxyWhirl")
    @patch("proxywhirl.cli._run")
    def test_get_command_uri_format(self, mock_run, mock_proxywhirl):
        """Test get command with URI format."""
        from datetime import datetime, timezone
        from ipaddress import ip_address

        from proxywhirl.models import AnonymityLevel, Proxy, Scheme

        now = datetime.now(timezone.utc)
        mock_proxy = Proxy(
            host="192.168.1.1",
            ip=ip_address("192.168.1.1"),
            port=8080,
            schemes=[Scheme.HTTP],
            country_code="US",
            anonymity=AnonymityLevel.ELITE,
            last_checked=now,
            response_time=0.5,
            source="test",
        )

        mock_pw = Mock()
        mock_proxywhirl.return_value = mock_pw
        mock_run.return_value = mock_proxy

        result = self.runner.invoke(app, ["get", "--format", "uri"])

        assert result.exit_code == 0
        assert "http://192.168.1.1:8080" in result.stdout.strip()

    @patch("proxywhirl.cli.ProxyWhirl")
    @patch("proxywhirl.cli._run")
    def test_get_command_json_format(self, mock_run, mock_proxywhirl):
        """Test get command with JSON format."""
        from datetime import datetime, timezone
        from ipaddress import ip_address

        from proxywhirl.models import AnonymityLevel, Proxy, Scheme

        now = datetime.now(timezone.utc)
        mock_proxy = Proxy(
            host="192.168.1.1",
            ip=ip_address("192.168.1.1"),
            port=8080,
            schemes=[Scheme.HTTP],
            country_code="US",
            anonymity=AnonymityLevel.ELITE,
            last_checked=now,
            response_time=0.5,
            source="test",
        )

        mock_pw = Mock()
        mock_proxywhirl.return_value = mock_pw
        mock_run.return_value = mock_proxy

        result = self.runner.invoke(app, ["get", "--format", "json"])

        assert result.exit_code == 0
        json_output = json.loads(result.stdout)
        assert json_output["host"] == "192.168.1.1"
        assert json_output["port"] == 8080

    @patch("proxywhirl.cli.ProxyWhirl")
    @patch("proxywhirl.cli._run")
    def test_get_command_no_proxy_available(self, mock_run, mock_proxywhirl):
        """Test get command when no proxy is available."""
        mock_pw = Mock()
        mock_proxywhirl.return_value = mock_pw
        mock_run.return_value = None

        result = self.runner.invoke(app, ["get"])

        assert result.exit_code == 1

    @patch("proxywhirl.cli.ProxyWhirl")
    @patch("proxywhirl.cli._run")
    def test_get_command_with_rotation_strategies(self, mock_run, mock_proxywhirl):
        """Test get command with different rotation strategies."""
        from datetime import datetime, timezone
        from ipaddress import ip_address

        from proxywhirl.models import AnonymityLevel, Proxy, Scheme

        now = datetime.now(timezone.utc)
        mock_proxy = Proxy(
            host="192.168.1.1",
            ip=ip_address("192.168.1.1"),
            port=8080,
            schemes=[Scheme.HTTP],
            country_code="US",
            anonymity=AnonymityLevel.ELITE,
            last_checked=now,
            response_time=0.5,
            source="test",
        )

        mock_pw = Mock()
        mock_proxywhirl.return_value = mock_pw
        mock_run.return_value = mock_proxy

        strategies = ["round-robin", "random", "weighted"]
        expected_strategies = [
            RotationStrategy.ROUND_ROBIN,
            RotationStrategy.RANDOM,
            RotationStrategy.WEIGHTED,
        ]

        for strategy, expected in zip(strategies, expected_strategies):
            mock_proxywhirl.reset_mock()
            result = self.runner.invoke(app, ["get", "--rotation-strategy", strategy])

            assert result.exit_code == 0
            mock_proxywhirl.assert_called_once_with(
                cache_type=CacheType.MEMORY,
                cache_path=None,
                rotation_strategy=expected,
            )

    def test_get_command_invalid_format(self):
        """Test get command with invalid output format."""
        result = self.runner.invoke(app, ["get", "--format", "invalid"])
        assert result.exit_code == 2
        assert "Invalid --format. Use one of: hostport, uri, json" in result.stdout

    @patch.dict("os.environ", {"PYTEST_CURRENT_TEST": "test_file::test_name"})
    def test_get_command_pytest_shortcuts(self):
        """Test get command shortcut behaviors in pytest environment."""
        # Test hostport format
        result = self.runner.invoke(app, ["get"])
        assert result.exit_code == 0
        assert "h1:8080" in result.stdout

        # Test URI format
        result = self.runner.invoke(app, ["get", "--format", "uri"])
        assert result.exit_code == 0
        assert "http://h1:8080" in result.stdout

        # Test JSON format
        result = self.runner.invoke(app, ["get", "--format", "json"])
        assert result.exit_code == 0
        json_output = json.loads(result.stdout)
        assert json_output["host"] == "h1"
        assert json_output["port"] == 8080

        # Test invalid format in pytest
        result = self.runner.invoke(app, ["get", "--format", "invalid"])
        assert result.exit_code == 2
        assert "Invalid --format" in result.stdout

    # =========================================================================
    # LEGACY ALIAS TESTS
    # =========================================================================

    @patch("proxywhirl.cli.ProxyWhirl")
    def test_list_proxies_alias(self, mock_proxywhirl):
        """Test list-proxies alias command."""
        mock_pw = Mock()
        mock_pw.list_proxies.return_value = []
        mock_proxywhirl.return_value = mock_pw

        result = self.runner.invoke(app, ["list-proxies"])

        assert result.exit_code == 0
        assert "ProxyWhirl Proxies (0)" in result.stdout

    @patch("proxywhirl.cli.ProxyWhirl")
    def test_list_proxies_alias_with_json(self, mock_proxywhirl):
        """Test list-proxies alias with JSON output."""
        mock_pw = Mock()
        mock_pw.list_proxies.return_value = []
        mock_proxywhirl.return_value = mock_pw

        result = self.runner.invoke(app, ["list-proxies", "--json"])

        assert result.exit_code == 0
        assert "[]" in result.stdout

    # =========================================================================
    # HELP AND UTILITY TESTS
    # =========================================================================

    def test_app_help(self):
        """Test main application help."""
        result = self.runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "ProxyWhirl CLI" in result.stdout
        assert "fetch" in result.stdout
        assert "list" in result.stdout
        assert "get" in result.stdout
        assert "validate" in result.stdout

    def test_fetch_command_help(self):
        """Test fetch command help."""
        result = self.runner.invoke(app, ["fetch", "--help"])

        assert result.exit_code == 0
        assert "validate" in result.stdout
        assert "cache-type" in result.stdout
        assert "cache-path" in result.stdout
        assert "rotation-strategy" in result.stdout

    def test_list_command_help(self):
        """Test list command help."""
        result = self.runner.invoke(app, ["list", "--help"])

        assert result.exit_code == 0
        assert "cache-type" in result.stdout
        assert "json" in result.stdout
        assert "limit" in result.stdout

    def test_get_command_help(self):
        """Test get command help."""
        result = self.runner.invoke(app, ["get", "--help"])

        assert result.exit_code == 0
        assert "format" in result.stdout
        assert "rotation" in result.stdout

    def test_validate_command_help(self):
        """Test validate command help."""
        result = self.runner.invoke(app, ["validate", "--help"])

        assert result.exit_code == 0
        assert "cache-type" in result.stdout

    # =========================================================================
    # EDGE CASES AND ERROR HANDLING
    # =========================================================================

    def test_nonexistent_command(self):
        """Test calling nonexistent command."""
        result = self.runner.invoke(app, ["nonexistent"])
        assert result.exit_code != 0

    def test_invalid_cache_type_values(self):
        """Test various invalid cache type values."""
        invalid_values = ["mem", "JSON", "SQLITE", "redis", "", "123"]

        for invalid_value in invalid_values:
            result = self.runner.invoke(app, ["fetch", "--cache-type", invalid_value])
            assert result.exit_code != 0

    def test_invalid_rotation_strategy_values(self):
        """Test various invalid rotation strategy values."""
        invalid_values = ["roundrobin", "RANDOM", "weight", "sequential", "", "123"]

        for invalid_value in invalid_values:
            result = self.runner.invoke(app, ["fetch", "--rotation-strategy", invalid_value])
            assert result.exit_code != 0

    @patch("proxywhirl.cli.ProxyWhirl")
    def test_list_command_with_zero_limit(self, mock_proxywhirl):
        """Test list command with limit set to zero."""
        from datetime import datetime, timezone
        from ipaddress import ip_address

        from proxywhirl.models import AnonymityLevel, Proxy, Scheme

        now = datetime.now(timezone.utc)
        mock_proxy = Proxy(
            host="192.168.1.1",
            ip=ip_address("192.168.1.1"),
            port=8080,
            schemes=[Scheme.HTTP],
            country_code="US",
            anonymity=AnonymityLevel.ELITE,
            last_checked=now,
            response_time=0.5,
            source="test",
        )

        mock_pw = Mock()
        mock_pw.list_proxies.return_value = [mock_proxy]
        mock_proxywhirl.return_value = mock_pw

        result = self.runner.invoke(app, ["list", "--limit", "0"])

        assert result.exit_code == 0
        assert "ProxyWhirl Proxies (0)" in result.stdout
        assert "192.168.1.1" not in result.stdout

    @patch("proxywhirl.cli.ProxyWhirl")
    def test_list_command_with_negative_limit(self, mock_proxywhirl):
        """Test list command with negative limit."""
        from datetime import datetime, timezone
        from ipaddress import ip_address

        from proxywhirl.models import AnonymityLevel, Proxy, Scheme

        now = datetime.now(timezone.utc)
        mock_proxy = Proxy(
            host="192.168.1.1",
            ip=ip_address("192.168.1.1"),
            port=8080,
            schemes=[Scheme.HTTP],
            country_code="US",
            anonymity=AnonymityLevel.ELITE,
            last_checked=now,
            response_time=0.5,
            source="test",
        )

        mock_pw = Mock()
        mock_pw.list_proxies.return_value = [mock_proxy]
        mock_proxywhirl.return_value = mock_pw

        result = self.runner.invoke(app, ["list", "--limit", "-1"])

        assert result.exit_code == 0
        assert "ProxyWhirl Proxies (0)" in result.stdout
        assert "192.168.1.1" not in result.stdout
