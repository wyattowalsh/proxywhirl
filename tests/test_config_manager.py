"""Tests for advanced configuration management."""

import asyncio
import json
import os
import tempfile
from pathlib import Path

import pytest

from proxywhirl.config_manager import (
    ConfigurationManager,
    ConfigVersion,
    EnvironmentExpander,
    HotReloadConfig,
)


class TestEnvironmentExpander:
    """Tests for environment variable expansion."""

    def test_simple_env_expansion(self):
        """Test simple environment variable expansion."""
        os.environ["TEST_VAR"] = "test_value"
        result = EnvironmentExpander.expand("prefix_${TEST_VAR}_suffix")
        assert result == "prefix_test_value_suffix"

    def test_missing_env_with_default(self):
        """Test missing env variable with default."""
        # Remove if exists
        os.environ.pop("MISSING_VAR", None)
        result = EnvironmentExpander.expand("value_${MISSING_VAR:default_value}")
        assert result == "value_default_value"

    def test_missing_env_strict_mode(self):
        """Test missing env variable in strict mode raises error."""
        os.environ.pop("NONEXISTENT_VAR", None)
        with pytest.raises(ValueError, match="not found"):
            EnvironmentExpander.expand("${NONEXISTENT_VAR}", strict=True)

    def test_missing_env_non_strict_mode(self):
        """Test missing env variable in non-strict mode returns unexpanded."""
        os.environ.pop("NONEXISTENT_VAR", None)
        result = EnvironmentExpander.expand("${NONEXISTENT_VAR}")
        assert result == "${NONEXISTENT_VAR}"

    def test_multiple_expansions(self):
        """Test multiple env variables in one string."""
        os.environ["VAR1"] = "value1"
        os.environ["VAR2"] = "value2"
        result = EnvironmentExpander.expand("${VAR1}-${VAR2}")
        assert result == "value1-value2"

    def test_expand_dict_nested(self):
        """Test recursive dict expansion."""
        os.environ["DB_HOST"] = "localhost"
        os.environ["DB_PORT"] = "5432"

        data = {
            "database": {
                "host": "${DB_HOST}",
                "port": "${DB_PORT}",
            },
            "simple": "value",
        }

        expanded = EnvironmentExpander.expand_dict(data)

        assert expanded["database"]["host"] == "localhost"
        assert expanded["database"]["port"] == "5432"
        assert expanded["simple"] == "value"

    def test_expand_dict_with_lists(self):
        """Test dict expansion with lists."""
        os.environ["LIST_ITEM"] = "item1"

        data = {"items": ["${LIST_ITEM}", "static"]}
        expanded = EnvironmentExpander.expand_dict(data)

        assert expanded["items"] == ["item1", "static"]


class TestConfigurationManager:
    """Tests for ConfigurationManager."""

    def test_basic_get_set(self):
        """Test basic get/set operations."""
        config = ConfigurationManager({"key": "value"})

        assert config.get("key") == "value"
        config.set("key", "new_value")
        assert config.get("key") == "new_value"

    def test_nested_key_access(self):
        """Test dot notation for nested keys."""
        config = ConfigurationManager(
            {
                "server": {"host": "localhost", "port": 8000},
            }
        )

        assert config.get("server.host") == "localhost"
        assert config.get("server.port") == 8000

    def test_default_value(self):
        """Test default value when key not found."""
        config = ConfigurationManager({})

        assert config.get("missing", "default") == "default"
        assert config.get("missing") is None

    def test_set_nested_key_creates_path(self):
        """Test setting nested key creates intermediate dicts."""
        config = ConfigurationManager({})

        config.set("a.b.c", "value")

        assert config.get("a.b.c") == "value"

    def test_subscriber_notification(self):
        """Test subscribers are notified of changes."""
        config = ConfigurationManager({"key": "value"})
        calls = []

        def handler(data):
            calls.append(data)

        config.subscribe(handler)
        config.set("key", "new_value")

        assert len(calls) == 1
        assert calls[0]["key"] == "new_value"

    def test_unsubscribe(self):
        """Test unsubscribe removes handler."""
        config = ConfigurationManager({"key": "value"})
        calls = []

        def handler(data):
            calls.append(data)

        unsubscribe = config.subscribe(handler)
        config.set("key", "new_value")

        assert len(calls) == 1

        unsubscribe()
        config.set("key", "another_value")

        assert len(calls) == 1

    def test_environment_expansion_on_init(self):
        """Test environment variables expanded on initialization."""
        os.environ["INIT_VAR"] = "init_value"
        config = ConfigurationManager({"key": "${INIT_VAR}"})

        assert config.get("key") == "init_value"

    def test_to_dict(self):
        """Test to_dict export."""
        data = {"key": "value", "nested": {"key": "value2"}}
        config = ConfigurationManager(data)

        exported = config.to_dict()

        assert exported == data

    def test_to_json(self):
        """Test to_json export."""
        data = {"key": "value"}
        config = ConfigurationManager(data)

        json_str = config.to_json()
        parsed = json.loads(json_str)

        assert parsed == data

    def test_version_tracking(self):
        """Test version tracking."""
        config = ConfigurationManager({"key": "value"})
        v1 = config.get_version()

        assert v1.version == "1.0.0"
        assert v1.change_id

        config.set("key", "new_value")
        v2 = config.get_version()

        assert v2.change_id != v1.change_id

    def test_json_schema_generation(self):
        """Test JSON schema generation."""
        config = ConfigurationManager(
            {
                "string_key": "value",
                "int_key": 42,
                "bool_key": True,
                "list_key": [1, 2, 3],
                "nested": {"key": "value"},
            }
        )

        schema = config.generate_json_schema()

        assert schema["type"] == "object"
        assert "string_key" in schema["properties"]
        assert "int_key" in schema["properties"]
        assert "bool_key" in schema["properties"]
        assert "list_key" in schema["properties"]
        assert "nested" in schema["properties"]

        # Verify type inference
        assert schema["properties"]["string_key"]["type"] == "string"
        assert schema["properties"]["int_key"]["type"] == "integer"
        assert schema["properties"]["bool_key"]["type"] == "boolean"
        assert schema["properties"]["list_key"]["type"] == "array"
        assert schema["properties"]["nested"]["type"] == "object"

    @pytest.mark.asyncio
    async def test_hot_reload_disabled_by_default(self):
        """Test hot-reload is disabled by default."""
        config = ConfigurationManager({})
        await config.start_hot_reload("/path/to/config.json")

        assert config._watcher_task is None

    @pytest.mark.asyncio
    async def test_hot_reload_file_change(self):
        """Test hot-reload on file change."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"

            # Initial config
            config_data = {"key": "value"}
            config_path.write_text(json.dumps(config_data))

            config = ConfigurationManager(
                config_data,
                hot_reload_config=HotReloadConfig(enabled=True, reload_delay_seconds=0.1),
            )

            notified = []

            def handler(data):
                notified.append(data)

            config.subscribe(handler)

            # Start hot reload
            await config.start_hot_reload(str(config_path))

            # Modify file
            await asyncio.sleep(0.2)
            new_data = {"key": "new_value", "extra": "data"}
            config_path.write_text(json.dumps(new_data))

            # Wait for reload
            await asyncio.sleep(0.5)

            # Verify config was reloaded
            assert config.get("key") == "new_value"
            assert config.get("extra") == "data"

            # Verify subscriber was notified
            assert len(notified) > 0

            # Cleanup
            if config._watcher_task:
                config._watcher_task.cancel()
                try:
                    await config._watcher_task
                except asyncio.CancelledError:
                    pass

    @pytest.mark.asyncio
    async def test_hot_reload_validation_enabled(self):
        """Test hot-reload validates config before applying."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"

            config_data = {"key": "value"}
            config_path.write_text(json.dumps(config_data))

            config = ConfigurationManager(
                config_data,
                hot_reload_config=HotReloadConfig(
                    enabled=True,
                    reload_delay_seconds=0.1,
                    validate_before_reload=True,
                ),
            )

            await config.start_hot_reload(str(config_path))

            # Modify file with valid JSON
            await asyncio.sleep(0.2)
            new_data = {"key": "new_value"}
            config_path.write_text(json.dumps(new_data))

            await asyncio.sleep(0.5)

            assert config.get("key") == "new_value"

            # Cleanup
            if config._watcher_task:
                config._watcher_task.cancel()
                try:
                    await config._watcher_task
                except asyncio.CancelledError:
                    pass

    def test_hot_reload_config_model(self):
        """Test HotReloadConfig model."""
        config = HotReloadConfig(
            enabled=True,
            watch_path="/path/to/config.json",
            reload_delay_seconds=2.0,
            validate_before_reload=False,
        )

        assert config.enabled
        assert config.watch_path == "/path/to/config.json"
        assert config.reload_delay_seconds == 2.0
        assert not config.validate_before_reload

    def test_config_version_model(self):
        """Test ConfigVersion model."""
        version = ConfigVersion(version="1.2.3")

        assert version.version == "1.2.3"
        assert version.change_id
        assert version.timestamp


class TestIntegration:
    """Integration tests for configuration management."""

    def test_env_expansion_with_defaults_in_config(self):
        """Test env expansion with defaults in complex config."""
        os.environ["CACHE_SIZE"] = "1000"

        config = ConfigurationManager(
            {
                "cache": {
                    "size": "${CACHE_SIZE}",
                    "ttl": "${CACHE_TTL:3600}",
                },
                "database": {
                    "host": "${DB_HOST:localhost}",
                },
            }
        )

        assert config.get("cache.size") == "1000"
        assert config.get("cache.ttl") == "3600"
        assert config.get("database.host") == "localhost"

    def test_complex_workflow(self):
        """Test complex workflow with get/set/expand."""
        os.environ["ENV_VAR"] = "env_value"

        config = ConfigurationManager(
            {
                "app": {
                    "name": "myapp",
                    "version": "1.0.0",
                    "settings": {"timeout": "${TIMEOUT:30}"},
                }
            }
        )

        # Verify initial state
        assert config.get("app.name") == "myapp"
        assert config.get("app.settings.timeout") == "30"

        # Update
        config.set("app.settings.timeout", "60")
        assert config.get("app.settings.timeout") == "60"

        # Schema generation
        schema = config.generate_json_schema()
        assert schema["type"] == "object"
        assert "app" in schema["properties"]
