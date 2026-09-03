from pathlib import Path

path = Path('index.html')
text = path.read_text()

old_dom = '''      <div id="bottom-bar"></div>
    </div>

    <div id="toast"></div>'''
new_dom = '''      <div id="toast"></div>
      <div id="bottom-bar"></div>
    </div>'''
if old_dom not in text:
    raise SystemExit('Expected toast/map UI DOM layout not found')
text = text.replace(old_dom, new_dom, 1)

old_position = '''        position: fixed;
        bottom: 120px;
        left: 50%;'''
new_position = '''        position: absolute;
        bottom: 120px;
        left: 50%;'''
if old_position not in text:
    raise SystemExit('Expected refined toast positioning CSS not found')
text = text.replace(old_position, new_position, 1)

old_fn = '''        const barRect = bar.getBoundingClientRect();
        const gap = 16;
        const bottomOffset = Math.max(24, window.innerHeight - barRect.top + gap);
        t.style.top = 'auto';
        t.style.bottom = bottomOffset + 'px';'''
new_fn = '''        const barStyle = getComputedStyle(bar);
        const barBottom = Number.parseFloat(barStyle.bottom) || 28;
        const gap = 16;
        t.style.top = 'auto';
        t.style.bottom = barBottom + bar.offsetHeight + gap + 'px';'''
if old_fn not in text:
    raise SystemExit('Expected refined toast position function not found')
text = text.replace(old_fn, new_fn, 1)

path.write_text(text)
