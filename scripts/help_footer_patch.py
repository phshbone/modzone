from pathlib import Path

p = Path('index.html')
s = p.read_text()

if 'class="instr-scroll"' in s:
    print('Help footer already corrected.')
    raise SystemExit(0)

anchor = "      .instr-title {\n"
css = """      .instr-scroll {
        flex: 1 1 auto;
        min-height: 0;
        overflow-y: auto;
        -webkit-overflow-scrolling: touch;
        padding: 0 2px 4px;
      }
      .instr-close-wrap {
        flex: 0 0 auto;
        text-align: center;
        padding: 10px 0 18px;
        background: #f3f4f6;
        position: relative;
        z-index: 4;
      }
      .instr-title {
"""
if s.count(anchor) != 1:
    raise SystemExit('CSS anchor mismatch')
s = s.replace(anchor, css, 1)

card = '<div class="instr-card">'
if s.count(card) != 1:
    raise SystemExit('card anchor mismatch')
s = s.replace(card, card + '\n        <div class="instr-scroll">', 1)

footer = '<div style="text-align:center;padding:12px 0 18px;position:sticky;bottom:-1px;z-index:5;background:linear-gradient(to bottom,rgba(243,244,246,0),#f3f4f6 32%);">'
if s.count(footer) != 1:
    raise SystemExit('footer anchor mismatch')
s = s.replace(footer, '</div>\n        <div class="instr-close-wrap">', 1)

p.write_text(s)
print('Help footer corrected.')
