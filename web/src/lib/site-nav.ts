import type { BaseLayoutProps } from "fumadocs-ui/layouts/shared";

export const GITHUB_URL = "https://github.com/wyattowalsh/proxywhirl";

export type SiteNavLink = {
	label: string;
	href: string;
	external?: boolean;
};

export const siteNavLinks: SiteNavLink[] = [
	{ label: "Home", href: "/" },
	{ label: "Docs", href: "/docs/" },
	{ label: "Analytics", href: "/analytics" },
	{ label: "GitHub", href: GITHUB_URL, external: true },
];

export const docsLayoutLinks: NonNullable<BaseLayoutProps["links"]> =
	siteNavLinks.map(({ label, href, external }) => ({
		text: label,
		url: href,
		...(external ? { external: true } : {}),
	}));

export const proxyListLinks = [
	{ label: "HTTP", href: "/proxy-lists/http.txt" },
	{ label: "All proxies", href: "/proxy-lists/all.txt" },
	{ label: "Rich JSON", href: "/proxy-lists/proxies-rich.json" },
	{ label: "Metadata", href: "/proxy-lists/metadata.json" },
] as const;