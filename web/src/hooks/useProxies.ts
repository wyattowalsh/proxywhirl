import type { Protocol, Proxy } from "@/types";
import { compareIPs } from "@/lib/ip";

export { parseSlimProxyJson } from "@/lib/proxy-fetch";

export interface ProxyFilters {
	search: string;
	protocols: Protocol[];
	statuses: string[];
	countries: string[];
}

export function filterProxies(
	proxies: Proxy[],
	filters: ProxyFilters,
): Proxy[] {
	return proxies.filter((proxy) => {
		if (filters.search) {
			const searchLower = filters.search.toLowerCase();
			const matchesSearch =
				proxy.ip.toLowerCase().includes(searchLower) ||
				proxy.port.toString().includes(searchLower) ||
				proxy.source.toLowerCase().includes(searchLower);
			if (!matchesSearch) return false;
		}

		if (filters.protocols.length > 0) {
			if (!filters.protocols.includes(proxy.protocol)) return false;
		}

		if (filters.statuses.length > 0) {
			if (!filters.statuses.includes(proxy.status)) return false;
		}

		if (filters.countries && filters.countries.length > 0) {
			if (
				!proxy.country_code ||
				!filters.countries.includes(proxy.country_code)
			) {
				return false;
			}
		}

		return true;
	});
}

export type SortField =
	| "ip"
	| "port"
	| "protocol"
	| "status"
	| "response_time"
	| "source"
	| "created_at";
export type SortDirection = "asc" | "desc";

export function sortProxies(
	proxies: Proxy[],
	field: SortField,
	direction: SortDirection,
): Proxy[] {
	return [...proxies].sort((a, b) => {
		let comparison = 0;

		switch (field) {
			case "ip":
				comparison = compareIPs(a.ip, b.ip);
				break;
			case "port":
				comparison = a.port - b.port;
				break;
			case "protocol":
				comparison = a.protocol.localeCompare(b.protocol);
				break;
			case "status":
				comparison = a.status.localeCompare(b.status);
				break;
			case "response_time": {
				const aTime = a.response_time ?? Infinity;
				const bTime = b.response_time ?? Infinity;
				comparison = aTime - bTime;
				break;
			}
			case "source":
				comparison = a.source.localeCompare(b.source);
				break;
			case "created_at":
				comparison =
					new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
				break;
		}

		return direction === "asc" ? comparison : -comparison;
	});
}
