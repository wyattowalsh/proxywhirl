import {
  getLLMFullText,
  getOrderedPages,
  generateLLMHeader,
} from '@/lib/llm';

// cached forever
export const revalidate = false;

export async function GET() {
  const orderedPages = getOrderedPages();
  const header = generateLLMHeader(orderedPages);

  const scan = orderedPages.map(getLLMFullText);
  const scanned = await Promise.all(scan);

  const fullContent = [header, ...scanned].join('\n\n---\n\n');

  return new Response(fullContent);
} 