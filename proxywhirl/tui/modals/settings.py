"""Settings modal dialog for TUI application configuration."""

from __future__ import annotations

from typing import Any, Dict

from textual import on
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Input,
    Label,
    RadioButton,
    RadioSet,
    Static,
    Switch,
)

from ...caches import CacheType
from ...models import RotationStrategy


class SettingsModal(ModalScreen[Dict[str, Any]]):
    """Modal dialog for application settings."""

    def __init__(self, current_settings: Dict[str, Any], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.current_settings = current_settings

    def compose(self):
        with Vertical(classes="settings-modal"):
            yield Static("⚙️  Settings", classes="modal-title")

            with VerticalScroll():
                with Vertical(classes="settings-section"):
                    yield Label("💾 Cache Settings", classes="section-title")
                    with RadioSet(id="cache-type-selector"):
                        yield RadioButton("Memory", id="cache-memory", 
                                        value=self.current_settings.get("cache_type") == CacheType.MEMORY)
                        yield RadioButton("SQLite", id="cache-sqlite",
                                        value=self.current_settings.get("cache_type") == CacheType.SQLITE)
                        yield RadioButton("JSON", id="cache-json",
                                        value=self.current_settings.get("cache_type") == CacheType.JSON)
                    yield Label("Cache Path (optional):")
                    yield Input(
                        value=str(self.current_settings.get("cache_path", "")),
                        placeholder="/path/to/cache",
                        id="cache-path-input",
                        classes="settings-input"
                    )

                with Vertical(classes="settings-section"):
                    yield Label("✅ Validation Settings", classes="section-title")
                    yield Switch(
                        value=self.current_settings.get("auto_validate", True),
                        id="auto-validate-switch"
                    )
                    yield Label("Auto-validate on fetch")
                    yield Label("Timeout (seconds):")
                    yield Input(
                        value=str(self.current_settings.get("validator_timeout", 10.0)),
                        placeholder="10.0",
                        id="timeout-input",
                        classes="settings-input"
                    )

                with Vertical(classes="settings-section"):
                    yield Label("🔄 Rotation Settings", classes="section-title")
                    with RadioSet(id="rotation-selector"):
                        yield RadioButton("Round Robin", id="rotation-round-robin",
                                        value=self.current_settings.get("rotation_strategy") == RotationStrategy.ROUND_ROBIN)
                        yield RadioButton("Random", id="rotation-random",
                                        value=self.current_settings.get("rotation_strategy") == RotationStrategy.RANDOM)
                        yield RadioButton("Least Used", id="rotation-least-used",
                                        value=self.current_settings.get("rotation_strategy") == RotationStrategy.LEAST_USED)

            with Horizontal(classes="settings-buttons"):
                yield Button("Save", variant="primary", id="save-settings")
                yield Button("Cancel", variant="default", id="cancel-settings")

    @on(Button.Pressed, "#save-settings")
    def handle_save(self) -> None:
        """Save settings and return to main app."""
        settings = {}

        # Get cache type
        cache_type_selector = self.query_one("#cache-type-selector", RadioSet)
        for radio in cache_type_selector.query(RadioButton):
            if radio.value:
                if radio.id == "cache-memory":
                    settings["cache_type"] = CacheType.MEMORY
                elif radio.id == "cache-sqlite":
                    settings["cache_type"] = CacheType.SQLITE
                elif radio.id == "cache-json":
                    settings["cache_type"] = CacheType.JSON
                break

        # Get cache path
        cache_path = self.query_one("#cache-path-input", Input).value
        if cache_path.strip():
            settings["cache_path"] = cache_path.strip()

        # Get validation settings
        settings["auto_validate"] = self.query_one("#auto-validate-switch", Switch).value

        timeout_input = self.query_one("#timeout-input", Input).value
        try:
            settings["validator_timeout"] = float(timeout_input)
        except ValueError:
            settings["validator_timeout"] = 10.0

        # Get rotation strategy
        rotation_selector = self.query_one("#rotation-selector", RadioSet)
        for radio in rotation_selector.query(RadioButton):
            if radio.value:
                if radio.id == "rotation-round-robin":
                    settings["rotation_strategy"] = RotationStrategy.ROUND_ROBIN
                elif radio.id == "rotation-random":
                    settings["rotation_strategy"] = RotationStrategy.RANDOM
                elif radio.id == "rotation-least-used":
                    settings["rotation_strategy"] = RotationStrategy.LEAST_USED
                break

        self.dismiss(settings)

    @on(Button.Pressed, "#cancel-settings")
    def handle_cancel(self) -> None:
        self.dismiss({})
        self.dismiss({})
