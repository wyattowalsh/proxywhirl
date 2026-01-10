"""Unit tests for safe regex pattern matching with ReDoS protection.

Tests the safe_regex module's ability to prevent Regular Expression Denial of
Service (ReDoS) attacks through timeout and complexity validation.
"""

from __future__ import annotations

import re
import time

import pytest
import typer

from proxywhirl.safe_regex import (
    MAX_PATTERN_LENGTH,
    MAX_REPETITIONS,
    safe_regex_compile,
    safe_regex_findall,
    safe_regex_match,
    safe_regex_search,
    validate_regex_pattern,
)


class TestRegexValidation:
    """Test regex pattern validation for safety."""

    def test_validate_simple_pattern(self) -> None:
        """Simple patterns should pass validation."""
        # Should not raise
        validate_regex_pattern(r"hello")
        validate_regex_pattern(r"[a-z]+")
        validate_regex_pattern(r"\d{1,3}")

    def test_validate_pattern_too_long(self) -> None:
        """Patterns exceeding max length should be rejected."""
        # Create a pattern longer than MAX_PATTERN_LENGTH
        long_pattern = "a" * (MAX_PATTERN_LENGTH + 1)

        with pytest.raises(typer.Exit) as exc_info:
            validate_regex_pattern(long_pattern)
        assert exc_info.value.exit_code == 1

    def test_validate_pattern_too_many_repetitions(self) -> None:
        """Patterns with too many repetitions should be rejected."""
        # Create a pattern with more than MAX_REPETITIONS quantifiers
        pattern = "a*" * (MAX_REPETITIONS + 1)

        with pytest.raises(typer.Exit) as exc_info:
            validate_regex_pattern(pattern)
        assert exc_info.value.exit_code == 1

    def test_validate_nested_quantifiers(self) -> None:
        """Patterns with nested quantifiers should be rejected."""
        dangerous_patterns = [
            r"(a+)+",  # Nested + quantifiers
            r"(a*)*",  # Nested * quantifiers
            r"(a+)*",  # Mixed nested quantifiers
            r"(a?)+",  # Nested ? quantifiers
        ]

        for pattern in dangerous_patterns:
            with pytest.raises(typer.Exit) as exc_info:
                validate_regex_pattern(pattern)
            assert exc_info.value.exit_code == 1

    def test_validate_safe_quantifiers(self) -> None:
        """Non-nested quantifiers should pass validation."""
        safe_patterns = [
            r"a+b+",  # Sequential, not nested
            r"a*b*",  # Sequential, not nested
            r"a{1,3}b{2,5}",  # Bounded repetitions
            r"(abc)+",  # Group with single quantifier
        ]

        for pattern in safe_patterns:
            # Should not raise
            validate_regex_pattern(pattern)


class TestSafeRegexCompile:
    """Test safe regex compilation with timeout."""

    def test_compile_simple_pattern(self) -> None:
        """Simple patterns should compile successfully."""
        pattern = safe_regex_compile(r"hello")
        assert pattern is not None
        assert isinstance(pattern, re.Pattern)

    def test_compile_with_flags(self) -> None:
        """Compilation should support regex flags."""
        pattern = safe_regex_compile(r"hello", flags=re.IGNORECASE)
        assert pattern.match("HELLO") is not None

    def test_compile_rejects_complex_pattern(self) -> None:
        """Complex patterns should be rejected during validation."""
        # Pattern with nested quantifiers
        with pytest.raises(typer.Exit) as exc_info:
            safe_regex_compile(r"(a+)+")
        assert exc_info.value.exit_code == 1

    def test_compile_without_validation(self) -> None:
        """Validation can be disabled for trusted patterns."""
        # This would normally be rejected, but validation is disabled
        pattern = safe_regex_compile(r"(a+)+", validate=False, timeout=0.1)
        assert pattern is not None

    def test_compile_timeout_on_pathological_pattern(self) -> None:
        """Extremely complex patterns should be rejected or timeout."""
        # Create a pathological pattern - this will be caught by validation
        with pytest.raises(typer.Exit):
            safe_regex_compile(r"(a+)+", validate=True)


class TestSafeRegexMatch:
    """Test safe regex matching with timeout."""

    def test_match_simple_pattern(self) -> None:
        """Simple patterns should match successfully."""
        match = safe_regex_match(r"hello", "hello world")
        assert match is not None
        assert match.group() == "hello"

    def test_match_no_match(self) -> None:
        """Non-matching patterns should return None."""
        match = safe_regex_match(r"goodbye", "hello world")
        assert match is None

    def test_match_with_flags(self) -> None:
        """Matching should support regex flags."""
        match = safe_regex_match(r"hello", "HELLO world", flags=re.IGNORECASE)
        assert match is not None

    def test_match_with_compiled_pattern(self) -> None:
        """Matching should work with pre-compiled patterns."""
        pattern = re.compile(r"hello")
        match = safe_regex_match(pattern, "hello world", validate=False)
        assert match is not None

    def test_match_rejects_complex_pattern(self) -> None:
        """Complex patterns should be rejected during validation."""
        with pytest.raises(typer.Exit) as exc_info:
            safe_regex_match(r"(a+)+", "aaaaa")
        assert exc_info.value.exit_code == 1

    def test_match_timeout_on_redos_attack(self) -> None:
        """ReDoS attack patterns should be rejected."""
        # Classic ReDoS pattern: (a+)+ - will be caught by validation
        redos_pattern = r"(a+)+"
        redos_input = "a" * 30 + "!"  # Doesn't match, causes backtracking

        with pytest.raises(typer.Exit):
            safe_regex_match(redos_pattern, redos_input, validate=True)

    def test_match_fast_on_normal_input(self) -> None:
        """Normal patterns should match quickly."""
        start = time.time()
        match = safe_regex_match(r"a+", "a" * 1000)
        elapsed = time.time() - start
        assert match is not None
        assert elapsed < 0.1  # Should be very fast


class TestSafeRegexSearch:
    """Test safe regex search (alias for match)."""

    def test_search_finds_pattern(self) -> None:
        """Search should find patterns anywhere in text."""
        match = safe_regex_search(r"world", "hello world")
        assert match is not None
        assert match.group() == "world"

    def test_search_no_match(self) -> None:
        """Non-matching searches should return None."""
        match = safe_regex_search(r"goodbye", "hello world")
        assert match is None


class TestSafeRegexFindall:
    """Test safe regex findall with timeout."""

    def test_findall_simple_pattern(self) -> None:
        """Simple patterns should find all matches."""
        matches = safe_regex_findall(r"\d+", "1 2 3 4 5")
        assert matches == ["1", "2", "3", "4", "5"]

    def test_findall_no_matches(self) -> None:
        """Non-matching patterns should return empty list."""
        matches = safe_regex_findall(r"\d+", "abc def")
        assert matches == []

    def test_findall_with_flags(self) -> None:
        """Findall should support regex flags."""
        matches = safe_regex_findall(r"hello", "HELLO hello HeLLo", flags=re.IGNORECASE)
        assert len(matches) == 3

    def test_findall_limits_results(self) -> None:
        """Findall should limit results to prevent DoS."""
        # Create input with many matches
        text = " ".join(str(i) for i in range(20000))
        matches = safe_regex_findall(r"\d+", text, max_results=100)
        assert len(matches) == 100  # Should be limited

    def test_findall_timeout_protection(self) -> None:
        """Findall should reject pathological patterns."""
        redos_pattern = r"(a+)+"
        redos_input = "a" * 30 + "!"

        with pytest.raises(typer.Exit):
            safe_regex_findall(redos_pattern, redos_input, validate=True)


class TestReDoSVulnerabilities:
    """Test protection against known ReDoS vulnerability patterns."""

    def test_email_validation_redos(self) -> None:
        """Test protection against email validation ReDoS."""
        # Classic email validation ReDoS pattern
        redos_pattern = r"^([a-zA-Z0-9])(([\-.]|[_]+)?([a-zA-Z0-9]+))*(@){1}[a-z0-9]+[.]{1}(([a-z]{2,3})|([a-z]{2,3}[.]{1}[a-z]{2,3}))$"

        # This pattern has nested quantifiers and should be rejected
        with pytest.raises(typer.Exit):
            safe_regex_compile(redos_pattern)

    def test_url_validation_redos(self) -> None:
        """Test protection against URL validation ReDoS."""
        # Pathological URL pattern
        redos_pattern = r"^(https?://)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$"

        # Should be rejected or timeout
        with pytest.raises(typer.Exit):
            safe_regex_compile(redos_pattern)

    def test_repeated_grouping_attack(self) -> None:
        """Test protection against repeated grouping attacks."""
        dangerous_patterns = [
            r"(a*)*",
            r"(a+)+",
            r"(a|a)*",
            r"(a*)*b",
        ]

        for pattern in dangerous_patterns:
            with pytest.raises(typer.Exit):
                safe_regex_compile(pattern)

    def test_exponential_backtracking(self) -> None:
        """Test protection against exponential backtracking."""
        # Pattern that causes exponential backtracking
        pattern = r"(a+)+"
        text = "a" * 25 + "!"  # No match at end causes backtracking

        with pytest.raises(typer.Exit):
            safe_regex_match(pattern, text, validate=True)


class TestLegitimateUseCases:
    """Test that legitimate use cases still work correctly."""

    def test_simple_proxy_url_pattern(self) -> None:
        """Simple proxy URL matching should work."""
        pattern = r"^(https?|socks[45])://([^:]+):(\d+)$"
        text = "http://proxy.example.com:8080"

        match = safe_regex_match(pattern, text)
        assert match is not None

    def test_ip_address_pattern(self) -> None:
        """IP address matching should work."""
        pattern = r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"
        text = "Server at 192.168.1.1 is running"

        match = safe_regex_match(pattern, text)
        assert match is not None
        assert match.group() == "192.168.1.1"

    def test_log_parsing_pattern(self) -> None:
        """Log parsing patterns should work."""
        pattern = r"\[(\d{4}-\d{2}-\d{2})\] (\w+): (.+)"
        text = "[2024-01-01] INFO: Server started"

        match = safe_regex_match(pattern, text)
        assert match is not None
        assert match.group(1) == "2024-01-01"
        assert match.group(2) == "INFO"

    def test_extract_all_numbers(self) -> None:
        """Extracting all numbers should work efficiently."""
        pattern = r"\d+"
        text = "Ports: 80, 443, 8080, 3000"

        matches = safe_regex_findall(pattern, text)
        assert matches == ["80", "443", "8080", "3000"]

    def test_complex_but_safe_pattern(self) -> None:
        """Complex but safe patterns should work."""
        # Pattern with alternation and groups but no nested quantifiers
        pattern = r"^(http|https)://[a-z0-9-]+\.[a-z]{2,}$"
        text = "https://example.com"

        # This pattern is complex but safe (no nested quantifiers)
        match = safe_regex_match(pattern, text)
        assert match is not None


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_pattern(self) -> None:
        """Empty patterns should be handled."""
        match = safe_regex_match(r"", "text")
        assert match is not None  # Empty pattern matches

    def test_empty_text(self) -> None:
        """Empty text should be handled."""
        match = safe_regex_match(r"hello", "")
        assert match is None

    def test_unicode_pattern(self) -> None:
        """Unicode patterns should work."""
        pattern = r"café"
        text = "I love café"

        match = safe_regex_match(pattern, text)
        assert match is not None

    def test_multiline_pattern(self) -> None:
        """Multiline patterns should work."""
        pattern = r"^start"
        text = "not start\nstart of line"

        match = safe_regex_match(pattern, text, flags=re.MULTILINE)
        assert match is not None

    def test_very_long_text(self) -> None:
        """Very long text should be handled efficiently."""
        pattern = r"needle"
        text = "hay" * 100000 + "needle" + "hay" * 100000

        start = time.time()
        match = safe_regex_match(pattern, text)
        elapsed = time.time() - start

        assert match is not None
        assert elapsed < 1.0  # Should be fast even with long text


class TestSecurityScenarios:
    """Test security scenarios and attack vectors."""

    def test_user_input_sanitization(self) -> None:
        """User input should be sanitized before regex matching."""
        # Simulate user providing a malicious pattern
        user_pattern = "(a+)+" * 10  # Highly nested

        with pytest.raises(typer.Exit):
            safe_regex_compile(user_pattern)

    def test_filter_proxy_list_by_country(self) -> None:
        """Filtering proxy list by country code should be safe."""
        pattern = r"^US:"
        proxy_list = [
            "US:192.168.1.1:8080",
            "UK:192.168.1.2:8080",
            "US:192.168.1.3:8080",
        ]

        us_proxies = [p for p in proxy_list if safe_regex_match(pattern, p)]
        assert len(us_proxies) == 2

    def test_search_logs_with_user_pattern(self) -> None:
        """Searching logs with user-provided pattern should be safe."""
        # User wants to search for failed requests
        user_pattern = r"ERROR: .+"
        log_line = "ERROR: Connection refused to proxy:8080"

        match = safe_regex_match(user_pattern, log_line)
        assert match is not None

    def test_malicious_pattern_in_filter(self) -> None:
        """Malicious patterns in filters should be rejected."""
        # User tries to DoS the system with a malicious filter
        malicious_filter = r"(x+x+)+y"

        with pytest.raises(typer.Exit):
            safe_regex_compile(malicious_filter)
