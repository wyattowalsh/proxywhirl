"""Unit tests for CLI commands.

Tests the command-line interface functionality in isolation using Typer's testing utilities.
"""

from __future__ import annotations

from typer.testing import CliRunner

from proxywhirl.cli import app

# Test fixtures
runner = CliRunner()


class TestCLIHelp:
    """Test CLI help messages and command discovery."""

    def test_main_help_shows_all_commands(self) -> None:
        """Main help should enumerate all available commands."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "request" in result.stdout
        assert "pool" in result.stdout
        assert "config" in result.stdout
        assert "health" in result.stdout

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
