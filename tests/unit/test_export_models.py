"""Unit tests for export data models."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

from proxywhirl.export_models import (
    CompressionType,
    ConfigurationExportFilter,
    ExportConfig,
    ExportDestinationType,
    ExportFormat,
    ExportHistoryEntry,
    ExportJob,
    ExportMetadata,
    ExportProgress,
    ExportResult,
    ExportStatus,
    ExportType,
    LocalFileDestination,
    LogExportFilter,
    MemoryDestination,
    MetricsExportFilter,
    ProxyExportFilter,
)


class TestProxyExportFilter:
    """Tests for ProxyExportFilter model."""

    def test_create_empty_filter(self) -> None:
        """Test creating filter with no criteria."""
        filter_obj = ProxyExportFilter()
        
        assert filter_obj.health_status is None
        assert filter_obj.source is None
        assert filter_obj.min_success_rate is None

    def test_create_with_health_status_filter(self) -> None:
        """Test creating filter with health status criteria."""
        filter_obj = ProxyExportFilter(
            health_status=["healthy", "degraded"]
        )
        
        assert filter_obj.health_status == ["healthy", "degraded"]

    def test_create_with_success_rate_filter(self) -> None:
        """Test creating filter with success rate criteria."""
        filter_obj = ProxyExportFilter(min_success_rate=0.8)
        
        assert filter_obj.min_success_rate == 0.8

    def test_success_rate_validation_min(self) -> None:
        """Test success rate must be >= 0.0."""
        with pytest.raises(ValidationError):
            ProxyExportFilter(min_success_rate=-0.1)

    def test_success_rate_validation_max(self) -> None:
        """Test success rate must be <= 1.0."""
        with pytest.raises(ValidationError):
            ProxyExportFilter(min_success_rate=1.1)

    def test_field_selection(self) -> None:
        """Test field include/exclude options."""
        filter_obj = ProxyExportFilter(
            include_fields=["url", "health_status"],
            exclude_fields=["credentials"]
        )
        
        assert filter_obj.include_fields == ["url", "health_status"]
        assert filter_obj.exclude_fields == ["credentials"]


class TestMetricsExportFilter:
    """Tests for MetricsExportFilter model."""

    def test_create_with_time_range(self) -> None:
        """Test creating filter with time range."""
        start = datetime.now(timezone.utc) - timedelta(hours=1)
        end = datetime.now(timezone.utc)
        
        filter_obj = MetricsExportFilter(start_time=start, end_time=end)
        
        assert filter_obj.start_time == start
        assert filter_obj.end_time == end

    def test_time_range_validation(self) -> None:
        """Test end_time must be after start_time."""
        now = datetime.now(timezone.utc)
        
        with pytest.raises(ValidationError) as exc_info:
            MetricsExportFilter(start_time=now, end_time=now - timedelta(hours=1))
        
        assert "end_time must be after start_time" in str(exc_info.value)

    def test_with_metric_names(self) -> None:
        """Test creating filter with specific metric names."""
        start = datetime.now(timezone.utc) - timedelta(hours=1)
        end = datetime.now(timezone.utc)
        
        filter_obj = MetricsExportFilter(
            start_time=start,
            end_time=end,
            metric_names=["requests_total", "response_time"],
        )
        
        assert filter_obj.metric_names == ["requests_total", "response_time"]


class TestLogExportFilter:
    """Tests for LogExportFilter model."""

    def test_create_with_log_levels(self) -> None:
        """Test creating filter with log level criteria."""
        filter_obj = LogExportFilter(log_levels=["ERROR", "CRITICAL"])
        
        assert filter_obj.log_levels == ["ERROR", "CRITICAL"]

    def test_create_with_search_text(self) -> None:
        """Test creating filter with search text."""
        filter_obj = LogExportFilter(search_text="connection failed")
        
        assert filter_obj.search_text == "connection failed"

    def test_create_with_max_entries(self) -> None:
        """Test creating filter with entry limit."""
        filter_obj = LogExportFilter(max_entries=1000)
        
        assert filter_obj.max_entries == 1000


class TestConfigurationExportFilter:
    """Tests for ConfigurationExportFilter model."""

    def test_default_redact_secrets(self) -> None:
        """Test secrets are redacted by default."""
        filter_obj = ConfigurationExportFilter()
        
        assert filter_obj.redact_secrets is True

    def test_disable_secret_redaction(self) -> None:
        """Test disabling secret redaction."""
        filter_obj = ConfigurationExportFilter(redact_secrets=False)
        
        assert filter_obj.redact_secrets is False

    def test_section_selection(self) -> None:
        """Test section include/exclude."""
        filter_obj = ConfigurationExportFilter(
            include_sections=["proxy_pool", "rotation"],
            exclude_sections=["credentials"],
        )
        
        assert filter_obj.include_sections == ["proxy_pool", "rotation"]
        assert filter_obj.exclude_sections == ["credentials"]


class TestDestinationModels:
    """Tests for export destination models."""

    def test_local_file_destination(self) -> None:
        """Test LocalFileDestination model."""
        dest = LocalFileDestination(
            file_path=Path("/tmp/export.csv"),
            overwrite=True,
        )
        
        assert dest.type == ExportDestinationType.LOCAL_FILE
        assert dest.file_path == Path("/tmp/export.csv")
        assert dest.overwrite is True
        assert dest.create_directories is True

    def test_memory_destination(self) -> None:
        """Test MemoryDestination model."""
        dest = MemoryDestination()
        
        assert dest.type == ExportDestinationType.MEMORY


class TestExportConfig:
    """Tests for ExportConfig model."""

    def test_create_basic_export_config(self) -> None:
        """Test creating basic export configuration."""
        config = ExportConfig(
            export_type=ExportType.PROXIES,
            export_format=ExportFormat.CSV,
            destination=LocalFileDestination(file_path=Path("/tmp/proxies.csv")),
        )
        
        assert config.export_type == ExportType.PROXIES
        assert config.export_format == ExportFormat.CSV
        assert config.compression == CompressionType.NONE
        assert config.pretty_print is True

    def test_create_with_compression(self) -> None:
        """Test creating config with compression."""
        config = ExportConfig(
            export_type=ExportType.PROXIES,
            export_format=ExportFormat.JSON,
            destination=LocalFileDestination(file_path=Path("/tmp/proxies.json.gz")),
            compression=CompressionType.GZIP,
        )
        
        assert config.compression == CompressionType.GZIP

    def test_create_with_filters(self) -> None:
        """Test creating config with filters."""
        proxy_filter = ProxyExportFilter(health_status=["healthy"])
        
        config = ExportConfig(
            export_type=ExportType.PROXIES,
            export_format=ExportFormat.JSON,
            destination=MemoryDestination(),
            proxy_filter=proxy_filter,
        )
        
        assert config.proxy_filter == proxy_filter


class TestExportProgress:
    """Tests for ExportProgress model."""

    def test_progress_percentage_zero_records(self) -> None:
        """Test progress percentage with zero total records."""
        progress = ExportProgress(total_records=0, processed_records=0)
        
        assert progress.progress_percentage == 0.0

    def test_progress_percentage_partial(self) -> None:
        """Test progress percentage calculation."""
        progress = ExportProgress(total_records=100, processed_records=50)
        
        assert progress.progress_percentage == 50.0

    def test_progress_percentage_complete(self) -> None:
        """Test progress percentage at 100%."""
        progress = ExportProgress(total_records=100, processed_records=100)
        
        assert progress.progress_percentage == 100.0


class TestExportJob:
    """Tests for ExportJob model."""

    def test_create_export_job(self) -> None:
        """Test creating an export job."""
        config = ExportConfig(
            export_type=ExportType.PROXIES,
            export_format=ExportFormat.CSV,
            destination=LocalFileDestination(file_path=Path("/tmp/proxies.csv")),
        )
        
        job = ExportJob(config=config)
        
        assert job.status == ExportStatus.PENDING
        assert isinstance(job.job_id, type(uuid4()))
        assert job.started_at is None
        assert job.completed_at is None

    def test_job_duration_not_started(self) -> None:
        """Test duration calculation when job not started."""
        config = ExportConfig(
            export_type=ExportType.PROXIES,
            export_format=ExportFormat.CSV,
            destination=MemoryDestination(),
        )
        
        job = ExportJob(config=config)
        
        assert job.duration_seconds is None

    def test_job_duration_in_progress(self) -> None:
        """Test duration calculation for running job."""
        config = ExportConfig(
            export_type=ExportType.PROXIES,
            export_format=ExportFormat.CSV,
            destination=MemoryDestination(),
        )
        
        job = ExportJob(config=config)
        job.started_at = datetime.now(timezone.utc) - timedelta(seconds=5)
        
        duration = job.duration_seconds
        assert duration is not None
        assert duration >= 5.0

    def test_job_duration_completed(self) -> None:
        """Test duration calculation for completed job."""
        config = ExportConfig(
            export_type=ExportType.PROXIES,
            export_format=ExportFormat.CSV,
            destination=MemoryDestination(),
        )
        
        job = ExportJob(config=config)
        job.started_at = datetime.now(timezone.utc) - timedelta(seconds=10)
        job.completed_at = datetime.now(timezone.utc)
        
        duration = job.duration_seconds
        assert duration is not None
        assert 9.0 <= duration <= 11.0


class TestExportResult:
    """Tests for ExportResult model."""

    def test_create_successful_result(self) -> None:
        """Test creating successful export result."""
        job_id = uuid4()
        
        result = ExportResult(
            success=True,
            job_id=job_id,
            export_type=ExportType.PROXIES,
            export_format=ExportFormat.CSV,
            records_exported=100,
            duration_seconds=5.0,
        )
        
        assert result.success is True
        assert result.job_id == job_id
        assert result.records_exported == 100
        assert result.error is None

    def test_create_failed_result(self) -> None:
        """Test creating failed export result."""
        job_id = uuid4()
        
        result = ExportResult(
            success=False,
            job_id=job_id,
            export_type=ExportType.PROXIES,
            export_format=ExportFormat.CSV,
            records_exported=0,
            duration_seconds=1.0,
            error="Export failed due to invalid configuration",
        )
        
        assert result.success is False
        assert result.error == "Export failed due to invalid configuration"


class TestExportMetadata:
    """Tests for ExportMetadata model."""

    def test_create_metadata(self) -> None:
        """Test creating export metadata."""
        metadata = ExportMetadata(
            export_type=ExportType.PROXIES,
            export_format=ExportFormat.JSON,
            total_records=100,
            file_size_bytes=5000,
        )
        
        assert isinstance(metadata.export_id, type(uuid4()))
        assert metadata.export_type == ExportType.PROXIES
        assert metadata.total_records == 100
        assert metadata.compression_used == CompressionType.NONE


class TestExportHistoryEntry:
    """Tests for ExportHistoryEntry model."""

    def test_create_history_entry(self) -> None:
        """Test creating export history entry."""
        job_id = uuid4()
        created = datetime.now(timezone.utc)
        
        entry = ExportHistoryEntry(
            job_id=job_id,
            export_type=ExportType.PROXIES,
            export_format=ExportFormat.CSV,
            status=ExportStatus.COMPLETED,
            created_at=created,
            records_exported=100,
        )
        
        assert entry.job_id == job_id
        assert entry.status == ExportStatus.COMPLETED
        assert entry.records_exported == 100
