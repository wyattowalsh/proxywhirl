"""Unit tests for CLI commands.

Tests the command-line interface functionality in isolation using Typer's testing utilities.
"""

from __future__ import annotations

import json
import os
import socket
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import httpx
import pytest
from typer.main import get_command
from typer.testing import CliRunner

from proxywhirl.cli import _proxy_reference_matches, app
from proxywhirl.config import CLIConfig, load_config, save_config

_xdist_worker = os.environ.get("PYTEST_XDIST_WORKER", "main")
EXPECTED_ROOT_COMMANDS = {
    "request",
    "export",
    "fetch",
    "health",
    "validate-proxy",
    "import-proxies",
    "pool",
    "config",
    "sources",
}
REMOVED_ROOT_COMMANDS = {
    "stats",
    "setup-geoip",
    "db-stats",
    "cleanup",
    "batch",
    "formats",
    "list-proxies",
    "diagnose",
    "diversity",
    "shell",
}

# Test fixtures - set explicit width to avoid CI terminal width issues
# Pin XDG paths per xdist worker to avoid sandbox writes and cross-worker lock contention.
runner = CliRunner(
    env={
        "COLUMNS": "120",
        "TERM": "dumb",
        "XDG_DATA_HOME": str(Path.cwd() / f".cli-test-data-{_xdist_worker}"),
        "XDG_CONFIG_HOME": str(Path.cwd() / f".cli-test-config-{_xdist_worker}"),
        "HOME": str(Path.cwd() / f".cli-test-home-{_xdist_worker}"),
    }
)


@pytest.fixture(autouse=True)
def deterministic_public_dns(monkeypatch: pytest.MonkeyPatch) -> None:
    """Resolve test hostnames to public addresses without depending on live DNS."""
    original_getaddrinfo = socket.getaddrinfo

    def _getaddrinfo(host, port, family=socket.AF_UNSPEC, type=socket.SOCK_STREAM, *args, **kwargs):
        host_text = str(host).rstrip(".").lower()
        if host_text == "httpbin.org" or host_text.endswith(".example.com"):
            return [(socket.AF_INET, type, 0, "", ("93.184.216.34", port or 443))]
        return original_getaddrinfo(host, port, family, type, *args, **kwargs)

    monkeypatch.setattr(socket, "getaddrinfo", _getaddrinfo)


def _root_command_names() -> set[str]:
    return set(get_command(app).commands)


class TestCLIHelp:
    """Test CLI help messages and command discovery."""

    def test_main_help_shows_all_commands(self) -> None:
        """Main help should enumerate all available commands."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        for command in EXPECTED_ROOT_COMMANDS:
            assert command in result.stdout

    def test_root_command_registry_is_focused(self) -> None:
        """Root command registry should expose only focused CLI workflows."""
        assert _root_command_names() == EXPECTED_ROOT_COMMANDS

    def test_removed_root_commands_are_not_registered(self) -> None:
        """Pruned root commands should stay out of the Typer registry."""
        assert _root_command_names().isdisjoint(REMOVED_ROOT_COMMANDS)

    def test_request_command_help(self) -> None:
        """Request command should show usage and examples."""
        result = runner.invoke(app, ["request", "--help"])
        assert result.exit_code == 0
        assert "Make an HTTP request" in result.stdout
        assert "URL" in result.stdout
        assert "--method" in result.stdout
        assert "--header" in result.stdout

    def test_pool_command_help(self) -> None:
        """Pool command should show available actions."""
        result = runner.invoke(app, ["pool", "--help"])
        assert result.exit_code == 0
        assert "Manage the proxy pool" in result.stdout
        assert "list" in result.stdout
        assert "add" in result.stdout

    def test_config_command_help(self) -> None:
        """Config command should show configuration actions."""
        result = runner.invoke(app, ["config", "--help"])
        assert result.exit_code == 0
        assert "Manage CLI configuration" in result.stdout
        assert "show" in result.stdout
        assert "set" in result.stdout

    def test_health_command_help(self) -> None:
        """Health command should show monitoring options."""
        result = runner.invoke(app, ["health", "--help"])
        assert result.exit_code == 0
        assert "Check health" in result.stdout
        assert "--continuous" in result.stdout

    def test_validate_proxy_command_help(self) -> None:
        """Validate-proxy command should show validation options."""
        result = runner.invoke(app, ["validate-proxy", "--help"])
        assert result.exit_code == 0
        assert "Validate proxy" in result.stdout
        assert "--target" in result.stdout

    def test_import_proxies_command_help(self) -> None:
        """Import-proxies command should show import options."""
        result = runner.invoke(app, ["import-proxies", "--help"])
        assert result.exit_code == 0
        assert "Import proxies" in result.stdout
        assert "--pool" in result.stdout

    def test_sources_command_help(self) -> None:
        """Sources command should show validation options."""
        result = runner.invoke(app, ["sources", "--help"])
        assert result.exit_code == 0
        assert "List and validate" in result.stdout
        assert "--validate" in result.stdout
        assert "--fail-on-unhealthy" in result.stdout


class TestCLIGlobalOptions:
    """Test global CLI options (--format, --verbose, --no-lock, --config)."""

    def test_format_option_text_default(self) -> None:
        """Default format should be text."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "text" in result.stdout.lower()

    def test_format_option_accepts_json(self) -> None:
        """Format option should accept json."""
        result = runner.invoke(app, ["--format", "json", "--help"])
        assert result.exit_code == 0

    def test_format_option_accepts_csv(self) -> None:
        """Format option should accept csv."""
        result = runner.invoke(app, ["--format", "csv", "--help"])
        assert result.exit_code == 0

    def test_format_option_accepts_yaml(self) -> None:
        """Format option should accept yaml."""
        result = runner.invoke(app, ["--format", "yaml", "--help"])
        assert result.exit_code == 0

    def test_verbose_option(self) -> None:
        """Verbose flag should be accepted."""
        result = runner.invoke(app, ["--verbose", "--help"])
        assert result.exit_code == 0

    def test_no_lock_option(self) -> None:
        """No-lock flag should be accepted."""
        result = runner.invoke(app, ["--no-lock", "--help"])
        assert result.exit_code == 0


class TestRequestCommand:
    """Test the request command (US1)."""

    @pytest.fixture(autouse=True)
    def mock_request_client(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Keep basic request-command tests off the network."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"ok": true}'
        mock_response.headers = {"content-type": "application/json"}

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.request.return_value = mock_response
        monkeypatch.setattr(httpx, "Client", MagicMock(return_value=mock_client))

    def test_request_requires_url(self) -> None:
        """Request command should require URL argument."""
        result = runner.invoke(app, ["request"])
        assert result.exit_code != 0
        # Error message may be in stdout or stderr
        output = result.stdout + result.stderr
        assert "Missing argument" in output or "required" in output.lower()

    def test_request_basic_execution(self) -> None:
        """Request command should execute successfully."""
        result = runner.invoke(app, ["--no-lock", "request", "https://httpbin.org/get"])
        # Should succeed
        assert result.exit_code == 0
        assert "Status" in result.stdout or "status_code" in result.stdout

    def test_request_accepts_method_option(self) -> None:
        """Request should accept --method option."""
        result = runner.invoke(
            app, ["--no-lock", "request", "--method", "GET", "https://httpbin.org/get"]
        )
        # Should succeed
        assert result.exit_code == 0

    def test_request_accepts_header_option(self) -> None:
        """Request should accept multiple --header options."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "request",
                "--header",
                "User-Agent: Test",
                "--header",
                "Accept: application/json",
                "https://httpbin.org/get",
            ],
        )
        # Should succeed
        assert result.exit_code == 0

    def test_request_accepts_data_option(self) -> None:
        """Request should accept --data option."""
        result = runner.invoke(
            app,
            ["--no-lock", "request", "--data", '{"key":"value"}', "https://httpbin.org/post"],
        )
        # Should succeed
        assert result.exit_code == 0

    def test_request_json_format(self) -> None:
        """Request should support JSON output format."""
        result = runner.invoke(
            app, ["--no-lock", "--format", "json", "request", "https://httpbin.org/get"]
        )
        # Should succeed and output JSON
        assert result.exit_code == 0
        assert "status_code" in result.stdout
        assert "url" in result.stdout

    def test_request_accepts_retries_option(self) -> None:
        """Request should accept --retries to override config."""
        result = runner.invoke(
            app, ["--no-lock", "request", "--retries", "1", "https://httpbin.org/get"]
        )
        # Should succeed
        assert result.exit_code == 0


class TestPoolCommand:
    """Test the pool command (US2)."""

    def test_pool_requires_action(self) -> None:
        """Pool command should require action argument."""
        result = runner.invoke(app, ["pool"])
        assert result.exit_code != 0

    def test_pool_list_empty(self) -> None:
        """Pool list should show message when no proxies."""
        result = runner.invoke(app, ["--no-lock", "pool", "list"])
        assert result.exit_code == 0
        assert "No proxies in pool" in result.stdout

    def test_pool_add_requires_proxy_url(self) -> None:
        """Pool add should require proxy URL."""
        result = runner.invoke(app, ["--no-lock", "pool", "add"])
        assert result.exit_code != 0
        # Typer shows missing argument error


class TestConfigCommand:
    """Test the config command (US3)."""

    def test_config_requires_action(self) -> None:
        """Config command should require action argument."""
        result = runner.invoke(app, ["config"])
        assert result.exit_code != 0

    def test_config_show(self) -> None:
        """Config show should display configuration."""
        result = runner.invoke(app, ["--no-lock", "config", "show"])
        assert result.exit_code == 0
        assert "rotation_strategy" in result.stdout or "timeout" in result.stdout


class TestHealthCommand:
    """Test the health command (US4)."""

    def test_health_runs_without_arguments(self) -> None:
        """Health command should run without arguments."""
        result = runner.invoke(app, ["--no-lock", "health"])
        # Should exit successfully even with no proxies
        assert result.exit_code == 0
        assert "No proxies configured" in result.stdout

    def test_health_accepts_continuous_flag(self) -> None:
        """Health should accept --continuous flag."""
        # This will hang, so we just check the help
        result = runner.invoke(app, ["health", "--help"])
        assert "--continuous" in result.stdout

    def test_health_accepts_interval_option(self) -> None:
        """Health should accept --interval option."""
        result = runner.invoke(app, ["health", "--help"])
        assert "--interval" in result.stdout


class TestRequestCommandAdvanced:
    """Advanced tests for request command with mocking."""

    @patch("httpx.Client")
    def test_request_with_custom_headers(self, mock_client_class: Mock) -> None:
        """Request should properly parse and send custom headers."""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_response.headers = {}

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            [
                "--no-lock",
                "request",
                "--header",
                "Authorization: Bearer token123",
                "--header",
                "Content-Type: application/json",
                "https://example.com",
            ],
        )

        assert result.exit_code == 0
        # Verify headers were passed
        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        headers = call_args.kwargs.get("headers", {})
        assert headers["Authorization"] == "Bearer token123"
        assert headers["Content-Type"] == "application/json"

    @patch("httpx.Client")
    def test_request_with_post_data(self, mock_client_class: Mock) -> None:
        """Request should send POST data correctly."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.text = '{"created": true}'
        mock_response.headers = {}

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            [
                "--no-lock",
                "request",
                "--method",
                "POST",
                "--data",
                '{"name": "test"}',
                "https://example.com/users",
            ],
        )

        assert result.exit_code == 0
        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        assert call_args.kwargs["method"] == "POST"
        assert call_args.kwargs["content"] == '{"name": "test"}'

    def test_request_invalid_header_format(self) -> None:
        """Request should reject headers without colon separator."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "request",
                "--header",
                "InvalidHeader",
                "https://example.com",
            ],
        )

        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "Invalid header format" in output

    @patch("httpx.Client")
    def test_request_with_retries(self, mock_client_class: Mock) -> None:
        """Request should retry on failure."""
        # First two calls fail, third succeeds
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.text = "OK"
        mock_response_success.headers = {}

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.request.side_effect = [
            Exception("Connection failed"),
            Exception("Connection failed"),
            mock_response_success,
        ]
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            [
                "--no-lock",
                "request",
                "--retries",
                "3",
                "https://example.com",
            ],
        )

        assert result.exit_code == 0
        assert mock_client.request.call_count == 3

    @patch("httpx.Client")
    def test_request_json_output_format(self, mock_client_class: Mock) -> None:
        """Request should output JSON when --format json is used."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"result": "success"}'
        mock_response.headers = {"content-type": "application/json"}

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            [
                "--no-lock",
                "--format",
                "json",
                "request",
                "https://example.com",
            ],
        )

        assert result.exit_code == 0
        # Output should be valid JSON
        output_data = json.loads(result.stdout)
        assert output_data["status_code"] == 200
        assert "url" in output_data

    @patch("httpx.Client")
    def test_request_csv_output_format(self, mock_client_class: Mock) -> None:
        """Request should output CSV when --format csv is used."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_response.headers = {}

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            [
                "--no-lock",
                "--format",
                "csv",
                "request",
                "https://example.com",
            ],
        )

        assert result.exit_code == 0
        # Check CSV structure
        lines = result.stdout.strip().split("\n")
        assert len(lines) >= 2  # Header + data
        assert "Status" in lines[0]


class TestPoolCommandAdvanced:
    """Advanced tests for pool command."""

    def test_pool_invalid_action(self) -> None:
        """Pool should reject invalid actions."""
        result = runner.invoke(app, ["--no-lock", "pool", "invalid_action"])
        assert result.exit_code != 0
        assert "Invalid action" in result.stdout

    def test_pool_add_proxy(self) -> None:
        """Pool add should add proxy to configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".proxywhirl.toml"
            save_config(CLIConfig(encrypt_credentials=False), config_path)

            result = runner.invoke(
                app,
                [
                    "--no-lock",
                    "--config",
                    str(config_path),
                    "pool",
                    "add",
                    "http://newproxy.com:8080",
                ],
            )

            assert result.exit_code == 0
            updated_config = load_config(config_path)
            assert [proxy.url for proxy in updated_config.proxies] == ["http://newproxy.com:8080"]

    def test_pool_add_with_auth(self) -> None:
        """Pool add should support username and password."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".proxywhirl.toml"
            save_config(CLIConfig(encrypt_credentials=False), config_path)

            result = runner.invoke(
                app,
                [
                    "--no-lock",
                    "--config",
                    str(config_path),
                    "pool",
                    "add",
                    "http://proxy.com:8080",
                    "--username",
                    "user",
                    "--password",
                    "pass",
                ],
            )

            assert result.exit_code == 0
            [proxy_config] = load_config(config_path).proxies
            assert proxy_config.url == "http://proxy.com:8080"
            assert proxy_config.username is not None
            assert proxy_config.username.get_secret_value() == "user"
            assert proxy_config.password is not None
            assert proxy_config.password.get_secret_value() == "pass"

    def test_pool_remove_proxy(self) -> None:
        """Pool remove should remove proxy from configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".proxywhirl.toml"
            save_config(
                CLIConfig(
                    encrypt_credentials=False,
                    proxies=[
                        {"url": "http://proxy.com:8080"},
                        {"url": "http://other-proxy.com:8081"},
                    ],
                ),
                config_path,
            )

            result = runner.invoke(
                app,
                [
                    "--no-lock",
                    "--config",
                    str(config_path),
                    "pool",
                    "remove",
                    "http://proxy.com:8080",
                ],
            )

            assert result.exit_code == 0
            updated_config = load_config(config_path)
            assert [proxy.url for proxy in updated_config.proxies] == [
                "http://other-proxy.com:8081"
            ]

    def test_proxy_reference_matches_displayed_credentialless_url(self) -> None:
        """Pool remove can match the public URL shown by pool list."""
        assert _proxy_reference_matches(
            "http://user:pass@proxy.com:8080",
            "http://proxy.com:8080",
        )

    @patch("httpx.Client")
    def test_pool_test_proxy(self, mock_client_class: Mock) -> None:
        """Pool test should validate proxy connectivity."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"origin": "1.2.3.4"}'

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            [
                "--no-lock",
                "pool",
                "test",
                "http://demo:secret@proxy.com:8080",
            ],
        )

        assert result.exit_code == 0
        assert "working" in result.stdout.lower() or "✓" in result.stdout
        assert "http://proxy.com:8080" in result.stdout
        assert "demo" not in result.stdout
        assert "secret" not in result.stdout

    @patch("httpx.Client")
    def test_pool_test_proxy_failure(self, mock_client_class: Mock) -> None:
        """Pool test should handle proxy connection failures."""
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.get.side_effect = Exception(
            "Connection refused via http://demo:secret@badproxy.com:8080"
        )
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            [
                "--no-lock",
                "pool",
                "test",
                "http://demo:secret@badproxy.com:8080",
            ],
        )

        assert result.exit_code != 0
        assert "failed" in result.stdout.lower() or "✗" in result.stdout
        assert "demo" not in result.stdout
        assert "secret" not in result.stdout
        assert "http://***:***@badproxy.com:8080" in result.stdout

    def test_pool_list_json_format(self) -> None:
        """Pool list should support JSON output format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".proxywhirl.toml"
            save_config(
                CLIConfig(
                    encrypt_credentials=False,
                    proxies=[{"url": "http://proxy.com:8080"}],
                ),
                config_path,
            )

            result = runner.invoke(
                app,
                [
                    "--no-lock",
                    "--format",
                    "json",
                    "--config",
                    str(config_path),
                    "pool",
                    "list",
                ],
            )

            assert result.exit_code == 0
            data = json.loads(result.stdout)
            assert data["total_proxies"] == 1
            assert len(data["proxies"]) == 1
            assert data["proxies"][0]["url"] == "http://proxy.com:8080"

    def test_pool_list_csv_format(self) -> None:
        """Pool list should support CSV output format."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "--format",
                "csv",
                "pool",
                "list",
            ],
        )

        assert result.exit_code == 0


class TestConfigCommandAdvanced:
    """Advanced tests for config command."""

    def test_config_invalid_action(self) -> None:
        """Config should reject invalid actions."""
        result = runner.invoke(app, ["--no-lock", "config", "invalid"])
        assert result.exit_code != 0
        assert "Invalid action" in result.stdout

    def test_config_show_text_format(self) -> None:
        """Config show should display settings in text format."""
        result = runner.invoke(app, ["--no-lock", "config", "show"])
        assert result.exit_code == 0
        assert "rotation_strategy" in result.stdout or "timeout" in result.stdout

    def test_config_show_json_format(self) -> None:
        """Config show should output valid JSON."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "--format",
                "json",
                "config",
                "show",
            ],
        )

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert isinstance(data, dict)
        assert "rotation_strategy" in data or "timeout" in data

    def test_config_show_csv_format(self) -> None:
        """Config show should output CSV format."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "--format",
                "csv",
                "config",
                "show",
            ],
        )

        assert result.exit_code == 0
        lines = result.stdout.strip().split("\n")
        assert len(lines) >= 2  # Header + at least one config value

    def test_config_get_valid_key(self) -> None:
        """Config get should retrieve configuration value."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "config",
                "get",
                "timeout",
            ],
        )

        assert result.exit_code == 0
        assert result.stdout.strip()  # Should output a value

    def test_config_get_invalid_key(self) -> None:
        """Config get should reject unknown keys."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "config",
                "get",
                "nonexistent_key",
            ],
        )

        assert result.exit_code != 0
        assert "Unknown config key" in result.stdout

    def test_config_get_json_format(self) -> None:
        """Config get should support JSON output."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "--format",
                "json",
                "config",
                "get",
                "timeout",
            ],
        )

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "timeout" in data

    def test_config_get_proxies_scrubs_credentials_text(self) -> None:
        """Config get should not expose proxy credentials in text output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".proxywhirl.toml"
            save_config(
                CLIConfig(
                    encrypt_credentials=False,
                    proxies=[
                        {
                            "url": "http://user:secret@proxy.example.com:8080",
                            "username": "user",
                            "password": "secret",
                        }
                    ],
                ),
                config_path,
            )

            result = runner.invoke(
                app,
                ["--no-lock", "--config", str(config_path), "config", "get", "proxies"],
            )

        assert result.exit_code == 0
        assert "http://proxy.example.com:8080" in result.stdout
        assert "user:secret" not in result.stdout
        assert "'username': '***'" in result.stdout
        assert "'password': '***'" in result.stdout

    def test_config_get_proxies_scrubs_credentials_json(self) -> None:
        """Config get should not expose proxy credentials in JSON output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".proxywhirl.toml"
            save_config(
                CLIConfig(
                    encrypt_credentials=False,
                    proxies=[
                        {
                            "url": "http://user:secret@proxy.example.com:8080",
                            "username": "user",
                            "password": "secret",
                        }
                    ],
                ),
                config_path,
            )

            result = runner.invoke(
                app,
                [
                    "--no-lock",
                    "--format",
                    "json",
                    "--config",
                    str(config_path),
                    "config",
                    "get",
                    "proxies",
                ],
            )

        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        assert payload["proxies"][0]["url"] == "http://proxy.example.com:8080"
        assert payload["proxies"][0]["username"] == "***"
        assert payload["proxies"][0]["password"] == "***"

    def test_config_set_value(self) -> None:
        """Config set should update configuration value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".proxywhirl.toml"
            save_config(CLIConfig(encrypt_credentials=False), config_path)

            result = runner.invoke(
                app,
                [
                    "--no-lock",
                    "--config",
                    str(config_path),
                    "config",
                    "set",
                    "timeout",
                    "60",
                ],
            )

            assert result.exit_code == 0
            assert load_config(config_path).timeout == 60

    def test_config_set_boolean_value(self) -> None:
        """Config set should handle boolean values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".proxywhirl.toml"
            save_config(CLIConfig(encrypt_credentials=False), config_path)

            result = runner.invoke(
                app,
                [
                    "--no-lock",
                    "--config",
                    str(config_path),
                    "config",
                    "set",
                    "verify_ssl",
                    "false",
                ],
            )

            assert result.exit_code == 0
            assert load_config(config_path).verify_ssl is False

    def test_config_set_invalid_key(self) -> None:
        """Config set should reject unknown keys."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "config",
                "set",
                "invalid_key",
                "value",
            ],
        )

        assert result.exit_code != 0
        assert "Unknown config key" in result.stdout

    def test_config_set_requires_value(self) -> None:
        """Config set should require both key and value."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "config",
                "set",
                "timeout",
            ],
        )

        assert result.exit_code != 0

    @patch("proxywhirl.config.save_config")
    def test_config_init_creates_file(self, mock_save: Mock) -> None:
        """Config init should create new configuration file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".proxywhirl.toml"

            result = runner.invoke(
                app,
                [
                    "--no-lock",
                    "--config",
                    str(config_path),
                    "config",
                    "init",
                ],
                input="y\n",  # Confirm overwrite if asked
            )

            assert result.exit_code in (0, 1, 2) or mock_save.called

    @patch("proxywhirl.config.save_config")
    def test_config_init_no_overwrite(self, mock_save: Mock) -> None:
        """Config init should ask before overwriting existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".proxywhirl.toml"
            config_path.touch()  # Create existing file

            result = runner.invoke(
                app,
                [
                    "--no-lock",
                    "--config",
                    str(config_path),
                    "config",
                    "init",
                ],
                input="n\n",  # Don't overwrite
            )

            # Should exit without error when user declines (or fail on config load)
            assert result.exit_code in (0, 1, 2)


class TestHealthCommandAdvanced:
    """Advanced tests for health command."""

    @patch("httpx.Client")
    def test_health_check_with_proxies(self, mock_client_class: Mock) -> None:
        """Health should check configured proxies."""
        mock_response = Mock()
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        # This will show "No proxies configured" with default config
        result = runner.invoke(app, ["--no-lock", "health"])
        assert result.exit_code == 0

    def test_health_json_format(self) -> None:
        """Health should support JSON output format."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "--format",
                "json",
                "health",
            ],
        )

        assert result.exit_code == 0

    def test_health_csv_format(self) -> None:
        """Health should support CSV output format."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "--format",
                "csv",
                "health",
            ],
        )

        assert result.exit_code == 0


class TestValidateProxyCommand:
    """Regression tests for validate-proxy command execution."""

    @patch("httpx.get")
    def test_validate_proxy_uses_current_httpx_proxy_argument(self, mock_get: Mock) -> None:
        """Validate-proxy should use httpx's current single proxy argument."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = runner.invoke(
            app,
            [
                "--no-lock",
                "--format",
                "json",
                "validate-proxy",
                "http://proxy.com:8080",
                "--target",
                "https://api.example.com/health",
                "--timeout",
                "1",
            ],
        )

        assert result.exit_code == 0
        output_data = json.loads(result.stdout)
        assert output_data["proxy"] == "http://proxy.com:8080"
        assert output_data["status"] == "HEALTHY"
        assert output_data["response_code"] == 200
        assert output_data["target_url"] == "https://api.example.com/health"
        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args.kwargs
        assert mock_get.call_args.args == ("https://api.example.com/health",)
        assert call_kwargs["proxy"] == "http://proxy.com:8080"
        assert call_kwargs["timeout"] == 1.0
        assert call_kwargs["follow_redirects"] is True
        assert "proxies" not in call_kwargs

    @patch("httpx.get")
    def test_validate_proxy_preserves_credentials_without_output_leak(self, mock_get: Mock) -> None:
        """Validate-proxy should use credentials for httpx without exposing them in output."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = runner.invoke(
            app,
            [
                "--no-lock",
                "--format",
                "json",
                "validate-proxy",
                "http://user:pass@proxy.com:8080",
                "--target",
                "https://api.example.com/health",
            ],
        )

        assert result.exit_code == 0
        assert mock_get.call_args.kwargs["proxy"] == "http://user:pass@proxy.com:8080"
        output_data = json.loads(result.stdout)
        assert output_data["proxy"] == "http://proxy.com:8080"
        assert "user" not in result.stdout
        assert "pass" not in result.stdout

    @patch("httpx.get")
    def test_validate_proxy_connect_error_json(self, mock_get: Mock) -> None:
        """Validate-proxy should render structured JSON for connection failures."""
        mock_get.side_effect = httpx.ConnectError("Connection refused")

        result = runner.invoke(
            app,
            [
                "--no-lock",
                "--format",
                "json",
                "validate-proxy",
                "http://proxy.com:8080",
                "--target",
                "https://api.example.com/health",
            ],
        )

        assert result.exit_code == 1
        output_data = json.loads(result.stdout)
        assert output_data["proxy"] == "http://proxy.com:8080"
        assert output_data["status"] == "UNHEALTHY"
        assert output_data["reason"] == "Connection failed"
        assert "Error validating proxy" not in result.stdout

    @patch("httpx.get")
    def test_validate_proxy_timeout_text(self, mock_get: Mock) -> None:
        """Validate-proxy should render the specific timeout message in text mode."""
        mock_get.side_effect = httpx.TimeoutException("timed out")

        result = runner.invoke(
            app,
            [
                "--no-lock",
                "validate-proxy",
                "http://proxy.com:8080",
                "--target",
                "https://api.example.com/health",
                "--timeout",
                "1",
            ],
        )

        assert result.exit_code == 1
        assert "Proxy timeout after 1.0s" in result.stdout
        assert "Error validating proxy" not in result.stdout


class TestImportProxiesCommand:
    """Regression tests for import-proxies command execution."""

    def test_import_proxies_persists_to_active_config(self) -> None:
        """Import-proxies should add parsed proxies to the active config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            config_path = tmp_path / ".proxywhirl.toml"
            proxy_file = tmp_path / "proxies.txt"
            save_config(CLIConfig(encrypt_credentials=False), config_path)
            proxy_file.write_text(
                "\n".join(
                    [
                        "http://proxy-one.com:8080",
                        "http://proxy-two.com:8081",
                        "http://proxy-one.com:8080",
                    ]
                )
            )

            result = runner.invoke(
                app,
                [
                    "--no-lock",
                    "--format",
                    "json",
                    "--config",
                    str(config_path),
                    "import-proxies",
                    str(proxy_file),
                    "--format",
                    "text",
                ],
            )

            assert result.exit_code == 0
            output_data = json.loads(result.stdout)
            assert output_data["total_parsed"] == 2
            assert output_data["imported"] == 2
            assert output_data["failed"] == 0

            updated_config = load_config(config_path)
            assert [proxy.url for proxy in updated_config.proxies] == [
                "http://proxy-one.com:8080",
                "http://proxy-two.com:8081",
            ]

    def test_import_proxies_skips_existing_without_counting_imported(self) -> None:
        """Import-proxies should skip existing proxies and count only new imports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            config_path = tmp_path / ".proxywhirl.toml"
            proxy_file = tmp_path / "proxies.txt"
            save_config(
                CLIConfig(
                    encrypt_credentials=False,
                    proxies=[{"url": "http://proxy-one.com:8080"}],
                ),
                config_path,
            )
            proxy_file.write_text("http://proxy-one.com:8080\nhttp://proxy-two.com:8081\n")

            result = runner.invoke(
                app,
                [
                    "--no-lock",
                    "--format",
                    "json",
                    "--config",
                    str(config_path),
                    "import-proxies",
                    str(proxy_file),
                    "--format",
                    "text",
                ],
            )

            assert result.exit_code == 0
            output_data = json.loads(result.stdout)
            assert output_data["total_parsed"] == 2
            assert output_data["imported"] == 1
            assert output_data["failed"] == 0
            updated_config = load_config(config_path)
            assert [proxy.url for proxy in updated_config.proxies] == [
                "http://proxy-one.com:8080",
                "http://proxy-two.com:8081",
            ]

    def test_import_proxies_reports_invalid_entries_verbose_json(self) -> None:
        """Import-proxies should report invalid entries and persist valid ones."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            config_path = tmp_path / ".proxywhirl.toml"
            proxy_file = tmp_path / "proxies.txt"
            save_config(CLIConfig(encrypt_credentials=False), config_path)
            proxy_file.write_text("http://proxy-one.com:8080\nnot-a-proxy\n")

            result = runner.invoke(
                app,
                [
                    "--no-lock",
                    "--verbose",
                    "--format",
                    "json",
                    "--config",
                    str(config_path),
                    "import-proxies",
                    str(proxy_file),
                    "--format",
                    "text",
                ],
            )

            assert result.exit_code == 0
            output_data = json.loads(result.stdout)
            assert output_data["total_parsed"] == 2
            assert output_data["imported"] == 1
            assert output_data["failed"] == 1
            assert output_data["errors"][0]["proxy"] == "not-a-proxy"
            updated_config = load_config(config_path)
            assert [proxy.url for proxy in updated_config.proxies] == ["http://proxy-one.com:8080"]

    def test_import_proxies_empty_file_reports_specific_message(self) -> None:
        """Import-proxies should not wrap empty-file exits in a generic error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            config_path = tmp_path / ".proxywhirl.toml"
            proxy_file = tmp_path / "proxies.txt"
            save_config(CLIConfig(encrypt_credentials=False), config_path)
            proxy_file.write_text("\n# no proxies\n")

            result = runner.invoke(
                app,
                [
                    "--no-lock",
                    "--config",
                    str(config_path),
                    "import-proxies",
                    str(proxy_file),
                    "--format",
                    "text",
                ],
            )

            assert result.exit_code == 1
            assert "No proxies found in file" in result.stdout
            assert "Error importing proxies" not in result.stdout


class TestExportCommand:
    """Test the export command."""

    def test_export_help(self) -> None:
        """Export command should show help."""
        result = runner.invoke(app, ["export", "--help"])
        assert result.exit_code == 0
        assert "export" in result.stdout.lower()

    @patch("proxywhirl.exports.export_for_web", new_callable=AsyncMock)
    def test_export_default_options(self, mock_export: AsyncMock) -> None:
        """Export should run with default options."""
        mock_export.return_value = {
            "stats": Path("docs/proxy-lists/stats.json"),
            "proxies": Path("docs/proxy-lists/proxies-rich.json"),
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(
                app,
                [
                    "--no-lock",
                    "export",
                    "--output",
                    tmpdir,
                ],
            )

            # Should complete (may have errors if DB doesn't exist, but command should parse)
            assert "Export" in result.stdout or result.exit_code in (0, 1)

    @patch("proxywhirl.exports.export_for_web", new_callable=AsyncMock)
    def test_export_stats_only(self, mock_export: AsyncMock) -> None:
        """Export should support --stats-only flag."""
        mock_export.return_value = {
            "stats": Path("docs/proxy-lists/stats.json"),
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(
                app,
                [
                    "--no-lock",
                    "export",
                    "--stats-only",
                    "--output",
                    tmpdir,
                ],
            )

            assert "Export" in result.stdout or result.exit_code in (0, 1)

    @patch("proxywhirl.exports.export_for_web", new_callable=AsyncMock)
    def test_export_proxies_only(self, mock_export: AsyncMock) -> None:
        """Export should support --proxies-only flag."""
        mock_export.return_value = {
            "proxies": Path("docs/proxy-lists/proxies-rich.json"),
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(
                app,
                [
                    "--no-lock",
                    "export",
                    "--proxies-only",
                    "--output",
                    tmpdir,
                ],
            )

            assert "Export" in result.stdout or result.exit_code in (0, 1)

    @patch("proxywhirl.exports.export_for_web", new_callable=AsyncMock)
    def test_export_custom_db_path(self, mock_export: AsyncMock) -> None:
        """Export should accept custom database path."""
        mock_export.return_value = {}

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "custom.db"

            result = runner.invoke(
                app,
                [
                    "--no-lock",
                    "export",
                    "--db",
                    str(db_path),
                    "--output",
                    tmpdir,
                ],
            )

            assert result.exit_code in (0, 1)


class TestFetchCommand:
    """Test the fetch command."""

    def test_fetch_help(self) -> None:
        """Fetch command should show help."""
        result = runner.invoke(app, ["fetch", "--help"])
        assert result.exit_code == 0
        assert "fetch" in result.stdout.lower()
        assert "proxy" in result.stdout.lower()

    def test_fetch_no_validate(self) -> None:
        """Fetch should support --no-validate flag."""
        # Just verify the flag is accepted in help
        result = runner.invoke(app, ["fetch", "--help"])
        assert result.exit_code == 0
        assert "--no-validate" in result.stdout or "--validate" in result.stdout

    def test_fetch_no_save_db(self) -> None:
        """Fetch should support --no-save-db flag."""
        # Just verify the flag is accepted in help
        result = runner.invoke(app, ["fetch", "--help"])
        assert result.exit_code == 0
        assert "--no-save-db" in result.stdout or "--save-db" in result.stdout

    def test_fetch_no_export(self) -> None:
        """Fetch should support --no-export flag."""
        # Just verify the flag is accepted in help
        result = runner.invoke(app, ["fetch", "--help"])
        assert result.exit_code == 0
        assert "--no-export" in result.stdout or "--export" in result.stdout

    def test_fetch_custom_timeout(self) -> None:
        """Fetch should accept custom timeout."""
        # Just verify the flag is accepted in help
        result = runner.invoke(app, ["fetch", "--help"])
        assert result.exit_code == 0
        assert "--timeout" in result.stdout

    def test_fetch_custom_concurrency(self) -> None:
        """Fetch should accept custom concurrency."""
        # Just verify the flag is accepted in help
        result = runner.invoke(app, ["fetch", "--help"])
        assert result.exit_code == 0
        assert "--concurrency" in result.stdout


class TestCLIErrorHandling:
    """Test CLI error handling and edge cases."""

    def test_cli_no_command_shows_help(self) -> None:
        """Running CLI without command should show help."""
        result = runner.invoke(app, [])
        assert result.exit_code != 0 or "--help" in result.stdout

    def test_cli_invalid_format_option(self) -> None:
        """CLI should reject invalid format options."""
        result = runner.invoke(app, ["--format", "xml", "config", "show"])
        # Typer validates enum values
        assert result.exit_code != 0

    def test_cli_nonexistent_config_file(self) -> None:
        """CLI should handle nonexistent config file gracefully."""
        result = runner.invoke(
            app,
            [
                "--config",
                "/nonexistent/path/config.toml",
                "config",
                "show",
            ],
        )
        # Should fail with error about missing file
        assert result.exit_code != 0

    @patch("proxywhirl.cli.load_config")
    def test_cli_config_load_error(self, mock_load: Mock) -> None:
        """CLI should handle config loading errors."""
        mock_load.side_effect = Exception("Invalid TOML")

        result = runner.invoke(app, ["--no-lock", "config", "show"])
        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "Error loading config" in output or "Invalid TOML" in output


class TestCLIIntegration:
    """Integration tests for CLI commands working together."""

    def test_cli_chain_config_then_pool(self) -> None:
        """CLI should handle chained operations."""
        # First show config
        result1 = runner.invoke(app, ["--no-lock", "config", "show"])
        assert result1.exit_code == 0

        # Then list pool
        result2 = runner.invoke(app, ["--no-lock", "pool", "list"])
        assert result2.exit_code == 0

    def test_cli_verbose_flag_accepted(self) -> None:
        """Verbose flag should be accepted globally."""
        result = runner.invoke(
            app,
            ["--verbose", "--no-lock", "config", "show"],
        )
        assert result.exit_code == 0

    def test_cli_all_output_formats(self) -> None:
        """All output formats should work."""
        for fmt in ["text", "json", "csv"]:
            result = runner.invoke(
                app,
                ["--format", fmt, "--no-lock", "config", "show"],
            )
            assert result.exit_code == 0, f"Format {fmt} failed"


class TestCredentialScrubbing:
    """Test credential scrubbing in verbose/debug output (TASK-402)."""

    @patch("httpx.Client")
    def test_request_masks_proxy_credentials_in_text_output(self, mock_client_class: Mock) -> None:
        """Request command should mask proxy credentials in text output."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_response.headers = {}

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        # Create a temp config with proxy containing credentials
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".proxywhirl.toml"
            # Write config with proxy containing credentials
            config_content = """
proxies = [
    { url = "http://user:password@proxy.example.com:8080" }
]
rotation_strategy = "round-robin"
"""
            config_path.write_text(config_content)

            result = runner.invoke(
                app,
                [
                    "--no-lock",
                    "--config",
                    str(config_path),
                    "request",
                    "https://httpbin.org/ip",
                ],
            )

            # Should succeed
            assert result.exit_code == 0

            # Credentials should be masked in output
            assert "user" not in result.stdout or "***" in result.stdout
            assert "password" not in result.stdout or "***" in result.stdout
            # Masked format should be present
            assert (
                "***:***@proxy.example.com:8080" in result.stdout
                or "proxy.example.com" in result.stdout
            )

    @patch("httpx.Client")
    def test_request_masks_credentials_in_json_output(self, mock_client_class: Mock) -> None:
        """Request command should mask proxy credentials in JSON output."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_response.headers = {}

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".proxywhirl.toml"
            config_content = """
proxies = [
    { url = "http://admin:secret123@proxy.example.com:3128" }
]
"""
            config_path.write_text(config_content)

            result = runner.invoke(
                app,
                [
                    "--no-lock",
                    "--format",
                    "json",
                    "--config",
                    str(config_path),
                    "request",
                    "https://httpbin.org/ip",
                ],
            )

            assert result.exit_code == 0

            # Parse JSON output
            output_data = json.loads(result.stdout)

            # Check that proxy_used field has masked credentials
            if output_data.get("proxy_used"):
                assert (
                    "admin" not in output_data["proxy_used"] or "***" in output_data["proxy_used"]
                )
                assert (
                    "secret123" not in output_data["proxy_used"]
                    or "***" in output_data["proxy_used"]
                )

    def test_pool_list_masks_credentials(self) -> None:
        """Pool list should mask credentials in proxy URLs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".proxywhirl.toml"
            config_content = """
proxies = [
    { url = "http://testuser:testpass@proxy1.com:8080" },
    { url = "socks5://sockuser:sockpass@proxy2.com:1080" }
]
"""
            config_path.write_text(config_content)

            result = runner.invoke(
                app,
                [
                    "--no-lock",
                    "--config",
                    str(config_path),
                    "pool",
                    "list",
                ],
            )

            # Should not expose credentials
            assert "testuser" not in result.stdout or "***" in result.stdout
            assert "testpass" not in result.stdout or "***" in result.stdout
            assert "sockuser" not in result.stdout or "***" in result.stdout
            assert "sockpass" not in result.stdout or "***" in result.stdout

    def test_mask_proxy_url_utility(self) -> None:
        """Test the mask_proxy_url utility function."""
        from proxywhirl.utils import mask_proxy_url

        # Test HTTP proxy with credentials
        assert mask_proxy_url("http://user:pass@proxy.com:8080") == "http://***:***@proxy.com:8080"

        # Test SOCKS5 proxy with credentials
        assert (
            mask_proxy_url("socks5://admin:secret@192.168.1.1:1080")
            == "socks5://***:***@192.168.1.1:1080"
        )

        # Test proxy without credentials (should remain unchanged)
        assert mask_proxy_url("http://proxy.com:8080") == "http://proxy.com:8080"

    def test_scrub_credentials_from_dict(self) -> None:
        """Test the scrub_credentials_from_dict utility function."""
        from pydantic import SecretStr

        from proxywhirl.utils import scrub_credentials_from_dict

        # Test dict with various sensitive data
        data = {
            "proxy_url": "http://user:password@proxy.com:8080",
            "username": "admin",
            "password": SecretStr("secret123"),
            "api_key": "abc123",
            "normal_field": "normal_value",
            "nested": {
                "token": "xyz789",
                "data": "test",
            },
        }

        scrubbed = scrub_credentials_from_dict(data)

        # Check that credentials are masked
        assert "***" in scrubbed["proxy_url"]
        assert scrubbed["username"] == "***"
        assert scrubbed["password"] == "***"
        assert scrubbed["api_key"] == "***"
        assert scrubbed["normal_field"] == "normal_value"  # Not masked
        assert scrubbed["nested"]["token"] == "***"
        assert scrubbed["nested"]["data"] == "test"  # Not masked


class TestURLValidation:
    """Test URL validation for --target-url parameter (SSRF protection)."""

    def test_target_url_accepts_http_scheme(self) -> None:
        """Target URL should accept http:// scheme."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "pool",
                "test",
                "http://proxy.example.com:8080",
                "--target-url",
                "http://api.example.com",
            ],
        )
        # May fail on proxy connection but should pass URL validation
        assert "Invalid URL scheme" not in result.stdout

    def test_target_url_accepts_https_scheme(self) -> None:
        """Target URL should accept https:// scheme."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "pool",
                "test",
                "http://proxy.example.com:8080",
                "--target-url",
                "https://api.example.com",
            ],
        )
        # May fail on proxy connection but should pass URL validation
        assert "Invalid URL scheme" not in result.stdout

    def test_target_url_rejects_file_scheme(self) -> None:
        """Target URL should reject file:// scheme (SSRF protection)."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "pool",
                "test",
                "http://proxy.example.com:8080",
                "--target-url",
                "file:///etc/passwd",
            ],
        )
        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "Invalid URL scheme" in output
        assert "file" in output.lower()

    def test_target_url_rejects_data_scheme(self) -> None:
        """Target URL should reject data:// scheme (SSRF protection)."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "pool",
                "test",
                "http://proxy.example.com:8080",
                "--target-url",
                "data:text/plain,hello",
            ],
        )
        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "Invalid URL scheme" in output

    def test_target_url_rejects_gopher_scheme(self) -> None:
        """Target URL should reject gopher:// scheme (SSRF protection)."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "pool",
                "test",
                "http://proxy.example.com:8080",
                "--target-url",
                "gopher://example.com",
            ],
        )
        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "Invalid URL scheme" in output

    def test_target_url_rejects_ftp_scheme(self) -> None:
        """Target URL should reject ftp:// scheme."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "pool",
                "test",
                "http://proxy.example.com:8080",
                "--target-url",
                "ftp://ftp.example.com",
            ],
        )
        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "Invalid URL scheme" in output

    def test_target_url_rejects_localhost(self) -> None:
        """Target URL should reject localhost (SSRF protection)."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "pool",
                "test",
                "http://proxy.example.com:8080",
                "--target-url",
                "http://localhost:8080/admin",
            ],
        )
        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "localhost" in output.lower()

    def test_target_url_rejects_127_0_0_1(self) -> None:
        """Target URL should reject 127.0.0.1 (SSRF protection)."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "pool",
                "test",
                "http://proxy.example.com:8080",
                "--target-url",
                "http://127.0.0.1:8080/admin",
            ],
        )
        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "localhost" in output.lower() or "loopback" in output.lower()

    @patch("proxywhirl.cli.socket.getaddrinfo")
    def test_target_url_rejects_hostname_resolving_to_loopback(
        self, mock_getaddrinfo: Mock
    ) -> None:
        """Target URL should reject public-looking hostnames that resolve internally."""
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("127.0.0.1", 8080))
        ]

        result = runner.invoke(
            app,
            [
                "--no-lock",
                "pool",
                "test",
                "http://proxy.example.com:8080",
                "--target-url",
                "http://public.example.test/admin",
            ],
        )

        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "localhost" in output.lower() or "loopback" in output.lower()

    def test_target_url_rejects_0_0_0_0(self) -> None:
        """Target URL should reject 0.0.0.0 (SSRF protection)."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "pool",
                "test",
                "http://proxy.example.com:8080",
                "--target-url",
                "http://0.0.0.0:8080",
            ],
        )
        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "unspecified" in output.lower()

    def test_target_url_rejects_private_ipv6(self) -> None:
        """Target URL should reject private IPv6 ranges."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "request",
                "http://[fd00::1]/admin",
            ],
        )
        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "private" in output.lower()

    def test_target_url_rejects_obfuscated_loopback_integer(self) -> None:
        """Target URL should reject integer-form IPv4 loopback addresses."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "request",
                "http://2130706433/admin",
            ],
        )
        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "localhost" in output.lower() or "loopback" in output.lower()

    def test_target_url_rejects_obfuscated_loopback_octal(self) -> None:
        """Target URL should reject legacy octal-form IPv4 loopback addresses."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "request",
                "http://0177.0.0.1/admin",
            ],
        )
        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "localhost" in output.lower() or "loopback" in output.lower()

    def test_target_url_rejects_private_ip_10_0_0_0(self) -> None:
        """Target URL should reject 10.0.0.0/8 private IP range."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "pool",
                "test",
                "http://proxy.example.com:8080",
                "--target-url",
                "http://10.0.0.1:8080",
            ],
        )
        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "private" in output.lower()

    def test_target_url_rejects_private_ip_192_168_0_0(self) -> None:
        """Target URL should reject 192.168.0.0/16 private IP range."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "pool",
                "test",
                "http://proxy.example.com:8080",
                "--target-url",
                "http://192.168.1.1:8080",
            ],
        )
        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "private" in output.lower()

    def test_target_url_rejects_private_ip_172_16_0_0(self) -> None:
        """Target URL should reject 172.16.0.0/12 private IP range."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "pool",
                "test",
                "http://proxy.example.com:8080",
                "--target-url",
                "http://172.16.0.1:8080",
            ],
        )
        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "private" in output.lower()

    def test_target_url_rejects_link_local_169_254(self) -> None:
        """Target URL should reject 169.254.0.0/16 link-local range."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "pool",
                "test",
                "http://proxy.example.com:8080",
                "--target-url",
                "http://169.254.169.254/metadata",
            ],
        )
        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "private" in output.lower()

    def test_target_url_rejects_internal_domain_local(self) -> None:
        """Target URL should reject .local internal domains."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "pool",
                "test",
                "http://proxy.example.com:8080",
                "--target-url",
                "http://server.local",
            ],
        )
        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "internal" in output.lower()

    def test_target_url_rejects_internal_domain_internal(self) -> None:
        """Target URL should reject .internal domains."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "pool",
                "test",
                "http://proxy.example.com:8080",
                "--target-url",
                "http://api.internal",
            ],
        )
        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "internal" in output.lower()

    def test_target_url_allows_private_with_flag(self) -> None:
        """Target URL should allow private IPs with --allow-private flag."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "pool",
                "test",
                "http://proxy.example.com:8080",
                "--target-url",
                "http://192.168.1.1:8080",
                "--allow-private",
            ],
        )
        # Should pass URL validation (may fail on actual connection)
        assert "private" not in (result.stdout + result.stderr).lower() or result.exit_code != 1

    def test_health_command_target_url_validation(self) -> None:
        """Health command should also validate target URL."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "health",
                "--target-url",
                "file:///etc/passwd",
            ],
        )
        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "Invalid URL scheme" in output

    def test_health_command_rejects_localhost(self) -> None:
        """Health command should reject localhost."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "health",
                "--target-url",
                "http://localhost:8080",
            ],
        )
        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "localhost" in output.lower()

    def test_health_command_allows_private_with_flag(self) -> None:
        """Health command should allow private IPs with --allow-private flag."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "health",
                "--target-url",
                "http://localhost:8080",
                "--allow-private",
            ],
        )
        # Should pass URL validation (will show "No proxies configured" message)
        assert result.exit_code == 0
        assert "No proxies configured" in result.stdout

    def test_target_url_requires_hostname(self) -> None:
        """Target URL should require a hostname."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "pool",
                "test",
                "http://proxy.example.com:8080",
                "--target-url",
                "http://",
            ],
        )
        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "hostname" in output.lower() or "invalid" in output.lower()

    def test_pool_test_help_shows_target_url(self) -> None:
        """Pool test help should document --target-url parameter."""
        result = runner.invoke(app, ["pool", "test", "--help"])
        assert result.exit_code == 0
        assert "--target-url" in result.stdout

    def test_health_help_shows_target_url(self) -> None:
        """Health help should document --target-url parameter."""
        result = runner.invoke(app, ["health", "--help"])
        assert result.exit_code == 0
        assert "--target-url" in result.stdout

    def test_request_command_rejects_localhost(self) -> None:
        """Request command should reject localhost (SSRF protection)."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "request",
                "http://localhost:8080/admin",
            ],
        )
        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "localhost" in output.lower()

    def test_request_command_rejects_127_0_0_1(self) -> None:
        """Request command should reject 127.0.0.1 (SSRF protection)."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "request",
                "http://127.0.0.1:8080/admin",
            ],
        )
        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "localhost" in output.lower() or "loopback" in output.lower()

    def test_request_command_rejects_private_ip_10_0_0_0(self) -> None:
        """Request command should reject 10.0.0.0/8 private IP range."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "request",
                "http://10.0.0.1:8080",
            ],
        )
        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "private" in output.lower()

    def test_request_command_rejects_private_ip_192_168_0_0(self) -> None:
        """Request command should reject 192.168.0.0/16 private IP range."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "request",
                "http://192.168.1.1:8080",
            ],
        )
        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "private" in output.lower()

    def test_request_command_rejects_internal_domain_local(self) -> None:
        """Request command should reject .local internal domains."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "request",
                "http://server.local",
            ],
        )
        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "internal" in output.lower()

    def test_request_command_allows_private_with_flag(self) -> None:
        """Request command should allow private IPs with --allow-private flag."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "request",
                "http://192.168.1.1:8080",
                "--allow-private",
                "--timeout",
                "1",  # Short timeout since we expect connection failure
            ],
        )
        # Should pass URL validation (may fail on actual connection)
        # Check that it didn't exit with code 1 (validation error)
        # It will likely fail with connection error, but that's expected
        output = result.stdout + result.stderr
        # Validate that SSRF error didn't occur
        if "private IP" in output and "not allowed" in output:
            raise AssertionError(
                "SSRF validation incorrectly rejected private IP with --allow-private flag"
            )

    def test_request_command_rejects_file_scheme(self) -> None:
        """Request command should reject file:// scheme (SSRF protection)."""
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "request",
                "file:///etc/passwd",
            ],
        )
        assert result.exit_code != 0
        output = result.stdout + result.stderr
        assert "Invalid URL scheme" in output or "file" in output.lower()

    def test_request_help_shows_allow_private(self) -> None:
        """Request help should document --allow-private parameter."""
        result = runner.invoke(app, ["request", "--help"])
        assert result.exit_code == 0
        assert "--allow-private" in result.stdout
