import { remark } from 'remark';
import remarkGfm from 'remark-gfm';
import remarkMdx from 'remark-mdx';
import { remarkInclude } from 'fumadocs-mdx/config';
import { source } from './source';
import type { InferPageType, PageTree } from 'fumadocs-core/source';

const processor = remark().use(remarkMdx).use(remarkInclude).use(remarkGfm);

function getOrderedUrls(nodes: PageTree.Node[] = []): string[] {
  const urls: string[] = [];
  for (const node of nodes) {
    if (node.type === 'page') {
      urls.push(node.url);
    } else if (node.type === 'folder') {
      if (node.index) {
        urls.push(node.index.url);
      }
      urls.push(...getOrderedUrls(node.children));
    }
  }
  return urls;
}

export function getOrderedPages(): InferPageType<typeof source>[] {
  const pages = source.getPages();
  const pageMap = new Map(pages.map((page) => [page.url, page]));
  const orderedUrls = getOrderedUrls(source.pageTree.children);

  return orderedUrls
    .map((url) => pageMap.get(url))
    .filter(Boolean) as InferPageType<typeof source>[];
}

function formatTree(nodes: PageTree.Node[], prefix = ''): string {
  let list = '';
  for (const node of nodes) {
    if (node.type === 'folder') {
      list += `${prefix}📁 ${node.name}/\n`;
      list += formatTree(node.children, prefix + '  ');
    } else {
      list += `${prefix}📄 ${node.name}\n`;
    }
  }
  return list;
}

export function generateLLMSummary(): string {
  const orderedPages = getOrderedPages();
  const title = '# proxywhirl';
  const summary =
    '> An advanced rotating proxy service with Python SDK, CLI, and REST API with several cache formats, advanced validation, and many providers.';
  const toc = `## Table of Contents\n\n${orderedPages
    .map((page) => `- [${page.data.title}](${page.url})`)
    .join('\n')}`;

  return [title, summary, toc].join('\n\n---\n\n');
}

export function generateLLMHeader(
  orderedPages: InferPageType<typeof source>[],
): string {
  const metadata = `
# proxywhirl Documentation for LLM

This document contains the full documentation for the proxywhirl project, formatted for consumption by Large Language Models.

**Project**: proxywhirl
**Description**: An advanced rotating proxy service with Python SDK, CLI, and REST API with several cache formats, advanced validation, and many providers.
`.trim();

  const fileStructure = `
## Documentation File Structure

\`\`\`
${formatTree(source.pageTree.children)}
\`\`\`
  `.trim();

  const fileSummary = `
## Included Files Summary

${orderedPages
  .map((page) => `- **${page.data.title}**: [${page.url}](${page.url})`)
  .join('\n')}
  `.trim();

  return [metadata, fileStructure, fileSummary].join('\n\n---\n\n');
}

export async function getLLMFullText(
  page: InferPageType<typeof source>,
): Promise<string> {
  const processed = await processor.process(page.content);

  return `# ${page.data.title}\nURL: ${page.url}\n\n${
    page.data.description ?? ''
  }\n\n---\n\n${processed.value}`;
} 