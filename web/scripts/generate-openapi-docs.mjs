import { generateFiles } from "fumadocs-openapi";
import { createOpenAPI } from "fumadocs-openapi/server";
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