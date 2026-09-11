import { execFileSync } from "node:child_process"
import { readFileSync, readdirSync } from "node:fs"
import { dirname, join } from "node:path"
import { fileURLToPath } from "node:url"

import { describe, expect, it } from "vitest"

const scriptDir = dirname(fileURLToPath(import.meta.url))
const webRoot = join(scriptDir, "..")
const repoRoot = join(webRoot, "..")
const generatedDocsDir = join(webRoot, "content", "docs", "generated")
const openApiDocsDir = join(webRoot, "content", "docs", "api", "openapi")
const openApiDocument = "./content/generated/openapi.json"
const llmsIndex = join(webRoot, "public", "llms.txt")

function read(path) {
  return readFileSync(path, "utf8")
}

function filesUnder(root, extension) {
  return readdirSync(root, { recursive: true, withFileTypes: true })
    .filter((entry) => entry.isFile() && entry.name.endsWith(extension))
    .map((entry) => join(entry.parentPath, entry.name))
    .sort()
}

function publicRegistry() {
  const script = String.raw`
import json
from proxywhirl.strategies import BUILTIN_STRATEGY_CLASSES

items = []
seen = set()
for name, strategy_class in BUILTIN_STRATEGY_CLASSES.items():
    if strategy_class in seen:
        continue
    seen.add(strategy_class)
    aliases = [
        alias
        for alias, registered_class in BUILTIN_STRATEGY_CLASSES.items()
        if registered_class is strategy_class
    ]
    items.append({"name": name, "class": strategy_class.__name__, "aliases": aliases})

print(json.dumps(items))
`
  return JSON.parse(
    execFileSync("uv", ["run", "python", "-c", script], {
      cwd: repoRoot,
      encoding: "utf8",
      env: { ...process.env, PYTHONWARNINGS: "ignore" },
    }),
  )
}

describe("generated documentation contracts", () => {
  it("derives the strategy reference from every unique public registry class", () => {
    const registry = publicRegistry()
    const reference = read(join(generatedDocsDir, "strategies.mdx"))

    expect(registry).not.toHaveLength(0)
    expect(reference).toContain(
      `<div className="text-2xl font-semibold tracking-tight">${registry.length}</div>`,
    )
    for (const item of registry) {
      expect(reference).toContain(`\`${item.name}\``)
      expect(reference).toContain(`\`${item.class}\``)
      for (const alias of item.aliases) expect(reference).toContain(alias)
    }
  })

  it("keeps generated metadata free of wall-clock timestamps", () => {
    const generator = read(join(scriptDir, "generate-docs.mjs"))
    const llmsGenerator = read(join(scriptDir, "generate-llms.mjs"))
    const generatedPages = filesUnder(generatedDocsDir, ".mdx")
    const openApiPages = filesUnder(openApiDocsDir, ".mdx")

    expect(generator).not.toMatch(/\bnew\s+Date\s*\(|\bDate\.now\s*\(|datetime\.now\s*\(|utcnow\s*\(/)
    expect(llmsGenerator).not.toMatch(
      /\bnew\s+Date\s*\(|\bDate\.now\s*\(|datetime\.now\s*\(|utcnow\s*\(/,
    )
    expect(read(llmsIndex)).not.toMatch(/^Generated:\s/m)
    for (const path of [...generatedPages, ...openApiPages]) {
      expect(read(path)).not.toMatch(/^generated(?:_|-|)at\s*:/im)
    }
  })

  it("includes the Fumadocs v11 preload document on every OpenAPI operation page", () => {
    const operationPages = filesUnder(openApiDocsDir, ".mdx").filter(
      (path) => !path.endsWith("/index.mdx"),
    )

    expect(operationPages).not.toHaveLength(0)
    for (const path of operationPages) {
      const page = read(path)
      expect(page).toMatch(/^_openapi:\s*$/m)
      expect(page).toMatch(/^\s+preload:\s*$/m)
      expect(page).toContain(`- ${openApiDocument}`)
    }
  })

  it("keeps OpenAPI navigation metadata aligned with generated groups", () => {
    const meta = JSON.parse(read(join(openApiDocsDir, "meta.json")))
    const groups = readdirSync(openApiDocsDir, { withFileTypes: true })
      .filter((entry) => entry.isDirectory())
      .map((entry) => entry.name)
      .sort()

    expect(meta.pages.filter((page) => page !== "index").sort()).toEqual(groups)
    expect(groups.every((group) => /^[a-z0-9._-]+$/.test(group))).toBe(true)
  })
})
