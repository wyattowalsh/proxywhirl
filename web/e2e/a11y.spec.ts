import AxeBuilder from '@axe-core/playwright';
import { test, expect } from '@playwright/test';
import { waitForHomeReady } from './helpers';

/**
 * Practical axe CI gate: WCAG 2 A/AA structure rules, excluding known noisy
 * chart SVG sectors (covered by sr-only tables) and color-contrast (theme
 * follow-ups tracked separately from Wave 4 wiring).
 */
function axeFor(page: ConstructorParameters<typeof AxeBuilder>[0]['page']) {
  return new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .disableRules(['color-contrast', 'svg-img-alt'])
    .exclude('.recharts-wrapper')
    .exclude('.recharts-surface');
}

test.describe('Accessibility (axe)', () => {
  test.describe.configure({ mode: 'serial' });

  test('home has no serious axe violations', async ({ page }, testInfo) => {
    test.skip(testInfo.project.name !== 'chromium', 'axe CI gate runs on desktop chromium only');

    await page.goto('/');
    await waitForHomeReady(page);

    const results = await axeFor(page).analyze();
    expect(results.violations, JSON.stringify(results.violations, null, 2)).toEqual([]);
  });

  test('docs quickstart has skip link and no serious axe violations', async ({ page }, testInfo) => {
    test.skip(testInfo.project.name !== 'chromium', 'axe CI gate runs on desktop chromium only');

    await page.goto('/docs/quickstart');
    await expect(
      page.getByRole('heading', { name: 'Quickstart', level: 1 }).first(),
    ).toBeVisible();

    const skipLink = page.getByRole('link', { name: 'Skip to content' });
    await expect(skipLink).toHaveCount(1);

    const results = await axeFor(page).analyze();
    expect(results.violations, JSON.stringify(results.violations, null, 2)).toEqual([]);
  });
});
