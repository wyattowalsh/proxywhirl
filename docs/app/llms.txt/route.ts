import { generateLLMSummary } from '@/lib/llm';

// cached forever
export const revalidate = false;

export async function GET() {
  const summaryContent = generateLLMSummary();
  return new Response(summaryContent);
} 