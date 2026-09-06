from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

reset_old = """        STATE.photoQueue = [];
        if (STATE.entranceMarker) {
"""
reset_new = """        STATE.photoQueue = [];
        // Reset is destructive by design: also remove any previously saved evidence session
        // so a stale queued batch cannot reappear after reload.
        clearSession();
        if (STATE.entranceMarker) {
"""
if reset_old not in s:
    raise SystemExit('Reset queue marker not found')
s = s.replace(reset_old, reset_new, 1)

success_old = """                STATE.photoQueue = [];
                showToast(
"""
success_new = """                STATE.photoQueue = [];
                // Persist the confirmed empty queue so a successfully sent batch cannot
                // be restored from an older localStorage snapshot on the next launch.
                saveSession();
                showToast(
"""
if success_old not in s:
    raise SystemExit('Successful-send queue marker not found')
s = s.replace(success_old, success_new, 1)

p.write_text(s, encoding='utf-8')
print('Fixed reset/send queue persistence after field test.')
