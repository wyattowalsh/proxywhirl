import { generateFiles } from "fumadocs-openapi";
import { createOpenAPI } from "fumadocs-openapi/server";
import { readdir, readFile, rename, rm, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const webRoot = join(__dirname, "..");
const outputDir = join(webRoot, "content", "docs", "api", "openapi");

const openapi = createOpenAPI({
	input: ["./content/generated/openapi.json"],
});

await generateFiles({
	input: openapi,
	output: outputDir,
	per: "operation",
	groupBy: "tag",
	includeDescription: true,
	meta: true,
});

/**
 * Normalize OpenAPI group/operation slugs for URL-safe Fumadocs paths.
 * fumadocs-openapi can emit tags like "Retry & Failover" → "retry-&-failover".
 */
function sanitizeSlug(slug) {
	return String(slug)
		.trim()
		.replace(/&/g, "and")
		.replace(/[^a-zA-Z0-9._-]+/g, "-")
		.replace(/-+/g, "-")
		.replace(/^-|-$/g, "")
		.toLowerCase();
}

function titleFromSlug(slug) {
	return sanitizeSlug(slug)
		.split(/[-_]+/)
		.filter(Boolean)
		.map((part) => part.charAt(0).toUpperCase() + part.slice(1))
		.join(" ");
}

async function readJson(path) {
	return JSON.parse(await readFile(path, "utf8"));
}

async function writeJson(path, value) {
	await writeFile(path, `${JSON.stringify(value, null, 2)}\n`);
}

async function sanitizeOpenApiDirs() {
	const entries = await readdir(outputDir, { withFileTypes: true });
	const renames = [];

	for (const entry of entries) {
		if (!entry.isDirectory()) continue;
		const safe = sanitizeSlug(entry.name);
		if (safe !== entry.name) {
			renames.push({ from: entry.name, to: safe });
		}
	}

	for (const { from, to } of renames) {
		const fromPath = join(outputDir, from);
		const toPath = join(outputDir, to);
		// Prior runs leave the sanitized dir; replace it with freshly generated content.
		await rm(toPath, { recursive: true, force: true });
		await rename(fromPath, toPath);
	}

	const metaPath = join(outputDir, "meta.json");
	try {
		const meta = await readJson(metaPath);
		if (Array.isArray(meta.pages)) {
			meta.pages = meta.pages.map((page) =>
				page === "index" || page.startsWith("---") ? page : sanitizeSlug(page),
			);
			await writeJson(metaPath, meta);
		}
	} catch {
		// meta.json may not exist yet
	}

	return renames;
}

await sanitizeOpenApiDirs();

const metaPath = join(outputDir, "meta.json");
const meta = await readJson(metaPath);
if (Array.isArray(meta.pages) && !meta.pages.includes("index")) {
	meta.pages = ["index", ...meta.pages];
	await writeJson(metaPath, meta);
}

const groupEntries = await readdir(outputDir, { withFileTypes: true });
const groups = [];

for (const entry of groupEntries) {
	if (!entry.isDirectory()) continue;

	const groupSlug = entry.name;
	const groupDir = join(outputDir, groupSlug);
	const groupMetaPath = join(groupDir, "meta.json");
	let groupMeta;
	try {
		groupMeta = await readJson(groupMetaPath);
	} catch {
		continue;
	}

	const title = groupMeta.title || titleFromSlug(groupSlug);
	const description = groupMeta.description || "Generated OpenAPI operation pages.";
	const pages = Array.isArray(groupMeta.pages) ? groupMeta.pages : [];
	const sanitizedPages = pages.map((page) =>
		page === "index" ? page : sanitizeSlug(page),
	);
	if (!sanitizedPages.includes("index")) {
		groupMeta.pages = ["index", ...sanitizedPages];
	} else {
		groupMeta.pages = sanitizedPages;
	}
	await writeJson(groupMetaPath, groupMeta);

	const operationLinks = groupMeta.pages
		.filter((page) => page !== "index")
		.map((page) => `- [${titleFromSlug(page)}](/docs/api/openapi/${groupSlug}/${page})`)
		.join("\n");

	await writeFile(
		join(groupDir, "index.mdx"),
		`---\ntitle: ${title}\ndescription: ${description}\n---\n\n${description}\n\n${operationLinks}\n`,
	);

	groups.push({ slug: groupSlug, title, description });
}

groups.sort((a, b) => a.title.localeCompare(b.title));

const groupRows = groups
	.map((group) => `| [${group.title}](/docs/api/openapi/${group.slug}) | ${group.description} |`)
	.join("\n");

await writeFile(
	join(outputDir, "index.mdx"),
	`---\ntitle: OpenAPI Endpoints\ndescription: Per-endpoint FastAPI reference pages grouped by operation area.\n---\n\nThe OpenAPI endpoint pages are generated from \`proxywhirl.api.app.openapi()\` and grouped by operational area.\n\n| Group | Covers |\n| ----- | ------ |\n${groupRows}\n\nFor a compact route inventory, see the [REST/OpenAPI Reference](/docs/generated/rest-api).\n`,
);
