import { test, expect } from '@playwright/test';
import {
  waitForAnalyticsDashboard,
  waitForAnalyticsReady,
  waitForDeferredSection,
  waitForHomeReady,
} from './helpers';

test.describe('Analytics Page', () => {
  test('should load analytics dashboard', async ({ page }) => {
    await page.goto('/analytics');
    await waitForAnalyticsReady(page);

    await expect(page).toHaveTitle(/Analytics/i);
    await expect(
      page.getByText('Comprehensive proxy health, performance, and geographic insights'),
    ).toBeVisible();
  });

  test('should render analytics charts after data loads', async ({ page }) => {
    await page.goto('/analytics');
    await waitForAnalyticsDashboard(page);

    await expect(page.getByRole('heading', { name: 'Response Speed', level: 3 })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Validation Depth', level: 3 })).toBeVisible();
  });

  test('should render deferred global distribution section after scroll', async ({ page }) => {
    test.setTimeout(60_000);
    await page.goto('/analytics');
    await waitForAnalyticsDashboard(page);
    await waitForDeferredSection(page, 'Global Distribution');
  });

  test('should navigate back to home', async ({ page }) => {
    await page.goto('/analytics');
    await waitForAnalyticsReady(page);

    await page.getByRole('link', { name: 'Back to home' }).click();

    await expect(page).toHaveURL('/');
    await waitForHomeReady(page);
  });
});
