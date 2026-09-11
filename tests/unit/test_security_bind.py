"""Unit tests for bind safety and placeholder secret helpers."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from proxywhirl.security import (
    allow_insecure_bind,
    is_loopback_host,
    is_placeholder_secret,
)


class TestPlaceholderSecrets:
    @pytest.mark.parametrize(
        "value",
        [
            None,
            "",
            "   ",
            "changeme",
            "CHANGEME",
            "change_me",
            "password",
            "admin",
            "your-api-key-here",
            "CHANGE_ME_GENERATE_WITH_OPENSSL",
        ],
    )
    def test_placeholder_detected(self, value: str | None) -> None:
        assert is_placeholder_secret(value) is True

    @pytest.mark.parametrize(
        "value",
        [
            "sk-live-9f3a2c1b0e8d7c6a",
            "x" * 32,
            "real-secret-value-not-placeholder",
        ],
    )
    def test_real_secret_not_placeholder(self, value: str) -> None:
        assert is_placeholder_secret(value) is False


class TestLoopbackHost:
    @pytest.mark.parametrize(
        "host",
        ["127.0.0.1", "localhost", "LOCALHOST", "::1", "[::1]"],
    )
    def test_loopback(self, host: str) -> None:
        assert is_loopback_host(host) is True

    @pytest.mark.parametrize(
        "host",
        ["0.0.0.0", "192.168.1.1", "example.com", None, ""],
    )
    def test_non_loopback(self, host: str | None) -> None:
        assert is_loopback_host(host) is False


class TestAllowInsecureBind:
    def test_default_false(self) -> None:
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("PROXYWHIRL_ALLOW_INSECURE_BIND", None)
            assert allow_insecure_bind() is False

    def test_true_variants(self) -> None:
        for raw in ("1", "true", "YES", "on"):
            with patch.dict(os.environ, {"PROXYWHIRL_ALLOW_INSECURE_BIND": raw}):
                assert allow_insecure_bind() is True


class TestBindHostAuthContract:
    """Bind host must match container listen posture (PROXYWHIRL_BIND_HOST SSOT)."""

    def test_zero_bind_requires_auth_or_override(self) -> None:
        from proxywhirl.api import app
        from proxywhirl.api.core import lifespan

        with (
            patch.dict(
                os.environ,
                {
                    "PROXYWHIRL_BIND_HOST": "0.0.0.0",
                    "PROXYWHIRL_REQUIRE_AUTH": "false",
                },
                clear=True,
            ),
            pytest.raises(RuntimeError, match="0.0.0.0"),
        ):
            import asyncio

            async def _run() -> None:
                async with lifespan(app):
                    pass

            asyncio.run(_run())

    def test_loopback_bind_allows_auth_disabled(self) -> None:
        from proxywhirl.api import app
        from proxywhirl.api.core import lifespan

        with (
            patch.dict(
                os.environ,
                {
                    "PROXYWHIRL_BIND_HOST": "127.0.0.1",
                    "PROXYWHIRL_REQUIRE_AUTH": "false",
                },
                clear=True,
            ),
            patch("proxywhirl.api.core.ProxyWhirl"),
            patch("proxywhirl.api.core.set_rotator"),
            patch("proxywhirl.api.core.set_storage"),
            patch("proxywhirl.api.core.set_config"),
            patch("proxywhirl.api.core.get_storage", return_value=None),
            patch("proxywhirl.api.core.get_current_rotator", return_value=None),
        ):
            import asyncio

            async def _run() -> None:
                async with lifespan(app):
                    pass

            asyncio.run(_run())


class TestShippedBindConfiguration:
    """Launch surfaces must declare the same host they pass to Uvicorn."""

    def test_root_compose_marks_loopback_stack_as_explicit_local_exception(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        compose = yaml.safe_load((repo_root / "docker-compose.yml").read_text())
        service = compose["services"]["proxywhirl-api"]
        environment_entries = service["environment"]
        environment = dict(
            entry.split("=", maxsplit=1) for entry in environment_entries if "=" in entry
        )

        assert service["ports"] == ["127.0.0.1:8000:8000"]
        assert environment["PROXYWHIRL_BIND_HOST"] == "0.0.0.0"
        assert environment["PROXYWHIRL_ALLOW_INSECURE_BIND"] == "1"
        assert "PROXYWHIRL_CACHE_ENCRYPTION_KEY" in environment_entries

    def test_systemd_uses_declared_bind_host_for_uvicorn(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        unit = (repo_root / "deploy/systemd/proxywhirl.service").read_text()

        assert 'Environment="PROXYWHIRL_BIND_HOST=0.0.0.0"' in unit
        assert "uvicorn proxywhirl.api:app --host ${PROXYWHIRL_BIND_HOST}" in unit
