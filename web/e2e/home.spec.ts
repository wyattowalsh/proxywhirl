import { test, expect } from '@playwright/test';
import { waitForHomeReady } from './helpers';

test.describe('Home Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await waitForHomeReady(page);
  });

  test('should display correct title and heading', async ({ page }) => {
    await expect(page).toHaveTitle(/ProxyWhirl/);
    await expect(page.getByRole('heading', { name: 'ProxyWhirl', level: 1 })).toBeVisible();
  });

  test('should load statistics', async ({ page }) => {
    await expect(page.getByText('Total Proxies')).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('Countries')).toBeVisible();
  });

  test('should show Analytics link in header', async ({ page, isMobile }) => {
    test.skip(isMobile, 'Analytics nav link is in the desktop header bar');

    const analyticsLink = page.locator('header').getByRole('link', { name: 'Analytics' });
    await expect(analyticsLink).toBeVisible();
    await expect(analyticsLink).toHaveAttribute('href', '/analytics');
  });

  test('should display proxy table and test button', async ({ page }) => {
    const searchInput = page.getByRole('textbox', { name: 'Search proxies by IP, port, or source' });
    await expect(searchInput).toBeVisible({ timeout: 10000 });
    await expect(searchInput).toHaveAttribute(
      'aria-label',
      'Search proxies by IP, port, or source',
    );
    await expect(page.getByRole('button', { name: 'Copy test command' }).first()).toBeVisible({
      timeout: 10000,
    });
  });

  test('should show scroll-to-top button', async ({ page }) => {
    await expect(page.getByRole('textbox', { name: 'Search proxies by IP, port, or source' })).toBeVisible({
      timeout: 10000,
    });
    await expect.poll(async () => page.evaluate(() => document.documentElement.scrollHeight - window.innerHeight)).toBeGreaterThan(300);

    // Scroll down
    await page.evaluate(() => {
      const scrollingElement = document.scrollingElement ?? document.documentElement;
      scrollingElement.scrollTop = scrollingElement.scrollHeight;
    });
    await expect.poll(async () => page.evaluate(() => window.scrollY || document.documentElement.scrollTop)).toBeGreaterThan(300);

    // Check for Scroll to Top button.
    const scrollBtn = page.getByLabel('Scroll to top');
    await expect(scrollBtn).toBeVisible();
    await scrollBtn.scrollIntoViewIfNeeded();

    // Click it (scroll can trigger re-render; allow retry)
    await scrollBtn.click({ timeout: 10_000 });

    // Verify we are back at top
    await expect.poll(async () => page.evaluate(() => window.scrollY)).toBeLessThan(10);
  });
});

test.describe('Mobile Navigation', () => {
  test('should toggle mobile menu', async ({ page, isMobile }) => {
    test.skip(!isMobile, 'Mobile-only navigation');

    await page.goto('/');
    await waitForHomeReady(page);

    const menuBtn = page.getByRole('button', { name: 'Toggle menu' });
    await expect(menuBtn).toBeVisible();
    await menuBtn.click();

    await expect(page.getByRole('menuitem', { name: 'Docs' })).toBeVisible();
    await expect(page.getByRole('menuitem', { name: 'Analytics' })).toBeVisible();
    await expect(page.getByRole('menuitem', { name: 'GitHub' })).toBeVisible();
  });
});
