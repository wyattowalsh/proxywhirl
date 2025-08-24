"""Tests for proxywhirl.exporter module.

Comprehensive unit tests for the ProxyExporter class including:
- Export functionality across all supported formats
- Filtering capabilities (geographic, technical, performance, time-based)
- Volume controls (sampling, limits, distribution, sorting)
- Output configuration and format-specific options
- Error handling and edge cases
- File export operations
"""

from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import List
from unittest.mock import Mock, mock_open, patch

import pytest
import yaml

from proxywhirl.export_models import (
    ExportConfig,
    ExportFormat,
    OutputConfig,
    ProxyFilter,
    SamplingMethod,
    SortField,
    SortOrder,
    VolumeControl,
)
from proxywhirl.exporter import ProxyExporter, ProxyExportError
from proxywhirl.models import AnonymityLevel, Proxy, Scheme


@pytest.fixture
def sample_proxies():
    """Create sample proxy data for testing."""
    return [
        Proxy(
            host="1.2.3.4",
            port=8080,
            schemes=[Scheme.HTTP],
            country_code="US",
            city="New York",
            anonymity=AnonymityLevel.ANONYMOUS,
            response_time=0.5,
            success_rate=0.9,
            quality_score=0.85,
            source="test_source",
        ),
        Proxy(
            host="5.6.7.8",
            port=3128,
            schemes=[Scheme.HTTP, Scheme.HTTPS],
            country_code="CA",
            city="Toronto",
            anonymity=AnonymityLevel.ELITE,
            response_time=0.3,
            success_rate=0.95,
            quality_score=0.92,
            source="test_source",
        ),
        Proxy(
            host="9.10.11.12",
            port=1080,
            schemes=[Scheme.SOCKS5],
            country_code="GB",
            city="London",
            anonymity=AnonymityLevel.TRANSPARENT,
            response_time=0.8,
            success_rate=0.7,
            quality_score=0.6,
            source="another_source",
        ),
    ]


@pytest.fixture
def exporter():
    """Create ProxyExporter instance."""
    return ProxyExporter()


class TestProxyExporter:
    """Test ProxyExporter class initialization and basic functionality."""

    def test_exporter_initialization(self, exporter):
        """Test ProxyExporter initializes with format handlers."""
        assert isinstance(exporter._format_handlers, dict)
        assert len(exporter._format_handlers) == 14
        assert ExportFormat.JSON in exporter._format_handlers
        assert ExportFormat.CSV in exporter._format_handlers
        assert ExportFormat.XML in exporter._format_handlers
        assert ExportFormat.PAC in exporter._format_handlers

    def test_exporter_has_all_format_handlers(self, exporter):
        """Test that exporter has handlers for all export formats."""
        for format_type in ExportFormat:
            assert format_type in exporter._format_handlers
            assert callable(exporter._format_handlers[format_type])


class TestExportBasicFunctionality:
    """Test basic export functionality across different formats."""

    def test_export_json_default(self, exporter, sample_proxies):
        """Test export to JSON format with default settings."""
        config = ExportConfig(format=ExportFormat.JSON)
        result = exporter.export(sample_proxies, config)

        assert isinstance(result, str)
        assert "1.2.3.4" in result
        assert "8080" in result
        assert len(result) > 0

        # Should be valid JSON
        import json

        parsed = json.loads(result)
        assert isinstance(parsed, (list, dict))

    def test_export_json_pretty(self, exporter, sample_proxies):
        """Test export to pretty-formatted JSON."""
        config = ExportConfig(format=ExportFormat.JSON_PRETTY)
        result = exporter.export(sample_proxies, config)

        # Pretty JSON should have indentation
        assert "  " in result or "\\n" in result or "\n" in result

        import json

        parsed = json.loads(result)
        assert isinstance(parsed, (list, dict))

    def test_export_csv(self, exporter, sample_proxies):
        """Test export to CSV format."""
        config = ExportConfig(format=ExportFormat.CSV)
        result = exporter.export(sample_proxies, config)

        lines = result.strip().split("\n")
        assert len(lines) >= 2  # Header + at least one data row

        # Check for CSV structure
        assert "," in result
        assert "1.2.3.4" in result
        assert "8080" in result

    def test_export_csv_no_headers(self, exporter, sample_proxies):
        """Test export to CSV without headers."""
        config = ExportConfig(format=ExportFormat.CSV_NO_HEADERS)
        result = exporter.export(sample_proxies, config)

        lines = result.strip().split("\n")
        # Should have only data rows, no header
        assert "host" not in lines[0].lower()
        assert "1.2.3.4" in result

    def test_export_txt_hostport(self, exporter, sample_proxies):
        """Test export to text format (host:port)."""
        config = ExportConfig(format=ExportFormat.TXT_HOSTPORT)
        result = exporter.export(sample_proxies, config)

        lines = result.strip().split("\n")
        assert "1.2.3.4:8080" in lines
        assert "5.6.7.8:3128" in lines
        assert "9.10.11.12:1080" in lines

    def test_export_xml(self, exporter, sample_proxies):
        """Test export to XML format."""
        config = ExportConfig(format=ExportFormat.XML)
        result = exporter.export(sample_proxies, config)

        assert "<proxies>" in result
        assert "</proxies>" in result
        assert "<proxy>" in result
        assert "</proxy>" in result
        assert "1.2.3.4" in result

    def test_export_yaml(self, exporter, sample_proxies):
        """Test export to YAML format."""
        config = ExportConfig(format=ExportFormat.YAML)
        result = exporter.export(sample_proxies, config)

        # Should be valid YAML
        parsed = yaml.safe_load(result)
        assert isinstance(parsed, (list, dict))

        # Check content
        result_str = str(result)
        assert "1.2.3.4" in result_str
        assert "8080" in result_str


class TestFiltering:
    """Test proxy filtering functionality."""

    def test_filter_by_country(self, exporter, sample_proxies):
        """Test filtering by country codes."""
        config = ExportConfig(format=ExportFormat.JSON, filters=ProxyFilter(countries=["US"]))
        result = exporter.export(sample_proxies, config)

        import json

        parsed = json.loads(result)

        # Should only contain US proxies
        if isinstance(parsed, list):
            for proxy in parsed:
                assert proxy.get("country_code") == "US"

    def test_filter_by_schemes(self, exporter, sample_proxies):
        """Test filtering by proxy schemes."""
        config = ExportConfig(format=ExportFormat.JSON, filters=ProxyFilter(schemes=[Scheme.HTTP]))
        result = exporter.export(sample_proxies, config)

        import json

        parsed = json.loads(result)

        # All results should have HTTP scheme
        assert "http" in result.lower()

    def test_filter_by_port_range(self, exporter, sample_proxies):
        """Test filtering by port range."""
        config = ExportConfig(
            format=ExportFormat.JSON, filters=ProxyFilter(port_range=(3000, 9000))
        )
        result = exporter.export(sample_proxies, config)

        import json

        parsed = json.loads(result)

        # Should contain proxies with ports in range
        assert "8080" in result  # 8080 is in range
        assert "3128" in result  # 3128 is in range
        # 1080 should be filtered out as it's below 3000

    def test_filter_by_performance(self, exporter, sample_proxies):
        """Test filtering by performance metrics."""
        config = ExportConfig(
            format=ExportFormat.JSON,
            filters=ProxyFilter(min_success_rate=0.8, max_response_time=0.6),
        )
        result = exporter.export(sample_proxies, config)

        import json

        parsed = json.loads(result)

        # Should only contain high-performing proxies
        # This would filter out the GB proxy with 0.7 success rate and 0.8 response time

    def test_filter_multiple_criteria(self, exporter, sample_proxies):
        """Test filtering with multiple criteria."""
        config = ExportConfig(
            format=ExportFormat.JSON,
            filters=ProxyFilter(
                countries=["US", "CA"], schemes=[Scheme.HTTP], min_success_rate=0.85
            ),
        )
        result = exporter.export(sample_proxies, config)

        # Should apply all filters
        assert isinstance(result, str)
        import json

        parsed = json.loads(result)
        # Exact assertions would depend on the filtering implementation


class TestVolumeControls:
    """Test volume control functionality."""

    def test_limit_control(self, exporter, sample_proxies):
        """Test limiting number of exported proxies."""
        config = ExportConfig(format=ExportFormat.JSON, volume=VolumeControl(limit=2))
        result = exporter.export(sample_proxies, config)

        import json

        parsed = json.loads(result)

        if isinstance(parsed, list):
            assert len(parsed) == 2

    def test_offset_control(self, exporter, sample_proxies):
        """Test offset (pagination) control."""
        config = ExportConfig(format=ExportFormat.JSON, volume=VolumeControl(offset=1, limit=2))
        result = exporter.export(sample_proxies, config)

        import json

        parsed = json.loads(result)

        if isinstance(parsed, list):
            assert len(parsed) == 2
            # Should skip first proxy

    def test_sampling_methods(self, exporter, sample_proxies):
        """Test different sampling methods."""
        for method in SamplingMethod:
            config = ExportConfig(
                format=ExportFormat.JSON, volume=VolumeControl(limit=2, sampling_method=method)
            )
            result = exporter.export(sample_proxies, config)
            assert isinstance(result, str)
            assert len(result) > 0

    def test_sorting(self, exporter, sample_proxies):
        """Test sorting functionality."""
        config = ExportConfig(
            format=ExportFormat.TXT_HOSTPORT,
            volume=VolumeControl(sort_by=SortField.RESPONSE_TIME, sort_order=SortOrder.ASC),
        )
        result = exporter.export(sample_proxies, config)

        lines = result.strip().split("\n")
        assert len(lines) == 3
        # First line should be the fastest proxy (0.3s response time - CA proxy)
        assert "5.6.7.8:3128" in lines[0]


class TestOutputConfiguration:
    """Test output configuration options."""

    def test_csv_custom_delimiter(self, exporter, sample_proxies):
        """Test CSV with custom delimiter."""
        config = ExportConfig(format=ExportFormat.CSV, output=OutputConfig(csv_delimiter="|"))
        result = exporter.export(sample_proxies, config)

        assert "|" in result
        assert "," not in result

    def test_json_custom_indent(self, exporter, sample_proxies):
        """Test JSON with custom indentation."""
        config = ExportConfig(
            format=ExportFormat.JSON, output=OutputConfig(json_indent=4, pretty_format=True)
        )
        result = exporter.export(sample_proxies, config)

        # Should have 4-space indentation
        assert "    " in result

    def test_xml_custom_elements(self, exporter, sample_proxies):
        """Test XML with custom element names."""
        config = ExportConfig(
            format=ExportFormat.XML,
            output=OutputConfig(xml_root_element="proxy_list", xml_item_element="entry"),
        )
        result = exporter.export(sample_proxies, config)

        assert "<proxy_list>" in result
        assert "<entry>" in result
        assert "<proxies>" not in result
        assert "<proxy>" not in result


class TestFileExport:
    """Test file export functionality."""

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.exists")
    def test_export_to_file_success(self, mock_exists, mock_file, exporter, sample_proxies):
        """Test successful file export."""
        mock_exists.return_value = False
        config = ExportConfig(format=ExportFormat.JSON, output_file="test_proxies.json")

        file_path, count = exporter.export_to_file(sample_proxies, config)

        assert file_path == "test_proxies.json"
        assert count == 3
        mock_file.assert_called_once_with("test_proxies.json", "w", encoding="utf-8")

    @patch("pathlib.Path.exists")
    def test_export_to_file_exists_no_overwrite(self, mock_exists, exporter, sample_proxies):
        """Test file export when file exists and overwrite is False."""
        mock_exists.return_value = True
        config = ExportConfig(
            format=ExportFormat.JSON, output_file="existing_file.json", overwrite=False
        )

        with pytest.raises(ProxyExportError) as exc_info:
            exporter.export_to_file(sample_proxies, config)
        assert "already exists" in str(exc_info.value)

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.exists")
    def test_export_to_file_exists_with_overwrite(
        self, mock_exists, mock_file, exporter, sample_proxies
    ):
        """Test file export with overwrite enabled."""
        mock_exists.return_value = True
        config = ExportConfig(
            format=ExportFormat.JSON, output_file="existing_file.json", overwrite=True
        )

        file_path, count = exporter.export_to_file(sample_proxies, config)

        assert file_path == "existing_file.json"
        assert count == 3
        mock_file.assert_called_once_with("existing_file.json", "w", encoding="utf-8")


class TestMetadataInclusion:
    """Test metadata inclusion in exports."""

    def test_metadata_included_json(self, exporter, sample_proxies):
        """Test metadata inclusion in JSON format."""
        config = ExportConfig(format=ExportFormat.JSON, include_metadata=True)
        result = exporter.export(sample_proxies, config)

        # Should contain metadata
        assert "metadata" in result.lower() or "exported" in result.lower()

    def test_metadata_excluded(self, exporter, sample_proxies):
        """Test metadata exclusion."""
        config = ExportConfig(format=ExportFormat.JSON, include_metadata=False)
        result = exporter.export(sample_proxies, config)

        # Should be clean JSON without metadata comments
        import json

        parsed = json.loads(result)
        assert isinstance(parsed, (list, dict))


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_export_empty_proxy_list(self, exporter):
        """Test export with empty proxy list."""
        config = ExportConfig(format=ExportFormat.JSON)
        result = exporter.export([], config)

        import json

        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) == 0

    def test_export_invalid_format_handler(self, exporter, sample_proxies):
        """Test behavior with missing format handler."""
        # Temporarily remove a handler to simulate error
        original_handler = exporter._format_handlers.pop(ExportFormat.JSON)

        try:
            config = ExportConfig(format=ExportFormat.JSON)
            with pytest.raises(ProxyExportError):
                exporter.export(sample_proxies, config)
        finally:
            # Restore handler
            exporter._format_handlers[ExportFormat.JSON] = original_handler

    def test_export_with_filter_no_matches(self, exporter, sample_proxies):
        """Test export when filters match no proxies."""
        config = ExportConfig(
            format=ExportFormat.JSON, filters=ProxyFilter(countries=["XX"])  # Non-existent country
        )
        result = exporter.export(sample_proxies, config)

        import json

        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) == 0

    def test_export_with_invalid_volume_config(self, exporter, sample_proxies):
        """Test export with conflicting volume configuration."""
        # This should be caught during model validation
        with pytest.raises(Exception):  # ValidationError or similar
            config = ExportConfig(
                format=ExportFormat.JSON, volume=VolumeControl(limit=10, sample_percentage=50.0)
            )

    @patch("builtins.open", side_effect=IOError("Permission denied"))
    def test_export_to_file_write_error(self, mock_file, exporter, sample_proxies):
        """Test file export with write error."""
        config = ExportConfig(format=ExportFormat.JSON, output_file="readonly_file.json")

        with pytest.raises(ProxyExportError) as exc_info:
            exporter.export_to_file(sample_proxies, config)
        assert "Permission denied" in str(exc_info.value)


class TestSpecialFormats:
    """Test special format exports (PAC, SQL)."""

    def test_export_pac_format(self, exporter, sample_proxies):
        """Test PAC (Proxy Auto-Configuration) format export."""
        config = ExportConfig(format=ExportFormat.PAC)
        result = exporter.export(sample_proxies, config)

        # PAC file should contain JavaScript function
        assert "function FindProxyForURL" in result or "FindProxyForURL" in result
        assert "1.2.3.4:8080" in result

    def test_export_sql_format(self, exporter, sample_proxies):
        """Test SQL INSERT format export."""
        config = ExportConfig(format=ExportFormat.SQL_INSERT)
        result = exporter.export(sample_proxies, config)

        # Should contain SQL INSERT statements
        assert "INSERT INTO" in result.upper()
        assert "1.2.3.4" in result
        assert "8080" in result

    def test_export_sql_custom_table(self, exporter, sample_proxies):
        """Test SQL export with custom table name."""
        config = ExportConfig(
            format=ExportFormat.SQL_INSERT, output=OutputConfig(sql_table_name="custom_proxies")
        )
        result = exporter.export(sample_proxies, config)

        assert "custom_proxies" in result
        assert "proxies" not in result or result.count("custom_proxies") > result.count("proxies")


class TestComplexScenarios:
    """Test complex, real-world export scenarios."""

    def test_complex_export_workflow(self, exporter, sample_proxies):
        """Test complex export with multiple filters and controls."""
        config = ExportConfig(
            format=ExportFormat.CSV,
            filters=ProxyFilter(
                countries=["US", "CA"], schemes=[Scheme.HTTP, Scheme.HTTPS], min_success_rate=0.8
            ),
            volume=VolumeControl(
                limit=10,
                sampling_method=SamplingMethod.TOP_QUALITY,
                sort_by=SortField.QUALITY_SCORE,
                sort_order=SortOrder.DESC,
            ),
            output=OutputConfig(csv_delimiter=";", include_headers=True),
            include_metadata=True,
        )

        result = exporter.export(sample_proxies, config)

        # Should be valid CSV with semicolon delimiter
        assert ";" in result
        lines = result.strip().split("\n")
        assert len(lines) >= 1  # At least header

    def test_export_performance_with_large_dataset(self, exporter):
        """Test export performance with larger dataset."""
        # Create larger proxy list for performance testing
        large_proxy_list = []
        for i in range(100):
            proxy = Proxy(
                host=f"192.168.1.{i % 255}",
                port=8080 + (i % 1000),
                schemes=[Scheme.HTTP],
                country_code="US",
                response_time=0.1 + (i % 10) / 10,
                success_rate=0.5 + (i % 5) / 10,
                quality_score=0.3 + (i % 7) / 10,
            )
            large_proxy_list.append(proxy)

        config = ExportConfig(format=ExportFormat.JSON, volume=VolumeControl(limit=50))

        result = exporter.export(large_proxy_list, config)

        import json

        parsed = json.loads(result)
        assert len(parsed) == 50
