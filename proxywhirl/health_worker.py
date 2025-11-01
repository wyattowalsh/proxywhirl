"""
Background worker threads for health monitoring.

Manages concurrent health check execution using thread pool
and per-source worker threads.
"""

import threading
import time
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from loguru import logger

__all__ = ["HealthWorker"]


class HealthWorker:
    """
    Background thread worker for executing health checks.
    
    Runs in background per proxy source, scheduling and executing
    health checks at configured intervals.
    """
    
    def __init__(
        self,
        source: str,
        check_interval: int,
        check_func: Callable[[str], Any],
        proxies: dict[str, Any],
        lock: threading.RLock,
    ) -> None:
        """Initialize health worker.
        
        Args:
            source: Source identifier for proxies
            check_interval: Seconds between checks
            check_func: Function to call for health checks
            proxies: Shared proxy state dictionary
            lock: Thread lock for synchronized access
        """
        self.source = source
        self.check_interval = check_interval
        self.check_func = check_func
        self.proxies = proxies
        self.lock = lock
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        logger.debug(f"HealthWorker initialized for source: {source}, interval: {check_interval}s")
    
    def start(self) -> None:
        """Start the health check worker thread."""
        if self._running:
            logger.warning(f"HealthWorker already running for source: {self.source}")
            return
        
        self._running = True
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._check_loop,
            name=f"HealthWorker-{self.source}",
            daemon=True
        )
        self._thread.start()
        logger.info(f"HealthWorker started for source: {self.source}")
    
    def stop(self, timeout: float = 5.0) -> None:
        """Stop the health check worker thread.
        
        Args:
            timeout: Maximum seconds to wait for graceful shutdown
        """
        if not self._running:
            return
        
        logger.info(f"Stopping HealthWorker for source: {self.source}")
        self._running = False
        self._stop_event.set()
        
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=timeout)
            if self._thread.is_alive():
                logger.warning(f"HealthWorker thread for {self.source} did not stop gracefully")
    
    def _check_loop(self) -> None:
        """Main check loop that runs in background thread."""
        while self._running and not self._stop_event.is_set():
            try:
                # Get proxies for this source
                with self.lock:
                    source_proxies = [
                        url for url, state in self.proxies.items()
                        if state.get("source") == self.source
                    ]
                
                # Check each proxy
                for proxy_url in source_proxies:
                    if not self._running:
                        break
                    
                    try:
                        result = self.check_func(proxy_url)
                        logger.debug(f"Health check complete for {proxy_url}: {result.status}")
                    except Exception as e:
                        logger.error(f"Health check failed for {proxy_url}: {e}")
                
            except Exception as e:
                logger.error(f"Error in health check loop for {self.source}: {e}")
            
            # Wait for next check interval
            self._stop_event.wait(self.check_interval)
