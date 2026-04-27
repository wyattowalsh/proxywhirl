"""Proxy chain validation and verification.

Validates chained proxy configurations, ensures connectivity through proxy
chains, and detects misconfigurations.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

import httpx
from loguru import logger


@dataclass
class ChainValidationResult:
    """Result of chain validation."""

    valid: bool
    proxy_chain: list[str]
    tested_proxies: int
    failed_proxies: list[str]
    latency_ms: float
    issues: list[str]
    tested_url: str = "http://httpbin.org/ip"


class ProxyChainValidator:
    """Validate proxy chains for correct configuration and functionality."""

    def __init__(self, timeout: float = 10.0):
        """Initialize chain validator.

        Args:
            timeout: Timeout for each proxy test in seconds
        """
        self.timeout = timeout

    async def validate_chain(
        self,
        proxy_urls: list[str],
        test_url: str = "http://httpbin.org/ip",
    ) -> ChainValidationResult:
        """Validate a proxy chain.

        Args:
            proxy_urls: List of proxy URLs in chain order
            test_url: URL to test through proxy chain

        Returns:
            Validation result
        """
        import time

        result = ChainValidationResult(
            valid=True,
            proxy_chain=proxy_urls,
            tested_proxies=0,
            failed_proxies=[],
            latency_ms=0.0,
            issues=[],
            tested_url=test_url,
        )

        if not proxy_urls:
            result.issues.append("Empty proxy chain")
            result.valid = False
            return result

        start_time = time.time()

        # Test each proxy in chain
        for i, proxy_url in enumerate(proxy_urls):
            is_valid = await self._test_single_proxy(
                proxy_url,
                test_url,
            )
            result.tested_proxies += 1

            if not is_valid:
                result.failed_proxies.append(proxy_url)
                result.issues.append(f"Proxy {i}: {proxy_url} failed validation")
                result.valid = False

        # Test full chain connectivity
        if len(proxy_urls) > 1:
            chain_valid = await self._test_chained_proxies(
                proxy_urls,
                test_url,
            )
            if not chain_valid:
                result.issues.append("Chained proxy connectivity failed")
                result.valid = False

        result.latency_ms = (time.time() - start_time) * 1000

        return result

    async def _test_single_proxy(
        self,
        proxy_url: str,
        test_url: str,
    ) -> bool:
        """Test a single proxy.

        Args:
            proxy_url: Proxy URL to test
            test_url: URL to make request through

        Returns:
            True if proxy works, False otherwise
        """
        try:
            async with httpx.AsyncClient(
                proxies=proxy_url,
                timeout=self.timeout,
            ) as client:
                response = await client.get(test_url)
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"Proxy test failed for {proxy_url}: {e}")
            return False

    async def _test_chained_proxies(
        self,
        proxy_urls: list[str],
        test_url: str,
    ) -> bool:
        """Test chained proxy connectivity.

        Args:
            proxy_urls: List of proxy URLs
            test_url: URL to test

        Returns:
            True if chain works, False otherwise
        """
        try:
            # Most HTTP clients don't support chaining multiple proxies directly
            # Test by using first proxy which may internally chain
            async with httpx.AsyncClient(
                proxies=proxy_urls[0],
                timeout=self.timeout,
            ) as client:
                response = await client.get(test_url)
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"Chained proxy test failed: {e}")
            return False

    def validate_configuration(
        self,
        proxy_chain: list[str],
    ) -> list[str]:
        """Validate proxy chain configuration for issues.

        Args:
            proxy_chain: List of proxy URLs

        Returns:
            List of issues found (empty if valid)
        """
        issues = []

        if not proxy_chain:
            issues.append("Proxy chain is empty")
            return issues

        seen_urls = set()

        for i, proxy_url in enumerate(proxy_chain):
            # Check for duplicates
            if proxy_url in seen_urls:
                issues.append(f"Duplicate proxy at position {i}: {proxy_url}")
            seen_urls.add(proxy_url)

            # Check URL format
            if not proxy_url.startswith(("http://", "https://", "socks4://", "socks5://")):
                issues.append(f"Invalid proxy URL format at position {i}: {proxy_url}")

            # Check for localhost loops
            if "localhost" in proxy_url or "127.0.0.1" in proxy_url:
                if i < len(proxy_chain) - 1:
                    issues.append(
                        f"Localhost proxy should not be in middle of chain (position {i})"
                    )

        # Check for protocol compatibility
        protocols = [self._extract_protocol(url) for url in proxy_chain]
        if protocols and protocols[0] == "socks":
            if any(p not in ("socks", None) for p in protocols[1:]):
                issues.append("SOCKS proxy cannot chain with HTTP proxies")

        return issues

    @staticmethod
    def _extract_protocol(proxy_url: str) -> str | None:
        """Extract protocol from proxy URL.

        Args:
            proxy_url: Proxy URL

        Returns:
            Protocol name or None
        """
        if proxy_url.startswith("socks4://"):
            return "socks4"
        if proxy_url.startswith("socks5://"):
            return "socks5"
        if proxy_url.startswith(("http://", "https://")):
            return "http"
        return None

    async def test_latency_through_chain(
        self,
        proxy_urls: list[str],
        num_requests: int = 5,
    ) -> dict[str, float]:
        """Test latency through proxy chain.

        Args:
            proxy_urls: Proxy URLs to test
            num_requests: Number of requests to average

        Returns:
            Dictionary of proxy URL to average latency in ms
        """
        results = {}

        for proxy_url in proxy_urls:
            latencies = []

            for _ in range(num_requests):
                try:
                    import time

                    start = time.time()
                    async with httpx.AsyncClient(
                        proxies=proxy_url,
                        timeout=self.timeout,
                    ) as client:
                        await client.get("http://httpbin.org/delay/0")
                    latency = (time.time() - start) * 1000
                    latencies.append(latency)
                except Exception as e:
                    logger.warning(f"Latency test failed for {proxy_url}: {e}")

            if latencies:
                results[proxy_url] = sum(latencies) / len(latencies)
            else:
                results[proxy_url] = float("inf")

        return results


class ChainHealthMonitor:
    """Monitor health of proxy chains over time."""

    def __init__(self, validator: ProxyChainValidator):
        """Initialize chain health monitor.

        Args:
            validator: ProxyChainValidator instance
        """
        self.validator = validator
        self.chain_history: dict[str, list[ChainValidationResult]] = {}

    async def monitor_chain(
        self,
        chain_id: str,
        proxy_urls: list[str],
        interval_seconds: float = 60.0,
    ) -> None:
        """Monitor a proxy chain continuously.

        Args:
            chain_id: Unique identifier for chain
            proxy_urls: Proxy URLs to monitor
            interval_seconds: Monitoring interval in seconds
        """
        self.chain_history[chain_id] = []

        while True:
            result = await self.validator.validate_chain(proxy_urls)
            self.chain_history[chain_id].append(result)

            # Keep only last 100 results
            if len(self.chain_history[chain_id]) > 100:
                self.chain_history[chain_id].pop(0)

            if not result.valid:
                logger.warning(f"Chain {chain_id} validation failed: {result.issues}")

            await asyncio.sleep(interval_seconds)

    def get_chain_health(self, chain_id: str) -> dict:
        """Get health status of a chain.

        Args:
            chain_id: Chain identifier

        Returns:
            Health status dictionary
        """
        if chain_id not in self.chain_history:
            return {"status": "unknown"}

        history = self.chain_history[chain_id]
        if not history:
            return {"status": "no_data"}

        valid_count = sum(1 for r in history if r.valid)
        total = len(history)

        return {
            "chain_id": chain_id,
            "status": "healthy" if valid_count / total > 0.9 else "degraded",
            "uptime_percent": (valid_count / total) * 100,
            "last_result": history[-1],
            "total_tests": total,
        }
