"""Behavioral coverage for supported CLI orchestration branches."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
import typer
from rich.console import Console
from typer.testing import CliRunner

from proxywhirl.cli import _impl as cli_impl
from proxywhirl.cli import app
from proxywhirl.config import CLIConfig
from proxywhirl.formatters import OutputFormat
from proxywhirl.models import Proxy

_xdist_worker = os.environ.get("PYTEST_XDIST_WORKER", "main")
runner = CliRunner(
    env={
        "COLUMNS": "120",
        "TERM": "dumb",
        "XDG_DATA_HOME": str(Path.cwd() / f".cli-coverage-data-{_xdist_worker}"),
        "XDG_CONFIG_HOME": str(Path.cwd() / f".cli-coverage-config-{_xdist_worker}"),
        "HOME": str(Path.cwd() / f".cli-coverage-home-{_xdist_worker}"),
    }
)


def _context(
    tmp_path: Path,
    *,
    output_format: OutputFormat = OutputFormat.TEXT,
    verbose: bool = False,
) -> cli_impl.CommandContext:
    return cli_impl.CommandContext(
        config=CLIConfig(),
        config_path=tmp_path / "config.toml",
        format=output_format,
        verbose=verbose,
        console=Console(force_terminal=False, width=120),
    )


def _source(name: str, *, enabled: bool = True) -> SimpleNamespace:
    return SimpleNamespace(
        name=name,
        url=f"https://{name}.example.com/list.txt",
        format=SimpleNamespace(value="text"),
        protocol=SimpleNamespace(value="http"),
        render_mode=SimpleNamespace(value="http"),
        enabled=enabled,
    )


class TestFormatterBehavior:
    """Exercise every public output branch with real serialization."""

    def test_render_text_message_table_and_mapping(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        console = Console(force_terminal=False, width=120)

        cli_impl.render_text(console, {"message": "ready"})
        cli_impl.render_text(
            console,
            {"title": "Rows", "table": {"headers": ["name", "count"], "rows": [["ok", 2]]}},
        )
        cli_impl.render_text(console, {"status": "healthy"})

        output = capsys.readouterr().out
        assert "ready" in output
        assert "Rows" in output
        assert "healthy" in output

    @pytest.mark.parametrize(
        ("output_format", "expected"),
        [
            (OutputFormat.TEXT, "ready"),
            (OutputFormat.JSON, '"message": "ready"'),
            (OutputFormat.CSV, "name,count"),
            (OutputFormat.YAML, "message: ready"),
        ],
    )
    def test_render_output_dispatches_supported_formats(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
        output_format: OutputFormat,
        expected: str,
    ) -> None:
        context = _context(tmp_path, output_format=output_format)
        data = {
            "message": "ready",
            "table": {"headers": ["name", "count"], "rows": [["ok", 2]]},
        }

        cli_impl.render_output(context, data)

        assert expected in capsys.readouterr().out

    def test_render_csv_rejects_non_table_data(self) -> None:
        with pytest.raises(typer.Exit) as exc_info:
            cli_impl.render_csv({"message": "not tabular"})

        assert exc_info.value.exit_code == 1

    def test_render_yaml_reports_missing_dependency(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        monkeypatch.setitem(sys.modules, "yaml", None)

        with pytest.raises(typer.Exit) as exc_info:
            cli_impl.render_yaml({"message": "ready"})

        assert exc_info.value.exit_code == 1
        assert "PyYAML not installed" in capsys.readouterr().err


class TestFetchServiceSeams:
    """Cover fetch helpers through their supported storage and source contracts."""

    async def test_fetch_from_sources_updates_fetch_and_validation_progress(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        sources = [_source("one"), _source("two")]
        expected = [{"url": "http://proxy.example.com:8080", "protocol": "http"}]

        async def fake_fetch_all_sources(**kwargs):
            kwargs["fetch_progress_callback"](1, 2, 3)
            kwargs["fetch_progress_callback"](2, 2, 5)
            kwargs["validate_progress_callback"](0, 5, 0)
            kwargs["validate_progress_callback"](5, 5, 1)
            return expected

        monkeypatch.setattr("proxywhirl.sources.ALL_SOURCES", sources)
        monkeypatch.setattr("proxywhirl.sources.fetch_all_sources", fake_fetch_all_sources)

        result = await cli_impl._fetch_from_sources(
            validate=True,
            timeout=2,
            max_concurrent=4,
            console=Console(force_terminal=False),
        )

        assert result == expected

    async def test_fetch_from_sources_without_validation_omits_callback(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        seen: dict[str, object] = {}

        async def fake_fetch_all_sources(**kwargs):
            seen.update(kwargs)
            kwargs["fetch_progress_callback"](1, 1, 2)
            return []

        monkeypatch.setattr("proxywhirl.sources.ALL_SOURCES", [_source("one")])
        monkeypatch.setattr("proxywhirl.sources.fetch_all_sources", fake_fetch_all_sources)

        assert await cli_impl._fetch_from_sources(False, 3, 6) == []
        assert seen["validate_progress_callback"] is None

    async def test_save_results_normalizes_dicts_and_always_closes(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        storage = MagicMock()
        storage.initialize = AsyncMock()
        storage.save = AsyncMock()
        storage.close = AsyncMock()
        storage_class = Mock(return_value=storage)
        monkeypatch.setattr("proxywhirl.storage.SQLiteStorage", storage_class)
        existing = Proxy(url="http://two.example.com:8080")

        await cli_impl._save_results(
            [{"url": "http://one.example.com:8080"}, existing],
            tmp_path / "proxies.sqlite",
            validated=False,
        )

        storage.initialize.assert_awaited_once()
        saved = storage.save.await_args.args[0]
        assert [str(proxy.url) for proxy in saved] == [
            "http://one.example.com:8080",
            "http://two.example.com:8080",
        ]
        storage.save.assert_awaited_once_with(saved, validated=False)
        storage.close.assert_awaited_once()

    async def test_save_results_closes_after_save_failure(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        storage = MagicMock()
        storage.initialize = AsyncMock()
        storage.save = AsyncMock(side_effect=RuntimeError("write failed"))
        storage.close = AsyncMock()
        monkeypatch.setattr("proxywhirl.storage.SQLiteStorage", Mock(return_value=storage))

        with pytest.raises(RuntimeError, match="write failed"):
            await cli_impl._save_results([], tmp_path / "proxies.sqlite")

        storage.close.assert_awaited_once()

    async def test_export_results_forwards_paths(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        export_for_web = AsyncMock()
        monkeypatch.setattr("proxywhirl.exports.export_for_web", export_for_web)

        await cli_impl._export_results(tmp_path / "db.sqlite", tmp_path / "exports")

        export_for_web.assert_awaited_once_with(
            db_path=tmp_path / "db.sqlite",
            output_dir=tmp_path / "exports",
        )


class TestRevalidationWorkflow:
    """Cover successful, empty, prune, and cleanup behavior for revalidation."""

    @staticmethod
    def _storage(existing: list[dict[str, object]]) -> MagicMock:
        storage = MagicMock()
        storage.initialize = AsyncMock()
        storage.load_revalidation_candidates = AsyncMock(return_value=existing)
        storage.record_validations_batch = AsyncMock()
        storage.cleanup = AsyncMock()
        storage.close = AsyncMock()
        return storage

    async def test_empty_database_returns_cleanly_and_closes(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        storage = self._storage([])
        monkeypatch.setattr("proxywhirl.storage.SQLiteStorage", Mock(return_value=storage))

        result = await cli_impl._revalidate_existing_proxies(
            tmp_path / "db.sqlite", 2, 4, False, None, Console(force_terminal=False)
        )

        assert result == ([], 0)
        storage.close.assert_awaited_once()

    @pytest.mark.parametrize("prune_failed", [False, True])
    async def test_records_success_and_failure_with_optional_pruning(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        prune_failed: bool,
    ) -> None:
        existing = [
            {"url": "http://good.example.com:8080", "protocol": "http"},
            {"url": "http://bad.example.com:8080"},
        ]
        validated = [
            {
                "url": "http://good.example.com:8080",
                "protocol": "http",
                "average_response_time_ms": 12.5,
            }
        ]
        storage = self._storage(existing)
        monkeypatch.setattr("proxywhirl.storage.SQLiteStorage", Mock(return_value=storage))

        validator = MagicMock()
        validator.validate_batch = AsyncMock()
        validator.close = AsyncMock()

        async def validate_batch(items, progress_callback):
            assert items == [
                {"url": "http://good.example.com:8080", "protocol": "http"},
                {"url": "http://bad.example.com:8080", "protocol": "http"},
            ]
            progress_callback(0, 2, 0)
            progress_callback(2, 2, 1)
            return validated

        validator.validate_batch.side_effect = validate_batch
        validator_class = Mock(return_value=validator)
        monkeypatch.setattr("proxywhirl.fetchers.ProxyValidator", validator_class)

        result = await cli_impl._revalidate_existing_proxies(
            tmp_path / "db.sqlite",
            timeout=3,
            max_concurrent=7,
            prune_failed=prune_failed,
            revalidate_limit=2,
            console=Console(force_terminal=False),
        )

        assert result == (validated, 1)
        validator_class.assert_called_once_with(timeout=3, concurrency=7)
        validator.close.assert_awaited_once()
        storage.record_validations_batch.assert_awaited_once_with(
            [
                ("http://good.example.com:8080", True, 12.5, None),
                ("http://bad.example.com:8080", False, None, "validation_failed"),
            ]
        )
        if prune_failed:
            storage.cleanup.assert_awaited_once_with(
                remove_dead=True,
                remove_stale_days=0,
                remove_never_validated=False,
                vacuum=False,
            )
        else:
            storage.cleanup.assert_not_awaited()
        storage.close.assert_awaited_once()

    async def test_validator_failure_closes_validator_and_storage(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        storage = self._storage([{"url": "http://bad.example.com:8080"}])
        monkeypatch.setattr("proxywhirl.storage.SQLiteStorage", Mock(return_value=storage))
        validator = MagicMock()
        validator.validate_batch = AsyncMock(side_effect=RuntimeError("validator failed"))
        validator.close = AsyncMock()
        monkeypatch.setattr("proxywhirl.fetchers.ProxyValidator", Mock(return_value=validator))

        with pytest.raises(RuntimeError, match="validator failed"):
            await cli_impl._revalidate_existing_proxies(
                tmp_path / "db.sqlite", 2, 4, False, None, Console(force_terminal=False)
            )

        validator.close.assert_awaited_once()
        storage.close.assert_awaited_once()


class TestFetchCommandBehavior:
    """Exercise normal, revalidation, dual-validation, persistence, and error branches."""

    @patch("proxywhirl.cli._impl._export_results", new_callable=AsyncMock)
    @patch("proxywhirl.cli._impl._save_results", new_callable=AsyncMock)
    @patch("proxywhirl.cli._impl._fetch_from_sources", new_callable=AsyncMock)
    def test_normal_fetch_saves_exports_and_reports_json(
        self,
        fetch_from_sources: AsyncMock,
        save_results: AsyncMock,
        export_results: AsyncMock,
    ) -> None:
        fetch_from_sources.return_value = [
            {"url": "socks5://proxy.example.com:1080", "protocol": "socks5"}
        ]

        result = runner.invoke(
            app,
            [
                "--no-lock",
                "--format",
                "json",
                "fetch",
                "--no-https-validate",
                "--timeout",
                "4",
                "--concurrency",
                "8",
            ],
        )

        assert result.exit_code == 0
        payload, _ = json.JSONDecoder().raw_decode(result.stdout)
        assert payload == {"total": 1, "validated": True}
        assert "Saved to database" in result.stdout
        assert "Exported to docs/proxy-lists" in result.stdout
        fetch_from_sources.assert_awaited_once()
        save_results.assert_awaited_once()
        export_results.assert_awaited_once()

    @patch("proxywhirl.cli._impl._export_results", new_callable=AsyncMock)
    @patch("proxywhirl.cli._impl._revalidate_existing_proxies", new_callable=AsyncMock)
    def test_revalidate_limit_reports_counts_and_exports(
        self,
        revalidate: AsyncMock,
        export_results: AsyncMock,
    ) -> None:
        revalidate.return_value = ([{"url": "http://good.example.com:8080"}], 2)

        result = runner.invoke(
            app,
            [
                "--no-lock",
                "fetch",
                "--revalidate",
                "--revalidate-limit",
                "10",
                "--prune-failed",
            ],
        )

        assert result.exit_code == 0
        assert "limit 10" in result.stdout
        assert "1 valid" in result.stdout
        assert "2 failed" in result.stdout
        assert revalidate.await_args.kwargs["revalidate_limit"] == 10
        assert revalidate.await_args.kwargs["prune_failed"] is True
        export_results.assert_awaited_once()

    @pytest.mark.parametrize(
        ("args", "message"),
        [
            (["--revalidate-limit", "-1"], "must be >= 0"),
            (["--revalidate-limit", "3"], "can only be used with --revalidate"),
        ],
    )
    def test_revalidate_limit_validation(self, args: list[str], message: str) -> None:
        result = runner.invoke(app, ["--no-lock", "fetch", *args])

        assert result.exit_code == 1
        assert message in result.stdout

    @patch("proxywhirl.cli._impl._revalidate_existing_proxies", new_callable=AsyncMock)
    def test_revalidate_failure_is_reported(self, revalidate: AsyncMock) -> None:
        revalidate.side_effect = RuntimeError(
            "database unavailable api_key=revalidate_probe_marker"
        )

        result = runner.invoke(
            app,
            ["--no-lock", "fetch", "--revalidate", "--no-export"],
        )

        assert result.exit_code == 1
        assert "Re-validation failed" in result.stdout
        assert "database unavailable" in result.stdout
        assert "revalidate_probe_marker" not in result.stdout

    @patch("proxywhirl.cli._impl._fetch_from_sources", new_callable=AsyncMock)
    def test_fetch_failure_is_reported(self, fetch_from_sources: AsyncMock) -> None:
        fetch_from_sources.side_effect = RuntimeError("source unavailable token=fetch_probe_marker")

        result = runner.invoke(
            app,
            ["--no-lock", "fetch", "--no-save-db", "--no-export"],
        )

        assert result.exit_code == 1
        assert "Fetch failed" in result.stdout
        assert "fetch_probe_marker" not in result.stdout

    @patch("proxywhirl.cli._impl._save_results", new_callable=AsyncMock)
    @patch("proxywhirl.cli._impl._fetch_from_sources", new_callable=AsyncMock)
    def test_save_failure_is_reported(
        self,
        fetch_from_sources: AsyncMock,
        save_results: AsyncMock,
    ) -> None:
        fetch_from_sources.return_value = []
        save_results.side_effect = RuntimeError("write unavailable password=save_probe_marker")

        result = runner.invoke(
            app,
            ["--no-lock", "fetch", "--no-https-validate", "--no-export"],
        )

        assert result.exit_code == 1
        assert "Save failed" in result.stdout
        assert "save_probe_marker" not in result.stdout

    @patch("proxywhirl.cli._impl._export_results", new_callable=AsyncMock)
    @patch("proxywhirl.cli._impl._fetch_from_sources", new_callable=AsyncMock)
    def test_export_failure_is_reported(
        self,
        fetch_from_sources: AsyncMock,
        export_results: AsyncMock,
    ) -> None:
        fetch_from_sources.return_value = []
        export_results.side_effect = RuntimeError(
            "export unavailable Authorization: Bearer export_probe_marker"
        )

        result = runner.invoke(
            app,
            ["--no-lock", "fetch", "--no-https-validate", "--no-save-db"],
        )

        assert result.exit_code == 1
        assert "Export failed" in result.stdout
        assert "export_probe_marker" not in result.stdout

    @patch("proxywhirl.cli._impl._fetch_from_sources", new_callable=AsyncMock)
    def test_https_dual_validation_adds_capable_proxies(
        self,
        fetch_from_sources: AsyncMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        fetch_from_sources.return_value = [
            {"url": "http://proxy.example.com:8080", "protocol": "http"}
        ]
        validator = MagicMock()
        validator.validate_https_capability_batch = AsyncMock()

        async def validate_https(items, concurrency, max_results, progress_callback):
            assert concurrency == 500
            assert max_results is None
            progress_callback(0, 1, 0)
            progress_callback(1, 1, 1)
            return [{"url": "https://proxy.example.com:8080", "protocol": "https"}]

        validator.validate_https_capability_batch.side_effect = validate_https
        monkeypatch.setattr("proxywhirl.fetchers.ProxyValidator", Mock(return_value=validator))

        result = runner.invoke(
            app,
            [
                "--no-lock",
                "fetch",
                "--concurrency",
                "900",
                "--https-max",
                "0",
                "--no-save-db",
                "--no-export",
            ],
        )

        assert result.exit_code == 0
        assert "Found 1 HTTPS-capable" in result.stdout

    @patch("proxywhirl.cli._impl._fetch_from_sources", new_callable=AsyncMock)
    def test_https_dual_validation_failure_is_nonfatal(
        self,
        fetch_from_sources: AsyncMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        fetch_from_sources.return_value = [
            {"url": "http://proxy.example.com:8080", "protocol": "http"}
        ]
        validator = MagicMock()
        validator.validate_https_capability_batch = AsyncMock(
            side_effect=RuntimeError("no tunnel api_key=https_probe_marker")
        )
        monkeypatch.setattr("proxywhirl.fetchers.ProxyValidator", Mock(return_value=validator))

        result = runner.invoke(
            app,
            ["--no-lock", "fetch", "--no-save-db", "--no-export"],
        )

        assert result.exit_code == 0
        assert "HTTPS dual-validation skipped" in result.stdout
        assert "https_probe_marker" not in result.stdout

    def test_verbose_request_failure_redacts_exception_secrets(self) -> None:
        """Verbose retry diagnostics must not expose the explicit proxy or bearer token."""
        proxy_url = "http://request_user_marker:request_pass_marker@proxy.example.com:8080"
        error = RuntimeError(f"failed via {proxy_url} Authorization: Bearer request_bearer_marker")

        with (
            patch("proxywhirl.cli._impl.validate_target_url"),
            patch("httpx.Client", side_effect=error),
        ):
            result = runner.invoke(
                app,
                [
                    "--no-lock",
                    "--verbose",
                    "request",
                    "--proxy",
                    proxy_url,
                    "--retries",
                    "0",
                    "https://example.com",
                ],
            )

        output = result.stdout + result.stderr
        assert result.exit_code == 1
        assert "Attempt 1/1 failed" in output
        assert "request_user_marker" not in output
        assert "request_pass_marker" not in output
        assert "request_bearer_marker" not in output


class TestSourcesCommandBehavior:
    """Cover source listing, validation output, and strict exit semantics."""

    def test_sources_lists_only_enabled_entries(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "proxywhirl.sources.ALL_SOURCES",
            [_source("enabled"), _source("disabled", enabled=False)],
        )

        result = runner.invoke(app, ["--no-lock", "sources"])

        assert result.exit_code == 0
        assert "enabled.example.com" in result.stdout
        assert "disabled.example.com" not in result.stdout
        assert "1/2 sources enabled" in result.stdout

    @pytest.mark.parametrize("fail_on_unhealthy", [False, True])
    def test_sources_validation_renders_report_and_honors_strict_exit(
        self,
        monkeypatch: pytest.MonkeyPatch,
        fail_on_unhealthy: bool,
    ) -> None:
        monkeypatch.setattr("proxywhirl.sources.ALL_SOURCES", [_source("one"), _source("two")])
        report = SimpleNamespace(
            results=[
                SimpleNamespace(
                    is_healthy=True,
                    name="Healthy",
                    status_code=200,
                    has_proxies=True,
                    content_length=100,
                    response_time_ms=12.0,
                    error=None,
                ),
                SimpleNamespace(
                    is_healthy=False,
                    name="Broken",
                    status_code=None,
                    has_proxies=False,
                    content_length=0,
                    response_time_ms=9.0,
                    error="invalid payload",
                ),
            ],
            healthy_sources=1,
            total_sources=2,
            unhealthy_sources=1,
            all_healthy=False,
        )
        validate = Mock(return_value=report)
        monkeypatch.setattr("proxywhirl.sources.validate_sources_sync", validate)
        args = ["--no-lock", "sources", "--validate", "--timeout", "2", "--concurrency", "3"]
        if fail_on_unhealthy:
            args.append("--fail-on-unhealthy")

        result = runner.invoke(app, args)

        assert result.exit_code == (1 if fail_on_unhealthy else 0)
        assert "Healthy" in result.stdout
        assert "Broken" in result.stdout
        assert "1/2 sources healthy" in result.stdout
        validate.assert_called_once_with(timeout=2.0, concurrency=3)


class TestHealthCommandBehavior:
    """Cover healthy, degraded, failed, CSV, and continuous monitoring paths."""

    @staticmethod
    def _config(tmp_path: Path) -> Path:
        path = tmp_path / "config.toml"
        path.write_text(
            'proxies = [{ url = "http://one.example.com:8080" }, '
            '{ url = "http://two.example.com:8080" }]\n'
            "encrypt_credentials = false\n"
            "verbose = true\n"
        )
        return path

    def test_health_text_reports_healthy_and_exception(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        config_path = self._config(tmp_path)
        healthy = Mock(status_code=200)
        clients = []

        class FakeClient:
            def __init__(self, **kwargs):
                self.proxy = str(kwargs["proxy"])
                clients.append(self.proxy)

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def get(self, url):
                if "two" in self.proxy:
                    raise RuntimeError("connection failed")
                return healthy

        monkeypatch.setattr("httpx.Client", FakeClient)

        result = runner.invoke(
            app,
            ["--no-lock", "--verbose", "--config", str(config_path), "health"],
        )

        assert result.exit_code == 0
        assert "Healthy: 1" in result.stdout
        assert "Failed: 1" in result.stdout
        assert "connection failed" in result.stdout
        assert len(clients) == 2

    def test_health_json_reports_degraded_response(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        config_path = self._config(tmp_path)
        response = Mock(status_code=503)
        client = MagicMock()
        client.__enter__.return_value = client
        client.get.return_value = response
        monkeypatch.setattr("httpx.Client", Mock(return_value=client))

        result = runner.invoke(
            app,
            ["--no-lock", "--format", "json", "--config", str(config_path), "health"],
        )

        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        assert payload["degraded"] == 2
        assert {proxy["health"] for proxy in payload["proxies"]} == {"degraded"}

    def test_health_csv_projects_supported_fields_without_extra_model_columns(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        config_path = self._config(tmp_path)
        response = Mock(status_code=503)
        client = MagicMock()
        client.__enter__.return_value = client
        client.get.return_value = response
        monkeypatch.setattr("httpx.Client", Mock(return_value=client))

        result = runner.invoke(
            app,
            ["--no-lock", "--format", "csv", "--config", str(config_path), "health"],
        )

        assert result.exit_code == 0
        lines = result.stdout.strip().splitlines()
        assert lines[0] == "url,health,response_time_ms,success_rate"
        assert len(lines) == 3
        assert all(",degraded," in row for row in lines[1:])

    def test_continuous_health_stops_cleanly_after_first_sleep(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        config_path = self._config(tmp_path)
        response = Mock(status_code=200)
        client = MagicMock()
        client.__enter__.return_value = client
        client.get.return_value = response
        monkeypatch.setattr("httpx.Client", Mock(return_value=client))
        monkeypatch.setattr("time.sleep", Mock(side_effect=KeyboardInterrupt))

        result = runner.invoke(
            app,
            [
                "--no-lock",
                "--config",
                str(config_path),
                "health",
                "--continuous",
                "--interval",
                "1",
            ],
        )

        assert result.exit_code == 0
        assert "Check #1" in result.stdout
        assert "2 healthy" in result.stdout
        assert "Monitoring stopped" in result.stdout


class TestPoolBehaviorCoverage:
    """Cover live pool output formats, statistics, and test response branches."""

    @staticmethod
    def _config(tmp_path: Path) -> Path:
        path = tmp_path / "config.toml"
        path.write_text(
            'proxies = [{ url = "http://proxy.example.com:8080" }]\nencrypt_credentials = false\n'
        )
        return path

    @pytest.mark.parametrize(
        ("output_format", "expected"),
        [("json", '"total_proxies": 1'), ("text", "Proxy Pool Summary")],
    )
    def test_pool_list_structured_formats(
        self,
        tmp_path: Path,
        output_format: str,
        expected: str,
    ) -> None:
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "--format",
                output_format,
                "--config",
                str(self._config(tmp_path)),
                "pool",
                "list",
            ],
        )

        assert result.exit_code == 0
        assert expected in result.stdout

    def test_pool_list_csv_projects_supported_fields_without_extra_model_columns(
        self,
        tmp_path: Path,
    ) -> None:
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "--format",
                "csv",
                "--config",
                str(self._config(tmp_path)),
                "pool",
                "list",
            ],
        )

        assert result.exit_code == 0
        lines = result.stdout.strip().splitlines()
        assert lines[0] == "url,health,response_time_ms,success_rate"
        assert len(lines) == 2
        assert lines[1].startswith("http://proxy.example.com:8080,")

    @pytest.mark.parametrize(
        ("output_format", "expected"),
        [
            ("json", '"total_proxies": 1'),
            ("csv", "total_proxies,healthy"),
            ("yaml", "total_proxies: 1"),
        ],
    )
    def test_pool_stats_structured_formats(
        self,
        tmp_path: Path,
        output_format: str,
        expected: str,
    ) -> None:
        result = runner.invoke(
            app,
            [
                "--no-lock",
                "--format",
                output_format,
                "--config",
                str(self._config(tmp_path)),
                "pool",
                "stats",
            ],
        )

        assert result.exit_code == 0
        assert expected in result.stdout

    def test_pool_test_verbose_success_and_degraded_response(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        config_path = self._config(tmp_path)
        client = MagicMock()
        client.__enter__.return_value = client
        client.get.side_effect = [Mock(status_code=200, text="public IP"), Mock(status_code=503)]
        monkeypatch.setattr("httpx.Client", Mock(return_value=client))

        success = runner.invoke(
            app,
            [
                "--no-lock",
                "--verbose",
                "--config",
                str(config_path),
                "pool",
                "test",
                "http://proxy.example.com:8080",
            ],
        )
        degraded = runner.invoke(
            app,
            [
                "--no-lock",
                "--config",
                str(config_path),
                "pool",
                "test",
                "http://proxy.example.com:8080",
            ],
        )

        assert success.exit_code == 0
        assert "Proxy is working" in success.stdout
        assert "Response: public IP" in success.stdout
        assert degraded.exit_code == 0
        assert "status 503" in degraded.stdout


class TestValidateAndImportCoverage:
    """Cover remaining supported result and file-format branches."""

    @patch("httpx.get")
    def test_validate_proxy_degraded_text(self, get: Mock) -> None:
        get.return_value = Mock(status_code=407)

        result = runner.invoke(
            app,
            ["--no-lock", "validate-proxy", "http://proxy.example.com:8080"],
        )

        assert result.exit_code == 0
        assert "Proxy degraded" in result.stdout
        assert "Response Code: 407" in result.stdout

    @patch("httpx.get")
    def test_validate_proxy_timeout_json(self, get: Mock) -> None:
        import httpx

        get.side_effect = httpx.TimeoutException("timed out")

        result = runner.invoke(
            app,
            [
                "--no-lock",
                "--format",
                "json",
                "validate-proxy",
                "http://proxy.example.com:8080",
            ],
        )

        assert result.exit_code == 1
        assert json.loads(result.stdout)["reason"] == "Timeout"

    @pytest.mark.parametrize(
        ("name", "contents", "expected_format"),
        [
            ("proxies.json", '{"proxies": ["http://json.example.com:8080"]}', "json"),
            ("proxies.csv", "url\nhttp://csv.example.com:8080\n", "csv"),
            ("proxies.data", "# comment\nhttp://text.example.com:8080\n", "text"),
        ],
    )
    def test_import_auto_detects_supported_formats(
        self,
        tmp_path: Path,
        name: str,
        contents: str,
        expected_format: str,
    ) -> None:
        source = tmp_path / name
        source.write_text(contents)
        config_path = tmp_path / "config.toml"
        config_path.write_text("encrypt_credentials = false\n")

        result = runner.invoke(
            app,
            [
                "--no-lock",
                "--format",
                "json",
                "--config",
                str(config_path),
                "import-proxies",
                str(source),
            ],
        )

        assert result.exit_code == 0
        assert json.loads(result.stdout)["format"] == expected_format

    def test_import_csv_falls_back_to_first_column(self, tmp_path: Path) -> None:
        source = tmp_path / "proxies.csv"
        source.write_text("endpoint\nhttp://fallback.example.com:8080\n")
        config_path = tmp_path / "config.toml"
        config_path.write_text("encrypt_credentials = false\n")

        result = runner.invoke(
            app,
            ["--no-lock", "--config", str(config_path), "import-proxies", str(source)],
        )

        assert result.exit_code == 0
        assert "Imported: 1 proxies" in result.stdout
