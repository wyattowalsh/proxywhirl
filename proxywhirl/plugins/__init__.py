"""Extensible plugin system for ProxyWhirl.

Provides:
- Plugin interface and base classes
- Strategy plugins (custom rotation strategies)
- Parser plugins (custom proxy formats)
- Middleware plugins (request/response processing)
- Plugin registry and loader
"""

from __future__ import annotations

import importlib
import inspect
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, TypeVar

from loguru import logger

T = TypeVar("T")


class PluginError(Exception):
    """Base exception for plugin system."""

    pass


class PluginInterface(ABC):
    """Base interface for all plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version (semver)."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description."""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize plugin (called when registered)."""

    @abstractmethod
    async def shutdown(self) -> None:
        """Cleanup plugin resources."""


class StrategyPlugin(PluginInterface):
    """Plugin interface for custom rotation strategies.

    Plugins implementing this interface provide custom rotation
    strategy implementations.
    """

    @property
    @abstractmethod
    def strategy_type(self) -> str:
        """Unique identifier for the strategy."""

    @abstractmethod
    async def select_proxy(self, context: dict[str, Any]) -> Any:
        """Select a proxy from the pool.

        Args:
            context: Selection context with pool, proxies, metrics

        Returns:
            Selected proxy
        """


class ParserPlugin(PluginInterface):
    """Plugin interface for custom proxy parsers.

    Plugins implementing this interface provide parsers
    for custom proxy formats.
    """

    @property
    @abstractmethod
    def parser_format(self) -> str:
        """Format identifier (e.g., 'custom-json')."""

    @abstractmethod
    async def parse(self, data: str | bytes) -> list[dict[str, Any]]:
        """Parse proxy data.

        Args:
            data: Raw proxy data

        Returns:
            List of parsed proxy dicts
        """


class MiddlewarePlugin(PluginInterface):
    """Plugin interface for request/response middleware.

    Plugins implementing this interface can hook into
    request/response pipeline.
    """

    @property
    @abstractmethod
    def middleware_type(self) -> str:
        """Middleware type: 'pre_request', 'post_request', 'pre_response'."""

    @abstractmethod
    async def process(self, context: dict[str, Any]) -> dict[str, Any] | None:
        """Process request/response.

        Args:
            context: Request/response context

        Returns:
            Modified context or None to pass through
        """


class HookPlugin(PluginInterface):
    """Plugin interface for lifecycle hooks."""

    @property
    @abstractmethod
    def hook_event(self) -> str:
        """Hook event name (e.g., 'pool_created', 'rotation_executed')."""

    @abstractmethod
    async def execute(self, event_data: dict[str, Any]) -> None:
        """Execute hook.

        Args:
            event_data: Event-specific data
        """


class PluginRegistry:
    """Central registry for plugins.

    Manages plugin registration, loading, and lifecycle.
    """

    def __init__(self) -> None:
        """Initialize plugin registry."""
        self._plugins: dict[str, PluginInterface] = {}
        self._strategy_plugins: dict[str, StrategyPlugin] = {}
        self._parser_plugins: dict[str, ParserPlugin] = {}
        self._middleware_plugins: dict[str, list[MiddlewarePlugin]] = {
            "pre_request": [],
            "post_request": [],
            "pre_response": [],
        }
        self._hook_plugins: dict[str, list[HookPlugin]] = {}

    async def register(self, plugin: PluginInterface) -> None:
        """Register a plugin.

        Args:
            plugin: Plugin instance to register

        Raises:
            PluginError: If plugin name already registered
        """
        if plugin.name in self._plugins:
            raise PluginError(f"Plugin '{plugin.name}' already registered")

        try:
            await plugin.initialize()
            self._plugins[plugin.name] = plugin

            # Register by type
            if isinstance(plugin, StrategyPlugin):
                self._strategy_plugins[plugin.strategy_type] = plugin
                logger.info(
                    "Registered strategy plugin",
                    name=plugin.name,
                    version=plugin.version,
                    strategy=plugin.strategy_type,
                )

            elif isinstance(plugin, ParserPlugin):
                self._parser_plugins[plugin.parser_format] = plugin
                logger.info(
                    "Registered parser plugin",
                    name=plugin.name,
                    version=plugin.version,
                    format=plugin.parser_format,
                )

            elif isinstance(plugin, MiddlewarePlugin):
                mw_type = plugin.middleware_type
                if mw_type not in self._middleware_plugins:
                    self._middleware_plugins[mw_type] = []
                self._middleware_plugins[mw_type].append(plugin)
                logger.info(
                    "Registered middleware plugin",
                    name=plugin.name,
                    version=plugin.version,
                    type=mw_type,
                )

            elif isinstance(plugin, HookPlugin):
                event = plugin.hook_event
                if event not in self._hook_plugins:
                    self._hook_plugins[event] = []
                self._hook_plugins[event].append(plugin)
                logger.info(
                    "Registered hook plugin",
                    name=plugin.name,
                    version=plugin.version,
                    event=event,
                )

            logger.info(
                "Plugin registered successfully",
                name=plugin.name,
                version=plugin.version,
            )

        except Exception as e:
            logger.error(
                "Failed to register plugin",
                name=plugin.name,
                error=e,
            )
            raise PluginError(f"Failed to register plugin '{plugin.name}': {e}") from e

    async def unregister(self, plugin_name: str) -> None:
        """Unregister a plugin.

        Args:
            plugin_name: Name of plugin to unregister
        """
        plugin = self._plugins.pop(plugin_name, None)
        if not plugin:
            raise PluginError(f"Plugin '{plugin_name}' not found")

        try:
            await plugin.shutdown()

            # Remove from type-specific registries
            if isinstance(plugin, StrategyPlugin):
                self._strategy_plugins.pop(plugin.strategy_type, None)
            elif isinstance(plugin, ParserPlugin):
                self._parser_plugins.pop(plugin.parser_format, None)
            elif isinstance(plugin, MiddlewarePlugin):
                mw_type = plugin.middleware_type
                if mw_type in self._middleware_plugins:
                    self._middleware_plugins[mw_type] = [
                        p for p in self._middleware_plugins[mw_type] if p.name != plugin_name
                    ]
            elif isinstance(plugin, HookPlugin):
                event = plugin.hook_event
                if event in self._hook_plugins:
                    self._hook_plugins[event] = [
                        p for p in self._hook_plugins[event] if p.name != plugin_name
                    ]

            logger.info("Plugin unregistered", name=plugin_name)

        except Exception as e:
            logger.error(
                "Error unregistering plugin",
                name=plugin_name,
                error=e,
            )

    def get_plugin(self, name: str) -> PluginInterface | None:
        """Get plugin by name.

        Args:
            name: Plugin name

        Returns:
            Plugin instance or None
        """
        return self._plugins.get(name)

    def get_strategy_plugin(self, strategy_type: str) -> StrategyPlugin | None:
        """Get strategy plugin by type.

        Args:
            strategy_type: Strategy type identifier

        Returns:
            Strategy plugin or None
        """
        return self._strategy_plugins.get(strategy_type)

    def get_parser_plugin(self, format: str) -> ParserPlugin | None:
        """Get parser plugin by format.

        Args:
            format: Format identifier

        Returns:
            Parser plugin or None
        """
        return self._parser_plugins.get(format)

    def get_middleware_plugins(self, middleware_type: str) -> list[MiddlewarePlugin]:
        """Get all middleware plugins of a type.

        Args:
            middleware_type: Middleware type

        Returns:
            List of middleware plugins
        """
        return self._middleware_plugins.get(middleware_type, [])

    def get_hook_plugins(self, event: str) -> list[HookPlugin]:
        """Get all hook plugins for an event.

        Args:
            event: Event name

        Returns:
            List of hook plugins
        """
        return self._hook_plugins.get(event, [])

    def list_plugins(self) -> dict[str, dict[str, str]]:
        """List all registered plugins.

        Returns:
            Dict of plugin name -> (name, version, description)
        """
        return {
            name: {
                "name": plugin.name,
                "version": plugin.version,
                "description": plugin.description,
            }
            for name, plugin in self._plugins.items()
        }

    async def shutdown_all(self) -> None:
        """Shutdown all plugins."""
        for plugin in list(self._plugins.values()):
            try:
                await plugin.shutdown()
            except Exception as e:
                logger.error(
                    "Error shutting down plugin",
                    name=plugin.name,
                    error=e,
                )
        self._plugins.clear()
        self._strategy_plugins.clear()
        self._parser_plugins.clear()
        self._middleware_plugins.clear()
        self._hook_plugins.clear()


class PluginLoader:
    """Load plugins from modules and files."""

    def __init__(self, registry: PluginRegistry) -> None:
        """Initialize loader.

        Args:
            registry: Plugin registry
        """
        self.registry = registry

    async def load_from_module(self, module_path: str) -> list[PluginInterface]:
        """Load plugins from a Python module.

        Args:
            module_path: Import path (e.g., 'mypackage.plugins')

        Returns:
            List of loaded plugins

        Raises:
            PluginError: If module cannot be loaded
        """
        try:
            # Try to import the module
            if module_path in sys.modules:
                module = sys.modules[module_path]
            else:
                module = importlib.import_module(module_path)

            # Find all PluginInterface subclasses
            plugins: list[PluginInterface] = []
            for name, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, PluginInterface)
                    and obj is not PluginInterface
                    and obj is not StrategyPlugin
                    and obj is not ParserPlugin
                    and obj is not MiddlewarePlugin
                    and obj is not HookPlugin
                ):
                    try:
                        instance = obj()
                        await self.registry.register(instance)
                        plugins.append(instance)
                    except Exception as e:
                        logger.error(
                            "Failed to instantiate plugin",
                            class_name=name,
                            error=e,
                        )

            return plugins

        except ImportError as e:
            raise PluginError(f"Failed to import module '{module_path}': {e}") from e

    async def load_from_directory(self, directory: Path | str) -> list[PluginInterface]:
        """Load plugins from all modules in a directory.

        Args:
            directory: Directory path

        Returns:
            List of loaded plugins
        """
        directory = Path(directory)
        if not directory.is_dir():
            raise PluginError(f"Not a directory: {directory}")

        plugins: list[PluginInterface] = []
        for py_file in sorted(directory.glob("*.py")):
            if py_file.name.startswith("_"):
                continue

            module_name = py_file.stem
            try:
                # Add directory to sys.path temporarily
                dir_str = str(directory)
                if dir_str not in sys.path:
                    sys.path.insert(0, dir_str)

                module = importlib.import_module(module_name)
                loaded = await self.load_from_module(module.__name__)
                plugins.extend(loaded)

            except Exception as e:
                logger.error(
                    "Failed to load plugin module",
                    module=module_name,
                    error=e,
                )

        return plugins


# Global plugin registry
_plugin_registry: PluginRegistry | None = None


def get_plugin_registry() -> PluginRegistry:
    """Get or create global plugin registry."""
    global _plugin_registry
    if _plugin_registry is None:
        _plugin_registry = PluginRegistry()
    return _plugin_registry


def set_plugin_registry(registry: PluginRegistry) -> None:
    """Set global plugin registry (for testing)."""
    global _plugin_registry
    _plugin_registry = registry


__all__ = [
    "PluginError",
    "PluginInterface",
    "StrategyPlugin",
    "ParserPlugin",
    "MiddlewarePlugin",
    "HookPlugin",
    "PluginRegistry",
    "PluginLoader",
    "get_plugin_registry",
    "set_plugin_registry",
]
