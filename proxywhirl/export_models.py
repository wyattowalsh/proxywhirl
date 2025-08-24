"""proxywhirl/export_models.py -- Export-specific models and enums

This module provides models for configuring proxy list exports including:
- Export formats (JSON, CSV, XML, TXT variants)
- Comprehensive filtering options based on proxy metadata
- Volume controls (limits, sampling, pagination)
- Output configuration options
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum, auto
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from .models import AnonymityLevel, ProxyStatus, Scheme


class ExportFormat(StrEnum):
    """Supported export formats for proxy lists."""

    # JSON variants
    JSON = auto()
    JSON_PRETTY = "json_pretty"
    JSON_COMPACT = "json_compact"

    # CSV variants
    CSV = auto()
    CSV_HEADERS = "csv_headers"
    CSV_NO_HEADERS = "csv_no_headers"

    # Text variants
    TXT_HOSTPORT = "txt_hostport"  # host:port format
    TXT_URI = "txt_uri"  # scheme://host:port format
    TXT_SIMPLE = "txt_simple"  # one proxy per line, minimal info
    TXT_DETAILED = "txt_detailed"  # detailed info per line

    # Structured formats
    XML = auto()
    YAML = auto()

    # Special formats
    SQL_INSERT = "sql_insert"
    PAC = "pac"  # Proxy Auto-Configuration


class SamplingMethod(StrEnum):
    """Methods for sampling proxy subsets."""

    FIRST = auto()  # Take first N proxies
    RANDOM = auto()  # Random sampling
    TOP_QUALITY = "top_quality"  # Best by quality_score
    TOP_SPEED = "top_speed"  # Best by response_time
    TOP_RELIABILITY = "top_reliability"  # Best by success_rate
    BALANCED = auto()  # Balanced across sources


class SortField(StrEnum):
    """Fields available for sorting proxy exports."""

    HOST = auto()
    PORT = auto()
    COUNTRY_CODE = "country_code"
    RESPONSE_TIME = "response_time"
    SUCCESS_RATE = "success_rate"
    QUALITY_SCORE = "quality_score"
    LAST_CHECKED = "last_checked"
    SOURCE = auto()
    ANONYMITY = auto()


class SortOrder(StrEnum):
    """Sort order options."""

    ASC = "asc"
    DESC = "desc"


class ProxyFilter(BaseModel):
    """Comprehensive filtering options for proxy exports."""

    # Geographic filters
    countries: Optional[List[str]] = Field(
        None, description="Filter by country codes (e.g., ['US', 'CA'])"
    )
    exclude_countries: Optional[List[str]] = Field(
        None, description="Exclude specific country codes"
    )
    cities: Optional[List[str]] = Field(None, description="Filter by cities")
    regions: Optional[List[str]] = Field(None, description="Filter by regions/states")

    # Technical filters
    schemes: Optional[List[Scheme]] = Field(None, description="Filter by proxy schemes")
    ports: Optional[List[int]] = Field(None, description="Filter by specific ports")
    port_range: Optional[tuple[int, int]] = Field(None, description="Port range filter (min, max)")
    anonymity_levels: Optional[List[AnonymityLevel]] = Field(
        None, description="Filter by anonymity levels"
    )

    # Performance filters
    min_response_time: Optional[float] = Field(
        None, ge=0.0, description="Minimum response time in seconds"
    )
    max_response_time: Optional[float] = Field(
        None, ge=0.0, description="Maximum response time in seconds"
    )
    min_success_rate: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Minimum success rate (0-1)"
    )
    min_quality_score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Minimum quality score (0-1)"
    )
    min_uptime: Optional[float] = Field(
        None, ge=0.0, le=100.0, description="Minimum uptime percentage"
    )

    # Status filters
    statuses: Optional[List[ProxyStatus]] = Field(None, description="Filter by proxy statuses")
    exclude_statuses: Optional[List[ProxyStatus]] = Field(
        None, description="Exclude specific statuses"
    )

    # Source filters
    sources: Optional[List[str]] = Field(None, description="Filter by loader/source names")
    exclude_sources: Optional[List[str]] = Field(None, description="Exclude specific sources")

    # Time-based filters
    checked_after: Optional[datetime] = Field(
        None, description="Only proxies checked after this time"
    )
    checked_before: Optional[datetime] = Field(
        None, description="Only proxies checked before this time"
    )
    success_after: Optional[datetime] = Field(
        None, description="Only proxies with success after this time"
    )

    # Health filters
    healthy_only: bool = Field(False, description="Only include healthy proxies")
    max_consecutive_failures: Optional[int] = Field(
        None, ge=0, description="Maximum consecutive failures allowed"
    )

    @field_validator("countries", "exclude_countries", mode="before")
    @classmethod
    def validate_country_codes(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate and normalize country codes."""
        if v is None:
            return None
        normalized = []
        for code in v:
            if len(code) != 2 or not code.isalpha():
                raise ValueError(f"Invalid country code: {code}. Must be 2 alphabetic characters.")
            normalized.append(code.upper())
        return normalized

    @field_validator("port_range")
    @classmethod
    def validate_port_range(cls, v: Optional[tuple[int, int]]) -> Optional[tuple[int, int]]:
        """Validate port range."""
        if v is None:
            return None
        min_port, max_port = v
        if min_port < 1 or max_port > 65535 or min_port > max_port:
            raise ValueError(
                "Invalid port range. Must be (min, max) where 1 <= min <= max <= 65535"
            )
        return v

    @model_validator(mode="after")
    def validate_time_ranges(self) -> ProxyFilter:
        """Validate time range consistency."""
        if self.checked_after and self.checked_before and self.checked_after >= self.checked_before:
            raise ValueError("checked_after must be before checked_before")
        return self


class VolumeControl(BaseModel):
    """Volume control options for proxy exports."""

    # Basic limits
    limit: Optional[int] = Field(None, ge=1, description="Maximum number of proxies to export")
    offset: Optional[int] = Field(None, ge=0, description="Number of proxies to skip (pagination)")

    # Sampling options
    sampling_method: SamplingMethod = Field(
        SamplingMethod.FIRST, description="Method for selecting proxies"
    )
    sample_percentage: Optional[float] = Field(
        None, ge=0.01, le=100.0, description="Percentage of total proxies to sample (1-100%)"
    )

    # Distribution controls
    max_per_source: Optional[int] = Field(
        None, ge=1, description="Maximum proxies per source/loader"
    )
    max_per_country: Optional[int] = Field(None, ge=1, description="Maximum proxies per country")
    balanced_sources: bool = Field(
        False, description="Ensure equal representation from each source"
    )

    # Sorting
    sort_by: Optional[SortField] = Field(None, description="Field to sort by")
    sort_order: SortOrder = Field(SortOrder.ASC, description="Sort order")

    @model_validator(mode="after")
    def validate_sampling(self) -> VolumeControl:
        """Validate sampling configuration."""
        if self.sample_percentage is not None and self.limit is not None:
            raise ValueError("Cannot specify both sample_percentage and limit")
        return self


class OutputConfig(BaseModel):
    """Configuration for export output formatting."""

    # General options
    include_headers: bool = True
    pretty_format: bool = False

    # CSV-specific options
    csv_delimiter: str = ","
    csv_quote_char: str = '"'
    csv_columns: Optional[List[str]] = None

    # JSON-specific options
    json_indent: Optional[int] = None
    json_ensure_ascii: bool = False

    # XML-specific options
    xml_root_element: str = "proxies"
    xml_item_element: str = "proxy"
    xml_pretty: bool = True

    # TXT-specific options
    txt_template: Optional[str] = None
    txt_separator: str = "\n"

    # SQL-specific options
    sql_table_name: str = "proxies"
    sql_batch_size: int = 100

    # PAC-specific options
    pac_function_name: str = "FindProxyForURL"
    pac_proxy_type: str = "PROXY"

    @field_validator("csv_delimiter", "csv_quote_char")
    @classmethod
    def validate_csv_chars(cls, v: str) -> str:
        """Validate CSV formatting characters."""
        if len(v) != 1:
            raise ValueError("CSV delimiter and quote character must be single characters")
        return v


class ExportConfig(BaseModel):
    """Complete export configuration combining all options."""

    # Configuration
    format: ExportFormat = ExportFormat.JSON
    filters: Optional[ProxyFilter] = None
    volume: Optional[VolumeControl] = None
    output: OutputConfig = OutputConfig()

    # Metadata options
    include_metadata: bool = Field(
        True, description="Include export metadata (timestamp, counts, etc.)"
    )
    metadata_format: str = Field(
        "comment", description="How to include metadata (comment, header, separate)"
    )

    # File output options
    output_file: Optional[str] = Field(None, description="Output file path (None for stdout)")
    overwrite: bool = Field(False, description="Allow overwriting existing output files")

    @model_validator(mode="after")
    def validate_format_config(self) -> ExportConfig:
        """Validate format-specific configurations."""
        # Adjust output config based on format
        if str(self.format).startswith("json"):
            if self.format == ExportFormat.JSON_PRETTY:
                self.output.json_indent = 2
                self.output.pretty_format = True
            elif self.format == ExportFormat.JSON_COMPACT:
                self.output.json_indent = None
                self.output.pretty_format = False

        elif str(self.format).startswith("csv"):
            if self.format == ExportFormat.CSV_NO_HEADERS:
                self.output.include_headers = False

        return self
