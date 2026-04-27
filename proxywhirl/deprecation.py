"""
Deprecation utilities for ProxyWhirl.

Provides decorators and helpers for deprecating functions and classes.
"""

from __future__ import annotations

import functools
import warnings
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def deprecated(
    reason: str,
    version: str,
    removal_version: str | None = None,
    alternative: str | None = None,
) -> Callable[[F], F]:
    """Decorator to mark functions/methods as deprecated.

    Args:
        reason: Why the function is deprecated
        version: Version in which it was deprecated
        removal_version: Version in which it will be removed
        alternative: Suggested alternative to use

    Returns:
        Decorated function that emits deprecation warning
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            message = f"{func.__qualname__} is deprecated since v{version}. {reason}"
            if alternative:
                message += f" Use {alternative} instead."
            if removal_version:
                message += f" Will be removed in v{removal_version}."

            warnings.warn(
                message,
                category=DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


def deprecated_parameter(
    param_name: str,
    reason: str,
    version: str,
    removal_version: str | None = None,
    alternative: str | None = None,
) -> Callable[[F], F]:
    """Decorator to mark function parameters as deprecated.

    Args:
        param_name: Name of the deprecated parameter
        reason: Why the parameter is deprecated
        version: Version in which it was deprecated
        removal_version: Version in which it will be removed
        alternative: Suggested alternative parameter

    Returns:
        Decorated function that warns when parameter is used
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if param_name in kwargs:
                message = f"Parameter '{param_name}' is deprecated since v{version}. {reason}"
                if alternative:
                    message += f" Use '{alternative}' instead."
                if removal_version:
                    message += f" Will be removed in v{removal_version}."

                warnings.warn(
                    message,
                    category=DeprecationWarning,
                    stacklevel=2,
                )

            return func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


class DeprecatedPropertyDescriptor:
    """Descriptor for deprecated properties."""

    def __init__(
        self,
        fget: Callable[[Any], Any],
        reason: str,
        version: str,
        removal_version: str | None = None,
        alternative: str | None = None,
    ):
        self.fget = fget
        self.reason = reason
        self.version = version
        self.removal_version = removal_version
        self.alternative = alternative
        functools.update_wrapper(self, fget)

    def __get__(self, obj: Any, objtype: Any = None) -> Any:
        if obj is None:
            return self

        message = (
            f"Property '{self.fget.__name__}' is deprecated since v{self.version}. {self.reason}"
        )
        if self.alternative:
            message += f" Use '{self.alternative}' instead."
        if self.removal_version:
            message += f" Will be removed in v{self.removal_version}."

        warnings.warn(
            message,
            category=DeprecationWarning,
            stacklevel=2,
        )
        return self.fget(obj)


def deprecated_property(
    reason: str,
    version: str,
    removal_version: str | None = None,
    alternative: str | None = None,
) -> Callable[[Callable[[Any], Any]], DeprecatedPropertyDescriptor]:
    """Decorator for deprecated properties.

    Args:
        reason: Why the property is deprecated
        version: Version in which it was deprecated
        removal_version: Version in which it will be removed
        alternative: Suggested alternative property

    Returns:
        Decorator that creates a deprecated property descriptor
    """

    def decorator(fget: Callable[[Any], Any]) -> DeprecatedPropertyDescriptor:
        return DeprecatedPropertyDescriptor(
            fget,
            reason=reason,
            version=version,
            removal_version=removal_version,
            alternative=alternative,
        )

    return decorator
