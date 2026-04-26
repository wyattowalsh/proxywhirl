"""Streaming response support for API v2.

Provides:
- Server-Sent Events (SSE) for real-time updates
- NDJSON (newline-delimited JSON) streaming
- MessagePack binary streaming
- Chunked response handling
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any, Optional

from fastapi.responses import StreamingResponse


class StreamingFormatter:
    """Format data for streaming responses."""

    @staticmethod
    async def ndjson_stream(
        data_iterator: AsyncIterator[Any],
    ) -> AsyncIterator[str]:
        """Format data as NDJSON (one JSON object per line).

        Args:
            data_iterator: Async iterator of data objects

        Yields:
            JSON strings with newline separator
        """
        async for item in data_iterator:
            yield json.dumps(item) + "\n"

    @staticmethod
    async def sse_stream(
        data_iterator: AsyncIterator[Any],
        event_name: str = "message",
    ) -> AsyncIterator[str]:
        """Format data as Server-Sent Events.

        Args:
            data_iterator: Async iterator of data objects
            event_name: SSE event name

        Yields:
            SSE-formatted strings
        """
        async for i, item in enumerate(data_iterator):
            payload = json.dumps(item)
            yield f"id: {i}\n"
            yield f"event: {event_name}\n"
            yield f"data: {payload}\n\n"

    @staticmethod
    async def csv_stream(
        data_iterator: AsyncIterator[dict[str, Any]],
        headers: Optional[list[str]] = None,
    ) -> AsyncIterator[str]:
        """Format data as CSV.

        Args:
            data_iterator: Async iterator of dict objects
            headers: CSV headers (auto-detected from first item if None)

        Yields:
            CSV lines
        """
        import csv
        import io

        headers_written = False
        async for item in data_iterator:
            if not headers_written:
                if headers is None and isinstance(item, dict):
                    headers = list(item.keys())
                if headers:
                    output = io.StringIO()
                    writer = csv.DictWriter(output, fieldnames=headers)
                    writer.writeheader()
                    yield output.getvalue()
                    headers_written = True

            if isinstance(item, dict) and headers:
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=headers)
                writer.writerow(item)
                yield output.getvalue()


async def stream_proxies(
    data_iterator: AsyncIterator[dict[str, Any]],
    format: str = "ndjson",
) -> StreamingResponse:
    """Create streaming response for proxies.

    Args:
        data_iterator: Async iterator of proxy dicts
        format: Output format (ndjson, sse, csv)

    Returns:
        StreamingResponse
    """
    if format == "sse":
        formatter = StreamingFormatter.sse_stream(data_iterator, "proxy")
        media_type = "text/event-stream"
    elif format == "csv":
        formatter = StreamingFormatter.csv_stream(data_iterator)
        media_type = "text/csv"
    else:  # ndjson
        formatter = StreamingFormatter.ndjson_stream(data_iterator)
        media_type = "application/x-ndjson"

    return StreamingResponse(
        formatter,
        media_type=media_type,
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


class ChunkedResponse:
    """Manage chunked response streaming."""

    def __init__(self, chunk_size: int = 100):
        """Initialize chunked response manager.

        Args:
            chunk_size: Number of items per chunk
        """
        self.chunk_size = chunk_size

    async def chunk_iterator(self, items: list[Any]) -> AsyncIterator[list[Any]]:
        """Yield items in chunks.

        Args:
            items: List of items to chunk

        Yields:
            Chunks of items
        """
        for i in range(0, len(items), self.chunk_size):
            yield items[i : i + self.chunk_size]
