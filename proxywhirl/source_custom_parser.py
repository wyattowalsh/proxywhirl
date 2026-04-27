"""Custom proxy source parser system for ProxyWhirl.

Allows users to define custom parsers for proprietary
proxy source formats and data structures.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from loguru import logger


@dataclass
class ParserConfig:
    """Configuration for a custom parser."""

    name: str
    format_type: str
    description: str = ""
    metadata: dict[str, Any] = None

    def __post_init__(self) -> None:
        """Initialize metadata."""
        if self.metadata is None:
            self.metadata = {}


class CustomProxyParser(ABC):
    """Base class for custom proxy parsers."""

    def __init__(self, config: ParserConfig) -> None:
        """Initialize parser.

        Args:
            config: Parser configuration
        """
        self.config = config
        logger.debug(f"Parser initialized: {config.name}")

    @abstractmethod
    def parse(self, raw_data: str) -> list[dict[str, Any]]:
        """Parse raw data into proxy dictionaries.

        Args:
            raw_data: Raw proxy data

        Returns:
            List of parsed proxy dictionaries
        """
        pass

    @abstractmethod
    def validate(self) -> bool:
        """Validate parser implementation.

        Returns:
            True if valid
        """
        pass

    def parse_with_fallback(
        self, raw_data: str, fallback_parser: CustomProxyParser | None = None
    ) -> list[dict[str, Any]]:
        """Parse with fallback parser.

        Args:
            raw_data: Raw proxy data
            fallback_parser: Fallback parser to use on error

        Returns:
            List of parsed proxies
        """
        try:
            return self.parse(raw_data)
        except Exception as e:
            logger.error(f"Parser failed: {self.config.name} - {e}")
            if fallback_parser:
                return fallback_parser.parse(raw_data)
            return []


class JSONProxyParser(CustomProxyParser):
    """Parser for JSON-formatted proxy data."""

    def parse(self, raw_data: str) -> list[dict[str, Any]]:
        """Parse JSON proxy data.

        Args:
            raw_data: JSON string

        Returns:
            List of proxy dictionaries
        """
        import json

        data = json.loads(raw_data)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
        return []

    def validate(self) -> bool:
        """Validate JSON parser."""
        return True


class CSVProxyParser(CustomProxyParser):
    """Parser for CSV-formatted proxy data."""

    def parse(self, raw_data: str) -> list[dict[str, Any]]:
        """Parse CSV proxy data.

        Args:
            raw_data: CSV string

        Returns:
            List of proxy dictionaries
        """
        import csv
        from io import StringIO

        proxies = []
        reader = csv.DictReader(StringIO(raw_data))
        for row in reader:
            if row:
                proxies.append(dict(row))
        return proxies

    def validate(self) -> bool:
        """Validate CSV parser."""
        return True


class CustomParserRegistry:
    """Registry for custom proxy parsers."""

    def __init__(self) -> None:
        """Initialize parser registry."""
        self._parsers: dict[str, CustomProxyParser] = {}
        logger.debug("CustomParserRegistry initialized")

    def register_parser(self, parser: CustomProxyParser) -> bool:
        """Register a custom parser.

        Args:
            parser: Parser instance

        Returns:
            True if registered
        """
        if not parser.validate():
            logger.error(f"Parser validation failed: {parser.config.name}")
            return False

        if parser.config.name in self._parsers:
            logger.warning(f"Parser already registered: {parser.config.name}")
            return False

        self._parsers[parser.config.name] = parser
        logger.info(f"Custom parser registered: {parser.config.name}")
        return True

    def get_parser(self, name: str) -> CustomProxyParser | None:
        """Get a parser by name.

        Args:
            name: Parser name

        Returns:
            Parser instance or None
        """
        return self._parsers.get(name)

    def parse(self, parser_name: str, raw_data: str) -> list[dict[str, Any]]:
        """Parse data using registered parser.

        Args:
            parser_name: Name of parser to use
            raw_data: Raw data to parse

        Returns:
            List of parsed proxy dictionaries
        """
        parser = self.get_parser(parser_name)
        if not parser:
            logger.error(f"Parser not found: {parser_name}")
            return []

        try:
            return parser.parse(raw_data)
        except Exception as e:
            logger.error(f"Parse error: {parser_name} - {e}")
            return []

    def get_all_parsers(self) -> dict[str, str]:
        """Get all registered parsers.

        Returns:
            Dictionary mapping parser names to format types
        """
        return {name: parser.config.format_type for name, parser in self._parsers.items()}

    def export_metadata(self) -> dict[str, Any]:
        """Export parser metadata.

        Returns:
            Dictionary of parser metadata
        """
        return {
            name: {
                "name": parser.config.name,
                "format_type": parser.config.format_type,
                "description": parser.config.description,
            }
            for name, parser in self._parsers.items()
        }
