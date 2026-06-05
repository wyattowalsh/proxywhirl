import { test, expect } from '@playwright/test';

test.describe('Home Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display correct title and heading', async ({ page }) => {
    await expect(page).toHaveTitle(/ProxyWhirl/);
    await expect(page.getByRole('heading', { name: 'ProxyWhirl', level: 1 })).toBeVisible();
  });

  test('should load statistics', async ({ page }) => {
    await expect(page.getByText('Total Proxies')).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('Countries')).toBeVisible();
  });

  test('should display proxy table and test button', async ({ page }) => {
    await expect(page.getByRole('textbox', { name: 'Search IP, port... (/)' })).toBeVisible({
      timeout: 10000,
    });
    await expect(page.getByRole('button', { name: 'Copy test command' }).first()).toBeVisible({
      timeout: 10000,
    });
  });

  test('should show scroll-to-top button', async ({ page }) => {
    // Scroll down
    await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
    await expect.poll(async () => page.evaluate(() => window.scrollY)).toBeGreaterThan(300);

    // Check for Scroll to Top button.
    const scrollBtn = page.getByLabel('Scroll to top');
    await expect(scrollBtn).toBeVisible();

    // Click it
    await scrollBtn.click();

    // Verify we are back at top
    await expect.poll(async () => page.evaluate(() => window.scrollY)).toBeLessThan(10);
  });
});

test.describe('Mobile Navigation', () => {
  test('should toggle mobile menu', async ({ page, isMobile }) => {
    test.skip(!isMobile, 'Mobile-only navigation');

    await page.goto('/');

    const menuBtn = page.getByRole('button', { name: 'Toggle menu' });
    await expect(menuBtn).toBeVisible();
    await menuBtn.click();

    await expect(page.getByRole('menuitem', { name: 'Docs' })).toBeVisible();
    await expect(page.getByRole('menuitem', { name: 'GitHub' })).toBeVisible();
  });
});
