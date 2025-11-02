"""
Export manager for ProxyWhirl data export operations.

This module provides comprehensive export functionality for proxies, metrics,
logs, and configurations with support for multiple formats, compression,
filtering, and validation.
"""

import csv
import gzip
import io
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from uuid import UUID

import yaml
from loguru import logger
from pydantic import BaseModel

from proxywhirl.cache import CacheManager
from proxywhirl.exceptions import ProxyWhirlError
from proxywhirl.export_models import (
    CompressionType,
    ConfigurationExportFilter,
    ExportConfig,
    ExportDestination,
    ExportDestinationType,
    ExportFormat,
    ExportHistoryEntry,
    ExportJob,
    ExportMetadata,
    ExportProgress,
    ExportResult,
    ExportStatus,
    ExportType,
    HTTPDestination,
    LocalFileDestination,
    LogExportFilter,
    MemoryDestination,
    MetricsExportFilter,
    ProxyExportFilter,
    S3Destination,
)
from proxywhirl.models import Proxy, ProxyPool
from proxywhirl.storage import SQLiteStorage


# ============================================================================
# EXCEPTIONS
# ============================================================================


class ExportError(ProxyWhirlError):
    """Base exception for export errors."""

    pass


class ExportValidationError(ExportError):
    """Raised when export validation fails."""

    pass


class ExportDestinationError(ExportError):
    """Raised when export destination is inaccessible."""

    pass


class ExportFormatError(ExportError):
    """Raised when export format is invalid or unsupported."""

    pass


# ============================================================================
# EXPORT MANAGER
# ============================================================================


class ExportManager:
    """
    Manager for data export operations.
    
    Handles exporting proxy lists, metrics, logs, and configurations in multiple
    formats with filtering, compression, validation, and progress tracking.
    
    Example:
        ```python
        from proxywhirl import ExportManager, ProxyPool
        from proxywhirl.export_models import (
            ExportConfig, ExportType, ExportFormat,
            LocalFileDestination, ProxyExportFilter
        )
        
        manager = ExportManager(proxy_pool=pool)
        
        # Export proxies to CSV
        config = ExportConfig(
            export_type=ExportType.PROXIES,
            export_format=ExportFormat.CSV,
            destination=LocalFileDestination(file_path="proxies.csv"),
            proxy_filter=ProxyExportFilter(health_status=["healthy"])
        )
        
        result = manager.export(config)
        print(f"Exported {result.records_exported} proxies")
        ```
    """

    def __init__(
        self,
        proxy_pool: Optional[ProxyPool] = None,
        storage: Optional[SQLiteStorage] = None,
        cache_manager: Optional[CacheManager] = None,
        history_file: Optional[Path] = None,
    ) -> None:
        """
        Initialize ExportManager.
        
        Args:
            proxy_pool: Proxy pool for proxy exports
            storage: Storage backend for persistent data
            cache_manager: Cache manager for cache data exports
            history_file: File to store export history (optional)
        """
        self.proxy_pool        = proxy_pool
        self.storage           = storage
        self.cache_manager     = cache_manager
        self.history_file      = history_file or Path(".proxywhirl/export_history.jsonl")
        
        # Active jobs
        self._active_jobs: dict[UUID, ExportJob] = {}
        
        # Ensure history directory exists
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

    # ========================================================================
    # PUBLIC API
    # ========================================================================

    def export(self, config: ExportConfig) -> ExportResult:
        """
        Execute an export operation.
        
        Args:
            config: Export configuration
            
        Returns:
            ExportResult with export details and status
            
        Raises:
            ExportError: If export fails
        """
        # Create job
        job = ExportJob(config=config)
        self._active_jobs[job.job_id] = job
        
        try:
            # Update status
            job.status     = ExportStatus.RUNNING
            job.started_at = datetime.now(timezone.utc)
            
            logger.info(f"Starting export job {job.job_id}: {config.export_type.value} -> {config.export_format.value}")
            
            # Validate configuration
            if config.validate_before_export:
                self._validate_config(config)
            
            # Export data based on type
            if config.export_type == ExportType.PROXIES:
                data = self._export_proxies(config, job)
            elif config.export_type == ExportType.METRICS:
                data = self._export_metrics(config, job)
            elif config.export_type == ExportType.LOGS:
                data = self._export_logs(config, job)
            elif config.export_type == ExportType.CONFIGURATION:
                data = self._export_configuration(config, job)
            elif config.export_type == ExportType.HEALTH_STATUS:
                data = self._export_health_status(config, job)
            elif config.export_type == ExportType.CACHE_DATA:
                data = self._export_cache_data(config, job)
            else:
                raise ExportError(f"Unsupported export type: {config.export_type}")
            
            # Format data
            formatted_data = self._format_data(data, config, job)
            
            # Compress if needed
            if config.compression != CompressionType.NONE:
                formatted_data = self._compress_data(formatted_data, config.compression)
            
            # Write to destination
            destination_path = self._write_to_destination(formatted_data, config, job)
            
            # Update job status
            job.status       = ExportStatus.COMPLETED
            job.completed_at = datetime.now(timezone.utc)
            job.result_path  = destination_path if isinstance(config.destination, LocalFileDestination) else None
            job.result_data  = data if isinstance(config.destination, MemoryDestination) else None
            
            # Create metadata
            job.metadata = self._create_metadata(config, job, len(formatted_data) if isinstance(formatted_data, bytes) else 0)
            
            # Create result
            result = ExportResult(
                success           = True,
                job_id            = job.job_id,
                export_type       = config.export_type,
                export_format     = config.export_format,
                destination_path  = destination_path,
                data              = job.result_data,
                records_exported  = job.progress.processed_records,
                file_size_bytes   = job.metadata.file_size_bytes,
                duration_seconds  = job.duration_seconds or 0.0,
                metadata          = job.metadata,
            )
            
            # Save to history
            self._save_to_history(job)
            
            logger.info(f"Export job {job.job_id} completed successfully: {result.records_exported} records")
            
            return result
            
        except Exception as e:
            # Update job with error
            job.status         = ExportStatus.FAILED
            job.completed_at   = datetime.now(timezone.utc)
            job.error_message  = str(e)
            
            # Save to history
            self._save_to_history(job)
            
            logger.error(f"Export job {job.job_id} failed: {e}")
            
            # Create error result
            result = ExportResult(
                success           = False,
                job_id            = job.job_id,
                export_type       = config.export_type,
                export_format     = config.export_format,
                records_exported  = job.progress.processed_records,
                duration_seconds  = job.duration_seconds or 0.0,
                error             = str(e),
            )
            
            raise ExportError(f"Export failed: {e}") from e
            
        finally:
            # Remove from active jobs
            self._active_jobs.pop(job.job_id, None)

    def get_job_status(self, job_id: UUID) -> Optional[ExportJob]:
        """
        Get status of an export job.
        
        Args:
            job_id: Job ID to query
            
        Returns:
            ExportJob if found, None otherwise
        """
        return self._active_jobs.get(job_id)

    def get_export_history(self, limit: int = 100) -> list[ExportHistoryEntry]:
        """
        Get export history.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of export history entries
        """
        if not self.history_file.exists():
            return []
        
        history: list[ExportHistoryEntry] = []
        
        with open(self.history_file, "r") as f:
            for line in f:
                if line.strip():
                    try:
                        entry = ExportHistoryEntry.model_validate_json(line)
                        history.append(entry)
                    except Exception as e:
                        logger.warning(f"Failed to parse history entry: {e}")
        
        # Return most recent entries
        return history[-limit:]

    # ========================================================================
    # EXPORT IMPLEMENTATIONS
    # ========================================================================

    def _export_proxies(self, config: ExportConfig, job: ExportJob) -> list[dict[str, Any]]:
        """Export proxy data."""
        if not self.proxy_pool:
            raise ExportError("No proxy pool configured")
        
        proxy_filter = config.proxy_filter or ProxyExportFilter()
        
        # Get proxies
        proxies = self.proxy_pool.proxies
        
        # Apply filters
        filtered_proxies = self._apply_proxy_filters(proxies, proxy_filter)
        
        # Update progress
        job.progress.total_records = len(filtered_proxies)
        job.progress.current_phase = "exporting"
        
        # Convert to dict
        proxy_data: list[dict[str, Any]] = []
        for proxy in filtered_proxies:
            proxy_dict = self._proxy_to_dict(proxy, proxy_filter)
            proxy_data.append(proxy_dict)
            job.progress.processed_records += 1
        
        return proxy_data

    def _export_metrics(self, config: ExportConfig, job: ExportJob) -> list[dict[str, Any]]:
        """Export metrics data."""
        metrics_filter = config.metrics_filter
        
        if not metrics_filter:
            raise ExportError("Metrics filter required for metrics export")
        
        # Placeholder: In a real implementation, this would query a metrics backend
        # For now, return basic system metrics
        job.progress.total_records = 1
        job.progress.current_phase = "exporting"
        
        metrics_data = [{
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "start_time": metrics_filter.start_time.isoformat(),
            "end_time": metrics_filter.end_time.isoformat(),
            "metrics": {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "average_response_time_ms": 0.0,
            }
        }]
        
        job.progress.processed_records = 1
        
        return metrics_data

    def _export_logs(self, config: ExportConfig, job: ExportJob) -> list[dict[str, Any]]:
        """Export log data."""
        log_filter = config.log_filter or LogExportFilter()
        
        # Placeholder: In a real implementation, this would read from log files
        job.progress.total_records = 0
        job.progress.current_phase = "exporting"
        
        log_data: list[dict[str, Any]] = []
        
        # Return placeholder data
        logger.info("Log export is a placeholder - implement log file reading")
        
        return log_data

    def _export_configuration(self, config: ExportConfig, job: ExportJob) -> dict[str, Any]:
        """Export configuration data."""
        config_filter = config.config_filter or ConfigurationExportFilter()
        
        job.progress.total_records = 1
        job.progress.current_phase = "exporting"
        
        # Build configuration dict
        config_data: dict[str, Any] = {
            "proxywhirl_version": "1.0.0",
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }
        
        # Add proxy pool config
        if self.proxy_pool:
            pool_config = {
                "name": self.proxy_pool.name,
                "proxy_count": len(self.proxy_pool.proxies),
                "proxies": [p.url for p in self.proxy_pool.proxies] if not config_filter.redact_secrets else []
            }
            config_data["proxy_pool"] = pool_config
        
        # Redact secrets if requested
        if config_filter.redact_secrets:
            config_data = self._redact_secrets(config_data)
        
        job.progress.processed_records = 1
        
        return config_data

    def _export_health_status(self, config: ExportConfig, job: ExportJob) -> list[dict[str, Any]]:
        """Export health status data."""
        if not self.proxy_pool:
            raise ExportError("No proxy pool configured")
        
        job.progress.total_records = len(self.proxy_pool.proxies)
        job.progress.current_phase = "exporting"
        
        health_data: list[dict[str, Any]] = []
        
        for proxy in self.proxy_pool.proxies:
            health_entry = {
                "url": proxy.url,
                "health_status": proxy.health_status.value,
                "total_requests": proxy.total_requests,
                "total_successes": proxy.total_successes,
                "total_failures": proxy.total_failures,
                "success_rate": proxy.success_rate,
                "consecutive_failures": proxy.consecutive_failures,
                "average_response_time_ms": proxy.average_response_time_ms,
                "last_success_at": proxy.last_success_at.isoformat() if proxy.last_success_at else None,
                "last_failure_at": proxy.last_failure_at.isoformat() if proxy.last_failure_at else None,
            }
            health_data.append(health_entry)
            job.progress.processed_records += 1
        
        return health_data

    def _export_cache_data(self, config: ExportConfig, job: ExportJob) -> dict[str, Any]:
        """Export cache data."""
        if not self.cache_manager:
            raise ExportError("No cache manager configured")
        
        job.progress.total_records = 1
        job.progress.current_phase = "exporting"
        
        # Get cache statistics
        stats = self.cache_manager.get_statistics()
        
        cache_data = {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "statistics": {
                "total_entries": stats.total_entries,
                "l1_entries": stats.l1_entries,
                "l2_entries": stats.l2_entries,
                "l3_entries": stats.l3_entries,
                "total_hits": stats.total_hits,
                "total_misses": stats.total_misses,
                "hit_rate": stats.hit_rate,
            }
        }
        
        job.progress.processed_records = 1
        
        return cache_data

    # ========================================================================
    # FILTERING
    # ========================================================================

    def _apply_proxy_filters(
        self,
        proxies: list[Proxy],
        proxy_filter: ProxyExportFilter,
    ) -> list[Proxy]:
        """Apply filters to proxy list."""
        filtered = proxies
        
        # Health status filter
        if proxy_filter.health_status:
            filtered = [p for p in filtered if p.health_status.value in proxy_filter.health_status]
        
        # Source filter
        if proxy_filter.source:
            filtered = [p for p in filtered if p.source.value in proxy_filter.source]
        
        # Protocol filter
        if proxy_filter.protocol:
            filtered = [p for p in filtered if p.protocol in proxy_filter.protocol]
        
        # Success rate filter
        if proxy_filter.min_success_rate is not None:
            filtered = [p for p in filtered if p.success_rate >= proxy_filter.min_success_rate]
        
        # Response time filter
        if proxy_filter.max_response_time_ms is not None:
            filtered = [
                p for p in filtered
                if p.average_response_time_ms is not None and p.average_response_time_ms <= proxy_filter.max_response_time_ms
            ]
        
        # Request count filter
        if proxy_filter.min_requests is not None:
            filtered = [p for p in filtered if p.total_requests >= proxy_filter.min_requests]
        
        # Time filters
        if proxy_filter.created_after:
            filtered = [p for p in filtered if p.created_at >= proxy_filter.created_after]
        
        if proxy_filter.created_before:
            filtered = [p for p in filtered if p.created_at <= proxy_filter.created_before]
        
        if proxy_filter.last_success_after and hasattr(filtered[0] if filtered else None, 'last_success_at'):
            filtered = [
                p for p in filtered
                if p.last_success_at and p.last_success_at >= proxy_filter.last_success_after
            ]
        
        return filtered

    # ========================================================================
    # FORMATTING
    # ========================================================================

    def _format_data(
        self,
        data: Any,
        config: ExportConfig,
        job: ExportJob,
    ) -> bytes:
        """Format data according to export format."""
        job.progress.current_phase = "formatting"
        
        if config.export_format == ExportFormat.JSON:
            return self._format_json(data, config.pretty_print)
        elif config.export_format == ExportFormat.JSONL:
            return self._format_jsonl(data)
        elif config.export_format == ExportFormat.CSV:
            return self._format_csv(data)
        elif config.export_format == ExportFormat.YAML:
            return self._format_yaml(data)
        elif config.export_format == ExportFormat.TEXT:
            return self._format_text(data)
        elif config.export_format == ExportFormat.MARKDOWN:
            return self._format_markdown(data)
        else:
            raise ExportFormatError(f"Unsupported format: {config.export_format}")

    def _format_json(self, data: Any, pretty: bool) -> bytes:
        """Format data as JSON."""
        if pretty:
            json_str = json.dumps(data, indent=2, default=str)
        else:
            json_str = json.dumps(data, default=str)
        return json_str.encode("utf-8")

    def _format_jsonl(self, data: Any) -> bytes:
        """Format data as JSON Lines."""
        if isinstance(data, list):
            lines = [json.dumps(item, default=str) for item in data]
        else:
            lines = [json.dumps(data, default=str)]
        return "\n".join(lines).encode("utf-8")

    def _format_csv(self, data: Any) -> bytes:
        """Format data as CSV."""
        output = io.StringIO()
        
        if isinstance(data, list) and len(data) > 0:
            # Get fieldnames from first item
            if isinstance(data[0], dict):
                fieldnames = list(data[0].keys())
            else:
                fieldnames = ["value"]
                data = [{"value": item} for item in data]
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        elif isinstance(data, dict):
            # Single dict - write as two-column CSV (key, value)
            writer = csv.writer(output)
            writer.writerow(["key", "value"])
            for key, value in data.items():
                writer.writerow([key, value])
        
        return output.getvalue().encode("utf-8")

    def _format_yaml(self, data: Any) -> bytes:
        """Format data as YAML."""
        yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False)
        return yaml_str.encode("utf-8")

    def _format_text(self, data: Any) -> bytes:
        """Format data as plain text."""
        if isinstance(data, list):
            lines = [str(item) for item in data]
            return "\n".join(lines).encode("utf-8")
        else:
            return str(data).encode("utf-8")

    def _format_markdown(self, data: Any) -> bytes:
        """Format data as Markdown table."""
        lines: list[str] = []
        
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            # Table format
            fieldnames = list(data[0].keys())
            
            # Header
            lines.append("| " + " | ".join(fieldnames) + " |")
            lines.append("| " + " | ".join(["---"] * len(fieldnames)) + " |")
            
            # Rows
            for item in data:
                row_values = [str(item.get(field, "")) for field in fieldnames]
                lines.append("| " + " | ".join(row_values) + " |")
        else:
            # Simple list or dict
            lines.append("```")
            lines.append(json.dumps(data, indent=2, default=str))
            lines.append("```")
        
        return "\n".join(lines).encode("utf-8")

    # ========================================================================
    # COMPRESSION
    # ========================================================================

    def _compress_data(self, data: bytes, compression: CompressionType) -> bytes:
        """Compress data."""
        if compression == CompressionType.GZIP:
            return gzip.compress(data)
        elif compression == CompressionType.ZIP:
            output = io.BytesIO()
            with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("export.dat", data)
            return output.getvalue()
        else:
            return data

    # ========================================================================
    # DESTINATION HANDLING
    # ========================================================================

    def _write_to_destination(
        self,
        data: bytes,
        config: ExportConfig,
        job: ExportJob,
    ) -> Optional[str]:
        """Write data to destination."""
        job.progress.current_phase = "writing"
        
        destination = config.destination
        
        if isinstance(destination, LocalFileDestination):
            return self._write_to_local_file(data, destination)
        elif isinstance(destination, MemoryDestination):
            return None  # Data stored in job.result_data
        elif isinstance(destination, S3Destination):
            return self._write_to_s3(data, destination)
        elif isinstance(destination, HTTPDestination):
            return self._write_to_http(data, destination)
        else:
            raise ExportDestinationError(f"Unsupported destination type: {type(destination)}")

    def _write_to_local_file(self, data: bytes, destination: LocalFileDestination) -> str:
        """Write data to local file."""
        file_path = Path(destination.file_path)
        
        # Create directories if needed
        if destination.create_directories:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if file exists
        if file_path.exists() and not destination.overwrite:
            raise ExportDestinationError(f"File already exists: {file_path}")
        
        # Write file
        with open(file_path, "wb") as f:
            f.write(data)
        
        logger.info(f"Exported data to {file_path} ({len(data)} bytes)")
        
        return str(file_path.absolute())

    def _write_to_s3(self, data: bytes, destination: S3Destination) -> str:
        """Write data to S3."""
        # Placeholder: In a real implementation, use boto3
        raise ExportDestinationError("S3 export not yet implemented")

    def _write_to_http(self, data: bytes, destination: HTTPDestination) -> str:
        """Write data to HTTP endpoint."""
        # Placeholder: In a real implementation, use httpx
        raise ExportDestinationError("HTTP export not yet implemented")

    # ========================================================================
    # HELPERS
    # ========================================================================

    def _validate_config(self, config: ExportConfig) -> None:
        """Validate export configuration."""
        # Validate filters match export type
        if config.export_type == ExportType.PROXIES and not config.proxy_filter:
            pass  # Proxy filter is optional
        elif config.export_type == ExportType.METRICS and not config.metrics_filter:
            raise ExportValidationError("Metrics filter required for metrics export")

    def _proxy_to_dict(self, proxy: Proxy, proxy_filter: ProxyExportFilter) -> dict[str, Any]:
        """Convert proxy to dictionary with field selection."""
        proxy_dict = {
            "url": proxy.url,
            "protocol": proxy.protocol,
            "host": proxy.host,
            "port": proxy.port,
            "health_status": proxy.health_status.value,
            "source": proxy.source.value,
            "total_requests": proxy.total_requests,
            "total_successes": proxy.total_successes,
            "total_failures": proxy.total_failures,
            "success_rate": proxy.success_rate,
            "consecutive_failures": proxy.consecutive_failures,
            "average_response_time_ms": proxy.average_response_time_ms,
            "last_success_at": proxy.last_success_at.isoformat() if proxy.last_success_at else None,
            "last_failure_at": proxy.last_failure_at.isoformat() if proxy.last_failure_at else None,
            "created_at": proxy.created_at.isoformat(),
        }
        
        # Apply field selection
        if proxy_filter.include_fields:
            proxy_dict = {k: v for k, v in proxy_dict.items() if k in proxy_filter.include_fields}
        
        if proxy_filter.exclude_fields:
            proxy_dict = {k: v for k, v in proxy_dict.items() if k not in proxy_filter.exclude_fields}
        
        return proxy_dict

    def _redact_secrets(self, data: dict[str, Any]) -> dict[str, Any]:
        """Redact sensitive values from configuration."""
        sensitive_keys = ["password", "api_key", "secret", "token", "credential", "auth"]
        
        def redact_dict(d: dict[str, Any]) -> dict[str, Any]:
            result = {}
            for key, value in d.items():
                # Check if key contains sensitive term
                if any(term in key.lower() for term in sensitive_keys):
                    result[key] = "***REDACTED***"
                elif isinstance(value, dict):
                    result[key] = redact_dict(value)
                elif isinstance(value, list):
                    result[key] = [redact_dict(item) if isinstance(item, dict) else item for item in value]
                else:
                    result[key] = value
            return result
        
        return redact_dict(data)

    def _create_metadata(
        self,
        config: ExportConfig,
        job: ExportJob,
        file_size: int,
    ) -> ExportMetadata:
        """Create export metadata."""
        filters_applied = {}
        
        if config.proxy_filter:
            filters_applied["proxy"] = config.proxy_filter.model_dump(exclude_none=True)
        if config.metrics_filter:
            filters_applied["metrics"] = config.metrics_filter.model_dump(exclude_none=True)
        if config.log_filter:
            filters_applied["log"] = config.log_filter.model_dump(exclude_none=True)
        if config.config_filter:
            filters_applied["config"] = config.config_filter.model_dump(exclude_none=True)
        
        return ExportMetadata(
            export_id         = job.job_id,
            export_type       = config.export_type,
            export_format     = config.export_format,
            total_records     = job.progress.processed_records,
            file_size_bytes   = file_size,
            compression_used  = config.compression,
            filters_applied   = filters_applied if filters_applied else None,
        )

    def _save_to_history(self, job: ExportJob) -> None:
        """Save job to export history."""
        try:
            history_entry = ExportHistoryEntry(
                job_id            = job.job_id,
                export_type       = job.config.export_type,
                export_format     = job.config.export_format,
                status            = job.status,
                created_at        = job.created_at,
                completed_at      = job.completed_at,
                duration_seconds  = job.duration_seconds,
                records_exported  = job.progress.processed_records,
                file_size_bytes   = job.metadata.file_size_bytes if job.metadata else None,
                destination_path  = job.result_path,
                error             = job.error_message,
            )
            
            with open(self.history_file, "a") as f:
                f.write(history_entry.model_dump_json() + "\n")
                
        except Exception as e:
            logger.warning(f"Failed to save export history: {e}")
