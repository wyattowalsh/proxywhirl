#!/usr/bin/env python3
"""
Configuration Management Example for ProxyWhirl

This example demonstrates all configuration management features:
1. Multi-source configuration loading
2. Runtime configuration updates
3. Configuration validation
4. Hot reload from files
5. Configuration export and backup
"""

import time
from pathlib import Path

from loguru import logger

from proxywhirl import (
    ConfigurationManager,
    ConfigurationSource,
    ProxyWhirlSettings,
    User,
    load_yaml_config,
    parse_cli_args,
    validate_config,
)


def example_1_multi_source_loading() -> None:
    """Example 1: Load configuration from multiple sources."""
    logger.info("=" * 70)
    logger.info("Example 1: Multi-Source Configuration Loading")
    logger.info("=" * 70)
    
    # Load from YAML file
    yaml_config = {}
    yaml_path = Path("proxywhirl.yaml")
    if yaml_path.exists():
        yaml_config = load_yaml_config(yaml_path)
        logger.info(f"Loaded YAML config: {yaml_config}")
    
    # Parse CLI arguments (simulated)
    cli_args = ['--timeout', '10', '--log-level', 'DEBUG']
    cli_config = parse_cli_args(cli_args)
    logger.info(f"CLI overrides: {cli_config}")
    
    # Merge sources (CLI has highest precedence)
    merged_config = {**yaml_config, **cli_config}
    config = ProxyWhirlSettings(**merged_config)
    
    logger.info(f"Final configuration:")
    logger.info(f"  timeout: {config.timeout}s (from CLI)")
    logger.info(f"  max_retries: {config.max_retries}")
    logger.info(f"  log_level: {config.log_level} (from CLI)")
    logger.info("")


def example_2_runtime_updates() -> None:
    """Example 2: Runtime configuration updates with authorization."""
    logger.info("=" * 70)
    logger.info("Example 2: Runtime Configuration Updates")
    logger.info("=" * 70)
    
    # Initialize configuration manager
    config_manager = ConfigurationManager()
    
    # Create admin user
    admin = User(
        id="admin123",
        username="admin",
        is_admin=True,
        email="admin@example.com"
    )
    
    # Current configuration
    current_config = config_manager.get_config()
    logger.info(f"Current timeout: {current_config.timeout}s")
    
    # Update configuration
    updates = {
        'timeout': 15,
        'max_retries': 5,
        'log_level': 'DEBUG'
    }
    
    logger.info(f"Applying updates: {updates}")
    config_manager.update_runtime_config(updates, admin)
    
    # Verify update
    updated_config = config_manager.get_config()
    logger.info(f"Updated timeout: {updated_config.timeout}s")
    logger.info(f"Updated max_retries: {updated_config.max_retries}")
    logger.info(f"Updated log_level: {updated_config.log_level}")
    
    # Show sources
    sources = config_manager.get_sources()
    logger.info(f"Configuration sources:")
    for field, source in sources.items():
        logger.info(f"  {field}: {source.value}")
    logger.info("")


def example_3_validation() -> None:
    """Example 3: Configuration validation with errors and warnings."""
    logger.info("=" * 70)
    logger.info("Example 3: Configuration Validation")
    logger.info("=" * 70)
    
    # Valid configuration
    valid_config = {'timeout': 10, 'max_retries': 3}
    result = validate_config(valid_config)
    logger.info(f"Valid config: {valid_config}")
    logger.info(f"  Validation result: {'? PASS' if result.valid else '? FAIL'}")
    
    # Invalid configuration (timeout too high)
    invalid_config = {'timeout': 500}  # Exceeds max of 300
    result = validate_config(invalid_config)
    logger.info(f"Invalid config: {invalid_config}")
    logger.info(f"  Validation result: {'? PASS' if result.valid else '? FAIL'}")
    if result.has_errors:
        for error in result.errors:
            logger.error(f"  Error: {error.message}")
    
    # Configuration with warnings
    warning_config = {'timeout': 1, 'max_retries': 0}
    result = validate_config(warning_config)
    logger.info(f"Config with warnings: {warning_config}")
    logger.info(f"  Validation result: {'? PASS' if result.valid else '? FAIL'}")
    if result.has_warnings:
        for warning in result.warnings:
            logger.warning(f"  Warning: {warning}")
    logger.info("")


def example_4_hot_reload() -> None:
    """Example 4: Hot reload from configuration file."""
    logger.info("=" * 70)
    logger.info("Example 4: Configuration Hot Reload")
    logger.info("=" * 70)
    
    # Create test configuration file
    test_config_path = Path("test_config.yaml")
    with open(test_config_path, 'w') as f:
        f.write("timeout: 5\nmax_retries: 3\nlog_level: INFO\n")
    
    logger.info(f"Created test config file: {test_config_path}")
    
    # Initialize manager with config file
    config_manager = ConfigurationManager(config_path=test_config_path)
    
    logger.info(f"Initial timeout: {config_manager.get_config().timeout}s")
    
    # Modify configuration file
    with open(test_config_path, 'w') as f:
        f.write("timeout: 20\nmax_retries: 7\nlog_level: DEBUG\n")
    
    logger.info("Modified config file (timeout: 20, max_retries: 7)")
    
    # Trigger reload
    config_manager.reload()
    
    # Verify reload
    reloaded_config = config_manager.get_config()
    logger.info(f"Reloaded timeout: {reloaded_config.timeout}s")
    logger.info(f"Reloaded max_retries: {reloaded_config.max_retries}")
    logger.info(f"Reloaded log_level: {reloaded_config.log_level}")
    
    # Cleanup
    test_config_path.unlink()
    logger.info(f"Cleaned up test config file")
    logger.info("")


def example_5_export() -> None:
    """Example 5: Configuration export and backup."""
    logger.info("=" * 70)
    logger.info("Example 5: Configuration Export")
    logger.info("=" * 70)
    
    # Initialize configuration manager with custom settings
    config = ProxyWhirlSettings(
        timeout=10,
        max_retries=5,
        log_level='DEBUG',
        rate_limit_requests=200
    )
    config_manager = ConfigurationManager(config=config)
    
    # Export to string
    yaml_export = config_manager.export_config()
    logger.info("Exported configuration:")
    logger.info("-" * 70)
    for line in yaml_export.split('\n')[:15]:  # Show first 15 lines
        logger.info(line)
    logger.info("...")
    
    # Export to file
    export_path = Path("config_export.yaml")
    config_manager.export_config_to_file(export_path)
    logger.info(f"\nConfiguration exported to: {export_path}")
    
    # Cleanup
    if export_path.exists():
        export_path.unlink()
        logger.info(f"Cleaned up export file")
    logger.info("")


def example_6_file_watching() -> None:
    """Example 6: Automatic reload with file watching."""
    logger.info("=" * 70)
    logger.info("Example 6: Automatic File Watching")
    logger.info("=" * 70)
    
    # Create test configuration file
    test_config_path = Path("watched_config.yaml")
    with open(test_config_path, 'w') as f:
        f.write("timeout: 5\nmax_retries: 3\n")
    
    # Initialize manager with file watching
    config_manager = ConfigurationManager(config_path=test_config_path)
    
    logger.info("Starting file watching...")
    observer = config_manager.enable_file_watching()
    
    logger.info(f"Initial timeout: {config_manager.get_config().timeout}s")
    
    # Simulate file modification
    time.sleep(1)
    logger.info("Modifying configuration file...")
    with open(test_config_path, 'w') as f:
        f.write("timeout: 25\nmax_retries: 8\n")
    
    # Wait for automatic reload (debounced)
    time.sleep(2)
    logger.info(f"After auto-reload timeout: {config_manager.get_config().timeout}s")
    
    # Stop watching
    observer.stop()
    observer.join()
    logger.info("File watching stopped")
    
    # Cleanup
    test_config_path.unlink()
    logger.info("Cleaned up test config file")
    logger.info("")


def example_7_rollback() -> None:
    """Example 7: Configuration rollback."""
    logger.info("=" * 70)
    logger.info("Example 7: Configuration Rollback")
    logger.info("=" * 70)
    
    config_manager = ConfigurationManager()
    admin = User(id="admin123", username="admin", is_admin=True)
    
    logger.info(f"Initial timeout: {config_manager.get_config().timeout}s")
    
    # Make an update
    config_manager.update_runtime_config({'timeout': 50}, admin)
    logger.info(f"After update timeout: {config_manager.get_config().timeout}s")
    
    # Rollback
    success = config_manager.rollback()
    if success:
        logger.info(f"After rollback timeout: {config_manager.get_config().timeout}s")
    logger.info("")


def example_8_concurrent_updates() -> None:
    """Example 8: Concurrent update conflict detection."""
    logger.info("=" * 70)
    logger.info("Example 8: Concurrent Update Conflict Detection")
    logger.info("=" * 70)
    
    config_manager = ConfigurationManager()
    
    admin1 = User(id="admin1", username="alice", is_admin=True)
    admin2 = User(id="admin2", username="bob", is_admin=True)
    
    # First update
    logger.info("Admin 'alice' updates timeout to 10")
    config_manager.update_runtime_config({'timeout': 10}, admin1)
    
    # Concurrent update (within 5 seconds)
    logger.info("Admin 'bob' updates timeout to 15 (concurrent conflict!)")
    config_manager.update_runtime_config({'timeout': 15}, admin2)
    
    # Check history
    history = config_manager.get_config_history(limit=5)
    logger.info(f"\nConfiguration history (last {len(history)} updates):")
    for update in history:
        logger.info(f"  Version {update.version}: {update.username} changed {list(update.changes.keys())}")
    logger.info("")


def main() -> None:
    """Run all configuration management examples."""
    logger.info("\n" + "=" * 70)
    logger.info("ProxyWhirl Configuration Management Examples")
    logger.info("=" * 70 + "\n")
    
    try:
        example_1_multi_source_loading()
        example_2_runtime_updates()
        example_3_validation()
        example_4_hot_reload()
        example_5_export()
        example_6_file_watching()
        example_7_rollback()
        example_8_concurrent_updates()
        
        logger.info("=" * 70)
        logger.info("All examples completed successfully!")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"Error running examples: {e}")
        raise


if __name__ == '__main__':
    main()
