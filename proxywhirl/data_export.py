"""Data export and serialization utilities."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from io import StringIO
from pathlib import Path
from typing import Any

from loguru import logger

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class ExportFormat(str, Enum):
    """Export format options."""

    JSON = "json"
    CSV = "csv"
    TSV = "tsv"
    PLAIN_TEXT = "text"
    HTML = "html"
    XML = "xml"
    YAML = "yaml"


class DataExporter:
    """Exports data in various formats."""

    @staticmethod
    def to_json(data: Any, indent: int = 2, default: callable | None = None) -> str:
        """Export to JSON.

        Args:
            data: Data to export
            indent: JSON indent level
            default: Custom serializer

        Returns:
            JSON string
        """

        def default_handler(obj: Any) -> Any:
            if is_dataclass(obj):
                return asdict(obj)
            if isinstance(obj, Enum):
                return obj.value
            if hasattr(obj, "__dict__"):
                return obj.__dict__
            if default:
                return default(obj)
            return str(obj)

        return json.dumps(data, indent=indent, default=default_handler)

    @staticmethod
    def to_csv(
        data: list[dict[str, Any]],
        fieldnames: list[str] | None = None,
    ) -> str:
        """Export to CSV.

        Args:
            data: List of dicts
            fieldnames: Field names (auto-detected if None)

        Returns:
            CSV string
        """
        if not data:
            return ""

        if fieldnames is None:
            fieldnames = list(data[0].keys())

        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)

        writer.writeheader()
        for row in data:
            writer.writerow({field: row.get(field, "") for field in fieldnames})

        return output.getvalue()

    @staticmethod
    def to_tsv(
        data: list[dict[str, Any]],
        fieldnames: list[str] | None = None,
    ) -> str:
        """Export to TSV.

        Args:
            data: List of dicts
            fieldnames: Field names

        Returns:
            TSV string
        """
        if not data:
            return ""

        if fieldnames is None:
            fieldnames = list(data[0].keys())

        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=fieldnames,
            delimiter="\t",
        )

        writer.writeheader()
        for row in data:
            writer.writerow({field: row.get(field, "") for field in fieldnames})

        return output.getvalue()

    @staticmethod
    def to_text(data: Any, separator: str = "-" * 80) -> str:
        """Export to plain text.

        Args:
            data: Data to export
            separator: Line separator

        Returns:
            Text string
        """
        if isinstance(data, list):
            lines = [str(item) for item in data]
            return f"\n{separator}\n".join(lines)

        return str(data)

    @staticmethod
    def to_html(data: list[dict[str, Any]]) -> str:
        """Export to HTML table.

        Args:
            data: List of dicts

        Returns:
            HTML string
        """
        if not data:
            return "<table></table>"

        fieldnames = list(data[0].keys())

        html_lines = ["<table border='1'>", "<thead>", "<tr>"]

        for field in fieldnames:
            html_lines.append(f"<th>{field}</th>")

        html_lines.extend(["</tr>", "</thead>", "<tbody>"])

        for row in data:
            html_lines.append("<tr>")
            for field in fieldnames:
                value = row.get(field, "")
                html_lines.append(f"<td>{value}</td>")
            html_lines.append("</tr>")

        html_lines.extend(["</tbody>", "</table>"])

        return "\n".join(html_lines)

    @staticmethod
    def to_xml(data: Any, root_tag: str = "root") -> str:
        """Export to XML (simplified).

        Args:
            data: Data to export
            root_tag: Root element tag

        Returns:
            XML string
        """
        lines = ["<?xml version='1.0'?>", f"<{root_tag}>"]

        if isinstance(data, list):
            for item in data:
                lines.append("<item>")
                if isinstance(item, dict):
                    for key, value in item.items():
                        lines.append(f"<{key}>{value}</{key}>")
                else:
                    lines.append(str(item))
                lines.append("</item>")
        else:
            lines.append(str(data))

        lines.append(f"</{root_tag}>")

        return "\n".join(lines)

    @staticmethod
    def to_yaml(data: Any, default_flow_style: bool = False) -> str:
        """Export to YAML.

        Args:
            data: Data to export
            default_flow_style: Use flow style for collections

        Returns:
            YAML string

        Raises:
            ImportError: If PyYAML not installed
        """
        if not HAS_YAML:
            raise ImportError(
                "PyYAML is required for YAML export. Install with: pip install pyyaml"
            )

        def default_handler(obj: Any) -> Any:
            if is_dataclass(obj):
                return asdict(obj)
            if isinstance(obj, Enum):
                return obj.value
            if hasattr(obj, "__dict__"):
                return obj.__dict__
            return str(obj)

        class CustomEncoder(yaml.SafeDumper):
            pass

        CustomEncoder.add_representer(
            type(None), lambda dumper, _: dumper.represent_scalar("tag:yaml.org,2002:null", "")
        )

        return yaml.dump(
            data, Dumper=CustomEncoder, default_flow_style=default_flow_style, allow_unicode=True
        )


class FileExporter:
    """Exports data to files."""

    def __init__(self, output_dir: Path | str = "."):
        """Initialize exporter.

        Args:
            output_dir: Output directory
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(
        self,
        data: Any,
        filename: str,
        format: ExportFormat = ExportFormat.JSON,
    ) -> Path:
        """Export data to file.

        Args:
            data: Data to export
            filename: Output filename
            format: Export format

        Returns:
            File path
        """
        file_path = self.output_dir / filename

        try:
            if format == ExportFormat.JSON:
                content = DataExporter.to_json(data)
            elif format == ExportFormat.CSV:
                content = DataExporter.to_csv(data)
            elif format == ExportFormat.TSV:
                content = DataExporter.to_tsv(data)
            elif format == ExportFormat.PLAIN_TEXT:
                content = DataExporter.to_text(data)
            elif format == ExportFormat.HTML:
                content = DataExporter.to_html(data)
            elif format == ExportFormat.XML:
                content = DataExporter.to_xml(data)
            elif format == ExportFormat.YAML:
                content = DataExporter.to_yaml(data)
            else:
                raise ValueError(f"Unsupported format: {format}")

            file_path.write_text(content)
            logger.info(f"Exported data to {file_path}")

            return file_path
        except Exception as e:
            logger.error(f"Export failed: {e}")
            raise

    def export_multiple(
        self,
        exports: dict[str, tuple[Any, ExportFormat]],
    ) -> list[Path]:
        """Export multiple files.

        Args:
            exports: Dict of filename -> (data, format)

        Returns:
            List of file paths
        """
        paths = []

        for filename, (data, format) in exports.items():
            path = self.export(data, filename, format)
            paths.append(path)

        return paths
