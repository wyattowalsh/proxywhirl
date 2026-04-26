"""Tests for plugin system."""

from __future__ import annotations

import pytest

from proxywhirl.plugins import (
    HookPlugin,
    MiddlewarePlugin,
    ParserPlugin,
    PluginError,
    PluginRegistry,
    StrategyPlugin,
)


class TestStrategyPlugin(StrategyPlugin):
    """Test strategy plugin implementation."""

    @property
    def name(self) -> str:
        return "test_strategy"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Test strategy plugin"

    @property
    def strategy_type(self) -> str:
        return "test"

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def select_proxy(self, context: dict) -> dict:
        return {"url": "http://test:8080"}


class TestParserPlugin(ParserPlugin):
    """Test parser plugin implementation."""

    @property
    def name(self) -> str:
        return "test_parser"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Test parser plugin"

    @property
    def parser_format(self) -> str:
        return "test-format"

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def parse(self, data: str | bytes) -> list[dict]:
        return [{"url": "http://test:8080"}]


class TestMiddlewarePlugin(MiddlewarePlugin):
    """Test middleware plugin implementation."""

    @property
    def name(self) -> str:
        return "test_middleware"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Test middleware plugin"

    @property
    def middleware_type(self) -> str:
        return "pre_request"

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def process(self, context: dict) -> dict | None:
        context["processed"] = True
        return context


class TestHookPlugin(HookPlugin):
    """Test hook plugin implementation."""

    def __init__(self):
        """Initialize hook plugin."""
        self.called = False

    @property
    def name(self) -> str:
        return "test_hook"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Test hook plugin"

    @property
    def hook_event(self) -> str:
        return "pool_created"

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def execute(self, event_data: dict) -> None:
        self.called = True


@pytest.fixture
def registry() -> PluginRegistry:
    """Create fresh plugin registry."""
    return PluginRegistry()


@pytest.mark.asyncio
async def test_register_strategy_plugin(registry: PluginRegistry) -> None:
    """Test registering a strategy plugin."""
    plugin = TestStrategyPlugin()
    await registry.register(plugin)

    assert registry.get_plugin("test_strategy") is not None
    assert registry.get_strategy_plugin("test") is plugin


@pytest.mark.asyncio
async def test_register_parser_plugin(registry: PluginRegistry) -> None:
    """Test registering a parser plugin."""
    plugin = TestParserPlugin()
    await registry.register(plugin)

    assert registry.get_plugin("test_parser") is not None
    assert registry.get_parser_plugin("test-format") is plugin


@pytest.mark.asyncio
async def test_register_middleware_plugin(registry: PluginRegistry) -> None:
    """Test registering a middleware plugin."""
    plugin = TestMiddlewarePlugin()
    await registry.register(plugin)

    assert registry.get_plugin("test_middleware") is not None
    middlewares = registry.get_middleware_plugins("pre_request")
    assert plugin in middlewares


@pytest.mark.asyncio
async def test_register_hook_plugin(registry: PluginRegistry) -> None:
    """Test registering a hook plugin."""
    plugin = TestHookPlugin()
    await registry.register(plugin)

    assert registry.get_plugin("test_hook") is not None
    hooks = registry.get_hook_plugins("pool_created")
    assert plugin in hooks


@pytest.mark.asyncio
async def test_duplicate_plugin_registration(registry: PluginRegistry) -> None:
    """Test that duplicate plugin registration fails."""
    plugin = TestStrategyPlugin()
    await registry.register(plugin)

    with pytest.raises(PluginError, match="already registered"):
        await registry.register(plugin)


@pytest.mark.asyncio
async def test_unregister_plugin(registry: PluginRegistry) -> None:
    """Test unregistering a plugin."""
    plugin = TestStrategyPlugin()
    await registry.register(plugin)

    await registry.unregister("test_strategy")

    assert registry.get_plugin("test_strategy") is None
    assert registry.get_strategy_plugin("test") is None


@pytest.mark.asyncio
async def test_unregister_nonexistent_plugin(registry: PluginRegistry) -> None:
    """Test unregistering a non-existent plugin fails."""
    with pytest.raises(PluginError, match="not found"):
        await registry.unregister("nonexistent")


@pytest.mark.asyncio
async def test_list_plugins(registry: PluginRegistry) -> None:
    """Test listing all plugins."""
    strategy = TestStrategyPlugin()
    parser = TestParserPlugin()

    await registry.register(strategy)
    await registry.register(parser)

    plugins = registry.list_plugins()
    assert len(plugins) == 2
    assert "test_strategy" in plugins
    assert "test_parser" in plugins


@pytest.mark.asyncio
async def test_middleware_pipeline(registry: PluginRegistry) -> None:
    """Test middleware plugin execution."""
    middleware = TestMiddlewarePlugin()
    await registry.register(middleware)

    middlewares = registry.get_middleware_plugins("pre_request")
    assert len(middlewares) == 1

    context = {"url": "http://test"}
    result = await middlewares[0].process(context)
    assert result["processed"] is True


@pytest.mark.asyncio
async def test_hook_plugin_execution(registry: PluginRegistry) -> None:
    """Test hook plugin execution."""
    hook = TestHookPlugin()
    await registry.register(hook)

    hooks = registry.get_hook_plugins("pool_created")
    assert len(hooks) == 1

    await hooks[0].execute({"pool_id": "test"})
    assert hook.called is True


@pytest.mark.asyncio
async def test_shutdown_all_plugins(registry: PluginRegistry) -> None:
    """Test shutting down all plugins."""
    strategy = TestStrategyPlugin()
    parser = TestParserPlugin()

    await registry.register(strategy)
    await registry.register(parser)

    assert len(registry.list_plugins()) == 2

    await registry.shutdown_all()

    assert len(registry.list_plugins()) == 0


@pytest.mark.asyncio
async def test_multiple_middleware_same_type(registry: PluginRegistry) -> None:
    """Test registering multiple middleware of same type."""

    class Middleware1(MiddlewarePlugin):
        @property
        def name(self) -> str:
            return "mw1"

        @property
        def version(self) -> str:
            return "1.0.0"

        @property
        def description(self) -> str:
            return "Middleware 1"

        @property
        def middleware_type(self) -> str:
            return "pre_request"

        async def initialize(self) -> None:
            pass

        async def shutdown(self) -> None:
            pass

        async def process(self, context: dict) -> dict | None:
            return context

    class Middleware2(MiddlewarePlugin):
        @property
        def name(self) -> str:
            return "mw2"

        @property
        def version(self) -> str:
            return "1.0.0"

        @property
        def description(self) -> str:
            return "Middleware 2"

        @property
        def middleware_type(self) -> str:
            return "pre_request"

        async def initialize(self) -> None:
            pass

        async def shutdown(self) -> None:
            pass

        async def process(self, context: dict) -> dict | None:
            return context

    mw1 = Middleware1()
    mw2 = Middleware2()

    await registry.register(mw1)
    await registry.register(mw2)

    middlewares = registry.get_middleware_plugins("pre_request")
    assert len(middlewares) == 2
