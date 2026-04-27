"""Configuration templates for the CLI.

Provides predefined config templates for different use cases.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ConfigTemplate(str, Enum):
    """Available configuration templates."""

    MINIMAL = "minimal"
    STANDARD = "standard"
    ADVANCED = "advanced"
    PERFORMANCE = "performance"
    SECURITY = "security"


@dataclass
class TemplateConfig:
    """Template configuration definition."""

    name: str
    description: str
    config: dict[str, Any]


class ConfigTemplateManager:
    """Manager for configuration templates.

    Provides predefined templates for different use cases.

    Example:
        >>> manager = ConfigTemplateManager()
        >>> config = manager.get_template(ConfigTemplate.STANDARD)
    """

    def __init__(self) -> None:
        """Initialize template manager."""
        self.templates = self._init_templates()

    def _init_templates(self) -> dict[ConfigTemplate, TemplateConfig]:
        """Initialize all templates.

        Returns:
            Dict of available templates
        """
        return {
            ConfigTemplate.MINIMAL: TemplateConfig(
                name="Minimal",
                description="Minimal configuration for basic proxy rotation",
                config={
                    "pool": {
                        "max_size": 10,
                        "validation": {"enabled": False},
                    },
                    "rotation": {"strategy": "round_robin"},
                    "retry": {"enabled": False},
                },
            ),
            ConfigTemplate.STANDARD: TemplateConfig(
                name="Standard",
                description="Standard configuration with validation and retry",
                config={
                    "pool": {
                        "max_size": 100,
                        "validation": {
                            "enabled": True,
                            "timeout": 10,
                            "max_concurrent": 50,
                        },
                    },
                    "rotation": {"strategy": "weighted"},
                    "retry": {
                        "enabled": True,
                        "max_attempts": 3,
                        "backoff_factor": 1.5,
                    },
                    "cache": {"enabled": True, "ttl_seconds": 3600},
                },
            ),
            ConfigTemplate.ADVANCED: TemplateConfig(
                name="Advanced",
                description="Advanced configuration with circuit breaker and rate limiting",
                config={
                    "pool": {
                        "max_size": 500,
                        "validation": {
                            "enabled": True,
                            "timeout": 15,
                            "max_concurrent": 100,
                        },
                    },
                    "rotation": {"strategy": "performance_based"},
                    "circuit_breaker": {
                        "enabled": True,
                        "failure_threshold": 5,
                        "timeout_duration": 30,
                    },
                    "rate_limiting": {
                        "enabled": True,
                        "requests_per_minute": 1000,
                    },
                    "retry": {
                        "enabled": True,
                        "max_attempts": 5,
                        "backoff_factor": 2.0,
                    },
                    "cache": {
                        "enabled": True,
                        "ttl_seconds": 7200,
                        "max_entries": 10000,
                    },
                },
            ),
            ConfigTemplate.PERFORMANCE: TemplateConfig(
                name="Performance",
                description="Configuration optimized for high throughput",
                config={
                    "pool": {
                        "max_size": 1000,
                        "validation": {
                            "enabled": True,
                            "timeout": 5,
                            "max_concurrent": 200,
                        },
                    },
                    "rotation": {"strategy": "hash_based"},
                    "cache": {
                        "enabled": True,
                        "ttl_seconds": 1800,
                        "max_entries": 50000,
                    },
                    "retry": {
                        "enabled": True,
                        "max_attempts": 2,
                        "backoff_factor": 1.0,
                    },
                },
            ),
            ConfigTemplate.SECURITY: TemplateConfig(
                name="Security",
                description="Configuration emphasizing security and reliability",
                config={
                    "pool": {
                        "max_size": 200,
                        "validation": {
                            "enabled": True,
                            "timeout": 20,
                            "max_concurrent": 25,
                        },
                    },
                    "rotation": {"strategy": "performance_based"},
                    "circuit_breaker": {
                        "enabled": True,
                        "failure_threshold": 3,
                        "timeout_duration": 60,
                    },
                    "rate_limiting": {
                        "enabled": True,
                        "requests_per_minute": 500,
                    },
                    "retry": {
                        "enabled": True,
                        "max_attempts": 4,
                        "backoff_factor": 2.5,
                    },
                },
            ),
        }

    def get_template(self, template_type: ConfigTemplate) -> TemplateConfig:
        """Get a configuration template.

        Args:
            template_type: Template type

        Returns:
            TemplateConfig instance
        """
        if template_type not in self.templates:
            raise ValueError(f"Unknown template: {template_type}")
        return self.templates[template_type]

    def list_templates(self) -> list[dict[str, str]]:
        """List all available templates.

        Returns:
            List of template info dicts
        """
        return [
            {
                "name": template.name,
                "type": template.name.lower(),
                "description": template.description,
            }
            for template in self.templates.values()
        ]

    def merge_template(
        self,
        template_type: ConfigTemplate,
        custom_config: dict[str, Any],
    ) -> dict[str, Any]:
        """Merge template with custom config.

        Args:
            template_type: Template type
            custom_config: Custom configuration overrides

        Returns:
            Merged configuration
        """
        template = self.get_template(template_type)
        config = template.config.copy()

        def deep_merge(
            base: dict[str, Any],
            override: dict[str, Any],
        ) -> dict[str, Any]:
            """Recursively merge dicts.

            Args:
                base: Base config
                override: Override config

            Returns:
                Merged config
            """
            result = base.copy()
            for key, value in override.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result

        return deep_merge(config, custom_config)
