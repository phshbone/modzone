from pathlib import Path

INDEX = Path('index.html')
FEEDBACK = Path('feedback.html')
SMOKE = Path('tests/source-smoke.spec.js')

index = INDEX.read_text()
feedback = FEEDBACK.read_text()

# 1) Remove the builder-only agreement bypass from the production candidate.
index = index.replace("\n        // Builder-only testing shortcut. Type this in the beta agreement name box.\n        builderBypassCode: '2840',\n", "\n")
bypass = """\n        if (name === CONFIG.builderBypassCode) {\n          const bypassData = {\n            name: 'Builder bypass',\n            date: new Date().toLocaleString(),\n            device: 'Builder test',\n          };\n          localStorage.setItem(CONFIG.agreementKey, JSON.stringify(bypassData));\n          setBetaStatus('agree-status', 'Builder bypass accepted.', '#1d4ed8');\n          showBetaSplash();\n          return;\n        }\n"""
index = index.replace(bypass, "\n")

# 2) Require the full 200-foot radius at release. A short drag must never lock the zone.
old_drag_end = """      function onDragEnd(e) {\n        if (!STATE.dragging) return;\n        STATE.dragging = false;\n        document.getElementById('dist-readout').className = '';\n        if (STATE.arcData && STATE.screen === 's3') {\n          STATE.arcLocked = true;\n          drawGPSMarker('normal');\n          setTimeout(() => goTo('s4'), 400);\n        }\n      }\n"""
new_drag_end = """      function onDragEnd(e) {\n        if (!STATE.dragging) return;\n        STATE.dragging = false;\n        document.getElementById('dist-readout').className = '';\n\n        if (!STATE.arcData || STATE.screen !== 's3') {\n          drawGPSMarker('normal');\n          return;\n        }\n\n        const reachedRequiredRadius =\n          STATE.arcData.radiusM >= CONFIG.defaultRadiusMeters - 0.05;\n\n        if (!reachedRequiredRadius) {\n          STATE.arcLocked = false;\n          zoneDone = false;\n          drawGPSMarker('normal');\n          showToast('Drag to the full 200 ft before releasing.', '#d97706');\n          return;\n        }\n\n        // Normalize the locked boundary to the legal target rather than preserving rounding drift.\n        STATE.arcData.radiusM = CONFIG.defaultRadiusMeters;\n        STATE.arcData.radiusPx = metersToPixels(CONFIG.defaultRadiusMeters);\n        STATE.arcLocked = true;\n        drawGPSMarker('normal');\n        saveSession();\n        setTimeout(() => goTo('s4'), 400);\n      }\n"""
if old_drag_end not in index:
    raise SystemExit('Expected onDragEnd block not found; refusing broad repair.')
index = index.replace(old_drag_end, new_drag_end, 1)

# 3) Browser-visible routing values are compatibility values, not authentication secrets.
# Rename every legacy identifier, including any older formatting variants left by historical patches.
index = index.replace('BETA_SECRET_TOKEN', 'BETA_ROUTING_TOKEN')
index = index.replace('SECRET_TOKEN', 'CLIENT_ROUTING_TOKEN')
feedback = feedback.replace('SECRET_TOKEN', 'CLIENT_ROUTING_TOKEN')

# Add accurate comments next to the routing-value declarations if not already present.
index = index.replace(
    "      const BETA_ROUTING_TOKEN = 'ezone-2026-secret-change-this';",
    "      // Browser-visible routing value for the current Apps Script contract; not an authentication secret.\n      const BETA_ROUTING_TOKEN = 'ezone-2026-secret-change-this';",
    1,
)
index = index.replace(
    "        const CLIENT_ROUTING_TOKEN = 'ezone-2026-secret-change-this';",
    "        // Browser-visible routing value for the current Apps Script contract; not an authentication secret.\n        const CLIENT_ROUTING_TOKEN = 'ezone-2026-secret-change-this';",
    1,
)
feedback = feedback.replace(
    "      const CLIENT_ROUTING_TOKEN = 'ezone-2026-secret-change-this';",
    "      // Browser-visible routing value for the current Apps Script contract; not an authentication secret.\n      const CLIENT_ROUTING_TOKEN = 'ezone-2026-secret-change-this';",
    1,
)

# 4) Align privacy wording with actual beta-record transmission while being explicit about GPS/photos.
old_privacy = """            This beta may submit agreement/check-in records and app testing materials through the\n            connected E-Zone submission system. GPS is used to support the electioneering boundary\n            workflow.\n"""
new_privacy = """            This beta submits agreement/check-in records and tester feedback through the connected\n            E-Zone submission system. Those records can include your name, device/browser information,\n            timestamps, and testing responses. GPS is used for the electioneering boundary workflow.\n            Evidence photos are queued on the device and are transmitted only when you choose the app's\n            send-to-BOE action.\n"""
if old_privacy not in index:
    raise SystemExit('Expected privacy wording not found; refusing broad repair.')
index = index.replace(old_privacy, new_privacy, 1)

# 5) Feedback must receive and validate an explicit backend success response.
old_feedback_fetch = """        fetch(SCRIPT_URL, {\n          method: 'POST',\n          mode: 'no-cors',\n          headers: {\n            'Content-Type': 'text/plain;charset=utf-8',\n          },\n          body: JSON.stringify(payload),\n        })\n          .then(() => {\n            showThankYou();\n          })\n          .catch(() => {\n            alert(\n              'The report could not be sent automatically. Please check your connection and try again.',\n            );\n            btn.disabled = false;\n            btn.textContent = 'Submit Beta Report ★';\n          });\n"""
new_feedback_fetch = """        fetch(SCRIPT_URL, {\n          method: 'POST',\n          headers: {\n            'Content-Type': 'text/plain;charset=utf-8',\n          },\n          body: JSON.stringify(payload),\n        })\n          .then(async (res) => {\n            const data = await res.json().catch(() => null);\n            const accepted =\n              data && (data.success === true || data.ok === true || data.status === 'success');\n\n            if (!res.ok || !accepted) {\n              throw new Error('Beta report was not accepted by the submission service.');\n            }\n\n            return data;\n          })\n          .then(() => {\n            showThankYou();\n          })\n          .catch(() => {\n            alert(\n              'The report could not be confirmed as received. Please check your connection and try again.',\n            );\n            btn.disabled = false;\n            btn.textContent = 'Submit Beta Report ★';\n          });\n"""
if old_feedback_fetch not in feedback:
    raise SystemExit('Expected feedback fetch block not found; refusing broad repair.')
feedback = feedback.replace(old_feedback_fetch, new_feedback_fetch, 1)

# Safety assertions before writing.
assert 'builderBypassCode' not in index
assert 'Builder bypass accepted' not in index
assert "mode: 'no-cors'" not in feedback
assert 'SECRET_TOKEN' not in index
assert 'SECRET_TOKEN' not in feedback
assert 'reachedRequiredRadius' in index
assert 'data.success === true' in feedback

INDEX.write_text(index)
FEEDBACK.write_text(feedback)

SMOKE.write_text("""const { test, expect } = require('@playwright/test');\nconst fs = require('fs');\n\nconst indexSource = fs.readFileSync('index.html', 'utf8');\nconst feedbackSource = fs.readFileSync('feedback.html', 'utf8');\n\ntest.describe('E-Zone regular source smoke', () => {\n  test('200-foot zone cannot lock from a short drag', async () => {\n    expect(indexSource).toContain('reachedRequiredRadius');\n    expect(indexSource).toContain('STATE.arcData.radiusM >= CONFIG.defaultRadiusMeters - 0.05');\n    expect(indexSource).toContain('Drag to the full 200 ft before releasing.');\n    expect(indexSource).toContain('STATE.arcData.radiusM = CONFIG.defaultRadiusMeters');\n  });\n\n  test('feedback requires an explicit backend success response', async () => {\n    expect(feedbackSource).not.toContain(\"mode: 'no-cors'\");\n    expect(feedbackSource).toContain('data.success === true');\n    expect(feedbackSource).toContain('if (!res.ok || !accepted)');\n  });\n\n  test('old builder bypass is absent', async () => {\n    expect(indexSource).not.toContain('builderBypassCode');\n    expect(indexSource).not.toContain('Builder bypass accepted');\n  });\n\n  test('browser routing values are not labeled as secrets', async () => {\n    expect(indexSource).not.toContain('SECRET_TOKEN');\n    expect(feedbackSource).not.toContain('SECRET_TOKEN');\n    expect(indexSource).toContain('not an authentication secret');\n    expect(feedbackSource).toContain('not an authentication secret');\n  });\n\n  test('privacy wording matches beta-record and photo transmission behavior', async () => {\n    expect(indexSource).toContain('name, device/browser information');\n    expect(indexSource).toContain('Evidence photos are queued on the device');\n    expect(indexSource).toContain(\"send-to-BOE action\");\n  });\n});\n""")

print('Targeted cleanup repairs applied and source smoke tests written.')
