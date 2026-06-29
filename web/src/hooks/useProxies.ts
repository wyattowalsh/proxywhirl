import { useEffect, useState, useCallback, useRef } from "react";
import type { Protocol, RichProxyData, Proxy, SlimProxyData } from "@/types";
import { compareIPs } from "@/lib/ip";
import {
	getCache,
	setCache,
	getLargeCache,
	setLargeCache,
	CACHE_KEYS,
	DEFAULT_TTL,
} from "@/lib/cache";
import { fetchJsonWithProgress, parseSlimProxyJson } from "@/lib/proxy-fetch";
import type { SlimProxyJsonRaw } from "@/types";

export { parseSlimProxyJson } from "@/lib/proxy-fetch";

const BASE_URL = "/proxy-lists/";

export function useProxiesSlim() {
	const [data, setData] = useState<SlimProxyData | null>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [progress, setProgress] = useState<number | undefined>(undefined);
	const isMounted = useRef(true);

	useEffect(() => {
		isMounted.current = true;
		return () => {
			isMounted.current = false;
		};
	}, []);

	const fetchFromNetwork = useCallback(
		async (options: { force?: boolean; background?: boolean }) => {
			const forceRefresh = options.force ?? false;
			const background = options.background ?? false;

			if (!background) {
				setLoading(true);
				setProgress(0);
			}

			try {
				const cacheBuster = forceRefresh ? `?v=${Date.now()}` : "";
				const raw = await fetchJsonWithProgress<SlimProxyJsonRaw>(
					`${BASE_URL}proxies.json${cacheBuster}`,
					background
						? undefined
						: (percent) => {
								if (isMounted.current) setProgress(percent);
							},
				);
				const json = parseSlimProxyJson(raw);

				if (isMounted.current) {
					setData(json);
					setError(null);
				}
				setCache(CACHE_KEYS.PROXIES_SLIM, json, DEFAULT_TTL);
			} catch (err) {
				if (isMounted.current && !background) {
					setError(err instanceof Error ? err.message : "Unknown error");
				}
			} finally {
				if (isMounted.current && !background) {
					setLoading(false);
					setProgress(undefined);
				}
			}
		},
		[],
	);

	const loadData = useCallback(
		async (options?: { force?: boolean; background?: boolean }) => {
			const forceRefresh = options?.force ?? false;
			const background = options?.background ?? false;

			if (!forceRefresh) {
				const cached = getCache<SlimProxyData>(CACHE_KEYS.PROXIES_SLIM);
				if (cached) {
					setData(cached);
					setLoading(false);
					setProgress(undefined);
					void fetchFromNetwork({ force: true, background: true });
					return;
				}
			}

			await fetchFromNetwork({ force: forceRefresh, background });
		},
		[fetchFromNetwork],
	);

	useEffect(() => {
		void loadData();
	}, [loadData]);

	return { data, loading, error, progress, refresh: () => loadData({ force: true }) };
}

export function useProxiesRich() {
	const [data, setData] = useState<RichProxyData | null>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [progress, setProgress] = useState<number | undefined>(undefined);
	const isMounted = useRef(true);

	useEffect(() => {
		isMounted.current = true;
		return () => {
			isMounted.current = false;
		};
	}, []);

	const fetchFromNetwork = useCallback(
		async (options: { force?: boolean; background?: boolean }) => {
			const forceRefresh = options.force ?? false;
			const background = options.background ?? false;

			if (!background) {
				setLoading(true);
				setProgress(0);
			}

			try {
				const cacheBuster = forceRefresh ? `?v=${Date.now()}` : "";
				const json = await fetchJsonWithProgress<RichProxyData>(
					`${BASE_URL}proxies-rich.json${cacheBuster}`,
					background
						? undefined
						: (percent) => {
								if (isMounted.current) setProgress(percent);
							},
				);

				if (isMounted.current) {
					setData(json);
					setError(null);
				}
				await setLargeCache(CACHE_KEYS.PROXIES_RICH, json, DEFAULT_TTL);
			} catch (err) {
				if (isMounted.current && !background) {
					setError(err instanceof Error ? err.message : "Unknown error");
				}
			} finally {
				if (isMounted.current && !background) {
					setLoading(false);
					setProgress(undefined);
				}
			}
		},
		[],
	);

	const loadData = useCallback(
		async (options?: { force?: boolean; background?: boolean }) => {
			const forceRefresh = options?.force ?? false;
			const background = options?.background ?? false;

			if (!forceRefresh) {
				const cached =
					(await getLargeCache<RichProxyData>(CACHE_KEYS.PROXIES_RICH)) ??
					getCache<RichProxyData>(CACHE_KEYS.PROXIES);
				if (cached) {
					setData(cached);
					setLoading(false);
					setProgress(undefined);
					void fetchFromNetwork({ force: true, background: true });
					return;
				}
			}

			await fetchFromNetwork({ force: forceRefresh, background });
		},
		[fetchFromNetwork],
	);

	useEffect(() => {
		void loadData();
	}, [loadData]);

	return { data, loading, error, progress, refresh: () => loadData({ force: true }) };
}

/** @deprecated Use useProxiesRich() */
export function useRichProxies() {
	return useProxiesRich();
}

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
		// Search filter
		if (filters.search) {
			const searchLower = filters.search.toLowerCase();
			const matchesSearch =
				proxy.ip.toLowerCase().includes(searchLower) ||
				proxy.port.toString().includes(searchLower) ||
				proxy.source.toLowerCase().includes(searchLower);
			if (!matchesSearch) return false;
		}

		// Protocol filter
		if (filters.protocols.length > 0) {
			if (!filters.protocols.includes(proxy.protocol)) return false;
		}

		// Status filter
		if (filters.statuses.length > 0) {
			if (!filters.statuses.includes(proxy.status)) return false;
		}

		// Country filter
		if (filters.countries && filters.countries.length > 0) {
			if (
				!proxy.country_code ||
				!filters.countries.includes(proxy.country_code)
			)
				return false;
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
			case "response_time":
				const aTime = a.response_time ?? Infinity;
				const bTime = b.response_time ?? Infinity;
				comparison = aTime - bTime;
				break;
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