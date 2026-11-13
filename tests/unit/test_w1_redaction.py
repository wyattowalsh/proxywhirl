"""W1-T4 redaction sweep: async logs, validators, CLILock, exception attrs."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import ValidationError

from proxywhirl.exceptions import ProxyWhirlError
from proxywhirl.models import Proxy
from proxywhirl.utils import CLILock, create_proxy_from_url


def test_create_proxy_from_url_masks_credentials_in_error() -> None:
    with pytest.raises(ValueError) as exc_info:
        create_proxy_from_url("http://user:pass@host")
    assert "user:pass" not in str(exc_info.value)
    assert "pass" not in str(exc_info.value) or "***" in str(exc_info.value)


def test_proxy_validator_masks_invalid_credentialed_url() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Proxy(url="not-a-scheme://user:pass@x:1")
    messages = " ".join(err.get("msg", "") for err in exc_info.value.errors())
    assert "user:pass" not in messages


def test_proxy_whirl_error_redacts_operation_and_recovery_hint() -> None:
    err = ProxyWhirlError(
        "failed",
        operation="GET http://user:pass@proxy.example.com:8080",
        recovery_hint="retry password=hunter2",
    )
    assert err.operation is not None
    assert "user:pass" not in err.operation
    upper = ProxyWhirlError("failed", operation="GET HTTP://user:pass@proxy.example.com:8080")
    assert upper.operation is not None
    assert "user:pass" not in upper.operation
    assert err.recovery_hint is not None
    assert "hunter2" not in err.recovery_hint


def test_clilock_redacts_argv_on_contention(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import typer

    lock_dir = tmp_path
    leaked = "http://user:pass@proxy.example.com:8080"
    monkeypatch.setattr("sys.argv", ["proxywhirl", "request", leaked])

    first = CLILock(lock_dir)
    with first:
        lock_json = json.loads((lock_dir / ".proxywhirl.lock.json").read_text())
        assert "user:pass" not in lock_json["command"]
        assert "***" in lock_json["command"]

        second = CLILock(lock_dir)
        with pytest.raises(typer.Exit) as exc_info:
            second.__enter__()
        assert exc_info.value.exit_code == 4


@pytest.mark.asyncio
async def test_async_rotator_logs_redacted_target_url() -> None:
    from proxywhirl.models import HealthStatus, ProxyPool, ProxySource
    from proxywhirl.rotator.async_ import AsyncProxyWhirl

    proxy = Proxy(
        url="http://proxy.example.com:8080",
        protocol="http",
        health_status=HealthStatus.HEALTHY,
        source=ProxySource.USER,
    )
    rotator = AsyncProxyWhirl()
    rotator.pool = ProxyPool(name="redact", proxies=[proxy])
    rotator.orchestrator = MagicMock()

    async def _fake_execute(*_args: object, **kwargs: object) -> None:
        factory = kwargs["request_fn_factory"]  # type: ignore[index]
        factory(proxy)
        raise RuntimeError("stop-after-log")

    rotator.orchestrator.execute_async = AsyncMock(side_effect=_fake_execute)

    captured: list[str] = []

    def _sink(message: object) -> None:
        captured.append(str(message))

    from loguru import logger

    sink_id = logger.add(_sink, format="{message}")
    try:
        with pytest.raises(Exception):
            await rotator._make_request("GET", "https://user:token@api.example.com/secret")
        joined = "\n".join(captured)
    finally:
        logger.remove(sink_id)

    assert "user:token" not in joined
    assert "Making GET request" in joined


@pytest.mark.asyncio
async def test_validator_debug_logs_redact_userinfo_without_patcher() -> None:
    """Validator debug paths must call redact_url even if the loguru patcher is off."""
    from loguru import logger

    from proxywhirl.fetchers.validator import ProxyValidator, ValidationResult

    captured: list[str] = []

    def _sink(message: object) -> None:
        captured.append(str(message))

    sink_id = logger.add(_sink, format="{message}", level="DEBUG")
    try:
        validator = ProxyValidator()
        await validator.validate({"url": "http://user:pass@proxy.example.com:8080"})
        validator._set_cached_result(
            {"url": "http://user:pass@proxy.example.com:8080"},
            ValidationResult(is_valid=False, response_time_ms=None),
        )
        validator._get_cached_result({"url": "http://user:pass@proxy.example.com:8080"})
        joined = "\n".join(captured)
    finally:
        logger.remove(sink_id)

    assert captured
    assert "user:pass" not in joined
    assert "Validation cache hit" in joined or "Skipping validation" in joined


def test_fetcher_request_cache_debug_redacts_userinfo() -> None:
    from loguru import logger

    from proxywhirl.fetchers.fetcher import ProxyFetcher

    captured: list[str] = []

    def _sink(message: object) -> None:
        captured.append(str(message))

    sink_id = logger.add(_sink, format="{message}", level="DEBUG")
    try:
        fetcher = ProxyFetcher()
        url = "http://user:pass@source.example.com/list"
        fetcher._set_cached_response(url, "ok")
        assert fetcher._get_cached_response(url) == "ok"
        joined = "\n".join(captured)
    finally:
        logger.remove(sink_id)

    assert "Request cache hit" in joined
    assert "user:pass" not in joined
