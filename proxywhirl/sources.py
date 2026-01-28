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

from proxywhirl.fetchers import GeonodeParser
from proxywhirl.models import ProxySourceConfig

# =============================================================================
# API-Based Sources (JSON/CSV formats)
# =============================================================================


PROXY_SCRAPE_HTTP = ProxySourceConfig(
    url="https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    format="plain_text",
)

# ProxyScrape with additional filters for more coverage
PROXY_SCRAPE_HTTP_ANONYMOUS = ProxySourceConfig(
    url="https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=elite,anonymous",
    format="plain_text",
)

PROXY_SCRAPE_HTTPS = ProxySourceConfig(
    url="https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=yes&anonymity=all",
    format="plain_text",
)

GEONODE_HTTP = ProxySourceConfig(
    url="https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=http%2Chttps",
    format="json",
    custom_parser=GeonodeParser(),  # GeoNode uses {"data": [...]} wrapper
    trusted=True,  # GeoNode validates and sorts by lastChecked
)

GEONODE_SOCKS4 = ProxySourceConfig(
    url="https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks4",
    format="json",
    custom_parser=GeonodeParser(),
    trusted=True,
)

GEONODE_SOCKS5 = ProxySourceConfig(
    url="https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5",
    format="json",
    custom_parser=GeonodeParser(),
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
    protocol="socks4",
)

GITHUB_THESPEEDX_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    format="plain_text",
    protocol="socks5",
)

GITHUB_MONOSANS_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    format="plain_text",
    trusted=True,  # monosans validates every 5 minutes
)

GITHUB_MONOSANS_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt",
    format="plain_text",
    protocol="socks4",
    trusted=True,
)

GITHUB_MONOSANS_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
    format="plain_text",
    protocol="socks5",
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
    protocol="socks4",
    trusted=True,
)

GITHUB_JETKAI_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt",
    format="plain_text",
    protocol="socks5",
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
    protocol="socks4",
)

GITHUB_SHIFTYTR_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
    format="plain_text",
    protocol="socks5",
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
    protocol="socks4",
    trusted=True,
)

GITHUB_PRXCHK_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt",
    format="plain_text",
    protocol="socks5",
    trusted=True,
)

GITHUB_RDAVYDOV_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt",
    format="plain_text",
)

GITHUB_RDAVYDOV_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks4.txt",
    format="plain_text",
    protocol="socks4",
)

GITHUB_RDAVYDOV_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks5.txt",
    format="plain_text",
    protocol="socks5",
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
    protocol="socks4",
)

GITHUB_MMPX12_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt",
    format="plain_text",
    protocol="socks5",
)

GITHUB_PROXIFLY_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt",
    format="plain_text",
    trusted=True,  # proxifly = verified working proxies
)

GITHUB_PROXIFLY_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks4/data.txt",
    format="plain_text",
    protocol="socks4",
    trusted=True,
)

GITHUB_PROXIFLY_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt",
    format="plain_text",
    protocol="socks5",
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
    protocol="socks4",
    trusted=True,
)

GITHUB_ELLIOTTOPHELLIA_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/elliottophellia/yakumo/master/results/socks5/global/socks5_checked.txt",
    format="plain_text",
    protocol="socks5",
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
    protocol="socks4",
)

GITHUB_OPENPROXY_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt",
    format="plain_text",
    protocol="socks5",
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
    protocol="socks4",
    trusted=True,
)

GITHUB_VAKHOV_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks5.txt",
    format="plain_text",
    protocol="socks5",
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
    protocol="socks4",
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
    protocol="socks4",
)

GITHUB_MURONGPIG_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/MuRongPig/Proxy-Master/main/socks5.txt",
    format="plain_text",
    protocol="socks5",
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
    protocol="socks4",
    trusted=True,
)

GITHUB_KOMUTAN_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/komutan234/Proxy-List-Free/main/proxies/socks5.txt",
    format="plain_text",
    protocol="socks5",
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
    protocol="socks4",
)

GITHUB_ANONYM0US_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/socks5_proxies.txt",
    format="plain_text",
    protocol="socks5",
)

# hookzof/socks5_list - Well-known SOCKS5 source
GITHUB_HOOKZOF_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    format="plain_text",
    protocol="socks5",
)

# im-razvan/proxy_list - HTTP and SOCKS5 proxies
GITHUB_IMRAZVAN_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/im-razvan/proxy_list/main/http.txt",
    format="plain_text",
)

GITHUB_IMRAZVAN_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/im-razvan/proxy_list/main/socks5.txt",
    format="plain_text",
    protocol="socks5",
)

# proxyspace.pro - Very large proxy lists (1MB+ each)
PROXYSPACE_HTTP = ProxySourceConfig(
    url="https://proxyspace.pro/http.txt",
    format="plain_text",
)

PROXYSPACE_SOCKS4 = ProxySourceConfig(
    url="https://proxyspace.pro/socks4.txt",
    format="plain_text",
    protocol="socks4",
)

PROXYSPACE_SOCKS5 = ProxySourceConfig(
    url="https://proxyspace.pro/socks5.txt",
    format="plain_text",
    protocol="socks5",
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
    protocol="socks4",
)

GITHUB_DPANGESTUW_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/dpangestuw/Free-Proxy/master/socks5_proxies.txt",
    format="plain_text",
    protocol="socks5",
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
    protocol="socks4",
)

GITHUB_TSPRNAY_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/Tsprnay/Proxy-lists/master/proxies/socks5.txt",
    format="plain_text",
    protocol="socks5",
)

# zevtyardt/proxy-list - Very large lists (40k+ each)
GITHUB_ZEVTYARDT_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/zevtyardt/proxy-list/main/http.txt",
    format="plain_text",
)

GITHUB_ZEVTYARDT_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks4.txt",
    format="plain_text",
    protocol="socks4",
)

GITHUB_ZEVTYARDT_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks5.txt",
    format="plain_text",
    protocol="socks5",
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
    protocol="socks4",
)

# ProxyScrape SOCKS5 - Additional protocol support
PROXY_SCRAPE_SOCKS5 = ProxySourceConfig(
    url="https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=10000&country=all",
    format="plain_text",
    protocol="socks5",
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
    protocol="socks4",
)

GITHUB_ERCINDEDEOGLU_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks5.txt",
    format="plain_text",
    protocol="socks5",
)

# =============================================================================
# NEW HIGH-YIELD SOURCES - Added Jan 2026 (targeting 25k+ proxies)
# =============================================================================

# iplocate/free-proxy-list - Updated every 30 minutes, validated proxies
GITHUB_IPLOCATE_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/iplocate/free-proxy-list/main/protocols/http.txt",
    format="plain_text",
    trusted=True,  # Validated proxies
)

GITHUB_IPLOCATE_HTTPS = ProxySourceConfig(
    url="https://raw.githubusercontent.com/iplocate/free-proxy-list/main/protocols/https.txt",
    format="plain_text",
    trusted=True,
)

GITHUB_IPLOCATE_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/iplocate/free-proxy-list/main/protocols/socks4.txt",
    format="plain_text",
    protocol="socks4",
    trusted=True,
)

GITHUB_IPLOCATE_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/iplocate/free-proxy-list/main/protocols/socks5.txt",
    format="plain_text",
    protocol="socks5",
    trusted=True,
)

GITHUB_IPLOCATE_ALL = ProxySourceConfig(
    url="https://raw.githubusercontent.com/iplocate/free-proxy-list/main/all-proxies.txt",
    format="plain_text",
    trusted=True,
)

# a2u/free-proxy-list - Updated hourly
GITHUB_A2U_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/a2u/free-proxy-list/master/free-proxy-list.txt",
    format="plain_text",
)

# ProxyScraper/ProxyScraper - Updated every 30 minutes
GITHUB_PROXYSCRAPER_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/ProxyScraper/ProxyScraper/main/http.txt",
    format="plain_text",
)

GITHUB_PROXYSCRAPER_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/ProxyScraper/ProxyScraper/main/sock4.txt",
    format="plain_text",
    protocol="socks4",
)

GITHUB_PROXYSCRAPER_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/ProxyScraper/ProxyScraper/main/sock5.txt",
    format="plain_text",
    protocol="socks5",
)

# zebbern/Proxy-Scraper - Updated hourly
GITHUB_ZEBBERN_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/zebbern/Proxy-Scraper/main/http.txt",
    format="plain_text",
)

GITHUB_ZEBBERN_HTTPS = ProxySourceConfig(
    url="https://raw.githubusercontent.com/zebbern/Proxy-Scraper/main/https.txt",
    format="plain_text",
)

GITHUB_ZEBBERN_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/zebbern/Proxy-Scraper/main/socks4.txt",
    format="plain_text",
    protocol="socks4",
)

GITHUB_ZEBBERN_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/zebbern/Proxy-Scraper/main/socks5.txt",
    format="plain_text",
    protocol="socks5",
)

# UptimerBot/proxy-list - Frequently updated
GITHUB_UPTIMERBOT_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/UptimerBot/proxy-list/main/proxies/http.txt",
    format="plain_text",
)

GITHUB_UPTIMERBOT_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/UptimerBot/proxy-list/main/proxies/socks4.txt",
    format="plain_text",
    protocol="socks4",
)

GITHUB_UPTIMERBOT_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/UptimerBot/proxy-list/main/proxies/socks5.txt",
    format="plain_text",
    protocol="socks5",
)

# MuRongPIG/Proxy-Master - Large aggregated lists
GITHUB_MURONGPIG_HTTP_ALL = ProxySourceConfig(
    url="https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt",
    format="plain_text",
)

# sunny9577/proxy-scraper - Additional source
GITHUB_SUNNY9577_ALL = ProxySourceConfig(
    url="https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/generated/http_proxies.txt",
    format="plain_text",
)

# officialputuid/KangProxy - Large Indonesian source
GITHUB_KANGPROXY_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/http/http.txt",
    format="plain_text",
)

GITHUB_KANGPROXY_HTTPS = ProxySourceConfig(
    url="https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/https/https.txt",
    format="plain_text",
)

GITHUB_KANGPROXY_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks4/socks4.txt",
    format="plain_text",
    protocol="socks4",
)

GITHUB_KANGPROXY_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt",
    format="plain_text",
    protocol="socks5",
)

# proxy4parsing/proxy-list - Frequently updated
GITHUB_PROXY4PARSING_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt",
    format="plain_text",
)

GITHUB_PROXY4PARSING_HTTPS = ProxySourceConfig(
    url="https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/https.txt",
    format="plain_text",
)

# rx443/proxy-list - Updated frequently
GITHUB_RX443_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/rx443/proxy-list/main/online/http.txt",
    format="plain_text",
    trusted=True,  # "online" = validated
)

GITHUB_RX443_HTTPS = ProxySourceConfig(
    url="https://raw.githubusercontent.com/rx443/proxy-list/main/online/https.txt",
    format="plain_text",
    trusted=True,
)

GITHUB_RX443_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/rx443/proxy-list/main/online/socks4.txt",
    format="plain_text",
    protocol="socks4",
    trusted=True,
)

GITHUB_RX443_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/rx443/proxy-list/main/online/socks5.txt",
    format="plain_text",
    protocol="socks5",
    trusted=True,
)

# KangProxy combined RAW list - All protocols in one
GITHUB_KANGPROXY_RAW = ProxySourceConfig(
    url="https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/xResults/RAW.txt",
    format="plain_text",
)

# MrMarble/proxy-list - Frequently updated
GITHUB_MRMARBLE_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/MrMarble/proxy-list/main/http.txt",
    format="plain_text",
)

GITHUB_MRMARBLE_HTTPS = ProxySourceConfig(
    url="https://raw.githubusercontent.com/MrMarble/proxy-list/main/https.txt",
    format="plain_text",
)

GITHUB_MRMARBLE_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/MrMarble/proxy-list/main/socks4.txt",
    format="plain_text",
    protocol="socks4",
)

GITHUB_MRMARBLE_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/MrMarble/proxy-list/main/socks5.txt",
    format="plain_text",
    protocol="socks5",
)

# caliphdev/Proxy-List - Updated hourly
GITHUB_CALIPH_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/caliphdev/Proxy-List/main/http.txt",
    format="plain_text",
)

GITHUB_CALIPH_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/caliphdev/Proxy-List/main/socks4.txt",
    format="plain_text",
    protocol="socks4",
)

GITHUB_CALIPH_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/caliphdev/Proxy-List/main/socks5.txt",
    format="plain_text",
    protocol="socks5",
)

# zloi-user/hideip.me - Very large lists
GITHUB_ZLOI_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/zloi-user/hideip.me/main/http.txt",
    format="plain_text",
)

GITHUB_ZLOI_HTTPS = ProxySourceConfig(
    url="https://raw.githubusercontent.com/zloi-user/hideip.me/main/https.txt",
    format="plain_text",
)

GITHUB_ZLOI_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks4.txt",
    format="plain_text",
    protocol="socks4",
)

GITHUB_ZLOI_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks5.txt",
    format="plain_text",
    protocol="socks5",
)

# proxy-list.download API - Free API with all proxy types
PROXYLISTDOWNLOAD_HTTP = ProxySourceConfig(
    url="https://www.proxy-list.download/api/v1/get?type=http",
    format="plain_text",
)

PROXYLISTDOWNLOAD_HTTPS = ProxySourceConfig(
    url="https://www.proxy-list.download/api/v1/get?type=https",
    format="plain_text",
)

PROXYLISTDOWNLOAD_SOCKS4 = ProxySourceConfig(
    url="https://www.proxy-list.download/api/v1/get?type=socks4",
    format="plain_text",
    protocol="socks4",
)

PROXYLISTDOWNLOAD_SOCKS5 = ProxySourceConfig(
    url="https://www.proxy-list.download/api/v1/get?type=socks5",
    format="plain_text",
    protocol="socks5",
)

# mishakorzik/100000-Proxy - Claims 100k+ proxies
GITHUB_MISHAKORZIK_ALL = ProxySourceConfig(
    url="https://raw.githubusercontent.com/mishakorzik/100000-Proxy/main/proxy.txt",
    format="plain_text",
)

# roosterkid/openproxylist - SOCKS proxies
GITHUB_ROOSTERKID_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4.txt",
    format="plain_text",
    protocol="socks4",
)

GITHUB_ROOSTERKID_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5.txt",
    format="plain_text",
    protocol="socks5",
)

# sunny9577/proxy-scraper - SOCKS proxies
GITHUB_SUNNY9577_SOCKS4 = ProxySourceConfig(
    url="https://sunny9577.github.io/proxy-scraper/generated/socks4_proxies.txt",
    format="plain_text",
    protocol="socks4",
)

GITHUB_SUNNY9577_SOCKS5 = ProxySourceConfig(
    url="https://sunny9577.github.io/proxy-scraper/generated/socks5_proxies.txt",
    format="plain_text",
    protocol="socks5",
)

# =============================================================================
# NEW SOURCES - Added Jan 2026 (targeting 10k+ validated proxies)
# =============================================================================

# ALIILAPRO/Proxy - Updated hourly, large lists
GITHUB_ALIILAPRO_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/http.txt",
    format="plain_text",
)

GITHUB_ALIILAPRO_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/socks4.txt",
    format="plain_text",
    protocol="socks4",
)

GITHUB_ALIILAPRO_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/socks5.txt",
    format="plain_text",
    protocol="socks5",
)

# fate0/proxylist - Generated every 15 minutes
GITHUB_FATE0_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list",
    format="plain_text",
)

# Skillter/ProxyGather - Automated every 30 minutes
GITHUB_SKILLTER_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/Skillter/ProxyGather/master/proxies/working-proxies-http.txt",
    format="plain_text",
    trusted=True,  # Pre-validated working proxies
)

GITHUB_SKILLTER_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/Skillter/ProxyGather/master/proxies/working-proxies-socks4.txt",
    format="plain_text",
    protocol="socks4",
    trusted=True,
)

GITHUB_SKILLTER_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/Skillter/ProxyGather/master/proxies/working-proxies-socks5.txt",
    format="plain_text",
    protocol="socks5",
    trusted=True,
)

GITHUB_SKILLTER_ALL = ProxySourceConfig(
    url="https://raw.githubusercontent.com/Skillter/ProxyGather/master/proxies/working-proxies-all.txt",
    format="plain_text",
    trusted=True,
)

# sh4dowb/proxy-scraper - Hourly updated
GITHUB_SH4DOWB_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/sh4dowb/proxy-scraper/main/proxies/http.txt",
    format="plain_text",
)

GITHUB_SH4DOWB_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/sh4dowb/proxy-scraper/main/proxies/socks4.txt",
    format="plain_text",
    protocol="socks4",
)

GITHUB_SH4DOWB_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/sh4dowb/proxy-scraper/main/proxies/socks5.txt",
    format="plain_text",
    protocol="socks5",
)

# Anonym0usWork1221/Free-Proxies - Large lists
GITHUB_ANONYM0USWORK_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/http_proxies.txt",
    format="plain_text",
)

GITHUB_ANONYM0USWORK_HTTPS = ProxySourceConfig(
    url="https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/https_proxies.txt",
    format="plain_text",
)

GITHUB_ANONYM0USWORK_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/socks4_proxies.txt",
    format="plain_text",
    protocol="socks4",
)

GITHUB_ANONYM0USWORK_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/socks5_proxies.txt",
    format="plain_text",
    protocol="socks5",
)

# a2u/free-proxy-list - Validated hourly
GITHUB_A2U_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/a2u/free-proxy-list/master/free-proxy-list.txt",
    format="plain_text",
    trusted=True,  # Pre-validated for IP hiding
)

# PubProxy API - Random proxy API
PUBPROXY_HTTP = ProxySourceConfig(
    url="http://pubproxy.com/api/proxy?limit=20&format=txt&type=http",
    format="plain_text",
)

PUBPROXY_SOCKS4 = ProxySourceConfig(
    url="http://pubproxy.com/api/proxy?limit=20&format=txt&type=socks4",
    format="plain_text",
    protocol="socks4",
)

PUBPROXY_SOCKS5 = ProxySourceConfig(
    url="http://pubproxy.com/api/proxy?limit=20&format=txt&type=socks5",
    format="plain_text",
    protocol="socks5",
)

# hidemy.name free proxy list
HIDEMY_HTTP = ProxySourceConfig(
    url="https://hidemy.io/api/proxylist.php?out=plain&type=h",
    format="plain_text",
)

HIDEMY_SOCKS4 = ProxySourceConfig(
    url="https://hidemy.io/api/proxylist.php?out=plain&type=4",
    format="plain_text",
    protocol="socks4",
)

HIDEMY_SOCKS5 = ProxySourceConfig(
    url="https://hidemy.io/api/proxylist.php?out=plain&type=5",
    format="plain_text",
    protocol="socks5",
)

# proxy-list.org - Free proxy lists
PROXYLISTORG_HTTP = ProxySourceConfig(
    url="https://proxy-list.org/english/index.php",
    format="plain_text",
)

# MuRongPIG/Proxy-Master - Aggregated large lists
GITHUB_MURONGPIG_ALL = ProxySourceConfig(
    url="https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt",
    format="plain_text",
)

# =============================================================================
# Predefined Source Collections
# =============================================================================

# All HTTP/HTTPS sources
ALL_HTTP_SOURCES = [
    # API sources (high reliability)
    PROXY_SCRAPE_HTTP,  # ProxyScrape - large list
    PROXY_SCRAPE_HTTP_ANONYMOUS,  # Elite/anonymous proxies
    PROXY_SCRAPE_HTTPS,  # SSL proxies
    GEONODE_HTTP,
    # GitHub sources (high volume)
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
    # NEW sources (Jan 2026) - targeting 25k+ total
    GITHUB_IPLOCATE_HTTP,
    GITHUB_IPLOCATE_HTTPS,
    GITHUB_IPLOCATE_ALL,
    GITHUB_A2U_HTTP,
    GITHUB_PROXYSCRAPER_HTTP,
    GITHUB_ZEBBERN_HTTP,
    GITHUB_ZEBBERN_HTTPS,
    GITHUB_UPTIMERBOT_HTTP,
    GITHUB_MURONGPIG_HTTP_ALL,
    GITHUB_SUNNY9577_ALL,
    GITHUB_KANGPROXY_HTTP,
    GITHUB_KANGPROXY_HTTPS,
    GITHUB_PROXY4PARSING_HTTPS,
    GITHUB_RX443_HTTP,
    GITHUB_RX443_HTTPS,
    GITHUB_ZLOI_HTTP,
    GITHUB_ZLOI_HTTPS,
    GITHUB_KANGPROXY_RAW,
    GITHUB_MRMARBLE_HTTP,
    GITHUB_MRMARBLE_HTTPS,
    GITHUB_CALIPH_HTTP,
    # High-volume sources (Jan 2026)
    PROXYLISTDOWNLOAD_HTTP,
    PROXYLISTDOWNLOAD_HTTPS,
    GITHUB_MISHAKORZIK_ALL,
    # NEW sources (Jan 2026) - targeting 10k+ validated
    GITHUB_ALIILAPRO_HTTP,
    GITHUB_FATE0_HTTP,
    GITHUB_SKILLTER_HTTP,
    GITHUB_SKILLTER_ALL,
    GITHUB_SH4DOWB_HTTP,
    GITHUB_ANONYM0USWORK_HTTP,
    GITHUB_ANONYM0USWORK_HTTPS,
    GITHUB_A2U_HTTP,
    PUBPROXY_HTTP,
    HIDEMY_HTTP,
    GITHUB_MURONGPIG_ALL,
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
    # NEW sources (Jan 2026) - targeting 25k+ total
    GITHUB_IPLOCATE_SOCKS4,
    GITHUB_PROXYSCRAPER_SOCKS4,
    GITHUB_ZEBBERN_SOCKS4,
    GITHUB_UPTIMERBOT_SOCKS4,
    GITHUB_KANGPROXY_SOCKS4,
    GITHUB_RX443_SOCKS4,
    GITHUB_ZLOI_SOCKS4,
    GITHUB_MRMARBLE_SOCKS4,
    GITHUB_CALIPH_SOCKS4,
    # High-volume sources (Jan 2026)
    PROXYLISTDOWNLOAD_SOCKS4,
    GITHUB_ROOSTERKID_SOCKS4,
    GITHUB_SUNNY9577_SOCKS4,
    # NEW sources (Jan 2026) - targeting 10k+ validated
    GITHUB_ALIILAPRO_SOCKS4,
    GITHUB_SKILLTER_SOCKS4,
    GITHUB_SH4DOWB_SOCKS4,
    GITHUB_ANONYM0USWORK_SOCKS4,
    PUBPROXY_SOCKS4,
    HIDEMY_SOCKS4,
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
    # NEW sources (Jan 2026) - targeting 25k+ total
    GITHUB_IPLOCATE_SOCKS5,
    GITHUB_PROXYSCRAPER_SOCKS5,
    GITHUB_ZEBBERN_SOCKS5,
    GITHUB_UPTIMERBOT_SOCKS5,
    GITHUB_KANGPROXY_SOCKS5,
    GITHUB_RX443_SOCKS5,
    GITHUB_ZLOI_SOCKS5,
    GITHUB_MRMARBLE_SOCKS5,
    GITHUB_CALIPH_SOCKS5,
    # High-volume sources (Jan 2026)
    PROXYLISTDOWNLOAD_SOCKS5,
    GITHUB_ROOSTERKID_SOCKS5,
    GITHUB_SUNNY9577_SOCKS5,
    # NEW sources (Jan 2026) - targeting 10k+ validated
    GITHUB_ALIILAPRO_SOCKS5,
    GITHUB_SKILLTER_SOCKS5,
    GITHUB_SH4DOWB_SOCKS5,
    GITHUB_ANONYM0USWORK_SOCKS5,
    PUBPROXY_SOCKS5,
    HIDEMY_SOCKS5,
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
