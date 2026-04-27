"""Test isolation utilities for preventing flake in concurrent tests.

Provides mechanisms to isolate tests and prevent race conditions
in async/concurrent test scenarios.
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass
from typing import Any

from loguru import logger


@dataclass
class IsolationContext:
    """Context for isolated test execution."""

    context_id: str
    name: str
    thread_id: int | None = None
    resources: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Post-initialization setup."""
        if self.resources is None:
            self.resources = {}
        if self.thread_id is None:
            self.thread_id = threading.get_ident()


class TestFlakeIsolationManager:
    """Manages test isolation to prevent flakiness."""

    def __init__(self) -> None:
        """Initialize test flake isolation manager."""
        self._contexts: dict[str, IsolationContext] = {}
        self._lock = threading.RLock()
        logger.debug("TestFlakeIsolationManager initialized")

    def create_context(self, name: str = "") -> IsolationContext:
        """Create an isolated test context.

        Args:
            name: Context name

        Returns:
            Isolation context
        """
        context_id = str(uuid.uuid4())
        context = IsolationContext(context_id=context_id, name=name or context_id)

        with self._lock:
            self._contexts[context_id] = context
            logger.debug(f"Isolation context created: {context_id}")

        return context

    def destroy_context(self, context_id: str) -> bool:
        """Destroy an isolation context.

        Args:
            context_id: Context ID

        Returns:
            True if destroyed
        """
        with self._lock:
            if context_id in self._contexts:
                del self._contexts[context_id]
                logger.debug(f"Isolation context destroyed: {context_id}")
                return True
        return False

    def allocate_resource(self, context_id: str, resource_key: str, resource: Any) -> bool:
        """Allocate resource to context.

        Args:
            context_id: Context ID
            resource_key: Resource key
            resource: Resource object

        Returns:
            True if allocated
        """
        with self._lock:
            if context_id not in self._contexts:
                logger.error(f"Context not found: {context_id}")
                return False

            context = self._contexts[context_id]
            context.resources[resource_key] = resource
            logger.debug(f"Resource allocated: {context_id}/{resource_key}")
            return True

    def get_resource(self, context_id: str, resource_key: str) -> Any | None:
        """Get resource from context.

        Args:
            context_id: Context ID
            resource_key: Resource key

        Returns:
            Resource or None
        """
        with self._lock:
            if context_id not in self._contexts:
                return None

            context = self._contexts[context_id]
            return context.resources.get(resource_key)

    def release_resource(self, context_id: str, resource_key: str) -> bool:
        """Release resource from context.

        Args:
            context_id: Context ID
            resource_key: Resource key

        Returns:
            True if released
        """
        with self._lock:
            if context_id not in self._contexts:
                return False

            context = self._contexts[context_id]
            if resource_key in context.resources:
                del context.resources[resource_key]
                logger.debug(f"Resource released: {context_id}/{resource_key}")
                return True

        return False

    def cleanup_context(self, context_id: str) -> bool:
        """Cleanup context and release all resources.

        Args:
            context_id: Context ID

        Returns:
            True if cleaned up
        """
        with self._lock:
            if context_id not in self._contexts:
                return False

            context = self._contexts[context_id]
            context.resources.clear()
            logger.debug(f"Context cleaned up: {context_id}")
            return True

    def get_active_contexts(self) -> list[IsolationContext]:
        """Get active isolation contexts.

        Returns:
            List of active contexts
        """
        with self._lock:
            return list(self._contexts.values())

    def export_metrics(self) -> dict[str, Any]:
        """Export isolation metrics.

        Returns:
            Dictionary of metrics
        """
        with self._lock:
            return {
                "total_contexts": len(self._contexts),
                "contexts": {
                    ctx.context_id: {
                        "name": ctx.name,
                        "thread_id": ctx.thread_id,
                        "resource_count": len(ctx.resources),
                    }
                    for ctx in self._contexts.values()
                },
            }
