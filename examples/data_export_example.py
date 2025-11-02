"""
Example script demonstrating ProxyWhirl data export functionality.

This script shows how to:
1. Export proxy lists in various formats (CSV, JSON, YAML)
2. Export with filtering and field selection
3. Export with compression
4. Export metrics and configuration data
5. View export history
"""

from pathlib import Path

from proxywhirl import (
    CompressionType,
    ExportConfig,
    ExportFormat,
    ExportManager,
    ExportType,
    LocalFileDestination,
    Proxy,
    ProxyExportFilter,
    ProxyPool,
)


def main() -> None:
    """Demonstrate data export functionality."""
    
    # ========================================================================
    # Setup: Create sample proxy pool
    # ========================================================================
    
    print("=" * 80)
    print("ProxyWhirl Data Export Examples")
    print("=" * 80)
    print()
    
    # Create sample proxies
    proxies = [
        Proxy(url="http://proxy1.example.com:8080"),
        Proxy(url="http://proxy2.example.com:8080"),
        Proxy(url="socks5://proxy3.example.com:1080"),
        Proxy(url="http://proxy4.example.com:8080"),
    ]
    
    # Simulate some usage stats
    proxies[0].total_requests    = 100
    proxies[0].total_successes   = 95
    proxies[0].total_failures    = 5
    proxies[0].health_status.value = "healthy"
    
    proxies[1].total_requests    = 50
    proxies[1].total_successes   = 40
    proxies[1].total_failures    = 10
    
    proxies[2].total_requests    = 10
    proxies[2].total_successes   = 5
    proxies[2].total_failures    = 5
    
    proxies[3].total_requests    = 0
    
    # Create proxy pool
    pool = ProxyPool(name="example-pool", proxies=proxies)
    
    # Create export manager
    export_manager = ExportManager(proxy_pool=pool)
    
    print(f"Created proxy pool with {len(proxies)} proxies")
    print()
    
    # ========================================================================
    # Example 1: Export all proxies to CSV
    # ========================================================================
    
    print("Example 1: Export all proxies to CSV")
    print("-" * 80)
    
    config = ExportConfig(
        export_type=ExportType.PROXIES,
        export_format=ExportFormat.CSV,
        destination=LocalFileDestination(
            file_path="exports/proxies_all.csv",
            overwrite=True,
        ),
        pretty_print=True,
        include_metadata=True,
    )
    
    result = export_manager.export(config)
    
    print(f"? Exported {result.records_exported} proxies to {result.destination_path}")
    print(f"  File size: {result.file_size_bytes} bytes")
    print(f"  Duration: {result.duration_seconds:.3f}s")
    print()
    
    # ========================================================================
    # Example 2: Export healthy proxies only to JSON
    # ========================================================================
    
    print("Example 2: Export healthy proxies to JSON with filtering")
    print("-" * 80)
    
    config = ExportConfig(
        export_type=ExportType.PROXIES,
        export_format=ExportFormat.JSON,
        destination=LocalFileDestination(
            file_path="exports/proxies_healthy.json",
            overwrite=True,
        ),
        proxy_filter=ProxyExportFilter(
            health_status=["healthy"],
            min_success_rate=0.8,
        ),
        pretty_print=True,
    )
    
    result = export_manager.export(config)
    
    print(f"? Exported {result.records_exported} healthy proxies to {result.destination_path}")
    print(f"  File size: {result.file_size_bytes} bytes")
    print()
    
    # ========================================================================
    # Example 3: Export with compression (GZIP)
    # ========================================================================
    
    print("Example 3: Export proxies with GZIP compression")
    print("-" * 80)
    
    config = ExportConfig(
        export_type=ExportType.PROXIES,
        export_format=ExportFormat.JSON,
        destination=LocalFileDestination(
            file_path="exports/proxies_compressed.json.gz",
            overwrite=True,
        ),
        compression=CompressionType.GZIP,
        pretty_print=True,
    )
    
    result = export_manager.export(config)
    
    print(f"? Exported {result.records_exported} proxies (compressed) to {result.destination_path}")
    print(f"  Compressed file size: {result.file_size_bytes} bytes")
    print()
    
    # ========================================================================
    # Example 4: Export to YAML format
    # ========================================================================
    
    print("Example 4: Export proxies to YAML format")
    print("-" * 80)
    
    config = ExportConfig(
        export_type=ExportType.PROXIES,
        export_format=ExportFormat.YAML,
        destination=LocalFileDestination(
            file_path="exports/proxies.yaml",
            overwrite=True,
        ),
        pretty_print=True,
    )
    
    result = export_manager.export(config)
    
    print(f"? Exported {result.records_exported} proxies to {result.destination_path}")
    print()
    
    # ========================================================================
    # Example 5: Export with field selection
    # ========================================================================
    
    print("Example 5: Export with specific fields only")
    print("-" * 80)
    
    config = ExportConfig(
        export_type=ExportType.PROXIES,
        export_format=ExportFormat.CSV,
        destination=LocalFileDestination(
            file_path="exports/proxies_minimal.csv",
            overwrite=True,
        ),
        proxy_filter=ProxyExportFilter(
            include_fields=["url", "protocol", "health_status", "success_rate"],
        ),
    )
    
    result = export_manager.export(config)
    
    print(f"? Exported {result.records_exported} proxies with selected fields to {result.destination_path}")
    print()
    
    # ========================================================================
    # Example 6: Export health status report
    # ========================================================================
    
    print("Example 6: Export health status report")
    print("-" * 80)
    
    config = ExportConfig(
        export_type=ExportType.HEALTH_STATUS,
        export_format=ExportFormat.JSON,
        destination=LocalFileDestination(
            file_path="exports/health_report.json",
            overwrite=True,
        ),
        pretty_print=True,
    )
    
    result = export_manager.export(config)
    
    print(f"? Exported health status for {result.records_exported} proxies to {result.destination_path}")
    print()
    
    # ========================================================================
    # Example 7: Export to Markdown table
    # ========================================================================
    
    print("Example 7: Export proxies to Markdown table")
    print("-" * 80)
    
    config = ExportConfig(
        export_type=ExportType.PROXIES,
        export_format=ExportFormat.MARKDOWN,
        destination=LocalFileDestination(
            file_path="exports/proxies_table.md",
            overwrite=True,
        ),
        proxy_filter=ProxyExportFilter(
            include_fields=["url", "protocol", "total_requests", "success_rate"],
        ),
    )
    
    result = export_manager.export(config)
    
    print(f"? Exported {result.records_exported} proxies to Markdown table: {result.destination_path}")
    print()
    
    # ========================================================================
    # Example 8: View export history
    # ========================================================================
    
    print("Example 8: View export history")
    print("-" * 80)
    
    history = export_manager.get_export_history(limit=10)
    
    print(f"Export history ({len(history)} entries):")
    for entry in history:
        status_emoji = "?" if entry.status == "completed" else "?"
        print(f"  {status_emoji} {entry.export_type.value:15} ? {entry.export_format.value:8} "
              f"({entry.records_exported} records, {entry.duration_seconds:.2f}s)")
    
    print()
    
    # ========================================================================
    # Summary
    # ========================================================================
    
    print("=" * 80)
    print("Export Examples Complete!")
    print("=" * 80)
    print()
    print("Files created in exports/ directory:")
    print("  - proxies_all.csv")
    print("  - proxies_healthy.json")
    print("  - proxies_compressed.json.gz")
    print("  - proxies.yaml")
    print("  - proxies_minimal.csv")
    print("  - health_report.json")
    print("  - proxies_table.md")
    print()
    print("Check the files to see the exported data!")
    

if __name__ == "__main__":
    main()
