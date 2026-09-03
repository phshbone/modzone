from pathlib import Path

path = Path('tests/smoke.spec.js')
text = path.read_text()
old = """    await page.evaluate(() => {
      hideStartupOverlays();
      document.getElementById('map-ui').style.display = 'block';
      renderScreen('s8');
      showToast('GPS location saved', '#16a34a');
    });
"""
new = """    await page.evaluate(() => {
      const agreement = document.getElementById('agreement-overlay');
      const returning = document.getElementById('returning-overlay');
      const welcome = document.getElementById('welcome-overlay');
      if (agreement) agreement.style.display = 'none';
      if (returning) returning.style.display = 'none';
      if (welcome) welcome.style.display = 'none';

      const mapUi = document.getElementById('map-ui');
      mapUi.style.display = 'block';

      const bar = document.getElementById('bottom-bar');
      bar.innerHTML = '<div class=\"btn-row\"><button class=\"app-btn btn-blue\">Back</button></div>';
      showToast('GPS location saved', '#16a34a');
    });
"""
if old not in text:
    raise SystemExit('Expected generated toast smoke setup not found')
path.write_text(text.replace(old, new, 1))
