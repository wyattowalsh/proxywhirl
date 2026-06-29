import type { MetadataRoute } from "next";

import { baseUrl } from "@/lib/metadata";
import { source } from "@/lib/source";

export default function sitemap(): MetadataRoute.Sitemap {
	const now = new Date();

	return [
		{
			url: baseUrl,
			lastModified: now,
		},
		{
			url: `${baseUrl}/analytics`,
			lastModified: now,
		},
		{
			url: `${baseUrl}/llms.txt`,
			lastModified: now,
		},
		...source.getPages().map((page) => ({
			url: `${baseUrl}${page.url}`,
			lastModified: now,
		})),
	];
}