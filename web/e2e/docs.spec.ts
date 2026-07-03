import { test, expect, type Page } from '@playwright/test';

async function openDocsSidebarIfNeeded(page: Page) {
  const openSidebar = page.getByRole('button', { name: /open sidebar/i });
  if (await openSidebar.isVisible()) {
    await openSidebar.click();
  }
}

test.describe('Docs', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/docs/');
  });

  test('should show docs sidebar navigation', async ({ page }) => {
    await expect(page.getByRole('link', { name: 'Quickstart' }).first()).toBeVisible();
    await expect(page.getByRole('link', { name: 'Guides' }).first()).toBeVisible();
  });

  test('should open search dialog', async ({ page }) => {
    const searchButton = page.getByRole('button', { name: /search/i });
    await searchButton.first().click();

    const dialog = page.getByRole('dialog');
    await expect(dialog).toBeVisible({ timeout: 10000 });
    await expect(
      dialog.getByRole('combobox').or(dialog.getByRole('textbox')).first(),
    ).toBeVisible();
  });

  test('should load quickstart page with a single h1', async ({ page }) => {
    await page.goto('/docs/quickstart');

    await expect(page).toHaveTitle(/Quickstart/i);
    await expect(
      page.getByRole('heading', { name: 'Quickstart', level: 1 }).first(),
    ).toBeVisible();
    await expect(page.getByText('Install ProxyWhirl with uv first')).toBeVisible();
    await expect(page.getByRole('heading', { level: 1 })).toHaveCount(1);
  });

  test('should show project ADR section in sidebar', async ({ page }) => {
    await page.goto('/docs/project/adr');

    await expect(
      page.getByRole('heading', { name: /Architecture Decision Records/i, level: 1 }).first(),
    ).toBeVisible();
    await openDocsSidebarIfNeeded(page);
    await expect(page.getByRole('link', { name: /Architecture Decision Records/i }).first()).toBeVisible();
  });

  test('should load operations ci-cd page', async ({ page }) => {
    await page.goto('/docs/operations/ci-cd');

    await expect(page).toHaveTitle(/CI\/CD/i);
    await expect(page.getByRole('heading', { level: 1 })).toHaveCount(1);
  });

  test('should load generated python-api reference with one h1', async ({ page }) => {
    await page.goto('/docs/generated/python-api');

    await expect(page.getByText('Package').first()).toBeVisible({ timeout: 10000 });
    await expect(page.getByRole('heading', { level: 1 })).toHaveCount(1);
  });

  test('should load an OpenAPI endpoint page', async ({ page }) => {
    await page.goto('/docs/api/openapi/monitoring/get_stats_api_stats_get');

    await expect(page.getByRole('heading', { name: /performance statistics/i }).first()).toBeVisible({
      timeout: 10000,
    });
  });

  test('should return search results for deployment', async ({ page }) => {
    const searchButton = page.getByRole('button', { name: /search/i });
    await searchButton.first().click();

    const dialog = page.getByRole('dialog');
    await expect(dialog).toBeVisible({ timeout: 10000 });

    const input = dialog.getByRole('combobox').or(dialog.getByRole('textbox')).first();
    await input.fill('deployment');
    await expect(dialog.getByText(/deployment/i).first()).toBeVisible({ timeout: 10000 });
  });

  test('should toggle dark mode on quickstart', async ({ page }) => {
    await page.goto('/docs/quickstart');

    await openDocsSidebarIfNeeded(page);
    const themeToggle = page.getByRole('button', { name: /toggle theme/i }).first();
    await expect(themeToggle).toBeVisible();
    await themeToggle.click();

    await expect(page.locator('html')).toHaveClass(/dark/);
  });
});
