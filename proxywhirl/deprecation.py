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
    *args: Any,
    **kwargs: Any,
) -> Callable[[F], F]:
    """Decorator to mark functions/classes as deprecated.

    Supports all calling conventions:
        @deprecated("1.0", "2.0", alternative="new_func")
        @deprecated("Use new_func instead", "1.0", "2.0")
        @deprecated(version="1.0", removal_version="2.0", alternative="new_func")

    Returns:
        Decorator function
    """
    # Normalize args/kwargs into canonical fields
    version: str | None = None
    removal_version: str | None = None
    alternative: str | None = kwargs.get("alternative")
    reason: str | None = kwargs.get("reason")

    if kwargs and not args:
        # Pure keyword call: @deprecated(version="1.0", ...)
        version = kwargs.get("version", "0.0")
        removal_version = kwargs.get("removal_version")
    elif args:
        first = args[0]
        # Detect legacy signature where first arg is a message, not a version
        if isinstance(first, str) and (" " in first or first.lower().startswith("use ")):
            message = first
            version = args[1] if len(args) > 1 else "0.0"
            removal_version = args[2] if len(args) > 2 else kwargs.get("removal_version")
            alternative = kwargs.get("alternative")
            if alternative is None and "use " in message.lower():
                import re

                match = re.search(r"use (\w+)", message, re.IGNORECASE)
                if match:
                    alternative = match.group(1)
            reason = message
        else:
            version = first
            removal_version = args[1] if len(args) > 1 else kwargs.get("removal_version")

    if version is None:
        version = "0.0"

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


def deprecated_parameter(
    param_name: str,
    message: str,
    version: str,
    alternative: str | None = None,
) -> Callable[[F], F]:
    """Decorator to mark a function parameter as deprecated.

    Args:
        param_name: Name of deprecated parameter
        message: Deprecation message
        version: Version when deprecated
        alternative: Suggested replacement parameter

    Returns:
        Decorator function
    """

    def decorator(func: F) -> F:
        func_name = func.__qualname__
        alt_msg = f"; use {alternative} instead" if alternative else ""
        full_message = f"{func_name} parameter '{param_name}' is deprecated since {version}{alt_msg}. {message}"

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if param_name in kwargs:
                warnings.warn(full_message, DeprecationWarning, stacklevel=2)
                logger.warning(f"Deprecated parameter used: {full_message}")
            return func(*args, **kwargs)

        return wrapper

    return decorator


class deprecated_property:
    """Decorator/descriptor for deprecated properties."""

    def __init__(
        self,
        message: str,
        version: str,
        alternative: str | None = None,
    ):
        self.message = message
        self.version = version
        self.alternative = alternative
        alt_msg = f"; use {alternative} instead" if alternative else ""
        self._template = f"{{name}} is deprecated since {version}{alt_msg}. {message}"

    def __call__(self, func: Callable[..., Any]) -> "deprecated_property":
        self.func = func
        self.name = func.__name__
        self.full_message = self._template.format(name=self.name)
        return self

    def __get__(self, instance: Any, owner: type[Any] | None = None) -> Any:
        if instance is None:
            return self
        warnings.warn(self.full_message, DeprecationWarning, stacklevel=2)
        logger.warning(f"Deprecated property accessed: {self.full_message}")
        return self.func(instance)

    def __set__(self, instance: Any, value: Any) -> None:
        raise AttributeError("Can't set deprecated property")


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
                    if pkg_version.parse(info.removal_version) <= pkg_version.parse("0.4.0"):
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
