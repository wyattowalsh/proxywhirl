"""Plugin system for custom proxy parsers.

Allows third-party extensions to register custom parsers for proxy formats.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from loguru import logger


class ParserPlugin(ABC):
    """Base class for proxy parser plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name for this parser."""
        pass

    @property
    @abstractmethod
    def format(self) -> str:
        """Format this parser handles (e.g., 'json', 'csv', 'xml')."""
        pass

    @abstractmethod
    def can_parse(self, content: str) -> bool:
        """Check if this parser can handle the content."""
        pass

    @abstractmethod
    def parse(self, content: str) -> list[dict[str, Any]]:
        """Parse content and return list of proxy dicts."""
        pass


class ParserPluginRegistry:
    """Registry for proxy parser plugins."""

    _plugins: dict[str, type[ParserPlugin]] = {}

    @classmethod
    def register(cls, plugin_class: type[ParserPlugin]) -> None:
        """Register a new parser plugin."""
        plugin = plugin_class()
        key = f"{plugin.format}:{plugin.name}"

        if key in cls._plugins:
            logger.warning(f"Overwriting parser plugin: {key}")

        cls._plugins[key] = plugin_class
        logger.info(f"Registered parser plugin: {key}")

    @classmethod
    def unregister(cls, format_name: str, parser_name: str) -> None:
        """Unregister a parser plugin."""
        key = f"{format_name}:{parser_name}"

        if key in cls._plugins:
            del cls._plugins[key]
            logger.info(f"Unregistered parser plugin: {key}")

    @classmethod
    def get(cls, format_name: str, parser_name: str) -> Optional[ParserPlugin]:
        """Get a registered parser plugin."""
        key = f"{format_name}:{parser_name}"
        plugin_class = cls._plugins.get(key)

        if plugin_class:
            return plugin_class()

        return None

    @classmethod
    def get_by_format(cls, format_name: str) -> list[ParserPlugin]:
        """Get all parsers for a specific format."""
        plugins = []

        for key, plugin_class in cls._plugins.items():
            if key.startswith(f"{format_name}:"):
                plugins.append(plugin_class())

        return plugins

    @classmethod
    def list_all(cls) -> dict[str, type[ParserPlugin]]:
        """List all registered plugins."""
        return cls._plugins.copy()

    @classmethod
    def find_parser(cls, content: str) -> Optional[ParserPlugin]:
        """Find a parser that can handle the given content."""
        for plugin_class in cls._plugins.values():
            plugin = plugin_class()
            if plugin.can_parse(content):
                logger.debug(f"Found matching parser: {plugin.name}")
                return plugin

        return None


# Example custom parser plugin


class XMLProxyParser(ParserPlugin):
    """Example XML proxy parser plugin."""

    @property
    def name(self) -> str:
        """Name of this parser."""
        return "xml_parser"

    @property
    def format(self) -> str:
        """Format this parser handles."""
        return "xml"

    def can_parse(self, content: str) -> bool:
        """Check if content is XML."""
        return content.strip().startswith("<?xml") or "<proxy" in content.lower()

    def parse(self, content: str) -> list[dict[str, Any]]:
        """Parse XML content."""
        import xml.etree.ElementTree as ET

        proxies = []

        try:
            root = ET.fromstring(content)

            for proxy_elem in root.findall(".//proxy"):
                proxy_dict = {}

                for child in proxy_elem:
                    proxy_dict[child.tag] = child.text

                if "url" in proxy_dict or "host" in proxy_dict:
                    proxies.append(proxy_dict)

        except ET.ParseError as e:
            logger.error(f"Failed to parse XML: {e}")

        return proxies


class YAMLProxyParser(ParserPlugin):
    """Example YAML proxy parser plugin."""

    @property
    def name(self) -> str:
        """Name of this parser."""
        return "yaml_parser"

    @property
    def format(self) -> str:
        """Format this parser handles."""
        return "yaml"

    def can_parse(self, content: str) -> bool:
        """Check if content is YAML."""
        # Simple heuristic: YAML often starts with ---
        return content.strip().startswith("---") or "\n- " in content

    def parse(self, content: str) -> list[dict[str, Any]]:
        """Parse YAML content."""
        try:
            import yaml

            data = yaml.safe_load(content)

            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "proxies" in data:
                return data["proxies"]

            return []

        except ImportError:
            logger.error("PyYAML not installed. Cannot parse YAML.")
            return []
        except Exception as e:
            logger.error(f"Failed to parse YAML: {e}")
            return []


class JSONLProxyParser(ParserPlugin):
    """Example JSONL (JSON Lines) proxy parser plugin."""

    @property
    def name(self) -> str:
        """Name of this parser."""
        return "jsonl_parser"

    @property
    def format(self) -> str:
        """Format this parser handles."""
        return "jsonl"

    def can_parse(self, content: str) -> bool:
        """Check if content is JSONL."""
        import json

        for line in content.strip().split("\n"):
            if not line.strip():
                continue

            try:
                json.loads(line)
            except json.JSONDecodeError:
                return False

        return True

    def parse(self, content: str) -> list[dict[str, Any]]:
        """Parse JSONL content."""
        import json

        proxies = []

        for line in content.strip().split("\n"):
            if not line.strip():
                continue

            try:
                proxy_dict = json.loads(line)
                proxies.append(proxy_dict)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSONL line: {e}")

        return proxies


# Register default plugins
def register_default_plugins() -> None:
    """Register built-in parser plugins."""
    ParserPluginRegistry.register(XMLProxyParser)
    ParserPluginRegistry.register(YAMLProxyParser)
    ParserPluginRegistry.register(JSONLProxyParser)
    logger.info("Registered default parser plugins")
