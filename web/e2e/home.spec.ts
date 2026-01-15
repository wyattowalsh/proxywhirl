import { test, expect, devices } from '@playwright/test';

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
    await expect(page.getByPlaceholder('Search proxies...')).toBeVisible();
    
    // Check for table rows. Wait for data loading.
    const table = page.locator('table');
    await expect(table).toBeVisible();
    
    // Hover over a row to see the Test button (Terminal Icon)
    const firstRow = page.locator('table tbody tr').first();
    await expect(firstRow).toBeVisible({ timeout: 10000 });
    
    await firstRow.hover();
    
    const testButton = firstRow.locator('button[title="Copy test command"]');
    await expect(testButton).toBeVisible();
  });

  test('should show scroll-to-top button', async ({ page }) => {
    // Scroll down
    await page.evaluate(() => window.scrollTo(0, 1000));
    
    // Check for Scroll to Top button.
    const scrollBtn = page.getByLabel('Scroll to top');
    await expect(scrollBtn).toBeVisible();
    
    // Click it
    await scrollBtn.click();
    
    // Verify we are back at top
    await expect(page.evaluate(() => window.scrollY)).resolves.toBeLessThan(10);
  });
});

test.describe('Mobile Navigation', () => {
  test.use({ ...devices['Pixel 5'] });

  test('should toggle mobile menu', async ({ page }) => {
    await page.goto('/');
    
    // Check menu button exists (md:hidden)
    const menuBtn = page.locator('button').filter({ has: page.locator('svg.lucide-menu') }).first();
    await expect(menuBtn).toBeVisible();
    await menuBtn.click();
    
    // Check if menu content appears
    await expect(page.getByRole('menuitem', { name: 'Raw List' })).toBeVisible();
  });
});
