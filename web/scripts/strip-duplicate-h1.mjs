#!/usr/bin/env node
/**
 * strip-duplicate-h1.mjs
 *
 * Fumadocs renders each page's frontmatter `title` as the page `<h1>`. Any
 * top-level ATX heading (`# ...`) as the first body line therefore produces a
 * second, duplicate `<h1>` (audit finding RV-N1). This codemod removes that
 * leading duplicate heading from handwritten MDX pages.
 *
 * Rules:
 *   1. Parse the leading YAML frontmatter block (`---` ... `---`).
 *   2. Inspect the first non-empty body line. If it is a single-`#` heading
 *      (`# Heading`), it duplicates the auto-rendered title -> remove it (plus
 *      one trailing blank line so spacing stays clean).
 *   3. Never touch fenced code blocks: if the first body line opens a code
 *      fence, skip the file.
 *   4. EXEMPT globs are skipped entirely:
 *        - api/openapi/**  (OpenAPI pages use `full: true`, no body h1)
 *        - generated/**    (owned by generate-docs.mjs template h1 removal)
 *
 * Usage:
 *   node scripts/strip-duplicate-h1.mjs [--dry-run] [path ...]
 *
 * With no path arguments, walks web/content/docs recursively.
 */
import { readdirSync, readFileSync, statSync, writeFileSync } from "node:fs"
import { dirname, join, relative } from "node:path"
import { fileURLToPath } from "node:url"

const __dirname = dirname(fileURLToPath(import.meta.url))
const webRoot = join(__dirname, "..")
const docsRoot = join(webRoot, "content", "docs")

const args = process.argv.slice(2)
const dryRun = args.includes("--dry-run")
const targets = args.filter((arg) => arg !== "--dry-run")

const EXEMPT = [/\/api\/openapi\//, /\/generated\//]

function isExempt(path) {
  const normalized = path.replaceAll("\\", "/")
  return EXEMPT.some((pattern) => pattern.test(normalized))
}

function walk(root) {
  const results = []
  for (const entry of readdirSync(root)) {
    const full = join(root, entry)
    const stats = statSync(full)
    if (stats.isDirectory()) results.push(...walk(full))
    else if (entry.endsWith(".mdx")) results.push(full)
  }
  return results
}

function resolveTargets() {
  if (targets.length === 0) return walk(docsRoot)
  const files = []
  for (const target of targets) {
    const stats = statSync(target)
    if (stats.isDirectory()) files.push(...walk(target))
    else if (target.endsWith(".mdx")) files.push(target)
  }
  return files
}

/**
 * Strip the leading duplicate `# heading` from an MDX source string.
 * @returns {{ changed: boolean, content: string, heading?: string }}
 */
function stripLeadingH1(source) {
  const lines = source.split("\n")

  if (lines[0]?.trim() !== "---") return { changed: false, content: source }

  let frontmatterEnd = -1
  for (let i = 1; i < lines.length; i += 1) {
    if (lines[i].trim() === "---") {
      frontmatterEnd = i
      break
    }
  }
  if (frontmatterEnd === -1) return { changed: false, content: source }

  let bodyStart = frontmatterEnd + 1
  while (bodyStart < lines.length && lines[bodyStart].trim() === "") bodyStart += 1
  if (bodyStart >= lines.length) return { changed: false, content: source }

  const firstBodyLine = lines[bodyStart]

  if (firstBodyLine.trimStart().startsWith("```")) return { changed: false, content: source }

  const headingMatch = firstBodyLine.match(/^#\s+(.+?)\s*$/)
  if (!headingMatch) return { changed: false, content: source }

  const removeUpTo = bodyStart + 1
  const nextIsBlank = lines[removeUpTo]?.trim() === ""
  const spliceCount = nextIsBlank ? 2 : 1
  lines.splice(bodyStart, spliceCount)

  return { changed: true, content: lines.join("\n"), heading: headingMatch[1] }
}

const files = resolveTargets()
let changedCount = 0
const skippedExempt = []

for (const file of files) {
  const rel = relative(webRoot, file)
  if (isExempt(file)) {
    skippedExempt.push(rel)
    continue
  }
  const source = readFileSync(file, "utf8")
  const { changed, content, heading } = stripLeadingH1(source)
  if (!changed) continue
  changedCount += 1
  if (dryRun) {
    console.log(`[dry-run] would strip "# ${heading}" from ${rel}`)
  } else {
    writeFileSync(file, content)
    console.log(`stripped "# ${heading}" from ${rel}`)
  }
}

console.log(
  `${dryRun ? "[dry-run] " : ""}${changedCount} file(s) ${dryRun ? "would be " : ""}updated; ${skippedExempt.length} exempt file(s) skipped.`,
)
