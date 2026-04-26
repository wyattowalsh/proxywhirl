"""Safe regex pattern matching with ReDoS protection.

This module provides utilities for safely compiling and matching user-provided
regex patterns with timeout protection to prevent Regular Expression Denial of
Service (ReDoS) attacks.
"""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError
from re import Pattern

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


def _compile_with_timeout(pattern: str, flags: int, timeout: float) -> Pattern[str]:
    """Compile regex with timeout using thread pool.

    Args:
        pattern: Regex pattern
        flags: Regex flags
        timeout: Timeout in seconds

    Returns:
        Compiled regex pattern

    Raises:
        RegexTimeoutError: If compilation exceeds timeout
    """
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(re.compile, pattern, flags)  # type: ignore[arg-type]
        try:
            return future.result(timeout=timeout)  # type: ignore[return-value]
        except FuturesTimeoutError as e:
            raise RegexTimeoutError(
                f"Regex compilation timed out after {timeout}s: {pattern[:50]}..."
            ) from e


def _match_with_timeout(pattern: Pattern[str], text: str, timeout: float) -> re.Match[str] | None:
    """Match regex with timeout using thread pool.

    Args:
        pattern: Compiled regex pattern
        text: Text to match against
        timeout: Timeout in seconds

    Returns:
        Match object or None

    Raises:
        RegexTimeoutError: If matching exceeds timeout
    """
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(pattern.search, text)  # type: ignore[arg-type]
        try:
            return future.result(timeout=timeout)  # type: ignore[return-value]
        except FuturesTimeoutError as e:
            raise RegexTimeoutError(f"Regex matching timed out after {timeout}s") from e


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
    # Compile pattern if needed
    if isinstance(pattern, str):
        compiled_pattern = safe_regex_compile(pattern, flags, timeout, validate)
    else:
        compiled_pattern = pattern

    # Find all matches with timeout
    def _findall() -> list[str]:
        matches = compiled_pattern.findall(text)
        # Limit results to prevent DoS
        return matches[:max_results]

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_findall)
        try:
            return future.result(timeout=timeout)
        except FuturesTimeoutError as e:
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
