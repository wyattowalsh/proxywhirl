"""Predefined pool templates for common configurations.

Provides ready-to-use templates for different proxy usage scenarios,
reducing configuration boilerplate for common setups.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from loguru import logger

from proxywhirl.models import ProxyConfiguration


@dataclass
class PoolTemplate:
    """Template configuration for common pool setups."""

    name: str
    description: str
    config: ProxyConfiguration
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert template to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "config": (
                self.config.model_dump() if hasattr(self.config, "model_dump") else str(self.config)
            ),
            "tags": self.tags,
        }


class TemplateLibrary:
    """Library of predefined pool templates."""

    _templates: dict[str, PoolTemplate] = {}

    @classmethod
    def register_template(cls, template: PoolTemplate) -> None:
        """Register a template in the library.

        Args:
            template: PoolTemplate to register
        """
        cls._templates[template.name] = template
        logger.debug(f"Registered pool template: {template.name}")

    @classmethod
    def get_template(cls, name: str) -> PoolTemplate | None:
        """Get a template by name.

        Args:
            name: Template name

        Returns:
            PoolTemplate if found, None otherwise
        """
        return cls._templates.get(name)

    @classmethod
    def list_templates(cls) -> list[str]:
        """List all available template names."""
        return list(cls._templates.keys())

    @classmethod
    def list_templates_by_tag(cls, tag: str) -> list[str]:
        """List template names by tag.

        Args:
            tag: Tag to filter by

        Returns:
            List of matching template names
        """
        return [name for name, tpl in cls._templates.items() if tag in tpl.tags]

    @classmethod
    def get_template_info(cls, name: str) -> dict[str, Any] | None:
        """Get template information.

        Args:
            name: Template name

        Returns:
            Template info dict or None if not found
        """
        template = cls.get_template(name)
        return template.to_dict() if template else None

    @classmethod
    def initialize_defaults(cls) -> None:
        """Register default templates."""
        # Fast rotation template
        cls.register_template(
            PoolTemplate(
                name="fast-rotation",
                description="Optimized for fast rotation with low latency",
                config=ProxyConfiguration(
                    timeout=5,
                    health_check_interval_seconds=30,
                ),
                tags=["performance", "rotation"],
            )
        )

        # Reliable rotation template
        cls.register_template(
            PoolTemplate(
                name="reliable-rotation",
                description="Prioritizes reliability and error handling",
                config=ProxyConfiguration(
                    timeout=10,
                    max_retries=3,
                    health_check_interval_seconds=60,
                ),
                tags=["reliability", "production"],
            )
        )

        # Geolocation template
        cls.register_template(
            PoolTemplate(
                name="geo-targeted",
                description="Optimized for geo-targeted requests",
                config=ProxyConfiguration(
                    timeout=8,
                    health_check_interval_seconds=120,
                ),
                tags=["geo", "location-based"],
            )
        )

        # Performance template
        cls.register_template(
            PoolTemplate(
                name="performance",
                description="Maximizes performance metrics",
                config=ProxyConfiguration(
                    timeout=3,
                    health_check_interval_seconds=45,
                ),
                tags=["performance", "metrics"],
            )
        )

        # Development template
        cls.register_template(
            PoolTemplate(
                name="dev-testing",
                description="For development and testing",
                config=ProxyConfiguration(timeout=15),
                tags=["development", "testing"],
            )
        )

        # High-availability template
        cls.register_template(
            PoolTemplate(
                name="high-availability",
                description="Multi-region HA configuration",
                config=ProxyConfiguration(
                    timeout=10,
                    max_retries=5,
                    health_check_interval_seconds=20,
                ),
                tags=["ha", "failover", "production"],
            )
        )

        # Rate-limited template
        cls.register_template(
            PoolTemplate(
                name="rate-limited",
                description="For rate-limited target APIs",
                config=ProxyConfiguration(
                    timeout=20,
                    health_check_interval_seconds=60,
                ),
                tags=["rate-limiting", "api"],
            )
        )

        logger.info(f"Initialized {len(cls._templates)} default pool templates")


# Initialize templates on module load
TemplateLibrary.initialize_defaults()
