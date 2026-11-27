import { expect, test } from '@playwright/test';

test.describe('VIREONIQ UI Smoke & Basic Accessibility', () => {
  test('renders login page with accessible controls and captures screenshot', async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', (err) => errors.push(err.message));

    await page.goto('/login');
    await expect(page).toHaveTitle(/VIREONIQ/i);

    const emailInput = page.locator('input[type="email"]');
    const passwordInput = page.locator('input[type="password"]');
    await expect(emailInput).toBeVisible();
    await expect(passwordInput).toBeVisible();

    const submitButton = page.locator('button[type="submit"]');
    await expect(submitButton).toBeVisible();

    await page.screenshot({ path: 'playwright-report/login-smoke.png', fullPage: true });
    expect(errors).toEqual([]);
  });

  test('renders registration route without runtime errors', async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', (err) => errors.push(err.message));

    await page.goto('/register');
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await page.screenshot({ path: 'playwright-report/register-smoke.png', fullPage: true });
    expect(errors).toEqual([]);
  });
});
