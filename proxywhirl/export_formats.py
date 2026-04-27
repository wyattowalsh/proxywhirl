"""Multiple export format support for proxy data."""

import csv
import io
import json
from enum import Enum
from pathlib import Path
from typing import List, Optional

try:
    import yaml
except ImportError:
    yaml = None

from proxywhirl.models import Proxy


class ExportFormat(str, Enum):
    """Supported export formats."""

    JSON = "json"
    CSV = "csv"
    YAML = "yaml"
    JSONL = "jsonl"
    TSV = "tsv"


class MultiFormatExporter:
    """Export proxies in multiple formats."""

    def __init__(self):
        self.formats = {
            ExportFormat.JSON: self._export_json,
            ExportFormat.CSV: self._export_csv,
            ExportFormat.YAML: self._export_yaml,
            ExportFormat.JSONL: self._export_jsonl,
            ExportFormat.TSV: self._export_tsv,
        }

    def export(
        self, proxies: List[Proxy], format: ExportFormat, output_path: Optional[str] = None
    ) -> str:
        """Export proxies to specified format."""
        exporter = self.formats.get(format)
        if not exporter:
            raise ValueError(f"Unsupported format: {format}")

        content = exporter(proxies)

        if output_path:
            Path(output_path).write_text(content)

        return content

    def _export_json(self, proxies: List[Proxy]) -> str:
        """Export as JSON."""
        data = [
            {
                "url": p.url,
                "protocol": p.protocol,
                "country": p.country,
                "is_residential": p.is_residential,
                "port": p.port if hasattr(p, "port") else None,
                "ip": p.ip if hasattr(p, "ip") else None,
            }
            for p in proxies
        ]
        return json.dumps(data, indent=2)

    def _export_csv(self, proxies: List[Proxy]) -> str:
        """Export as CSV."""
        output = io.StringIO()
        writer = csv.DictWriter(
            output, fieldnames=["url", "protocol", "country", "is_residential", "port"]
        )
        writer.writeheader()

        for p in proxies:
            writer.writerow(
                {
                    "url": p.url,
                    "protocol": p.protocol,
                    "country": p.country,
                    "is_residential": p.is_residential,
                    "port": p.port if hasattr(p, "port") else None,
                }
            )

        return output.getvalue()

    def _export_yaml(self, proxies: List[Proxy]) -> str:
        """Export as YAML."""
        if not yaml:
            raise ImportError("PyYAML not installed. Install with: pip install pyyaml")

        data = [
            {
                "url": p.url,
                "protocol": p.protocol,
                "country": p.country,
                "is_residential": p.is_residential,
            }
            for p in proxies
        ]
        return yaml.dump(data, default_flow_style=False)

    def _export_jsonl(self, proxies: List[Proxy]) -> str:
        """Export as JSONL (JSON Lines)."""
        lines = [
            json.dumps(
                {
                    "url": p.url,
                    "protocol": p.protocol,
                    "country": p.country,
                    "is_residential": p.is_residential,
                }
            )
            for p in proxies
        ]
        return "\n".join(lines)

    def _export_tsv(self, proxies: List[Proxy]) -> str:
        """Export as TSV."""
        output = io.StringIO()
        writer = csv.DictWriter(
            output, fieldnames=["url", "protocol", "country", "is_residential"], delimiter="\t"
        )
        writer.writeheader()

        for p in proxies:
            writer.writerow(
                {
                    "url": p.url,
                    "protocol": p.protocol,
                    "country": p.country,
                    "is_residential": p.is_residential,
                }
            )

        return output.getvalue()
