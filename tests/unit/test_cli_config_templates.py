"""Tests for CLI config templates."""

import pytest

from proxywhirl.cli_config_templates import ConfigTemplate, ConfigTemplateManager


class TestConfigTemplateManager:
    """Test config templates."""

    def test_get_template(self):
        """Test getting a template."""
        manager = ConfigTemplateManager()
        template = manager.get_template(ConfigTemplate.STANDARD)
        assert template is not None
        assert "pool" in template.config

    def test_list_templates(self):
        """Test listing templates."""
        manager = ConfigTemplateManager()
        templates = manager.list_templates()
        assert len(templates) == 5

    def test_merge_template(self):
        """Test merging template with custom config."""
        manager = ConfigTemplateManager()
        merged = manager.merge_template(ConfigTemplate.STANDARD, {"pool": {"max_size": 200}})
        assert merged["pool"]["max_size"] == 200
        assert "rotation" in merged
