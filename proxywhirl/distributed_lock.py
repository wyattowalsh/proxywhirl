"""Distributed locking for multi-process synchronization."""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from loguru import logger


@dataclass
class LockInfo:
    """Distributed lock information."""

    name: str
    acquired_at: datetime
    expires_at: datetime
    owner: str


class DistributedLockManager:
    """Manages distributed locks."""

    def __init__(self, default_ttl_seconds: int = 60):
        self.locks: dict = {}
        self.default_ttl = default_ttl_seconds

    async def acquire_lock(
        self, lock_name: str, owner: str, ttl_seconds: Optional[int] = None
    ) -> bool:
        """Acquire a distributed lock."""
        ttl = ttl_seconds or self.default_ttl
        now = datetime.now()

        # Check if lock exists and is expired
        if lock_name in self.locks:
            lock_info = self.locks[lock_name]
            if lock_info.expires_at > now:
                return False

        # Acquire lock
        self.locks[lock_name] = LockInfo(
            name=lock_name, acquired_at=now, expires_at=now + timedelta(seconds=ttl), owner=owner
        )
        logger.debug(f"Lock acquired: {lock_name} by {owner}")
        return True

    async def release_lock(self, lock_name: str, owner: str) -> bool:
        """Release a distributed lock."""
        if lock_name not in self.locks:
            return False

        lock_info = self.locks[lock_name]
        if lock_info.owner != owner:
            return False

        del self.locks[lock_name]
        logger.debug(f"Lock released: {lock_name}")
        return True

    async def wait_for_lock(self, lock_name: str, owner: str, timeout_seconds: int = 30) -> bool:
        """Wait for lock with timeout."""
        start = datetime.now()
        while True:
            if await self.acquire_lock(lock_name, owner):
                return True

            if (datetime.now() - start).total_seconds() > timeout_seconds:
                return False

            await asyncio.sleep(0.1)
