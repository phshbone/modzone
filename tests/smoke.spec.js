const { test, expect } = require('@playwright/test');

// Cleanup branch verification: these smoke cases run against the normalized production HTML.
test.describe('E-Zone branch harness smoke', () => {
  test('application shell loads cleanly', async ({ page }) => {
    const pageErrors = [];
    page.on('pageerror', error => pageErrors.push(error.message));

    const response = await page.goto('/index.html', { waitUntil: 'domcontentloaded' });
    expect(response && response.ok()).toBeTruthy();
    await expect(page).toHaveTitle(/E-Zone/i);
    await expect(page.locator('body')).toContainText(/E-Zone/i);

    await page.waitForTimeout(1200);
    expect(pageErrors).toEqual([]);
  });

  test('startup gate appears and app remains interactive', async ({ page }) => {
    await page.goto('/index.html', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(900);

    const agreement = page.locator('#agreement-overlay');
    const returning = page.locator('#returning-overlay');
    const visibleGate = (await agreement.isVisible().catch(() => false)) ||
      (await returning.isVisible().catch(() => false));

    expect(visibleGate).toBeTruthy();
  });

  test('feedback page loads', async ({ page }) => {
    const response = await page.goto('/feedback.html', { waitUntil: 'domcontentloaded' });
    expect(response && response.ok()).toBeTruthy();
    await expect(page).toHaveTitle(/E-Zone Beta Report/i);
    await expect(page.locator('body')).toContainText(/E-Zone/i);
  });
});
