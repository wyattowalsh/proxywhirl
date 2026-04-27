"""Structured logging configuration."""

import json
from typing import Any, Dict
from loguru import logger
import sys


class StructuredLogger:
    """Provides structured logging output."""
    
    @staticmethod
    def configure(
        level: str = "INFO",
        output_format: str = "json"
    ) -> None:
        """Configure structured logging."""
        logger.remove()
        
        if output_format == "json":
            logger.add(
                sys.stderr,
                format=StructuredLogger._json_format,
                level=level,
                serialize=True
            )
        else:
            logger.add(
                sys.stderr,
                format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
                level=level
            )
    
    @staticmethod
    def _json_format(record):
        """Format log record as JSON."""
        log_data = {
            "timestamp": record["time"].isoformat(),
            "level": record["level"].name,
            "message": record["message"],
            "module": record["name"],
            "function": record["function"],
            "line": record["line"],
        }
        
        # Add extra fields
        if record["extra"]:
            log_data.update(record["extra"])
        
        return json.dumps(log_data)
    
    @staticmethod
    def log_proxy_request(
        proxy_url: str,
        status_code: int,
        latency_ms: float,
        **extra
    ) -> None:
        """Log a proxy request with structured data."""
        logger.info(
            "proxy_request",
            proxy_url=proxy_url,
            status_code=status_code,
            latency_ms=latency_ms,
            **extra
        )
    
    @staticmethod
    def log_error(
        error_type: str,
        message: str,
        **context
    ) -> None:
        """Log an error with context."""
        logger.error(
            message,
            error_type=error_type,
            **context
        )

