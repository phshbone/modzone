const { test, expect } = require('@playwright/test');

// Final verified cleanup candidate: these smoke cases run against the normalized repaired HTML.
test.describe('E-Zone branch harness smoke', () => {
  test('application shell loads cleanly', async ({ page }) => {
    const pageErrors = [];
    page.on('pageerror', (error) => pageErrors.push(error.message));

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
    const visibleGate =
      (await agreement.isVisible().catch(() => false)) ||
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
  test('compact mandatory beta gate avoids forced scrolling', async ({ page }) => {
    await page.goto('/index.html', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(900);
    await expect(page.locator('#agreement-overlay')).toBeVisible();
    await expect(page.locator('#agreement-card')).toBeVisible();
    await expect(page.locator('#agree-scroll')).toHaveCount(0);
    await expect(page.locator('#agree-check')).toBeEnabled();
    await expect(page.locator('#agreement-card details summary')).toContainText(
      'View full beta terms',
    );
    await expect(page.locator('#agreement-card')).not.toContainText('Please scroll through');
  });

  test('status toast stays above the bottom action area', async ({ page }) => {
    await page.goto('/index.html', { waitUntil: 'domcontentloaded' });
    await page.evaluate(() => {
      const agreement = document.getElementById('agreement-overlay');
      const returning = document.getElementById('returning-overlay');
      const welcome = document.getElementById('welcome-overlay');
      if (agreement) agreement.style.display = 'none';
      if (returning) returning.style.display = 'none';
      if (welcome) welcome.style.display = 'none';

      const mapUi = document.getElementById('map-ui');
      mapUi.style.display = 'block';

      const bar = document.getElementById('bottom-bar');
      bar.innerHTML = '<div class="btn-row"><button class="app-btn btn-blue">Back</button></div>';
      showToast('GPS location saved', '#16a34a');
    });
    await page.waitForTimeout(100);
    const positions = await page.evaluate(() => {
      const toast = document.getElementById('toast').getBoundingClientRect();
      const bar = document.getElementById('bottom-bar').getBoundingClientRect();
      return { toastBottom: toast.bottom, barTop: bar.top };
    });
    expect(positions.toastBottom).toBeLessThan(positions.barTop);
  });
});
