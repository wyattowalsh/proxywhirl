import { test, expect } from '@playwright/test';

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

  test('should load quickstart page', async ({ page }) => {
    await page.goto('/docs/quickstart');

    await expect(page).toHaveTitle(/Quickstart/i);
    await expect(
      page.getByRole('heading', { name: 'Quickstart', level: 1 }).first(),
    ).toBeVisible();
    await expect(page.getByText('Install ProxyWhirl with uv first')).toBeVisible();
  });
});