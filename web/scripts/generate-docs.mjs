import { execFileSync } from "node:child_process"
import { copyFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs"
import { dirname, join } from "node:path"
import { fileURLToPath } from "node:url"

const __dirname = dirname(fileURLToPath(import.meta.url))
const webRoot = join(__dirname, "..")
const repoRoot = join(webRoot, "..")
const generatedDocsDir = join(webRoot, "content", "docs", "generated")
const generatedDataDir = join(webRoot, "content", "generated")
const publicProxyDir = join(webRoot, "public", "proxy-lists")
const publicOgImageSvg = join(webRoot, "public", "og-image.svg")
const publicOgImagePng = join(webRoot, "public", "og-image.png")
const socialPreviewSvg = join(repoRoot, "docs", "assets", "social-preview.svg")

function runPython(script) {
  const output = execFileSync("uv", ["run", "python", "-c", script], {
    cwd: repoRoot,
    encoding: "utf8",
    env: { ...process.env, PYTHONWARNINGS: "ignore" },
  })
  return JSON.parse(output)
}

function writeFile(path, content) {
  mkdirSync(dirname(path), { recursive: true })
  writeFileSync(path, content)
}

function frontmatter(title, description) {
  return ["---", `title: ${title}`, `description: ${description}`, "---", ""].join("\n")
}

function jsonFence(value) {
  return ["```json", JSON.stringify(value, null, 2), "```"].join("\n")
}

function table(headers, rows) {
  const header = `| ${headers.join(" | ")} |`
  const separator = `| ${headers.map(() => "---").join(" | ")} |`
  const body = rows.map((row) => {
    return `| ${row.map((cell) => String(cell ?? "-").replaceAll("|", "\\|")).join(" | ")} |`
  })
  return [header, separator, ...body].join("\n")
}

function statGrid(items) {
  const cards = items
    .map(
      ([label, value, note]) => `<div className="rounded-xl border bg-fd-card p-4 shadow-sm">
  <div className="text-2xl font-semibold tracking-tight">${value}</div>
  <div className="mt-1 text-sm font-medium">${label}</div>
  <div className="mt-1 text-xs text-fd-muted-foreground">${note}</div>
</div>`,
    )
    .join("\n")
  return `<div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">\n${cards}\n</div>`
}

function generatedNote(source) {
  return [
    `<div className="rounded-xl border border-fd-border bg-fd-muted/40 p-4 text-sm">`,
    `<strong>Generated reference.</strong> This page is derived from ${source} during <code>pnpm --dir web run docs:generate</code>. Edit <code>web/scripts/generate-docs.mjs</code>, not this MDX file.`,
    `</div>`,
  ].join("\n")
}

function enumValue(value) {
  return String(value ?? "").split(".").pop()?.toLowerCase().replaceAll("_", "-") || "-"
}

function hostLabel(url) {
  try {
    const parsed = new URL(url)
    if (parsed.hostname === "raw.githubusercontent.com") {
      const [, owner, repo] = parsed.pathname.split("/")
      return `${owner}/${repo}`
    }
    if (parsed.hostname === "cdn.jsdelivr.net") {
      const parts = parsed.pathname.split("/")
      const ghIndex = parts.findIndex((part) => part.startsWith("gh"))
      if (ghIndex >= 0 && parts[ghIndex + 1]) return parts[ghIndex + 1]
    }
    return parsed.hostname.replace(/^www\./, "")
  } catch {
    return url
  }
}

function countBy(items, selector) {
  const counts = new Map()
  for (const item of items) {
    const key = selector(item) || "Other"
    counts.set(key, (counts.get(key) ?? 0) + 1)
  }
  return Array.from(counts.entries()).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
}

function commandPath(appName, command) {
  const prefixes = {
    app: "proxywhirl",
    pool_app: "proxywhirl pool",
    config_app: "proxywhirl config",
    sources_app: "proxywhirl sources",
  }
  return `${prefixes[appName] ?? "proxywhirl"} ${command}`.trim()
}

function commandGroup(appName) {
  const groups = {
    app: "Top-level",
    pool_app: "Pool",
    config_app: "Config",
    sources_app: "Sources",
  }
  return groups[appName] ?? "Top-level"
}

function firstSentence(text) {
  const normalized = String(text ?? "").replace(/\s+/g, " ").trim()
  return normalized.match(/.*?[.!?](?:\s|$)/)?.[0]?.trim() || normalized || "-"
}

function extractCommandFlags(lines, functionLine) {
  const flags = new Set()

  for (let scan = functionLine; scan < Math.min(lines.length, functionLine + 200); scan += 1) {
    const line = lines[scan]
    if (line.match(/^\s*\)\s*(?:->[^:]+)?:\s*$/)) break

    for (const match of line.matchAll(/"(--[\w-]+(?:\/--[\w-]+)?|-[a-zA-Z])"/g)) {
      const flag = match[1].split("/")[0]
      if (flag.startsWith("--") || /^-[a-zA-Z]$/.test(flag)) flags.add(flag)
    }
  }

  const sorted = Array.from(flags).sort()
  return sorted.length > 0 ? sorted.join(", ") : "-"
}

function fallbackCommandSummary(path) {
  const summaries = {
    "proxywhirl pool list": "List proxies in the active pool.",
    "proxywhirl pool add": "Add a proxy URL to the pool.",
    "proxywhirl pool remove": "Remove a proxy URL from the pool.",
    "proxywhirl pool test": "Test one proxy against a target URL.",
    "proxywhirl pool stats": "Show active pool statistics.",
    "proxywhirl config init": "Create a local configuration file.",
    "proxywhirl config show": "Print the current configuration.",
    "proxywhirl config get": "Read one configuration value.",
    "proxywhirl config set": "Write one configuration value.",
    "proxywhirl export": "Export validated proxies for files, docs, and dashboards.",
    "proxywhirl fetch": "Fetch and validate proxies from configured sources.",
                    "proxywhirl import-proxies": "Import proxy records into storage.",
    "proxywhirl sources": "List and validate built-in proxy sources.",
    "proxywhirl request": "Make a proxied HTTP request.",
    "proxywhirl health": "Check rotator health.",
    "proxywhirl validate-proxy": "Validate a single proxy URL.",
  }
  return summaries[path] ?? "-"
}

function extractCommands(source) {
  const lines = source.split("\n")
  const commands = []

  for (let index = 0; index < lines.length; index += 1) {
    const decorator = lines[index].match(
      /^\s*@(app|pool_app|config_app|sources_app)\.command\((?:name=)?(?:(['"])(.*?)\2)?\)/,
    )
    if (!decorator) continue

    const appName = decorator[1]
    const explicitName = decorator[3]?.trim()
    let functionName = ""
    let functionLine = -1

    for (let scan = index + 1; scan < Math.min(lines.length, index + 12); scan += 1) {
      const functionMatch = lines[scan].match(/^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\(/)
      if (functionMatch) {
        functionName = functionMatch[1]
        functionLine = scan
        break
      }
    }

    if (!functionName) continue

    const command = explicitName || functionName.replace(/^_/, "").replaceAll("_", "-")
    let summary = "-"
    let docSearchStart = functionLine + 1
    if (!lines[functionLine].trimEnd().endsWith(":")) {
      for (let scan = functionLine + 1; scan < Math.min(lines.length, functionLine + 120); scan += 1) {
        if (lines[scan].match(/^\s*\)\s*(?:->[^:]*)?:\s*$/)) {
          docSearchStart = scan + 1
          break
        }
      }
    }
    for (let scan = docSearchStart; scan < Math.min(lines.length, docSearchStart + 8); scan += 1) {
      if (lines[scan].trim() === "") continue
      const docMatch = lines[scan].match(/^\s+"""(.*)/)
      if (!docMatch) break
      const inline = docMatch[1].replace(/"""\s*$/, "")
      if (inline.trim()) summary = firstSentence(inline)
      else summary = firstSentence(lines[scan + 1]?.replace(/^\s*/, ""))
      break
    }

    const path = commandPath(appName, command)
    if (summary === "-") summary = fallbackCommandSummary(path)
    const flags = extractCommandFlags(lines, functionLine)

    commands.push({
      app: appName,
      group: commandGroup(appName),
      command,
      path,
      function: functionName,
      summary,
      flags,
    })
  }

  const deduped = new Map()
  for (const command of commands) {
    const existing = deduped.get(command.path)
    if (!existing || (existing.summary === "-" && command.summary !== "-")) {
      deduped.set(command.path, command)
    }
  }

  return Array.from(deduped.values())
}

const packageData = runPython(String.raw`
import inspect
import json
import tomllib
from pathlib import Path

import proxywhirl

pyproject = tomllib.loads(Path("pyproject.toml").read_text())
exports = []
for name in getattr(proxywhirl, "__all__", []):
    obj = getattr(proxywhirl, name, None)
    exports.append({
        "name": name,
        "kind": "class" if inspect.isclass(obj) else "function" if inspect.isfunction(obj) else "value",
        "module": getattr(obj, "__module__", "proxywhirl"),
        "doc": (inspect.getdoc(obj) or "").split("\n")[0],
    })

print(json.dumps({
    "name": pyproject["project"]["name"],
    "version": getattr(proxywhirl, "__version__", pyproject["project"]["version"]),
    "python": pyproject["project"].get("requires-python"),
    "exports": exports,
}))
`)

const openApi = runPython(String.raw`
import json
from proxywhirl.api import app
print(json.dumps(app.openapi()))
`)

const sourceData = runPython(String.raw`
import json
from proxywhirl import sources

items = []
for source in sources.ALL_SOURCES:
    items.append({
        "url": str(getattr(source, "url", "")),
        "format": getattr(getattr(source, "format", ""), "value", str(getattr(source, "format", ""))),
        "render_mode": getattr(getattr(source, "render_mode", ""), "value", str(getattr(source, "render_mode", ""))),
        "protocol": getattr(source, "protocol", None) or "http",
        "enabled": getattr(source, "enabled", True),
        "trusted": getattr(source, "trusted", False),
        "priority": getattr(source, "priority", 0),
        "timeout": getattr(source, "wait_timeout", None),
    })

protocol_counts = {}
for item in items:
    protocol = item["protocol"]
    protocol_counts[protocol] = protocol_counts.get(protocol, 0) + 1

print(json.dumps({
    "total": len(items),
    "recommended": len(getattr(sources, "RECOMMENDED_SOURCES", [])),
    "http": protocol_counts.get("http", 0) + protocol_counts.get("https", 0),
    "socks4": protocol_counts.get("socks4", 0),
    "socks5": protocol_counts.get("socks5", 0),
    "items": items,
}))
`)

const strategyData = runPython(String.raw`
import inspect
import json
from proxywhirl import strategies

items = []
for name, obj in inspect.getmembers(strategies, inspect.isclass):
    if (
        obj.__module__ == strategies.__name__
        and name.endswith("Strategy")
        and name != "RotationStrategy"
    ):
        try:
            line_number = inspect.getsourcelines(obj)[1]
        except OSError:
            line_number = 0
        items.append({
            "class": name,
            "module": obj.__module__,
            "summary": (inspect.getdoc(obj) or "").split("\n")[0],
            "line": line_number,
        })

items.sort(key=lambda item: item["line"])
print(json.dumps({"total": len(items), "items": items}))
`)

const cliSource = readFileSync(join(repoRoot, "proxywhirl", "cli.py"), "utf8")
const commands = extractCommands(cliSource)

const statsPath = join(repoRoot, "docs", "proxy-lists", "stats.json")
if (existsSync(statsPath)) {
  mkdirSync(publicProxyDir, { recursive: true })
  const proxyListFiles = [
    "README.md",
    "metadata.json",
    "stats.json",
    "proxies.json",
    "proxies-rich.json",
    "all.txt",
    "http.txt",
    "https.txt",
    "socks4.txt",
    "socks5.txt",
  ]
  for (const file of proxyListFiles) {
    const source = join(repoRoot, "docs", "proxy-lists", file)
    if (existsSync(source)) copyFileSync(source, join(publicProxyDir, file))
  }
}

function copyOgImageAssets() {
  if (!existsSync(socialPreviewSvg)) return
  copyFileSync(socialPreviewSvg, publicOgImageSvg)
  try {
    execFileSync(
      "rsvg-convert",
      ["-w", "1200", "-h", "630", "-o", publicOgImagePng, socialPreviewSvg],
      { stdio: "ignore", timeout: 30_000 },
    )
  } catch {
    // PNG optional when rsvg-convert is unavailable; metadata falls back to SVG.
  }
}

const exportKinds = countBy(packageData.exports, (item) => item.kind)
const exportModules = countBy(packageData.exports, (item) => item.module).slice(0, 12)
const coreExports = [
  "ProxyWhirl",
  "AsyncProxyWhirl",
  "Proxy",
  "ProxyPool",
  "BootstrapConfig",
  "ProxyFetcher",
  "ProxyValidator",
  "StrategyRegistry",
  "ALL_SOURCES",
  "RECOMMENDED_SOURCES",
]
  .map((name) => packageData.exports.find((item) => item.name === name))
  .filter(Boolean)

const operations = Object.entries(openApi.paths ?? {}).flatMap(([path, methods]) =>
  Object.entries(methods).map(([method, operation]) => ({
    method: method.toUpperCase(),
    path,
    area: path.split("/").filter(Boolean).slice(1, 2)[0] || "root",
    summary: operation.summary || operation.operationId || "-",
  })),
)
const operationAreas = countBy(operations, (item) => item.area)

const commandGroups = countBy(commands, (item) => item.group)
const sourceItems = sourceData.items.map((item) => ({
  ...item,
  host: hostLabel(item.url),
  format: enumValue(item.format),
  render_mode: enumValue(item.render_mode),
}))
const sourceHosts = countBy(sourceItems, (item) => item.host).slice(0, 12)
const sourceFormats = countBy(sourceItems, (item) => item.format)
const sourceProtocols = countBy(sourceItems, (item) => item.protocol)

function strategyUseWhen(item) {
  return item.summary || "Use for custom rotation behavior."
}


writeFile(
  join(generatedDocsDir, "python-api.mdx"),
  [
    frontmatter("Python API Reference", "Source-grounded public exports from proxywhirl.__all__."),
    "",
    generatedNote("`proxywhirl.__all__`, package metadata, and object docstrings"),
    "",
    statGrid([
      ["Package", packageData.name, `Version ${packageData.version}`],
      ["Python", packageData.python, "Supported runtime range"],
      ["Public exports", packageData.exports.length, "Entries in `proxywhirl.__all__`"],
      ["Modules", exportModules.length, "Top namespaces shown below"],
    ]),
    "",
    "## Core Surface",
    "",
    table(
      ["Export", "Kind", "Module", "Use"],
      coreExports.map((item) => [`\`${item.name}\``, item.kind, `\`${item.module}\``, item.doc || "-"]),
    ),
    "",
    "## Export Shape",
    "",
    table(["Kind", "Count"], exportKinds.map(([kind, count]) => [kind, count])),
    "",
    "## Top Namespaces",
    "",
    table(["Module", "Exports"], exportModules.map(([module, count]) => [`\`${module}\``, count])),
    "",
    "## All Public Exports",
    "",
    table(
      ["Export", "Kind", "Module", "Summary"],
      packageData.exports.map((item) => [
        `\`${item.name}\``,
        item.kind,
        `\`${item.module}\``,
        item.doc || "-",
      ]),
    ),

  ].join("\n"),
)

writeFile(
  join(generatedDocsDir, "rest-api.mdx"),
  [
    frontmatter("REST/OpenAPI Reference", "FastAPI OpenAPI summary generated from proxywhirl.api.app."),
    "",
    generatedNote("`proxywhirl.api.app.openapi()`"),
    "",
    statGrid([
      ["API", openApi.info?.title ?? "ProxyWhirl API", `Version ${openApi.info?.version ?? "unknown"}`],
      ["Paths", Object.keys(openApi.paths ?? {}).length, "OpenAPI path entries"],
      ["Operations", operations.length, "HTTP method + path pairs"],
      ["Schemas", Object.keys(openApi.components?.schemas ?? {}).length, "Request/response models"],
    ]),
    "",
    "## Route Areas",
    "",
    table(["Area", "Operations"], operationAreas.map(([area, count]) => [area, count])),
    "",
    "## Operation Inventory",
    "",
    table(
      ["Method", "Path", "Operation"],
      operations.map((item) => [item.method, `\`${item.path}\``, item.summary]),
    ),
  ].join("\n"),
)

writeFile(
  join(generatedDocsDir, "cli-reference.mdx"),
  [
    frontmatter("CLI Reference", "Typer command inventory parsed from proxywhirl.cli."),
    "",
    generatedNote("Typer command declarations and docstrings in `proxywhirl/cli.py`"),
    "",
    statGrid([
      ["Commands", commands.length, "Typer command declarations"],
      ["Groups", commandGroups.length, "Top-level plus nested apps"],
      ["Primary flow", "fetch", "Hydrate and validate proxy data"],
      ["Data flow", "export", "Write dashboard-ready proxy lists"],
    ]),
    "",
    "## Command Groups",
    "",
    table(["Group", "Commands"], commandGroups.map(([group, count]) => [group, count])),
    "",
    "## Command Inventory",
    "",
    table(
      ["Command", "Summary", "Flags", "Function"],
      commands.map((item) => [
        `\`${item.path}\``,
        item.summary,
        item.flags === "-" ? "-" : `\`${item.flags}\``,
        `\`${item.function}\``,
      ]),
    ),
  ].join("\n"),
)

writeFile(
  join(generatedDocsDir, "proxy-sources.mdx"),
  [
    frontmatter("Proxy Sources", "Proxy source catalog generated from proxywhirl.sources."),
    "",
    generatedNote("`proxywhirl.sources.ALL_SOURCES` and related source collections"),
    "",
    statGrid([
      ["Total sources", sourceData.total, "Enabled built-in catalog"],
      ["Recommended", sourceData.recommended, "Fast-start curated set"],
      ["HTTP", sourceData.http, "HTTP/HTTPS source entries"],
      ["SOCKS", sourceData.socks4 + sourceData.socks5, "SOCKS4 + SOCKS5 source entries"],
    ]),
    "",
    "## Protocol Mix",
    "",
    table(["Protocol", "Sources"], sourceProtocols.map(([protocol, count]) => [protocol, count])),
    "",
    "## Format Mix",
    "",
    table(["Format", "Sources"], sourceFormats.map(([format, count]) => [format, count])),
    "",
    "## Top Providers",
    "",
    table(["Provider", "Sources"], sourceHosts.map(([host, count]) => [host, count])),
    "",
    "## Source Catalog",
    "",
    table(
      ["Provider", "URL", "Protocol", "Enabled", "Format", "Timeout"],
      sourceItems.map((item) => [
        item.host,
        item.url.length > 48 ? `${item.url.slice(0, 45)}...` : item.url,
        item.protocol,
        item.enabled ? "yes" : "no",
        item.format,
        item.timeout ? `${item.timeout / 1000}s` : "-",
      ]),
    ),
  ].join("\n"),
)

writeFile(
  join(generatedDocsDir, "strategies.mdx"),
  [
    frontmatter("Strategy Matrix", "Rotation strategy matrix generated from proxywhirl.strategies."),
    "",
    generatedNote("exported strategy classes in `proxywhirl.strategies`"),
    "",
    statGrid([
      ["Strategies", strategyData.total, "Concrete rotation classes"],
      ["Default", "RoundRobin", "Balanced first choice"],
      ["Fastest", "PerformanceBased", "EMA latency preference"],
      ["Composable", "Composite", "Filter and select pipeline"],
    ]),
    "",
    "## Strategy Selection",
    "",
    table(
      ["Strategy", "Use When", "Source Summary"],
      strategyData.items.map((item) => [
        `\`${item.class}\``,
        strategyUseWhen(item),
        item.summary || "-",
      ]),
    ),
    "",
    "## Source Modules",
    "",
    table(["Module", "Strategies"], countBy(strategyData.items, (item) => item.module).map(([module, count]) => [`\`${module}\``, count])),
  ].join("\n"),
)

writeFile(join(generatedDataDir, "openapi.json"), `${JSON.stringify(openApi, null, 2)}\n`)
writeFile(join(generatedDataDir, "sources.json"), `${JSON.stringify(sourceData, null, 2)}\n`)
writeFile(join(generatedDataDir, "strategies.json"), `${JSON.stringify(strategyData, null, 2)}\n`)

copyOgImageAssets()

console.log(`Generated docs surfaces in ${generatedDocsDir}`)
