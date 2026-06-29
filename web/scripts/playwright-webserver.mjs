import { execSync, spawn } from "node:child_process";
import { existsSync, unlinkSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const webRoot = join(fileURLToPath(new URL(".", import.meta.url)), "..");
const buildIdPath = join(webRoot, ".next", "BUILD_ID");
const lockPath = join(webRoot, ".next", "lock");
const port = process.env.E2E_PORT ?? "4177";
const nextBin = join(webRoot, "node_modules", ".bin", "next");

function ensureBuild() {
	const forceBuild = process.env.E2E_FORCE_BUILD === "1";
	if (!forceBuild && existsSync(buildIdPath)) {
		return;
	}

	if (existsSync(lockPath)) {
		unlinkSync(lockPath);
	}

	execSync("pnpm run build", { cwd: webRoot, stdio: "inherit" });
}

ensureBuild();

const child = spawn(nextBin, ["start", "-p", port], {
	cwd: webRoot,
	stdio: "inherit",
});

child.on("exit", (code) => {
	process.exit(code ?? 0);
});
