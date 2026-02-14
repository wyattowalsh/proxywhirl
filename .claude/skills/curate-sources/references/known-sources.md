# Known Proxy Sources Inventory

Current sources in `proxywhirl/sources.py`. Use this to avoid adding duplicates.

> **Note:** Regenerate this file before each curation run using:
> `uv run python scripts/curate_sources.py validate | python -c "import json,sys; ..."`

## API Sources

| Variable | URL | Protocol | Trusted | Collections |
|----------|-----|----------|---------|-------------|
| `PROXY_SCRAPE_HTTP` | api.proxyscrape.com (http) | http | No | HTTP |
| `PROXY_SCRAPE_HTTP_ANONYMOUS` | api.proxyscrape.com (elite/anonymous) | http | No | HTTP |
| `PROXY_SCRAPE_HTTPS` | api.proxyscrape.com (ssl=yes) | http | No | HTTP |
| `GEONODE_HTTP` | proxylist.geonode.com (http/https) | http | Yes | HTTP, RECOMMENDED, API |
| `GEONODE_SOCKS4` | proxylist.geonode.com (socks4) | socks4 | Yes | SOCKS4, API |
| `GEONODE_SOCKS5` | proxylist.geonode.com (socks5) | socks5 | Yes | SOCKS5, API |
| `PROXY_SCRAPE_SOCKS4` | api.proxyscrape.com (socks4) | socks4 | No | SOCKS4 |
| `PROXY_SCRAPE_SOCKS5` | api.proxyscrape.com (socks5) | socks5 | No | SOCKS5 |
| `PUBPROXY_HTTP` | pubproxy.com (http) | http | No | HTTP |
| `PUBPROXY_SOCKS4` | pubproxy.com (socks4) | socks4 | No | SOCKS4 |
| `PUBPROXY_SOCKS5` | pubproxy.com (socks5) | socks5 | No | SOCKS5 |

## Non-GitHub Web Sources

| Variable | URL | Protocol | Trusted | Collections |
|----------|-----|----------|---------|-------------|
| `PROXYSPACE_HTTP` | proxyspace.pro/http.txt | http | No | HTTP |
| `PROXYSPACE_SOCKS4` | proxyspace.pro/socks4.txt | socks4 | No | SOCKS4 |
| `PROXYSPACE_SOCKS5` | proxyspace.pro/socks5.txt | socks5 | No | SOCKS5 |
| `OPENPROXYLIST_HTTP` | openproxylist.xyz/http.txt | http | No | HTTP |
| `JSDELIVR_PROXIFLY_ALL` | cdn.jsdelivr.net (proxifly) | http | Yes | HTTP |

## GitHub Sources

| Variable | Repo | Protocol | Trusted | Collections |
|----------|------|----------|---------|-------------|
| `GITHUB_THESPEEDX_HTTP` | TheSpeedX/PROXY-List | http | No | HTTP |
| `GITHUB_THESPEEDX_SOCKS4` | TheSpeedX/PROXY-List | socks4 | No | SOCKS4 |
| `GITHUB_THESPEEDX_SOCKS5` | TheSpeedX/PROXY-List | socks5 | No | SOCKS5 |
| `GITHUB_MONOSANS_HTTP` | monosans/proxy-list | http | Yes | HTTP, RECOMMENDED |
| `GITHUB_MONOSANS_SOCKS4` | monosans/proxy-list | socks4 | Yes | SOCKS4 |
| `GITHUB_MONOSANS_SOCKS5` | monosans/proxy-list | socks5 | Yes | SOCKS5, RECOMMENDED |
| `GITHUB_ROOSTERKID_HTTP` | roosterkid/openproxylist | http | No | HTTP |
| `GITHUB_ROOSTERKID_SOCKS4` | roosterkid/openproxylist | socks4 | No | SOCKS4 |
| `GITHUB_ROOSTERKID_SOCKS5` | roosterkid/openproxylist | socks5 | No | SOCKS5 |
| `GITHUB_SUNNY9577_HTTP` | sunny9577/proxy-scraper | http | No | HTTP |
| `GITHUB_SUNNY9577_ALL` | sunny9577/proxy-scraper | http | No | HTTP |
| `GITHUB_SUNNY9577_SOCKS4` | sunny9577/proxy-scraper | socks4 | No | SOCKS4 |
| `GITHUB_SUNNY9577_SOCKS5` | sunny9577/proxy-scraper | socks5 | No | SOCKS5 |
| `GITHUB_ASLISK_HTTP` | aslisk/proxyhttps | http | No | HTTP |
| `GITHUB_MMPX12_HTTP` | mmpx12/proxy-list | http | No | HTTP |
| `GITHUB_MMPX12_HTTPS` | mmpx12/proxy-list | http | No | HTTP |
| `GITHUB_MMPX12_SOCKS4` | mmpx12/proxy-list | socks4 | No | SOCKS4 |
| `GITHUB_MMPX12_SOCKS5` | mmpx12/proxy-list | socks5 | No | SOCKS5 |
| `GITHUB_PROXIFLY_HTTP` | proxifly/free-proxy-list | http | Yes | HTTP, RECOMMENDED |
| `GITHUB_PROXIFLY_SOCKS4` | proxifly/free-proxy-list | socks4 | Yes | SOCKS4 |
| `GITHUB_PROXIFLY_SOCKS5` | proxifly/free-proxy-list | socks5 | Yes | SOCKS5 |
| `GITHUB_ELLIOTTOPHELLIA_HTTP` | elliottophellia/yakumo | http | Yes | HTTP |
| `GITHUB_ELLIOTTOPHELLIA_SOCKS4` | elliottophellia/yakumo | socks4 | Yes | SOCKS4 |
| `GITHUB_ELLIOTTOPHELLIA_SOCKS5` | elliottophellia/yakumo | socks5 | Yes | SOCKS5 |
| `GITHUB_OPENPROXY_HTTP` | officialputuid/KangProxy | http | No | HTTP |
| `GITHUB_OPENPROXY_HTTPS` | officialputuid/KangProxy | http | No | HTTP |
| `GITHUB_OPENPROXY_SOCKS4` | officialputuid/KangProxy | socks4 | No | SOCKS4 |
| `GITHUB_OPENPROXY_SOCKS5` | officialputuid/KangProxy | socks5 | No | SOCKS5 |
| `GITHUB_VAKHOV_HTTP` | vakhov/fresh-proxy-list | http | Yes | HTTP |
| `GITHUB_VAKHOV_HTTPS` | vakhov/fresh-proxy-list | http | Yes | HTTP |
| `GITHUB_VAKHOV_SOCKS4` | vakhov/fresh-proxy-list | socks4 | Yes | SOCKS4 |
| `GITHUB_VAKHOV_SOCKS5` | vakhov/fresh-proxy-list | socks5 | Yes | SOCKS5 |
| `GITHUB_ZAEEM_HTTP` | Zaeem20/FREE_PROXIES_LIST | http | No | HTTP |
| `GITHUB_ZAEEM_SOCKS4` | Zaeem20/FREE_PROXIES_LIST | socks4 | No | SOCKS4 |
| `GITHUB_MURONGPIG_HTTP` | MuRongPig/Proxy-Master | http | No | HTTP |
| `GITHUB_MURONGPIG_SOCKS4` | MuRongPig/Proxy-Master | socks4 | No | SOCKS4 |
| `GITHUB_MURONGPIG_SOCKS5` | MuRongPig/Proxy-Master | socks5 | No | SOCKS5 |
| `GITHUB_KOMUTAN_HTTP` | komutan234/Proxy-List-Free | http | Yes | HTTP, RECOMMENDED |
| `GITHUB_KOMUTAN_SOCKS4` | komutan234/Proxy-List-Free | socks4 | Yes | SOCKS4 |
| `GITHUB_KOMUTAN_SOCKS5` | komutan234/Proxy-List-Free | socks5 | Yes | SOCKS5 |
| `GITHUB_ANONYM0US_HTTP` | Anonym0usWork1221/Free-Proxies | http | No | HTTP |
| `GITHUB_ANONYM0US_HTTPS` | Anonym0usWork1221/Free-Proxies | http | No | HTTP |
| `GITHUB_ANONYM0US_SOCKS4` | Anonym0usWork1221/Free-Proxies | socks4 | No | SOCKS4 |
| `GITHUB_ANONYM0US_SOCKS5` | Anonym0usWork1221/Free-Proxies | socks5 | No | SOCKS5 |
| `GITHUB_HOOKZOF_SOCKS5` | hookzof/socks5_list | socks5 | No | SOCKS5 |
| `GITHUB_DPANGESTUW_HTTP` | dpangestuw/Free-Proxy | http | No | HTTP |
| `GITHUB_DPANGESTUW_SOCKS4` | dpangestuw/Free-Proxy | socks4 | No | SOCKS4 |
| `GITHUB_DPANGESTUW_SOCKS5` | dpangestuw/Free-Proxy | socks5 | No | SOCKS5 |
| `GITHUB_TSPRNAY_HTTP` | Tsprnay/Proxy-lists | http | No | HTTP |
| `GITHUB_TSPRNAY_HTTPS` | Tsprnay/Proxy-lists | http | No | HTTP |
| `GITHUB_TSPRNAY_SOCKS4` | Tsprnay/Proxy-lists | socks4 | No | SOCKS4 |
| `GITHUB_TSPRNAY_SOCKS5` | Tsprnay/Proxy-lists | socks5 | No | SOCKS5 |
| `GITHUB_ZEVTYARDT_HTTP` | mzyui/proxy-list | http | No | HTTP |
| `GITHUB_ZEVTYARDT_SOCKS4` | mzyui/proxy-list | socks4 | No | SOCKS4 |
| `GITHUB_ZEVTYARDT_SOCKS5` | mzyui/proxy-list | socks5 | No | SOCKS5 |
| `GITHUB_ERCINDEDEOGLU_HTTP` | ErcinDedeoglu/proxies | http | No | HTTP |
| `GITHUB_ERCINDEDEOGLU_HTTPS` | ErcinDedeoglu/proxies | http | No | HTTP |
| `GITHUB_ERCINDEDEOGLU_SOCKS4` | ErcinDedeoglu/proxies | socks4 | No | SOCKS4 |
| `GITHUB_ERCINDEDEOGLU_SOCKS5` | ErcinDedeoglu/proxies | socks5 | No | SOCKS5 |
| `GITHUB_IPLOCATE_HTTP` | iplocate/free-proxy-list | http | Yes | HTTP |
| `GITHUB_IPLOCATE_HTTPS` | iplocate/free-proxy-list | http | Yes | HTTP |
| `GITHUB_IPLOCATE_SOCKS4` | iplocate/free-proxy-list | socks4 | Yes | SOCKS4 |
| `GITHUB_IPLOCATE_SOCKS5` | iplocate/free-proxy-list | socks5 | Yes | SOCKS5 |
| `GITHUB_IPLOCATE_ALL` | iplocate/free-proxy-list | http | Yes | HTTP |
| `GITHUB_PROXYSCRAPER_HTTP` | ProxyScraper/ProxyScraper | http | No | HTTP |
| `GITHUB_PROXYSCRAPER_SOCKS4` | ProxyScraper/ProxyScraper | socks4 | No | SOCKS4 |
| `GITHUB_PROXYSCRAPER_SOCKS5` | ProxyScraper/ProxyScraper | socks5 | No | SOCKS5 |
| `GITHUB_RX443_HTTP` | rx443/proxy-list | http | Yes | HTTP |
| `GITHUB_RX443_HTTPS` | rx443/proxy-list | http | Yes | HTTP |
| `GITHUB_RX443_SOCKS4` | rx443/proxy-list | socks4 | Yes | SOCKS4 |
| `GITHUB_RX443_SOCKS5` | rx443/proxy-list | socks5 | Yes | SOCKS5 |
| `GITHUB_MRMARBLE_HTTP` | MrMarble/proxy-list | http | No | HTTP |
| `GITHUB_MRMARBLE_HTTPS` | MrMarble/proxy-list | http | No | HTTP |
| `GITHUB_MRMARBLE_SOCKS4` | MrMarble/proxy-list | socks4 | No | SOCKS4 |
| `GITHUB_MRMARBLE_SOCKS5` | MrMarble/proxy-list | socks5 | No | SOCKS5 |
| `GITHUB_ZLOI_HTTP` | zloi-user/hideip.me | http | No | HTTP |
| `GITHUB_ZLOI_HTTPS` | zloi-user/hideip.me | http | No | HTTP |
| `GITHUB_ZLOI_SOCKS4` | zloi-user/hideip.me | socks4 | No | SOCKS4 |
| `GITHUB_ZLOI_SOCKS5` | zloi-user/hideip.me | socks5 | No | SOCKS5 |
| `GITHUB_ALIILAPRO_HTTP` | ALIILAPRO/Proxy | http | No | HTTP |
| `GITHUB_ALIILAPRO_SOCKS4` | ALIILAPRO/Proxy | socks4 | No | SOCKS4 |
| `GITHUB_ALIILAPRO_SOCKS5` | ALIILAPRO/Proxy | socks5 | No | SOCKS5 |
| `GITHUB_SKILLTER_HTTP` | Skillter/ProxyGather | http | Yes | HTTP |
| `GITHUB_SKILLTER_SOCKS4` | Skillter/ProxyGather | socks4 | Yes | SOCKS4 |
| `GITHUB_SKILLTER_SOCKS5` | Skillter/ProxyGather | socks5 | Yes | SOCKS5 |
| `GITHUB_SKILLTER_ALL` | Skillter/ProxyGather | http | Yes | HTTP |
| `GITHUB_R00TEE_HTTP` | r00tee/Proxy-List | http | No | HTTP |
| `GITHUB_R00TEE_SOCKS4` | r00tee/Proxy-List | socks4 | No | SOCKS4 |
| `GITHUB_R00TEE_SOCKS5` | r00tee/Proxy-List | socks5 | No | SOCKS5 |
| `GITHUB_SEVENWORKS_HTTP` | SevenworksDev/proxy-list | http | No | HTTP |
| `GITHUB_SEVENWORKS_HTTPS` | SevenworksDev/proxy-list | http | No | HTTP |
| `GITHUB_SEVENWORKS_SOCKS4` | SevenworksDev/proxy-list | socks4 | No | SOCKS4 |
| `GITHUB_SEVENWORKS_SOCKS5` | SevenworksDev/proxy-list | socks5 | No | SOCKS5 |
| `GITHUB_VANNDEV_HTTP` | Vann-Dev/proxy-list | http | No | HTTP |
| `GITHUB_VANNDEV_SOCKS4` | Vann-Dev/proxy-list | socks4 | No | SOCKS4 |
| `GITHUB_VANNDEV_SOCKS5` | Vann-Dev/proxy-list | socks5 | No | SOCKS5 |
| `GITHUB_CLEARPROXY_HTTP` | ClearProxy/checked-proxy-list | http | Yes | HTTP |
| `GITHUB_CLEARPROXY_SOCKS4` | ClearProxy/checked-proxy-list | socks4 | Yes | SOCKS4 |
| `GITHUB_CLEARPROXY_SOCKS5` | ClearProxy/checked-proxy-list | socks5 | Yes | SOCKS5 |
| `GITHUB_TUANMINPAY_HTTP` | TuanMinPay/live-proxy | http | No | HTTP |
| `GITHUB_TUANMINPAY_SOCKS4` | TuanMinPay/live-proxy | socks4 | No | SOCKS4 |
| `GITHUB_TUANMINPAY_SOCKS5` | TuanMinPay/live-proxy | socks5 | No | SOCKS5 |
| `GITHUB_VMHEAVEN_HTTP` | vmheaven/VMHeaven-Free-Proxy-Updated | http | No | HTTP |
| `GITHUB_VMHEAVEN_SOCKS4` | vmheaven/VMHeaven-Free-Proxy-Updated | socks4 | No | SOCKS4 |
| `GITHUB_VMHEAVEN_SOCKS5` | vmheaven/VMHeaven-Free-Proxy-Updated | socks5 | No | SOCKS5 |
| `GITHUB_VADIM287_HTTP` | Vadim287/free-proxy | http | No | HTTP |
| `GITHUB_VADIM287_SOCKS4` | Vadim287/free-proxy | socks4 | No | SOCKS4 |
| `GITHUB_VADIM287_SOCKS5` | Vadim287/free-proxy | socks5 | No | SOCKS5 |

## Unique GitHub Repos (for dedup)

These are the unique GitHub repos currently tracked:
- TheSpeedX/PROXY-List
- monosans/proxy-list
- roosterkid/openproxylist
- sunny9577/proxy-scraper
- aslisk/proxyhttps
- mmpx12/proxy-list
- proxifly/free-proxy-list
- elliottophellia/yakumo
- officialputuid/KangProxy
- vakhov/fresh-proxy-list
- Zaeem20/FREE_PROXIES_LIST
- MuRongPig/Proxy-Master
- komutan234/Proxy-List-Free
- Anonym0usWork1221/Free-Proxies
- hookzof/socks5_list
- dpangestuw/Free-Proxy
- Tsprnay/Proxy-lists
- mzyui/proxy-list (formerly zevtyardt/proxy-list)
- ErcinDedeoglu/proxies
- iplocate/free-proxy-list
- ProxyScraper/ProxyScraper
- rx443/proxy-list
- MrMarble/proxy-list
- zloi-user/hideip.me
- ALIILAPRO/Proxy
- Skillter/ProxyGather
- r00tee/Proxy-List
- SevenworksDev/proxy-list
- Vann-Dev/proxy-list
- ClearProxy/checked-proxy-list
- TuanMinPay/live-proxy
- vmheaven/VMHeaven-Free-Proxy-Updated
- Vadim287/free-proxy

## API/Web Endpoints (for dedup)

- api.proxyscrape.com
- proxylist.geonode.com
- pubproxy.com
- proxyspace.pro
- openproxylist.xyz
- cdn.jsdelivr.net (proxifly mirror)
