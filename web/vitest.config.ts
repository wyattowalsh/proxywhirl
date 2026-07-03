import path from "node:path";
import { configDefaults, defineConfig } from "vitest/config";

export default defineConfig({
	css: {
		postcss: {
			plugins: [],
		},
	},
	resolve: {
		alias: {
			"@": path.resolve(__dirname, "./src"),
		},
	},
	test: {
		env: {
			NODE_ENV: "test",
		},
		environment: "jsdom",
		exclude: [...configDefaults.exclude, "e2e/**"],
		globals: true,
		// jsdom setup is memory-heavy; cap workers so local/CI runs do not starve forks.
		maxWorkers: 1,
		setupFiles: ["./src/setupTests.ts"],
	},
});
