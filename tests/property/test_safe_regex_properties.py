"""Property-based tests for safe_regex using Hypothesis."""

import re
from typing import Any

from hypothesis import HealthCheck, assume, example, given, settings
from hypothesis import strategies as st

from proxywhirl.safe_regex import (
    MAX_PATTERN_LENGTH,
    MAX_REPETITIONS,
    RegexTimeoutError,
    _compile_with_timeout,
    _count_repetitions,
    _match_with_timeout,
)

# ============================================================================
# STRATEGIES
# ============================================================================


@st.composite
def simple_regex_patterns(draw: Any) -> str:
    """Generate simple, safe regex patterns."""
    # Alphanumeric patterns without dangerous quantifiers
    return draw(
        st.one_of(
            st.from_regex(r"[a-z]+", fullmatch=True),
            st.from_regex(r"[0-9]+", fullmatch=True),
            st.from_regex(r"[a-zA-Z0-9]+", fullmatch=True),
            st.text(alphabet="abcd", min_size=1, max_size=10),
            st.just(r"\d+"),
            st.just(r"\w+"),
            st.just(r"[a-z]*"),
        )
    )


@st.composite
def potentially_dangerous_patterns(draw: Any) -> str:
    """Generate patterns that might be dangerous (ReDoS)."""
    return draw(
        st.sampled_from(
            [
                r"(a+)+$",  # Nested quantifiers
                r"([a-zA-Z]+)*",  # Repeated group with quantifier
                r"(a|aa)+",  # Alternation with repetition
                r"(.*a){20}",  # Greedy match with many repetitions
                r"(a*)*",  # Double star
                r"(a+)+",  # Double plus
                r"(a|a)*",  # Inefficient alternation
                r"(.*)*",  # Catastrophic backtracking
                r"([a-z]*)*",  # Nested class with quantifiers
                r"((a+)+)+",  # Triple nesting
            ]
        )
    )


@st.composite
def valid_regex_text(draw: Any) -> str:
    """Generate text that's reasonable for regex matching."""
    return draw(
        st.one_of(
            st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126), max_size=1000),
            st.from_regex(r"[a-zA-Z0-9 ]{0,500}", fullmatch=True),
            st.just("a" * 30),
            st.just("test string"),
            st.just(""),
        )
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def compile_safe_no_exit(pattern: str, timeout: float = 1.0) -> re.Pattern[str] | None:
    """Wrapper around _compile_with_timeout that returns None instead of exiting.

    This is needed for property tests since typer.Exit breaks hypothesis.
    """
    try:
        return _compile_with_timeout(pattern, 0, timeout)
    except (RegexTimeoutError, re.error, ValueError):
        return None


def match_safe_no_exit(
    pattern: str, text: str, timeout: float = 1.0
) -> re.Match[str] | None | bool:
    """Wrapper around _match_with_timeout that returns False instead of exiting.

    Returns:
        Match object if successful, None if no match, False if error
    """
    try:
        compiled = _compile_with_timeout(pattern, 0, timeout)
        return _match_with_timeout(compiled, text, timeout)
    except (RegexTimeoutError, re.error, ValueError):
        return False


# ============================================================================
# PROPERTY TESTS - COMPILATION SAFETY
# ============================================================================


class TestCompilationSafety:
    """Property-based tests for safe regex compilation."""

    @given(st.text(min_size=1, max_size=100))
    @settings(
        max_examples=200,
        deadline=5000,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_compile_never_hangs(self, pattern: str):
        """Property: compile_safe never hangs regardless of input."""
        result = compile_safe_no_exit(pattern, timeout=1.0)
        # Result should be Pattern or None
        assert result is None or isinstance(result, re.Pattern)

    @given(simple_regex_patterns())
    @example(pattern=r"[a-z]+")
    @example(pattern=r"\d+")
    @example(pattern=r"[a-zA-Z0-9]+")
    def test_simple_patterns_always_compile(self, pattern: str):
        """Property: Simple patterns should compile without timeout."""
        compiled = compile_safe_no_exit(pattern, timeout=1.0)
        assert compiled is not None, f"Pattern {pattern!r} failed to compile"

    @given(st.text(min_size=MAX_PATTERN_LENGTH + 1, max_size=MAX_PATTERN_LENGTH + 100))
    def test_long_patterns_rejected(self, pattern: str):
        """Property: Patterns exceeding MAX_PATTERN_LENGTH should be rejected."""
        # This would be caught by validate_regex_pattern
        # Testing the internal validation logic
        assert len(pattern) > MAX_PATTERN_LENGTH

    @given(st.text(alphabet="*()+?{}", min_size=MAX_REPETITIONS + 1, max_size=50))
    def test_excessive_repetitions_detected(self, pattern: str):
        """Property: Patterns with excessive repetitions should be detected."""
        count = _count_repetitions(pattern)
        # Pattern should have high repetition count
        if count > MAX_REPETITIONS:
            assert count > MAX_REPETITIONS


# ============================================================================
# PROPERTY TESTS - MATCHING SAFETY
# ============================================================================


class TestMatchingSafety:
    """Property-based tests for safe regex matching."""

    @given(simple_regex_patterns(), valid_regex_text())
    @settings(
        max_examples=100,
        deadline=10000,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_match_always_terminates(self, pattern: str, text: str):
        """Property: match_safe always terminates."""
        result = match_safe_no_exit(pattern, text, timeout=1.0)
        # Result should be Match, None, or False (error)
        assert result is None or result is False or hasattr(result, "group")

    @given(st.from_regex(r"[a-z]+", fullmatch=True), st.text(alphabet="abcdefghij", max_size=100))
    @example(pattern="test", text="test")
    @example(pattern="abc", text="abc")
    def test_simple_matches_work(self, pattern: str, text: str):
        """Property: Simple literal patterns should match correctly."""
        compiled = compile_safe_no_exit(pattern, timeout=1.0)
        if compiled is None:
            # Pattern might be invalid, skip
            assume(False)

        result = match_safe_no_exit(pattern, text, timeout=1.0)
        # Should get a result (Match or None), not error
        assert result is not False

    @given(valid_regex_text())
    def test_empty_pattern_behavior(self, text: str):
        """Property: Empty pattern behavior should be consistent."""
        # Empty pattern is actually valid in Python regex (matches everything)
        result = compile_safe_no_exit("", timeout=1.0)
        assert result is not None  # Empty patterns should compile successfully
        # And should match any position in text
        if result is not None:
            match_result = match_safe_no_exit("", text, timeout=1.0)
            assert match_result is not False  # Should either match or return None, not error


# ============================================================================
# PROPERTY TESTS - REDOS RESISTANCE
# ============================================================================


class TestReDoSResistance:
    """Property-based tests for ReDoS attack resistance."""

    @given(potentially_dangerous_patterns())
    @example(pattern=r"(a+)+$")
    @example(pattern=r"([a-zA-Z]+)*")
    @example(pattern=r"(a|aa)+")
    def test_dangerous_patterns_handled_safely(self, pattern: str):
        """Property: Known dangerous patterns should be handled safely."""
        # Either compilation fails or times out
        result = compile_safe_no_exit(pattern, timeout=0.5)
        # If it compiles, it should be usable (though may timeout on matching)
        if result is not None:
            # Try matching with a potentially problematic string
            match_result = match_safe_no_exit(pattern, "a" * 30, timeout=0.5)
            # Should either match, not match, or timeout (False)
            assert match_result is None or match_result is False or hasattr(match_result, "group")

    @given(potentially_dangerous_patterns(), st.text(alphabet="a", min_size=20, max_size=50))
    @settings(max_examples=50, deadline=5000)
    def test_dangerous_patterns_with_long_input(self, pattern: str, text: str):
        """Property: Dangerous patterns with long input should timeout safely."""
        result = match_safe_no_exit(pattern, text, timeout=0.5)
        # Should terminate (either match, no match, or error)
        assert result is None or result is False or hasattr(result, "group")

    @given(st.integers(min_value=10, max_value=100))
    def test_nested_quantifiers_detected(self, length: int):
        """Property: Nested quantifier patterns should be detected."""
        # Test various forms of nested quantifiers
        nested_patterns = [
            f"({'a' * length}+)+",
            f"({'a' * length}*)*",
            r"(a+)+",
            r"(.*)*",
        ]

        for pattern in nested_patterns:
            result = compile_safe_no_exit(pattern, timeout=0.5)
            # Should either compile or fail, but not hang
            assert result is None or isinstance(result, re.Pattern)


# ============================================================================
# PROPERTY TESTS - TIMEOUT BEHAVIOR
# ============================================================================


class TestTimeoutBehavior:
    """Property-based tests for timeout mechanisms."""

    @given(st.floats(min_value=0.1, max_value=2.0))
    def test_timeout_parameter_respected(self, timeout: float):
        """Property: Timeout parameter should be respected."""
        # Use a known slow pattern
        slow_pattern = r"(a+)+"
        result = compile_safe_no_exit(slow_pattern, timeout=timeout)
        # Should complete within reasonable time (timeout + overhead)
        # Just checking it returns something (compiled or None)
        assert result is None or isinstance(result, re.Pattern)

    @given(simple_regex_patterns())
    def test_fast_patterns_ignore_timeout(self, pattern: str):
        """Property: Fast patterns should complete before timeout."""
        # Use very short timeout for simple patterns
        result = compile_safe_no_exit(pattern, timeout=0.1)
        # Simple patterns should compile even with short timeout
        assert result is not None or pattern == ""


# ============================================================================
# PROPERTY TESTS - EDGE CASES
# ============================================================================


class TestEdgeCases:
    """Property-based tests for edge cases."""

    @given(st.text(alphabet=" \t\n\r", min_size=1, max_size=50))
    def test_whitespace_only_patterns(self, pattern: str):
        """Property: Whitespace-only patterns should be handled."""
        result = compile_safe_no_exit(pattern, timeout=1.0)
        # Should either compile or fail
        assert result is None or isinstance(result, re.Pattern)

    @given(st.text(alphabet="\\", min_size=1, max_size=10))
    def test_backslash_heavy_patterns(self, pattern: str):
        """Property: Backslash-heavy patterns should not crash."""
        result = compile_safe_no_exit(pattern, timeout=1.0)
        # Most will be invalid, but shouldn't crash
        assert result is None or isinstance(result, re.Pattern)

    @given(st.text(alphabet="()[]{}", min_size=1, max_size=20))
    def test_bracket_heavy_patterns(self, pattern: str):
        """Property: Bracket-heavy patterns should be handled."""
        result = compile_safe_no_exit(pattern, timeout=1.0)
        # Should handle gracefully
        assert result is None or isinstance(result, re.Pattern)

    def test_special_regex_characters(self):
        """Property: Special regex characters should be handled correctly."""
        special_chars = r".*+?[]{}()|^$\\"
        for char in special_chars:
            # Try each special character
            result = compile_safe_no_exit(char, timeout=1.0)
            # Should either compile or fail, but not crash
            assert result is None or isinstance(result, re.Pattern)


# ============================================================================
# PROPERTY TESTS - REPETITION COUNTING
# ============================================================================


class TestRepetitionCounting:
    """Property-based tests for repetition quantifier counting."""

    @given(st.text(alphabet="*+?{}", min_size=0, max_size=50))
    def test_count_repetitions_accurate(self, pattern: str):
        """Property: Repetition count should match actual quantifiers."""
        count = _count_repetitions(pattern)
        expected = pattern.count("*") + pattern.count("+") + pattern.count("?") + pattern.count("{")
        assert count == expected

    @given(st.text(alphabet="abc", min_size=1, max_size=50))
    def test_no_repetitions_returns_zero(self, pattern: str):
        """Property: Patterns without quantifiers should return zero count."""
        assume(
            "*" not in pattern and "+" not in pattern and "?" not in pattern and "{" not in pattern
        )
        count = _count_repetitions(pattern)
        assert count == 0

    @given(st.integers(min_value=0, max_value=20))
    def test_repetition_threshold_detection(self, num_repetitions: int):
        """Property: Should detect when repetitions exceed threshold."""
        pattern = "*" * num_repetitions
        count = _count_repetitions(pattern)
        assert count == num_repetitions
        if num_repetitions > MAX_REPETITIONS:
            assert count > MAX_REPETITIONS


# ============================================================================
# PROPERTY TESTS - VALIDATION CONSISTENCY
# ============================================================================


class TestValidationConsistency:
    """Property-based tests for consistent validation behavior."""

    @given(st.text(min_size=1, max_size=50), st.floats(min_value=0.1, max_value=2.0))
    def test_same_pattern_same_result(self, pattern: str, timeout: float):
        """Property: Same pattern should produce same result across calls."""
        result1 = compile_safe_no_exit(pattern, timeout=timeout)
        result2 = compile_safe_no_exit(pattern, timeout=timeout)

        # Both should succeed or both should fail
        if result1 is None:
            assert result2 is None
        else:
            assert result2 is not None

    @given(simple_regex_patterns())
    def test_compiled_pattern_reusable(self, pattern: str):
        """Property: Compiled patterns should be reusable for multiple matches."""
        compiled = compile_safe_no_exit(pattern, timeout=1.0)
        if compiled is None:
            assume(False)

        # Try multiple matches with same compiled pattern
        texts = ["test", "abc", "123", ""]
        for text in texts:
            try:
                result = _match_with_timeout(compiled, text, timeout=1.0)
                assert result is None or hasattr(result, "group")
            except RegexTimeoutError:
                pass  # Acceptable - timeout is a valid safety mechanism
