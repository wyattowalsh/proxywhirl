"use client";

import {
	createContext,
	useCallback,
	useContext,
	useEffect,
	useMemo,
	useRef,
	useState,
	type ReactNode,
} from "react";
import { usePathname } from "next/navigation";
import type { RichProxyData, SlimProxyData, SlimProxyJsonRaw, Stats } from "@/types";
import {
	getCache,
	setCache,
	getLargeCache,
	setLargeCache,
	CACHE_KEYS,
	DEFAULT_TTL,
} from "@/lib/cache";
import { fetchJsonWithProgress, parseSlimProxyJson } from "@/lib/proxy-fetch";

const BASE_URL = "/proxy-lists/";
const STATS_URL = "/proxy-lists/stats.json";

interface FetchOptions {
	force?: boolean;
	background?: boolean;
}

interface ProxyDataContextValue {
	stats: Stats | null;
	statsLoading: boolean;
	statsError: string | null;
	refreshStats: () => void;

	slimData: SlimProxyData | null;
	slimLoading: boolean;
	slimError: string | null;
	slimProgress: number | undefined;
	refreshSlim: () => void;

	richData: RichProxyData | null;
	richLoading: boolean;
	richError: string | null;
	richProgress: number | undefined;
	refreshRich: () => void;
}

const ProxyDataContext = createContext<ProxyDataContextValue | null>(null);

function isAnalyticsRoute(pathname: string | null): boolean {
	return pathname === "/analytics" || (pathname?.startsWith("/analytics/") ?? false);
}

export function ProxyDataProvider({ children }: { children: ReactNode }) {
	const pathname = usePathname();
	const shouldFetchRich = isAnalyticsRoute(pathname);

	const [stats, setStats] = useState<Stats | null>(null);
	const [statsLoading, setStatsLoading] = useState(true);
	const [statsError, setStatsError] = useState<string | null>(null);

	const [slimData, setSlimData] = useState<SlimProxyData | null>(null);
	const [slimLoading, setSlimLoading] = useState(true);
	const [slimError, setSlimError] = useState<string | null>(null);
	const [slimProgress, setSlimProgress] = useState<number | undefined>(undefined);

	const [richData, setRichData] = useState<RichProxyData | null>(null);
	const [richLoading, setRichLoading] = useState(false);
	const [richError, setRichError] = useState<string | null>(null);
	const [richProgress, setRichProgress] = useState<number | undefined>(undefined);

	const isMounted = useRef(true);

	useEffect(() => {
		isMounted.current = true;
		return () => {
			isMounted.current = false;
		};
	}, []);

	const fetchStatsFromNetwork = useCallback(async (options: FetchOptions) => {
		const forceRefresh = options.force ?? false;
		const background = options.background ?? false;

		if (!background) setStatsLoading(true);

		try {
			const cacheBuster = forceRefresh ? `?v=${Date.now()}` : "";
			const res = await fetch(`${STATS_URL}${cacheBuster}`);
			if (!res.ok) throw new Error("Failed to fetch stats");
			const data: Stats = await res.json();

			if (isMounted.current) {
				setStats(data);
				setStatsError(null);
			}
			setCache(CACHE_KEYS.STATS, data, DEFAULT_TTL);
		} catch (err) {
			if (isMounted.current && !background) {
				setStatsError(err instanceof Error ? err.message : "Unknown error");
			}
		} finally {
			if (isMounted.current && !background) {
				setStatsLoading(false);
			}
		}
	}, []);

	const loadStats = useCallback(
		async (options?: FetchOptions) => {
			const forceRefresh = options?.force ?? false;
			const background = options?.background ?? false;

			if (!forceRefresh) {
				const cached = getCache<Stats>(CACHE_KEYS.STATS);
				if (cached) {
					setStats(cached);
					setStatsLoading(false);
					void fetchStatsFromNetwork({ force: true, background: true });
					return;
				}
			}

			await fetchStatsFromNetwork({ force: forceRefresh, background });
		},
		[fetchStatsFromNetwork],
	);

	const fetchSlimFromNetwork = useCallback(async (options: FetchOptions) => {
		const forceRefresh = options.force ?? false;
		const background = options.background ?? false;

		if (!background) {
			setSlimLoading(true);
			setSlimProgress(0);
		}

		try {
			const cacheBuster = forceRefresh ? `?v=${Date.now()}` : "";
			const raw = await fetchJsonWithProgress<SlimProxyJsonRaw>(
				`${BASE_URL}proxies.json${cacheBuster}`,
				background
					? undefined
					: (percent) => {
							if (isMounted.current) setSlimProgress(percent);
						},
			);
			const json = parseSlimProxyJson(raw);

			if (isMounted.current) {
				setSlimData(json);
				setSlimError(null);
			}
			setCache(CACHE_KEYS.PROXIES_SLIM, json, DEFAULT_TTL);
		} catch (err) {
			if (isMounted.current && !background) {
				setSlimError(err instanceof Error ? err.message : "Unknown error");
			}
		} finally {
			if (isMounted.current && !background) {
				setSlimLoading(false);
				setSlimProgress(undefined);
			}
		}
	}, []);

	const loadSlim = useCallback(
		async (options?: FetchOptions) => {
			const forceRefresh = options?.force ?? false;
			const background = options?.background ?? false;

			if (!forceRefresh) {
				const cached = getCache<SlimProxyData>(CACHE_KEYS.PROXIES_SLIM);
				if (cached) {
					setSlimData(cached);
					setSlimLoading(false);
					setSlimProgress(undefined);
					void fetchSlimFromNetwork({ force: true, background: true });
					return;
				}
			}

			await fetchSlimFromNetwork({ force: forceRefresh, background });
		},
		[fetchSlimFromNetwork],
	);

	const fetchRichFromNetwork = useCallback(async (options: FetchOptions) => {
		const forceRefresh = options.force ?? false;
		const background = options.background ?? false;

		if (!background) {
			setRichLoading(true);
			setRichProgress(0);
		}

		try {
			const cacheBuster = forceRefresh ? `?v=${Date.now()}` : "";
			const json = await fetchJsonWithProgress<RichProxyData>(
				`${BASE_URL}proxies-rich.json${cacheBuster}`,
				background
					? undefined
					: (percent) => {
							if (isMounted.current) setRichProgress(percent);
						},
			);

			if (isMounted.current) {
				setRichData(json);
				setRichError(null);
			}
			await setLargeCache(CACHE_KEYS.PROXIES_RICH, json, DEFAULT_TTL);
		} catch (err) {
			if (isMounted.current && !background) {
				setRichError(err instanceof Error ? err.message : "Unknown error");
			}
		} finally {
			if (isMounted.current && !background) {
				setRichLoading(false);
				setRichProgress(undefined);
			}
		}
	}, []);

	const loadRich = useCallback(
		async (options?: FetchOptions) => {
			const forceRefresh = options?.force ?? false;
			const background = options?.background ?? false;

			if (!forceRefresh) {
				const cached =
					(await getLargeCache<RichProxyData>(CACHE_KEYS.PROXIES_RICH)) ??
					getCache<RichProxyData>(CACHE_KEYS.PROXIES);
				if (cached) {
					setRichData(cached);
					setRichLoading(false);
					setRichProgress(undefined);
					void fetchRichFromNetwork({ force: true, background: true });
					return;
				}
			}

			await fetchRichFromNetwork({ force: forceRefresh, background });
		},
		[fetchRichFromNetwork],
	);

	useEffect(() => {
		void loadStats();
	}, [loadStats]);

	useEffect(() => {
		if (!shouldFetchRich) {
			void loadSlim();
		}
	}, [shouldFetchRich, loadSlim]);

	useEffect(() => {
		if (shouldFetchRich) {
			void loadRich();
		}
	}, [shouldFetchRich, loadRich]);

	const value = useMemo<ProxyDataContextValue>(
		() => ({
			stats,
			statsLoading,
			statsError,
			refreshStats: () => void loadStats({ force: true }),

			slimData,
			slimLoading,
			slimError,
			slimProgress,
			refreshSlim: () => void loadSlim({ force: true }),

			richData,
			richLoading,
			richError,
			richProgress,
			refreshRich: () => void loadRich({ force: true }),
		}),
		[
			stats,
			statsLoading,
			statsError,
			loadStats,
			slimData,
			slimLoading,
			slimError,
			slimProgress,
			loadSlim,
			richData,
			richLoading,
			richError,
			richProgress,
			loadRich,
		],
	);

	return (
		<ProxyDataContext.Provider value={value}>
			{children}
		</ProxyDataContext.Provider>
	);
}

export function useProxyData(): ProxyDataContextValue {
	const context = useContext(ProxyDataContext);
	if (!context) {
		throw new Error("useProxyData must be used within ProxyDataProvider");
	}
	return context;
}