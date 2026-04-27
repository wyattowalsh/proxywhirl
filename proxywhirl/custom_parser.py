"""Custom proxy parser support and plugin framework."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol

from loguru import logger


class ParseFormat(str, Enum):
    """Supported parse formats."""

    JSON = "json"
    CSV = "csv"
    TEXT = "text"
    HTML_TABLE = "html_table"
    CUSTOM = "custom"


@dataclass
class ParseResult:
    """Result of parsing proxy data."""

    proxies: list[dict[str, Any]]
    format: ParseFormat
    source_url: str
    success: bool
    error_message: str | None = None
    metadata: dict = None

    def __post_init__(self) -> None:
        """Post-init handler."""
        if self.metadata is None:
            self.metadata = {}


class ProxyParser(Protocol):
    """Protocol for custom proxy parsers."""

    def __call__(
        self,
        data: str | bytes,
        **kwargs: Any,
    ) -> ParseResult:
        """Parse proxy data and return result."""
        ...


class CustomParserRegistry:
    """
    Registry for custom proxy parsers.

    Allows registration of custom parsers for proprietary or
    special proxy formats.
    """

    def __init__(self):
        """Initialize parser registry."""
        self.parsers: dict[str, ProxyParser] = {}
        self.format_mappings: dict[str, str] = {}

    def register_parser(
        self,
        name: str,
        parser_func: ProxyParser,
        format_name: str | None = None,
    ) -> None:
        """
        Register a custom parser.

        Args:
            name: Parser name
            parser_func: Parser callable
            format_name: Associated format name

        Raises:
            ValueError: If parser already registered
        """
        if name in self.parsers:
            raise ValueError(f"Parser already registered: {name}")

        self.parsers[name] = parser_func
        logger.info(f"Registered custom parser: {name}")

        if format_name:
            self.format_mappings[format_name] = name

    def unregister_parser(self, name: str) -> None:
        """
        Unregister a parser.

        Args:
            name: Parser name
        """
        if name in self.parsers:
            del self.parsers[name]
            logger.info(f"Unregistered parser: {name}")

    def get_parser(self, name: str) -> ProxyParser | None:
        """
        Get a registered parser.

        Args:
            name: Parser name

        Returns:
            Parser function or None
        """
        return self.parsers.get(name)

    def parse(
        self,
        parser_name: str,
        data: str | bytes,
        source_url: str = "",
        **kwargs: Any,
    ) -> ParseResult:
        """
        Parse data with a registered parser.

        Args:
            parser_name: Parser name
            data: Data to parse
            source_url: Source URL for metadata
            **kwargs: Additional arguments for parser

        Returns:
            Parse result
        """
        parser = self.get_parser(parser_name)

        if not parser:
            return ParseResult(
                proxies=[],
                format=ParseFormat.CUSTOM,
                source_url=source_url,
                success=False,
                error_message=f"Parser not found: {parser_name}",
            )

        try:
            result = parser(data, **kwargs)
            logger.debug(f"Parsed {len(result.proxies)} proxies using {parser_name}")
            return result

        except Exception as e:
            logger.error(f"Error parsing with {parser_name}: {e}")

            return ParseResult(
                proxies=[],
                format=ParseFormat.CUSTOM,
                source_url=source_url,
                success=False,
                error_message=str(e),
            )

    def list_parsers(self) -> list[str]:
        """
        List all registered parsers.

        Returns:
            List of parser names
        """
        return list(self.parsers.keys())

    def get_parser_info(self, name: str) -> dict[str, Any]:
        """
        Get information about a parser.

        Args:
            name: Parser name

        Returns:
            Parser info dictionary
        """
        parser = self.get_parser(name)

        if not parser:
            return {}

        return {
            "name": name,
            "callable": str(parser),
            "format_mapping": next(
                (fmt for fmt, pname in self.format_mappings.items() if pname == name),
                None,
            ),
        }

    def validate_parser(self, name: str) -> bool:
        """
        Validate that a parser is callable.

        Args:
            name: Parser name

        Returns:
            True if valid
        """
        parser = self.get_parser(name)

        if not parser:
            return False

        return callable(parser)

    def test_parser(
        self,
        name: str,
        test_data: str | bytes,
    ) -> dict[str, Any]:
        """
        Test a parser with sample data.

        Args:
            name: Parser name
            test_data: Test data

        Returns:
            Test result
        """
        result = self.parse(name, test_data, source_url="test")

        return {
            "parser": name,
            "success": result.success,
            "proxy_count": len(result.proxies),
            "error": result.error_message,
        }

    def clone_parser(self, src_name: str, dst_name: str) -> bool:
        """
        Clone a parser under a new name.

        Args:
            src_name: Source parser name
            dst_name: Destination parser name

        Returns:
            True if cloned
        """
        parser = self.get_parser(src_name)

        if not parser:
            return False

        try:
            self.register_parser(dst_name, parser)
            return True

        except ValueError:
            return False
