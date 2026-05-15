"""Response validation and parsing utilities."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from loguru import logger


class ResponseContentType(str, Enum):
    """Content type for responses."""

    JSON = "application/json"
    HTML = "text/html"
    XML = "application/xml"
    PLAIN_TEXT = "text/plain"
    BINARY = "application/octet-stream"


@dataclass
class ValidationRule:
    """Rule for validating response."""

    name: str
    check_fn: Callable[[Any], bool]
    message: str


class ResponseValidator:
    """Validates HTTP responses."""

    def __init__(self):
        """Initialize validator."""
        self._rules: list[ValidationRule] = []

    def add_rule(self, rule: ValidationRule) -> None:
        """Add a validation rule.

        Args:
            rule: Validation rule
        """
        self._rules.append(rule)

    def validate_status(self, status_code: int, expected: int | list[int]) -> bool:
        """Validate status code.

        Args:
            status_code: Response status code
            expected: Expected code(s)

        Returns:
            True if valid
        """
        if isinstance(expected, list):
            return status_code in expected
        return status_code == expected

    def validate_content_type(self, content_type: str, expected: str | list[str]) -> bool:
        """Validate content type.

        Args:
            content_type: Response content type
            expected: Expected type(s)

        Returns:
            True if valid
        """
        if isinstance(expected, list):
            return any(exp in content_type for exp in expected)
        return expected in content_type

    def validate_content_length(
        self,
        content_length: int,
        min_length: int | None = None,
        max_length: int | None = None,
    ) -> bool:
        """Validate content length.

        Args:
            content_length: Content length
            min_length: Minimum length
            max_length: Maximum length

        Returns:
            True if valid
        """
        if min_length and content_length < min_length:
            return False
        return not (max_length and content_length > max_length)

    def validate_json(self, content: str) -> bool:
        """Validate JSON content.

        Args:
            content: Response content

        Returns:
            True if valid JSON
        """
        try:
            json.loads(content)
            return True
        except (json.JSONDecodeError, TypeError):
            return False

    def validate_headers(self, headers: dict[str, str], required: list[str] | None = None) -> bool:
        """Validate response headers.

        Args:
            headers: Response headers
            required: Required header names

        Returns:
            True if valid
        """
        if required:
            return all(h.lower() in (k.lower() for k in headers) for h in required)
        return True

    def validate_all_rules(self, response: dict[str, Any]) -> bool:
        """Validate response against all rules.

        Args:
            response: Response object

        Returns:
            True if all rules pass
        """
        for rule in self._rules:
            try:
                if not rule.check_fn(response):
                    logger.warning(f"Validation failed: {rule.name}: {rule.message}")
                    return False
            except Exception as e:
                logger.error(f"Validation error: {rule.name}: {e}")
                return False

        return True


class ResponseParser:
    """Parses HTTP responses."""

    @staticmethod
    def parse_json(content: str) -> dict[str, Any] | None:
        """Parse JSON response.

        Args:
            content: Response content

        Returns:
            Parsed JSON or None
        """
        try:
            return json.loads(content)
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Failed to parse JSON: {e}")
            return None

    @staticmethod
    def parse_headers(headers: dict[str, str]) -> dict[str, str]:
        """Parse headers to lowercase keys.

        Args:
            headers: Response headers

        Returns:
            Headers with lowercase keys
        """
        return {k.lower(): v for k, v in headers.items()}

    @staticmethod
    def extract_json_field(content: str, field_path: str) -> Any | None:
        """Extract field from JSON response.

        Args:
            content: Response content
            field_path: Dot-separated path (e.g., "data.user.id")

        Returns:
            Field value or None
        """
        try:
            data = json.loads(content)
            parts = field_path.split(".")

            for part in parts:
                if isinstance(data, dict):
                    data = data.get(part)
                else:
                    return None

            return data
        except Exception as e:
            logger.debug(f"Failed to extract field: {e}")
            return None


@dataclass
class ResponseQuality:
    """Assessment of response quality."""

    is_valid: bool
    issues: list[str]
    warnings: list[str]
    score: float  # 0-1


class ResponseQualityChecker:
    """Checks quality of responses."""

    def check(
        self,
        status_code: int,
        headers: dict[str, str] | None = None,
        content: str | None = None,
    ) -> ResponseQuality:
        """Check response quality.

        Args:
            status_code: HTTP status code
            headers: Response headers
            content: Response content

        Returns:
            Quality assessment
        """
        issues = []
        warnings = []
        score = 1.0

        # Check status code
        if status_code >= 500:
            issues.append("Server error status code")
            score -= 0.5
        elif status_code >= 400:
            warnings.append("Client error status code")
            score -= 0.2

        # Check headers
        if headers:
            headers_lower = {k.lower(): v for k, v in headers.items()}

            if "content-length" not in headers_lower:
                warnings.append("Missing Content-Length header")
                score -= 0.1

            if "content-type" not in headers_lower:
                warnings.append("Missing Content-Type header")
                score -= 0.1

        # Check content
        if content and len(content) == 0:
            warnings.append("Empty response body")
            score -= 0.1

        return ResponseQuality(
            is_valid=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            score=max(0.0, score),
        )
