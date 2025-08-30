"""Tests for proxywhirl.export_models module.

Comprehensive unit tests for export-specific models and enums including:
- ExportFormat, SamplingMethod, SortField, SortOrder enums
- ProxyFilter model with geographic, technical, performance, and time-based filters
- VolumeControl model with sampling, distribution, and sorting options
- OutputConfig model for format-specific output configuration
- ExportConfig model combining all export options with validation
"""

from datetime import datetime, timezone
from typing import List, Optional

import pytest
from pydantic import ValidationError

from proxywhirl.exporter import (
    ExportConfig,
    ExportFormat,
    OutputConfig,
    ProxyFilter,
    SamplingMethod,
    SortField,
    SortOrder,
    VolumeControl,
)
from proxywhirl.models import AnonymityLevel, ProxyStatus, Scheme


class TestExportFormat:
    """Test ExportFormat enum."""

    def test_export_format_values(self):
        """Test ExportFormat enum has correct values."""
        assert ExportFormat.JSON == "json"
        assert ExportFormat.JSON_PRETTY == "json_pretty"
        assert ExportFormat.JSON_COMPACT == "json_compact"
        assert ExportFormat.CSV == "csv"
        assert ExportFormat.CSV_HEADERS == "csv_headers"
        assert ExportFormat.CSV_NO_HEADERS == "csv_no_headers"
        assert ExportFormat.TXT_HOSTPORT == "txt_hostport"
        assert ExportFormat.TXT_URI == "txt_uri"
        assert ExportFormat.TXT_SIMPLE == "txt_simple"
        assert ExportFormat.TXT_DETAILED == "txt_detailed"
        assert ExportFormat.XML == "xml"
        assert ExportFormat.YAML == "yaml"
        assert ExportFormat.SQL_INSERT == "sql_insert"
        assert ExportFormat.PAC == "pac"

    def test_export_format_iteration(self):
        """Test ExportFormat enum iteration."""
        formats = list(ExportFormat)
        assert len(formats) == 14
        assert ExportFormat.JSON in formats
        assert ExportFormat.PAC in formats

    def test_export_format_membership(self):
        """Test ExportFormat enum membership."""
        assert "json" in ExportFormat
        assert "invalid_format" not in ExportFormat


class TestSamplingMethod:
    """Test SamplingMethod enum."""

    def test_sampling_method_values(self):
        """Test SamplingMethod enum has correct values."""
        assert SamplingMethod.FIRST == "first"
        assert SamplingMethod.RANDOM == "random"
        assert SamplingMethod.TOP_QUALITY == "top_quality"
        assert SamplingMethod.TOP_SPEED == "top_speed"
        assert SamplingMethod.TOP_RELIABILITY == "top_reliability"
        assert SamplingMethod.BALANCED == "balanced"

    def test_sampling_method_iteration(self):
        """Test SamplingMethod enum iteration."""
        methods = list(SamplingMethod)
        assert len(methods) == 6
        assert SamplingMethod.FIRST in methods
        assert SamplingMethod.BALANCED in methods


class TestSortField:
    """Test SortField enum."""

    def test_sort_field_values(self):
        """Test SortField enum has correct values."""
        assert SortField.HOST == "host"
        assert SortField.PORT == "port"
        assert SortField.COUNTRY_CODE == "country_code"
        assert SortField.RESPONSE_TIME == "response_time"
        assert SortField.SUCCESS_RATE == "success_rate"
        assert SortField.QUALITY_SCORE == "quality_score"
        assert SortField.LAST_CHECKED == "last_checked"
        assert SortField.SOURCE == "source"
        assert SortField.ANONYMITY == "anonymity"

    def test_sort_field_iteration(self):
        """Test SortField enum iteration."""
        fields = list(SortField)
        assert len(fields) == 9
        assert SortField.HOST in fields
        assert SortField.ANONYMITY in fields


class TestSortOrder:
    """Test SortOrder enum."""

    def test_sort_order_values(self):
        """Test SortOrder enum has correct values."""
        assert SortOrder.ASC == "asc"
        assert SortOrder.DESC == "desc"

    def test_sort_order_iteration(self):
        """Test SortOrder enum iteration."""
        orders = list(SortOrder)
        assert len(orders) == 2
        assert SortOrder.ASC in orders
        assert SortOrder.DESC in orders


class TestProxyFilter:
    """Test ProxyFilter model."""

    def test_proxy_filter_creation_empty(self):
        """Test ProxyFilter creation with no filters."""
        filter_obj = ProxyFilter()
        assert filter_obj.countries is None
        assert filter_obj.exclude_countries is None
        assert filter_obj.schemes is None
        assert filter_obj.healthy_only is False

    def test_proxy_filter_creation_with_values(self):
        """Test ProxyFilter creation with various filter values."""
        filter_obj = ProxyFilter(
            countries=["US", "CA"],
            schemes=[Scheme.HTTP, Scheme.HTTPS],
            ports=[80, 443, 8080],
            anonymity_levels=[AnonymityLevel.ANONYMOUS, AnonymityLevel.ELITE],
            min_response_time=0.1,
            max_response_time=5.0,
            min_success_rate=0.8,
            min_quality_score=0.7,
            healthy_only=True,
        )
        assert filter_obj.countries == ["US", "CA"]
        assert filter_obj.schemes == [Scheme.HTTP, Scheme.HTTPS]
        assert filter_obj.ports == [80, 443, 8080]
        assert filter_obj.anonymity_levels == [AnonymityLevel.ANONYMOUS, AnonymityLevel.ELITE]
        assert filter_obj.min_response_time == 0.1
        assert filter_obj.max_response_time == 5.0
        assert filter_obj.min_success_rate == 0.8
        assert filter_obj.min_quality_score == 0.7
        assert filter_obj.healthy_only is True

    def test_country_code_validation_valid(self):
        """Test country code validation with valid codes."""
        filter_obj = ProxyFilter(countries=["us", "CA", "gb"])
        assert filter_obj.countries == ["US", "CA", "GB"]

    def test_country_code_validation_invalid_length(self):
        """Test country code validation with invalid lengths."""
        with pytest.raises(ValidationError) as exc_info:
            ProxyFilter(countries=["USA"])
        assert "Invalid country code" in str(exc_info.value)

    def test_country_code_validation_invalid_characters(self):
        """Test country code validation with non-alphabetic characters."""
        with pytest.raises(ValidationError) as exc_info:
            ProxyFilter(countries=["U1"])
        assert "Invalid country code" in str(exc_info.value)

    def test_port_range_validation_valid(self):
        """Test port range validation with valid ranges."""
        filter_obj = ProxyFilter(port_range=(80, 8080))
        assert filter_obj.port_range == (80, 8080)

    def test_port_range_validation_invalid_range(self):
        """Test port range validation with invalid ranges."""
        with pytest.raises(ValidationError) as exc_info:
            ProxyFilter(port_range=(8080, 80))
        assert "Invalid port range" in str(exc_info.value)

    def test_port_range_validation_invalid_bounds(self):
        """Test port range validation with out-of-bounds values."""
        with pytest.raises(ValidationError) as exc_info:
            ProxyFilter(port_range=(0, 80))
        assert "Invalid port range" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            ProxyFilter(port_range=(80, 65536))
        assert "Invalid port range" in str(exc_info.value)

    def test_time_range_validation_valid(self):
        """Test time range validation with valid ranges."""
        before = datetime(2023, 1, 2, tzinfo=timezone.utc)
        after = datetime(2023, 1, 1, tzinfo=timezone.utc)
        filter_obj = ProxyFilter(checked_after=after, checked_before=before)
        assert filter_obj.checked_after == after
        assert filter_obj.checked_before == before

    def test_time_range_validation_invalid(self):
        """Test time range validation with invalid ranges."""
        before = datetime(2023, 1, 1, tzinfo=timezone.utc)
        after = datetime(2023, 1, 2, tzinfo=timezone.utc)
        with pytest.raises(ValidationError) as exc_info:
            ProxyFilter(checked_after=after, checked_before=before)
        assert "checked_after must be before checked_before" in str(exc_info.value)

    def test_numeric_field_constraints(self):
        """Test numeric field constraints."""
        # Valid ranges
        filter_obj = ProxyFilter(
            min_response_time=0.0,
            max_response_time=10.0,
            min_success_rate=0.0,
            min_quality_score=1.0,
            min_uptime=0.0,
        )
        assert filter_obj.min_response_time == 0.0
        assert filter_obj.min_success_rate == 0.0
        assert filter_obj.min_quality_score == 1.0

        # Invalid ranges
        with pytest.raises(ValidationError):
            ProxyFilter(min_response_time=-1.0)

        with pytest.raises(ValidationError):
            ProxyFilter(min_success_rate=1.5)

        with pytest.raises(ValidationError):
            ProxyFilter(min_uptime=-5.0)


class TestVolumeControl:
    """Test VolumeControl model."""

    def test_volume_control_creation_defaults(self):
        """Test VolumeControl creation with defaults."""
        volume = VolumeControl()
        assert volume.limit is None
        assert volume.offset is None
        assert volume.sampling_method == SamplingMethod.FIRST
        assert volume.sample_percentage is None
        assert volume.balanced_sources is False
        assert volume.sort_order == SortOrder.ASC

    def test_volume_control_creation_with_values(self):
        """Test VolumeControl creation with various values."""
        volume = VolumeControl(
            limit=100,
            offset=50,
            sampling_method=SamplingMethod.RANDOM,
            sample_percentage=10.0,
            max_per_source=20,
            max_per_country=30,
            balanced_sources=True,
            sort_by=SortField.RESPONSE_TIME,
            sort_order=SortOrder.DESC,
        )
        assert volume.limit == 100
        assert volume.offset == 50
        assert volume.sampling_method == SamplingMethod.RANDOM
        assert volume.sample_percentage == 10.0
        assert volume.max_per_source == 20
        assert volume.max_per_country == 30
        assert volume.balanced_sources is True
        assert volume.sort_by == SortField.RESPONSE_TIME
        assert volume.sort_order == SortOrder.DESC

    def test_volume_control_limit_constraints(self):
        """Test limit field constraints."""
        # Valid values
        VolumeControl(limit=1)
        VolumeControl(limit=10000)

        # Invalid values
        with pytest.raises(ValidationError):
            VolumeControl(limit=0)

        with pytest.raises(ValidationError):
            VolumeControl(limit=-1)

    def test_volume_control_offset_constraints(self):
        """Test offset field constraints."""
        # Valid values
        VolumeControl(offset=0)
        VolumeControl(offset=100)

        # Invalid values
        with pytest.raises(ValidationError):
            VolumeControl(offset=-1)

    def test_sampling_percentage_constraints(self):
        """Test sample_percentage field constraints."""
        # Valid values
        VolumeControl(sample_percentage=0.01)
        VolumeControl(sample_percentage=50.0)
        VolumeControl(sample_percentage=100.0)

        # Invalid values
        with pytest.raises(ValidationError):
            VolumeControl(sample_percentage=0.001)

        with pytest.raises(ValidationError):
            VolumeControl(sample_percentage=100.1)

    def test_sampling_validation_conflict(self):
        """Test sampling validation prevents conflicting options."""
        with pytest.raises(ValidationError) as exc_info:
            VolumeControl(limit=100, sample_percentage=50.0)
        assert "Cannot specify both sample_percentage and limit" in str(exc_info.value)


class TestOutputConfig:
    """Test OutputConfig model."""

    def test_output_config_creation_defaults(self):
        """Test OutputConfig creation with defaults."""
        output = OutputConfig()
        assert output.include_headers is True
        assert output.pretty_format is False
        assert output.csv_delimiter == ","
        assert output.csv_quote_char == '"'
        assert output.json_indent is None
        assert output.json_ensure_ascii is False
        assert output.xml_root_element == "proxies"
        assert output.xml_item_element == "proxy"
        assert output.xml_pretty is True
        assert output.txt_separator == "\n"
        assert output.sql_table_name == "proxies"
        assert output.sql_batch_size == 100
        assert output.pac_function_name == "FindProxyForURL"
        assert output.pac_proxy_type == "PROXY"

    def test_output_config_creation_with_values(self):
        """Test OutputConfig creation with custom values."""
        output = OutputConfig(
            include_headers=False,
            pretty_format=True,
            csv_delimiter="|",
            csv_quote_char="'",
            json_indent=4,
            json_ensure_ascii=True,
            xml_root_element="proxy_list",
            xml_item_element="entry",
            xml_pretty=False,
            txt_separator="\\n",
            sql_table_name="proxy_data",
            sql_batch_size=500,
            pac_function_name="CustomProxyFunction",
            pac_proxy_type="HTTP",
        )
        assert output.include_headers is False
        assert output.pretty_format is True
        assert output.csv_delimiter == "|"
        assert output.csv_quote_char == "'"
        assert output.json_indent == 4
        assert output.json_ensure_ascii is True
        assert output.xml_root_element == "proxy_list"
        assert output.xml_item_element == "entry"
        assert output.xml_pretty is False
        assert output.txt_separator == "\\n"
        assert output.sql_table_name == "proxy_data"
        assert output.sql_batch_size == 500
        assert output.pac_function_name == "CustomProxyFunction"
        assert output.pac_proxy_type == "HTTP"

    def test_csv_char_validation(self):
        """Test CSV character validation."""
        # Valid single characters
        OutputConfig(csv_delimiter=";", csv_quote_char="'")

        # Invalid multi-character strings
        with pytest.raises(ValidationError) as exc_info:
            OutputConfig(csv_delimiter="||")
        assert "single characters" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            OutputConfig(csv_quote_char="''")
        assert "single characters" in str(exc_info.value)


class TestExportConfig:
    """Test ExportConfig model."""

    def test_export_config_creation_defaults(self):
        """Test ExportConfig creation with defaults."""
        config = ExportConfig()
        assert config.format == ExportFormat.JSON
        assert config.filters is None
        assert config.volume is None
        assert isinstance(config.output, OutputConfig)
        assert config.include_metadata is True
        assert config.metadata_format == "comment"
        assert config.output_file is None
        assert config.overwrite is False

    def test_export_config_creation_with_values(self):
        """Test ExportConfig creation with custom values."""
        filters = ProxyFilter(countries=["US"])
        volume = VolumeControl(limit=100)
        output = OutputConfig(pretty_format=True)

        config = ExportConfig(
            format=ExportFormat.CSV,
            filters=filters,
            volume=volume,
            output=output,
            include_metadata=False,
            metadata_format="header",
            output_file="proxies.csv",
            overwrite=True,
        )
        assert config.format == ExportFormat.CSV
        assert config.filters == filters
        assert config.volume == volume
        assert config.output == output
        assert config.include_metadata is False
        assert config.metadata_format == "header"
        assert config.output_file == "proxies.csv"
        assert config.overwrite is True

    def test_format_config_validation_json_pretty(self):
        """Test format-specific configuration for JSON_PRETTY."""
        config = ExportConfig(format=ExportFormat.JSON_PRETTY)
        assert config.output.json_indent == 2
        assert config.output.pretty_format is True

    def test_format_config_validation_json_compact(self):
        """Test format-specific configuration for JSON_COMPACT."""
        config = ExportConfig(format=ExportFormat.JSON_COMPACT)
        assert config.output.json_indent is None
        assert config.output.pretty_format is False

    def test_format_config_validation_csv_no_headers(self):
        """Test format-specific configuration for CSV_NO_HEADERS."""
        config = ExportConfig(format=ExportFormat.CSV_NO_HEADERS)
        assert config.output.include_headers is False

    def test_export_config_serialization(self):
        """Test ExportConfig serialization and deserialization."""
        original = ExportConfig(
            format=ExportFormat.XML,
            filters=ProxyFilter(countries=["US", "CA"]),
            volume=VolumeControl(limit=50, sampling_method=SamplingMethod.RANDOM),
            output_file="test.xml",
        )

        # Serialize to dict
        data = original.model_dump()

        # Deserialize back
        recreated = ExportConfig(**data)

        assert recreated.format == original.format
        assert recreated.filters.countries == original.filters.countries
        assert recreated.volume.limit == original.volume.limit
        assert recreated.volume.sampling_method == original.volume.sampling_method
        assert recreated.output_file == original.output_file

    def test_export_config_edge_cases(self):
        """Test ExportConfig edge cases and boundary conditions."""
        # Complex configuration
        config = ExportConfig(
            format=ExportFormat.SQL_INSERT,
            filters=ProxyFilter(
                countries=["us", "gb", "ca"],  # Test lowercase normalization
                port_range=(1, 65535),  # Test boundary ports
                min_response_time=0.0,  # Test boundary response time
                max_response_time=30.0,
            ),
            volume=VolumeControl(
                limit=1,  # Test minimum limit
                sample_percentage=100.0,  # Test maximum percentage (should conflict)
                sort_by=SortField.QUALITY_SCORE,
                sort_order=SortOrder.DESC,
            ),
            output=OutputConfig(
                sql_table_name="custom_proxies",
                sql_batch_size=1,  # Test minimum batch size
            ),
        )

        # This should raise validation error due to conflicting limit and percentage
        with pytest.raises(ValidationError) as exc_info:
            # Need to trigger validation - the model is created but validation happens on access
            _ = config.model_dump()

        # Fix the conflict and test valid complex config
        config = ExportConfig(
            format=ExportFormat.SQL_INSERT,
            filters=ProxyFilter(
                countries=["us", "gb", "ca"],
                port_range=(1, 65535),
                min_response_time=0.0,
                max_response_time=30.0,
            ),
            volume=VolumeControl(
                limit=1000,
                sort_by=SortField.QUALITY_SCORE,
                sort_order=SortOrder.DESC,
            ),
            output=OutputConfig(
                sql_table_name="custom_proxies",
                sql_batch_size=50,
            ),
        )

        # Should work without errors
        data = config.model_dump()
        assert data["format"] == "sql_insert"
        assert data["filters"]["countries"] == ["US", "GB", "CA"]
