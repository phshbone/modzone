from pathlib import Path

p = Path('index.html')
s = p.read_text()

old = """      .instr-scroll {
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
"""
new = """      .instr-scroll {
        flex: 1 1 auto;
        min-height: 0;
        overflow-y: auto;
        -webkit-overflow-scrolling: touch;
        padding: 0 2px 86px;
      }
      .instr-close-wrap {
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
if s.count(old) != 1:
    raise SystemExit(f'Help footer CSS match count: {s.count(old)}')
s = s.replace(old, new, 1)
p.write_text(s)
print('Anchored Help footer applied.')
