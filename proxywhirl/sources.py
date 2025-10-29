"""Built-in proxy source configurations.

This module provides pre-configured ProxySourceConfig instances for popular
free proxy list APIs and websites. These can be used directly with ProxyFetcher.

Example:
    >>> from proxywhirl import ProxyFetcher
    >>> from proxywhirl.sources import FREE_PROXY_LIST, PROXY_SCRAPE
    >>> fetcher = ProxyFetcher(sources=[FREE_PROXY_LIST, PROXY_SCRAPE])
    >>> proxies = await fetcher.fetch_all()
"""

from proxywhirl.fetchers import ProxySourceConfig

# =============================================================================
# API-Based Sources (JSON/CSV formats)
# =============================================================================

FREE_PROXY_LIST = ProxySourceConfig(
    url="https://www.proxy-list.download/api/v1/get?type=http",
    format="plain_text",
)

PROXY_SCRAPE_HTTP = ProxySourceConfig(
    url="https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    format="plain_text",
)

PROXY_SCRAPE_SOCKS4 = ProxySourceConfig(
    url="https://api.proxyscrape.com/v2/?request=get&protocol=socks4&timeout=10000&country=all",
    format="plain_text",
)

PROXY_SCRAPE_SOCKS5 = ProxySourceConfig(
    url="https://api.proxyscrape.com/v2/?request=get&protocol=socks5&timeout=10000&country=all",
    format="plain_text",
)

GEONODE_HTTP = ProxySourceConfig(
    url="https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=http%2Chttps",
    format="json",
)

GEONODE_SOCKS4 = ProxySourceConfig(
    url="https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks4",
    format="json",
)

GEONODE_SOCKS5 = ProxySourceConfig(
    url="https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5",
    format="json",
)

PROXY_NOVA = ProxySourceConfig(
    url="https://www.proxynova.com/proxy-server-list/",
    format="html",
)

# =============================================================================
# GitHub-Hosted Proxy Lists (Updated frequently)
# =============================================================================

GITHUB_CLARKETM_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    format="plain_text",
)

GITHUB_THESPECBAY_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    format="plain_text",
)

GITHUB_THESPECBAY_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
    format="plain_text",
)

GITHUB_THESPECBAY_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    format="plain_text",
)

GITHUB_MONOSANS_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    format="plain_text",
)

GITHUB_MONOSANS_SOCKS4 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt",
    format="plain_text",
)

GITHUB_MONOSANS_SOCKS5 = ProxySourceConfig(
    url="https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
    format="plain_text",
)

GITHUB_HOOKZOF_HTTP = ProxySourceConfig(
    url="https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    format="plain_text",
)

# =============================================================================
# Predefined Source Collections
# =============================================================================

# All HTTP/HTTPS sources
ALL_HTTP_SOURCES = [
    FREE_PROXY_LIST,
    PROXY_SCRAPE_HTTP,
    GEONODE_HTTP,
    GITHUB_CLARKETM_HTTP,
    GITHUB_THESPECBAY_HTTP,
    GITHUB_MONOSANS_HTTP,
]

# All SOCKS4 sources
ALL_SOCKS4_SOURCES = [
    PROXY_SCRAPE_SOCKS4,
    GEONODE_SOCKS4,
    GITHUB_THESPECBAY_SOCKS4,
    GITHUB_MONOSANS_SOCKS4,
]

# All SOCKS5 sources
ALL_SOCKS5_SOURCES = [
    PROXY_SCRAPE_SOCKS5,
    GEONODE_SOCKS5,
    GITHUB_THESPECBAY_SOCKS5,
    GITHUB_MONOSANS_SOCKS5,
    GITHUB_HOOKZOF_HTTP,
]

# All sources combined
ALL_SOURCES = ALL_HTTP_SOURCES + ALL_SOCKS4_SOURCES + ALL_SOCKS5_SOURCES

# Recommended fast/reliable sources
RECOMMENDED_SOURCES = [
    PROXY_SCRAPE_HTTP,
    GEONODE_HTTP,
    GITHUB_MONOSANS_HTTP,
    GITHUB_MONOSANS_SOCKS5,
]

# API-based sources only (typically faster/more reliable)
API_SOURCES = [
    PROXY_SCRAPE_HTTP,
    PROXY_SCRAPE_SOCKS4,
    PROXY_SCRAPE_SOCKS5,
    GEONODE_HTTP,
    GEONODE_SOCKS4,
    GEONODE_SOCKS5,
]
