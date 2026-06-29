import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const webRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const docsRoot = join(webRoot, "content", "docs");
const baseUrl = process.env.PROXYWHIRL_SITE_URL ?? "https://www.proxywhirl.com";
const generatedAt = new Date().toISOString();

const PAGE_TITLE_OVERRIDES = {
	"../api/openapi": "OpenAPI Endpoints",
};

const ACRONYMS = {
	api: "API",
	cli: "CLI",
	rest: "REST",
	mcp: "MCP",
	http: "HTTP",
	socks4: "SOCKS4",
	socks5: "SOCKS5",
};

function readMeta(metaDir) {
	const metaPath = join(metaDir, "meta.json");
	if (!existsSync(metaPath)) {
		return { title: "", pages: [] };
	}
	return JSON.parse(readFileSync(metaPath, "utf8"));
}

function isSeparator(page) {
	return typeof page === "string" && page.startsWith("---");
}

function pageToUrl(page, metaDir) {
	if (page === "index") {
		const rel = metaDir.replace(docsRoot, "").replace(/^\//, "");
		return rel ? `${baseUrl}/docs/${rel}` : `${baseUrl}/docs`;
	}
	if (page.startsWith("../")) {
		const normalized = page.replace(/^\.\.\//, "");
		return `${baseUrl}/docs/${normalized}`;
	}
	const rel = metaDir.replace(docsRoot, "").replace(/^\//, "");
	const prefix = rel ? `${rel}/` : "";
	return `${baseUrl}/docs/${prefix}${page}`;
}

function pageToMdxPath(metaDir, page) {
	if (page === "index") {
		return join(metaDir, "index.mdx");
	}
	if (page.startsWith("../")) {
		const rel = page.replace(/^\.\.\//, "");
		const indexCandidate = join(docsRoot, rel, "index.mdx");
		if (existsSync(indexCandidate)) {
			return indexCandidate;
		}
		return join(docsRoot, `${rel}.mdx`);
	}
	return join(metaDir, `${page}.mdx`);
}

function readFrontmatterTitle(mdxPath) {
	if (!existsSync(mdxPath)) {
		return null;
	}
	const raw = readFileSync(mdxPath, "utf8");
	const match = raw.match(/^---\s*\n([\s\S]*?)\n---/);
	if (!match) {
		return null;
	}
	const titleLine = match[1].match(/^title:\s*(.+)$/m);
	if (!titleLine) {
		return null;
	}
	return titleLine[1].trim().replace(/^["']|["']$/g, "");
}

function titleCaseSlug(slug) {
	return slug
		.split("-")
		.map((part) => ACRONYMS[part.toLowerCase()] ?? part.charAt(0).toUpperCase() + part.slice(1))
		.join(" ");
}

function sectionTitle(page) {
	const sectionMeta = readMeta(join(docsRoot, page));
	return sectionMeta.title || titleCaseSlug(page);
}

function formatTitle(page, metaTitle, metaDir) {
	if (PAGE_TITLE_OVERRIDES[page]) {
		return PAGE_TITLE_OVERRIDES[page];
	}

	const mdxTitle = readFrontmatterTitle(pageToMdxPath(metaDir, page));
	if (mdxTitle) {
		return mdxTitle;
	}

	if (page === "index") {
		return metaTitle || "Home";
	}

	return titleCaseSlug(page);
}

function linksFromMeta(metaDir, { skipIndex = false, filter } = {}) {
	const meta = readMeta(metaDir);
	return meta.pages
		.filter((page) => !isSeparator(page))
		.filter((page) => !(skipIndex && page === "index"))
		.filter((page) => (filter ? filter(page) : true))
		.map((page) => {
			const title =
				metaDir === docsRoot &&
				page !== "index" &&
				page !== "quickstart" &&
				!page.startsWith("../")
					? sectionTitle(page)
					: formatTitle(page, meta.title, metaDir);
			return `- [${title}](${pageToUrl(page, metaDir)})`;
		});
}

const startHere = linksFromMeta(docsRoot, {
	filter: (page) => page === "index" || page === "quickstart" || !page.includes("/"),
});

const keyGuides = linksFromMeta(join(docsRoot, "guides"), { skipIndex: true });

const generatedReference = linksFromMeta(join(docsRoot, "reference"), {
	skipIndex: true,
	filter: (page) => page.startsWith("../generated/") || page === "../api/openapi",
});

const content = `# ProxyWhirl

> Production-grade Python proxy rotation library with live proxy lists, REST API, MCP server, and canonical Fumadocs documentation.

Generated: ${generatedAt}

## Start Here

${startHere.join("\n")}

## Generated Reference

${generatedReference.join("\n")}

## Key Guides

${keyGuides.join("\n")}

## Live Assets

- [HTTP proxy list](${baseUrl}/proxy-lists/http.txt)
- [All proxies](${baseUrl}/proxy-lists/all.txt)
- [Rich JSON export](${baseUrl}/proxy-lists/proxies-rich.json)

## Repository

- [GitHub](https://github.com/wyattowalsh/proxywhirl)
- [AGENTS.md](https://github.com/wyattowalsh/proxywhirl/blob/main/AGENTS.md)
`;

writeFileSync(join(webRoot, "public", "llms.txt"), content);
console.log("Wrote public/llms.txt");
