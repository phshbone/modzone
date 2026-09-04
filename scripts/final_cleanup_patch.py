from pathlib import Path
import re

p = Path('index.html')
s = p.read_text()


def once(old, new, label):
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 match, found {n}')
    s = s.replace(old, new, 1)


# Help panel: use more phone width and keep close control fully inside the card.
once('        padding: 56px 16px 20px;', '        padding: 56px 10px 20px;', 'instructions outer padding')
once('        max-width: 420px;\n        width: 92%;', '        max-width: 460px;\n        width: 96%;', 'instructions width')
once('        width: 56px;\n        height: 56px;', '        width: 48px;\n        height: 48px;', 'instructions close size')
once("        font-size: 22px;\n        font-weight: 900;\n        cursor: pointer;\n        box-shadow: var(--btn-shadow);\n        font-family: 'Nunito', sans-serif;\n        position: relative;", "        font-size: 20px;\n        font-weight: 900;\n        cursor: pointer;\n        box-shadow: var(--btn-shadow);\n        font-family: 'Nunito', sans-serif;\n        position: relative;", 'instructions close font')
once('<div style="text-align: center; padding: 18px 0 10px">', '<div style="text-align: center; padding: 12px 0 22px">', 'instructions close padding')

# Preserve photo aspect ratio in static, screenshot, and camera previews.
once('        width: 84%;\n        max-height: 55vh;\n        border-radius: 14px;\n        border: 3px solid white;\n        object-fit: cover;', '        max-width: 84%;\n        width: auto;\n        height: auto;\n        max-height: 55vh;\n        border-radius: 14px;\n        border: 3px solid white;\n        object-fit: contain;', 'static photo preview ratio')
once("'width:100%;max-height:58vh;border-radius:12px;border:3px solid white;object-fit:contain;'", "'max-width:100%;width:auto;height:auto;max-height:58vh;border-radius:12px;border:3px solid white;object-fit:contain;'", 'screenshot preview ratio')
once("'width:100%;max-height:55vh;border-radius:12px;border:3px solid white;object-fit:contain;'", "'max-width:100%;width:auto;height:auto;max-height:55vh;border-radius:12px;border:3px solid white;object-fit:contain;'", 'camera preview ratio')

# Campaign sign: slightly smaller, same bottom-tip geographic anchor.
once("          iconSize: [58, 82],\n          iconAnchor: [29, 82],\n          popupAnchor: [0, -80],", "          iconSize: [52, 74],\n          iconAnchor: [26, 74],\n          popupAnchor: [0, -72],", 'campaign marker size')

# Replace legacy DROP button stake with campaign sign asset.
stake_const = re.compile(r"      const STAKE_BUTTON_SVG = `.*?`;\n", re.S)
if len(stake_const.findall(s)) != 1:
    raise SystemExit('stake button constant: expected exactly one match')
s = stake_const.sub("      const CAMPAIGN_BUTTON_ICON =\n        '<img src=\"assets/campaign-sign-marker.svg\" alt=\"\" aria-hidden=\"true\" style=\"width:24px;height:34px;object-fit:contain;vertical-align:middle;margin-left:4px;\" />';\n", s, count=1)
once("{ label: 'DROP ' + STAKE_BUTTON_SVG, cls: 'btn-green', fn: 'dropPin()' },", "{ label: 'DROP ' + CAMPAIGN_BUTTON_ICON, cls: 'btn-green', fn: 'dropPin()' },", 'drop button icon')

# Help Step 5 marker and Steps 6-9 wording match actual workflow.
step5 = re.compile(r"(>Walk to the offense — tap <strong>DROP</strong>)\s*<svg.*?</svg>\s*(to mark the sign/photo location</span)", re.S)
if len(step5.findall(s)) != 1:
    raise SystemExit('help step 5: expected exactly one marker block')
s = step5.sub(r'\1 <img src="assets/campaign-sign-marker.svg" alt="campaign sign" style="width:22px;height:31px;object-fit:contain;vertical-align:middle;display:inline-block;margin:0 3px" /> \2', s, count=1)
once('Photograph the offense — saves to your camera roll/downloads', 'Photograph the offense — review the GPS-stamped photo before continuing', 'help step 6')
once('Done? Tap <strong>NO</strong> when asked to report another incident', 'Done adding incidents? Tap <strong>NO</strong> when asked to report another incident', 'help step 7')
once('Tap <strong>YES</strong> when asked to send pics to the Board of Elections', 'At <strong>Send pics to BOE?</strong>, tap <strong>Send</strong> when you have internet service', 'help step 8')
once('Photos are GPS-stamped and queued — send to BOE when done', 'Photos stay queued until BOE confirms a successful send — if service is weak or offline, try Send again when signal improves', 'help step 9')

# Toasts may remain visible for a live network operation.
once("      function showToast(msg, color) {\n        color = color || '#16a34a';", "      function showToast(msg, color, durationMs) {\n        color = color || '#16a34a';", 'toast duration signature')
once("        clearTimeout(toastTimer);\n        toastTimer = setTimeout(() => t.classList.remove('show'), 2200);", "        clearTimeout(toastTimer);\n        if (durationMs !== 0) {\n          toastTimer = setTimeout(() => t.classList.remove('show'), durationMs || 2200);\n        }", 'toast duration body')

# BOE sending: offline preflight, one retry, hard timeout, queued-photo reassurance.
once('        const MAX_RETRIES = 3;', '        const MAX_RETRIES = 1;\n        const SEND_TIMEOUT_MS = 20000;', 'send retry policy')
once("        const total = q.length;\n        const finalizedPromise", "        if (!navigator.onLine) {\n          boeSendInProgress = false;\n          showToast('No internet — photos are still queued. Try Send again when connected.', '#d97706', 5000);\n          returnFromBOEPopup();\n          return;\n        }\n\n        const total = q.length;\n        const finalizedPromise", 'offline preflight')
once("          showToast(\n            'Sending ' + total + ' medium photo' + (total === 1 ? '' : 's') + ' to BOE...',\n            '#1d4ed8',\n          );\n\n          fetch(APPS_SCRIPT_URL, {", "          if (!navigator.onLine) {\n            boeSendInProgress = false;\n            showToast('Internet connection lost — photos are still queued. Try Send again when connected.', '#d97706', 5000);\n            returnFromBOEPopup();\n            return;\n          }\n\n          showToast(\n            'Sending ' + total + ' photo' + (total === 1 ? '' : 's') + ' to BOE — keep this screen open...',\n            '#1d4ed8',\n            0,\n          );\n\n          const controller = new AbortController();\n          const timeoutId = setTimeout(function () { controller.abort(); }, SEND_TIMEOUT_MS);\n\n          fetch(APPS_SCRIPT_URL, {", 'send start and timeout')
once("              photos: finalizedPhotos,\n            }),\n          })\n            .then(function (res) {\n              return res.json();", "              photos: finalizedPhotos,\n            }),\n            signal: controller.signal,\n          })\n            .then(function (res) {\n              clearTimeout(timeoutId);\n              if (!res.ok) throw new Error('BOE send HTTP ' + res.status);\n              return res.json();", 'send fetch signal')
once("                showToast(\n                  'All ' + total + ' photo' + (total === 1 ? '' : 's') + ' sent to BOE!',\n                  '#16a34a',\n                );", "                showToast(\n                  'All ' + total + ' photo' + (total === 1 ? '' : 's') + ' sent to BOE!',\n                  '#16a34a',\n                  3200,\n                );", 'send success toast')
once("                  showToast('Send failed — retrying...', '#dc2626');", "                  showToast('Send did not complete — retrying once...', '#d97706', 0);", 'send backend retry toast')
once("                  showToast('Send failed after retries', '#dc2626');", "                  showToast('Send paused — photos are still queued. Try again when signal improves.', '#dc2626', 5000);", 'send backend final failure')

old_catch = """            .catch(function () {
              if (retryCount < MAX_RETRIES) {
                showToast('Network error — retrying...', '#dc2626');
                setTimeout(function () {
                  attempt(retryCount + 1, finalizedPhotos);
                }, 2000);
              } else {
                boeSendInProgress = false;
                showToast('Send failed after retries', '#dc2626');
                returnFromBOEPopup();
              }
            });"""
new_catch = """            .catch(function (err) {
              clearTimeout(timeoutId);
              if (!navigator.onLine) {
                boeSendInProgress = false;
                showToast('Internet connection lost — photos are still queued. Try Send again when connected.', '#d97706', 5000);
                returnFromBOEPopup();
              } else if (retryCount < MAX_RETRIES) {
                showToast(err && err.name === 'AbortError' ? 'Send timed out — retrying once...' : 'Network error — retrying once...', '#d97706', 0);
                setTimeout(function () {
                  attempt(retryCount + 1, finalizedPhotos);
                }, 2000);
              } else {
                boeSendInProgress = false;
                showToast('Send paused — photos are still queued. Try again when signal improves.', '#dc2626', 5000);
                returnFromBOEPopup();
              }
            });"""
once(old_catch, new_catch, 'network failure handling')

p.write_text(s)
print('Final cleanup patch applied successfully.')
