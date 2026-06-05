import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback, useMemo } from "react";
import type { Protocol } from "@/types";
import type { ProxyFilters, SortField, SortDirection } from "./useProxies";

const VALID_PROTOCOLS: Protocol[] = ["http", "socks4", "socks5"];

interface UrlFilterState {
	filters: ProxyFilters;
	sortField: SortField;
	sortDirection: SortDirection;
	setFilters: (filters: ProxyFilters) => void;
	setSort: (field: SortField, direction: SortDirection) => void;
	clearAll: () => void;
}

export function useUrlFilters(): UrlFilterState {
	const router = useRouter();
	const pathname = usePathname() ?? "/";
	const searchParams = useSearchParams();
	const currentSearchParams = useMemo(
		() => new URLSearchParams(searchParams?.toString() ?? ""),
		[searchParams],
	);

	const replaceSearchParams = useCallback(
		(params: URLSearchParams) => {
			const query = params.toString();
			router.replace(query ? `${pathname}?${query}` : pathname, {
				scroll: false,
			});
		},
		[pathname, router],
	);

	const filters = useMemo<ProxyFilters>(() => {
		const q = currentSearchParams.get("q") || "";
		const protocolsParam =
			currentSearchParams.get("protocols")?.split(",") || [];
		const protocols = protocolsParam.filter((p): p is Protocol =>
			VALID_PROTOCOLS.includes(p as Protocol),
		);
		const countries =
			currentSearchParams.get("countries")?.split(",").filter(Boolean) || [];

		return {
			search: q,
			protocols,
			statuses: [],
			countries,
		};
	}, [currentSearchParams]);

	const sortField = useMemo<SortField>(() => {
		const sort = currentSearchParams.get("sort");
		if (
			sort &&
			[
				"ip",
				"port",
				"protocol",
				"status",
				"response_time",
				"source",
				"created_at",
			].includes(sort)
		) {
			return sort as SortField;
		}
		return "response_time";
	}, [currentSearchParams]);

	const sortDirection = useMemo<SortDirection>(() => {
		const dir = currentSearchParams.get("dir");
		return dir === "desc" ? "desc" : "asc";
	}, [currentSearchParams]);

	const setFilters = useCallback(
		(newFilters: ProxyFilters) => {
			const params = new URLSearchParams(currentSearchParams);

			// Search
			if (newFilters.search) {
				params.set("q", newFilters.search);
			} else {
				params.delete("q");
			}

			// Protocols
			if (newFilters.protocols.length > 0) {
				params.set("protocols", newFilters.protocols.join(","));
			} else {
				params.delete("protocols");
			}

			// Countries
			if (newFilters.countries.length > 0) {
				params.set("countries", newFilters.countries.join(","));
			} else {
				params.delete("countries");
			}

			replaceSearchParams(params);
		},
		[replaceSearchParams, currentSearchParams],
	);

	const setSort = useCallback(
		(field: SortField, direction: SortDirection) => {
			const params = new URLSearchParams(currentSearchParams);

			if (field !== "response_time") {
				params.set("sort", field);
			} else {
				params.delete("sort");
			}

			if (direction !== "asc") {
				params.set("dir", direction);
			} else {
				params.delete("dir");
			}

			replaceSearchParams(params);
		},
		[replaceSearchParams, currentSearchParams],
	);

	const clearAll = useCallback(() => {
		replaceSearchParams(new URLSearchParams());
	}, [replaceSearchParams]);

	return {
		filters,
		sortField,
		sortDirection,
		setFilters,
		setSort,
		clearAll,
	};
}
