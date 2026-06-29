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

/** Wait until analytics dashboard charts have loaded (not just the page shell). */
export async function waitForAnalyticsDashboard(page: Page) {
	await waitForAnalyticsReady(page);
	await expect(
		page.getByRole("heading", { name: "Reliability & Performance" }),
	).toBeVisible({ timeout: 30_000 });
	await expect(page.getByText("Reliability Distribution")).toBeVisible({
		timeout: 30_000,
	});
}
