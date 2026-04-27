"""Proxy fingerprinting and blocking detection."""

from dataclasses import dataclass
from typing import Optional

import httpx
from loguru import logger


@dataclass
class FingerprintingIndicators:
    """Indicators of proxy fingerprinting."""

    headers_detected: bool = False
    tls_fingerprint_mismatch: bool = False
    geolocation_mismatch: bool = False
    dns_leak: bool = False
    webrtc_leak: bool = False
    risk_score: float = 0.0


class ProxyFingerprintingDetector:
    """Detects proxy fingerprinting and blocking."""

    def __init__(self):
        self.test_endpoints = [
            "https://api.ipify.org?format=json",
            "https://api.my-ip.io/ip",
            "https://httpbin.org/headers",
        ]

    async def detect_blocking(self, proxy_url: str) -> Optional[FingerprintingIndicators]:
        """Detect if proxy is being fingerprinted/blocked."""
        indicators = FingerprintingIndicators()

        try:
            async with httpx.AsyncClient(proxies=proxy_url) as client:
                # Check for detection headers
                for endpoint in self.test_endpoints:
                    response = await client.get(endpoint, timeout=10)
                    if response.status_code != 200:
                        indicators.headers_detected = True
                        break

                # Check TLS fingerprint consistency
                resp1 = await client.get("https://httpbin.org/tls", timeout=10)
                resp2 = await client.get("https://httpbin.org/tls", timeout=10)
                if resp1.text != resp2.text:
                    indicators.tls_fingerprint_mismatch = True
        except Exception as e:
            logger.error(f"Fingerprinting detection error: {e}")
            indicators.risk_score = 1.0
            return indicators

        # Calculate risk score
        indicators.risk_score = sum(
            [
                indicators.headers_detected * 0.4,
                indicators.tls_fingerprint_mismatch * 0.3,
                indicators.geolocation_mismatch * 0.2,
                indicators.dns_leak * 0.1,
            ]
        )

        return indicators
