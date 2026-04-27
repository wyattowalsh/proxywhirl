"""Request tracing through proxy selection workflow.

Implements distributed tracing for proxy selection
decisions and request routing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from loguru import logger


@dataclass
class TraceSpan:
    """Represents a trace span."""

    span_id: str
    trace_id: str
    parent_span_id: str | None
    operation_name: str
    start_time: float
    end_time: float | None = None
    tags: dict[str, Any] | None = None
    logs: list[dict[str, Any]] | None = None

    def duration_ms(self) -> float:
        """Get span duration in milliseconds.

        Returns:
            Duration in ms
        """
        if self.end_time is None:
            return 0.0
        return (self.end_time - self.start_time) * 1000


class RequestTracer:
    """Traces requests through proxy selection workflow."""

    def __init__(self, trace_id: str) -> None:
        """Initialize request tracer.

        Args:
            trace_id: Unique trace identifier
        """
        self.trace_id = trace_id
        self._spans: dict[str, TraceSpan] = {}
        self._current_span_id: str | None = None
        logger.debug(f"RequestTracer initialized: {trace_id}")

    def start_span(
        self,
        span_id: str,
        operation_name: str,
        parent_span_id: str | None = None,
    ) -> str:
        """Start a new trace span.

        Args:
            span_id: Span identifier
            operation_name: Operation name
            parent_span_id: Parent span ID

        Returns:
            Span ID
        """
        import time

        span = TraceSpan(
            span_id=span_id,
            trace_id=self.trace_id,
            parent_span_id=parent_span_id or self._current_span_id,
            operation_name=operation_name,
            start_time=time.time(),
            tags={},
            logs=[],
        )

        self._spans[span_id] = span
        self._current_span_id = span_id

        logger.debug(f"Span started: {span_id} ({operation_name})")
        return span_id

    def end_span(self, span_id: str) -> bool:
        """End a trace span.

        Args:
            span_id: Span identifier

        Returns:
            True if ended
        """
        import time

        if span_id not in self._spans:
            return False

        span = self._spans[span_id]
        span.end_time = time.time()

        if self._current_span_id == span_id:
            self._current_span_id = span.parent_span_id

        logger.debug(f"Span ended: {span_id}")
        return True

    def add_tag(self, span_id: str, key: str, value: Any) -> bool:
        """Add tag to span.

        Args:
            span_id: Span identifier
            key: Tag key
            value: Tag value

        Returns:
            True if added
        """
        if span_id not in self._spans:
            return False

        self._spans[span_id].tags[key] = value
        return True

    def log_event(self, span_id: str, event: str, fields: dict[str, Any] | None = None) -> bool:
        """Log event to span.

        Args:
            span_id: Span identifier
            event: Event description
            fields: Event fields

        Returns:
            True if logged
        """
        import time

        if span_id not in self._spans:
            return False

        log_entry = {
            "timestamp": time.time(),
            "event": event,
            "fields": fields or {},
        }
        self._spans[span_id].logs.append(log_entry)
        return True

    def get_trace(self) -> dict[str, Any]:
        """Get complete trace data.

        Returns:
            Dictionary with trace data
        """
        spans_data = []
        for span_id, span in sorted(self._spans.items()):
            spans_data.append(
                {
                    "span_id": span.span_id,
                    "operation_name": span.operation_name,
                    "parent_span_id": span.parent_span_id,
                    "duration_ms": span.duration_ms(),
                    "tags": span.tags or {},
                    "log_count": len(span.logs or []),
                }
            )

        return {
            "trace_id": self.trace_id,
            "span_count": len(self._spans),
            "spans": spans_data,
        }
