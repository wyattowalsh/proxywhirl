"""Graceful shutdown handling."""

import asyncio
import signal
from typing import Callable, List
from loguru import logger


class GracefulShutdownManager:
    """Manages graceful shutdown."""

    def __init__(self):
        self.callbacks: List[Callable] = []
        self.is_shutting_down = False

    def register_shutdown_handler(self, callback: Callable) -> None:
        """Register a shutdown callback."""
        self.callbacks.append(callback)

    async def shutdown(self) -> None:
        """Execute graceful shutdown."""
        if self.is_shutting_down:
            return

        self.is_shutting_down = True
        logger.info("Starting graceful shutdown")

        for callback in self.callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()
                logger.debug(f"Shutdown callback completed: {callback.__name__}")
            except Exception as e:
                logger.error(f"Shutdown callback error: {e}")

        logger.info("Graceful shutdown complete")

    def setup_signal_handlers(self, loop: asyncio.AbstractEventLoop) -> None:
        """Setup signal handlers for graceful shutdown."""
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.shutdown()))
