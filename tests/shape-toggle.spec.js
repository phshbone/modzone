const { test, expect } = require('@playwright/test');

async function prep(page) {
  await page.goto('index.html', { waitUntil: 'domcontentloaded' });
  await page.evaluate(() => {
    ['agreement-overlay', 'returning-overlay', 'welcome-overlay', 'beta-splash-overlay', 'testing-tips-overlay'].forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.style.display = 'none';
    });
    document.getElementById('map-wrapper').style.display = 'flex';
    document.getElementById('map-ui').style.display = 'block';
    if (!STATE.mapReady) initMap();
    STATE.gpsPos = { lat: 40.0, lng: -74.5 };
    STATE.lockedPos = { lat: 40.0, lng: -74.5 };
    STATE.arcData = { radiusM: 60.96, radiusPx: 100, openingAngleDeg: 90 };
    STATE.arcLocked = true;
    map.setView([40.0, -74.5], 18, { animate: false });
    drawZone();
  });
}

test.describe('temporary zone shape comparison toggle', () => {
  test('270 degrees remains the production default', async ({ page }) => {
    await prep(page);
    const state = await page.evaluate(() => ({
      mode: STATE.zoneShapeMode,
      active270: document.querySelector('[data-zone-shape="270"]').classList.contains('active'),
      active180: document.querySelector('[data-zone-shape="180"]').classList.contains('active'),
      radiusM: STATE.arcData.radiusM,
      openingAngleDeg: STATE.arcData.openingAngleDeg,
    }));
    expect(state.mode).toBe('270');
    expect(state.active270).toBe(true);
    expect(state.active180).toBe(false);
    expect(state.radiusM).toBeCloseTo(60.96, 2);
    expect(state.openingAngleDeg).toBe(90);
  });

  test('180 degrees redraws a semicircle and preserves the same stored radius/orientation', async ({ page }, testInfo) => {
    await prep(page);
    const before = await page.evaluate(() => ({ ...STATE.arcData }));
    await page.locator('[data-zone-shape="180"]').click();
    await page.waitForTimeout(100);

    const result = await page.evaluate(() => {
      const svg = document.getElementById('zone-svg');
      return {
        mode: STATE.zoneShapeMode,
        arcData: { ...STATE.arcData },
        pathCount: svg.querySelectorAll('path').length,
        lineCount: svg.querySelectorAll('line').length,
        active180: document.querySelector('[data-zone-shape="180"]').classList.contains('active'),
        active270: document.querySelector('[data-zone-shape="270"]').classList.contains('active'),
        pathData: Array.from(svg.querySelectorAll('path')).map((p) => p.getAttribute('d') || ''),
      };
    });

    expect(result.mode).toBe('180');
    expect(result.active180).toBe(true);
    expect(result.active270).toBe(false);
    expect(result.arcData.radiusM).toBe(before.radiusM);
    expect(result.arcData.openingAngleDeg).toBe(before.openingAngleDeg);
    expect(result.pathCount).toBeGreaterThanOrEqual(2);
    expect(result.lineCount).toBeGreaterThanOrEqual(1); // explicit diameter boundary
    expect(result.pathData.some((d) => d.includes(' A') && d.includes(' 0 0 1 '))).toBe(true);

    await page.screenshot({
      path: `verification-artifacts/${testInfo.project.name}/zone-shape-180.png`,
      fullPage: false,
    });
  });

  test('toggle can return to 270 degrees without changing arc data', async ({ page }) => {
    await prep(page);
    const before = await page.evaluate(() => ({ ...STATE.arcData }));
    await page.locator('[data-zone-shape="180"]').click();
    await page.locator('[data-zone-shape="270"]').click();
    const after = await page.evaluate(() => ({
      mode: STATE.zoneShapeMode,
      arcData: { ...STATE.arcData },
      active270: document.querySelector('[data-zone-shape="270"]').classList.contains('active'),
    }));
    expect(after.mode).toBe('270');
    expect(after.active270).toBe(true);
    expect(after.arcData.radiusM).toBe(before.radiusM);
    expect(after.arcData.openingAngleDeg).toBe(before.openingAngleDeg);
  });
});
