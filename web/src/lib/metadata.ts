import type { Metadata } from "next";

import { GITHUB_URL } from "@/lib/site-nav";

export const baseUrl =
	process.env.NEXT_PUBLIC_SITE_URL ?? "https://www.proxywhirl.com";

export const siteConfig = {
	name: "ProxyWhirl",
	title: "ProxyWhirl",
	tagline: "Python Proxy Rotation Library",
	description:
		"Production-grade proxy rotation for Python with live proxy lists and canonical docs.",
	githubUrl: GITHUB_URL,
} as const;

export const defaultMetadata: Metadata = {
	metadataBase: new URL(baseUrl),
	title: {
		default: siteConfig.title,
		template: `%s | ${siteConfig.title}`,
	},
	description: siteConfig.description,
	openGraph: {
		type: "website",
		locale: "en_US",
		url: baseUrl,
		siteName: siteConfig.name,
		title: `${siteConfig.name} — ${siteConfig.tagline}`,
		description: siteConfig.description,
	},
	twitter: {
		card: "summary_large_image",
		title: `${siteConfig.name} — ${siteConfig.tagline}`,
		description: siteConfig.description,
	},
	icons: {
		icon: [{ url: "/favicon.svg", type: "image/svg+xml" }],
		shortcut: ["/favicon.svg"],
	},
};

export function createPageMetadata({
	title,
	description = siteConfig.description,
	path = "",
}: {
	title: string;
	description?: string;
	path?: string;
}): Metadata {
	const url = `${baseUrl}${path}`;

	return {
		title,
		description,
		openGraph: {
			title,
			description,
			url,
			type: "website",
			siteName: siteConfig.name,
		},
		twitter: {
			card: "summary_large_image",
			title,
			description,
		},
	};
}