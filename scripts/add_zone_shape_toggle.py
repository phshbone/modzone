from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# 1) Test-toggle styling.
css_marker = """      #screen-tag {\n        display: none;\n      }\n"""
css_insert = css_marker + """
      /* Temporary geometry comparison control: 270° production shape vs 180° test semicircle. */
      #shape-test-toggle {
        position: absolute;
        left: 12px;
        bottom: 175px;
        z-index: 500;
        pointer-events: auto;
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 5px;
        border-radius: 12px;
        background: rgba(10, 22, 40, 0.82);
        border: 1px solid rgba(255, 255, 255, 0.28);
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
      }
      #shape-test-toggle .shape-label {
        color: rgba(255, 255, 255, 0.72);
        font-family: 'Nunito', sans-serif;
        font-size: 10px;
        font-weight: 900;
        letter-spacing: 0.7px;
        padding: 0 4px;
      }
      .shape-test-btn {
        min-width: 48px;
        min-height: 36px;
        padding: 6px 9px;
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.12);
        color: white;
        font-family: 'Nunito', sans-serif;
        font-size: 13px;
        font-weight: 900;
        cursor: pointer;
      }
      .shape-test-btn.active {
        background: #dc2626;
        border-color: rgba(255, 255, 255, 0.75);
      }
"""
if css_marker not in s:
    raise SystemExit('CSS marker not found')
s = s.replace(css_marker, css_insert, 1)

# 2) Toggle UI inside existing map UI.
html_marker = """      <div id=\"screen-tag\"></div>\n"""
html_insert = html_marker + """      <div id=\"shape-test-toggle\" aria-label=\"Test zone shape\">\n        <span class=\"shape-label\">TEST SHAPE</span>\n        <button type=\"button\" class=\"shape-test-btn active\" data-zone-shape=\"270\" onclick=\"setZoneShapeMode('270')\">270°</button>\n        <button type=\"button\" class=\"shape-test-btn\" data-zone-shape=\"180\" onclick=\"setZoneShapeMode('180')\">180°</button>\n      </div>\n"""
if html_marker not in s:
    raise SystemExit('HTML marker not found')
s = s.replace(html_marker, html_insert, 1)

# 3) Preserve production geometry as the default state.
state_marker = """        prevMapScreen: null,\n"""
state_insert = state_marker + """        zoneShapeMode: '270', // temporary comparison toggle; 270 remains the production/default geometry\n"""
if state_marker not in s:
    raise SystemExit('STATE marker not found')
s = s.replace(state_marker, state_insert, 1)

# 4) Insert an isolated 180° draw branch before the existing 270° implementation.
geometry_marker = """        const excludeCenter = (openingAngleDeg + 180) % 360;\n"""
geometry_insert = """        // Temporary 180° comparison mode. The existing 270° path below is intentionally left intact.
        if ((STATE.zoneShapeMode || '270') === '180') {
          const startDeg180 = (openingAngleDeg - 90 + 360) % 360;
          const endDeg180 = (openingAngleDeg + 90) % 360;
          const startRad180 = (startDeg180 * Math.PI) / 180;
          const endRad180 = (endDeg180 * Math.PI) / 180;
          const sx180 = cx + r * Math.cos(startRad180);
          const sy180 = cy + r * Math.sin(startRad180);
          const ex180 = cx + r * Math.cos(endRad180);
          const ey180 = cy + r * Math.sin(endRad180);

          const fill180 = document.createElementNS('http://www.w3.org/2000/svg', 'path');
          fill180.setAttribute(
            'd',
            `M${cx},${cy} L${sx180},${sy180} A${r},${r} 0 0 1 ${ex180},${ey180} Z`,
          );
          fill180.setAttribute(
            'fill',
            STATE.arcLocked ? 'rgba(220,38,38,0.28)' : 'rgba(220,38,38,0.18)',
          );
          svg.appendChild(fill180);

          const border180 = document.createElementNS('http://www.w3.org/2000/svg', 'path');
          border180.setAttribute('d', `M${sx180},${sy180} A${r},${r} 0 0 1 ${ex180},${ey180}`);
          border180.setAttribute('fill', 'none');
          border180.setAttribute(
            'stroke',
            STATE.nearBoundary ? 'rgba(220,38,38,0.9)' : 'rgba(180,20,20,0.45)',
          );
          border180.setAttribute('stroke-width', STATE.arcLocked ? '4' : '2');
          if (!STATE.arcLocked) border180.setAttribute('stroke-dasharray', '6 3');
          svg.appendChild(border180);

          // Straight diameter through the entrance makes the semicircle boundary explicit.
          const diameter180 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
          diameter180.setAttribute('x1', sx180);
          diameter180.setAttribute('y1', sy180);
          diameter180.setAttribute('x2', ex180);
          diameter180.setAttribute('y2', ey180);
          diameter180.setAttribute('stroke', 'rgba(180,20,20,0.45)');
          diameter180.setAttribute('stroke-width', STATE.arcLocked ? '3' : '2');
          if (!STATE.arcLocked) diameter180.setAttribute('stroke-dasharray', '6 3');
          svg.appendChild(diameter180);

          // Keep the same drag-direction guide used by the current geometry while sizing the zone.
          if (!STATE.arcLocked && STATE.dragging) {
            const guide180 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            const ang180 = (openingAngleDeg * Math.PI) / 180;
            guide180.setAttribute('x1', cx);
            guide180.setAttribute('y1', cy);
            guide180.setAttribute('x2', cx + r * Math.cos(ang180));
            guide180.setAttribute('y2', cy + r * Math.sin(ang180));
            guide180.setAttribute('stroke', 'rgba(220,38,38,0.6)');
            guide180.setAttribute('stroke-width', '2');
            guide180.setAttribute('stroke-dasharray', '4 3');
            svg.appendChild(guide180);
          }

          // Outer-rim distance label for the 180° test shape.
          const currentFeet180 = Math.min(200, Math.max(0, Math.round(radiusM * 3.28084)));
          const labelAngle180 = openingAngleDeg * Math.PI / 180;
          const labelRadius180 = r + 18;
          const text180 = document.createElementNS('http://www.w3.org/2000/svg', 'text');
          text180.setAttribute('x', cx + labelRadius180 * Math.cos(labelAngle180));
          text180.setAttribute('y', cy + labelRadius180 * Math.sin(labelAngle180));
          text180.setAttribute('fill', '#dc2626');
          text180.setAttribute('font-family', 'Oswald, sans-serif');
          text180.setAttribute('font-size', '15');
          text180.setAttribute('font-weight', '700');
          text180.setAttribute('text-anchor', 'middle');
          text180.setAttribute('dominant-baseline', 'middle');
          text180.setAttribute('paint-order', 'stroke');
          text180.setAttribute('stroke', 'rgba(255,255,255,0.9)');
          text180.setAttribute('stroke-width', '3');
          text180.textContent = currentFeet180 + ' ft';
          svg.appendChild(text180);
          return;
        }

""" + geometry_marker
if geometry_marker not in s:
    raise SystemExit('Geometry marker not found')
s = s.replace(geometry_marker, geometry_insert, 1)

# 5) Toggle behavior; redraws the same stored radius/orientation and never mutates the 270° arc data.
function_marker = """      function drawZone() {\n"""
function_insert = """      function setZoneShapeMode(mode) {
        if (mode !== '270' && mode !== '180') return;
        STATE.zoneShapeMode = mode;
        document.querySelectorAll('.shape-test-btn').forEach((btn) => {
          btn.classList.toggle('active', btn.dataset.zoneShape === mode);
          btn.setAttribute('aria-pressed', btn.dataset.zoneShape === mode ? 'true' : 'false');
        });
        if (STATE.arcData) drawZone();
        showToast(mode === '180' ? '180° semicircle test' : '270° current E-Zone', mode === '180' ? '#d97706' : '#16a34a');
      }

""" + function_marker
if function_marker not in s:
    raise SystemExit('drawZone marker not found')
s = s.replace(function_marker, function_insert, 1)

# Sanity checks.
checks = [
    "zoneShapeMode: '270'",
    "setZoneShapeMode(mode)",
    "data-zone-shape=\"180\"",
    "startDeg180",
    "A${r},${r} 0 0 1",
    "Temporary 180° comparison mode",
]
for needle in checks:
    if needle not in s:
        raise SystemExit(f'Missing expected result: {needle}')

p.write_text(s, encoding='utf-8')
print('Added isolated 270° / 180° test toggle and semicircle geometry.')
