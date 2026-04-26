"""Streaming response helpers for FastAPI routes.

Provides async generators and streaming utilities for efficient
data transfer over HTTP with async/await patterns.
"""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator, AsyncIterator
from typing import Any

from fastapi.responses import StreamingResponse
from loguru import logger


async def stream_json_lines(data: list[dict[str, Any]]) -> AsyncGenerator[str, None]:
    """Stream data as JSON Lines format.

    Each line is a complete JSON object, allowing streaming without
    buffering the entire dataset in memory.

    Args:
        data: List of dictionaries to stream

    Yields:
        JSON line strings (one per item)
    """
    for item in data:
        line = json.dumps(item) + "\n"
        yield line


async def stream_proxies_as_jsonl(
    proxies: list[dict[str, Any]],
) -> AsyncGenerator[str, None]:
    """Stream proxy data as JSON Lines.

    Converts proxy data to JSON Lines format for efficient streaming.
    Each proxy is a complete JSON object on one line.

    Args:
        proxies: List of proxy dictionaries

    Yields:
        Proxy JSON line strings
    """
    for proxy in proxies:
        try:
            line = json.dumps(proxy) + "\n"
            yield line
        except Exception as e:
            logger.warning(f"Failed to serialize proxy: {e}")
            continue


async def stream_text_lines(lines: list[str]) -> AsyncGenerator[str, None]:
    """Stream text data as lines.

    Simple line-by-line streaming with newline separators.

    Args:
        lines: List of strings to stream

    Yields:
        Text lines with newline separators
    """
    for line in lines:
        yield line + "\n"


async def stream_csv_lines(
    data: list[dict[str, Any]], fieldnames: list[str]
) -> AsyncGenerator[str, None]:
    """Stream data as CSV format.

    Yields header row and then data rows as CSV lines.

    Args:
        data: List of dictionaries to stream
        fieldnames: Column names for CSV header

    Yields:
        CSV lines (header + data rows)
    """
    import csv
    from io import StringIO

    # Yield header
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    yield buffer.getvalue()

    # Yield data rows
    for row in data:
        buffer = StringIO()
        writer = csv.DictWriter(buffer, fieldnames=fieldnames)
        writer.writerow(row)
        yield buffer.getvalue()


def create_streaming_response(
    generator: AsyncIterator[str],
    media_type: str = "application/x-ndjson",
) -> StreamingResponse:
    """Create a StreamingResponse from an async generator.

    Args:
        generator: Async generator yielding strings
        media_type: MIME type for response (default: JSON Lines)

    Returns:
        StreamingResponse that can be returned from FastAPI routes
    """
    return StreamingResponse(
        generator,
        media_type=media_type,
    )


def get_json_lines_media_type() -> str:
    """Get MIME type for JSON Lines format."""
    return "application/x-ndjson"


def get_csv_media_type() -> str:
    """Get MIME type for CSV format."""
    return "text/csv"


def get_text_media_type() -> str:
    """Get MIME type for plain text."""
    return "text/plain"
