"""
Comprehensive demonstration of ProxyWhirl's structured logging system.

This example shows how to:
- Configure structured logging (JSON, logfmt formats)
- Use multiple output destinations
- Apply log rotation and retention
- Add contextual metadata to logs
- Redact sensitive data
- Use sampling and filtering
"""

from pathlib import Path

from loguru import logger

from proxywhirl import (
    LogConfiguration,
    LogContext,
    LogHandlerConfig,
    LogHandlerType,
    LogLevel,
    apply_logging_configuration,
    bind_context,
    generate_request_id,
)


def example_1_basic_structured_logging() -> None:
    """Example 1: Basic JSON structured logging."""
    print("\n=== Example 1: Basic JSON Structured Logging ===\n")
    
    # Configure with single JSON console handler
    config = LogConfiguration(
        level=LogLevel.INFO,
        handlers=[
            LogHandlerConfig(
                type=LogHandlerType.CONSOLE,
                format="json",
            )
        ],
    )
    
    apply_logging_configuration(config)
    
    # Log some messages
    logger.info("Application started")
    logger.warning("This is a warning with structured output")
    logger.error("Error with exception", exception="ValueError: Invalid input")


def example_2_multiple_destinations() -> None:
    """Example 2: Multiple output destinations."""
    print("\n=== Example 2: Multiple Output Destinations ===\n")
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure with console (JSON) and file (logfmt) handlers
    config = LogConfiguration(
        level=LogLevel.DEBUG,
        handlers=[
            LogHandlerConfig(
                type=LogHandlerType.CONSOLE,
                level=LogLevel.INFO,
                format="json",
            ),
            LogHandlerConfig(
                type=LogHandlerType.FILE,
                path="logs/app.log",
                level=LogLevel.DEBUG,
                format="logfmt",
            ),
        ],
    )
    
    apply_logging_configuration(config)
    
    logger.debug("Debug message (only in file)")
    logger.info("Info message (in both)")
    logger.error("Error message (in both)")
    
    print(f"\nLogs written to {logs_dir / 'app.log'}")


def example_3_contextual_logging() -> None:
    """Example 3: Contextual logging with metadata."""
    print("\n=== Example 3: Contextual Logging ===\n")
    
    config = LogConfiguration(
        level=LogLevel.INFO,
        handlers=[
            LogHandlerConfig(
                type=LogHandlerType.CONSOLE,
                format="json",
            )
        ],
    )
    
    apply_logging_configuration(config)
    
    # Use LogContext to automatically attach metadata
    request_id = generate_request_id()
    
    with LogContext(request_id=request_id, operation="proxy_selection"):
        logger.info("Starting proxy selection")
        
        with LogContext(strategy="weighted", proxy_url="http://proxy1.example.com:8080"):
            logger.info("Proxy selected successfully")
            logger.info("Health check passed")
    
    # Context is automatically removed outside the block
    logger.info("Request completed")


def example_4_credential_redaction() -> None:
    """Example 4: Automatic credential redaction."""
    print("\n=== Example 4: Credential Redaction ===\n")
    
    config = LogConfiguration(
        level=LogLevel.INFO,
        redact_credentials=True,
        handlers=[
            LogHandlerConfig(
                type=LogHandlerType.CONSOLE,
                format="json",
            )
        ],
    )
    
    apply_logging_configuration(config)
    
    # Log with sensitive data - will be automatically redacted
    log = bind_context(
        proxy_url="http://user:secretpass@proxy.example.com:8080",
        api_key="secret-key-12345",
        username="admin",
    )
    
    log.info("Authenticated proxy connection")
    # Credentials in the output will be redacted as "**REDACTED**"


def example_5_rotation_and_retention() -> None:
    """Example 5: Log rotation and retention."""
    print("\n=== Example 5: Log Rotation and Retention ===\n")
    
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure file handler with rotation and retention
    config = LogConfiguration(
        level=LogLevel.INFO,
        handlers=[
            LogHandlerConfig(
                type=LogHandlerType.FILE,
                path="logs/rotated.log",
                format="json",
                rotation="1 MB",      # Rotate when file reaches 1 MB
                retention="7 days",   # Keep logs for 7 days
            )
        ],
    )
    
    apply_logging_configuration(config)
    
    # Generate some logs
    for i in range(100):
        logger.info(f"Log entry {i}")
    
    print(f"\nRotated logs in {logs_dir} (check for .log.* files)")


def example_6_filtering_and_sampling() -> None:
    """Example 6: Module filtering and log sampling."""
    print("\n=== Example 6: Filtering and Sampling ===\n")
    
    # Only log from specific modules, and sample at 50%
    config = LogConfiguration(
        level=LogLevel.DEBUG,
        handlers=[
            LogHandlerConfig(
                type=LogHandlerType.CONSOLE,
                format="json",
                filter_modules=["proxywhirl.rotator", "proxywhirl.strategies"],
                sample_rate=0.5,  # Only log 50% of entries
            )
        ],
    )
    
    apply_logging_configuration(config)
    
    # Only about 50% of these logs will appear
    for i in range(10):
        logger.info(f"Sampled log entry {i}")
    
    print("\n(Note: Due to sampling, you'll see roughly 50% of logs)")


def example_7_async_logging() -> None:
    """Example 7: Async logging for high performance."""
    print("\n=== Example 7: Async Logging ===\n")
    
    # Enable async logging with bounded queue
    config = LogConfiguration(
        level=LogLevel.INFO,
        async_logging=True,
        queue_size=1000,
        drop_on_full=True,
        handlers=[
            LogHandlerConfig(
                type=LogHandlerType.CONSOLE,
                format="json",
            )
        ],
    )
    
    apply_logging_configuration(config)
    
    # Logs are written asynchronously - won't block main thread
    for i in range(100):
        logger.info(f"Async log entry {i}")
    
    print("\n(Logs written asynchronously in background thread)")


def example_8_runtime_reconfiguration() -> None:
    """Example 8: Runtime log level changes."""
    print("\n=== Example 8: Runtime Reconfiguration ===\n")
    
    # Start with INFO level
    config = LogConfiguration(
        level=LogLevel.INFO,
        handlers=[
            LogHandlerConfig(
                type=LogHandlerType.CONSOLE,
                format="json",
            )
        ],
    )
    
    apply_logging_configuration(config)
    
    logger.debug("This won't appear (level=INFO)")
    logger.info("This will appear")
    
    # Change to DEBUG level without restart
    config.level = LogLevel.DEBUG
    apply_logging_configuration(config)
    
    logger.debug("Now this debug message appears!")
    logger.info("Info still appears")


def main() -> None:
    """Run all examples."""
    examples = [
        example_1_basic_structured_logging,
        example_2_multiple_destinations,
        example_3_contextual_logging,
        example_4_credential_redaction,
        example_5_rotation_and_retention,
        example_6_filtering_and_sampling,
        example_7_async_logging,
        example_8_runtime_reconfiguration,
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"Error in {example.__name__}: {e}")
    
    print("\n=== All Examples Complete ===\n")


if __name__ == "__main__":
    main()
