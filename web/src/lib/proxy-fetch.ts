import type { Proxy, SlimProxyData, SlimProxyJsonRaw } from "@/types";
import { PROTOCOLS } from "@/types";

export function parseSlimProxyJson(raw: SlimProxyJsonRaw): SlimProxyData {
	const generatedAt = raw.metadata.generated_at;
	const proxies: Proxy[] = [];

	for (const protocol of PROTOCOLS) {
		const entries = raw.proxies[protocol] ?? [];
		for (const entry of entries) {
			const lastColon = entry.lastIndexOf(":");
			if (lastColon <= 0) continue;

			const ip = entry.slice(0, lastColon);
			const port = Number.parseInt(entry.slice(lastColon + 1), 10);
			if (!Number.isFinite(port)) continue;

			proxies.push({
				ip,
				port,
				protocol,
				status: "unknown",
				response_time: null,
				success_rate: null,
				total_checks: 0,
				source: "",
				last_checked: null,
				created_at: generatedAt,
			});
		}
	}

	return {
		generated_at: generatedAt,
		total: proxies.length,
		proxies,
		metadata: raw.metadata,
	};
}

export async function fetchJsonWithProgress<T>(
	url: string,
	onProgress?: (percent: number) => void,
): Promise<T> {
	const res = await fetch(url);
	if (!res.ok) throw new Error(`Failed to fetch ${url}`);

	const contentLength = res.headers.get("Content-Length");

	if (contentLength && res.body && onProgress) {
		const total = Number.parseInt(contentLength, 10);
		const reader = res.body.getReader();
		let received = 0;
		const chunks: Uint8Array[] = [];

		while (true) {
			const { done, value } = await reader.read();
			if (done) break;

			if (value) {
				chunks.push(value);
				received += value.length;
				onProgress(Math.round((received / total) * 100));
			}
		}

		const bodyContent = new Uint8Array(received);
		let position = 0;
		for (const chunk of chunks) {
			bodyContent.set(chunk, position);
			position += chunk.length;
		}

		const text = new TextDecoder("utf-8").decode(bodyContent);
		return JSON.parse(text) as T;
	}

	return res.json() as Promise<T>;
}