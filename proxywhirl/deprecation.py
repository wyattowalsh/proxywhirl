"""Deprecation utilities for marking and managing deprecated features."""

from __future__ import annotations

import functools
import warnings
from typing import Any, Callable, TypeVar

from loguru import logger

F = TypeVar("F", bound=Callable[..., Any])


class DeprecationInfo:
    """Information about a deprecated feature."""

    def __init__(
        self,
        name: str,
        version: str,
        removal_version: str | None = None,
        alternative: str | None = None,
        reason: str | None = None,
    ):
        """Initialize deprecation info.

        Args:
            name: Name of deprecated feature
            version: Version when deprecated
            removal_version: Version when will be removed
            alternative: Suggested replacement
            reason: Reason for deprecation
        """
        self.name = name
        self.version = version
        self.removal_version = removal_version
        self.alternative = alternative
        self.reason = reason

    def __str__(self) -> str:
        """Format as deprecation message."""
        msg = f"{self.name} is deprecated since {self.version}"

        if self.removal_version:
            msg += f" and will be removed in {self.removal_version}"

        if self.alternative:
            msg += f"; use {self.alternative} instead"

        if self.reason:
            msg += f". Reason: {self.reason}"

        return msg


def deprecated(
    version: str,
    removal_version: str | None = None,
    alternative: str | None = None,
    reason: str | None = None,
) -> Callable[[F], F]:
    """Decorator to mark functions/classes as deprecated.

    Args:
        version: Version when deprecated
        removal_version: Version when will be removed
        alternative: Suggested replacement
        reason: Reason for deprecation

    Returns:
        Decorator function
    """

    def decorator(func: F) -> F:
        func_name = func.__qualname__

        info = DeprecationInfo(
            name=func_name,
            version=version,
            removal_version=removal_version,
            alternative=alternative,
            reason=reason,
        )

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            message = str(info)
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            logger.warning(f"Deprecated function called: {message}")
            return func(*args, **kwargs)

        wrapper.__deprecated__ = info
        return wrapper

    return decorator


class DeprecationManager:
    """Manages deprecated features and their usage tracking."""

    def __init__(self):
        """Initialize deprecation manager."""
        self._deprecated_features: dict[str, DeprecationInfo] = {}
        self._usage_count: dict[str, int] = {}

    def register_deprecated(self, feature: DeprecationInfo) -> None:
        """Register a deprecated feature.

        Args:
            feature: Deprecation information
        """
        self._deprecated_features[feature.name] = feature
        self._usage_count[feature.name] = 0
        logger.info(f"Registered deprecated feature: {feature.name}")

    def mark_as_used(self, feature_name: str) -> None:
        """Record usage of deprecated feature.

        Args:
            feature_name: Name of feature
        """
        self._usage_count[feature_name] = self._usage_count.get(feature_name, 0) + 1

    def get_deprecation(self, feature_name: str) -> DeprecationInfo | None:
        """Get deprecation info.

        Args:
            feature_name: Name of feature

        Returns:
            Deprecation info or None
        """
        return self._deprecated_features.get(feature_name)

    def get_usage_report(self) -> dict[str, int]:
        """Get usage report for deprecated features.

        Returns:
            Dict of {feature_name: usage_count}
        """
        return dict(self._usage_count)

    def is_deprecated(self, feature_name: str) -> bool:
        """Check if feature is deprecated.

        Args:
            feature_name: Name of feature

        Returns:
            True if deprecated
        """
        return feature_name in self._deprecated_features

    def get_all_deprecated(self) -> dict[str, DeprecationInfo]:
        """Get all deprecated features.

        Returns:
            Dict of {name: DeprecationInfo}
        """
        return dict(self._deprecated_features)

    def get_removal_candidates(self) -> list[DeprecationInfo]:
        """Get features that should be removed soon.

        Returns:
            List of DeprecationInfo for features near removal
        """
        from packaging import version as pkg_version

        # Assuming current version in some standard location
        candidates = []

        for info in self._deprecated_features.values():
            if info.removal_version and self._usage_count.get(info.name, 0) > 0:
                try:
                    if pkg_version.parse(info.removal_version) <= pkg_version.parse(
                        "0.4.0"
                    ):
                        candidates.append(info)
                except Exception:
                    pass

        return candidates


_global_manager = DeprecationManager()


def get_deprecation_manager() -> DeprecationManager:
    """Get global deprecation manager.

    Returns:
        Global DeprecationManager instance
    """
    return _global_manager
