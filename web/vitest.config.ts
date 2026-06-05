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
		setupFiles: ["./src/setupTests.ts"],
	},
});
