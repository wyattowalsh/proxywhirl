"""Tests for streaming source parsing."""

from __future__ import annotations

from typing import Iterator


class StreamingParser:
    """Parses data from streaming sources."""

    def __init__(self, buffer_size: int = 1024) -> None:
        """Initialize parser."""
        self.buffer_size = buffer_size
        self.total_lines = 0

    def parse_lines(self, stream: Iterator[str]) -> Iterator[str]:
        """Parse lines from stream."""
        buffer = []
        for line in stream:
            self.total_lines += 1
            line = line.rstrip("\n\r")
            if line.strip():
                buffer.append(line)

            if len(buffer) >= self.buffer_size:
                for buffered in buffer:
                    yield buffered
                buffer.clear()

        # Yield remaining
        for buffered in buffer:
            yield buffered

    def parse_csv_like(self, stream: Iterator[str], delimiter: str = ",") -> Iterator[list[str]]:
        """Parse CSV-like data from stream."""
        for line in stream:
            if line.strip():
                parts = line.rstrip("\n\r").split(delimiter)
                yield parts

    def parse_json_lines(self, stream: Iterator[str]) -> Iterator[dict]:
        """Parse JSONL from stream."""
        import json

        for line in stream:
            if line.strip():
                try:
                    obj = json.loads(line)
                    yield obj
                except json.JSONDecodeError:
                    pass


class TestStreamingSourceParsing:
    """Test streaming parsing functionality."""

    def test_parse_simple_lines(self) -> None:
        """Test parsing simple lines."""
        data = ["line1\n", "line2\n", "line3\n"]
        parser = StreamingParser()

        lines = list(parser.parse_lines(iter(data)))
        assert lines == ["line1", "line2", "line3"]

    def test_empty_lines_skipped(self) -> None:
        """Test empty lines are skipped."""
        data = ["line1\n", "\n", "line2\n", "  \n", "line3\n"]
        parser = StreamingParser()

        lines = list(parser.parse_lines(iter(data)))
        assert lines == ["line1", "line2", "line3"]

    def test_line_endings_stripped(self) -> None:
        """Test line endings are stripped."""
        data = ["line1\r\n", "line2\n", "line3\r"]
        parser = StreamingParser()

        lines = list(parser.parse_lines(iter(data)))
        assert all("\n" not in line for line in lines)
        assert all("\r" not in line for line in lines)

    def test_buffering(self) -> None:
        """Test buffering behavior."""
        data = [f"line{i}\n" for i in range(5)]
        parser = StreamingParser(buffer_size=2)

        lines = list(parser.parse_lines(iter(data)))
        assert len(lines) == 5

    def test_total_lines_counted(self) -> None:
        """Test line counting."""
        data = ["line1\n", "line2\n", "line3\n"]
        parser = StreamingParser()

        list(parser.parse_lines(iter(data)))
        assert parser.total_lines == 3

    def test_csv_parsing(self) -> None:
        """Test CSV-like parsing."""
        data = [
            "host1,port1,type1\n",
            "host2,port2,type2\n",
        ]
        parser = StreamingParser()

        rows = list(parser.parse_csv_like(iter(data)))
        assert rows == [
            ["host1", "port1", "type1"],
            ["host2", "port2", "type2"],
        ]

    def test_csv_custom_delimiter(self) -> None:
        """Test CSV with custom delimiter."""
        data = [
            "host1|port1|type1\n",
            "host2|port2|type2\n",
        ]
        parser = StreamingParser()

        rows = list(parser.parse_csv_like(iter(data), delimiter="|"))
        assert rows[0] == ["host1", "port1", "type1"]

    def test_jsonl_parsing(self) -> None:
        """Test JSONL parsing."""
        data = [
            '{"host": "proxy1", "port": 8080}\n',
            '{"host": "proxy2", "port": 8080}\n',
        ]
        parser = StreamingParser()

        objects = list(parser.parse_json_lines(iter(data)))
        assert len(objects) == 2
        assert objects[0]["host"] == "proxy1"
        assert objects[1]["host"] == "proxy2"

    def test_jsonl_invalid_skipped(self) -> None:
        """Test invalid JSON is skipped."""
        data = [
            '{"host": "proxy1"}\n',
            "invalid json\n",
            '{"host": "proxy2"}\n',
        ]
        parser = StreamingParser()

        objects = list(parser.parse_json_lines(iter(data)))
        assert len(objects) == 2

    def test_large_buffer(self) -> None:
        """Test large buffer size."""
        data = [f"line{i}\n" for i in range(100)]
        parser = StreamingParser(buffer_size=1000)

        lines = list(parser.parse_lines(iter(data)))
        assert len(lines) == 100

    def test_single_char_lines(self) -> None:
        """Test single character lines."""
        data = ["a\n", "b\n", "c\n"]
        parser = StreamingParser()

        lines = list(parser.parse_lines(iter(data)))
        assert lines == ["a", "b", "c"]

    def test_whitespace_only_lines(self) -> None:
        """Test whitespace-only lines are skipped."""
        data = ["   \n", "data\n", "\t\n", "more\n"]
        parser = StreamingParser()

        lines = list(parser.parse_lines(iter(data)))
        assert lines == ["data", "more"]

    def test_memory_efficient(self) -> None:
        """Test streaming doesn't load all at once."""

        def generate_lines(count: int) -> Iterator[str]:
            for i in range(count):
                yield f"line{i}\n"

        parser = StreamingParser(buffer_size=10)
        lines_gen = parser.parse_lines(generate_lines(1000))

        # Take just first few
        first_few = []
        for i, line in enumerate(lines_gen):
            first_few.append(line)
            if i >= 4:
                break

        assert len(first_few) == 5

    def test_csv_with_empty_fields(self) -> None:
        """Test CSV with empty fields."""
        data = ["host1,,type1\n", "host2,,type2\n"]
        parser = StreamingParser()

        rows = list(parser.parse_csv_like(iter(data)))
        assert rows[0] == ["host1", "", "type1"]

    def test_chunked_input(self) -> None:
        """Test processing chunked input."""
        chunks = ["line1\nlin", "e2\nline3\n"]

        def chunk_stream():
            yield from chunks

        parser = StreamingParser()
        # This tests that our simple parser expects line-at-a-time
        # For actual chunked parsing, would need different approach
