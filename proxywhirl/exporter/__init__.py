"""proxywhirl/exporter -- Comprehensive proxy list export functionality

This package provides advanced proxy list export capabilities with multiple formats,
sophisticated filtering, volume controls, and extensive formatting options.

Features:
- Multiple export formats: JSON, CSV, XML, TXT variants, YAML, SQL, PAC
- Comprehensive filtering by geography, performance, status, and metadata
- Volume controls including sampling, limits, pagination, and distribution
- Async-first design consistent with ProxyWhirl architecture
- Extensible format handler system for custom formats

Classes:
- ProxyExporter: Main export functionality
- ExportConfig: Complete export configuration
- ExportFormat: Supported output formats
- ProxyFilter: Filtering criteria
- VolumeControl: Volume and sampling controls
- OutputConfig: Format-specific output options

Usage:
    from proxywhirl.exporter import ProxyExporter, ExportConfig, ExportFormat
    
    exporter = ProxyExporter()
    config = ExportConfig(format=ExportFormat.JSON_PRETTY)
    result = exporter.export(proxies, config)
"""

from .core import ProxyExporter, ProxyExportError
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

__all__ = [
    # Main exporter class
    "ProxyExporter",
    "ProxyExportError",
    # Configuration models
    "ExportConfig",
    "ExportFormat",
    "OutputConfig", 
    "ProxyFilter",
    "SamplingMethod",
    "SortField",
    "SortOrder",
    "VolumeControl",
]
