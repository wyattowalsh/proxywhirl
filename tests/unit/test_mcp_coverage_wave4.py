"""Focused coverage for MCP startup, registration, and error boundaries."""

from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from proxywhirl.mcp import server
from proxywhirl.mcp.auth import MCPAuth
from proxywhirl.models import HealthStatus, Proxy, ProxySource


class _FakePool:
    def __init__(self, size: int = 0) -> None:
        self.size = size

    async def asize(self) -> int:
        return self.size


class _FakeRotator:
    def __init__(self, *, pool_size: int = 0, rate_limiter: object | None = None) -> None:
        self.pool = _FakePool(pool_size)
        self.rate_limiter = rate_limiter
        self.add_proxy = AsyncMock(side_effect=self._add_proxy)
        self.aclose = AsyncMock()

    async def _add_proxy(self, proxy: object) -> None:
        self.pool.size += 1


class _FakeMiddleware:
    """Minimal FastMCP middleware base used by the isolated import."""


class _FakeContext:
    """Minimal injectable FastMCP Context marker."""


class _FakeFastMCP:
    def __init__(self, name: str, *, lifespan: object) -> None:
        self.name = name
        self.lifespan = lifespan
        self.middlewares: list[object] = []
        self.tools: list[object] = []
        self.resources: dict[str, tuple[object, dict[str, object]]] = {}
        self.prompts: list[object] = []

    def add_middleware(self, middleware: object) -> None:
        self.middlewares.append(middleware)

    def tool(self) -> Any:
        def decorator(function: object) -> object:
            self.tools.append(function)
            return function

        return decorator

    def resource(self, uri: str, **options: object) -> Any:
        def decorator(function: object) -> object:
            self.resources[uri] = (function, options)
            return function

        return decorator

    def prompt(self) -> Any:
        def decorator(function: object) -> object:
            self.prompts.append(function)
            return function

        return decorator

    def run(self, *, transport: str) -> None:
        return None


@pytest.fixture(autouse=True)
async def reset_mcp_globals(monkeypatch: pytest.MonkeyPatch) -> Any:
    """Keep this module's global MCP state isolated from the broader suite."""
    await server.cleanup_rotator()
    server.set_auth(MCPAuth())
    monkeypatch.setattr(server, "_mcp_db_path", None)
    yield
    await server.cleanup_rotator()
    server.set_auth(None)


@pytest.fixture
def fastmcp_server_module(monkeypatch: pytest.MonkeyPatch) -> Any:
    """Load MCP server in isolation with the optional FastMCP surface available."""
    fastmcp_module = ModuleType("fastmcp")
    fastmcp_module.__dict__.update({"Context": _FakeContext, "FastMCP": _FakeFastMCP})

    fastmcp_server_package = ModuleType("fastmcp.server")
    fastmcp_server_package.__dict__["__path__"] = []
    middleware_module = ModuleType("fastmcp.server.middleware")
    middleware_module.__dict__.update({"Middleware": _FakeMiddleware, "MiddlewareContext": object})

    monkeypatch.setitem(sys.modules, "fastmcp", fastmcp_module)
    monkeypatch.setitem(sys.modules, "fastmcp.server", fastmcp_server_package)
    monkeypatch.setitem(sys.modules, "fastmcp.server.middleware", middleware_module)

    module_name = "proxywhirl_mcp_server_wave4"
    module_path = Path(server.__file__)
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    isolated_module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, module_name, isolated_module)
    spec.loader.exec_module(isolated_module)
    return isolated_module


async def test_fastmcp_startup_registers_middleware_tool_resources_and_prompts(
    fastmcp_server_module: Any,
) -> None:
    """Optional FastMCP startup should expose the complete curated MCP surface."""
    module = fastmcp_server_module
    fake_mcp = module.mcp

    assert isinstance(fake_mcp, _FakeFastMCP)
    assert fake_mcp.name == "ProxyWhirl"
    assert fake_mcp.lifespan is module._mcp_lifespan
    assert len(fake_mcp.middlewares) == 1
    assert len(fake_mcp.tools) == 1
    assert set(fake_mcp.resources) == {
        "resource://proxywhirl/health",
        "resource://proxywhirl/config",
    }
    assert all(
        options == {"mime_type": "application/json"} for _, options in fake_mcp.resources.values()
    )
    assert len(fake_mcp.prompts) == 2


async def test_generated_middleware_authorizes_tools_and_resources(
    fastmcp_server_module: Any,
) -> None:
    """The dynamically generated middleware must pass valid auth and reject invalid auth."""
    module = fastmcp_server_module
    module.set_auth(MCPAuth(api_key="expected-key"))
    middleware = module.ProxyWhirlAuthMiddleware()
    valid_context = SimpleNamespace(
        message=SimpleNamespace(params=SimpleNamespace(arguments={"action": "list"})),
        metadata={"api_key": "expected-key"},
    )
    invalid_context = SimpleNamespace(
        message=SimpleNamespace(params=SimpleNamespace(arguments={"action": "list"})),
        metadata={"api_key": "wrong-key"},
    )
    tool_next = AsyncMock(return_value={"ok": True})
    resource_next = AsyncMock(return_value="resource payload")

    assert await middleware.on_call_tool(valid_context, tool_next) == {"ok": True}
    tool_next.assert_awaited_once_with(valid_context)
    denied_tool = await middleware.on_call_tool(invalid_context, tool_next)
    assert denied_tool == {"error": "Authentication failed: Invalid API key", "code": 401}

    assert await middleware.on_read_resource(valid_context, resource_next) == "resource payload"
    resource_next.assert_awaited_once_with(valid_context)
    denied_resource = await middleware.on_read_resource(invalid_context, resource_next)
    assert denied_resource == {
        "error": "Authentication failed: Invalid API key",
        "code": 401,
    }


async def test_registered_resource_and_prompt_wrappers_delegate_context(
    fastmcp_server_module: Any,
) -> None:
    """Registered wrappers should delegate injected context and return canonical prompt text."""
    module = fastmcp_server_module
    context = _FakeContext()
    health_impl = AsyncMock(return_value='{"health": "ok"}')
    config_impl = AsyncMock(return_value='{"config": "ok"}')
    selection_impl = AsyncMock(return_value="selection workflow")
    troubleshooting_impl = AsyncMock(return_value="troubleshooting workflow")
    module._get_proxy_health_impl = health_impl
    module._get_proxy_config_impl = config_impl
    module._proxy_selection_workflow_prompt = selection_impl
    module._troubleshooting_workflow_prompt = troubleshooting_impl

    assert await module.proxy_health_resource(context) == '{"health": "ok"}'
    assert await module.proxy_config_resource(context) == '{"config": "ok"}'
    health_impl.assert_awaited_once_with(ctx=context)
    config_impl.assert_awaited_once_with(ctx=context)
    assert await module.proxy_selection_workflow() == "selection workflow"
    assert await module.troubleshooting_workflow() == "troubleshooting workflow"
    selection_impl.assert_awaited_once_with()
    troubleshooting_impl.assert_awaited_once_with()


async def test_get_rotator_loads_storage_models_and_closes_storage(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Cold startup should add model-returning storage records and close the adapter."""
    from proxywhirl import storage as storage_module

    db_path = tmp_path / "models.db"
    db_path.touch()
    proxy = Proxy(
        url="http://stored.example.com:8080",
        protocol="http",
        source=ProxySource.USER,
        health_status=HealthStatus.HEALTHY,
    )
    storage_adapter = SimpleNamespace(
        initialize=AsyncMock(),
        load_models=AsyncMock(return_value=[proxy]),
        close=AsyncMock(),
    )
    rotator = _FakeRotator()
    monkeypatch.setattr(server, "_rotator", None)
    monkeypatch.setattr(server, "_mcp_db_path", db_path)
    monkeypatch.setattr(server, "AsyncProxyWhirl", lambda: rotator)
    monkeypatch.setattr(server, "_mcp_auto_fetch_allowed", lambda: False)
    monkeypatch.setattr(storage_module, "SQLiteStorage", lambda path: storage_adapter)

    assert await server.get_rotator() is rotator
    storage_adapter.initialize.assert_awaited_once_with()
    storage_adapter.load_models.assert_awaited_once_with()
    rotator.add_proxy.assert_awaited_once_with(proxy)
    storage_adapter.close.assert_awaited_once_with()
    assert await rotator.pool.asize() == 1


async def test_get_rotator_sanitizes_storage_load_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Storage startup failures should be non-fatal and redact embedded URL credentials."""
    from proxywhirl import storage as storage_module

    db_path = tmp_path / "broken.db"
    db_path.touch()
    leaked_url = "http://probe_user:probe_password@storage.example.com:8080"
    storage_adapter = SimpleNamespace(
        initialize=AsyncMock(),
        load_models=AsyncMock(side_effect=RuntimeError(f"load failed via {leaked_url}")),
        close=AsyncMock(),
    )
    rotator = _FakeRotator()
    warning = MagicMock()
    monkeypatch.setattr(server, "_rotator", None)
    monkeypatch.setattr(server, "_mcp_db_path", db_path)
    monkeypatch.setattr(server, "AsyncProxyWhirl", lambda: rotator)
    monkeypatch.setattr(server, "_mcp_auto_fetch_allowed", lambda: False)
    monkeypatch.setattr(server.logger, "warning", warning)
    monkeypatch.setattr(storage_module, "SQLiteStorage", lambda path: storage_adapter)

    assert await server.get_rotator() is rotator
    warning.assert_called_once()
    warning_text = str(warning.call_args.args[0])
    assert "probe_user" not in warning_text
    assert "probe_password" not in warning_text
    assert "***:***@storage.example.com:8080" in warning_text
    storage_adapter.close.assert_awaited_once_with()


async def test_unified_tool_awaits_context_logging_before_dispatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Context logging must settle inside the tool call instead of leaking a task."""
    events: list[str] = []

    class Context:
        async def info(self, message: str) -> None:
            await asyncio.sleep(0)
            events.append(f"log:{message}")

    async def list_impl(*, ctx: object | None = None) -> dict[str, object]:
        events.append("dispatch")
        return {"proxies": []}

    monkeypatch.setattr(server, "_authorize_tool_call", lambda *args, **kwargs: None)
    monkeypatch.setattr(server, "_list_proxies_impl", list_impl)

    result = await server._proxywhirl_tool("list", ctx=Context())

    assert result == {"proxies": []}
    assert events == ["log:proxywhirl action=list", "dispatch"]


async def test_auto_fetch_failure_is_non_fatal_and_redacted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Bootstrap fetch errors should stop cleanly without leaking URL credentials."""
    from proxywhirl.rotator import _bootstrap

    leaked_url = "socks5://probe_user:probe_password@fetch.example.com:1080"
    fetch_candidates = AsyncMock(side_effect=RuntimeError(f"fetch failed via {leaked_url}"))
    warning = MagicMock()
    rotator = _FakeRotator()
    monkeypatch.setattr(_bootstrap, "_fetch_bootstrap_candidates", fetch_candidates)
    monkeypatch.setattr(server.logger, "warning", warning)

    await server._auto_fetch_proxies(rotator, max_proxies=7)

    fetch_candidates.assert_awaited_once()
    rotator.add_proxy.assert_not_awaited()
    warning.assert_called_once()
    warning_text = str(warning.call_args.args[0])
    assert "probe_user" not in warning_text
    assert "probe_password" not in warning_text
    assert "***:***@fetch.example.com:1080" in warning_text


async def test_health_reports_configured_rate_limiter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Pool health should include configured rate-limiter capacity and window."""
    rotator = _FakeRotator(
        rate_limiter=SimpleNamespace(max_requests=120, time_window=60),
    )
    monkeypatch.setattr(server, "get_rotator", AsyncMock(return_value=rotator))
    monkeypatch.setattr(server, "list_proxy_views_async", AsyncMock(return_value=[]))

    result = await server._get_health_impl()

    assert result["rate_limit"] == {
        "enabled": True,
        "max_requests": 120,
        "time_window_seconds": 60,
    }


async def test_health_rate_limiter_introspection_failure_uses_safe_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Broken rate-limiter metadata should not break the health resource."""

    class BrokenRateLimiter:
        @property
        def max_requests(self) -> int:
            raise RuntimeError("metadata unavailable")

    rotator = _FakeRotator(rate_limiter=BrokenRateLimiter())
    monkeypatch.setattr(server, "get_rotator", AsyncMock(return_value=rotator))
    monkeypatch.setattr(server, "list_proxy_views_async", AsyncMock(return_value=[]))

    result = await server._get_health_impl()

    assert result["rate_limit"] == {
        "enabled": False,
        "message": "Rate limiting not configured",
    }


@pytest.mark.parametrize("resource", ["health", "config"])
async def test_resources_reject_missing_configured_auth_without_runtime_access(
    monkeypatch: pytest.MonkeyPatch,
    resource: str,
) -> None:
    """Protected resources should reject missing auth before touching rotator state."""
    server.set_auth(MCPAuth(api_key="required-key"))
    get_rotator = AsyncMock()
    get_health = AsyncMock()
    monkeypatch.setattr(server, "get_rotator", get_rotator)
    monkeypatch.setattr(server, "_get_health_impl", get_health)

    if resource == "health":
        payload = json.loads(await server._get_proxy_health_impl())
    else:
        payload = json.loads(await server._get_proxy_config_impl())

    assert payload == {"error": "Authentication failed: Invalid API key", "code": 401}
    get_rotator.assert_not_awaited()
    get_health.assert_not_awaited()
