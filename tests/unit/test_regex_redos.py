"""Tests for ReDoS protection in safe regex utilities.

Session 5 SA-5.2: Validates that evil regex patterns (e.g. ``(a+)+$``)
time out or are rejected by the safe regex module.
"""

from __future__ import annotations

import re

import pytest
import typer

from proxywhirl.safe_regex import (
    MAX_PATTERN_LENGTH,
    MAX_REPETITIONS,
    RegexTimeoutError,
    safe_regex_compile,
    safe_regex_findall,
    safe_regex_match,
    safe_regex_search,
    validate_regex_pattern,
)

# ============================================================================
# EVIL PATTERN REJECTION
# ============================================================================


class TestEvilPatternRejection:
    """Test that known ReDoS-prone patterns are rejected."""

    @pytest.mark.timeout(5)
    @pytest.mark.parametrize(
        "evil_pattern",
        [
            r"(a+)+$",
            r"(a+)+",
            r"(a*)*",
            r"(a+)*",
            r"(a?)+",
            r"(.*)*",
            r"(a|a)*",
            r"(a*)*b",
            r"(x+x+)+y",
        ],
    )
    def test_evil_pattern_rejected_by_validation(self, evil_pattern: str) -> None:
        """Each evil pattern must raise typer.Exit during validation."""
        with pytest.raises(typer.Exit) as exc_info:
            validate_regex_pattern(evil_pattern)
        assert exc_info.value.exit_code == 1

    @pytest.mark.timeout(5)
    @pytest.mark.parametrize(
        "evil_pattern",
        [
            r"(a+)+$",
            r"(a+)+",
            r"(a*)*",
            r"(a+)*",
        ],
    )
    def test_evil_pattern_rejected_by_compile(self, evil_pattern: str) -> None:
        """``safe_regex_compile`` must reject evil patterns."""
        with pytest.raises(typer.Exit) as exc_info:
            safe_regex_compile(evil_pattern)
        assert exc_info.value.exit_code == 1

    @pytest.mark.timeout(5)
    @pytest.mark.parametrize(
        "evil_pattern",
        [
            r"(a+)+$",
            r"(a+)+",
            r"(a*)*",
        ],
    )
    def test_evil_pattern_rejected_by_match(self, evil_pattern: str) -> None:
        """ "``safe_regex_match`` must reject evil patterns before matching."""
        with pytest.raises(typer.Exit) as exc_info:
            safe_regex_match(evil_pattern, "aaaaab")
        assert exc_info.value.exit_code == 1

    @pytest.mark.timeout(5)
    def test_classic_redos_input_with_validation(self) -> None:
        """Classic ReDoS: (a+)+ with input that causes backtracking."""
        redos_input = "a" * 30 + "!"
        with pytest.raises(typer.Exit):
            safe_regex_match(r"(a+)+", redos_input, validate=True)

    @pytest.mark.timeout(5)
    def test_email_redos_pattern_rejected(self) -> None:
        """A known email-validation ReDoS pattern must be rejected."""
        pattern = (
            r"^([a-zA-Z0-9])(([-.]|[+]+)?([a-zA-Z0-9]+))*"
            r"(@){1}[a-z0-9]+[.]{1}"
            r"(([a-z]{2,3})|([a-z]{2,3}[.]{1}[a-z]{2,3}))$"
        )
        with pytest.raises(typer.Exit):
            safe_regex_compile(pattern)

    @pytest.mark.timeout(5)
    def test_url_redos_pattern_rejected(self) -> None:
        """A known URL-validation ReDoS pattern must be rejected."""
        pattern = r"^(https?://)?([\da-z\.-]+)\.([a-z\.]{2,6})([/\w \.-]*)*\/?$"
        with pytest.raises(typer.Exit):
            safe_regex_compile(pattern)


# ============================================================================
# SAFE PATTERN ACCEPTANCE
# ============================================================================


class TestSafePatternAcceptance:
    """Test that benign patterns continue to work."""

    @pytest.mark.timeout(5)
    @pytest.mark.parametrize(
        "safe_pattern",
        [
            r"^hello$",
            r"\d{1,3}",
            r"[a-zA-Z_][a-zA-Z0-9_]*",
            r"^(http|https)://[a-z0-9.-]+\.[a-z]{2,}$",
            r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
            r"^(https?|socks[45])://([^:]+):(\d+)$",
        ],
    )
    def test_safe_pattern_compiles(self, safe_pattern: str) -> None:
        """Benign patterns must compile successfully."""
        compiled = safe_regex_compile(safe_pattern)
        assert isinstance(compiled, re.Pattern)

    @pytest.mark.timeout(5)
    def test_safe_pattern_matches(self) -> None:
        """A safe pattern must match expected input."""
        match = safe_regex_match(r"hello", "hello world")
        assert match is not None
        assert match.group() == "hello"

    @pytest.mark.timeout(5)
    def test_safe_pattern_search(self) -> None:
        """A safe pattern must search successfully."""
        match = safe_regex_search(r"world", "hello world")
        assert match is not None
        assert match.group() == "world"

    @pytest.mark.timeout(5)
    def test_safe_pattern_findall(self) -> None:
        """A safe pattern must find all matches."""
        matches = safe_regex_findall(r"\d+", "1 2 3 4 5")
        assert matches == ["1", "2", "3", "4", "5"]

    @pytest.mark.timeout(5)
    def test_safe_pattern_with_flags(self) -> None:
        """Safe patterns must support regex flags."""
        compiled = safe_regex_compile(r"hello", flags=re.IGNORECASE)
        assert compiled.match("HELLO") is not None


# ============================================================================
# COMPLEXITY LIMITS
# ============================================================================


class TestComplexityLimits:
    """Test length and repetition limits."""

    def test_pattern_too_long_rejected(self) -> None:
        """Patterns longer than ``MAX_PATTERN_LENGTH`` must be rejected."""
        long_pattern = "a" * (MAX_PATTERN_LENGTH + 1)
        with pytest.raises(typer.Exit) as exc_info:
            validate_regex_pattern(long_pattern)
        assert exc_info.value.exit_code == 1

    def test_pattern_max_length_accepted(self) -> None:
        """Patterns exactly at ``MAX_PATTERN_LENGTH`` must be accepted
        if otherwise safe."""
        pattern = "a" * MAX_PATTERN_LENGTH
        validate_regex_pattern(pattern)  # should not raise

    def test_too_many_repetitions_rejected(self) -> None:
        """Patterns with more than ``MAX_REPETITIONS`` quantifiers must be rejected."""
        pattern = "a*" * (MAX_REPETITIONS + 1)
        with pytest.raises(typer.Exit) as exc_info:
            validate_regex_pattern(pattern)
        assert exc_info.value.exit_code == 1

    def test_repetition_at_limit_accepted(self) -> None:
        """Patterns with exactly ``MAX_REPETITIONS`` quantifiers must be accepted."""
        pattern = "a*" * MAX_REPETITIONS
        validate_regex_pattern(pattern)  # should not raise


# ============================================================================
# TIMEOUT PATHS
# ============================================================================


class TestTimeoutProtection:
    """Test that regex operations timeout rather than hanging."""

    @pytest.mark.slow
    @pytest.mark.timeout(10)
    def test_compile_timeout_on_pathological_pattern(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Extremely slow compilation must trigger timeout path.

        We force the timeout by monkey-patching ThreadPoolExecutor to
        always raise FuturesTimeoutError.
        """
        from concurrent.futures import TimeoutError as FuturesTimeoutError

        import proxywhirl.safe_regex as safe_regex_module

        class _TimeoutFuture:
            def result(self, timeout: float | None = None) -> None:
                raise FuturesTimeoutError()

        class _TimeoutExecutor:
            def __init__(self, *args: object, **kwargs: object) -> None:
                pass

            def __enter__(self):
                return self

            def __exit__(self, *args: object) -> bool:
                return False

            def submit(self, *args: object, **kwargs: object) -> _TimeoutFuture:
                return _TimeoutFuture()

        monkeypatch.setattr(safe_regex_module, "ThreadPoolExecutor", _TimeoutExecutor)

        with pytest.raises(typer.Exit) as exc_info:
            safe_regex_compile(r"a+b", validate=False, timeout=0.01)
        assert exc_info.value.exit_code == 1

    @pytest.mark.slow
    @pytest.mark.timeout(10)
    def test_match_timeout_on_slow_match(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Slow matching must trigger timeout path."""
        from concurrent.futures import TimeoutError as FuturesTimeoutError

        import proxywhirl.safe_regex as safe_regex_module

        class _TimeoutFuture:
            def result(self, timeout: float | None = None) -> None:
                raise FuturesTimeoutError()

        class _TimeoutExecutor:
            def __init__(self, *args: object, **kwargs: object) -> None:
                pass

            def __enter__(self):
                return self

            def __exit__(self, *args: object) -> bool:
                return False

            def submit(self, *args: object, **kwargs: object) -> _TimeoutFuture:
                return _TimeoutFuture()

        monkeypatch.setattr(safe_regex_module, "ThreadPoolExecutor", _TimeoutExecutor)

        compiled = re.compile(r"a+")
        with pytest.raises(typer.Exit) as exc_info:
            safe_regex_match(compiled, "aaaa", validate=False, timeout=0.01)
        assert exc_info.value.exit_code == 1

    @pytest.mark.slow
    @pytest.mark.timeout(10)
    def test_findall_timeout_on_slow_findall(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Slow findall must trigger timeout path."""
        from concurrent.futures import TimeoutError as FuturesTimeoutError

        import proxywhirl.safe_regex as safe_regex_module

        class _TimeoutFuture:
            def result(self, timeout: float | None = None) -> None:
                raise FuturesTimeoutError()

        class _TimeoutExecutor:
            def __init__(self, *args: object, **kwargs: object) -> None:
                pass

            def __enter__(self):
                return self

            def __exit__(self, *args: object) -> bool:
                return False

            def submit(self, *args: object, **kwargs: object) -> _TimeoutFuture:
                return _TimeoutFuture()

        monkeypatch.setattr(safe_regex_module, "ThreadPoolExecutor", _TimeoutExecutor)

        compiled = re.compile(r"a+")
        with pytest.raises(typer.Exit) as exc_info:
            safe_regex_findall(compiled, "aaaa", validate=False, timeout=0.01)
        assert exc_info.value.exit_code == 1


# ============================================================================
# EDGE CASES
# ============================================================================


class TestEdgeCases:
    """Boundary conditions for safe regex."""

    @pytest.mark.timeout(5)
    def test_empty_pattern(self) -> None:
        """Empty pattern should compile and match."""
        compiled = safe_regex_compile(r"")
        assert compiled.match("anything") is not None

    @pytest.mark.timeout(5)
    def test_empty_text(self) -> None:
        """Matching against empty text should return None for non-empty pattern."""
        match = safe_regex_match(r"hello", "")
        assert match is None

    @pytest.mark.timeout(5)
    def test_unicode_pattern(self) -> None:
        """Unicode patterns should work."""
        match = safe_regex_match(r"café", "I love café")
        assert match is not None

    @pytest.mark.timeout(5)
    def test_very_long_safe_text(self) -> None:
        """Very long text with a simple pattern should complete quickly."""
        text = "hay" * 10000 + "needle" + "hay" * 10000
        match = safe_regex_match(r"needle", text)
        assert match is not None

    @pytest.mark.timeout(5)
    def test_disabling_validation_allows_dangerous_pattern(self) -> None:
        """When ``validate=False``, dangerous patterns compile (but may still timeout)."""
        compiled = safe_regex_compile(r"(a+)+$", validate=False, timeout=0.5)
        assert isinstance(compiled, re.Pattern)

    @pytest.mark.timeout(5)
    def test_findall_limits_results(self) -> None:
        """``safe_regex_findall`` must respect ``max_results``."""
        text = " ".join(str(i) for i in range(500))
        matches = safe_regex_findall(r"\d+", text, max_results=50)
        assert len(matches) == 50

    def test_regex_timeout_error_is_exception(self) -> None:
        """ "``RegexTimeoutError`` must be an Exception subclass."""
        assert issubclass(RegexTimeoutError, Exception)


# ============================================================================
# COUNT CHECK
# ============================================================================


def test_at_least_fifteen_tests_exist() -> None:
    """Meta-test: ensure this module contains >= 15 test functions."""
    import inspect
    import sys

    module = sys.modules[__name__]

    def _collect_tests(obj):
        tests = []
        for name, member in inspect.getmembers(obj):
            if name.startswith("test_") and (
                inspect.isfunction(member) or inspect.ismethod(member)
            ):
                tests.append(member)
        return tests

    test_funcs = _collect_tests(module)
    for _, cls in inspect.getmembers(module, inspect.isclass):
        test_funcs.extend(_collect_tests(cls))

    assert len(test_funcs) >= 15, f"Expected >= 15 tests, found {len(test_funcs)}"
