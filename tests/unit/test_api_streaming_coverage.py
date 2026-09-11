"""Behavioral coverage for API streaming helpers."""

from __future__ import annotations

import csv
import io
import json
from collections.abc import AsyncIterable, Callable

import pytest
from fastapi.responses import StreamingResponse

from proxywhirl.api.streaming import (
    create_streaming_response,
    get_csv_media_type,
    get_json_lines_media_type,
    get_text_media_type,
    stream_csv_lines,
    stream_json_lines,
    stream_proxies_as_jsonl,
    stream_text_lines,
)


async def _collect(chunks: AsyncIterable[str]) -> list[str]:
    return [chunk async for chunk in chunks]


async def test_stream_json_lines_emits_one_complete_document_per_item() -> None:
    records = [{"id": 1, "active": True}, {"id": 2, "tags": ["fast", "secure"]}]

    chunks = await _collect(stream_json_lines(records))

    assert len(chunks) == len(records)
    assert all(chunk.endswith("\n") for chunk in chunks)
    assert [json.loads(chunk) for chunk in chunks] == records


async def test_stream_proxies_skips_only_unserializable_records() -> None:
    proxies = [
        {"url": "http://proxy-one.test:8080"},
        {"url": "http://broken.test:8080", "unsupported": {"set-values"}},
        {"url": "socks5://proxy-two.test:1080"},
    ]

    chunks = await _collect(stream_proxies_as_jsonl(proxies))

    assert [json.loads(chunk) for chunk in chunks] == [proxies[0], proxies[2]]


async def test_stream_text_lines_preserves_content_and_adds_separators() -> None:
    chunks = await _collect(stream_text_lines(["first", "", "third\nline"]))

    assert chunks == ["first\n", "\n", "third\nline\n"]


async def test_stream_csv_lines_emits_parseable_header_and_rows() -> None:
    rows = [
        {"name": "alpha", "note": "uses, comma"},
        {"name": "beta", "note": "plain"},
    ]

    chunks = await _collect(stream_csv_lines(rows, ["name", "note"]))

    assert len(chunks) == 3
    assert list(csv.reader(io.StringIO("".join(chunks)))) == [
        ["name", "note"],
        ["alpha", "uses, comma"],
        ["beta", "plain"],
    ]


async def test_create_streaming_response_exposes_media_type_and_stream_body() -> None:
    response = create_streaming_response(
        stream_text_lines(["alpha", "beta"]),
        media_type="text/plain",
    )

    assert isinstance(response, StreamingResponse)
    assert response.media_type == "text/plain"
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    assert await _collect(response.body_iterator) == ["alpha\n", "beta\n"]


@pytest.mark.parametrize(
    ("helper", "expected"),
    [
        (get_json_lines_media_type, "application/x-ndjson"),
        (get_csv_media_type, "text/csv"),
        (get_text_media_type, "text/plain"),
    ],
)
def test_media_type_helpers_return_stable_values(
    helper: Callable[[], str],
    expected: str,
) -> None:
    assert helper() == expected
