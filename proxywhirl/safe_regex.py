"""Safe regex pattern matching with ReDoS protection.

This module provides utilities for safely compiling and matching user-provided
regex patterns with timeout protection to prevent Regular Expression Denial of
Service (ReDoS) attacks.
"""

from __future__ import annotations

import multiprocessing as mp
import os
import re
import sys
from re import Pattern
from typing import Any, cast

import typer

# Maximum regex compilation/matching time in seconds.
# Keep the released default stable. Callers that opt into process isolation on
# a spawn-based platform can pass a larger explicit budget when needed.
DEFAULT_REGEX_TIMEOUT = 1.0


# Maximum regex pattern length to prevent extremely long patterns
MAX_PATTERN_LENGTH = 1000

# Maximum number of repetition quantifiers to limit backtracking
MAX_REPETITIONS = 10


class RegexTimeoutError(typer.Exit):
    """Raised when regex compilation or matching exceeds timeout.

    The exception remains catchable as ``typer.Exit`` for 0.3.3 callers while
    providing a specific library exception and a useful error message.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(code=1)
        # ``Exception`` accepted arbitrary constructor arguments in 0.3.3.
        # Click's Exit constructor only accepts an exit code, so restore the
        # released ``BaseException.args`` surface after establishing code 1.
        self.args = args


class RegexComplexityError(typer.Exit):
    """Raised when regex pattern is too complex or dangerous.

    The specific type improves programmatic handling without removing the
    released ``typer.Exit(code=1)`` compatibility surface.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(code=1)
        self.args = args


_NESTED_QUANTIFIER_PATTERNS = (
    r"\([^)]*[*+?{][^)]*\)[*+?{]",  # (...)+ or (...)*
    r"\([^)]*[*+?]\)[*+?]",  # Simpler nested quantifier detection
    r"[*+]{2,}",  # **, ++, etc.
    r"\(.*\|.*\)[*+]",  # (a|a)* or similar
)


def _count_repetitions(pattern: str) -> int:
    """Count repetition quantifiers in a regex pattern.

    Args:
        pattern: Regex pattern string

    Returns:
        Number of repetition quantifiers found
    """
    # Count *, +, ?, {n,m} quantifiers
    count = 0
    count += pattern.count("*")
    count += pattern.count("+")
    count += pattern.count("?")
    count += pattern.count("{")
    return count


def _static_has_nested_quantifiers(pattern: str) -> bool:
    """Detect nested quantifiers with trusted, fixed detector patterns.

    Detectors are constant and simple; the *user* pattern is only the haystack.
    This stays in-process so validation never depends on process isolation
    (which is flaky under pytest-cov / multi-threaded parents).
    """
    for dangerous_pattern in _NESTED_QUANTIFIER_PATTERNS:
        try:
            if re.search(dangerous_pattern, pattern) is not None:
                return True
        except re.error:
            continue
    return False


def _pattern_has_nested_quantifiers(
    pattern: str,
    timeout: float = DEFAULT_REGEX_TIMEOUT,
) -> bool:
    """Detect nested quantifiers that may cause catastrophic backtracking.

    ``timeout`` is retained for API compatibility; detection is static.
    """
    del timeout  # API compatibility only
    return _static_has_nested_quantifiers(pattern)


def validate_regex_pattern(pattern: str, max_length: int = MAX_PATTERN_LENGTH) -> None:
    """Validate a regex pattern for safety.

    Args:
        pattern: Regex pattern to validate
        max_length: Maximum allowed pattern length

    Raises:
        RegexComplexityError: If pattern is too complex or dangerous
    """
    if len(pattern) > max_length:
        raise RegexComplexityError(
            f"Regex pattern too long ({len(pattern)} chars, max {max_length})"
        )

    repetition_count = _count_repetitions(pattern)
    if repetition_count > MAX_REPETITIONS:
        raise RegexComplexityError(
            f"Regex pattern too complex ({repetition_count} repetitions, max {MAX_REPETITIONS})"
        )

    if _pattern_has_nested_quantifiers(pattern):
        raise RegexComplexityError(
            "Regex pattern contains nested quantifiers that may cause catastrophic backtracking"
        )


def _findall_limited(compiled_pattern: Pattern[str], text: str, max_results: int) -> list[Any]:
    """Return re.findall-compatible values without materializing unbounded matches."""
    if max_results <= 0:
        return []

    matches: list[Any] = []
    for match in compiled_pattern.finditer(text):
        if compiled_pattern.groups == 0:
            matches.append(match.group(0))
        elif compiled_pattern.groups == 1:
            matches.append(match.group(1))
        else:
            matches.append(match.groups())

        if len(matches) >= max_results:
            break
    return matches


def _regex_worker(
    conn: Any,
    operation: str,
    pattern: str,
    flags: int,
    text: str,
    max_results: int,
) -> None:
    """Run one regex operation in an isolated child process."""
    try:
        compiled_pattern = re.compile(pattern, flags)
        if operation == "compile":
            payload: Any = True
        elif operation == "search":
            payload = compiled_pattern.search(text) is not None
        elif operation == "findall":
            payload = _findall_limited(compiled_pattern, text, max_results)
        else:
            raise ValueError(f"Unsupported regex operation: {operation}")
        conn.send(("ok", payload))
    except re.error as exc:
        conn.send(("re_error", str(exc)))
    except ValueError as exc:
        conn.send(("value_error", str(exc)))
    except BaseException as exc:  # pragma: no cover - defensive child-process boundary
        conn.send(("error", f"{type(exc).__name__}: {exc}"))
    finally:
        conn.close()


def _regex_process_context() -> Any:
    """Return a process context for isolated regex execution.

    Prefer ``fork`` only while the parent is still single-threaded (fast path).
    Once other threads exist (pytest, coverage, aggregation timers), use
    ``spawn``/``forkserver`` — forking a multi-threaded process has segfaulted
    during quality-gates coverage on macOS.
    """
    import threading

    methods = mp.get_all_start_methods()
    # Main thread only → fork is safe and much faster for per-call isolation.
    if len(threading.enumerate()) <= 1 and "fork" in methods:
        return mp.get_context("fork")
    if "spawn" in methods:
        return mp.get_context("spawn")
    if "forkserver" in methods:
        return mp.get_context("forkserver")
    return mp.get_context()


def _stop_regex_process(process: Any) -> None:
    """Terminate a regex worker that exceeded its budget.

    Never join without a timeout: an uninterruptible child (or a stuck
    wait on macOS under suite load / coverage) previously hung the parent
    long enough for pytest-timeout to fire during quality-gates coverage.
    """
    process.terminate()
    process.join(0.2)
    if process.is_alive():
        process.kill()
        process.join(0.5)


def _coverage_active() -> bool:
    """True when coverage is *actively* measuring this process.

    Merely having ``coverage`` / ``pytest_cov`` importable (or imported by a
    plugin) is not enough — that is true for nearly every pytest run and used
    to disable process isolation unconditionally, leaving in-process ReDoS
    matches unbounded.
    """
    if bool(os.environ.get("COVERAGE_RUN")) or bool(os.environ.get("COVERAGE_PROCESS_START")):
        return True
    if bool(os.environ.get("COV_CORE_SOURCE")) or bool(os.environ.get("COV_CORE_DATAFILE")):
        return True
    # Active tracer (coverage.py sets one while collecting).
    return sys.gettrace() is not None


def _process_isolation_enabled() -> bool:
    """Whether to run match/search/findall in a killable child process.

    Static complexity checks reject nested quantifiers at validate time.
    Process isolation is optional defense-in-depth for residual catastrophic
    backtracking (including ``validate=False`` trusted patterns).

    Default is **off** — spawn isolation costs multi-hundred-ms per call on
    macOS and is flaky under multi-threaded parents. Opt in with
    ``PROXYWHIRL_REGEX_PROCESS_ISOLATION=1``. When isolation is off, nested
    quantifiers are refused in-process (cannot interrupt CPython ``re``)
    instead of hanging the caller.
    """
    flag = os.environ.get("PROXYWHIRL_REGEX_PROCESS_ISOLATION", "").strip().lower()
    if flag in {"0", "false", "no", "off"}:
        return False
    if flag in {"1", "true", "yes", "on"}:
        return not _coverage_active()
    # Default: in-process with static nested-quantifier refusal.
    return False


def _run_regex_inprocess(
    operation: str,
    pattern: str,
    flags: int,
    text: str = "",
    max_results: int = 0,
) -> Any:
    """Execute a regex op in-process (used under coverage / isolation fallback).

    Mirrors ``_regex_worker`` semantics.

    CPython ``re`` cannot be interrupted mid-match from another thread, so
    nested-quantifier patterns are refused here rather than allowed to hang.
    """
    if operation != "compile" and _static_has_nested_quantifiers(pattern):
        raise RegexTimeoutError(
            f"Regex {operation} refused nested quantifiers without process isolation"
        )

    compiled = re.compile(pattern, flags)
    if operation == "compile":
        return True
    if operation == "match":
        return compiled.match(text) is not None
    if operation == "search":
        return compiled.search(text) is not None
    if operation == "findall":
        return _findall_limited(compiled, text, max_results if max_results > 0 else 10000)
    raise ValueError(f"Unknown regex operation: {operation}")


def _run_regex_operation(
    operation: str,
    pattern: str,
    flags: int,
    text: str = "",
    timeout: float = DEFAULT_REGEX_TIMEOUT,
    max_results: int = 0,
) -> Any:
    """Run a regex operation in a killable process with a hard timeout."""
    if timeout <= 0:
        raise RegexTimeoutError(f"Regex {operation} timed out after {timeout}s")

    if not _process_isolation_enabled():
        try:
            return _run_regex_inprocess(operation, pattern, flags, text, max_results)
        except re.error as exc:
            raise re.error(str(exc)) from exc

    ctx = _regex_process_context()
    parent_conn, child_conn = ctx.Pipe(duplex=False)
    process = ctx.Process(
        target=_regex_worker,
        args=(child_conn, operation, pattern, flags, text, max_results),
    )
    process.daemon = True

    try:
        process.start()
    except OSError as exc:
        parent_conn.close()
        child_conn.close()
        raise RegexTimeoutError(f"Regex {operation} worker failed to start") from exc

    child_conn.close()
    process.join(timeout)
    if process.is_alive():
        _stop_regex_process(process)
        parent_conn.close()
        raise RegexTimeoutError(f"Regex {operation} timed out after {timeout}s")

    try:
        if not parent_conn.poll():
            raise RegexTimeoutError(
                f"Regex {operation} worker exited without a result (exit code {process.exitcode})"
            )
        status, payload = parent_conn.recv()
    finally:
        parent_conn.close()

    if status == "ok":
        return payload
    if status == "re_error":
        raise re.error(payload)
    if status == "value_error":
        raise ValueError(payload)
    raise RegexTimeoutError(f"Regex {operation} worker failed: {payload}")


def _compile_with_timeout(pattern: str, flags: int, timeout: float) -> Pattern[str]:
    """Compile regex after caller-side complexity validation.

    Args:
        pattern: Regex pattern
        flags: Regex flags
        timeout: Timeout in seconds

    Returns:
        Compiled regex pattern

    Raises:
        RegexTimeoutError: If compilation exceeds timeout
    """
    if timeout <= 0:
        raise RegexTimeoutError(f"Regex compilation timed out after {timeout}s: {pattern[:50]}...")
    return re.compile(pattern, flags)


def _match_with_timeout(
    pattern: Pattern[str],
    text: str,
    timeout: float,
) -> re.Match[str] | None:
    """Search regex with timeout using a killable worker process.

    Args:
        pattern: Compiled regex pattern
        text: Text to match against
        timeout: Timeout in seconds

    Returns:
        Match-like object or None

    Raises:
        RegexTimeoutError: If matching exceeds timeout
    """
    try:
        matched = cast(
            bool,
            _run_regex_operation(
                "search",
                pattern.pattern,
                pattern.flags,
                text,
                timeout,
                max_results=0,
            ),
        )
    except RegexTimeoutError as e:
        raise RegexTimeoutError(f"Regex matching timed out after {timeout}s") from e

    if not matched:
        return None
    # The bounded worker has proved the deterministic pattern/text pair
    # completes. Re-run it to return the native, non-picklable Match object
    # exposed by the released API.
    return pattern.search(text)


def safe_regex_compile(
    pattern: str,
    flags: int = 0,
    timeout: float = DEFAULT_REGEX_TIMEOUT,
    validate: bool = True,
) -> Pattern[str]:
    """Safely compile a regex pattern with timeout protection.

    Args:
        pattern: Regex pattern string
        flags: Regex compilation flags (re.IGNORECASE, etc.)
        timeout: Maximum time allowed for compilation in seconds
        validate: Whether to validate pattern complexity first

    Returns:
        Compiled regex pattern

    Raises:
        RegexTimeoutError: If compilation exceeds timeout
        RegexComplexityError: If pattern is rejected during validation
    """
    if validate:
        validate_regex_pattern(pattern)

    return _compile_with_timeout(pattern, flags, timeout)


def safe_regex_match(
    pattern: str | Pattern[str],
    text: str,
    flags: int = 0,
    timeout: float = DEFAULT_REGEX_TIMEOUT,
    validate: bool = True,
) -> re.Match[str] | None:
    """Safely match a regex pattern against text with timeout protection.

    Args:
        pattern: Regex pattern (string or compiled pattern)
        text: Text to match against
        flags: Regex flags (only used if pattern is a string)
        timeout: Maximum time allowed for matching in seconds
        validate: Whether to validate pattern complexity first (only for string patterns)

    Returns:
        Match object if pattern matches, None otherwise

    Raises:
        RegexTimeoutError: If matching exceeds timeout
        RegexComplexityError: If pattern is rejected during validation
    """
    if isinstance(pattern, str):
        compiled_pattern = safe_regex_compile(pattern, flags, timeout, validate)
    else:
        compiled_pattern = pattern

    return _match_with_timeout(compiled_pattern, text, timeout)


def safe_regex_search(
    pattern: str | Pattern[str],
    text: str,
    flags: int = 0,
    timeout: float = DEFAULT_REGEX_TIMEOUT,
    validate: bool = True,
) -> re.Match[str] | None:
    """Safely search for a regex pattern in text with timeout protection.

    This is an alias for safe_regex_match for API compatibility.

    Args:
        pattern: Regex pattern (string or compiled pattern)
        text: Text to search in
        flags: Regex flags (only used if pattern is a string)
        timeout: Maximum time allowed for searching in seconds
        validate: Whether to validate pattern complexity first (only for string patterns)

    Returns:
        Match object if pattern found, None otherwise

    Raises:
        RegexTimeoutError: If searching exceeds timeout
        RegexComplexityError: If pattern is rejected during validation
    """
    return safe_regex_match(pattern, text, flags, timeout, validate)


def safe_regex_findall(
    pattern: str | Pattern[str],
    text: str,
    flags: int = 0,
    timeout: float = DEFAULT_REGEX_TIMEOUT,
    validate: bool = True,
    max_results: int = 10000,
) -> list[str]:
    """Safely find all matches of a regex pattern in text with timeout protection.

    Args:
        pattern: Regex pattern (string or compiled pattern)
        text: Text to search in
        flags: Regex flags (only used if pattern is a string)
        timeout: Maximum time allowed for searching in seconds
        validate: Whether to validate pattern complexity first (only for string patterns)
        max_results: Maximum number of results to return (prevents DoS)

    Returns:
        List of matching strings

    Raises:
        RegexTimeoutError: If searching exceeds timeout
        RegexComplexityError: If pattern is rejected during validation
    """
    if isinstance(pattern, str):
        if validate:
            validate_regex_pattern(pattern)
        pattern_text = pattern
        pattern_flags = flags
    else:
        pattern_text = pattern.pattern
        pattern_flags = pattern.flags

    return cast(
        list[str],
        _run_regex_operation(
            "findall",
            pattern_text,
            pattern_flags,
            text,
            timeout,
            max_results,
        ),
    )
