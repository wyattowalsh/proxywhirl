"""proxywhirl/utils.py -- utility functions for proxywhirl"""

import asyncio

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=15),
    retry=retry_if_exception_type((httpx.HTTPError, asyncio.TimeoutError)),
)
async def fetch(url: str, timeout: float = 30.0) -> httpx.Response:
    """Fetch data from a URL with retry logic."""
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=15),
    retry=retry_if_exception_type((httpx.HTTPError, asyncio.TimeoutError)),
)
async def fetch_text(url: str, timeout: float = 30.0) -> str:
    """Fetch text content with retries."""
    resp = await fetch(url, timeout=timeout)
    return resp.text


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=15),
    retry=retry_if_exception_type((httpx.HTTPError, asyncio.TimeoutError, ValueError)),
)
async def fetch_json(url: str, timeout: float = 30.0):
    """Fetch JSON content with retries, returning parsed JSON."""
    resp = await fetch(url, timeout=timeout)
    return resp.json()
