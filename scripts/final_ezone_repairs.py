from pathlib import Path
import re

index_path = Path('index.html')
svg_path = Path('assets/campaign-sign-marker.svg')
source_test_path = Path('tests/source-smoke.spec.js')
smoke_test_path = Path('tests/smoke.spec.js')

s = index_path.read_text()

# --- Help visual restoration / consistency ---
if '.instr-stars {' not in s:
    anchor = """      .instr-close-wrap {
        position: absolute;
        left: 0;
        right: 0;
        bottom: 0;
        height: 78px;
        box-sizing: border-box;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(to bottom, rgba(243, 244, 246, 0.92), #f3f4f6 28%);
        border-radius: 0 0 24px 24px;
        z-index: 40;
      }
"""
    addition = anchor + """      .instr-scroll > div:first-child {
        display: none;
      }
      .instr-stars {
        position: absolute;
        left: 22px;
        right: 22px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        z-index: 60;
        pointer-events: none;
        line-height: 1;
      }
      .instr-stars-top { top: 10px; }
      .instr-stars-bottom { bottom: 12px; }
      .instr-stars span { font-size: 14px; font-weight: 900; }
      .instr-stars .red { color: #dc2626; }
      .instr-stars .blue { color: #1d4ed8; }
      .instr-stars .outline-red { color: white; -webkit-text-stroke: 1px #dc2626; }
      .instr-stars .outline-blue { color: white; -webkit-text-stroke: 1px #1d4ed8; }
      .instr-locator {
        display: inline-block;
        vertical-align: middle;
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: #1d4ed8;
        border: 3px solid white;
        margin: 0 5px;
        box-sizing: border-box;
      }
      .instr-locator-drag {
        box-shadow: 0 0 0 4px #dc2626;
      }
      .instr-locator-return {
        box-shadow: 0 0 0 3px rgba(29, 78, 216, 0.32);
      }
      .instr-nav-hint {
        opacity: 1 !important;
        justify-content: center;
        text-align: center;
        color: #374151;
        margin-bottom: 4px;
      }
"""
    if anchor not in s:
        raise SystemExit('Help close-wrap CSS anchor not found')
    s = s.replace(anchor, addition, 1)

s = s.replace('padding: 0 2px 86px;', 'padding: 0 2px 108px;', 1)

card_open = '      <div class="instr-card">\n        <div class="instr-scroll">'
if 'instr-stars instr-stars-top' not in s:
    star_markup = '''      <div class="instr-card">
        <div class="instr-stars instr-stars-top" aria-hidden="true">
          <span class="red">★</span><span class="outline-red">★</span><span class="blue">★</span><span class="red">★</span><span class="outline-blue">★</span><span class="blue">★</span><span class="red">★</span><span class="outline-red">★</span><span class="blue">★</span>
        </div>
        <div class="instr-stars instr-stars-bottom" aria-hidden="true">
          <span class="blue">★</span><span class="red">★</span><span class="outline-blue">★</span><span class="red">★</span><span class="blue">★</span><span class="outline-red">★</span><span class="red">★</span><span class="blue">★</span><span class="red">★</span>
        </div>
        <div class="instr-scroll">'''
    if card_open not in s:
        raise SystemExit('Help card opening anchor not found')
    s = s.replace(card_open, star_markup, 1)

# Replace Step 2 with one consistent draggable locator symbol.
step2_pattern = re.compile(r'''          <div class="instr-step">\s*<span class="num">2\.</span.*?</div>\s*(?=          <div class="instr-step">\s*<span class="num">3\.</span)''', re.S)
step2 = '''          <div class="instr-step">
            <span class="num">2.</span><span>Drag the <span class="instr-locator instr-locator-drag" aria-hidden="true"></span> away from the entrance to set your 200 ft E-Zone — release when it beeps</span>
          </div>
'''
s, n = step2_pattern.subn(step2, s, count=1)
if n != 1:
    raise SystemExit(f'Step 2 replacement count {n}')

# Replace Step 4 with the same blue locator language, using a softer return ring.
step4_pattern = re.compile(r'''          <div class="instr-step">\s*<span class="num">4\.</span.*?</div>\s*(?=          <div class="instr-step">\s*<span class="num">5\.</span)''', re.S)
step4 = '''          <div class="instr-step">
            <span class="num">4.</span><span>Dot returns to <span class="instr-locator instr-locator-return" aria-hidden="true"></span> — walk the boundary, phone vibrates at the edge</span>
          </div>
'''
s, n = step4_pattern.subn(step4, s, count=1)
if n != 1:
    raise SystemExit(f'Step 4 replacement count {n}')

s = s.replace('style="width:22px;height:31px;object-fit:contain;vertical-align:middle;display:inline-block;margin:0 3px"',
              'style="width:26px;height:37px;object-fit:contain;vertical-align:middle;display:inline-block;margin:0 4px"', 1)
s = s.replace('class="instr-step"\n            style="opacity: 0.82; justify-content: center; text-align: center"',
              'class="instr-step instr-nav-hint"', 1)

# --- Deterministic campaign-sign composition for screenshots ---
if 'function drawCampaignSignCanvas(' not in s:
    helper = r'''      function drawCampaignSignCanvas(ctx, left, top, width, height) {
        const sx = width / 52;
        const sy = height / 74;
        ctx.save();
        ctx.translate(left, top);
        ctx.scale(sx, sy);

        // Stake first so the sign face sits naturally in front of it.
        const pole = ctx.createLinearGradient(24.6, 0, 27.5, 0);
        pole.addColorStop(0, '#2d3138');
        pole.addColorStop(0.45, '#6a7079');
        pole.addColorStop(0.72, '#2b2f35');
        pole.addColorStop(1, '#111318');
        ctx.fillStyle = pole;
        ctx.strokeStyle = '#111318';
        ctx.lineWidth = 0.4;
        ctx.beginPath();
        ctx.moveTo(24.6, 40.3);
        ctx.lineTo(27.4, 40.3);
        ctx.lineTo(27.4, 66.2);
        ctx.lineTo(26, 72);
        ctx.lineTo(24.6, 66.2);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        // Small shadow behind the board.
        ctx.save();
        ctx.shadowColor = 'rgba(0,0,0,.35)';
        ctx.shadowBlur = 2.2;
        ctx.shadowOffsetY = 1.2;
        ctx.fillStyle = '#f8f9fb';
        ctx.fillRect(3.7, 16.6, 44.6, 26.4);
        ctx.restore();

        ctx.fillStyle = '#f8f9fb';
        ctx.strokeStyle = '#e5e7eb';
        ctx.lineWidth = 1;
        ctx.fillRect(3.7, 16.6, 44.6, 26.4);
        ctx.strokeRect(3.7, 16.6, 44.6, 26.4);
        ctx.strokeStyle = '#0b3f91';
        ctx.lineWidth = 1.5;
        ctx.strokeRect(4.8, 17.7, 42.4, 24.2);
        ctx.strokeStyle = '#d71920';
        ctx.lineWidth = 0.8;
        ctx.strokeRect(6.1, 19, 39.8, 21.6);

        // Patriotic corners and stars.
        ctx.fillStyle = '#d71920';
        ctx.beginPath(); ctx.moveTo(6.2, 19); ctx.lineTo(16.4, 19); ctx.lineTo(6.2, 27); ctx.closePath(); ctx.fill();
        ctx.beginPath(); ctx.moveTo(45.8, 19); ctx.lineTo(35.6, 19); ctx.lineTo(45.8, 27); ctx.closePath(); ctx.fill();
        ctx.font = 'bold 4.4px Arial, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillStyle = '#d71920'; ctx.fillText('★', 21.4, 25.5); ctx.fillText('★', 30.6, 25.5);
        ctx.fillStyle = '#0b3f91'; ctx.font = 'bold 5.4px Arial, sans-serif'; ctx.fillText('★', 26, 23.8);

        ctx.fillStyle = '#0b3f91';
        ctx.font = '900 6.3px Arial Black, Arial, sans-serif';
        ctx.fillText('CAMPAIGN', 26, 34.4);
        ctx.strokeStyle = '#d71920';
        ctx.lineWidth = 0.8;
        ctx.beginPath(); ctx.moveTo(7.9, 36.5); ctx.lineTo(18.3, 36.5); ctx.moveTo(33.7, 36.5); ctx.lineTo(44.1, 36.5); ctx.stroke();
        ctx.restore();
      }

      function compositeIncidentMarkers(canvas) {
        if (!canvas || !STATE.incidentMarkers || !STATE.incidentMarkers.length) return;
        const wrapper = document.getElementById('map-wrapper');
        if (!wrapper) return;
        const wrapperRect = wrapper.getBoundingClientRect();
        if (!wrapperRect.width || !wrapperRect.height) return;
        const scaleX = canvas.width / wrapperRect.width;
        const scaleY = canvas.height / wrapperRect.height;
        const ctx = canvas.getContext('2d');
        STATE.incidentMarkers.forEach((marker) => {
          const el = marker && marker.getElement ? marker.getElement() : null;
          if (!el) return;
          const rect = el.getBoundingClientRect();
          if (rect.right < wrapperRect.left || rect.left > wrapperRect.right || rect.bottom < wrapperRect.top || rect.top > wrapperRect.bottom) return;
          drawCampaignSignCanvas(
            ctx,
            (rect.left - wrapperRect.left) * scaleX,
            (rect.top - wrapperRect.top) * scaleY,
            rect.width * scaleX,
            rect.height * scaleY,
          );
        });
      }

'''
    marker = '      function captureScreen(nextScreen) {'
    if marker not in s:
        raise SystemExit('captureScreen anchor not found')
    s = s.replace(marker, helper + marker, 1)

old_capture = """          logging: false,
        })
          .then((canvas) => showScreenshotPreview(canvas.toDataURL('image/png'), nextScreen))
"""
new_capture = """          logging: false,
          onclone: (clonedDoc) => {
            clonedDoc
              .querySelectorAll('img[src*="campaign-sign-marker.svg"]')
              .forEach((img) => { img.style.visibility = 'hidden'; });
          },
        })
          .then((canvas) => {
            compositeIncidentMarkers(canvas);
            showScreenshotPreview(canvas.toDataURL('image/png'), nextScreen);
          })
"""
if old_capture not in s:
    raise SystemExit('capture promise block not found')
s = s.replace(old_capture, new_capture, 1)

index_path.write_text(s)

# Shorten visible stake another ~8% by moving the unchanged sign face down 12 SVG units.
svg = svg_path.read_text()
svg = svg.replace('sign face down so the visible stake is ~25% shorter', 'sign face down so the visible stake is ~30% shorter', 1)
if 'transform="translate(0 51)"' not in svg:
    raise SystemExit('SVG translate anchor not found')
svg = svg.replace('transform="translate(0 51)"', 'transform="translate(0 63)"', 1)
svg_path.write_text(svg)

# Extend regular source smoke to guard the fixes.
t = source_test_path.read_text()
if "screenshot export deliberately composites the campaign sign" not in t:
    insertion = r'''
  test('screenshot export deliberately composites the campaign sign', async () => {
    expect(indexSource).toContain('function drawCampaignSignCanvas');
    expect(indexSource).toContain('function compositeIncidentMarkers');
    expect(indexSource).toContain('onclone: (clonedDoc) =>');
    expect(indexSource).toContain('campaign-sign-marker.svg');
    expect(indexSource).toContain('compositeIncidentMarkers(canvas);');
  });

  test('Help patriotic frame and locator symbols are explicit', async () => {
    expect(indexSource).toContain('instr-stars instr-stars-top');
    expect(indexSource).toContain('instr-stars instr-stars-bottom');
    expect(indexSource).toContain('instr-locator instr-locator-drag');
    expect(indexSource).toContain('instr-locator instr-locator-return');
    expect(indexSource).toContain('width:26px;height:37px');
    expect(indexSource).toContain('instr-nav-hint');
  });
'''
    t = t.replace('\n});\n', insertion + '\n});\n', 1)
source_test_path.write_text(t)

# Extend live smoke with a deterministic canvas-render check and Help decoration checks.
t = smoke_test_path.read_text()
if "campaign sign export compositor paints a complete marker" not in t:
    live_test = r'''

  test('campaign sign export compositor paints a complete marker', async ({ page }, testInfo) => {
    await page.goto('index.html', { waitUntil: 'domcontentloaded' });
    const painted = await page.evaluate(() => {
      const c = document.createElement('canvas');
      c.width = 60;
      c.height = 82;
      const ctx = c.getContext('2d');
      drawCampaignSignCanvas(ctx, 4, 4, 52, 74);
      const data = ctx.getImageData(0, 0, c.width, c.height).data;
      let alphaPixels = 0;
      for (let i = 3; i < data.length; i += 4) if (data[i] > 0) alphaPixels++;
      return alphaPixels;
    });
    expect(painted).toBeGreaterThan(800);
    await page.evaluate(() => {
      const instructions = document.getElementById('instructions');
      instructions.classList.add('active');
      instructions.style.display = 'flex';
    });
    await captureVerification(page, testInfo, 'campaign-export-compositor');
  });
'''
    t = t.replace('\n});\n', live_test + '\n});\n', 1)

# Strengthen existing Help visual test.
needle = '    await expect(page.locator(\'.instr-card img[alt="campaign sign"]\')).toBeVisible();\n'
if needle in t and "instr-stars-top" not in t:
    replacement = needle + "    await expect(page.locator('.instr-stars-top')).toBeVisible();\n    await expect(page.locator('.instr-stars-bottom')).toBeVisible();\n    await expect(page.locator('.instr-locator-drag')).toBeVisible();\n    await expect(page.locator('.instr-locator-return')).toBeVisible();\n"
    t = t.replace(needle, replacement, 1)
smoke_test_path.write_text(t)

print('Final E-Zone repairs applied.')
