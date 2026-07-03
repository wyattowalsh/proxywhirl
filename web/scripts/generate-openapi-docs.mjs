import { generateFiles } from "fumadocs-openapi";
import { createOpenAPI } from "fumadocs-openapi/server";
import { readdir, readFile, writeFile } from "node:fs/promises";
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

function titleFromSlug(slug) {
	return slug
		.split(/[-_]+/)
		.filter(Boolean)
		.map((part) => part.charAt(0).toUpperCase() + part.slice(1))
		.join(" ")
		.replace("&", "&");
}

async function readJson(path) {
	return JSON.parse(await readFile(path, "utf8"));
}

async function writeJson(path, value) {
	await writeFile(path, `${JSON.stringify(value, null, 2)}\n`);
}

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
	if (!pages.includes("index")) {
		groupMeta.pages = ["index", ...pages];
		await writeJson(groupMetaPath, groupMeta);
	}

	const operationLinks = pages
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
