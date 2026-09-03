const { test, expect } = require('@playwright/test');
const fs = require('fs');

const indexSource = fs.readFileSync('index.html', 'utf8');
const feedbackSource = fs.readFileSync('feedback.html', 'utf8');
const normalizedIndexSource = indexSource.replace(/\s+/g, ' ');

test.describe('E-Zone regular source smoke', () => {
  test('200-foot zone cannot lock from a short drag', async () => {
    expect(indexSource).toContain('reachedRequiredRadius');
    expect(indexSource).toContain('STATE.arcData.radiusM >= CONFIG.defaultRadiusMeters - 0.05');
    expect(indexSource).toContain('Drag to the full 200 ft before releasing.');
    expect(indexSource).toContain('STATE.arcData.radiusM = CONFIG.defaultRadiusMeters');
  });

  test('feedback requires an explicit backend success response', async () => {
    expect(feedbackSource).not.toContain("mode: 'no-cors'");
    expect(feedbackSource).toContain('data.success === true');
    expect(feedbackSource).toContain('if (!res.ok || !accepted)');
  });

  test('old builder bypass is absent', async () => {
    expect(indexSource).not.toContain('builderBypassCode');
    expect(indexSource).not.toContain('Builder bypass accepted');
  });

  test('browser routing values are not labeled as secrets', async () => {
    expect(indexSource).not.toContain('SECRET_TOKEN');
    expect(feedbackSource).not.toContain('SECRET_TOKEN');
    expect(indexSource).toContain('not an authentication secret');
    expect(feedbackSource).toContain('not an authentication secret');
  });

  test('privacy wording matches beta-record and photo transmission behavior', async () => {
    expect(normalizedIndexSource).toMatch(
      /submits agreement\/check-in records and tester feedback through the (?:designated E-Zone tester system|connected E-Zone submission system)/i,
    );
    expect(normalizedIndexSource).toMatch(/name, device\/browser information/i);
    expect(normalizedIndexSource).toMatch(
      /Evidence photos are queued on the device.*send-to-BOE action/i,
    );
  });

  test('campaign sign is the preferred incident marker and legacy marker remains available', async () => {
    expect(indexSource).toContain("iconUrl: 'assets/campaign-sign-marker.svg'");
    expect(indexSource).toContain('iconSize: [58, 82]');
    expect(indexSource).toContain('iconAnchor: [29, 82]');
    expect(indexSource).toContain('LEGACY_INCIDENT_ICON = L.divIcon');
    expect(indexSource).toContain('INCIDENT_ICON = CAMPAIGN_SIGN_ICON');
  });
});
