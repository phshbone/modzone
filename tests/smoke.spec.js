const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

function verificationPath(testInfo, name) {
  const dir = path.join('verification-artifacts', testInfo.project.name);
  fs.mkdirSync(dir, { recursive: true });
  return path.join(dir, `${name}.png`);
}

async function captureVerification(page, testInfo, name) {
  await page.screenshot({ path: verificationPath(testInfo, name), fullPage: true });
}

// Permanent cleanup-branch regression suite: product repairs, compact beta UI, toast layout, and campaign incident marker.
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

  test('startup gate appears and app remains interactive', async ({ page }, testInfo) => {
    await page.goto('/index.html', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(900);

    const agreement = page.locator('#agreement-overlay');
    const returning = page.locator('#returning-overlay');
    const visibleGate =
      (await agreement.isVisible().catch(() => false)) ||
      (await returning.isVisible().catch(() => false));

    expect(visibleGate).toBeTruthy();
    await captureVerification(page, testInfo, 'startup-gate');
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

  test('status toast stays above the bottom action area', async ({ page }, testInfo) => {
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
    await captureVerification(page, testInfo, 'status-toast');
  });

  test('campaign sign incident marker loads with stake-tip anchor and legacy fallback', async ({
    page,
  }, testInfo) => {
    const assetResponse = await page.goto('/assets/campaign-sign-marker.svg');
    expect(assetResponse && assetResponse.ok()).toBeTruthy();
    await captureVerification(page, testInfo, 'campaign-sign-marker');

    await page.goto('/index.html', { waitUntil: 'domcontentloaded' });
    const marker = await page.evaluate(() => {
      initIcons();
      return {
        activeUrl: INCIDENT_ICON?.options?.iconUrl,
        activeSize: INCIDENT_ICON?.options?.iconSize,
        activeAnchor: INCIDENT_ICON?.options?.iconAnchor,
        legacyExists: Boolean(LEGACY_INCIDENT_ICON),
        campaignIsActive: INCIDENT_ICON === CAMPAIGN_SIGN_ICON,
      };
    });

    expect(marker.activeUrl).toBe('assets/campaign-sign-marker.svg');
    expect(marker.activeSize).toEqual([58, 82]);
    expect(marker.activeAnchor).toEqual([29, 82]);
    expect(marker.legacyExists).toBe(true);
    expect(marker.campaignIsActive).toBe(true);
  });
});
