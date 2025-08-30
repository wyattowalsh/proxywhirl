"""proxywhirl/exporter.py -- Comprehensive proxy list export functionality

This module provides the ProxyExporter class for creating proxy lists in various
data formats with advanced filtering, volume controls, and comprehensive formatting options.

Features:
- Multiple export formats: JSON, CSV, XML, TXT variants, YAML, SQL, PAC
- Comprehensive filtering by geography, performance, status, and metadata
- Volume controls including sampling, limits, pagination, and distribution
- Async-first design consistent with ProxyWhirl architecture
- Extensible format handler system for custom formats
"""

from __future__ import annotations

import csv
import json
import random
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml
from loguru import logger

from ..models import Proxy
from .models import (
    ExportConfig,
    ExportFormat,
    OutputConfig,
    ProxyFilter,
    SamplingMethod,
    SortField,
    SortOrder,
    VolumeControl,
)


class ProxyExportError(Exception):
    """Exception raised during proxy export operations."""


class ProxyExporter:
    """
    Comprehensive proxy list exporter with filtering, formatting, and volume controls.

    This class provides a unified interface for exporting proxy lists in various formats
    with sophisticated filtering and volume control capabilities.

    Examples
    --------
    Basic export:
        >>> exporter = ProxyExporter()
        >>> result = exporter.export(proxies, ExportConfig(format=ExportFormat.JSON))

    Advanced filtering and export:
        >>> config = ExportConfig(
        ...     format=ExportFormat.CSV,
        ...     filters=ProxyFilter(countries=['US', 'CA'], min_success_rate=0.8),
        ...     volume=VolumeControl(limit=100, sampling_method=SamplingMethod.TOP_QUALITY)
        ... )
        >>> result = exporter.export(proxies, config)

    Export to file:
        >>> config = ExportConfig(
        ...     format=ExportFormat.JSON_PRETTY,
        ...     output_file='proxies.json'
        ... )
        >>> exporter.export_to_file(proxies, config)
    """

    def __init__(self) -> None:
        """Initialize the ProxyExporter."""
        self._format_handlers: Dict[ExportFormat, callable] = {
            ExportFormat.JSON: self._format_json,
            ExportFormat.JSON_PRETTY: self._format_json,
            ExportFormat.JSON_COMPACT: self._format_json,
            ExportFormat.CSV: self._format_csv,
            ExportFormat.CSV_HEADERS: self._format_csv,
            ExportFormat.CSV_NO_HEADERS: self._format_csv,
            ExportFormat.TXT_HOSTPORT: self._format_txt,
            ExportFormat.TXT_URI: self._format_txt,
            ExportFormat.TXT_SIMPLE: self._format_txt,
            ExportFormat.TXT_DETAILED: self._format_txt,
            ExportFormat.XML: self._format_xml,
            ExportFormat.YAML: self._format_yaml,
            ExportFormat.SQL_INSERT: self._format_sql,
            ExportFormat.PAC: self._format_pac,
        }

    def export(self, proxies: List[Proxy], config: ExportConfig) -> str:
        """
        Export proxy list to string with specified configuration.

        Parameters
        ----------
        proxies : List[Proxy]
            List of proxies to export
        config : ExportConfig
            Export configuration including format, filters, and options

        Returns
        -------
        str
            Formatted export string

        Raises
        ------
        ProxyExportError
            If export operation fails
        """
        try:
            # Apply filtering
            filtered_proxies = self._apply_filters(proxies, config.filters)
            logger.info(f"Filtered {len(proxies)} proxies down to {len(filtered_proxies)}")

            # Apply volume controls
            processed_proxies = self._apply_volume_controls(filtered_proxies, config.volume)
            logger.info(f"Applied volume controls, final count: {len(processed_proxies)}")

            # Format output
            formatted_content = self._format_output(processed_proxies, config)

            # Add metadata if requested
            if config.include_metadata:
                formatted_content = self._add_metadata(formatted_content, processed_proxies, config)

            return formatted_content

        except Exception as e:
            raise ProxyExportError(f"Export failed: {e}") from e

    def export_to_file(self, proxies: List[Proxy], config: ExportConfig) -> Tuple[str, int]:
        """
        Export proxy list to file.

        Parameters
        ----------
        proxies : List[Proxy]
            List of proxies to export
        config : ExportConfig
            Export configuration including file path

        Returns
        -------
        Tuple[str, int]
            File path and number of proxies exported

        Raises
        ------
        ProxyExportError
            If file operation fails
        """
        if not config.output_file:
            raise ProxyExportError("output_file must be specified for file export")

        output_path = Path(config.output_file)

        # Check if file exists and overwrite is disabled
        if output_path.exists() and not config.overwrite:
            raise ProxyExportError(
                f"File {output_path} already exists. Use overwrite=True to replace it."
            )

        # Export to string first
        content = self.export(proxies, config)

        # Count proxies after all processing
        filtered_proxies = self._apply_filters(proxies, config.filters)
        final_proxies = self._apply_volume_controls(filtered_proxies, config.volume)
        export_count = len(final_proxies)

        try:
            # Write to file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding="utf-8")
            logger.info(f"Exported {export_count} proxies to {output_path}")

            return str(output_path), export_count

        except Exception as e:
            raise ProxyExportError(f"Failed to write to file {output_path}: {e}") from e

    def _apply_filters(self, proxies: List[Proxy], filters: Optional[ProxyFilter]) -> List[Proxy]:
        """Apply filtering criteria to proxy list."""
        if not filters:
            return proxies

        filtered = []

        for proxy in proxies:
            # Geographic filters
            if filters.countries and proxy.country_code not in filters.countries:
                continue
            if filters.exclude_countries and proxy.country_code in filters.exclude_countries:
                continue
            if filters.cities and proxy.city not in filters.cities:
                continue
            if filters.regions and proxy.region not in filters.regions:
                continue

            # Technical filters
            if filters.schemes and not any(scheme in proxy.schemes for scheme in filters.schemes):
                continue
            if filters.ports and proxy.port not in filters.ports:
                continue
            if filters.port_range:
                min_port, max_port = filters.port_range
                if not (min_port <= proxy.port <= max_port):
                    continue
            if filters.anonymity_levels and proxy.anonymity not in filters.anonymity_levels:
                continue

            # Performance filters
            if filters.min_response_time and (
                not proxy.response_time or proxy.response_time < filters.min_response_time
            ):
                continue
            if filters.max_response_time and (
                proxy.response_time and proxy.response_time > filters.max_response_time
            ):
                continue
            if filters.min_success_rate and (
                not hasattr(proxy, "metrics")
                or not proxy.metrics
                or proxy.metrics.success_rate / 100.0 < filters.min_success_rate
            ):
                continue
            if filters.min_quality_score and (
                not proxy.quality_score or proxy.quality_score < filters.min_quality_score
            ):
                continue
            if filters.min_uptime and (
                not hasattr(proxy, "metrics")
                or not proxy.metrics
                or not proxy.metrics.uptime_percentage
                or proxy.metrics.uptime_percentage < filters.min_uptime
            ):
                continue

            # Status filters
            if filters.statuses and proxy.status not in filters.statuses:
                continue
            if filters.exclude_statuses and proxy.status in filters.exclude_statuses:
                continue

            # Source filters
            if filters.sources and proxy.source not in filters.sources:
                continue
            if filters.exclude_sources and proxy.source in filters.exclude_sources:
                continue

            # Time-based filters
            if filters.checked_after and (
                not proxy.last_checked or proxy.last_checked < filters.checked_after
            ):
                continue
            if filters.checked_before and (
                not proxy.last_checked or proxy.last_checked > filters.checked_before
            ):
                continue
            if filters.success_after and (
                not hasattr(proxy, "metrics")
                or not proxy.metrics
                or not proxy.metrics.last_success
                or proxy.metrics.last_success < filters.success_after
            ):
                continue

            # Health filters
            if filters.healthy_only and (
                not hasattr(proxy, "metrics") or not proxy.metrics or not proxy.metrics.is_healthy
            ):
                continue
            if filters.max_consecutive_failures and (
                hasattr(proxy, "metrics")
                and proxy.metrics
                and proxy.metrics.consecutive_failures > filters.max_consecutive_failures
            ):
                continue

            filtered.append(proxy)

        return filtered

    def _apply_volume_controls(
        self, proxies: List[Proxy], volume: Optional[VolumeControl]
    ) -> List[Proxy]:
        """Apply volume controls to proxy list."""
        if not volume:
            return proxies

        processed = list(proxies)  # Create a copy

        # Apply sorting first
        if volume.sort_by:
            processed = self._sort_proxies(processed, volume.sort_by, volume.sort_order)

        # Apply distribution limits
        if volume.max_per_source:
            processed = self._limit_per_source(processed, volume.max_per_source)

        if volume.max_per_country:
            processed = self._limit_per_country(processed, volume.max_per_country)

        # Apply balanced sources if requested
        if volume.balanced_sources:
            processed = self._balance_sources(processed)

        # Apply sampling
        if volume.sampling_method != SamplingMethod.FIRST:
            processed = self._apply_sampling(processed, volume)

        # Apply percentage sampling
        if volume.sample_percentage:
            target_count = int(len(processed) * volume.sample_percentage / 100.0)
            processed = processed[:target_count]

        # Apply offset and limit
        if volume.offset:
            processed = processed[volume.offset :]

        if volume.limit:
            processed = processed[: volume.limit]

        return processed

    def _sort_proxies(
        self, proxies: List[Proxy], sort_field: SortField, sort_order: SortOrder
    ) -> List[Proxy]:
        """Sort proxies by specified field and order."""
        reverse = sort_order == SortOrder.DESC

        if sort_field == SortField.HOST:
            return sorted(proxies, key=lambda p: p.host, reverse=reverse)
        elif sort_field == SortField.PORT:
            return sorted(proxies, key=lambda p: p.port, reverse=reverse)
        elif sort_field == SortField.COUNTRY_CODE:
            return sorted(proxies, key=lambda p: p.country_code or "", reverse=reverse)
        elif sort_field == SortField.RESPONSE_TIME:
            return sorted(proxies, key=lambda p: p.response_time or float("inf"), reverse=reverse)
        elif sort_field == SortField.SUCCESS_RATE:
            return sorted(
                proxies,
                key=lambda p: (
                    p.metrics.success_rate if hasattr(p, "metrics") and p.metrics else 0.0
                ),
                reverse=reverse,
            )
        elif sort_field == SortField.QUALITY_SCORE:
            return sorted(proxies, key=lambda p: p.quality_score or 0.0, reverse=reverse)
        elif sort_field == SortField.LAST_CHECKED:
            return sorted(proxies, key=lambda p: p.last_checked or datetime.min, reverse=reverse)
        elif sort_field == SortField.SOURCE:
            return sorted(proxies, key=lambda p: p.source or "", reverse=reverse)
        elif sort_field == SortField.ANONYMITY:
            return sorted(
                proxies, key=lambda p: p.anonymity.value if p.anonymity else "", reverse=reverse
            )
        else:
            return proxies

    def _limit_per_source(self, proxies: List[Proxy], max_per_source: int) -> List[Proxy]:
        """Limit number of proxies per source."""
        source_counts = defaultdict(int)
        filtered = []

        for proxy in proxies:
            source = proxy.source or "unknown"
            if source_counts[source] < max_per_source:
                filtered.append(proxy)
                source_counts[source] += 1

        return filtered

    def _limit_per_country(self, proxies: List[Proxy], max_per_country: int) -> List[Proxy]:
        """Limit number of proxies per country."""
        country_counts = defaultdict(int)
        filtered = []

        for proxy in proxies:
            country = proxy.country_code or "unknown"
            if country_counts[country] < max_per_country:
                filtered.append(proxy)
                country_counts[country] += 1

        return filtered

    def _balance_sources(self, proxies: List[Proxy]) -> List[Proxy]:
        """Ensure balanced representation from each source."""
        # Group by source
        by_source = defaultdict(list)
        for proxy in proxies:
            source = proxy.source or "unknown"
            by_source[source].append(proxy)

        if not by_source:
            return proxies

        # Find minimum count
        min_count = min(len(source_proxies) for source_proxies in by_source.values())

        # Take equal amounts from each source
        balanced = []
        for source_proxies in by_source.values():
            balanced.extend(source_proxies[:min_count])

        return balanced

    def _apply_sampling(self, proxies: List[Proxy], volume: VolumeControl) -> List[Proxy]:
        """Apply sampling method to proxy list."""
        if volume.sampling_method == SamplingMethod.RANDOM:
            return random.sample(proxies, min(len(proxies), volume.limit or len(proxies)))

        elif volume.sampling_method == SamplingMethod.TOP_QUALITY:
            # Sort by quality score descending
            sorted_proxies = sorted(proxies, key=lambda p: p.quality_score or 0.0, reverse=True)
            return sorted_proxies

        elif volume.sampling_method == SamplingMethod.TOP_SPEED:
            # Sort by response time ascending (fastest first)
            sorted_proxies = sorted(proxies, key=lambda p: p.response_time or float("inf"))
            return sorted_proxies

        elif volume.sampling_method == SamplingMethod.TOP_RELIABILITY:
            # Sort by success rate descending
            sorted_proxies = sorted(
                proxies,
                key=lambda p: (
                    p.metrics.success_rate if hasattr(p, "metrics") and p.metrics else 0.0
                ),
                reverse=True,
            )
            return sorted_proxies

        elif volume.sampling_method == SamplingMethod.BALANCED:
            # Already handled in _balance_sources
            return proxies

        else:  # SamplingMethod.FIRST
            return proxies

    def _format_output(self, proxies: List[Proxy], config: ExportConfig) -> str:
        """Format proxy list according to specified format."""
        handler = self._format_handlers.get(config.format)
        if not handler:
            raise ProxyExportError(f"Unsupported format: {config.format}")

        return handler(proxies, config.output)

    def _format_json(self, proxies: List[Proxy], output_config: OutputConfig) -> str:
        """Format proxies as JSON."""
        proxy_data = [proxy.model_dump(mode="json") for proxy in proxies]

        indent = output_config.json_indent
        ensure_ascii = output_config.json_ensure_ascii
        separators = None

        # Handle compact format
        if not output_config.pretty_format and indent is None:
            separators = (",", ":")  # Compact separators

        return json.dumps(
            proxy_data, indent=indent, ensure_ascii=ensure_ascii, separators=separators
        )

    def _format_csv(self, proxies: List[Proxy], output_config: OutputConfig) -> str:
        """Format proxies as CSV."""
        if not proxies:
            return ""

        output = StringIO()

        # Determine columns
        if output_config.csv_columns:
            fieldnames = output_config.csv_columns
        else:
            # Default columns based on available data
            fieldnames = [
                "host",
                "port",
                "schemes",
                "country_code",
                "anonymity",
                "response_time",
                "status",
                "source",
            ]

        writer = csv.DictWriter(
            output,
            fieldnames=fieldnames,
            delimiter=output_config.csv_delimiter,
            quotechar=output_config.csv_quote_char,
        )

        # Write headers
        if output_config.include_headers:
            writer.writeheader()

        # Write data
        for proxy in proxies:
            row = {}
            proxy_dict = proxy.model_dump()

            for field in fieldnames:
                if field == "schemes":
                    # Convert schemes list to comma-separated string
                    row[field] = ",".join(s.value for s in proxy.schemes)
                elif field in proxy_dict:
                    value = proxy_dict[field]
                    # Handle datetime serialization
                    if hasattr(value, "isoformat"):
                        value = value.isoformat()
                    row[field] = value
                else:
                    row[field] = ""

            writer.writerow(row)

        return output.getvalue()

    def _format_xml(self, proxies: List[Proxy], output_config: OutputConfig) -> str:
        """Format proxies as XML."""
        root = ET.Element(output_config.xml_root_element)

        for proxy in proxies:
            proxy_elem = ET.SubElement(root, output_config.xml_item_element)

            # Add basic fields
            ET.SubElement(proxy_elem, "host").text = proxy.host
            ET.SubElement(proxy_elem, "port").text = str(proxy.port)
            ET.SubElement(proxy_elem, "schemes").text = ",".join(s.value for s in proxy.schemes)

            if proxy.country_code:
                ET.SubElement(proxy_elem, "country_code").text = proxy.country_code

            if proxy.anonymity:
                ET.SubElement(proxy_elem, "anonymity").text = proxy.anonymity.value

            if proxy.response_time:
                ET.SubElement(proxy_elem, "response_time").text = str(proxy.response_time)

            if proxy.status:
                ET.SubElement(proxy_elem, "status").text = proxy.status.value

            if proxy.source:
                ET.SubElement(proxy_elem, "source").text = proxy.source

        if output_config.xml_pretty:
            self._indent_xml(root)

        return ET.tostring(root, encoding="unicode")

    def _indent_xml(self, elem: ET.Element, level: int = 0) -> None:
        """Add pretty-printing indentation to XML element."""
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for child in elem:
                self._indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def _format_yaml(self, proxies: List[Proxy], output_config: OutputConfig) -> str:
        """Format proxies as YAML."""
        proxy_data = [proxy.model_dump(mode="json") for proxy in proxies]
        return yaml.dump(proxy_data, default_flow_style=False, indent=2)

    def _format_txt(self, proxies: List[Proxy], output_config: OutputConfig) -> str:
        """Format proxies as text in various formats."""
        lines = []

        for proxy in proxies:
            if output_config.txt_template:
                # Custom template formatting
                line = output_config.txt_template.format(
                    host=proxy.host,
                    port=proxy.port,
                    country_code=proxy.country_code or "",
                    anonymity=proxy.anonymity.value if proxy.anonymity else "",
                    response_time=proxy.response_time or "",
                    status=proxy.status.value if proxy.status else "",
                    source=proxy.source or "",
                    schemes=",".join(s.value for s in proxy.schemes),
                )
            else:
                # Default format based on export format
                format_name = str(
                    output_config.__class__.__name__
                )  # This is a hack, need format type
                if "hostport" in format_name.lower():
                    line = f"{proxy.host}:{proxy.port}"
                elif "uri" in format_name.lower():
                    scheme = proxy.schemes[0].value if proxy.schemes else "http"
                    line = f"{scheme}://{proxy.host}:{proxy.port}"
                elif "detailed" in format_name.lower():
                    line = f"{proxy.host}:{proxy.port} | {proxy.country_code or 'N/A'} | {proxy.anonymity.value if proxy.anonymity else 'N/A'} | {proxy.response_time or 'N/A'}s"
                else:  # simple
                    line = f"{proxy.host}:{proxy.port}"

            lines.append(line)

        return output_config.txt_separator.join(lines)

    def _format_sql(self, proxies: List[Proxy], output_config: OutputConfig) -> str:
        """Format proxies as SQL INSERT statements."""
        if not proxies:
            return ""

        table_name = output_config.sql_table_name
        batch_size = output_config.sql_batch_size

        # Define columns for SQL table
        columns = [
            "host",
            "port",
            "schemes",
            "country_code",
            "anonymity",
            "response_time",
            "status",
            "source",
            "last_checked",
        ]
        columns_str = ", ".join(columns)

        statements = []

        # Process in batches
        for i in range(0, len(proxies), batch_size):
            batch = proxies[i : i + batch_size]
            values_list = []

            for proxy in batch:
                values = [
                    f"'{proxy.host}'",
                    str(proxy.port),
                    f"'{','.join(s.value for s in proxy.schemes)}'",
                    f"'{proxy.country_code or ''}'" if proxy.country_code else "NULL",
                    f"'{proxy.anonymity.value}'" if proxy.anonymity else "NULL",
                    str(proxy.response_time) if proxy.response_time else "NULL",
                    f"'{proxy.status.value}'" if proxy.status else "NULL",
                    f"'{proxy.source or ''}'" if proxy.source else "NULL",
                    f"'{proxy.last_checked.isoformat()}'" if proxy.last_checked else "NULL",
                ]
                values_list.append(f"({', '.join(values)})")

            statement = (
                f"INSERT INTO {table_name} ({columns_str}) VALUES\n  "
                + ",\n  ".join(values_list)
                + ";"
            )
            statements.append(statement)

        return "\n\n".join(statements)

    def _format_pac(self, proxies: List[Proxy], output_config: OutputConfig) -> str:
        """Format proxies as PAC (Proxy Auto-Configuration) file."""
        function_name = output_config.pac_function_name
        proxy_type = output_config.pac_proxy_type

        # Build proxy list for PAC
        proxy_entries = []
        for proxy in proxies:
            entry = f'"{proxy_type} {proxy.host}:{proxy.port}"'
            proxy_entries.append(entry)

        # Create PAC file content
        pac_content = f"""function {function_name}(url, host) {{
    // ProxyWhirl generated PAC file
    // Generated on: {datetime.now(timezone.utc).isoformat()}
    // Total proxies: {len(proxies)}
    
    // Define proxy list
    var proxies = [
        {',\n        '.join(proxy_entries)}
    ];
    
    // Simple round-robin selection
    var proxy_index = Math.floor(Math.random() * proxies.length);
    return proxies[proxy_index] + "; DIRECT";
}}"""

        return pac_content

    def _add_metadata(self, content: str, proxies: List[Proxy], config: ExportConfig) -> str:
        """Add export metadata to formatted content."""
        now = datetime.now(timezone.utc)
        metadata_lines = [
            f"Export generated: {now.isoformat()}",
            f"Format: {config.format}",
            f"Total proxies: {len(proxies)}",
        ]

        # Add filter summary if filters were applied
        if config.filters:
            filter_summary = []
            if config.filters.countries:
                filter_summary.append(f"Countries: {', '.join(config.filters.countries)}")
            if config.filters.schemes:
                filter_summary.append(
                    f"Schemes: {', '.join(s.value for s in config.filters.schemes)}"
                )
            if config.filters.min_success_rate:
                filter_summary.append(f"Min success rate: {config.filters.min_success_rate}")
            if config.filters.healthy_only:
                filter_summary.append("Healthy proxies only")

            if filter_summary:
                metadata_lines.append(f"Filters applied: {'; '.join(filter_summary)}")

        # Add volume control summary
        if config.volume:
            if config.volume.limit:
                metadata_lines.append(f"Limited to: {config.volume.limit} proxies")
            if config.volume.sampling_method != SamplingMethod.FIRST:
                metadata_lines.append(f"Sampling: {config.volume.sampling_method}")

        metadata_text = "\n".join(f"# {line}" for line in metadata_lines)

        # Add metadata based on format
        if config.metadata_format == "comment":
            if str(config.format).startswith(("json", "xml", "yaml")):
                # These formats don't support comments, add as separate section
                return f"{metadata_text}\n\n{content}"
            else:
                return f"{metadata_text}\n\n{content}"
        elif config.metadata_format == "header":
            return f"{metadata_text}\n{content}"
        else:  # separate
            return f"{metadata_text}\n\n{content}"
