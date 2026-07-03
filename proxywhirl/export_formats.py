"""Multiple export format support for proxy data."""

from __future__ import annotations

import csv
import io
import json
from enum import Enum
from pathlib import Path
from urllib.parse import urlparse

try:
    import yaml
except ImportError:
    yaml = None

from proxywhirl.models import Proxy
from proxywhirl.utils import public_proxy_url


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
        self, proxies: list[Proxy], format: ExportFormat, output_path: str | None = None
    ) -> str:
        """Export proxies to specified format."""
        exporter = self.formats.get(format)
        if not exporter:
            raise ValueError(f"Unsupported format: {format}")

        content = exporter(proxies)

        if output_path:
            Path(output_path).write_text(content)

        return content

    def _export_json(self, proxies: list[Proxy]) -> str:
        """Export as JSON."""
        data = [self._proxy_export_row(p, include_ip=True, include_port=True) for p in proxies]
        return json.dumps(data, indent=2)

    def _export_csv(self, proxies: list[Proxy]) -> str:
        """Export as CSV."""
        output = io.StringIO()
        writer = csv.DictWriter(
            output, fieldnames=["url", "protocol", "country", "is_residential", "port"]
        )
        writer.writeheader()

        for p in proxies:
            writer.writerow(
                {
                    "url": public_proxy_url(str(p.url)),
                    "protocol": p.protocol,
                    "country": self._country(p),
                    "is_residential": bool(getattr(p, "is_residential", False)),
                    "port": self._port(p),
                }
            )

        return output.getvalue()

    def _export_yaml(self, proxies: list[Proxy]) -> str:
        """Export as YAML."""
        if not yaml:
            raise ImportError("PyYAML not installed. Install with: pip install pyyaml")

        data = [self._proxy_export_row(p) for p in proxies]
        return yaml.dump(data, default_flow_style=False)

    def _export_jsonl(self, proxies: list[Proxy]) -> str:
        """Export as JSONL (JSON Lines)."""
        lines = [
            json.dumps(
                {
                    "url": public_proxy_url(str(p.url)),
                    "protocol": p.protocol,
                    "country": self._country(p),
                    "is_residential": bool(getattr(p, "is_residential", False)),
                }
            )
            for p in proxies
        ]
        return "\n".join(lines)

    def _export_tsv(self, proxies: list[Proxy]) -> str:
        """Export as TSV."""
        output = io.StringIO()
        writer = csv.DictWriter(
            output, fieldnames=["url", "protocol", "country", "is_residential"], delimiter="\t"
        )
        writer.writeheader()

        for p in proxies:
            writer.writerow(
                {
                    "url": public_proxy_url(str(p.url)),
                    "protocol": p.protocol,
                    "country": self._country(p),
                    "is_residential": bool(getattr(p, "is_residential", False)),
                }
            )

        return output.getvalue()

    @staticmethod
    def _country(proxy: Proxy) -> str | None:
        metadata = getattr(proxy, "metadata", {}) or {}
        return (
            getattr(proxy, "country_code", None)
            or metadata.get("country_code")
            or metadata.get("country")
        )

    @staticmethod
    def _port(proxy: Proxy) -> int | None:
        parsed = urlparse(public_proxy_url(str(proxy.url)))
        return parsed.port

    def _proxy_export_row(
        self,
        proxy: Proxy,
        *,
        include_ip: bool = False,
        include_port: bool = False,
    ) -> dict[str, object]:
        row: dict[str, object] = {
            "url": public_proxy_url(str(proxy.url)),
            "protocol": proxy.protocol,
            "country": self._country(proxy),
            "is_residential": bool(getattr(proxy, "is_residential", False)),
        }
        if include_port:
            row["port"] = self._port(proxy)
        if include_ip:
            row["ip"] = getattr(proxy, "ip", None)
        return row
