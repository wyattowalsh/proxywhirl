"""Example demonstrating the structured logging system.

This example shows how to use the MVP Phase 1 logging features:
- JSON and logfmt output formats
- Context binding for metadata
- Log rotation and retention
"""

import tempfile
from pathlib import Path

from proxywhirl.logging_config import (
    LogContext,
    bind_context,
    configure_logging,
    get_logger,
)

# Example 1: Default logging (colored console output)
print("=" * 60)
print("Example 1: Default console logging")
print("=" * 60)
configure_logging(format="default", level="INFO")
logger = get_logger()
logger.info("This is a default format log message")
logger.warning("This is a warning message")
logger.error("This is an error message")

# Example 2: JSON logging
print("\n" + "=" * 60)
print("Example 2: JSON structured logging")
print("=" * 60)
configure_logging(format="json", level="DEBUG")
logger = get_logger()
logger.debug("Debug message in JSON format")
logger.info("Info message in JSON format")

# Example 3: JSON logging with context
print("\n" + "=" * 60)
print("Example 3: JSON logging with contextual metadata")
print("=" * 60)
configure_logging(format="json", level="INFO")
logger = get_logger()

# Add context to logs
request_logger = bind_context(
    request_id="req-abc-123", operation="proxy_fetch", source="free-proxy-list"
)
request_logger.info("Starting proxy fetch operation")
request_logger.info("Successfully fetched 10 proxies")
request_logger.warning("3 proxies failed validation")

# Example 4: Logfmt logging
print("\n" + "=" * 60)
print("Example 4: Logfmt format logging")
print("=" * 60)
configure_logging(format="logfmt", level="INFO")
logger = get_logger()
logger.info("Logfmt is a key=value format")
logger.bind(user_id=42, action="rotate_proxy").info("User rotated proxy")

# Example 5: File logging with rotation (to tmp file for demo)
print("\n" + "=" * 60)
print("Example 5: File logging with rotation")
print("=" * 60)

log_dir = Path(tempfile.gettempdir()) / "proxywhirl_logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "proxywhirl.log"

configure_logging(
    format="json",
    level="INFO",
    sink=str(log_file),
    rotation="10 MB",  # Rotate when file reaches 10MB
    retention="1 week",  # Keep logs for 1 week
)

logger = get_logger()
logger.info("This message is written to a file with rotation")
logger.bind(proxy_id="proxy-123").info("Proxy validated successfully")

print(f"Logs written to: {log_file}")
if log_file.exists():
    print(f"Log file size: {log_file.stat().st_size} bytes")
    print("\nLog file contents:")
    print(log_file.read_text())

# Example 6: Using LogContext context manager
print("\n" + "=" * 60)
print("Example 6: Using LogContext context manager")
print("=" * 60)

configure_logging(format="json", level="INFO")
logger = get_logger()

# Context manager automatically binds metadata
with LogContext(request_id="req-xyz-789", operation="health_check"):
    logger.bind(request_id="req-xyz-789", operation="health_check").info(
        "Health check started"
    )
    logger.bind(request_id="req-xyz-789", operation="health_check").info(
        "All systems operational"
    )

print("\nLogging examples complete!")
