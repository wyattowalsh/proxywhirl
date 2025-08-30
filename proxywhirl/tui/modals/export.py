"""Export modal dialog for proxy export configuration."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, List

from textual import on
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Checkbox,
    Collapsible,
    Input,
    Label,
    RadioButton,
    RadioSet,
    Rule,
    Static,
)

from ...exporter import ExportConfig, ExportFormat, ProxyExporter, ProxyExportError
from ...logger import get_logger
from ...models import Proxy

logger = get_logger(__name__)


class ExportModal(ModalScreen[bool]):
    """Enhanced modal dialog for configuring proxy export with rich UI."""

    def __init__(self, proxies: List[Proxy], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.proxies = proxies

    def compose(self):
        with Vertical(classes="export-modal"):
            yield Static("📤 Export Proxies", classes="modal-title")
            yield Rule()

            with Horizontal(classes="export-options"):
                with Vertical(classes="format-section"):
                    yield Label("📋 Export Format", classes="section-title")
                    with RadioSet(id="format-selector"):
                        yield RadioButton("JSON", id="json-format", value=True)
                        yield RadioButton("CSV", id="csv-format")
                        yield RadioButton("TXT", id="txt-format")
                        yield RadioButton("XML", id="xml-format")

                with Vertical(classes="filter-section"):
                    yield Label("🎯 Filters", classes="section-title")
                    yield Checkbox("Active proxies only", id="active-only", classes="export-checkbox")
                    yield Checkbox("Include metadata", id="include-metadata", classes="export-checkbox")
                    yield Label("📊 Limit (optional):")
                    yield Input(placeholder="e.g. 100", id="export-limit", classes="export-input")

            yield Rule()

            # Export preview
            with Collapsible(collapsed=False):
                yield Label("📋 Export Preview")
                yield Static(f"Ready to export {len(self.proxies)} proxies", id="export-preview")

            with Horizontal(classes="export-buttons"):
                yield Button(
                    "📤 Export", variant="primary", id="export-btn", classes="export-action-btn"
                )
                yield Button(
                    "❌ Cancel", variant="default", id="cancel-btn", classes="export-action-btn"
                )

    @on(RadioSet.Changed, "#format-selector")
    def on_format_changed(self, event: RadioSet.Changed) -> None:
        """Update preview when format changes."""
        self.update_preview()

    @on(Checkbox.Changed)
    def on_filter_changed(self, event: Checkbox.Changed) -> None:
        """Update preview when filters change."""
        self.update_preview()

    @on(Input.Changed, "#export-limit")
    def on_limit_changed(self, event: Input.Changed) -> None:
        """Update preview when limit changes."""
        self.update_preview()

    def update_preview(self) -> None:
        """Update the export preview text."""
        preview = self.query_one("#export-preview", Static)

        # Calculate filtered proxy count
        active_only = self.query_one("#active-only", Checkbox).value
        limit_input = self.query_one("#export-limit", Input)

        filtered_count = len(self.proxies)
        if active_only:
            filtered_count = sum(
                1 for p in self.proxies if getattr(p, "status", "unknown") == "active"
            )

        if limit_input.value.strip():
            try:
                limit = int(limit_input.value.strip())
                filtered_count = min(filtered_count, limit)
            except ValueError:
                pass

        # Get selected format
        format_name = "JSON"
        format_selector = self.query_one("#format-selector", RadioSet)
        for radio in format_selector.query(RadioButton):
            if radio.value:
                if radio.id == "csv-format":
                    format_name = "CSV"
                elif radio.id == "txt-format":
                    format_name = "TXT"
                elif radio.id == "xml-format":
                    format_name = "XML"
                break

        preview.update(
            f"Will export [bold green]{filtered_count}[/bold green] proxies in [bold blue]{format_name}[/bold blue] format"
        )

    @on(Button.Pressed, "#export-btn")
    async def handle_export(self) -> None:
        """Handle export button press with enhanced error handling."""
        format_selector = self.query_one("#format-selector", RadioSet)
        limit_input = self.query_one("#export-limit", Input)
        export_btn = self.query_one("#export-btn", Button)

        # Get selected format
        selected_format = ExportFormat.JSON  # Default
        for radio in format_selector.query(RadioButton):
            if radio.value:
                if radio.id == "csv-format":
                    selected_format = ExportFormat.CSV
                elif radio.id == "txt-format":
                    selected_format = ExportFormat.TXT_HOSTPORT
                elif radio.id == "xml-format":
                    selected_format = ExportFormat.XML
                break

        # Configure export with enhanced options
        include_metadata = self.query_one("#include-metadata", Checkbox).value
        export_config = ExportConfig(
            format=selected_format,
            include_metadata=include_metadata,
            metadata_format="inline" if include_metadata else "none",
            output_file=None,
            overwrite=True,
        )

        # Apply filters
        proxies_to_export = self.proxies

        # Filter active only
        if self.query_one("#active-only", Checkbox).value:
            proxies_to_export = [
                p for p in proxies_to_export if getattr(p, "status", "unknown") == "active"
            ]

        # Apply limit
        if limit_input.value.strip():
            try:
                limit = int(limit_input.value.strip())
                proxies_to_export = proxies_to_export[:limit]
            except ValueError:
                pass

        try:
            # Show loading state
            export_btn.label = "⏳ Exporting..."
            export_btn.disabled = True

            exporter = ProxyExporter()
            result = exporter.export(proxies_to_export, export_config)

            # Generate filename with timestamp and format
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            extension = selected_format.value.lower()
            filename = f"proxywhirl_export_{timestamp}.{extension}"

            Path(filename).write_text(result, encoding="utf-8")

            self.dismiss(True)

        except ProxyExportError as export_error:
            # Reset button state
            export_btn.label = "📤 Export"
            export_btn.disabled = False

            # Log the specific export error
            logger.error("Export error: %s", export_error)
            # Show error (could be enhanced with error dialog)
            self.dismiss(False)
        except Exception as general_error:
            # Reset button state
            export_btn.label = "📤 Export"
            export_btn.disabled = False
            logger.exception("Unexpected export error: %s", general_error)
            self.dismiss(False)

    @on(Button.Pressed, "#cancel-btn")
    def handle_cancel(self) -> None:
        self.dismiss(False)
        self.dismiss(False)
