import { expect, test } from '@playwright/test';

test.describe('VIREONIQ UI Smoke & Accessibility', () => {
  test('login page renders without console errors and passes basic accessibility structure', async ({ page }) => {
    const errors: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    page.on('pageerror', (err) => {
      errors.push(err.message);
    });

    await page.goto('/login');
    await page.waitForLoadState('networkidle');

    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();

    const headingCount = await page.locator('h1, h2').count();
    expect(headingCount).toBeGreaterThan(0);

    await page.screenshot({ path: 'playwright-report/login-smoke.png', fullPage: true });
    expect(errors).toEqual([]);
  });

  test('register page renders form inputs cleanly', async ({ page }) => {
    await page.goto('/register');
    await page.waitForLoadState('networkidle');

    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]').first()).toBeVisible();
    await page.screenshot({ path: 'playwright-report/register-smoke.png', fullPage: true });
  });
});
