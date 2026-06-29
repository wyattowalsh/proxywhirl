import { test, expect } from '@playwright/test';
import { waitForAnalyticsReady, waitForHomeReady } from './helpers';

test.describe('Analytics Page', () => {
  test('should load analytics dashboard', async ({ page }) => {
    await page.goto('/analytics');
    await waitForAnalyticsReady(page);

    await expect(page).toHaveTitle(/Analytics/i);
    await expect(
      page.getByText('Comprehensive proxy health, performance, and geographic insights'),
    ).toBeVisible();
  });

  test('should navigate back to home', async ({ page }) => {
    await page.goto('/analytics');
    await waitForAnalyticsReady(page);

    await page.getByRole('link', { name: 'Back to home' }).click();

    await expect(page).toHaveURL('/');
    await waitForHomeReady(page);
  });
});
