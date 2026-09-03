const { test, expect } = require('@playwright/test');

// Final verified cleanup candidate: these smoke cases run against the normalized repaired HTML.
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

  test('short drag cannot lock the electioneering boundary', async ({ page }) => {
    await page.goto('/index.html', { waitUntil: 'domcontentloaded' });

    const result = await page.evaluate(() => {
      STATE.screen = 's3';
      STATE.dragging = true;
      STATE.arcLocked = false;
      STATE.arcData = { radiusM: 30, radiusPx: 50, openingAngleDeg: 0 };
      STATE.gpsPos = null;
      zoneDone = false;

      onDragEnd({});

      return {
        arcLocked: STATE.arcLocked,
        radiusM: STATE.arcData.radiusM,
        screen: STATE.screen,
        zoneDone,
      };
    });

    expect(result.arcLocked).toBe(false);
    expect(result.radiusM).toBe(30);
    expect(result.screen).toBe('s3');
    expect(result.zoneDone).toBe(false);
  });

  test('full 200-foot drag locks at the normalized legal radius', async ({ page }) => {
    await page.goto('/index.html', { waitUntil: 'domcontentloaded' });

    const result = await page.evaluate(() => {
      STATE.screen = 's3';
      STATE.dragging = true;
      STATE.arcLocked = false;
      STATE.arcData = {
        radiusM: CONFIG.defaultRadiusMeters,
        radiusPx: 100,
        openingAngleDeg: 0,
      };
      STATE.gpsPos = null;
      zoneDone = true;

      onDragEnd({});

      return {
        arcLocked: STATE.arcLocked,
        radiusM: STATE.arcData.radiusM,
        expectedRadiusM: CONFIG.defaultRadiusMeters,
      };
    });

    expect(result.arcLocked).toBe(true);
    expect(result.radiusM).toBe(result.expectedRadiusM);
    expect(result.radiusM).toBeCloseTo(60.96, 2);
  });
});
