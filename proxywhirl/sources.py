"""Built-in proxy source configurations.

This module provides pre-configured ProxySourceConfig instances for popular
free proxy list APIs and websites. These can be used directly with ProxyFetcher.

Example:
    >>> from proxywhirl import ProxyFetcher
    >>> from proxywhirl.sources import PROXY_SCRAPE_HTTP, GEONODE_HTTP
    >>> fetcher = ProxyFetcher(sources=[PROXY_SCRAPE_HTTP, GEONODE_HTTP])
    >>> proxies = await fetcher.fetch_all()
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from proxywhirl.models import ProxySourceConfig

# =============================================================================
# API-Based Sources (JSON/CSV formats)
# =============================================================================


PROXY_SCRAPE_HTTP = ProxySourceConfig(
    url="https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    format="plain_text",
)

GEONODE_HTTP = ProxySourceConfig(
    url="https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=http%2Chttps",
    format="json",
    trusted=True,  # GeoNode validates and sorts by lastChecked
)

GEONODE_SOCKS4 = ProxySourceConfig(
    url="https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks4",
    format="json",
    trusted=True,
)

GEONODE_SOCKS5 = ProxySourceConfig(
    url="https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5",
    format="json",
    trusted=True,
)


# =============================================================================
# GitHub-Hosted Proxy Lists (Updated frequently)
# =============================================================================


# TheSpeedX/PROXY-List - Very large, frequently updated lists
GITHUB_THESPEEDX_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    format="plain_text",
)

GITHUB_THESPEEDX_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
    format="plain_text",
)

GITHUB_THESPEEDX_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    format="plain_text",
)

GITHUB_MONOSANS_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    format="plain_text",
    trusted=True,  # monosans validates every 5 minutes
)

GITHUB_MONOSANS_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt",
    format="plain_text",
    trusted=True,
)

GITHUB_MONOSANS_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
    format="plain_text",
    trusted=True,
)

# Additional GitHub proxy sources for maximum coverage
GITHUB_JETKAI_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
    format="plain_text",
    trusted=True,  # jetkai "online-proxies" = pre-validated
)

GITHUB_JETKAI_HTTPS = ProxySourceConfig(
    url="https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt",
    format="plain_text",
    trusted=True,
)

GITHUB_JETKAI_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt",
    format="plain_text",
    trusted=True,
)

GITHUB_JETKAI_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt",
    format="plain_text",
    trusted=True,
)

GITHUB_ROOSTERKID_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
    format="plain_text",
)

GITHUB_SUNNY9577_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
    format="plain_text",
)

GITHUB_SHIFTYTR_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    format="plain_text",
)

GITHUB_SHIFTYTR_HTTPS = ProxySourceConfig(
    url="https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt",
    format="plain_text",
)

GITHUB_SHIFTYTR_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt",
    format="plain_text",
)

GITHUB_SHIFTYTR_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
    format="plain_text",
)

GITHUB_ALMROOT_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/almroot/proxylist/master/list.txt",
    format="plain_text",
)

GITHUB_ASLISK_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/aslisk/proxyhttps/main/https.txt",
    format="plain_text",
)

GITHUB_PRXCHK_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt",
    format="plain_text",
    trusted=True,  # prxchk = regularly checked proxies
)

GITHUB_PRXCHK_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/prxchk/proxy-list/main/socks4.txt",
    format="plain_text",
    trusted=True,
)

GITHUB_PRXCHK_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt",
    format="plain_text",
    trusted=True,
)

GITHUB_RDAVYDOV_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt",
    format="plain_text",
)

GITHUB_RDAVYDOV_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks4.txt",
    format="plain_text",
)

GITHUB_RDAVYDOV_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks5.txt",
    format="plain_text",
)

GITHUB_MMPX12_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
    format="plain_text",
)

GITHUB_MMPX12_HTTPS = ProxySourceConfig(
    url="https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt",
    format="plain_text",
)

GITHUB_MMPX12_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks4.txt",
    format="plain_text",
)

GITHUB_MMPX12_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt",
    format="plain_text",
)

GITHUB_PROXIFLY_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt",
    format="plain_text",
    trusted=True,  # proxifly = verified working proxies
)

GITHUB_PROXIFLY_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks4/data.txt",
    format="plain_text",
    trusted=True,
)

GITHUB_PROXIFLY_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt",
    format="plain_text",
    trusted=True,
)

GITHUB_ELLIOTTOPHELLIA_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/elliottophellia/yakumo/master/results/http/global/http_checked.txt",
    format="plain_text",
    trusted=True,  # elliottophellia "_checked" = validated
)

GITHUB_ELLIOTTOPHELLIA_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/elliottophellia/yakumo/master/results/socks4/global/socks4_checked.txt",
    format="plain_text",
    trusted=True,
)

GITHUB_ELLIOTTOPHELLIA_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/elliottophellia/yakumo/master/results/socks5/global/socks5_checked.txt",
    format="plain_text",
    trusted=True,
)

# OpenProxy GitHub sources
GITHUB_OPENPROXY_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/http/http.txt",
    format="plain_text",
)

GITHUB_OPENPROXY_HTTPS = ProxySourceConfig(
    url="https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/https/https.txt",
    format="plain_text",
)

GITHUB_OPENPROXY_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks4/socks4.txt",
    format="plain_text",
)

GITHUB_OPENPROXY_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt",
    format="plain_text",
)

# vakhov/fresh-proxy-list - Verified working proxies
GITHUB_VAKHOV_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/http.txt",
    format="plain_text",
    trusted=True,  # vakhov "fresh" = pre-validated
)

GITHUB_VAKHOV_HTTPS = ProxySourceConfig(
    url="https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/https.txt",
    format="plain_text",
    trusted=True,
)

GITHUB_VAKHOV_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks4.txt",
    format="plain_text",
    trusted=True,
)

GITHUB_VAKHOV_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks5.txt",
    format="plain_text",
    trusted=True,
)

# Zaeem20/FREE_PROXIES_LIST - Checked proxies
GITHUB_ZAEEM_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt",
    format="plain_text",
)

GITHUB_ZAEEM_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/socks4.txt",
    format="plain_text",
)


# proxy4parsing - Regularly validated
GITHUB_PROXY4PARSING_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt",
    format="plain_text",
)

# MuRongPig/Proxy-Master - Updated frequently, very large lists
GITHUB_MURONGPIG_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/MuRongPig/Proxy-Master/main/http.txt",
    format="plain_text",
)

GITHUB_MURONGPIG_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/MuRongPig/Proxy-Master/main/socks4.txt",
    format="plain_text",
)

GITHUB_MURONGPIG_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/MuRongPig/Proxy-Master/main/socks5.txt",
    format="plain_text",
)

# =============================================================================
# NEW SOURCES - Added Dec 2025 (verified working, actively maintained)
# =============================================================================

# komutan234/Proxy-List-Free - Updated every 2 minutes via GitHub Actions
GITHUB_KOMUTAN_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/komutan234/Proxy-List-Free/main/proxies/http.txt",
    format="plain_text",
    trusted=True,  # Updated every 2 minutes
)

GITHUB_KOMUTAN_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/komutan234/Proxy-List-Free/main/proxies/socks4.txt",
    format="plain_text",
    trusted=True,
)

GITHUB_KOMUTAN_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/komutan234/Proxy-List-Free/main/proxies/socks5.txt",
    format="plain_text",
    trusted=True,
)

# Anonym0usWork1221/Free-Proxies - Updated every 2 hours
GITHUB_ANONYM0US_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/http_proxies.txt",
    format="plain_text",
)

GITHUB_ANONYM0US_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/socks4_proxies.txt",
    format="plain_text",
)

GITHUB_ANONYM0US_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/socks5_proxies.txt",
    format="plain_text",
)

# hookzof/socks5_list - Well-known SOCKS5 source
GITHUB_HOOKZOF_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    format="plain_text",
)

# im-razvan/proxy_list - HTTP and SOCKS5 proxies
GITHUB_IMRAZVAN_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/im-razvan/proxy_list/main/http.txt",
    format="plain_text",
)

GITHUB_IMRAZVAN_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/im-razvan/proxy_list/main/socks5.txt",
    format="plain_text",
)

# proxyspace.pro - Very large proxy lists (1MB+ each)
PROXYSPACE_HTTP = ProxySourceConfig(
    url="https://proxyspace.pro/http.txt",
    format="plain_text",
)

PROXYSPACE_SOCKS4 = ProxySourceConfig(
    url="https://proxyspace.pro/socks4.txt",
    format="plain_text",
)

PROXYSPACE_SOCKS5 = ProxySourceConfig(
    url="https://proxyspace.pro/socks5.txt",
    format="plain_text",
)

# openproxylist.xyz - Large HTTP proxy list
OPENPROXYLIST_HTTP = ProxySourceConfig(
    url="https://openproxylist.xyz/http.txt",
    format="plain_text",
)

# dpangestuw/Free-Proxy - Frequently updated large lists
GITHUB_DPANGESTUW_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/dpangestuw/Free-Proxy/master/http_proxies.txt",
    format="plain_text",
)

GITHUB_DPANGESTUW_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/dpangestuw/Free-Proxy/master/socks4_proxies.txt",
    format="plain_text",
)

GITHUB_DPANGESTUW_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/dpangestuw/Free-Proxy/master/socks5_proxies.txt",
    format="plain_text",
)

# clarketm/proxy-list - Classic source, daily updates
GITHUB_CLARKETM_PROXY = ProxySourceConfig(
    url="https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    format="plain_text",
)

# =============================================================================
# HIGH-YIELD SOURCES - Added Jan 2026 (very large lists, 100k+ proxies each)
# =============================================================================

# Tsprnay/Proxy-lists - Extremely large proxy lists (100k+ each)
GITHUB_TSPRNAY_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/Tsprnay/Proxy-lists/master/proxies/http.txt",
    format="plain_text",
)

GITHUB_TSPRNAY_HTTPS = ProxySourceConfig(
    url="https://raw.githubusercontent.com/Tsprnay/Proxy-lists/master/proxies/https.txt",
    format="plain_text",
)

GITHUB_TSPRNAY_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/Tsprnay/Proxy-lists/master/proxies/socks4.txt",
    format="plain_text",
)

GITHUB_TSPRNAY_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/Tsprnay/Proxy-lists/master/proxies/socks5.txt",
    format="plain_text",
)

# zevtyardt/proxy-list - Very large lists (40k+ each)
GITHUB_ZEVTYARDT_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/zevtyardt/proxy-list/main/http.txt",
    format="plain_text",
)

GITHUB_ZEVTYARDT_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks4.txt",
    format="plain_text",
)

GITHUB_ZEVTYARDT_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks5.txt",
    format="plain_text",
)

# proxifly via jsDelivr CDN - Fast, reliable, 5-min updates
JSDELIVR_PROXIFLY_ALL = ProxySourceConfig(
    url="https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/all/data.txt",
    format="plain_text",
    trusted=True,  # Updated every 5 minutes, pre-validated
)

# ProxyScrape SOCKS4 - Additional protocol support
PROXY_SCRAPE_SOCKS4 = ProxySourceConfig(
    url="https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4&timeout=10000&country=all",
    format="plain_text",
)

# ProxyScrape SOCKS5 - Additional protocol support
PROXY_SCRAPE_SOCKS5 = ProxySourceConfig(
    url="https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=10000&country=all",
    format="plain_text",
)

# ErcinDedeoglu/proxies - Very large lists (50k+ each), frequently updated
GITHUB_ERCINDEDEOGLU_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt",
    format="plain_text",
)

GITHUB_ERCINDEDEOGLU_HTTPS = ProxySourceConfig(
    url="https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/https.txt",
    format="plain_text",
)

GITHUB_ERCINDEDEOGLU_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks4.txt",
    format="plain_text",
)

GITHUB_ERCINDEDEOGLU_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks5.txt",
    format="plain_text",
)

# =============================================================================
# Predefined Source Collections
# =============================================================================

# All HTTP/HTTPS sources
ALL_HTTP_SOURCES = [
    # API sources
    GEONODE_HTTP,
    # GitHub sources
    GITHUB_THESPEEDX_HTTP,
    GITHUB_MONOSANS_HTTP,
    # GitHub sources
    GITHUB_JETKAI_HTTP,
    GITHUB_JETKAI_HTTPS,
    GITHUB_ROOSTERKID_HTTP,
    GITHUB_SUNNY9577_HTTP,
    GITHUB_SHIFTYTR_HTTP,
    GITHUB_SHIFTYTR_HTTPS,
    GITHUB_ALMROOT_HTTP,
    GITHUB_ASLISK_HTTP,
    GITHUB_PRXCHK_HTTP,
    GITHUB_RDAVYDOV_HTTP,
    GITHUB_MMPX12_HTTP,
    GITHUB_MMPX12_HTTPS,
    GITHUB_PROXIFLY_HTTP,
    GITHUB_ELLIOTTOPHELLIA_HTTP,
    GITHUB_OPENPROXY_HTTP,
    GITHUB_OPENPROXY_HTTPS,
    # High-quality verified sources
    GITHUB_VAKHOV_HTTP,
    GITHUB_VAKHOV_HTTPS,
    GITHUB_ZAEEM_HTTP,
    GITHUB_PROXY4PARSING_HTTP,
    GITHUB_MURONGPIG_HTTP,
    # New sources (Dec 2025)
    GITHUB_KOMUTAN_HTTP,
    GITHUB_ANONYM0US_HTTP,
    GITHUB_IMRAZVAN_HTTP,
    PROXYSPACE_HTTP,
    OPENPROXYLIST_HTTP,
    # Newest sources
    GITHUB_DPANGESTUW_HTTP,
    GITHUB_CLARKETM_PROXY,
    # HIGH-YIELD sources (Jan 2026) - 100k+ proxies each
    GITHUB_TSPRNAY_HTTP,
    GITHUB_TSPRNAY_HTTPS,
    GITHUB_ZEVTYARDT_HTTP,
    JSDELIVR_PROXIFLY_ALL,
    GITHUB_ERCINDEDEOGLU_HTTP,
    GITHUB_ERCINDEDEOGLU_HTTPS,
]

# All SOCKS4 sources
ALL_SOCKS4_SOURCES = [
    # API sources
    GEONODE_SOCKS4,
    PROXY_SCRAPE_SOCKS4,
    # GitHub sources
    GITHUB_THESPEEDX_SOCKS4,
    GITHUB_MONOSANS_SOCKS4,
    # GitHub sources
    GITHUB_JETKAI_SOCKS4,
    GITHUB_SHIFTYTR_SOCKS4,
    GITHUB_PRXCHK_SOCKS4,
    GITHUB_RDAVYDOV_SOCKS4,
    GITHUB_MMPX12_SOCKS4,
    GITHUB_PROXIFLY_SOCKS4,
    GITHUB_ELLIOTTOPHELLIA_SOCKS4,
    GITHUB_OPENPROXY_SOCKS4,
    # High-quality verified sources
    GITHUB_VAKHOV_SOCKS4,
    GITHUB_ZAEEM_SOCKS4,
    GITHUB_MURONGPIG_SOCKS4,
    # New sources (Dec 2025)
    GITHUB_KOMUTAN_SOCKS4,
    GITHUB_ANONYM0US_SOCKS4,
    PROXYSPACE_SOCKS4,
    GITHUB_DPANGESTUW_SOCKS4,
    # HIGH-YIELD sources (Jan 2026) - 100k+ proxies each
    GITHUB_TSPRNAY_SOCKS4,
    GITHUB_ZEVTYARDT_SOCKS4,
    GITHUB_ERCINDEDEOGLU_SOCKS4,
]

# All SOCKS5 sources
ALL_SOCKS5_SOURCES = [
    # API sources
    GEONODE_SOCKS5,
    # GitHub sources
    GITHUB_THESPEEDX_SOCKS5,
    GITHUB_MONOSANS_SOCKS5,
    # GitHub sources
    GITHUB_JETKAI_SOCKS5,
    GITHUB_SHIFTYTR_SOCKS5,
    GITHUB_PRXCHK_SOCKS5,
    GITHUB_RDAVYDOV_SOCKS5,
    GITHUB_MMPX12_SOCKS5,
    GITHUB_PROXIFLY_SOCKS5,
    GITHUB_ELLIOTTOPHELLIA_SOCKS5,
    GITHUB_OPENPROXY_SOCKS5,
    # High-quality verified sources
    GITHUB_VAKHOV_SOCKS5,
    GITHUB_MURONGPIG_SOCKS5,
    # New sources (Dec 2025)
    GITHUB_KOMUTAN_SOCKS5,
    GITHUB_ANONYM0US_SOCKS5,
    GITHUB_HOOKZOF_SOCKS5,
    GITHUB_IMRAZVAN_SOCKS5,
    PROXYSPACE_SOCKS5,
    GITHUB_DPANGESTUW_SOCKS5,
    # HIGH-YIELD sources (Jan 2026) - 100k+ proxies each
    GITHUB_TSPRNAY_SOCKS5,
    GITHUB_ZEVTYARDT_SOCKS5,
    GITHUB_ERCINDEDEOGLU_SOCKS5,
    PROXY_SCRAPE_SOCKS5,
]

# All sources combined
ALL_SOURCES = ALL_HTTP_SOURCES + ALL_SOCKS4_SOURCES + ALL_SOCKS5_SOURCES

# Recommended fast/reliable sources for quick start
RECOMMENDED_SOURCES = [
    GEONODE_HTTP,
    GITHUB_MONOSANS_HTTP,
    GITHUB_MONOSANS_SOCKS5,
    GITHUB_PROXIFLY_HTTP,
    GITHUB_KOMUTAN_HTTP,  # Updated every 2 minutes
]

# API-based sources only (typically faster/more reliable)
API_SOURCES = [
    GEONODE_HTTP,
    GEONODE_SOCKS4,
    GEONODE_SOCKS5,
]


# =============================================================================
# Source Validation
# =============================================================================


@dataclass
class SourceValidationResult:
    """Result of validating a single proxy source."""

    source: ProxySourceConfig
    name: str
    status_code: int | None
    content_length: int
    has_proxies: bool
    error: str | None
    response_time_ms: float

    @property
    def is_healthy(self) -> bool:
        """Check if source is healthy (returns valid proxy data)."""
        return self.status_code == 200 and self.has_proxies and self.error is None


@dataclass
class SourceValidationReport:
    """Aggregate report of source validation."""

    results: list[SourceValidationResult]
    total_sources: int
    healthy_sources: int
    unhealthy_sources: int
    total_time_ms: float

    @property
    def healthy(self) -> list[SourceValidationResult]:
        """Get all healthy sources."""
        return [r for r in self.results if r.is_healthy]

    @property
    def unhealthy(self) -> list[SourceValidationResult]:
        """Get all unhealthy sources."""
        return [r for r in self.results if not r.is_healthy]

    @property
    def all_healthy(self) -> bool:
        """Check if all sources are healthy."""
        return self.unhealthy_sources == 0


def _get_source_name(source: ProxySourceConfig) -> str:
    """Extract a readable name from a source URL."""
    url = str(source.url)
    if "github" in url.lower():
        # Extract repo name from GitHub raw URL
        parts = url.split("/")
        if len(parts) >= 5:
            owner = parts[3]
            repo = parts[4]
            filename = parts[-1].replace(".txt", "").upper()
            return f"{owner}/{repo} ({filename})"
    elif "proxylist.geonode.com" in url:
        if "socks4" in url:
            return "GeoNode (SOCKS4)"
        elif "socks5" in url:
            return "GeoNode (SOCKS5)"
        return "GeoNode (HTTP)"
    elif "proxyscrape.com" in url:
        if "socks4" in url:
            return "ProxyScrape (SOCKS4)"
        elif "socks5" in url:
            return "ProxyScrape (SOCKS5)"
        if "country=US" in url:
            return "ProxyScrape US (HTTP)"
        if "country=DE" in url:
            return "ProxyScrape DE (HTTP)"
        if "country=FR" in url:
            return "ProxyScrape FR (HTTP)"
        if "country=GB" in url:
            return "ProxyScrape GB (HTTP)"
        return "ProxyScrape (HTTP)"
    elif "proxyspace.pro" in url:
        filename = url.split("/")[-1].replace(".txt", "").upper()
        return f"ProxySpace ({filename})"
    elif "openproxylist.xyz" in url:
        return "OpenProxyList (HTTP)"
    return url[:50] + "..." if len(url) > 50 else url


async def validate_source(
    source: ProxySourceConfig,
    timeout: float = 15.0,
    client: httpx.AsyncClient | None = None,
) -> SourceValidationResult:
    """Validate a single proxy source.

    Args:
        source: The proxy source configuration to validate
        timeout: Request timeout in seconds
        client: Optional shared HTTP client

    Returns:
        SourceValidationResult with validation details
    """
    import time

    name = _get_source_name(source)
    start = time.perf_counter()

    try:
        if client is None:
            async with httpx.AsyncClient(follow_redirects=True) as c:
                resp = await c.get(str(source.url), timeout=timeout)
        else:
            resp = await client.get(str(source.url), timeout=timeout)

        elapsed_ms = (time.perf_counter() - start) * 1000
        content = resp.text.strip() if resp.status_code == 200 else ""
        content_length = len(content)

        # Check if content looks like proxy data (contains IP:port patterns)
        has_proxies = (
            content_length > 50
            and (":" in content[:500] or "." in content[:500])
            and any(c.isdigit() for c in content[:100])
        )

        return SourceValidationResult(
            source=source,
            name=name,
            status_code=resp.status_code,
            content_length=content_length,
            has_proxies=has_proxies,
            error=None,
            response_time_ms=elapsed_ms,
        )
    except Exception as e:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return SourceValidationResult(
            source=source,
            name=name,
            status_code=None,
            content_length=0,
            has_proxies=False,
            error=str(e)[:100],
            response_time_ms=elapsed_ms,
        )


async def validate_sources(
    sources: list[ProxySourceConfig] | None = None,
    timeout: float = 15.0,
    concurrency: int = 20,
) -> SourceValidationReport:
    """Validate multiple proxy sources concurrently.

    Args:
        sources: List of sources to validate (defaults to ALL_SOURCES)
        timeout: Request timeout per source in seconds
        concurrency: Maximum concurrent requests

    Returns:
        SourceValidationReport with all validation results
    """
    import asyncio
    import time

    if sources is None:
        sources = ALL_SOURCES

    start = time.perf_counter()
    semaphore = asyncio.Semaphore(concurrency)

    async def validate_with_semaphore(
        source: ProxySourceConfig, client: httpx.AsyncClient
    ) -> SourceValidationResult:
        async with semaphore:
            return await validate_source(source, timeout=timeout, client=client)

    async with httpx.AsyncClient(follow_redirects=True) as client:
        tasks = [validate_with_semaphore(src, client) for src in sources]
        results = await asyncio.gather(*tasks)

    elapsed_ms = (time.perf_counter() - start) * 1000
    healthy_count = sum(1 for r in results if r.is_healthy)

    return SourceValidationReport(
        results=list(results),
        total_sources=len(sources),
        healthy_sources=healthy_count,
        unhealthy_sources=len(sources) - healthy_count,
        total_time_ms=elapsed_ms,
    )


def validate_sources_sync(
    sources: list[ProxySourceConfig] | None = None,
    timeout: float = 15.0,
    concurrency: int = 20,
) -> SourceValidationReport:
    """Synchronous wrapper for validate_sources.

    Args:
        sources: List of sources to validate (defaults to ALL_SOURCES)
        timeout: Request timeout per source in seconds
        concurrency: Maximum concurrent requests

    Returns:
        SourceValidationReport with all validation results
    """
    import asyncio

    return asyncio.run(validate_sources(sources=sources, timeout=timeout, concurrency=concurrency))


async def fetch_all_sources(
    validate: bool = True,
    timeout: int = 10,
    max_concurrent: int = 100,
    sources: list[ProxySourceConfig] | None = None,
    fetch_progress_callback: Any | None = None,
    validate_progress_callback: Any | None = None,
    test_url: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch proxies from all built-in sources.

    Args:
        validate: Whether to validate proxies
        timeout: Validation timeout in seconds
        max_concurrent: Maximum concurrent validation requests
        sources: List of sources to fetch from (defaults to ALL_SOURCES)
        fetch_progress_callback: Optional callback(completed, total, proxies_found) for fetch progress
        validate_progress_callback: Optional callback(completed, total, valid_count) for validation progress
        test_url: Optional URL to validate against (defaults to http://www.gstatic.com/generate_204)

    Returns:
        List of proxy dictionaries
    """
    from proxywhirl.fetchers import ProxyFetcher, ProxyValidator

    validator_kwargs = {"timeout": timeout, "concurrency": max_concurrent}
    if test_url:
        validator_kwargs["test_url"] = test_url

    validator = ProxyValidator(**validator_kwargs)
    fetcher = ProxyFetcher(sources=sources or ALL_SOURCES, validator=validator)
    try:
        return await fetcher.fetch_all(
            validate=validate,
            fetch_progress_callback=fetch_progress_callback,
            validate_progress_callback=validate_progress_callback,
        )
    finally:
        await fetcher.close()
