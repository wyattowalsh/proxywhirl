import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import {
	ProxyDataProvider,
	useProxyData,
} from "@/providers/ProxyDataProvider";
import { CACHE_KEYS } from "@/lib/cache";
import type { RichProxyData, Stats } from "@/types";

const mockPathname = vi.fn(() => "/");

vi.mock("next/navigation", () => ({
	usePathname: () => mockPathname(),
}));

const mockFetchJsonWithProgress = vi.fn();
vi.mock("@/lib/proxy-fetch", async (importOriginal) => {
	const original =
		await importOriginal<typeof import("@/lib/proxy-fetch")>();
	return {
		...original,
		fetchJsonWithProgress: (...args: unknown[]) =>
			mockFetchJsonWithProgress(...args),
	};
	it("serves cached rich data from IndexedDB immediately on analytics route", async () => {
		mockPathname.mockReturnValue("/analytics");
		mockGetLargeCache.mockResolvedValue(mockRich);

		render(
			<ProxyDataProvider>
				<DataProbe />
			</ProxyDataProvider>,
		);

		await waitFor(() => {
			expect(screen.getByTestId("rich-count")).toHaveTextContent("1");
			expect(screen.getByTestId("rich-loading")).toHaveTextContent("false");
		});

		await waitFor(() => {
			const richCalls = mockFetchJsonWithProgress.mock.calls.filter(([url]) =>
				String(url).includes("proxies-rich"),
			);
			expect(richCalls.length).toBeGreaterThan(0);
		});
	});

	it("falls back to legacy session cache for rich data", async () => {
		mockPathname.mockReturnValue("/analytics");
		mockGetLargeCache.mockResolvedValue(null);
		mockGetCache.mockImplementation((key: string) => {
			if (key === CACHE_KEYS.PROXIES) {
				return mockRich;
			}
			return null;
		});

		render(
			<ProxyDataProvider>
				<DataProbe />
			</ProxyDataProvider>,
		);

		await waitFor(() => {
			expect(screen.getByTestId("rich-count")).toHaveTextContent("1");
		});
	});

	it("surfaces rich fetch errors on analytics route", async () => {
		mockPathname.mockReturnValue("/analytics");
		mockFetchJsonWithProgress.mockRejectedValue(new Error("Rich fetch failed"));

		render(
			<ProxyDataProvider>
				<DataProbe />
			</ProxyDataProvider>,
		);

		await waitFor(() => {
			expect(screen.getByTestId("rich-error")).toHaveTextContent("Rich fetch failed");
			expect(screen.getByTestId("rich-count")).toHaveTextContent("0");
		});
	});

});

const mockGetCache = vi.fn();
const mockSetCache = vi.fn();
const mockGetLargeCache = vi.fn();
const mockSetLargeCache = vi.fn();

vi.mock("@/lib/cache", async (importOriginal) => {
	const original = await importOriginal<typeof import("@/lib/cache")>();
	return {
		...original,
		getCache: (...args: unknown[]) => mockGetCache(...args),
		setCache: (...args: unknown[]) => mockSetCache(...args),
		getLargeCache: (...args: unknown[]) => mockGetLargeCache(...args),
		setLargeCache: (...args: unknown[]) => mockSetLargeCache(...args),
	};
	it("serves cached rich data from IndexedDB immediately on analytics route", async () => {
		mockPathname.mockReturnValue("/analytics");
		mockGetLargeCache.mockResolvedValue(mockRich);

		render(
			<ProxyDataProvider>
				<DataProbe />
			</ProxyDataProvider>,
		);

		await waitFor(() => {
			expect(screen.getByTestId("rich-count")).toHaveTextContent("1");
			expect(screen.getByTestId("rich-loading")).toHaveTextContent("false");
		});

		await waitFor(() => {
			const richCalls = mockFetchJsonWithProgress.mock.calls.filter(([url]) =>
				String(url).includes("proxies-rich"),
			);
			expect(richCalls.length).toBeGreaterThan(0);
		});
	});

	it("falls back to legacy session cache for rich data", async () => {
		mockPathname.mockReturnValue("/analytics");
		mockGetLargeCache.mockResolvedValue(null);
		mockGetCache.mockImplementation((key: string) => {
			if (key === CACHE_KEYS.PROXIES) {
				return mockRich;
			}
			return null;
		});

		render(
			<ProxyDataProvider>
				<DataProbe />
			</ProxyDataProvider>,
		);

		await waitFor(() => {
			expect(screen.getByTestId("rich-count")).toHaveTextContent("1");
		});
	});

	it("surfaces rich fetch errors on analytics route", async () => {
		mockPathname.mockReturnValue("/analytics");
		mockFetchJsonWithProgress.mockRejectedValue(new Error("Rich fetch failed"));

		render(
			<ProxyDataProvider>
				<DataProbe />
			</ProxyDataProvider>,
		);

		await waitFor(() => {
			expect(screen.getByTestId("rich-error")).toHaveTextContent("Rich fetch failed");
			expect(screen.getByTestId("rich-count")).toHaveTextContent("0");
		});
	});

});

const mockStats: Stats = {
	generated_at: "2026-01-01T00:00:00Z",
	sources: { total: 2 },
	proxies: { total: 42, unique: 42, by_protocol: { http: 42 } },
	file_sizes: {},
	health: { healthy: 42, unhealthy: 0, dead: 0, unknown: 0 },
	performance: {
		avg_response_ms: 100,
		median_response_ms: 100,
		p95_response_ms: 200,
		min_response_ms: 50,
		max_response_ms: 300,
		samples: 42,
	},
	validation: { total_validated: 42, success_rate_pct: 100 },
	geographic: { total_countries: 5, top_countries: [], by_continent: {} },
	sources_ranking: { total_active: 2, top_sources: [] },
};

const mockSlimRaw = {
	metadata: { generated_at: "2026-01-01T00:00:00Z" },
	proxies: { http: ["192.168.1.1:8080"] },
};

const mockRich: RichProxyData = {
	generated_at: "2026-01-01T00:00:00Z",
	total: 1,
	proxies: [
		{
			ip: "192.168.1.1",
			port: 8080,
			protocol: "http",
			status: "healthy",
			response_time: 100,
			success_rate: 95,
			total_checks: 10,
			source: "test",
			last_checked: null,
			created_at: "2026-01-01T00:00:00Z",
		},
	],
};

function DataProbe() {
	const {
		stats,
		statsLoading,
		statsError,
		slimData,
		slimLoading,
		richData,
		richLoading,
		richError,
	} = useProxyData();

	return (
		<div>
			<span data-testid="stats-loading">{String(statsLoading)}</span>
			<span data-testid="stats-total">{stats?.proxies?.total ?? "none"}</span>
			<span data-testid="stats-error">{statsError ?? ""}</span>
			<span data-testid="slim-loading">{String(slimLoading)}</span>
			<span data-testid="slim-count">{slimData?.proxies?.length ?? 0}</span>
			<span data-testid="rich-loading">{String(richLoading)}</span>
			<span data-testid="rich-count">{richData?.proxies?.length ?? 0}</span>
			<span data-testid="rich-error">{richError ?? ""}</span>
		</div>
	);
}

describe("ProxyDataProvider", () => {
	beforeEach(() => {
		vi.clearAllMocks();
		mockPathname.mockReturnValue("/");
		mockGetCache.mockReturnValue(null);
		mockGetLargeCache.mockResolvedValue(null);
		mockSetLargeCache.mockResolvedValue(undefined);

		global.fetch = vi.fn().mockResolvedValue({
			ok: true,
			json: async () => mockStats,
		}) as typeof fetch;

		mockFetchJsonWithProgress.mockImplementation(async (url: string) => {
			if (url.includes("proxies-rich")) {
				return mockRich;
			}
			return mockSlimRaw;
		});
	});

	it("throws when useProxyData is used outside provider", () => {
		expect(() => render(<DataProbe />)).toThrow(
			/useProxyData must be used within ProxyDataProvider/,
		);
	});

	it("loads stats and slim on home route", async () => {
		render(
			<ProxyDataProvider>
				<DataProbe />
			</ProxyDataProvider>,
		);

		await waitFor(() => {
			expect(screen.getByTestId("stats-total")).toHaveTextContent("42");
		});
		await waitFor(() => {
			expect(screen.getByTestId("slim-count")).toHaveTextContent("1");
		});

		const slimCalls = mockFetchJsonWithProgress.mock.calls.filter(([url]) =>
			String(url).includes("proxies.json"),
		);
		const richCalls = mockFetchJsonWithProgress.mock.calls.filter(([url]) =>
			String(url).includes("proxies-rich"),
		);
		expect(slimCalls.length).toBeGreaterThan(0);
		expect(richCalls).toHaveLength(0);
	});

	it("loads stats and rich on analytics route and skips slim", async () => {
		mockPathname.mockReturnValue("/analytics");

		render(
			<ProxyDataProvider>
				<DataProbe />
			</ProxyDataProvider>,
		);

		await waitFor(() => {
			expect(screen.getByTestId("rich-count")).toHaveTextContent("1");
		});

		const slimCalls = mockFetchJsonWithProgress.mock.calls.filter(([url]) =>
			String(url).includes("proxies.json"),
		);
		const richCalls = mockFetchJsonWithProgress.mock.calls.filter(([url]) =>
			String(url).includes("proxies-rich"),
		);
		expect(slimCalls).toHaveLength(0);
		expect(richCalls.length).toBeGreaterThan(0);
	});

	it("serves cached stats immediately", async () => {
		mockGetCache.mockImplementation((key: string) => {
			if (key === CACHE_KEYS.STATS) {
				return mockStats;
			}
			return null;
		});

		render(
			<ProxyDataProvider>
				<DataProbe />
			</ProxyDataProvider>,
		);

		await waitFor(() => {
			expect(screen.getByTestId("stats-total")).toHaveTextContent("42");
			expect(screen.getByTestId("stats-loading")).toHaveTextContent("false");
		});
	});

	it("surfaces fetch errors for stats", async () => {
		global.fetch = vi.fn().mockResolvedValue({
			ok: false,
		}) as typeof fetch;

		render(
			<ProxyDataProvider>
				<DataProbe />
			</ProxyDataProvider>,
		);

		await waitFor(() => {
			expect(screen.getByTestId("stats-error")).toHaveTextContent(
				"Failed to fetch stats",
			);
		});
	});

	it("serves cached rich data from IndexedDB immediately on analytics route", async () => {
		mockPathname.mockReturnValue("/analytics");
		mockGetLargeCache.mockResolvedValue(mockRich);

		render(
			<ProxyDataProvider>
				<DataProbe />
			</ProxyDataProvider>,
		);

		await waitFor(() => {
			expect(screen.getByTestId("rich-count")).toHaveTextContent("1");
			expect(screen.getByTestId("rich-loading")).toHaveTextContent("false");
		});

		await waitFor(() => {
			const richCalls = mockFetchJsonWithProgress.mock.calls.filter(([url]) =>
				String(url).includes("proxies-rich"),
			);
			expect(richCalls.length).toBeGreaterThan(0);
		});
	});

	it("falls back to legacy session cache for rich data", async () => {
		mockPathname.mockReturnValue("/analytics");
		mockGetLargeCache.mockResolvedValue(null);
		mockGetCache.mockImplementation((key: string) => {
			if (key === CACHE_KEYS.PROXIES) {
				return mockRich;
			}
			return null;
		});

		render(
			<ProxyDataProvider>
				<DataProbe />
			</ProxyDataProvider>,
		);

		await waitFor(() => {
			expect(screen.getByTestId("rich-count")).toHaveTextContent("1");
		});
	});

	it("surfaces rich fetch errors on analytics route", async () => {
		mockPathname.mockReturnValue("/analytics");
		mockFetchJsonWithProgress.mockRejectedValue(new Error("Rich fetch failed"));

		render(
			<ProxyDataProvider>
				<DataProbe />
			</ProxyDataProvider>,
		);

		await waitFor(() => {
			expect(screen.getByTestId("rich-error")).toHaveTextContent("Rich fetch failed");
			expect(screen.getByTestId("rich-count")).toHaveTextContent("0");
		});
	});

});
