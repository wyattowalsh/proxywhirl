"""Safe regex pattern matching with ReDoS protection.

This module provides utilities for safely compiling and matching user-provided
regex patterns with timeout protection to prevent Regular Expression Denial of
Service (ReDoS) attacks.
"""

from __future__ import annotations

import multiprocessing as mp
import re
from re import Pattern
from typing import Any, cast

import typer

# Maximum regex compilation/matching time in seconds
DEFAULT_REGEX_TIMEOUT = 1.0

# Maximum regex pattern length to prevent extremely long patterns
MAX_PATTERN_LENGTH = 1000

# Maximum number of repetition quantifiers to limit backtracking
MAX_REPETITIONS = 10


class RegexTimeoutError(Exception):
    """Raised when regex compilation or matching exceeds timeout."""

    pass


class RegexComplexityError(Exception):
    """Raised when regex pattern is too complex or dangerous."""

    pass


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


def validate_regex_pattern(pattern: str, max_length: int = MAX_PATTERN_LENGTH) -> None:
    """Validate a regex pattern for safety.

    Args:
        pattern: Regex pattern to validate
        max_length: Maximum allowed pattern length

    Raises:
        RegexComplexityError: If pattern is too complex or dangerous
        typer.Exit: If pattern is rejected
    """
    # Check pattern length
    if len(pattern) > max_length:
        typer.secho(
            f"Error: Regex pattern too long ({len(pattern)} chars, max {max_length})",
            err=True,
            fg="red",
        )
        raise typer.Exit(code=1)

    # Check for excessive repetition quantifiers (potential catastrophic backtracking)
    repetition_count = _count_repetitions(pattern)
    if repetition_count > MAX_REPETITIONS:
        typer.secho(
            f"Error: Regex pattern too complex ({repetition_count} repetitions, max {MAX_REPETITIONS})",
            err=True,
            fg="red",
        )
        typer.secho(
            "This pattern may cause performance issues (ReDoS attack)",
            err=True,
            fg="yellow",
        )
        raise typer.Exit(code=1)

    # Check for nested quantifiers (e.g., (a+)+ or (a*)*) which are particularly dangerous
    nested_patterns = [
        r"\([^)]*[*+?{][^)]*\)[*+?{]",  # (...)+ or (...)*
        r"\([^)]*[*+?]\)[*+?]",  # Simpler nested quantifier detection
        r"[*+]{2,}",  # **, ++, etc.
        r"\(.*\|.*\)[*+]",  # (a|a)* or similar
    ]
    for dangerous_pattern in nested_patterns:
        if re.search(dangerous_pattern, pattern):
            typer.secho(
                "Error: Regex pattern contains nested quantifiers",
                err=True,
                fg="red",
            )
            typer.secho(
                "Nested quantifiers like (a+)+ can cause catastrophic backtracking",
                err=True,
                fg="yellow",
            )
            raise typer.Exit(code=1)


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
    """Use fork when available to keep per-call isolation practical."""
    if "fork" in mp.get_all_start_methods():
        return mp.get_context("fork")
    return mp.get_context()


def _stop_regex_process(process: Any) -> None:
    """Terminate a regex worker that exceeded its budget."""
    process.terminate()
    process.join(0.2)
    if process.is_alive():
        process.kill()
        process.join()


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
                f"Regex {operation} worker exited without a result "
                f"(exit code {process.exitcode})"
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
        raise RegexTimeoutError(
            f"Regex compilation timed out after {timeout}s: {pattern[:50]}..."
        )
    return re.compile(pattern, flags)


def _match_with_timeout(pattern: Pattern[str], text: str, timeout: float) -> re.Match[str] | None:
    """Search regex with timeout using a killable worker process.

    Args:
        pattern: Compiled regex pattern
        text: Text to match against
        timeout: Timeout in seconds

    Returns:
        Match object or None

    Raises:
        RegexTimeoutError: If matching exceeds timeout
    """
    try:
        matched = cast(
            bool,
            _run_regex_operation("search", pattern.pattern, pattern.flags, text, timeout),
        )
    except RegexTimeoutError as e:
        raise RegexTimeoutError(f"Regex matching timed out after {timeout}s") from e

    if not matched:
        return None
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
        typer.Exit: If pattern is rejected during validation
    """
    # Validate pattern complexity
    if validate:
        validate_regex_pattern(pattern)

    # Compile with timeout
    try:
        return _compile_with_timeout(pattern, flags, timeout)
    except RegexTimeoutError as e:
        typer.secho(
            f"Error: {e}",
            err=True,
            fg="red",
        )
        typer.secho(
            "This pattern may be too complex or malicious (ReDoS attack)",
            err=True,
            fg="yellow",
        )
        raise typer.Exit(code=1)


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
        typer.Exit: If pattern is rejected during validation
    """
    # Compile pattern if needed
    if isinstance(pattern, str):
        compiled_pattern = safe_regex_compile(pattern, flags, timeout, validate)
    else:
        compiled_pattern = pattern

    # Match with timeout
    try:
        return _match_with_timeout(compiled_pattern, text, timeout)
    except RegexTimeoutError as e:
        typer.secho(
            f"Error: {e}",
            err=True,
            fg="red",
        )
        typer.secho(
            "The input text may trigger pathological backtracking",
            err=True,
            fg="yellow",
        )
        raise typer.Exit(code=1)


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
        typer.Exit: If pattern is rejected during validation
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
        typer.Exit: If pattern is rejected during validation
    """
    if isinstance(pattern, str):
        if validate:
            validate_regex_pattern(pattern)
        pattern_text = pattern
        pattern_flags = flags
    else:
        pattern_text = pattern.pattern
        pattern_flags = pattern.flags

    try:
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
    except RegexTimeoutError as e:
        typer.secho(
            f"Error: Regex findall timed out after {timeout}s",
            err=True,
            fg="red",
        )
        typer.secho(
            "The input text may trigger pathological backtracking",
            err=True,
            fg="yellow",
        )
        raise typer.Exit(code=1) from e
