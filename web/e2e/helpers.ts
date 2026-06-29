import { expect, type Page } from "@playwright/test";

/** Wait until the home shell has hydrated and primary content is visible. */
export async function waitForHomeReady(page: Page) {
	await expect(
		page.getByRole("heading", { name: "ProxyWhirl", level: 1 }),
	).toBeVisible({ timeout: 15_000 });
}

/** Wait until analytics page shell has hydrated. */
export async function waitForAnalyticsReady(page: Page) {
	await expect(
		page.getByRole("heading", { name: "Analytics Dashboard", level: 1 }),
	).toBeVisible({ timeout: 15_000 });
}
