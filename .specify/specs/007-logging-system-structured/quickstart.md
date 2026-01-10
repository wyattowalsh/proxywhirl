# Quickstart: Structured Logging

**Feature**: 007-logging-system-structured

This guide provides a brief overview of how to configure and use the new structured logging system.

## Enabling Structured Logging

Structured logging is configured via environment variables. Here are some examples:

### Basic Console Logging (JSON)

This configuration logs INFO-level messages and above to the console in JSON format.

```bash
export PROXYWHIRL_LOG_LEVEL="INFO"
export PROXYWHIRL_LOG_HANDLERS='[{"type": "console", "format": "json"}]'
```

### File Logging with Rotation

This configuration logs DEBUG-level messages to a file, with rotation when the file reaches 10 MB, and retains the last 5 log files.

```bash
export PROXYWHIRL_LOG_LEVEL="DEBUG"
export PROXYWHIRL_LOG_HANDLERS='[{"type": "file", "path": "/var/log/proxywhirl.log", "rotation": "10 MB", "retention": "5 files"}]'
```

### Multiple Handlers

You can configure multiple handlers at once. This example sends INFO logs to the console and DEBUG logs to a file.

```bash
export PROXYWHIRL_LOG_HANDLERS='[
  {"type": "console", "level": "INFO"},
  {"type": "file", "level": "DEBUG", "path": "/var/log/proxywhirl.log"}
]'
```

## Attaching Context to Logs

To add contextual information to your logs, use the `bind` method of the logger:

```python
from proxywhirl.logging import logger

request_id = "req-abc-123"

# Bind the request_id to the logger context
context_logger = logger.bind(request_id=request_id)

context_logger.info("Processing request")
# This log entry will now contain '"request_id": "req-abc-123"' in its JSON payload.
```
