from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# 1) Replace per-call AudioContexts with one reusable, user-unlocked context.
start = s.find('      function playDing() {')
end = s.find('\n      function ', s.find('      function playBoundaryWarning() {') + 10)
if start < 0 or end < 0:
    raise SystemExit('audio function block not found')
new_audio = '''      let sharedAudioContext = null;
      function getAudioContext() {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (!AudioCtx) return null;
        if (!sharedAudioContext) sharedAudioContext = new AudioCtx();
        return sharedAudioContext;
      }
      function unlockAudio() {
        try {
          const c = getAudioContext();
          if (c && c.state === 'suspended') c.resume();
        } catch (e) {}
      }
      function playTone(frequency, startOffset, duration, volume) {
        try {
          const c = getAudioContext();
          if (!c) return;
          if (c.state === 'suspended') c.resume();
          const o = c.createOscillator();
          const g = c.createGain();
          const start = c.currentTime + (startOffset || 0);
          const stop = start + duration;
          o.connect(g);
          g.connect(c.destination);
          o.type = 'sine';
          o.frequency.setValueAtTime(frequency, start);
          g.gain.setValueAtTime(0.001, start);
          g.gain.exponentialRampToValueAtTime(volume || 0.25, start + 0.015);
          g.gain.exponentialRampToValueAtTime(0.001, stop);
          o.start(start);
          o.stop(stop + 0.02);
        } catch (e) {}
      }
      function playDing() {
        // One clear high ding: zone setup reached 200 ft.
        playTone(880, 0, 0.42, 0.28);
      }
      function playBoundaryWarning() {
        // Three lower pulses: walking crossed the established 200-ft boundary.
        playTone(520, 0.00, 0.18, 0.30);
        playTone(520, 0.26, 0.18, 0.30);
        playTone(520, 0.52, 0.22, 0.34);
      }
'''
s = s[:start] + new_audio + s[end:]

# Unlock audio while the user is actively touching the drag control (iOS/WebKit requirement).
needle = "      function onDragStart(e) {\n        if (STATE.screen !== 's3' || zoneDone || !STATE.gpsPos) return;\n"
replacement = "      function onDragStart(e) {\n        if (STATE.screen !== 's3' || zoneDone || !STATE.gpsPos) return;\n        unlockAudio();\n"
if needle not in s:
    raise SystemExit('onDragStart marker not found')
s = s.replace(needle, replacement, 1)

# 2) Make evidence recovery explicit instead of overloading Yes/No.
old_s8 = '''        s8: {
          bubble: 'Report another Electioneering Incident?' + queueLabel(),
          buttons: [
            { label: 'Yes', cls: 'btn-green', fn: 'goTo("s6")' },
            { label: 'No', cls: 'btn-amber', fn: 'showBOEPopup()' },
            { label: 'Reset', cls: 'btn-reset', fn: 'doReset()' },
          ],
        },'''
new_s8 = '''        s8: {
          bubble: 'Evidence saved.' + queueLabel() + '<br><strong>Add another incident or send this batch to BOE.</strong>',
          buttons: [
            { label: 'ADD INCIDENT', cls: 'btn-green', fn: 'goTo("s6")' },
            { label: 'SEND TO BOE', cls: 'btn-amber', fn: 'showBOEPopup()' },
            { label: 'Reset', cls: 'btn-reset', fn: 'doReset()' },
          ],
        },'''
if old_s8 not in s:
    raise SystemExit('s8 block not found')
s = s.replace(old_s8, new_s8, 1)

# 3) Neutral send wording: do not blame signal when payload/server processing may be the cause.
s = s.replace(
    "showToast('Send paused — photos are still queued. Try again when signal improves.', '#dc2626', 5000);",
    "showToast('Send didn’t finish. Your photos are still saved. Tap SEND TO BOE to try again.', '#dc2626', 6000);",
)
s = s.replace(
    "showToast(err && err.name === 'AbortError' ? 'Send timed out — retrying once...' : 'Network error — retrying once...', '#d97706', 0);",
    "showToast(err && err.name === 'AbortError' ? 'Send is taking longer than expected — checking once more...' : 'Send was interrupted — checking once more...', '#d97706', 0);",
)

# Keep explicit offline wording when navigator.onLine actually reports offline.

p.write_text(s, encoding='utf-8')
print('Applied iPhone audio unlock, distinct boundary triple-tone, and explicit send recovery UI.')
